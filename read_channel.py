import os
import re
import json
import base64

from telethon import TelegramClient

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]

session_data = base64.b64decode(
    os.environ["TELEGRAM_SESSION"]
)

with open(
    "telegram_session.session",
    "wb"
) as f:
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
    "كل سنة",

    "عيد",
    "العيد",
    "اجازة",
    "إجازة",
    "استئناف العمل",
    "الشحن",
    "مكتب",
    "بداية جديدة",
    "كل عام وانتم بخير",
    "كل عام وأنتم بخير"
]


def is_admin_message(text):

    text = text.lower()

    for word in IGNORE_WORDS:

        if word.lower() in text:
            return True

    return False


def extract_fabric(text):

    match = re.search(
        r"الخامه\s*👈\s*(.+)",
        text
    )

    if match:
        return match.group(1).strip()

    return ""


def extract_size(text):

    match = re.search(
        r"المقاس\s*👈\s*(.+)",
        text
    )

    if match:
        return match.group(1).strip()

    return ""


def extract_product_type(text):

    match = re.search(
        r"الموديل\s*👈\s*(.+)",
        text
    )

    if match:
        return match.group(1).strip()

    return ""

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


def extract_product_code(text):

    lines = text.splitlines()

    for line in reversed(lines):

        line = line.strip()

        if line.isdigit():
            return f"FS{line}"

    return ""


def clean_description(text):

    text = re.sub(
        r"السعر.*",
        "",
        text,
        flags=re.IGNORECASE
    )

    return text.strip()


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

    text = (
        msg.message or ""
    ).strip()

    if not text:
        continue

    if len(text) < 20:
        continue

    if is_admin_message(text):
        continue

    if not msg.media:
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

        print("PRODUCT INDEX NOT FOUND")
        return

    for i in range(
        product_index + 1,
        len(messages)
    ):

        msg = messages[i]

        text = (
            msg.message or ""
        ).strip()

        if text:
            break

        if msg.media:
            image_messages.append(msg)

    image_messages.reverse()

    os.makedirs(
        "downloads",
        exist_ok=True
    )

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

    product_code = extract_product_code(
        product_msg.message
    )

    description = clean_description(
        product_msg.message
    )

    product_data = {
        "product_id": product_msg.id,
        "product_code": product_code,
        "price": price,
        "description": description,
        "images": downloaded
    }
    product_summary = {
        "product_code": product_code,
        "product_type": extract_product_type(
            product_msg.message
        ),
        "fabric": extract_fabric(
            product_msg.message
        ),
        "size": extract_size(
            product_msg.message
        ),
        "price": price
    }

    with open(
        "product_summary.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            product_summary,
            f,
            ensure_ascii=False,
            indent=2
        )

    with open(
        "product.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            product_data,
            f,
            ensure_ascii=False,
            indent=2
        )

    with open(
        "price_db.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            {
                product_code: price
            },
            f,
            ensure_ascii=False,
            indent=2
        )
       

    prompt = f"""
الكود:
{product_code}

الوصف:
{description}

اكتب:
1- Facebook Post
2- Hashtags
3- Story Post
4- Reel Idea
5- Best Images
"""

    with open(
        "post_prompt.txt",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(prompt)

    print("\n========================")

    print("PRODUCT_ID:")
    print(product_msg.id)

    print("\nPRODUCT_CODE:")
    print(product_code)

    print("\nPRICE:")
    print(price)

    print("\nIMAGES_COUNT:")
    print(len(downloaded))

    print("\nFILES_CREATED:")

    print("product.json")
    print("price_db.json")
    print("post_prompt.txt")

    print("\n========================")


with client:
    client.loop.run_until_complete(
        main()
    )
