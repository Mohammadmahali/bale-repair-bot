# ==================== نگهداری ۶ ماهه ====================
"""
پاکسازی خودکار داده‌های قدیمی‌تر از ۶ ماه:
- jobs (پروژه‌های قدیمی)
- comments (نظرات قدیمی)
- device_logs (لاگ‌های قدیمی)
- wallet_transactions (تراکنش‌های تسویه‌شده)
- security_events (رویدادهای قدیمی)
"""
import time
from texts import RETENTION_CLEANUP_DONE_FULL, RETENTION_CLEANUP_START
from db import cleanup_old_data, get_operators
from config import SUPER_ADMIN


def run_cleanup(days=180, notify_admin=False):
    """
    پاکسازی داده‌های قدیمی‌تر از days روز
    """
    print(RETENTION_CLEANUP_START)
    try:
        result = cleanup_old_data(days=days)
        print("[RETENTION] Cleanup done:", result)

        if notify_admin:
            _notify_admins(result, days)

        return result
    except Exception as ex:
        print("[RETENTION] Error:", str(ex)[:200])
        return None


def _notify_admins(result, days):
    """اطلاع به ادمین‌ها (اختیاری)"""
    try:
        from api_admin import admin_send_message
        msg = RETENTION_CLEANUP_DONE_FULL.format(
            jobs=result.get("jobs", 0),
            comments=result.get("comments", 0),
            logs=result.get("logs", 0),
            txns=result.get("txns", 0),
            events=result.get("events", 0),
        )
        msg += "\n\n📅 حذف داده‌های قدیمی‌تر از {} روز".format(days)

        admin_send_message(SUPER_ADMIN, msg)
        for op in get_operators():
            try:
                admin_send_message(op, msg)
            except:
                pass
    except Exception as ex:
        print("[RETENTION] Notify error:", str(ex)[:100])


def check_retention():
    """
    این تابع از حلقه اصلی صدا زده می‌شه
    اگه ۲۴ ساعت از آخرین پاکسازی گذشته باشه، اجرا می‌کنه
    """
    from database import config_get, config_set

    last_run = config_get("last_retention_run", 0)
    now = int(time.time())

    if now - last_run < 86400:  # ۲۴ ساعت
        return

    # اجرا
    run_cleanup(days=180, notify_admin=False)
    config_set("last_retention_run", now)
