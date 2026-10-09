# ==================== توابع کمکی ====================
import random
import string
import re
import time
from math import radians, sin, cos, sqrt, atan2
from config import IRAN_CITIES, FUZZY_DISTANCE


def gen_tracking_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def gen_expert_code(name):
    base = "".join(c for c in name if c.isascii() and c.isalnum()).lower()
    if len(base) < 4:
        base = "expert"
    chars = string.ascii_lowercase + string.digits
    return base[:6] + "".join(random.choices(chars, k=4))


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


# ==================== تجزیه ورودی ====================
def parse_numbers(text, max_num):
    text = text.replace("،", ",").replace(" ", ",")
    result = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            n = int(part)
            if 1 <= n <= max_num:
                result.append(n)
        except:
            pass
    return result


def parse_single_number(text, max_num):
    nums = parse_numbers(text, max_num)
    return None if len(nums) != 1 else nums[0] - 1


def parse_priorities(text, criteria):
    text = text.strip().replace("،", ",").replace(" ", ",")
    if text == "0" or text == "":
        return []
    keys = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            n = int(part)
            if 1 <= n <= len(criteria):
                keys.append(criteria[n-1]["key"])
        except:
            pass
    return keys


def format_numbered_list(lst):
    return "\n".join(["{}. {}".format(i, s) for i, s in enumerate(lst, 1)])


def format_criteria_list(criteria):
    return "\n".join(["{}. {}".format(i, c["label"]) for i, c in enumerate(criteria, 1)])


# ==================== تشخیص غلط تایپی ====================
def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def find_similar_cities(input_city, max_distance=None):
    if max_distance is None:
        max_distance = FUZZY_DISTANCE

    input_clean = input_city.strip().replace("ي", "ی").replace("ك", "ک")
    if not input_clean:
        return []

    # لیست شهرها رو از config بگیر (که ممکنه با مدیریت شهر آپدیت شده باشه)
    try:
        from config import IRAN_CITIES as CITIES
    except:
        CITIES = IRAN_CITIES

    matches = []

    for city in CITIES:
        city_clean = city.strip()
        if input_clean == city_clean:
            return [city]
        distance = levenshtein_distance(input_clean, city_clean)
        dynamic_max = max_distance
        if len(city_clean) >= 5:
            dynamic_max = max_distance + 1
        if len(city_clean) >= 7:
            dynamic_max = max_distance + 2
        if distance <= dynamic_max and distance <= len(city_clean) * 0.4:
            matches.append((city, distance))

    matches.sort(key=lambda x: x[1])
    return [m[0] for m in matches]


def suggest_city(input_city):
    matches = find_similar_cities(input_city)
    if not matches:
        return None
    return matches


# ==================== اعتبارسنجی ====================
def is_valid_phone(phone):
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("+98"):
        phone = "0" + phone[3:]
    if phone.startswith("98") and len(phone) == 12:
        phone = "0" + phone[2:]
    return len(phone) == 11 and phone.startswith("0")


def is_valid_name(name):
    return len(name.strip()) >= 3 and len(name.strip()) <= 50


def normalize_text(text):
    if not text:
        return ""
    return text.strip().replace("ي", "ی").replace("ك", "ک").replace("ة", "ه")


# ==================== امنیت ====================
# الگوهای مشکوک (لینک، تبلیغات، اسپم)
SUSPICIOUS_PATTERNS = [
    r"https?://",
    r"t\.me/",
    r"telegram\.me",
    r"ble\.ir/[a-z]+",
    r"\bBTC\b",
    r"کازینو",
    r"شرط‌بندی",
    r"قمار",
]

# کلمات رکیک (نمونه - می‌تونی کامل کنی)
BAD_WORDS = [
    "حرومزاده", "حروم‌زاده", "احمق", "خرفت", "کثافت",
    "بیشعور", "بی‌شعور", "دیوانه", "خر", "سگ",
]


def is_suspicious_text(text, max_links=1):
    """آیا متن مشکوک هست؟"""
    if not text:
        return False

    text_lower = text.lower()

    # چک لینک‌ها
    link_count = 0
    for pattern in SUSPICIOUS_PATTERNS:
        matches = re.findall(pattern, text_lower)
        link_count += len(matches)
    if link_count > max_links:
        return True

    # چک کلمات رکیک
    bad_count = 0
    for word in BAD_WORDS:
        if word in text:
            bad_count += 1
    if bad_count >= 2:
        return True

    return False


def sanitize_text(text, max_length=500):
    """پاکسازی متن ورودی"""
    if not text:
        return ""
    text = text.strip()
    if len(text) > max_length:
        text = text[:max_length]
    # حذف کاراکترهای کنترلی
    text = "".join(c for c in text if c == "\n" or c == "\t" or (ord(c) >= 32))
    return text


def is_rate_limit_exceeded(timestamps, max_count, window_seconds):
    """
    بررسی rate limit
    timestamps: لیست زمان‌های قبلی (ثانیه)
    max_count: حداکثر تعداد مجاز
    window_seconds: پنجره زمانی به ثانیه
    """
    now = int(time.time())
    cutoff = now - window_seconds
    recent = [t for t in timestamps if t > cutoff]
    return len(recent) >= max_count


# ==================== کمکی ====================
def truncate(text, max_len=100):
    if len(text) <= max_len:
        return text
    return text[:max_len-3] + "..."


def days_to_seconds(days):
    return days * 86400


def seconds_to_days(seconds):
    return int(seconds / 86400)


def format_toman(amount):
    return "{:,}".format(amount) + " تومان"


def format_relative_time(timestamp):
    """نمایش زمان نسبی: 'همین الان', '۵ دقیقه پیش', ..."""
    if not timestamp:
        return "—"
    diff = int(time.time()) - int(timestamp)
    if diff < 0:
        return "آینده"
    if diff < 60:
        return "همین الان"
    if diff < 3600:
        return "{} دقیقه پیش".format(diff // 60)
    if diff < 86400:
        return "{} ساعت پیش".format(diff // 3600)
    if diff < 30 * 86400:
        return "{} روز پیش".format(diff // 86400)
    if diff < 365 * 86400:
        return "{} ماه پیش".format(diff // (30 * 86400))
    return "{} سال پیش".format(diff // (365 * 86400))
