import threading
import asyncio
import logging
from bot import main as bot_main
from app import app

def run_web():
    logging.info("🌐 WEB STARTED")
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # 🔥 Flask в фоне (daemon=True чтобы не мешал)
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()

    # 😈 Бот в главном потоке (ВАЖНО)
    logging.info("🔥 BOT STARTING...")

    try:
        asyncio.run(bot_main())
    except Exception as e:
        logging.error(f"BOT CRASH: {e}")
