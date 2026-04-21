"""
seed_book2_unit9_real.py
Replaces Unit 9 vocabulary and story with the real content from
4000 Essential English Words — "The Starfish".

Run: python tools/seed_book2_unit9_real.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.book import Book, Unit, Word, UnitStory

Base.metadata.create_all(bind=engine)
db = SessionLocal()

book = db.query(Book).filter(Book.book_number == 2).first()
unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 9).first()
if not unit:
    print("ERROR: Unit 9 not found.")
    db.close()
    sys.exit(1)

# ── 1. Replace vocabulary with real unit words ────────────────────────────────
db.query(Word).filter(Word.unit_id == unit.id).delete()

WORDS = [
    (1,  "Against",   "🤜", "preposition",
     "Against means touching, leaning on, or in the opposite direction of something.",
     "She leaned against the wall and closed her eyes.",
     "ضد / مقابل",
     []),

    (2,  "Beach",     "🏖️", "noun",
     "A beach is an area of sand or small stones next to the sea.",
     "We played on the beach all afternoon.",
     "شاطئ",
     ["beaches (pl)", "beachside (adj)"]),

    (3,  "Damage",    "💥", "verb",
     "To damage something means to break or harm it.",
     "The storm damaged many houses in the town.",
     "يتلف / يضر",
     ["damages", "damaged", "damage (n)"]),

    (4,  "Discover",  "🔍", "verb",
     "To discover something means to find or learn about it for the first time.",
     "She discovered a beautiful waterfall on her walk.",
     "يكتشف",
     ["discovers", "discovered", "discovery (n)"]),

    (5,  "Emotion",   "❤️", "noun",
     "An emotion is a strong feeling such as happiness, sadness, or fear.",
     "She could not hide her emotion when she said goodbye.",
     "مشاعر / عاطفة",
     ["emotions (pl)", "emotional (adj)", "emotionally (adv)"]),

    (6,  "Fix",       "🔧", "verb",
     "To fix something means to repair it or to solve a problem.",
     "Can you fix the broken chair before the guests arrive?",
     "يصلح / يحل",
     ["fixes", "fixed", "fixer (n)"]),

    (7,  "Identify",  "🔎", "verb",
     "To identify something means to recognize and say what it is.",
     "Can you identify the bird in this photo?",
     "يُحدّد / يتعرّف على",
     ["identifies", "identified", "identification (n)"]),

    (8,  "Island",    "🏝️", "noun",
     "An island is a piece of land that is completely surrounded by water.",
     "We took a boat to reach the small island.",
     "جزيرة",
     ["islands (pl)", "islander (n)"]),

    (9,  "Ocean",     "🌊", "noun",
     "An ocean is a very large area of salt water that covers much of the Earth.",
     "Many unusual creatures live deep in the ocean.",
     "محيط",
     ["oceans (pl)", "oceanic (adj)"]),

    (10, "Perhaps",   "🤔", "adverb",
     "Perhaps means possibly or maybe — used when you are not sure about something.",
     "Perhaps we can visit the island again next summer.",
     "ربما / لعل",
     []),

    (11, "Pleasant",  "😊", "adjective",
     "Something pleasant is enjoyable, nice, or easy to like.",
     "We had a very pleasant walk along the river.",
     "ممتع / لطيف",
     ["pleasantly (adv)", "pleasantness (n)", "unpleasant (opp)"]),

    (12, "Prevent",   "🛑", "verb",
     "To prevent something means to stop it from happening.",
     "We must prevent pollution to protect the ocean.",
     "يمنع",
     ["prevents", "prevented", "prevention (n)"]),

    (13, "Rock",      "🪨", "noun",
     "A rock is a large, hard piece of stone.",
     "He sat on a rock by the river and thought quietly.",
     "صخرة",
     ["rocks (pl)", "rocky (adj)"]),

    (14, "Save",      "🦸", "verb",
     "To save someone means to rescue them from danger or harm.",
     "The lifeguard jumped into the water to save the child.",
     "ينقذ",
     ["saves", "saved", "savior (n)"]),

    (15, "Smile",     "😄", "verb",
     "To smile means to make a happy expression by turning the corners of your mouth up.",
     "She smiled when she saw her best friend.",
     "يبتسم",
     ["smiles", "smiled", "smile (n)"]),

    (16, "Step",      "👣", "verb",
     "To step means to move your foot carefully in a particular direction.",
     "She stepped over the puddle so she would not get wet.",
     "يخطو / يمشي بحذر",
     ["steps", "stepped", "step (n)"]),

    (17, "Still",     "🧘", "adverb",
     "Still means continuing to happen or be true at a certain time.",
     "The starfish were still on the beach when we arrived.",
     "لا يزال / ما زال",
     ["stillness (n)", "still (adj)"]),

    (18, "Taste",     "👅", "noun",
     "The taste of food or drink is the particular quality it has in your mouth.",
     "The soup had a strong and spicy taste.",
     "طعم / مذاق",
     ["tastes (pl)", "taste (v)", "tasty (adj)"]),

    (19, "Throw",     "🎯", "verb",
     "To throw something means to use your hand to send it through the air.",
     "He threw the ball as far as he could.",
     "يرمي / يقذف",
     ["throws", "threw (past)", "thrown (pp)", "throw (n)"]),

    (20, "Wave",      "🌊", "noun",
     "A wave is a raised line of water that moves across the surface of the sea.",
     "The children played in the waves at the beach.",
     "موجة",
     ["waves (pl)", "wave (v)", "wavy (adj)"]),
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
print(f"Replaced vocabulary: {len(WORDS)} words for Unit 9.")

# ── 2. Replace story with real "The Starfish" content ─────────────────────────
STORY_HTML = """
<p>
  Last summer I took a trip to an <span class="vocab">island</span>.
  I sat and watched the <span class="vocab">waves</span> and listened to the
  <span class="vocab">ocean</span>. I <span class="vocab">discovered</span>
  new things and enjoyed the <span class="vocab">taste</span> of different
  foods. It was a very <span class="vocab">pleasant</span> experience.
