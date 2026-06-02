import os
import time
import requests
import json
import csv
from datetime import datetime

if os.path.exists("skip_flag.txt"): exit(0)

PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN")

if not PAGE_ID or not ACCESS_TOKEN: exit(0)

def post_video_story(video_path):
    if not os.path.exists(video_path): 
        print("❌ فيديو الستوري غير موجود!")
        return
    print("🚀 جاري نشر الستوري...")
    file_size = str(os.path.getsize(video_path))
    start_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_stories"
    try:
        start_res = requests.post(start_url, data={'upload_phase': 'start', 'access_token': ACCESS_TOKEN, 'file_size': file_size}).json()
        if 'video_id' not in start_res: return
        video_id = start_res['video_id']
        upload_url = f"https://rupload.facebook.com/video-upload/v19.0/{video_id}"
        headers = {'Authorization': f'OAuth {ACCESS_TOKEN}', 'offset': '0', 'file_size': file_size, 'X-Entity-Length': file_size, 'Content-Type': 'application/octet-stream'}
        with open(video_path, 'rb') as f:
            upload_res = requests.post(upload_url, headers=headers, data=f.read())
        if upload_res.status_code == 200:
            requests.post(start_url, data={'upload_phase': 'finish', 'video_id': video_id, 'access_token': ACCESS_TOKEN})
            print("✅ تم نشر الستوري بنجاح.")
    except Exception as e: print(f"⚠️ فشل الستوري: {e}")

def upload_reel(video_path, description):
    if not os.path.exists(video_path): 
        print("❌ فيديو الريلز غير موجود!")
        return
    print("🚀 جاري رفع ونشر الريلز...")
    file_size = str(os.path.getsize(video_path))
    start_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_reels"
    try:
        start_res = requests.post(start_url, data={'upload_phase': 'start', 'access_token': ACCESS_TOKEN, 'file_size': file_size}).json()
        if 'video_id' not in start_res: return
        video_id = start_res['video_id']
        upload_url = f"https://rupload.facebook.com/video-upload/v19.0/{video_id}"
        headers = {'Authorization': f'OAuth {ACCESS_TOKEN}', 'offset': '0', 'file_size': file_size, 'X-Entity-Length': file_size, 'Content-Type': 'application/octet-stream'}
        with open(video_path, 'rb') as f:
            upload_res = requests.post(upload_url, headers=headers, data=f.read())
        if upload_res.status_code == 200:
            requests.post(start_url, data={'upload_phase': 'finish', 'video_id': video_id, 'video_state': 'PUBLISHED', 'description': description, 'access_token': ACCESS_TOKEN})
            print("🎉 تم نشر فيديو الريلز بنجاح.")
    except Exception as e: print(f"⚠️ فشل الريلز: {e}")

try:
    with open("product.json", "r", encoding="utf-8") as f: product_data = json.load(f)
    product_id = product_data.get("product_id")
    code = product_data.get("product_code", "")
    price = product_data.get("price", "")
except: product_id = None; code = ""; price = ""

try:
    with open("facebook_post_sales.txt", "r", encoding="utf-8") as f: caption = f.read().strip()
except: caption = "كوليكشن جديد متاح الآن."

url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos?access_token={ACCESS_TOKEN}"

try:
    print("🚀 جاري نشر البوست الأساسي...")
    with open("marketing_collage.jpg", "rb") as img:
        response = requests.post(url, data={"caption": caption}, files={"source": ("post.jpg", img, "image/jpeg")})
        
    res_data = response.json()
    if "id" in res_data:
        print("✅ تم نشر البوست الأساسي بنجاح!")
        post_link = f"https://facebook.com/{res_data['id']}"
        
        # التحديث الإجباري للذاكرة لمنع الـ Loop
        if product_id:
            try:
                with open("posted_ids.json", "r") as f: posted_ids = json.load(f)
            except: posted_ids = []
            if product_id not in posted_ids:
                posted_ids.append(product_id)
                with open("posted_ids.json", "w") as f: json.dump(posted_ids[-1000:], f)
                print("💾 تم تأمين حفظ الـ ID في الذاكرة بنجاح.")

        # تحديث لوحة التحكم
        dashboard_file = 'dashboard.csv'
        file_exists = os.path.isfile(dashboard_file)
        with open(dashboard_file, 'a', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists: writer.writerow(['التاريخ والوقت', 'كود الموديل', 'السعر', 'رابط البوست'])
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), code, price, post_link])

        time.sleep(5)
        # سيتم النشر فقط إذا تم إنشاء الفيديو بنجاح
        if os.path.exists("reel_video.mp4"):
            post_video_story("reel_video.mp4")
            time.sleep(5)
            upload_reel("reel_video.mp4", caption + "\n\n#ريلز #أزياء #موضة #Fastyle")
        else:
            print("⚠️ تم تخطي الستوري والريلز لعدم وجود ملف الفيديو.")
except Exception as e:
    print(f"❌ خطأ غير متوقع في عملية النشر: {e}")
