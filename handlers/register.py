# ==================== ثبت‌نام تعمیرکار ====================
import time
from config import DB_FILE
from texts import (
    CAT_ELEC, CAT_GAS, CAT_COOL, CAT_CAR,
    YES, NO, CHOOSE_OPTION, INVALID_INPUT, BTN_BACK,
    ASK_NAME, ASK_PHONE, ASK_CITY, ASK_AREA, ASK_LOCATION, ASK_SEND_LOCATION,
    LOCATION_SAVED, ASK_ONSITE, ASK_RESPONSE_SPEED, ASK_REPAIR_TIME,
    RESPONSE_TIMES, REPAIR_TIMES, REGISTER_OK, REGISTER_PENDING,
    LBL_NAME, LBL_ROLE, LBL_SUBSPEC, LBL_AREA, LBL_PHONE, LBL_ONSITE,
    LBL_CODE, LBL_LINK, SHARE_HINT,
)
from keyboards import (
    kb_categories, kb_yes_no, kb_back, kb_location,
    kb_text_only, kb_share_link,
)
from api import send_message
from db import add_or_update_expert
from utils import (
    parse_numbers, parse_single_number, format_numbered_list,
    gen_expert_code,
)
from handlers.start import format_public_profile


# ==================== زیرتخصص‌ها ====================
SUBS_ELEC = [
    "ماکروفون / مایکروویو",
    "توستر",
    "فر برقی توکار",
    "جاروبرقی",
    "چای‌ساز / کتری برقی",
    "قهوه‌ساز",
    "پلوپز",
    "سرخ‌کن / آیرفرایر",
    "سشوار",
    "اتو (بخارشو، پرس، ایستاده)",
    "ماشین لباسشویی",
    "ماشین ظرفشویی",
    "دستگاه تصفیه آب",
    "آبسردکن",
    "تلویزیون",
    "لامپ و پروژکتور",
    "انواع محافظ (یخچال، کولر، تلویزیون)",
    "تعمیر بردهای الکترونیکی",
    "پنکه دستی و رومیزی",
    "پنکه سقفی",
    "سایر لوازم برقی",
]

SUBS_GAS = [
    "اجاق گاز",
    "آبگرمکن دیواری",
    "آبگرمکن زمینی",
    "بخاری گازی",
    "پکیج شوفاژ",
    "شومینه گازی",
    "سایر لوازم گازی",
]

SUBS_COOL = [
    "یخچال و فریزر",
    "کولر آبی",
    "کولر گازی (اسپلیت)",
    "چیلر",
    "رادیاتور",
    "سایر سرمایشی",
]

SUBS_CAR = [
    "جلوبندی‌ساز",
    "تنظیم موتور",
    "تعمیر ترمز",
    "تعمیر فرمان",
    "برق خودرو",
    "باتری‌ساز",
    "آپاراتی (پنچرگیری)",
    "تعویض روغن، فیلتر و سرویس",
    "مکانیکی (تعمیرات موتور)",
    "گیربکس و کلاچ",
    "کمک‌فنر و فنر",
    "اگزوز",
    "کولر و بخاری خودرو",
    "دیاگ و عیب‌یابی",
    "صافکاری",
    "نقاشی خودرو",
    "سایر خدمات خودرو",
]


# ==================== نقشه بازگشت ====================
PREV_STEP = {
    "reg_cat": None,
    "reg_subs": "reg_cat",
    "reg_name": "reg_subs",
    "reg_phone": "reg_name",
    "reg_city": "reg_phone",
    "reg_area": "reg_city",
    "reg_ask_location": "reg_area",
    "reg_location": "reg_ask_location",
    "reg_onsite": "reg_ask_location",
    "reg_response": "reg_onsite",
    "reg_repair": "reg_response",
}

def get_subs_by_category(category):
    if category == CAT_ELEC:
        return SUBS_ELEC
    if category == CAT_GAS:
        return SUBS_GAS
    if category == CAT_COOL:
        return SUBS_COOL
    if category == CAT_CAR:
        return SUBS_CAR
    return []


