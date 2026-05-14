"""
Generate AI images for Book 2 Unit 17 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit17_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit17")

WORD_PROMPTS = {
    "aim":        "An archer drawing back a bow, focused intensely on a distant target with the arrow pointed straight ahead. Realistic photo, golden hour.",
    "attach":     "Two hands clicking a metal carabiner onto a climbing rope, attaching them together. Realistic close-up photo.",
    "bet":        "A poker chip being placed on a card table beside playing cards as a bet. Realistic photo, casino atmosphere.",
    "carriage":   "An old-fashioned wooden carriage pulled by two brown horses on a cobblestone street. Realistic photo, historic setting.",
    "classic":    "A vintage 1960s red convertible car parked on a quiet street, looking timeless and elegant. Realistic photo.",
    "commute":    "A crowded morning train with commuters in business attire heading to work, viewed from inside the carriage. Realistic photo.",
    "confirm":    "A businessperson signing a confirmation document at a desk while a colleague nods in agreement. Realistic photo.",
    "criticize":  "A boss frowning while pointing at a paper, criticizing an employee's work in an office setting. Realistic photo.",
    "differ":     "Two completely different shoes side by side — a formal black dress shoe next to a colorful sports sneaker. Realistic photo.",
    "expense":    "A person reviewing a stack of receipts and bills at a desk with a calculator, calculating expenses. Realistic photo.",
    "formal":     "A man in a perfectly tailored black tuxedo with bowtie at a formal evening event. Realistic portrait photo.",
    "height":     "A measuring tape stretched vertically against a wall showing the height of a tall child marked at 150 cm. Realistic photo.",
    "invent":     "An inventor in a workshop surrounded by sketches, tools, and a newly built prototype machine. Realistic photo, creative atmosphere.",
    "junior":     "A young apprentice in work clothes learning from a senior craftsperson in a workshop. Realistic warm photo.",
    "labor":      "A construction worker doing hard physical labor — laying bricks and lifting heavy materials at a building site. Realistic photo.",
    "mechanic":   "A mechanic in oil-stained overalls working under the hood of a car in a garage. Realistic photo.",
    "prime":      "A juicy prime cut of steak being served on a fine plate at an upscale restaurant. Realistic close-up photo.",
    "shift":      "A worker pushing a heavy wooden crate across a warehouse floor, shifting it to a new position. Realistic photo.",
    "signal":     "A traffic light glowing bright green at an intersection, signaling cars to go. Realistic photo, urban night scene.",
    "sincere":    "Two friends sharing a heartfelt moment, one giving the other a genuinely sincere apology with eye contact. Realistic warm photo.",
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
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 17).first()
        if not unit:
            print("Unit 17 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 17\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} -- no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit17/{word_lower}.png"

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
