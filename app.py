from flask import Flask
import threading
import requests
import time
import logging
import os

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# 🌍 URL для пинга (меняй если нужно)
RENDER_URL = os.getenv("RENDER_URL", "https://nastya-cxkb.onrender.com")


@app.route("/")
def home():
    return "Bot is alive 😈"


def ping():
    while True:
        try:
            logging.info("📡 PING...")
            requests.get(RENDER_URL, timeout=10)
            logging.info("✅ PING OK")
        except Exception as e:
            logging.error(f"❌ PING ERROR: {e}")

        time.sleep(300)


def start_ping():
    thread = threading.Thread(target=ping, daemon=True)
    thread.start()


# 🚀 запуск пинга сразу
start_ping()


if __name__ == "__main__":
    logging.info("🌐 FLASK START")
    app.run(host="0.0.0.0", port=10000)
