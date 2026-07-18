"""
B1 Vocabulary & Grammar Exam renderer.

Reads exam content from a JSON file (default: tools/exam_b1_vocab.json) and
renders a print-ready A4 PDF:
    cover · Part I picture MCQ · Part II word bank · Part III story T/F
    · Part IV grammar · teacher answer key.

Usage:
    py tools/generate_vocab_exam.py [--config tools/exam_b1_vocab.json] [--out FILE.pdf]
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from io import BytesIO

from PIL import Image, ImageChops
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import simpleSplit, ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY

from app.database import SessionLocal
from app.models.book import Word
from app.pdf_generator import _resolve_image_path, _draw_image_fitted

PAGE_W, PAGE_H = A4
MX = 15 * mm

INK = HexColor("#1A1209")
ACCENT = HexColor("#8B1F12")
RED = HexColor("#C0392B")
MUTED = HexColor("#7A6E63")
RULE = HexColor("#C9BFB4")
BANK_BG = HexColor("#FAF5EC")
BANK_BORDER = HexColor("#D8C9A6")
GOLD = HexColor("#B08D3E")
CREAM = HexColor("#FBF7F0")


# ── shared chrome ────────────────────────────────────────────────────────────

def _footer(c, n):
    c.setFont("Times-Italic", 8.5)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, 10 * mm, f"— {n} —")


def _running_header(c, cfg):
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(MUTED)
    c.drawString(MX, PAGE_H - 10 * mm, f"{cfg['title'].upper()}  ·  LEVEL {cfg['level']}")
    c.drawRightString(PAGE_W - MX, PAGE_H - 10 * mm, cfg["instructor"].upper())
    c.setStrokeColor(RULE)
    c.setLineWidth(0.3)
    c.line(MX, PAGE_H - 12 * mm, PAGE_W - MX, PAGE_H - 12 * mm)


def _section_title(c, y, roman, label, hint="", marks=None):
    c.setFillColor(ACCENT)
    c.setFont("Times-Bold", 12)
    c.drawString(MX, y, roman.upper())
    c.setFillColor(INK)
    c.setFont("Times-Bold", 13)
    c.drawString(MX + 20 * mm, y, label)
    if marks is not None:
        c.setFont("Times-Bold", 11)
        c.setFillColor(ACCENT)
        c.drawRightString(PAGE_W - MX, y, f"{marks} marks")
    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    c.line(MX, y - 2.5 * mm, PAGE_W - MX, y - 2.5 * mm)
    if hint:
        c.setFont("Times-Italic", 9.5)
        c.setFillColor(MUTED)
        c.drawString(MX, y - 7 * mm, hint)
        return y - 12 * mm
    return y - 6 * mm


def _fit_size(c, text, font, max_size, min_size, max_w):
    s = max_size
    while s > min_size and c.stringWidth(text, font, s) > max_w:
        s -= 1
    return s


# ── cover ────────────────────────────────────────────────────────────────────

def _cover_image_reader(path: str, target_ratio: float) -> ImageReader | None:
    """Open the cover art, trim near-white letterbox bars, then center-crop
    to the panel's aspect ratio so it fills the frame edge to edge."""
    if not path or not os.path.exists(path):
        return None
    im = Image.open(path).convert("RGB")
    bg = Image.new("RGB", im.size, (255, 255, 255))
    diff = ImageChops.difference(im, bg)
    bbox = diff.point(lambda p: 255 if p > 12 else 0).getbbox()
    if bbox:
        im = im.crop(bbox)
    w, h = im.size
    if w / h > target_ratio:                      # too wide — trim sides
        new_w = int(h * target_ratio)
        x0 = (w - new_w) // 2
        im = im.crop((x0, 0, x0 + new_w, h))
    else:                                         # too tall — trim top/bottom
        new_h = int(w / target_ratio)
        y0 = (h - new_h) // 2
        im = im.crop((0, y0, w, y0 + new_h))
    buf = BytesIO()
    im.save(buf, format="JPEG", quality=88)
    buf.seek(0)
    return ImageReader(buf)


