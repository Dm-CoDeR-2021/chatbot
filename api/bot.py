from flask import Flask, request, jsonify
import os
import requests
import random
import json
import sys
sys.path.append("api/")
import db as database

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

    if msg.reply:
        send_message(msg.chat_id, str(update))

    if msg.type == "private":
        try:
            if msg.text == "/start" and msg.is_admin:
                keyboard1 = {
                    "keyboard": [
                        [{"text": "Show unread messages 💌"}, {"text": "Show all messages 📮"}],
                    ],
                    "resize_keyboard": True
                }

                data = {
                    "chat_id": msg.chat_id,
                    "text": "Select an option:",
                    "reply_markup": json.dumps(keyboard1)
                }

                send_message_advanced(data)
            elif msg.text == "Show unread messages 💌" and msg.is_admin:
                res = database.Select("messages", eq="read", eq_value=False).data
                data = [{"id": "NULL", "name": "NULL", "username": "NULL"}]
                ids = []
                _data = "💌 Unread messages:\n\n"
            
                for i in res:
                    data.append({"id": i["id"], "name": i["name"], "username": f"@{i["username"]}"})
                    ids.append(i["id"])

                for i in data:
                    for _i in ids:
                        if i["id"] == _i:
                            _data += f'({ids.count(_i)}) [ {i["name"]} ] {i["username"]} :\n<a href="https://t.me/chat_samibot?start=get_{i["id"]}">Show all </a>\n\n'

                            while _i in ids:
                                ids.remove(_i)

                send_message_advanced({"chat_id": msg.chat_id, "text": _data, "parse_mode": "HTML"})
                    
                
            if len(database.Exist(eq_value=msg.mfrom["id"])) == 0:
                        
                res = database.Upsert(data={
                    "id": msg.mfrom["id"],
                    "first_name": str(msg.mfrom["first_name"]),
                    "last_name": str(msg.mfrom.get("last_name", "NULL")),
                    "username": str(msg.mfrom["username"])
                })

            data = {
                "chat_id": 7839178126,
                "from_chat_id": msg.chat_id,
                "message_id": msg.id
            }

            res = send_forward(data) 
            send_reply(msg.chat_id, msg.id, "Your message sent to @samijunior.")

            if len(update["message"].get("photo", [])) != 0:
                database.Insert("messages", data=
                {
                    "id": msg.mfrom["id"],
                    "username": msg.username,
                    "name": msg.first_name,
                    "text": update["message"].get("caption", msg.text),
                    "message_id": res["result"]["message_id"],
                    "file": str(update["message"]["photo"][len(update["message"]["photo"])-1]["file_id"]),
                    "read": False
                })
            else:
                database.Insert("messages", data=
                {
                    "id": msg.mfrom["id"],
                    "username": msg.username,
                    "name": msg.first_name,
                    "text": msg.text,
                    "message_id": res["result"]["message_id"],
                    "read": False
                })
                
        except Exception as e: 
            send_message(msg.chat_id, e)
    return jsonify(ok=True)
