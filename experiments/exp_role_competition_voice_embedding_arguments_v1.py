"""pri 103 -- THE ROLE COMPETITION: voice from the auxiliary frame, the embedded/inverted configuration, and an argument
class wide enough to label whatever fills the slot.

BRAIN COMPUTATION (PINNED at the computational level -- Bates & MacWhinney Competition Model 1982/1989; MacWhinney 1987;
McDonald & MacWhinney 1989): a nominal's grammatical role is decided by PARALLEL competition of surface CUES, each carrying
a LEARNED VALIDITY (availability x reliability) read WITHIN the configuration it applies to; activation(role) =
log P(role) + [log P(role|config) - log P(role)] + SUM_cues [log P(role|config,value) - log P(role|config)], softmax = the
posterior. This experiment does NOT change that operation. It changes WHAT THE CUES READ, on five points where the built
cue set reads a surface proxy where the brain reads a structure:

  1. VOICE IS THE AUXILIARY FRAME OF *THIS* PREDICATE, NOT A SENTENCE-WIDE PATTERN. The built cue calls
     `is_passive_clause(toks, pos, h)` -- whose third parameter is `window`, so the head index is passed as a window and the
     test is run over the WHOLE SENTENCE. Any be+participle anywhere makes every nominal in the sentence read
     "passive_weak". The brain reads the auxiliary chain of the predicate it is integrating (be/get + V-en = passive;
     have + V-en = perfect ACTIVE; be + V-ing = progressive ACTIVE), and that chain is available as the predicate's own AUX
     dependents -- which also recovers INVERSION ("Attached is a spreadsheet": the aux FOLLOWS the participle).
  2. ARGUMENT RANK IS OVER THE VERB'S ARGUMENTS, NOT OVER TOKENS. The built `post_slot` counts every NOMINAL TOKEN between
     the verb and the nominal, so an NP-internal compound ("criticized President Bush") makes the object the "second"
     post-verbal nominal. The Competition Model's first-noun/second-noun cue is over ARGUMENTS: count the verb's own
     nominal DEPENDENTS. The same rank cue was missing entirely on the PRE-verbal side, where it separates a relativizer
     filler from the embedded subject ("the aid that Darfur needs": `that` is first, `Darfur` is nearest = the subject) --
     the active-filler configuration (Frazier & Clifton 1989), the same one the organ's PATIENT arm reads as `gap_config`.
  3. AN EXPLETIVE DOES NOT FILL THE SUBJECT SLOT. "there is/are X" is a stored CONSTRUCTION (Goldberg 1995; MacWhinney's
     item-based constructions): the pre-verbal slot is occupied by a non-referential expletive and the notional subject
     FOLLOWS. The organ already reads this construction on the AGENT side (`_existential_agent`); the label competition did
     not, so existential subjects read as objects.
  4. CASE IS LEXICAL. English marks oblique roles with a PREPOSITION, and WHICH preposition is the cue value (Bates &
     MacWhinney: case marking is a top cue). The built cue collapses every preposition but by/of into "other", so the verb
     PARTICLE of a phrasal verb ("worked OUT a deal", "checking OUT my options") carries the same validity as a locative
     "in" and pushes objects to oblique. Lexicalising the value lets each preposition learn its own validity, and the
     Dirichlet shrinkage already in `strengths_from_counts` IS the backoff for rare ones. The scan must also STOP at a
     relativizer ("in which KENNEDY joined": "in" governs "which", not "KENNEDY").
  5. AN ARGUMENT IS WHATEVER FILLS THE SLOT. `NOMINAL = {NOUN, PROPN, PRON}` means a quantifier / numeral / nominalised
     adjective head ("Many were talking", "One of the pictures shows", "keeping most of his money") is NEVER LABELLED. The
     brain labels the filler; the category of the filler is itself a CUE (`selfcat`), so an ADJ under a NOUN head still
     learns OTHER (amod) from the counts -- no hand rule.
  Plus the COPULA cue generalised to both orders (inverted "Here is a draft") and the head-class inventory widened so an
  ADV/ADP/SYM/INTJ predicate is not collapsed into one OTHERH bucket.

Knowledge stays COUNTS (the asset), strengths a pure function of the counts (`GRA.strengths_from_counts`), and the online
`observe_role_outcome` path keeps working unchanged.

INSTRUMENT CORRECTION (measured here, the first result): the strategy diagnostic `_diag_roles_by_clause_type.py` reads its
gold through `tools/build_attachment_validities.sentences`, which does `rels.append(c[7].split(":")[0])` -- it STRIPS UD
subtypes. Gold `nsubj:pass` therefore arrives as `nsubj`, so every CORRECTLY labelled passive subject was scored as a miss.
All 41 "nsubj -> nsubj:pass confusions" in the brief are that artifact: on the true gold the labeler's PASS_SUBJ recall is
1.000 (embedded, n=16) and 0.750 (matrix, n=32) and it never calls an active subject passive under gold heads.

Run:  python experiments/exp_role_competition_voice_embedding_arguments_v1.py --self-test
      python experiments/exp_role_competition_voice_embedding_arguments_v1.py --cache     # perceive train+test once
      python experiments/exp_role_competition_voice_embedding_arguments_v1.py --run [--wide-adv] [--penn] [--ablate]
      python experiments/exp_role_competition_voice_embedding_arguments_v1.py --agent     # the board agent-dimension probe
      python experiments/exp_role_competition_voice_embedding_arguments_v1.py --emit      # write the candidate table
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
os.environ.setdefault("PYTHONHASHSEED", "0")
import json
import pickle
import sys
import time
from collections import Counter, defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments._seed_checkpoint import get_output_dir
from hdlab import graded_role_assigner as GRA
from hdlab.animacy_lexicon import lookup_animacy
from hdlab.graded_competition import net_activation
from hdlab.thematic_role_labeler import _is_participle, is_passive_clause, lemma_verb

UD = os.path.join(REPO, "data", "corpora", "ud_english_ewt")
TRAIN = os.path.join(UD, "en_ewt-ud-train.conllu")
TEST = os.path.join(UD, "en_ewt-ud-test.conllu")
TEST_CAP = 700
ROLE_CLASSES = GRA.ROLE_CLASSES
ROLE_TO_DEP = GRA.ROLE_TO_DEP
K = len(ROLE_CLASSES)
RIX = {r: k for k, r in enumerate(ROLE_CLASSES)}

NOMINAL = frozenset(GRA.NOMINAL)                                  # the built set: NOUN / PROPN / PRON
EXTRA = frozenset({"NUM", "ADJ", "DET", "SYM", "X"})              # + quantifier / numeral / nominalised-adjective heads
EXTRA_ADV = frozenset(EXTRA | {"ADV"})                            # swept: locative/temporal pro-forms ("somewhere")
WIDE = frozenset(NOMINAL | EXTRA)
WIDE_ADV = frozenset(NOMINAL | EXTRA_ADV)
_MODSCAN = frozenset({"ADJ", "NUM", "ADV", "DET"})
_POSS = frozenset({"'s", "'", "s'", "’s", "’"})


def is_arg_head(toks, pos, i, extra):
    """Is token i (1-based) the HEAD of an argument phrase? NOUN/PROPN/PRON always (the shipped population, unchanged);
    a NUM / ADJ / DET / SYM only when it is NOT an NP-internal modifier -- the Right-hand Head Rule (Williams 1981) and
    the DP-head rule (Abney 1987), the landed `hdlab.np_head_reduce` criterion, extended over the intervening modifier
    run ("a FEW nerves" -> modifier; "the very FEW who read" -> head; "MANY of them" -> head). Arc-free."""
    p = pos[i - 1]
    if p in NOMINAL:
        return True
    if p not in extra:
        return False
    j, steps = i, 0
    while j < len(pos) and steps < 4:
        q = pos[j]
        if q in ("NOUN", "PROPN"):
            return False
        if toks[j].lower() in _POSS:
            return False
        if q in _MODSCAN:
            j += 1; steps += 1; continue
        break
    return True


def arg_heads(toks, pos, extra):
    return frozenset(i for i in range(1, len(pos) + 1) if is_arg_head(toks, pos, i, extra))
HEADCLS = ("VERB", "AUX", "NOUN", "PROPN", "ADJ", "PRON", "NUM", "ADV", "ADP", "SYM", "INTJ")
_SPAN_POS = frozenset({"DET", "ADJ", "NUM", "ADV", "PART", "NOUN", "PROPN", "PRON", "SYM", "X"})
_OBJ_CASE = frozenset({"him", "her", "them", "me", "us", "whom", "himself", "herself", "themselves", "myself",
                       "ourselves", "itself"})
_SUBJ_CASE = frozenset({"he", "she", "they", "i", "we", "who"})
BE = frozenset({"be", "is", "am", "are", "was", "were", "been", "being", "'s", "'re", "'m", "ai"})
GET = frozenset({"get", "gets", "got", "gotten", "getting"})
HAVE = frozenset({"have", "has", "had", "having", "'ve", "'d"})
WHREL = frozenset({"who", "whom", "whose", "which", "that", "what", "where", "when", "why"})

MODALS = frozenset({"will", "would", "shall", "should", "can", "could", "may", "might", "must", "do", "does", "did",
                    "'ll", "'d", "'ve", "ca", "wo"})
AUXWORDS = frozenset(BE | GET | HAVE | MODALS)
ALL_FLAGS = ("voice", "rank", "rank_gate", "expl", "exconfig", "prep", "prep_lex", "cop", "headcls",
              "selfcat", "selfcat_full", "relform", "constr_ungated", "fgconfig", "prep_prt")
FLAGS_OFF = {f: False for f in ALL_FLAGS}
# THE LANDED CONFIGURATION (every member measured; the three OFF members are REFUTED-AS-BUILT with numbers below).
FLAGS_ON = dict({f: False for f in ALL_FLAGS}, rank=True, rank_gate=True, expl=True, exconfig=True, prep=True,
                cop=True, headcls=True, prep_lex=True)
# ACCRUAL RELIABILITY GATE (swept operating point): a comprehension outcome teaches the cue validities only when the
# governor believed its own attachment (P(head) >= this). The brain consolidates what it UNDERSTOOD, not every parse it
# guessed. 0.0 / 0.5 / 0.8 swept: 0.5 is the operating point (gold-heads core +0.044 vs +0.025 ungated).
ACCRUE_MIN_CONF = 0.5


def coarse_of(dep):
    """Gold coarse role from a FULL UD deprel (subtypes preserved -- see the instrument correction above)."""
    d = (dep or "").split(":")[0]
    full = dep or ""
    if full.startswith("nsubj:pass") or full == "nsubjpass":
        return "PASS_SUBJ"
    if d in ("nsubj", "csubj"):
        return "SUBJ"
    if d == "iobj":
        return "IOBJ"
    if d in ("obj", "dobj"):
        return "OBJ"
    if full == "obl:agent":
        return "BY_AGENT"
    if full == "nmod:poss":
        return "OTHER"
    if d in ("obl", "nmod"):
        return "OBL"
    return "OTHER"


def sentences(path, cap=None):
    """UD reader that KEEPS the deprel subtype (the instrument correction)."""
    out, toks, pos, heads, rels = [], [], [], [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if toks:
                    out.append((toks, pos, heads, rels))
                toks, pos, heads, rels = [], [], [], []
                if cap and len(out) >= cap:
                    break
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if "-" in c[0] or "." in c[0]:
                continue
            toks.append(c[1]); pos.append(c[3]); heads.append(int(c[6])); rels.append(c[7])
    if toks and (not cap or len(out) < cap):
        out.append((toks, pos, heads, rels))
    return out


# ================================================================================================ THE CUE SET (v3)
HEADCLS_SHIPPED = ("VERB", "AUX", "NOUN", "PROPN", "ADJ", "PRON", "NUM")


def _hcls(pos, h, wide=True):
    if not h or h < 1 or h > len(pos):
        return "ROOT"
    p = pos[h - 1]
    return p if p in (HEADCLS if wide else HEADCLS_SHIPPED) else "OTHERH"


def aux_frame(toks, pos, h):
    """The predicate's auxiliary frame read from the SURFACE, CLAUSE-LOCALLY (arc-free). Auxiliaries are closed-class
    function words that sit contiguously before their verb (adverbs and negation may intervene); in an INVERTED clause a
    clause-initial participle is followed by its aux ("Attached IS a spreadsheet"). Returns (chain, inverted).

    ARC-FREE ON PURPOSE (measured negative, this cell): reading the chain as the predicate's AUX *dependents* makes the
    cue inherit the governor's attachment noise at LEARNING time -- the be+participle bucket's reliability for PASS_SUBJ
    fell 0.719 -> 0.549 and subject recall lost 0.025 CI-separated. English auxiliary order is fixed, so the surface
    scan is the higher-validity read; only the CLAUSE BOUND and the inversion case need fixing, not the mechanism."""
    low = [t.lower() for t in toks]
    lo, hi = GRA.clause_bounds(toks, pos, h - 1)
    chain = []
    j = h - 2
    while j >= lo:
        w = low[j]
        p = pos[j] if j < len(pos) else None
        if p in ("ADV", "PART") or w in ("not", "n't"):
            j -= 1
            continue
        if p == "AUX" or w in AUXWORDS:
            chain.append(w)
            j -= 1
            continue
        break
    if not chain and (h - 1) == lo:                      # clause-initial predicate -> look RIGHT for the inverted aux
        k = h
        while k < hi and k < len(pos) and pos[k] == "ADV":
            k += 1
        if k < hi and k < len(pos) and (low[k] in BE or low[k] in GET):
            return [low[k]], True
    return chain, False


def voice_value(toks, pos, heads, h, penn=None):
    """VOICE read from the auxiliary frame of THIS predicate, clause-locally (cue 1). be/get + V-en = passive;
    have + V-en = perfect ACTIVE; be + V-ing = progressive ACTIVE; a bare participle with no aux = the reduced-passive
    garden path (its own value, so the learner sets its validity)."""
    chain, inverted = aux_frame(toks, pos, h)
    w = toks[h - 1]
    tag = penn[h - 1] if (penn is not None and h - 1 < len(penn)) else None
    if tag is not None:
        part, ger = tag == "VBN", tag == "VBG"
    else:
        part = _is_participle(w, pos[h - 1] if h - 1 < len(pos) else None)
        ger = w.lower().endswith("ing") and len(w) > 4
    hasbe = any(a in BE or a in GET for a in chain)
    if ger:
        return "progressive"
    if part and hasbe:
        return "passive_inv" if inverted else "passive"
    if part and any(a in HAVE for a in chain) and not hasbe:
        return "perfect_active"
    if part and not chain:
        return "passive_reduced"
    return "active"


def relative_frame(toks, pos, h):
    """The RELATIVE-CLAUSE (filler-gap) CONSTRUCTION: the clause containing the predicate at h opens with a relativizer
    (that / which / who / whom / whose). Like the existential, this is a stored construction with its OWN argument
    mapping -- inside it, "which pre-verbal argument is nearest the verb" decides subject vs. extracted object
    ("the man THAT came" vs "the aid THAT Darfur needs"), a contrast that is swamped when relative and main clauses
    share one configuration. Surface-only (arc-free)."""
    low = [t.lower() for t in toks]
    lo, hi = GRA.clause_bounds(toks, pos, h - 1)
    for j in range(lo, min(h - 1, hi)):
        p = pos[j] if j < len(pos) else None
        if low[j] in ("that", "which", "who", "whom", "whose") and p in ("PRON", "DET", "SCONJ"):
            return True
        if p in ("NOUN", "PROPN", "PRON", "VERB", "NUM", "ADJ"):
            return False                                   # a full argument opened the clause -> not relativizer-initial
    return False


def existential_frame(toks, pos, h):
    """The there-BE CONSTRUCTION (Goldberg 1995; a stored form-meaning pairing): a clause-initial expletive `there`
    before the predicate with no nominal between. In the Competition Model the construction is the CONFIGURATION within
    which cue validities are read -- so it belongs in the config key, not as one additive contrast fighting the general
    post-verbal-object configuration. Surface-only (arc-free)."""
    low = [t.lower() for t in toks]
    lo, hi = GRA.clause_bounds(toks, pos, h - 1)
    for j in range(lo, min(h - 1, hi)):
        if low[j] == "there" and (pos[j] if j < len(pos) else None) in ("PRON", "ADV", "DET"):
            if not any((pos[k] if k < len(pos) else None) in ("NOUN", "PROPN") for k in range(j + 1, h - 1)):
                return True
    return False


def prep_of(toks, pos, heads, i):
    """(form or None, far, particle) -- LEXICAL case marking (cue 4), the scan STOPPED at a relativizer, with a PARTICLE
    test (an ADP whose own head is a verb is a phrasal-verb particle, not a case marker for i)."""
    for j in range(1, i):
        if heads.get(j) == i and j - 1 < len(pos) and pos[j - 1] == "ADP":
            return toks[j - 1].lower(), False, False
    j, steps, crossed = i - 1, 0, False
    while j >= 1 and steps < 5:
        p = pos[j - 1]
        low = toks[j - 1].lower()
        if p == "ADP":
            hj = heads.get(j, 0)
            particle = bool(hj and 1 <= hj <= len(pos) and pos[hj - 1] in ("VERB", "AUX") and hj != i)
            return low, crossed, particle
        if low in WHREL:
            return None, False, False                       # relativizer = clause boundary for the case scan
        if p not in _SPAN_POS:
            return None, False, False
        if p in ("DET", "PRON"):                            # the NP's left edge
            if j >= 2 and pos[j - 2] == "ADP":
                hj = heads.get(j - 1, 0)
                particle = bool(hj and 1 <= hj <= len(pos) and pos[hj - 1] in ("VERB", "AUX") and hj != i)
                return toks[j - 2].lower(), crossed, particle
            return None, False, False
        if p in ("NOUN", "PROPN", "NUM"):
            crossed = True
        j -= 1
        steps += 1
    return None, False, False


RANK_TAU = 0.5      # SWEPT operating point: the head posterior above which the ARC-DEPENDENT rank cue votes


def cues_v3(toks, pos, heads, i, frames=None, penn=None, extra=EXTRA, flags=None, conf=None):
    """Categorical cue VALUES for the argument-head token i (1-based). Reads toks / pos / heads (+ the category organ's
    Penn arm, optional) only -- no gold, no labels. flags=FLAGS_OFF + argset=NOMINAL reproduces the shipped cue set."""
    fl = FLAGS_ON if flags is None else flags
    h = heads.get(i, 0) or 0
    low = toks[i - 1].lower()
    hc = _hcls(pos, h, fl.get("headcls"))
    order = "pre" if (h and i < h) else ("post" if h else "root")
    verbhead = hc in ("VERB", "AUX") and bool(h)
    cfgkey = "%s_%s" % (hc, order)
    if verbhead and fl.get("exconfig") and existential_frame(toks, pos, h):
        cfgkey += "_ex"                                   # the CONSTRUCTION is the configuration
    elif verbhead and fl.get("fgconfig") and relative_frame(toks, pos, h):
        cfgkey += "_rel"
    cues = {"config": cfgkey}
    # ---- cue 1: VOICE from the auxiliary frame of this predicate
    if verbhead:
        if fl.get("voice"):
            v = voice_value(toks, pos, heads, h, penn)
        else:
            vc = GRA.voice_cues(toks, pos, h)
            strong = bool(vc["vc_strong"] or vc["vc_get"] or vc["vc_being"])
            weak = bool(vc["vc_bypp"] or is_passive_clause(toks, pos, h))
            v = "passive_strong" if strong else ("passive_weak" if weak else "active")
        passive = v.startswith("passive")
        cues["voice_order"] = v + "_" + order
    else:
        passive = False
        cues["voice_order"] = "na"
    # ---- cue 4: LEXICAL case marking
    if fl.get("prep"):
        prep, far, particle = prep_of(toks, pos, heads, i)
    else:
        prep, far = GRA._prep_of(toks, pos, heads, i)
        particle = False
    if prep is None:
        cues["prep"] = "none"
    elif particle and fl.get("prep_prt"):
        cues["prep"] = "prt"
    elif prep == "by":
        cues["prep"] = "by_passive" if passive else "by"
    elif fl.get("prep_lex"):
        cues["prep"] = prep + ("_far" if far else "")
    elif prep == "of":
        cues["prep"] = "of_far" if far else "of"
    else:
        cues["prep"] = "other_far" if far else "other"
    # ---- cues 2/3: ARGUMENT RANK over the verb's own dependents, and the EXPLETIVE pre-verbal slot
    sib_pre = [j for j in range(1, h) if heads.get(j) == h and is_arg_head(toks, pos, j, extra)] if verbhead else []
    sib_post = ([j for j in range(h + 1, len(pos) + 1) if heads.get(j) == h and is_arg_head(toks, pos, j, extra)]
                if verbhead else [])
    # PRECISION GATE on the ARC-DEPENDENT rank cue (self-gating, the organ's `structure`/`byhead` pattern; Ernst &
    # Banks 2002 reliability weighting): rank is read off the governor's SIBLING set, so where the governor is unsure of
    # this nominal's attachment the cue abstains and the arc-free cues carry the decision. Measured: ungated, rank costs
    # the LIVE copular subject read 0.667 -> 0.623 (the copular head is right only 46.5% of the time under the arm).
    rank_on = bool(fl.get("rank")) and (conf is None or not fl.get("rank_gate") or conf.get(i, 1.0) >= RANK_TAU)
    if order == "post" and verbhead:
        if rank_on:
            between = sum(1 for j in sib_post if j < i)
        else:
            between = sum(1 for j in range(h + 1, i) if is_arg_head(toks, pos, j, extra))
        bare = [j for j in sib_post if j != i and prep_of(toks, pos, heads, j)[0] is None]
        pair = "pair" if (bare and prep is None) else "single"
        cues["post_slot"] = ("first" if between == 0 else "later") + "_" + pair
        if fl.get("expl"):
            eff = sib_pre
            if not eff:
                j, surf = h - 1, []
                while j >= 1:
                    pj = pos[j - 1]
                    if pj in ("PUNCT", "SCONJ", "CCONJ", "VERB"):
                        break
                    if is_arg_head(toks, pos, j, extra):
                        surf.append(j)
                    j -= 1
                eff = surf
            if not eff:
                cues["pre_slot"] = "empty"
            elif all(toks[j - 1].lower() == "there" for j in eff):
                cues["pre_slot"] = "expletive"
            else:
                cues["pre_slot"] = "filled"
        else:
            j, filled = h - 1, False
            while j >= 1:
                pj = pos[j - 1]
                if pj in ("PUNCT", "SCONJ", "CCONJ", "VERB"):
                    break
                if pj in NOMINAL:
                    filled = True
                    break
                j -= 1
            cues["pre_slot"] = "filled" if filled else "empty"
    else:
        cues["post_slot"] = "na"
        cues["pre_slot"] = "na"
    # ---- cue 2b: PRE-verbal argument RANK (the active-filler / relativizer configuration)
    if order == "pre" and verbhead and rank_on:
        nearer = sum(1 for j in sib_pre if j > i)
        cues["pre_rank"] = "nearest" if nearer == 0 else ("second" if nearer == 1 else "earlier")
    else:
        cues["pre_rank"] = "na"
    # ---- COPULA, both orders (inverted "Here is a draft")
    if h and not verbhead and fl.get("cop"):
        lo, hi = (i, h) if i < h else (h, i)
        between_aux = any(pos[j - 1] == "AUX" for j in range(lo + 1, hi))
        aux_dep = any(heads.get(j) == h and pos[j - 1] == "AUX" for j in range(1, len(pos) + 1))
        cues["cop"] = ("aux_between_" if between_aux else ("aux_dep_" if aux_dep else "none_")) + order
    elif order == "pre" and h and not verbhead:
        cues["cop"] = "aux_between" if any(pos[j - 1] == "AUX" for j in range(i + 1, h)) else "none"
    else:
        cues["cop"] = "na"
    # CASE, including the RELATIVE-PRONOUN forms. English case-marks its relative pronouns (who nominative / whom
    # accusative) and its unmarked relativizers (that / which) still MARK the clause as a filler-gap construction --
    # a distinct cue value, not "none" (Bates & MacWhinney: case marking is a top cue; Frazier & Clifton active filler).
    if fl.get("relform") and low in ("that", "which", "who", "whom", "what") and order == "pre" and verbhead:
        cues["case"] = "rel_" + low
    else:
        cues["case"] = "obj" if low in _OBJ_CASE else ("subj" if low in _SUBJ_CASE else "none")
    a = lookup_animacy(low, pos[i - 1])
    an = a.get("animacy") if isinstance(a, dict) else None
    cues["animacy"] = "anim" if an == "animate" else ("inan" if an == "inanimate" else "unk")
    if low in _OBJ_CASE or low in _SUBJ_CASE:
        cues["animacy"] = "anim"
    if verbhead and frames:
        fr = frames.get(lemma_verb(toks[h - 1]).lower())
        cues["frame"] = ("ditrans" if fr[0] / fr[1] >= 0.05 else "mono") if (fr and fr[1] >= 5) else "unk"
    else:
        cues["frame"] = "na"
    # ---- cue 5: the FILLER'S OWN CATEGORY. COLLAPSED over NOUN/PROPN/PRON by measurement: as a full 8-value inventory
    # this cue DOUBLE-COUNTS the animacy and case cues (a PRON is already marked animate + nominative), and every
    # common-noun subject then pays a negative contrast -- 77 canonical subjects flipped to OTHER, -0.10 CI-sep. The
    # informative contrast is only between "a referential nominal" and "a quantifier / numeral / nominalised adjective",
    # so the nominal classes share ONE value whose within-config contrast is ~0 (no double counting).
    if fl.get("selfcat"):
        cues["selfcat"] = "nom" if pos[i - 1] in NOMINAL else pos[i - 1]
    if fl.get("selfcat_full"):
        cues["selfcat"] = pos[i - 1]
    return cues


# ================================================================================================ learn / label
def accrue(rows, extra, flags, penn_on, frames, use_gold_heads=False, weighted=True, min_conf=0.0):
    """Accrue the Competition-Model cue COUNTS from reading. One comprehension outcome per argument head, weighted by the
    governor's own confidence in the attachment (reliability-weighted learning; the counts are the knowledge)."""
    prior = [0.0] * K
    cfg_counts = defaultdict(lambda: [0.0] * K)
    cue_counts = defaultdict(lambda: defaultdict(lambda: [0.0] * K))
    dec = 0.0
    for r in rows:
        toks, gpos, rels = r["toks"], r["gpos"], r["rels"]
        if use_gold_heads:
            pos = list(gpos)
            heads = {i: r["gheads"][i - 1] for i in range(1, len(toks) + 1)}
            penn = r["penn_g"] if penn_on else None
            conf = None
        else:
            pos, heads = r["ppos"], r["pheads"]
            penn = r["penn_p"] if penn_on else None
            conf = r["conf"] if weighted else None
        for i in range(1, len(toks) + 1):
            if not is_arg_head(toks, list(gpos), i, extra):
                continue
            w = 1.0 if conf is None else float(conf.get(i, 0.0))
            gate = min_conf
            if flags.get("constr_ungated") and gate > 0:
                hh = heads.get(i, 0) or 0
                if hh and 1 <= hh <= len(pos) and pos[hh - 1] in ("VERB", "AUX") and existential_frame(toks, pos, hh):
                    gate = 0.0        # the construction is recognised on the SURFACE, so every exposure teaches it
                    w = max(w, 0.25)  #   (item-based construction learning; the attachment uncertainty is not the
                                      #    uncertainty about the construction)
            if w <= 0 or (conf is not None and w < gate):
                continue
            g = RIX[coarse_of(rels[i - 1])]
            dec += w
            prior[g] += w
            cu = cues_v3(toks, pos, heads, i, frames, penn, extra, flags, conf)
            cfg = cu["config"]
            cfg_counts[cfg][g] += w
            for c, v in cu.items():
                if c != "config":
                    cue_counts[c]["%s|%s" % (cfg, v)][g] += w
    return {"prior": prior, "config": dict(cfg_counts),
            "cues": {c: dict(d) for c, d in cue_counts.items()}, "decisions": dec}


