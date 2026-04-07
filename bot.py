import asyncio
import random
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from openai import OpenAI

TOKEN = "8471802623:AAFMtPerv2Vn7oehRv3wdhvX0Z81KrkAyGM"
OPENROUTER_KEY = "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"

# ⚠️ ВСТАВЬ СЮДА ID ГРУППЫ
CHAT_ID = -100XXXXXXXXXX

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

SYSTEM_PROMPT = """
Ты дерзкий, токсичный, матерящийся чат-бот.
Используешь черный юмор, сарказм и пошлые намёки (без откровенной жести).
Отвечаешь коротко, живо и агрессивно в шутку.
Иногда веди себя странно, иногда игнорируй, иногда провоцируй.
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

    # 🔥 80% отвечает
    if random.randint(1, 100) > 80:
        return

    username = message.from_user.first_name

    reply = await generate_reply(message.text)
    reply = f"{username}, {reply}"
    reply += "\n\n" + random.choice(EXTRA_PHRASES)

    await message.reply(reply)

# 😈 АВТО-СООБЩЕНИЯ
async def auto_chat():
    while True:
        await asyncio.sleep(random.randint(300, 900))  # 5–15 минут

        phrases = [
            "чё так тихо стало, вымерли все?",
            "или вы просто не знаете что написать?",
            "я один тут живой вообще?",
            "кто-нибудь скажет что-нибудь умное или как обычно?",
            "мне уже скучно с вами 🤡"
        ]

        try:
            await bot.send_message(CHAT_ID, random.choice(phrases))
        except Exception as e:
            logging.error(f"AUTO CHAT ERROR: {e}")

async def main():
    logging.info("🔥 BOT STARTING...")

    # запускаем авто-чат
    asyncio.create_task(auto_chat())

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
