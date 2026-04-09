import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart

# 🔐 ENV
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("❌ TOKEN не найден!")

CHAT_ID = -1002447821457

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🚫 СПИСОК ЦЕЛЕВЫХ ПОЛЬЗОВАТЕЛЕЙ
TARGET_USERS = [
    8276937335,
    785245733,
]

# 💣 ТЕКСТ ОТВЕТА (ВПИШИ ЧТО ХОЧЕШЬ)
TARGET_REPLY = "НАПИШИ ТУТ СВОЙ ТЕКСТ"


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("бот активен 😈")


@dp.message()
async def chat(message: Message):
    if not message.text:
        return

    user_id = message.from_user.id

    # 💣 ЕСЛИ ЭТО ЦЕЛЕВОЙ ПОЛЬЗОВАТЕЛЬ
    if user_id in TARGET_USERS:
        name = message.from_user.first_name

        # упоминание пользователя
        mention = f"<a href='tg://user?id={user_id}'>{name}</a>"

        await message.reply(
            f"{mention}, {TARGET_REPLY}",
            parse_mode="HTML"
        )
        return


async def auto_chat():
    while True:
        await asyncio.sleep(600)

        try:
            await bot.send_message(CHAT_ID, "я тут 😈")
        except Exception as e:
            logging.error(f"AUTO CHAT ERROR: {e}")


async def main():
    logging.info("🔥 BOT STARTING...")

    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(auto_chat())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