def table_from_counts(counts, frames, slot_capacity=None):
    b = GRA.strengths_from_counts(counts)
    return {"prior": b["prior"], "strength": b["strength"], "counts": counts, "lemma_frames": frames,
            "slot_capacity": slot_capacity}


def _supports(toks, pos, heads, i, tab, extra, flags, penn, conf=None):
    cu = cues_v3(toks, pos, heads, i, tab.get("lemma_frames"), penn, extra, flags, conf)
    S = {"prior": tab["prior"]}
    cfg = cu["config"]
    vec = tab["strength"].get("config", {}).get(cfg)
    if vec is not None:
        S["config"] = vec
    for c, v in cu.items():
        if c == "config":
            continue
        vec = tab["strength"].get(c, {}).get("%s|%s" % (cfg, v))
        if vec is not None:
            S[c] = vec
    return S


def activations(toks, pos, heads, tab, extra, flags, penn=None, conf=None):
    """The additive cue-competition activation vector per argument head."""
    out = {}
    for i in range(1, len(toks) + 1):
        if i - 1 >= len(pos) or not is_arg_head(toks, pos, i, extra):
            continue
        S = _supports(toks, pos, heads, i, tab, extra, flags, penn, conf)
        out[i] = np.asarray(net_activation(S, {c: 1.0 for c in S}), dtype=float)
    return out


