"""
seed_book1_words.py
Inserts vocabulary words for 4000 Essential English Words Book 1, Units 1-5.
Each unit has 20 target words with definition, example, Arabic translation,
emoji, and derivatives — matching the format used in index.html (Unit 18).

Run: python tools/seed_book1_words.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import *  # noqa: F401
from app.models.book import Book, Unit, Word

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ── Find Book 1 ───────────────────────────────────────────────────────────────
book = db.query(Book).filter(Book.book_number == 1).first()
if not book:
    print("ERROR: Book 1 not found. Run tools/seed_db.py first.")
    db.close()
    sys.exit(1)

# ── Vocabulary data: Units 1-5 ────────────────────────────────────────────────
# Format per word:
#   (position, word, emoji, part_of_speech, definition, example,
#    arabic_translation, [derivatives])

UNITS = {
    1: {
        "title": "Unit 1",
        "words": [
            (1,  "Abandon",   "🚪", "verb",
             "To abandon means to leave something or someone permanently without planning to return.",
             "The sailors were forced to abandon the sinking ship.",
             "يتخلى عن",
             ["abandons", "abandoned", "abandonment (n)"]),

            (2,  "Benefit",   "🎁", "noun",
             "A benefit is something that helps you or gives you an advantage.",
             "Regular exercise has many health benefits.",
             "فائدة / ميزة",
             ["benefits (pl)", "beneficial (adj)", "benefit (v)"]),

            (3,  "Bold",      "🦁", "adjective",
             "Someone who is bold is brave and willing to take risks.",
             "The bold firefighter ran into the burning building.",
             "جريء / شجاع",
             ["boldly (adv)", "boldness (n)", "timid (opp)"]),

            (4,  "Cease",     "🛑", "verb",
             "To cease means to stop doing something completely.",
             "The rain finally ceased after three days.",
             "يتوقف / ينتهي",
             ["ceases", "ceased", "ceaseless (adj)"]),

            (5,  "Crime",     "🚔", "noun",
             "A crime is an action that is against the law.",
             "Stealing from a shop is a crime.",
             "جريمة",
             ["crimes (pl)", "criminal (n/adj)", "criminally (adv)"]),

            (6,  "Cure",      "💊", "noun",
             "A cure is a treatment that makes an illness or problem go away.",
             "Scientists are searching for a cure for the disease.",
             "علاج / شفاء",
             ["cures (pl)", "cure (v)", "curable (adj)"]),

            (7,  "Damage",    "💥", "noun",
             "Damage is harm done to something that reduces its value or usefulness.",
             "The storm caused serious damage to the houses.",
             "ضرر / أذى",
             ["damages (pl)", "damage (v)", "damaged (adj)"]),

            (8,  "Defend",    "🛡️", "verb",
             "To defend means to protect someone or something from attack or harm.",
             "The soldiers defended the city bravely.",
             "يدافع عن",
             ["defends", "defended", "defense (n)", "defender (n)"]),

            (9,  "Depend",    "🤝", "verb",
             "To depend on something means to need it in order to survive or succeed.",
             "Plants depend on sunlight and water to grow.",
             "يعتمد على",
             ["depends", "dependent (adj)", "independence (n)"]),

            (10, "Duty",      "📋", "noun",
             "A duty is something you must do because it is your responsibility.",
             "It is your duty to look after your younger brothers.",
             "واجب / مسؤولية",
             ["duties (pl)", "dutiful (adj)", "dutifully (adv)"]),

            (11, "Escape",    "🏃", "verb",
             "To escape means to get away from a dangerous or unpleasant situation.",
             "The prisoner tried to escape from jail.",
             "يهرب / يفر",
             ["escapes", "escaped", "escape (n)"]),

            (12, "Fame",      "⭐", "noun",
             "Fame is the state of being known and admired by many people.",
             "The singer's fame spread all around the world.",
             "شهرة",
             ["famous (adj)", "famously (adv)", "infamous (adj)"]),

            (13, "Famine",    "🌵", "noun",
             "A famine is a serious situation where many people have very little food.",
             "The famine caused thousands of people to leave their homes.",
             "مجاعة",
             ["famines (pl)", "famine-stricken (adj)"]),

            (14, "Grief",     "😢", "noun",
             "Grief is a strong feeling of sadness, especially after losing someone.",
             "He felt deep grief when his grandfather died.",
             "حزن عميق",
             ["grieves (v)", "grievous (adj)", "grievously (adv)"]),

            (15, "Guard",     "💂", "verb",
             "To guard means to protect someone or something by watching over it carefully.",
             "Two soldiers guarded the palace gate all night.",
             "يحرس",
             ["guards (n)", "guarded (adj)", "guardian (n)"]),

            (16, "Guilty",    "⚖️", "adjective",
             "If someone is guilty, they have done something wrong or illegal.",
             "The jury decided the man was guilty of theft.",
             "مذنب",
             ["guilt (n)", "guiltily (adv)", "innocent (opp)"]),

            (17, "Hardship",  "😤", "noun",
             "Hardship is a situation that is very difficult and involves suffering.",
             "Many families faced hardship during the long war.",
             "صعوبة / معاناة",
             ["hardships (pl)"]),

            (18, "Harvest",   "🌾", "noun",
             "A harvest is the act of collecting crops when they are ready to eat.",
             "The farmers were very happy with the large harvest this year.",
             "حصاد",
             ["harvests (pl)", "harvest (v)", "harvester (n)"]),

            (19, "Humble",    "🙇", "adjective",
             "Someone who is humble does not believe they are better than other people.",
             "Despite his great success, he remained humble and kind.",
             "متواضع",
             ["humbly (adv)", "humility (n)", "arrogant (opp)"]),

            (20, "Increase",  "📈", "verb",
             "To increase means to become greater in number, level, or amount.",
             "The temperature will increase during the afternoon.",
             "يزيد / يرتفع",
             ["increases", "increased", "increase (n)", "decrease (opp)"]),
        ],
    },

    2: {
        "title": "Unit 2",
        "words": [
            (1,  "Labor",     "⛏️", "noun",
             "Labor is hard physical work.",
             "Building the wall required months of hard labor.",
             "عمل شاق / جهد",
             ["labors (pl)", "labor (v)", "laborer (n)"]),

            (2,  "Lack",      "❌", "verb",
             "To lack something means to not have enough of it.",
             "The young team lacked the experience to win the championship.",
             "يفتقر إلى",
             ["lacks", "lack (n)", "lacking (adj)"]),

            (3,  "Loyal",     "🤜", "adjective",
             "Someone who is loyal is firm and faithful in their support for someone.",
             "A loyal friend will stand by you in difficult times.",
             "مخلص / وفي",
             ["loyally (adv)", "loyalty (n)", "disloyal (opp)"]),

            (4,  "Master",    "🏆", "noun",
             "A master is someone who has very great skill or knowledge in something.",
             "He is a true master of the piano.",
             "متقن / سيد",
             ["masters (pl)", "master (v)", "mastery (n)"]),

            (5,  "Mercy",     "🕊️", "noun",
             "Mercy is kindness or forgiveness shown to someone you have power over.",
             "The king showed mercy and set the prisoner free.",
             "رحمة / عفو",
             ["mercies (pl)", "merciful (adj)", "merciless (opp)"]),

            (6,  "Moral",     "✅", "adjective",
             "Something moral relates to what is considered right or good behavior.",
             "He made the moral choice to tell the truth.",
             "أخلاقي",
             ["morally (adv)", "morality (n)", "immoral (opp)"]),

            (7,  "Noble",     "👑", "adjective",
             "A noble person has high moral qualities and acts with great dignity.",
             "It was a noble act to give his food to those who needed it most.",
             "نبيل / شريف",
             ["nobly (adv)", "nobility (n)"]),

            (8,  "Patience",  "⏳", "noun",
             "Patience is the ability to wait or continue calmly without becoming upset.",
             "Learning a new language requires a great deal of patience.",
             "صبر",
             ["patient (adj)", "patiently (adv)", "impatience (opp)"]),

            (9,  "Peace",     "☮️", "noun",
             "Peace is a state of calm, quiet, and freedom from war or conflict.",
             "After years of fighting, the two countries finally agreed to peace.",
             "سلام",
             ["peaceful (adj)", "peacefully (adv)", "war (opp)"]),

            (10, "Plain",     "🏔️", "adjective",
             "Something plain is simple and not decorated or fancy.",
             "She wore a plain white dress to the interview.",
             "بسيط / سادة",
             ["plainly (adv)", "plainness (n)"]),

            (11, "Poison",    "☠️", "noun",
             "A poison is a substance that harms or kills if swallowed or touched.",
             "The doctor warned that the berries contain a dangerous poison.",
             "سم",
             ["poisons (pl)", "poison (v)", "poisonous (adj)"]),

            (12, "Pray",      "🙏", "verb",
             "To pray means to speak to God or a higher power, asking for help or giving thanks.",
             "She prayed every night before going to sleep.",
             "يصلي / يدعو",
             ["prays", "prayed", "prayer (n)", "prayerful (adj)"]),

            (13, "Rare",      "💎", "adjective",
             "Something rare does not happen often or is not found in many places.",
             "Snow is very rare in this part of the country.",
             "نادر",
             ["rarely (adv)", "rarity (n)", "common (opp)"]),

            (14, "Seek",      "🔍", "verb",
             "To seek something means to try to find or achieve it.",
             "He sought advice from his teacher about the difficult problem.",
             "يبحث عن / يسعى إلى",
             ["seeks", "sought (past)", "seeker (n)"]),

            (15, "Shelter",   "🏠", "noun",
             "A shelter is a place that provides protection from weather or danger.",
             "The hikers found shelter in a small cave during the storm.",
             "مأوى / ملجأ",
             ["shelters (pl)", "shelter (v)"]),

            (16, "Steady",    "🎯", "adjective",
             "Something steady is firm, stable, and not likely to change or shake suddenly.",
             "He kept a steady pace throughout the long race.",
             "ثابت / مستقر",
             ["steadily (adv)", "steadiness (n)", "unsteady (opp)"]),

            (17, "Struggle",  "🥊", "verb",
             "To struggle means to try very hard to do something that is difficult.",
             "She struggled to carry the heavy bags up the stairs.",
             "يكافح / يعاني",
             ["struggles (n)", "struggled", "struggling (adj)"]),

            (18, "Talent",    "🎭", "noun",
             "A talent is a natural ability to do something very well.",
             "She has a great talent for music and singing.",
             "موهبة",
             ["talents (pl)", "talented (adj)", "talentless (opp)"]),

            (19, "Trust",     "🤲", "noun",
             "Trust is the belief that someone is honest and will not harm or deceive you.",
             "It took years to build trust between the two groups.",
             "ثقة",
             ["trusts (pl)", "trust (v)", "trustworthy (adj)", "distrust (opp)"]),

            (20, "Vital",     "❤️", "adjective",
             "Something vital is extremely important and necessary for life or success.",
             "It is vital to drink enough water every day to stay healthy.",
             "حيوي / ضروري جداً",
             ["vitally (adv)", "vitality (n)"]),
        ],
    },

    3: {
        "title": "Unit 3",
        "words": [
            (1,  "Admire",    "😍", "verb",
             "To admire someone means to have a very high opinion of them and respect them.",
             "She admired her teacher's dedication and hard work.",
             "يُعجب بـ / يكن تقديراً لـ",
             ["admires", "admired", "admiration (n)", "admirable (adj)"]),

            (2,  "Aid",       "🆘", "noun",
             "Aid is help or support given to someone who needs it.",
             "The organization sent aid to the flood victims.",
             "مساعدة / دعم",
             ["aids (pl)", "aid (v)", "unaided (adj)"]),

            (3,  "Ancient",   "🏛️", "adjective",
             "Something ancient is very old and belongs to a time long ago.",
             "The archaeologists found ancient coins buried deep in the ground.",
             "قديم / أثري",
             ["ancients (n)", "anciently (adv)"]),

            (4,  "Assist",    "🤗", "verb",
             "To assist means to help someone do something.",
             "The nurse assisted the doctor during the long operation.",
             "يساعد / يعاون",
             ["assists", "assistance (n)", "assistant (n)"]),

            (5,  "Battle",    "⚔️", "noun",
             "A battle is a fight between two groups of people, especially soldiers.",
             "The battle lasted for three days before one side surrendered.",
             "معركة",
             ["battles (pl)", "battle (v)", "battlefield (n)"]),

            (6,  "Bitter",    "😖", "adjective",
             "Something bitter has a sharp, unpleasant taste, or a feeling of anger and sadness.",
             "The medicine tasted very bitter but the child swallowed it.",
             "مر / مرير",
             ["bitterly (adv)", "bitterness (n)", "sweet (opp)"]),

            (7,  "Capture",   "🪤", "verb",
             "To capture means to catch a person or animal and keep them as a prisoner.",
             "The police captured the thief after a long chase.",
             "يأسر / يلتقط",
             ["captures", "captured", "capture (n)"]),

            (8,  "Chase",     "🏃‍♂️", "verb",
             "To chase someone means to run after them quickly in order to catch them.",
             "The dog chased the ball across the park.",
             "يلاحق / يطارد",
             ["chases", "chased", "chase (n)"]),

            (9,  "Companion", "👫", "noun",
             "A companion is someone who spends time with you and is your friend.",
             "His dog was his closest companion during the long journey.",
             "رفيق / صاحب",
             ["companions (pl)", "companionship (n)"]),

            (10, "Conquer",   "🏅", "verb",
             "To conquer means to take control of a place or people by force.",
             "Alexander the Great conquered many lands across Asia.",
             "يفتح / يغزو",
             ["conquers", "conquered", "conqueror (n)"]),

            (11, "Creature",  "🐾", "noun",
             "A creature is any living animal or human being.",
             "The deep ocean is home to many strange and beautiful creatures.",
             "مخلوق / كائن",
             ["creatures (pl)"]),

            (12, "Custom",    "🎎", "noun",
             "A custom is a traditional activity or practice in a culture or society.",
             "It is a custom in many cultures to give gifts on special days.",
             "عادة / تقليد",
             ["customs (pl)", "customary (adj)", "customarily (adv)"]),

            (13, "Dawn",      "🌅", "noun",
             "Dawn is the time of day when the sun first appears in the sky.",
             "The farmer got up before dawn to start his daily work.",
             "فجر / بزوغ الفجر",
             ["dawns (pl)", "dawn (v)"]),

            (14, "Defeat",    "🏳️", "verb",
             "To defeat someone means to beat them in a fight or competition.",
             "The home team defeated their opponents by three goals.",
             "يهزم / يتغلب على",
             ["defeats", "defeated", "defeat (n)"]),

            (15, "Deserve",   "🥇", "verb",
             "To deserve something means to have earned it because of your actions.",
             "She worked so hard that she truly deserved to win the prize.",
             "يستحق",
             ["deserves", "deserved", "deserving (adj)"]),

            (16, "Devote",    "💛", "verb",
             "To devote time or energy to something means to give it completely to that thing.",
             "She devoted her life to helping sick and poor children.",
             "يكرّس / يوقف",
             ["devotes", "devoted (adj)", "devotion (n)"]),

            (17, "Distant",   "🌌", "adjective",
             "Something distant is far away in space or time.",
             "The stars are very distant from the Earth.",
             "بعيد",
             ["distantly (adv)", "distance (n)", "near (opp)"]),

            (18, "Eager",     "🙌", "adjective",
             "Someone who is eager is enthusiastic and really wants to do or learn something.",
             "The students were eager to hear the results of the test.",
             "متحمس / متلهف",
             ["eagerly (adv)", "eagerness (n)"]),

            (19, "Envy",      "😒", "noun",
             "Envy is the feeling of wanting something that someone else has.",
             "She felt envy when her friend received a better grade.",
             "حسد / غيرة",
             ["envies (pl)", "envious (adj)", "enviously (adv)", "envy (v)"]),

            (20, "Evil",      "😈", "adjective",
             "Something evil is very bad and causes great harm or suffering.",
             "The villain in the story was an evil king who ruled with fear.",
             "شرير / خبيث",
             ["evilly (adv)", "evil (n)", "good (opp)"]),
        ],
    },

    4: {
        "title": "Unit 4",
        "words": [
            (1,  "Exact",     "🎯", "adjective",
             "Something exact is completely correct and accurate in every detail.",
             "The exact time of the meeting is 3:00 PM.",
             "دقيق / محدد",
             ["exactly (adv)", "exactness (n)", "inexact (opp)"]),

            (2,  "Expand",    "📐", "verb",
             "To expand means to become larger or wider in size or amount.",
             "The company plans to expand its business to other countries.",
             "يتوسع / ينمو",
             ["expands", "expanded", "expansion (n)"]),

            (3,  "Extreme",   "🌡️", "adjective",
             "Something extreme is much greater or more severe than usual.",
             "The explorers faced extreme cold in the mountains.",
             "متطرف / شديد",
             ["extremely (adv)", "extremity (n)"]),

            (4,  "Fail",      "❌", "verb",
             "To fail means to not succeed in doing something that you were trying to do.",
             "He failed his driving test the first time but passed the second time.",
             "يفشل",
             ["fails", "failed", "failure (n)", "succeed (opp)"]),

            (5,  "Fond",      "🥰", "adjective",
             "If you are fond of someone or something, you like them very much.",
             "She is very fond of chocolate cake.",
             "مُحب لـ / معجب بـ",
             ["fondly (adv)", "fondness (n)"]),

            (6,  "Force",     "💪", "noun",
             "Force is strength or power used to do something or to make someone do something.",
             "The police used force to control the angry crowd.",
             "قوة",
             ["forces (pl)", "force (v)", "forceful (adj)"]),

            (7,  "Freeze",    "🧊", "verb",
             "To freeze means to become extremely cold and turn into ice.",
             "The lake freezes every winter because of the cold weather.",
             "يتجمد",
             ["freezes", "froze (past)", "frozen (adj)", "freeze (n)"]),

            (8,  "Gain",      "➕", "verb",
             "To gain something means to get or achieve something useful or valuable.",
             "He gained a lot of experience during his first year at work.",
             "يكتسب / يحقق",
             ["gains", "gained", "gain (n)", "lose (opp)"]),

            (9,  "Gentle",    "🌸", "adjective",
             "Someone or something gentle is kind, calm, and not rough or violent.",
             "The nurse had a gentle way of speaking to the sick patients.",
             "لطيف / رقيق",
             ["gently (adv)", "gentleness (n)", "rough (opp)"]),

            (10, "Grave",     "😐", "adjective",
             "A grave situation is very serious and worrying.",
             "The doctor told the family that the patient was in grave danger.",
             "خطير / جسيم",
             ["gravely (adv)", "gravity (n)"]),

            (11, "Harsh",     "🌩️", "adjective",
             "Something harsh is unpleasant, cruel, or very difficult to deal with.",
             "The prisoners suffered under the harsh conditions of the jail.",
             "قاسٍ / صارم",
             ["harshly (adv)", "harshness (n)", "gentle (opp)"]),

            (12, "Heal",      "🩹", "verb",
             "To heal means to become healthy again after an illness or injury.",
             "The broken bone took six weeks to heal completely.",
             "يشفى / يعالج",
             ["heals", "healed", "healing (n)", "healer (n)"]),

            (13, "Honor",     "🏅", "noun",
             "Honor is a great feeling of pride and respect for doing what is right.",
             "It is a great honor to receive this award from the president.",
             "شرف / كرامة",
             ["honors (pl)", "honorable (adj)", "dishonor (opp)"]),

            (14, "Horror",    "😱", "noun",
             "Horror is a strong feeling of shock, fear, or disgust.",
             "She screamed in horror when she saw the snake in the kitchen.",
             "رعب / فزع",
             ["horrors (pl)", "horrible (adj)", "horribly (adv)"]),

            (15, "Hunt",      "🏹", "verb",
             "To hunt means to chase and kill wild animals for food or sport.",
             "The lion hunts at night when it is cooler.",
             "يصطاد",
             ["hunts", "hunted", "hunter (n)", "hunting (n)"]),

            (16, "Ignore",    "🙈", "verb",
             "To ignore someone or something means to pay no attention to them.",
             "She ignored his advice and made the same mistake again.",
             "يتجاهل",
             ["ignores", "ignored", "ignorance (n)"]),

            (17, "Impact",    "💢", "noun",
             "An impact is the strong effect that something has on a person or situation.",
             "The new law had a big impact on how businesses operate.",
             "تأثير / أثر",
             ["impacts (pl)", "impact (v)", "impactful (adj)"]),

            (18, "Inspire",   "✨", "verb",
             "To inspire means to make someone feel enthusiastic and full of new ideas.",
             "Her courage inspired everyone around her to work harder.",
             "يُلهم / يشجع",
             ["inspires", "inspired", "inspiration (n)", "inspiring (adj)"]),

            (19, "Judge",     "⚖️", "verb",
             "To judge means to form an opinion about someone or to decide a legal case.",
             "Do not judge a person before you know their full story.",
             "يحكم على / يقيّم",
             ["judges", "judged", "judge (n)", "judgment (n)"]),

            (20, "Justice",   "🏛️", "noun",
             "Justice is the quality of being fair and treating people in the right way.",
             "The people demanded justice for those who suffered.",
             "عدالة",
             ["just (adj)", "justly (adv)", "injustice (opp)"]),
        ],
    },

    5: {
        "title": "Unit 5",
        "words": [
            (1,  "Keen",      "👁️", "adjective",
             "If you are keen to do something, you really want to do it and are enthusiastic.",
             "She was keen to learn everything about the new subject.",
             "متحمس / حريص على",
             ["keenly (adv)", "keenness (n)"]),

            (2,  "Lead",      "🗺️", "verb",
             "To lead means to guide a group of people or to be the most important person.",
             "She was chosen to lead the team in the final competition.",
             "يقود",
             ["leads", "led (past)", "leader (n)", "leadership (n)"]),

            (3,  "Legend",    "📜", "noun",
             "A legend is a very old, famous story that may or may not be true.",
             "The children loved listening to the legend of the dragon.",
             "أسطورة",
             ["legends (pl)", "legendary (adj)"]),

            (4,  "Limb",      "🦵", "noun",
             "A limb is an arm or a leg of a person or an animal.",
             "The athlete injured a limb and could not finish the race.",
             "طرف (ذراع أو ساق)",
             ["limbs (pl)"]),

            (5,  "Miserable", "😞", "adjective",
             "Someone who is miserable is very unhappy or suffers a great deal.",
             "The cold, rainy weather made everyone feel miserable.",
             "بائس / تعيس",
             ["miserably (adv)", "misery (n)", "happy (opp)"]),

            (6,  "Naive",     "😇", "adjective",
             "A naive person lacks experience and tends to trust people too easily.",
             "He was so naive that he believed every story he heard.",
             "ساذج / بسيط",
             ["naively (adv)", "naivety (n)"]),

            (7,  "Obstacle",  "🚧", "noun",
             "An obstacle is something that makes it difficult for you to do something.",
             "The lack of money was the biggest obstacle to her dream.",
             "عقبة / عائق",
             ["obstacles (pl)"]),

            (8,  "Obvious",   "💡", "adjective",
             "Something obvious is easy to see or understand.",
             "It was obvious from his smile that he was very happy.",
             "واضح / جليّ",
             ["obviously (adv)", "obviousness (n)"]),

            (9,  "Opponent",  "🥊", "noun",
             "An opponent is the person who you compete against in a game or contest.",
             "She shook hands with her opponent before the chess match.",
             "خصم / منافس",
             ["opponents (pl)", "oppose (v)", "opposition (n)"]),

            (10, "Origin",    "🌍", "noun",
             "The origin of something is where it started or where it came from.",
             "The origin of the word can be traced back to Latin.",
             "أصل / مصدر",
             ["origins (pl)", "original (adj)", "originally (adv)"]),

            (11, "Overcome",  "🧗", "verb",
             "To overcome means to succeed in dealing with a difficult problem or challenge.",
             "She overcame her fear of water and learned to swim.",
             "يتغلب على / يتجاوز",
             ["overcomes", "overcame (past)", "overcoming (adj)"]),

            (12, "Pause",     "⏸️", "verb",
             "To pause means to stop doing something for a short time before continuing.",
             "She paused the video to go and answer the door.",
             "يتوقف مؤقتاً",
             ["pauses", "paused", "pause (n)"]),

            (13, "Possess",   "🗝️", "verb",
             "To possess something means to own or have it.",
             "He possesses great intelligence and a kind heart.",
             "يمتلك",
             ["possesses", "possessed", "possession (n)"]),

            (14, "Predict",   "🔮", "verb",
             "To predict something means to say what you think will happen in the future.",
             "It is difficult to predict exactly what the weather will be like.",
             "يتنبأ / يتوقع",
             ["predicts", "predicted", "prediction (n)", "predictable (adj)"]),

            (15, "Preserve",  "🥒", "verb",
             "To preserve something means to keep it safe and in good condition.",
             "We must preserve the environment for future generations.",
             "يحافظ على / يصون",
             ["preserves", "preserved", "preservation (n)"]),

            (16, "Punish",    "🪄", "verb",
             "To punish someone means to make them suffer because they have done something wrong.",
             "The teacher punished the students who cheated on the exam.",
             "يعاقب",
             ["punishes", "punished", "punishment (n)"]),

            (17, "Reduce",    "📉", "verb",
             "To reduce something means to make it smaller in size, amount, or degree.",
             "You can reduce electricity costs by turning off the lights.",
             "يقلل / يخفض",
             ["reduces", "reduced", "reduction (n)", "increase (opp)"]),

            (18, "Rely",      "🏗️", "verb",
             "To rely on someone means to trust them and depend on them for help.",
             "You can always rely on your best friend in a difficult time.",
             "يعتمد على / يثق بـ",
             ["relies", "relied", "reliable (adj)", "reliability (n)"]),

            (19, "Reveal",    "🎭", "verb",
             "To reveal something means to show or tell something that was hidden or secret.",
             "She revealed the surprise at the end of the party.",
             "يكشف / يُظهر",
             ["reveals", "revealed", "revelation (n)"]),

            (20, "Reward",    "🏆", "noun",
             "A reward is something given to someone because they have done something good.",
             "He received a small reward for returning the lost wallet.",
             "مكافأة / جائزة",
             ["rewards (pl)", "reward (v)", "rewarding (adj)"]),
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
        print(f"  WARNING: Unit {unit_number} not found in Book 1 — skipping.")
        continue

    # Update unit title
    unit.title = unit_data["title"]

    # Remove existing words for this unit (idempotent re-run)
    existing = db.query(Word).filter(Word.unit_id == unit.id).count()
    if existing > 0:
        db.query(Word).filter(Word.unit_id == unit.id).delete()
        print(f"  Unit {unit_number}: Removed {existing} existing words.")

    # Insert new words
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
    print(f"  Unit {unit_number} '{unit_data['title']}': {len(unit_data['words'])} words added.")

db.commit()
print(f"\nDone! {total_inserted} words inserted across {len(UNITS)} units of Book 1.")
db.close()
