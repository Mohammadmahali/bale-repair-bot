# ==================== ربات اتصال متخصصین - فایل اصلی ====================
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


# ==================== شروع ربات ادمین ====================
def start_admin_bot_thread():
    try:
        from admin_bot import run_admin_bot
        run_admin_bot()
    except Exception as ex:
        print("[ADMIN THREAD ERROR]", str(ex)[:100])


threading.Thread(target=start_admin_bot_thread, daemon=True).start()


# ==================== Import ها ====================
from config import SUPER_ADMIN, TOKEN, ADMIN_TOKEN
from api import (
    send_message, answer_callback, get_me,
    get_updates, delete_webhook, clear_old_updates,
)
from keyboards import (
    kb_main, kb_profile_location_send,
    kb_device_log_menu,
)
from texts import (
    WELCOME, BTN_REGISTER, BTN_SEARCH_SIMPLE, BTN_SEARCH_ADVANCED,
    BTN_EXPERTS_LIST, BTN_MY_PROFILE, BTN_FEEDBACK, BTN_SHOP_STATUS,
    USE_MENU, YES, NO, SHOP_ACTIVE, SHOP_CLOSED_TEMP, SHOP_CLOSED_PERM,
    BTN_WALLET, BTN_CHARGE_WALLET,
    PROFILE_LOCATION_SAVED,
    BTN_BACK,
    BTN_DEVICE_LOG, BTN_ADD_DEFECT, BTN_VIEW_DEVICE_LOGS,
    BTN_MY_DEVICE_LOGS,
    SEC_BLOCKED_PERMANENT, SEC_RATE_LIMIT,
)

# Handlers
from handlers.start import handle_start, handle_experts_list, handle_feedback
from handlers.register import (
    start_registration, continue_registration, handle_location as reg_location,
)
from handlers.search import (
    start_search, continue_search, handle_location as search_location,
    handle_pick_expert, handle_city_fuzzy_callback, handle_city_multiple_callback,
)
from handlers.profile import show_profile, handle_profile_location
from handlers.wallet import (
    show_wallet, start_charge, handle_amount, handle_receipt,
)
from handlers.rating import (
    start_rating, handle_rating_callback, check_followups,
    handle_comment_choice, handle_comment_name_choice, handle_comment_text,
)
from handlers.shop_status import (
    show_shop_status, start_temp_close, continue_shop_close,
    set_permanent_close, set_shop_active, check_shop_reactivations,
)
from handlers.feedback import handle_feedback as do_feedback
from handlers.device_log import (
    show_device_log_menu, start_add_defect, continue_add_defect,
    show_logs_for_job, show_my_device_logs,
    start_edit_log, continue_edit_log, do_delete_log,
)
from handlers.security import (
    check_user_access, check_suspicious_text, check_rate_limit,
)
from handlers.retention import check_retention

# DB
from db import (
    load_experts, save_experts, find_expert_by_id,
    get_pending_job, add_message,
)


# ==================== State های سراسری ====================
sessions = {}
search_modes = {}


