# ==================== امنیت ====================
"""
سیستم امنیت:
- بررسی مسدود بودن کاربر
- بررسی متن مشکوک (لینک، تبلیغات)
- Rate limit (با معافیت ادمین)
- قفل ورود ادمین (brute force)
- لاگ رویدادهای امنیتی

⚠️ همه توابع اصلی داخل try/except هستن که اگه خطا دادن،
    ربات کرش نکنه و پیام‌ها رد نشن.
"""
import time
from config import SUPER_ADMIN
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
    find_expert_by_id, get_operators,
)
from utils import is_suspicious_text, format_relative_time


# ==================== Rate Limit State ====================
_rate_limit_store = {}


def _is_admin(user_id):
    """آیا ادمین هست؟ (که rate limit و ... روش اعمال نشه)"""
    try:
        if user_id == SUPER_ADMIN:
            return True
        return user_id in get_operators()
    except:
        return False


# ==================== بررسی دسترسی ====================
def check_user_access(chat_id, user_id):
    """
    آیا کاربر اجازه استفاده داره؟
    Return: True اگه مسدود نیست
    """
    try:
        # ادمین‌ها هرگز مسدود نمی‌شن
        if _is_admin(user_id):
            return True

        if not is_user_blocked(user_id):
            return True

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
    except Exception as ex:
        # اگه خطا داد، بذار پیام رد بشه
        print("[SECURITY] check_user_access error:", str(ex)[:100])
        return True


# ==================== بررسی متن مشکوک ====================
def check_suspicious_text(chat_id, user_id, text):
    """
    Return: True اگه OK، False اگه مشکوک
    """
    try:
        if not text:
            return True

        # ادمین‌ها بررسی نمی‌شن
        if _is_admin(user_id):
            return True

        if is_suspicious_text(text):
            try:
                log_security_event(user_id, "suspicious_text", text[:100])
            except:
                pass
            send_message(chat_id, SEC_SUSPICIOUS_MSG)
            return False
        return True
    except Exception as ex:
        print("[SECURITY] check_suspicious_text error:", str(ex)[:100])
        return True


# ==================== Rate Limit ====================
def check_rate_limit(chat_id, user_id, max_count=60, window_seconds=60):
    """
    Return: True اگه OK، False اگه زیاده
    - ادمین‌ها معاف هستن
    - پیش‌فرض: ۶۰ پیام در ۶۰ ثانیه (خیلی سخاوتمندانه)
    """
    try:
        # ادمین‌ها معاف
        if _is_admin(user_id):
            return True

        now = int(time.time())
        times = _rate_limit_store.get(user_id, [])
        cutoff = now - window_seconds
        times = [t for t in times if t > cutoff]

        if len(times) >= max_count:
            try:
                log_security_event(user_id, "rate_limit_exceeded", str(len(times)))
            except:
                pass
            return False

        times.append(now)
        _rate_limit_store[user_id] = times
        return True
    except Exception as ex:
        print("[SECURITY] check_rate_limit error:", str(ex)[:100])
        return True


# ==================== قفل ورود ادمین ====================
def check_admin_login_locked(chat_id, user_id):
    """آیا ورود ادمین قفل هست؟"""
    try:
        if not is_login_locked(user_id):
            return False

        info = get_login_attempts(user_id)
        locked_until = info.get("locked_until", 0) if info else 0
        minutes = max(1, int((locked_until - time.time()) / 60) + 1)
        send_message(chat_id, SEC_LOGIN_LOCKED.format(minutes=minutes))
        return True
    except Exception as ex:
        print("[SECURITY] check_admin_login_locked error:", str(ex)[:100])
        return False


def do_record_admin_attempt(user_id, success):
    """ثبت تلاش ورود - هیچ‌وقت کرش نکنه"""
    try:
        record_login_attempt(user_id, success)
        try:
            if success:
                log_security_event(user_id, "admin_login_success")
            else:
                log_security_event(user_id, "admin_login_failed")
        except:
            pass
    except Exception as ex:
        print("[SECURITY] do_record_admin_attempt error:", str(ex)[:100])


# ==================== پنل امنیتی ادمین ====================
def show_security_menu(chat_id):
    send_message(chat_id, "🛡 پنل امنیت\n\nیکی از گزینه‌ها رو انتخاب کنید:", kb_security_menu())


def show_security_events(chat_id):
    try:
        events = get_recent_security_events(limit=30)
    except:
        events = []

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
    try:
        blocked = get_blocked_users()
    except:
        blocked = []

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
    try:
        unblock_user(user_id)
        log_security_event(user_id, "unblocked_by_admin")
    except:
        pass
    send_message(chat_id, SEC_UNBLOCKED_OK, kb_security_menu())


# ==================== مسدودسازی ====================
def do_block_user(chat_id, target_id, reason, admin_id, duration_hours=0):
    try:
        block_user(target_id, reason, admin_id, duration_hours)
        log_security_event(target_id, "blocked", reason)
    except:
        pass
    send_message(chat_id, "✅ کاربر {} مسدود شد.".format(target_id), kb_admin())
