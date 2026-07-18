"""
Revision-sheet PDF generator: word + picture + English meaning + Arabic.

One row per word (image | word + definition | Arabic translation),
each unit starts on a new page with a header. A4 portrait.

Arabic is shaped with arabic_reshaper + python-bidi and rendered with a
Windows system font that has Arabic glyphs (Tahoma, falling back to Arial).

Usage:
    py tools/generate_revision_pdf.py [--out FILE.pdf] BOOK:UNIT [BOOK:UNIT ...]
    e.g.  py tools/generate_revision_pdf.py --out revision.pdf 2:29 2:30 3:1 3:2 3:3 3:4 3:5
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from io import BytesIO

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.database import SessionLocal
from app.models.book import Book, Unit, Word
from app.pdf_generator import _resolve_image_path, _draw_image_fitted

PAGE_W, PAGE_H = A4
MARGIN_X = 12 * mm
MARGIN_TOP = 14 * mm
MARGIN_BOT = 12 * mm
ROW_H = 34 * mm

INK = HexColor("#1A1209")
ACCENT = HexColor("#8B1F12")
MUTED = HexColor("#7A6E63")
RULE = HexColor("#C9BFB4")

ARABIC_FONT = "ArabicUI"


def _register_arabic_font():
    for path in (r"C:\Windows\Fonts\tahoma.ttf", r"C:\Windows\Fonts\arial.ttf"):
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont(ARABIC_FONT, path))
            return
    raise RuntimeError("No Arabic-capable font found (tahoma.ttf / arial.ttf)")


def shape_ar(text: str) -> str:
    """Reshape + reorder Arabic for correct glyph joining and RTL display."""
    return get_display(arabic_reshaper.reshape(text or ""))


def _draw_unit_header(c: canvas.Canvas, book, unit, continued=False):
    y = PAGE_H - MARGIN_TOP
    c.setStrokeColor(INK)
    c.setLineWidth(0.9)
    c.line(MARGIN_X, y, PAGE_W - MARGIN_X, y)

    label = f"BOOK {book.book_number}  ·  UNIT {unit.unit_number}"
    if continued:
        label += "  (CONTINUED)"
    c.setFont("Times-Bold", 16)
    c.setFillColor(INK)
    c.drawString(MARGIN_X, y - 7 * mm, label)

    c.setFont("Times-Italic", 9.5)
    c.setFillColor(MUTED)
    c.drawRightString(PAGE_W - MARGIN_X, y - 7 * mm,
                      "Revision Sheet — word · picture · meaning (EN / AR)")

    c.setStrokeColor(RULE)
    c.setLineWidth(0.4)
    c.line(MARGIN_X, y - 10 * mm, PAGE_W - MARGIN_X, y - 10 * mm)
    return y - 13 * mm  # top y for first row


def _fit_font_size(c, text, font, max_size, min_size, max_width):
    size = max_size
    while size > min_size and c.stringWidth(text, font, size) > max_width:
        size -= 0.5
    return size


def _draw_word_row(c: canvas.Canvas, w: Word, num: int, top_y: float):
    """One revision row. top_y is the TOP edge; returns nothing."""
    bot_y = top_y - ROW_H

    # Row number — small, muted, far left
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(MUTED)
    c.drawString(MARGIN_X, top_y - 5 * mm, f"{num:02d}")

    # Image — left block
    img_x = MARGIN_X + 7 * mm
    img_w = 36 * mm
    img_path = _resolve_image_path(w.image_url)
    if img_path:
        _draw_image_fitted(c, img_path, img_x, bot_y + 2 * mm, img_w, ROW_H - 4 * mm, padding=1)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.3)
    elif w.emoji:
        c.setFont("Helvetica", 30)
        c.setFillColor(INK)
        c.drawCentredString(img_x + img_w / 2, (top_y + bot_y) / 2 - 4 * mm, w.emoji)

    # Text block — middle
    text_x = img_x + img_w + 6 * mm
    ar_w = 52 * mm                                   # right block reserved for Arabic
    text_w = (PAGE_W - MARGIN_X - ar_w - 4 * mm) - text_x

    word_y = top_y - 7 * mm
    c.setFont("Times-Bold", 15)
    c.setFillColor(INK)
    c.drawString(text_x, word_y, w.word)
    if w.part_of_speech:
        wx = text_x + c.stringWidth(w.word, "Times-Bold", 15) + 2.5 * mm
        c.setFont("Times-Italic", 9)
        c.setFillColor(MUTED)
        c.drawString(wx, word_y, f"({w.part_of_speech})")

    definition = (w.definition or "").strip()
    font_size, leading = 10, 13
    lines = simpleSplit(definition, "Helvetica", font_size, text_w)
    if len(lines) > 4:
        font_size, leading = 9, 11.5
        lines = simpleSplit(definition, "Helvetica", font_size, text_w)
    c.setFont("Helvetica", font_size)
    c.setFillColor(INK)
    dy = word_y - 6.5 * mm
    for line in lines[:5]:
        c.drawString(text_x, dy, line)
        dy -= leading

    # Arabic — right block, right-aligned, vertically centered on the word line
    ar_text = shape_ar(w.arabic_translation or "")
    if ar_text:
        ar_right = PAGE_W - MARGIN_X
        size = _fit_font_size(c, ar_text, ARABIC_FONT, 14, 9, ar_w)
        c.setFont(ARABIC_FONT, size)
        c.setFillColor(ACCENT)
        c.drawRightString(ar_right, word_y, ar_text)

    # Divider under the row
    c.setStrokeColor(RULE)
    c.setLineWidth(0.3)
    c.line(MARGIN_X, bot_y, PAGE_W - MARGIN_X, bot_y)


def generate_revision_pdf(unit_specs: list[tuple[int, int]]) -> bytes:
    """unit_specs: list of (book_number, unit_number), rendered in order."""
    db = SessionLocal()
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle("Vocabulary Revision — " +
               ", ".join(f"B{b}U{u}" for b, u in unit_specs))

    for bn, un in unit_specs:
        book = db.query(Book).filter(Book.book_number == bn).first()
        if not book:
            print(f"  !! book {bn} not found — skipped")
            continue
        unit = db.query(Unit).filter(Unit.book_id == book.id,
                                     Unit.unit_number == un).first()
        if not unit:
            print(f"  !! book {bn} unit {un} not found — skipped")
            continue
        words = db.query(Word).filter(Word.unit_id == unit.id).order_by(Word.position).all()
        if not words:
            print(f"  !! book {bn} unit {un} has no words — skipped")
            continue

        top_y = _draw_unit_header(c, book, unit)
        for i, w in enumerate(words):
            if top_y - ROW_H < MARGIN_BOT:
                c.showPage()
                top_y = _draw_unit_header(c, book, unit, continued=True)
            _draw_word_row(c, w, i + 1, top_y)
            top_y -= ROW_H
        c.showPage()
        print(f"  b{bn} u{un}: {len(words)} words")

    db.close()
    c.save()
    return buf.getvalue()


def main():
    args = sys.argv[1:]
    out_path = "revision.pdf"
    if "--out" in args:
        i = args.index("--out")
        out_path = args[i + 1]
        args = args[:i] + args[i + 2:]
    if not args:
        print(__doc__)
        sys.exit(1)

    specs = []
    for a in args:
        b, u = a.split(":")
        specs.append((int(b), int(u)))

    _register_arabic_font()
    pdf = generate_revision_pdf(specs)
    with open(out_path, "wb") as f:
        f.write(pdf)
    print(f"\nSaved: {out_path}  ({len(pdf) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
