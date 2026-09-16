"""
Answer-review PDF — every student's sheet, replayed on paper.

For each student: a full answer grid where the chosen letter is marked, a red X
is struck through every WRONG choice, and the correct letter is ringed in green.
Underneath, each missed question is written out (prompt, what they picked, what
was right). Front matter carries the ranked class table, the missed-question
numbers per student, and a per-question difficulty analysis.

Sources
    reads   .tmp/bubble_reads*.json      (via CLASSES in grade_bubble_sheets)
    key     tools/exam_*.json            (both legacy part1..part4 and "parts")

Run: py tools/generate_answer_review_pdf.py [pm91|pm82|pm101|all]
"""

import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

from grade_bubble_sheets import CLASSES, build_key

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

PAGE_W, PAGE_H = A4
MX = 16 * mm                       # side margin
TOP_RULE_Y = PAGE_H - 14 * mm
FOOT_RULE_Y = 15 * mm

INK = HexColor("#1A1209")
ACCENT = HexColor("#8B1F12")
MUTED = HexColor("#7A6E63")
RULE = HexColor("#C9BFB4")
GOLD = HexColor("#B08D3E")
GREEN = HexColor("#2E6B4F")
RED = HexColor("#B3261E")
FAINT = HexColor("#EFEAE3")
PAPER = HexColor("#FBF8F4")

CLASS_META = {
    "pm91":  {"label": "PM 91",  "level": "B1",
              "subtitle": "Level B1  ·  Book 3, Units 6–10  ·  Instructor: Hasan Alaa"},
    "pm82":  {"label": "PM 82",  "level": "B1",
              "subtitle": "Level B1  ·  Book 3, Units 6–10  ·  Instructor: Hasan Alaa"},
    "pm101": {"label": "PM 101", "level": "A1",
              "subtitle": "Level A1  ·  Book 1, Units 6–10  ·  Instructor: Hasan Alaa"},
    "pm101w": {"label": "PM 101", "level": "A1",
               "subtitle": "Weekly Exam  ·  Units 11–15 & Future Simple  ·  "
                           "Instructor: Hasan Alaa"},
    "b1final": {"label": "B1 FINAL", "level": "B1",
                "subtitle": "Level B1  ·  Final Exam  ·  Instructor: Hasan Alaa"},
}

LETTERS = "abcdefgh"


# ---------------------------------------------------------------- exam model

def build_questions(cfg):
    """{num: {kind, prompt, options[(letter,text)], answer, part}} for both schemas."""
    q = {}

    def add_items(part, label):
        for it in part.get("items", []):
            opts = [(LETTERS[i], str(t)) for i, t in enumerate(it.get("options", []))]
            q[str(it["num"])] = {
                "kind": "mcq",
                "prompt": it.get("sentence") or it.get("word") or "",
                "options": opts,
                "answer": str(it["answer"]).lower(),
                "part": label,
            }

    def add_statements(part, label):
        for s in part.get("statements", []):
            q[str(s["num"])] = {
                "kind": "tf",
                "prompt": s.get("text", ""),
                "options": [("t", "True"), ("f", "False")],
                "answer": "t" if s["answer"] else "f",
                "part": label,
            }

    if "parts" in cfg:                                   # A1 / B1 list schema
        for part in cfg["parts"]:
            label = part.get("label", "")
            if part.get("statements"):
                add_statements(part, label)
            else:
                add_items(part, label)
    else:                                                # legacy B3 schema
        for p in ("part1", "part2", "part4"):
            add_items(cfg[p], cfg[p].get("label", ""))
        add_statements(cfg["part3"], cfg["part3"].get("label", ""))
    return q


