import os
import json
import shutil
from PIL import Image
from google import genai

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

with open(
    "product.json",
    "r",
    encoding="utf-8"
) as f:
    product = json.load(f)

images = []

for file in product["images"]:

    if os.path.exists(file):

        try:
            images.append(
                Image.open(file)
            )
        except Exception:
            pass

available_images = "\n".join(
    product["images"]
)

prompt = f"""
You are an expert Facebook fashion marketer.

Product code:
{product["product_code"]}

Product description:
{product["description"]}

Available image paths:

{available_images}

IMPORTANT:

- Product description is the primary source of truth.
- Use images only to improve understanding.
- Never invent colors, sizes, fabrics or features.
- Never mention colors unless they are explicitly written in Product description.
- Do not infer colors from images.
- Analyze ALL images.
- Select only the best selling images.
- Do not select more than 4 images.
- Avoid duplicate angles.
- Prefer clear and attractive photos.

VERY IMPORTANT:

best_images must contain ONLY paths from Available image paths.

cover_image must contain ONLY one path from Available image paths.

Do NOT create URLs.
Do NOT create filenames.
Do NOT create image numbers.

Return ONLY valid JSON:

{{
  "facebook_post": "",
  "facebook_post_short": "",
  "hashtags": [],
  "story_post": "",
  "reel_idea": "",
  "best_images": [],
  "cover_image": ""
}}
"""

contents = images + [prompt]

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents
)

result = response.text

print("\nRAW_RESPONSE:\n")
print(result)

with open(
    "ai_result.json",
    "w",
    encoding="utf-8"
) as f:
    f.write(result)

clean_result = result.strip()

if clean_result.startswith("```json"):
    clean_result = clean_result.replace(
        "```json",
        "",
        1
    )

if clean_result.endswith("```"):
    clean_result = clean_result[:-3]

clean_result = clean_result.strip()

data = json.loads(
    clean_result
)

with open(
    "facebook_post.txt",
    "w",
    encoding="utf-8"
) as f:
    f.write(
        data.get(
            "facebook_post",
            ""
        )
    )

with open(
    "facebook_post_short.txt",
    "w",
    encoding="utf-8"
) as f:
    f.write(
        data.get(
            "facebook_post_short",
            ""
        )
    )

with open(
    "story_post.txt",
    "w",
    encoding="utf-8"
) as f:
    f.write(
        data.get(
            "story_post",
            ""
        )
    )

with open(
    "reel_idea.txt",
    "w",
    encoding="utf-8"
) as f:
    f.write(
        data.get(
            "reel_idea",
            ""
        )
    )

os.makedirs(
    "selected_images",
    exist_ok=True
)

for image_path in data.get(
    "best_images",
    []
):

    if os.path.exists(
        image_path
    ):

        shutil.copy(
            image_path,
            os.path.join(
                "selected_images",
                os.path.basename(
                    image_path
                )
            )
        )

cover_image = data.get(
    "cover_image",
    ""
)

if (
    cover_image
    and os.path.exists(
        cover_image
    )
):

    shutil.copy(
        cover_image,
        "cover_image.jpg"
    )

print(
    "\nFILES_CREATED:\n"
)

print("ai_result.json")
print("facebook_post.txt")
print("facebook_post_short.txt")
print("story_post.txt")
print("reel_idea.txt")
print("selected_images/")
print("cover_image.jpg")
