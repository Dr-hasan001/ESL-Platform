"""
seed_reading_hw.py — Insert the first Reading homework assignment.

Source: Outcomes Elementary A2, Unit 1 (Places) — Reading B
Run: python tools/seed_reading_hw.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.homework import (
    HomeworkAssignment, AssignmentStudent,
    HWReading, HomeworkQuestion,
)
from app.models.user import User

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ── Find teacher & students ───────────────────────────────────────────────────
teacher = db.query(User).filter(User.role == "teacher").first()
if not teacher:
    print("ERROR: No teacher account found. Run seed_db.py first.")
    db.close()
    sys.exit(1)

students = db.query(User).filter(User.role == "student", User.is_active == True).all()
a2_students = [s for s in students if s.cefr_level == "A2" or s.cefr_level is None]
if not a2_students:
    print("WARNING: No A2 students found. Assigning to all students.")
    a2_students = students

# ── Reading passage (Outcomes Elementary A2, Unit 1) ─────────────────────────
PASSAGE = """\
Hi, everyone! I'm Jeff, your teacher. Welcome to the course. Can you all say something about where you live?

I live in a little place called New Romney on the south coast. I'm from London, but I moved here because my wife is from here and it's cheaper to live. The town has one main road with some small shops and restaurants. There's a big supermarket where people from other villages come to do shopping. But for me, there aren't enough things to do here. There's a beach, but I don't like swimming in the sea - it's too cold and a bit dirty.

Hi! I'm William. I'm a student in Cuiaba. I was born here. People from outside Brazil often don't know Cuiaba, but it's quite big. It's famous for its food and culture. Now, there are quite a lot of tall buildings and there's a big modern stadium, but I like the old parts of the city and all the parks and trees. Cuiaba is the capital of the Mato Grosso region, which has lots of beautiful rivers and forests. It's very hot here all year and it rains a lot from October to April.

Hi, I'm Rocio. I live in a little village in the north-east of Spain called Arnedillo. I went to university in Zaragoza but I prefer it here. There aren't any big shops or noisy bars. People from other parts of Spain and Europe visit here because there are beautiful mountains and quiet places to relax. Arnedillo is also famous for natural hot water and I sometimes go in the river in the winter when it's 0 degrees outside.

