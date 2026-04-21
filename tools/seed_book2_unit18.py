"""
seed_book2_unit18.py
Seeds Unit 18 vocabulary and story "The Priest" for Book 2.
Content extracted from 4000 Essential English Words Book 2.

Run: python tools/seed_book2_unit18.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.book import Book, Unit, Word, UnitStory

Base.metadata.create_all(bind=engine)
db = SessionLocal()

book = db.query(Book).filter(Book.book_number == 2).first()
unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 18).first()
if not unit:
    print("ERROR: Unit 18 not found.")
    db.close()
    sys.exit(1)

# ── 1. Replace vocabulary (exact definitions & examples from the book) ─────────
db.query(Word).filter(Word.unit_id == unit.id).delete()

WORDS = [
    (1,  "Ability",     "⭐", "noun",
     "Ability is the quality of a person being able to do something well.",
     "His swimming abilities let him cross the entire lake.",
     "قدرة / موهبة",
     ["abilities (pl)", "able (adj)"]),

    (2,  "Agriculture", "🌾", "noun",
     "Agriculture is the growing of plants and raising of animals for food.",
     "The farmer studied agriculture in college.",
     "زراعة",
     ["agricultural (adj)", "agriculturalist (n)"]),

    (3,  "Cartoon",     "🖼️", "noun",
     "A cartoon is a funny drawing.",
     "Sometimes, people draw cartoons for the newspaper.",
     "رسم كاريكاتير",
     ["cartoons (pl)", "cartoonist (n)"]),

    (4,  "Ceiling",     "🏠", "noun",
     "The ceiling is the top of a room.",
     "He painted the ceiling with a special roller.",
     "سقف",
     ["ceilings (pl)"]),

    (5,  "Convince",    "🗣️", "verb",
     "To convince someone means to make that person sure of something.",
     "She convinced me to buy the house.",
     "يُقنع",
     ["convinces", "convinced", "convincing (adj)"]),

    (6,  "Curious",     "🔍", "adjective",
     "A curious person or animal wants to know about something.",
     "I opened up the clock because I was curious about how it worked.",
     "فضولي",
     ["curiously (adv)", "curiosity (n)"]),

    (7,  "Delay",       "⏳", "verb",
     "To delay means to wait to do something.",
     "I was delayed at the airport for over two hours.",
     "يؤجّل / يتأخر",
     ["delays", "delayed", "delay (n)"]),

    (8,  "Diary",       "📔", "noun",
     "A diary is a book in which people write their personal experiences.",
     "I do not let anybody read my diary.",
     "مذكرة يومية",
     ["diaries (pl)"]),

    (9,  "Element",     "🧩", "noun",
     "An element of something is a particular part of it.",
     "Tackling an opponent is Johnny's favorite element of American football.",
     "عنصر / جزء",
     ["elements (pl)", "elementary (adj)"]),

    (10, "Faith",       "🙏", "noun",
     "Faith is trust or belief without proof.",
     "The sick girl had faith in doctors. She knew they would make her better.",
     "إيمان / ثقة",
     ["faithful (adj)", "faithfully (adv)"]),

    (11, "Grain",       "🌾", "noun",
     "A grain is a food crop such as wheat, corn, rice, or oats.",
     "The farmer planted two fields of grain this year.",
     "حبوب / محاصيل",
     ["grains (pl)", "grainy (adj)"]),

    (12, "Greet",       "👋", "verb",
     "To greet someone means to meet and welcome that person.",
     "When my friend came over, I greeted him at the door.",
     "يرحّب / يسلّم",
     ["greets", "greeted", "greeting (n)"]),

    (13, "Investigate", "🔎", "verb",
     "To investigate means to search for something or learn about it.",
     "The detective went to investigate the crime.",
     "يحقق / يتحقق",
     ["investigates", "investigated", "investigation (n)"]),

    (14, "Joy",         "😄", "noun",
     "Joy is a feeling of great happiness.",
     "I love baseball. I feel joy when I play.",
     "بهجة / فرح",
     ["joys (pl)", "joyful (adj)", "joyfully (adv)"]),

    (15, "Label",       "🏷️", "noun",
     "A label is a tag that tells about something.",
     "The label on the back of your shirt will tell you what size it is.",
     "ملصق / تسمية",
     ["labels (pl)", "label (v)", "labeled (adj)"]),

    (16, "Monk",        "🧘", "noun",
     "A monk is a religious person who lives a simple life.",
     "The monks knew a lot about religion.",
     "راهب",
     ["monks (pl)", "monastery (n)"]),

    (17, "Odd",         "🤨", "adjective",
     "Something odd is unusual.",
     "Her cat is odd. It walks on two feet.",
     "غريب / عجيب",
     ["oddly (adv)", "oddness (n)"]),

    (18, "Pause",       "⏸️", "verb",
     "To pause means to stop doing something for a while.",
     "Since she was so hungry, she paused to make a snack.",
     "يتوقف / يقف لحظة",
     ["pauses", "paused", "pause (n)"]),

    (19, "Priest",      "⛪", "noun",
     "A priest is a person trained to perform religious duties.",
     "The priest taught us about God.",
     "كاهن / قسيس",
     ["priests (pl)", "priesthood (n)"]),

    (20, "Profession",  "💼", "noun",
     "A profession is a person's job.",
     "He loved sailing, so he chose to work on ships as a profession.",
     "مهنة",
     ["professions (pl)", "professional (adj/n)"]),
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
print(f"Replaced vocabulary: {len(WORDS)} words for Unit 18.")

# ── 2. Story ──────────────────────────────────────────────────────────────────
STORY_HTML = """
<p>
  A young <span class="vocab">priest</span> was always sad. He was good at his
  <span class="vocab">profession</span>, but he still had no
  <span class="vocab">joy</span>. He visited a group of
  <span class="vocab">monks</span>.
