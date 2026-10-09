# ==================== مدیریت دیتابیس (SQLite) ====================
import json
import time
import database as db_sql
from config import DEFAULT_PASSWORD, FEEDBACK_ID
from utils import gen_tracking_code, gen_expert_code


# ==================== تعمیرکاران ====================
def load_experts():
    return db_sql.load_all_experts()


def save_experts(experts):
    db_sql.save_all_experts(experts)
    return True


def find_expert_by_id(user_id):
    return db_sql.get_expert(user_id)


def find_expert_by_code(code):
    for e in db_sql.load_all_experts():
        if e.get("expert_code") == code:
            return e
    return None


def add_or_update_expert(data):
    if not data.get("expert_code"):
        data["expert_code"] = gen_expert_code(data.get("name", "expert"))
    if "created_at" not in data:
        data["created_at"] = int(time.time())
    db_sql.upsert_expert(data)
    return True


def update_expert_field(user_id, field, value):
    db_sql.update_expert(user_id, field, value)
    return True


def delete_expert(user_id):
    db_sql.delete_expert_db(user_id)
    return True


def inc_referral_count(user_id):
    e = db_sql.get_expert(user_id)
    if e:
        new_count = e.get("referral_count", 0) + 1
        db_sql.update_expert(user_id, "referral_count", new_count)
    return True


# ==================== پروژه‌ها ====================
def load_jobs():
    return db_sql.load_all_jobs()


def save_jobs(jobs):
    db_sql.save_all_jobs(jobs)
    return True


def create_job(customer_id, customer_chat_id, expert, info):
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
        "rated_stages": [],
        "device_name": info.get("sub", ""),
    }
    db_sql.upsert_job(job)
    inc_referral_count(expert["user_id"])
    return code


def get_pending_job(customer_id, expert_id):
    j = db_sql.find_job(customer_id, expert_id)
    if j and j.get("sent_for_stage", 0) > j.get("stage", 0) and j.get("stage", 0) < 2:
        return j
    return None


def advance_job_stage(customer_id, expert_id):
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


def find_job_by_code(code):
    return db_sql.find_job_by_code(code)


# ==================== تنظیمات ادمین ====================
def get_user_password(user_id):
    passwords = db_sql.config_get("passwords", {})
    return passwords.get(str(user_id))


def set_user_password(user_id, password):
    passwords = db_sql.config_get("passwords", {})
    passwords[str(user_id)] = password
    db_sql.config_set("passwords", passwords)
    return True


def get_operators():
    return db_sql.config_get("operators", [])


def add_operator(user_id):
    operators = get_operators()
    if user_id not in operators:
        operators.append(user_id)
        db_sql.config_set("operators", operators)
    return True


def remove_operator(user_id):
    operators = [o for o in get_operators() if o != user_id]
    db_sql.config_set("operators", operators)
    return True


def get_feedback_id():
    return db_sql.config_get("feedback_id", FEEDBACK_ID)


def set_feedback_id(feedback_id):
    db_sql.config_set("feedback_id", feedback_id)
    return True


# ==================== تعرفه‌ها ====================
def get_tariff(category, sub_specialty):
    tariffs = db_sql.config_get("tariffs", {})
    key = "{}::{}".format(category, sub_specialty)
    return tariffs.get(key, 50000)


def set_tariff(category, sub_specialty, amount):
    tariffs = db_sql.config_get("tariffs", {})
    key = "{}::{}".format(category, sub_specialty)
    tariffs[key] = amount
    db_sql.config_set("tariffs", tariffs)
    return True


def get_all_tariffs():
    return db_sql.config_get("tariffs", {})


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


# ==================== سازگاری ====================
def load_admin_config():
    return {
        "passwords": db_sql.config_get("passwords", {}),
        "operators": db_sql.config_get("operators", []),
        "feedback_id": db_sql.config_get("feedback_id", FEEDBACK_ID),
        "tariffs": db_sql.config_get("tariffs", {}),
    }


