"""
Seed Book 2 Unit 28 — 4000 Essential English Words
Source: textbook word list (accompany → whisper)
Run: python tools/seed_book2_unit28.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.book import Book, Unit, Word

Base.metadata.create_all(bind=engine)
db = SessionLocal()

book = db.query(Book).filter(Book.book_number == 2).first()
unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 28).first()
if not unit:
    print("ERROR: Unit 28 not found.")
    db.close()
    sys.exit(1)

WORDS = [
    (1,  "Accompany",  "👫", "verb",
     "To accompany other people means to join them or go with them.",
     "My brothers accompanied me to the movie.",
     "يرافق / يصاحب",
     ["accompanies (v)", "accompanied (past)", "accompaniment (n)"]),

    (2,  "Bare",       "🦶", "adjective",
     "A bare thing is plain and not covered.",
     "He likes to walk around in his bare feet.",
     "عارٍ / مكشوف",
     ["barely (adv)", "bareness (n)"]),

    (3,  "Branch",     "🌿", "noun",
     "A branch is the part of a tree with leaves.",
     "The monkey was hanging from a branch on the tree.",
     "غصن / فرع",
     ["branches (pl)", "branch out (v)"]),

    (4,  "Breath",     "💨", "noun",
     "A breath is the air that goes into and out of one's lungs.",
     "You can't take a breath under water.",
     "نَفَس",
     ["breaths (pl)", "breathe (v)", "breathless (adj)"]),

    (5,  "Bridge",     "🌉", "noun",
     "A bridge is something that is built over a river so people can cross it.",
     "The old bridge fell into the river.",
     "جسر",
     ["bridges (pl)"]),

    (6,  "Cast",       "🎣", "verb",
     "To cast something means to throw it.",
     "The fisherman cast his line into the water.",
     "يرمي / يلقي",
     ["casts (v)", "casting (n)"]),

    (7,  "Dare",       "🪂", "verb",
     "To dare means to be brave enough to try something.",
     "He dared to jump out of the airplane and skydive.",
     "يجرؤ / يتجرأ",
     ["dares (v)", "dared (past)", "daring (adj)"]),

    (8,  "Electronic", "📱", "adjective",
     "An electronic thing uses electricity to work.",
     "I like having electronic devices such as an MP3 player.",
     "إلكتروني",
     ["electronics (n)", "electronically (adv)", "electron (n)"]),

    (9,  "Inn",        "🏨", "noun",
     "An inn is a place where travelers can rest and eat.",
     "The visitor got a room at the inn.",
     "نُزل / خان",
     ["inns (pl)", "innkeeper (n)"]),

    (10, "Net",        "🥅", "noun",
     "A net is a bag made of strong thread. It is used to catch animals.",
     "The boy caught butterflies in his net.",
     "شبكة",
     ["nets (pl)", "netting (n)"]),

    (11, "Philosophy", "🤔", "noun",
     "A philosophy is a way to think about truth and life.",
     "My philosophy is 'live and let live.'",
     "فلسفة",
     ["philosophies (pl)", "philosopher (n)", "philosophical (adj)"]),

    (12, "Pot",        "🍲", "noun",
     "A pot is a deep, round metal container used for cooking.",
     "Don't touch the pot on the stove. It's hot.",
     "قِدر / إناء",
     ["pots (pl)"]),

    (13, "Seed",       "🌱", "noun",
     "A seed is the hard part of a plant or fruit that trees grow from.",
     "I planted the seed in the dirt, hoping that it would grow into a tree.",
     "بذرة",
     ["seeds (pl)", "seedling (n)", "seed (v)"]),

    (14, "Sharp",      "🔪", "adjective",
     "A sharp object has a thin edge that cuts things easily.",
     "That knife is very sharp. Be careful not to hurt yourself.",
     "حاد",
     ["sharply (adv)", "sharpen (v)", "sharpness (n)"]),

    (15, "Sort",       "🗂️", "noun",
     "A sort is something or a type of it.",
     "What sort of instrument do you want to learn to play?",
     "نوع / صنف",
     ["sorts (pl)", "sort (v)", "sorting (n)"]),

    (16, "Subtract",   "➖", "verb",
     "To subtract means to take something away.",
     "We learned how to subtract numbers in class.",
     "يطرح / ينقص",
     ["subtracts (v)", "subtracted (past)", "subtraction (n)"]),

    (17, "Tight",      "🔩", "adjective",
     "A tight thing is hard to move because it is firmly in place.",
     "The knots were too tight to untie.",
     "مُحكم / ضيق",
     ["tightly (adv)", "tighten (v)", "tightness (n)"]),

    (18, "Virtual",    "🕶️", "adjective",
     "A virtual thing is very close to being true or accurate.",
     "Because he's popular, Joe is the virtual leader of the group.",
     "فعلي / شبه حقيقي",
     ["virtually (adv)", "virtual reality (n)"]),

    (19, "Weigh",      "⚖️", "verb",
     "To weigh something means to measure how heavy it is.",
     "The little dog weighed exactly 3 kilograms.",
     "يزن",
     ["weighs (v)", "weighed (past)", "weight (n)"]),

    (20, "Whisper",    "🤫", "verb",
     "To whisper means to say very quietly.",
     "We have to whisper in the library so people can focus on reading.",
     "يهمس",
     ["whispers (v)", "whispered (past)", "whispering (n)"]),
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
print(f"Unit 28 seeded: {len(WORDS)} words inserted.")
