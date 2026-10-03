import json, time, requests, random, string, ssl, os, threading
from math import radians, sin, cos, sqrt, atan2
from http.server import HTTPServer, BaseHTTPRequestHandler
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# ==================== Health Server برای Runflare ====================
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

# ==================== SSL Adapter برای ویندوز ۷ ====================
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

# ==================== تنظیمات ====================
TOKEN = "2007928769:p_l7euP0ifN0Vh7OWyFqRaJiN9KNRpgsAWY"
SUPER_ADMIN = 1808576881
ADMIN_PASSWORD = "63618"
API_URL = "https://tapi.bale.ai/bot" + TOKEN
DB_FILE = "experts.json"
JOBS_FILE = "jobs.json"
CONFIG_FILE = "config.json"
BOT_USERNAME = ""

user_states = {}
rating_states = {}
search_ctx = {}
admin_sessions = set()

# ==================== زمان‌ها ====================
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
CLOSE_DURATIONS = [
    ("\u06f1 \u0631\u0648\u0632", 1),
    ("\u06f3 \u0631\u0648\u0632", 3),
    ("\u06f1 \u0647\u0641\u062a\u0647", 7),
    ("\u06f1\u06f0 \u0631\u0648\u0632", 10),
    ("\u06f1 \u0645\u0627\u0647", 30),
]
CRITERIA = [
    {"key": "price",          "label": "\U0001F4B0 \u062f\u0633\u062a\u0645\u0632\u062f \u0645\u0646\u0627\u0633\u0628"},
    {"key": "behavior",       "label": "\U0001F60A \u0627\u062e\u0644\u0627\u0642 \u062e\u0648\u0628"},
    {"key": "speed",          "label": "\u26A1 \u0633\u0631\u0639\u062a \u0639\u0645\u0644"},
    {"key": "quality",        "label": "\u2728 \u06a9\u06cc\u0641\u06cc\u062a \u06a9\u0627\u0631"},
    {"key": "punctuality",    "label": "\U0001F550 \u0648\u0642\u062a\u200C\u0634\u0646\u0627\u0633\u06cc"},
    {"key": "cleanliness",    "label": "\U0001F9F9 \u0646\u0638\u0627\u0641\u062a"},
    {"key": "warranty",       "label": "\U0001F6E1 \u0636\u0645\u0627\u0646\u062a \u06a9\u0627\u0631"},
    {"key": "responsiveness", "label": "\U0001F4DE \u067E\u0627\u0633\u062e\u06af\u0648\u06cc\u06cc"},
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
    "reg_ok": "\u2705 \u062b\u0628\u062a\u200c\u0646\u0627\u0645 \u0627\u0646\u062c\u0627\u0645 \u0634\u062f!",
    "reg_pending": "\u2705 \u062b\u0628\u062a\u200c\u0646\u0627\u0645 \u0634\u0645\u0627 \u062b\u0628\u062a \u0634\u062f \u0648 \u062f\u0631 \u0627\u0646\u062a\u0638\u0627\u0631 \u062a\u0623\u06cc\u06cc\u062f \u0645\u062f\u06cc\u0631 \u0627\u0633\u062a.\n\u067e\u0633 \u0627\u0632 \u062a\u0623\u06cc\u06cc\u062f\u060c \u0628\u0647 \u0634\u0645\u0627 \u0627\u0637\u0644\u0627\u0639 \u062f\u0627\u062f\u0647 \u0645\u06cc\u200c\u0634\u0648\u062f.",
    "found": "\U0001F50D \u0645\u062a\u062e\u0635\u0635\u06cc\u0646 \u0628\u0631\u062a\u0631:\n\n",
    "not_found": "\u274C \u0645\u062a\u062e\u0635\u0635\u06cc \u067e\u06cc\u062f\u0627 \u0646\u0634\u062f.",
    "direct": "\n\u26A0\uFE0F \u0644\u0637\u0641\u0627\u064b \u0645\u0633\u062a\u0642\u06cc\u0645\u0627\u064b \u062a\u0645\u0627\u0633 \u0628\u06af\u06cc\u0631\u06cc\u062f.",
    "new_cust": "\U0001F514 \u0645\u0634\u062a\u0631\u06cc \u062c\u062f\u06cc\u062f!",
    "use_menu": "\u0627\u0632 \u0645\u0646\u0648 \u0627\u0633\u062a\u0641\u0627\u062f\u0647 \u06a9\u0646\u06cc\u062f.",
    "invalid": "\u0645\u0642\u062f\u0627\u0631 \u0645\u0639\u062a\u0628\u0631 \u0646\u06cc\u0633\u062a. \u062f\u0648\u0628\u0627\u0631\u0647 \u062a\u0644\u0627\u0634 \u06a9\u0646\u06cc\u062f.",
    "no_expert": "\u0647\u0646\u0648\u0632 \u0645\u062a\u062e\u0635\u0635\u06cc \u0646\u06cc\u0633\u062a.",
    "my_prof": "\U0001F464 \u067e\u0631\u0648\u0641\u0627\u06cc\u0644 \u0634\u0645\u0627:\n\n",
    "no_prof": "\u062b\u0628\u062a\u200c\u0646\u0627\u0645 \u0646\u06a9\u0631\u062f\u06cc\u062f.",
    "tracking": "\U0001F3AB \u06a9\u062f \u067e\u06cc\u06af\u06cc\u0631\u06cc: ",
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
    "response_speed": "\u23F1 \u0633\u0631\u0639\u062a \u067E\u0627\u0633\u062E\u06af\u0648\u06cc\u06cc:",
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
    "share_hint": "\n\n\u0644\u06cc\u0646\u06a9 \u062e\u0648\u062f\u062a\u0627\u0646 \u0631\u0627 \u0628\u0631\u0627\u06cc \u0645\u0634\u062a\u0631\u06cc\u0627\u0646 \u0627\u0631\u0633\u0627\u0644 \u06a9\u0646\u06cc\u062f.",
    "share_btn": "\U0001F517 \u0646\u0645\u0627\u06cc\u0634 \u0644\u06cc\u0646\u06a9 \u0627\u0634\u062a\u0631\u0627\u06a9",
    "copy_link_btn": "\U0001F4CB \u06a9\u067E\u06cc \u0644\u06cc\u0646\u06a9",
    "public_prof": "\U0001F464 \u067E\u0631\u0648\u0641\u0627\u06cc\u0644 \u0645\u062a\u062e\u0635\u0635:\n\n",
    "expert_not_found": "\u274C \u0645\u062a\u062e\u0635\u0635\u06cc \u0628\u0627 \u0627\u06cc\u0646 \u06a9\u062f \u067e\u06cc\u062f\u0627 \u0646\u0634\u062f.",
    "welcome_via_link": "\u0634\u0645\u0627 \u0627\u0632 \u0637\u0631\u06cc\u0642 \u0644\u06cc\u0646\u06a9 \u0648\u0627\u0631\u062f \u0634\u062f\u06cc\u062f:",
    # Admin
    "adm_title": "\U0001F510 \u067E\u0646\u0644 \u0645\u062f\u06cc\u0631\u06cc\u062a",
    "adm_ask_pass": "\U0001F510 \u0644\u0637\u0641\u0627\u064b \u0631\u0645\u0632 \u0639\u0628\u0648\u0631 \u0631\u0627 \u0648\u0627\u0631\u062f \u06a9\u0646\u06cc\u062f:",
    "adm_wrong_pass": "\u274C \u0631\u0645\u0632 \u0639\u0628\u0648\u0631 \u0627\u0634\u062a\u0628\u0627\u0647 \u0627\u0633\u062a.",
    "adm_stats": "\U0001F4CA \u0622\u0645\u0627\u0631 \u06a9\u0644\u06cc",
    "adm_experts": "\U0001F465 \u0645\u062a\u062e\u0635\u0635\u06cc\u0646",
    "adm_pending": "\u23F3 \u062f\u0631 \u0627\u0646\u062a\u0638\u0627\u0631 \u062a\u0623\u06cc\u06cc\u062f",
    "adm_jobs": "\U0001F4CB \u0622\u062e\u0631\u06cc\u0646 \u0645\u0639\u0631\u0641\u06cc\u200c\u0647\u0627",
    "adm_revenue": "\U0001F4B0 \u062f\u0631\u0622\u0645\u062f",
    "adm_operators": "\U0001F465 \u0645\u062f\u06cc\u0631\u0627\u0646",
    "adm_exit": "\U0001F519 \u062e\u0631\u0648\u062c",
    "adm_back": "\U0001F519 \u0628\u0627\u0632\u06af\u0634\u062a",
    "adm_not_auth": "\u0634\u0645\u0627 \u062f\u0633\u062a\u0631\u0633\u06cc \u0646\u062f\u0627\u0631\u06cc\u062f.",
    "adm_tog_on": "\u2705 \u0641\u0639\u0627\u0644",
    "adm_tog_off": "\u274C \u063a\u06cc\u0631\u0641\u0639\u0627\u0644",
    "adm_prem_on": "\u2B50 \u0627\u0634\u062a\u0631\u0627\u06a9 \u0648\u06cc\u0698\u0647",
    "adm_prem_off": "\u2B50 \u062d\u0630\u0641 \u0627\u0634\u062a\u0631\u0627\u06a9",
    "adm_delete": "\U0001F5D1 \u062d\u0630\u0641",
    "adm_deleted": "\u0645\u062a\u062e\u0635\u0635 \u062d\u0630\u0641 \u0634\u062f.",
    "adm_approve": "\u2705 \u062a\u0623\u06cc\u06cc\u062f",
    "adm_reject": "\u274C \u0631\u062f",
    "adm_approved_ok": "\u062a\u0623\u06cc\u06cc\u062f \u0634\u062f.",
    "adm_rejected_ok": "\u0631\u062f \u0634\u062f.",
    "adm_new_expert": "\U0001F514 \u0645\u062a\u062e\u0635\u0635 \u062c\u062f\u06cc\u062f \u062f\u0631 \u0627\u0646\u062a\u0638\u0627\u0631 \u062a\u0623\u06cc\u06cc\u062f:",
    "adm_no_pending": "\u0647\u06cc\u0686 \u0645\u062a\u062e\u0635\u0635\u06cc \u062f\u0631 \u0627\u0646\u062a\u0638\u0627\u0631 \u062a\u0623\u06cc\u06cc\u062f \u0646\u06cc\u0633\u062a.",
    "adm_no_exp": "\u0647\u06cc\u0686 \u0645\u062a\u062e\u0635\u0635\u06cc \u0646\u06cc\u0633\u062a.",
    "adm_no_op": "\u0647\u06cc\u0686 \u0645\u062f\u06cc\u0631\u06cc \u062a\u0639\u06cc\u06cc\u0646 \u0646\u0634\u062f\u0647.",
    "adm_ask_op_id": "\u0622\u06cc\u062f\u06cc \u0639\u062f\u062f\u06cc \u0645\u062f\u06cc\u0631 \u062c\u062f\u06cc\u062f \u0631\u0627 \u0648\u0627\u0631\u062f \u06a9\u0646\u06cc\u062f:",
    "adm_op_added": "\u0645\u062f\u06cc\u0631 \u0627\u0636\u0627\u0641\u0647 \u0634\u062f.",
    "adm_add_op": "\u2795 \u0627\u0641\u0632\u0648\u062f\u0646 \u0645\u062f\u06cc\u0631",
    "adm_rm_op": "\u2796 \u062d\u0630\u0641 \u0645\u062f\u06cc\u0631",
    "exp_approved_notify": "\U0001F389 \u062a\u0628\u0631\u06cc\u06a9! \u062b\u0628\u062a\u200C\u0646\u0627\u0645 \u0634\u0645\u0627 \u062a\u0623\u06cc\u06cc\u062f \u0634\u062f.",
    "exp_rejected_notify": "\u0645\u062a\u0623\u0633\u0641\u0627\u0646\u0647 \u062b\u0628\u062a\u200C\u0646\u0627\u0645 \u0634\u0645\u0627 \u062a\u0623\u06cc\u06cc\u062f \u0646\u0634\u062f.",
    # Shop status
    "shop_btn": "\U0001F3EA \u0648\u0636\u0639\u06cc\u062a \u0645\u063a\u0627\u0632\u0647",
    "shop_status": "\U0001F3EA \u0648\u0636\u0639\u06cc\u062a \u0645\u063a\u0627\u0632\u0647:\n",
    "shop_active": "\U0001F7E2 \u0641\u0639\u0627\u0644 (\u062f\u0631\u06cc\u0627\u0641\u062a \u0645\u0634\u062a\u0631\u06cc)",
    "shop_closed_temp": "\U0001F7E1 \u062a\u0639\u0637\u06cc\u0644 \u0645\u0648\u0642\u062a",
    "shop_closed_perm": "\U0001F534 \u062a\u0639\u0637\u06cc\u0644 \u062f\u0627\u0626\u0645",
    "shop_ask": "\u0648\u0636\u0639\u06cc\u062a \u0645\u063a\u0627\u0632\u0647 \u0631\u0627 \u0627\u0646\u062a\u062e\u0627\u0628 \u06a9\u0646\u06cc\u062f:",
    "shop_ask_duration": "\u062a\u0627 \u0686\u0646\u062f \u0631\u0648\u0632 \u062a\u0639\u0637\u06cc\u0644 \u0647\u0633\u062a\u06cc\u062f\u061f",
    "shop_close_ok": "\u2705 \u0645\u063a\u0627\u0632\u0647 \u062a\u0639\u0637\u06cc\u0644 \u0634\u062f \u062a\u0627: ",
    "shop_open_ok": "\u2705 \u0645\u063a\u0627\u0632\u0647 \u0641\u0639\u0627\u0644 \u0634\u062f.",
    "shop_reason_ask": "\u062f\u0644\u06cc\u0644 \u062a\u0639\u0637\u06cc\u0644\u06cc \u0631\u0627 \u0628\u0646\u0648\u06cc\u0633\u06cc\u062f (\u06cc\u0627 \u0628\u0646\u0648\u06cc\u0633\u06cc\u062f \u0645\u0647\u0645 \u0646\u06cc\u0633\u062a):",
    "shop_skip_reason": "\u0645\u0647\u0645 \u0646\u06cc\u0633\u062a",
    "shop_countdown": "\u23F3 \u062a\u0627 \u0641\u0639\u0627\u0644 \u0634\u062f\u0646: ",
    "shop_days": " \u0631\u0648\u0632",
    "shop_reopen": "\U0001F513 \u0641\u0639\u0627\u0644 \u0633\u0627\u0632\u06cc \u0645\u062c\u062f\u062f",
    "shop_reopened": "\u0645\u063a\u0627\u0632\u0647 \u0641\u0639\u0627\u0644 \u0634\u062f.",
    "shop_reopened_notify": "\U0001F514 \u0645\u063a\u0627\u0632\u0647 \u0634\u0645\u0627 \u0645\u062c\u062f\u062f\u0627\u064b \u0641\u0639\u0627\u0644 \u0634\u062f.",
    # Feedback
    "feedback": "\n\n\U0001F4AC \u0646\u0638\u0631\u0627\u062a \u0648 \u067E\u06cc\u0634\u0646\u0647\u0627\u062f\u0627\u062a: ",
    # Location to customer
    "navigate_btn": "\U0001F4CD \u0645\u0633\u06cc\u0631\u06cc\u0627\u0628\u06cc \u0628\u0647 \u062a\u0639\u0645\u06cc\u0631\u06a9\u0627\u0631",
    "no_location": "\u062a\u0639\u0645\u06cc\u0631\u06a9\u0627\u0631 \u0645\u0648\u0642\u0639\u06cc\u062a \u062b\u0628\u062a \u0646\u06a9\u0631\u062f\u0647.",
}

