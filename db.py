# ==================== مدیریت دیتابیس (SQLite) ====================
# این فایل API قبلی رو نگه داشته، ولی از SQLite استفاده می‌کنه
import json
import time
import database as db_sql
from config import DEFAULT_PASSWORD, FEEDBACK_ID
from utils import gen_tracking_code, gen_expert_code


# ==================== تعمیرکاران ====================
def load_experts():
    """خوندن همه تعمیرکاران"""
    return db_sql.load_all_experts()


def save_experts(experts):
    """ذخیره همه تعمیرکاران"""
    db_sql.save_all_experts(experts)
    return True


def find_expert_by_id(user_id):
    """پیدا کردن تعمیرکار با user_id"""
    return db_sql.get_expert(user_id)


def find_expert_by_code(code):
    """پیدا کردن تعمیرکار با کد اختصاصی"""
    for e in db_sql.load_all_experts():
        if e.get("expert_code") == code:
            return e
    return None


def add_or_update_expert(data):
    """اضافه یا آپدیت تعمیرکار"""
    if not data.get("expert_code"):
        data["expert_code"] = gen_expert_code(data.get("name", "expert"))
    if "created_at" not in data:
        data["created_at"] = int(time.time())
    db_sql.upsert_expert(data)
    return True


def update_expert_field(user_id, field, value):
    """آپدیت یه فیلد"""
    db_sql.update_expert(user_id, field, value)
    return True


def delete_expert(user_id):
    """حذف تعمیرکار"""
    db_sql.delete_expert_db(user_id)
    return True


def inc_referral_count(user_id):
    """اضافه کردن تعداد معرفی"""
    e = db_sql.get_expert(user_id)
    if e:
        new_count = e.get("referral_count", 0) + 1
        db_sql.update_expert(user_id, "referral_count", new_count)
    return True


# ==================== پروژه‌ها ====================
def load_jobs():
    """خوندن همه پروژه‌ها"""
    return db_sql.load_all_jobs()


def save_jobs(jobs):
    """ذخیره همه پروژه‌ها"""
    db_sql.save_all_jobs(jobs)
    return True


def create_job(customer_id, customer_chat_id, expert, info):
    """ساخت پروژه جدید"""
    jobs = load_jobs()
    code = gen_tracking_code()
    while any(j.get("tracking_code") == code for j in jobs):
        code = gen_tracking_code()
    
    now = int(time.time())
    job = {
        "id": "{}_{}".format(customer_id, now),
        "tracking_code": code,
        "customer_id": customer_id,
        "customer_chat_id": customer_chat_id,
        "expert_id": expert["user_id"],
        "expert_name": expert.get("name", "?"),
        "created_at": now,
        "stage": 0,
        "next_at": now + (30 * 86400),
        "sent_for_stage": 0,
        "info": info,
    }
    db_sql.upsert_job(job)
    inc_referral_count(expert["user_id"])
    return code


def get_pending_job(customer_id, expert_id):
    """گرفتن پروژه در انتظار نظرسنجی"""
    j = db_sql.find_job(customer_id, expert_id)
    if j and j.get("sent_for_stage", 0) > j.get("stage", 0) and j.get("stage", 0) < 2:
        return j
    return None


def advance_job_stage(customer_id, expert_id):
    """جلو بردن مرحله نظرسنجی"""
    j = db_sql.find_job(customer_id, expert_id)
    if not j:
        return
    if j.get("sent_for_stage", 0) > j.get("stage", 0):
        new_stage = j.get("stage", 0) + 1
        db_sql.update_job(j["id"], "stage", new_stage)
        if new_stage == 1:
            db_sql.update_job(j["id"], "next_at", int(time.time()) + (150 * 86400))
        else:
            db_sql.update_job(j["id"], "next_at", 0)


def update_job_field(job_id, field, value):
    db_sql.update_job(job_id, field, value)
    return True


