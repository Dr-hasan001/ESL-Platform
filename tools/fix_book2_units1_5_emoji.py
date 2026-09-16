"""
fix_book2_units1_5_emoji.py

Book 2 Units 1-5 word/definition/example/Arabic were already corrected to the
real "4000 Essential English Words Book 2" textbook (see seed_book2_units.py
and tools/words_book2.json). That script only ever wrote word/pos/definition/
example/arabic_translation, so emoji and derivatives were left untouched --
for units 2-4 that meant each row still carried the emoji/derivatives from
whichever OLD academic-word-list headword used to occupy that position (e.g.
unit 2's real word "anxious" was showing emoji + derivatives for "Choice").
Units 1 and 5 just got their words replaced for the first time and have no
emoji/derivatives at all yet.

This script sets emoji + derivatives for all 100 words in Units 1-5, keyed by
(unit_number, word.lower()) so it only ever touches the word it names.

Run: python tools/fix_book2_units1_5_emoji.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.book import Book, Unit, Word

# (unit_number, word_lower): (emoji, [derivatives])
DATA = {
    # ── Unit 1 ──────────────────────────────────────────────────────────
    (1, "because"): ("🤔", ["because (no derivatives — function word)"]),
    (1, "east"): ("🌅", ["eastern (adj)", "eastward (adv)"]),
    (1, "expensive"): ("💰", ["expensively (adv)", "expense (n)", "inexpensive (opp)"]),
    (1, "flower"): ("🌸", ["flowers (pl)", "flower (v)", "flowery (adj)"]),
    (1, "garden"): ("🌷", ["gardens (pl)", "garden (v)", "gardener (n)", "gardening (n)"]),
    (1, "holiday"): ("🏖️", ["holidays (pl)", "holiday (v)"]),
    (1, "many"): ("🔢", ["many (no derivatives — function word)"]),
    (1, "million"): ("💯", ["millions (pl)", "millionth (adj)", "millionaire (n)"]),
    (1, "mountain"): ("⛰️", ["mountains (pl)", "mountainous (adj)"]),
    (1, "place"): ("📍", ["places (pl)", "place (v)", "placement (n)"]),
    (1, "popular"): ("🌟", ["popularly (adv)", "popularity (n)", "unpopular (opp)"]),
    (1, "ski"): ("⛷️", ["skis", "skied", "skiing (n)", "skier (n)"]),
    (1, "such"): ("👉", ["such (no derivatives — function word)"]),
    (1, "total"): ("➕", ["totals (pl)", "total (v)", "total (adj)", "totally (adv)"]),
    (1, "tower"): ("🗼", ["towers (pl)", "tower (v)", "towering (adj)"]),
    (1, "town"): ("🏘️", ["towns (pl)", "township (n)"]),
    (1, "train"): ("🚆", ["trains (pl)", "train (v)", "training (n)"]),
    (1, "walk"): ("🚶", ["walks", "walked", "walking (n)", "walker (n)"]),
    (1, "watch"): ("👀", ["watches", "watched", "watching (n)", "watcher (n)"]),
    (1, "world"): ("🌍", ["worlds (pl)", "worldwide (adj/adv)", "worldly (adj)"]),

    # ── Unit 2 ──────────────────────────────────────────────────────────
    (2, "anxious"): ("😰", ["anxiously (adv)", "anxiety (n)"]),
    (2, "awful"): ("😖", ["awfully (adv)"]),
    (2, "consist"): ("🧩", ["consists", "consisted", "consistency (n)", "consistent (adj)"]),
    (2, "desire"): ("💭", ["desires", "desired", "desire (n)", "desirable (adj)"]),
    (2, "eager"): ("🤩", ["eagerly (adv)", "eagerness (n)"]),
    (2, "household"): ("🏠", ["households (pl)", "household (adj)"]),
    (2, "intent"): ("🎯", ["intents (pl)", "intend (v)", "intentional (adj)", "intentionally (adv)"]),
    (2, "landscape"): ("🏞️", ["landscapes (pl)", "landscape (v)", "landscaping (n)"]),
    (2, "lift"): ("🏋️", ["lifts", "lifted", "lift (n)", "lifting (n)"]),
    (2, "load"): ("📦", ["loads", "loaded", "load (n)", "unload (opp)"]),
    (2, "lung"): ("🫁", ["lungs (pl)"]),
    (2, "motion"): ("🎥", ["motions (pl)", "motion (v)", "motionless (adj)"]),
    (2, "pace"): ("🏃", ["paces (pl)", "pace (v)"]),
    (2, "polite"): ("🙏", ["politely (adv)", "politeness (n)", "impolite (opp)"]),
    (2, "possess"): ("🗝️", ["possesses", "possessed", "possession (n)", "possessive (adj)"]),
    (2, "rapidly"): ("⚡", ["rapid (adj)", "rapidity (n)"]),
    (2, "remark"): ("💬", ["remarks", "remarked", "remark (n)", "remarkable (adj)"]),
    (2, "seek"): ("🔍", ["seeks", "sought (past)", "seeker (n)"]),
    (2, "shine"): ("✨", ["shines", "shone/shined (past)", "shiny (adj)", "shine (n)"]),
    (2, "spill"): ("🥤", ["spills", "spilled/spilt (past)", "spill (n)"]),

    # ── Unit 3 ──────────────────────────────────────────────────────────
    (3, "arrow"): ("🏹", ["arrows (pl)"]),
    (3, "battle"): ("⚔️", ["battles (pl)", "battle (v)"]),
    (3, "bow"): ("🏹", ["bows (pl)", "bow (v, different meaning)"]),
    (3, "brave"): ("🦁", ["bravely (adv)", "bravery (n)"]),
    (3, "chief"): ("👑", ["chiefs (pl)", "chief (adj)", "chiefly (adv)"]),
    (3, "disadvantage"): ("👎", ["disadvantages (pl)", "disadvantage (v)", "advantage (opp)"]),
    (3, "enemy"): ("🛡️", ["enemies (pl)"]),
    (3, "entrance"): ("🚪", ["entrances (pl)", "enter (v)", "exit (opp)"]),
    (3, "hardly"): ("🤏", ["hard (adj)"]),
    (3, "intend"): ("🎯", ["intends", "intended", "intent (n)", "intention (n)"]),
    (3, "laughter"): ("😂", ["laugh (v)", "laughable (adj)"]),
    (3, "log"): ("🪵", ["logs (pl)", "log (v)"]),
    (3, "military"): ("🎖️", ["military (adj)", "militarize (v)"]),
    (3, "obey"): ("✅", ["obeys", "obeyed", "obedience (n)", "obedient (adj)", "disobey (opp)"]),
    (3, "secure"): ("🔒", ["secures", "secured", "secure (adj)", "security (n)"]),
    (3, "steady"): ("⚖️", ["steadily (adv)", "steadiness (n)", "unsteady (opp)"]),
    (3, "trust"): ("🤝", ["trusts", "trusted", "trust (n)", "trustworthy (adj)", "distrust (opp)"]),
    (3, "twist"): ("🌀", ["twists", "twisted", "twist (n)"]),
    (3, "unless"): ("❗", ["unless (no derivatives — function word)"]),
    (3, "weapon"): ("🗡️", ["weapons (pl)"]),

    # ── Unit 4 ──────────────────────────────────────────────────────────
    (4, "chest"): ("🫁", ["chests (pl)"]),
    (4, "confidence"): ("💪", ["confident (adj)", "confidently (adv)"]),
    (4, "consequence"): ("➡️", ["consequences (pl)", "consequently (adv)", "consequent (adj)"]),
    (4, "disaster"): ("🌪️", ["disasters (pl)", "disastrous (adj)"]),
    (4, "disturb"): ("😣", ["disturbs", "disturbed", "disturbance (n)", "undisturbed (opp)"]),
    (4, "estimate"): ("🧮", ["estimates", "estimated", "estimate (n)", "estimation (n)"]),
    (4, "honor"): ("🎖️", ["honors", "honored", "honor (n)", "honorable (adj)"]),
    (4, "impress"): ("😮", ["impresses", "impressed", "impression (n)", "impressive (adj)"]),
    (4, "narrow"): ("📏", ["narrowly (adv)", "narrowness (n)", "narrow (v)", "wide (opp)"]),
    (4, "pale"): ("😳", ["palely (adv)", "paleness (n)", "pale (v)"]),
    (4, "rough"): ("🪨", ["roughly (adv)", "roughness (n)", "smooth (opp)"]),
    (4, "satisfy"): ("😊", ["satisfies", "satisfied", "satisfaction (n)", "satisfactory (adj)"]),
    (4, "scream"): ("😱", ["screams", "screamed", "scream (n)"]),
    (4, "sensitive"): ("🌡️", ["sensitively (adv)", "sensitivity (n)", "insensitive (opp)"]),
    (4, "shade"): ("🌳", ["shades (pl)", "shade (v)", "shady (adj)"]),
    (4, "strength"): ("💪", ["strengths (pl)", "strengthen (v)", "strong (adj)"]),
    (4, "supplement"): ("➕", ["supplements", "supplemented", "supplement (n)", "supplementary (adj)"]),
    (4, "terror"): ("😱", ["terrors (pl)", "terrify (v)", "terrifying (adj)", "terrorize (v)"]),
    (4, "threat"): ("⚠️", ["threats (pl)", "threaten (v)", "threatening (adj)"]),
    (4, "victim"): ("🩹", ["victims (pl)", "victimize (v)"]),

    # ── Unit 5 ──────────────────────────────────────────────────────────
    (5, "ancestor"): ("🧓", ["ancestors (pl)", "ancestral (adj)", "ancestry (n)"]),
    (5, "angle"): ("📐", ["angles (pl)", "angle (v)", "angular (adj)"]),
    (5, "boot"): ("🥾", ["boots (pl)", "boot (v)"]),
    (5, "border"): ("🗺️", ["borders (pl)", "border (v)", "borderline (adj)"]),
    (5, "congratulate"): ("🎉", ["congratulates", "congratulated", "congratulation(s) (n)", "congratulatory (adj)"]),
    (5, "frame"): ("🖼️", ["frames (pl)", "frame (v)", "framework (n)"]),
    (5, "heaven"): ("😇", ["heavens (pl)", "heavenly (adj)"]),
    (5, "incredible"): ("😲", ["incredibly (adv)", "credible (opp)", "credibility (n)"]),
    (5, "legend"): ("📖", ["legends (pl)", "legendary (adj)"]),
    (5, "praise"): ("👏", ["praises", "praised", "praise (n)", "praiseworthy (adj)"]),
    (5, "proceed"): ("➡️", ["proceeds", "proceeded", "procedure (n)", "proceeding(s) (n)"]),
    (5, "pure"): ("💎", ["purely (adv)", "purity (n)", "purify (v)", "impure (opp)"]),
    (5, "relative"): ("👪", ["relatives (pl)", "relative (adj)", "relatively (adv)"]),
    (5, "senior"): ("🎓", ["seniors (pl)", "seniority (n)", "junior (opp)"]),
    (5, "silent"): ("🤫", ["silently (adv)", "silence (n)"]),
    (5, "sink"): ("🛳️", ["sinks", "sank (past)", "sunk (pp)", "sinking (n)"]),
    (5, "superior"): ("🏅", ["superiors (pl, n)", "superiority (n)", "inferior (opp)"]),
    (5, "surround"): ("⭕", ["surrounds", "surrounded", "surrounding (adj)", "surroundings (n, pl)"]),
    (5, "thick"): ("📏", ["thickly (adv)", "thickness (n)", "thicken (v)", "thin (opp)"]),
    (5, "wrap"): ("🎁", ["wraps", "wrapped", "wrapping (n)", "unwrap (opp)"]),
}

db = SessionLocal()
book = db.query(Book).filter(Book.book_number == 2).first()
if not book:
    print("ERROR: Book 2 not found.")
    sys.exit(1)

updated = missing = 0
for un in (1, 2, 3, 4, 5):
    unit = db.query(Unit).filter(Unit.book_id == book.id, Unit.unit_number == un).first()
    words = db.query(Word).filter(Word.unit_id == unit.id).all()
    for w in words:
        key = (un, (w.word or "").lower())
        if key not in DATA:
            print(f"  MISSING data for unit {un} word '{w.word}'")
            missing += 1
            continue
        emoji, derivatives = DATA[key]
        w.emoji = emoji
        w.derivatives = derivatives
        updated += 1

db.commit()
print(f"\nDone. {updated} words updated, {missing} missing a data row.")
db.close()