def label_all(toks, pos, heads, tab, extra, flags, penn=None, conf=None):
    return {i: ROLE_TO_DEP[ROLE_CLASSES[int(np.argmax(A))]]
            for i, A in activations(toks, pos, heads, tab, extra, flags, penn, conf).items()}


def label_all_marg(toks, pos, heads, post, tab, extra, flags, penn=None, min_p=0.05):
    """PRECISION-WEIGHTED read: the heads rung hands DOWN a DISTRIBUTION, not a point (the organ's own
    `coarse_role_posterior_headmarg`, spec RESEARCH_attachment_organ_spec s3). P(role|i) = SUM_h P(h|i) *
    softmax(activation computed with i attached to h); the other tokens keep their MAP heads. Where the governor is
    confident this is byte-identical to the hard read; where it is not, the competition runs in every candidate frame
    in parallel and the roles are averaged under the attachment belief (Lewis & Vasishth parallel maintenance;
    MacDonald constraint satisfaction; Ernst & Banks reliability weighting)."""
    from hdlab.graded_competition import softmax as _sm
    out = {}
    for i in range(1, len(toks) + 1):
        if i - 1 >= len(pos) or not is_arg_head(toks, pos, i, extra):
            continue
        hp = (post or {}).get(i) or {}
        acc = np.zeros(K); tot = 0.0
        for h, pr in sorted(hp.items(), key=lambda kv: -kv[1]):
            if pr < min_p or h == i:
                continue
            hh = dict(heads); hh[i] = int(h)
            S = _supports(toks, pos, hh, i, tab, extra, flags, penn)
            acc += pr * _sm(net_activation(S, {c: 1.0 for c in S}), gain=1.0); tot += pr
        if tot <= 0:
            S = _supports(toks, pos, heads, i, tab, extra, flags, penn)
            acc = np.asarray(net_activation(S, {c: 1.0 for c in S}), dtype=float)
        out[i] = ROLE_TO_DEP[ROLE_CLASSES[int(np.argmax(acc))]]
    return out


