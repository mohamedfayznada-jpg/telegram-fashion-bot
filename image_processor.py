import os
import io
import random
from PIL import Image, ImageDraw, ImageFont
from rembg import remove
import arabic_reshaper
from bidi.algorithm import get_display

folder = "selected_images"
bg_folder = "backgrounds" # المجلد اللي هتحط فيه صور الخلفيات الاحترافية

if not os.path.exists(folder):
    raise Exception("selected_images folder not found")

# ألوان استوديو راقية جداً (بديل لو مجلد الخلفيات فاضي)
# (بيج فاتح، كشمير هادي، رمادي فاتح، أبيض كريمي)
FALLBACK_COLORS = [(248, 245, 242), (242, 235, 235), (230, 230, 235), (255, 253, 248)]

images = []
print("⏳ جاري تفريغ الخلفيات ودمجها في بيئات احترافية...")

for file in sorted(os.listdir(folder)):
    path = os.path.join(folder, file)
    try:
        # 1. قراءة وتفريغ الصورة
        with open(path, 'rb') as i:
            input_data = i.read()
        
        output_data = remove(input_data)
        dress_img = Image.open(io.BytesIO(output_data)).convert("RGBA")
        
        # 2. اختيار الخلفية (صورة حقيقية أو لون استوديو)
        if os.path.exists(bg_folder) and len(os.listdir(bg_folder)) > 0:
            # اختيار خلفية عشوائية من المجلد
            bg_file = random.choice(os.listdir(bg_folder))
            bg_path = os.path.join(bg_folder, bg_file)
            bg = Image.open(bg_path).convert("RGBA")
            # تظبيط مقاس الخلفية عشان تبقى على قد الفستان بالظبط
            bg = bg.resize(dress_img.size, Image.Resampling.LANCZOS)
        else:
            # لو مفيش صور، نختار لون استوديو عشوائي
            color = random.choice(FALLBACK_COLORS)
            bg = Image.new("RGBA", dress_img.size, color)
        
        # 3. الدمج السحري
        bg.paste(dress_img, (0, 0), dress_img)
        images.append(bg.convert("RGB"))
        print(f"✅ تم دمج الصورة ببيئة جديدة: {file}")
    except Exception as e:
        print(f"⚠️ خطأ في معالجة {file}: {e}")

if len(images) == 0:
    print("No images found")
    exit(0)

# تجميع الصور في الكولاچ (حد أقصى 4)
images = images[:4]
canvas = Image.new("RGB", (1200, 1200), (255, 255, 255))

if len(images) == 1:
    canvas.paste(images[0].resize((1200, 1200)), (0, 0))
elif len(images) == 2:
    canvas.paste(images[0].resize((600, 1200)), (0, 0))
    canvas.paste(images[1].resize((600, 1200)), (600, 0))
elif len(images) == 3:
    canvas.paste(images[0].resize((1200, 600)), (0, 0))
    canvas.paste(images[1].resize((600, 600)), (0, 600))
    canvas.paste(images[2].resize((600, 600)), (600, 600))
elif len(images) == 4:
    positions = [(0, 0), (600, 0), (0, 600), (600, 600)]
    for img, pos in zip(images, positions):
        canvas.paste(img.resize((600, 600)), pos)

# --- رسم الختم البصري الذكي (مُحَمَّد فَايِز) ---
draw = ImageDraw.Draw(canvas, "RGBA")
badge_w, badge_h = 240, 55
bx1, by1 = 30, 1200 - 30 - badge_h
bx2, by2 = bx1 + badge_w, by1 + badge_h

draw.rounded_rectangle([bx1, by1, bx2, by2], radius=15, fill=(15, 23, 42, 180), outline=(218, 165, 32, 220), width=2)

text = "مُحَمَّد فَايِز"
reshaped = arabic_reshaper.reshape(text)
bidi_text = get_display(reshaped)

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
if os.path.exists(font_path):
    font = ImageFont.truetype(font_path, 22)
else:
    font = ImageFont.load_default()

draw.text((bx1 + 35, by1 + 10), bidi_text, fill=(255, 215, 0, 255), font=font)
# -------------------------------

canvas.save("marketing_collage.jpg", quality=95)
print("🎉 تم إنشاء الكولاچ الاستوديو بنجاح!")
