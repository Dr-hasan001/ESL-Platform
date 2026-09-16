"""
Mark one B1 final answer sheet against tools/exam_b1_final.json.

Reads  Books/Answers_B1_Final/<CLASS>/<Student>/reads.json
Writes ...                    /<Student>/result.json
and prints a per-part breakdown plus every wrong answer.

Questions 1-8 are the hand-marked listening gaps: they are reported for the
teacher's convenience but are NOT included in the machine score.

Run: py tools/mark_b1_final.py "PM91/Nasser Haider"
     py tools/mark_b1_final.py --all PM91
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from tools.grade_bubble_sheets import build_key

BASE = os.path.join(ROOT, "Books", "Answers_B1_Final")
CONFIG = os.path.join(HERE, "exam_b1_final.json")
GAPS = os.path.join(BASE, "gap_scores.json")


def gap_score_for(rel_path, sheet):
    """Teacher-marked Q1-8 score. gap_scores.json is the source of truth; a
    gaps_score inside the student's own reads.json is the fallback."""
    if os.path.exists(GAPS):
        with open(GAPS, encoding="utf-8") as f:
            table = json.load(f)
        if rel_path.replace("\\", "/") in table:
            return table[rel_path.replace("\\", "/")]
    return sheet.get("gaps_score")

PARTS = {
    "I  Listening gaps":    range(1, 9),
    "II  Listening MCQ":    range(9, 21),
    "III Pictures":         range(21, 31),
    "IV  Definitions":      range(31, 41),
    "V   Passage T/F":      range(41, 51),
    "VI  Passage MCQ":      range(51, 61),
    "VII Grammar":          range(61, 101),
}
HAND_MARKED = range(1, 9)


def mark(rel_path):
    folder = os.path.join(BASE, rel_path)
    with open(os.path.join(folder, "reads.json"), encoding="utf-8") as f:
        sheet = json.load(f)
    with open(CONFIG, encoding="utf-8") as f:
        key = build_key(json.load(f))

    answers = {str(k): (v or "").strip().lower() for k, v in sheet["answers"].items()}

    machine = [q for q in range(1, 101) if q not in HAND_MARKED]
    missing = [q for q in machine if str(q) not in answers]
    if missing:
        raise SystemExit(f"reads.json is missing questions: {missing}")

    wrong, blank, correct = [], [], 0
    for q in machine:
        got, want = answers[str(q)], key[str(q)]
        if not got:
            blank.append(q)
        elif got == want:
            correct += 1
        else:
            wrong.append((q, got, want))

    total = len(machine)
    print(f"\n{sheet['student']}   ({sheet['class']}  ·  {sheet['exam']})")
    print("=" * 62)
    for name, rng in PARTS.items():
        qs = [q for q in rng if q not in HAND_MARKED]
        if not qs:
            print(f"  {name:<22}      —      hand-marked by teacher")
            continue
        got = sum(1 for q in qs if answers[str(q)] == key[str(q)])
        bar = "█" * round(10 * got / len(qs)) + "·" * (10 - round(10 * got / len(qs)))
        print(f"  {name:<22} {got:>3} / {len(qs):<3}  {bar}")

    print("-" * 62)
    pct = 100 * correct / total
    gaps = gap_score_for(rel_path, sheet)   # set once the teacher has marked Q1-8
    print(f"  MACHINE SCORE          {correct:>3} / {total}   ({pct:.0f}%)")
    if gaps is None:
        print(f"  hand-marked gaps 1-8     ? / 8    <- add these for the /100")
    else:
        print(f"  hand-marked gaps 1-8   {gaps:>3} / 8    (marked on the paper)")
        print(f"  FINAL                  {correct + gaps:>3} / 100")
    print(f"  blank / not answered   {len(blank):>3}" + (f"   {blank}" if blank else ""))

    if wrong:
        print(f"\n  WRONG ({len(wrong)}):")
        for i in range(0, len(wrong), 6):
            print("    " + "   ".join(f"{q}:{g or '-'}->{w}" for q, g, w in wrong[i:i + 6]))

    print("\n  Gaps 1-8 as written (mark by hand):")
    for q, txt in sorted(sheet.get("gaps_written", {}).items(), key=lambda kv: int(kv[0])):
        print(f"    {q}. {txt}")

    result = {
        "student": sheet["student"], "class": sheet["class"], "exam": sheet["exam"],
        "machine_score": correct, "machine_total": total, "percent": round(pct, 1),
        "blank": blank,
        "wrong": [{"q": q, "got": g, "correct": w} for q, g, w in wrong],
        "by_part": {n: sum(1 for q in r if q not in HAND_MARKED
                           and answers[str(q)] == key[str(q)]) for n, r in PARTS.items()},
        "gaps_written": sheet.get("gaps_written", {}),
        "gaps_score": gaps,
        "final_score": (correct + gaps) if gaps is not None else None,
    }
    out = os.path.join(folder, "result.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n  saved -> {os.path.relpath(out, ROOT)}")
    return result


def main():
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    if args[0] == "--all":
        cls = args[1]
        for name in sorted(os.listdir(os.path.join(BASE, cls))):
            if os.path.exists(os.path.join(BASE, cls, name, "reads.json")):
                mark(f"{cls}/{name}")
    else:
        mark(args[0])


if __name__ == "__main__":
    main()
