"""
All-MCQ B1 exam renderer with machine-markable bubble answer sheet.

Reads content from a JSON config (default: tools/exam_b3_u6-10_mcq.json):
    cover · Part I picture MCQ (1-10) · Part II sentence MCQ (11-20)
    · Part III story T/F (21-30) · Part IV grammar MCQ (31-40)
    · bubble ANSWER SHEET (print one per student) · teacher answer key.

Bubble sheet: 4 solid corner markers for photo alignment, 2 columns x 20
rows; rows 21-30 show only T / F bubbles. Teacher photographs filled
sheets after the exam for fast marking.

Usage:
    py tools/generate_mcq_exam.py [--config FILE.json] [--out FILE.pdf]
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY

from app.database import SessionLocal
from tools.generate_vocab_exam import (
    _cover, _running_header, _section_title, _footer,
    _part1,
    INK, ACCENT, MUTED, RULE, BANK_BG, BANK_BORDER, GOLD,
)

PAGE_W, PAGE_H = A4
MX = 15 * mm


# ── Parts II & IV: text MCQ ─────────────────────────────────────────────────

def _mcq_text_part(c, cfg, part_key, roman, page):
    p = cfg[part_key]
    _running_header(c, cfg)
    y = _section_title(c, PAGE_H - 20 * mm, roman, p["label"], p["hint"], marks=10)
    y -= 2 * mm

    for item in p["items"]:
        lines = simpleSplit(item["sentence"], "Times-Roman", 11, PAGE_W - 2 * MX - 10 * mm)
        block_h = len(lines) * 5 * mm + 2.5 * mm + 11 * mm + 4.5 * mm
        if y - block_h < 16 * mm:
            _footer(c, page[0]); c.showPage(); page[0] += 1
            _running_header(c, cfg)
            y = _section_title(c, PAGE_H - 20 * mm, roman, "(continued)")
            y -= 2 * mm

        c.setFont("Times-Bold", 11)
        c.setFillColor(ACCENT)
        c.drawString(MX, y, f"{item['num']}.")
        c.setFont("Times-Roman", 11)
        c.setFillColor(INK)
        for i, line in enumerate(lines):
            c.drawString(MX + 9 * mm, y - i * 5 * mm, line)
        y -= len(lines) * 5 * mm + 2.5 * mm

        col_w = (PAGE_W - 2 * MX - 9 * mm) / 2
        for i, opt in enumerate(item["options"]):
            row, col = i // 2, i % 2
            ox = MX + 9 * mm + col * col_w
            oy = y - row * 5.5 * mm
            c.setStrokeColor(INK)
            c.setLineWidth(0.5)
            c.circle(ox + 2.2 * mm, oy + 1.1 * mm, 2.2 * mm, stroke=1, fill=0)
            c.setFont("Times-Bold", 8.5)
            c.setFillColor(INK)
            c.drawCentredString(ox + 2.2 * mm, oy - 0.4 * mm, "abcd"[i])
            c.setFont("Helvetica", 9.5)
            c.drawString(ox + 6.5 * mm, oy, opt)
        y -= 11 * mm + 4.5 * mm

    _footer(c, page[0]); c.showPage(); page[0] += 1


# ── Part III: story + T/F (answers go on the sheet — no circles here) ───────

def _part3_story(c, cfg, page):
    p3 = cfg["part3"]
    _running_header(c, cfg)
    y = _section_title(c, PAGE_H - 20 * mm, "Part III", p3["label"], p3["hint"], marks=10)

    style = ParagraphStyle(name="story", fontName="Times-Roman", fontSize=11.5,
                           leading=16.5, textColor=INK, alignment=TA_JUSTIFY)
    pad = 6 * mm
    box_w = PAGE_W - 2 * MX
    para = Paragraph(p3["story"], style)
    _, ph = para.wrap(box_w - 2 * pad, 999)
    title_h = 9 * mm
    box_h = ph + 2 * pad + title_h
    box_top = y - 1 * mm
    box_bot = box_top - box_h

    c.setFillColor(BANK_BG)
    c.setStrokeColor(BANK_BORDER)
    c.setLineWidth(0.8)
    c.roundRect(MX, box_bot, box_w, box_h, 4 * mm, stroke=1, fill=1)
    c.setFont("Times-Bold", 13)
    c.setFillColor(ACCENT)
    c.drawCentredString(PAGE_W / 2, box_top - pad - 3 * mm, p3["story_title"])
    para.drawOn(c, MX + pad, box_bot + pad)

    y = box_bot - 9 * mm
    for s in p3["statements"]:
        c.setFont("Times-Bold", 11)
        c.setFillColor(ACCENT)
        c.drawString(MX, y, f"{s['num']}.")
        c.setFont("Times-Roman", 11.5)
        c.setFillColor(INK)
        lines = simpleSplit(s["text"], "Times-Roman", 11.5, PAGE_W - 2 * MX - 30 * mm)
        for i, line in enumerate(lines):
            c.drawString(MX + 9 * mm, y - i * 5 * mm, line)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(MUTED)
        c.drawRightString(PAGE_W - MX, y, "T  /  F")
        y -= max(1, len(lines)) * 5 * mm + 5.2 * mm
    _footer(c, page[0]); c.showPage(); page[0] += 1


# ── Bubble answer sheet ─────────────────────────────────────────────────────

BUBBLE_R = 3.2 * mm
ROW_H = 10.2 * mm
GRID_TOP = PAGE_H - 62 * mm
COL_X = (32 * mm, 120 * mm)   # x of question-number right edge per column
BUBBLE_DX = 11 * mm           # spacing between bubble centers
BUBBLE_X0 = 8 * mm            # first bubble center offset from number edge


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
    c.setFont("Helvetica", 7.5)
    c.setFillColor(HexColor("#B5AB9E"))
    c.drawCentredString(cx, cy - 2.5, label)
    c.setFillColor(INK)


def _bubble_sheet(c, cfg, page):
    _corner_markers(c)

    c.setFont("Times-Bold", 19)
    c.setFillColor(INK)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 22 * mm, "ANSWER  SHEET")
    c.setFont("Helvetica", 8.5)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 27.5 * mm,
                        f"{cfg['title'].upper()}  ·  {cfg['exam_id']}  ·  {cfg['instructor'].upper()}  ·  LEVEL {cfg['level']}")

    # name / date
    by = PAGE_H - 38 * mm
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(INK)
    c.drawString(28 * mm, by, "NAME")
    c.setStrokeColor(INK)
    c.setLineWidth(0.6)
    c.line(42 * mm, by - 0.5, 120 * mm, by - 0.5)
    c.drawString(128 * mm, by, "DATE")
    c.line(140 * mm, by - 0.5, PAGE_W - 28 * mm, by - 0.5)

    # instructions with example bubbles
    iy = PAGE_H - 47 * mm
    c.setFont("Helvetica", 8.5)
    c.setFillColor(INK)
    c.drawString(28 * mm, iy, "Fill ONE bubble completely with a dark pen or pencil.   Correct:")
    ex_x = 28 * mm + c.stringWidth("Fill ONE bubble completely with a dark pen or pencil.   Correct:", "Helvetica", 8.5) + 5 * mm
    c.setFillColor(black)
    c.circle(ex_x, iy + 1.1 * mm, 2.4 * mm, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont("Helvetica", 8.5)
    c.drawString(ex_x + 6 * mm, iy, "Wrong:")
    _bubble(c, ex_x + 20 * mm, iy + 1.1 * mm, "", r=2.4 * mm)
    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    c.line(ex_x + 18.5 * mm, iy - 0.4 * mm, ex_x + 21.5 * mm, iy + 2.6 * mm)   # slash through

    # grid — 2 columns of 20 rows
    for col in range(2):
        x_num = COL_X[col]
        for row in range(20):
            q = col * 20 + row + 1
            cy = GRID_TOP - row * ROW_H
            if row % 5 == 0 and row > 0:
                c.setStrokeColor(RULE)
                c.setLineWidth(0.3)
                c.line(x_num - 8 * mm, cy + ROW_H / 2 + 1.2 * mm,
                       x_num + BUBBLE_X0 + 3.6 * BUBBLE_DX, cy + ROW_H / 2 + 1.2 * mm)
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(INK)
            c.drawRightString(x_num, cy - 1.2 * mm, str(q))
            if 21 <= q <= 30:
                _bubble(c, x_num + BUBBLE_X0, cy, "T")
                _bubble(c, x_num + BUBBLE_X0 + BUBBLE_DX, cy, "F")
            else:
                for k in range(4):
                    _bubble(c, x_num + BUBBLE_X0 + k * BUBBLE_DX, cy, "abcd"[k])

    # teacher score box
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.9)
    c.rect(PAGE_W / 2 - 22 * mm, 15 * mm, 44 * mm, 9 * mm, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, 20.5 * mm, "T E A C H E R   O N L Y")
    c.setFont("Times-Bold", 11)
    c.setFillColor(INK)
    c.drawCentredString(PAGE_W / 2, 16.8 * mm, "SCORE            /  40")

    _footer(c, page[0]); c.showPage(); page[0] += 1


# ── Answer key ──────────────────────────────────────────────────────────────

def _answer_key(c, cfg, page):
    c.setStrokeColor(ACCENT)
    c.setLineWidth(0.9)
    c.line(MX, PAGE_H - 14 * mm, PAGE_W - MX, PAGE_H - 14 * mm)
    c.setFont("Times-Bold", 16)
    c.setFillColor(ACCENT)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 22 * mm, "TEACHER ANSWER KEY")
    c.setFont("Times-Italic", 10.5)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 28 * mm,
                        f"{cfg['exam_id']} — detach before handing out.")

    y = PAGE_H - 38 * mm

    def head(label, yy):
        c.setFont("Times-Bold", 12)
        c.setFillColor(INK)
        c.drawString(MX, yy, label)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.3)
        c.line(MX, yy - 2 * mm, PAGE_W - MX, yy - 2 * mm)
        return yy - 7 * mm

    def grid(items, yy, fmt):
        c.setFont("Helvetica", 10)
        c.setFillColor(INK)
        for i, it in enumerate(items):
            col, row = i % 5, i // 5
            c.drawString(MX + col * 36 * mm, yy - row * 6 * mm, fmt(it))
        return yy - ((len(items) + 4) // 5) * 6 * mm - 8 * mm

    y = head("Part I — Picture MCQ (1–10)", y)
    y = grid(cfg["part1"]["items"], y,
             lambda it: f"{it['num']}.  {it['answer']})  {it['options']['abcd'.index(it['answer'])]}")
    y = head("Part II — Sentence MCQ (11–20)", y)
    y = grid(cfg["part2"]["items"], y,
             lambda it: f"{it['num']}.  {it['answer']})  {it['options']['abcd'.index(it['answer'])]}")
    y = head("Part III — Story T / F (21–30)", y)
    y = grid(cfg["part3"]["statements"], y,
             lambda s: f"{s['num']}.  {'T' if s['answer'] else 'F'}")
    y = head("Part IV — Grammar MCQ (31–40)", y)
    y = grid(cfg["part4"]["items"], y,
             lambda it: f"{it['num']}.  {it['answer']})")
    c.setFont("Helvetica", 8.5)
    c.setFillColor(MUTED)
    c.drawString(MX, y, "Answer-letter spread — I: a3 b3 c2 d2 · II: a2 b3 c2 d3 · III: 5T/5F · IV: a3 b2 c3 d2")

    _footer(c, page[0])


# ── main ────────────────────────────────────────────────────────────────────

def generate(cfg_path: str) -> bytes:
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)
    db = SessionLocal()
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"{cfg['title']} {cfg['exam_id']} — {cfg['instructor']}")

    _cover(c, cfg, 40)
    _footer(c, 1)
    c.showPage()

    page = [2]
    _part1(c, cfg, db, page)                       # picture MCQ, reused renderer
    _mcq_text_part(c, cfg, "part2", "Part II", page)
    _part3_story(c, cfg, page)
    _mcq_text_part(c, cfg, "part4", "Part IV", page)
    _bubble_sheet(c, cfg, page)
    _answer_key(c, cfg, page)

    db.close()
    c.save()
    return buf.getvalue()


def main():
    args = sys.argv[1:]
    cfg_path = "tools/exam_b3_u6-10_mcq.json"
    out_path = "exports/Exam_B3_U6-10_MCQ.pdf"
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
