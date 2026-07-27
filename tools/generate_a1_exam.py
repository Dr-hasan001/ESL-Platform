"""
Modern A1 all-MCQ exam renderer — big, clear Segoe UI type (the Windows
equivalent of the Apple system font stack), generous white space, and a
machine-markable bubble answer sheet.

Reads a 5-part JSON config (tools/exam_a1_u6-10_mcq.json):
    cover · picture MCQ · definition MCQ · grammar MCQ · plural MCQ
    · story with T/F · bubble ANSWER SHEET · teacher answer key.

Bubble sheet keeps the same OMR conventions as the B1 sheets (4 solid
corner markers, numbered rows) so the photograph-and-mark workflow is
identical; rows listed in cfg["tf_rows"] show only T / F bubbles.

Usage:
    py tools/generate_a1_exam.py [--config FILE.json] [--out FILE.pdf]
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT

from app.database import SessionLocal
from app.models.book import Word
from app.pdf_generator import _resolve_image_path, _draw_image_fitted
from tools.generate_vocab_exam import _cover_image_reader

PAGE_W, PAGE_H = A4
MX = 16 * mm

INK = HexColor("#1D1D1F")      # near-black, Apple-style
ACCENT = HexColor("#0071E3")   # system blue
MUTED = HexColor("#6E6E73")
RULE = HexColor("#D9D9DE")
CARD = HexColor("#F5F5F7")
TINT = HexColor("#EAF2FF")
GHOST = HexColor("#B8B8BF")    # letters inside bubbles


# ── fonts ───────────────────────────────────────────────────────────────────

_FONT_FILES = {
    "UI": "segoeui.ttf",
    "UI-Bold": "segoeuib.ttf",
    "UI-Semibold": "seguisb.ttf",
    "UI-Light": "segoeuil.ttf",
    "UI-Italic": "segoeuii.ttf",
}


def _register_fonts():
    fdir = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
    for name, fn in _FONT_FILES.items():
        pdfmetrics.registerFont(TTFont(name, os.path.join(fdir, fn)))
    pdfmetrics.registerFontFamily("UI", normal="UI", bold="UI-Bold", italic="UI-Italic")


def _tracked(c, x, y, text, font, size, color, tracking=2.5, centered=True):
    w = c.stringWidth(text, font, size) + tracking * max(0, len(text) - 1)
    t = c.beginText()
    t.setFont(font, size)
    t.setFillColor(color)
    t.setCharSpace(tracking)
    t.setTextOrigin(x - w / 2 if centered else x, y)
    t.textOut(text)
    t.setCharSpace(0)   # Tc persists past the text object — reset or it leaks
    c.drawText(t)


def _fit_size(c, text, font, max_size, min_size, max_w):
    s = max_size
    while s > min_size and c.stringWidth(text, font, s) > max_w:
        s -= 0.5
    return s


# ── page furniture ──────────────────────────────────────────────────────────

def _running_header(c, cfg):
    _tracked(c, MX, PAGE_H - 11 * mm, f"{cfg['title'].upper()}  ·  LEVEL {cfg['level']}",
             "UI-Semibold", 8, MUTED, tracking=1.2, centered=False)
    c.setFont("UI-Semibold", 8)
    c.setFillColor(MUTED)
    c.drawRightString(PAGE_W - MX, PAGE_H - 11 * mm, cfg["instructor"].upper())
    c.setStrokeColor(RULE)
    c.setLineWidth(0.4)
    c.line(MX, PAGE_H - 13.5 * mm, PAGE_W - MX, PAGE_H - 13.5 * mm)


def _footer(c, cfg, page):
    c.setFont("UI", 8)
    c.setFillColor(MUTED)
    c.drawString(MX, 10 * mm, cfg["exam_id"])
    c.drawCentredString(PAGE_W / 2, 10 * mm, str(page))
    c.drawRightString(PAGE_W - MX, 10 * mm, cfg["instructor"])


def _section(c, cfg, part, marks):
    _running_header(c, cfg)
    y = PAGE_H - 25 * mm
    chip = part["roman"].upper()
    tw = c.stringWidth(chip, "UI-Semibold", 10.5)
    ch_w = tw + 8 * mm
    c.setFillColor(TINT)
    c.roundRect(MX, y - 2.6 * mm, ch_w, 8.6 * mm, 2.8 * mm, stroke=0, fill=1)
    c.setFillColor(ACCENT)
    c.setFont("UI-Semibold", 10.5)
    c.drawCentredString(MX + ch_w / 2, y, chip)

    label_x = MX + ch_w + 5 * mm
    label_w = PAGE_W - MX - label_x - 26 * mm
    size = _fit_size(c, part["label"], "UI-Semibold", 16, 12, label_w)
    c.setFillColor(INK)
    c.setFont("UI-Semibold", size)
    c.drawString(label_x, y, part["label"])

    c.setFillColor(ACCENT)
    c.setFont("UI-Semibold", 10)
    c.drawRightString(PAGE_W - MX, y, f"{marks} MARKS")

    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.line(MX, y - 6 * mm, PAGE_W - MX, y - 6 * mm)
    if part.get("hint"):
        c.setFillColor(MUTED)
        c.setFont("UI", 10.5)
        c.drawString(MX, y - 12 * mm, part["hint"])
        return y - 19 * mm
    return y - 12 * mm


def _bubble_option(c, x, y, letter, text, size=12):
    r = 2.6 * mm
    c.setStrokeColor(INK)
    c.setLineWidth(0.6)
    c.circle(x + r, y + 1.3 * mm, r, stroke=1, fill=0)
    c.setFont("UI-Semibold", 9)
    c.setFillColor(INK)
    c.drawCentredString(x + r, y - 0.4 * mm, letter)
    c.setFont("UI", size)
    c.drawString(x + 2 * r + 2.5 * mm, y, text)


# ── Part: picture MCQ, 2 cols x 3 rows ──────────────────────────────────────

P1_COLS, P1_ROWS = 2, 3
P1_W = (PAGE_W - 2 * MX) / P1_COLS
P1_H = 79 * mm


def _picture_cell(c, x, y, item, img_path):
    inner_x = x + 5 * mm
    inner_w = P1_W - 10 * mm

    c.setFillColor(ACCENT)
    c.setFont("UI-Semibold", 14)
    c.drawString(inner_x, y + P1_H - 8 * mm, f"{item['num']}.")

    img_h = 47 * mm
    img_w = inner_w
    img_x = inner_x
    img_y = y + P1_H - 10 * mm - img_h
    c.saveState()
    p = c.beginPath()
    p.roundRect(img_x, img_y, img_w, img_h, 3 * mm)
    c.clipPath(p, stroke=0, fill=0)
    c.setFillColor(white)
    c.rect(img_x, img_y, img_w, img_h, stroke=0, fill=1)
    if img_path:
        _draw_image_fitted(c, img_path, img_x, img_y, img_w, img_h, padding=0)
    c.restoreState()
    c.setStrokeColor(RULE)
    c.setLineWidth(0.7)
    c.roundRect(img_x, img_y, img_w, img_h, 3 * mm, stroke=1, fill=0)

    opts_y = img_y - 8.5 * mm
    col_w = inner_w / 2
    for i, opt in enumerate(item["options"]):
        row, col = i // 2, i % 2
        _bubble_option(c, inner_x + col * col_w, opts_y - row * 8 * mm, "abcd"[i], opt, size=12)


def _picture_part(c, cfg, part, db, page):
    top = _section(c, cfg, part, len(part["items"]))
    on_page = 0
    for item in part["items"]:
        if on_page >= P1_COLS * P1_ROWS:
            _footer(c, cfg, page[0]); c.showPage(); page[0] += 1
            top = _section(c, cfg, {"roman": part["roman"], "label": "(continued)"}, len(part["items"]))
            on_page = 0
        row, col = on_page // P1_COLS, on_page % P1_COLS
        x = MX + col * P1_W
        y = top - (row + 1) * P1_H
        w = db.query(Word).filter(Word.word == item["word"]).first()
        img_path = _resolve_image_path(w.image_url) if w else None
        _picture_cell(c, x, y, item, img_path)
        on_page += 1
    _footer(c, cfg, page[0]); c.showPage(); page[0] += 1


# ── Part: text MCQ (adaptive option layout) ─────────────────────────────────

def _mcq_part(c, cfg, part, page):
    y = _section(c, cfg, part, len(part["items"]))
    y -= 3 * mm
    avail_w = PAGE_W - 2 * MX - 10 * mm

    for item in part["items"]:
        lines = simpleSplit(item["sentence"], "UI-Semibold", 13, avail_w)
        longest = max(c.stringWidth(o, "UI", 12) for o in item["options"])
        grid = longest <= min(avail_w / 2 - 16 * mm, 55 * mm)
        opts_h = 2 * 8.5 * mm if grid else 4 * 8 * mm
        block_h = len(lines) * 6.5 * mm + 3.5 * mm + opts_h + 8 * mm
        if y - block_h < 16 * mm:
            _footer(c, cfg, page[0]); c.showPage(); page[0] += 1
            y = _section(c, cfg, {"roman": part["roman"], "label": "(continued)"}, len(part["items"]))
            y -= 3 * mm

        c.setFillColor(ACCENT)
        c.setFont("UI-Semibold", 13)
        c.drawString(MX, y, f"{item['num']}.")
        c.setFillColor(INK)
        for i, line in enumerate(lines):
            c.drawString(MX + 10 * mm, y - i * 6.5 * mm, line)
        y -= (len(lines) - 1) * 6.5 * mm + 9 * mm

        if grid:
            col_w = (PAGE_W - 2 * MX - 10 * mm) / 2
            for i, opt in enumerate(item["options"]):
                row, col = i // 2, i % 2
                _bubble_option(c, MX + 10 * mm + col * col_w, y - row * 8.5 * mm, "abcd"[i], opt)
            y -= 2 * 8.5 * mm
        else:
            for i, opt in enumerate(item["options"]):
                _bubble_option(c, MX + 10 * mm, y - i * 8 * mm, "abcd"[i], opt)
            y -= 4 * 8 * mm
        y -= 4.5 * mm

    _footer(c, cfg, page[0]); c.showPage(); page[0] += 1


# ── Part: story + T/F ───────────────────────────────────────────────────────

def _story_part(c, cfg, part, page):
    y = _section(c, cfg, part, len(part["statements"]))

    style = ParagraphStyle(name="story", fontName="UI", fontSize=13.5,
                           leading=21, textColor=INK, alignment=TA_LEFT)
    pad = 8 * mm
    box_w = PAGE_W - 2 * MX
    para = Paragraph(part["story"], style)
    _, ph = para.wrap(box_w - 2 * pad, 999)
    title_h = 11 * mm
    box_h = ph + 2 * pad + title_h
    box_top = y - 2 * mm
    box_bot = box_top - box_h

    c.setFillColor(CARD)
    c.roundRect(MX, box_bot, box_w, box_h, 4 * mm, stroke=0, fill=1)
    c.setFont("UI-Semibold", 15)
    c.setFillColor(ACCENT)
    c.drawCentredString(PAGE_W / 2, box_top - pad - 3.5 * mm, part["story_title"])
    para.drawOn(c, MX + pad, box_bot + pad)

    y = box_bot - 13 * mm
    for s in part["statements"]:
        c.setFillColor(ACCENT)
        c.setFont("UI-Semibold", 13)
        c.drawString(MX, y, f"{s['num']}.")
        c.setFillColor(INK)
        c.setFont("UI", 13)
        c.drawString(MX + 10 * mm, y, s["text"])
        c.setFont("UI-Semibold", 11)
        c.setFillColor(MUTED)
        c.drawRightString(PAGE_W - MX, y, "T  /  F")
        y -= 11.5 * mm

    _footer(c, cfg, page[0]); c.showPage(); page[0] += 1


# ── cover ───────────────────────────────────────────────────────────────────

def _cover(c, cfg, total_marks, n_parts):
    c.setFillColor(white)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    _tracked(c, PAGE_W / 2, PAGE_H - 26 * mm, cfg["eyebrow"], "UI-Semibold", 9, MUTED, tracking=3)

    c.setFillColor(ACCENT)
    c.roundRect(PAGE_W / 2 - 9 * mm, PAGE_H - 33.5 * mm, 18 * mm, 1.4 * mm, 0.7 * mm, stroke=0, fill=1)

    c.setFont("UI-Semibold", 76)
    c.setFillColor(INK)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 64 * mm, cfg["title"])

    c.setFont("UI", 14)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 75 * mm, cfg["subtitle"])

    # hero image in rounded card
    panel_w, panel_h = 152 * mm, 80 * mm
    panel_x = (PAGE_W - panel_w) / 2
    panel_top = PAGE_H - 86 * mm
    panel_y = panel_top - panel_h
    reader = _cover_image_reader(cfg.get("cover_image"), panel_w / panel_h)
    if reader:
        c.saveState()
        p = c.beginPath()
        p.roundRect(panel_x, panel_y, panel_w, panel_h, 5 * mm)
        c.clipPath(p, stroke=0, fill=0)
        c.drawImage(reader, panel_x, panel_y, width=panel_w, height=panel_h, mask="auto")
        c.restoreState()
    c.setStrokeColor(RULE)
    c.setLineWidth(0.8)
    c.roundRect(panel_x, panel_y, panel_w, panel_h, 5 * mm, stroke=1, fill=0)

    # info pills
    pills = [f"LEVEL {cfg['level']}", cfg["time_allowed"].upper(),
             f"{n_parts} PARTS", f"{total_marks} MARKS"]
    pill_h, gap = 9.5 * mm, 4 * mm
    widths = [c.stringWidth(t, "UI-Semibold", 9.5) + 10 * mm for t in pills]
    row_w = sum(widths) + gap * (len(pills) - 1)
    px = (PAGE_W - row_w) / 2
    py = panel_y - 19 * mm
    for t, w in zip(pills, widths):
        c.setFillColor(CARD)
        c.roundRect(px, py, w, pill_h, pill_h / 2, stroke=0, fill=1)
        c.setFillColor(INK)
        c.setFont("UI-Semibold", 9.5)
        c.drawCentredString(px + w / 2, py + 3.2 * mm, t)
        px += w + gap

    # instructor
    _tracked(c, PAGE_W / 2, py - 14 * mm, "INSTRUCTOR", "UI-Semibold", 8, MUTED, tracking=3)
    c.setFont("UI-Semibold", 20)
    c.setFillColor(INK)
    c.drawCentredString(PAGE_W / 2, py - 22.5 * mm, cfg["instructor"])

    # name / date
    by = py - 40 * mm
    bx, bw = 30 * mm, PAGE_W - 60 * mm
    c.setFont("UI-Semibold", 10)
    c.setFillColor(INK)
    c.drawString(bx, by, "NAME")
    c.setStrokeColor(RULE)
    c.setLineWidth(0.8)
    c.line(bx + 16 * mm, by - 0.5, bx + bw * 0.55, by - 0.5)
    c.drawString(bx + bw * 0.62, by, "DATE")
    c.line(bx + bw * 0.62 + 14 * mm, by - 0.5, bx + bw, by - 0.5)

    # score chip — bottom right
    sw, sh = 40 * mm, 18 * mm
    sx, sy = PAGE_W - MX - sw, 16 * mm
    c.setFillColor(CARD)
    c.roundRect(sx, sy, sw, sh, 4 * mm, stroke=0, fill=1)
    _tracked(c, sx + sw / 2, sy + sh - 6 * mm, "SCORE", "UI-Semibold", 7.5, MUTED, tracking=2.5)
    c.setFont("UI-Semibold", 17)
    c.setFillColor(INK)
    c.drawCentredString(sx + sw / 2, sy + 4 * mm, f"/  {total_marks}")

    c.setFont("UI", 8)
    c.setFillColor(MUTED)
    c.drawString(MX, 10 * mm, cfg["exam_id"])


# ── bubble answer sheet ─────────────────────────────────────────────────────

BUBBLE_R = 3.2 * mm
ROW_H = 11 * mm
GRID_TOP = PAGE_H - 66 * mm
COL_X = (34 * mm, 122 * mm)   # x of question-number right edge per column
BUBBLE_DX = 11 * mm
BUBBLE_X0 = 8 * mm


def _corner_markers(c):
    s = 8 * mm
    c.setFillColor(black)
    for x, y in ((12 * mm, PAGE_H - 12 * mm - s), (PAGE_W - 12 * mm - s, PAGE_H - 12 * mm - s),
                 (12 * mm, 12 * mm), (PAGE_W - 12 * mm - s, 12 * mm)):
        c.rect(x, y, s, s, stroke=0, fill=1)


def _bubble(c, cx, cy, label, r=BUBBLE_R):
    c.setStrokeColor(INK)
    c.setLineWidth(0.7)
    c.circle(cx, cy, r, stroke=1, fill=0)
    c.setFont("UI-Semibold", 7.5)
    c.setFillColor(GHOST)
    c.drawCentredString(cx, cy - 2.5, label)
    c.setFillColor(INK)


def _bubble_sheet(c, cfg, total_q, page):
    tf_rows = set(cfg.get("tf_rows", []))
    _corner_markers(c)

    _tracked(c, PAGE_W / 2, PAGE_H - 23 * mm, "ANSWER SHEET", "UI-Bold", 19, INK, tracking=3)
    c.setFont("UI", 8.5)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 29 * mm,
                        f"{cfg['title'].upper()}  ·  {cfg['exam_id']}  ·  {cfg['instructor'].upper()}  ·  LEVEL {cfg['level']}")

    by = PAGE_H - 40 * mm
    c.setFont("UI-Semibold", 9.5)
    c.setFillColor(INK)
    c.drawString(28 * mm, by, "NAME")
    c.setStrokeColor(INK)
    c.setLineWidth(0.6)
    c.line(42 * mm, by - 0.5, 120 * mm, by - 0.5)
    c.drawString(128 * mm, by, "DATE")
    c.line(140 * mm, by - 0.5, PAGE_W - 28 * mm, by - 0.5)

    iy = PAGE_H - 49 * mm
    c.setFont("UI", 9)
    c.setFillColor(INK)
    lead = "Fill ONE bubble completely with a dark pen or pencil.   Correct:"
    c.drawString(28 * mm, iy, lead)
    ex_x = 28 * mm + c.stringWidth(lead, "UI", 9) + 5 * mm
    c.setFillColor(black)
    c.circle(ex_x, iy + 1.1 * mm, 2.4 * mm, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont("UI", 9)
    c.drawString(ex_x + 6 * mm, iy, "Wrong:")
    _bubble(c, ex_x + 20 * mm, iy + 1.1 * mm, "", r=2.4 * mm)
    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    c.line(ex_x + 18.5 * mm, iy - 0.4 * mm, ex_x + 21.5 * mm, iy + 2.6 * mm)

    rows_per_col = (total_q + 1) // 2
    for col in range(2):
        x_num = COL_X[col]
        for row in range(rows_per_col):
            q = col * rows_per_col + row + 1
            if q > total_q:
                break
            cy = GRID_TOP - row * ROW_H
            if row % 5 == 0 and row > 0:
                c.setStrokeColor(RULE)
                c.setLineWidth(0.3)
                c.line(x_num - 8 * mm, cy + ROW_H / 2 + 1.2 * mm,
                       x_num + BUBBLE_X0 + 3.6 * BUBBLE_DX, cy + ROW_H / 2 + 1.2 * mm)
            c.setFont("UI-Semibold", 10.5)
            c.setFillColor(INK)
            c.drawRightString(x_num, cy - 1.2 * mm, str(q))
            if q in tf_rows:
                _bubble(c, x_num + BUBBLE_X0, cy, "T")
                _bubble(c, x_num + BUBBLE_X0 + BUBBLE_DX, cy, "F")
            else:
                for k in range(4):
                    _bubble(c, x_num + BUBBLE_X0 + k * BUBBLE_DX, cy, "abcd"[k])

    c.setFillColor(CARD)
    c.roundRect(PAGE_W / 2 - 24 * mm, 14.5 * mm, 48 * mm, 10 * mm, 3 * mm, stroke=0, fill=1)
    _tracked(c, PAGE_W / 2, 21 * mm, "TEACHER ONLY", "UI-Semibold", 6.5, MUTED, tracking=2)
    c.setFont("UI-Semibold", 11)
    c.setFillColor(INK)
    c.drawCentredString(PAGE_W / 2, 16.3 * mm, f"SCORE            /  {total_q}")

    # no footer here — text near the corner markers can confuse OMR alignment
    c.showPage(); page[0] += 1


# ── answer key ──────────────────────────────────────────────────────────────

def _answer_key(c, cfg, page):
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1)
    c.line(MX, PAGE_H - 14 * mm, PAGE_W - MX, PAGE_H - 14 * mm)
    _tracked(c, PAGE_W / 2, PAGE_H - 23 * mm, "TEACHER ANSWER KEY", "UI-Bold", 15, ACCENT, tracking=2)
    c.setFont("UI", 10)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 29.5 * mm,
                        f"{cfg['exam_id']} — detach before handing out.")

    y = PAGE_H - 40 * mm
    for part in cfg["parts"]:
        items = part.get("items") or part["statements"]
        nums = f"({items[0]['num']}–{items[-1]['num']})"
        c.setFont("UI-Semibold", 12)
        c.setFillColor(INK)
        c.drawString(MX, y, f"{part['roman']} — {part['label']}  {nums}")
        c.setStrokeColor(RULE)
        c.setLineWidth(0.3)
        c.line(MX, y - 2.5 * mm, PAGE_W - MX, y - 2.5 * mm)
        y -= 9 * mm
        c.setFont("UI", 10.5)
        c.setFillColor(INK)
        for i, it in enumerate(items):
            col, row = i % 5, i // 5
            if part["kind"] == "story":
                txt = f"{it['num']}.  {'T' if it['answer'] else 'F'}"
            elif part["kind"] == "picture":
                txt = f"{it['num']}.  {it['answer']})  {it['options']['abcd'.index(it['answer'])]}"
            else:
                txt = f"{it['num']}.  {it['answer']})"
            c.drawString(MX + col * 35 * mm, y - row * 6.5 * mm, txt)
        y -= ((len(items) + 4) // 5) * 6.5 * mm + 9 * mm

    _footer(c, cfg, page[0])


# ── main ────────────────────────────────────────────────────────────────────

def generate(cfg_path: str) -> bytes:
    _register_fonts()
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)
    parts = cfg["parts"]
    total = sum(len(p.get("items") or p["statements"]) for p in parts)

    db = SessionLocal()
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"{cfg['title']} {cfg['exam_id']} — {cfg['instructor']}")

    _cover(c, cfg, total, len(parts))
    c.showPage()

    page = [2]
    for part in parts:
        if part["kind"] == "picture":
            _picture_part(c, cfg, part, db, page)
        elif part["kind"] == "story":
            _story_part(c, cfg, part, page)
        else:
            _mcq_part(c, cfg, part, page)
    _bubble_sheet(c, cfg, total, page)
    _answer_key(c, cfg, page)

    db.close()
    c.save()
    return buf.getvalue()


def main():
    args = sys.argv[1:]
    cfg_path = "tools/exam_a1_u6-10_mcq.json"
    out_path = "exports/Exam_A1_U6-10_MCQ.pdf"
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
