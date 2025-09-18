from flask import Flask, request, jsonify
import os
import requests
import random
import json
import sys
from io import BytesIO
sys.path.append("api/")

import db as database
from PIL import Image

db = []
last_random = 0

app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN", "")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"


def send_reply(chat_id, message_id, text):
    if not TOKEN:
        return
    try:
        requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text, "reply_to_message_id": message_id}, timeout=10)
    except Exception as e:
        print("Error sending message:", e)

def send_message(chat_id, text):
    try:
        requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        print("Error sending message:", e)

def send_forward(data):
    try:
        return requests.post(f"{TELEGRAM_API}/forwardMessage", json=data, timeout=10).json()
    except Exception as e:
        print("Error sending message:", e)

def send_message_advanced(data):
    try:
        return requests.post(f"{TELEGRAM_API}/sendMessage", json=data, timeout=10).json()
    except Exception as e:
        print("Error sending message:", e)

@app.get("/")
def index():
    # Simple health check
    return "ok good"

@app.post("/")
def webhook():
    update = request.get_json(silent=True) or {}
    message = update.get("message") or update.get("edited_message")
    # if not message:
    #     return jsonify(ok=True)

    if message["from"]["is_bot"] == True:
        return

    class msg: 
        chat_id = message["chat"]["id"]
        id = message.get("message_id","")
        username = message["from"].get("username","")
        first_name = message["from"].get("first_name","")
        last_name = message["from"].get("last_name","")
        mfrom = message["from"]
        reply = message.get("reply_to_message","")
        
        type = str(message["chat"]["type"])
        text = str(message.get("text", ""))
        date = message["date"]
        caption = message.get("caption","")
        is_admin = True if message["from"]["id"] == 5859474607 or message["from"]["id"] == 7839178126 else False

    if msg.type == "private":
        try:
            if msg.text == "/start":
                text = """
- 💡 ربات در حال توسعه میباشد بنابرین امکانات ربات محدود است. به زودی آپشن های بیشتر به ربات اضافه میشود.

سلام. به ربات تفکیک نقشه های هواشناسی خوش اومدی.

لطفا سایت مورد نظر را جهت انجام تفکیک انتخاب کنید.
"""

                keyboard = {
                    "inline_keyboard": [
                        [{"text": "Meteologix / Weather.us / Kachelmanweather", "callback_data": "meteologix"}],
                    ]
                }   

                data = {
                    "chat_id": msg.chat_id,
                    "text": text,
                    "reply_markup": keyboard
                }

                database.Upsert("users", {"id": msg.mfrom["id"], "first_name": msg.first_name, "last_name": msg.last_name, "username": msg.username ,"user_state": "none"})
                send_message_advanced(data)
            
            elif "callback_query" in update:
                cq = update["callback_query"]
                cq_id = cq["id"]
                data = cq["data"]
                chat_id = cq["message"]["chat"]["id"]
                msg_id = cq["message"]["message_id"]

                if data == "metelogix":
                    database.Upsert("users", {"id": msg.mfrom["id"], "first_name": msg.first_name, "last_name": msg.last_name, "username": msg.username ,"user_state": "meteologix"})
                    send_reply(msg.chat_id, msg.id, "عکس مدل مورد نظر را ارسال کنید. (توجه کنید عکس را از طریق سایت دانلود کنید و زوم استان مازندران باشد.)")
                    

            if "photo" in update:
                if database.Select(eq="id", eq_value=msg.mfrom["id"]).data["user_state"] == "meteologix":

                    res = requests.get(f"{TELEGRAM_API}/getFile", params={"file_id": update["message"]["photo"][-1]["file_id"]}).json()
                    file_path = res["result"]["file_path"]

                    # 2️⃣ دانلود فایل به حافظه
                    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
                    file_bytes = BytesIO(requests.get(file_url).content)

                    # 3️⃣ باز کردن با PIL
                    base = Image.open(file_bytes)  # تصویر کاربر
                    overlay = Image.open("layer_prec.png")  # تصویر خودت

                    # 4️⃣ اعمال overlay
                    base.paste(overlay, (0, 0), overlay)

                    # 5️⃣ آماده سازی خروجی در حافظه
                    output_bytes = BytesIO()
                    base.save(output_bytes, format="PNG")
                    output_bytes.seek(0)

                    # 6️⃣ ارسال دوباره به تلگرام
                    files = {"photo": ("output.png", output_bytes)}
                    requests.post(f"{TELEGRAM_API}/sendPhoto", data={"chat_id": msg.chat_id}, files=files)

                    database.Upsert("users", {"id": msg.mfrom["id"], "first_name": msg.first_name, "last_name": msg.last_name, "username": msg.username ,"user_state": "none"})



        except Exception as e: 
            send_message(msg.chat_id, e)
    return jsonify(ok=True)
