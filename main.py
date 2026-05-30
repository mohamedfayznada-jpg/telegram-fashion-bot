from telegram import Bot

BOT_TOKEN = "8874494543:AAG5Xt4nuEkSWIMt4DHwSFHoDB6hh9DZWMI"
CHAT_ID = "823684938"

bot = Bot(token=BOT_TOKEN)

async def main():
    await bot.send_message(
        chat_id=CHAT_ID,
        text="✅ البوت شغال بنجاح"
    )

import asyncio
asyncio.run(main())
