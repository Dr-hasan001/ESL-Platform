from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.homework import HomeworkAssignment, HWListening, HWGeneralTopic
from app.models.media_play import MediaPlayEvent


def get_play_gate(db: Session, assignment_id: int) -> int:
    """Return the required number of completed plays for this assignment."""
    hw = db.query(HWListening).filter(HWListening.assignment_id == assignment_id).first()
    if hw:
        return hw.play_gate
    hw = db.query(HWGeneralTopic).filter(HWGeneralTopic.assignment_id == assignment_id).first()
    if hw:
        return hw.play_gate
    return 3  # safe default


def get_completed_plays(db: Session, user_id: int, assignment_id: int) -> int:
    """Count verified completed plays for this user + assignment."""
    return (
        db.query(MediaPlayEvent)
        .filter(
            MediaPlayEvent.user_id == user_id,
            MediaPlayEvent.assignment_id == assignment_id,
            MediaPlayEvent.completed_at.isnot(None),
        )
        .count()
    )


def gate_status(db: Session, user_id: int, assignment_id: int) -> dict:
    required = get_play_gate(db, assignment_id)
    completed = get_completed_plays(db, user_id, assignment_id)
    return {
        "plays_completed": completed,
        "plays_required": required,
        "gate_open": completed >= required,
    }


def start_play(db: Session, user_id: int, assignment_id: int, media_type: str) -> MediaPlayEvent:
    completed = get_completed_plays(db, user_id, assignment_id)
    event = MediaPlayEvent(
        user_id=user_id,
        assignment_id=assignment_id,
        media_type=media_type,
        play_number=completed + 1,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def complete_play(
    db: Session,
    play_event_id: int,
    user_id: int,
    duration_listened: int,
    assignment_id: int,
) -> dict:
    """
    Validate and mark a play event as complete.
    Returns gate_status dict or raises ValueError.
    """
    event = db.query(MediaPlayEvent).filter(MediaPlayEvent.id == play_event_id).first()
    if not event:
        raise ValueError("Play event not found.")
    if event.user_id != user_id:
        raise ValueError("Not authorised.")
    if event.assignment_id != assignment_id:
        raise ValueError("Assignment mismatch.")
    if event.completed_at is not None:
        raise ValueError("Play already completed.")

    # Must have been started within 8 hours
    started = event.started_at
    if started.tzinfo is None:
        started = started.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) - started > timedelta(hours=8):
        raise ValueError("Play session expired. Please listen again.")

    # Duration plausibility: we accept without media duration check (client sends what it tracked)
    # Minimum 10 seconds to prevent accidental clicks
    if duration_listened < 10:
        raise ValueError("Listening duration too short.")

    event.completed_at = datetime.now(timezone.utc)
    event.duration_listened = duration_listened
    db.commit()

    return gate_status(db, user_id, assignment_id)
