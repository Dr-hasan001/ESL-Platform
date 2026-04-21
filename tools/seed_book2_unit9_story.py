"""
seed_book2_unit9_story.py
Inserts the Unit 9 story "Starfish" for Book 2 (A2).
Uses all 20 Unit 9 vocabulary words (highlighted with <span class="vocab">).
10 comprehension questions — answer distribution A×3, B×3, C×2, D×2.

Run: python tools/seed_book2_unit9_story.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.book import Book, Unit, UnitStory

Base.metadata.create_all(bind=engine)
db = SessionLocal()

book = db.query(Book).filter(Book.book_number == 2).first()
unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == 9).first()
if not unit:
    print("ERROR: Unit 9 not found.")
    db.close()
    sys.exit(1)

# ── Story HTML ────────────────────────────────────────────────────────────────
# Vocabulary words are highlighted with <span class="vocab">word</span>

STORY_HTML = """
<p>
  One morning, Omar walked along the beach. He had a clear
  <span class="vocab">plan</span> in his mind and a big
  <span class="vocab">goal</span>: to win first prize at the school science competition.
  The <span class="vocab">deadline</span> was Friday — just three days away.
  He <span class="vocab">intended</span> to collect interesting shells and
  <span class="vocab">prepare</span> a display about ocean life.
</p>

<p>
  As he walked, Omar saw something strange. Hundreds of starfish lay on the sand,
  washed up by the waves overnight. He knew that if they stayed in the morning sun,
  they would die. He picked one up and threw it back into the sea. Then another. And another.
</p>

<p>
  An old man passed by and watched. "Why are you doing this?" he asked.
  "There are thousands of them. You cannot
  <span class="vocab">expect</span> to save them all."
</p>

<p>
  Omar picked up another starfish and threw it carefully into the water.
  "I <span class="vocab">wish</span> I could save them all," he said quietly.
  "But I <span class="vocab">promise</span> I will keep trying for as long as I can."
</p>

<p>
  The old man stopped. He thought about it. Then he nodded and bent down beside Omar.
  He had no <span class="vocab">appointment</span>, no fixed
  <span class="vocab">schedule</span>, and had not
  <span class="vocab">reserved</span> time for anything special that morning.
  But something had changed in him. He picked up a starfish and threw it into the sea.
</p>

<p>
  Omar's friend Layla saw them from the road and sent a message:
  "I'll <span class="vocab">remind</span> everyone at school to come and help.
  I'll <span class="vocab">invite</span> the whole class!"
  Omar replied quickly to <span class="vocab">update</span> her:
  "Come now — the tide is turning. Please
  <span class="vocab">confirm</span> how many people are coming so we can
  <span class="vocab">book</span> enough time before the beach closes."
</p>

<p>
  One by one, students arrived. Nobody
  <span class="vocab">cancelled</span> their morning to
  <span class="vocab">worry</span> about small things.
  They all worked together, side by side, with the same shared goal.
</p>

<p>
  By midday, the beach was clear and the sea sparkled in the sun.
  Omar looked out at the water and thought about the
  <span class="vocab">future</span>. He <span class="vocab">hoped</span>
  that the starfish would be safe. He also had a new idea — not about shells,
  but about teamwork. That, he decided, would be his science project.
</p>
"""

# ── 10 comprehension questions ────────────────────────────────────────────────
# Distribution: A×3, B×3, C×2, D×2
# q = question text | opts = 4 options | ans = correct index (0=A,1=B,2=C,3=D)

QUESTIONS = [
    # Q1 — correct A(0)
    {
        "q": "What is Omar's goal at the start of the story?",
        "opts": [
            "To win first prize at the school science competition.",
            "To collect as many starfish as possible.",
            "To take photos of the beach.",
            "To meet his friend Layla.",
        ],
        "ans": 0,
    },
    # Q2 — correct B(1)
    {
        "q": "When is the deadline for the competition?",
        "opts": [
            "The next morning.",
            "Friday — three days away.",
            "The following week.",
            "Saturday afternoon.",
        ],
        "ans": 1,
    },
    # Q3 — correct A(0)
    {
        "q": "Why does Omar start throwing starfish into the sea?",
        "opts": [
            "Because he knows they will die if they stay in the sun.",
            "Because the old man tells him to.",
            "Because it is part of his science project.",
            "Because Layla asks him to.",
        ],
        "ans": 0,
    },
    # Q4 — correct C(2)
    {
        "q": "What does the old man say Omar cannot expect to do?",
        "opts": [
            "Finish the project by Friday.",
            "Win the science competition.",
            "Save all the starfish.",
            "Find his friends on the beach.",
        ],
        "ans": 2,
    },
    # Q5 — correct B(1)
    {
        "q": "What does Omar promise?",
        "opts": [
            "That he will cancel the competition.",
            "That he will keep trying for as long as he can.",
            "That he will call Layla immediately.",
            "That he will build a shelter for the starfish.",
        ],
        "ans": 1,
    },
    # Q6 — correct D(3)
    {
        "q": "What does the old man do after he stops and thinks?",
        "opts": [
            "He goes home to prepare breakfast.",
            "He calls the school to report the problem.",
            "He takes a photo of the starfish.",
            "He picks up a starfish and throws it into the sea.",
        ],
        "ans": 3,
    },
    # Q7 — correct B(1)
    {
        "q": "What does Layla offer to do?",
        "opts": [
            "Reserve a table at a nearby café for the group.",
            "Remind everyone at school and invite the whole class.",
            "Book a bus to take everyone to the beach.",
            "Confirm the competition rules with the teacher.",
        ],
        "ans": 1,
    },
    # Q8 — correct A(0)
    {
        "q": "What does Omar ask Layla to confirm?",
        "opts": [
            "How many people are coming.",
            "What time the competition starts.",
            "Whether the old man will stay.",
            "Where they should meet.",
        ],
        "ans": 0,
    },
    # Q9 — correct C(2)
    {
        "q": "What is Omar's new idea for his science project?",
        "opts": [
            "A display about shells he collected.",
            "A poster about starfish biology.",
            "A story about teamwork.",
            "A video of the beach clean-up.",
        ],
        "ans": 2,
    },
    # Q10 — correct D(3)
    {
        "q": "Which word best describes how Omar and the students acted together?",
        "opts": [
            "Worried.",
            "Careless.",
            "Competitive.",
            "Cooperative.",
        ],
        "ans": 3,
    },
]

# ── Insert / update ───────────────────────────────────────────────────────────
existing = db.query(UnitStory).filter(UnitStory.unit_id == unit.id).first()
if existing:
    existing.story_title = "Starfish"
    existing.story_html = STORY_HTML
    existing.story_questions = QUESTIONS
    print("Updated existing story for Unit 9.")
else:
    db.add(UnitStory(
        unit_id=unit.id,
        story_title="Starfish",
        story_html=STORY_HTML,
        story_questions=QUESTIONS,
    ))
    print("Created new story for Unit 9.")

db.commit()
print(f"Unit 9 story 'Starfish': {len(QUESTIONS)} questions saved.")
db.close()
