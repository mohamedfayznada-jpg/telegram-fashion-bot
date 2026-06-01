import os
import json
import shutil
import base64
import time
import requests

# 1. قراءة بيانات المنتج
with open("product.json", "r", encoding="utf-8") as f:
    product = json.load(f)

available_images = "\n".join(product.get("images", []))

# 2. إعداد الـ Prompt الاحترافي
prompt = f"""
أنت خبير تسويق أزياء مصري محترف (Fashion Copywriter).
مهمتك كتابة محتوى لبراند ملابس مصري راقي اسمه "Fastyle".

بيانات المنتج:
- كود الموديل: {product.get("product_code", "")}
- الوصف الأصلي: {product.get("description", "")}
- مسارات الصور: {available_images}

شروط الكتابة (صارمة جداً):
1. اللهجة: مصرية شبابية، راقية، وجذابة جداً (زي بلوجرز الفاشون).
2. الـ Hook (أول سطر): لازم يكون سطر بيخطف العين ويلعب على المشاعر.
3. التنسيق: قسم الكلام لفقرات قصيرة جداً (سطرين بالكتير).
4. الإيموجيز: استخدم إيموجيز راقية وهادية (✨, 🎀, 👗, 🤍).
5. الكود: كود الموديل ينزل في سطر لوحده خالص في آخر البوست.
6. المصداقية: إياك تخترع ألوان، خامات، أو مقاسات مش موجودة في الوصف الأصلي.

Return ONLY valid JSON with this exact structure:
{{
  "facebook_post_sales": "اكتب البوست الجذاب هنا",
  "facebook_post_soft": "اكتب بوست هادي بدون بيع مباشر",
  "facebook_post_viral": "اكتب بوست تفاعلي بيكلم البنات",
  "facebook_post_short": "بوست قصير جدا",
  "story_post": "اكتب سطرين جذابين للستوري",
  "reel_idea": "فكرة فيديو ريلز",
  "best_images": ["path1", "path2"],
  "cover_image": "path1",
  "selling_points": [],
  "customer_questions": [],
  "carousel_order": []
}}
"""

# تجهيز البيانات للإرسال (النص + الصور)
content_array = [{"type": "text", "text": prompt}]

for file in product.get("images", []):
    if os.path.exists(file):
        try:
            with open(file, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                ext = os.path.splitext(file)[1].lower().replace('.', '')
                mime_type = f"image/{ext}" if ext in ['jpg', 'jpeg', 'png', 'webp'] else "image/jpeg"
                
                content_array.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{encoded_string}"
                    }
                })
        except Exception as e:
            print(f"⚠️ تعذر قراءة الصورة {file}: {e}")

# 3. الاتصال بـ OpenRouter
api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key:
    print("❌ مفتاح OPENROUTER_API_KEY غير موجود في الـ Secrets!")
    exit(1)

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 🚀 تم تحديث الموديل لأحدث نسخة مستقرة ومدعومة بالكامل 
data = {
    "model": "google/gemini-3.5-flash", 
    "messages": [{"role": "user", "content": content_array}]
}

result = None
for attempt in range(3):
    try:
        print(f"⏳ جاري الاتصال بـ OpenRouter (محاولة {attempt + 1}/3)...")
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()['choices'][0]['message']['content']
            break
        else:
            print(f"⚠️ خطأ من السيرفر: {response.text}")
            time.sleep(5)
    except Exception as e:
        print(f"⚠️ خطأ في الاتصال: {e}")
        time.sleep(5)
else:
    print("❌ فشل الاتصال بـ OpenRouter.")
    exit(1)

# 4. تنظيف وحفظ المخرجات
print("\nRAW_RESPONSE:\n", result)

# استخراج الـ JSON لو الموديل رجعه جوه علامات ```json
if result and "```json" in result:
    result = result.split("```json")[1].split("```")[0].strip()
elif result and "```" in result:
    result = result.split("```")[1].split("```")[0].strip()

with open("ai_result.json", "w", encoding="utf-8") as f:
    f.write(result if result else "{}")

try:
    data_json = json.loads(result)
except Exception as e:
    print("\nJSON ERROR:\n", result)
    raise e

marketing_package = {
    "product_code": product.get("product_code", ""),
    "cover_image": data_json.get("cover_image", ""),
    "best_images": data_json.get("best_images", []),
    "facebook_post_sales": data_json.get("facebook_post_sales", ""),
    "story_post": data_json.get("story_post", ""),
    "reel_idea": data_json.get("reel_idea", ""),
}

# حفظ النصوص في ملفات منفصلة
files_to_write = {
    "facebook_post_sales.txt": "facebook_post_sales",
    "story_post.txt": "story_post",
    "reel_idea.txt": "reel_idea"
}

for filename, key in files_to_write.items():
    with open(filename, "w", encoding="utf-8") as f:
        f.write(data_json.get(key, ""))

# نسخ أفضل 4 صور
os.makedirs("selected_images", exist_ok=True)
for image_path in data_json.get("best_images", [])[:4]:
    if os.path.exists(image_path):
        shutil.copy(image_path, os.path.join("selected_images", os.path.basename(image_path)))

cover_image = data_json.get("cover_image", "")
if cover_image and os.path.exists(cover_image):
    shutil.copy(cover_image, "cover_image.jpg")

print("\n✅ تم تجهيز محتوى الذكاء الاصطناعي بنجاح من OpenRouter!")
