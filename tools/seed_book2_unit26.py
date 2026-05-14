"""
Seed Book 2 Unit 26 — 4000 Essential English Words
Story: The Two Captains
Run: python tools/seed_book2_unit26.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.book import Book, Unit, Word, UnitStory

Base.metadata.create_all(bind=engine)
db = SessionLocal()

book = db.query(Book).filter(Book.book_number == 2).first()
unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 26).first()
if not unit:
    print("ERROR: Unit 26 not found.")
    db.close()
    sys.exit(1)

WORDS = [
    (1,  "Accuse",    "⚖️", "verb",
     "To accuse someone of something is to blame them for doing it.",
     "She accused her brother of breaking her computer.",
     "يتهم",
     ["accuses (v)", "accused (past)", "accusation (n)"]),

    (2,  "Adjust",    "🔧", "verb",
     "To adjust something means to change it so it is better.",
     "He adjusted the old guitar to make it sound better.",
     "يضبط / يعدّل",
     ["adjusts (v)", "adjusted (past)", "adjustment (n)"]),

    (3,  "Amuse",     "😄", "verb",
     "To amuse someone means to do something that is funny or entertaining.",
     "The singer was very good. She amused the crowd.",
     "يسلّي / يمتّع",
     ["amuses (v)", "amused (past)", "amusement (n)", "amusing (adj)"]),

    (4,  "Coral",     "🪸", "noun",
     "Coral is the hard, colorful material formed by the shells of animals.",
     "The diver admired the beautiful coral under the water.",
     "مرجان",
     ["corals (pl)"]),

    (5,  "Cotton",    "👕", "noun",
     "Cotton is a cloth made from the fibers of the cotton plant.",
     "I like to wear clothes made from cotton in the summer.",
     "قطن",
     []),

    (6,  "Crash",     "💥", "verb",
     "To crash means to hit and break something.",
     "There was a loud noise when the car crashed into the tree.",
     "يصطدم / يحطم",
     ["crashes (v)", "crashed (past)", "crash (n)"]),

    (7,  "Deck",      "🛳️", "noun",
     "A deck is a wooden floor built outside of a house or the floor of a ship.",
     "A ship will store many supplies below its deck.",
     "سطح السفينة / شرفة خشبية",
     ["decks (pl)"]),

    (8,  "Engage",    "🔨", "verb",
     "To engage in something means to do it.",
     "Dad was engaged in sawing a piece of wood in half.",
     "يشارك / ينخرط",
     ["engages (v)", "engaged (past)", "engagement (n)"]),

    (9,  "Firm",      "🛏️", "adjective",
     "A firm thing is solid but not too hard.",
     "He sleeps better on a firm bed.",
     "صلب / ثابت",
     ["firmly (adv)", "firmness (n)"]),

    (10, "Fuel",      "🔥", "noun",
     "Fuel is something that creates heat or energy.",
     "Wood is the fuel that burns to make heat in this fire.",
     "وقود",
     ["fuels (pl)", "fuel (v)"]),

    (11, "Grand",     "🏔️", "adjective",
     "Something grand is big and liked by people.",
     "The grand mountain rose high into the sky.",
     "عظيم / فخم",
     ["grandly (adv)", "grandeur (n)"]),

    (12, "Hurricane", "🌀", "noun",
     "A hurricane is a bad storm that happens over the ocean.",
     "The wind from the hurricane bent the palm tree.",
     "إعصار",
     ["hurricanes (pl)"]),

    (13, "Loss",      "📉", "noun",
     "A loss is the act or instance of losing something.",
     "I suffered a big loss while I was gambling.",
     "خسارة",
     ["losses (pl)", "lose (v)", "lost (adj)"]),

    (14, "Plain",     "👟", "adjective",
     "A plain thing is simple and not decorated.",
     "He bought a pair of plain white shoes over the weekend.",
     "بسيط / عادي",
     ["plainly (adv)", "plainness (n)"]),

    (15, "Reef",      "🐠", "noun",
     "A reef is a group of rocks or coral in the ocean.",
     "He walked along the reef and looked at the water below.",
     "شعاب مرجانية",
     ["reefs (pl)"]),

    (16, "Shut",      "🚪", "verb",
     "To shut something means to close it tightly.",
     "Please shut the door; the air outside is cold.",
     "يغلق",
     ["shuts (v)", "shut (past)", "shutting (n)"]),

    (17, "Strict",    "👨‍🏫", "adjective",
     "A strict person makes sure others follow rules.",
     "The teacher is strict. She does not let students talk in class.",
     "صارم",
     ["stricter (comp)", "strictly (adv)", "strictness (n)"]),

    (18, "Surf",      "🏄", "verb",
     "To surf means to use a special board to ride on waves in the ocean.",
     "The students went to the beach to surf during their vacation.",
     "يركب الأمواج",
     ["surfs (v)", "surfed (past)", "surfing (n)", "surfer (n)"]),

    (19, "Task",      "✅", "noun",
     "A task is a piece of work to be done that is sometimes hard.",
     "My task for the weekend was to clean the entire back yard.",
     "مهمة",
     ["tasks (pl)"]),

    (20, "Zone",      "🚧", "noun",
     "A zone is a place that has different qualities from the areas around it.",
     "Firefighters often work in danger zones.",
     "منطقة",
     ["zones (pl)"]),
]

STORY_TITLE = "The Two Captains"

STORY_HTML = """
<p>Once, there were two ships. Both ships carried <strong>cotton</strong>. The captains were very different. Thomas was <strong>strict</strong>. He made his crew <strong>engage</strong> in difficult <strong>tasks</strong>, and he kept <strong>firm</strong> control of his ship and men. His ship's <strong>deck</strong> was always clean and working well and he sailed carefully to use less <strong>fuel</strong>. His ship was very <strong>plain</strong>, but he never had a problem with it.</p>

