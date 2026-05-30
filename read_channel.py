import os
import re
import json
import base64
import requests

from telethon import TelegramClient

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]

OPENROUTER_API_KEY = os.environ[
    "OPENROUTER_API_KEY"
]

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


def generate_facebook_post(prompt):

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization":
                f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type":
                "application/json"
        },
        json={
            "model": "openai/gpt-4.1",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]


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
        "product_id":
            product_msg.id,

        "product_code":
            product_code,

        "price":
            price,

        "description":
            description,

        "images":
            downloaded
    }

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
أنت خبير تسويق محترف في الملابس النسائية.

اكتب بوست فيسبوك احترافي باللهجة المصرية.

بيانات المنتج:

الكود:
{product_code}

الوصف:
{description}

قواعد مهمة:

- ممنوع ذكر السعر.
- اذكر الكود فقط.
- ركز على الشياكة.
- ركز على جودة الخامة.
- استخدم ايموجي.
- اعمل Call To Action قوي.
- اطلب من العميل إرسال الكود لمعرفة السعر.
- اجعل البوست جاهز للنشر.
"""

    with open(
        "post_prompt.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(prompt)

    print("\nGENERATING_FACEBOOK_POST...\n")

    facebook_post = generate_facebook_post(
        prompt
    )

    with open(
        "facebook_post.txt",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            facebook_post
        )

    print(
        "========================"
    )

    print(
        "PRODUCT_ID:"
    )
    print(
        product_msg.id
    )

    print(
        "\nPRODUCT_CODE:"
    )
    print(
        product_code
    )

    print(
        "\nPRICE:"
    )
    print(
        price
    )

    print(
        "\nIMAGES_COUNT:"
    )
    print(
        len(downloaded)
    )

    print(
        "\nFACEBOOK_POST:\n"
    )

    print(
        facebook_post
    )

    print(
        "\n========================"
    )


with client:
    client.loop.run_until_complete(
        main()
    )        "yasminstoriii"
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
        print("PRODUCT INDEX NOT FOUND")
        return

    for i in range(product_index + 1, len(messages)):

        msg = messages[i]

        text = (msg.message or "").strip()

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

    clean_text = clean_description(
        product_msg.message
    )

    product_data = {
        "product_id": product_msg.id,
        "product_code": product_code,
        "price": price,
        "description": clean_text,
        "images": downloaded
    }

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

    price_db = {
        product_code: price
    }

    with open(
        "price_db.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            price_db,
            f,
            ensure_ascii=False,
            indent=2
        )

    prompt = f"""
أنت خبير تسويق احترافي في مجال الملابس النسائية.

بيانات المنتج:

الكود:
{product_code}

الوصف:
{clean_text}

المطلوب:

1- كتابة بوست فيسبوك احترافي باللهجة المصرية.
2- عدم ذكر السعر نهائياً.
3- التركيز على جودة الخامة.
4- التركيز على الأناقة والشياكة.
5- إضافة Call To Action قوي.
6- إضافة Emojis.
7- إضافة Hashtags.
8- ذكر كود المنتج فقط.
9- دعوة العميل لإرسال الكود لمعرفة السعر.
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

    print("========================\n")


with client:
    client.loop.run_until_complete(main())
