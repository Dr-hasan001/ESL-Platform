import csv
import io
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
import boto3
from botocore.config import Config

from app.config import settings
from app.database import get_db
from app.models.homework import (
    HomeworkAssignment, AssignmentStudent,
    HWListening, HWReading, HWGrammar, HWWriting, HWGeneralTopic, HomeworkQuestion,
)
from app.models.submission import Submission, SubmissionAnswer
from app.models.user import User
from app.pdf_generator import generate_answer_key_pdf, generate_results_pdf
from app.routers.deps import current_teacher
from app.services.auth_service import hash_password

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _random_password(length: int = 8) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


# ── HTML pages ────────────────────────────────────────────────────────────────

@router.get("/teacher")
async def teacher_dashboard(request: Request, db: Session = Depends(get_db), user: User = Depends(current_teacher)):
    students = db.query(User).filter(User.role == "student", User.is_active == True).order_by(User.display_name).all()
    active_assignments = (
        db.query(HomeworkAssignment)
        .filter(HomeworkAssignment.teacher_id == user.id, HomeworkAssignment.is_active == True)
        .order_by(HomeworkAssignment.created_at.desc())
        .limit(20)
        .all()
    )
    inactive_assignments = (
        db.query(HomeworkAssignment)
        .filter(HomeworkAssignment.teacher_id == user.id, HomeworkAssignment.is_active == False)
        .order_by(HomeworkAssignment.created_at.desc())
        .limit(20)
        .all()
    )
    assignments = active_assignments + inactive_assignments

    # Compute submission status per assignment in two bulk queries
    hw_ids = [a.id for a in assignments]
    assigned_counts = {}
    submitted_counts = {}
    if hw_ids:
        assigned_counts = dict(
            db.query(AssignmentStudent.assignment_id, func.count(AssignmentStudent.student_id))
            .filter(AssignmentStudent.assignment_id.in_(hw_ids))
            .group_by(AssignmentStudent.assignment_id)
            .all()
        )
        submitted_counts = dict(
            db.query(Submission.assignment_id, func.count(Submission.id))
            .filter(Submission.assignment_id.in_(hw_ids), Submission.is_complete == True)
            .group_by(Submission.assignment_id)
            .all()
        )

    hw_status = {
        hw.id: {
            "assigned": assigned_counts.get(hw.id, 0),
            "submitted": submitted_counts.get(hw.id, 0),
        }
        for hw in assignments
    }

    # Build per-assignment student schedule
    schedule = []
    if hw_ids:
        all_assigned = (
            db.query(AssignmentStudent, User)
            .join(User, User.id == AssignmentStudent.student_id)
            .filter(AssignmentStudent.assignment_id.in_(hw_ids))
            .all()
        )
        all_subs = (
            db.query(Submission)
            .filter(Submission.assignment_id.in_(hw_ids))
            .all()
        )
        sub_map = {(s.assignment_id, s.student_id): s for s in all_subs}

        assigned_by_hw: dict[int, list] = {hw.id: [] for hw in assignments}
        for row, student in all_assigned:
            sub = sub_map.get((row.assignment_id, student.id))
            if sub and sub.is_complete:
                status = "done"
            elif sub:
                status = "started"
            else:
                status = "not_started"
            assigned_by_hw[row.assignment_id].append({"student": student, "status": status})

        # Schedule grid is only useful for active assignments
        for hw in active_assignments:
            schedule.append({"hw": hw, "rows": assigned_by_hw.get(hw.id, [])})

    return templates.TemplateResponse("teacher/dashboard.html", {
        "request": request,
        "user": user,
        "students": students,
        "active_assignments": active_assignments,
        "inactive_assignments": inactive_assignments,
        "hw_status": hw_status,
        "schedule": schedule,
    })


@router.get("/teacher/assign")
async def assign_page(request: Request, db: Session = Depends(get_db), user: User = Depends(current_teacher)):
    from app.models.topic import Topic
    topics = db.query(Topic).order_by(Topic.cefr_level, Topic.sort_order).all()
    # Distinct class names (non-null) ordered alphabetically
    class_names = [
        row[0] for row in
        db.query(User.class_name).filter(
            User.role == "student", User.is_active == True, User.class_name != None
        ).distinct().order_by(User.class_name).all()
    ]
    return templates.TemplateResponse("teacher/assign.html", {
        "request": request, "user": user, "topics": topics, "class_names": class_names,
    })


