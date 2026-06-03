import os
import time
import requests
import json

if os.path.exists("skip_flag.txt"): exit(0)

PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN")
IG_ACCOUNT_ID = os.environ.get("INSTAGRAM_ACCOUNT_ID")

processed_folder = "processed_images"
ready_reels_folder = "ready_reels"
images_to_post = [os.path.join(processed_folder, f) for f in sorted(os.listdir(processed_folder)) if f.endswith('.jpg')] if os.path.exists(processed_folder) else []
reels_to_post = [os.path.join(ready_reels_folder, f) for f in sorted(os.listdir(ready_reels_folder)) if f.endswith('.mp4')] if os.path.exists(ready_reels_folder) else []

def get_public_url(local_path):
    try:
        with open(local_path, 'rb') as f:
            res = requests.post("https://tmpfiles.org/api/v1/upload", files={"file": f})
            if res.status_code == 200: return res.json()['data']['url'].replace("tmpfiles.org/", "tmpfiles.org/dl/")
    except: pass
    try:
        with open(local_path, 'rb') as f:
            res = requests.post("https://pomf2.lain.la/upload.php", files={"files[]": f})
            if res.status_code == 200: return res.json()["files"][0]["url"]
    except: pass
    return None

def wait_for_ig_media(creation_id):
    for _ in range(15):
        res = requests.get(f"https://graph.facebook.com/v19.0/{creation_id}?fields=status_code&access_token={ACCESS_TOKEN}").json()
        if res.get("status_code") == "FINISHED": return True
        time.sleep(5)
    return False

def post_fb_video_story(video_path):
    file_size = str(os.path.getsize(video_path))
    try:
        start_res = requests.post(f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_stories", data={'upload_phase': 'start', 'access_token': ACCESS_TOKEN, 'file_size': file_size}).json()
        vid_id = start_res['video_id']
        requests.post(f"https://rupload.facebook.com/video-upload/v19.0/{vid_id}", headers={'Authorization': f'OAuth {ACCESS_TOKEN}', 'offset': '0', 'file_size': file_size, 'X-Entity-Length': file_size, 'Content-Type': 'application/octet-stream'}, data=open(video_path, 'rb').read())
        requests.post(f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_stories", data={'upload_phase': 'finish', 'video_id': vid_id, 'access_token': ACCESS_TOKEN})
        print("✅ تم نشر ستوري فيسبوك بنجاح.")
    except Exception as e: print(f"⚠️ خطأ في الستوري: {e}")

def upload_fb_reel(video_path, description):
    print(f"🚀 جاري نشر ريلز فيسبوك للفيديو: {os.path.basename(video_path)}")
    file_size = str(os.path.getsize(video_path))
    try:
        start_res = requests.post(f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_reels", data={'upload_phase': 'start', 'access_token': ACCESS_TOKEN, 'file_size': file_size}).json()
        vid_id = start_res['video_id']
        requests.post(f"https://rupload.facebook.com/video-upload/v19.0/{vid_id}", headers={'Authorization': f'OAuth {ACCESS_TOKEN}', 'offset': '0', 'file_size': file_size, 'X-Entity-Length': file_size, 'Content-Type': 'application/octet-stream'}, data=open(video_path, 'rb').read())
        requests.post(f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_reels", data={'upload_phase': 'finish', 'video_id': vid_id, 'video_state': 'PUBLISHED', 'description': description, 'access_token': ACCESS_TOKEN})
        print("🎉 تم نشر ريلز فيسبوك بنجاح.")
    except Exception as e: print(f"⚠️ خطأ في الريلز: {e}")

def post_ig_carousel(images, caption):
    if not IG_ACCOUNT_ID or not images: return
    print("🚀 جاري نشر كاروسيل إنستجرام...")
    children = []
    for img in images[:10]:
        url = get_public_url(img)
        if url:
            res = requests.post(f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media", data={"image_url": url, "is_carousel_item": "true", "access_token": ACCESS_TOKEN}).json()
            if "id" in res: children.append(res["id"])
    if children:
        container = requests.post(f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media", data={"media_type": "CAROUSEL", "children": ",".join(children), "caption": caption, "access_token": ACCESS_TOKEN}).json()
        if "id" in container and wait_for_ig_media(container["id"]):
            requests.post(f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media_publish", data={"creation_id": container["id"], "access_token": ACCESS_TOKEN})
            print("✅ تم نشر كاروسيل إنستجرام بنجاح.")

def post_ig_reel(video_path, caption):
    if not IG_ACCOUNT_ID: return
    print(f"🚀 جاري نشر ريلز إنستجرام للفيديو: {os.path.basename(video_path)}")
    vid_url = get_public_url(video_path)
    if vid_url:
        reel = requests.post(f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media", data={"media_type": "REELS", "video_url": vid_url, "caption": caption, "access_token": ACCESS_TOKEN}).json()
        if "id" in reel and wait_for_ig_media(reel["id"]):
            requests.post(f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media_publish", data={"creation_id": reel["id"], "access_token": ACCESS_TOKEN})
            print("🎉 تم نشر ريلز إنستجرام بنجاح.")

# --- التنفيذ الأساسي ---
try:
    with open("facebook_post_sales.txt", "r", encoding="utf-8") as f: base_caption = f.read().strip()
except: base_caption = "كوليكشن جديد."

print("🚀 جاري نشر ألبوم صور فيسبوك...")
try:
    attached_media = []
    for img in images_to_post:
        res = requests.post(f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos", data={"published": "false", "access_token": ACCESS_TOKEN}, files={"source": open(img, "rb")}).json()
        if "id" in res: attached_media.append({"media_fbid": res["id"]})
    if attached_media:
        fb_post = requests.post(f"https://graph.facebook.com/v19.0/{PAGE_ID}/feed", json={"message": base_caption, "attached_media": attached_media, "access_token": ACCESS_TOKEN}).json()
        if "id" in fb_post: print("✅ تم نشر ألبوم فيسبوك بنجاح!")
except Exception as e: print(f"❌ خطأ في بوست فيسبوك: {e}")

time.sleep(5)
post_ig_carousel(images_to_post, base_caption)

# مصفوفة الجمل التسويقية عشان نغير بيها الكابشن لكل فيديو
hook_variations = [
    "التفاصيل على الطبيعة حكاية! 😍\n",
    "شوفوا خامة الموديل والتقفيل! 🔥\n",
    "القطعة دي لازم تكون في دولابك الموسم ده! ✨\n",
    "فخامة التفاصيل تتحدث عن نفسها! 👑\n"
]

if reels_to_post:
    print(f"🎬 جاري معالجة ونشر {len(reels_to_post)} فيديوهات...")
    for idx, reel_vid in enumerate(reels_to_post):
        # تجميع كابشن جديد لكل ريلز
        hook = hook_variations[idx % len(hook_variations)]
        reel_caption = f"{hook}\n{base_caption}\n\n#ريلز #موضة #Fastyle #أزياء"
        
        # هننشر الستوري لأول فيديو بس عشان منعملش إزعاج للعملاء
        if idx == 0:
            post_fb_video_story(reel_vid)
            time.sleep(5)
            
        upload_fb_reel(reel_vid, reel_caption)
        time.sleep(5)
        post_ig_reel(reel_vid, reel_caption)
        time.sleep(10) # فاصل زمني بين كل فيديو والتاني عشان الأمان
