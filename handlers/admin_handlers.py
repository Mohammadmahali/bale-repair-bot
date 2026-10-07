# ==================== هندلرهای پنل ادمین ====================
import time
from config import SUPER_ADMIN
from texts import (
    ADM_TITLE, ADM_ASK_PASS, ADM_WRONG_PASS, ADM_NOT_AUTH,
    ADM_STATS, ADM_EXPERTS, ADM_PENDING, ADM_JOBS, ADM_REVENUE,
    ADM_OPERATORS, ADM_CHANGE_PASS, ADM_EXIT, ADM_BACK,
    ADM_SET_PASS_FIRST, ADM_ENTER_NEW_PASS, ADM_ENTER_AGAIN,
    ADM_PASS_MISMATCH, ADM_PASS_SHORT, ADM_PASS_SET_OK,
    ADM_ASK_OP_ID, ADM_OP_ADDED, ADM_NO_OPERATOR,
    BTN_BACK, USE_MENU, INVALID_INPUT,
)
from keyboards import kb_admin, kb_back, kb_main, kb_operators
from api import send_message
from db import (
    get_operators, add_operator, remove_operator,
    get_user_password, set_user_password,
)


def is_super_admin(user_id):
    return user_id == SUPER_ADMIN


def is_admin(user_id):
    if user_id == SUPER_ADMIN:
        return True
    return user_id in get_operators()


def is_authed_admin(user_id, admin_sessions):
    return user_id in admin_sessions and is_admin(user_id)


def handle_admin_command(chat_id, user_id, sessions, admin_sessions):
    """هندل /admin"""
    if not is_admin(user_id):
        send_message(chat_id, ADM_NOT_AUTH)
        return
    
    if is_authed_admin(user_id, admin_sessions):
        send_message(chat_id, ADM_TITLE, kb_admin())
        return
    
    pw = get_user_password(user_id)
    if pw is None:
        sessions[user_id] = {"step": "adm_set_pass", "data": {}}
        send_message(chat_id, ADM_SET_PASS_FIRST, kb_back())
    else:
        sessions[user_id] = {"step": "adm_password", "data": {}}
        send_message(chat_id, ADM_ASK_PASS, kb_back())


def continue_admin(chat_id, user_id, text, sessions, admin_sessions):
    """ادامه فرآیند پنل ادمین"""
    if user_id not in sessions:
        return False
    
    session = sessions[user_id]
    step = session["step"]
    data = session["data"]
    
    # ===== رمز اول بار =====
    if step == "adm_set_pass":
        if len(text) < 4:
            send_message(chat_id, ADM_PASS_SHORT, kb_back())
            return True
        data["new_pass"] = text
        session["step"] = "adm_set_pass_confirm"
        send_message(chat_id, ADM_ENTER_AGAIN, kb_back())
        return True
    
    if step == "adm_set_pass_confirm":
        if text != data.get("new_pass"):
            session["step"] = "adm_set_pass"
            data["new_pass"] = ""
            send_message(chat_id, ADM_PASS_MISMATCH, kb_back())
            return True
        set_user_password(user_id, text)
        sessions.pop(user_id, None)
        admin_sessions.add(user_id)
        send_message(chat_id, ADM_PASS_SET_OK)
        send_message(chat_id, ADM_TITLE, kb_admin())
        return True
    
    # ===== ورود با رمز =====
    if step == "adm_password":
        pw = get_user_password(user_id)
        if text == pw:
            admin_sessions.add(user_id)
            sessions.pop(user_id, None)
            send_message(chat_id, ADM_TITLE, kb_admin())
        else:
            send_message(chat_id, ADM_WRONG_PASS, kb_back())
        return True
    
    # ===== تغییر رمز =====
    if step == "adm_change_new":
        if len(text) < 4:
            send_message(chat_id, ADM_PASS_SHORT, kb_back())
            return True
        data["new_pass"] = text
        session["step"] = "adm_change_confirm"
        send_message(chat_id, ADM_ENTER_AGAIN, kb_back())
        return True
    
    if step == "adm_change_confirm":
        if text != data.get("new_pass"):
            session["step"] = "adm_change_new"
            data["new_pass"] = ""
            send_message(chat_id, ADM_PASS_MISMATCH, kb_back())
            return True
        set_user_password(user_id, text)
        sessions.pop(user_id, None)
        send_message(chat_id, ADM_PASS_SET_OK, kb_admin())
        return True
    
    # ===== افزودن اپراتور =====
    if step == "adm_add_op":
        try:
            new_id = int(text.strip())
            add_operator(new_id)
            sessions.pop(user_id, None)
            send_message(chat_id, ADM_OP_ADDED, kb_admin())
        except:
            send_message(chat_id, INVALID_INPUT, kb_back())
        return True
    
    if text == BTN_BACK:
        sessions.pop(user_id, None)
        send_message(chat_id, USE_MENU, kb_main())
        return True
    
    return False


def handle_admin_callback(chat_id, user_id, data, admin_sessions):
    """هندل callback های ادمین"""
    if not is_authed_admin(user_id, admin_sessions):
        return False
    
    parts = data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    
    if action == "exp":
        from admin import show_expert_detail
        show_expert_detail(chat_id, int(parts[2]))
        return True
    elif action == "tog":
        from admin import toggle_active
        toggle_active(int(parts[2]), chat_id)
        return True
    elif action == "prem":
        from admin import toggle_premium
        toggle_premium(int(parts[2]), chat_id)
        return True
    elif action == "del":
        from admin import remove_expert
        remove_expert(int(parts[2]), chat_id)
        return True
    elif action == "back":
        from admin import show_experts_list
        show_experts_list(chat_id)
        return True
    elif action == "backmain":
        send_message(chat_id, ADM_TITLE, kb_admin())
        return True
    elif action == "pendinglist":
        from admin import show_pending_list
        show_pending_list(chat_id)
        return True
    elif action == "viewp":
        from admin import show_pending_detail
        show_pending_detail(chat_id, int(parts[2]))
        return True
    elif action == "appr":
        from admin import approve_expert
        approve_expert(int(parts[2]), chat_id)
        return True
    elif action == "rej":
        from admin import reject_expert
        reject_expert(int(parts[2]), chat_id)
        return True
    elif action == "rmopid":
        if not is_super_admin(user_id):
            return False
        remove_operator(int(parts[2]))
        send_message(chat_id, "حذف شد.", kb_admin())
        return True
    
    return False
