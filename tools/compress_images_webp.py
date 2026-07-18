"""
Convert all card images under app/static/images/ from PNG to WebP
(quality 82, max 1024px long edge — ~11x smaller, no visible loss on
these photo-style cards) so the full set fits in the git repo for free
static hosting on Render.

Originals are NOT deleted: each PNG is moved to Books/png_originals/
(gitignored) mirroring the same book/unit path, since regenerating them
costs real API money.

Idempotent: skips PNGs whose .webp already exists; safe to re-run.

Run: py tools/compress_images_webp.py
"""

import os
import shutil
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_ROOT = os.path.join(ROOT, "app", "static", "images")
ARCHIVE_ROOT = os.path.join(ROOT, "Books", "png_originals")

QUALITY = 82
MAX_EDGE = 1024


def main():
    converted = skipped = errors = 0
    bytes_in = bytes_out = 0

    for dirpath, _dirs, files in os.walk(IMAGES_ROOT):
        for name in sorted(files):
            if not name.lower().endswith(".png"):
                continue
            png_path = os.path.join(dirpath, name)
            webp_path = os.path.splitext(png_path)[0] + ".webp"

            rel = os.path.relpath(png_path, IMAGES_ROOT)
            archive_path = os.path.join(ARCHIVE_ROOT, rel)

            try:
                if not os.path.exists(webp_path):
                    with Image.open(png_path) as im:
                        im = im.convert("RGB")
                        im.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
                        im.save(webp_path, "WEBP", quality=QUALITY, method=4)
                    converted += 1
                else:
                    skipped += 1
                bytes_in += os.path.getsize(png_path)
                bytes_out += os.path.getsize(webp_path)

                os.makedirs(os.path.dirname(archive_path), exist_ok=True)
                shutil.move(png_path, archive_path)
            except Exception as e:
                errors += 1
                print(f"  ERROR {rel}: {e}")

    print(f"converted {converted}, skipped (already existed) {skipped}, errors {errors}")
    print(f"{bytes_in / 1048576:.0f} MB PNG -> {bytes_out / 1048576:.0f} MB WebP")
    print(f"originals archived to {ARCHIVE_ROOT}")
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
