"""
Seed Book 2 Unit 22 — 4000 Essential English Words
Story: The Farm Festival
Run: python tools/seed_book2_unit22.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.book import Book, Unit, Word, UnitStory

Base.metadata.create_all(bind=engine)
db = SessionLocal()

book = db.query(Book).filter(Book.book_number == 2).first()
unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 22).first()
if not unit:
    print("ERROR: Unit 22 not found.")
    db.close()
    sys.exit(1)

WORDS = [
    (1,  "Alarm",      "🚨", "noun",
     "An alarm is something that warns people of danger.",
     "When the students heard the fire alarm, they left the building.",
     "إنذار",
     ["alarms (pl)", "alarming (adj)"]),

    (2,  "Arrest",     "🚓", "verb",
     "To arrest someone means to catch that person for doing something bad.",
     "The man was arrested for breaking the law.",
     "يعتقل",
     ["arrests (v)", "arrested (past)", "arrest (n)"]),

    (3,  "Award",      "🏆", "noun",
     "An award is a prize for doing something well.",
     "He got an award for having the best grades in class.",
     "جائزة",
     ["awards (pl)", "award (v)"]),

    (4,  "Breed",      "🐕", "noun",
     "A breed is a group of animals within a species.",
     "I like small dog breeds, such as terriers.",
     "سلالة",
     ["breeds (pl)", "breed (v)", "breeding (n)"]),

    (5,  "Bucket",     "🪣", "noun",
     "A bucket is a round container to put things in.",
     "I filled the bucket with water.",
     "دلو",
     ["buckets (pl)"]),

    (6,  "Contest",    "🏅", "noun",
     "A contest is a game or a race.",
     "The girls had a contest to see who could jump higher.",
     "مسابقة",
     ["contests (pl)", "contest (v)", "contestant (n)"]),

    (7,  "Convict",    "⚖️", "verb",
     "To convict means to prove that someone did a bad thing.",
     "He was convicted of the crime and sent to jail.",
     "يدين",
     ["convicts (v)", "convicted (past)", "conviction (n)"]),

    (8,  "Festival",   "🎉", "noun",
     "A festival is an event that is held to celebrate a particular thing.",
     "I heard the song at the music festival in London.",
     "مهرجان",
     ["festivals (pl)", "festive (adj)"]),

    (9,  "Garage",     "🏠", "noun",
     "A garage is the part of a house where people put their cars.",
     "My car does not get dirty because I keep it in the garage.",
     "كراج / مرآب",
     ["garages (pl)"]),

    (10, "Journalist", "📰", "noun",
     "A journalist is a person who writes news stories.",
     "The journalist took notes for a story he was writing.",
     "صحفي",
     ["journalists (pl)", "journalism (n)", "journalistic (adj)"]),

    (11, "Pup",        "🐶", "noun",
     "A pup is a young dog.",
     "All the girl wanted for her birthday was a pup.",
     "جرو",
     ["pups (pl)", "puppy (n)"]),

    (12, "Qualify",    "✅", "verb",
     "To qualify is to have or do the things that are needed for something.",
     "He qualified to go to the final match by beating the opponent.",
     "يتأهل",
     ["qualifies (v)", "qualified (past)", "qualification (n)"]),

    (13, "Repair",     "🔧", "verb",
     "To repair something is to fix it.",
     "I repaired the flat tire on my car.",
     "يصلح",
     ["repairs (v)", "repaired (past)", "repair (n)"]),

    (14, "Resume",     "🔄", "verb",
     "To resume something means to start it again after taking a break.",
     "I put the newspaper down to eat breakfast. Then, I resumed reading.",
     "يستأنف",
     ["resumes (v)", "resumed (past)", "resumption (n)"]),

    (15, "Rob",        "🥷", "verb",
     "To rob is to take property by using force.",
     "A thief has robbed me of my passport.",
     "يسرق",
     ["robs (v)", "robbed (past)", "robber (n)", "robbery (n)"]),

    (16, "Slip",       "🪨", "verb",
     "To slip means to slide and fall down.",
     "The man slipped on the wet floor.",
     "ينزلق",
     ["slips (v)", "slipped (past)", "slippery (adj)"]),

    (17, "Somewhat",   "🤏", "adverb",
     "Somewhat means to some degree, but not to a large degree.",
     "James was somewhat upset when he had to move heavy boxes.",
     "إلى حد ما",
     []),

    (18, "Stable",     "⚖️", "adjective",
     "A stable thing will not move, change, or fall over.",
     "The chair is stable. Its legs are strong.",
     "ثابت",
     ["stably (adv)", "stability (n)"]),

    (19, "Tissue",     "🧻", "noun",
     "A tissue is a soft piece of paper people use to wipe their noses.",
     "There was a box of tissue on the table.",
     "منديل ورقي",
     ["tissues (pl)"]),

    (20, "Yard",       "🌳", "noun",
     "A yard is the ground just outside of a house.",
     "The girls jumped rope in the yard.",
     "فناء / حديقة",
     ["yards (pl)"]),
]

STORY_TITLE = "The Farm Festival"

STORY_HTML = """
<p>Once there was a farm. Many animals lived there. One day, they had a <strong>contest</strong> in the <strong>yard</strong>. They were going to race from the barn to the farmer's <strong>garage</strong>. The barn and the garage were far apart. It would be a long race. The winner <strong>qualified</strong> to win a bag full of apples as an <strong>award</strong>.</p>

