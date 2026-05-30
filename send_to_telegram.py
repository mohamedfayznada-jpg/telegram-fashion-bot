import os
import requests

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

caption = ""

files_to_read = [
    "facebook_post_soft.txt",
    "facebook_post_sales.txt",
    "facebook_post_viral.txt",
    "story_post.txt"
]

for file in files_to_read:

    if os.path.exists(file):

        caption += f"\n\n===== {file} =====\n\n"

        with open(
            file,
            "r",
            encoding="utf-8"
        ) as f:

            caption += f.read()

r = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    data={
        "chat_id": CHAT_ID,
        "text": caption[:4000]
    }
)

print("\nSEND MESSAGE RESPONSE:\n")
print(r.text)

if os.path.exists("marketing_collage.jpg"):

    with open(
        "marketing_collage.jpg",
        "rb"
    ) as photo:

        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
            data={
                "chat_id": CHAT_ID
            },
            files={
                "photo": photo
            }
        )

        print("\nSEND PHOTO RESPONSE:\n")
        print(r.text)

else:

    print(
        "\nmarketing_collage.jpg NOT FOUND\n"
    )

print("SENT TO TELEGRAM")
