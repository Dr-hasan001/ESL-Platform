"""
seed_book2_units16_17_19_20.py
Seeds Book 2 (A2) Units 16, 17, 19, and 20.
(Units 15 and 18 are already seeded.)

Run: python tools/seed_book2_units16_17_19_20.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.book import Book, Unit, Word, UnitStory

Base.metadata.create_all(bind=engine)
db = SessionLocal()

book = db.query(Book).filter(Book.book_number == 2).first()
if not book:
    print("ERROR: Book 2 not found.")
    db.close()
    sys.exit(1)


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
        db.add(UnitStory(
            unit_id=unit.id,
            story_title=story_title,
            story_html=story_html,
            story_questions=questions,
        ))
    print(f"Unit {unit_number}: {len(words_data)} words, story '{story_title}', {len(questions)} questions.")


# ── UNIT 16 ────────────────────────────────────────────────────────────────────

WORDS_16 = [
    (1,  "Academy",    "🏫", "noun",
     "An academy is a special type of school.",
     "There are many courses taught at the academy that I go to.",
     "أكاديمية",
     ["academies (pl)", "academic (adj)"]),

    (2,  "Ancient",    "🏛️", "adjective",
     "If something is ancient, it is very old.",
     "I want to see the ancient buildings in Rome.",
     "قديم",
     ["anciently (adv)"]),

    (3,  "Board",      "🪵", "noun",
     "A board is a flat piece of wood.",
     "The sign was made of fine wooden boards.",
     "لوح",
     ["boards (pl)", "board (v)"]),

    (4,  "Century",    "📅", "noun",
     "A century is one hundred years.",
     "Our company is celebrating a century of business in London.",
     "قرن",
     ["centuries (pl)", "centennial (adj)"]),

    (5,  "Clue",       "🔎", "noun",
     "A clue is a fact or object that helps solve a mystery or crime.",
     "The detective found some clues on the sidewalk.",
     "دليل / إشارة",
     ["clues (pl)"]),

    (6,  "Concert",    "🎶", "noun",
     "A concert is a performance where you listen to people play music.",
     "I enjoyed the concert last night. The band was very good.",
     "حفل موسيقي",
     ["concerts (pl)"]),

    (7,  "County",     "🗺️", "noun",
     "A county is the largest division of a state or a country.",
     "He wanted to represent the citizens of his county.",
     "مقاطعة",
     ["counties (pl)"]),

    (8,  "Dictionary", "📖", "noun",
     "A dictionary is a book that tells you what words mean.",
     "I use the dictionary to learn new words.",
     "قاموس",
     ["dictionaries (pl)"]),

    (9,  "Exist",      "🌍", "verb",
     "To exist is to be real.",
     "Do you really think that unicorns ever existed?",
     "يوجد",
     ["exists", "existed", "existence (n)"]),

    (10, "Flat",       "⬜", "adjective",
     "Flat describes something that is level and smooth with no curved parts.",
     "My parents bought a new flat-screen TV on the weekend.",
     "مستوٍ / مسطح",
     ["flatly (adv)", "flatten (v)"]),

    (11, "Gentleman",  "🎩", "noun",
     "A gentleman is a polite and well-mannered man.",
     "My grandfather is a kind and helpful gentleman.",
     "رجل محترم / سيد",
     ["gentlemen (pl)", "gentlemanly (adj)"]),

    (12, "Hidden",     "🙈", "adjective",
     "Hidden means not easily noticed or too hard to find.",
     "The hidden camera recorded everything in the parking lot.",
     "مخفي",
     ["hide (v)", "hid (past)"]),

    (13, "Maybe",      "🤷", "adverb",
     "Maybe means that something is possible or may be true.",
     "If I focus hard enough, maybe I can come up with the right answer.",
     "ربما",
     []),

    (14, "Officer",    "🪖", "noun",
     "An officer is a leader in the army.",
     "The soldiers followed the orders of the officer.",
     "ضابط",
     ["officers (pl)"]),

    (15, "Original",   "🖼️", "adjective",
     "If something is original, it is the first one of that thing.",
     "This is the original painting of the Mona Lisa.",
     "أصلي",
     ["originally (adv)", "origin (n)"]),

    (16, "Pound",      "🔨", "verb",
     "To pound something means to hit it many times with a lot of force.",
     "He pounded the nail with the hammer.",
     "يدق / يطرق",
     ["pounds", "pounded", "pound (n)"]),

    (17, "Process",    "⚙️", "noun",
     "A process is the steps to take to do something.",
     "Making a cake is a long process.",
     "عملية / إجراء",
     ["processes (pl)", "process (v)"]),

    (18, "Publish",    "📰", "verb",
     "To publish a book is to get it printed and ready to sell.",
     "That company publishes daily newspapers.",
     "ينشر / يصدر",
     ["publishes", "published", "publisher (n)", "publication (n)"]),

    (19, "Theater",    "🎭", "noun",
     "A theater is a building where you watch plays, shows, and movies.",
     "We went to the theater to see a play.",
     "مسرح / سينما",
     ["theaters (pl)"]),

    (20, "Wealth",     "💰", "noun",
     "Wealth is the total of one's possessions such as money and land.",
     "One of the most important things for some people is wealth.",
     "ثروة / غنى",
     ["wealthy (adj)", "wealthiest (superlative)"]),
]

STORY_HTML_16 = """
<p>
  Adams <span class="vocab">Academy</span> was a good school. Boys lived there
  and took classes. Tom worked hard all week. On a spring Saturday, he wanted to
  do something fun.
