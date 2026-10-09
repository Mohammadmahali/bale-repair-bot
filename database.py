# ==================== لایه دیتابیس SQLite ====================
import sqlite3
import json
import threading
from config import SQLITE_FILE, DB_FILE, JOBS_FILE, CONFIG_FILE

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
                info TEXT DEFAULT '{}',
                rated_stages TEXT DEFAULT '[]',
                device_name TEXT DEFAULT ''
            )
        """)

        # جدول تنظیمات
        c.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        # جدول تراکنش‌های کیف پول
        c.execute("""
            CREATE TABLE IF NOT EXISTS wallet_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expert_id INTEGER,
                amount INTEGER,
                type TEXT,
                status TEXT DEFAULT 'pending',
                receipt_message_id INTEGER,
                created_at INTEGER,
                reviewed_at INTEGER,
                reviewed_by INTEGER,
                reject_reason TEXT DEFAULT ''
            )
        """)

        # جدول چت‌ها
        c.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expert_id INTEGER,
                customer_id INTEGER,
                job_code TEXT DEFAULT '',
                status TEXT DEFAULT 'active',
                created_at INTEGER,
                last_message_at INTEGER,
                expert_hidden INTEGER DEFAULT 0,
                customer_hidden INTEGER DEFAULT 0,
                phone_shared INTEGER DEFAULT 0,
                expert_unread INTEGER DEFAULT 0,
                customer_unread INTEGER DEFAULT 0
            )
        """)

        # جدول پیام‌ها
        c.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                sender_id INTEGER,
                sender_type TEXT,
                content TEXT,
                message_id INTEGER,
                is_photo INTEGER DEFAULT 0,
                created_at INTEGER
            )
        """)

        # جدول نظرات متنی
        c.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expert_id INTEGER,
                customer_id INTEGER,
                specialty TEXT DEFAULT '',
                stage INTEGER DEFAULT 0,
                stars REAL DEFAULT 0,
                comment TEXT DEFAULT '',
                author_name TEXT DEFAULT '',
                is_anonymous INTEGER DEFAULT 0,
                created_at INTEGER DEFAULT 0
            )
        """)

        # جدول لاگ عیوب دستگاه
        c.execute("""
            CREATE TABLE IF NOT EXISTS device_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_code TEXT,
                expert_id INTEGER,
                customer_id INTEGER,
                device_name TEXT DEFAULT '',
                defect_text TEXT DEFAULT '',
                author_id INTEGER,
                author_role TEXT,
                created_at INTEGER,
                updated_at INTEGER DEFAULT 0,
                is_edited INTEGER DEFAULT 0,
                old_text TEXT DEFAULT ''
            )
        """)

        # جدول رویدادهای امنیتی
        c.execute("""
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                event_type TEXT,
                details TEXT DEFAULT '',
                created_at INTEGER
            )
        """)

        # جدول کاربران مسدود
        c.execute("""
            CREATE TABLE IF NOT EXISTS blocked_users (
                user_id INTEGER PRIMARY KEY,
                reason TEXT DEFAULT '',
                blocked_by INTEGER,
                blocked_at INTEGER,
                blocked_until INTEGER DEFAULT 0
            )
        """)

        # جدول تلاش‌های ورود ادمین
        c.execute("""
            CREATE TABLE IF NOT EXISTS admin_login_attempts (
                user_id INTEGER PRIMARY KEY,
                attempts INTEGER DEFAULT 0,
                last_attempt INTEGER,
                locked_until INTEGER DEFAULT 0
            )
        """)

        # ===== Migration: اضافه کردن ستون‌های جدید (اگه نبودن) =====
        try:
            c.execute("SELECT rated_stages FROM jobs LIMIT 1")
        except:
            try:
                c.execute("ALTER TABLE jobs ADD COLUMN rated_stages TEXT DEFAULT '[]'")
                print("Migration: added rated_stages to jobs")
            except Exception as e:
                print("Migration rated_stages error:", str(e)[:100])

        try:
            c.execute("SELECT device_name FROM jobs LIMIT 1")
        except:
            try:
                c.execute("ALTER TABLE jobs ADD COLUMN device_name TEXT DEFAULT ''")
                print("Migration: added device_name to jobs")
            except Exception as e:
                print("Migration device_name error:", str(e)[:100])

        conn.commit()
        conn.close()


