import json, time, requests, random, string, ssl
from math import radians, sin, cos, sqrt, atan2
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        except: pass
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

session = requests.Session()
adapter = SSLAdapter(max_retries=Retry(total=5, backoff_factor=2))
session.mount('https://', adapter)
session.verify = False

TOKEN = "2007928769:p_l7euP0ifN0Vh7OWyFqRaJiN9KNRpgsAWY"
ADMIN_ID = 1808576881
API_URL = "https://tapi.bale.ai/bot" + TOKEN
DB_FILE = "experts.json"
JOBS_FILE = "jobs.json"
BOT_USERNAME = ""

user_states = {}
rating_states = {}
search_ctx = {}
viewing_expert = {}

RESPONSE_TIMES = [
    "\u0647\u0645\u06cc\u0634\u0647 \u062f\u0631 \u062f\u0633\u062a\u0631\u0633 (\u0641\u0648\u0631\u06cc)",
    "\u062d\u062f\u0627\u06a9\u062b\u0631 \u0646\u06cc\u0645 \u0633\u0627\u0639\u062a",
    "\u0686\u0646\u062f \u0633\u0627\u0639\u062a",
    "\u0628\u0627 \u062a\u0639\u06cc\u06cc\u0646 \u0648\u0642\u062a \u0642\u0628\u0644\u06cc",
]
REPAIR_TIMES = [
    "\u06a9\u0645\u062a\u0631 \u0627\u0632 \u06cc\u06a9 \u0633\u0627\u0639\u062a",
    "\u0646\u0635\u0641 \u0631\u0648\u0632",
    "\u06cc\u06a9 \u0631\u0648\u0632",
    "\u0686\u0646\u062f \u0631\u0648\u0632",
]
HANDOVER_TIMES = [
    "\u0641\u0648\u0631\u06cc (\u062a\u0627 \u0646\u06cc\u0645 \u0633\u0627\u0639\u062a)",
    "\u062a\u0627 \u0686\u0646\u062f \u0633\u0627\u0639\u062a",
    "\u0627\u0645\u0631\u0648\u0632",
    "\u0641\u0631\u062f\u0627 \u06cc\u0627 \u0628\u0639\u062f\u062a\u0631",
]
RETURN_TIMES = [
    "\u0627\u0645\u0631\u0648\u0632",
    "\u0641\u0631\u062f\u0627",
    "\u062a\u0627 \u06f2-\u06f3 \u0631\u0648\u0632",
    "\u062a\u0627 \u0647\u0641\u062a\u0647",
    "\u0639\u062c\u0644\u0647\u200c\u0627\u06cc \u0646\u06cc\u0633\u062a",
]
CRITERIA = [
    {"key": "price",          "label": "\U0001F4B0 \u062f\u0633\u062a\u0645\u0632\u062f \u0645\u0646\u0627\u0633\u0628"},
    {"key": "behavior",       "label": "\U0001F60A \u0627\u062e\u0644\u0627\u0642 \u062e\u0648\u0628"},
    {"key": "speed",          "label": "\u26A1 \u0633\u0631\u0639\u062a \u0639\u0645\u0644"},
    {"key": "quality",        "label": "\u2728 \u06a9\u06cc\u0641\u06cc\u062a \u06a9\u0627\u0631"},
    {"key": "punctuality",    "label": "\U0001F550 \u0648\u0642\u062a\u200C\u0634\u0646\u0627\u0633\u06cc"},
    {"key": "cleanliness",    "label": "\U0001F9F9 \u0646\u0638\u0627\u0641\u062a"},
    {"key": "warranty",       "label": "\U0001F6E1 \u0636\u0645\u0627\u0646\u062a \u06a9\u0627\u0631"},
    {"key": "responsiveness", "label": "\U0001F4DE \u067E\u0627\u0633\u062E\u06af\u0648\u06cc\u06cc"},
]