Hi. I'm Barbora. I'm from Prague, the beautiful capital of the Czech Republic. I live in the centre, not far from the famous Charles Bridge. People from all over the world come here. My parents are sometimes unhappy because they say there's rubbish from the tourists and it's noisy at night because places close late. But I don't agree with them - I don't think it's dirty and it's good to have lots of places to meet friends at night.\
"""

# ── Questions ─────────────────────────────────────────────────────────────────
QUESTIONS = [
    {
        "question_text": "Why did Jeff move from London to New Romney?",
        "options": [
            "He prefers the beach.",
            "His wife is from there and it is cheaper to live.",
            "He wanted a quieter life.",
            "He got a new job there.",
        ],
        "correct_index": 1,
    },
    {
        "question_text": "What does Jeff say about the sea in New Romney?",
        "options": [
            "It is warm and clean.",
            "It is perfect for swimming.",
            "It is too cold and a bit dirty.",
            "It is very popular with tourists.",
        ],
        "correct_index": 2,
    },
    {
        "question_text": "What is Cuiaba famous for?",
        "options": [
            "Its cold weather and mountains.",
            "Its food and culture.",
            "Its famous old bridge.",
            "Its universities.",
        ],
        "correct_index": 1,
    },
    {
        "question_text": "Which part of Cuiaba does William prefer?",
        "options": [
            "The modern stadium.",
            "The tall buildings.",
            "The old parts with parks and trees.",
            "The supermarkets.",
        ],
        "correct_index": 2,
    },
    {
        "question_text": "When does it rain a lot in Cuiaba?",
        "options": [
            "From January to June.",
            "From October to April.",
            "From May to September.",
            "All year round.",
        ],
        "correct_index": 1,
    },
    {
        "question_text": "Where did Rocio go to university?",
        "options": [
            "Arnedillo.",
            "Madrid.",
            "Zaragoza.",
            "Barcelona.",
        ],
        "correct_index": 2,
    },
    {
        "question_text": "What is Arnedillo famous for?",
        "options": [
            "Big shopping centres.",
            "Natural hot water.",
            "A famous stadium.",
            "Noisy bars.",
        ],
        "correct_index": 1,
    },
    {
        "question_text": "Where does Barbora live in Prague?",
        "options": [
            "In the suburbs, near a supermarket.",
            "In the north of the city.",
            "In the centre, near the Charles Bridge.",
            "Outside the city, in a village.",
        ],
        "correct_index": 2,
    },
    {
        "question_text": "Why are Barbora's parents sometimes unhappy?",
        "options": [
            "Because it is too cold at night.",
            "Because there is rubbish from tourists and it is noisy at night.",
            "Because there are not enough places to meet friends.",
            "Because the city is too expensive.",
        ],
        "correct_index": 1,
    },
    {
        "question_text": "What is Barbora's opinion about Prague?",
        "options": [
            "She thinks it is too dirty and noisy.",
            "She agrees with her parents that it needs to be cleaner.",
            "She thinks it is not dirty and likes having places to meet friends.",
            "She wants to move to a quieter city.",
        ],
        "correct_index": 2,
    },
    # ── Questions 11–20 ───────────────────────────────────────────────────────
    {
        "question_text": "Where is New Romney located?",
        "options": [
            "On the south coast of England.",
            "In the north of London.",
            "In the centre of England.",
            "Near the border with Scotland.",
        ],
        "correct_index": 0,
    },
    {
        "question_text": "What does Jeff say New Romney's main road has?",
        "options": [
            "A big market and a stadium.",
            "Many offices and banks.",
            "A famous old church.",
            "Some small shops and restaurants.",
        ],
        "correct_index": 3,
    },
    {
        "question_text": "Where is Jeff originally from?",
        "options": [
            "London.",
            "New Romney.",
            "Manchester.",
            "Brighton.",
        ],
        "correct_index": 0,
    },
    {
        "question_text": "What does William say is new in Cuiaba?",
        "options": [
            "A famous old bridge.",
            "A large airport and a new university.",
            "Many new parks and forests.",
            "Tall buildings and a big modern stadium.",
        ],
        "correct_index": 3,
    },
    {
        "question_text": "What is the Mato Grosso region known for?",
        "options": [
            "Beautiful rivers and forests.",
            "Its cold mountains and snow.",
            "Its famous food markets.",
            "Its old historic buildings.",
        ],
        "correct_index": 0,
    },
    {
        "question_text": "What is the weather like in Cuiaba all year?",
        "options": [
            "Cold and rainy.",
            "Mild and windy.",
            "Very cold in winter.",
            "Very hot.",
        ],
        "correct_index": 3,
    },
    {
        "question_text": "Where is Arnedillo located in Spain?",
        "options": [
            "In the north-east.",
            "In the south.",
            "In the centre.",
            "On the coast.",
        ],
        "correct_index": 0,
    },
    {
        "question_text": "What does Rocio sometimes do in winter in Arnedillo?",
        "options": [
            "She goes skiing in the mountains.",
            "She visits friends in Zaragoza.",
            "She stays at home and reads.",
            "She goes in the river when it is 0 degrees outside.",
        ],
        "correct_index": 3,
    },
    {
        "question_text": "Who visits Prague according to Barbora?",
        "options": [
            "People from all over the world.",
            "Mainly people from Europe.",
            "Mainly business travellers.",
            "Students from other Czech cities.",
        ],
        "correct_index": 0,
    },
    {
        "question_text": "What do Barbora's parents complain about?",
        "options": [
            "The city is too expensive to live in.",
            "There are not enough restaurants.",
            "The public transport is bad.",
            "There is rubbish from tourists and it is noisy at night.",
        ],
        "correct_index": 3,
    },
]

# ── Create assignment (skip if already exists) ────────────────────────────────
TITLE = "Unit 1 Reading - Where Do You Live?"
if db.query(HomeworkAssignment).filter_by(title=TITLE).first():
    print(f"Already exists: '{TITLE}' — skipping.")
    db.close()
    sys.exit(0)

hw = HomeworkAssignment(
    teacher_id=teacher.id,
    type="reading",
    title=TITLE,
    instructions="Read what four people say about where they live, then answer the comprehension questions.",
    is_active=True,
)
db.add(hw)
db.flush()

db.add(HWReading(assignment_id=hw.id, passage_text=PASSAGE))

for i, q in enumerate(QUESTIONS, start=1):
    db.add(HomeworkQuestion(
        assignment_id=hw.id,
        position=i,
        question_text=q["question_text"],
        question_type="multiple_choice",
        options=q["options"],
        correct_index=q["correct_index"],
    ))

for student in a2_students:
    db.add(AssignmentStudent(assignment_id=hw.id, student_id=student.id))

db.commit()
print(f"Reading homework created: ID={hw.id}  '{hw.title}'")
print(f"Assigned to {len(a2_students)} student(s): {[s.username for s in a2_students]}")
db.close()
