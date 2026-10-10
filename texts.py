# ==================== متن‌های فارسی ربات ====================

# ---- پیام‌های عمومی ----
WELCOME = "سلام! به ربات اتصال متخصصین خوش آمدید 👋"
WELCOME_BACK = "خوش برگشتی! 👋"
USE_MENU = "از منو استفاده کنید."
INVALID_INPUT = "مقدار معتبر نیست. دوباره تلاش کنید."
CHOOSE_OPTION = "یک گزینه را انتخاب کنید:"
ERR = "خطا"
ERR_NOT_FOUND = "پیدا نشد."

# ---- منوی اصلی ----
BTN_REGISTER = "🏪 ثبت‌نام متخصص"
BTN_SEARCH_SIMPLE = "🔍 جستجوی ساده"
BTN_SEARCH_ADVANCED = "🔎 جستجوی پیشرفته"
BTN_EXPERTS_LIST = "📋 لیست متخصصین"
BTN_MY_PROFILE = "👤 پروفایل من"
BTN_FEEDBACK = "💬 نظرات و پیشنهادات"
BTN_SHOP_STATUS = "🏪 وضعیت مغازه"
BTN_WALLET = "💰 کیف پول من"
BTN_CHARGE_WALLET = "📸 شارژ کیف پول"
BTN_BACK = "🔙 بازگشت"
BTN_HOME = "🏠 منوی اصلی"

# ---- دسته‌بندی‌ها ----
CAT_ELEC = "🔌 لوازم برقی"
CAT_GAS = "🔥 لوازم گازی"
CAT_COOL = "❄️ سرمایشی و گرمایشی"
CAT_CAR = "🚗 خودرو"

# ---- پاسخ‌های عمومی ----
YES = "✅ بله"
NO = "❌ خیر"
WHO_ME = "👤 خودم انتخاب می‌کنم"
WHO_SYS = "🤖 سیستم انتخاب کند"

# ---- ثبت‌نام ----
ASK_NAME = "نام و نام خانوادگی:"
ASK_PHONE = "شماره تماس:"
ASK_CITY = "شهر خود را وارد کنید:"
ASK_AREA = "محله یا محدوده خدمات را وارد کنید (مثلاً سعادت‌آباد):"
ASK_LOCATION = """برای جذب مشتریان بیشتر، توصیه می‌شود موقعیت مکانی خود را هم ثبت کنید.
آیا می‌خواهید الان ثبت کنید؟"""
ASK_SEND_LOCATION = "لطفاً روی دکمه زیر بزنید تا موقعیتتان ارسال شود:"
LOCATION_SAVED = "✅ موقعیت شما ثبت شد."
ASK_ONSITE = "آیا در محل مشتری حاضر می‌شوید؟"
ASK_RESPONSE_SPEED = "⏱ سرعت پاسخگویی:"
ASK_REPAIR_TIME = "🔧 زمان تعمیر:"
REGISTER_OK = "✅ ثبت‌نام انجام شد!"
REGISTER_PENDING = """✅ ثبت‌نام شما ثبت شد و در انتظار تأیید مدیر است.
پس از تأیید، به شما اطلاع داده می‌شود."""

# ---- سرعت پاسخگویی ----
RESPONSE_TIMES = [
    "همیشه در دسترس (فوری)",
    "حداکثر نیم ساعت",
    "چند ساعت",
    "با تعیین وقت قبلی",
]

# ---- زمان تعمیر ----
REPAIR_TIMES = [
    "کمتر از یک ساعت",
    "نصف روز",
    "یک روز",
    "چند روز",
]

# ---- درخواست مشتری ----
ASK_CUST_AREA = "محدوده خودتان را تایپ کنید یا موقعیت بفرستید:"
ASK_DESC = "مشکل را توضیح دهید:"
ASK_PHONE_SHARE = "آیا شماره تماستان برای تعمیرکار ارسال شود؟"
ASK_PHONE_INPUT = "شماره تماستان را وارد کنید:"
ASK_WHO_PICK = "خودتان تعمیرکار را انتخاب می‌کنید یا سیستم؟"

# ---- جستجوی پیشرفته ----
ASK_PRIORITY = "کدام معیارها مهم‌تره؟ شماره بزنید (مثلاً 1,4). یا 0 برای هیچ‌کدام.\n\n"
ASK_HANDOVER = "چه زمانی می‌خواهید دستگاه را تحویل بدهید؟\n\n"
ASK_RETURN = "چه زمانی دستگاه را لازم دارید؟\n\n"

HANDOVER_TIMES = [
    "فوری (تا نیم ساعت)",
    "تا چند ساعت",
    "امروز",
    "فردا یا بعدتر",
]

