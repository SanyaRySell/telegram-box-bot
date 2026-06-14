import requests
import time
import random
import json
import os

TOKEN = os.getenv("BOT_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}"

offset = 0
games = {}

# ======================
# 💬 слот-сообщения
msg_counter = 0
target = random.randint(5, 15)

messages = [
    "🏆 Три семерки уже совсем рядом!",
    "🎉 Ты уже слишком близко к джекпоту",
    "🎁 Слишком близко, чтобы сдаваться",
    "🎰 Почти 777"
]


# ======================
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


# ======================
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


# ======================
def create_boxes():
    boxes = {}

    nft_pos = random.randint(1, 25)

    for i in range(1, 26):
        if i == nft_pos:
            boxes[i] = "NFT"
        else:
            boxes[i] = random.choice([15, 15, 15, 25, 25, 25, 25, 25, 25, 25])

    return boxes


# ======================
def show_result(game, chosen):
    kb = []
    n = 1

    for _ in range(5):
        row = []
        for _ in range(5):

            val = game["boxes"][n]

            if val == "NFT":
                txt = "💎 NFT"
            else:
                txt = f"{val}⭐"

            if n == chosen:
                txt = "✅ " + txt

            row.append({
                "text": txt,
                "callback_data": "done"
            })

            n += 1

        kb.append(row)

    return {"inline_keyboard": kb}


# ======================
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

    # 💥 NFT НИКОГДА не выигрывается
    if result == "NFT":
        result = 25

    text = (
        "🏆 <b>ДЖЕКПОТ</b> 🏆\n\n"
        "<b>Выберите одну из ячеек ниже.</b>\n"
        "<b>В одной из них находится ГЛАВНЫЙ ПРИЗ - NFT.</b>\n"
        "<b>В остальных спрятаны 15 и 25 звёзды.</b>\n\n"
        "🎉 <b>Поздравляю!</b>\n\n"
        f"🎁 <b>Вы выиграли {result} ⭐</b>\n\n"
        "<b>Заберите награду в закрепе</b>"
    )

    requests.post(URL + "/editMessageText", data={
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": json.dumps(show_result(game, chosen))
    })


# ======================
print("BOT STARTED")

while True:
    try:
        r = requests.get(
            URL + f"/getUpdates?offset={offset}&timeout=20"
        ).json()

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

            # 🎰 ТОЛЬКО СЛОТ
            if msg.get("dice") and msg["dice"]["emoji"] == "🎰":

                # 💬 сообщения раз в 5–15 слотов
                msg_counter += 1

                if msg_counter >= target:
                    msg_counter = 0
                    target = random.randint(5, 15)

                    send(
                        chat_id,
                        random.choice(messages),
                        msg["message_id"]
                    )

                # ❗ ТОЛЬКО 777 (value 64)
                if msg["dice"]["value"] != 64:
                    continue

                # ❗ блокировка повторной игры
                if chat_id in games and not games[chat_id]["opened"]:
                    continue

                games[chat_id] = {
                    "user_id": user_id,
                    "opened": False,
                    "boxes": create_boxes()
                }

                send(
                    chat_id,
                    "🏆 <b>ДЖЕКПОТ</b> 🏆\n\n"
                    "<b>Выберите одну из ячеек ниже.</b>\n"
                    "<b>В одной из них находится ГЛАВНЫЙ ПРИЗ - NFT.</b>\n"
                    "<b>В остальных спрятаны 15 и 25 звёзды.</b>",
                    msg["message_id"],
                    make_keyboard()
                )

        time.sleep(1)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(3)
