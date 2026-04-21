"""
Generate AI images for Book 2 Unit 19 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit19_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit19")

WORD_PROMPTS = {
    "ball":        "A colorful soccer ball resting on short green grass in bright sunlight. Realistic photo, sharp focus, vibrant colors.",
    "bottom":      "The bottom of a clear glass bottle seen from directly below, resting on a wooden table. Realistic macro photo, sharp detail.",
    "company":     "A diverse group of smiling colleagues collaborating around a table in a bright modern office. Realistic photo, natural lighting.",
    "drink":       "A person taking a refreshing sip from a tall glass of cold water with ice and condensation on the outside. Realistic photo.",
    "few":         "Three ripe red apples placed on a rustic wooden table. Realistic photo, warm natural light, shallow depth of field.",
    "line":        "A long queue of people waiting patiently outside a shop on a sunny city street. Realistic street photo.",
    "pet":         "A happy golden retriever puppy sitting on green grass, tongue out, looking at the camera. Realistic photo, warm sunlight.",
    "product":     "Neatly arranged consumer products on a clean supermarket shelf with colorful packaging. Realistic photo.",
    "responsible": "A young person carefully watering a small potted plant on a sunny windowsill, looking attentive. Realistic photo.",
    "sell":        "A friendly market vendor smiling while handing fresh vegetables to a customer at an outdoor market stall. Realistic photo.",
    "snake":       "A bright green tree snake coiled around a branch in a rainforest, scales glistening. Realistic nature photo, sharp detail.",
    "stand":       "A confident person standing tall in a sunlit park, hands relaxed at their sides. Realistic photo, natural background.",
    "strange":     "A surreal scene of an umbrella floating alone in the middle of a living room with no one around. Realistic photo, eerie atmosphere.",
    "tea":         "A steaming cup of tea on a wooden table with a small teapot beside it, warm morning light. Realistic photo.",
    "test":        "A student sitting at a school desk focused on writing a paper exam, pencil in hand. Realistic classroom photo.",
    "tongue":      "A close-up of a person playfully sticking their tongue out, bright smile, warm lighting. Realistic portrait photo.",
    "they":        "A diverse group of four friends laughing and walking together on a sunny city street. Realistic lifestyle photo.",
    "type":        "A pair of hands typing quickly on a laptop keyboard on a clean desk. Realistic photo, overhead angle, natural light.",
    "very":        "A giant skyscraper photographed from directly below, towering into a clear blue sky, emphasizing extreme height. Realistic photo.",
    "wait":        "A person sitting alone on a wooden bench at a bus stop, glancing at their wristwatch. Realistic photo, natural outdoor light.",
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
        if not book:
            print("Book 2 not found.")
            sys.exit(1)
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 19).first()
        if not unit:
            print("Unit 19 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 19\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} — no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit19/{word_lower}.png"

            if os.path.exists(out_path):
                print(f"  [{w.position:2}] {w.word} — already exists, updating DB only")
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
                print("FAILED — keeping emoji")

            time.sleep(1)

        print("\nDone.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
