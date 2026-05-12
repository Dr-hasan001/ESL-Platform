"""
Generate AI images for Book 2 Unit 24 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit24_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit24")

WORD_PROMPTS = {
    "bath":       "A clean bathtub filled with warm water and bubbles, in a bright, modern bathroom. Realistic photo, cozy lighting.",
    "bend":       "A young man bending down to pick up a piece of paper from the ground in a park. Realistic photo, natural daylight.",
    "chew":       "A close-up of a child carefully chewing a piece of food, eyes closed in concentration, at a kitchen table. Realistic photo.",
    "disabled":   "A man in a wheelchair smiling and rolling along a paved sidewalk on a bright day. Realistic photo.",
    "fantastic":  "A student proudly holding up a school project with a gold award ribbon, beaming with pride. Realistic photo, classroom.",
    "fiction":    "A close-up of a person reading a colorful fiction novel with imaginative book illustrations spilling out. Realistic photo.",
    "flag":       "A bright national flag waving in the wind on a tall pole against a blue sky. Realistic photo.",
    "inspect":    "A mechanic in overalls carefully inspecting a car engine with a flashlight. Realistic photo, garage setting.",
    "journal":    "A close-up of an academic journal magazine on a wooden desk, with a pen and reading glasses beside it. Realistic photo.",
    "liquid":     "A clear glass of water on a marble table with light reflecting through the liquid. Realistic close-up photo.",
    "marvel":     "An audience marveling with wide eyes and open mouths at a child playing piano beautifully on stage. Realistic photo.",
    "overcome":   "A determined woman triumphantly speaking in front of a class, overcoming her shyness with confidence. Realistic photo.",
    "recall":     "A woman with her hand on her chin trying to recall a memory, with a thoughtful expression. Realistic photo.",
    "regret":     "A young person sitting alone on a bench with head in hands, expressing deep regret. Realistic photo, soft lighting.",
    "soul":       "A peaceful spiritual scene with a glowing ethereal light rising into a starry sky. Realistic artistic photo.",
    "sufficient": "A satisfied person pushing back from a dining table after eating a sufficient meal, with leftover food on the plate. Realistic photo.",
    "surgery":    "A surgical team in scrubs and masks performing surgery in a bright operating room. Realistic photo, medical setting.",
    "tough":      "A young driver gripping the steering wheel during a tough driving test on a busy road. Realistic photo, focused expression.",
    "tube":       "A pile of long white plastic tubes stacked on a construction site, ready to be put in the ground. Realistic photo.",
    "value":      "A jeweler examining a sparkling diamond with a loupe, demonstrating its great value. Realistic close-up photo.",
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
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 24).first()
        if not unit:
            print("Unit 24 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 24\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} -- no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit24/{word_lower}.png"

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
