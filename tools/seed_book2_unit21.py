"""
Seed Book 2 Unit 21 — 4000 Essential English Words
Story: From the Earth to the Stars
Run: python tools/seed_book2_unit21.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.book import Book, Unit, Word, UnitStory

Base.metadata.create_all(bind=engine)
db = SessionLocal()

book = db.query(Book).filter(Book.book_number == 2).first()
if not book:
    print("ERROR: Book 2 not found.")
    db.close()
    sys.exit(1)

unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 21).first()
if not unit:
    print("ERROR: Unit 21 not found.")
    db.close()
    sys.exit(1)

WORDS = [
    (1,  "Accident",    "💥", "noun",
     "An accident is unexpected and may cause some trouble.",
     "He damaged the car in an accident.",
     "حادث",
     ["accidents (pl)", "accidental (adj)", "accidentally (adv)"]),

    (2,  "Astronaut",   "👨‍🚀", "noun",
     "An astronaut is a person who goes into outer space.",
     "The astronaut was walking on the moon.",
     "رائد فضاء",
     ["astronauts (pl)"]),

    (3,  "Awake",       "👀", "adjective",
     "A person who is awake is not asleep.",
     "Sometimes, I lay awake in bed because I am not tired.",
     "مستيقظ",
     ["awaken (v)", "awoke (past)"]),

    (4,  "Courage",     "🦁", "noun",
     "Courage is the feeling of not being afraid.",
     "The man had the courage to touch the lion.",
     "شجاعة",
     ["courageous (adj)", "courageously (adv)"]),

    (5,  "Float",       "🪵", "verb",
     "To float is to move on top of water without sinking.",
     "The boy's toy boat floated in the pool.",
     "يطفو",
     ["floats (v)", "floating (adj)", "floated (past)"]),

    (6,  "Grant",       "🎁", "verb",
     "To grant something is to allow someone to have it.",
     "The teacher granted us a break after studying hard all day.",
     "يمنح",
     ["grants (v)", "granted (past)"]),

    (7,  "Gravity",     "🌍", "noun",
     "Gravity is the force that makes things fall to Earth.",
     "There is no gravity in space.",
     "جاذبية",
     ["gravitational (adj)"]),

    (8,  "Jewel",       "💎", "noun",
     "A jewel is a beautiful stone that is worth a lot of money.",
     "A diamond is one of the most expensive jewels in the world.",
     "جوهرة",
     ["jewels (pl)", "jewelry (n)", "jeweler (n)"]),

    (9,  "Miner",       "⛏️", "noun",
     "A miner is a person who works in a mine.",
     "The miner was looking for gold.",
     "عامل منجم",
     ["miners (pl)", "mine (n/v)"]),

    (10, "Mineral",     "🪨", "noun",
     "A mineral is a type of substance found in the Earth.",
     "Rocks are made up of different kinds of minerals.",
     "معدن",
     ["minerals (pl)", "mineral (adj)"]),

    (11, "Participate", "🙋", "verb",
     "To participate is to be active and do something.",
     "The students participated in the school play.",
     "يشارك",
     ["participation (n)", "participant (n)"]),

    (12, "Permission",  "✅", "noun",
     "Permission means the act of allowing some action.",
     "I have permission to drive my mom's car.",
     "إذن",
     ["permissions (pl)", "permit (v/n)"]),

    (13, "Pour",        "🫗", "verb",
     "To pour a liquid means to make it come out of a container.",
     "I poured some milk into my sister's cup.",
     "يسكب",
     ["pours (v)", "poured (past)", "pouring (adj)"]),

    (14, "Raw",         "🥩", "adjective",
     "A raw material is natural and has not been processed.",
     "The company dumped raw sewage into the river.",
     "خام / نيء",
     ["rawness (n)"]),

    (15, "Satellite",   "🛰️", "noun",
     "A satellite is a machine sent into space to get information.",
     "The satellite was traveling around the Earth.",
     "قمر صناعي",
     ["satellites (pl)", "satellite (adj)"]),

    (16, "Scale",       "📏", "noun",
     "The scale of something is its size, especially when it is very large.",
     "I was surprised by the scale of the buildings in the downtown area.",
     "مقياس / حجم",
     ["scales (pl)", "scaled (adj)"]),

    (17, "Skip",        "⏭️", "verb",
     "To skip something is to not do it.",
     "He skipped work to get more sleep.",
     "يتخطى",
     ["skips (v)", "skipped (past)", "skipping (adj)"]),

    (18, "Stretch",     "🤸", "verb",
     "To stretch is to make your arms or legs reach out.",
     "She stretched her body before exercising.",
     "يمتد / يمد",
     ["stretches (v)", "stretched (past)", "stretchy (adj)"]),

    (19, "Telescope",   "🔭", "noun",
     "A telescope is a tool people use to look at the stars.",
     "With a telescope, you can see the moon and stars easily.",
     "تلسكوب",
     ["telescopes (pl)", "telescopic (adj)"]),

    (20, "Underground", "🚇", "adjective",
     "Underground action happens below the surface of the Earth.",
     "Subway trains travel underground.",
     "تحت الأرض",
     ["underground (adv)"]),
]

STORY_TITLE = "From the Earth to the Stars"

STORY_HTML = """
<p>Jeremy was from a family of <strong>miners</strong>. Like them, he worked <strong>underground</strong> during the day. His job was to find <strong>raw</strong> <strong>minerals</strong> and <strong>jewels</strong>. Each night after work, he lay <strong>awake</strong> in an open field. With his <strong>telescope</strong>, he looked at the stars. He was amazed by the <strong>scale</strong> of space. He wished someday he might travel there.</p>

