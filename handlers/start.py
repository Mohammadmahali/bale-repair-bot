# ==================== هندلر شروع و منو ====================
import time
from config import SUPER_ADMIN
from texts import (
    WELCOME, BTN_REGISTER, BTN_SEARCH_SIMPLE, BTN_SEARCH_ADVANCED,
    BTN_EXPERTS_LIST, BTN_MY_PROFILE, BTN_FEEDBACK, BTN_SHOP_STATUS,
    WELCOME_VIA_LINK, EXPERT_NOT_FOUND, PUBLIC_PROFILE,
    USE_MENU, FEEDBACK_MSG, FEEDBACK_EMPTY,
    LBL_NAME, LBL_ROLE, LBL_SUBSPEC, LBL_AREA, LBL_PHONE,
    LBL_ONSITE, LBL_RATING, LBL_REFERRAL,
    YES, NO,
)
from keyboards import kb_main
from api import send_message
from db import (
    find_expert_by_code, find_expert_by_id, load_experts,
    get_feedback_id, is_shop_open,
)


# ==================== /start ====================
def handle_start(chat_id, user_id, text, sessions):
    """هندل کردن دستور /start"""
    
    # بررسی اگه با کد اختصاصی اومده
    if text.startswith("/start "):
        payload = text[7:].strip()
        sessions.pop(user_id, None)
        if payload:
            expert = find_expert_by_code(payload)
            if expert and expert.get("status", "approved") == "approved":
                send_message(chat_id, WELCOME_VIA_LINK)
                send_message(chat_id, format_public_profile(expert), kb_main())
                return
            else:
                send_message(chat_id, EXPERT_NOT_FOUND)
        send_message(chat_id, WELCOME, kb_main())
        return
    
    # /start معمولی
    sessions.pop(user_id, None)
    send_message(chat_id, WELCOME, kb_main())


# ==================== نمایش پروفایل عمومی ====================
def format_public_profile(expert):
    """فرمت پروفایل عمومی تعمیرکار"""
    txt = PUBLIC_PROFILE
    txt += LBL_NAME + " " + expert.get("name", "?") + "\n"
    txt += LBL_ROLE + " " + expert.get("category", "?") + "\n"
    txt += LBL_SUBSPEC + " " + "، ".join(expert.get("sub_specialties", [])) + "\n"
    txt += LBL_AREA + " " + expert.get("area", "?") + "\n"
    txt += LBL_PHONE + " " + expert.get("phone", "?") + "\n"
    txt += LBL_ONSITE + " " + (YES if expert.get("works_on_site") else NO) + "\n\n"
    txt += "⭐ " + "{:.1f}/5".format(_calc_rating(expert))
    rv = _count_reviews(expert)
    if rv > 0:
        txt += " (" + str(rv) + " نظر)"
    txt += "\n"
    txt += LBL_REFERRAL + str(expert.get("referral_count", 0))
    return txt


def _calc_rating(expert):
    total = 0
    count = 0
    ratings = expert.get("ratings_by_stage", {})
    for stage in ["0", "1", "2"]:
        for key, val in ratings.get(stage, {}).items():
            if isinstance(val, dict) and val.get("count", 0) > 0:
                total += val["sum"]
                count += val["count"]
    if count == 0:
        return 5.0
    return total / count


def _count_reviews(expert):
    """تعداد کل نظرات"""
    max_count = 0
    ratings = expert.get("ratings_by_stage", {})
    for stage in ["0", "1", "2"]:
        for key, val in ratings.get(stage, {}).items():
            if isinstance(val, dict):
                max_count = max(max_count, val.get("count", 0))
    return max_count


# ==================== نمایش لیست متخصصین ====================
def handle_experts_list(chat_id):
    """نمایش لیست همه متخصصین"""
    experts = [
        e for e in load_experts()
        if e.get("status", "approved") == "approved" and is_shop_open(e)
    ]
    
    if not experts:
        send_message(chat_id, "هنوز متخصصی نیست.", kb_main())
        return
    
    txt = "📋 لیست متخصصین:\n\n"
    for e in experts[:20]:
        txt += "👤 " + e.get("name", "?") + " | ⭐ {:.1f}".format(_calc_rating(e)) + "\n"
        txt += "   📂 " + e.get("category", "?") + "\n"
        txt += "   📍 " + e.get("area", "?") + "\n"
        txt += "   📞 " + e.get("phone", "?") + "\n\n"
    
    send_message(chat_id, txt, kb_main())


# ==================== نظرات و پیشنهادات ====================
def handle_feedback(chat_id):
    """نمایش آیدی نظرات و پیشنهادات"""
    feedback_id = get_feedback_id()
    if feedback_id:
        send_message(chat_id, FEEDBACK_MSG + feedback_id, kb_main())
    else:
        send_message(chat_id, FEEDBACK_EMPTY, kb_main())
