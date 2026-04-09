import asyncio
import random
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from openai import OpenAI

# 🔐 ENV
TOKEN = os.getenv("TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

if not TOKEN or not OPENROUTER_KEY:
    raise ValueError("❌ TOKEN или OPENROUTER_KEY не найдены!")

# ✅ ВСТАВЬ СЮДА СВОЙ CHAT_ID (ты уже получил его)
CHAT_ID = -1002447821457

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_KEY,
    default_headers={
        "HTTP-Referer": "https://your-bot.onrender.com",
        "X-Title": "telegram-bot"
    }
)

user_memory = {}
user_stats = {}

SYSTEM_PROMPT = """
Ты живая, уверенная, немного дерзкая девушка.

Ты:
- говоришь как реальный человек
- понимаешь смысл
- иногда подкалываешь
- иногда задаёшь вопросы

НЕ:
- не пиши тупые короткие ответы
- не говори как бот

Будь естественной.
"""

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Ну привет... давай пообщаемся 😏")


# 🔥 ПРОВЕРКА AI (теперь бесплатная модель)
async def check_ai():
    try:
        client.chat.completions.create(
            model="google/gemma-7b-it:free",
            messages=[{"role": "user", "content": "ок"}],
            max_tokens=5,
        )
        return True
    except Exception as e:
        logging.error(f"AI ERROR: {e}")
        return False


# 🔥 ОСНОВНОЙ AI (БЕСПЛАТНЫЙ)
async def generate_reply(user_id, text):
    try:
        history = user_memory.get(user_id, [])
        history.append({"role": "user", "content": text})

        response = client.chat.completions.create(
            model="google/gemma-7b-it:free",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *history[-10:]
            ],
            temperature=0.9,
            max_tokens=250,
        )

        reply = response.choices[0].message.content.strip()

        history.append({"role": "assistant", "content": reply})
        user_memory[user_id] = history

        return reply

    except Exception as e:
        logging.error(f"GPT ERROR: {e}")
        return "мне лень думать… скажи ещё раз 😒"


@dp.message()
async def chat(message: Message):
    if not message.text:
        return

    logging.info(f"CHAT ID: {message.chat.id}")

    user_id = message.from_user.id

    if user_id not in user_stats:
        user_stats[user_id] = {"messages": 0}

    user_stats[user_id]["messages"] += 1

    # 🔥 80% отвечает
    if random.randint(1, 100) > 80:
        return

    reply = await generate_reply(user_id, message.text)

    reply = f"{message.from_user.first_name}, {reply}"

    # 🔥 иногда добавляем живость
    if "?" not in reply and random.randint(1, 100) < 40:
        reply += "\n\nи вообще… ты это серьёзно сейчас?"

    await message.reply(reply)


# 😈 авто-чат
async def auto_chat():
    while True:
        await asyncio.sleep(random.randint(300, 900))

        try:
            await bot.send_message(CHAT_ID, "чё притихли… мне уже скучно 😏")
        except Exception as e:
            logging.error(f"AUTO CHAT ERROR: {e}")


async def main():
    logging.info("🔥 BOT STARTING...")

    await bot.delete_webhook(drop_pending_updates=True)

    status = await check_ai()

    if status:
        logging.info("🟢 AI OK")
    else:
        logging.error("🔴 AI ERROR")

    asyncio.create_task(auto_chat())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
