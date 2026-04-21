"""
seed_book2_units6_8.py
Seeds Book 2 (A2) Units 6, 7, and 8 with vocabulary, stories, and comprehension questions.

Run: python tools/seed_book2_units6_8.py
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
        print(f"  Unit {unit_number}: updated story '{story_title}'")
    else:
        db.add(UnitStory(
            unit_id=unit.id,
            story_title=story_title,
            story_html=story_html,
            story_questions=questions,
        ))
        print(f"  Unit {unit_number}: created story '{story_title}'")

    print(f"  Unit {unit_number}: {len(words_data)} words, {len(questions)} questions.")


# ── UNIT 6 ────────────────────────────────────────────────────────────────────

UNIT6_WORDS = [
    (1,  "also",          "➕", "adverb",
     "Also means in addition or too.",
     "I like blue, and I also like yellow.",
     "أيضاً",
     ["also (no derivatives — function word)"]),

    (2,  "automatically", "⚙️", "adverb",
     "If an action happens automatically, it happens without thinking or planning.",
     "The man automatically smiled when he thought about his friend.",
     "تلقائياً",
     ["automatic (adj)", "automate (v)", "automation (n)"]),

    (3,  "busy",          "📋", "adjective",
     "A busy person has a lot of things to do.",
     "Everyone is busy at the office today.",
     "مشغول",
     ["busily (adv)", "business (n)", "busier (comp)", "busiest (sup)"]),

    (4,  "can",           "💪", "auxiliary verb",
     "Can shows that a person or thing has the ability to do an action.",
     "Sad news can make her cry.",
     "يستطيع / قادر على",
     ["could (past)"]),

    (5,  "clear",         "🧹", "verb",
     "To clear is to remove everything from a place.",
     "I need to clear my desk because it is too messy.",
     "يُرتّب / يُخلي",
     ["clears", "cleared", "clearly (adv)", "clear (adj)", "clarity (n)"]),

    (6,  "close",         "🚪", "verb",
     "To close is to shut something or cover up an opening.",
     "The man wanted to close the door tightly.",
     "يُغلق",
     ["closes", "closed", "closure (n)"]),

    (7,  "discuss",       "💬", "verb",
     "To discuss is to talk about something with another person.",
     "James began to discuss his report with his teacher.",
     "يناقش",
     ["discusses", "discussed", "discussion (n)"]),

    (8,  "feel",          "❤️", "verb",
     "To feel is to experience an emotion or feeling.",
     "The girl must feel happy because it is her birthday today.",
     "يشعر",
     ["feels", "felt (past)", "feeling (n)"]),

    (9,  "listen",        "👂", "verb",
     "To listen is to pay attention to a sound that you can hear.",
     "She wanted to listen carefully to her friend.",
     "يستمع",
     ["listens", "listened", "listener (n)"]),

    (10, "meet",          "🤝", "verb",
     "To meet is to come together so that you can talk or do something together.",
     "Ken's mother wanted to meet his teacher today.",
     "يلتقي",
     ["meets", "met (past)", "meeting (n)"]),

    (11, "music",         "🎵", "noun",
     "Music is the sound made by singing or playing musical instruments.",
     "The boy makes music by playing a guitar.",
     "موسيقى",
     ["musical (adj)", "musician (n)"]),

    (12, "normal",        "✅", "adjective",
     "A normal thing is usual and not strange.",
     "It is normal to wear school uniforms in private schools.",
     "طبيعي / عادي",
     ["normally (adv)", "abnormal (opp)"]),

    (13, "quiet",         "🤫", "adjective",
     "If something is quiet, it does not make much sound.",
     "The man told the children to be quiet.",
     "هادئ / صامت",
     ["quietly (adv)", "quietness (n)", "loud (opp)"]),

    (14, "relax",         "😌", "verb",
     "To relax is to rest or do something enjoyable.",
     "Nicole likes to relax by reading books.",
     "يرتاح / يسترخي",
     ["relaxes", "relaxed", "relaxing (adj)", "relaxation (n)"]),

    (15, "sleep",         "😴", "verb",
     "To sleep is to rest your mind and body, usually at night in bed.",
     "The child goes to sleep in her bedroom at night.",
     "ينام",
     ["sleeps", "slept (past)", "sleep (n)", "sleepy (adj)"]),

    (16, "stress",        "😰", "noun",
     "Stress is a strong feeling of worry caused by problems in life, work, etc.",
     "Dan has a lot of stress at work.",
     "ضغط / توتر",
     ["stresses (pl)", "stressed (adj)", "stressful (adj)", "stress (v)"]),

    (17, "study",         "📚", "verb",
     "To study is to learn something by reading, memorizing, or going to school.",
     "Karen needed a quiet place to study for a big test.",
     "يدرس",
     ["studies", "studied", "study (n)", "student (n)"]),

    (18, "talk",          "🗣️", "verb",
     "To talk is to say words to express your thoughts, opinions, etc.",
     "They went somewhere to talk to each other.",
     "يتحدث",
     ["talks", "talked", "talk (n)", "talkative (adj)"]),

    (19, "work",          "💼", "verb",
     "To work is to do a job that you get paid for.",
     "They need to work together to finish an important project.",
     "يعمل",
     ["works", "worked", "work (n)", "worker (n)"]),

    (20, "write",         "✍️", "verb",
     "To write is to use a pen or keyboard to make letters and words on paper or a screen.",
     "I need to write a story for my homework.",
     "يكتب",
     ["writes", "wrote (past)", "written (pp)", "writer (n)", "writing (n)"]),
]

UNIT6_STORY_HTML = """
<p>
  Everyone experiences <span class="vocab">stress</span>.
  Stress is a <span class="vocab">normal</span> part of life, but too much stress
  <span class="vocab">can</span> create health problems. People who are stressed
  can suffer from headaches, depression, and even heart problems. Whether you are
  <span class="vocab">busy</span> <span class="vocab">studying</span> or
  <span class="vocab">working</span>, you need to make sure you have time to
  <span class="vocab">relax</span>.