def test_posteriors(out_dir, rows):
    """The attachment arm's exact single-root head posterior for every test token (cached)."""
    p = os.path.join(out_dir, "post_test.pkl")
    if os.path.exists(p):
        with open(p, "rb") as f:
            return pickle.load(f)
    import hdlab.attachment_arm as AA
    tab = AA.load_attachment_validities()
    out = []
    for r in rows:
        po = AA.head_posterior(list(r["toks"]), list(r["ppos"]), tab)
        out.append({i: {h: float(pp) for h, pp in d.items() if pp >= 0.02} for i, d in po.items()})
    with open(p, "wb") as f:
        pickle.dump(out, f, protocol=4)
    return out


def twin_table(tab, seed=17):
    """INFO-FREE TWIN: the learned strength VECTORS permuted across the cue VALUES of every cue (config included). The
    whole competition machinery runs, on a destroyed value->role mapping."""
    rng = np.random.default_rng(seed)
    st = {}
    for c, vals in tab["strength"].items():
        keys = list(vals.keys())
        perm = list(rng.permutation(len(keys)))
        st[c] = {keys[j]: vals[keys[perm[j]]] for j in range(len(keys))}
    return {"prior": tab["prior"], "strength": st, "counts": tab.get("counts"),
            "lemma_frames": tab.get("lemma_frames")}


