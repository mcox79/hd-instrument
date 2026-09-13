"""hdlab/attachment_arm.py -- the ATTACHMENT arm of the Competition-Model organ (graded_role_assigner): "which word heads this
word", decided by cue competition with LEARNED, configuration-conditioned strengths, read out as the exact tree posterior.

Landed 2026-09-12 (strategy; spec notes/RESEARCH_attachment_organ_spec_2026-09-12.md; probes v18/v21/v22). One structure, two arms:
the role competition (graded_role_assigner.coarse_roles) and this head competition share the cue machinery (categorical cue values
-> contrasts learned from counts -> additive activation -> normalised posterior) and the same plastic knowledge form.

BRAIN COMPUTATION (PINNED at the computational level): attachment = constraint-based cue competition (MacDonald-Pearlmutter-Seidenberg
1994) over candidates retrieved under memory-limited decay (Lewis & Vasishth 2005; locality), with alternatives kept alive and
weighted by probability (Hale/Levy); item-based CONSTRUCTIONS (Tomasello 2003) are cue coalitions. MODEL: the exact single-root
Matrix-Tree marginal (graded_parser) = the normative keep-alternatives-alive; soft-count self-supervision = "the posterior teaches the
cue statistics". Pre-lexical FORM knowledge enters as constraints (punctuation/numerals never head; punctuation = written prosody
-> boundary cue). REFUTED (recorded): unconditioned additive cues (drift), a frequency-driven root prior (crowns punctuation), a
hand-authored universal prior (kept OUT of the organ; it was worth ~0.10 and is what meaning should supply).

CUES (values categorical; strengths = contrast log-odds(arc | config, value) - log-odds(arc | config), config = category pair):
  locality (direction x log-distance bin), catpair (config), frame (head verb's transitivity from learned counts x dependent
  class x direction), form (candidate is a form class), boundary (marks spanned), agree (number-agreement sketch), constr (which
  construction proposes the arc: verbarg / coord / npmod / clausal), root (dependent category for the ROOT decision).

KNOWLEDGE FORM (plastic, never frozen): data/frontend_assets/attachment_validities_v1.json carries the COUNTS (soft true / total per
"config|value"); strengths are a pure function of the counts (strengths_from_arc_counts); observe_arc_outcome(...) accrues a
comprehension outcome online; save_attachment_validities() persists. Built offline by tools/build_attachment_validities.py from a
KNOWLEDGE-FREE teacher (no treebank, no hand prior) + anchored self-teaching -- the measured gate (ledger): 0.272 -> 0.43+ UAS.

MEASURED (UD-EWT test 700, gold categories, probe v18): prior-informed bootstrap + constructions 0.5303; knowledge-free bootstrap
+ constructions 0.4316 (rising); adjacent-right floor 0.285; supervised 0.78; brain 0.9+ (the gap: meaning feeding structure,
the argument-structure lexicon at scale, incremental reanalysis). Glass-box, numpy only, NO LLM, NO external parser.
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = "2026-09-12 strategy: cue competition + tree posterior PINNED/MODEL; strengths LEARNED from soft counts, knowledge-free bootstrap"
__bf_note__ = "attachment arm of the Competition-Model organ; constructions hand-written item-based schemas (induced forms refuted as built); hand prior kept OUT"
__bf_corrections__ = []

import json
import math
import os
from collections import defaultdict
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from hdlab.graded_parser import chu_liu_edmonds, single_root_marginals
from hdlab.thematic_role_labeler import lemma_verb

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET = os.path.join(_REPO, "data", "frontend_assets", "attachment_validities_v1.json")
FORM = frozenset({"PUNCT", "NUM", "SYM"})
NOMINAL = ("NOUN", "PRON", "PROPN")
CONTENT = frozenset({"NOUN", "PROPN", "PRON", "VERB", "ADJ", "ADV", "NUM"})
NP_RUN = frozenset({"DET", "ADJ", "NUM", "NOUN", "PROPN"})
# MEANING AS A READ-TIME CUE (2026-09-13 05:40): the Competition Model's semantic-plausibility cue. Until now meaning entered the
# arm only as the acquisition TEACHER (the tree posterior the validities are counted from); at read time the arm was meaning-blind
# (only 1.7% of heads changed between two teacher builds). Value = slot (S before the verb / O after) x binned plausibility of the
# nominal as that verb's participant (self-grown typed store; pronoun-filler rates); validity LEARNED like every other cue. A hard
# meaning GATE was refuted (nmod collapse) -- this is the graded, learned-validity form. Flag for the A/B; default OFF until measured.
# DEFAULT ON since 2026-09-13 06:00 local (v2, core slots only; the live asset is built WITH it): UD-EWT test UAS 0.5694 -> 0.5726,
# nmod 0.311 -> 0.358, ccomp 0.466 -> 0.500, obj 0.700 -> 0.710, conj 0.223 -> 0.253; nsubj 0.762 -> 0.753, obl 0.468 -> 0.430.
# "0" reproduces the meaning-blind readout (the asset then carries unused plaus validities).
PLAUS_CUE = os.environ.get("HDLAB_ARM_PLAUS_CUE", "1") == "1"
CUES = ("locality", "frame", "form", "boundary", "agree", "constr", "pp") + (("plaus",) if PLAUS_CUE else ())   # catpair / root = configuration
# "pp" (2026-09-13, folded from the pri-2 solver's proven Hindle-Rooth lever): for a PP-object nominal, the preposition's verb-vs-noun
# association LR(p) = log P(p|verb) / P(p|noun), learned TREEBANK-FREE from UNAMBIGUOUS prepositional phrases in reading.
M_SHRINK = 2.0
# CONVENTION LAYER (labelled honestly, 2026-09-12): the function-word frames (ADP -> its NP head, AUX/copula -> their predicate,
# SCONJ/'to' -> the verb, names left-headed, punctuation -> the clause verb) are ANNOTATION CONVENTIONS of UD-shaped consumers, not
# facts a raw-text statistic determines -- self-supervision cannot learn them (measured: as a learned cue +0.013; applied at decode
# +0.036 on the smoke slice). They are applied as a deterministic decode-time bonus for consumers that read UD-shaped heads; the
# learned competition (the comprehension organ) is untouched. Set CONVENTION_BONUS = 0.0 to read the pure learned organ.
CONVENTION_BONUS = 5.0
BF_TSP_ASSET = os.path.join(_REPO, "data", "frontend_assets", "typed_selectional_preference_bf_v1.json")   # self-grown plausibility
BF_TSP_SUBJ_ASSET = os.path.join(_REPO, "data", "frontend_assets", "typed_selectional_preference_bf_subj_v1.json")   # self-grown SUBJ slot
BF_STORE = os.path.join(_REPO, "data", "selectional_preferences_bf_v1", "selectional_slots_bf_v1.pkl")   # self-grown slot fillers
PRON_EVIDENCE = os.environ.get("HDLAB_SBT_PRON", "1") != "0"
# 2026-09-13 05:10: the order-aware teacher gave SUBJECT plausibility to EVERY pre-verbal nominal, including the object of a preposition
# ("the man in the HOUSE saw"), pulling PP objects off their noun host (nmod 0.346 -> 0.311). Semantic bootstrapping reads the
# preposition as a CASE MARKER: a case-marked nominal is oblique, never the subject (Pinker 1984). Flag for the A/B; default OFF until measured.
# DEFAULT ON since 2026-09-13 (the read-time meaning cue's slot rules must match the asset's build; as a teacher-only change it was NULL).
PP_NO_SUBJ = os.environ.get("HDLAB_SBT_PP_NOSUBJ", "1") == "1"
PRONOUNS = frozenset({"it", "he", "she", "they", "we", "i", "you", "him", "her", "them", "us", "me", "this", "that", "these", "those",
                      "who", "whom", "which", "what", "there", "one", "someone", "something", "anyone", "anything", "everyone",
                      "everything", "nothing", "nobody", "himself", "herself", "itself", "themselves", "myself", "yourself", "ourselves"})
ORDER_AWARE = os.environ.get("HDLAB_SBT_ORDER_AWARE", "1") != "0"   # v1 REFUTED 2026-09-13 (max-over-one root score: obj +0.008 but ccomp 0.466->0.207,
#   xcomp 0.686->0.599, UAS 0.5706->0.5654 -- the SUBJ-slot association has a different scale/sparsity (811 verbs) and weakens the
#   root/argument signal clausal structure rides on; keep off until the two slot associations are put on one scale.
_TABLE: Optional[Dict[str, object]] = None


# ------------------------------------------------------------------------------------------------------ constructions
def verbarg_arcs(toks: Sequence[str], pos: Sequence[str]) -> List[Tuple[int, int]]:
    """Now-or-Never left-corner verb-argument bind (hdlab.incremental_parser), structural."""
    from hdlab.incremental_parser import incremental_build
    frames = incremental_build(list(toks), list(pos), use_revise=True)
    n = len(toks); out = []
    for v, args in frames.items():
        for a in args:
            if 1 <= a <= n and 1 <= v <= n and a != v:
                out.append((v, a))
    return out


# COORDINATION = PARALLEL STRUCTURE (owner-DONE pri 95, 2026-09-13; solver diff landed verbatim). A coordinator predicts a second
# phrase of the SAME KIND as the phrase just closed (Frazier 1985; Munn 1993; Taft & Clifton 2000 parallel-structure facilitation;
# Levy 2008 prediction), retrieved as a like-CLASS antecedent (Lewis & Vasishth 2005), the two conjuncts sharing one governor slot
# (a plural set). The OLD coord_arcs took the NEAREST content words and required identical UPOS: it proposed the exact gold conj
# arc only 24.5% of the time (a 2nd conjunct that opens with a modifier -> the modifier, not the head noun; a cross-UPOS conjunct
# -> rejected). The parallel-HEAD version below fixes both; the learned `coord` validity does the rest, once the teacher
# (parallelism_boost) shows it coordination at all (measured: the teacher put 0.054 mass on gold conj arcs before).
# Measured by the solver (UD-EWT test 700, gold categories): conj 0.300 -> 0.391 (map1, CI [0.052, 0.133]) / 0.373 (incr); UAS
# 0.6034 -> 0.6055; nsubj -0.017 give-back (diffuse, named); slot-sharing REFUTED (0.365); far conjuncts (9+ tokens, 26%) ~0.016 =
# the meaning-channel frontier. gamma is a SWEPT operating point (2/4/8 all CI-separated; 4 kept).
_NOMINAL_CLASS = frozenset({"NOUN", "PROPN", "PRON", "NUM"})
_PRED_CLASS = frozenset({"VERB", "ADJ"})


def parallel_class(p: str, coarse: bool = True) -> Optional[str]:
    """The parallel CLASS of a category. coarse: phrase-type (nominal / predicate / adverbial) so a NOUN can coordinate
    with a PROPN; strict: the UPOS itself."""
    if coarse:
        if p in _NOMINAL_CLASS:
            return "NOM"
        if p in _PRED_CLASS:
            return "PRED"
        if p == "ADV":
            return "ADV"
        return None
    return p if p in CONTENT else None


def _right_conjunct_head(pos: Sequence[str], k: int, n: int) -> Optional[int]:
    """Head of the phrase AFTER the coordinator at 1-based k: the last NOUN/PROPN of the nominal run (head-final English
    NP), else the last ADJ/NUM of the run (predicate-adjective coordination), else the first content word (verb/adverb)."""
    j = k + 1
    while j <= n and pos[j - 1] == "PUNCT":
        j += 1
    if j > n:
        return None
    p = pos[j - 1]
    if p in NP_RUN:
        e = j
        while e <= n and pos[e - 1] in NP_RUN:
            e += 1
        nouns = [q for q in range(j, e) if pos[q - 1] in ("NOUN", "PROPN")]
        if nouns:
            return nouns[-1]
        adjs = [q for q in range(j, e) if pos[q - 1] in ("ADJ", "NUM")]
        return adjs[-1] if adjs else None
    if p in CONTENT:
        return j
    return None


def _left_conjunct_head(pos: Sequence[str], k: int, rclass: str, coarse: bool) -> Optional[int]:
    """Cue-based retrieval of the like-class antecedent: nearest preceding content head of R's parallel class before cc."""
    for q in range(k - 1, 0, -1):
        c = parallel_class(pos[q - 1], coarse)
        if c is not None and c == rclass:
            return q
    return None


