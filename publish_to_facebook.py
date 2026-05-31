import os
import requests

PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN")

if not PAGE_ID or not ACCESS_TOKEN:
    print("❌ بيانات الفيسبوك غير موجودة. سيتم تخطي النشر.")
    exit(0)

post_file = "facebook_post_sales.txt"
image_file = "marketing_collage.jpg"

if os.path.exists(post_file) and os.path.exists(image_file):
    with open(post_file, "r", encoding="utf-8") as f:
        caption = f.read().strip()

    print("🚀 جاري النشر على الفيسبوك...")
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
    
    payload = {
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }
    
    with open(image_file, "rb") as img:
        files = {"source": img}
        response = requests.post(url, data=payload, files=files)
        
    res_data = response.json()
    if "id" in res_data:
        print(f"✅ تم النشر بنجاح! رقم البوست: {res_data['id']}")
    else:
        print("❌ حدث خطأ أثناء النشر:", res_data)
else:
    print("⚠ الملفات المطلوبة للنشر غير متوفرة.")

