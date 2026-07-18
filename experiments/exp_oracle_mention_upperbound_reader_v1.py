"""
ORACLE-MENTION UPPER-BOUND: is MENTION/ENTITY DETECTION the bottleneck that starved the v4 reader
on REAL grade-2 text? Inject GOLD mentions into the EXISTING v4 pipeline (everything else FIXED) and
measure whether the downstream machinery (learned role-assigner + maintained-salience coref +
composition) RECOVERS. This is the cheap info-ceiling-before-fix-cell that BOUNDS THE PRIZE + tests
the mention-starvation hypothesis BEFORE building any learned mention detector.

WHY (v4 HARD_FAIL root; VET ada2392b + drill research_learned_mention_detector_blueprint_..._2026-07-18):
  v4 (exp_learned_role_assigner_reader_wildtext_v4) HARD_FAILed on real 2nd-reader text
  (RELF1 F1=0.217 P=0.153 R=0.375; CO=CC=0.000; CMP=0.250 < freq 0.375). The VET localized the ROOT
  to MENTION/ENTITY DETECTION: the hand-rule detector (v4 candidate_indices + grounding observe-gate)
  grabs mis-grounded non-entities (e.g. daytime->LOCATION, silver/year/gift->owned THING) as mentions
  AND floods the coref antecedent pool -> garbage mentions starve role-assigner + coref + composition.
  The drill's DECISIVE cheap first step: inject GOLD mentions (oracle), hold downstream FIXED, measure
  the RELF1/slice DELTA = how much of the collapse was MENTION-STARVATION.

ONE VARIABLE = the MENTION SET (mention_mode). The downstream is BYTE-IDENTICAL to v4 (same trained
AveragedPerceptron role-assigner, same WorkingOverlay maintained-salience coref, same relation
emission, same RELF1 scorer, same comprehension Q-set + query engine). The mention gate controls BOTH
(a) candidate_indices (role-assigner argument slots + relation args) AND (b) the overlay observe loop
(coref antecedent pool) -- the two places v4 hand-rule mentions feed downstream. NOTHING else is tuned
(coref strategy FIXED = maintained, v4 claim strategy).

ARMS (mention_mode; role-assigner + maintained coref held FIXED):
  oracle     : GOLD hand-annotated referring-entity heads (+ subj/obj pronouns)   [THE UPPER BOUND]
  handrule   : v4 candidate_indices + v4 grounding observe-gate (VERBATIM)         [the 0.217 FLOOR /
               POSITIVE-CONTROL reproduce of v4 -- must match v4 within tolerance]
  everyword  : every POS-noun (NN/NNS/NNP/NNPS) + pronouns                         [high-recall ref]
  grounding  : grounding-lookup nouns only (ground_category not None/COLOR)        [grounding-gate ref]
  frequency  : v4 no-relation grounded frequency floor (mention-independent)       [Q-slice floor ref]

GOLD-MENTION ANNOTATION RULE (documented; applied by the referring-entity rule, NOT tuned to the gold
RELATIONS -- anti-circular): a GOLD mention = a token whose HEAD is a CONCRETE referring discourse
entity (person / animal / thing / place the narrative tracks), PLUS every subj/obj pronoun (pronouns
always refer). EXCLUDE: adjectives incl. color/size/quality (little, brown, great, silver, bright,
old, blind, greedy); quantifiers/numerals (two, three, more, some, one); predicate adjectives after a
copula (dead, poor, asleep); predicate NOMINALS that merely categorize the subject (boy for Henry,
girl for Laura, watchdog for Sport, friends); relational/abstract/temporal non-entity nouns (name,
daytime, years, time, side, middle); surname parts of a multi-word proper name (White, Ellet, Mason,
Brown-as-surname). Concrete "distractor" nouns ARE included even when they hurt precision
(flies/worms/bugs/berries in L18) -- excluding them to help the oracle would be gaming. The gold
comprehension answers are a SEPARATE, independent annotation (anti-circular: mentions are the INPUT
oracle; comprehension gold is the OUTPUT truth).

MEASURE (oracle vs handrule vs everyword vs grounding): RELF1 (P/R/F1, micro over all real passages)
+ the downstream Q-slices NC (single-hop) / CO (ordinary coref) / CC (competitive coref) / CMP
(2-edge composition). The DELTA (oracle - handrule) = how much of the v4 collapse was mention-
starvation vs deeper downstream (coref/attachment/argument-structure) failures a mention fix cannot
reach. HONEST CAVEAT: RELF1 gold is a SPARSE annotation (only the interesting relations), so
PRECISION is gold-coverage-limited (a true-but-unannotated relation is penalized); the LOAD-BEARING
signals are RELF1 RECALL (does oracle recover the gold relations?) + the Q-slice accuracies (COMPLETE
gold -- one answer per Q). Precision reported with that caveat.

BRANCHES (DIAGNOSTIC -- both decisive + informative; genuinely can-fail either way):
  STARVATION_CONFIRMED = oracle mentions RECOVER RELF1 to good AND un-starve composition/coref (rise
    substantially over the handrule floor) -> mention detection IS the bottleneck; the learned mention-
    detector is the worthwhile cheap high-leverage fix, ceiling = the recovered numbers.
  STARVATION_REFUTED  = RELF1 + coref stay poor even with GOLD mentions -> the downstream has its OWN
    real-text failures a mention-detector alone cannot fix; the learned-parser plan must go DEEPER.
  STARVATION_PARTIAL  = mentions help but do not fully recover -> localize WHAT still breaks.

DESIGN-GATE (verified at self-test/smoke, USER: fair tests): (1) POSITIVE-CONTROL: handrule arm
reproduces the v4 pipeline within tolerance; (2) REAL baseline (handrule = the 0.217 floor) + two
reference arms; (3) CAN-FAIL (oracle RELF1/coref can STAY poor); (4) TELEMETRY-SENSITIVE (swapping
mention_mode MUST move the metrics); (5) ONE variable (mention gate; downstream fixed); (6) provenance-
verified verbatim passages; (7) gold mentions validated (each head occurs in its passage; classic
false-positive modifiers DISJOINT from every gold set); (8) determinism OMP=1, fixed seed, sorted(set).

Glass-box, local/foreground-to-completion, NO push / NO remote-persist. Reported CLAIM-VET-pending
(NOT self-declared chain-grade). DIAGNOSTIC (bound the prize + test the hypothesis), NOT the learned-
detector build (that follows from this result + USER steer).

ANCHOR: oracle_mention_upperbound_reader_v1
CORPUS: data/corpora/graded_readers_graded/cleaned/mcguffey_second_reader.clean.txt (REAL, PD, PG#14668).
COMPUTE: sequential-CPU (POS-tag + tiny perceptron fit + symbolic query); wall < 90s; no HD/torch/GPU
  (COMPUTE-PROPORTIONALITY: a directional info-ceiling diagnostic). Local/foreground; no push/no remote.

CELL-TEMPLATE MANDATES (relevant subset; many SCHEMA-VET gates N/A for this non-HD cell-type):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)             [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check at gate                        [META_RULE_AF]
# - discriminator CAN-FAIL (oracle can stay poor)             [design-gate]
# - Gate D positive-control: handrule reproduces v4 at test regime (tol) [reproduce_prior]
# - deterministic seeding (fixed int seed, fixed order, sorted set)  [F.5 / PROT-023]
# - real_code_path: self-test CONSTRUCTS + EXERCISES the REAL WorkingOverlay + REAL perceptron fit +
#   REAL POS tagger + the REAL v4 candidate_indices (handrule) on held-out text  [F.1]
# - substrate_signature: binds WorkingOverlay/observe/resolve_pronoun sigs  [F.2]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 90s)
# - all reported numbers MEASURED@this metrics.json (v4 floor CITED@v4 metrics.json)
# - N/A: KGStore (no KG); N/A cardinality sweep-axis; N/A CRLB (no HD noise floor)
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
import re
import json
import time
import random
import argparse
import hashlib
import platform
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

_THIS = os.path.abspath(__file__)
REPO = os.path.dirname(os.path.dirname(_THIS))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

ANCHOR_NAME = "oracle_mention_upperbound_reader_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)
CORPUS_PATH = os.path.join(REPO, "data", "corpora", "graded_readers_graded", "cleaned",
                           "mcguffey_second_reader.clean.txt")
# v4 landed floor (CITED@ for the positive-control reproduce; NOT re-measured here).
V4_METRICS_PATH = os.path.join(REPO, "data", "exp_learned_role_assigner_reader_wildtext_v4",
                               "metrics.json")

SEED = 12345
N_BOOT = 5000
N_EPOCHS = 12  # averaged-perceptron passes (fixed order, deterministic)

# ---- Pre-registered DIAGNOSTIC bands (set BEFORE the final run) ------------------------
# This is a DIAGNOSTIC info-ceiling cell (both branches informative). The mention_mode is the
# ONE variable; downstream is byte-identical to v4. Primary signals = RELF1 RECALL (does oracle
# recover the gold relations?) + the Q-slice accuracies (COMPLETE gold). RELF1 precision reported
# but flagged gold-coverage-limited. Bands are HYPOTHESIZED@this prereg (pre-run estimates).
#
# POSITIVE-CONTROL (Gate D reproduce_prior): the handrule arm must reproduce the v4 pipeline at the
# test regime -- proves the oracle injection is truly one-variable off REAL v4.
V4_HANDRULE_RELF1_F1 = 0.217   # CITED@V4_METRICS_PATH:relation_f1.learned_full.micro_f1
V4_HANDRULE_CMP = 0.250        # CITED@V4_METRICS_PATH:discriminators.composition_learned_full
V4_HANDRULE_CC = 0.000         # CITED@V4_METRICS_PATH:discriminators.cc_maintained
V4_HANDRULE_NC = 0.571         # CITED@V4_METRICS_PATH:arms.learned_full.acc_NC
REPRODUCE_TOL_F1 = 0.03        # handrule RELF1 F1 must be within this of the v4 floor
REPRODUCE_TOL_SLICE = 0.05     # handrule CMP/CC/NC within this of v4
# STARVATION_CONFIRMED thresholds (oracle mentions un-starve the machinery to good):
CONF_RELF1_F1 = 0.55           # oracle RELF1 micro-F1 recovers toward good
CONF_RELF1_RECALL = 0.70       # oracle recovers most gold relations
CONF_CMP = 0.55                # oracle composition recovers
CONF_CC = 0.40                 # oracle competitive coref recovers off the 0.000 floor
# STARVATION_REFUTED thresholds (oracle stays poor even with gold mentions):
REF_RELF1_F1 = 0.45            # oracle RELF1 micro-F1 still poor
REF_CC = 0.20                  # oracle competitive coref still near the floor
# Telemetry-sensitivity: swapping handrule->oracle must MOVE at least one primary metric by this.
TELEMETRY_MIN_MOVE = 0.05
# baseline-in-band guard (comprehension_all for the non-mechanism frequency floor).
BASELINE_BAND = (0.05, 0.95)

# =======================================================================================
# GROUNDING (dictionary = picture/teacher stand-in). Words are KNOWN, NOT held out.
# Animacy from WordNet lexname + a small curated set of proper NAMES and grade-1 ANIMALS
# (names are absent from WordNet; a few concrete nouns have a non-obvious first sense).
# This is GROUNDING of already-known words -- it is NOT the per-passage extraction rule
# table that made v1 construction-determined. The role ASSIGNMENT is learned, not grounded.
# =======================================================================================
NAME_GENDER = {
    "ned": "masc", "tom": "masc", "john": "masc", "ben": "masc", "nat": "masc",
    "sam": "masc", "will": "masc",
    "ann": "fem", "kitty": "fem", "nell": "fem", "kate": "fem", "mamma": "fem",
    "mary": "fem", "sue": "fem", "jane": "fem",
    "jip": None, "rab": None, "prince": None, "fido": None, "spot": None,
    # v4 -- 2nd-reader NAMES (grounding dictionary; gender is a real dictionary fact, not a rule table)
    "harry": "masc", "james": "masc", "henry": "masc", "george": "masc", "willie": "masc",
    "robert": "masc", "mason": "masc", "ellet": "masc", "herbert": "masc",
    "susie": "fem", "patty": "fem", "laura": "fem", "katie": "fem",
    "dodger": None, "sport": None, "bounce": None, "dash": None, "puss": None,
    "brown": None, "english": None,
}
ANIMALS = {"hen", "hens", "duck", "ducks", "cow", "dog", "dogs", "cat", "cats", "rat",
           "rats", "pet", "bird", "birds", "frog", "fox", "nag", "owl", "pig", "hare",
           "lamb", "colt", "goat", "bee", "ox",
           # v4 -- 2nd-reader animals + the named pets (grounded animacy)
           "kingbird", "robin", "sport", "dodger", "bounce", "puss", "kitten", "kittens",
           "eagle", "hawk", "tiger", "tigress", "horse", "squirrel", "mouse", "sheep"}
PERSON_NOUNS = {"man", "men", "lad", "boy", "boys", "girl", "girls", "child",
                "baby", "woman",
                # v4 -- 2nd-reader person nouns
                "father", "mother", "sister", "brother", "children", "fellow",
                "servant", "grandfather", "gentleman", "master"}
COLORS = {"black", "white", "red", "brown", "green", "blue", "gray", "grey", "gold"}
LOC_NOUNS = {"nest", "box", "cage", "pond", "bank", "rock", "pen", "log", "tree",
             "mat", "stand", "hill", "yard", "field", "barn", "roof", "wall", "road",
             "hand", "back", "head", "lap", "top", "web",
             # v4 -- 2nd-reader locations
             "door", "house", "hive", "street", "window", "cellar", "attic", "forest",
             "tent", "country", "trees"}
PREPS_LOC = {"in", "on", "under", "at", "by", "over", "near", "into", "onto"}
PREP_TO = {"to"}
PREP_OF_WITH = {"of", "with", "for"}
PRONOUNS_SUBJ_OBJ = {"he", "him", "she", "her", "it", "they", "them", "i", "you", "we", "us", "me"}
PRONOUNS_POSS = {"his", "her", "its", "their", "my", "your", "our"}
ACTION_HINTS = {"fed", "feed", "left", "ran", "run", "swim", "swam", "put", "catch",
                "caught", "likes", "like", "loves", "love", "get", "got", "drink",
                "sing", "sang", "sees", "see", "saw", "holds", "held", "bit", "bites",
                "sat", "sits", "stand", "stood", "hold", "gave", "give", "gives",
                "made", "make", "throw", "threw", "kicks", "kicked", "opened", "opens",
                "helps", "helped", "chased", "chases", "carries", "carried"}
AUX_LEMMAS = {"is", "am", "are", "was", "were", "be", "been", "being", "has", "have",
              "had", "will", "shall", "can", "could", "would", "should", "may", "might",
              "must", "do", "does", "did", "not", "let"}

_WN = None
_GROUND_CACHE = {}
_TAGGER = None


def _wn():
    global _WN
    if _WN is None:
        from nltk.corpus import wordnet as wn
        _WN = wn
    return _WN


def _tagger():
    global _TAGGER
    if _TAGGER is None:
        from nltk.tag import PerceptronTagger
        _TAGGER = PerceptronTagger()
    return _TAGGER


def ground_category(word):
    """Grounded semantic category of a KNOWN word (dictionary stand-in). Cached, deterministic.
    Returns one of PERSON / ANIMAL / LOCATION / COLOR / THING / None."""
    w = word.lower().strip(".,'\"!?;:")
    if w in _GROUND_CACHE:
        return _GROUND_CACHE[w]
    cat = None
    if w in NAME_GENDER or w in PERSON_NOUNS:
        cat = "PERSON"
    elif w in ANIMALS:
        cat = "ANIMAL"
    elif w in COLORS:
        cat = "COLOR"
    elif w in LOC_NOUNS:
        cat = "LOCATION"
    else:
        syns = _wn().synsets(w, pos="n")
        if not syns and w.endswith("s") and len(w) > 3:
            # depluralize (WordNet lemma is singular; e.g. 'eggs'->'egg', 'boys'->'boy')
            sing = w[:-2] if w.endswith("es") and w[:-2] in set(NAME_GENDER) | PERSON_NOUNS | ANIMALS | LOC_NOUNS else w[:-1]
            if sing in NAME_GENDER or sing in PERSON_NOUNS:
                cat = "PERSON"
            elif sing in ANIMALS:
                cat = "ANIMAL"
            elif sing in LOC_NOUNS:
                cat = "LOCATION"
            else:
                syns = _wn().synsets(sing, pos="n")
        if cat is None and syns:
            ln = syns[0].lexname()
            if ln == "noun.person":
                cat = "PERSON"
            elif ln == "noun.animal":
                cat = "ANIMAL"
            elif ln == "noun.location":
                cat = "LOCATION"
            else:
                cat = "THING"
    _GROUND_CACHE[w] = cat
    return cat


ANIMATE_CATS = {"PERSON", "ANIMAL"}


def is_animate(word):
    return ground_category(word) in ANIMATE_CATS


def grounded_gender_number(word, is_name):
    """Grounding-fed agreement for the UNMODIFIED overlay.observe(). Inanimate -> neuter;
    names -> curated gender; animals/persons -> gender unknown (compatible with he/she/it)."""
    w = word.lower().strip(".,'\"!?;:")
    number = "plural" if (w.endswith("s") and w in
                          ("eggs", "hens", "ducks", "boys", "girls", "birds", "them")) else "singular"
    if is_name:
        return NAME_GENDER.get(w, None), number
    cat = ground_category(w)
    if cat in ("PERSON", "ANIMAL"):
        return None, number
    if cat is not None and cat not in ("PERSON", "ANIMAL"):
        return "neuter", number
    return None, number


# =======================================================================================
# Tokenize + POS-tag. Candidate arguments = grounded nouns / names / subj-obj pronouns.
# =======================================================================================
_TOKEN_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")


# v4 RICHER-SENTENCE HANDLER (documented): clause-aware splitter. Splits on sentence punctuation
# AND word-identity-free coordinating/subordinating connectives, giving the grade-1 extractor its fair
# shot at grade-2 syntax. General (function-word cues only), NOT passage-tuned. The coref overlay still
# accumulates left-to-right across the resulting clauses (order preserved), so cross-clause coref holds.
_CLAUSE_SPLIT = re.compile(
    r"[.!?;:]+"
    r"|,\s+(?:and|but|or|for|so|when|while|as|which|who|that|though|until|because|after|before|near)\b"
    r"|\s+(?:but|when|while|though|until|because)\s+",
    re.IGNORECASE)


def split_sentences(text):
    parts = _CLAUSE_SPLIT.split(text)
    return [p.strip() for p in parts if p and p.strip()]


def tokenize(sentence):
    return [m.group(0) for m in _TOKEN_RE.finditer(sentence)]


def pos_tag_sentence(sentence):
    """Return list of (surface, low, pos) using NLTK PerceptronTagger (legal shallow tool)."""
    toks = tokenize(sentence)
    tagged = _tagger().tag(toks)
    out = []
    for surf, pos in tagged:
        low = surf.lower().strip(".,'\"!?;:")
        out.append((surf, low, pos))
    return out


# =======================================================================================
# WORD-IDENTITY-FREE feature extractor (the anti-memorization core). Each candidate
# argument gets a binary feature dict relative to the main verb of its sentence.
# =======================================================================================
def find_main_verb(tagged):
    """Return (verb_idx, verb_low, is_passive). Content verb wins over aux; 'has/have' is the
    verb only if no content verb; copula 'is/are/was/were' only if nothing else."""
    lows = [t[1] for t in tagged]
    n = len(tagged)
    # content verb = a VB* token whose lemma is not a pure auxiliary, OR an ACTION_HINT word.
    for i, (surf, low, pos) in enumerate(tagged):
        is_vb = pos.startswith("VB")
        if (is_vb and low not in AUX_LEMMAS) or (low in ACTION_HINTS):
            # passive: preceding was/were and this token is a past participle-ish
            is_passive = False
            for j in range(max(0, i - 3), i):
                if lows[j] in ("was", "were", "is", "are", "be", "been"):
                    if pos == "VBN" or low.endswith("ed") or low in ("fed", "held", "seen",
                                                                       "made", "put", "caught",
                                                                       "given", "left", "bit"):
                        is_passive = True
                    break
            return i, low, is_passive
    # possessive verb
    for i, (surf, low, pos) in enumerate(tagged):
        if low in ("has", "have", "had"):
            return i, "has", False
    # copula
    for i, (surf, low, pos) in enumerate(tagged):
        if low in ("is", "are", "was", "were"):
            return i, "is", False
    return None, None, False


FUNCTION_WORDS = (PREPS_LOC | PREP_TO | PREP_OF_WITH | AUX_LEMMAS | {
    "the", "a", "an", "this", "that", "these", "those", "and", "or", "but", "so",
    "there", "here", "five", "new", "old", "fat", "big", "little", "kind", "blind",
    "yes", "no", "too", "well", "fast", "not", "as", "if", "then", "what", "how"})
_NONNOUN_POS = {"IN", "DT", "CC", "TO", "MD", "VB", "VBD", "VBZ", "VBN", "VBG", "VBP",
                "JJ", "JJR", "JJS", "RB", "RBR", "RBS", "PRP$", "WDT", "WP", "WRB", "EX", "CD"}


def candidate_indices(tagged):
    """Indices of argument-candidate tokens: grounded nouns/names or subj/obj pronouns.
    Function words + possessive pronouns + possessive 's are handled structurally, not as args."""
    idx = []
    for i, (surf, low, pos) in enumerate(tagged):
        if low in PRONOUNS_POSS or low in FUNCTION_WORDS:
            continue
        if low in PRONOUNS_SUBJ_OBJ:
            idx.append(i)
            continue
        cat = ground_category(low)
        if cat == "COLOR":
            continue
        if pos in ("NN", "NNS", "NNP", "NNPS"):
            idx.append(i)
        elif cat in ("PERSON", "ANIMAL", "LOCATION", "THING") and pos in ("JJ", "JJR", "JJS") \
                and i > 0 and tagged[i - 1][2] == "DT":
            # POS-tagger error recovery: a GROUNDED concrete noun mis-tagged as an adjective while
            # in DETERMINER position ('The nest(JJS) has ...') is really the head noun. Word-identity-
            # free (uses grounding + determiner context, not the specific word). Fixes 'the nest has'.
            idx.append(i)
        elif cat is not None and pos not in _NONNOUN_POS:
            idx.append(i)
    return idx


