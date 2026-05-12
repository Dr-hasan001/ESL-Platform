from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.book import Unit, Word, UnitPDFCache
from app.models.user import User
from app.pdf_generator import PDF_GENERATORS
from app.routers.deps import current_user

router = APIRouter()


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
