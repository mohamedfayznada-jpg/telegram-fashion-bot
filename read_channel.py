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
    text = text.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))
    
    # فلتر خارق: يبحث عن كلمة السعر، ثم يتخطى أي إيموجي أو مسافات أو أسطر، ويجلب الرقم
    match = re.search(r"(السعر|سعر)[\s\S]*?(\d{3,4})", text, re.IGNORECASE)
    if match: 
        return match.group(2)
        
    # خطة بديلة لو لم يكتب كلمة السعر أصلاً
    numbers = re.findall(r'\b\d{3,4}\b', text)
    return numbers[-1] if numbers else "غير محدد"

def extract_product_code(text):
    text = text.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))
    
    match = re.search(r"كود[\s\S]*?(\d+)", text, re.IGNORECASE)
    if match: 
        return f"FS{match.group(1)}"
        
    numbers = re.findall(r'\b\d{3,5}\b', text)
    if numbers:
        price = extract_price(text)
        for num in reversed(numbers):
            if num != price: 
                return f"FS{num}"
                
    return f"FS{random.randint(1000, 9999)}"

async def main():
    await client.start()
    channel = await client.get_entity("yasminstoriii")
    
    # قللنا البحث لـ 40 رسالة فقط للتركيز على "أحدث المنتجات" وعدم جلب القديم
    messages = await client.get_messages(channel, limit=40)

    try:
        with open("posted_ids.json", "r") as f: 
            posted_ids = json.load(f)
    except: 
        posted_ids = []

    messages.reverse() # من الأقدم للأحدث داخل النطاق القصير

    target_text_msg = None
    target_images = []
    temp_image_buffer = []

    for msg in messages:
        if msg.photo:
            temp_image_buffer.append(msg)
            
        text = (msg.text or "").strip()
        
        if text:
            if is_ignored_msg(text):
                continue
            
            if msg.id not in posted_ids:
                target_text_msg = msg
                target_images = temp_image_buffer.copy()
                break
            else:
                temp_image_buffer = []

    if not target_text_msg:
        print("✅ جميع المنتجات الحديثة تم نشرها، لا يوجد جديد.")
        with open("skip_flag.txt", "w", encoding="utf-8") as f: 
            f.write("skip")
        return

    os.makedirs("downloads", exist_ok=True)
    downloaded = []
    for img_msg in target_images:
        filename = await client.download_media(img_msg, file=f"downloads/{img_msg.id}")
        if filename: 
            downloaded.append(filename)

    if not downloaded:
        print("⚠️ وصف بدون صور، سيتم تخطيه.")
        posted_ids.append(target_text_msg.id)
        with open("posted_ids.json", "w") as f: json.dump(posted_ids[-1000:], f)
        with open("skip_flag.txt", "w") as f: f.write("skip")
        return

    price = extract_price(target_text_msg.text)
    code = extract_product_code(target_text_msg.text)
    desc = re.sub(r"(السعر|سعر)[\s\S]*", "", target_text_msg.text, flags=re.IGNORECASE).strip()

    product_data = {
        "product_id": target_text_msg.id,
        "product_code": code,
        "price": price,
        "description": desc,
        "images": downloaded
    }
    
    with open("product.json", "w", encoding="utf-8") as f: 
        json.dump(product_data, f, ensure_ascii=False, indent=4)
    
    posted_ids.append(target_text_msg.id)
    with open("posted_ids.json", "w") as f: 
        json.dump(posted_ids[-1000:], f)

    print(f"🎯 تم صيد المنتج بنجاح! الكود: {code} | السعر: {price}")

with client:
    client.loop.run_until_complete(main())
