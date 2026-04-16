from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
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

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# ── HTML pages ────────────────────────────────────────────────────────────────

@router.get("/teacher")
async def teacher_dashboard(request: Request, db: Session = Depends(get_db), user: User = Depends(current_teacher)):
    students = db.query(User).filter(User.role == "student", User.is_active == True).order_by(User.display_name).all()
    assignments = db.query(HomeworkAssignment).filter(HomeworkAssignment.teacher_id == user.id).order_by(HomeworkAssignment.created_at.desc()).limit(20).all()
    return templates.TemplateResponse("teacher/dashboard.html", {
        "request": request, "user": user, "students": students, "assignments": assignments,
    })


@router.get("/teacher/assign")
async def assign_page(request: Request, db: Session = Depends(get_db), user: User = Depends(current_teacher)):
    students = db.query(User).filter(User.role == "student", User.is_active == True).order_by(User.display_name).all()
    from app.models.topic import Topic
    topics = db.query(Topic).order_by(Topic.cefr_level, Topic.sort_order).all()
    return templates.TemplateResponse("teacher/assign.html", {
        "request": request, "user": user, "students": students, "topics": topics,
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
    student_ids: list[int] = []
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

    # Assign to students
    for sid in body.student_ids:
        db.add(AssignmentStudent(assignment_id=hw.id, student_id=sid))

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


@router.get("/api/admin/students")
async def list_students(db: Session = Depends(get_db), user: User = Depends(current_teacher)):
    students = db.query(User).filter(User.role == "student", User.is_active == True).order_by(User.display_name).all()
    return [{"id": s.id, "username": s.username, "display_name": s.display_name, "cefr_level": s.cefr_level} for s in students]


@router.get("/api/admin/assignments/{assignment_id}/submissions")
async def get_submissions(assignment_id: int, db: Session = Depends(get_db), user: User = Depends(current_teacher)):
    subs = db.query(Submission).filter(Submission.assignment_id == assignment_id).all()
    return [
        {
            "id": s.id,
            "student_id": s.student_id,
            "is_complete": s.is_complete,
            "score": float(s.score) if s.score is not None else None,
            "teacher_score": float(s.teacher_score) if s.teacher_score is not None else None,
            "teacher_feedback": s.teacher_feedback,
            "written_response": s.written_response,
            "submitted_at": s.submitted_at.isoformat(),
        }
        for s in subs
    ]


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
