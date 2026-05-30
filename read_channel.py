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
        limit=30
    )

    product_text = None
    product_message_id = None

    # ابحث عن أول رسالة نصية حقيقية
    for msg in messages:

        text = (msg.message or "").strip()

        if text:

            product_text = text
            product_message_id = msg.id
            break

    if not product_text:

        print("NO PRODUCT FOUND")
        return

    images = []

    found_description = False

    # اجمع الصور الموجودة فوق الوصف
    for msg in messages:

        if msg.id == product_message_id:
            found_description = True
            continue

        if not found_description:
            continue

        text = (msg.message or "").strip()

        # وصلنا لوصف المنتج السابق
        if text:
            break

        if msg.media:
            images.append(msg.id)

    price = extract_price(product_text)

    clean_text = product_text

    clean_text = re.sub(
        r'\d+\s*جنيه',
        '',
        clean_text,
        flags=re.IGNORECASE
    )

    clean_text = re.sub(
        r'\d+\s*ج',
        '',
        clean_text,
        flags=re.IGNORECASE
    )

    clean_text = re.sub(
        r'السعر\s*:?\s*\d+',
        '',
        clean_text,
        flags=re.IGNORECASE
    )

    print("\n======================")
    print("PRODUCT_TEXT:")
    print(clean_text)

    print("\nPRICE:")
    print(price)

    print("\nIMAGES_COUNT:")
    print(len(images))

    print("\nIMAGE_IDS:")
    print(images)

    print("======================\n")


with client:
    client.loop.run_until_complete(main())
