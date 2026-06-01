import os
import json
import requests

# التأكد من عدم وجود علم التخطي
if os.path.exists("skip_flag.txt"):
    exit(0)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    print("❌ بيانات بوت تيلجرام غير متوفرة.")
    exit(0)

# محاولة قراءة بيانات المنتج
try:
    with open("product.json", "r", encoding="utf-8") as f:
        product = json.load(f)
except Exception:
    product = {}

code = product.get("product_code", "غير محدد")
price = product.get("price", "غير محدد")

# قراءة الذاكرة (posted_ids.json) لمعرفة عدد المنتجات التي تم نشرها
try:
    if os.path.exists("posted_ids.json"):
        with open("posted_ids.json", "r") as f:
            posted_ids = json.load(f)
        processed_count = len(posted_ids)
    else:
        processed_count = 0
except Exception:
    processed_count = 0

# قراءة نص البوست الذي تم نشره
try:
    with open("facebook_post_sales.txt", "r", encoding="utf-8") as f:
        fb_post = f.read().strip()
except Exception:
    fb_post = "تم النشر بنجاح."

# تجهيز الرسالة الشاملة التي ستصلك في البوت
message = f"""
🎉 **تم النشر التلقائي بنجاح!** 🚀

👗 **كود الموديل:** {code}
💰 **السعر:** {price}

📊 **حالة الطابور:**
تم معالجة {processed_count} منتج حتى الآن.

📄 **نص البوست:**
{fb_post}

✅ (تم رفع البوست + الستوري + فيديو الريلز بنجاح)
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
