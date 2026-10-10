# ==================== کیبوردهای ربات ====================
from texts import (
    BTN_REGISTER, BTN_SEARCH_SIMPLE, BTN_SEARCH_ADVANCED,
    BTN_EXPERTS_LIST, BTN_MY_PROFILE, BTN_FEEDBACK, BTN_SHOP_STATUS,
    BTN_BACK, BTN_HOME, CAT_ELEC, CAT_GAS, CAT_COOL, CAT_CAR,
    YES, NO, WHO_ME, WHO_SYS,
    SHOP_ACTIVE, SHOP_CLOSED_TEMP, SHOP_CLOSED_PERM,
    BTN_SHARE, BTN_COPY_LINK,
    BTN_WALLET, BTN_CHARGE_WALLET, BTN_SET_LOCATION,
    ADM_STATS, ADM_EXPERTS, ADM_PENDING, ADM_JOBS, ADM_REVENUE,
    ADM_OPERATORS, ADM_CHANGE_PASS, ADM_EXIT,
    ADM_ADD_OP, ADM_RM_OP, ADM_APPROVE, ADM_REJECT, ADM_BACK,
    ADM_TOGGLE_ON, ADM_TOGGLE_OFF, ADM_PREMIUM_ON, ADM_PREMIUM_OFF, ADM_DELETE,
    BTN_NAV_NESHAN, BTN_NAV_GOOGLE,
    BTN_EDIT, BTN_EDIT_CATEGORIES, BTN_EDIT_TARIFFS,
    BTN_EDIT_FEEDBACK, BTN_EDIT_CARD, BTN_SHOW_QR,
    BTN_BULK_TARIFF, BTN_EDIT_CITIES,
    COMMENT_SKIP_BTN, BTN_COMMENT_WITH_NAME, BTN_COMMENT_ANON,
    BTN_DEVICE_LOG, BTN_ADD_DEFECT, BTN_VIEW_DEVICE_LOGS,
    BTN_MY_DEVICE_LOGS, BTN_DEVICE_LOG_VIEW, BTN_DEVICE_LOG_EDIT,
    ADM_SECURITY, ADM_SEC_EVENTS, ADM_SEC_BLOCKED, ADM_SEC_BACK,
    SEC_UNBLOCK, EDIT_CITIES_RESET,
    BTN_EDIT_CAT_NAME, BTN_EDIT_SUB_NAME,
    BTN_BROADCAST, BCAST_TARGET_ALL, BCAST_TARGET_BY_CAT, BCAST_TARGET_BY_SUB,
)


def kb_main():
    return {"keyboard": [
        [{"text": BTN_REGISTER}],
        [{"text": BTN_SEARCH_SIMPLE}],
        [{"text": BTN_SEARCH_ADVANCED}],
        [{"text": BTN_EXPERTS_LIST}, {"text": BTN_MY_PROFILE}],
        [{"text": BTN_FEEDBACK}]
    ], "resize_keyboard": True}


def kb_categories():
    from db import get_all_categories
    cats = list(get_all_categories().keys())
    keyboard = []
    for c in cats:
        keyboard.append([{"text": c}])
    keyboard.append([{"text": BTN_BACK}])
    return {"keyboard": keyboard, "resize_keyboard": True, "one_time_keyboard": True}