@router.get("/teacher/students")
async def students_page(request: Request, db: Session = Depends(get_db), user: User = Depends(current_teacher)):
    students = (
        db.query(User)
        .filter(User.role == "student")
        .order_by(User.class_name, User.display_name)
        .all()
    )
    seen = {}
    for s in students:
        key = s.class_name or "No Class"
        seen.setdefault(key, []).append(s)
    student_groups = [{"name": k, "students": v} for k, v in seen.items()]
    return templates.TemplateResponse("teacher/students.html", {
        "request": request, "user": user, "students": students, "student_groups": student_groups,
    })


@router.get("/teacher/submissions/{assignment_id}")
async def view_submissions(assignment_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(current_teacher)):
    hw = db.query(HomeworkAssignment).filter(HomeworkAssignment.id == assignment_id).first()
    subs = (
        db.query(Submission)
        .filter(Submission.assignment_id == assignment_id)
        .join(User, Submission.student_id == User.id)
        .order_by(User.display_name)
        .all()
    )
    sub_map = {s.student_id: s for s in subs}

    # All assigned students merged with their submission (or None)
    assigned_students = (
        db.query(User)
        .join(AssignmentStudent, AssignmentStudent.student_id == User.id)
        .filter(AssignmentStudent.assignment_id == assignment_id)
        .order_by(User.display_name)
        .all()
    )
    student_rows = [
        {"student": s, "submission": sub_map.get(s.id)}
        for s in assigned_students
    ]

    return templates.TemplateResponse("teacher/submissions.html", {
        "request": request, "user": user, "hw": hw,
        "submissions": subs, "student_rows": student_rows,
    })


# ── API ───────────────────────────────────────────────────────────────────────

class CreateAssignmentBody(BaseModel):
    type: str
    title: str
    instructions: str | None = None
    due_date: str | None = None
    class_name: str | None = None   # assign to all active students in this class
    questions: list[dict] = []
    # type-specific fields
    audio_url: str | None = None
    play_gate: int = 3
    transcript: str | None = None
    passage_text: str | None = None
    exercise_type: str | None = None
    grammar_point: str | None = None
    model_text: str | None = None
    useful_language: list[str] = []
    prompt: str | None = None
    text_type: str | None = None
    min_words: int = 80
    max_words: int = 150
    topic_id: int | None = None


@router.post("/api/admin/assignments")
async def create_assignment(body: CreateAssignmentBody, db: Session = Depends(get_db), user: User = Depends(current_teacher)):
    from datetime import date
    due = date.fromisoformat(body.due_date) if body.due_date else None

    hw = HomeworkAssignment(
        teacher_id=user.id,
        type=body.type,
        title=body.title,
        instructions=body.instructions,
        due_date=due,
        class_name=body.class_name,
    )
    db.add(hw)
    db.flush()

    # Type-specific detail
    if body.type == "listening":
        db.add(HWListening(assignment_id=hw.id, audio_url=body.audio_url or "", play_gate=body.play_gate, transcript=body.transcript))
    elif body.type == "reading":
        db.add(HWReading(assignment_id=hw.id, passage_text=body.passage_text or ""))
    elif body.type == "grammar":
        db.add(HWGrammar(assignment_id=hw.id, exercise_type=body.exercise_type, grammar_point=body.grammar_point))
    elif body.type == "writing":
        db.add(HWWriting(assignment_id=hw.id, model_text=body.model_text, useful_language=body.useful_language,
                          prompt=body.prompt or "", text_type=body.text_type, min_words=body.min_words, max_words=body.max_words))
    elif body.type == "general_topic":
        db.add(HWGeneralTopic(assignment_id=hw.id, topic_id=body.topic_id, play_gate=body.play_gate))

    # Questions
    for i, q in enumerate(body.questions):
        db.add(HomeworkQuestion(
            assignment_id=hw.id,
            position=i + 1,
            question_text=q.get("question_text", ""),
            question_type=q.get("question_type", "multiple_choice"),
            options=q.get("options"),
            correct_index=q.get("correct_index"),
            correct_text=q.get("correct_text"),
        ))

    # Assign to all active students in the selected class
    if body.class_name:
        class_students = db.query(User).filter(
            User.role == "student",
            User.class_name == body.class_name,
            User.is_active == True,
        ).all()
        for s in class_students:
            db.add(AssignmentStudent(assignment_id=hw.id, student_id=s.id))

    db.commit()
    return {"id": hw.id, "title": hw.title}


