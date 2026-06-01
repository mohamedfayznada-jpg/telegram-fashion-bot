import os
import json
import shutil
import random
import requests

# 1. قراءة بيانات المنتج
with open("product.json", "r", encoding="utf-8") as f:
    product = json.load(f)

all_images = [img for img in product.get("images", []) if os.path.exists(img)]
best_images = all_images[:4]
cover_image = all_images[0] if all_images else ""

# ==========================================
# 2. محرك القوالب الذكي (الخطة البديلة المضمونة 100%)
# ==========================================
def generate_fallback_content():
    desc = product.get("description", "تصميم عصري ومريح يناسب خروجاتك.")
    code = product.get("product_code", "")
    
    hooks = [
        "✨ الشياكة اللي بتدوري عليها لقيناها لك! 🎀",
        "🤍 عشان تفاصيلك بتفرق، جبنالك الكوليكشن الجديد!",
        "👗 قطعة أساسية في دولابك متتفوتش.. خطفت قلوبنا!",
        "✨ الجمال في التفاصيل.. تألقي مع أحدث موديلات Fastyle! 🌸"
    ]
    
    facebook_post = f"{random.choice(hooks)}\n\nوفرنالك الموديل ده عشان يكمل شياكتك، خامة ممتازة وتقفيل بريميوم 💯\n\n📌 التفاصيل:\n{desc}\n\nاطلبيها دلوقتي قبل نفاذ الكمية 💌\n\nكود الموديل: {code}"
    
    return {
        "facebook_post_sales": facebook_post,
        "story_post": f"الجديد وصل! ✨\nكود: {code}\nاسحبي الشاشة واطلبيها دلوقتي 🤍",
        "reel_idea": facebook_post,
        "best_images": best_images,
        "cover_image": cover_image
    }

# ==========================================
# 3. محاولة الاتصال بالذكاء الاصطناعي
# ==========================================
api_key = os.environ.get("GEMINI_API_KEY")
result_json = None

if api_key:
    print("🚀 جاري محاولة الاتصال بـ Gemini...")
    prompt_text = f"""أنت خبير تسويق أزياء مصري. اكتب محتوى لبراند "Fastyle".
بيانات المنتج:
- كود: {product.get("product_code", "")}
- الوصف: {product.get("description", "")}
الرد يجب أن يكون JSON فقط يحتوي على: facebook_post_sales, story_post, reel_idea."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }
    
    try:
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=15)
        if response.status_code == 200:
            result_text = response.json()['candidates'][0]['content']['parts'][0]['text']
            result_text = result_text.strip()
            
            # تنظيف الـ JSON بشكل آمن ومفرود
            if result_text.startswith("```json"):
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif result_text.startswith("```"):
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            try:
                result_json = json.loads(result_text)
                result_json["best_images"] = best_images
                result_json["cover_image"] = cover_image
                print("✅ نجح Gemini في كتابة المحتوى التسويقي!")
            except json.JSONDecodeError:
                print("⚠️ جوجل أرسل نص غير صالح. سيتم التحويل للمحرك البديل.")
                result_json = None
        else:
            print(f"⚠️ جوجل رفض الطلب (الخطأ {response.status_code}). سيتم التحويل للمحرك البديل.")
    except Exception as e:
        print(f"⚠️ فشل الاتصال بالسيرفر: {e}. سيتم التحويل للمحرك البديل.")

# ==========================================
# 4. تفعيل الخطة البديلة فوراً في حالة فشل جوجل
# ==========================================
if not result_json:
    print("💡 تفعيل (المحرك البديل المحلي) لضمان استمرار النشر بدون أي توقف...")
    result_json = generate_fallback_content()

# ==========================================
# 5. تصدير الملفات وبدء النشر
# ==========================================
print("\n✅ جاري تجهيز الملفات النهائية...")
files_to_write = {
    "facebook_post_sales.txt": "facebook_post_sales",
    "story_post.txt": "story_post",
    "reel_idea.txt": "reel_idea"
}

for filename, key in files_to_write.items():
    with open(filename, "w", encoding="utf-8") as f:
        f.write(result_json.get(key, ""))

os.makedirs("selected_images", exist_ok=True)
for image_path in result_json.get("best_images", []):
    shutil.copy(image_path, os.path.join("selected_images", os.path.basename(image_path)))

if result_json.get("cover_image"):
    shutil.copy(result_json["cover_image"], "cover_image.jpg")

print("🎉 اكتمل استخراج المحتوى بنجاح تام!")
