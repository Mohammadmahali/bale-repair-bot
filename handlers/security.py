# ==================== امنیت (فقط پنل ادمین) ====================
"""
این ماژول فقط توابع نمایش پنل امنیتی ادمین رو داره.
هیچ auto-block یا rate limit اینجا اعمال نمی‌شه.
قفل ورود ادمین در database.py و admin_bot.py مدیریت می‌شه.
"""
import time
from texts import (
    ADM_SEC_EVENTS, ADM_SEC_BLOCKED, SEC_EVENTS_TITLE,
    SEC_EVENTS_EMPTY, SEC_BLOCKED_TITLE, SEC_BLOCKED_EMPTY,
    SEC_UNBLOCKED_OK, SEC_EVENT_LINE, SEC_BLOCKED_LINE,
    BTN_BACK,
)
from keyboards import kb_security_menu, kb_admin
from api_admin import admin_send_message
from db import (
    unblock_user, get_blocked_users,
    log_security_event, get_recent_security_events,
)
from utils import format_relative_time


def show_security_menu(chat_id):
    admin_send_message(chat_id, "🛡 پنل امنیت\n\nیکی از گزینه‌ها رو انتخاب کنید:", kb_security_menu())


def show_security_events(chat_id):
    try:
        events = get_recent_security_events(limit=30)
    except:
        events = []

    if not events:
        admin_send_message(chat_id, SEC_EVENTS_EMPTY, kb_security_menu())
        return

    txt = SEC_EVENTS_TITLE
    for e in events[:20]:
        user = e.get("user_id", "?")
        evt = e.get("event_type", "?")
        date = format_relative_time(e.get("created_at", 0))
        txt += SEC_EVENT_LINE.format(date=date, user=user, type=evt)

    admin_send_message(chat_id, txt, kb_security_menu())


def show_blocked_users(chat_id):
    try:
        blocked = get_blocked_users()
    except:
        blocked = []

    if not blocked:
        admin_send_message(chat_id, SEC_BLOCKED_EMPTY, kb_security_menu())
        return

    txt = SEC_BLOCKED_TITLE
    kb = {"inline_keyboard": []}
    for b in blocked[:20]:
        user = b.get("user_id", "?")
        reason = b.get("reason", "?")
        date = format_relative_time(b.get("blocked_at", 0))
        txt += SEC_BLOCKED_LINE.format(user=user, reason=reason, date=date)
        kb["inline_keyboard"].append([
            {"text": "🔓 {} - {}".format(user, reason[:20]),
             "callback_data": "adm:unblock:" + str(user)}
        ])

    kb["inline_keyboard"].append([
        {"text": BTN_BACK, "callback_data": "adm:backmain"}
    ])

    admin_send_message(chat_id, txt, kb)


def do_unblock_user(chat_id, user_id):
    try:
        unblock_user(user_id)
        log_security_event(user_id, "unblocked_by_admin")
    except:
        pass
    admin_send_message(chat_id, SEC_UNBLOCKED_OK, kb_security_menu())


def do_block_user(chat_id, target_id, reason, admin_id, duration_hours=0):
    from db import block_user
    try:
        block_user(target_id, reason, admin_id, duration_hours)
        log_security_event(target_id, "blocked", reason)
    except:
        pass
    admin_send_message(chat_id, "✅ کاربر {} مسدود شد.".format(target_id), kb_admin())
