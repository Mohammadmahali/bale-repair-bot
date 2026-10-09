# ==================== ثبت‌نام تعمیرکار ====================
import time
from config import DB_FILE, IRAN_CITIES
from texts import (
    CAT_ELEC, CAT_GAS, CAT_COOL, CAT_CAR,
    YES, NO, CHOOSE_OPTION, INVALID_INPUT, BTN_BACK,
    ASK_NAME, ASK_PHONE, ASK_CITY, ASK_AREA, ASK_LOCATION, ASK_SEND_LOCATION,
    LOCATION_SAVED, ASK_ONSITE, ASK_RESPONSE_SPEED, ASK_REPAIR_TIME,
    RESPONSE_TIMES, REPAIR_TIMES, REGISTER_OK, REGISTER_PENDING,
    LBL_NAME, LBL_ROLE, LBL_SUBSPEC, LBL_AREA, LBL_PHONE, LBL_ONSITE,
    LBL_CODE, LBL_LINK, SHARE_HINT,
    FUZZY_CONFIRM, FUZZY_YES, FUZZY_NO, FUZZY_MULTIPLE,
)
from keyboards import (
    kb_categories, kb_yes_no, kb_back, kb_location,
    kb_text_only, kb_share_link,
)
from api import send_message
from db import add_or_update_expert
from utils import (
    parse_numbers, parse_single_number, format_numbered_list,
    gen_expert_code, find_similar_cities,
)


# ==================== زیرتخصص‌ها ====================
SUBS_ELEC = [
    "ماکروفون / مایکروویو", "توستر", "فر برقی توکار", "جاروبرقی",
    "چای‌ساز / کتری برقی", "قهوه‌ساز", "پلوپز", "سرخ‌کن / آیرفرایر",
    "سشوار", "اتو (بخارشو، پرس، ایستاده)", "ماشین لباسشویی",
    "ماشین ظرفشویی", "دستگاه تصفیه آب", "آبسردکن", "تلویزیون",
    "لامپ و پروژکتور", "انواع محافظ (یخچال، کولر، تلویزیون)",
    "تعمیر بردهای الکترونیکی", "پنکه دستی و رومیزی", "پنکه سقفی",
    "سایر لوازم برقی",
]
SUBS_GAS = [
    "اجاق گاز", "آبگرمکن دیواری", "آبگرمکن زمینی", "بخاری گازی",
    "پکیج شوفاژ", "شومینه گازی", "سایر لوازم گازی",
]
SUBS_COOL = [
    "یخچال و فریزر", "کولر آبی", "کولر گازی (اسپلیت)",
    "چیلر", "رادیاتور", "سایر سرمایشی",
]
SUBS_CAR = [
    "جلوبندی‌ساز", "تنظیم موتور", "تعمیر ترمز", "تعمیر فرمان",
    "برق خودرو", "باتری‌ساز", "آپاراتی (پنچرگیری)",
    "تعویض روغن، فیلتر و سرویس", "مکانیکی (تعمیرات موتور)",
    "گیربکس و کلاچ", "کمک‌فنر و فنر", "اگزوز", "کولر و بخاری خودرو",
    "دیاگ و عیب‌یابی", "صافکاری", "نقاشی خودرو", "سایر خدمات خودرو",
]


PREV_STEP = {
    "reg_cat": None, "reg_subs": "reg_cat", "reg_name": "reg_subs",
    "reg_phone": "reg_name", "reg_city": "reg_phone", "reg_area": "reg_city",
    "reg_ask_location": "reg_area", "reg_location": "reg_ask_location",
    "reg_onsite": "reg_ask_location", "reg_response": "reg_onsite",
    "reg_repair": "reg_response",
}


def get_subs_by_category(category):
    from db import get_category_subs
    return get_category_subs(category)


def is_valid_category(text):
    from db import get_all_categories
    return text in get_all_categories().keys()


