# ==================== امنیت ====================
"""
سیستم امنیت:
- بررسی مسدود بودن کاربر
- بررسی متن مشکوک (لینک، تبلیغات)
- Rate limit برای پیام‌های تکراری
- قفل ورود ادمین (brute force)
- لاگ رویدادهای امنیتی
"""
import time
from texts import (
    SEC_SUSPICIOUS_MSG, SEC_BLOCKED_PERMANENT, SEC_BLOCKED_TEMP,
    SEC_LOGIN_LOCKED, SEC_LOGIN_ATTEMPTS_LEFT,
    ADM_SEC_EVENTS, ADM_SEC_BLOCKED, SEC_EVENTS_TITLE,
    SEC_EVENTS_EMPTY, SEC_BLOCKED_TITLE, SEC_BLOCKED_EMPTY,
    SEC_UNBLOCKED_OK, SEC_EVENT_LINE, SEC_BLOCKED_LINE,
    BTN_BACK,
)
from keyboards import kb_security_menu, kb_blocked_user, kb_admin
from api import send_message
from db import (
    is_user_blocked, block_user, unblock_user,
    get_blocked_users, is_login_locked,
    record_login_attempt, reset_login_attempts,
    log_security_event, get_recent_security_events,
    find_expert_by_id,
)
from utils import is_suspicious_text, format_relative_time


# ==================== Rate Limit State ====================
_rate_limit_store = {}  # {user_id: [timestamps]}


# ==================== بررسی دسترسی ====================
def check_user_access(chat_id, user_id):
    """
    آیا کاربر اجازه استفاده داره؟
    Return: True اگه مسدود نیست، False اگه مسدود هست (پیام فرستاده می‌شه)
    """
    if not is_user_blocked(user_id):
        return True

    from db import get_blocked_users
    blocked = get_blocked_users()
    info = None
    for b in blocked:
        if b.get("user_id") == user_id:
            info = b
            break

    if not info:
        return True

    reason = info.get("reason", "نامشخص")
    until = info.get("blocked_until", 0)

    if until == 0:
        send_message(chat_id, SEC_BLOCKED_PERMANENT.format(reason=reason))
    else:
        until_str = time.strftime("%Y/%m/%d - %H:%M", time.localtime(until))
        send_message(chat_id, SEC_BLOCKED_TEMP.format(reason=reason, until=until_str))
    return False


# ==================== بررسی متن مشکوک ====================
def check_suspicious_text(chat_id, user_id, text):
    """
    بررسی متن مشکوک
    Return: True اگه OK، False اگه مشکوک (پیام فرستاده شده)
    """
    if not text:
        return True

    if is_suspicious_text(text):
        log_security_event(user_id, "suspicious_text", text[:100])
        send_message(chat_id, SEC_SUSPICIOUS_MSG)
        return False
    return True


# ==================== Rate Limit ====================
def check_rate_limit(chat_id, user_id, max_count=10, window_seconds=60):
    """
    بررسی rate limit
    Return: True اگه OK، False اگه زیاده
    """
    now = int(time.time())
    times = _rate_limit_store.get(user_id, [])
    cutoff = now - window_seconds
    times = [t for t in times if t > cutoff]

    if len(times) >= max_count:
        log_security_event(user_id, "rate_limit_exceeded", str(len(times)))
        return False

    times.append(now)
    _rate_limit_store[user_id] = times
    return True


# ==================== قفل ورود ادمین ====================
def check_admin_login_locked(chat_id, user_id):
    """آیا ورود ادمین قفل هست؟"""
    if not is_login_locked(user_id):
        return False

    from db import get_login_attempts
    info = get_login_attempts(user_id)
    locked_until = info.get("locked_until", 0) if info else 0
    minutes = max(1, int((locked_until - time.time()) / 60) + 1)
    send_message(chat_id, SEC_LOGIN_LOCKED.format(minutes=minutes))
    return True


def do_record_admin_attempt(user_id, success):
    """ثبت تلاش ورود"""
    record_login_attempt(user_id, success)
    if success:
        log_security_event(user_id, "admin_login_success")
    else:
        log_security_event(user_id, "admin_login_failed")


# ==================== پنل امنیتی ادمین ====================
def show_security_menu(chat_id):
    send_message(chat_id, "🛡 پنل امنیت\n\nیکی از گزینه‌ها رو انتخاب کنید:", kb_security_menu())


def show_security_events(chat_id):
    events = get_recent_security_events(limit=30)
    if not events:
        send_message(chat_id, SEC_EVENTS_EMPTY, kb_security_menu())
        return

    txt = SEC_EVENTS_TITLE
    for e in events[:20]:
        user = e.get("user_id", "?")
        evt = e.get("event_type", "?")
        date = format_relative_time(e.get("created_at", 0))
        txt += SEC_EVENT_LINE.format(date=date, user=user, type=evt)

    send_message(chat_id, txt, kb_security_menu())


def show_blocked_users(chat_id):
    blocked = get_blocked_users()
    if not blocked:
        send_message(chat_id, SEC_BLOCKED_EMPTY, kb_security_menu())
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

    send_message(chat_id, txt, kb)


def do_unblock_user(chat_id, user_id):
    unblock_user(user_id)
    log_security_event(user_id, "unblocked_by_admin")
    send_message(chat_id, SEC_UNBLOCKED_OK, kb_security_menu())


# ==================== مسدودسازی ====================
def do_block_user(chat_id, target_id, reason, admin_id, duration_hours=0):
    block_user(target_id, reason, admin_id, duration_hours)
    log_security_event(target_id, "blocked", reason)
    send_message(chat_id, "✅ کاربر {} مسدود شد.".format(target_id), kb_admin())