# ==================== زیرتخصص‌ها ====================
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


# ==================== Config ====================
def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"password": ADMIN_PASSWORD, "operators": [], "feedback_id": ""}

def save_config(d):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def get_feedback_id():
    return load_config().get("feedback_id", "")

def is_super_admin(uid):
    return uid == SUPER_ADMIN

def is_admin(uid):
    if uid == SUPER_ADMIN:
        return True
    return uid in load_config().get("operators", [])

def is_authed_admin(uid):
    return uid in admin_sessions and is_admin(uid)

def get_operators():
    return load_config().get("operators", [])

def add_operator(uid):
    c = load_config()
    ops = c.get("operators", [])
    if uid not in ops and uid != SUPER_ADMIN:
        ops.append(uid)
        c["operators"] = ops
        save_config(c)

def remove_operator(uid):
    c = load_config()
    ops = [o for o in c.get("operators", []) if o != uid]
    c["operators"] = ops
    save_config(c)


# ==================== DB ====================
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
    dlat = radians(lat2 - lat1); dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


# ==================== Shop Status ====================
def is_shop_open(e):
    if not e.get("active", True): return False
    st = e.get("shop_status", "active")
    if st == "active": return True
    if st == "closed_perm": return False
    if st == "closed_temp":
        if e.get("closed_until", 0) > time.time(): return False
    return True

