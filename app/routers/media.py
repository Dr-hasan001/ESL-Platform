from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.routers.deps import current_user
from app.services import media_gate_service as gate

router = APIRouter(prefix="/api/media", tags=["media"])


class PlayCompleteBody(BaseModel):
    play_event_id: int
    duration_listened: int  # seconds


@router.get("/{assignment_id}/gate-status")
async def get_gate_status(assignment_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    return gate.gate_status(db, user.id, assignment_id)


@router.post("/{assignment_id}/play-start")
async def play_start(assignment_id: int, media_type: str = "audio", db: Session = Depends(get_db), user: User = Depends(current_user)):
    event = gate.start_play(db, user.id, assignment_id, media_type)
    return {"play_event_id": event.id, "play_number": event.play_number}


@router.post("/{assignment_id}/play-complete")
async def play_complete(assignment_id: int, body: PlayCompleteBody, db: Session = Depends(get_db), user: User = Depends(current_user)):
    try:
        status_info = gate.complete_play(db, body.play_event_id, user.id, body.duration_listened, assignment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return status_info
