# ==================== ربات ادمین (جدا) ====================
import time
import threading
from config import SUPER_ADMIN
from api_admin import (
    admin_send_message, admin_answer_callback,
    admin_get_me, admin_get_updates,
    admin_delete_webhook, admin_clear_old_updates,
    admin_forward_message,
)
from keyboards import kb_admin, kb_back, kb_main
from texts import (
    ADM_TITLE, ADM_ASK_PASS, ADM_WRONG_PASS, ADM_NOT_AUTH,
    ADM_STATS, ADM_EXPERTS, ADM_PENDING, ADM_JOBS, ADM_REVENUE,
    ADM_OPERATORS, ADM_CHANGE_PASS, ADM_EXIT,
    ADM_SET_PASS_FIRST, ADM_ENTER_NEW_PASS, ADM_ENTER_AGAIN,
    ADM_PASS_MISMATCH, ADM_PASS_SHORT, ADM_PASS_SET_OK,
    ADM_ASK_OP_ID, ADM_OP_ADDED, ADM_NO_OPERATOR,
    ADM_APPROVE, ADM_REJECT, ADM_APPROVED_OK, ADM_REJECTED_OK,
    ADM_NEW_EXPERT, ADM_NO_PENDING, ADM_NO_EXPERT,
    ADM_DELETED, ADM_BACK,
    USE_MENU, INVALID_INPUT, YES, NO, BTN_BACK,
)
from db import (
    get_operators, add_operator, remove_operator,
    get_user_password, set_user_password,
    find_expert_by_id, delete_expert, update_expert_field,
    get_stats, load_experts, load_jobs,
    get_wallet_balance, approve_wallet_charge, reject_wallet_charge,
)


# ==================== State های ربات ادمین ====================
admin_sessions = set()
admin_user_states = {}


# ==================== بررسی دسترسی ====================
def is_super_admin(user_id):
    return user_id == SUPER_ADMIN


def is_admin(user_id):
    if user_id == SUPER_ADMIN:
        return True
    return user_id in get_operators()


def is_authed_admin(user_id):
    return user_id in admin_sessions and is_admin(user_id)


# ==================== Start ====================
def handle_admin_start(chat_id, user_id):
    if not is_admin(user_id):
        admin_send_message(chat_id, ADM_NOT_AUTH)
        return
    
    if is_authed_admin(user_id):
        admin_send_message(chat_id, ADM_TITLE, kb_admin())
        return
    
    pw = get_user_password(user_id)
    if pw is None:
        admin_user_states[user_id] = {"step": "adm_set_pass", "data": {}}
        admin_send_message(chat_id, ADM_SET_PASS_FIRST, kb_back())
    else:
        admin_user_states[user_id] = {"step": "adm_password", "data": {}}
        admin_send_message(chat_id, ADM_ASK_PASS, kb_back())


