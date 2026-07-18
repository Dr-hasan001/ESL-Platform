"""
link_existing_images.py — Wire up Word.image_url for images already committed
to app/static/images/.

This is the FREE, no-API step that pairs with the cost-incurring
generate_unit*_images.py scripts. Generation happens manually, locally, once.
The resulting PNGs land in the repo. On every deploy this script walks the
directory tree and updates each matching Word row so the UI renders the image.

Path layout it expects:
    app/static/images/book{N}/unit{M}/{word}.png   (or .webp)

For each file it finds, it looks up:
    Book(book_number=N) → Unit(book_id=..., unit_number=M) → Word(unit_id=..., word ILIKE filename)
and sets Word.image_url = "/static/images/book{N}/unit{M}/{word}.png".

Safe to run on every deploy:
    - Idempotent (sets the same URL on the same row).
    - Never calls an external API.
    - Skips files with no matching Word row (prints a warning, no crash).
    - Skips Word rows with no matching file on disk (leaves image_url unchanged).
"""

import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401 — register all model classes
from app.models.book import Book, Unit, Word

Base.metadata.create_all(bind=engine)

# ── deploy-chain shim ────────────────────────────────────────────────────────
# The Render service runs a buildCommand stored in its dashboard settings (the
# repo's render.yaml is not applied), and that stored chain predates the
# Book 1 / Book 2 u27-30 / Book 3 / stories seeders. This script IS the last
# step of that stored chain, so newer idempotent seeders are run from here to
# guarantee they execute on every deploy. Remove once the dashboard
# buildCommand is updated to match render.yaml.
_PENDING_SEEDERS = [
    ["tools/seed_book1.py"],
    ["tools/seed_book2_unit27.py"],
    ["tools/seed_book2_unit28.py"],
    ["tools/seed_book2_unit29.py"],
    ["tools/seed_book2_unit30.py"],
    ["tools/seed_book3.py"],
    ["tools/seed_stories.py", "3"],
]


def run_pending_seeders():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for script in _PENDING_SEEDERS:
        path = os.path.join(root, script[0])
        if not os.path.exists(path):
            print(f"[seed-shim] missing {script[0]} — skipped")
            continue
        print(f"[seed-shim] running {' '.join(script)}")
        subprocess.run([sys.executable, path, *script[1:]], check=True, cwd=root)

IMAGES_ROOT = os.path.join("app", "static", "images")
PATH_RE = re.compile(r"book(\d+)[\\/]unit(\d+)[\\/]([^\\/]+)\.(png|webp)$", re.IGNORECASE)


def discover_pngs():
    """Yield (book_number, unit_number, word_filename, static_url) for every
    PNG/WebP under app/static/images/book*/unit*/. word_filename is lowercase,
    no extension. Sorted so .webp comes after .png — if both exist for a word,
    the .webp URL wins."""
    if not os.path.isdir(IMAGES_ROOT):
        return
    found = []
    for root, _dirs, files in os.walk(IMAGES_ROOT):
        for name in files:
            if not name.lower().endswith((".png", ".webp")):
                continue
            full = os.path.join(root, name)
            m = PATH_RE.search(full)
            if not m:
                continue
            book_num = int(m.group(1))
            unit_num = int(m.group(2))
            word_file = m.group(3).lower()
            ext = m.group(4).lower()
            static_url = f"/static/images/book{book_num}/unit{unit_num}/{word_file}.{ext}"
            found.append((ext == "webp", book_num, unit_num, word_file, static_url))
    for _webp_last, book_num, unit_num, word_file, static_url in sorted(found):
        yield book_num, unit_num, word_file, static_url


def main():
    run_pending_seeders()
    db = SessionLocal()
    try:
        linked = 0
        no_word = 0
        already = 0
        unmatched_files = []

        # Cache book + unit lookups so we don't re-query for every file
        book_cache: dict[int, Book] = {}
        unit_cache: dict[tuple[int, int], Unit] = {}

        for book_num, unit_num, word_file, static_url in discover_pngs():
            book = book_cache.get(book_num)
            if book is None:
                book = db.query(Book).filter(Book.book_number == book_num).first()
                if book is None:
                    unmatched_files.append(f"book{book_num}/unit{unit_num}/{word_file}.png (no Book)")
                    continue
                book_cache[book_num] = book

            key = (book.id, unit_num)
            unit = unit_cache.get(key)
            if unit is None:
                unit = (
                    db.query(Unit)
                    .filter(Unit.book_id == book.id, Unit.unit_number == unit_num)
                    .first()
                )
                if unit is None:
                    unmatched_files.append(f"book{book_num}/unit{unit_num}/{word_file}.png (no Unit)")
                    continue
                unit_cache[key] = unit

            # Match Word by case-insensitive equality on the filename stem.
            word = (
                db.query(Word)
                .filter(Word.unit_id == unit.id, Word.word.ilike(word_file))
                .first()
            )
            if word is None:
                no_word += 1
                unmatched_files.append(f"book{book_num}/unit{unit_num}/{word_file}.png (no Word row)")
                continue

            if word.image_url == static_url:
                already += 1
                continue

            word.image_url = static_url
            linked += 1

        db.commit()
        print(f"Linked {linked} new image URLs to Word rows.")
        print(f"  Already linked: {already}")
        print(f"  PNG files with no matching Word row: {no_word}")
        if unmatched_files and no_word <= 20:
            for line in unmatched_files[:20]:
                print(f"    - {line}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
