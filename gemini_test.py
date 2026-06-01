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
# 2. محرك القوالب الذكي (Fault Tolerance Fallback)
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
# 3. محاولة الاتصال بالذكاء الاصطناعي (Primary Core)
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
        # محاولة واحدة سريعة، مفيش انتظار أو تضييع وقت
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=10)
        if response.status_code == 200:
            result_text = response.json()['candidates'][0]['content']['parts'][0]['text']
            # تنظيف الـ JSON
            if result_text.startswith("
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1

انسخ الكود ده يا فايز واعمل Run. الإستراتيجية دي هتحول الـ Pipeline بتاعك لماكينة لا تتوقف أبداً، ولو جوجل عملت 429، السيستم هيبتسم ويكمل شغله وينشر البوست! مستني أسمع الأخبار الحلوة.
