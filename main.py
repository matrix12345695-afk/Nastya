import threading
import asyncio
import logging
from bot import main as bot_main
from app import app

def run_bot():
    print("🔥 BOT STARTING...")
    asyncio.run(bot_main())

def run_web():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    threading.Thread(target=run_bot).start()
    run_web()
