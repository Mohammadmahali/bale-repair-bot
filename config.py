# ==================== تنظیمات اصلی ====================
TOKEN = "2007928769:77pB0gIf5DmKtAlPAEdgVAub21mH7mHn7V0"
ADMIN_TOKEN = "1415928893:_EHB_I20KIoNvYcRWOk6QWA0LewuSHSAM9c"
SUPER_ADMIN = 1808576881
API_URL = "https://tapi.bale.ai/bot" + TOKEN
BOT_USERNAME = ""

# ==================== نام فایل‌ها ====================
import os
import shutil

# چک کن دیسک پایدار (/data) وجود داره یا نه
if os.path.exists("/data"):
    # ===== حالت Persistent (روی رانفلر با دیسک) =====
    SQLITE_FILE = "/data/bot.db"

    # مهاجرت خودکار: اگه دیتابیس قبلی توی ریشه پروژه هست و توی /data نیست
    _old_db = "bot.db"
    if os.path.exists(_old_db) and not os.path.exists(SQLITE_FILE):
        try:
            shutil.copy2(_old_db, SQLITE_FILE)
            print("[CONFIG] ✅ Migrated old bot.db to /data/bot.db")
        except Exception as e:
            print("[CONFIG] ⚠️ Migration failed:", str(e)[:100])

    print("[CONFIG] Using persistent storage: /data/bot.db")
else:
    # ===== حالت عادی (لوکال یا بدون دیسک) =====
    SQLITE_FILE = "bot.db"
    print("[CONFIG] Using local storage: bot.db")

# بقیه فایل‌ها (فقط برای مهاجرت از JSON)
DB_FILE = "experts.json"
JOBS_FILE = "jobs.json"
CONFIG_FILE = "bot_config.json"

# ==================== تنظیمات ادمین ====================
DEFAULT_PASSWORD = "1234"
FEEDBACK_ID = "@mahalservice"

# ==================== سیستم رایگان ====================
FREE_DAYS = 30
FREE_CUSTOMERS = 30
COMMISSION_DEFAULT = 50000

# ==================== اعلان‌های مرحله‌ای ====================
NOTIFY_STAGE_1 = 25
NOTIFY_STAGE_2 = 28
NOTIFY_STAGE_3 = 30

# ==================== فعال/غیرفعال ====================
ENABLE_SHOP_STATUS = True
ENABLE_FUZZY_SEARCH = True
ENABLE_RATING_COMMENTS = False
ENABLE_LEVEL2_CONSULT = False
ENABLE_REPORTS = False
ENABLE_QA = False

# ==================== تنظیمات ====================
FUZZY_DISTANCE = 3
LOCATION_RADIUS_KM = 20
RATE_LIMIT_REPORTS = 3
SESSION_TIMEOUT = 1800

# ==================== کیف پول ====================
CARD_NUMBER = "0000-0000-0000-0000"
CARD_OWNER = "نام صاحب کارت"

# ==================== QR کد ====================
QR_API_URL = "https://api.qrserver.com/v1/create-qr-code/"
QR_SIZE = "500x500"

# ==================== تعرفه هر دسته (پیش‌فرض) ====================
TARIFFS = {
    "🔌 لوازم برقی": 40000,
    "🔥 لوازم گازی": 70000,
    "❄️ سرمایشی و گرمایشی": 90000,
    "🚗 خودرو": 60000,
}

# ==================== تعرفه هر زیرتخصص ====================
SUB_TARIFFS = {
    "ماکروفر / مایکروویو": 50000,
    "توستر": 30000,
    "فر برقی توکار": 60000,
    "جاروبرقی": 35000,
    "چای‌ساز / کتری برقی": 25000,
    "قهوه‌ساز": 35000,
    "پلوپز": 30000,
    "سرخ‌کن / آیرفرایر": 40000,
    "سشوار": 25000,
    "اتو (بخارشو، پرس، ایستاده)": 35000,
    "ماشین لباسشویی": 100000,
    "ماشین ظرفشویی": 90000,
    "دستگاه تصفیه آب": 50000,
    "آبسردکن": 40000,
    "تلویزیون": 80000,
    "لامپ و پروژکتور": 20000,
    "انواع محافظ (یخچال، کولر، تلویزیون)": 25000,
    "تعمیر بردهای الکترونیکی": 120000,
    "پنکه دستی و رومیزی": 25000,
    "پنکه سقفی": 30000,
    "سایر لوازم برقی": 40000,
    "اجاق گاز": 60000,
    "آبگرمکن دیواری": 80000,
    "آبگرمکن زمینی": 80000,
    "بخاری گازی": 50000,
    "پکیج شوفاژ": 100000,
    "شومینه گازی": 50000,
    "سایر لوازم گازی": 50000,
    "یخچال و فریزر": 100000,
    "کولر آبی": 50000,
    "کولر گازی (اسپلیت)": 90000,
    "چیلر": 150000,
    "رادیاتور": 60000,
    "سایر سرمایشی": 50000,
    "جلوبندی‌ساز": 150000,
    "تنظیم موتور": 100000,
    "تعمیر ترمز": 60000,
    "تعمیر فرمان": 70000,
    "برق خودرو": 60000,
    "باتری‌ساز": 40000,
    "آپاراتی (پنچرگیری)": 30000,
    "تعویض روغن، فیلتر و سرویس": 40000,
    "مکانیکی (تعمیرات موتور)": 200000,
    "گیربکس و کلاچ": 180000,
    "کمک‌فنر و فنر": 80000,
    "اگزوز": 70000,
    "کولر و بخاری خودرو": 80000,
    "دیاگ و عیب‌یابی": 50000,
    "صافکاری": 150000,
    "نقاشی خودرو": 200000,
    "سایر خدمات خودرو": 50000,
}

# ==================== شهرهای ایران ====================
try:
    from cities_data import get_all_cities as _get_all_cities
    IRAN_CITIES = _get_all_cities()
    print("[CONFIG] Loaded {} cities from cities_data.py".format(len(IRAN_CITIES)))
except Exception as e:
    print("[CONFIG] cities_data.py not found:", str(e)[:100])
    IRAN_CITIES = [
        "تهران", "مشهد", "اصفهان", "شیراز", "تبریز", "کرج", "اهواز", "قم",
        "کرمانشاه", "ارومیه", "رشت", "زاهدان", "همدان", "کرمان", "یزد",
        "اردبیل", "بندرعباس", "اراک", "اسلامشهر", "زنجان", "ساری", "قزوین",
    ]