CANDIDATE_TABLE = os.path.join(REPO, "data", "hook_state", "coarse_role_validities_pri103_v3.json")
_V3_TAB = None


def load_v3_table(path=None):
    """The candidate v3 validity table (counts on disk; strengths a pure function of the counts)."""
    global _V3_TAB
    if _V3_TAB is None or path:
        with open(path or CANDIDATE_TABLE, encoding="utf-8") as f:
            doc = json.load(f)
        b = GRA.strengths_from_counts(doc["counts"])
        t = {"prior": b["prior"], "strength": b["strength"], "counts": doc["counts"],
             "lemma_frames": doc.get("lemma_frames", {}), "slot_capacity": doc.get("slot_capacity")}
        if path:
            return t
        _V3_TAB = t
    return _V3_TAB


def coarse_roles_v3(toks, pos, heads, validities=None, head_posterior=None, extra=EXTRA, flags=None, penn=None):
    """THE PROPOSED ORGAN ENTRY POINT -- drop-in for `graded_role_assigner.coarse_roles`. Same Competition-Model
    operation (additive cue activation -> MAP); the v3 cue set; the ARGUMENT-HEAD population (NP-head-gated).
    `head_posterior` (the heads rung's graded hand-off) drives the rank cue's precision gate: where the governor does
    not believe its own attachment above RANK_TAU, the arc-dependent rank cue abstains and the arc-free cues decide."""
    tab = validities or load_v3_table()
    fl = FLAGS_ON if flags is None else flags
    conf = None
    if head_posterior:
        conf = {i: float((head_posterior.get(i) or {}).get(heads.get(i, 0), 1.0)) for i in head_posterior}
    return label_all(toks, pos, heads, tab, extra, fl, penn, conf)


# ================================================================================================ perception cache
def _penn_tagger():
    import hdlab.lexical_categories as LC
    return LC.LexicalCategories.load(LC.ASSET_PENN)


def build_cache(out_dir):
    """Perceive TRAIN and TEST once with the live BF chain (category organ -> attachment arm), with the attachment arm's
    exact single-root head posterior as the CONFIDENCE weight, plus the category organ's Penn-arm form tags."""
    import hdlab.attachment_arm as AA
    import hdlab.lexical_categories as LC
    lc = LC.get()
    pn = _penn_tagger()
    tab = AA.load_attachment_validities()
    for name, path, cap in (("test", TEST, TEST_CAP), ("train", TRAIN, None)):
        t0 = time.time()
        rows = []
        for toks, gpos, gheads, rels in sentences(path, cap=cap):
            ppos = lc.tag(list(toks))
            pheads = AA.heads(toks, ppos, tab)
            post = AA.head_posterior(list(toks), list(ppos), tab)
            conf = {i: float((post.get(i) or {}).get(h, 0.0)) for i, h in pheads.items()}
            rows.append({"toks": toks, "gpos": gpos, "gheads": gheads, "rels": rels, "ppos": ppos,
                         "pheads": pheads, "conf": conf, "penn_g": pn.tag(list(toks)), "penn_p": pn.tag(list(toks))})
        p = os.path.join(out_dir, "perc_%s.pkl" % name)
        with open(p, "wb") as f:
            pickle.dump(rows, f, protocol=4)
        print("[cache] %s: %d sentences in %.0fs -> %s" % (name, len(rows), time.time() - t0, p), flush=True)


def load_cache(out_dir, name):
    with open(os.path.join(out_dir, "perc_%s.pkl" % name), "rb") as f:
        return pickle.load(f)


def lemma_frames_from(rows):
    """The verb-frame knowledge in COUNTS (per lemma: recipients out of nominal dependents), accrued from reading."""
    lf = defaultdict(lambda: [0, 0])
    for r in rows:
        toks, gpos, gheads, rels = r["toks"], r["gpos"], r["gheads"], r["rels"]
        for i in range(1, len(toks) + 1):
            h = gheads[i - 1]
            if gpos[i - 1] in NOMINAL and h and gpos[h - 1] in ("VERB", "AUX"):
                f = lf[lemma_verb(toks[h - 1]).lower()]
                f[1] += 1
                f[0] += int((rels[i - 1] or "").split(":")[0] == "iobj")
    return {k: v for k, v in lf.items() if v[1] >= 5}


def slot_capacity_from(rows):
    n1, n2 = Counter(), Counter()
    for r in rows:
        toks, gpos, gheads, rels = r["toks"], r["gpos"], r["gheads"], r["rels"]
        by_verb = defaultdict(list)
        for i in range(1, len(toks) + 1):
            h = gheads[i - 1]
            if gpos[i - 1] in NOMINAL and h and gpos[h - 1] in ("VERB", "AUX"):
                by_verb[h].append(coarse_of(rels[i - 1]))
        for h, roles in by_verb.items():
            sc = Counter(GRA.ROLE_TO_SLOT.get(x) for x in roles if GRA.ROLE_TO_SLOT.get(x))
            for slot, c in sc.items():
                n1[slot] += 1
                if c >= 2:
                    n2[slot] += 1
    return {s: [int(n1[s]), int(n2[s])] for s in GRA.CORE_SLOTS}


# ================================================================================================ evaluation
EMBED = {"ccomp", "xcomp", "advcl", "acl", "csubj", "parataxis"}
TARGET = {"nsubj", "nsubj:pass", "obj"}


def clause_type(i, gpos, gheads, rels):
    h = gheads[i - 1]
    if h <= 0:
        return "matrix"
    if gpos[h - 1] not in ("VERB", "AUX"):
        return "copular"
    return "embedded" if rels[h - 1].split(":")[0] in EMBED else "matrix"


