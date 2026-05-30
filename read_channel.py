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

IGNORE_WORDS = [
    "السلام عليكم",
    "تم تحويل",
    "العمولات",
    "اوردر",
    "يمنشن",
    "منشن",
    "قاهره",
    "جيزه",
    "كل سنه",
    "كل سنة"
]


def is_admin_message(text):

    text = text.lower()

    for word in IGNORE_WORDS:
        if word.lower() in text:
            return True

    return False


def extract_price(text):

    patterns = [
        r"السعر.*?(\d+)",
        r"(\d+)\s*ج",
        r"(\d+)\s*جنيه"
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

        if not text:
            continue

        if is_admin_message(text):
            continue

        product_msg = msg
        break

    if not product_msg:

        print("NO PRODUCT FOUND")
        return

    images = []

    found_product = False

    for msg in messages:

        if msg.id == product_msg.id:
            found_product = True
            continue

        if not found_product:
            continue

        text = (msg.message or "").strip()

        if text:
            break

        if msg.media:
            images.append(msg.id)

    print("\n========================")
    print("PRODUCT_ID:")
    print(product_msg.id)

    print("\nPRODUCT_TEXT:")
    print(product_msg.message)

    print("\nPRICE:")
    print(extract_price(product_msg.message))

    print("\nIMAGES_COUNT:")
    print(len(images))

    print("\nIMAGE_IDS:")
    print(images)

    print("========================\n")


with client:
    client.loop.run_until_complete(main())
