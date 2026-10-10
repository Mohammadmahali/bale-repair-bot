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
from keyboards import (
    kb_admin, kb_back, kb_main,
    kb_edit_menu, kb_categories_list, kb_tariffs_list,
    kb_bulk_confirm,
    kb_edit_cities_menu, kb_cities_delete_list, kb_cities_reset_confirm,
    kb_security_menu, kb_blocked_user,
    kb_category_detail, kb_sub_detail,
    kb_broadcast_target, kb_broadcast_cats, kb_broadcast_subs, kb_broadcast_confirm,
)
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
    BTN_EDIT, BTN_EDIT_CATEGORIES, BTN_EDIT_TARIFFS,
    BTN_EDIT_FEEDBACK, BTN_EDIT_CARD, BTN_SAVE, BTN_CANCEL,
    EDIT_MENU_TITLE, EDIT_CATEGORIES_TITLE, EDIT_CATEGORY_ASK_NEW,
    EDIT_CATEGORY_ADDED, EDIT_CATEGORY_EXISTS, EDIT_CATEGORY_ASK_DELETE,
    EDIT_CATEGORY_DELETED, EDIT_TARIFFS_TITLE, EDIT_TARIFF_ASK,
    EDIT_TARIFF_UPDATED, EDIT_TARIFF_INVALID, EDIT_FEEDBACK_ASK,
    EDIT_FEEDBACK_UPDATED, EDIT_CARD_ASK, EDIT_CARD_OWNER_ASK,
    EDIT_CARD_UPDATED, EDIT_SAVED, EDIT_CANCELED,
    BTN_BULK_TARIFF,
    EDIT_BULK_TITLE, EDIT_BULK_ASK, EDIT_BULK_INVALID,
    EDIT_BULK_PREVIEW, EDIT_BULK_DONE, EDIT_BULK_CANCELED,
    BTN_EDIT_CITIES,
    EDIT_CITIES_TITLE, EDIT_CITIES_ASK_NEW,
    EDIT_CITY_ADDED, EDIT_CITY_EXISTS, EDIT_CITY_REMOVED,
    EDIT_CITY_NOT_FOUND, EDIT_CITY_INVALID,
    EDIT_CITIES_LIST_TITLE, EDIT_CITIES_RESET,
    EDIT_CITIES_RESET_OK, EDIT_CITIES_RESET_CONFIRM,
    ADM_SECURITY, ADM_SEC_EVENTS, ADM_SEC_BLOCKED, ADM_SEC_BACK,
    EDIT_CAT_NAME_ASK, EDIT_CAT_NAME_DONE, EDIT_CAT_NAME_EXISTS,
    EDIT_CAT_NAME_NOT_FOUND, EDIT_CAT_NAME_INVALID,
    EDIT_SUB_NAME_ASK, EDIT_SUB_NAME_DONE, EDIT_SUB_NAME_EXISTS,
    EDIT_SUB_NAME_NOT_FOUND, EDIT_SUB_NAME_INVALID,
    BTN_EDIT_CAT_NAME, BTN_EDIT_SUB_NAME,
    BTN_BROADCAST,
    BCAST_TITLE, BCAST_SELECT_TARGET, BCAST_SELECT_CAT, BCAST_SELECT_SUB,
    BCAST_ASK_TEXT, BCAST_TEXT_TOO_LONG, BCAST_TEXT_EMPTY,
    BCAST_PREVIEW, BCAST_NO_RECIPIENTS, BCAST_CANCELED,
    BCAST_SENDING, BCAST_DONE,
    BCAST_TARGET_ALL, BCAST_TARGET_BY_CAT, BCAST_TARGET_BY_SUB,
)
from db import (
    get_operators, add_operator, remove_operator,
    get_user_password, set_user_password,
    find_expert_by_id, delete_expert, update_expert_field,
    get_stats, load_experts, load_jobs,
    get_wallet_balance, approve_wallet_charge, reject_wallet_charge,
    load_admin_config, save_admin_config,
    get_all_categories, get_category_subs, add_category_db,
    remove_category_db, add_sub_db, remove_sub_db,
    rename_category_db, rename_sub_db,
    get_category_by_index, get_sub_by_index,
    get_sub_tariff, set_sub_tariff, get_all_sub_tariffs,
    get_all_cities, add_city_db, remove_city_db,
    reset_cities_db, refresh_cities_cache,
)
from tariffs import preview_bulk, apply_bulk, get_current_tariffs
from handlers.security import (
    show_security_menu, show_security_events,
    show_blocked_users, do_unblock_user,
)
import config


