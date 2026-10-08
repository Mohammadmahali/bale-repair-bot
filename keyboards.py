# ==================== کیبوردهای ربات ====================
from texts import (
    BTN_REGISTER, BTN_SEARCH_SIMPLE, BTN_SEARCH_ADVANCED,
    BTN_EXPERTS_LIST, BTN_MY_PROFILE, BTN_FEEDBACK, BTN_SHOP_STATUS,
    BTN_BACK, BTN_HOME, CAT_ELEC, CAT_GAS, CAT_COOL, CAT_CAR,
    YES, NO, WHO_ME, WHO_SYS,
    SHOP_ACTIVE, SHOP_CLOSED_TEMP, SHOP_CLOSED_PERM,
    BTN_SHARE, BTN_COPY_LINK,
    BTN_WALLET, BTN_CHARGE_WALLET, BTN_SET_LOCATION,
    BTN_CHAT_EXPERT, BTN_CHAT_CUSTOMER, BTN_MY_CHATS,
    BTN_CHAT_BACK, BTN_CHAT_HIDE, BTN_CHAT_SHARE_PHONE, BTN_CHAT_REFRESH,
    ADM_STATS, ADM_EXPERTS, ADM_PENDING, ADM_JOBS, ADM_REVENUE,
    ADM_OPERATORS, ADM_CHANGE_PASS, ADM_EXIT,
    ADM_ADD_OP, ADM_RM_OP, ADM_APPROVE, ADM_REJECT, ADM_BACK,
    ADM_TOGGLE_ON, ADM_TOGGLE_OFF, ADM_PREMIUM_ON, ADM_PREMIUM_OFF, ADM_DELETE,
    BTN_NAV_NESHAN, BTN_NAV_GOOGLE,
    BTN_EDIT, BTN_EDIT_CATEGORIES, BTN_EDIT_TARIFFS,
    BTN_EDIT_FEEDBACK, BTN_EDIT_CARD,
)


# ==================== کیبورد اصلی ====================
def kb_main():
    return {"keyboard": [
        [{"text": BTN_REGISTER}],
        [{"text": BTN_SEARCH_SIMPLE}],
        [{"text": BTN_SEARCH_ADVANCED}],
        [{"text": BTN_EXPERTS_LIST}, {"text": BTN_MY_PROFILE}],
        [{"text": BTN_FEEDBACK}]
    ], "resize_keyboard": True}


