# ==================== لایه دیتابیس SQLite ====================
import sqlite3
import json
import threading
from config import SQLITE_FILE, DB_FILE, JOBS_FILE, CONFIG_FILE, USERS_FILE

_lock = threading.Lock()


def get_conn():
    conn = sqlite3.connect(SQLITE_FILE, check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """ساخت جدول‌ها (اگه وجود نداشته باشن)"""
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        
        # جدول تعمیرکاران
        c.execute("""
            CREATE TABLE IF NOT EXISTS experts (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                phone TEXT,
                city TEXT,
                area TEXT,
                category TEXT,
                sub_specialties TEXT,
                works_on_site INTEGER DEFAULT 0,
                response_speed INTEGER DEFAULT 0,
                repair_time INTEGER DEFAULT 0,
                lat REAL,
                lng REAL,
                active INTEGER DEFAULT 1,
                is_premium INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                shop_status TEXT DEFAULT 'active',
                closed_from INTEGER DEFAULT 0,
                closed_until INTEGER DEFAULT 0,
                close_reason TEXT DEFAULT '',
                expert_code TEXT UNIQUE,
                referral_count INTEGER DEFAULT 0,
                ratings_by_stage TEXT DEFAULT '{}',
                wallet_balance INTEGER DEFAULT 0,
                free_customers_used INTEGER DEFAULT 0,
                created_at INTEGER DEFAULT 0
            )
        """)
        
        # جدول پروژه‌ها
        c.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                tracking_code TEXT UNIQUE,
                customer_id INTEGER,
                customer_chat_id INTEGER,
                expert_id INTEGER,
                expert_name TEXT,
                created_at INTEGER,
                next_at INTEGER,
                stage INTEGER DEFAULT 0,
                sent_for_stage INTEGER DEFAULT 0,
                info TEXT DEFAULT '{}'
            )
        """)
        
        # جدول تنظیمات (key-value)
        c.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # جدول کاربران (برای اتصال بله-تلگرام)
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        conn.commit()
        conn.close()


# ==================== تعمیرکاران ====================
def _row_to_expert(row):
    """تبدیل ردیف دیتابیس به دیکشنری"""
    d = dict(row)
    d["sub_specialties"] = json.loads(d.get("sub_specialties") or "[]")
    d["ratings_by_stage"] = json.loads(d.get("ratings_by_stage") or "{}")
    d["works_on_site"] = bool(d.get("works_on_site"))
    d["active"] = bool(d.get("active"))
    d["is_premium"] = bool(d.get("is_premium"))
    return d


def load_all_experts():
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM experts")
        rows = c.fetchall()
        conn.close()
        return [_row_to_expert(r) for r in rows]


def save_all_experts(experts):
    """جایگزینی کامل همه تعمیرکاران (برای سازگاری)"""
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM experts")
        for e in experts:
            _insert_expert(c, e)
        conn.commit()
        conn.close()


def _insert_expert(c, e):
    """درج یه تعمیرکار"""
    c.execute("""
        INSERT OR REPLACE INTO experts (
            user_id, name, phone, city, area, category, sub_specialties,
            works_on_site, response_speed, repair_time, lat, lng,
            active, is_premium, status, shop_status, closed_from,
            closed_until, close_reason, expert_code, referral_count,
            ratings_by_stage, wallet_balance, free_customers_used, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        e.get("user_id"),
        e.get("name", ""),
        e.get("phone", ""),
        e.get("city", ""),
        e.get("area", ""),
        e.get("category", ""),
        json.dumps(e.get("sub_specialties", []), ensure_ascii=False),
        1 if e.get("works_on_site") else 0,
        int(e.get("response_speed", 0)),
        int(e.get("repair_time", 0)),
        e.get("lat"),
        e.get("lng"),
        1 if e.get("active", True) else 0,
        1 if e.get("is_premium") else 0,
        e.get("status", "pending"),
        e.get("shop_status", "active"),
        int(e.get("closed_from", 0)),
        int(e.get("closed_until", 0)),
        e.get("close_reason", ""),
        e.get("expert_code", ""),
        int(e.get("referral_count", 0)),
        json.dumps(e.get("ratings_by_stage", {}), ensure_ascii=False),
        int(e.get("wallet_balance", 0)),
        int(e.get("free_customers_used", 0)),
        int(e.get("created_at", 0)),
    ))


def upsert_expert(e):
    """درج یا آپدیت یه تعمیرکار"""
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        _insert_expert(c, e)
        conn.commit()
        conn.close()


def get_expert(user_id):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM experts WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        return _row_to_expert(row) if row else None


