# config.py

# URL اصلی که لیست دانشگاه‌ها در آن قرار دارد
BASE_URL = "https://www.usnews.com/education/best-global-universities/united-states/computer-science"

# سلکتور برای دکمه "Load More"
PAGINATION_NEXT_BUTTON_SELECTOR = "#load-more-button"

# سلکتور برای پیدا کردن بلاک (کارت) هر دانشگاه در لیست
UNIVERSITY_LIST_ITEM_SELECTOR = "li[class*='item-list__ListItemStyled']"

# سلکتور برای لینک صفحه داخلی (Detail) هر دانشگاه (که روی آن کلیک می‌کنیم)
UNIVERSITY_DETAIL_LINK_SELECTOR = "h2 a[href*='/education/best-global-universities/']"


# -----------------------------------------------------------------
# ۲. تنظیمات صفحه داخلی (صفحه جزئیات هر دانشگاه)
# -----------------------------------------------------------------

# سلکتور برای نام دانشگاه
DETAIL_NAME_SELECTOR = "div[class*='Villain__TitleContainer'] h1"

# سلکتور برای لینک وب‌سایت رسمی دانشگاه
DETAIL_WEBSITE_SELECTOR = "a[class*='WebsiteIconLink__IconAnchor']"

# سلکتور برای بلاک "University Data" (که شامل آمار است)
# ما از ID که شما پیدا کردید استفاده می‌کنیم
DETAIL_DATA_CONTAINER_SELECTOR = "#uniData"

# سلکتور برای هر "ردیف" از آمار در بلاک بالا
DETAIL_DATA_ROW_SELECTOR = "div[class*='DataRow__Row']"
# در هر ردیف بالا:
#   - سلکتور کلید (Label): p:first-child
#   - سلکتور مقدار (Value): p:last-child

# سلکتور برای بلاک "Rankings"
# ما از ID که شما پیدا کردید استفاده می‌کنیم
DETAIL_RANKINGS_CONTAINER_SELECTOR = "#rankings"

# سلکتور برای هر "آیتم" رنکینگ در بلاک بالا
DETAIL_RANKINGS_ITEM_SELECTOR = "li[class*='RankList__ListItem']"
# در هر آیتم بالا:
#   - سلکتور رتبه (عدد): p[class*='RankList__Rank']
#   - سلکتور موضوع رتبه: p[class*='RankList__Subject']
DETAIL_RANKINGS_RANK_TEXT_SELECTOR = "div[class*='RankList__Rank']"
DETAIL_RANKINGS_SUBJECT_TEXT_SELECTOR = "a > strong:last-of-type"