</p>

<p>
  One of the best ways to relax and reduce stress is to meditate. First, find a
  <span class="vocab">quiet</span> place and sit up straight. Then,
  <span class="vocab">close</span> your eyes,
  <span class="vocab">clear</span> your mind, and pay attention to your breathing.
  This practice will make you <span class="vocab">feel</span> relaxed and happier.
  It will <span class="vocab">also</span> help you
  <span class="vocab">sleep</span> better at night. Studies show that sleep is very
  important because that is when your body repairs itself. In addition, being tired
  can make your stress worse.
</p>

<p>
  Another way to relax is to <span class="vocab">listen</span> to
  <span class="vocab">music</span>. Music is a very powerful tool.
  Listening to slow and quiet music can relax your mind. Listening to fast, lively
  music can make you feel happy, which will then help you relax and reduce your stress.
  Some people find that singing along to songs helps take their minds off whatever is
  giving them stress.
</p>

<p>
  If your stress is worrying you, it is best to
  <span class="vocab">meet</span> with a friend and
  <span class="vocab">talk</span> it out. When you
  <span class="vocab">discuss</span> your feelings and problems with someone, you will
  <span class="vocab">automatically</span> feel better. At times when you don't feel
  like talking, you can <span class="vocab">write</span> instead. Many people find it
  helpful to keep a journal and record their feelings.
</p>

<p>
  Remember that stress is a part of life and that you cannot completely get rid of it.
  That being said, you need to reduce stress as much as you can. Make time for yourself
  and try the above suggestions in order to feel relaxed and stay happy and healthy.
