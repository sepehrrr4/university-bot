# telegram_bot.py
import logging
import os
import pandas as pd 
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
from dotenv import load_dotenv

# --- تنظیمات اولیه ---
# بارگذاری متغیرهای محیطی از فایل .env

# --- بخش ترجمه‌ها ---
translations = {
    "fa": {
        "welcome": "🎓 *به ربات جامع اطلاعات دانشگاه‌ها خوش آمدید!*\n\nبرای شروع، یکی از گزینه‌های زیر را انتخاب کنید:",
        "main_menu_unis": "📚 لیست دانشگاه‌ها",
        "main_menu_help": "❓ راهنما",
        "main_menu_lang": "🌐 تغییر زبان",
        "select_language": "لطفاً زبان مورد نظر خود را انتخاب کنید:",
        "back_to_main_menu": "🔙 بازگشت به منوی اصلی",
        "help_text": (
            "❓ *راهنمای ربات*\n\n"
            "سلام! این ربات برای دسترسی سریع به اطلاعات دانشگاه‌های مختلف طراحی شده است.\n\n"
            "1️⃣ با کلیک روی دکمه «📚 *لیست دانشگاه‌ها*»، فهرست کاملی از دانشگاه‌ها را به صورت صفحه‌بندی شده مشاهده می‌کنید.\n\n"
            "2️⃣ با انتخاب هر دانشگاه، به صفحه جزئیات آن هدایت می‌شوید.\n\n"
            "3️⃣ در صفحه جزئیات، می‌توانید به اطلاعاتی مانند *رنکینگ*، *ددلاین‌ها* و *لیست اساتید* دسترسی پیدا کنید."
        ),
        "uni_list_header": "📖 *لیست دانشگاه‌ها - صفحه {page_num}*\n\nلطفاً دانشگاه مورد نظر خود را انتخاب کنید:",
        "prev_page": "⬅️ صفحه قبل",
        "main_menu_btn": "🔝 منوی اصلی",
        "next_page": "صفحه بعد ➡️",
        "uni_details_website": "🌐 ورود به سایت دانشگاه",
        "uni_details_data": "📊 دیتاها",
        "uni_details_rankings": "🏆 رنکینگ‌ها",
        "uni_details_deadlines": "🗓️ ددلاین‌ها",
        "uni_details_professors": "👨‍🏫 لیست اساتید",
        "uni_details_all_professors": "👨‍🏫 نمایش همه اساتید",
        "uni_details_back_to_list": "🔙 بازگشت به لیست",
        "uni_details_prompt": "لطفاً بخش مورد نظر خود را برای مشاهده اطلاعات انتخاب کنید:",
        "prof_list_header": "👨‍🏫 *لیست اساتید برای {uni_name}* (صفحه {page_num})",
        "prof_list_back": "🔙 بازگشت",
        "no_profs_found": "🔸 لیست اساتیدی برای این دانشگاه یافت نشد.",
        "no_db_found": "😕 متاسفانه در حال حاضر دیتابیسی برای نمایش وجود ندارد. لطفاً از صحت فایل `final_university_database.csv` مطمئن شوید.",
        # ... سایر ترجمه‌های فارسی
    },
    "en": {
        "welcome": "🎓 *Welcome to the University Information Bot!*\n\nPlease select an option to begin:",
        "main_menu_unis": "📚 University List",
        "main_menu_help": "❓ Help",
        "main_menu_lang": "🌐 Change Language",
        "select_language": "Please select your preferred language:",
        "back_to_main_menu": "🔙 Back to Main Menu",
        "help_text": (
            "❓ *Bot Help*\n\n"
            "Hello! This bot is designed for quick access to information about various universities.\n\n"
            "1️⃣ By clicking the '📚 *University List*' button, you can see a paginated list of all universities.\n\n"
            "2️⃣ By selecting a university, you will be taken to its details page.\n\n"
            "3️⃣ On the details page, you can access information like *rankings*, *deadlines*, and the *list of professors*."
        ),
        "uni_list_header": "📖 *List of Universities - Page {page_num}*\n\nPlease select a university:",
        "prev_page": "⬅️ Previous Page",
        "main_menu_btn": "🔝 Main Menu",
        "next_page": "Next Page ➡️",
        "uni_details_website": "🌐 Visit University Website",
        "uni_details_data": "📊 Data",
        "uni_details_rankings": "🏆 Rankings",
        "uni_details_deadlines": "🗓️ Deadlines",
        "uni_details_professors": "👨‍🏫 Professor List",
        "uni_details_all_professors": "👨‍🏫 Show All Professors",
        "uni_details_back_to_list": "🔙 Back to List",
        "uni_details_prompt": "Please select a section to view its information:",
        "prof_list_header": "👨‍🏫 *List of Professors for {uni_name}* (Page {page_num})",
        "prof_list_back": "🔙 Back",
        "no_profs_found": "🔸 No professor list found for this university.",
        "no_db_found": "😕 Unfortunately, no database is available to display. Please ensure the `final_university_database.csv` file is correct.",
    }
}

