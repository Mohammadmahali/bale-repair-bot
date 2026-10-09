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
    BTN_BULK_TARIFF,
    COMMENT_SKIP_BTN, BTN_COMMENT_WITH_NAME, BTN_COMMENT_ANON,
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
    """کیبورد اشتراک‌گذاری لینک + QR"""
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


# ==================== کیبورد ویرایش (ربات ادمین) ====================
def kb_edit_menu():
    return {"keyboard": [
        [{"text": BTN_EDIT_CATEGORIES}],
        [{"text": BTN_EDIT_TARIFFS}],
        [{"text": BTN_BULK_TARIFF}],
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


# ==================== کیبورد ویرایش کلی تعرفه ====================
def kb_tariffs_menu():
    """منوی فرعی تعرفه‌ها (شامل ویرایش کلی)"""
    return {"keyboard": [
        [{"text": BTN_BULK_TARIFF}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True}


def kb_bulk_confirm():
    """دکمه‌های تأیید/انصراف ویرایش کلی"""
    return {"inline_keyboard": [[
        {"text": "✅ بله، اعمال کن", "callback_data": "bulk:confirm"},
        {"text": "❌ انصراف", "callback_data": "bulk:cancel"}
    ]]}


# ==================== کیبورد امتیاز فوری ====================
def kb_rate_expert(expert_id):
    """دکمه امتیاز فوری بعد از انتخاب تعمیرکار"""
    return {"inline_keyboard": [[
        {"text": "⭐ امتیاز به تعمیرکار",
         "callback_data": "rate:" + str(expert_id)}
    ]]}


# ==================== کیبورد نظرات متنی ====================
def kb_comment_choice():
    """انتخاب: نوشتن نظر یا رد کردن"""
    return {"inline_keyboard": [[
        {"text": "✍️ نوشتن نظر", "callback_data": "comment:yes"},
        {"text": COMMENT_SKIP_BTN, "callback_data": "comment:skip"}
    ]]}


def kb_comment_name_choice():
    """انتخاب: با نام یا ناشناس"""
    return {"inline_keyboard": [[
        {"text": BTN_COMMENT_WITH_NAME, "callback_data": "comment:named"},
        {"text": BTN_COMMENT_ANON, "callback_data": "comment:anon"}
    ]]}
