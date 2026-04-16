"""
seed_unit2_reading.py - Insert Unit 7 Reading homework (Free time).
Outcomes Elementary A2, Unit 7.
Run: python tools/seed_unit2_reading.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.homework import HomeworkAssignment, AssignmentStudent, HWReading, HomeworkQuestion
from app.models.user import User

Base.metadata.create_all(bind=engine)
db = SessionLocal()

teacher = db.query(User).filter(User.role == "teacher").first()
if not teacher:
    print("ERROR: No teacher found. Run seed_db.py first.")
    db.close()
    sys.exit(1)

a2_students = db.query(User).filter(
    User.role == "student", User.cefr_level == "A2", User.is_active == True
).all()

PASSAGE = (
    "Hi! My name is Clara. I am from Argentina. In my free time, I love dancing. "
    "I go to a dance class every Tuesday and Thursday evening. My favourite style is salsa. "
    "I also like watching films at the cinema with my friends at the weekend. "
    "I do not watch much TV at home because I prefer to go out and be active.\n\n"

    "Hello, I am Yusuf. I am from Turkey. I spend a lot of my free time playing football. "
    "I play with my friends in the park every Saturday morning. I also follow a football team online "
    "and I watch their matches on TV. When I am at home, I enjoy reading books, especially adventure stories. "
    "I read before I go to sleep every night.\n\n"

    "My name is Sophie. I am from France. My favourite hobby is cooking. "
    "I like trying new recipes from different countries. Last week I made Japanese food for the first time. "
    "At the weekend, I sometimes go cycling in the countryside with my brother. "
    "I think it is important to have an active hobby and a relaxing hobby.\n\n"

    "Hi! I am Liam. I am from Ireland. In my free time, I play video games online with my friends. "
    "We usually play together in the evening after work. I also like going to concerts. "
    "I see live music about once a month. My favourite type of music is rock. "
    "At the weekend, I sometimes go hiking in the mountains. I love being in nature."
)

QUESTIONS = [
    {
        "question_text": "How often does Clara go to her dance class?",
        "options": [
            "Once a week.",
            "Every day.",
            "Twice a week.",
            "Three times a week.",
        ],
        "correct_index": 2,
    },
    {
        "question_text": "What is Clara's favourite dance style?",
        "options": [
            "Tango.",
            "Salsa.",
            "Ballet.",
            "Hip hop.",
        ],
        "correct_index": 1,
    },
    {
        "question_text": "Why does Clara not watch much TV at home?",
        "options": [
            "She does not have a TV.",
            "She is too busy with work.",
            "She prefers to go out and be active.",
            "She does not like films.",
        ],
        "correct_index": 2,
    },
    {
        "question_text": "When does Yusuf play football?",
        "options": [
            "Every Friday evening.",
            "Every Sunday afternoon.",
            "Every Saturday morning.",
            "Every weekday morning.",
        ],
        "correct_index": 2,
    },
    {
        "question_text": "What kind of books does Yusuf like to read?",
        "options": [
            "Science books.",
            "Adventure stories.",
            "History books.",
            "Comic books.",
        ],
        "correct_index": 1,
    },
    {
        "question_text": "What did Sophie cook last week?",
        "options": [
            "French food.",
            "Turkish food.",
            "Italian food.",
            "Japanese food.",
        ],
        "correct_index": 3,
    },
    {
        "question_text": "Who does Sophie go cycling with?",
        "options": [
            "Her friends.",
            "Her brother.",
            "Her parents.",
            "Her colleagues.",
        ],
        "correct_index": 1,
    },
    {
        "question_text": "How often does Liam go to concerts?",
        "options": [
            "Every week.",
            "Every day.",
            "About once a month.",
            "Twice a year.",
        ],
        "correct_index": 2,
    },
    {
        "question_text": "What is Liam's favourite type of music?",
        "options": [
            "Jazz.",
            "Pop.",
            "Classical.",
            "Rock.",
        ],
        "correct_index": 3,
    },
    {
        "question_text": "What does Liam like to do at the weekend?",
        "options": [
            "Go cycling.",
            "Cook new recipes.",
            "Go hiking in the mountains.",
            "Go to the cinema.",
        ],
        "correct_index": 2,
    },
]

TITLE = "Unit 7 Reading - Free Time"
if db.query(HomeworkAssignment).filter_by(title=TITLE).first():
    print(f"Already exists: '{TITLE}' — skipping.")
    db.close()
    sys.exit(0)

hw = HomeworkAssignment(
    teacher_id=teacher.id,
    type="reading",
    title=TITLE,
    instructions="Read what four people say about their free time, then answer the comprehension questions.",
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
print(f"Created: ID={hw.id}  \"{hw.title}\"")
print(f"Assigned to: {[s.username for s in a2_students]}")
print(f"Questions: {len(QUESTIONS)}")
db.close()