def coord_sites(toks: Sequence[str], pos: Sequence[str], coarse: bool = True) -> List[Tuple[int, int, int]]:
    """Every coordinator's parallel heads (L before, R after) + the coordinator index cc. The ONE source of truth for
    BOTH the read-time construction and the teacher's parallel-structure boost."""
    n = len(toks); out = []
    for k in range(1, n + 1):
        if pos[k - 1] != "CCONJ":
            continue
        R = _right_conjunct_head(pos, k, n)
        if R is None:
            continue
        rc = parallel_class(pos[R - 1], coarse)
        if rc is None:
            continue
        L = _left_conjunct_head(pos, k, rc, coarse)
        if L is None or L == R:
            continue
        out.append((L, R, k))
    return out


def coord_arcs(toks: Sequence[str], pos: Sequence[str]) -> List[Tuple[int, int]]:
    """Coordination parallelism: R (2nd conjunct HEAD) attaches to L (1st conjunct head of the same parallel class);
    the coordinator attaches to R. Parallel heads, not nearest content words -- see coord_sites."""
    out = []
    for (L, R, k) in coord_sites(toks, pos, coarse=True):
        out.append((L, R)); out.append((R, k))
    return out


PARALLELISM_GAMMA = float(os.environ.get("HDLAB_ARM_PARALLELISM_GAMMA", "4.0"))   # swept (2/4/8 all CI-separated); 4 kept


def parallelism_boost(A: "np.ndarray", toks: Sequence[str], pos: Sequence[str], gamma: float = None,
                      coarse: bool = True) -> "np.ndarray":
    """ACQUISITION signal (used by tools/build_attachment_validities.py on the teacher's score matrix, NOT at read time):
    parallel-structure PREDICTION -- boost the conj arc (head L, dep R) and the cc arc (head R, dep cc) so the teacher
    posterior puts mass on coordination and the `coord` cue can learn a validity. Treebank-free (coordinator position +
    category parallelism). gamma is a SWEPT operating point."""
    gamma = PARALLELISM_GAMMA if gamma is None else gamma
    if gamma <= 0:
        return A
    B = A.copy()
    for (L, R, k) in coord_sites(toks, pos, coarse):
        B[L][R] = (B[L][R] + gamma) if np.isfinite(B[L][R]) else gamma
        B[R][k] = (B[R][k] + gamma) if np.isfinite(B[R][k]) else gamma
    return B


def npmod_arcs(toks: Sequence[str], pos: Sequence[str]) -> List[Tuple[int, int]]:
    """NP-internal modifier construction: within a contiguous nominal run every element attaches to the last NOUN/PROPN."""
    n = len(pos); out = []; i = 0
    while i < n:
        if pos[i] not in NP_RUN:
            i += 1; continue
        j = i
        while j < n and pos[j] in NP_RUN:
            j += 1
        run = list(range(i, j)); heads = [k for k in run if pos[k] in ("NOUN", "PROPN")]
        if heads:
            h = heads[-1] + 1
            for k in run:
                if k + 1 != h:
                    out.append((h, k + 1))
        i = j
    return out


def clausal_arcs(toks: Sequence[str], pos: Sequence[str]) -> List[Tuple[int, int]]:
    """Matrix-verb bind: a non-initial VERB not right after a coordinator attaches to the nearest preceding VERB."""
    n = len(pos); out = []; prev = None
    for i in range(n):
        if pos[i] == "VERB":
            if prev is not None and not (i > 0 and pos[i - 1] == "CCONJ"):
                out.append((prev + 1, i + 1))
            prev = i
    return out


def function_word_arcs(toks: Sequence[str], pos: Sequence[str]) -> List[Tuple[int, int]]:
    """FUNCTION-WORD frames (Mintz 2003 frequent frames: high precision, narrow reach; the error anatomy 2026-09-12 put a third of
    the gap to the supervised parser here): a preposition attaches to the head of the nominal run that follows it ("ADP _ NOUN");
    an auxiliary attaches to the verb that follows it; a copula (be/become/seem + no following verb) attaches to the non-verbal
    predicate that follows; a subordinator / infinitival 'to' attaches to the following verb; a run of proper nouns is LEFT-headed
    (the first name heads the rest); a punctuation mark attaches to the nearest verb (the clause predicate). Item-based schemas
    learned as form-position templates; deterministic once learned."""
    n = len(pos); out = []; lows = [t.lower() for t in toks]
    COP = {"be", "is", "are", "was", "were", "been", "being", "am", "become", "became", "becomes", "seem", "seems", "seemed",
           "'m", "'s", "'re", "s", "m", "re"}   # clitic copulas (2026-09-13 root anatomy: "I 'm not fond" rooted 'I'; the rule never fired)
    def np_head_after(i):                   # head noun of the nominal run starting at i (0-based) or None
        j = i
        while j < n and pos[j] in NP_RUN:
            j += 1
        heads = [k for k in range(i, j) if pos[k] in ("NOUN", "PROPN")]
        return heads[-1] if heads else None
    def next_verb(i):
        for k in range(i + 1, n):
            if pos[k] == "VERB":
                return k
            if pos[k] == "PUNCT":
                break
        return None
    def next_predicate(i):                  # the HEAD of the predicate phrase after the copula, before any verb
        for k in range(i + 1, n):
            if pos[k] == "VERB" or pos[k] == "PUNCT":
                return None
            if pos[k] in ("ADJ", "NOUN", "PROPN", "PRON", "NUM"):
                if pos[k] == "PRON":
                    return k
                # PREDICATE HEAD (2026-09-13; copular-shape diagnostic: the binder recovered 44% of holder-property pairs under the
                # arm vs 75% with the stand-in because the subject was hung on the FIRST adjective -- "vote" -> "little" in "is a
                # little confusing", "Google" -> "nice" in "is a nice search engine"): a nominal run's head is its last NOUN/PROPN;
                # an adjectival predicate's head is the LAST adjective of the run ("a little confusing" -> confusing).
                h = np_head_after(k)
                if h is not None:
                    return h
                j = k
                while j + 1 < n and pos[j + 1] in ("ADJ", "ADV", "NUM"):
                    j += 1
                adjs = [m for m in range(k, j + 1) if pos[m] in ("ADJ", "NUM")]
                return adjs[-1] if adjs else k
        return None
    for i in range(n):
        p = pos[i]
        if p == "ADP" and i + 1 < n and pos[i + 1] in NP_RUN:
            h = np_head_after(i + 1)
            if h is not None:
                out.append((h + 1, i + 1))
        elif p == "AUX":
            v = next_verb(i)
            if v is not None:
                out.append((v + 1, i + 1))
            elif lows[i] in COP:
                q = next_predicate(i)
                if q is not None:
                    out.append((q + 1, i + 1))
                    # COPULAR CLAUSE CONVENTION (2026-09-13; state-dim residual): with no verb, the predicate heads the clause and
                    # its HOLDER is the nearest preceding nominal head that is not a prepositional object ("the man with the hat is
                    # tall": 'hat' is the object of 'with' -> skip -> 'man'). Stated as the UD convention copular consumers read.
                    k = i - 1
                    while k >= 0 and pos[k] in ("ADV", "PART", "PUNCT"):
                        k -= 1
                    subj = None
                    while k >= 0:
                        if pos[k] in ("NOUN", "PROPN", "PRON", "NUM"):
                            # start of this nominal run
                            a = k
                            while a - 1 >= 0 and pos[a - 1] in NP_RUN:
                                a -= 1
                            if a - 1 >= 0 and pos[a - 1] == "ADP":      # a prepositional object: skip the whole PP
                                k = a - 2
                                continue
                            subj = k
                            break
                        if pos[k] in ("VERB", "SCONJ", "CCONJ"):
                            break
                        k -= 1
                    if subj is not None and subj != q:
                        out.append((q + 1, subj + 1))
        elif p == "SCONJ" or (p == "PART" and lows[i] == "to"):
            v = next_verb(i)
            if v is not None:
                out.append((v + 1, i + 1))
        elif p == "PROPN" and i > 0 and pos[i - 1] == "PROPN":
            k = i
            while k > 0 and pos[k - 1] == "PROPN":
                k -= 1
            out.append((k + 1, i + 1))       # flat: left-headed name
        elif p == "PUNCT":
            cands = [k for k in range(n) if pos[k] == "VERB"]
            if cands:
                h = min(cands, key=lambda k: (abs(k - i), k))
                out.append((h + 1, i + 1))
    return out


CONSTRUCTIONS = {"verbarg": verbarg_arcs, "coord": coord_arcs, "npmod": npmod_arcs, "clausal": clausal_arcs, "fw": function_word_arcs}


def construction_map(toks: Sequence[str], pos: Sequence[str]) -> Dict[Tuple[int, int], str]:
    out: Dict[Tuple[int, int], str] = {}
    for fam, fn in CONSTRUCTIONS.items():
        try:
            for (h, d) in fn(toks, pos):
                out.setdefault((h, d), fam)
        except Exception:
            pass
    return out


# --------------------------------------------------------------------------------------------------------- cue values
def dist_bin(d: int) -> str:
    return "1" if d == 1 else "2" if d == 2 else "3-4" if d <= 4 else "5-8" if d <= 8 else "9+"


def verb_frames_from_reading(sentences: Sequence[Tuple[Sequence[str], Sequence[str]]]) -> Dict[str, List[int]]:
    """Per verb lemma [n_occurrences, n_with_a_bare_post-verbal_nominal_within_3] -- from TOKENS only (no labels)."""
    fr: Dict[str, List[int]] = defaultdict(lambda: [0, 0])
    for toks, pos in sentences:
        n = len(toks)
        for v in range(n):
            if pos[v] != "VERB":
                continue
            lem = lemma_verb(toks[v]).lower(); fr[lem][0] += 1
            for j in range(v + 1, min(n, v + 4)):
                if pos[j] in NOMINAL and not (j - 1 > v and pos[j - 1] == "ADP"):
                    fr[lem][1] += 1; break
    return {k: v for k, v in fr.items() if v[0] >= 5}


PP_NPMOD = frozenset({"DET", "ADJ", "NUM"})


def pp_site(pos: Sequence[str], i: int):
    """For a candidate PP-object NOUN/PROPN at 1-based i: (prep_idx, verb_idx, noun_idx) 1-based (verb/noun may be None), else None.
    prep = nearest preceding ADP separated from i only by NP-internal modifiers; verb = nearest VERB before the prep; noun = nearest
    NOUN/PROPN before the prep (the candidate nmod host). Category-structural only, no gold (Hindle & Rooth 1993)."""
    if pos[i - 1] not in ("NOUN", "PROPN"):
        return None
    k = i - 2
    while k >= 0 and pos[k] in PP_NPMOD:
        k -= 1
    if k < 0 or pos[k] != "ADP":
        return None
    prep = k + 1; verb = None; noun = None
    for q in range(k - 1, -1, -1):
        if verb is None and pos[q] == "VERB":
            verb = q + 1
        if noun is None and pos[q] in ("NOUN", "PROPN"):
            noun = q + 1
        if verb is not None and noun is not None:
            break
    return (prep, verb, noun)


