# ==================== ارتباط با API بله (ربات ادمین) ====================
import time
import ssl
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from config import ADMIN_TOKEN

ADMIN_API_URL = "https://tapi.bale.ai/bot" + ADMIN_TOKEN


# ==================== SSL Adapter ====================
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
admin_session = requests.Session()
_admin_adapter = SSLAdapter(max_retries=Retry(total=5, backoff_factor=2))
admin_session.mount('https://', _admin_adapter)
admin_session.verify = False


# ==================== توابع API ====================
def admin_api_call(method, json_data=None):
    """ارسال درخواست به API ربات ادمین"""
    url = ADMIN_API_URL + "/" + method
    for attempt in range(3):
        try:
            if json_data is not None:
                r = admin_session.post(url, json=json_data, timeout=60)
            else:
                r = admin_session.post(url, timeout=60)
            return r.json()
        except Exception as ex:
            print("[admin:" + method + "] " + str(attempt+1) + ": " + str(ex)[:100])
            time.sleep(5)
    return {"ok": False}


def admin_send_message(chat_id, text, reply_markup=None):
    """ارسال پیام از ربات ادمین"""
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = reply_markup
    return admin_api_call("sendMessage", data)


def admin_answer_callback(callback_id, text=None):
    """پاسخ به کلیک دکمه inline"""
    data = {"callback_query_id": callback_id}
    if text:
        data["text"] = text
    return admin_api_call("answerCallbackQuery", data)


def admin_get_me():
    """گرفتن اطلاعات ربات ادمین"""
    try:
        r = admin_api_call("getMe")
        if r.get("ok"):
            return r["result"]
    except:
        pass
    return None


def admin_get_updates(offset=None, timeout=25):
    """گرفتن پیام‌های جدید ربات ادمین"""
    params = {"timeout": timeout}
    if offset:
        params["offset"] = offset
    try:
        url = ADMIN_API_URL + "/getUpdates"
        r = admin_session.get(url, params=params, timeout=45)
        return r.json()
    except Exception as ex:
        print("admin getUpdates error:", str(ex)[:100])
        return {"ok": False, "result": []}


def admin_delete_webhook():
    return admin_api_call("deleteWebhook")


def admin_clear_old_updates():
    try:
        url = ADMIN_API_URL + "/getUpdates"
        admin_session.get(url, params={"offset": -1}, timeout=30)
        return True
    except:
        return False


def admin_forward_message(chat_id, from_chat_id, message_id):
    """Forward پیام"""
    data = {
        "chat_id": chat_id,
        "from_chat_id": from_chat_id,
        "message_id": message_id
    }
    return admin_api_call("forwardMessage", data)


def admin_send_photo(chat_id, photo_bytes, caption=""):
    """ارسال عکس با ربات ادمین"""
    url = ADMIN_API_URL + "/sendPhoto"
    files = {"photo": ("receipt.jpg", photo_bytes, "image/jpeg")}
    data = {"chat_id": chat_id}
    if caption:
        data["caption"] = caption
    try:
        r = admin_session.post(url, files=files, data=data, timeout=60)
        return r.json()
    except Exception as ex:
        print("[admin sendPhoto]", str(ex)[:100])
        return {"ok": False}
