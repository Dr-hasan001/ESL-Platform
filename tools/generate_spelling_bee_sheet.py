"""
generate_spelling_bee_sheet.py
Single-page A4 answer sheet for the Level 1 Spelling Bee (Book 1, Units 1-13).

Two columns of 10 numbered boxes, sized for large handwriting. Matches the
house palette used by tools/generate_vocab_exam.py.

Run:
    py -3 tools/generate_spelling_bee_sheet.py           # blank student sheet
    py -3 tools/generate_spelling_bee_sheet.py --key     # teacher answer key
"""

import os
import sys

from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

# ── Palette (matches generate_vocab_exam.py) ──────────────────────────────────
INK = HexColor("#1A1209")
ACCENT_DARK = HexColor("#8B1F12")
ACCENT = HexColor("#C0392B")
MUTED = HexColor("#7A6E63")
LINE = HexColor("#C9BFB4")
GOLD = HexColor("#B08D3E")
PAPER = HexColor("#FBF7F0")

# ── The 20 words (Book 1, Units 1-13) ─────────────────────────────────────────
WORDS = [
    "friend", "weather", "breakfast", "village", "balance",
    "library", "patient", "nervous", "adventure", "suddenly",
    "challenge", "surprised", "familiar", "foreign", "difference",
    "eventually", "separate", "neighbor", "necessary", "embarrass",
]

W, H = A4
MARGIN = 36.0
BAND_H = 76.0
ROWS = 10
GUTTER = 22.0
BOX_H = 50.0
BADGE_W = 42.0
GRID_BOTTOM = 46.0


def _tracked_string(c, x, y, text, font, size, space):
    """drawString with manual character spacing (canvas has no setCharSpace)."""
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setCharSpace(space)
    t.textOut(text)
    c.drawText(t)


def _fit_font_size(text, font, max_width, start_size):
    size = start_size
    while size > 8 and stringWidth(text, font, size) > max_width:
        size -= 0.5
    return size


def draw_sheet(c, with_key=False):
    # Page background
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    # ── Header band ───────────────────────────────────────────────────────────
    c.setFillColor(ACCENT_DARK)
    c.rect(0, H - BAND_H, W, BAND_H, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.rect(0, H - BAND_H - 3, W, 3, stroke=0, fill=1)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 27)
    c.drawString(MARGIN, H - 38, "SPELLING BEE")

    c.setFillColor(GOLD)
    _tracked_string(
        c, MARGIN, H - 57,
        "LEVEL 1   ·   BOOK 1   ·   UNITS 1-13   ·   20 WORDS",
        "Helvetica-Bold", 9, 1.3,
    )

    # Score box (top right)
    sb_w, sb_h = 116.0, 48.0
    sb_x, sb_y = W - MARGIN - sb_w, H - 62
    c.setFillColor(PAPER)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.roundRect(sb_x, sb_y, sb_w, sb_h, 6, stroke=1, fill=1)

    c.setFillColor(ACCENT_DARK)
    _tracked_string(c, sb_x + 41, sb_y + sb_h - 15, "SCORE", "Helvetica-Bold", 8, 1.6)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 19)
    c.drawCentredString(sb_x + sb_w / 2, sb_y + 10, "____ / 20")

    # ── Name / Class / Date row ───────────────────────────────────────────────
    row_y = H - 106
    rule_y = row_y - 4
    c.setStrokeColor(LINE)
    c.setLineWidth(1.0)

    def field(label, label_x, rule_from, rule_to):
        c.setFillColor(MUTED)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(label_x, row_y, label)
        c.line(rule_from, rule_y, rule_to, rule_y)

    field("Name:", MARGIN, MARGIN + 40, 322)
    field("Class:", 338, 338 + 40, 448)
    field("Date:", 464, 464 + 36, W - MARGIN)

    # ── Instruction line ──────────────────────────────────────────────────────
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Oblique", 9.5)
    c.drawString(
        MARGIN, H - 130,
        "Listen carefully to each word, then write it clearly inside the box."
        if not with_key else
        "TEACHER ANSWER KEY — do not distribute to students.",
    )

    # ── Grid of 20 boxes ──────────────────────────────────────────────────────
    grid_top = H - 144
    pitch = (grid_top - GRID_BOTTOM) / ROWS
    col_w = (W - 2 * MARGIN - GUTTER) / 2

    for i in range(20):
        col, row = divmod(i, ROWS)
        x = MARGIN + col * (col_w + GUTTER)
        y = grid_top - row * pitch - BOX_H

        # Number badge
        c.setFillColor(ACCENT_DARK)
        c.roundRect(x, y, BADGE_W, BOX_H, 6, stroke=0, fill=1)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 21)
        c.drawCentredString(x + BADGE_W / 2, y + BOX_H / 2 - 7.5, str(i + 1))

        # Writing box
        bx = x + BADGE_W + 6
        bw = col_w - BADGE_W - 6
        c.setFillColor(white)
        c.setStrokeColor(LINE)
        c.setLineWidth(1.1)
        c.roundRect(bx, y, bw, BOX_H, 6, stroke=1, fill=1)

        if with_key:
            word = WORDS[i]
            size = _fit_font_size(word, "Helvetica-Bold", bw - 16, 22)
            c.setFillColor(ACCENT)
            c.setFont("Helvetica-Bold", size)
            c.drawCentredString(bx + bw / 2, y + BOX_H / 2 - size * 0.35, word)

    # ── Footer ────────────────────────────────────────────────────────────────
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(MARGIN, 32, W - MARGIN, 32)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, 21, "4000 Essential English Words  ·  Book 1  ·  Units 1-13")


def main():
    with_key = "--key" in sys.argv
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(root, "exports")
    os.makedirs(out_dir, exist_ok=True)
    name = "spelling_bee_level1_answer_key.pdf" if with_key else "spelling_bee_level1_answer_sheet.pdf"
    out = os.path.join(out_dir, name)

    c = canvas.Canvas(out, pagesize=A4)
    c.setTitle("Spelling Bee - Level 1 - Units 1-13")
    draw_sheet(c, with_key=with_key)
    c.showPage()
    c.save()
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