</p>

<p>
  He asked his friend Jeff to go to the movie <span class="vocab">theater</span>.
  "Sorry," Jeff answered. "I'm going to a <span class="vocab">concert</span>."
  So Tom asked Joe to go to the movies. But Joe's soccer team had a game.
</p>

<p>
  Tom next went down the hall to Brad's room. Brad was reading a very large old
  book. "Hi, Brad," Tom said. "Are you reading a
  <span class="vocab">dictionary</span>? It looks <span class="vocab">ancient</span>."
</p>

<p>
  "No. This is called <em>The Wealth of Adams <span class="vocab">County</span></em>.
  It's about <span class="vocab">hidden</span> gold in Adams County. It's more than a
  <span class="vocab">century</span> old. It was <span class="vocab">published</span>
  in 1870! Look, it even has the <span class="vocab">original</span> cover on it."
</p>

<p>
  Tom asked, "Where did you get it?" "It's from my dad's friend. He is a nice
  <span class="vocab">gentleman</span>, an <span class="vocab">officer</span> in the
  army," answered Brad.
</p>

<p>
  "The gold doesn't really <span class="vocab">exist</span>, does it?" Tom asked.
  "I don't know, but <span class="vocab">maybe</span>! There are
  <span class="vocab">clues</span> in this book. Let's find it!" Looking for gold
  sounded like fun.
</p>

<p>
  The first clue was to find a <span class="vocab">flat</span> tree underground.
  "It must be in the forest," Tom said. Brad said, "The flat tree could be a
  <span class="vocab">board</span> under the dirt. It could cover the gold."
</p>

<p>
  Tom and Brad dug in the dirt all morning. The <span class="vocab">process</span>
  of looking for gold made them hungry. They were ready to stop for lunch. But
  then Brad hit something hard. It was a board!
</p>

<p>
  Brad <span class="vocab">pounded</span> on the board until it broke. There was a
  small hole under it. "Look!" He held up a gold coin. Tom saw a piece of paper
  in the hole. "Brad, there's more. It's a map to the rest of the gold!" Brad
  smiled. "Let's go!" And they hurried to find the
  <span class="vocab">wealth</span> of Adams County.
