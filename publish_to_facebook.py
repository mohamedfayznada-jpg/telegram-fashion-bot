import os
import time
import requests

PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN")

if not PAGE_ID or not ACCESS_TOKEN:
    print("❌ بيانات الفيسبوك غير موجودة. سيتم تخطي النشر.")
    exit(0)

def post_story(image_path):
    print("⏳ انتظار 10 ثواني قبل رفع الستوري لتجنب حظر الفيسبوك...")
    time.sleep(10)
    print("🚀 جاري نشر الستوري...")
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photo_stories"
    with open(image_path, "rb") as img:
        response = requests.post(url, data={"access_token": ACCESS_TOKEN}, files={"source": img})
    res_data = response.json()
    if "id" in res_data:
        print(f"✅ تم نشر الستوري بنجاح! رقم الستوري: {res_data['id']}")
    else:
        print(f"❌ حدث خطأ أثناء نشر الستوري: {res_data}")

def upload_reel(video_path, description):
    if not os.path.exists(video_path):
        print("⚠️ ملف فيديو الريلز غير موجود!")
        return
        
    print("⏳ انتظار 15 ثانية قبل رفع الريلز...")
    time.sleep(15)
    print("🚀 بدء رفع فيديو الريلز (3 Phases)...")
    
    start_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_reels"
    start_res = requests.post(start_url, data={'upload_phase': 'start', 'access_token': ACCESS_TOKEN}).json()
    
    if 'video_id' not in start_res:
        print(f"❌ خطأ في بدء رفع الريلز: {start_res}")
        return
        
    video_id = start_res['video_id']
    upload_url = f"https://rupload.facebook.com/video-upload/v19.0/{video_id}"
    headers = {'Authorization': f'OAuth {ACCESS_TOKEN}', 'offset': '0'}
    
    with open(video_path, 'rb') as f:
        upload_res = requests.post(upload_url, headers=headers, data=f.read())
        
    if upload_res.status_code != 200:
        print(f"❌ خطأ في رفع ملف الريلز: {upload_res.text}")
        return
        
    finish_res = requests.post(start_url, data={
        'upload_phase': 'finish',
        'video_id': video_id,
        'video_state': 'PUBLISHED',
        'description': description,
        'access_token': ACCESS_TOKEN
    }).json()
    
    if 'success' in finish_res and finish_res['success']:
        print("🎉 تم نشر الريلز بنجاح على الصفحة!")
    else:
        print(f"❌ خطأ في النشر النهائي للريلز: {finish_res}")

# ==============================
# التنفيذ الرئيسي
# ==============================
post_file = "facebook_post_sales.txt"
reel_text_file = "reel_idea.txt" # النص المخصص للريلز
image_file = "marketing_collage.jpg"
video_file = "reel_video.mp4"

if os.path.exists(post_file) and os.path.exists(image_file):
    with open(post_file, "r", encoding="utf-8") as f:
        caption = f.read().strip()

    print("🚀 جاري النشر على الفيسبوك (البوست الأساسي)...")
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
    
    with open(image_file, "rb") as img:
        response = requests.post(url, data={"caption": caption, "access_token": ACCESS_TOKEN}, files={"source": img})
        
    res_data = response.json()
    if "id" in res_data:
        print(f"✅ تم نشر البوست بنجاح! رقم البوست: {res_data['id']}")
        
        # 1. نشر الستوري بصورة الكولاچ
        post_story(image_file)
        
        # 2. نشر فيديو الريلز
        reel_desc = caption # لو ملف reel_idea مش موجود هنستخدم البوست العادي
        if os.path.exists(reel_text_file):
            with open(reel_text_file, "r", encoding="utf-8") as rf:
                reel_desc = rf.read().strip() + f"\n\n#ريلز #Fastyle"
                
        upload_reel(video_file, reel_desc)
        
    else:
        print("❌ حدث خطأ أثناء النشر:", res_data)
else:
    print("⚠ الملفات المطلوبة للنشر غير متوفرة.")
