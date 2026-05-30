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
        limit=150
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

    image_messages = []

    product_index = None

    for i, msg in enumerate(messages):

        if msg.id == product_msg.id:
            product_index = i
            break

    if product_index is None:
        return

    for i in range(product_index + 1, len(messages)):

        msg = messages[i]

        text = (msg.message or "").strip()

        if text:
            break

        if msg.media:
            image_messages.append(msg)

    image_messages.reverse()

    os.makedirs("downloads", exist_ok=True)

    downloaded = []

    for msg in image_messages:

        filename = await client.download_media(
            msg,
            file=f"downloads/{msg.id}"
        )

        downloaded.append(filename)

    price = extract_price(
        product_msg.message
    )

    product_code = f"FS{product_msg.id}"

    print("\n========================")

    print("PRODUCT_ID:")
    print(product_msg.id)

    print("\nPRODUCT_CODE:")
    print(product_code)

    print("\nPRODUCT_TEXT:")
    print(product_msg.message)

    print("\nPRICE:")
    print(price)

    print("\nIMAGES_COUNT:")
    print(len(downloaded))

    print("\nDOWNLOADED_FILES:")

    for f in downloaded:
        print(f)

    print("\nPROMPT_FOR_AI:")

    print(
        f"""
PRODUCT_CODE: {product_code}

PRODUCT_DESCRIPTION:
{product_msg.message}

HIDDEN_PRICE:
{price}

TASK:
Create a powerful Facebook fashion post in Egyptian Arabic.
Do not mention the price.
Create urgency.
Highlight fabric quality.
Highlight style.
Add call to action.
Use emojis.
Mention product code only.
"""
    )

    print("========================\n")


with client:
    client.loop.run_until_complete(main())