</p>
"""

QUESTIONS_16 = [
    {
        "q": "Where do the boys look for the gold?",
        "opts": [
            "At Adams Academy.",
            "At the movie theater.",
            "In the forest.",
            "In a concert hall.",
        ],
        "ans": 2,
    },
    {
        "q": "What is NOT true about The Wealth of Adams County?",
        "opts": [
            "It was published more than a century ago.",
            "It was written by an army officer.",
            "It still has its original cover.",
            "It is about hidden gold in Adams County.",
        ],
        "ans": 1,
    },
    {
        "q": "Why does Brad think the gold really exists?",
        "opts": [
            "Because there are clues to it in a book.",
            "Because a gentleman told him it did.",
            "Because he was given an ancient dictionary.",
            "Because it was hidden in the spring.",
        ],
        "ans": 0,
    },
    {
        "q": "Where will the boys probably go at the end of the story?",
        "opts": [
            "To get tools to carry the gold.",
            "To continue the process of finding gold.",
            "To watch Joe's soccer team.",
            "To pound on more boards.",
        ],
        "ans": 1,
    },
    {
        "q": "Why can't Jeff go to the movie theater with Tom?",
        "opts": [
            "He is studying at the academy.",
            "He has a soccer game.",
            "He is going to a concert.",
            "He is reading an ancient book.",
        ],
        "ans": 2,
    },
    {
        "q": "What does Brad say about the 'flat tree' clue?",
        "opts": [
            "It is a tree with no leaves in the forest.",
            "It could be a board hidden under the dirt.",
            "It is a clue that does not exist.",
            "It is a painting on an original cover.",
        ],
        "ans": 1,
    },
    {
        "q": "What does Tom find in the hole under the board?",
        "opts": [
            "An ancient dictionary.",
            "A map and a gold coin.",
            "A note from an army officer.",
            "The wealth of the whole county.",
        ],
        "ans": 1,
    },
    {
        "q": "How old is the book The Wealth of Adams County?",
        "opts": [
            "More than a century old.",
            "Only a few years old.",
            "Exactly one hundred years old.",
            "Published last year.",
        ],
        "ans": 0,
    },
    {
        "q": "What does Brad do when he hits something hard?",
        "opts": [
            "He calls the officer for help.",
            "He publishes the discovery.",
            "He pounds on it until it breaks.",
            "He hides it under the dirt again.",
        ],
        "ans": 2,
    },
    {
        "q": "What word best describes Tom and Brad at the end of the story?",
        "opts": [
            "Tired and ready to go home.",
            "Unsure if the gold is real.",
            "Angry at each other.",
            "Excited and ready to find more gold.",
        ],
        "ans": 3,
    },
]


# ── UNIT 17 ────────────────────────────────────────────────────────────────────

WORDS_17 = [
    (1,  "Aim",       "🎯", "noun",
     "An aim is a goal that someone wants to make happen.",
     "My aim is to become a helicopter pilot.",
     "هدف / غاية",
     ["aims (pl)", "aim (v)"]),

    (2,  "Attach",    "📎", "verb",
     "To attach is to put two things together.",
     "I attached the socks to the clothesline to dry.",
     "يربط / يلصق",
     ["attaches", "attached", "attachment (n)"]),

    (3,  "Bet",       "🎰", "verb",
     "To bet is to risk money on the result of a game or a business.",
     "How much will you bet that your horse will win?",
     "يراهن",
     ["bets", "bet (past)", "betting (n)"]),

    (4,  "Carriage",  "🐴", "noun",
     "A carriage is a vehicle pulled by a horse.",
     "We took a carriage ride in the park.",
     "عربة (تجرها الخيل)",
     ["carriages (pl)"]),

    (5,  "Classic",   "⭐", "adjective",
     "A classic thing is something that is common from the past.",
     "The athlete made a classic mistake — he started running too soon.",
     "كلاسيكي / تقليدي",
     ["classically (adv)", "classics (n pl)"]),

    (6,  "Commute",   "🚆", "verb",
     "To commute is to travel a long distance to get to work.",
     "I usually commute to work on the train.",
     "يتنقل / يذهب إلى العمل",
     ["commutes", "commuted", "commuter (n)"]),

    (7,  "Confirm",   "✅", "verb",
     "To confirm is to make sure that something is correct.",
     "Winning the game confirmed that James was a good player.",
     "يؤكد",
     ["confirms", "confirmed", "confirmation (n)"]),

    (8,  "Criticize", "🗣️", "verb",
     "To criticize is to say bad things about someone or something.",
     "He criticized his wife for spending too much money.",
     "ينتقد",
     ["criticizes", "criticized", "criticism (n)", "critic (n)"]),

    (9,  "Differ",    "↔️", "verb",
     "To differ is to not be the same as another person or thing.",
     "I differ from my brother; he is short, while I am tall.",
     "يختلف",
     ["differs", "differed", "difference (n)", "different (adj)"]),

    (10, "Expense",   "💸", "noun",
     "An expense is the money that people spend on something.",
     "She wrote down all the expenses for her trip.",
     "نفقة / مصاريف",
     ["expenses (pl)", "expensive (adj)"]),

    (11, "Formal",    "👔", "adjective",
     "A formal thing is official or serious.",
     "It was a formal dinner, so we wore our best clothes.",
     "رسمي",
     ["formally (adv)", "formality (n)", "informal (opp)"]),

    (12, "Height",    "📏", "noun",
     "Height is how tall someone or something is.",
     "My height is 168 centimeters.",
     "طول / ارتفاع",
     ["heights (pl)", "high (adj)", "tall (adj)"]),

    (13, "Invent",    "💡", "verb",
     "To invent is to create something that never existed before.",
     "My grandfather has invented some interesting things.",
     "يخترع",
     ["invents", "invented", "inventor (n)", "invention (n)"]),

    (14, "Junior",    "🔽", "adjective",
     "A junior person is younger or less experienced.",
     "When she started at the company, she was only a junior manager.",
     "أصغر / أدنى رتبة",
     ["junior (n)", "seniors (opp)"]),

    (15, "Labor",     "🔧", "noun",
     "Labor is the act of doing or making something.",
     "Building the house took a lot of labor.",
     "عمل / جهد",
     ["labors (pl)", "labor (v)", "laborer (n)"]),

    (16, "Mechanic",  "🔩", "noun",
     "A mechanic is someone who fixes vehicles or machines.",
     "We took the car to the mechanic to be fixed.",
     "ميكانيكي",
     ["mechanics (pl)", "mechanical (adj)"]),

    (17, "Prime",     "🥇", "adjective",
     "Prime shows that something is the most important one.",
     "Dirty air is a prime cause of illness.",
     "رئيسي / أساسي",
     ["primarily (adv)", "primary (adj)"]),

    (18, "Shift",     "➡️", "verb",
     "To shift is to move into a different place or direction.",
     "He shifted to the other side of the table to eat his breakfast.",
     "ينتقل / يتحول",
     ["shifts", "shifted", "shift (n)"]),

    (19, "Signal",    "🚦", "noun",
     "A signal is a sound or action that tells someone to do something.",
     "The coach blew his whistle as a signal to begin the game.",
     "إشارة",
     ["signals (pl)", "signal (v)"]),

    (20, "Sincere",   "🤝", "adjective",
     "A sincere person is honest, especially about emotions or opinions.",
     "He sounded sincere when he apologized to me.",
     "صادق / مخلص",
     ["sincerely (adv)", "sincerity (n)"]),
]

STORY_HTML_17 = """
<p>
  My name is Henry Ford, and I <span class="vocab">invented</span> a car called
  the Model T. I used to watch <span class="vocab">carriages</span> on the streets.
  They were very interesting. Then, I got a job as a
  <span class="vocab">junior</span> <span class="vocab">mechanic</span>. My father
  <span class="vocab">criticized</span> me. He wanted me to run the farm.