<p>But the race did not start well. The cart with all the apples was not <strong>stable</strong>, and the animals had to <strong>repair</strong> it. Then, the <strong>pup</strong> knocked over the apples. The pig said, "We are going to <strong>slip</strong>! We must clean up this mess." The pup felt bad, and she began to cry. The dog gave her a <strong>tissue</strong> to dry her tears.</p>

<p>Then, the race <strong>resumed</strong>. But the duck tried to <strong>rob</strong> them and take all the apples. The cat said, "I will have you <strong>arrested</strong>!" The duck said, "You can't <strong>convict</strong> me! You can't prove I took them." The race stopped yet again.</p>

<p>The animals tried to race one more time. Then, they heard an <strong>alarm</strong> coming from the barn. There was a fire! They got <strong>buckets</strong> of water to put out the fire. A <strong>journalist</strong> came to write a story about the <strong>festival</strong> and the race. The horse told her, "I am a special <strong>breed</strong> of horse. I would have won the race easily." The pig said, "It was <strong>somewhat</strong> hard to have the race. But we had fun. That is what's important!"</p>
"""

STORY_QUESTIONS = [
    {
        "q": "Where were the animals racing from and to?",
        "opts": [
            "From the garage to the barn.",
            "From the barn to the farmer's garage.",
            "From the yard to the festival.",
            "Around the apple cart."
        ],
        "ans": 1
    },
    {
        "q": "What was the prize for the winner?",
        "opts": [
            "A bag of apples.",
            "A new pup.",
            "A trophy.",
            "Free tissues."
        ],
        "ans": 0
    },
    {
        "q": "Why did the cart need to be repaired?",
        "opts": [
            "The duck broke it.",
            "It was on fire.",
            "It was not stable.",
            "The journalist crashed into it."
        ],
        "ans": 2
    },
    {
        "q": "What did the duck try to do during the race?",
        "opts": [
            "Win the contest.",
            "Rob the animals of the apples.",
            "Repair the cart.",
            "Put out the fire."
        ],
        "ans": 1
    },
    {
        "q": "Why did the race stop the third time?",
        "opts": [
            "The pup got tired.",
            "The journalist asked too many questions.",
            "There was a fire alarm from the barn.",
            "The pig fell asleep."
        ],
        "ans": 2
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
print(f"Unit 22 seeded: {len(WORDS)} words, story '{STORY_TITLE}', {len(STORY_QUESTIONS)} questions.")
