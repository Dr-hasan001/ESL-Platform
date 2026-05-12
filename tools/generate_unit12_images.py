"""
Generate AI images for Book 2 Unit 12 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit12_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit12")

WORD_PROMPTS = {
    "abuse":       "A person looking sad and hurt sitting alone in a corner, representing the concept of mistreatment. Realistic photo, soft lighting.",
    "afford":      "A happy family holding shopping bags outside a store, smiling because they could afford new things. Realistic photo.",
    "bake":        "A person in an apron sliding a golden loaf of bread into a hot oven in a home kitchen. Realistic photo.",
    "bean":        "A handful of colorful beans — red, black, and white — spread on a wooden table. Close-up realistic photo.",
    "candle":      "A single white candle with a warm glowing flame in a dark room, casting soft shadows. Realistic photo.",
    "convert":     "A worker converting an old warehouse into a modern apartment, with tools and renovation in progress. Realistic photo.",
    "debt":        "A stressed person surrounded by bills and a large 'DEBT' sign on paper, looking worried. Realistic photo.",
    "decrease":    "A graph on a screen clearly showing a downward trend with a red arrow pointing lower. Realistic photo.",
    "fault":       "A person raising their hand to take the blame while others point at them. Realistic photo, office setting.",
    "fund":        "A large jar filled with coins and cash labeled 'SAVINGS FUND' on a wooden desk. Realistic photo.",
    "generous":    "A smiling woman handing a food basket to a grateful elderly neighbor. Realistic warm photo.",
    "ingredient":  "Fresh cooking ingredients laid out on a kitchen counter — vegetables, spices, eggs, and flour. Realistic top-down photo.",
    "insist":      "A firm person pointing at a contract and insisting the other person sign it. Realistic photo, business setting.",
    "mess":        "A very messy children's bedroom with clothes, toys, and books scattered everywhere on the floor. Realistic photo.",
    "metal":       "A collection of shiny metal objects — steel pipes, bolts, and sheets — on an industrial workbench. Realistic photo.",
    "monitor":     "A security guard watching multiple surveillance screens in a control room. Realistic photo, dim lighting.",
    "oppose":      "Two people facing each other in a debate, one firmly opposing the other's idea with a raised hand. Realistic photo.",
    "passive":     "A person sitting back with arms folded, watching a problem unfold without doing anything. Realistic photo.",
    "quantity":    "A large pile of apples being measured and counted on a market scale. Realistic photo.",
    "sue":         "A lawyer presenting documents in a courtroom while pointing at the defendant. Realistic photo, formal setting.",
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
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 12).first()
        if not unit:
            print("Unit 12 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 12\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} -- no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit12/{word_lower}.png"

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