def load_class(cls):
    spec = CLASSES[cls]
    with open(os.path.join(ROOT, spec["reads"]), encoding="utf-8") as f:
        reads = json.load(f)
    with open(os.path.join(HERE, spec["config"]), encoding="utf-8") as f:
        cfg = json.load(f)
    key = build_key(cfg)
    questions = build_questions(cfg)
    total_q = len(key)

    students = []
    for sheet in reads:
        fname = sheet["file"]
        answers = {str(k): (v or "-").strip().lower() for k, v in sheet["answers"].items()}
        answers.update({q: v.lower() for q, v in spec["overrides"].get(fname, {}).items()})
        missed, blank = [], 0
        for n in range(1, total_q + 1):
            given = answers.get(str(n), "-")
            if given in ("-", "?"):
                blank += 1
            if given != key[str(n)]:
                missed.append(n)
        students.append({
            "name": spec["roster"].get(fname, sheet.get("name_written") or fname),
            "file": fname,
            "answers": answers,
            "missed": missed,
            "blank": blank,
            "total": total_q - len(missed),
            "pct": round((total_q - len(missed)) / total_q * 100),
            "uncertain": sheet.get("uncertain") or [],
        })
    students.sort(key=lambda s: (-s["total"], s["name"]))
    return spec, key, questions, total_q, students


# ------------------------------------------------------------------ drawing

def frame(c, exam, label, page_note=""):
    c.setStrokeColor(INK)
    c.setLineWidth(1.1)
    c.line(MX - 2 * mm, TOP_RULE_Y, PAGE_W - MX + 2 * mm, TOP_RULE_Y)
    c.line(MX - 2 * mm, FOOT_RULE_Y, PAGE_W - MX + 2 * mm, FOOT_RULE_Y)
    c.setFont("Helvetica", 7.2)
    c.setFillColor(MUTED)
    c.drawString(MX - 2 * mm, 10.5 * mm,
                 f"ANSWER REVIEW · {exam.replace('_', ' ')} · CLASS {label.upper()}")
    c.drawRightString(PAGE_W - MX + 2 * mm, 10.5 * mm, page_note or "HASAN ALAA")


def mark(c, cx, cy, letter, state):
    """One option letter. state: plain | picked_ok | picked_wrong | key."""
    w = 6.0 * mm
    h = 6.0 * mm
    x, y = cx - w / 2, cy - h / 2 + 0.6 * mm
    up = letter.upper()

    if state == "picked_ok":
        c.setFillColor(GREEN)
        c.roundRect(x, y, w, h, 1.6 * mm, stroke=0, fill=1)
        c.setFillColor(HexColor("#FFFFFF"))
        c.setFont("Helvetica-Bold", 9)
    elif state == "picked_wrong":
        c.setFillColor(HexColor("#FBE9E7"))
        c.setStrokeColor(RED)
        c.setLineWidth(0.7)
        c.roundRect(x, y, w, h, 1.6 * mm, stroke=1, fill=1)
        c.setFillColor(RED)
        c.setFont("Helvetica-Bold", 9)
    elif state == "key":
        c.setStrokeColor(GREEN)
        c.setLineWidth(0.7)
        c.roundRect(x, y, w, h, 1.6 * mm, stroke=1, fill=0)
        c.setFillColor(GREEN)
        c.setFont("Helvetica-Bold", 9)
    else:
        c.setFillColor(HexColor("#B6ADA3"))
        c.setFont("Helvetica", 8.4)

    c.drawCentredString(cx, cy - 1.1 * mm, up)

    if state == "picked_wrong":                    # the X, struck across the choice
        c.setStrokeColor(RED)
        c.setLineWidth(1.15)
        p = 1.1 * mm
        c.line(x + p, y + p, x + w - p, y + h - p)
        c.line(x + p, y + h - p, x + w - p, y + p)


def legend(c, y):
    items = [("picked_ok", "a", "correct choice"),
             ("picked_wrong", "b", "wrong choice (X)"),
             ("key", "c", "right answer"),
             ("plain", "d", "not chosen")]
    x = MX + 3 * mm
    for state, ltr, text in items:
        mark(c, x, y, ltr, state)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7.4)
        c.drawString(x + 4.6 * mm, y - 2.4 * mm, text)
        x += 4.6 * mm + c.stringWidth(text, "Helvetica", 7.4) + 9 * mm