# ==================== هندل پیام ====================
def handle_admin_message(msg):
    chat_id = msg.get("chat", {}).get("id")
    user_id = msg.get("from", {}).get("id")
    text = msg.get("text", "")
    
    print("[ADMIN]", user_id, text[:30].encode("ascii", "replace").decode())
    
    # /start
    if text == "/start":
        handle_admin_start(chat_id, user_id)
        return
    
    # اگه authed هست
    if is_authed_admin(user_id):
        if text == ADM_EXIT:
            admin_sessions.discard(user_id)
            admin_user_states.pop(user_id, None)
            admin_send_message(chat_id, "از پنل خارج شدید.")
            return
        if text == ADM_STATS:
            show_stats(chat_id); return
        if text == ADM_EXPERTS:
            show_experts_list(chat_id); return
        if text == ADM_PENDING:
            show_pending_list(chat_id); return
        if text == ADM_JOBS:
            show_jobs(chat_id); return
        if text == ADM_REVENUE:
            show_revenue(chat_id); return
        if text == ADM_OPERATORS:
            show_operators(chat_id); return
        if text == ADM_CHANGE_PASS:
            ask_change_password(chat_id, user_id); return
    
    # state machine
    if user_id in admin_user_states:
        state = admin_user_states[user_id]
        step = state["step"]
        data = state["data"]
        
        if text == BTN_BACK:
            admin_user_states.pop(user_id, None)
            admin_send_message(chat_id, USE_MENU)
            return
        
        # تنظیم رمز اول
        if step == "adm_set_pass":
            if len(text) < 4:
                admin_send_message(chat_id, ADM_PASS_SHORT, kb_back())
                return
            data["new_pass"] = text
            state["step"] = "adm_set_pass_confirm"
            admin_send_message(chat_id, ADM_ENTER_AGAIN, kb_back())
            return
        
        if step == "adm_set_pass_confirm":
            if text != data.get("new_pass"):
                state["step"] = "adm_set_pass"
                data["new_pass"] = ""
                admin_send_message(chat_id, ADM_PASS_MISMATCH, kb_back())
                return
            set_user_password(user_id, text)
            admin_user_states.pop(user_id, None)
            admin_sessions.add(user_id)
            admin_send_message(chat_id, ADM_PASS_SET_OK)
            admin_send_message(chat_id, ADM_TITLE, kb_admin())
            return
        
        # ورود با رمز
        if step == "adm_password":
            pw = get_user_password(user_id)
            if text == pw:
                admin_sessions.add(user_id)
                admin_user_states.pop(user_id, None)
                admin_send_message(chat_id, ADM_TITLE, kb_admin())
            else:
                admin_send_message(chat_id, ADM_WRONG_PASS, kb_back())
            return
        
        # تغییر رمز
        if step == "adm_change_new":
            if len(text) < 4:
                admin_send_message(chat_id, ADM_PASS_SHORT, kb_back())
                return
            data["new_pass"] = text
            state["step"] = "adm_change_confirm"
            admin_send_message(chat_id, ADM_ENTER_AGAIN, kb_back())
            return
        
        if step == "adm_change_confirm":
            if text != data.get("new_pass"):
                state["step"] = "adm_change_new"
                data["new_pass"] = ""
                admin_send_message(chat_id, ADM_PASS_MISMATCH, kb_back())
                return
            set_user_password(user_id, text)
            admin_user_states.pop(user_id, None)
            admin_send_message(chat_id, ADM_PASS_SET_OK, kb_admin())
            return
        
        # افزودن اپراتور
        if step == "adm_add_op":
            try:
                new_id = int(text.strip())
                add_operator(new_id)
                admin_user_states.pop(user_id, None)
                admin_send_message(chat_id, ADM_OP_ADDED, kb_admin())
            except:
                admin_send_message(chat_id, INVALID_INPUT, kb_back())
            return
    
    # پیام نامشخص
    if is_admin(user_id):
        handle_admin_start(chat_id, user_id)
    else:
        admin_send_message(chat_id, ADM_NOT_AUTH)


# ==================== هندل Callback ====================
def handle_admin_callback(cb):
    cb_id = cb.get("id")
    user_id = cb.get("from", {}).get("id")
    chat_id = cb.get("message", {}).get("chat", {}).get("id")
    data = cb.get("data", "")
    
    if not is_authed_admin(user_id):
        admin_answer_callback(cb_id, "دسترسی ندارید")
        return
    
    parts = data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    
    try:
        if action == "exp":
            show_expert_detail(chat_id, int(parts[2]))
        elif action == "tog":
            toggle_active(int(parts[2]), chat_id)
        elif action == "prem":
            toggle_premium(int(parts[2]), chat_id)
        elif action == "del":
            remove_expert(int(parts[2]), chat_id)
        elif action == "back":
            show_experts_list(chat_id)
        elif action == "backmain":
            admin_send_message(chat_id, ADM_TITLE, kb_admin())
        elif action == "pendinglist":
            show_pending_list(chat_id)
        elif action == "viewp":
            show_pending_detail(chat_id, int(parts[2]))
        elif action == "appr":
            approve_expert(int(parts[2]), chat_id)
        elif action == "rej":
            reject_expert(int(parts[2]), chat_id)
        elif action == "addop":
            if not is_super_admin(user_id):
                admin_answer_callback(cb_id, "فقط مدیر اصلی")
                return
            admin_user_states[user_id] = {"step": "adm_add_op", "data": {}}
            admin_send_message(chat_id, ADM_ASK_OP_ID, kb_back())
        elif action == "rmop":
            if not is_super_admin(user_id):
                admin_answer_callback(cb_id, "فقط مدیر اصلی")
                return
            show_remove_operator(chat_id)
        elif action == "rmopid":
            if not is_super_admin(user_id):
                admin_answer_callback(cb_id, "فقط مدیر اصلی")
                return
            remove_operator(int(parts[2]))
            admin_send_message(chat_id, "حذف شد.", kb_admin())
    except Exception as ex:
        print("[ADMIN CB ERROR]", str(ex)[:100])
    
    admin_answer_callback(cb_id)


