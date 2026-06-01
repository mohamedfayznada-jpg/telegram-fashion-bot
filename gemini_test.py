import os
import json
import shutil
import time
import random
import google.generativeai as genai
from PIL import Image

# 1. قراءة بيانات المنتج
with open("product.json", "r", encoding="utf-8") as f:
    product = json.load(f)

# 2. تجهيز الصور
images = []
for file in product.get("images", []):
    if os.path.exists(file):
        try:
            images.append(Image.open(file))
        except Exception as e:
            print(f"⚠️ تعذر فتح الصورة {file}: {e}")

available_images = "\n".join(product.get("images", []))

# 3. إعداد الـ Prompt
prompt = f"""
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

contents = images + [prompt]

# 💡 انتظار بسيط لتخفيف ضغط جيتهاب
sleep_time = random.randint(10, 20)
print(f"⏳ انتظار {sleep_time} ثانية للهروب من زحام جيتهاب...")
time.sleep(sleep_time)

# 4. الاتصال بمكتبة جوجل الرسمية المستقرة
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ مفتاح GEMINI_API_KEY غير موجود!")
    exit(1)

genai.configure(api_key=api_key)

# ضبط الموديل عشان يرجع JSON دايماً
generation_config = genai.types.GenerationConfig(
    response_mime_type="application/json"
)

model = genai.GenerativeModel('gemini-1.5-flash', generation_config=generation_config)

result = None
for attempt in range(4):
    try:
        print(f"⏳ جاري الاتصال بـ Gemini (محاولة {attempt + 1}/4)...")
        response = model.generate_content(contents)
        result = response.text
        break 
    except Exception as e:
        error_msg = str(e).lower()
        if "429" in error_msg or "503" in error_msg or "quota" in error_msg:
            wait_t = 20 * (attempt + 1)
            print(f"⚠️ زحام على السيرفر. سننتظر {wait_t} ثانية...")
            time.sleep(wait_t)
        else:
            print(f"⚠️ خطأ غير متوقع: {e}")
            time.sleep(10)

if not result:
    print("❌ فشل الاتصال بجوجل تماماً.")
    exit(1)

# 5. معالجة وتصدير الملفات
print("\n✅ تم الاتصال بنجاح واستلام المحتوى!")
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