# ==================== State ها ====================
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

    try:
        print("[ADMIN]", user_id, text[:30].encode("ascii", "replace").decode())
    except:
        pass

    if text == "/start":
        handle_admin_start(chat_id, user_id)
        return

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
        if text == ADM_SECURITY:
            show_security_menu(chat_id); return
        if text == ADM_SEC_EVENTS:
            show_security_events(chat_id); return
        if text == ADM_SEC_BLOCKED:
            show_blocked_users(chat_id); return
        if text == ADM_SEC_BACK:
            admin_send_message(chat_id, ADM_TITLE, kb_admin()); return
        if text == BTN_BROADCAST:
            show_broadcast_menu(chat_id, user_id); return
        if text == BTN_EDIT:
            show_edit_menu(chat_id); return
        if text == BTN_EDIT_CATEGORIES:
            show_categories_list(chat_id); return
        if text == BTN_EDIT_TARIFFS:
            show_tariffs_list(chat_id); return
        if text == BTN_BULK_TARIFF:
            start_bulk_edit(chat_id, user_id); return
        if text == BTN_EDIT_CITIES:
            show_cities_menu(chat_id); return
        if text == "➕ افزودن شهر":
            admin_user_states[user_id] = {"step": "city_add", "data": {}}
            admin_send_message(chat_id, EDIT_CITIES_ASK_NEW, kb_back())
            return
        if text == "🗑 حذف شهر":
            show_cities_delete(chat_id, page=0); return
        if text == EDIT_CITIES_RESET:
            admin_send_message(chat_id, EDIT_CITIES_RESET_CONFIRM, kb_cities_reset_confirm())
            return
        if text == BTN_EDIT_FEEDBACK:
            admin_user_states[user_id] = {"step": "edit_feedback", "data": {}}
            admin_send_message(chat_id, EDIT_FEEDBACK_ASK, kb_back())
            return
        if text == BTN_EDIT_CARD:
            admin_user_states[user_id] = {"step": "edit_card_number", "data": {}}
            admin_send_message(chat_id, EDIT_CARD_ASK, kb_back())
            return

    # state machine
    if user_id in admin_user_states:
        state = admin_user_states[user_id]
        step = state["step"]
        data = state["data"]

        if text == BTN_BACK:
            admin_user_states.pop(user_id, None)
            admin_send_message(chat_id, USE_MENU)
            return

        # ===== تنظیم رمز اول =====
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

        # ===== ورود با رمز =====
        if step == "adm_password":
            pw = get_user_password(user_id)
            if text == pw:
                admin_sessions.add(user_id)
                admin_user_states.pop(user_id, None)
                admin_send_message(chat_id, ADM_TITLE, kb_admin())
            else:
                admin_send_message(chat_id, ADM_WRONG_PASS, kb_back())
            return

        # ===== تغییر رمز =====
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

        # ===== افزودن اپراتور =====
        if step == "adm_add_op":
            try:
                new_id = int(text.strip())
                add_operator(new_id)
                admin_user_states.pop(user_id, None)
                admin_send_message(chat_id, ADM_OP_ADDED, kb_admin())
            except:
                admin_send_message(chat_id, INVALID_INPUT, kb_back())
            return

        # ===== ویرایش: افزودن دسته =====
        if step == "edit_cat_add":
            if text in [BTN_CANCEL, BTN_BACK]:
                admin_user_states.pop(user_id, None)
                show_edit_menu(chat_id)
                return
            new_cat = text.strip()
            if not new_cat:
                admin_send_message(chat_id, INVALID_INPUT, kb_back())
                return
            if add_category_db(new_cat):
                admin_send_message(chat_id, "✅ دسته‌بندی «{}» اضافه شد.".format(new_cat), kb_edit_menu())
            else:
                admin_send_message(chat_id, "⚠️ این دسته‌بندی قبلاً وجود داره.", kb_edit_menu())
            admin_user_states.pop(user_id, None)
            return

        # ===== ویرایش: افزودن زیرتخصص =====
        if step == "edit_sub_add":
            if text in [BTN_CANCEL, BTN_BACK]:
                admin_user_states.pop(user_id, None)
                show_edit_menu(chat_id)
                return
            new_sub = text.strip()
            if not new_sub:
                admin_send_message(chat_id, INVALID_INPUT, kb_back())
                return
            cat_idx = data.get("cat_idx", -1)
            cat = get_category_by_index(cat_idx)
            if not cat:
                admin_send_message(chat_id, "دسته پیدا نشد.", kb_edit_menu())
                admin_user_states.pop(user_id, None)
                return
            if add_sub_db(cat, new_sub):
                admin_send_message(chat_id, "✅ زیرتخصص «{}» اضافه شد.".format(new_sub), kb_edit_menu())
            else:
                admin_send_message(chat_id, "⚠️ این زیرتخصص قبلاً وجود داره.", kb_edit_menu())
            admin_user_states.pop(user_id, None)
            return

        # ===== ویرایش نام گروه =====
        if step == "rename_cat":
            if text in [BTN_CANCEL, BTN_BACK]:
                cat_idx = data.get("cat_idx", -1)
                admin_user_states.pop(user_id, None)
                show_category_detail(chat_id, cat_idx)
                return
            old_name = data.get("old_name", "")
            new_name = text.strip()
            if not new_name or len(new_name) < 2 or len(new_name) > 60:
                admin_send_message(chat_id, EDIT_CAT_NAME_INVALID, kb_back())
                return
            if rename_category_db(old_name, new_name):
                admin_user_states.pop(user_id, None)
                admin_send_message(
                    chat_id,
                    EDIT_CAT_NAME_DONE.format(old=old_name, new=new_name),
                    kb_edit_menu()
                )
            else:
                admin_send_message(chat_id, EDIT_CAT_NAME_EXISTS.format(name=new_name), kb_back())
            return

        # ===== ویرایش نام زیرتخصص =====
        if step == "rename_sub":
            if text in [BTN_CANCEL, BTN_BACK]:
                cat_idx = data.get("cat_idx", -1)
                admin_user_states.pop(user_id, None)
                show_category_detail(chat_id, cat_idx)
                return
            old_name = data.get("old_name", "")
            cat_name = data.get("cat_name", "")
            new_name = text.strip()
            if not new_name or len(new_name) < 2 or len(new_name) > 100:
                admin_send_message(chat_id, EDIT_SUB_NAME_INVALID, kb_back())
                return
            if rename_sub_db(cat_name, old_name, new_name):
                admin_user_states.pop(user_id, None)
                admin_send_message(
                    chat_id,
                    EDIT_SUB_NAME_DONE.format(old=old_name, new=new_name),
                    kb_edit_menu()
                )
            else:
                admin_send_message(chat_id, EDIT_SUB_NAME_EXISTS.format(name=new_name), kb_back())
            return

        # ===== تعرفه زیرتخصص =====
        if step == "edit_sub_tariff":
            if text in [BTN_CANCEL, BTN_BACK]:
                admin_user_states.pop(user_id, None)
                show_edit_menu(chat_id)
                return
            try:
                amount = int(text.strip().replace(",", "").replace("،", ""))
                if amount < 10000 or amount > 10000000:
                    raise ValueError
            except:
                admin_send_message(chat_id, "❌ مبلغ نامعتبر.", kb_back())
                return
            sub = data.get("sub", "")
            if sub:
                set_sub_tariff(sub, amount)
                admin_send_message(
                    chat_id,
                    "✅ تعرفه «{}» به {:,} تومان بروزرسانی شد.".format(sub, amount),
                    kb_edit_menu()
                )
            else:
                admin_send_message(chat_id, "خطا در ذخیره.", kb_edit_menu())
            admin_user_states.pop(user_id, None)
            return

        # ===== ویرایش آیدی نظرات =====
        if step == "edit_feedback":
            if text in [BTN_CANCEL, BTN_BACK]:
                admin_user_states.pop(user_id, None)
                show_edit_menu(chat_id)
                return
            new_id = text.strip()
            if not new_id.startswith("@"):
                new_id = "@" + new_id
            cfg = load_admin_config()
            cfg["feedback_id"] = new_id
            save_admin_config(cfg)
            admin_user_states.pop(user_id, None)
            admin_send_message(chat_id, EDIT_FEEDBACK_UPDATED.format(id=new_id), kb_edit_menu())
            return

        # ===== ویرایش شماره کارت =====
        if step == "edit_card_number":
            if text in [BTN_CANCEL, BTN_BACK]:
                admin_user_states.pop(user_id, None)
                show_edit_menu(chat_id)
                return
            data["new_card"] = text.strip()
            state["step"] = "edit_card_owner"
            admin_send_message(chat_id, EDIT_CARD_OWNER_ASK, kb_back())
            return

        if step == "edit_card_owner":
            if text in [BTN_CANCEL, BTN_BACK]:
                admin_user_states.pop(user_id, None)
                show_edit_menu(chat_id)
                return
            new_owner = text.strip()
            new_card = data.get("new_card", "")
            cfg = load_admin_config()
            cfg["card_number"] = new_card
            cfg["card_owner"] = new_owner
            save_admin_config(cfg)
            admin_user_states.pop(user_id, None)
            admin_send_message(chat_id, EDIT_CARD_UPDATED.format(card=new_card, owner=new_owner), kb_edit_menu())
            return

        # ===== ویرایش کلی تعرفه =====
        if step == "edit_bulk_percent":
            if text in [BTN_CANCEL, BTN_BACK]:
                admin_user_states.pop(user_id, None)
                show_edit_menu(chat_id)
                return
            try:
                percent = float(text.strip().replace("٪", "").replace("%", "").replace("،", ""))
                if percent < -50 or percent > 100:
                    raise ValueError
            except:
                admin_send_message(chat_id, EDIT_BULK_INVALID, kb_back())
                return

            data["percent"] = percent
            preview = preview_bulk(percent)

            ex1 = preview["examples"][0] if len(preview["examples"]) > 0 else ("—", 0, 0)
            ex2 = preview["examples"][1] if len(preview["examples"]) > 1 else ("—", 0, 0)

            msg = EDIT_BULK_PREVIEW.format(
                count=preview["count"],
                percent=percent,
                ex_old1="{:,}".format(ex1[1]),
                ex_new1="{:,}".format(ex1[2]),
                ex_old2="{:,}".format(ex2[1]),
                ex_new2="{:,}".format(ex2[2]),
            )
            admin_send_message(chat_id, msg, kb_bulk_confirm())
            state["step"] = "edit_bulk_confirm"
            return

        if step == "edit_bulk_confirm":
            admin_send_message(chat_id, "لطفاً از دکمه‌های بالا استفاده کنید.", kb_bulk_confirm())
            return

        # ===== افزودن شهر =====
        if step == "city_add":
            if text in [BTN_CANCEL, BTN_BACK]:
                admin_user_states.pop(user_id, None)
                show_cities_menu(chat_id)
                return
            name = text.strip()
            if not name or len(name) < 2 or len(name) > 30:
                admin_send_message(chat_id, EDIT_CITY_INVALID, kb_back())
                return
            if add_city_db(name):
                refresh_cities_cache()
                count = len(get_all_cities())
                admin_user_states.pop(user_id, None)
                admin_send_message(
                    chat_id,
                    EDIT_CITY_ADDED.format(city=name) + "\n\n📊 تعداد فعلی: " + str(count),
                    kb_edit_cities_menu()
                )
            else:
                admin_send_message(chat_id, EDIT_CITY_EXISTS.format(city=name), kb_back())
            return

        # ===== پیام گروهی: دریافت متن =====
        if step == "broadcast_text":
            if text in [BTN_CANCEL, BTN_BACK]:
                admin_user_states.pop(user_id, None)
                admin_send_message(chat_id, BCAST_CANCELED, kb_admin())
                return
            msg_text = text.strip()
            if not msg_text:
                admin_send_message(chat_id, BCAST_TEXT_EMPTY, kb_back())
                return
            if len(msg_text) > 2000:
                admin_send_message(chat_id, BCAST_TEXT_TOO_LONG, kb_back())
                return

            # تعداد گیرندگان
            recipients = _get_broadcast_recipients(data)
            if not recipients:
                admin_user_states.pop(user_id, None)
                admin_send_message(chat_id, BCAST_NO_RECIPIENTS, kb_admin())
                return

            data["text"] = msg_text
            target_label = _get_target_label(data)

            preview = BCAST_PREVIEW.format(
                count=len(recipients),
                target=target_label,
                text=msg_text
            )
            state["step"] = "broadcast_confirm"
            admin_send_message(chat_id, preview, kb_broadcast_confirm())
            return

        if step == "broadcast_confirm":
            admin_send_message(chat_id, "لطفاً از دکمه‌های بالا استفاده کنید.", kb_broadcast_confirm())
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

    try:
        print("[ADMIN CB]", user_id, data[:40])
    except:
        pass

    if not is_authed_admin(user_id):
        admin_answer_callback(cb_id, "دسترسی ندارید")
        return

    parts = data.split(":")
    action = parts[1] if len(parts) > 1 else ""

    # ===== شارژ کیف پول =====
    if data.startswith("wadm:"):
        sub_action = parts[1]
        txn_id = int(parts[2])
        if sub_action == "approve":
            from admin import approve_wallet_txn
            approve_wallet_txn(txn_id, chat_id, user_id)
        elif sub_action == "reject":
            from admin import reject_wallet_txn
            reject_wallet_txn(txn_id, chat_id, user_id)
        admin_answer_callback(cb_id)
        return

    # ===== ویرایش کلی تعرفه =====
    if data == "bulk:confirm":
        state = admin_user_states.get(user_id, {})
        percent = state.get("data", {}).get("percent")
        if percent is None:
            admin_answer_callback(cb_id, "خطا: درصد پیدا نشد")
            return
        count = apply_bulk(percent)
        admin_user_states.pop(user_id, None)
        admin_answer_callback(cb_id, "✅ اعمال شد")
        admin_send_message(
            chat_id,
            EDIT_BULK_DONE.format(count=count, percent=percent),
            kb_edit_menu()
        )
        return

    if data == "bulk:cancel":
        admin_user_states.pop(user_id, None)
        admin_answer_callback(cb_id, "❌ لغو شد")
        admin_send_message(chat_id, EDIT_BULK_CANCELED, kb_edit_menu())
        return

    # ===== مدیریت شهرها =====
    if data.startswith("adm:citypage:"):
        page = int(parts[2])
        admin_answer_callback(cb_id)
        show_cities_delete(chat_id, page)
        return

    if data.startswith("adm:citydel:"):
        city_name = parts[2]
        if remove_city_db(city_name):
            refresh_cities_cache()
            count = len(get_all_cities())
            admin_answer_callback(cb_id, "حذف شد")
            admin_send_message(
                chat_id,
                EDIT_CITY_REMOVED.format(city=city_name) + "\n\n📊 تعداد فعلی: " + str(count),
                kb_cities_delete_list(page=0)
            )
        else:
            admin_answer_callback(cb_id, "خطا")
            admin_send_message(chat_id, EDIT_CITY_NOT_FOUND.format(city=city_name), kb_edit_cities_menu())
        return

    if data == "adm:cityreset:yes":
        reset_cities_db()
        refresh_cities_cache()
        admin_answer_callback(cb_id, "✅ انجام شد")
        admin_send_message(chat_id, EDIT_CITIES_RESET_OK, kb_edit_cities_menu())
        return

    if data == "adm:cityreset:no":
        admin_answer_callback(cb_id, "لغو شد")
        admin_send_message(chat_id, "لغو شد.", kb_edit_cities_menu())
        return

    # ===== رفع مسدودی =====
    if data.startswith("adm:unblock:"):
        target = int(parts[2])
        do_unblock_user(chat_id, target)
        admin_answer_callback(cb_id, "✅")
        return

    # ===== پیام گروهی =====
    if data == "bcast:back":
        admin_answer_callback(cb_id)
        admin_user_states.pop(user_id, None)
        admin_send_message(chat_id, ADM_TITLE, kb_admin())
        return

    if data == "bcast:all":
        admin_answer_callback(cb_id)
        admin_user_states[user_id] = {
            "step": "broadcast_text",
            "data": {"target_type": "all"}
        }
        admin_send_message(chat_id, BCAST_ASK_TEXT, kb_back())
        return

    if data == "bcast:cats":
        admin_answer_callback(cb_id)
        admin_send_message(chat_id, BCAST_SELECT_CAT, kb_broadcast_cats())
        return

    if data == "bcast:subs":
        admin_answer_callback(cb_id)
        admin_send_message(chat_id, BCAST_SELECT_CAT, kb_broadcast_cats())
        return

    if data.startswith("bcast:cat:"):
        cat_idx = int(parts[2])
        cat = get_category_by_index(cat_idx)
        if not cat:
            admin_answer_callback(cb_id, "پیدا نشد")
            return
        admin_answer_callback(cb_id)
        admin_user_states[user_id] = {
            "step": "broadcast_text",
            "data": {"target_type": "category", "target_value": cat}
        }
        admin_send_message(chat_id, BCAST_ASK_TEXT, kb_back())
        return

    if data.startswith("bcast:sub:"):
        cat_idx = int(parts[2])
        sub_idx = int(parts[3])
        cat = get_category_by_index(cat_idx)
        sub = get_sub_by_index(cat, sub_idx)
        if not cat or not sub:
            admin_answer_callback(cb_id, "پیدا نشد")
            return
        admin_answer_callback(cb_id)
        admin_user_states[user_id] = {
            "step": "broadcast_text",
            "data": {"target_type": "sub", "target_value": cat, "sub_value": sub}
        }
        admin_send_message(chat_id, BCAST_ASK_TEXT, kb_back())
        return

    if data == "bcast:confirm":
        state = admin_user_states.get(user_id, {})
        bdata = state.get("data", {})
        msg_text = bdata.get("text", "")
        if not msg_text:
            admin_answer_callback(cb_id, "خطا: متن پیدا نشد")
            return

        recipients = _get_broadcast_recipients(bdata)
        if not recipients:
            admin_user_states.pop(user_id, None)
            admin_answer_callback(cb_id, "گیرنده‌ای نیست")
            admin_send_message(chat_id, BCAST_NO_RECIPIENTS, kb_admin())
            return

        admin_answer_callback(cb_id, "شروع ارسال")
        admin_user_states.pop(user_id, None)

        # محاسبه زمان تقریبی
        seconds = int(len(recipients) * 0.5)

        admin_send_message(
            chat_id,
            BCAST_SENDING.format(count=len(recipients), seconds=seconds),
            kb_admin()
        )

        # ارسال در thread جداگانه
        t = threading.Thread(
            target=_send_broadcast,
            args=(chat_id, recipients, msg_text),
            daemon=True
        )
        t.start()
        return

    if data == "bcast:cancel":
        admin_user_states.pop(user_id, None)
        admin_answer_callback(cb_id, "لغو شد")
        admin_send_message(chat_id, BCAST_CANCELED, kb_admin())
        return

    # ===== سایر callbacks =====
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
        elif action == "backedit":
            show_edit_menu(chat_id)
        elif action == "editcatlist":
            show_categories_list(chat_id)
        elif action == "editcat":
            show_category_detail(chat_id, int(parts[2]))
        elif action == "addcat":
            admin_user_states[user_id] = {"step": "edit_cat_add", "data": {}}
            admin_send_message(chat_id, "📂 نام دسته‌بندی جدید را وارد کنید:", kb_back())
        elif action == "rencat":
            cat_idx = int(parts[2])
            cat = get_category_by_index(cat_idx)
            if not cat:
                admin_answer_callback(cb_id, "پیدا نشد")
                return
            admin_user_states[user_id] = {
                "step": "rename_cat",
                "data": {"cat_idx": cat_idx, "old_name": cat}
            }
            admin_send_message(
                chat_id,
                EDIT_CAT_NAME_ASK.format(old=cat),
                kb_back()
            )
        elif action == "subdet":
            cat_idx = int(parts[2])
            sub_idx = int(parts[3])
            cat = get_category_by_index(cat_idx)
            sub = get_sub_by_index(cat, sub_idx)
            if not cat or not sub:
                admin_answer_callback(cb_id, "پیدا نشد")
                return
            txt = "📂 گروه: {}\n\n".format(cat)
            txt += "🔧 زیرتخصص: {}\n".format(sub)
            txt += "💰 تعرفه: {:,} تومان".format(get_sub_tariff(sub))
            admin_send_message(chat_id, txt, kb_sub_detail(cat_idx, sub_idx))
        elif action == "rensub":
            cat_idx = int(parts[2])
            sub_idx = int(parts[3])
            cat = get_category_by_index(cat_idx)
            sub = get_sub_by_index(cat, sub_idx)
            if not cat or not sub:
                admin_answer_callback(cb_id, "پیدا نشد")
                return
            admin_user_states[user_id] = {
                "step": "rename_sub",
                "data": {"cat_idx": cat_idx, "cat_name": cat, "old_name": sub}
            }
            admin_send_message(
                chat_id,
                EDIT_SUB_NAME_ASK.format(old=sub),
                kb_back()
            )
        elif action == "addsub":
            cat_idx = int(parts[2])
            admin_user_states[user_id] = {"step": "edit_sub_add", "data": {"cat_idx": cat_idx}}
            admin_send_message(chat_id, "📝 نام زیرتخصص جدید را وارد کنید:", kb_back())
        elif action == "delsublist":
            show_subs_delete_list(chat_id, int(parts[2]))
        elif action == "delsubid":
            cat_idx = int(parts[2])
            sub_idx = int(parts[3])
            cat = get_category_by_index(cat_idx)
            sub = get_sub_by_index(cat, sub_idx)
            if cat and sub:
                remove_sub_db(cat, sub)
                admin_send_message(chat_id, "✅ «{}» حذف شد.".format(sub), kb_edit_menu())
            else:
                admin_send_message(chat_id, "خطا در حذف.", kb_edit_menu())
        elif action == "delcat":
            cat_idx = int(parts[2])
            cat = get_category_by_index(cat_idx)
            if cat:
                remove_category_db(cat)
                admin_send_message(chat_id, "✅ دسته «{}» حذف شد.".format(cat), kb_edit_menu())
            else:
                admin_send_message(chat_id, "خطا در حذف.", kb_edit_menu())
        elif action == "editfeedback":
            admin_user_states[user_id] = {"step": "edit_feedback", "data": {}}
            admin_send_message(chat_id, EDIT_FEEDBACK_ASK, kb_back())
        elif action == "editcard":
            admin_user_states[user_id] = {"step": "edit_card_number", "data": {}}
            admin_send_message(chat_id, EDIT_CARD_ASK, kb_back())
        elif action == "tariffcat":
            show_sub_tariffs_list(chat_id, int(parts[2]))
        elif action == "edittarifflist":
            show_tariffs_list(chat_id)
        elif action == "tariffsub":
            cat_idx = int(parts[2])
            sub_idx = int(parts[3])
            cat = get_category_by_index(cat_idx)
            sub = get_sub_by_index(cat, sub_idx)
            if cat and sub:
                admin_user_states[user_id] = {
                    "step": "edit_sub_tariff",
                    "data": {"cat_idx": cat_idx, "sub_idx": sub_idx, "sub": sub}
                }
                admin_send_message(
                    chat_id,
                    "💰 تعرفه جدید برای «{}» را وارد کنید (تومان):\n\nمثال: 50000".format(sub),
                    kb_back()
                )
    except Exception as ex:
        print("[ADMIN CB ERROR]", str(ex)[:200])

    admin_answer_callback(cb_id)