# ==================== کیبورد دسته‌بندی ====================
def kb_categories():
    return {"keyboard": [
        [{"text": CAT_ELEC}],
        [{"text": CAT_GAS}],
        [{"text": CAT_COOL}],
        [{"text": CAT_CAR}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True, "one_time_keyboard": True}


# ==================== کیبورد بله/خیر ====================
def kb_yes_no():
    return {"keyboard": [
        [{"text": YES}, {"text": NO}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True, "one_time_keyboard": True}


# ==================== کیبورد بازگشت ====================
def kb_back():
    return {"keyboard": [[{"text": BTN_BACK}]], "resize_keyboard": True}


# ==================== کیبورد ارسال لوکیشن ====================
def kb_location():
    return {"keyboard": [
        [{"text": "📍 ارسال موقعیت من", "request_location": True}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True, "one_time_keyboard": True}


# ==================== کیبورد فقط متن ====================
def kb_text_only():
    return {"keyboard": [[{"text": BTN_BACK}]], "resize_keyboard": True}


# ==================== کیبورد انتخاب تعمیرکار ====================
def kb_who_picks():
    return {"keyboard": [
        [{"text": WHO_ME}],
        [{"text": WHO_SYS}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True, "one_time_keyboard": True}


# ==================== کیبورد وضعیت مغازه ====================
def kb_shop_status():
    return {"keyboard": [
        [{"text": SHOP_ACTIVE}],
        [{"text": SHOP_CLOSED_TEMP}],
        [{"text": SHOP_CLOSED_PERM}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True, "one_time_keyboard": True}


# ==================== کیبورد پروفایل ====================
def kb_profile():
    return {"keyboard": [
        [{"text": BTN_WALLET}],
        [{"text": BTN_MY_CHATS}],
        [{"text": BTN_SHOP_STATUS}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True}


# ==================== کیبورد کیف پول ====================
def kb_wallet():
    return {"keyboard": [
        [{"text": BTN_CHARGE_WALLET}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True}


# ==================== کیبورد ادمین ====================
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


# ==================== کیبورد ستاره‌ها (inline) ====================
def kb_stars(criteria_key):
    return {"inline_keyboard": [[
        {"text": "1⭐", "callback_data": "crit:" + criteria_key + ":1"},
        {"text": "2⭐", "callback_data": "crit:" + criteria_key + ":2"},
        {"text": "3⭐", "callback_data": "crit:" + criteria_key + ":3"},
        {"text": "4⭐", "callback_data": "crit:" + criteria_key + ":4"},
        {"text": "5⭐", "callback_data": "crit:" + criteria_key + ":5"}
    ]]}


# ==================== کیبورد اشتراک‌گذاری لینک ====================
def kb_share_link(url):
    return {"inline_keyboard": [
        [{"text": BTN_SHARE, "url": url}],
        [{"text": BTN_COPY_LINK, "copy_text": {"text": url}}]
    ]}


# ==================== کیبورد مسیریابی ====================
def kb_navigation(lat, lng):
    neshan_web = "https://neshan.org/maps/@{},{}".format(lat, lng)
    google_url = "https://www.google.com/maps?q={},{}".format(lat, lng)
    return {"inline_keyboard": [
        [{"text": BTN_NAV_NESHAN, "url": neshan_web}],
        [{"text": BTN_NAV_GOOGLE, "url": google_url}]
    ]}


# ==================== کیبورد تأیید/رد (ادمین) ====================
def kb_approve_reject(user_id):
    return {"inline_keyboard": [[
        {"text": ADM_APPROVE, "callback_data": "adm:appr:" + str(user_id)},
        {"text": ADM_REJECT, "callback_data": "adm:rej:" + str(user_id)}
    ]]}


# ==================== کیبورد جزئیات تعمیرکار (ادمین) ====================
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


# ==================== کیبورد مدیریت اپراتورها ====================
def kb_operators():
    return {"inline_keyboard": [
        [{"text": ADM_ADD_OP, "callback_data": "adm:addop"}],
        [{"text": ADM_RM_OP, "callback_data": "adm:rmop"}],
        [{"text": ADM_BACK, "callback_data": "adm:backmain"}]
    ]}


# ==================== کیبورد کیف پول (ادمین) ====================
def kb_wallet_admin(txn_id):
    return {"inline_keyboard": [[
        {"text": "✅ تأیید", "callback_data": "wadm:approve:" + str(txn_id)},
        {"text": "❌ رد", "callback_data": "wadm:reject:" + str(txn_id)}
    ]]}


# ==================== کیبورد تأیید شهر (Fuzzy) ====================
def kb_city_confirm(suggested_city):
    return {"inline_keyboard": [[
        {"text": "✅ بله، " + suggested_city, "callback_data": "cityfuzzy:yes"},
        {"text": "❌ خیر", "callback_data": "cityfuzzy:no"}
    ]]}


# ==================== کیبورد چند شهر مشابه ====================
def kb_city_multiple(cities):
    keyboard = []
    for i, city in enumerate(cities, 1):
        keyboard.append([
            {"text": "{}. {}".format(i, city), "callback_data": "citymulti:{}".format(i)}
        ])
    keyboard.append([{"text": "❌ هیچکدام", "callback_data": "citymulti:no"}])
    return {"inline_keyboard": keyboard}


# ==================== کیبورد لوکیشن از پروفایل ====================
def kb_profile_location():
    return {"inline_keyboard": [[
        {"text": BTN_SET_LOCATION, "callback_data": "profile:set_location"}
    ]]}


# ==================== کیبورد ارسال لوکیشن از پروفایل ====================
def kb_profile_location_send():
    return {"keyboard": [
        [{"text": "📍 ارسال موقعیت من", "request_location": True}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True, "one_time_keyboard": True}


# ==================== کیبورد چت (مشتری) ====================
def kb_chat_expert():
    return {"keyboard": [
        [{"text": BTN_CHAT_BACK}]
    ], "resize_keyboard": True}


# ==================== کیبورد چت (تعمیرکار) ====================
def kb_chat_customer():
    return {"keyboard": [
        [{"text": BTN_CHAT_SHARE_PHONE}],
        [{"text": BTN_CHAT_HIDE}],
        [{"text": BTN_CHAT_BACK}]
    ], "resize_keyboard": True}


# ==================== کیبورد منوی چت ====================
def kb_chat_menu():
    return {"keyboard": [
        [{"text": BTN_CHAT_REFRESH}],
        [{"text": BTN_BACK}]
    ], "resize_keyboard": True}


# ==================== کیبورد فیلتر چت ====================
def kb_chat_list():
    return {"inline_keyboard": [
        [{"text": "📋 همه", "callback_data": "chatfilter:all"}],
        [{"text": "🔴 فقط نخونده‌ها", "callback_data": "chatfilter:unread"}],
        [{"text": "📅 امروز", "callback_data": "chatfilter:today"}]
    ]}


# ==================== کیبورد تأیید اشتراک شماره ====================
def kb_chat_share_phone_confirm():
    return {"inline_keyboard": [[
        {"text": "✅ بله", "callback_data": "chatphone:yes"},
        {"text": "❌ خیر", "callback_data": "chatphone:no"}
    ]]}


# ==================== کیبورد تأیید مخفی کردن چت ====================
def kb_chat_hide_confirm():
    return {"inline_keyboard": [[
        {"text": "✅ بله، مخفی کن", "callback_data": "chathide:yes"},
        {"text": "❌ انصراف", "callback_data": "chathide:no"}
    ]]}


# ==================== کیبورد ویرایش (ربات ادمین) ====================
def kb_edit_menu():
    return {"keyboard": [
        [{"text": BTN_EDIT_CATEGORIES}],
        [{"text": BTN_EDIT_TARIFFS}],
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