# =======================================================================================
# MENTION GATE (the ONE variable). Selects which tokens are argument-candidate MENTIONS.
# Subj/obj pronouns are ALWAYS mentions in every mode (needed for coref-fed roles). The NOUN gate
# is what the mention_mode swaps. handrule = v4 candidate_indices VERBATIM (positive-control floor).
# Everything downstream of this selection (perceptron role assignment, relation emission, RELF1,
# Q-answering) is byte-identical across modes -> a clean one-variable oracle-mention test.
# =======================================================================================
NOUN_POS = ("NN", "NNS", "NNP", "NNPS")


def candidate_indices_mode(tagged, mention_mode, gold_heads):
    """Mention-gated argument candidates. mention_mode in {oracle, handrule, everyword, grounding}."""
    if mention_mode == "handrule":
        return candidate_indices(tagged)  # v4 VERBATIM (positive control)
    idx = []
    for i, (surf, low, pos) in enumerate(tagged):
        if low in PRONOUNS_POSS or low in FUNCTION_WORDS:
            continue
        if low in PRONOUNS_SUBJ_OBJ:
            idx.append(i)
            continue
        if mention_mode == "oracle":
            if low in gold_heads:
                idx.append(i)
        elif mention_mode == "everyword":
            if pos in NOUN_POS:
                idx.append(i)
        elif mention_mode == "grounding":
            cat = ground_category(low)
            if cat is not None and cat != "COLOR":
                idx.append(i)
        else:
            raise ValueError(f"unknown mention_mode {mention_mode!r}")
    return idx


