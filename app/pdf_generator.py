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


# ─────────────────────────────────────────────────────────────────────────────
# Weekly Exam generator
# ─────────────────────────────────────────────────────────────────────────────

import random
from reportlab.lib.enums import TA_LEFT

# Elegant palette
EXAM_INK = HexColor("#1A1209")          # dark, near-black body text
EXAM_ACCENT = HexColor("#8B1F12")        # deep crimson — used sparingly
EXAM_MUTED = HexColor("#7A6E63")         # soft gray for hints
EXAM_RULE = HexColor("#C9BFB4")          # divider rule
EXAM_BANK_BG = HexColor("#FAF5EC")       # cream — word bank background
EXAM_BANK_BORDER = HexColor("#D8C9A6")   # warm gold border

# Words whose images are too abstract / ambiguous to make good MCQ stimuli.
# Stripped from the image-question pool but still eligible for fill-in-the-blank.
ABSTRACT_FOR_IMAGE = {
    "soul", "despair", "gloom", "regret", "ugly", "maybe", "somewhat",
    "value", "exist", "form", "process", "status", "spectrum", "scale",
    "experience", "qualify", "sufficient", "tough", "smooth", "stable",
    "fantastic", "obvious", "apparent", "hidden", "original", "double",
    "best", "easy", "short", "ancient", "classic", "formal", "junior",
    "prime", "sincere", "solitary", "blind",
}


def _blank_word_in_sentence(word: str, sentence: str) -> str:
    """Replace the target word (and inflections) with a blank line."""
    if not sentence or not word:
        return sentence or ""
    base = word.strip()
    forms = {base, base + "s", base + "es", base + "ed", base + "ing", base + "d"}
    if base.endswith("e"):
        forms.add(base[:-1] + "ing")
        forms.add(base[:-1] + "ed")
    if base.endswith("y") and len(base) > 1 and base[-2].lower() not in "aeiou":
        forms.add(base[:-1] + "ies")
        forms.add(base[:-1] + "ied")
    # CVC rule — short verbs ending consonant-vowel-consonant double the final consonant
    # before -ed / -ing (skip→skipped/skipping, rob→robbed, plan→planned, etc.).
    if (
        len(base) >= 3
        and base[-1].lower() not in "aeiouwxy"
        and base[-2].lower() in "aeiou"
        and base[-3].lower() not in "aeiou"
    ):
        forms.add(base + base[-1] + "ed")
        forms.add(base + base[-1] + "ing")
    forms_alt = "(?:" + "|".join(re.escape(f) for f in sorted(forms, key=len, reverse=True)) + ")"
    pattern = r"\b" + forms_alt + r"\b"
    blanked = re.sub(pattern, "______________", sentence, flags=re.IGNORECASE)
    return blanked


def _draw_exam_header(c: canvas.Canvas, title: str, unit_label: str):
    """Elegant title block with double-rule frame, Name/Date lines."""
    # Top decorative rule
    c.setStrokeColor(EXAM_INK)
    c.setLineWidth(0.6)
    c.line(15 * mm, PAGE_H - 12 * mm, PAGE_W - 15 * mm, PAGE_H - 12 * mm)

    # Title (elegant serif, generous tracking via uppercase)
    c.setFillColor(EXAM_INK)
    c.setFont("Times-Bold", 22)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 22 * mm, title.upper())

    # Subtitle — italic, smaller
    c.setFont("Times-Italic", 11.5)
    c.setFillColor(EXAM_MUTED)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 28 * mm, unit_label)

    # Thin decorative rule under title
    c.setStrokeColor(EXAM_RULE)
    c.setLineWidth(0.4)
    c.line(70 * mm, PAGE_H - 32 * mm, PAGE_W - 70 * mm, PAGE_H - 32 * mm)

    # Name / Date row — minimal labels with hairline lines
    y = PAGE_H - 42 * mm
    c.setStrokeColor(EXAM_INK)
    c.setLineWidth(0.5)
    c.setFillColor(EXAM_INK)
    c.setFont("Helvetica", 9.5)
    c.drawString(15 * mm, y, "NAME")
    c.line(28 * mm, y - 0.5, 105 * mm, y - 0.5)
    c.drawString(115 * mm, y, "DATE")
    c.line(127 * mm, y - 0.5, PAGE_W - 15 * mm, y - 0.5)

    # Bottom rule of header block — heavier
    c.setStrokeColor(EXAM_INK)
    c.setLineWidth(0.9)
    c.line(15 * mm, y - 6 * mm, PAGE_W - 15 * mm, y - 6 * mm)


def _draw_section_title(c: canvas.Canvas, y: float, roman: str, label: str, hint: str = ""):
    """Part header styled as PART I — Label with rule and italic hint."""
    c.setFillColor(EXAM_ACCENT)
    c.setFont("Times-Bold", 12)
    c.drawString(15 * mm, y, roman.upper())
    c.setFillColor(EXAM_INK)
    c.setFont("Times-Bold", 13.5)
    c.drawString(15 * mm + 22 * mm, y, label)
    # Decorative hairline under the title
    c.setStrokeColor(EXAM_RULE)
    c.setLineWidth(0.5)
    c.line(15 * mm, y - 2.5 * mm, PAGE_W - 15 * mm, y - 2.5 * mm)
    if hint:
        c.setFont("Times-Italic", 9.5)
        c.setFillColor(EXAM_MUTED)
        c.drawString(15 * mm, y - 7 * mm, hint)