def save_admin_config(config):
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
    e = db_sql.get_expert(user_id)
    if not e:
        return 0
    return e.get("wallet_balance", 0)


def add_to_wallet(user_id, amount):
    e = db_sql.get_expert(user_id)
    if not e:
        return False
    new_balance = e.get("wallet_balance", 0) + amount
    db_sql.update_expert(user_id, "wallet_balance", new_balance)
    return True


def subtract_from_wallet(user_id, amount):
    e = db_sql.get_expert(user_id)
    if not e:
        return False
    new_balance = max(0, e.get("wallet_balance", 0) - amount)
    db_sql.update_expert(user_id, "wallet_balance", new_balance)
    return True


def create_wallet_charge_request(user_id, amount, receipt_message_id):
    return db_sql.create_wallet_request(user_id, amount, receipt_message_id)


def approve_wallet_charge(txn_id, admin_id):
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
    return db_sql.get_expert_wallet_history(user_id, limit)


def is_expert_in_free_period(expert):
    from config import FREE_DAYS, FREE_CUSTOMERS
    created_at = expert.get("created_at", 0)
    if not created_at:
        return True
    now = int(time.time())
    days_passed = (now - created_at) / 86400
    customers_used = expert.get("referral_count", 0)
    time_done = days_passed >= FREE_DAYS
    customers_done = customers_used >= FREE_CUSTOMERS
    if time_done and customers_done:
        return False
    return True


def get_customer_history(customer_id, limit=20):
    jobs = load_jobs()
    result = [j for j in jobs if j.get("customer_id") == customer_id]
    result.sort(key=lambda x: x.get("created_at", 0), reverse=True)
    return result[:limit]


def get_expert_priority_penalty(expert):
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


# ==================== چت ====================
def create_chat(expert_id, customer_id, job_code=""):
    return db_sql.create_chat(expert_id, customer_id, job_code)


def get_chat(chat_id):
    return db_sql.get_chat(chat_id)


def get_chat_between(expert_id, customer_id):
    return db_sql.get_chat_between(expert_id, customer_id)


def update_chat(chat_id, field, value):
    return db_sql.update_chat(chat_id, field, value)


def add_message(chat_id, sender_id, sender_type, content, message_id=0, is_photo=0):
    return db_sql.add_message(chat_id, sender_id, sender_type, content, message_id, is_photo)


def get_chat_messages(chat_id, limit=20):
    return db_sql.get_chat_messages(chat_id, limit)


def reset_unread(chat_id, user_type):
    return db_sql.reset_unread(chat_id, user_type)


def get_expert_chats(expert_id, filter_type="all"):
    return db_sql.get_expert_chats(expert_id, filter_type)


def get_customer_chats(customer_id, filter_type="all"):
    return db_sql.get_customer_chats(customer_id, filter_type)


def share_phone_in_chat(chat_id):
    import time
    db_sql.update_chat(chat_id, "phone_shared", 1)
    return True


def hide_chat(chat_id, user_type):
    if user_type == "expert":
        db_sql.update_chat(chat_id, "expert_hidden", 1)
    else:
        db_sql.update_chat(chat_id, "customer_hidden", 1)
    return True


