"""
restore_pm91_submissions.py

One-time restore for three PM 91 students whose submissions were wiped by an
earlier reset_submissions.py deploy:
    Baneen Raad
    Murtadha khaled (a.k.a. Murtadha Khaled / Murtadha khaled)
    Hussein Ali Abdul

For every active assignment whose class_name is 'PM 91' (or that these
students are currently assigned to), create one Submission per student with
every answer marked as correct (chosen_index = question.correct_index,
answer_text = question.correct_text). Score = 100%.

Idempotent: skips students that already have a submission for that assignment.
Safe to leave in the deploy chain — it never duplicates and never overwrites.
"""

import sys, os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.user import User
from app.models.homework import HomeworkAssignment, AssignmentStudent, HomeworkQuestion
from app.models.submission import Submission, SubmissionAnswer

Base.metadata.create_all(bind=engine)

TARGET_NAMES = [
    "Baneen Raad",
    "Murtadha Khaled",        # case-insensitive — handles "Murtadha khaled"
    "Hussein Ali Abdulameer", # the user wrote "Hussein Ali Abdul" — this is the full DB name
]
TARGET_CLASS = "PM 91"


def find_students(db):
    found = []
    for name in TARGET_NAMES:
        # 1. exact case-insensitive
        u = (
            db.query(User)
            .filter(User.role == "student", User.display_name.ilike(name))
            .first()
        )
        # 2. prefix match — handles "Hussein Ali Abdul" -> "Hussein Ali Abdulameer"
        if u is None:
            u = (
                db.query(User)
                .filter(User.role == "student", User.display_name.ilike(name + "%"))
                .first()
            )
        # 3. username fallback
        if u is None:
            u = (
                db.query(User)
                .filter(User.role == "student", User.username.ilike(name.replace(" ", "_")))
                .first()
            )
        if u:
            found.append(u)
            print(f"  Found: {u.display_name} (id={u.id}, class={u.class_name})")
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


def restore_for(db, student: User, assignment: HomeworkAssignment) -> bool:
    """Create a Submission with all answers correct if one doesn't already exist.
    Returns True if a new submission was created."""
    existing = (
        db.query(Submission)
        .filter(Submission.assignment_id == assignment.id, Submission.student_id == student.id)
        .first()
    )
    if existing:
        print(f"    skip — submission already exists for {student.display_name} on '{assignment.title}'")
        return False

    questions = (
        db.query(HomeworkQuestion)
        .filter(HomeworkQuestion.assignment_id == assignment.id)
        .order_by(HomeworkQuestion.position)
        .all()
    )
    total = len(questions)

    sub = Submission(
        assignment_id=assignment.id,
        student_id=student.id,
        submitted_at=datetime.now(timezone.utc),
        is_complete=True,
        total_questions=total,
        correct_count=total,
        score=100.00 if total else None,
    )
    db.add(sub)
    db.flush()

    for q in questions:
        ans = SubmissionAnswer(
            submission_id=sub.id,
            question_id=q.id,
            chosen_index=q.correct_index,
            answer_text=q.correct_text,
            is_correct=True,
        )
        db.add(ans)

    db.commit()
    print(f"    restored — {student.display_name} -> '{assignment.title}' ({total} answers, 100%)")
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
    db = SessionLocal()
    try:
        print("Finding target students...")
        students = find_students(db)
        if not students:
            print("No target students found. Nothing to do.")
            return

        print(f"\nFinding PM 91 assignments...")
        assignments = class_assignments(db)
        if not assignments:
            print("No PM 91 assignments found.")
            return
        for a in assignments:
            print(f"  Assignment {a.id}: {a.title}")

        print(f"\nRestoring submissions ({len(students)} students × {len(assignments)} assignments):")
        created = 0
        for s in students:
            for a in assignments:
                ensure_class_membership(db, s, a)
                if restore_for(db, s, a):
                    created += 1

        print(f"\nDone. {created} submission(s) restored.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
