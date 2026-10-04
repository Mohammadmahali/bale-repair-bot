# ==================== پنل مدیریت ====================
import time
from config import SUPER_ADMIN, COMMISSION_DEFAULT
from db import (
    load_experts, find_expert_by_id, delete_expert,
    update_expert_field, get_stats, load_jobs,
    get_operators, add_operator, remove_operator,
    get_user_password, set_user_password, load_admin_config,
)
from api import send_message
from keyboards import (
    kb_admin, kb_approve_reject, kb_expert_detail,
    kb_operators, kb_back,
)
from texts import (
    ADM_TITLE, ADM_STATS, ADM_PENDING, ADM_NEW_EXPERT,
    ADM_NO_PENDING, ADM_NO_EXPERT, ADM_NO_OPERATOR,
    ADM_ASK_OP_ID, ADM_OP_ADDED, ADM_APPROVED_OK, ADM_REJECTED_OK,
    ADM_DELETED, EXP_APPROVED_NOTIFY, EXP_REJECTED_NOTIFY,
    ADM_SET_PASS_FIRST, ADM_ENTER_NEW_PASS, ADM_ENTER_AGAIN,
    ADM_PASS_MISMATCH, ADM_PASS_SHORT, ADM_PASS_SET_OK,
    LBL_NAME, LBL_PHONE, LBL_ROLE, LBL_SUBSPEC, LBL_AREA,
    LBL_RATING, LBL_REFERRAL,
    ADM_BACK,
)
from utils import format_toman


# ==================== بررسی دسترسی ====================
def is_super_admin(user_id):
    return user_id == SUPER_ADMIN


def is_admin(user_id):
    if user_id == SUPER_ADMIN:
        return True
    return user_id in get_operators()


# ==================== اعلان به مدیران ====================
def notify_admins_new_expert(expert):
    """اطلاع به مدیران از تعمیرکار جدید"""
    msg = ADM_NEW_EXPERT + "\n\n"
    msg += LBL_NAME + " " + expert.get("name", "?") + "\n"
    msg += LBL_PHONE + " " + expert.get("phone", "?") + "\n"
    msg += LBL_ROLE + " " + expert.get("category", "?") + "\n"
    msg += LBL_SUBSPEC + " " + "، ".join(expert.get("sub_specialties", [])) + "\n"
    msg += LBL_AREA + " " + expert.get("area", "?") + "\n"
    
    kb = kb_approve_reject(expert["user_id"])
    send_message(SUPER_ADMIN, msg, kb)
    for op in get_operators():
        send_message(op, msg, kb)


def notify_admins_report(report):
    """اطلاع به مدیران از گزارش جدید"""
    msg = "🚨 گزارش جدید!\n\n"
    msg += "نوع: " + report.get("target_type", "?") + "\n"
    msg += "دلیل: " + report.get("reason", "?") + "\n"
    msg += "توضیحات: " + report.get("description", "?") + "\n"
    msg += "شناسه گزارش: " + str(report.get("id"))
    send_message(SUPER_ADMIN, msg)
    for op in get_operators():
        send_message(op, msg)


# ==================== آمار ====================
def show_stats(chat_id):
    stats = get_stats()
    txt = "📊 آمار کلی ربات\n\n"
    txt += "👥 کل متخصصین: " + str(stats["total_experts"]) + "\n"
    txt += "✅ تأیید شده: " + str(stats["approved_experts"]) + "\n"
    txt += "⏳ در انتظار: " + str(stats["pending_experts"]) + "\n"
    txt += "🟢 فعال: " + str(stats["active_experts"]) + "\n"
    txt += "⭐ ویژه: " + str(stats["premium_experts"]) + "\n"
    txt += "📈 کل معرفی‌ها: " + str(stats["total_referrals"]) + "\n"
    txt += "📋 کل پروژه‌ها: " + str(stats["total_jobs"]) + "\n"
    txt += "👤 مشتریان یکتا: " + str(stats["unique_customers"]) + "\n"
    txt += "🚨 گزارش‌های در انتظار: " + str(stats["pending_reports"])
    send_message(chat_id, txt, kb_admin())


# ==================== لیست در انتظار تأیید ====================
def show_pending_list(chat_id):
    pending = [e for e in load_experts() if e.get("status") == "pending"]
    if not pending:
        send_message(chat_id, ADM_NO_PENDING, kb_admin())
        return
    
    kb = {"inline_keyboard": []}
    for e in pending:
        label = e.get("name", "?") + " | " + e.get("category", "?")
        kb["inline_keyboard"].append([
            {"text": label, "callback_data": "adm:viewp:" + str(e["user_id"])}
        ])
    send_message(chat_id, "⏳ در انتظار تأیید:", kb)


