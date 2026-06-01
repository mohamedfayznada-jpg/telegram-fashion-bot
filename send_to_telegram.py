import os
import json
import requests

if os.path.exists("skip_flag.txt"):
    exit(0)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    print("❌ بيانات بوت تيلجرام غير متوفرة.")
    exit(0)

try:
    with open("product.json", "r", encoding="utf-8") as f:
        product = json.load(f)
except Exception:
    product = {}

code = product.get("product_code", "غير محدد")
price = product.get("price", "غير محدد")

try:
    with open("facebook_post_sales.txt", "r", encoding="utf-8") as f:
        fb_post = f.read().strip()
except Exception:
    fb_post = "تم النشر."

message = f"""
🎉 **تم النشر التلقائي بنجاح!** 🚀

👗 **كود الموديل:** {code}
💰 **السعر:** {price}

📄 **نص البوست:**
{fb_post}

✅ تمت العملية بالكامل (بوست + ستوري + ريلز)
"""

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": message,
    "parse_mode": "Markdown"
}

try:
    response = requests.post(url, json=payload, timeout=10)
    if response.status_code == 200:
        print("✅ تم إرسال تقرير النجاح إلى تيلجرام.")
    else:
        print(f"⚠️ خطأ في إرسال التقرير: {response.text}")
except Exception as e:
    print(f"⚠️ فشل الاتصال بتيلجرام: {e}")
