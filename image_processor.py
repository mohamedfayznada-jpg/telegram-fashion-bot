import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

folder_selected = "selected_images"
folder_all = "downloads"

if not os.path.exists(folder_selected) or not os.path.exists(folder_all):
    raise Exception("Folders not found! Make sure 'selected_images' and 'downloads' exist.")

# ==========================================
# 1. إنشاء الكولاچ (للبوست والستوري)
# ==========================================
print("⏳ جاري إنشاء كولاچ الصور الأساسي...")
images_collage = []
for file in sorted(os.listdir(folder_selected)):
    path = os.path.join(folder_selected, file)
    try:
        images_collage.append(Image.open(path).convert("RGB"))
    except: pass

images_collage = images_collage[:4]
canvas = Image.new("RGB", (1200, 1200), "white")

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

# الشريط السفلي واللوجو للكولاچ
draw = ImageDraw.Draw(canvas, "RGBA")
footer_height = 100
draw.rectangle([0, 1200 - footer_height, 1200, 1200], fill=(15, 23, 42, 240))

logo_path = "logo.png"
if os.path.exists(logo_path):
    logo = Image.open(logo_path).convert("RGBA")
    logo_th = 65
    w_percent = (logo_th / float(logo.height))
    logo_tw = int((float(logo.width) * float(w_percent)))
    logo = logo.resize((logo_tw, logo_th), Image.Resampling.LANCZOS)
    x_pos = (1200 - logo_tw) // 2
    y_pos = 1200 - footer_height + 17
    transparent = Image.new('RGBA', canvas.size, (0,0,0,0))
    transparent.paste(logo, (x_pos, y_pos), mask=logo)
    canvas = Image.alpha_composite(canvas.convert("RGBA"), transparent)

canvas.convert("RGB").save("marketing_collage.jpg", quality=95)
print("✅ تم تجهيز صورة الكولاچ!")

# ==========================================
# 2. إنشاء فيديو الريلز من كل الصور
# ==========================================
print("🎥 جاري إنشاء فيديو الريلز (Slideshow) من جميع الصور...")
video_path = "reel_video.mp4"
width, height = 1080, 1920
fps = 30
frames_per_image = 75 # يعني كل صورة هتتعرض 2.5 ثانية

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

all_images = [os.path.join(folder_all, f) for f in sorted(os.listdir(folder_all)) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

for img_path in all_images:
    try:
        base_img = Image.open(img_path).convert("RGB")
        
        # عمل خلفية ضبابية (Blur) تملأ الشاشة بالطول
        bg = base_img.resize((height, height)).crop(((height-width)//2, 0, (height+width)//2, height))
        bg = bg.filter(ImageFilter.GaussianBlur(radius=40))
        dark_overlay = Image.new('RGBA', bg.size, (0,0,0, 80))
        bg = Image.alpha_composite(bg.convert('RGBA'), dark_overlay).convert('RGB')
        
        # تظبيط مقاس الفستان في النص
        fg_w = width
        fg_h = int((float(base_img.height) * (width / float(base_img.width))))
        if fg_h > height - 200:
            fg_h = height - 200
            fg_w = int((float(base_img.width) * (fg_h / float(base_img.height))))
            
        fg = base_img.resize((fg_w, fg_h), Image.Resampling.LANCZOS)
        y_offset = (height - fg_h) // 2 - 50
        x_offset = (width - fg_w) // 2
        bg.paste(fg, (x_offset, y_offset))
        
        # إضافة الشريط واللوجو في الفيديو
        v_draw = ImageDraw.Draw(bg, 'RGBA')
        v_draw.rectangle([0, height - 150, width, height], fill=(15, 23, 42, 240))
        if os.path.exists(logo_path):
            vx_pos = (width - logo_tw) // 2
            vy_pos = height - 150 + (150 - logo_th) // 2
            bg.paste(logo, (vx_pos, vy_pos), mask=logo)
            
        # تحويل الصورة لفريم فيديو
        frame = np.array(bg)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        for _ in range(frames_per_image):
            video.write(frame)
    except Exception as e:
        print(f"⚠️ خطأ في معالجة إحدى صور الفيديو: {e}")

video.release()
print("✅ تم إنشاء فيديو الريلز بنجاح!")
