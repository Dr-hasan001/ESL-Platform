"""
Seed Book 2 Unit 25 — 4000 Essential English Words
Story: How Comet Got His Tail
Run: python tools/seed_book2_unit25.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.book import Book, Unit, Word, UnitStory

Base.metadata.create_all(bind=engine)
db = SessionLocal()

book = db.query(Book).filter(Book.book_number == 2).first()
unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 25).first()
if not unit:
    print("ERROR: Unit 25 not found.")
    db.close()
    sys.exit(1)

WORDS = [
    (1,  "Atom",       "⚛️", "noun",
     "An atom is the smallest unit of a substance.",
     "A molecule consists of a combination of two or more atoms.",
     "ذرة",
     ["atoms (pl)", "atomic (adj)"]),

    (2,  "Beautiful",  "🌅", "adjective",
     "A beautiful thing is good to look at.",
     "There was a beautiful sunset.",
     "جميل",
     ["beauty (n)", "beautifully (adv)"]),

    (3,  "Breadth",    "📐", "noun",
     "Breadth is the distance from one side to the other side of something.",
     "The breadth of the northern wall of the house is twenty meters.",
     "عرض / اتساع",
     ["broad (adj)", "broaden (v)"]),

    (4,  "Comet",      "☄️", "noun",
     "A comet is an object in space made of ice and rock with a tail of glowing dust.",
     "Comets take many decades to complete an orbit around a star.",
     "مذنّب",
     ["comets (pl)"]),

    (5,  "Cover",      "🛡️", "verb",
     "To cover something is to put things over it.",
     "The Earth was covered with clouds.",
     "يغطي",
     ["covers (v)", "covered (past)", "covering (n)"]),

    (6,  "Despair",    "😞", "noun",
     "Despair is the feeling of having no hope.",
     "After we lost the big account, our salespeople were filled with despair.",
     "يأس",
     ["despair (v)", "desperate (adj)"]),

    (7,  "Form",       "🧱", "verb",
     "To form is to make or to shape something.",
     "They formed a new government.",
     "يشكّل / يكوّن",
     ["forms (v)", "formed (past)", "formation (n)"]),

    (8,  "Fragment",   "🧩", "noun",
     "A fragment is a small part of something.",
     "After the light broke, there were fragments of glass to clean up.",
     "شظية / جزء",
     ["fragments (pl)", "fragmented (adj)"]),

    (9,  "Galaxy",     "🌌", "noun",
     "A galaxy is an extremely large collection of star systems.",
     "Our solar system is located in the outer area of our galaxy.",
     "مجرّة",
     ["galaxies (pl)", "galactic (adj)"]),

    (10, "Gloom",      "🌫️", "noun",
     "Gloom is a state of almost complete darkness or sadness.",
     "In the gloom of the morning, it was difficult to see the boat on the lake.",
     "كآبة / ظلام",
     ["gloomy (adj)", "gloomily (adv)"]),

    (11, "Large",      "🐘", "adjective",
     "Something large is very big.",
     "I was frightened by a large bird.",
     "كبير",
     ["larger (comp)", "largely (adv)"]),

    (12, "Moon",       "🌙", "noun",
     "The moon is an object that travels around our Earth.",
     "The moon looks beautiful tonight.",
     "قمر",
     ["moons (pl)", "moonlight (n)"]),

    (13, "Radiate",    "☀️", "verb",
     "To radiate means to send out energy or heat.",
     "The heat from the fireplace radiated throughout the room.",
     "يشع",
     ["radiates (v)", "radiated (past)", "radiation (n)"]),

    (14, "Roam",       "🚶", "verb",
     "To roam means to move around without a plan or purpose.",
     "All day, the cows roamed around the field eating grass.",
     "يتجول / يتيه",
     ["roams (v)", "roamed (past)", "roaming (n)"]),

    (15, "Solitary",   "🪑", "adjective",
     "A solitary thing is lonely or the only one.",
     "The only thing in the room was a solitary chair.",
     "وحيد / منفرد",
     ["solitude (n)", "solitarily (adv)"]),

    (16, "Spectrum",   "🌈", "noun",
     "The spectrum is the full range of color ranging from red to violet.",
     "You can see the entire spectrum in a rainbow.",
     "طيف",
     ["spectrums (pl)", "spectral (adj)"]),

    (17, "Sphere",     "🌐", "noun",
     "A sphere is a three-dimensional round shape, like a ball.",
     "The balloons were inflated into a variety of colorful spheres.",
     "كرة",
     ["spheres (pl)", "spherical (adj)"]),

    (18, "Star",       "⭐", "noun",
     "A star is a bright shining thing in the night sky.",
     "The stars come out at night.",
     "نجم",
     ["stars (pl)", "starry (adj)"]),

    (19, "Status",     "🏷️", "noun",
     "Status is the position of something or someone in relation to others.",
     "She had achieved the status of being the smartest girl in the class.",
     "مكانة / وضع",
     ["statuses (pl)"]),

    (20, "Ugly",       "🦂", "adjective",
     "Something ugly is not good to look at.",
     "It was an ugly night.",
     "قبيح",
     ["uglier (comp)", "ugliness (n)"]),
]

STORY_TITLE = "How Comet Got His Tail"

STORY_HTML = """
<p>A <strong>solitary</strong> rock <strong>roamed</strong> through the cold <strong>gloom</strong> of space. It slowly moved through space with a feeling of sadness. In the large and <strong>beautiful galaxy</strong>, it was only a tiny rock. It felt like an as small as an <strong>atom</strong>.</p>

