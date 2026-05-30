from PIL import Image
import os

images = []

folder = "selected_images"

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

if len(images) < 4:

    raise Exception(
        "Need at least 4 images"
    )

size = (1200, 1200)

canvas = Image.new(
    "RGB",
    size,
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
    "marketing_collage.jpg created"
)
