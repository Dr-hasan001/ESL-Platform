"""
seed_book2_unit9.py
Inserts vocabulary words for 4000 Essential English Words Book 2 (A2), Unit 9 - Plans.
20 target words themed around making plans, intentions, and future arrangements.

Run: python tools/seed_book2_unit9.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.book import Book, Unit, Word

Base.metadata.create_all(bind=engine)
db = SessionLocal()

book = db.query(Book).filter(Book.book_number == 2).first()
if not book:
    print("ERROR: Book 2 not found. Run tools/seed_db.py first.")
    db.close()
    sys.exit(1)

unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 9).first()
if not unit:
    print("ERROR: Unit 9 not found.")
    db.close()
    sys.exit(1)

# ── Remove existing words (idempotent) ────────────────────────────────────────
existing = db.query(Word).filter(Word.unit_id == unit.id).count()
if existing:
    db.query(Word).filter(Word.unit_id == unit.id).delete()
    print(f"Removed {existing} existing words from Unit 9.")

# ── 20 words — theme: Plans ───────────────────────────────────────────────────
WORDS = [
    (1,  "Appointment", "📅", "noun",
     "An appointment is a time you arrange to meet someone or go somewhere.",
     "She made an appointment with the doctor for Thursday morning.",
     "موعد",
     ["appointments (pl)", "appoint (v)"]),

    (2,  "Book",        "🎟️", "verb",
     "To book means to arrange in advance to have or use something.",
     "We booked two seats on the train to Paris.",
     "يحجز",
     ["books", "booked", "booking (n)"]),

    (3,  "Cancel",      "❌", "verb",
     "To cancel means to decide that something planned will not happen.",
     "She cancelled the meeting because she was feeling ill.",
     "يلغي",
     ["cancels", "cancelled", "cancellation (n)"]),

    (4,  "Confirm",     "✅", "verb",
     "To confirm means to say officially that something is definite or true.",
     "Please confirm your attendance by emailing us before Friday.",
     "يؤكد",
     ["confirms", "confirmed", "confirmation (n)"]),

    (5,  "Deadline",    "⏰", "noun",
     "A deadline is the latest time by which you must finish something.",
     "The deadline for submitting the report is next Monday.",
     "موعد نهائي",
     ["deadlines (pl)"]),

    (6,  "Expect",      "🤞", "verb",
     "To expect something means to believe it will happen.",
     "We expect the results to arrive by the end of the week.",
     "يتوقع",
     ["expects", "expected", "expectation (n)"]),

    (7,  "Future",      "🔭", "noun",
     "The future is the time that has not happened yet.",
     "Nobody knows exactly what the future will bring.",
     "المستقبل",
     ["futures (pl)", "future (adj)"]),

    (8,  "Goal",        "🥅", "noun",
     "A goal is something important that you want to achieve.",
     "Her goal is to become a doctor and help sick people.",
     "هدف",
     ["goals (pl)"]),

    (9,  "Hope",        "🌈", "verb",
     "To hope means to want something to happen and believe it might.",
     "I hope the weather will be good for the picnic on Saturday.",
     "يأمل / يتمنى",
     ["hopes", "hoped", "hope (n)", "hopeful (adj)"]),

    (10, "Intend",      "🧭", "verb",
     "To intend means to have a plan or purpose to do something.",
     "I intend to finish this book before the end of the month.",
     "ينوي / يعتزم",
     ["intends", "intended", "intention (n)"]),

    (11, "Invite",      "💌", "verb",
     "To invite someone means to ask them to come to an event or place.",
     "She invited all her friends to her birthday party.",
     "يدعو",
     ["invites", "invited", "invitation (n)"]),

    (12, "Plan",        "📋", "noun",
     "A plan is a decision about what you will do in the future.",
     "What are your plans for the summer holiday?",
     "خطة / برنامج",
     ["plans (pl)", "plan (v)", "planned (adj)"]),

    (13, "Prepare",     "🍳", "verb",
     "To prepare means to make yourself or something ready for something.",
     "She spent the whole evening preparing for the big interview.",
     "يستعد / يحضّر",
     ["prepares", "prepared", "preparation (n)"]),

    (14, "Promise",     "🤝", "verb",
     "To promise means to say that you will definitely do or not do something.",
     "He promised his mother he would call every week.",
     "يعد / يتعهد",
     ["promises", "promised", "promise (n)"]),

    (15, "Remind",      "🔔", "verb",
     "To remind someone means to help them remember something.",
     "Can you remind me to buy milk on the way home?",
     "يذكّر",
     ["reminds", "reminded", "reminder (n)"]),

    (16, "Reserve",     "🔖", "verb",
     "To reserve something means to arrange for it to be kept for you to use later.",
     "We reserved a table at the restaurant for seven o'clock.",
     "يحجز (مكاناً)",
     ["reserves", "reserved", "reservation (n)"]),

    (17, "Schedule",    "🗓️", "noun",
     "A schedule is a plan that shows what will happen and when.",
     "According to the schedule, the bus leaves at nine.",
     "جدول زمني",
     ["schedules (pl)", "schedule (v)", "scheduled (adj)"]),

    (18, "Update",      "🔄", "verb",
     "To update means to add new information or make something more modern.",
     "Please update me as soon as you hear any news.",
     "يحدّث / يُطلع",
     ["updates", "updated", "update (n)"]),

    (19, "Wish",        "⭐", "verb",
     "To wish means to want something to happen, even if it is unlikely.",
     "I wish I could travel to Japan one day.",
     "يتمنى",
     ["wishes", "wished", "wish (n)", "wishful (adj)"]),

    (20, "Worry",       "😰", "verb",
     "To worry means to feel anxious or nervous about something that might happen.",
     "Don't worry — I'm sure everything will be fine.",
     "يقلق",
     ["worries", "worried", "worry (n)", "worrying (adj)"]),
]

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
print(f"Unit 9 '{unit.title}' (id={unit.id}): {len(WORDS)} words added.")
db.close()