T = {
    "start": "\u0633\u0644\u0627\u0645! \u0628\u0647 \u0631\u0628\u0627\u062a \u0627\u062a\u0635\u0627\u0644 \u0645\u062a\u062e\u0635\u0635\u06cc\u0646 \u062e\u0648\u0634 \u0622\u0645\u062f\u06cc\u062f \U0001F44B",
    "reg": "\U0001F3EA \u062b\u0628\u062a\u200C\u0646\u0627\u0645 \u0645\u062a\u062e\u0635\u0635",
    "simple": "\U0001F50D \u062c\u0633\u062a\u062c\u0648\u06cc \u0633\u0627\u062f\u0647",
    "adv": "\U0001F50E \u062c\u0633\u062a\u062c\u0648\u06cc \u067E\u06cc\u0634\u0631\u0641\u062a\u0647",
    "list": "\U0001F4CB \u0644\u06cc\u0633\u062a \u0645\u062a\u062e\u0635\u0635\u06cc\u0646",
    "prof": "\U0001F464 \u067E\u0631\u0648\u0641\u0627\u06cc\u0644 \u0645\u0646",
    "elec": "\U0001F50C \u0644\u0648\u0627\u0632\u0645 \u0628\u0631\u0642\u06cc",
    "gas": "\U0001F525 \u0644\u0648\u0627\u0632\u0645 \u06af\u0627\u0632\u06cc",
    "cool": "\u2744\uFE0F \u0633\u0631\u0645\u0627\u06cc\u0634\u06cc \u0648 \u06af\u0631\u0645\u0627\u06cc\u0634\u06cc",
    "car": "\U0001F697 \u062e\u0648\u062f\u0631\u0648",
    "back": "\U0001F519 \u0628\u0627\u0632\u06af\u0634\u062a",
    "yes": "\u2705 \u0628\u0644\u0647",
    "no": "\u274C \u062e\u06cc\u0631",
    "choose": "\u06cc\u06a9 \u06af\u0632\u06cc\u0646\u0647 \u0631\u0627 \u0627\u0646\u062a\u062e\u0627\u0628 \u06a9\u0646\u06cc\u062f:",
    "ask_name": "\u0646\u0627\u0645 \u0648 \u0646\u0627\u0645 \u062e\u0627\u0646\u0648\u0627\u062f\u06af\u06cc:",
    "ask_phone": "\u0634\u0645\u0627\u0631\u0647 \u062a\u0645\u0627\u0633:",
    "ask_area": "\u0645\u062d\u062f\u0648\u062f\u0647 \u062e\u062f\u0645\u0627\u062a \u0631\u0627 \u062a\u0627\u06cc\u067e \u06a9\u0646\u06cc\u062f (\u0645\u062b\u0644\u0627\u064b \u062a\u0647\u0631\u0627\u0646\u060c \u0633\u0639\u0627\u062f\u062a\u200c\u0622\u0628\u0627\u062f):",
    "ask_location": "\u0628\u0631\u0627\u06cc \u062c\u0630\u0628 \u0645\u0634\u062a\u0631\u06cc\u0627\u0646 \u0628\u06cc\u0634\u062a\u0631\u060c \u062a\u0648\u0635\u06cc\u0647 \u0645\u06cc\u200c\u0634\u0648\u062f \u0645\u0648\u0642\u0639\u06cc\u062a \u0645\u06a9\u0627\u0646\u06cc \u062e\u0648\u062f \u0631\u0627 \u0647\u0645 \u062b\u0628\u062a \u06a9\u0646\u06cc\u062f.\n\u0622\u06cc\u0627 \u0645\u06cc\u200c\u062e\u0648\u0627\u0647\u06cc\u062f \u0627\u0644\u0627\u0646 \u062b\u0628\u062a \u06a9\u0646\u06cc\u062f\u061f",
    "ask_send_location": "\u0644\u0637\u0641\u0627\u064b \u0631\u0648\u06cc \u062f\u06a9\u0645\u0647 \u0632\u06cc\u0631 \u0628\u0632\u0646\u06cc\u062f \u062a\u0627 \u0645\u0648\u0642\u0639\u06cc\u062a\u062a\u0627\u0646 \u0627\u0631\u0633\u0627\u0644 \u0634\u0648\u062f:",
    "location_saved": "\u2705 \u0645\u0648\u0642\u0639\u06cc\u062a \u0634\u0645\u0627 \u062b\u0628\u062a \u0634\u062f.",
    "ask_onsite": "\u0622\u06cc\u0627 \u062f\u0631 \u0645\u062d\u0644 \u0645\u0634\u062a\u0631\u06cc \u062d\u0627\u0636\u0631 \u0645\u06cc\u200c\u0634\u0648\u06cc\u062f\u061f",
    "ask_cust_area": "\u0645\u062d\u062f\u0648\u062f\u0647 \u062e\u0648\u062f\u062a\u0627\u0646 \u0631\u0627 \u062a\u0627\u06cc\u067e \u06a9\u0646\u06cc\u062f \u06cc\u0627 \u0645\u0648\u0642\u0639\u06cc\u062a \u0628\u0641\u0631\u0633\u062a\u06cc\u062f:",
    "ask_desc": "\u0645\u0634\u06a9\u0644 \u0631\u0627 \u062a\u0648\u0636\u06cc\u062d \u0628\u062f\u0647\u06cc\u062f:",
    "ask_priority": "\u06a9\u062f\u0627\u0645 \u0645\u0639\u06cc\u0627\u0631\u0647\u0627 \u0645\u0647\u0645\u200c\u062a\u0631\u0647\u061f \u0634\u0645\u0627\u0631\u0647 \u0628\u0632\u0646\u06cc\u062f (\u0645\u062b\u0644\u0627\u064b 1,4). \u06cc\u0627 0 \u0628\u0631\u0627\u06cc \u0647\u06cc\u0686\u200c\u06a9\u062f\u0627\u0645.\n\n",
    "ask_handover": "\u0686\u0647 \u0632\u0645\u0627\u0646\u06cc \u0645\u06cc\u200c\u062e\u0648\u0627\u0647\u06cc\u062f \u062f\u0633\u062a\u06af\u0627\u0647 \u0631\u0627 \u062a\u062d\u0648\u06cc\u0644 \u0628\u062f\u0647\u06cc\u062f\u061f\n\n",
    "ask_return": "\u0686\u0647 \u0632\u0645\u0627\u0646\u06cc \u062f\u0633\u062a\u06af\u0627\u0647 \u0631\u0627 \u0644\u0627\u0632\u0645 \u062f\u0627\u0631\u06cc\u062f\u061f\n\n",
    "ask_phone_share": "\u0622\u06cc\u0627 \u0634\u0645\u0627\u0631\u0647 \u062a\u0645\u0627\u0633\u062a\u0627\u0646 \u0628\u0631\u0627\u06cc \u062a\u0639\u0645\u06cc\u0631\u06a9\u0627\u0631 \u0627\u0631\u0633\u0627\u0644 \u0634\u0648\u062f\u061f",
    "ask_phone_input": "\u0634\u0645\u0627\u0631\u0647 \u062a\u0645\u0627\u0633\u062a\u0627\u0646 \u0631\u0627 \u0648\u0627\u0631\u062f \u06a9\u0646\u06cc\u062f:",
    "ask_who_pick": "\u062e\u0648\u062f\u062a\u0627\u0646 \u062a\u0639\u0645\u06cc\u0631\u06a9\u0627\u0631 \u0631\u0627 \u0627\u0646\u062a\u062e\u0627\u0628 \u0645\u06cc\u200c\u06a9\u0646\u06cc\u062f \u06cc\u0627 \u0633\u06cc\u0633\u062a\u0645\u061f",
    "who_me": "\U0001F464 \u062e\u0648\u062f\u0645 \u0627\u0646\u062a\u062e\u0627\u0628 \u0645\u06cc\u200c\u06a9\u0646\u0645",
    "who_sys": "\U0001F916 \u0633\u06cc\u0633\u062a\u0645 \u0627\u0646\u062a\u062e\u0627\u0628 \u06a9\u0646\u062f",
    "reg_ok": "\u2705 \u062b\u0628\u062a\u200C\u0646\u0627\u0645 \u0627\u0646\u062c\u0627\u0645 \u0634\u062f!",
    "found": "\U0001F50D \u0645\u062a\u062e\u0635\u0635\u06cc\u0646 \u0628\u0631\u062a\u0631:\n\n",
    "not_found": "\u274C \u0645\u062a\u062e\u0635\u0635\u06cc \u067e\u06cc\u062f\u0627 \u0646\u0634\u062f.",
    "direct": "\n\u26A0\uFE0F \u0644\u0637\u0641\u0627\u064b \u0645\u0633\u062a\u0642\u06cc\u0645\u0627\u064b \u062a\u0645\u0627\u0633 \u0628\u06af\u06cc\u0631\u06cc\u062f.",
    "new_cust": "\U0001F514 \u0645\u0634\u062a\u0631\u06cc \u062c\u062f\u06cc\u062f!",
    "use_menu": "\u0627\u0632 \u0645\u0646\u0648 \u0627\u0633\u062a\u0641\u0627\u062f\u0647 \u06a9\u0646\u06cc\u062f.",
    "invalid": "\u0645\u0642\u062f\u0627\u0631 \u0645\u0639\u062a\u0628\u0631 \u0646\u06cc\u0633\u062a. \u062f\u0648\u0628\u0627\u0631\u0647 \u062a\u0644\u0627\u0634 \u06a9\u0646\u06cc\u062f.",
    "no_expert": "\u0647\u0646\u0648\u0632 \u0645\u062a\u062e\u0635\u0635\u06cc \u0646\u06cc\u0633\u062a.",
    "my_prof": "\U0001F464 \u067E\u0631\u0648\u0641\u0627\u06cc\u0644 \u0634\u0645\u0627:\n\n",
    "no_prof": "\u062b\u0628\u062a\u200C\u0646\u0627\u0645 \u0646\u06a9\u0631\u062f\u06cc\u062f.",
    "tracking": "\U0001F3AB \u06a9\u062f \u067E\u06cc\u06af\u06cc\u0631\u06cc: ",
    "tracking_note": "\n\n\u0644\u0637\u0641\u0627\u064b \u0647\u0646\u06af\u0627\u0645 \u0645\u0631\u0627\u062c\u0639\u0647 \u06a9\u062f \u0631\u0627 \u0628\u0647 \u062a\u0639\u0645\u06cc\u0631\u06a9\u0627\u0631 \u0628\u062f\u0647\u06cc\u062f.",
    "chosen_expert": "\U0001F464 \u062a\u0639\u0645\u06cc\u0631\u06a9\u0627\u0631 \u0627\u0646\u062a\u062e\u0627\u0628\u06cc:\n",
    "rate_ask": "\u0644\u0637\u0641\u0627\u064b \u0628\u0647 \u062a\u0639\u0645\u06cc\u0631\u06a9\u0627\u0631 \u0627\u0645\u062a\u06cc\u0627\u0632 \u062f\u0647\u06cc\u062f:",
    "rate_thx": "\U0001F64F \u0645\u0645\u0646\u0648\u0646!",
    "rate_start": "\u2B50 \u0627\u0645\u062a\u06cc\u0627\u0632 \u0628\u0647 ",
    "rate_select": "\n\u0627\u0645\u062a\u06cc\u0627\u0632 (\u06f1-\u06f5):",
    "rate_ok": "\u062b\u0628\u062a",
    "err": "\u062e\u0637\u0627",
    "choose_subs": "\u0634\u0645\u0627\u0631\u0647 \u062a\u062e\u0635\u0635\u200c\u0647\u0627 \u0631\u0627 \u0628\u0627 \u06a9\u0627\u0645\u0627 \u0628\u0646\u0648\u06cc\u0633\u06cc\u062f (\u0645\u062b\u0644\u0627\u064b 1,3):\n\n",
    "choose_sub": "\u0634\u0645\u0627\u0631\u0647 \u0646\u0648\u0639 \u062e\u0631\u0627\u0628\u06cc:\n\n",
    "priority": "\U0001F3AF \u0627\u0648\u0644\u0648\u06cc\u062a: ",
    "rating_avg": "\u2B50 \u0627\u0645\u062a\u06cc\u0627\u0632: ",
    "referral_count": "\U0001F4C8 \u062a\u0639\u062f\u0627\u062f \u0645\u0639\u0631\u0641\u06cc: ",
    "rating_stages": "\n\n\U0001F4CA \u0645\u0631\u0627\u062d\u0644 \u0646\u0638\u0631\u0633\u0646\u062c\u06cc:\n",
    "response_speed": "\u23F1 \u0633\u0631\u0639\u062a \u067E\u0627\u0633\u062E\u06AF\u0648\u06cc\u06cc:",
    "repair_time": "\U0001F527 \u0632\u0645\u0627\u0646 \u062a\u0639\u0645\u06cc\u0631:",
    "onsite": "\U0001F3E0 \u062d\u0636\u0648\u0631 \u062f\u0631 \u0645\u062d\u0644:",
    "role": "\U0001F4C2 \u062f\u0633\u062a\u0647:",
    "subspec": "\U0001F527 \u0632\u06cc\u0631\u062a\u062e\u0635\u0635:",
    "area": "\U0001F4CD \u0645\u062d\u062f\u0648\u062f\u0647:",
    "phone": "\U0001F4DE \u062a\u0644\u0641\u0646:",
    "name": "\U0001F464 \u0646\u0627\u0645:",
    "problem": "\U0001F4DD \u0645\u0634\u06a9\u0644:",
    "my_code": "\U0001F194 \u06a9\u062f \u0634\u0645\u0627: ",
    "my_link": "\U0001F517 \u0644\u06cc\u0646\u06a9 \u0634\u0645\u0627:\n",
    "share_hint": "\n\n\u0644\u06cc\u0646\u06a9 \u062e\u0648\u062f\u062a\u0627\u0646 \u0631\u0627 \u0628\u0631\u0627\u06cc \u0645\u0634\u062a\u0631\u06cc\u0627\u0646 \u0627\u0631\u0633\u0627\u0644 \u06a9\u0646\u06cc\u062f.\n\u0647\u0631 \u06a9\u0633 \u0628\u0631 \u0631\u0648\u06cc \u0644\u06cc\u0646\u06a9 \u0628\u0632\u0646\u062f \u0645\u0633\u062a\u0642\u06cc\u0645\u0627\u064b \u067e\u0631\u0648\u0641\u0627\u06cc\u0644 \u0634\u0645\u0627 \u0631\u0627 \u0645\u06cc\u200c\u0628\u06cc\u0646\u062f.",
    "share_btn": "\U0001F517 \u0646\u0645\u0627\u06cc\u0634 \u0644\u06cc\u0646\u06a9 \u0627\u0634\u062a\u0631\u0627\u06a9",    "copy_link_btn": "\U0001F4CB \u06a9\u067E\u06cc \u0644\u06cc\u0646\u06a9",
    "public_prof": "\U0001F464 \u067E\u0631\u0648\u0641\u0627\u06cc\u0644 \u0645\u062a\u062e\u0635\u0635:\n\n",
    "contact_expert": "\U0001F4DE \u062a\u0645\u0627\u0633 \u0628\u0627 \u062a\u0639\u0645\u06cc\u0631\u06a9\u0627\u0631",
    "expert_not_found": "\u274C \u0645\u062a\u062e\u0635\u0635\u06cc \u0628\u0627 \u0627\u06cc\u0646 \u06a9\u062f \u067e\u06cc\u062f\u0627 \u0646\u0634\u062f.",
    "welcome_via_link": "\u0634\u0645\u0627 \u0627\u0632 \u0637\u0631\u06cc\u0642 \u0644\u06cc\u0646\u06a9 \u0648\u0627\u0631\u062f \u0634\u062f\u06cc\u062f. \u0627\u06cc\u0646 \u067E\u0631\u0648\u0641\u0627\u06cc\u0644 \u0645\u062a\u062e\u0635\u0635 \u0645\u0648\u0631\u062f \u0646\u0638\u0631 \u0634\u0645\u0627\u0633\u062a:",
    "adm_title": "\U0001F510 \u067E\u0646\u0644 \u0645\u062f\u06cc\u0631\u06cc\u062a\n\u06cc\u06a9 \u06af\u0632\u06cc\u0646\u0647 \u0631\u0627 \u0627\u0646\u062a\u062e\u0627\u0628 \u06a9\u0646\u06cc\u062f:",
    "adm_stats": "\U0001F4CA \u0622\u0645\u0627\u0631 \u06a9\u0644\u06cc",
    "adm_experts": "\U0001F465 \u0644\u06cc\u0633\u062a \u0645\u062a\u062e\u0635\u0635\u06cc\u0646",
    "adm_jobs": "\U0001F4CB \u0622\u062e\u0631\u06cc\u0646 \u0645\u0639\u0631\u0641\u06cc\u200c\u0647\u0627",
    "adm_revenue": "\U0001F4B0 \u062f\u0631\u0622\u0645\u062f",
    "adm_exit": "\U0001F519 \u062e\u0631\u0648\u062c \u0627\u0632 \u067E\u0646\u0644",
    "adm_back": "\U0001F519 \u0628\u0627\u0632\u06af\u0634\u062a \u0628\u0647 \u067E\u0646\u0644",
    "adm_no_exp": "\u0647\u0646\u0648\u0632 \u0645\u062a\u062e\u0635\u0635\u06cc \u062b\u0628\u062a\u200c\u0646\u0627\u0645 \u0646\u06a9\u0631\u062f\u0647.",
    "adm_no_job": "\u0647\u0646\u0648\u0632 \u0645\u0639\u0631\u0641\u06cc\u200c\u0627\u06cc \u0627\u0646\u062c\u0627\u0645 \u0646\u0634\u062f\u0647.",
    "adm_not_auth": "\u0634\u0645\u0627 \u062f\u0633\u062a\u0631\u0633\u06cc \u0628\u0647 \u067E\u0646\u0644 \u0645\u062f\u06cc\u0631\u06cc\u062a \u0646\u062f\u0627\u0631\u06cc\u062f.",
    "adm_tog_on": "\u2705 \u0641\u0639\u0627\u0644 \u06a9\u0631\u062f\u0646",
    "adm_tog_off": "\u274C \u063a\u06cc\u0631\u0641\u0639\u0627\u0644 \u06a9\u0631\u062f\u0646",
    "adm_prem_on": "\u2B50 \u062f\u0627\u062f\u0646 \u0627\u0634\u062a\u0631\u0627\u06a9 \u0648\u06cc\u0698\u0647",
    "adm_prem_off": "\u2B50 \u06af\u0631\u0641\u062a\u0646 \u0627\u0634\u062a\u0631\u0627\u06a9 \u0648\u06cc\u0698\u0647",
    "adm_delete": "\U0001F5D1 \u062d\u0630\u0641 \u0645\u062a\u062e\u0635\u0635",
    "adm_deleted": "\u0645\u062a\u062e\u0635\u0635 \u062d\u0630\u0641 \u0634\u062f.",
    "adm_st_active": "\u2705 \u0641\u0639\u0627\u0644",
    "adm_st_inactive": "\u274C \u063a\u06cc\u0631\u0641\u0639\u0627\u0644",
    "adm_st_prem": "\u2B50 \u0648\u06cc\u0698\u0647",
    "adm_stats_total": "\u06a9\u0644 \u0645\u062a\u062e\u0635\u0635\u06cc\u0646: ",
    "adm_stats_active": "\u0641\u0639\u0627\u0644: ",
    "adm_stats_premium": "\u0648\u06cc\u0698\u0647: ",
    "adm_stats_referrals": "\u06a9\u0644 \u0645\u0639\u0631\u0641\u06cc\u200c\u0647\u0627: ",
    "adm_stats_jobs": "\u06a9\u0644 \u067e\u0631\u0648\u0698\u0647\u200c\u0647\u0627: ",
    "adm_stats_ratings": "\u06a9\u0644 \u0646\u0637\u0631\u0627\u062a \u062b\u0628\u062a\u200c\u0634\u062f\u0647: ",
    "adm_stats_customers": "\u0645\u0634\u062a\u0631\u06cc\u0627\u0646 \u06cc\u06a9\u062a\u0627: ",
    "adm_exp_detail": "\U0001F464 \u062c\u0632\u0626\u06cc\u0627\u062a \u0645\u062a\u062e\u0635\u0635:",
    "adm_revenue_note": "\u062f\u0631\u0622\u0645\u062f \u0628\u0631 \u0627\u0633\u0627\u0633 \u06f1\u06f0\u06f0\u0650\u06f0\u06f0\u06f0 \u062a\u0648\u0645\u0627\u0646 \u06a9\u0645\u06cc\u0633\u06cc\u0648\u0646 \u0641\u0631\u0636 \u0634\u062f\u0647 \u0627\u0633\u062a.",
    "adm_revenue_total": "\u062f\u0631\u0622\u0645\u062f \u062a\u062e\u0645\u06cc\u0646\u06cc: ",
    "adm_toman": " \u062a\u0648\u0645\u0627\u0646",
    "adm_jobs_list": "\U0001F4CB \u0622\u062e\u0631\u06cc\u0646 \u0645\u0639\u0631\u0641\u06cc\u200c\u0647\u0627:\n\n",
    "adm_exp_list": "\U0001F465 \u0644\u06cc\u0633\u062a \u0645\u062a\u062e\u0635\u0635\u06cc\u0646:\n(\u0631\u0648\u06cc \u0647\u0631 \u06a9\u062f\u0627\u0645 \u0628\u0632\u0646\u06cc\u062f)\n\n",
}