# ==================== هندل پیام ====================
def handle_message(msg):
    chat_id = msg.get("chat", {}).get("id")
    user_id = msg.get("from", {}).get("id")
    text = msg.get("text", "")
    location = msg.get("location")

    print(">>>", user_id, text[:30].encode("ascii", "replace").decode())

    # ===== امنیت: چک مسدود بودن =====
    if not check_user_access(chat_id, user_id):
        return

    # ===== امنیت: Rate limit =====
    if not check_rate_limit(chat_id, user_id, max_count=15, window_seconds=60):
        send_message(chat_id, SEC_RATE_LIMIT)
        return

    # ===== امنیت: متن مشکوک =====
    if text and not check_suspicious_text(chat_id, user_id, text):
        return

    # ===== عکس (رسید کیف پول) =====
    if "photo" in msg:
        photos = msg.get("photo", [])
        if photos:
            message_id = msg.get("message_id")
            file_id = photos[-1].get("file_id")
            if user_id in sessions and sessions[user_id].get("step") == "wallet_receipt":
                handle_receipt(chat_id, user_id, message_id, sessions, file_id)
                return
        return

    # ===== لوکیشن =====
    if location:
        if user_id in sessions and sessions[user_id].get("step") == "profile_location":
            handle_profile_location(chat_id, user_id, location)
            sessions.pop(user_id, None)
            send_message(chat_id, PROFILE_LOCATION_SAVED, kb_main())
            return
        if reg_location(chat_id, user_id, location, sessions):
            return
        if search_location(chat_id, user_id, location, sessions):
            return
        return

    # ===== /start =====
    if text.startswith("/start"):
        handle_start(chat_id, user_id, text, sessions)
        return

    # ===== اگه توی state خاصی هست =====
    if user_id in sessions:
        step = sessions[user_id].get("step", "")

        # ===== امتیازدهی =====
        if "rating" in sessions[user_id]:
            rating_data = sessions[user_id].get("rating", {})
            rstep = rating_data.get("step")

            if rstep == "ask_comment_text":
                if handle_comment_text(chat_id, user_id, text, sessions):
                    return
            if rstep == "ask_name":
                send_message(chat_id, "لطفاً از دکمه‌های بالا استفاده کنید.", kb_main())
                return
            if rstep == "ask_comment":
                send_message(chat_id, "لطفاً از دکمه‌های بالا استفاده کنید.", kb_main())
                return
            send_message(chat_id, "لطفاً از دکمه‌های ⭐ استفاده کنید یا بازگشت بزنید.", kb_main())
            return

        # ===== لاگ عیوب =====
        if step in ["devlog_job_code", "devlog_device", "devlog_defect"]:
            if continue_add_defect(chat_id, user_id, text, sessions):
                return

        if step == "devlog_edit":
            if continue_edit_log(chat_id, user_id, text, sessions):
                return

        # ===== لوکیشن پروفایل =====
        if step == "profile_location":
            if text == BTN_BACK:
                sessions.pop(user_id, None)
                send_message(chat_id, "لغو شد.", kb_main())
                return
            send_message(chat_id, "لطفاً موقعیت مکانی خود را ارسال کنید.", kb_profile_location_send())
            return

        # ===== کیف پول =====
        if step == "wallet_amount":
            if text == BTN_BACK:
                sessions.pop(user_id, None)
                show_wallet(chat_id, user_id)
                return
            if handle_amount(chat_id, user_id, text, sessions):
                return

        if step == "wallet_receipt":
            if text == BTN_BACK:
                sessions.pop(user_id, None)
                send_message(chat_id, "لغو شد.", kb_main())
                return
            send_message(chat_id, "لطفاً عکس رسید را ارسال کنید.", kb_back())
            return

        # ===== ثبت‌نام =====
        if step.startswith("reg_"):
            if continue_registration(chat_id, user_id, text, sessions):
                return

        # ===== جستجو =====
        if step.startswith("req_"):
            if continue_search(chat_id, user_id, text, sessions, search_modes):
                return

        # ===== مغازه =====
        if step.startswith("shop_"):
            if continue_shop_close(chat_id, user_id, text, sessions):
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

    # ===== لاگ عیوب =====
    if text == BTN_DEVICE_LOG:
        show_device_log_menu(chat_id, user_id, sessions); return

    if text == BTN_ADD_DEFECT:
        start_add_defect(chat_id, user_id, sessions); return

    if text == BTN_MY_DEVICE_LOGS:
        show_my_device_logs(chat_id, user_id, sessions); return

    if text == BTN_VIEW_DEVICE_LOGS:
        # معادل BTN_MY_DEVICE_LOGS
        show_my_device_logs(chat_id, user_id, sessions); return

    # ===== پیش‌فرض =====
    send_message(chat_id, USE_MENU, kb_main())


