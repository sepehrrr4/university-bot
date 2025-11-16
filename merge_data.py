# merge_data.py
# این اسکریپت داده‌ها را از فایل‌های مختلف خوانده و در یک فایل جامع ادغام می‌کند.
# نیازمند: pip install pandas

import pandas as pd
import json
import re

# --- نام فایل‌های ورودی و خروجی ---
USNEWS_FILE = "usnews_university_data.csv"
DEADLINES_FILE = "successful_deadlines.csv"
PROFESSORS_FILE = "all_professors.csv"
OUTPUT_FILE = "final_university_database.csv"

def normalize_name(name):
    """
    نام دانشگاه را برای تطبیق بهتر، نرمال‌سازی می‌کند.
    - حذف فاصله‌های اضافی
    - تبدیل به حروف کوچک
    - حذف کاراکترهای خاص
    """
    if pd.isna(name):
        return ""
    name = name.lower().strip()
    name = re.sub(r'[^a-z0-9\s-]', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name

def main():
    print("--- شروع فرآیند یکپارچه‌سازی داده‌ها ---")

    # --- ۱. خواندن فایل‌های داده ---
    try:
        print(f" خواندن فایل اصلی دانشگاه‌ها: {USNEWS_FILE}")
        df_usnews = pd.read_csv(USNEWS_FILE)
        
        print(f" خواندن فایل ددلاین‌ها: {DEADLINES_FILE}")
        df_deadlines = pd.read_csv(DEADLINES_FILE)
        
        print(f" خواندن فایل اساتید: {PROFESSORS_FILE}")
        df_professors = pd.read_csv(PROFESSORS_FILE)
        print("✅ فایل‌ها با موفقیت خوانده شدند.")
    except FileNotFoundError as e:
        print(f"❌ خطا: فایل {e.filename} پیدا نشد. لطفاً مطمئن شوید تمام اسکریپت‌های قبلی را اجرا کرده‌اید.")
        return

    # --- ۲. پردازش و گروه‌بندی اطلاعات اساتید ---
    print("\n پردازش و گروه‌بندی اطلاعات اساتید بر اساس دانشگاه...")
    # حذف ردیف‌های بدون نام استاد
    df_professors.dropna(subset=['name'], inplace=True)
    
    # تبدیل اطلاعات هر استاد به یک دیکشنری و سپس گروه‌بندی بر اساس دانشگاه
    professors_grouped = (
        df_professors.groupby('affiliation')
        .apply(lambda x: x.to_dict('records'))
        .reset_index(name='professors_list')
    )
    # تبدیل لیست دیکشنری‌ها به رشته JSON
    professors_grouped['professors'] = professors_grouped['professors_list'].apply(lambda x: json.dumps(x, indent=2))
    professors_grouped.drop(columns=['professors_list'], inplace=True)
    print(f"✅ اطلاعات {len(df_professors)} استاد در {len(professors_grouped)} دانشگاه گروه‌بندی شد.")

    # --- ۳. نرمال‌سازی نام دانشگاه‌ها برای ادغام بهتر ---
    print("\n نرمال‌سازی نام دانشگاه‌ها برای تطبیق...")
    df_usnews['normalized_name'] = df_usnews['Name'].apply(normalize_name)
    df_deadlines['normalized_name'] = df_deadlines['University'].apply(normalize_name)
    professors_grouped['normalized_name'] = professors_grouped['affiliation'].apply(normalize_name)

    # --- ۴. ادغام (Merge) داده‌ها ---
    print(" ادغام داده‌های US News با اطلاعات ددلاین‌ها...")
    # استفاده از left merge برای نگه داشتن تمام دانشگاه‌های فایل اصلی
    merged_df = pd.merge(
        df_usnews,
        df_deadlines,
        on='normalized_name',
        how='left'
    )

    print(" ادغام نتیجه با اطلاعات اساتید...")
    final_df = pd.merge(
        merged_df,
        professors_grouped,
        on='normalized_name',
        how='left'
    )
    print("✅ ادغام داده‌ها با موفقیت انجام شد.")

    # --- 5. تمیزکاری نهایی و انتخاب ستون‌ها ---
    print("\n تمیزکاری و مرتب‌سازی ستون‌های نهایی...")

    # انتخاب و تغییر نام ستون‌ها
    final_df = final_df.rename(columns={
        'Name': 'university_name',
        'Website': 'university_website',
        'Rankings': 'rankings_data',
        'Data': 'university_data',
        'Found Deadline Info': 'deadline_info', # از df_deadlines
        'Deadline Page URL': 'deadline_url',   # از df_deadlines
        'affiliation': 'affiliation_prof',     # از professors_grouped
    })

    # لیست ستون‌های نهایی به ترتیب دلخواه
    final_columns = [
        'university_name',
        'university_website',
        'university_data',
        'rankings_data',
        'deadline_info',
        'deadline_url',
        'professors'
    ]

    # اطمینان از وجود تمام ستون‌های مورد نیاز و پر کردن مقادیر خالی
    for col in final_columns:
        if col not in final_df.columns:
            final_df[col] = pd.NA

    # انتخاب فقط ستون‌های مورد نیاز و حذف بقیه (شامل normalized_name و ستون‌های اضافی merge)
    final_df = final_df[final_columns].copy()

    # پر کردن مقادیر NaN با رشته‌های مناسب
    final_df['deadline_info'].fillna("Not Found", inplace=True)
    final_df['deadline_url'].fillna("N/A", inplace=True)
    final_df['professors'].fillna("[]", inplace=True) # لیست خالی JSON برای دانشگاه‌های بدون استاد

    # --- ۶. ذخیره فایل نهایی ---
    final_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print("\n🎉 فرآیند یکپارچه‌سازی با موفقیت به پایان رسید!")
    print(f"   فایل نهایی در '{OUTPUT_FILE}' با {len(final_df)} ردیف ذخیره شد.")


if __name__ == "__main__":
    main()
