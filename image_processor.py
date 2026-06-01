import os
import cv2
import json
import hashlib
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

if os.path.exists("skip_flag.txt"): 
    exit(0)

folder_selected = "selected_images"
folder_all = "downloads"

if not os.path.exists(folder_selected) or not os.path.exists(folder_all): 
    exit(0)

font_path = "Cairo-Bold.ttf"
font_ready = os.path.exists(font_path)
if not font_ready:
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
        except: 
            continue

def get_image_hash(filepath):
    with open(filepath, "rb") as f: 
        return hashlib.md5(f.read()).hexdigest()

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

# ==========================================
# دمج اللوجو مع تأثير "الهالة المضيئة" (Glow Effect) في أسفل اليسار
# ==========================================
draw = ImageDraw.Draw(canvas, "RGBA")
footer_height = 220 
draw.rectangle([0, 1200 - footer_height, 1200, 1200], fill=(15, 23, 42, 240))

logo_path = "logo.png"
if os.path.exists(logo_path):
    logo = Image.open(logo_path).convert("RGBA")
    logo_target_height = 180 # اللوجو بقى ضخم جداً
    
    w_percent = (logo_target_height / float(logo.height))
    logo_target_width = int((float(logo.width) * float(w_percent)))
    logo = logo.resize((logo_target_width, logo_target_height), Image.Resampling.LANCZOS)
    
    x_pos = 40
    y_pos = 1200 - footer_height + ((footer_height - logo_target_height) // 2)
    
    # 1. رسم هالة بيضاء مضيئة خلف اللوجو لضمان بروزه
    aura = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    draw_aura = ImageDraw.Draw(aura)
    pad = 15
    draw_aura.ellipse([x_pos - pad, y_pos - pad, x_pos + logo_target_width + pad, y_pos + logo_target_height + pad], fill=(255, 255, 255, 150))
    aura = aura.filter(ImageFilter.GaussianBlur(15))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), aura)
    
    # 2. لصق اللوجو فوق الهالة المضيئة
    transparent = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    transparent.paste(logo, (x_pos, y_pos), mask=logo)
    canvas = Image.alpha_composite(canvas.convert("RGBA"), transparent)

canvas.convert("RGB").save("marketing_collage.jpg", quality=95)

# صورة الستوري (جودة 80 لتخفيف الحجم لفيسبوك)
story_canvas = canvas.resize((1080, 1080))
story_bg = story_canvas.resize((1080, 1920)).filter(ImageFilter.GaussianBlur(30))
story_bg.paste(story_canvas, (0, (1920 - 1080) // 2))
story_bg.convert("RGB").save("story_ready.jpg", quality=80)

# ==========================================
# إعداد فيديو الريلز
# ==========================================
try:
    with open("ai_result.json", "r", encoding="utf-8") as f: 
        ai_data = json.load(f)
except: 
    ai_data = {}

def draw_arabic_text(img_pil, text, y_pos, font_size=70):
    if not font_ready: 
        return img_pil
    try:
        bidi_text = get_display(arabic_reshaper.reshape(text))
        font = ImageFont.truetype(font_path, font_size)
        draw = ImageDraw.Draw(img_pil, "RGBA")
        try: 
            w = font.getlength(bidi_text)
        except: 
            w = 400
        x_pos = (1080 - w) / 2
        draw.text((x_pos + 4, y_pos + 4), bidi_text, font=font, fill=(0, 0, 0, 255))
        draw.text((x_pos, y_pos), bidi_text, font=font, fill=(255, 215, 0, 255))
    except: 
        pass
    return img_pil

fps = 30
frames_per_img = 45 
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
        bg = base.resize((1920, 1920)).crop(((1920-1080)//2, 0, (1920+1080)//2, 1920)).filter(ImageFilter.GaussianBlur(40))
        bg = Image.alpha_composite(bg.convert('RGBA'), Image.new('RGBA', bg.size, (0, 0, 0, 100))).convert('RGB')
        
        fg_w = 1080
        fg_h = int((float(base.height) * (1080 / float(base.width))))
        if fg_h > 1650:
            fg_h = 1650
            fg_w = int((float(base.width) * (fg_h / float(base.height))))
            
        fg = base.resize((fg_w, fg_h), Image.Resampling.LANCZOS)
        bg.paste(fg, ((1080 - fg_w) // 2, (1920 - fg_h) // 2))
        
        # فوتر الريلز واللوجو في أسفل اليسار
        reel_footer_h = 280
        ImageDraw.Draw(bg, 'RGBA').rectangle([0, 1920 - reel_footer_h, 1080, 1920], fill=(15, 23, 42, 240))
        
        if os.path.exists(logo_path):
            logo_reel_h = 220
            w_percent_r = (logo_reel_h / float(logo.height))
            logo_r = logo.resize((int(float(logo.width) * w_percent_r), logo_reel_h), Image.Resampling.LANCZOS)
            
            # هالة الريلز
            draw_v_aura = ImageDraw.Draw(bg, 'RGBA')
            pad = 20
            v_y_pos = 1920 - reel_footer_h + ((reel_footer_h - logo_reel_h) // 2)
            draw_v_aura.ellipse([40 - pad, v_y_pos - pad, 40 + logo_r.width + pad, v_y_pos + logo_reel_h + pad], fill=(255, 255, 255, 100))
            
            bg.paste(logo_r, (40, v_y_pos), mask=logo_r)

        if idx == 0: 
            bg = draw_arabic_text(bg, ai_data.get("reel_text_1", "شياكة لا تقاوم!"), 250, 85)
        elif idx == len(v_unique) - 1: 
            bg = draw_arabic_text(bg, ai_data.get("reel_text_2", "اطلبيها دلوقتي"), 250, 80)
            
        frame = cv2.cvtColor(np.array(bg), cv2.COLOR_RGB2BGR)
        for _ in range(frames_per_img): 
            video.write(frame)
    except: 
        pass

video.release()
print("🎉 اكتمل إنشاء الصور والريلز بنجاح.")
