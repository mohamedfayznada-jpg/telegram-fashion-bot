import os
import re
import json
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ.get("TELEGRAM_SESSION", "").strip()

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH, device_model="Desktop", system_version="Windows 10", app_version="1.0")

IGNORE_WORDS = ["السلام عليكم", "العمولات", "اوردر", "يمنشن", "قاهره", "جيزه", "عيد", "اجازة"]

def extract_price(text):
    arabic_to_english = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
    text = text.translate(arabic_to_english)
    patterns = [r"السعر\s*[:\-]?\s*(\d+)", r"سعر\s*القطعه\s*(\d+)", r"(\d+)\s*ج\.?م", r"(\d+)\s*ج", r"(\d+)\s*جنيه"]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match: return match.group(1)
    return "غير محدد"

def extract_product_code(text):
    text = text.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))
    for line in reversed(text.splitlines()):
        match = re.search(r"(\d{3,})", line.strip())
        if match: return f"FS{match.group(1)}"
    import random
    return f"FS{random.randint(100, 999)}"

async def main():
    await client.start()
    channel = await client.get_entity("yasminstoriii")
    messages = await client.get_messages(channel, limit=100) # فحص آخر 100 رسالة

    # قراءة ذاكرة المنتجات المنشورة مسبقاً
    try:
        with open("posted_ids.json", "r") as f:
            posted_ids = json.load(f)
    except:
        posted_ids = []

    product_msg = None
    
    # البحث من الأقدم للأحدث لنشر المنتجات بالترتيب
    for msg in reversed(messages):
        text = (msg.message or "").strip()
        if not text or any(w.lower() in text.lower() for w in IGNORE_WORDS):
            continue
            
        # التحقق إذا كان المنتج لم يُنشر من قبل
        if msg.id not in posted_ids:
            product_msg = msg
            break

    if not product_msg:
        print("✅ لا يوجد منتجات جديدة لنشرها حالياً.")
        # نكتب ملف فاضي عشان باقي الأكواد تقف باحترام
        with open("skip_flag.txt", "w") as f: f.write("skip")
        return

    # تجميع الصور التابعة للمنتج الجديد
    image_messages = []
    found_start = False
    for msg in reversed(messages):
        if msg.id == product_msg.id:
            found_start = True
            continue
        if found_start:
            if msg.message and msg.message.strip(): break # وقف لو لقيت رسالة نصية جديدة
            if msg.media: image_messages.append(msg)

    os.makedirs("downloads", exist_ok=True)
    downloaded = []
    
    for msg in image_messages:
        filename = await client.download_media(msg, file=f"downloads/{msg.id}")
        if filename and filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            downloaded.append(filename)

    price = extract_price(product_msg.message)
    product_code = extract_product_code(product_msg.message)
    description = re.sub(r"السعر.*", "", product_msg.message, flags=re.IGNORECASE).strip()

    product_data = {
        "product_id": product_msg.id,
        "product_code": product_code,
        "price": price,
        "description": description,
        "images": downloaded
    }

    with open("product.json", "w", encoding="utf-8") as f:
        json.dump(product_data, f, ensure_ascii=False, indent=2)
        
    print(f"🎯 تم صيد منتج جديد! كود: {product_code}")

with client:
    client.loop.run_until_complete(main())
