"""
Generate AI images for Book 2 Unit 27 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit27_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit27")

WORD_PROMPTS = {
    "apology":    "A young woman with a sincere, regretful expression handing a small handwritten note to her teacher in a classroom. Realistic photo.",
    "bold":       "A confident lion standing proudly on a rocky cliff, mane blowing in the wind. Realistic wildlife photo.",
    "bug":        "A close-up macro photo of a colorful red ladybug with black spots crawling on a fresh green leaf. Realistic photo, bright daylight.",
    "capture":    "A child's hands cupped together gently holding a small butterfly in a sunny garden. Realistic close-up photo.",
    "duke":       "A regal man in elegant 17th-century European nobility clothing, wearing a velvet cloak and a small jeweled crown, standing in a grand hall. Realistic photo.",
    "expose":     "A man pulling open his plain black shirt to reveal a bright superhero costume underneath. Realistic photo, dramatic lighting.",
    "guilty":     "A young girl looking down at the floor with a sad guilty expression, her hand near an empty cookie jar on a kitchen counter. Realistic photo, warm light.",
    "hire":       "A businessman in a suit shaking hands with a smiling job candidate across an office desk, contract papers visible. Realistic photo.",
    "innocent":   "A judge in a black robe standing in a courtroom with a 'NOT GUILTY' verdict document in hand, a relieved woman standing beside. Realistic photo.",
    "language":   "A diverse group of four people of different ethnicities having a friendly conversation with speech bubbles containing text in different scripts (Arabic, Chinese, English) floating above. Realistic photo with subtle overlay.",
    "minister":   "A formal-looking man in a dark suit standing at a podium in front of a national flag inside a government chamber. Realistic photo.",
    "ordinary":   "A plain wooden kitchen table with a single glass of water and a regular white plate -- nothing unusual, completely normal. Realistic photo, neutral daylight.",
    "permanent":  "A weathered stone monument with deeply carved inscription standing in a quiet cemetery. Realistic photo, soft daylight.",
    "preserve":   "A man spraying a clear protective chemical from a can onto the wooden walls of a house exterior. Realistic photo, daytime.",
    "pronounce":  "A teacher in front of a chalkboard pointing at a written word, mouth open mid-pronunciation, attentive young students seated. Realistic photo.",
    "resemble":   "A father and his young son standing side by side, both wearing similar shirts, with strikingly similar facial features. Realistic portrait photo.",
    "symptom":    "A young man sitting on a sofa sneezing into a tissue with a thermometer and a cup of tea on the side table. Realistic photo, soft indoor light.",
    "tobacco":    "Dried brown tobacco leaves stacked on a wooden farm table next to a few unrolled cigars. Realistic photo, rustic warm light.",
    "twin":       "Two identical young sisters with matching dresses and pigtails, smiling at the camera side by side. Realistic photo.",
    "witch":      "A woman in a tall black pointed hat and dark cloak holding a wooden broomstick, mysterious forest in background. Realistic photo, atmospheric lighting.",
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
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 27).first()
        if not unit:
            print("Unit 27 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 27\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} -- no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit27/{word_lower}.png"

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