SUBS_ELEC = [
    "\u0645\u0627\u06a9\u0631\u0648\u0641\u0631 / \u0645\u0627\u06cc\u06a9\u0631\u0648\u0648\u06cc\u0648",
    "\u062a\u0648\u0633\u062a\u0631",
    "\u0641\u0631 \u0628\u0631\u0642\u06cc \u062a\u0648\u06a9\u0627\u0631",
    "\u062c\u0627\u0631\u0648\u0628\u0631\u0642\u06cc",
    "\u0686\u0627\u06cc\u200c\u0633\u0627\u0632 / \u06a9\u062a\u0631\u06cc \u0628\u0631\u0642\u06cc",
    "\u0642\u0647\u0648\u0647\u200c\u0633\u0627\u0632",
    "\u067e\u0644\u0648\u067e\u0632",
    "\u0633\u0631\u062e\u200c\u06a9\u0646 / \u0622\u06cc\u0631\u0641\u0631\u0627\u06cc\u0631",
    "\u0633\u0634\u0648\u0627\u0631",
    "\u0627\u062a\u0648 (\u0628\u062e\u0627\u0631\u0634\u0648\u060c \u067e\u0631\u0633\u060c \u0627\u06cc\u0633\u062a\u0627\u062f\u0647)",
    "\u0645\u0627\u0634\u06cc\u0646 \u0644\u0628\u0627\u0633\u0634\u0648\u06cc\u06cc",
    "\u0645\u0627\u0634\u06cc\u0646 \u0638\u0631\u0641\u0634\u0648\u06cc\u06cc",
    "\u062f\u0633\u062a\u06af\u0627\u0647 \u062a\u0635\u0641\u06cc\u0647 \u0622\u0628",
    "\u0622\u0628\u0633\u0631\u062f\u06a9\u0646",
    "\u062a\u0644\u0648\u06cc\u0632\u06cc\u0648\u0646",
    "\u0633\u0627\u06cc\u0631 \u0644\u0648\u0627\u0632\u0645 \u0628\u0631\u0642\u06cc",
]