# ==================== دسته‌بندی‌ها ====================
DEFAULT_CATEGORIES = {
    "🔌 لوازم برقی": [
        "ماکروفر / مایکروویو", "توستر", "فر برقی توکار", "جاروبرقی",
        "چای‌ساز / کتری برقی", "قهوه‌ساز", "پلوپز", "سرخ‌کن / آیرفرایر",
        "سشوار", "اتو (بخارشو، پرس، ایستاده)", "ماشین لباسشویی",
        "ماشین ظرفشویی", "دستگاه تصفیه آب", "آبسردکن", "تلویزیون",
        "لامپ و پروژکتور", "انواع محافظ (یخچال، کولر، تلویزیون)",
        "تعمیر بردهای الکترونیکی", "پنکه دستی و رومیزی", "پنکه سقفی",
        "سایر لوازم برقی",
    ],
    "🔥 لوازم گازی": [
        "اجاق گاز", "آبگرمکن دیواری", "آبگرمکن زمینی", "بخاری گازی",
        "پکیج شوفاژ", "شومینه گازی", "سایر لوازم گازی",
    ],
    "❄️ سرمایشی و گرمایشی": [
        "یخچال و فریزر", "کولر آبی", "کولر گازی (اسپلیت)",
        "چیلر", "رادیاتور", "سایر سرمایشی",
    ],
    "🚗 خودرو": [
        "جلوبندی‌ساز", "تنظیم موتور", "تعمیر ترمز", "تعمیر فرمان",
        "برق خودرو", "باتری‌ساز", "آپاراتی (پنچرگیری)",
        "تعویض روغن، فیلتر و سرویس", "مکانیکی (تعمیرات موتور)",
        "گیربکس و کلاچ", "کمک‌فنر و فنر", "اگزوز", "کولر و بخاری خودرو",
        "دیاگ و عیب‌یابی", "صافکاری", "نقاشی خودرو", "سایر خدمات خودرو",
    ],
}


def get_all_categories():
    cats = db_sql.config_get("categories", None)
    if not cats:
        db_sql.config_set("categories", DEFAULT_CATEGORIES)
        return dict(DEFAULT_CATEGORIES)
    return cats


def get_category_subs(category):
    cats = get_all_categories()
    return cats.get(category, [])


def add_category_db(label):
    cats = get_all_categories()
    if label in cats:
        return False
    cats[label] = []
    db_sql.config_set("categories", cats)
    return True


def remove_category_db(label):
    cats = get_all_categories()
    if label not in cats:
        return False
    del cats[label]
    db_sql.config_set("categories", cats)
    return True


def add_sub_db(category, sub):
    cats = get_all_categories()
    if category not in cats:
        return False
    if sub in cats[category]:
        return False
    cats[category].append(sub)
    db_sql.config_set("categories", cats)
    return True


def remove_sub_db(category, sub):
    cats = get_all_categories()
    if category not in cats:
        return False
    if sub not in cats[category]:
        return False
    cats[category].remove(sub)
    db_sql.config_set("categories", cats)
    return True


def get_category_by_index(idx):
    cats = list(get_all_categories().keys())
    if 0 <= idx < len(cats):
        return cats[idx]
    return None


def get_sub_by_index(cat_label, idx):
    subs = get_category_subs(cat_label)
    if 0 <= idx < len(subs):
        return subs[idx]
    return None


# ==================== تعرفه زیرتخصص ====================
def get_sub_tariff(sub_specialty):
    from config import SUB_TARIFFS
    tariffs = db_sql.config_get("sub_tariffs", {})
    if sub_specialty in tariffs:
        return tariffs[sub_specialty]
    if sub_specialty in SUB_TARIFFS:
        return SUB_TARIFFS[sub_specialty]
    return 50000


def set_sub_tariff(sub_specialty, amount):
    tariffs = db_sql.config_get("sub_tariffs", {})
    tariffs[sub_specialty] = amount
    db_sql.config_set("sub_tariffs", tariffs)
    return True


def get_all_sub_tariffs():
    from config import SUB_TARIFFS
    user_tariffs = db_sql.config_get("sub_tariffs", {})
    result = dict(SUB_TARIFFS)
    result.update(user_tariffs)
    return result