def show_pending_detail(chat_id, user_id):
    e = find_expert_by_id(user_id)
    if not e:
        send_message(chat_id, "پیدا نشد.", kb_admin())
        return
    
    txt = ADM_NEW_EXPERT + "\n\n"
    txt += LBL_NAME + " " + e.get("name", "?") + "\n"
    txt += LBL_PHONE + " " + e.get("phone", "?") + "\n"
    txt += LBL_ROLE + " " + e.get("category", "?") + "\n"
    txt += LBL_SUBSPEC + " " + "، ".join(e.get("sub_specialties", [])) + "\n"
    txt += LBL_AREA + " " + e.get("area", "?") + "\n"
    if e.get("works_on_site"):
        txt += "🏠 حضور در محل: بله\n"
    else:
        txt += "🏠 حضور در محل: خیر\n"
    
    kb = {
        "inline_keyboard": [
            [{"text": "✅ تأیید", "callback_data": "adm:appr:" + str(user_id)},
             {"text": "❌ رد", "callback_data": "adm:rej:" + str(user_id)}],
            [{"text": "🔙 بازگشت", "callback_data": "adm:pendinglist"}]
        ]
    }
    send_message(chat_id, txt, kb)


def approve_expert(user_id, chat_id):
    update_expert_field(user_id, "status", "approved")
    send_message(chat_id, ADM_APPROVED_OK, kb_admin())
    send_message(user_id, EXP_APPROVED_NOTIFY)


def reject_expert(user_id, chat_id):
    update_expert_field(user_id, "status", "rejected")
    send_message(chat_id, ADM_REJECTED_OK, kb_admin())
    send_message(user_id, EXP_REJECTED_NOTIFY)


# ==================== لیست متخصصین ====================
def show_experts_list(chat_id):
    experts = [e for e in load_experts() if e.get("status", "approved") == "approved"]
    if not experts:
        send_message(chat_id, ADM_NO_EXPERT, kb_admin())
        return
    
    kb = {"inline_keyboard": []}
    for i, e in enumerate(experts[:15], 1):
        star = "⭐" if e.get("is_premium") else ""
        stat = "✅" if e.get("active", True) else "❌"
        label = "{}. {} {} {} | {:.1f}".format(
            i, stat, star, e.get("name", "?"),
            _calc_avg_rating(e)
        )
        kb["inline_keyboard"].append([
            {"text": label, "callback_data": "adm:exp:" + str(e["user_id"])}
        ])
    send_message(chat_id, "👥 متخصصین:", kb)


def _calc_avg_rating(expert):
    """محاسبه امتیاز کل تعمیرکار"""
    total = 0
    count = 0
    ratings = expert.get("ratings_by_stage", {})
    for stage in ["0", "1", "2"]:
        for key, val in ratings.get(stage, {}).items():
            if isinstance(val, dict) and val.get("count", 0) > 0:
                total += val["sum"]
                count += val["count"]
    if count == 0:
        return 5.0
    return total / count


# ==================== جزئیات تعمیرکار ====================
def show_expert_detail(chat_id, expert_id):
    e = find_expert_by_id(expert_id)
    if not e:
        send_message(chat_id, "پیدا نشد.", kb_admin())
        return
    
    txt = "👤 جزئیات تعمیرکار:\n\n"
    txt += LBL_NAME + " " + e.get("name", "?") + "\n"
    txt += LBL_PHONE + " " + e.get("phone", "?") + "\n"
    txt += LBL_ROLE + " " + e.get("category", "?") + "\n"
    txt += LBL_SUBSPEC + " " + "، ".join(e.get("sub_specialties", [])) + "\n"
    txt += LBL_AREA + " " + e.get("area", "?") + "\n"
    txt += LBL_RATING + "{:.1f}/5".format(_calc_avg_rating(e)) + "\n"
    txt += LBL_REFERRAL + str(e.get("referral_count", 0)) + "\n"
    txt += "🆔 " + e.get("expert_code", "?") + "\n"
    txt += "📱 " + str(e["user_id"]) + "\n"
    
    # وضعیت
    status = "✅ فعال" if e.get("active", True) else "❌ غیرفعال"
    txt += "⚙️ " + status + "\n"
    if e.get("is_premium"):
        txt += "⭐ اشتراک ویژه\n"
    
    # وضعیت مغازه
    shop = e.get("shop_status", "active")
    if shop == "active":
        txt += "🏪 مغازه فعال\n"
    elif shop == "closed_temp":
        txt += "🏪 مغازه تعطیل موقت\n"
    elif shop == "closed_perm":
        txt += "🏪 مغازه تعطیل دائم\n"
    
    kb = kb_expert_detail(
        expert_id,
        e.get("active", True),
        e.get("is_premium", False)
    )
    send_message(chat_id, txt, kb)


def toggle_active(expert_id, chat_id):
    e = find_expert_by_id(expert_id)
    if e:
        new_state = not e.get("active", True)
        update_expert_field(expert_id, "active", new_state)
    show_expert_detail(chat_id, expert_id)