SUBS_GAS = [
    "\u0627\u062c\u0627\u0642 \u06af\u0627\u0632",
    "\u0622\u0628\u06af\u0631\u0645\u06a9\u0646 \u062f\u06cc\u0648\u0627\u0631\u06cc",
    "\u0622\u0628\u06af\u0631\u0645\u06a9\u0646 \u0632\u0645\u06cc\u0646\u06cc",
    "\u0628\u062e\u0627\u0631\u06cc \u06af\u0627\u0632\u06cc",
    "\u067e\u06a9\u06cc\u062c \u0634\u0648\u0641\u0627\u0698",
    "\u0634\u0648\u0645\u06cc\u0646\u0647 \u06af\u0627\u0632\u06cc",
    "\u0633\u0627\u06cc\u0631 \u0644\u0648\u0627\u0632\u0645 \u06af\u0627\u0632\u06cc",
]
SUBS_COOL = [
    "\u06cc\u062e\u0686\u0627\u0644 \u0648 \u0641\u0631\u06cc\u0632\u0631",
    "\u06a9\u0648\u0644\u0631 \u0622\u0628\u06cc",
    "\u06a9\u0648\u0644\u0631 \u06af\u0627\u0632\u06cc (\u0627\u0633\u067e\u0644\u06cc\u062a)",
    "\u0686\u06cc\u0644\u0631",
    "\u0631\u0627\u062f\u06cc\u0627\u062a\u0648\u0631",
    "\u0633\u0627\u06cc\u0631 \u0633\u0631\u0645\u0627\u06cc\u0634\u06cc",
]
SUBS_CAR = [
    "\u062c\u0644\u0648\u0628\u0646\u062f\u06cc\u200c\u0633\u0627\u0632",
    "\u062a\u0646\u0638\u06cc\u0645 \u0645\u0648\u062a\u0648\u0631",
    "\u062a\u0639\u0645\u06cc\u0631 \u062a\u0631\u0645\u0632",
    "\u062a\u0639\u0645\u06cc\u0631 \u0641\u0631\u0645\u0627\u0646",
    "\u0628\u0631\u0642 \u062e\u0648\u062f\u0631\u0648",
    "\u0628\u0627\u062a\u0631\u06cc\u200c\u0633\u0627\u0632",
    "\u0622\u067e\u0627\u0631\u0627\u062a\u06cc (\u067e\u0646\u0686\u0631\u06af\u06cc\u0631\u06cc)",
    "\u062a\u0639\u0648\u06cc\u0636 \u0631\u0648\u063a\u0646\u060c \u0641\u06cc\u0644\u062a\u0631 \u0648 \u0633\u0631\u0648\u06cc\u0633",
    "\u0645\u06a9\u0627\u0646\u06cc\u06a9\u06cc (\u062a\u0639\u0645\u06cc\u0631\u0627\u062a \u0645\u0648\u062a\u0648\u0631)",
    "\u06af\u06cc\u0631\u0628\u06a9\u0633 \u0648 \u06a9\u0644\u0627\u0686",
    "\u06a9\u0645\u06a9\u200c\u0641\u0646\u0631 \u0648 \u0641\u0646\u0631",
    "\u0627\u06af\u0632\u0648\u0632",
    "\u06a9\u0648\u0644\u0631 \u0648 \u0628\u062e\u0627\u0631\u06cc \u062e\u0648\u062f\u0631\u0648",
    "\u062f\u06cc\u0627\u06af \u0648 \u0639\u06cc\u0628\u200c\u06cc\u0627\u0628\u06cc",
    "\u0635\u0627\u0641\u06a9\u0627\u0631\u06cc",
    "\u0646\u0642\u0627\u0634\u06cc \u062e\u0648\u062f\u0631\u0648",
    "\u0633\u0627\u06cc\u0631 \u062e\u062f\u0645\u0627\u062a \u062e\u0648\u062f\u0631\u0648",
]
STAGE_DAYS = {0: 30, 1: 150}
COMMISSION = 100000


def load_db():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

def save_db(d):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=2)

