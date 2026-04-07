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

# 📊 АКТИВНОСТЬ
user_stats = {}

SYSTEM_PROMPT = """
Ты умная, дерзкая девушка.

Ты:
- понимаешь контекст
- отвечаешь логично и по делу
- если вопрос тупой — подкалываешь
- если нормальный — отвечаешь нормально

НЕ:
- не пиши шаблоны
- не повторяйся
- не пиши банальности

Говори как живой человек.
"""

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Ну привет... давай, удиви меня 😏")


# 🔥 ПРОВЕРКА AI
async def check_ai():
    try:
        client.chat.completions.create(
            model="meta-llama/llama-3-70b-instruct",
            messages=[{"role": "user", "content": "Ответь: ок"}],
            max_tokens=5,
        )
        return True
    except Exception as e:
        logging.error(f"AI CHECK ERROR: {e}")
        return False


# 🔥 УМНЫЙ AI
async def generate_reply(user_id, text):
    try:
        history = user_memory.get(user_id, [])

        history.append({"role": "user", "content": text})

        response = client.chat.completions.create(
            model="meta-llama/llama-3-70b-instruct",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *history[-12:]
            ],
            temperature=0.9,
            max_tokens=300,
        )

        reply = response.choices[0].message.content.strip()

        history.append({"role": "assistant", "content": reply})
        user_memory[user_id] = history

        reply = reply.replace("я сказал", "я сказала")
        reply = reply.replace("я думал", "я думала")

        return reply

    except Exception as e:
        logging.error(f"GPT ERROR: {e}")
        return "блин, я зависла… повтори нормально 😒"


# 🎯 цель (активный)
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
        reply += "\n\nты слишком часто пишешь… я уже наблюдаю 😏"

    await message.reply(reply)


# 😈 авто-чат
async def auto_chat():
    while True:
        await asyncio.sleep(random.randint(300, 900))

        phrases = [
            "чё так тихо стало?",
            "мне уже скучно с вами 😏",
            "я одна тут думаю или как?",
            "кто-нибудь вообще умеет нормально говорить?",
            "или вы просто пишете ради шума?"
        ]

        try:
            await bot.send_message(CHAT_ID, random.choice(phrases))
        except Exception as e:
            logging.error(f"AUTO CHAT ERROR: {e}")


# 🔥 уведомление о статусе AI
async def ai_status_notify():
    while True:
        await asyncio.sleep(1800)  # каждые 30 минут

        status = await check_ai()

        try:
            if status:
                await bot.send_message(CHAT_ID, "🟢 я жива, мозги работают 😏")
            else:
                await bot.send_message(CHAT_ID, "🔴 я сломалась… не тупите пока без меня 😒")
        except Exception as e:
            logging.error(f"STATUS ERROR: {e}")


async def main():
    logging.info("🔥 BOT STARTING...")

    await bot.delete_webhook(drop_pending_updates=True)

    # 🔥 проверка при старте
    status = await check_ai()

    if status:
        await bot.send_message(CHAT_ID, "🟢 я запустилась и готова разносить чат 😈")
    else:
        await bot.send_message(CHAT_ID, "🔴 я запустилась, но мозги не работают 😒")

    asyncio.create_task(auto_chat())
    asyncio.create_task(ai_status_notify())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
