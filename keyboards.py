# ==================== کیبوردهای ربات ====================
from texts import (
    BTN_REGISTER, BTN_SEARCH_SIMPLE, BTN_SEARCH_ADVANCED,
    BTN_EXPERTS_LIST, BTN_MY_PROFILE, BTN_FEEDBACK, BTN_SHOP_STATUS,
    BTN_BACK, CAT_ELEC, CAT_GAS, CAT_COOL, CAT_CAR,
    YES, NO, WHO_ME, WHO_SYS,
    SHOP_ACTIVE, SHOP_CLOSED_TEMP, SHOP_CLOSED_PERM,
    BTN_SHARE, BTN_COPY_LINK,
    ADM_STATS, ADM_EXPERTS, ADM_PENDING, ADM_JOBS, ADM_REVENUE,
    ADM_OPERATORS, ADM_CHANGE_PASS, ADM_EXIT,
    ADM_ADD_OP, ADM_RM_OP, ADM_APPROVE, ADM_REJECT, ADM_BACK,
    ADM_TOGGLE_ON, ADM_TOGGLE_OFF, ADM_PREMIUM_ON, ADM_PREMIUM_OFF, ADM_DELETE,
    BTN_NAV_NESHAN, BTN_NAV_GOOGLE,
)


# ==================== کیبورد اصلی ====================
def kb_main():
    return {
        "keyboard": [
            [{"text": BTN_REGISTER}],
            [{"text": BTN_SEARCH_SIMPLE}],
            [{"text": BTN_SEARCH_ADVANCED}],
            [{"text": BTN_EXPERTS_LIST}, {"text": BTN_MY_PROFILE}],
            [{"text": BTN_FEEDBACK}]
        ],
        "resize_keyboard": True
    }


# ==================== کیبورد دسته‌بندی ====================
def kb_categories():
    return {
        "keyboard": [
            [{"text": CAT_ELEC}],
            [{"text": CAT_GAS}],
            [{"text": CAT_COOL}],
            [{"text": CAT_CAR}],
            [{"text": BTN_BACK}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }


# ==================== کیبورد بله/خیر ====================
def kb_yes_no():
    return {
        "keyboard": [
            [{"text": YES}, {"text": NO}],
            [{"text": BTN_BACK}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }


# ==================== کیبورد بازگشت ====================
def kb_back():
    return {
        "keyboard": [[{"text": BTN_BACK}]],
        "resize_keyboard": True
    }


# ==================== کیبورد ارسال لوکیشن ====================
def kb_location():
    return {
        "keyboard": [
            [{"text": "📍 ارسال موقعیت من", "request_location": True}],
            [{"text": BTN_BACK}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }


# ==================== کیبورد فقط متن (بدون لوکیشن) ====================
def kb_text_only():
    return {
        "keyboard": [[{"text": BTN_BACK}]],
        "resize_keyboard": True
    }


# ==================== کیبورد انتخاب تعمیرکار ====================
def kb_who_picks():
    return {
        "keyboard": [
            [{"text": WHO_ME}],
            [{"text": WHO_SYS}],
            [{"text": BTN_BACK}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }


# ==================== کیبورد وضعیت مغازه ====================
def kb_shop_status():
    return {
        "keyboard": [
            [{"text": SHOP_ACTIVE}],
            [{"text": SHOP_CLOSED_TEMP}],
            [{"text": SHOP_CLOSED_PERM}],
            [{"text": BTN_BACK}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }


# ==================== کیبورد پنل ادمین ====================
def kb_admin():
    return {
        "keyboard": [
            [{"text": ADM_STATS}],
            [{"text": ADM_EXPERTS}],
            [{"text": ADM_PENDING}],
            [{"text": ADM_JOBS}],
            [{"text": ADM_REVENUE}],
            [{"text": ADM_OPERATORS}],
            [{"text": ADM_CHANGE_PASS}],
            [{"text": ADM_EXIT}]
        ],
        "resize_keyboard": True
    }


# ==================== کیبورد ستاره‌ها (inline) ====================
def kb_stars(criteria_key):
    return {
        "inline_keyboard": [[
            {"text": "1⭐", "callback_data": "crit:" + criteria_key + ":1"},
            {"text": "2⭐", "callback_data": "crit:" + criteria_key + ":2"},
            {"text": "3⭐", "callback_data": "crit:" + criteria_key + ":3"},
            {"text": "4⭐", "callback_data": "crit:" + criteria_key + ":4"},
            {"text": "5⭐", "callback_data": "crit:" + criteria_key + ":5"}
        ]]
    }


# ==================== کیبورد اشتراک‌گذاری لینک ====================
def kb_share_link(url):
    return {
        "inline_keyboard": [
            [{"text": BTN_SHARE, "url": url}],
            [{"text": BTN_COPY_LINK, "copy_text": {"text": url}}]
        ]
    }


# ==================== کیبورد مسیریابی ====================
def kb_navigation(lat, lng):
    neshan_url = "https://neshan.org/maps/@{},{}".format(lat, lng)
    google_url = "https://www.google.com/maps?q={},{}".format(lat, lng)
    return {
        "inline_keyboard": [
            [{"text": BTN_NAV_NESHAN, "url": neshan_url}],
            [{"text": BTN_NAV_GOOGLE, "url": google_url}]
        ]
    }


# ==================== کیبورد تأیید/رد (ادمین) ====================
def kb_approve_reject(user_id):
    return {
        "inline_keyboard": [[
            {"text": ADM_APPROVE, "callback_data": "adm:appr:" + str(user_id)},
            {"text": ADM_REJECT, "callback_data": "adm:rej:" + str(user_id)}
        ]]
    }


# ==================== کیبورد جزئیات تعمیرکار (ادمین) ====================
def kb_expert_detail(expert_id, is_active, is_premium):
    return {
        "inline_keyboard": [
            [{"text": ADM_TOGGLE_OFF if is_active else ADM_TOGGLE_ON,
              "callback_data": "adm:tog:" + str(expert_id)}],
            [{"text": ADM_PREMIUM_OFF if is_premium else ADM_PREMIUM_ON,
              "callback_data": "adm:prem:" + str(expert_id)}],
            [{"text": ADM_DELETE,
              "callback_data": "adm:del:" + str(expert_id)}],
            [{"text": ADM_BACK,
              "callback_data": "adm:back"}]
        ]
    }


# ==================== کیبورد مدیریت اپراتورها ====================
def kb_operators():
    return {
        "inline_keyboard": [
            [{"text": ADM_ADD_OP, "callback_data": "adm:addop"}],
            [{"text": ADM_RM_OP, "callback_data": "adm:rmop"}],
            [{"text": ADM_BACK, "callback_data": "adm:backmain"}]
        ]
    }


# ==================== کیبورد اختیاری برای نظرات ====================
def kb_rating_comment():
    return {
        "inline_keyboard": [[
            {"text": "⏭ رد کردن", "callback_data": "rate:skip_comment"}
        ]]
    }
