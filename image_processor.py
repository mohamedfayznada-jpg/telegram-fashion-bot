import os
import cv2
import json
import hashlib
import requests
import random
import shutil
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

if os.path.exists("skip_flag.txt"): exit(0)

folder_selected = "selected_images"
folder_all = "downloads"

if not os.path.exists(folder_selected) or not os.path.exists(folder_all): exit(0)

font_path = "Cairo-Bold.ttf"
font_ready = os.path.exists(font_path)
if not font_ready:
    for url in ["https://raw.githubusercontent.com/google/fonts/main/ofl/cairo/static/Cairo-Bold.ttf", "https://raw.githubusercontent.com/Gue22/Cairo-Font/master/Cairo-Bold.ttf"]:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                with open(font_path, 'wb') as f: f.write(res.content)
                font_ready = True
                break
        except: continue

def get_image_hash(filepath):
    with open(filepath, "rb") as f: return hashlib.md5(f.read()).hexdigest()

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
layout_style = random.choice(["standard", "modern"])

if len(imgs) == 1: canvas.paste(imgs[0].resize((1200, 1200)), (0, 0))
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
    for img, pos in zip(imgs, positions): canvas.paste(img.resize((600, 600)), pos)

# إضافة ختم الندرة
draw = ImageDraw.Draw(canvas, "RGBA")
if font_ready:
    badges = ["🔥 أحدث كوليكشن", "⚡ عرض حصري", "🏃‍♀️ الحق قبل النفاذ", "⭐ الأكثر مبيعاً"]
    badge_text = random.choice(badges)
    bidi_text = get_display(arabic_reshaper.reshape(badge_text))
    b_font = ImageFont.truetype(font_path, 45)
    left, top, right, bottom = b_font.getbbox(bidi_text)
    tw, th = right - left, bottom - top
    bx, by = 1150 - tw - 40, 40 
    draw.rounded_rectangle([bx - 20, by - 15, bx + tw + 20, by + th + 15], radius=15, fill=(220, 38, 38, 230))
    draw.text((bx, by - 10), bidi_text, font=b_font, fill=(255, 255, 255, 255))

# الختم السفلي
footer_height = 220 
draw.rectangle([0, 1200 - footer_height, 1200, 1200], fill=(15, 23, 42, 240))
logo_path = "logo.png"
if os.path.exists(logo_path):
    logo = Image.open(logo_path).convert("RGBA")
    logo_target_height = 180 
    w_percent = (logo_target_height / float(logo.height))
    logo = logo.resize((int(float(logo.width) * float(w_percent)), logo_target_height), Image.Resampling.LANCZOS)
    x_pos = 40
    y_pos = 1200 - footer_height + ((footer_height - logo_target_height) // 2)
    aura = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(aura).ellipse([x_pos-15, y_pos-15, x_pos+logo.width+15, y_pos+logo_target_height+15], fill=(255, 255, 255, 150))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), aura.filter(ImageFilter.GaussianBlur(15)))
    transparent = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    transparent.paste(logo, (x_pos, y_pos), mask=logo)
    canvas = Image.alpha_composite(canvas.convert("RGBA"), transparent)

canvas.convert("RGB").save("marketing_collage.jpg", quality=95)
story_canvas = canvas.resize((1080, 1080))
story_bg = story_canvas.resize((1080, 1920)).filter(ImageFilter.GaussianBlur(30))
story_bg.paste(story_canvas, (0, (1920 - 1080) // 2))
story_bg.convert("RGB").save("story_ready.jpg", quality=80)

print("🎥 جاري إنشاء فيديو الريلز الحركي...")
try:
    with open("ai_result.json", "r", encoding="utf-8") as f: ai_data = json.load(f)
except: ai_data = {}

def draw_text(img_pil, text, y_pos, font_size, alpha):
    if not font_ready: return img_pil
    try:
        bidi_text = get_display(arabic_reshaper.reshape(text))
        font = ImageFont.truetype(font_path, font_size)
        txt_layer = Image.new('RGBA', img_pil.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        try: w = font.getlength(bidi_text)
        except: w = 400
        x_pos = (1080 - w) / 2
        draw.text((x_pos + 4, y_pos + 4), bidi_text, font=font, fill=(0, 0, 0, int(alpha)))
        draw.text((x_pos, y_pos), bidi_text, font=font, fill=(255, 215, 0, int(alpha)))
        return Image.alpha_composite(img_pil.convert('RGBA'), txt_layer).convert('RGB')
    except: return img_pil.convert('RGB')

fps, frames_per_img = 30, 45 
video = cv2.VideoWriter("reel_video_temp.mp4", cv2.VideoWriter_fourcc(*'mp4v'), fps, (1080, 1920))

v_unique = []
for p in [os.path.join(folder_all, f) for f in sorted(os.listdir(folder_all)) if f.lower().endswith(('.png', '.jpg'))]:
    if get_image_hash(p) not in seen: v_unique.append(p)

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
            bg.paste(base.resize((fg_w, fg_h), Image.Resampling.LANCZOS), ((1080 - fg_w) // 2, (1920 - fg_h) // 2))
            ImageDraw.Draw(bg, 'RGBA').rectangle([0, 1640, 1080, 1920], fill=(15, 23, 42, 240))
            if os.path.exists(logo_path):
                logo_r = logo.resize((int(float(logo.width) * (220 / float(logo.height))), 220), Image.Resampling.LANCZOS)
                bg.paste(logo_r, (40, 1670), mask=logo_r)
            alpha = min(255, (frame_idx / 15) * 255)
            text_y = 300 - int(50 * (frame_idx / frames_per_img)) 
            if idx == 0: bg = draw_text(bg, ai_data.get("reel_text_1", "شياكة لا تقاوم!"), text_y, 85, alpha)
            elif idx == len(v_unique) - 1: bg = draw_text(bg, ai_data.get("reel_text_2", "اطلبيها دلوقتي"), text_y, 80, alpha)
            video.write(cv2.cvtColor(np.array(bg), cv2.COLOR_RGB2BGR))
    except: pass
video.release()

print("🎙️ جاري توليد التعليق الصوتي بالذكاء الاصطناعي...")
video_created = False
try:
    script = ai_data.get("voiceover_script", "كوليكشن جديد متاح الآن.")
    subprocess.run(['edge-tts', '--voice', 'ar-EG-SalmaNeural', '--text', script, '--write-media', 'voice.mp3'], check=True)
    result = subprocess.run(["ffmpeg", "-i", "reel_video_temp.mp4", "-i", "voice.mp3", "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", "reel_video.mp4", "-y"], capture_output=True, text=True)
    if result.returncode == 0:
        video_created = True
except Exception as e:
    print(f"⚠️ فشل الصوت: {e}")

if not video_created and os.path.exists("reel_video_temp.mp4"):
    shutil.copy("reel_video_temp.mp4", "reel_video.mp4")

if os.path.exists("reel_video.mp4"):
    print("✅ تم إنشاء ملف الريلز النهائي بنجاح.")