# ==================== پیام گروهی: کمکی ====================
def _get_broadcast_recipients(data):
    """گرفتن لیست گیرندگان بر اساس فیلتر"""
    target_type = data.get("target_type", "all")
    target_value = data.get("target_value", "")
    sub_value = data.get("sub_value", "")

    all_experts = load_experts()
    recipients = []

    for e in all_experts:
        if e.get("status", "approved") != "approved":
            continue
        if not e.get("active", True):
            continue

        if target_type == "all":
            recipients.append(e)
        elif target_type == "category":
            if e.get("category") == target_value:
                recipients.append(e)
        elif target_type == "sub":
            if e.get("category") == target_value:
                subs = e.get("sub_specialties", [])
                if sub_value in subs:
                    recipients.append(e)

    return recipients


def _get_target_label(data):
    """برچسب فیلتر برای پیش‌نمایش"""
    target_type = data.get("target_type", "all")
    target_value = data.get("target_value", "")
    sub_value = data.get("sub_value", "")

    if target_type == "all":
        return "همه تعمیرکاران"
    elif target_type == "category":
        return target_value
    elif target_type == "sub":
        return "{} → {}".format(target_value, sub_value)
    return "؟"


def _send_broadcast(admin_chat_id, recipients, msg_text):
    """ارسال پیام به لیست گیرندگان (در thread جداگانه)"""
    from api import send_message

    ok = 0
    fail = 0
    total = len(recipients)

    for expert in recipients:
        try:
            uid = expert.get("user_id")
            if not uid:
                fail += 1
                continue
            result = send_message(uid, msg_text)
            if result and result.get("ok"):
                ok += 1
            else:
                fail += 1
        except Exception as ex:
            fail += 1
            try:
                print("[BCAST ERROR]", str(ex)[:100])
            except:
                pass
        time.sleep(0.5)

    # اطلاع به ادمین
    try:
        admin_send_message(
            admin_chat_id,
            BCAST_DONE.format(ok=ok, fail=fail, total=total),
            kb_admin()
        )
    except Exception as ex:
        print("[BCAST NOTIFY ERROR]", str(ex)[:100])


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