def student_header(c, s, total_q, continued=False):
    y = PAGE_H - 24 * mm
    c.setFont("Times-Bold", 21)
    c.setFillColor(INK)
    c.drawString(MX, y, s["name"] + (" (cont.)" if continued else ""))

    badge_w, badge_h = 40 * mm, 12 * mm
    bx, by = PAGE_W - MX - badge_w, y - 3.4 * mm
    c.setFillColor(FAINT)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    c.roundRect(bx, by, badge_w, badge_h, 2 * mm, stroke=1, fill=1)
    c.setFillColor(ACCENT)
    c.setFont("Times-Bold", 15)
    c.drawString(bx + 4 * mm, by + 4 * mm, f"{s['total']} / {total_q}")
    c.setFillColor(GOLD)
    c.setFont("Times-Bold", 12)
    c.drawRightString(bx + badge_w - 3.5 * mm, by + 4 * mm, f"{s['pct']}%")

    y -= 7.5 * mm
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.line(MX, y, PAGE_W - MX - badge_w - 4 * mm, y)

    y -= 6 * mm
    c.setFont("Helvetica-Bold", 8.2)
    c.setFillColor(RED if s["missed"] else GREEN)
    c.drawString(MX, y, f"WRONG ({len(s['missed'])}):  " +
                 (", ".join(map(str, s["missed"])) if s["missed"] else "none — full marks"))
    if s["blank"]:
        y -= 4.6 * mm
        c.setFont("Helvetica", 8)
        c.setFillColor(MUTED)
        c.drawString(MX, y, f"left blank: {s['blank']}")
    return y - 7 * mm


