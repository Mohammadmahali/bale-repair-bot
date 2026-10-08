# ==================== جستجوی متخصصین ====================
import time
from texts import (
    CAT_ELEC, CAT_GAS, CAT_COOL, CAT_CAR,
    YES, NO, CHOOSE_OPTION, INVALID_INPUT, BTN_BACK,
    ASK_CUST_AREA, ASK_DESC, ASK_PHONE_SHARE, ASK_PHONE_INPUT,
    ASK_WHO_PICK, WHO_ME, WHO_SYS, ASK_PRIORITY, ASK_HANDOVER, ASK_RETURN,
    HANDOVER_TIMES, RETURN_TIMES, CRITERIA, FOUND_EXPERTS, NOT_FOUND,
    CALL_DIRECT, NEW_CUSTOMER, CHOSEN_EXPERT, LBL_NAME, LBL_PHONE,
    LBL_AREA, LBL_RATING, LBL_SUBSPEC, LBL_ROLE, LBL_REFERRAL, LBL_ONSITE,
    LBL_TRACKING, TRACKING_NOTE, LBL_PROBLEM,
    FUZZY_CONFIRM, FUZZY_YES, FUZZY_NO, FUZZY_MULTIPLE,
    FUZZY_CITY_NOT_FOUND, FUZZY_LOCATION_HINT,
    BTN_NAV_NESHAN, BTN_NAV_GOOGLE,
    BTN_CHAT_EXPERT,
)
from keyboards import (
    kb_categories, kb_yes_no, kb_back, kb_location,
    kb_who_picks, kb_navigation, kb_main,
    kb_city_confirm, kb_city_multiple,
)
from api import send_message
from db import (
    load_experts, create_job, is_shop_open,
    find_expert_by_id, get_feedback_id,
    get_expert_priority_penalty,
)
from utils import (
    parse_numbers, parse_single_number, parse_priorities,
    find_similar_cities, format_numbered_list, format_criteria_list,
    haversine, normalize_text,
)
from handlers.register import get_subs_by_category, is_valid_category


STAGE_DAYS = {0: 30, 1: 150}
LOCATION_RADIUS_KM = 20


PREV_STEP = {
    "req_cat": None,
    "req_sub": "req_cat",
    "req_priority": "req_sub",
    "req_handover": "req_priority",
    "req_return": "req_handover",
    "req_area": "req_sub",
    "req_desc": "req_area",
    "req_phone_share": "req_desc",
    "req_phone_input": "req_phone_share",
    "req_who": "req_phone_share",
}


def _normalize_city(text):
    if not text:
        return ""
    return text.strip().replace("ي", "ی").replace("ك", "ک").replace("\u200c", "").replace(" ", "").replace("‌", "")


def _find_exact_city(input_city):
    from config import IRAN_CITIES
    normalized_input = _normalize_city(input_city)
    if not normalized_input:
        return None
    for city in IRAN_CITIES:
        if _normalize_city(city) == normalized_input:
            return city
    return None


def start_search(chat_id, user_id, mode, sessions, search_modes):
    search_modes[user_id] = mode
    sessions[user_id] = {"step": "req_cat", "data": {}}
    send_message(chat_id, CHOOSE_OPTION, kb_categories())