# ==================== نرمال‌سازی شهر ====================
def _normalize_city(text):
    """نرمال‌سازی نام شهر برای مقایسه دقیق"""
    if not text:
        return ""
    return text.strip().replace("ي", "ی").replace("ك", "ک").replace("\u200c", "").replace(" ", "").replace("‌", "")


def _find_exact_city(input_city):
    """پیدا کردن تطبیق دقیق شهر (با نرمال‌سازی)"""
    normalized_input = _normalize_city(input_city)
    if not normalized_input:
        return None
    for city in IRAN_CITIES:
        if _normalize_city(city) == normalized_input:
            return city
    return None


# ==================== شروع ثبت‌نام ====================
def start_registration(chat_id, user_id, sessions):
    sessions[user_id] = {"step": "reg_cat", "data": {}}
    send_message(chat_id, CHOOSE_OPTION, kb_categories())


# ==================== ادامه ثبت‌نام ====================
def continue_registration(chat_id, user_id, text, sessions):
    if user_id not in sessions:
        return False

    session = sessions[user_id]
    step = session["step"]
    data = session["data"]

    # ===== بازگشت =====
    if text == BTN_BACK:
        prev = PREV_STEP.get(step)
        if prev is None:
            sessions.pop(user_id, None)
            from keyboards import kb_main
            send_message(chat_id, "به منوی اصلی بازگشتید.", kb_main())
        else:
            session["step"] = prev
            ask_for_step(chat_id, prev, data)
        return True

    # ===== مرحله: انتخاب دسته =====
    if step == "reg_cat":
        if not is_valid_category(text):
            send_message(chat_id, CHOOSE_OPTION, kb_categories())
            return True
        data["category"] = text
        data["_subs"] = get_subs_by_category(text)
        session["step"] = "reg_subs"
        msg = "شماره تخصص‌هایتان را با کاما بنویسید (مثلاً 1,3):\n\n"
        msg += format_numbered_list(data["_subs"])
        send_message(chat_id, msg, kb_back())
        return True

    # ===== مرحله: انتخاب زیرتخصص‌ها =====
    if step == "reg_subs":
        nums = parse_numbers(text, len(data["_subs"]))
        if not nums:
            send_message(chat_id, INVALID_INPUT, kb_back())
            return True
        data["sub_specialties"] = [data["_subs"][n-1] for n in nums]
        session["step"] = "reg_name"
        send_message(chat_id, ASK_NAME, kb_back())
        return True

    # ===== مرحله: نام =====
    if step == "reg_name":
        data["name"] = text.strip()
        session["step"] = "reg_phone"
        send_message(chat_id, ASK_PHONE, kb_back())
        return True

    # ===== مرحله: تلفن =====
    if step == "reg_phone":
        data["phone"] = text.strip()
        session["step"] = "reg_city"
        send_message(chat_id, ASK_CITY, kb_text_only())
        return True

    # ===== مرحله: شهر با Fuzzy Match =====
    if step == "reg_city":
        city_input = text.strip()

        # مرحله ۱: تطبیق دقیق (با نرمال‌سازی)
        exact = _find_exact_city(city_input)
        if exact:
            data["city"] = exact
            session["step"] = "reg_area"
            send_message(chat_id, ASK_AREA, kb_text_only())
            return True

        # مرحله ۲: Fuzzy Match
        similar = find_similar_cities(city_input)

        # هیچ شهری پیدا نشد → خطا
        if not similar:
            send_message(
                chat_id,
                "❌ شهر «{}» توی لیست شهرهای ما پیدا نشد.\n\n"
                "لطفاً دوباره امتحان کنید یا اسم شهر نزدیک‌تر رو وارد کنید:".format(city_input),
                kb_text_only()
            )
            return True

        # یه شهر مشابه پیدا شد → تأیید
        if len(similar) == 1:
            data["_pending_city"] = city_input
            data["_suggested_city"] = similar[0]
            session["step"] = "reg_city_confirm"
            kb = {
                "inline_keyboard": [[
                    {"text": FUZZY_YES, "callback_data": "regfuzzy:yes"},
                    {"text": FUZZY_NO, "callback_data": "regfuzzy:no"}
                ]]
            }
            send_message(chat_id, FUZZY_CONFIRM.format(city=similar[0]), kb)
            return True

        # چند شهر مشابه → کاربر انتخاب کنه
        data["_pending_city"] = city_input
        data["_suggested_cities"] = similar[:3]
        session["step"] = "reg_city_multiple"
        msg = FUZZY_MULTIPLE
        for i, city in enumerate(similar[:3], 1):
            msg += "{}. {}\n".format(i, city)
        send_message(chat_id, msg, kb_back())
        return True

    # ===== انتخاب از چند شهر =====
    if step == "reg_city_multiple":
        n = parse_single_number(text, len(data.get("_suggested_cities", [])))
        if n is None:
            send_message(chat_id, INVALID_INPUT, kb_back())
            return True
        data["city"] = data["_suggested_cities"][n]
        session["step"] = "reg_area"
        send_message(chat_id, ASK_AREA, kb_text_only())
        return True

    # ===== مرحله: محدوده (محله) =====
    if step == "reg_area":
        neighborhood = text.strip()
        city = data.get("city", "")
        if neighborhood:
            data["area"] = city + "، " + neighborhood
        else:
            data["area"] = city
        session["step"] = "reg_ask_location"
        send_message(chat_id, ASK_LOCATION, kb_yes_no())
        return True

    # ===== پرسیدن لوکیشن =====
    if step == "reg_ask_location":
        if text not in [YES, NO]:
            send_message(chat_id, CHOOSE_OPTION, kb_yes_no())
            return True
        if text == YES:
            session["step"] = "reg_location"
            send_message(chat_id, ASK_SEND_LOCATION, kb_location())
        else:
            session["step"] = "reg_onsite"
            send_message(chat_id, ASK_ONSITE, kb_yes_no())
        return True

    # ===== لوکیشن =====
    if step == "reg_location":
        send_message(chat_id, ASK_SEND_LOCATION, kb_location())
        return True

    # ===== حضور در محل =====
    if step == "reg_onsite":
        if text not in [YES, NO]:
            send_message(chat_id, CHOOSE_OPTION, kb_yes_no())
            return True
        data["works_on_site"] = (text == YES)
        session["step"] = "reg_response"
        msg = ASK_RESPONSE_SPEED + "\n\n" + format_numbered_list(RESPONSE_TIMES)
        send_message(chat_id, msg, kb_back())
        return True

    # ===== سرعت پاسخگویی =====
    if step == "reg_response":
        n = parse_single_number(text, len(RESPONSE_TIMES))
        if n is None:
            send_message(chat_id, INVALID_INPUT, kb_back())
            return True
        data["response_speed"] = str(n)
        session["step"] = "reg_repair"
        msg = ASK_REPAIR_TIME + "\n\n" + format_numbered_list(REPAIR_TIMES)
        send_message(chat_id, msg, kb_back())
        return True

    # ===== زمان تعمیر =====
    if step == "reg_repair":
        n = parse_single_number(text, len(REPAIR_TIMES))
        if n is None:
            send_message(chat_id, INVALID_INPUT, kb_back())
            return True
        data["repair_time"] = str(n)
        finalize_registration(chat_id, user_id, data, sessions)
        return True

    return False


