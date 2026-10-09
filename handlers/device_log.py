# ==================== لاگ عیوب دستگاه ====================
"""
سیستم لاگ عیوب:
- مشتری موقع درخواست، عیب اولیه رو ثبت می‌کنه (خودکار)
- تعمیرکار می‌تونه عیب‌های تشخیصی اضافه کنه
- مشتری می‌تونه نتیجه نهایی رو ثبت کنه
- همه لاگ‌ها با تاریخ، نویسنده، نقش
- ویرایش با ثبت متن قبلی
"""
import time
from texts import (
    BTN_BACK, BTN_ADD_DEFECT, BTN_VIEW_DEVICE_LOGS, BTN_MY_DEVICE_LOGS,
    BTN_DEVICE_LOG_EDIT, INVALID_INPUT, USE_MENU,
    DEVICE_LOG_EMPTY, DEVICE_LOG_FOR_JOB,
    DEVICE_LOG_ASK_DEVICE_NAME, DEVICE_LOG_ASK_DEFECT,
    DEVICE_LOG_ADDED, DEVICE_LOG_UPDATED, DEVICE_LOG_DELETED_MSG,
    DEVICE_LOG_EDIT_ASK, DEVICE_LOG_ONLY_AUTHOR, DEVICE_LOG_NO_JOBS,
    DEVICE_LOG_ITEM_SIMPLE, DEVICE_LOG_ITEM_EDITED,
    DEVICE_LOG_NEW_NOTIFY,
    BTN_REGISTER,
)
from keyboards import (
    kb_main, kb_back, kb_device_log_menu, kb_device_log_item,
    kb_device_log_confirm_delete,
)
from api import send_message
from db import (
    find_expert_by_id, find_job_by_code, get_customer_history,
    add_device_log, get_device_logs, get_device_log,
    update_device_log, delete_device_log, get_customer_jobs_with_logs,
)
from utils import sanitize_text, format_relative_time


# ==================== نمایش منوی لاگ ====================
def show_device_log_menu(chat_id, user_id, sessions):
    """منوی مدیریت لاگ عیوب"""
    # اگه تعمیرکاره یا مشتری، همون منو
    send_message(
        chat_id,
        "📋 مدیریت لاگ عیوب دستگاه\n\n"
        "می‌تونید عیب جدیدی ثبت کنید یا لاگ‌های قبلی رو ببینید:",
        kb_device_log_menu()
    )


# ==================== افزودن عیب جدید ====================
def start_add_defect(chat_id, user_id, sessions):
    """شروع افزودن عیب - اول کد پیگیری"""
    sessions[user_id] = {"step": "devlog_job_code", "data": {}}
    send_message(
        chat_id,
        "🎫 کد پیگیری دستگاه رو وارد کنید:\n\n"
        "(کدی که موقع درخواست تعمیرکار گرفته بودید)",
        kb_back()
    )


def continue_add_defect(chat_id, user_id, text, sessions):
    """ادامه افزودن عیب"""
    if user_id not in sessions:
        return False
    session = sessions[user_id]
    step = session["step"]
    data = session["data"]

    if text == BTN_BACK:
        sessions.pop(user_id, None)
        send_message(chat_id, USE_MENU, kb_main())
        return True

    # ===== مرحله: کد پیگیری =====
    if step == "devlog_job_code":
        code = text.strip().upper()
        job = find_job_by_code(code)
        if not job:
            send_message(chat_id, "❌ کدی با این شماره پیدا نشد. دوباره وارد کنید:", kb_back())
            return True

        # چک دسترسی: کاربر باید مشتری یا تعمیرکار این job باشه
        is_customer = (job.get("customer_id") == user_id)
        is_expert = (job.get("expert_id") == user_id)
        if not is_customer and not is_expert:
            send_message(chat_id, "❌ شما به این پروژه دسترسی ندارید.", kb_main())
            sessions.pop(user_id, None)
            return True

        data["job_code"] = code
        data["job"] = job
        data["author_role"] = "expert" if is_expert else "customer"

        # چک: اگه job توی دیتابیس device_name داره، مستقیم برو به عیب
        if job.get("device_name"):
            data["device_name"] = job["device_name"]
            session["step"] = "devlog_defect"
            send_message(chat_id, DEVICE_LOG_ASK_DEFECT, kb_back())
        else:
            session["step"] = "devlog_device"
            send_message(chat_id, DEVICE_LOG_ASK_DEVICE_NAME, kb_back())
        return True

    # ===== مرحله: نام دستگاه =====
    if step == "devlog_device":
        name = sanitize_text(text, 100)
        if len(name) < 2:
            send_message(chat_id, "❌ نام دستگاه خیلی کوتاهه. دوباره وارد کنید:", kb_back())
            return True
        data["device_name"] = name
        session["step"] = "devlog_defect"
        send_message(chat_id, DEVICE_LOG_ASK_DEFECT, kb_back())
        return True

    # ===== مرحله: متن عیب =====
    if step == "devlog_defect":
        defect = sanitize_text(text, 500)
        if len(defect) < 3:
            send_message(chat_id, "❌ متن عیب خیلی کوتاهه. دوباره وارد کنید:", kb_back())
            return True

        job = data.get("job", {})
        author_role = data.get("author_role", "customer")

        log_id = add_device_log(
            job_code=data.get("job_code", ""),
            expert_id=job.get("expert_id", 0),
            customer_id=job.get("customer_id", 0),
            device_name=data.get("device_name", ""),
            defect_text=defect,
            author_id=user_id,
            author_role=author_role,
        )

        sessions.pop(user_id, None)

        send_message(
            chat_id,
            DEVICE_LOG_ADDED + "\n\n"
            "🎫 کد: " + data.get("job_code", "") + "\n"
            "🔧 دستگاه: " + data.get("device_name", "") + "\n"
            "📝 متن: " + defect,
            kb_main()
        )

        # اطلاع به طرف مقابل
        _notify_other_side(job, user_id, data.get("device_name", ""), defect)
        return True

    return False