# ==================== تعمیرکاران ====================
def _row_to_expert(row):
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
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM experts")
        for e in experts:
            _insert_expert(c, e)
        conn.commit()
        conn.close()


def _insert_expert(c, e):
    c.execute("""
        INSERT OR REPLACE INTO experts (
            user_id, name, phone, city, area, category, sub_specialties,
            works_on_site, response_speed, repair_time, lat, lng,
            active, is_premium, status, shop_status, closed_from,
            closed_until, close_reason, expert_code, referral_count,
            ratings_by_stage, wallet_balance, free_customers_used, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        e.get("user_id"), e.get("name", ""), e.get("phone", ""),
        e.get("city", ""), e.get("area", ""), e.get("category", ""),
        json.dumps(e.get("sub_specialties", []), ensure_ascii=False),
        1 if e.get("works_on_site") else 0,
        int(e.get("response_speed", 0)), int(e.get("repair_time", 0)),
        e.get("lat"), e.get("lng"),
        1 if e.get("active", True) else 0,
        1 if e.get("is_premium") else 0,
        e.get("status", "pending"), e.get("shop_status", "active"),
        int(e.get("closed_from", 0)), int(e.get("closed_until", 0)),
        e.get("close_reason", ""), e.get("expert_code", ""),
        int(e.get("referral_count", 0)),
        json.dumps(e.get("ratings_by_stage", {}), ensure_ascii=False),
        int(e.get("wallet_balance", 0)), int(e.get("free_customers_used", 0)),
        int(e.get("created_at", 0)),
    ))


def upsert_expert(e):
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
    d["rated_stages"] = json.loads(d.get("rated_stages") or "[]")
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
            stage, sent_for_stage, info, rated_stages, device_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        j.get("id", ""), j.get("tracking_code", ""),
        j.get("customer_id"), j.get("customer_chat_id"),
        j.get("expert_id"), j.get("expert_name", ""),
        int(j.get("created_at", 0)), int(j.get("next_at", 0)),
        int(j.get("stage", 0)), int(j.get("sent_for_stage", 0)),
        json.dumps(j.get("info", {}), ensure_ascii=False),
        json.dumps(j.get("rated_stages", []), ensure_ascii=False),
        j.get("device_name", ""),
    ))


def upsert_job(j):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        _insert_job(c, j)
        conn.commit()
        conn.close()


def update_job(job_id, field, value):
    if field in ["info", "rated_stages"]:
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


def find_job_by_code(tracking_code):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM jobs WHERE tracking_code = ?", (tracking_code,))
        row = c.fetchone()
        conn.close()
        return _row_to_job(row) if row else None


def delete_old_jobs(cutoff_timestamp):
    """حذف پروژه‌های قدیمی‌تر از cutoff"""
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) as cnt FROM jobs WHERE created_at < ?", (cutoff_timestamp,))
        row = c.fetchone()
        count = row["cnt"] if row else 0
        c.execute("DELETE FROM jobs WHERE created_at < ?", (cutoff_timestamp,))
        conn.commit()
        conn.close()
        return count


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


# ==================== مهاجرت ====================
def migrate_from_json():
    import os
    existing = load_all_experts()
    if existing:
        return
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                experts = json.load(f)
                if experts:
                    save_all_experts(experts)
                    print("Migrated {} experts".format(len(experts)))
        except Exception as e:
            print("Expert migration error:", str(e)[:100])
    if os.path.exists(JOBS_FILE):
        try:
            with open(JOBS_FILE, "r", encoding="utf-8") as f:
                jobs = json.load(f)
                if jobs:
                    save_all_jobs(jobs)
                    print("Migrated {} jobs".format(len(jobs)))
        except Exception as e:
            print("Job migration error:", str(e)[:100])
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
                print("Migrated config")
        except Exception as e:
            print("Config migration error:", str(e)[:100])


# ==================== کیف پول ====================
def create_wallet_request(expert_id, amount, receipt_message_id):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        now = int(__import__("time").time())
        c.execute("""
            INSERT INTO wallet_transactions
            (expert_id, amount, type, status, receipt_message_id, created_at)
            VALUES (?, ?, 'charge', 'pending', ?, ?)
        """, (expert_id, amount, receipt_message_id, now))
        txn_id = c.lastrowid
        conn.commit()
        conn.close()
        return txn_id


def get_wallet_transaction(txn_id):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM wallet_transactions WHERE id = ?", (txn_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None


def update_wallet_transaction(txn_id, field, value):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("UPDATE wallet_transactions SET {} = ? WHERE id = ?".format(field), (value, txn_id))
        conn.commit()
        conn.close()


def get_pending_wallet_requests():
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM wallet_transactions WHERE status = 'pending' ORDER BY created_at DESC")
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]


def get_expert_wallet_history(expert_id, limit=10):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT * FROM wallet_transactions
            WHERE expert_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (expert_id, limit))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]


def delete_old_wallet_transactions(cutoff_timestamp):
    """حذف تراکنش‌های قدیمی (فقط approved/rejected)"""
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            DELETE FROM wallet_transactions
            WHERE created_at < ? AND status != 'pending'
        """, (cutoff_timestamp,))
        count = c.rowcount
        conn.commit()
        conn.close()
        return count