def observe_as_mention(low, pos, mention_mode, gold_heads):
    """Should this NOUN/NAME token be observed as a coref antecedent? (pronouns handled separately.)
    handrule/grounding = v4 grounding gate; oracle = gold membership; everyword = any POS-noun."""
    if mention_mode == "oracle":
        return low in gold_heads
    if mention_mode == "everyword":
        return pos in NOUN_POS
    # handrule + grounding both use the v4 grounding observe-gate
    cat = ground_category(low)
    return cat is not None and cat != "COLOR"


def prev_prep(tagged, i):
    """The preposition immediately governing candidate i (scan left over a determiner)."""
    j = i - 1
    while j >= 0 and tagged[j][1] in ("the", "a", "an", "this", "that", "some", "five",
                                      "new", "old", "fat", "big", "little", "kind", "blind"):
        j -= 1
    if j >= 0 and tagged[j][1] in (PREPS_LOC | PREP_TO | PREP_OF_WITH):
        return tagged[j][1]
    return None


def candidate_features(tagged, i, verb_idx, is_passive, first_cand_idx):
    """WORD-IDENTITY-FREE feature dict for candidate token i. No token identity is used;
    only structural / POS / grounded-animacy / preposition / order cues -> the classifier
    cannot memorize a passage, only learn the multi-cue competition."""
    surf, low, pos = tagged[i]
    f = {"bias": 1.0}
    if verb_idx is not None:
        f["before_verb"] = 1.0 if i < verb_idx else 0.0
        f["after_verb"] = 1.0 if i > verb_idx else 0.0
        f["immediately_after_verb"] = 1.0 if i == verb_idx + 1 else 0.0
        d = abs(i - verb_idx)
        f["adjacent_to_verb"] = 1.0 if d == 1 else 0.0
        f["far_from_verb"] = 1.0 if d >= 3 else 0.0
    f["is_first_candidate"] = 1.0 if i == first_cand_idx else 0.0
    f["animate"] = 1.0 if is_animate(low) else 0.0
    f["inanimate"] = 1.0 if (ground_category(low) not in ANIMATE_CATS
                             and low not in PRONOUNS_SUBJ_OBJ) else 0.0
    f["is_pronoun"] = 1.0 if low in PRONOUNS_SUBJ_OBJ else 0.0
    f["is_proper"] = 1.0 if pos in ("NNP", "NNPS") else 0.0
    pp = prev_prep(tagged, i)
    f["prep_to"] = 1.0 if pp in PREP_TO else 0.0
    f["prep_loc"] = 1.0 if pp in PREPS_LOC else 0.0
    f["prep_by"] = 1.0 if pp == "by" else 0.0
    f["prep_ofwith"] = 1.0 if pp in PREP_OF_WITH else 0.0
    f["sentence_passive"] = 1.0 if is_passive else 0.0
    # interaction cues the competition model needs: passive-subject and by-agent
    f["passive_and_before_verb"] = 1.0 if (is_passive and verb_idx is not None and i < verb_idx) else 0.0
    f["passive_and_by"] = 1.0 if (is_passive and pp == "by") else 0.0
    return f


ROLES = ["AGENT", "PATIENT", "RECIPIENT", "LOCATION", "NONE"]


class AveragedPerceptron:
    """Deterministic multiclass averaged perceptron over interpretable features. The learned
    weights per (role, feature) ARE the competition-model cue weights -- fully inspectable."""

    def __init__(self):
        self.w = defaultdict(float)
        self._acc = defaultdict(float)
        self._t = 0

    def _score(self, role, feats):
        s = 0.0
        for name, val in feats.items():
            if val:
                s += self.w[(role, name)] * val
        return s

    def predict(self, feats):
        best, best_s = None, None
        for role in ROLES:  # fixed order -> deterministic argmax tie-break (first wins)
            s = self._score(role, feats)
            if best_s is None or s > best_s:
                best_s, best = s, role
        return best

    def _update(self, feats, gold, pred):
        for name, val in feats.items():
            if not val:
                continue
            self.w[(gold, name)] += val
            self.w[(pred, name)] -= val
            self._acc[(gold, name)] += self._t * val
            self._acc[(pred, name)] -= self._t * val

    def fit(self, examples, epochs):
        """examples: list of (feats, gold_role). Fixed-order passes (no shuffle) -> deterministic."""
        self._t = 0
        for _ep in range(epochs):
            for feats, gold in examples:
                self._t += 1
                pred = self.predict(feats)
                if pred != gold:
                    self._update(feats, gold, pred)
        # average
        for key, wv in list(self.w.items()):
            self.w[key] = wv - (self._acc[key] / self._t if self._t else 0.0)

    def top_weights(self, k=6):
        """Inspectable: top features per role (glass-box report)."""
        by_role = {r: [] for r in ROLES}
        for (role, name), wv in self.w.items():
            by_role[role].append((name, round(wv, 3)))
        for r in by_role:
            by_role[r] = sorted(by_role[r], key=lambda x: -abs(x[1]))[:k]
        return by_role


# =======================================================================================
# TRAINING corpus: labeled simple sentences covering the construction inventory
# (SV / SVO / SVOO / SVO-PP / passive / locative). Roles per head word. DISJOINT from the
# held-out test passages. Because features are word-identity-free, this teaches the cue
# competition, not the vocabulary. Labels are supervised SRL (drill-endorsed).
# =======================================================================================
# each: (sentence, {head_low: ROLE})  -- heads not named get NONE.
TRAIN = [
    # canonical active SVO (agent animate before verb, patient after)
    ("The boy fed the lamb", {"boy": "AGENT", "lamb": "PATIENT"}),
    ("A girl held the cat", {"girl": "AGENT", "cat": "PATIENT"}),
    ("The dog chased the fox", {"dog": "AGENT", "fox": "PATIENT"}),
    ("Sam sees the bird", {"sam": "AGENT", "bird": "PATIENT"}),
    ("The colt kicked the pig", {"colt": "AGENT", "pig": "PATIENT"}),
    ("Jane carried a lamp", {"jane": "AGENT", "lamp": "PATIENT"}),
    ("The hare bit the dog", {"hare": "AGENT", "dog": "PATIENT"}),
    ("A man made a cart", {"man": "AGENT", "cart": "PATIENT"}),
    ("The goat sees a boy", {"goat": "AGENT", "boy": "PATIENT"}),
    ("Will threw a ball", {"will": "AGENT", "ball": "PATIENT"}),
    # possessive 'has'
    ("The lad has a cap", {"lad": "AGENT", "cap": "PATIENT"}),
    ("A cat has a rat", {"cat": "AGENT", "rat": "PATIENT"}),
    ("Sam has a colt", {"sam": "AGENT", "colt": "PATIENT"}),
    # locative (subject figure + LOCATION ground after loc-prep)
    ("The cat sat on the mat", {"cat": "AGENT", "mat": "LOCATION"}),
    ("A frog is on the log", {"frog": "AGENT", "log": "LOCATION"}),
    ("The lamb ran in the field", {"lamb": "AGENT", "field": "LOCATION"}),
    ("A bird is in the tree", {"bird": "AGENT", "tree": "LOCATION"}),
    ("The pig sat by the barn", {"pig": "AGENT", "barn": "LOCATION"}),
    ("A hare hid under the rock", {"hare": "AGENT", "rock": "LOCATION"}),
    # SVO + locative together
    ("The boy put a ball in the box", {"boy": "AGENT", "ball": "PATIENT", "box": "LOCATION"}),
    ("A girl fed the hen in the yard", {"girl": "AGENT", "hen": "PATIENT", "yard": "LOCATION"}),
    ("Sam sees a fox on the hill", {"sam": "AGENT", "fox": "PATIENT", "hill": "LOCATION"}),
    # ditransitive: recipient after 'to' and double-object
    ("The man gave a hat to a lad", {"man": "AGENT", "hat": "PATIENT", "lad": "RECIPIENT"}),
    ("A girl gave the boy a doll", {"girl": "AGENT", "boy": "RECIPIENT", "doll": "PATIENT"}),
    ("Jane threw a ball to the dog", {"jane": "AGENT", "ball": "PATIENT", "dog": "RECIPIENT"}),
    ("The lad gave a bone to the pig", {"lad": "AGENT", "bone": "PATIENT", "pig": "RECIPIENT"}),
    # PASSIVE: subject = PATIENT, by-NP = AGENT (the multi-cue signal positional cannot get)
    ("The lamb was fed by the boy", {"lamb": "PATIENT", "boy": "AGENT"}),
    ("A cat was held by the girl", {"cat": "PATIENT", "girl": "AGENT"}),
    ("The fox was chased by a dog", {"fox": "PATIENT", "dog": "AGENT"}),
    ("A bird was seen by Sam", {"bird": "PATIENT", "sam": "AGENT"}),
    ("The pig was kicked by the colt", {"pig": "PATIENT", "colt": "AGENT"}),
    ("A ball was thrown by Will", {"ball": "PATIENT", "will": "AGENT"}),
    ("The hen was caught by a fox", {"hen": "PATIENT", "fox": "AGENT"}),
    ("A doll was made by Jane", {"doll": "PATIENT", "jane": "AGENT"}),
    # animate-object active (both animate -> position must carry it, agent still first)
    ("The man helps a boy", {"man": "AGENT", "boy": "PATIENT"}),
    ("A girl sees the lad", {"girl": "AGENT", "lad": "PATIENT"}),
    ("The dog bit a man", {"dog": "AGENT", "man": "PATIENT"}),
    ("A boy chased the girl", {"boy": "AGENT", "girl": "PATIENT"}),
    # intransitive (subject only)
    ("The lamb ran", {"lamb": "AGENT"}),
    ("A bird sang", {"bird": "AGENT"}),
    ("The boy sat", {"boy": "AGENT"}),
    # pronoun subject/object (coref feeds the head; roles same as nominal)
    ("He fed the cat", {"he": "AGENT", "cat": "PATIENT"}),
    ("A girl held it", {"girl": "AGENT", "it": "PATIENT"}),
    ("She sees the dog", {"she": "AGENT", "dog": "PATIENT"}),
    ("The boy gave it to her", {"boy": "AGENT", "it": "PATIENT", "her": "RECIPIENT"}),
]


def build_training_examples():
    """Turn labeled sentences into (features, gold_role) items via the REAL feature pipeline."""
    ex = []
    for sent, labels in TRAIN:
        tagged = pos_tag_sentence(sent)
        verb_idx, verb, passive = find_main_verb(tagged)
        cand = candidate_indices(tagged)
        first = cand[0] if cand else None
        for i in cand:
            feats = candidate_features(tagged, i, verb_idx, passive, first)
            gold = labels.get(tagged[i][1], "NONE")
            ex.append((feats, gold))
    return ex


