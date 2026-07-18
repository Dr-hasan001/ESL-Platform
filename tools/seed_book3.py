"""
Seed Book 3 (B1) — all units — from tools/book3_words.json.
Words + emoji + Arabic only. NO images.
Idempotent: clears + re-inserts words per unit present in the JSON.
Run: python tools/seed_book3.py
"""

import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.book import Book, Unit, Word

Base.metadata.create_all(bind=engine)

DATA = os.path.join(os.path.dirname(__file__), "book3_words.json")
with open(DATA, encoding="utf-8") as f:
    data = json.load(f)

db = SessionLocal()
book = db.query(Book).filter(Book.book_number == 3).first()
if not book:
    print("ERROR: Book 3 not found.")
    db.close()
    sys.exit(1)

total = 0
for unit_number_str, words in sorted(data.items(), key=lambda kv: int(kv[0])):
    un = int(unit_number_str)
    unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == un).first()
    if not unit:
        print(f"  skip unit {un}: no Unit record")
        continue

    db.query(Word).filter(Word.unit_id == unit.id).delete()
    for w in sorted(words, key=lambda x: x["position"]):
        db.add(Word(
            unit_id=unit.id,
            position=w["position"],
            word=w["word"],
            emoji=w.get("emoji"),
            part_of_speech=w.get("part_of_speech"),
            definition=w.get("definition"),
            example=w.get("example"),
            arabic_translation=w.get("arabic"),
            derivatives=w.get("derivatives") or [],
        ))
    unit.word_count = len(words)
    total += len(words)
    print(f"  Unit {un}: {len(words)} words")

db.commit()
db.close()
print(f"Done. Book 3: {total} words across {len(data)} units (no images).")
