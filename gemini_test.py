import os
import json
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

available_images = "\n".join(product["images"])

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
- Analyze ALL images.
- Select only the best selling images.
- Do not select more than 4 images.
- Avoid duplicate angles.
- Prefer clear and attractive photos.

VERY IMPORTANT:

best_images must contain ONLY paths from Available image paths.
Never mention colors unless they are explicitly written in Product description.

Do not infer colors from images.
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

print(result)

with open(
    "ai_result.json",
    "w",
    encoding="utf-8"
) as f:
    f.write(result)
