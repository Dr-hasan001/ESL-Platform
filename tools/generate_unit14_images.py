"""
Generate AI images for Book 2 Unit 14 vocabulary words using OpenRouter's
Google Gemini 3.1 Flash Image Preview model, then update the database.

Usage:
    python tools/generate_unit14_images.py
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
OUT_DIR = os.path.join("app", "static", "images", "book2", "unit14")

WORD_PROMPTS = {
    "apparent":   "A woman with a clearly visible bright smile of joy on her face, expressing apparent happiness. Realistic close-up portrait photo.",
    "blind":      "A blind man wearing dark sunglasses walking confidently with a long white cane on a city sidewalk. Realistic photo.",
    "calculate":  "A student carefully working out a math problem on paper using a calculator and pencil at a desk. Realistic photo.",
    "chat":       "Two friends sitting at a cafe table laughing and chatting over cups of coffee. Realistic warm photo.",
    "commit":     "Two people firmly shaking hands across a desk to commit to an agreement, with a contract on the table. Realistic photo.",
    "compose":    "An artist arranging puzzle pieces together to compose a whole picture on a wooden table. Realistic close-up photo.",
    "dormitory":  "A college dormitory bedroom with two beds, desks, and decorations, where students live together. Realistic photo.",
    "exhaust":    "A swimmer collapsed on the pool deck looking completely exhausted after swimming all day. Realistic photo.",
    "greenhouse": "A small glass greenhouse in a backyard filled with green plants, tomatoes, and herbs growing inside. Realistic photo.",
    "ignore":     "A girl studying at a desk with focus, ignoring text messages popping up on her phone. Realistic photo.",
    "obvious":    "A man fast asleep with his head resting on his arms at a desk, obviously very tired. Realistic photo.",
    "physics":    "A physics class with students watching a Newton's cradle in action, showing energy transfer. Realistic photo, classroom.",
    "portion":    "A pizza cut into slices, with one small portion served on a plate next to the rest of the pizza. Realistic photo.",
    "remind":     "A father pointing at his son's homework on the table, reminding him to finish it. Realistic photo, home setting.",
    "secretary":  "A professional secretary working at a tidy office desk with a computer, papers, and a phone. Realistic photo.",
    "severe":     "A man holding his hand in pain after hitting it with a hammer, with a wince of severe discomfort. Realistic photo.",
    "talent":     "A young girl playing the piano beautifully on a grand stage, showing her musical talent. Realistic photo.",
    "thesis":     "A university student presenting a thesis paper at a podium, with professors listening attentively. Realistic photo.",
    "uniform":    "A school marching band lined up in matching uniforms, holding their instruments in formation. Realistic photo.",
    "vision":     "An eye doctor examining a patient's vision using a vision test chart in a clinic. Realistic photo.",
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
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 14).first()
        if not unit:
            print("Unit 14 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Found {len(words)} words in Book 2 Unit 14\n")

        for w in words:
            word_lower = w.word.lower()
            prompt = WORD_PROMPTS.get(word_lower)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} -- no prompt defined, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{word_lower}.png")
            static_url = f"/static/images/book2/unit14/{word_lower}.png"

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
