"""
Merge per-unit story JSONs (tools/book3_stories/unitNN.json) into
tools/stories_book3.json — the format seed_stories.py expects — with
validation. Only complains; never guesses or repairs content.

Run: py tools/merge_book3_stories.py
"""

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(HERE, "book3_stories")
OUT = os.path.join(HERE, "stories_book3.json")

merged = {}
problems = []

for path in sorted(glob.glob(os.path.join(SRC_DIR, "unit*.json"))):
    name = os.path.basename(path)
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except Exception as e:
        problems.append(f"{name}: unreadable JSON ({e})")
        continue

    un = d.get("unit")
    title = d.get("title") or ""
    html = d.get("story_html") or ""
    qs = d.get("questions") or []

    if not isinstance(un, int) or not (1 <= un <= 30):
        problems.append(f"{name}: bad unit field {un!r}")
        continue
    if not title:
        problems.append(f"{name}: missing title")
    if "<p>" not in html:
        problems.append(f"{name}: story_html has no <p> paragraphs")
    n_spans = len(re.findall(r'<span class="vocab">', html))
    if n_spans < 10:
        problems.append(f"{name}: only {n_spans} vocab spans (expected ~15+)")
    if len(qs) != 10:
        problems.append(f"{name}: {len(qs)} questions (expected 10)")
    for i, q in enumerate(qs, 1):
        if not q.get("q") or len(q.get("opts", [])) != 4 or q.get("ans") not in (0, 1, 2, 3):
            problems.append(f"{name}: question {i} malformed")

    merged[str(un)] = {"title": title, "story_html": html, "questions": qs}

print(f"merged {len(merged)} units: {sorted(map(int, merged.keys()))}")
missing = sorted(set(range(1, 31)) - {int(k) for k in merged})
if missing:
    print("MISSING units:", missing)
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  -", p)
    sys.exit(1)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=1)
print(f"wrote {OUT}")
