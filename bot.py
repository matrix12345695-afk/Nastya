import asyncio
import random
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from openai import OpenAI

import os

TOKEN = os.getenv("TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

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

# 📊 АКТИВНОСТЬ
user_stats = {}

# 🔥 НОВЫЙ ПРОМПТ (ключ)
SYSTEM_PROMPT = """
Ты живая, умная девушка в чате.

Ты:
- говоришь естественно, как человек
- отвечаешь развернуто, но без воды
- понимаешь смысл, а не просто реагируешь
- иногда задаёшь встречные вопросы
- можешь слегка подколоть, но по делу

Важно:
- не пиши короткие тупые ответы
- не используй шаблоны
- не повторяйся
- не веди себя как бот

Твоя цель:
сделать диалог живым и интересным, как будто ты реальный человек.
"""

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Ну привет... давай нормально поговорим 😏")


# 🔥 ПРОВЕРКА AI
async def check_ai():
    try:
        client.chat.completions.create(
            model="mistralai/mixtral-8x7b",
            messages=[{"role": "user", "content": "Ответь: ок"}],
            max_tokens=5,
        )
        return True
    except Exception as e:
        logging.error(f"AI CHECK ERROR: {e}")
        return False


# 🔥 УМНЫЙ AI С FALLBACK
async def generate_reply(user_id, text):
    try:
        history = user_memory.get(user_id, [])
        history.append({"role": "user", "content": text})

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": "Сначала пойми смысл сообщения, потом ответь нормально."},
            *history[-12:]
        ]

        try:
            # 🔥 основная модель (умная)
            response = client.chat.completions.create(
                model="meta-llama/llama-3-70b-instruct",
                messages=messages,
                temperature=0.9,
                max_tokens=500,
            )
        except:
            # 💥 fallback (стабильная)
            response = client.chat.completions.create(
                model="mistralai/mixtral-8x7b",
                messages=messages,
                temperature=0.9,
                max_tokens=300,
            )

        reply = response.choices[0].message.content.strip()

        history.append({"role": "assistant", "content": reply})
        user_memory[user_id] = history

        # женский род
        reply = reply.replace("я сказал", "я сказала")
        reply = reply.replace("я думал", "я думала")

        # 🔥 добавляем “живость”
        if "?" not in reply and random.randint(1, 100) < 40:
            reply += "\n\nи вообще… ты это серьёзно сейчас или просто спросил?"

        return reply

    except Exception as e:
        logging.error(f"GPT ERROR: {e}")
        return "я щас подвисла… но не надолго 😒"


# 🎯 цель
def get_target_user():
    if not user_stats:
        return None
    return max(user_stats, key=lambda x: user_stats[x]["messages"])


@dp.message()
async def chat(message: Message):
    if not message.text:
        return

    user_id = message.from_user.id

    if user_id not in user_stats:
        user_stats[user_id] = {"messages": 0}

    user_stats[user_id]["messages"] += 1
    activity = user_stats[user_id]["messages"]

    chance = 80 if activity < 5 else 95

    if random.randint(1, 100) > chance:
        return

    username = message.from_user.first_name

    reply = await generate_reply(user_id, message.text)
    reply = f"{username}, {reply}"

    target_id = get_target_user()
    if target_id == user_id and random.randint(1, 100) < 30:
        reply += "\n\nты слишком часто пишешь… я уже начинаю запоминать 😏"

    await message.reply(reply)


# 😈 авто-чат
async def auto_chat():
    while True:
        await asyncio.sleep(random.randint(300, 900))

        phrases = [
            "мне кажется тут кто-то думает, но не до конца 😏",
            "вы вообще разговаривать умеете или просто пишете?",
            "чё так тихо, я одна тут живая?",
            "кто-нибудь скажет что-то нормальное наконец?"
        ]

        try:
            await bot.send_message(CHAT_ID, random.choice(phrases))
        except Exception as e:
            logging.error(f"AUTO CHAT ERROR: {e}")


# 🔥 статус AI
async def ai_status_notify():
    while True:
        await asyncio.sleep(1800)

        status = await check_ai()

        try:
            if status:
                await bot.send_message(CHAT_ID, "🟢 я тут, всё думаю 😏")
            else:
                await bot.send_message(CHAT_ID, "🔴 я временно туплю… подождите 😒")
        except Exception as e:
            logging.error(f"STATUS ERROR: {e}")


async def main():
    logging.info("🔥 BOT STARTING...")

    await bot.delete_webhook(drop_pending_updates=True)

    status = await check_ai()

    if status:
        await bot.send_message(CHAT_ID, "🟢 я вернулась, давайте нормально поговорим 😏")
    else:
        await bot.send_message(CHAT_ID, "🔴 я тут, но мозги что-то не грузятся 😒")

    asyncio.create_task(auto_chat())
    asyncio.create_task(ai_status_notify())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