def draw_grid(c, s, key, questions, total_q, y_top):
    """Column-major answer grid; wrong picks struck with a red X."""
    cols = 4
    rows = -(-total_q // cols)
    col_w = (PAGE_W - 2 * MX) / cols
    row_h = 11.4 * mm

    for i in range(1, total_q + 1):
        col, row = (i - 1) // rows, (i - 1) % rows
        x0 = MX + col * col_w
        y = y_top - row * row_h

        if row % 2 == 0:
            c.setFillColor(PAPER)
            c.rect(x0, y - 4.2 * mm, col_w - 3 * mm, row_h - 1.4 * mm, stroke=0, fill=1)

        qs = str(i)
        c.setFont("Helvetica-Bold", 8.2)
        c.setFillColor(INK if qs not in map(str, s["missed"]) else RED)
        c.drawRightString(x0 + 7 * mm, y - 1.4 * mm, str(i))

        given = s["answers"].get(qs, "-")
        correct = key[qs]
        opts = [ltr for ltr, _ in questions[qs]["options"]]
        cx = x0 + 12.5 * mm
        for ltr in opts:
            if ltr == given == correct:
                state = "picked_ok"
            elif ltr == given:
                state = "picked_wrong"
            elif ltr == correct:
                state = "key" if given != correct else "plain"
            else:
                state = "plain"
            mark(c, cx, y, ltr, state)
            cx += 7.2 * mm

        if given in ("-", "?"):
            c.setFillColor(MUTED)
            c.setFont("Helvetica-Oblique", 5.8)
            c.drawString(x0 + 12.5 * mm, y - 5.4 * mm,
                         "left blank" if given == "-" else "two bubbles marked")

    return y_top - rows * row_h - 3 * mm


def draw_misses(c, s, key, questions, y, ctx):
    """Written-out list of every missed question. Flows onto extra pages."""
    exam, label, total_q = ctx

    def new_page():
        c.showPage()
        frame(c, exam, label, page_note=s["name"].upper())
        yy = student_header(c, s, total_q, continued=True)
        c.setFont("Times-Bold", 10.5)
        c.setFillColor(ACCENT)
        c.drawString(MX, yy, "WHAT WENT WRONG")
        return yy - 6 * mm

    if not s["missed"]:
        return
    c.setFont("Times-Bold", 10.5)
    c.setFillColor(ACCENT)
    c.drawString(MX, y, "WHAT WENT WRONG")
    y -= 6.5 * mm

    text_w = PAGE_W - 2 * MX - 14 * mm
    for n in s["missed"]:
        qs = str(n)
        q = questions[qs]
        given = s["answers"].get(qs, "-")
        opt_text = dict(q["options"])
        if given == "-":
            mine = "left blank"
        elif given == "?":
            mine = "two bubbles marked, neither crossed out"
        else:
            mine = f"{given.upper()}) {opt_text.get(given, given.upper())}"
        right = f"{key[qs].upper()}) {opt_text.get(key[qs], key[qs].upper())}"
        prompt = simpleSplit(q["prompt"], "Times-Italic", 8.4, text_w)[:1]

        need = 11.5 * mm if prompt else 8 * mm
        if y - need < FOOT_RULE_Y + 8 * mm:
            y = new_page()

        c.setFillColor(RED)
        c.setFont("Helvetica-Bold", 8.4)
        c.drawString(MX, y, f"Q{n}")
        if prompt:
            c.setFillColor(MUTED)
            c.setFont("Times-Italic", 8.4)
            c.drawString(MX + 10 * mm, y, prompt[0])
            y -= 4.6 * mm

        x = MX + 10 * mm
        c.setFillColor(RED)
        c.setFont("Helvetica-Bold", 8.2)
        c.drawString(x, y, "X")
        c.setFont("Helvetica", 8.2)
        c.drawString(x + 4 * mm, y, mine[:64])
        x += 4 * mm + c.stringWidth(mine[:64], "Helvetica", 8.2) + 9 * mm
        c.setFillColor(GREEN)
        c.setFont("Helvetica-Bold", 8.2)
        c.drawString(x, y, "✓")
        c.setFont("Helvetica", 8.2)
        c.drawString(x + 4 * mm, y, right[:64])

        y -= 3 * mm
        c.setStrokeColor(FAINT)
        c.setLineWidth(0.4)
        c.line(MX, y, PAGE_W - MX, y)
        y -= 4.2 * mm


# -------------------------------------------------------------- front matter

def cover(c, cls, meta, exam, students, total_q):
    frame(c, exam, meta["label"])
    c.setFont("Helvetica", 8.6)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 24 * mm, "E X A M   A N S W E R   R E V I E W")
    c.setFont("Times-Bold", 30)
    c.setFillColor(INK)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 36 * mm, f"Class {meta['label']}")
    c.setFont("Times-Italic", 11)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 43 * mm, meta["subtitle"])
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.7)
    c.line(58 * mm, PAGE_H - 48 * mm, PAGE_W - 58 * mm, PAGE_H - 48 * mm)

    n = len(students)
    avg = sum(s["total"] for s in students) / n
    stats = [("students", str(n)),
             ("average", f"{avg:.1f}/{total_q}"),
             ("highest", f"{students[0]['total']}/{total_q}"),
             ("lowest", f"{students[-1]['total']}/{total_q}")]
    bw = (PAGE_W - 2 * MX) / 4
    by = PAGE_H - 70 * mm
    for i, (k, v) in enumerate(stats):
        x = MX + i * bw
        c.setFillColor(PAPER)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.4)
        c.roundRect(x + 1.5 * mm, by, bw - 3 * mm, 16 * mm, 2 * mm, stroke=1, fill=1)
        c.setFillColor(ACCENT)
        c.setFont("Times-Bold", 15)
        c.drawCentredString(x + bw / 2, by + 8.4 * mm, v)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7)
        c.drawCentredString(x + bw / 2, by + 4 * mm, k.upper())

    y = by - 12 * mm
    c.setFont("Helvetica-Bold", 7.6)
    c.setFillColor(MUTED)
    c.drawString(MX, y, "RANK")
    c.drawString(MX + 14 * mm, y, "STUDENT")
    c.drawRightString(PAGE_W - MX - 48 * mm, y, "SCORE")
    c.drawRightString(PAGE_W - MX - 30 * mm, y, "%")
    c.drawRightString(PAGE_W - MX, y, "WRONG")
    y -= 2.4 * mm
    c.setStrokeColor(INK)
    c.setLineWidth(0.6)
    c.line(MX, y, PAGE_W - MX, y)
    y -= 7 * mm

    for i, s in enumerate(students, 1):
        if i % 2 == 1:
            c.setFillColor(PAPER)
            c.rect(MX, y - 2.6 * mm, PAGE_W - 2 * MX, 7.6 * mm, stroke=0, fill=1)
        c.setFillColor(GOLD if i <= 3 else MUTED)
        c.setFont("Times-Bold", 10)
        c.drawString(MX + 1.5 * mm, y, str(i))
        c.setFillColor(INK)
        c.setFont("Times-Roman", 11.5)
        c.drawString(MX + 14 * mm, y, s["name"])
        c.setFillColor(ACCENT)
        c.setFont("Times-Bold", 11.5)
        c.drawRightString(PAGE_W - MX - 48 * mm, y, f"{s['total']}/{total_q}")
        c.setFillColor(INK if s["pct"] >= 50 else RED)
        c.setFont("Times-Bold", 11.5)
        c.drawRightString(PAGE_W - MX - 30 * mm, y, f"{s['pct']}%")
        c.setFillColor(RED if s["missed"] else GREEN)
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(PAGE_W - MX - 1.5 * mm, y, str(len(s["missed"])))
        y -= 7.6 * mm
    c.showPage()


