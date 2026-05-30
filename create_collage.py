from PIL import Image
import os

folder = "selected_images"

if not os.path.exists(folder):
    raise Exception(
        "selected_images folder not found"
    )

images = []

for file in sorted(os.listdir(folder)):

    path = os.path.join(
        folder,
        file
    )

    try:
        images.append(
            Image.open(path)
            .convert("RGB")
        )
    except Exception:
        pass

if len(images) == 0:

    raise Exception(
        "No images found"
    )

while len(images) < 4:

    images.append(
        images[-1].copy()
    )

canvas = Image.new(
    "RGB",
    (1200, 1200),
    "white"
)

positions = [
    (0, 0),
    (600, 0),
    (0, 600),
    (600, 600)
]

for img, pos in zip(
    images[:4],
    positions
):

    img = img.resize(
        (600, 600)
    )

    canvas.paste(
        img,
        pos
    )

canvas.save(
    "marketing_collage.jpg",
    quality=95
)

print(
    f"Collage created using {len(images[:4])} images"
)
