# ==================== چت مشتری-تعمیرکار ====================
import time
from texts import (
    BTN_CHAT_EXPERT, BTN_CHAT_CUSTOMER, BTN_MY_CHATS,
    BTN_CHAT_BACK, BTN_CHAT_HIDE, BTN_CHAT_SHARE_PHONE, BTN_CHAT_REFRESH,
    BTN_BACK,
    CHAT_TITLE, CHAT_NO_CHATS, CHAT_NEW_WELCOME,
    CHAT_STARTED_WITH_EXPERT, CHAT_STARTED_WITH_CUSTOMER,
    CHAT_MESSAGE_SENT, CHAT_PHOTO_SENT,
    CHAT_NEW_MESSAGE,
    CHAT_SHARE_PHONE_REQUEST, CHAT_PHONE_SHARED, CHAT_PHONE_ALREADY_SHARED,
    CHAT_HIDDEN_OK, CHAT_NOT_FOUND, CHAT_NO_PERMISSION,
    CHAT_LIST_HEADER, CHAT_MENU_TITLE,
    CHAT_EXPIRED_MSG,
)
from keyboards import (
    kb_chat_expert, kb_chat_customer, kb_chat_menu,
    kb_chat_list, kb_chat_share_phone_confirm, kb_chat_hide_confirm,
    kb_main, kb_back,
)
from api import send_message, api_call
from db import (
    create_chat, get_chat, get_chat_between, update_chat,
    add_message, get_chat_messages, reset_unread,
    get_expert_chats, get_customer_chats,
    find_expert_by_id, share_phone_in_chat, hide_chat,
    load_jobs,
)


# ==================== چت مشتری با تعمیرکار ====================
def start_chat_with_expert(chat_id, customer_id, expert_id, sessions):
    """شروع چت مشتری با تعمیرکار"""
    expert = find_expert_by_id(expert_id)
    if not expert:
        send_message(chat_id, CHAT_NOT_FOUND, kb_main())
        return False
    
    chat = get_chat_between(expert_id, customer_id)
    if not chat:
        chat_id_db = create_chat(expert_id, customer_id)
        chat = get_chat(chat_id_db)
        welcome_msg = CHAT_NEW_WELCOME.format(name=expert.get("name", "تعمیرکار"))
        send_message(chat_id, welcome_msg, kb_chat_expert())
    else:
        send_message(chat_id, CHAT_STARTED_WITH_EXPERT.format(name=expert.get("name", "تعمیرکار")), kb_chat_expert())
    
    sessions[customer_id] = {
        "step": "chat_active",
        "data": {"chat_id": chat["id"], "role": "customer"}
    }
    return True


# ==================== چت تعمیرکار با مشتری ====================
def start_chat_with_customer(chat_id, expert_id, customer_id, sessions):
    """شروع چت تعمیرکار با مشتری"""
    expert = find_expert_by_id(expert_id)
    if not expert:
        send_message(chat_id, CHAT_NOT_FOUND, kb_main())
        return False
    
    chat = get_chat_between(expert_id, customer_id)
    if not chat:
        chat_id_db = create_chat(expert_id, customer_id)
        chat = get_chat(chat_id_db)
    
    send_message(chat_id, CHAT_STARTED_WITH_CUSTOMER, kb_chat_customer())
    
    sessions[expert_id] = {
        "step": "chat_active",
        "data": {"chat_id": chat["id"], "role": "expert"}
    }
    return True