def missed_numbers_page(c, meta, exam, students):
    frame(c, exam, meta["label"])
    c.setFont("Times-Bold", 19)
    c.setFillColor(INK)
    c.drawString(MX, PAGE_H - 26 * mm, "Wrong-answer numbers")
    c.setFont("Times-Italic", 9.5)
    c.setFillColor(MUTED)
    c.drawString(MX, PAGE_H - 32 * mm, "Question numbers each student got wrong.")
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.line(MX, PAGE_H - 35 * mm, PAGE_W - MX, PAGE_H - 35 * mm)

    y = PAGE_H - 44 * mm
    name_w = 44 * mm
    list_w = PAGE_W - 2 * MX - name_w - 4 * mm
    for s in students:
        nums = ", ".join(map(str, s["missed"])) or "none"
        lines = simpleSplit(nums, "Helvetica", 8.6, list_w)
        need = max(12 * mm, len(lines) * 4.6 * mm + 7.5 * mm)
        if y - need < FOOT_RULE_Y + 8 * mm:
            c.showPage()
            frame(c, exam, meta["label"])
            y = PAGE_H - 26 * mm
        c.setFillColor(INK)
        c.setFont("Times-Bold", 10.5)
        c.drawString(MX, y, s["name"])
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7.4)
        c.drawString(MX, y - 4.4 * mm, f"{len(s['missed'])} wrong")
        c.setFillColor(RED if s["missed"] else GREEN)
        c.setFont("Helvetica", 8.6)
        yy = y
        for ln in lines:
            c.drawString(MX + name_w, yy, ln)
            yy -= 4.6 * mm
        y -= need
        c.setStrokeColor(FAINT)
        c.setLineWidth(0.4)
        c.line(MX, y + 2 * mm, PAGE_W - MX, y + 2 * mm)
    c.showPage()