# ==================== نمایش آمار ====================
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
    txt += "👤 مشتریان یکتا: " + str(stats["unique_customers"])
    admin_send_message(chat_id, txt, kb_admin())


# ==================== لیست در انتظار ====================
def show_pending_list(chat_id):
    pending = [e for e in load_experts() if e.get("status") == "pending"]
    if not pending:
        admin_send_message(chat_id, ADM_NO_PENDING, kb_admin())
        return
    
    kb = {"inline_keyboard": []}
    for e in pending:
        label = e.get("name", "?") + " | " + e.get("category", "?")
        kb["inline_keyboard"].append([
            {"text": label, "callback_data": "adm:viewp:" + str(e["user_id"])}
        ])
    admin_send_message(chat_id, "⏳ در انتظار تأیید:", kb)


def show_pending_detail(chat_id, user_id):
    e = find_expert_by_id(user_id)
    if not e:
        admin_send_message(chat_id, "پیدا نشد.", kb_admin())
        return
    
    txt = ADM_NEW_EXPERT + "\n\n"
    txt += "👤 نام: " + e.get("name", "?") + "\n"
    txt += "📞 تلفن: " + e.get("phone", "?") + "\n"
    txt += "📂 دسته: " + e.get("category", "?") + "\n"
    txt += "🔧 زیرتخصص: " + "، ".join(e.get("sub_specialties", [])) + "\n"
    txt += "📍 محدوده: " + e.get("area", "?") + "\n"
    
    kb = {"inline_keyboard": [
        [{"text": ADM_APPROVE, "callback_data": "adm:appr:" + str(user_id)},
         {"text": ADM_REJECT, "callback_data": "adm:rej:" + str(user_id)}],
        [{"text": ADM_BACK, "callback_data": "adm:pendinglist"}]
    ]}
    admin_send_message(chat_id, txt, kb)


def approve_expert(user_id, chat_id):
    update_expert_field(user_id, "status", "approved")
    admin_send_message(chat_id, ADM_APPROVED_OK, kb_admin())
    # اطلاع به ربات اصلی
    try:
        from api import send_message
        send_message(user_id, "🎉 تبریک! ثبت‌نام شما تأیید شد.")
    except:
        pass


def reject_expert(user_id, chat_id):
    update_expert_field(user_id, "status", "rejected")
    admin_send_message(chat_id, ADM_REJECTED_OK, kb_admin())
    try:
        from api import send_message
        send_message(user_id, "متأسفانه ثبت‌نام شما تأیید نشد.")
    except:
        pass


# ==================== لیست متخصصین ====================
def show_experts_list(chat_id):
    experts = [e for e in load_experts() if e.get("status", "approved") == "approved"]
    if not experts:
        admin_send_message(chat_id, ADM_NO_EXPERT, kb_admin())
        return
    
    kb = {"inline_keyboard": []}
    for i, e in enumerate(experts[:15], 1):
        star = "⭐" if e.get("is_premium") else ""
        stat = "✅" if e.get("active", True) else "❌"
        label = "{}. {} {} {}".format(i, stat, star, e.get("name", "?"))
        kb["inline_keyboard"].append([
            {"text": label, "callback_data": "adm:exp:" + str(e["user_id"])}
        ])
    admin_send_message(chat_id, "👥 متخصصین:", kb)