# ==================== چت ====================
def create_chat(expert_id, customer_id, job_code=""):
    import time as _time
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT id FROM chats
            WHERE expert_id = ? AND customer_id = ?
            ORDER BY created_at DESC LIMIT 1
        """, (expert_id, customer_id))
        row = c.fetchone()
        if row:
            chat_id = row["id"]
            c.execute("UPDATE chats SET status = 'active' WHERE id = ?", (chat_id,))
            conn.commit()
            conn.close()
            return chat_id
        now = int(_time.time())
        c.execute("""
            INSERT INTO chats
            (expert_id, customer_id, job_code, status, created_at, last_message_at)
            VALUES (?, ?, ?, 'active', ?, ?)
        """, (expert_id, customer_id, job_code, now, now))
        chat_id = c.lastrowid
        conn.commit()
        conn.close()
        return chat_id


def get_chat(chat_id):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM chats WHERE id = ?", (chat_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None


def get_chat_between(expert_id, customer_id):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT * FROM chats
            WHERE expert_id = ? AND customer_id = ? AND status = 'active'
            ORDER BY created_at DESC LIMIT 1
        """, (expert_id, customer_id))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None


def update_chat(chat_id, field, value):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("UPDATE chats SET {} = ? WHERE id = ?".format(field), (value, chat_id))
        conn.commit()
        conn.close()


