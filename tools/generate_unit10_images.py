"""
Generate AI images for Book 2 Unit 10 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit10_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit10")

WORD_PROMPTS = {
    "citizen":       "A proud person holding a citizenship certificate in front of a national flag. Realistic photo, warm natural lighting.",
    "council":       "A group of officials sitting around a large oval table in a formal meeting room, discussing seriously. Realistic photo.",
    "declare":       "A politician standing at a podium making an important announcement to a crowd. Realistic photo, dramatic lighting.",
    "enormous":      "A tiny person standing next to an enormous ancient sequoia tree in a forest, showing the massive scale. Realistic photo.",
    "extraordinary": "A breathtaking view of the Northern Lights over a snow-covered mountain landscape at night. Realistic photo.",
    "fog":           "A dense white fog rolling through a quiet forest road at dawn, barely visible trees in the distance. Realistic atmospheric photo.",
    "funeral":       "A solemn outdoor funeral ceremony with mourners in black standing around a flower-covered casket. Realistic photo.",
    "giant":         "A giant stone statue towering over small tourists standing at its base. Realistic photo, wide angle.",
    "impression":    "A person making a strong first impression with a confident handshake and warm smile in a professional setting. Realistic photo.",
    "intention":     "A focused person writing a clear goal or plan in a notebook on a desk. Realistic photo, natural light.",
    "mad":           "A person with an extremely frustrated and angry expression, clenching their fists. Realistic portrait photo.",
    "ought":         "A parent pointing gently at homework on a table, reminding their child to do it. Realistic photo, warm home lighting.",
    "resist":        "A person firmly pushing away a plate of tempting donuts, resisting the urge to eat. Realistic photo.",
    "reveal":        "A magician dramatically pulling back a curtain to reveal a hidden object on stage. Realistic photo, spotlight effect.",
    "rid":           "A person spraying insecticide to get rid of insects in a kitchen. Realistic photo.",
    "sword":         "An ancient ornate steel sword resting on a stone surface with dramatic lighting. Realistic photo, sharp detail.",
    "tale":          "An elderly grandparent telling a captivating story to wide-eyed grandchildren by a fireplace. Realistic photo, warm cozy light.",
    "trap":          "A rusty metal animal trap set on a forest floor among fallen leaves. Realistic nature photo, close-up.",
    "trial":         "A serious courtroom scene with a judge, lawyers, and defendant at the stand. Realistic photo.",
    "violent":       "A fierce storm with dark clouds, lightning striking, and strong winds bending trees. Realistic dramatic weather photo.",
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
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 10).first()
        if not unit:
            print("Unit 10 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 10\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} — no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit10/{word_lower}.png"

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
