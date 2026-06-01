import os
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

folder = "selected_images"
if not os.path.exists(folder):
    raise Exception("selected_images folder not found")

images = []
print("⏳ جاري تجميع الصور الأصلية وإنشاء تصميم المجلة...")

for file in sorted(os.listdir(folder)):
    path = os.path.join(folder, file)
    try:
        images.append(Image.open(path).convert("RGB"))
    except Exception as e:
        print(f"⚠️ خطأ في قراءة {file}: {e}")

if len(images) == 0:
    print("No images found")
    exit(0)

# تجميع أفضل 4 صور
images = images[:4]
canvas = Image.new("RGB", (1200, 1200), "white")

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

# ==========================================
# اللمسة الاحترافية: شريط سفلي (Footer) لإخفاء العيوب وإضافة التوقيع
# ==========================================
draw = ImageDraw.Draw(canvas, "RGBA")
footer_height = 90

# رسم شريط داكن بعرض الصورة من الأسفل (يغطي أي نصوص قديمة)
draw.rectangle(
    [0, 1200 - footer_height, 1200, 1200],
    fill=(15, 23, 42, 240) # لون كحلي/أسود أنيق جداً
)

# النص اللي هيتكتب جوه الشريط
text = "مُحَمَّد فَايِز   |   F A S T Y L E"
reshaped = arabic_reshaper.reshape(text)
bidi_text = get_display(reshaped)

# إعداد الخط الذهبي
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
try:
    font = ImageFont.truetype(font_path, 34)
except:
    font = ImageFont.load_default()

# حساب مكان النص ليكون في المنتصف
try:
    text_width = font.getlength(bidi_text)
except:
    text_width = 400

x_pos = (1200 - text_width) / 2
y_pos = 1200 - footer_height + 25

# طباعة النص
draw.text((x_pos, y_pos), bidi_text, fill=(218, 165, 32, 255), font=font)

canvas.convert("RGB").save("marketing_collage.jpg", quality=95)
print("🎉 تم إنشاء الكولاچ بتصميم المجلات الاحترافي!")