</p>

<p>
  When I <span class="vocab">shifted</span> to Detroit, I worked for the Detroit
  Auto Company. But I wanted to make cars using less <span class="vocab">labor</span>.
  That way, there would be fewer <span class="vocab">expenses</span>. I started the
  Ford Motor Company in 1903. At first, the company did not do well. But many
  people were <span class="vocab">betting</span> on my success. I also had a
  <span class="vocab">sincere</span> <span class="vocab">aim</span> to make a car
  that anybody could buy.
</p>

<p>
  Then, in 1908, I introduced the Model T. It <span class="vocab">confirmed</span>
  that I was right: it was possible to build a car my way!
</p>

<p>
  The Model T <span class="vocab">differed</span> from other vehicles. Each worker
  would <span class="vocab">attach</span> a different part to the car. This made
  their job easy to learn and saved a lot of time. One Model T could be put together
  in 93 minutes. All of them had the same <span class="vocab">classic</span> design.
  They were all the same size and <span class="vocab">height</span>. The
  <span class="vocab">prime</span> reason for doing this was to save money. We had a
  <span class="vocab">formal</span> ceremony to celebrate our success when the
  millionth car was made in our factory.
</p>

<p>
  Over 19 years, I sold more than 15 million Model Ts. This sent a
  <span class="vocab">signal</span> to other companies. People would buy cars to
  <span class="vocab">commute</span> to work if the price was low enough.
