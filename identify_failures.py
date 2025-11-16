import csv
import os

USNEWS_FILE = "usnews_university_data.csv"
FINAL_OUTPUT_FILE = "university_deadlines.csv"
SUCCESSFUL_OUTPUT_FILE = "successful_deadlines.csv"
RETRY_LIST_FILE = "retry_list.csv"

# These are the messages the main script outputs on failure.
FAILURE_MESSAGES = [
    "Could not find deadline page.",
    "Could not find specific deadline dates. Check URL manually."
]

def find_failed_universities():
    """
    Reads the latest scraper output, separates failed from successful,
    and intelligently merges the new successful results with any existing ones.
    """
    # 1. خواندن تمام دانشگاه‌ها از فایل اصلی
    all_universities = set()
    try:
        with open(USNEWS_FILE, 'r', newline='', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                all_universities.add(row['Name'])
    except FileNotFoundError:
        print(f"❌ Error: The main university file '{USNEWS_FILE}' was not found. Please run 'usnews_scraper.py' first.")
        return

    newly_successful_rows = []
    
    try:
        # 2. Read the latest run's output and separate successes from failures
        with open(FINAL_OUTPUT_FILE, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                info = row['Found Deadline Info']
                if info in FAILURE_MESSAGES or info.startswith("An error occurred:"):
                    pass # موارد ناموفق را نادیده می‌گیریم
                else:
                    newly_successful_rows.append(row)
        
        # 3. Load existing successful results into a dictionary for easy updates
        all_successful_rows = {}
        if os.path.exists(SUCCESSFUL_OUTPUT_FILE):
            with open(SUCCESSFUL_OUTPUT_FILE, 'r', newline='', encoding='utf-8') as existing_file:
                reader = csv.DictReader(existing_file)
                for row in reader:
                    all_successful_rows[row['University']] = row
            print(f"✅ Loaded {len(all_successful_rows)} existing successful results.")

        # 4. Merge new successful results into the main dictionary (upsert logic)
        if newly_successful_rows:
            for row in newly_successful_rows:
                university_name = row['University']
                all_successful_rows[university_name] = row
            print(f"✅ Merged {len(newly_successful_rows)} new successful results.")

        # 5. شناسایی دانشگاه‌هایی که هنوز موفق نشده‌اند و ایجاد retry_list.csv
        successful_universities = set(all_successful_rows.keys())
        universities_to_retry = all_universities - successful_universities

        if universities_to_retry:
            with open(RETRY_LIST_FILE, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.writer(outfile)
                writer.writerow(['University'])  # Write header
                for uni_name in sorted(list(universities_to_retry)):
                    writer.writerow([uni_name])
            print(f"✅ Identified {len(universities_to_retry)} universities to retry. Saved to '{RETRY_LIST_FILE}'.")
        else:
            print("✅ Great news! No new failures were found in the latest run.")
            # Clear the retry file if it exists, as there's nothing to retry
            if os.path.exists(RETRY_LIST_FILE):
                os.remove(RETRY_LIST_FILE)

        # 6. Write the final, complete list of successful results
        if all_successful_rows:
            # Sort by university name before writing for consistency
            final_list = sorted(all_successful_rows.values(), key=lambda x: x['University'])
            with open(SUCCESSFUL_OUTPUT_FILE, 'w', newline='', encoding='utf-8') as outfile:
                fieldnames = ['University', 'Found Deadline Info', 'Deadline Page URL']
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(final_list)
            print(f"✅ Saved a total of {len(final_list)} successful results to '{SUCCESSFUL_OUTPUT_FILE}'.")
        
    except FileNotFoundError:
        print(f"❌ Error: The output file '{FINAL_OUTPUT_FILE}' was not found. Please run the main scraper first.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    find_failed_universities()