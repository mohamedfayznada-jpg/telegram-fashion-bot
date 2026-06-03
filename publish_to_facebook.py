import os
import time
import requests
import json
import csv
from datetime import datetime

if os.path.exists("skip_flag.txt"): exit(0)

PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN")
IG_ACCOUNT_ID = os.environ.get("INSTAGRAM_ACCOUNT_ID")

if not PAGE_ID or not ACCESS_TOKEN: 
    print("❌ خطأ: التوكن أو الـ ID غير متوفر في الإعدادات!")
    exit(0)

# Micro-service: رفع الملفات لسيرفر مؤقت لتقديمها لإنستجرام
def get_public_url(local_path):
    print(f"🌐 جاري توليد رابط عام للملف: {local_path}...")
    try:
        with open(local_path, 'rb') as f:
            res = requests.post("https://catbox.moe/user/api.php", data={"reqtype": "fileupload"}, files={"fileToUpload": f})
            if res.status_code == 200:
                return res.text.strip()
            else:
                print(f"⚠️ فشل توليد الرابط: {res.text}")
    except Exception as e:
        print(f"⚠️ خطأ في الاستضافة المؤقتة: {e}")
    return None

def post_fb_video_story(video_path):
    if not os.path.exists(video_path): return
    print("🚀 جاري نشر ستوري فيسبوك...")
    file_size = str(os.path.getsize(video_path))
    start_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_stories"
    try:
        start_res = requests.post(start_url, data={'upload_phase': 'start', 'access_token': ACCESS_TOKEN, 'file_size': file_size}).json()
        if 'video_id' not in start_res: 
            print(f"❌ فشل بدء رفع الستوري: {start_res}")
            return
        vid_id = start_res['video_id']
        requests.post(f"https://rupload.facebook.com/video-upload/v19.0/{vid_id}", headers={'Authorization': f'OAuth {ACCESS_TOKEN}', 'offset': '0', 'file_size': file_size, 'X-Entity-Length': file_size, 'Content-Type': 'application/octet-stream'}, data=open(video_path, 'rb').read())
        finish_res = requests.post(start_url, data={'upload_phase': 'finish', 'video_id': vid_id, 'access_token': ACCESS_TOKEN}).json()
        if "success" in finish_res or "video_id" in finish_res:
            print("✅ تم نشر ستوري فيسبوك بنجاح.")
        else:
            print(f"❌ خطأ في إنهاء الستوري: {finish_res}")
    except Exception as e: print(f"⚠️ خطأ برمجي في الستوري: {e}")

def upload_fb_reel(video_path, description):
    if not os.path.exists(video_path): return
    print("🚀 جاري نشر ريلز فيسبوك...")
    file_size = str(os.path.getsize(video_path))
    start_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_reels"
    try:
        start_res = requests.post(start_url, data={'upload_phase': 'start', 'access_token': ACCESS_TOKEN, 'file_size': file_size}).json()
        if 'video_id' not in start_res:
            print(f"❌ فشل بدء رفع الريلز: {start_res}")
            return
        vid_id = start_res['video_id']
        requests.post(f"https://rupload.facebook.com/video-upload/v19.0/{vid_id}", headers={'Authorization': f'OAuth {ACCESS_TOKEN}', 'offset': '0', 'file_size': file_size, 'X-Entity-Length': file_size, 'Content-Type': 'application/octet-stream'}, data=open(video_path, 'rb').read())
        finish_res = requests.post(start_url, data={'upload_phase': 'finish', 'video_id': vid_id, 'video_state': 'PUBLISHED', 'description': description, 'access_token': ACCESS_TOKEN}).json()
        if "success" in finish_res or "video_id" in finish_res:
            print("🎉 تم نشر ريلز فيسبوك بنجاح.")
        else:
            print(f"❌ خطأ في إنهاء الريلز: {finish_res}")
    except Exception as e: print(f"⚠️ خطأ برمجي في الريلز: {e}")

def post_to_instagram(image_path, video_path, caption):
    if not IG_ACCOUNT_ID:
        print("⚠️ تم تخطي النشر على إنستجرام (IG_ACCOUNT_ID غير متوفر).")
        return

    print("🚀 جاري النشر على إنستجرام...")
    
    if os.path.exists(image_path):
        img_url = get_public_url(image_path)
        if img_url:
            container_res = requests.post(f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media", data={"image_url": img_url, "caption": caption, "access_token": ACCESS_TOKEN}).json()
            if "id" in container_res:
                pub_res = requests.post(f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media_publish", data={"creation_id": container_res["id"], "access_token": ACCESS_TOKEN}).json()
                if "id" in pub_res: print("✅ تم نشر بوست إنستجرام بنجاح.")
                else: print(f"❌ فشل نشر بوست إنستجرام: {pub_res}")
            else: print(f"❌ فشل إنشاء حاوية إنستجرام (Post): {container_res}")

    if os.path.exists(video_path):
        vid_url = get_public_url(video_path)
        if vid_url:
            reel_container = requests.post(f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media", data={"media_type": "REELS", "video_url": vid_url, "caption": caption + "\n\n#موضة #أزياء #ريلز", "access_token": ACCESS_TOKEN}).json()
            if "id" in reel_container:
                time.sleep(15) 
                pub_res = requests.post(f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media_publish", data={"creation_id": reel_container["id"], "access_token": ACCESS_TOKEN}).json()
                if "id" in pub_res: print("🎉 تم نشر ريلز إنستجرام بنجاح.")
                else: print(f"❌ فشل نشر ريلز إنستجرام: {pub_res}")
            else: print(f"❌ فشل إنشاء حاوية إنستجرام (Reel): {reel_container}")

# التنفيذ الرئيسي
try:
    with open("product.json", "r", encoding="utf-8") as f: product_data = json.load(f)
    product_id, code, price = product_data.get("product_id"), product_data.get("product_code", ""), product_data.get("price", "")
except: product_id = None; code = ""; price = ""

try:
    with open("facebook_post_sales.txt", "r", encoding="utf-8") as f: caption = f.read().strip()
except: caption = "كوليكشن جديد."

url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos?access_token={ACCESS_TOKEN}"

try:
    print("🚀 جاري نشر البوست الأساسي (فيسبوك)...")
    res_data = requests.post(url, data={"caption": caption}, files={"source": open("marketing_collage.jpg", "rb")}).json()
        
    if "id" in res_data:
        print("✅ تم نشر بوست فيسبوك بنجاح!")
        post_link = f"https://facebook.com/{res_data['id']}"
        
        if product_id:
            try:
                with open("posted_ids.json", "r") as f: posted_ids = json.load(f)
            except: posted_ids = []
            if product_id not in posted_ids:
                posted_ids.append(product_id)
                with open("posted_ids.json", "w") as f: json.dump(posted_ids[-1000:], f)

        dashboard_file = 'dashboard.csv'
        file_exists = os.path.isfile(dashboard_file)
        with open(dashboard_file, 'a', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists: writer.writerow(['التاريخ والوقت', 'كود الموديل', 'السعر', 'رابط البوست'])
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), code, price, post_link])

        time.sleep(5)
        if os.path.exists("reel_video.mp4"):
            post_fb_video_story("reel_video.mp4")
            time.sleep(5)
            upload_fb_reel("reel_video.mp4", caption + "\n\n#ريلز #موضة #Fastyle")

        time.sleep(5)
        post_to_instagram("marketing_collage.jpg", "reel_video.mp4", caption)

    else:
        print(f"❌ كارثة فيسبوك (البوست لم ينشر): {res_data}")

except Exception as e:
    print(f"❌ خطأ غير متوقع في الكود الأساسي: {e}")
