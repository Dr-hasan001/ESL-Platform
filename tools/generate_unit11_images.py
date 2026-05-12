"""
Generate AI images for Book 2 Unit 11 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit11_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit11")

WORD_PROMPTS = {
    "admission":   "A person handing a ticket to a staff member at the entrance of a museum, being allowed inside. Realistic photo.",
    "astronomy":   "An astronomer looking through a large telescope at a star-filled night sky in an observatory. Realistic photo, dark blue night.",
    "blame":       "A person pointing their finger accusingly at someone else during an argument. Realistic photo, expressive faces.",
    "chemistry":   "A scientist in a lab coat mixing colorful liquids in glass flasks, surrounded by lab equipment. Realistic photo.",
    "despite":     "A determined runner finishing a race in heavy rain despite the bad weather, pushing through the finish line. Realistic photo.",
    "dinosaur":    "A large realistic Tyrannosaurus Rex dinosaur standing in a prehistoric jungle landscape. Realistic detailed photo-style illustration.",
    "exhibit":     "Visitors in a museum gallery admiring paintings and sculptures on display. Realistic photo, soft gallery lighting.",
    "fame":        "A famous celebrity surrounded by paparazzi cameras and flashing lights on a red carpet. Realistic photo.",
    "forecast":    "A weather forecaster standing in front of a large screen showing rain clouds and temperature maps. Realistic photo.",
    "genius":      "A brilliant scientist covered in equations on a chalkboard, looking focused and intelligent. Realistic photo.",
    "gentle":      "A kind person gently stroking a small kitten with a soft smile. Realistic warm photo.",
    "geography":   "A student studying a large colorful world map spread out on a desk with a globe nearby. Realistic photo.",
    "interfere":   "A person stepping in between two others who are arguing, trying to interrupt and cause disruption. Realistic photo.",
    "lightly":     "A hand lightly touching the surface of a calm pond, barely disturbing the water. Realistic close-up photo.",
    "principal":   "A school principal in a suit standing at the entrance of a school, welcoming students. Realistic photo.",
    "row":         "A long straight row of colorful tulips in a flower field. Realistic nature photo, bright daylight.",
    "shelf":       "Wooden wall shelves neatly lined with books, plants, and decorative items in a cozy living room. Realistic photo.",
    "spite":       "A person giving a mean, spiteful glare to someone across a room, arms crossed. Realistic photo.",
    "super":       "A person jumping in the air with excitement and a huge smile, celebrating something amazing. Realistic photo.",
    "wet":         "A child completely soaked, laughing while playing in a heavy rain puddle. Realistic candid photo.",
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
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 11).first()
        if not unit:
            print("Unit 11 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 11\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} — no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit11/{word_lower}.png"

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
