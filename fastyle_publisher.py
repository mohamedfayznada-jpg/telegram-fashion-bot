import os
import re
import json
import asyncio
import requests
from telethon.sync import TelegramClient
from telethon import events
from PIL import Image, ImageDraw

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

# تعريف العميل قبل الـ decorators لضمان عملها بشكل سليم
client = TelegramClient('fastyle_session', API_ID, API_HASH)

# ==========================================
# دالة الرد على استعلام الأسعار
# ==========================================
@client.on(events.NewMessage(pattern=r'(?i)^(سعر|بكام)\s+([A-Za-z]+\d+)'))
async def price_query_handler(event):
    word = event.pattern_match.group(1)
    item_code = event.pattern_match.group(2).upper()
    
    print(f"🔍 استعلام جديد عن سعر الكود: {item_code}")
    
    try:
        with open('prices.json', 'r', encoding='utf-8') as f:
            prices_db = json.load(f)
            
        if item_code in prices_db:
            price = prices_db[item_code]
            reply_msg = f"👗 الموديل كود {item_code}\n💰 السعر المتسجل: {price} جنيه"
        else:
            reply_msg = f"⚠️ الكود {item_code} مش متسجل في قاعدة البيانات حالياً."
            
    except FileNotFoundError:
        reply_msg = "❌ ملف الأسعار مش موجود لسه (لم يتم سحب منتجات حتى الآن)."
        
    await event.reply(reply_msg)

# ==========================================
# 2. إضافة اللوجو (مع إخفاء أي نصوص مقلوبة)
# ==========================================
def add_watermark(image_path, output_path):
    try:
        base_image = Image.open(image_path).convert("RGBA")
        
        # رسم مربع أسود شفاف لتغطية النصوص القديمة
        draw = ImageDraw.Draw(base_image)
        margin = 15
        draw.rectangle(
            [0, base_image.height - 90, 170, base_image.height],
            fill=(0, 0, 0, 180)
        )
        
        if os.path.exists(LOGO_PATH):
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo_width = int(base_image.width * 0.15)
            w_percent = (logo_width / float(logo.width))
            logo_height = int((float(logo.height) * float(w_percent)))
            logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
            
            x = margin
            y = base_image.height - logo_height - margin
            
            transparent = Image.new('RGBA', base_image.size, (0,0,0,0))
            transparent.paste(logo, (x, y), mask=logo)
            final_image = Image.alpha_composite(base_image, transparent)
        else:
            final_image = base_image

        final_image.convert("RGB").save(output_path, "JPEG", quality=95)
        return output_path
    except Exception as e:
        print(f"❌ خطأ في دمج اللوجو: {e}")
        return image_path

# ==========================================
# 3. معالجة النص واستخراج الداتا
# ==========================================
def process_data(raw_text):
    code_match = re.search(r'([a-zA-Z]+\d+)', raw_text)
    price_match = re.search(r'(\d{3,4})', raw_text)
    
    item_code = code_match.group(1).upper() if code_match else None
    price = price_match.group(1) if price_match else None
    
    if item_code and price:
        prices_data = {}
        if os.path.exists(PRICES_DB):
            with open(PRICES_DB, 'r', encoding='utf-8') as f:
                try: prices_data = json.load(f)
                except: pass
        
        prices_data[item_code] = price
        with open(PRICES_DB, 'w', encoding='utf-8') as f:
            json.dump(prices_data, f, ensure_ascii=False, indent=4)
            
    clean_text = raw_text
    if item_code: clean_text = clean_text.replace(item_code, '')
    if price: clean_text = clean_text.replace(price, '')
    
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
# 4. النشر على فيسبوك (البوست + الستوري)
# ==========================================
def post_to_facebook(image_path, message):
    # نشر البوست
    url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photos"
    payload = {'message': message, 'access_token': FB_ACCESS_TOKEN}
    with open(image_path, 'rb') as img:
        files = {'source': img}
        response = requests.post(url, data=payload, files=files)
        
    res_data = response.json()
    
    # إذا نجح البوست، انشر ستوري بنفس الصورة
    if 'id' in res_data:
        print(f"✅ تم نشر البوست! Post ID: {res_data['id']}")
        
        story_url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photo_stories"
        story_payload = {'access_token': FB_ACCESS_TOKEN}
        with open(image_path, 'rb') as story_img:
            story_files = {'source': story_img}
            story_res = requests.post(story_url, data=story_payload, files=story_files)
            if 'id' in story_res.json():
                print("✅ تم نشر الستوري بنجاح!")
            else:
                print(f"❌ خطأ في نشر الستوري: {story_res.json()}")
                
    return res_data

# ==========================================
# 5. تشغيل النظام وجلب الجديد فقط
# ==========================================
async def main():
    last_id = 0
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            last_id = int(f.read().strip() or 0)

    await client.start()
    
    print(f"🔍 جاري البحث عن رسائل جديدة بعد ID: {last_id}")
    
    messages = await client.get_messages(CHANNEL_USERNAME, min_id=last_id, limit=10)
    messages.reverse() 
    
    for msg in messages:
        if msg.media and msg.text:
            print(f"⏳ جاري معالجة رسالة ID: {msg.id}")
            
            img_path = await msg.download_media('temp.jpg')
            fb_text = process_data(msg.text)
            watermarked = add_watermark(img_path, 'ready.jpg')
            
            res = post_to_facebook(watermarked, fb_text)
            
            last_id = msg.id
            with open(STATE_FILE, 'w') as f:
                f.write(str(last_id))
                
            os.remove(img_path)
            if os.path.exists('ready.jpg'): os.remove('ready.jpg')

if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
