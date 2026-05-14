from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.book import Book, Unit, Word, UnitPDFCache
from app.models.user import User
from app.pdf_generator import PDF_GENERATORS, generate_exam_pdf
from app.routers.deps import current_user, current_teacher

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _get_or_build_pdf(db: Session, unit: Unit, pdf_type: str) -> bytes:
    cached = (
        db.query(UnitPDFCache)
        .filter(UnitPDFCache.unit_id == unit.id, UnitPDFCache.pdf_type == pdf_type)
        .first()
    )
    if cached:
        return cached.pdf_data

    if pdf_type not in PDF_GENERATORS:
        raise HTTPException(status_code=400, detail=f"Unknown pdf_type: {pdf_type}")

    words = (
        db.query(Word)
        .filter(Word.unit_id == unit.id)
        .order_by(Word.position)
        .all()
    )
    if not words:
        raise HTTPException(status_code=404, detail="Unit has no words to render.")

    pdf_bytes = PDF_GENERATORS[pdf_type](unit, words)
    db.add(UnitPDFCache(unit_id=unit.id, pdf_type=pdf_type, pdf_data=pdf_bytes))
    db.commit()
    return pdf_bytes


def _filename(unit: Unit, label: str) -> str:
    return f"unit{unit.unit_number}_{label}.pdf"


def _pdf_response(pdf_bytes: bytes, filename: str) -> Response:
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/units/{unit_id}/download/flashcards.pdf")
async def download_flashcards(unit_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    pdf = _get_or_build_pdf(db, unit, "flashcards")
    return _pdf_response(pdf, _filename(unit, "flashcards"))


@router.get("/units/{unit_id}/download/images.pdf")
async def download_images_only(unit_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    pdf = _get_or_build_pdf(db, unit, "images_only")
    return _pdf_response(pdf, _filename(unit, "image_cards"))


@router.get("/units/{unit_id}/download/definitions/study.pdf")
async def download_definitions_study(unit_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    pdf = _get_or_build_pdf(db, unit, "definitions_study")
    return _pdf_response(pdf, _filename(unit, "definitions_study"))


@router.get("/units/{unit_id}/download/definitions/game.pdf")
async def download_definitions_game(unit_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    pdf = _get_or_build_pdf(db, unit, "definitions_game")
    return _pdf_response(pdf, _filename(unit, "definitions_guess_the_word"))


# ── Weekly Exam (teacher) ─────────────────────────────────────────────────────

@router.get("/teacher/exam/create")
async def exam_create_page(request: Request, db: Session = Depends(get_db), user: User = Depends(current_teacher)):
    """Teacher picks units and question counts to generate an exam PDF."""
    books_with_units = []
    for b in db.query(Book).order_by(Book.book_number).all():
        units = db.query(Unit).filter(Unit.book_id == b.id).order_by(Unit.unit_number).all()
        rows = []
        for u in units:
            wc = db.query(Word).filter(Word.unit_id == u.id).count()
            img_count = db.query(Word).filter(Word.unit_id == u.id, Word.image_url.isnot(None)).count()
            if wc > 0:
                rows.append({"id": u.id, "number": u.unit_number, "title": u.title or f"Unit {u.unit_number}",
                             "word_count": wc, "image_count": img_count})
        if rows:
            books_with_units.append({"book": b, "units": rows})
    return templates.TemplateResponse("teacher/exam_create.html", {
        "request": request, "user": user, "books_with_units": books_with_units,
    })


@router.get("/teacher/exam/download.pdf")
async def exam_download(
    request: Request,
    unit_ids: str,
    num_image: int = 8,
    num_blank: int = 12,
    title: str = "Weekly Vocabulary Exam",
    db: Session = Depends(get_db),
    user: User = Depends(current_teacher),
):
    """Generate the exam PDF on-the-fly. Not cached (combinations vary)."""
    try:
        ids = [int(s) for s in unit_ids.split(",") if s.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid unit_ids")
    if not ids:
        raise HTTPException(status_code=400, detail="Pick at least one unit")
    num_image = max(0, min(num_image, 50))
    num_blank = max(0, min(num_blank, 50))
    if num_image + num_blank == 0:
        raise HTTPException(status_code=400, detail="Pick at least one question for either section")

    units = db.query(Unit).filter(Unit.id.in_(ids)).order_by(Unit.unit_number).all()
    if not units:
        raise HTTPException(status_code=404, detail="No matching units")
    unit_label = "Units " + ", ".join(str(u.unit_number) for u in units)

    words = (
        db.query(Word)
        .filter(Word.unit_id.in_(ids))
        .order_by(Word.unit_id, Word.position)
        .all()
    )
    if not words:
        raise HTTPException(status_code=404, detail="Chosen units have no words")

    pdf = generate_exam_pdf(unit_label, words, num_image, num_blank, exam_title=title)
    safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in title).strip().replace(" ", "_") or "exam"
    return _pdf_response(pdf, f"{safe}.pdf")
