import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from openai import OpenAI

TOKEN = "YOUR_TELEGRAM_TOKEN"
OPENROUTER_KEY = "YOUR_OPENROUTER_API_KEY"

bot = Bot(token=TOKEN)
dp = Dispatcher()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_KEY,
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

async def generate_reply(text):
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

@dp.message()
async def chat(message: Message):
    if random.randint(1, 100) > 40:
        return

    reply = await generate_reply(message.text)
    reply += "\n\n" + random.choice(EXTRA_PHRASES)

    await message.reply(reply)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