RETURN_TIMES = [
    "امروز",
    "فردا",
    "تا ۲-۳ روز",
    "تا هفته",
    "عجله‌ای نیست",
]

# ---- معیارهای امتیازدهی ----
CRITERIA = [
    {"key": "price",          "label": "💰 دستمزد مناسب"},
    {"key": "behavior",       "label": "😊 اخلاق خوب"},
    {"key": "speed",          "label": "⚡ سرعت عمل"},
    {"key": "quality",        "label": "✨ کیفیت کار"},
    {"key": "punctuality",    "label": "🕐 وقت‌شناسی"},
    {"key": "cleanliness",    "label": "🧹 نظافت"},
    {"key": "warranty",       "label": "🛡 ضمانت کار"},
    {"key": "responsiveness", "label": "📞 پاسخگویی"},
]

# ---- نتایج جستجو ----
FOUND_EXPERTS = "🔍 متخصصین برتر:\n\n"
NOT_FOUND = "❌ متخصصی پیدا نشد."
CALL_DIRECT = "\n⚠️ لطفاً مستقیم تماس بگیرید."
NEW_CUSTOMER = "🔔 مشتری جدید!"
CHOSEN_EXPERT = "👤 تعمیرکار انتخابی:\n"
NO_EXPERTS = "هنوز متخصصی نیست."
TRACKING_NOTE = "\n\nلطفاً هنگام مراجعه کد را به تعمیرکار بدهید."

# ---- پروفایل ----
MY_PROFILE = "👤 پروفایل شما:\n\n"
NO_PROFILE = "ثبت‌نام نکردید."
LBL_NAME = "👤 نام: "
LBL_ROLE = "📂 دسته: "
LBL_SUBSPEC = "🔧 زیرتخصص: "
LBL_AREA = "📍 محدوده: "
LBL_PHONE = "📞 تلفن: "
LBL_ONSITE = "🏠 حضور در محل: "
LBL_RATING = "⭐ امتیاز: "
LBL_REFERRAL = "📈 تعداد معرفی: "
LBL_PROBLEM = "📝 مشکل: "
LBL_TRACKING = "🎫 کد پیگیری: "
LBL_CODE = "🆔 کد شما: "
LBL_LINK = "🔗 لینک شما:\n"
SHARE_HINT = "\n\nلینک خودتان را برای مشتریان ارسال کنید."
BTN_SHARE = "🔗 نمایش لینک اشتراک"
BTN_COPY_LINK = "📋 کپی لینک"
PUBLIC_PROFILE = "👤 پروفایل متخصص:\n\n"
WELCOME_VIA_LINK = "شما از طریق لینک وارد شدید:"
EXPERT_NOT_FOUND = "❌ متخصصی با این کد پیدا نشد."

# ---- امتیازدهی ----
RATE_ASK = "لطفاً به تعمیرکار امتیاز بدهید:"
RATE_THX = "🙏 ممنون!"
RATE_START = "⭐ امتیاز به "
RATE_SELECT = "\nامتیاز (۱-۵):"
RATE_OK = "ثبت"
RATE_COMMENT_ASK = "\n\nمی‌خواهی نظر هم بنویسی؟ (اختیاری)"
RATE_COMMENT_SKIP = "⏭ رد کردن"
RATE_COMMENT_THX = "✅ نظر شما ثبت شد."

# ---- نظرسنجی دوره‌ای ----
FOLLOWUP_1MONTH = "🔔 یک ماه از خدمات {name} گذشت.\nنظر جدیدتان چیه؟"
FOLLOWUP_6MONTH = "🔔 شش ماه از خدمات {name} گذشت.\nنظر بلندمدت شما برای ما ارزشمنده."
FOLLOWUP_BTN = "⭐ ثبت نظر جدید"

# ---- مسیریابی ----
BTN_NAV_NESHAN = "📍 مسیریابی با نشان"
BTN_NAV_GOOGLE = "🗺 مسیریابی با گوگل مپ"

# ---- وضعیت مغازه ----
SHOP_STATUS_TITLE = "🏪 وضعیت مغازه:\n"
SHOP_ACTIVE = "🟢 فعال (دریافت مشتری)"
SHOP_CLOSED_TEMP = "🟡 تعطیل موقت"
SHOP_CLOSED_PERM = "🔴 تعطیل دائم"
SHOP_ASK = "وضعیت مغازه را انتخاب کنید:"
SHOP_ASK_FROM_DAY = """از چند روز دیگه می‌خوای مغازه تعطیل شه؟
0 = از امروز
1 = از فردا
4 = از 4 روز دیگه
"""
SHOP_ASK_DAYS = "چند روز تعطیل باشه؟"
SHOP_ASK_REASON = "دلیل تعطیلی را بنویسید (یا بنویسید مهم نیست):"
SHOP_SKIP_REASON = "مهم نیست"
SHOP_CLOSE_OK = "✅ مغازه تعطیل شد."
SHOP_REOPEN = "🔓 فعال سازی مجدد"
SHOP_REOPENED = "مغازه فعال شد."
SHOP_REOPENED_NOTIFY = "🔔 مغازه شما مجدداً فعال شد."
SHOP_COUNTDOWN = "⏳ تا فعال شدن: "
SHOP_DAYS = " روز"

