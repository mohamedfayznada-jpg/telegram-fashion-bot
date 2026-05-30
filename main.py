import os
from telegram import Bot
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

async def main():
    await bot.send_message(
        chat_id=CHAT_ID,
        text="✅ البوت شغال بنجاح"
    )

asyncio.run(main())
