# ==================== ارتباط با API بله ====================
import json
import time
import ssl
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from config import TOKEN, API_URL


# ==================== SSL Adapter (برای ویندوز ۷) ====================
class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        except:
            pass
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)


# ==================== Session ====================
session = requests.Session()
adapter = SSLAdapter(max_retries=Retry(total=5, backoff_factor=2))
session.mount('https://', adapter)
session.verify = False
requests.packages.urllib3.disable_warnings()


# ==================== توابع API ====================
def api_call(method, json_data=None):
    """ارسال درخواست به API بله"""
    url = API_URL + "/" + method
    for attempt in range(3):
        try:
            if json_data is not None:
                r = session.post(url, json=json_data, timeout=60)
            else:
                r = session.post(url, timeout=60)
            return r.json()
        except Exception as ex:
            print("[" + method + "] attempt " + str(attempt+1) + ": " + str(ex)[:100])
            time.sleep(5)
    return {"ok": False}


def send_message(chat_id, text, reply_markup=None):
    """ارسال پیام"""
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = reply_markup
    return api_call("sendMessage", data)


def answer_callback(callback_id, text=None):
    """پاسخ به کلیک دکمه inline"""
    data = {"callback_query_id": callback_id}
    if text:
        data["text"] = text
    return api_call("answerCallbackQuery", data)


def delete_message(chat_id, message_id):
    """حذف پیام"""
    data = {"chat_id": chat_id, "message_id": message_id}
    return api_call("deleteMessage", data)


def edit_message(chat_id, message_id, text, reply_markup=None):
    """ویرایش پیام"""
    data = {"chat_id": chat_id, "message_id": message_id, "text": text}
    if reply_markup:
        data["reply_markup"] = reply_markup
    return api_call("editMessageText", data)


# ==================== اطلاعات ربات ====================
def get_me():
    """گرفتن اطلاعات ربات"""
    try:
        r = api_call("getMe")
        if r.get("ok"):
            return r["result"]
    except:
        pass
    return None


def get_updates(offset=None, timeout=25):
    """گرفتن پیام‌های جدید"""
    params = {"timeout": timeout}
    if offset:
        params["offset"] = offset
    try:
        url = API_URL + "/getUpdates"
        r = session.get(url, params=params, timeout=45)
        return r.json()
    except Exception as ex:
        print("getUpdates error:", str(ex)[:100])
        return {"ok": False, "result": []}


def delete_webhook():
    """حذف Webhook (برای polling)"""
    return api_call("deleteWebhook")


def clear_old_updates():
    """پاک کردن پیام‌های قدیمی"""
    try:
        url = API_URL + "/getUpdates"
        session.get(url, params={"offset": -1}, timeout=30)
        return True
    except:
        return False


# ==================== ارسال لوکیشن ====================
def send_location(chat_id, latitude, longitude):
    """ارسال لوکیشن"""
    data = {"chat_id": chat_id, "latitude": latitude, "longitude": longitude}
    return api_call("sendLocation", data)


# ==================== استخراج اطلاعات از پیام ====================
def extract_message_info(message):
    """استخراج اطلاعات کلیدی از پیام"""
    result = {
        "chat_id": message.get("chat", {}).get("id"),
        "user_id": message.get("from", {}).get("id"),
        "text": message.get("text", ""),
        "location": message.get("location"),
        "contact": message.get("contact"),
        "message_id": message.get("message_id"),
    }
    return result
