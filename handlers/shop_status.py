# ==================== وضعیت مغازه ====================
import time
from texts import (
    SHOP_STATUS_TITLE, SHOP_ACTIVE, SHOP_CLOSED_TEMP, SHOP_CLOSED_PERM,
    SHOP_ASK, SHOP_ASK_FROM_DAY, SHOP_ASK_DAYS, SHOP_ASK_REASON,
    SHOP_SKIP_REASON, SHOP_CLOSE_OK, SHOP_REOPEN, SHOP_REOPENED,
    SHOP_REOPENED_NOTIFY, SHOP_COUNTDOWN, SHOP_DAYS,
    YES, NO, BTN_BACK, CHOOSE_OPTION, INVALID_INPUT, USE_MENU,
)
from keyboards import kb_main, kb_back, kb_shop_status
from api import send_message
from db import load_experts, save_experts, find_expert_by_id
from utils import parse_single_number, format_numbered_list


# ==================== نمایش وضعیت مغازه ====================
def show_shop_status(chat_id, user_id):
    """نمایش صفحه وضعیت مغازه"""
    expert = find_expert_by_id(user_id)
    if not expert:
        send_message(chat_id, "شما ثبت‌نام نکردید.", kb_main())
        return
    
    txt = SHOP_STATUS_TITLE + _get_shop_label(expert)
    
    if expert.get("shop_status") == "closed_temp" and expert.get("closed_until", 0) > time.time():
        days = max(1, int((expert["closed_until"] - time.time()) / 86400) + 1)
        txt += "\n⏳ " + str(days) + SHOP_DAYS + " باقی مونده"
        if expert.get("close_reason"):
            txt += "\n📝 " + expert["close_reason"]
        
        kb = {
            "inline_keyboard": [[
                {"text": SHOP_REOPEN, "callback_data": "shop:open"}
            ]]
        }
        send_message(chat_id, txt, kb)
    else:
        send_message(chat_id, txt + "\n\n" + SHOP_ASK, kb_shop_status())


def _get_shop_label(expert):
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


# ==================== تعطیلی موقت ====================
def start_temp_close(chat_id, user_id, sessions):
    """شروع فرآیند تعطیلی موقت"""
    sessions[user_id] = {"step": "shop_close_from", "data": {}}
    send_message(chat_id, SHOP_ASK_FROM_DAY, kb_back())


# ==================== ادامه فرآیند ====================
def continue_shop_close(chat_id, user_id, text, sessions):
    """ادامه فرآیند تعطیلی مغازه"""
    if user_id not in sessions:
        return False
    
    session = sessions[user_id]
    step = session["step"]
    data = session["data"]
    
    # ===== بازگشت =====
    if text == BTN_BACK:
        sessions.pop(user_id, None)
        send_message(chat_id, USE_MENU, kb_main())
        return True
    
    # ===== مرحله ۱: از چند روز دیگه =====
    if step == "shop_close_from":
        try:
            days_from = int(text.strip())
            if days_from < 0 or days_from > 365:
                raise ValueError
        except:
            send_message(chat_id, INVALID_INPUT, kb_back())
            return True
        
        data["days_from"] = days_from
        session["step"] = "shop_close_days"
        send_message(chat_id, SHOP_ASK_DAYS, kb_back())
        return True
    
    # ===== مرحله ۲: چند روز تعطیل =====
    if step == "shop_close_days":
        try:
            days_count = int(text.strip())
            if days_count < 1 or days_count > 365:
                raise ValueError
        except:
            send_message(chat_id, INVALID_INPUT, kb_back())
            return True
        
        data["days_count"] = days_count
        session["step"] = "shop_close_reason"
        send_message(chat_id, SHOP_ASK_REASON, kb_back())
        return True
    
    # ===== مرحله ۳: دلیل تعطیلی =====
    if step == "shop_close_reason":
        reason = "" if text == SHOP_SKIP_REASON else text.strip()
        days_from = data.get("days_from", 0)
        days_count = data.get("days_count", 1)
        
        # محاسبه زمان شروع و پایان
        now = int(time.time())
        start_time = now + (days_from * 86400)
        end_time = start_time + (days_count * 86400)
        
        # ذخیره
        experts = load_experts()
        for e in experts:
            if e.get("user_id") == user_id:
                e["shop_status"] = "closed_temp"
                e["closed_from"] = start_time
                e["closed_until"] = end_time
                e["close_reason"] = reason
                break
        save_experts(experts)
        
        sessions.pop(user_id, None)
        
        # پیام تأیید
        if days_from == 0:
            msg = SHOP_CLOSE_OK + " از امروز"
        elif days_from == 1:
            msg = SHOP_CLOSE_OK + " از فردا"
        else:
            msg = SHOP_CLOSE_OK + " از " + str(days_from) + " روز دیگه"
        msg += " به مدت " + str(days_count) + SHOP_DAYS
        
        send_message(chat_id, msg, kb_main())
        return True
    
    return False


# ==================== تعطیلی دائم ====================
def set_permanent_close(chat_id, user_id):
    """تعطیلی دائمی مغازه"""
    experts = load_experts()
    for e in experts:
        if e.get("user_id") == user_id:
            e["shop_status"] = "closed_perm"
            e["closed_until"] = 0
            e["closed_from"] = 0
            break
    save_experts(experts)
    send_message(chat_id, "🔴 مغازه به صورت دائم تعطیل شد.", kb_main())


# ==================== فعال‌سازی مجدد ====================
def set_shop_active(chat_id, user_id):
    """فعال کردن مجدد مغازه"""
    experts = load_experts()
    for e in experts:
        if e.get("user_id") == user_id:
            e["shop_status"] = "active"
            e["closed_until"] = 0
            e["closed_from"] = 0
            e["close_reason"] = ""
            break
    save_experts(experts)
    send_message(chat_id, SHOP_REOPENED, kb_main())


# ==================== بررسی فعال‌سازی خودکار ====================
def check_shop_reactivations():
    """بررسی مغازه‌های تعطیل که باید فعال بشن"""
    experts = load_experts()
    now = time.time()
    changed = False
    
    for e in experts:
        if e.get("shop_status") == "closed_temp":
            if e.get("closed_until", 0) <= now and e.get("closed_until", 0) > 0:
                e["shop_status"] = "active"
                e["closed_until"] = 0
                e["closed_from"] = 0
                try:
                    send_message(e["user_id"], SHOP_REOPENED_NOTIFY)
                except:
                    pass
                changed = True
    
    if changed:
        save_experts(experts)