</p>
"""

QUESTIONS_17 = [
    {
        "q": "What is this story about?",
        "opts": [
            "How Ford attached cars and engines.",
            "How Ford aimed to build a car everyone could buy.",
            "Why Ford shifted away from carriages.",
            "Why Ford bet on the gasoline engine.",
        ],
        "ans": 1,
    },
    {
        "q": "How did the Model T change other car companies?",
        "opts": [
            "It confirmed that their expenses were large.",
            "It made workers criticize their bosses about their labor.",
            "It created a signal for them to start making cheaper cars.",
            "It forced car companies to bet on Ford's success.",
        ],
        "ans": 2,
    },
    {
        "q": "In paragraph 1, readers can infer that ______.",
        "opts": [
            "Ford had a very formal childhood.",
            "Ford differed in thought from his father.",
            "Ford was not of great height.",
            "Ford's father was sincere.",
        ],
        "ans": 1,
    },
    {
        "q": "According to the passage, all the following are true EXCEPT ______.",
        "opts": [
            "The Model T had a classic design.",
            "People would use cars to commute if they were not expensive.",
            "Ford worked as a junior mechanic.",
            "The first vehicle from the Ford Motor Company was a truck.",
        ],
        "ans": 3,
    },
    {
        "q": "What was Ford's prime aim when making the Model T?",
        "opts": [
            "To make the most expensive car ever built.",
            "To build a car that anybody could buy.",
            "To attach more engines to each vehicle.",
            "To confirm that Detroit was a great city.",
        ],
        "ans": 1,
    },
    {
        "q": "Why did Ford have each worker attach only one part?",
        "opts": [
            "To make the car more classic looking.",
            "To signal other workers to be careful.",
            "To make the job easy to learn and save time.",
            "To increase the expense of each car.",
        ],
        "ans": 2,
    },
    {
        "q": "What does 'shifted to Detroit' mean in the story?",
        "opts": [
            "Ford changed his car design while in Detroit.",
            "Ford moved to Detroit to find work.",
            "Ford started a formal ceremony in Detroit.",
            "Ford criticized Detroit's labor conditions.",
        ],
        "ans": 1,
    },
    {
        "q": "How long did it take to build one Model T?",
        "opts": [
            "19 minutes.",
            "1903 minutes.",
            "93 minutes.",
            "15 minutes.",
        ],
        "ans": 2,
    },
    {
        "q": "What did Ford's father want him to do instead of going to Detroit?",
        "opts": [
            "Work as a junior mechanic.",
            "Commute to a new city.",
            "Run the farm.",
            "Attach parts to carriages.",
        ],
        "ans": 2,
    },
    {
        "q": "What celebrated the millionth Model T being made?",
        "opts": [
            "A classic car show in Detroit.",
            "A formal ceremony at the factory.",
            "A signal sent to other companies.",
            "A shift in labor cost.",
        ],
        "ans": 1,
    },
]


# ── UNIT 19 ────────────────────────────────────────────────────────────────────

WORDS_19 = [
    (1,  "Ball",        "⚽", "noun",
     "A ball is a round object that is thrown, kicked, or hit in a game or sport.",
     "Seth bought a new soccer ball.",
     "كرة",
     ["balls (pl)"]),

    (2,  "Bottom",      "⬇️", "noun",
     "The bottom is the lowest part, place, or level of something.",
     "Sarah is so tall that her feet can touch the bottom of the swimming pool.",
     "قاع / أسفل",
     ["bottoms (pl)", "bottomless (adj)"]),

    (3,  "Company",     "🏢", "noun",
     "A company is a business or organization that makes or sells goods or services.",
     "I want to work for a small software company.",
     "شركة",
     ["companies (pl)"]),

    (4,  "Drink",       "🥤", "verb",
     "To drink is to take liquid into the body through the mouth.",
     "The woman likes to drink water after she exercises.",
     "يشرب",
     ["drinks", "drank (past)", "drunk (pp)", "drink (n)"]),

    (5,  "Few",         "🔢", "adjective",
     "A few things means a small number of them.",
     "I have only a few coins.",
     "قليل",
     ["fewer (comparative)", "fewest (superlative)"]),

    (6,  "Line",        "🚶", "noun",
     "A line is a row of people or things.",
     "This is the longest line I have ever seen.",
     "طابور / صف",
     ["lines (pl)", "line (v)"]),

    (7,  "Pet",         "🐶", "noun",
     "A pet is an animal such as a cat or dog that people keep and care for.",
     "Tyler likes to spend time with his pet dog.",
     "حيوان أليف",
     ["pets (pl)", "pet (adj)"]),

    (8,  "Product",     "📦", "noun",
     "A product is something grown or made in a factory in order to be sold.",
     "There is no room for even one more product in Marissa's bag.",
     "منتج",
     ["products (pl)", "produce (v)", "production (n)"]),

    (9,  "Responsible", "👤", "adjective",
     "A responsible person is in charge of someone or something.",
     "Peter is responsible for leading his department.",
     "مسؤول",
     ["responsibly (adv)", "responsibility (n)"]),

    (10, "Sell",        "🛒", "verb",
     "To sell is to give something to someone in exchange for money.",
     "This man's job is to sell houses.",
     "يبيع",
     ["sells", "sold (past)", "seller (n)", "sale (n)"]),

    (11, "Snake",       "🐍", "noun",
     "A snake is an animal with a long, thin body and no legs.",
     "Be careful of the snakes in the tree.",
     "ثعبان",
     ["snakes (pl)", "snaky (adj)"]),

    (12, "Stand",       "🧍", "verb",
     "To stand is to use the legs and feet to hold the body upright.",
     "Alan prefers to stand and work at his desk.",
     "يقف",
     ["stands", "stood (past)", "standing (adj)"]),

    (13, "Strange",     "😮", "adjective",
     "A strange thing is unusual or surprising.",
     "They are wearing very strange costumes.",
     "غريب",
     ["strangely (adv)", "strangeness (n)"]),

    (14, "Tea",         "🍵", "noun",
     "Tea is a drink made by pouring boiling water over dried leaves.",
     "Many people drink green tea because it has many health benefits.",
     "شاي",
     ["teas (pl)"]),

    (15, "Test",        "🔬", "verb",
     "To test is to examine something to see if its quality is good.",
     "His job is to test the electricity to make sure it works correctly.",
     "يختبر / يفحص",
     ["tests", "tested", "test (n)", "tester (n)"]),

    (16, "Tongue",      "👅", "noun",
     "A tongue is the muscle inside the mouth used to speak, eat, and taste.",
     "The cat uses its tongue to drink water.",
     "لسان",
     ["tongues (pl)"]),

    (17, "They",        "👥", "pronoun",
     "They refers to two or more people or things.",
     "They are playing a fun game.",
     "هم / هن",
     ["them (obj)", "their (poss)", "theirs (poss)"]),

    (18, "Type",        "🗂️", "noun",
     "A type is a particular kind or group of things or people.",
     "Tulips are a type of flower.",
     "نوع",
     ["types (pl)", "typical (adj)"]),

    (19, "Very",        "‼️", "adverb",
     "Very is used to emphasize an adjective or adverb.",
     "A snake is a very big animal.",
     "جداً",
     []),

    (20, "Wait",        "⏳", "verb",
     "To wait is to stay in a place until an expected event happens.",
     "She has to wait for the airplane to arrive.",
     "ينتظر",
     ["waits", "waited", "wait (n)"]),
]

STORY_HTML_19 = """
<p>
  <span class="vocab">Strange</span> and unusual jobs are usually not popular.
  However, they pay well and may be a good option for people who want to do
  something fun and exciting for work. Here are a <span class="vocab">few</span>
  strange and unusual jobs.
