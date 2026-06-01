import os
import re
import json
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]

# قراءة الرمز وتنظيفه من أي مسافات
SESSION_STRING = os.environ.get("TELEGRAM_SESSION", "").strip()

# الدخول بالجلسة ببيانات وهمية لعدم غلق الحساب
client = TelegramClient(
    StringSession(SESSION_STRING), 
    API_ID, 
    API_HASH,
    device_model="Desktop",
    system_version="Windows 10",
    app_version="1.0"
)

IGNORE_WORDS = [
    "السلام عليكم", "تم تحويل", "العمولات", "اوردر", "يمنشن", "منشن", 
    "قاهره", "جيزه", "كل سنه", "كل سنة", "عيد", "العيد", "اجازة", "إجازة", 
    "استئناف العمل", "الشحن", "مكتب", "بداية جديدة", "كل عام وانتم بخير", "كل عام وأنتم بخير"
]

def is_admin_message(text):
    text = text.lower()
    for word in IGNORE_WORDS:
        if word.lower() in text:
            return True
    return False

# ==========================================
# فلاتر الاستخراج الذكية
# ==========================================
def extract_fabric(text):
    match = re.search(r"الخامه\s*👈\s*(.+)", text)
    return match.group(1).strip() if match else ""

def extract_size(text):
    match = re.search(r"المقاس\s*👈\s*(.+)", text)
    return match.group(1).strip() if match else ""

def extract_product_type(text):
    match = re.search(r"الموديل\s*👈\s*(.+)", text)
    return match.group(1).strip() if match else ""

def extract_price(text):
    # تحويل الأرقام العربية (الهندية) إلى إنجليزية لسهولة البحث
    arabic_to_english = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
    text = text.translate(arabic_to_english)
    
    # فلاتر صيد السعر بكل أشكاله الممكنة
    patterns = [
        r"السعر\s*[:\-]?\s*(\d+)",   # السعر 350 أو السعر: 350
        r"سعر\s*القطعه\s*(\d+)",    # سعر القطعه 350
        r"(\d+)\s*ج\.?م",           # 350 ج.م
        r"(\d+)\s*ج",               # 350 ج
        r"(\d+)\s*جنيه"             # 350 جنيه
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return "غير محدد"

def extract_product_code(text):
    arabic_to_english = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
    text = text.translate(arabic_to_english)
    
    lines = text.splitlines()
    for line in reversed(lines):
        line = line.strip()
        # البحث عن أي أرقام في السطر الأخير
        match = re.search(r"(\d{3,})", line)
        if match:
            return f"FS{match.group(1)}"
            
    # لو ملقاش كود، يحط كود افتراضي بدل ما يسيبه فاضي
    import random
    return f"FS{random.randint(100, 999)}"

def clean_description(text):
    # مسح السعر من الوصف عشان الذكاء الاصطناعي ما يتلخبطش
    text = re.sub(r"السعر.*", "", text, flags=re.IGNORECASE)
    # تنظيف المسافات الزائدة
    return " ".join(text.split())

# ==========================================
# الوظيفة الرئيسية
# ==========================================
async def main():
    await client.start()
    channel = await client.get_entity("yasminstoriii")
    messages = await client.get_messages(channel, limit=150)

    product_msg = None

    for msg in messages:
        text = (msg.message or "").strip()
        if not text or is_admin_message(text):
            continue
        product_msg = msg
        break

    if not product_msg:
        print("NO PRODUCT FOUND")
        return

    image_messages = []
    product_index = None

    for i, msg in enumerate(messages):
        if msg.id == product_msg.id:
            product_index = i
            break

    if product_index is None:
        print("PRODUCT INDEX NOT FOUND")
        return

    for i in range(product_index + 1, len(messages)):
        msg = messages[i]
        text = (msg.message or "").strip()
        
        if text:
            break
        if msg.media:
            image_messages.append(msg)

    image_messages.reverse()
    os.makedirs("downloads", exist_ok=True)
    downloaded = []
    ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]

    for msg in image_messages:
        filename = await client.download_media(
            msg,
            file=f"downloads/{msg.id}"
        )

        if not filename:
            continue

        ext = os.path.splitext(filename)[1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            print(f"SKIPPED NON IMAGE: {filename}")
            continue

        downloaded.append(filename)

    if len(downloaded) == 0:
        print("NO IMAGES FOUND")
        return

    price = extract_price(product_msg.message)
    product_code = extract_product_code(product_msg.message)
    description = clean_description(product_msg.message)

    product_data = {
        "product_id": product_msg.id,
        "product_code": product_code,
        "price": price,
        "description": description,
        "images": downloaded
    }
    
    product_summary = {
        "product_code": product_code,
        "product_type": extract_product_type(product_msg.message),
        "fabric": extract_fabric(product_msg.message),
        "size": extract_size(product_msg.message),
        "price": price
    }

    with open("product_summary.json", "w", encoding="utf-8") as f:
        json.dump(product_summary, f, ensure_ascii=False, indent=2)

    with open("product.json", "w", encoding="utf-8") as f:
        json.dump(product_data, f, ensure_ascii=False, indent=2)

    with open("price_db.json", "w", encoding="utf-8") as f:
        json.dump({product_code: price}, f, ensure_ascii=False, indent=2)
       
    print("\n========================")
    print("PRODUCT_ID:", product_msg.id)
    print("PRODUCT_CODE:", product_code)
    print("PRICE:", price)
    print("IMAGES_COUNT:", len(downloaded))
    print("========================\n")

with client:
    client.loop.run_until_complete(main())
