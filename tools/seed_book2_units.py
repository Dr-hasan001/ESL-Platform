"""
Reseed Book 2 unit word lists from tools/words_book2.json.

Why this exists: Book 2 Units 1-5 were seeded from a generic academic word
list (Achieve, Accurate, Adult ... View -- straight down the alphabet, with
British spellings) rather than from 4000 Essential English Words Book 2. Units
6-30 were seeded per unit from the book itself and are correct. This tool
replaces a unit's twenty words in place, transcribed from the book.

Rows are UPDATED, not deleted and re-inserted, so word ids survive and anything
pointing at them (homework, submissions, progress) stays intact. When a row's
headword actually changes, its image_url is cleared -- the old picture belongs
to the old word, and the file on disk is named after it.

JSON shape:
    {"2": [{"word", "pos", "definition", "example"}, ... x20], ...}

Run: python tools/seed_book2_units.py <unit> [<unit> ...]
     python tools/seed_book2_units.py 2
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.book import Book, Unit, Word

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "words_book2.json")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    units = [int(a) for a in sys.argv[1:]]

    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    book = db.query(Book).filter(Book.book_number == 2).first()
    if not book:
        print("ERROR: Book 2 not found.")
        db.close()
        sys.exit(1)

    for un in units:
        entries = data.get(str(un))
        if not entries:
            print(f"  skip unit {un}: not in words_book2.json")
            continue
        unit = db.query(Unit).filter(Unit.book_id == book.id,
                                     Unit.unit_number == un).first()
        if not unit:
            print(f"  skip unit {un}: no Unit record")
            continue

        rows = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        changed = cleared = added = 0

        for i, entry in enumerate(entries):
            if i < len(rows):
                w = rows[i]
            else:
                w = Word(unit_id=unit.id, position=i + 1, word=entry["word"])
                db.add(w)
                added += 1
            if (w.word or "").lower() != entry["word"].lower() and w.image_url:
                w.image_url = None          # old picture belongs to the old word
                cleared += 1
            if w.word != entry["word"]:
                changed += 1
            w.position = i + 1
            w.word = entry["word"]
            w.part_of_speech = entry.get("pos")
            w.definition = entry.get("definition")
            w.example = entry.get("example")
            # Every field that describes the word must be rewritten, not just the
            # ones we happen to have data for. Leaving arabic_translation alone
            # left the OLD word's Arabic sitting under the new headword.
            w.arabic_translation = entry.get("ar")

        for extra in rows[len(entries):]:    # unit shrank -- drop the leftovers
            db.delete(extra)

        db.commit()
        print(f"  unit {un}: {len(entries)} words "
              f"({changed} headwords changed, {cleared} images unlinked, {added} added)")

    db.close()


if __name__ == "__main__":
    main()