def _draw_page_footer(c: canvas.Canvas, page_num: int, total_pages: int | None = None):
    """Small footer with page number — centered."""
    c.setFont("Times-Italic", 8.5)
    c.setFillColor(EXAM_MUTED)
    txt = f"— {page_num} —" if total_pages is None else f"— {page_num} of {total_pages} —"
    c.drawCentredString(PAGE_W / 2, 10 * mm, txt)


# Layout for Image MCQs — fewer per page so each can breathe
IMG_Q_COLS = 2
IMG_Q_ROWS = 2  # 4 questions per page now (was 6, too cramped)
IMG_Q_W = (PAGE_W - 2 * 15 * mm) / IMG_Q_COLS
IMG_Q_H = 115 * mm
IMG_Q_PER_PAGE = IMG_Q_COLS * IMG_Q_ROWS


def _draw_image_question(c: canvas.Canvas, x: float, y: float, num: int, word_obj, options: list, letters="abcd"):
    """One elegant image-MCQ cell with generous spacing between image and choices.
    y is the BOTTOM-left of the cell."""
    cell_inner_x = x + 8 * mm
    inner_w = IMG_Q_W - 16 * mm

    # Question number — elegant serif
    c.setFillColor(EXAM_INK)
    c.setFont("Times-Bold", 13)
    c.drawString(cell_inner_x, y + IMG_Q_H - 8 * mm, f"{num}.")

    # Image — large, framed with subtle border
    img_h = 60 * mm
    img_w = inner_w - 4 * mm
    img_x = cell_inner_x + 2 * mm
    img_y = y + IMG_Q_H - 12 * mm - img_h
    img_path = _resolve_image_path(getattr(word_obj, "image_url", None))
    if img_path:
        _draw_image_fitted(c, img_path, img_x, img_y, img_w, img_h, padding=0)
    else:
        c.setStrokeColor(EXAM_RULE)
        c.setLineWidth(0.4)
        c.rect(img_x, img_y, img_w, img_h, stroke=1, fill=0)
        c.setFont("Times-Italic", 9)
        c.setFillColor(EXAM_MUTED)
        c.drawCentredString(img_x + img_w / 2, img_y + img_h / 2 - 3, "(no image)")

    # Thin frame around the image
    c.setStrokeColor(EXAM_RULE)
    c.setLineWidth(0.4)
    c.rect(img_x, img_y, img_w, img_h, stroke=1, fill=0)

    # Generous gap between image and options — 10mm
    options_y = img_y - 12 * mm

    # Options — 2 rows × 2 cols with circle bullets to mark answers
    c.setFont("Helvetica", 11)
    c.setFillColor(EXAM_INK)
    col_w = inner_w / 2
    row_gap = 7 * mm
    for i, opt in enumerate(options[:4]):
        row = i // 2
        col = i % 2
        ox = cell_inner_x + col * col_w
        oy = options_y - row * row_gap
        # circle for letter
        c.setStrokeColor(EXAM_INK)
        c.setLineWidth(0.6)
        c.circle(ox + 2.5 * mm, oy + 1.2 * mm, 2.5 * mm, stroke=1, fill=0)
        c.setFont("Times-Bold", 9.5)
        c.setFillColor(EXAM_INK)
        c.drawCentredString(ox + 2.5 * mm, oy - 0.5 * mm, letters[i])
        c.setFont("Helvetica", 11)
        c.drawString(ox + 7 * mm, oy, opt)


def _generate_image_questions(c: canvas.Canvas, word_pool: list, count: int, distractor_pool: list, start_num: int = 1) -> int:
    """Draws `count` image questions. Returns the question number used for the
    next section. Inserts page breaks as needed."""
    # Filter to words that actually have images
    candidates = [w for w in word_pool if getattr(w, "image_url", None)]
    if not candidates:
        return start_num

    chosen = random.sample(candidates, min(count, len(candidates)))

    on_page = 0
    num = start_num
    # State: are we on the first page? If so, content starts BELOW the header.
    # Otherwise, start near top of page.
    first_page_start_y = PAGE_H - 50 * mm  # below header rules
    later_page_start_y = PAGE_H - 18 * mm
    started_first_page_content = True

    # Section title above the first row
    _draw_section_title(c, first_page_start_y + 2 * mm, "Part 1 — Look at the picture and circle the correct word.",
                       hint="Circle one letter (a, b, c, or d) per question.")
    start_y = first_page_start_y - 10 * mm

    for w in chosen:
        if on_page >= IMG_Q_PER_PAGE:
            c.showPage()
            on_page = 0
            started_first_page_content = False
            start_y = later_page_start_y
            _draw_section_title(c, start_y + 2 * mm, "Part 1 (continued)", "")
            start_y -= 10 * mm

        row = on_page // IMG_Q_COLS
        col = on_page % IMG_Q_COLS
        x = 15 * mm + col * IMG_Q_W
        y = start_y - (row + 1) * IMG_Q_H

        # Build options: correct answer + 3 random distractors from full pool
        distractors_avail = [d.word for d in distractor_pool if d.id != w.id]
        random.shuffle(distractors_avail)
        opts = [w.word] + distractors_avail[:3]
        random.shuffle(opts)

        _draw_image_question(c, x, y, num, w, opts)
        on_page += 1
        num += 1

    # Flush page after image section
    c.showPage()
    return num