</p>

<p>
  A tea sampler is a person who <span class="vocab">drinks</span> tea. Tea
  samplers have very good <span class="vocab">tongues</span>. <span class="vocab">They</span>
  must know all the different <span class="vocab">types</span> of teas from around
  the world. It can take years to train for this job. This is not an office job,
  as tea samplers travel around the world throughout the year.
</p>

<p>
  Another unusual but well-paying job is a professional
  <span class="vocab">line</span> stander. For this job, a person
  <span class="vocab">stands</span> in line for another person. Professional line
  standers are usually <span class="vocab">very</span> busy during big sales such
  as Black Friday or the day a new smartphone comes out. During these sales, line
  standers can earn quite a lot of money. For example, one professional line
  stander <span class="vocab">waited</span> in line for an iPhone 5 for 100 hours
  and earned $1,500.
</p>

<p>
  <span class="vocab">Pet</span> food <span class="vocab">companies</span> hire
  pet food tasters to <span class="vocab">test</span> the taste and quality of
  their <span class="vocab">products</span>. Pet food tasters normally taste dog
  food or cat food. After tasting the food, they usually spit it out. They need
  to know which products <span class="vocab">sell</span> the best, so they read
  and write many reports about pet food quality.
</p>

<p>
  Another unusual job is a golf <span class="vocab">ball</span> diver. Golf ball
  divers are <span class="vocab">responsible</span> for collecting golf balls that
  people have hit into ponds. This job is not as easy as it sounds. The divers
  wear wetsuits to dive to the <span class="vocab">bottom</span> of a pond, which
  is usually very dirty and dark. This job can also be dangerous, because
  sometimes there are <span class="vocab">snakes</span> in the ponds. There have
  also been cases of divers being bitten by alligators.
</p>

<p>
  If you're looking for a job out of the ordinary, figure out what your interest
  is and consider a strange or unusual job. You may have to
  <span class="vocab">wait</span> for one, but it will be worth it!