<p>One day, there was an <strong>accident</strong> in the mine. Water <strong>poured</strong> into the mine. Everything was dark. Jeremy <strong>stretched</strong> out and grabbed a piece of wood. It kept him from sinking. For a long time, he <strong>floated</strong> in silence. Then, he heard voices. The other miners were coming to rescue him.</p>

<p>This accident made Jeremy think about his job and his life. The next day, he <strong>skipped</strong> work and made a very important decision. He had the <strong>courage</strong> to follow his decision. He decided to become an <strong>astronaut</strong>. For the next two years, Jeremy studied and trained hard. He completed his training, and one day, he was given <strong>permission</strong> to <strong>participate</strong> in a journey to space. His wish had been <strong>granted</strong>.</p>

<p>His spaceship left the ground. It went higher until there was no more <strong>gravity</strong>. Part of his job was to send out a <strong>satellite</strong> that would then float away from the spaceship. Now, instead of just looking at the stars, Jeremy could look at the Earth as well.</p>
"""

STORY_QUESTIONS = [
    {
        "q": "What was Jeremy's job at the beginning of the story?",
        "opts": [
            "He was an astronaut.",
            "He was a miner who worked underground.",
            "He was a teacher.",
            "He worked at a telescope factory."
        ],
        "ans": 1
    },
    {
        "q": "What happened to Jeremy during the accident in the mine?",
        "opts": [
            "He was hit by a falling rock.",
            "He got lost in the dark.",
            "Water poured in and he floated on a piece of wood.",
            "He was rescued by a satellite."
        ],
        "ans": 2
    },
    {
        "q": "What decision did Jeremy make after the accident?",
        "opts": [
            "He decided to find more jewels.",
            "He decided to become an astronaut.",
            "He decided to buy a telescope.",
            "He decided to teach other miners."
        ],
        "ans": 1
    },
    {
        "q": "What was Jeremy's job in space?",
        "opts": [
            "To look for minerals on the moon.",
            "To repair the spaceship.",
            "To send out a satellite.",
            "To take photos of jewels."
        ],
        "ans": 2
    },
    {
        "q": "What does the word 'gravity' mean in the story?",
        "opts": [
            "The force that makes things float in water.",
            "The force that makes things fall to Earth.",
            "A type of mineral found underground.",
            "The scale of a building."
        ],
        "ans": 1
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
print(f"Unit 21 seeded: {len(WORDS)} words, story '{STORY_TITLE}', {len(STORY_QUESTIONS)} questions.")
