"""
One-page grades-only PDF (big font): student name + score, ranked.
Reads .tmp/bubble_results_<class>.json produced by grade_bubble_sheets.py.

Run: py tools/generate_grades_pdf.py [pm91|pm82]
"""

import json
import os
import sys

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

PAGE_W, PAGE_H = A4
INK = HexColor("#1A1209")
ACCENT = HexColor("#8B1F12")
MUTED = HexColor("#7A6E63")
RULE = HexColor("#C9BFB4")
GOLD = HexColor("#B08D3E")

CLASS_LABEL = {"pm91": "PM 91", "pm82": "PM 82"}


def main():
    cls = sys.argv[1] if len(sys.argv) > 1 else "pm91"
    label = CLASS_LABEL.get(cls, cls.upper())
    out = os.path.join(ROOT, "exports", f"Exam_B3_U6-10_Grades_{cls.upper()}.pdf")

    with open(os.path.join(ROOT, ".tmp", f"bubble_results_{cls}.json"), encoding="utf-8") as f:
        results = json.load(f)["results"]          # already sorted by score desc

    c = canvas.Canvas(out, pagesize=A4)
    c.setTitle(f"Exam Results — {label} — B3 U6-10")

    c.setStrokeColor(INK)
    c.setLineWidth(1.2)
    c.line(18 * mm, PAGE_H - 16 * mm, PAGE_W - 18 * mm, PAGE_H - 16 * mm)
    c.setFont("Times-Bold", 30)
    c.setFillColor(INK)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 30 * mm, "EXAM  RESULTS")
    c.setFont("Times-Bold", 16)
    c.setFillColor(ACCENT)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 39 * mm, f"Class {label}")
    c.setFont("Times-Italic", 12)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 46 * mm,
                        "Level B1  ·  Book 3, Units 6–10  ·  Instructor: Hasan Alaa")
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.7)
    c.line(60 * mm, PAGE_H - 51 * mm, PAGE_W - 60 * mm, PAGE_H - 51 * mm)

    top = PAGE_H - 64 * mm
    row_h = 15.5 * mm
    for i, r in enumerate(results):
        y = top - i * row_h
        c.setFont("Times-Bold", 18)
        c.setFillColor(INK)
        c.drawString(24 * mm, y, r["name"])
        c.setFont("Times-Bold", 20)
        c.setFillColor(ACCENT)
        c.drawRightString(PAGE_W - 24 * mm, y, f"{r['total']} / 40")
        c.setStrokeColor(RULE)
        c.setLineWidth(0.4)
        c.line(24 * mm, y - 4.5 * mm, PAGE_W - 24 * mm, y - 4.5 * mm)

    c.setStrokeColor(INK)
    c.setLineWidth(1.2)
    c.line(18 * mm, 16 * mm, PAGE_W - 18 * mm, 16 * mm)
    c.setFont("Helvetica", 8)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, 11.5 * mm, f"EXAM · B3 U6-10 · CLASS {label.upper()} · HASAN ALAA")

    c.save()
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