def show_expert_detail(chat_id, expert_id):
    e = find_expert_by_id(expert_id)
    if not e:
        admin_send_message(chat_id, "پیدا نشد.", kb_admin())
        return
    
    txt = "👤 جزئیات متخصص:\n\n"
    txt += "👤 نام: " + e.get("name", "?") + "\n"
    txt += "📞 تلفن: " + e.get("phone", "?") + "\n"
    txt += "📂 دسته: " + e.get("category", "?") + "\n"
    txt += "🔧 زیرتخصص: " + "، ".join(e.get("sub_specialties", [])) + "\n"
    txt += "📍 محدوده: " + e.get("area", "?") + "\n"
    txt += "📈 تعداد معرفی: " + str(e.get("referral_count", 0)) + "\n"
    txt += "💰 موجودی: " + "{:,}".format(get_wallet_balance(expert_id)) + " تومان\n"
    status = "✅ فعال" if e.get("active", True) else "❌ غیرفعال"
    txt += "⚙️ " + status + "\n"
    if e.get("is_premium"):
        txt += "⭐ اشتراک ویژه\n"
    
    from keyboards import kb_expert_detail
    kb = kb_expert_detail(expert_id, e.get("active", True), e.get("is_premium", False))
    admin_send_message(chat_id, txt, kb)


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
    admin_send_message(chat_id, ADM_DELETED, kb_admin())


# ==================== آخرین معرفی‌ها ====================
def show_jobs(chat_id):
    jobs = load_jobs()
    if not jobs:
        admin_send_message(chat_id, "هنوز معرفی‌ای انجام نشده.", kb_admin())
        return
    
    txt = "📋 آخرین ۱۰ معرفی:\n\n"
    for j in jobs[-10:][::-1]:
        txt += "🎫 " + j.get("tracking_code", "?") + " | " + j.get("expert_name", "?") + "\n"
    admin_send_message(chat_id, txt, kb_admin())


# ==================== درآمد ====================
def show_revenue(chat_id):
    experts = load_experts()
    total_refs = sum(e.get("referral_count", 0) for e in experts)
    estimated = total_refs * 50000
    
    txt = "💰 درآمد:\n\n"
    txt += "📈 کل معرفی‌ها: " + str(total_refs) + "\n"
    txt += "💵 درآمد تخمینی: " + "{:,}".format(estimated) + " تومان\n"
    admin_send_message(chat_id, txt, kb_admin())


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
    
    from keyboards import kb_operators
    admin_send_message(chat_id, txt, kb_operators())


def show_remove_operator(chat_id):
    operators = get_operators()
    if not operators:
        admin_send_message(chat_id, ADM_NO_OPERATOR, kb_admin())
        return
    kb = {"inline_keyboard": []}
    for op in operators:
        kb["inline_keyboard"].append([
            {"text": str(op), "callback_data": "adm:rmopid:" + str(op)}
        ])
    kb["inline_keyboard"].append([
        {"text": ADM_BACK, "callback_data": "adm:backmain"}
    ])
    admin_send_message(chat_id, "روی مدیر مورد نظر بزنید:", kb)


# ==================== تغییر رمز ====================
def ask_change_password(chat_id, user_id):
    admin_user_states[user_id] = {"step": "adm_change_new", "data": {}}
    admin_send_message(chat_id, ADM_ENTER_NEW_PASS, kb_back())


# ==================== حلقه اصلی ربات ادمین ====================
def run_admin_bot():
    """حلقه اصلی ربات ادمین (توی thread جداگانه اجرا می‌شه)"""
    print("[ADMIN] Starting admin bot...")
    
    try:
        admin_delete_webhook()
        print("[ADMIN] Webhook deleted")
    except:
        pass
    
    me = admin_get_me()
    if me:
        print("[ADMIN] Bot username:", me.get("username", "?"))
    
    try:
        admin_clear_old_updates()
        print("[ADMIN] Old updates cleared")
    except:
        pass
    
    offset = None
    fail_count = 0
    
    while True:
        try:
            updates = admin_get_updates(offset)
            fail_count = 0
            
            if updates.get("ok") and updates.get("result"):
                for u in updates["result"]:
                    offset = u["update_id"] + 1
                    try:
                        if "message" in u:
                            handle_admin_message(u["message"])
                        elif "callback_query" in u:
                            handle_admin_callback(u["callback_query"])
                    except Exception as ex:
                        print("[ADMIN Handler]", str(ex)[:100])
        
        except Exception as ex:
            fail_count += 1
            print("[ADMIN Loop]", str(fail_count), str(ex)[:100])
            if fail_count > 5:
                time.sleep(30)
                fail_count = 0
            else:
                time.sleep(10)
            continue
        
        time.sleep(2)
