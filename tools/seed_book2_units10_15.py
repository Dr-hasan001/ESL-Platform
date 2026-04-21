"""
seed_book2_units10_15.py
Seeds Book 2 (A2) Units 10-15 with vocabulary, stories, and comprehension questions.
Run: python tools/seed_book2_units10_15.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.book import Book, Unit, Word, UnitStory

Base.metadata.create_all(bind=engine)
db = SessionLocal()

book = db.query(Book).filter(Book.book_number == 2).first()

def seed_unit(unit_number, words_data, story_title, story_html, questions):
    unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == unit_number).first()
    if not unit:
        print(f"ERROR: Unit {unit_number} not found.")
        return
    db.query(Word).filter(Word.unit_id == unit.id).delete()
    for pos, word, emoji, pos_tag, definition, example, arabic, derivatives in words_data:
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
    unit.word_count = len(words_data)
    existing = db.query(UnitStory).filter(UnitStory.unit_id == unit.id).first()
    if existing:
        existing.story_title = story_title
        existing.story_html = story_html
        existing.story_questions = questions
    else:
        db.add(UnitStory(unit_id=unit.id, story_title=story_title,
                         story_html=story_html, story_questions=questions))
    print(f"Unit {unit_number}: {len(words_data)} words, story '{story_title}', {len(questions)} questions.")

# ── UNIT 10 ───────────────────────────────────────────────────────────────────

WORDS_10 = [
    (1,  "Citizen",      "👤", "noun",
     "A citizen is someone who lives in a certain place.",
     "Carlos was born in Spain. He is a Spanish citizen.",
     "مواطن", ["citizens (pl)", "citizenship (n)"]),
    (2,  "Council",      "🏛️", "noun",
     "A council is a group of people who run a city or town.",
     "The council met to discuss the new laws for the city.",
     "مجلس", ["councils (pl)"]),
    (3,  "Declare",      "📢", "verb",
     "To declare is to say something officially.",
     "I declared my love for him.",
     "يُعلن", ["declares", "declared", "declaration (n)"]),
    (4,  "Enormous",     "🐘", "adjective",
     "Enormous people or things are very large.",
     "My dog looks enormous next to yours.",
     "ضخم / هائل", ["enormously (adv)"]),
    (5,  "Extraordinary","⭐", "adjective",
     "Extraordinary things are amazing.",
     "The fireman who rescued the girl was extraordinary.",
     "استثنائي / غير عادي", ["extraordinarily (adv)"]),
    (6,  "Fog",          "🌫️", "noun",
     "Fog is a thick cloud that is near the ground or water.",
     "I did not want to drive in the thick fog.",
     "ضباب", ["fogs (pl)", "foggy (adj)"]),
    (7,  "Funeral",      "⚫", "noun",
     "A funeral is a ceremony that takes place after a person dies.",
     "They had a funeral for the soldier who died during the war.",
     "جنازة", ["funerals (pl)"]),
    (8,  "Giant",        "🏔️", "adjective",
     "Giant means very big.",
     "The giant truck got in my way.",
     "عملاق / ضخم", ["giants (pl)", "gigantic (adj)"]),
    (9,  "Impression",   "🧠", "noun",
     "An impression is one way of thinking about someone or something.",
     "Most people's first impression of Dr. Giam is that he is mean.",
     "انطباع", ["impressions (pl)", "impress (v)", "impressive (adj)"]),
    (10, "Intention",    "🎯", "noun",
     "An intention is what a person plans to do.",
     "Do you have good intentions?",
     "نية / قصد", ["intentions (pl)", "intend (v)", "intentional (adj)"]),
    (11, "Mad",          "😡", "adjective",
     "A mad person or animal is angry.",
     "Mother got mad when I didn't listen to her.",
     "غاضب / مجنون", ["madly (adv)", "madness (n)"]),
    (12, "Ought",        "✅", "modal verb",
     "If you ought to do an action, it is the right thing to do.",
     "I ought to take my library books back.",
     "يجب / ينبغي", []),
    (13, "Resist",       "💪", "verb",
     "To resist something is to fight against it.",
     "He resisted the treatment at the hospital.",
     "يقاوم", ["resists", "resisted", "resistance (n)", "resistant (adj)"]),
    (14, "Reveal",       "🔦", "verb",
     "To reveal is to show something.",
     "I will reveal where I hid the candy bar.",
     "يكشف", ["reveals", "revealed", "revelation (n)"]),
    (15, "Rid",          "🚫", "verb",
     "To get rid of something means to free something or someone from it.",
     "I will rid our home of mice by using traps.",
     "يتخلص", ["rids", "rid (past)"]),
    (16, "Sword",        "⚔️", "noun",
     "A sword is a long sharp weapon.",
     "They used swords in battles in ancient times.",
     "سيف", ["swords (pl)"]),
    (17, "Tale",         "📖", "noun",
     "A tale is a story.",
     "She told her two friends about the wild tale of her day.",
     "حكاية / قصة", ["tales (pl)"]),
    (18, "Trap",         "🪤", "verb",
     "To trap people or animals is to catch them so they cannot get away.",
     "We trapped butterflies in a net.",
     "يوقع / يصطاد", ["traps", "trapped", "trap (n)"]),
    (19, "Trial",        "⚖️", "noun",
     "A trial is the way a court discovers if a person is guilty or innocent.",
     "He went on trial for robbing the bank.",
     "محاكمة", ["trials (pl)"]),
    (20, "Violent",      "⚡", "adjective",
     "A violent person or animal uses force to hurt others.",
     "The man was put into jail because he was violent.",
     "عنيف", ["violently (adv)", "violence (n)"]),
]

STORY_10 = """
<p>
  A long time ago, Blackbeard was one of the most <span class="vocab">violent</span>
  pirates ever. He was also an <span class="vocab">enormous</span> man.
</p>
<p>
  One day, there was a thick <span class="vocab">fog</span> over the water. Blackbeard
  did an <span class="vocab">extraordinary</span> thing. With his <span class="vocab">sword</span>
  in his belt, he attacked several <span class="vocab">giant</span> ships near a town and
  took some of the town's <span class="vocab">citizens</span>. Then, he
  <span class="vocab">revealed</span> his <span class="vocab">intentions</span>. He
  <span class="vocab">declared</span>, "You will give me medicine!" The people had a bad
  <span class="vocab">impression</span> of him. They were <span class="vocab">mad</span>,
  and they <span class="vocab">resisted</span>. But they were <span class="vocab">trapped</span>.
  They wanted to get <span class="vocab">rid</span> of him. So the town's
  <span class="vocab">council</span> decided to give him the medicine.
