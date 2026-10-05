# ==================== مدیریت دیتابیس ====================
import json
import time
from config import (
    DB_FILE, JOBS_FILE, CONFIG_FILE, USERS_FILE, REPORTS_FILE,
    DEFAULT_PASSWORD, FEEDBACK_ID, FREE_CUSTOMERS
)
from utils import gen_tracking_code, gen_expert_code


# ==================== توابع پایه ====================
def load_json(file_path, default=None):
    """خوندن فایل JSON"""
    if default is None:
        default = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default


def save_json(file_path, data):
    """ذخیره در فایل JSON"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print("Error saving {}: {}".format(file_path, str(e)[:100]))
        return False


# ==================== تعمیرکاران ====================
def load_experts():
    return load_json(DB_FILE, [])


def save_experts(experts):
    return save_json(DB_FILE, experts)


def find_expert_by_id(user_id):
    for e in load_experts():
        if e.get("user_id") == user_id:
            return e
    return None


def find_expert_by_code(code):
    for e in load_experts():
        if e.get("expert_code") == code:
            return e
    return None


def add_or_update_expert(data):
    experts = load_experts()
    experts = [e for e in experts if e.get("user_id") != data["user_id"]]
    experts.append(data)
    return save_experts(experts)


def update_expert_field(user_id, field, value):
    experts = load_experts()
    for e in experts:
        if e.get("user_id") == user_id:
            e[field] = value
            break
    return save_experts(experts)


def delete_expert(user_id):
    experts = [e for e in load_experts() if e.get("user_id") != user_id]
    return save_experts(experts)


def inc_referral_count(user_id):
    experts = load_experts()
    for e in experts:
        if e.get("user_id") == user_id:
            e["referral_count"] = e.get("referral_count", 0) + 1
            break
    return save_experts(experts)


# ==================== پروژه‌ها (معرفی‌ها) ====================
def load_jobs():
    return load_json(JOBS_FILE, [])


def save_jobs(jobs):
    return save_json(JOBS_FILE, jobs)


def create_job(customer_id, customer_chat_id, expert, info):
    jobs = load_jobs()
    code = gen_tracking_code()
    # اطمینان از یکتا بودن کد
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
    jobs.append(job)
    save_jobs(jobs)
    inc_referral_count(expert["user_id"])
    return code


def get_pending_job(customer_id, expert_id):
    for j in load_jobs():
        if j.get("customer_id") == customer_id and j.get("expert_id") == expert_id:
            if j.get("sent_for_stage", 0) > j.get("stage", 0) and j.get("stage", 0) < 2:
                return j
    return None


def advance_job_stage(customer_id, expert_id):
    jobs = load_jobs()
    now = int(time.time())
    for j in jobs:
        if j.get("customer_id") == customer_id and j.get("expert_id") == expert_id:
            if j.get("sent_for_stage", 0) > j.get("stage", 0):
                new_stage = j.get("stage", 0) + 1
                j["stage"] = new_stage
                if new_stage == 1:
                    j["next_at"] = now + (150 * 86400)
                else:
                    j["next_at"] = 0
                break
    save_jobs(jobs)


# ==================== تنظیمات ادمین ====================
def load_admin_config():
    default = {
        "passwords": {},
        "operators": [],
        "feedback_id": FEEDBACK_ID,
        "tariffs": {},
    }
    return load_json(CONFIG_FILE, default)


def save_admin_config(config):
    return save_json(CONFIG_FILE, config)


def get_user_password(user_id):
    config = load_admin_config()
    return config.get("passwords", {}).get(str(user_id))


def set_user_password(user_id, password):
    config = load_admin_config()
    if "passwords" not in config:
        config["passwords"] = {}
    config["passwords"][str(user_id)] = password
    return save_admin_config(config)


def get_operators():
    config = load_admin_config()
    return config.get("operators", [])


def add_operator(user_id):
    config = load_admin_config()
    operators = config.get("operators", [])
    if user_id not in operators:
        operators.append(user_id)
        config["operators"] = operators
        save_admin_config(config)


def remove_operator(user_id):
    config = load_admin_config()
    config["operators"] = [o for o in config.get("operators", []) if o != user_id]
    save_admin_config(config)


def get_feedback_id():
    config = load_admin_config()
    return config.get("feedback_id", FEEDBACK_ID)


def set_feedback_id(feedback_id):
    config = load_admin_config()
    config["feedback_id"] = feedback_id
    return save_admin_config(config)


# ==================== تعرفه‌ها ====================
def get_tariff(category, sub_specialty):
    """گرفتن تعرفه برای یه تخصص خاص"""
    config = load_admin_config()
    tariffs = config.get("tariffs", {})
    key = "{}::{}".format(category, sub_specialty)
    return tariffs.get(key, 50000)  # پیش‌فرض 50,000


def set_tariff(category, sub_specialty, amount):
    config = load_admin_config()
    if "tariffs" not in config:
        config["tariffs"] = {}
    key = "{}::{}".format(category, sub_specialty)
    config["tariffs"][key] = amount
    return save_admin_config(config)


def get_all_tariffs():
    config = load_admin_config()
    return config.get("tariffs", {})


# ==================== کاربران (برای تلگرام) ====================
def load_users():
    return load_json(USERS_FILE, {})


def save_users(users):
    return save_json(USERS_FILE, users)


def get_user_link(bale_user_id=None, telegram_user_id=None):
    """گرفتن اطلاعات اتصال بین پیام‌رسان‌ها"""
    users = load_users()
    if bale_user_id:
        key = "bale_{}".format(bale_user_id)
        return users.get(key)
    if telegram_user_id:
        key = "tg_{}".format(telegram_user_id)
        return users.get(key)
    return None


def link_users(bale_user_id, telegram_user_id):
    """اتصال حساب بله و تلگرام"""
    users = load_users()
    users["bale_{}".format(bale_user_id)] = {
        "telegram_id": telegram_user_id,
        "linked_at": int(time.time()),
    }
    users["tg_{}".format(telegram_user_id)] = {
        "bale_id": bale_user_id,
        "linked_at": int(time.time()),
    }
    return save_users(users)


# ==================== گزارشات ====================
def load_reports():
    return load_json(REPORTS_FILE, [])


def save_reports(reports):
    return save_json(REPORTS_FILE, reports)


def create_report(reporter_id, reporter_messenger, target_id, target_type, reason, description=""):
    reports = load_reports()
    report = {
        "id": len(reports) + 1,
        "reporter_id": reporter_id,
        "reporter_messenger": reporter_messenger,
        "target_id": target_id,
        "target_type": target_type,  # "expert" یا "customer"
        "reason": reason,
        "description": description,
        "status": "pending",
        "created_at": int(time.time()),
    }
    reports.append(report)
    save_reports(reports)
    return report["id"]


def update_report_status(report_id, status):
    reports = load_reports()
    for r in reports:
        if r.get("id") == report_id:
            r["status"] = status
            r["reviewed_at"] = int(time.time())
            break
    return save_reports(reports)


# ==================== آمار ====================
def get_stats():
    experts = load_experts()
    jobs = load_jobs()
    reports = load_reports()
    
    return {
        "total_experts": len(experts),
        "approved_experts": sum(1 for e in experts if e.get("status", "approved") == "approved"),
        "pending_experts": sum(1 for e in experts if e.get("status") == "pending"),
        "active_experts": sum(1 for e in experts if e.get("active", True)),
        "premium_experts": sum(1 for e in experts if e.get("is_premium")),
        "total_referrals": sum(e.get("referral_count", 0) for e in experts),
        "total_jobs": len(jobs),
        "unique_customers": len(set(j.get("customer_id") for j in jobs)),
        "pending_reports": sum(1 for r in reports if r.get("status") == "pending"),
    }


def is_shop_open(expert):
    """بررسی باز بودن مغازه - با چک کردن زمان شروع و پایان تعطیلی"""
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
        # اگه هنوز تعطیلی شروع نشده → مغازه بازه
        if closed_from > 0 and closed_from > now:
            return True
        # اگه تعطیلی تموم شده → مغازه بازه
        if closed_until > 0 and closed_until <= now:
            return True
        # در غیر این صورت → بسته
        return False
    return True
