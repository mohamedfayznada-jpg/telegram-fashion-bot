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
IGNORE_WORDS = [
    "السلام عليكم", "العمولات", "اوردر", "يمنشن", "قاهره", 
    "جيزه", "عيد", "اجازة", "استئناف العمل", "شحن", "مصاريف شحن"
]

def is_ignored_msg(text):
    if not text: return True
    text = text.lower()
    for word in IGNORE_WORDS:
        if word.lower() in text: return True
    return False

def extract_price(text):
    # تحويل الأرقام العربية إلى إنجليزية
    text = text.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))
    
    # البحث عن كلمة السعر والتقاط أول رقم بعدها مباشرة (يحل مشكلة "290 فقط" و "400جينه")
    match = re.search(r"السعر.*?(\d+)", text, re.IGNORECASE)
    if match: 
        return match.group(1)
    return "غير محدد"

def extract_product_code(text):
    text = text.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))
    
    # محاولة إيجاد كلمة "كود"
    match = re.search(r"كود.*?(\d+)", text, re.IGNORECASE)
    if match: 
        return f"FS{match.group(1)}"
        
    # إذا لم يكتب "كود"، نأخذ الأرقام الموجودة أسفل البوست (مثل 1808 أو 2211)
    numbers = re.findall(r'\b\d{3,5}\b', text)
    if numbers:
        price = extract_price(text)
        # نأخذ آخر رقم بشرط ألا يكون هو نفسه السعر
        for num in reversed(numbers):
            if num != price: 
                return f"FS{num}"
                
    return f"FS{random.randint(1000, 9999)}"

async def main():
    await client.start()
    channel = await client.get_entity("yasminstoriii")
    # قراءة آخر 300 رسالة لضمان تغطية التراكمات
    messages = await client.get_messages(channel, limit=300)

    try:
        with open("posted_ids.json", "r") as f: 
            posted_ids = json.load(f)
    except: 
        posted_ids = []

    # قلب ترتيب الرسائل (من الأقدم للأحدث) لرفع الطابور بالترتيب الصحيح
    messages.reverse()

    target_text_msg = None
    target_images = []
    temp_image_buffer = []

    for msg in messages:
        # 1. تجميع الصور في السلة المؤقتة
        if msg.photo:
            temp_image_buffer.append(msg)
            
        text = (msg.text or "").strip()
        
        # 2. عندما نجد رسالة نصية
        if text:
            if is_ignored_msg(text):
                continue # رسالة إدمن: نتجاهلها ونكمل تجميع الصور للمنتج الفعلي
            
            # إذا لم يتم نشر هذا المنتج من قبل
            if msg.id not in posted_ids:
                target_text_msg = msg
                # نأخذ كل الصور التي تم تجميعها قبل هذا النص
                target_images = temp_image_buffer.copy()
                break # وجدنا الهدف! نوقف البحث
            else:
                # هذا المنتج نُشر مسبقاً، نفرغ السلة لنبدأ تجميع صور المنتج الذي يليه
                temp_image_buffer = []

    # لو لفينا على كل الرسائل ومفيش جديد
    if not target_text_msg:
        print("✅ جميع المنتجات تم نشرها، لا يوجد جديد في الطابور.")
        with open("skip_flag.txt", "w", encoding="utf-8") as f: 
            f.write("skip")
        return

    # تنزيل الصور المرتبطة بالمنتج
    os.makedirs("downloads", exist_ok=True)
    downloaded = []
    for img_msg in target_images:
        filename = await client.download_media(img_msg, file=f"downloads/{img_msg.id}")
        if filename: 
            downloaded.append(filename)

    # حماية: لو النص ملوش صور، نرفعه في الذاكرة عشان ميعلقش الطابور ونتخطاه
    if not downloaded:
        print("⚠️ تم العثور على وصف بدون صور، سيتم تخطيه لتجنب الأخطاء.")
        posted_ids.append(target_text_msg.id)
        with open("posted_ids.json", "w") as f: json.dump(posted_ids[-1000:], f)
        with open("skip_flag.txt", "w") as f: f.write("skip")
        return

    # استخراج البيانات
    price = extract_price(target_text_msg.text)
    code = extract_product_code(target_text_msg.text)
    
    # مسح السطر الذي يحتوي على السعر من الوصف
    desc = re.sub(r"السعر.*", "", target_text_msg.text, flags=re.IGNORECASE).strip()

    product_data = {
        "product_id": target_text_msg.id,
        "product_code": code,
        "price": price,
        "description": desc,
        "images": downloaded
    }
    
    with open("product.json", "w", encoding="utf-8") as f: 
        json.dump(product_data, f, ensure_ascii=False, indent=4)
    
    # تحديث الذاكرة فوراً لضمان عدم التكرار
    posted_ids.append(target_text_msg.id)
    with open("posted_ids.json", "w") as f: 
        json.dump(posted_ids[-1000:], f)

    print(f"🎯 تم صيد المنتج بنجاح! الكود: {code} | السعر: {price} | عدد الصور: {len(downloaded)}")

with client:
    client.loop.run_until_complete(main())
