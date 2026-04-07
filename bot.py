import asyncio
import random
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from openai import OpenAI

TOKEN = "8471802623:AAFMtPerv2Vn7oehRv3wdhvX0Z81KrkAyGM"
OPENROUTER_KEY = "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"

# ЛОГИ
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ✅ ВАЖНО — добавили headers
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_KEY,
    default_headers={
        "HTTP-Referer": "https://your-bot.onrender.com",
        "X-Title": "telegram-bot"
    }
)

SYSTEM_PROMPT = """
Ты дерзкий, токсичный, матерящийся чат-бот.
Используешь черный юмор, сарказм и пошлые намёки (без откровенной жести).
Отвечаешь коротко, живо и агрессивно в шутку.
"""

EXTRA_PHRASES = [
    "ты это серьёзно сейчас?",
    "я в шоке с тебя",
    "ну ты и персонаж конечно",
    "гений... наоборот"
]

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Ну привет... давай, удиви меня 🤡")

# ✅ Добавили try/except чтобы видеть ошибки
async def generate_reply(text):
    try:
        response = client.chat.completions.create(
            model="mistralai/mixtral-8x7b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=1.2,
            max_tokens=200,
        )
        return response.choices[0].message.content

    except Exception as e:
        logging.error(f"GPT ERROR: {e}")
        return "я щас задумался… и сломался 🤡"

@dp.message()
async def chat(message: Message):
    if not message.text:
        return

    # шанс ответа
    if random.randint(1, 100) > 40:
        return

    reply = await generate_reply(message.text)
    reply += "\n\n" + random.choice(EXTRA_PHRASES)

    await message.reply(reply)

async def main():
    logging.info("🔥 BOT STARTING...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
