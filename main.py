# ==================== ربات اتصال متخصصین ====================
# فایل اصلی اجرا
import time
import threading
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==================== Health Server ====================
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write("Bot is running".encode('utf-8'))
    
    def log_message(self, format, *args):
        pass


def start_health_server():
    port = int(os.environ.get("PORT", 8080))
    try:
        server = HTTPServer(("0.0.0.0", port), HealthHandler)
        print("Health server on port " + str(port))
        server.serve_forever()
    except Exception as ex:
        print("Health server error:", str(ex)[:100])


threading.Thread(target=start_health_server, daemon=True).start()


# ==================== Import ها ====================
from config import SUPER_ADMIN, TOKEN
from api import (
    send_message, answer_callback, get_me,
    get_updates, delete_webhook, clear_old_updates,
)
from keyboards import kb_main, kb_wallet, kb_profile, kb_back
from texts import (
    WELCOME, BTN_REGISTER, BTN_SEARCH_SIMPLE, BTN_SEARCH_ADVANCED,
    BTN_EXPERTS_LIST, BTN_MY_PROFILE, BTN_FEEDBACK, BTN_SHOP_STATUS,
    USE_MENU, YES, NO, SHOP_ACTIVE, SHOP_CLOSED_TEMP, SHOP_CLOSED_PERM,
    ADM_STATS, ADM_EXPERTS, ADM_PENDING, ADM_JOBS, ADM_REVENUE,
    ADM_OPERATORS, ADM_CHANGE_PASS, ADM_EXIT,
    BTN_WALLET, BTN_CHARGE_WALLET, BTN_BACK,
)

# ==================== Handlers ====================
from handlers.start import handle_start, handle_experts_list, handle_feedback
from handlers.register import (
    start_registration, continue_registration,
    handle_location as reg_location,
)
from handlers.search import (
    start_search, continue_search,
    handle_location as search_location,
    handle_pick_expert,
    handle_city_fuzzy_callback as search_city_fuzzy,
    handle_city_multiple_callback as search_city_multiple,
)
from handlers.profile import show_profile
from handlers.wallet import (
    show_wallet, start_charge, handle_amount, handle_receipt,
)
from handlers.rating import (
    start_rating, handle_rating_callback, check_followups,
)
from handlers.shop_status import (
    show_shop_status, start_temp_close, continue_shop_close,
    set_permanent_close, set_shop_active, check_shop_reactivations,
)
from handlers.feedback import handle_feedback as do_feedback
from handlers.admin_handlers import (
    handle_admin_command, continue_admin, handle_admin_callback,
    is_admin, is_authed_admin,
)

# ==================== Admin ====================
from admin import (
    show_stats, show_pending_list, show_pending_detail,
    show_experts_list, show_expert_detail, show_jobs, show_revenue,
    show_operators, ask_change_password, ask_add_operator,
    approve_wallet_txn, reject_wallet_txn,
)

# ==================== DB ====================
from db import (
    load_experts, save_experts, find_expert_by_id,
    get_pending_job,
)


# ==================== State های سراسری ====================
sessions = {}
admin_sessions = set()
search_modes = {}


