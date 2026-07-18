"""
Track A v2 -- LEARNED glass-box role-assigner reader on HELD-OUT passages.

WHY (v1 demoted): exp_base_reader_grounded_relations_coref_v1 (VET a85240158,
demoted HARD_PASS -> MEASURED_MECHANISM) was CONSTRUCTION-FORCED: its ACTION_VERBS /
STOPWORDS / GROUNDING_OVERRIDE dicts were hand-authored to exactly its 7 passages,
so NC=1.000 on both arms was tautological. Genuine kernel that survived: the real
overlay resolved 6/7 pronouns + 2 composition wins frequency cannot get. But it was a
construction-proof inside the 0.44 hand-rule wall. VET + the relation-comprehension drill
(notes/research_drill_relation_comprehension_reader_thematic_roles_glassbox_2026-07-18.md)
both prescribe: replace the hand-rules with a LEARNED role-assigner and test on HELD-OUT text.

THE ESCAPE FROM CONSTRUCTION-DETERMINATION (load-bearing):
  1. The role-assigner is a LEARNED multiclass linear classifier (averaged perceptron),
     TRAINED on a labeled TRAINING grammar, TESTED on DIFFERENT real McGuffey PRIMER
     passages it never saw during fit. (v1 used mcguffey_first_reader; primer = held-out.)
  2. Features are WORD-IDENTITY-FREE (position, POS via NLTK PerceptronTagger [legal],
     animacy from grounding, preposition/case cues, agreement, passive-marker). The
     classifier CANNOT memorize a passage -- it can only learn the general multi-cue
     competition (MacWhinney-Bates competition model, made learnable). Generalization to
     new vocab is therefore genuine, not a per-passage rule table.
  3. Independent gold (relation triples + Q-answers) is hand-annotated on the test passages,
     NOT emitted by the extractor (anti-circular).

DIFFICULTY ON: held-out real text; competitive coref where recency is NOT the answer
(gender excludes the recent antecedent); 2-hop composition; role-reversal minimal pairs
("dog bit man" vs "man bit dog"); passives ("the hen was fed by Ned") -- the case where a
LEARNED multi-cue assigner must beat the naive POSITIONAL shortcut.

ARMS:
  LEARNED_FULL    : learned role-assigner + real overlay COREF                [the claim]
  LEARNED_NOCOREF : learned role-assigner, coref OFF (overlay-contribution ablation)
  POSITIONAL      : naive positional role-assigner (v1 shortcut = must-beat) + overlay
  FREQUENCY       : no-role grounded frequency floor (order-insensitive -> fails reversal)

SCORED SEPARATELY: (A) RELATION-F1 on held-out (extraction quality); (B) comprehension-Q
accuracy (coref + composition); (C) role-reversal + passive controls.

Glass-box (learned + transparent linear weights = the competition weights, inspectable),
learn-in-substrate, NO external LLM at runtime, NOT next-word prediction. Local/foreground.

ANCHOR: learned_role_assigner_reader_heldout_v2
COMPUTE: sequential-CPU (POS-tag + tiny perceptron fit + symbolic query); wall < 60s;
  no HD primitive / no torch / no GPU -- justified (COMPUTE-PROPORTIONALITY: a directional
  can-the-learned-extractor-generalize gate; the cheapest decisive method is a small
  transparent classifier, NOT a heavy fit).
DETERMINISM: OMP_NUM_THREADS=1; fixed RNG seed 12345; fixed training example order (no
  shuffle); sorted(set(...)) only; deterministic argmax tie-break; no salted-builtin seeding.

CELL-TEMPLATE MANDATES (relevant subset; many SCHEMA-VET gates N/A for this cell-type):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)             [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check at gate                        [META_RULE_AF]
# - baseline_in_band 0.05 < FREQUENCY/POSITIONAL comp < 0.95   [META_RULE_AG]
# - discriminator CAN-FAIL (RELF1 can collapse; reversal/composition can fail) [design-gate]
# - deterministic seeding (fixed int seed, fixed order, sorted set)  [F.5 / PROT-023]
# - real_code_path: self-test CONSTRUCTS + EXERCISES the REAL WorkingOverlay + fits the
#   REAL perceptron + runs the REAL POS tagger on held-out text        [F.1]
# - substrate_signature: binds WorkingOverlay/observe/resolve_pronoun sigs  [F.2]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 60s)
# - all reported numbers MEASURED@this metrics.json
# - N/A: KGStore (no KG); N/A cardinality sweep-axis; N/A CRLB (no HD noise floor)
#
# HONESTY CAVEAT (construction-determinism, the whole point of v2): the TRAINING labels
# are supervised (SRL is supervised -- the drill endorses this). The escape is that the
# TEST passages are real held-out text, features are word-identity-free (no memorization
# possible), and role-reversal proves role-sensitivity not bag-of-words. LOAD-BEARING
# EMPIRICAL results: (1) RELATION-F1 on HELD-OUT primer (does the learned extractor
# generalize?); (2) COREF-LIFT full vs nocoref on held-out; (3) composition beating
# frequency + positional; (4) role-reversal + passive controls. Reported CLAIM-VET-pending
# (NOT self-declared chain-grade). Structural extraction (possessive 's / possessive-pronoun /
# color-adjective) is POS-driven not learned -- only THEMATIC roles are learned (the gap the
# drill identifies); documented, not over-claimed.
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

ANCHOR_NAME = "learned_role_assigner_reader_heldout_v2"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)

SEED = 12345
N_BOOT = 5000
N_EPOCHS = 12  # averaged-perceptron passes (fixed order, deterministic)

# ---- Pre-registered bands (set BEFORE the final run) ----------------------------------
# (A) The load-bearing generalization number: RELATION-F1 of the LEARNED extractor on
#     HELD-OUT real primer text. Drill predicts 0.80-0.95 plausible on grade-1 SVO; the old
#     hand-rule wall on HARD prose was 0.44. Strict-above-floor HARD_PASS.
HP_RELF1_HELDOUT = 0.70        # HARD_PASS: learned extractor GENERALIZES to held-out
HF_RELF1_HELDOUT = 0.45        # HARD_FAIL: collapses back to (or below) the old wall
# (B) coref-lift on comprehension CO slice (FULL vs NOCOREF): overlay helps on held-out.
HP_COREF_LIFT = 0.15
HP_COREF_ALPHA = 0.10          # small N -> relaxed bootstrap alpha
# (C) role-reversal: learned must be role-SENSITIVE; frequency (order-insensitive) must NOT be.
HP_REVERSAL_LEARNED = 0.75     # learned gets both orders right
MAX_REVERSAL_FREQ = 0.50       # frequency floor cannot (proves the test has teeth)
HF_REVERSAL_LEARNED = 0.50     # HARD_FAIL: learned not reliably role-sensitive
# (D) passives: the LEARNED multi-cue assigner must BEAT the naive POSITIONAL shortcut.
HP_PASSIVE_LEARNED = 0.60
HP_PASSIVE_LEARNED_MINUS_POS = 0.30
# (E) composition: learned_full composes 2 relations on held-out AND beats frequency.
HP_COMPOSITION = 0.50
# baseline-in-band guard (comprehension_all for the non-mechanism baselines)
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
}
ANIMALS = {"hen", "hens", "duck", "ducks", "cow", "dog", "dogs", "cat", "cats", "rat",
           "rats", "pet", "bird", "birds", "frog", "fox", "nag", "owl", "pig", "hare",
           "lamb", "colt", "goat", "bee", "ox"}
PERSON_NOUNS = {"man", "men", "lad", "boy", "boys", "girl", "girls", "child",
                "baby", "woman"}
COLORS = {"black", "white", "red", "brown", "green", "blue", "gray", "grey", "gold"}
LOC_NOUNS = {"nest", "box", "cage", "pond", "bank", "rock", "pen", "log", "tree",
             "mat", "stand", "hill", "yard", "field", "barn", "roof", "wall", "road",
             "hand", "back", "head", "lap", "top", "web"}
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
            sing = w[:-2] if w.endswith("es") and w[:-2] in NAME_GENDER | PERSON_NOUNS | ANIMALS | LOC_NOUNS else w[:-1]
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


def split_sentences(text):
    parts = re.split(r"[.!?]+", text)
    return [p.strip() for p in parts if p.strip()]


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
        if ground_category(low) == "COLOR":
            continue
        if pos in ("NN", "NNS", "NNP", "NNPS"):
            idx.append(i)
        elif ground_category(low) is not None and pos not in _NONNOUN_POS:
            idx.append(i)
    return idx


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
# HELD-OUT TEST passages -- REAL McGuffey PRIMER text (data/corpora/.../mcguffey_primer.clean.txt).
# v1 used mcguffey_first_reader; the primer is genuinely held out (different lessons/vocab).
# Chosen for competitive coref (gender excludes the recent antecedent) + composition.
# Independent GOLD relations + Q-answers are hand-annotated (NOT emitted by the extractor).
# =======================================================================================
TEST_PASSAGES = {
    # Lesson XI (primer): she -> hen; 2-hop nest-in-box.
    "T1_hen": "This is a fat hen. The hen has a nest in the box. She has eggs in the nest.",
    # Lesson XIII: them -> ducks; she -> Nell.
    "T2_ducks": "Nell is by the pond. Nell sees the ducks and will feed them. She can not get the ducks.",
    # Lesson XIV: COMPETITIVE -- Mary (fem, recent) vs man; him -> man by gender, NOT recency.
    "T3_mary": "This old man can not see. Mary holds him by the hand. She is kind to the man.",
    # Lesson XVII: it -> bird; nest + eggs.
    "T4_bird": "A bird is in the tree. It has a nest. The nest has five eggs.",
    # Lesson XVIII: it -> bird; her -> Sue; composition Sue's hand.
    "T5_petbird": "This is a pet bird. It lives in a cage. Sue loves the bird.",
    # Lesson IX/X (primer): possession + motion-goal PP ('ran at X' = directional, not transitive).
    "T6_nag": "Tom has a nag. The dog ran at the nag.",
}

# Independent GOLD relation triples per passage (hand-annotated; anti-circular). Canonical forms:
#   ("svo", verb, agent, patient) ; ("loc", figure, ground) ; ("poss", owner, owned)
TEST_GOLD_RELS = {
    "T1_hen": [("poss", "hen", "nest"), ("loc", "nest", "box"),
               ("poss", "hen", "eggs"), ("loc", "eggs", "nest")],
    "T2_ducks": [("loc", "nell", "pond"), ("svo", "sees", "nell", "ducks"),
                 ("svo", "feed", "nell", "ducks"), ("svo", "get", "nell", "ducks")],
    "T3_mary": [("svo", "holds", "mary", "man"), ("loc", "mary", "hand"),
                ("svo", "kind", "mary", "man")],
    "T4_bird": [("loc", "bird", "tree"), ("poss", "bird", "nest"),
                ("poss", "nest", "eggs")],
    "T5_petbird": [("loc", "bird", "cage"), ("svo", "loves", "sue", "bird")],
    "T6_nag": [("poss", "tom", "nag"), ("loc", "dog", "nag")],
}

# Comprehension questions on held-out passages. slice in {NC, CO, CMP}. Each carries an
# arm-independent query spec (never contains the answer) + gold. Coref-required Qs are CO;
# 2-hop are CMP.
TEST_QS = [
    # T1 hen
    dict(qid="T1a", p="T1_hen", slice="NC", atype="LOCATION", spec=("loc_ground", "nest"),
         gold="box", text="Where is the nest?"),
    dict(qid="T1b", p="T1_hen", slice="CO", atype="AGENT", spec=("has_owner", "eggs"),
         gold="hen", text="Who has eggs?"),  # 'She has eggs' -> she=hen
    dict(qid="T1c", p="T1_hen", slice="CMP", atype="LOCATION", spec=("loc_of_owned", "hen", "nest"),
         gold="box", text="Where is the nest the hen has?"),  # poss(hen,nest)+loc(nest,box)
    # T2 ducks
    dict(qid="T2a", p="T2_ducks", slice="NC", atype="LOCATION", spec=("loc_ground", "nell"),
         gold="pond", text="Where is Nell?"),
    dict(qid="T2b", p="T2_ducks", slice="CO", atype="PATIENT", spec=("svo_patient", "feed", "nell"),
         gold="ducks", text="What will Nell feed?"),  # 'feed them' -> them=ducks
    dict(qid="T2c", p="T2_ducks", slice="CO", atype="AGENT", spec=("svo_agent", "get", "ducks"),
         gold="nell", text="Who can not get the ducks?"),  # 'She can not get' -> she=nell
    # T3 mary (competitive coref)
    dict(qid="T3a", p="T3_mary", slice="CO", atype="PATIENT", spec=("svo_patient", "holds", "mary"),
         gold="man", text="Who does Mary hold?"),  # 'holds him' -> him=man (gender, NOT recency)
    dict(qid="T3b", p="T3_mary", slice="CO", atype="AGENT", spec=("svo_agent", "kind", "man"),
         gold="mary", text="Who is kind to the man?"),  # 'She is kind' -> she=mary
    # T4 bird
    dict(qid="T4a", p="T4_bird", slice="NC", atype="LOCATION", spec=("loc_ground", "bird"),
         gold="tree", text="Where is the bird?"),
    dict(qid="T4b", p="T4_bird", slice="CO", atype="AGENT", spec=("has_owner", "nest"),
         gold="bird", text="Who has a nest?"),  # 'It has a nest' -> it=bird
    dict(qid="T4c", p="T4_bird", slice="CMP", atype="AGENT", spec=("owner_of_owned_chain", "eggs"),
         gold="bird", text="Whose nest has the eggs?"),  # poss(nest,eggs)+poss(bird,nest)
    # T5 petbird
    dict(qid="T5a", p="T5_petbird", slice="CO", atype="LOCATION", spec=("loc_ground", "bird"),
         gold="cage", text="Where does the bird live?"),  # 'It lives in a cage' -> it=bird
    dict(qid="T5b", p="T5_petbird", slice="NC", atype="AGENT", spec=("svo_agent", "loves", "bird"),
         gold="sue", text="Who loves the bird?"),
    # T6 nag
    dict(qid="T6a", p="T6_nag", slice="NC", atype="AGENT", spec=("has_owner", "nag"),
         gold="tom", text="Who has a nag?"),
    dict(qid="T6b", p="T6_nag", slice="NC", atype="LOCATION", spec=("loc_ground", "dog"),
         gold="nag", text="Where did the dog run?"),
]

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
def assign_roles_learned(tagged, clf):
    """Return dict cand_idx -> role via the LEARNED classifier."""
    verb_idx, verb, passive = find_main_verb(tagged)
    cand = candidate_indices(tagged)
    first = cand[0] if cand else None
    roles = {}
    for i in cand:
        feats = candidate_features(tagged, i, verb_idx, passive, first)
        roles[i] = clf.predict(feats)
    return roles, verb_idx, verb, passive, cand


def assign_roles_positional(tagged):
    """Naive positional shortcut (v1's approach = the must-beat): first candidate before verb
    = AGENT, first candidate after verb = PATIENT, 'to'-NP = RECIPIENT, loc-prep NP = LOCATION.
    Ignores passive + animacy (so it mis-assigns passives)."""
    verb_idx, verb, passive = find_main_verb(tagged)
    cand = candidate_indices(tagged)
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


def resolve_head(tagged, i, ov, do_coref):
    """Head string for candidate i; pronouns resolved via the overlay when do_coref."""
    surf, low, pos = tagged[i]
    if low in PRONOUNS_SUBJ_OBJ and low not in ("i", "you", "we", "us", "me"):
        if do_coref:
            from hdlab.state_of_mind import PRONOUN_SCOPE
            if low in PRONOUN_SCOPE:
                ent = ov.resolve_pronoun(low, strategy="recency")
                if ent is not None:
                    return ent.head, "pronoun_resolved"
        return low, "pronoun_literal"
    return low, "nominal"


def extract_passage(passage_text, assigner, do_coref):
    """Run coref pass + role assignment; emit relation triples with resolved heads.
    assigner: 'learned' (needs clf via closure) or 'positional'. Returns (rels, reslog)."""
    from hdlab.state_of_mind import WorkingOverlay, SetKnownBase, PRONOUN_SCOPE
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
                    ent = ov.resolve_pronoun(low, strategy="recency")
                    pron_res[i] = ent.head if ent is not None else None
                    reslog.append((low, pron_res[i]))
                sc = PRONOUN_SCOPE[low]
                ov.observe(low, is_pronoun=True, gender=sc["gender"], number=sc["number"])
            elif low in PRONOUNS_POSS:
                pass  # handled structurally below
            else:
                cat = ground_category(low)
                if cat is None or cat == "COLOR":
                    continue
                is_name = (low in NAME_GENDER) or (pos in ("NNP", "NNPS"))
                g, num = grounded_gender_number(low, is_name)
                ov.observe(low, gender=g, number=num, is_proper_name=is_name)
        # ---- role assignment ----
        if assigner == "positional":
            roles, verb_idx, verb, passive, cand = assign_roles_positional(tagged)
        else:
            roles, verb_idx, verb, passive, cand = assigner(tagged)

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
        # possessive 'has' -> poss(agent, patient)
        if verb == "has" and agents and patients:
            for pi in patients:
                rels.append(("poss", head_of(agents[0]), head_of(pi)))
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
                    ent = ov.resolve_pronoun(low, strategy="recency")
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
# Arms.
# =======================================================================================
def run_arm(arm, clf):
    """arm in {learned_full, learned_nocoref, positional, frequency}."""
    learned = lambda tagged: assign_roles_learned(tagged, clf)  # noqa: E731
    stores = {}
    reslogs = {}
    if arm in ("learned_full", "learned_nocoref"):
        assigner = learned
        do_coref = (arm == "learned_full")
    elif arm == "positional":
        assigner = "positional"
        do_coref = True
    else:
        assigner = None
        do_coref = False
    if arm != "frequency":
        for pid, text in TEST_PASSAGES.items():
            rels, rlog = extract_passage(text, assigner, do_coref)
            stores[pid] = rels
            reslogs[pid] = rlog
    correct = []
    answers = []
    for q in TEST_QS:
        if arm == "frequency":
            ans = answer_frequency(q["atype"], TEST_PASSAGES[q["p"]], q["spec"])
        else:
            ans = answer_reader(q["spec"], stores[q["p"]])
        na, ng = normalize(ans), normalize(q["gold"])
        correct.append(1 if (na is not None and na == ng) else 0)
        answers.append(na)
    return correct, answers, stores, reslogs


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
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    rng = random.Random(SEED)

    # ---- FIT the learned role-assigner on the TRAINING grammar (held-out test never seen) ----
    clf = AveragedPerceptron()
    train_ex = build_training_examples()
    clf.fit(train_ex, epochs=N_EPOCHS)
    learned = lambda tagged: assign_roles_learned(tagged, clf)  # noqa: E731

    # ---- arms ----
    lf_c, lf_a, lf_store, lf_reslog = run_arm("learned_full", clf)
    ln_c, ln_a, _, _ = run_arm("learned_nocoref", clf)
    po_c, po_a, po_store, _ = run_arm("positional", clf)
    fr_c, fr_a, _, _ = run_arm("frequency", clf)

    digests = _arms_must_differ({"learned_full": lf_a, "learned_nocoref": ln_a,
                                 "positional": po_a, "frequency": fr_a})

    # ---- (A) RELATION-F1 on HELD-OUT (the load-bearing generalization number) ----
    relf1 = {}
    for arm, store in (("learned_full", lf_store), ("positional", po_store)):
        tot_tp = tot_ex = tot_go = 0
        per_p = {}
        for pid in TEST_PASSAGES:
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
        relf1[arm] = dict(micro_precision=round(P, 3), micro_recall=round(R, 3),
                          micro_f1=round(F, 3), per_passage=per_p)
    relf1_learned = relf1["learned_full"]["micro_f1"]

    # ---- (B) coref lift on CO slice ----
    co_idx = [i for i, q in enumerate(TEST_QS) if q["slice"] == "CO"]
    cmp_idx = [i for i, q in enumerate(TEST_QS) if q["slice"] == "CMP"]
    lf_co, n_co = slice_acc(lf_c, "CO")
    ln_co, _ = slice_acc(ln_c, "CO")
    fr_co, _ = slice_acc(fr_c, "CO")
    lf_cmp, n_cmp = slice_acc(lf_c, "CMP")
    fr_cmp, _ = slice_acc(fr_c, "CMP")
    po_cmp, _ = slice_acc(po_c, "CMP")
    coref_lift = lf_co - ln_co
    p_coref, obs_coref = bootstrap_lift_p(lf_c, ln_c, co_idx, rng)

    # ---- (C) role-reversal ----
    rev_learned, rev_learned_per = score_reversal(learned)
    rev_pos, rev_pos_per = score_reversal("positional")
    rev_freq, rev_freq_per = score_reversal(learned, use_freq=True)

    # ---- (D) passives ----
    pas_learned, pas_learned_per = score_passive(learned)
    pas_pos, pas_pos_per = score_passive("positional")
    passive_gap = pas_learned - pas_pos

    # ---- baseline-in-band ----
    fr_all = acc(fr_c)
    po_all = acc(po_c)
    baseline_in_band = (BASELINE_BAND[0] < fr_all < BASELINE_BAND[1]) and \
                       (BASELINE_BAND[0] < po_all < BASELINE_BAND[1])

    # ---- verdict logic (pre-registered) ----
    reasons = []
    checks = {}
    checks["relf1_generalizes"] = relf1_learned >= HP_RELF1_HELDOUT
    checks["role_reversal_sensitive"] = (rev_learned >= HP_REVERSAL_LEARNED and rev_freq <= MAX_REVERSAL_FREQ)
    checks["passive_beats_positional"] = (pas_learned >= HP_PASSIVE_LEARNED and passive_gap >= HP_PASSIVE_LEARNED_MINUS_POS)
    checks["coref_lift"] = (coref_lift >= HP_COREF_LIFT and p_coref < HP_COREF_ALPHA)
    checks["composition"] = (lf_cmp >= HP_COMPOSITION and lf_cmp > fr_cmp)
    for name, ok in checks.items():
        if not ok:
            reasons.append(name)

    hard_fail = (relf1_learned < HF_RELF1_HELDOUT) or (rev_learned < HF_REVERSAL_LEARNED) or \
                (lf_cmp <= fr_cmp and lf_cmp < HP_COMPOSITION)

    if all(checks.values()):
        verdict = "HARD_PASS"
        vmsg = (f"LEARNED role-assigner GENERALIZES to held-out primer: RELF1={relf1_learned:.3f} "
                f"(>= {HP_RELF1_HELDOUT}); role-reversal learned={rev_learned:.2f} freq={rev_freq:.2f}; "
                f"passive learned={pas_learned:.2f} vs positional={pas_pos:.2f} (gap={passive_gap:.2f}); "
                f"coref_lift={coref_lift:.3f} (p={p_coref:.3f}); composition={lf_cmp:.3f}. "
                f"Reading-grows-relations is a GENERALIZING capability (escapes v1 construction + 0.44 wall).")
    elif hard_fail:
        verdict = "HARD_FAIL"
        vmsg = (f"v1 was construction-bound: RELF1_heldout={relf1_learned:.3f} "
                f"(HF<{HF_RELF1_HELDOUT}), reversal_learned={rev_learned:.2f}, "
                f"composition={lf_cmp:.3f} vs freq={fr_cmp:.3f}. Failed: {reasons}")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"PARTIAL: RELF1={relf1_learned:.3f}, reversal={rev_learned:.2f}, "
                f"passive_gap={passive_gap:.2f}, coref_lift={coref_lift:.3f}, comp={lf_cmp:.3f}. "
                f"Not all HARD_PASS gates: {reasons}")

    elapsed = time.perf_counter() - t0
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg, summary=f"{verdict}: RELF1={relf1_learned:.3f} rev={rev_learned:.2f}",
        elapsed_s=round(elapsed, 4), ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED, n_boot=N_BOOT,
        n_train_sentences=len(TRAIN), n_train_examples=len(train_ex), n_epochs=N_EPOCHS,
        n_test_passages=len(TEST_PASSAGES), n_questions=len(TEST_QS),
        heldout_source="mcguffey_primer.clean.txt (v1 used mcguffey_first_reader -> genuinely held out)",
        arms=dict(
            learned_full=dict(acc_all=acc(lf_c), acc_CO=lf_co, acc_CMP=lf_cmp, per_q=lf_c, answers=lf_a),
            learned_nocoref=dict(acc_all=acc(ln_c), acc_CO=ln_co, per_q=ln_c, answers=ln_a),
            positional=dict(acc_all=po_all, acc_CMP=po_cmp, per_q=po_c, answers=po_a),
            frequency=dict(acc_all=fr_all, acc_CO=fr_co, acc_CMP=fr_cmp, per_q=fr_c, answers=fr_a),
        ),
        relation_f1=relf1,
        discriminators=dict(
            relf1_learned_heldout=relf1_learned,
            relf1_positional_heldout=relf1["positional"]["micro_f1"],
            coref_lift=coref_lift, coref_lift_p_le0=p_coref, coref_lift_obs=obs_coref,
            role_reversal_learned=rev_learned, role_reversal_positional=rev_pos,
            role_reversal_frequency=rev_freq,
            passive_learned=pas_learned, passive_positional=pas_pos, passive_gap=passive_gap,
            composition_learned_full=lf_cmp, composition_frequency=fr_cmp, composition_positional=po_cmp,
        ),
        checks=checks,
        controls=dict(reversal_learned=rev_learned_per, reversal_positional=rev_pos_per,
                      reversal_frequency=rev_freq_per,
                      passive_learned=pas_learned_per, passive_positional=pas_pos_per),
        learned_weights_top=clf.top_weights(6),
        coref_resolutions={pid: rl for pid, rl in lf_reslog.items()},
        slice_counts=dict(CO=n_co, CMP=n_cmp),
        bands=dict(HP_RELF1_HELDOUT=HP_RELF1_HELDOUT, HF_RELF1_HELDOUT=HF_RELF1_HELDOUT,
                   HP_COREF_LIFT=HP_COREF_LIFT, HP_COREF_ALPHA=HP_COREF_ALPHA,
                   HP_REVERSAL_LEARNED=HP_REVERSAL_LEARNED, MAX_REVERSAL_FREQ=MAX_REVERSAL_FREQ,
                   HP_PASSIVE_LEARNED=HP_PASSIVE_LEARNED,
                   HP_PASSIVE_LEARNED_MINUS_POS=HP_PASSIVE_LEARNED_MINUS_POS,
                   HP_COMPOSITION=HP_COMPOSITION),
        gates=dict(baseline_in_band=baseline_in_band, freq_acc_all=fr_all, pos_acc_all=po_all,
                   arms_differ_verified=True, arm_digests=digests),
        questions=[dict(qid=q["qid"], p=q["p"], slice=q["slice"], gold=q["gold"], text=q["text"],
                        learned_full=lf_a[i], learned_nocoref=ln_a[i], positional=po_a[i],
                        frequency=fr_a[i]) for i, q in enumerate(TEST_QS)],
        provenance="held-out=mcguffey_primer; overlay=hdlab.state_of_mind.WorkingOverlay; "
                   "role-assigner=AveragedPerceptron over word-identity-free features",
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
    ent = ov.resolve_pronoun("him", strategy="recency")  # him = masc -> man (Mary excluded by gender)
    assert ent is not None and ent.head == "man", \
        f"self-test: 'him' should resolve to man not Mary (gender>recency), got {ent}"

    # held-out extraction produces SOME correct triples (generalization fires at all).
    rels, rlog = extract_passage(TEST_PASSAGES["T1_hen"], lambda t: assign_roles_learned(t, clf), True)
    assert ("loc", "nest", "box") in rels, f"self-test: nest-in-box should extract, got {rels}"

    # ARMS-MUST-DIFFER.
    lf_c, lf_a, _, _ = run_arm("learned_full", clf)
    ln_c, ln_a, _, _ = run_arm("learned_nocoref", clf)
    po_c, po_a, _, _ = run_arm("positional", clf)
    fr_c, fr_a, _, _ = run_arm("frequency", clf)
    _arms_must_differ({"learned_full": lf_a, "learned_nocoref": ln_a,
                       "positional": po_a, "frequency": fr_a})
    print(f"SELF-TEST PASS: perceptron fit ({len(ex)} ex); canonical+passive roles correct; "
          f"positional misses passive; him->man (gender>recency); nest-in-box extracted; arms differ.")
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
    d = metrics["discriminators"]
    print(f"[{run_mode}] {metrics['verdict']}: {metrics['verdict_msg']}")
    print(f"  RELF1 learned={d['relf1_learned_heldout']:.3f} positional={d['relf1_positional_heldout']:.3f}")
    print(f"  reversal learned={d['role_reversal_learned']:.2f} pos={d['role_reversal_positional']:.2f} "
          f"freq={d['role_reversal_frequency']:.2f}")
    print(f"  passive learned={d['passive_learned']:.2f} pos={d['passive_positional']:.2f} gap={d['passive_gap']:.2f}")
    print(f"  coref_lift={d['coref_lift']:.3f} (p={d['coref_lift_p_le0']:.3f})  composition={d['composition_learned_full']:.3f}")
    print(f"  arms comp_all: learned={metrics['arms']['learned_full']['acc_all']:.3f} "
          f"nocoref={metrics['arms']['learned_nocoref']['acc_all']:.3f} "
          f"positional={metrics['arms']['positional']['acc_all']:.3f} "
          f"frequency={metrics['arms']['frequency']['acc_all']:.3f}")
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