</p>
"""

UNIT6_QUESTIONS = [
    {
        "q": "What is this reading about?",
        "opts": [
            "How stress is unhealthy.",
            "How to relax and reduce stress.",
            "How stress is good for people.",
            "How to get more stress.",
        ],
        "ans": 1,
    },
    {
        "q": "How do people meditate?",
        "opts": [
            "They meet a friend and feel better.",
            "They write down their feelings in a journal.",
            "They listen and sing along to fast, lively music.",
            "They close their eyes and clear their mind in a quiet place.",
        ],
        "ans": 3,
    },
    {
        "q": "What kind of music can make people feel happy?",
        "opts": [
            "Fast and lively.",
            "Sad and quiet.",
            "Slow and relaxing.",
            "Loud and slow.",
        ],
        "ans": 0,
    },
    {
        "q": "Which of the following is true, according to the reading?",
        "opts": [
            "Singing songs makes stress worse.",
            "Sleep is not important.",
            "A little stress is unhealthy.",
            "Stress is a normal part of life.",
        ],
        "ans": 3,
    },
    {
        "q": "According to the reading, what happens when you discuss your problems with someone?",
        "opts": [
            "You will automatically feel better.",
            "You will feel more stressed.",
            "You will sleep better that night.",
            "You will need to write in a journal.",
        ],
        "ans": 0,
    },
    {
        "q": "Why is sleep important, according to the reading?",
        "opts": [
            "It makes stress disappear completely.",
            "It helps you listen to music better.",
            "The body repairs itself during sleep.",
            "It helps you feel busy during the day.",
        ],
        "ans": 2,
    },
    {
        "q": "What does the reading suggest doing when you don't feel like talking?",
        "opts": [
            "Listening to fast music.",
            "Finding a quiet place to sleep.",
            "Writing in a journal.",
            "Going for a walk.",
        ],
        "ans": 2,
    },
    {
        "q": "What can make your stress worse, according to the reading?",
        "opts": [
            "Listening to music.",
            "Being tired.",
            "Meeting with a friend.",
            "Closing your eyes.",
        ],
        "ans": 1,
    },
    {
        "q": "What is one benefit of singing along to songs?",
        "opts": [
            "It helps you study better.",
            "It makes you feel quiet.",
            "It helps you sleep faster.",
            "It takes your mind off things that give you stress.",
        ],
        "ans": 3,
    },
    {
        "q": "What is the writer's main message?",
        "opts": [
            "Stress can never be reduced.",
            "Music is the only way to reduce stress.",
            "You should reduce stress as much as you can and make time for yourself.",
            "Working hard is the best way to feel relaxed.",
        ],
        "ans": 2,
    },
]


# ── UNIT 7 ────────────────────────────────────────────────────────────────────

UNIT7_WORDS = [
    (1,  "basis",         "🔑", "noun",
     "The basis of something is the main part or amount of it.",
     "My grandfather gets his hearing checked on a yearly basis.",
     "أساس",
     ["bases (pl)", "basic (adj)", "basically (adv)"]),

    (2,  "biology",       "🔬", "noun",
     "Biology is the study of living things.",
     "We learned about the human heart in biology class.",
     "علم الأحياء",
     ["biological (adj)", "biologist (n)"]),

    (3,  "cage",          "🦜", "noun",
     "A cage is something that holds an animal so it cannot leave.",
     "We put the parrots in their cage at night.",
     "قفص",
     ["cages (pl)", "cage (v)"]),

    (4,  "colleague",     "👔", "noun",
     "A colleague is somebody you work with.",
     "My colleague helped me finish the job.",
     "زميل",
     ["colleagues (pl)"]),

    (5,  "colony",        "🏴", "noun",
     "A colony is a country or area controlled by another country.",
     "The USA was at one time a colony of Great Britain.",
     "مستعمرة",
     ["colonies (pl)", "colonial (adj)", "colonize (v)"]),

    (6,  "debate",        "🗣️", "verb",
     "To debate is to seriously discuss something with someone.",
     "The husband and wife debated which TV to buy.",
     "يناقش / يجادل",
     ["debates", "debated", "debate (n)", "debatable (adj)"]),

    (7,  "depart",        "✈️", "verb",
     "To depart is to leave some place so you can go to another place.",
     "The plane departed for Italy at 3:00 this afternoon.",
     "يغادر",
     ["departs", "departed", "departure (n)"]),

    (8,  "depress",       "😔", "verb",
     "To depress someone is to make that person sad.",
     "The bad news from work depressed the man.",
     "يُحبط / يُحزن",
     ["depresses", "depressed (adj)", "depression (n)", "depressing (adj)"]),

    (9,  "factual",       "📋", "adjective",
     "A factual report or message includes true details.",
     "John learns about history from factual books.",
     "واقعي / حقيقي",
     ["factually (adv)", "fact (n)"]),

    (10, "fascinate",     "✨", "verb",
     "To fascinate is to make a person very interested.",
     "The kitten was fascinated by the ball of yarn.",
     "يُفتن / يأسر الاهتمام",
     ["fascinates", "fascinated (adj)", "fascinating (adj)", "fascination (n)"]),

    (11, "mission",       "🎯", "noun",
     "A mission is an important job that is sometimes far away.",
     "The woman's mission was to help sick people.",
     "مهمة",
     ["missions (pl)"]),

    (12, "nevertheless",  "🔄", "adverb",
     "Nevertheless shows a difference to what is expected or known.",
     "He is usually friendly. Nevertheless, he wasn't friendly this afternoon.",
     "ومع ذلك / بالرغم من ذلك",
     []),

    (13, "occupation",    "💼", "noun",
     "An occupation is a person's job.",
     "My father's occupation is a dentist.",
     "مهنة / وظيفة",
     ["occupations (pl)", "occupy (v)"]),

    (14, "overseas",      "🌍", "adverb",
     "Overseas means happening in another country, across an ocean.",
     "John often goes overseas for vacations.",
     "في الخارج / خارج البلاد",
     ["overseas (adj)"]),

    (15, "persuade",      "🤝", "verb",
     "To persuade someone is to make that person agree to do something.",
     "The children persuaded their parents to buy them gifts.",
     "يُقنع",
     ["persuades", "persuaded", "persuasion (n)", "persuasive (adj)"]),

    (16, "route",         "🗺️", "noun",
     "A route is the way you go from one place to another.",
     "I saw many new houses along the route to the city.",
     "طريق / مسار",
     ["routes (pl)"]),

    (17, "ruins",         "🏛️", "noun",
     "Ruins are old buildings that are not used anymore.",
     "I liked seeing interesting ruins in Greece.",
     "أطلال / خرائب",
     ["ruin (sing)", "ruin (v)", "ruined (adj)"]),

    (18, "scholar",       "🎓", "noun",
     "A scholar is a person who studies something and knows a lot about it.",
     "The scholar knew much about art history.",
     "عالم / باحث",
     ["scholars (pl)", "scholarly (adj)", "scholarship (n)"]),

    (19, "significant",   "⭐", "adjective",
     "A significant person or thing is important.",
     "I read many significant novels as a literature major in university.",
     "مهم / بالغ الأهمية",
     ["significantly (adv)", "significance (n)", "insignificant (opp)"]),

    (20, "volcano",       "🌋", "noun",
     "A volcano is a mountain with a hole on top where hot liquid comes out.",
     "When the volcano erupted, smoke and heat filled the air.",
     "بركان",
     ["volcanoes (pl)", "volcanic (adj)"]),
]

UNIT7_STORY_HTML = """
<p>
  Dr. Norton's <span class="vocab">occupation</span> was a
  <span class="vocab">scholar</span> of
  <span class="vocab">biology</span>. He learned all about animals on a daily
  <span class="vocab">basis</span>. One day, he met a sailor from a
  <span class="vocab">colony</span>
  <span class="vocab">overseas</span>. The man told Dr. Norton about a talking bird!
  The bird <span class="vocab">fascinated</span> Dr. Norton, so he told his
  <span class="vocab">colleagues</span> about it. They
  <span class="vocab">debated</span> with him: no one thought a bird would be able
  to talk. He tried to <span class="vocab">persuade</span> them, but they laughed
  at him. <span class="vocab">Nevertheless</span>, Dr. Norton believed the bird was
  real. His new <span class="vocab">mission</span> was to find it. He wanted
  <span class="vocab">factual</span> proof.