# ==================== هندل پیام ====================
def handle_message(msg):
    chat_id = msg.get("chat", {}).get("id")
    user_id = msg.get("from", {}).get("id")
    text = msg.get("text", "")
    location = msg.get("location")
    
    print(">>>", user_id, text[:30].encode("ascii", "replace").decode())
    
    # ===== عکس (رسید کیف پول) =====
    if "photo" in msg:
        photos = msg.get("photo", [])
        if photos:
            if user_id in sessions and sessions[user_id].get("step") == "wallet_receipt":
                message_id = msg.get("message_id")
                handle_receipt(chat_id, user_id, message_id, sessions)
                return
        return
    
    # ===== لوکیشن =====
    if location:
        # لوکیشن از پروفایل
        if user_id in sessions and sessions[user_id].get("step") == "profile_location":
            experts = load_experts()
            for e in experts:
                if e.get("user_id") == user_id:
                    e["lat"] = location.get("latitude")
                    e["lng"] = location.get("longitude")
                    break
            save_experts(experts)
            sessions.pop(user_id, None)
            send_message(chat_id, "✅ موقعیت مکانی ثبت شد.", kb_main())
            return
        
        # لوکیشن در ثبت‌نام
        if reg_location(chat_id, user_id, location, sessions):
            return
        # لوکیشن در جستجو
        if search_location(chat_id, user_id, location, sessions):
            return
        return
    
    # ===== /start =====
    if text.startswith("/start"):
        handle_start(chat_id, user_id, text, sessions)
        return
    
    # ===== /admin =====
    if text == "/admin":
        handle_admin_command(chat_id, user_id, sessions, admin_sessions)
        return
    
    # ===== پنل ادمین =====
    if is_authed_admin(user_id, admin_sessions):
        if text == ADM_EXIT:
            admin_sessions.discard(user_id)
            sessions.pop(user_id, None)
            send_message(chat_id, USE_MENU, kb_main())
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
            ask_change_password(chat_id); return
    
    # ===== State Machine =====
    if user_id in sessions:
        step = sessions[user_id].get("step", "")
        
        # ثبت‌نام
        if step.startswith("reg_"):
            if continue_registration(chat_id, user_id, text, sessions):
                return
        
        # جستجو
        if step.startswith("req_"):
            if continue_search(chat_id, user_id, text, sessions, search_modes):
                return
        
        # ادمین
        if step.startswith("adm_"):
            if continue_admin(chat_id, user_id, text, sessions, admin_sessions):
                return
        
        # تعطیلی مغازه
        if step.startswith("shop_"):
            if continue_shop_close(chat_id, user_id, text, sessions):
                return
        
        # شارژ کیف پول - مبلغ
        if step == "wallet_amount":
            if text == BTN_BACK:
                sessions.pop(user_id, None)
                show_wallet(chat_id, user_id)
                return
            if handle_amount(chat_id, user_id, text, sessions):
                return
        
        # شارژ کیف پول - منتظر عکس
        if step == "wallet_receipt":
            if text == BTN_BACK:
                sessions.pop(user_id, None)
                send_message(chat_id, "لغو شد.", kb_main())
                return
            send_message(chat_id, "لطفاً عکس رسید را ارسال کنید.", kb_back())
            return
    
    # ===== منوی اصلی =====
    if text == BTN_REGISTER:
        start_registration(chat_id, user_id, sessions); return
    
    if text == BTN_SEARCH_SIMPLE:
        start_search(chat_id, user_id, "simple", sessions, search_modes); return
    
    if text == BTN_SEARCH_ADVANCED:
        start_search(chat_id, user_id, "adv", sessions, search_modes); return
    
    if text == BTN_EXPERTS_LIST:
        handle_experts_list(chat_id); return
    
    if text == BTN_MY_PROFILE:
        show_profile(chat_id, user_id); return
    
    if text == BTN_FEEDBACK:
        do_feedback(chat_id); return
    
    if text == BTN_SHOP_STATUS:
        show_shop_status(chat_id, user_id); return
    
    if text == BTN_WALLET:
        show_wallet(chat_id, user_id); return
    
    if text == BTN_CHARGE_WALLET:
        start_charge(chat_id, user_id, sessions); return
    
    # ===== وضعیت مغازه =====
    if text == SHOP_ACTIVE:
        set_shop_active(chat_id, user_id); return
    
    if text == SHOP_CLOSED_TEMP:
        start_temp_close(chat_id, user_id, sessions); return
    
    if text == SHOP_CLOSED_PERM:
        set_permanent_close(chat_id, user_id); return
    
    send_message(chat_id, USE_MENU, kb_main())


