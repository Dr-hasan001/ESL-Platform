"""
Generate AI images for Book 2 Unit 20 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit20_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit20")

WORD_PROMPTS = {
    "accomplish":    "An athlete crossing a finish line with arms raised in triumph, celebrating a big achievement. Realistic photo, stadium background.",
    "approve":       "A smiling manager giving a thumbs up and nodding approval to an employee presenting a project. Realistic photo, office setting.",
    "approximate":   "A person measuring ingredients on a kitchen scale with a small hand gesture indicating 'about this much'. Realistic photo, natural light.",
    "barrier":       "A large concrete road barrier blocking a street entrance, orange warning signs attached. Realistic photo, urban setting.",
    "detect":        "A detective using a magnifying glass to closely inspect fingerprints on a surface. Realistic photo, dramatic close-up lighting.",
    "duty":          "A uniformed security guard standing alert at the entrance of a building, doing their duty. Realistic photo.",
    "elementary":    "A young child sitting at a small school desk in a colorful elementary classroom, learning basic letters. Realistic photo.",
    "failure":       "A discouraged person sitting slumped at a desk with a failed exam paper showing a red X score. Realistic photo.",
    "gradual":       "A timelapse-style photo showing a seed sprouting and growing slowly into a small plant in rich soil. Realistic nature photo.",
    "immigrant":     "A family arriving at an airport with luggage, looking hopeful and excited at a new country. Realistic photo, warm lighting.",
    "insert":        "A hand inserting a coin into a vending machine slot. Realistic close-up photo.",
    "instant":       "A sprinter exploding off the starting blocks the instant a starter pistol fires, frozen in motion. Realistic action photo.",
    "poverty":       "A child in worn, patched clothes sitting outside a simple, small house in a poor rural neighborhood. Realistic documentary-style photo.",
    "pretend":       "Two children dressed in costumes pretending to be superheroes in their backyard, one with a cape. Realistic candid photo.",
    "rank":          "Military officers standing in a row, each with different rank badges on their uniforms. Realistic photo, formal setting.",
    "recognition":   "A person receiving an award trophy on stage in front of a clapping audience. Realistic photo, spotlight.",
    "refrigerate":   "An open refrigerator full of fresh vegetables, fruits, and food neatly organized on shelves. Realistic photo.",
    "rent":          "A landlord handing door keys to a new tenant outside an apartment building, both smiling. Realistic photo.",
    "retire":        "An elderly couple relaxing happily in garden chairs, celebrating retirement with coffee. Realistic warm photo.",
    "statistic":     "A large whiteboard covered in charts, graphs, and percentage figures being presented in a business meeting. Realistic photo.",
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
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 20).first()
        if not unit:
            print("Unit 20 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 20\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} — no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit20/{word_lower}.png"

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
