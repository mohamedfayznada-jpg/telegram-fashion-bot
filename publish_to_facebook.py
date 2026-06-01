import os
import requests
from PIL import Image

PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")[cite: 8]
ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN")[cite: 8]

if not PAGE_ID or not ACCESS_TOKEN:[cite: 8]
    print("❌ بيانات الفيسبوك غير موجودة. سيتم تخطي النشر.")[cite: 8]
    exit(0)[cite: 8]

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
        
        # وضع اللوجو في الزاوية اليمنى السفلية (عكس ختم مُحَمَّد فَايِز)
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

def post_story(image_path):[cite: 8]
    if not os.path.exists(image_path):[cite: 8]
        print("⚠️ صورة الستوري غير موجودة.")[cite: 8]
        return[cite: 8]
        
    print("🚀 جاري نشر الستوري...")[cite: 8]
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photo_stories"[cite: 8]
    payload = {"access_token": ACCESS_TOKEN}[cite: 8]
    
    with open(image_path, "rb") as img:[cite: 8]
        files = {"source": img}[cite: 8]
        response = requests.post(url, data=payload, files=files)[cite: 8]
        
    res_data = response.json()[cite: 8]
    if "id" in res_data:[cite: 8]
        print(f"✅ تم نشر الستوري بنجاح! رقم الستوري: {res_data['id']}")[cite: 8]
    else:[cite: 8]
        print(f"❌ حدث خطأ أثناء نشر الستوري: {res_data}")[cite: 8]

# ==============================
# التنفيذ الرئيسي
# ==============================
post_file = "facebook_post_sales.txt"[cite: 8]
image_file = "marketing_collage.jpg"[cite: 8]
story_image = "cover_image.jpg"[cite: 8] 

if os.path.exists(post_file) and os.path.exists(image_file):[cite: 8]
    with open(post_file, "r", encoding="utf-8") as f:[cite: 8]
        caption = f.read().strip()[cite: 8]
        
    print("🎨 جاري وضع لوجو Fastyle...")
    final_image_to_post = add_clean_watermark(image_file)

    print("🚀 جاري النشر على الفيسبوك (البوست الأساسي)...")[cite: 8]
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"[cite: 8]
    
    payload = {[cite: 8]
        "caption": caption,[cite: 8]
        "access_token": ACCESS_TOKEN[cite: 8]
    }[cite: 8]
    
    with open(final_image_to_post, "rb") as img:[cite: 8]
        files = {"source": img}[cite: 8]
        response = requests.post(url, data=payload, files=files)[cite: 8]
        
    res_data = response.json()[cite: 8]
    if "id" in res_data:[cite: 8]
        print(f"✅ تم نشر البوست بنجاح! رقم البوست: {res_data['id']}")[cite: 8]
        
        # استدعاء دالة نشر الستوري
        post_story(story_image)[cite: 8]
        
    else:[cite: 8]
        print("❌ حدث خطأ أثناء النشر:", res_data)[cite: 8]
else:[cite: 8]
    print("⚠ الملفات المطلوبة للنشر غير متوفرة.")[cite: 8]