# ==================== منوی ویرایش ====================
def show_edit_menu(chat_id):
    admin_send_message(chat_id, "✏️ منوی ویرایش\n\nیکی از گزینه‌ها را انتخاب کنید:", kb_edit_menu())


def show_categories_list(chat_id):
    cats = get_all_categories()
    txt = "📂 مدیریت دسته‌بندی‌ها\n\n"
    kb = {"inline_keyboard": []}
    for idx, (cat, subs) in enumerate(cats.items()):
        txt += "{}. {} ({} زیرتخصص)\n".format(idx + 1, cat, len(subs))
        kb["inline_keyboard"].append([
            {"text": "✏️ " + cat, "callback_data": "adm:editcat:" + str(idx)}
        ])
    kb["inline_keyboard"].append([
        {"text": "➕ افزودن دسته جدید", "callback_data": "adm:addcat"}
    ])
    kb["inline_keyboard"].append([
        {"text": BTN_BACK, "callback_data": "adm:backedit"}
    ])
    admin_send_message(chat_id, txt, kb)


def show_category_detail(chat_id, cat_idx):
    cat = get_category_by_index(cat_idx)
    if not cat:
        admin_send_message(chat_id, "دسته پیدا نشد.", kb_edit_menu())
        return
    subs = get_category_subs(cat)
    txt = "📂 دسته: {}\n\n".format(cat)
    if subs:
        for i, s in enumerate(subs, 1):
            txt += "{}. {}\n".format(i, s)
    else:
        txt += "هنوز زیرتخصصی نداره.\n"
    kb = kb_category_detail(cat_idx)
    admin_send_message(chat_id, txt, kb)


