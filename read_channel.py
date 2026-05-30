import os
import re
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


IGNORED_WORDS = [
    "السلام عليكم",
    "تم تحويل",
    "العمولات",
    "كل سنه",
    "كل سنة",
    "عيد",
    "❤️",
    "❤"
]


def is_product_text(text):
    text = text.strip()

    if len(text) < 10:
        return False

    for word in IGNORED_WORDS:
        if word in text:
            return False

    return True


def extract_price(text):

    patterns = [
        r'(\d+)\s*جنيه',
        r'(\d+)\s*ج',
        r'(\d+)\s*ج\.م',
        r'(\d+)\s*EGP',
        r'السعر\s*:?\s*(\d+)'
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    return ""


async def main():

    await client.start()

    channel = await client.get_entity(
        "yasminstoriii"
    )

    messages = await client.get_messages(
        channel,
        limit=100
    )

    product_msg = None

    for msg in messages:

        text = (msg.message or "").strip()

        if is_product_text(text):
            product_msg = msg
            break

    if not product_msg:
        print("NO PRODUCT FOUND")
        return

    product_text = product_msg.message

    images = []

    found_description = False

    for msg in messages:

        if msg.id == product_msg.id:
            found_description = True
            continue

        if not found_description:
            continue

        text = (msg.message or "").strip()

        if text:
            break

        if msg.media:
            images.append(msg.id)

    print("\n========================")
    print("PRODUCT_TEXT:")
    print(product_text)

    print("\nPRICE:")
    print(extract_price(product_text))

    print("\nIMAGES_COUNT:")
    print(len(images))

    print("\nIMAGE_IDS:")
    print(images)

    print("========================\n")


with client:
    client.loop.run_until_complete(main())
