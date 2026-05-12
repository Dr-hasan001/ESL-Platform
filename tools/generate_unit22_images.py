"""
Generate AI images for Book 2 Unit 22 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit22_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit22")

WORD_PROMPTS = {
    "alarm":      "A loud red fire alarm bell mounted on a school hallway wall, with people walking past quickly. Realistic photo.",
    "arrest":     "Two police officers handcuffing a suspect on a city street next to a patrol car. Realistic photo, daylight.",
    "award":      "A smiling person standing on a podium holding up a shiny gold trophy with a proud expression. Realistic photo.",
    "breed":      "A lineup of different dog breeds sitting together — a terrier, a golden retriever, and a bulldog — on green grass. Realistic photo.",
    "bucket":     "A round metal bucket filled with clear water, sitting on a wooden floor. Realistic photo, soft lighting.",
    "contest":    "Two children racing each other in a friendly contest at a school field, with classmates cheering. Realistic photo.",
    "convict":    "A judge in a courtroom holding a gavel, pointing at the defendant who looks guilty. Realistic photo, formal setting.",
    "festival":   "A lively outdoor music festival with crowds of happy people, colorful lights, and a band on stage at night. Realistic photo.",
    "garage":     "A modern home garage with a car parked inside, tools hanging on the wall, and the door open. Realistic photo.",
    "journalist": "A journalist holding a notebook and pen, interviewing someone with a microphone in front of a news event. Realistic photo.",
    "pup":        "An adorable golden retriever puppy with floppy ears sitting on green grass, wagging its tail. Realistic photo.",
    "qualify":    "An athlete crossing the finish line of a qualifying race with arms raised in victory. Realistic photo, stadium setting.",
    "repair":     "A mechanic in overalls fixing a flat tire on a car using tools, in a garage setting. Realistic photo.",
    "resume":     "A woman picking up a book she had set down, opening it to where she left off, on a couch with a cup of tea nearby. Realistic photo.",
    "rob":        "A masked thief in a dark hoodie sneaking through a doorway carrying a bag, in a dimly lit alley. Realistic photo.",
    "slip":       "A man slipping on a wet kitchen floor, arms flailing, with a yellow 'CAUTION' sign nearby. Realistic photo.",
    "somewhat":   "A man with a slightly worried half-smile shrugging his shoulders, expressing 'somewhat' uncertain feeling. Realistic photo.",
    "stable":     "A perfectly balanced wooden chair standing firmly on a polished floor, looking solid and unmoving. Realistic photo.",
    "tissue":     "A box of soft white tissues on a side table next to a person blowing their nose. Realistic photo, warm lighting.",
    "yard":       "Children jumping rope and playing in a sunny grassy backyard outside a family house. Realistic photo.",
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
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 22).first()
        if not unit:
            print("Unit 22 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 22\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} -- no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit22/{word_lower}.png"

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