def _cover(c, cfg, total_marks):
    # cream field + certificate double frame
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    c.setStrokeColor(INK)
    c.setLineWidth(1.2)
    c.rect(9 * mm, 9 * mm, PAGE_W - 18 * mm, PAGE_H - 18 * mm, stroke=1, fill=0)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.rect(11.5 * mm, 11.5 * mm, PAGE_W - 23 * mm, PAGE_H - 23 * mm, stroke=1, fill=0)

    # eyebrow — tracked small caps
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 30 * mm, "  ".join(cfg["eyebrow"]))

    c.setStrokeColor(GOLD)
    c.setLineWidth(0.7)
    c.line(PAGE_W / 2 - 16 * mm, PAGE_H - 35 * mm, PAGE_W / 2 + 16 * mm, PAGE_H - 35 * mm)

    # hero title, letterspaced
    title = "  ".join(cfg["title"].upper())
    size = _fit_size(c, title, "Times-Bold", 84, 40, PAGE_W - 60 * mm)
    c.setFont("Times-Bold", size)
    c.setFillColor(INK)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 70 * mm, title)

    # skills line
    c.setFont("Times-Italic", 16)
    c.setFillColor(ACCENT)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 82 * mm, cfg["subtitle"])

    orn_y = PAGE_H - 93 * mm
    c.setStrokeColor(RULE)
    c.setLineWidth(0.4)
    c.line(PAGE_W / 2 - 52 * mm, orn_y, PAGE_W / 2 - 14 * mm, orn_y)
    c.line(PAGE_W / 2 + 14 * mm, orn_y, PAGE_W / 2 + 52 * mm, orn_y)
    c.setFont("Times-Roman", 12)
    c.setFillColor(GOLD)
    c.drawCentredString(PAGE_W / 2, orn_y - 4, "❖  ❖  ❖")

    # framed hero image panel
    panel_w, panel_h = 148 * mm, 74 * mm
    panel_x = (PAGE_W - panel_w) / 2
    panel_top = PAGE_H - 101 * mm
    panel_y = panel_top - panel_h
    reader = _cover_image_reader(cfg.get("cover_image"), panel_w / panel_h)
    if reader:
        c.drawImage(reader, panel_x, panel_y, width=panel_w, height=panel_h, mask="auto")
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.0)
    c.rect(panel_x - 1.5 * mm, panel_y - 1.5 * mm, panel_w + 3 * mm, panel_h + 3 * mm, stroke=1, fill=0)
    c.setStrokeColor(INK)
    c.setLineWidth(0.4)
    c.rect(panel_x, panel_y, panel_w, panel_h, stroke=1, fill=0)

    # instructor
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, panel_y - 12 * mm, "I N S T R U C T O R")
    c.setFont("Times-Italic", 23)
    c.setFillColor(INK)
    c.drawCentredString(PAGE_W / 2, panel_y - 21 * mm, cfg["instructor"])

    # info strip
    info_y = panel_y - 35 * mm
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    c.line(MX + 18 * mm, info_y + 5.5 * mm, PAGE_W - MX - 18 * mm, info_y + 5.5 * mm)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(INK)
    info = f"LEVEL {cfg['level']}     ·     {cfg['time_allowed'].upper()}     ·     4 PARTS     ·     {total_marks} MARKS"
    c.drawCentredString(PAGE_W / 2, info_y, info)
    c.line(MX + 18 * mm, info_y - 4 * mm, PAGE_W - MX - 18 * mm, info_y - 4 * mm)

    # name / date
    by = info_y - 20 * mm
    bx = 28 * mm
    bw = PAGE_W - 56 * mm
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(INK)
    c.drawString(bx, by, "NAME")
    c.setStrokeColor(INK)
    c.setLineWidth(0.6)
    c.line(bx + 16 * mm, by - 0.5, bx + bw * 0.55, by - 0.5)
    c.drawString(bx + bw * 0.62, by, "DATE")
    c.line(bx + bw * 0.62 + 14 * mm, by - 0.5, bx + bw, by - 0.5)

    # score box — bottom right, inside the frame
    box_w, box_h = 36 * mm, 20 * mm
    box_x, box_y = PAGE_W - 20 * mm - box_w, 20 * mm
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.9)
    c.rect(box_x, box_y, box_w, box_h, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(MUTED)
    c.drawCentredString(box_x + box_w / 2, box_y + box_h - 6, "S C O R E")
    c.setFont("Times-Bold", 21)
    c.setFillColor(INK)
    c.drawCentredString(box_x + box_w / 2, box_y + 3.5 * mm, f"/  {total_marks}")

    # footer signature
    c.setFont("Helvetica", 7.5)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, 14.5 * mm,
                        f"{cfg['title'].upper()}   ·   {cfg['instructor'].upper()}")