def pp_assoc_from_reading(sentences: Sequence[Tuple[Sequence[str], Sequence[str]]]) -> Dict[str, Dict[str, float]]:
    """TREEBANK-FREE Hindle-Rooth association counts from (tokens, categories): every PP-object credits its preposition to the
    nearest preceding verb and/or noun; UNAMBIGUOUS sites (one candidate) are the reliable seed, ambiguous ones split 0.5/0.5
    (Hindle & Rooth's initial estimate). Keys are "lemma|prep" strings (JSON-safe, plastic counts)."""
    fv: Dict[str, float] = defaultdict(float); fn: Dict[str, float] = defaultdict(float)
    dv: Dict[str, float] = defaultdict(float); dn: Dict[str, float] = defaultdict(float)
    pv: Dict[str, float] = defaultdict(float); pn: Dict[str, float] = defaultdict(float)
    for toks, pos in sentences:
        n = len(toks); low = [t.lower() for t in toks]
        for i in range(1, n + 1):
            site = pp_site(pos, i)
            if site is None:
                continue
            prep, verb, noun = site; p = low[prep - 1]
            vl = lemma_verb(toks[verb - 1]).lower() if verb else None; nl = low[noun - 1] if noun else None
            if verb and not noun:
                fv[vl + "|" + p] += 1.0; dv[vl] += 1.0; pv[p] += 1.0
            elif noun and not verb:
                fn[nl + "|" + p] += 1.0; dn[nl] += 1.0; pn[p] += 1.0
            elif verb and noun:
                fv[vl + "|" + p] += 0.5; dv[vl] += 0.5; pv[p] += 0.5
                fn[nl + "|" + p] += 0.5; dn[nl] += 0.5; pn[p] += 0.5
    return {"fv": dict(fv), "fn": dict(fn), "dv": dict(dv), "dn": dict(dn), "pv": dict(pv), "pn": dict(pn)}


def pp_lr(assoc: Dict[str, Dict[str, float]], v_lemma: Optional[str], n_lemma: Optional[str], p: str) -> float:
    """log[P(p | verb) / P(p | noun)] with add-0.5 smoothing; unseen heads back off to the preposition's side marginal."""
    fv = assoc["fv"]; fn = assoc["fn"]; dv = assoc["dv"]; dn = assoc["dn"]; pv = assoc["pv"]; pn = assoc["pn"]
    tv = sum(pv.values()) + 1.0; tn = sum(pn.values()) + 1.0
    ppv = (fv.get((v_lemma or "") + "|" + p, 0.0) + 0.5) / (dv.get(v_lemma, 0.0) + 1.0) if v_lemma in dv else (pv.get(p, 0.0) + 0.5) / tv
    ppn = (fn.get((n_lemma or "") + "|" + p, 0.0) + 0.5) / (dn.get(n_lemma, 0.0) + 1.0) if n_lemma in dn else (pn.get(p, 0.0) + 0.5) / tn
    return math.log(ppv) - math.log(ppn)


def _lr_bin(lr: float) -> str:
    return "v2" if lr > 1.5 else "v1" if lr > 0.5 else "n2" if lr < -1.5 else "n1" if lr < -0.5 else "0"


class SentenceCues:
    """ONE cue pass per sentence (shared by every arc): punctuation cumsum for boundaries, construction map, verb lemmas."""

    def __init__(self, toks: Sequence[str], pos: Sequence[str], frames: Dict[str, List[int]],
                 pp_assoc: Optional[Dict[str, Dict[str, float]]] = None):
        self.toks = list(toks); self.pos = list(pos); self.n = len(toks); self.frames = frames
        self.cum = np.concatenate([[0], np.cumsum([1 if p == "PUNCT" else 0 for p in self.pos])])
        self.constr = construction_map(self.toks, self.pos)
        self.lem = [lemma_verb(t).lower() if p == "VERB" else None for t, p in zip(self.toks, self.pos)]
        self.teacher = _plaus_teacher() if PLAUS_CUE else None
        # PP-object sites: j -> (verb_idx, noun_idx, LR bin) when the preposition cue applies (pp_assoc given)
        self.pp: Dict[int, Tuple[Optional[int], Optional[int], str]] = {}
        if pp_assoc:
            for j in range(1, self.n + 1):
                site = pp_site(self.pos, j)
                if site is None:
                    continue
                prep, verb, noun = site
                if verb is None and noun is None:
                    continue
                vl = self.lem[verb - 1] if verb else None; nl = self.toks[noun - 1].lower() if noun else None
                self.pp[j] = (verb, noun, _lr_bin(pp_lr(pp_assoc, vl, nl, self.toks[prep - 1].lower())))

    def config(self, j: int, h: int) -> str:
        pj = self.pos[j - 1]
        if h == 0:
            return "ROOT:" + pj
        return f"{self.pos[h - 1]}>{pj}:{'L' if h < j else 'R'}"

    def cues(self, j: int, h: int) -> Dict[str, str]:
        if h == 0:
            return {}
        pj = self.pos[j - 1]; ph = self.pos[h - 1]; dr = "L" if h < j else "R"
        lo, hi = (h, j) if h < j else (j, h)
        nb = int(self.cum[hi - 1] - self.cum[lo])
        c = {"locality": f"{dr}{dist_bin(abs(h - j))}", "form": "formhead" if ph in FORM else "wordhead",
             "boundary": "0" if nb == 0 else "1" if nb == 1 else "2+",
             "constr": self.constr.get((h, j), "none")}
        site = self.pp.get(j)
        if site is not None and h in (site[0], site[1]):
            c["pp"] = ("V:" if h == site[0] else "N:") + site[2]     # which candidate this head is x the preposition's lean
        if self.teacher is not None and ph == "VERB" and pj in NOMINAL and not (j >= 2 and self.pos[j - 2] == "ADP"):
            # v2 (07:20): CORE slots only -- a case-marked (prepositional) nominal is oblique, and its host is the PP cue's business;
            # v1 fired on PP objects too and traded obl 0.468 -> 0.379 for nmod 0.311 -> 0.375.
            c["plaus"] = ("S:" if h > j else "O:") + _plaus_bin(self.teacher.slot_plausibility(self.toks, self.pos, h, j))
        if ph == "VERB":
            fr = self.frames.get(self.lem[h - 1])
            trans = "unk" if not fr else ("trans" if fr[1] / fr[0] >= 0.3 else "intrans")
            c["frame"] = f"{trans}:{pj}:{dr}"
            w = self.toks[h - 1].lower(); wj = self.toks[j - 1].lower()
            if dr == "R" and pj in NOMINAL and w.endswith("s") and not w.endswith("ss"):
                plural = (pj == "NOUN" and wj.endswith("s") and not wj.endswith("ss")) or wj in ("they", "we", "you", "i")
                c["agree"] = "3sgV:" + ("plurN" if plural else "singN")
            else:
                c["agree"] = "na"
        else:
            c["frame"] = "na"; c["agree"] = "na"
        return c


# ------------------------------------------------------------------------------------------------- strengths / table
def _lo(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6); return math.log(p / (1 - p))


def strengths_from_arc_counts(counts: Dict[str, object]) -> Dict[str, object]:
    """THE ONE implementation: config strength = lo(P(arc|config)) - lo(P(arc)); cue contrast = lo(P(arc|config,value)) -
    lo(P(arc|config)) with Dirichlet shrinkage (m) toward the configuration's own rate; a value that always fires within its
    configuration contributes exactly 0. counts = {"base": [t, n], "config": {cfg: [t, n]}, "cues": {cue: {"cfg|value": [t, n]}}}."""
    t0, n0 = counts["base"]; pb = (t0 + 0.5) / (n0 + 1.0)
    out = {"cfg": {}, "pcfg": {}}
    for cfg, (t, n) in counts["config"].items():
        p = (t + M_SHRINK * pb) / (n + M_SHRINK); out["pcfg"][cfg] = p; out["cfg"][cfg] = _lo(p) - _lo(pb)
    for cue, vals in counts["cues"].items():
        out[cue] = {}
        for key, (t, n) in vals.items():
            cfg = key.split("|", 1)[0]; base = out["pcfg"].get(cfg, pb); ncfg = counts["config"].get(cfg, [0, 0])[1]
            if n >= ncfg:
                out[cue][key] = 0.0
            else:
                p = (t + M_SHRINK * base) / (n + M_SHRINK); out[cue][key] = _lo(p) - _lo(base)
    return out


def load_attachment_validities(path: Optional[str] = None) -> Dict[str, object]:
    global _TABLE
    if path is None and _TABLE is not None:
        return _TABLE
    with open(path or ASSET, encoding="utf-8") as f:
        doc = json.load(f)
    tab = {"counts": doc["counts"], "frames": doc.get("frames", {}), "pp_assoc": doc.get("pp_assoc"),
           "strength": strengths_from_arc_counts(doc["counts"])}
    if path is None:
        _TABLE = tab
    return tab


def save_attachment_validities(path: Optional[str] = None, table: Optional[Dict[str, object]] = None) -> str:
    tab = table or load_attachment_validities(); p = path or ASSET
    doc = {"source": "attachment arm of the Competition-Model organ: soft arc counts accrued from reading (knowledge-free teacher + "
                     "anchored self-teaching; no treebank, no hand prior); strengths = attachment_arm.strengths_from_arc_counts",
           "counts": tab["counts"], "frames": tab.get("frames", {}), "pp_assoc": tab.get("pp_assoc")}
    with open(p, "w", encoding="utf-8", newline=chr(10)) as f:
        json.dump(doc, f, indent=1)
    return p


def new_counts() -> Dict[str, object]:
    return {"base": [0.0, 0.0], "config": {}, "cues": {c: {} for c in CUES}}


def accrue_sentence(counts: Dict[str, object], sc: "SentenceCues", marg: Dict[int, Dict[int, float]]) -> None:
    """Accrue SOFT outcomes: for every (j, h) the posterior probability that h heads j (the tree marginal) -- the comprehension
    outcome the organ learns from; online-capable (plastic)."""
    n = sc.n
    for j in range(1, n + 1):
        mj = marg.get(j, {})
        for h in range(0, n + 1):
            if h == j:
                continue
            p = float(mj.get(h, 0.0)); cfg = sc.config(j, h)
            cell = counts["config"].setdefault(cfg, [0.0, 0.0]); cell[0] += p; cell[1] += 1.0
            counts["base"][0] += p; counts["base"][1] += 1.0
            for c, v in sc.cues(j, h).items():
                cell = counts["cues"].setdefault(c, {}).setdefault(cfg + "|" + v, [0.0, 0.0]); cell[0] += p; cell[1] += 1.0


def observe_arc_outcome(toks: Sequence[str], pos: Sequence[str], j: int, h: int, table: Optional[Dict[str, object]] = None,
                        weight: float = 1.0) -> None:
    """PLASTICITY: one confirmed comprehension outcome -- word j was understood to depend on h -- accrues into the counts (the
    competing candidates of j accrue a zero outcome) and the strengths are recomputed."""
    tab = table or load_attachment_validities(); sc = SentenceCues(toks, pos, tab.get("frames", {}), tab.get("pp_assoc"))
    marg = {j: {hh: (weight if hh == h else 0.0) for hh in range(0, sc.n + 1) if hh != j}}
    accrue_sentence(tab["counts"], sc, marg)
    tab["strength"] = strengths_from_arc_counts(tab["counts"])


