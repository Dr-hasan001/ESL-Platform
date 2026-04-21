"""
seed_students.py — Create login accounts for all real students.

Run:  python tools/seed_students.py

Idempotent: uses get_or_create, so safe to re-run on every deploy.
Credentials are printed at the end — visible in Render deploy logs.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401 — register all models with Base
from app.models.user import User
from app.services.auth_service import hash_password

Base.metadata.create_all(bind=engine)

# Add plain_password column if it doesn't exist (safe to run on existing databases)
from sqlalchemy import text, inspect as sa_inspect
with engine.connect() as conn:
    existing_cols = [col["name"] for col in sa_inspect(engine).get_columns("users")]
    if "plain_password" not in existing_cols:
        conn.execute(text("ALTER TABLE users ADD COLUMN plain_password VARCHAR(100)"))
        conn.commit()
    if "class_name" not in existing_cols:
        conn.execute(text("ALTER TABLE users ADD COLUMN class_name VARCHAR(60)"))
        conn.commit()

db = SessionLocal()


def get_or_create(model, defaults=None, **kwargs):
    obj = db.query(model).filter_by(**kwargs).first()
    if obj:
        return obj, False
    obj = model(**{**kwargs, **(defaults or {})})
    db.add(obj)
    db.flush()
    return obj, True


# ── Student roster ────────────────────────────────────────────────────────────
# (username, plain_password, display_name, cefr_level, class_name)
STUDENTS = [
    ("m_karem",   "karem1847",    "Mohammed Karem",          "A2", "PM 91"),
    ("aqeel",     "aqeel3856",    "Aqeel Albdulrazaq",       "A2", "PM 91"),
    ("h_adnan",   "adnan6274",    "Hussein Ali Adnan",       "A2", "PM 91"),
    ("murtadha",  "murtadha9431", "Murtadha Khaled",         "A2", "PM 91"),
    ("ruqaya",    "ruqaya5817",   "Ruqaya Mazin",            "A2", "PM 91"),
    ("baneen",    "baneen2963",   "Baneen Raad",             "A2", "PM 91"),
    ("aya",       "aya7154",      "Aya Sabah",               "A2", "PM 91"),
    ("fatimah",   "fatimah4029",  "Fatimah Hassan",          "A2", "PM 91"),
    ("m_rida",    "rida8563",     "Mohammed Rida",           "A2", "PM 91"),
    ("nasser",    "nasser6748",   "Nasser Haider",           "A2", "PM 91"),
    ("muhsin",    "muhsin3195",   "Muhsin Ahmed",            "A2", "PM 91"),
    ("h_abd",     "abd8342",      "Hussein Ali Abdulameer",  "A2", "PM 91"),
    ("raghad",    "raghad5209",   "Raghad Mufak",            "A2", "PM 91"),
    ("aymen",     "aymen6382",    "Aymen",                   "A2", "PM 91"),
    ("fatima_abd","abd7519",      "Fatima Abd",              "A2", "PM 91"),
    ("muntadhar", "muntadhar4617","Muntadhar",               "A2", "PM 91"),
    # ── B1 students ───────────────────────────────────────────────────────────
    ("yasser",    "yasser2847",   "Yasser",                  "B1", "PM 82"),
    ("muna",      "muna5193",     "Muna",                    "B1", "PM 82"),
    ("hasan",     "hasan2026",    "Hasan",                   "B1", "PM 82"),
    ("haider",    "haider8251",   "Haider",                  "B1", "PM 82"),
    ("sajad",     "sajad3679",    "Sajad Mohammed",          "B1", "PM 82"),
    ("wissam",    "wissam4928",   "Wissam",                  "B1", "PM 82"),
    ("ahmed",     "ahmed6173",    "Ahmed",                   "B1", "PM 82"),
    ("m_sadiq",   "sadiq5847",    "Mohammed Sadiq",          "B1", "PM 82"),
    ("fiqar",     "fiqar3847",    "Fiqar",                   "B1", "PM 82"),
    ("faisal",    "faisal5293",   "Faisal",                  "B1", "PM 82"),
    ("karar",     "karar7162",    "Karar",                   "B1", "PM 82"),
    ("ali_sajad", "sajad9384",    "Ali Alsajad",             "B1", "PM 82"),
]

print("Creating student accounts…")
results = []
for username, password, display_name, level, cls in STUDENTS:
    user, created = get_or_create(
        User,
        username=username,
        defaults={
            "password_hash": hash_password(password),
            "plain_password": password,
            "role": "student",
            "display_name": display_name,
            "cefr_level": level,
            "class_name": cls,
        },
    )
    # Always sync password and class on re-run
    if not created:
        user.password_hash = hash_password(password)
        user.plain_password = password
        user.class_name = cls
    results.append((username, password, display_name, "CREATED" if created else "exists"))

db.commit()
db.close()

# ── Print credentials table ───────────────────────────────────────────────────
print()
print("=" * 68)
print(f"{'Display Name':<30} {'Username':<14} {'Password':<16} {'Status'}")
print("-" * 68)
for username, password, display_name, status in results:
    print(f"{display_name:<30} {username:<14} {password:<16} {status}")
print("=" * 68)
print()