def evaluate(rows, tab, extra, flags, arm, penn_on, posts=None, min_p=0.05):
    """Per-item correctness, keyed by population -> [(sent_idx, tok_idx, correct)]."""
    pops = defaultdict(list)
    for si, r in enumerate(rows):
        toks, gpos, gheads, rels = r["toks"], r["gpos"], r["gheads"], r["rels"]
        if arm == "gold":
            pos = list(gpos)
            heads = {i: gheads[i - 1] for i in range(1, len(toks) + 1)}
            penn = r["penn_g"] if penn_on else None
        else:
            pos, heads = r["ppos"], r["pheads"]
            penn = r["penn_p"] if penn_on else None
        conf = None if arm == "gold" else r["conf"]
        roles = (label_all_marg(toks, pos, heads, posts[si], tab, extra, flags, penn, min_p)
                 if (posts is not None and arm != "gold") else label_all(toks, pos, heads, tab, extra, flags, penn, conf))
        for i in range(1, len(toks) + 1):
            g = rels[i - 1]
            p = roles.get(i, "<none>")
            if gpos[i - 1] in NOMINAL:                     # the organ's OWN held-out accuracy, apples-to-apples
                pops["ACC_NOMINAL"].append((si, i, int(ROLE_TO_DEP[coarse_of(g)] == p)))
            if gpos[i - 1] in WIDE_ADV:
                pops["ACC_WIDE"].append((si, i, int(ROLE_TO_DEP[coarse_of(g)] == p)))
            if g not in TARGET:
                continue
            ct = clause_type(i, gpos, gheads, rels)
            ok = int(p == g)
            pops["%s|%s" % (ct, g)].append((si, i, ok))
            pops["ALL|%s" % g].append((si, i, ok))
            pops["ALL|core"].append((si, i, ok))
            pops["NOMINALPOP" if gpos[i - 1] in NOMINAL else "NONEPOP"].append((si, i, ok))
            if g in ("nsubj", "nsubj:pass"):
                pops["ALL|subjects"].append((si, i, ok))
    return pops


def confusions(rows, tab, extra, flags, arm, penn_on):
    conf = defaultdict(Counter)
    for r in rows:
        toks, gpos, gheads, rels = r["toks"], r["gpos"], r["gheads"], r["rels"]
        if arm == "gold":
            pos = list(gpos)
            heads = {i: gheads[i - 1] for i in range(1, len(toks) + 1)}
            penn = r["penn_g"] if penn_on else None
        else:
            pos, heads = r["ppos"], r["pheads"]
            penn = r["penn_p"] if penn_on else None
        roles = label_all(toks, pos, heads, tab, extra, flags, penn, None if arm == "gold" else r["conf"])
        for i in range(1, len(toks) + 1):
            g = rels[i - 1]
            if g not in TARGET:
                continue
            p = roles.get(i, "<none>")
            if p != g:
                conf["%s|%s" % (clause_type(i, gpos, gheads, rels), g)][p] += 1
    return {k: dict(v.most_common(5)) for k, v in conf.items()}