</p>

<p>
  He went to the monks' house. They <span class="vocab">greeted</span> him and
  let him in. The monks asked the priest, "What is the matter?" The priest said,
  "I should be happy. But I am not. I don't know what to do." One of the monks
  <span class="vocab">paused</span> for a minute. Then he said, "We are
  <span class="vocab">convinced</span> of your <span class="vocab">faith</span>.
  You are a very good priest. But to find joy, you must
  <span class="vocab">investigate</span> your own life. Look at every
  <span class="vocab">element</span> of it and find what makes you happy."
  The priest thought the answer was <span class="vocab">odd</span>, but he was
  <span class="vocab">curious</span>.
</p>

<p>
  The next day, the priest thought about his
  <span class="vocab">abilities</span>. He got a few ideas, and he did not want
  to <span class="vocab">delay</span> any longer. He liked to draw, so he made
  some <span class="vocab">cartoons</span>. He also liked to write, so he started
  a <span class="vocab">diary</span>. He was interested in
  <span class="vocab">agriculture</span>, so he planted some
  <span class="vocab">grain</span>. He made jam from his fruit. He made his own
  <span class="vocab">labels</span> to put on the jars of jam. He painted his
  <span class="vocab">ceiling</span>.
</p>

<p>
  The priest learned something. It is not too hard to be happy after all.
  All one has to do is find things one likes doing — and do them.
</p>
"""

QUESTIONS = [
    # Q1 correct A(0)
    {
        "q": "Why was the young priest sad?",
        "opts": [
            "He had no joy, even though he was good at his profession.",
            "He did not like the monks he worked with.",
            "He was not good at his job.",
            "He had no friends in the village.",
        ],
        "ans": 0,
    },
    # Q2 correct B(1)
    {
        "q": "Where did the priest go to get help?",
        "opts": [
            "To a hospital.",
            "To a group of monks.",
            "To his family home.",
            "To a school.",
        ],
        "ans": 1,
    },
    # Q3 correct C(2)
    {
        "q": "What did the monk tell the priest to investigate?",
        "opts": [
            "His profession.",
            "The lives of other priests.",
            "His own life and what makes him happy.",
            "The history of the monastery.",
        ],
        "ans": 2,
    },
    # Q4 correct D(3)
    {
        "q": "How did the priest feel about the monk's advice at first?",
        "opts": [
            "He was angry and left immediately.",
            "He was very happy and understood at once.",
            "He was convinced right away.",
            "He thought it was odd, but he was curious.",
        ],
        "ans": 3,
    },
    # Q5 correct A(0)
    {
        "q": "What did the priest make because he liked to draw?",
        "opts": [
            "Cartoons.",
            "Labels for jars.",
            "A diary.",
            "Paintings of monks.",
        ],
        "ans": 0,
    },
    # Q6 correct B(1)
    {
        "q": "What did the priest start because he liked to write?",
        "opts": [
            "A letter to the monks.",
            "A diary.",
            "A book about his profession.",
            "A list of his abilities.",
        ],
        "ans": 1,
    },
    # Q7 correct C(2)
    {
        "q": "What did the priest plant because he was interested in agriculture?",
        "opts": [
            "Flowers.",
            "Vegetables.",
            "Grain.",
            "Trees.",
        ],
        "ans": 2,
    },
    # Q8 correct A(0)
    {
        "q": "What did the priest put his own labels on?",
        "opts": [
            "Jars of jam.",
            "His paintings.",
            "His diary.",
            "His cartoons.",
        ],
        "ans": 0,
    },
    # Q9 correct D(3)
    {
        "q": "Which of these did the priest NOT do to find happiness?",
        "opts": [
            "Draw cartoons.",
            "Plant grain.",
            "Paint his ceiling.",
            "Learn a new profession.",
        ],
        "ans": 3,
    },
    # Q10 correct B(1)
    {
        "q": "What was the lesson the priest learned?",
        "opts": [
            "A good priest must always visit monks.",
            "Happiness comes from doing things you like.",
            "Agriculture is the best way to feel joy.",
            "It is impossible to be happy in a difficult profession.",
        ],
        "ans": 1,
    },
]

existing = db.query(UnitStory).filter(UnitStory.unit_id == unit.id).first()
if existing:
    existing.story_title = "The Priest"
    existing.story_html = STORY_HTML
    existing.story_questions = QUESTIONS
    print("Updated story: 'The Priest'")
else:
    db.add(UnitStory(
        unit_id=unit.id,
        story_title="The Priest",
        story_html=STORY_HTML,
        story_questions=QUESTIONS,
    ))
    print("Created story: 'The Priest'")

db.commit()
print(f"Done — {len(QUESTIONS)} questions saved.")
db.close()