</p>
<p>
  After this, there was a reward for catching Blackbeard. If Blackbeard was caught, he
  would have a <span class="vocab">trial</span>. He didn't want to go to jail, so he quit
  being a pirate. Blackbeard became a fisherman. But he <span class="vocab">ought</span>
  to have stayed on land. The Royal Navy was still looking for him. They attacked him while
  he was fishing on his boat. Blackbeard fought as hard as he could, but finally, he was
  killed. He didn't even get a <span class="vocab">funeral</span>. But people still tell
  <span class="vocab">tales</span> about him many years later.
</p>
"""

QUESTIONS_10 = [
    {"q": "What is this tale about?",
     "opts": ["How many pirates become fishermen",
              "An enormous, violent pirate",
              "A boy resisting having to take medicine",
              "A ship that ought to have stayed at sea"],
     "ans": 1},
    {"q": "What can be assumed from the passage?",
     "opts": ["The town did not give Blackbeard the medicine.",
              "Blackbeard was an extraordinary fighter.",
              "Blackbeard was a kind and gentle man.",
              "The citizens were mad when Blackbeard was killed."],
     "ans": 1},
    {"q": "Which of the following is true about Blackbeard?",
     "opts": ["He kept his sword in his belt.",
              "He lit his cigarettes using a lamp.",
              "He wanted to get rid of his giant ship.",
              "He had a trial in the town."],
     "ans": 0},
    {"q": "Why were the people in town trapped?",
     "opts": ["Blackbeard was waiting for a reward.",
              "The fog was too thick for ships to sail in.",
              "Blackbeard wouldn't let ships in or out.",
              "Blackbeard declared that there was a strong storm coming."],
     "ans": 1},
    {"q": "What did Blackbeard demand from the town?",
     "opts": ["Gold coins", "Medicine", "Food and water", "New weapons"],
     "ans": 1},
    {"q": "What did Blackbeard do after the reward was posted?",
     "opts": ["He attacked more ships",
              "He hid in the fog",
              "He became a fisherman",
              "He went to trial"],
     "ans": 2},
    {"q": "How was Blackbeard eventually killed?",
     "opts": ["The town's council caught him",
              "He drowned at sea",
              "He was attacked while fishing on his boat",
              "He was caught during a trial"],
     "ans": 2},
    {"q": "What impression did the people have of Blackbeard?",
     "opts": ["They admired his courage",
              "They thought he was a great leader",
              "They had a bad impression of him",
              "They wanted him to stay"],
     "ans": 2},
    {"q": "What does the story say about Blackbeard's funeral?",
     "opts": ["It was held by the Royal Navy",
              "The town's citizens attended",
              "It was a giant ceremony",
              "He did not get a funeral"],
     "ans": 3},
    {"q": "Why are tales about Blackbeard still told today?",
     "opts": ["Because he was a kind and generous man",
              "Because he became a famous fisherman",
              "Because his story is remembered even after his death",
              "Because he revealed the council's secrets"],
     "ans": 2},
]

seed_unit(10, WORDS_10, "Blackbeard", STORY_10, QUESTIONS_10)

# ── UNIT 11 ───────────────────────────────────────────────────────────────────

WORDS_11 = [
    (1,  "Admission",   "🎟️", "noun",
     "Admission is the act of allowing someone to enter a place.",
     "Admission to the movie was $5.",
     "دخول / قبول", ["admissions (pl)", "admit (v)"]),
    (2,  "Astronomy",   "🔭", "noun",
     "Astronomy is the study of the stars and planets.",
     "Harold loved looking at the stars, so he decided to study astronomy.",
     "علم الفلك", ["astronomer (n)", "astronomical (adj)"]),
    (3,  "Blame",       "👉", "verb",
     "To blame someone for something bad is to say they did it.",
     "My mom blamed me for something I didn't do.",
     "يلوم", ["blames", "blamed", "blame (n)"]),
    (4,  "Chemistry",   "🧪", "noun",
     "Chemistry is the study of substances and reactions between them.",
     "In chemistry class, the professor taught us about chemical reactions.",
     "علم الكيمياء", ["chemical (adj/n)", "chemist (n)"]),
    (5,  "Despite",     "↔️", "preposition",
     "Despite shows a difference from what is expected.",
     "We still played the game despite the cold weather.",
     "رغم / على الرغم من", []),
    (6,  "Dinosaur",    "🦕", "noun",
     "A dinosaur is a big animal that lived millions of years ago.",
     "I like to see the dinosaur bones at the museum.",
     "ديناصور", ["dinosaurs (pl)"]),
    (7,  "Exhibit",     "🖼️", "verb",
     "To exhibit is to show something so that people can go look at it.",
     "My painting will be exhibited at the fair.",
     "يعرض", ["exhibits", "exhibited", "exhibition (n)"]),
    (8,  "Fame",        "🌟", "noun",
     "Fame is a reputation one has gained among the public.",
     "He had fame and fortune, but he was not happy.",
     "شهرة", ["famous (adj)", "famously (adv)"]),
    (9,  "Forecast",    "🌦️", "noun",
     "A forecast is an idea about what the weather will be like in the future.",
     "The forecast says that it will rain all week.",
     "توقعات / نشرة الطقس", ["forecasts (pl)", "forecast (v)", "forecaster (n)"]),
    (10, "Genius",      "💡", "noun",
     "A genius is a very smart person.",
     "Since she was a genius, she easily passed all of her school exams.",
     "عبقري", ["geniuses (pl)", "ingenious (adj)"]),
    (11, "Gentle",      "🕊️", "adjective",
     "A person who is gentle is kind and calm.",
     "He is very gentle with the baby.",
     "لطيف / هادئ", ["gently (adv)", "gentleness (n)"]),
    (12, "Geography",   "🌍", "noun",
     "Geography is the study of the Earth, its land, weather, etc.",
     "I had to draw a map for geography class.",
     "الجغرافيا", ["geographical (adj)", "geographer (n)"]),
    (13, "Interfere",   "🛑", "verb",
     "To interfere is to cause problems and keep something from happening.",
     "My little sister always interferes when I'm trying to study.",
     "يتدخل", ["interferes", "interfered", "interference (n)"]),
    (14, "Lightly",     "🪶", "adverb",
     "To do something lightly is to not push very hard.",
     "Draw lightly so you do not tear your paper.",
     "بخفة / برفق", ["light (adj)", "lightness (n)"]),
    (15, "Principal",   "👩‍💼", "noun",
     "A principal is a person in charge of a school.",
     "My school's principal can be very strict with the rules.",
     "مدير المدرسة", ["principals (pl)"]),
    (16, "Row",         "🪑", "noun",
     "A row is a line of things.",
     "James put all of his toy soldiers into neat rows.",
     "صف", ["rows (pl)", "row (v)"]),
    (17, "Shelf",       "🗄️", "noun",
     "A shelf is a place on a wall where you put things.",
     "I keep my clothes on a shelf in my closet.",
     "رف", ["shelves (pl)"]),
    (18, "Spite",       "😤", "noun",
     "Spite is the desire to be mean.",
     "He snuck into his sister's room and stole her bag out of spite.",
     "حقد / خبث", ["spiteful (adj)", "spitefully (adv)"]),
    (19, "Super",       "🦸", "adjective",
     "Super means really good.",
     "My dad said I did a super job cleaning the house.",
     "رائع / ممتاز", ["superb (adj)", "superior (adj)"]),
    (20, "Wet",         "💧", "adjective",
     "A wet thing has water on it.",
     "Since my dog was wet, he tried to shake all the water off his body.",
     "مبلل / رطب", ["wetter (comp)", "wetness (n)"]),
]

STORY_11 = """
<p>
  It was the worst morning ever. When Carl woke up, he realized that he hadn't done his
  <span class="vocab">astronomy</span> and <span class="vocab">chemistry</span> homework.
  Also, the <span class="vocab">forecast</span> called for rain, and that would mean no
  baseball practice. Suddenly, his mother <span class="vocab">interfered</span>: "Take out
  the garbage right now!" When Carl returned from taking the garbage outside, he was all
  <span class="vocab">wet</span>. "What a terrible day!" he said.