</p>
"""

QUESTIONS_19 = [
    {
        "q": "What is this reading about?",
        "opts": [
            "How to turn your passion into your job.",
            "Jobs that are out of the ordinary.",
            "How to get an interesting job.",
            "Dangerous and difficult jobs.",
        ],
        "ans": 1,
    },
    {
        "q": "What must a tea sampler know?",
        "opts": [
            "How to make the best tea.",
            "The way tea is best made.",
            "How to travel around the world.",
            "All the different types of teas.",
        ],
        "ans": 3,
    },
    {
        "q": "When are professional line standers busiest?",
        "opts": [
            "During big sales.",
            "During sports games.",
            "During summer vacation.",
            "During a movie release.",
        ],
        "ans": 0,
    },
    {
        "q": "Which of the following is true about pet food tasters?",
        "opts": [
            "Pet food tasters must eat and swallow the pet food.",
            "Pet food tasters test the shape and quality of the food.",
            "Pet food tasters do not care about the popularity of the pet food.",
            "Pet food tasters write a lot of reports about pet food quality.",
        ],
        "ans": 3,
    },
    {
        "q": "Why can being a golf ball diver be dangerous?",
        "opts": [
            "Because the ponds are very cold.",
            "Because the golf balls are very heavy.",
            "Because there may be snakes or alligators in the ponds.",
            "Because the water is too deep to dive into.",
        ],
        "ans": 2,
    },
    {
        "q": "How much did one professional line stander earn for 100 hours of waiting?",
        "opts": [
            "$500.",
            "$1,000.",
            "$1,500.",
            "$5,000.",
        ],
        "ans": 2,
    },
    {
        "q": "What do pet food tasters usually do after tasting the food?",
        "opts": [
            "They eat all of it to test the quality.",
            "They spit it out.",
            "They sell the best product.",
            "They drink tea to clean their tongues.",
        ],
        "ans": 1,
    },
    {
        "q": "What do tea samplers need to travel the world for?",
        "opts": [
            "To drink tea with company bosses.",
            "To sell different types of tea products.",
            "To train other line standers.",
            "To sample teas from around the world.",
        ],
        "ans": 3,
    },
    {
        "q": "What do golf ball divers wear to do their job?",
        "opts": [
            "Formal uniforms.",
            "Wetsuits.",
            "Strange costumes.",
            "Pet food taster gloves.",
        ],
        "ans": 1,
    },
    {
        "q": "What is the writer's advice at the end of the passage?",
        "opts": [
            "Stick to popular jobs so you can earn more money.",
            "Test pet food products to find the best ones.",
            "Find your interest and consider a strange or unusual job.",
            "Wait until a normal job becomes available.",
        ],
        "ans": 2,
    },
]


# ── UNIT 20 ────────────────────────────────────────────────────────────────────

WORDS_20 = [
    (1,  "Accomplish",   "🏆", "verb",
     "To accomplish something means to finish it successfully.",
     "He accomplished his goal of running ten miles.",
     "ينجز / يحقق",
     ["accomplishes", "accomplished", "accomplishment (n)"]),

    (2,  "Approve",      "👍", "verb",
     "To approve of something means you like or agree with it.",
     "Her co-workers approved her new plan.",
     "يوافق / يقبل",
     ["approves", "approved", "approval (n)", "disapprove (opp)"]),

    (3,  "Approximate",  "≈", "adjective",
     "Approximate means close to an exact amount, number, or time.",
     "My approximate height is two meters.",
     "تقريبي",
     ["approximately (adv)", "approximation (n)"]),

    (4,  "Barrier",      "🚧", "noun",
     "A barrier is something that blocks a path or way.",
     "The Great Wall was a barrier between China and its enemies.",
     "حاجز / عائق",
     ["barriers (pl)"]),

    (5,  "Detect",       "🔍", "verb",
     "To detect is to notice or find something.",
     "The boy ran to the kitchen when he detected the smell of cookies.",
     "يكتشف / يلاحظ",
     ["detects", "detected", "detection (n)", "detective (n)"]),

    (6,  "Duty",         "📋", "noun",
     "A duty is a task that someone has to do.",
     "It is parents' duty to take care of their children.",
     "واجب",
     ["duties (pl)"]),

    (7,  "Elementary",   "🔤", "adjective",
     "An elementary thing is the first or most simple thing.",
     "Children go to elementary school before high school.",
     "ابتدائي / أولي",
     ["elementarily (adv)"]),

    (8,  "Failure",      "❌", "noun",
     "A failure happens when something is not done right.",
     "My cooking ended in failure because I burned the food.",
     "فشل",
     ["failures (pl)", "fail (v)", "failed (adj)"]),

    (9,  "Gradual",      "📈", "adjective",
     "Something gradual happens or develops slowly over time.",
     "Children learn to read at a gradual pace. They do not learn right away.",
     "تدريجي",
     ["gradually (adv)"]),

    (10, "Immigrant",    "✈️", "noun",
     "An immigrant is a person who moves to a different country.",
     "My parents were immigrants. They came from Poland.",
     "مهاجر",
     ["immigrants (pl)", "immigrate (v)", "immigration (n)"]),

    (11, "Insert",       "📥", "verb",
     "To insert something means to put it in something else.",
     "He inserted an extra sentence into the story.",
     "يدرج / يُدخل",
     ["inserts", "inserted", "insertion (n)"]),

    (12, "Instant",      "⚡", "noun",
     "An instant is a very short amount of time.",
     "A microwave oven cooks food in an instant.",
     "لحظة / فوري",
     ["instantly (adv)", "instantaneous (adj)"]),

    (13, "Poverty",      "💔", "noun",
     "Poverty is the state of being poor.",
     "Poverty is a problem in many countries around the world.",
     "فقر",
     ["poor (adj)", "impoverished (adj)"]),

    (14, "Pretend",      "🎭", "verb",
     "To pretend means to make believe something is real.",
     "The boy liked to pretend he was a king.",
     "يتظاهر / يتصنع",
     ["pretends", "pretended", "pretense (n)"]),

    (15, "Rank",         "🎖️", "noun",
     "A rank is a person's place in an order or group.",
     "The man got to the rank of captain in the navy.",
     "رتبة / مرتبة",
     ["ranks (pl)", "rank (v)"]),

    (16, "Recognition",  "🏅", "noun",
     "Recognition is the act of getting praise from other people.",
     "The hero got recognition for his brave deed.",
     "اعتراف / تقدير",
     ["recognize (v)", "recognized (adj)"]),

    (17, "Refrigerate",  "❄️", "verb",
     "To refrigerate something means to make it cold.",
     "Supermarkets refrigerate fruit to make it last long.",
     "يبرد / يضع في الثلاجة",
     ["refrigerates", "refrigerated", "refrigerator (n)"]),

    (18, "Rent",         "🏠", "noun",
     "Rent is the money people pay to live in a certain place.",
     "To live in this house, I have to pay rent at the start of each month.",
     "إيجار",
     ["rents (pl)", "rent (v)", "renter (n)"]),

    (19, "Retire",       "🌅", "verb",
     "To retire is to leave a job, usually because of old age.",
     "My father is sixty-five years old. He is about to retire from work.",
     "يتقاعد",
     ["retires", "retired", "retirement (n)"]),

    (20, "Statistic",    "📊", "noun",
     "A statistic is a number that tells a fact about something.",
     "The statistics showed that we did just as well this year as last year.",
     "إحصاء / إحصائية",
     ["statistics (pl)", "statistical (adj)"]),
]

STORY_HTML_20 = """
<p>
  My name is Albert Einstein. Many people know about the great things I've
  <span class="vocab">accomplished</span>. But I had many
  <span class="vocab">barriers</span> to get through before I became famous.
</p>

