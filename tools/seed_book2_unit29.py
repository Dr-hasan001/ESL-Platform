"""
Seed Book 2 Unit 29 — 4000 Essential English Words
Source: textbook word list (abstract → wooden)
Run: python tools/seed_book2_unit29.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.book import Book, Unit, Word

Base.metadata.create_all(bind=engine)
db = SessionLocal()

book = db.query(Book).filter(Book.book_number == 2).first()
unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 29).first()
if not unit:
    print("ERROR: Unit 29 not found.")
    db.close()
    sys.exit(1)

WORDS = [
    (1,  "Abstract",     "🎨", "adjective",
     "An abstract thing is an idea or thought, not a physical thing.",
     "The idea of beauty is abstract and changes over time.",
     "مجرد / تجريدي",
     ["abstractly (adv)", "abstraction (n)"]),

    (2,  "Annual",       "📅", "adjective",
     "An annual event happens once a year.",
     "The only time I see my aunts and uncles is at our annual family picnic.",
     "سنوي",
     ["annually (adv)"]),

    (3,  "Clay",         "🏺", "noun",
     "Clay is a type of heavy, wet soil used to make pots.",
     "She made a bowl out of the clay.",
     "طين / صلصال",
     ["clays (pl)"]),

    (4,  "Cloth",        "🧵", "noun",
     "Cloth is material used to make clothes.",
     "His shirt is made of a very soft type of cloth.",
     "قماش",
     ["cloths (pl)", "clothe (v)"]),

    (5,  "Curtain",      "🪟", "noun",
     "A curtain is a cloth hung over a window or used to divide a room.",
     "She opened the curtains to let light into the room.",
     "ستارة",
     ["curtains (pl)"]),

    (6,  "Deserve",      "🦴", "verb",
     "To deserve is to be worthy of something as a result of one's actions.",
     "The dog deserved a bone for behaving very well.",
     "يستحق",
     ["deserves (v)", "deserved (past)", "deserving (adj)"]),

    (7,  "Feather",      "🪶", "noun",
     "Feathers are the things covering a bird's bodies.",
     "That bird has orange feathers on its chest.",
     "ريشة",
     ["feathers (pl)", "feathered (adj)"]),

    (8,  "Fertile",      "🌾", "adjective",
     "Fertile land is able to produce good crops and plants.",
     "The farmer grew many vegetables in the fertile soil.",
     "خصب",
     ["fertility (n)", "fertilize (v)", "fertilizer (n)"]),

    (9,  "Flood",        "🌊", "noun",
     "A flood is an event in which water covers an area that is usually dry.",
     "After three days of rain, there was a flood in the city.",
     "فيضان",
     ["floods (pl)", "flooded (adj)", "flooding (n)"]),

    (10, "Furniture",    "🛋️", "noun",
     "Furniture means the things used in a house such as tables and chairs.",
     "His living room only had a few simple pieces of furniture.",
     "أثاث",
     ["furnish (v)", "furnished (adj)"]),

    (11, "Grave",        "🪦", "noun",
     "A grave is the place where a dead person is buried.",
     "We visit our grandfather's grave each year.",
     "قبر",
     ["graves (pl)", "graveyard (n)"]),

    (12, "Ideal",        "✨", "adjective",
     "An ideal thing is the best that it can possibly be.",
     "This house is an ideal place for my family. It has everything we need.",
     "مثالي",
     ["ideally (adv)", "idealize (v)", "idealism (n)"]),

    (13, "Intelligence", "🧠", "noun",
     "Intelligence is the ability to learn and understand things.",
     "Because of his high intelligence, he finished school early.",
     "ذكاء",
     ["intelligent (adj)", "intelligently (adv)"]),

    (14, "Obtain",       "🪪", "verb",
     "To obtain is to get something you want or need.",
     "After I passed the test, I obtained my driver's license.",
     "يحصل على",
     ["obtains (v)", "obtained (past)", "obtainable (adj)"]),

    (15, "Religious",    "🛐", "adjective",
     "Religious means related to or about religion.",
     "The holy man spoke about religious topics.",
     "ديني / متدين",
     ["religion (n)", "religiously (adv)"]),

    (16, "Romantic",     "💕", "adjective",
     "Romantic means related to or about love.",
     "The young couple went to see a romantic movie.",
     "رومانسي",
     ["romance (n)", "romantically (adv)"]),

    (17, "Shell",        "🐚", "noun",
     "A shell is a hard covering that protects the body of some sea creatures.",
     "There were many pretty shells on the beach.",
     "صدفة",
     ["shells (pl)", "seashell (n)"]),

    (18, "Shore",        "🏖️", "noun",
     "A shore is the edge of a large body of water.",
     "All of the boats were floating near the shore.",
     "شاطئ / ساحل",
     ["shores (pl)", "shoreline (n)"]),

    (19, "Wheel",        "🛞", "noun",
     "A wheel is a round thing on a vehicle that turns when it moves.",
     "A car has four wheels.",
     "عجلة",
     ["wheels (pl)", "wheeled (adj)"]),

    (20, "Wooden",       "🪵", "adjective",
     "Wooden objects are made of wood.",
     "My mother gave me a wooden spoon.",
     "خشبي",
     ["wood (n)", "woodwork (n)"]),
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
print(f"Unit 29 seeded: {len(WORDS)} words inserted.")
