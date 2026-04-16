"""
seed_unit2_reading.py - Insert Unit 2 Reading homework (Family).
Outcomes Elementary A2, Unit 2.
Run: python tools/seed_unit2_reading.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.homework import HomeworkAssignment, AssignmentStudent, HWReading, HomeworkQuestion
from app.models.user import User
from collections import Counter

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
    "Hi! My name is Ana. I am from Mexico. I have a big family - I have three brothers and two sisters. "
    "My parents live in Mexico City with my two younger brothers. I am the oldest child, so I help my parents a lot. "
    "My grandmother also lives with us. She is 82 years old but she is very active. She cooks for the whole family "
    "every Sunday. I love big family dinners!\n\n"
    "My name is David. I am from Australia. I am an only child, which means I do not have any brothers or sisters. "
    "Some people think it is sad, but I do not agree. I have a lot of friends, and my parents give me a lot of "
    "attention. My parents are divorced, so I live with my mother during the week and with my father at the weekend. "
    "Both my parents work, so I help at home a lot.\n\n"
    "Hello! I am Fatima. I am from Morocco but I live in France now. I have one brother and one sister. "
    "My sister is married and has two children - a boy and a girl. I love being an aunt! My niece is only one year "
    "old and my nephew is three. My parents are still in Morocco, so I only see them two or three times a year. "
    "I talk to them on the phone every day.\n\n"
    "Hi, I am Pete. I am from the UK. I am married and I have two children - a son called Jack and a daughter "
    "called Emma. Jack is 15 and Emma is 12. They go to school near our house. My wife is called Helen and she is "
    "a nurse. I am a teacher. In the evening, the family usually eats dinner together and then the children do "
    "their homework. At the weekend, we often go to the park or watch films at home."
)

# 20 questions — answer distribution: A×5, B×5, C×5, D×5
# Correct index per question: 0,1,2,3, 1,2,3,0, 2,3,0,1, 3,0,1,2, 0,3,2,1
QUESTIONS = [
    # Q1 correct=A(0)
    {
        "question_text": "Who is Ana in her family?",
        "options": ["She is the oldest child.", "She is the youngest child.", "She is an only child.", "She is the second child."],
        "correct_index": 0,
    },
    # Q2 correct=B(1)
    {
        "question_text": "How many siblings does Ana have in total?",
        "options": ["Three.", "Five.", "Two.", "Four."],
        "correct_index": 1,
    },
    # Q3 correct=C(2)
    {
        "question_text": "How old is Ana's grandmother?",
        "options": ["72 years old.", "78 years old.", "82 years old.", "86 years old."],
        "correct_index": 2,
    },
    # Q4 correct=D(3)
    {
        "question_text": "What does Ana's grandmother do every Sunday?",
        "options": ["She goes to church.", "She visits friends.", "She goes shopping.", "She cooks for the whole family."],
        "correct_index": 3,
    },
    # Q5 correct=B(1)
    {
        "question_text": "Is David an only child?",
        "options": ["No, he has one brother.", "Yes, he has no brothers or sisters.", "No, he has one sister.", "No, he has two brothers."],
        "correct_index": 1,
    },
    # Q6 correct=C(2)
    {
        "question_text": "Where does David live during the week?",
        "options": ["With his father.", "With his grandparents.", "With his mother.", "At a school dormitory."],
        "correct_index": 2,
    },
    # Q7 correct=D(3)
    {
        "question_text": "What do both of David's parents do?",
        "options": ["They both cook at home.", "They both live together.", "They both travel for work.", "They both work."],
        "correct_index": 3,
    },
    # Q8 correct=A(0)
    {
        "question_text": "Where is Fatima originally from?",
        "options": ["Morocco.", "France.", "Spain.", "Algeria."],
        "correct_index": 0,
    },
    # Q9 correct=C(2)
    {
        "question_text": "How old is Fatima's niece?",
        "options": ["Three years old.", "Two years old.", "One year old.", "Four years old."],
        "correct_index": 2,
    },
    # Q10 correct=D(3)
    {
        "question_text": "How often does Fatima visit her parents in Morocco?",
        "options": ["Every week.", "Once a year.", "Every month.", "Two or three times a year."],
        "correct_index": 3,
    },
    # Q11 correct=A(0)
    {
        "question_text": "What is Pete's daughter called?",
        "options": ["Emma.", "Helen.", "Sarah.", "Lucy."],
        "correct_index": 0,
    },
    # Q12 correct=B(1)
    {
        "question_text": "How old is Pete's son Jack?",
        "options": ["12 years old.", "15 years old.", "14 years old.", "16 years old."],
        "correct_index": 1,
    },
    # Q13 correct=D(3)
    {
        "question_text": "What is Pete's wife's job?",
        "options": ["She is a teacher.", "She is a doctor.", "She is a chef.", "She is a nurse."],
        "correct_index": 3,
    },
    # Q14 correct=A(0)
    {
        "question_text": "What does Pete's family usually do in the evening?",
        "options": ["They eat dinner together and the children do homework.", "They watch films.", "They go to the park.", "They play games."],
        "correct_index": 0,
    },
    # Q15 correct=B(1)
    {
        "question_text": "What does Pete's family often do at the weekend?",
        "options": ["They visit grandparents.", "They go to the park or watch films at home.", "They go shopping.", "They play sports."],
        "correct_index": 1,
    },
    # Q16 correct=C(2)
    {
        "question_text": "Where does Fatima live now?",
        "options": ["Morocco.", "Spain.", "France.", "Belgium."],
        "correct_index": 2,
    },
    # Q17 correct=A(0)
    {
        "question_text": "What is Ana's nationality?",
        "options": ["Mexican.", "Spanish.", "Brazilian.", "Argentinian."],
        "correct_index": 0,
    },
    # Q18 correct=D(3)
    {
        "question_text": "How many children does Fatima's sister have?",
        "options": ["None.", "Three.", "One.", "Two."],
        "correct_index": 3,
    },
    # Q19 correct=C(2)
    {
        "question_text": "What does David think about being an only child?",
        "options": ["He thinks it is very sad.", "He finds it very difficult.", "He does not think it is sad.", "He wishes he had a brother."],
        "correct_index": 2,
    },
    # Q20 correct=B(1)
    {
        "question_text": "How does Fatima contact her parents every day?",
        "options": ["She sends emails.", "She calls them on the phone.", "She visits them.", "She sends letters."],
        "correct_index": 1,
    },
]

# Verify distribution
dist = Counter(q["correct_index"] for q in QUESTIONS)
print("Answer distribution:", {chr(65 + k): v for k, v in sorted(dist.items())})

TITLE = "Unit 2 Reading - My Family"
if db.query(HomeworkAssignment).filter_by(title=TITLE).first():
    print(f"Already exists: '{TITLE}' — skipping.")
    db.close()
    sys.exit(0)

hw = HomeworkAssignment(
    teacher_id=teacher.id,
    type="reading",
    title=TITLE,
    instructions="Read what four people say about their families, then answer the comprehension questions.",
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