<p>
  I was born in Germany. When I was in <span class="vocab">elementary</span>
  school, I already knew about math and <span class="vocab">statistics</span>.
  When I was a boy, I <span class="vocab">pretended</span> to be a great
  scientist. I loved school, but my life at home was hard. My father lost his
  job, so my family lived in <span class="vocab">poverty</span>. We could not
  pay the <span class="vocab">rent</span> in Germany. We became
  <span class="vocab">immigrants</span> and went to Italy. I finished high school
  and went to college in Switzerland.
</p>

<p>
  After college, I began writing about science. I did not reach success in an
  <span class="vocab">instant</span>, though. At first, other scientists did not
  <span class="vocab">approve</span> of my work. They thought I was a
  <span class="vocab">failure</span>. Rising to the <span class="vocab">rank</span>
  of an admired scientist was a <span class="vocab">gradual</span> process. Soon,
  people started to notice that I was right. At last, I began to get some
  <span class="vocab">recognition</span>.
</p>

<p>
  I showed how to find the <span class="vocab">approximate</span> size of very
  big things, like stars. I also <span class="vocab">detected</span> and
  explained the motion of very small things, like atoms. And for fun, I made a
  machine that could <span class="vocab">refrigerate</span> food by
  <span class="vocab">inserting</span> heat. I never <span class="vocab">retired</span>.
  I felt it was my <span class="vocab">duty</span> to keep working.
</p>
"""

QUESTIONS_20 = [
    {
        "q": "What is this story about?",
        "opts": [
            "How Einstein got instant recognition.",
            "Why Einstein was a failure at first.",
            "How Einstein got past barriers to accomplish many great things.",
            "Why Einstein pretended to be sick in elementary school.",
        ],
        "ans": 2,
    },
    {
        "q": "Why did Einstein's family become immigrants?",
        "opts": [
            "They were unhappy about new developments in math and statistics.",
            "They couldn't pay their rent in Germany and had to leave.",
            "His parents didn't want him to stay in school.",
            "They wanted Einstein to go to college in Switzerland.",
        ],
        "ans": 1,
    },
    {
        "q": "Why was Einstein's rise in the ranks of scientists gradual?",
        "opts": [
            "Einstein did not write down his ideas.",
            "Einstein's ideas could not be proven.",
            "Other scientists already knew about his ideas.",
            "Other scientists didn't approve of his ideas at first.",
        ],
        "ans": 3,
    },
    {
        "q": "According to the passage, all the following are true about Einstein EXCEPT ______.",
        "opts": [
            "He found the approximate size of stars.",
            "He refrigerated food by inserting heat.",
            "He had a duty to retire.",
            "He detected the motion of atoms.",
        ],
        "ans": 2,
    },
    {
        "q": "Where did Einstein and his family go after leaving Germany?",
        "opts": [
            "To Switzerland.",
            "To France.",
            "To Italy.",
            "To Poland.",
        ],
        "ans": 2,
    },
    {
        "q": "What does the story say about Einstein's early school days?",
        "opts": [
            "He was a failure at math and statistics.",
            "He pretended to love science but hated it.",
            "He already knew about math and statistics in elementary school.",
            "He did not approve of going to school.",
        ],
        "ans": 2,
    },
    {
        "q": "How did other scientists treat Einstein's work at first?",
        "opts": [
            "They approved of it immediately.",
            "They thought he was a failure.",
            "They gave him instant recognition.",
            "They asked him to retire.",
        ],
        "ans": 1,
    },
    {
        "q": "Which of the following did Einstein accomplish?",
        "opts": [
            "He found the approximate size of stars.",
            "He became an elementary school teacher.",
            "He built a barrier between countries.",
            "He detected that immigrants were gradual.",
        ],
        "ans": 0,
    },
    {
        "q": "What unusual invention did Einstein make for fun?",
        "opts": [
            "A machine to detect stars.",
            "A machine to approximate statistics.",
            "A machine to refrigerate food using heat.",
            "A machine to insert atoms into barriers.",
        ],
        "ans": 2,
    },
    {
        "q": "What does the story tell us about Einstein's character?",
        "opts": [
            "He gave up when others did not approve of his work.",
            "He retired early and stopped doing science.",
            "He was determined and felt it was his duty to keep working.",
            "He pretended to be a scientist but was not one.",
        ],
        "ans": 2,
    },
]


# ── Run all units ──────────────────────────────────────────────────────────────

seed_unit(16, WORDS_16, "Adams County's Gold",      STORY_HTML_16, QUESTIONS_16)
seed_unit(17, WORDS_17, "Henry Ford's Famous Car",  STORY_HTML_17, QUESTIONS_17)
seed_unit(19, WORDS_19, "Strange and Unusual Jobs", STORY_HTML_19, QUESTIONS_19)
seed_unit(20, WORDS_20, "Albert Einstein",          STORY_HTML_20, QUESTIONS_20)

db.commit()
print("Done — Units 16, 17, 19, and 20 seeded successfully.")
db.close()
