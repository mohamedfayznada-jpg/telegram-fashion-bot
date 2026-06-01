import os
import re
import json
import random
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ.get("TELEGRAM_SESSION", "").strip()

client = TelegramClient(
    StringSession(SESSION_STRING), 
    API_ID, 
    API_HASH, 
    device_model="Desktop", 
    system_version="Windows 10", 
    app_version="1.0"
)

# كلمات الإدمن/الرسائل العامة للتجاهل
IGNORE_WORDS = ["السلام عليكم", "العمولات", "اوردر", "يمنشن", "قاهره", "جيزه", "عيد", "اجازة", "استئناف العمل", "شحن"]

def is_ignored_msg(text):
    if not text: return True
    text = text.lower()
    for word in IGNORE_WORDS:
        if word.lower() in text: return True
    return False

def extract_price(text):
    text = text.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))
    patterns = [r"السعر\s*[:\-]?\s*(\d+)", r"(\d+)\s*ج\b", r"(\d+)\s*جنيه"]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match: return match.group(1)
    # البحث عن أي رقم 3 أو 4 خانات في آخر البوست
    numbers = re.findall(r'\b\d{3,4}\b', text)
    return numbers[-1] if numbers else "غير محدد"

def extract_product_code(text):
    text = text.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))
    for line in reversed(text.splitlines()):
        match = re.search(r"(\d{3,})", line.strip())
        if match: return f"FS{match.group(1)}"
    return f"FS{random.randint(100, 999)}"

async def main():
    await client.start()
    channel = await client.get_entity("yasminstoriii")
    # زيادة العدد لـ 200 لضمان تغطية كل اللي فات
    messages = await client.get_messages(channel, limit=200)

    try:
        with open("posted_ids.json", "r") as f: posted_ids = json.load(f)
    except: posted_ids = []

    product_msg = None
    
    # البحث من الأقدم للأحدث (عشان نرفع القديم الأول)
    for msg in reversed(messages):
        # 1. نتجاهل الرسائل اللي اترفت قبل كده
        if msg.id in posted_ids: continue
            
        text = (msg.message or "").strip()
        
        # 2. نتجاهل رسائل الإدمن بدون ما نوقف البحث
        if is_ignored_msg(text) or not msg.media:
            # نسجل الـ ID ده في الذاكرة عشان مايراجعوش تاني
            posted_ids.append(msg.id)
            continue
            
        # لو وصلنا هنا يبقى لقينا منتج حقيقي جديد
        product_msg = msg
        break

    if not product_msg:
        print("✅ كل المنتجات تم معالجتها بالفعل.")
        with open("skip_flag.txt", "w", encoding="utf-8") as f: f.write("skip")
        return

    # حفظ الذاكرة المحدثة
    with open("posted_ids.json", "w") as f: json.dump(posted_ids[-1000:], f)

    print(f"🎯 تم اختيار المنتج الجديد (ID: {product_msg.id})")
    
    # تجميع الصور التابعة للمنتج
    image_messages = []
    # البحث في الرسائل التالية للرسالة الرئيسية
    for msg in messages: # البحث في كل الرسائل
        if msg.reply_to_msg_id == product_msg.id or (msg.date >= product_msg.date and msg.date <= product_msg.date + 1):
             if msg.media: image_messages.append(msg)

    os.makedirs("downloads", exist_ok=True)
    downloaded = []
    for msg in image_messages:
        filename = await client.download_media(msg, file=f"downloads/{msg.id}")
        if filename and filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            downloaded.append(filename)

    # حفظ بيانات المنتج
    product_data = {
        "product_id": product_msg.id,
        "product_code": extract_product_code(product_msg.message),
        "price": extract_price(product_msg.message),
        "description": re.sub(r"السعر.*", "", product_msg.message, flags=re.IGNORECASE).strip(),
        "images": downloaded
    }
    with open("product.json", "w", encoding="utf-8") as f: json.dump(product_data, f, ensure_ascii=False, indent=4)
    print(f"✅ تم حفظ المنتج {product_data['product_code']}.")

with client:
    client.loop.run_until_complete(main())