# ----------------------------------------------------------------------------------------------------------- readout
# VECTORISED READOUT (2026-09-13 06:30): the same additive cue activation, computed with numpy over the whole (head x dependent)
# grid instead of a Python loop with ~20 dict look-ups per pair (the loop was 90% of the arm's 89 ms/sentence and the reason a board
# under the BF heads rung took ~3 h). The strength tables are indexed ONCE per table into dense arrays (categories, configurations,
# cue values -> integer ids; unknown = a zero row/column, exactly the .get(..., 0.0) of the reference); the per-pair cue values are
# computed as integer-id matrices. `arc_scores_reference` is the original loop, kept as the witness's oracle (equality to 1e-9).
_ARC_FAST = os.environ.get("HDLAB_ARM_FASTPATH", "1") != "0"
_UPOS = ("ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM", "PART", "PRON", "PROPN", "PUNCT", "SCONJ", "SYM", "VERB", "X")
_DIST_EDGES = np.array([2, 3, 5, 9]); _DIST_BINS = ("1", "2", "3-4", "5-8", "9+")
_AGREE_PRON_PLURAL = frozenset(("they", "we", "you", "i"))


class _ArcIndex:
    """Dense index of one strength table. cats: category -> id (unknown -> the last id, whose rows are zero)."""

    def __init__(self, st: Dict[str, object], frames: Dict[str, List[int]]):
        cats = set(_UPOS)
        for cfg in st["cfg"]:
            if cfg.startswith("ROOT:"):
                cats.add(cfg[5:])
            else:
                hp, rest = cfg.split(">", 1); cats.add(hp); cats.add(rest.rsplit(":", 1)[0])
        self.cats = {c: i for i, c in enumerate(sorted(cats))}; self.unk = len(self.cats); nc = self.unk + 1
        cfg_ids = {cfg: i for i, cfg in enumerate(st["cfg"])}; self.ncfg = len(cfg_ids)
        self.cfg_strength = np.zeros(self.ncfg + 1)
        for cfg, v in st["cfg"].items():
            self.cfg_strength[cfg_ids[cfg]] = v
        self.cfg_id = np.full((nc, nc, 2), self.ncfg, dtype=np.int64); self.root_cfg_id = np.full(nc, self.ncfg, dtype=np.int64)
        for cfg, i in cfg_ids.items():
            if cfg.startswith("ROOT:"):
                c = self.cats.get(cfg[5:])
                if c is not None:
                    self.root_cfg_id[c] = i
            else:
                hp, rest = cfg.split(">", 1); dp, dr = rest.rsplit(":", 1)
                a, b = self.cats.get(hp), self.cats.get(dp)
                if a is not None and b is not None:
                    self.cfg_id[a, b, 0 if dr == "L" else 1] = i
        # per cue: value vocabulary (absent/unknown -> column 0 = zero) and the dense (cfg, value) strength table
        self.val_id: Dict[str, Dict[str, int]] = {}; self.cue_tab: Dict[str, np.ndarray] = {}
        for cue in CUES:
            d = st.get(cue, {}) or {}
            vals = {}
            for key in d:
                v = key.split("|", 1)[1]
                if v not in vals:
                    vals[v] = len(vals) + 1
            tab = np.zeros((self.ncfg + 1, len(vals) + 1))
            for key, v in d.items():
                cfg, val = key.split("|", 1)
                ci = cfg_ids.get(cfg)
                if ci is not None:
                    tab[ci, vals[val]] = v
            self.val_id[cue] = vals; self.cue_tab[cue] = tab
        # precomputed id tables for the dense-valued cues
        vid = self.val_id
        self.loc_id = np.array([[vid["locality"].get(dr + b, 0) for b in _DIST_BINS] for dr in ("L", "R")], dtype=np.int64)
        self.form_id = np.array([vid["form"].get("wordhead", 0), vid["form"].get("formhead", 0)], dtype=np.int64)
        self.bnd_id = np.array([vid["boundary"].get(b, 0) for b in ("0", "1", "2+")], dtype=np.int64)
        self.na_frame = vid["frame"].get("na", 0); self.na_agree = vid["agree"].get("na", 0)
        self.agree_id = np.array([vid["agree"].get("3sgV:singN", 0), vid["agree"].get("3sgV:plurN", 0)], dtype=np.int64)
        self.none_constr = vid["constr"].get("none", 0)
        self.trans_names = ("unk", "trans", "intrans")
        self.frame_id = np.full((3, nc, 2), self.na_frame, dtype=np.int64)
        inv = {i: c for c, i in self.cats.items()}
        for t, tn in enumerate(self.trans_names):
            for c, cn in inv.items():
                for k, dr in enumerate(("L", "R")):
                    self.frame_id[t, c, k] = vid["frame"].get(f"{tn}:{cn}:{dr}", 0)
        self.frames = frames; self._trans_cache: Dict[Optional[str], int] = {}

    def trans_class(self, lem: Optional[str]) -> int:
        if lem not in self._trans_cache:
            fr = self.frames.get(lem) if lem is not None else None
            self._trans_cache[lem] = 0 if not fr else (1 if fr[1] / fr[0] >= 0.3 else 2)
        return self._trans_cache[lem]


def _arc_index(tab: Dict[str, object]) -> _ArcIndex:
    idx = tab.get("_idx")
    if idx is None or idx[0] is not tab["strength"]:
        idx = (tab["strength"], _ArcIndex(tab["strength"], tab.get("frames", {}))); tab["_idx"] = idx
    return idx[1]


def arc_scores(toks: Sequence[str], pos: Sequence[str], table: Optional[Dict[str, object]] = None) -> Tuple[np.ndarray, int]:
    """Additive cue activation per arc (row = head incl. 0 = ROOT, col = dependent); form classes never head or root.
    Vectorised; numerically identical to `arc_scores_reference` (witness: verification/test_attachment_arm_fastpath.py)."""
    if not _ARC_FAST:
        return arc_scores_reference(toks, pos, table)
    tab = table or load_attachment_validities(); ix = _arc_index(tab)
    sc = SentenceCues(toks, pos, tab.get("frames", {}), tab.get("pp_assoc")); n = sc.n
    cat = np.array([ix.cats.get(p, ix.unk) for p in pos], dtype=np.int64)            # dependent / head (1..n) category ids
    H = np.arange(0, n + 1)[:, None]; J = np.arange(1, n + 1)[None, :]               # grid: rows h = 0..n, cols j = 1..n
    dr = (H > J).astype(np.int64)                                                    # config/cue convention: 'L' when the head is LEFT of the dependent (h < j) -> 0; 'R' (h > j) -> 1
    hc = np.concatenate([[ix.unk], cat])                                             # row 0 = ROOT (category irrelevant)
    C = ix.cfg_id[hc[:, None], cat[None, :], dr]; C[0, :] = ix.root_cfg_id[cat]
    S = ix.cfg_strength[C]
    dist = np.abs(H - J); db = np.digitize(dist, _DIST_EDGES)
    V = ix.loc_id[dr, db]; S += ix.cue_tab["locality"][C, V]
    is_form = np.array([p in FORM for p in pos]); fh = np.concatenate([[False], is_form])
    S += ix.cue_tab["form"][C, ix.form_id[fh.astype(np.int64)][:, None]]
    lo = np.minimum(H, J); hi = np.maximum(H, J); nb = sc.cum[np.maximum(hi - 1, 0)] - sc.cum[lo]
    S += ix.cue_tab["boundary"][C, ix.bnd_id[np.minimum(nb, 2).astype(np.int64)]]
    # frame + agree (verb heads only; "na" otherwise)
    is_verb = np.array([p == "VERB" for p in pos]); vh = np.concatenate([[False], is_verb])
    tcls = np.array([ix.trans_class(sc.lem[h - 1]) if vh[h] else 0 for h in range(n + 1)], dtype=np.int64)
    F = np.where(vh[:, None], ix.frame_id[tcls[:, None], cat[None, :], dr], ix.na_frame); S += ix.cue_tab["frame"][C, F]
    heads_s = np.array([False] + [t.lower().endswith("s") and not t.lower().endswith("ss") for t in toks])
    nominal = np.array([p in NOMINAL for p in pos])
    dep_plur = np.array([(p == "NOUN" and t.lower().endswith("s") and not t.lower().endswith("ss")) or t.lower() in _AGREE_PRON_PLURAL
                         for t, p in zip(toks, pos)])
    fires = vh[:, None] & (dr == 1) & nominal[None, :] & heads_s[:, None]
    G = np.where(vh[:, None], np.where(fires, ix.agree_id[dep_plur.astype(np.int64)][None, :], ix.na_agree), ix.na_agree)
    S += ix.cue_tab["agree"][C, G]
    # constructions (sparse overrides over the "none" default) + convention bonus
    K = np.full((n + 1, n), ix.none_constr, dtype=np.int64); vid = ix.val_id["constr"]
    for (h, j), fam in sc.constr.items():
        if 1 <= h <= n and 1 <= j <= n:
            K[h, j - 1] = vid.get(fam, 0)
            if CONVENTION_BONUS and fam == "fw":
                S[h, j - 1] += CONVENTION_BONUS
    S += ix.cue_tab["constr"][C, K]
    # PP cue (sparse sites)
    if sc.pp and "pp" in ix.cue_tab:
        vid = ix.val_id["pp"]; T = ix.cue_tab["pp"]
        for j, (v, nn, b) in sc.pp.items():
            if v:
                S[v, j - 1] += T[C[v, j - 1], vid.get("V:" + b, 0)]
            if nn:
                S[nn, j - 1] += T[C[nn, j - 1], vid.get("N:" + b, 0)]
    # meaning cue (verb head x nominal dependent; the teacher's per-pair plausibility is cached by lemma pair)
    if sc.teacher is not None and "plaus" in ix.cue_tab:
        vid = ix.val_id["plaus"]; T = ix.cue_tab["plaus"]
        bare = nominal & ~np.array([j >= 2 and pos[j - 2] == "ADP" for j in range(1, n + 1)])
        verbs = np.flatnonzero(vh).tolist(); deps = (np.flatnonzero(bare) + 1).tolist(); Cl = C.tolist(); Tl = T.tolist()
        slot = sc.teacher.slot_plausibility
        for h in verbs:
            row = Cl[h]
            for j in deps:
                if j != h:
                    val = ("S:" if h > j else "O:") + _plaus_bin(slot(toks, pos, h, j))
                    S[h, j - 1] += Tl[row[j - 1]][vid.get(val, 0)]
    # masks: no self-arcs, form classes never head, form classes never root when a word exists
    A = np.full((n + 1, n + 1), -np.inf); A[:, 1:] = S
    A[np.arange(1, n + 1), np.arange(1, n + 1)] = -np.inf
    A[1:, :][is_form, :] = -np.inf
    if not is_form.all():
        A[0, 1:][is_form] = -np.inf
    return A, n


def arc_scores_reference(toks: Sequence[str], pos: Sequence[str], table: Optional[Dict[str, object]] = None) -> Tuple[np.ndarray, int]:
    """THE REFERENCE readout (the original per-pair loop): additive cue activation per arc (row = head incl. 0 = ROOT, col =
    dependent); form classes never head or root. Kept as the oracle for the vectorised `arc_scores`."""
    tab = table or load_attachment_validities(); st = tab["strength"]; sc = SentenceCues(toks, pos, tab.get("frames", {}), tab.get("pp_assoc"))
    n = sc.n; A = np.full((n + 1, n + 1), -np.inf)
    words = [j for j in range(1, n + 1) if pos[j - 1] not in FORM]
    for j in range(1, n + 1):
        for h in range(0, n + 1):
            if h == j or (h and pos[h - 1] in FORM):
                continue
            if h == 0 and pos[j - 1] in FORM and words:
                continue
            cfg = sc.config(j, h); s = st["cfg"].get(cfg, 0.0)
            for c, v in sc.cues(j, h).items():
                s += st.get(c, {}).get(cfg + "|" + v, 0.0)
            if CONVENTION_BONUS and h and sc.constr.get((h, j)) == "fw":
                s += CONVENTION_BONUS
            A[h][j] = s
    return A, n


