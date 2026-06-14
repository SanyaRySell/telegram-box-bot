import os
import requests
import time
import random
import json

TOKEN = os.getenv("BOT_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}"

offset = 0

games = {}

# ===============================
# СЧЁТЧИК СООБЩЕНИЙ ДЛЯ АНИМАЦИИ
# ===============================
message_counter = 0
next_trigger = random.randint(5, 15)

print("BOT STARTED")


# ===============================
# ОТПРАВКА СООБЩЕНИЙ
# ===============================
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


# ===============================
# КЛАВИАТУРА 5x5
# ===============================
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


# ===============================
# СОЗДАНИЕ КОРОБОК
# ===============================
def create_boxes():
    boxes = {}

    nft_position = random.randint(1, 25)

    for i in range(1, 26):
        if i == nft_position:
            boxes[i] = "NFT"
        else:
            boxes[i] = random.choice([15, 25])

    return boxes


# ===============================
# ОТКРЫТИЕ КОРОБКИ
# ===============================
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

    # NFT = редкий выигрыш
    if result == "NFT":
        stars = 25
        title = "💎 NFT ДЖЕКПОТ!"
    else:
        stars = result
        title = "🎁 ВЫИГРЫШ"

    text = (
        f"{title}\n\n"
        f"🎉 <b>Вы выиграли {stars} ⭐</b>\n\n"
        "🎰 <b>Вы почти выиграли NFT</b>\n\n"
        "<b>Заберите награду в закрепе</b>"
    )

    requests.post(URL + "/editMessageText", data={
        "chat_id": chat_id,
        "message_id": msg_id,
        "text": text,
        "parse_mode": "HTML"
    })


# ===============================
# АНИМАЦИИ / СЛУЧАЙНЫЕ СООБЩЕНИЯ
# ===============================
def random_animation(chat_id):
    texts = [
        "🎰 777 крутится...",
        "💎 NFT почти выпал...",
        "🎁 удача на подходе...",
        "🔥 система анализирует шанс...",
        "🎉 бонус энергия активирована..."
    ]

    send(chat_id, random.choice(texts))


# ===============================
# ГЛАВНЫЙ ЦИКЛ
# ===============================
while True:
    try:
        r = requests.get(
            URL + "/getUpdates",
            params={"offset": offset, "timeout": 20},
            timeout=30
        ).json()

        if not r.get("ok"):
            continue

        for upd in r.get("result", []):
            offset = upd["update_id"] + 1

            # =======================
            # КНОПКИ
            # =======================
            if "callback_query" in upd:
                open_box(upd["callback_query"])
                continue

            if "message" not in upd:
                continue

            msg = upd["message"]
            chat_id = msg["chat"]["id"]
            user_id = msg["from"]["id"]

            text = msg.get("text", "").strip()

            print("MSG:", text)

            # =======================
            # 777 СТАРТ ИГРЫ
            # =======================
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

            # =======================
            # СЧЁТЧИК СООБЩЕНИЙ
            # =======================
            message_counter += 1

            if message_counter >= next_trigger:
                random_animation(chat_id)
                message_counter = 0
                next_trigger = random.randint(5, 15)

        time.sleep(0.5)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(3)
