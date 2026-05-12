"""
Generate AI images for Book 2 Unit 15 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit15_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit15")

WORD_PROMPTS = {
    "absorb":     "A blue paper towel absorbing a spilled glass of water on a kitchen counter, water droplets visible. Realistic close-up photo.",
    "boss":       "A confident female boss in business attire standing in an office, giving directions to her team. Realistic photo.",
    "charitable": "Volunteers from a charitable organization handing out food and warm coats to people in need. Realistic photo, warm lighting.",
    "committee":  "A group of professionals seated around a long conference table in a meeting room, discussing decisions. Realistic photo.",
    "contract":   "Two business professionals signing a written contract on a desk with a pen, official document visible. Realistic close-up photo.",
    "crew":       "A construction crew of workers in hard hats and uniforms working together at a building site. Realistic photo, daytime.",
    "devote":     "A young pianist deeply focused at her piano, devoting hours to practice in a music room. Realistic photo, warm light.",
    "dig":        "A man with a shovel digging a deep hole in the dirt of a backyard garden. Realistic photo, sunny day.",
    "dine":       "A family happily dining together at a beautifully set dinner table with candles and food. Realistic warm photo.",
    "donate":     "A person dropping coins and bills into a charity donation box at a community event. Realistic close-up photo.",
    "double":     "A double scoop of ice cream in a cone — twice the amount of a single scoop, side by side comparison. Realistic photo.",
    "flavor":     "An assortment of colorful ice cream cones with different flavors — chocolate, strawberry, vanilla, mint. Realistic close-up photo.",
    "foundation": "A large modern foundation building with the word 'FOUNDATION' on the entrance, where research is funded. Realistic photo.",
    "generation": "A multi-generational family photo with grandparents, parents, and children gathered together smiling. Realistic warm photo.",
    "handle":     "A close-up of a hand gripping the wooden handle of a kitchen knife while preparing food. Realistic photo.",
    "layer":      "A cross-section of a colorful layered cake showing multiple distinct layers of cream and sponge. Realistic close-up photo.",
    "mud":        "Children playing happily in soft, wet brown mud on a rainy day, splashing and laughing. Realistic photo.",
    "smooth":     "A close-up of a polished, perfectly smooth marble countertop with no bumps or rough edges. Realistic photo.",
    "soil":       "A close-up of rich, dark brown soil in a garden bed with a small plant sprouting from it. Realistic photo, daylight.",
    "unique":     "A single bright orange goldfish standing out in a school of identical silver fish in an aquarium. Realistic photo.",
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
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 15).first()
        if not unit:
            print("Unit 15 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 15\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} -- no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit15/{word_lower}.png"

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
