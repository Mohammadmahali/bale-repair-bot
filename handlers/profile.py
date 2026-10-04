# ==================== پروفایل تعمیرکار ====================
from texts import (
    MY_PROFILE, NO_PROFILE, YES, NO,
    LBL_NAME, LBL_ROLE, LBL_SUBSPEC, LBL_AREA, LBL_PHONE, LBL_ONSITE,
    LBL_RATING, LBL_REFERRAL, LBL_CODE, LBL_LINK, SHARE_HINT,
    CRITERIA,
    SHOP_STATUS_TITLE, SHOP_ACTIVE, SHOP_CLOSED_TEMP, SHOP_CLOSED_PERM,
    SHOP_COUNTDOWN, SHOP_DAYS,
    RESPONSE_TIMES, REPAIR_TIMES,
    BTN_SHOP_STATUS,
)
from keyboards import kb_main, kb_share_link
from api import send_message
from db import find_expert_by_id, is_shop_open, load_experts, save_experts
from utils import gen_expert_code
from config import BOT_USERNAME, DB_FILE
from db import find_expert_by_id, is_shop_open, load_experts, save_experts


# ==================== نمایش پروفایل ====================
def show_profile(chat_id, user_id):
    """نمایش پروفایل تعمیرکار"""
    expert = find_expert_by_id(user_id)
    if not expert:
        send_message(chat_id, NO_PROFILE, kb_main())
        return
    
    txt = MY_PROFILE
    txt += LBL_NAME + " " + expert.get("name", "?") + "\n"
    txt += LBL_ROLE + " " + expert.get("category", "?") + "\n"
    txt += LBL_SUBSPEC + " " + "، ".join(expert.get("sub_specialties", [])) + "\n"
    txt += LBL_AREA + " " + expert.get("area", "?") + "\n"
    txt += LBL_PHONE + " " + expert.get("phone", "?") + "\n"
    txt += LBL_ONSITE + " " + (YES if expert.get("works_on_site") else NO) + "\n"
    
    # سرعت پاسخگویی
    resp = int(expert.get("response_speed", 0))
    txt += "⏱ " + RESPONSE_TIMES[resp] + "\n"
    
    # زمان تعمیر
    rep = int(expert.get("repair_time", 0))
    txt += "🔧 " + REPAIR_TIMES[rep] + "\n"
    
    # وضعیت مغازه
    txt += "\n" + SHOP_STATUS_TITLE
    shop = expert.get("shop_status", "active")
    if shop == "active":
        txt += SHOP_ACTIVE + "\n"
    elif shop == "closed_temp":
        closed_until = expert.get("closed_until", 0)
        import time as t
        if closed_until > t.time():
            days = max(1, int((closed_until - t.time()) / 86400) + 1)
            txt += SHOP_CLOSED_TEMP + " (" + SHOP_COUNTDOWN + str(days) + SHOP_DAYS + ")\n"
        else:
            txt += SHOP_ACTIVE + "\n"
    elif shop == "closed_perm":
        txt += SHOP_CLOSED_PERM + "\n"
    
    # اگه در انتظار تأیید
    if expert.get("status", "approved") == "pending":
        txt += "\n⏳ در انتظار تأیید مدیر\n"
    
    # امتیاز
    txt += "\n" + LBL_RATING + "{:.1f}/5".format(calc_overall_rating(expert))
    reviews = count_reviews(expert)
    if reviews > 0:
        txt += " (" + str(reviews) + " نظر)"
    
    # تعداد معرفی
    txt += "\n" + LBL_REFERRAL + str(expert.get("referral_count", 0)) + "\n\n"
    
    # امتیاز هر معیار
    txt += "📊 امتیاز شما در هر معیار:\n"
    for cr in CRITERIA:
        avg = calc_criteria_rating(expert, cr["key"])
        stars = round(avg)
        txt += cr["label"] + " " + ("⭐" * stars) + " ({:.1f})\n".format(avg)
    
    # مراحل نظرسنجی
    txt += "\n📊 مراحل نظرسنجی:\n"
    for st in [0, 1, 2]:
        avg, cnt = calc_stage_stats(expert, st)
        name = ["اولیه", "یک‌ماه", "شش‌ماه"][st]
        if avg is None:
            txt += name + ": هنوز نیست\n"
        else:
            txt += name + ": {:.1f} ({} نظر)\n".format(avg, cnt)
    
    send_message(chat_id, txt, kb_main())
    
    # نمایش کد اختصاصی
    show_my_link(chat_id, user_id)
    
    # دکمه وضعیت مغازه
    shop_kb = {"keyboard": [[{"text": BTN_SHOP_STATUS}]], "resize_keyboard": True}
    send_message(chat_id, "برای تغییر وضعیت مغازه:", shop_kb)


# ==================== نمایش لینک اشتراک‌گذاری ====================
def show_my_link(chat_id, user_id):
    """نمایش کد اختصاصی و لینک اشتراک‌گذاری"""
    expert = find_expert_by_id(user_id)
    if not expert:
        return
    
    code = expert.get("expert_code", "")
    if not code:
        code = gen_expert_code(expert.get("name", "expert"))
        experts = load_experts()
        for e in experts:
            if e.get("user_id") == user_id:
                e["expert_code"] = code
                break
        save_experts(experts)
    
    link = "https://ble.ir/" + BOT_USERNAME + "?start=" + code if BOT_USERNAME else "https://ble.ir/yourbot?start=" + code
    
    txt = LBL_CODE + code + "\n\n" + LBL_LINK + link + SHARE_HINT
    send_message(chat_id, txt, kb_share_link(link))


# ==================== محاسبات ====================
def calc_overall_rating(expert):
    """میانگین امتیاز کل"""
    total = 0
    count = 0
    for cr in CRITERIA:
        rt = 0
        rc = 0
        for s in ["0", "1", "2"]:
            r = expert.get("ratings_by_stage", {}).get(s, {}).get(cr["key"], {})
            rt += r.get("sum", 0)
            rc += r.get("count", 0)
        if rc > 0:
            total += rt / rc
            count += 1
    if count == 0:
        return 5.0
    return total / count


def calc_criteria_rating(expert, criteria_key):
    """میانگین امتیاز یه معیار خاص"""
    total = 0
    count = 0
    for s in ["0", "1", "2"]:
        r = expert.get("ratings_by_stage", {}).get(s, {}).get(criteria_key, {})
        total += r.get("sum", 0)
        count += r.get("count", 0)
    if count == 0:
        return 5.0
    return total / count


def count_reviews(expert):
    """تعداد کل نظرات"""
    max_count = 0
    for cr in CRITERIA:
        cnt = 0
        for s in ["0", "1", "2"]:
            r = expert.get("ratings_by_stage", {}).get(s, {}).get(cr["key"], {})
            cnt += r.get("count", 0)
        max_count = max(max_count, cnt)
    return max_count


def calc_stage_stats(expert, stage):
    """امتیاز یه مرحله خاص"""
    total = 0
    count = 0
    stage_data = expert.get("ratings_by_stage", {}).get(str(stage), {})
    for cr in CRITERIA:
        r = stage_data.get(cr["key"], {})
        if r.get("count", 0) > 0:
            total += r["sum"] / r["count"]
            count += 1
    if count == 0:
        return None, 0
    return total / count, count