# ==================== هندل Callback ====================
def handle_callback(cb):
    cb_id = cb.get("id")
    user_id = cb.get("from", {}).get("id")
    chat_id = cb.get("message", {}).get("chat", {}).get("id")
    data = cb.get("data", "")

    # ===== امنیت: چک مسدود =====
    if not check_user_access(chat_id, user_id):
        answer_callback(cb_id)
        return

    # ===== ثبت لوکیشن =====
    if data == "profile:set_location":
        sessions[user_id] = {"step": "profile_location", "data": {}}
        send_message(chat_id, "لطفاً موقعیت مکانی خود را ارسال کنید:", kb_profile_location_send())
        answer_callback(cb_id)
        return

    # ===== Fuzzy city =====
    if data.startswith("cityfuzzy:"):
        action = data.split(":")[1]
        if handle_city_fuzzy_callback(chat_id, user_id, action, sessions):
            answer_callback(cb_id)
            return
        answer_callback(cb_id, "خطا")
        return

    if data.startswith("citymulti:"):
        choice = data.split(":")[1]
        if handle_city_multiple_callback(chat_id, user_id, choice, sessions):
            answer_callback(cb_id)
            return
        answer_callback(cb_id, "خطا")
        return

    # ===== انتخاب تعمیرکار =====
    if data.startswith("pick:"):
        expert_id = int(data.split(":")[1])
        if handle_pick_expert(chat_id, user_id, expert_id, sessions):
            answer_callback(cb_id, "✅")
            return
        answer_callback(cb_id, "خطا")
        return

    # ===== امتیازدهی (ستاره‌ها) =====
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

    # ===== نظر متنی =====
    if data.startswith("comment:"):
        choice = data.split(":")[1]
        if choice in ["yes", "skip"]:
            if handle_comment_choice(chat_id, user_id, choice, sessions):
                answer_callback(cb_id)
                return
        if choice in ["named", "anon"]:
            if handle_comment_name_choice(chat_id, user_id, choice, sessions):
                answer_callback(cb_id)
                return
        answer_callback(cb_id, "خطا")
        return

    # ===== امتیاز فوری =====
    if data.startswith("rate:"):
        expert_id = int(data.split(":")[1])
        if start_rating(chat_id, user_id, expert_id, sessions, stage=0):
            answer_callback(cb_id)
            return
        answer_callback(cb_id, "خطا")
        return

    # ===== نظرسنجی دوره‌ای =====
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

    # ===== لاگ عیوب =====
    if data.startswith("devlog:"):
        parts = data.split(":")
        sub = parts[1] if len(parts) > 1 else ""

        if sub == "show":
            job_code = parts[2]
            show_logs_for_job(chat_id, user_id, job_code)
            answer_callback(cb_id)
            return

        if sub == "edit":
            log_id = int(parts[2])
            start_edit_log(chat_id, user_id, log_id, sessions)
            answer_callback(cb_id)
            return

        if sub == "del":
            log_id = int(parts[2])
            do_delete_log(chat_id, user_id, log_id)
            answer_callback(cb_id)
            return

        if sub == "cancel":
            answer_callback(cb_id, "لغو شد")
            return

        if sub == "back":
            answer_callback(cb_id)
            send_message(chat_id, USE_MENU, kb_main())
            return

    # ===== وضعیت مغازه =====
    if data == "shop:open":
        set_shop_active(chat_id, user_id)
        answer_callback(cb_id, "✅")
        return

    answer_callback(cb_id)


# ==================== حلقه اصلی ====================
def main():
    print("Bot is starting...")
    print("Token:", TOKEN[:10] + "..." if len(TOKEN) > 10 else TOKEN)

    try:
        from database import init_db, migrate_from_json
        init_db()
        print("Database initialized")
        migrate_from_json()
        print("Migration check done")
        from db import refresh_cities_cache
        count = refresh_cities_cache()
        print("Cities cache loaded: {} cities".format(count))
    except Exception as ex:
        print("DB init error:", str(ex)[:100])

    try:
        delete_webhook()
        print("Webhook deleted")
    except:
        pass

    me = get_me()
    if me:
        import config
        config.BOT_USERNAME = me.get("username", "")
        print("Bot username:", config.BOT_USERNAME)

    try:
        clear_old_updates()
        print("Old updates cleared")
    except Exception as ex:
        print("Clear error:", str(ex)[:100])

    offset = None
    last_followup = 0
    last_retention = 0
    fail_count = 0

    while True:
        try:
            now = time.time()

            # هر ۶۰ ثانیه: نظرسنجی + مغازه
            if now - last_followup > 60:
                try:
                    check_followups()
                    check_shop_reactivations()
                except Exception as ex:
                    print("Followup error:", str(ex)[:100])
                last_followup = now

            # هر ۶۰ ثانیه چک: پاکسازی ۶ ماهه (خودش ۲۴ ساعته چک می‌کنه)
            if now - last_retention > 60:
                try:
                    check_retention()
                except Exception as ex:
                    print("Retention error:", str(ex)[:100])
                last_retention = now

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