# ---- نظرات و پیشنهادات ----
FEEDBACK_MSG = """💬 نظرات، پیشنهادات و شکایات خود را به آیدی زیر ارسال کنید:

📌 لطفاً جهت بالا بردن کیفیت و رضایت کاربران، اسم مشاغلی که در لیست نیست رو به ما اطلاع دهید.

"""

"""
FEEDBACK_EMPTY = "در حال حاضر آیدی تماس تنظیم نشده است."

# ---- پنل ادمین ----
ADM_TITLE = "🔐 پنل مدیریت"
ADM_ASK_PASS = "🔐 لطفاً رمز عبور را وارد کنید:"
ADM_WRONG_PASS = "❌ رمز عبور اشتباه است."
ADM_NOT_AUTH = "شما دسترسی ندارید."

ADM_STATS = "📊 آمار کلی"
ADM_EXPERTS = "👥 متخصصین"
ADM_PENDING = "⏳ در انتظار تأیید"
ADM_JOBS = "📋 آخرین معرفی‌ها"
ADM_REVENUE = "💰 درآمد"
ADM_OPERATORS = "👥 مدیران"
ADM_CHANGE_PASS = "🔐 تغییر رمز عبور"
ADM_EXIT = "🔙 خروج"
ADM_BACK = "🔙 بازگشت"

ADM_APPROVE = "✅ تأیید"
ADM_REJECT = "❌ رد"
ADM_APPROVED_OK = "تأیید شد."
ADM_REJECTED_OK = "رد شد."

ADM_TOGGLE_ON = "✅ فعال"
ADM_TOGGLE_OFF = "❌ غیرفعال"
ADM_PREMIUM_ON = "⭐ اشتراک ویژه"
ADM_PREMIUM_OFF = "⭐ حذف اشتراک"
ADM_DELETE = "🗑 حذف"
ADM_DELETED = "متخصص حذف شد."

ADM_NEW_EXPERT = "🔔 متخصص جدید در انتظار تأیید:"
ADM_NO_PENDING = "هیچ متخصصی در انتظار تأیید نیست."
ADM_NO_EXPERT = "هیچ متخصصی نیست."
ADM_NO_OPERATOR = "هیچ مدیری تعیین نشده."
ADM_ASK_OP_ID = "آیدی عددی مدیر جدید را وارد کنید:"
ADM_OP_ADDED = "مدیر اضافه شد."
ADM_ADD_OP = "➕ افزودن مدیر"
ADM_RM_OP = "➖ حذف مدیر"

ADM_ASK_PASS_FERST = "🔐 برای اولین بار یک رمز عبور حداقل 4 کاراکتری وارد کنید:"
ADM_ENTER_NEW_PASS = "🔐 رمز عبور جدید را وارد کنید:"
ADM_ENTER_AGAIN = "🔐 رمز عبور را دوباره وارد کنید:"
ADM_PASS_MISMATCH = "❌ رمزها یکسان نیستند."
ADM_PASS_SHORT = "❌ رمز باید حداقل ۴ کاراکتر باشد."
ADM_PASS_SET_OK = "✅ رمز عبور تنظیم شد."

# ---- اعلان‌های تعمیرکار ----
EXP_APPROVED_NOTIFY = "🎉 تبریک! ثبت‌نام شما تأیید شد."
EXP_REJECTED_NOTIFY = "متأسفانه ثبت‌نام شما تأیید نشد."

# ---- اعلان‌های مرحله‌ای ----
FREE_WARN_25 = """⚠ توجه!

شما تا حالا 25 مشتری از طریق ربات گرفتید.
فقط 5 مشتری دیگه رایگان دارید.

بعد از این 5 مشتری، برای هر مشتری جدید باید هزینه پرداخت کنید."""
FREE_WARN_28 = """🔴 هشدار جدی!

شما تا حالا 28 مشتری گرفتید.
فقط 2 مشتری دیگه رایگان دارید!"""
FREE_END_30 = """🎉 تبریک!

شما از 30 مشتری رایگان استفاده کردید.
از این به بعد، برای هر مشتری جدید باید هزینه پرداخت کنید.

برای ادامه با پشتیبانی در تماس باشید."""
FREE_NO_BALANCE = """🔔 یک مشتری جدید درخواست داده!

