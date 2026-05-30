import os
import json
import shutil
from PIL import Image
from google import genai
PROCESSED_FILE = (
    "processed_products.json"
)
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

STRICT RULES:

- Product description is the ONLY source of truth.
- Images are used only for selecting the best photos.
- NEVER invent colors.
- NEVER invent sizes.
- NEVER invent materials.
- NEVER invent discounts.
- NEVER invent offers.
- NEVER invent stock availability.
- NEVER invent customer benefits not explicitly mentioned.
- NEVER invent product details from image analysis.

If information is not written in Product description,
DO NOT mention it.

customer_questions must only contain questions that can be answered from existing product data.

selling_points must only contain facts explicitly written in Product description.

facebook posts must never mention:

- discounts
- offers
- limited stock
- free shipping
- colors unless explicitly written
- features not present in description

IMPORTANT LANGUAGE RULE:

All generated content must be written in Egyptian Arabic.

facebook_post_soft must be Egyptian Arabic.
facebook_post_sales must be Egyptian Arabic.
facebook_post_viral must be Egyptian Arabic.
facebook_post_short must be Egyptian Arabic.
story_post must be Egyptian Arabic.
reel_idea must be Egyptian Arabic.

Do not use English except product code.

VERY IMPORTANT:

best_images must contain ONLY paths from Available image paths.

carousel_order must contain ONLY paths from Available image paths.

cover_image must contain ONLY one path from Available image paths.

Do NOT create URLs.
Do NOT create filenames.
Do NOT create image numbers.

facebook_post_soft:
Friendly and elegant post.

facebook_post_sales:
Strong sales-oriented post with urgency and call to action.

facebook_post_viral:
Engagement-focused post designed to generate comments and reactions.

selling_points:
List the strongest selling points.

customer_questions:
List the most likely customer questions.

carousel_order:
Return the best image order for Facebook carousel.

Return ONLY valid JSON:

{{
  "facebook_post_soft": "",
  "facebook_post_sales": "",
  "facebook_post_viral": "",

  "facebook_post_short": "",

  "hashtags": [],

  "story_post": "",

  "reel_idea": "",

  "selling_points": [],

  "customer_questions": [],

  "carousel_order": [],

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

try:

    data = json.loads(
        clean_result
    )

except Exception as e:

    print(
        "\nJSON ERROR:\n"
    )

    print(
        clean_result
    )

    raise e

marketing_package = {
    "product_code":
        product["product_code"],

    "cover_image":
        data.get(
            "cover_image",
            ""
        ),

    "best_images":
        data.get(
            "best_images",
            []
        ),

    "facebook_post_soft":
        data.get(
            "facebook_post_soft",
            ""
        ),

    "facebook_post_sales":
        data.get(
            "facebook_post_sales",
            ""
        ),

    "facebook_post_viral":
        data.get(
            "facebook_post_viral",
            ""
        ),

    "facebook_post_short":
        data.get(
            "facebook_post_short",
            ""
        ),

    "story_post":
        data.get(
            "story_post",
            ""
        ),

    "reel_idea":
        data.get(
            "reel_idea",
            ""
        ),

    "selling_points":
        data.get(
            "selling_points",
            []
        ),

    "customer_questions":
        data.get(
            "customer_questions",
            []
        ),

    "carousel_order":
        data.get(
            "carousel_order",
            []
        )
}

with open(
    "marketing_package.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        marketing_package,
        f,
        ensure_ascii=False,
        indent=2
    )

if len(data.get("best_images", [])) > 4:
    data["best_images"] = data["best_images"][:4]

if len(data.get("carousel_order", [])) > 4:
    data["carousel_order"] = data["carousel_order"][:4]
with open(
    "facebook_post_soft.txt",
    "w",
    encoding="utf-8"
) as f:
    f.write(
        data.get(
            "facebook_post_soft",
            ""
        )
    )

with open(
    "facebook_post_sales.txt",
    "w",
    encoding="utf-8"
) as f:
    f.write(
        data.get(
            "facebook_post_sales",
            ""
        )
    )

with open(
    "facebook_post_viral.txt",
    "w",
    encoding="utf-8"
) as f:
    f.write(
        data.get(
            "facebook_post_viral",
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

with open(
    "selling_points.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        data.get(
            "selling_points",
            []
        ),
        f,
        ensure_ascii=False,
        indent=2
    )

with open(
    "customer_questions.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        data.get(
            "customer_questions",
            []
        ),
        f,
        ensure_ascii=False,
        indent=2
    )

with open(
    "carousel_order.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        data.get(
            "carousel_order",
            []
        ),
        f,
        ensure_ascii=False,
        indent=2
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
print("facebook_post_soft.txt")
print("facebook_post_sales.txt")
print("facebook_post_viral.txt")
print("facebook_post_short.txt")
print("story_post.txt")
print("reel_idea.txt")
print("selling_points.json")
print("customer_questions.json")
print("carousel_order.json")
print("selected_images/")
print("cover_image.jpg")
