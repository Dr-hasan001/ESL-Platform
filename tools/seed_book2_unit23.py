"""
Seed Book 2 Unit 23 — 4000 Essential English Words
Story: 48 Hours in Hong Kong
Run: python tools/seed_book2_unit23.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.book import Book, Unit, Word, UnitStory

Base.metadata.create_all(bind=engine)
db = SessionLocal()

book = db.query(Book).filter(Book.book_number == 2).first()
unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 23).first()
if not unit:
    print("ERROR: Unit 23 not found.")
    db.close()
    sys.exit(1)

WORDS = [
    (1,  "Best",       "🥇", "adjective",
     "The best person or thing is better than all the others.",
     "I got the best score on the math test.",
     "الأفضل",
     ["better (comp)"]),

    (2,  "Card",       "💳", "noun",
     "A card is a small piece of plastic or paper used to buy or use things.",
     "Adam used his library card to borrow a book.",
     "بطاقة",
     ["cards (pl)"]),

    (3,  "Crowd",      "👥", "noun",
     "A crowd is a large group of people who are together in one place.",
     "The crowd waved to the camera.",
     "حشد",
     ["crowds (pl)", "crowded (adj)"]),

    (4,  "Day",        "📅", "noun",
     "A day is a period of twenty-four hours, beginning at midnight.",
     "There are two more days until the weekend.",
     "يوم",
     ["days (pl)", "daily (adj/adv)"]),

    (5,  "Dish",       "🍽️", "noun",
     "A dish is a type of food that is cooked in a particular way.",
     "My favorite dish at the restaurant is chicken curry.",
     "طبق",
     ["dishes (pl)"]),

    (6,  "Easy",       "👌", "adjective",
     "An easy action is not difficult to do.",
     "Karen is happy because her English homework is easy.",
     "سهل",
     ["easier (comp)", "easily (adv)"]),

    (7,  "Experience", "🎢", "verb",
     "To experience is to do or see something, or have something happen to you.",
     "Going to the concert was the best thing I've ever experienced.",
     "يختبر / يجرب",
     ["experiences (v)", "experienced (adj/past)", "experience (n)"]),

    (8,  "Hotel",      "🏨", "noun",
     "A hotel is a place where people stay overnight when they are traveling.",
     "This family is staying at their favorite hotel.",
     "فندق",
     ["hotels (pl)"]),

    (9,  "Hour",       "⏰", "noun",
     "An hour is sixty minutes.",
     "The man waited for the train for over an hour.",
     "ساعة",
     ["hours (pl)", "hourly (adj/adv)"]),

    (10, "Light",      "💡", "noun",
     "Light is a form of energy or brightness that makes it possible to see something.",
     "I will turn on the light so that you can see.",
     "ضوء",
     ["lights (pl)", "lighting (n)", "light (adj)"]),

    (11, "Market",     "🛒", "noun",
     "A market is a place where people buy and sell products or food.",
     "I go to the market every weekend to buy vegetables.",
     "سوق",
     ["markets (pl)", "marketing (n)"]),

    (12, "Plan",       "📋", "verb",
     "To plan is to think about and arrange the details of something you want to do.",
     "It's Sam's turn to plan the company party.",
     "يخطط",
     ["plans (v)", "planned (past)", "plan (n)", "planning (n)"]),

    (13, "Price",      "💰", "noun",
     "The price is the amount of money needed to pay for something.",
     "Julie is checking the price of a sweater.",
     "سعر",
     ["prices (pl)", "pricing (n)"]),

    (14, "Short",      "📏", "adjective",
     "A short thing is not long or not tall.",
     "The days are short in the winter.",
     "قصير",
     ["shorter (comp)", "shortly (adv)"]),

    (15, "Shop",       "🛍️", "verb",
     "To shop is to visit places where goods are sold in order to look at and buy things.",
     "Tom decided to shop for groceries on his way home.",
     "يتسوق",
     ["shops (v)", "shopped (past)", "shopping (n)", "shop (n)"]),

    (16, "Station",    "🚉", "noun",
     "A station is a place where buses and trains stop for passengers.",
     "This man is waiting at the train station.",
     "محطة",
     ["stations (pl)"]),

    (17, "Surprise",   "🎁", "verb",
     "To surprise is to cause something that is unexpected.",
     "His parents decided to surprise him with a puppy.",
     "يفاجئ",
     ["surprises (v)", "surprised (adj/past)", "surprise (n)", "surprising (adj)"]),

    (18, "System",     "⚙️", "noun",
     "A system is a group of related parts that move or work together.",
     "This device controls the building's heating system.",
     "نظام",
     ["systems (pl)", "systematic (adj)"]),

    (19, "Taxi",       "🚖", "noun",
     "A taxi is a car and driver that you pay to take you somewhere.",
     "Gary drives a taxi, so he knows the roads very well.",
     "سيارة أجرة",
     ["taxis (pl)"]),

    (20, "Two",        "2️⃣", "noun",
     "Two is the word for the number 2.",
     "Two friends study together at the coffee shop.",
     "اثنان",
     []),
]

STORY_TITLE = "48 Hours in Hong Kong"

STORY_HTML = """
<p>Forty-eight <strong>hours</strong> in Hong Kong may sound like a <strong>short</strong> visit, but it will <strong>surprise</strong> you how much you can see and do. The <strong>best</strong> way to get the most out of your trip is to <strong>plan</strong> in advance.</p>