def t(key: str, context: ContextTypes.DEFAULT_TYPE) -> str:
    """متن ترجمه شده را بر اساس زبان کاربر برمی‌گرداند."""
    lang = context.user_data.get('language', 'fa')  # زبان پیش‌فرض فارسی است
    return translations.get(lang, translations['fa']).get(key, key)

load_dotenv()
# توکن ربات خود را که از BotFather گرفته‌اید، اینجا قرار دهید
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
DATABASE_FILE = "final_university_database.csv"
UNIVERSITIES_PER_PAGE = 8  # تعداد دانشگاه‌ها در هر صفحه
PROFESSORS_PER_PAGE = 10   # تعداد اساتید در هر صفحه

# فعال کردن لاگ برای دیباگ کردن
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# خواندن دیتابیس در ابتدای اجرای ربات
try:
    df_unis = pd.read_csv(DATABASE_FILE)
    # تبدیل مقادیر NaN به رشته خالی برای جلوگیری از خطا
    df_unis.fillna('', inplace=True)
    logger.info(f"✅ دیتابیس با موفقیت بارگذاری شد. {len(df_unis)} دانشگاه یافت شد.")
except FileNotFoundError:
    logger.error(f"❌ فایل دیتابیس '{DATABASE_FILE}' پیدا نشد. لطفاً ابتدا اسکریپت merge_data.py را اجرا کنید.")
    df_unis = pd.DataFrame() # ایجاد دیتافریم خالی برای جلوگیری از کرش

# --- توابع ساخت کیبورد ---

def build_main_menu_keyboard(context: ContextTypes.DEFAULT_TYPE) -> InlineKeyboardMarkup:
    """منوی اصلی ربات را می‌سازد."""
    keyboard = [
        [InlineKeyboardButton(t("main_menu_unis", context), callback_data="show_unis_0")],
        [InlineKeyboardButton(t("main_menu_help", context), callback_data="help")],
        [InlineKeyboardButton(t("main_menu_lang", context), callback_data="change_lang")],
    ]
    return InlineKeyboardMarkup(keyboard)

def build_university_keyboard(context: ContextTypes.DEFAULT_TYPE, page: int = 0) -> InlineKeyboardMarkup:
    """کیبورد صفحه‌بندی شده برای لیست دانشگاه‌ها را می‌سازد."""
    keyboard = []
    start_index = page * UNIVERSITIES_PER_PAGE
    end_index = start_index + UNIVERSITIES_PER_PAGE

    # ایجاد دکمه برای هر دانشگاه در صفحه فعلی
    for idx, row in df_unis.iloc[start_index:end_index].iterrows():
        button = [InlineKeyboardButton(row['university_name'], callback_data=f"uni_{idx}")]
        keyboard.append(button)

    # ایجاد دکمه‌های ناوبری (قبلی/بعدی)
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(t("prev_page", context), callback_data=f"page_{page-1}"))

    # دکمه بازگشت به منوی اصلی
    nav_buttons.append(InlineKeyboardButton(t("main_menu_btn", context), callback_data="main_menu"))

    if end_index < len(df_unis):
        nav_buttons.append(InlineKeyboardButton(t("next_page", context), callback_data=f"page_{page+1}"))

    if nav_buttons:
        keyboard.append(nav_buttons)
        
    return InlineKeyboardMarkup(keyboard)

