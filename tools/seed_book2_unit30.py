"""
Seed Book 2 Unit 30 — 4000 Essential English Words
Source: textbook word list (appliance → swing)
Run: python tools/seed_book2_unit30.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.book import Book, Unit, Word

Base.metadata.create_all(bind=engine)
db = SessionLocal()

book = db.query(Book).filter(Book.book_number == 2).first()
unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 30).first()
if not unit:
    print("ERROR: Unit 30 not found.")
    db.close()
    sys.exit(1)

WORDS = [
    (1,  "Appliance",   "🔌", "noun",
     "An appliance is a piece of equipment used for jobs in the home.",
     "Many homes have appliances like ovens, toasters, and refrigerators.",
     "جهاز منزلي",
     ["appliances (pl)"]),

    (2,  "Basin",       "🪣", "noun",
     "A basin is a large bowl for washing things. A sink is sometimes called a basin.",
     "She filled the basin with water and washed her face.",
     "حوض / طشت",
     ["basins (pl)"]),

    (3,  "Broom",       "🧹", "noun",
     "A broom is a brush with a long handle used for cleaning floors.",
     "My father usually uses a broom to sweep away dust in the basement.",
     "مكنسة",
     ["brooms (pl)"]),

    (4,  "Caterpillar", "🐛", "noun",
     "A caterpillar is a small insect that looks like a worm and eats plants.",
     "After eating a lot of leaves, caterpillars change into butterflies.",
     "يرقة / دودة",
     ["caterpillars (pl)"]),

    (5,  "Cupboard",    "🗄️", "noun",
     "A cupboard is a piece of furniture that is used to store food or household items.",
     "We put all of our dishes and food in the cupboards.",
     "خزانة / دولاب",
     ["cupboards (pl)"]),

    (6,  "Delicate",    "🍃", "adjective",
     "Delicate things are easy to break or harm.",
     "You should hold the baby carefully because she's very delicate.",
     "رقيق / هش",
     ["delicately (adv)", "delicacy (n)"]),

    (7,  "Emerge",      "🐹", "verb",
     "To emerge from something means to come out of it.",
     "A groundhog emerged from a snow-covered hole.",
     "يخرج / يظهر",
     ["emerges (v)", "emerged (past)", "emergence (n)"]),

    (8,  "Handicap",    "♿", "noun",
     "A handicap is a condition that limits someone's mental or physical abilities.",
     "Joe has a slight handicap, so he uses a walker to get around.",
     "إعاقة",
     ["handicaps (pl)", "handicapped (adj)"]),

    (9,  "Hole",        "🕳️", "noun",
     "A hole is a hollow space in something solid.",
     "They made a big hole in the wall.",
     "ثقب / حفرة",
     ["holes (pl)"]),

    (10, "Hook",        "🪝", "noun",
     "A hook is a sharp curved piece of metal used for catching or holding things.",
     "The fish went after the sharp hook.",
     "خطاف / صنارة",
     ["hooks (pl)"]),

    (11, "Hop",         "🦘", "verb",
     "To hop means to jump a short distance.",
     "The kangaroo quickly hopped away from danger.",
     "يقفز / ينط",
     ["hops (v)", "hopped (past)", "hopping (n)"]),

    (12, "Laundry",     "🧺", "noun",
     "Laundry is clothing that have been or need to be washed.",
     "He folded the clean laundry and put the dirty laundry in a basket.",
     "غسيل",
     ["launder (v)", "laundromat (n)"]),

    (13, "Pursue",      "🏃", "verb",
     "To pursue is to chase or follow someone or something.",
     "The mother pursued her young child down the hill.",
     "يطارد / يلاحق",
     ["pursues (v)", "pursued (past)", "pursuit (n)"]),

    (14, "Reluctant",   "😟", "adjective",
     "Reluctant means not wanting to do something.",
     "She was reluctant to say that she saw the robbery.",
     "متردد / محجم",
     ["reluctantly (adv)", "reluctance (n)"]),

    (15, "Sleeve",      "👕", "noun",
     "Sleeves are the part of a shirt in which arms go.",
     "Ryan bought a new shirt with long sleeves to keep his arms warm.",
     "كُمّ",
     ["sleeves (pl)", "sleeveless (adj)"]),

    (16, "Spine",       "🦴", "noun",
     "The spine is the group of bones that run up and down the middle of the back.",
     "Our spine helps us to stand up nice and straight.",
     "العمود الفقري",
     ["spines (pl)", "spinal (adj)"]),

    (17, "Stain",       "🔴", "noun",
     "A stain is a dirty mark that is difficult to clean.",
     "He had a red stain on the collar of his shirt.",
     "بقعة / لطخة",
     ["stains (pl)", "stained (adj)"]),

    (18, "Strip",       "🎞️", "noun",
     "A strip is a long, narrow piece of material or land.",
     "He had long strips of film that held images of his trip abroad.",
     "شريط",
     ["strips (pl)"]),

    (19, "Swear",       "🤚", "verb",
     "To swear means to promise to do something.",
     "I will put my hand on the Bible and swear to do my best for the country.",
     "يقسم / يحلف",
     ["swears (v)", "swore (past)", "sworn (adj)"]),

    (20, "Swing",       "⛳", "verb",
     "To swing something means to move it back and forth or from side to side.",
     "He can swing a golf club very powerfully.",
     "يؤرجح / يلوّح",
     ["swings (v)", "swung (past)", "swinging (n)"]),
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
print(f"Unit 30 seeded: {len(WORDS)} words inserted.")
