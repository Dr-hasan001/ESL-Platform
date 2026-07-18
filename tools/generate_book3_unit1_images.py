"""
Generate AI images for Book 3 (B1) Unit 1 using Nano Banana 1
(google/gemini-2.5-flash-image) via OpenRouter, update the DB,
and report the ACTUAL billed cost summed across the whole unit.

Usage:
    python tools/generate_book3_unit1_images.py
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
MODEL = "google/gemini-2.5-flash-image"  # Nano Banana 1
OUT_DIR = os.path.join("app", "static", "images", "book3", "unit1")

WORD_PROMPTS = {
    "acre":        "A vast green farm field stretching to the horizon, many acres of farmland under a blue sky. Realistic aerial photo.",
    "afterlife":   "An ethereal heavenly scene with soft glowing clouds and warm rays of light, symbolizing the afterlife. Realistic atmospheric photo.",
    "archaeology": "An archaeologist carefully brushing dust off ancient pottery at a desert excavation site near old stone ruins. Realistic photo.",
    "chamber":     "A large formal meeting chamber with a long polished wooden table and ornate walls. Realistic interior photo.",
    "channel":     "A narrow water channel carved between rocky cliffs with a clear stream flowing through it. Realistic nature photo.",
    "core":        "A close-up of a red apple sliced in half revealing the core with seeds at the center. Realistic photo.",
    "corridor":    "A long narrow corridor with doors on both sides leading down a building hallway. Realistic photo, soft lighting.",
    "distinct":    "One bright red apple standing out distinctly among a group of identical green apples. Realistic photo.",
    "elite":       "An exclusive elite private club lounge with luxurious furniture and elegantly dressed members. Realistic photo.",
    "engineer":    "An engineer in a workshop carefully designing and assembling a robot, technical blueprints nearby. Realistic photo.",
    "found":       "A businessman cutting a red ribbon at the grand opening of a newly founded bank building. Realistic photo.",
    "gap":         "A close-up of a small gap between two blocks of wood on a table. Realistic photo.",
    "glory":       "A breathtaking, magnificent golden sunset over mountains in all its glory. Realistic landscape photo.",
    "interior":    "The interior of a cozy, well-decorated living room seen from inside. Realistic interior photo, warm light.",
    "lion":        "A majestic male lion with a full mane standing proudly in the savanna. Realistic wildlife photo.",
    "role":        "A confident saleswoman in an office presenting products to a customer, fulfilling her role. Realistic photo.",
    "royal":       "A regal royal family wearing elegant crowns and robes in a grand palace hall. Realistic photo.",
    "sole":        "A single woman standing alone as the sole person in an otherwise empty meeting room. Realistic photo.",
    "stairs":      "A wide staircase with many steps inside a bright building. Realistic photo.",
    "surface":     "A close-up of a hand wiping the smooth surface of a wooden table with a cloth. Realistic photo.",
}


def ensure_output_dir():
    os.makedirs(OUT_DIR, exist_ok=True)


def generate_image(word: str, prompt: str):
    """Return (image_bytes | None, cost_usd | None)."""
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
        timeout=90,
    )

    if resp.status_code != 200:
        print(f"  ERROR {resp.status_code}: {resp.text[:300]}")
        return None, None

    data = resp.json()
    cost = (data.get("usage") or {}).get("cost")
    choices = data.get("choices", [])
    if not choices:
        print(f"  ERROR: no choices for '{word}'")
        return None, cost

    message = choices[0].get("message", {})

    def _decode(url):
        if url.startswith("data:image"):
            return base64.b64decode(url.split(",", 1)[1])
        if url.startswith("http"):
            return requests.get(url, timeout=30).content
        return None

    for part in message.get("images", []) or []:
        if isinstance(part, dict) and part.get("type") == "image_url":
            img = _decode(part.get("image_url", {}).get("url", ""))
            if img:
                return img, cost

    content = message.get("content", "")
    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") == "image_url":
                img = _decode(part.get("image_url", {}).get("url", ""))
                if img:
                    return img, cost

    print(f"  WARNING: no image data for '{word}'.")
    return None, cost


def main():
    if not OPENROUTER_API_KEY:
        print("OPENROUTER_API_KEY not set in .env")
        sys.exit(1)

    ensure_output_dir()
    db = SessionLocal()
    total_cost = 0.0
    cost_known = 0
    saved = 0
    try:
        book = db.query(Book).filter(Book.book_number == 3).first()
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 1).first()
        if not unit:
            print("Book 3 Unit 1 not found.")
            sys.exit(1)

        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        print(f"Model: {MODEL} (Nano Banana 1)")
        print(f"Found {len(words)} words in Book 3 Unit 1\n")

        for w in words:
            wl = w.word.lower()
            prompt = WORD_PROMPTS.get(wl)
            if not prompt:
                print(f"  [{w.position:2}] {w.word} -- no prompt, skipping")
                continue

            out_path = os.path.join(OUT_DIR, f"{wl}.png")
            static_url = f"/static/images/book3/unit1/{wl}.png"

            print(f"  [{w.position:2}] {w.word:12} ...", end=" ", flush=True)
            img_bytes, cost = None, None
            for attempt in range(3):
                try:
                    img_bytes, cost = generate_image(w.word, prompt)
                    break
                except Exception as e:
                    print(f"\n      retry {attempt+1}/3: {e}")
                    time.sleep(3)

            if cost is not None:
                total_cost += cost
                cost_known += 1

            if img_bytes:
                with open(out_path, "wb") as f:
                    f.write(img_bytes)
                w.image_url = static_url
                db.commit()
                saved += 1
                cstr = f"${cost:.5f}" if cost is not None else "cost n/a"
                print(f"saved ({len(img_bytes):,} B, {cstr})")
            else:
                print("FAILED -- keeping emoji")

            time.sleep(1)

        print("\n" + "=" * 48)
        print(f"Images saved : {saved}/{len(words)}")
        print(f"Billed images: {cost_known}")
        print(f"TOTAL COST   : ${total_cost:.4f}")
        if cost_known:
            print(f"Avg / image  : ${total_cost / cost_known:.5f}")
        print("=" * 48)

    finally:
        db.close()


if __name__ == "__main__":
    main()
