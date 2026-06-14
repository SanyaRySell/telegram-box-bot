import os
import time
import json
import random
import requests

TOKEN = os.getenv("BOT_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}"

offset = 0
games = {}

print("BOT STARTED")


# =====================
def send(chat_id, text, reply_to=None, markup=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    if reply_to:
        data["reply_to_message_id"] = reply_to

    if markup:
        data["reply_markup"] = json.dumps(markup)

    requests.post(URL + "/sendMessage", data=data)


# =====================
def keyboard():
    kb = []
    n = 1

    for _ in range(5):
        row = []
        for _ in range(5):
            row.append({
                "text": "🎁",
                "callback_data": str(n)
            })
            n += 1
        kb.append(row)

    return {"inline_keyboard": kb}


# =====================
def create_boxes():
    boxes = {}
    for i in range(1, 26):
        boxes[i] = random.choice([15, 25])  # NFT НЕТ ВООБЩЕ
    return boxes


# =====================
def open_box(cb):
    chat_id = cb["message"]["chat"]["id"]
    user_id = cb["from"]["id"]
    msg_id = cb["message"]["message_id"]

    requests.post(URL + "/answerCallbackQuery", data={
        "callback_query_id": cb["id"]
    })

    if chat_id not in games:
        return

    game = games[chat_id]

    if user_id != game["user_id"]:
        return

    if game["opened"]:
        return

    game["opened"] = True

    chosen = int(cb["data"])
    result = game["boxes"][chosen]

    text = (
        f"🎉 <b>Вы выиграли {result} ⭐</b>\n\n"
        "<b>Заберите награду в закрепе</b>"
    )

    requests.post(URL + "/editMessageText", data={
        "chat_id": chat_id,
        "message_id": msg_id,
        "text": text,
        "parse_mode": "HTML"
    })


# =====================
def handle_slot(chat_id, user_id, msg_id, value):

    # ❗ ВАЖНО: ТОЛЬКО 777 (64)
    if value != 64:
        return  # НИЧЕГО НЕ ДЕЛАЕМ

    # если игра уже идёт
    if chat_id in games and not games[chat_id]["opened"]:
        return

    games[chat_id] = {
        "user_id": user_id,
        "boxes": create_boxes(),
        "opened": False
    }

    send(
        chat_id,
        "🏆 <b>ДЖЕКПОТ 777!</b> 🏆\n\nВыберите коробку",
        msg_id,
        keyboard()
    )


# =====================
while True:
    try:
        r = requests.get(
            URL + "/getUpdates",
            params={"offset": offset, "timeout": 20},
            timeout=30
        ).json()

        for upd in r.get("result", []):
            offset = upd["update_id"] + 1

            if "message" not in upd:
                continue

            msg = upd["message"]
            chat_id = msg["chat"]["id"]
            user_id = msg["from"]["id"]
            msg_id = msg["message_id"]

            # 🎰 слот Telegram
            if "dice" in msg:
                if msg["dice"]["emoji"] == "🎰":
                    handle_slot(
                        chat_id,
                        user_id,
                        msg_id,
                        msg["dice"]["value"]
                    )

        time.sleep(0.5)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(3)
