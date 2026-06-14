import os
import requests
import time
import random
import json

TOKEN = os.getenv("8807117107:AAFmuQU7pxZ6R8FdWF5QsevJePpe6MqGl8E")
URL = f"https://api.telegram.org/bot{TOKEN}"

offset = 0
games = {}

msg_counter = 0
target = random.randint(5, 15)

messages = [
    "🎰 ПОЧТИ JACKPOT 777! 🎰",
    "🎁 Слишком близко чтобы сдаваться",
    "🔥 Удача уже рядом",
    "💎 Ты почти поймал NFT"
]


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


def make_keyboard():
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


def create_boxes():
    boxes = {}
    nft_pos = random.randint(1, 25)

    for i in range(1, 26):
        boxes[i] = "NFT" if i == nft_pos else random.choice([15, 25])

    return boxes


def handle_gift(cb):
    chat_id = cb["message"]["chat"]["id"]
    user_id = cb["from"]["id"]
    message_id = cb["message"]["message_id"]

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
        f"🎁 <b>Вы выиграли {result} звёзд</b>\n\n"
        "🎰 <b>Вы почти выиграли NFT</b>\n\n"
        "<b>Заберите выигрыш в закрепе</b>"
    )

    requests.post(URL + "/editMessageText", data={
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": json.dumps(make_keyboard())
    })


print("BOT STARTED")

while True:
    try:
        r = requests.get(URL + f"/getUpdates?offset={offset}&timeout=20").json()

        for upd in r.get("result", []):

            offset = upd["update_id"] + 1

            if "callback_query" in upd:
                handle_gift(upd["callback_query"])
                continue

            if "message" not in upd:
                continue

            msg = upd["message"]
            chat_id = msg["chat"]["id"]
            user_id = msg["from"]["id"]

            is_777 = False

            if msg.get("text") == "777":
                is_777 = True

            if msg.get("dice") and msg["dice"]["value"] == 64:
                is_777 = True

            if is_777:
                games[chat_id] = {
                    "user_id": user_id,
                    "opened": False,
                    "boxes": create_boxes()
                }

                send(
                    chat_id,
                    "🏆 <b>ДЖЕКПОТ 777!</b>\n\n🎁 Выберите коробку",
                    msg["message_id"],
                    make_keyboard()
                )

            msg_counter += 1

            if msg_counter >= target:
                msg_counter = 0
                target = random.randint(5, 15)

                send(
                    chat_id,
                    random.choice(messages),
                    msg["message_id"]
                )

        time.sleep(1)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(3)
