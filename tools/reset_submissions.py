"""
reset_submissions.py — Wipe all submission data so students start fresh.
Safe to re-run; skips silently if tables are already empty.

Run: python tools/reset_submissions.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401

Base.metadata.create_all(bind=engine)
db = SessionLocal()

from app.models.submission import Submission, SubmissionAnswer
from app.models.homework import HomeworkAssignment, HomeworkQuestion, AssignmentStudent, HWReading

answers_deleted = db.query(SubmissionAnswer).delete()
subs_deleted    = db.query(Submission).delete()

# Assignments to delete on every deploy
REMOVE_TITLES = [
    "Unit 2 Reading - Tell Us About Your Free Time",
    "Unit 7 Reading - Free Time",
    "Grammar_Comparatives",
]
removed = 0
for title in REMOVE_TITLES:
    hw = db.query(HomeworkAssignment).filter_by(title=title).first()
    if hw:
        db.query(HomeworkQuestion).filter_by(assignment_id=hw.id).delete()
        db.query(AssignmentStudent).filter_by(assignment_id=hw.id).delete()
        db.query(HWReading).filter_by(assignment_id=hw.id).delete()
        db.delete(hw)
        removed += 1
        print(f"  Deleted assignment: '{title}'")

db.commit()
db.close()

print(f"Submissions reset: {subs_deleted} submissions, {answers_deleted} answers deleted. {removed} assignment(s) removed.")
