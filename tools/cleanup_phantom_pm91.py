"""
cleanup_phantom_pm91.py — Remove phantom submissions created by an older
version of restore_pm91_submissions.py.

Background:
    restore_pm91_submissions.py used to run on every Render deploy. It
    iterated over every active PM 91 assignment and fabricated a "submitted"
    row for Baneen Raad / Murtadha Khaled / Hussein Ali Abdulameer with a
    hardcoded score (80% / 100% / 75%). That meant every freshly uploaded
    homework for class PM 91 immediately showed those 3 students as having
    submitted — before they could actually do the work.

What this script does:
    Lists submissions for those 3 students grouped by assignment. With
    --apply, it deletes the phantom rows for a specific assignment so the
    students appear as "Not Started" again and can do the homework properly.

Usage:
    # 1. Dry-run — see what's in the DB for the 3 students:
    python tools/cleanup_phantom_pm91.py

    # 2. Target a specific assignment (still dry-run):
    python tools/cleanup_phantom_pm91.py --assignment-id 42

    # 3. Actually delete phantoms for assignment 42:
    python tools/cleanup_phantom_pm91.py --assignment-id 42 --apply

    # 4. Delete phantoms from ALL assignments newer than a cutoff date
    #    (use when bulk-cleaning after the restore script was removed):
    python tools/cleanup_phantom_pm91.py --since 2026-05-13 --apply

Safety:
    - Default mode is dry-run; no rows are touched without --apply.
    - Only deletes Submission + SubmissionAnswer rows for the 3 named students.
    - Never touches HomeworkAssignment, HomeworkQuestion, or any other table.
    - Never touches submissions for students outside the 3-name list.
"""

import argparse
import sys
import os
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.user import User
from app.models.homework import HomeworkAssignment
from app.models.submission import Submission, SubmissionAnswer

Base.metadata.create_all(bind=engine)

TARGET_NAMES = ["Baneen Raad", "Murtadha Khaled", "Hussein Ali Abdulameer"]


def find_target_students(db):
    found = []
    for name in TARGET_NAMES:
        u = (
            db.query(User)
            .filter(User.role == "student", User.display_name.ilike(name))
            .first()
        )
        if u is None:
            u = (
                db.query(User)
                .filter(User.role == "student", User.display_name.ilike(name + "%"))
                .first()
            )
        if u is None:
            u = (
                db.query(User)
                .filter(
                    User.role == "student",
                    User.username.ilike(name.replace(" ", "_").lower()),
                )
                .first()
            )
        if u:
            found.append(u)
    return found


def list_submissions(db, students, assignment_id=None, since=None):
    """Return rows: (assignment, student, submission)."""
    q = (
        db.query(HomeworkAssignment, User, Submission)
        .join(Submission, Submission.assignment_id == HomeworkAssignment.id)
        .join(User, User.id == Submission.student_id)
        .filter(Submission.student_id.in_([s.id for s in students]))
    )
    if assignment_id is not None:
        q = q.filter(HomeworkAssignment.id == assignment_id)
    if since is not None:
        q = q.filter(HomeworkAssignment.created_at >= since)
    return q.order_by(HomeworkAssignment.id, User.display_name).all()


def fmt_row(hw, student, sub):
    when = sub.submitted_at.strftime("%Y-%m-%d %H:%M") if sub.submitted_at else "—"
    score = f"{float(sub.score):.0f}%" if sub.score is not None else "—"
    cc = sub.correct_count if sub.correct_count is not None else "?"
    tot = sub.total_questions if sub.total_questions is not None else "?"
    return (
        f"  hw#{hw.id:<4} {hw.type:<14} {hw.title[:38]:<38} | "
        f"{student.display_name[:22]:<22} | {score:>5} ({cc}/{tot}) | submitted {when}"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--assignment-id", type=int, default=None,
                        help="Limit to a single assignment ID.")
    parser.add_argument("--since", type=str, default=None,
                        help="Only consider assignments created on/after this date (YYYY-MM-DD).")
    parser.add_argument("--apply", action="store_true",
                        help="Actually delete matching rows. Without this flag, the script only lists.")
    args = parser.parse_args()

    since = None
    if args.since:
        try:
            since = datetime.strptime(args.since, "%Y-%m-%d").date()
            since = datetime.combine(since, datetime.min.time())
        except ValueError:
            print(f"Bad --since value '{args.since}'. Use YYYY-MM-DD.")
            sys.exit(2)

    db = SessionLocal()
    try:
        students = find_target_students(db)
        if not students:
            print("No target students found in the database. Nothing to do.")
            return
        print(f"Target students ({len(students)}):")
        for s in students:
            print(f"  - {s.display_name} (id={s.id}, class={s.class_name})")
        print()

        rows = list_submissions(db, students, args.assignment_id, since)
        if not rows:
            print("No submissions match the filter. Nothing to clean.")
            return

        print(f"Submissions found ({len(rows)}):")
        for hw, student, sub in rows:
            print(fmt_row(hw, student, sub))
        print()

        if not args.apply:
            print("DRY-RUN — no rows deleted.")
            print("Re-run with --apply (and the same --assignment-id / --since filters)")
            print("to actually delete the listed submissions.")
            return

        if args.assignment_id is None and since is None:
            print("Refusing to delete without --assignment-id or --since filter.")
            print("Pick one to scope the deletion. Aborting.")
            sys.exit(3)

        sub_ids = [sub.id for _, _, sub in rows]
        ans_deleted = (
            db.query(SubmissionAnswer)
            .filter(SubmissionAnswer.submission_id.in_(sub_ids))
            .delete(synchronize_session=False)
        )
        sub_deleted = (
            db.query(Submission)
            .filter(Submission.id.in_(sub_ids))
            .delete(synchronize_session=False)
        )
        db.commit()
        print(f"Deleted {sub_deleted} submission(s) and {ans_deleted} answer row(s).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
