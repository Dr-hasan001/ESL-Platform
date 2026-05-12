"""
PDF generators for unit flashcards / definitions / image cards.
A4 portrait, 2 cols x 5 rows = 10 cards per page.
Designed for classroom games — dashed cut lines around each card.
"""

import os
import re
from io import BytesIO

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# Print resolution: ~200 DPI at card size (~95mm wide) = ~750px. Bumping a bit for crisp output.
TARGET_IMG_W = 900
JPEG_QUALITY = 78
_image_reader_cache: dict[str, ImageReader] = {}

PAGE_W, PAGE_H = A4
COLS, ROWS = 2, 5
MARGIN_X = 8 * mm
MARGIN_Y = 10 * mm
CARD_W = (PAGE_W - 2 * MARGIN_X) / COLS
CARD_H = (PAGE_H - 2 * MARGIN_Y) / ROWS
CARDS_PER_PAGE = COLS * ROWS

CARD_BG = HexColor("#FFFFFF")
CARD_BORDER = HexColor("#1A1209")
CUT_COLOR = HexColor("#9A9A9A")


def _card_xy(idx_on_page: int):
    col = idx_on_page % COLS
    row = idx_on_page // COLS
    x = MARGIN_X + col * CARD_W
    y = PAGE_H - MARGIN_Y - (row + 1) * CARD_H
    return x, y


def _draw_cut_border(c: canvas.Canvas, x, y):
    c.saveState()
    c.setStrokeColor(CUT_COLOR)
    c.setLineWidth(0.4)
    c.setDash(2, 2)
    c.rect(x, y, CARD_W, CARD_H, stroke=1, fill=0)
    c.restoreState()


def _draw_centered_text(c: canvas.Canvas, text: str, cx, cy, max_width, font="Helvetica-Bold", size=24, color=black):
    while size > 8:
        if c.stringWidth(text, font, size) <= max_width:
            break
        size -= 1
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawCentredString(cx, cy, text)


def _draw_paragraph(c: canvas.Canvas, text: str, x, y, w, h, align="center", font_size=14, leading=18, color=black, vcenter=True):
    """Draw wrapped, centered text directly on the canvas with true vertical centering."""
    from reportlab.lib.utils import simpleSplit
    inner_w = w - 16
    font = "Helvetica"
    lines = simpleSplit(text, font, font_size, inner_w)
    total_h = max(1, len(lines)) * leading
    cx = x + w / 2
    if vcenter:
        top_y = y + h / 2 + total_h / 2 - (leading - font_size) / 2 - font_size
    else:
        top_y = y + h - leading
    c.setFont(font, font_size)
    c.setFillColor(color)
    for i, line in enumerate(lines):
        c.drawCentredString(cx, top_y - i * leading, line)


def _resolve_image_path(image_url: str | None) -> str | None:
    if not image_url:
        return None
    rel = image_url.lstrip("/")
    if rel.startswith("static/"):
        rel = "app/" + rel
    abs_path = os.path.abspath(rel)
    return abs_path if os.path.exists(abs_path) else None


def _compressed_reader(img_path: str) -> ImageReader | None:
    if img_path in _image_reader_cache:
        return _image_reader_cache[img_path]
    try:
        with Image.open(img_path) as im:
            im = im.convert("RGB")
            if im.width > TARGET_IMG_W:
                ratio = TARGET_IMG_W / im.width
                im = im.resize((TARGET_IMG_W, int(im.height * ratio)), Image.LANCZOS)
            buf = BytesIO()
            im.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
            buf.seek(0)
            reader = ImageReader(buf)
            _image_reader_cache[img_path] = reader
            return reader
    except Exception:
        return None


def _draw_image_fitted(c: canvas.Canvas, img_path: str, x, y, w, h, padding=4):
    reader = _compressed_reader(img_path)
    if reader is None:
        return
    try:
        c.drawImage(
            reader,
            x + padding, y + padding,
            width=w - 2 * padding, height=h - 2 * padding,
            preserveAspectRatio=True, anchor="c", mask="auto",
        )
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Generators
# ─────────────────────────────────────────────────────────────────────────────

def generate_flashcards_pdf(unit, words) -> bytes:
    """Cards: image (top ~70%) + word (bottom ~30%). No defs, no derivatives."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"Unit {unit.unit_number} — Flashcards")

    for i, w in enumerate(words):
        if i > 0 and i % CARDS_PER_PAGE == 0:
            c.showPage()
        x, y = _card_xy(i % CARDS_PER_PAGE)

        _draw_cut_border(c, x, y)

        img_h = CARD_H * 0.70
        text_h = CARD_H * 0.30
        img_path = _resolve_image_path(w.image_url)
        if img_path:
            _draw_image_fitted(c, img_path, x, y + text_h, CARD_W, img_h, padding=6)
        elif w.emoji:
            _draw_centered_text(c, w.emoji, x + CARD_W / 2, y + text_h + img_h / 2 - 14, CARD_W - 12, size=44)

        _draw_centered_text(
            c, w.word,
            x + CARD_W / 2, y + text_h / 2 - 8,
            CARD_W - 12, font="Helvetica-Bold", size=22,
        )

    c.showPage()
    c.save()
    return buf.getvalue()


def generate_images_only_pdf(unit, words) -> bytes:
    """Cards: image only. No words, no numbers."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"Unit {unit.unit_number} — Image Cards")

    for i, w in enumerate(words):
        if i > 0 and i % CARDS_PER_PAGE == 0:
            c.showPage()
        x, y = _card_xy(i % CARDS_PER_PAGE)

        _draw_cut_border(c, x, y)

        img_path = _resolve_image_path(w.image_url)
        if img_path:
            _draw_image_fitted(c, img_path, x, y, CARD_W, CARD_H, padding=8)
        elif w.emoji:
            _draw_centered_text(c, w.emoji, x + CARD_W / 2, y + CARD_H / 2 - 28, CARD_W - 12, size=72)

    c.showPage()
    c.save()
    return buf.getvalue()