def show_subs_delete_list(chat_id, cat_idx):
    cat = get_category_by_index(cat_idx)
    if not cat:
        admin_send_message(chat_id, "دسته پیدا نشد.", kb_edit_menu())
        return
    subs = get_category_subs(cat)
    if not subs:
        admin_send_message(chat_id, "زیرتخصصی برای ویرایش وجود نداره.", kb_edit_menu())
        return
    kb = {"inline_keyboard": []}
    for i, s in enumerate(subs):
        kb["inline_keyboard"].append([
            {"text": "✏️ " + s, "callback_data": "adm:subdet:" + str(cat_idx) + ":" + str(i)}
        ])
    kb["inline_keyboard"].append([
        {"text": BTN_BACK, "callback_data": "adm:editcat:" + str(cat_idx)}
    ])
    admin_send_message(chat_id, "روی زیرتخصص مورد نظر بزنید:", kb)


def show_tariffs_list(chat_id):
    cats = get_all_categories()
    txt = "💰 ویرایش تعرفه‌ها\n\n"
    txt += "یه دسته‌بندی رو انتخاب کنید تا تعرفه زیرتخصص‌هاش رو ببینید:\n\n"
    kb = {"inline_keyboard": []}
    for idx, (cat, subs) in enumerate(cats.items()):
        kb["inline_keyboard"].append([
            {"text": "💰 " + cat, "callback_data": "adm:tariffcat:" + str(idx)}
        ])
    kb["inline_keyboard"].append([
        {"text": BTN_BACK, "callback_data": "adm:backedit"}
    ])
    admin_send_message(chat_id, txt, kb)


