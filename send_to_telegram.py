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
pending_count = product.get("pending_count", 0)

try:
    with open("facebook_post_sales.txt", "r", encoding="utf-8") as f:
        fb_post = f.read().strip()
except Exception:
    fb_post = "تم النشر بنجاح."

# تجهيز الرسالة لتظهر حالة الطابور بشكل واضح
if pending_count > 0:
    queue_status = f"⏳ **حالة الطابور:**\nيوجد عدد **{pending_count}** منتج في الانتظار (سيتم نشرهم تباعاً)."
else:
    queue_status = f"✅ **حالة الطابور:**\nتم الانتهاء من جميع المنتجات، في انتظار منتجات جديدة."

message = f"""
🎉 **تم النشر التلقائي بنجاح!** 🚀

👗 **كود الموديل:** {code}
💰 **السعر الداخلي:** {price}

{queue_status}

📄 **نص البوست اللي نزل:**
{fb_post}

✅ (تم رفع البوست + الستوري + فيديو الريلز)
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
