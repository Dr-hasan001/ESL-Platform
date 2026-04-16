"""
update_unit2_reading.py
Replaces Unit 2 Reading (ID=2) with the real Outcomes Elementary A2
passage and 20 questions. Answer distribution: A x5, B x5, C x5, D x5.
Run: python tools/update_unit2_reading.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.homework import HomeworkAssignment, HWReading, HomeworkQuestion
from collections import Counter

Base.metadata.create_all(bind=engine)
db = SessionLocal()

hw = db.query(HomeworkAssignment).filter(HomeworkAssignment.id == 2).first()
if not hw:
    print("ERROR: Assignment ID=2 not found.")
    db.close()
    sys.exit(1)

# ── Update title & instructions ───────────────────────────────────────────────
hw.title = "Unit 2 Reading - Tell Us About Your Free Time"
hw.instructions = (
    "Read what four people say about their free time, "
    "then answer the comprehension questions."
)

# ── Replace passage ───────────────────────────────────────────────────────────
PASSAGE = (
    "Many of us spend most of our time working or studying. "
    "There's sleeping, eating and sitting on buses or trains! "
    "So how much free time do our readers around the world have? "
    "And what do they do in it? Here's what they told us:\n\n"

    "ERASMO, MEXICO\n"
    "I do something most nights. On Mondays and Wednesdays, I go to my English "
    "class, and on Tuesdays, I usually go to the cinema with friends, because the "
    "tickets are cheap then. On Thursdays, I always go to the gym. I usually go "
    "out dancing on Saturday nights. I often get home at four or five in the "
    "morning, so on Sundays I sleep! I sometimes get up at three in the afternoon.\n\n"

    "LENA, SWITZERLAND\n"
    "Free time? I don't have any free time because I have my own business. "
    "I sometimes go to rock concerts, but not very often - maybe once or twice a "
    "year - and I sometimes go shopping at the weekend. I like buying nice things "
    "with the money I make. I have an expensive new car and a very big TV. "
    "I like watching sport.\n\n"

    "IBRAHIM, EGYPT\n"
    "I'm a student and I'm lucky because I have a lot of free time. I try to do "
    "some exercise most days. I often go running in the morning and on Tuesdays "
    "and Thursdays I play basketball in the park. I usually prepare dinner for my "
    "family. I like cooking and everyone says I'm good at it. My friends often "
    "play video games, but I don't like them. In the evening, I usually tidy my "
    "room, answer emails and then read.\n\n"

    "MALEE, THAILAND\n"
    "I don't go out much during the week. I usually study for two hours in the "
    "evening. I never watch TV, really. I usually play the piano every day. "
    "It helps me relax. Then I go to bed at nine or ten and listen to music. "
    "At the weekend, I go out with my family to a park or to the countryside, "
    "and we go for a walk. I sometimes go to a shopping centre with friends, "
    "but I don't usually buy much!"
)

reading = db.query(HWReading).filter(HWReading.assignment_id == 2).first()
reading.passage_text = PASSAGE

# ── Replace all questions ─────────────────────────────────────────────────────
db.query(HomeworkQuestion).filter(HomeworkQuestion.assignment_id == 2).delete()
db.flush()

# Correct index plan: A x5, B x5, C x5, D x5
# A(0): Q1,Q8,Q11,Q14,Q17   B(1): Q2,Q5,Q12,Q15,Q20
# C(2): Q3,Q6,Q9,Q16,Q19    D(3): Q4,Q7,Q10,Q13,Q18
QUESTIONS = [
    # Q1 correct=A(0)
    {
        "question_text": "What does Erasmo do on Mondays and Wednesdays?",
        "options": [
            "He goes to English class.",
            "He goes to the gym.",
            "He goes out dancing.",
            "He goes to the cinema.",
        ],
        "correct_index": 0,
    },
    # Q2 correct=B(1)
    {
        "question_text": "Why does Erasmo go to the cinema on Tuesdays?",
        "options": [
            "He loves films.",
            "The tickets are cheap.",
            "His friends invite him.",
            "The cinema is near his home.",
        ],
        "correct_index": 1,
    },
    # Q3 correct=C(2)
    {
        "question_text": "What does Erasmo do on Thursdays?",
        "options": [
            "He goes out dancing.",
            "He goes to the cinema.",
            "He goes to the gym.",
            "He goes to English class.",
        ],
        "correct_index": 2,
    },
    # Q4 correct=D(3)
    {
        "question_text": "What does Erasmo usually do on Saturday nights?",
        "options": [
            "He goes to the cinema.",
            "He goes to the gym.",
            "He stays home and sleeps.",
            "He goes out dancing.",
        ],
        "correct_index": 3,
    },
    # Q5 correct=B(1)
    {
        "question_text": "What time does Erasmo sometimes get up on Sundays?",
        "options": [
            "At twelve in the afternoon.",
            "At three in the afternoon.",
            "At ten in the morning.",
            "At nine in the morning.",
        ],
        "correct_index": 1,
    },
    # Q6 correct=C(2)
    {
        "question_text": "Why doesn't Lena have much free time?",
        "options": [
            "She works long hours at a hospital.",
            "She looks after her children.",
            "She has her own business.",
            "She studies at university.",
        ],
        "correct_index": 2,
    },
    # Q7 correct=D(3)
    {
        "question_text": "How often does Lena go to rock concerts?",
        "options": [
            "Every week.",
            "Every month.",
            "Three or four times a year.",
            "Once or twice a year.",
        ],
        "correct_index": 3,
    },
    # Q8 correct=A(0)
    {
        "question_text": "What does Lena like doing with the money she makes?",
        "options": [
            "Buying nice things.",
            "Saving for holidays.",
            "Giving to charity.",
            "Investing in her business.",
        ],
        "correct_index": 0,
    },
    # Q9 correct=C(2)
    {
        "question_text": "What does Ibrahim often do in the morning?",
        "options": [
            "He plays basketball.",
            "He cooks breakfast.",
            "He goes running.",
            "He does homework.",
        ],
        "correct_index": 2,
    },
    # Q10 correct=D(3)
    {
        "question_text": "On which days does Ibrahim play basketball in the park?",
        "options": [
            "Mondays and Fridays.",
            "Mondays and Wednesdays.",
            "Wednesdays and Fridays.",
            "Tuesdays and Thursdays.",
        ],
        "correct_index": 3,
    },
    # Q11 correct=A(0)
    {
        "question_text": "What does Ibrahim usually do for his family?",
        "options": [
            "He prepares dinner.",
            "He cleans the house.",
            "He goes shopping.",
            "He does the laundry.",
        ],
        "correct_index": 0,
    },
    # Q12 correct=B(1)
    {
        "question_text": "What do Ibrahim's friends often do that he doesn't enjoy?",
        "options": [
            "Go running.",
            "Play video games.",
            "Watch TV.",
            "Go to the cinema.",
        ],
        "correct_index": 1,
    },
    # Q13 correct=D(3)
    {
        "question_text": "What is the last thing Ibrahim does before sleeping?",
        "options": [
            "He answers emails.",
            "He watches TV.",
            "He tidies his room.",
            "He reads.",
        ],
        "correct_index": 3,
    },
    # Q14 correct=A(0)
    {
        "question_text": "How long does Malee study each evening?",
        "options": [
            "For two hours.",
            "For one hour.",
            "For three hours.",
            "For thirty minutes.",
        ],
        "correct_index": 0,
    },
    # Q15 correct=B(1)
    {
        "question_text": "What does Malee say she never does in the evening?",
        "options": [
            "Play the piano.",
            "Watch TV.",
            "Study.",
            "Listen to music.",
        ],
        "correct_index": 1,
    },
    # Q16 correct=C(2)
    {
        "question_text": "Why does Malee play the piano every day?",
        "options": [
            "She wants to become a professional musician.",
            "Her parents ask her to practise.",
            "It helps her relax.",
            "She has a piano exam coming up.",
        ],
        "correct_index": 2,
    },
    # Q17 correct=A(0)
    {
        "question_text": "What time does Malee usually go to bed?",
        "options": [
            "At nine or ten.",
            "At eleven or twelve.",
            "At seven or eight.",
            "At midnight.",
        ],
        "correct_index": 0,
    },
    # Q18 correct=D(3)
    {
        "question_text": "Where does Malee go with her family at the weekend?",
        "options": [
            "To a restaurant.",
            "To the cinema.",
            "To a shopping centre.",
            "To a park or the countryside.",
        ],
        "correct_index": 3,
    },
    # Q19 correct=C(2)
    {
        "question_text": "Where does Malee sometimes go with her friends?",
        "options": [
            "To a park.",
            "To the cinema.",
            "To a shopping centre.",
            "To the countryside.",
        ],
        "correct_index": 2,
    },
    # Q20 correct=B(1)
    {
        "question_text": "What does Malee say about shopping with friends?",
        "options": [
            "She often spends a lot of money.",
            "She doesn't usually buy much.",
            "She enjoys buying clothes.",
            "She goes every weekend.",
        ],
        "correct_index": 1,
    },
]

dist = Counter(q["correct_index"] for q in QUESTIONS)
print("Answer distribution:", {chr(65 + k): v for k, v in sorted(dist.items())})

for i, q in enumerate(QUESTIONS, start=1):
    db.add(HomeworkQuestion(
        assignment_id=2,
        position=i,
        question_text=q["question_text"],
        question_type="multiple_choice",
        options=q["options"],
        correct_index=q["correct_index"],
    ))

db.commit()
total = db.query(HomeworkQuestion).filter(HomeworkQuestion.assignment_id == 2).count()
print(f'Updated: ID=2  "{hw.title}"')
print(f"Questions: {total}")
db.close()
