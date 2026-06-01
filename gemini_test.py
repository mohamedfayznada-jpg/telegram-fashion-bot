import os
import json
import shutil
import requests
import time

# 1. قراءة بيانات المنتج
with open("product.json", "r", encoding="utf-8") as f:
    product = json.load(f)

# 2. تحديد الصور محلياً (بدون استهلاك الذكاء الاصطناعي لتسريع النظام 1000%)
all_images = [img for img in product.get("images", []) if os.path.exists(img)]
best_images = all_images[:4] # اختيار أول 4 صور للكولاچ
cover_image = all_images[0] if all_images else ""

# 3. إعداد الـ Prompt (نص فقط)
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
  "reel_idea": "فكرة فيديو ريلز"
}}
"""

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ مفتاح GEMINI_API_KEY غير موجود!")
    exit(1)

# استخدام موديل gemini-2.0-flash المتاح والمستقر في حسابك
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
headers = {"Content-Type": "application/json"}
payload = {
    "contents": [{"parts": [{"text": prompt_text}]}],
    "generationConfig": {"response_mime_type": "application/json"}
}

print("🚀 جاري إرسال البيانات (نص فقط لضمان استجابة فورية وتفادي الحظر)...")

result = None
for attempt in range(3):
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()['candidates'][0]['content']['parts'][0]['text']
            print("✅ نجح الاتصال واستلام المحتوى التسويقي في لمح البصر!")
            break
        elif response.status_code == 429:
            print("⚠️ زحام طفيف. انتظار 10 ثواني...")
            time.sleep(10)
        else:
            print(f"⚠️ خطأ {response.status_code}: {response.text}")
            time.sleep(5)
    except Exception as e:
        print(f"⚠️ خطأ في الاتصال: {e}")
        time.sleep(5)

if not result:
    print("❌ فشل الاتصال بجوجل.")
    exit(1)

# 4. تنظيف وتصدير الملفات
print("\n✅ جاري تجهيز الملفات النهائية...")
if result.startswith("```json"):
    result = result.split("```json")[1].split("```")[0].strip()
elif result.startswith("```"):
    result = result.split("```")[1].split("```")[0].strip()

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

# حفظ الصور المختارة محلياً لاستخدامها في الكولاچ والريلز
os.makedirs("selected_images", exist_ok=True)
for image_path in best_images:
    shutil.copy(image_path, os.path.join("selected_images", os.path.basename(image_path)))

if cover_image:
    shutil.copy(cover_image, "cover_image.jpg")

print("🎉 اكتمل استخراج المحتوى وتجهيز الصور بنجاح تام!")