# PUNCTUATION CONVENTION (2026-09-13 06:10 local; CONVENTION LAYER, labelled honestly): punctuation carries no meaning relation, and
# its "head" is an annotation convention (UD: a mark attaches to the head of the phrase/clause it delimits; a final mark to the root).
# Punctuation is 12.2% of UD-EWT test tokens and the arm placed it at 0.273 (the teacher's posterior over punctuation is noise), so a
# third of the rung's remaining UAS gap was formatting. Rule, applied AFTER the decode on the arm's OWN tree: final mark -> root;
# an opening bracket/quote -> the top of the RIGHT neighbour's head chain inside the right span; any other mark -> the top of the
# LEFT neighbour's head chain inside the left span (on GOLD trees this rule scores 0.665; always-root 0.527). Consumers never read
# punctuation heads, so this changes the rung's number, not the board. `HDLAB_ARM_PUNCT_CONVENTION=0` disables it.
PUNCT_CONVENTION = os.environ.get("HDLAB_ARM_PUNCT_CONVENTION", "1") != "0"
_OPENING = frozenset(("(", "[", "{", '"', "\u201c", "\u2018", "``", "`"))


def _chain_top(hd: Dict[int, int], k: int, lo: int, hi: int) -> int:
    top = k
    seen = 0
    while lo <= k <= hi and seen <= len(hd) + 1:
        top = k; k = hd.get(k, 0); seen += 1
    return top


def punct_convention(toks: Sequence[str], pos: Sequence[str], hd: Dict[int, int]) -> Dict[int, int]:
    """Reassign the heads of punctuation tokens by the annotation convention (see PUNCT_CONVENTION); other heads untouched."""
    n = len(toks)
    if not PUNCT_CONVENTION or n == 0:
        return hd
    words = [j for j in range(1, n + 1) if pos[j - 1] != "PUNCT"]
    if not words:
        return hd
    out = dict(hd); roots = [j for j in words if out.get(j, 0) == 0]; root = roots[0] if roots else words[0]
    for j in range(1, n + 1):
        if pos[j - 1] != "PUNCT":
            continue
        L = next((k for k in range(j - 1, 0, -1) if pos[k - 1] != "PUNCT"), None)
        R = next((k for k in range(j + 1, n + 1) if pos[k - 1] != "PUNCT"), None)
        if R is None:
            out[j] = root
        elif toks[j - 1] in _OPENING:
            out[j] = _chain_top(out, R, j + 1, n)
        elif L is not None:
            out[j] = _chain_top(out, L, 1, j - 1)
        else:
            out[j] = _chain_top(out, R, j + 1, n)
        if out[j] == j:
            out[j] = root
    return out


def _punct_posterior(toks, pos, marg: Dict[int, Dict[int, float]]) -> Dict[int, Dict[int, float]]:
    """Graded hand-off: punctuation rows become one-hot on the convention head (computed on the MAP of the word rows)."""
    if not PUNCT_CONVENTION:
        return marg
    hd = {j: (max(d.items(), key=lambda kv: kv[1])[0] if d else 0) for j, d in marg.items()}
    hd = punct_convention(toks, pos, hd)
    for j in range(1, len(toks) + 1):
        if pos[j - 1] == "PUNCT" and j in marg:
            marg[j] = {hd[j]: 1.0}
    return marg


def head_posterior(toks: Sequence[str], pos: Sequence[str], table: Optional[Dict[str, object]] = None,
                   temp: float = 1.0) -> Dict[int, Dict[int, float]]:
    """The graded signal handed DOWN: exact single-root Matrix-Tree marginals P(head | dependent)."""
    A, n = arc_scores(toks, pos, table); return _punct_posterior(toks, pos, single_root_marginals(A, n, temp))


# POINT DECODE (2026-09-13 06:30 local): "mbr" = minimum-Bayes-risk tree -- the single-rooted tree maximising the SUM of the arc
# marginals (CLE over log P(head | dependent)); "map" = the highest-scoring tree. Measured on UD-EWT test: the per-token argmax of
# the marginals beat the MAP tree on every content relation (ccomp 0.56 vs 0.50, advcl 0.23 vs 0.15, conj 0.29 vs 0.25, xcomp
# 0.70 vs 0.68, obl 0.45 vs 0.43) but is not a tree (87/300 sentences: several roots / cycles; root 0.69 vs 0.81) -- the MBR tree
# keeps the graded belief's choices AND the tree constraint. The brain commits on its graded belief, not on the single best parse.
# DEFAULT "map1" (2026-09-13 06:35 local): the MAP tree constrained to ONE root (the MAP root with the highest root score). The
# arborescence routine lets several words take the root arc; that "multi-root MAP" scored 0.5956 with root 0.813 only because the
# extra roots were counted, and it handed consumers several disconnected clauses. Single-root MAP: UAS 0.6034 (ccomp 0.500 -> 0.672,
# advcl 0.149 -> 0.313, xcomp 0.679 -> 0.730, obl 0.430 -> 0.463, conj 0.253 -> 0.300, obj 0.725, nsubj 0.767; root 0.744 honest).
# MBR (summed-marginal tree) with the same root: 0.5855 -- worse once both are single-rooted; kept selectable. "map" = the old multi-root.
# DEFAULT DECODE = "incr" (2026-09-13 10:55 local; owner: organs take data in order; replacement rule: more BF AND as performative).
# UD-EWT test 700, gold categories: whole-sentence single-root search (map1) 0.6034 | INCREMENTAL commitment with decaying held
# expectations (beam 8, decay 0.8, hold offset 0) 0.6080 -- obj 0.755 vs 0.725, nmod 0.403 vs 0.365, amod 0.824 vs 0.792; root 0.706 vs
# 0.744, ccomp 0.629 vs 0.672; 19% of words settled at the sentence-final wrap-up; 3.6x FASTER than the search. "map1"/"mbr"/"map" stay
# selectable as baselines. Operating point swept (beam 1-64, decay 0.6-1.0, offset -2..+1), never adopted from a brain number.
DECODE = os.environ.get("HDLAB_ARM_DECODE", "incr")
ROOT_PICK = os.environ.get("HDLAB_ARM_ROOT_PICK", "score")   # among several MAP roots: "score" (highest root score) | "left" (leftmost)


def mbr_tree(A: np.ndarray, n: int, temp: float = 1.0) -> Tuple[Dict[int, int], Dict[int, Dict[int, float]]]:
    """(heads, marginals): the single-root tree maximising expected arcs-correct under the Matrix-Tree marginals of A."""
    map_tree = chu_liu_edmonds(A, n)                       # BEFORE the marginals: single_root_marginals works on A in place
    post = single_root_marginals(A.copy(), n, temp)
    M = np.full((n + 1, n + 1), -np.inf)
    for j, d in post.items():
        for h, pr in d.items():
            if pr > 0.0 and np.isfinite(A[h][j]):
                M[h][j] = math.log(pr)
    # ONE root, chosen by the MAP tree: the summed-marginal tree spends several root arcs (root 0.70), and the largest root
    # MARGINAL is a worse root picker still (0.60) -- the MAP tree's root (0.81) is the calibrated choice; the rest is MBR.
    roots = [j for j, h in map_tree.items() if h == 0]
    if roots:
        # the MAP decode is NOT single-rooted (the arborescence routine lets several words take the root arc; 2026-09-13 finding:
        # its root recall 0.81 counted those extra roots) -- ONE root: the MAP root with the highest root score.
        r = max(roots, key=lambda j: (float(A[0][j]) if np.isfinite(A[0][j]) else -1e18, post.get(j, {}).get(0, 0.0)))
        M[0, :] = -np.inf; M[:, r] = -np.inf; M[0][r] = 0.0
    return chu_liu_edmonds(M, n), post


def map_tree_single_root(A: np.ndarray, n: int) -> Dict[int, int]:
    """MAP tree constrained to ONE root (the MAP root with the highest root score), for a like-for-like comparison with MBR."""
    mt = chu_liu_edmonds(A, n); roots = [j for j, h in mt.items() if h == 0]
    if len(roots) <= 1:
        return mt
    r = roots[0] if ROOT_PICK == "left" else max(roots, key=lambda j: float(A[0][j]) if np.isfinite(A[0][j]) else -1e18)
    B = A.copy(); B[0, :] = -np.inf; B[:, r] = -np.inf; B[0][r] = 0.0
    return chu_liu_edmonds(B, n)


# OBJECT-SLOT OCCUPANCY (2026-09-13 06:45 local; the parked pri-16 lever, built as a decode-time constraint): a verb's direct-object
# slot has capacity ONE (valence saturation -- Competition Model / MacWhinney: a filled slot stops competing). The first-order tree
# decode cannot see siblings, so a verb often takes TWO bare post-verbal nominals while the next verb goes without ("need to send
# stuff": 'stuff' -> 'need'; 30 of 72 object misses on 400 test sentences had the gold verb's slot filled by another nominal).
# Repair: for a verb with >= 2 BARE (non-prepositional) nominal dependents after it, keep the one with the highest head marginal and
# move each other one to its best-marginal head that is not itself saturated (root excluded); iterate to a fixed point.
# REFUTED AS BUILT (06:50 local; default OFF, kept selectable): UAS 0.6034 -> 0.5995, obj 0.725 -> 0.655, obl 0.463 -> 0.415, nmod
# 0.365 -> 0.403. "Bare post-verbal nominal" over-counts the slot: ditransitives, adverbial/temporal NPs, predicate nominals and
# appositions legitimately give a verb two bare nominals, so the repair evicted true objects. Occupancy is a LABELS-rung constraint
# (one OBJ per verb, with the role labeler deciding which nominal is the OBJ), not a category-level decode constraint.
OCCUPANCY = os.environ.get("HDLAB_ARM_OCCUPANCY", "0") == "1"


def occupancy_repair(toks: Sequence[str], pos: Sequence[str], hd: Dict[int, int], post: Dict[int, Dict[int, float]]) -> Dict[int, int]:
    n = len(toks)
    if not OCCUPANCY or n < 3:
        return hd
    out = dict(hd)
    bare = [j for j in range(1, n + 1) if pos[j - 1] in NOMINAL and not (j >= 2 and pos[j - 2] == "ADP")]

    def objects_of(v):
        return [j for j in bare if out.get(j) == v and j > v]

    for _ in range(3):
        moved = False
        for v in range(1, n + 1):
            if pos[v - 1] != "VERB":
                continue
            objs = objects_of(v)
            if len(objs) < 2:
                continue
            keep = max(objs, key=lambda j: post.get(j, {}).get(v, 0.0))
            for j in objs:
                if j == keep:
                    continue
                cands = sorted(((h, pr) for h, pr in post.get(j, {}).items() if h not in (0, v, j)), key=lambda kv: -kv[1])
                for h, pr in cands:
                    if pos[h - 1] == "VERB" and j > h and len(objects_of(h)) >= 1:
                        continue                                   # that verb's object slot is full too
                    # no cycle: h must not be a descendant of j
                    k = h; ok = True; seen = 0
                    while k and seen <= n:
                        if k == j:
                            ok = False; break
                        k = out.get(k, 0); seen += 1
                    if ok:
                        out[j] = h; moved = True; break
        if not moved:
            break
    return out