❗ متأسفانه موجودی کیف پول شما کافی نیست.
برای دیدن مشتری، لطفاً کیف پول خود را شارژ کنید."""

# ---- Fuzzy Match ----
FUZZY_CONFIRM = "🔍 آیا منظور شما «{city}» بود؟"
FUZZY_YES = "✅ بله"
FUZZY_NO = "❌ خیر"
FUZZY_MULTIPLE = "🔍 چند شهر مشابه پیدا کردم:\n\n"
FUZZY_NO_MATCH = "❌ شهری با این نام پیدا نکردم."
FUZZY_SUGGEST_LOCATION = "📍 می‌تونی لوکیشنت رو بفرستی یا اسم شهر رو دوباره بنویسی."
FUZZY_SUGGEST_LOC_AFTER = "📍 برای نتیجه دقیق‌تر، لوکیشن بفرستید."
FUZZY_CITY_NOT_FOUND = """❌ شهر «{city}» در لیست شهرهای ما پیدا نشد.

📍 راهنما:
• اسم شهر رو دقیق‌تر بنویسید
• یا موقعیت مکانی خود را ارسال کنید

مثال: تهران، بهبهان، اهواز"""
FUZZY_LOCATION_HINT = "📍 موقعیت مکانی شما ثبت شد.\n\nحالا مشکل را توضیح دهید:"

# ==================== کیف پول ====================
WALLET_TITLE = "💰 کیف پول شما\n\n"
WALLET_BALANCE = "💵 موجودی: {balance} تومان\n"
WALLET_FREE_PERIOD = "🎁 شما در دوره رایگان هستید (۳۰ روز یا ۳۰ مشتری)\n"
WALLET_FREE_LEFT = "⏳ {days} روز یا {customers} نفر تا پایان دوره رایگان\n"
WALLET_STATUS_FREE = "✅ وضعیت: رایگان"
WALLET_STATUS_CHARGED = "✅ وضعیت: فعال"
WALLET_STATUS_LOW = "⚠️ وضعیت: موجودی کم"
WALLET_STATUS_EMPTY = "❌ وضعیت: بدون شارژ (پایین‌تر نمایش داده می‌شوید)"
WALLET_HISTORY = "\n📋 آخرین تراکنش‌ها:\n"

WALLET_CHARGE_INTRO = """💳 برای شارژ کیف پول:

1️⃣ مبلغ مورد نظر را به شماره کارت زیر واریز کنید:

💳 شماره کارت: {card}
👤 صاحب کارت: {owner}

2️⃣ بعد از واریز، همین‌جا مبلغ را تایپ کنید و بفرستید.

مثلاً: 100000"""

WALLET_ASK_AMOUNT = "💰 لطفاً مبلغ شارژ را وارد کنید (تومان):\n\nمثلاً: 100000"
WALLET_INVALID_AMOUNT = "❌ مبلغ نامعتبر. لطفاً یه عدد بین 10,000 تا 10,000,000 وارد کنید."
WALLET_ASK_RECEIPT = """✅ مبلغ: {amount} تومان

📸 لطفاً عکس رسید پرداخت را ارسال کنید."""

WALLET_RECEIPT_SENT = """✅ رسید شما دریافت شد.

⏳ در انتظار تأیید مدیر. بعد از تأیید به شما اطلاع داده می‌شود."""

WALLET_ADMIN_NEW = """💰 درخواست شارژ کیف پول

👤 تعمیرکار: {name}
🆔 آیدی: {user_id}
📞 تلفن: {phone}
💵 مبلغ: {amount} تومان
📅 تاریخ: {date}

عکس رسید بالا ⬆️"""

WALLET_APPROVED_NOTIFY = """🎉 شارژ کیف پول تأیید شد!

💵 مبلغ: {amount} تومان
💰 موجودی جدید: {balance} تومان"""

WALLET_REJECTED_NOTIFY = """❌ متأسفانه درخواست شارژ شما رد شد.

📝 دلیل: {reason}

برای اطلاعات بیشتر با مدیر تماس بگیرید."""

# ---- لوکیشن ----
PROFILE_LOCATION_ASK = "لطفاً موقعیت مکانی خود را ارسال کنید:"
PROFILE_LOCATION_SAVED = "✅ موقعیت مکانی ثبت شد."
LOCATION_WARNING = """⚠️ توجه: شما موقعیت مکانی ثبت نکردید.
با ثبت موقعیت، مشتریان راحت‌تر شما را پیدا می‌کنند."""
BTN_SET_LOCATION = "📍 ثبت موقعیت مکانی"

# ---- پروفایل مشتری ----
CUSTOMER_PROFILE_TITLE = "📜 فعالیت‌های ۶ ماه اخیر شما\n\n"
CUSTOMER_NO_ACTIVITY = """هنوز درخواستی ثبت نکردی.

