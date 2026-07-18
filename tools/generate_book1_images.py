"""
Generate AI images for Book 1 (A1) units with Nano Banana 1
(google/gemini-2.5-flash-image) via OpenRouter.

- Prompts auto-built from each word's definition + example.
- SAFE_PROMPTS overrides for words the content filter would block.
- Concurrent, resumable (skips existing PNGs), tracks billed cost.

Usage:
    python tools/generate_book1_images.py <start_unit> <end_unit>
    e.g.  python tools/generate_book1_images.py 1 7
"""

import base64
import os
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.book import Word, Unit, Book

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "google/gemini-2.5-flash-image"  # Nano Banana 1
MAX_WORKERS = 5

# Safe, concept-appropriate prompts for words whose definition/example trips the
# image model's content filter. Keyed by lowercase headword. Use the textbook's
# own (benign) example where possible so the image still teaches the word.
SAFE_PROMPTS = {
    "kill": ("Generate an image: A hand holding a flyswatter about to swat a single small "
             "fly resting on a kitchen table. Realistic close-up photo, natural lighting, "
             "no text, letters, or words in the image."),
    "evil": ("Generate an image: A dark, spooky old haunted house at night with one eerie "
             "glowing window and rolling fog, ominous mysterious mood. Realistic atmospheric "
             "photo, no text, letters, or words in the image."),
    "scare": ("Generate an image: A person with a wide-eyed, startled and frightened "
              "expression, hands raised defensively. Realistic portrait photo, natural "
              "lighting, no text, letters, or words in the image."),
    "punish": ("Generate an image: A young child standing facing the corner of a classroom "
               "as a mild time-out, a teacher seated at a desk in the background. Realistic "
               "photo, soft lighting, no text, letters, or words in the image."),
    "harm": ("Generate an image: A hot clothes iron standing on an ironing board with a hand "
             "cautiously pulling back from it. Realistic photo, natural lighting, no text, "
             "letters, or words in the image."),
    "alcohol": ("Generate an image: Several bottles of wine and beer arranged on a wooden bar "
                "counter. Realistic product photo, warm lighting, no text, letters, or words "
                "in the image."),
}


def build_prompt(word, definition, example):
    override = SAFE_PROMPTS.get(word.lower())
    if override:
        return override
    scene = " ".join(p for p in (definition, example) if p)
    return (
        f"Generate an image: A clear, realistic photograph illustrating the concept of "
        f"\"{word}\". {scene} Natural lighting, no text, letters, or words in the image."
    )


def generate_image(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://esl-vocab-app.local",
        "X-Title": "ESL Vocabulary Cards",
    }
    payload = {"model": MODEL, "messages": [{"role": "user", "content": prompt}]}
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers, json=payload, timeout=120,
    )
    if resp.status_code != 200:
        return None, None, f"HTTP {resp.status_code}: {resp.text[:160]}"
    data = resp.json()
    cost = (data.get("usage") or {}).get("cost")
    choices = data.get("choices", [])
    if not choices:
        return None, cost, "no choices"
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
                return img, cost, None
    content = message.get("content", "")
    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") == "image_url":
                img = _decode(part.get("image_url", {}).get("url", ""))
                if img:
                    return img, cost, None
    return None, cost, "no image in response"


def main():
    if not OPENROUTER_API_KEY:
        print("OPENROUTER_API_KEY not set")
        sys.exit(1)
    start, end = int(sys.argv[1]), int(sys.argv[2])

    db = SessionLocal()
    book = db.query(Book).filter(Book.book_number == 1).first()
    tasks = []
    for un in range(start, end + 1):
        unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == un).first()
        if not unit:
            continue
        out_dir = os.path.join("app", "static", "images", "book1", f"unit{un}")
        os.makedirs(out_dir, exist_ok=True)
        for w in db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all():
            wl = w.word.lower()
            tasks.append((
                un, w.id, w.word,
                os.path.join(out_dir, f"{wl}.png"),
                f"/static/images/book1/unit{un}/{wl}.png",
                build_prompt(w.word, w.definition, w.example),
            ))
    db.close()

    todo = [t for t in tasks if not os.path.exists(t[3])]
    print(f"Model: {MODEL} (Nano Banana 1)")
    print(f"Units {start}-{end}: {len(tasks)} words, {len(todo)} to generate, "
          f"{len(tasks) - len(todo)} already on disk\n")

    lock = threading.Lock()
    state = {"cost": 0.0, "billed": 0, "done": 0, "fail": 0}

    def work(t):
        un, wid, word, out_path, static_url, prompt = t
        img = cost = err = None
        for attempt in range(3):
            try:
                img, cost, err = generate_image(prompt)
                if img:
                    break
            except Exception as e:
                err = str(e)
                time.sleep(2)
        with lock:
            if cost is not None:
                state["cost"] += cost
                state["billed"] += 1
            if img:
                with open(out_path, "wb") as f:
                    f.write(img)
                state["done"] += 1
                print(f"  u{un:<2} {word:<14} ${cost:.5f}  "
                      f"[{state['done']}/{len(todo)}] running ${state['cost']:.4f}", flush=True)
            else:
                state["fail"] += 1
                print(f"  u{un:<2} {word:<14} FAILED ({err})", flush=True)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = [ex.submit(work, t) for t in todo]
        for _ in as_completed(futs):
            pass

    db = SessionLocal()
    updated = 0
    for un, wid, word, out_path, static_url, prompt in tasks:
        if os.path.exists(out_path):
            w = db.get(Word, wid)
            if w and w.image_url != static_url:
                w.image_url = static_url
                updated += 1
    db.commit()
    db.close()

    print("\n" + "=" * 52)
    print(f"Generated this run : {state['done']}   Failed: {state['fail']}")
    print(f"DB image_url set   : {updated}")
    print(f"TOTAL BILLED COST  : ${state['cost']:.4f} over {state['billed']} calls")
    if state["billed"]:
        print(f"Avg / image        : ${state['cost'] / state['billed']:.5f}")
    print("=" * 52)


if __name__ == "__main__":
    main()
