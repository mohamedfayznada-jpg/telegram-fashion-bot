import os
import re
import json
import asyncio
import requests
from telethon import TelegramClient, events
from PIL import Image

# ==========================================
# إعدادات النظام (املأ بياناتك هنا)
# ==========================================
# 1. إعدادات تيلجرام (من my.telegram.org)
API_ID = 'رقم_الـ_API_بتاعك'
API_HASH = 'الـ_HASH_بتاعك'
CHANNEL_USERNAME = 'يوزر_قناة_تيلجرام_مثلا_@mychannel'

# 2. إعدادات فيسبوك
FB_PAGE_ID = '204833249369688'
FB_ACCESS_TOKEN = 'التوكن_الدائم_اللي_استخرجناه'

# 3. إعدادات الملفات
LOGO_PATH = 'logo.png' # مسار اللوجو بتاعك (يُفضل يكون PNG بخلفية شفافة)
PRICES_DB = 'prices.json' # الملف اللي هيتحفظ فيه الأكواد والأسعار للبوت

# تهيئة عميل تيلجرام
client = TelegramClient('fastyle_session', API_ID, API_HASH)

# ==========================================
# دالة 1: إضافة اللوجو على الصورة
# ==========================================
def add_watermark(image_path, output_path):
    try:
        # فتح الصورة الأساسية واللوجو
        base_image = Image.open(image_path).convert("RGBA")
        logo = Image.open(LOGO_PATH).convert("RGBA")
        
        # تصغير اللوجو ليكون متناسق (مثلا 20% من عرض الصورة)
        logo_width = int(base_image.width * 0.2)
        w_percent = (logo_width / float(logo.width))
        logo_height = int((float(logo.height) * float(w_percent)))
        logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
        
        # وضع اللوجو في الزاوية اليسرى السفلية
        margin = 20
        x = margin
        y = base_image.height - logo_height - margin
        
        # دمج اللوجو مع الصورة
        transparent = Image.new('RGBA', base_image.size, (0,0,0,0))
        transparent.paste(logo, (x, y), mask=logo)
        watermarked_image = Image.alpha_composite(base_image, transparent)
        
        # حفظ الصورة النهائية
        watermarked_image.convert("RGB").save(output_path, "JPEG")
        return output_path
    except Exception as e:
        print(f"❌ خطأ في إضافة اللوجو: {e}")
        return image_path # لو حصل خطأ يرجع الصورة الأصلية

# ==========================================
# دالة 2: معالجة النص واستخراج السعر والكود
# ==========================================
def process_text_and_save_price(raw_text):
    # البحث عن كود الصنف (مثال: FS816) والسعر (أرقام)
    # يمكنك تعديل الـ Regex حسب طريقة كتابتك في تيلجرام
    code_match = re.search(r'([a-zA-Z]+\d+)', raw_text)
    price_match = re.search(r'(\d{3,4})', raw_text)
    
    item_code = code_match.group(1).upper() if code_match else "غير_محدد"
    price = price_match.group(1) if price_match else "غير_محدد"
    
    # حفظ الكود والسعر في قاعدة بيانات البوت (JSON)
    if item_code != "غير_محدد" and price != "غير_محدد":
        prices_data = {}
        if os.path.exists(PRICES_DB):
            with open(PRICES_DB, 'r', encoding='utf-8') as f:
                prices_data = json.load(f)
                
        prices_data[item_code] = price
        
        with open(PRICES_DB, 'w', encoding='utf-8') as f:
            json.dump(prices_data, f, ensure_ascii=False, indent=4)
            
    # تنظيف النص لصياغة بوست فيسبوك (إزالة السعر والكود من وسط الكلام)
    clean_text = raw_text.replace(item_code, '').replace(price, '')
    
    # الصياغة النهائية للبوست
    fb_post_text = (
        f"✨ استعدي لأجمل إطلالة! ✨\n\n"
        f"{clean_text.strip()}\n\n"
        f"خامة ممتازة وجودة تعيش معاكي.. اطلبيه دلوقتي عشان متفوتيش الفرصة! 🛒❤️\n\n"
        f"للاستفسار أو الحجز ابعتيلنا رسالة 📩\n"
        f"---------------------------\n"
        f"📌 كود الموديل: {item_code}"
    )
    
    return fb_post_text

# ==========================================
# دالة 3: النشر على فيسبوك
# ==========================================
def post_to_facebook(image_path, message):
    url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photos"
    payload = {
        'message': message,
        'access_token': FB_ACCESS_TOKEN
    }
    
    with open(image_path, 'rb') as img:
        files = {'source': img}
        response = requests.post(url, data=payload, files=files)
        
    result = response.json()
    if 'id' in result:
        print(f"✅ تم النشر على فيسبوك بنجاح! ID البوست: {result['id']}")
    else:
        print(f"❌ خطأ في النشر: {result}")

# ==========================================
# المستمع اللحظي (Listener) لقناة تيلجرام
# ==========================================
@client.on(events.NewMessage(chats=CHANNEL_USERNAME))
async def handle_new_message(event):
    print("🔔 رسالة جديدة وصلت من تيلجرام!")
    
    if event.message.media and event.message.text:
        # 1. تحميل الصورة من تيلجرام
        print("⏳ جاري تحميل الصورة...")
        download_path = await event.message.download_media('temp_image.jpg')
        
        # 2. معالجة النص وحفظ السعر
        print("⏳ جاري معالجة النص...")
        fb_text = process_text_and_save_price(event.message.text)
        
        # 3. إضافة اللوجو
        print("⏳ جاري إضافة اللوجو...")
        watermarked_path = add_watermark(download_path, 'ready_to_post.jpg')
        
        # 4. النشر على فيسبوك
        print("⏳ جاري النشر على فيسبوك...")
        post_to_facebook(watermarked_path, fb_text)
        
        # تنظيف الملفات المؤقتة
        if os.path.exists(download_path): os.remove(download_path)
        if os.path.exists(watermarked_path): os.remove(watermarked_path)
        
    else:
        print("⚠️ الرسالة لا تحتوي على صورة أو نص، تم التخطي.")

# ==========================================
# تشغيل النظام
# ==========================================
if __name__ == '__main__':
    print("🚀 النظام يعمل الآن ويراقب قناة تيلجرام...")
    client.start()
    client.run_until_disconnected()
