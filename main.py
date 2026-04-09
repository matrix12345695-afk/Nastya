import threading
import asyncio
import logging
import time
from bot import main as bot_main
from app import app


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def run_web():
    while True:
        try:
            logging.info("🌐 WEB SERVER STARTED")
            app.run(host="0.0.0.0", port=10000)
        except Exception as e:
            logging.error(f"💥 WEB CRASH: {e}")
            logging.info("🔄 Перезапуск WEB через 3 секунды...")
            time.sleep(3)


async def run_bot_forever():
    while True:
        try:
            logging.info("🤖 BOT LAUNCH...")
            await bot_main()
        except Exception as e:
            logging.error(f"💥 BOT CRASH: {e}")
            logging.info("🔄 Перезапуск бота через 5 секунд...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    logging.info("🚀 SYSTEM START")

    # 🌐 Flask в отдельном потоке
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()

    # 🤖 Бот
    try:
        asyncio.run(run_bot_forever())
    except KeyboardInterrupt:
        logging.info("🛑 SYSTEM STOPPED")
