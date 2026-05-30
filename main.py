import os
from telegram import Bot
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)
async def main():
    await client.start()

    channel = await client.get_entity("yasminstoriii")

    messages = await client.get_messages(
        channel,
        limit=5
    )

    for i, msg in enumerate(messages):
        print("=" * 50)
        print("MESSAGE", i + 1)
        print("ID:", msg.id)
        print("TEXT:", repr(msg.message))
        print("MEDIA:", msg.media is not None)
asyncio.run(main())
