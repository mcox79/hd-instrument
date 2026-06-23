"""contextual_encoding_hrr_PRODUCTION_held_out_v1 -- production-regime
substrate-native polysemy via HRR-binding with TRUE leave-one-out CV.

Production upgrade of contextual_encoding_hrr_binding_smoke_v1
(landed HARD_PASS bind-arms 0.99-1.00 vs static 0.20, but Skunkworks flagged
by-construction-saturation: the smoke had query sentence and gold centroid
encoded from the SAME context bundle, so trivial cosine identity drove the
result. This cell upgrades to sense-held-out leave-one-out where context for
the query and context for the gold centroid come from DIFFERENT sentences for
the same sense.)

DESIGN (4 arms x 3 seeds at N_DIM=4096 over 50 polysemous words x 5 senses x
4 distinct contexts per sense = 1000 (word, sense, context) tuples):

  ARM_STATIC_WORD2VEC      -- control; one vector per word (no binding).
  ARM_BIND_RECENT_5        -- bind(w2v[w], bundle(w2v[w-1..w-5])).
  ARM_BIND_SENTENCE        -- bind(w2v[w], bundle(all w2v in sentence)).
  ARM_BIND_WEIGHTED_PHASE  -- bind(w2v[w], sum_i alpha_i * roll(w2v[w-i], i*k)).

bind = element-wise product on sign-quantized bipolar vectors (substrate-
native HRR analog; involutive).
bundle = mean + L2-normalize then sign-quantize.

Critical evaluation (TRUE leave-one-out across distinct contexts):
  For each (word, sense_i, context_j) query out of 4 contexts per sense:
    gold_centroid = mean(encode arm on each of the OTHER 3 contexts for
                         (word, sense_i)); j' != j
    wrong_centroid[k] (for each k != i) = mean(encode arm on the 4 contexts
                         for (word, sense_k))
  correct iff cos(query, gold_centroid) > max_k cos(query, wrong_centroid[k])
  WSD_acc = correct fraction across all 1000 queries.

  Since gold centroid does NOT include the query's own context vector, this
  is GENUINELY held-out. Static arm: all centroids reduce to the same
  word-vector (since the bundle of a word's centroid across contexts
  collapses) -> ties broken by argmax index -> ~1/5 random.

PRE-REG HARD_PASS bands (preregs/
2026-06-22_contextual_encoding_hrr_PRODUCTION_held_out_v1.md):
  HARD_PASS = ARM_BIND_RECENT_5 mean WSD acc on leave-one-out held-out
              contexts >= 0.70 AND lift over ARM_STATIC_WORD2VEC >= 0.30.
  HARD_FAIL = ALL bind-arms WSD acc <= STATIC + 0.05 (binding does not
              generalize to held-out contexts; mechanism null at production).
  MIDDLE    = partial generalization (some lift but below HARD_PASS).

SANITY: same-context (no held-out) reproduces smoke 0.99-1.00 result.

SUBSTRATE-ONLY: n_llm_calls = 0; numpy + gensim cache (open-weight).
"""
from __future__ import annotations
import sys, os, argparse, time, signal, atexit
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "contextual_encoding_hrr_PRODUCTION_held_out_v1"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)
_LLM_CALL_COUNTER = [0]

# Pre-reg HARD bands (per task spec)
HP_WSD_ACC = 0.70             # ARM_BIND_RECENT_5 must clear this on held-out
HP_LIFT_OVER_STATIC = 0.30    # ... AND lift >= 0.30 over STATIC
HF_LIFT_OVER_STATIC = 0.05    # ALL bind-arms within 0.05 of static -> HARD_FAIL
HP_TARGET_ARM = "ARM_BIND_RECENT_5"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")

# Default is FULL (this is the production cell). Smoke arg or --self-test still
# triggers smoke for queue-gate. Anchor name does NOT contain "_smoke", so
# default is full.
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config
N_DIM = 4096
PRETRAIN_DIM = 300
PHASE_K = 7  # roll shift per position for weighted-phase arm
CONTEXTS_PER_SENSE = 4
SENSES_PER_WORD = 5

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
else:
    SEEDS = [7]

ARMS = ["ARM_STATIC_WORD2VEC", "ARM_BIND_RECENT_5", "ARM_BIND_SENTENCE", "ARM_BIND_WEIGHTED_PHASE"]

CONFIG_VERSION = (
    "contextual_encoding_hrr_PRODUCTION_held_out_v1; N_DIM=%d PRETRAIN_DIM=%d "
    "arms=%s seeds=%s mode=%s PHASE_K=%d contexts_per_sense=%d senses_per_word=%d; "
    "leave_one_out=TRUE; bands HP_arm=%s HP_acc>=%.2f HP_lift>=%.2f HF_lift<=%.2f"
) % (N_DIM, PRETRAIN_DIM, ARMS, SEEDS, RUN_MODE, PHASE_K,
     CONTEXTS_PER_SENSE, SENSES_PER_WORD,
     HP_TARGET_ARM, HP_WSD_ACC, HP_LIFT_OVER_STATIC, HF_LIFT_OVER_STATIC)


# ============================================================================
# WSD dataset: 50 polysemous words x 5 senses x 4 distinct contexts per sense
# = 1000 (word, sense, context) tuples. Each sense has 4 sentences with the
# same disambiguating sense but different surrounding context. This permits
# TRUE leave-one-out: gold centroid is built from OTHER 3 contexts, never the
# query's own.
# ============================================================================

