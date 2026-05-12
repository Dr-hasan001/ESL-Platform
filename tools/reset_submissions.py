"""
reset_submissions.py — Deploy hook for removing specific obsolete assignments.

DOES NOT WIPE SUBMISSIONS. Student work is preserved across deploys.

Run: python tools/reset_submissions.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401

Base.metadata.create_all(bind=engine)
db = SessionLocal()

from app.models.submission import Submission, SubmissionAnswer
from app.models.homework import (
    HomeworkAssignment, HomeworkQuestion, AssignmentStudent,
    HWReading, HWListening, HWGrammar, HWWriting, HWGeneralTopic,
)

# Assignments to delete on every deploy (full cleanup, including any submissions for them)
REMOVE_TITLES = [
    "Unit 2 Reading - Tell Us About Your Free Time",
    "Unit 7 Reading - Free Time",
    "Grammar_Comparatives",
]
removed = 0
for title in REMOVE_TITLES:
    hw = db.query(HomeworkAssignment).filter_by(title=title).first()
    if hw:
        # Delete only the submissions tied to THIS assignment, then the assignment itself.
        sub_ids = [s.id for s in db.query(Submission).filter(Submission.assignment_id == hw.id).all()]
        if sub_ids:
            db.query(SubmissionAnswer).filter(SubmissionAnswer.submission_id.in_(sub_ids)).delete(synchronize_session=False)
            db.query(Submission).filter(Submission.id.in_(sub_ids)).delete(synchronize_session=False)
        db.query(HomeworkQuestion).filter_by(assignment_id=hw.id).delete()
        db.query(AssignmentStudent).filter_by(assignment_id=hw.id).delete()
        db.query(HWReading).filter_by(assignment_id=hw.id).delete()
        db.query(HWListening).filter_by(assignment_id=hw.id).delete()
        db.query(HWGrammar).filter_by(assignment_id=hw.id).delete()
        db.query(HWWriting).filter_by(assignment_id=hw.id).delete()
        db.query(HWGeneralTopic).filter_by(assignment_id=hw.id).delete()
        db.delete(hw)
        removed += 1
        print(f"  Deleted assignment: '{title}'")

db.commit()
db.close()

print(f"Deploy cleanup complete. {removed} assignment(s) removed. Submissions preserved.")
