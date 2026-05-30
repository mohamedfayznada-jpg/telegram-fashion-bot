import os
import base64
from telethon import TelegramClient

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]

session_data = base64.b64decode(
    os.environ["TELEGRAM_SESSION"]
)

with open("telegram_session.session", "wb") as f:
    f.write(session_data)

client = TelegramClient(
    "telegram_session",
    API_ID,
    API_HASH
)

async def main():
    await client.start()

    channel = await client.get_entity(
        "yasminstoriii"
    )

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
print("RAW_TEXT:", msg.message)
with client:
    client.loop.run_until_complete(main())