از منوی اصلی می‌تونی جستجوی تعمیرکار کنی:"""
CUSTOMER_SUMMARY = "📊 خلاصه:\n"
CUSTOMER_TOTAL = "• کل درخواست‌ها: "
CUSTOMER_LAST = "• آخرین درخواست: "
CUSTOMER_ITEM_HEADER = "━━━━━━━━━━━━━━━━━\n"
CUSTOMER_HISTORY_FOOTER = "━━━━━━━━━━━━━━━━━\nℹ️ اطلاعات بعد از ۶ ماه به دلایل قانونی حذف می‌شود."

# ---- QR کد ----
BTN_SHOW_QR = "🔳 نمایش QR کد"
QR_HINT = """🔳 QR کد اختصاصی شما

روی دکمه زیر بزنید تا QR کد رو ببینید.
می‌تونید ازش اسکرین‌شات بگیرید و چاپ کنید.
"""

# ==================== ویرایش (ربات ادمین) ====================
BTN_EDIT = "✏️ ویرایش"
BTN_EDIT_CATEGORIES = "📂 ویرایش دسته‌بندی‌ها"
BTN_EDIT_TARIFFS = "💰 ویرایش تعرفه‌ها"
BTN_EDIT_FEEDBACK = "💬 ویرایش آیدی نظرات"
BTN_EDIT_CARD = "💳 ویرایش شماره کارت"
BTN_SAVE = "💾 ذخیره"
BTN_CANCEL = "❌ انصراف"

EDIT_MENU_TITLE = """✏️ منوی ویرایش

یکی از گزینه‌ها را انتخاب کنید:"""

EDIT_CATEGORIES_TITLE = """📂 ویرایش دسته‌بندی‌ها

دسته‌های فعلی:
"""
EDIT_CATEGORY_ASK_NEW = "📂 نام دسته‌بندی جدید را وارد کنید:"
EDIT_CATEGORY_ADDED = "✅ دسته‌بندی جدید اضافه شد."
EDIT_CATEGORY_EXISTS = "⚠️ این دسته‌بندی قبلاً وجود داره."
EDIT_CATEGORY_ASK_DELETE = "روی دسته‌ای که می‌خواهید حذف کنید بزنید:"
EDIT_CATEGORY_DELETED = "✅ دسته‌بندی حذف شد."

EDIT_TARIFFS_TITLE = """💰 ویرایش تعرفه‌ها

تعرفه‌های فعلی:
"""
EDIT_TARIFF_ASK = "💰 تعرفه جدید برای «{category}» را وارد کنید (تومان):\n\nمثال: 50000"
EDIT_TARIFF_UPDATED = "✅ تعرفه به {amount} تومان بروزرسانی شد."
EDIT_TARIFF_INVALID = "❌ مبلغ نامعتبر. یه عدد بین 10,000 تا 10,000,000 وارد کنید."

EDIT_FEEDBACK_ASK = "💬 آیدی نظرات جدید را وارد کنید (با @):\n\nمثال: @username"
EDIT_FEEDBACK_UPDATED = "✅ آیدی نظرات بروزرسانی شد: {id}"

EDIT_CARD_ASK = """💳 اطلاعات کارت جدید:

شماره کارت را وارد کنید (مثال: 6037-XXXX-XXXX-XXXX):"""
EDIT_CARD_OWNER_ASK = "👤 نام صاحب کارت را وارد کنید:"
EDIT_CARD_UPDATED = """✅ اطلاعات کارت بروزرسانی شد.

💳 شماره کارت: {card}
👤 صاحب کارت: {owner}"""

EDIT_SAVED = "✅ تغییرات ذخیره شد."
EDIT_CANCELED = "❌ لغو شد."

# ==================== ویرایش کلی تعرفه (درصدی) ====================
BTN_BULK_TARIFF = "📈 ویرایش کلی (درصدی)"
EDIT_BULK_TITLE = """📈 ویرایش کلی تعرفه‌ها

با این ابزار می‌توانید همه تعرفه‌ها را با یک درصد مشخص
افزایش یا کاهش دهید.

مثال:
• ورود 12 = افزایش ۱۲٪
• ورود -10 = کاهش ۱۰٪

📌 توجه: هر تعرفه بعد از محاسبه، به ۱۰۰۰ تومان پایین رند می‌شود.
مثال: 128,236 → 128,000"""
EDIT_BULK_ASK = "📈 چند درصد تغییر بدهیم؟ (مثبت برای افزایش، منفی برای کاهش):\n\nمثال: 12 یا -10"
EDIT_BULK_INVALID = "❌ مقدار نامعتبر. یه عدد بین -50 تا +100 وارد کنید."
EDIT_BULK_PREVIEW = """📊 پیش‌نمایش تغییرات:

