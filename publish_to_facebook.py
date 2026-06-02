import os
import time
import requests
import json
import csv
from datetime import datetime

# 1. التحقق من التخطي
if os.path.exists("skip_flag.txt"):
    exit(0)

PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN")

if not PAGE_ID or not ACCESS_TOKEN:
    print("❌ بيانات الفيسبوك غير موجودة.")
    exit(0)

# ==============================
# دالة نشر فيديو الستوري 
# ==============================
def post_video_story(video_path):
    if not os.path.exists(video_path): 
        return
    print("🚀 جاري نشر الستوري...")
    file_size = str(os.path.getsize(video_path))
    start_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_stories"
    try:
        start_res = requests.post(start_url, data={'upload_phase': 'start', 'access_token': ACCESS_TOKEN, 'file_size': file_size}).json()
        if 'video_id' not in start_res: 
            return
            
        video_id = start_res['video_id']
        upload_url = f"https://rupload.facebook.com/video-upload/v19.0/{video_id}"
        headers = {
            'Authorization': f'OAuth {ACCESS_TOKEN}', 
            'offset': '0', 
            'file_size': file_size, 
            'X-Entity-Length': file_size, 
            'Content-Type': 'application/octet-stream'
        }
        
        with open(video_path, 'rb') as f:
            upload_res = requests.post(upload_url, headers=headers, data=f.read())
            
        if upload_res.status_code == 200:
            requests.post(start_url, data={'upload_phase': 'finish', 'video_id': video_id, 'access_token': ACCESS_TOKEN})
            print("✅ تم نشر الستوري بنجاح.")
    except Exception as e:
        print(f"⚠️ فشل نشر الستوري: {e}")

# ==============================
# دالة نشر فيديو الريلز 
# ==============================
def upload_reel(video_path, description):
    if not os.path.exists(video_path): 
        return
    print("🚀 جاري رفع ونشر الريلز...")
    file_size = str(os.path.getsize(video_path))
    start_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_reels"
    try:
        start_res = requests.post(start_url, data={'upload_phase': 'start', 'access_token': ACCESS_TOKEN, 'file_size': file_size}).json()
        if 'video_id' not in start_res: 
            return
            
        video_id = start_res['video_id']
        upload_url = f"https://rupload.facebook.com/video-upload/v19.0/{video_id}"
        headers = {
            'Authorization': f'OAuth {ACCESS_TOKEN}', 
            'offset': '0', 
            'file_size': file_size, 
            'X-Entity-Length': file_size, 
            'Content-Type': 'application/octet-stream'
        }
        
        with open(video_path, 'rb') as f:
            upload_res = requests.post(upload_url, headers=headers, data=f.read())
            
        if upload_res.status_code == 200:
            requests.post(start_url, data={'upload_phase': 'finish', 'video_id': video_id, 'video_state': 'PUBLISHED', 'description': description, 'access_token': ACCESS_TOKEN})
            print("🎉 تم نشر فيديو الريلز بنجاح.")
    except Exception as e:
        print(f"⚠️ فشل نشر الريلز: {e}")

# ==============================
# التنفيذ الرئيسي (البوست الأساسي + لوحة التحكم)
# ==============================
try:
    with open("product.json", "r", encoding="utf-8") as f: 
        product_data = json.load(f)
    product_id = product_data.get("product_id")
    code = product_data.get("product_code", "")
    price = product_data.get("price", "")
except Exception: 
    product_id = None
    code = ""
    price = ""

try:
    with open("facebook_post_sales.txt", "r", encoding="utf-8") as f: 
        caption = f.read().strip()
except Exception: 
    caption = "كوليكشن جديد متاح الآن."

url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos?access_token={ACCESS_TOKEN}"

try:
    print("🚀 جاري نشر البوست الأساسي...")
    with open("marketing_collage.jpg", "rb") as img:
        response = requests.post(url, data={"caption": caption}, files={"source": ("post.jpg", img, "image/jpeg")})
        
    res_data = response.json()
    if "id" in res_data:
        print("✅ تم نشر البوست الأساسي بنجاح!")
        post_link = f"https://facebook.com/{res_data['id']}"
        
        # 1. تحديث ذاكرة الطابور المركزية
        if product_id:
            try:
                with open("posted_ids.json", "r") as f: 
                    posted_ids = json.load(f)
            except Exception: 
                posted_ids = []
                
            if product_id not in posted_ids:
                posted_ids.append(product_id)
                with open("posted_ids.json", "w") as f: 
                    json.dump(posted_ids[-1000:], f)

        # 2. بناء وتحديث لوحة التحكم (Excel Dashboard CSV)
        dashboard_file = 'dashboard.csv'
        file_exists = os.path.isfile(dashboard_file)
        
        with open(dashboard_file, 'a', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            # إضافة الترويسة إذا كان الملف جديداً
            if not file_exists:
                writer.writerow(['التاريخ والوقت', 'كود الموديل', 'السعر', 'رابط البوست'])
                
            # تسجيل بيانات البوست الحالي
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            writer.writerow([now, code, price, post_link])
            
        print("📊 تم تحديث لوحة التحكم (Dashboard) وتسجيل البيانات.")

        time.sleep(5)
        # رفع فيديو الستوري
        post_video_story("reel_video.mp4")
        
        time.sleep(5)
        # رفع الريلز
        reel_caption = caption + "\n\n#ريلز #أزياء #موضة #Fastyle"
        upload_reel("reel_video.mp4", reel_caption)
    else:
        print(f"❌ خطأ من فيسبوك أثناء نشر البوست الأساسي: {res_data}")
except Exception as e:
    print(f"❌ خطأ غير متوقع في عملية النشر: {e}")