def kb_yes_no():
    return {"keyboard": [
        [{"text": YES}, {"text": NO}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True, "one_time_keyboard": True}


def kb_back():
    return {"keyboard": [[{"text": BTN_BACK}]], "resize_keyboard": True}


def kb_location():
    return {"keyboard": [
        [{"text": "📍 ارسال موقعیت من", "request_location": True}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True, "one_time_keyboard": True}


def kb_text_only():
    return {"keyboard": [[{"text": BTN_BACK}]], "resize_keyboard": True}


def kb_who_picks():
    return {"keyboard": [
        [{"text": WHO_ME}],
        [{"text": WHO_SYS}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True, "one_time_keyboard": True}


def kb_shop_status():
    return {"keyboard": [
        [{"text": SHOP_ACTIVE}],
        [{"text": SHOP_CLOSED_TEMP}],
        [{"text": SHOP_CLOSED_PERM}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True, "one_time_keyboard": True}


def kb_profile():
    return {"keyboard": [
        [{"text": BTN_WALLET}],
        [{"text": BTN_SHOP_STATUS}],
        [{"text": BTN_MY_DEVICE_LOGS}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True}


def kb_wallet():
    return {"keyboard": [
        [{"text": BTN_CHARGE_WALLET}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True}


def kb_admin():
    return {"keyboard": [
        [{"text": ADM_STATS}],
        [{"text": ADM_EXPERTS}],
        [{"text": ADM_PENDING}],
        [{"text": ADM_JOBS}],
        [{"text": ADM_REVENUE}],
        [{"text": ADM_OPERATORS}],
        [{"text": BTN_BROADCAST}],
        [{"text": ADM_SECURITY}],
        [{"text": BTN_EDIT}],
        [{"text": ADM_CHANGE_PASS}],
        [{"text": ADM_EXIT}]
    ], "resize_keyboard": True}


def kb_stars(criteria_key):
    return {"inline_keyboard": [[
        {"text": "1⭐", "callback_data": "crit:" + criteria_key + ":1"},
        {"text": "2⭐", "callback_data": "crit:" + criteria_key + ":2"},
        {"text": "3⭐", "callback_data": "crit:" + criteria_key + ":3"},
        {"text": "4⭐", "callback_data": "crit:" + criteria_key + ":4"},
        {"text": "5⭐", "callback_data": "crit:" + criteria_key + ":5"}
    ]]}


def kb_share_link(url):
    return {"inline_keyboard": [
        [{"text": BTN_SHARE, "url": url}],
        [{"text": BTN_COPY_LINK, "copy_text": {"text": url}}]
    ]}


def kb_share_link_with_qr(url):
    qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=500x500&data=" + url
    return {"inline_keyboard": [
        [{"text": BTN_SHOW_QR, "url": qr_url}],
        [{"text": BTN_SHARE, "url": url}],
        [{"text": BTN_COPY_LINK, "copy_text": {"text": url}}]
    ]}


def kb_navigation(lat, lng):
    neshan_web = "https://neshan.org/maps/@{},{}".format(lat, lng)
    google_url = "https://www.google.com/maps?q={},{}".format(lat, lng)
    return {"inline_keyboard": [
        [{"text": BTN_NAV_NESHAN, "url": neshan_web}],
        [{"text": BTN_NAV_GOOGLE, "url": google_url}]
    ]}


def kb_approve_reject(user_id):
    return {"inline_keyboard": [[
        {"text": ADM_APPROVE, "callback_data": "adm:appr:" + str(user_id)},
        {"text": ADM_REJECT, "callback_data": "adm:rej:" + str(user_id)}
    ]]}


def kb_expert_detail(expert_id, is_active, is_premium):
    return {"inline_keyboard": [
        [{"text": ADM_TOGGLE_OFF if is_active else ADM_TOGGLE_ON,
          "callback_data": "adm:tog:" + str(expert_id)}],
        [{"text": ADM_PREMIUM_OFF if is_premium else ADM_PREMIUM_ON,
          "callback_data": "adm:prem:" + str(expert_id)}],
        [{"text": ADM_DELETE,
          "callback_data": "adm:del:" + str(expert_id)}],
        [{"text": ADM_BACK,
          "callback_data": "adm:back"}]
    ]}


def kb_operators():
    return {"inline_keyboard": [
        [{"text": ADM_ADD_OP, "callback_data": "adm:addop"}],
        [{"text": ADM_RM_OP, "callback_data": "adm:rmop"}],
        [{"text": ADM_BACK, "callback_data": "adm:backmain"}]
    ]}


def kb_wallet_admin(txn_id):
    return {"inline_keyboard": [[
        {"text": "✅ تأیید", "callback_data": "wadm:approve:" + str(txn_id)},
        {"text": "❌ رد", "callback_data": "wadm:reject:" + str(txn_id)}
    ]]}


def kb_city_confirm(suggested_city):
    return {"inline_keyboard": [[
        {"text": "✅ بله، " + suggested_city, "callback_data": "cityfuzzy:yes"},
        {"text": "❌ خیر", "callback_data": "cityfuzzy:no"}
    ]]}


def kb_city_multiple(cities):
    keyboard = []
    for i, city in enumerate(cities, 1):
        keyboard.append([
            {"text": "{}. {}".format(i, city), "callback_data": "citymulti:{}".format(i)}
        ])
    keyboard.append([{"text": "❌ هیچکدام", "callback_data": "citymulti:no"}])
    return {"inline_keyboard": keyboard}


def kb_profile_location():
    return {"inline_keyboard": [[
        {"text": BTN_SET_LOCATION, "callback_data": "profile:set_location"}
    ]]}


def kb_profile_location_send():
    return {"keyboard": [
        [{"text": "📍 ارسال موقعیت من", "request_location": True}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True, "one_time_keyboard": True}


# ==================== کیبورد ویرایش ====================
def kb_edit_menu():
    return {"keyboard": [
        [{"text": BTN_EDIT_CATEGORIES}],
        [{"text": BTN_EDIT_TARIFFS}],
        [{"text": BTN_BULK_TARIFF}],
        [{"text": BTN_EDIT_CITIES}],
        [{"text": BTN_EDIT_FEEDBACK}],
        [{"text": BTN_EDIT_CARD}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True}


def kb_categories_list():
    return {"inline_keyboard": [
        [{"text": "➕ افزودن دسته جدید", "callback_data": "adm:editcat_add"}],
        [{"text": "🗑 حذف دسته سفارشی", "callback_data": "adm:editcat_del"}],
        [{"text": BTN_BACK, "callback_data": "adm:backedit"}]
    ]}


def kb_tariffs_list():
    return {"inline_keyboard": [
        [{"text": BTN_BACK, "callback_data": "adm:backedit"}]
    ]}


def kb_tariffs_menu():
    return {"keyboard": [
        [{"text": BTN_BULK_TARIFF}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True}


def kb_bulk_confirm():
    return {"inline_keyboard": [[
        {"text": "✅ بله، اعمال کن", "callback_data": "bulk:confirm"},
        {"text": "❌ انصراف", "callback_data": "bulk:cancel"}
    ]]}


# ==================== کیبورد امتیاز ====================
def kb_rate_expert(expert_id):
    return {"inline_keyboard": [[
        {"text": "⭐ امتیاز به تعمیرکار",
         "callback_data": "rate:" + str(expert_id)}
    ]]}


def kb_comment_choice():
    return {"inline_keyboard": [[
        {"text": "✍️ نوشتن نظر", "callback_data": "comment:yes"},
        {"text": COMMENT_SKIP_BTN, "callback_data": "comment:skip"}
    ]]}


def kb_comment_name_choice():
    return {"inline_keyboard": [[
        {"text": BTN_COMMENT_WITH_NAME, "callback_data": "comment:named"},
        {"text": BTN_COMMENT_ANON, "callback_data": "comment:anon"}
    ]]}


# ==================== کیبورد مدیریت شهرها ====================
def kb_edit_cities_menu():
    return {"keyboard": [
        [{"text": "➕ افزودن شهر"}],
        [{"text": "🗑 حذف شهر"}],
        [{"text": EDIT_CITIES_RESET}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True}


def kb_cities_delete_list(page=0, per_page=20):
    from db import get_all_cities
    from texts import BTN_CITIES_NEXT, BTN_CITIES_PREV

    cities = get_all_cities()
    total = len(cities)
    total_pages = max(1, (total + per_page - 1) // per_page)

    if page < 0:
        page = 0
    if page >= total_pages:
        page = total_pages - 1

    start = page * per_page
    end = start + per_page
    page_cities = cities[start:end]

    kb = []
    for city in page_cities:
        kb.append([{"text": "🗑 " + city, "callback_data": "adm:citydel:" + city}])

    nav = []
    if page > 0:
        nav.append({"text": BTN_CITIES_PREV, "callback_data": "adm:citypage:" + str(page - 1)})
    if page < total_pages - 1:
        nav.append({"text": BTN_CITIES_NEXT, "callback_data": "adm:citypage:" + str(page + 1)})
    if nav:
        kb.append(nav)

    kb.append([{"text": BTN_BACK, "callback_data": "adm:backedit"}])

    return {"inline_keyboard": kb}


def kb_cities_reset_confirm():
    return {"inline_keyboard": [[
        {"text": "✅ بله، بازگردان", "callback_data": "adm:cityreset:yes"},
        {"text": "❌ انصراف", "callback_data": "adm:cityreset:no"}
    ]]}


# ==================== کیبورد لاگ عیوب ====================
def kb_device_log_menu():
    return {"keyboard": [
        [{"text": BTN_ADD_DEFECT}],
        [{"text": BTN_VIEW_DEVICE_LOGS}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True}


def kb_device_log_list():
    return {"keyboard": [
        [{"text": BTN_MY_DEVICE_LOGS}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True}


def kb_device_log_item(log_id, can_edit=False):
    kb = {"inline_keyboard": []}
    if can_edit:
        kb["inline_keyboard"].append([
            {"text": BTN_DEVICE_LOG_EDIT, "callback_data": "devlog:edit:" + str(log_id)}
        ])
    return kb if kb["inline_keyboard"] else None


def kb_device_log_confirm_delete(log_id):
    return {"inline_keyboard": [[
        {"text": "🗑 حذف", "callback_data": "devlog:del:" + str(log_id)},
        {"text": "❌ انصراف", "callback_data": "devlog:cancel"}
    ]]}


# ==================== کیبورد امنیت ====================
def kb_security_menu():
    return {"keyboard": [
        [{"text": ADM_SEC_EVENTS}],
        [{"text": ADM_SEC_BLOCKED}],
        [{"text": ADM_SEC_BACK}]
    ], "resize_keyboard": True}


def kb_blocked_user(user_id):
    return {"inline_keyboard": [[
        {"text": SEC_UNBLOCK, "callback_data": "adm:unblock:" + str(user_id)}
    ]]}


# ==================== کیبورد ویرایش نام گروه/زیرگروه ====================
def kb_category_detail(cat_idx):
    """جزئیات یه گروه (با دکمه ویرایش نام)"""
    return {"inline_keyboard": [
        [{"text": BTN_EDIT_CAT_NAME, "callback_data": "adm:rencat:" + str(cat_idx)}],
        [{"text": "➕ افزودن زیرتخصص", "callback_data": "adm:addsub:" + str(cat_idx)}],
        [{"text": "🗑 حذف زیرتخصص", "callback_data": "adm:delsublist:" + str(cat_idx)}],
        [{"text": "🗑 حذف کل دسته", "callback_data": "adm:delcat:" + str(cat_idx)}],
        [{"text": BTN_BACK, "callback_data": "adm:editcatlist"}]
    ]}


def kb_sub_detail(cat_idx, sub_idx):
    """جزئیات یه زیرتخصص (با دکمه ویرایش نام)"""
    return {"inline_keyboard": [
        [{"text": BTN_EDIT_SUB_NAME, "callback_data": "adm:rensub:" + str(cat_idx) + ":" + str(sub_idx)}],
        [{"text": "🗑 حذف این زیرتخصص", "callback_data": "adm:delsubid:" + str(cat_idx) + ":" + str(sub_idx)}],
        [{"text": BTN_BACK, "callback_data": "adm:editcat:" + str(cat_idx)}]
    ]}
    
    # ==================== کیبورد پیام گروهی ====================
def kb_broadcast_target():
    return {"inline_keyboard": [
        [{"text": BCAST_TARGET_ALL, "callback_data": "bcast:all"}],
        [{"text": BCAST_TARGET_BY_CAT, "callback_data": "bcast:cats"}],
        [{"text": BCAST_TARGET_BY_SUB, "callback_data": "bcast:subs"}],
        [{"text": BTN_BACK, "callback_data": "bcast:back"}]
    ]}


def kb_broadcast_cats(mode="cat"):
    """لیست گروه‌ها - mode: cat (برای گروه) یا subcat (برای زیرتخصص)"""
    from db import get_all_categories
    cats = list(get_all_categories().keys())
    kb = []
    for idx, cat in enumerate(cats):
        cb = "bcast:{}:{}".format(mode, idx)
        kb.append([{"text": cat, "callback_data": cb}])
    kb.append([{"text": BTN_BACK, "callback_data": "bcast:back"}])
    return {"inline_keyboard": kb}


def kb_broadcast_subs(cat_idx):
    from db import get_category_by_index, get_category_subs
    cat = get_category_by_index(cat_idx)
    if not cat:
        return {"inline_keyboard": []}
    subs = get_category_subs(cat)
    kb = []
    for i, sub in enumerate(subs):
        kb.append([{"text": sub, "callback_data": "bcast:sub:" + str(cat_idx) + ":" + str(i)}])
    kb.append([{"text": BTN_BACK, "callback_data": "bcast:cats"}])
    return {"inline_keyboard": kb}


def kb_broadcast_confirm():
    return {"inline_keyboard": [[
        {"text": "✅ ارسال کن", "callback_data": "bcast:confirm"},
        {"text": "❌ انصراف", "callback_data": "bcast:cancel"}
    ]]}
