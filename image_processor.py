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

if len(imgs) == 1: canvas.paste(imgs[0].resize((1200, 1200)), (0, 0))
elif len(imgs) == 2:
    canvas.paste(imgs[0].resize((600, 1200)), (0, 0))
    canvas.paste(imgs[1].resize((600, 1200)), (600, 0))
elif len(imgs) == 3:
    canvas.paste(imgs[0].resize((1200, 600)), (0, 0))
    canvas.paste(imgs[1].resize((600, 600)), (0, 600))
    canvas.paste(imgs[2].resize((600, 600)), (600, 600))
elif len(imgs) == 4:
    positions = [(0, 0), (600, 0), (0, 600), (600, 600)]
    for img, pos in zip(imgs, positions): canvas.paste(img.resize((600, 600)), pos)

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
    x_pos = 40
    y_pos = 1200 - footer_height + ((footer_height - logo_target_height) // 2)
    
    aura = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    draw_aura = ImageDraw.Draw(aura)
    pad = 15
    draw_aura.ellipse([x_pos - pad, y_pos - pad, x_pos + logo_target_width + pad, y_pos + logo_target_height + pad], fill=(255, 255, 255, 150))
    aura = aura.filter(ImageFilter.GaussianBlur(15))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), aura)
    
    transparent = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    transparent.paste(logo, (x_pos, y_pos), mask=logo)
    canvas = Image.alpha_composite(canvas.convert("RGBA"), transparent)

canvas.convert("RGB").save("marketing_collage.jpg", quality=95)

story_canvas = canvas.resize((1080, 1080))
story_bg = story_canvas.resize((1080, 1920)).filter(ImageFilter.GaussianBlur(30))
story_bg.paste(story_canvas, (0, (1920 - 1080) // 2))
story_bg.convert("RGB").save("story_ready.jpg", quality=80)

# ==========================================
# إعداد فيديو الريلز (بتقنية الحركة لمنع الحظر)
# ==========================================
try:
    with open("ai_result.json", "r", encoding="utf-8") as f: ai_data = json.load(f)
except: ai_data = {}

def draw_dynamic_arabic_text(img_pil, text, y_pos, font_size, alpha):
    if not font_ready: return img_pil
    try:
        bidi_text = get_display(arabic_reshaper.reshape(text))
        font = ImageFont.truetype(font_path, font_size)
        txt_layer = Image.new('RGBA', img_pil.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        try: w = font.getlength(bidi_text)
        except: w = 400
        x_pos = (1080 - w) / 2
        
        # رسم النص بظل أسود وتأثير الشفافية (Motion)
        draw.text((x_pos + 4, y_pos + 4), bidi_text, font=font, fill=(0, 0, 0, int(alpha)))
        draw.text((x_pos, y_pos), bidi_text, font=font, fill=(255, 215, 0, int(alpha)))
        img_pil = Image.alpha_composite(img_pil.convert('RGBA'), txt_layer)
    except: pass
    return img_pil.convert('RGB')

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

print("🎥 جاري إنشاء الريلز الحركي (Motion Video)...")
for idx, img_path in enumerate(v_unique):
    try:
        base = Image.open(img_path).convert("RGB")
        
        # إضافة حركة (Animation) على كل فريم
        for frame_idx in range(frames_per_img):
            # 1. تأثير الزووم البطيء (Ken Burns Effect)
            zoom_factor = 1.0 + (0.05 * frame_idx / frames_per_img) # زووم 5%
            
            bg = base.resize((1920, 1920)).crop(((1920-1080)//2, 0, (1920+1080)//2, 1920)).filter(ImageFilter.GaussianBlur(40))
            bg = Image.alpha_composite(bg.convert('RGBA'), Image.new('RGBA', bg.size, (0, 0, 0, 100))).convert('RGB')
            
            fg_w = int(1080 * zoom_factor)
            fg_h = int((float(base.height) * (1080 / float(base.width))) * zoom_factor)
            if fg_h > 1650 * zoom_factor:
                fg_h = int(1650 * zoom_factor)
                fg_w = int((float(base.width) * (fg_h / float(base.height))))
                
            fg = base.resize((fg_w, fg_h), Image.Resampling.LANCZOS)
            bg.paste(fg, ((1080 - fg_w) // 2, (1920 - fg_h) // 2))
            
            # فوتر الريلز واللوجو
            reel_footer_h = 280
            ImageDraw.Draw(bg, 'RGBA').rectangle([0, 1920 - reel_footer_h, 1080, 1920], fill=(15, 23, 42, 240))
            if os.path.exists(logo_path):
                logo_reel_h = 220
                w_percent_r = (logo_reel_h / float(logo.height))
                logo_r = logo.resize((int(float(logo.width) * w_percent_r), logo_reel_h), Image.Resampling.LANCZOS)
                v_y_pos = 1920 - reel_footer_h + ((reel_footer_h - logo_reel_h) // 2)
                bg.paste(logo_r, (40, v_y_pos), mask=logo_r)

            # 2. حركة النص (يظهر تدريجياً ويتحرك لأعلى)
            alpha = min(255, (frame_idx / 15) * 255) # Fade in
            text_y = 300 - int(50 * (frame_idx / frames_per_img)) # Slide up
            
            if idx == 0: 
                bg = draw_dynamic_arabic_text(bg, ai_data.get("reel_text_1", "شياكة لا تقاوم!"), text_y, 85, alpha)
            elif idx == len(v_unique) - 1: 
                bg = draw_dynamic_arabic_text(bg, ai_data.get("reel_text_2", "اطلبيها دلوقتي"), text_y, 80, alpha)
                
            frame = cv2.cvtColor(np.array(bg), cv2.COLOR_RGB2BGR)
            video.write(frame)
    except Exception as e: 
        print(f"Error frame: {e}")

video.release()
print("🎉 اكتمل إنشاء فيديو الريلز الحركي بنجاح.")