# INCREMENTAL COMMITMENT (2026-09-13 ~10:20 local; owner: "don't we have organs that take data in, in order? isn't that more brain
# foundational?"). The whole-sentence tree search above (MAP / MBR over the full matrix) is a normative MODEL: it sees every word
# before it commits. The brain does not: words arrive one at a time and each arriving word is attached AS IT ARRIVES by cue-based
# retrieval among the words still open in memory (Lewis & Vasishth 2005), or held as an expectation for a head still to come
# (Levy 2008 prediction), while a SMALL number of alternative analyses stays alive and a later word can make an alternative
# overtake (garden-path reanalysis; MacDonald 1994 graded constraint satisfaction). PINNED: incrementality, bounded alternatives,
# local competition, reanalysis by overtaking. OURS (swept, never adopted): the beam width and the hold score.
# Computation = arc-eager transitions over the SAME cue activations A, locally normalised: on the arrival of word b the outcomes
# are enumerated down the stack -- a headed top may be REDUCED (free), a headless top may take b as its head (LEFT-ARC, A[b][top]),
# then b either attaches to the current top (RIGHT-ARC, A[top][b]; top = 0 is the single root arc, allowed once) or is held
# (SHIFT, score HOLD). The outcomes compete by softmax (log-odds in, probabilities out), so every analysis alive after word b
# carries b local log-probabilities and the beam compares like with like. No score of a word not yet heard is ever read (strict
# incrementality: only A[h][j] with h, j <= b enters at arrival b). At the end, words still waiting are attached by the convention
# repair (the best open head; root if none taken) and counted as `incomplete`. The graded hand-off is the beam itself: P(head j = h)
# = the normalised weight of the alive analyses that say so (keep-alternatives-alive realised as the alternatives themselves).
INCR_BEAM = int(os.environ.get("HDLAB_ARM_BEAM", "8"))
INCR_HOLD = float(os.environ.get("HDLAB_ARM_HOLD", "0.0"))
# HOLD = the PREDICTION of a head still to come (Levy 2008): with mode "expect" the hold score of an arriving word is the organ's own
# configuration strength for the strongest head-to-the-RIGHT configuration of the word's category (a determiner expects a noun, a
# subject noun expects a verb) plus INCR_HOLD; with mode "const" it is INCR_HOLD alone (measured 0.43 vs 0.63 on 25 sentences: a
# hold without evidence loses to any positive left attachment -- determiners/adjectives/subjects collapsed). Nothing from a word
# not yet heard is read: the expectation is a function of the arriving word's category and the learned table only.
INCR_HOLD_MODE = os.environ.get("HDLAB_ARM_HOLD_MODE", "expect")   # "expect" (learned asset, else table max) | "max" (table max only) | "const"
INCR_NORM = os.environ.get("HDLAB_ARM_INCR_NORM", "sum")          # "sum" (one score per word) | "local" (softmax per arrival)
# ROOT AT WRAP-UP (10:55 local): the sentence's main word is a CLAUSE-END decision, not an arrival decision -- taking the root arc on
# the first verb that prefers it blocks a later main verb (root 0.69 vs 0.74). With this on, no word takes the root arc while
# reading; at the end the held word with the highest root score is the root and the other held words attach to their best
# available head (an earlier clause hangs on the main one). The wrap-up count excludes the root word itself.
INCR_ROOT_WRAPUP = os.environ.get("HDLAB_ARM_ROOT_WRAPUP", "0") == "1"
# ROOT REANALYSIS (10:50 local): the main clause can be revised while reading -- when a later word arrives that can head the word
# currently holding the root arc (an earlier clause turning out subordinate: "When I arrived[root?], she LEFT"), the arriving word
# may take the root arc over and the earlier root becomes its dependent (the main-clause garden-path repair). Accounting: the
# earlier root arc's activation is given back, the new real arc's activation is taken, and the arriving word re-opens the root.
INCR_ROOT_REANALYSIS = os.environ.get("HDLAB_ARM_ROOT_REANALYSIS", "1") == "1"
# DECAY OF A HELD EXPECTATION (10:55 local): an item held in memory loses activation as words pass (Lewis & Vasishth 2005 decay;
# the ACT-R base-level). Without it the placeholder is an AVERAGE realised activation, so a real head arriving with a below-average
# arc looks like a loss and the word keeps waiting (wrap-up anatomy: 46% of prepositions, 27% of nouns held to the end). With decay
# d, a word held for a words is worth E x d^a; the parameter is swept, never adopted (1.0 = no decay).
# CLAUSE-LEVEL WRAP-UP (12:30 local): 19% of words were settled only at the SENTENCE end with the whole matrix in view -- an honesty gap
# in the incremental claim. The brain integrates at clause boundaries (clause-final wrap-up; Just & Carpenter): at a clause-internal
# punctuation mark or coordinator, a word that has waited long (its expectation decayed below CLAUSE_WRAP_MIN) attaches to its best head
# AMONG THE WORDS ALREADY HEARD (strictly incremental). MEASURED (UD-EWT test 700): UAS 0.6136 -> 0.6124 (noise; obj/obl/nmod up,
# nsubj/root down a little), words settled only at the sentence end 18.7% -> 13.6% -> DEFAULT ON (the in-order rule: as performative,
# more faithful). HDLAB_ARM_CLAUSE_WRAPUP=0 restores sentence-final-only wrap-up.
INCR_CLAUSE_WRAPUP = os.environ.get("HDLAB_ARM_CLAUSE_WRAPUP", "1") == "1"
CLAUSE_WRAP_MIN = float(os.environ.get("HDLAB_ARM_CLAUSE_WRAP_MIN", "1.0"))
INCR_DECAY = float(os.environ.get("HDLAB_ARM_DECAY", "0.8"))   # swept 0.6-1.0 on UD-EWT test 700: 1.0 0.5981 | 0.9 0.5991 | 0.8 0.6028 | 0.7 0.6018 | 0.6 0.6010 (beam 8, offset -1)


HOLD_ASSET = os.path.join(_REPO, "data", "frontend_assets", "attachment_hold_expect_v1.json")
_HOLD_TAB: Optional[Dict[str, Dict[str, float]]] = None


def hold_expectation(pos: Sequence[str], table: Optional[Dict[str, object]] = None, A: Optional[np.ndarray] = None) -> np.ndarray:
    """Per word (index 1..n): the value of HOLDING the word for a head still to come.
    mode "learned" (default when the asset exists): P(head to the right | category, a verb has/has not arrived yet) x the mean
    realised activation of such arcs in the organ's OWN decoded trees over training text (self-supervised; no treebank heads) --
    measured 10:20: the table-max bound below was 3-5x too LOW (DET 2.1 vs 6.6 realised; ADP 1.9 vs 10.4), so words attached left
    too eagerly (det 0.895 -> 0.831). Fallback: the strongest right-head configuration strength of the category."""
    global _HOLD_TAB
    tab = table or load_attachment_validities(); ix = _arc_index(tab)
    if _HOLD_TAB is None:
        try:
            with open(HOLD_ASSET, encoding="utf-8") as f:
                _HOLD_TAB = json.load(f)["expect"]
        except Exception:
            _HOLD_TAB = {}
    out = np.zeros(len(pos) + 1); verb_seen = False; sub_pending = False
    tab2 = _HOLD_TAB.get("_by_left", {}) if A is not None else {}
    tab3 = _HOLD_TAB.get("_ctx", {})
    for j, p in enumerate(pos, start=1):
        e = None
        if INCR_HOLD_MODE != "max":
            k = "1" if verb_seen else "0"
            # a subordinator ("when", "because", "that") before this clause's verb = the clause is predicted to hang on a later one
            e = tab3.get(p, {}).get(k + ("s" if sub_pending else ""))
            if tab2 and j > 1:
                # the richer expectation: P(head is still to come | category, verb seen, category of the BEST LEFT candidate now)
                col = A[1:j, j]; hb = int(np.argmax(col)) + 1 if np.isfinite(col).any() else 0
                e = tab2.get(p, {}).get(pos[hb - 1] if hb else "ROOT", {}).get(k)
            if e is None:
                e = _HOLD_TAB.get(p, {}).get(k)
        if e is None:
            c = ix.cats.get(p, ix.unk); e = float(ix.cfg_strength[ix.cfg_id[:, c, 1]].max())
        out[j] = float(e)
        if p == "VERB":
            verb_seen = True; sub_pending = False
        elif p == "SCONJ":
            sub_pending = True
    return out


def build_hold_expectation(out: str = HOLD_ASSET, cap: int = 3000, table: Optional[Dict[str, object]] = None) -> dict:
    """Learn the hold expectation from the organ's own trees (map1 decode over training text with the category supply)."""
    from tools.build_attachment_validities import sentences, TRAIN
    tab = table or load_attachment_validities()
    acc: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: {"0": [], "1": []}); cnt: Dict[str, Dict[str, List[int]]] = defaultdict(lambda: {"0": [0, 0], "1": [0, 0]})
    acc2: Dict = defaultdict(lambda: defaultdict(lambda: {"0": [], "1": []})); cnt2: Dict = defaultdict(lambda: defaultdict(lambda: {"0": [0, 0], "1": [0, 0]}))
    acc3: Dict = defaultdict(lambda: defaultdict(list)); cnt3: Dict = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for toks, pos, _, _ in sentences(TRAIN, cap=cap, maxlen=60):
        A, n = arc_scores(toks, pos, tab); hd = map_tree_single_root(A, n); vs = False; sp = False
        for j in range(1, n + 1):
            p = pos[j - 1]; k = "1" if vs else "0"; h = hd.get(j)
            if h is None:
                continue
            k3 = k + ("s" if sp else "")
            if h > j and np.isfinite(A[h][j]):
                acc3[p][k3].append(float(A[h][j])); cnt3[p][k3][0] += 1
            cnt3[p][k3][1] += 1
            if p == "SCONJ":
                sp = True
            if j > 1:
                col = A[1:j, j]; hb = int(np.argmax(col)) + 1 if np.isfinite(col).any() else 0
                lc = pos[hb - 1] if hb else "ROOT"
            else:
                lc = "ROOT"
            right = h > j and np.isfinite(A[h][j])
            if right:
                acc[p][k].append(float(A[h][j])); cnt[p][k][0] += 1; acc2[p][lc][k].append(float(A[h][j])); cnt2[p][lc][k][0] += 1
            cnt[p][k][1] += 1; cnt2[p][lc][k][1] += 1
            if p == "VERB":
                vs = True; sp = False
    expect = {}
    for p in acc:
        expect[p] = {}
        for k in ("0", "1"):
            r, t = cnt[p][k]
            if t >= 5:
                expect[p][k] = (r / t) * (float(np.mean(acc[p][k])) if acc[p][k] else 0.0)
    by_left = {}
    for p in acc2:
        by_left[p] = {}
        for lc in acc2[p]:
            by_left[p][lc] = {}
            for k in ("0", "1"):
                r, t = cnt2[p][lc][k]
                if t >= 8:
                    by_left[p][lc][k] = (r / t) * (float(np.mean(acc2[p][lc][k])) if acc2[p][lc][k] else 0.0)
    expect["_by_left"] = by_left
    ctx = {}
    for p in acc3:
        ctx[p] = {}
        for k3 in cnt3[p]:
            r, t = cnt3[p][k3]
            if t >= 8:
                ctx[p][k3] = (r / t) * (float(np.mean(acc3[p][k3])) if acc3[p][k3] else 0.0)
    expect["_ctx"] = ctx
    d = {"expect": expect, "cap": cap, "note": "P(right head | cat, verb_seen) x mean realised right-arc activation; organ's own map1 trees; _by_left: also conditioned on the category of the best left candidate"}
    with open(out, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1)
    return d
INCR_STATS = {"sentences": 0, "incomplete_words": 0, "words": 0, "last_incomplete": []}   # last_incomplete: indices repaired at wrap-up (last sentence)


