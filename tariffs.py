# ==================== منطق تعرفه‌ها (Bulk Edit) ====================
"""
مدیریت تعرفه‌ها:
- خوندن تعرفه‌های فعلی (پیش‌فرض + override کاربر)
- اعمال تغییر درصدی روی همه
- رند کردن به ۱۰۰۰
- ذخیره در config
"""
from database import config_get, config_set


# ==================== ابزار ====================
def round_to_1000(amount):
    """رند کردن به نزدیک‌ترین ۱۰۰۰ پایین‌تر
    مثال: 128,236 → 128,000
    """
    return (int(amount) // 1000) * 1000


# ==================== خوندن تعرفه‌های فعلی ====================
def get_current_tariffs():
    """
    برگرداندن تعرفه‌های فعلی:
    - subs: زیرتخصص → مبلغ (پیش‌فرض config.py + override دیتابیس)
    - categories: دسته → مبلغ
    """
    from config import SUB_TARIFFS, TARIFFS

    user_subs = config_get("sub_tariffs", {})
    user_cats = config_get("tariffs", {})

    merged_subs = dict(SUB_TARIFFS)
    merged_subs.update(user_subs)

    merged_cats = dict(TARIFFS)
    merged_cats.update(user_cats)

    return {
        "subs": merged_subs,
        "categories": merged_cats,
    }


# ==================== پیش‌نمایش تغییر ====================
def preview_bulk(percent):
    """
    محاسبه پیش‌نمایش بدون ذخیره
    """
    current = get_current_tariffs()
    factor = 1 + (percent / 100.0)

    subs_new = {}
    for name, amount in current["subs"].items():
        new_amount = round_to_1000(int(amount) * factor)
        if new_amount < 1000:
            new_amount = 1000
        subs_new[name] = new_amount

    cats_new = {}
    for name, amount in current["categories"].items():
        new_amount = round_to_1000(int(amount) * factor)
        if new_amount < 1000:
            new_amount = 1000
        cats_new[name] = new_amount

    count = len(subs_new) + len(cats_new)

    # نمونه‌ها برای پیش‌نمایش
    examples = []

    if "ماکروفر / مایکروویو" in subs_new:
        examples.append((
            "ماکروفر",
            current["subs"]["ماکروفر / مایکروویو"],
            subs_new["ماکروفر / مایکروویو"]
        ))

    if "ماشین لباسشویی" in subs_new:
        examples.append((
            "ماشین لباسشویی",
            current["subs"]["ماشین لباسشویی"],
            subs_new["ماشین لباسشویی"]
        ))

    if len(examples) < 2:
        for name, amount in list(subs_new.items())[:2]:
            if not any(e[0] == name for e in examples):
                examples.append((name, current["subs"][name], amount))
            if len(examples) >= 2:
                break

    return {
        "count": count,
        "percent": percent,
        "examples": examples[:2],
        "subs_new": subs_new,
        "cats_new": cats_new,
    }


# ==================== اعمال تغییر ====================
def apply_bulk(percent):
    """
    اعمال درصد تغییر روی همه تعرفه‌ها و ذخیره در دیتابیس
    """
    preview = preview_bulk(percent)

    config_set("sub_tariffs", preview["subs_new"])
    config_set("tariffs", preview["cats_new"])

    return preview["count"]


# ==================== برگشت به پیش‌فرض ====================
def reset_to_default():
    """
    حذف همه override‌ها و برگشت به پیش‌فرض config.py
    """
    config_set("sub_tariffs", {})
    config_set("tariffs", {})
    return True
