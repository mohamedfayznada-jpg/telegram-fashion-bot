import os
import requests
from PIL import Image

PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN")

if not PAGE_ID or not ACCESS_TOKEN:
    print("❌ بيانات الفيسبوك غير موجودة. سيتم تخطي النشر.")
    exit(0)

def add_clean_watermark(image_path, logo_path="logo.png"):
    try:
        base_image = Image.open(image_path).convert("RGBA")
        
        if not os.path.exists(logo_path):
            print("⚠️ ملف اللوجو غير موجود، سيتم النشر بدون لوجو إضافي.")
            return image_path
            
        logo = Image.open(logo_path).convert("RGBA")
        
        # تصغير اللوجو ليكون 15% من العرض
        logo_width = int(base_image.width * 0.15)
        w_percent = (logo_width / float(logo.width))
        logo_height = int((float(logo.height) * float(w_percent)))
        logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
        
        # وضع اللوجو في الزاوية اليمنى السفلية
        margin = 30
        x = base_image.width - logo_width - margin
        y = base_image.height - logo_height - margin
        
        # لصق اللوجو مباشرة
        transparent = Image.new('RGBA', base_image.size, (0,0,0,0))
        transparent.paste(logo, (x, y), mask=logo)
        final_image = Image.alpha_composite(base_image, transparent)
        
        output_path = "watermarked_collage.jpg"
        final_image.convert("RGB").save(output_path, "JPEG", quality=95)
        return output_path
    except Exception as e:
        print(f"❌ خطأ في إضافة اللوجو: {e}")
        return image_path

def post_story(image_path):
    if not os.path.exists(image_path):
        print("⚠️ صورة الستوري غير موجودة.")
        return
        
    print("🚀 جاري نشر الستوري...")
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photo_stories"
    payload = {"access_token": ACCESS_TOKEN}
    
    with open(image_path, "rb") as img:
        files = {"source": img}
        response = requests.post(url, data=payload, files=files)
        
    res_data = response.json()
    if "id" in res_data:
        print(f"✅ تم نشر الستوري بنجاح! رقم الستوري: {res_data['id']}")
    else:
        print(f"❌ حدث خطأ أثناء نشر الستوري: {res_data}")

# ==============================
# التنفيذ الرئيسي
# ==============================
post_file = "facebook_post_sales.txt"
image_file = "marketing_collage.jpg"
story_image = "cover_image.jpg" 

if os.path.exists(post_file) and os.path.exists(image_file):
    with open(post_file, "r", encoding="utf-8") as f:
        caption = f.read().strip()
        
    print("🎨 جاري وضع لوجو Fastyle...")
    final_image_to_post = add_clean_watermark(image_file)

    print("🚀 جاري النشر على الفيسبوك (البوست الأساسي)...")
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
    
    payload = {
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }
    
    with open(final_image_to_post, "rb") as img:
        files = {"source": img}
        response = requests.post(url, data=payload, files=files)
        
    res_data = response.json()
    if "id" in res_data:
        print(f"✅ تم نشر البوست بنجاح! رقم البوست: {res_data['id']}")
        
        # استدعاء دالة نشر الستوري
        post_story(story_image)
        
    else:
        print("❌ حدث خطأ أثناء النشر:", res_data)
else:
    print("⚠ الملفات المطلوبة للنشر غير متوفرة.")