def load_jobs():
    try:
        with open(JOBS_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

def save_jobs(d):
    with open(JOBS_FILE, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=2)

def find_expert(uid):
    for e in load_db():
        if e.get("user_id") == uid: return e
    return None

def find_expert_by_code(code):
    for e in load_db():
        if e.get("expert_code") == code: return e
    return None

def is_admin(uid):
    return uid == ADMIN_ID

def gen_code():
    while True:
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not any(j.get("tracking_code") == code for j in load_jobs()):
            return code

def gen_expert_code(name):
    base = "".join(c for c in name if c.isascii() and c.isalnum()).lower()
    if len(base) < 4:
        base = "expert"
    chars = string.ascii_lowercase + string.digits
    for _ in range(50):
        code = base[:6] + "".join(random.choices(chars, k=4))
        if not any(e.get("expert_code") == code for e in load_db()):
            return code
    while True:
        code = "".join(random.choices(chars, k=8))
        if not any(e.get("expert_code") == code for e in load_db()):
            return code

def get_me():
    global BOT_USERNAME
    try:
        r = api_call("getMe")
        if r.get("ok"):
            BOT_USERNAME = r["result"].get("username", "")
            print("Bot username:", BOT_USERNAME)
    except Exception as ex:
        print("getMe error:", str(ex)[:100])

def expert_link(code):
    if BOT_USERNAME:
        return "https://ble.ir/" + BOT_USERNAME + "?start=" + code
    return "https://ble.ir/yourbot?start=" + code

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


def avg_crit(e, key):
    t = 0; c = 0
    for s in ["0","1","2"]:
        r = e.get("ratings_by_stage",{}).get(s,{}).get(key,{})
        t += r.get("sum",0); c += r.get("count",0)
    return 5.0 if c == 0 else t / c

def overall_rating(e):
    t = 0; c = 0
    for cr in CRITERIA:
        rt = 0; rc = 0
        for s in ["0","1","2"]:
            r = e.get("ratings_by_stage",{}).get(s,{}).get(cr["key"],{})
            rt += r.get("sum",0); rc += r.get("count",0)
        if rc > 0: t += rt / rc; c += 1
    return 5.0 if c == 0 else t / c

def total_reviews(e):
    mx = 0
    for cr in CRITERIA:
        cnt = 0
        for s in ["0","1","2"]:
            cnt += e.get("ratings_by_stage",{}).get(s,{}).get(cr["key"],{}).get("count",0)
        mx = max(mx, cnt)
    return mx

def priority_rating(e, priorities):
    if not priorities: return 5.0
    t = 0; c = 0
    for k in priorities:
        rt = 0; rc = 0
        for s in ["0","1","2"]:
            r = e.get("ratings_by_stage",{}).get(s,{}).get(k,{})
            rt += r.get("sum",0); rc += r.get("count",0)
        if rc > 0: t += rt / rc; c += 1
    return 5.0 if c == 0 else t / c

def stage_stats(e, st):
    t = 0; c = 0
    sd = e.get("ratings_by_stage",{}).get(str(st),{})
    for cr in CRITERIA:
        r = sd.get(cr["key"],{})
        if r.get("count",0) > 0: t += r["sum"] / r["count"]; c += 1
    return (None,0) if c == 0 else (t/c, c)

def rank_score(e, priorities=None):
    s = (priority_rating(e,priorities)*40 + overall_rating(e)*10) if priorities else overall_rating(e)*20
    if e.get("is_premium"): s += 50
    if e.get("works_on_site"): s += 10
    return s

def rating_breakdown(e, priorities=None):
    lines = []
    for cr in CRITERIA:
        a = avg_crit(e, cr["key"]); s = round(a)
        m = "\U0001F3AF " if priorities and cr["key"] in priorities else ""
        lines.append(m + cr["label"] + " " + ("\u2B50"*s) + " ({:.1f})".format(a))
    return "\n".join(lines)


def matches_times(e, handover, return_t):
    if handover is not None and handover < 3:
        rp = int(e.get("response_speed", 3))
        if handover == 0 and rp > 0: return False
        if handover == 1 and rp > 1: return False
        if handover == 2 and rp > 2: return False
    return True

def find_matching(category, sub, area, same_area, needs_onsite, priorities, handover=None, cust_lat=None, cust_lng=None):
    all_match = []; loc_match = []; text_match = []
    for e in load_db():
        if not e.get("active", True): continue
        if e.get("category") != category: continue
        if sub not in e.get("sub_specialties", []): continue
        if needs_onsite and not e.get("works_on_site", False): continue
        if not matches_times(e, handover, None): continue
        all_match.append(e)
        if cust_lat and cust_lng and e.get("lat") and e.get("lng"):
            if haversine(cust_lat, cust_lng, e["lat"], e["lng"]) <= 20: loc_match.append(e)
        elif area:
            e_area = e.get("area", "")
            if area in e_area or e_area in area:
                text_match.append(e)
            else:
                a_w = set(area.replace("\u060c", " ").replace(",", " ").split())
                e_w = set(e_area.replace("\u060c", " ").replace(",", " ").split())
                if a_w & e_w: text_match.append(e)
    if cust_lat and cust_lng:
        res = loc_match if loc_match else (text_match if text_match else all_match)
    elif area:
        res = text_match if text_match else all_match
    else:
        res = all_match
    res.sort(key=lambda x: rank_score(x, priorities), reverse=True)
    return res[:3]

def format_expert_line(e, idx, priorities, show_times=True):
    s = "{}. ".format(idx) + "\U0001F464 " + e["name"] + "\n"
    s += "   " + T["phone"] + " " + e["phone"] + "\n"
    s += "   " + T["area"] + " " + e["area"] + "\n"
    s += "   " + T["rating_avg"] + "{:.1f}/5".format(overall_rating(e))
    rv = total_reviews(e)
    if rv > 0: s += " (" + str(rv) + " \u0646\u0638\u0631)"
    s += "\n"
    if priorities:
        s += "   \U0001F3AF " + "{:.1f}".format(priority_rating(e, priorities)) + "/5\n"
    if e.get("works_on_site"): s += "   \U0001F3E0 \u062d\u0636\u0648\u0631 \u062f\u0631 \u0645\u062d\u0644\n"
    if show_times:
        s += "   " + T["response_speed"] + " " + RESPONSE_TIMES[int(e.get("response_speed",0))] + "\n"
        s += "   " + T["repair_time"] + " " + REPAIR_TIMES[int(e.get("repair_time",0))] + "\n"
    return s

def format_public_profile(e):
    r = T["public_prof"]
    r += T["name"] + " " + e.get("name","?") + "\n"
    r += T["role"] + " " + e.get("category","?") + "\n"
    r += T["subspec"] + " " + "\u060c ".join(e.get("sub_specialties",[])) + "\n"
    r += T["area"] + " " + e.get("area","?") + "\n"
    r += T["phone"] + " " + e.get("phone","?") + "\n"
    r += T["onsite"] + " " + (T["yes"] if e.get("works_on_site") else T["no"]) + "\n"
    r += T["response_speed"] + " " + RESPONSE_TIMES[int(e.get("response_speed",0))] + "\n"
    r += T["repair_time"] + " " + REPAIR_TIMES[int(e.get("repair_time",0))] + "\n\n"
    r += "\u2B50 {:.1f}/5".format(overall_rating(e))
    rv = total_reviews(e)
    if rv > 0: r += " (" + str(rv) + " \u0646\u0638\u0631)"
    r += "\n" + T["referral_count"] + str(e.get("referral_count",0)) + "\n\n"
    r += rating_breakdown(e)
    return r


def api_call(m, jd=None):
    url = API_URL + "/" + m
    for attempt in range(3):
        try:
            if jd is not None:
                r = session.post(url, json=jd, timeout=60)
            else:
                r = session.post(url, timeout=60)
            return r.json()
        except Exception as ex:
            print("[" + m + "] attempt " + str(attempt+1) + ": " + str(ex)[:100])
            time.sleep(5)
    return {"ok": False}

def send_message(chat_id, text, reply_markup=None):
    d = {"chat_id": chat_id, "text": text}
    if reply_markup: d["reply_markup"] = reply_markup
    api_call("sendMessage", d)

def answer_callback(cb_id, text=None):
    d = {"callback_query_id": cb_id}
    if text: d["text"] = text
    api_call("answerCallbackQuery", d)


def kb_main():
    return {"keyboard": [
        [{"text": T["reg"]}],
        [{"text": T["simple"]}],
        [{"text": T["adv"]}],
        [{"text": T["list"]}, {"text": T["prof"]}]
    ], "resize_keyboard": True}

def kb_cat():
    return {"keyboard": [
        [{"text": T["elec"]}],
        [{"text": T["gas"]}],
        [{"text": T["cool"]}],
        [{"text": T["car"]}],
        [{"text": T["back"]}]
    ], "resize_keyboard": True, "one_time_keyboard": True}

def kb_yn():
    return {"keyboard": [[{"text": T["yes"]}, {"text": T["no"]}], [{"text": T["back"]}]],
            "resize_keyboard": True, "one_time_keyboard": True}

def kb_back():
    return {"keyboard": [[{"text": T["back"]}]], "resize_keyboard": True}

def kb_area():
    return {"keyboard": [
        [{"text": "\U0001F4CD \u0627\u0631\u0633\u0627\u0644 \u0645\u0648\u0642\u0639\u06cc\u062a \u0645\u0646", "request_location": True}],
        [{"text": T["back"]}]
    ], "resize_keyboard": True, "one_time_keyboard": True}

def kb_area_text():
    return {"keyboard": [[{"text": T["back"]}]], "resize_keyboard": True}

def kb_who():
    return {"keyboard": [[{"text": T["who_me"]}], [{"text": T["who_sys"]}], [{"text": T["back"]}]],
            "resize_keyboard": True, "one_time_keyboard": True}

def kb_stars(ck):
    return {"inline_keyboard": [[
        {"text": "1\u2B50", "callback_data": "crit:" + ck + ":1"},
        {"text": "2\u2B50", "callback_data": "crit:" + ck + ":2"},
        {"text": "3\u2B50", "callback_data": "crit:" + ck + ":3"},
        {"text": "4\u2B50", "callback_data": "crit:" + ck + ":4"},
        {"text": "5\u2B50", "callback_data": "crit:" + ck + ":5"}
    ]]}

def kb_admin():
    return {"keyboard": [
        [{"text": T["adm_stats"]}],
        [{"text": T["adm_experts"]}],
        [{"text": T["adm_jobs"]}],
        [{"text": T["adm_revenue"]}],
        [{"text": T["adm_exit"]}]
    ], "resize_keyboard": True}

def kb_share_link(url):
    return {"inline_keyboard": [
        [{"text": T["share_btn"], "url": url}],
        [{"text": T["copy_link_btn"], "copy_text": {"text": url}}]
    ]}


def get_subs(cat_text):
    return {T["elec"]: SUBS_ELEC, T["gas"]: SUBS_GAS, T["cool"]: SUBS_COOL, T["car"]: SUBS_CAR}.get(cat_text, [])

def valid_cat(text):
    return text in [T["elec"], T["gas"], T["cool"], T["car"]]

def parse_nums(text, mx):
    text = text.replace("\u060c", ",").replace(" ", ",")
    res = []
    for p in text.split(","):
        p = p.strip()
        if not p: continue
        try:
            n = int(p)
            if 1 <= n <= mx: res.append(n)
        except: pass
    return res

def parse_priority(text):
    text = text.strip().replace("\u060c", ",").replace(" ", ",")
    if text == "0" or text == "": return []
    keys = []
    for p in text.split(","):
        p = p.strip()
        if not p: continue
        try:
            n = int(p)
            if 1 <= n <= len(CRITERIA): keys.append(CRITERIA[n-1]["key"])
        except: pass
    return keys

def fmt_list(lst):
    return "\n".join(["{}. {}".format(i, s) for i, s in enumerate(lst, 1)])

def fmt_criteria():
    return "\n".join(["{}. {}".format(i, c["label"]) for i, c in enumerate(CRITERIA, 1)])

def parse_single(text, mx):
    n = parse_nums(text, mx)
    return None if len(n) != 1 else n[0] - 1


PREV_STEP = {
    "reg_cat": None, "reg_subs": "reg_cat", "reg_name": "reg_subs",
    "reg_phone": "reg_name", "reg_area": "reg_phone", "reg_ask_location": "reg_area",
    "reg_location": "reg_ask_location", "reg_onsite": "reg_ask_location",
    "reg_response": "reg_onsite", "reg_repair": "reg_response",
    "req_cat": None, "req_sub": "req_cat", "req_priority": "req_sub",
    "req_handover": "req_priority", "req_return": "req_handover",
    "req_area": "req_sub", "req_desc": "req_area",
    "req_phone_share": "req_desc", "req_phone_input": "req_phone_share",
    "req_who": "req_phone_share",
}

def ask_for_step(chat_id, step, d):
    if step == "reg_cat": send_message(chat_id, T["choose"], kb_cat())
    elif step == "reg_subs": send_message(chat_id, T["choose_subs"] + fmt_list(d.get("_subs", [])), kb_back())
    elif step == "reg_name": send_message(chat_id, T["ask_name"], kb_back())
    elif step == "reg_phone": send_message(chat_id, T["ask_phone"], kb_back())
    elif step == "reg_area": send_message(chat_id, T["ask_area"], kb_area_text())
    elif step == "reg_ask_location": send_message(chat_id, T["ask_location"], kb_yn())
    elif step == "reg_location": send_message(chat_id, T["ask_send_location"], kb_area())
    elif step == "reg_onsite": send_message(chat_id, T["ask_onsite"], kb_yn())
    elif step == "reg_response": send_message(chat_id, T["response_speed"] + "\n\n" + fmt_list(RESPONSE_TIMES), kb_back())
    elif step == "reg_repair": send_message(chat_id, T["repair_time"] + "\n\n" + fmt_list(REPAIR_TIMES), kb_back())
    elif step == "req_cat": send_message(chat_id, T["choose"], kb_cat())
    elif step == "req_sub": send_message(chat_id, T["choose_sub"] + fmt_list(d.get("_subs", [])), kb_back())
    elif step == "req_priority": send_message(chat_id, T["ask_priority"] + fmt_criteria(), kb_back())
    elif step == "req_handover": send_message(chat_id, T["ask_handover"] + fmt_list(HANDOVER_TIMES), kb_back())
    elif step == "req_return": send_message(chat_id, T["ask_return"] + fmt_list(RETURN_TIMES), kb_back())
    elif step == "req_area": send_message(chat_id, T["ask_cust_area"], kb_area())
    elif step == "req_desc": send_message(chat_id, T["ask_desc"], kb_back())
    elif step == "req_phone_share": send_message(chat_id, T["ask_phone_share"], kb_yn())
    elif step == "req_phone_input": send_message(chat_id, T["ask_phone_input"], kb_back())
    elif step == "req_who": send_message(chat_id, T["ask_who_pick"], kb_who())


def create_job(cust_id, chat_id, expert, info):
    jobs = load_jobs()
    code = gen_code()
    now = int(time.time())
    jobs.append({
        "id": "{}_{}".format(cust_id, now),
        "tracking_code": code,
        "customer_id": cust_id,
        "customer_chat_id": chat_id,
        "expert_id": expert["user_id"],
        "expert_name": expert.get("name", "?"),
        "created_at": now,
        "stage": 0,
        "next_at": now + STAGE_DAYS[0] * 86400,
        "sent_for_stage": 0,
        "info": info,
    })
    save_jobs(jobs)
    inc_referral(expert["user_id"])
    return code

def inc_referral(expert_id):
    db = load_db()
    for e in db:
        if e.get("user_id") == expert_id:
            e["referral_count"] = e.get("referral_count", 0) + 1
            break
    save_db(db)

def notify_expert(expert, info, code, send_phone):
    msg = T["new_cust"] + "\n\n"
    msg += T["role"] + " " + info.get("category", "?") + "\n"
    msg += T["subspec"] + " " + info.get("sub", "?") + "\n"
    if info.get("area"): msg += T["area"] + " " + info["area"] + "\n"
    msg += T["problem"] + " " + info.get("desc", "") + "\n\n"
    msg += T["tracking"] + code
    if send_phone and info.get("phone"):
        msg += "\n\n\U0001F4DE \u062a\u0645\u0627\u0633 \u0645\u0634\u062a\u0631\u06cc: " + info["phone"]
    else:
        msg += "\n\n\u2139\uFE0F \u0645\u0634\u062a\u0631\u06cc \u062e\u0648\u062f\u0634 \u0628\u0627 \u0634\u0645\u0627 \u062a\u0645\u0627\u0633 \u0645\u06cc\u200c\u06af\u06cc\u0631\u062f."
    send_message(expert["user_id"], msg)


def apply_rating(expert_id, cr, stage):
    db = load_db()
    for e in db:
        if e.get("user_id") == expert_id:
            if "ratings_by_stage" not in e: e["ratings_by_stage"] = {}
            sd = e["ratings_by_stage"].setdefault(str(stage), {})
            for k, v in cr.items():
                if k not in sd: sd[k] = {"sum": 0, "count": 0}
                sd[k]["sum"] += v; sd[k]["count"] += 1
            break
    save_db(db)

def advance_job(cust_id, expert_id):
    jobs = load_jobs(); now = int(time.time())
    for j in jobs:
        if j.get("customer_id") == cust_id and j.get("expert_id") == expert_id:
            if j.get("sent_for_stage", 0) > j.get("stage", 0):
                ns = j.get("stage", 0) + 1; j["stage"] = ns
                j["next_at"] = now + STAGE_DAYS[1]*86400 if ns == 1 else 0
                break
    save_jobs(jobs)

def get_pending_job(cust_id, expert_id):
    for j in load_jobs():
        if j.get("customer_id") == cust_id and j.get("expert_id") == expert_id:
            if j.get("sent_for_stage", 0) > j.get("stage", 0) and j.get("stage", 0) < 2:
                return j
    return None

def ask_next(chat_id, uid, expert):
    st = rating_states.get(uid)
    if not st: return
    for c in CRITERIA:
        if c["key"] not in st["ratings"]:
            send_message(chat_id, c["label"] + T["rate_select"], kb_stars(c["key"])); return
    finalize_rating(chat_id, uid, expert)

def finalize_rating(chat_id, uid, expert):
    st = rating_states.pop(uid, None)
    if not st: return
    stage = st.get("stage", 0)
    apply_rating(expert["user_id"], st["ratings"], stage)
    if stage != 0: advance_job(uid, expert["user_id"])
    txt = T["rate_thx"] + "\n\n" + expert["name"] + ":\n\n"
    for c in CRITERIA:
        s = st["ratings"].get(c["key"], 0)
        txt += c["label"] + ": " + ("\u2B50"*s) + "\n"
    send_message(chat_id, txt, kb_main())

def check_followups():
    jobs = load_jobs(); now = int(time.time()); ch = False
    for j in jobs:
        if j.get("stage",0) >= 2: continue
        if j.get("sent_for_stage",0) > j.get("stage",0): continue
        if j.get("next_at",0) > now: continue
        st = j.get("stage",0)
        if st == 0:
            msg = "\U0001F514 \u06cc\u06a9 \u0645\u0627\u0647 \u0627\u0632 \u062e\u062f\u0645\u0627\u062a " + j.get("expert_name","?") + " \u06af\u0630\u0634\u062a.\n\u0646\u0638\u0631 \u062c\u062f\u06cc\u062f\u062a\u0627\u0646 \u0686\u06cc\u0647\u061f"
        else:
            msg = "\U0001F514 \u0634\u0634 \u0645\u0627\u0647 \u0627\u0632 \u062e\u062f\u0645\u0627\u062a " + j.get("expert_name","?") + " \u06af\u0630\u0634\u062a.\n\u0646\u0638\u0631 \u0628\u0644\u0646\u062f\u0645\u062f\u062a \u0634\u0645\u0627 \u0628\u0631\u0627\u06cc \u0645\u0627 \u0627\u0631\u0632\u0634\u0645\u0646\u062f\u0647."
        kb = {"inline_keyboard": [[{"text": "\u2B50 \u062b\u0628\u062a \u0646\u0638\u0631 \u062c\u062f\u06cc\u062f", "callback_data": "frate:" + str(j["expert_id"])}]]}
        send_message(j["customer_chat_id"], msg, kb)
        j["sent_for_stage"] = st + 1; ch = True
    if ch: save_jobs(jobs)


def deliver_expert(chat_id, uid, expert, info, send_phone):
    code = create_job(uid, chat_id, expert, info)
    msg = T["chosen_expert"]
    msg += "\U0001F464 " + expert["name"] + "\n"
    msg += T["phone"] + " " + expert["phone"] + "\n"
    msg += T["area"] + " " + expert.get("area", "?") + "\n"
    msg += T["tracking"] + code
    msg += T["tracking_note"]
    send_message(chat_id, msg, kb_main())
    notify_expert(expert, info, code, send_phone)
    rate_kb = {"inline_keyboard": [[
        {"text": T["rate_start"] + expert["name"], "callback_data": "rate:" + str(expert["user_id"])}
    ]]}
    send_message(chat_id, T["rate_ask"], rate_kb)


def admin_stats(chat_id):
    db = load_db(); jobs = load_jobs()
    total = len(db); active = sum(1 for e in db if e.get("active", True))
    premium = sum(1 for e in db if e.get("is_premium"))
    refs = sum(e.get("referral_count", 0) for e in db)
    customers = len(set(j.get("customer_id") for j in jobs))
    ratings = 0
    for e in db:
        for st in ["0", "1", "2"]:
            for cr in CRITERIA:
                ratings += e.get("ratings_by_stage", {}).get(st, {}).get(cr["key"], {}).get("count", 0)
    txt = T["adm_stats"] + ":\n\n"
    txt += "\U0001F465 " + T["adm_stats_total"] + str(total) + "\n"
    txt += "\u2705 " + T["adm_stats_active"] + str(active) + "\n"
    txt += "\u2B50 " + T["adm_stats_premium"] + str(premium) + "\n"
    txt += "\U0001F4C8 " + T["adm_stats_referrals"] + str(refs) + "\n"
    txt += "\U0001F4CB " + T["adm_stats_jobs"] + str(len(jobs)) + "\n"
    txt += "\U0001F4DD " + T["adm_stats_ratings"] + str(ratings) + "\n"
    txt += "\U0001F464 " + T["adm_stats_customers"] + str(customers)
    send_message(chat_id, txt, kb_admin())

def admin_experts_list(chat_id):
    db = load_db()
    if not db:
        send_message(chat_id, T["adm_no_exp"], kb_admin()); return
    kb = {"inline_keyboard": []}
    for i, e in enumerate(db[:15], 1):
        star = "\u2B50" if e.get("is_premium") else ""
        stat = "\u2705" if e.get("active", True) else "\u274C"
        label = "{}. {} {} {} | {:.1f}".format(i, stat, star, e.get("name", "?"), overall_rating(e))
        kb["inline_keyboard"].append([{"text": label, "callback_data": "adm:exp:" + str(e["user_id"])}])
    send_message(chat_id, T["adm_exp_list"], kb)

def admin_expert_detail(chat_id, expert_id):
    e = find_expert(expert_id)
    if not e:
        send_message(chat_id, "\u0645\u062a\u062e\u0635\u0635 \u067e\u06cc\u062f\u0627 \u0646\u0634\u062f.", kb_admin()); return
    txt = T["adm_exp_detail"] + "\n\n"
    txt += T["name"] + " " + e.get("name", "?") + "\n"
    txt += T["phone"] + " " + e.get("phone", "?") + "\n"
    txt += T["role"] + " " + e.get("category", "?") + "\n"
    txt += T["subspec"] + " " + "\u060c ".join(e.get("sub_specialties", [])) + "\n"
    txt += T["area"] + " " + e.get("area", "?") + "\n"
    txt += "\u2B50 " + T["rating_avg"] + "{:.1f}/5".format(overall_rating(e)) + "\n"
    txt += "\U0001F4C8 " + T["referral_count"] + str(e.get("referral_count", 0)) + "\n"
    txt += "\U0001F194 " + e.get("expert_code", "?") + "\n"
    txt += "\U0001F4F1 " + str(e["user_id"]) + "\n"
    status = T["adm_st_active"] if e.get("active", True) else T["adm_st_inactive"]
    txt += "\u2699 " + status + "\n"
    if e.get("is_premium"): txt += T["adm_st_prem"] + "\n"
    kb = {"inline_keyboard": [
        [{"text": T["adm_tog_off"] if e.get("active", True) else T["adm_tog_on"], "callback_data": "adm:tog:" + str(expert_id)}],
        [{"text": T["adm_prem_off"] if e.get("is_premium") else T["adm_prem_on"], "callback_data": "adm:prem:" + str(expert_id)}],
        [{"text": T["adm_delete"], "callback_data": "adm:del:" + str(expert_id)}],
        [{"text": T["adm_back"], "callback_data": "adm:back"}]
    ]}
    send_message(chat_id, txt, kb)

def admin_jobs(chat_id):
    jobs = load_jobs()
    if not jobs:
        send_message(chat_id, T["adm_no_job"], kb_admin()); return
    txt = T["adm_jobs_list"]
    for j in jobs[-10:][::-1]:
        txt += "\U0001F3AB " + j.get("tracking_code", "?") + "\n"
        txt += "   \U0001F464 " + j.get("expert_name", "?") + "\n"
        info = j.get("info", {})
        if info.get("category"): txt += "   " + T["role"] + " " + info["category"] + "\n"
        if info.get("sub"): txt += "   " + T["subspec"] + " " + info["sub"] + "\n"
        txt += "\n"
    send_message(chat_id, txt, kb_admin())

def admin_revenue(chat_id):
    db = load_db()
    refs = sum(e.get("referral_count", 0) for e in db)
    total = refs * COMMISSION
    txt = T["adm_revenue"] + ":\n\n"
    txt += "\U0001F4C8 " + T["adm_stats_referrals"] + str(refs) + "\n"
    txt += "\U0001F4B0 " + T["adm_revenue_total"] + "{:,}".format(total) + T["adm_toman"] + "\n\n"
    txt += "\u2139\uFE0F " + T["adm_revenue_note"]
    send_message(chat_id, txt, kb_admin())

def admin_toggle_active(expert_id, chat_id):
    db = load_db()
    for e in db:
        if e.get("user_id") == expert_id:
            e["active"] = not e.get("active", True); break
    save_db(db)
    admin_expert_detail(chat_id, expert_id)

def admin_toggle_premium(expert_id, chat_id):
    db = load_db()
    for e in db:
        if e.get("user_id") == expert_id:
            e["is_premium"] = not e.get("is_premium", False); break
    save_db(db)
    admin_expert_detail(chat_id, expert_id)

def admin_delete(expert_id, chat_id):
    db = [e for e in load_db() if e.get("user_id") != expert_id]
    save_db(db)
    send_message(chat_id, T["adm_deleted"], kb_admin())


def show_my_link(chat_id, uid):
    e = find_expert(uid)
    if not e:
        send_message(chat_id, T["no_prof"], kb_main()); return
    code = e.get("expert_code", "")
    if not code:
        code = gen_expert_code(e.get("name", "expert"))
        db = load_db()
        for x in db:
            if x.get("user_id") == uid:
                x["expert_code"] = code; break
        save_db(db)
    link = expert_link(code)
    txt = T["my_code"] + code + "\n\n" + T["my_link"] + link + T["share_hint"]
    send_message(chat_id, txt, kb_share_link(link))


def handle_message(msg):
    chat_id = msg["chat"]["id"]
    uid = msg["from"]["id"]
    text = msg.get("text", "")
    print(">>>", uid, text[:30].encode("ascii", "replace").decode())

    loc = msg.get("location")
    if loc and uid in user_states:
        st = user_states[uid]
        if st["step"] == "reg_area":
            send_message(chat_id, T["ask_area"] + "\n\n\u0627\u0628\u062a\u062f\u0627 \u0622\u062f\u0631\u0633 \u0645\u062a\u0646\u06cc \u0631\u0627 \u0648\u0627\u0631\u062f \u06a9\u0646\u06cc\u062f.", kb_area_text()); return
        if st["step"] == "reg_location":
            st["data"]["lat"] = loc.get("latitude"); st["data"]["lng"] = loc.get("longitude")
            st["step"] = "reg_onsite"
            send_message(chat_id, T["location_saved"])
            send_message(chat_id, T["ask_onsite"], kb_yn()); return
        if st["step"] == "req_area":
            st["data"]["lat"] = loc.get("latitude"); st["data"]["lng"] = loc.get("longitude")
            st["data"]["area"] = st["data"].get("area", "")
            st["step"] = "req_desc"; send_message(chat_id, T["ask_desc"]); return

    if text.startswith("/start "):
        payload = text[7:].strip()
        user_states.pop(uid, None)
        if payload:
            e = find_expert_by_code(payload)
            if e:
                send_message(chat_id, T["welcome_via_link"])
                send_message(chat_id, format_public_profile(e), kb_main())
                viewing_expert[uid] = e["user_id"]
                return
            else:
                send_message(chat_id, T["expert_not_found"])
        send_message(chat_id, T["start"], kb_main())
        return

    if text == "/start":
        user_states.pop(uid, None)
        send_message(chat_id, T["start"], kb_main()); return

    if text == "/admin":
        if not is_admin(uid):
            send_message(chat_id, T["adm_not_auth"]); return
        user_states.pop(uid, None)
        send_message(chat_id, T["adm_title"], kb_admin()); return

    if is_admin(uid):
        if text == T["adm_exit"]:
            user_states.pop(uid, None); send_message(chat_id, T["use_menu"], kb_main()); return
        if text == T["adm_stats"]: admin_stats(chat_id); return
        if text == T["adm_experts"]: admin_experts_list(chat_id); return
        if text == T["adm_jobs"]: admin_jobs(chat_id); return
        if text == T["adm_revenue"]: admin_revenue(chat_id); return

    if text == T["reg"]:
        user_states[uid] = {"step": "reg_cat", "data": {}}
        send_message(chat_id, T["choose"], kb_cat()); return

    if text == T["simple"]:
        search_ctx[uid] = {"mode": "simple"}
        user_states[uid] = {"step": "req_cat", "data": {}}
        send_message(chat_id, T["choose"], kb_cat()); return

    if text == T["adv"]:
        search_ctx[uid] = {"mode": "adv"}
        user_states[uid] = {"step": "req_cat", "data": {}}
        send_message(chat_id, T["choose"], kb_cat()); return

    if text == T["list"]:
        db = load_db()
        if not db: send_message(chat_id, T["no_expert"], kb_main()); return
        r = T["list"] + ":\n\n"
        for e in db[:20]:
            r += "\U0001F464 " + e.get("name","?") + " | \u2B50 {:.1f}".format(overall_rating(e)) + "\n"
            r += "   " + T["role"] + " " + e.get("category","?") + "\n"
            r += "   " + T["area"] + " " + e.get("area","?") + "\n"
            r += "   " + T["phone"] + " " + e.get("phone","?") + "\n\n"
        send_message(chat_id, r, kb_main()); return

    if text == T["prof"]:
        e = find_expert(uid)
        if not e: send_message(chat_id, T["no_prof"], kb_main()); return
        r = T["my_prof"]
        r += T["name"] + " " + e.get("name","?") + "\n"
        r += T["role"] + " " + e.get("category","?") + "\n"
        r += T["subspec"] + " " + "\u060c ".join(e.get("sub_specialties",[])) + "\n"
        r += T["area"] + " " + e.get("area","?") + "\n"
        r += T["phone"] + " " + e.get("phone","?") + "\n"
        r += T["onsite"] + " " + (T["yes"] if e.get("works_on_site") else T["no"]) + "\n"
        r += T["response_speed"] + " " + RESPONSE_TIMES[int(e.get("response_speed",0))] + "\n"
        r += T["repair_time"] + " " + REPAIR_TIMES[int(e.get("repair_time",0))] + "\n\n"
        r += "\u2B50 {:.1f}/5".format(overall_rating(e))
        rv = total_reviews(e)
        if rv > 0: r += " (" + str(rv) + " \u0646\u0638\u0631)"
        r += "\n" + T["referral_count"] + str(e.get("referral_count",0)) + "\n\n"
        r += rating_breakdown(e) + T["rating_stages"]
        for st in [0,1,2]:
            a, c = stage_stats(e, st)
            nm = ["\u0627\u0648\u0644\u06cc\u0647","\u06cc\u06a9\u200c\u0645\u0627\u0647","\u0634\u0634\u200c\u0645\u0627\u0647"][st]
            r += "\n" + nm + ": " + ("\u0647\u0646\u0648\u0632 \u0646\u06cc\u0633\u062a" if a is None else "{:.1f} ({} \u0646\u0638\u0631)".format(a,c))
        send_message(chat_id, r, kb_main())
        show_my_link(chat_id, uid); return

    if uid in user_states:
        st = user_states[uid]; step = st["step"]; d = st["data"]

        if text == T["back"]:
            if step == "req_area":
                mode = search_ctx.get(uid, {}).get("mode", "simple")
                prev = "req_sub" if mode == "simple" else "req_return"
            else:
                prev = PREV_STEP.get(step)
            if prev is None:
                user_states.pop(uid, None); send_message(chat_id, T["use_menu"], kb_main())
            else:
                st["step"] = prev; ask_for_step(chat_id, prev, d)
            return

        if step == "reg_cat":
            if not valid_cat(text): send_message(chat_id, T["choose"], kb_cat()); return
            d["category"] = text; d["_subs"] = get_subs(text); st["step"] = "reg_subs"
            send_message(chat_id, T["choose_subs"] + fmt_list(d["_subs"]), kb_back()); return

        if step == "reg_subs":
            ns = parse_nums(text, len(d["_subs"]))
            if not ns: send_message(chat_id, T["invalid"], kb_back()); return
            d["sub_specialties"] = [d["_subs"][n-1] for n in ns]
            st["step"] = "reg_name"; send_message(chat_id, T["ask_name"], kb_back()); return

        if step == "reg_name":
            d["name"] = text; st["step"] = "reg_phone"
            send_message(chat_id, T["ask_phone"], kb_back()); return

        if step == "reg_phone":
            d["phone"] = text; st["step"] = "reg_area"
            send_message(chat_id, T["ask_area"], kb_area_text()); return

        if step == "reg_area":
            d["area"] = text; st["step"] = "reg_ask_location"
            send_message(chat_id, T["ask_location"], kb_yn()); return

        if step == "reg_ask_location":
            if text not in [T["yes"], T["no"]]: send_message(chat_id, T["choose"], kb_yn()); return
            if text == T["yes"]:
                st["step"] = "reg_location"
                send_message(chat_id, T["ask_send_location"], kb_area())
            else:
                st["step"] = "reg_onsite"
                send_message(chat_id, T["ask_onsite"], kb_yn())
            return

        if step == "reg_onsite":
            if text not in [T["yes"], T["no"]]: send_message(chat_id, T["choose"], kb_yn()); return
            d["works_on_site"] = (text == T["yes"]); st["step"] = "reg_response"
            send_message(chat_id, T["response_speed"] + "\n\n" + fmt_list(RESPONSE_TIMES), kb_back()); return

        if step == "reg_response":
            n = parse_single(text, len(RESPONSE_TIMES))
            if n is None: send_message(chat_id, T["invalid"], kb_back()); return
            d["response_speed"] = str(n); st["step"] = "reg_repair"
            send_message(chat_id, T["repair_time"] + "\n\n" + fmt_list(REPAIR_TIMES), kb_back()); return

        if step == "reg_repair":
            n = parse_single(text, len(REPAIR_TIMES))
            if n is None: send_message(chat_id, T["invalid"], kb_back()); return
            d["repair_time"] = str(n); d["user_id"] = uid; d["is_premium"] = False
            d["active"] = True; d.setdefault("ratings_by_stage", {}); d.setdefault("referral_count", 0)
            d["expert_code"] = gen_expert_code(d.get("name", "expert"))
            d.pop("_subs", None)
            db = [e for e in load_db() if e.get("user_id") != uid]; db.append(d); save_db(db)
            user_states.pop(uid, None)
            r = T["reg_ok"] + "\n\n"
            r += T["name"] + " " + d["name"] + "\n"
            r += T["role"] + " " + d["category"] + "\n"
            r += T["subspec"] + " " + "\u060c ".join(d["sub_specialties"]) + "\n"
            r += T["area"] + " " + d["area"] + "\n"
            r += T["phone"] + " " + d["phone"] + "\n"
            r += T["onsite"] + " " + (T["yes"] if d["works_on_site"] else T["no"]) + "\n"
            r += T["response_speed"] + " " + RESPONSE_TIMES[int(d["response_speed"])] + "\n"
            r += T["repair_time"] + " " + REPAIR_TIMES[int(d["repair_time"])] + "\n\n"
            r += T["my_code"] + d["expert_code"] + "\n"
            r += T["my_link"] + expert_link(d["expert_code"])
            send_message(chat_id, r, kb_share_link(expert_link(d["expert_code"]))); return

        if step == "req_cat":
            if not valid_cat(text): send_message(chat_id, T["choose"], kb_cat()); return
            d["category"] = text; d["_subs"] = get_subs(text); st["step"] = "req_sub"
            send_message(chat_id, T["choose_sub"] + fmt_list(d["_subs"]), kb_back()); return

        if step == "req_sub":
            ns = parse_nums(text, len(d["_subs"]))
            if len(ns) != 1: send_message(chat_id, T["invalid"], kb_back()); return
            d["sub"] = d["_subs"][ns[0]-1]
            mode = search_ctx.get(uid, {}).get("mode", "simple")
            if mode == "adv":
                st["step"] = "req_priority"
                send_message(chat_id, T["ask_priority"] + fmt_criteria(), kb_back())
            else:
                st["step"] = "req_area"
                send_message(chat_id, T["ask_cust_area"], kb_area())
            return

        if step == "req_priority":
            if text.strip() != "0" and text.strip() != "" and not parse_priority(text):
                send_message(chat_id, T["invalid"], kb_back()); return
            d["priorities"] = parse_priority(text); st["step"] = "req_handover"
            send_message(chat_id, T["ask_handover"] + fmt_list(HANDOVER_TIMES), kb_back()); return

        if step == "req_handover":
            n = parse_single(text, len(HANDOVER_TIMES))
            if n is None: send_message(chat_id, T["invalid"], kb_back()); return
            d["handover"] = n; st["step"] = "req_return"
            send_message(chat_id, T["ask_return"] + fmt_list(RETURN_TIMES), kb_back()); return

        if step == "req_return":
            n = parse_single(text, len(RETURN_TIMES))
            if n is None: send_message(chat_id, T["invalid"], kb_back()); return
            d["return_time"] = n; st["step"] = "req_area"
            send_message(chat_id, T["ask_cust_area"], kb_area()); return

        if step == "req_area":
            d["area"] = text; st["step"] = "req_desc"
            send_message(chat_id, T["ask_desc"], kb_back()); return

        if step == "req_desc":
            d["desc"] = text; st["step"] = "req_phone_share"
            send_message(chat_id, T["ask_phone_share"], kb_yn()); return

        if step == "req_phone_share":
            if text not in [T["yes"], T["no"]]: send_message(chat_id, T["choose"], kb_yn()); return
            if text == T["yes"]:
                st["step"] = "req_phone_input"
                send_message(chat_id, T["ask_phone_input"], kb_back())
            else:
                d["send_phone"] = False; d["customer_phone"] = None
                st["step"] = "req_who"; send_message(chat_id, T["ask_who_pick"], kb_who())
            return

        if step == "req_phone_input":
            d["send_phone"] = True; d["customer_phone"] = text
            st["step"] = "req_who"; send_message(chat_id, T["ask_who_pick"], kb_who()); return

        if step == "req_who":
            if text not in [T["who_me"], T["who_sys"]]: send_message(chat_id, T["choose"], kb_who()); return
            d["who"] = "me" if text == T["who_me"] else "sys"
            hv = d.get("handover"); clat = d.get("lat"); clng = d.get("lng")
            results = find_matching(d["category"], d["sub"], d.get("area",""), False, False, d.get("priorities",[]), hv, clat, clng)
            if not results and hv is not None:
                results = find_matching(d["category"], d["sub"], d.get("area",""), False, False, d.get("priorities",[]), None, clat, clng)
            if not results:
                send_message(chat_id, T["not_found"], kb_main())
                user_states.pop(uid,None); search_ctx.pop(uid,None); return
            info = {
                "category": d["category"], "sub": d["sub"],
                "area": d.get("area",""), "desc": d.get("desc",""),
                "phone": d.get("customer_phone") if d.get("send_phone") else None
            }
            search_ctx[uid] = {
                "mode": search_ctx.get(uid,{}).get("mode","simple"),
                "results": results, "info": info,
                "send_phone": d.get("send_phone", False),
                "who": d.get("who","me")
            }
            if d["who"] == "sys":
                deliver_expert(chat_id, uid, results[0], info, d.get("send_phone", False))
            else:
                txt = T["found"]
                for i, e in enumerate(results, 1):
                    txt += format_expert_line(e, i, d.get("priorities",[])) + "\n"
                txt += "\n\u06cc\u06a9\u06cc \u0631\u0627 \u0627\u0646\u062a\u062e\u0627\u0628 \u06a9\u0646\u06cc\u062f:"
                kb = {"inline_keyboard": []}
                for e in results:
                    kb["inline_keyboard"].append([{"text": "\u2705 " + e["name"], "callback_data": "pick:" + str(e["user_id"])}])
                send_message(chat_id, txt, kb)
            user_states.pop(uid, None); return

    send_message(chat_id, T["use_menu"], kb_main())


def handle_callback(cb):
    cb_id = cb["id"]; uid = cb["from"]["id"]; chat_id = cb["message"]["chat"]["id"]
    data = cb.get("data", "")

    if data.startswith("adm:"):
        if not is_admin(uid):
            answer_callback(cb_id, T["adm_not_auth"]); return
        parts = data.split(":")
        action = parts[1]
        answer_callback(cb_id)
        if action == "exp": admin_expert_detail(chat_id, int(parts[2]))
        elif action == "tog": admin_toggle_active(int(parts[2]), chat_id)
        elif action == "prem": admin_toggle_premium(int(parts[2]), chat_id)
        elif action == "del": admin_delete(int(parts[2]), chat_id)
        elif action == "back": admin_experts_list(chat_id)
        return

    if data.startswith("pick:"):
        expert_id = int(data.split(":")[1])
        e = find_expert(expert_id); ctx = search_ctx.get(uid)
        if not e or not ctx: answer_callback(cb_id, T["err"]); return
        answer_callback(cb_id)
        deliver_expert(chat_id, uid, e, ctx["info"], ctx.get("send_phone", False))
        search_ctx.pop(uid, None)

    elif data.startswith("rate:"):
        expert_id = int(data.split(":")[1]); e = find_expert(expert_id)
        if not e: answer_callback(cb_id, T["err"]); return
        rating_states[uid] = {"expert_id": expert_id, "ratings": {}, "stage": 0}
        answer_callback(cb_id); ask_next(chat_id, uid, e)

    elif data.startswith("frate:"):
        expert_id = int(data.split(":")[1]); e = find_expert(expert_id)
        if not e: answer_callback(cb_id, T["err"]); return
        j = get_pending_job(uid, expert_id)
        if not j: answer_callback(cb_id, "\u067e\u0631\u0648\u0698\u0647 \u067e\u06cc\u062f\u0627 \u0646\u0634\u062f."); return
        rating_states[uid] = {"expert_id": expert_id, "ratings": {}, "stage": j.get("stage",0)+1}
        answer_callback(cb_id); ask_next(chat_id, uid, e)

    elif data.startswith("crit:"):
        parts = data.split(":"); ck = parts[1]; stars = int(parts[2])
        st = rating_states.get(uid)
        if not st: answer_callback(cb_id, T["err"]); return
        st["ratings"][ck] = stars
        answer_callback(cb_id, T["rate_ok"])
        e = find_expert(st["expert_id"])
        if e: ask_next(chat_id, uid, e)


def main():
    print("Bot is running... (Ctrl+C to stop)")
    requests.packages.urllib3.disable_warnings()
    try:
        api_call("deleteWebhook"); print("Webhook deleted")
    except: pass
    get_me()
    try:
        session.get(API_URL + "/getUpdates", params={"offset": -1}, timeout=30)
        print("Old updates cleared")
    except Exception as ex: print("Clear:", str(ex)[:100])
    offset = None; last_fp = 0; fail_count = 0
    while True:
        try:
            now = time.time()
            if now - last_fp > 60:
                try: check_followups()
                except Exception as ex: print("FP:", str(ex)[:100])
                last_fp = now
            p = {"timeout": 25}
            if offset: p["offset"] = offset
            r = session.get(API_URL + "/getUpdates", params=p, timeout=45)
            data = r.json()
            fail_count = 0
            if data.get("ok") and data.get("result"):
                for u in data["result"]:
                    offset = u["update_id"] + 1
                    try:
                        if "message" in u: handle_message(u["message"])
                        elif "callback_query" in u: handle_callback(u["callback_query"])
                    except Exception as ex: print("H:", str(ex)[:100])
        except Exception as ex:
            fail_count += 1
            print("P (" + str(fail_count) + "):", str(ex)[:100])
            if fail_count > 5:
                time.sleep(30); fail_count = 0
            else:
                time.sleep(10)
            continue
        time.sleep(2)

if __name__ == "__main__":
    main()