# ── Part I: picture MCQ, 2 cols × 3 rows ────────────────────────────────────

P1_COLS, P1_ROWS = 2, 3
P1_W = (PAGE_W - 2 * MX) / P1_COLS
P1_H = 78 * mm


def _p1_cell(c, x, y, item, img_path):
    """x,y = bottom-left of cell."""
    inner_x = x + 6 * mm
    inner_w = P1_W - 12 * mm

    c.setFillColor(INK)
    c.setFont("Times-Bold", 13)
    c.drawString(inner_x, y + P1_H - 7 * mm, f"{item['num']}.")

    img_h = 46 * mm
    img_w = inner_w - 6 * mm
    img_x = inner_x + 3 * mm
    img_y = y + P1_H - 9 * mm - img_h
    if img_path:
        _draw_image_fitted(c, img_path, img_x, img_y, img_w, img_h, padding=0)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.4)
    c.rect(img_x, img_y, img_w, img_h, stroke=1, fill=0)

    opts_y = img_y - 8 * mm
    col_w = inner_w / 2
    for i, opt in enumerate(item["options"]):
        row, col = i // 2, i % 2
        ox = inner_x + col * col_w
        oy = opts_y - row * 7 * mm
        c.setStrokeColor(INK)
        c.setLineWidth(0.6)
        c.circle(ox + 2.5 * mm, oy + 1.2 * mm, 2.5 * mm, stroke=1, fill=0)
        c.setFont("Times-Bold", 9.5)
        c.setFillColor(INK)
        c.drawCentredString(ox + 2.5 * mm, oy - 0.5 * mm, "abcd"[i])
        c.setFont("Helvetica", 10.5)
        c.drawString(ox + 7 * mm, oy, opt)


def _part1(c, cfg, db, page):
    p1 = cfg["part1"]
    _running_header(c, cfg)
    top = _section_title(c, PAGE_H - 20 * mm, "Part I", p1["label"], p1["hint"], marks=10)
    on_page = 0
    for item in p1["items"]:
        if on_page >= P1_COLS * P1_ROWS:
            _footer(c, page[0]); c.showPage(); page[0] += 1
            _running_header(c, cfg)
            top = _section_title(c, PAGE_H - 20 * mm, "Part I", "(continued)")
            on_page = 0
        row, col = on_page // P1_COLS, on_page % P1_COLS
        x = MX + col * P1_W
        y = top - (row + 1) * P1_H
        w = db.query(Word).filter(Word.word == item["word"]).first()
        img_path = _resolve_image_path(w.image_url) if w else None
        _p1_cell(c, x, y, item, img_path)
        on_page += 1
    _footer(c, page[0]); c.showPage(); page[0] += 1


# ── Part II: word bank ───────────────────────────────────────────────────────

def _word_bank_box(c, y_top, words):
    box_x, box_w, pad = MX, PAGE_W - 2 * MX, 5 * mm
    c.setFont("Times-Bold", 10)
    c.setFillColor(ACCENT)
    c.drawString(box_x, y_top, "WORD BANK")

    font, size = "Helvetica", 11
    gap_x, gap_y, pad_x, pad_y = 4 * mm, 4 * mm, 3 * mm, 1.6 * mm
    rows, cur_w = [[]], 0
    inner_w = box_w - 2 * pad
    for w in words:
        tw = c.stringWidth(w, font, size) + 2 * pad_x
        if cur_w + tw + gap_x > inner_w and rows[-1]:
            rows.append([]); cur_w = 0
        rows[-1].append((w, tw)); cur_w += tw + gap_x

    chip_h = size + 2 * pad_y
    box_h = pad * 2 + len(rows) * chip_h + (len(rows) - 1) * gap_y
    box_top = y_top - 4 * mm
    box_bot = box_top - box_h

    c.setFillColor(BANK_BG)
    c.setStrokeColor(BANK_BORDER)
    c.setLineWidth(0.8)
    c.roundRect(box_x, box_bot, box_w, box_h, 4 * mm, stroke=1, fill=1)

    cy = box_top - pad - chip_h
    for row in rows:
        row_w = sum(w for _, w in row) + gap_x * (len(row) - 1)
        cx = box_x + (box_w - row_w) / 2
        for word, tw in row:
            c.setStrokeColor(BANK_BORDER); c.setFillColor(white); c.setLineWidth(0.4)
            c.roundRect(cx, cy, tw, chip_h, 2 * mm, stroke=1, fill=1)
            c.setFillColor(INK); c.setFont(font, size)
            c.drawCentredString(cx + tw / 2, cy + pad_y, word)
            cx += tw + gap_x
        cy -= chip_h + gap_y
    return box_bot - 8 * mm


