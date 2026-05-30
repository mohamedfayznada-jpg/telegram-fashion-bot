import os
import json
from PIL import Image
from google import genai

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

images = []

for file in [
    "downloads/199024.jpg",
    "downloads/199025.jpg",
    "downloads/199026.jpg"
]:
    if os.path.exists(file):
        images.append(Image.open(file))

prompt = """
ارجع JSON فقط بالشكل التالي:

{
  "facebook_post":"",
  "hashtags":[],
  "story_post":"",
  "reel_idea":"",
  "best_images":[]
}
"""

contents = images + [prompt]

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents
)

print(response.text)

with open(
    "ai_result.json",
    "w",
    encoding="utf-8"
) as f:
    f.write(response.text)
