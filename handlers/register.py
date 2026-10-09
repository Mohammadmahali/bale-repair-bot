# ==================== امتیازدهی ====================
import time
from texts import (
    CRITERIA, RATE_ASK, RATE_THX, RATE_START, RATE_SELECT,
    RATE_OK, ERR, LBL_NAME, FOLLOWUP_1MONTH, FOLLOWUP_6MONTH,
    FOLLOWUP_BTN,
    COMMENT_ASK, COMMENT_SKIP_BTN, COMMENT_SAVED, COMMENT_THANKS,
    COMMENT_ASK_NAME, BTN_COMMENT_WITH_NAME, BTN_COMMENT_ANON,
)
from keyboards import (
    kb_stars, kb_main, kb_comment_ask, kb_comment_name_choice,
)
from api import send_message, answer_callback
from db import (
    load_experts, save_experts, find_expert_by_id,
    load_jobs, save_jobs, get_pending_job, advance_job_stage,
    has_rated, mark_job_rated, add_comment,
)


# ==================== پیدا کردن تخصص ====================
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


# ==================== شروع امتیازدهی ====================
def start_rating(chat_id, user_id, expert_id, sessions, stage=0, specialty=None):
    """شروع فرآیند امتیازدهی"""
    expert = find_expert_by_id(expert_id)
    if not expert:
        send_message(chat_id, ERR)
        return False

    # ===== ضد تقلب: چک کن قبلاً امتیاز نداده =====
    if has_rated(expert_id, user_id, stage):
        send_message(
            chat_id,
            "⚠️ شما قبلاً به این تعمیرکار امتیاز داده‌اید.\n"
            "هر مشتری فقط یک بار می‌تواند امتیاز بدهد.",
            kb_main()
        )
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

    # همه معیارها ثبت شد → برو سراغ نظر متنی
    _ask_comment(chat_id, user_id, sessions)


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
def _ask_comment(chat_id, user_id, sessions):
    """بعد از ۸ معیار، از کاربر می‌پرسیم نظر متنی بذاره"""
    if user_id not in sessions:
        return
    rating_data = sessions[user_id].get("rating")
    if not rating_data:
        return

    rating_data["step"] = "comment_ask"
    send_message(chat_id, COMMENT_ASK, kb_comment_ask())


# ==================== هندل نظر متنی ====================
def handle_comment_text(chat_id, user_id, text, sessions):
    """هندل متن نظر"""
    if user_id not in sessions:
        return False
    rating_data = sessions[user_id].get("rating")
    if not rating_data:
        return False
    if rating_data.get("step") != "comment_ask":
        return False

    # ذخیره متن
    rating_data["comment"] = text.strip()
    rating_data["step"] = "comment_name_choice"

    send_message(
        chat_id,
        "👤 می‌خواهید نظرتان با نام نمایش داده شود یا ناشناس؟",
        kb_comment_name_choice()
    )
    return True


def handle_comment_skip(chat_id, user_id, sessions):
    """کاربر نظر متنی نمی‌خواد بذاره"""
    if user_id not in sessions:
        return False
    rating_data = sessions[user_id].get("rating")
    if not rating_data:
        return False
    if rating_data.get("step") != "comment_ask":
        return False

    rating_data["comment"] = ""
    rating_data["author_name"] = ""
    rating_data["is_anonymous"] = 0

    _finalize_rating(chat_id, user_id, sessions)
    return True


def handle_comment_name_choice(chat_id, user_id, choice, sessions):
    """
    choice: "with_name" | "anon"
    """
    if user_id not in sessions:
        return False
    rating_data = sessions[user_id].get("rating")
    if not rating_data:
        return False
    if rating_data.get("step") != "comment_name_choice":
        return False

    if choice == "anon":
        rating_data["author_name"] = ""
        rating_data["is_anonymous"] = 1
        _finalize_rating(chat_id, user_id, sessions)
        return True

    # با نام → از کاربر اسم بخواه
    rating_data["step"] = "comment_name_input"
    send_message(chat_id, COMMENT_ASK_NAME, kb_main())
    return True


def handle_comment_name_input(chat_id, user_id, text, sessions):
    """دریافت اسم نمایشی"""
    if user_id not in sessions:
        return False
    rating_data = sessions[user_id].get("rating")
    if not rating_data:
        return False
    if rating_data.get("step") != "comment_name_input":
        return False

    rating_data["author_name"] = text.strip()[:50]
    rating_data["is_anonymous"] = 0

    _finalize_rating(chat_id, user_id, sessions)
    return True


# ==================== نهایی‌سازی امتیاز ====================
def _finalize_rating(chat_id, user_id, sessions):
    """ذخیره امتیازها + ثبت نظر"""
    rating_data = sessions.pop(user_id, {}).get("rating", {})
    if not rating_data:
        return

    stage = rating_data.get("stage", 0)
    ratings = rating_data.get("ratings", {})
    specialty = rating_data.get("specialty")
    expert_id = rating_data.get("expert_id")
    comment = rating_data.get("comment", "")
    author_name = rating_data.get("author_name", "")
    is_anonymous = rating_data.get("is_anonymous", 0)

    expert = find_expert_by_id(expert_id)
    if not expert:
        return

    # ===== محاسبه میانگین امتیاز برای نمایش =====
    avg_stars = 0
    if ratings:
        avg_stars = sum(ratings.values()) / len(ratings)

    # ===== ذخیره توی دیتابیس (کلی + تفکیک + نظر) =====
    _apply_rating(expert_id, ratings, stage, specialty)

    # ===== ثبت نظر در جدول comments (حتی اگه متن خالی باشه) =====
    add_comment(
        expert_id=expert_id,
        customer_id=user_id,
        specialty=specialty or "",
        stage=stage,
        stars=avg_stars,
        comment=comment,
        author_name=author_name,
        is_anonymous=is_anonymous,
    )

    # ===== علامت‌گذاری که این مشتری امتیاز داده =====
    mark_job_rated(user_id, expert_id, stage)

    # اگه نظرسنجی دوره‌ای بود، stage رو جلو ببر
    if stage != 0:
        advance_job_stage(user_id, expert_id)

    # ===== پیام تشکر =====
    txt = RATE_THX + "\n\n" + expert["name"] + ":\n\n"
    for cr in CRITERIA:
        s = ratings.get(cr["key"], 0)
        txt += cr["label"] + ": " + ("⭐" * s) + "\n"

    if specialty:
        txt += "\n🔧 تخصص: " + specialty

    if comment:
        txt += "\n\n" + COMMENT_THANKS

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

            # ===== بخش ۱: امتیاز کلی =====
            stage_data = e["ratings_by_stage"].setdefault(str(stage), {})
            for k, v in ratings.items():
                if k not in stage_data:
                    stage_data[k] = {"sum": 0, "count": 0}
                stage_data[k]["sum"] += v
                stage_data[k]["count"] += 1

            # ===== بخش ۲: امتیاز تفکیک‌شده بر تخصص =====
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

        # اگه قبلاً امتیاز داده، نپرس
        if j.get("stage", 0) in j.get("rated_stages", []):
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