🔢 تعداد تعرفه‌ها: {count}
📈 درصد تغییر: {percent}٪

💰 مثال:
• ماکروفر: {ex_old1} → {ex_new1}
• ماشین لباسشویی: {ex_old2} → {ex_new2}

آیا اعمال شود؟
[✅ بله] [❌ انصراف]"""
EDIT_BULK_DONE = """✅ تغییرات با موفقیت اعمال شد.

🔢 تعداد تعرفه‌های بروزرسانی شده: {count}
📈 درصد تغییر: {percent}٪"""
EDIT_BULK_CANCELED = "❌ ویرایش کلی لغو شد."

# ==================== امتیازدهی جداگانه هر تخصص ====================
RATING_BY_SPEC = "⭐ امتیاز به تفکیک تخصص:\n\n"
RATING_SPEC_LINE = "• {spec}: {avg} ({count} نظر)\n"
RATING_NO_SPEC = "هنوز نظری برای این تخصص ثبت نشده."
RATING_CUSTOMER_HINT = """🎯 امتیاز در تخصص «{spec}»:

{avg}/5 ({count} نظر)
"""
RATING_SHOW_ALL = "📊 مشاهده همه امتیازها"
BTN_SHOW_ALL_RATINGS = "📊 همه امتیازها"

# ==================== نظرات متنی ====================
COMMENT_ASK = """💬 اگر می‌خواهید نظر خود را هم بنویسید:

(اختیاری - می‌توانید رد کنید)"""
COMMENT_SKIP_BTN = "⏭ رد کردن"
COMMENT_SAVED = "✅ نظر شما ثبت شد."
COMMENT_THANKS = "🙏 ممنون از نظر شما!"
COMMENTS_HEADER = "\n📝 نظرات کاربران:\n\n"
COMMENTS_NO = "هنوز نظری ثبت نشده."
COMMENTS_ITEM = """⭐ {stars}/5 - {name}
«{comment}»
📅 {date}
"""
COMMENTS_ITEM_ANON = """⭐ {stars}/5 - ناشناس
«{comment}»
📅 {date}
"""
COMMENT_ASK_NAME = "نام نمایشی برای نظر (مثلاً «علی ر»):"
BTN_COMMENT_WITH_NAME = "👤 با نام"
BTN_COMMENT_ANON = "🕵️ ناشناس"

# ==================== لاگ عیوب دستگاه ====================
DEVICE_LOG_TITLE = "📋 عیوب دستگاه:\n"
DEVICE_LOG_ADD = "➕ افزودن عیب"
DEVICE_LOG_EDIT = "✏️ ویرایش"
DEVICE_LOG_DELETED = "🗑 حذف"
DEVICE_LOG_NOT_FOUND = "❌ لاگی برای این دستگاه پیدا نشد."
DEVICE_LOG_ASK_DESC = "📝 عیب دستگاه را توضیح دهید:"
DEVICE_LOG_SAVED = "✅ عیب ثبت شد."
DEVICE_LOG_LIST = """📋 لاگ عیوب دستگاه:

🎫 کد پیگیری: {code}
🔧 دستگاه: {device}

━━━━━━━━━━━━━━━━━
{logs}
━━━━━━━━━━━━━━━━━
✅ این گزارش مدرک رسمی محسوب می‌شود."""
DEVICE_LOG_ITEM = """📝 {date}
👤 {author} {role}:
«{text}»
"""
DEVICE_LOG_ITEM_EDIT = """📝 {date}
👤 {author} {role} - ✏️ ویرایش شده:
«{text}»
قبل: «{old_text}»
"""
DEVICE_LOG_ROLE_CUSTOMER = "(مشتری)"
DEVICE_LOG_ROLE_EXPERT = "(تعمیرکار)"
DEVICE_LOG_ASK_EDIT = "📝 متن جدید را وارد کنید:"
DEVICE_LOG_EDIT_SAVED = "✅ ویرایش ثبت شد."
DEVICE_LOG_NEW_NOTIFY = """🔔 مشتری جدید!

📝 عیب اولیه:
«{desc}»

🎫 کد پیگیری: {code}"""

# ==================== امنیت ====================
SEC_TITLE = "🛡 امنیت"
SEC_LOGIN_ATTEMPTS = "❌ تعداد تلاش‌های ناموفق زیاد است. لطفاً {minutes} دقیقه صبر کنید."
SEC_RATE_LIMIT = "⚠️ درخواست‌های شما زیاد است. لطفاً کمی صبر کنید."
SEC_SUSPICIOUS = "⚠️ فعالیت مشکوک شناسایی شد."
SEC_RATING_ALREADY = "⚠️ شما قبلاً به این تعمیرکار امتیاز داده‌اید."
SEC_RATING_NEED_JOB = "❌ فقط بعد از یه معرفی واقعی می‌توانید امتیاز بدهید."
SEC_BLOCKED = "❌ دسترسی شما محدود شده است."

# ==================== نگهداری ۶ ماهه ====================
RETENTION_NOTICE = "ℹ️ اطلاعات بعد از ۶ ماه به دلایل قانونی حذف می‌شود."
RETENTION_CLEANUP_DONE = "✅ پاکسازی داده‌های قدیمی انجام شد."
# ==================== مدیریت شهرها ====================
BTN_EDIT_CITIES = "🏙 ویرایش شهرها"

EDIT_CITIES_TITLE = """🏙 مدیریت شهرها

