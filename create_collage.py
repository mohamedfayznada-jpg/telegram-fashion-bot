from PIL import Image
import os

folder = "selected_images"

if not os.path.exists(folder):
    raise Exception("selected_images folder not found")

images = []

for file in sorted(os.listdir(folder)):
    path = os.path.join(folder, file)
    try:
        images.append(Image.open(path).convert("RGB"))
    except Exception:
        pass

if len(images) == 0:
    print("No images found")
    exit(0)

# نأخذ أقصى حاجة 4 صور
images = images[:4]
canvas = Image.new("RGB", (1200, 1200), "white")

# تقسيم ديناميكي بناءً على عدد المتاح من الصور عشان نمنع التكرار
if len(images) == 1:
    img = images[0].resize((1200, 1200))
    canvas.paste(img, (0, 0))

elif len(images) == 2:
    img1 = images[0].resize((600, 1200))
    img2 = images[1].resize((600, 1200))
    canvas.paste(img1, (0, 0))
    canvas.paste(img2, (600, 0))

elif len(images) == 3:
    img1 = images[0].resize((1200, 600))
    img2 = images[1].resize((600, 600))
    img3 = images[2].resize((600, 600))
    canvas.paste(img1, (0, 0))
    canvas.paste(img2, (0, 600))
    canvas.paste(img3, (600, 600))

elif len(images) == 4:
    positions = [(0, 0), (600, 0), (0, 600), (600, 600)]
    for img, pos in zip(images, positions):
        img = img.resize((600, 600))
        canvas.paste(img, pos)

canvas.save("marketing_collage.jpg", quality=95)
print(f"Collage created using {len(images)} images dynamically.")