</p>
<p>
  He walked to class. He put his umbrella on the <span class="vocab">shelf</span> and sat
  in the third <span class="vocab">row</span>. But the teacher asked why Carl's umbrella
  was on the floor. He told her not to <span class="vocab">blame</span> him because it had
  fallen down. But she sent him to the <span class="vocab">principal</span> anyway out of
  <span class="vocab">spite</span>.
</p>
<p>
  Next, he took a <span class="vocab">geography</span> test.
  <span class="vocab">Despite</span> studying, Carl didn't know the answers. He started
  drawing patterns <span class="vocab">lightly</span> on his paper.
</p>
<p>
  Carl drew a huge <span class="vocab">dinosaur</span>. What if it were real? He saw it
  in his mind. Carl's friends said he was a <span class="vocab">genius</span> for creating
  a dinosaur. Soon, Carl's <span class="vocab">fame</span> spread through school. He taught
  his dinosaur to be very <span class="vocab">gentle</span> and
  <span class="vocab">exhibited</span> it to the public. But
  <span class="vocab">admission</span> would only be given to those who paid him a fee.
  His idea was <span class="vocab">super</span>.
</p>
<p>
  "It's time to turn in your tests," the teacher said. Carl looked at his paper. As he
  was dreaming in class, he hadn't finished the test!
</p>
"""

QUESTIONS_11 = [
    {"q": "What is this story about?",
     "opts": ["A wet classroom",
              "A boy who is a genius",
              "A bell that keeps ringing",
              "A day that was not super"],
     "ans": 3},
    {"q": "What does Carl think his dinosaur can do for him?",
     "opts": ["Make money for him with admission fees",
              "Help him with taking out the garbage",
              "Take the blame for failing geography",
              "Reach things on the top shelf"],
     "ans": 0},
    {"q": "What did Carl do during the geography test?",
     "opts": ["Break a jar at breakfast",
              "Draw lightly on his test paper",
              "Forget his hat on the bus",
              "Stay after school for being late"],
     "ans": 1},
    {"q": "Despite Carl studying for his test, what happened?",
     "opts": ["His teacher was not gentle with him.",
              "He had to sit in the last row.",
              "The exhibit did not earn him any fame.",
              "He did not do well on his geography test."],
     "ans": 3},
    {"q": "Why was Carl sent to the principal?",
     "opts": ["He refused to do his homework",
              "He was late to class",
              "The teacher blamed him for the umbrella on the floor",
              "He drew on the geography test instead of writing"],
     "ans": 2},
    {"q": "What interfered with Carl's morning at home?",
     "opts": ["His chemistry teacher called",
              "His mother told him to take out the garbage",
              "He could not find his umbrella",
              "The forecast was wrong"],
     "ans": 1},
    {"q": "Where did Carl sit in the classroom?",
     "opts": ["In the first row",
              "Near the window",
              "In the third row",
              "Next to the principal's office"],
     "ans": 2},
    {"q": "In Carl's daydream, how did his dinosaur fame spread?",
     "opts": ["He exhibited it at the school fair",
              "His teacher announced it to the class",
              "His friends said he was a genius for creating it",
              "He posted pictures on the school board"],
     "ans": 2},
    {"q": "What was Carl's plan for his dinosaur exhibit?",
     "opts": ["Let everyone in for free",
              "Charge an admission fee",
              "Give it to the principal as a gift",
              "Enter it in a geography competition"],
     "ans": 1},
    {"q": "What happened to Carl at the very end of the story?",
     "opts": ["He got a perfect score on his test",
              "He received detention for drawing",
              "His teacher praised his dinosaur drawings",
              "He realized he had not finished his test"],
     "ans": 3},
]

seed_unit(11, WORDS_11, "Dinosaur Drawings", STORY_11, QUESTIONS_11)

# ── UNIT 12 ───────────────────────────────────────────────────────────────────

WORDS_12 = [
    (1,  "Abuse",       "🚫", "verb",
     "To abuse is to hurt someone or something on purpose.",
     "The mean man abused his dog when it barked too loudly.",
     "يُسيء / إساءة", ["abuses", "abused", "abuse (n)", "abusive (adj)"]),
    (2,  "Afford",      "💰", "verb",
     "To afford something means to have enough money to pay for it.",
     "I've been saving my money so I can afford to buy a new bike.",
     "يتحمل التكلفة / يستطيع الدفع", ["affords", "afforded", "affordable (adj)"]),
    (3,  "Bake",        "🥧", "verb",
     "To bake means to cook food in an oven.",
     "My sister is a good cook. She bakes delicious cakes.",
     "يخبز", ["bakes", "baked", "baker (n)", "bakery (n)"]),
    (4,  "Bean",        "🫘", "noun",
     "A bean is a plant seed that is good to eat.",
     "There are many different kinds of beans to eat.",
     "فاصوليا", ["beans (pl)"]),
    (5,  "Candle",      "🕯️", "noun",
     "A candle is a stick of wax that is lit on fire for light or heat.",
     "When the lights went out, we lit some candles.",
     "شمعة", ["candles (pl)", "candlelight (n)"]),
    (6,  "Convert",     "🔄", "verb",
     "To convert something is to change it into something else.",
     "The man converted his messy field into a garden of flowers.",
     "يحول / يغير", ["converts", "converted", "conversion (n)"]),
    (7,  "Debt",        "💳", "noun",
     "A debt is an amount of money that a person owes.",
     "I have not paid my gas bill. I owe a debt to the gas company.",
     "دين", ["debts (pl)", "debtor (n)"]),
    (8,  "Decrease",    "📉", "verb",
     "To decrease something is to make it less than it was before.",
     "Hiring more police officers has decreased crime in the city.",
     "يُقلل / ينقص", ["decreases", "decreased", "decrease (n)"]),
    (9,  "Fault",       "❌", "noun",
     "A fault is responsibility for a mistake.",
     "It is my fault that the cat ran away. I left the door open.",
     "خطأ / ذنب", ["faults (pl)", "faulty (adj)"]),
    (10, "Fund",        "💵", "noun",
     "A fund is an amount of money that people have.",
     "We all put money into our club's fund.",
     "صندوق / أموال", ["funds (pl)", "fund (v)", "funding (n)"]),
    (11, "Generous",    "🤲", "adjective",
     "A generous person likes to give things to people.",
     "The generous man donated several new computers to our school.",
     "كريم / سخي", ["generously (adv)", "generosity (n)"]),
    (12, "Ingredient",  "🥕", "noun",
     "An ingredient is something that is part of a food dish.",
     "The main ingredients in cake are eggs, sugar, and flour.",
     "مكوّن", ["ingredients (pl)"]),
    (13, "Insist",      "✊", "verb",
     "To insist means to be firm in telling people what to do.",
     "I insist that you try some of these cookies.",
     "يُصرّ", ["insists", "insisted", "insistence (n)"]),
    (14, "Mess",        "🌪️", "noun",
     "A mess is a condition that is not clean or neat.",
     "The kitchen was a complete mess after cooking.",
     "فوضى", ["messy (adj)", "messes (pl)"]),
    (15, "Metal",       "⚙️", "noun",
     "Metal is a strong material used to build things.",
     "Steel is a common metal that is used to build buildings.",
     "معدن", ["metals (pl)", "metallic (adj)"]),
    (16, "Monitor",     "👀", "verb",
     "To monitor people or things is to watch them carefully.",
     "The teacher monitors the students when they take tests.",
     "يراقب", ["monitors", "monitored", "monitor (n)"]),
    (17, "Oppose",      "🤜", "verb",
     "To oppose something means to dislike it or act against it.",
     "I want to be a police officer because I oppose crime.",
     "يعارض", ["opposes", "opposed", "opposition (n)"]),
    (18, "Passive",     "😑", "adjective",
     "A passive person does not take action to solve problems.",
     "Marcie is so passive that she never solves her own problems.",
     "سلبي / غير فاعل", ["passively (adv)"]),
    (19, "Quantity",    "📦", "noun",
     "A quantity is a certain amount of something.",
     "I have a small quantity of milk in my glass.",
     "كمية", ["quantities (pl)"]),
    (20, "Sue",         "⚖️", "verb",
     "To sue is to take someone to court for some harmful action.",
     "I sued the company after I slipped on a banana peel in their hallway.",
     "يقاضي / يرفع دعوى", ["sues", "sued", "lawsuit (n)"]),
]

STORY_12 = """
<p>
  Once there was a chef who was mean to his cooks. He was mean to the people who came in
  to eat. He charged too much for meals. Many people were not able to
  <span class="vocab">afford</span> the cheapest <span class="vocab">bean</span> dish.
  When his <span class="vocab">metal</span> oven broke, he did not have it fixed. So
  everything they tried to <span class="vocab">bake</span> in it burned. The only light
  was from <span class="vocab">candles</span>, and the whole place was a
  <span class="vocab">mess</span>. Sometimes, he didn't pay his waiters. Since they had
  no <span class="vocab">funds</span>, they had many <span class="vocab">debts</span>.
