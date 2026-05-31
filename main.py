import os
from telethon import TelegramClient
import asyncio

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")

async def main():
    # استخدام Telethon بدلاً من python-telegram-bot عشان ميبقاش في تعارض
    client = TelegramClient("telegram_session", API_ID, API_HASH)
    await client.start()

    channel = await client.get_entity("yasminstoriii")
    messages = await client.get_messages(channel, limit=5)

    for i, msg in enumerate(messages):
        print("=" * 50)
        print("MESSAGE", i + 1)
        print("ID:", msg.id)
        print("TEXT:", repr(msg.message))
        print("MEDIA:", msg.media is not None)
        
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
