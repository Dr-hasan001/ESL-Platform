import csv
import io
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
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
from app.models.submission import Submission
from app.models.user import User
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
    assignments = (
        db.query(HomeworkAssignment)
        .filter(HomeworkAssignment.teacher_id == user.id)
        .order_by(HomeworkAssignment.created_at.desc())
        .limit(20)
        .all()
    )

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

    return templates.TemplateResponse("teacher/dashboard.html", {
        "request": request,
        "user": user,
        "students": students,
        "assignments": assignments,
        "hw_status": hw_status,
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
    return templates.TemplateResponse("teacher/submissions.html", {
        "request": request, "user": user, "hw": hw, "submissions": subs,
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
    return {
        "id": student.id,
        "username": student.username,
        "display_name": student.display_name,
        "cefr_level": student.cefr_level,
        "class_name": student.class_name,
        "password": plain,
        "is_active": student.is_active,
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

@router.post("/api/admin/upload-audio")
async def upload_audio(file: UploadFile = File(...), user: User = Depends(current_teacher)):
    """Upload an audio/video file to Cloudflare R2 and return the public URL."""
    if not settings.r2_access_key:
        raise HTTPException(status_code=501, detail="R2 storage not configured. Set R2_* env vars.")
    s3 = boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key,
        aws_secret_access_key=settings.r2_secret_key,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )
    key = f"media/{file.filename}"
    s3.upload_fileobj(file.file, settings.r2_bucket_name, key, ExtraArgs={"ContentType": file.content_type})
    url = f"{settings.r2_public_url}/{key}"
    return {"url": url, "filename": file.filename}