<p>On its journeys, it encountered many amazing objects. It flew by beautiful <strong>moons</strong> that were <strong>covered</strong> with dust.</p>

<p>"Why can't I be as beautiful as them?" it thought. The rock passed a large planet. The <strong>sphere</strong> was hundreds of times larger than the <strong>breadth</strong> of the small rock.</p>

<p>"Why can't I be as large as that?" it wondered.</p>

<p>The rock was filled with <strong>despair</strong>. It was surrounded by beauty and greatness, yet it was just a small and <strong>ugly fragment</strong> of rock.</p>

<p>One day, it approached the area of a bright <strong>star</strong>.</p>

<p>"What's wrong?" the star asked. "Oh, I wish I had a higher <strong>status</strong> in the galaxy. All the other objects are so beautiful and <strong>large</strong>," the rock replied. "But I'm just an ugly rock."</p>

<p>The star considered the problem. At last, it said, "You don't have to worry anymore. I think I can help." The star <strong>radiated</strong> its light brighter and hotter than it had ever done before. "Come a little closer," the star said to the rock.</p>

<p>The rock drifted closer to the star. Suddenly, the ice that was in the rock's tiny holes melted and became gas. Then, the gas came out behind the <strong>comet</strong> to <strong>form</strong> a brilliant tail. The tail shone with all the colors of the <strong>spectrum</strong>.</p>

<p>The little rock had become a beautiful comet. It looked so amazing. It realized that the star helped it change its appearance. "Thank you," the comet said and then flew away with its new beautiful tail following behind it like a giant cape.</p>
"""

STORY_QUESTIONS = [
    {
        "q": "How did the rock feel as it roamed through space at the beginning?",
        "opts": [
            "Excited and adventurous.",
            "Solitary and full of sadness.",
            "Proud of its size.",
            "Hungry and tired."
        ],
        "ans": 1
    },
    {
        "q": "Why was the rock filled with despair?",
        "opts": [
            "It was lost in the galaxy.",
            "It was being chased by another comet.",
            "It felt small and ugly compared to other beautiful objects.",
            "It was afraid of the star."
        ],
        "ans": 2
    },
    {
        "q": "What did the rock wish for when it met the star?",
        "opts": [
            "To travel faster.",
            "To go back home.",
            "To meet the moon.",
            "To have a higher status and be beautiful like other objects."
        ],
        "ans": 3
    },
    {
        "q": "What did the star do to help the rock?",
        "opts": [
            "Pushed it into a galaxy.",
            "Radiated bright hot light that melted the ice and formed a tail of gas.",
            "Gave it a new color.",
            "Made it larger."
        ],
        "ans": 1
    },
    {
        "q": "What did the rock become at the end of the story?",
        "opts": [
            "A planet.",
            "A new star.",
            "A beautiful comet with a brilliant tail.",
            "A piece of moon."
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
print(f"Unit 25 seeded: {len(WORDS)} words, story '{STORY_TITLE}', {len(STORY_QUESTIONS)} questions.")
