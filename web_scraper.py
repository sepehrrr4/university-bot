#!/usr/bin/env python3
# web_scraper.py
# اسکریپت جدید برای استخراج اطلاعات اساتید مستقیماً از وب‌سایت CSRankings
# نیازمند: pip install selenium webdriver-manager beautifulsoup4 pandas selenium-wire

from bs4 import BeautifulSoup
import pandas as pd
import sys
import urllib.parse
import time
import logging

# --- Selenium Imports ---
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://csrankings.org/#/fromyear/1970/toyear/2025/index?all&us"

# --- FIX: Suppress unnecessary log messages from Selenium ---
logging.getLogger('WDM').setLevel(logging.NOTSET)

def get_page_content(url):
    """
    دانلود محتوای HTML صفحه وب با استفاده از Selenium.
    این تابع ابتدا به پایین صفحه اسکرول می‌کند تا تمام دانشگاه‌ها لود شوند،
    سپس روی تمام دکمه‌های "►" کلیک می‌کند تا لیست اساتید ظاهر شود.
    """
    print(f"Fetching data from: {url} using Selenium...")
    chrome_options = Options()
    #chrome_options.add_argument("--headless")  # اجرای مرورگر در پس‌زمینه (بدون نمایش پنجره)
    chrome_options.add_argument("--log-level=3") # کاهش لاگ‌های اضافی selenium
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging']) # کاهش لاگ‌های webdriver
    
    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)
        print("Waiting for dynamic content to load (10 seconds)...")
        time.sleep(10)  # انتظار برای بارگذاری کامل محتوای جاوا اسکریپت
        html = driver.page_source

        # --- NEW: Scroll to the bottom to load all universities ---
        print("Scrolling to load all universities...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) # Wait for page to load
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        # --- NEW: Click all '►' buttons to expand faculty lists ---
        try:
            # Wait until at least one button is present
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.hovertip[id$='-widget']"))
            )
            # Find and click all expand buttons
            expand_buttons = driver.find_elements(By.CSS_SELECTOR, "span.hovertip[id$='-widget']")
            print(f"Found {len(expand_buttons)} universities. Expanding all faculty lists...")
            for button in expand_buttons:
                driver.execute_script("arguments[0].click();", button)
            print("All lists expanded. Waiting a moment for content to render...")
            time.sleep(5) # Give time for all lists to render
        except TimeoutException:
            print("Warning: Could not find any expand buttons. The page structure might have changed.", file=sys.stderr)

        html = driver.page_source # Get the final, fully expanded HTML
        driver.quit()
        return html
    except (WebDriverException, ValueError) as e:
        print(f"Error with Selenium/WebDriver: {e}", file=sys.stderr)
        print("Please ensure Google Chrome is installed.", file=sys.stderr)
        return None

def parse_faculty_data(html_content):
    """تجزیه محتوای HTML و استخراج اطلاعات اساتید"""
    soup = BeautifulSoup(html_content, 'html.parser')
    all_faculty_data = []

    # پیدا کردن تمام ردیف‌های دانشگاه‌ها در جدول اصلی
    uni_rows = soup.select("div#success table > tbody > tr")

    for row in uni_rows:
        # پیدا کردن اسپنی که نام دانشگاه را در خود دارد
        uni_span = row.find('span', onclick=lambda x: x and 'toggleFaculty' in x)
        if not uni_span:
            continue
        
        # The university name is in the *next* span sibling
        name_span = uni_span.find_next_sibling('span')
        if not name_span:
            continue
        university_name = name_span.text.strip()
        # Processing message is now handled in the main loop

        # پیدا کردن div مخفی حاوی اطلاعات اساتید بر اساس id
        faculty_div_id = urllib.parse.quote(university_name) + "-faculty"
        faculty_div = soup.find('div', id=faculty_div_id)

        if not faculty_div:
            continue
        print(f"  - Processing: {university_name}")

        # پیدا کردن تمام ردیف‌های اساتید در جدول داخلی
        faculty_rows = faculty_div.select("table > tbody > tr")
        for prof_row in faculty_rows:
            # --- FIX: Select the second 'td' which contains the main info ---
            all_cells = prof_row.find_all('td')
            # A valid professor row has at least 2 cells.
            if len(all_cells) < 2:
                continue
            prof_cell = all_cells[1] # The second cell (index 1) has the data

            name_tag = prof_cell.find('a', href=True)
            name = name_tag.text.strip() if name_tag else "N/A"
            homepage = name_tag['href'] if name_tag and 'href' in name_tag.attrs else "N/A"
            
            dblp_tag = prof_cell.find('a', href=lambda x: x and 'dblp.org' in x)
            dblp_link = dblp_tag['href'] if dblp_tag else "N/A"

            areas = [span.text for span in prof_cell.select('span.areaname > span')]

            all_faculty_data.append({
                "name": name,
                "affiliation": university_name,
                "homepage": homepage,
                "dblp": dblp_link,
                "areas": ", ".join(areas)
            })

    return all_faculty_data

def main():
    html = get_page_content(BASE_URL)
    if not html:
        sys.exit("Could not retrieve website content. Please check your internet connection.")

    faculty_list = parse_faculty_data(html)
    df = pd.DataFrame(faculty_list)
    df.to_csv("all_professors.csv", index=False, encoding="utf-8-sig")
    print(f"\nSuccessfully extracted {len(df)} records. Data saved to all_professors.csv")

if __name__ == "__main__":
    main()