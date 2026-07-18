"""
Generate the branded Weekly Exam PDF for Book 2 Units 11-15.

Output: ./Weekly_Exam_Book2_Units_11-15.pdf in the project root.
No git commit, no upload — purely local artifact for the teacher.

Usage:
    python tools/generate_exam_units11_15.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.book import Book, Unit, Word
from app.pdf_generator import generate_branded_exam_pdf

EXAM_TITLE = "Weekly Exam"
INSTRUCTOR = "Mr. Hassan"
EYEBROW = "ESL VOCABULARY  ·  BOOK 2"
UNIT_RANGE = (11, 15)
NUM_IMAGE_Q = 20
NUM_BLANK_Q = 10
OUT_FILE = f"Weekly_Exam_Book2_Units_{UNIT_RANGE[0]}-{UNIT_RANGE[1]}.pdf"


def main():
    db = SessionLocal()
    try:
        book = db.query(Book).filter(Book.book_number == 2).first()
        if not book:
            print("Book 2 not found. Run tools/seed_db.py first.")
            sys.exit(1)

        units = (
            db.query(Unit)
            .filter(
                Unit.book_id == book.id,
                Unit.unit_number >= UNIT_RANGE[0],
                Unit.unit_number <= UNIT_RANGE[1],
            )
            .order_by(Unit.unit_number)
            .all()
        )
        if not units:
            print(f"No units found in Book 2 between {UNIT_RANGE[0]} and {UNIT_RANGE[1]}.")
            sys.exit(1)

        unit_ids = [u.id for u in units]
        words = (
            db.query(Word)
            .filter(Word.unit_id.in_(unit_ids))
            .order_by(Word.unit_id, Word.position)
            .all()
        )

        with_images = sum(1 for w in words if w.image_url)
        print(f"Pool: {len(words)} words across Units {UNIT_RANGE[0]}-{UNIT_RANGE[1]} ({with_images} with images).")
        if with_images < NUM_IMAGE_Q:
            print(f"WARNING: only {with_images} words have images; requested {NUM_IMAGE_Q}. PDF will use all available.")

        pdf_bytes = generate_branded_exam_pdf(
            word_pool=words,
            num_image_q=NUM_IMAGE_Q,
            num_blank_q=NUM_BLANK_Q,
            exam_title=EXAM_TITLE,
            instructor=INSTRUCTOR,
            unit_label=f"Units {UNIT_RANGE[0]} – {UNIT_RANGE[1]}",
            eyebrow=EYEBROW,
        )

        with open(OUT_FILE, "wb") as f:
            f.write(pdf_bytes)
        print(f"\nWrote {OUT_FILE} ({len(pdf_bytes):,} bytes).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