def build_details_keyboard(context: ContextTypes.DEFAULT_TYPE, uni_index: int, page: int) -> InlineKeyboardMarkup:
    """کیبورد نمایش جزئیات برای یک دانشگاه خاص را می‌سازد."""
    university = df_unis.iloc[uni_index]
    keyboard = [
        [InlineKeyboardButton(t("uni_details_website", context), url=university['university_website'])],
        [
            InlineKeyboardButton(t("uni_details_data", context), callback_data=f"detail_data_{uni_index}"),
            InlineKeyboardButton(t("uni_details_rankings", context), callback_data=f"detail_rank_{uni_index}"),
        ],
        [
            InlineKeyboardButton(t("uni_details_deadlines", context), callback_data=f"detail_deadline_{uni_index}"),
            InlineKeyboardButton(t("uni_details_professors", context), callback_data=f"detail_prof_{uni_index}"),
        ],
    ]
    if university['professors'] and university['professors'] != '[]':
        keyboard.append([InlineKeyboardButton(t("uni_details_all_professors", context), callback_data=f"prof_all_{uni_index}_0")])
    keyboard.append([InlineKeyboardButton(t("uni_details_back_to_list", context), callback_data=f"page_{page}")])
    return InlineKeyboardMarkup(keyboard)

# --- توابع قالب‌بندی متن ---

def format_data(data_json: str) -> str:
    """قالب‌بندی زیبا برای نمایش اطلاعات دیتا."""
    try:
        data = json.loads(data_json)
        if not data:
            return "🔸 اطلاعات کلی برای این دانشگاه ثبت نشده است."
        return "\n".join([f"▫️ *{key}:*  `{value}`" for key, value in data.items()])
    except (json.JSONDecodeError, TypeError):
        return "اطلاعات این بخش به درستی ثبت نشده است."

def format_rankings(rankings_json: str) -> str:
    """قالب‌بندی زیبا برای نمایش رنکینگ‌ها."""
    try:
        ranks = json.loads(rankings_json)
        if not ranks:
            return "🔸 رنکینگی برای این دانشگاه ثبت نشده است."
        # نمایش حداکثر ۱۵ رنکینگ برای جلوگیری از طولانی شدن پیام
        return "\n".join([f"▫️ {rank}" for rank in ranks[:15]])
    except (json.JSONDecodeError, TypeError):
        return "اطلاعات این بخش به درستی ثبت نشده است."

def format_professors_preview(professors_json: str) -> str:
    """قالب‌بندی زیبا برای نمایش پیش‌نمایش لیست اساتید."""
    try:
        profs = json.loads(professors_json)
        if not profs:
            return "🔸 لیست اساتیدی برای این دانشگاه یافت نشد."
        
        # نمایش حداکثر ۵ استاد برای پیش‌نمایش
        output = []
        for p in profs[:5]:
            name = p.get('name', 'N/A')
            areas = p.get('areas', 'N/A')
            output.append(f"👨‍🏫 *{name}*\n    *حوزه‌ها:* `{areas}`")
        
        if len(profs) > 5:
            output.append(
                f"\n... و {len(profs) - 5} استاد دیگر.\n"
                "برای مشاهده لیست کامل، روی دکمه \"👨‍🏫 نمایش همه اساتید\" کلیک کنید."
            )
            
        return "\n\n".join(output)
    except (json.JSONDecodeError, TypeError):
        return "اطلاعات این بخش به درستی ثبت نشده است."

