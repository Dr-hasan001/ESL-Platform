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

answers_deleted = db.query(SubmissionAnswer).delete()
subs_deleted    = db.query(Submission).delete()
db.commit()
db.close()

print(f"Submissions reset: {subs_deleted} submissions, {answers_deleted} answers deleted.")