# ==================== نمایش لاگ‌های یه پروژه ====================
def show_logs_for_job(chat_id, user_id, job_code):
    """نمایش همه لاگ‌های یه پروژه"""
    job = find_job_by_code(job_code)
    if not job:
        send_message(chat_id, "❌ پروژه پیدا نشد.", kb_main())
        return

    # چک دسترسی
    if job.get("customer_id") != user_id and job.get("expert_id") != user_id:
        send_message(chat_id, "❌ دسترسی ندارید.", kb_main())
        return

    logs = get_device_logs(job_code)
    if not logs:
        send_message(chat_id, DEVICE_LOG_EMPTY, kb_main())
        return

    device_name = job.get("device_name") or (logs[0].get("device_name") if logs else "—")

    logs_text = ""
    for log in logs:
        logs_text += _format_log_item(log) + "\n"

    msg = DEVICE_LOG_FOR_JOB.format(
        code=job_code,
        device=device_name,
        logs=logs_text.strip()
    )
    send_message(chat_id, msg, kb_main())


# ==================== لاگ‌های من (لیست پروژه‌ها) ====================
def show_my_device_logs(chat_id, user_id, sessions):
    """نمایش لیست پروژه‌هایی که لاگ عیب دارن"""
    jobs = get_customer_jobs_with_logs(user_id, limit=10)

    if not jobs:
        send_message(chat_id, DEVICE_LOG_NO_JOBS, kb_main())
        return

    kb = {"inline_keyboard": []}
    for j in jobs:
        code = j.get("tracking_code", "?")
        device = j.get("device_name") or j.get("info", {}).get("sub", "—")
        kb["inline_keyboard"].append([
            {"text": "🎫 {} | {}".format(code, device),
             "callback_data": "devlog:show:" + code}
        ])
    kb["inline_keyboard"].append([
        {"text": BTN_BACK, "callback_data": "devlog:back"}
    ])

    send_message(
        chat_id,
        "📋 لاگ‌های شما:\n\nروی هر کد بزنید تا جزئیات رو ببینید:",
        kb
    )


# ==================== ویرایش لاگ ====================
def start_edit_log(chat_id, user_id, log_id, sessions):
    log = get_device_log(log_id)
    if not log:
        send_message(chat_id, "❌ لاگ پیدا نشد.", kb_main())
        return

    if log.get("author_id") != user_id:
        send_message(chat_id, DEVICE_LOG_ONLY_AUTHOR, kb_main())
        return

    sessions[user_id] = {
        "step": "devlog_edit",
        "data": {"log_id": log_id}
    }
    send_message(
        chat_id,
        DEVICE_LOG_EDIT_ASK + "\n\nمتن قبلی:\n«" + log.get("defect_text", "") + "»",
        kb_back()
    )


def continue_edit_log(chat_id, user_id, text, sessions):
    if user_id not in sessions:
        return False
    session = sessions[user_id]
    if session["step"] != "devlog_edit":
        return False

    if text == BTN_BACK:
        sessions.pop(user_id, None)
        send_message(chat_id, USE_MENU, kb_main())
        return True

    new_text = sanitize_text(text, 500)
    if len(new_text) < 3:
        send_message(chat_id, "❌ متن خیلی کوتاهه. دوباره وارد کنید:", kb_back())
        return True

    log_id = session["data"].get("log_id")
    if update_device_log(log_id, new_text):
        sessions.pop(user_id, None)
        send_message(chat_id, DEVICE_LOG_UPDATED, kb_main())
    else:
        sessions.pop(user_id, None)
        send_message(chat_id, "❌ خطا در ویرایش.", kb_main())
    return True


# ==================== حذف لاگ ====================
def do_delete_log(chat_id, user_id, log_id):
    log = get_device_log(log_id)
    if not log:
        send_message(chat_id, "❌ لاگ پیدا نشد.", kb_main())
        return
    if log.get("author_id") != user_id:
        send_message(chat_id, DEVICE_LOG_ONLY_AUTHOR, kb_main())
        return
    delete_device_log(log_id)
    send_message(chat_id, DEVICE_LOG_DELETED_MSG, kb_main())


# ==================== کمکی ====================
def _format_log_item(log):
    """فرمت یه لاگ"""
    author = "👤 کاربر"
    role = ""
    if log.get("author_role") == "expert":
        role = "(تعمیرکار)"
    elif log.get("author_role") == "customer":
        role = "(مشتری)"

    date_str = format_relative_time(log.get("created_at", 0))

    if log.get("is_edited"):
        return DEVICE_LOG_ITEM_EDITED.format(
            date=date_str,
            author=author,
            role=role,
            text=log.get("defect_text", ""),
            old_text=log.get("old_text", ""),
        )
    return DEVICE_LOG_ITEM_SIMPLE.format(
        date=date_str,
        author=author,
        role=role,
        text=log.get("defect_text", ""),
    )


def _notify_other_side(job, author_id, device_name, defect_text):
    """اطلاع به طرف مقابل"""
    # تعیین طرف مقابل
    if author_id == job.get("expert_id"):
        target = job.get("customer_id")
        role = "مشتری"
    else:
        target = job.get("expert_id")
        role = "تعمیرکار"

    if not target:
        return

    try:
        msg = DEVICE_LOG_NEW_NOTIFY.format(
            code=job.get("tracking_code", "?"),
            device=device_name,
            text=defect_text,
            author="طرف مقابل"
        )
        send_message(target, msg)
    except Exception as ex:
        print("Notify error:", str(ex)[:100])
