"""
Generate AI images for Book 2 Unit 23 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit23_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit23")

WORD_PROMPTS = {
    "best":       "A student proudly holding up a math test paper with a perfect 'A+' grade marked in red ink. Realistic photo, classroom setting.",
    "card":       "A close-up of a student handing a library card to a librarian at a check-out desk. Realistic photo, library setting.",
    "crowd":      "A large crowd of cheering people waving at a camera at an outdoor event. Realistic photo, daytime, festival vibe.",
    "day":        "A wall calendar with the current day circled in red marker, sitting on a kitchen counter. Realistic photo, bright lighting.",
    "dish":       "A beautifully plated chicken curry dish at a fine restaurant, garnished with fresh herbs. Realistic close-up food photo.",
    "easy":       "A cheerful student smiling and pointing at her completed English homework with a thumbs up. Realistic photo, cozy desk.",
    "experience": "A young person riding a thrilling roller coaster with arms raised, having an exciting experience. Realistic photo.",
    "hotel":      "A modern hotel reception lobby with a smiling family checking in, suitcases beside them. Realistic photo.",
    "hour":       "A close-up of a wristwatch showing exactly one hour past the previous time, on a man's wrist at a train station. Realistic photo.",
    "light":      "A bright glowing light bulb hanging from the ceiling illuminating a dim room. Realistic close-up photo.",
    "market":     "A busy outdoor farmer's market with stalls full of fresh fruits and vegetables, shoppers browsing. Realistic photo.",
    "plan":       "A businessperson at a desk arranging schedule notes and calendar items, planning out party details. Realistic photo.",
    "price":      "A woman in a clothing store checking the price tag on a sweater. Realistic photo, retail setting.",
    "short":      "A bare tree with leafless branches against a gray winter sky during a short winter day. Realistic photo, late afternoon.",
    "shop":       "A man walking out of a grocery shop carrying paper bags full of fresh groceries. Realistic photo, evening light.",
    "station":    "A man standing on a train station platform looking at the arrival board, waiting for his train. Realistic photo.",
    "surprise":   "Parents holding a small puppy with a red bow as a surprise gift for their excited child. Realistic warm family photo.",
    "system":     "A modern building's heating control panel with various dials and digital readings on a wall. Realistic close-up photo.",
    "taxi":       "A bright yellow taxi cab with its 'TAXI' sign lit, parked on a busy city street. Realistic photo.",
    "two":        "Two close friends sitting together at a coffee shop table, studying with open books. Realistic warm photo.",
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
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 23).first()
        if not unit:
            print("Unit 23 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 23\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} -- no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit23/{word_lower}.png"

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
