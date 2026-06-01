import os
import cv2
import numpy as np
import hashlib
from PIL import Image, ImageDraw, ImageFilter

folder_selected = "selected_images"
folder_all = "downloads"

if not os.path.exists(folder_selected) or not os.path.exists(folder_all):
    print("⚠️ لم يتم العثور على مجلدات الصور.")
    exit(0)

# ==========================================
# 1. إزالة الصور المتكررة (Deduplication)
# ==========================================
def get_image_hash(filepath):
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

print("⏳ جاري تنظيف الصور وإزالة التكرارات...")
unique_images = []
seen_hashes = set()
for file in sorted(os.listdir(folder_selected)):
    path = os.path.join(folder_selected, file)
    try:
        img_hash = get_image_hash(path)
        if img_hash not in seen_hashes:
            seen_hashes.add(img_hash)
            unique_images.append(Image.open(path).convert("RGB"))
    except Exception as e:
        pass

if not unique_images:
    print("❌ لم يتم العثور على صور صالحة.")
    exit(0)

images_collage = unique_images[:4]
canvas = Image.new("RGB", (1200, 1200), "white")

# ==========================================
# 2. إنشاء الكولاچ بناءً على عدد الصور
# ==========================================
if len(images_collage) == 1:
    canvas.paste(images_collage[0].resize((1200, 1200)), (0, 0))
elif len(images_collage) == 2:
    canvas.paste(images_collage[0].resize((600, 1200)), (0, 0))
    canvas.paste(images_collage[1].resize((600, 1200)), (600, 0))
elif len(images_collage) == 3:
    canvas.paste(images_collage[0].resize((1200, 600)), (0, 0))
    canvas.paste(images_collage[1].resize((600, 600)), (0, 600))
    canvas.paste(images_collage[2].resize((600, 600)), (600, 600))
elif len(images_collage) == 4:
    positions = [(0, 0), (600, 0), (0, 600), (600, 600)]
    for img, pos in zip(images_collage, positions):
        canvas.paste(img.resize((600, 600)), pos)

# رسم الشريط السفلي الداكن
draw = ImageDraw.Draw(canvas, "RGBA")
footer_height = 100
draw.rectangle([0, 1200 - footer_height, 1200, 1200], fill=(15, 23, 42, 240))

# إضافة الختم/اللوجو في الزاوية اليسرى السفلية
logo_path = "logo.png"
if os.path.exists(logo_path):
    logo = Image.open(logo_path).convert("RGBA")
    logo_th = 65
    w_percent = (logo_th / float(logo.height))
    logo_tw = int((float(logo.width) * float(w_percent)))
    logo = logo.resize((logo_tw, logo_th), Image.Resampling.LANCZOS)
    
    # الزاوية اليسرى السفلية
    x_pos = 30
    y_pos = 1200 - footer_height + 17
    
    transparent = Image.new('RGBA', canvas.size, (0,0,0,0))
    transparent.paste(logo, (x_pos, y_pos), mask=logo)
    canvas = Image.alpha_composite(canvas.convert("RGBA"), transparent)

canvas.convert("RGB").save("marketing_collage.jpg", quality=95)
print("✅ تم تجهيز صورة الكولاچ الأساسية.")

# ==========================================
# 3. تجهيز صورة مخصصة للستوري (1080x1920)
# ==========================================
story_canvas = canvas.resize((1080, 1080))
story_bg = story_canvas.resize((1080, 1920)).filter(ImageFilter.GaussianBlur(30))
story_bg.paste(story_canvas, (0, (1920 - 1080) // 2))
story_bg.convert("RGB").save("story_ready.jpg", quality=95)
print("✅ تم تجهيز صورة الستوري المتوافقة مع فيسبوك.")

# ==========================================
# 4. إنشاء فيديو الريلز (Slideshow)
# ==========================================
print("🎥 جاري إنشاء فيديو الريلز من جميع الصور بدون تكرار...")
video_path = "reel_video.mp4"
width, height = 1080, 1920
fps, frames_per_image = 30, 75 # 2.5 ثانية لكل صورة
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

all_img_paths = [os.path.join(folder_all, f) for f in sorted(os.listdir(folder_all)) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

# فلترة الصور للفيديو أيضاً لمنع التكرار
unique_video_imgs = []
v_seen = set()
for p in all_img_paths:
    h = get_image_hash(p)
    if h not in v_seen:
        v_seen.add(h)
        unique_video_imgs.append(p)

for img_path in unique_video_imgs:
    try:
        base_img = Image.open(img_path).convert("RGB")
        
        # خلفية ضبابية
        bg = base_img.resize((height, height)).crop(((height-width)//2, 0, (height+width)//2, height)).filter(ImageFilter.GaussianBlur(40))
        dark = Image.new('RGBA', bg.size, (0,0,0, 80))
        bg = Image.alpha_composite(bg.convert('RGBA'), dark).convert('RGB')
        
        # ضبط مقاس الصورة الأصلية في المنتصف
        fg_w = width
        fg_h = int((float(base_img.height) * (width / float(base_img.width))))
        if fg_h > height - 200:
            fg_h = height - 200
            fg_w = int((float(base_img.width) * (fg_h / float(base_img.height))))
            
        fg = base_img.resize((fg_w, fg_h), Image.Resampling.LANCZOS)
        bg.paste(fg, ((width - fg_w) // 2, (height - fg_h) // 2 - 50))
        
        # إضافة الشريط والختم للريلز
        v_draw = ImageDraw.Draw(bg, 'RGBA')
        v_draw.rectangle([0, height - 150, width, height], fill=(15, 23, 42, 240))
        if os.path.exists(logo_path):
            bg.paste(logo, (30, height - 150 + (150 - logo_th) // 2), mask=logo)
            
        frame = cv2.cvtColor(np.array(bg), cv2.COLOR_RGB2BGR)
        for _ in range(frames_per_image):
            video.write(frame)
    except Exception as e:
        print(f"⚠️ خطأ في معالجة إحدى صور الفيديو: {e}")

video.release()
print("✅ تم إنشاء فيديو الريلز بنجاح!")