def get_shop_label(e):
    if not e.get("active", True):
        return T["adm_st_inactive"]
    st = e.get("shop_status", "active")
    if st == "active": return T["shop_active"]
    if st == "closed_perm": return T["shop_closed_perm"]
    if st == "closed_temp":
        if e.get("closed_until", 0) > time.time():
            days = max(1, int((e["closed_until"] - time.time()) / 86400) + 1)
            return T["shop_closed_temp"] + " (" + T["shop_countdown"] + str(days) + T["shop_days"] + ")"
        return T["shop_active"]
    return T["shop_active"]


# ==================== Rating ====================
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


# ==================== Match ====================
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
        if not is_shop_open(e): continue
        if e.get("status", "approved") != "approved": continue
        if e.get("category") != category: continue
        if sub not in e.get("sub_specialties", []): continue
        if needs_onsite and not e.get("works_on_site", False): continue
        if not matches_times(e, handover, None): continue
        all_match.append(e)
        if cust_lat and cust_lng and e.get("lat") and e.get("lng"):
            if haversine(cust_lat, cust_lng, e["lat"], e["lng"]) <= 20: loc_match.append(e)
        elif area:
            e_area = e.get("area", "")
            if area in e_area or e_area in area: text_match.append(e)
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


# ==================== API ====================
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
            print("[" + m + "] " + str(attempt+1) + ": " + str(ex)[:100])
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


