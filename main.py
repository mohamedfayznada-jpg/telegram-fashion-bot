from telegram import Bot

BOT_TOKEN = "PUT_BOT_TOKEN"
CHAT_ID = "823684938"

bot = Bot(token=BOT_TOKEN)

async def main():
    await bot.send_message(
        chat_id=CHAT_ID,
        text="✅ البوت شغال بنجاح"
    )

import asyncio
asyncio.run(main())