# ==================== دریافت پیام چت ====================
def handle_chat_message(chat_id, user_id, text, sessions):
    """هندل پیام در چت"""
    if user_id not in sessions:
        return False
    session = sessions[user_id]
    if session.get("step") != "chat_active":
        return False
    
    chat_id_db = session["data"].get("chat_id")
    role = session["data"].get("role")
    chat = get_chat(chat_id_db)
    if not chat:
        sessions.pop(user_id, None)
        send_message(chat_id, CHAT_NOT_FOUND, kb_main())
        return True
    
    if text == BTN_BACK or text == BTN_CHAT_BACK:
        sessions.pop(user_id, None)
        if role == "expert":
            show_my_chats(chat_id, user_id)
        else:
            send_message(chat_id, "از منو استفاده کنید.", kb_main())
        return True
    
    if text == BTN_CHAT_HIDE:
        if role == "expert":
            send_message(chat_id, "آیا مطمئنید چت مخفی شود؟", kb_chat_hide_confirm())
        return True
    
    if text == BTN_CHAT_SHARE_PHONE:
        if role == "expert":
            send_message(chat_id, CHAT_SHARE_PHONE_REQUEST, kb_chat_share_phone_confirm())
        return True
    
    # پیام متنی
    if text and text not in [BTN_CHAT_BACK, BTN_CHAT_HIDE, BTN_CHAT_SHARE_PHONE, BTN_BACK]:
        add_message(chat_id_db, user_id, role, text, 0, 0)
        send_message(chat_id, CHAT_MESSAGE_SENT, kb_chat_expert() if role == "customer" else kb_chat_customer())
        notify_other_side(chat_id_db, user_id, role, text, is_photo=False)
        return True
    
    return False


# ==================== دریافت عکس چت ====================
def handle_chat_photo(chat_id, user_id, message_id, sessions):
    """هندل عکس در چت"""
    if user_id not in sessions:
        return False
    session = sessions[user_id]
    if session.get("step") != "chat_active":
        return False
    
    chat_id_db = session["data"].get("chat_id")
    role = session["data"].get("role")
    chat = get_chat(chat_id_db)
    if not chat:
        return False
    
    add_message(chat_id_db, user_id, role, "[عکس]", message_id, 1)
    send_message(chat_id, CHAT_PHOTO_SENT, kb_chat_expert() if role == "customer" else kb_chat_customer())
    notify_other_side(chat_id_db, user_id, role, "[عکس]", is_photo=True, photo_message_id=message_id)
    return True


# ==================== اطلاع به طرف مقابل ====================
def notify_other_side(chat_id_db, sender_id, sender_role, content, is_photo=False, photo_message_id=None):
    """اطلاع به طرف مقابل از پیام جدید"""
    chat = get_chat(chat_id_db)
    if not chat:
        return
    
    if sender_role == "customer":
        target_id = chat["expert_id"]
        sender_name = "مشتری"
    else:
        target_id = chat["customer_id"]
        sender_name = "تعمیرکار"
    
    msg = CHAT_NEW_MESSAGE.format(name=sender_name, message=content)
    
    if is_photo and photo_message_id:
        try:
            api_call("forwardMessage", {
                "chat_id": target_id,
                "from_chat_id": target_id,
                "message_id": photo_message_id
            })
        except:
            pass
    
    # دکمه باز کردن چت
    kb = {"inline_keyboard": [[
        {"text": "💬 باز کردن چت", "callback_data": "chatopen:" + str(chat_id_db)}
    ]]}
    
    send_message(target_id, msg, kb)


# ==================== لیست چت‌های تعمیرکار ====================
def show_my_chats(chat_id, expert_id, filter_type="all"):
    """نمایش لیست چت‌های تعمیرکار"""
    chats = get_expert_chats(expert_id, filter_type)
    
    if not chats:
        send_message(chat_id, CHAT_NO_CHATS, kb_chat_menu())
        return
    
    txt = CHAT_MENU_TITLE + "\n"
    for c in chats[:10]:
        customer = c.get("customer_id", "?")
        unread = c.get("expert_unread", 0)
        last = c.get("last_message_at", 0)
        emoji = "🔴" if unread > 0 else "💬"
        time_ago = _format_time_ago(last)
        txt += "{} مشتری #{} - {} پیام نخونده ({})\n".format(emoji, customer, unread, time_ago)
    
    kb = {"inline_keyboard": []}
    for c in chats[:10]:
        unread = c.get("expert_unread", 0)
        emoji = "🔴" if unread > 0 else "💬"
        kb["inline_keyboard"].append([
            {"text": "{} مشتری #{}".format(emoji, c.get("customer_id", "?")),
             "callback_data": "chatopen:" + str(c["id"])}
        ])
    
    send_message(chat_id, txt, kb_chat_menu())
    send_message(chat_id, "برای دیدن چت، روی دکمه بزنید:", kb)


