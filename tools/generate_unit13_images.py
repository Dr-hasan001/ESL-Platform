"""
Generate AI images for Book 2 Unit 13 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit13_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit13")

WORD_PROMPTS = {
    "adequate":  "A simple but well-prepared meal of bread, cheese, and soup on a wooden table — adequate and satisfying. Realistic photo.",
    "anxiety":   "A young person sitting on a bed with hands on their head looking worried and stressed. Realistic photo, soft lighting.",
    "army":      "A large group of soldiers in green uniforms marching in formation on a military training field. Realistic photo.",
    "billion":   "A massive pile of stacked banknotes and coins shown in a vault, representing one billion dollars. Realistic photo.",
    "carve":     "A skilled artist using a chisel to carve a detailed sculpture out of a block of wood. Realistic close-up photo.",
    "consult":   "A patient sitting across from a doctor in a clinic, asking for medical advice while the doctor takes notes. Realistic photo.",
    "emergency": "Paramedics rushing a stretcher into an ambulance with flashing red lights at night. Realistic photo, dramatic.",
    "fortune":   "A smiling person holding up a winning lottery ticket with golden coins falling around them. Realistic photo.",
    "guarantee": "A businessperson shaking hands with a customer next to a 'GUARANTEED' stamp on a contract. Realistic photo.",
    "initial":   "A runner crouched at the starting line of a track race, ready for the initial sprint. Realistic photo, golden hour.",
    "intense":   "A focused boxer training hard in a gym with sweat dripping, showing intense effort. Realistic photo, dramatic lighting.",
    "lend":      "A friend handing a book over to another friend in a cozy library. Realistic warm photo.",
    "peak":      "A snow-covered mountain peak rising above the clouds against a clear blue sky. Realistic majestic photo.",
    "potential": "A young athlete at sunrise looking up determined toward a clear sky, full of potential. Realistic inspirational photo.",
    "pride":     "A graduate in cap and gown smiling proudly while holding their diploma, with family clapping in the background. Realistic photo.",
    "proof":     "A detective showing fingerprint evidence under a magnifying glass on a desk full of case files. Realistic photo.",
    "quit":      "A person taking off their work badge and walking out of an office building, deciding to quit their job. Realistic photo.",
    "spin":      "A child laughing while spinning a colorful top toy on a wooden floor. Realistic playful photo.",
    "tiny":      "A tiny ladybug resting on the tip of a person's finger, showing how small it is. Realistic macro close-up photo.",
    "tutor":     "A tutor sitting at a desk explaining math problems to a single attentive student in a quiet study room. Realistic photo.",
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
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 13).first()
        if not unit:
            print("Unit 13 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 13\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} -- no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit13/{word_lower}.png"

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