# ==================== Keyboards ====================
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
        [{"text": T["adm_pending"]}],
        [{"text": T["adm_jobs"]}],
        [{"text": T["adm_revenue"]}],
        [{"text": T["adm_operators"]}],
        [{"text": T["adm_exit"]}]
    ], "resize_keyboard": True}

def kb_shop():
    return {"keyboard": [
        [{"text": T["shop_active"]}],
        [{"text": T["shop_closed_temp"]}],
        [{"text": T["shop_closed_perm"]}],
        [{"text": T["back"]}]
    ], "resize_keyboard": True, "one_time_keyboard": True}

def kb_share_link(url):
    return {"inline_keyboard": [
        [{"text": T["share_btn"], "url": url}],
        [{"text": T["copy_link_btn"], "copy_text": {"text": url}}]
    ]}


# ==================== Helpers ====================
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


# ==================== Back Map ====================
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


# ==================== Jobs ====================
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


# ==================== Rating flow ====================
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

def check_shop_reactivations():
    db = load_db(); now = time.time(); changed = False
    for e in db:
        if e.get("shop_status") == "closed_temp" and e.get("closed_until", 0) <= now:
            e["shop_status"] = "active"
            e["closed_until"] = 0
            send_message(e["user_id"], T["shop_reopened_notify"])
            changed = True
    if changed: save_db(db)

