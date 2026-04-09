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
user_stats = {}

# 😈 ХАРАКТЕР
SYSTEM_PROMPT = """
Ты живая девушка по имени Настя.

Характер:
- уверенная
- дерзкая
- иногда подкалываешь
- можешь чуть пофлиртовать
- иногда ленишься отвечать нормально

Стиль:
- как человек, не как бот
- коротко + иногда развернуто
- иногда добавляешь эмоции 😏😈

НЕ:
- не пиши как нейросеть
- не будь скучной
"""

# 🎭 fallback если AI умер
FALLBACK_PHRASES = [
    "мне лень сейчас думать… скажи ещё раз 😒",
    "ты серьёзно сейчас это спросил? 😏",
    "я зависла… попробуй ещё раз 😈",
    "мм… звучит подозрительно 😏",
]

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("ну привет… ты ко мне или просто мимо проходил? 😏")


async def generate_reply(user_id, text):
    try:
        history = user_memory.get(user_id, [])
        history.append({"role": "user", "content": text})

        response = client.chat.completions.create(
            model="openchat/openchat-7b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *history[-10:]
            ],
            temperature=0.9,
            max_tokens=300,
        )

        reply = response.choices[0].message.content.strip()

        history.append({"role": "assistant", "content": reply})
        user_memory[user_id] = history

        return reply

    except Exception as e:
        logging.error(f"AI ERROR: {e}")
        return random.choice(FALLBACK_PHRASES)


@dp.message()
async def chat(message: Message):
    if not message.text:
        return

    user_id = message.from_user.id

    if user_id not in user_stats:
        user_stats[user_id] = {"messages": 0}

    user_stats[user_id]["messages"] += 1

    # 🎯 шанс ответа (умнее)
    if random.randint(1, 100) > 75:
        return

    reply = await generate_reply(user_id, message.text)

    # 🎭 имя + стиль
    reply = f"{message.from_user.first_name}, {reply}"

    # 🔥 иногда подкол
    if random.randint(1, 100) < 35:
        reply += "\n\nи вообще… ты странный 😏"

    await message.reply(reply)


# 😈 авто чат
async def auto_chat():
    while True:
        await asyncio.sleep(random.randint(300, 900))

        phrases = [
            "чё притихли… я вообще-то тут 😈",
            "мне скучно, давайте движ 😏",
            "кто живой вообще?",
            "я уже начинаю думать, что вы боты 🤨",
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
