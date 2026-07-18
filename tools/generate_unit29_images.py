"""
Generate AI images for Book 2 Unit 29 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit29_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit29")

WORD_PROMPTS = {
    "abstract":     "A colorful abstract painting with swirling shapes and bold brushstrokes hanging on a clean gallery wall. Realistic photo.",
    "annual":       "A large happy extended family gathered around tables at an outdoor annual family picnic in a green park. Realistic photo, sunny day.",
    "clay":         "A potter's hands shaping a bowl out of wet brown clay on a spinning pottery wheel. Realistic close-up photo.",
    "cloth":        "Folded stacks of colorful soft fabric cloth neatly arranged on a tailor's wooden table. Realistic photo, warm light.",
    "curtain":      "A woman pulling open flowing white curtains over a large window, bright sunlight streaming into the room. Realistic photo.",
    "deserve":      "A well-behaved happy dog being given a large bone treat by its owner's hand in a living room. Realistic photo.",
    "feather":      "A close-up macro photo of a small bird with bright orange and brown feathers on its chest. Realistic wildlife photo.",
    "fertile":      "A farmer kneeling in a lush green field of healthy vegetable crops growing in rich dark fertile soil. Realistic photo.",
    "flood":        "A flooded city street with brown water covering the road and cars partly submerged after heavy rain. Realistic photo.",
    "furniture":    "A simply furnished living room with a sofa, a wooden coffee table, and a couple of chairs. Realistic interior photo, warm light.",
    "grave":        "A quiet peaceful cemetery with a single stone gravestone and fresh flowers placed in front. Realistic photo, soft daylight.",
    "ideal":        "A beautiful perfect family house with a neat green garden under a clear blue sky. Realistic photo, bright daylight.",
    "intelligence": "A bright young student smiling confidently in front of a chalkboard full of complex equations. Realistic photo.",
    "obtain":       "A happy young person proudly holding up a newly issued plastic driver's license card. Realistic photo, bright light.",
    "religious":    "A holy man in robes speaking peacefully to a small gathering of people inside a place of worship. Realistic photo, soft light.",
    "romantic":     "A young couple sharing popcorn and smiling warmly while watching a romantic movie in a dim cinema. Realistic photo.",
    "shell":        "A close-up of pretty seashells of different shapes and colors scattered on golden sand at the beach. Realistic photo, bright daylight.",
    "shore":        "Several small wooden boats floating on calm blue water near a sandy shore. Realistic photo, golden hour light.",
    "wheel":        "A close-up of a shiny clean car wheel and rubber tire on a parked car. Realistic photo, daylight.",
    "wooden":       "A set of handmade wooden kitchen spoons and utensils resting on a rustic wooden table. Realistic photo, warm light.",
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
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 29).first()
        if not unit:
            print("Unit 29 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 29\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} -- no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit29/{word_lower}.png"

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
