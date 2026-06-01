import os
import json
import shutil
import time
import base64
import requests
import io
from PIL import Image

# 1. قراءة بيانات المنتج
with open("product.json", "r", encoding="utf-8") as f:
    product = json.load(f)

# 2. 💡 الحل السحري الثاني: ضغط الصور قبل الإرسال (Smart Compression)
image_parts = []
for file in product.get("images", []):
    if os.path.exists(file):
        try:
            with Image.open(file) as img:
                # تصغير الأبعاد لـ 800 بيكسل كحد أقصى
                img.thumbnail((800, 800))
                # تحويل الصورة لـ RGB لضمان التوافق مع JPEG
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # حفظ الصورة في الذاكرة الوهمية (Buffer) بجودة 75%
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=75)
                
                # تشفير الصورة المصغرة
                encoded_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
                image_parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": encoded_string
                    }
                })
        except Exception as e:
            print(f"⚠️ تعذر ضغط أو قراءة الصورة {file}: {e}")

available_images = "\n".join(product.get("images", []))

# 3. إعداد الـ Prompt
prompt_text = f"""
أنت خبير تسويق أزياء مصري محترف.
مهمتك كتابة محتوى لبراند ملابس مصري راقي اسمه "Fastyle".

بيانات المنتج:
- كود الموديل: {product.get("product_code", "")}
- الوصف الأصلي: {product.get("description", "")}

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

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ مفتاح GEMINI_API_KEY غير موجود!")
    exit(1)

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
headers = {"Content-Type": "application/json"}
parts = [{"text": prompt_text}] + image_parts
payload = {
    "contents": [{"parts": parts}],
    "generationConfig": {"response_mime_type": "application/json"}
}

result = None
print("🚀 جاري إرسال البيانات المحسنة والمضغوطة إلى Gemini...")

for attempt in range(3):
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()['candidates'][0]['content']['parts'][0]['text']
            print("✅ نجح الاتصال واستلام المحتوى في لمح البصر!")
            break
        elif response.status_code == 429:
            print("⚠️ زحام على السيرفر (الخطأ 429). انتظار 30 ثانية...")
            time.sleep(30)
        else:
            print(f"⚠️ خطأ {response.status_code}: {response.text}")
            time.sleep(10)
    except Exception as e:
        print(f"⚠️ خطأ في الاتصال: {e}")
        time.sleep(10)

if not result:
    print("\n❌ فشل الاتصال بجوجل تماماً.")
    exit(1)

# 4. تنظيف وتصدير الملفات
print("\n✅ جاري تجهيز الملفات النهائية...")
if result.startswith("```json"):
    result = result.split("```json")[1].split("```")[0].strip()
elif result.startswith("```"):
    result = result.split("```")[1].split("```")[0].strip()

with open("ai_result.json", "w", encoding="utf-8") as f:
    f.write(result)

try:
    data_json = json.loads(result)
except Exception as e:
    print("❌ خطأ في قراءة ملف JSON الناتج")
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

print("🎉 اكتمل استخراج المحتوى بنجاح!")