def build_professors_paginated(context: ContextTypes.DEFAULT_TYPE, uni_index: int, prof_page: int = 0):
    """یک صفحه از لیست اساتید را به همراه دکمه‌های صفحه‌بندی ایجاد می‌کند."""
    university = df_unis.iloc[uni_index]
    profs = json.loads(university['professors'])
    
    start_index = prof_page * PROFESSORS_PER_PAGE
    end_index = start_index + PROFESSORS_PER_PAGE
    
    output = [t("prof_list_header", context).format(uni_name=university['university_name'], page_num=prof_page + 1)]
    
    for p in profs[start_index:end_index]:
        name = p.get('name', 'N/A')
        homepage = p.get('homepage', '')
        areas = p.get('areas', 'N/A')
        
        name_part = f"*{name}*"
        if homepage and homepage != "N/A":
            # ایجاد لینک قابل کلیک با Markdown
            name_part = f"{name}"
        output.append(f"👤 {name_part}\n    *حوزه‌ها:* `{areas}`")

    text = "\n\n".join(output)

    # ساخت دکمه‌های ناوبری
    nav_buttons = []
    if prof_page > 0:
        nav_buttons.append(InlineKeyboardButton(t("prev_page", context), callback_data=f"prof_page_{uni_index}_{prof_page-1}"))
    
    # دکمه بازگشت به منوی دانشگاه
    page = uni_index // UNIVERSITIES_PER_PAGE
    nav_buttons.append(InlineKeyboardButton(t("prof_list_back", context), callback_data=f"uni_{uni_index}"))

    if end_index < len(profs):
        nav_buttons.append(InlineKeyboardButton(t("next_page", context), callback_data=f"prof_page_{uni_index}_{prof_page+1}"))

    keyboard = InlineKeyboardMarkup([nav_buttons])
    return text, keyboard

# --- کنترل‌کننده‌های ربات (Handlers) ---

