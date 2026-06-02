import os
import json
import shutil
import random
import requests

# 1. التحقق من وجود علم التخطي
if os.path.exists("skip_flag.txt"):
    print("تخطي: لا توجد منتجات جديدة.")
    exit(0)

# 2. قراءة بيانات المنتج
try:
    with open("product.json", "r", encoding="utf-8") as f:
        product = json.load(f)
except Exception as e:
    print(f"❌ خطأ في قراءة بيانات المنتج: {e}")
    exit(1)

all_images = [img for img in product.get("images", []) if os.path.exists(img)]
best_images = all_images[:4]
cover_image = all_images[0] if all_images else ""

code = product.get("product_code", "")

# ==========================================
# إعداد الـ Prompt (أوامر صارمة بمنع السعر + طلب التعليق الصوتي)
# ==========================================
prompt_text = f"""أنت خبير تسويق أزياء مصري. مهمتك كتابة محتوى لبراند "Fastyle".
بيانات المنتج:
- كود الموديل: {code}
- الوصف: {product.get("description", "")}
(ملاحظة: السعر مخفي عمداً لزيادة التفاعل والرسائل)

التعليمات الصارمة:
1. البوست الأساسي (facebook_post_sales) جذاب وقصير جداً (3 أسطر كحد أقصى).
2. ممنوع منعاً باتاً كتابة أي سعر أو أرقام تدل على السعر في البوست أو الستوري أو الريلز.
3. انهي البوست دائماً بعبارة: "للسؤال عن السعر ولطلب الأوردر ابعتيلنا رسالة للصفحة 💌 كود الموديل: {code}"
4. أضف جملتين قصيرتين للريلز.
5. اكتب جملة واحدة بالعامية المصرية تكون جذابة جداً ومناسبة لتُقرأ كتعليق صوتي (Voiceover) في فيديو مدته 3 ثواني، وممنوع ذكر أي سعر فيها.

الرد يجب أن يكون JSON فقط بالهيكل التالي:
{{
  "facebook_post_sales": "نص البوست القصير بدون أي سعر",
  "story_post": "جملة للستوري بدون سعر",
  "reel_text_1": "كلمتين لأول الفيديو",
  "reel_text_2": "جملة لآخر الفيديو",
  "voiceover_script": "جملة التعليق الصوتي الجذابة بدون سعر"
}}"""

api_key = os.environ.get("GEMINI_API_KEY")
result_json = None

if api_key:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}], 
        "generationConfig": {"response_mime_type": "application/json"}
    }
    
    try:
        print("🚀 جاري الاتصال بموديل Gemini...")
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=30)
        
        if response.status_code == 200:
            result_text = response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            
            # معالجة الرد لضمان أن يكون بصيغة JSON نقية
            if result_text.startswith("```json"): 
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif result_text.startswith("```"): 
                result_text = result_text.split("```")[1].split("```")[0].strip()
                
            result_json = json.loads(result_text)
            print("✅ تم استلام المحتوى التسويقي والسكريبت الصوتي بنجاح (بدون أي أسعار).")
    except Exception as e:
        print(f"⚠️ فشل الاتصال بجوجل: {e}")

# ==========================================
# الخطة البديلة (تم إزالة السعر وإضافة السكريبت الصوتي)
# ==========================================
if not result_json:
    print("💡 تفعيل المحرك التسويقي البديل (نص طبيعي وجذاب بدون سعر).")
    
    fb_post = f"الجمال في التفاصيل ✨\n\nوفرنالك الموديل ده عشان يكمل شياكتك، خامة ممتازة وتقفيل بريميوم 💯\n\nللسؤال عن السعر ولطلب الأوردر ابعتيلنا رسالة للصفحة 💌\nكود الموديل: {code}"
        
    result_json = {
        "facebook_post_sales": fb_post,
        "story_post": f"إيه رأيكم في الموديل ده؟ 😍 كود: {code}",
        "reel_text_1": "شياكة متتقارنش!",
        "reel_text_2": f"اطلبي دلوقتي بكود {code}",
        "voiceover_script": "شياكة وتفاصيل تخطف العين، متفوتيش الموديل ده واطلبيه دلوقتي."
    }

# 3. إلحاق الصور بالبيانات للتسليم للمرحلة القادمة
result_json["best_images"] = best_images
result_json["cover_image"] = cover_image

# 4. حفظ المخرجات في ملفات نصية منظمة
with open("ai_result.json", "w", encoding="utf-8") as f: 
    json.dump(result_json, f, ensure_ascii=False, indent=4)
    
with open("facebook_post_sales.txt", "w", encoding="utf-8") as f: 
    f.write(result_json.get("facebook_post_sales", ""))
    
with open("story_post.txt", "w", encoding="utf-8") as f: 
    f.write(result_json.get("story_post", ""))
    
with open("reel_idea.txt", "w", encoding="utf-8") as f: 
    f.write(result_json.get("facebook_post_sales", ""))

# 5. تجهيز الصور المختارة
os.makedirs("selected_images", exist_ok=True)
for img in best_images: 
    shutil.copy(img, os.path.join("selected_images", os.path.basename(img)))
    
if cover_image: 
    shutil.copy(cover_image, "cover_image.jpg")
    
print("🎉 اكتمل تجهيز النصوص والسكريبت الصوتي بنجاح.")
