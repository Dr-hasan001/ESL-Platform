"""
Generate AI images for Book 1 Unit 1 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit1_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book1", "unit1")

WORD_PROMPTS = {
    "abandon":  "A person walking away and leaving through an open door, leaving behind a house. Simple flat design illustration, warm colors, white background.",
    "benefit":  "A smiling person receiving a glowing gift box with a ribbon. Simple flat design illustration, warm colors, white background.",
    "bold":     "A confident lion standing proudly with its mane blowing in the wind. Simple flat design illustration, vibrant colors, white background.",
    "cease":    "A large red stop sign with a hand raised in a halt gesture. Simple flat design illustration, white background.",
    "crime":    "A pair of silver handcuffs next to a gavel. Simple flat design illustration, neutral colors, white background.",
    "cure":     "A doctor handing a glowing medicine bottle to a smiling patient. Simple flat design illustration, clean colors, white background.",
    "damage":   "A cracked and broken vase with pieces falling apart. Simple flat design illustration, muted tones, white background.",
    "defend":   "A knight holding a large shield in front of them protectively. Simple flat design illustration, bold colors, white background.",
    "depend":   "Two people leaning on each other for support, back to back. Simple flat design illustration, warm colors, white background.",
    "duty":     "A person in uniform checking items off a clipboard checklist. Simple flat design illustration, clean colors, white background.",
    "escape":   "A person running joyfully out of a maze exit into open space. Simple flat design illustration, bright colors, white background.",
    "fame":     "A performer on a bright stage under a spotlight with a cheering crowd. Simple flat design illustration, vibrant colors, white background.",
    "famine":   "An empty bowl on cracked dry earth under a scorching sun. Simple flat design illustration, muted warm tones, white background.",
    "grief":    "A person sitting alone with head bowed, a single tear on their cheek. Simple flat design illustration, soft blue tones, white background.",
    "guard":    "A security guard standing alert at a door with arms crossed. Simple flat design illustration, clean colors, white background.",
    "guilty":   "A person standing in a courtroom looking down with a judge's gavel raised. Simple flat design illustration, neutral tones, white background.",
    "hardship": "A small person struggling to climb a steep rocky hill in stormy weather. Simple flat design illustration, dark dramatic tones, white background.",
    "harvest":  "A happy farmer collecting golden wheat crops in a sunny field with a basket. Simple flat design illustration, warm golden colors, white background.",
    "humble":   "A person bowing graciously with a gentle smile, eyes downcast. Simple flat design illustration, soft colors, white background.",
    "increase": "A bar chart with an upward arrow showing growth, surrounded by rising coins. Simple flat design illustration, green tones, white background.",
}


def ensure_output_dir():
    os.makedirs(OUT_DIR, exist_ok=True)


def add_image_url_column():
    """Add image_url column to words table if it doesn't exist (SQLite safe)."""
    import sqlite3
    db_path = "esl.db"
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. Run seed_db.py first.")
        sys.exit(1)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(words)")
    cols = [row[1] for row in cur.fetchall()]
    if "image_url" not in cols:
        cur.execute("ALTER TABLE words ADD COLUMN image_url VARCHAR(500)")
        conn.commit()
        print("Added image_url column to words table.")
    conn.close()


def generate_image(word: str, prompt: str) -> bytes | None:
    """Call OpenRouter Gemini image model and return raw PNG bytes."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://esl-vocab-app.local",
        "X-Title": "ESL Vocabulary Cards",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": f"Generate an image: {prompt}",
            }
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

    # OpenRouter Gemini returns images in message['images'] as a list of image_url parts
    for part in message.get("images", []):
        if isinstance(part, dict) and part.get("type") == "image_url":
            url = part.get("image_url", {}).get("url", "")
            if url.startswith("data:image"):
                b64 = url.split(",", 1)[1]
                return base64.b64decode(b64)
            elif url.startswith("http"):
                img_resp = requests.get(url, timeout=30)
                return img_resp.content

    # Fallback: check content list (some providers use this format)
    content = message.get("content", "")
    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") == "image_url":
                url = part.get("image_url", {}).get("url", "")
                if url.startswith("data:image"):
                    b64 = url.split(",", 1)[1]
                    return base64.b64decode(b64)
                elif url.startswith("http"):
                    img_resp = requests.get(url, timeout=30)
                    return img_resp.content

    print(f"  WARNING: no image data found in response for '{word}'.")
    return None


def main():
    if not OPENROUTER_API_KEY:
        print("OPENROUTER_API_KEY not set in .env")
        sys.exit(1)

    ensure_output_dir()
    add_image_url_column()

    db = SessionLocal()
    try:
        # Get Book 1 Unit 1
        book = db.query(Book).filter(Book.book_number == 1).first()
        if not book:
            print("Book 1 not found in database.")
            sys.exit(1)
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 1).first()
        if not unit:
            print("Unit 1 not found in database.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 1 Unit 1\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position}] {w.word} — no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book1/unit1/{word_lower}.png"

            if os.path.exists(out_path):
                print(f"  [{w.position}] {w.word} — image already exists, updating DB only")
                w.image_url = static_url
                db.commit()
                continue

            print(f"  [{w.position}] Generating image for '{w.word}'...", end=" ", flush=True)
            img_bytes = generate_image(w.word, prompt)

            if img_bytes:
                with open(out_path, "wb") as f:
                    f.write(img_bytes)
                w.image_url = static_url
                db.commit()
                print(f"saved ({len(img_bytes):,} bytes)")
            else:
                print("FAILED — keeping emoji")

            time.sleep(1)  # be polite to the API

        print("\nDone.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
