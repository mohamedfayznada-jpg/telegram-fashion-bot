import os
import cv2
import json
import hashlib
import requests
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
from gtts import gTTS

# 1. التحقق من وجود علم التخطي
if os.path.exists("skip_flag.txt"):
    print("تخطي: لا توجد منتجات جديدة لمعالجتها.")
    exit(0)

folder_selected = "selected_images"
folder_all = "downloads"

if not os.path.exists(folder_selected) or not os.path.exists(folder_all):
    print("⚠️ مجلدات الصور غير موجودة.")
    exit(0)

# ==========================================
# 2. تحميل الخطوط العربية للتصميم
# ==========================================
font_path = "Cairo-Bold.ttf"
font_ready = os.path.exists(font_path)
if not font_ready:
    print("⏳ جاري تحميل الخطوط العربية...")
    font_urls = [
        "https://raw.githubusercontent.com/google/fonts/main/ofl/cairo/static/Cairo-Bold.ttf",
        "https://raw.githubusercontent.com/Gue22/Cairo-Font/master/Cairo-Bold.ttf"
    ]
    for url in font_urls:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                with open(font_path, 'wb') as f:
                    f.write(res.content)
                font_ready = True
                break
        except Exception:
            continue

def get_image_hash(filepath):
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

# ==========================================
# 3. إعداد الكولاچ الديناميكي (Dynamic Layouts)
# ==========================================
print("⏳ جاري إنشاء الكولاچ الإعلاني...")
unique_images = []
seen = set()
for file in sorted(os.listdir(folder_selected)):
    path = os.path.join(folder_selected, file)
    h = get_image_hash(path)
    if h not in seen:
        seen.add(h)
        unique_images.append(Image.open(path).convert("RGB"))

canvas = Image.new("RGB", (1200, 1200), "white")
imgs = unique_images[:4]

# اختيار قالب التصميم عشوائياً لكسر الملل
layout_style = random.choice(["standard", "modern"])

if len(imgs) == 1:
    canvas.paste(imgs[0].resize((1200, 1200)), (0, 0))
elif len(imgs) == 2:
    if layout_style == "modern":
        canvas.paste(imgs[0].resize((1200, 600)), (0, 0))
        canvas.paste(imgs[1].resize((1200, 600)), (0, 600))
    else:
        canvas.paste(imgs[0].resize((600, 1200)), (0, 0))
        canvas.paste(imgs[1].resize((600, 1200)), (600, 0))
elif len(imgs) == 3:
    canvas.paste(imgs[0].resize((1200, 600)), (0, 0))
    canvas.paste(imgs[1].resize((600, 600)), (0, 600))
    canvas.paste(imgs[2].resize((600, 600)), (600, 600))
elif len(imgs) == 4:
    positions = [(0, 0), (600, 0), (0, 600), (600, 600)]
    for img, pos in zip(imgs, positions):
        canvas.paste(img.resize((600, 600)), pos)

# ==========================================
# 4. دمج اللوجو في الزاوية اليسرى السفلية مع هالة مضيئة
# ==========================================
draw = ImageDraw.Draw(canvas, "RGBA")
footer_height = 220 
draw.rectangle([0, 1200 - footer_height, 1200, 1200], fill=(15, 23, 42, 240))

logo_path = "logo.png"
if os.path.exists(logo_path):
    logo = Image.open(logo_path).convert("RGBA")
    logo_target_height = 180 
    w_percent = (logo_target_height / float(logo.height))
    logo_target_width = int((float(logo.width) * float(w_percent)))
    logo = logo.resize((logo_target_width, logo_target_height), Image.Resampling.LANCZOS)
    
    # تحديد الموضع في الزاوية اليسرى السفلية تماماً
    x_pos = 40
    y_pos = 1200 - footer_height + ((footer_height - logo_target_height) // 2)
    
    # رسم الهالة
    aura = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    draw_aura = ImageDraw.Draw(aura)
    draw_aura.ellipse([x_pos - 15, y_pos - 15, x_pos + logo_target_width + 15, y_pos + logo_target_height + 15], fill=(255, 255, 255, 150))
    aura = aura.filter(ImageFilter.GaussianBlur(15))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), aura)
    
    # لصق اللوجو
    transparent = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    transparent.paste(logo, (x_pos, y_pos), mask=logo)
    canvas = Image.alpha_composite(canvas.convert("RGBA"), transparent)

canvas.convert("RGB").save("marketing_collage.jpg", quality=95)

