"""
Generate AI images for Book 2 Unit 9 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit9_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit9")

WORD_PROMPTS = {
    "against":  "A person leaning their back against a brick wall, arms crossed, looking relaxed. Simple flat design illustration, warm colors, white background.",
    "beach":    "A sunny beach with golden sand, gentle waves, and a blue sky. Simple flat design illustration, bright colors, white background.",
    "damage":   "A cracked and broken vase with pieces falling apart on the floor. Simple flat design illustration, muted tones, white background.",
    "discover": "An excited explorer finding a glowing treasure chest in the ground. Simple flat design illustration, vibrant colors, white background.",
    "emotion":  "A face showing a strong happy emotion with tears of joy and a big smile. Simple flat design illustration, warm colors, white background.",
    "fix":      "A person using a wrench to repair a broken machine. Simple flat design illustration, clean colors, white background.",
    "identify": "A person holding a magnifying glass and pointing at a colorful bird to name it. Simple flat design illustration, bright colors, white background.",
    "island":   "A small tropical island surrounded by clear blue water with a palm tree. Simple flat design illustration, bright colors, white background.",
    "ocean":    "A vast deep blue ocean stretching to the horizon under a clear sky. Simple flat design illustration, cool blue tones, white background.",
    "perhaps":  "A person with a thoughtful expression, chin on hand, looking up wondering. Simple flat design illustration, soft colors, white background.",
    "pleasant": "A happy person sitting outside on a sunny day enjoying a gentle breeze. Simple flat design illustration, warm cheerful colors, white background.",
    "prevent":  "A hand raised firmly in a stop gesture blocking something from passing. Simple flat design illustration, bold colors, white background.",
    "rock":     "A large gray rock sitting beside a calm river. Simple flat design illustration, natural earthy tones, white background.",
    "save":     "A lifeguard reaching out to rescue a person in the water. Simple flat design illustration, bright colors, white background.",
    "smile":    "A person with a big warm smile and bright eyes. Simple flat design illustration, warm colors, white background.",
    "step":     "A person carefully stepping over a puddle on a path. Simple flat design illustration, clean colors, white background.",
    "still":    "A starfish sitting completely still and motionless on dry sand. Simple flat design illustration, neutral tones, white background.",
    "taste":    "A person tasting soup from a spoon with a delighted expression. Simple flat design illustration, warm colors, white background.",
    "throw":    "A person throwing a ball through the air with both arms raised. Simple flat design illustration, vibrant colors, white background.",
    "wave":     "A tall curling ocean wave about to break on the shore. Simple flat design illustration, blue tones, white background.",
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
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 9).first()
        if not unit:
            print("Unit 9 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 9\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} — no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit9/{word_lower}.png"

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
