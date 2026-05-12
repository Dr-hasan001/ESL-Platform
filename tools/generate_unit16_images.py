"""
Generate AI images for Book 2 Unit 16 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit16_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit16")

WORD_PROMPTS = {
    "academy":    "A grand academy building with classical architecture and 'ACADEMY' written above the entrance, students walking inside. Realistic photo.",
    "ancient":    "Ancient Roman ruins of marble columns and old stone walls under a blue sky. Realistic photo.",
    "board":      "A flat wooden board lying on a workshop bench, with grain visible. Realistic close-up photo.",
    "century":    "A vintage 1924 calendar page beside a modern 2024 calendar page, showing the passage of one century. Realistic photo.",
    "clue":       "A detective using a magnifying glass to examine a small clue — a footprint or note — at a crime scene. Realistic photo.",
    "concert":    "A live concert with a band performing on stage, colorful lights, and a cheering crowd. Realistic photo, dramatic lighting.",
    "county":     "A wide aerial view of a rural county with farmland, small towns, and rolling hills. Realistic photo, daylight.",
    "dictionary": "An open thick English dictionary on a wooden desk with reading glasses beside it. Realistic close-up photo.",
    "exist":      "A glowing fingerprint visible in a magnifying glass, symbolizing something real that exists. Realistic photo.",
    "flat":       "A perfectly flat smooth surface — a calm lake at dawn with no ripples, mirror-like. Realistic photo.",
    "gentleman":  "An elegant gentleman in a classic suit and tie, tipping his hat politely. Realistic warm portrait photo.",
    "hidden":     "A treasure chest partially hidden beneath leaves and branches in a forest. Realistic photo, dappled sunlight.",
    "maybe":      "A person standing at a fork in the road, scratching their head uncertain which way to go. Realistic photo.",
    "officer":    "A confident military officer in dress uniform with rank insignia, standing at attention. Realistic portrait photo.",
    "original":   "A '1st Edition' book on display under glass, marked clearly as the original printing. Realistic photo.",
    "pound":      "A blacksmith pounding hot metal with a heavy hammer at an anvil, sparks flying. Realistic dramatic photo.",
    "process":    "A flowchart drawn on a whiteboard showing step 1, step 2, step 3 — illustrating a process. Realistic photo, office setting.",
    "publish":    "A printing press machine producing freshly printed books rolling off the line. Realistic photo, factory setting.",
    "theater":    "A grand theater with red velvet seats, a stage with curtains, and ornate balconies. Realistic photo.",
    "wealth":     "A vault filled with stacks of gold coins, dollar bills, and jewelry — representing great wealth. Realistic photo, dramatic lighting.",
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
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 16).first()
        if not unit:
            print("Unit 16 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 16\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} -- no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit16/{word_lower}.png"

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
