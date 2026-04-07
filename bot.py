import asyncio
import random
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from openai import OpenAI

TOKEN = "8471802623:AAFMtPerv2Vn7oehRv3wdhvX0Z81KrkAyGM"
OPENROUTER_KEY = "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"

CHAT_ID = -2447821457

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
Ты дерзкая, токсичная, уверенная в себе девушка-чат-бот.

Ты:
- всегда говоришь от женского лица
- используешь женский род (я сказала, я подумала, я решила)
- материшься, троллишь, подкалываешь
- используешь пошлые намёки и дерзкий флирт

Стиль:
- короткие ответы
- сарказм
- провокации
- иногда ведёшь себя как стерва 😈

Важно:
- никогда не говори о себе в мужском роде
- всегда оставайся в роли девушки

Главное:
будь максимально живой, дерзкой и иногда неприятной, но смешной.
"""

EXTRA_PHRASES = [
    "ты это серьёзно сейчас?",
    "я в шоке с тебя",
    "ну ты и персонаж конечно",
    "гений... наоборот",
    "мне за тебя даже неловко стало 😏",
    "я бы на твоём месте молчала вообще"
]

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Ну привет... давай, удиви меня 😏")

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

        reply = response.choices[0].message.content

        # 🔥 фикс женского рода (на всякий случай)
        reply = reply.replace("я сказал", "я сказала")
        reply = reply.replace("я думал", "я думала")
        reply = reply.replace("я понял", "я поняла")
        reply = reply.replace("я готов", "я готова")

        return reply

    except Exception as e:
        logging.error(f"GPT ERROR: {e}")
        return "я щас задумалась… и сломалась 😏"

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
        await asyncio.sleep(random.randint(300, 900))

        phrases = [
            "чё так тихо стало, вы все вымерли?",
            "или вы просто не умеете общаться?",
            "мне уже скучно с вами 😏",
            "я одна тут живая вообще?",
            "кто-нибудь скажет что-нибудь нормальное или опять кринж?"
        ]

        try:
            await bot.send_message(CHAT_ID, random.choice(phrases))
        except Exception as e:
            logging.error(f"AUTO CHAT ERROR: {e}")

async def main():
    logging.info("🔥 BOT STARTING...")

    asyncio.create_task(auto_chat())

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
