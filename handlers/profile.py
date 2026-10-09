# ==================== پروفایل ====================
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
    CUSTOMER_PROFILE_TITLE, CUSTOMER_NO_ACTIVITY, CUSTOMER_SUMMARY,
    CUSTOMER_TOTAL, CUSTOMER_LAST, CUSTOMER_ITEM_HEADER,
    CUSTOMER_HISTORY_FOOTER,
    RATING_BY_SPEC, RATING_SPEC_LINE, RATING_NO_SPEC,
    COMMENTS_HEADER, COMMENTS_NO, COMMENTS_ITEM, COMMENTS_ITEM_ANON,
    RETENTION_NOTICE,
)
from keyboards import (
    kb_main, kb_share_link, kb_profile,
    kb_profile_location, kb_share_link_with_qr,
)
from api import send_message
from db import (
    find_expert_by_id, is_shop_open, get_customer_history,
    get_all_spec_ratings, get_expert_comments,
)
from utils import gen_expert_code, format_relative_time
from db import load_experts, save_experts


# ==================== محاسبه امتیاز ====================
def calc_avg_rating(expert):
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
    try:
        from db import get_comment_count
        return get_comment_count(expert.get("user_id", 0))
    except:
        max_count = 0
        for cr in CRITERIA:
            cnt = 0
            for s in ["0", "1", "2"]:
                r = expert.get("ratings_by_stage", {}).get(s, {}).get(cr["key"], {})
                cnt += r.get("count", 0)
            max_count = max(max_count, cnt)
        return max_count


def calc_stage_stats(expert, stage):
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
    lines = []
    for cr in CRITERIA:
        avg = calc_criteria_rating(expert, cr["key"])
        stars = round(avg)
        lines.append(cr["label"] + " " + ("⭐" * stars) + " ({:.1f})".format(avg))
    return "\n".join(lines)


# ==================== امتیاز تفکیک‌شده ====================
def rating_by_spec_section(expert):
    spec_ratings = get_all_spec_ratings(expert)
    if not spec_ratings:
        return "\n" + RATING_BY_SPEC + RATING_NO_SPEC + "\n"
    txt = "\n" + RATING_BY_SPEC
    for spec, data in spec_ratings.items():
        txt += RATING_SPEC_LINE.format(
            spec=spec,
            avg="{:.1f}".format(data["avg"]),
            count=data["count"]
        )
    return txt


# ==================== نظرات متنی ====================
def comments_section(expert, limit=5):
    try:
        comments = get_expert_comments(expert.get("user_id"), limit)
    except:
        comments = []

    text_comments = [c for c in comments if (c.get("comment") or "").strip()]
    if not text_comments:
        return ""

    txt = COMMENTS_HEADER
    for c in text_comments:
        stars = int(round(c.get("stars", 5)))
        comment_text = c.get("comment", "")
        created = c.get("created_at", 0)
        date_str = format_relative_time(created)

        if c.get("is_anonymous"):
            txt += COMMENTS_ITEM_ANON.format(
                stars=stars, comment=comment_text, date=date_str,
            )
        else:
            name = c.get("author_name") or "کاربر"
            txt += COMMENTS_ITEM.format(
                stars=stars, name=name,
                comment=comment_text, date=date_str,
            )
    return txt


# ==================== وضعیت مغازه ====================
def get_shop_label(expert):
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
    expert = find_expert_by_id(user_id)
    if not expert:
        show_customer_profile(chat_id, user_id)
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
    txt += rating_breakdown(expert) + "\n"

    txt += rating_by_spec_section(expert)
    txt += comments_section(expert)

    txt += "\n📊 مراحل نظرسنجی:\n"
    for st in [0, 1, 2]:
        a, c = calc_stage_stats(expert, st)
        nm = ["اولیه", "یک‌ماه", "شش‌ماه"][st]
        if a is None:
            txt += "• " + nm + ": هنوز نیست\n"
        else:
            txt += "• " + nm + ": {:.1f} ({} نظر)\n".format(a, c)

    send_message(chat_id, txt, kb_main())

    _show_expert_link(chat_id, user_id, expert)

    if not expert.get("lat") or not expert.get("lng"):
        send_message(chat_id, LOCATION_WARNING, kb_profile_location())

    send_message(chat_id, "👤 منوی پروفایل:", kb_profile())


# ==================== پروفایل مشتری ====================
def show_customer_profile(chat_id, user_id):
    jobs = get_customer_history(user_id, 10)

    if not jobs:
        send_message(chat_id, CUSTOMER_NO_ACTIVITY, kb_main())
        return

    txt = CUSTOMER_PROFILE_TITLE
    txt += CUSTOMER_SUMMARY
    txt += CUSTOMER_TOTAL + str(len(jobs)) + "\n"

    last_time = jobs[0].get("created_at", 0)
    if last_time:
        txt += CUSTOMER_LAST + format_relative_time(last_time) + "\n"

    txt += "\n"

    for j in jobs[:10]:
        info = j.get("info", {})
        created = j.get("created_at", 0)
        date_str = format_relative_time(created)

        txt += CUSTOMER_ITEM_HEADER
        txt += "📅 " + date_str + "\n"
        if info.get("sub"):
            txt += "🔧 " + info["sub"] + "\n"
        txt += "👤 " + j.get("expert_name", "?") + "\n"
        if info.get("phone"):
            txt += "📞 " + info["phone"] + "\n"
        txt += "🎫 " + j.get("tracking_code", "?") + "\n\n"

    txt += CUSTOMER_HISTORY_FOOTER

    send_message(chat_id, txt, kb_main())


# ==================== لینک اختصاصی + QR ====================
def _show_expert_link(chat_id, user_id, expert):
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
    send_message(chat_id, txt, kb_share_link_with_qr(link))


def _build_expert_link(code):
    bot_user = config.BOT_USERNAME
    if bot_user:
        return "https://ble.ir/" + bot_user + "?start=" + code
    return "https://ble.ir/yourbot?start=" + code


# ==================== ذخیره لوکیشن ====================
def handle_profile_location(chat_id, user_id, location):
    experts = load_experts()
    for e in experts:
        if e.get("user_id") == user_id:
            e["lat"] = location.get("latitude")
            e["lng"] = location.get("longitude")
            break
    save_experts(experts)
    return True
