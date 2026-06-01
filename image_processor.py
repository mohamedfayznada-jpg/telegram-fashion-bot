import os
import io
from PIL import Image, ImageDraw, ImageFont
from rembg import remove
import arabic_reshaper
from bidi.algorithm import get_display

folder = "selected_images"
if not os.path.exists(folder):
    raise Exception("selected_images folder not found")

# لون خلفية الاستوديو (بيج فاتح راقي يناسب الفاشون)
STUDIO_BG_COLOR = (248, 245, 242)

images = []
print("⏳ جاري تفريغ الخلفيات بالذكاء الاصطناعي...")

for file in sorted(os.listdir(folder)):
    path = os.path.join(folder, file)
    try:
        # قراءة الصورة
        with open(path, 'rb') as i:
            input_data = i.read()
        
        # إزالة الخلفية الأصلية (وأي كتابات عليها)
        output_data = remove(input_data)
        dress_img = Image.open(io.BytesIO(output_data)).convert("RGBA")
        
        # إنشاء خلفية استوديو جديدة
        studio_bg = Image.new("RGBA", dress_img.size, STUDIO_BG_COLOR)
        # دمج الفستان مع الخلفية الجديدة
        studio_bg.paste(dress_img, (0, 0), dress_img)
        
        images.append(studio_bg.convert("RGB"))
        print(f"✅ تم معالجة الصورة: {file}")
    except Exception as e:
        print(f"⚠️ خطأ في معالجة {file}: {e}")

if len(images) == 0:
    print("No images found")
    exit(0)

# أخذ أفضل 4 صور فقط
images = images[:4]
canvas = Image.new("RGB", (1200, 1200), STUDIO_BG_COLOR)

# ترتيب الكولاچ
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

# --- رسم الختم البصري الذكي (مُحَمَّد فَايِز) في أسفل اليسار ---
draw = ImageDraw.Draw(canvas, "RGBA")
badge_w, badge_h = 240, 55
bx1, by1 = 30, 1200 - 30 - badge_h
bx2, by2 = bx1 + badge_w, by1 + badge_h

draw.rounded_rectangle([bx1, by1, bx2, by2], radius=15, fill=(15, 23, 42, 180), outline=(218, 165, 32, 220), width=2)[cite: 1]

text = "مُحَمَّد فَايِز"[cite: 1]
reshaped = arabic_reshaper.reshape(text)[cite: 1]
bidi_text = get_display(reshaped)[cite: 1]

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"[cite: 1]
if os.path.exists(font_path):[cite: 1]
    font = ImageFont.truetype(font_path, 22)[cite: 1]
else:[cite: 1]
    font = ImageFont.load_default()[cite: 1]

draw.text((bx1 + 35, by1 + 10), bidi_text, fill=(255, 215, 0, 255), font=font)[cite: 1]
# -------------------------------

canvas.save("marketing_collage.jpg", quality=95)
print("🎉 تم إنشاء الكولاچ الاستوديو بنجاح!")