# =======================================================================================
# REAL McGuffey SECOND READER test passages (VERBATIM; each cites its LESSON). Passages are
# NOT authored (the v3 limit the VET flagged) -- self_test asserts every clause is a substring
# of the cleaned corpus file. Only the comprehension QUESTIONS + GOLD are hand-authored
# (independent of the extractor; anti-circular). Chosen for a mix of single-hop / coref /
# competitive-coref / composition, across a representative range of real grade-2 syntax.
# =======================================================================================
TEST_PASSAGES = {
    # LESSON V TWO DOGS -- possession + topical(James) vs recent(Sport) competitive coref
    "L5_dogs": "James White has two dogs. His name is Sport. Sport is a good watchdog. "
               "In the daytime, James often uses Sport for his horse. He has a little wagon. "
               "He hitches Sport to this wagon, and drives over the country.",
    # LESSON V -- possessive 's + coref
    "L5b_dodger": "The name of James's Scotch terrier is Dodger. "
                  "Dodger has very bright eyes, and he does many funny things.",
    # LESSON XVIII KINGBIRD -- coref he->kingbird + nest-in-tree rel+rel composition
    "L18_king": "The kingbird is not bigger than a robin. He eats flies, and worms, and bugs, "
                "and berries. He builds his nest in a tree, near some house.",
    # LESSON XIV HENRY -- within-clause coref (His->Henry) + possession
    "L14_henry": "Henry was a kind, good boy. His father was dead, and his mother was very poor. "
                 "He had a little sister about two years old.",
    # LESSON XXIII TORN DOLL -- double coref (she->Mary, him->Dash)
    "L23_doll": "Mary ran about and played with Dash, her pet dog, and was having a happy time. "
                "She knew, at once, that Dash had done this, and she scolded him harshly.",
    # LESSON II BUBBLES -- location (PP-attachment: on the mat by the door)
    "L2_cat": "The old cat is asleep on the mat by the door.",
    # LESSON XXI BEE -- location single-hop
    "L21_bee": "Bees live in a house that is called a hive.",
    # LESSON LX BROKEN WINDOW -- coref He->George + svo chain
    "L60_geo": "George Ellet had a bright silver dollar for a New-year gift. "
               "He sent a ball at James Mason, but it missed him, and broke a window on the "
               "other side of the street.",
    # LESSON XXVIII SAM AND HARRY -- coref + possession (man's hat)
    "L28_sam": "The blind man stood, and held out his hat. His mother gave him some cents. "
               "Harry took them, but did not put them into the man's hat.",
    # LESSON VIII PUSS AND KITTENS -- possession + coref them->kittens
    "L8_puss": "Puss, with her three kittens, had lived in the coal cellar. "
               "Then the strange cat took the little kittens, one by one, and carried them to the attic.",
    # LESSON XXVI PATTY -- location + coref she->Patty
    "L26_patty": "Little Patty lives in a log house near a great forest. "
                 "She brought her bread and milk to eat under the trees.",
    # LESSON LVII GREEDY GIRL -- coref Her->Laura + possession
    "L57_laura": "Laura English is a greedy little girl. Her kitten never eats more than it needs.",
    # LESSON XXXII TIGER -- coref she->tigress
    "L32_tiger": "All at once, a large tigress bounded into the middle of the tent. "
                 "She caught her kitten by the neck, and broke the chain which bound it.",
    # LESSON XXXV WILLIE AND BOUNCE -- possession + coref his->Willie
    "L35_willie": "Two fast friends were Willie Brown and his little dog Bounce. "
                  "Willie taught his dog many cunning tricks.",
}

# Independent GOLD relation triples per passage (hand-annotated TRUTH; anti-circular; NOT emitted by
# the extractor). Canonical forms: ("svo", verb, agent, patient) ; ("loc", figure, ground) ;
# ("poss", owner, owned). RELF1 is micro-averaged over ALL passages below.
TEST_GOLD_RELS = {
    "L5_dogs": [("poss", "james", "dogs"), ("svo", "uses", "james", "sport"),
                ("poss", "james", "horse"), ("poss", "james", "wagon"),
                ("svo", "hitches", "james", "sport")],
    "L5b_dodger": [("poss", "dodger", "eyes")],
    "L18_king": [("poss", "kingbird", "nest"), ("loc", "nest", "tree")],
    "L14_henry": [("poss", "henry", "father"), ("poss", "henry", "mother"),
                  ("poss", "henry", "sister")],
    "L23_doll": [("svo", "scolded", "mary", "dash")],
    "L2_cat": [("loc", "cat", "mat")],
    "L21_bee": [("loc", "bees", "house")],
    "L60_geo": [("poss", "george", "dollar"), ("svo", "broke", "george", "window")],
    "L28_sam": [("svo", "took", "harry", "cents")],
    "L8_puss": [("poss", "puss", "kittens"), ("svo", "carried", "cat", "kittens")],
    "L26_patty": [("loc", "patty", "house")],
    "L57_laura": [("poss", "laura", "kitten")],
    "L32_tiger": [("svo", "caught", "tigress", "kitten")],
    "L35_willie": [("poss", "willie", "dog"), ("svo", "taught", "willie", "dog")],
}

# Comprehension questions on REAL passages. slice in {NC, CO, CC, CMP}. Each carries an
# arm-independent query spec (never contains the answer) + independent gold. NC=single-hop no-coref;
# CO=ordinary (non-competitive) coref; CC=competitive coref (recent competitor present); CMP=
# composition (2-edge join: cross-clause coref+relation, or rel+rel loc_of_owned). N_CMP >= 15.
TEST_QS = [
    # ---- NC single-hop (no coref) ----
    dict(qid="N1", p="L5_dogs", slice="NC", atype="AGENT", spec=("has_owner", "dogs"),
         gold="james", text="Who has two dogs?"),
    dict(qid="N2", p="L2_cat", slice="NC", atype="LOCATION", spec=("loc_ground", "cat"),
         gold="mat", text="Where is the cat?"),
    dict(qid="N3", p="L21_bee", slice="NC", atype="LOCATION", spec=("loc_ground", "bees"),
         gold="house", text="Where do bees live?"),
    dict(qid="N4", p="L60_geo", slice="NC", atype="AGENT", spec=("has_owner", "dollar"),
         gold="george", text="Who had a dollar?"),
    dict(qid="N5", p="L5b_dodger", slice="NC", atype="AGENT", spec=("has_owner", "eyes"),
         gold="dodger", text="Who has bright eyes?"),
    dict(qid="N6", p="L26_patty", slice="NC", atype="LOCATION", spec=("loc_ground", "patty"),
         gold="house", text="Where does Patty live?"),
    dict(qid="N7", p="L23_doll", slice="NC", atype="PATIENT", spec=("svo_patient", "scolded", "mary"),
         gold="dash", text="Whom did Mary scold?"),
    # ---- CO ordinary coref (non-competitive; within-clause His->Henry) ----
    dict(qid="O1", p="L14_henry", slice="CO", atype="AGENT", spec=("has_owner", "father"),
         gold="henry", text="Whose father was dead?"),
    dict(qid="O2", p="L14_henry", slice="CO", atype="AGENT", spec=("has_owner", "mother"),
         gold="henry", text="Whose mother was poor?"),
    dict(qid="O3", p="L14_henry", slice="CO", atype="AGENT", spec=("has_owner", "sister"),
         gold="henry", text="Who has a little sister?"),
    # ---- CC competitive coref (recent competitor present; maintained vs recency contrast) ----
    dict(qid="CC1", p="L5_dogs", slice="CC", atype="AGENT", spec=("has_owner", "wagon"),
         gold="james", text="Who has a wagon?"),      # He->James (topical) not Sport (recent)
    dict(qid="CC2", p="L23_doll", slice="CC", atype="AGENT", spec=("svo_agent", "scolded", "dash"),
         gold="mary", text="Who scolded Dash?"),
    dict(qid="CC3", p="L60_geo", slice="CC", atype="AGENT", spec=("svo_agent", "broke", "window"),
         gold="george", text="Who broke the window?"),
    dict(qid="CC4", p="L28_sam", slice="CC", atype="AGENT", spec=("svo_agent", "took", "cents"),
         gold="harry", text="Who took the cents?"),
    dict(qid="CC5", p="L8_puss", slice="CC", atype="AGENT", spec=("svo_agent", "carried", "kittens"),
         gold="cat", text="Who carried the kittens?"),
    # ---- CMP composition = 2-edge join (cross-clause coref+relation, or rel+rel) ; N_CMP=16 ----
    dict(qid="M1", p="L18_king", slice="CMP", atype="LOCATION", spec=("loc_of_owned", "kingbird", "nest"),
         gold="tree", text="Where is the kingbird's nest?"),          # rel+rel: poss+loc
    dict(qid="M2", p="L18_king", slice="CMP", atype="AGENT", spec=("has_owner", "nest"),
         gold="kingbird", text="Whose nest is in the tree?"),         # coref he->kingbird + poss
    dict(qid="M3", p="L5_dogs", slice="CMP", atype="PATIENT", spec=("svo_patient", "uses", "james"),
         gold="sport", text="What does James use as a horse?"),
    dict(qid="M4", p="L5_dogs", slice="CMP", atype="AGENT", spec=("svo_agent", "hitches", "sport"),
         gold="james", text="Who hitches Sport to the wagon?"),        # He->James cross-clause
    dict(qid="M5", p="L57_laura", slice="CMP", atype="AGENT", spec=("has_owner", "kitten"),
         gold="laura", text="Whose kitten eats little?"),              # Her->Laura + poss
    dict(qid="M6", p="L32_tiger", slice="CMP", atype="AGENT", spec=("svo_agent", "caught", "kitten"),
         gold="tigress", text="Who caught the kitten?"),               # She->tigress cross-clause
    dict(qid="M7", p="L32_tiger", slice="CMP", atype="AGENT", spec=("has_owner", "kitten"),
         gold="tigress", text="Whose kitten was on the chain?"),
    dict(qid="M8", p="L60_geo", slice="CMP", atype="PATIENT", spec=("svo_patient", "sent", "george"),
         gold="ball", text="What did George send?"),                   # He->George + svo
    dict(qid="M9", p="L8_puss", slice="CMP", atype="AGENT", spec=("has_owner", "kittens"),
         gold="puss", text="Who has three kittens?"),
    dict(qid="M10", p="L35_willie", slice="CMP", atype="AGENT", spec=("has_owner", "dog"),
         gold="willie", text="Who taught his dog tricks?"),            # his->Willie + poss
    dict(qid="M11", p="L35_willie", slice="CMP", atype="PATIENT", spec=("svo_patient", "taught", "willie"),
         gold="dog", text="What did Willie teach?"),
    dict(qid="M12", p="L5b_dodger", slice="CMP", atype="AGENT", spec=("has_owner", "terrier"),
         gold="james", text="Whose terrier is Dodger?"),               # possessive 's cross-phrase
    dict(qid="M13", p="L23_doll", slice="CMP", atype="AGENT", spec=("has_owner", "dog"),
         gold="mary", text="Whose pet dog is Dash?"),                  # her->Mary + poss
    dict(qid="M14", p="L28_sam", slice="CMP", atype="AGENT", spec=("has_owner", "hat"),
         gold="man", text="Whose hat was held out?"),
    dict(qid="M15", p="L28_sam", slice="CMP", atype="PATIENT", spec=("svo_patient", "gave", "mother"),
         gold="cents", text="What did his mother give?"),
    dict(qid="M16", p="L26_patty", slice="CMP", atype="PATIENT", spec=("svo_patient", "brought", "patty"),
         gold="bread", text="What did Patty bring?"),                  # She->Patty + svo
]

# =======================================================================================
# GOLD MENTION HEADS per passage (the ORACLE mention set). Hand-annotated INDEPENDENTLY by the
# referring-entity rule documented in the module docstring: a mention = the HEAD lemma of a CONCRETE
# referring discourse entity (person/animal/thing/place the narrative tracks). Subj/obj PRONOUNS are
# ALWAYS mentions (added automatically, not listed here). EXCLUDED (NOT listed): adjectives/colors/
# sizes/qualities, quantifiers/numerals, predicate adjectives + predicate nominals after a copula,
# relational/abstract/temporal non-entity nouns, and surname parts of multi-word proper names.
# ANTI-CIRCULAR: annotated by the linguistic rule, NOT to match the gold RELATIONS; concrete
# "distractor" nouns (flies/worms/bugs/berries) ARE included even though they hurt precision.
# Lemmas are the lowercased, punctuation-stripped surface forms the tokenizer/POS pipeline produces
# (e.g. plurals stay plural: dogs, kittens, eyes -- matching candidate `low`).
GOLD_MENTIONS = {
    # "James White has two dogs. His name is Sport. Sport is a good watchdog. In the daytime, James
    #  often uses Sport for his horse. He has a little wagon. He hitches Sport to this wagon, and
    #  drives over the country." (excl: white[surname], name, watchdog[pred-nom], daytime, two, good, little)
    "L5_dogs": {"james", "dogs", "sport", "horse", "wagon", "country"},
    # "The name of James's Scotch terrier is Dodger. Dodger has very bright eyes, and he does many
    #  funny things." (excl: name, scotch/bright[adj], james-owner via structural 's, things[vague])
    "L5b_dodger": {"terrier", "dodger", "eyes"},
    # "The kingbird is not bigger than a robin. He eats flies, and worms, and bugs, and berries. He
    #  builds his nest in a tree, near some house." (distractors flies/worms/bugs/berries INCLUDED)
    "L18_king": {"kingbird", "robin", "flies", "worms", "bugs", "berries", "nest", "tree", "house"},
    # "Henry was a kind, good boy. His father was dead, and his mother was very poor. He had a little
    #  sister about two years old." (excl: boy[pred-nom], kind/good/dead/poor/little, years)
    "L14_henry": {"henry", "father", "mother", "sister"},
    # "Mary ran about and played with Dash, her pet dog, and was having a happy time. She knew, at
    #  once, that Dash had done this, and she scolded him harshly." (excl: pet[mod], happy, time)
    "L23_doll": {"mary", "dash", "dog"},
    # "The old cat is asleep on the mat by the door." (excl: old, asleep)
    "L2_cat": {"cat", "mat", "door"},
    # "Bees live in a house that is called a hive." (excl: hive[naming pred-nom of house])
    "L21_bee": {"bees", "house"},
    # "George Ellet had a bright silver dollar for a New-year gift. He sent a ball at James Mason, but
    #  it missed him, and broke a window on the other side of the street." (excl: ellet/mason[surname],
    #  bright/silver, gift[role of dollar], year, side)
    "L60_geo": {"george", "dollar", "ball", "james", "window", "street"},
    # "The blind man stood, and held out his hat. His mother gave him some cents. Harry took them, but
    #  did not put them into the man's hat." (excl: blind, some)
    "L28_sam": {"man", "hat", "mother", "cents", "harry"},
    # "Puss, with her three kittens, had lived in the coal cellar. Then the strange cat took the little
    #  kittens, one by one, and carried them to the attic." (excl: three/coal/strange/little, one)
    "L8_puss": {"puss", "kittens", "cellar", "cat", "attic"},
    # "Little Patty lives in a log house near a great forest. She brought her bread and milk to eat
    #  under the trees." (excl: little/log/great)
    "L26_patty": {"patty", "house", "forest", "bread", "milk", "trees"},
    # "Laura English is a greedy little girl. Her kitten never eats more than it needs." (excl:
    #  english[surname], girl[pred-nom], greedy/little, more)
    "L57_laura": {"laura", "kitten"},
    # "All at once, a large tigress bounded into the middle of the tent. She caught her kitten by the
    #  neck, and broke the chain which bound it." (excl: large, middle, once)
    "L32_tiger": {"tigress", "tent", "kitten", "neck", "chain"},
    # "Two fast friends were Willie Brown and his little dog Bounce. Willie taught his dog many cunning
    #  tricks." (excl: two/fast, friends[pred-nom], brown[surname], little/cunning)
    "L35_willie": {"willie", "dog", "bounce", "tricks"},
}