</p>

<p>
  One morning I went for a walk along the <span class="vocab">beach</span>.
  When the waves came in, many starfish fell onto the shore. Some went back
  into the water and were safe. But other starfish were
  <span class="vocab">still</span> on the dry sand. They would die if they
  did not reach the water. I <span class="vocab">stepped</span> very carefully
  so I did not <span class="vocab">damage</span> them.
</p>

<p>
  Then I saw a little girl. She tried to
  <span class="vocab">identify</span> which starfish were still alive. She
  wanted to <span class="vocab">prevent</span> them from dying. She felt a
  strong <span class="vocab">emotion</span> — she could not stand there and
  do nothing.
</p>

<p>
  "I don't think we can do anything," I said. She sat
  <span class="vocab">against</span> a <span class="vocab">rock</span>
  and thought for a while. Then she stood up with a
  <span class="vocab">smile</span>. She picked up a starfish and
  <span class="vocab">threw</span> it into the water.
</p>

<p>
  "What are you doing?" I asked. "<span class="vocab">Perhaps</span>
  I can <span class="vocab">fix</span> this!" she said. She kept throwing
  starfish into the ocean. "You cannot <span class="vocab">save</span>
  all of them!" I told her.
</p>

<p>
  She stopped and looked at me. "No, I cannot save them all." Then she picked
  up another starfish and smiled at it. "But I can save <em>this</em> one."
  And she threw the starfish as far as she could into the ocean.
</p>
"""

QUESTIONS = [
    {
        "q": "Where did the narrator go last summer?",
        "opts": [
            "To an island.",
            "To a mountain.",
            "To a forest.",
            "To a city.",
        ],
        "ans": 0,
    },
    {
        "q": "Why were the starfish in danger on the beach?",
        "opts": [
            "Because people were stepping on them.",
            "Because they would die if they did not get back into the water.",
            "Because the waves were too strong.",
            "Because it was too cold.",
        ],
        "ans": 1,
    },
    {
        "q": "Why did the narrator step carefully?",
        "opts": [
            "Because the sand was very hot.",
            "Because the waves were coming in.",
            "Because he did not want to damage the starfish.",
            "Because the girl asked him to.",
        ],
        "ans": 2,
    },
    {
        "q": "What did the girl try to do first?",
        "opts": [
            "Throw all the starfish into the water.",
            "Ask the narrator for help.",
            "Identify which starfish were still alive.",
            "Build a sandcastle on the beach.",
        ],
        "ans": 2,
    },
    {
        "q": "What emotion did the girl feel when she saw the starfish?",
        "opts": [
            "She felt bored and walked away.",
            "She felt afraid of the waves.",
            "She felt angry at the narrator.",
            "She felt a strong emotion and could not do nothing.",
        ],
        "ans": 3,
    },
    {
        "q": "What did the narrator say to the girl at first?",
        "opts": [
            "\"I will help you.\"",
            "\"That is a great idea.\"",
            "\"Be careful near the water.\"",
            "\"I don't think we can do anything.\"",
        ],
        "ans": 3,
    },
    {
        "q": "What did the girl do after she sat against the rock?",
        "opts": [
            "She went home.",
            "She stood up with a smile and threw a starfish into the water.",
            "She asked the narrator to help again.",
            "She started to cry.",
        ],
        "ans": 1,
    },
    {
        "q": "What did the girl say when she started throwing starfish?",
        "opts": [
            "\"You cannot save all of them!\"",
            "\"I will save every single one.\"",
            "\"Perhaps I can fix this!\"",
            "\"Help me throw them in.\"",
        ],
        "ans": 2,
    },
    {
        "q": "What was the girl's answer to \"You cannot save all of them\"?",
        "opts": [
            "\"I know, but I have to try.\"",
            "\"Yes, you are right. I will stop.\"",
            "\"We can save them all if you help.\"",
            "\"No — but I can save this one.\"",
        ],
        "ans": 3,
    },
    {
        "q": "What is the main lesson of the story?",
        "opts": [
            "One small action can still make a difference.",
            "It is impossible to help everyone.",
            "The ocean is a dangerous place.",
            "Children are braver than adults.",
        ],
        "ans": 0,
    },
]

existing = db.query(UnitStory).filter(UnitStory.unit_id == unit.id).first()
if existing:
    existing.story_title = "The Starfish"
    existing.story_html = STORY_HTML
    existing.story_questions = QUESTIONS
    print("Updated story: 'The Starfish'")
else:
    db.add(UnitStory(
        unit_id=unit.id,
        story_title="The Starfish",
        story_html=STORY_HTML,
        story_questions=QUESTIONS,
    ))
    print("Created story: 'The Starfish'")

db.commit()
print(f"Done — {len(QUESTIONS)} questions saved.")
db.close()