def add_message(chat_id, sender_id, sender_type, content, message_id=0, is_photo=0):
    import time as _time
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        now = int(_time.time())
        c.execute("""
            INSERT INTO messages
            (chat_id, sender_id, sender_type, content, message_id, is_photo, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (chat_id, sender_id, sender_type, content, message_id, is_photo, now))
        msg_id = c.lastrowid
        c.execute("UPDATE chats SET last_message_at = ? WHERE id = ?", (now, chat_id))
        if sender_type == "expert":
            c.execute("UPDATE chats SET customer_unread = customer_unread + 1 WHERE id = ?", (chat_id,))
        else:
            c.execute("UPDATE chats SET expert_unread = expert_unread + 1 WHERE id = ?", (chat_id,))
        conn.commit()
        conn.close()
        return msg_id


def get_chat_messages(chat_id, limit=20):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT * FROM messages
            WHERE chat_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (chat_id, limit))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in reversed(rows)]


def reset_unread(chat_id, user_type):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        if user_type == "expert":
            c.execute("UPDATE chats SET expert_unread = 0 WHERE id = ?", (chat_id,))
        else:
            c.execute("UPDATE chats SET customer_unread = 0 WHERE id = ?", (chat_id,))
        conn.commit()
        conn.close()


def get_expert_chats(expert_id, filter_type="all"):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        if filter_type == "unread":
            c.execute("""
                SELECT * FROM chats
                WHERE expert_id = ? AND expert_hidden = 0
                AND status = 'active' AND expert_unread > 0
                ORDER BY last_message_at DESC
            """, (expert_id,))
        else:
            c.execute("""
                SELECT * FROM chats
                WHERE expert_id = ? AND expert_hidden = 0
                AND status = 'active'
                ORDER BY last_message_at DESC
            """, (expert_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]


def get_customer_chats(customer_id, filter_type="all"):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        if filter_type == "unread":
            c.execute("""
                SELECT * FROM chats
                WHERE customer_id = ? AND customer_hidden = 0
                AND status = 'active' AND customer_unread > 0
                ORDER BY last_message_at DESC
            """, (customer_id,))
        else:
            c.execute("""
                SELECT * FROM chats
                WHERE customer_id = ? AND customer_hidden = 0
                AND status = 'active'
                ORDER BY last_message_at DESC
            """, (customer_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]


# ==================== نظرات متنی ====================
def add_comment(expert_id, customer_id, specialty, stage, stars, comment,
                author_name="", is_anonymous=0):
    import time as _time
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        now = int(_time.time())
        c.execute("""
            INSERT INTO comments
            (expert_id, customer_id, specialty, stage, stars, comment,
             author_name, is_anonymous, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (expert_id, customer_id, specialty, stage, stars, comment,
              author_name, is_anonymous, now))
        comment_id = c.lastrowid
        conn.commit()
        conn.close()
        return comment_id


def get_expert_comments(expert_id, limit=20):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT * FROM comments
            WHERE expert_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (expert_id, limit))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]


def get_expert_spec_comments(expert_id, specialty, limit=10):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT * FROM comments
            WHERE expert_id = ? AND specialty = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (expert_id, specialty, limit))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]


def get_comment_count(expert_id):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) as cnt FROM comments WHERE expert_id = ?", (expert_id,))
        row = c.fetchone()
        conn.close()
        return row["cnt"] if row else 0


def has_rated(expert_id, customer_id, stage):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT COUNT(*) as cnt FROM comments
            WHERE expert_id = ? AND customer_id = ? AND stage = ?
        """, (expert_id, customer_id, stage))
        row = c.fetchone()
        conn.close()
        return row["cnt"] > 0 if row else False


def delete_old_comments(cutoff_timestamp):
    """حذف نظرات قدیمی"""
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM comments WHERE created_at < ?", (cutoff_timestamp,))
        count = c.rowcount
        conn.commit()
        conn.close()
        return count


# ==================== لاگ عیوب دستگاه ====================
def add_device_log(job_code, expert_id, customer_id, device_name, defect_text,
                   author_id, author_role):
    import time as _time
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        now = int(_time.time())
        c.execute("""
            INSERT INTO device_logs
            (job_code, expert_id, customer_id, device_name, defect_text,
             author_id, author_role, created_at, updated_at, is_edited, old_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, '')
        """, (job_code, expert_id, customer_id, device_name, defect_text,
              author_id, author_role, now))
        log_id = c.lastrowid
        conn.commit()
        conn.close()
        return log_id


def get_device_logs(job_code):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT * FROM device_logs
            WHERE job_code = ?
            ORDER BY created_at ASC
        """, (job_code,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]


def get_device_log(log_id):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM device_logs WHERE id = ?", (log_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None


