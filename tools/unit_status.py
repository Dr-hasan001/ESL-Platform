"""Print status of every unit: word count, story, questions."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.book import Book, Unit, Word, UnitStory

db = SessionLocal()
books = db.query(Book).order_by(Book.id).all()

for book in books:
    print(f"\nBook {book.book_number} ({book.cefr_level})")
    print("-" * 50)
    units = db.query(Unit).filter(Unit.book_id == book.id).order_by(Unit.unit_number).all()
    for unit in units:
        words = db.query(Word).filter(Word.unit_id == unit.id).count()
        story = db.query(UnitStory).filter(UnitStory.unit_id == unit.id).first()
        if story:
            q_count = len(story.story_questions) if story.story_questions else 0
            story_status = f"Story ({q_count}Q)"
        else:
            story_status = "No story"
        print(f"  Unit {unit.unit_number:2d}: {words:2d} words | {story_status}")

db.close()
