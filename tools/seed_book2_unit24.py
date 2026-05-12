"""
Seed Book 2 Unit 24 — 4000 Essential English Words
Story: The Doctor's Cure
Run: python tools/seed_book2_unit24.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.book import Book, Unit, Word, UnitStory

Base.metadata.create_all(bind=engine)
db = SessionLocal()

book = db.query(Book).filter(Book.book_number == 2).first()
unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 24).first()
if not unit:
    print("ERROR: Unit 24 not found.")
    db.close()
    sys.exit(1)

WORDS = [
    (1,  "Bath",       "🛁", "noun",
     "A bath is the act of sitting in a tub of water in order to get clean.",
     "After playing in the dirt, the boy took a bath.",
     "حمام / استحمام",
     ["baths (pl)", "bathe (v)"]),

    (2,  "Bend",       "🪢", "verb",
     "To bend is to move something so it is not straight.",
     "Lee bent over and picked up the paper on the ground.",
     "ينحني / يثني",
     ["bends (v)", "bent (past)", "bending (n)"]),

    (3,  "Chew",       "🍖", "verb",
     "To chew is to break up food by using the mouth and teeth.",
     "I always chew my food carefully before swallowing it.",
     "يمضغ",
     ["chews (v)", "chewed (past)", "chewing (n)"]),

    (4,  "Disabled",   "♿", "adjective",
     "A disabled person has a physical problem that makes some activities difficult.",
     "The disabled man used a wheelchair to move around.",
     "معاق",
     ["disability (n)", "disable (v)"]),

    (5,  "Fantastic",  "🤩", "adjective",
     "A fantastic thing is really good.",
     "The student did a fantastic job on his project and got an award.",
     "رائع",
     ["fantastically (adv)"]),

    (6,  "Fiction",    "📖", "noun",
     "Fiction is a story that is not true.",
     "I enjoy reading works of fiction because they are very entertaining.",
     "خيال / قصص خيالية",
     ["fictional (adj)", "fictitious (adj)"]),

    (7,  "Flag",       "🚩", "noun",
     "A flag is a piece of colored cloth that represents something.",
     "Our country has a beautiful flag.",
     "علم / راية",
     ["flags (pl)"]),

    (8,  "Inspect",    "🔍", "verb",
     "To inspect is to look at something carefully.",
     "The mechanic inspected our car to see if it had any problems.",
     "يفحص",
     ["inspects (v)", "inspected (past)", "inspection (n)", "inspector (n)"]),

    (9,  "Journal",    "📔", "noun",
     "A journal is a type of magazine that deals with an academic subject.",
     "Mi-young was busy working on an article for an art journal.",
     "مجلة علمية / دورية",
     ["journals (pl)", "journalist (n)"]),

    (10, "Liquid",     "💧", "noun",
     "A liquid is a substance that is neither solid nor gas.",
     "Water is the most important liquid for life.",
     "سائل",
     ["liquids (pl)"]),

    (11, "Marvel",     "😮", "verb",
     "To marvel at something is to feel surprise and interest in it.",
     "We marveled at her excellent piano playing.",
     "يندهش / يتعجب",
     ["marvels (v)", "marveled (past)", "marvelous (adj)"]),

    (12, "Overcome",   "💪", "verb",
     "To overcome a problem is to successfully fix it.",
     "She overcame her shyness and spoke in front of the class.",
     "يتغلب على",
     ["overcomes (v)", "overcame (past)", "overcoming (n)"]),

    (13, "Recall",     "🧠", "verb",
     "To recall something is to remember it.",
     "She was trying to recall what she had told her friend.",
     "يتذكر",
     ["recalls (v)", "recalled (past)", "recall (n)"]),

    (14, "Regret",     "😔", "verb",
     "To regret something is to wish that it hadn't happened.",
     "I regret that I was mean to my sister.",
     "يندم",
     ["regrets (v)", "regretted (past)", "regretful (adj)"]),

    (15, "Soul",       "✨", "noun",
     "A soul is a person's spirit.",
     "Some people believe that the soul lives after the body dies.",
     "روح",
     ["souls (pl)", "soulful (adj)"]),

    (16, "Sufficient", "✅", "adjective",
     "Sufficient shows that something is enough, in quality or quantity.",
     "After eating a sufficient amount of food, I left the table.",
     "كافٍ",
     ["sufficiently (adv)", "sufficiency (n)"]),

    (17, "Surgery",    "🩺", "noun",
     "Surgery is medical treatment involving a doctor cutting into a body.",
     "I agreed to surgery to repair my leg after the accident.",
     "جراحة",
     ["surgeries (pl)", "surgical (adj)", "surgeon (n)"]),

    (18, "Tough",      "😤", "adjective",
     "A tough thing is difficult.",
     "The man passed his driving test even though it was very tough.",
     "صعب / قاسٍ",
     ["tougher (comp)", "toughness (n)"]),

    (19, "Tube",       "🪈", "noun",
     "A tube is a pipe through which water or air passes.",
     "The pile of tubes was going to be put in the ground.",
     "أنبوب",
     ["tubes (pl)", "tubular (adj)"]),

    (20, "Value",      "💎", "noun",
     "The value of something is what it is worth.",
     "Your love for me has greater value than gold.",
     "قيمة",
     ["values (pl)", "valuable (adj)", "value (v)"]),
]

STORY_TITLE = "The Doctor's Cure"

STORY_HTML = """
<p>James Fry was a <strong>fantastic</strong> doctor. His <strong>surgery</strong> helped many <strong>disabled</strong> people <strong>overcome</strong> their problems. He also wrote for a popular doctors' <strong>journal</strong>. James was very busy. His son, Steve, rarely saw him.</p>

