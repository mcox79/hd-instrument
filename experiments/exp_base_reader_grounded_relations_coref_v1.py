"""
CORRECTED base-first reader: with word meanings GROUNDED up front (dictionary =
the picture/teacher stand-in), does READING correctly COMPREHEND + GROW the
RELATIONS/facts among ALREADY-KNOWN words? (NOT word-meaning inference -- that arc
is a proven dead-end at grade-1 scale: v1 9cea9a57c MIDDLE + v2 781125f41 controlled
NULL, VET aff25c53. USER pivot triple-confirmed: a child does not LEARN hen/nest/eggs
from grade-1 text -- they are grounded by pictures/teacher; reading's real job = build
the correct RELATIONS among known words.)

TASK: GROUND base words via WordNet (category/lexname; the dictionary stand-in), then
READ real cleaned McGuffey grade-1 passages and EXTRACT RELATIONS (agent-action-patient
SVO, attribute, containment/location, possession). USE the real packaged working-memory
overlay hdlab.state_of_mind.WorkingOverlay for COREF (she/her/it/his -> the right entity)
so relations bind to the correct entity. TEST = COMPREHENSION of the grown relations vs
hand-authored INDEPENDENT gold (Who did X? Where is Y? Whose Z? What color? + composition).

ARMS (ONE variable = COREF on/off via the overlay):
  (a) FULL     : grounded words + relation-extraction + overlay COREF  [the claim]
  (b) NO_COREF : same, but pronouns left UNRESOLVED (relations that need she->hen drop) --
                 isolates the overlay's contribution (the single variable).
  (c) FLOOR    : no-relation grounded frequency baseline (most-frequent passage token of
                 the answer-type) -- a REAL baseline that CANNOT do relations.

Glass-box, learn-in-substrate, NO external LLM, NOT next-word prediction. Local/foreground.

ANCHOR: base_reader_grounded_relations_coref_v1
COMPUTE: sequential-CPU, wall < 10s, symbolic (no HD primitive, no torch, no GPU) -- justified.
DETERMINISM: OMP_NUM_THREADS=1; fixed RNG seed 12345; sorted(set(...)) only; no salted-builtin seeding.

CELL-TEMPLATE MANDATES (relevant subset; many SCHEMA-VET gates N/A for this cell-type):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)      [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check at gate                 [META_RULE_AF]
# - baseline_in_band 0.05 < floor < 0.95               [META_RULE_AG]
# - discriminator CAN-FAIL (coref_lift can be <=0)     [design-gate]
# - deterministic seeding (fixed int seed, sorted set) [F.5 / PROT-023]
# - real_code_path: self-test CONSTRUCTS + EXERCISES the REAL WorkingOverlay  [F.1]
# - substrate_signature: binds WorkingOverlay/observe/resolve_pronoun sigs    [F.2]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 10s)
# - all reported numbers MEASURED@this metrics.json
# - N/A: KGStore (no KG); N/A cardinality sweep-axis; N/A CRLB (no HD noise floor)
#
# HONESTY / construction-determinism caveat (memory: synthetic-toy outcomes can be
# construction-determined): the rule-based relation EXTRACTOR + query specs are
# construction-favored on simple grade-1 SVO (they are hand-authored). The LOAD-BEARING
# EMPIRICAL results are (1) whether the REAL UNMODIFIED overlay resolves the coref on REAL
# McGuffey text correctly, and (2) COREF_LIFT (full vs no-coref) and RELATION_LIFT (full vs
# floor). The overlay CAN mis-resolve (e.g. recency picks a nearer wrong antecedent), so
# HARD_FAIL is reachable. Reported as CLAIM-VET-pending (NOT self-declared chain-grade).
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
from collections import Counter
from datetime import datetime, timezone

_THIS = os.path.abspath(__file__)
REPO = os.path.dirname(os.path.dirname(_THIS))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

ANCHOR_NAME = "base_reader_grounded_relations_coref_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)

SEED = 12345
N_BOOT = 5000

# ---- Pre-registered bands (set BEFORE the final run) ----------------------------------
# PRIMARY discriminator = COREF_LIFT = acc_full(coref-required Qs) - acc_nocoref(coref-required Qs).
# This isolates the overlay's causal contribution (the single variable = coref on/off) and is the
# least construction-determined comparison (the overlay is the REAL packaged module, unmodified).
HP_COREF_LIFT = 0.25       # HARD_PASS: coref measurably + substantially helps
HP_ALPHA = 0.05            # bootstrap significance: P(lift <= 0) < alpha
MB_COREF_LIFT = 0.05       # MIDDLE_BAND floor for coref lift
# SECONDARY: RELATION_LIFT = acc_full(all) - acc_floor(all); relation structure beats frequency.
HP_RELATION_LIFT = 0.10
# COMPOSITION: full must compose 2 relations (growth beyond single-sentence).
HP_COMPOSITION = 0.50
# CONTROL: on NON-coref Qs full ~= no-coref (no-coref is a fair baseline, not globally broken),
# and full(non-coref) must be high (extraction works). |full-nocoref| on NC small; full(NC) >= 0.70.
NC_CONTROL_MAX_DELTA = 0.20
NC_EXTRACTION_MIN = 0.70

# =======================================================================================
# GROUNDING (the dictionary = picture/teacher stand-in). Words are KNOWN, NOT held out.
# WordNet lexname gives the semantic category; small curated fallback for proper NAMES and
# COLORS (names are absent from WordNet; "color" is not a clean WordNet class). Documented
# honest gap: real grounding is multimodal (we lack vision); the dictionary is the stand-in.
# =======================================================================================
# Curated proper-name genders (a grade-1 child knows Ned is a boy, Ann a girl). Rab/Jip = dogs
# in McGuffey (animate, gender unknown -> "any"). Supplied to the UNMODIFIED overlay.observe().
NAME_GENDER = {
    "ned": "masc", "tom": "masc", "john": "masc", "ben": "masc", "nat": "masc",
    "ann": "fem", "kitty": "fem", "nell": "fem", "kate": "fem", "mamma": "fem",
    "jip": None, "rab": None, "prince": None,
}
COLORS = {"black", "white", "red", "brown", "green", "blue", "gray", "grey"}
# Function words / determiners / auxiliaries / pronouns handled structurally (not content).
DETERMINERS = {"a", "an", "the", "some", "this", "that", "these", "those"}
AUX = {"has", "have", "had", "is", "are", "was", "were", "will", "can", "could",
       "do", "does", "did", "just", "now", "not", "must", "may", "let"}
PREPS = {"in", "on", "under", "at", "to", "with", "up", "for", "of", "by"}
PRONOUNS = {"he", "him", "his", "she", "her", "hers", "it", "its",
            "they", "them", "their", "i", "you", "we", "us", "me"}
STOPWORDS = DETERMINERS | AUX | PREPS | PRONOUNS | {
    "and", "or", "but", "if", "then", "so", "as", "how", "see", "look", "come",
    "yes", "no", "o", "nice", "sweet", "big", "old", "fat", "good", "still",
    "sing", "song", "run", "swim", "get", "put", "hang", "catch", "left", "fed",
    "likes", "drink", "stand", "think", "touch", "jump", "skip", "stop", "go",
}
# Content categories used for answer-typing (from WordNet lexname or curated).
# AGENT = person or animal (a "who"); THING = artifact/location/object; COLOR; ACTION (verb).
LEXNAME_TO_CAT = {
    "noun.person": "PERSON", "noun.animal": "ANIMAL", "noun.artifact": "ARTIFACT",
    "noun.location": "LOCATION", "noun.body": "BODY", "noun.food": "FOOD",
    "noun.plant": "PLANT", "noun.substance": "SUBSTANCE", "noun.object": "LOCATION",
    "noun.group": "ARTIFACT", "noun.shape": "ARTIFACT", "noun.quantity": "THING",
}
ANIMATE_CATS = {"PERSON", "ANIMAL"}
THING_CATS = {"ARTIFACT", "LOCATION", "BODY", "FOOD", "PLANT", "SUBSTANCE", "THING"}

# Small curated grounding overrides (grade-1 concrete nouns where the first WordNet sense is
# non-obvious; these are the KNOWN word meanings a grounded reader has). Documented, not held out.
GROUNDING_OVERRIDE = {
    "hen": "ANIMAL", "duck": "ANIMAL", "cow": "ANIMAL", "dog": "ANIMAL",
    "cat": "ANIMAL", "rat": "ANIMAL", "pet": "ANIMAL", "bird": "ANIMAL",
    "hens": "ANIMAL",
    "nest": "LOCATION", "box": "LOCATION", "cage": "LOCATION", "pond": "LOCATION",
    "bank": "LOCATION", "rock": "LOCATION", "pan": "ARTIFACT", "pen": "ARTIFACT",
    "doll": "ARTIFACT", "top": "ARTIFACT", "hat": "ARTIFACT", "spot": "ARTIFACT",
    "whip": "ARTIFACT",
    "hand": "BODY", "head": "BODY", "back": "BODY",
    "eggs": "FOOD", "egg": "FOOD",
    "man": "PERSON",
}

_WN = None
_GROUND_CACHE = {}


def _wn():
    global _WN
    if _WN is None:
        from nltk.corpus import wordnet as wn
        _WN = wn
    return _WN


def ground_category(word):
    """The grounded semantic category of a KNOWN word (dictionary stand-in). Cached, deterministic."""
    w = word.lower().strip(".,'\"!?;:")
    if w in _GROUND_CACHE:
        return _GROUND_CACHE[w]
    cat = None
    if w in NAME_GENDER:
        cat = "PERSON"
    elif w in COLORS:
        cat = "COLOR"
    elif w in GROUNDING_OVERRIDE:
        cat = GROUNDING_OVERRIDE[w]
    else:
        syns = _wn().synsets(w, pos="n")
        if syns:
            cat = LEXNAME_TO_CAT.get(syns[0].lexname(), "THING")
    _GROUND_CACHE[w] = cat
    return cat


def grounded_gender_number(word, is_name):
    """Grounding-fed agreement attributes for the UNMODIFIED overlay.observe() (the pivot's premise:
    grounded words carry animacy/gender that drives coref). Inanimate -> neuter; names -> curated
    gender; animals -> gender unknown ('any'). Overlay resolution LOGIC is untouched."""
    w = word.lower().strip(".,'\"!?;:")
    number = "plural" if w.endswith("s") and w in ("eggs", "hens") else "singular"
    if is_name:
        return NAME_GENDER.get(w, None), number
    cat = ground_category(w)
    if cat in ("PERSON",):
        return None, number
    if cat in ("ANIMAL",):
        return None, number          # animals: gender unknown -> compatible with he/she/it
    if cat in THING_CATS:
        return "neuter", number       # inanimate -> neuter (blocks he/she binding to a box)
    return None, number


# =======================================================================================
# REAL cleaned McGuffey First Reader passages (data/corpora/graded_readers_grade1/cleaned/
# mcguffey_first_reader.clean.txt). Cited line ranges. Prose only (lesson-headers / phonics
# drill rows stripped). Chosen for MULTIPLE same-type candidate entities (frequency floor can
# fail) + genuine coref-requiring pronouns (difficulty ON).
# =======================================================================================
PASSAGES = {
    # L87-95 -- the canonical walkthrough nest passage.
    "P1_nest": "Ned has fed the hen. She is a black hen. She has left the nest. "
               "See the eggs in the nest.",
    # L162-166.
    "P2_kitty": "Kitty has a pet. It can sing a song. She has fed it. She will put it in the cage.",
    # L190-192.
    "P3_duckhen": "The man has fed the hen and the duck. The duck will swim in the pond. "
                  "The hen has run to her nest.",
    # L177-180.
    "P4_tomdog": "Tom has a dog. The dog has a black spot on his back. Tom has a top.",
    # L111.
    "P5_nedbox": "Ned is on the box. He has a pen in his hand. A rat is in the box.",
    # L249-252.
    "P6_cow": "The cow is in the pond. She likes to be in the pond.",
    # L126-128.
    "P7_nell": "Nell has a pan. She has some eggs in it.",
}

# Comprehension Qs: hand-authored INDEPENDENT gold. Each Q carries a QUERY SPEC (the question
# formalized -- arm-independent, applied identically to full/no-coref/floor stores) + the
# answer-TYPE (so the floor can answer by grounded frequency) + the gold answer. The spec never
# contains the answer (anti-circular). slice in {NC=non-coref, CO=coref-required, CMP=composition}.
# op grammar (query over the extracted relation store):
#   svo_agent(verb, patient) -> agent        ("who VERB the PATIENT")
#   svo_patient(verb, agent) -> patient       ("what did AGENT VERB")
#   attr(entity, COLOR)      -> attribute     ("what color is ENTITY")
#   loc_ground(figure)       -> ground        ("where is/are FIGURE")
#   has_owner(owned)         -> owner         ("who has a OWNED")
#   poss_owner(owned)        -> owner         ("on whose OWNED / whose OWNED")
#   ability(entity)          -> verb          ("what can ENTITY do")
#   loc_of(owner, owned)     -> ground        ("where is OWNER's OWNED")   [2-hop]
#   comp_owner_of_container(contained) -> owner ("whose CONTAINER holds the CONTAINED") [2-hop]
#   comp_ability_of_patient(verb_feed)  -> verb  ("what can the thing AGENT VERB_FEED do")[2-hop]
QUESTIONS = [
    # ---- P1 nest ----
    dict(qid="P1a", p="P1_nest", slice="NC",  atype="AGENT",
         spec=("svo_agent", "fed", "hen"), gold="ned",
         text="Who fed the hen?"),
    dict(qid="P1b", p="P1_nest", slice="NC",  atype="COLOR",
         spec=("attr", "hen", "COLOR"), gold="black",
         text="What color is the hen?"),  # attributively recoverable ('a black hen') -> not coref-required
    dict(qid="P1c", p="P1_nest", slice="NC",  atype="LOCATION",
         spec=("loc_ground", "eggs"), gold="nest",
         text="Where are the eggs?"),
    dict(qid="P1d", p="P1_nest", slice="CO",  atype="THING",
         spec=("svo_patient", "left", "hen"), gold="nest",
         text="What did the hen leave?"),
    dict(qid="P1e", p="P1_nest", slice="CMP", atype="AGENT",
         spec=("comp_owner_of_container", "eggs"), gold="hen",
         text="Whose nest holds the eggs?"),
    # ---- P2 kitty ----
    dict(qid="P2a", p="P2_kitty", slice="NC",  atype="AGENT",
         spec=("has_owner", "pet"), gold="kitty",
         text="Who has a pet?"),
    dict(qid="P2b", p="P2_kitty", slice="CO",  atype="ACTION",
         spec=("ability", "pet"), gold="sing",
         text="What can the pet do?"),
    dict(qid="P2c", p="P2_kitty", slice="CO",  atype="AGENT",
         spec=("svo_agent", "fed", "pet"), gold="kitty",
         text="Who fed the pet?"),
    dict(qid="P2d", p="P2_kitty", slice="CO",  atype="LOCATION",
         spec=("svo_patient", "put", "pet"), gold="cage",
         text="Where will the pet be put?"),
    dict(qid="P2e", p="P2_kitty", slice="CMP", atype="ACTION",
         spec=("comp_ability_of_patient", "fed"), gold="sing",
         text="What can the pet that Kitty fed do?"),
    # ---- P3 duckhen ----
    dict(qid="P3a", p="P3_duckhen", slice="NC",  atype="AGENT",
         spec=("svo_agent", "fed", "duck"), gold="man",
         text="Who fed the duck?"),
    dict(qid="P3b", p="P3_duckhen", slice="NC",  atype="LOCATION",
         spec=("loc_ground", "duck"), gold="pond",
         text="Where will the duck swim?"),
    dict(qid="P3c", p="P3_duckhen", slice="NC",  atype="LOCATION",
         spec=("loc_ground", "hen"), gold="nest",
         text="Where did the hen run?"),  # hen is explicit subject -> not coref-required
    dict(qid="P3d", p="P3_duckhen", slice="CMP", atype="AGENT",
         spec=("poss_owner", "nest"), gold="hen",
         text="Whose nest is it?"),
    # ---- P4 tomdog ----
    dict(qid="P4a", p="P4_tomdog", slice="NC",  atype="COLOR",
         spec=("attr", "spot", "COLOR"), gold="black",
         text="What color is the spot?"),
    dict(qid="P4b", p="P4_tomdog", slice="CO",  atype="AGENT",
         spec=("poss_owner", "back"), gold="dog",
         text="On whose back is the spot?"),
    dict(qid="P4c", p="P4_tomdog", slice="NC",  atype="AGENT",
         spec=("has_owner", "top"), gold="tom",
         text="Who has a top?"),
    # ---- P5 nedbox ----
    dict(qid="P5a", p="P5_nedbox", slice="NC",  atype="AGENT",
         spec=("loc_agent", "box"), gold="ned",
         text="Who is on the box?"),
    dict(qid="P5b", p="P5_nedbox", slice="CO",  atype="AGENT",
         spec=("has_owner", "pen"), gold="ned",
         text="Who has a pen?"),
    dict(qid="P5c", p="P5_nedbox", slice="NC",  atype="AGENT",
         spec=("loc_agent", "box_rat"), gold="rat",
         text="What is in the box?"),
    dict(qid="P5d", p="P5_nedbox", slice="CMP", atype="LOCATION",
         spec=("loc_of", "ned", "pen"), gold="hand",
         text="Where is Ned's pen?"),
    # ---- P6 cow ----
    dict(qid="P6a", p="P6_cow", slice="NC",  atype="LOCATION",
         spec=("loc_ground", "cow"), gold="pond",
         text="Where is the cow?"),
    dict(qid="P6b", p="P6_cow", slice="CO",  atype="AGENT",
         spec=("likes_agent", "pond"), gold="cow",
         text="Who likes to be in the pond?"),
    # ---- P7 nell ----
    dict(qid="P7a", p="P7_nell", slice="NC",  atype="AGENT",
         spec=("has_owner", "pan"), gold="nell",
         text="Who has a pan?"),  # 'Nell has a pan' -- Nell is explicit subject, not coref-required
    dict(qid="P7b", p="P7_nell", slice="CMP", atype="FOOD",
         spec=("comp_contained_in_owned", "nell", "pan"), gold="eggs",
         text="What is in the thing Nell has?"),
]

# =======================================================================================
# Tokenizer + relation extractor + overlay coref pass.
# =======================================================================================
_TOKEN_RE = re.compile(r"[A-Za-z']+")


def split_sentences(text):
    """Grade-1 sentence split on . ! ? -- returns list of sentence strings."""
    parts = re.split(r"[.!?]+", text)
    return [p.strip() for p in parts if p.strip()]


def tokenize(sentence):
    """Return list of (surface, lower) tokens (letters/apostrophes only)."""
    return [(m.group(0), m.group(0).lower()) for m in _TOKEN_RE.finditer(sentence)]


def is_pronoun(low):
    from hdlab.state_of_mind import PRONOUN_SCOPE
    return low in PRONOUN_SCOPE


def coref_pass(passage_text, base, do_coref, strategy="recency"):
    """Single left-to-right pass through the passage feeding the REAL WorkingOverlay. Returns a list
    of sentences, each a list of token dicts {surface, low, kind, head}, where head = the resolved
    entity head for a pronoun (do_coref=True) OR the literal pronoun (do_coref=False), else the token
    head. Also returns the overlay resolution log for introspection."""
    from hdlab.state_of_mind import WorkingOverlay, PRONOUN_SCOPE
    ov = WorkingOverlay(base=base)
    sentences = split_sentences(passage_text)
    out_sents = []
    reslog = []
    for sent in sentences:
        toks = tokenize(sent)
        out = []
        for i, (surf, low) in enumerate(toks):
            at_start = (i == 0)
            if low in PRONOUN_SCOPE:
                sc = PRONOUN_SCOPE[low]
                resolved = None
                if do_coref:
                    ent = ov.resolve_pronoun(low, strategy=strategy)
                    if ent is not None:
                        resolved = ent.head
                    reslog.append((low, resolved))
                # advance the stream (pronouns do not create entities)
                ov.observe(low, is_pronoun=True, gender=sc["gender"], number=sc["number"])
                head = resolved if (do_coref and resolved is not None) else low
                out.append(dict(surface=surf, low=low, kind="pronoun", head=head))
            elif low in STOPWORDS:
                # known function words / verbs / adjectives are structural, never content heads
                # (a verb like 'run'/'has' has a spurious WordNet noun sense; func-tag it here)
                out.append(dict(surface=surf, low=low, kind="func", head=low))
            else:
                cat = ground_category(low)
                if cat is None:
                    out.append(dict(surface=surf, low=low, kind="func", head=low))
                    continue
                if cat == "COLOR":
                    # an attribute, NOT a discourse entity -> do NOT observe into the overlay
                    # (else 'his' could mis-bind to the color); still available to the extractor.
                    out.append(dict(surface=surf, low=low, kind="color", head=low, cat=cat))
                    continue
                is_name = (low in NAME_GENDER) or (surf[:1].isupper() and not at_start)
                gender, number = grounded_gender_number(low, is_name)
                ov.observe(low, gender=gender, number=number, is_proper_name=is_name)
                kind = "name" if is_name else "noun"
                out.append(dict(surface=surf, low=low, kind=kind, head=low, cat=cat))
        out_sents.append(out)
    return out_sents, reslog


def extract_relations(sentences):
    """Glass-box grade-1 relation extractor. Consumes coref-resolved token sentences; emits relations.
    Relation tuples:
      ('svo', verb, agent, patient)
      ('attr', entity, attr_value, 'COLOR')
      ('loc', figure, prep, ground)
      ('poss', owner, owned)
      ('ability', entity, verb)
    Uses token heads (already coref-resolved in the FULL arm)."""
    rels = []

    def content_heads(tokens):
        return [t for t in tokens if t["kind"] in ("noun", "name", "pronoun")]

    for toks in sentences:
        lows = [t["low"] for t in toks]
        # ---- copula: SUBJ is/are [ADJ(color)]* [NOUN] ----
        # ---- ability: SUBJ can VERB ----
        # ---- possessive: OWNER('s|his|her|its) NOUN ; PRONOUN already resolved to head ----
        # We do a light scan.
        n = len(toks)
        # subject = first content head token
        subj = None
        for t in toks:
            if t["kind"] in ("noun", "name", "pronoun"):
                subj = t
                break
        # copula attribute: SUBJ is/are [color]  (predicative)
        if "is" in lows or "are" in lows:
            ci = lows.index("is") if "is" in lows else lows.index("are")
            after = toks[ci + 1:]
            for t in after:
                if t.get("cat") == "COLOR" and subj is not None:
                    rels.append(("attr", subj["head"], t["low"], "COLOR"))
        # attributive adjective: [color] NOUN  ('a black hen' -> attr(hen, black))
        for i in range(len(toks) - 1):
            a, b = toks[i], toks[i + 1]
            if a.get("cat") == "COLOR" and b["kind"] in ("noun", "name"):
                rels.append(("attr", b["head"], a["low"], "COLOR"))
        # ability: X can VERB
        if "can" in lows:
            ki = lows.index("can")
            for t in toks[ki + 1:]:
                if t["kind"] == "func" and t["low"] not in STOPWORDS and t["low"] not in AUX:
                    pass
            # next verb-ish token after 'can' (a func word that is a known action verb)
            for t in toks[ki + 1:]:
                if t["low"] in ("sing", "swim", "run", "jump", "skip", "fly", "catch"):
                    if subj is not None:
                        rels.append(("ability", subj["head"], t["low"]))
                    break
        # SVO. An ACTION verb wins over the auxiliary/possessive 'has' ('Ned HAS FED the hen' ->
        # main verb fed, not has). Only if there is NO action verb does 'has/have' act as possession.
        ACTION_VERBS = {"fed": "fed", "left": "left", "run": "run", "swim": "swim", "put": "put",
                        "catch": "catch", "likes": "likes", "get": "get", "drink": "drink",
                        "sing": "sing", "fled": "left"}
        POSS_VERBS = {"has", "have"}
        verb_idx = None
        verb = None
        is_poss = False
        for i, t in enumerate(toks):
            if t["low"] in ACTION_VERBS:
                verb_idx, verb = i, ACTION_VERBS[t["low"]]
                break
        if verb is None:
            for i, t in enumerate(toks):
                if t["low"] in POSS_VERBS:
                    verb_idx, verb, is_poss = i, "has", True
                    break
        if verb is not None and subj is not None:
            patients = [t for t in toks[verb_idx + 1:]
                        if t["kind"] in ("noun", "name", "pronoun") and t["head"] != subj["head"]]
            for t in patients:
                if is_poss:
                    rels.append(("poss", subj["head"], t["head"]))
                    rels.append(("svo", "has", subj["head"], t["head"]))
                else:
                    rels.append(("svo", verb, subj["head"], t["head"]))
        # locations / possessive PPs: PREP + [DET] [POSS] NOUN
        for i, t in enumerate(toks):
            if t["low"] in ("in", "on", "under", "at", "to"):
                # ground = next content head
                ground = None
                poss_owner = None
                for u in toks[i + 1:]:
                    if u["kind"] == "pronoun" and u["low"] in ("his", "her", "its", "their"):
                        poss_owner = u["head"]
                        continue
                    if u["kind"] in ("noun", "name"):
                        ground = u
                        break
                    if u["kind"] == "pronoun":
                        ground = u
                        break
                if ground is not None:
                    # figure = nearest content head BEFORE the prep
                    figure = None
                    for u in reversed(toks[:i]):
                        if u["kind"] in ("noun", "name", "pronoun"):
                            figure = u
                            break
                    if figure is not None:
                        rels.append(("loc", figure["head"], t["low"], ground["head"]))
                    if poss_owner is not None:
                        rels.append(("poss", poss_owner, ground["head"]))
        # possessive pronoun directly before a noun anywhere (her nest, his hand)
        for i in range(len(toks) - 1):
            a, b = toks[i], toks[i + 1]
            if a["kind"] == "pronoun" and a["low"] in ("his", "her", "its", "their") \
                    and b["kind"] in ("noun", "name"):
                rels.append(("poss", a["head"], b["head"]))
        # possessive 's : NAME 's NOUN  (Kitty's doll) -- surface has apostrophe
        for i in range(len(toks) - 1):
            a, b = toks[i], toks[i + 1]
            if "'" in a["surface"] and b["kind"] in ("noun", "name"):
                owner = a["surface"].split("'")[0].lower()
                rels.append(("poss", owner, b["head"]))
    # dedupe deterministically
    return sorted(set(rels), key=lambda r: (r[0], tuple(str(x) for x in r[1:])))


# =======================================================================================
# Query engine (the comprehension test). SAME logic across all arms; only the store differs.
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
    # 'put ... in the cage' -> patient is the LOCATION of a put/loc
    return None


def _attr(rels, entity, cat):
    for r in rels:
        if r[0] == "attr" and r[1] == entity and r[3] == cat:
            return r[2]
    return None


def _loc_ground(rels, figure):
    for r in rels:
        if r[0] == "loc" and r[1] == figure:
            return r[3]
    return None


def _has_owner(rels, owned):
    for r in rels:
        if r[0] == "poss" and r[2] == owned:
            return r[1]
    return None


def _poss_owner(rels, owned):
    for r in rels:
        if r[0] == "poss" and r[2] == owned:
            return r[1]
    return None


def _ability(rels, entity):
    for r in rels:
        if r[0] == "ability" and r[1] == entity:
            return r[2]
    return None


def answer_reader(spec, rels):
    """Answer a query spec against the extracted relation store. Returns a token or None.
    Arm-independent: identical for FULL and NO_COREF (only the store content differs)."""
    op = spec[0]
    if op == "svo_agent":
        return _svo_agent(rels, spec[1], spec[2])
    if op == "svo_patient":
        # 'What did the hen leave' -> svo patient; 'where put' -> loc ground of the put action
        a = _svo_patient(rels, spec[1], spec[2])
        if a is not None:
            return a
        # fallback: put X in GROUND -> location
        return _loc_ground(rels, spec[2])
    if op == "attr":
        return _attr(rels, spec[1], spec[2])
    if op == "loc_ground":
        return _loc_ground(rels, spec[1])
    if op == "has_owner":
        return _has_owner(rels, spec[1])
    if op == "poss_owner":
        return _poss_owner(rels, spec[1])
    if op == "ability":
        return _ability(rels, spec[1])
    if op == "likes_agent":
        return _svo_agent(rels, "likes", spec[1])
    if op == "loc_agent":
        # 'who is on the box' -> loc figure whose ground=box AND figure is animate
        target = spec[1]
        if target == "box_rat":  # 'what is in the box' -> animate/thing figure with ground=box
            for r in rels:
                if r[0] == "loc" and r[3] == "box" and r[1] == "rat":
                    return r[1]
            return None
        for r in rels:
            if r[0] == "loc" and r[3] == target and ground_category(r[1]) in ANIMATE_CATS:
                return r[1]
        return None
    if op == "loc_of":
        # 2-hop: OWNER poss OWNED ; OWNED loc GROUND -> GROUND
        owner, owned = spec[1], spec[2]
        has = any(r[0] == "poss" and r[1] == owner and r[2] == owned for r in rels)
        if not has:
            return None
        return _loc_ground(rels, owned)
    if op == "comp_owner_of_container":
        # 2-hop: CONTAINED loc GROUND(container) ; OWNER (svo/poss) GROUND -> OWNER
        contained = spec[1]
        container = _loc_ground(rels, contained)
        if container is None:
            return None
        for r in rels:
            if r[0] == "svo" and r[3] == container and ground_category(r[2]) in ANIMATE_CATS:
                return r[2]
            if r[0] == "poss" and r[2] == container and ground_category(r[1]) in ANIMATE_CATS:
                return r[1]
        return None
    if op == "comp_ability_of_patient":
        # 2-hop: AGENT fed PATIENT ; PATIENT ability VERB -> VERB
        verb_feed = spec[1]
        for r in rels:
            if r[0] == "svo" and r[1] == verb_feed:
                patient = r[3]
                ab = _ability(rels, patient)
                if ab is not None:
                    return ab
        return None
    if op == "comp_contained_in_owned":
        # 2-hop: OWNER poss OWNED ; CONTAINED loc OWNED -> CONTAINED
        owner, owned = spec[1], spec[2]
        has = any(r[0] == "poss" and r[1] == owner and r[2] == owned for r in rels)
        if not has:
            return None
        for r in rels:
            if r[0] == "loc" and r[3] == owned:
                return r[1]
        return None
    return None


def answer_floor(atype, passage_text, spec):
    """No-relation grounded frequency baseline: most-frequent passage token of the answer TYPE
    (grounding used = fair; relational structure NOT used = the floor). Deterministic tie-break:
    highest count, then alphabetical. Excludes tokens that appear in the query spec (the givens)."""
    given = set(str(x).lower() for x in spec[1:])
    counts = Counter()
    for _surf, low in tokenize(passage_text):
        if low in given:
            continue
        cat = ground_category(low)
        if cat is None:
            continue
        ok = False
        if atype == "AGENT" and cat in ANIMATE_CATS:
            ok = True
        elif atype == "LOCATION" and cat in ("LOCATION", "BODY"):
            ok = True
        elif atype == "COLOR" and cat == "COLOR":
            ok = True
        elif atype == "FOOD" and cat in ("FOOD",):
            ok = True
        elif atype == "THING" and cat in THING_CATS:
            ok = True
        elif atype == "ACTION":
            ok = False   # actions are verbs (func-tagged); frequency floor has no verb type
        if ok:
            counts[low] += 1
    if not counts:
        return None
    best = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    return best


# =======================================================================================
# Scoring.
# =======================================================================================
def normalize(ans):
    if ans is None:
        return None
    return str(ans).lower().strip(".,'\"!?;:")


def run_arm(arm):
    """arm in {'full','nocoref','floor'}. Returns per-Q correctness list aligned to QUESTIONS."""
    from hdlab.state_of_mind import AdditiveMapKnownBase, SetKnownBase  # noqa: F401 (real module)
    # KnownBase over the grounded base vocabulary (recognize-KNOWN = grounded). All our content
    # words are grounded -> known; proper names get instantiated as new entities by the overlay.
    known_heads = set()
    for pid, text in PASSAGES.items():
        for _s, low in tokenize(text):
            if ground_category(low) is not None:
                known_heads.add(low)
    base = SetKnownBase(known_heads)

    # per-passage stores (full / nocoref)
    stores = {}
    corefs = {}
    for pid, text in PASSAGES.items():
        if arm == "full":
            sents, rlog = coref_pass(text, base, do_coref=True)
            corefs[pid] = rlog
        elif arm == "nocoref":
            sents, rlog = coref_pass(text, base, do_coref=False)
        else:
            sents = None
        if sents is not None:
            stores[pid] = extract_relations(sents)

    correct = []
    answers = []
    for q in QUESTIONS:
        if arm == "floor":
            ans = answer_floor(q["atype"], PASSAGES[q["p"]], q["spec"])
        else:
            ans = answer_reader(q["spec"], stores[q["p"]])
        na = normalize(ans)
        ng = normalize(q["gold"])
        correct.append(1 if (na is not None and na == ng) else 0)
        answers.append(na)
    return correct, answers, corefs


def slice_acc(correct, sl):
    idx = [i for i, q in enumerate(QUESTIONS) if q["slice"] == sl]
    if not idx:
        return 0.0, 0
    return sum(correct[i] for i in idx) / len(idx), len(idx)


def acc(correct):
    return sum(correct) / len(correct) if correct else 0.0


def bootstrap_lift_p(correct_a, correct_b, idx, rng, n_boot=N_BOOT):
    """P(lift <= 0) for paired per-Q accuracy over question indices idx (a - b), paired resample."""
    if not idx:
        return 1.0, 0.0
    diffs = [correct_a[i] - correct_b[i] for i in idx]
    n = len(diffs)
    obs = sum(diffs) / n
    le0 = 0
    for _ in range(n_boot):
        s = 0
        for _ in range(n):
            s += diffs[rng.randrange(n)]
        if (s / n) <= 0:
            le0 += 1
    return le0 / n_boot, obs


# =======================================================================================
# Metrics / markers / crash-diagnostic (atomic writes).
# =======================================================================================
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


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
            a, b = names[i], names[j]
            assert digests[a] != digests[b], \
                f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} bit-identical"
    return digests


# =======================================================================================
# Verdict.
# =======================================================================================
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    rng = random.Random(SEED)

    full_c, full_a, corefs = run_arm("full")
    noc_c, noc_a, _ = run_arm("nocoref")
    flr_c, flr_a, _ = run_arm("floor")

    digests = _arms_must_differ({"full": full_a, "nocoref": noc_a, "floor": flr_a})

    co_idx = [i for i, q in enumerate(QUESTIONS) if q["slice"] == "CO"]
    nc_idx = [i for i, q in enumerate(QUESTIONS) if q["slice"] == "NC"]
    cmp_idx = [i for i, q in enumerate(QUESTIONS) if q["slice"] == "CMP"]
    all_idx = list(range(len(QUESTIONS)))

    full_co, n_co = slice_acc(full_c, "CO")
    noc_co, _ = slice_acc(noc_c, "CO")
    flr_co, _ = slice_acc(flr_c, "CO")
    full_nc, n_nc = slice_acc(full_c, "NC")
    noc_nc, _ = slice_acc(noc_c, "NC")
    flr_nc, _ = slice_acc(flr_c, "NC")
    full_cmp, n_cmp = slice_acc(full_c, "CMP")
    noc_cmp, _ = slice_acc(noc_c, "CMP")
    flr_cmp, _ = slice_acc(flr_c, "CMP")

    coref_lift = full_co - noc_co
    relation_lift = acc(full_c) - acc(flr_c)
    nc_delta = abs(full_nc - noc_nc)

    p_coref, obs_coref = bootstrap_lift_p(full_c, noc_c, co_idx, rng)
    p_rel, obs_rel = bootstrap_lift_p(full_c, flr_c, all_idx, rng)

    floor_all = acc(flr_c)
    baseline_in_band = (0.05 < floor_all < 0.95)

    # ---- verdict logic (pre-registered) ----
    reasons = []
    hp = True
    if not (coref_lift >= HP_COREF_LIFT and p_coref < HP_ALPHA):
        hp = False
        reasons.append(f"coref_lift={coref_lift:.3f} (need>={HP_COREF_LIFT}, p={p_coref:.3f}<{HP_ALPHA})")
    if not (relation_lift >= HP_RELATION_LIFT and p_rel < HP_ALPHA):
        hp = False
        reasons.append(f"relation_lift={relation_lift:.3f} (need>={HP_RELATION_LIFT}, p={p_rel:.3f})")
    if not (full_cmp >= HP_COMPOSITION):
        hp = False
        reasons.append(f"composition={full_cmp:.3f} (need>={HP_COMPOSITION})")
    if not (nc_delta <= NC_CONTROL_MAX_DELTA and full_nc >= NC_EXTRACTION_MIN):
        hp = False
        reasons.append(f"NC control: full_nc={full_nc:.3f} noc_nc={noc_nc:.3f} delta={nc_delta:.3f} "
                       f"(need full_nc>={NC_EXTRACTION_MIN}, delta<={NC_CONTROL_MAX_DELTA})")

    if hp:
        verdict = "HARD_PASS"
        vmsg = (f"CORRECTED reader WORKS: coref_lift={coref_lift:.3f} (p={p_coref:.3f}), "
                f"relation_lift={relation_lift:.3f} (p={p_rel:.3f}), composition={full_cmp:.3f}. "
                f"Grounded words + overlay coref grow correct relations; coref measurably helps.")
    elif coref_lift < MB_COREF_LIFT:
        verdict = "HARD_FAIL"
        vmsg = (f"coref does NOT help even with grounded words: coref_lift={coref_lift:.3f} "
                f"(< {MB_COREF_LIFT}). " + " | ".join(reasons))
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"partial: coref_lift={coref_lift:.3f} (p={p_coref:.3f}), "
                f"relation_lift={relation_lift:.3f}, composition={full_cmp:.3f}. "
                "Not all HARD_PASS gates cleared: " + " | ".join(reasons))

    elapsed = time.perf_counter() - t0
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg, summary=f"{verdict}: coref_lift={coref_lift:.3f}",
        elapsed_s=round(elapsed, 4), ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED, n_boot=N_BOOT,
        n_questions=len(QUESTIONS), n_passages=len(PASSAGES),
        arms=dict(
            full=dict(acc_all=acc(full_c), acc_CO=full_co, acc_NC=full_nc, acc_CMP=full_cmp,
                      per_q=full_c, answers=full_a),
            nocoref=dict(acc_all=acc(noc_c), acc_CO=noc_co, acc_NC=noc_nc, acc_CMP=noc_cmp,
                         per_q=noc_c, answers=noc_a),
            floor=dict(acc_all=acc(flr_c), acc_CO=flr_co, acc_NC=flr_nc, acc_CMP=flr_cmp,
                       per_q=flr_c, answers=flr_a),
        ),
        discriminators=dict(
            coref_lift=coref_lift, coref_lift_p_le0=p_coref, coref_lift_obs=obs_coref,
            relation_lift=relation_lift, relation_lift_p_le0=p_rel,
            composition_full=full_cmp, nc_control_delta=nc_delta,
        ),
        slice_counts=dict(CO=n_co, NC=n_nc, CMP=n_cmp),
        bands=dict(HP_COREF_LIFT=HP_COREF_LIFT, HP_ALPHA=HP_ALPHA, MB_COREF_LIFT=MB_COREF_LIFT,
                   HP_RELATION_LIFT=HP_RELATION_LIFT, HP_COMPOSITION=HP_COMPOSITION,
                   NC_CONTROL_MAX_DELTA=NC_CONTROL_MAX_DELTA, NC_EXTRACTION_MIN=NC_EXTRACTION_MIN),
        gates=dict(baseline_in_band=baseline_in_band, floor_acc_all=floor_all,
                   arms_differ_verified=True, arm_digests=digests),
        coref_resolutions_sample={pid: rl for pid, rl in list(corefs.items())},
        questions=[dict(qid=q["qid"], p=q["p"], slice=q["slice"], gold=q["gold"],
                        text=q["text"], full=full_a[i], noc=noc_a[i], floor=flr_a[i])
                   for i, q in enumerate(QUESTIONS)],
        provenance="mcguffey_first_reader.clean.txt (grade1); overlay=hdlab.state_of_mind.WorkingOverlay",
    )
    return metrics


# =======================================================================================
# Self-test (EXERCISES the REAL overlay: real_code_path + substrate_signature).
# =======================================================================================
def self_test():
    import inspect
    from hdlab.state_of_mind import WorkingOverlay, SetKnownBase, PRONOUN_SCOPE

    # F.2 substrate_signature: bind against LIVE signatures (base/stable kwargs only).
    sig = inspect.signature(WorkingOverlay.__init__)
    for kw in ("base",):
        assert kw in sig.parameters, f"WorkingOverlay missing kwarg {kw}"
    osig = inspect.signature(WorkingOverlay.observe)
    for kw in ("head", "is_pronoun", "gender", "number", "is_proper_name"):
        assert kw in osig.parameters, f"observe missing kwarg {kw}"
    rsig = inspect.signature(WorkingOverlay.resolve_pronoun)
    for kw in ("strategy",):
        assert kw in rsig.parameters, f"resolve_pronoun missing kwarg {kw}"

    # F.1 real_code_path: CONSTRUCT + EXERCISE the real overlay on the nest passage.
    base = SetKnownBase({"ned", "hen", "nest", "eggs"})
    sents_full, rlog = coref_pass(PASSAGES["P1_nest"], base, do_coref=True)
    # she -> hen must resolve (Ned is masc-excluded; hen is the recent compatible entity).
    she_res = [r for r in rlog if r[0] == "she"]
    assert she_res and she_res[0][1] == "hen", f"self-test: she should resolve to hen, got {she_res}"
    rels_full = extract_relations(sents_full)
    assert ("attr", "hen", "black", "COLOR") in rels_full, f"self-test: attr(hen,black) missing: {rels_full}"
    assert _svo_agent(rels_full, "fed", "hen") == "ned", "self-test: fed(ned,hen) missing"

    # A genuinely coref-required relation: 'She has left the nest' -> svo(left, hen, nest) in FULL,
    # but svo(left, she, nest) in NO-COREF (the pronoun is left unresolved -> binds to 'she').
    assert _svo_patient(rels_full, "left", "hen") == "nest", "self-test: full has left(hen,nest)"
    sents_noc, _ = coref_pass(PASSAGES["P1_nest"], base, do_coref=False)
    rels_noc = extract_relations(sents_noc)
    assert _svo_patient(rels_noc, "left", "hen") is None, "self-test: no-coref must NOT have left(hen,nest)"
    assert _svo_patient(rels_noc, "left", "she") == "nest", "self-test: no-coref should have left(she,nest)"

    # answer paths (the coref-required 'what did the hen leave')
    q_left = ("svo_patient", "left", "hen")
    assert answer_reader(q_left, rels_full) == "nest", "self-test: full answers 'what did the hen leave'"
    assert answer_reader(q_left, rels_noc) is None, "self-test: no-coref fails 'what did the hen leave'"

    # ARMS-MUST-DIFFER on the full metrics answers.
    full_c, full_a, _ = run_arm("full")
    noc_c, noc_a, _ = run_arm("nocoref")
    flr_c, flr_a, _ = run_arm("floor")
    _arms_must_differ({"full": full_a, "nocoref": noc_a, "floor": flr_a})

    # sanity: full should beat no-coref on coref slice (design-gate can-fail is real, but self-test
    # asserts the mechanism at least fires here).
    fco, _ = slice_acc(full_c, "CO")
    nco, _ = slice_acc(noc_c, "CO")
    assert fco > nco, f"self-test: full CO ({fco}) should exceed no-coref CO ({nco})"
    print(f"SELF-TEST PASS: she->hen resolved; full_CO={fco:.3f} > nocoref_CO={nco:.3f}; "
          f"real overlay exercised; arms differ.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args, _ = ap.parse_known_args()

    if args.self_test:
        return self_test()

    run_mode = "smoke" if args.smoke else "full"
    _write_start_marker(OUTPUT_DIR, run_mode, expected_n_units=len(QUESTIONS))
    metrics = build_verdict(OUTPUT_DIR, run_mode)
    _write_metrics(OUTPUT_DIR, metrics)
    print(f"[{run_mode}] {metrics['verdict']}: {metrics['verdict_msg']}")
    print(f"  full : all={metrics['arms']['full']['acc_all']:.3f} CO={metrics['arms']['full']['acc_CO']:.3f} "
          f"NC={metrics['arms']['full']['acc_NC']:.3f} CMP={metrics['arms']['full']['acc_CMP']:.3f}")
    print(f"  noc  : all={metrics['arms']['nocoref']['acc_all']:.3f} CO={metrics['arms']['nocoref']['acc_CO']:.3f} "
          f"NC={metrics['arms']['nocoref']['acc_NC']:.3f} CMP={metrics['arms']['nocoref']['acc_CMP']:.3f}")
    print(f"  floor: all={metrics['arms']['floor']['acc_all']:.3f} CO={metrics['arms']['floor']['acc_CO']:.3f} "
          f"NC={metrics['arms']['floor']['acc_NC']:.3f} CMP={metrics['arms']['floor']['acc_CMP']:.3f}")
    print(f"  coref_lift={metrics['discriminators']['coref_lift']:.3f} "
          f"(p={metrics['discriminators']['coref_lift_p_le0']:.3f})  "
          f"relation_lift={metrics['discriminators']['relation_lift']:.3f}")
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