WSD_DATASET: Dict[str, List[Tuple[str, List[str]]]] = {
    "apple": [
        ("fruit", [
            "i ate a red apple from the orchard tree",
            "the apple on the plate was crisp and juicy",
            "she sliced a green apple for the salad bowl",
            "every apple in the basket was perfectly ripe",
        ]),
        ("company", [
            "apple released a new iphone with a faster chip",
            "the apple developer conference unveiled exciting software",
            "shares of apple rose sharply after the earnings report",
            "apple announced an upgrade to its mac operating system",
        ]),
        ("color", [
            "the apple red paint on the wall looks vibrant",
            "she chose an apple shade lipstick for the party",
            "his apple colored sweater stood out in the crowd",
            "the car had a glossy apple finish on its hood",
        ]),
        ("variety", [
            "this gala apple is sweeter than fuji apples",
            "honeycrisp apple trees produce fragrant white blossoms",
            "the granny smith apple is tart and bright green",
            "i planted a braeburn apple tree in the backyard",
        ]),
        ("pie", [
            "she baked an apple pie with cinnamon sugar",
            "the diner serves warm apple pie with vanilla ice cream",
            "grandma rolled the apple pie crust by hand",
            "we ordered a slice of apple pie after dinner tonight",
        ]),
    ],
    "bank": [
        ("finance", [
            "i deposited my paycheck at the bank yesterday",
            "the bank approved my home loan application quickly",
            "she opened a checking account at the local bank",
            "the central bank raised interest rates again today",
        ]),
        ("river", [
            "we sat on the river bank watching the fish swim",
            "the muddy river bank was slippery from the rain",
            "wildflowers grew along the river bank in spring",
            "the otter slid down the river bank into the water",
        ]),
        ("memory", [
            "store this value in the memory bank for later",
            "the computer memory bank holds gigabytes of data",
            "her mind has a vast memory bank of trivia facts",
            "the recovered memory bank revealed the missing logs",
        ]),
        ("aircraft", [
            "the plane began to bank sharply to the left",
            "pilots learn to bank smoothly during basic flight training",
            "the jet had to bank hard to avoid the storm",
            "watch the wings bank as the airliner turns over the airport",
        ]),
        ("trust", [
            "you can bank on her to deliver the project",
            "i bank on his judgment when making tough decisions",
            "do not bank on the weather being clear tomorrow",
            "everyone can bank on his integrity in the courtroom",
        ]),
    ],
    "bass": [
        ("fish", [
            "i caught a large bass while fishing in the lake",
            "the bass put up a strong fight on the line",
            "the striped bass were running in the river this morning",
            "she released the small bass back into the pond",
        ]),
        ("guitar", [
            "he plays bass guitar in a jazz band",
            "the bass guitarist anchored the rhythm section all night",
            "her new bass guitar has five strings instead of four",
            "the bass player tuned his instrument before the gig",
        ]),
        ("pitch", [
            "the bass tones in this recording are very deep",
            "i love the warm bass frequencies of this old amplifier",
            "the engineer boosted the bass on the final mix",
            "the rumbling bass sound shook the entire concert hall",
        ]),
        ("singer", [
            "the bass singer hit a remarkably low note",
            "the bass vocalist anchored the choir with rich tone",
            "his deep bass voice carried across the cathedral",
            "she trained as a bass for the opera company",
        ]),
        ("speaker", [
            "turn up the bass on your stereo speakers",
            "the subwoofer delivers powerful bass at every frequency",
            "this car bass system rattles the rear view mirror",
            "i upgraded my bass cabinet to a larger fifteen inch driver",
        ]),
    ],
    "crane": [
        ("bird", [
            "a tall white crane stood at the edge of the marsh",
            "the crane took flight gracefully across the misty wetland",
            "we watched a crane wade slowly through the shallow river",
            "the sandhill crane migrates south every autumn season",
        ]),
        ("machine", [
            "the construction crane lifted steel beams up high",
            "the dock crane unloaded shipping containers all morning",
            "operators use a tower crane to build tall skyscrapers",
            "the harbor crane swung the cargo onto the waiting truck",
        ]),
        ("stretch", [
            "i had to crane my neck to see over the crowd",
            "she would crane forward to read the chalkboard better",
            "do not crane your head out the open car window",
            "the children crane upward to watch the parade balloons",
        ]),
        ("origami", [
            "she folded a paper crane for the wedding gift",
            "thousand origami crane garlands hung from the ceiling",
            "his paper crane collection filled the entire shelf",
            "the children learned to fold a crane in art class",
        ]),
        ("name", [
            "frasier crane is a famous television character",
            "doctor crane wrote a column for the daily newspaper",
            "the crane family hosted the holiday dinner this year",
            "miss crane teaches the third grade at the local school",
        ]),
    ],
    "match": [
        ("fire", [
            "he lit the match to start the campfire",
            "a single match was enough to ignite the tinder",
            "she struck a match against the rough box surface",
            "the wet match would not catch despite many tries",
        ]),
        ("game", [
            "the soccer match ended in a draw last night",
            "we watched the tennis match on television together",
            "the wrestling match drew a large local crowd",
            "their boxing match lasted twelve grueling rounds",
        ]),
        ("pair", [
            "her dress is a perfect match for those shoes",
            "the curtains were a beautiful match for the rug",
            "this paint is a close match to the original color",
            "your tie is a wonderful match for the new suit jacket",
        ]),
        ("equal", [
            "no one can match his speed on the track",
            "few players match her skill on the basketball court",
            "no chef can match the flavor of her family recipe",
            "the rookie tried to match the veteran in every drill",
        ]),
        ("dating", [
            "the dating app found me a great match this week",
            "her best friend turned out to be a wonderful match",
            "the matchmaker arranged a promising match for him",
            "they were a perfect match from the very first date",
        ]),
    ],
    "spring": [
        ("season", [
            "the flowers bloom every spring in the garden",
            "spring brings warm rain and new green leaves",
            "she loves the smell of fresh spring grass outside",
            "the festival is held each spring at the park",
        ]),
        ("water", [
            "the natural spring provides fresh drinking water",
            "a hot spring bubbled up from the rocky hillside",
            "we hiked to the mountain spring for cool refreshment",
            "the village built a stone wall around the spring source",
        ]),
        ("coil", [
            "the metal spring inside the clock is broken",
            "the spring on the door slammed it shut behind us",
            "a small spring keeps the pen tip retracted",
            "the mechanic replaced the worn spring in the car suspension",
        ]),
        ("jump", [
            "watch the cat spring onto the high shelf",
            "the frog will spring from the lily pad",
            "i saw the runner spring forward at the starting gun",
            "she made the dog spring through the agility hoop",
        ]),
        ("origin", [
            "his decisions spring from a deep moral conviction",
            "many great ideas spring from casual conversations",
            "her creativity seems to spring from genuine curiosity",
            "good leadership traits spring from honest self examination",
        ]),
    ],
    "bark": [
        ("dog", [
            "the dog will bark loudly at every passing stranger",
            "puppies bark to get attention from their owners",
            "she heard the bark of a small terrier outside",
            "the sharp bark startled the children playing nearby",
        ]),
        ("tree", [
            "the rough bark on the oak tree protects the wood",
            "moss grew thick on the bark of the maple",
            "she peeled a strip of birch bark for the craft",
            "the bark of this tree is a deep reddish brown",
        ]),
        ("ship", [
            "the old wooden bark sailed across the harbor",
            "the captain steered the bark through narrow channels",
            "a three masted bark anchored just off the coast",
            "the historic bark was restored at the maritime museum",
        ]),
        ("command", [
            "the sergeant began to bark orders at the recruits",
            "the coach would bark instructions during every practice",
            "she did not appreciate his harsh bark of complaint",
            "the foreman bark commands echoed across the worksite",
        ]),
        ("cinnamon", [
            "grind the cinnamon bark to release the strong spice",
            "the apothecary stocks dried bark of many medicinal trees",
            "willow bark has been used for centuries as a remedy",
            "she boiled bark from the cassia tree to make tea",
        ]),
    ],
    "bat": [
        ("animal", [
            "the bat flew silently out of the cave at dusk",
            "a small bat circled overhead chasing summer insects",
            "the fruit bat hung upside down in the tall tree",
            "we spotted a bat darting through the porch lights",
        ]),
        ("baseball", [
            "he swung the wooden bat and hit a home run",
            "the heavy aluminum bat cracked against the fastball",
            "she chose a lighter bat for her swing speed",
            "the rookie picked up his lucky bat at the dugout",
        ]),
        ("eye", [
            "she did not bat an eye at the shocking news",
            "he never seemed to bat an eyelash during interviews",
            "the witness did not bat an eyelid under questioning",
            "she would bat her eyes whenever she wanted attention",
        ]),
        ("cricket", [
            "the cricket bat is made of high quality willow",
            "he polished his cricket bat before the test match",
            "the batsman lifted his cricket bat after the century",
            "she purchased a new cricket bat from the sports shop",
        ]),
        ("turn", [
            "you go up to bat after the next batter",
            "i will bat fourth in the lineup tonight",
            "she came to bat with two runners on base",
            "he is scheduled to bat leadoff in the championship",
        ]),
    ],
    "bow": [
        ("weapon", [
            "he drew the bow and released the arrow swiftly",
            "the archer raised her bow with steady hands",
            "the long bow had a draw weight of fifty pounds",
            "his recurve bow was crafted from layered horn and wood",
        ]),
        ("ribbon", [
            "tie a pretty bow around the gift box",
            "the wrapping featured a silver bow on top",
            "she added a velvet bow to her holiday wreath",
            "the bow on the package matched the paper pattern",
        ]),
        ("ship", [
            "the bow of the ship cut through the cold waves",
            "salt spray washed over the bow during the storm",
            "the figurehead at the bow was carved from oak",
            "she stood at the bow watching dolphins race ahead",
        ]),
        ("bend", [
            "the actors will bow to the audience after the show",
            "the violinist took a deep bow at the curtain call",
            "the gymnast performed a graceful bow at the end",
            "guests bow politely when greeting the elderly host",
        ]),
        ("violin", [
            "she rosined her violin bow before the concert",
            "the cellist drew a long stroke with the bow",
            "his bow technique improved with daily disciplined practice",
            "the maestro tapped his bow against the music stand",
        ]),
    ],
    "case": [
        ("box", [
            "put the camera back in its leather case carefully",
            "she carried her glasses in a hard plastic case",
            "the violin case had velvet lining inside",
            "his briefcase doubled as a laptop case for travel",
        ]),
        ("legal", [
            "the lawyer presented a strong case to the jury",
            "the case went to the supreme court last spring",
            "she won her first case as a public defender",
            "the prosecutor built a case against the accused over months",
        ]),
        ("instance", [
            "in this case we should call the manager directly",
            "in any case we will arrive before noon tomorrow",
            "in such a case the warranty fully applies",
            "in that case let us reconsider the entire plan",
        ]),
        ("medical", [
            "the doctor reviewed a difficult medical case today",
            "the rare case puzzled the hospital diagnostic team",
            "she presented her clinical case at the conference",
            "this case of unusual symptoms baffled even the specialists",
        ]),
        ("grammar", [
            "the noun case in latin grammar can be tricky",
            "russian declines nouns by case across many forms",
            "the genitive case marks possession in old english",
            "german grammar uses four distinct case endings throughout",
        ]),
    ],
    "club": [
        ("weapon", [
            "the cave man held a heavy wooden club above his head",
            "the guard swung his club at the approaching threat",
            "a knotted club lay at the edge of the clearing",
            "primitive humans crafted a club from a sturdy branch",
        ]),
        ("group", [
            "she joined the book club at the public library",
            "the chess club meets every thursday after school",
            "the garden club organized a spring plant sale",
            "the photography club exhibited their work downtown",
        ]),
        ("nightclub", [
            "they danced at the night club until early morning",
            "the new club downtown plays great house music",
            "the club had a long line of people waiting outside",
            "live bands perform every weekend at this popular club",
        ]),
        ("card", [
            "the club symbol on the playing card is black",
            "she held three of the club suit in her hand",
            "the ace of club beat his queen of heart",
            "deal me one more club from the top of the deck",
        ]),
        ("golf", [
            "his favorite golf club is the seven iron",
            "she swapped to a different club for the long approach shot",
            "the pro recommended a hybrid club for the steep hill",
            "he wiped each club carefully before returning to the bag",
        ]),
    ],
    "court": [
        ("legal", [
            "the supreme court will hear the appeal next month",
            "the federal court ruled in favor of the plaintiff",
            "she clerked at the appellate court after graduation",
            "the district court scheduled the trial for october",
        ]),
        ("sport", [
            "the tennis court was wet from the morning rain",
            "they played a competitive game on the indoor court",
            "the basketball court was freshly painted with new lines",
            "she practiced volleyball drills on the sand court",
        ]),
        ("royal", [
            "the king held court in the grand throne room",
            "courtiers gathered at court every morning to flatter",
            "the medieval court included jesters and musicians",
            "diplomats arrived at the royal court bearing gifts",
        ]),
        ("woo", [
            "he tried to court her with flowers and poetry",
            "the suitor would court the duchess for many months",
            "she politely refused to court her boss for promotion",
            "the senator did not court controversy with his speech",
        ]),
        ("yard", [
            "the apartment court yard has a small fountain",
            "the inner court of the monastery was peaceful",
            "they hung laundry in the back court of the building",
            "a stone court fronted the old farmhouse entryway",
        ]),
    ],
    "date": [
        ("calendar", [
            "what is the date of your next dentist appointment",
            "the historical date of the battle is well documented",
            "she circled the date on the kitchen wall calendar",
            "the closing date for applications is next friday",
        ]),
        ("fruit", [
            "i ate a sweet date from the desert palm tree",
            "the date harvest in tunisia happens every autumn",
            "she added chopped date to the morning oatmeal",
            "fresh date can be eaten right off the palm branch",
        ]),
        ("romantic", [
            "their first date went very well at the restaurant",
            "she suggested coffee for a casual first date",
            "he planned a romantic date for their anniversary",
            "the blind date turned out better than either expected",
        ]),
        ("anchor", [
            "the news anchor will date the broadcast clearly",
            "experts date the rock layer using radiocarbon methods",
            "geologists date fossils with isotopic analysis tools",
            "archaeologists date pottery by stylistic comparison standards",
        ]),
        ("expire", [
            "check the date on the milk before you drink it",
            "the medication date had already passed by months",
            "the package date showed it was still fresh",
            "the date on the canned soup expired last winter",
        ]),
    ],
    "fair": [
        ("just", [
            "the judge made a fair decision in the difficult case",
            "she insisted on a fair distribution of the resources",
            "the referee called a fair penalty against the home team",
            "everyone agreed the verdict was both fair and reasonable",
        ]),
        ("event", [
            "the county fair has rides and cotton candy booths",
            "the science fair showcased student projects all weekend",
            "vendors set up booths at the medieval fair downtown",
            "the renaissance fair drew thousands of costumed visitors",
        ]),
        ("complexion", [
            "she has very fair skin and light blonde hair",
            "his fair complexion burned easily in summer sun",
            "the model had a notably fair color about her face",
            "her fair skin tone required extra sunscreen protection",
        ]),
        ("average", [
            "his performance on the exam was only fair",
            "the restaurant received a fair review in the paper",
            "the harvest yield this year was fair but not great",
            "her presentation skills are still fair at best",
        ]),
        ("weather", [
            "the fair weather brought everyone to the park",
            "we hope for fair skies during the wedding ceremony",
            "the forecast predicted fair conditions all week",
            "after the storm the next morning was clear and fair",
        ]),
    ],
    "fly": [
        ("insect", [
            "a small fly buzzed around the picnic basket",
            "the horse swatted a fly with its long tail",
            "she swatted the fly with a rolled up newspaper",
            "the fly landed on the rim of the lemonade glass",
        ]),
        ("airplane", [
            "we will fly to paris on a morning flight",
            "she learned to fly small single engine planes",
            "the pilots fly transpacific routes for the airline",
            "i fly out of the local airport tomorrow afternoon",
        ]),
        ("pants", [
            "your pants fly is unzipped right now",
            "the tailor adjusted the trouser fly for better fit",
            "the new jeans had a button fly instead of a zipper",
            "she checked her zipper fly before leaving the office",
        ]),
        ("baseball", [
            "the batter hit a long fly ball to center field",
            "the outfielder caught the fly easily near the wall",
            "his pop fly drifted into foul territory just barely",
            "she hit a deep fly that bounced off the warning track",
        ]),
        ("fishing", [
            "he tied a colorful fly to the fishing line",
            "the angler cast a hand tied fly into the stream",
            "trout fishing with a dry fly takes real patience",
            "her favorite fly imitates the local mayfly hatch",
        ]),
    ],
    "kind": [
        ("nice", [
            "she is a very kind person who helps everyone",
            "his kind nature was evident in every interaction",
            "the kind stranger returned the lost wallet promptly",
            "her grandmother was the most kind soul i ever knew",
        ]),
        ("type", [
            "what kind of music do you like to hear",
            "this kind of cheese pairs well with red wine",
            "you can find every kind of tool at this store",
            "the new kind of phone has a folding screen design",
        ]),
        ("sort", [
            "this kind of weather is unusual for april",
            "i do not appreciate this kind of behavior at work",
            "that kind of mistake can ruin an entire project",
            "the kind of patience required for chess is enormous",
        ]),
        ("payment", [
            "they paid him in kind with food and lodging",
            "the farmer received goods in kind for his harvest",
            "the donation was made in kind rather than cash",
            "we settled the debt in kind with carpentry work",
        ]),
        ("offspring", [
            "the lions raised their kind in the open savanna",
            "every species protects its own kind from predators",
            "the elephants gathered to mourn one of their kind",
            "the wolves taught their kind to hunt as a pack",
        ]),
    ],
    "lead": [
        ("metal", [
            "the lead pipes in old houses are very dangerous",
            "the roof flashing was made from sheet lead",
            "they tested the water for traces of lead contamination",
            "old paint sometimes contains harmful amounts of lead",
        ]),
        ("guide", [
            "she will lead the tour group through the museum",
            "the captain will lead the expedition into the jungle",
            "the senior engineer will lead the design review meeting",
            "she was asked to lead the committee on safety standards",
        ]),
        ("clue", [
            "the detective followed a lead in the murder case",
            "a hot lead came in from an anonymous caller",
            "investigators chased every lead until they found him",
            "the witness gave them their first solid lead all week",
        ]),
        ("pencil", [
            "the pencil lead broke when i pressed too hard",
            "sharpen the pencil lead carefully with a small knife",
            "the soft lead made a darker line on the paper",
            "his mechanical pencil holds extra lead in the barrel",
        ]),
        ("first", [
            "the runner took the lead in the final lap",
            "she held the lead from the very start of the race",
            "the horse jumped into the lead at the final turn",
            "they kept their lead in the standings all season",
        ]),
    ],
    "left": [
        ("direction", [
            "turn left at the next intersection by the bank",
            "the church is on the left side of main street",
            "she pointed left toward the distant mountain range",
            "exit on the left after the third traffic signal",
        ]),
        ("departed", [
            "she left the party early to catch her train",
            "the bus left the station at exactly nine sharp",
            "they left for vacation on monday last week",
            "he left his old job to start a new business",
        ]),
        ("remaining", [
            "only three cookies were left in the jar",
            "how much time is left on the parking meter",
            "she had little money left after paying rent",
            "two days are left before the final deadline",
        ]),
        ("political", [
            "the candidate has a strong left wing policy stance",
            "the left coalition won the parliamentary election",
            "her economic ideas lean to the political left",
            "the far left party gained seats in the assembly",
        ]),
        ("hand", [
            "i write with my left hand even though i am ambidextrous",
            "she held the racquet in her left hand for backhand",
            "the surgeon prefers using the left hand for delicate work",
            "the boxer landed a powerful left to the chin",
        ]),
    ],
    "light": [
        ("illumination", [
            "turn on the light when you enter the dark room",
            "the porch light flickered during the thunderstorm",
            "she replaced the burnt out light in the hallway",
            "the soft light from the lamp filled the cozy room",
        ]),
        ("weight", [
            "this suitcase is very light and easy to carry",
            "the feathers are remarkably light for their size",
            "she preferred a light backpack for the long hike",
            "the new aluminum frame is incredibly light yet strong",
        ]),
        ("color", [
            "she painted the walls a light pastel blue",
            "his light gray suit looked elegant at the wedding",
            "the room felt brighter with the light yellow curtains",
            "she chose a light pink shade for the nursery walls",
        ]),
        ("ignite", [
            "use a match to light the birthday candles",
            "he tried to light the campfire in the rain",
            "she struck flint to light the small kindling pile",
            "the host will light the menorah candles each evening",
        ]),
        ("traffic", [
            "the traffic light turned green so we moved forward",
            "the broken traffic light caused a major delay",
            "wait at the red light until it changes to green",
            "the intersection got a new traffic light last week",
        ]),
    ],
    "mean": [
        ("cruel", [
            "do not be mean to your younger brother again",
            "her mean comment hurt his feelings deeply",
            "the mean girl at school finally apologized today",
            "they were mean to the new student on his first day",
        ]),
        ("intend", [
            "i did not mean to spill the coffee on you",
            "she did not mean any harm by the offhand remark",
            "what do you mean by that strange comment",
            "i did mean to call you back yesterday afternoon",
        ]),
        ("average", [
            "calculate the mean of these five exam scores",
            "the arithmetic mean differs from the median value",
            "the mean temperature in july was eighty degrees",
            "compute the mean of the data set before analysis",
        ]),
        ("signify", [
            "what does this strange symbol mean in the manuscript",
            "the red flag might mean danger ahead on the trail",
            "her silence could mean any number of different things",
            "in this context the word can mean two opposite things",
        ]),
        ("intermediate", [
            "find the golden mean between work and rest",
            "the mean position lies halfway between the extremes",
            "the geometric mean is the central tendency for ratios",
            "aristotle wrote about the mean as a virtue",
        ]),
    ],
    "miss": [
        ("title", [
            "good morning miss anderson how are you today",
            "miss jones taught third grade for many years",
            "the contest crowned a new miss universe this evening",
            "miss patel runs the front desk at the dental clinic",
        ]),
        ("fail", [
            "he will miss the bus if he does not hurry",
            "do not miss this chance to study abroad",
            "she did not want to miss the meeting friday",
            "we cannot miss the deadline for the grant application",
        ]),
        ("yearn", [
            "i miss my family back home very much",
            "she will miss her best friend when they move",
            "we all miss the small town we grew up in",
            "he began to miss the routine of his old job",
        ]),
        ("avoid", [
            "duck down to miss the low hanging branch",
            "swerve to miss the deer that crossed the road",
            "she tilted her head to miss the doorway frame",
            "the goalkeeper dove to miss the incoming shot",
        ]),
        ("error", [
            "the goalie made a critical miss in the final minute",
            "his miss of the open shot cost the team the game",
            "the kicker felt terrible about the late miss",
            "the shooter compensated for the previous miss carefully",
        ]),
    ],
    "nail": [
        ("finger", [
            "she painted her finger nail bright red yesterday",
            "her nail polish chipped after one day of work",
            "he bit his thumb nail nervously during the interview",
            "the manicurist filed each nail into a perfect oval",
        ]),
        ("hardware", [
            "hammer the nail into the wooden board firmly",
            "she pulled out the rusty nail with pliers",
            "the carpenter drove each nail with three quick strokes",
            "he found a bent nail sticking out of the deck plank",
        ]),
        ("perform", [
            "she will nail her piano recital with that practice",
            "the comedian nail his audience timing every set",
            "i hope you nail your job interview tomorrow morning",
            "she nail the dive routine despite the pressure",
        ]),
        ("catch", [
            "the police will nail the thief by morning",
            "they finally nail the suspect after years of pursuit",
            "the prosecutor hopes to nail him with this evidence",
            "the detective will nail the embezzler with bank records",
        ]),
        ("animal", [
            "the dog scratched the door with its long nail",
            "the cat sharpens its nail on the scratching post",
            "the cougar tracks showed each individual claw nail",
            "trim the dog nail every few weeks to keep them healthy",
        ]),
    ],
    "park": [
        ("recreation", [
            "we had a picnic at the city park last sunday",
            "the children played soccer at the neighborhood park",
            "the park has hiking trails and a small pond",
            "dogs run freely in the off leash area of the park",
        ]),
        ("vehicle", [
            "park your car in the driveway near the garage",
            "she will park in the lot behind the building",
            "please park along the curb on the west side",
            "you cannot park here during morning rush hour",
        ]),
        ("baseball", [
            "the baseball park was packed for the home opener",
            "the historic baseball park hosted many memorable games",
            "they renovated the old ball park last summer",
            "the new baseball park features a retractable roof",
        ]),
        ("preserve", [
            "yellowstone national park has wild geysers everywhere",
            "the national park rangers led informative wildlife tours",
            "grand canyon national park spans over a million acres",
            "the state park preserves an old growth forest",
        ]),
        ("amusement", [
            "the amusement park has thrilling roller coaster rides",
            "the theme park added a new water ride last spring",
            "we spent the day at the amusement park together",
            "the local amusement park draws crowds every summer weekend",
        ]),
    ],
    "pen": [
        ("writing", [
            "use a blue pen to sign the legal document",
            "the fountain pen wrote smoothly on quality paper",
            "she lost her favorite pen at the conference",
            "the pen leaked ink all over the new shirt",
        ]),
        ("enclosure", [
            "the pigs were kept in a muddy pen behind the barn",
            "she built a small pen for the new chickens",
            "the sheep returned to the pen at sundown",
            "the rancher repaired the cattle pen fencing last week",
        ]),
        ("compose", [
            "she will pen a letter to her grandmother tomorrow",
            "the author will pen a sequel next year",
            "he asked her to pen the introduction for his book",
            "she would pen poetry late into the evening hours",
        ]),
        ("prison", [
            "the convict spent ten years in the state pen",
            "he was sent to the federal pen for fraud charges",
            "the warden ran the pen with strict discipline",
            "they released him from the pen after good behavior",
        ]),
        ("swan", [
            "the female swan is called a pen in nature",
            "the pen guarded her cygnets along the pond edge",
            "the breeding pen swam gracefully near the male",
            "the elegant pen swan glided across the still lake",
        ]),
    ],
    "pitch": [
        ("baseball", [
            "the pitcher threw a fast pitch over the plate",
            "her curve pitch broke sharply at the last moment",
            "the rookie threw a wild pitch that hit the backstop",
            "the closer delivered a perfect pitch for strike three",
        ]),
        ("sales", [
            "the start up gave their sales pitch to investors",
            "her elevator pitch impressed the venture capitalist",
            "the marketing pitch convinced the board to invest",
            "his pitch to the new client landed the contract",
        ]),
        ("sound", [
            "the pitch of her voice is unusually high today",
            "the tuning fork held its pitch steadily for seconds",
            "he could match any pitch on a piano keyboard",
            "her perfect pitch helped her excel in music theory",
        ]),
        ("field", [
            "the soccer pitch was muddy from the heavy rain",
            "they marked the rugby pitch with fresh white lines",
            "the cricket pitch was rolled smooth before the match",
            "groundskeepers prepared the pitch overnight for the game",
        ]),
        ("tar", [
            "the workers spread hot pitch on the roof seams",
            "ancient ships used pitch to seal the wooden hulls",
            "the asphalt pitch sealed the cracks in the driveway",
            "barrels of pitch were stored near the shipyard",
        ]),
    ],
    "ring": [
        ("jewelry", [
            "she wears a gold ring on her left hand",
            "the diamond ring sparkled in the candlelight",
            "her engagement ring was a family heirloom",
            "he gave her a silver ring for their anniversary",
        ]),
        ("phone", [
            "the phone will ring loudly when grandma calls",
            "i heard the ring from the kitchen telephone",
            "the office phone began to ring just after lunch",
            "her cell phone ring tone was a classical melody",
        ]),
        ("circle", [
            "form a ring around the camp fire to keep warm",
            "the dancers made a ring in the grassy meadow",
            "the children sat in a ring during story time",
            "the protesters formed a ring around the building",
        ]),
        ("boxing", [
            "the boxers entered the ring before the championship fight",
            "the referee called the fighters to the center of the ring",
            "she trained for years to compete in the ring",
            "the heavyweight ring announcer introduced both fighters",
        ]),
        ("sound", [
            "the church bells ring every sunday at noon",
            "i could hear the alarm clock ring across the hall",
            "the school bell would ring at exactly three",
            "the meditation gong has a deep resonant ring",
        ]),
    ],
    "rock": [
        ("stone", [
            "she picked up a large rock from the beach",
            "the climber found solid rock on the cliff face",
            "we sat on a flat rock by the riverbank",
            "the granite rock had been smoothed by the glacier",
        ]),
        ("music", [
            "they play rock music at the venue every weekend",
            "classic rock dominated the radio station playlist",
            "his rock band toured nationally last summer",
            "she grew up listening to old rock albums",
        ]),
        ("sway", [
            "the gentle waves rock the boat back and forth",
            "the mother began to rock the baby to sleep",
            "the wind would rock the hammock between the trees",
            "the earthquake made the building rock for several seconds",
        ]),
        ("rocking", [
            "grandma loves to rock in her favorite chair",
            "the porch rock chair creaked with every motion",
            "he liked to rock back on the wooden chair legs",
            "the antique rock chair sat in the corner of the room",
        ]),
        ("gem", [
            "the diamond rock on her finger is enormous",
            "the jeweler appraised the rock at a high value",
            "her engagement rock was nearly three carats",
            "the rapper showed off his iced out rock chain",
        ]),
    ],
    "run": [
        ("jog", [
            "i will run three miles around the park tonight",
            "she likes to run early in the cool morning air",
            "the marathoner can run for hours without stopping",
            "he learned to run a faster pace this summer",
        ]),
        ("operate", [
            "she will run the bakery while her mother recovers",
            "he learned to run the family business from his father",
            "they hired a manager to run the new restaurant",
            "she can run a small team of engineers effectively",
        ]),
        ("flow", [
            "the water will run down the slope after the rain",
            "the river will run faster in the spring melt",
            "tears began to run down her cheeks slowly",
            "the dye would run in the wash with hot water",
        ]),
        ("campaign", [
            "he plans to run for mayor in the next election",
            "she decided to run for the city council seat",
            "they will run a strong candidate against the incumbent",
            "the senator may run for president in two years",
        ]),
        ("baseball", [
            "the batter scored a home run in the ninth inning",
            "he hit a grand slam run for four total runs",
            "the leadoff run came in the bottom of the first",
            "she stole a base to set up the winning run",
        ]),
    ],
    "scale": [
        ("weigh", [
            "step on the scale to check your weight every morning",
            "the kitchen scale measures ingredients to the gram",
            "the postal scale weighs each package before shipping",
            "she calibrated the lab scale before the experiment",
        ]),
        ("fish", [
            "the fish scale glittered in the afternoon sunlight",
            "snake scales differ from fish scale in texture",
            "remove every fish scale with the back of a knife",
            "the iridescent scale of the trout shimmered underwater",
        ]),
        ("size", [
            "the scale of the construction project is enormous",
            "the disaster occurred on an unprecedented scale",
            "the map shows the scale of the entire continent",
            "the architect drew the building at a smaller scale",
        ]),
        ("climb", [
            "the climbers will scale the rock face by morning",
            "they planned to scale the mountain in three days",
            "the soldiers had to scale the castle walls quickly",
            "she could scale the fence with surprising ease",
        ]),
        ("music", [
            "practice the c major scale on the piano daily",
            "she played the minor scale slowly to warm up",
            "the violinist mastered every chromatic scale by age ten",
            "the music teacher taught the pentatonic scale first",
        ]),
    ],
    "sole": [
        ("foot", [
            "the sole of my shoe has worn through completely",
            "the cobbler replaced the sole on the leather boot",
            "she felt a pebble against the sole of her foot",
            "the rubber sole gripped the wet pavement firmly",
        ]),
        ("only", [
            "she is the sole survivor of the terrible accident",
            "he is the sole heir to his uncle vast fortune",
            "they were the sole witnesses of the strange event",
            "the foundation was her sole source of charity income",
        ]),
        ("fish", [
            "the chef prepared a delicate lemon sole for dinner",
            "the sole fillet was served with butter and capers",
            "fresh sole arrives at the market every morning",
            "dover sole is considered a delicacy by many chefs",
        ]),
        ("guitar", [
            "the guitar sole melody captivated the entire audience",
            "the jazz sole featured a long improvised guitar lead",
            "his sole performance earned a standing ovation",
            "the rock sole closed out the entire encore set",
        ]),
        ("law", [
            "she has the sole right to the inheritance now",
            "the company holds the sole rights to that patent",
            "he has sole custody of the children after the ruling",
            "they negotiated for sole distribution rights in europe",
        ]),
    ],
    # Continue extending to 50 polysemous words. Adding 20 more words.
    "table": [
        ("furniture", [
            "set the dishes on the wooden kitchen table",
            "they gathered around the table for sunday dinner",
            "the polished oak table fit perfectly in the dining room",
            "she covered the table with a white linen cloth",
        ]),
        ("data", [
            "the data table summarized the experimental results clearly",
            "consult the reference table for conversion factors",
            "the multiplication table is memorized in elementary school",
            "the periodic table includes every known element",
        ]),
        ("postpone", [
            "the committee voted to table the motion until next week",
            "they decided to table the discussion for later review",
            "the board agreed to table the proposal indefinitely",
            "let us table this debate and return to the agenda",
        ]),
        ("plateau", [
            "the colorado table land stretched for hundreds of miles",
            "the table mountain rises dramatically above cape town",
            "they hiked across a high desert table at sunrise",
            "the geological table formation took millions of years",
        ]),
        ("water_table", [
            "the water table dropped during the long drought",
            "farmers worried about the falling water table all summer",
            "the high water table flooded basements in the area",
            "geologists monitor the water table for changes seasonally",
        ]),
    ],
    "trunk": [
        ("tree", [
            "the squirrel climbed up the trunk of the oak tree",
            "lightning struck the trunk and split it open",
            "the redwood trunk was thicker than a small car",
            "moss grew thick on the north side of the trunk",
        ]),
        ("elephant", [
            "the elephant used its trunk to grasp the apple",
            "the baby elephant trunk could not yet hold water",
            "the trunk of an elephant has thousands of muscles",
            "she watched the elephant lift logs with its trunk",
        ]),
        ("luggage", [
            "she packed her clothes into the heavy steamer trunk",
            "the antique trunk had brass fittings and leather straps",
            "they stored the wedding gifts in an old trunk",
            "the costume trunk held outfits from every era",
        ]),
        ("car", [
            "load the groceries into the back trunk of the car",
            "the spare tire is stored in the trunk compartment",
            "she popped the trunk to retrieve her luggage",
            "the trunk of the sedan was surprisingly spacious",
        ]),
        ("body", [
            "the trunk of the human body holds the vital organs",
            "the gymnast strengthened her trunk muscles with crunches",
            "core exercises focus on the trunk and lower back",
            "the trunk supports the head and connects to the limbs",
        ]),
    ],
    "wave": [
        ("ocean", [
            "a huge wave crashed against the rocky shore",
            "the surfer caught a perfect wave at sunset",
            "the wave broke gently on the sandy beach",
            "the tsunami wave traveled across the entire ocean",
        ]),
        ("gesture", [
            "she gave him a friendly wave from across the street",
            "the queen gave a slow wave to the cheering crowd",
            "he ended the call with a quick wave goodbye",
            "the child sent a small wave to her grandmother",
        ]),
        ("physics", [
            "the radio wave traveled at the speed of light",
            "sound is a longitudinal wave through the air",
            "the wave equation describes oscillating phenomena precisely",
            "ocean wave physics involves complex fluid dynamics",
        ]),
        ("hair", [
            "her hair had a natural wave that everyone admired",
            "the stylist added a soft wave to her short cut",
            "his beard had a slight wave near the chin",
            "the new perm gave her hair a gentle wave",
        ]),
        ("trend", [
            "a new wave of immigration arrived in the city",
            "the next wave of technology will be transformative",
            "the second wave of the pandemic was milder",
            "the heat wave broke records across the southwest",
        ]),
    ],
    "draft": [
        ("writing", [
            "the author finished a first draft of the novel",
            "she edited the draft chapter before submitting it",
            "the rough draft contained many typographical errors",
            "his final draft was much improved over earlier versions",
        ]),
        ("beer", [
            "he ordered a cold draft beer at the local pub",
            "the bartender pulled a fresh draft from the tap",
            "they serve craft draft at the new brewpub downtown",
            "the draft beer special was buy one get one free",
        ]),
        ("conscription", [
            "the army draft notice arrived in the morning mail",
            "many men avoided the wartime draft by leaving the country",
            "the military draft ended in the seventies in america",
            "the draft board reviewed each individual case carefully",
        ]),
        ("sports", [
            "the football draft begins next thursday evening",
            "the team selected the quarterback in the first draft round",
            "the basketball draft generated significant fan excitement",
            "the baseball draft features hundreds of college prospects",
        ]),
        ("air", [
            "a cold draft came under the old wooden door",
            "she felt a chilly draft from the broken window",
            "the chimney draft pulled the smoke up and away",
            "the drafty hallway had a constant cold draft",
        ]),
    ],
    "tip": [
        ("end", [
            "she balanced the pencil on its sharp tip carefully",
            "the tip of the arrow was hand forged from steel",
            "snow covered the tip of the mountain in winter",
            "he cut his finger on the tip of the knife blade",
        ]),
        ("gratuity", [
            "she left a generous tip for the friendly server",
            "the standard tip in this country is fifteen percent",
            "he forgot to leave a tip at the coffee shop",
            "the tip jar at the bakery was always overflowing",
        ]),
        ("advice", [
            "her best tip for cooking pasta is salty water",
            "the chef shared a tip about choosing fresh herbs",
            "let me give you a tip about job interviews",
            "his tip about the stock market proved profitable",
        ]),
        ("lean", [
            "do not tip the canoe by leaning too far over",
            "the boat began to tip dangerously in the storm",
            "she helped tip the heavy box onto the dolly",
            "the wind made the tall vase tip and shatter",
        ]),
        ("informant", [
            "the police received an anonymous tip about the heist",
            "the reporter got a tip from a reliable inside source",
            "her tip led to the arrest of the missing suspect",
            "the detective followed the tip to the abandoned warehouse",
        ]),
    ],
    "post": [
        ("mail", [
            "the post arrived early this morning with three letters",
            "she dropped the package in the post box yesterday",
            "the rural post office closes at noon on saturday",
            "international post can take weeks to arrive sometimes",
        ]),
        ("pole", [
            "the wooden fence post leaned slightly after the storm",
            "the lamp post on the corner needs a new bulb",
            "they sank each post deep into the firm ground",
            "the goal post was knocked over during the wild game",
        ]),
        ("job", [
            "she accepted the new post at the london office",
            "the diplomatic post in tokyo went to her this year",
            "his teaching post at the university paid modestly",
            "she resigned from her post on the executive board",
        ]),
        ("publish", [
            "she will post the photos online tomorrow afternoon",
            "do not post anything you would regret seeing later",
            "he loves to post recipes on his cooking blog",
            "the company will post the quarterly results next monday",
        ]),
        ("after", [
            "the post game show featured player interviews and analysis",
            "the post war era saw rapid economic expansion",
            "post production took longer than the filming itself",
            "post surgery recovery requires patience and physical therapy",
        ]),
    ],
    "stick": [
        ("wood", [
            "the dog fetched the stick from the yard happily",
            "she gathered each stick for the camp fire",
            "the boy whittled a stick into a small whistle",
            "the long stick made a good walking aid",
        ]),
        ("adhere", [
            "the stamps will stick better if you moisten them",
            "the tape would not stick to the dusty surface",
            "the dough began to stick to the wooden counter",
            "the labels stick well to clean glass jars",
        ]),
        ("stab", [
            "do not stick a fork in the toaster ever",
            "she would stick the needle through the fabric carefully",
            "he managed to stick the landing on his backflip",
            "the carpenter would stick each nail at the right angle",
        ]),
        ("persist", [
            "stick with the plan even when it gets hard",
            "if you stick to the schedule you will succeed",
            "she would stick to her decision despite pressure",
            "they decided to stick together through every challenge",
        ]),
        ("hockey", [
            "the hockey stick had been taped at the blade",
            "she chose a lighter composite stick this season",
            "the goalie stick is much wider than a player stick",
            "his slap shot was powered by an expensive carbon stick",
        ]),
    ],
    "block": [
        ("obstruct", [
            "do not block the doorway during the evacuation drill",
            "the parked van will block traffic for several minutes",
            "she tried to block his view of the surprise gift",
            "the fallen tree will block the road until cleared",
        ]),
        ("section", [
            "the bakery is on the next block over from here",
            "they live two block away from the elementary school",
            "the city block was being redeveloped into housing",
            "every block in this neighborhood has a community garden",
        ]),
        ("toy", [
            "the toddler stacked each colored block carefully",
            "she gave the baby a soft fabric block to chew",
            "the wooden building block set lasted three generations",
            "he placed the final block on his alphabet tower",
        ]),
        ("computer", [
            "the data block contained the entire transaction record",
            "the block of memory was allocated for image storage",
            "each block on the disk holds a fixed amount of data",
            "the file system splits files into many block units",
        ]),
        ("sports", [
            "the basketball player made a great block at the rim",
            "the lineman threw a powerful block on the play",
            "the volleyball block sent the ball back over the net",
            "the goalie made a critical block to end the attack",
        ]),
    ],
    "ground": [
        ("earth", [
            "the seedlings broke through the fresh ground in march",
            "she dug into the soft ground with the spade",
            "the rain soaked into the parched garden ground",
            "the construction crew cleared the ground for the new house",
        ]),
        ("electrical", [
            "the wire must be connected to the ground to be safe",
            "the appliance had a faulty ground that caused shocks",
            "an electrician checked the ground wire in the panel",
            "every outlet should have a working ground connection",
        ]),
        ("coffee", [
            "she stored the fresh ground coffee in an airtight jar",
            "the ground espresso smelled wonderful at the cafe",
            "use medium ground coffee for the drip brewer machine",
            "his favorite blend tastes best when freshly ground",
        ]),
        ("forbid", [
            "her parents ground her for breaking the curfew",
            "they ground their teenager for poor grades on the report",
            "do not ground him for an innocent mistake at school",
            "the dean would ground students caught cheating on exams",
        ]),
        ("basis", [
            "the lawyer had no ground for the lawsuit appeal",
            "the philosopher built her argument on solid ground",
            "the agreement rested on the common ground they shared",
            "his theory stood on shaky ground without more evidence",
        ]),
    ],
    "plant": [
        ("vegetation", [
            "she watered the new house plant every morning",
            "the rare desert plant survives on minimal moisture",
            "each plant in the greenhouse received daily care",
            "the climbing plant had reached the top of the trellis",
        ]),
        ("factory", [
            "the auto plant employs over two thousand local workers",
            "the chemical plant met all emissions standards last year",
            "the steel plant operates around the clock daily",
            "the manufacturing plant produced engines for the company",
        ]),
        ("place", [
            "they will plant the flag at the mountain summit",
            "she would plant a kiss on his cheek every morning",
            "the spy was sent to plant evidence at the scene",
            "the gardener would plant tulip bulbs in the autumn",
        ]),
        ("informant", [
            "the police plant infiltrated the criminal organization successfully",
            "the undercover plant gathered evidence for many months",
            "the union suspected a plant was leaking meeting notes",
            "the corporate plant reported back to the rival company",
        ]),
        ("power", [
            "the power plant generated electricity for the entire region",
            "the nuclear plant required extensive safety inspections monthly",
            "the hydroelectric plant operated continuously for decades",
            "the solar plant covered hundreds of desert acres",
        ]),
    ],
    "fine": [
        ("good", [
            "the weather was fine for the outdoor wedding ceremony",
            "the chef prepared a fine meal for the guests",
            "her painting received a fine review in the magazine",
            "the symphony gave a fine performance last evening",
        ]),
        ("delicate", [
            "the fine lace doily decorated the antique table",
            "she has very fine hair that styles easily",
            "the watch had fine engraving on the case back",
            "the artist used a fine brush for the detailed work",
        ]),
        ("penalty", [
            "the speeding fine was three hundred dollars total",
            "she paid the parking fine before the deadline",
            "the late fee fine added up to forty dollars",
            "the court imposed a heavy fine on the company",
        ]),
        ("small", [
            "sift the flour into a fine powder before mixing",
            "the fine sand on this beach felt soft underfoot",
            "the fine mist hung over the meadow at dawn",
            "the fine print at the bottom warned about restrictions",
        ]),
        ("acceptable", [
            "she said it was fine to borrow her car tomorrow",
            "his answer was fine but not particularly insightful",
            "the soup was fine although a bit too salty",
            "their hotel room was perfectly fine for a short stay",
        ]),
    ],
    "letter": [
        ("alphabet", [
            "the first letter of the english alphabet is a",
            "she taught the children each letter of the alphabet",
            "the greek letter alpha is used widely in physics",
            "the chinese character is more complex than a single letter",
        ]),
        ("mail", [
            "she received a long letter from her grandmother today",
            "he wrote a heartfelt letter to his old friend",
            "the love letter was sealed with red wax",
            "the formal letter requested a meeting next month",
        ]),
        ("literal", [
            "follow the instructions to the letter for best results",
            "the contract was honored to the letter by both parties",
            "she obeyed the rules to the letter every single day",
            "he followed the recipe to the letter for the first try",
        ]),
        ("award", [
            "she earned her varsity letter in track and field",
            "the senior letter jacket displayed all of his sports",
            "earning a letter requires consistent dedication and skill",
            "he proudly wore his college letter sweater every winter",
        ]),
        ("font", [
            "the bold letter style stood out on the page",
            "she chose a cursive letter font for the wedding invitations",
            "the headline used a large block letter typeface",
            "the historical letter forms were carefully reproduced by hand",
        ]),
    ],
    "current": [
        ("now", [
            "the current situation requires our immediate attention",
            "the current president took office last january",
            "the current trends in fashion favor bold colors",
            "her current job is more rewarding than the last",
        ]),
        ("water", [
            "the river current was too strong for safe swimming",
            "the tidal current pulled the boat away from shore",
            "swimmers should respect the powerful ocean current always",
            "the current swept the canoe rapidly downstream",
        ]),
        ("electric", [
            "the electric current flowed through the copper wire",
            "the alternating current powers most household appliances",
            "the direct current battery had finally run out",
            "the high voltage current could prove fatal instantly",
        ]),
        ("air", [
            "the air current lifted the kite high into the sky",
            "the jet stream is a fast moving air current",
            "warm air current rose from the heated rocks below",
            "the convection current circulated heat through the room",
        ]),
        ("trend", [
            "the political current shifted toward reform last year",
            "the cultural current flows toward greater individualism",
            "the social current of the era favored progressive ideas",
            "an underground current of dissent ran through the gathering",
        ]),
    ],
    "show": [
        ("display", [
            "she wanted to show her painting at the local gallery",
            "the museum will show the dinosaur exhibit next month",
            "they show the historical artifacts in glass cases",
            "the architect will show the building model tomorrow",
        ]),
        ("performance", [
            "the broadway show opened to rave reviews last night",
            "the television show was renewed for another season",
            "the magic show entertained children at the birthday party",
            "the comedy show sold out within minutes of release",
        ]),
        ("prove", [
            "his actions show that he truly cares about people",
            "the data show a clear trend over the past decade",
            "the results show significant improvement in test scores",
            "her experiments show that the hypothesis was correct",
        ]),
        ("guide", [
            "let me show you around the new office building",
            "she will show the visitors to the conference room",
            "the docent will show us through the museum galleries",
            "he will show you how the new software works",
        ]),
        ("appear", [
            "the guests did not show up until after midnight",
            "the bruise began to show on his arm by morning",
            "the stars show clearly on this dark moonless night",
            "the photograph did not show the speaker very clearly",
        ]),
    ],
    "play": [
        ("game", [
            "the children play tag in the backyard every afternoon",
            "we will play chess after dinner together tonight",
            "they play soccer on saturday mornings at the field",
            "she likes to play card games with her grandchildren",
        ]),
        ("instrument", [
            "she can play the violin beautifully at her age",
            "he learned to play the guitar in high school",
            "the children play piano lessons after school each week",
            "the band members play their instruments with passion",
        ]),
        ("drama", [
            "the high school play opened to a full audience",
            "shakespeare wrote each play with rich layered meaning",
            "the new play ran for six months on broadway",
            "the experimental play was praised by critics this season",
        ]),
        ("recording", [
            "play the recording one more time for accuracy",
            "press the green button to play the audio file",
            "she will play the dvd in the living room tonight",
            "the radio would play her favorite song every hour",
        ]),
        ("freedom", [
            "the rope had too much play to hold the weight",
            "the steering wheel had developed some play over time",
            "give the chain a bit of play to allow movement",
            "the slack play in the cable needed adjustment",
        ]),
    ],
    "stand": [
        ("upright", [
            "please stand for the national anthem before the game",
            "she had to stand for hours on the crowded subway",
            "the children stand quietly during the morning announcements",
            "she will stand at the entrance to greet the guests",
        ]),
        ("booth", [
            "they set up a lemonade stand on the corner",
            "the fruit stand had ripe peaches and strawberries today",
            "the news stand sold magazines and the daily papers",
            "the souvenir stand near the gate had postcards and shirts",
        ]),
        ("opinion", [
            "the senator took a strong stand against the new bill",
            "she would not change her stand on the controversial issue",
            "his moral stand earned him both critics and admirers",
            "the company took a public stand on workers rights",
        ]),
        ("tolerate", [
            "i cannot stand the smell of this old paint",
            "she could not stand his rude behavior any longer",
            "few people can stand the heat of a desert summer",
            "i could not stand watching the sad movie ending",
        ]),
        ("support", [
            "the camera stand held the heavy lens steady",
            "the music stand supported the open sheet music",
            "the bike stand kept the bicycle from falling over",
            "the antique vase stand was carved from solid mahogany",
        ]),
    ],
    "type": [
        ("kind", [
            "what type of music do you usually enjoy listening to",
            "this type of weather is common for the season",
            "the rare type of orchid grows only in the rainforest",
            "her type of humor appeals to many different people",
        ]),
        ("keyboard", [
            "she can type sixty words per minute on the keyboard",
            "he learned to type without looking at the keys",
            "please type the report and email it to me",
            "she likes to type her notes during the lecture",
        ]),
        ("character", [
            "she is exactly the type of person we need on the team",
            "he was a fascinating type who told great stories",
            "the strong silent type rarely showed his true emotions",
            "you are a creative type with a flair for design",
        ]),
        ("printing", [
            "the printer used hot lead type for the headlines",
            "the antique press still used metal type by hand",
            "the bold type made the headline stand out clearly",
            "the historic type was preserved in the museum collection",
        ]),
        ("blood", [
            "her blood type is rare and in high demand",
            "the patient needed type o negative blood urgently",
            "everyone should know their type for emergencies",
            "the donor center matches blood type carefully for each transfusion",
        ]),
    ],
    "sound": [
        ("noise", [
            "the strange sound came from the basement around midnight",
            "the sound of the rain was soothing as she fell asleep",
            "the sound of laughter filled the entire restaurant",
            "the sound from the engine seemed wrong to the mechanic",
        ]),
        ("solid", [
            "she gave a sound argument for the policy change",
            "the bridge was structurally sound after the inspection",
            "his investment advice was always financially sound",
            "the building had sound foundations despite its age",
        ]),
        ("water", [
            "the puget sound is famous for its scenic beauty",
            "they sailed across the long island sound at sunrise",
            "the small fishing boat crossed the deep sound easily",
            "the narrow sound separates the two islands geographically",
        ]),
        ("test", [
            "the doctor will sound the chest with the stethoscope",
            "they sound the patient lungs for irregular breathing",
            "the engineer would sound the metal for hidden cracks",
            "the sailor would sound the depth before approaching shore",
        ]),
        ("convey", [
            "her voice did not sound right on the phone today",
            "the new plan does not sound feasible to me at all",
            "his explanation did not sound convincing to anyone",
            "her excuse did not sound believable to her parents",
        ]),
    ],
    "head": [
        ("body", [
            "she rested her head on the soft pillow",
            "his head ached after the long meeting today",
            "the patient turned her head toward the doctor",
            "he scratched his head while pondering the problem",
        ]),
        ("leader", [
            "the new head of the department arrived yesterday",
            "she became the head of the engineering team",
            "the head of the committee called the meeting to order",
            "the head of state addressed the nation tonight",
        ]),
        ("front", [
            "the parade marched at the head of the street",
            "she sat at the head of the long dinner table",
            "the captain stood at the head of the formation",
            "the river head originates high in the mountains",
        ]),
        ("toilet", [
            "the sailor cleaned the head before inspection",
            "the ship head was located near the bow",
            "report to the head for routine cleaning duty",
            "the small head on the boat needed minor repair",
        ]),
        ("foam", [
            "she poured the beer with a thick head on top",
            "the head on the cappuccino was perfectly creamy",
            "the bartender judges quality by the beer head",
            "a tall head formed on the freshly poured stout",
        ]),
    ],
    "right": [
        ("direction", [
            "turn right at the next traffic signal ahead",
            "the church stands on the right side of the road",
            "she pointed right toward the distant lighthouse",
            "exit on the right after the toll booth plaza",
        ]),
        ("correct", [
            "her answer was right on the very first try",
            "you are right about the weather forecast tomorrow",
            "the right approach will save us hours of work",
            "his guess turned out to be exactly right",
        ]),
        ("entitlement", [
            "every citizen has the right to free speech",
            "she fought for her right to equal pay",
            "the constitutional right protects every individual citizen",
            "they defended the right of the people to vote",
        ]),
        ("political", [
            "the right wing party gained seats in parliament",
            "her economic views lean to the political right",
            "the far right coalition won the recent election",
            "the right of center candidate took office last week",
        ]),
        ("immediately", [
            "i will leave for the airport right after lunch",
            "she answered the phone right when it rang",
            "the package arrived right on schedule this morning",
            "he started writing right as the bell rang",
        ]),
    ],
}