def _generate_blank_questions(c: canvas.Canvas, word_pool: list, count: int, start_num: int = 1) -> list:
    """Draws fill-in-the-blank questions across pages. Returns list of (num, correct_word) for the answer key."""
    candidates = [w for w in word_pool if (getattr(w, "example", None) and getattr(w, "word", None))]
    if not candidates:
        return []

    chosen = random.sample(candidates, min(count, len(candidates)))

    _draw_section_title(c, PAGE_W and (PAGE_H - 18 * mm),
                       "Part 2 — Fill in the blank with the correct word.",
                       hint="Write your answer on the line.")

    style = ParagraphStyle(
        name="exam_blank",
        fontName="Helvetica",
        fontSize=11.5,
        leading=15,
        textColor=black,
        alignment=TA_LEFT,
    )

    y = PAGE_H - 30 * mm
    bottom = 18 * mm
    answer_key = []
    num = start_num
    for w in chosen:
        text = _blank_word_in_sentence(w.word, w.example or "")
        # Render as a Paragraph for wrapping
        p = Paragraph(f"<b>{num}.</b> &nbsp;&nbsp; {text}", style)
        avail_w = PAGE_W - 30 * mm
        _, p_h = p.wrap(avail_w, 999)
        # Add space for an answer line below
        row_h = p_h + 8 * mm
        if y - row_h < bottom:
            c.showPage()
            _draw_section_title(c, PAGE_H - 18 * mm, "Part 2 (continued)", "")
            y = PAGE_H - 30 * mm
        # Draw paragraph
        p.drawOn(c, 15 * mm, y - p_h)
        # No extra line — the blank in the sentence IS the answer line
        y -= row_h
        answer_key.append((num, w.word))
        num += 1

    c.showPage()
    return answer_key


def _draw_answer_key(c: canvas.Canvas, image_answers: list, blank_answers: list):
    """Final page with elegant answer key — teacher detaches before handing out."""
    # Top decorative rule
    c.setStrokeColor(EXAM_ACCENT)
    c.setLineWidth(0.9)
    c.line(15 * mm, PAGE_H - 14 * mm, PAGE_W - 15 * mm, PAGE_H - 14 * mm)

    c.setFont("Times-Bold", 16)
    c.setFillColor(EXAM_ACCENT)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 22 * mm, "TEACHER ANSWER KEY")
    c.setFont("Times-Italic", 10.5)
    c.setFillColor(EXAM_MUTED)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 28 * mm, "Detach this page before handing the exam to students.")

    c.setStrokeColor(EXAM_RULE)
    c.setLineWidth(0.4)
    c.line(15 * mm, PAGE_H - 32 * mm, PAGE_W - 15 * mm, PAGE_H - 32 * mm)

    # Two-column layout for answers
    col_w = (PAGE_W - 30 * mm - 8 * mm) / 2
    y = PAGE_H - 42 * mm

    def draw_section(label, items, y_start):
        c.setFillColor(EXAM_INK)
        c.setFont("Times-Bold", 12.5)
        c.drawString(15 * mm, y_start, label)
        c.setStrokeColor(EXAM_RULE)
        c.setLineWidth(0.3)
        c.line(15 * mm, y_start - 2 * mm, PAGE_W - 15 * mm, y_start - 2 * mm)
        yy = y_start - 8 * mm

        per_col = (len(items) + 1) // 2
        for idx, (num, word) in enumerate(items):
            col = idx // per_col
            row = idx % per_col
            cx = 15 * mm + col * (col_w + 8 * mm)
            cy = yy - row * 6 * mm
            if cy < 18 * mm:
                c.showPage()
                cy = PAGE_H - 20 * mm
            c.setFont("Helvetica", 11)
            c.setFillColor(EXAM_INK)
            c.drawString(cx, cy, f"{num}.")
            c.setFont("Times-Bold", 11)
            c.drawString(cx + 8 * mm, cy, word)
        return yy - per_col * 6 * mm - 6 * mm

    if image_answers:
        y = draw_section("Part I — Picture → Word", image_answers, y)

    if blank_answers:
        if y < 30 * mm:
            c.showPage()
            y = PAGE_H - 20 * mm
        y = draw_section("Part II — Fill in the Blank", blank_answers, y)


def _draw_word_bank(c: canvas.Canvas, y_top: float, words: list) -> float:
    """Draws a cream box at the top of the fill-in-blank section containing the
    answer words (shuffled). Returns the y-position below the box."""
    if not words:
        return y_top

    shuffled = list(words)
    random.shuffle(shuffled)

    box_x = 15 * mm
    box_w = PAGE_W - 30 * mm
    pad = 6 * mm

    # Label above the box
    c.setFont("Times-Bold", 10)
    c.setFillColor(EXAM_ACCENT)
    c.drawString(box_x, y_top, "WORD BANK")
    label_h = 4 * mm

    # Build chip layout — wrap chips across lines
    chip_font = "Helvetica"
    chip_size = 11
    c.setFont(chip_font, chip_size)
    chip_gap_x = 4 * mm
    chip_gap_y = 5 * mm
    chip_pad_x = 3 * mm
    chip_pad_y = 1.6 * mm

    # First pass — measure rows
    rows = [[]]   # list of rows, each is list of (word, width)
    cur_w = 0
    inner_w = box_w - 2 * pad
    for w in shuffled:
        tw = c.stringWidth(w, chip_font, chip_size) + 2 * chip_pad_x
        if cur_w + tw + chip_gap_x > inner_w and rows[-1]:
            rows.append([])
            cur_w = 0
        rows[-1].append((w, tw))
        cur_w += tw + chip_gap_x

    chip_h = chip_size + 2 * chip_pad_y
    box_h = pad * 2 + len(rows) * chip_h + (len(rows) - 1) * chip_gap_y
    box_top = y_top - label_h
    box_bot = box_top - box_h

    # Box
    c.setFillColor(EXAM_BANK_BG)
    c.setStrokeColor(EXAM_BANK_BORDER)
    c.setLineWidth(0.8)
    c.roundRect(box_x, box_bot, box_w, box_h, 4 * mm, stroke=1, fill=1)

    # Chips
    cy = box_top - pad - chip_h
    for row in rows:
        # center the row horizontally inside the box
        row_w = sum(w for _, w in row) + chip_gap_x * (len(row) - 1)
        cx = box_x + (box_w - row_w) / 2
        for word, tw in row:
            # subtle chip outline
            c.setStrokeColor(EXAM_BANK_BORDER)
            c.setFillColor(white)
            c.setLineWidth(0.4)
            c.roundRect(cx, cy, tw, chip_h, 2 * mm, stroke=1, fill=1)
            c.setFillColor(EXAM_INK)
            c.setFont(chip_font, chip_size)
            c.drawCentredString(cx + tw / 2, cy + chip_pad_y, word)
            cx += tw + chip_gap_x
        cy -= chip_h + chip_gap_y

    return box_bot - 6 * mm