</p>
<p>
  The chef behaved this way all the time. He <span class="vocab">monitored</span> the
  cooks and got angry if they did not do things his way.
</p>
<p>
  One day, the cooks decided that they were tired of the <span class="vocab">abuse</span>
  and that they would not be <span class="vocab">passive</span> anymore. Everyone
  <span class="vocab">opposed</span> the chef. At first, they thought about
  <span class="vocab">suing</span> him. Instead, they made him sit quietly while they
  controlled the restaurant! They <span class="vocab">decreased</span> the price of food.
  They used the best <span class="vocab">ingredients</span> and served large
  <span class="vocab">quantities</span> of food. They repaired the equipment. They turned
  on the lights. The whole place was <span class="vocab">converted</span> into a happy
  place. For the first time, many people came to eat.
</p>
<p>
  The chef realized that the restaurant's problems were his <span class="vocab">fault</span>.
  The chef learned an important lesson, and now the <span class="vocab">generous</span>
  chef <span class="vocab">insisted</span> on giving the customers a free meal.
</p>
"""

QUESTIONS_12 = [
    {"q": "What is this story about?",
     "opts": ["How a mean chef was converted into a generous man",
              "Why metal ovens bake food until it burns",
              "Why waiters' funds are not enough to pay their debts",
              "How simple beans brought a large quantity of customers"],
     "ans": 0},
    {"q": "Why could people not afford to eat at the restaurant?",
     "opts": ["The chef insisted they take free food.",
              "The chef made prices too high.",
              "The chef monitored the cooks.",
              "The chef got tied up."],
     "ans": 1},
    {"q": "What did the chef learn at the end of the story?",
     "opts": ["Electricity was better than using candles.",
              "It was his fault that the restaurant did so well.",
              "The waiters and cooks took over his restaurant.",
              "Behaving in a nice way is better than being mean."],
     "ans": 3},
    {"q": "According to the passage, all the following are true of the waiters and cooks EXCEPT ______.",
     "opts": ["they decreased prices",
              "they used good ingredients",
              "they were replaced by robots",
              "they opposed the abuse of the chef"],
     "ans": 2},
    {"q": "What happened to the chef's metal oven?",
     "opts": ["It was converted into a bean cooker",
              "The cooks repaired it themselves",
              "It broke and was not fixed",
              "The chef bought a new one"],
     "ans": 2},
    {"q": "What problem did the waiters have because of the chef?",
     "opts": ["They were monitored too closely",
              "They were passive about their work",
              "They had no funds and many debts",
              "They were forced to bake all day"],
     "ans": 2},
    {"q": "What did the cooks first think about doing to oppose the chef?",
     "opts": ["Converting the restaurant into a cafe",
              "Decreasing the menu prices themselves",
              "Suing him",
              "Monitoring his every move"],
     "ans": 2},
    {"q": "What changes did the cooks make to the restaurant?",
     "opts": ["They increased food quantity and decreased prices",
              "They removed all the candles and metal equipment",
              "They hired a new generous chef",
              "They gave the funds to a local charity"],
     "ans": 0},
    {"q": "After the chef sat quietly, who controlled the restaurant?",
     "opts": ["The customers",
              "The waiters and cooks",
              "The building's owner",
              "A committee of chefs"],
     "ans": 1},
    {"q": "How did the chef change by the end of the story?",
     "opts": ["He remained passive and mean",
              "He became generous and insisted on giving free meals",
              "He continued to monitor the cooks",
              "He opposed all changes to the restaurant"],
     "ans": 1},
]

seed_unit(12, WORDS_12, "The Mean Chef", STORY_12, QUESTIONS_12)

# ── UNIT 13 ───────────────────────────────────────────────────────────────────

WORDS_13 = [
    (1,  "Adequate",    "✔️", "adjective",
     "Adequate means good enough.",
     "This is adequate for my needs.",
     "كافٍ / مناسب", ["adequately (adv)", "inadequate (opp)"]),
    (2,  "Anxiety",     "😰", "noun",
     "Anxiety is a feeling of worry and fear.",
     "When I have to climb to high places, I'm filled with anxiety.",
     "قلق", ["anxious (adj)", "anxiously (adv)"]),
    (3,  "Army",        "🪖", "noun",
     "An army is a large group of people who fight in wars.",
     "The army protected all the people in the country.",
     "جيش", ["armies (pl)", "armed (adj)"]),
    (4,  "Billion",     "💰", "noun",
     "A billion is a very large number: 1,000,000,000.",
     "There are billions of stars in outer space.",
     "مليار", ["billions (pl)", "billionaire (n)"]),
    (5,  "Carve",       "🪚", "verb",
     "To carve means to cut into something.",
     "My father usually carves the turkey for Thanksgiving.",
     "ينحت / يحفر", ["carves", "carved", "carving (n)"]),
    (6,  "Consult",     "🤝", "verb",
     "To consult means to ask someone for help.",
     "I will consult my accountant to find a way to pay my bills.",
     "يستشير", ["consults", "consulted", "consultation (n)"]),
    (7,  "Emergency",   "🚨", "noun",
     "An emergency is a time when someone needs help right away.",
     "There is a huge fire in my house! This is an emergency!",
     "طوارئ / حالة طارئة", ["emergencies (pl)", "emergent (adj)"]),
    (8,  "Fortune",     "🍀", "noun",
     "Fortune means the things that happen but are not controlled by a person.",
     "I have good fortune when I play cards.",
     "حظ / ثروة", ["fortunes (pl)", "fortunate (adj)", "fortunately (adv)"]),
    (9,  "Guarantee",   "📜", "verb",
     "To guarantee means to promise that something will happen.",
     "I guarantee that the sun will come up in the morning.",
     "يضمن / ضمان", ["guarantees", "guaranteed", "guarantee (n)"]),
    (10, "Initial",     "🔤", "adjective",
     "Initial shows that something is first.",
     "The initial step when writing a paper is to find a good topic.",
     "أولي / ابتدائي", ["initially (adv)", "initiate (v)"]),
    (11, "Intense",     "🔥", "adjective",
     "Something intense is very strong.",
     "The skunk made an intense odor that filled the air.",
     "شديد / مكثف", ["intensely (adv)", "intensity (n)"]),
    (12, "Lend",        "🤲", "verb",
     "To lend something is to give it to someone for a short time.",
     "My sister lent me her pen, so I will return it.",
     "يُعير / يُقرض", ["lends", "lent (past)", "lender (n)"]),
    (13, "Peak",        "⛰️", "noun",
     "The peak is the very top of a mountain.",
     "There is snow on the peaks of those mountains.",
     "قمة / ذروة", ["peaks (pl)", "peak (v)"]),
    (14, "Potential",   "🌱", "adjective",
     "Potential means capable of being but not yet actual or real.",
     "I've thought of some potential problems with your idea.",
     "إمكانية / قدرة محتملة", ["potentially (adv)"]),
    (15, "Pride",       "🦁", "noun",
     "Pride is a feeling of happiness about oneself or one's things.",
     "I take pride in getting good grades.",
     "كبرياء / فخر", ["proud (adj)", "proudly (adv)"]),
    (16, "Proof",       "🔍", "noun",
     "Proof is a fact that shows something is real.",
     "They used his fingerprint as proof that he committed the crime.",
     "دليل / إثبات", ["prove (v)", "proven (adj)"]),
    (17, "Quit",        "🚪", "verb",
     "To quit something means to stop doing it.",
     "I quit running because I got tired.",
     "يتوقف / يستقيل", ["quits", "quit (past)"]),
    (18, "Spin",        "🌀", "verb",
     "To spin is to turn around in circles.",
     "The boy kept spinning until he fell down.",
     "يدور / يلف", ["spins", "spun (past)", "spinner (n)"]),
    (19, "Tiny",        "🐜", "adjective",
     "A tiny thing is very small.",
     "A baby's hand is tiny.",
     "صغير جداً", ["tinier (comp)", "tiniest (sup)"]),
    (20, "Tutor",       "👨‍🏫", "noun",
     "A tutor is someone who gives lessons to one student.",
     "My sister is bad at math. So my mother hired a tutor to help her.",
     "مدرس خاص", ["tutors (pl)", "tutor (v)", "tutoring (n)"]),
]

STORY_13 = """
<p>
  One day, a cat climbed a mountain. When he reached the <span class="vocab">peak</span>,
  he met a fox. They began talking about how to get away from their enemies.
