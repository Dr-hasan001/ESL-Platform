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
    """Title block + name/date lines at the top of page 1."""
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(black)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 18 * mm, title)

    c.setFont("Helvetica", 11)
    c.setFillColor(HexColor("#444444"))
    c.drawCentredString(PAGE_W / 2, PAGE_H - 25 * mm, unit_label)

    c.setStrokeColor(black)
    c.setLineWidth(0.6)
    c.setFillColor(black)
    c.setFont("Helvetica", 10)
    y = PAGE_H - 35 * mm
    c.drawString(15 * mm, y, "Name:")
    c.line(28 * mm, y - 1, 100 * mm, y - 1)
    c.drawString(110 * mm, y, "Date:")
    c.line(123 * mm, y - 1, 180 * mm, y - 1)

    c.setLineWidth(1.2)
    c.line(15 * mm, y - 7 * mm, PAGE_W - 15 * mm, y - 7 * mm)


def _draw_section_title(c: canvas.Canvas, y: float, label: str, hint: str = ""):
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(black)
    c.drawString(15 * mm, y, label)
    if hint:
        c.setFont("Helvetica-Oblique", 9.5)
        c.setFillColor(HexColor("#666666"))
        c.drawString(15 * mm, y - 5.5 * mm, hint)


# Layout for Image MCQs: 2 columns x N rows, each cell ~ (95 x 70) mm
IMG_Q_COLS = 2
IMG_Q_ROWS = 3
IMG_Q_W = (PAGE_W - 2 * 15 * mm) / IMG_Q_COLS
IMG_Q_H = 73 * mm
IMG_Q_PER_PAGE = IMG_Q_COLS * IMG_Q_ROWS


def _draw_image_question(c: canvas.Canvas, x: float, y: float, num: int, word_obj, options: list, letters="abcd"):
    """Draws one image-MCQ cell. y is the BOTTOM-left of the cell."""
    img_h = 38 * mm
    img_w = IMG_Q_W - 12 * mm

    # Question number
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(black)
    c.drawString(x + 4 * mm, y + IMG_Q_H - 6 * mm, f"{num}.")

    # Image
    img_path = _resolve_image_path(getattr(word_obj, "image_url", None))
    img_x = x + 6 * mm
    img_y = y + IMG_Q_H - 6 * mm - img_h
    if img_path:
        _draw_image_fitted(c, img_path, img_x, img_y, img_w, img_h, padding=0)
    else:
        # placeholder rectangle
        c.setStrokeColor(HexColor("#999999"))
        c.setLineWidth(0.4)
        c.rect(img_x, img_y, img_w, img_h, stroke=1, fill=0)
        c.setFont("Helvetica-Oblique", 9)
        c.setFillColor(HexColor("#999999"))
        c.drawCentredString(img_x + img_w / 2, img_y + img_h / 2 - 3, "(no image)")

    # Options — 2 rows of 2
    c.setFont("Helvetica", 10.5)
    c.setFillColor(black)
    opt_y = img_y - 6 * mm
    for i, opt in enumerate(options[:4]):
        row = i // 2
        col = i % 2
        ox = x + 6 * mm + col * (img_w / 2)
        oy = opt_y - row * 5.5 * mm
        c.drawString(ox, oy, f"  {letters[i]}) {opt}")


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
    """Final page with answer key — teacher detaches before handing out."""
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(black)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 20 * mm, "TEACHER ANSWER KEY (detach before handing out)")
    c.setStrokeColor(HexColor("#C84830"))
    c.setLineWidth(0.8)
    c.line(15 * mm, PAGE_H - 24 * mm, PAGE_W - 15 * mm, PAGE_H - 24 * mm)

    y = PAGE_H - 35 * mm

    if image_answers:
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(black)
        c.drawString(15 * mm, y, "Part 1 — Picture → word")
        y -= 7 * mm
        c.setFont("Helvetica", 11)
        for num, word in image_answers:
            if y < 18 * mm:
                c.showPage()
                y = PAGE_H - 20 * mm
            c.drawString(20 * mm, y, f"{num}.  {word}")
            y -= 5.5 * mm
        y -= 4 * mm

    if blank_answers:
        if y < 30 * mm:
            c.showPage()
            y = PAGE_H - 20 * mm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(15 * mm, y, "Part 2 — Fill in the blank")
        y -= 7 * mm
        c.setFont("Helvetica", 11)
        for num, word in blank_answers:
            if y < 18 * mm:
                c.showPage()
                y = PAGE_H - 20 * mm
            c.drawString(20 * mm, y, f"{num}.  {word}")
            y -= 5.5 * mm


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

    # Page 1 header
    _draw_exam_header(c, exam_title, unit_label)

    # Track answer key
    img_words_chosen = []

    # ── Image MCQ section ────────────────────────────────────────────────────
    candidates_img = [w for w in word_pool if getattr(w, "image_url", None)]
    chosen_img = random.sample(candidates_img, min(num_image_q, len(candidates_img))) if candidates_img else []

    if chosen_img:
        _draw_section_title(c, PAGE_H - 48 * mm,
                           "Part 1 — Look at the picture and circle the correct word.",
                           hint="Circle one letter per question.")
        start_y = PAGE_H - 60 * mm
        on_page = 0
        num = 1
        for w in chosen_img:
            if on_page >= IMG_Q_PER_PAGE:
                c.showPage()
                on_page = 0
                _draw_section_title(c, PAGE_H - 18 * mm, "Part 1 (continued)", "")
                start_y = PAGE_H - 28 * mm
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
        c.showPage()
        next_num = num
    else:
        next_num = 1

    # ── Fill in the blank section ────────────────────────────────────────────
    blank_candidates = [w for w in word_pool if (getattr(w, "example", None) and getattr(w, "word", None))]
    chosen_blanks = random.sample(blank_candidates, min(num_blank_q, len(blank_candidates))) if blank_candidates else []

    blank_words_chosen = []
    if chosen_blanks:
        # If we're on the first page already (no image section ran), draw header
        if not chosen_img:
            _draw_exam_header(c, exam_title, unit_label)
            y = PAGE_H - 50 * mm
        else:
            y = PAGE_H - 20 * mm

        _draw_section_title(c, y, "Part 2 — Fill in the blank with the correct word.",
                           hint="Write the missing word on the blank line in each sentence.")
        y -= 12 * mm

        style = ParagraphStyle(
            name="exam_blank", fontName="Helvetica", fontSize=11.5,
            leading=15, textColor=black, alignment=TA_LEFT,
        )
        avail_w = PAGE_W - 30 * mm
        bottom = 18 * mm
        for w in chosen_blanks:
            text = _blank_word_in_sentence(w.word, w.example or "")
            p = Paragraph(f"<b>{next_num}.</b> &nbsp;&nbsp; {text}", style)
            _, p_h = p.wrap(avail_w, 999)
            row_h = p_h + 6 * mm
            if y - row_h < bottom:
                c.showPage()
                _draw_section_title(c, PAGE_H - 18 * mm, "Part 2 (continued)", "")
                y = PAGE_H - 30 * mm
            p.drawOn(c, 15 * mm, y - p_h)
            y -= row_h
            blank_words_chosen.append((next_num, w.word))
            next_num += 1
        c.showPage()

    # ── Answer key ───────────────────────────────────────────────────────────
    _draw_answer_key(c, img_words_chosen, blank_words_chosen)

    c.save()
    return buf.getvalue()