def is_valid_category(text):
    return text in [CAT_ELEC, CAT_GAS, CAT_COOL, CAT_CAR]


# ==================== شروع ثبت‌نام ====================
def start_registration(chat_id, user_id, sessions):
    sessions[user_id] = {"step": "reg_cat", "data": {}}
    send_message(chat_id, CHOOSE_OPTION, kb_categories())


# ==================== ادامه ثبت‌نام ====================
def continue_registration(chat_id, user_id, text, sessions):
    """ادامه فرآیند ثبت‌نام"""
    if user_id not in sessions:
        return False
    
    session = sessions[user_id]
    step = session["step"]
    data = session["data"]
    
    # ===== بررسی بازگشت =====
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
    elif step == "reg_city":
        send_message(chat_id, ASK_CITY, kb_text_only())
    elif step == "reg_area":
        send_message(chat_id, ASK_AREA, kb_text_only())
        return True
    
    if step == "reg_city":
        data["city"] = text.strip()
        session["step"] = "reg_area"
        send_message(chat_id, ASK_AREA, kb_text_only())
        return True
    
    # ===== مرحله: محدوده (فقط متن) =====
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
    
    # ===== مرحله: پرسیدن لوکیشن =====
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
    
    # ===== مرحله: لوکیشن =====
    if step == "reg_location":
        # این مرحله رو handler لوکیشن مدیریت می‌کنه
        # اگه متن اومد، دوباره درخواست کن
        send_message(chat_id, ASK_SEND_LOCATION, kb_location())
        return True
    
    # ===== مرحله: حضور در محل =====
    if step == "reg_onsite":
        if text not in [YES, NO]:
            send_message(chat_id, CHOOSE_OPTION, kb_yes_no())
            return True
        data["works_on_site"] = (text == YES)
        session["step"] = "reg_response"
        msg = ASK_RESPONSE_SPEED + "\n\n" + format_numbered_list(RESPONSE_TIMES)
        send_message(chat_id, msg, kb_back())
        return True
    
    # ===== مرحله: سرعت پاسخگویی =====
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
    
    # ===== مرحله: زمان تعمیر =====
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
    """هندل ارسال لوکیشن در ثبت‌نام"""
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


# ==================== نهایی‌سازی ثبت‌نام ====================
def finalize_registration(chat_id, user_id, data, sessions):
    """ذخیره اطلاعات و پایان ثبت‌نام"""
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
    
    # حذف فیلد کمکی
    data.pop("_subs", None)
    
    add_or_update_expert(data)
    sessions.pop(user_id, None)
    
    # پیام تأیید به تعمیرکار
    msg = REGISTER_OK + "\n\n"
    msg += LBL_NAME + " " + data["name"] + "\n"
    msg += LBL_ROLE + " " + data["category"] + "\n"
    msg += LBL_SUBSPEC + " " + "، ".join(data["sub_specialties"]) + "\n"
    msg += LBL_AREA + " " + data["area"] + "\n"
    msg += LBL_PHONE + " " + data["phone"] + "\n"
    msg += LBL_ONSITE + " " + (YES if data["works_on_site"] else NO) + "\n\n"
    msg += LBL_CODE + data["expert_code"] + "\n"
    msg += LBL_LINK
    msg += "https://ble.ir/" + str(data["expert_code"])
    msg += "\n\n" + REGISTER_PENDING
    
    # ارسال پیام + دکمه کپی لینک
    link = "https://ble.ir/yourbot?start=" + data["expert_code"]
    send_message(chat_id, msg, kb_share_link(link))
    
    # اعلان به مدیران
    from admin import notify_admins_new_expert
    try:
        notify_admins_new_expert(data)
    except Exception as ex:
        print("Notify admins error:", str(ex)[:100])


# ==================== نمایش مجدد مرحله ====================
def ask_for_step(chat_id, step, data):
    """نمایش مجدد درخواست برای هر مرحله (برای بازگشت)"""
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