def check_followups():
    check_shop_reactivations()
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


# ==================== Deliver ====================
def deliver_expert(chat_id, uid, expert, info, send_phone):
    code = create_job(uid, chat_id, expert, info)
    msg = T["chosen_expert"]
    msg += "\U0001F464 " + expert["name"] + "\n"
    msg += T["phone"] + " " + expert["phone"] + "\n"
    msg += T["area"] + " " + expert.get("area", "?") + "\n"
    msg += T["tracking"] + code
    msg += T["tracking_note"]
    msg += T["feedback"] + (get_feedback_id() or "\u062f\u0631 \u062f\u0633\u062a\u0631\u0633 \u0646\u06cc\u0633\u062a")
    send_message(chat_id, msg, kb_main())
    notify_expert(expert, info, code, send_phone)
    if expert.get("lat") and expert.get("lng"):
        nav_kb = {"inline_keyboard": [[
            {"text": T["navigate_btn"], "url": "https://www.google.com/maps?q={},{}".format(expert["lat"], expert["lng"])}
        ]]}
        send_message(chat_id, T["navigate_btn"], nav_kb)
    rate_kb = {"inline_keyboard": [[
        {"text": T["rate_start"] + expert["name"], "callback_data": "rate:" + str(expert["user_id"])}
    ]]}
    send_message(chat_id, T["rate_ask"], rate_kb)


# ==================== Admin ====================
def notify_admins_new_expert(expert):
    msg = T["adm_new_expert"] + "\n\n"
    msg += T["name"] + " " + expert.get("name", "?") + "\n"
    msg += T["phone"] + " " + expert.get("phone", "?") + "\n"
    msg += T["role"] + " " + expert.get("category", "?") + "\n"
    msg += T["subspec"] + " " + "\u060c ".join(expert.get("sub_specialties", [])) + "\n"
    msg += T["area"] + " " + expert.get("area", "?") + "\n"
    kb = {"inline_keyboard": [[
        {"text": T["adm_approve"], "callback_data": "adm:appr:" + str(expert["user_id"])},
        {"text": T["adm_reject"], "callback_data": "adm:rej:" + str(expert["user_id"])}
    ]]}
    send_message(SUPER_ADMIN, msg, kb)
    for op in get_operators():
        send_message(op, msg, kb)