</p>
<p>
  "I am very smart. I have the <span class="vocab">potential</span> to think of
  <span class="vocab">billions</span> of ideas. For instance, I can
  <span class="vocab">carve</span> a <span class="vocab">tiny</span> hole in a tree and
  then climb in," the fox said. He added, "I have a lot of friends. If I am in trouble,
  I can call them to <span class="vocab">lend</span> their help. I can escape a whole
  <span class="vocab">army</span> if I have to!"
</p>
<p>
  Then, the fox asked, "What are your plans?" The cat said, "I have only one plan. Climb
  a tree." The fox said, "I hope you have good <span class="vocab">fortune</span>, then!
  However, one plan does not seem to be <span class="vocab">adequate</span>. Do you want
  me to be your <span class="vocab">tutor</span>? I can help you develop many new plans."
  The cat said, "I <span class="vocab">guarantee</span> that my plan works every time.
  We can <span class="vocab">quit</span> talking about it."
</p>
<p>
  Soon, they saw a group of wolves. It was clearly an
  <span class="vocab">emergency</span> and the time to put plans into action. The cat
  quickly followed her plan. She ran up a tree. The fox was so full of
  <span class="vocab">intense</span> <span class="vocab">anxiety</span> that he could
  not decide which plan to use. "What should my <span class="vocab">initial</span> move
  be? Should I <span class="vocab">consult</span> my friends?" All he could do was
  <span class="vocab">spin</span> in a circle. The wolves caught the fox. The cat was
  full of <span class="vocab">pride</span>. This is <span class="vocab">proof</span>
  that having one good plan is better than having many bad plans.
