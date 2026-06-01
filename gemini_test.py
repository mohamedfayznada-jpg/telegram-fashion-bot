import os
import json
import shutil
import time
import random
import base64
import requests

# 1. قراءة بيانات المنتج
with open("product.json", "r", encoding="utf-8") as f:
    product = json.load(f)

# 2. تجهيز الصور وإرسالها لجوجل كبيانات خام (Base64)
image_parts = []
for file in product.get("images", []):
    if os.path.exists(file):
        try:
            with open(file, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                ext = os.path.splitext(file)[1].lower().replace('.', '')
                mime_type = f"image/{ext}" if ext in ['jpg', 'jpeg', 'png', 'webp'] else "image/jpeg"
                image_parts.append({
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": encoded_string
                    }
                })
        except Exception as e:
            print(f"⚠️ تعذر قراءة الصورة {file}: {e}")

available_images = "\n".join(product.get("images", []))

# 3. إعداد الـ Prompt
prompt_text = f"""
أنت خبير تسويق أزياء مصري محترف.
مهمتك كتابة محتوى لبراند ملابس مصري راقي اسمه "Fastyle".

بيانات المنتج:
- كود الموديل: {product.get("product_code", "")}
- الوصف الأصلي: {product.get("description", "")}
- مسارات الصور: {available_images}

شروط الكتابة:
1. اللهجة: مصرية شبابية جذابة جداً.
2. قسم الكلام لفقرات قصيرة.
3. استخدم إيموجيز راقية (✨, 🎀, 👗, 🤍).
4. كود الموديل في سطر لوحده في النهاية.

Return ONLY valid JSON with this exact structure:
{{
  "facebook_post_sales": "اكتب البوست الجذاب هنا",
  "facebook_post_soft": "اكتب بوست هادي بدون بيع مباشر",
  "facebook_post_viral": "اكتب بوست تفاعلي بيكلم البنات",
  "facebook_post_short": "بوست قصير جدا",
  "story_post": "اكتب سطرين جذابين للستوري",
  "reel_idea": "فكرة فيديو ريلز",
  "best_images": ["path1", "path2"],
  "cover_image": "path1"
}}
"""

# 💡 الخدعة للهروب من زحام جيتهاب
sleep_time = random.randint(15, 45)
print(f"⏳ انتظار {sleep_time} ثانية للهروب من زحام السيرفرات...")
time.sleep(sleep_time)

# 4. الاتصال المباشر بجوجل بدون أي مكتبات (REST API)
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ مفتاح GEMINI_API_KEY غير موجود!")
    exit(1)

# رابط الاتصال المباشر الثابت (عمره ما يتغير ولا يضرب 404)
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

headers = {"Content-Type": "application/json"}

# تركيب الطلب
parts = [{"text": prompt_text}] + image_parts
payload = {
    "contents": [{"parts": parts}],
    "generationConfig": {"response_mime_type": "application/json"}
}

result = None
for attempt in range(4):
    try:
        print(f"⏳ جاري الاتصال المباشر بـ Gemini (محاولة {attempt + 1}/4)...")
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            try:
                result = result['candidates'][0]['content']['parts'][0]['text']
                break
            except KeyError:
                print(f"⚠️ رد غير متوقع من السيرفر: {response.text}")
                time.sleep(10)
        elif response.status_code == 429 or response.status_code >= 500:
            wait_t = 30 * (attempt + 1)
            print(f"⚠️ زحام على السيرفر (الخطأ {response.status_code}). سننتظر {wait_t} ثانية...")
            time.sleep(wait_t)
        else:
            print(f"⚠️ خطأ {response.status_code}: {response.text}")
            break
    except Exception as e:
        print(f"⚠️ خطأ في الاتصال: {e}")
        time.sleep(10)

if not result:
    print("❌ فشل الاتصال بجوجل تماماً.")
    exit(1)

# 5. معالجة وتصدير الملفات
print("\n✅ تم الاتصال بنجاح واستلام المحتوى!")

# تنظيف الـ JSON
if result.startswith("```json"):
    result = result.split("```json")[1].split("```")[0].strip()
elif result.startswith("```"):
    result = result.split("```")[1].split("```")[0].strip()

with open("ai_result.json", "w", encoding="utf-8") as f:
    f.write(result)

try:
    data_json = json.loads(result)
except Exception as e:
    print("❌ خطأ في قراءة ملف JSON")
    raise e

files_to_write = {
    "facebook_post_sales.txt": "facebook_post_sales",
    "story_post.txt": "story_post",
    "reel_idea.txt": "reel_idea"
}

for filename, key in files_to_write.items():
    with open(filename, "w", encoding="utf-8") as f:
        f.write(data_json.get(key, ""))

os.makedirs("selected_images", exist_ok=True)
for image_path in data_json.get("best_images", [])[:4]:
    if os.path.exists(image_path):
        shutil.copy(image_path, os.path.join("selected_images", os.path.basename(image_path)))

cover_image = data_json.get("cover_image", "")
if cover_image and os.path.exists(cover_image):
    shutil.copy(cover_image, "cover_image.jpg")