<p>Hong Kong has a great public transportation <strong>system</strong> that is <strong>easy</strong> to use. The system is called the MTR, which includes the metro, trains, and buses. You can get a <strong>card</strong> called the Octopus Card at a metro <strong>station</strong> and use it to travel around. <strong>Taxis</strong> are another way to get around Hong Kong. Not only are there many taxis everywhere, but they are also quite cheap compared to taxis in other large cities.</p>

<p>On the first <strong>day</strong> of your trip, go up Victoria Peak. At the top of the mountain, you will see beautiful city views. Then have 'dim sum' for lunch. Dim sum consists of many different <strong>dishes</strong>. It is a great way to taste a little bit of everything. After lunch, take the Star Ferry from Hong Kong Island and cruise across Victoria Harbor to Kowloon. There are many <strong>markets</strong> in this area: Temple Market and Ladies Market are very popular. At 8:00 pm, join the <strong>crowd</strong> that is watching the Symphony of Lights, which is a fifteen-minute <strong>light</strong> show around Hong Kong's tall buildings.</p>

<p>On the second day of your trip, spend your time <strong>shopping</strong> at one of Hong Kong's many malls, such as IFC or Times Square. You can also shop at smaller stores in Soho and Sheung Wan as well. Unlike the markets, the <strong>prices</strong> are set, so you cannot change them. After shopping, try an order of roast goose, which is similar to roast duck. Roast goose is a special dish in Hong Kong. If you want to <strong>experience</strong> Hong Kong's nightlife, head to Lan Kwai Fong. If not, go back to your <strong>hotel</strong> for a good night's rest.</p>

<p>With careful planning, you can do a lot in just <strong>two</strong> days in Hong Kong.</p>
"""

STORY_QUESTIONS = [
    {
        "q": "What is the best way to get the most out of a trip to Hong Kong?",
        "opts": [
            "Stay only one day.",
            "Travel only by taxi.",
            "Plan in advance.",
            "Skip the markets."
        ],
        "ans": 2
    },
    {
        "q": "What is the Octopus Card used for?",
        "opts": [
            "Buying dim sum at restaurants.",
            "Traveling on Hong Kong's MTR public transportation.",
            "Entering hotels.",
            "Shopping in malls only."
        ],
        "ans": 1
    },
    {
        "q": "Where can you see beautiful views of Hong Kong on the first day?",
        "opts": [
            "From the top of Victoria Peak.",
            "From the IFC mall.",
            "From the train station.",
            "From the hotel rooftop."
        ],
        "ans": 0
    },
    {
        "q": "What happens at 8:00 pm in Hong Kong?",
        "opts": [
            "All the markets close.",
            "Taxis stop running.",
            "The Symphony of Lights show takes place.",
            "Dim sum restaurants open."
        ],
        "ans": 2
    },
    {
        "q": "How are markets different from malls in Hong Kong?",
        "opts": [
            "Markets only sell food.",
            "Mall prices are set and cannot be changed.",
            "Markets are open only at night.",
            "Malls do not accept the Octopus Card."
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
print(f"Unit 23 seeded: {len(WORDS)} words, story '{STORY_TITLE}', {len(STORY_QUESTIONS)} questions.")
