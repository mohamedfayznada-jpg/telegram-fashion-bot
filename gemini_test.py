import os
import json
import shutil
import random
import requests

if os.path.exists("skip_flag.txt"):
    print("تخطي: لا توجد منتجات جديدة.")
    exit(0)

try:
    with open("product.json", "r", encoding="utf-8") as f:
        product = json.load(f)
except Exception as e:
    print(f"❌ خطأ في قراءة بيانات المنتج: {e}")
    exit(1)

all_images = [img for img in product.get("images", []) if os.path.exists(img)]
best_images = all_images[:4]
cover_image = all_images[0] if all_images else ""

prompt_text = f"""أنت خبير تسويق أزياء مصري. مهمتك كتابة محتوى لبراند "Fastyle".
بيانات المنتج:
- كود الموديل: {product.get("product_code", "")}
- الوصف: {product.get("description", "")}
- السعر: {product.get("price", "")}

التعليمات الصارمة:
1. اختر أسلوباً تسويقياً واحداً (الندرة، حل المشكلة، أو الفخامة).
2. البوست الأساسي (facebook_post_sales) يجب أن يكون جذاباً، 3 أسطر فقط، يتضمن السعر إن وجد، وينتهي بعبارة: "لطلب الأوردر ابعتيلنا رسالة، كود الموديل: [الكود]".
3. أضف جملتين قصيرتين للريلز (reel_text_1 و reel_text_2) لتظهر كطبقة نصية على الفيديو.

الرد يجب أن يكون JSON فقط بالهيكل التالي:
{{
  "facebook_post_sales": "نص البوست القصير",
  "story_post": "جملة واحدة جذابة للستوري",
  "reel_text_1": "كلمتين أو ثلاثة لأول الفيديو",
  "reel_text_2": "جملة تشجيعية لآخر الفيديو"
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
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=20)
        
        if response.status_code == 200:
            result_text = response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            
            # تنظيف مخرجات JSON
            if result_text.startswith("```json"):
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif result_text.startswith("```"):
                result_text = result_text.split("```")[1].split("```")[0].strip()
                
            result_json = json.loads(result_text)
            print("✅ تم استلام المحتوى التسويقي بنجاح.")
        else:
            print(f"⚠️ خطأ من سيرفر جوجل: {response.status_code}")
    except Exception as e:
        print(f"⚠️ فشل الاتصال بجوجل: {e}")

# خطة الطوارئ في حال فشل الذكاء الاصطناعي
if not result_json:
    print("💡 تفعيل المحرك التسويقي البديل للحفاظ على استمرار النشر.")
    c = product.get("product_code", "")
    p = product.get("price", "")
    price_text = f"\n💰 السعر: {p}" if p != "غير محدد" else ""
    
    result_json = {
        "facebook_post_sales": f"شياكة متتفوتش وتفاصيل تخطف العين ✨{price_text}\n\nالسعر والتفاصيل كاملة في رسايل الصفحة 💌\nكود الموديل: {c}",
        "story_post": f"إيه رأيكم في الموديل ده؟ 😍 كود: {c}",
        "reel_text_1": "شياكة متتقارنش!",
        "reel_text_2": f"اطلبي دلوقتي بكود {c}"
    }

# إضافة الصور للبيانات
result_json["best_images"] = best_images
result_json["cover_image"] = cover_image

# حفظ البيانات للمرحلة القادمة
with open("ai_result.json", "w", encoding="utf-8") as f:
    json.dump(result_json, f, ensure_ascii=False, indent=4)

with open("facebook_post_sales.txt", "w", encoding="utf-8") as f:
    f.write(result_json.get("facebook_post_sales", ""))
    
with open("story_post.txt", "w", encoding="utf-8") as f:
    f.write(result_json.get("story_post", ""))
    
with open("reel_idea.txt", "w", encoding="utf-8") as f:
    f.write(result_json.get("facebook_post_sales", ""))

# نسخ الصور المختارة
os.makedirs("selected_images", exist_ok=True)
for img in best_images:
    shutil.copy(img, os.path.join("selected_images", os.path.basename(img)))
    
if cover_image:
    shutil.copy(cover_image, "cover_image.jpg")

print("🎉 اكتمل تجهيز النصوص والصور.")
