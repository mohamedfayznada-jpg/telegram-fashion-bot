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
        limit=30
    )

    print("\nSTART_MESSAGES\n")

    for msg in messages:

        print("=" * 60)

        print("ID:", msg.id)

        text = (msg.message or "").strip()

        print("TEXT:")
        print(repr(text))

        print("MEDIA:")
        print(msg.media is not None)

    print("\nEND_MESSAGES\n")


with client:
    client.loop.run_until_complete(main())
