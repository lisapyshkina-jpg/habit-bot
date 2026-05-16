import asyncio
import json
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# --------------------
# 🔑 ТОКЕН ВСТАВЛЯЕШЬ СЮДА
# --------------------

TOKEN = "8980941844:AAHAN54PXJMgFPrlwOpZEzLGiGeDHJ-iNu8"

DATA_FILE = "data.json"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --------------------
# DATA
# --------------------

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

user_data = load_data()

# --------------------
# ФРАЗЫ
# --------------------

PHRASE_MAP = {
    "1": "Отлично! Маленький шаг запускает движение.",
    "4": "Не останавливайся. Успех — это производная системности.",
    "9": "Спорим, ты себе спасибо за это скажешь?",
    "15": "Дисциплина, контроль и регулярные вложения. Что сегодня и куда ты вкладываешь?",
    "25": "Напоминание. Ты строишь систему.",
    "29": "Финал почти собран. Не сдавай темп."
}

# --------------------
# START
# --------------------

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Напиши привычку и месяц.\n\nПример:\nспорт январь"
    )

# --------------------
# КНОПКИ
# --------------------

def create_keyboard(days):
    kb = InlineKeyboardBuilder()

    for i in range(1, 32):
        day = str(i)
        text = "✔️" if day in days else day

        kb.button(text=text, callback_data=day)

    kb.adjust(7)
    return kb.as_markup()

# --------------------
# СОЗДАНИЕ ТРЕКЕРА
# --------------------

@dp.message()
async def create_tracker(message: types.Message):

    if not message.text or " " not in message.text:
        return

    habit, month = message.text.split(" ", 1)
    user_id = str(message.from_user.id)

    user_data[user_id] = {
        "habit": habit,
        "month": month,
        "days": [],
        "sent_days": []
    }

    save_data(user_data)

    await message.answer(
        f"🔥 {habit.upper()} — {month}",
        reply_markup=create_keyboard([])
    )

# --------------------
# НАЖАТИЯ КНОПОК
# --------------------

@dp.callback_query()
async def click(callback: types.CallbackQuery):

    user_id = str(callback.from_user.id)
    data = user_data.get(user_id)

    if not data:
        return

    day = callback.data

    if day in data["days"]:
        data["days"].remove(day)
    else:
        data["days"].append(day)

        if day in PHRASE_MAP and day not in data["sent_days"]:
            await bot.send_message(
                callback.message.chat.id,
                PHRASE_MAP[day]
            )
            data["sent_days"].append(day)

    save_data(user_data)

    await callback.message.edit_reply_markup(
        reply_markup=create_keyboard(data["days"])
    )

    await callback.answer()

# --------------------
# WEB (нужен для Render)
# --------------------

async def handle(request):
    return web.Response(text="Bot is running")

async def start_web():
    app = web.Application()
    app.add_routes([web.get("/", handle)])

    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# --------------------
# MAIN
# --------------------

async def main():
    await bot.delete_webhook(drop_pending_updates=True)

    await asyncio.gather(
        dp.start_polling(bot),
        start_web()
    )

if __name__ == "__main__":
    asyncio.run(main())