"""
Grade photographed bubble sheets for an MCQ exam. Multi-class.

Inputs per class:
    .tmp/bubble_reads_<class>.json — list of {file, name_written, answers{1..40}, uncertain[]}
    tools/exam_b3_u6-10_mcq.json   — answer key source
    CLASSES below                  — roster (file -> official name) + teacher overrides

Outputs per class:
    .tmp/bubble_results_<class>.json
    exports/Exam_B3_U6-10_Results_<CLASS>.csv   (falls back to _v2 if locked by Excel)
    printed per-student scores + per-question analysis

Run: py tools/grade_bubble_sheets.py [pm91|pm82]
"""

import csv
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONFIG = os.path.join(HERE, "exam_b3_u6-10_mcq.json")

CLASSES = {
    "pm91": {
        "roster": {
            "Aqeel Abdul alrazaq.jpg":     "Aqeel Abdul-Razaq",
            "Aya Sabah.jpg":               "Aya Sabah",
            "Baneen Raad.jpg":             "Baneen Raad",
            "Fatima Abdul mutalib.jpg":    "Fatima Abdu-Mutalib",
            "Fatima Hassan.jpg":           "Fatima Hassan",
            "Hussain Ali Abdul-ameer.jpg": "Hussein Ali Abdu-Ameer",
            "Hussain Ali Adnan.jpg":       "Hussein Ali Adnan",
            "Mohammed Reda.jpg":           "Mohammed Reda",
            "Mortadha.jpg":                "Mortdha Khaled",
            "Nasser Haider.jpg":           "Nasser Haider",
            "Raghad.jpg":                  "Raghad Moafak",
            "Ruqya Mazin.jpg":             "Ruqya Mazin",
        },
        # Teacher-confirmed corrections: file -> {question: answer}
        "overrides": {
            "Aqeel Abdul alrazaq.jpg": {"5": "a"},
            # Q40 answered correctly on the question paper, bubble not filled
            "Baneen Raad.jpg": {"40": "c"},
        },
        "reads": ".tmp/bubble_reads.json",       # original PM 91 reads file
    },
    "pm82": {
        "roster": {
            "Baneen Ali.jpg":        "Baneen Ali",
            "Faisal Ghazi.jpg":      "Faisal Ghazi",
            "Haider Widad.jpg":      "Haider Widad",
            "Mohammed Abdullah.jpg": "Mohammed Abdullah",
            "Muna Ibrahim.jpg":      "Muna Ibrahim",
            "Sajad Ahmed.jpg":       "Sajad Ahmed",
            "Sajad Salah.jpg":       "Sajad Salah",
            "Thulfiqar Rashid.jpg":  "Thulfiqar Rashid",
            "Yassir Kamil.jpg":      "Yassir Kamil",
            "Zain.jpg":              "Zain",
            "Zuha.jpg":              "Zuha Fadhil",
        },
        "overrides": {},
        "reads": ".tmp/bubble_reads_pm82.json",
    },
}

PARTS = {"I": range(1, 11), "II": range(11, 21), "III": range(21, 31), "IV": range(31, 41)}


def build_key(cfg):
    key = {}
    for p in ("part1", "part2", "part4"):
        for it in cfg[p]["items"]:
            key[str(it["num"])] = it["answer"].lower()
    for s in cfg["part3"]["statements"]:
        key[str(s["num"])] = "t" if s["answer"] else "f"
    return key


def grade_class(cls: str):
    spec = CLASSES[cls]
    with open(os.path.join(ROOT, spec["reads"]), encoding="utf-8") as f:
        reads = json.load(f)
    with open(CONFIG, encoding="utf-8") as f:
        cfg = json.load(f)
    key = build_key(cfg)
    assert len(key) == 40

    results = []
    q_wrong = {str(q): [] for q in range(1, 41)}

    for sheet in reads:
        fname = sheet["file"]
        name = spec["roster"].get(fname, sheet.get("name_written") or fname)
        answers = {str(k): (v or "-").strip().lower() for k, v in sheet["answers"].items()}
        for q, v in spec["overrides"].get(fname, {}).items():
            answers[q] = v.lower()

        per_part = {p: 0 for p in PARTS}
        missed = []
        blank = 0
        for q in range(1, 41):
            qs = str(q)
            given = answers.get(qs, "-")
            if given in ("-", "?"):
                blank += 1
            if given == key[qs]:
                for p, rng in PARTS.items():
                    if q in rng:
                        per_part[p] += 1
            else:
                missed.append(q)
                q_wrong[qs].append(given)
        total = sum(per_part.values())
        results.append({
            "name": name, "file": fname, "total": total,
            "pct": round(total / 40 * 100),
            **{f"part_{p}": n for p, n in per_part.items()},
            "missed": missed, "blank": blank,
            "uncertain": sheet.get("uncertain") or [],
        })

    results.sort(key=lambda r: -r["total"])

    with open(os.path.join(ROOT, ".tmp", f"bubble_results_{cls}.json"), "w", encoding="utf-8") as f:
        json.dump({"results": results, "q_wrong": q_wrong, "key": key, "class": cls}, f, indent=1)

    out_csv = os.path.join(ROOT, "exports", f"Exam_B3_U6-10_Results_{cls.upper()}.csv")
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    try:
        f = open(out_csv, "w", newline="", encoding="utf-8-sig")
    except PermissionError:                        # open in Excel — use a fresh name
        out_csv = out_csv.replace(".csv", "_v2.csv")
        f = open(out_csv, "w", newline="", encoding="utf-8-sig")
    with f:
        w = csv.writer(f)
        w.writerow(["Student", "Score /40", "%", "Part I /10", "Part II /10",
                    "Part III /10", "Part IV /10", "Blank", "Missed questions"])
        for r in results:
            w.writerow([r["name"], r["total"], r["pct"], r["part_I"], r["part_II"],
                        r["part_III"], r["part_IV"], r["blank"],
                        " ".join(map(str, r["missed"]))])

    print(f"=== {cls.upper()} — STUDENTS (sorted) ===")
    for r in results:
        u = f"  UNCERTAIN:{[x['q'] for x in r['uncertain']]}" if r["uncertain"] else ""
        print(f"{r['name']:26s} {r['total']:2d}/40 ({r['pct']:3d}%)  "
              f"I:{r['part_I']:2d} II:{r['part_II']:2d} III:{r['part_III']:2d} IV:{r['part_IV']:2d}"
              f"  missed: {','.join(map(str, r['missed'])) or 'none'}{u}")

    n = len(results)
    avg = sum(r["total"] for r in results) / n
    print(f"\nclass size {n} · average {avg:.1f}/40 ({avg/40*100:.0f}%) · "
          f"top {results[0]['total']} · low {results[-1]['total']}")

    print(f"\n=== {cls.upper()} — HARDEST QUESTIONS ===")
    for q, wrongs in sorted(q_wrong.items(), key=lambda kv: -len(kv[1])):
        if len(wrongs) >= 2:
            common = Counter(wrongs).most_common(1)[0]
            print(f"Q{q:>2}: {len(wrongs):2d}/{n} wrong (correct={key[q]}, "
                  f"most common wrong: {common[0]} x{common[1]})")
    print(f"\nCSV: {out_csv}")


if __name__ == "__main__":
    grade_class(sys.argv[1] if len(sys.argv) > 1 else "pm91")
