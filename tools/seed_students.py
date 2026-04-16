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
# (username, plain_password, display_name, cefr_level)
STUDENTS = [
    ("m_karem",   "karem1847",    "Mohammed Karem",          "A2"),
    ("aqeel",     "aqeel3856",    "Aqeel Albdulrazaq",       "A2"),
    ("h_adnan",   "adnan6274",    "Hussein Ali Adnan",       "A2"),
    ("murtadha",  "murtadha9431", "Murtadha Khaled",         "A2"),
    ("ruqaya",    "ruqaya5817",   "Ruqaya Mazin",            "A2"),
    ("baneen",    "baneen2963",   "Baneen Raad",             "A2"),
    ("aya",       "aya7154",      "Aya Sabah",               "A2"),
    ("fatimah",   "fatimah4029",  "Fatimah Hassan",          "A2"),
    ("m_rida",    "rida8563",     "Mohammed Rida",           "A2"),
    ("nasser",    "nasser6748",   "Nasser Haider",           "A2"),
    ("muhsin",    "muhsin3195",   "Muhsin Ahmed",            "A2"),
    ("h_abd",     "abd8342",      "Hussein Ali Abdulameer",  "A2"),
    ("raghad",    "raghad5209",   "Raghad Mufak",            "A2"),
    ("aymen",     "aymen6382",    "Aymen",                   "A2"),
    ("fatima_abd","abd7519",      "Fatima Abd",              "A2"),
    ("muntadhar", "muntadhar4617","Muntadhar",               "A2"),
    # ── B1 students ───────────────────────────────────────────────────────────
    ("yasser",    "yasser2847",   "Yasser",                  "B1"),
    ("muna",      "muna5193",     "Muna",                    "B1"),
    ("hasan",     "hasan7364",    "Hasan",                   "B1"),
    ("haider",    "haider8251",   "Haider",                  "B1"),
    ("sajad",     "sajad3679",    "Sajad Mohammed",          "B1"),
    ("wissam",    "wissam4928",   "Wissam",                  "B1"),
    ("ahmed",     "ahmed6173",    "Ahmed",                   "B1"),
    ("m_sadiq",   "sadiq5847",    "Mohammed Sadiq",          "B1"),
    ("fiqar",     "fiqar3847",    "Fiqar",                   "B1"),
    ("faisal",    "faisal5293",   "Faisal",                  "B1"),
    ("karar",     "karar7162",    "Karar",                   "B1"),
    ("ali_sajad", "sajad9384",    "Ali Alsajad",             "B1"),
]

print("Creating student accounts…")
results = []
for username, password, display_name, level in STUDENTS:
    _, created = get_or_create(
        User,
        username=username,
        defaults={
            "password_hash": hash_password(password),
            "role": "student",
            "display_name": display_name,
            "cefr_level": level,
        },
    )
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