def continue_search(chat_id, user_id, text, sessions, search_modes):
    if user_id not in sessions:
        return False
    
    session = sessions[user_id]
    step = session["step"]
    data = session["data"]
    
    if text == BTN_BACK:
        if step == "req_area":
            mode = search_modes.get(user_id, "simple")
            prev = "req_sub" if mode == "simple" else "req_return"
        else:
            prev = PREV_STEP.get(step)
        if prev is None:
            sessions.pop(user_id, None)
            send_message(chat_id, "به منوی اصلی بازگشتید.", kb_main())
        else:
            session["step"] = prev
            ask_for_step(chat_id, prev, data, search_modes.get(user_id, "simple"))
        return True
    
    if step == "req_cat":
        if not is_valid_category(text):
            send_message(chat_id, CHOOSE_OPTION, kb_categories())
            return True
        data["category"] = text
        data["_subs"] = get_subs_by_category(text)
        session["step"] = "req_sub"
        msg = "شماره نوع خرابی را وارد کنید:\n\n"
        msg += format_numbered_list(data["_subs"])
        send_message(chat_id, msg, kb_back())
        return True
    
    if step == "req_sub":
        nums = parse_numbers(text, len(data["_subs"]))
        if len(nums) != 1:
            send_message(chat_id, INVALID_INPUT, kb_back())
            return True
        data["sub"] = data["_subs"][nums[0]-1]
        mode = search_modes.get(user_id, "simple")
        if mode == "adv":
            session["step"] = "req_priority"
            msg = ASK_PRIORITY + format_criteria_list(CRITERIA)
            send_message(chat_id, msg, kb_back())
        else:
            session["step"] = "req_area"
            send_message(chat_id, ASK_CUST_AREA, kb_location())
        return True
    
    if step == "req_priority":
        if text.strip() != "0" and text.strip() != "" and not parse_priorities(text, CRITERIA):
            send_message(chat_id, INVALID_INPUT, kb_back())
            return True
        data["priorities"] = parse_priorities(text, CRITERIA)
        session["step"] = "req_handover"
        msg = ASK_HANDOVER + format_numbered_list(HANDOVER_TIMES)
        send_message(chat_id, msg, kb_back())
        return True
    
    if step == "req_handover":
        n = parse_single_number(text, len(HANDOVER_TIMES))
        if n is None:
            send_message(chat_id, INVALID_INPUT, kb_back())
            return True
        data["handover"] = n
        session["step"] = "req_return"
        msg = ASK_RETURN + format_numbered_list(RETURN_TIMES)
        send_message(chat_id, msg, kb_back())
        return True
    
    if step == "req_return":
        n = parse_single_number(text, len(RETURN_TIMES))
        if n is None:
            send_message(chat_id, INVALID_INPUT, kb_back())
            return True
        data["return_time"] = n
        session["step"] = "req_area"
        send_message(chat_id, ASK_CUST_AREA, kb_location())
        return True
    
    # ===== مرحله شهر =====
    if step == "req_area":
        city_input = text.strip()
        
        exact = _find_exact_city(city_input)
        if exact:
            data["area"] = exact
            session["step"] = "req_desc"
            send_message(chat_id, ASK_DESC, kb_back())
            return True
        
        similar = find_similar_cities(city_input)
        
        if not similar:
            send_message(
                chat_id,
                FUZZY_CITY_NOT_FOUND.format(city=city_input),
                kb_location()
            )
            return True
        
        if len(similar) == 1:
            data["_pending_area"] = city_input
            data["_suggested_city"] = similar[0]
            session["step"] = "req_fuzzy_confirm"
            send_message(chat_id, FUZZY_CONFIRM.format(city=similar[0]), kb_city_confirm(similar[0]))
            return True
        
        if len(similar) > 1:
            data["_pending_area"] = city_input
            data["_suggested_cities"] = similar[:3]
            session["step"] = "req_fuzzy_multiple"
            send_message(chat_id, FUZZY_MULTIPLE, kb_city_multiple(similar[:3]))
            return True
    
    if step == "req_fuzzy_confirm":
        send_message(chat_id, "لطفاً از دکمه‌های بالا استفاده کنید.", kb_back())
        return True
    
    if step == "req_fuzzy_multiple":
        send_message(chat_id, "لطفاً از دکمه‌های بالا استفاده کنید.", kb_back())
        return True
    
    if step == "req_desc":
        data["desc"] = text.strip()
        session["step"] = "req_phone_share"
        send_message(chat_id, ASK_PHONE_SHARE, kb_yes_no())
        return True
    
    if step == "req_phone_share":
        if text not in [YES, NO]:
            send_message(chat_id, CHOOSE_OPTION, kb_yes_no())
            return True
        if text == YES:
            session["step"] = "req_phone_input"
            send_message(chat_id, ASK_PHONE_INPUT, kb_back())
        else:
            data["send_phone"] = False
            data["customer_phone"] = None
            session["step"] = "req_who"
            send_message(chat_id, ASK_WHO_PICK, kb_who_picks())
        return True
    
    if step == "req_phone_input":
        data["send_phone"] = True
        data["customer_phone"] = text.strip()
        session["step"] = "req_who"
        send_message(chat_id, ASK_WHO_PICK, kb_who_picks())
        return True
    
    if step == "req_who":
        if text not in [WHO_ME, WHO_SYS]:
            send_message(chat_id, CHOOSE_OPTION, kb_who_picks())
            return True
        data["who"] = "me" if text == WHO_ME else "sys"
        
        results = find_matching(
            category=data["category"],
            sub=data["sub"],
            area=data.get("area", ""),
            needs_onsite=False,
            priorities=data.get("priorities", []),
            handover=data.get("handover"),
            cust_lat=data.get("lat"),
            cust_lng=data.get("lng"),
        )
        
        if not results and data.get("handover") is not None:
            results = find_matching(
                category=data["category"],
                sub=data["sub"],
                area=data.get("area", ""),
                needs_onsite=False,
                priorities=data.get("priorities", []),
                handover=None,
                cust_lat=data.get("lat"),
                cust_lng=data.get("lng"),
            )
        
        if not results:
            send_message(chat_id, NOT_FOUND, kb_main())
            sessions.pop(user_id, None)
            search_modes.pop(user_id, None)
            return True
        
        info = {
            "category": data["category"],
            "sub": data["sub"],
            "area": data.get("area", ""),
            "desc": data.get("desc", ""),
            "phone": data.get("customer_phone") if data.get("send_phone") else None,
        }
        
        if data["who"] == "sys":
            deliver_expert(chat_id, user_id, results[0], info, data.get("send_phone", False))
        else:
            txt = FOUND_EXPERTS
            if data.get("priorities"):
                labels = "، ".join([c["label"] for c in CRITERIA if c["key"] in data["priorities"]])
                txt += "🎯 اولویت: " + labels + "\n\n"
            for i, e in enumerate(results, 1):
                txt += format_expert_line(e, i, data.get("priorities", [])) + "\n"
            txt += "\nیکی را انتخاب کنید:"
            kb = {"inline_keyboard": []}
            for e in results:
                kb["inline_keyboard"].append([
                    {"text": "✅ " + e["name"], "callback_data": "pick:" + str(e["user_id"])}
                ])
            send_message(chat_id, txt, kb)
            session["step"] = "req_pick_waiting"
            session["data"]["_results"] = results
            session["data"]["_info"] = info
            return True
    
    return False


