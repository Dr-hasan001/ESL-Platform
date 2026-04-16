"""
seed_db.py — Populate the ESL Platform database with initial data.

Run: python tools/seed_db.py

Creates:
  • 6 books (A1–C2) for the "4000 Essential English Words" series
  • 30 stub units per book
  • Outcomes Elementary A2 — 16 units with correct titles and week mapping
  • 42 General Topics (6 levels × 7 topics)
  • 1 teacher account  (username: teacher  password: teacher123)
  • 1 sample student   (username: student1 password: student123)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401 — import all models so Base sees them
from app.services.auth_service import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ── Helpers ──────────────────────────────────────────────────────────────────

def get_or_create(model, defaults=None, **kwargs):
    obj = db.query(model).filter_by(**kwargs).first()
    if obj:
        return obj, False
    obj = model(**{**kwargs, **(defaults or {})})
    db.add(obj)
    db.flush()
    return obj, True


# ── 1. Users ──────────────────────────────────────────────────────────────────
print("Creating users…")
teacher, _ = get_or_create(
    User, username="teacher",
    defaults={"password_hash": hash_password("teacher123"), "role": "teacher", "display_name": "Teacher"}
)
student1, _ = get_or_create(
    User, username="student1",
    defaults={"password_hash": hash_password("student123"), "role": "student", "display_name": "Student One", "cefr_level": "A2"}
)


# ── 2. Books ──────────────────────────────────────────────────────────────────
BOOKS = [
    {"book_number": 1, "cefr_level": "A1", "cover_color": "#C84830", "unit_count": 30},
    {"book_number": 2, "cefr_level": "A2", "cover_color": "#1E5C72", "unit_count": 30},
    {"book_number": 3, "cefr_level": "B1", "cover_color": "#4A3580", "unit_count": 30},
    {"book_number": 4, "cefr_level": "B2", "cover_color": "#2A6B3D", "unit_count": 30},
    {"book_number": 5, "cefr_level": "C1", "cover_color": "#8B4513", "unit_count": 30},
    {"book_number": 6, "cefr_level": "C2", "cover_color": "#1A1209", "unit_count": 30},
]
print("Creating books…")
book_map = {}
for b in BOOKS:
    book, _ = get_or_create(
        Book,
        book_number=b["book_number"],
        defaults={
            "title": f"4000 Essential English Words Book {b['book_number']} ({b['cefr_level']})",
            "series": "4000 Essential English Words",
            "cefr_level": b["cefr_level"],
            "cover_color": b["cover_color"],
            "unit_count": b["unit_count"],
        }
    )
    book_map[b["book_number"]] = book


# ── 3. Units for all books (stub titles) ──────────────────────────────────────
print("Creating units…")
for book_num, book in book_map.items():
    for u in range(1, book.unit_count + 1):
        get_or_create(Unit, book_id=book.id, unit_number=u, defaults={"title": f"Unit {u}", "word_count": 20})


# ── 4. Outcomes A2 unit titles (overwrite Unit 1–16 of Book 2) ───────────────
OUTCOMES_A2_TITLES = [
    "Stuff",          # Unit 1
    "Family",         # Unit 2
    "My life",        # Unit 3
    "Food",           # Unit 4
    "Places",         # Unit 5
    "Work",           # Unit 6
    "Free time",      # Unit 7
    "Shopping",       # Unit 8
    "Plans",          # Unit 9
    "Days",           # Unit 10
    "Feelings",       # Unit 11
    "Experiences",    # Unit 12
    "Problems",       # Unit 13
    "The future",     # Unit 14
    "People",         # Unit 15
    "Life events",    # Unit 16
]
book2 = book_map[2]
for i, title in enumerate(OUTCOMES_A2_TITLES, start=1):
    unit = db.query(Unit).filter(Unit.book_id == book2.id, Unit.unit_number == i).first()
    if unit:
        unit.title = title


# ── 5. General Topics (42 videos) ────────────────────────────────────────────
TOPICS = [
    # A1 — 7 topics
    ("A1", "My Family & Home",       "Social",      1),
    ("A1", "Food I Like",            "Culture",     2),
    ("A1", "My School",              "Social",      3),
    ("A1", "My Body",                "Science",     4),
    ("A1", "Animals",                "Science",     5),
    ("A1", "Colors & Numbers",       "Educational", 6),
    ("A1", "My Community",           "Social",      7),
    # A2 — 7 topics
    ("A2", "Daily Routines",         "Social",      1),
    ("A2", "Shopping",               "Social",      2),
    ("A2", "Weather & Seasons",      "Geography",   3),
    ("A2", "Transport",              "Technology",  4),
    ("A2", "Health & Body",          "Science",     5),
    ("A2", "Hobbies & Free Time",    "Social",      6),
    ("A2", "Community Helpers",      "Social",      7),
    # B1 — 7 topics
    ("B1", "Simple Machines",        "Science",     1),
    ("B1", "The Internet",           "Technology",  2),
    ("B1", "The 7 Continents",       "Geography",   3),
    ("B1", "Ancient Egypt",          "History",     4),
    ("B1", "Friendship & Conflict",  "Social",      5),
    ("B1", "The Lost Key",           "Story",       6),
    ("B1", "What Is a Vote?",        "Politics",    7),
    # B2 — 7 topics
    ("B2", "DNA & Genetics",         "Science",     1),
    ("B2", "Renewable Energy",       "Technology",  2),
    ("B2", "Climate Zones",          "Geography",   3),
    ("B2", "World Wars",             "History",     4),
    ("B2", "The Immigrant",          "Story",       5),
    ("B2", "Mental Health",          "Social",      6),
    ("B2", "Democracy & Dictatorship","Politics",   7),
    # C1 — 7 topics
    ("C1", "Neuroscience & Behavior","Science",     1),
    ("C1", "AI & Society",           "Technology",  2),
    ("C1", "Geopolitics",            "Geography",   3),
    ("C1", "Colonialism",            "History",     4),
    ("C1", "The Whistleblower",      "Story",       5),
    ("C1", "Economic Inequality",    "Social",      6),
    ("C1", "International Law",      "Politics",    7),
    # C2 — 7 topics
    ("C2", "Philosophy of Science",  "Science",     1),
    ("C2", "Transhumanism & Ethics", "Technology",  2),
    ("C2", "Global Migration",       "Geography",   3),
    ("C2", "Historiography",         "History",     4),
    ("C2", "The Unreliable Narrator","Story",       5),
    ("C2", "Justice Systems",        "Social",      6),
    ("C2", "Power & Corruption",     "Politics",    7),
]
print("Creating general topics…")
for cefr, name, category, order in TOPICS:
    get_or_create(Topic, cefr_level=cefr, topic_name=name, defaults={"category": category, "sort_order": order})


db.commit()
print("Database seeded successfully.")
print(f"  Teacher login:  username=teacher   password=teacher123")
print(f"  Student login:  username=student1  password=student123")
db.close()
