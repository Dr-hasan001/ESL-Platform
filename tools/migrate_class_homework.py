"""
migrate_class_homework.py

Runs on every deploy. Two passes:

1. Backfill `class_name` on existing HomeworkAssignment rows by looking at
   the most common class of currently-assigned students.

2. Sync membership: for every active class-scoped assignment, ensure every
   active student in that class has an AssignmentStudent row.

Safe to re-run — only adds the column when missing, only fills nulls,
only adds missing AssignmentStudent rows.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from collections import Counter

from sqlalchemy import text

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.user import User
from app.models.homework import HomeworkAssignment, AssignmentStudent

Base.metadata.create_all(bind=engine)


def ensure_class_name_column():
    """Add homework_assignments.class_name column if it doesn't exist (Postgres + SQLite)."""
    with engine.connect() as conn:
        dialect = engine.dialect.name
        if dialect == "postgresql":
            conn.execute(text("ALTER TABLE homework_assignments ADD COLUMN IF NOT EXISTS class_name VARCHAR(120);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_homework_assignments_class_name ON homework_assignments(class_name);"))
            conn.commit()
        elif dialect == "sqlite":
            res = conn.execute(text("PRAGMA table_info(homework_assignments);")).fetchall()
            cols = [r[1] for r in res]
            if "class_name" not in cols:
                conn.execute(text("ALTER TABLE homework_assignments ADD COLUMN class_name VARCHAR(120);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_homework_assignments_class_name ON homework_assignments(class_name);"))
                conn.commit()


def backfill_class_name(db) -> int:
    """For each assignment without class_name, set it to the most common class of its students."""
    rows = db.query(HomeworkAssignment).filter(HomeworkAssignment.class_name.is_(None)).all()
    filled = 0
    for hw in rows:
        student_ids = [a.student_id for a in hw.assigned_students]
        if not student_ids:
            continue
        classes = Counter(
            u.class_name for u in db.query(User).filter(
                User.id.in_(student_ids),
                User.role == "student",
                User.class_name.isnot(None),
            ).all()
        )
        if not classes:
            continue
        most_common, _ = classes.most_common(1)[0]
        hw.class_name = most_common
        filled += 1
        print(f"  Backfilled assignment {hw.id} '{hw.title}' -> class '{most_common}'")
    if filled:
        db.commit()
    return filled


def sync_membership(db) -> int:
    """Ensure every active student in a class is assigned to every class assignment."""
    added = 0
    assignments = db.query(HomeworkAssignment).filter(
        HomeworkAssignment.is_active == True,
        HomeworkAssignment.class_name.isnot(None),
    ).all()
    for hw in assignments:
        class_students = db.query(User).filter(
            User.role == "student",
            User.is_active == True,
            User.class_name == hw.class_name,
        ).all()
        for s in class_students:
            exists = db.query(AssignmentStudent).filter(
                AssignmentStudent.assignment_id == hw.id,
                AssignmentStudent.student_id == s.id,
            ).first()
            if not exists:
                db.add(AssignmentStudent(assignment_id=hw.id, student_id=s.id))
                added += 1
                print(f"  Assigned student {s.id} ({s.username}) -> assignment {hw.id} '{hw.title}'")
    if added:
        db.commit()
    return added


def main():
    ensure_class_name_column()
    db = SessionLocal()
    try:
        filled = backfill_class_name(db)
        added = sync_membership(db)
        print(f"\nMigration complete: {filled} assignment class_name(s) filled, {added} membership row(s) added.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