def handle_location(chat_id, user_id, location, sessions):
    if user_id not in sessions:
        return False
    session = sessions[user_id]
    step = session["step"]
    data = session["data"]
    
    if step == "req_area":
        data["lat"] = location.get("latitude")
        data["lng"] = location.get("longitude")
        data["area"] = ""
        session["step"] = "req_desc"
        send_message(chat_id, FUZZY_LOCATION_HINT, kb_back())
        return True
    
    return False


def handle_city_fuzzy_callback(chat_id, user_id, action, sessions):
    if user_id not in sessions:
        return False
    session = sessions[user_id]
    if session.get("step") != "req_fuzzy_confirm":
        return False
    data = session["data"]
    if action == "yes" and data.get("_suggested_city"):
        data["area"] = data["_suggested_city"]
    else:
        data["area"] = data.get("_pending_area", "")
    session["step"] = "req_desc"
    send_message(chat_id, ASK_DESC, kb_back())
    return True


def handle_city_multiple_callback(chat_id, user_id, choice, sessions):
    if user_id not in sessions:
        return False
    session = sessions[user_id]
    if session.get("step") != "req_fuzzy_multiple":
        return False
    data = session["data"]
    cities = data.get("_suggested_cities", [])
    if choice == "no":
        data["area"] = data.get("_pending_area", "")
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(cities):
                data["area"] = cities[idx]
            else:
                data["area"] = data.get("_pending_area", "")
        except:
            data["area"] = data.get("_pending_area", "")
    session["step"] = "req_desc"
    send_message(chat_id, ASK_DESC, kb_back())
    return True