# صورة الستوري المخصصة
story_canvas = canvas.resize((1080, 1080))
story_bg = story_canvas.resize((1080, 1920)).filter(ImageFilter.GaussianBlur(30))
story_bg.paste(story_canvas, (0, (1920 - 1080) // 2))
story_bg.convert("RGB").save("story_ready.jpg", quality=80)
print("✅ تم تجهيز الصور بنجاح.")

# ==========================================
# 5. إعداد فيديو الريلز الحركي (Motion Video)
# ==========================================
print("🎥 جاري إنشاء فيديو الريلز الحركي...")
try:
    with open("ai_result.json", "r", encoding="utf-8") as f:
        ai_data = json.load(f)
except Exception:
    ai_data = {}

def draw_dynamic_arabic_text(img_pil, text, y_pos, font_size, alpha):
    if not font_ready:
        return img_pil
    try:
        bidi_text = get_display(arabic_reshaper.reshape(text))
        font = ImageFont.truetype(font_path, font_size)
        txt_layer = Image.new('RGBA', img_pil.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        try:
            w = font.getlength(bidi_text)
        except AttributeError:
            w = 400
        x_pos = (1080 - w) / 2
        
        # إضافة ظل قوي ثم النص مع درجة الشفافية (Motion Fade)
        draw.text((x_pos + 4, y_pos + 4), bidi_text, font=font, fill=(0, 0, 0, int(alpha)))
        draw.text((x_pos, y_pos), bidi_text, font=font, fill=(255, 215, 0, int(alpha)))
        img_pil = Image.alpha_composite(img_pil.convert('RGBA'), txt_layer)
    except Exception:
        pass
    return img_pil.convert('RGB')

fps = 30
frames_per_img = 45 
video = cv2.VideoWriter("reel_video_temp.mp4", cv2.VideoWriter_fourcc(*'mp4v'), fps, (1080, 1920))

all_img_paths = [os.path.join(folder_all, f) for f in sorted(os.listdir(folder_all)) if f.lower().endswith(('.png', '.jpg'))]
v_unique = []
v_seen = set()
for p in all_img_paths:
    h = get_image_hash(p)
    if h not in v_seen:
        v_seen.add(h)
        v_unique.append(p)

for idx, img_path in enumerate(v_unique):
    try:
        base = Image.open(img_path).convert("RGB")
        for frame_idx in range(frames_per_img):
            zoom_factor = 1.0 + (0.05 * frame_idx / frames_per_img) 
            bg = base.resize((1920, 1920)).crop(((1920-1080)//2, 0, (1920+1080)//2, 1920)).filter(ImageFilter.GaussianBlur(40))
            bg = Image.alpha_composite(bg.convert('RGBA'), Image.new('RGBA', bg.size, (0, 0, 0, 100))).convert('RGB')
            
            fg_w = int(1080 * zoom_factor)
            fg_h = int((float(base.height) * (1080 / float(base.width))) * zoom_factor)
            if fg_h > 1650 * zoom_factor:
                fg_h = int(1650 * zoom_factor)
                fg_w = int((float(base.width) * (fg_h / float(base.height))))
                
            fg = base.resize((fg_w, fg_h), Image.Resampling.LANCZOS)
            bg.paste(fg, ((1080 - fg_w) // 2, (1920 - fg_h) // 2))
            
            # فوتر الريلز واللوجو في أسفل اليسار أيضاً
            reel_footer_h = 280
            ImageDraw.Draw(bg, 'RGBA').rectangle([0, 1920 - reel_footer_h, 1080, 1920], fill=(15, 23, 42, 240))
            if os.path.exists(logo_path):
                logo_reel_h = 220
                w_percent_r = (logo_reel_h / float(logo.height))
                logo_r = logo.resize((int(float(logo.width) * w_percent_r), logo_reel_h), Image.Resampling.LANCZOS)
                v_y_pos = 1920 - reel_footer_h + ((reel_footer_h - logo_reel_h) // 2)
                bg.paste(logo_r, (40, v_y_pos), mask=logo_r)

            alpha = min(255, (frame_idx / 15) * 255)
            text_y = 300 - int(50 * (frame_idx / frames_per_img)) 
            
            if idx == 0:
                bg = draw_dynamic_arabic_text(bg, ai_data.get("reel_text_1", "شياكة لا تقاوم!"), text_y, 85, alpha)
            elif idx == len(v_unique) - 1:
                bg = draw_dynamic_arabic_text(bg, ai_data.get("reel_text_2", "اطلبيها دلوقتي"), text_y, 80, alpha)
                
            video.write(cv2.cvtColor(np.array(bg), cv2.COLOR_RGB2BGR))
    except Exception as e:
        print(f"⚠️ خطأ في معالجة إطار الفيديو: {e}")
video.release()

# ==========================================
# 6. إنشاء التعليق الصوتي ودمجه مع الفيديو (Voiceover AI)
# ==========================================
print("🎙️ جاري توليد التعليق الصوتي ودمجه...")
try:
    script = ai_data.get("voiceover_script", "كوليكشن جديد متاح الآن، اطلبي الأوردر قبل نفاذ الكمية.")
    tts = gTTS(text=script, lang='ar', slow=False)
    tts.save("voice.mp3")
    
    # دمج الصوت مع الفيديو بشكل احترافي
    os.system("ffmpeg -i reel_video_temp.mp4 -i voice.mp3 -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest reel_video.mp4 -y")
    print("✅ تم دمج الصوت بالذكاء الاصطناعي بنجاح!")
except Exception as e:
    print(f"⚠️ فشل توليد أو دمج الصوت، سيتم استخدام الفيديو الصامت كبديل: {e}")
    if os.path.exists("reel_video_temp.mp4"):
        os.rename("reel_video_temp.mp4", "reel_video.mp4")