<p>One day, James was walking and <strong>inspecting</strong> a patient's file. There was water all over the floor. James slipped on the <strong>liquid</strong> and fell. He fell on a broken glass <strong>tube</strong>. He was hurt. Steve came to visit him in the hospital. James said, "It will be <strong>tough</strong> for me to stay in bed. But I can hardly <strong>bend</strong> my legs."</p>

<p>"Then let's watch a movie," Steve said. It made them laugh together. Steve said, "I have to leave, but here's some <strong>fiction</strong> to read."</p>

<p>James started to <strong>recall</strong> fun parts of life. He <strong>marveled</strong> at small things, like food. He was too busy to notice them before. "Steve," he said, "you get more food <strong>value</strong> when you <strong>chew</strong> slowly. But I think it makes food taste better, too!"</p>

<p>Weeks later, James said, "Steve, I haven't spent enough time with you. I <strong>regret</strong> this. Even my <strong>soul</strong> feels better when you visit. But I have spent <strong>sufficient</strong> time here. We should go home."</p>

<p>Outside, there was a warm breeze. James watched a <strong>flag</strong> blow.</p>

<p>Finally, James said, "I'm still not ready to work. I'm going to take a long <strong>bath</strong>. And then we'll watch a movie together. I'll start work tomorrow, and this time I will not work too hard."</p>
"""

STORY_QUESTIONS = [
    {
        "q": "What kind of doctor was James Fry?",
        "opts": [
            "A new doctor with little experience.",
            "A fantastic doctor whose surgery helped disabled people overcome problems.",
            "A doctor who only wrote articles.",
            "A doctor who never saw patients."
        ],
        "ans": 1
    },
    {
        "q": "How did James get hurt?",
        "opts": [
            "He fell off a ladder.",
            "He slipped on liquid and fell on a broken glass tube.",
            "A patient pushed him.",
            "His car had an accident."
        ],
        "ans": 1
    },
    {
        "q": "What did James say about chewing food slowly?",
        "opts": [
            "It makes you feel sick.",
            "You get more food value and it tastes better.",
            "It is bad for your teeth.",
            "It makes meals take too long."
        ],
        "ans": 1
    },
    {
        "q": "What did James regret?",
        "opts": [
            "Becoming a doctor.",
            "Slipping in the hospital.",
            "Not spending enough time with his son Steve.",
            "Reading fiction books."
        ],
        "ans": 2
    },
    {
        "q": "What did James plan to do when he got home?",
        "opts": [
            "Go right back to work.",
            "Travel around the world.",
            "Take a long bath, then watch a movie with Steve.",
            "Write another article."
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
print(f"Unit 24 seeded: {len(WORDS)} words, story '{STORY_TITLE}', {len(STORY_QUESTIONS)} questions.")
