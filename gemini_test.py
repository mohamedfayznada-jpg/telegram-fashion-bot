import os
import json
import shutil
import time
from PIL import Image
from google import genai
from google.genai import types, errors # تم استيراد errors لاصطياد أخطاء السيرفر

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 1. قراءة بيانات المنتج
with open("product.json", "r", encoding="utf-8") as f:
    product = json.load(f)

# 2. تجهيز الصور
images = []
for file in product["images"]:
    if os.path.exists(file):
        try:
            images.append(Image.open(file))
        except Exception as e:
            print(f"⚠️ تعذر فتح الصورة {file}: {e}")

available_images = "\n".join(product["images"])

# 3. إعداد الـ Prompt
prompt = f"""
You are an expert Facebook fashion marketer.

Product code:
{product["product_code"]}

Product description:
{product["description"]}

Available image paths:
{available_images}

STRICT RULES:
- Product description is the ONLY source of truth.
- Images are used only for selecting the best photos.
- NEVER invent colors, sizes, materials, discounts, offers, stock availability, or customer benefits not explicitly mentioned.
- NEVER invent product details from image analysis.
- customer_questions must be answerable from existing product data only.

Image selection is extremely important.
Analyze all images carefully.
Rank images by clarity, lighting, composition, product visibility, and sales potential.
Choose the strongest images for Facebook marketing.
If two images are similar, keep only the better one.
Never ask about information that does not exist in Product description.
If information is not written in Product description, DO NOT mention it.

IMPORTANT LANGUAGE RULE:
All generated content must be written in Egyptian Arabic.

VERY IMPORTANT:
best_images must contain ONLY paths from Available image paths.
carousel_order must contain ONLY paths from Available image paths.
cover_image must contain ONLY one path from Available image paths.
Do NOT create URLs, filenames, or image numbers.

Return ONLY valid JSON:
{{
  "facebook_post_soft": "",
  "facebook_post_sales": "",
  "facebook_post_viral": "",
  "facebook_post_short": "",
  "hashtags": [],
  "story_post": "",
  "reel_idea": "",
  "selling_points": [],
  "customer_questions": [],
  "carousel_order": [],
  "best_images": [],
  "cover_image": ""
}}
"""

contents = images + [prompt]

# 4. استدعاء Gemini مع آلية إعادة المحاولة (Retry Mechanism)
max_retries = 3
result = None

for attempt in range(max_retries):
    try:
        print(f"⏳ جاري الاتصال بـ Gemini (محاولة {attempt + 1}/{max_retries})...")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        result = response.text
        break  # خروج من اللوب فوراً في حالة النجاح
        
    except errors.APIError as e:
        # التقاط أخطاء الضغط على السيرفر (503) أو تخطي الحد المسموح (429)
        if e.code in [503, 429]:
            print(f"⚠️ سيرفر Gemini مشغول (الخطأ {e.code}). انتظار 10 ثواني...")
            time.sleep(10)
        else:
            # لو خطأ مختلف، يتم إظهاره وإيقاف البرنامج
            raise e
else:
    # سيتم تنفيذ هذا الجزء فقط إذا استنفذ البرنامج كل المحاولات وفشل
    print("❌ فشلت جميع المحاولات للاتصال بـ Gemini بسبب الضغط على السيرفر.")
    exit(1)

# 5. معالجة وحفظ المخرجات
print("\nRAW_RESPONSE:\n")
print(result)

with open("ai_result.json", "w", encoding="utf-8") as f:
    f.write(result)

try:
    data = json.loads(result)
except Exception as e:
    print("\nJSON ERROR:\n", result)
    raise e

print("\nBEST_IMAGES_FROM_GEMINI:\n")
for img in data.get("best_images", []):
    print(img)

print("\nFILES_IN_DOWNLOADS:\n")
if os.path.exists("downloads"):
    for f in os.listdir("downloads"):
        print(os.path.join("downloads", f))

# 6. تجهيز حزمة التسويق وتصدير الملفات
marketing_package = {
    "product_code": product.get("product_code", ""),
    "cover_image": data.get("cover_image", ""),
    "best_images": data.get("best_images", []),
    "facebook_post_soft": data.get("facebook_post_soft", ""),
    "facebook_post_sales": data.get("facebook_post_sales", ""),
    "facebook_post_viral": data.get("facebook_post_viral", ""),
    "facebook_post_short": data.get("facebook_post_short", ""),
    "story_post": data.get("story_post", ""),
    "reel_idea": data.get("reel_idea", ""),
    "selling_points": data.get("selling_points", []),
    "customer_questions": data.get("customer_questions", []),
    "carousel_order": data.get("carousel_order", [])
}

with open("marketing_package.json", "w", encoding="utf-8") as f:
    json.dump(marketing_package, f, ensure_ascii=False, indent=2)

# تقييد عدد الصور لـ 4 كحد أقصى للبوستات
if len(data.get("best_images", [])) > 4:
    data["best_images"] = data["best_images"][:4]

if len(data.get("carousel_order", [])) > 4:
    data["carousel_order"] = data["carousel_order"][:4]

# حفظ النصوص في ملفات منفصلة
files_to_write = {
    "facebook_post_soft.txt": "facebook_post_soft",
    "facebook_post_sales.txt": "facebook_post_sales",
    "facebook_post_viral.txt": "facebook_post_viral",
    "facebook_post_short.txt": "facebook_post_short",
    "story_post.txt": "story_post",
    "reel_idea.txt": "reel_idea"
}

for filename, key in files_to_write.items():
    with open(filename, "w", encoding="utf-8") as f:
        f.write(data.get(key, ""))

# حفظ القوائم في ملفات JSON
json_files_to_write = {
    "selling_points.json": "selling_points",
    "customer_questions.json": "customer_questions",
    "carousel_order.json": "carousel_order"
}

for filename, key in json_files_to_write.items():
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data.get(key, []), f, ensure_ascii=False, indent=2)

# 7. نسخ الصور المختارة
os.makedirs("selected_images", exist_ok=True)

for image_path in data.get("best_images", []):
    if os.path.exists(image_path):
        shutil.copy(image_path, os.path.join("selected_images", os.path.basename(image_path)))

cover_image = data.get("cover_image", "")
if cover_image and os.path.exists(cover_image):
    shutil.copy(cover_image, "cover_image.jpg")

print("\nFILES_CREATED_SUCCESSFULLY")