def _part2(c, cfg, page):
    p2 = cfg["part2"]
    _running_header(c, cfg)
    y = _section_title(c, PAGE_H - 20 * mm, "Part II", p2["label"], p2["hint"], marks=10)
    y = _word_bank_box(c, y - 2 * mm, p2["bank"])

    style = ParagraphStyle(name="wb", fontName="Times-Roman", fontSize=12,
                           leading=17, textColor=INK)
    avail_w = PAGE_W - 2 * MX
    for s in p2["sentences"]:
        p = Paragraph(f'<font name="Times-Bold">{s["num"]}.</font> &nbsp; {s["text"]}', style)
        _, ph = p.wrap(avail_w, 999)
        p.drawOn(c, MX, y - ph)
        y -= ph + 5.5 * mm
    _footer(c, page[0]); c.showPage(); page[0] += 1


# ── Part III: story + T/F ────────────────────────────────────────────────────

def _part3(c, cfg, page):
    p3 = cfg["part3"]
    _running_header(c, cfg)
    y = _section_title(c, PAGE_H - 20 * mm, "Part III", p3["label"], p3["hint"], marks=10)

    # story box
    style = ParagraphStyle(name="story", fontName="Times-Roman", fontSize=11.5,
                           leading=16.5, textColor=INK, alignment=TA_JUSTIFY)
    pad = 6 * mm
    box_w = PAGE_W - 2 * MX
    inner_w = box_w - 2 * pad
    para = Paragraph(p3["story"], style)
    _, ph = para.wrap(inner_w, 999)
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

    # statements
    y = box_bot - 10 * mm
    tf_x = PAGE_W - MX - 24 * mm
    for s in p3["statements"]:
        c.setFont("Times-Bold", 11)
        c.setFillColor(INK)
        c.drawString(MX, y, f"{s['num']}.")
        c.setFont("Times-Roman", 11.5)
        lines = simpleSplit(s["text"], "Times-Roman", 11.5, tf_x - MX - 12 * mm)
        for i, line in enumerate(lines):
            c.drawString(MX + 8 * mm, y - i * 5 * mm, line)
        for j, letter in enumerate(("T", "F")):
            cx = tf_x + j * 11 * mm
            c.setStrokeColor(INK)
            c.setLineWidth(0.6)
            c.circle(cx, y + 1.2 * mm, 3.2 * mm, stroke=1, fill=0)
            c.setFont("Times-Bold", 10.5)
            c.setFillColor(INK)
            c.drawCentredString(cx, y - 0.2 * mm, letter)
        y -= max(1, len(lines)) * 5 * mm + 5.5 * mm
    _footer(c, page[0]); c.showPage(); page[0] += 1


# ── Part IV: grammar ─────────────────────────────────────────────────────────

def _part4(c, cfg, page):
    p4 = cfg["part4"]
    _running_header(c, cfg)
    y = _section_title(c, PAGE_H - 20 * mm, "Part IV", p4["label"], p4["hint"], marks=10)
    y -= 2 * mm

    for item in p4["items"]:
        req = f"({item['requirement']})"
        req_w = c.stringWidth(req, "Helvetica-BoldOblique", 10)
        sent_w = PAGE_W - 2 * MX - req_w - 6 * mm

        c.setFont("Times-Bold", 11.5)
        c.setFillColor(ACCENT)
        c.drawString(MX, y, f"{item['num']}.")

        lines = simpleSplit(item["sentence"], "Times-Roman", 11.5, sent_w - 8 * mm)
        c.setFont("Times-Roman", 11.5)
        c.setFillColor(INK)
        for i, line in enumerate(lines):
            c.drawString(MX + 8 * mm, y - i * 5.5 * mm, line)

        c.setFont("Helvetica-BoldOblique", 10)
        c.setFillColor(RED)
        c.drawRightString(PAGE_W - MX, y, req)

        y -= max(1, len(lines)) * 5.5 * mm + 2 * mm
        if item.get("line"):
            c.setStrokeColor(MUTED)
            c.setLineWidth(0.4)
            c.line(MX + 8 * mm, y - 3 * mm, PAGE_W - MX, y - 3 * mm)
            y -= 8 * mm
        else:
            y -= 3 * mm

        # separator after EVERY question — each item is its own block
        c.setStrokeColor(RULE)
        c.setLineWidth(0.3)
        c.setDash(1, 2)
        c.line(MX, y, PAGE_W - MX, y)
        c.setDash()
        y -= 7 * mm
    _footer(c, page[0]); c.showPage(); page[0] += 1