# Modifier / non-entity blacklist -- the classic hand-rule FALSE POSITIVES + excluded classes. The
# self-test asserts these are DISJOINT from every gold-mention set (anti-error: catches accidental
# inclusion of a modifier/quantifier/predicate as a gold mention).
MODIFIER_BLACKLIST = {
    "great", "brown", "more", "silver", "little", "good", "old", "blind", "kind", "greedy", "strange",
    "dead", "poor", "asleep", "happy", "bright", "fast", "cunning", "large", "log", "coal", "scotch",
    "two", "three", "some", "one", "many", "new",
    "boy", "girl", "watchdog", "friends", "hive",  # predicate nominals in these passages
    "name", "daytime", "years", "time", "side", "middle", "once", "things", "pet",  # relational/abstract
    "white", "ellet", "mason", "english",  # surname parts
}

# CONTROL sets (authored minimal pairs, grade-1 vocab, clearly separated from TEST_REAL).
# Role-reversal proves role-SENSITIVITY (learned+positional pass; frequency fails).
# Passives prove the LEARNED multi-cue assigner beats the naive POSITIONAL shortcut.
REVERSAL_PAIRS = [
    ("The dog bit the man", "dog", "man"),
    ("The man bit the dog", "man", "dog"),
    ("The cat sees the rat", "cat", "rat"),
    ("The rat sees the cat", "rat", "cat"),
    ("A boy chased the girl", "boy", "girl"),
    ("A girl chased the boy", "girl", "boy"),
]  # (sentence, gold_agent, gold_patient)
PASSIVE_ITEMS = [
    ("The hen was fed by Ned", "ned", "hen"),
    ("The rat was seen by the cat", "cat", "rat"),
    ("The doll was held by Ann", "ann", "doll"),
    ("A boy was chased by the dog", "dog", "boy"),
    ("The lamb was caught by a fox", "fox", "lamb"),
]  # (sentence, gold_agent, gold_patient)


# =======================================================================================
# Extraction pipeline. Per passage: left-to-right pass feeds the REAL overlay for coref;
# per sentence, assign roles (learned OR positional) then emit relations with resolved heads.
# =======================================================================================
def assign_roles_learned(tagged, clf, mention_mode="handrule", gold_heads=frozenset()):
    """Return dict cand_idx -> role via the LEARNED classifier. mention_mode gates the candidates."""
    verb_idx, verb, passive = find_main_verb(tagged)
    cand = candidate_indices_mode(tagged, mention_mode, gold_heads)
    first = cand[0] if cand else None
    roles = {}
    for i in cand:
        feats = candidate_features(tagged, i, verb_idx, passive, first)
        roles[i] = clf.predict(feats)
    return roles, verb_idx, verb, passive, cand


def assign_roles_positional(tagged, mention_mode="handrule", gold_heads=frozenset()):
    """Naive positional shortcut (v1's approach = the must-beat): first candidate before verb
    = AGENT, first candidate after verb = PATIENT, 'to'-NP = RECIPIENT, loc-prep NP = LOCATION.
    Ignores passive + animacy (so it mis-assigns passives)."""
    verb_idx, verb, passive = find_main_verb(tagged)
    cand = candidate_indices_mode(tagged, mention_mode, gold_heads)
    roles = {}
    got_agent = got_patient = False
    for i in cand:
        pp = prev_prep(tagged, i)
        if pp in PREP_TO:
            roles[i] = "RECIPIENT"
        elif pp in PREPS_LOC:
            roles[i] = "LOCATION"
        elif verb_idx is not None and i < verb_idx and not got_agent:
            roles[i] = "AGENT"
            got_agent = True
        elif verb_idx is not None and i > verb_idx and not got_patient:
            roles[i] = "PATIENT"
            got_patient = True
        else:
            roles[i] = "NONE"
    return roles, verb_idx, verb, passive, cand


def extract_passage(passage_text, assigner_kind, clf, coref_strategy, mention_mode, gold_heads):
    """Run coref pass + role assignment; emit relation triples with resolved heads.
    assigner_kind: 'learned' or 'positional'. coref_strategy: None (OFF) or a WorkingOverlay strategy
    ('maintained' = the v3/v4 claim). mention_mode + gold_heads = the ONE variable (gate BOTH the
    coref observe loop AND the role-assigner candidates). Returns (rels, reslog)."""
    from hdlab.state_of_mind import WorkingOverlay, SetKnownBase, PRONOUN_SCOPE
    do_coref = coref_strategy is not None
    known = set()
    for txt in list(TEST_PASSAGES.values()):
        for s in split_sentences(txt):
            for _su, lo, _po in pos_tag_sentence(s):
                if ground_category(lo) is not None:
                    known.add(lo)
    ov = WorkingOverlay(base=SetKnownBase(known))
    rels = []
    reslog = []
    for sent in split_sentences(passage_text):
        tagged = pos_tag_sentence(sent)
        # ---- observe entities + resolve pronouns left-to-right (feeds coref) ----
        # First observe all nominal/name candidates and pronouns in order to build overlay state
        # BUT resolution must happen at the pronoun's position, so we interleave.
        pron_res = {}
        for i, (surf, low, pos) in enumerate(tagged):
            if low in PRONOUN_SCOPE:  # subj/obj/poss pronoun -> reference
                if do_coref and low not in ("i", "you", "we"):
                    ent = ov.resolve_pronoun(low, strategy=coref_strategy)
                    pron_res[i] = ent.head if ent is not None else None
                    reslog.append((low, pron_res[i]))
                sc = PRONOUN_SCOPE[low]
                ov.observe(low, is_pronoun=True, gender=sc["gender"], number=sc["number"])
            elif low in PRONOUNS_POSS:
                pass  # handled structurally below
            else:
                # MENTION GATE on the coref antecedent pool (the ONE variable). handrule/grounding =
                # v4 grounding gate; oracle = gold membership; everyword = any POS-noun.
                if not observe_as_mention(low, pos, mention_mode, gold_heads):
                    continue
                is_name = (low in NAME_GENDER) or (pos in ("NNP", "NNPS"))
                g, num = grounded_gender_number(low, is_name)
                ov.observe(low, gender=g, number=num, is_proper_name=is_name)
        # ---- role assignment (mention gate applied inside via mention_mode) ----
        if assigner_kind == "positional":
            roles, verb_idx, verb, passive, cand = assign_roles_positional(tagged, mention_mode, gold_heads)
        else:
            roles, verb_idx, verb, passive, cand = assign_roles_learned(tagged, clf, mention_mode, gold_heads)

        def head_of(i):
            surf, low, pos = tagged[i]
            if i in pron_res and pron_res[i] is not None:
                return pron_res[i]
            return low

        agents = [i for i in cand if roles.get(i) == "AGENT"]
        patients = [i for i in cand if roles.get(i) == "PATIENT"]
        recips = [i for i in cand if roles.get(i) == "RECIPIENT"]
        locs = [i for i in cand if roles.get(i) == "LOCATION"]
        subj_head = head_of(agents[0]) if agents else (head_of(cand[0]) if cand else None)
        # svo (ACTION verbs only; possessive 'has'/copula 'is' handled separately -> no svo(has,..))
        if verb is not None and agents and patients and verb not in ("has", "is"):
            for pi in patients:
                rels.append(("svo", verb, head_of(agents[0]), head_of(pi)))
        # copula 'is kind to X' -> svo(kind, subj, X): grade-1 predicate-adjective + recipient
        lows = [t[1] for t in tagged]
        if "kind" in lows and subj_head is not None:
            for i in cand:
                if roles.get(i) in ("PATIENT", "RECIPIENT", "LOCATION") or prev_prep(tagged, i) == "to":
                    if head_of(i) != subj_head:
                        rels.append(("svo", "kind", subj_head, head_of(i)))
        # possessive 'has/have/had' -> poss(owner, owned). v3 INANIMATE-POSSESSOR FIX: owner =
        # labeled AGENT if present, ELSE the first pre-verb candidate REGARDLESS OF ANIMACY. This
        # destructures ONLY the possessive relation (mirrors the possessive-'s / poss-pronoun
        # structural handlers below); THEMATIC roles of action verbs stay learned (animacy is a
        # genuine cue there). Fixes "The nest has eggs" -> poss(nest,eggs) and "The pen has a rat".
        if verb == "has" and patients:
            pre_verb = [i for i in cand if verb_idx is not None and i < verb_idx]
            owner_idx = agents[0] if agents else (pre_verb[0] if pre_verb else None)
            if owner_idx is not None:
                for pi in patients:
                    if pi != owner_idx:
                        rels.append(("poss", head_of(owner_idx), head_of(pi)))
        # recipient
        for ri in recips:
            if verb is not None and agents:
                rels.append(("recipient", verb, head_of(agents[0]), head_of(ri)))
        # locations: figure = subject (agent) else nearest preceding candidate
        for li in locs:
            figure = subj_head
            for j in cand:
                if j < li and roles.get(j) in ("AGENT", "PATIENT"):
                    figure = head_of(j)
            if figure is not None and figure != head_of(li):
                rels.append(("loc", figure, head_of(li)))
        # ---- structural (POS-driven, NOT learned): possessive 's, possessive-pronoun, color ----
        for i, (surf, low, pos) in enumerate(tagged):
            if "'" in surf and (surf.lower().endswith("'s")):
                owner = surf.split("'")[0].lower()
                # next candidate noun = owned
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        rels.append(("poss", owner, head_of(j)))
                        break
            if low in PRONOUNS_POSS and do_coref:
                if low in PRONOUN_SCOPE:
                    ent = ov.resolve_pronoun(low, strategy=coref_strategy)
                    owner = ent.head if ent is not None else low
                else:
                    owner = low
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        rels.append(("poss", owner, head_of(j)))
                        break
        # color attribute
        for i in range(len(tagged) - 1):
            if ground_category(tagged[i][1]) == "COLOR":
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        rels.append(("attr", head_of(j), tagged[i][1], "COLOR"))
                        break
    return sorted(set(rels), key=lambda r: (r[0], tuple(str(x) for x in r[1:]))), reslog


