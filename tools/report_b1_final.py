"""
Class report for the B1 final exam.

Reads every Books/Answers_B1_Final/<CLASS>/<Student>/result.json, prints a
ranked table per class with the per-part breakdown, class averages, and the
questions the cohort found hardest. Writes a CSV per class for the gradebook.

Run: py tools/report_b1_final.py
"""

import csv
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BASE = os.path.join(ROOT, "Books", "Answers_B1_Final")
EXPORTS = os.path.join(ROOT, "exports")

PARTS = [
    ("II  Listen", "II  Listening MCQ", 12),
    ("III Pics",   "III Pictures", 10),
    ("IV  Defs",   "IV  Definitions", 10),
    ("V   T/F",    "V   Passage T/F", 10),
    ("VI  Psg",    "VI  Passage MCQ", 10),
    ("VII Gram",   "VII Grammar", 40),
]


def load(cls):
    out = []
    d = os.path.join(BASE, cls)
    if not os.path.isdir(d):
        return out
    for name in sorted(os.listdir(d)):
        p = os.path.join(d, name, "result.json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                out.append(json.load(f))
    return out


def table(cls, rows):
    rows = sorted(rows, key=lambda r: -r["machine_score"])
    w = max(len(r["student"]) for r in rows)
    head = f"  {'#':<3}{'STUDENT':<{w}}  {'/92':>4} {'%':>4}  " + "  ".join(
        f"{s:>9}" for s, _, _ in PARTS) + "   FINAL"
    print(f"\n{'=' * len(head)}\n  {cls}   —   {len(rows)} students\n{'=' * len(head)}")
    print(head)
    print("  " + "-" * (len(head) - 2))

    for i, r in enumerate(rows, 1):
        cells = []
        for _, key, mx in PARTS:
            cells.append(f"{r['by_part'][key]:>4} /{mx:<4}")
        nblank = len(r["blank"])
        final = r.get("final_score")
        fin = f"{final:>3}/100" if final is not None else ("  —  " if not nblank else "  —  ")
        warn = f"  <- {nblank} blank" if nblank >= 5 else ""
        print(f"  {i:<3}{r['student']:<{w}}  {r['machine_score']:>4} {r['percent']:>4.0f}  "
              + "  ".join(cells) + f"   {fin}{warn}")

    print("  " + "-" * (len(head) - 2))
    n = len(rows)
    avg = sum(r["machine_score"] for r in rows) / n
    cells = []
    for _, key, mx in PARTS:
        cells.append(f"{sum(r['by_part'][key] for r in rows) / n:>4.1f}/{mx:<4}")
    print(f"  {'':<3}{'CLASS AVERAGE':<{w}}  {avg:>4.1f} {100*avg/92:>4.0f}  " + "  ".join(cells))
    return rows


def hardest(all_rows, top=12):
    misses = Counter()
    for r in all_rows:
        for wnew in r["wrong"]:
            misses[wnew["q"]] += 1
        for q in r["blank"]:
            misses[q] += 1
    n = len(all_rows)
    print(f"\n  HARDEST QUESTIONS  (missed by, out of {n} students)")
    print("  " + "-" * 46)
    for q, c in misses.most_common(top):
        bar = "█" * round(20 * c / n)
        print(f"    Q{q:<4} {c:>2}/{n}  {bar}")


def write_csv(cls, rows):
    os.makedirs(EXPORTS, exist_ok=True)
    path = os.path.join(EXPORTS, f"B1_Final_Results_{cls}.csv")
    cols = ["Rank", "Student", "Machine/92", "Percent"] + [k for _, k, _ in PARTS] \
        + ["Gaps/8", "Final/100", "Blank", "Notes"]
    try:
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            wr = csv.writer(f)
            wr.writerow(cols)
            for i, r in enumerate(rows, 1):
                nb = len(r["blank"])
                wr.writerow([i, r["student"], r["machine_score"], r["percent"]]
                            + [r["by_part"][k] for _, k, _ in PARTS]
                            + [r.get("gaps_score", ""), r.get("final_score", ""), nb,
                               "INCOMPLETE" if nb >= 5 else ""])
        print(f"\n  CSV -> {os.path.relpath(path, ROOT)}")
    except PermissionError:
        print(f"\n  CSV skipped (file open in Excel?): {os.path.relpath(path, ROOT)}")


def main():
    everyone = []
    for cls in ("PM91", "PM82"):
        rows = load(cls)
        if not rows:
            continue
        rows = table(cls, rows)
        write_csv(cls, rows)
        everyone += rows

    if everyone:
        print(f"\n{'=' * 60}\n  BOTH CLASSES  —  {len(everyone)} students\n{'=' * 60}")
        avg = sum(r["machine_score"] for r in everyone) / len(everyone)
        print(f"  overall average   {avg:.1f} / 92   ({100*avg/92:.0f}%)")
        for _, key, mx in PARTS:
            a = sum(r["by_part"][key] for r in everyone) / len(everyone)
            bar = "█" * round(20 * a / mx)
            print(f"    {key:<20} {a:>4.1f}/{mx:<3} {100*a/mx:>4.0f}%  {bar}")
        hardest(everyone)


if __name__ == "__main__":
    main()