</p>
"""

QUESTIONS_13 = [
    {"q": "What is this story about?",
     "opts": ["Why cats have good fortune",
              "How you make guarantees about plans",
              "Why you need a good plan in an emergency",
              "How foxes have the potential to make billions of plans"],
     "ans": 2},
    {"q": "Why did the fox feel intense anxiety?",
     "opts": ["Because he tried to spin in circles",
              "Because his army of friends did not lend their help",
              "Because he did not know what his initial move should be",
              "Because he could not find a tree in which to carve a tiny hole"],
     "ans": 2},
    {"q": "Why was the cat full of pride at the end of the story?",
     "opts": ["He climbed the mountain peak.",
              "He had proof that his plan was best.",
              "He did not let the fox become his tutor.",
              "He loved to hide in the trees."],
     "ans": 1},
    {"q": "According to the passage, all the following are true EXCEPT ______.",
     "opts": ["the fox got caught by the wolves",
              "the cat did not get caught by the wolves",
              "the fox said he could consult his friends if he got into trouble",
              "the fox decided to quit thinking of plans and just use one"],
     "ans": 3},
    {"q": "Where did the cat and the fox first meet?",
     "opts": ["At the bottom of a valley",
              "Near the fox's den",
              "At the peak of a mountain",
              "Inside a carved tree hole"],
     "ans": 2},
    {"q": "What did the fox offer to do for the cat?",
     "opts": ["Lend the cat some of his army friends",
              "Be the cat's tutor to teach more plans",
              "Carve a hiding hole in a tree for the cat",
              "Consult his friends on the cat's behalf"],
     "ans": 1},
    {"q": "What was the cat's only plan to escape enemies?",
     "opts": ["Spin in circles to confuse them",
              "Call an army of friends",
              "Climb a tree",
              "Carve a tiny hole in a tree"],
     "ans": 2},
    {"q": "What did the fox say about having only one plan?",
     "opts": ["It was adequate for any emergency",
              "It was proof of real intelligence",
              "One plan did not seem adequate",
              "One plan had the potential to work every time"],
     "ans": 2},
    {"q": "When the wolves appeared, what did the fox do instead of using a plan?",
     "opts": ["Called his army of friends",
              "Climbed a tree",
              "Ran to the peak of the mountain",
              "Spun in a circle"],
     "ans": 3},
    {"q": "What is the main lesson of 'The Cat and the Fox'?",
     "opts": ["Foxes always have more potential than cats",
              "One reliable plan is better than many unreliable ones",
              "You should always consult friends in an emergency",
              "It is best to quit talking and start spinning"],
     "ans": 1},
]

seed_unit(13, WORDS_13, "The Cat and the Fox", STORY_13, QUESTIONS_13)

# ── UNIT 14 ───────────────────────────────────────────────────────────────────

WORDS_14 = [
    (1,  "Apparent",    "👁️", "adjective",
     "Apparent means clear or easy to see.",
     "Her happiness was apparent from the smile on her face.",
     "واضح / ظاهر", ["apparently (adv)"]),
    (2,  "Blind",       "🙈", "adjective",
     "A blind person or animal cannot see.",
     "The blind man didn't see the hole and almost fell in.",
     "أعمى / كفيف", ["blindly (adv)", "blindness (n)"]),
    (3,  "Calculate",   "🧮", "verb",
     "To calculate is to find an answer using math.",
     "She calculated how much money she would need to buy the car.",
     "يحسب", ["calculates", "calculated", "calculation (n)", "calculator (n)"]),
    (4,  "Chat",        "💬", "verb",
     "To chat is to talk with someone.",
     "Even though they were far apart, the couple chatted every day.",
     "يتحدث / يدردش", ["chats", "chatted", "chat (n)"]),
    (5,  "Commit",      "🤝", "verb",
     "To commit to something is to promise to do it.",
     "Sam wanted to go home, but he had committed to finishing the job.",
     "يلتزم", ["commits", "committed", "commitment (n)"]),
    (6,  "Compose",     "✍️", "verb",
     "To compose something is to make it from many sources of information.",
     "Tony composed his report using many sources of information.",
     "يؤلف / يكتب", ["composes", "composed", "composition (n)"]),
    (7,  "Dormitory",   "🏠", "noun",
     "A dormitory is a school building where students live.",
     "I will move into the dormitory at the beginning of the school year.",
     "سكن الطلاب", ["dormitories (pl)", "dorm (short)"]),
    (8,  "Exhaust",     "😓", "verb",
     "To exhaust someone is to make that person very tired.",
     "John exhausted himself by swimming all day.",
     "يُرهق / يستنزف", ["exhausts", "exhausted", "exhaustion (n)"]),
    (9,  "Greenhouse",  "🌿", "noun",
     "A greenhouse is a small glass building that is used to grow plants.",
     "We have a greenhouse in our backyard where we grow plants.",
     "بيت زجاجي / دفيئة", ["greenhouses (pl)"]),
    (10, "Ignore",      "🙉", "verb",
     "To ignore is to act like you do not see or hear something.",
     "I ignored the message he was making and kept studying.",
     "يتجاهل", ["ignores", "ignored", "ignorance (n)"]),
    (11, "Obvious",     "❗", "adjective",
     "Obvious means clear or easy to see.",
     "It was obvious that he was tired. He kept falling asleep.",
     "واضح / بديهي", ["obviously (adv)"]),
    (12, "Physics",     "⚛️", "noun",
     "Physics is a science that deals with energy and how it affects things.",
     "In physics class, we learned about Newton's Cradle to learn about energy.",
     "علم الفيزياء", ["physical (adj)", "physicist (n)"]),
    (13, "Portion",     "🍽️", "noun",
     "A portion is something that is a part of something.",
     "I only ate a small portion of the pizza.",
     "جزء / حصة", ["portions (pl)", "portion (v)"]),
    (14, "Remind",      "🔔", "verb",
     "To remind is to tell someone to remember to do something.",
     "Nick's dad reminded him to do his homework.",
     "يُذكّر", ["reminds", "reminded", "reminder (n)"]),
    (15, "Secretary",   "📋", "noun",
     "A secretary is a person who works in an office.",
     "Rebecca asked her secretary to type a report.",
     "سكرتير / أمين سر", ["secretaries (pl)", "secretarial (adj)"]),
    (16, "Severe",      "⚠️", "adjective",
     "Severe means very bad or serious.",
     "After hitting his hand with the hammer, Sam was in severe pain.",
     "شديد / حاد", ["severely (adv)", "severity (n)"]),
    (17, "Talent",      "🌟", "noun",
     "A talent is a natural ability to do something well.",
     "Maria has a talent for playing the piano.",
     "موهبة", ["talents (pl)", "talented (adj)"]),
    (18, "Thesis",      "📄", "noun",
     "A thesis is an idea that needs to be proved.",
     "She did not support her thesis very well.",
     "أطروحة / رسالة علمية", ["theses (pl)"]),
    (19, "Uniform",     "👔", "noun",
     "A uniform is a piece of clothing worn by people of the same group.",
     "All the members of our marching band wear matching uniforms.",
     "زي موحد", ["uniforms (pl)"]),
    (20, "Vision",      "👁️", "noun",
     "Vision is the ability to see things.",
     "The eye doctor tested my vision.",
     "بصر / رؤية", ["visual (adj)", "visually (adv)"]),
]

STORY_14 = """
<p>
  Sue left her <span class="vocab">dormitory</span> early that morning. She had even
  washed her <span class="vocab">uniform</span> the night before. She wanted to look
  nice for the day.
