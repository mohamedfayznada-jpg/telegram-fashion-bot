import os
import re
import json
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ.get("TELEGRAM_SESSION", "").strip()

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# كلمات الإدمن اللي البوت هيتجاهلها تماماً
IGNORE_WORDS = ["السلام عليكم", "العمولات", "اوردر", "يمنشن", "قاهره", "جيزه", "عيد", "اجازة", "استئناف العمل", "شحن", "كل سنة"]

def is_ignored_msg(text):
    if not text: return True  # لو مفيش نص نعتبرها رسالة تابعة للألبوم ونتخطاها مؤقتاً
    for word in IGNORE_WORDS:
        if word.lower() in text.lower(): return True
    return False

def extract_price(text):
    text = text.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))
    patterns = [r"السعر\s*[:\-]?\s*(\d+)", r"(\d+)\s*ج\b", r"(\d+)\s*جنيه"]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match: return match.group(1)
    
    # صيد آخر رقم مكون من 3 أو 4 خانات (سعر التاجر)
    numbers = re.findall(r'\b\d{3,4}\b', text)
    return numbers[-1] if numbers else "غير محدد"

def extract_product_code(text):
    import random
    text = text.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))
    for line in reversed(text.splitlines()):
        match = re.search(r"(\d{3,})", line.strip())
        if match: return f"FS{match.group(1)}"
    return f"FS{random.randint(1000, 9999)}"

async def main():
    await client.start()
    
    # ⚠️ تنبيه: تأكد من اسم القناة هنا ⚠️
    channel = await client.get_entity("yasminstoriii") 
    
    # قراءة أحدث 50 رسالة فقط من الأحدث للأقدم
    messages = await client.get_messages(channel, limit=50) 

    try:
        with open("posted_ids.json", "r") as f: posted_ids = json.load(f)
    except: posted_ids = []

    product_msg = None
    
    # 1. البحث عن أحدث منتج (أول رسالة تقابلنا فيها نص وصورة ومش في الذاكرة)
    for msg in messages:
        if msg.id in posted_ids: 
            continue
            
        text = (msg.message or "").strip()
        
        if msg.media and not is_ignored_msg(text):
            product_msg = msg
            break
        else:
            # لو رسالة إدمن أو صورة بدون نص، نسجلها إنها "اتقرأت" عشان ننساها
            if msg.id not in posted_ids:
                posted_ids.append(msg.id)

    if not product_msg:
        print("✅ لا توجد منتجات جديدة (تم معالجة كل الأحدث).")
        with open("skip_flag.txt", "w") as f: f.write("skip")
        with open("posted_ids.json", "w") as f: json.dump(posted_ids[-1000:], f)
        return

    print(f"🎯 تم صيد أحدث منتج نزل على القناة! ID: {product_msg.id}")

    # 2. تجميع كل صور الألبوم بناءً على الـ Group ID
    downloaded = []
    os.makedirs("downloads", exist_ok=True)
    
    if product_msg.grouped_id:
        # لو ده ألبوم، هنجيب كل صوره حتى لو معلهاش كلام
        for m in messages:
            if m.grouped_id == product_msg.grouped_id:
                if m.id not in posted_ids: posted_ids.append(m.id)
                if m.media:
                    file = await client.download_media(m, file=f"downloads/{m.id}")
                    if file: downloaded.append(file)
    else:
        # لو صورة واحدة بس
        posted_ids.append(product_msg.id)
        file = await client.download_media(product_msg, file=f"downloads/{product_msg.id}")
        if file: downloaded.append(file)

    # حفظ الذاكرة
    with open("posted_ids.json", "w") as f: json.dump(posted_ids[-1000:], f)

    # حفظ بيانات المنتج النهائية
    product_data = {
        "product_id": product_msg.id,
        "product_code": extract_product_code(product_msg.message),
        "price": extract_price(product_msg.message),
        "description": re.sub(r"السعر.*", "", product_msg.message, flags=re.IGNORECASE).strip(),
        "images": downloaded
    }
    
    with open("product.json", "w", encoding="utf-8") as f: 
        json.dump(product_data, f, ensure_ascii=False, indent=4)
        
    print(f"✅ تم حفظ أحدث منتج بنجاح. تم تجميع {len(downloaded)} صور.")

with client:
    client.loop.run_until_complete(main())
