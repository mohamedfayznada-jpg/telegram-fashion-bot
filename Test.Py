import os
import requests

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

r = requests.get(
    f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
)

print(r.text)