@router.post("/api/admin/assignments/{assignment_id}/questions")
async def add_questions_to_assignment(assignment_id: int, data: dict, db: Session = Depends(get_db), user: User = Depends(current_teacher)):
    hw = db.query(HomeworkAssignment).filter(HomeworkAssignment.id == assignment_id, HomeworkAssignment.teacher_id == user.id).first()
    if not hw:
        raise HTTPException(status_code=404, detail="Assignment not found")
    questions = data.get("questions", [])
    db.query(HomeworkQuestion).filter(HomeworkQuestion.assignment_id == assignment_id).delete()
    for i, q in enumerate(questions):
        db.add(HomeworkQuestion(
            assignment_id=assignment_id,
            position=i + 1,
            question_text=q.get("question_text", ""),
            question_type=q.get("question_type", "multiple_choice"),
            options=q.get("options"),
            correct_index=q.get("correct_index"),
            correct_text=q.get("correct_text"),
        ))
    db.commit()
    return {"ok": True, "count": len(questions)}


@router.post("/api/admin/assignments/{assignment_id}/assign")
async def assign_students(assignment_id: int, data: dict, db: Session = Depends(get_db), user: User = Depends(current_teacher)):
    student_ids = data.get("student_ids", [])
    for sid in student_ids:
        exists = db.query(AssignmentStudent).filter(
            AssignmentStudent.assignment_id == assignment_id,
            AssignmentStudent.student_id == sid,
        ).first()
        if not exists:
            db.add(AssignmentStudent(assignment_id=assignment_id, student_id=sid))
    db.commit()
    return {"ok": True}


