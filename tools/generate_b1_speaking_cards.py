"""
B1 speaking examination — six printable examiner cards.

Formal front sheet (reused from the written paper) + one full-page card per
topic + a shared marking sheet.  Each card carries its own AI-generated picture
for Part B, produced by tools/generate_speaking_card_images.py.

Usage:
    py tools/generate_b1_speaking_cards.py [--config FILE.json] [--out FILE.pdf]
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

from app.pdf_generator import _draw_image_fitted
from tools.generate_a1_exam import (
    PAGE_W, PAGE_H, MX,
    INK, ACCENT, MUTED, RULE, CARD,
    _register_fonts, _tracked, _fit_size, _footer, _bubble,
)
from tools.generate_b1_final_exam import _cover, _hrule

NAVY = HexColor("#0B3A6F")     # banner + block headers
BADGE = HexColor("#1D59AD")    # level chip inside the banner
TINT_A = HexColor("#EAF2FF")   # interview block
TINT_B = HexColor("#FFF4E8")   # picture block
TINT_C = HexColor("#EEF7EE")   # topic-talk block
GOLD = HexColor("#B8863B")


# ── one topic card ──────────────────────────────────────────────────────────

def _clock(c, cx, cy, r):
    """Vector clock — Segoe UI has no ⏱ glyph, so draw it."""
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.1)
    c.circle(cx, cy, r, stroke=1, fill=0)
    c.setLineWidth(1.0)
    c.line(cx, cy, cx, cy + r * 0.55)          # minute hand
    c.line(cx, cy, cx + r * 0.42, cy - r * 0.3)  # hour hand


def _diamond(c, cx, cy, r, color):
    c.setFillColor(color)
    p = c.beginPath()
    p.moveTo(cx, cy + r)
    p.lineTo(cx + r, cy)
    p.lineTo(cx, cy - r)
    p.lineTo(cx - r, cy)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def _block(c, y, h, tint, letter, title, timing):
    """Coloured rounded block with a lettered chip, title and timing."""
    c.setFillColor(tint)
    c.roundRect(MX, y - h, PAGE_W - 2 * MX, h, 3.5 * mm, stroke=0, fill=1)

    chip = 7 * mm
    c.setFillColor(NAVY)
    c.roundRect(MX + 4 * mm, y - 9.5 * mm, chip, chip, 1.6 * mm, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("UI-Bold", 11)
    c.drawCentredString(MX + 4 * mm + chip / 2, y - 8 * mm, letter)

    c.setFillColor(NAVY)
    c.setFont("UI-Bold", 12)
    c.drawString(MX + 15 * mm, y - 8 * mm, title.upper())
    c.setFillColor(MUTED)
    c.setFont("UI-Semibold", 9.5)
    c.drawRightString(PAGE_W - MX - 5 * mm, y - 8 * mm, timing)


def _bullets(c, x, y, w, lines, size=12, leading=7.6 * mm):
    for line in lines:
        segs = simpleSplit(line, "UI", size, w - 5 * mm)
        for k, seg in enumerate(segs):
            c.setFillColor(ACCENT if k == 0 else INK)
            c.setFont("UI-Bold" if k == 0 else "UI", size)
            if k == 0:
                c.drawString(x, y, "•")
            c.setFillColor(INK)
            c.setFont("UI", size)
            c.drawString(x + 4.5 * mm, y, seg)
            y -= leading
        y -= 0.8 * mm
    return y


def _card_page(c, cfg, card, page):
    # ── running header ──────────────────────────────────────────────────────
    _tracked(c, MX, PAGE_H - 11 * mm, f"SPEAKING EXAMINATION  ·  LEVEL {cfg['level']}",
             "UI-Semibold", 8, MUTED, tracking=1.2, centered=False)
    c.setFont("UI-Semibold", 8)
    c.setFillColor(MUTED)
    c.drawRightString(PAGE_W - MX, PAGE_H - 11 * mm, "20 MARKS")
    _hrule(c, PAGE_H - 13.5 * mm, 0.4)

    # ── banner ──────────────────────────────────────────────────────────────
    by, bh = PAGE_H - 18 * mm, 16 * mm
    c.setFillColor(NAVY)
    c.roundRect(MX, by - bh, PAGE_W - 2 * MX, bh, 3.5 * mm, stroke=0, fill=1)

    title = f"CARD {card['num']}  —  {card['theme'].upper()}"
    size = _fit_size(c, title, "UI-Bold", 19, 13, PAGE_W - 2 * MX - 40 * mm)
    _tracked(c, MX + 8 * mm, by - 10.5 * mm, title, "UI-Bold", size, white,
             tracking=1.6, centered=False)

    badge_w, badge_h = 20 * mm, 8 * mm
    bx = PAGE_W - MX - 8 * mm - badge_w
    c.setFillColor(BADGE)
    c.roundRect(bx, by - 12 * mm, badge_w, badge_h, 2 * mm, stroke=0, fill=1)
    _tracked(c, bx + badge_w / 2, by - 9.6 * mm, f"LEVEL {cfg['level']}",
             "UI-Semibold", 8, white, tracking=1.4)

    # ── teacher-only strip ──────────────────────────────────────────────────
    y = by - bh - 4 * mm
    sh = 8 * mm
    c.setFillColor(CARD)
    c.roundRect(MX, y - sh, PAGE_W - 2 * MX, sh, 2 * mm, stroke=0, fill=1)
    c.setFillColor(MUTED)
    c.setFont("UI-Italic", 9.5)
    c.drawCentredString(PAGE_W / 2, y - 5.4 * mm,
                        "TEACHER ONLY — do not give this page to the student.   "
                        "Total time: 8–10 minutes.")
    y -= sh + 5 * mm

    # ── A · interview ───────────────────────────────────────────────────────
    ha = 15 * mm + len(card["interview"]) * 8.4 * mm
    _block(c, y, ha, TINT_A, "A", "Interview", "2–3 minutes")
    _bullets(c, MX + 9 * mm, y - 17 * mm, PAGE_W - 2 * MX - 14 * mm, card["interview"])
    y -= ha + 6 * mm

    # ── B · picture ─────────────────────────────────────────────────────────
    # the generator returns square images — a square frame avoids white pillars
    img_w = img_h = 68 * mm
    hb = max(15 * mm + len(card["picture"]) * 8.4 * mm, img_h + 16 * mm)
    _block(c, y, hb, TINT_B, "B", "Describe the picture", "2–3 minutes")

    text_w = PAGE_W - 2 * MX - img_w - 20 * mm
    _bullets(c, MX + 9 * mm, y - 17 * mm, text_w, card["picture"])

    img_x = PAGE_W - MX - img_w - 5 * mm
    img_y = y - hb + (hb - img_h) / 2 - 3 * mm
    path = card.get("image")
    if path and os.path.exists(path):
        c.saveState()
        p = c.beginPath()
        p.roundRect(img_x, img_y, img_w, img_h, 2.5 * mm)
        c.clipPath(p, stroke=0, fill=0)
        c.setFillColor(white)
        c.rect(img_x, img_y, img_w, img_h, stroke=0, fill=1)
        _draw_image_fitted(c, path, img_x, img_y, img_w, img_h, padding=0)
        c.restoreState()
    else:
        c.setFillColor(CARD)
        c.roundRect(img_x, img_y, img_w, img_h, 2.5 * mm, stroke=0, fill=1)
        c.setFillColor(MUTED)
        c.setFont("UI-Italic", 9)
        c.drawCentredString(img_x + img_w / 2, img_y + img_h / 2, "[ picture missing ]")
    c.setStrokeColor(RULE)
    c.setLineWidth(0.7)
    c.roundRect(img_x, img_y, img_w, img_h, 2.5 * mm, stroke=1, fill=0)
    y -= hb + 6 * mm

    # ── C · topic talk ──────────────────────────────────────────────────────
    hc = 17 * mm + len(card["topic_points"]) * 8.4 * mm
    _block(c, y, hc, TINT_C, "C", "Topic talk", "3–4 minutes")

    prep_w = 48 * mm
    prep_h = hc - 17 * mm
    px, py = MX + 6 * mm, y - hc + 5 * mm
    c.setFillColor(white)
    c.roundRect(px, py, prep_w, prep_h, 2.5 * mm, stroke=0, fill=1)
    _clock(c, px + prep_w / 2, py + prep_h - 8 * mm, 3.4 * mm)
    c.setFillColor(INK)
    c.setFont("UI", 10)
    for i, line in enumerate(("Give the student ONE minute",
                              "to prepare, then TWO minutes",
                              "to talk.")):
        c.drawCentredString(px + prep_w / 2, py + prep_h - 16 * mm - i * 5.4 * mm, line)

    tx = px + prep_w + 8 * mm
    c.setFillColor(NAVY)
    c.setFont("UI-Bold", 12)
    c.drawString(tx, y - 17 * mm, f"Topic:  {card['topic']}")
    _bullets(c, tx, y - 25 * mm, PAGE_W - MX - tx - 4 * mm, card["topic_points"],
             size=11.5, leading=8 * mm)
    y -= hc + 6 * mm

    # ── follow-up ───────────────────────────────────────────────────────────
    fh = 11 * mm
    c.setFillColor(TINT_A)
    c.roundRect(MX, y - fh, PAGE_W - 2 * MX, fh, 2.5 * mm, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.setFont("UI-Bold", 9.5)
    c.drawString(MX + 5 * mm, y - 7 * mm, "Follow-up:")
    c.setFillColor(INK)
    c.setFont("UI", 10.5)
    c.drawString(MX + 25 * mm, y - 7 * mm, card["followup"])
    y -= fh + 7 * mm

    # ── footer flourish ─────────────────────────────────────────────────────
    mid = PAGE_W / 2
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.line(MX + 20 * mm, y, mid - 40 * mm, y)
    c.line(mid + 49 * mm, y, PAGE_W - MX - 20 * mm, y)
    _tracked(c, mid - 22 * mm, y - 1.2 * mm, "SPEAK CLEARLY", "UI-Semibold", 7.5,
             MUTED, tracking=2)
    _tracked(c, mid + 27 * mm, y - 1.2 * mm, "SPEAK CONFIDENTLY", "UI-Semibold", 7.5,
             MUTED, tracking=2)
    _diamond(c, mid, y + 0.2 * mm, 1.6 * mm, GOLD)

    _footer(c, cfg, page[0])
    c.showPage()
    page[0] += 1


# ── shared marking sheet ────────────────────────────────────────────────────

def _mark_sheet(c, cfg, page):
    _tracked(c, PAGE_W / 2, PAGE_H - 22 * mm, "SPEAKING MARK SHEET", "UI-Bold", 17,
             INK, tracking=3)
    c.setFont("UI", 9.5)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 29 * mm,
                        f"{cfg['exam_id']}  ·  {cfg['instructor']}  —  one row per candidate")
    _hrule(c, PAGE_H - 33 * mm, 1.2, INK)

    y = PAGE_H - 42 * mm
    cols = [("CANDIDATE NAME", 58 * mm), ("CARD", 14 * mm), ("FLU", 15 * mm),
            ("VOC", 15 * mm), ("GRA", 15 * mm), ("PRO", 15 * mm), ("TOTAL", 22 * mm)]
    total_w = sum(w for _, w in cols)
    x0 = (PAGE_W - total_w) / 2

    c.setFillColor(NAVY)
    c.rect(x0, y - 8 * mm, total_w, 8 * mm, stroke=0, fill=1)
    cx = x0
    for label, w in cols:
        _tracked(c, cx + w / 2, y - 5.4 * mm, label, "UI-Semibold", 7.5, white, tracking=1.2)
        cx += w

    rh = 9.5 * mm
    rows = 16
    for r in range(rows):
        ry = y - 8 * mm - (r + 1) * rh
        if r % 2:
            c.setFillColor(HexColor("#F7F9FC"))
            c.rect(x0, ry, total_w, rh, stroke=0, fill=1)
        _hrule(c, ry, 0.4, RULE, x0, x0 + total_w)
    cx = x0
    for _, w in cols:
        c.setStrokeColor(RULE)
        c.setLineWidth(0.4)
        c.line(cx, y - 8 * mm - rows * rh, cx, y - 8 * mm)
        cx += w
    c.line(x0 + total_w, y - 8 * mm - rows * rh, x0 + total_w, y - 8 * mm)

    y = y - 8 * mm - rows * rh - 12 * mm
    _tracked(c, MX, y, "BAND DESCRIPTORS  —  SCORE EACH COLUMN 1 TO 5",
             "UI-Semibold", 8, ACCENT, tracking=2, centered=False)
    y -= 7 * mm
    for label, text in (
        ("FLU  Fluency", "5 speaks smoothly with little hesitation  ·  3 hesitates but keeps going  ·  1 needs constant prompting"),
        ("VOC  Vocabulary", "5 wide, precise range  ·  3 adequate for familiar topics  ·  1 very limited, repeats words"),
        ("GRA  Grammar", "5 accurate, varied structures  ·  3 simple forms mostly correct  ·  1 frequent basic errors"),
        ("PRO  Pronunciation", "5 clear and easy to follow  ·  3 understandable with effort  ·  1 often hard to understand"),
    ):
        c.setFillColor(NAVY)
        c.setFont("UI-Bold", 9.5)
        c.drawString(MX, y, label)
        c.setFillColor(INK)
        c.setFont("UI", 9.5)
        c.drawString(MX + 34 * mm, y, text)
        y -= 6.6 * mm

    _footer(c, cfg, page[0])


# ── main ────────────────────────────────────────────────────────────────────

def _render(cfg, total_pages):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"{cfg['title']} {cfg['exam_id']} — {cfg['instructor']}")

    speaking_marks = sum(m for _, m in (("A", 5), ("B", 5), ("C", 10)))
    parts = [{"kind": "speaking", "roman": "Part A-C", "blocks": [
        {"title": "A · Interview", "marks": 5},
        {"title": "B · Picture", "marks": 5},
        {"title": "C · Topic talk", "marks": 10},
    ]}]
    _cover(c, cfg, 0, speaking_marks, parts, total_pages)
    c.showPage()

    page = [2]
    for card in cfg["cards"]:
        _card_page(c, cfg, card, page)
    _mark_sheet(c, cfg, page)

    c.save()
    return buf.getvalue(), page[0]


def generate(cfg_path: str) -> bytes:
    _register_fonts()
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)
    _, pages = _render(cfg, None)      # pass 1 counts, pass 2 prints the count
    pdf, _ = _render(cfg, pages)
    return pdf


def main():
    args = sys.argv[1:]
    cfg_path = "tools/exam_b1_speaking_cards.json"
    out_path = "exports/Final_Exam_B1_Speaking_Cards.pdf"
    if "--config" in args:
        cfg_path = args[args.index("--config") + 1]
    if "--out" in args:
        out_path = args[args.index("--out") + 1]
    pdf = generate(cfg_path)
    with open(out_path, "wb") as f:
        f.write(pdf)
    print(f"Saved: {out_path}  ({len(pdf) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
