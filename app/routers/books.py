from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.book import Book, Unit, Word, UnitProgress
from app.models.user import User
from app.routers.deps import current_user


def _assert_level(book: Book, user: User):
    """Redirect to /books if the student tries to access a wrong-level book."""
    if user.cefr_level and book.cefr_level != user.cefr_level:
        raise HTTPException(status_code=403, detail="This book is not available at your level.")

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# ── HTML pages ───────────────────────────────────────────────────────────────

@router.get("/books")
async def bookshelf_page(request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)):
    books_q = db.query(Book).order_by(Book.book_number)
    if user.cefr_level:
        books_q = books_q.filter(Book.cefr_level == user.cefr_level)
    books = books_q.all()
    return templates.TemplateResponse("student/bookshelf.html", {"request": request, "books": books, "user": user})


@router.get("/books/{book_id}")
async def units_page(book_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")
    _assert_level(book, user)
    units = db.query(Unit).filter(Unit.book_id == book_id).order_by(Unit.unit_number).all()

    # Attach progress per unit
    progress_map = {}
    if units:
        unit_ids = [u.id for u in units]
        rows = db.query(UnitProgress).filter(
            UnitProgress.user_id == user.id,
            UnitProgress.unit_id.in_(unit_ids),
        ).all()
        progress_map = {r.unit_id: r for r in rows}

    return templates.TemplateResponse("student/units.html", {
        "request": request, "book": book, "units": units, "progress_map": progress_map, "user": user,
    })


@router.get("/units/{unit_id}/study")
async def study_page(unit_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found.")
    _assert_level(db.query(Book).filter(Book.id == unit.book_id).first(), user)
    words = db.query(Word).filter(Word.unit_id == unit_id).order_by(Word.position).all()
    progress = db.query(UnitProgress).filter(UnitProgress.user_id == user.id, UnitProgress.unit_id == unit_id).first()
    cards_seen = progress.cards_seen if progress else []
    return templates.TemplateResponse("student/study.html", {
        "request": request, "unit": unit, "words": words, "cards_seen": cards_seen, "user": user,
    })


@router.get("/units/{unit_id}/quiz")
async def quiz_page(unit_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found.")
    _assert_level(db.query(Book).filter(Book.id == unit.book_id).first(), user)
    words = db.query(Word).filter(Word.unit_id == unit_id).order_by(Word.position).all()
    progress = db.query(UnitProgress).filter(UnitProgress.user_id == user.id, UnitProgress.unit_id == unit_id).first()
    quiz_revealed = progress.quiz_revealed if progress else []
    return templates.TemplateResponse("student/quiz.html", {
        "request": request, "unit": unit, "words": words, "quiz_revealed": quiz_revealed, "user": user,
    })


@router.get("/units/{unit_id}/story")
async def story_page(unit_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found.")
    _assert_level(db.query(Book).filter(Book.id == unit.book_id).first(), user)
    words = db.query(Word).filter(Word.unit_id == unit_id).order_by(Word.position).all()
    progress = db.query(UnitProgress).filter(UnitProgress.user_id == user.id, UnitProgress.unit_id == unit_id).first()
    story_score = progress.story_score if progress else None
    return templates.TemplateResponse("student/story.html", {
        "request": request, "unit": unit, "words": words, "story_score": story_score, "user": user,
    })


# ── API ──────────────────────────────────────────────────────────────────────

@router.get("/api/books")
async def api_books(db: Session = Depends(get_db), user: User = Depends(current_user)):
    books_q = db.query(Book).order_by(Book.book_number)
    if user.cefr_level:
        books_q = books_q.filter(Book.cefr_level == user.cefr_level)
    books = books_q.all()
    return [{"id": b.id, "title": b.title, "cefr_level": b.cefr_level, "cover_color": b.cover_color, "unit_count": b.unit_count} for b in books]


@router.get("/api/books/{book_id}/units")
async def api_units(book_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")
    _assert_level(book, user)
    units = db.query(Unit).filter(Unit.book_id == book_id).order_by(Unit.unit_number).all()
    return [{"id": u.id, "unit_number": u.unit_number, "title": u.title} for u in units]


@router.get("/api/units/{unit_id}/words")
async def api_words(unit_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found.")
    _assert_level(db.query(Book).filter(Book.id == unit.book_id).first(), user)
    words = db.query(Word).filter(Word.unit_id == unit_id).order_by(Word.position).all()
    return [
        {"id": w.id, "position": w.position, "word": w.word, "emoji": w.emoji,
         "pos": w.part_of_speech, "def": w.definition, "ex": w.example,
         "ar": w.arabic_translation, "deriv": w.derivatives}
        for w in words
    ]


@router.post("/api/units/{unit_id}/progress")
async def save_progress(unit_id: int, data: dict, db: Session = Depends(get_db), user: User = Depends(current_user)):
    progress = db.query(UnitProgress).filter(UnitProgress.user_id == user.id, UnitProgress.unit_id == unit_id).first()
    if not progress:
        progress = UnitProgress(user_id=user.id, unit_id=unit_id)
        db.add(progress)
    if "cards_seen" in data:
        progress.cards_seen = data["cards_seen"]
    if "quiz_revealed" in data:
        progress.quiz_revealed = data["quiz_revealed"]
    if "story_score" in data:
        progress.story_score = data["story_score"]
    db.commit()
    return {"ok": True}