# ==================== امتیازدهی تفکیک‌شده ====================
def add_spec_rating(expert_id, specialty, stage, criteria_key, stars):
    e = find_expert_by_id(expert_id)
    if not e:
        return False
    ratings_by_stage = e.get("ratings_by_stage", {})
    by_spec = ratings_by_stage.setdefault("by_spec", {})
    spec_data = by_spec.setdefault(specialty, {})
    stage_data = spec_data.setdefault(str(stage), {})
    cell = stage_data.setdefault(criteria_key, {"sum": 0, "count": 0})
    cell["sum"] += stars
    cell["count"] += 1
    update_expert_field(expert_id, "ratings_by_stage", ratings_by_stage)
    return True


def calc_spec_rating(expert, specialty):
    from texts import CRITERIA
    by_spec = expert.get("ratings_by_stage", {}).get("by_spec", {})
    spec_data = by_spec.get(specialty, {})
    if not spec_data:
        return None
    total = 0
    count = 0
    for cr in CRITERIA:
        rt = 0
        rc = 0
        for s in ["0", "1", "2"]:
            r = spec_data.get(s, {}).get(cr["key"], {})
            rt += r.get("sum", 0)
            rc += r.get("count", 0)
        if rc > 0:
            total += rt / rc
            count += 1
    if count == 0:
        return None
    return total / count


def get_spec_reviews_count(expert, specialty):
    from texts import CRITERIA
    by_spec = expert.get("ratings_by_stage", {}).get("by_spec", {})
    spec_data = by_spec.get(specialty, {})
    max_count = 0
    for cr in CRITERIA:
        cnt = 0
        for s in ["0", "1", "2"]:
            r = spec_data.get(s, {}).get(cr["key"], {})
            cnt += r.get("count", 0)
        max_count = max(max_count, cnt)
    return max_count


def get_all_spec_ratings(expert):
    by_spec = expert.get("ratings_by_stage", {}).get("by_spec", {})
    result = {}
    for spec in by_spec.keys():
        avg = calc_spec_rating(expert, spec)
        cnt = get_spec_reviews_count(expert, spec)
        if avg is not None and cnt > 0:
            result[spec] = {"avg": avg, "count": cnt}
    result = dict(sorted(result.items(), key=lambda x: x[1]["count"], reverse=True))
    return result


def get_spec_rating_for_search(expert, specialty, fallback_to_overall=True):
    spec_avg = calc_spec_rating(expert, specialty)
    if spec_avg is not None:
        return spec_avg
    if fallback_to_overall:
        return _calc_overall_rating(expert)
    return 5.0


def _calc_overall_rating(expert):
    from texts import CRITERIA
    total = 0
    count = 0
    for cr in CRITERIA:
        rt = 0
        rc = 0
        for s in ["0", "1", "2"]:
            r = expert.get("ratings_by_stage", {}).get(s, {}).get(cr["key"], {})
            rt += r.get("sum", 0)
            rc += r.get("count", 0)
        if rc > 0:
            total += rt / rc
            count += 1
    if count == 0:
        return 5.0
    return total / count


# ==================== نظرات متنی ====================
def add_comment(expert_id, customer_id, specialty, stage, stars, comment,
                author_name="", is_anonymous=0):
    return db_sql.add_comment(expert_id, customer_id, specialty, stage,
                              stars, comment, author_name, is_anonymous)


def get_expert_comments(expert_id, limit=20):
    return db_sql.get_expert_comments(expert_id, limit)


def get_expert_spec_comments(expert_id, specialty, limit=10):
    return db_sql.get_expert_spec_comments(expert_id, specialty, limit)


def get_comment_count(expert_id):
    return db_sql.get_comment_count(expert_id)


def has_rated(expert_id, customer_id, stage):
    return db_sql.has_rated(expert_id, customer_id, stage)


# ==================== مدیریت شهرها ====================
def get_all_cities():
    from config import IRAN_CITIES as DEFAULT
    extras = db_sql.config_get("extra_cities", [])
    removed = db_sql.config_get("removed_cities", [])

    result = list(DEFAULT)
    for c in extras:
        if c not in result:
            result.append(c)
    result = [c for c in result if c not in removed]
    return result