در این بخش می‌توانید شهرها را اضافه یا حذف کنید.

📊 تعداد فعلی شهرها: {count}"""

EDIT_CITIES_ASK_NEW = "🏙 نام شهر جدید را وارد کنید:\n\nمثال: رشت"
EDIT_CITY_ADDED = "✅ شهر «{city}» اضافه شد."
EDIT_CITY_EXISTS = "⚠️ شهر «{city}» قبلاً وجود داره."
EDIT_CITY_REMOVED = "✅ شهر «{city}» حذف شد."
EDIT_CITY_NOT_FOUND = "❌ شهر «{city}» پیدا نشد."
EDIT_CITY_INVALID = "❌ نام شهر نامعتبر. لطفاً دوباره وارد کنید."
EDIT_CITIES_LIST_TITLE = "🗑 حذف شهر:\n\nروی شهر مورد نظر بزنید تا حذف بشه:"
EDIT_CITIES_RESET = "🔄 بازگشت به لیست پیش‌فرض"
EDIT_CITIES_RESET_OK = "✅ لیست شهرها به حالت پیش‌فرض برگشت."
EDIT_CITIES_RESET_CONFIRM = """⚠️ مطمئنید؟

با این کار همه تغییرات (اضافه/حذف) پاک می‌شن و
لیست شهرها به حالت اولیه برمی‌گرده."""
BTN_CITIES_NEXT = "➡️ بعدی"
BTN_CITIES_PREV = "⬅️ قبلی"

# ==================== لاگ عیوب دستگاه (اضافه‌ها) ====================
BTN_DEVICE_LOG = "📋 لاگ عیوب"
BTN_ADD_DEFECT = "➕ افزودن عیب"
BTN_VIEW_DEVICE_LOGS = "📋 لاگ عیوب دستگاه‌ها"

DEVICE_LOG_EMPTY = "📋 هنوز عیبی برای این دستگاه ثبت نشده."
DEVICE_LOG_FOR_JOB = """📋 لاگ عیوب دستگاه

🎫 کد پیگیری: {code}
🔧 دستگاه: {device}

━━━━━━━━━━━━━━━━━
{logs}
━━━━━━━━━━━━━━━━━"""

DEVICE_LOG_ASK_DEVICE_NAME = "🔧 نام دستگاه را وارد کنید:\n\nمثال: ماشین لباسشویی"
DEVICE_LOG_ASK_DEFECT = "📝 عیب دستگاه را توضیح دهید:"
DEVICE_LOG_ADDED = "✅ عیب ثبت شد."
DEVICE_LOG_UPDATED = "✅ ویرایش ثبت شد."
DEVICE_LOG_DELETED_MSG = "🗑 حذف شد."
DEVICE_LOG_EDIT_BTN = "✏️ ویرایش"
DEVICE_LOG_EDIT_ASK = "📝 متن جدید را وارد کنید:"
DEVICE_LOG_ONLY_AUTHOR = "❌ فقط نویسنده می‌تواند ویرایش کند."
DEVICE_LOG_NO_JOBS = "هنوز درخواستی با لاگ عیب ندارید."

DEVICE_LOG_ITEM_SIMPLE = """📝 {date}
👤 {author} {role}:
«{text}»"""

DEVICE_LOG_ITEM_EDITED = """📝 {date}
👤 {author} {role} - ✏️ ویرایش شده:
«{text}»
قبل: «{old_text}»"""

DEVICE_LOG_NEW_NOTIFY = """🔔 عیب جدید ثبت شد!

🎫 کد: {code}
🔧 دستگاه: {device}
📝 «{text}»

نویسنده: {author}"""

# ==================== امنیت (اضافه‌ها) ====================
SEC_LOGIN_LOCKED = """🔐 حساب شما به دلیل تلاش‌های ناموفق قفل شده.

⏳ لطفاً {minutes} دقیقه دیگر دوباره تلاش کنید."""

SEC_LOGIN_ATTEMPTS_LEFT = "⚠️ رمز اشتباه. {left} تلاش باقی‌مانده."
SEC_LOGIN_SUCCESS = "✅ ورود موفق."

SEC_SUSPICIOUS_MSG = """⚠️ فعالیت مشکوک شناسایی شد.