</p>
<p>
  Sue was <span class="vocab">committed</span> to learning, and she had a
  <span class="vocab">talent</span> for getting good grades. In fact, Sue didn't sleep
  much. She <span class="vocab">calculated</span>, however, that she only had enough
  time for a few hours of sleep. She <span class="vocab">composed</span> a paper and
  did some work on her <span class="vocab">thesis</span> about the importance of
  <span class="vocab">greenhouses</span>. She also studied for her
  <span class="vocab">physics</span> test. Sue was already tired.
</p>
<p>
  During the test, she felt sick. Her face got hot, and her
  <span class="vocab">vision</span> began to become unclear. She was
  <span class="vocab">blind</span> for a moment. The teacher saw Sue's
  <span class="vocab">apparent</span> problem. He wanted to send her to the nurse,
  but she wouldn't go. Sue still had a <span class="vocab">portion</span> of the
  test to finish.
</p>
<p>
  After that, Sue went to the nurse. After seeing the
  <span class="vocab">secretary</span>, she waited. A few minutes later, the nurse
  came in with a glass of juice and told Sue they needed to
  <span class="vocab">chat</span>. "It is <span class="vocab">obvious</span> that you
  have <span class="vocab">exhausted</span> yourself," the nurse said. "If you keep
  working so hard, it could have <span class="vocab">severe</span> results."
</p>
<p>
  "My parents tell me that all the time. I guess I shouldn't
  <span class="vocab">ignore</span> them," Sue said. "You have to
  <span class="vocab">remind</span> yourself that it is OK to rest," the nurse said.
  When Sue got back to her room, she went right to bed. She made sure she got enough
  rest every night after that.
</p>
"""

QUESTIONS_14 = [
    {"q": "What is this story about?",
     "opts": ["A nurse reminding a student about her history paper",
              "How to calculate an answer",
              "A girl's apparent talent for science",
              "A girl who studies so much that she gets sick"],
     "ans": 3},
    {"q": "According to the passage, why did Sue stay up late the night before?",
     "opts": ["She was washing her uniform.",
              "She was ignoring her parents on purpose.",
              "She was talking with friends.",
              "She was cleaning her dormitory."],
     "ans": 0},
    {"q": "What did the nurse bring into the room?",
     "opts": ["A glass of juice",
              "The secretary",
              "Sue's physics test",
              "A vision chart"],
     "ans": 0},
    {"q": "According to the passage, what was obvious to the nurse after seeing Sue?",
     "opts": ["Sue had committed herself to learning.",
              "Sue had exhausted herself.",
              "Sue had done only a portion of the test.",
              "Sue had become blind."],
     "ans": 1},
    {"q": "What was Sue's thesis about?",
     "opts": ["The importance of greenhouses",
              "How to calculate physics problems",
              "Why uniforms are important in school",
              "The talent of good students"],
     "ans": 0},
    {"q": "What happened to Sue's vision during the test?",
     "opts": ["Her vision became super clear",
              "Her vision began to become unclear",
              "She could see the answers clearly",
              "She composed her ideas better"],
     "ans": 1},
    {"q": "Why did Sue refuse to leave during the test?",
     "opts": ["She was ignoring the teacher's concern",
              "She was committed to finishing the exam",
              "She still had a portion of the test to finish",
              "She was not aware of her apparent problem"],
     "ans": 2},
    {"q": "What did the nurse tell Sue she needed?",
     "opts": ["More physics practice",
              "To chat with the secretary",
              "To rest and not ignore the advice",
              "To calculate a better sleep schedule"],
     "ans": 2},
    {"q": "What did Sue do after returning to her dormitory?",
     "opts": ["She composed another paper",
              "She went right to bed",
              "She ignored the nurse's advice",
              "She continued studying her thesis"],
     "ans": 1},
    {"q": "What lesson did Sue learn?",
     "opts": ["Talent is more important than rest",
              "Physics tests are the most severe challenges",
              "It is important to rest and not exhaust yourself",
              "A secretary is more helpful than a nurse"],
     "ans": 2},
]

seed_unit(14, WORDS_14, "The Good Student", STORY_14, QUESTIONS_14)

# ── UNIT 15 ───────────────────────────────────────────────────────────────────

WORDS_15 = [
    (1,  "Absorb",      "🧽", "verb",
     "To absorb a liquid means to take it inside.",
     "He used a sponge to absorb the water on the floor.",
     "يمتص", ["absorbs", "absorbed", "absorption (n)"]),
    (2,  "Boss",        "👔", "noun",
     "A boss is a person in charge of other people at work.",
     "My boss is a nice person.",
     "رئيس / مدير", ["bosses (pl)", "boss (v)", "bossy (adj)"]),
    (3,  "Charitable",  "❤️", "adjective",
     "A charitable organization aims to help people.",
     "I give money each year to a charitable foundation.",
     "خيري", ["charitably (adv)", "charity (n)"]),
    (4,  "Committee",   "👥", "noun",
     "A committee is a group of people who meet together to make decisions.",
     "The school's committee agreed on a new dress code for students.",
     "لجنة", ["committees (pl)"]),
    (5,  "Contract",    "📝", "noun",
     "A contract is a written agreement between two people.",
     "The woman signed a contract when she bought the house.",
     "عقد", ["contracts (pl)", "contract (v)"]),
    (6,  "Crew",        "👷", "noun",
     "A crew is a group of workers.",
     "My father has a crew that helps him build houses.",
     "طاقم / فريق عمل", ["crews (pl)"]),
    (7,  "Devote",      "💪", "verb",
     "To devote time to something means to spend a lot of time doing it.",
     "She devotes two hours a day to playing the piano.",
     "يكرّس / يُخصص", ["devotes", "devoted", "devotion (n)"]),
    (8,  "Dig",         "⛏️", "verb",
     "To dig is to make a hole in the ground.",
     "My dog digs in the yard so he can bury his bones.",
     "يحفر", ["digs", "dug (past)", "digger (n)"]),
    (9,  "Dine",        "🍽️", "verb",
     "Dine means to eat dinner.",
     "The young couple dined at their home.",
     "يتناول العشاء", ["dines", "dined", "dining (n)", "dinner (n)"]),
    (10, "Donate",      "🤲", "verb",
     "To donate is to give something to a charity or organization.",
     "We donate money to charities every year.",
     "يتبرع", ["donates", "donated", "donation (n)", "donor (n)"]),
    (11, "Double",      "✌️", "adjective",
     "Double means twice as much or twice as many.",
     "I paid almost double the amount for that shirt.",
     "مضاعف / ضعف", ["doubles", "doubled", "double (adv)"]),
    (12, "Flavor",      "👅", "noun",
     "A flavor is the taste of food or drinks.",
     "The flavor of the ice cream was very good.",
     "نكهة / طعم", ["flavors (pl)", "flavorful (adj)"]),
    (13, "Foundation",  "🏛️", "noun",
     "A foundation is a group that provides money for research.",
     "The foundation raised money to give scholarships to students.",
     "مؤسسة / جمعية", ["foundations (pl)", "found (v)"]),
    (14, "Generation",  "👨‍👩‍👧‍👦", "noun",
     "A generation is a group of people who live at the same time.",
     "My grandparents are from a different generation than me.",
     "جيل", ["generations (pl)", "generational (adj)"]),
    (15, "Handle",      "✋", "noun",
     "A handle is the part of an object people hold while using it.",
     "The pot is very hot, so pick it up by the handle.",
     "مقبض / يد", ["handles (pl)", "handle (v)", "handler (n)"]),
    (16, "Layer",       "📚", "noun",
     "A layer covers something or is one of several pieces lying on top of each other.",
     "There was a layer of snow on the tops of the houses this morning.",
     "طبقة", ["layers (pl)", "layer (v)"]),
    (17, "Mud",         "🟫", "noun",
     "Mud is soft, wet dirt.",
     "My brother played rugby in the mud. Now, he's dirty.",
     "طين / وحل", ["muddy (adj)", "muddier (comp)"]),
    (18, "Smooth",      "✨", "adjective",
     "A smooth thing has no bumps or rough parts.",
     "The baby's skin felt very smooth.",
     "ناعم / أملس", ["smoother (comp)", "smoothly (adv)", "smoothness (n)"]),
    (19, "Soil",        "🌱", "noun",
     "Soil is the top layer of land on the Earth.",
     "The boy planted flowers in the soil and watered them every day.",
     "تربة", ["soils (pl)", "soil (v)"]),
    (20, "Unique",      "🦄", "adjective",
     "A unique person or thing is not like others.",
     "Her dog is unique. I've never seen one quite like it.",
     "فريد / نادر", ["uniquely (adv)", "uniqueness (n)"]),
]

STORY_15 = """
<p>
  Last year, I had a <span class="vocab">unique</span> chance to work with my uncle,
  who has <span class="vocab">devoted</span> his life to studying past
  <span class="vocab">generations</span>. I was part of a <span class="vocab">crew</span>
  of students he had hired. We signed a <span class="vocab">contract</span> to work
  with him. He was the <span class="vocab">boss</span>. We lived far from the nearest
  town, and we <span class="vocab">dined</span> on what we could find. Some of the
  things we ate had an unusual <span class="vocab">flavor</span>.