def admin_stats(chat_id):
    db = load_db(); jobs = load_jobs()
    total = len(db); active = sum(1 for e in db if e.get("active", True))
    approved = sum(1 for e in db if e.get("status", "approved") == "approved")
    pending = sum(1 for e in db if e.get("status") == "pending")
    premium = sum(1 for e in db if e.get("is_premium"))
    refs = sum(e.get("referral_count", 0) for e in db)
    customers = len(set(j.get("customer_id") for j in jobs))
    txt = T["adm_stats"] + ":\n\n"
    txt += "\U0001F465 \u06a9\u0644: " + str(total) + "\n"
    txt += "\u2705 \u062a\u0623\u06cc\u06cc\u062f \u0634\u062f\u0647: " + str(approved) + "\n"
    txt += "\u23F3 \u062f\u0631 \u0627\u0646\u062a\u0638\u0627\u0631: " + str(pending) + "\n"
    txt += "\U0001F7E2 \u0641\u0639\u0627\u0644: " + str(active) + "\n"
    txt += "\u2B50 \u0648\u06cc\u0698\u0647: " + str(premium) + "\n"
    txt += "\U0001F4C8 \u0645\u0639\u0631\u0641\u06cc\u200c\u0647\u0627: " + str(refs) + "\n"
    txt += "\U0001F4CB \u067e\u0631\u0648\u0698\u0647\u200c\u0647\u0627: " + str(len(jobs)) + "\n"
    txt += "\U0001F464 \u0645\u0634\u062a\u0631\u06cc\u0627\u0646: " + str(customers)
    send_message(chat_id, txt, kb_admin())

def admin_pending_list(chat_id):
    pending = [e for e in load_db() if e.get("status") == "pending"]
    if not pending:
        send_message(chat_id, T["adm_no_pending"], kb_admin()); return
    kb = {"inline_keyboard": []}
    for e in pending:
        label = e.get("name", "?") + " | " + e.get("category", "?")
        kb["inline_keyboard"].append([{"text": label, "callback_data": "adm:viewp:" + str(e["user_id"])}])
    send_message(chat_id, T["adm_pending"] + ":", kb)

def admin_view_pending(chat_id, uid):
    e = find_expert(uid)
    if not e:
        send_message(chat_id, "\u067e\u06cc\u062f\u0627 \u0646\u0634\u062f.", kb_admin()); return
    txt = T["adm_new_expert"] + "\n\n"
    txt += T["name"] + " " + e.get("name","?") + "\n"
    txt += T["phone"] + " " + e.get("phone","?") + "\n"
    txt += T["role"] + " " + e.get("category","?") + "\n"
    txt += T["subspec"] + " " + "\u060c ".join(e.get("sub_specialties", [])) + "\n"
    txt += T["area"] + " " + e.get("area","?") + "\n"
    kb = {"inline_keyboard": [
        [{"text": T["adm_approve"], "callback_data": "adm:appr:" + str(uid)},
         {"text": T["adm_reject"], "callback_data": "adm:rej:" + str(uid)}],
        [{"text": T["adm_back"], "callback_data": "adm:pendinglist"}]
    ]}
    send_message(chat_id, txt, kb)

def admin_experts_list(chat_id):
    db = [e for e in load_db() if e.get("status", "approved") == "approved"]
    if not db:
        send_message(chat_id, T["adm_no_exp"], kb_admin()); return
    kb = {"inline_keyboard": []}
    for i, e in enumerate(db[:15], 1):
        star = "\u2B50" if e.get("is_premium") else ""
        stat = "\u2705" if e.get("active", True) else "\u274C"
        label = "{}. {} {} {} | {:.1f}".format(i, stat, star, e.get("name", "?"), overall_rating(e))
        kb["inline_keyboard"].append([{"text": label, "callback_data": "adm:exp:" + str(e["user_id"])}])
    send_message(chat_id, T["adm_experts"] + ":", kb)

def admin_expert_detail(chat_id, expert_id):
    e = find_expert(expert_id)
    if not e:
        send_message(chat_id, "\u067e\u06cc\u062f\u0627 \u0646\u0634\u062f.", kb_admin()); return
    txt = "\U0001F464 " + T["name"] + " " + e.get("name","?") + "\n"
    txt += T["phone"] + " " + e.get("phone","?") + "\n"
    txt += T["role"] + " " + e.get("category","?") + "\n"
    txt += T["subspec"] + " " + "\u060c ".join(e.get("sub_specialties", [])) + "\n"
    txt += T["area"] + " " + e.get("area","?") + "\n"
    txt += T["rating_avg"] + "{:.1f}/5".format(overall_rating(e)) + "\n"
    txt += T["referral_count"] + str(e.get("referral_count", 0)) + "\n"
    txt += T["shop_status"] + get_shop_label(e) + "\n"
    txt += "\U0001F194 " + e.get("expert_code", "?") + "\n"
    status = T["adm_st_active"] if e.get("active", True) else T["adm_st_inactive"]
    txt += "\u2699 " + status + "\n"
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
        send_message(chat_id, "\u0647\u0646\u0648\u0632 \u0645\u0639\u0631\u0641\u06cc\u200c\u0627\u06cc \u0646\u06cc\u0633\u062a.", kb_admin()); return
    txt = T["adm_jobs"] + ":\n\n"
    for j in jobs[-10:][::-1]:
        txt += "\U0001F3AB " + j.get("tracking_code", "?") + " | " + j.get("expert_name", "?") + "\n"
    send_message(chat_id, txt, kb_admin())

