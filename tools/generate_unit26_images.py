"""
Generate AI images for Book 2 Unit 26 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit26_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit26")

WORD_PROMPTS = {
    "accuse":     "A child pointing accusingly at her younger brother while a parent watches, in a tidy living room. Realistic photo, daylight.",
    "adjust":     "A man carefully tuning the strings of a wooden acoustic guitar with focused attention. Realistic close-up photo.",
    "amuse":      "A delighted crowd at a small comedy club laughing and clapping during a performance. Realistic photo, warm stage lights.",
    "coral":      "A vibrant underwater coral reef with bright orange, pink, and purple corals and small tropical fish swimming. Realistic underwater photo.",
    "cotton":     "A close-up of fluffy white cotton bolls growing on a green plant in a sunny field. Realistic photo.",
    "crash":      "A red car that has crashed into a tree on a country road, with crumpled hood and broken glass. Realistic photo, daytime.",
    "deck":       "A clean wooden deck on a large modern sailing ship, with neatly coiled ropes and the ocean in the background. Realistic photo.",
    "engage":     "A father and son working together in a workshop, sawing a piece of wood. Realistic warm photo.",
    "firm":       "A neatly made bed with a firm white mattress and tidy pillows in a clean bedroom. Realistic photo.",
    "fuel":       "Logs of wood burning brightly in a campfire, sending up flames and sparks. Realistic close-up photo, night.",
    "grand":      "A grand snow-capped mountain rising majestically into a clear blue sky above a wide valley. Realistic landscape photo.",
    "hurricane":  "A satellite-style view of a powerful spiral hurricane storm over the ocean, with palm trees bending below. Realistic photo.",
    "loss":       "A sad person sitting alone at a poker table, head in hands, with chips pushed away. Realistic photo, dim lighting.",
    "plain":      "A pair of clean, simple white sneakers on a wooden floor — no logos, no decorations. Realistic close-up photo.",
    "reef":       "A long underwater coral reef stretching into the distance, with rocky outcrops and turquoise water. Realistic photo from above the water.",
    "shut":       "A hand gently closing a wooden front door from the inside of a home. Realistic close-up photo, daylight.",
    "strict":     "A serious-looking female teacher standing in front of a quiet classroom of attentive students. Realistic photo.",
    "surf":       "A surfer riding a tall blue wave on a white surfboard, ocean spray flying. Realistic action photo.",
    "task":       "A young person diligently sweeping fallen leaves out of a backyard with a wide broom. Realistic photo, warm afternoon light.",
    "zone":       "Firefighters in protective gear standing inside a marked danger zone with safety tape and warning signs. Realistic photo.",
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
        "messages": [{"role": "user", "content": f"Generate an image: {prompt}"}],
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
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 26).first()
        if not unit:
            print("Unit 26 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 26\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} -- no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit26/{word_lower}.png"

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