# ==================== باز کردن چت ====================
def open_chat(chat_id, user_id, chat_id_db, sessions):
    """باز کردن یه چت خاص"""
    chat = get_chat(chat_id_db)
    if not chat:
        return False
    
    if chat["expert_id"] != user_id and chat["customer_id"] != user_id:
        send_message(chat_id, CHAT_NO_PERMISSION)
        return False
    
    role = "expert" if chat["expert_id"] == user_id else "customer"
    reset_unread(chat_id_db, role)
    
    messages = get_chat_messages(chat_id_db, 10)
    txt = "💬 چت فعال\n\n"
    if messages:
        for m in messages:
            sender = "👤 شما" if m["sender_id"] == user_id else "👥 طرف مقابل"
            if m.get("is_photo"):
                txt += "{}: [عکس]\n".format(sender)
            else:
                txt += "{}: {}\n".format(sender, m.get("content", ""))
    else:
        txt += "هنوز پیامی ارسال نشده.\n"
    
    txt += "\n━━━━━━━━━━━━━━━━━\n"
    txt += "برای ارسال پیام، تایپ کنید یا عکس بفرستید."
    
    sessions[user_id] = {
        "step": "chat_active",
        "data": {"chat_id": chat_id_db, "role": role}
    }
    
    kb = kb_chat_expert() if role == "customer" else kb_chat_customer()
    send_message(chat_id, txt, kb)
    return True


# ==================== اشتراک شماره ====================
def do_share_phone(chat_id, user_id, sessions):
    """اشتراک شماره تلفن بین دو طرف"""
    if user_id not in sessions:
        return False
    session = sessions[user_id]
    if session.get("step") != "chat_active":
        return False
    
    chat_id_db = session["data"].get("chat_id")
    role = session["data"].get("role")
    chat = get_chat(chat_id_db)
    if not chat:
        return False
    
    # گرفتن شماره تعمیرکار
    expert = find_expert_by_id(chat["expert_id"])
    expert_phone = expert.get("phone", "?") if expert else "?"
    
    # گرفتن شماره مشتری از job info
    customer_phone = "?"
    jobs = load_jobs()
    for j in reversed(jobs):
        if j.get("customer_id") == chat["customer_id"] and j.get("expert_id") == chat["expert_id"]:
            info = j.get("info", {})
            if info.get("phone"):
                customer_phone = info["phone"]
                break
    
    # اگه شماره مشتری موجود نبود
    if customer_phone == "?":
        send_message(chat_id, 
            "❌ متأسفانه شماره مشتری در سیستم ثبت نشده.\n"
            "لطفاً از مشتری بخواهید شماره‌اش را در چت ارسال کند.")
        return True
    
    # ثبت اشتراک
    share_phone_in_chat(chat_id_db)
    
    # پیام برای هر دو طرف
    msg = CHAT_PHONE_SHARED.format(
        expert_phone=expert_phone,
        customer_phone=customer_phone
    )
    
    # ارسال به خود کاربر
    send_message(chat_id, msg)
    
    # ارسال به طرف مقابل
    if role == "expert":
        other_id = chat["customer_id"]
    else:
        other_id = chat["expert_id"]
    
    send_message(other_id, msg)
    return True


# ==================== مخفی کردن چت ====================
def do_hide_chat(chat_id, user_id, sessions):
    """مخفی کردن چت"""
    if user_id not in sessions:
        return False
    session = sessions[user_id]
    if session.get("step") != "chat_active":
        return False
    
    chat_id_db = session["data"].get("chat_id")
    role = session["data"].get("role")
    
    hide_chat(chat_id_db, role)
    sessions.pop(user_id, None)
    
    send_message(chat_id, CHAT_HIDDEN_OK, kb_main())
    return True


# ==================== کمکی ====================
def _format_time_ago(timestamp):
    """نمایش زمان نسبی"""
    if not timestamp:
        return "جدید"
    diff = int(time.time()) - timestamp
    if diff < 60:
        return "همین الان"
    if diff < 3600:
        return "{} دقیقه پیش".format(diff // 60)
    if diff < 86400:
        return "{} ساعت پیش".format(diff // 3600)
    return "{} روز پیش".format(diff // 86400)
