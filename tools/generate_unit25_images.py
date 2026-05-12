"""
Generate AI images for Book 2 Unit 25 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit25_images.py
"""

import base64
import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.book import Word, Unit, Book

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_IMAGE_MODEL", "google/gemini-3.1-flash-image-preview")
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit25")

WORD_PROMPTS = {
    "atom":      "A scientific illustration of an atom showing a nucleus with orbiting electrons, glowing against a dark background. Realistic 3D rendering.",
    "beautiful": "A breathtaking colorful sunset over a calm ocean with golden and pink clouds. Realistic photo, peaceful scene.",
    "breadth":   "A tape measure stretched across the breadth of a long wall, showing horizontal width measurement. Realistic close-up photo.",
    "comet":     "A bright comet streaking across the dark night sky with a long glowing tail of dust and ice. Realistic space photo.",
    "cover":     "A satellite view of Earth covered in thick swirling white clouds. Realistic photo from space.",
    "despair":   "A person sitting alone on the floor with head in hands, surrounded by darkness, expressing deep despair. Realistic photo, dim lighting.",
    "form":      "Two hands pressing clay together to form a new sculpture on a pottery wheel. Realistic close-up photo, workshop setting.",
    "fragment":  "Scattered shards and small fragments of broken glass on a wooden floor. Realistic close-up photo, dramatic lighting.",
    "galaxy":    "A spiral galaxy in deep space with millions of stars and swirling arms of cosmic dust. Realistic space photo, vibrant colors.",
    "gloom":     "A foggy gloomy morning on a lake with mist hanging low over the dark water. Realistic photo, melancholy mood.",
    "large":     "A very large elephant in a savanna next to a small bird, showing dramatic size difference. Realistic wildlife photo.",
    "moon":      "A full bright moon shining in a clear starry night sky over a quiet landscape. Realistic photo, beautiful detail.",
    "radiate":   "A glowing fireplace radiating warm orange light and heat throughout a cozy living room. Realistic photo.",
    "roam":      "A herd of cows wandering and roaming freely across a wide green pasture. Realistic photo, daytime.",
    "solitary":  "A single solitary chair standing alone in an empty white room. Realistic photo, minimalist composition.",
    "spectrum":  "A perfect rainbow with all spectrum colors clearly visible — red, orange, yellow, green, blue, indigo, violet — across the sky. Realistic photo.",
    "sphere":    "A collection of perfectly round colorful balloon spheres of different colors. Realistic close-up photo.",
    "star":      "A brilliantly bright star shining in a deep black night sky with smaller stars around it. Realistic space photo.",
    "status":    "A confident student standing at the front of a class with classmates respectfully looking up to her, showing high status. Realistic photo.",
    "ugly":      "A gnarled, ugly toad-like creature sitting on a damp rock in a swamp at night. Realistic photo, eerie mood.",
}


def ensure_output_dir():
    os.makedirs(OUT_DIR, exist_ok=True)


def generate_image(word: str, prompt: str) -> bytes | None:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://esl-vocab-app.local",
        "X-Title": "ESL Vocabulary Cards",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": f"Generate an image: {prompt}"}
        ],
    }

    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )

    if resp.status_code != 200:
        print(f"  ERROR {resp.status_code}: {resp.text[:300]}")
        return None

    data = resp.json()
    choices = data.get("choices", [])
    if not choices:
        print(f"  ERROR: no choices in response for '{word}'")
        return None

    message = choices[0].get("message", {})

    for part in message.get("images", []):
        if isinstance(part, dict) and part.get("type") == "image_url":
            url = part.get("image_url", {}).get("url", "")
            if url.startswith("data:image"):
                b64 = url.split(",", 1)[1]
                return base64.b64decode(b64)
            elif url.startswith("http"):
                return requests.get(url, timeout=30).content

    content = message.get("content", "")
    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") == "image_url":
                url = part.get("image_url", {}).get("url", "")
                if url.startswith("data:image"):
                    b64 = url.split(",", 1)[1]
                    return base64.b64decode(b64)
                elif url.startswith("http"):
                    return requests.get(url, timeout=30).content

    print(f"  WARNING: no image data found in response for '{word}'.")
    return None


def main():
    if not OPENROUTER_API_KEY:
        print("OPENROUTER_API_KEY not set in .env")
        sys.exit(1)

    ensure_output_dir()

    db = SessionLocal()
    try:
        book = db.query(Book).filter(Book.book_number == 2).first()
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 25).first()
        if not unit:
            print("Unit 25 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 25\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} -- no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit25/{word_lower}.png"

            if os.path.exists(out_path):
                print(f"  [{w.position:2}] {w.word} -- already exists, updating DB only")
                w.image_url = static_url
                db.commit()
                continue

            print(f"  [{w.position:2}] Generating image for '{w.word}'...", end=" ", flush=True)
            img_bytes = None
            for attempt in range(3):
                try:
                    img_bytes = generate_image(w.word, prompt)
                    break
                except Exception as e:
                    print(f"\n      retry {attempt+1}/3 after error: {e}")
                    time.sleep(3)

            if img_bytes:
                with open(out_path, "wb") as f:
                    f.write(img_bytes)
                w.image_url = static_url
                db.commit()
                print(f"saved ({len(img_bytes):,} bytes)")
            else:
                print("FAILED -- keeping emoji")

            time.sleep(1)

        print("\nDone.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