# =======================================================================================
# RELATION-F1 (held-out extraction quality) -- match extracted vs independent gold.
# =======================================================================================
def rel_prf(extracted, gold):
    """Set-based precision/recall/F1 over relation triples (svo/loc/poss). 'attr'/'recipient'
    excluded from the F1 gold set (gold has none) but not penalized: only score triple-kinds
    present in gold. We score svo/loc/poss which the gold uses."""
    kinds = {"svo", "loc", "poss"}
    ex = set(r for r in extracted if r[0] in kinds)
    go = set(r for r in gold if r[0] in kinds)
    if not go:
        return 1.0, 1.0, 1.0, 0, 0
    tp = len(ex & go)
    p = tp / len(ex) if ex else 0.0
    r = tp / len(go) if go else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
    return p, r, f1, tp, len(go)


# =======================================================================================
# Query engine (comprehension). SAME logic across arms; only the store differs.
# =======================================================================================
def _svo_agent(rels, verb, patient):
    for r in rels:
        if r[0] == "svo" and r[1] == verb and r[3] == patient:
            return r[2]
    return None


def _svo_patient(rels, verb, agent):
    for r in rels:
        if r[0] == "svo" and r[1] == verb and r[2] == agent:
            return r[3]
    return None


def _loc_ground(rels, figure):
    for r in rels:
        if r[0] == "loc" and r[1] == figure:
            return r[2]
    return None


def _has_owner(rels, owned):
    for r in rels:
        if r[0] == "poss" and r[2] == owned:
            return r[1]
    return None


def answer_reader(spec, rels):
    op = spec[0]
    if op == "svo_agent":
        return _svo_agent(rels, spec[1], spec[2])
    if op == "svo_patient":
        return _svo_patient(rels, spec[1], spec[2])
    if op == "loc_ground":
        return _loc_ground(rels, spec[1])
    if op == "has_owner":
        return _has_owner(rels, spec[1])
    if op == "loc_of_owned":
        owner, owned = spec[1], spec[2]
        if any(r[0] == "poss" and r[1] == owner and r[2] == owned for r in rels):
            return _loc_ground(rels, owned)
        return None
    if op == "owner_of_owned_chain":
        # 2-hop: poss(X, owned) ; poss(Y, X) -> Y  (whose NEST has the eggs -> bird)
        contained = spec[1]
        mids = [r[1] for r in rels if r[0] == "poss" and r[2] == contained]
        for mid in mids:
            for r in rels:
                if r[0] == "poss" and r[2] == mid:
                    return r[1]
        return None
    return None


def answer_frequency(atype, passage_text, spec):
    """No-relation grounded frequency baseline: most-frequent passage token of the answer TYPE.
    Order-insensitive -> cannot do role-reversal. Excludes query givens (anti-leak)."""
    given = set(str(x).lower() for x in spec[1:])
    counts = Counter()
    for s in split_sentences(passage_text):
        for _su, low, _po in pos_tag_sentence(s):
            if low in given:
                continue
            cat = ground_category(low)
            if cat is None:
                continue
            ok = False
            if atype == "AGENT" and cat in ANIMATE_CATS:
                ok = True
            elif atype == "PATIENT" and cat is not None:
                ok = True
            elif atype == "LOCATION" and cat == "LOCATION":
                ok = True
            if ok:
                counts[low] += 1
    if not counts:
        return None
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


def normalize(a):
    return None if a is None else str(a).lower().strip(".,'\"!?;:")


# =======================================================================================
# Control scoring: role-reversal + passive.
# =======================================================================================
def score_reversal(assigner, use_freq=False):
    """Fraction of reversal items with correct (agent, patient). use_freq: a bag-of-words proxy
    (agent = most-frequent animate, patient = other) -> order-insensitive -> fails reversal."""
    correct = 0
    per = []
    for sent, g_agent, g_patient in REVERSAL_PAIRS:
        tagged = pos_tag_sentence(sent)
        if use_freq:
            animates = [t[1] for t in tagged if is_animate(t[1])]
            pa = sorted(Counter(animates).items(), key=lambda kv: (-kv[1], kv[0]))
            pred_agent = pa[0][0] if pa else None
            pred_patient = pa[1][0] if len(pa) > 1 else None
        else:
            if assigner == "positional":
                roles, vi, v, ps, cand = assign_roles_positional(tagged)
            else:
                roles, vi, v, ps, cand = assigner(tagged)
            ag = [tagged[i][1] for i in cand if roles.get(i) == "AGENT"]
            pt = [tagged[i][1] for i in cand if roles.get(i) == "PATIENT"]
            pred_agent = ag[0] if ag else None
            pred_patient = pt[0] if pt else None
        ok = (pred_agent == g_agent and pred_patient == g_patient)
        correct += 1 if ok else 0
        per.append(dict(sent=sent, pred_agent=pred_agent, pred_patient=pred_patient,
                        gold_agent=g_agent, gold_patient=g_patient, ok=ok))
    return correct / len(REVERSAL_PAIRS), per


def score_passive(assigner):
    """Fraction of passive items with correct (agent, patient)."""
    correct = 0
    per = []
    for sent, g_agent, g_patient in PASSIVE_ITEMS:
        tagged = pos_tag_sentence(sent)
        if assigner == "positional":
            roles, vi, v, ps, cand = assign_roles_positional(tagged)
        else:
            roles, vi, v, ps, cand = assigner(tagged)
        ag = [tagged[i][1] for i in cand if roles.get(i) == "AGENT"]
        pt = [tagged[i][1] for i in cand if roles.get(i) == "PATIENT"]
        pred_agent = ag[0] if ag else None
        pred_patient = pt[0] if pt else None
        ok = (pred_agent == g_agent and pred_patient == g_patient)
        correct += 1 if ok else 0
        per.append(dict(sent=sent, pred_agent=pred_agent, pred_patient=pred_patient,
                        gold_agent=g_agent, gold_patient=g_patient, ok=ok))
    return correct / len(PASSIVE_ITEMS), per


# =======================================================================================
# Arms = MENTION MODES. ONE variable = the mention gate; role-assigner (learned) + coref
# ('maintained') held FIXED across all mention arms. 'frequency' is a mention-independent Q-slice
# floor reference. Contrast: oracle vs handrule = GOLD mentions vs v4 hand-rule mentions.
# =======================================================================================
MENTION_ARMS = ["oracle", "handrule", "everyword", "grounding"]
FIXED_COREF_STRATEGY = "maintained"  # v4 claim strategy; NOT tuned (mention set is the variable)


def run_mention_arm(mention_mode, clf):
    """mention_mode in MENTION_ARMS. learned role-assigner + maintained coref FIXED; only the mention
    gate differs. Returns (per_q_correct, answers, stores, reslogs)."""
    stores = {}
    reslogs = {}
    for pid, text in TEST_PASSAGES.items():
        gold_heads = GOLD_MENTIONS.get(pid, frozenset())
        rels, rlog = extract_passage(text, "learned", clf, FIXED_COREF_STRATEGY, mention_mode, gold_heads)
        stores[pid] = rels
        reslogs[pid] = rlog
    correct = []
    answers = []
    for q in TEST_QS:
        ans = answer_reader(q["spec"], stores[q["p"]])
        na, ng = normalize(ans), normalize(q["gold"])
        correct.append(1 if (na is not None and na == ng) else 0)
        answers.append(na)
    return correct, answers, stores, reslogs


def run_frequency_floor(clf):
    """Mention-independent grounded-frequency Q floor (v4 frequency arm). Returns (correct, answers)."""
    correct = []
    answers = []
    for q in TEST_QS:
        ans = answer_frequency(q["atype"], TEST_PASSAGES[q["p"]], q["spec"])
        na, ng = normalize(ans), normalize(q["gold"])
        correct.append(1 if (na is not None and na == ng) else 0)
        answers.append(na)
    return correct, answers


def slice_acc(correct, sl):
    idx = [i for i, q in enumerate(TEST_QS) if q["slice"] == sl]
    if not idx:
        return 0.0, 0
    return sum(correct[i] for i in idx) / len(idx), len(idx)


def acc(correct):
    return sum(correct) / len(correct) if correct else 0.0


def bootstrap_lift_p(ca, cb, idx, rng, n_boot=N_BOOT):
    if not idx:
        return 1.0, 0.0
    diffs = [ca[i] - cb[i] for i in idx]
    n = len(diffs)
    obs = sum(diffs) / n
    le0 = 0
    for _ in range(n_boot):
        s = sum(diffs[rng.randrange(n)] for _ in range(n))
        if (s / n) <= 0:
            le0 += 1
    return le0 / n_boot, obs


# =======================================================================================
# Markers / metrics / crash-diagnostic (atomic).
# =======================================================================================
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=f"{type(exc).__name__}: {str(exc)[:500]}",
                summary=f"CELL_CRASHED: {type(exc).__name__}", elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
                anchor_name=ANCHOR_NAME)
    _write_metrics(output_dir, diag)


def _arms_must_differ(named_outputs):
    digests = {}
    for name, out in named_outputs.items():
        b = json.dumps(out, sort_keys=True).encode("utf-8")
        digests[name] = hashlib.sha256(b).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            assert digests[names[i]] != digests[names[j]], \
                f"META_RULE_AF VIOLATION: arms {names[i]!r} and {names[j]!r} bit-identical"
    return digests


# =======================================================================================
# Verdict.
# =======================================================================================
def _relf1_for_store(store):
    """Micro-averaged RELF1 (svo/loc/poss) over ALL real passages for one mention arm's store."""
    tot_tp = tot_ex = tot_go = 0
    per_p = {}
    for pid in TEST_GOLD_RELS:
        p, r, f1, tp, ngo = rel_prf(store[pid], TEST_GOLD_RELS[pid])
        per_p[pid] = dict(precision=round(p, 3), recall=round(r, 3), f1=round(f1, 3),
                          tp=tp, n_gold=ngo, extracted=[list(x) for x in store[pid]])
        ex_k = set(x for x in store[pid] if x[0] in ("svo", "loc", "poss"))
        go_k = set(x for x in TEST_GOLD_RELS[pid] if x[0] in ("svo", "loc", "poss"))
        tot_tp += len(ex_k & go_k)
        tot_ex += len(ex_k)
        tot_go += len(go_k)
    P = tot_tp / tot_ex if tot_ex else 0.0
    R = tot_tp / tot_go if tot_go else 0.0
    F = 2 * P * R / (P + R) if (P + R) > 0 else 0.0
    return dict(micro_precision=round(P, 3), micro_recall=round(R, 3), micro_f1=round(F, 3),
                tp=tot_tp, n_extracted=tot_ex, n_gold=tot_go, per_passage=per_p)


def _slices(correct):
    """Q-slice accuracies + counts for one mention arm's per-Q correctness list."""
    d = {}
    for sl in ("NC", "CO", "CC", "CMP"):
        a, n = slice_acc(correct, sl)
        d[sl] = round(a, 4)
        d["n_" + sl] = n
    d["all"] = round(acc(correct), 4)
    return d


def _mention_report():
    """Per-passage NOUN-head mention set per mode + the handrule-vs-oracle set DIFF (the concrete
    evidence of WHAT the mention gate changed). Pronouns excluded for readability."""
    rep = {}
    counts = {mm: 0 for mm in MENTION_ARMS}
    for pid, text in TEST_PASSAGES.items():
        gh = GOLD_MENTIONS.get(pid, frozenset())
        per = {}
        for mm in MENTION_ARMS:
            heads = set()
            for sent in split_sentences(text):
                tagged = pos_tag_sentence(sent)
                for i in candidate_indices_mode(tagged, mm, gh):
                    low = tagged[i][1]
                    if low not in PRONOUNS_SUBJ_OBJ:
                        heads.add(low)
            per[mm] = sorted(heads)
            counts[mm] += len(heads)
        hr, orc = set(per["handrule"]), set(per["oracle"])
        per["handrule_only_vs_oracle"] = sorted(hr - orc)   # v4 FALSE-POSITIVE mentions (garbage)
        per["oracle_only_vs_handrule"] = sorted(orc - hr)   # mentions v4 MISSED
        rep[pid] = per
    return rep, counts


