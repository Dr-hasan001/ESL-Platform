"""
seed_b1_reading_work.py — B1 Reading: "How's it going at work?"
Three people (Si-Woo, Talita, Jada) talk about their work situations.
Run: python tools/seed_b1_reading_work.py
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

b1_students = db.query(User).filter(
    User.role == "student", User.cefr_level == "B1", User.is_active == True
).all()

PASSAGE = """\
Si-Woo, South Korea
I LEFT UNIVERSITY two years ago with a degree in Media Studies and I applied for jobs in the film industry — hundreds of jobs! — but there's so much competition, I didn't get one! Not even an interview! Everyone asked for experience, but how can you get work experience if nobody offers you a job? In the end, I agreed to spend time at a public relations company without pay. At first, I only did boring jobs like making coffee, but I'm beginning to do more interesting things now. We're working with a film company to promote their new film. I'm helping to organize some events with the actors. It's good to get new skills, but I'm not even getting the minimum wage. I want to learn and earn — so I'm going to an interview for a properly paid job next week. Wish me luck!

Talita, Uruguay
BEFORE, I DIDN'T WORK MUCH. Because I had children, I had a part-time job for a while, but a couple of times my children were sick, so I took time off, and the second time my boss said don't come back. Later I also cared for my dad. I was happy to do it, but it's a full-time job without pay! Then a few years ago, the government started providing support for people like me. I got some training and now I work in a centre that teaches parents new skills and provides free day care for kids. I love my work and seeing the kids grow up. Obviously, they can be difficult sometimes, but if I'm having a bad day, I think of how I'm helping so many other parents and I'm grateful for my life now.

Jada, UK
I'M STUDYING PART-TIME here and working as a delivery driver at the same time. I can borrow money to pay for my course, but it's not enough. I started doing deliveries by bike through an app, but thankfully, I have a van now! I work for a company on a flexible contract. It means the hours change each week and sometimes you hardly earn anything because you don't get enough work — and then if you're late with a delivery, you can lose money too. It depends a lot on the manager. Luckily, I get on with mine, so it's OK for me. During the holidays, I have lots of hours, but then if I'm working on a project or an essay, I tell her I can't work and it's fine. So it suits me and I'm really enjoying getting to know Manchester.\
"""