def find_matching(category, sub, area, needs_onsite, priorities,
                  handover=None, cust_lat=None, cust_lng=None):
    all_match = []
    loc_match = []
    text_match = []
    
    for e in load_experts():
        if not is_shop_open(e):
            continue
        if e.get("status", "approved") != "approved":
            continue
        if e.get("category") != category:
            continue
        if sub not in e.get("sub_specialties", []):
            continue
        if needs_onsite and not e.get("works_on_site", False):
            continue
        if not _matches_times(e, handover):
            continue
        all_match.append(e)
        
        if cust_lat and cust_lng and e.get("lat") and e.get("lng"):
            dist = haversine(cust_lat, cust_lng, e["lat"], e["lng"])
            if dist <= LOCATION_RADIUS_KM:
                loc_match.append(e)
        elif area:
            e_area = e.get("area", "")
            if area in e_area or e_area in area:
                text_match.append(e)
            else:
                a_w = set(area.replace("،", " ").replace(",", " ").split())
                e_w = set(e_area.replace("،", " ").replace(",", " ").split())
                if a_w & e_w:
                    text_match.append(e)
    
    if cust_lat and cust_lng:
        result = loc_match if loc_match else (text_match if text_match else all_match)
    elif area:
        result = text_match if text_match else all_match
    else:
        result = all_match
    
    result.sort(key=lambda x: _rank_score(x, priorities), reverse=True)
    return result[:3]


def _matches_times(e, handover):
    if handover is not None and handover < 3:
        rp = int(e.get("response_speed", 3))
        if handover == 0 and rp > 0:
            return False
        if handover == 1 and rp > 1:
            return False
        if handover == 2 and rp > 2:
            return False
    return True


def _rank_score(e, priorities=None):
    if priorities:
        score = _priority_rating(e, priorities) * 40 + _overall_rating(e) * 10
    else:
        score = _overall_rating(e) * 20
    if e.get("is_premium"):
        score += 50
    if e.get("works_on_site"):
        score += 10
    try:
        score += get_expert_priority_penalty(e)
    except:
        pass
    return score


def _calculate_commission(expert, sub_specialty):
    """محاسبه کمیسیون بر اساس زیرتخصص"""
    try:
        from db import get_sub_tariff
        return get_sub_tariff(sub_specialty)
    except:
        return 50000


def _overall_rating(e):
    total = 0
    count = 0
    for cr in CRITERIA:
        rt = 0
        rc = 0
        for s in ["0", "1", "2"]:
            r = e.get("ratings_by_stage", {}).get(s, {}).get(cr["key"], {})
            rt += r.get("sum", 0)
            rc += r.get("count", 0)
        if rc > 0:
            total += rt / rc
            count += 1
    if count == 0:
        return 5.0
    return total / count


def _priority_rating(e, priorities):
    if not priorities:
        return 5.0
    total = 0
    count = 0
    for k in priorities:
        rt = 0
        rc = 0
        for s in ["0", "1", "2"]:
            r = e.get("ratings_by_stage", {}).get(s, {}).get(k, {})
            rt += r.get("sum", 0)
            rc += r.get("count", 0)
        if rc > 0:
            total += rt / rc
            count += 1
    if count == 0:
        return 5.0
    return total / count