def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    rng = random.Random(SEED)

    # ---- FIT the learned role-assigner on the TRAINING grammar (held-out test never seen) ----
    clf = AveragedPerceptron()
    train_ex = build_training_examples()
    clf.fit(train_ex, epochs=N_EPOCHS)

    # ---- MENTION ARMS (oracle / handrule / everyword / grounding): learned role-assigner +
    #      maintained coref FIXED; only the mention gate differs. + a mention-independent freq floor.
    corrects = {}
    answers = {}
    stores = {}
    reslogs = {}
    for mm in MENTION_ARMS:
        c, a, st, rl = run_mention_arm(mm, clf)
        corrects[mm] = c
        answers[mm] = a
        stores[mm] = st
        reslogs[mm] = rl
    fr_c, fr_a = run_frequency_floor(clf)

    # ARMS-MUST-DIFFER across mention modes (answers differ -> mention gate is not vacuous).
    digests = _arms_must_differ({mm: answers[mm] for mm in MENTION_ARMS})

    # ---- RELF1 + Q-slices per mention arm ----
    relf1 = {mm: _relf1_for_store(stores[mm]) for mm in MENTION_ARMS}
    sl = {mm: _slices(corrects[mm]) for mm in MENTION_ARMS}
    fr_sl = _slices(fr_c)

    o, h = relf1["oracle"], relf1["handrule"]
    oF, oP, oR = o["micro_f1"], o["micro_precision"], o["micro_recall"]
    hF, hP, hR = h["micro_f1"], h["micro_precision"], h["micro_recall"]
    o_cmp, h_cmp = sl["oracle"]["CMP"], sl["handrule"]["CMP"]
    o_cc, h_cc = sl["oracle"]["CC"], sl["handrule"]["CC"]
    o_co, h_co = sl["oracle"]["CO"], sl["handrule"]["CO"]
    o_nc, h_nc = sl["oracle"]["NC"], sl["handrule"]["NC"]
    o_all, h_all = sl["oracle"]["all"], sl["handrule"]["all"]

    # ---- DELTAS (oracle - handrule) = how much of the v4 collapse was MENTION-STARVATION ----
    d_f1, d_precision, d_recall = round(oF - hF, 4), round(oP - hP, 4), round(oR - hR, 4)
    d_cmp, d_cc, d_co, d_nc = round(o_cmp - h_cmp, 4), round(o_cc - h_cc, 4), round(o_co - h_co, 4), round(o_nc - h_nc, 4)
    d_all = round(o_all - h_all, 4)

    # ---- bootstrap p (oracle > handrule) on CMP / CC / all-Q ----
    cmp_idx = [i for i, q in enumerate(TEST_QS) if q["slice"] == "CMP"]
    cc_idx = [i for i, q in enumerate(TEST_QS) if q["slice"] == "CC"]
    all_idx = list(range(len(TEST_QS)))
    p_cmp, obs_cmp = bootstrap_lift_p(corrects["oracle"], corrects["handrule"], cmp_idx, rng)
    p_cc, obs_cc = bootstrap_lift_p(corrects["oracle"], corrects["handrule"], cc_idx, rng)
    p_all, obs_all = bootstrap_lift_p(corrects["oracle"], corrects["handrule"], all_idx, rng)

    # ---- mention-set report + telemetry ----
    ment_rep, ment_counts = _mention_report()
    oracle_handrule_sets_differ = any(
        ment_rep[pid]["handrule_only_vs_oracle"] or ment_rep[pid]["oracle_only_vs_handrule"]
        for pid in ment_rep)
    telemetry_moved = (abs(d_f1) >= TELEMETRY_MIN_MOVE or abs(d_cmp) >= TELEMETRY_MIN_MOVE
                       or abs(d_cc) >= TELEMETRY_MIN_MOVE or abs(d_recall) >= TELEMETRY_MIN_MOVE
                       or answers["oracle"] != answers["handrule"])

    # ---- POSITIVE-CONTROL (Gate D reproduce_prior): handrule reproduces the v4 pipeline ----
    reproduce_f1_ok = abs(hF - V4_HANDRULE_RELF1_F1) <= REPRODUCE_TOL_F1
    reproduce_cmp_ok = abs(h_cmp - V4_HANDRULE_CMP) <= REPRODUCE_TOL_SLICE
    reproduce_cc_ok = abs(h_cc - V4_HANDRULE_CC) <= REPRODUCE_TOL_SLICE
    reproduce_nc_ok = abs(h_nc - V4_HANDRULE_NC) <= REPRODUCE_TOL_SLICE
    positive_control_ok = reproduce_f1_ok and reproduce_cmp_ok and reproduce_cc_ok and reproduce_nc_ok

    # ---- baseline-in-band (frequency floor must be a real, non-saturated baseline) ----
    fr_all = fr_sl["all"]
    baseline_in_band = BASELINE_BAND[0] < fr_all < BASELINE_BAND[1]

    # ---- DIAGNOSTIC BRANCH (pre-registered) ----
    confirmed = (oF >= CONF_RELF1_F1 and oR >= CONF_RELF1_RECALL and o_cmp >= CONF_CMP and o_cc >= CONF_CC)
    refuted = (oF < REF_RELF1_F1 and o_cc <= REF_CC)

    if not positive_control_ok:
        verdict = "HARD_FAIL_REPRODUCE"
        vmsg = (f"POSITIVE-CONTROL FAIL: handrule arm did NOT reproduce v4 at test regime -- "
                f"RELF1_F1={hF:.3f} (v4={V4_HANDRULE_RELF1_F1}, tol={REPRODUCE_TOL_F1}); "
                f"CMP={h_cmp:.3f} (v4={V4_HANDRULE_CMP}); CC={h_cc:.3f} (v4={V4_HANDRULE_CC}); "
                f"NC={h_nc:.3f} (v4={V4_HANDRULE_NC}). Oracle injection is NOT one-variable off real v4 -> "
                f"do NOT trust the oracle delta until the reproduce is fixed.")
    elif confirmed:
        verdict = "STARVATION_CONFIRMED"
        vmsg = (f"MENTION-STARVATION CONFIRMED: GOLD mentions RECOVER the machinery -- oracle "
                f"RELF1_F1={oF:.3f} (P={oP:.3f} R={oR:.3f}) vs handrule floor {hF:.3f}; CMP {o_cmp:.3f} "
                f"vs {h_cmp:.3f} (d={d_cmp:+.3f}); CC {o_cc:.3f} vs {h_cc:.3f} (d={d_cc:+.3f}); NC "
                f"{o_nc:.3f} vs {h_nc:.3f}. Mention detection IS the bottleneck -> a learned mention-"
                f"detector is the worthwhile cheap fix; recovered numbers = the prize ceiling. "
                f"CLAIM-VET-pending.")
    elif refuted:
        verdict = "STARVATION_REFUTED"
        vmsg = (f"MENTION-STARVATION REFUTED: even with GOLD mentions the downstream stays poor -- "
                f"oracle RELF1_F1={oF:.3f} (P={oP:.3f} R={oR:.3f}); CC={o_cc:.3f} (d={d_cc:+.3f}); "
                f"CMP={o_cmp:.3f} (d={d_cmp:+.3f}). The role-assigner/coref/composition have their OWN "
                f"real-text failures a mention-detector alone cannot fix -> the learned-parser plan must "
                f"go DEEPER than mentions. CLAIM-VET-pending.")
    else:
        verdict = "STARVATION_PARTIAL"
        vmsg = (f"MENTION-STARVATION PARTIAL: GOLD mentions HELP but do NOT fully recover -- oracle "
                f"RELF1_F1={oF:.3f} (P={oP:.3f} R={oR:.3f}) vs handrule {hF:.3f} (dF1={d_f1:+.3f}, "
                f"dRecall={d_recall:+.3f}); CMP {o_cmp:.3f} vs {h_cmp:.3f} (d={d_cmp:+.3f}); CC {o_cc:.3f} "
                f"vs {h_cc:.3f} (d={d_cc:+.3f}); NC {o_nc:.3f} vs {h_nc:.3f}. Mentions are NECESSARY but "
                f"not SUFFICIENT: residual downstream failures remain (see per-passage extracted). "
                f"CLAIM-VET-pending.")

    elapsed = time.perf_counter() - t0
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: oracle RELF1_F1={oF:.3f}(P={oP:.3f}/R={oR:.3f}) vs handrule {hF:.3f}; "
                 f"CMP {o_cmp:.3f}/{h_cmp:.3f} CC {o_cc:.3f}/{h_cc:.3f} NC {o_nc:.3f}/{h_nc:.3f}; "
                 f"reproduce_ok={positive_control_ok}"),
        diagnostic=True,
        elapsed_s=round(elapsed, 4), ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED, n_boot=N_BOOT,
        n_train_sentences=len(TRAIN), n_train_examples=len(train_ex), n_epochs=N_EPOCHS,
        n_test_passages=len(TEST_PASSAGES), n_questions=len(TEST_QS),
        heldout_source="mcguffey_second_reader.clean.txt -- ALL passages VERBATIM real text (provenance-verified); questions hand-authored",
        one_variable="mention_mode (oracle/handrule/everyword/grounding); role-assigner=learned + coref=maintained held FIXED",
        arms={mm: dict(acc_all=sl[mm]["all"], acc_NC=sl[mm]["NC"], acc_CO=sl[mm]["CO"],
                       acc_CC=sl[mm]["CC"], acc_CMP=sl[mm]["CMP"], per_q=corrects[mm], answers=answers[mm])
              for mm in MENTION_ARMS},
        frequency_floor=dict(acc_all=fr_sl["all"], acc_NC=fr_sl["NC"], acc_CO=fr_sl["CO"],
                             acc_CC=fr_sl["CC"], acc_CMP=fr_sl["CMP"], per_q=fr_c, answers=fr_a),
        relation_f1=relf1,
        deltas_oracle_minus_handrule=dict(
            relf1_f1=d_f1, relf1_precision=d_precision, relf1_recall=d_recall,
            CMP=d_cmp, CC=d_cc, CO=d_co, NC=d_nc, all_Q=d_all,
            cmp_p_oracle_le_handrule=p_cmp, cc_p_oracle_le_handrule=p_cc, all_p_oracle_le_handrule=p_all),
        diagnostic_thresholds=dict(
            CONF_RELF1_F1=CONF_RELF1_F1, CONF_RELF1_RECALL=CONF_RELF1_RECALL, CONF_CMP=CONF_CMP,
            CONF_CC=CONF_CC, REF_RELF1_F1=REF_RELF1_F1, REF_CC=REF_CC,
            confirmed=confirmed, refuted=refuted),
        positive_control=dict(
            v4_handrule_relf1_f1=V4_HANDRULE_RELF1_F1, measured_handrule_relf1_f1=hF, reproduce_f1_ok=reproduce_f1_ok,
            v4_handrule_cmp=V4_HANDRULE_CMP, measured_handrule_cmp=h_cmp, reproduce_cmp_ok=reproduce_cmp_ok,
            v4_handrule_cc=V4_HANDRULE_CC, measured_handrule_cc=h_cc, reproduce_cc_ok=reproduce_cc_ok,
            v4_handrule_nc=V4_HANDRULE_NC, measured_handrule_nc=h_nc, reproduce_nc_ok=reproduce_nc_ok,
            positive_control_ok=positive_control_ok, reproduce_tol_f1=REPRODUCE_TOL_F1, reproduce_tol_slice=REPRODUCE_TOL_SLICE),
        mention_report=ment_rep,
        mention_head_counts=ment_counts,
        learned_weights_top=clf.top_weights(6),
        coref_resolutions_oracle={pid: rl for pid, rl in reslogs["oracle"].items()},
        coref_resolutions_handrule={pid: rl for pid, rl in reslogs["handrule"].items()},
        slice_counts=dict(NC=sl["oracle"]["n_NC"], CO=sl["oracle"]["n_CO"],
                          CC=sl["oracle"]["n_CC"], CMP=sl["oracle"]["n_CMP"]),
        gates=dict(positive_control_ok=positive_control_ok, telemetry_moved=telemetry_moved,
                   oracle_handrule_sets_differ=oracle_handrule_sets_differ,
                   baseline_in_band=baseline_in_band, freq_acc_all=fr_all,
                   arms_differ_verified=True, arm_digests=digests),
        questions=[dict(qid=q["qid"], p=q["p"], slice=q["slice"], gold=q["gold"], text=q["text"],
                        oracle=answers["oracle"][i], handrule=answers["handrule"][i],
                        everyword=answers["everyword"][i], grounding=answers["grounding"][i],
                        frequency=fr_a[i]) for i, q in enumerate(TEST_QS)],
        provenance="passages=VERBATIM mcguffey_second_reader.clean.txt (real, provenance-verified); "
                   "ONE variable=mention_mode (oracle GOLD mentions vs v4 handrule); downstream "
                   "byte-identical to v4 (AveragedPerceptron role-assigner + WorkingOverlay maintained "
                   "coref + relation emission + RELF1 + Q-engine); RELF1 gold is SPARSE so PRECISION is "
                   "gold-coverage-limited -- lead with RECALL + Q-slices; gold mentions independent of "
                   "comprehension gold (anti-circular).",
    )
    return metrics


