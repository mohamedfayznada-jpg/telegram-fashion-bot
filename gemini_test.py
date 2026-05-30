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

prompt = f"""
You are an expert Facebook fashion marketer.

Product code:
{product["product_code"]}

Product description:
{product["description"]}

IMPORTANT:

- Product description is the primary source of truth.
- Use images only to improve understanding.
- Do not invent colors, sizes, fabrics or features not mentioned in the description.
- Analyze ALL images.
- Select only the best selling images.
- Do not select more than 4 images.
- Avoid duplicate angles.
- Prefer clear and attractive photos.

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
