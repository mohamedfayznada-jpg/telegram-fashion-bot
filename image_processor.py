import os
from PIL import Image, ImageDraw

folder = "selected_images"
if not os.path.exists(folder):
    raise Exception("selected_images folder not found")

images = []
print("⏳ جاري تجميع الصور وتجهيز الكولاچ...")

for file in sorted(os.listdir(folder)):
    path = os.path.join(folder, file)
    try:
        images.append(Image.open(path).convert("RGB"))
    except Exception as e:
        print(f"⚠️ خطأ في قراءة {file}: {e}")

if len(images) == 0:
    print("No images found")
    exit(0)

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
# الشريط السفلي (Footer) + اللوجو
# ==========================================
draw = ImageDraw.Draw(canvas, "RGBA")
footer_height = 100

# رسم شريط داكن بعرض الصورة من الأسفل
draw.rectangle(
    [0, 1200 - footer_height, 1200, 1200],
    fill=(15, 23, 42, 240) # لون داكن أنيق
)

# دمج اللوجو داخل الشريط (بدل النص العربي اللي بيبوظ)
logo_path = "logo.png"
if os.path.exists(logo_path):
    logo = Image.open(logo_path).convert("RGBA")
    
    # تصغير اللوجو ليكون مناسب لارتفاع الشريط
    logo_target_height = 70
    w_percent = (logo_target_height / float(logo.height))
    logo_target_width = int((float(logo.width) * float(w_percent)))
    logo = logo.resize((logo_target_width, logo_target_height), Image.Resampling.LANCZOS)
    
    # وضع اللوجو في الجانب الأيسر داخل الشريط
    x_pos = 40
    y_pos = 1200 - footer_height + 15
    
    transparent = Image.new('RGBA', canvas.size, (0,0,0,0))
    transparent.paste(logo, (x_pos, y_pos), mask=logo)
    canvas = Image.alpha_composite(canvas.convert("RGBA"), transparent)

canvas.convert("RGB").save("marketing_collage.jpg", quality=95)
print("🎉 تم إنشاء الكولاچ ووضع اللوجو بنجاح!")