def update_device_log(log_id, new_text):
    import time as _time
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT defect_text FROM device_logs WHERE id = ?", (log_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            return False
        old_text = row["defect_text"]
        now = int(_time.time())
        c.execute("""
            UPDATE device_logs
            SET defect_text = ?, old_text = ?, updated_at = ?, is_edited = 1
            WHERE id = ?
        """, (new_text, old_text, now, log_id))
        conn.commit()
        conn.close()
        return True


def delete_device_log(log_id):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM device_logs WHERE id = ?", (log_id,))
        conn.commit()
        conn.close()


def get_customer_jobs_with_logs(customer_id, limit=10):
    """پروژه‌های مشتری که لاگ عیب دارن"""
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT DISTINCT j.* FROM jobs j
            INNER JOIN device_logs dl ON dl.job_code = j.tracking_code
            WHERE j.customer_id = ?
            ORDER BY j.created_at DESC
            LIMIT ?
        """, (customer_id, limit))
        rows = c.fetchall()
        conn.close()
        return [_row_to_job(r) for r in rows]


def delete_old_device_logs(cutoff_timestamp):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM device_logs WHERE created_at < ?", (cutoff_timestamp,))
        count = c.rowcount
        conn.commit()
        conn.close()
        return count


# ==================== امنیت ====================
def log_security_event(user_id, event_type, details=""):
    import time as _time
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        now = int(_time.time())
        c.execute("""
            INSERT INTO security_events (user_id, event_type, details, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, event_type, details, now))
        conn.commit()
        conn.close()


def get_recent_security_events(limit=50):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT * FROM security_events
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]


def is_user_blocked(user_id):
    """آیا کاربر مسدود هست؟"""
    import time as _time
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM blocked_users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        if not row:
            return False
        blocked_until = row["blocked_until"]
        if blocked_until == 0:
            return True  # دائم
        return blocked_until > int(_time.time())


def block_user(user_id, reason, blocked_by, duration_hours=0):
    import time as _time
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        now = int(_time.time())
        blocked_until = 0
        if duration_hours > 0:
            blocked_until = now + (duration_hours * 3600)
        c.execute("""
            INSERT OR REPLACE INTO blocked_users
            (user_id, reason, blocked_by, blocked_at, blocked_until)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, reason, blocked_by, now, blocked_until))
        conn.commit()
        conn.close()


def unblock_user(user_id):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM blocked_users WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()


def get_blocked_users():
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM blocked_users ORDER BY blocked_at DESC")
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]


def get_login_attempts(user_id):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM admin_login_attempts WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None


def record_login_attempt(user_id, success):
    import time as _time
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        now = int(_time.time())
        row = get_login_attempts(user_id)
        if success:
            # ریست
            c.execute("""
                INSERT OR REPLACE INTO admin_login_attempts
                (user_id, attempts, last_attempt, locked_until)
                VALUES (?, 0, ?, 0)
            """, (user_id, now))
        else:
            attempts = (row.get("attempts", 0) if row else 0) + 1
            locked_until = 0
            if attempts >= 5:
                locked_until = now + (15 * 60)  # ۱۵ دقیقه قفل
                attempts = 0
            c.execute("""
                INSERT OR REPLACE INTO admin_login_attempts
                (user_id, attempts, last_attempt, locked_until)
                VALUES (?, ?, ?, ?)
            """, (user_id, attempts, now, locked_until))
        conn.commit()
        conn.close()


def is_login_locked(user_id):
    import time as _time
    row = get_login_attempts(user_id)
    if not row:
        return False
    return row.get("locked_until", 0) > int(_time.time())


def reset_login_attempts(user_id):
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM admin_login_attempts WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()


def cleanup_old_security_events(days=30):
    import time as _time
    cutoff = int(_time.time()) - (days * 86400)
    with _lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM security_events WHERE created_at < ?", (cutoff,))
        count = c.rowcount
        conn.commit()
        conn.close()
        return count