def boot_paired(a, b, n=4000, seed=7):
    """Paired bootstrap over ITEMS of the difference b-a."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if len(a) == 0:
        return 0.0, 0.0, 0.0
    rng = np.random.default_rng(seed)
    ni = len(a)
    d = np.empty(n)
    for k in range(n):
        idx = rng.integers(0, ni, ni)
        d[k] = b[idx].mean() - a[idx].mean()
    lo, hi = np.percentile(d, [2.5, 97.5])
    return float(b.mean() - a.mean()), float(lo), float(hi)


def align(pf, pn):
    """Align two populations on the SAME items (the paired population)."""
    fk = {(s, t): o for s, t, o in pf}
    nk = {(s, t): o for s, t, o in pn}
    keys = sorted(set(fk) & set(nk))
    return [fk[k] for k in keys], [nk[k] for k in keys]


def compare(pf, pn, name):
    a, b = align(pf.get(name, []), pn.get(name, []))
    if not a:
        return None
    d, lo, hi = boot_paired(a, b)
    return {"n": len(a), "floor": round(float(np.mean(a)), 4), "new": round(float(np.mean(b)), 4),
            "delta": round(d, 4), "ci": [round(lo, 4), round(hi, 4)], "ci_sep": bool(lo > 0 or hi < 0)}


REPORT_POPS = ["matrix|nsubj", "embedded|nsubj", "copular|nsubj", "matrix|nsubj:pass", "embedded|nsubj:pass",
               "matrix|obj", "embedded|obj", "ALL|nsubj", "ALL|obj", "ALL|subjects", "ALL|core",
               "NOMINALPOP", "NONEPOP", "ACC_NOMINAL", "ACC_WIDE"]


def summarize(pops):
    return {k: {"n": len(v), "recall": round(float(np.mean([x[2] for x in v])), 4)}
            for k, v in sorted(pops.items()) if v}


# ================================================================================================ the agent probe
def agent_probe(out_dir, tab_new, extra, flags, penn_on, cap=None, label=""):
    """The board's who_did_what_agent dimension scored on the LIVE CHAIN (strategy 2026-09-13). Arms: the positional
    floor; the chain with the naive first-nsubj pick; the chain with the SUBJECT-SLOT COMPETITION (the highest SUBJ
    activation among the verb's nsubj-labelled dependents -- the brain reads one subject slot, filled by the strongest
    competitor); each with a positional fallback when the chain abstains."""
    import experiments.exp_board_agent_slot_ud_v1 as AG
    import hdlab.attachment_arm as AA
    import hdlab.lexical_categories as LC
    sents = AG.load_ud(AG.UD_TEST)
    if cap:
        sents = sents[:cap]
    items = AG.gold_agent_items(sents)
    lc = LC.get()
    pn = _penn_tagger() if penn_on else None
    atab = AA.load_attachment_validities()
    cache = {}
    n = 0
    ok = Counter()
    dec = Counter()
    conf = Counter()
    per_item = defaultdict(list)
    for it, (toks, v, gold, passive) in enumerate(items):
        key = tuple(toks)
        if key not in cache:
            pos = lc.tag(list(toks))
            heads = AA.heads(toks, pos, atab)
            penn = pn.tag(list(toks)) if pn is not None else None
            A = activations(toks, pos, heads, tab_new, extra, flags, penn)
            roles = {i: ROLE_TO_DEP[ROLE_CLASSES[int(np.argmax(a))]] for i, a in A.items()}
            cache[key] = (pos, heads, roles, A)
        pos, heads, roles, A = cache[key]
        n += 1
        want = "obl:agent" if passive else "nsubj"
        cands = [i for i in range(1, len(toks) + 1) if heads.get(i, -1) == v and roles.get(i) == want]
        floor_c = AG._clause_local_nominals(toks, pos, v)
        fl = AG.floor_positional_agent(toks, pos, v, floor_c) if floor_c else None
        fl_ok = int(fl is not None and AG._match(fl, toks[gold - 1]))
        ok["floor"] += fl_ok
        per_item["floor"].append((it, 0, fl_ok))
        if cands:
            dec["chain"] += 1
            naive = cands[0] if not passive else cands[-1]
            slot = RIX["BY_AGENT"] if passive else RIX["SUBJ"]
            comp = max(cands, key=lambda i: float(A[i][slot]))
            ok["naive_decided"] += int(naive == gold)
            ok["comp_decided"] += int(comp == gold)
            ok["naive_fb"] += int(naive == gold)
            ok["comp_fb"] += int(comp == gold)
            per_item["naive_fb"].append((it, 0, int(naive == gold)))
            per_item["comp_fb"].append((it, 0, int(comp == gold)))
            if comp != gold:
                conf[("wrong", "passive" if passive else "active", roles.get(gold, "<none>"),
                      "head_ok" if heads.get(gold, -1) == v else "head_wrong")] += 1
        else:
            conf[("abstain", "passive" if passive else "active", roles.get(gold, "<none>"),
                  "head_ok" if heads.get(gold, -1) == v else "head_wrong")] += 1
            ok["naive_fb"] += fl_ok
            ok["comp_fb"] += fl_ok
            per_item["naive_fb"].append((it, 0, fl_ok))
            per_item["comp_fb"].append((it, 0, fl_ok))
    a = [x[2] for x in per_item["floor"]]
    out = {"label": label, "n": n, "floor_positional": round(ok["floor"] / n, 4),
           "chain_decision_rate": round(dec["chain"] / n, 4),
           "chain_precision_naive": round(ok["naive_decided"] / max(1, dec["chain"]), 4),
           "chain_precision_competition": round(ok["comp_decided"] / max(1, dec["chain"]), 4),
           "chain_naive_plus_fallback": round(ok["naive_fb"] / n, 4),
           "chain_competition_plus_fallback": round(ok["comp_fb"] / n, 4),
           "vs_floor_naive": boot_paired(a, [x[2] for x in per_item["naive_fb"]]),
           "vs_floor_competition": boot_paired(a, [x[2] for x in per_item["comp_fb"]]),
           "misses": {"|".join(map(str, k)): c for k, c in conf.most_common(14)}}
    print(json.dumps({k: v for k, v in out.items() if k != "misses"}, default=str), flush=True)
    for k, c in out["misses"].items():
        print("   ", k, c)
    return out


# ================================================================================================ self-test
BASE_DIR = os.path.join(REPO, "data", "exp_role_competition_voice_embedding_arguments_v1")
# WITNESS on REAL UD-EWT test trees (gold heads; the labeler's own rung). Each row: a sentence prefix, the surface form
# of the argument, the gold dep, and the mechanism it witnesses. Every row is a case the SHIPPED organ gets wrong.
SELFTEST = [
    ("One of the pictures shows a flag", "One", "nsubj", "numeral partitive head IS an argument (was <none>)"),
    ("One of the pictures shows a flag", "that", "nsubj:pass", "relative passive subject stays right"),
    ("BREYER filed a concurring opinion , in which KENNEDY", "KENNEDY", "nsubj",
     "the preposition governs the relativizer, not the following nominal (was obl)"),
    ("SCALIA filed a dissenting opinion , in which THOMAS", "THOMAS", "nsubj", "same, coordinated conjunct (was obl)"),
    ("What if Google Morphed", "Google", "nsubj", "embedded subject under a fronted conditional (was dep)"),
    ("Most troubling , however , is the fact", "troubling", "nsubj",
     "nominalised adjective head IS an argument (was <none>)"),
    ("I doubt the very few who actually read my blog", "few", "nsubj", "quantifier head IS an argument (was <none>)"),
    ("The African Union is clearly not up to the task", "15,000", "obj", "numeral object head (was <none>)"),
    ("The media routinely obscures the lines", "lines", "obj", "canonical SVO object -- no regress"),
    ("U.S. Muslim groups criticized President Bush on Thursday", "Bush", "obj",
     "an NP-internal compound is not a second argument slot (was dep)"),
    ("And international donors have given only half of the relief aid that Darfur needs", "Darfur", "nsubj",
     "active filler: the NEAREST pre-verbal argument is the subject"),
    ("But there is no proof", "proof", "nsubj", "existential construction: the notional subject follows (was obj)"),
]


def self_test(tab, extra, flags, penn_on):
    te = load_cache(BASE_DIR, "test")
    idx = {}
    for r in te:
        idx.setdefault(" ".join(r["toks"]), r)
    npass = total = 0
    for prefix, form, want, why in SELFTEST:
        row = next((r for k, r in idx.items() if k.startswith(prefix)), None)
        if row is None:
            print("  SKIP  (sentence not in the test cache) %s" % prefix[:50]); continue
        toks, gpos, gheads, rels = row["toks"], row["gpos"], row["gheads"], row["rels"]
        cand = [i for i in range(1, len(toks) + 1) if toks[i - 1] == form and rels[i - 1] == want]
        if not cand:
            print("  SKIP  (token/gold not found) %s / %s" % (prefix[:40], form)); continue
        i = cand[0]
        heads = {j: gheads[j - 1] for j in range(1, len(toks) + 1)}
        got = label_all(toks, list(gpos), heads, tab, extra, flags, None).get(i, "<none>")
        total += 1; npass += int(got == want)
        print("  %s  %-12s -> %-11s (want %-11s)  %s" % ("PASS" if got == want else "FAIL", form, got, want, why))
    print("WITNESS %d/%d" % (npass, total))
    return npass, total


# ================================================================================================ main
def main():
    argv = sys.argv[1:]
    out_dir = str(get_output_dir("role_competition_voice_embedding_arguments_v1"))
    os.makedirs(out_dir, exist_ok=True)
    penn_on = "--penn" in argv
    extra = EXTRA_ADV if "--wide-adv" in argv else EXTRA
    NONE_EXTRA = frozenset()
    if "--cache" in argv:
        build_cache(out_dir)
        return
    if "--self-test" in argv:
        tab = load_v3_table()                       # the SHIPPED candidate asset (counts -> strengths), not a rebuild
        n, t = self_test(tab, extra, FLAGS_ON, penn_on)
        print("DONE" if n == t else "DONE (witness incomplete)")
        return
    tr = load_cache(out_dir, "train")
    te = load_cache(out_dir, "test")
    frames = lemma_frames_from(tr)
    slotcap = slot_capacity_from(tr)
    if "--agent" in argv:
        counts = accrue(tr, extra, FLAGS_ON, penn_on, frames, min_conf=ACCRUE_MIN_CONF)
        tab = table_from_counts(counts, frames, slotcap)
        res = {"v3": agent_probe(out_dir, tab, extra, FLAGS_ON, penn_on, label="v3")}
        cf = accrue(tr, NONE_EXTRA, FLAGS_OFF, False, frames)
        tf = table_from_counts(cf, frames, slotcap)
        res["floor"] = agent_probe(out_dir, tf, NONE_EXTRA, FLAGS_OFF, False, label="floor(v2 repro)")
        json.dump(res, open(os.path.join(out_dir, "agent_metrics.json"), "w", encoding="utf-8"), indent=1, default=str)
        print("DONE")
        return
    if "--board-patient" in argv:
        # NO-REGRESS on the board's who_did_what PATIENT dimension, measured by an IN-PROCESS A/B (no hdlab file is
        # edited): the same board entry point is run twice, once with the shipped `coarse_roles` and once with
        # `coarse_roles_v3` bound in its place.
        import experiments.exp_board_patient_slot_v1 as BP
        out = {}
        counts = accrue(tr, extra, FLAGS_ON, penn_on, frames, min_conf=ACCRUE_MIN_CONF)
        counts["slot_capacity"] = slotcap
        v3tab = table_from_counts(counts, frames, slotcap)
        orig = GRA.coarse_roles
        cap = None
        for arm in ("floor", "v3"):
            if arm == "v3":
                GRA.coarse_roles = (lambda toks, pos, heads, validities=None, head_posterior=None:
                                    coarse_roles_v3(toks, pos, heads, v3tab, head_posterior, extra, FLAGS_ON))
            else:
                GRA.coarse_roles = orig
            t0 = time.time()
            row, _detail = BP.board_patient_dimension(cap=cap)
            out[arm] = {k: row.get(k) for k in ("n", "model_acc", "strongest_floor", "twin_acc",
                                                "model_minus_strongest", "model_minus_twin",
                                                "ci_sep_over_strongest", "ci_sep_over_twin")}
            print("[board patient] %-5s %s  (%.0fs)" % (arm, json.dumps(out[arm], default=str), time.time() - t0),
                  flush=True)
        GRA.coarse_roles = orig
        json.dump(out, open(os.path.join(out_dir, "board_patient.json"), "w", encoding="utf-8"), indent=1, default=str)
        print("DONE")
        return
    if "--emit" in argv:
        counts = accrue(tr, extra, FLAGS_ON, penn_on, frames, min_conf=ACCRUE_MIN_CONF)
        counts["slot_capacity"] = slotcap
        b = GRA.strengths_from_counts(counts)
        doc = {"source": "pri103 v3 cue set (auxiliary-frame voice, argument rank, expletive slot, lexical case, "
                         "generalized copula, widened argument class + selfcat); Competition-Model strengths = "
                         "graded_role_assigner.strengths_from_counts(counts); UD-EWT train, PERCEIVED heads, "
                         "confidence-weighted accrual.",
               "roles": ROLE_CLASSES, "decisions": counts["decisions"], "perceived": True, "confidence_weighted": True,
               "argset": sorted(NOMINAL | extra), "penn": penn_on, "cue_set": "v3",
               "prior": [float(x) for x in b["prior"]],
               "strength": {c: {v: [round(float(x), 4) for x in vec] for v, vec in vals.items()}
                            for c, vals in b["strength"].items()},
               "lemma_frames": frames, "counts": counts, "slot_capacity": slotcap}
        p = os.path.join(REPO, "data", "hook_state", "coarse_role_validities_pri103_v3.json")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, indent=1)
        print("wrote", p)
        print("DONE")
        return

    # ---------------- the measured run
    t0 = time.time()
    res = {"n_train": len(tr), "n_test": len(te), "penn": penn_on, "argset": sorted(NOMINAL | extra)}
    print("[floor] building the v2-repro table (shipped cue set, NOMINAL argset, weighted perceived accrual)", flush=True)
    cf = accrue(tr, NONE_EXTRA, FLAGS_OFF, False, frames)
    tab_f = table_from_counts(cf, frames, slotcap)
    print("[new] building the v3 table", flush=True)
    cn = accrue(tr, extra, FLAGS_ON, penn_on, frames, min_conf=ACCRUE_MIN_CONF)
    tab_n = table_from_counts(cn, frames, slotcap)
    tab_tw = twin_table(tab_n)
    res["decisions"] = {"floor": round(cf["decisions"], 1), "v3": round(cn["decisions"], 1)}

    # the SHIPPED organ, byte-for-byte, as the external floor reference
    shipped = {}
    for name, path in (("live_table", None),
                       ("weighted_table", os.path.join(REPO, "data", "frontend_assets",
                                                       "coarse_role_validities_ud_ewt_perceived_w.json"))):
        st = GRA.load_coarse_validities(path)
        for arm in ("gold", "live"):
            pops = defaultdict(list)
            for si, r in enumerate(te):
                toks, gpos, gheads, rels = r["toks"], r["gpos"], r["gheads"], r["rels"]
                if arm == "gold":
                    pos = list(gpos)
                    heads = {i: gheads[i - 1] for i in range(1, len(toks) + 1)}
                else:
                    pos, heads = r["ppos"], r["pheads"]
                roles = GRA.coarse_roles(toks, pos, heads, st)
                for i in range(1, len(toks) + 1):
                    g = rels[i - 1]
                    p = roles.get(i, "<none>")
                    if gpos[i - 1] in NOMINAL:
                        pops["ACC_NOMINAL"].append((si, i, int(ROLE_TO_DEP[coarse_of(g)] == p)))
                    if g not in TARGET:
                        continue
                    ct = clause_type(i, gpos, gheads, rels)
                    ok = int(p == g)
                    pops["%s|%s" % (ct, g)].append((si, i, ok))
                    pops["ALL|%s" % g].append((si, i, ok))
                    pops["ALL|core"].append((si, i, ok))
                    pops["NOMINALPOP" if gpos[i - 1] in NOMINAL else "NONEPOP"].append((si, i, ok))
                    if g in ("nsubj", "nsubj:pass"):
                        pops["ALL|subjects"].append((si, i, ok))
            shipped["%s|%s" % (name, arm)] = summarize(pops)
    res["shipped_organ"] = shipped

    for arm in ("gold", "live"):
        pf = evaluate(te, tab_f, NONE_EXTRA, FLAGS_OFF, arm, False)
        pn = evaluate(te, tab_n, extra, FLAGS_ON, arm, penn_on)
        pt = evaluate(te, tab_tw, extra, FLAGS_ON, arm, penn_on)
        res["%s|floor" % arm] = summarize(pf)
        res["%s|v3" % arm] = summarize(pn)
        res["%s|twin" % arm] = summarize(pt)
        res["%s|vs_floor" % arm] = {k: compare(pf, pn, k) for k in REPORT_POPS if compare(pf, pn, k)}
        res["%s|vs_twin" % arm] = {k: compare(pt, pn, k) for k in REPORT_POPS if compare(pt, pn, k)}
        res["%s|confusions_v3" % arm] = confusions(te, tab_n, extra, FLAGS_ON, arm, penn_on)
        res["%s|confusions_floor" % arm] = confusions(te, tab_f, NONE_EXTRA, FLAGS_OFF, arm, False)
        print("== %s arm ==" % arm, flush=True)
        for k in REPORT_POPS:
            c = res["%s|vs_floor" % arm].get(k)
            if c:
                print("   %-22s n=%4d floor %.4f -> v3 %.4f  d=%+.4f CI[%+.4f,%+.4f]%s"
                      % (k, c["n"], c["floor"], c["new"], c["delta"], c["ci"][0], c["ci"][1],
                         "  CI-SEP" if c["ci_sep"] else ""), flush=True)

    if "--ablate" in argv:
        abl = {}
        pf_g = evaluate(te, tab_f, NONE_EXTRA, FLAGS_OFF, "gold", False)
        pf_l = evaluate(te, tab_f, NONE_EXTRA, FLAGS_OFF, "live", False)
        arms = []
        for f in ALL_FLAGS:                                   # each cue change ALONE, on the shipped argument class
            if f == "selfcat":
                continue
            fl = dict(FLAGS_OFF); fl[f] = True
            if f == "prep_lex":
                fl["prep"] = True
            arms.append(("ONE:" + f, NONE_EXTRA, fl, penn_on and f == "voice"))
        cum = dict(FLAGS_OFF)                                 # CUMULATIVE build order (top-down by loss addressed)
        for step in ("rank", "prep", "exconfig+expl", "headcls+cop", "rank_gate", "wide",
                     "wide+selfcat", "wide+selfcat_full", "wide+voice"):
            for f in step.split("+"):
                cum[f] = True
            aset = extra if "wide" in step else NONE_EXTRA
            arms.append(("CUM:" + step, aset, dict(cum), penn_on))
        for name, aset, fl, pon in arms:
            c = accrue(tr, aset, fl, pon, frames, min_conf=ACCRUE_MIN_CONF if fl.get("rank_gate") else 0.0)
            t = table_from_counts(c, frames, slotcap)
            row = {}
            for arm, pf in (("gold", pf_g), ("live", pf_l)):
                p = evaluate(te, t, aset, fl, arm, pon)
                row[arm] = {k: compare(pf, p, k) for k in
                            ("ALL|nsubj", "ALL|obj", "ALL|core", "ACC_NOMINAL", "NONEPOP", "matrix|nsubj",
                             "embedded|nsubj", "copular|nsubj")}
            abl[name] = row
            print("[ablate] %-13s gold %s" % (name, json.dumps(
                {k: (v["delta"], "S" if v["ci_sep"] else "") for k, v in row["gold"].items() if v})), flush=True)
        res["ablation"] = abl

    res["runtime_s"] = round(time.time() - t0, 1)
    json.dump(res, open(os.path.join(out_dir, "metrics.json"), "w", encoding="utf-8"), indent=1, default=str)
    print("wrote", os.path.join(out_dir, "metrics.json"))
    print("DONE")


if __name__ == "__main__":
    main()
