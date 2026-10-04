# ==================== نظرات و پیشنهادات ====================
from texts import FEEDBACK_MSG, FEEDBACK_EMPTY
from keyboards import kb_main
from api import send_message
from db import get_feedback_id


# ==================== نمایش آیدی نظرات ====================
def handle_feedback(chat_id):
    """نمایش آیدی نظرات و پیشنهادات"""
    feedback_id = get_feedback_id()
    if feedback_id:
        send_message(chat_id, FEEDBACK_MSG + feedback_id, kb_main())
    else:
        send_message(chat_id, FEEDBACK_EMPTY, kb_main())


# ==================== آیدی کوتاه برای پیام‌ها ====================
def get_short_feedback():
    """گرفتن آیدی برای اضافه کردن به پیام‌ها"""
    fid = get_feedback_id()
    if fid:
        return "\n\n💬 نظرات: " + fid
    return ""
