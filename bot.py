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

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🎯 ЦЕЛЕВЫЕ ПОЛЬЗОВАТЕЛИ
TARGET_USERS = [
    8276937335,
    785245733,
    7836790626,
]


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("бот активен")


@dp.message()
async def chat(message: Message):
    if not message.text:
        return

    user_id = message.from_user.id

    if user_id in TARGET_USERS:
        name = message.from_user.first_name
        mention = f"<a href='tg://user?id={user_id}'>{name}</a>"

        await message.reply(
            f"{mention}, ПОШЁЛ НА ХУЙ ЧЁРТ !!!",
            parse_mode="HTML"
        )


async def main():
    logging.info("🔥 BOT STARTING...")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
