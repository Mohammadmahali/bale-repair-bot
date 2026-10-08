# ==================== کیف پول ====================
import time
from config import CARD_NUMBER, CARD_OWNER, FREE_DAYS, SUPER_ADMIN
from texts import (
    WALLET_TITLE, WALLET_BALANCE, WALLET_FREE_PERIOD, WALLET_FREE_LEFT,
    WALLET_STATUS_FREE, WALLET_STATUS_CHARGED, WALLET_STATUS_LOW,
    WALLET_STATUS_EMPTY, WALLET_HISTORY,
    WALLET_CHARGE_INTRO, WALLET_INVALID_AMOUNT,
    WALLET_ASK_RECEIPT, WALLET_RECEIPT_SENT,
    WALLET_ADMIN_NEW,
    BTN_BACK, BTN_CHARGE_WALLET,
)
from keyboards import kb_back, kb_wallet, kb_main, kb_wallet_admin
from api import send_message, api_call
from db import (
    find_expert_by_id, get_wallet_balance,
    create_wallet_charge_request, is_expert_in_free_period,
    get_expert_wallet_history, get_operators,
)


def show_wallet(chat_id, user_id):
    """نمایش کیف پول"""
    expert = find_expert_by_id(user_id)
    if not expert:
        send_message(chat_id, "شما ثبت‌نام نکردید.", kb_main())
        return
    
    balance = get_wallet_balance(user_id)
    txt = WALLET_TITLE
    txt += WALLET_BALANCE.format(balance="{:,}".format(balance))
    
    if is_expert_in_free_period(expert):
        created = expert.get("created_at", int(time.time()))
        free_until = created + (FREE_DAYS * 86400)
        days_left = max(0, int((free_until - time.time()) / 86400))
        txt += WALLET_FREE_PERIOD
        txt += WALLET_FREE_LEFT.format(days=days_left)
        txt += "\n" + WALLET_STATUS_FREE
    else:
        if balance <= 0:
            txt += "\n" + WALLET_STATUS_EMPTY
        elif balance < 50000:
            txt += "\n" + WALLET_STATUS_LOW
        else:
            txt += "\n" + WALLET_STATUS_CHARGED
    
    # تاریخچه
    history = get_expert_wallet_history(user_id, 5)
    if history:
        txt += WALLET_HISTORY
        for h in history:
            status_map = {
                "pending": "⏳ در انتظار",
                "approved": "✅ تأیید",
                "rejected": "❌ رد",
            }
            txt += "• {} {} تومان - {}\n".format(
                "+" if h.get("type") == "charge" else "-",
                "{:,}".format(h.get("amount", 0)),
                status_map.get(h.get("status", ""), h.get("status", ""))
            )
    
    send_message(chat_id, txt, kb_wallet())


def start_charge(chat_id, user_id, sessions):
    """شروع فرآیند شارژ"""
    txt = WALLET_CHARGE_INTRO.format(
        card=CARD_NUMBER,
        owner=CARD_OWNER
    )
    sessions[user_id] = {"step": "wallet_amount", "data": {}}
    send_message(chat_id, txt, kb_back())


def handle_amount(chat_id, user_id, text, sessions):
    """دریافت مبلغ"""
    try:
        amount = int(text.strip().replace(",", "").replace("،", ""))
    except:
        send_message(chat_id, WALLET_INVALID_AMOUNT, kb_back())
        return False
    
    if amount < 10000 or amount > 10000000:
        send_message(chat_id, WALLET_INVALID_AMOUNT, kb_back())
        return False
    
    sessions[user_id]["data"]["amount"] = amount
    sessions[user_id]["step"] = "wallet_receipt"
    
    send_message(
        chat_id,
        WALLET_ASK_RECEIPT.format(amount="{:,}".format(amount)),
        kb_back()
    )
    return True


def handle_receipt(chat_id, user_id, message_id, sessions):
    """دریافت عکس رسید"""
    if user_id not in sessions:
        return False
    session = sessions[user_id]
    if session.get("step") != "wallet_receipt":
        return False
    
    amount = session["data"].get("amount", 0)
    if amount <= 0:
        sessions.pop(user_id, None)
        send_message(chat_id, "خطا در مبلغ. دوباره تلاش کنید.", kb_main())
        return False
    
    # ساخت درخواست
    txn_id = create_wallet_charge_request(user_id, amount, message_id)
    if not txn_id:
        send_message(chat_id, "خطا در ثبت. دوباره تلاش کنید.", kb_main())
        sessions.pop(user_id, None)
        return False
    
    send_message(chat_id, WALLET_RECEIPT_SENT, kb_main())
    sessions.pop(user_id, None)
    
    # ارسال به مدیر
    notify_admin_receipt(user_id, amount, message_id, txn_id, chat_id)
    return True


def notify_admin_receipt(user_id, amount, message_id, txn_id, expert_chat_id):
    """اطلاع به مدیر از رسید جدید (از طریق ربات ادمین)"""
    from api_admin import admin_send_message, admin_forward_message
    expert = find_expert_by_id(user_id)
    if not expert:
        return
    
    # اول forward عکس رسید با ربات ادمین
    try:
        admin_forward_message(SUPER_ADMIN, expert_chat_id, message_id)
    except Exception as ex:
        print("Forward error:", str(ex)[:100])
    
    # بعد پیام اطلاعات + دکمه
    txt = WALLET_ADMIN_NEW.format(
        name=expert.get("name", "?"),
        user_id=user_id,
        phone=expert.get("phone", "?"),
        amount="{:,}".format(amount),
        date=time.strftime("%Y/%m/%d - %H:%M", time.localtime())
    )
    
    kb = kb_wallet_admin(txn_id)
    admin_send_message(SUPER_ADMIN, txt, kb)
    
    # برای اپراتورها
    for op in get_operators():
        try:
            admin_forward_message(op, expert_chat_id, message_id)
            admin_send_message(op, txt, kb)
        except:
            pass
