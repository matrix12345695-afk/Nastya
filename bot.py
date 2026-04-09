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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ TOKEN или OPENAI_API_KEY не найдены!")

CHAT_ID = -1002447821457

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

client = OpenAI(api_key=OPENAI_API_KEY)

user_memory = {}
user_stats = {}

SYSTEM_PROMPT = """
Ты Настя.

Характер:
- дерзкая
- уверенная
- иногда флиртуешь
- иногда игноришь
- можешь подколоть

Пиши как живой человек.
Не будь скучной.
"""

FALLBACK_PHRASES = [
    "я сейчас не в настроении отвечать 😏",
    "подожди… я думаю 😈",
    "ты меня немного грузишь сейчас 😒",
]


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("ну привет… неужели решил написать? 😏")


async def generate_reply(user_id, text):
    try:
        history = user_memory.get(user_id, [])
        history.append({"role": "user", "content": text})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
        logging.error(f"AI ERROR FULL: {repr(e)}")
        return random.choice(FALLBACK_PHRASES)


@dp.message()
async def chat(message: Message):
    if not message.text:
        return

    user_id = message.from_user.id

    if user_id not in user_stats:
        user_stats[user_id] = {"messages": 0}

    user_stats[user_id]["messages"] += 1

    # шанс ответа
    if random.randint(1, 100) > 80:
        return

    reply = await generate_reply(user_id, message.text)

    reply = f"{message.from_user.first_name}, {reply}"

    if random.randint(1, 100) < 30:
        reply += "\n\nты вообще всегда такой? 😏"

    await message.reply(reply)


async def auto_chat():
    while True:
        await asyncio.sleep(random.randint(300, 900))

        phrases = [
            "чё притихли… 😈",
            "мне скучно уже",
            "кто живой?",
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
