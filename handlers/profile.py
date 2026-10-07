# ==================== پروفایل تعمیرکار ====================
import time
import config
from config import DB_FILE, FREE_DAYS
from texts import (
    MY_PROFILE, NO_PROFILE, YES, NO,
    LBL_NAME, LBL_ROLE, LBL_SUBSPEC, LBL_AREA, LBL_PHONE, LBL_ONSITE,
    LBL_RATING, LBL_REFERRAL, LBL_CODE, LBL_LINK, SHARE_HINT,
    CRITERIA,
    SHOP_STATUS_TITLE, SHOP_ACTIVE, SHOP_CLOSED_TEMP, SHOP_CLOSED_PERM,
    SHOP_COUNTDOWN, SHOP_DAYS,
    RESPONSE_TIMES, REPAIR_TIMES,
    BTN_SHOP_STATUS, BTN_WALLET, BTN_BACK,
    LOCATION_WARNING,
)
from keyboards import kb_main, kb_share_link, kb_profile, kb_profile_location
from api import send_message
from db import find_expert_by_id, is_shop_open
from utils import gen_expert_code
from db import load_experts, save_experts


# ==================== محاسبه امتیاز ====================
def calc_avg_rating(expert):
    """میانگین امتیاز کلی"""
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
    """میانگین امتیاز یه معیار"""
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
    """امتیاز یه مرحله"""
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


def rating_breakdown(expert):
    """نمایش تفصیلی امتیازها"""
    lines = []
    for cr in CRITERIA:
        avg = calc_criteria_rating(expert, cr["key"])
        stars = round(avg)
        lines.append(cr["label"] + " " + ("⭐" * stars) + " ({:.1f})".format(avg))
    return "\n".join(lines)


# ==================== وضعیت مغازه ====================
def get_shop_label(expert):
    """گرفتن وضعیت مغازه"""
    if not expert.get("active", True):
        return "❌ غیرفعال"
    st = expert.get("shop_status", "active")
    if st == "active":
        return SHOP_ACTIVE
    if st == "closed_perm":
        return SHOP_CLOSED_PERM
    if st == "closed_temp":
        if expert.get("closed_until", 0) > time.time():
            days = max(1, int((expert["closed_until"] - time.time()) / 86400) + 1)
            return SHOP_CLOSED_TEMP + " (" + SHOP_COUNTDOWN + str(days) + SHOP_DAYS + ")"
        return SHOP_ACTIVE
    return SHOP_ACTIVE


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
    txt += "⏱ سرعت پاسخگویی: " + RESPONSE_TIMES[int(expert.get("response_speed", 0))] + "\n"
    txt += "🔧 زمان تعمیر: " + REPAIR_TIMES[int(expert.get("repair_time", 0))] + "\n"
    txt += SHOP_STATUS_TITLE + get_shop_label(expert) + "\n\n"
    
    if expert.get("status", "approved") == "pending":
        txt += "⏳ در انتظار تأیید مدیر\n\n"
    
    txt += "⭐ {:.1f}/5".format(calc_avg_rating(expert))
    rv = count_reviews(expert)
    if rv > 0:
        txt += " (" + str(rv) + " نظر)"
    txt += "\n" + LBL_REFERRAL + str(expert.get("referral_count", 0)) + "\n\n"
    txt += rating_breakdown(expert) + "\n\n"
    txt += "📊 مراحل نظرسنجی:\n"
    for st in [0, 1, 2]:
        a, c = calc_stage_stats(expert, st)
        nm = ["اولیه", "یک‌ماه", "شش‌ماه"][st]
        if a is None:
            txt += "• " + nm + ": هنوز نیست\n"
        else:
            txt += "• " + nm + ": {:.1f} ({} نظر)\n".format(a, c)
    
    send_message(chat_id, txt, kb_main())
    
    # لینک اشتراک
    _show_expert_link(chat_id, user_id, expert)
    
    # هشدار لوکیشن
    if not expert.get("lat") or not expert.get("lng"):
        send_message(
            chat_id,
            LOCATION_WARNING,
            kb_profile_location()
        )
    
    # منوی پروفایل
    send_message(chat_id, "👤 منوی پروفایل:", kb_profile())


def _show_expert_link(chat_id, user_id, expert):
    """نمایش کد اختصاصی و لینک اشتراک"""
    code = expert.get("expert_code", "")
    if not code:
        code = gen_expert_code(expert.get("name", "expert"))
        experts = load_experts()
        for x in experts:
            if x.get("user_id") == user_id:
                x["expert_code"] = code
                break
        save_experts(experts)
    
    link = _build_expert_link(code)
    txt = LBL_CODE + code + "\n\n" + LBL_LINK + link + SHARE_HINT
    send_message(chat_id, txt, kb_share_link(link))


def _build_expert_link(code):
    """ساخت لینک اختصاصی"""
    bot_user = config.BOT_USERNAME
    if bot_user:
        return "https://ble.ir/" + bot_user + "?start=" + code
    return "https://ble.ir/yourbot?start=" + code