def analysis_page(c, meta, exam, students, key, questions, total_q):
    frame(c, exam, meta["label"])
    c.setFont("Times-Bold", 19)
    c.setFillColor(INK)
    c.drawString(MX, PAGE_H - 26 * mm, "Question analysis")
    c.setFont("Times-Italic", 9.5)
    c.setFillColor(MUTED)
    c.drawString(MX, PAGE_H - 32 * mm,
                 "How many of the class missed each question · key = right answer · "
                 "top wrong = the wrong choice picked most often.")
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.line(MX, PAGE_H - 35 * mm, PAGE_W - MX, PAGE_H - 35 * mm)

    n = len(students)
    wrong_by_q = {}
    for q in range(1, total_q + 1):
        picks = [s["answers"].get(str(q), "-") for s in students
                 if s["answers"].get(str(q), "-") != key[str(q)]]
        wrong_by_q[q] = picks

    order = sorted(range(1, total_q + 1), key=lambda q: (-len(wrong_by_q[q]), q))
    col_w = (PAGE_W - 2 * MX) / 2
    rows = -(-total_q // 2)
    y0 = PAGE_H - 44 * mm
    row_h = 8.6 * mm

    for i, q in enumerate(order):
        col, row = i // rows, i % rows
        x = MX + col * col_w
        y = y0 - row * row_h
        picks = wrong_by_q[q]
        share = len(picks) / n

        if row % 2 == 0:
            c.setFillColor(PAPER)
            c.rect(x, y - 2.4 * mm, col_w - 5 * mm, row_h - 1.2 * mm, stroke=0, fill=1)

        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 8.2)
        c.drawString(x + 1.5 * mm, y, f"Q{q}")

        bar_x, bar_w = x + 11 * mm, 26 * mm
        c.setFillColor(FAINT)
        c.rect(bar_x, y - 0.9 * mm, bar_w, 3.4 * mm, stroke=0, fill=1)
        if share:
            c.setFillColor(RED if share >= 0.5 else GOLD if share >= 0.25 else GREEN)
            c.rect(bar_x, y - 0.9 * mm, bar_w * share, 3.4 * mm, stroke=0, fill=1)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7.4)
        c.drawString(bar_x + bar_w + 2 * mm, y, f"{len(picks)}/{n}")

        c.setFillColor(GREEN)
        c.setFont("Helvetica-Bold", 7.4)
        c.drawString(bar_x + bar_w + 12 * mm, y, f"key {key[str(q)].upper()}")
        if picks:
            common, cnt = Counter(picks).most_common(1)[0]
            c.setFillColor(RED)
            label = {"-": "blank", "?": "2 marked"}.get(common, common.upper())
            c.drawRightString(x + col_w - 7 * mm, y, f"top wrong {label} ×{cnt}")
    c.showPage()


# ---------------------------------------------------------------------- main

def build(cls):
    spec, key, questions, total_q, students = load_class(cls)
    meta = CLASS_META.get(cls, {"label": cls.upper(), "subtitle": "Instructor: Hasan Alaa"})
    exam = spec["exam"]
    out = os.path.join(ROOT, "exports",
                       f"Exam_{exam}_Answer_Review_{cls.upper()}.pdf")
    os.makedirs(os.path.dirname(out), exist_ok=True)

    c = canvas.Canvas(out, pagesize=A4)
    c.setTitle(f"Answer Review — {meta['label']} — {exam.replace('_', ' ')}")
    c.setAuthor("Hasan Alaa")

    cover(c, cls, meta, exam, students, total_q)
    missed_numbers_page(c, meta, exam, students)
    analysis_page(c, meta, exam, students, key, questions, total_q)

    for s in students:
        frame(c, exam, meta["label"], page_note=s["name"].upper())
        y = student_header(c, s, total_q)
        legend(c, y)
        y -= 14 * mm
        y = draw_grid(c, s, key, questions, total_q, y)
        for u in s["uncertain"][:4]:
            c.setFillColor(MUTED)
            c.setFont("Helvetica-Oblique", 7.4)
            c.drawString(MX, y, f"sheet note — Q{u['q']}: {u['note']}")
            y -= 4.4 * mm
        if s["uncertain"]:
            y -= 2 * mm
        draw_misses(c, s, key, questions, y, (exam, meta["label"], total_q))
        c.showPage()

    c.save()
    kb = os.path.getsize(out) / 1024
    print(f"{cls}: {len(students)} students · {total_q} questions · {kb:.0f} KB")
    print(f"  {out}")
    return out


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "pm91"
    targets = [k for k in ("pm91", "pm82", "pm101")] if arg == "all" else [arg]
    for t in targets:
        build(t)


if __name__ == "__main__":
    main()
