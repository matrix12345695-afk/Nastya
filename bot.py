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

CHAT_ID = -1002447821457

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_KEY,
)

user_memory = {}
flirt_level = {}

# 🚫 СПИСОК ТЕХ КОГО ШЛЁМ
TARGET_USERS = [
    8276937335,  # сюда вставь user_id
    785245733,
]

SYSTEM_BASE = """
Ты Настя.

Характер:
- дерзкая
- уверенная
- флиртуешь
- иногда подкалываешь

Пиши как живая девушка.
"""

FALLBACK = [
    "ты меня немного загрузил… попробуй ещё раз 😏",
    "я думаю… не мешай 😈",
    "мм… интересно, продолжай 💋",
]


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("ну привет… посмотрим, чем ты меня удивишь 😏")


async def generate_reply(user_id, text, name):
    try:
        if user_id not in flirt_level:
            flirt_level[user_id] = 0

        flirt_level[user_id] += 1
        level = flirt_level[user_id]

        if level < 3:
            mood = "легкий флирт"
        elif level < 7:
            mood = "активный флирт"
        else:
            mood = "дерзкий флирт"

        prompt = f"""
{SYSTEM_BASE}

Режим: {mood}
Общайся с {name}

Сообщение:
{text}
"""

        response = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct:free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=200,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        logging.error(f"AI ERROR: {repr(e)}")
        return random.choice(FALLBACK)


@dp.message()
async def chat(message: Message):
    if not message.text:
        return

    user_id = message.from_user.id
    name = message.from_user.first_name

    # 💣 ЖЁСТКАЯ ЛОГИКА
    if user_id in TARGET_USERS:
        await message.reply("ПОШЁЛ НА ХУЙ")
        return

    # 🎭 обычное поведение
    if random.randint(1, 100) > 75:
        return

    reply = await generate_reply(user_id, message.text, name)

    await message.reply(f"{name}, {reply}")


async def auto_chat():
    while True:
        await asyncio.sleep(random.randint(300, 900))

        phrases = [
            "чё притихли… 😈",
            "мне скучно уже",
            "кто тут самый интересный?",
        ]

        try:
            await bot.send_message(CHAT_ID, random.choice(phrases))
        except Exception as e:
            logging.error(f"AUTO CHAT ERROR: {e}")


async def main():
    logging.info("🔥 BOT STARTING...")

    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(auto_chat())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