def generate_definitions_study_pdf(unit, words) -> bytes:
    """Cards: definition text only — no word, no picture."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"Unit {unit.unit_number} — Definitions (Study)")

    for i, w in enumerate(words):
        if i > 0 and i % CARDS_PER_PAGE == 0:
            c.showPage()
        x, y = _card_xy(i % CARDS_PER_PAGE)

        _draw_cut_border(c, x, y)

        text = _strip_word_from_definition(w.word, w.definition or "")
        _draw_paragraph(
            c, text,
            x, y, CARD_W, CARD_H,
            align="center", font_size=14, leading=19, color=black,
        )

    c.showPage()
    c.save()
    return buf.getvalue()


def generate_definitions_game_pdf(unit, words) -> bytes:
    """Cards: definition centered + word in top-right corner UPSIDE DOWN (rotated 180°)."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"Unit {unit.unit_number} — Definitions (Guess the Word)")

    for i, w in enumerate(words):
        if i > 0 and i % CARDS_PER_PAGE == 0:
            c.showPage()
        x, y = _card_xy(i % CARDS_PER_PAGE)

        _draw_cut_border(c, x, y)

        # Definition centered (leave top-right room for upside-down word)
        text = _strip_word_from_definition(w.word, w.definition or "")
        _draw_paragraph(
            c, text,
            x, y, CARD_W, CARD_H - 12,
            align="center", font_size=13, leading=18, color=black,
        )

        # Upside-down word in top-right corner
        word = w.word
        c.saveState()
        # Rotate 180° around a point inside the card's top-right corner
        corner_x = x + CARD_W - 8
        corner_y = y + CARD_H - 8
        c.translate(corner_x, corner_y)
        c.rotate(180)
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(HexColor("#666666"))
        c.drawString(0, 0, word)
        c.restoreState()

    c.showPage()
    c.save()
    return buf.getvalue()


def _strip_word_from_definition(word: str, definition: str) -> str:
    """Remove the target word (and common inflections) from the definition
    so the sentence still reads cleanly. Handles common 4000 EEW patterns:
        "X means Y."         -> "Y."
        "An X is Y."         -> "Y."
        "To X is to Y."      -> "Y."
        "A X person..."      -> "Person..."
        "...kinds of Xs."    -> "...kinds." (trailing prep cleanup)
    """
    if not word or not definition:
        return definition or ""

    base = word.strip()
    forms = {base, base + "s", base + "es", base + "ed", base + "ing", base + "d"}
    if base.endswith("e"):
        forms.add(base[:-1] + "ing")
        forms.add(base[:-1] + "ed")
    if base.endswith("y") and len(base) > 1 and base[-2].lower() not in "aeiou":
        forms.add(base[:-1] + "ies")
        forms.add(base[:-1] + "ied")

    forms_alt = "(?:" + "|".join(re.escape(f) for f in sorted(forms, key=len, reverse=True)) + ")"

    result = definition

    # 1. Strip the typical leading definition prefix.
    leading_re = re.compile(
        r"^\s*(?:to\s+)?(?:an?|the)?\s*" + forms_alt
        + r"\s+(?:means|is)(?:\s+to)?(?:\s+(?:an?|the))?\s+",
        flags=re.IGNORECASE,
    )
    result = leading_re.sub("", result, count=1)

    # 2. Remove remaining occurrences (anywhere) along with preceding article.
    inner_re = re.compile(
        r"\b(?:an?|the)\s+" + forms_alt + r"\b|\b" + forms_alt + r"\b",
        flags=re.IGNORECASE,
    )
    result = inner_re.sub("", result)

    # 3. Cleanup
    result = re.sub(r"\s+", " ", result)
    result = re.sub(r"\s+([,.;:!?])", r"\1", result)
    # Drop trailing dangling preposition before period: "kinds of." -> "kinds."
    result = re.sub(
        r"\s+(?:of|in|on|at|to|for|with|by|into|onto)\s*([.!?])",
        r"\1", result, flags=re.IGNORECASE,
    )
    # Collapse double "is is" / "to to" left behind
    result = re.sub(r"\b(is|to|a|an|the)\s+\1\b", r"\1", result, flags=re.IGNORECASE)
    # Drop dangling "To " at start (e.g. "To is to be..." after removing verb)
    result = re.sub(r"^to\s+(?=is\b|means\b)", "", result, flags=re.IGNORECASE)
    result = re.sub(r"^(?:to|is|means)\s+(?=to\b)", "", result, flags=re.IGNORECASE)

    result = result.strip(" ,;:")
    if result:
        result = result[0].upper() + result[1:]
    return result


PDF_GENERATORS = {
    "flashcards":         generate_flashcards_pdf,
    "images_only":        generate_images_only_pdf,
    "definitions_study":  generate_definitions_study_pdf,
    "definitions_game":   generate_definitions_game_pdf,
}
