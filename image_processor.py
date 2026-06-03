import os
import cv2
import json
import hashlib
import requests
import random
import shutil
import subprocess
import glob
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

if os.path.exists("skip_flag.txt"): exit(0)

folder_selected = "selected_images"
folder_all = "downloads"
processed_folder = "processed_images"
ready_reels_folder = "ready_reels"

os.makedirs(processed_folder, exist_ok=True)
os.makedirs(ready_reels_folder, exist_ok=True)

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

print("⏳ جاري معالجة الصور الفردية للكاروسيل...")
seen = set()
processed_files = []

for idx, file in enumerate(sorted(os.listdir(folder_selected))):
    path = os.path.join(folder_selected, file)
    h = get_image_hash(path)
    if h not in seen:
        seen.add(h)
        try:
            img = Image.open(path).convert("RGB")
            bg = img.resize((1080, 1080)).filter(ImageFilter.GaussianBlur(30))
            img_ratio = img.width / img.height
            if img_ratio > 1: new_w, new_h = 1080, int(1080 / img_ratio)
            else: new_w, new_h = int(1080 * img_ratio), 1080
            bg.paste(img.resize((new_w, new_h), Image.Resampling.LANCZOS), ((1080 - new_w) // 2, (1080 - new_h) // 2))
            
            logo_path = "logo.png"
            if os.path.exists(logo_path):
                logo = Image.open(logo_path).convert("RGBA")
                logo_h = 120
                logo_w = int(float(logo.width) * (logo_h / float(logo.height)))
                logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
                x_pos, y_pos = 30, 1080 - logo_h - 30
                aura = Image.new('RGBA', bg.size, (0, 0, 0, 0))
                ImageDraw.Draw(aura).ellipse([x_pos-10, y_pos-10, x_pos+logo_w+10, y_pos+logo_h+10], fill=(255, 255, 255, 120))
                bg = Image.alpha_composite(bg.convert("RGBA"), aura.filter(ImageFilter.GaussianBlur(10)))
                transparent = Image.new('RGBA', bg.size, (0, 0, 0, 0))
                transparent.paste(logo, (x_pos, y_pos), mask=logo)
                bg = Image.alpha_composite(bg.convert("RGBA"), transparent).convert("RGB")

            out_path = os.path.join(processed_folder, f"img_{idx}.jpg")
            bg.save(out_path, quality=95)
            processed_files.append(out_path)
        except Exception as e: print(f"⚠️ خطأ في معالجة {file}: {e}")

print("🎥 جاري البحث عن فيديوهات أصلية للموديل...")
original_videos = glob.glob(os.path.join(folder_all, "*.mp4"))

if len(original_videos) > 0:
    print(f"🎬 ممتاز! تم العثور على {len(original_videos)} فيديوهات أصلية، سيتم استخدامها كـ Reels.")
    for i, vid in enumerate(original_videos):
        shutil.copy(vid, os.path.join(ready_reels_folder, f"original_reel_{i}.mp4"))
else:
    print("🛠️ لم يتم العثور على فيديوهات أصلية، سيتم إنشاء فيديو حركي بالذكاء الاصطناعي...")
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

    for idx, img_path in enumerate(processed_files):
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
                
                alpha = min(255, (frame_idx / 15) * 255)
                text_y = 300 - int(50 * (frame_idx / frames_per_img)) 
                if idx == 0: bg = draw_text(bg, ai_data.get("reel_text_1", "كوليكشن جديد"), text_y, 85, alpha)
                elif idx == len(processed_files) - 1: bg = draw_text(bg, ai_data.get("reel_text_2", "اطلبيها دلوقتي"), text_y, 80, alpha)
                video.write(cv2.cvtColor(np.array(bg), cv2.COLOR_RGB2BGR))
        except: pass
    video.release()

    try:
        script = ai_data.get("voiceover_script", "كوليكشن جديد متاح الآن.")
        subprocess.run(['edge-tts', '--voice', 'ar-EG-SalmaNeural', '--text', script, '--write-media', 'voice.mp3'], check=True)
        res = subprocess.run(["ffmpeg", "-i", "reel_video_temp.mp4", "-i", "voice.mp3", "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", os.path.join(ready_reels_folder, "generated_reel.mp4"), "-y"], capture_output=True)
    except:
        if os.path.exists("reel_video_temp.mp4"): shutil.copy("reel_video_temp.mp4", os.path.join(ready_reels_folder, "generated_reel.mp4"))
