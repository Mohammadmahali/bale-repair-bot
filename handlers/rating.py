# ==================== امتیازدهی + نظرات متنی ====================
import time
from texts import (
    CRITERIA, RATE_ASK, RATE_THX, RATE_START, RATE_SELECT,
    RATE_OK, ERR, LBL_NAME, FOLLOWUP_1MONTH, FOLLOWUP_6MONTH,
    FOLLOWUP_BTN,
    COMMENT_ASK, COMMENT_SKIP_BTN, COMMENT_SAVED, COMMENT_THANKS,
    COMMENT_ASK_NAME, BTN_COMMENT_WITH_NAME, BTN_COMMENT_ANON,
    SEC_RATING_ALREADY, SEC_RATING_NEED_JOB,
    BTN_BACK,
)
from keyboards import kb_stars, kb_main, kb_back, kb_comment_choice, kb_comment_name_choice
from api import send_message, answer_callback
from db import (
    load_experts, save_experts, find_expert_by_id,
    load_jobs, save_jobs, get_pending_job, advance_job_stage,
    find_job_by_code, add_comment, has_rated,
)


# ==================== پیدا کردن تخصص و job ====================
def _find_specialty(customer_id, expert_id):
    """پیدا کردن تخصص از آخرین job بین مشتری و تعمیرکار"""
    jobs = load_jobs()
    matching = [
        j for j in jobs
        if j.get("customer_id") == customer_id and j.get("expert_id") == expert_id
    ]
    if not matching:
        return None
    matching.sort(key=lambda x: x.get("created_at", 0), reverse=True)
    info = matching[0].get("info", {})
    return info.get("sub")


def _find_job(customer_id, expert_id):
    """پیدا کردن آخرین job بین مشتری و تعمیرکار"""
    jobs = load_jobs()
    matching = [
        j for j in jobs
        if j.get("customer_id") == customer_id and j.get("expert_id") == expert_id
    ]
    if not matching:
        return None
    matching.sort(key=lambda x: x.get("created_at", 0), reverse=True)
    return matching[0]


def _mark_rated(job_id, stage):
    """ثبت اینکه این stage امتیاز گرفته شده"""
    jobs = load_jobs()
    for j in jobs:
        if j.get("id") == job_id:
            rated = j.get("rated_stages", [])
            if stage not in rated:
                rated.append(stage)
                j["rated_stages"] = rated
            break
    save_jobs(jobs)


# ==================== شروع امتیازدهی ====================
def start_rating(chat_id, user_id, expert_id, sessions, stage=0, specialty=None):
    """شروع فرآیند امتیازدهی"""
    expert = find_expert_by_id(expert_id)
    if not expert:
        send_message(chat_id, ERR)
        return False

    # چک ضد تقلب: آیا قبلاً امتیاز داده؟
    job = _find_job(user_id, expert_id)
    if not job:
        send_message(chat_id, SEC_RATING_NEED_JOB)
        return False

    rated_stages = job.get("rated_stages", [])
    if stage in rated_stages:
        send_message(chat_id, SEC_RATING_ALREADY)
        return False

    # اگه تخصص پاس داده نشد، از job پیدا کن
    if specialty is None:
        specialty = _find_specialty(user_id, expert_id)

    sessions[user_id] = {
        "rating": {
            "expert_id": expert_id,
            "ratings": {},
            "stage": stage,
            "specialty": specialty,
            "job_id": job.get("id"),
        }
    }

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

    # همه معیارها ثبت شد → برو به مرحله نظر متنی
    _ask_comment(chat_id, user_id, expert, sessions)


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


# ==================== پرسیدن نظر متنی ====================
def _ask_comment(chat_id, user_id, expert, sessions):
    """بعد از ۸ ستاره، از مشتری می‌پرسیم نظر بذاره یا نه"""
    if user_id not in sessions:
        return
    rating_data = sessions[user_id].get("rating")
    if not rating_data:
        return
    rating_data["step"] = "ask_comment"
    send_message(chat_id, COMMENT_ASK, kb_comment_choice())


# ==================== هندل انتخاب نظر (بله/رد) ====================
def handle_comment_choice(chat_id, user_id, choice, sessions):
    """
    choice: 'yes' یا 'skip'
    """
    if user_id not in sessions:
        return False
    rating_data = sessions[user_id].get("rating")
    if not rating_data or rating_data.get("step") != "ask_comment":
        return False

    if choice == "skip":
        _finalize_rating(chat_id, user_id, sessions, comment=None)
        return True

    # choice == "yes" → پرسیدن اسم
    rating_data["step"] = "ask_name"
    send_message(chat_id, COMMENT_ASK_NAME, kb_comment_name_choice())
    return True


