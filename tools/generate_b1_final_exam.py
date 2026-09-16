"""
B1 final exam renderer — 100 questions across Listening, Reading, Grammar
and Speaking, on a two-page machine-markable answer sheet.

Extends the A1 renderer (tools/generate_a1_exam.py) rather than duplicating it:
fonts, palette, section headers, picture cells and plain MCQ layout are all
imported. What this file adds is what the B1 paper needs and A1 does not:

    kind "gap"       listening fill-the-blanks (hand-marked, not bubbled)
    kind "passage"   long reading text + T/F or MCQ, with pagination
    kind "speaking"  teacher examiner card + scoring rubric
    subhead          topic rule inside an mcq part, so 40 grammar questions
                     live in ONE part instead of burning seven pages
    answer sheets    3 columns x 15 rows, split across 2 sheets, plus a
                     write-in box for the listening gaps

The bubble geometry (r=3.2mm, 11mm pitch, 4 solid corner markers) is identical
to the A1/B3 sheets, so the photograph-and-mark workflow is unchanged.

Usage:
    py tools/generate_b1_final_exam.py [--config FILE.json] [--out FILE.pdf]
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import black, white
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT

from app.database import SessionLocal
from tools.generate_vocab_exam import _cover_image_reader
from tools.generate_a1_exam import (
    PAGE_W, PAGE_H, MX,
    INK, ACCENT, MUTED, RULE, CARD, TINT, GHOST,
    _register_fonts, _tracked, _fit_size,
    _running_header, _footer, _section, _bubble_option,
    _picture_part, _story_part, _corner_markers, _bubble,
)


# ── helpers ─────────────────────────────────────────────────────────────────

def _part_items(part):
    """Every part type exposes its questions under one of these keys."""
    return part.get("items") or part.get("statements") or []


def _recording_title(c, y, text):
    """Names the recording a listening part is based on, so the two audio parts
    are told apart at a glance. Mirrors the passage-title treatment in Parts V-VI."""
    h = 10 * mm
    c.setFillColor(TINT)
    c.roundRect(MX, y - h, PAGE_W - 2 * MX, h, 2.5 * mm, stroke=0, fill=1)
    _tracked(c, PAGE_W / 2, y - 6.6 * mm, text.upper(), "UI-Semibold", 11.5,
             ACCENT, tracking=2)
    return y - h - 6 * mm


def _new_page(c, cfg, part, page, total):
    """Close the current page and re-open the same part as '(continued)'."""
    _footer(c, cfg, page[0])
    c.showPage()
    page[0] += 1
    return _section(c, cfg, {"roman": part["roman"], "label": "(continued)"}, total)


# ── Part: listening gap-fill (hand-marked) ──────────────────────────────────

RULE_W = 34 * mm        # writing room on the rule itself
NUM_GAP = 1.8 * mm      # space between the "(1)" label and the rule


def _blank_w(c, num, size):
    """A blank renders as  (1) ______________  — number on the baseline, never
    floating over the rule, so it reads as a label rather than an answer."""
    return c.stringWidth(f"({num})", "UI-Semibold", size) + NUM_GAP + RULE_W


def _tokenise(text):
    """'... beautiful [[1]] there' -> ['...', 'beautiful', ('blank', 1), 'there']"""
    out, buf, i = [], "", 0
    while i < len(text):
        if text[i:i + 2] == "[[":
            j = text.index("]]", i)
            out.extend(buf.split())
            buf = ""
            out.append(("blank", int(text[i + 2:j])))
            i = j + 2
        else:
            buf += text[i]
            i += 1
    out.extend(buf.split())
    return out


def _glued(t):
    """Trailing punctuation must hug the previous token, not float after a space."""
    return isinstance(t, str) and t[:1] in ".,!?;:"


def _wrap_runs(c, tokens, font, size, width):
    """Greedy word-wrap over a mix of words and fixed-width blanks."""
    space = c.stringWidth(" ", font, size)
    lines, cur, cur_w = [], [], 0.0
    for t in tokens:
        w = _blank_w(c, t[1], size) if isinstance(t, tuple) else c.stringWidth(t, font, size)
        gap = 0 if (not cur or _glued(t)) else space
        if cur and cur_w + w + gap > width:
            lines.append(cur)
            cur, cur_w, gap = [], 0.0, 0
        cur.append(t)
        cur_w += w + gap
    if cur:
        lines.append(cur)
    return lines


def _draw_run_line(c, line, x, y, font, size):
    space = c.stringWidth(" ", font, size)
    for k, t in enumerate(line):
        if k and not _glued(t):
            x += space
        if isinstance(t, tuple):
            label = f"({t[1]})"
            c.setFillColor(ACCENT)
            c.setFont("UI-Semibold", size)
            c.drawString(x, y, label)
            lx = x + c.stringWidth(label, "UI-Semibold", size) + NUM_GAP
            c.setStrokeColor(INK)
            c.setLineWidth(0.7)
            c.line(lx, y - 1.4 * mm, lx + RULE_W, y - 1.4 * mm)
            c.setFillColor(INK)
            c.setFont(font, size)
            x += _blank_w(c, t[1], size)
        else:
            c.drawString(x, y, t)
            x += c.stringWidth(t, font, size)


def _dialogue_gaps(c, cfg, part, page):
    """Listening transcript rendered as speaker turns with numbered blanks."""
    items = part["items"]
    y = _section(c, cfg, part, len(items)) - 2 * mm
    if part.get("part_title"):
        y = _recording_title(c, y, part["part_title"])
    label_w = 16 * mm
    x = MX + label_w
    avail = PAGE_W - MX - x
    size, leading = 12, 7.2 * mm

    for turn in part["dialogue"]:
        lines = _wrap_runs(c, _tokenise(turn["text"]), "UI", size, avail)
        if y - len(lines) * leading < 20 * mm:
            y = _new_page(c, cfg, part, page, len(items)) - 2 * mm
        c.setFillColor(ACCENT)
        c.setFont("UI-Semibold", size)
        c.drawString(MX, y, turn["speaker"] + ":")
        c.setFillColor(INK)
        c.setFont("UI", size)
        for line in lines:
            _draw_run_line(c, line, x, y, "UI", size)
            y -= leading
        y -= 1.6 * mm

    _footer(c, cfg, page[0])
    c.showPage()
    page[0] += 1


def _gap_part(c, cfg, part, page):
    if part.get("dialogue"):
        return _dialogue_gaps(c, cfg, part, page)
    items = part["items"]
    y = _section(c, cfg, part, len(items))

    if part.get("bank"):
        bank = part["bank"]
        pad = 5 * mm
        cols = 4
        rows = (len(bank) + cols - 1) // cols
        box_h = rows * 7 * mm + 2 * pad
        box_y = y - box_h + 2 * mm
        c.setFillColor(TINT)
        c.roundRect(MX, box_y, PAGE_W - 2 * MX, box_h, 3 * mm, stroke=0, fill=1)
        col_w = (PAGE_W - 2 * MX - 2 * pad) / cols
        for i, w in enumerate(bank):
            r, col = i // cols, i % cols
            c.setFillColor(ACCENT)
            c.setFont("UI-Semibold", 11.5)
            c.drawString(MX + pad + col * col_w, box_y + box_h - pad - 4 * mm - r * 7 * mm, w)
        y = box_y - 9 * mm

    for item in items:
        if y < 26 * mm:
            y = _new_page(c, cfg, part, page, len(items)) - 3 * mm

        c.setFillColor(ACCENT)
        c.setFont("UI-Semibold", 13)
        c.drawString(MX, y, f"{item['num']}.")

        # split the sentence on the blank so the ruled line sits inline
        text = item["text"]
        marker = "______"
        before, _, after = text.partition(marker)
        x = MX + 11 * mm
        avail = PAGE_W - MX - x
        c.setFillColor(INK)
        c.setFont("UI", 13)

        tail = after.lstrip()
        lines = simpleSplit(before.rstrip() + " " + tail, "UI", 13, avail)
        if len(lines) > 1 or c.stringWidth(before, "UI", 13) + 34 * mm + c.stringWidth(after, "UI", 13) > avail:
            # long sentence — wrap it, then put the answer line underneath
            wrapped = simpleSplit(text.replace(marker, "____________"), "UI", 13, avail) or [text]
            for i, line in enumerate(wrapped):
                c.drawString(x, y - i * 6.5 * mm, line)
            y -= len(wrapped) * 6.5 * mm + 4 * mm
        else:
            c.drawString(x, y, before.rstrip())
            lx = x + c.stringWidth(before.rstrip() + " ", "UI", 13)
            c.setStrokeColor(INK)
            c.setLineWidth(0.7)
            c.line(lx, y - 1.2 * mm, lx + 32 * mm, y - 1.2 * mm)
            # punctuation hugs the rule; a real word gets a word space
            pad_after = 0.6 * mm if tail[:1] in ".,!?;:" else 2 * mm
            c.drawString(lx + 32 * mm + pad_after, y, tail)
            y -= 12 * mm

    _footer(c, cfg, page[0])
    c.showPage()
    page[0] += 1


# ── Part: long passage + T/F or MCQ ─────────────────────────────────────────

def _passage_part(c, cfg, part, page):
    items = _part_items(part)
    total = len(items)
    mode = "tf" if part.get("statements") else "mcq"
    y = _section(c, cfg, part, total)

    style = ParagraphStyle(name="passage", fontName="UI", fontSize=11.5,
                           leading=18, textColor=INK, alignment=TA_LEFT)
    pad = 7 * mm
    box_w = PAGE_W - 2 * MX
    inner_w = box_w - 2 * pad
    paras = [Paragraph(p, style) for p in part["passage"].split("\n\n") if p.strip()]
    heights = [p.wrap(inner_w, 9999)[1] for p in paras]
    GAP = 6

    # Long B1 passages run past one page, so flow the paragraphs and draw a
    # fresh card behind whatever lands on each page.
    idx, first = 0, True
    while idx < len(paras):
        title_h = 10 * mm if first else 0
        avail = (y - 2 * mm) - 22 * mm - 2 * pad - title_h
        take, used = 0, 0.0
        while idx + take < len(paras):
            h = heights[idx + take] + (GAP if take else 0)
            if take and used + h > avail:
                break
            used += h
            take += 1
            if used > avail:      # one paragraph taller than the page — emit it alone
                break

        box_h = used + 2 * pad + title_h
        box_top = y - 2 * mm
        box_bot = box_top - box_h
        c.setFillColor(CARD)
        c.roundRect(MX, box_bot, box_w, box_h, 4 * mm, stroke=0, fill=1)
        if first:
            c.setFont("UI-Semibold", 14)
            c.setFillColor(ACCENT)
            c.drawCentredString(PAGE_W / 2, box_top - pad - 3 * mm, part["passage_title"])

        py = box_bot + pad
        for k in range(idx + take - 1, idx - 1, -1):
            paras[k].drawOn(c, MX + pad, py)
            py += heights[k] + GAP

        idx += take
        y = box_bot - 12 * mm
        first = False
        if idx < len(paras):
            y = _new_page(c, cfg, part, page, total)

    if mode == "tf":
        tx = MX + 11 * mm
        # leave a clear lane for the right-aligned T / F so long statements
        # wrap instead of running into it
        text_w = PAGE_W - MX - tx - 22 * mm
        for s in items:
            lines = simpleSplit(s["text"], "UI", 12.5, text_w) or [s["text"]]
            # 15mm keeps the lowest baseline ~21mm up, well clear of the 10mm footer
            if y - len(lines) * 6.4 * mm < 15 * mm:
                y = _new_page(c, cfg, part, page, total)
            c.setFillColor(ACCENT)
            c.setFont("UI-Semibold", 12.5)
            c.drawString(MX, y, f"{s['num']}.")
            c.setFillColor(INK)
            c.setFont("UI", 12.5)
            for i, line in enumerate(lines):
                c.drawString(tx, y - i * 6.4 * mm, line)
            c.setFont("UI-Semibold", 11)
            c.setFillColor(MUTED)
            c.drawRightString(PAGE_W - MX, y, "T  /  F")
            y -= (len(lines) - 1) * 6.4 * mm + 10.5 * mm
    else:
        y = _mcq_items(c, cfg, part, items, y, page, total)

    _footer(c, cfg, page[0])
    c.showPage()
    page[0] += 1


# ── shared MCQ item renderer (adds `subhead` support) ────────────────────────

def _mcq_items(c, cfg, part, items, y, page, total):
    avail_w = PAGE_W - 2 * MX - 10 * mm

    for item in items:
        lines = simpleSplit(item["sentence"], "UI-Semibold", 12.5, avail_w)
        longest = max(c.stringWidth(o, "UI", 11.5) for o in item["options"])
        grid = longest <= min(avail_w / 2 - 16 * mm, 52 * mm)
        opts_h = 2 * 8 * mm if grid else 4 * 7.6 * mm
        head_h = 11 * mm if item.get("subhead") else 0
        block_h = head_h + len(lines) * 6.2 * mm + 3.5 * mm + opts_h + 7 * mm

        if y - block_h < 18 * mm:
            y = _new_page(c, cfg, part, page, total) - 3 * mm

        if item.get("subhead"):
            c.setStrokeColor(RULE)
            c.setLineWidth(0.5)
            c.line(MX, y + 4 * mm, PAGE_W - MX, y + 4 * mm)
            _tracked(c, MX, y - 1 * mm, item["subhead"].upper(),
                     "UI-Semibold", 8.5, ACCENT, tracking=1.6, centered=False)
            y -= 8 * mm

        c.setFillColor(ACCENT)
        c.setFont("UI-Semibold", 12.5)
        c.drawString(MX, y, f"{item['num']}.")
        c.setFillColor(INK)
        for i, line in enumerate(lines):
            c.drawString(MX + 11 * mm, y - i * 6.2 * mm, line)
        y -= (len(lines) - 1) * 6.2 * mm + 8.5 * mm

        if grid:
            col_w = avail_w / 2
            for i, opt in enumerate(item["options"]):
                r, col = i // 2, i % 2
                _bubble_option(c, MX + 11 * mm + col * col_w, y - r * 8 * mm, "abcd"[i], opt, size=11.5)
            y -= 2 * 8 * mm
        else:
            for i, opt in enumerate(item["options"]):
                _bubble_option(c, MX + 11 * mm, y - i * 7.6 * mm, "abcd"[i], opt, size=11.5)
            y -= 4 * 7.6 * mm
        y -= 4 * mm

    return y


def _mcq_part(c, cfg, part, page):
    items = part["items"]
    y = _section(c, cfg, part, len(items)) - 3 * mm
    if part.get("part_title"):
        y = _recording_title(c, y + 1 * mm, part["part_title"])
    _mcq_items(c, cfg, part, items, y, page, len(items))
    _footer(c, cfg, page[0])
    c.showPage()
    page[0] += 1


# ── Part: speaking examiner card (teacher only) ─────────────────────────────

def _speaking_part(c, cfg, part, page):
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
    c.setFillColor(INK)
    c.setFont("UI-Semibold", 16)
    c.drawString(MX + ch_w + 5 * mm, y, part["label"])
    c.setFillColor(ACCENT)
    c.setFont("UI-Semibold", 10)
    c.drawRightString(PAGE_W - MX, y, f"{part['marks']} MARKS")
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.line(MX, y - 6 * mm, PAGE_W - MX, y - 6 * mm)

    c.setFillColor(MUTED)
    c.setFont("UI-Italic", 10.5)
    c.drawString(MX, y - 12 * mm, part["hint"])
    y -= 22 * mm

    for block in part["blocks"]:
        pad = 5 * mm
        prompts = block["prompts"]
        box_h = 15 * mm + len(prompts) * 7 * mm
        c.setFillColor(CARD)
        c.roundRect(MX, y - box_h, PAGE_W - 2 * MX, box_h, 3.5 * mm, stroke=0, fill=1)

        c.setFillColor(ACCENT)
        c.setFont("UI-Semibold", 12.5)
        c.drawString(MX + pad, y - 8 * mm, block["title"])
        c.setFillColor(MUTED)
        c.setFont("UI", 10)
        c.drawRightString(PAGE_W - MX - pad, y - 8 * mm, block["timing"])

        c.setFillColor(INK)
        c.setFont("UI", 11.5)
        for i, p in enumerate(prompts):
            c.drawString(MX + pad + 4 * mm, y - 15 * mm - i * 7 * mm, f"•  {p}")
        y -= box_h + 6 * mm

    # rubric
    y -= 2 * mm
    _tracked(c, MX, y, "SCORING RUBRIC", "UI-Semibold", 9, MUTED, tracking=2, centered=False)
    y -= 7 * mm
    rows = part["rubric"]
    band_w = 14 * mm
    label_w = PAGE_W - 2 * MX - 5 * band_w

    c.setFont("UI-Semibold", 9)
    c.setFillColor(MUTED)
    for i, band in enumerate(("1", "2", "3", "4", "5")):
        c.drawCentredString(MX + label_w + i * band_w + band_w / 2, y, band)
    y -= 5 * mm

    for label in rows:
        c.setStrokeColor(RULE)
        c.setLineWidth(0.4)
        c.line(MX, y + 5.5 * mm, PAGE_W - MX, y + 5.5 * mm)
        c.setFillColor(INK)
        c.setFont("UI", 11.5)
        c.drawString(MX, y, label)
        for i in range(5):
            _bubble(c, MX + label_w + i * band_w + band_w / 2, y + 1.2 * mm, "", r=2.6 * mm)
        y -= 9 * mm

    c.setStrokeColor(RULE)
    c.line(MX, y + 5.5 * mm, PAGE_W - MX, y + 5.5 * mm)
    y -= 3 * mm
    c.setFillColor(CARD)
    c.roundRect(PAGE_W - MX - 48 * mm, y - 6 * mm, 48 * mm, 12 * mm, 3 * mm, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont("UI-Semibold", 12)
    c.drawCentredString(PAGE_W - MX - 24 * mm, y - 2 * mm, f"TOTAL        /  {part['marks']}")

    _footer(c, cfg, page[0])
    c.showPage()
    page[0] += 1


# ── cover ───────────────────────────────────────────────────────────────────

def _hrule(c, y, weight=0.5, color=RULE, x0=MX, x1=PAGE_W - MX):
    c.setStrokeColor(color)
    c.setLineWidth(weight)
    c.line(x0, y, x1, y)


def _section_caption(c, y, text):
    """Small tracked caption above a block, in the formal-paper style."""
    _tracked(c, MX, y, text, "UI-Semibold", 8, ACCENT, tracking=2, centered=False)
    return y - 6 * mm


def _entry_field(c, x, y, w, label, h=13 * mm):
    """A ruled box the candidate writes into — Cambridge-style detail grid."""
    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    c.rect(x, y, w, h, stroke=1, fill=0)
    _tracked(c, x + 2.5 * mm, y + h - 4.6 * mm, label, "UI-Semibold", 6.5, MUTED,
             tracking=1.4, centered=False)


def _cover(c, cfg, written_total, speaking_marks, parts, total_pages):
    """Formal examination front sheet: identity, candidate details, instructions,
    information, examiner mark grid.  Deliberately typographic — no imagery."""
    c.setFillColor(white)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    # ── masthead ────────────────────────────────────────────────────────────
    y = PAGE_H - 18 * mm
    _hrule(c, y + 4 * mm, 1.6, INK)
    if cfg.get("institution"):
        _tracked(c, PAGE_W / 2, y - 3 * mm, cfg["institution"], "UI-Semibold", 10, INK, tracking=3)
        y -= 9 * mm
    _tracked(c, PAGE_W / 2, y - 3 * mm, cfg["eyebrow"], "UI-Semibold", 8, MUTED, tracking=3)
    y -= 9 * mm
    _hrule(c, y, 0.5)

    y -= 12 * mm
    size = _fit_size(c, cfg["title"].upper(), "UI-Semibold", 30, 18, PAGE_W - 2 * MX - 10 * mm)
    _tracked(c, PAGE_W / 2, y, cfg["title"].upper(), "UI-Semibold", size, INK, tracking=2.5)

    y -= 9 * mm
    c.setFont("UI", 13)
    c.setFillColor(INK)
    c.drawCentredString(PAGE_W / 2, y, f"{cfg['paper_subject']}  —  Level {cfg['level']}")
    y -= 6.5 * mm
    c.setFont("UI-Italic", 11)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, y, cfg["subtitle"])
    y -= 6 * mm
    c.setFont("UI", 9.5)
    c.drawCentredString(PAGE_W / 2, y, f"{cfg['exam_id']}          {cfg.get('session', '')}")

    y -= 8 * mm
    _hrule(c, y, 1.2, INK)

    # ── candidate details ───────────────────────────────────────────────────
    y -= 10 * mm
    y = _section_caption(c, y, "CANDIDATE DETAILS")
    fw = (PAGE_W - 2 * MX) / 2
    _entry_field(c, MX, y - 13 * mm, fw, "CANDIDATE NAME")
    _entry_field(c, MX + fw, y - 13 * mm, fw, "CLASS / SECTION")
    _entry_field(c, MX, y - 26 * mm, fw, "CANDIDATE NUMBER")
    _entry_field(c, MX + fw, y - 26 * mm, fw, "DATE")
    y -= 32 * mm

    # ── paper facts strip ───────────────────────────────────────────────────
    facts = [("TIME ALLOWED", cfg["time_allowed"])]
    if written_total:
        facts += [("TOTAL MARKS", str(written_total)),
                  ("QUESTIONS", str(written_total))]
    else:
        facts += [("TOTAL MARKS", str(speaking_marks))]
    facts.append(("PAGES", str(total_pages) if total_pages else "—"))

    cw = (PAGE_W - 2 * MX) / len(facts)
    _hrule(c, y + 1 * mm, 0.5)
    for i, (label, val) in enumerate(facts):
        cx = MX + i * cw
        _tracked(c, cx + 2 * mm, y - 4.5 * mm, label, "UI-Semibold", 6.5, MUTED,
                 tracking=1.4, centered=False)
        c.setFont("UI-Semibold", 12)
        c.setFillColor(INK)
        c.drawString(cx + 2 * mm, y - 11 * mm, val)
        if i:
            c.setStrokeColor(RULE)
            c.setLineWidth(0.4)
            c.line(cx, y - 13 * mm, cx, y + 1 * mm)
    y -= 15 * mm
    _hrule(c, y, 0.5)

    # ── instructions ────────────────────────────────────────────────────────
    y -= 10 * mm
    y = _section_caption(c, y, "INSTRUCTIONS TO CANDIDATES")
    c.setFont("UI", 10.5)
    avail = PAGE_W - 2 * MX - 7 * mm
    for i, line in enumerate(cfg["instructions"], 1):
        for k, seg in enumerate(simpleSplit(line, "UI", 10.5, avail)):
            if k == 0:
                c.setFillColor(ACCENT)
                c.setFont("UI-Semibold", 10.5)
                c.drawString(MX, y, f"{i}")
                c.setFillColor(INK)
                c.setFont("UI", 10.5)
            c.drawString(MX + 7 * mm, y, seg)
            y -= 5.4 * mm
        y -= 0.8 * mm

    # ── information ─────────────────────────────────────────────────────────
    y -= 4 * mm
    y = _section_caption(c, y, "INFORMATION FOR CANDIDATES")
    c.setFont("UI", 10.5)
    for line in cfg["information"]:
        for k, seg in enumerate(simpleSplit(line, "UI", 10.5, avail)):
            c.setFillColor(INK)
            if k == 0:
                c.drawString(MX, y, "•")
            c.drawString(MX + 7 * mm, y, seg)
            y -= 5.4 * mm
        y -= 0.8 * mm

    # ── examiner mark grid ──────────────────────────────────────────────────
    y -= 5 * mm
    y = _section_caption(c, y, "FOR EXAMINER'S USE ONLY  —  ENTER THE MARK FOR EACH PART IN THE BOTTOM ROW")
    cols = []
    for p in parts:
        if p["kind"] == "speaking":
            # break the speaking card down by block so the examiner can record each
            cols += [(b["title"].split(" ·")[0], b["marks"]) for b in p["blocks"]]
        else:
            cols.append((p["roman"].replace("Part ", ""), len(_part_items(p))))
    cols.append(("TOTAL", sum(n for _, n in cols)))
    gw = (PAGE_W - 2 * MX) / len(cols)
    top, rh = y, 7 * mm
    for r in range(3):
        _hrule(c, top - r * rh, 0.5)
    _hrule(c, top - 3 * rh, 0.5)
    for i, (name, marks) in enumerate(cols):
        gx = MX + i * gw
        c.setStrokeColor(RULE)
        c.setLineWidth(0.4)
        c.line(gx, top - 3 * rh, gx, top)
        bold = i == len(cols) - 1
        c.setFont("UI-Semibold" if bold else "UI-Semibold", 9)
        c.setFillColor(INK if bold else MUTED)
        c.drawCentredString(gx + gw / 2, top - 4.8 * mm, name)
        c.setFont("UI", 9)
        c.setFillColor(MUTED)
        c.drawCentredString(gx + gw / 2, top - rh - 4.8 * mm, f"/ {marks}")
    c.line(PAGE_W - MX, top - 3 * rh, PAGE_W - MX, top)

    # ── do not open — anchored to the page foot, clear of the footer line ───
    warn_h, warn_y = 11 * mm, 17 * mm
    c.setFillColor(INK)
    c.rect(MX, warn_y, PAGE_W - 2 * MX, warn_h, stroke=0, fill=1)
    _tracked(c, PAGE_W / 2, warn_y + 4 * mm, cfg["warning"], "UI-Bold", 10, white, tracking=2)

    c.setFont("UI", 8)
    c.setFillColor(MUTED)
    c.drawString(MX, 10 * mm, cfg["exam_id"])
    c.drawRightString(PAGE_W - MX, 10 * mm, f"Examiner: {cfg['instructor']}")


# ── answer sheets — 3 columns x 15 rows, split across 2 pages ───────────────

BUBBLE_R = 3.2 * mm
ROW_H = 11 * mm
COL_X = (30 * mm, 88 * mm, 146 * mm)
BUBBLE_DX = 11 * mm
BUBBLE_X0 = 8 * mm
HEADER_BOTTOM = PAGE_H - 56 * mm   # y returned by _sheet_header
BOTTOM_LIMIT = 30 * mm             # keeps the last row clear of the score box


def _written_box_h(n, cols=4):
    return 12 * mm + ((n + cols - 1) // cols) * 11 * mm


def _rows_that_fit(grid_top):
    return int((grid_top - BOTTOM_LIMIT) / ROW_H) + 1


def _plan_sheets(bubbled, written):
    """Split the bubbled questions across sheets. Sheet A also carries the
    write-in gap box, so it holds fewer rows than the sheets after it."""
    top_a = HEADER_BOTTOM - ((_written_box_h(len(written)) + 8 * mm) if written else 0) - 6 * mm
    top_b = HEADER_BOTTOM - 6 * mm
    cap_a, cap_b = _rows_that_fit(top_a) * len(COL_X), _rows_that_fit(top_b) * len(COL_X)

    n = len(bubbled)
    if n <= cap_a + cap_b:                       # two sheets — split as evenly as caps allow
        n_a = min(cap_a, -(-n // 2))
        counts = [n_a, n - n_a]
    else:                                        # spill onto further sheets
        counts, rest = [cap_a], n - cap_a
        while rest > 0:
            counts.append(min(cap_b, rest))
            rest -= counts[-1]

    sheets, i = [], 0
    for k, cnt in enumerate(counts):
        top = top_a if k == 0 else top_b
        rows = min(_rows_that_fit(top), -(-cnt // len(COL_X)))   # balance the columns
        sheets.append((bubbled[i:i + cnt], top, rows))
        i += cnt
    return sheets


def _sheet_header(c, cfg, label):
    _corner_markers(c)
    _tracked(c, PAGE_W / 2, PAGE_H - 23 * mm, "ANSWER SHEET", "UI-Bold", 18, INK, tracking=3)
    c.setFont("UI", 8.5)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 29 * mm,
                        f"{cfg['title'].upper()}  ·  {cfg['exam_id']}  ·  "
                        f"{cfg['instructor'].upper()}  ·  LEVEL {cfg['level']}  ·  {label}")

    by = PAGE_H - 40 * mm
    c.setFont("UI-Semibold", 9.5)
    c.setFillColor(INK)
    c.drawString(26 * mm, by, "NAME")
    c.setStrokeColor(INK)
    c.setLineWidth(0.6)
    c.line(40 * mm, by - 0.5, 118 * mm, by - 0.5)
    c.drawString(126 * mm, by, "DATE")
    c.line(138 * mm, by - 0.5, PAGE_W - 26 * mm, by - 0.5)

    iy = PAGE_H - 48 * mm
    c.setFont("UI", 9)
    c.setFillColor(INK)
    lead = "Fill ONE bubble completely with a dark pen or pencil.   Correct:"
    c.drawString(26 * mm, iy, lead)
    ex_x = 26 * mm + c.stringWidth(lead, "UI", 9) + 5 * mm
    c.setFillColor(black)
    c.circle(ex_x, iy + 1.1 * mm, 2.4 * mm, stroke=0, fill=1)
    c.setFillColor(INK)
    c.drawString(ex_x + 6 * mm, iy, "Wrong:")
    _bubble(c, ex_x + 20 * mm, iy + 1.1 * mm, "", r=2.4 * mm)
    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    c.line(ex_x + 18.5 * mm, iy - 0.4 * mm, ex_x + 21.5 * mm, iy + 2.6 * mm)
    return iy - 8 * mm


def _written_box(c, y, written):
    """Write-in lines for the hand-marked listening gaps."""
    pad = 5 * mm
    cols = 4
    rows = (len(written) + cols - 1) // cols
    box_h = _written_box_h(len(written), cols)
    box_y = y - box_h
    c.setFillColor(TINT)
    c.roundRect(MX, box_y, PAGE_W - 2 * MX, box_h, 3 * mm, stroke=0, fill=1)
    _tracked(c, MX + pad, box_y + box_h - 7 * mm, "LISTENING · WRITE YOUR ANSWERS",
             "UI-Semibold", 8, ACCENT, tracking=1.8, centered=False)

    col_w = (PAGE_W - 2 * MX - 2 * pad) / cols
    for i, q in enumerate(written):
        r, col = i // cols, i % cols
        cx = MX + pad + col * col_w
        cy = box_y + box_h - 15 * mm - r * 11 * mm
        c.setFillColor(INK)
        c.setFont("UI-Semibold", 10)
        c.drawString(cx, cy, f"{q}.")
        c.setStrokeColor(INK)
        c.setLineWidth(0.6)
        c.line(cx + 6 * mm, cy - 0.8 * mm, cx + col_w - 5 * mm, cy - 0.8 * mm)
    return box_y - 8 * mm


def _grid(c, cfg, questions, grid_top, tf_rows, rows_per_col):
    for idx, q in enumerate(questions):
        col, row = idx // rows_per_col, idx % rows_per_col
        x_num = COL_X[col]
        cy = grid_top - row * ROW_H
        if row % 5 == 0 and row > 0:
            c.setStrokeColor(RULE)
            c.setLineWidth(0.3)
            c.line(x_num - 7 * mm, cy + ROW_H / 2 + 1.2 * mm,
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


def _answer_sheets(c, cfg, total_q, page):
    tf_rows = set(cfg.get("tf_rows", []))
    written = sorted(cfg.get("written_rows", []))
    bubbled = [q for q in range(1, total_q + 1) if q not in set(written)]
    sheets = _plan_sheets(bubbled, written)

    for s, (questions, grid_top, rows) in enumerate(sheets):
        label = f"SHEET {chr(65 + s)} OF {len(sheets)}"
        y = _sheet_header(c, cfg, label)
        if s == 0 and written:
            y = _written_box(c, y, written)
        _grid(c, cfg, questions, grid_top, tf_rows, rows)

        # sits between the two bottom corner markers, clear of the last bubble row
        c.setFillColor(CARD)
        c.roundRect(PAGE_W / 2 - 26 * mm, 12 * mm, 52 * mm, 10 * mm, 3 * mm, stroke=0, fill=1)
        _tracked(c, PAGE_W / 2, 18.5 * mm, "TEACHER ONLY", "UI-Semibold", 6.5, MUTED, tracking=2)
        c.setFont("UI-Semibold", 10.5)
        c.setFillColor(INK)
        c.drawCentredString(PAGE_W / 2, 13.8 * mm,
                            f"{label}          /  {len(questions)}")
        # no footer — text near the corner markers confuses OMR alignment
        c.showPage()
        page[0] += 1


# ── answer key ──────────────────────────────────────────────────────────────

def _answer_key(c, cfg, page):
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1)
    c.line(MX, PAGE_H - 14 * mm, PAGE_W - MX, PAGE_H - 14 * mm)
    _tracked(c, PAGE_W / 2, PAGE_H - 22 * mm, "TEACHER ANSWER KEY", "UI-Bold", 14, ACCENT, tracking=2)
    c.setFont("UI", 9.5)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 28 * mm,
                        f"{cfg['exam_id']} — detach before handing out.")

    y = PAGE_H - 38 * mm
    spread = {"a": 0, "b": 0, "c": 0, "d": 0}

    for part in cfg["parts"]:
        items = _part_items(part)
        if not items:
            continue
        if y < 40 * mm:
            _footer(c, cfg, page[0])
            c.showPage()
            page[0] += 1
            y = PAGE_H - 25 * mm

        nums = f"({items[0]['num']}–{items[-1]['num']})"
        label = part["label"]
        c.setFont("UI-Semibold", 11)
        c.setFillColor(INK)
        c.drawString(MX, y, f"{part['roman']} — {label}  {nums}")
        c.setStrokeColor(RULE)
        c.setLineWidth(0.3)
        c.line(MX, y - 2.5 * mm, PAGE_W - MX, y - 2.5 * mm)
        y -= 8 * mm

        kind = part["kind"]
        per_row = 4 if kind == "gap" else 5
        col_w = (PAGE_W - 2 * MX) / per_row
        c.setFont("UI", 10)
        c.setFillColor(INK)
        for i, it in enumerate(items):
            col, row = i % per_row, i // per_row
            if kind == "story" or (kind == "passage" and "statements" in part):
                txt = f"{it['num']}.  {'T' if it['answer'] else 'F'}"
            elif kind == "gap":
                txt = f"{it['num']}.  {it['answer']}"
            elif kind == "picture":
                txt = f"{it['num']}.  {it['answer']})  {it['options']['abcd'.index(it['answer'])]}"
            else:
                txt = f"{it['num']}.  {it['answer']})"
            if kind not in ("gap", "story") and it.get("answer") in spread:
                spread[it["answer"]] += 1
            c.drawString(MX + col * col_w, y - row * 6 * mm, txt)
        y -= ((len(items) + per_row - 1) // per_row) * 6 * mm + 8 * mm

    y -= 2 * mm
    c.setFont("UI-Semibold", 9.5)
    c.setFillColor(MUTED)
    c.drawString(MX, y, "ANSWER SPREAD   " + "    ".join(
        f"{k}) {v}" for k, v in spread.items()))
    _footer(c, cfg, page[0])


# ── main ────────────────────────────────────────────────────────────────────

RENDERERS = {
    "picture": lambda c, cfg, p, page, db: _picture_part(c, cfg, p, db, page),
    "mcq": lambda c, cfg, p, page, db: _mcq_part(c, cfg, p, page),
    "gap": lambda c, cfg, p, page, db: _gap_part(c, cfg, p, page),
    "passage": lambda c, cfg, p, page, db: _passage_part(c, cfg, p, page),
    "story": lambda c, cfg, p, page, db: _story_part(c, cfg, p, page),
    "speaking": lambda c, cfg, p, page, db: _speaking_part(c, cfg, p, page),
}


def _render(cfg, db, total_pages):
    parts = cfg["parts"]
    written_total = sum(len(_part_items(p)) for p in parts if p["kind"] != "speaking")
    speaking = next((p for p in parts if p["kind"] == "speaking"), None)
    speaking_marks = speaking["marks"] if speaking else 0

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"{cfg['title']} {cfg['exam_id']} — {cfg['instructor']}")

    _cover(c, cfg, written_total, speaking_marks, parts, total_pages)
    c.showPage()

    page = [2]
    for part in parts:
        RENDERERS[part["kind"]](c, cfg, part, page, db)

    # a speaking-only paper is rubric-marked: no sheets to bubble, no key to print
    if written_total:
        _answer_sheets(c, cfg, written_total, page)
        _answer_key(c, cfg, page)

    c.save()
    # page[0] is the NEXT page number. The answer key is the only block that
    # doesn't end with showPage(), so it leaves the counter on the real last page.
    return buf.getvalue(), page[0] if written_total else page[0] - 1


def generate(cfg_path: str) -> bytes:
    _register_fonts()
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)

    db = SessionLocal()
    # Pass 1 establishes the page count; pass 2 prints it on the cover. The count
    # is stable because the cover is exactly one page either way.
    _, pages = _render(cfg, db, None)
    pdf, _ = _render(cfg, db, pages)
    db.close()
    return pdf


def main():
    args = sys.argv[1:]
    cfg_path = "tools/exam_b1_final.json"
    out_path = "exports/Final_Exam_B1.pdf"
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