# ==================== تنظیمات ادمین ====================
def get_user_password(user_id):
    """گرفتن رمز عبور کاربر"""
    passwords = db_sql.config_get("passwords", {})
    return passwords.get(str(user_id))


def set_user_password(user_id, password):
    """ذخیره رمز عبور"""
    passwords = db_sql.config_get("passwords", {})
    passwords[str(user_id)] = password
    db_sql.config_set("passwords", passwords)
    return True


def get_operators():
    """گرفتن لیست مدیران"""
    return db_sql.config_get("operators", [])


def add_operator(user_id):
    """اضافه کردن مدیر"""
    operators = get_operators()
    if user_id not in operators:
        operators.append(user_id)
        db_sql.config_set("operators", operators)
    return True


def remove_operator(user_id):
    """حذف مدیر"""
    operators = [o for o in get_operators() if o != user_id]
    db_sql.config_set("operators", operators)
    return True


def get_feedback_id():
    """گرفتن آیدی نظرات"""
    return db_sql.config_get("feedback_id", FEEDBACK_ID)


def set_feedback_id(feedback_id):
    db_sql.config_set("feedback_id", feedback_id)
    return True


# ==================== تعرفه‌ها ====================
def get_tariff(category, sub_specialty):
    """گرفتن تعرفه یه تخصص"""
    tariffs = db_sql.config_get("tariffs", {})
    key = "{}::{}".format(category, sub_specialty)
    return tariffs.get(key, 50000)


def set_tariff(category, sub_specialty, amount):
    """ذخیره تعرفه"""
    tariffs = db_sql.config_get("tariffs", {})
    key = "{}::{}".format(category, sub_specialty)
    tariffs[key] = amount
    db_sql.config_set("tariffs", tariffs)
    return True


def get_all_tariffs():
    return db_sql.config_get("tariffs", {})


# ==================== کاربران (برای تلگرام) ====================
def load_users():
    """خوندن همه کاربران (سازگاری با کد قبلی)"""
    return {}


def save_users(users):
    return True


def get_user_link(bale_user_id=None, telegram_user_id=None):
    if bale_user_id:
        return db_sql.users_get("bale_{}".format(bale_user_id))
    if telegram_user_id:
        return db_sql.users_get("tg_{}".format(telegram_user_id))
    return None


def link_users(bale_user_id, telegram_user_id):
    db_sql.users_set("bale_{}".format(bale_user_id), {"telegram_id": telegram_user_id, "linked_at": int(time.time())})
    db_sql.users_set("tg_{}".format(telegram_user_id), {"bale_id": bale_user_id, "linked_at": int(time.time())})
    return True


# ==================== گزارشات ====================
def load_reports():
    return []


def save_reports(reports):
    return True


def create_report(reporter_id, reporter_messenger, target_id, target_type, reason, description=""):
    return 1


def update_report_status(report_id, status):
    return True


# ==================== آمار ====================
def get_stats():
    experts = load_experts()
    jobs = load_jobs()
    return {
        "total_experts": len(experts),
        "approved_experts": sum(1 for e in experts if e.get("status", "approved") == "approved"),
        "pending_experts": sum(1 for e in experts if e.get("status") == "pending"),
        "active_experts": sum(1 for e in experts if e.get("active", True)),
        "premium_experts": sum(1 for e in experts if e.get("is_premium")),
        "total_referrals": sum(e.get("referral_count", 0) for e in experts),
        "total_jobs": len(jobs),
        "unique_customers": len(set(j.get("customer_id") for j in jobs)),
        "pending_reports": 0,
    }


def is_shop_open(expert):
    """بررسی باز بودن مغازه"""
    if not expert.get("active", True):
        return False
    status = expert.get("shop_status", "active")
    if status == "active":
        return True
    if status == "closed_perm":
        return False
    if status == "closed_temp":
        now = time.time()
        closed_from = expert.get("closed_from", 0)
        closed_until = expert.get("closed_until", 0)
        if closed_from > 0 and closed_from > now:
            return True
        if closed_until > 0 and closed_until <= now:
            return True
        return False
    return True


