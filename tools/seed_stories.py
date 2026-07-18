"""
Seed unit reading stories (passage + comprehension questions) from
tools/stories_book{N}.json into UnitStory records. Upsert per unit — only
touches units present in the JSON (leaves other units' stories intact).

Run: python tools/seed_stories.py <book_number>
     e.g. python tools/seed_stories.py 1
"""

import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.book import Book, Unit, UnitStory

Base.metadata.create_all(bind=engine)

bn = int(sys.argv[1])
DATA = os.path.join(os.path.dirname(__file__), f"stories_book{bn}.json")
with open(DATA, encoding="utf-8") as f:
    data = json.load(f)

db = SessionLocal()
book = db.query(Book).filter(Book.book_number == bn).first()
if not book:
    print(f"ERROR: Book {bn} not found.")
    db.close()
    sys.exit(1)

n = 0
for un_str, story in sorted(data.items(), key=lambda kv: int(kv[0])):
    un = int(un_str)
    unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == un).first()
    if not unit:
        print(f"  skip unit {un}: no Unit record")
        continue
    title = story.get("title") or f"Unit {un}"
    html = story.get("story_html") or ""
    questions = story.get("questions") or []

    existing = db.query(UnitStory).filter(UnitStory.unit_id == unit.id).first()
    if existing:
        existing.story_title = title
        existing.story_html = html
        existing.story_questions = questions
    else:
        db.add(UnitStory(unit_id=unit.id, story_title=title,
                         story_html=html, story_questions=questions))
    n += 1
    print(f"  Unit {un}: '{title}' ({len(questions)} questions)")

db.commit()
db.close()
print(f"Done. Book {bn}: {n} stories seeded.")