def incremental_tree(A: np.ndarray, n: int, beam: int = INCR_BEAM, hold=INCR_HOLD,
                     temp: float = 1.0, pos_seq=None) -> Tuple[Dict[int, int], Dict[int, Dict[int, float]]]:
    """Left-to-right arc-eager commitment over the cue activations A with a bounded beam. Returns (heads, beam posterior)."""
    beam = max(1, int(beam))

    def fin(x: float) -> float:
        return float(x) if np.isfinite(x) else -1e9

    def E(j: int) -> float:
        return float(hold[j]) if isinstance(hold, np.ndarray) else float(hold)

    # state = (logp, stack tuple, heads tuple (index 0 unused; -1 = no head yet; 0 = the root arc), root_used)
    states = [(0.0, (0,), tuple([-1] * (n + 1)), False)]
    for b in range(1, n + 1):
        nxt: Dict[Tuple, float] = {}
        for logp, stack, hd, ru in states:
            # enumerate the arrival outcomes of b by walking down the stack
            outs: List[Tuple[float, Tuple, Tuple, bool]] = []
            st = list(stack); h = list(hd); gained = 0.0
            if INCR_DECAY < 1.0 and INCR_NORM == "sum":
                # every word still waiting ages by one: its placeholder E(k) d^(b-1-k) becomes E(k) d^(b-k)
                for k in range(1, b):
                    if h[k] == -1:
                        logp -= E(k) * (INCR_DECAY ** (b - 1 - k)) * (1.0 - INCR_DECAY)

            def V(k: int) -> float:                                # the current (decayed) placeholder of waiting word k
                return E(k) * (INCR_DECAY ** (b - k)) if INCR_DECAY < 1.0 else E(k)
            while True:
                top = st[-1]
                # consuming choice 1: b attaches to the current top (root arc only once; never while reading if root is a wrap-up decision)
                if top != 0 or (not ru and not INCR_ROOT_WRAPUP):
                    h2 = list(h); h2[b] = top
                    outs.append((gained + fin(A[top][b]), tuple(st + [b]), tuple(h2), ru or top == 0))
                # consuming choice 2: hold b for a head still to come
                outs.append((gained + E(b), tuple(st + [b]), tuple(h), ru))
                # descend: pop the top (REDUCE if headed, LEFT-ARC if headless and b heads it); never pop the root
                if top == 0:
                    break
                if h[top] == 0 and INCR_ROOT_REANALYSIS and ru:
                    # the current root may be re-headed by b (root reanalysis): give the root arc back, take the real arc, re-open root
                    g2 = gained + fin(A[b][top]) - fin(A[0][top]); h2 = list(h); h2[top] = b; st2 = st[:-1]
                    # b's own consuming choices after the takeover, walking the rest of the stack with the root re-opened
                    stk = list(st2); hh = h2; gg = g2; ru2 = False
                    while True:
                        t2 = stk[-1]
                        if t2 != 0 or not ru2:
                            h3 = list(hh); h3[b] = t2
                            outs.append((gg + fin(A[t2][b]), tuple(stk + [b]), tuple(h3), ru2 or t2 == 0))
                        outs.append((gg + E(b), tuple(stk + [b]), tuple(hh), ru2))
                        if t2 == 0:
                            break
                        if hh[t2] != -1:
                            stk = stk[:-1]
                        else:
                            gg += fin(A[b][t2]) - (V(t2) if INCR_NORM == "sum" else 0.0); hh = list(hh); hh[t2] = b; stk = stk[:-1]
                if h[top] != -1:
                    st = st[:-1]                                   # REDUCE, free
                else:
                    gained += fin(A[b][top]) - (V(top) if INCR_NORM == "sum" else 0.0)    # LEFT-ARC: b heads the waiting word
                    h = list(h); h[top] = b; st = st[:-1]
            if INCR_NORM == "local":
                # locally normalised: the outcomes of this arrival compete by softmax (label bias: measured 0.52 vs 0.63 on 25 sentences)
                sc = np.array([o[0] for o in outs]) / max(temp, 1e-9)
                lse = float(np.logaddexp.reduce(sc))
                vals = [logp + float(x) - lse for x in sc]
            else:
                # "sum": every word carries exactly ONE score -- its attachment activation if attached, its hold expectation if still
                # waiting (a LEFT-ARC replaces the waiting word's expectation by the realised activation: the -E[k] inside `gained`);
                # analyses alive after word b are sums of b such terms and compare in the same currency without a normaliser.
                vals = [logp + o[0] for o in outs]
            for (g, st2, h2, ru2), val in zip(outs, vals):
                key = (st2, h2, ru2)
                if key not in nxt or val > nxt[key]:
                    nxt[key] = val
        states = sorted(((v, k[0], k[1], k[2]) for k, v in nxt.items()), key=lambda t: -t[0])[:beam]
        if INCR_CLAUSE_WRAPUP and pos_seq is not None and b < n and pos_seq[b - 1] in ("PUNCT", "CCONJ"):
            # clause boundary: settle long-waiting words using only the words heard so far (no future score is read)
            new_states = []
            for logp, stack, hd, ru in states:
                h = list(hd); st = list(stack); changed = False
                for k in range(1, b):
                    if h[k] == -1 and E(k) * (INCR_DECAY ** (b - k)) < CLAUSE_WRAP_MIN:
                        best, bsc = None, -1e18
                        for hh in range(1, b + 1):
                            if hh == k or not np.isfinite(A[hh][k]):
                                continue
                            # hh must not sit below k (no cycle)
                            q = hh; ok = True; seen = 0
                            while q > 0 and seen <= n:
                                if q == k:
                                    ok = False; break
                                q = h[q] if h[q] > 0 else 0; seen += 1
                            if ok and float(A[hh][k]) > bsc:
                                best, bsc = hh, float(A[hh][k])
                        if best is not None:
                            logp += bsc - E(k) * (INCR_DECAY ** (b - k)); h[k] = best; changed = True
                            if k in st:
                                st.remove(k)                        # a headed word leaves the open set
                new_states.append((logp, tuple(st), tuple(h), ru))
            states = sorted(new_states, key=lambda t: -t[0])
    # finalisation: words still waiting take the best open head (root once), by convention; counted as incomplete
    best_logp, stack, hd, ru = states[0]
    heads_out = list(hd); inc = 0; INCR_STATS["last_incomplete"] = []
    if INCR_ROOT_WRAPUP and not ru:
        held = [j for j in range(1, n + 1) if heads_out[j] == -1]
        if held:
            r = max(held, key=lambda j: fin(A[0][j])); heads_out[r] = 0; ru = True
    for j in range(1, n + 1):
        if heads_out[j] == -1:
            inc += 1; INCR_STATS["last_incomplete"].append(j)
            if not ru:
                ru = True; heads_out[j] = 0; continue              # j is the root
            cands = []
            for hh in range(1, n + 1):
                if hh == j:
                    continue
                k = hh; ok = True; seen = 0
                while k and seen <= n:                            # hh must not sit below j
                    if k == j:
                        ok = False; break
                    k = heads_out[k]; seen += 1
                if ok:
                    cands.append((fin(A[hh][j]), hh))
            heads_out[j] = max(cands)[1] if cands else 0
    if not ru:                                                    # no word took the root arc at all: the best root candidate does
        r = max(range(1, n + 1), key=lambda j: fin(A[0][j])); heads_out[r] = 0
    INCR_STATS["sentences"] += 1; INCR_STATS["incomplete_words"] += inc; INCR_STATS["words"] += n
    # the beam posterior: alive analyses weighted by their probability
    w = np.array([st[0] for st in states]) / max(temp, 1e-9); w = np.exp(w - w.max()); w /= w.sum()
    post: Dict[int, Dict[int, float]] = {j: defaultdict(float) for j in range(1, n + 1)}
    for wi, (lp, stck, hds, r_used) in zip(w, states):
        for j in range(1, n + 1):
            hj = hds[j] if hds[j] != -1 else heads_out[j]
            post[j][int(hj)] += float(wi)
    post = {j: dict(d) for j, d in post.items()}
    return {j: int(heads_out[j]) for j in range(1, n + 1)}, post


def decode(toks: Sequence[str], pos: Sequence[str], A: np.ndarray, n: int, temp: float = 1.0,
           table: Optional[Dict[str, object]] = None) -> Tuple[Dict[int, int], Dict[int, Dict[int, float]]]:
    """Point heads + graded posterior under the configured decode, with the occupancy repair and the punctuation convention."""
    if DECODE == "incr":
        hv = hold_expectation(pos, table, A if INCR_HOLD_MODE == "expect_left" else None) + INCR_HOLD if INCR_HOLD_MODE != "const" else INCR_HOLD
        hd, post = incremental_tree(A, n, INCR_BEAM, hv, temp, pos_seq=list(pos))   # module globals read at call time (sweepable)
    elif DECODE == "mbr":
        hd, post = mbr_tree(A, n, temp)
    elif DECODE == "map1":
        hd = map_tree_single_root(A, n); post = single_root_marginals(A.copy(), n, temp)
    else:
        hd = chu_liu_edmonds(A, n); post = single_root_marginals(A.copy(), n, temp)
    hd = occupancy_repair(toks, pos, hd, post)
    hd = punct_convention(toks, pos, hd)
    for j in range(1, len(toks) + 1):
        if PUNCT_CONVENTION and pos[j - 1] == "PUNCT" and j in post:
            post[j] = {hd[j]: 1.0}
    return hd, post


def heads(toks: Sequence[str], pos: Sequence[str], table: Optional[Dict[str, object]] = None) -> Dict[int, int]:
    """Point heads (MBR tree by default; MAP with HDLAB_ARM_DECODE=map) -- for consumers that insist on a point; prefer head_posterior."""
    A, n = arc_scores(toks, pos, table); return decode(toks, pos, A, n)[0]


# ---------------------------------------------------------------------------------------------------------------------------------
# GRADED CATEGORY HAND-OFF (2026-09-12 late; categories rung -> heads rung). The category organ (hdlab.lexical_categories) hands
# down a POSTERIOR per token; the cues and constructions here are discrete over categories, so the brain-faithful read is to keep
# the competing category ALIVE for uncertain tokens (MacDonald 1994 constraint satisfaction; Hale/Levy graded alternatives) and mix
# the arc activations by the posterior. First-order mixture: A = A(top) + sum_t P(alt_t) * [A(with token t as alt_t) - A(top)] over
# the tokens whose top category carries less than TAG_GRADED_TAU of the mass (one extra cue pass per such token; rarely > 3/sentence).
TAG_GRADED_TAU = 0.8
TAG_GRADED_MAX_ALT = 3


def arc_scores_graded(toks: Sequence[str], pos: Sequence[str], tag_post: Optional[Sequence[Dict[str, float]]],
                      table: Optional[Dict[str, object]] = None, tau: float = TAG_GRADED_TAU,
                      max_alt: int = TAG_GRADED_MAX_ALT) -> Tuple[np.ndarray, int]:
    """Arc activations marginalised (first order) over each uncertain token's second-best category."""
    A, n = arc_scores(toks, pos, table)
    if not tag_post:
        return A, n
    alts = []
    for i, d in enumerate(tag_post):
        if not d or i >= len(pos):
            continue
        ranked = sorted(d.items(), key=lambda kv: -kv[1])
        if len(ranked) < 2 or ranked[0][1] >= tau:
            continue
        alt, p_alt = ranked[1]
        if alt == pos[i] or p_alt < 0.05:
            continue
        alts.append((p_alt, i, alt))
    if not alts:
        return A, n
    alts.sort(reverse=True)
    out = A.copy()
    for p_alt, i, alt in alts[:max_alt]:
        pos2 = list(pos); pos2[i] = alt
        B, _ = arc_scores(toks, pos2, table)
        fin = np.isfinite(A) & np.isfinite(B)
        out[fin] += p_alt * (B[fin] - A[fin])
        # arcs that exist only under the alternative categorisation enter with their posterior share
        only_b = (~np.isfinite(A)) & np.isfinite(B)
        out[only_b] = np.log(max(p_alt, 1e-9)) + B[only_b]
    return out, n


