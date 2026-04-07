import threading
import asyncio
import logging
import time
from bot import main as bot_main
from app import app


def run_web():
    logging.info("🌐 WEB STARTED")
    app.run(host="0.0.0.0", port=10000)


async def run_bot_forever():
    while True:
        try:
            logging.info("🔥 BOT STARTING...")
            await bot_main()
        except Exception as e:
            logging.error(f"💥 BOT CRASH: {e}")
            logging.info("🔄 Перезапуск через 5 секунд...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # 🌐 Flask в фоне
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()

    # 🤖 Бот (с авто-перезапуском)
    try:
        asyncio.run(run_bot_forever())
    except KeyboardInterrupt:
        logging.info("🛑 BOT STOPPED")