def show_sub_tariffs_list(chat_id, cat_idx):
    cat = get_category_by_index(cat_idx)
    if not cat:
        admin_send_message(chat_id, "دسته پیدا نشد.", kb_edit_menu())
        return
    subs = get_category_subs(cat)
    if not subs:
        admin_send_message(chat_id, "این دسته زیرتخصصی نداره.", kb_edit_menu())
        return
    txt = "💰 تعرفه‌های «{}»\n\n".format(cat)
    kb = {"inline_keyboard": []}
    for i, sub in enumerate(subs):
        tariff = get_sub_tariff(sub)
        txt += "• {}: {:,} تومان\n".format(sub, tariff)
        kb["inline_keyboard"].append([
            {"text": "✏️ {}".format(sub), "callback_data": "adm:tariffsub:" + str(cat_idx) + ":" + str(i)}
        ])
    kb["inline_keyboard"].append([
        {"text": BTN_BACK, "callback_data": "adm:edittarifflist"}
    ])
    admin_send_message(chat_id, txt, kb)


def start_bulk_edit(chat_id, user_id):
    admin_user_states[user_id] = {"step": "edit_bulk_percent", "data": {}}
    msg = EDIT_BULK_TITLE + "\n\n" + EDIT_BULK_ASK
    admin_send_message(chat_id, msg, kb_back())


def show_cities_menu(chat_id):
    count = len(get_all_cities())
    txt = EDIT_CITIES_TITLE.format(count=count)
    admin_send_message(chat_id, txt, kb_edit_cities_menu())


def show_cities_delete(chat_id, page=0):
    count = len(get_all_cities())
    txt = EDIT_CITIES_LIST_TITLE + "\n\n📊 تعداد: " + str(count)
    kb = kb_cities_delete_list(page=page)
    admin_send_message(chat_id, txt, kb)


# ==================== پیام گروهی ====================
def show_broadcast_menu(chat_id, user_id):
    """نمایش منوی پیام گروهی"""
    admin_user_states.pop(user_id, None)
    admin_send_message(chat_id, BCAST_TITLE + "\n\n" + BCAST_SELECT_TARGET, kb_broadcast_target())


# ==================== حلقه اصلی ====================
def run_admin_bot():
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