def format_expert_line(e, idx, priorities):
    txt = "{}. 👤 ".format(idx) + e["name"] + "\n"
    txt += "   📞 " + e["phone"] + "\n"
    txt += "   📍 " + e["area"] + "\n"
    txt += "   ⭐ " + "{:.1f}/5".format(_overall_rating(e))
    if priorities:
        txt += "   🎯 " + "{:.1f}".format(_priority_rating(e, priorities)) + "/5\n"
    else:
        txt += "\n"
    if e.get("works_on_site"):
        txt += "   🏠 حضور در محل\n"
    return txt


def deliver_expert(chat_id, customer_id, expert, info, send_phone):
    code = create_job(customer_id, chat_id, expert, info)
    msg = CHOSEN_EXPERT
    msg += "👤 " + expert["name"] + "\n"
    msg += "📞 " + expert["phone"] + "\n"
    msg += "📍 " + expert.get("area", "?") + "\n"
    msg += LBL_TRACKING + code
    msg += TRACKING_NOTE
    fid = get_feedback_id()
    if fid:
        msg += "\n\n💬 نظرات و پیشنهادات: " + fid
    send_message(chat_id, msg, kb_main())
    notify_expert(expert, info, code, send_phone)
    if expert.get("lat") and expert.get("lng"):
        send_message(chat_id, "📍 برای مسیریابی:", kb_navigation(expert["lat"], expert["lng"]))


def notify_expert(expert, info, code, send_phone):
    msg = NEW_CUSTOMER + "\n\n"
    msg += LBL_ROLE + " " + info.get("category", "?") + "\n"
    msg += LBL_SUBSPEC + " " + info.get("sub", "?") + "\n"
    if info.get("area"):
        msg += LBL_AREA + " " + info["area"] + "\n"
    msg += LBL_PROBLEM + " " + info.get("desc", "") + "\n\n"
    msg += LBL_TRACKING + code
    if send_phone and info.get("phone"):
        msg += "\n\n📞 تماس مشتری: " + info["phone"]
    else:
        msg += "\n\nℹ️ مشتری خودش با شما تماس می‌گیرد."
    send_message(expert["user_id"], msg)


def handle_pick_expert(chat_id, customer_id, expert_id, sessions):
    if customer_id not in sessions:
        return False
    session = sessions[customer_id]
    data = session.get("data", {})
    results = data.get("_results", [])
    info = data.get("_info", {})
    expert = None
    for e in results:
        if e.get("user_id") == expert_id:
            expert = e
            break
    if not expert:
        expert = find_expert_by_id(expert_id)
    if not expert:
        return False
    deliver_expert(chat_id, customer_id, expert, info, data.get("send_phone", False))
    sessions.pop(customer_id, None)
    return True


def ask_for_step(chat_id, step, data, mode):
    if step == "req_cat":
        send_message(chat_id, CHOOSE_OPTION, kb_categories())
    elif step == "req_sub":
        msg = "شماره نوع خرابی:\n\n" + format_numbered_list(data.get("_subs", []))
        send_message(chat_id, msg, kb_back())
    elif step == "req_priority":
        msg = ASK_PRIORITY + format_criteria_list(CRITERIA)
        send_message(chat_id, msg, kb_back())
    elif step == "req_handover":
        msg = ASK_HANDOVER + format_numbered_list(HANDOVER_TIMES)
        send_message(chat_id, msg, kb_back())
    elif step == "req_return":
        msg = ASK_RETURN + format_numbered_list(RETURN_TIMES)
        send_message(chat_id, msg, kb_back())
    elif step == "req_area":
        send_message(chat_id, ASK_CUST_AREA, kb_location())
    elif step == "req_desc":
        send_message(chat_id, ASK_DESC, kb_back())
    elif step == "req_phone_share":
        send_message(chat_id, ASK_PHONE_SHARE, kb_yes_no())
    elif step == "req_phone_input":
        send_message(chat_id, ASK_PHONE_INPUT, kb_back())
    elif step == "req_who":
        send_message(chat_id, ASK_WHO_PICK, kb_who_picks())
