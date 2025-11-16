from bs4 import BeautifulSoup
import re
import csv
import time
import undetected_chromedriver as uc
import random
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# A list of keywords to find in the text of the page
# We are looking for deadlines, which are often near month names.
DEADLINE_KEYWORDS = [
    'deadline', 'due', 'application period', 'submit by',
    'january', 'february', 'march', 'april', 'may', 'june',
    'july', 'august', 'september', 'october', 'november', 'december'
]

# Regex to find dates and surrounding text (e.g., "Deadline: January 15")
# This looks for a month name followed by 1 or 2 digits.

# --- FINAL IMPROVEMENT: Handles full month names, abbreviated names (e.g., Nov.), and both date formats ---
full_months = DEADLINE_KEYWORDS[4:]
abbreviated_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
# Combine both lists and allow for an optional period at the end (e.g., "Nov.")
all_months_regex = "|".join(full_months + abbreviated_months)
months_pattern = r"\b(?:{})\.?\b".format(all_months_regex) # e.g., matches "November" or "Nov."
DATE_PATTERN = re.compile(r"({0}\s+\d{{1,2}}|\d{{1,2}}\s+{0})".format(months_pattern), re.IGNORECASE)


def get_deadline_page_url(driver, university_name):
    """
    Searches Google robustly for the university's admission deadline page using undetected_chromedriver.
    """
    query = f"{university_name} undergraduate application deadlines"
    print(f"🔍 Searching for: '{query}'")
    screenshot_filename = "debug_screenshot.png"

    try:
        driver.get(f"https://www.google.com/search?q={query}")

        # --- ROBUST: Handle Cookie Consent Banner ---
        try:
            # Try multiple XPaths for different "Accept" buttons
            possible_xpaths = [
                "//button[.//div[contains(text(), 'Accept all')]]",
                "//button[.//div[contains(text(), 'I agree')]]",
                "//button[.//span[contains(text(), 'Accept all')]]",
                "//div[contains(text(), 'Accept all')]/ancestor::button",
            ]
            # Wait up to 5 seconds for any of the buttons
            accept_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, " | ".join(possible_xpaths)))
            )
            accept_button.click()
            print("✅ Clicked the 'Accept all' cookie button.")
            time.sleep(2) # Wait a moment after clicking
        except TimeoutException:
            print("ℹ️ Cookie consent banner not found, continuing...")

        # --- ROBUST: Use Explicit Wait and find links ---
        # Wait up to 30 seconds for search results to appear, giving you time to solve a CAPTCHA if needed.
        print("⏳ Waiting for search results (or CAPTCHA)...")
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "rcnt")))

        # Find all link elements within the search results area
        links = driver.find_elements(By.CSS_SELECTOR, "div#search a")

        for link in links:
            href = link.get_attribute('href')
            # Ensure the link is valid and contains a title (h3)
            if href and link.find_elements(By.CSS_SELECTOR, "h3"):
                # --- IMPROVED: More flexible domain filtering ---
                # List of common top-level domains for educational institutions
                valid_domains = ['.edu', '.ca', '.ac.uk', '.de', '.ch', '.org']
                
                # Check if the link belongs to a valid domain and is not a Google link
                if any(domain in href for domain in valid_domains) and 'google.com' not in href:
                    print(f"✅ Found a potential link: {href}")
                    return href # Return the first valid link

        # --- DEBUGGING: If no link was found, take a screenshot ---
        print(f"❌ No valid university link found in search results. Saving screenshot to {screenshot_filename}")
        driver.save_screenshot(screenshot_filename)

    except Exception as e:
        print(f"❌ An unexpected error occurred during search for {university_name}: {e}")
        print(f"   Saving screenshot to {screenshot_filename} for debugging.")
        driver.save_screenshot(screenshot_filename)
        
    return None


def scrape_deadlines_from_url(driver, url):
    """
    Scrapes a given URL to find text related to deadlines using Selenium.
    """
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Get the page source after JavaScript has run
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # --- FINAL ROBUST STRATEGY: Always scrape the entire body ---
        # This ensures sidebars and other non-main content areas are included.
        # The context extraction logic below is strong enough to handle the extra text.
        all_text = soup.find('body').get_text(separator=' ', strip=True)
            
        # --- NEW ROBUST METHOD: Find dates in the whole text, then extract context ---
        found_deadlines = set() # Use a set to avoid duplicate entries
        # Use finditer to get match objects with positions
        for match in DATE_PATTERN.finditer(all_text):
            # Get the position of the found date
            start, end = match.span()
            
            # Define a window of characters around the date to get context
            context_start = max(0, start - 50) # 50 characters before
            context_end = min(len(all_text), end + 100) # 100 characters after
            
            # Extract the snippet and clean it up
            context_snippet = all_text[context_start:context_end]
            clean_snippet = ' '.join(context_snippet.replace('\n', ' ').split())
            found_deadlines.add(f"...{clean_snippet}...")

        if found_deadlines:
            return "; ".join(found_deadlines)
        else:
            return "Could not find specific deadline dates. Check URL manually."

    except Exception as e:
        print(f"An error occurred while scraping {url}: {e}")
        return f"An error occurred: {e}"


def main():
    # --- NEW: Read universities from the CSV file ---
    input_csv_filename = "usnews_university_data.csv" # <<<< تغییر اصلی اینجاست
    universities = []
    try:
        with open(input_csv_filename, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile) # خواندن به صورت دیکشنری
            for row in reader:
                if row:  # Ensure the row is not empty
                    universities.append(row['Name']) # خواندن از ستون Name
        print(f"✅ Successfully loaded {len(universities)} universities from '{input_csv_filename}'.")
    except FileNotFoundError:
        print(f"❌ Error: Input file '{input_csv_filename}' not found. Please run 'usnews_scraper.py' first.")
        return  # Exit if the input file doesn't exist
    except Exception as e:
        print(f"❌ Error reading '{input_csv_filename}': {e}")
        return

    output_filename = "university_deadlines.csv"

    # --- Selenium Setup with undetected-chromedriver ---
    # This is much more robust against bot detection.
    options = uc.ChromeOptions()
    # Running in headless mode increases the chance of being detected, so it's commented out.
    # options.add_argument('--headless=new') # Use '--headless=new' for newer versions
    options.add_argument("--log-level=3")

    # --- NEW: Use a persistent user profile to avoid CAPTCHAs ---
    # This saves cookies and login sessions, making you look like a returning user.
    profile_path = os.path.join(os.getcwd(), "chrome_profile")
    options.add_argument(f'--user-data-dir={profile_path}')
    options.add_argument('--profile-directory=Default')

    # The library will automatically download and manage the correct chromedriver
    driver = uc.Chrome(options=options)

    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['University', 'Found Deadline Info', 'Deadline Page URL']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for uni in universities:
            deadline_url = get_deadline_page_url(driver, uni)
            deadline_info = "Could not find deadline page."

            if deadline_url:
                print(f"🔗 Found URL: {deadline_url}")
                deadline_info = scrape_deadlines_from_url(driver, deadline_url)
                print(f"ℹ️  Info: {deadline_info}\n")
            else:
                print(f"❌ Could not find a deadline page for {uni}.\n")
            
            # --- NEW: Use a random pause to look more human ---
            time.sleep(random.uniform(6, 11))

            writer.writerow({
                'University': uni,
                'Found Deadline Info': deadline_info,
                'Deadline Page URL': deadline_url or "N/A"
            })

    driver.quit() # Close the browser
    print(f"✅ Done! Results saved to {output_filename}")


if __name__ == "__main__":
    main()
