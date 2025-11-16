import csv
import time
import os
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Import all selectors and constants from your config file
import config

OUTPUT_FILE = "usnews_university_data.csv"

def scrape_university_details(driver, detail_url):
    """
    Navigates to a university's detail page and scrapes all required information.
    """
    print(f"  -> Scraping details from: {detail_url}")
    driver.get(detail_url)
    
    university_data = {}
    
    try:
        # Wait for the main content to be visible
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, config.DETAIL_NAME_SELECTOR)))

        # 1. Extract Name
        university_data['Name'] = driver.find_element(By.CSS_SELECTOR, config.DETAIL_NAME_SELECTOR).text.strip()

        # 2. Extract Website
        try:
            university_data['Website'] = driver.find_element(By.CSS_SELECTOR, config.DETAIL_WEBSITE_SELECTOR).get_attribute('href')
        except:
            university_data['Website'] = "Not Found"

        # 3. Extract University Data (Key-Value pairs)
        data_dict = {}
        try:
            # --- NEW ROBUST STRATEGY: Try multiple selectors ---
            data_container = None
            try:
                # Strategy 1: Find by the primary ID selector (most reliable)
                data_container = driver.find_element(By.CSS_SELECTOR, config.DETAIL_DATA_CONTAINER_SELECTOR)
            except:
                print("    - Info: Primary selector '#uniData' not found. Trying fallback strategy.")
                # Strategy 2 (Fallback): Find a heading with "Data" and get the container next to it.
                try:
                    data_heading = driver.find_element(By.XPATH, "//*[self::h2 or self::h3][contains(text(), 'Data')]")
                    data_container = data_heading.find_element(By.XPATH, "./following-sibling::div[1]")
                except:
                    print("    - Info: Fallback strategy also failed. Data section is likely missing or has a new structure.")

            # --- FIX: Only scrape rows if a container was successfully found ---
            if data_container:
                data_rows = data_container.find_elements(By.CSS_SELECTOR, config.DETAIL_DATA_ROW_SELECTOR)
                for row in data_rows:
                    key = row.find_element(By.CSS_SELECTOR, "p:first-child").text.strip()
                    value = row.find_element(By.CSS_SELECTOR, "p:last-child").text.strip()
                    data_dict[key] = value
        except Exception as e:
            # This warning is now more specific
            print(f"    - Warning: Could not scrape University Data. It might not exist on this page. Error: {e}")
        # Store as a JSON string for easy CSV storage
        university_data['Data'] = json.dumps(data_dict, indent=2)

        # 4. Extract Rankings
        rankings_list = []
        try:
            rankings_container = driver.find_element(By.CSS_SELECTOR, config.DETAIL_RANKINGS_CONTAINER_SELECTOR)
            ranking_items = rankings_container.find_elements(By.CSS_SELECTOR, config.DETAIL_RANKINGS_ITEM_SELECTOR)
            for item in ranking_items:
                rank = item.find_element(By.CSS_SELECTOR, "div[class*='RankList__Rank']").text.strip()
                subject = item.find_element(By.CSS_SELECTOR, "a > strong:last-of-type").text.strip()
                rankings_list.append(f"{rank} in {subject}")
        except Exception as e:
            print(f"    - Warning: Could not scrape Rankings. {e}")
        # Store as a JSON string
        university_data['Rankings'] = json.dumps(rankings_list, indent=2)

        return university_data

    except TimeoutException:
        print(f"    - Error: Timed out waiting for page content on {detail_url}")
        return None
    except Exception as e:
        print(f"    - Error: An unexpected error occurred on {detail_url}: {e}")
        return None

def main():
    """
    Main function to orchestrate the scraping process.
    """
    # --- Selenium Setup (using the same robust setup as before) ---
    options = uc.ChromeOptions()
    options.add_argument("--log-level=3")
    profile_path = os.path.join(os.getcwd(), "chrome_profile_usnews") # Use a separate profile
    options.add_argument(f'--user-data-dir={profile_path}')
    options.add_argument('--profile-directory=Default')
    driver = uc.Chrome(options=options)

    all_university_details = []

    try:
        # 1. Go to the base URL
        driver.get(config.BASE_URL)
        print(f"✅ Navigated to base URL: {config.BASE_URL}")

        # 2. Handle pagination by clicking "Load More" until it disappears
        while True:
            try:
                # --- IMPROVEMENT: Wait for the button to be present, then scroll to it ---
                load_more_button = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, config.PAGINATION_NEXT_BUTTON_SELECTOR))
                )
                # Scroll the button into view to ensure it's clickable
                driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                time.sleep(1) # A brief pause after scrolling

                # Now that it's in view, wait for it to be clickable and then click
                clickable_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, config.PAGINATION_NEXT_BUTTON_SELECTOR))
                )
                driver.execute_script("arguments[0].click();", clickable_button)
                print("... Clicked 'Load More' button.")
                time.sleep(3)  # Wait for new content to load
            except TimeoutException:
                print("✅ All universities have been loaded.")
                break

        # 3. Get all detail page links
        print("🔍 Extracting all university detail page links...")
        university_cards = driver.find_elements(By.CSS_SELECTOR, config.UNIVERSITY_LIST_ITEM_SELECTOR)
        detail_links = []
        for card in university_cards:
            try:
                link_element = card.find_element(By.CSS_SELECTOR, config.UNIVERSITY_DETAIL_LINK_SELECTOR)
                detail_links.append(link_element.get_attribute('href'))
            except:
                continue
        
        print(f"✅ Found {len(detail_links)} university links to scrape.")

        # 4. Scrape each detail page
        # --- REMOVED TEST LIMIT: Scraping all universities ---
        for i, link in enumerate(detail_links):
            print(f"\n--- Processing University {i+1}/{len(detail_links)} ---")
            details = scrape_university_details(driver, link)
            if details:
                all_university_details.append(details)
            time.sleep(2) # Be respectful to the server

    finally:
        driver.quit()

    # 5. Write all collected data to the final CSV file
    if all_university_details:
        print(f"\n💾 Writing {len(all_university_details)} universities to '{OUTPUT_FILE}'...")
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8-sig') as outfile:
            # The fieldnames are the keys from our scraped dictionary
            fieldnames = ['Name', 'Website', 'Data', 'Rankings']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_university_details)
        print("🎉 Scraping complete!")
    else:
        print("❌ No university data was scraped. Please check for errors.")

if __name__ == "__main__":
    main()