# ==================== سازگاری با کد قبلی ====================
def load_admin_config():
    """برای سازگاری"""
    return {
        "passwords": db_sql.config_get("passwords", {}),
        "operators": db_sql.config_get("operators", []),
        "feedback_id": db_sql.config_get("feedback_id", FEEDBACK_ID),
        "tariffs": db_sql.config_get("tariffs", {}),
    }


def save_admin_config(config):
    """برای سازگاری"""
    if "passwords" in config:
        db_sql.config_set("passwords", config["passwords"])
    if "operators" in config:
        db_sql.config_set("operators", config["operators"])
    if "feedback_id" in config:
        db_sql.config_set("feedback_id", config["feedback_id"])
    if "tariffs" in config:
        db_sql.config_set("tariffs", config["tariffs"])
    return True



# ==================== کیف پول ====================
def get_wallet_balance(user_id):
    """گرفتن موجودی کیف پول"""
    e = db_sql.get_expert(user_id)
    if not e:
        return 0
    return e.get("wallet_balance", 0)


def add_to_wallet(user_id, amount):
    """اضافه کردن به کیف پول"""
    e = db_sql.get_expert(user_id)
    if not e:
        return False
    new_balance = e.get("wallet_balance", 0) + amount
    db_sql.update_expert(user_id, "wallet_balance", new_balance)
    return True


def subtract_from_wallet(user_id, amount):
    """کم کردن از کیف پول"""
    e = db_sql.get_expert(user_id)
    if not e:
        return False
    new_balance = max(0, e.get("wallet_balance", 0) - amount)
    db_sql.update_expert(user_id, "wallet_balance", new_balance)
    return True


def create_wallet_charge_request(user_id, amount, receipt_message_id):
    """ساخت درخواست شارژ"""
    return db_sql.create_wallet_request(user_id, amount, receipt_message_id)


def approve_wallet_charge(txn_id, admin_id):
    """تأیید شارژ کیف پول"""
    import time
    txn = db_sql.get_wallet_transaction(txn_id)
    if not txn or txn.get("status") != "pending":
        return None
    db_sql.update_wallet_transaction(txn_id, "status", "approved")
    db_sql.update_wallet_transaction(txn_id, "reviewed_at", int(time.time()))
    db_sql.update_wallet_transaction(txn_id, "reviewed_by", admin_id)
    add_to_wallet(txn["expert_id"], txn["amount"])
    return txn


def reject_wallet_charge(txn_id, admin_id, reason=""):
    """رد شارژ کیف پول"""
    import time
    txn = db_sql.get_wallet_transaction(txn_id)
    if not txn or txn.get("status") != "pending":
        return None
    db_sql.update_wallet_transaction(txn_id, "status", "rejected")
    db_sql.update_wallet_transaction(txn_id, "reviewed_at", int(time.time()))
    db_sql.update_wallet_transaction(txn_id, "reviewed_by", admin_id)
    db_sql.update_wallet_transaction(txn_id, "reject_reason", reason)
    return txn


def get_expert_wallet_history(user_id, limit=10):
    """تاریخچه تراکنش‌ها"""
    return db_sql.get_expert_wallet_history(user_id, limit)


def is_expert_in_free_period(expert):
    """آیا تعمیرکار توی ۲ ماه اول هست؟"""
    from config import FREE_DAYS
    created_at = expert.get("created_at", 0)
    if not created_at:
        return True
    now = int(time.time())
    free_until = created_at + (FREE_DAYS * 86400)
    return now < free_until


def get_expert_priority_penalty(expert):
    """امتیاز منفی اگه بعد از ۲ ماه شارژ نداره"""
    from config import TARIFFS
    if is_expert_in_free_period(expert):
        return 0
    balance = expert.get("wallet_balance", 0)
    if balance <= 0:
        return -100
    category = expert.get("category", "")
    tariff = TARIFFS.get(category, 50000)
    if balance < tariff:
        return -30
    return 0
