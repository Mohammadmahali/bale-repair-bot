# ==================== امتیازدهی ====================
import time
from texts import (
    CRITERIA, RATE_ASK, RATE_THX, RATE_START, RATE_SELECT,
    RATE_OK, ERR, LBL_NAME, FOLLOWUP_1MONTH, FOLLOWUP_6MONTH,
    FOLLOWUP_BTN,
)
from keyboards import kb_stars, kb_main
from api import send_message, answer_callback
from db import (
    load_experts, save_experts, find_expert_by_id,
    load_jobs, save_jobs, get_pending_job, advance_job_stage,
)


# ==================== شروع امتیازدهی ====================
def start_rating(chat_id, user_id, expert_id, sessions, stage=0):
    """شروع فرآیند امتیازدهی"""
    expert = find_expert_by_id(expert_id)
    if not expert:
        send_message(chat_id, ERR)
        return False
    
    sessions[user_id] = {
        "rating": {
            "expert_id": expert_id,
            "ratings": {},
            "stage": stage,
        }
    }
    
    # شروع از اولین معیار
    _ask_next_criterion(chat_id, user_id, expert, sessions)
    return True


# ==================== پرسیدن معیار بعدی ====================
def _ask_next_criterion(chat_id, user_id, expert, sessions):
    """پرسیدن معیار بعدی امتیازدهی"""
    if user_id not in sessions:
        return
    rating_data = sessions[user_id].get("rating")
    if not rating_data:
        return
    
    current_ratings = rating_data.get("ratings", {})
    
    for cr in CRITERIA:
        if cr["key"] not in current_ratings:
            msg = cr["label"] + RATE_SELECT
            send_message(chat_id, msg, kb_stars(cr["key"]))
            return
    
    # همه معیارها ثبت شد
    _finalize_rating(chat_id, user_id, expert, sessions)


# ==================== ثبت یه معیار ====================
def handle_rating_callback(chat_id, user_id, criteria_key, stars, sessions):
    """ثبت امتیاز یه معیار"""
    if user_id not in sessions:
        return False
    rating_data = sessions[user_id].get("rating")
    if not rating_data:
        return False
    
    rating_data["ratings"][criteria_key] = stars
    
    expert = find_expert_by_id(rating_data["expert_id"])
    if expert:
        _ask_next_criterion(chat_id, user_id, expert, sessions)
    return True


# ==================== نهایی‌سازی امتیاز ====================
def _finalize_rating(chat_id, user_id, expert, sessions):
    """ذخیره امتیازها"""
    rating_data = sessions.pop(user_id, {}).get("rating", {})
    if not rating_data:
        return
    
    stage = rating_data.get("stage", 0)
    ratings = rating_data.get("ratings", {})
    
    # ذخیره توی دیتابیس
    _apply_rating(expert["user_id"], ratings, stage)
    
    # اگه نظرسنجی دوره‌ای بود، stage رو جلو ببر
    if stage != 0:
        advance_job_stage(user_id, expert["user_id"])
    
    # پیام تشکر
    txt = RATE_THX + "\n\n" + expert["name"] + ":\n\n"
    for cr in CRITERIA:
        s = ratings.get(cr["key"], 0)
        txt += cr["label"] + ": " + ("⭐" * s) + "\n"
    
    send_message(chat_id, txt, kb_main())


# ==================== اعمال امتیاز در دیتابیس ====================
def _apply_rating(expert_id, ratings, stage):
    """ذخیره امتیاز توی دیتابیس"""
    experts = load_experts()
    for e in experts:
        if e.get("user_id") == expert_id:
            if "ratings_by_stage" not in e:
                e["ratings_by_stage"] = {}
            stage_data = e["ratings_by_stage"].setdefault(str(stage), {})
            for k, v in ratings.items():
                if k not in stage_data:
                    stage_data[k] = {"sum": 0, "count": 0}
                stage_data[k]["sum"] += v
                stage_data[k]["count"] += 1
            break
    save_experts(experts)


# ==================== نظرسنجی دوره‌ای ====================
def check_followups():
    """بررسی زمان‌بندی نظرسنجی‌ها"""
    jobs = load_jobs()
    now = int(time.time())
    changed = False
    
    for j in jobs:
        if j.get("stage", 0) >= 2:
            continue
        if j.get("sent_for_stage", 0) > j.get("stage", 0):
            continue
        if j.get("next_at", 0) > now:
            continue
        
        stage = j.get("stage", 0)
        if stage == 0:
            msg = FOLLOWUP_1MONTH.format(name=j.get("expert_name", "?"))
        else:
            msg = FOLLOWUP_6MONTH.format(name=j.get("expert_name", "?"))
        
        kb = {
            "inline_keyboard": [[
                {"text": FOLLOWUP_BTN,
                 "callback_data": "frate:" + str(j["expert_id"])}
            ]]
        }
        send_message(j["customer_chat_id"], msg, kb)
        j["sent_for_stage"] = stage + 1
        changed = True
    
    if changed:
        save_jobs(jobs)