def generate_exam_pdf(
    unit_label: str,
    word_pool: list,
    num_image_q: int,
    num_blank_q: int,
    exam_title: str = "Weekly Vocabulary Exam",
) -> bytes:
    """Build a printable exam PDF mixing Image→Word MCQs and fill-in-the-blank
    questions drawn from `word_pool` (words across teacher-chosen units).
    Last page is an answer key for the teacher."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(exam_title)

    # Track page numbers for the footer
    page_num = [1]

    def page_break():
        _draw_page_footer(c, page_num[0])
        c.showPage()
        page_num[0] += 1

    # Page 1 header
    _draw_exam_header(c, exam_title, unit_label)

    # Track answer key
    img_words_chosen = []

    # ── Image MCQ section ────────────────────────────────────────────────────
    # Concrete-word pool only: image must exist AND word not in the abstract list
    candidates_img = [
        w for w in word_pool
        if getattr(w, "image_url", None)
        and (w.word or "").strip().lower() not in ABSTRACT_FOR_IMAGE
    ]
    # Fallback — if filter wipes everything, use any image we have
    if not candidates_img:
        candidates_img = [w for w in word_pool if getattr(w, "image_url", None)]
    chosen_img = random.sample(candidates_img, min(num_image_q, len(candidates_img))) if candidates_img else []

    if chosen_img:
        _draw_section_title(c, PAGE_H - 56 * mm,
                           "Part I", "Look at the picture and circle the correct word.",
                           hint="Circle one letter (a, b, c, or d) for each question.")
        start_y = PAGE_H - 66 * mm
        on_page = 0
        num = 1
        for w in chosen_img:
            if on_page >= IMG_Q_PER_PAGE:
                page_break()
                on_page = 0
                _draw_section_title(c, PAGE_H - 20 * mm, "Part I", "(continued)")
                start_y = PAGE_H - 30 * mm
            row = on_page // IMG_Q_COLS
            col = on_page % IMG_Q_COLS
            x = 15 * mm + col * IMG_Q_W
            y = start_y - (row + 1) * IMG_Q_H

            distractors = [d.word for d in word_pool if d.id != w.id]
            random.shuffle(distractors)
            opts = [w.word] + distractors[:3]
            random.shuffle(opts)
            _draw_image_question(c, x, y, num, w, opts)

            img_words_chosen.append((num, w.word))
            num += 1
            on_page += 1
        page_break()
        next_num = num
    else:
        next_num = 1

    # ── Fill in the blank section ────────────────────────────────────────────
    blank_candidates = [w for w in word_pool if (getattr(w, "example", None) and getattr(w, "word", None))]
    chosen_blanks = random.sample(blank_candidates, min(num_blank_q, len(blank_candidates))) if blank_candidates else []

    blank_words_chosen = []
    if chosen_blanks:
        # Header if no image section ran
        if not chosen_img:
            _draw_exam_header(c, exam_title, unit_label)
            y = PAGE_H - 56 * mm
        else:
            y = PAGE_H - 20 * mm

        _draw_section_title(c, y, "Part II", "Fill in the blank with the correct word.",
                           hint="Choose a word from the Word Bank and write it on the blank line.")
        y -= 12 * mm

        # Word bank box — at the top of part 2
        bank_words = [w.word for w in chosen_blanks]
        y = _draw_word_bank(c, y, bank_words)
        y -= 4 * mm

        style = ParagraphStyle(
            name="exam_blank", fontName="Times-Roman", fontSize=12,
            leading=17, textColor=EXAM_INK, alignment=TA_LEFT,
        )
        avail_w = PAGE_W - 30 * mm
        bottom = 18 * mm
        for w in chosen_blanks:
            text = _blank_word_in_sentence(w.word, w.example or "")
            p = Paragraph(f'<font name="Times-Bold">{next_num}.</font> &nbsp; {text}', style)
            _, p_h = p.wrap(avail_w, 999)
            row_h = p_h + 5 * mm
            if y - row_h < bottom:
                page_break()
                _draw_section_title(c, PAGE_H - 20 * mm, "Part II", "(continued)")
                y = PAGE_H - 32 * mm
            p.drawOn(c, 15 * mm, y - p_h)
            y -= row_h
            blank_words_chosen.append((next_num, w.word))
            next_num += 1
        page_break()

    # ── Answer key — teacher's last page ─────────────────────────────────────
    _draw_answer_key(c, img_words_chosen, blank_words_chosen)
    # final footer
    _draw_page_footer(c, page_num[0])

    c.save()
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# Homework: Answer-Key PDF (teacher only) and Results Report PDF
# ─────────────────────────────────────────────────────────────────────────────

def _letter(i: int) -> str:
    return "ABCD"[i] if 0 <= i < 4 else "?"


def generate_answer_key_pdf(hw, questions) -> bytes:
    """Render a printable answer key for a homework assignment.

    `hw` is a HomeworkAssignment, `questions` an iterable of HomeworkQuestion
    ordered by position. Reuses the elegant exam typography palette.
    """
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"{hw.title} — Answer Key")

    # Header
    c.setStrokeColor(EXAM_ACCENT)
    c.setLineWidth(0.9)
    c.line(15 * mm, PAGE_H - 14 * mm, PAGE_W - 15 * mm, PAGE_H - 14 * mm)

    c.setFont("Times-Bold", 20)
    c.setFillColor(EXAM_ACCENT)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 24 * mm, "TEACHER ANSWER KEY")

    c.setFont("Times-Italic", 11.5)
    c.setFillColor(EXAM_MUTED)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 30 * mm, hw.title)

    if hw.type:
        c.setFont("Helvetica", 9.5)
        c.setFillColor(EXAM_MUTED)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 35 * mm,
                            hw.type.replace("_", " ").upper())

    c.setStrokeColor(EXAM_RULE)
    c.setLineWidth(0.4)
    c.line(15 * mm, PAGE_H - 39 * mm, PAGE_W - 15 * mm, PAGE_H - 39 * mm)

    # Body — one question per block
    from reportlab.lib.utils import simpleSplit
    y = PAGE_H - 48 * mm
    bottom = 20 * mm
    page_num = 1

    def page_break(new_y):
        nonlocal page_num
        _draw_page_footer(c, page_num)
        c.showPage()
        page_num += 1
        c.setFont("Times-Italic", 9.5)
        c.setFillColor(EXAM_MUTED)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 12 * mm,
                            f"{hw.title} — Answer Key (continued)")
        c.setStrokeColor(EXAM_RULE)
        c.setLineWidth(0.3)
        c.line(15 * mm, PAGE_H - 14 * mm, PAGE_W - 15 * mm, PAGE_H - 14 * mm)
        return PAGE_H - 22 * mm

    if not list(questions):
        # No questions at all — print a friendly note
        c.setFont("Times-Italic", 12)
        c.setFillColor(EXAM_MUTED)
        c.drawCentredString(PAGE_W / 2, PAGE_H / 2,
                            "This assignment has no questions yet.")
        _draw_page_footer(c, page_num)
        c.save()
        return buf.getvalue()

    avail_w = PAGE_W - 30 * mm
    for q in questions:
        # Question text
        c.setFont("Times-Bold", 11.5)
        c.setFillColor(EXAM_INK)
        num_w = c.stringWidth(f"{q.position}.", "Times-Bold", 11.5)

        q_lines = simpleSplit(q.question_text or "", "Times-Roman", 11.5,
                              avail_w - num_w - 4 * mm)
        block_h = 6 * mm + len(q_lines) * 5.5 * mm + 2 * mm

        # Options/answer block
        if q.question_type == "multiple_choice" and q.options:
            block_h += len(q.options) * 5.5 * mm + 2 * mm
        else:
            block_h += 7 * mm

        if y - block_h < bottom:
            y = page_break(y)

        # Draw the number + question text
        c.setFont("Times-Bold", 11.5)
        c.setFillColor(EXAM_INK)
        c.drawString(15 * mm, y, f"{q.position}.")
        c.setFont("Times-Roman", 11.5)
        for i, line in enumerate(q_lines):
            c.drawString(15 * mm + num_w + 2 * mm, y - i * 5.5 * mm, line)
        y -= max(1, len(q_lines)) * 5.5 * mm + 3 * mm

        # Options or text answer
        if q.question_type == "multiple_choice" and q.options:
            for i, opt in enumerate(q.options):
                is_correct = (q.correct_index is not None and i == q.correct_index)
                # Filled bullet for correct, hollow for distractor
                if is_correct:
                    c.setFillColor(EXAM_ACCENT)
                    c.setStrokeColor(EXAM_ACCENT)
                    c.circle(20 * mm, y + 1.2 * mm, 1.6 * mm, stroke=1, fill=1)
                    c.setFont("Helvetica-Bold", 10.5)
                    c.setFillColor(EXAM_ACCENT)
                else:
                    c.setStrokeColor(EXAM_RULE)
                    c.setFillColor(white)
                    c.circle(20 * mm, y + 1.2 * mm, 1.6 * mm, stroke=1, fill=1)
                    c.setFont("Helvetica", 10.5)
                    c.setFillColor(EXAM_INK)
                c.drawString(25 * mm, y, f"{_letter(i)}.  {opt}")
                y -= 5.5 * mm
            y -= 2 * mm
        else:
            # Fill-blank / short-answer: show the expected text
            c.setFont("Helvetica-Bold", 10.5)
            c.setFillColor(EXAM_ACCENT)
            c.drawString(20 * mm, y, "Answer:")
            c.setFont("Times-Roman", 11)
            c.setFillColor(EXAM_INK)
            c.drawString(38 * mm, y, q.correct_text or "—")
            y -= 7 * mm

        # Hairline between questions
        c.setStrokeColor(EXAM_RULE)
        c.setLineWidth(0.3)
        c.line(15 * mm, y + 1 * mm, PAGE_W - 15 * mm, y + 1 * mm)
        y -= 3 * mm

    _draw_page_footer(c, page_num)
    c.save()
    return buf.getvalue()


def generate_results_pdf(hw, student_rows) -> bytes:
    """Render a printable grade report.

    `student_rows` is a list of dicts:
        {"student": User, "submission": Submission|None}
    """
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"{hw.title} — Results")

    # Header
    c.setStrokeColor(EXAM_INK)
    c.setLineWidth(0.6)
    c.line(15 * mm, PAGE_H - 12 * mm, PAGE_W - 15 * mm, PAGE_H - 12 * mm)

    c.setFont("Times-Bold", 20)
    c.setFillColor(EXAM_INK)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 22 * mm, "RESULTS REPORT")

    c.setFont("Times-Italic", 11.5)
    c.setFillColor(EXAM_MUTED)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 28 * mm, hw.title)

    c.setFont("Helvetica", 9.5)
    type_label = (hw.type or "").replace("_", " ").upper()
    due = f"  •  DUE {hw.due_date.isoformat()}" if getattr(hw, "due_date", None) else ""
    c.drawCentredString(PAGE_W / 2, PAGE_H - 33 * mm, f"{type_label}{due}")

    c.setStrokeColor(EXAM_RULE)
    c.setLineWidth(0.4)
    c.line(15 * mm, PAGE_H - 37 * mm, PAGE_W - 15 * mm, PAGE_H - 37 * mm)

    # Column layout
    x_name = 18 * mm
    x_status = 95 * mm
    x_score = 135 * mm
    x_date = 165 * mm

    y = PAGE_H - 47 * mm
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(EXAM_MUTED)
    c.drawString(x_name, y, "STUDENT")
    c.drawString(x_status, y, "STATUS")
    c.drawString(x_score, y, "SCORE")
    c.drawString(x_date, y, "SUBMITTED")
    c.setStrokeColor(EXAM_INK)
    c.setLineWidth(0.5)
    c.line(15 * mm, y - 2 * mm, PAGE_W - 15 * mm, y - 2 * mm)
    y -= 8 * mm

    page_num = 1
    bottom = 22 * mm

    def page_break():
        nonlocal page_num
        _draw_page_footer(c, page_num)
        c.showPage()
        page_num += 1
        c.setFont("Times-Italic", 9.5)
        c.setFillColor(EXAM_MUTED)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 12 * mm,
                            f"{hw.title} — Results (continued)")
        new_y = PAGE_H - 22 * mm
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(EXAM_MUTED)
        c.drawString(x_name, new_y, "STUDENT")
        c.drawString(x_status, new_y, "STATUS")
        c.drawString(x_score, new_y, "SCORE")
        c.drawString(x_date, new_y, "SUBMITTED")
        c.setStrokeColor(EXAM_INK)
        c.setLineWidth(0.5)
        c.line(15 * mm, new_y - 2 * mm, PAGE_W - 15 * mm, new_y - 2 * mm)
        return new_y - 8 * mm

    submitted = 0
    score_sum = 0.0
    score_n = 0

    for row in student_rows:
        if y < bottom:
            y = page_break()
        s = row["student"]
        sub = row.get("submission")

        # Name (bold) and username (light)
        c.setFont("Times-Bold", 10.5)
        c.setFillColor(EXAM_INK)
        c.drawString(x_name, y, (s.display_name or s.username)[:38])
        c.setFont("Helvetica", 8.5)
        c.setFillColor(EXAM_MUTED)
        c.drawString(x_name, y - 4 * mm, s.username[:38])

        # Status
        c.setFont("Helvetica-Bold", 9.5)
        if sub and sub.is_complete:
            c.setFillColor(HexColor("#2A6B3D"))
            status = "Submitted"
            submitted += 1
        elif sub:
            c.setFillColor(HexColor("#a07800"))
            status = "In progress"
        else:
            c.setFillColor(HexColor("#C84830"))
            status = "Not started"
        c.drawString(x_status, y, status)

        # Score
        score_val = None
        if sub:
            if hw.type == "writing" and sub.teacher_score is not None:
                score_val = float(sub.teacher_score)
                c.setFont("Times-Bold", 11)
                c.setFillColor(EXAM_INK)
                c.drawString(x_score, y, f"{score_val:.0f}/100")
            elif sub.score is not None:
                score_val = float(sub.score)
                c.setFont("Times-Bold", 11)
                c.setFillColor(EXAM_INK)
                c.drawString(x_score, y, f"{score_val:.0f}%")
                if sub.correct_count is not None and sub.total_questions:
                    c.setFont("Helvetica", 8)
                    c.setFillColor(EXAM_MUTED)
                    c.drawString(x_score, y - 4 * mm,
                                 f"{sub.correct_count}/{sub.total_questions}")
            else:
                c.setFont("Helvetica", 10)
                c.setFillColor(EXAM_MUTED)
                c.drawString(x_score, y, "—")
        else:
            c.setFont("Helvetica", 10)
            c.setFillColor(EXAM_MUTED)
            c.drawString(x_score, y, "—")

        if score_val is not None:
            score_sum += score_val
            score_n += 1

        # Submitted date
        c.setFont("Helvetica", 9)
        c.setFillColor(EXAM_INK if sub else EXAM_MUTED)
        if sub and sub.submitted_at:
            c.drawString(x_date, y, sub.submitted_at.strftime("%b %d, %H:%M"))
        else:
            c.drawString(x_date, y, "—")

        # Row divider
        c.setStrokeColor(EXAM_RULE)
        c.setLineWidth(0.3)
        c.line(15 * mm, y - 6 * mm, PAGE_W - 15 * mm, y - 6 * mm)
        y -= 11 * mm

    # Summary footer
    if y < bottom + 20 * mm:
        y = page_break()
    y -= 4 * mm
    c.setStrokeColor(EXAM_INK)
    c.setLineWidth(0.7)
    c.line(15 * mm, y, PAGE_W - 15 * mm, y)
    y -= 6 * mm
    c.setFont("Times-Bold", 11)
    c.setFillColor(EXAM_INK)
    total = len(student_rows)
    c.drawString(15 * mm, y, f"Submitted: {submitted} / {total}")
    if score_n:
        avg = score_sum / score_n
        c.drawString(85 * mm, y, f"Average: {avg:.1f}")

    _draw_page_footer(c, page_num)
    c.save()
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# Branded editorial exam — dramatic cover page + image MCQs + fill-blank
# ─────────────────────────────────────────────────────────────────────────────

def _draw_editorial_cover(
    c: canvas.Canvas,
    *,
    eyebrow: str,
    title: str,
    subtitle: str,
    instructor: str,
    total_marks: int,
    show_name_date: bool = True,
):
    """A magazine-grade cover page. Pure typography, generous whitespace."""
    # Outer double rule — top
    c.setStrokeColor(EXAM_INK)
    c.setLineWidth(1.4)
    c.line(15 * mm, PAGE_H - 12 * mm, PAGE_W - 15 * mm, PAGE_H - 12 * mm)
    c.setLineWidth(0.4)
    c.line(15 * mm, PAGE_H - 14.5 * mm, PAGE_W - 15 * mm, PAGE_H - 14.5 * mm)

    # Eyebrow — tiny, tracked
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(EXAM_MUTED)
    spaced = "    ".join(list(eyebrow))
    c.drawCentredString(PAGE_W / 2, PAGE_H - 28 * mm, spaced)

    # Decorative accent rule
    c.setStrokeColor(EXAM_ACCENT)
    c.setLineWidth(0.6)
    c.line(PAGE_W / 2 - 18 * mm, PAGE_H - 34 * mm, PAGE_W / 2 + 18 * mm, PAGE_H - 34 * mm)

    # HERO title — large serif
    c.setFont("Times-Bold", 56)
    c.setFillColor(EXAM_INK)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 75 * mm, title)

    # Italic subtitle
    c.setFont("Times-Italic", 18)
    c.setFillColor(EXAM_ACCENT)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 90 * mm, subtitle)

    # Center ornament — three diamonds with side rules
    orn_y = PAGE_H - 108 * mm
    c.setStrokeColor(EXAM_RULE)
    c.setLineWidth(0.4)
    c.line(PAGE_W / 2 - 50 * mm, orn_y, PAGE_W / 2 - 12 * mm, orn_y)
    c.line(PAGE_W / 2 + 12 * mm, orn_y, PAGE_W / 2 + 50 * mm, orn_y)
    c.setFont("Times-Roman", 14)
    c.setFillColor(EXAM_ACCENT)
    c.drawCentredString(PAGE_W / 2, orn_y - 4, "❖  ❖  ❖")

    # Instructor block
    inst_y = PAGE_H - 132 * mm
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(EXAM_MUTED)
    c.drawCentredString(PAGE_W / 2, inst_y, "I  N  S  T  R  U  C  T  O  R")
    c.setFont("Times-Italic", 22)
    c.setFillColor(EXAM_INK)
    c.drawCentredString(PAGE_W / 2, inst_y - 10 * mm, instructor)

    # Lower decorative rule
    c.setStrokeColor(EXAM_INK)
    c.setLineWidth(0.6)
    c.line(15 * mm, PAGE_H - 165 * mm, PAGE_W - 15 * mm, PAGE_H - 165 * mm)

    # Student fill-in block — Name / Date
    if show_name_date:
        bx = 20 * mm
        bw = PAGE_W - 40 * mm
        by = PAGE_H - 195 * mm
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(EXAM_INK)
        c.drawString(bx, by, "NAME")
        c.setStrokeColor(EXAM_INK)
        c.setLineWidth(0.6)
        c.line(bx + 16 * mm, by - 0.5, bx + bw * 0.55, by - 0.5)

        c.drawString(bx + bw * 0.6, by, "DATE")
        c.line(bx + bw * 0.6 + 14 * mm, by - 0.5, bx + bw, by - 0.5)

    # Total marks box — bottom right
    box_w = 36 * mm
    box_h = 22 * mm
    box_x = PAGE_W - 15 * mm - box_w
    box_y = 30 * mm
    c.setStrokeColor(EXAM_ACCENT)
    c.setLineWidth(0.8)
    c.rect(box_x, box_y, box_w, box_h, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(EXAM_MUTED)
    c.drawCentredString(box_x + box_w / 2, box_y + box_h - 6, "T O T A L   M A R K S")
    c.setFont("Times-Bold", 22)
    c.setFillColor(EXAM_INK)
    c.drawCentredString(box_x + box_w / 2, box_y + 4 * mm, f"/  {total_marks}")

    # Bottom rule
    c.setLineWidth(1.4)
    c.setStrokeColor(EXAM_INK)
    c.line(15 * mm, 18 * mm, PAGE_W - 15 * mm, 18 * mm)
    c.setLineWidth(0.4)
    c.line(15 * mm, 15.5 * mm, PAGE_W - 15 * mm, 15.5 * mm)

    # Footer signature
    c.setFont("Helvetica", 7.5)
    c.setFillColor(EXAM_MUTED)
    c.drawCentredString(PAGE_W / 2, 11 * mm, f"{title.upper()}   ·   {instructor.upper()}")


def _draw_branded_page_header(c: canvas.Canvas, title: str, instructor: str):
    """Slim running header used on every interior page."""
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(EXAM_MUTED)
    c.drawString(15 * mm, PAGE_H - 10 * mm, title.upper())
    c.drawRightString(PAGE_W - 15 * mm, PAGE_H - 10 * mm, instructor.upper())
    c.setStrokeColor(EXAM_RULE)
    c.setLineWidth(0.3)
    c.line(15 * mm, PAGE_H - 12 * mm, PAGE_W - 15 * mm, PAGE_H - 12 * mm)


def generate_branded_exam_pdf(
    *,
    word_pool: list,
    num_image_q: int,
    num_blank_q: int,
    exam_title: str,
    instructor: str,
    unit_label: str,
    eyebrow: str = "ESL VOCABULARY",
) -> bytes:
    """Editorial-grade exam PDF — cover page, image MCQs, fill-in-blank with
    word bank, teacher answer key. All branding strings come from the caller."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"{exam_title} - {instructor}")

    total_marks = num_image_q + num_blank_q

    # ── Cover page ──────────────────────────────────────────────────────────
    _draw_editorial_cover(
        c,
        eyebrow=eyebrow,
        title=exam_title,
        subtitle=unit_label,
        instructor=instructor,
        total_marks=total_marks,
    )
    _draw_page_footer(c, 1)
    c.showPage()

    page_num = [2]

    def page_break():
        _draw_page_footer(c, page_num[0])
        c.showPage()
        page_num[0] += 1

    img_words_chosen = []

    # ── PART I — Image MCQs ─────────────────────────────────────────────────
    candidates_img = [
        w for w in word_pool
        if getattr(w, "image_url", None)
        and (w.word or "").strip().lower() not in ABSTRACT_FOR_IMAGE
    ]
    if not candidates_img:
        candidates_img = [w for w in word_pool if getattr(w, "image_url", None)]
    chosen_img = random.sample(candidates_img, min(num_image_q, len(candidates_img))) if candidates_img else []

    if chosen_img:
        _draw_branded_page_header(c, exam_title, instructor)
        _draw_section_title(
            c, PAGE_H - 22 * mm,
            "Part I", "Look at the picture and circle the correct word.",
            hint="Circle one letter (a, b, c, or d) for each question.",
        )
        start_y = PAGE_H - 34 * mm
        on_page = 0
        num = 1
        for w in chosen_img:
            if on_page >= IMG_Q_PER_PAGE:
                page_break()
                _draw_branded_page_header(c, exam_title, instructor)
                _draw_section_title(c, PAGE_H - 22 * mm, "Part I", "(continued)")
                start_y = PAGE_H - 34 * mm
                on_page = 0
            row = on_page // IMG_Q_COLS
            col = on_page % IMG_Q_COLS
            x = 15 * mm + col * IMG_Q_W
            y = start_y - (row + 1) * IMG_Q_H

            distractors = [d.word for d in word_pool if d.id != w.id]
            random.shuffle(distractors)
            opts = [w.word] + distractors[:3]
            random.shuffle(opts)
            _draw_image_question(c, x, y, num, w, opts)

            img_words_chosen.append((num, w.word))
            num += 1
            on_page += 1
        page_break()
        next_num = num
    else:
        next_num = 1

    # ── PART II — Fill in the blank with word bank ──────────────────────────
    blank_candidates = [w for w in word_pool if (getattr(w, "example", None) and getattr(w, "word", None))]
    chosen_blanks = random.sample(blank_candidates, min(num_blank_q, len(blank_candidates))) if blank_candidates else []

    blank_words_chosen = []
    if chosen_blanks:
        _draw_branded_page_header(c, exam_title, instructor)
        y = PAGE_H - 22 * mm
        _draw_section_title(
            c, y, "Part II", "Fill in the blank with the correct word.",
            hint="Choose a word from the Word Bank and write it on the blank line.",
        )
        y -= 12 * mm

        bank_words = [w.word for w in chosen_blanks]
        y = _draw_word_bank(c, y, bank_words)
        y -= 4 * mm

        style = ParagraphStyle(
            name="exam_blank", fontName="Times-Roman", fontSize=12,
            leading=18, textColor=EXAM_INK, alignment=TA_LEFT,
        )
        avail_w = PAGE_W - 30 * mm
        bottom = 18 * mm
        for w in chosen_blanks:
            text = _blank_word_in_sentence(w.word, w.example or "")
            p = Paragraph(f'<font name="Times-Bold">{next_num}.</font> &nbsp; {text}', style)
            _, p_h = p.wrap(avail_w, 999)
            row_h = p_h + 6 * mm
            if y - row_h < bottom:
                page_break()
                _draw_branded_page_header(c, exam_title, instructor)
                _draw_section_title(c, PAGE_H - 22 * mm, "Part II", "(continued)")
                y = PAGE_H - 34 * mm
            p.drawOn(c, 15 * mm, y - p_h)
            y -= row_h
            blank_words_chosen.append((next_num, w.word))
            next_num += 1
        page_break()

    # ── Teacher answer key (last page) ──────────────────────────────────────
    _draw_answer_key(c, img_words_chosen, blank_words_chosen)
    _draw_page_footer(c, page_num[0])

    c.save()
    return buf.getvalue()