# ==================== هندل انتخاب نام (با نام/ناشناس) ====================
def handle_comment_name_choice(chat_id, user_id, choice, sessions):
    """
    choice: 'named' یا 'anon'
    """
    if user_id not in sessions:
        return False
    rating_data = sessions[user_id].get("rating")
    if not rating_data or rating_data.get("step") != "ask_name":
        return False

    rating_data["is_anonymous"] = (choice == "anon")
    rating_data["step"] = "ask_comment_text"
    send_message(chat_id, "✍️ متن نظر خودتون رو بنویسید:", kb_back())
    return True


# ==================== هندل متن نظر ====================
def handle_comment_text(chat_id, user_id, text, sessions):
    """ذخیره متن نظر و نهایی‌سازی"""
    if user_id not in sessions:
        return False
    rating_data = sessions[user_id].get("rating")
    if not rating_data or rating_data.get("step") != "ask_comment_text":
        return False

    if text == BTN_BACK:
        _finalize_rating(chat_id, user_id, sessions, comment=None)
        return True

    text = (text or "").strip()
    if len(text) < 2:
        send_message(chat_id, "❌ متن نظر خیلی کوتاهه. دوباره بنویسید یا بازگشت بزنید.", kb_back())
        return True

    if len(text) > 500:
        text = text[:500]

    _finalize_rating(chat_id, user_id, sessions, comment=text)
    return True


# ==================== نهایی‌سازی امتیاز ====================
def _finalize_rating(chat_id, user_id, sessions, comment=None):
    """ذخیره امتیازها + نظر متنی"""
    rating_data = sessions.pop(user_id, {}).get("rating", {})
    if not rating_data:
        return

    stage = rating_data.get("stage", 0)
    ratings = rating_data.get("ratings", {})
    specialty = rating_data.get("specialty")
    expert_id = rating_data.get("expert_id")
    job_id = rating_data.get("job_id")
    is_anonymous = rating_data.get("is_anonymous", False)

    expert = find_expert_by_id(expert_id)
    if not expert:
        return

    # ذخیره امتیازها (کلی + تفکیک‌شده)
    _apply_rating(expert_id, ratings, stage, specialty)

    # ثبت که این stage امتیاز گرفته
    if job_id:
        _mark_rated(job_id, stage)

    # ذخیره نظر متنی (حتی اگه خالی باشه، برای ضد تقلب)
    avg_stars = sum(ratings.values()) / len(ratings) if ratings else 0
    author_name = ""
    if not is_anonymous:
        author_name = "کاربر"

    add_comment(
        expert_id=expert_id,
        customer_id=user_id,
        specialty=specialty or "",
        stage=stage,
        stars=avg_stars,
        comment=comment or "",
        author_name=author_name,
        is_anonymous=1 if is_anonymous else 0,
    )

    # اگه نظرسنجی دوره‌ای بود، stage رو جلو ببر
    if stage != 0:
        advance_job_stage(user_id, expert_id)

    # پیام تشکر
    txt = RATE_THX + "\n\n" + expert["name"] + ":\n\n"
    for cr in CRITERIA:
        s = ratings.get(cr["key"], 0)
        txt += cr["label"] + ": " + ("⭐" * s) + "\n"

    if specialty:
        txt += "\n🔧 تخصص: " + specialty

    if comment:
        txt += "\n\n💬 " + COMMENT_THANKS

    send_message(chat_id, txt, kb_main())


# ==================== اعمال امتیاز در دیتابیس ====================
def _apply_rating(expert_id, ratings, stage, specialty=None):
    """
    ذخیره امتیاز توی دیتابیس:
    - ratings_by_stage (کلی)
    - ratings_by_stage.by_spec[specialty] (تفکیک‌شده)
    """
    experts = load_experts()
    for e in experts:
        if e.get("user_id") == expert_id:
            if "ratings_by_stage" not in e:
                e["ratings_by_stage"] = {}

            # بخش ۱: امتیاز کلی
            stage_data = e["ratings_by_stage"].setdefault(str(stage), {})
            for k, v in ratings.items():
                if k not in stage_data:
                    stage_data[k] = {"sum": 0, "count": 0}
                stage_data[k]["sum"] += v
                stage_data[k]["count"] += 1

            # بخش ۲: تفکیک‌شده بر تخصص
            if specialty:
                by_spec = e["ratings_by_stage"].setdefault("by_spec", {})
                spec_data = by_spec.setdefault(specialty, {})
                spec_stage = spec_data.setdefault(str(stage), {})
                for k, v in ratings.items():
                    if k not in spec_stage:
                        spec_stage[k] = {"sum": 0, "count": 0}
                    spec_stage[k]["sum"] += v
                    spec_stage[k]["count"] += 1
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