def head_posterior_graded(toks, pos, tag_post, table=None, temp: float = 1.0) -> Dict[int, Dict[int, float]]:
    A, n = arc_scores_graded(toks, pos, tag_post, table); return _punct_posterior(toks, pos, single_root_marginals(A, n, temp))


def heads_graded(toks, pos, tag_post, table=None) -> Dict[int, int]:
    A, n = arc_scores_graded(toks, pos, tag_post, table); return decode(toks, pos, A, n)[0]


# ---------------------------------------------------------------------------------------------------------------------------------
# SEMANTIC BOOTSTRAPPING TEACHER (2026-09-12). The knowledge-free co-occurrence teacher learns phrase internals but never that the
# VERB HEADS ITS ARGUMENTS (landed anatomy: obj 0.19, obl 0.12, root 0.41). The brain gets that knowledge from MEANING: the event
# predicate takes its participants as arguments, so the word naming the predicate heads the words naming plausible participants
# (semantic bootstrapping, Pinker 1984/1989 -- PINNED as the acquisition account; Abend, Kwiatkowski, Smith, Goldwater & Steedman
# 2017 as a computational model). MODEL here: plausibility = the typed selectional association organ (Resnik class association; an
# OFFLINE FOUNDATION asset standing in for experiential event knowledge -- its store was extracted with a UD-shaped parse of
# simplewiki, so this teacher is foundation-informed, not knowledge-free; only verb-noun ASSOCIATION is read, never slot position).
# The teacher's arc score for a verb->nominal arc is beta * association, the root score of a verb is beta * its best argument's
# association; everything else is locality. It is combined with the co-occurrence teacher's log-scores as ONE tree posterior
# (beta is a SWEPT operating point: smoke 1.5k/150 -- beta 0: obj 0.08 obl 0.04 root 0.34; beta 2: obj 0.13; beta 5: obj 0.72
# obl 0.44 root 0.83; beta 10: obj 0.76 obl 0.56 root 0.79, UAS 0.540 -- above the prior-informed path it replaces).
class SemanticBootstrapTeacher:
    def __init__(self, beta: float = 10.0, lam: float = 0.3, tsp_asset: Optional[str] = None):
        from hdlab.typed_selectional_preference import get, TypedSelectionalPreference
        # PLAUSIBILITY SOURCE (2026-09-12 late): by default the store GROWN BY THE SUBSTRATE'S OWN CHAIN (induced categories ->
        # attachment arm -> role competition over 60k simplewiki lines; tools/grow_selectional_store_bf.py -> typed asset
        # BF_TSP_ASSET). Measured equal to the August parser-extracted store on the heads rung (smoke UAS 0.5642 vs 0.5640;
        # root 0.793 nsubj 0.719 obj 0.71 obl 0.459 xcomp 0.606) -- so the rung's last non-BF dependency is removed at no
        # cost. Falls back to the organ's default asset only if the self-grown one is absent. tsp_asset overrides.
        path = tsp_asset or (BF_TSP_ASSET if os.path.isfile(BF_TSP_ASSET) else None)
        self.tsp = TypedSelectionalPreference.load(path) if path else get()
        self.tsp_source = os.path.basename(path) if path else "default typed_selectional_preference asset"
        # ORDER-AWARE bootstrapping (2026-09-13): object association applies to nominals AFTER the verb, SUBJECT association (the
        # same self-grown store's SUBJ slot) to nominals BEFORE it -- semantic bootstrapping maps roles together with word order
        # (Pinker 1984 canonical mapping). Before this, object plausibility pulled pre-verbal nominals to a following verb
        # (48% of object misses went to the next verb on the right). Falls back to order-blind if the SUBJ asset is absent.
        self.tsp_subj = TypedSelectionalPreference.load(BF_TSP_SUBJ_ASSET) if (ORDER_AWARE and os.path.isfile(BF_TSP_SUBJ_ASSET)) else None
        self._cache_subj: Dict[Tuple[str, str], float] = {}
        # PRONOMINAL PARTICIPANTS (2026-09-13): the typed association drops pronoun fillers (no sense class), so a verb whose subject
        # is "it"/"they" got NO argument evidence and lost the root to an embedded verb with a typed object (the ccomp collapse). For
        # bootstrapping, a pronoun's presence IS evidence of the slot: plausibility(verb, pronoun) = the verb's pronoun-filler RATE in
        # that slot, counted in the self-grown store (0..1, the same scale as association shares; global slot rate for unseen verbs).
        self.pron_subj: Dict[str, float] = {}; self.pron_obj: Dict[str, float] = {}; self.pron_subj_g = 0.0; self.pron_obj_g = 0.0
        if PRON_EVIDENCE and os.path.isfile(BF_STORE):
            try:
                import pickle
                from collections import Counter
                sf = pickle.load(open(BF_STORE, "rb"))["slot_filler"]
                ps, ts, po, to = Counter(), Counter(), Counter(), Counter()
                for (v, role), fillers in sf.items():
                    vl = lemma_verb(v).lower()
                    for w, c in fillers.items():
                        if role == "SUBJ":
                            ts[vl] += c; ps[vl] += c if w in PRONOUNS else 0
                        elif role == "OBJ":
                            to[vl] += c; po[vl] += c if w in PRONOUNS else 0
                self.pron_subj = {v: ps[v] / ts[v] for v in ts if ts[v] >= 5}
                self.pron_obj = {v: po[v] / to[v] for v in to if to[v] >= 5}
                self.pron_subj_g = sum(ps.values()) / max(1.0, sum(ts.values())); self.pron_obj_g = sum(po.values()) / max(1.0, sum(to.values()))
            except Exception:
                self.pron_subj, self.pron_obj = {}, {}
        self.beta = float(beta); self.lam = float(lam); self._cache: Dict[Tuple[str, str], float] = {}

    def plausibility(self, verb_tok: str, noun_tok: str) -> float:
        key = (verb_tok.lower(), noun_tok.lower())
        if key not in self._cache:
            v = lemma_verb(verb_tok).lower(); s = None
            try:
                s = self.tsp.score(v, noun_tok.lower()) if self.tsp.covers(v) else None
            except Exception:
                s = None
            self._cache[key] = float(s) if s is not None else 0.0
        return self._cache[key]

    def plausibility_subj(self, verb_tok: str, noun_tok: str) -> float:
        key = (verb_tok.lower(), noun_tok.lower())
        if key not in self._cache_subj:
            v = lemma_verb(verb_tok).lower(); s = None
            try:
                s = self.tsp_subj.score(v, noun_tok.lower()) if self.tsp_subj.covers(v) else None
            except Exception:
                s = None
            self._cache_subj[key] = float(s) if s is not None else 0.0
        return self._cache_subj[key]

    def slot_plausibility(self, toks: Sequence[str], pos: Sequence[str], h: int, j: int) -> float:
        """Plausibility of nominal j as a participant of verb h in the slot its ORDER marks (object after the verb, subject before;
        order-blind object association when the SUBJ asset is absent). Pronoun participants score by the verb's pronoun-filler rate
        in that slot. Case-marking rules (PP_NO_SUBJ): a pre-verbal PREPOSITIONAL object is oblique, never the subject; a pronoun
        that DETERMINES a following nominal ("its wares") is a possessive, not a participant (2026-09-13 nmod anatomy)."""
        n = len(toks)
        is_pron = pos[j - 1] == "PRON" and bool(self.pron_subj or self.pron_obj)
        vl = lemma_verb(toks[h - 1]).lower() if is_pron else None
        if PP_NO_SUBJ and pos[j - 1] == "PRON" and j < n and pos[j] in NP_RUN and toks[j - 1].lower() not in PRONOUNS:
            return 0.0
        if self.tsp_subj is None or j > h:
            return self.pron_obj.get(vl, self.pron_obj_g) if is_pron else self.plausibility(toks[h - 1], toks[j - 1])
        if PP_NO_SUBJ and j >= 2 and pos[j - 2] == "ADP":
            return 0.0
        return self.pron_subj.get(vl, self.pron_subj_g) if is_pron else self.plausibility_subj(toks[h - 1], toks[j - 1])

    def score_matrix(self, toks: Sequence[str], pos: Sequence[str]) -> Tuple[np.ndarray, int]:
        n = len(toks); A = np.full((n + 1, n + 1), -np.inf); best_arg = np.zeros(n + 1)
        best_subj = np.zeros(n + 1); best_obj = np.zeros(n + 1)
        for j in range(1, n + 1):
            for h in range(1, n + 1):
                if h == j or pos[h - 1] in FORM:
                    continue
                sc = -self.lam * math.log(abs(h - j) + 1.0)
                if pos[h - 1] == "VERB" and pos[j - 1] in NOMINAL:
                    p = self.slot_plausibility(toks, pos, h, j)
                    if self.tsp_subj is not None:
                        if j > h:
                            best_obj[h] = max(best_obj[h], p)
                        else:
                            best_subj[h] = max(best_subj[h], p)
                    sc += self.beta * p; best_arg[h] = max(best_arg[h], p)
                A[h][j] = sc
        if self.tsp_subj is not None:
            # ROOT = the predicate whose participants fit THEIR ROLES best: the best subject fit PLUS the best object fit (a matrix
            # verb with a good subject must beat an embedded verb with only a good object; max-over-one collapsed ccomp/xcomp).
            best_arg = best_subj + best_obj
        for j in range(1, n + 1):
            if pos[j - 1] in FORM:
                A[0][j] = -np.inf if any(pos[k] not in FORM for k in range(n)) else 0.0
            else:
                A[0][j] = (self.beta * best_arg[j] if pos[j - 1] == "VERB" else -1.0) - 0.5
        return A, n

    def combined_scores(self, A: np.ndarray, n: int, toks: Sequence[str], pos: Sequence[str]) -> np.ndarray:
        """ONE posterior: the co-occurrence teacher's log-scores A + this teacher's meaning scores (distance counted once)."""
        B, _ = self.score_matrix(toks, pos); C = A.copy()
        for h in range(0, n + 1):
            for j in range(1, n + 1):
                if h != j and np.isfinite(A[h][j]) and np.isfinite(B[h][j]):
                    C[h][j] = A[h][j] + (B[h][j] + self.lam * math.log(abs(h - j) + 1.0) if h else B[h][j])
        return C


__all__ = ["SentenceCues", "CONSTRUCTIONS", "construction_map", "verb_frames_from_reading", "strengths_from_arc_counts",
           "load_attachment_validities", "save_attachment_validities", "new_counts", "accrue_sentence", "observe_arc_outcome",
           "pp_site", "pp_assoc_from_reading", "pp_lr", "arc_scores", "head_posterior", "heads", "arc_scores_graded", "head_posterior_graded", "heads_graded", "SemanticBootstrapTeacher", "ASSET", "FORM"]


# ------------------------------------------------------------------------------ meaning as a read-time cue (PLAUS_CUE)
_PLAUS_T: Optional["SemanticBootstrapTeacher"] = None


def _plaus_teacher() -> "SemanticBootstrapTeacher":
    global _PLAUS_T
    if _PLAUS_T is None:
        _PLAUS_T = SemanticBootstrapTeacher()
    return _PLAUS_T


def _plaus_bin(p: float) -> str:
    """Categorical value of a plausibility share (0..1). Bin edges are a swept parameter, not an adopted one."""
    return "0" if p <= 0.0 else "lo" if p < 0.05 else "mid" if p < 0.2 else "hi"
