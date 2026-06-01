import os
import json
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    print("❌ بيانات تيلجرام غير متوفرة (BOT_TOKEN أو CHAT_ID).")
    exit(0)

# قراءة بيانات المنتج والسعر
try:
    with open("product.json", "r", encoding="utf-8") as f:
        product = json.load(f)
except Exception:
    product = {}

code = product.get("product_code", "غير محدد")
price = product.get("price", "غير محدد") # ده اللي هيجيب السعر من الملف اللي قبله

# قراءة البوست النهائي
try:
    with open("facebook_post_sales.txt", "r", encoding="utf-8") as f:
        fb_post = f.read().strip()
except:
    fb_post = "تم النشر بنجاح."

# تجهيز الرسالة
message = f"""
🎉 **تم النشر بنجاح على صفحة Fastyle!** 🚀

👗 **كود الموديل:** {code}
💰 **السعر:** {price}

📄 **نص البوست اللي نزل:**
{fb_post}

✅ (تم رفع البوست + الستوري + فيديو الريلز بنجاح)
"""

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": message,
    "parse_mode": "Markdown"
}

response = requests.post(url, json=payload)
if response.status_code == 200:
    print("✅ تم إرسال تقرير النجاح إلى تيلجرام!")
else:
    print(f"❌ خطأ في إرسال التقرير: {response.text}")
