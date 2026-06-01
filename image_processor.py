import os
import cv2
import json
import numpy as np
import hashlib
import urllib.request
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

if os.path.exists("skip_flag.txt"):
    exit(0)

folder_selected = "selected_images"
folder_all = "downloads"

# 1. تحميل خط عربي آمن للكتابة على الفيديوهات
font_path = "Cairo-Bold.ttf"
if not os.path.exists(font_path):
    print("⏳ جاري تحميل الخط العربي للريلز...")
    urllib.request.urlretrieve("https://github.com/google/fonts/raw/main/ofl/cairo/Cairo-Bold.ttf", font_path)

def get_image_hash(filepath):
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

# 2. إعداد الصور والكولاچ (بدون تكرار)
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

# ترتيب الصور في الكولاچ
if len(imgs) == 1:
    canvas.paste(imgs[0].resize((1200, 1200)), (0, 0))
elif len(imgs) == 2:
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

# رسم شريط سفلي داكن لضمان وضوح اللوجو
draw = ImageDraw.Draw(canvas, "RGBA")
footer_height = 130  # تكبير مساحة الفوتر
draw.rectangle([0, 1200 - footer_height, 1200, 1200], fill=(15, 23, 42, 230))

# إضافة اللوجو بشكل بارز وواضح أسفل اليسار
logo_path = "logo.png"
if os.path.exists(logo_path):
    logo = Image.open(logo_path).convert("RGBA")
    logo_target_height = 95  # تكبير اللوجو ليكون بارزاً
    
    w_percent = (logo_target_height / float(logo.height))
    logo_target_width = int((float(logo.width) * float(w_percent)))
    logo = logo.resize((logo_target_width, logo_target_height), Image.Resampling.LANCZOS)
    
    # حساب موضع اللوجو (الزاوية اليسرى السفلية، في منتصف الشريط الداكن)
    x_position = 30
    y_position = 1200 - footer_height + ((footer_height - logo_target_height) // 2)
    
    transparent = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    transparent.paste(logo, (x_position, y_position), mask=logo)
    canvas = Image.alpha_composite(canvas.convert("RGBA"), transparent)
    print("✅ تم دمج اللوجو بشكل بارز في الكولاچ.")

canvas.convert("RGB").save("marketing_collage.jpg", quality=95)

# 3. إعداد صورة الستوري المخصصة
story_canvas = canvas.resize((1080, 1080))
story_bg = story_canvas.resize((1080, 1920)).filter(ImageFilter.GaussianBlur(30))
story_bg.paste(story_canvas, (0, (1920 - 1080) // 2))
story_bg.convert("RGB").save("story_ready.jpg", quality=95)

# 4. إعداد فيديو الريلز الديناميكي
try:
    with open("ai_result.json", "r", encoding="utf-8") as f:
        ai_data = json.load(f)
except Exception:
    ai_data = {}

reel_text_1 = ai_data.get("reel_text_1", "شياكة لا تقاوم!")
reel_text_2 = ai_data.get("reel_text_2", "اطلبيها دلوقتي")

def draw_arabic_text(img_pil, text, y_pos, font_size=70):
    reshaped = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped)
    font = ImageFont.truetype(font_path, font_size)
    draw = ImageDraw.Draw(img_pil, "RGBA")
    
    try:
        w = font.getlength(bidi_text)
    except AttributeError:
        w = 400
        
    x_pos = (1080 - w) / 2
    
    # رسم ظل أسود للنص عشان يكون واضح
    draw.text((x_pos + 4, y_pos + 4), bidi_text, font=font, fill=(0, 0, 0, 255))
    draw.text((x_pos, y_pos), bidi_text, font=font, fill=(255, 215, 0, 255)) # لون ذهبي
    return img_pil

print("🎥 جاري إنشاء فيديو الريلز...")
fps = 30
frames_per_img = 45 # فيديو سريع 1.5 ثانية للصورة
video = cv2.VideoWriter("reel_video.mp4", cv2.VideoWriter_fourcc(*'mp4v'), fps, (1080, 1920))

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
        
        # خلفية ضبابية
        bg = base.resize((1920, 1920)).crop(((1920-1080)//2, 0, (1920+1080)//2, 1920)).filter(ImageFilter.GaussianBlur(40))
        bg = Image.alpha_composite(bg.convert('RGBA'), Image.new('RGBA', bg.size, (0, 0, 0, 100))).convert('RGB')
        
        # الصورة الأصلية في المنتصف
        fg_w = 1080
        fg_h = int((float(base.height) * (1080 / float(base.width))))
        if fg_h > 1720:
            fg_h = 1720
            fg_w = int((float(base.width) * (fg_h / float(base.height))))
            
        fg = base.resize((fg_w, fg_h), Image.Resampling.LANCZOS)
        bg.paste(fg, ((1080 - fg_w) // 2, (1920 - fg_h) // 2))
        
        # الفوتر الخاص بالريلز ووضع اللوجو بشكل بارز
        ImageDraw.Draw(bg, 'RGBA').rectangle([0, 1750, 1080, 1920], fill=(15, 23, 42, 230))
        if os.path.exists(logo_path):
            logo_y_pos_video = 1750 + ((170 - logo_target_height) // 2)
            bg.paste(logo, (30, logo_y_pos_video), mask=logo)

        # إضافة النصوص المتحركة
        if idx == 0:
            bg = draw_arabic_text(bg, reel_text_1, 250, 85)
        elif idx == len(v_unique) - 1:
            bg = draw_arabic_text(bg, reel_text_2, 250, 80)
            
        frame = cv2.cvtColor(np.array(bg), cv2.COLOR_RGB2BGR)
        for _ in range(frames_per_img):
            video.write(frame)
    except Exception as e:
        print(f"⚠️ خطأ في معالجة إطار الفيديو: {e}")

video.release()
print("🎉 اكتمل إنشاء الريلز بنجاح.")