# ==================== مدیریت لوکیشن ====================
def handle_location(chat_id, user_id, location, sessions):
    if user_id not in sessions:
        return False
    session = sessions[user_id]
    step = session["step"]
    data = session["data"]
    if step == "reg_location":
        data["lat"] = location.get("latitude")
        data["lng"] = location.get("longitude")
        session["step"] = "reg_onsite"
        send_message(chat_id, LOCATION_SAVED)
        send_message(chat_id, ASK_ONSITE, kb_yes_no())
        return True
    return False


# ==================== هندل callback شهر ====================
def handle_city_fuzzy_callback(chat_id, user_id, action, sessions):
    if user_id not in sessions:
        return False
    session = sessions[user_id]
    if session.get("step") != "reg_city_confirm":
        return False
    data = session["data"]
    if action == "yes" and data.get("_suggested_city"):
        data["city"] = data["_suggested_city"]
    elif action == "no" and data.get("_pending_city"):
        data["city"] = data["_pending_city"]
    else:
        data["city"] = data.get("_pending_city", "")
    session["step"] = "reg_area"
    send_message(chat_id, ASK_AREA, kb_text_only())
    return True


# ==================== نهایی‌سازی ====================
def finalize_registration(chat_id, user_id, data, sessions):
    data["user_id"] = user_id
    data["is_premium"] = False
    data["active"] = True
    data["status"] = "pending"
    data["shop_status"] = "active"
    data["closed_until"] = 0
    data["ratings_by_stage"] = {}
    data["referral_count"] = 0
    data["expert_code"] = gen_expert_code(data.get("name", "expert"))
    data["created_at"] = int(time.time())

    data.pop("_subs", None)
    data.pop("_pending_city", None)
    data.pop("_suggested_city", None)
    data.pop("_suggested_cities", None)

    add_or_update_expert(data)
    sessions.pop(user_id, None)

    msg = REGISTER_OK + "\n\n"
    msg += LBL_NAME + " " + data["name"] + "\n"
    msg += LBL_ROLE + " " + data["category"] + "\n"
    msg += LBL_SUBSPEC + " " + "، ".join(data["sub_specialties"]) + "\n"
    msg += LBL_AREA + " " + data["area"] + "\n"
    msg += LBL_PHONE + " " + data["phone"] + "\n"
    msg += LBL_ONSITE + " " + (YES if data["works_on_site"] else NO) + "\n\n"
    msg += LBL_CODE + data["expert_code"] + "\n"
    msg += LBL_LINK + "https://ble.ir/" + str(data["expert_code"])
    msg += "\n\n" + REGISTER_PENDING

    link = "https://ble.ir/yourbot?start=" + data["expert_code"]
    send_message(chat_id, msg, kb_share_link(link))

    from admin import notify_admins_new_expert
    try:
        notify_admins_new_expert(data)
    except Exception as ex:
        print("Notify admins error:", str(ex)[:100])