# ==================== هندل Callback ====================
def handle_callback(cb):
    cb_id = cb.get("id")
    user_id = cb.get("from", {}).get("id")
    chat_id = cb.get("message", {}).get("chat", {}).get("id")
    data = cb.get("data", "")
    
    # ===== callback ادمین =====
    if data.startswith("adm:"):
        if handle_admin_callback(chat_id, user_id, data, admin_sessions):
            answer_callback(cb_id)
            return
        answer_callback(cb_id, "دسترسی ندارید")
        return
    
    # ===== callback تأیید/رد شارژ کیف پول =====
    if data.startswith("wadm:"):
        if not is_authed_admin(user_id, admin_sessions):
            answer_callback(cb_id, "دسترسی ندارید")
            return
        parts = data.split(":")
        if len(parts) >= 3:
            action = parts[1]
            try:
                txn_id = int(parts[2])
            except:
                answer_callback(cb_id, "خطا")
                return
            if action == "approve":
                approve_wallet_txn(txn_id, chat_id, user_id)
            elif action == "reject":
                reject_wallet_txn(txn_id, chat_id, user_id)
        answer_callback(cb_id)
        return
    
    # ===== callback ثبت لوکیشن از پروفایل =====
    if data == "profile:set_location":
        sessions[user_id] = {"step": "profile_location", "data": {}}
        send_message(
            chat_id,
            "لطفاً موقعیت مکانی خود را ارسال کنید:",
            {"keyboard": [[
                {"text": "📍 ارسال موقعیت من", "request_location": True}
            ], [{"text": BTN_BACK}]], "resize_keyboard": True}
        )
        answer_callback(cb_id)
        return
    
    # ===== callback شهر (Fuzzy) - مشتری =====
    if data.startswith("cityfuzzy:"):
        action = data.split(":")[1]
        if search_city_fuzzy(chat_id, user_id, action, sessions):
            answer_callback(cb_id)
            return
        answer_callback(cb_id, "خطا")
        return
    
    # ===== callback چند شهر =====
    if data.startswith("citymulti:"):
        choice = data.split(":")[1]
        if search_city_multiple(chat_id, user_id, choice, sessions):
            answer_callback(cb_id)
            return
        answer_callback(cb_id, "خطا")
        return
    
    # ===== callback شهر (Fuzzy) - ثبت‌نام =====
    if data.startswith("regfuzzy:"):
        action = data.split(":")[1]
        from handlers.register import handle_city_fuzzy_callback as reg_city_fuzzy
        if reg_city_fuzzy(chat_id, user_id, action, sessions):
            answer_callback(cb_id)
            return
        answer_callback(cb_id, "خطا")
        return
    
    # ===== callback امتیاز ستاره =====
    if data.startswith("crit:"):
        parts = data.split(":")
        if len(parts) == 3:
            criteria_key = parts[1]
            stars = int(parts[2])
            if handle_rating_callback(chat_id, user_id, criteria_key, stars, sessions):
                answer_callback(cb_id, "ثبت شد")
                return
        answer_callback(cb_id, "خطا")
        return
    
    # ===== callback انتخاب تعمیرکار =====
    if data.startswith("pick:"):
        expert_id = int(data.split(":")[1])
        if handle_pick_expert(chat_id, user_id, expert_id, sessions):
            answer_callback(cb_id, "✅")
            return
        answer_callback(cb_id, "خطا")
        return
    
    # ===== callback امتیازدهی اولیه =====
    if data.startswith("rate:"):
        expert_id = int(data.split(":")[1])
        if start_rating(chat_id, user_id, expert_id, sessions, stage=0):
            answer_callback(cb_id)
            return
        answer_callback(cb_id, "خطا")
        return
    
    # ===== callback نظرسنجی دوره‌ای =====
    if data.startswith("frate:"):
        expert_id = int(data.split(":")[1])
        job = get_pending_job(user_id, expert_id)
        if not job:
            answer_callback(cb_id, "پروژه پیدا نشد")
            return
        stage = job.get("stage", 0) + 1
        if start_rating(chat_id, user_id, expert_id, sessions, stage=stage):
            answer_callback(cb_id)
            return
        answer_callback(cb_id, "خطا")
        return
    
    # ===== callback وضعیت مغازه =====
    if data == "shop:open":
        set_shop_active(chat_id, user_id)
        answer_callback(cb_id, "✅")
        return
    
    answer_callback(cb_id)


# ==================== حلقه اصلی ====================
def main():
    print("Bot is starting...")
    
    # راه‌اندازی SQLite
    from database import init_db, migrate_from_json
    init_db()
    print("Database initialized")
    migrate_from_json()
    print("Migration check done")
    
    # حذف Webhook
    try:
        delete_webhook()
        print("Webhook deleted")
    except:
        pass
    
    # اطلاعات ربات
    me = get_me()
    if me:
        import config
        config.BOT_USERNAME = me.get("username", "")
        print("Bot username:", config.BOT_USERNAME)
    
    # پاک کردن پیام‌های قدیمی
    try:
        clear_old_updates()
        print("Old updates cleared")
    except Exception as ex:
        print("Clear error:", str(ex)[:100])
    
    # حلقه اصلی
    offset = None
    last_followup = 0
    fail_count = 0
    
    while True:
        try:
            now = time.time()
            
            if now - last_followup > 60:
                try:
                    check_followups()
                    check_shop_reactivations()
                except Exception as ex:
                    print("Followup error:", str(ex)[:100])
                last_followup = now
            
            updates = get_updates(offset)
            fail_count = 0
            
            if updates.get("ok") and updates.get("result"):
                for u in updates["result"]:
                    offset = u["update_id"] + 1
                    try:
                        if "message" in u:
                            handle_message(u["message"])
                        elif "callback_query" in u:
                            handle_callback(u["callback_query"])
                    except Exception as ex:
                        print("Handler error:", str(ex)[:100])
        
        except Exception as ex:
            fail_count += 1
            print("Main loop error (" + str(fail_count) + "):", str(ex)[:100])
            if fail_count > 5:
                time.sleep(30)
                fail_count = 0
            else:
                time.sleep(10)
            continue
        
        time.sleep(2)


if __name__ == "__main__":
    main()
