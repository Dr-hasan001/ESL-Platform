"""
Generate AI images for Book 2 Unit 28 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit28_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit28")

WORD_PROMPTS = {
    "accompany":  "Two young brothers walking side by side together toward the entrance of a movie theater at night, friendly and companionable. Realistic photo.",
    "bare":       "A close-up of a person's bare feet walking on a smooth polished wooden floor, no shoes or socks. Realistic photo, soft natural light.",
    "branch":     "A playful brown monkey hanging by one arm from a leafy green tree branch in a lush forest. Realistic wildlife photo.",
    "breath":     "A person outdoors on a cold winter morning exhaling a visible cloud of warm breath into frosty air. Realistic photo, soft daylight.",
    "bridge":     "A long old stone arch bridge spanning a wide calm river, a few people crossing it. Realistic photo, golden hour light.",
    "cast":       "A fisherman standing at the edge of a lake casting his fishing line out over the water, the line arcing through the air. Realistic photo.",
    "dare":       "A brave skydiver leaping out of an open airplane door into the open blue sky, parachute pack on his back. Realistic action photo.",
    "electronic": "A modern MP3 player and small electronic gadgets with glowing screens arranged neatly on a desk. Realistic product photo.",
    "inn":        "A cozy old countryside inn with warm glowing windows at dusk, a traveler with a bag arriving at the wooden front door. Realistic photo.",
    "net":        "A happy child holding a butterfly net, catching a colorful butterfly in a sunny green meadow. Realistic photo.",
    "philosophy": "A thoughtful man sitting alone on a hilltop at sunset, gazing at the horizon and contemplating life, peaceful expression. Realistic photo, soft light.",
    "pot":        "A deep round metal cooking pot sitting on a stove with steam gently rising from it. Realistic kitchen photo, warm light.",
    "seed":       "A close-up of a hand carefully planting a small seed into rich brown garden soil. Realistic photo, bright daylight.",
    "sharp":      "A close-up of a very sharp kitchen knife with a gleaming thin steel blade resting on a wooden cutting board. Realistic photo.",
    "sort":       "Several different types of musical instruments arranged together on a table -- an acoustic guitar, a violin, a flute, and a drum. Realistic photo.",
    "subtract":   "A school chalkboard showing a subtraction math problem, a teacher pointing at it while young students watch. Realistic classroom photo.",
    "tight":      "A close-up of a thick rope tied into several very tight knots, clearly hard to untie. Realistic photo, detailed.",
    "virtual":    "A person wearing a virtual reality headset, reaching out a hand into a glowing digital environment. Realistic photo, dramatic lighting.",
    "weigh":      "A small dog sitting calmly on a weighing scale at a vet clinic, the dial showing its weight. Realistic photo.",
    "whisper":    "Two students sitting in a quiet library, one whispering a secret into the other's ear with a finger to the lips. Realistic photo, soft light.",
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
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 28).first()
        if not unit:
            print("Unit 28 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 28\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} -- no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit28/{word_lower}.png"

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