def toggle_premium(expert_id, chat_id):
    e = find_expert_by_id(expert_id)
    if e:
        new_state = not e.get("is_premium", False)
        update_expert_field(expert_id, "is_premium", new_state)
    show_expert_detail(chat_id, expert_id)


def remove_expert(expert_id, chat_id):
    delete_expert(expert_id)
    send_message(chat_id, ADM_DELETED, kb_admin())


# ==================== آخرین معرفی‌ها ====================
def show_jobs(chat_id):
    jobs = load_jobs()
    if not jobs:
        send_message(chat_id, "هنوز معرفی‌ای انجام نشده.", kb_admin())
        return
    
    txt = "📋 آخرین ۱۰ معرفی:\n\n"
    for j in jobs[-10:][::-1]:
        txt += "🎫 " + j.get("tracking_code", "?") + " | " + j.get("expert_name", "?") + "\n"
        info = j.get("info", {})
        if info.get("sub"):
            txt += "   🔧 " + info["sub"] + "\n"
        txt += "\n"
    send_message(chat_id, txt, kb_admin())


# ==================== درآمد ====================
def show_revenue(chat_id):
    experts = load_experts()
    total_refs = sum(e.get("referral_count", 0) for e in experts)
    estimated = total_refs * COMMISSION_DEFAULT
    
    txt = "💰 درآمد:\n\n"
    txt += "📈 کل معرفی‌ها: " + str(total_refs) + "\n"
    txt += "💵 درآمد تخمینی: " + format_toman(estimated) + "\n\n"
    txt += "ℹ️ محاسبه بر اساس " + format_toman(COMMISSION_DEFAULT) + " برای هر معرفی"
    send_message(chat_id, txt, kb_admin())


# ==================== مدیران ====================
def show_operators(chat_id):
    operators = get_operators()
    txt = "👥 مدیران:\n\n"
    txt += "👑 مدیر اصلی: " + str(SUPER_ADMIN) + "\n\n"
    if not operators:
        txt += ADM_NO_OPERATOR
    else:
        for op in operators:
            txt += "👤 " + str(op) + "\n"
    
    send_message(chat_id, txt, kb_operators())


def ask_add_operator(chat_id):
    send_message(chat_id, ADM_ASK_OP_ID, kb_back())


def do_add_operator(new_id, chat_id):
    try:
        new_id_int = int(new_id.strip())
        add_operator(new_id_int)
        send_message(chat_id, ADM_OP_ADDED, kb_admin())
    except:
        send_message(chat_id, "❌ آیدی معتبر نیست.", kb_admin())


def show_remove_operator(chat_id):
    operators = get_operators()
    if not operators:
        send_message(chat_id, ADM_NO_OPERATOR, kb_admin())
        return
    
    kb = {"inline_keyboard": []}
    for op in operators:
        kb["inline_keyboard"].append([
            {"text": str(op), "callback_data": "adm:rmopid:" + str(op)}
        ])
    kb["inline_keyboard"].append([
        {"text": "🔙 بازگشت", "callback_data": "adm:backmain"}
    ])
    send_message(chat_id, "روی مدیر مورد نظر بزنید:", kb)


def do_remove_operator(op_id, chat_id):
    remove_operator(op_id)
    send_message(chat_id, "✅ حذف شد.", kb_admin())


# ==================== تغییر رمز ====================
def ask_change_password(chat_id):
    send_message(chat_id, ADM_ENTER_NEW_PASS, kb_back())


def ask_set_password_first(chat_id):
    send_message(chat_id, ADM_SET_PASS_FIRST, kb_back())


def handle_password_set(chat_id, user_id, new_pass):
    """ثبت رمز جدید"""
    if len(new_pass) < 4:
        return False, ADM_PASS_SHORT
    set_user_password(user_id, new_pass)
    return True, ADM_PASS_SET_OK


# ==================== گزارشات ====================
def show_pending_reports(chat_id):
    from db import load_reports
    reports = [r for r in load_reports() if r.get("status") == "pending"]
    if not reports:
        send_message(chat_id, "هیچ گزارش در انتظاری نیست.", kb_admin())
        return
    
    for r in reports[:5]:
        txt = "🚨 گزارش #" + str(r["id"]) + "\n\n"
        txt += "نوع: " + r.get("target_type", "?") + "\n"
        txt += "دلیل: " + r.get("reason", "?") + "\n"
        if r.get("description"):
            txt += "توضیحات: " + r["description"] + "\n"
        txt += "تاریخ: " + time.strftime("%Y/%m/%d", time.localtime(r.get("created_at", 0)))
        
        kb = {
            "inline_keyboard": [[
                {"text": "✅ تأیید", "callback_data": "adm:rpt_ok:" + str(r["id"])},
                {"text": "❌ رد", "callback_data": "adm:rpt_no:" + str(r["id"])}
            ]]
        }
        send_message(chat_id, txt, kb)