دسترسی شما به دلیل ارسال محتوای نامناسب محدود شد.
برای پیگیری با پشتیبانی تماس بگیرید."""

SEC_BLOCKED_PERMANENT = """🚫 دسترسی شما مسدود شده است.

دلیل: {reason}

برای پیگیری با پشتیبانی تماس بگیرید."""

SEC_BLOCKED_TEMP = """🚫 دسترسی شما موقتاً محدود شده است.

دلیل: {reason}
⏳ تا: {until}

برای پیگیری با پشتیبانی تماس بگیرید."""

# ---- پنل امنیتی ادمین ----
ADM_SECURITY = "🛡 امنیت"
ADM_SEC_EVENTS = "📋 رویدادهای اخیر"
ADM_SEC_BLOCKED = "🚫 کاربران مسدود"
ADM_SEC_BACK = "🔙 بازگشت"

SEC_EVENTS_TITLE = "📋 آخرین رویدادهای امنیتی:\n\n"
SEC_EVENTS_EMPTY = "هیچ رویداد امنیتی‌ای ثبت نشده."
SEC_BLOCKED_TITLE = "🚫 کاربران مسدود:\n\n"
SEC_BLOCKED_EMPTY = "هیچ کاربری مسدود نیست."
SEC_UNBLOCK = "🔓 رفع مسدودی"
SEC_UNBLOCKED_OK = "✅ کاربر رفع مسدودی شد."

SEC_EVENT_LINE = "• {date} - {user} - {type}\n"
SEC_BLOCKED_LINE = "• {user} - {reason} ({date})\n"

# ==================== نگهداری ۶ ماهه (اضافه‌ها) ====================
RETENTION_TITLE = "🗄 نگهداری اطلاعات"

RETENTION_DAYS = 180  # ۶ ماه
RETENTION_CLEANUP_INTERVAL = 86400  # هر ۲۴ ساعت

RETENTION_CLEANUP_START = "🗄 شروع پاکسازی داده‌های قدیمی..."
RETENTION_CLEANUP_DONE_FULL = """✅ پاکسازی انجام شد:

• پروژه‌های حذف‌شده: {jobs}
• نظرات حذف‌شده: {comments}
• لاگ‌های حذف‌شده: {logs}
• تراکنش‌های حذف‌شده: {txns}
• رویدادهای امنیتی حذف‌شده: {events}"""

# ==================== لاگ عیب (اختصاصی ربات اصلی) ====================
BTN_MY_DEVICE_LOGS = "📋 لاگ عیوب من"
BTN_DEVICE_LOG_BACK = "🔙 بازگشت"
BTN_DEVICE_LOG_VIEW = "👁 مشاهده"
BTN_DEVICE_LOG_EDIT = "✏️ ویرایش"

DEVICE_LOG_MENU_TITLE = "📋 لاگ عیوب شما:\n\n"
DEVICE_LOG_LIST_ITEM = """🎫 {code}
🔧 {device}
📝 {count} عیب
📅 {date}
"""

# ==================== ویرایش نام گروه و زیرگروه ====================
BTN_EDIT_CAT_NAME = "✏️ ویرایش نام گروه"
BTN_EDIT_SUB_NAME = "✏️ ویرایش نام"

EDIT_CAT_NAME_ASK = """✏️ ویرایش نام گروه

📛 نام فعلی: {old}

نام جدید را وارد کنید:"""

EDIT_CAT_NAME_DONE = """✅ نام گروه با موفقیت تغییر کرد.

📛 قبلی: {old}
✨ جدید: {new}"""

EDIT_CAT_NAME_EXISTS = "⚠️ گروهی با نام «{name}» قبلاً وجود داره. یه نام دیگه انتخاب کن:"
EDIT_CAT_NAME_NOT_FOUND = "❌ گروه پیدا نشد."
EDIT_CAT_NAME_INVALID = "❌ نام نامعتبر. دوباره وارد کن:"

EDIT_SUB_NAME_ASK = """✏️ ویرایش نام زیرتخصص

📛 نام فعلی: {old}

نام جدید را وارد کنید:"""

EDIT_SUB_NAME_DONE = """✅ نام زیرتخصص با تغییر کرد.

📛 قبلی: {old}
✨ جدید: {new}"""

EDIT_SUB_NAME_EXISTS = "⚠️ زیرتخصصی با نام «{name}» توی این گروه وجود داره. یه نام دیگه انتخاب کن:"
EDIT_SUB_NAME_NOT_FOUND = "❌ زیرتخصص پیدا نشد."
EDIT_SUB_NAME_INVALID = "❌ نام نامعتبر. دوباره وارد کن:"
