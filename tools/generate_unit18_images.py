"""
Generate AI images for Book 2 Unit 18 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit18_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit18")

WORD_PROMPTS = {
    "ability":      "A young athletic person doing a one-arm pull-up on a bar with focused effort, showing strength. Realistic photo, gym setting.",
    "agriculture":  "A wide green farm field with neat rows of crops and a red tractor working in the distance. Realistic landscape photo, sunny day.",
    "cartoon":      "A child laughing while watching a colorful animated cartoon on a TV screen in a cozy living room. Realistic photo, warm evening light.",
    "ceiling":      "Looking straight up at a tall white ceiling with elegant crown molding and a hanging crystal chandelier. Realistic photo.",
    "convince":     "A confident salesperson gesturing persuasively to a thoughtful customer in a modern showroom. Realistic photo, bright lighting.",
    "curious":      "A small child kneeling on the grass with wide eyes, peering closely at a butterfly resting on a flower. Realistic photo, garden setting.",
    "delay":        "A frustrated traveler checking their watch while standing in front of an airport flight board showing the word 'DELAYED'. Realistic photo.",
    "diary":        "An open leather-bound diary on a wooden desk with a fountain pen resting on it. Realistic close-up photo, soft window light.",
    "element":      "A row of glass beakers containing colorful liquids on a science laboratory bench. Realistic photo, bright daylight.",
    "faith":        "A peaceful person standing on a quiet hilltop at sunrise with hands gently clasped in prayer. Realistic photo, warm golden-hour light.",
    "grain":        "A close-up of golden wheat grains spilling from an open burlap sack onto a rustic wooden table. Realistic photo, warm light.",
    "greet":        "Two friends warmly shaking hands and smiling at each other outside a cafe on a sunny morning. Realistic photo.",
    "investigate":  "A detective in a long coat carefully examining a small clue with a magnifying glass at an indoor scene. Realistic photo, dim atmospheric lighting.",
    "joy":          "A group of children jumping and laughing together in a sunny park with colorful balloons floating around. Realistic photo.",
    "label":        "A close-up of a glass jam jar with a clean white label that clearly reads 'STRAWBERRY JAM' on a kitchen counter. Realistic photo.",
    "monk":         "A Buddhist monk in orange robes walking quietly through an old temple courtyard with stone steps. Realistic photo, soft morning light.",
    "odd":          "A single bright red sneaker placed unexpectedly next to a neat pair of plain black shoes on a wooden floor. Realistic photo.",
    "pause":        "A musician sitting still on a piano bench with hands resting motionless on the keys and eyes gently closed. Realistic photo, concert hall lighting.",
    "priest":       "A Catholic priest in black robes and white collar standing thoughtfully inside an old stone church. Realistic photo, light through stained-glass windows.",
    "profession":   "A confident doctor in a white coat with a stethoscope, standing in a bright modern hospital corridor. Realistic photo.",
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
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 18).first()
        if not unit:
            print("Unit 18 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 18\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} -- no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit18/{word_lower}.png"

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
