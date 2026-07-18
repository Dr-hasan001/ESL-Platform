"""
Seed Book 2 Unit 27 — 4000 Essential English Words
Source: textbook word list (apology → witch)
Run: python tools/seed_book2_unit27.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.book import Book, Unit, Word

Base.metadata.create_all(bind=engine)
db = SessionLocal()

book = db.query(Book).filter(Book.book_number == 2).first()
unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 27).first()
if not unit:
    print("ERROR: Unit 27 not found.")
    db.close()
    sys.exit(1)

WORDS = [
    (1,  "Apology",    "🙇", "noun",
     "An apology is what people say to show that they are sorry.",
     "After arguing with her teacher, the girl wrote the teacher an apology.",
     "اعتذار",
     ["apologies (pl)", "apologize (v)", "apologetic (adj)"]),

    (2,  "Bold",       "🦁", "adjective",
     "A bold person is not afraid of doing something.",
     "The bold man climbed the high mountain.",
     "جريء / شجاع",
     ["boldly (adv)", "boldness (n)", "timid (opp)"]),

    (3,  "Bug",        "🐛", "noun",
     "A bug is a small insect.",
     "Birds like eating bugs.",
     "حشرة",
     ["bugs (pl)", "buggy (adj)"]),

    (4,  "Capture",    "🥅", "verb",
     "To capture something is to catch and hold it.",
     "James tried to capture the bubbles in his hands.",
     "يأسر / يلتقط",
     ["captures (v)", "captured (past)", "captive (n/adj)", "captivity (n)"]),

    (5,  "Duke",       "👑", "noun",
     "A duke is a man of high social rank but below a king or queen.",
     "The duke ruled over the land.",
     "دوق / أمير",
     ["dukes (pl)", "duchess (fem.)", "dukedom (n)"]),

    (6,  "Expose",     "🔓", "verb",
     "To expose is to make known something that is hidden.",
     "He took off his shirt to expose his costume.",
     "يكشف / يظهر",
     ["exposes (v)", "exposed (past)", "exposure (n)"]),

    (7,  "Guilty",     "😔", "adjective",
     "Guilty people feel bad for something they did.",
     "I felt guilty for taking my sister's cookies.",
     "مذنب",
     ["guilt (n)", "guiltily (adv)", "innocent (opp)"]),

    (8,  "Hire",       "🤝", "verb",
     "To hire someone is to pay that person money to work for you.",
     "We hired a man to paint our house.",
     "يستأجر / يوظف",
     ["hires (v)", "hired (past)", "hiring (n)"]),

    (9,  "Innocent",   "😇", "adjective",
     "An innocent person is not guilty of a crime.",
     "The judge said that the woman was innocent of the crime.",
     "بريء",
     ["innocence (n)", "innocently (adv)", "guilty (opp)"]),

    (10, "Language",   "💬", "noun",
     "A language is a system of communication.",
     "The reporter spoke a language Sally had never heard before.",
     "لغة",
     ["languages (pl)", "linguistic (adj)"]),

    (11, "Minister",   "🏛️", "noun",
     "A minister is an important person in government with many duties.",
     "The minister of education controls the country's schools.",
     "وزير",
     ["ministers (pl)", "ministry (n)", "ministerial (adj)"]),

    (12, "Ordinary",   "📋", "adjective",
     "Ordinary means normal, or not special in any way.",
     "Today was just an ordinary day. Nothing unusual happened.",
     "عادي",
     ["ordinarily (adv)", "extraordinary (opp)"]),

    (13, "Permanent",  "⏳", "adjective",
     "Something permanent lasts for a long time or forever.",
     "We don't know if Aunt Mildred's visit will be a permanent one.",
     "دائم",
     ["permanently (adv)", "permanence (n)", "temporary (opp)"]),

    (14, "Preserve",   "🛡️", "verb",
     "To preserve is to protect something from harm.",
     "Dad sprayed a chemical on the house to help preserve the walls.",
     "يحافظ على",
     ["preserves (v)", "preserved (past)", "preservation (n)", "preservative (n)"]),

    (15, "Pronounce",  "🗣️", "verb",
     "To pronounce is to say the sounds of letters or words.",
     "Young children often have trouble pronouncing words right.",
     "ينطق",
     ["pronounces (v)", "pronounced (past)", "pronunciation (n)"]),

    (16, "Resemble",   "👥", "verb",
     "To resemble someone is to look like that person.",
     "The baby really resembles his father.",
     "يشبه",
     ["resembles (v)", "resembled (past)", "resemblance (n)"]),

    (17, "Symptom",    "🤒", "noun",
     "A symptom of a bad condition or illness is a sign that it is happening.",
     "Sneezing and a high fever are symptoms of the common cold.",
     "عَرَض / علامة",
     ["symptoms (pl)", "symptomatic (adj)"]),

    (18, "Tobacco",    "🚬", "noun",
     "Tobacco is a plant whose leaves are smoked, such as in cigarettes.",
     "The tobacco in cigarettes is bad for you.",
     "تبغ",
     ["tobaccos (pl)"]),

    (19, "Twin",       "👯", "noun",
     "Twins are two children born at the same time.",
     "My sister and I are twins. We look exactly the same.",
     "توأم",
     ["twins (pl)", "twin (adj)"]),

    (20, "Witch",      "🧙", "noun",
     "A witch is a woman with magical powers.",
     "People think that witches fly around on broomsticks.",
     "ساحرة",
     ["witches (pl)", "witchcraft (n)", "bewitch (v)"]),
]

# Idempotent: clear existing words for this unit first
db.query(Word).filter(Word.unit_id == unit.id).delete()

for pos, word, emoji, pos_tag, definition, example, arabic, derivatives in WORDS:
    db.add(Word(
        unit_id=unit.id,
        position=pos,
        word=word,
        emoji=emoji,
        part_of_speech=pos_tag,
        definition=definition,
        example=example,
        arabic_translation=arabic,
        derivatives=derivatives,
    ))

unit.word_count = len(WORDS)
db.commit()
db.close()
print(f"Unit 27 seeded: {len(WORDS)} words inserted.")