# ── answer key ───────────────────────────────────────────────────────────────

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
                        "Detach this page before handing the exam to students.")

    y = PAGE_H - 38 * mm

    def head(label, yy):
        c.setFont("Times-Bold", 12)
        c.setFillColor(INK)
        c.drawString(MX, yy, label)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.3)
        c.line(MX, yy - 2 * mm, PAGE_W - MX, yy - 2 * mm)
        return yy - 7 * mm

    # Parts I–III: compact two-row grids
    y = head("Part I — Picture MCQ", y)
    c.setFont("Helvetica", 10)
    c.setFillColor(INK)
    for i, item in enumerate(cfg["part1"]["items"]):
        col, row = i % 5, i // 5
        c.drawString(MX + col * 36 * mm, y - row * 6 * mm,
                     f"{item['num']}.  {item['answer']})  {item['options']['abcd'.index(item['answer'])]}")
    y -= 16 * mm

    y = head("Part II — Word Bank", y)
    c.setFont("Helvetica", 10)
    c.setFillColor(INK)
    for i, s in enumerate(cfg["part2"]["sentences"]):
        col, row = i % 5, i // 5
        c.drawString(MX + col * 36 * mm, y - row * 6 * mm, f"{s['num']}.  {s['answer']}")
    c.setFont("Helvetica", 8.5)
    c.setFillColor(MUTED)
    extras = [w for w in cfg["part2"]["bank"]
              if w not in {s["answer"] for s in cfg["part2"]["sentences"]}]
    c.drawString(MX, y - 17 * mm, f"Extra (unused) words: {', '.join(extras)}")
    y -= 24 * mm

    y = head("Part III — Story True / False", y)
    c.setFont("Helvetica", 10)
    c.setFillColor(INK)
    for i, s in enumerate(cfg["part3"]["statements"]):
        col, row = i % 5, i // 5
        c.drawString(MX + col * 36 * mm, y - row * 6 * mm,
                     f"{s['num']}.  {'T' if s['answer'] else 'F'}")
    y -= 16 * mm

    y = head("Part IV — Grammar", y)
    for item in cfg["part4"]["items"]:
        c.setFont("Helvetica", 10)
        c.setFillColor(INK)
        c.drawString(MX, y, f"{item['num']}.")
        c.setFont("Times-Bold", 10.5)
        c.drawString(MX + 8 * mm, y, item["answer"])
        c.setFont("Helvetica-Oblique", 8.5)
        c.setFillColor(RED)
        c.drawRightString(PAGE_W - MX, y, f"({item['requirement']})")
        y -= 6 * mm

    _footer(c, page[0])


# ── main ─────────────────────────────────────────────────────────────────────

def generate(cfg_path: str) -> bytes:
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)
    db = SessionLocal()
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"{cfg['title']} — {cfg['instructor']}")

    total_marks = 40
    _cover(c, cfg, total_marks)
    _footer(c, 1)
    c.showPage()

    page = [2]
    _part1(c, cfg, db, page)
    _part2(c, cfg, page)
    _part3(c, cfg, page)
    _part4(c, cfg, page)
    _answer_key(c, cfg, page)

    db.close()
    c.save()
    return buf.getvalue()


def main():
    args = sys.argv[1:]
    cfg_path = "tools/exam_b1_vocab.json"
    out_path = "Vocabulary_Exam_B1.pdf"
    if "--config" in args:
        i = args.index("--config"); cfg_path = args[i + 1]
    if "--out" in args:
        i = args.index("--out"); out_path = args[i + 1]
    pdf = generate(cfg_path)
    with open(out_path, "wb") as f:
        f.write(pdf)
    print(f"Saved: {out_path}  ({len(pdf) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
