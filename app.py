from flask import Flask
import threading
import requests
import time

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive 😈"

def ping():
    while True:
        try:
            requests.get("https://nastya-cxkb.onrender.com")
        except:
            pass
        time.sleep(300)

threading.Thread(target=ping).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
