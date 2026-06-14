import os
import requests
import time
import random
import json

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

    try:
        requests.post(URL + "/sendMessage", data=data, timeout=10)
    except:
        pass


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
    nft = random.randint(1, 25)

    for i in range(1, 26):
        boxes[i] = "NFT" if i == nft else random.choice([15, 25])

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

    if result == "NFT":
        result = 25

    text = (
        f"🎁 <b>Вы выиграли {result} ⭐</b>\n\n"
        "🎰 <b>Вы почти выиграли NFT</b>\n\n"
        "<b>Заберите награду</b>"
    )

    requests.post(URL + "/editMessageText", data={
        "chat_id": chat_id,
        "message_id": msg_id,
        "text": text,
        "parse_mode": "HTML"
    })


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

            # кнопки
            if "callback_query" in upd:
                open_box(upd["callback_query"])
                continue

            if "message" not in upd:
                continue

            msg = upd["message"]
            chat_id = msg["chat"]["id"]
            user_id = msg["from"]["id"]
            text = msg.get("text", "")

            print("MSG:", text)

            # =====================
            # 777 старт игры
            # =====================
            if text == "777":

                games[chat_id] = {
                    "user_id": user_id,
                    "opened": False,
                    "boxes": create_boxes()
                }

                send(
                    chat_id,
                    "🏆 <b>ДЖЕКПОТ 777!</b>\n\nВыберите коробку 👇",
                    msg["message_id"],
                    keyboard()
                )

            # =====================
            # ТЕСТ ОТВЕТА (важно для проверки reply)
            # =====================
            if text:
                send(chat_id, f"📩 Ты написал: {text}")

        time.sleep(0.5)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(3)