</p>
<p>
  We had been there about a month and still hadn't found anything. One day, I began
  to <span class="vocab">dig</span> in the <span class="vocab">soil</span>. The
  <span class="vocab">layers</span> of soil got wetter. Soon, I was digging in the
  <span class="vocab">mud</span>. My shovel began to get very heavy. It felt like it
  had <span class="vocab">doubled</span> in weight because the ground had
  <span class="vocab">absorbed</span> such a lot of water.
</p>
<p>
  Finally, I saw something in the mud. It was an old knife! The
  <span class="vocab">handle</span> felt <span class="vocab">smooth</span> in my hand.
  I lifted it up so I could see it better. There was writing on it.
</p>
<p>
  "It will bring good luck," my uncle said with a smile.
</p>
<p>
  The next day, we found many more things. There were pots and tools. My uncle
  <span class="vocab">donated</span> all of the things to a special
  <span class="vocab">committee</span> of a <span class="vocab">charitable</span>
  <span class="vocab">foundation</span>. Many newspapers wrote stories about it.
  It seemed the knife really did bring good luck!
</p>
"""

QUESTIONS_15 = [
    {"q": "What is this story about?",
     "opts": ["How someone found an old knife",
              "A generation of college students",
              "A crew of committee workers digging in the mud",
              "How a smooth knife handle feels"],
     "ans": 0},
    {"q": "All of the following are true EXCEPT ______.",
     "opts": ["the college students signed a contract",
              "the author's uncle worked for a foundation",
              "the items found at the site were donated",
              "the teen worked double the amount of everyone else"],
     "ans": 3},
    {"q": "What is probably true of the teen in the story?",
     "opts": ["He could not read the writing on the knife.",
              "He held a higher position than the other students.",
              "He did not know what the knife was.",
              "He didn't want to devote his time to history."],
     "ans": 2},
    {"q": "Where did the teen find the knife?",
     "opts": ["On top of the soil",
              "Under layers of dirt",
              "In the mud",
              "In his boss's tent"],
     "ans": 2},
    {"q": "Why did the shovel become harder to use?",
     "opts": ["It was too small for deep soil",
              "The ground had absorbed water, making the mud heavy",
              "The layers of dirt were full of rocks",
              "The smooth handle made it hard to grip"],
     "ans": 1},
    {"q": "How did the uncle react to finding the old knife?",
     "opts": ["He was disappointed it was not a pot",
              "He smiled and said it would bring good luck",
              "He donated it to the committee immediately",
              "He was worried about the writing on it"],
     "ans": 1},
    {"q": "What did the uncle do with all the items they found?",
     "opts": ["Kept them in his room",
              "Sold them to a newspaper",
              "Donated them to a charitable foundation",
              "Gave them to the crew as payment"],
     "ans": 2},
    {"q": "What is the uncle devoted to?",
     "opts": ["How soil absorbs water",
              "Studying past generations",
              "Building charitable foundations",
              "Finding unique flavors of food"],
     "ans": 1},
    {"q": "How did the newspapers react to the discovery?",
     "opts": ["They ignored the findings",
              "They criticized the foundation",
              "They wrote stories about it",
              "They donated money to the crew"],
     "ans": 2},
    {"q": "What seemed to be true about the knife at the end of the story?",
     "opts": ["It was too old to be of any value",
              "Only a committee could identify it",
              "It was a unique flavor of ancient culture",
              "It really did bring the crew good luck"],
     "ans": 3},
]

seed_unit(15, WORDS_15, "The Lucky Knife", STORY_15, QUESTIONS_15)

db.commit()
print("Done — Units 10-15 seeded successfully.")
db.close()
