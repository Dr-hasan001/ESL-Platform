from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.homework import HomeworkAssignment, AssignmentStudent, HWGeneralTopic
from app.models.submission import Submission
from app.models.user import User
from app.routers.deps import current_user
from app.services import media_gate_service as gate

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

HW_TEMPLATES = {
    "listening": "student/homework/listening.html",
    "reading": "student/homework/reading.html",
    "grammar": "student/homework/grammar.html",
    "writing": "student/homework/writing.html",
    "general_topic": "student/homework/general_topics.html",
}


# ── HTML page ─────────────────────────────────────────────────────────────────

@router.get("/homework/{assignment_id}")
async def homework_page(assignment_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)):
    hw = (
        db.query(HomeworkAssignment)
        .options(
            joinedload(HomeworkAssignment.hw_listening),
            joinedload(HomeworkAssignment.hw_reading),
            joinedload(HomeworkAssignment.hw_grammar),
            joinedload(HomeworkAssignment.hw_writing),
            joinedload(HomeworkAssignment.hw_general_topic).joinedload(HWGeneralTopic.topic),
            joinedload(HomeworkAssignment.questions),
        )
        .filter(HomeworkAssignment.id == assignment_id, HomeworkAssignment.is_active == True)
        .first()
    )

    # Check the student is assigned to this homework
    assigned = db.query(AssignmentStudent).filter(
        AssignmentStudent.assignment_id == assignment_id,
        AssignmentStudent.student_id == user.id,
    ).first()
    if not assigned and user.role != "teacher":
        return templates.TemplateResponse("student/not_assigned.html", {"request": request, "user": user})

    # Existing submission
    submission = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.student_id == user.id,
    ).first()

    # Gate status for media types
    gate_info = None
    if hw and hw.type in ("listening", "general_topic"):
        gate_info = gate.gate_status(db, user.id, assignment_id)

    # Serialize questions to plain dicts so tojson works in templates
    questions_json = [
        {
            "id": q.id,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "options": q.options,
            "correct_index": q.correct_index,
            "correct_text": q.correct_text,
        }
        for q in (hw.questions if hw else [])
    ]

    template_name = HW_TEMPLATES.get(hw.type, "student/homework/reading.html") if hw else "student/homework/reading.html"
    return templates.TemplateResponse(template_name, {
        "request": request, "hw": hw, "user": user,
        "submission": submission, "gate": gate_info,
        "questions_json": questions_json,
    })


# ── API ───────────────────────────────────────────────────────────────────────

@router.get("/api/homework")
async def api_my_homework(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = (
        db.query(AssignmentStudent)
        .filter(AssignmentStudent.student_id == user.id)
        .join(HomeworkAssignment, AssignmentStudent.assignment_id == HomeworkAssignment.id)
        .filter(HomeworkAssignment.is_active == True)
        .all()
    )
    result = []
    for row in rows:
        hw = row.assignment
        sub = db.query(Submission).filter(
            Submission.assignment_id == hw.id,
            Submission.student_id == user.id,
        ).first()
        result.append({
            "id": hw.id,
            "type": hw.type,
            "title": hw.title,
            "due_date": hw.due_date.isoformat() if hw.due_date else None,
            "status": "complete" if (sub and sub.is_complete) else ("in_progress" if sub else "not_started"),
            "score": float(sub.score) if sub and sub.score is not None else None,
        })
    return result


@router.get("/api/homework/{assignment_id}/gate-status")
async def api_gate_status(assignment_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    return gate.gate_status(db, user.id, assignment_id)