# 20 questions — balanced distribution: A×5, B×5, C×5, D×5
QUESTIONS = [
    # Q1 correct=B(1)
    {
        "question_text": "What subject did Si-Woo study at university?",
        "options": [
            "Business Studies.",
            "Media Studies.",
            "Film Production.",
            "Communications.",
        ],
        "correct_index": 1,
    },
    # Q2 correct=C(2)
    {
        "question_text": "What industry did Si-Woo apply to after university?",
        "options": [
            "Marketing.",
            "Public Relations.",
            "The film industry.",
            "Television.",
        ],
        "correct_index": 2,
    },
    # Q3 correct=A(0)
    {
        "question_text": "Why did Si-Woo find it difficult to get a job?",
        "options": [
            "There was too much competition and nobody offered him work experience.",
            "He did not have the right degree.",
            "He only applied to a few companies.",
            "He failed all his interviews.",
        ],
        "correct_index": 0,
    },
    # Q4 correct=D(3)
    {
        "question_text": "What did Si-Woo do at first at the PR company?",
        "options": [
            "He helped to organize events.",
            "He worked with film actors.",
            "He promoted new films.",
            "He did boring jobs like making coffee.",
        ],
        "correct_index": 3,
    },
    # Q5 correct=B(1)
    {
        "question_text": "What is Si-Woo's PR company currently working on?",
        "options": [
            "A new TV show.",
            "Promoting a new film.",
            "A music event.",
            "A sports competition.",
        ],
        "correct_index": 1,
    },
    # Q6 correct=C(2)
    {
        "question_text": "What is Si-Woo helping to organize?",
        "options": [
            "A film festival.",
            "A marketing campaign.",
            "Events with the actors.",
            "A press conference.",
        ],
        "correct_index": 2,
    },
    # Q7 correct=A(0)
    {
        "question_text": "What is Si-Woo planning to do next week?",
        "options": [
            "Go to an interview for a properly paid job.",
            "Start a new unpaid work placement.",
            "Go back to university.",
            "Ask for a pay rise.",
        ],
        "correct_index": 0,
    },
    # Q8 correct=D(3)
    {
        "question_text": "Why did Talita lose her job the second time?",
        "options": [
            "She decided to stay at home with her children.",
            "The company closed down.",
            "She wanted to care for her father.",
            "Her children were sick and her boss told her not to come back.",
        ],
        "correct_index": 3,
    },
    # Q9 correct=B(1)
    {
        "question_text": "What did Talita do after losing her job?",
        "options": [
            "She started her own business.",
            "She cared for her father.",
            "She went back to school.",
            "She moved to a new city.",
        ],
        "correct_index": 1,
    },
    # Q10 correct=C(2)
    {
        "question_text": "What helped Talita return to work?",
        "options": [
            "A friend recommended her for a job.",
            "She found a job online.",
            "The government provided support and training.",
            "Her children grew up and she had more time.",
        ],
        "correct_index": 2,
    },
    # Q11 correct=A(0)
    {
        "question_text": "What does Talita do in her job now?",
        "options": [
            "She teaches parents new skills and looks after children.",
            "She works in a hospital.",
            "She works in a school.",
            "She provides care for elderly people.",
        ],
        "correct_index": 0,
    },
    # Q12 correct=D(3)
    {
        "question_text": "Where does Talita work?",
        "options": [
            "In a hospital.",
            "At a school.",
            "At a government office.",
            "In a centre that teaches parents and provides day care for kids.",
        ],
        "correct_index": 3,
    },
    # Q13 correct=B(1)
    {
        "question_text": "What does Talita love most about her job?",
        "options": [
            "The high salary.",
            "Seeing the kids grow up and helping other parents.",
            "The flexible working hours.",
            "Working with the government.",
        ],
        "correct_index": 1,
    },
    # Q14 correct=C(2)
    {
        "question_text": "What does Talita think about when she is having a bad day?",
        "options": [
            "Her salary and benefits.",
            "Her children and family.",
            "How she is helping so many other parents.",
            "Her father and the difficult times.",
        ],
        "correct_index": 2,
    },
    # Q15 correct=A(0)
    {
        "question_text": "What is Jada doing at the same time as working?",
        "options": [
            "Studying part-time.",
            "Looking after her children.",
            "Running her own business.",
            "Caring for a family member.",
        ],
        "correct_index": 0,
    },
    # Q16 correct=D(3)
    {
        "question_text": "How did Jada start making deliveries?",
        "options": [
            "In a car.",
            "In a van.",
            "By motorcycle.",
            "By bike.",
        ],
        "correct_index": 3,
    },
    # Q17 correct=B(1)
    {
        "question_text": "What does Jada use for deliveries now?",
        "options": [
            "A motorcycle.",
            "A van.",
            "A car.",
            "A bicycle.",
        ],
        "correct_index": 1,
    },
    # Q18 correct=C(2)
    {
        "question_text": "What does Jada's flexible contract mean?",
        "options": [
            "She can work from home.",
            "She gets extra pay at weekends.",
            "The hours change each week.",
            "She can choose her own manager.",
        ],
        "correct_index": 2,
    },
    # Q19 correct=A(0)
    {
        "question_text": "How can Jada lose money at work?",
        "options": [
            "If she is late with a delivery.",
            "If she takes a day off.",
            "If she works too many hours.",
            "If she argues with her manager.",
        ],
        "correct_index": 0,
    },
    # Q20 correct=D(3)
    {
        "question_text": "Which city is Jada getting to know?",
        "options": [
            "London.",
            "Birmingham.",
            "Leeds.",
            "Manchester.",
        ],
        "correct_index": 3,
    },
]

TITLE = "Reading - How's it going at work?"
if db.query(HomeworkAssignment).filter_by(title=TITLE).first():
    print(f"Already exists: '{TITLE}' — skipping.")
    db.close()
    sys.exit(0)

hw = HomeworkAssignment(
    teacher_id=teacher.id,
    type="reading",
    title=TITLE,
    instructions="Read what Si-Woo, Talita and Jada say about their work, then answer the comprehension questions.",
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

for student in b1_students:
    db.add(AssignmentStudent(assignment_id=hw.id, student_id=student.id))

db.commit()
print(f"Created: ID={hw.id}  \"{hw.title}\"")
print(f"Assigned to {len(b1_students)} B1 student(s): {[s.username for s in b1_students]}")
print(f"Questions: {len(QUESTIONS)}")
db.close()