# ==================== نمایش مجدد مرحله ====================
def ask_for_step(chat_id, step, data):
    if step == "reg_cat":
        send_message(chat_id, CHOOSE_OPTION, kb_categories())
    elif step == "reg_subs":
        msg = "شماره تخصص‌هایتان را بنویسید:\n\n"
        msg += format_numbered_list(data.get("_subs", []))
        send_message(chat_id, msg, kb_back())
    elif step == "reg_name":
        send_message(chat_id, ASK_NAME, kb_back())
    elif step == "reg_phone":
        send_message(chat_id, ASK_PHONE, kb_back())
    elif step == "reg_city":
        send_message(chat_id, ASK_CITY, kb_text_only())
    elif step == "reg_area":
        send_message(chat_id, ASK_AREA, kb_text_only())
    elif step == "reg_ask_location":
        send_message(chat_id, ASK_LOCATION, kb_yes_no())
    elif step == "reg_location":
        send_message(chat_id, ASK_SEND_LOCATION, kb_location())
    elif step == "reg_onsite":
        send_message(chat_id, ASK_ONSITE, kb_yes_no())
    elif step == "reg_response":
        msg = ASK_RESPONSE_SPEED + "\n\n" + format_numbered_list(RESPONSE_TIMES)
        send_message(chat_id, msg, kb_back())
    elif step == "reg_repair":
        msg = ASK_REPAIR_TIME + "\n\n" + format_numbered_list(REPAIR_TIMES)
        send_message(chat_id, msg, kb_back())
