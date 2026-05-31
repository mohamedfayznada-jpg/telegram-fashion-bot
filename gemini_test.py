import os
import json
import shutil
from PIL import Image
from google import genai
from google.genai import types # التعديل: استيراد types للتحكم في نوع المخرجات

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

with open("product.json", "r", encoding="utf-8") as f:
    product = json.load(f)

images = []
for file in product["images"]:
    if os.path.exists(file):
        try:
            images.append(Image.open(file))
        except Exception:
            pass

available_images = "\n".join(product["images"])

# نفس الـ Prompt العبقري بتاعك ماتغيرش فيه حاجة
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

# التعديل هنا: إجبار Gemini على إرجاع JSON سليم
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
    )
)

result = response.text
print("\nRAW_RESPONSE:\n")
print(result)

with open("ai_result.json", "w", encoding="utf-8") as f:
    f.write(result)

# مفيش داعي لعملية التنظيف المعقدة لأن المخرجات دلوقتي JSON صافي مضمون
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
         
marketing_package = {
    "product_code": product["product_code"],
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

if len(data.get("best_images", [])) > 4:
    data["best_images"] = data["best_images"][:4]

if len(data.get("carousel_order", [])) > 4:
    data["carousel_order"] = data["carousel_order"][:4]

with open("facebook_post_soft.txt", "w", encoding="utf-8") as f:
    f.write(data.get("facebook_post_soft", ""))

with open("facebook_post_sales.txt", "w", encoding="utf-8") as f:
    f.write(data.get("facebook_post_sales", ""))

with open("facebook_post_viral.txt", "w", encoding="utf-8") as f:
    f.write(data.get("facebook_post_viral", ""))

with open("facebook_post_short.txt", "w", encoding="utf-8") as f:
    f.write(data.get("facebook_post_short", ""))

with open("story_post.txt", "w", encoding="utf-8") as f:
    f.write(data.get("story_post", ""))

with open("reel_idea.txt", "w", encoding="utf-8") as f:
    f.write(data.get("reel_idea", ""))

with open("selling_points.json", "w", encoding="utf-8") as f:
    json.dump(data.get("selling_points", []), f, ensure_ascii=False, indent=2)

with open("customer_questions.json", "w", encoding="utf-8") as f:
    json.dump(data.get("customer_questions", []), f, ensure_ascii=False, indent=2)

with open("carousel_order.json", "w", encoding="utf-8") as f:
    json.dump(data.get("carousel_order", []), f, ensure_ascii=False, indent=2)

os.makedirs("selected_images", exist_ok=True)

for image_path in data.get("best_images", []):
    if os.path.exists(image_path):
        shutil.copy(image_path, os.path.join("selected_images", os.path.basename(image_path)))

cover_image = data.get("cover_image", "")
if cover_image and os.path.exists(cover_image):
    shutil.copy(cover_image, "cover_image.jpg")

print("\nFILES_CREATED_SUCCESSFULLY")