# =======================================================================================
# Self-test (EXERCISES the REAL overlay + REAL perceptron fit + REAL POS tagger).
# =======================================================================================
def self_test():
    import inspect
    from hdlab.state_of_mind import WorkingOverlay, SetKnownBase, PRONOUN_SCOPE

    # F.2 substrate_signature: bind against LIVE overlay signatures (base/stable kwargs only).
    for kw in ("base",):
        assert kw in inspect.signature(WorkingOverlay.__init__).parameters
    for kw in ("head", "is_pronoun", "gender", "number", "is_proper_name"):
        assert kw in inspect.signature(WorkingOverlay.observe).parameters
    for kw in ("strategy",):
        assert kw in inspect.signature(WorkingOverlay.resolve_pronoun).parameters

    # F.1 real_code_path: fit the REAL perceptron on the REAL training grammar.
    clf = AveragedPerceptron()
    ex = build_training_examples()
    assert len(ex) > 40, f"expected many training examples, got {len(ex)}"
    clf.fit(ex, epochs=N_EPOCHS)

    # The learned assigner must get canonical active SVO right on a NON-training sentence.
    tagged = pos_tag_sentence("The pig fed the goat")
    roles, vi, v, ps, cand = assign_roles_learned(tagged, clf)
    heads = {tagged[i][1]: roles[i] for i in cand}
    assert heads.get("pig") == "AGENT", f"self-test: pig should be AGENT, got {heads}"
    assert heads.get("goat") == "PATIENT", f"self-test: goat should be PATIENT, got {heads}"

    # PASSIVE (the multi-cue signal): 'The goat was fed by the pig' -> agent=pig, patient=goat.
    tagged = pos_tag_sentence("The goat was fed by the pig")
    roles, vi, v, ps, cand = assign_roles_learned(tagged, clf)
    heads = {tagged[i][1]: roles[i] for i in cand}
    assert ps is True, f"self-test: sentence should be detected passive, got passive={ps}"
    assert heads.get("pig") == "AGENT", f"self-test passive: pig(by) should be AGENT, got {heads}"
    assert heads.get("goat") == "PATIENT", f"self-test passive: goat(subj) should be PATIENT, got {heads}"

    # POSITIONAL baseline must MISS the passive (agent=goat) -> the differentiator is real.
    proles, pvi, pv, pps, pcand = assign_roles_positional(tagged)
    pheads = {tagged[i][1]: proles[i] for i in pcand}
    assert pheads.get("goat") == "AGENT", f"self-test: positional should MIS-assign passive, got {pheads}"

    # F.1 real overlay: competitive coref on a held-out-style item -- him -> man (gender), NOT Mary.
    ov = WorkingOverlay(base=SetKnownBase({"man", "mary"}))
    ov.observe("man", gender=None, number="singular", is_proper_name=False)
    ov.observe("mary", gender="fem", number="singular", is_proper_name=True)
    ent = ov.resolve_pronoun("him", strategy="maintained")  # him = masc -> man (Mary excluded by gender)
    assert ent is not None and ent.head == "man", \
        f"self-test: 'him' should resolve to man not Mary (gender>recency), got {ent}"

    # v3 CRUX-2: MAINTAINED beats RECENCY on a competitive (topical) case -- topic mentioned twice
    # (distant), distractor once (recent, same gender): recency -> distractor, maintained -> topic.
    ov2 = WorkingOverlay(base=SetKnownBase({"ann", "kate"}))
    ov2.observe("ann", gender="fem", number="singular", is_proper_name=True)  # topic mention 1
    ov2.observe("ann", gender="fem", number="singular", is_proper_name=True)  # topic mention 2
    ov2.observe("kate", gender="fem", number="singular", is_proper_name=True)  # recent distractor
    e_maint = ov2.resolve_pronoun("she", strategy="maintained")
    e_rec = ov2.resolve_pronoun("she", strategy="recency")
    assert e_maint is not None and e_maint.head == "ann", f"self-test: maintained 'she'->ann, got {e_maint}"
    assert e_rec is not None and e_rec.head == "kate", f"self-test: recency 'she'->kate, got {e_rec}"

    # v4 PROVENANCE GATE (the wild-text fix): every passage CLAUSE must be a VERBATIM substring of the
    # cleaned McGuffey 2nd-reader corpus -> proves the passages were NOT authored (anti-circular).
    with open(CORPUS_PATH, encoding="utf-8") as fh:
        corpus_norm = re.sub(r"\s+", " ", fh.read())
    n_clauses = 0
    for pid, text in TEST_PASSAGES.items():
        for clause in split_sentences(text):
            cn = re.sub(r"\s+", " ", clause).strip()
            assert cn in corpus_norm, f"self-test PROVENANCE: passage {pid} clause not verbatim: {cn!r}"
            n_clauses += 1
    assert n_clauses >= 20, f"self-test: expected many real clauses, got {n_clauses}"

    # real_code_path: the assembled reader runs on REAL 2nd-reader text via the NEW mention-gated
    # extract_passage (handrule mode == v4). loc(bees,house) must fire (extraction not vacuous).
    rels_bee, _ = extract_passage(TEST_PASSAGES["L21_bee"], "learned", clf, "maintained", "handrule",
                                  GOLD_MENTIONS.get("L21_bee", frozenset()))
    assert ("loc", "bees", "house") in rels_bee, f"self-test: loc(bees,house) should extract (handrule), got {rels_bee}"

    # ORACLE gold-mention VALIDITY: every gold head occurs as a token in its passage (no typos/ghosts).
    for pid, heads in GOLD_MENTIONS.items():
        toks = set()
        for sent in split_sentences(TEST_PASSAGES[pid]):
            for _s, lo, _p in pos_tag_sentence(sent):
                toks.add(lo)
        for gm in heads:
            assert gm in toks, f"self-test GOLD: '{gm}' not a token in passage {pid} (tokens={sorted(toks)})"

    # ANTI-ERROR (anti-gaming): the classic false-positive modifiers / quantifiers / predicate nominals
    # / surname parts are DISJOINT from every gold mention set.
    all_gold = set().union(*GOLD_MENTIONS.values())
    bad = all_gold & MODIFIER_BLACKLIST
    assert not bad, f"self-test GOLD: modifier/non-entity wrongly annotated as a mention: {sorted(bad)}"

    # TELEMETRY-SENSITIVE + ONE-VARIABLE: swapping the mention gate MUST move the extracted relations
    # on a real passage (oracle vs handrule differ). L60_geo has mis-grounded handrule mentions
    # (silver/year/gift -> owned) the oracle drops -> the two extractions must differ.
    rk_o, _ = extract_passage(TEST_PASSAGES["L60_geo"], "learned", clf, "maintained", "oracle",
                              GOLD_MENTIONS["L60_geo"])
    rk_h, _ = extract_passage(TEST_PASSAGES["L60_geo"], "learned", clf, "maintained", "handrule",
                              GOLD_MENTIONS["L60_geo"])
    assert rk_o != rk_h, "self-test TELEMETRY: oracle vs handrule extraction must differ on L60_geo (got identical)"

    # N_CMP power gate (design-gate: composition must be POWERED).
    n_cmp = sum(1 for q in TEST_QS if q["slice"] == "CMP")
    assert n_cmp >= 15, f"self-test: composition underpowered, N_CMP={n_cmp} (< 15)"

    # ARMS-MUST-DIFFER across the 4 mention modes (answers differ -> the mention gate is not vacuous).
    ans = {}
    for mm in MENTION_ARMS:
        _c, _a, _s, _r = run_mention_arm(mm, clf)
        ans[mm] = _a
    _arms_must_differ(ans)

    print(f"SELF-TEST PASS: perceptron fit ({len(ex)} ex); canonical+passive roles; positional misses "
          f"passive; {n_clauses} REAL 2nd-reader clauses provenance-verified verbatim; loc(bees,house) "
          f"extracts (handrule=v4); {len(all_gold)} gold mention heads valid + blacklist-disjoint; "
          f"oracle!=handrule extraction (telemetry); N_CMP={n_cmp}; 4 mention arms differ.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args, _ = ap.parse_known_args()
    if args.self_test:
        return self_test()
    run_mode = "smoke" if args.smoke else "full"
    _write_start_marker(OUTPUT_DIR, run_mode, expected_n_units=len(TEST_QS))
    metrics = build_verdict(OUTPUT_DIR, run_mode)
    _write_metrics(OUTPUT_DIR, metrics)
    o = metrics["relation_f1"]["oracle"]
    h = metrics["relation_f1"]["handrule"]
    a = metrics["arms"]
    dl = metrics["deltas_oracle_minus_handrule"]
    pc = metrics["positive_control"]
    g = metrics["gates"]
    print(f"[{run_mode}] {metrics['verdict']}: {metrics['verdict_msg']}")
    print(f"  RELF1  oracle: P={o['micro_precision']:.3f} R={o['micro_recall']:.3f} F1={o['micro_f1']:.3f}  "
          f"| handrule(floor): P={h['micro_precision']:.3f} R={h['micro_recall']:.3f} F1={h['micro_f1']:.3f}  "
          f"| dF1={dl['relf1_f1']:+.3f} dR={dl['relf1_recall']:+.3f}")
    for mm in MENTION_ARMS:
        am = a[mm]
        print(f"    Q-slices {mm:9s}: all={am['acc_all']:.3f} NC={am['acc_NC']:.3f} CO={am['acc_CO']:.3f} "
              f"CC={am['acc_CC']:.3f} CMP={am['acc_CMP']:.3f}")
    fq = metrics["frequency_floor"]
    print(f"    Q-slices freq-floor: all={fq['acc_all']:.3f} NC={fq['acc_NC']:.3f} CO={fq['acc_CO']:.3f} "
          f"CC={fq['acc_CC']:.3f} CMP={fq['acc_CMP']:.3f}")
    print(f"  DELTA oracle-handrule: CMP={dl['CMP']:+.3f}(p={dl['cmp_p_oracle_le_handrule']:.3f}) "
          f"CC={dl['CC']:+.3f}(p={dl['cc_p_oracle_le_handrule']:.3f}) CO={dl['CO']:+.3f} NC={dl['NC']:+.3f} "
          f"allQ={dl['all_Q']:+.3f}")
    print(f"  POSITIVE-CONTROL reproduce v4: F1 {pc['measured_handrule_relf1_f1']:.3f} vs {pc['v4_handrule_relf1_f1']} "
          f"({pc['reproduce_f1_ok']}); CMP {pc['measured_handrule_cmp']:.3f} vs {pc['v4_handrule_cmp']} "
          f"({pc['reproduce_cmp_ok']}); NC {pc['measured_handrule_nc']:.3f} vs {pc['v4_handrule_nc']} "
          f"({pc['reproduce_nc_ok']}) -> reproduce_ok={pc['positive_control_ok']}")
    print(f"  gates: telemetry_moved={g['telemetry_moved']} sets_differ={g['oracle_handrule_sets_differ']} "
          f"baseline_in_band={g['baseline_in_band']} arms_differ={g['arms_differ_verified']}")
    return 0


if __name__ == "__main__":
    try:
        rc = main()
        sys.exit(rc if rc is not None else 0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
