"""
restore_pm91_submissions.py

ONE-TIME restore tool for three PM 91 students whose submissions were wiped
by an earlier reset_submissions.py deploy:
    Baneen Raad
    Murtadha khaled (a.k.a. Murtadha Khaled / Murtadha khaled)
    Hussein Ali Abdul

⚠️  THIS SCRIPT IS DANGEROUS IF LEFT IN THE DEPLOY CHAIN.
   It iterates over EVERY active PM 91 assignment, so every time a teacher
   uploads a new homework for class PM 91, this script will fabricate a fake
   submission for the three named students with a hardcoded score (80/75/100).
   It ALSO deletes any real submission whose score doesn't match the hardcode
   and replaces it with a fake one — silent data loss.

   It is REMOVED from render.yaml. To re-run for a genuine one-off restore,
   set the environment variable ALLOW_PM91_RESTORE=1 before invoking, e.g.:
       ALLOW_PM91_RESTORE=1 python tools/restore_pm91_submissions.py
"""

import sys, os
from datetime import datetime, timezone

if not os.environ.get("ALLOW_PM91_RESTORE"):
    print("restore_pm91_submissions.py: ALLOW_PM91_RESTORE is not set — skipping.")
    print("This script is intentionally gated to prevent fabricating submissions.")
    sys.exit(0)

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.user import User
from app.models.homework import HomeworkAssignment, AssignmentStudent, HomeworkQuestion
from app.models.submission import Submission, SubmissionAnswer

Base.metadata.create_all(bind=engine)

# Recalled scores, per student
TARGET_STUDENTS = [
    {"name": "Baneen Raad",            "score": 80},
    {"name": "Murtadha Khaled",        "score": 100},
    {"name": "Hussein Ali Abdulameer", "score": 75},
]
TARGET_CLASS = "PM 91"


def find_students(db):
    """Return list of (User, target_score) tuples."""
    found = []
    for entry in TARGET_STUDENTS:
        name = entry["name"]
        score = entry["score"]
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
                .filter(User.role == "student", User.username.ilike(name.replace(" ", "_")))
                .first()
            )
        if u:
            found.append((u, score))
            print(f"  Found: {u.display_name} (id={u.id}, class={u.class_name}) -> target {score}%")
        else:
            print(f"  NOT FOUND: {name}")
    return found


def class_assignments(db):
    """Return all active assignments scoped to PM 91, or where these students
    are already in the assignment_students table."""
    by_class = db.query(HomeworkAssignment).filter(
        HomeworkAssignment.is_active == True,
        HomeworkAssignment.class_name == TARGET_CLASS,
    ).all()
    return by_class


def _wrong_index(correct_index: int | None, options: list | None) -> int | None:
    """Pick any option index that isn't the correct one. Falls back to 0."""
    if not options:
        return None
    for i in range(len(options)):
        if i != correct_index:
            return i
    return 0


def restore_for(db, student: User, assignment: HomeworkAssignment, target_score: int) -> bool:
    """Create or replace a Submission with the target score (% correct).
    Returns True if a row was created or replaced."""
    questions = (
        db.query(HomeworkQuestion)
        .filter(HomeworkQuestion.assignment_id == assignment.id)
        .order_by(HomeworkQuestion.position)
        .all()
    )
    total = len(questions)
    if total == 0:
        print(f"    skip — '{assignment.title}' has no questions")
        return False

    correct_target = round(total * target_score / 100)

    # Check existing submission state.
    existing_list = (
        db.query(Submission)
        .filter(Submission.assignment_id == assignment.id, Submission.student_id == student.id)
        .all()
    )
    if len(existing_list) == 1:
        ex = existing_list[0]
        already_matches = (
            ex.score is not None
            and float(ex.score) == float(target_score)
            and ex.correct_count == correct_target
            and ex.total_questions == total
        )
        if already_matches:
            print(f"    skip — {student.display_name} already at {target_score}% on '{assignment.title}'")
            return False
    # Replace existing rows so the score matches the target.
    for old in existing_list:
        db.query(SubmissionAnswer).filter(SubmissionAnswer.submission_id == old.id).delete(synchronize_session=False)
        db.delete(old)
    if existing_list:
        db.commit()

    sub = Submission(
        assignment_id=assignment.id,
        student_id=student.id,
        submitted_at=datetime.now(timezone.utc),
        is_complete=True,
        total_questions=total,
        correct_count=correct_target,
        score=float(target_score),
    )
    db.add(sub)
    db.flush()

    # First correct_target questions get correct answers; rest get a deliberately wrong index.
    for idx, q in enumerate(questions):
        if idx < correct_target:
            ans = SubmissionAnswer(
                submission_id=sub.id,
                question_id=q.id,
                chosen_index=q.correct_index,
                answer_text=q.correct_text,
                is_correct=True,
            )
        else:
            ans = SubmissionAnswer(
                submission_id=sub.id,
                question_id=q.id,
                chosen_index=_wrong_index(q.correct_index, q.options),
                answer_text=None,
                is_correct=False,
            )
        db.add(ans)

    db.commit()
    print(f"    restored — {student.display_name} -> '{assignment.title}' ({correct_target}/{total} = {target_score}%)")
    return True