@router.patch("/api/admin/submissions/{submission_id}/feedback")
async def add_feedback(submission_id: int, data: dict, db: Session = Depends(get_db), user: User = Depends(current_teacher)):
    sub = db.query(Submission).filter(Submission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    sub.teacher_feedback = data.get("feedback")
    sub.teacher_score = data.get("score")
    db.commit()
    return {"ok": True}


# ── Class-based homework sync ─────────────────────────────────────────────────

def _assign_class_homework_to_student(db: Session, student: User) -> int:
    """Assign every active class-scoped homework matching the student's class.
    Returns the number of new assignment rows created."""
    if not student.class_name:
        return 0
    class_assignments = db.query(HomeworkAssignment).filter(
        HomeworkAssignment.is_active == True,
        HomeworkAssignment.class_name == student.class_name,
    ).all()
    new_count = 0
    for hw in class_assignments:
        exists = db.query(AssignmentStudent).filter(
            AssignmentStudent.assignment_id == hw.id,
            AssignmentStudent.student_id == student.id,
        ).first()
        if not exists:
            db.add(AssignmentStudent(assignment_id=hw.id, student_id=student.id))
            new_count += 1
    if new_count:
        db.commit()
    return new_count


def _sync_class_homework_membership(db: Session) -> dict:
    """For every active class-scoped assignment, ensure every active student
    in that class is assigned. Idempotent. Returns counts per assignment."""
    summary = {}
    assignments = db.query(HomeworkAssignment).filter(
        HomeworkAssignment.is_active == True,
        HomeworkAssignment.class_name.isnot(None),
    ).all()
    for hw in assignments:
        students = db.query(User).filter(
            User.role == "student",
            User.is_active == True,
            User.class_name == hw.class_name,
        ).all()
        new_count = 0
        for s in students:
            exists = db.query(AssignmentStudent).filter(
                AssignmentStudent.assignment_id == hw.id,
                AssignmentStudent.student_id == s.id,
            ).first()
            if not exists:
                db.add(AssignmentStudent(assignment_id=hw.id, student_id=s.id))
                new_count += 1
        summary[f"{hw.id}:{hw.title}"] = {"class": hw.class_name, "added": new_count}
    db.commit()
    return summary


@router.post("/api/admin/sync-class-homework")
async def sync_class_homework(db: Session = Depends(get_db), user: User = Depends(current_teacher)):
    """Manually trigger a class-homework sync."""
    return {"ok": True, "summary": _sync_class_homework_membership(db)}


# ── Student management ────────────────────────────────────────────────────────

class CreateStudentBody(BaseModel):
    username: str
    display_name: str | None = None
    cefr_level: str | None = None
    class_name: str | None = None
    password: str | None = None


@router.get("/api/admin/students")
async def list_students(db: Session = Depends(get_db), user: User = Depends(current_teacher)):
    students = (
        db.query(User)
        .filter(User.role == "student")
        .order_by(User.cefr_level, User.display_name)
        .all()
    )
    return [
        {
            "id": s.id,
            "username": s.username,
            "display_name": s.display_name,
            "cefr_level": s.cefr_level,
            "class_name": s.class_name,
            "plain_password": s.plain_password,
            "is_active": s.is_active,
        }
        for s in students
    ]


@router.post("/api/admin/students")
async def create_student(body: CreateStudentBody, db: Session = Depends(get_db), user: User = Depends(current_teacher)):
    existing = db.query(User).filter(User.username == body.username).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Username '{body.username}' is already taken.")

    plain = body.password or _random_password()
    student = User(
        username=body.username,
        display_name=body.display_name or body.username,
        cefr_level=body.cefr_level,
        class_name=body.class_name,
        password_hash=hash_password(plain),
        plain_password=plain,
        role="student",
        is_active=True,
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    # Auto-assign every active class-scoped assignment for this student's class.
    auto_count = _assign_class_homework_to_student(db, student)

    return {
        "id": student.id,
        "username": student.username,
        "display_name": student.display_name,
        "cefr_level": student.cefr_level,
        "class_name": student.class_name,
        "password": plain,
        "is_active": student.is_active,
        "auto_assigned_count": auto_count,
    }


@router.post("/api/admin/students/{student_id}/reset-password")
async def reset_password(student_id: int, data: dict = {}, db: Session = Depends(get_db), user: User = Depends(current_teacher)):
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    plain = data.get("password") or _random_password()
    student.password_hash = hash_password(plain)
    student.plain_password = plain
    db.commit()
    return {"password": plain}


@router.patch("/api/admin/students/{student_id}/toggle-active")
async def toggle_active(student_id: int, db: Session = Depends(get_db), user: User = Depends(current_teacher)):
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student.is_active = not student.is_active
    db.commit()
    return {"is_active": student.is_active}


# ── AI question generation ────────────────────────────────────────────────────

class GenerateQuestionsBody(BaseModel):
    content: str
    content_type: str = "reading"
    count: int = 10


@router.post("/api/admin/generate-questions")
async def generate_questions_endpoint(body: GenerateQuestionsBody, user: User = Depends(current_teacher)):
    if not settings.anthropic_api_key:
        raise HTTPException(status_code=501, detail="ANTHROPIC_API_KEY is not configured.")
    if not 1 <= body.count <= 30:
        raise HTTPException(status_code=400, detail="count must be between 1 and 30.")
    if not body.content.strip():
        raise HTTPException(status_code=400, detail="content cannot be empty.")

    from app.services.ai_service import generate_questions
    try:
        questions = generate_questions(body.content, body.content_type, body.count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"questions": questions}


# ── CSV question parsing ──────────────────────────────────────────────────────

@router.post("/api/admin/parse-questions-csv")
async def parse_questions_csv(file: UploadFile = File(...), user: User = Depends(current_teacher)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a .csv")

    contents = await file.read()
    text = contents.decode("utf-8-sig")  # handles BOM from Excel-saved CSVs
    reader = csv.DictReader(io.StringIO(text))

    required = {"question", "option_a", "option_b", "option_c", "option_d", "correct"}
    if not required.issubset({f.lower().strip() for f in (reader.fieldnames or [])}):
        raise HTTPException(
            status_code=400,
            detail=f"CSV must have columns: {', '.join(sorted(required))}",
        )

    letter_to_index = {"a": 0, "b": 1, "c": 2, "d": 3}
    questions = []
    for i, row in enumerate(reader, start=2):
        correct_letter = row.get("correct", "").strip().lower()
        if correct_letter not in letter_to_index:
            raise HTTPException(status_code=400, detail=f"Row {i}: 'correct' must be A, B, C, or D.")
        questions.append({
            "question_text": row["question"].strip(),
            "options": [
                row["option_a"].strip(),
                row["option_b"].strip(),
                row["option_c"].strip(),
                row["option_d"].strip(),
            ],
            "correct_index": letter_to_index[correct_letter],
        })

    return {"questions": questions}


# ── Media upload ──────────────────────────────────────────────────────────────

def _save_audio_locally(file: UploadFile) -> str:
    """Stream the uploaded file to app/static/audio/. Returns the URL path.

    Used as a fallback when R2 isn't configured, and as the default in dev.
    Note: on Render's free tier the filesystem is ephemeral, so this will not
    persist across deploys — R2 is still recommended for production.
    """
    import os, re, uuid

    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", file.filename or "audio")
    # Add a short uuid prefix to avoid name collisions
    final_name = f"{uuid.uuid4().hex[:8]}_{safe_name}"
    out_dir = os.path.join("app", "static", "audio")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, final_name)

    with open(out_path, "wb") as out_f:
        while True:
            chunk = file.file.read(1024 * 1024)  # 1 MB chunks
            if not chunk:
                break
            out_f.write(chunk)

    return f"/static/audio/{final_name}"


@router.post("/api/admin/upload-audio")
async def upload_audio(file: UploadFile = File(...), user: User = Depends(current_teacher)):
    """Upload an audio/video file. Uses Cloudflare R2 if configured, otherwise
    falls back to local static storage."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file received.")

    # Try R2 if configured
    if settings.r2_access_key and settings.r2_bucket_name and settings.r2_public_url:
        try:
            s3 = boto3.client(
                "s3",
                endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=settings.r2_access_key,
                aws_secret_access_key=settings.r2_secret_key,
                config=Config(signature_version="s3v4"),
                region_name="auto",
            )
            key = f"media/{file.filename}"
            s3.upload_fileobj(
                file.file, settings.r2_bucket_name, key,
                ExtraArgs={"ContentType": file.content_type or "application/octet-stream"},
            )
            url = f"{settings.r2_public_url}/{key}"
            return {"url": url, "filename": file.filename, "storage": "r2"}
        except Exception as e:
            # R2 was configured but failed (bad creds, missing bucket, network, etc.).
            # Fall back to local storage so the teacher isn't blocked.
            print(f"[upload-audio] R2 upload failed, falling back to local: {e}")
            try:
                file.file.seek(0)
            except Exception:
                pass

    # Local fallback (dev or R2 misconfigured)
    try:
        url = _save_audio_locally(file)
        return {"url": url, "filename": file.filename, "storage": "local"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio upload failed: {e}")


# ── Assignment lifecycle: deactivate / reactivate ─────────────────────────────

def _safe_filename(name: str) -> str:
    cleaned = "".join(c if c.isalnum() or c in " -_" else "_" for c in (name or ""))
    return cleaned.strip().replace(" ", "_") or "assignment"


@router.patch("/api/admin/assignments/{assignment_id}/toggle-active")
async def toggle_assignment_active(
    assignment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_teacher),
):
    """Flip is_active. When False the assignment vanishes from every student's
    dashboard (filtered out in /homework routes) but stays visible to the
    teacher in an 'Inactive' section. All existing submissions and answers
    remain intact."""
    hw = db.query(HomeworkAssignment).filter(
        HomeworkAssignment.id == assignment_id,
        HomeworkAssignment.teacher_id == user.id,
    ).first()
    if not hw:
        raise HTTPException(status_code=404, detail="Assignment not found")
    hw.is_active = not hw.is_active
    db.commit()
    return {"id": hw.id, "is_active": hw.is_active}


# ── Results: CSV + PDF download ───────────────────────────────────────────────

def _student_rows_for_assignment(db: Session, assignment_id: int):
    """All assigned students paired with their submission (or None)."""
    students = (
        db.query(User)
        .join(AssignmentStudent, AssignmentStudent.student_id == User.id)
        .filter(AssignmentStudent.assignment_id == assignment_id)
        .order_by(User.display_name)
        .all()
    )
    subs = (
        db.query(Submission)
        .filter(Submission.assignment_id == assignment_id)
        .all()
    )
    sub_map = {s.student_id: s for s in subs}
    return [{"student": s, "submission": sub_map.get(s.id)} for s in students]


@router.get("/api/admin/assignments/{assignment_id}/results.csv")
async def download_results_csv(
    assignment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_teacher),
):
    hw = db.query(HomeworkAssignment).filter(
        HomeworkAssignment.id == assignment_id,
        HomeworkAssignment.teacher_id == user.id,
    ).first()
    if not hw:
        raise HTTPException(status_code=404, detail="Assignment not found")

    rows = _student_rows_for_assignment(db, assignment_id)

    out = io.StringIO()
    # BOM so Excel opens UTF-8 correctly
    out.write("﻿")
    writer = csv.writer(out)
    writer.writerow([
        "Student Name", "Username", "Status", "Score", "Correct",
        "Total Questions", "Submitted At", "Teacher Feedback",
    ])
    for r in rows:
        s = r["student"]
        sub = r["submission"]
        if sub and sub.is_complete:
            status = "Submitted"
        elif sub:
            status = "In progress"
        else:
            status = "Not started"

        if sub:
            if hw.type == "writing":
                score = f"{float(sub.teacher_score):.0f}/100" if sub.teacher_score is not None else ""
            else:
                score = f"{float(sub.score):.0f}%" if sub.score is not None else ""
            correct = sub.correct_count if sub.correct_count is not None else ""
            total = sub.total_questions if sub.total_questions is not None else ""
            submitted_at = sub.submitted_at.strftime("%Y-%m-%d %H:%M") if sub.submitted_at else ""
            feedback = sub.teacher_feedback or ""
        else:
            score = correct = total = submitted_at = feedback = ""

        writer.writerow([
            s.display_name or s.username, s.username, status,
            score, correct, total, submitted_at, feedback,
        ])

    csv_bytes = out.getvalue().encode("utf-8")
    filename = f"{_safe_filename(hw.title)}_results.csv"
    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/api/admin/assignments/{assignment_id}/results.pdf")
async def download_results_pdf(
    assignment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_teacher),
):
    hw = db.query(HomeworkAssignment).filter(
        HomeworkAssignment.id == assignment_id,
        HomeworkAssignment.teacher_id == user.id,
    ).first()
    if not hw:
        raise HTTPException(status_code=404, detail="Assignment not found")

    rows = _student_rows_for_assignment(db, assignment_id)
    pdf_bytes = generate_results_pdf(hw, rows)
    filename = f"{_safe_filename(hw.title)}_results.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── Answer-key PDF (teacher only) ─────────────────────────────────────────────

@router.get("/api/admin/assignments/{assignment_id}/answer-key.pdf")
async def download_answer_key(
    assignment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_teacher),
):
    hw = db.query(HomeworkAssignment).filter(
        HomeworkAssignment.id == assignment_id,
        HomeworkAssignment.teacher_id == user.id,
    ).first()
    if not hw:
        raise HTTPException(status_code=404, detail="Assignment not found")

    questions = (
        db.query(HomeworkQuestion)
        .filter(HomeworkQuestion.assignment_id == assignment_id)
        .order_by(HomeworkQuestion.position)
        .all()
    )
    pdf_bytes = generate_answer_key_pdf(hw, questions)
    filename = f"{_safe_filename(hw.title)}_answer_key.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── Preview a single student's answers ────────────────────────────────────────

@router.get("/teacher/submissions/{assignment_id}/student/{student_id}")
async def view_student_answers(
    assignment_id: int,
    student_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(current_teacher),
):
    hw = db.query(HomeworkAssignment).filter(
        HomeworkAssignment.id == assignment_id,
        HomeworkAssignment.teacher_id == user.id,
    ).first()
    if not hw:
        raise HTTPException(status_code=404, detail="Assignment not found")
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    submission = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.student_id == student_id,
    ).first()

    questions = (
        db.query(HomeworkQuestion)
        .filter(HomeworkQuestion.assignment_id == assignment_id)
        .order_by(HomeworkQuestion.position)
        .all()
    )

    answer_map = {}
    if submission:
        for a in db.query(SubmissionAnswer).filter(
            SubmissionAnswer.submission_id == submission.id
        ).all():
            answer_map[a.question_id] = a

    rows = [{"question": q, "answer": answer_map.get(q.id)} for q in questions]

    return templates.TemplateResponse("teacher/student_answers.html", {
        "request": request, "user": user, "hw": hw,
        "student": student, "submission": submission, "rows": rows,
    })
