"""
One-off: generate a premium still-life cover image for the exam PDF
via OpenRouter (google/gemini-2.5-flash-image). Saves to tools/assets/exam_cover.png.

Usage:  py tools/generate_exam_cover.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from tools.generate_book3_images import generate_image

PROMPT = (
    "Generate an image: A premium, elegant academic still life for the cover of an "
    "English examination booklet. A classic fountain pen resting on a stack of old "
    "hardcover books beside a small brass hourglass, on a warm cream linen surface. "
    "Deep navy and antique gold tones, soft window light from the side, shallow depth "
    "of field, refined minimalist editorial composition, wide landscape 16:9 format. "
    "No text, letters, or words in the image."
)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "exam_cover.png")


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img, cost, err = generate_image(PROMPT)
    if err:
        print("FAILED:", err)
        sys.exit(1)
    with open(OUT, "wb") as f:
        f.write(img)
    print(f"Saved {OUT}  ({len(img)/1024:.0f} KB)  cost=${cost or 0:.4f}")


if __name__ == "__main__":
    main()