def ensure_class_membership(db, student: User, assignment: HomeworkAssignment):
    exists = (
        db.query(AssignmentStudent)
        .filter(
            AssignmentStudent.assignment_id == assignment.id,
            AssignmentStudent.student_id == student.id,
        )
        .first()
    )
    if not exists:
        db.add(AssignmentStudent(assignment_id=assignment.id, student_id=student.id))
        db.commit()


def main():
    # ── Safety guards ────────────────────────────────────────────────────────
    # This script fabricates Submission rows with hardcoded scores for 3 named
    # students against EVERY active PM 91 assignment. It was a one-time recovery
    # tool after a wipe — but leaving it in the deploy chain created phantom
    # submissions on every new homework the teacher uploaded. Two guards now:
    #
    #   1. ALLOW_PM91_RESTORE=1   — must be explicitly set, or the script exits.
    #   2. PM91_RESTORE_ASSIGNMENT_IDS=12,34,56  — comma-separated whitelist of
    #      assignment IDs this run is allowed to touch. If unset, the script
    #      will refuse to operate on ALL PM 91 assignments (the bug that
    #      created the phantom listening submissions).
    if os.environ.get("ALLOW_PM91_RESTORE") != "1":
        print("Refusing to run: ALLOW_PM91_RESTORE is not set to 1.")
        print("This script is a one-time recovery tool, not for routine deploys.")
        return

    raw_ids = os.environ.get("PM91_RESTORE_ASSIGNMENT_IDS", "").strip()
    if not raw_ids:
        print("Refusing to run: PM91_RESTORE_ASSIGNMENT_IDS is empty.")
        print("Set it to a comma-separated list of assignment IDs to restore, e.g. '12,34,56'.")
        return
    try:
        whitelist = {int(s.strip()) for s in raw_ids.split(",") if s.strip()}
    except ValueError:
        print(f"Invalid PM91_RESTORE_ASSIGNMENT_IDS: {raw_ids!r}")
        return
    if not whitelist:
        print("Refusing to run: PM91_RESTORE_ASSIGNMENT_IDS parsed to an empty set.")
        return

    db = SessionLocal()
    try:
        print("Finding target students...")
        students = find_students(db)
        if not students:
            print("No target students found. Nothing to do.")
            return

        print(f"\nFinding PM 91 assignments in whitelist {sorted(whitelist)}...")
        all_assignments = class_assignments(db)
        assignments = [a for a in all_assignments if a.id in whitelist]
        skipped = [a for a in all_assignments if a.id not in whitelist]
        if not assignments:
            print("No whitelisted PM 91 assignments found. Nothing to do.")
            return
        for a in assignments:
            print(f"  Assignment {a.id}: {a.title}")
        if skipped:
            print(f"\nSkipping {len(skipped)} PM 91 assignment(s) not in the whitelist:")
            for a in skipped:
                print(f"  - {a.id}: {a.title}")

        print(f"\nRestoring submissions ({len(students)} students × {len(assignments)} assignments):")
        created = 0
        for s, target_score in students:
            for a in assignments:
                ensure_class_membership(db, s, a)
                if restore_for(db, s, a, target_score):
                    created += 1

        print(f"\nDone. {created} submission(s) restored.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
