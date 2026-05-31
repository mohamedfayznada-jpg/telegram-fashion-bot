import os
import requests

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# 1. إرسال الصورة المجمعة (Collage) أولاً
if os.path.exists("marketing_collage.jpg"):
    with open("marketing_collage.jpg", "rb") as photo:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
            data={
                "chat_id": CHAT_ID,
                "caption": "🔥 كولاچ المنتج المجمع"
            },
            files={"photo": photo}
        )
        print("\nSEND PHOTO RESPONSE:\n")
        print(r.text)
else:
    print("\nmarketing_collage.jpg NOT FOUND\n")


# 2. إرسال كل بوست في رسالة منفصلة لتجنب قص النصوص (Truncation)
files_to_read = {
    "facebook_post_soft.txt": "البوست الهادي (Soft)",
    "facebook_post_sales.txt": "بوست البيع المباشر (Sales)",
    "facebook_post_viral.txt": "بوست التفاعل (Viral)",
    "story_post.txt": "محتوى الاستوري (Story)"
}

for file, title in files_to_read.items():
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            
        if content: # تأكد إن الملف فيه داتا فعلاً
            message_text = f"===== {title} =====\n\n{content}"
            r = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={
                    "chat_id": CHAT_ID,
                    "text": message_text
                }
            )
            print(f"\nSEND {file} RESPONSE:\n")
            print(r.text)

print("\nALL CONTENT SENT TO TELEGRAM")
