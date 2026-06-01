import os
import time
import requests

PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN")

if not PAGE_ID or not ACCESS_TOKEN:
    print("❌ بيانات الفيسبوك غير موجودة. سيتم تخطي النشر.")
    exit(0)

# ==============================
# دالة نشر الستوري (باستخدام الصورة المخصصة للستوري)
# ==============================
def post_story(image_path):
    if not os.path.exists(image_path):
        print(f"⚠️ صورة الستوري ({image_path}) غير موجودة.")
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
# دالة نشر فيديو الريلز (مع حل مشكلة حجم الملف)
# ==============================
def upload_reel(video_path, description):
    if not os.path.exists(video_path):
        print("⚠️ ملف فيديو الريلز غير موجود!")
        return
        
    print("🚀 بدء رفع فيديو الريلز (3 Phases)...")
    
    # 1. Start Phase (إرسال حجم الملف ضروري لتجنب خطأ السيرفر)
    file_size = os.path.getsize(video_path)
    start_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_reels"
    
    start_res = requests.post(start_url, data={
        'upload_phase': 'start', 
        'access_token': ACCESS_TOKEN,
        'file_size': file_size
    }).json()
    
    if 'video_id' not in start_res:
        print(f"❌ خطأ في بدء رفع الريلز: {start_res}")
        return
        
    video_id = start_res['video_id']
    
    # 2. Upload Phase
    upload_url = f"https://rupload.facebook.com/video-upload/v19.0/{video_id}"
    headers = {
        'Authorization': f'OAuth {ACCESS_TOKEN}', 
        'offset': '0'
    }
    
    print("⏳ جاري رفع ملف الفيديو للسيرفر...")
    with open(video_path, 'rb') as f:
        upload_res = requests.post(upload_url, headers=headers, data=f.read())
        
    if upload_res.status_code != 200:
        print(f"❌ خطأ في رفع ملف الريلز: {upload_res.status_code} - {upload_res.text}")
        return
        
    # 3. Finish Phase
    print("⏳ جاري نشر الفيديو على الصفحة...")
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
image_file = "marketing_collage.jpg"
story_file = "story_ready.jpg"
video_file = "reel_video.mp4"

if os.path.exists(post_file) and os.path.exists(image_file):
    with open(post_file, "r", encoding="utf-8") as f:
        caption = f.read().strip()

    print("🚀 جاري النشر على الفيسبوك (البوست الأساسي)...")
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
        print(f"✅ تم نشر البوست بنجاح! رقم البوست: {res_data['id']}")
        
        print("⏳ انتظار 5 ثواني لتخفيف الضغط على الفيسبوك...")
        time.sleep(5)
        
        # استدعاء دالة نشر الستوري بالصورة المعدلة
        post_story(story_file)
        
        # استدعاء دالة نشر الريلز
        reel_desc = caption
        if os.path.exists("reel_idea.txt"):
            with open("reel_idea.txt", "r", encoding="utf-8") as rf:
                reel_desc = rf.read().strip() + f"\n\n#ريلز #Fastyle"
                
        upload_reel(video_file, reel_desc)
        
    else:
        print("❌ حدث خطأ أثناء نشر البوست الأساسي:", res_data)
else:
    print("⚠ الملفات المطلوبة للنشر غير متوفرة.")