def update_expert(user_id, field, value):
    """آپدیت یه فیلد از تعمیرکار"""
    # فیلدهای خاص
    if field in ["sub_specialties", "ratings_by_stage"]:
        value = json.dumps(value, ensure_ascii=False)
    elif field in ["works_on_site", "active", "is_premium"]:
        value = 1 if value else 0
    
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("UPDATE experts SET {} = ? WHERE user_id = ?".format(field), (value, user_id))
        conn.commit()
        conn.close()


def delete_expert_db(user_id):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM experts WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()


# ==================== پروژه‌ها ====================
def _row_to_job(row):
    d = dict(row)
    d["info"] = json.loads(d.get("info") or "{}")
    return d


def load_all_jobs():
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM jobs ORDER BY created_at")
        rows = c.fetchall()
        conn.close()
        return [_row_to_job(r) for r in rows]


def save_all_jobs(jobs):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM jobs")
        for j in jobs:
            _insert_job(c, j)
        conn.commit()
        conn.close()


def _insert_job(c, j):
    c.execute("""
        INSERT OR REPLACE INTO jobs (
            id, tracking_code, customer_id, customer_chat_id,
            expert_id, expert_name, created_at, next_at,
            stage, sent_for_stage, info
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        j.get("id", ""),
        j.get("tracking_code", ""),
        j.get("customer_id"),
        j.get("customer_chat_id"),
        j.get("expert_id"),
        j.get("expert_name", ""),
        int(j.get("created_at", 0)),
        int(j.get("next_at", 0)),
        int(j.get("stage", 0)),
        int(j.get("sent_for_stage", 0)),
        json.dumps(j.get("info", {}), ensure_ascii=False),
    ))


def upsert_job(j):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        _insert_job(c, j)
        conn.commit()
        conn.close()


def update_job(job_id, field, value):
    if field == "info":
        value = json.dumps(value, ensure_ascii=False)
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("UPDATE jobs SET {} = ? WHERE id = ?".format(field), (value, job_id))
        conn.commit()
        conn.close()


def find_job(customer_id, expert_id):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM jobs WHERE customer_id = ? AND expert_id = ? ORDER BY created_at DESC", (customer_id, expert_id))
        row = c.fetchone()
        conn.close()
        return _row_to_job(row) if row else None


# ==================== تنظیمات ====================
def config_get(key, default=None):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT value FROM config WHERE key = ?", (key,))
        row = c.fetchone()
        conn.close()
        if row:
            try:
                return json.loads(row["value"])
            except:
                return row["value"]
        return default


def config_set(key, value):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value, ensure_ascii=False)
        elif isinstance(value, bool):
            value_str = json.dumps(value)
        elif value is None:
            value_str = "null"
        else:
            value_str = json.dumps(value, ensure_ascii=False)
        c.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, value_str))
        conn.commit()
        conn.close()


# ==================== کاربران (برای تلگرام) ====================
def users_get(key):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT value FROM users WHERE key = ?", (key,))
        row = c.fetchone()
        conn.close()
        if row:
            try:
                return json.loads(row["value"])
            except:
                return None
        return None


def users_set(key, value):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO users (key, value) VALUES (?, ?)", (key, json.dumps(value, ensure_ascii=False)))
        conn.commit()
        conn.close()


# ==================== مهاجرت از JSON ====================
def migrate_from_json():
    """مهاجرت از فایل‌های JSON قدیمی به SQLite (فقط یه بار)"""
    import os
    
    experts_migrated = False
    jobs_migrated = False
    
    # چک کن دیتابیس خالی هست
    existing_experts = load_all_experts()
    if existing_experts:
        return  # قبلاً مهاجرت شده
    
    # مهاجرت تعمیرکاران
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                experts = json.load(f)
                if experts:
                    save_all_experts(experts)
                    experts_migrated = True
                    print("Migrated {} experts from JSON".format(len(experts)))
        except Exception as e:
            print("Expert migration error:", str(e)[:100])
    
    # مهاجرت پروژه‌ها
    if os.path.exists(JOBS_FILE):
        try:
            with open(JOBS_FILE, "r", encoding="utf-8") as f:
                jobs = json.load(f)
                if jobs:
                    save_all_jobs(jobs)
                    jobs_migrated = True
                    print("Migrated {} jobs from JSON".format(len(jobs)))
        except Exception as e:
            print("Job migration error:", str(e)[:100])
    
    # مهاجرت تنظیمات
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                if cfg.get("passwords"):
                    config_set("passwords", cfg["passwords"])
                if cfg.get("operators"):
                    config_set("operators", cfg["operators"])
                if cfg.get("feedback_id"):
                    config_set("feedback_id", cfg["feedback_id"])
                if cfg.get("tariffs"):
                    config_set("tariffs", cfg["tariffs"])
                print("Migrated config from JSON")
        except Exception as e:
            print("Config migration error:", str(e)[:100])
