import os
import re
import json
import asyncio
import requests
from telethon.sync import TelegramClient
from PIL import Image

# ==========================================
# 1. قراءة المتغيرات من GitHub Secrets
# ==========================================
API_ID = int(os.environ.get('TG_API_ID', 0))
API_HASH = os.environ.get('TG_API_HASH', '')
CHANNEL_USERNAME = os.environ.get('TG_CHANNEL', '') # مثلا: @fastyle_channel
FB_PAGE_ID = os.environ.get('FACEBOOK_PAGE_ID', '')
FB_ACCESS_TOKEN = os.environ.get('FACEBOOK_ACCESS_TOKEN', '')

LOGO_PATH = 'logo.png' # تأكد إن اللوجو موجود في جيتهاب
STATE_FILE = 'last_message_id.txt'
PRICES_DB = 'prices.json'

# ==========================================
# 2. إضافة اللوجو (في الزاوية اليسرى السفلية)
# ==========================================
def add_watermark(image_path, output_path):
    try:
        base_image = Image.open(image_path).convert("RGBA")
        logo = Image.open(LOGO_PATH).convert("RGBA")
        
        # تصغير اللوجو ليكون 15% من عرض الصورة
        logo_width = int(base_image.width * 0.15)
        w_percent = (logo_width / float(logo.width))
        logo_height = int((float(logo.height) * float(w_percent)))
        logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
        
        # ضبط الإحداثيات للزاوية اليسرى السفلية
        margin = 20
        x = margin
        y = base_image.height - logo_height - margin
        
        transparent = Image.new('RGBA', base_image.size, (0,0,0,0))
        transparent.paste(logo, (x, y), mask=logo)
        watermarked_image = Image.alpha_composite(base_image, transparent)
        
        watermarked_image.convert("RGB").save(output_path, "JPEG")
        return output_path
    except Exception as e:
        print(f"❌ خطأ في دمج اللوجو: {e}")
        return image_path

# ==========================================
# 3. معالجة النص واستخراج الداتا
# ==========================================
def process_data(raw_text):
    # استخراج كود الصنف (حروف إنجليزي تليها أرقام) والسعر
    code_match = re.search(r'([a-zA-Z]+\d+)', raw_text)
    price_match = re.search(r'(\d{3,4})', raw_text)
    
    item_code = code_match.group(1).upper() if code_match else None
    price = price_match.group(1) if price_match else None
    
    # تحديث قاعدة بيانات الأسعار (JSON)
    if item_code and price:
        prices_data = {}
        if os.path.exists(PRICES_DB):
            with open(PRICES_DB, 'r', encoding='utf-8') as f:
                try: prices_data = json.load(f)
                except: pass
        
        prices_data[item_code] = price
        with open(PRICES_DB, 'w', encoding='utf-8') as f:
            json.dump(prices_data, f, ensure_ascii=False, indent=4)
            
    # تنظيف النص لفيسبوك
    clean_text = raw_text
    if item_code: clean_text = clean_text.replace(item_code, '')
    if price: clean_text = clean_text.replace(price, '')
    
    # صياغة تسويقية جديدة وفصل الكود في النهاية
    fb_text = (
        f"✨ كوليكشن جديد لأجمل إطلالة! ✨\n\n"
        f"{clean_text.strip()}\n\n"
        f"خامة ممتازة وجودة تعيش معاكي.. اطلبيه دلوقتي! 🛒❤️\n"
        f"للاستفسار أو الحجز ابعتيلنا رسالة 📩\n"
        f"---------------------------\n"
        f"📌 كود الموديل: {item_code if item_code else 'غير متوفر'}"
    )
    return fb_text

# ==========================================
# 4. النشر على فيسبوك
# ==========================================
def post_to_facebook(image_path, message):
    url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photos"
    payload = {'message': message, 'access_token': FB_ACCESS_TOKEN}
    with open(image_path, 'rb') as img:
        files = {'source': img}
        response = requests.post(url, data=payload, files=files)
    return response.json()

# ==========================================
# 5. تشغيل النظام وجلب الجديد فقط
# ==========================================
async def main():
    # قراءة آخر رسالة تم سحبها
    last_id = 0
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            last_id = int(f.read().strip() or 0)

    # استخدام ملف الجلسة للاتصال
    client = TelegramClient('fastyle_session', API_ID, API_HASH)
    await client.start()
    
    print(f"🔍 جاري البحث عن رسائل جديدة بعد ID: {last_id}")
    
    # جلب الرسائل من الأقدم للأحدث (عشان النشر يكون بالترتيب)
    messages = await client.get_messages(CHANNEL_USERNAME, min_id=last_id, limit=10)
    messages.reverse() 
    
    for msg in messages:
        if msg.media and msg.text:
            print(f"⏳ جاري معالجة رسالة ID: {msg.id}")
            
            # تحميل ومعالجة
            img_path = await msg.download_media('temp.jpg')
            fb_text = process_data(msg.text)
            watermarked = add_watermark(img_path, 'ready.jpg')
            
            # النشر
            res = post_to_facebook(watermarked, fb_text)
            if 'id' in res:
                print(f"✅ تم النشر! Post ID: {res['id']}")
            
            # تحديث الـ ID
            last_id = msg.id
            with open(STATE_FILE, 'w') as f:
                f.write(str(last_id))
                
            # تنظيف
            os.remove(img_path)
            if os.path.exists('ready.jpg'): os.remove('ready.jpg')

if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
