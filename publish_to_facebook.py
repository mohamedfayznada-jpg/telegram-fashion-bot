import os
import requests

PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN")

if not PAGE_ID or not ACCESS_TOKEN:
    print("❌ بيانات الفيسبوك غير موجودة. سيتم تخطي النشر.")
    exit(0)

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
# الصورة هنا بقت اللي طالعة جاهزة من كود معالجة الصور
image_file = "marketing_collage.jpg" 
story_image = "cover_image.jpg" 

if os.path.exists(post_file) and os.path.exists(image_file):
    with open(post_file, "r", encoding="utf-8") as f:
        caption = f.read().strip()

    print("🚀 جاري النشر على الفيسبوك (البوست الأساسي)...")
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
    
    payload = {
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }
    
    # هنرفع الصورة مباشرة بدون أي تعديلات إضافية
    with open(image_file, "rb") as img:
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