</p>

<p>
  The next day, he <span class="vocab">departed</span> for the colony. The sailor
  he had met told him to look for a man named Jai, who would be able to help him
  in his search. After a month of sailing, Dr. Norton finally reached the colony,
  where he met Jai.
</p>

<p>
  They left the next day. A week later, they arrived at the
  <span class="vocab">volcano</span>. Every day, they walked around and looked for
  the bird, but they couldn't find it. After one month, Dr. Norton could not find
  the bird, and this <span class="vocab">depressed</span> him. He decided to go home.
  On the <span class="vocab">route</span> back, he walked past some old
  <span class="vocab">ruins</span>. He heard someone say, "Hello."
</p>

<p>
  "Who are you?" he asked. Dr. Norton looked up and saw a bird! Dr. Norton put the
  talking bird into a <span class="vocab">cage</span>. Then, he returned home. He
  had made a <span class="vocab">significant</span> discovery.
</p>
"""

UNIT7_QUESTIONS = [
    {
        "q": "What is this story about?",
        "opts": [
            "A route to a new place.",
            "A scholar who finds a talking bird.",
            "How to learn about biology.",
            "Why people debate each other.",
        ],
        "ans": 1,
    },
    {
        "q": "Why did Dr. Norton go overseas?",
        "opts": [
            "He wanted to depart from his colleagues and start a new life.",
            "He was on a mission to find the talking bird.",
            "He wanted to see the volcano.",
            "He wanted to discover some old ruins.",
        ],
        "ans": 1,
    },
    {
        "q": "At the end of the story, we can infer that ______.",
        "opts": [
            "Jai didn't like Dr. Norton but nevertheless cheered his discovery.",
            "Finding the volcano was also a significant discovery.",
            "The bird would be the factual proof that would persuade his colleagues.",
            "The bird had fascinated people in the colony for a long time.",
        ],
        "ans": 2,
    },
    {
        "q": "According to the passage, all the following are true EXCEPT ______.",
        "opts": [
            "Jai fed bread to the talking bird.",
            "Dr. Norton put the bird into a cage.",
            "Dr. Norton took a ship to the colony.",
            "The talking bird was found near the ruins.",
        ],
        "ans": 0,
    },
    {
        "q": "What depressed Dr. Norton during his search?",
        "opts": [
            "He ran out of money for the journey.",
            "His colleagues refused to help him.",
            "He could not find the talking bird after one month.",
            "Jai refused to guide him to the volcano.",
        ],
        "ans": 2,
    },
    {
        "q": "How did Dr. Norton's colleagues react when he told them about the bird?",
        "opts": [
            "They believed him immediately.",
            "They offered to help him find the bird.",
            "They laughed at him and did not believe him.",
            "They were fascinated and wanted to debate it further.",
        ],
        "ans": 2,
    },
    {
        "q": "Who helped Dr. Norton search for the bird in the colony?",
        "opts": [
            "A sailor from the colony.",
            "His colleague from biology class.",
            "A man named Jai.",
            "A local scholar.",
        ],
        "ans": 2,
    },
    {
        "q": "Where was the talking bird finally found?",
        "opts": [
            "Near the volcano.",
            "By the ruins.",
            "By the ocean.",
            "In a cage at the colony.",
        ],
        "ans": 1,
    },
    {
        "q": "What did Dr. Norton do with the bird after finding it?",
        "opts": [
            "He left it in the ruins.",
            "He gave it to Jai.",
            "He put it in a cage and took it home.",
            "He set it free near the volcano.",
        ],
        "ans": 2,
    },
    {
        "q": "Which word best describes Dr. Norton's character?",
        "opts": [
            "Lazy and uninterested.",
            "Determined and curious.",
            "Rude and impatient.",
            "Shy and nervous.",
        ],
        "ans": 1,
    },
]


# ── UNIT 8 ────────────────────────────────────────────────────────────────────

UNIT8_WORDS = [
    (1,  "broad",         "↔️", "adjective",
     "Broad means that something is wide, not narrow.",
     "The river is very long and broad.",
     "عريض / واسع",
     ["broadly (adv)", "broaden (v)", "breadth (n)"]),

    (2,  "bush",          "🌿", "noun",
     "A bush is a woody plant that is smaller than a tree.",
     "My dad and I planted some small bushes around the house.",
     "شجيرة",
     ["bushes (pl)", "bushy (adj)"]),

    (3,  "capable",       "💪", "adjective",
     "A capable person or thing can do an action.",
     "The Olympic athlete is capable of lifting a lot of weight.",
     "قادر / كفء",
     ["capably (adv)", "capability (n)", "incapable (opp)"]),

    (4,  "cheat",         "🃏", "verb",
     "To cheat is to be dishonest in order to win or do well.",
     "They cheated on the test by sharing answers.",
     "يغش",
     ["cheats", "cheated", "cheat (n)", "cheater (n)"]),

    (5,  "concentrate",   "🧠", "verb",
     "To concentrate is to give one's full attention to something.",
     "I could not concentrate on my homework because the room was so loud.",
     "يركّز",
     ["concentrates", "concentrated", "concentration (n)"]),

    (6,  "conclude",      "🔍", "verb",
     "To conclude is to form an opinion by thinking carefully and looking at evidence.",
     "I saw crumbs on my dog's face, so I concluded that he ate my cookie.",
     "يستنتج",
     ["concludes", "concluded", "conclusion (n)"]),

    (7,  "confident",     "😎", "adjective",
     "Confident people believe that they can do something without failing.",
     "She was confident she could climb the mountain due to her training.",
     "واثق من نفسه",
     ["confidently (adv)", "confidence (n)", "unconfident (opp)"]),

    (8,  "considerable",  "📏", "adjective",
     "Considerable means large in size, amount, or extent.",
     "They paid a considerable amount of money for that car.",
     "كبير / ملحوظ",
     ["considerably (adv)", "consider (v)"]),

    (9,  "convey",        "📨", "verb",
     "To convey is to communicate or make ideas known.",
     "That picture of a crying child conveys a feeling of sadness.",
     "ينقل / يعبّر",
     ["conveys", "conveyed", "conveyance (n)"]),

    (10, "definite",      "✅", "adjective",
     "A definite thing is certain or sure to be true.",
     "There is a definite connection between hard work and success.",
     "محدد / مؤكد",
     ["definitely (adv)", "definition (n)", "indefinite (opp)"]),

    (11, "delight",       "😄", "noun",
     "Delight is a feeling of being very happy with something.",
     "He felt such delight after getting a promotion at work.",
     "بهجة / سرور",
     ["delights (pl)", "delighted (adj)", "delightful (adj)", "delight (v)"]),

    (12, "destination",   "📍", "noun",
     "A destination is the place where someone or something is going.",
     "The destination of this plane is Munich, Germany.",
     "وجهة / مقصد",
     ["destinations (pl)"]),

    (13, "edge",          "🔱", "noun",
     "The edge is the furthest part or side of something.",
     "He ran to the edge of the cliff.",
     "حافة / طرف",
     ["edges (pl)", "edgy (adj)"]),

    (14, "instructions",  "📄", "noun",
     "Instructions tell you how to do something.",
     "Just follow the instructions and you will be OK.",
     "تعليمات",
     ["instruction (sing)", "instruct (v)", "instructor (n)"]),

    (15, "path",          "🛤️", "noun",
     "A path is a way from one place to another that people can walk along.",
     "We followed a path through the woods.",
     "مسار / ممر",
     ["paths (pl)"]),

    (16, "resort",        "🔄", "verb",
     "To resort to something is to depend on it in order to solve a problem.",
     "I hope they don't resort to violence to end the argument.",
     "يلجأ إلى",
     ["resorts", "resorted", "resort (n — holiday resort)"]),

    (17, "shadow",        "🌑", "noun",
     "A shadow is the dark area that is made when something blocks light.",
     "The man's shadow was taller than he was.",
     "ظل / خيال",
     ["shadows (pl)", "shadowy (adj)"]),

    (18, "succeed",       "🏆", "verb",
     "To succeed is to complete something as planned.",
     "He will continue to work on the robot until he succeeds.",
     "ينجح",
     ["succeeds", "succeeded", "success (n)", "successful (adj)", "successfully (adv)"]),

    (19, "suspect",       "🤔", "verb",
     "To suspect something is to believe that it might be true.",
     "I suspect that those kids stole the money.",
     "يشتبه / يظن",
     ["suspects", "suspected", "suspect (n/adj)", "suspicion (n)", "suspicious (adj)"]),

    (20, "valley",        "🏔️", "noun",
     "A valley is a low area of land between two mountains or hills.",
     "We looked at the valley below from the top of the mountain.",
     "وادي",
     ["valleys (pl)"]),
]

UNIT8_STORY_HTML = """
<p>
  Ricky the rabbit and Tera the turtle met by the
  <span class="vocab">edge</span> of the river.
  "No one is <span class="vocab">capable</span> of beating me in a race!" Ricky said.
  He was <span class="vocab">confident</span> — his smile
  <span class="vocab">conveyed</span> that.
