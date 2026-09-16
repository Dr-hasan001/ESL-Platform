"""
Generate the picture-card images for the B1 speaking examination.

Reads the card definitions (and their image prompts) straight out of
tools/exam_b1_speaking_cards.json, so the prompt lives next to the card it
belongs to and there is only one place to edit.

COSTS CREDITS. Existing files are skipped unless --force is passed.

Usage:
    py tools/generate_speaking_card_images.py                 # only missing cards
    py tools/generate_speaking_card_images.py --only 3        # just card 3
    py tools/generate_speaking_card_images.py --force         # redo everything
    py tools/generate_speaking_card_images.py --dry-run       # show plan, spend nothing
"""

import base64
import json
import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_IMAGE_MODEL", "openai/gpt-5.4-image-2")
CONFIG = os.path.join(HERE, "exam_b1_speaking_cards.json")

# A 4:3 landscape frame sits in the Part B block; ask for it explicitly so the
# renderer never has to crop a face out of the picture.
STYLE_SUFFIX = (
    " Landscape 4:3 composition with the main subject centred and clear space "
    "around the edges. Absolutely no text, letters, numbers or written signs "
    "anywhere in the image."
)


def generate_image(prompt: str) -> bytes | None:
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://esl-vocab-app.local",
            "X-Title": "ESL Speaking Cards",
        },
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": f"Generate an image: {prompt}"}],
            "modalities": ["image", "text"],
        },
        timeout=180,
    )

    if resp.status_code != 200:
        print(f"    ERROR {resp.status_code}: {resp.text[:300]}")
        return None

    message = resp.json().get("choices", [{}])[0].get("message", {})

    candidates = list(message.get("images") or [])
    content = message.get("content")
    if isinstance(content, list):
        candidates += content

    for part in candidates:
        if not isinstance(part, dict):
            continue
        url = (part.get("image_url") or {}).get("url", "")
        if url.startswith("data:image"):
            return base64.b64decode(url.split(",", 1)[1])
        if url.startswith("http"):
            return requests.get(url, timeout=60).content

    print(f"    WARNING: no image data in response ({str(message)[:160]})")
    return None


def main():
    args = sys.argv[1:]
    force = "--force" in args
    dry = "--dry-run" in args
    only = int(args[args.index("--only") + 1]) if "--only" in args else None

    if not API_KEY and not dry:
        sys.exit("OPENROUTER_API_KEY not set in .env")

    os.chdir(ROOT)
    with open(CONFIG, encoding="utf-8") as f:
        cfg = json.load(f)

    cards = [c for c in cfg["cards"] if only is None or c["num"] == only]
    print(f"Model: {MODEL}")
    print(f"{len(cards)} card(s) selected"
          f"{'  [DRY RUN — nothing will be generated]' if dry else ''}\n")

    made = skipped = failed = 0
    for card in cards:
        out = card["image"]
        os.makedirs(os.path.dirname(out), exist_ok=True)
        label = f"Card {card['num']} — {card['theme']}"

        if os.path.exists(out) and not force:
            print(f"  {label:<32} exists, skipping")
            skipped += 1
            continue

        if dry:
            print(f"  {label:<32} would generate -> {out}")
            continue

        print(f"  {label:<32} generating...", end=" ", flush=True)
        data = None
        for attempt in range(3):
            try:
                data = generate_image(card["image_prompt"] + STYLE_SUFFIX)
                if data:
                    break
            except Exception as e:
                print(f"\n    retry {attempt + 1}/3 after {type(e).__name__}: {e}")
            time.sleep(3)

        if data:
            with open(out, "wb") as f:
                f.write(data)
            print(f"saved ({len(data):,} bytes)")
            made += 1
        else:
            print("FAILED")
            failed += 1
        time.sleep(1)

    print(f"\nGenerated {made}, skipped {skipped}, failed {failed}.")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
