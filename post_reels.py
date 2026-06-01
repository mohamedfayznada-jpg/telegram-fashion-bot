import os
import requests

FB_PAGE_ID = os.environ.get('FACEBOOK_PAGE_ID', 'حط_الآيدي_هنا')
FB_ACCESS_TOKEN = os.environ.get('FACEBOOK_ACCESS_TOKEN', 'حط_التوكن_هنا')

def upload_facebook_reel(video_path, description):
    print("🚀 بدء عملية رفع الريلز (3 Phases)...")
    
    # 1. مرحلة التهيئة (Start Phase)
    # بنقول لفيسبوك: إحنا عندنا فيديو عايزين نرفعه كـ Reel
    start_url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/video_reels"
    start_payload = {
        'upload_phase': 'start',
        'access_token': FB_ACCESS_TOKEN
    }
    start_res = requests.post(start_url, data=start_payload).json()
    
    if 'video_id' not in start_res:
        print(f"❌ خطأ في مرحلة التهيئة: {start_res}")
        return
        
    video_id = start_res['video_id']
    print(f"✅ تم فتح الاتصال! رقم الفيديو: {video_id}")
    
    # 2. مرحلة الرفع الفعلي (Transfer Phase)
    # بنرفع ملف الفيديو نفسه على سيرفرات rupload الخاصة بفيسبوك
    upload_url = f"https://rupload.facebook.com/video-upload/v19.0/{video_id}"
    headers = {
        'Authorization': f'OAuth {FB_ACCESS_TOKEN}',
        'offset': '0'
    }
    
    print("⏳ جاري رفع ملف الفيديو...")
    with open(video_path, 'rb') as f:
        video_data = f.read()
        upload_res = requests.post(upload_url, headers=headers, data=video_data)
        
    if upload_res.status_code != 200:
        print(f"❌ خطأ في مرحلة الرفع: {upload_res.text}")
        return
    print("✅ تم رفع ملف الفيديو بنجاح!")
    
    # 3. مرحلة النشر (Finish Phase)
    # بنقول لفيسبوك: الملف اترفع، انشره دلوقتي بالوصف ده
    finish_payload = {
        'upload_phase': 'finish',
        'video_id': video_id,
        'video_state': 'PUBLISHED',
        'description': description,
        'access_token': FB_ACCESS_TOKEN
    }
    finish_res = requests.post(start_url, data=finish_payload).json()
    
    if 'success' in finish_res and finish_res['success']:
        print("🎉 تم نشر الريلز على صفحة Fastyle بنجاح!")
    else:
        print(f"❌ خطأ في مرحلة النشر النهائية: {finish_res}")

# ==========================================
# تجربة الكود
# ==========================================
if __name__ == '__main__':
    video_file = 'test_video.mp4' # مسار الفيديو بتاعك
    post_text = "أشيك دريس ممكن تشوفيه! كوليكشن جديد متاح دلوقتي 🔥👗 #Fastyle #ريلز"
    
    if os.path.exists(video_file):
        upload_facebook_reel(video_file, post_text)
    else:
        print("⚠️ ملف الفيديو غير موجود!")