</p>

<p>
  "I can beat you," Tera said.
</p>

<p>
  Ricky laughed with <span class="vocab">delight</span>.
</p>

<p>
  Tera said, "We will race tomorrow. The
  <span class="vocab">destination</span> is the hill."
</p>

<p>
  Ricky agreed. Tera <span class="vocab">concentrated</span> on winning the race.
  She was not faster than Ricky. She needed a
  <span class="vocab">definite</span> way to
  <span class="vocab">succeed</span>. She told her family about the race. "I have
  <span class="vocab">concluded</span> that I have to
  <span class="vocab">resort</span> to something bad. I will
  <span class="vocab">cheat</span>." She quietly told her
  <span class="vocab">instructions</span> to them. Her family members all looked
  very similar!
</p>

<p>
  They hid in the <span class="vocab">shadows</span> on the
  <span class="vocab">path</span>. The race began. Tera was soon far behind.
  However, Tera's brother hid behind a
  <span class="vocab">bush</span> in the
  <span class="vocab">valley</span> below. When Ricky got close, Tera's brother
  began to run. He looked just like Tera! Ricky ran as fast as he could along the
  path. But, to him, it seemed like Tera was always ahead. Ricky had used a
  <span class="vocab">considerable</span> amount of energy.
</p>

<p>
  He reached the top, but Tera's sister was already there. "Well, you win," Ricky said.