def admin_revenue(chat_id):
    db = load_db()
    refs = sum(e.get("referral_count", 0) for e in db)
    total = refs * COMMISSION
    txt = T["adm_revenue"] + ":\n\n"
    txt += "\U0001F4C8 " + T["referral_count"] + str(refs) + "\n"
    txt += "\U0001F4B0 " + "{:,}".format(total) + " \u062a\u0648\u0645\u0627\u0646"
    send_message(chat_id, txt, kb_admin())

def admin_operators(chat_id):
    ops = get_operators()
    txt = T["adm_operators"] + ":\n\n"
    txt += "\U0001F451 \u0645\u062f\u06cc\u0631 \u0627\u0635\u0644\u06cc: " + str(SUPER_ADMIN) + "\n\n"
    if not ops:
        txt += T["adm_no_op"]
    else:
        for op in ops:
            txt += "\U0001F464 " + str(op) + "\n"
    kb = {"inline_keyboard": [
        [{"text": T["adm_add_op"], "callback_data": "adm:addop"}],
        [{"text": T["adm_rm_op"], "callback_data": "adm:rmop"}],
        [{"text": T["adm_back"], "callback_data": "adm:backmain"}]
    ]}
    send_message(chat_id, txt, kb)

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

def admin_approve(expert_id, chat_id):
    db = load_db()
    for e in db:
        if e.get("user_id") == expert_id:
            e["status"] = "approved"; break
    save_db(db)
    send_message(chat_id, T["adm_approved_ok"], kb_admin())
    send_message(expert_id, T["exp_approved_notify"])

def admin_reject(expert_id, chat_id):
    db = load_db()
    for e in db:
        if e.get("user_id") == expert_id:
            e["status"] = "rejected"; break
    save_db(db)
    send_message(chat_id, T["adm_rejected_ok"], kb_admin())
    send_message(expert_id, T["exp_rejected_notify"])


# ==================== Share ====================
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


# ==================== Shop Status Handler ====================
def show_shop_status(chat_id, uid):
    e = find_expert(uid)
    if not e:
        send_message(chat_id, T["no_prof"], kb_main()); return
    txt = T["shop_status"] + get_shop_label(e)
    if e.get("shop_status") == "closed_temp" and e.get("closed_until", 0) > time.time():
        days = max(1, int((e["closed_until"] - time.time()) / 86400) + 1)
        txt += "\n\u23F3 " + str(days) + T["shop_days"] + " \u0628\u0627\u0642\u06cc \u0645\u0627\u0646\u062f\u0647"
        if e.get("close_reason"):
            txt += "\n\U0001F4DD \u062f\u0644\u06cc\u0644: " + e["close_reason"]
        kb = {"inline_keyboard": [[{"text": T["shop_reopen"], "callback_data": "shop:open"}]]}
        send_message(chat_id, txt, kb)
    else:
        send_message(chat_id, txt + "\n\n" + T["shop_ask"], kb_shop())

def set_shop_closed_temp(chat_id, uid):
    st = user_states.get(uid) or {"step": "shop_close_dur", "data": {}}
    st["step"] = "shop_close_dur"
    user_states[uid] = st
    send_message(chat_id, T["shop_ask_duration"] + "\n\n" + fmt_list([c[0] for c in CLOSE_DURATIONS]), kb_back())

def set_shop_closed_perm(chat_id, uid):
    db = load_db()
    for e in db:
        if e.get("user_id") == uid:
            e["shop_status"] = "closed_perm"; e["closed_until"] = 0; break
    save_db(db)
    send_message(chat_id, T["shop_close_ok"] + T["shop_closed_perm"], kb_main())

def set_shop_active(chat_id, uid):
    db = load_db()
    for e in db:
        if e.get("user_id") == uid:
            e["shop_status"] = "active"; e["closed_until"] = 0; e["close_reason"] = ""; break
    save_db(db)
    send_message(chat_id, T["shop_open_ok"], kb_main())


