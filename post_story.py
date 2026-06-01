import os
import requests

FB_PAGE_ID = os.environ.get('FACEBOOK_PAGE_ID', '')
FB_ACCESS_TOKEN = os.environ.get('FACEBOOK_ACCESS_TOKEN', '')

# مسار الصورة اللي عايزين نرفعها ستوري
STORY_IMAGE_PATH = 'ready.jpg' 

def post_facebook_story(image_path):
    url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photo_stories"
    
    payload = {
        'access_token': FB_ACCESS_TOKEN
    }
    
    print("⏳ جاري رفع الستوري...")
    with open(image_path, 'rb') as img:
        files = {'source': img}
        response = requests.post(url, data=payload, files=files)
        
    result = response.json()
    if 'id' in result:
        print(f"✅ تم نشر الستوري بنجاح! Story ID: {result['id']}")
    else:
        print(f"❌ حدث خطأ أثناء نشر الستوري: {result}")

if __name__ == '__main__':
    # هنا هنستدعي الصورة (ممكن نبرمجه يختار صورة عشوائية من المجلد مستقبلاً)
    if os.path.exists(STORY_IMAGE_PATH):
        post_facebook_story(STORY_IMAGE_PATH)
    else:
        print("⚠️ لم يتم العثور على صورة لرفعها كستوري.")
