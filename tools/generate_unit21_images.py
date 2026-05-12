"""
Generate AI images for Book 2 Unit 21 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit21_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit21")

WORD_PROMPTS = {
    "accident":    "A damaged car on the side of a road after a crash, with broken glass and dents. Realistic photo, daylight.",
    "astronaut":   "An astronaut in a white spacesuit walking on the surface of the moon with Earth visible in the background. Realistic photo.",
    "awake":       "A person lying in bed with eyes wide open staring at the ceiling in a dark room at night. Realistic photo.",
    "courage":     "A brave person standing confidently facing a large roaring lion in an open savanna. Realistic dramatic photo.",
    "float":       "A small colorful toy boat floating gently on the calm surface of a swimming pool. Realistic photo, sunny day.",
    "grant":       "A teacher smiling and gesturing to students to take a break, students looking relieved and happy. Realistic classroom photo.",
    "gravity":     "An astronaut floating weightlessly inside a space station with objects drifting in the air around them. Realistic photo.",
    "jewel":       "A collection of sparkling diamonds and precious gems displayed on black velvet in a jewelry store. Realistic close-up photo.",
    "miner":       "A coal miner wearing a hard hat with a headlamp, working deep inside a dark mine tunnel. Realistic photo.",
    "mineral":     "A close-up of colorful mineral crystals and rock samples laid out on a geology table. Realistic photo.",
    "participate": "Students enthusiastically raising their hands and participating actively in a school play on stage. Realistic photo.",
    "permission":  "A teenager handing car keys while an adult parent nods giving permission. Realistic warm home photo.",
    "pour":        "A person carefully pouring fresh milk from a jug into a glass cup on a kitchen counter. Realistic photo.",
    "raw":         "A pile of raw unprocessed iron ore and natural minerals on industrial ground. Realistic close-up photo.",
    "satellite":   "A shiny satellite with solar panels orbiting the Earth in outer space against a starry background. Realistic photo.",
    "scale":       "A person looking up in awe at the massive towering skyscrapers in a busy downtown city. Realistic wide-angle photo.",
    "skip":        "A man casually skipping a work meeting, sitting relaxed on a park bench instead. Realistic photo.",
    "stretch":     "A woman stretching her arms wide and legs out on a yoga mat before morning exercise. Realistic photo.",
    "telescope":   "A person looking through a large telescope at a clear night sky full of stars and the moon. Realistic photo.",
    "underground": "A subway train moving through a dark underground tunnel below the city. Realistic photo.",
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
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 21).first()
        if not unit:
            print("Unit 21 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 21\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} -- no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit21/{word_lower}.png"

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