# ==================== Handle message ====================
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
            if e and e.get("status", "approved") == "approved":
                send_message(chat_id, T["welcome_via_link"])
                send_message(chat_id, format_public_profile(e), kb_main()); return
            else:
                send_message(chat_id, T["expert_not_found"])
        send_message(chat_id, T["start"] + T["feedback"] + (get_feedback_id() or ""), kb_main()); return

    if text == "/start":
        user_states.pop(uid, None)
        send_message(chat_id, T["start"] + T["feedback"] + (get_feedback_id() or ""), kb_main()); return

    if text == "/admin":
        if not is_admin(uid):
            send_message(chat_id, T["adm_not_auth"]); return
        if is_authed_admin(uid):
            send_message(chat_id, T["adm_title"], kb_admin()); return
        user_states[uid] = {"step": "adm_password", "data": {}}
        send_message(chat_id, T["adm_ask_pass"], kb_back()); return

    if is_authed_admin(uid):
        if text == T["adm_exit"]:
            admin_sessions.discard(uid)
            user_states.pop(uid, None)
            send_message(chat_id, T["use_menu"], kb_main()); return
        if text == T["adm_stats"]: admin_stats(chat_id); return
        if text == T["adm_experts"]: admin_experts_list(chat_id); return
        if text == T["adm_pending"]: admin_pending_list(chat_id); return
        if text == T["adm_jobs"]: admin_jobs(chat_id); return
        if text == T["adm_revenue"]: admin_revenue(chat_id); return
        if text == T["adm_operators"]: admin_operators(chat_id); return

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
        db = [e for e in load_db() if e.get("status", "approved") == "approved" and is_shop_open(e)]
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
        r += T["repair_time"] + " " + REPAIR_TIMES[int(e.get("repair_time",0))] + "\n"
        r += T["shop_status"] + get_shop_label(e) + "\n\n"
        if e.get("status", "approved") == "pending":
            r += "\u23F3 \u062f\u0631 \u0627\u0646\u062a\u0638\u0627\u0631 \u062a\u0623\u06cc\u06cc\u062f \u0645\u062f\u06cc\u0631\n\n"
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
        show_my_link(chat_id, uid)
        send_message(chat_id, T["shop_btn"] + ":", {"keyboard": [[{"text": T["shop_btn"]}]], "resize_keyboard": True})
        return

    if text == T["shop_btn"]:
        show_shop_status(chat_id, uid); return

    if uid in user_states:
        st = user_states[uid]; step = st["step"]; d = st["data"]

        # Admin password
        if step == "adm_password":
            if text == T["back"]:
                user_states.pop(uid, None); send_message(chat_id, T["use_menu"], kb_main()); return
            cfg = load_config()
            if text == cfg.get("password", ADMIN_PASSWORD):
                admin_sessions.add(uid)
                user_states.pop(uid, None)
                send_message(chat_id, T["adm_title"], kb_admin())
            else:
                send_message(chat_id, T["adm_wrong_pass"], kb_back())
            return

        # Shop status flow
        if step == "shop_close_dur":
            n = parse_single(text, len(CLOSE_DURATIONS))
            if n is None:
                send_message(chat_id, T["invalid"], kb_back()); return
            days = CLOSE_DURATIONS[n][1]
            d["close_days"] = days
            st["step"] = "shop_close_reason"
            send_message(chat_id, T["shop_reason_ask"], kb_back()); return

        if step == "shop_close_reason":
            reason = "" if text == T["shop_skip_reason"] else text
            days = d.get("close_days", 1)
            db = load_db()
            for e in db:
                if e.get("user_id") == uid:
                    e["shop_status"] = "closed_temp"
                    e["closed_until"] = int(time.time()) + days * 86400
                    e["close_reason"] = reason
                    break
            save_db(db)
            user_states.pop(uid, None)
            send_message(chat_id, T["shop_close_ok"] + str(days) + T["shop_days"], kb_main()); return

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

        # Registration
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
            d["active"] = True; d["status"] = "pending"; d["shop_status"] = "active"; d["closed_until"] = 0
            d.setdefault("ratings_by_stage", {}); d.setdefault("referral_count", 0)
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
            r += "\n\n" + T["reg_pending"]
            send_message(chat_id, r, kb_share_link(expert_link(d["expert_code"])))
            notify_admins_new_expert(d)
            return

        # Request flow
        if step == "req_cat":
            if not valid_cat(text): send_message(chat_id, T["choose"], kb_cat()); return
            d["category"] = text; d["_subs"] = get_subs(text); st["step"] = "req_sub"
            send_message(chat_id, T["choose_sub"] + fmt_list(d["_subs"]), kb_back()); return

        if step == "req_sub":
            ns
