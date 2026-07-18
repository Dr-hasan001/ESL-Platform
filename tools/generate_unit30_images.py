"""
Generate AI images for Book 2 Unit 30 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit30_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit30")

WORD_PROMPTS = {
    "appliance":   "A modern clean kitchen with home appliances -- an oven, a toaster, and a refrigerator. Realistic photo, bright light.",
    "basin":       "A white ceramic wash basin filled with clear water on a tidy bathroom counter. Realistic photo, soft light.",
    "broom":       "A person using a broom with a long wooden handle to sweep dust off a wooden floor. Realistic photo.",
    "caterpillar": "A close-up macro photo of a green caterpillar crawling on a leaf and eating it. Realistic nature photo, bright daylight.",
    "cupboard":    "An open wooden kitchen cupboard filled with neatly stacked dishes, plates, and food jars. Realistic photo.",
    "delicate":    "A pair of gentle hands carefully cupping a fragile delicate flower. Realistic close-up photo, soft light.",
    "emerge":      "A small groundhog poking its head out and emerging from a snow-covered hole in the ground. Realistic wildlife photo.",
    "handicap":    "An older man using a walking frame walker to move around his home. Realistic photo, warm light.",
    "hole":        "A large round hole broken into a plaster wall, revealing the dark space behind it. Realistic photo.",
    "hook":        "A close-up of a single shiny sharp curved metal fishing hook. Realistic photo, detailed, plain background.",
    "hop":         "A kangaroo mid-hop jumping across a dry golden grassland. Realistic wildlife action photo.",
    "laundry":     "A woven basket full of neatly folded clean laundry next to a white washing machine. Realistic photo, bright light.",
    "pursue":      "A smiling mother running down a grassy hill chasing after her laughing young child. Realistic photo, sunny day.",
    "reluctant":   "A young woman with a hesitant, unwilling expression, holding back and looking uncertain. Realistic portrait photo.",
    "sleeve":      "A close-up of a man wearing a warm long-sleeve shirt, focus on the long sleeves covering his arms. Realistic photo.",
    "spine":       "A clean medical anatomical model of the human spine backbone on a plain background. Realistic photo.",
    "stain":       "A close-up of a white shirt collar with a dark red stain mark on it. Realistic photo, detailed.",
    "strip":       "Long narrow strips of old photographic film laid out across a table. Realistic photo, detailed.",
    "swear":       "A person raising their right hand and placing the other hand on a book to swear an oath. Realistic photo, serious mood.",
    "swing":       "A golfer in mid-swing powerfully hitting a golf ball on a green golf course. Realistic action photo.",
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
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 30).first()
        if not unit:
            print("Unit 30 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 30\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} -- no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit30/{word_lower}.png"

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