# Sanity asserts at module load
assert len(WSD_DATASET) >= 50, "Need at least 50 polysemous words, got %d" % len(WSD_DATASET)
for w, senses in WSD_DATASET.items():
    assert len(senses) == SENSES_PER_WORD, (
        "Word %s has %d senses (expected %d)" % (w, len(senses), SENSES_PER_WORD))
    for sense_label, contexts in senses:
        assert len(contexts) == CONTEXTS_PER_SENSE, (
            "Word %s sense %s has %d contexts (expected %d)" % (
                w, sense_label, len(contexts), CONTEXTS_PER_SENSE))


# ============================================================================
# Substrate primitives: bipolar sign quantization, bind, bundle
# ============================================================================

def _l2_normalize(X, eps=1e-12):
    if X.ndim == 1:
        n = float(np.linalg.norm(X))
        return X / max(n, eps)
    n = np.linalg.norm(X, axis=1, keepdims=True)
    n[n < eps] = eps
    return X / n


def bipolar_quantize(v: np.ndarray) -> np.ndarray:
    """Sign-quantize real-valued vector to {-1, +1}^N. Zeros -> +1."""
    out = np.sign(v).astype(np.float32)
    out[out == 0] = 1.0
    return out


def bind_elementwise(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR-analog elementwise binding for bipolar vectors. Involutive."""
    return (a * b).astype(np.float32)


def bundle_mean_norm_bipolar(vs: List[np.ndarray]) -> np.ndarray:
    """Bundle = mean -> L2 normalize -> sign quantize (bipolar HD bundle)."""
    if not vs:
        return np.zeros(N_DIM, dtype=np.float32)
    M = np.stack(vs, 0).astype(np.float32)
    s = M.mean(axis=0)
    s = _l2_normalize(s)
    return bipolar_quantize(s)


def gaussian_projection(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    """Random Gaussian projection matrix P [out_dim, in_dim]; JL 1/sqrt(in_dim) scale."""
    rng = np.random.default_rng(seed * 991 + 73)
    P = rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim))
    return P


# ============================================================================
# Word2vec loader + per-word HD encoding pipeline
# ============================================================================

_GENSIM_KV_CACHE: Dict[str, object] = {}


def load_word2vec_kv():
    """Load gensim word2vec-google-news-300 KeyedVectors (cached)."""
    name = "word2vec-google-news-300"
    if name in _GENSIM_KV_CACHE:
        return _GENSIM_KV_CACHE[name]
    import gensim.downloader as gd
    try:
        gd.base_dir = GENSIM_CACHE_DIR
        gd.BASE_DIR = GENSIM_CACHE_DIR
    except Exception:
        pass
    kv = gd.load(name)
    _GENSIM_KV_CACHE[name] = kv
    return kv


def _lookup_w2v_vec(kv, w: str, dim: int) -> np.ndarray:
    """Lookup w2v with simple fallback (exact -> lower); OOV -> zero vec."""
    if w in kv.key_to_index:
        return kv[w].astype(np.float32)
    lw = w.lower()
    if lw in kv.key_to_index:
        return kv[lw].astype(np.float32)
    return np.zeros(dim, dtype=np.float32)


def encode_word_static_hd(word: str, kv, P: np.ndarray) -> np.ndarray:
    """Static word2vec -> project to N_DIM -> L2-normalize -> sign-quantize."""
    v300 = _lookup_w2v_vec(kv, word, P.shape[1])
    if np.linalg.norm(v300) < 1e-9:
        # OOV: deterministic random fallback (so sigma=0 ident still works)
        rng = np.random.default_rng(abs(hash(word)) & 0xFFFFFFFF)
        v = rng.standard_normal(P.shape[0]).astype(np.float32)
        return bipolar_quantize(_l2_normalize(v))
    v300n = _l2_normalize(v300)
    v_proj = (P @ v300n).astype(np.float32)
    return bipolar_quantize(_l2_normalize(v_proj))


def encode_sentence_static(tokens: List[str], kv, P: np.ndarray) -> List[np.ndarray]:
    """Encode each token in sentence as static-HD vector."""
    return [encode_word_static_hd(t, kv, P) for t in tokens]


# ============================================================================
# ARM encoders -- given (sentence tokens, target_word_idx), return HD vector
# ============================================================================

def encode_arm_static(static_vecs: List[np.ndarray], target_idx: int) -> np.ndarray:
    """ARM 1: static word2vec; target vector only (no context binding)."""
    return static_vecs[target_idx]


def encode_arm_bind_recent_5(static_vecs: List[np.ndarray], target_idx: int) -> np.ndarray:
    """ARM 2: bind(target, bundle(recent 5 words excluding target))."""
    start = max(0, target_idx - 5)
    ctx_vecs = static_vecs[start:target_idx]
    if not ctx_vecs:
        ctx_bundle = static_vecs[target_idx]
    else:
        ctx_bundle = bundle_mean_norm_bipolar(ctx_vecs)
    return bind_elementwise(static_vecs[target_idx], ctx_bundle)


def encode_arm_bind_sentence(static_vecs: List[np.ndarray], target_idx: int) -> np.ndarray:
    """ARM 3: bind(target, bundle(all OTHER words in sentence))."""
    ctx_vecs = [v for i, v in enumerate(static_vecs) if i != target_idx]
    if not ctx_vecs:
        ctx_bundle = static_vecs[target_idx]
    else:
        ctx_bundle = bundle_mean_norm_bipolar(ctx_vecs)
    return bind_elementwise(static_vecs[target_idx], ctx_bundle)


def encode_arm_bind_weighted_phase(static_vecs: List[np.ndarray], target_idx: int,
                                    phase_k: int = PHASE_K) -> np.ndarray:
    """ARM 4: bind(target, sum_i alpha_i * roll(w2v[w-i], i*phase_k))."""
    accum = np.zeros(N_DIM, dtype=np.float32)
    any_ctx = False
    for i in range(1, 6):
        j = target_idx - i
        if j < 0:
            break
        any_ctx = True
        alpha = 1.0 / (1.0 + i)
        rolled = np.roll(static_vecs[j], i * phase_k)
        accum += alpha * rolled.astype(np.float32)
    if not any_ctx:
        ctx_bundle = static_vecs[target_idx]
    else:
        ctx_bundle = bipolar_quantize(_l2_normalize(accum))
    return bind_elementwise(static_vecs[target_idx], ctx_bundle)


ARM_FUNCS = {
    "ARM_STATIC_WORD2VEC":      encode_arm_static,
    "ARM_BIND_RECENT_5":        encode_arm_bind_recent_5,
    "ARM_BIND_SENTENCE":        encode_arm_bind_sentence,
    "ARM_BIND_WEIGHTED_PHASE":  encode_arm_bind_weighted_phase,
}


# ============================================================================
# Encoding helpers
# ============================================================================

def find_target_idx(tokens: List[str], target_word: str) -> int:
    """Return first index of target_word in tokens, case-insensitive (with substring fallback)."""
    tw = target_word.lower()
    for i, t in enumerate(tokens):
        if t.lower() == tw:
            return i
    for i, t in enumerate(tokens):
        if tw in t.lower():
            return i
    return -1


def encode_pair(arm_label: str, target_word: str, context_sentence: str,
                kv, P: np.ndarray) -> np.ndarray:
    """Encode a (word, context) pair using the named arm."""
    tokens = context_sentence.split()
    tgt_idx = find_target_idx(tokens, target_word)
    if tgt_idx < 0:
        return np.zeros(N_DIM, dtype=np.float32)
    static_vecs = encode_sentence_static(tokens, kv, P)
    fn = ARM_FUNCS[arm_label]
    return fn(static_vecs, tgt_idx)


# ============================================================================
# TRUE leave-one-out WSD evaluation
# ============================================================================

def encode_all_contexts(arm_label: str,
                        dataset: Dict[str, List[Tuple[str, List[str]]]],
                        kv, P: np.ndarray) -> Dict[str, np.ndarray]:
    """Precompute encoding[w][s_idx, c_idx, :] = encode_pair(arm, w, contexts[c_idx], ...)
    Returns a dict word -> array shape (n_senses, n_contexts, N_DIM).
    """
    out: Dict[str, np.ndarray] = {}
    for w, senses_and_contexts in dataset.items():
        n_s = len(senses_and_contexts)
        n_c = len(senses_and_contexts[0][1])
        enc = np.zeros((n_s, n_c, N_DIM), dtype=np.float32)
        for s_idx, (sense_label, contexts) in enumerate(senses_and_contexts):
            for c_idx, sentence in enumerate(contexts):
                enc[s_idx, c_idx, :] = encode_pair(arm_label, w, sentence, kv, P)
        out[w] = enc
    return out


def eval_wsd_arm_held_out(arm_label: str,
                           dataset: Dict[str, List[Tuple[str, List[str]]]],
                           kv, P: np.ndarray) -> Tuple[float, Dict[str, float]]:
    """TRUE leave-one-out: for each query (w, s_i, c_j),
    gold_centroid = mean(enc[w][s_i, c_!=j, :]) (the OTHER 3 contexts for same sense)
    wrong_centroid[k] = mean(enc[w][s_k, :, :]) for k != s_i (all 4 contexts for OTHER senses)
    correct iff cos(query, gold_centroid) > max_k cos(query, wrong_centroid[k]).
    Returns (overall_acc, per_word_acc).
    """
    enc = encode_all_contexts(arm_label, dataset, kv, P)
    per_word_acc: Dict[str, float] = {}
    total_correct = 0
    total = 0
    for w, enc_w in enc.items():  # enc_w: [n_senses, n_contexts, N_DIM]
        n_senses, n_contexts, _ = enc_w.shape
        n_word_correct = 0
        n_word_total = 0
        for s_i in range(n_senses):
            for c_j in range(n_contexts):
                query = enc_w[s_i, c_j, :]
                # gold centroid: mean of OTHER contexts for sense s_i
                mask = np.ones(n_contexts, dtype=bool)
                mask[c_j] = False
                gold_bundle = enc_w[s_i, mask, :].mean(axis=0)
                gold_n = _l2_normalize(gold_bundle)
                # build all centroids: gold = s_i (held-out), wrong = s_k (full mean)
                centroids = np.zeros((n_senses, N_DIM), dtype=np.float32)
                for s_k in range(n_senses):
                    if s_k == s_i:
                        centroids[s_k, :] = gold_n
                    else:
                        centroids[s_k, :] = _l2_normalize(enc_w[s_k, :, :].mean(axis=0))
                C_n = _l2_normalize(centroids)
                q_n = _l2_normalize(query)
                sims = C_n @ q_n
                pred = int(np.argmax(sims))
                if pred == s_i:
                    n_word_correct += 1
                n_word_total += 1
                total += 1
        per_word_acc[w] = n_word_correct / max(n_word_total, 1)
        total_correct += n_word_correct
    overall = total_correct / max(total, 1)
    return overall, per_word_acc


def eval_wsd_arm_same_context_sanity(arm_label: str,
                                      dataset: Dict[str, List[Tuple[str, List[str]]]],
                                      kv, P: np.ndarray) -> float:
    """SANITY: same-context (NOT leave-one-out) reproduces smoke 0.99-1.00 result.
    For each query (w, s_i, c_j), gold_centroid = enc[w][s_i, c_j, :] (same context).
    correct iff cos(query, gold) > max_k!=i cos(query, mean(enc[w][s_k, :, :])).
    Returns overall accuracy.
    """
    enc = encode_all_contexts(arm_label, dataset, kv, P)
    total_correct = 0
    total = 0
    for w, enc_w in enc.items():
        n_senses, n_contexts, _ = enc_w.shape
        for s_i in range(n_senses):
            for c_j in range(n_contexts):
                query = enc_w[s_i, c_j, :]
                centroids = np.zeros((n_senses, N_DIM), dtype=np.float32)
                for s_k in range(n_senses):
                    if s_k == s_i:
                        centroids[s_k, :] = _l2_normalize(query)  # same context
                    else:
                        centroids[s_k, :] = _l2_normalize(enc_w[s_k, :, :].mean(axis=0))
                C_n = _l2_normalize(centroids)
                q_n = _l2_normalize(query)
                sims = C_n @ q_n
                pred = int(np.argmax(sims))
                if pred == s_i:
                    total_correct += 1
                total += 1
    return total_correct / max(total, 1)


# ============================================================================
# Per-seed unit
# ============================================================================

def run_unit(seed: int) -> Dict:
    t0 = time.time()
    print("\n[seed=%d] loading word2vec (cached)..." % seed, flush=True)
    kv = load_word2vec_kv()
    print("[seed=%d] word2vec loaded; vector_size=%d" % (seed, kv.vector_size), flush=True)
    P = gaussian_projection(in_dim=PRETRAIN_DIM, out_dim=N_DIM, seed=seed)
    by_arm = {}
    for arm_label in ARMS:
        t_arm = time.time()
        held_out_acc, per_word = eval_wsd_arm_held_out(arm_label, WSD_DATASET, kv, P)
        # Sanity: same-context reproduces smoke 0.99-1.00
        same_ctx_acc = eval_wsd_arm_same_context_sanity(arm_label, WSD_DATASET, kv, P)
        t_wall = time.time() - t_arm
        by_arm[arm_label] = {
            "wsd_acc_held_out": round(float(held_out_acc), 4),
            "wsd_acc_same_context_sanity": round(float(same_ctx_acc), 4),
            "per_word_acc_held_out": {w: round(float(v), 4) for w, v in per_word.items()},
            "wall_s": round(t_wall, 2),
        }
        print("  [seed=%d arm=%s] held_out_acc=%.3f same_ctx_sanity=%.3f wall=%.1fs" % (
            seed, arm_label, held_out_acc, same_ctx_acc, t_wall), flush=True)
    return {
        "seed": seed,
        "by_arm": by_arm,
        "N_DIM": N_DIM,
        "PRETRAIN_DIM": PRETRAIN_DIM,
        "n_words": len(WSD_DATASET),
        "n_senses_per_word": SENSES_PER_WORD,
        "n_contexts_per_sense": CONTEXTS_PER_SENSE,
        "n_tuples": len(WSD_DATASET) * SENSES_PER_WORD * CONTEXTS_PER_SENSE,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t0, 2),
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    arm_labels = list(units[0]["by_arm"].keys())
    by_arm_agg = {}
    for arm_label in arm_labels:
        accs = [u["by_arm"][arm_label]["wsd_acc_held_out"] for u in units]
        sames = [u["by_arm"][arm_label]["wsd_acc_same_context_sanity"] for u in units]
        a_mean = float(np.mean(accs))
        a_std = float(np.std(accs))
        a_cv = a_std / max(abs(a_mean), 1e-6)
        s_mean = float(np.mean(sames))
        by_arm_agg[arm_label] = {
            "wsd_acc_held_out_mean": round(a_mean, 4),
            "wsd_acc_held_out_std": round(a_std, 4),
            "wsd_acc_held_out_cv": round(a_cv, 4),
            "wsd_acc_held_out_per_seed": [round(x, 4) for x in accs],
            "wsd_acc_same_context_sanity_mean": round(s_mean, 4),
        }
    static_mean = by_arm_agg["ARM_STATIC_WORD2VEC"]["wsd_acc_held_out_mean"]
    bind_arms = [a for a in arm_labels if a != "ARM_STATIC_WORD2VEC"]
    lifts = {a: round(by_arm_agg[a]["wsd_acc_held_out_mean"] - static_mean, 4) for a in bind_arms}

    # Target arm pre-reg check
    target_mean = by_arm_agg[HP_TARGET_ARM]["wsd_acc_held_out_mean"]
    target_lift = lifts[HP_TARGET_ARM]
    target_hp = (target_mean >= HP_WSD_ACC) and (target_lift >= HP_LIFT_OVER_STATIC)
    all_hf = all(lifts[a] <= HF_LIFT_OVER_STATIC for a in bind_arms)

    # Sanity check status
    target_sanity_mean = by_arm_agg[HP_TARGET_ARM]["wsd_acc_same_context_sanity_mean"]
    sanity_ok = target_sanity_mean >= 0.90

    detail = {
        "by_arm_agg": by_arm_agg,
        "static_held_out_mean": static_mean,
        "lifts_over_static_held_out": lifts,
        "target_arm": HP_TARGET_ARM,
        "target_arm_held_out_mean": target_mean,
        "target_arm_lift": target_lift,
        "target_arm_hard_pass_eligible": bool(target_hp),
        "all_hard_fail": bool(all_hf),
        "sanity_target_same_context_mean": target_sanity_mean,
        "sanity_smoke_reproduction_ok": bool(sanity_ok),
        "n_seeds": len(units),
        "n_words": units[0]["n_words"],
        "n_tuples": units[0]["n_tuples"],
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "Substrate-native HRR-binding for polysemy with TRUE leave-one-out CV: "
            "4 arms (1 static word2vec + 3 context-bind variants) on 50-polysemous-word "
            "x 5-sense x 4-context = 1000 tuples; N_DIM=%d seeds=%d; HARD_PASS = "
            "ARM_BIND_RECENT_5 mean held-out WSD acc>=%.2f AND lift>=%.2f over static; "
            "HARD_FAIL = ALL bind arms within %.2f of static on held-out (binding does "
            "not generalize to new contexts; mechanism null at production)." % (
                N_DIM, len(units), HP_WSD_ACC, HP_LIFT_OVER_STATIC, HF_LIFT_OVER_STATIC)),
        "cites": [
            "preregs/2026-06-22_contextual_encoding_hrr_PRODUCTION_held_out_v1.md",
            "experiments/exp_contextual_encoding_hrr_binding_smoke_v1.py (smoke precedent; flagged by-construction-saturation)",
            "USER_2026-06-22_hippocampus_CA3_substrate_native_polysemy_held_out_generalization",
        ],
    }

    # Build per-arm summary
    parts = []
    for a in arm_labels:
        ag = by_arm_agg[a]
        if a == "ARM_STATIC_WORD2VEC":
            parts.append("%s=%.3f(baseline,same_ctx=%.3f)" % (
                a, ag["wsd_acc_held_out_mean"], ag["wsd_acc_same_context_sanity_mean"]))
        else:
            parts.append("%s=%.3f(lift=%+.3f,same_ctx=%.3f)" % (
                a, ag["wsd_acc_held_out_mean"], lifts[a], ag["wsd_acc_same_context_sanity_mean"]))
    summary = "HRR_BIND_HELD_OUT_WSD: " + " | ".join(parts)
    sanity_str = ("sanity[%s same_ctx=%.3f >=0.90 OK]" % (HP_TARGET_ARM, target_sanity_mean)
                  if sanity_ok else
                  "sanity[%s same_ctx=%.3f WARN <0.90 (smoke not reproduced)]" % (
                      HP_TARGET_ARM, target_sanity_mean))

    if target_hp:
        return ("HARD_PASS",
                ("HRR_BIND_HELD_OUT_WSD HARD_PASS: %s held-out acc=%.3f (>=%.2f) AND lift "
                 "%+.3f over static (>=%.2f); substrate-native HRR-binding for polysemy "
                 "GENUINELY GENERALIZES to held-out contexts; chain-grade-eligible "
                 "contextual-encoding primitive; hippocampus-CA3 brain analog validated "
                 "at production regime. %s. " % (
                     HP_TARGET_ARM, target_mean, HP_WSD_ACC, target_lift,
                     HP_LIFT_OVER_STATIC, sanity_str)) + summary,
                detail)

    if all_hf:
        return ("HARD_FAIL",
                ("HRR_BIND_HELD_OUT_WSD HARD_FAIL: ALL %d bind arms within %.2f of static "
                 "(lifts %s); context-binding does NOT generalize to held-out contexts; "
                 "substrate-native HRR polysemy mechanism null at production regime; "
                 "the smoke-time 0.99 result was by-construction-saturation. %s. " % (
                     len(bind_arms), HF_LIFT_OVER_STATIC, lifts, sanity_str)) + summary,
                detail)

    return ("MIDDLE_BAND",
            ("HRR_BIND_HELD_OUT_WSD MIDDLE_BAND: partial generalization to held-out "
             "contexts (lift over static exceeds %.2f for at least one bind arm but %s "
             "did not clear HP threshold acc>=%.2f AND lift>=%.2f). %s. " % (
                 HF_LIFT_OVER_STATIC, HP_TARGET_ARM, HP_WSD_ACC, HP_LIFT_OVER_STATIC,
                 sanity_str)) + summary,
            detail)


# ============================================================================
# atexit synthesizer
# ============================================================================
_METRICS_WRITTEN = [False]
_OUT_DIR_REF = [None]
_T0_REF = [None]


def _synthesize_on_exit():
    if _METRICS_WRITTEN[0]:
        return
    out_dir = _OUT_DIR_REF[0]
    if out_dir is None or not out_dir.exists():
        return
    try:
        partials = aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS])
        units = list(partials.values())
        if not units:
            return
        try:
            verdict, msg, detail = compute_verdict(units)
        except Exception as e:
            verdict, msg, detail = ("PARTIAL_TIMEOUT",
                                     "atexit synthesize: compute_verdict failed: %s" % e,
                                     {"n_seeds_recovered": len(units)})
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": ("TIMEOUT_PARTIAL_NSEEDS_%d" % len(units)) if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_contextual_encoding_hrr_PRODUCTION_held_out_v1",
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (len(units), len(SEEDS), msg),
            "substrate_only_decode_gate": "TRUE",
            "zero_llm_calls_at_inference": True,
            "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
            "_synthesized_by_atexit": True,
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
        sys.stderr.write("[atexit] synthesized metrics.json from %d/%d partials\n" % (
            len(units), len(SEEDS)))
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write("[atexit] synthesize failed: %s\n" % e)
        sys.stderr.flush()


# ============================================================================
# Self-test
# ============================================================================

def _selftest():
    # T1: bipolar_quantize bipolar output
    v = np.array([0.5, -0.3, 0.0, -0.8, 1.2], dtype=np.float32)
    q = bipolar_quantize(v)
    assert set(np.unique(q).tolist()).issubset({-1.0, 1.0}), "T1 quantize not bipolar"
    assert q[2] == 1.0, "T1 zero -> +1 expected"

    # T2: bind_elementwise involutive
    rng = np.random.default_rng(0)
    a = bipolar_quantize(rng.standard_normal(64).astype(np.float32))
    b = bipolar_quantize(rng.standard_normal(64).astype(np.float32))
    ab = bind_elementwise(a, b)
    abb = bind_elementwise(ab, b)
    assert np.allclose(abb, a), "T2 bind not involutive"

    # T3: bundle_mean_norm_bipolar
    vs = [bipolar_quantize(rng.standard_normal(64).astype(np.float32)) for _ in range(5)]
    bun = bundle_mean_norm_bipolar(vs)
    assert bun.shape == (64,), "T3 bundle shape"
    assert set(np.unique(bun).tolist()).issubset({-1.0, 1.0}), "T3 bundle not bipolar"

    # T4: gaussian_projection JL scale
    P = gaussian_projection(in_dim=300, out_dim=64, seed=0)
    assert P.shape == (64, 300), "T4 P shape"
    s = float(P.std())
    assert 0.04 < s < 0.08, "T4 P std out of JL range: %.4f" % s

    # T5: find_target_idx
    toks = ["the", "apple", "is", "red"]
    assert find_target_idx(toks, "apple") == 1
    assert find_target_idx(toks, "Apple") == 1
    assert find_target_idx(toks, "missing") == -1

    # T6: dataset shape: 50 words x 5 senses x 4 contexts each
    assert len(WSD_DATASET) >= 50, "T6 need >=50 words, got %d" % len(WSD_DATASET)
    for w, senses in WSD_DATASET.items():
        assert len(senses) == SENSES_PER_WORD, "T6 word %s wrong n_senses" % w
        for sense_label, contexts in senses:
            assert len(contexts) == CONTEXTS_PER_SENSE, (
                "T6 word %s sense %s wrong n_contexts" % (w, sense_label))
            for sentence in contexts:
                tokens = sentence.split()
                tgt = find_target_idx(tokens, w)
                assert tgt >= 0, "T6 word %s not in sentence: %s" % (w, sentence)

    # T7: arm encoders shape and bipolar output
    fake_static = [bipolar_quantize(rng.standard_normal(N_DIM).astype(np.float32))
                   for _ in range(8)]
    for arm_label in ARMS:
        fn = ARM_FUNCS[arm_label]
        out = fn(fake_static, target_idx=3)
        assert out.shape == (N_DIM,), "T7 arm %s shape" % arm_label
        assert set(np.unique(out).tolist()).issubset({-1.0, 1.0}), "T7 arm %s not bipolar" % arm_label

    # T8: static context-invariant
    static_a = encode_arm_static(fake_static, target_idx=3)
    fake_static_b = list(fake_static)
    fake_static_b[0] = bipolar_quantize(rng.standard_normal(N_DIM).astype(np.float32))
    static_b = encode_arm_static(fake_static_b, target_idx=3)
    assert np.array_equal(static_a, static_b), "T8 static depends on context (bug)"

    # T9: bind_recent_5 differs with context
    bind_a = encode_arm_bind_recent_5(fake_static, target_idx=5)
    bind_b = encode_arm_bind_recent_5(fake_static_b, target_idx=5)
    assert not np.array_equal(bind_a, bind_b), "T9 bind insensitive to context (bug)"

    # T10: verdict-shape sanity
    def _mk_unit(held_out_per_arm, same_ctx_per_arm):
        ba = {}
        for arm, h, s in zip(ARMS, held_out_per_arm, same_ctx_per_arm):
            ba[arm] = {"wsd_acc_held_out": h, "wsd_acc_same_context_sanity": s,
                       "per_word_acc_held_out": {}, "wall_s": 0.0}
        return {"seed": 0, "by_arm": ba, "N_DIM": N_DIM, "PRETRAIN_DIM": 300,
                "n_words": 50, "n_senses_per_word": 5, "n_contexts_per_sense": 4,
                "n_tuples": 1000, "run_mode": "smoke",
                "config_version": "selftest", "elapsed_s_seed": 0.01}
    # HARD_PASS: target arm at 0.78, static at 0.30 (lift 0.48 >= 0.30)
    u_hp = _mk_unit([0.30, 0.78, 0.45, 0.50], [0.20, 0.99, 0.98, 0.97])
    v, m, d = compute_verdict([u_hp, u_hp, u_hp])
    assert v == "HARD_PASS", "T10 HARD_PASS expected, got %s msg=%s" % (v, m[:200])
    # HARD_FAIL: all bind arms within 0.05 of static
    u_hf = _mk_unit([0.30, 0.33, 0.32, 0.34], [0.20, 0.99, 0.98, 0.97])
    v, m, d = compute_verdict([u_hf, u_hf, u_hf])
    assert v == "HARD_FAIL", "T10 HARD_FAIL expected, got %s msg=%s" % (v, m[:200])
    # MIDDLE: lift > 0.05 but target acc < 0.70
    u_mid = _mk_unit([0.30, 0.55, 0.40, 0.45], [0.20, 0.99, 0.98, 0.97])
    v, m, d = compute_verdict([u_mid, u_mid, u_mid])
    assert v == "MIDDLE_BAND", "T10 MIDDLE expected, got %s msg=%s" % (v, m[:200])

    # T11: held-out eval sanity (small synthetic; no w2v load)
    # Construct enc dict directly: 2 words x 5 senses x 4 contexts.
    # For a perfectly-discriminating arm, each (sense, context) should map to
    # a sense-specific vector that lifts >> chance.
    # We synthesize: enc[w][s,c,:] = sign(b_s + 0.1*noise(c,s)) where b_s differs per sense.
    test_enc = {}
    rng2 = np.random.default_rng(123)
    for w in ["alpha", "beta"]:
        n_s = 5
        n_c = 4
        e = np.zeros((n_s, n_c, N_DIM), dtype=np.float32)
        for s in range(n_s):
            base = rng2.standard_normal(N_DIM).astype(np.float32) * 2.0
            for c in range(n_c):
                noise = rng2.standard_normal(N_DIM).astype(np.float32) * 0.4
                e[s, c, :] = bipolar_quantize(base + noise)
        test_enc[w] = e
    # Run a tiny held-out eval inline to verify the logic shape
    n_correct = 0
    n_total = 0
    for w, enc_w in test_enc.items():
        n_senses, n_contexts, _ = enc_w.shape
        for s_i in range(n_senses):
            for c_j in range(n_contexts):
                query = enc_w[s_i, c_j, :]
                mask = np.ones(n_contexts, dtype=bool)
                mask[c_j] = False
                gold_n = _l2_normalize(enc_w[s_i, mask, :].mean(axis=0))
                centroids = np.zeros((n_senses, N_DIM), dtype=np.float32)
                for s_k in range(n_senses):
                    if s_k == s_i:
                        centroids[s_k, :] = gold_n
                    else:
                        centroids[s_k, :] = _l2_normalize(enc_w[s_k, :, :].mean(axis=0))
                C_n = _l2_normalize(centroids)
                q_n = _l2_normalize(query)
                sims = C_n @ q_n
                pred = int(np.argmax(sims))
                if pred == s_i:
                    n_correct += 1
                n_total += 1
    acc = n_correct / max(n_total, 1)
    # Sense-specific base vectors with mild noise should yield very-high acc
    assert acc >= 0.80, "T11 held-out logic acc too low: %.3f" % acc

    # T12: verify mask excludes self in held-out
    enc_w = test_enc["alpha"]
    n_s, n_c, _ = enc_w.shape
    for s_i in range(n_s):
        for c_j in range(n_c):
            mask = np.ones(n_c, dtype=bool)
            mask[c_j] = False
            assert int(mask.sum()) == n_c - 1, "T12 mask did not exclude self"
            # Verify no row of held-out centroid is the query itself
            held = enc_w[s_i, mask, :]
            for r in range(held.shape[0]):
                assert not np.array_equal(held[r], enc_w[s_i, c_j, :]), (
                    "T12 leave-one-out leak")

    print("[selftest] PASS: T1 quantize + T2 bind involutive + T3 bundle + "
          "T4 projection + T5 find_target + T6 dataset (50 words x 5 senses x 4 contexts) + "
          "T7 arm shapes + T8 static context-invariant + T9 bind context-sensitive + "
          "T10 verdict bands + T11 held-out logic + T12 leave-one-out mask OK",
          flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s N_DIM=%d arms=%s seeds=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, ARMS, SEEDS, CONFIG_VERSION),
          flush=True)
    # Smoke mode: subsample dataset to first 5 words for fast queue gate (<3min cap)
    if RUN_MODE == "smoke":
        keep = sorted(WSD_DATASET.keys())[:5]
        sub = {k: WSD_DATASET[k] for k in keep}
        WSD_DATASET.clear()
        WSD_DATASET.update(sub)
        print("[smoke] subsampled WSD_DATASET to %d words for queue-gate" %
              len(WSD_DATASET), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM,
               "schema": "contextual-encoding-hrr-PRODUCTION-held-out-v1"}
    t0 = time.time()
    _T0_REF[0] = t0
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "PRETRAIN_DIM": PRETRAIN_DIM,
        "n_seeds": len(SEEDS),
        "n_words": len(WSD_DATASET),
        "n_senses_per_word": SENSES_PER_WORD,
        "n_contexts_per_sense": CONTEXTS_PER_SENSE,
        "n_tuples": len(WSD_DATASET) * SENSES_PER_WORD * CONTEXTS_PER_SENSE,
        "detail": detail,
        "metrics_source": "measured_cpu_contextual_encoding_hrr_PRODUCTION_held_out_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        "substrate_only_decode_gate": "TRUE (substrate-native HRR bind on pretrained word2vec; numpy + open-weight gensim cache; zero LLM at inference; held-out leave-one-out CV)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
