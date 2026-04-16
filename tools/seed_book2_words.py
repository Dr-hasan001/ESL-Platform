"""
seed_book2_words.py
Inserts vocabulary words for 4000 Essential English Words Book 2 (A2), Units 1-5.
Each unit has 20 target words — definition, example, Arabic translation,
emoji, and derivatives in the same format as index.html (Unit 18).

Run: python tools/seed_book2_words.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.book import Book, Unit, Word

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ── Find Book 2 (A2) ──────────────────────────────────────────────────────────
book = db.query(Book).filter(Book.book_number == 2).first()
if not book:
    print("ERROR: Book 2 not found. Run tools/seed_db.py first.")
    db.close()
    sys.exit(1)

# ── Vocabulary data: Units 1-5 ────────────────────────────────────────────────
# Format per word:
#   (position, word, emoji, part_of_speech, definition, example,
#    arabic_translation, [derivatives])

UNITS = {
    1: {
        "words": [
            (1,  "Achieve",     "🥇", "verb",
             "To achieve means to successfully reach a goal after effort.",
             "She studied every day and achieved the highest score in the class.",
             "يحقق / ينجز",
             ["achieves", "achieved", "achievement (n)", "achievable (adj)"]),

            (2,  "Accurate",    "🎯", "adjective",
             "Something accurate is exactly correct and without any mistakes.",
             "The weather report was accurate — it rained in the afternoon.",
             "دقيق / صحيح",
             ["accurately (adv)", "accuracy (n)", "inaccurate (opp)"]),

            (3,  "Adult",       "🧑", "noun",
             "An adult is a person who is fully grown and no longer a child.",
             "Children must be accompanied by an adult in this area.",
             "بالغ / راشد",
             ["adults (pl)", "adulthood (n)"]),

            (4,  "Affect",      "🌊", "verb",
             "To affect something means to produce a change in it.",
             "Lack of sleep can seriously affect your ability to study.",
             "يؤثر على",
             ["affects", "affected", "effect (n)"]),

            (5,  "Afford",      "💳", "verb",
             "To afford something means to have enough money to pay for it.",
             "He worked two jobs so he could afford to buy a new car.",
             "يتحمل تكلفة / يستطيع شراء",
             ["affords", "afforded", "affordable (adj)"]),

            (6,  "Amount",      "🔢", "noun",
             "An amount is a quantity of something.",
             "A large amount of rain fell last night.",
             "كمية / مقدار",
             ["amounts (pl)", "amount (v)"]),

            (7,  "Appear",      "👀", "verb",
             "To appear means to start to be seen or to seem to be something.",
             "A rainbow appeared in the sky after the rain.",
             "يظهر / يبدو",
             ["appears", "appeared", "appearance (n)", "disappear (opp)"]),

            (8,  "Appreciate",  "🌟", "verb",
             "To appreciate something means to be grateful for it and recognise its value.",
             "I really appreciate your help with my homework.",
             "يقدّر / يشكر",
             ["appreciates", "appreciated", "appreciation (n)"]),

            (9,  "Arrange",     "📅", "verb",
             "To arrange means to plan and organise something in advance.",
             "She arranged a meeting with the manager for Friday morning.",
             "يرتّب / ينظّم",
             ["arranges", "arranged", "arrangement (n)"]),

            (10, "Attempt",     "🏋️", "verb",
             "To attempt means to try to do something, especially something difficult.",
             "He attempted to climb the mountain but turned back because of the snow.",
             "يحاول",
             ["attempts", "attempted", "attempt (n)"]),

            (11, "Attend",      "🏫", "verb",
             "To attend an event means to go and be present at it.",
             "All students are expected to attend every lesson.",
             "يحضر / يشارك",
             ["attends", "attended", "attendance (n)"]),

            (12, "Attitude",    "😤", "noun",
             "Your attitude is the way you think and feel about something.",
             "He has a positive attitude towards learning new things.",
             "موقف / طريقة تفكير",
             ["attitudes (pl)"]),

            (13, "Aware",       "🧠", "adjective",
             "If you are aware of something, you know about it or notice it.",
             "Are you aware that the library closes at six today?",
             "مدرك / واعٍ",
             ["awareness (n)", "unaware (opp)"]),

            (14, "Behave",      "🌿", "verb",
             "To behave means to act in a certain way towards others.",
             "The children behaved well during the school trip.",
             "يتصرف / يسلك",
             ["behaves", "behaved", "behaviour (n)"]),

            (15, "Belief",      "💭", "noun",
             "A belief is a strong feeling that something is true or real.",
             "It is his belief that everyone deserves a second chance.",
             "معتقد / إيمان",
             ["beliefs (pl)", "believe (v)", "believer (n)"]),

            (16, "Belong",      "🏡", "verb",
             "To belong to someone or somewhere means to be a part of or owned by them.",
             "This book belongs to the school library.",
             "ينتمي إلى / يخص",
             ["belongs", "belonged", "belonging (n)"]),

            (17, "Career",      "💼", "noun",
             "A career is the series of jobs that someone has during their working life.",
             "She chose a career in medicine because she wanted to help people.",
             "مسيرة مهنية / حياة وظيفية",
             ["careers (pl)"]),

            (18, "Certain",     "✅", "adjective",
             "If you are certain about something, you are completely sure it is true.",
             "Are you certain that you locked the door before leaving?",
             "متأكد / يقيني",
             ["certainly (adv)", "certainty (n)", "uncertain (opp)"]),

            (19, "Challenge",   "⚡", "noun",
             "A challenge is something difficult that requires effort and skill.",
             "Learning a new language is a challenge, but it is very rewarding.",
             "تحدٍّ / صعوبة",
             ["challenges (pl)", "challenge (v)", "challenging (adj)"]),

            (20, "Character",   "🎭", "noun",
             "A character is the combination of qualities that makes a person who they are.",
             "She is known for her honest and caring character.",
             "شخصية / طابع",
             ["characters (pl)", "characteristic (adj/n)"]),
        ],
    },

    2: {
        "words": [
            (1,  "Choice",      "🔀", "noun",
             "A choice is the decision you make when you select one thing from several.",
             "You have a choice between the chicken and the fish.",
             "خيار / اختيار",
             ["choices (pl)", "choose (v)", "choose (v)"]),

            (2,  "Claim",       "🗣️", "verb",
             "To claim means to say that something is true, even if it has not been proved.",
             "He claimed that he had never seen the stolen money.",
             "يدّعي / يزعم",
             ["claims", "claimed", "claim (n)"]),

            (3,  "Collect",     "🗃️", "verb",
             "To collect means to gather things together over a period of time.",
             "She collects old coins from different countries.",
             "يجمع / يحصّل",
             ["collects", "collected", "collection (n)", "collector (n)"]),

            (4,  "Combine",     "🧩", "verb",
             "To combine means to join two or more things together to make one thing.",
             "Combine the eggs and flour to make the dough.",
             "يجمع / يدمج",
             ["combines", "combined", "combination (n)"]),

            (5,  "Compare",     "⚖️", "verb",
             "To compare means to look at two or more things to see how they are similar or different.",
             "The teacher asked us to compare life in the city with life in the countryside.",
             "يقارن",
             ["compares", "compared", "comparison (n)", "comparative (adj)"]),

            (6,  "Compete",     "🏆", "verb",
             "To compete means to try to win something against others.",
             "Athletes from fifty countries competed in the games.",
             "يتنافس",
             ["competes", "competed", "competition (n)", "competitive (adj)"]),

            (7,  "Concern",     "😟", "noun",
             "A concern is a feeling of worry about something important.",
             "She expressed concern about the rise in traffic accidents.",
             "قلق / اهتمام",
             ["concerns (pl)", "concern (v)", "concerned (adj)"]),

            (8,  "Consider",    "🤔", "verb",
             "To consider means to think carefully about something before deciding.",
             "Please consider all your options before making a final decision.",
             "يفكّر في / يأخذ بعين الاعتبار",
             ["considers", "considered", "consideration (n)"]),

            (9,  "Contain",     "📦", "verb",
             "To contain means to have something inside.",
             "This bottle contains one litre of water.",
             "يحتوي على",
             ["contains", "contained", "container (n)"]),

            (10, "Continue",    "▶️", "verb",
             "To continue means to keep doing something without stopping.",
             "Despite the rain, they continued to walk.",
             "يستمر / يواصل",
             ["continues", "continued", "continuation (n)"]),

            (11, "Contrast",    "🔲", "noun",
             "A contrast is a clear difference between two things.",
             "There is a strong contrast between the hot days and cold nights in the desert.",
             "تناقض / فرق واضح",
             ["contrasts (pl)", "contrast (v)", "contrasting (adj)"]),

            (12, "Create",      "🎨", "verb",
             "To create means to make something new that did not exist before.",
             "The artist created a beautiful painting from simple colours.",
             "يبتكر / يصنع",
             ["creates", "created", "creation (n)", "creative (adj)"]),

            (13, "Decision",    "📌", "noun",
             "A decision is a choice you make after thinking about something.",
             "She made the difficult decision to leave her job.",
             "قرار",
             ["decisions (pl)", "decide (v)", "decisive (adj)"]),

            (14, "Decline",     "📉", "verb",
             "To decline means to become smaller, weaker, or worse over time.",
             "The number of students studying science has declined in recent years.",
             "ينخفض / يتراجع",
             ["declines", "declined", "decline (n)"]),

            (15, "Define",      "📖", "verb",
             "To define means to explain the exact meaning of a word or idea.",
             "Can you define the word 'sustainable' in your own words?",
             "يعرّف / يحدد",
             ["defines", "defined", "definition (n)"]),

            (16, "Describe",    "📝", "verb",
             "To describe means to say what something or someone is like.",
             "Can you describe what the thief looked like?",
             "يصف",
             ["describes", "described", "description (n)"]),

            (17, "Design",      "📐", "verb",
             "To design means to plan how something will look or how it will work.",
             "An architect designed the new school building.",
             "يصمّم",
             ["designs", "designed", "design (n)", "designer (n)"]),

            (18, "Develop",     "🌱", "verb",
             "To develop means to grow or change into something bigger or better over time.",
             "The town developed quickly after the new factory opened.",
             "يطوّر / ينمو",
             ["develops", "developed", "development (n)"]),

            (19, "Differ",      "🔄", "verb",
             "To differ means to be unlike or different from something else.",
             "People differ in the way they learn best.",
             "يختلف",
             ["differs", "differed", "difference (n)", "different (adj)"]),

            (20, "Discuss",     "💬", "verb",
             "To discuss means to talk about something with other people.",
             "The class discussed the advantages and disadvantages of social media.",
             "يناقش",
             ["discusses", "discussed", "discussion (n)"]),
        ],
    },

    3: {
        "words": [
            (1,  "Display",     "🖼️", "verb",
             "To display something means to put it somewhere so that people can see it.",
             "The museum displayed ancient Roman artefacts.",
             "يعرض / يُظهر",
             ["displays", "displayed", "display (n)"]),

            (2,  "Enable",      "🔓", "verb",
             "To enable means to make it possible for someone to do something.",
             "A good education enables people to get better jobs.",
             "يُمكّن / يتيح",
             ["enables", "enabled", "unable (opp)"]),

            (3,  "Encourage",   "📣", "verb",
             "To encourage means to give someone the confidence and support to do something.",
             "His teacher encouraged him to enter the writing competition.",
             "يشجّع",
             ["encourages", "encouraged", "encouragement (n)", "discourage (opp)"]),

            (4,  "Ensure",      "🔒", "verb",
             "To ensure means to make certain that something will happen.",
             "Please double-check your work to ensure there are no mistakes.",
             "يضمن / يكفل",
             ["ensures", "ensured"]),

            (5,  "Establish",   "🏗️", "verb",
             "To establish means to create or set up something that will last a long time.",
             "The charity was established in 1995 to help homeless children.",
             "يؤسس / يُنشئ",
             ["establishes", "established", "establishment (n)"]),

            (6,  "Examine",     "🔬", "verb",
             "To examine means to look at something carefully to understand it.",
             "The doctor examined the patient and found nothing seriously wrong.",
             "يفحص / يدرس",
             ["examines", "examined", "examination (n)"]),

            (7,  "Exist",       "🌐", "verb",
             "To exist means to be real and present in the world.",
             "Did dinosaurs really exist, or are they just stories?",
             "يوجد / يعيش",
             ["exists", "existed", "existence (n)"]),

            (8,  "Experience",  "📚", "noun",
             "Experience is the knowledge or skill you get from doing something.",
             "She has three years of experience working in a hospital.",
             "خبرة / تجربة",
             ["experiences (pl)", "experience (v)", "experienced (adj)"]),

            (9,  "Explain",     "💡", "verb",
             "To explain means to make something clear so that it is easier to understand.",
             "The teacher explained the grammar rule very clearly.",
             "يشرح / يوضّح",
             ["explains", "explained", "explanation (n)"]),

            (10, "Express",     "😊", "verb",
             "To express means to show your thoughts or feelings through words or actions.",
             "He expressed his gratitude by writing a letter.",
             "يُعبّر عن",
             ["expresses", "expressed", "expression (n)"]),

            (11, "Focus",       "🔭", "verb",
             "To focus means to give all your attention to one particular thing.",
             "Try to focus on one task at a time instead of doing many things at once.",
             "يركّز على",
             ["focuses", "focused", "focus (n)"]),

            (12, "Function",    "⚙️", "noun",
             "A function is the purpose or job that something is meant to do.",
             "The function of the heart is to pump blood around the body.",
             "وظيفة / دور",
             ["functions (pl)", "function (v)", "functional (adj)"]),

            (13, "Generate",    "⚡", "verb",
             "To generate means to produce or create something.",
             "Wind turbines generate electricity without polluting the air.",
             "يُولّد / ينتج",
             ["generates", "generated", "generation (n)"]),

            (14, "Identify",    "🔎", "verb",
             "To identify means to recognise who someone is or what something is.",
             "Scientists have identified a new type of bacteria.",
             "يحدّد / يتعرف على",
             ["identifies", "identified", "identification (n)"]),

            (15, "Imagine",     "🌈", "verb",
             "To imagine means to form a picture or idea of something in your mind.",
             "Imagine living in a world without phones or computers.",
             "يتخيّل",
             ["imagines", "imagined", "imagination (n)", "imaginative (adj)"]),

            (16, "Include",     "➕", "verb",
             "To include means to contain something as a part of a larger thing.",
             "The price includes breakfast and dinner.",
             "يشمل / يتضمن",
             ["includes", "included", "inclusion (n)", "exclude (opp)"]),

            (17, "Indicate",    "👉", "verb",
             "To indicate means to show, point to, or suggest something.",
             "The arrow indicates which way to go.",
             "يُشير إلى / يدل على",
             ["indicates", "indicated", "indication (n)"]),

            (18, "Individual",  "👤", "noun",
             "An individual is one single person, separate from a group.",
             "Every individual has the right to be treated with respect.",
             "فرد / شخص",
             ["individuals (pl)", "individual (adj)", "individually (adv)"]),

            (19, "Inform",      "📢", "verb",
             "To inform means to give someone information or tell them about something.",
             "Please inform the teacher if you are going to be absent.",
             "يُخبر / يُعلم",
             ["informs", "informed", "information (n)"]),

            (20, "Involve",     "🤝", "verb",
             "To involve means to include something as a necessary part.",
             "The job involves travelling to different cities every week.",
             "يشمل / يتضمن",
             ["involves", "involved", "involvement (n)"]),
        ],
    },

    4: {
        "words": [
            (1,  "Issue",       "📰", "noun",
             "An issue is an important topic or problem that people are discussing.",
             "Pollution is one of the most serious environmental issues today.",
             "قضية / مسألة",
             ["issues (pl)", "issue (v)"]),

            (2,  "Journey",     "🚂", "noun",
             "A journey is the act of travelling from one place to another.",
             "The journey from London to Paris takes about two hours by train.",
             "رحلة / مسيرة",
             ["journeys (pl)", "journey (v)"]),

            (3,  "Knowledge",   "📚", "noun",
             "Knowledge is information, facts, and understanding that you have learned.",
             "A doctor needs a deep knowledge of the human body.",
             "معرفة / علم",
             ["knowledgeable (adj)"]),

            (4,  "Likely",      "🎲", "adjective",
             "Something likely is probable or expected to happen.",
             "It is likely to rain tomorrow, so take an umbrella.",
             "مرجّح / محتمل",
             ["likely (adv)", "likelihood (n)", "unlikely (opp)"]),

            (5,  "Limit",       "🚦", "noun",
             "A limit is the greatest amount of something that is allowed or possible.",
             "There is a speed limit of 50 km/h in this area.",
             "حد / قيد",
             ["limits (pl)", "limit (v)", "limited (adj)", "unlimited (opp)"]),

            (6,  "Manage",      "🧭", "verb",
             "To manage means to succeed in doing something difficult.",
             "Despite the problems, they managed to finish the project on time.",
             "يتمكن من / يُدير",
             ["manages", "managed", "management (n)", "manager (n)"]),

            (7,  "Measure",     "📏", "verb",
             "To measure means to find out the size, amount, or degree of something.",
             "He measured the room before buying the new furniture.",
             "يقيس",
             ["measures", "measured", "measurement (n)"]),

            (8,  "Mention",     "🗣️", "verb",
             "To mention means to say or write about something briefly.",
             "She mentioned that she might be late for the meeting.",
             "يذكر",
             ["mentions", "mentioned", "mention (n)"]),

            (9,  "Method",      "🔧", "noun",
             "A method is a particular way of doing something.",
             "The teacher used a new method to help students remember vocabulary.",
             "طريقة / أسلوب",
             ["methods (pl)", "methodical (adj)"]),

            (10, "Occur",       "💥", "verb",
             "To occur means to happen, especially without being planned.",
             "The accident occurred at a busy crossroads.",
             "يحدث / يقع",
             ["occurs", "occurred", "occurrence (n)"]),

            (11, "Offer",       "🎁", "verb",
             "To offer means to say that you are willing to give or do something.",
             "He offered to carry her heavy bags up the stairs.",
             "يعرض / يُقدّم",
             ["offers", "offered", "offer (n)"]),

            (12, "Opportunity", "🚪", "noun",
             "An opportunity is a chance to do something you want to do.",
             "Moving to a new city was a great opportunity to start fresh.",
             "فرصة",
             ["opportunities (pl)"]),

            (13, "Organise",    "🗂️", "verb",
             "To organise means to plan and arrange something carefully.",
             "She organised all her notes before the exam.",
             "يُنظّم / يرتّب",
             ["organises", "organised", "organisation (n)"]),

            (14, "Participate", "🙋", "verb",
             "To participate means to take part in an activity.",
             "All students are encouraged to participate in class discussions.",
             "يشارك",
             ["participates", "participated", "participation (n)"]),

            (15, "Perform",     "🎤", "verb",
             "To perform means to do an activity or task, especially in front of others.",
             "The students performed a short play for their parents.",
             "يؤدي / يقدّم",
             ["performs", "performed", "performance (n)", "performer (n)"]),

            (16, "Predict",     "🔮", "verb",
             "To predict means to say what you think will happen in the future.",
             "Scientists predicted that the storm would arrive by midnight.",
             "يتنبأ / يتوقع",
             ["predicts", "predicted", "prediction (n)", "predictable (adj)"]),

            (17, "Prevent",     "🛑", "verb",
             "To prevent means to stop something from happening.",
             "Washing your hands regularly can help prevent illness.",
             "يمنع / يتفادى",
             ["prevents", "prevented", "prevention (n)"]),

            (18, "Produce",     "🏭", "verb",
             "To produce means to make or create something.",
             "This factory produces five hundred cars every day.",
             "ينتج",
             ["produces", "produced", "production (n)", "product (n)"]),

            (19, "Progress",    "📈", "noun",
             "Progress is the process of developing or improving over time.",
             "She made great progress in her English lessons this term.",
             "تقدّم",
             ["progresses (pl)", "progress (v)"]),

            (20, "Provide",     "🤲", "verb",
             "To provide means to give something that someone needs.",
             "The government provides free education for all children.",
             "يُوفّر / يُقدّم",
             ["provides", "provided", "provision (n)"]),
        ],
    },

    5: {
        "words": [
            (1,  "Purpose",     "🧭", "noun",
             "A purpose is the reason why something is done or made.",
             "The purpose of this lesson is to learn new vocabulary.",
             "هدف / غرض",
             ["purposes (pl)", "purposeful (adj)"]),

            (2,  "Realise",     "💡", "verb",
             "To realise means to become aware of something or understand it suddenly.",
             "She suddenly realised she had left her phone at home.",
             "يدرك / يتفهّم",
             ["realises", "realised", "realisation (n)"]),

            (3,  "Recognise",   "👁️", "verb",
             "To recognise means to know who someone is or what something is because you have seen it before.",
             "I recognised his voice immediately on the phone.",
             "يتعرف على / يدرك",
             ["recognises", "recognised", "recognition (n)"]),

            (4,  "Recommend",   "👍", "verb",
             "To recommend means to suggest that something is good or suitable for someone.",
             "My friend recommended this restaurant — the food is excellent.",
             "يوصي بـ / ينصح بـ",
             ["recommends", "recommended", "recommendation (n)"]),

            (5,  "Require",     "📋", "verb",
             "To require means to need something as necessary or essential.",
             "This job requires five years of experience.",
             "يتطلب / يشترط",
             ["requires", "required", "requirement (n)"]),

            (6,  "Respond",     "💬", "verb",
             "To respond means to say or do something as a reply or reaction.",
             "She responded to his message within five minutes.",
             "يردّ / يستجيب",
             ["responds", "responded", "response (n)"]),

            (7,  "Responsible", "🧑‍⚖️", "adjective",
             "Someone responsible has a duty to look after something or someone.",
             "Each student is responsible for keeping the classroom tidy.",
             "مسؤول",
             ["responsibly (adv)", "responsibility (n)", "irresponsible (opp)"]),

            (8,  "Result",      "🏁", "noun",
             "A result is something that happens because of something else.",
             "As a result of working hard, she passed all her exams.",
             "نتيجة",
             ["results (pl)", "result (v)", "resulting (adj)"]),

            (9,  "Select",      "🔘", "verb",
             "To select means to choose someone or something carefully from a group.",
             "The manager selected the best candidate for the job.",
             "يختار / ينتقي",
             ["selects", "selected", "selection (n)"]),

            (10, "Separate",    "✂️", "verb",
             "To separate means to move apart or keep things apart from each other.",
             "Please separate the coloured clothes from the white ones before washing.",
             "يفصل / يُفرّق",
             ["separates", "separated", "separation (n)", "separate (adj)"]),

            (11, "Similar",     "🪞", "adjective",
             "Two things are similar if they are almost the same but not exactly the same.",
             "These two photos look similar, but there are small differences.",
             "مشابه / متقارب",
             ["similarly (adv)", "similarity (n)", "different (opp)"]),

            (12, "Situation",   "🗺️", "noun",
             "A situation is the set of things that are happening at a particular time.",
             "The doctor calmly handled the dangerous medical situation.",
             "وضع / حالة",
             ["situations (pl)"]),

            (13, "Specific",    "🎯", "adjective",
             "Something specific is exact and clearly defined.",
             "Can you give me a specific example of what you mean?",
             "محدد / خاص",
             ["specifically (adv)", "specification (n)"]),

            (14, "Structure",   "🏗️", "noun",
             "A structure is the way something is built or organised.",
             "The structure of the essay should include an introduction and conclusion.",
             "هيكل / بنية",
             ["structures (pl)", "structure (v)", "structural (adj)"]),

            (15, "Suggest",     "🤔", "verb",
             "To suggest means to mention an idea for someone to think about.",
             "I suggest leaving early to avoid the traffic.",
             "يقترح",
             ["suggests", "suggested", "suggestion (n)"]),

            (16, "Support",     "🤗", "verb",
             "To support means to help someone by giving them what they need.",
             "Her family supported her throughout the difficult time.",
             "يدعم / يساند",
             ["supports", "supported", "support (n)", "supportive (adj)"]),

            (17, "Transfer",    "🔄", "verb",
             "To transfer means to move something or someone from one place to another.",
             "He transferred all the money to his new bank account.",
             "ينقل / يحوّل",
             ["transfers", "transferred", "transfer (n)"]),

            (18, "Value",       "💎", "noun",
             "The value of something is how important or useful it is.",
             "Education has great value for your future career.",
             "قيمة",
             ["values (pl)", "value (v)", "valuable (adj)"]),

            (19, "Various",     "🌈", "adjective",
             "Various means many different kinds of something.",
             "The shop sells various types of coffee from around the world.",
             "متنوع / مختلف",
             ["variously (adv)", "variety (n)", "vary (v)"]),

            (20, "View",        "🌅", "noun",
             "A view is your opinion or way of thinking about something.",
             "In my view, learning a language takes time and patience.",
             "رأي / وجهة نظر",
             ["views (pl)", "view (v)", "viewpoint (n)"]),
        ],
    },
}

# ── Insert words into the database ───────────────────────────────────────────
total_inserted = 0

for unit_number, unit_data in UNITS.items():
    unit = db.query(Unit).filter(
        Unit.book_id == book.id,
        Unit.unit_number == unit_number,
    ).first()

    if not unit:
        print(f"  WARNING: Unit {unit_number} not found in Book 2 — skipping.")
        continue

    # Remove existing words (idempotent re-run)
    existing = db.query(Word).filter(Word.unit_id == unit.id).count()
    if existing > 0:
        db.query(Word).filter(Word.unit_id == unit.id).delete()
        print(f"  Unit {unit_number}: Removed {existing} existing words.")

    for pos, word, emoji, part_of_speech, definition, example, arabic, derivatives in unit_data["words"]:
        db.add(Word(
            unit_id=unit.id,
            position=pos,
            word=word,
            emoji=emoji,
            part_of_speech=part_of_speech,
            definition=definition,
            example=example,
            arabic_translation=arabic,
            derivatives=derivatives,
        ))
        total_inserted += 1

    unit.word_count = len(unit_data["words"])
    title = unit.title or f"Unit {unit_number}"
    print(f"  Unit {unit_number} '{title}': {len(unit_data['words'])} words added.")

db.commit()
print(f"\nDone! {total_inserted} words inserted across {len(UNITS)} units of Book 2 (A2).")
db.close()