<p>The second captain, William, was not so serious. He had a <strong>grand</strong> ship, and he loved having fun. When they stopped at islands, his crew <strong>amused</strong> themselves by going <strong>surfing</strong> or diving on the reef. They gave more time to these things than to taking care of the ship.</p>

<p>One day, Thomas saw a <strong>hurricane</strong> ahead. He knew that his ship needed to turn around. But he was sure William did not see the storm. He <strong>adjusted</strong> the dials on the radio and called his friend to tell him how to avoid the danger <strong>zone</strong>. But William's radio was not working, so it was not possible to contact him. When William's ship got to the hurricane, the wind blew it into the <strong>reef</strong>.</p>

<p>William tried to <strong>shut</strong> the door, but the ship had already <strong>crashed</strong> into the <strong>coral</strong>, and there was a lot of damage. William's crew then <strong>accused</strong> him of being a bad captain. The <strong>loss</strong> of the ship taught William a lesson, and he then really understood the value of keeping equipment working well.</p>
"""

STORY_QUESTIONS = [
    {
        "q": "How were Thomas and William different as captains?",
        "opts": [
            "Thomas had a grand ship; William had a plain one.",
            "Thomas was strict and careful; William was fun-loving and not serious.",
            "Thomas's crew surfed; William's crew worked hard.",
            "They were exactly the same."
        ],
        "ans": 1
    },
    {
        "q": "What did William's crew do at islands instead of taking care of the ship?",
        "opts": [
            "Cleaned the deck and fixed the equipment.",
            "Studied maps.",
            "Surfed and went diving on the reef.",
            "Slept all day."
        ],
        "ans": 2
    },
    {
        "q": "Why couldn't Thomas warn William about the hurricane?",
        "opts": [
            "William's radio was not working.",
            "Thomas's radio was broken.",
            "William was already at home.",
            "It wasn't urgent."
        ],
        "ans": 0
    },
    {
        "q": "What happened to William's ship?",
        "opts": [
            "It safely escaped the hurricane.",
            "Thomas's ship rescued it.",
            "It was blown into the reef and crashed into the coral.",
            "It sank without damage."
        ],
        "ans": 2
    },
    {
        "q": "What lesson did William learn?",
        "opts": [
            "How to surf better.",
            "To always carry more cotton.",
            "To accuse his crew when things go wrong.",
            "The value of keeping equipment working well."
        ],
        "ans": 3
    },
]

# Clear existing words
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

existing_story = db.query(UnitStory).filter(UnitStory.unit_id == unit.id).first()
if existing_story:
    existing_story.story_title = STORY_TITLE
    existing_story.story_html = STORY_HTML
    existing_story.story_questions = STORY_QUESTIONS
else:
    db.add(UnitStory(
        unit_id=unit.id,
        story_title=STORY_TITLE,
        story_html=STORY_HTML,
        story_questions=STORY_QUESTIONS,
    ))

db.commit()
db.close()
print(f"Unit 26 seeded: {len(WORDS)} words, story '{STORY_TITLE}', {len(STORY_QUESTIONS)} questions.")