async def show_university_details(query: Update.callback_query, context: ContextTypes.DEFAULT_TYPE, uni_index: int, category: str = None):
    """جزئیات یک دانشگاه را بر اساس دسته‌بندی نمایش می‌دهد."""
    page = uni_index // UNIVERSITIES_PER_PAGE
    university = df_unis.iloc[uni_index]
    
    text = f"🏛️ *{university['university_name']}*\n\n"
    
    if category == "data":
        text += f"📊 *{t('uni_details_data', context)}:*\n\n" + format_data(university['university_data'])
    elif category == "rank":
        text += f"🏆 *{t('uni_details_rankings', context)} (Sample):*\n\n" + format_rankings(university['rankings_data'])
    elif category == "deadline":
        text += f"🗓️ *{t('uni_details_deadlines', context)}:*\n\n" + (university['deadline_info'] or "اطلاعاتی ثبت نشده است.")
        if university['deadline_url'] and university['deadline_url'] != 'N/A':
            text += f"\n\n🔗 [مشاهده صفحه اصلی ددلاین]({university['deadline_url']})"
    elif category == "prof":
        text += f"👨‍🏫 *{t('uni_details_professors', context)} (Preview):*\n\n" + format_professors_preview(university['professors'])
    else: # حالت پیش‌فرض، بدون انتخاب دسته‌بندی
        text += t('uni_details_prompt', context)

    keyboard = build_details_keyboard(context, uni_index, page)
    await query.edit_message_text(
        text=text,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی اصلی را نمایش می‌دهد یا ویرایش می‌کند."""
    keyboard = build_main_menu_keyboard(context)
    text = t("welcome", context)
    
    # اگر از یک دکمه آمده باشد، پیام را ویرایش می‌کند، در غیر این صورت پیام جدید می‌فرستد
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """دستور /start را مدیریت می‌کند و منوی اصلی را نمایش می‌دهد."""
    if df_unis.empty:
        # چون هنوز زبان کاربر مشخص نیست، از هر دو زبان استفاده می‌کنیم یا یک زبان پیش‌فرض
        await update.message.reply_text(
            "😕 متاسفانه در حال حاضر دیتابیسی برای نمایش وجود ندارد.\n\n"
            "😕 Unfortunately, no database is available to display."
        )
        return
    context.user_data.setdefault('language', 'fa') # تنظیم زبان پیش‌فرض برای کاربر جدید
    await show_main_menu(update, context)
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تمام کلیک‌های روی دکمه‌های شیشه‌ای را مدیریت می‌کند."""
    query = update.callback_query
    await query.answer()  # پاسخ به تلگرام برای بستن انیمیشن لودینگ دکمه
    
    data = query.data
    
    # بازگشت به منوی اصلی
    if data == "main_menu":
        await show_main_menu(update, context)
        return
    
    # نمایش راهنما
    if data == "help":
        text = t("help_text", context)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(t("back_to_main_menu", context), callback_data="main_menu")]])
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

    # نمایش منوی تغییر زبان
    elif data == "change_lang":
        keyboard = [
            [InlineKeyboardButton("🇮🇷 فارسی (Persian)", callback_data="set_lang_fa")],
            [InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en")],
            [InlineKeyboardButton(t("back_to_main_menu", context), callback_data="main_menu")]
        ]
        await query.edit_message_text(text=t("select_language", context), reply_markup=InlineKeyboardMarkup(keyboard))

    # تنظیم زبان
    elif data.startswith("set_lang_"):
        lang_code = data.split("_")[-1]
        context.user_data['language'] = lang_code
        await show_main_menu(update, context) # نمایش مجدد منوی اصلی با زبان جدید

    # صفحه‌بندی لیست دانشگاه‌ها
    if data.startswith("show_unis_") or data.startswith("page_"):
        if data.startswith("show_unis_"):
            page = int(data.split("_")[2])
        else: # data.startswith("page_")
            page = int(data.split("_")[1])
        keyboard = build_university_keyboard(context, page)
        await query.edit_message_text(
            text=t("uni_list_header", context).format(page_num=page + 1),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
        
    # انتخاب یک دانشگاه
    elif data.startswith("uni_"):
        uni_index = int(data.split("_")[1])
        await show_university_details(query, context, uni_index)

    # نمایش جزئیات یک بخش خاص
    elif data.startswith("detail_"):
        _, category, uni_index_str = data.split("_")
        uni_index = int(uni_index_str)
        await show_university_details(query, context, uni_index, category)
        
    # نمایش لیست کامل اساتید (صفحه‌بندی شده)
    elif data.startswith("prof_all_") or data.startswith("prof_page_"):
        parts = data.split("_")
        uni_index = int(parts[-2]) # uni_index همیشه یکی قبل از آخری است
        # prof_page از آخرین بخش callback_data گرفته می‌شود
        prof_page = int(parts[-1])

        try:
            text, keyboard = build_professors_paginated(context, uni_index, prof_page)
            await query.edit_message_text(
                text=text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
        except (IndexError, json.JSONDecodeError):
            await query.edit_message_text(text=t("no_profs_found", context), reply_markup=query.message.reply_markup)
            return

def main() -> None:
    """ربات را اجرا می‌کند."""
    if TELEGRAM_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE" or df_unis.empty:
        print("❌ توکن ربات تلگرام تنظیم نشده یا فایل دیتابیس خالی است. لطفاً فایل telegram_bot.py را ویرایش کنید.")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # افزودن کنترل‌کننده‌ها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))

    print("🚀 ربات در حال اجراست... برای توقف Ctrl+C را بزنید.")
    application.run_polling()

if __name__ == "__main__":
    main()