</p>

<p>
  Later, Tera had a <span class="vocab">broad</span> smile on her face. Ricky never
  <span class="vocab">suspected</span>. He had been cheated by a family of slow turtles.
</p>
"""

UNIT8_QUESTIONS = [
    {
        "q": "What is this story about?",
        "opts": [
            "A confident rabbit.",
            "A rabbit that cheats in a race.",
            "A turtle that rests in shadows.",
            "A turtle with a clever idea and a big family.",
        ],
        "ans": 3,
    },
    {
        "q": "Where was the final destination of the race?",
        "opts": [
            "The edge of the river.",
            "Behind the first bush.",
            "The middle of the valley.",
            "The top of the hill.",
        ],
        "ans": 3,
    },
    {
        "q": "Why was Tera the turtle angry at the start?",
        "opts": [
            "Because Ricky the rabbit said no one was capable of beating him.",
            "Because she thought that the path of the race was too difficult.",
            "Because she knew Ricky would resort to cheating.",
            "Because her family wouldn't gather when she asked them to.",
        ],
        "ans": 0,
    },
    {
        "q": "What did Tera say to her family?",
        "opts": [
            "She concluded that she must concentrate on the race.",
            "She conveyed that Ricky would cheat.",
            "She told them about her definite plan to succeed.",
            "She said the race would take a considerable amount of energy.",
        ],
        "ans": 2,
    },
    {
        "q": "What did Ricky never suspect?",
        "opts": [
            "That Tera had a twin sister.",
            "That the path had shadows.",
            "That he was being cheated by a family of turtles.",
            "That the destination was the top of the hill.",
        ],
        "ans": 2,
    },
    {
        "q": "How did Tera's family help her win the race?",
        "opts": [
            "They blocked Ricky's path at the edge of the river.",
            "Family members hid along the route and ran to make Ricky think Tera was always ahead.",
            "They told Ricky the wrong destination.",
            "They cheered for Tera to make her run faster.",
        ],
        "ans": 1,
    },
    {
        "q": "Why did Tera need a definite plan to succeed?",
        "opts": [
            "Because the path was very long and dangerous.",
            "Because she had never run a race before.",
            "Because she was not faster than Ricky.",
            "Because her family refused to help her.",
        ],
        "ans": 2,
    },
    {
        "q": "What does the story suggest about Ricky at the end?",
        "opts": [
            "He was kind and let Tera win.",
            "He was suspicious of Tera from the start.",
            "He used a considerable amount of energy but was still deceived.",
            "He knew the turtles were cheating but said nothing.",
        ],
        "ans": 2,
    },
    {
        "q": "How did Tera feel at the end of the story?",
        "opts": [
            "She felt considerable guilt about cheating.",
            "She was depressed because Ricky found out.",
            "She had a broad smile and was satisfied.",
            "She concentrated on apologizing to Ricky.",
        ],
        "ans": 2,
    },
    {
        "q": "What is the main message of this story?",
        "opts": [
            "Fast animals always win races.",
            "It is wrong to cheat, even if you win.",
            "Families should not help each other compete.",
            "Confidence is the key to success.",
        ],
        "ans": 1,
    },
]


# ── Run all three ─────────────────────────────────────────────────────────────

print("Seeding Book 2 Units 6, 7, and 8...")
seed_unit(6, UNIT6_WORDS, "Ways to Reduce Stress", UNIT6_STORY_HTML, UNIT6_QUESTIONS)
seed_unit(7, UNIT7_WORDS, "A Beautiful Bird",      UNIT7_STORY_HTML, UNIT7_QUESTIONS)
seed_unit(8, UNIT8_WORDS, "Tricky Turtle",         UNIT8_STORY_HTML, UNIT8_QUESTIONS)

db.commit()
print("Done.")
db.close()
