from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.homework import HomeworkAssignment, HomeworkQuestion
from app.models.submission import Submission, SubmissionAnswer
from app.models.user import User
from app.routers.deps import current_user
from app.services import media_gate_service as gate

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


class AnswerItem(BaseModel):
    question_id: int
    chosen_index: int | None = None
    answer_text: str | None = None


class SubmitBody(BaseModel):
    assignment_id: int
    answers: list[AnswerItem] = []
    written_response: str | None = None   # writing HW only
    word_count: int | None = None


@router.post("")
async def submit_homework(body: SubmitBody, db: Session = Depends(get_db), user: User = Depends(current_user)):
    hw = db.query(HomeworkAssignment).filter(HomeworkAssignment.id == body.assignment_id).first()
    if not hw:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Gate guard for media types
    if hw.type in ("listening", "general_topic"):
        status_info = gate.gate_status(db, user.id, body.assignment_id)
        if not status_info["gate_open"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You must listen/watch {status_info['plays_required']} times before submitting.",
            )

    # Upsert submission
    submission = db.query(Submission).filter(
        Submission.assignment_id == body.assignment_id,
        Submission.student_id == user.id,
    ).first()
    if not submission:
        submission = Submission(assignment_id=body.assignment_id, student_id=user.id)
        db.add(submission)
        db.flush()

    # Writing HW: save response
    if hw.type == "writing":
        submission.written_response = body.written_response
        submission.word_count = body.word_count
        submission.is_complete = True
        db.commit()
        return {"ok": True, "type": "writing", "status": "pending_review"}

    # Auto-graded types
    questions = {q.id: q for q in db.query(HomeworkQuestion).filter(HomeworkQuestion.assignment_id == hw.id).all()}

    # Clear old answers
    db.query(SubmissionAnswer).filter(SubmissionAnswer.submission_id == submission.id).delete()

    correct = 0
    for ans in body.answers:
        q = questions.get(ans.question_id)
        if not q:
            continue
        is_correct = None
        if q.question_type == "multiple_choice" and ans.chosen_index is not None:
            is_correct = ans.chosen_index == q.correct_index
            if is_correct:
                correct += 1
        db.add(SubmissionAnswer(
            submission_id=submission.id,
            question_id=ans.question_id,
            chosen_index=ans.chosen_index,
            answer_text=ans.answer_text,
            is_correct=is_correct,
        ))

    total = len(questions)
    submission.total_questions = total
    submission.correct_count = correct
    submission.score = round((correct / total * 100), 2) if total else None
    submission.is_complete = True
    db.commit()

    return {"ok": True, "score": float(submission.score or 0), "correct": correct, "total": total}


@router.get("/{assignment_id}")
async def get_my_submission(assignment_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    sub = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.student_id == user.id,
    ).first()
    if not sub:
        return None
    return {
        "id": sub.id,
        "is_complete": sub.is_complete,
        "score": float(sub.score) if sub.score is not None else None,
        "teacher_score": float(sub.teacher_score) if sub.teacher_score is not None else None,
        "teacher_feedback": sub.teacher_feedback,
        "written_response": sub.written_response,
        "word_count": sub.word_count,
    }