def add_city_db(name):
    from config import IRAN_CITIES as DEFAULT
    name = (name or "").strip()
    if not name:
        return False

    if name in DEFAULT:
        removed = db_sql.config_get("removed_cities", [])
        if name in removed:
            removed.remove(name)
            db_sql.config_set("removed_cities", removed)
            return True
        return False

    extras = db_sql.config_get("extra_cities", [])
    if name in extras:
        return False
    extras.append(name)
    db_sql.config_set("extra_cities", extras)
    return True


def remove_city_db(name):
    from config import IRAN_CITIES as DEFAULT
    name = (name or "").strip()
    if not name:
        return False

    extras = db_sql.config_get("extra_cities", [])
    if name in extras:
        extras.remove(name)
        db_sql.config_set("extra_cities", extras)
        return True

    if name in DEFAULT:
        removed = db_sql.config_get("removed_cities", [])
        if name not in removed:
            removed.append(name)
            db_sql.config_set("removed_cities", removed)
        return True

    return False


def reset_cities_db():
    db_sql.config_set("extra_cities", [])
    db_sql.config_set("removed_cities", [])
    return True


def refresh_cities_cache():
    try:
        import config
        new_list = get_all_cities()
        config.IRAN_CITIES.clear()
        config.IRAN_CITIES.extend(new_list)
        return len(new_list)
    except Exception as ex:
        print("refresh_cities_cache error:", str(ex)[:100])
        return 0


# ==================== لاگ عیوب دستگاه ====================
def add_device_log(job_code, expert_id, customer_id, device_name, defect_text,
                   author_id, author_role):
    return db_sql.add_device_log(job_code, expert_id, customer_id, device_name,
                                 defect_text, author_id, author_role)


def get_device_logs(job_code):
    return db_sql.get_device_logs(job_code)


def get_device_log(log_id):
    return db_sql.get_device_log(log_id)


def update_device_log(log_id, new_text):
    return db_sql.update_device_log(log_id, new_text)


def delete_device_log(log_id):
    return db_sql.delete_device_log(log_id)


def get_customer_jobs_with_logs(customer_id, limit=10):
    return db_sql.get_customer_jobs_with_logs(customer_id, limit)


# ==================== امنیت ====================
def log_security_event(user_id, event_type, details=""):
    return db_sql.log_security_event(user_id, event_type, details)


def get_recent_security_events(limit=50):
    return db_sql.get_recent_security_events(limit)


def is_user_blocked(user_id):
    return db_sql.is_user_blocked(user_id)


def block_user(user_id, reason, blocked_by, duration_hours=0):
    return db_sql.block_user(user_id, reason, blocked_by, duration_hours)


def unblock_user(user_id):
    return db_sql.unblock_user(user_id)


def get_blocked_users():
    return db_sql.get_blocked_users()


def get_login_attempts(user_id):
    return db_sql.get_login_attempts(user_id)


def record_login_attempt(user_id, success):
    return db_sql.record_login_attempt(user_id, success)


def is_login_locked(user_id):
    return db_sql.is_login_locked(user_id)


def reset_login_attempts(user_id):
    return db_sql.reset_login_attempts(user_id)


# ==================== نگهداری ====================
def cleanup_old_data(days=180):
    """پاکسازی داده‌های قدیمی‌تر از N روز"""
    cutoff = int(time.time()) - (days * 86400)

    jobs_deleted = db_sql.delete_old_jobs(cutoff)
    comments_deleted = db_sql.delete_old_comments(cutoff)
    logs_deleted = db_sql.delete_old_device_logs(cutoff)
    txns_deleted = db_sql.delete_old_wallet_transactions(cutoff)
    events_deleted = db_sql.cleanup_old_security_events(days=30)

    return {
        "jobs": jobs_deleted,
        "comments": comments_deleted,
        "logs": logs_deleted,
        "txns": txns_deleted,
        "events": events_deleted,
    }
