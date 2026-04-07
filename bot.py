import asyncio
import random
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from openai import OpenAI

TOKEN = "8471802623:AAFMtPerv2Vn7oehRv3wdhvX0Z81KrkAyGM"
OPENROUTER_KEY = "sk-or-v1-..."

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

# 🧠 ПАМЯТЬ
user_memory = {}

SYSTEM_PROMPT = """
Ты дерзкая, умная, токсичная девушка.

Ты:
- понимаешь контекст разговора
- отвечаешь логично
- умеешь подколоть, но не тупишь
- иногда саркастичная, но не бессмысленная

Важно:
- всегда говори от женского лица
- не пиши банальности
"""

EXTRA_PHRASES = [
    "ты это серьёзно сейчас?",
    "я в шоке с тебя",
    "ну ты и персонаж конечно",
    "гений... наоборот",
]

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Ну привет... давай, удиви меня 😏")


# 🔥 УМНЫЙ ОТВЕТ С ПАМЯТЬЮ
async def generate_reply(user_id, text):
    try:
        history = user_memory.get(user_id, [])

        history.append({"role": "user", "content": text})

        response = client.chat.completions.create(
            model="nousresearch/nous-hermes-2",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *history[-6:]
            ],
            temperature=1.1,
            max_tokens=200,
        )

        reply = response.choices[0].message.content

        history.append({"role": "assistant", "content": reply})
        user_memory[user_id] = history

        # фиксим женский род
        reply = reply.replace("я сказал", "я сказала")
        reply = reply.replace("я думал", "я думала")

        return reply

    except Exception as e:
        logging.error(f"GPT ERROR: {e}")
        return "я щас задумалась… и зависла 😏"


@dp.message()
async def chat(message: Message):
    if not message.text:
        return

    if random.randint(1, 100) > 80:
        return

    username = message.from_user.first_name

    reply = await generate_reply(message.from_user.id, message.text)

    reply = f"{username}, {reply}"

    # иногда добавляем токсичность
    if random.randint(1, 100) < 50:
        reply += "\n\n" + random.choice(EXTRA_PHRASES)

    await message.reply(reply)


# 😈 АВТО-ЧАТ
async def auto_chat():
    while True:
        await asyncio.sleep(random.randint(300, 900))

        phrases = [
            "чё так тихо стало?",
            "мне уже скучно с вами 😏",
            "я одна тут нормальная вообще?",
            "кто-нибудь скажет что-то умное или как обычно?"
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
