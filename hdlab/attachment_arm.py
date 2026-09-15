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
# THE MAIN-ASSERTION CUES (2026-09-13, solver pri-97).  Until now `SentenceCues.cues(j, h)` returned {} for h == 0:
# the ENTIRE root signal was the 17 per-category ROOT configuration strengths, so every VERB in a sentence had the
# IDENTICAL root activation and 378 of 700 UD-EWT test sentences (54%) had two or more candidates TIED at the best
# root score -- the main assertion was settled by tie-breaking, not by evidence (oracle on the root row alone: root
# 0.721 -> 0.943, UAS 0.6125 -> 0.6574).  Which word carries the main assertion is decided by the SAME cue
# competition as every other attachment (Bates & MacWhinney Competition Model), among the sentence's candidate
# PREDICATES, with these cues: FINITENESS (the assertion is the tensed one -- Wexler 1994 / Rizzi 1993 root
# infinitives; read off the word form by morphological decomposition plus the auxiliary frame), COPULAR PREDICATION
# (the non-verbal predicate carries the assertion, the copula is the tense carrier -- Pustet 2003), SUBORDINATION
# MARKING (a complementizer marks its clause dependent -- Diessel 2004) and MAIN-CLAUSE POSITION / subject support.
# Values are categorical, validities LEARNED from the teacher posterior exactly like every other cue; nothing is
# hand-weighted and nothing reads a tree.  MEASURED (UD-EWT test 700, paired bootstrap; floor = the identical pipeline with the change off, which reproduces the LIVE asset exactly). Root cues + conjunctive finiteness + copular locality + the copular-subject arc cue + the finiteness hold: IN-ORDER (live decode) UAS 0.6163 -> 0.6263, root 0.7214 -> 0.7586 (+0.0371 CI [+0.0171,+0.0571]), copular-subject 0.404 -> 0.466 (+0.0621 CI [+0.0287,+0.1007]), advcl 0.306 -> 0.358, xcomp 0.730 -> 0.766. SEARCH decode with ROOT_PICK=left: UAS 0.6178 -> 0.6257, root 0.7471 -> 0.7929 (+0.0457 CI [+0.0243,+0.0671]), ccomp 0.647 -> 0.733. LIVE CHAIN (the category organ's own tags, whole competition marginalised over its posterior): UAS 0.6030 -> 0.6152 (+0.0122 CI [+0.0051,+0.0194]), root 0.6971 -> 0.7529 (+0.0557 CI [+0.0314,+0.0800]) at +2.7 ms/sentence. Information-free twin (cue values permuted, 3 seeds) LOSES under both decodes.
ROOT_CUES = ("rpred", "rsub", "rpos")
# REFUTED AS BUILT (2026-09-13, recorded): reading the cue evidence as a COMPETITION for the one root slot -- the
# contribution centred to zero mean over the live candidates, on the argument that the root slot has capacity one
# (MacWhinney 1987) -- is WORSE than the plain additive form under BOTH decodes (UD-EWT test 700, train 1.5k:
# in-order root +0.021 centred vs +0.034 flat; search root -0.049 vs -0.030).  Reason, measured: 120 of 177 search
# root misses have the gold root OUTSIDE the unconstrained MAP root set at all, so what the search decode needs is
# the ABSOLUTE root-vs-attach margin that centring removes, not a better ranking.  Kept selectable, default OFF.
ROOT_CUE_CENTER = os.environ.get("HDLAB_ARM_ROOT_CENTER", "0") == "1"
# ROUND-2 SWITCHES, each measured separately (numbers in notes/problems/<slug>/SOLVED.md 6e/6f):
#  CONJ_RPRED  the bare "ed"/"base" finiteness values CONFLATE opposite predication statuses (148 finite pasts vs
#              65 bare participles; 146 finite presents vs 46 infinitives, UD VerbForm as the instrument) -- split
#              them by rank x whether a LATER assertion candidate exists. Best single lever on root (0.7571).
#  COP_LOCALITY  the copular detector's AUX scan stopped only at PUNCT, so "we ARE capable of PROTECTING it" bound
#              the copula to a verb behind a PREPOSITION and the copular reading never fired. Root cause of the
#              dominant copular-subject miss. Stop at ADP / SCONJ / PART-`to` / CCONJ too.
#  CSUB        the copular subject is a competition on the nsubj ARC, not the root arc: the predicate claims its
#              subject against the verbs inside its own predicate phrase. cop-subj 0.404 -> 0.466 / 0.528 -> 0.627.
#  HOLD_FINITENESS  the hold/prediction did not condition on finiteness, so a to-infinitive and a tensed verb
#              predicted a governor to the right with identical strength (Levy 2008). NULL alone, +0.0018 UAS with
#              the cues -- best UAS of the session, 0.6263.
CONJ_RPRED = os.environ.get("HDLAB_ARM_CONJ_RPRED", "1") != "0"
COP_LOCALITY = os.environ.get("HDLAB_ARM_COP_LOCALITY", "1") != "0"
CSUB_CUE = os.environ.get("HDLAB_ARM_CSUB", "1") != "0"
HOLD_FINITENESS = os.environ.get("HDLAB_ARM_HOLD_FINITENESS", "1") != "0"
# ----------------------------------------------------------------- CLAUSE MEMBERSHIP + CONSTITUENCY (solver pri-105)
# 2026-09-13.  286 of the 1,205 core arguments on UD-EWT test 700 were attached outside their clause (a verb in
# another clause, or the root) or absorbed into a neighbouring noun phrase.  Two brain computations the arm had no
# cue for -- both added as CUES with LEARNED validities (same counts, same log-odds contrast, same observe path):
#  CLAUSE MEMBERSHIP -- an argument is integrated inside its OWN clause: the first-stage parser packages roughly a
#    clause (Frazier & Fodor 1978), integration cost is paid across intervening referents and clause boundaries
#    (Gibson DLT; reading time rises AT a clause boundary, where the integration happens), a subordinator or
#    complementiser OPENS a clause (Diessel 2004 -- the child's acquisition cue for clause dependency), infinitival
#    `to` opens a non-finite one, and every predicate projects one.  The arm's only distance cues were log-distance
#    and PUNCTUATION marks spanned; neither sees a predicate or a complementiser standing between the noun and the
#    verb competing for it.  `clause` value = (predicates strictly between h and j, capped at 2) + "s" when a clause
#    opener stands between them; the validity is learned per configuration, so a VERB may head a VERB across a
#    boundary (that IS the subordinate clause arc) while a VERB may not head a NOUN across one.
#  CONSTITUENCY -- a noun phrase is a UNIT whose head is its rightmost noun (Right-hand Head Rule, Williams 1981) and
#    whose onset is its determiner (DP hypothesis; and as an acquisition fact the determiner is the infant's
#    phrase-onset marker -- Shi & Melancon 2010, Bernal et al. 2010, Christophe et al. 2008).  A determiner arriving
#    when the current phrase already has its noun opens a SECOND phrase ("gave the man | a book"); a determiner
#    sequence does not ("all the people").  `npb` value = "in" / "cross" for a nominal-domain pair.
#  NP_SPLIT applies the SAME computation to the phrase-internal CONSTRUCTIONS: `npmod_arcs` and the preposition frame
#    in `function_word_arcs` attached every element of a MAXIMAL DET/ADJ/NUM/NOUN/PROPN run to the run's last noun,
#    which is what proposed the absorbing arc in the first place (and, being an `fw` arc, collected the +5 convention
#    bonus).  Now the Right-hand Head Rule applies inside one PHRASE.
CLAUSE_CUE = os.environ.get("HDLAB_ARM_CLAUSE_CUE", "1") != "0"
NPB_CUE = os.environ.get("HDLAB_ARM_NPB_CUE", "1") != "0"
NP_SPLIT = os.environ.get("HDLAB_ARM_NP_SPLIT", "1") != "0"
CLAUSE_WRAP_OPENER = os.environ.get("HDLAB_ARM_CLAUSE_WRAP_OPENER", "1") != "0"   # the in-order decode wraps up at a clause opener too
CLAUSE_MAXV = 2                     # intervening predicates counted up to this (a swept operating point)
POSS_PRON = frozenset({"my", "your", "his", "her", "its", "their", "our", "whose"})
# ------------------------------------------- THE COPULAR-SUBJECT CUE, GRADED AND LEARNED (pri 117)
CSUBG_BINS = (0.25, 0.60, 0.85)        # occupancy bins (a swept operating point, never adopted)
CSUB_COVERAGE = os.environ.get("HDLAB_ARM_CSUB_COVERAGE", "1") != "0"
CSUBG_CUE = os.environ.get("HDLAB_ARM_CSUBG", "1") != "0"
CSUB_REANALYSIS = os.environ.get("HDLAB_ARM_CSUB_REANALYSIS", "1") != "0"
CSUB_REANALYSIS_LEFT = os.environ.get("HDLAB_ARM_CSUB_REANALYSIS_LEFT", "0") == "1"
# THE WIDE FORM (pri 117, measured): the in-order beam commits the subject to whatever is open when it arrives, and
# the committed head is NOT always a later verb -- measured on UD-EWT test 700 it is the tense carrier, a preceding
# matrix verb, a noun inside the subject's own phrase or the root.  The SAME whole-sentence scores decoded by the
# search put the non-verbal subject at 0.7041 against the beam's 0.6509, so the arc the competition prefers is
# already there and the beam cannot reach it; the brain's repair is REANALYSIS when the disambiguating word arrives
# (Frazier & Rayner 1982), not a wider beam.  The revision still carries NO parameter: it takes the arc the organ's
# own learned activations prefer, and only for a subject whose clause's predicate slot has been identified.
CSUB_REANALYSIS_ANY = os.environ.get("HDLAB_ARM_CSUB_REANALYSIS_ANY", "1") != "0"
# THE TENSE CARRIER'S PREDICATE, WHATEVER ITS CATEGORY (pri 117).  pri 110's three-way discharge says a carrier's
# slot goes to (1) a VERBAL HOST in its verb group, (2) a NON-VERBAL complement, or (3) itself.  The copular-subject
# cue fired for branch (2) only -- so "It 's just DISAPPOINTING" and "the people will be DEAD" lost the pair
# whenever the category organ read the predicate as a VERB (participial predicates: 14 of the 60 residual misses
# were exactly this).  The ARC claim is the same under both branches -- the subject attaches to the token holding
# the predicate slot -- so the cue fires on the host too, and the OCCUPANCY (P(VERB) for a host, (1-host)*copular
# for a complement) is the value whose validity the competition learns SEPARATELY per configuration.
CSUB_VERBAL_HOST = os.environ.get("HDLAB_ARM_CSUB_VERBAL_HOST", "1") != "0"
# THE TENSE CARRIER IS NOT THE PREDICATE when it has one (Pustet 2003): the copula competes for the subject and
# wins it 3 times on the 169 ("that IS how i want ..."), so the carrier's own arc takes the competing value.
CSUB_SUPPRESS_COP = os.environ.get("HDLAB_ARM_CSUB_SUPPRESS_COP", "1") != "0"
# THE TWO SUBJECT-SIDE CORRECTIONS the board's two lost patient items paid for, each behind its own switch
# because they do NOT cost the same (measured, pri 117 phase 7): crossing the hyphen of a compound name is free,
# and refusing a nominal that sits inside a CLAUSAL subject is NOT -- it also refuses the legitimate pre-copular
# nominal of an unmarked complement clause ("I think the sky is blue"), which is why it ships OFF.
CSUB_SUBJ_HYPHEN = os.environ.get("HDLAB_ARM_CSUB_SUBJ_HYPHEN", "1") != "0"
CSUB_SUBJ_NO_CLAUSAL = os.environ.get("HDLAB_ARM_CSUB_SUBJ_NO_CLAUSAL", "0") == "1"


CUES = (("locality", "frame", "form", "boundary", "agree", "constr", "pp", "ppobj") + (("plaus",) if PLAUS_CUE else ())
        + ROOT_CUES + (("csub",) if CSUB_CUE else ()) + (("csubg",) if CSUBG_CUE else ())
        + (("clause",) if CLAUSE_CUE else ()) + (("npb",) if NPB_CUE else ()))   # catpair / root = configuration
# "ppobj" (2026-09-13, solver pri-94): the THEMATIC channel of the PP cue -- what kind of thing the prepositional
# phrase is about, given the type of the candidate that would license it (Taraban & McClelland 1988; Ratnaparkhi's
# fourth element).  See the PP ATTACHMENT block below.
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


def np_starts(toks: Sequence[str], pos: Sequence[str]) -> "np.ndarray":
    """Per 1-based token: does it OPEN a new nominal phrase?  A determiner (or possessive pronoun) that arrives when
    the current phrase already has its noun starts a second phrase; a determiner sequence does not."""
    n = len(pos); lows = [t.lower() for t in toks]
    out = np.zeros(n + 1, dtype=np.int64); seen_head = False
    for i in range(1, n + 1):
        p = pos[i - 1]; w = lows[i - 1]
        if p not in NP_RUN:
            seen_head = False
            continue
        if p == "DET" or (p == "PRON" and w in POSS_PRON):
            if seen_head:
                out[i] = 1; seen_head = False
        elif p in ("NOUN", "PROPN"):
            seen_head = True
    return out


def split_runs(pos: Sequence[str], starts) -> List[Tuple[int, int]]:
    """Contiguous NP_RUN spans split at every phrase onset: inclusive 1-based (a, b) spans."""
    n = len(pos); out = []; i = 1
    while i <= n:
        if pos[i - 1] not in NP_RUN:
            i += 1; continue
        a = i; j = i + 1
        while j <= n and pos[j - 1] in NP_RUN and not starts[j]:
            j += 1
        out.append((a, j - 1)); i = j
    return out


def phrase_head(pos: Sequence[str], a: int, b: int) -> Optional[int]:
    """The Right-hand Head Rule INSIDE one phrase: the last NOUN/PROPN, else the last ADJ/NUM."""
    nouns = [k for k in range(a, b + 1) if pos[k - 1] in ("NOUN", "PROPN")]
    if nouns:
        return nouns[-1]
    adjs = [k for k in range(a, b + 1) if pos[k - 1] in ("ADJ", "NUM")]
    return adjs[-1] if adjs else None


NPB_VALUES = ("na", "in", "cross")


def npb_matrix(toks: Sequence[str], pos: Sequence[str]) -> "np.ndarray":
    """Value id per (head row 0..n, dependent col 1..n): 0 = na (not a nominal-domain pair), 1 = in (same phrase),
    2 = cross (a phrase onset stands between them, so they belong to different phrases)."""
    n = len(pos); starts = np_starts(toks, pos)
    cs = np.concatenate([[0], np.cumsum(starts[1:])])
    dom = np.array([False] + [p in NP_RUN for p in pos])
    H = np.arange(0, n + 1)[:, None]; J = np.arange(1, n + 1)[None, :]
    lo = np.minimum(H, J); hi = np.maximum(H, J)
    v = np.where((cs[hi] - cs[lo]) > 0, 2, 1)
    both = np.concatenate([np.zeros((1, n), dtype=bool), (dom[1:, None] & dom[None, 1:])], axis=0)
    return np.where(both, v, 0)


def predicate_flags(toks: Sequence[str], pos: Sequence[str]):
    """Per 1-based token: (is a PREDICATE, is a CLAUSE OPENER).  Predicate = a VERB or the arm's own copular
    predicate; opener = a subordinator, a wh relativizer/complementiser, or infinitival `to`."""
    n = len(pos); lows = [t.lower() for t in toks]
    pred = np.zeros(n + 1, dtype=np.int64); opn = np.zeros(n + 1, dtype=np.int64)
    cop = cop_predicates(toks, pos)
    for i in range(1, n + 1):
        p = pos[i - 1]; w = lows[i - 1]
        if p == "VERB" or i in cop:
            pred[i] = 1
        if p == "SCONJ":
            opn[i] = 1
        elif p in ("PRON", "DET", "ADV") and w in WH_FORMS:
            opn[i] = 1
        elif p == "PART" and w == "to":
            opn[i] = 1
    return pred, opn


def clause_matrices(toks: Sequence[str], pos: Sequence[str]):
    """(nv, sb) over (head row 0..n, dependent col 1..n): predicates strictly between h and j (capped) and whether a
    clause opener stands strictly between them.  The ROOT arc (row 0) crosses nothing."""
    n = len(pos); pred, opn = predicate_flags(toks, pos)
    cp = np.concatenate([[0], np.cumsum(pred[1:])]); co = np.concatenate([[0], np.cumsum(opn[1:])])
    H = np.arange(0, n + 1)[:, None]; J = np.arange(1, n + 1)[None, :]
    lo = np.minimum(H, J); hi = np.maximum(H, J)
    nv = cp[np.maximum(hi - 1, 0)] - cp[lo]; sb = co[np.maximum(hi - 1, 0)] - co[lo]
    nv[0, :] = 0; sb[0, :] = 0
    return np.minimum(nv, CLAUSE_MAXV), (sb > 0).astype(np.int64)


def clause_value(nv: int, sb: int) -> str:
    return ("%d" % nv) + ("s" if sb else "")


CLAUSE_VALUES = tuple(clause_value(v, s) for v in range(CLAUSE_MAXV + 1) for s in (0, 1))


def npmod_arcs(toks: Sequence[str], pos: Sequence[str]) -> List[Tuple[int, int]]:
    """NP-internal modifier construction: within one PHRASE every element attaches to the phrase's head noun (the
    Right-hand Head Rule).  The phrase ends at the next determiner that opens one (pri-105): the maximal-run version
    hung an argument noun under the NEXT phrase's noun ("gave the man a book" -> man under book), which is the
    dominant constituency error class.  HDLAB_ARM_NP_SPLIT=0 restores the maximal run."""
    if not NP_SPLIT:
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
    out = []
    for (a, b) in split_runs(pos, np_starts(toks, pos)):
        h = phrase_head(pos, a, b)
        if h is None or pos[h - 1] not in ("NOUN", "PROPN"):
            continue
        for k in range(a, b + 1):
            if k != h:
                out.append((h, k))
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
    starts = np_starts(toks, pos) if NP_SPLIT else None

    def np_head_after(i):                   # head noun of the nominal PHRASE starting at i (0-based) or None
        j = i + 1                           # the phrase ends at the next determiner that OPENS one (pri-105)
        while j < n and pos[j] in NP_RUN and not (NP_SPLIT and starts[j + 1]):
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


# ---------------------------------------------------------------------------------------- PP ATTACHMENT (obl/nmod)
# A prepositional phrase is a CASE-MARKED nominal looking for a host, and the reader picks the host by the SAME cue
# competition as every other attachment (Bates & MacWhinney Competition Model; MacDonald, Pearlmutter & Seidenberg
# 1994) over candidates RETRIEVED from working memory under decay (Lewis & Vasishth 2005), with the host-preposition
# LEXICAL ASSOCIATION as the discriminating cue (Hindle & Rooth 1993), learned from the cases experience leaves
# UNAMBIGUOUS and then re-apportioned over the ambiguous ones (Hindle & Rooth's reallocation; Ratnaparkhi 1998 mines
# exactly this from raw text: 81.9 vs a 70.4 baseline, no treebank).
#
# WHY THIS REPLACES `pp_site` (measured on UD-EWT test 700 before the change, solver pri-94):
#   `pp_site` offered exactly TWO candidates (nearest preceding VERB, nearest preceding NOUN) and only for a NOUN/PROPN
#   object sitting directly after DET/ADJ/NUM.  It fired on 253/477 gold obl and 195/534 gold nmod, and of those the
#   gold head was NEITHER offered candidate for 63 obl + 46 nmod -- at most 339 of the 1011 obl+nmod tokens (33.5%)
#   were decidable by the cue at all.  Losses: a PRON object (109 nmod + 44 obl) or a NUM object (55); a compound or
#   possessive inside the NP stopping the leftward scan ("of Google 's new toolbar", "on your hands": 98 obl + 77
#   nmod); a predicate ADJECTIVE host ("capable OF ...", 24 obl); a noun host that is not the nearest one (23 nmod).
#   `pp_sites` below is driven by the PREPOSITION (the case marker), takes the object as the head of the nominal run
#   after it (the arm's own NP-run convention) and retrieves EVERY open host to its left up to PP_KCAP: 333/477 obl
#   and 266/534 gold nmod detected, gold host inside the candidate set for 313 + 243 = 55.0% of the population.
#   PP_KCAP is a SWEPT operating point (4/6/8/12 -> 546/556/556/556 retrievable; 6 is the knee).
PP_NP_RUN = frozenset({"DET", "ADJ", "NUM", "NOUN", "PROPN", "PRON", "PART", "ADV"})
PP_NOM_HOST = frozenset({"NOUN", "PROPN", "PRON", "NUM"})
PP_PRED_HOST = frozenset({"VERB", "ADJ"})
PP_SENT_END = frozenset({".", "!", "?", ";"})
PP_KCAP = int(os.environ.get("HDLAB_ARM_PP_KCAP", "6"))          # capacity-limited retrieval; swept, never adopted
PP_M1, PP_M2 = 5.0, 20.0                                          # shrinkage: lemma -> class -> the preposition marginal
PP_M3, PP_M4 = 20.0, 50.0                                         # shrinkage of the thematic (object-class) channel
PP_Z_EDGES = (1.0, 0.3, -0.3, -1.0)
PP_Z_NAMES = ("w2", "w1", "0", "l1", "l2")
# READOUT FORM, measured not assumed: "share" = log[P(p|h) / mean_h' P(p|h')] -- divisive normalisation over the
# retrieved population (Carandini & Heeger 2012), symmetric in the host types.  "max" (this candidate against its
# STRONGEST rival, the literal two-candidate Hindle-Rooth contrast) is REFUTED AS BUILT and kept selectable: the
# strongest rival of a noun host is almost always a verb, so inside the NOUN>NOUN configuration nearly every value is
# a losing bin, the losing bin IS that configuration's baseline, its learned contrast collapses to ~0, and the cue
# degenerates into "prefer a verb" -- a type prior the CONFIGURATION already owns.  Measured seesaw under "max"
# (cap 1200, test 250): obl 0.443 -> 0.502 but nmod 0.454 -> 0.393 on the search decode.
PP_ZFORM = os.environ.get("HDLAB_ARM_PP_ZFORM", "share")
# PHRASE-LEVEL CASE MARKING -- REFUTED AS BUILT, DEFAULT OFF, kept selectable with its numbers.
# The read-time meaning cue and the semantic-bootstrapping teacher ask "is this nominal case-marked?" with
# `pos[j-2] == "ADP"` -- the preposition IMMEDIATELY before the noun.  A case marker marks the PHRASE (Pinker 1984)
# and any NP with more than one modifier breaks adjacency: MEASURED (UD-EWT test 700), 684 nominal run heads are
# case-marked by the phrase rule and only 396 by the adjacency rule -- 436 missed (63.7%), 199 gold obl and 144 gold
# nmod, each handed to the meaning cue as a candidate SUBJECT or OBJECT of a nearby verb.  Widening the rule is
# nevertheless WRONG, in both forms tried (train cap 1500, UD-EWT test 700, in-order decode, paired bootstrap):
#   "zero" (a case-marked nominal is not a core participant, so the cue is silent): obl 0.449 -> 0.380 alone, and
#     0.449 -> 0.199 together with the PP cue.  MECHANISM, read off the learned table: the over-broad adjacency guard
#     was the ONLY thing teaching the arm that a verb takes an oblique argument at all, so the acquisition teacher
#     stops putting mass on verb -> PP-object arcs and the organ learns V:* thematic validities of -1.5 to -1.8
#     (from about +0.5) -- it concludes that a verb never hosts a case-marked nominal.
#   "slot" (still a participant, but in a separate OBLIQUE slot value): obl +0.0335, nmod +0.0243, and WORSE than
#     leaving the guard alone (obl 0.482 vs 0.526).  87% of gold obl is prepositional and its host IS a verb, so the
#     blanket pull is NET CORRECT; what separates obl from nmod is the ASSOCIATION, not the guard.
PP_CASE_RULE = os.environ.get("HDLAB_ARM_PP_CASE_RULE", "0") != "0"


# ------------------------------------------------------------------ the TWO-SIDED acquisition teacher (pri 94 ph 7)
# `SemanticBootstrapTeacher.score_matrix` adds its meaning term `beta * slot_plausibility(h, j)` on exactly one kind
# of arc: a VERB host with a NOMINAL dependent.  A noun host receives no meaning support at all, ever.  While the arm
# learns, every case-marked nominal therefore has a verb voting for it with beta and a noun voting with nothing --
# and MEASURED (pri 94 phase 7, UD-EWT test 700), WHERE THAT BUDGET IS SPENT IS THE obl/nmod SEESAW: spend more on
# verbs and obl goes 0.541 -> 0.679 while nmod goes 0.489 -> 0.221; spend it on nouns and obl -> 0.210, nmod -> 0.566.
# The brain has no such asymmetry: a relational noun selects its complement as a verb selects its argument ("the
# picture OF the girl", "the edge OF the table"; Barker 1995 possessive descriptions; Loebner's relational nouns), and
# Hindle & Rooth 1993's contrast log[P(p|VERB)/P(p|NOUN)] is symmetric by construction.  Two additions, both counts:
#   (1) OBLIQUE SLOT.  A case-marked nominal hosted by a verb is scored in the OBLIQUE slot, by that predicate's own
#       oblique expectation with that preposition, read off the substrate's OWN grown `obl:<prep>` store (Pinker 1984
#       semantic bootstrapping with three slots instead of two).  When the store abstains the teacher's own value
#       stands, so the verb's pull is RE-SCORED and never removed -- zeroing it collapses obl 0.449 -> 0.199.
#   (2) NOMINAL HOST SLOT.  Every retrieved nominal host of a case-marked nominal gets `BETA_NOM * P_host`, where
#       P_host = P(p | this noun) / [P(p | this noun) + P(p | this noun's class)] -- 0.5 when this noun is no more
#       attracted to the preposition than nouns of its kind.
# MEASURED TOGETHER (cap 1500, test 700, paired bootstrap over sentences, in-order): retrieved-nmod +0.0752
# CI [+0.0308,+0.1231] over the floor and +0.0564 CI [+0.0115,+0.1020] over the arm without them; UAS +0.0121*,
# obl +0.0818*, nmod +0.1067*; nothing CI-separated down; and the downstream role competition returns to the floor
# (0.5769 vs 0.5760, against 0.5617 without them).  Beats a twin with BOTH stores scrambled on UAS (+0.0082*), obl
# (+0.1405*) and retrieved obl (+0.1952*).  BETA_NOM swept (2 / 6 / 14; 14 overshoots, obl 0.264), never adopted.
BETA_NOM = float(os.environ.get("HDLAB_SBT_BETA_NOM", "6.0"))       # swept operating point, never adopted
OBL_TEACH = os.environ.get("HDLAB_SBT_OBL_TEACH", "1") != "0"
OBL_SLOT_M1 = float(os.environ.get("HDLAB_SBT_OBL_M1", "5.0"))
OBL_SLOT_M2 = float(os.environ.get("HDLAB_SBT_OBL_M2", "20.0"))
_OBL_SLOTS = None


def obl_slot_store(path=None):
    '''P(class of the oblique filler | predicate lemma, preposition) as COUNTS, from the substrate's OWN grown slot
    store (tools/grow_selectional_store_bf.py: its own reading-induced categories -> this arm -> the role
    competition, 60k Simple-Wiki lines, no external parser): 6,947 (predicate, preposition) slots, 20,179
    filler-class cells, 39,222 observations.  Typed with the same WordNet supersense table the typed selectional
    organ reads.  Plastic: the counts are the store's own and grow with more reading.'''
    global _OBL_SLOTS
    if _OBL_SLOTS is not None and path is None:
        return _OBL_SLOTS
    from collections import defaultdict as _dd
    c = _dd(float); d = _dd(float); cg = _dd(float); dg = _dd(float); cw = _dd(float); tot = 0.0
    pth = path or BF_STORE
    if os.path.isfile(pth):
        import pickle
        from hdlab.typed_selectional_preference import noun_supersense
        sf = pickle.load(open(pth, "rb"))["slot_filler"]
        for (v, role), fillers in sf.items():
            if not role.startswith("obl:"):
                continue
            prep = role.split(":", 1)[1]
            if not prep or prep == "_":
                continue
            vl = lemma_verb(v).lower()
            for w, cnt in fillers.items():
                cls = noun_supersense(w) or "unk"
                cnt = float(cnt)
                c[vl + "|" + prep + "|" + cls] += cnt; d[vl + "|" + prep] += cnt
                cg[prep + "|" + cls] += cnt; dg[prep] += cnt; cw[cls] += cnt; tot += cnt
    out = {"c": dict(c), "d": dict(d), "cg": dict(cg), "dg": dict(dg), "cw": dict(cw), "tot": tot,
           "computation": "P(objclass|verb,prep) = (c + m1*P(objclass|prep))/(d + m1); oblique-slot plausibility = "
                          "P(objclass|verb,prep) / [P(objclass|verb,prep) + P(objclass|prep)]"}
    if path is None:
        _OBL_SLOTS = out
    return out


def obl_slot_plausibility(S, verb, prep, cls):
    '''The oblique slot on the SAME 0..1 scale the object slot uses; 0.5 = this predicate expects this kind of
    oblique filler no more than predicates in general do.  None = unseen predicate in this slot, and the caller must
    then leave the teacher's own value alone.'''
    d = S["d"].get(verb + "|" + prep, 0.0)
    if d <= 0.0:
        return None
    pg = (S["cw"].get(cls, 0.0) + 0.5) / (S["tot"] + 1.0)
    g = (S["cg"].get(prep + "|" + cls, 0.0) + OBL_SLOT_M2 * pg) / (S["dg"].get(prep, 0.0) + OBL_SLOT_M2)
    pl = (S["c"].get(verb + "|" + prep + "|" + cls, 0.0) + OBL_SLOT_M1 * g) / (d + OBL_SLOT_M1)
    return pl / (pl + g) if (pl + g) > 0 else 0.5


_PP_PREP_CACHE = {}


def pp_case_preps(toks, pos):
    '''{object index -> the preposition that marks it}, memoised; a pure function of (tokens, categories).'''
    key = (tuple(toks), tuple(pos))
    v = _PP_PREP_CACHE.get(key)
    if v is None:
        v = {obj: toks[prep - 1].lower() for prep, obj, _ in pp_sites(toks, pos)}
        if len(_PP_PREP_CACHE) > 20000:
            _PP_PREP_CACHE.clear()
        _PP_PREP_CACHE[key] = v
    return v



def pp_run_head(pos: Sequence[str], i: int) -> Optional[int]:
    """1-based head of the nominal run starting at 1-based i: its last NOUN/PROPN, else its last PRON/NUM, else None."""
    n = len(pos); j = i
    while j <= n and pos[j - 1] in PP_NP_RUN:
        j += 1
    nouns = [q for q in range(i, j) if pos[q - 1] in ("NOUN", "PROPN")]
    if nouns:
        return nouns[-1]
    other = [q for q in range(i, j) if pos[q - 1] in ("PRON", "NUM")]
    return other[-1] if other else None


def _pp_is_nominal_host(pos: Sequence[str], q: int) -> bool:
    """A nominal candidate host is the HEAD of its own run (a compound's modifier is not offered separately)."""
    if pos[q - 1] not in PP_NOM_HOST:
        return False
    return not (q < len(pos) and pos[q] in ("NOUN", "PROPN"))


def pp_host_type(p: str) -> str:
    return "V" if p == "VERB" else "A" if p == "ADJ" else "N"


def pp_sites(toks: Sequence[str], pos: Sequence[str], k_cap: Optional[int] = None):
    """Every case-marked nominal: (prep_idx, object_head_idx, [candidate host indices, nearest first]), 1-based.
    Category-structural only; no gold, no treebank, no external tool."""
    k_cap = PP_KCAP if k_cap is None else k_cap
    n = len(pos); out = []
    for k in range(1, n + 1):
        if pos[k - 1] != "ADP" or k == n or pos[k] == "ADP" or pos[k] not in PP_NP_RUN:
            continue                                   # "because of": the inner preposition carries the case
        obj = pp_run_head(pos, k + 1)
        if obj is None or obj <= k:
            continue
        cands = []
        for q in range(k - 1, 0, -1):
            p = pos[q - 1]
            if p == "PUNCT" and toks[q - 1] in PP_SENT_END:
                break
            if p in PP_PRED_HOST or _pp_is_nominal_host(pos, q):
                cands.append(q)
                if len(cands) >= k_cap:
                    break
        if cands:
            out.append((k, obj, cands))
    return out


_PP_CASE_CACHE: Dict[Tuple, set] = {}


def pp_case_marked(toks: Sequence[str], pos: Sequence[str], k_cap: Optional[int] = None) -> set:
    """The 1-based nominals a preposition has case-marked (the PHRASE rule). Memoised: `slot_plausibility` asks once
    per (verb, nominal) pair, so an unmemoised call is O(n^2) detector passes per sentence. Pure memo -- the set is a
    function of (tokens, categories, k_cap) and no number changes."""
    key = (tuple(toks), tuple(pos), k_cap)
    v = _PP_CASE_CACHE.get(key)
    if v is None:
        v = {obj for _, obj, _ in pp_sites(toks, pos, k_cap)}
        if len(_PP_CASE_CACHE) > 20000:
            _PP_CASE_CACHE.clear()
        _PP_CASE_CACHE[key] = v
    return v


def pp_mining_frame(toks: Sequence[str], pos: Sequence[str], k: int):
    """Hindle & Rooth's two-slot frame at preposition k: the nearest PREDICATE host (verb / predicate adjective) and
    the nearest NOMINAL host to its left. Exactly one present = an UNAMBIGUOUS case, the clean learning signal."""
    pred = nom = None
    for q in range(k - 1, 0, -1):
        p = pos[q - 1]
        if p == "PUNCT" and toks[q - 1] in PP_SENT_END:
            break
        if pred is None and p in PP_PRED_HOST:
            pred = q
        if nom is None and _pp_is_nominal_host(pos, q):
            nom = q
        if pred is not None and nom is not None:
            break
    return pred, nom


def pp_host_key(toks: Sequence[str], pos: Sequence[str], q: int) -> str:
    """<type>|<lemma>: verbs through the arm's verb lemmatiser, nouns through the morphology organ (glass-box)."""
    t = pp_host_type(pos[q - 1]); w = toks[q - 1].lower()
    if t == "V":
        return "V|" + lemma_verb(toks[q - 1]).lower()
    if t == "N":
        from hdlab import morphology as _m
        return "N|" + (_m.morphy(w, "n") or w)
    return "A|" + w


def pp_host_class(toks: Sequence[str], pos: Sequence[str], q: int) -> str:
    """The BACKOFF class: verbs/adjectives to their category, nouns to their WordNet supersense (the same offline
    foundation table the typed selectional-preference organ reads -- Resnik-style type generalisation)."""
    t = pp_host_type(pos[q - 1])
    if t != "N":
        return t
    from hdlab.typed_selectional_preference import noun_supersense
    return "N:" + (noun_supersense(toks[q - 1]) or "unk")


def pp_obj_class(toks: Sequence[str], pos: Sequence[str], q: int) -> str:
    """The TYPE of the prepositional object -- what the phrase is ABOUT (Taraban & McClelland 1988 thematic
    expectation; Ratnaparkhi 1998's fourth element)."""
    if pos[q - 1] == "NUM":
        return "num"
    from hdlab.typed_selectional_preference import noun_supersense
    return noun_supersense(toks[q - 1]) or ("pron" if pos[q - 1] == "PRON" else "unk")


def pp_new_assoc() -> Dict[str, object]:
    return {"c": {}, "d": {}, "cc": {}, "dc": {}, "cp": {}, "tot": 0.0,
            "o": {}, "od": {}, "oc": {}, "ocd": {}, "og": {}, "otot": 0.0}


def pp_observe(A: Dict[str, object], hkey: str, hcls: str, prep: str, w: float = 1.0,
               objclass: Optional[str] = None) -> None:
    """PLASTICITY: one comprehension outcome -- host `hkey` was understood to license the phrase headed by `prep`
    (and, when given, a phrase ABOUT `objclass`). Counts only; the probability is a pure function of them."""
    def add(d, k, v):
        d[k] = d.get(k, 0.0) + v
    add(A["c"], hkey + "|" + prep, w); add(A["d"], hkey, w)
    add(A["cc"], hcls + "|" + prep, w); add(A["dc"], hcls, w)
    add(A["cp"], prep, w); A["tot"] = A.get("tot", 0.0) + w
    if objclass is not None:
        t = hkey.split("|", 1)[0]
        add(A["o"], t + "|" + prep + "|" + objclass, w); add(A["od"], t + "|" + prep, w)
        add(A["oc"], t + "|" + objclass, w); add(A["ocd"], t, w)
        add(A["og"], objclass, w); A["otot"] = A.get("otot", 0.0) + w


def pp_p_given(A: Dict[str, object], hkey: str, hcls: str, prep: str) -> float:
    """P(preposition | host), shrunk lemma -> class -> the preposition's own marginal."""
    pp = (A["cp"].get(prep, 0.0) + 0.5) / (A.get("tot", 0.0) + 1.0)
    pc = (A["cc"].get(hcls + "|" + prep, 0.0) + PP_M2 * pp) / (A["dc"].get(hcls, 0.0) + PP_M2)
    return (A["c"].get(hkey + "|" + prep, 0.0) + PP_M1 * pc) / (A["d"].get(hkey, 0.0) + PP_M1)


def pp_p_obj(A: Dict[str, object], htype: str, prep: str, objclass: str) -> float:
    """P(class of the prepositional object | host type, preposition) -- the typed thematic expectation."""
    pg = (A["og"].get(objclass, 0.0) + 0.5) / (A.get("otot", 0.0) + 1.0)
    pt = (A["oc"].get(htype + "|" + objclass, 0.0) + PP_M4 * pg) / (A["ocd"].get(htype, 0.0) + PP_M4)
    return (A["o"].get(htype + "|" + prep + "|" + objclass, 0.0) + PP_M3 * pt) / (A["od"].get(htype + "|" + prep, 0.0) + PP_M3)


def pp_assoc_v2_from_reading(sentences_tp, rounds: int = 2, k_cap: Optional[int] = None) -> Dict[str, object]:
    """TREEBANK-FREE mining from (tokens, categories): the UNAMBIGUOUS sites (only one of the predicate / nominal slot
    present) give hard credit; the ambiguous ones are then apportioned by the CURRENT estimate and re-estimated for
    `rounds` rounds (Hindle & Rooth 1993). `rounds = 0` gives the unambiguous-only seed."""
    inst = []
    for toks, pos in sentences_tp:
        n = len(toks)
        for k in range(1, n + 1):
            if pos[k - 1] != "ADP" or k == n or pos[k] == "ADP" or pos[k] not in PP_NP_RUN:
                continue
            obj = pp_run_head(pos, k + 1)
            if obj is None:
                continue
            pred, nom = pp_mining_frame(toks, pos, k)
            if pred is None and nom is None:
                continue
            rec = {"p": toks[k - 1].lower(), "o": pp_obj_class(toks, pos, obj)}
            if pred is not None:
                rec["pred"] = (pp_host_key(toks, pos, pred), pp_host_class(toks, pos, pred))
            if nom is not None:
                rec["nom"] = (pp_host_key(toks, pos, nom), pp_host_class(toks, pos, nom))
            inst.append(rec)
    unamb = [r for r in inst if ("pred" in r) != ("nom" in r)]
    amb = [r for r in inst if ("pred" in r) and ("nom" in r)]
    A = pp_new_assoc()
    for r in unamb:
        h = r.get("pred") or r["nom"]
        pp_observe(A, h[0], h[1], r["p"], 1.0, r.get("o"))
    for _ in range(max(0, rounds)):
        B = pp_new_assoc()
        for r in unamb:
            h = r.get("pred") or r["nom"]
            pp_observe(B, h[0], h[1], r["p"], 1.0, r.get("o"))
        for r in amb:
            hp, hn = r["pred"], r["nom"]; p = r["p"]; oc = r.get("o") or "unk"
            a = pp_p_given(A, hp[0], hp[1], p) * pp_p_obj(A, hp[0].split("|", 1)[0], p, oc)
            b = pp_p_given(A, hn[0], hn[1], p) * pp_p_obj(A, hn[0].split("|", 1)[0], p, oc)
            w = a / (a + b) if (a + b) > 0 else 0.5
            pp_observe(B, hp[0], hp[1], p, w, oc); pp_observe(B, hn[0], hn[1], p, 1.0 - w, oc)
        A = B
    A["mining"] = {"instances": len(inst), "unambiguous": len(unamb), "ambiguous": len(amb), "rounds": rounds}
    return A


def _pp_zbin(z: float) -> str:
    for e, nm in zip(PP_Z_EDGES, PP_Z_NAMES):
        if z > e:
            return nm
    return PP_Z_NAMES[-1]


def _pp_contrast(sc, idx: int) -> float:
    if PP_ZFORM == "max":
        others = [s for i2, s in enumerate(sc) if i2 != idx]
        return sc[idx] - (max(others) if others else sc[idx] - 1.0)
    m = max(sc)
    return sc[idx] - (m + math.log(sum(math.exp(s - m) for s in sc) / len(sc)))


def pp_arc_values(toks: Sequence[str], pos: Sequence[str], assoc: Dict[str, object],
                  k_cap: Optional[int] = None):
    """(head, dependent) -> cue value for every retrieved candidate host of every case-marked nominal.
    `pp`    -- the contrast of this candidate's LEXICAL association with the preposition against the retrieved
               population; `ppobj` -- the same contrast on the THEMATIC channel (what the phrase is about, given the
               host's type), carrying the host type because that is the only thing that channel conditions on.
    Returns (pp_values, ppobj_values)."""
    out = {}; out2 = {}
    for prep, obj, cands in pp_sites(toks, pos, k_cap):
        p = toks[prep - 1].lower()
        sc = [math.log(max(pp_p_given(assoc, pp_host_key(toks, pos, q), pp_host_class(toks, pos, q), p), 1e-12))
              for q in cands]
        oc = pp_obj_class(toks, pos, obj)
        so = [math.log(max(pp_p_obj(assoc, pp_host_type(pos[q - 1]), p, oc), 1e-12)) for q in cands]
        for idx, q in enumerate(cands):
            if q == obj:
                continue
            out[(q, obj)] = _pp_zbin(_pp_contrast(sc, idx))
            out2[(q, obj)] = pp_host_type(pos[q - 1]) + ":" + _pp_zbin(_pp_contrast(so, idx))
    return out, out2


# ------------------------------------------------------------------------------------- THE GENITIVE CASE MARKER
# The nmod population is not one thing.  Split by construction (UD-EWT test 700, gold nmod, the live asset, in-order):
#   prepositional with a retrieved site 253 (recall 0.613) | POSSESSIVE PRONOUN 98 (0.449) | prepositional with no
#   site 56 (0.250) | bare PROPN 54 (0.167) | bare NOUN 35 (0.086) | GENITIVE enclitic 27 (0.074) | bare NUM 9 (0.000).
# 42% of nmod is not prepositional at all, so no preposition association can reach it -- and the two worst-served
# groups are the OTHER way English marks case: the enclitic genitive (a POSTposition) and the possessive pronoun
# (inherently genitive).  Same brain principle as the whole PP build -- a case marker identifies the dependent and
# opens the search for its host (Pinker 1984; the Competition Model's case cue) -- but a genitive's host is not
# competed for: it specifies the nominal it precedes, so it is an item-based CONSTRUCTION (Tomasello 2003), the
# family this organ already has for coordination, NP-internal modification and function words.  Its validity is
# LEARNED by the arm's own soft counts like every other construction; nothing here is hand-weighted.
# MEASURED (train cap 1500, UD-EWT test 700, in-order, paired bootstrap over sentences): alone, nmod 0.410 -> 0.476
# (+0.0655, CI [+0.0427, +0.0918]) and UAS +0.0061; with the PP cue, nmod 0.491 and obl 0.535.
NPMOD_INNER = frozenset({"DET", "ADJ", "NUM", "ADV"})
# a pronoun that is NOT a possessive determiner: nominative/accusative forms, demonstratives, relatives, quantifiers.
NON_POSS_PRON = frozenset({"i", "he", "she", "it", "they", "we", "you", "me", "him", "them", "us", "who", "whom",
                           "which", "that", "this", "these", "those", "what", "there", "one", "all", "some", "both",
                           "each", "any", "none", "such", "another", "other", "others", "someone", "something",
                           "anyone", "anything", "everyone", "everything", "nothing", "nobody", "himself",
                           "herself", "itself", "themselves", "myself", "yourself", "ourselves"})


def genitive_arcs(toks: Sequence[str], pos: Sequence[str]) -> List[Tuple[int, int]]:
    """GENITIVE construction: a nominal marked genitive -- by the enclitic ("John 's book") or by being a possessive
    pronoun ("its wares") -- depends on the head of the nominal run that follows it; the enclitic itself depends on
    the genitive nominal (a case marker attaches to its own nominal, as every case marker in this organ does)."""
    n = len(pos); out: List[Tuple[int, int]] = []
    lows = [t.lower() for t in toks]
    for i in range(1, n + 1):
        gen = None; mark = None
        if pos[i - 1] == "PART" and lows[i - 1] in ("'s", "s", "'"):
            for q in range(i - 1, 0, -1):
                if pos[q - 1] in ("NOUN", "PROPN", "PRON", "NUM"):
                    gen = q; mark = i; break
                if pos[q - 1] not in NPMOD_INNER:
                    break
        elif pos[i - 1] == "PRON" and i < n and pos[i] in PP_NP_RUN and lows[i - 1] not in NON_POSS_PRON:
            gen = i
        if gen is None:
            continue
        host = pp_run_head(pos, (mark or gen) + 1)
        if host is not None and host != gen:
            out.append((host, gen))
            if mark is not None:
                out.append((gen, mark))
    return out


CONSTRUCTIONS["gen"] = genitive_arcs      # registered here: the schema is defined below the construction table



# ------------------------------------------------------------------------------------ MAIN-ASSERTION (ROOT) CUES
COP_FORMS = frozenset({"be", "is", "are", "was", "were", "been", "being", "am", "become", "became", "becomes",
                       "seem", "seems", "seemed", "'m", "'s", "'re", "s", "m", "re"})
AUX_BE = frozenset({"be", "is", "are", "was", "were", "been", "being", "am", "'m", "'s", "'re", "m", "re", "s"})
AUX_HAVE = frozenset({"have", "has", "had", "'ve", "'d", "ve", "d", "having"})
AUX_MOD = frozenset({"will", "would", "can", "could", "may", "might", "shall", "should", "must", "do", "does",
                     "did", "done", "'ll", "ll", "wo", "ca", "need", "dare", "ought", "let"})
WH_FORMS = frozenset({"who", "whom", "whose", "which", "that", "what", "where", "when", "why", "how",
                      "whatever", "whoever", "whenever"})
SENT_END = frozenset({".", "!", "?", ";"})
_PREVERB_SKIP = frozenset({"not", "n't", "never", "also", "just", "really"})


def finiteness(toks: Sequence[str], pos: Sequence[str], i: int) -> str:
    """FINITENESS CUE: the morphological + auxiliary-frame tense class of the verbal candidate at 1-based i.  Form
    only -- the token against its lemma (the morphology organ's decomposition; Rastle & Davis 2008, Taft 1979) and
    the nearest preceding auxiliary or infinitival marker (Mintz 2003 frequent frames).  No treebank, no tagger."""
    lows = [t.lower() for t in toks]
    k = i - 1
    while k >= 1 and (pos[k - 1] == "ADV" or lows[k - 1] in _PREVERB_SKIP):
        k -= 1
    if k >= 1:
        if pos[k - 1] == "PART" and lows[k - 1] == "to":
            return "to"
        if pos[k - 1] == "AUX":
            w = lows[k - 1]
            return "auxhave" if w in AUX_HAVE else "auxbe" if w in AUX_BE else "auxmod"
        if pos[k - 1] == "VERB" and lows[k - 1] in AUX_MOD:
            return "auxmod"
    w = lows[i - 1]; lem = lemma_verb(toks[i - 1]).lower()
    if w.endswith("ing") and w != lem:
        return "ing"
    if w == lem:
        return "base"
    if w.endswith("s") and not w.endswith("ss"):
        return "s"
    return "ed"


_COP_STOP = frozenset({"PUNCT", "ADP", "SCONJ", "CCONJ"})


def cop_predicates(toks: Sequence[str], pos: Sequence[str]) -> set:
    """COPULAR-PREDICATION CUE: the 1-based indices that a copula with NO lexical verb in its own clause makes the
    predicate -- in "the vote is confusing" the assertion is CONFUSING (Pustet 2003).
    LOCALITY (2026-09-13 round 2; this is the ROOT CAUSE of the dominant copular-subject miss): the scan for a verb
    after the AUX must stop at ADP / SCONJ / infinitival `to` / CCONJ as well as PUNCT.  `function_word_arcs`'s
    next_verb stops only at PUNCT, so in "we ARE capable of PROTECTING it" the copula binds to `protecting` -- a
    verb behind a PREPOSITION, inside the predicate phrase -- and the copular reading never fires at all.  An
    auxiliary marks the tense of ITS OWN clause; a verb in an embedded phrase is not part of its verb group, the
    same locality every other cue in this organ respects.  MEASURED (in-order, n=700, on top of the root cues):
    root 0.7486 -> 0.7543, advcl 0.313 -> 0.343, xcomp 0.715 -> 0.759, cop-subj 0.422 -> 0.441.
    HDLAB_ARM_COP_LOCALITY=0 restores the PUNCT-only scan."""
    n = len(pos); lows = [t.lower() for t in toks]; out = set()
    for i in range(n):
        if pos[i] != "AUX" or lows[i] not in COP_FORMS:
            continue
        v = None
        for k in range(i + 1, n):
            if pos[k] == "VERB":
                v = k; break
            if pos[k] == "PUNCT":
                break
            if COP_LOCALITY and (pos[k] in _COP_STOP or (pos[k] == "PART" and lows[k] == "to")):
                break
        if v is not None:
            continue
        for k in range(i + 1, n):
            if pos[k] in ("VERB", "PUNCT"):
                break
            if pos[k] in ("ADJ", "NOUN", "PROPN", "PRON", "NUM"):
                if pos[k] == "PRON":
                    out.add(k + 1); break
                j = k
                while j + 1 < n and pos[j + 1] in NP_RUN:
                    j += 1
                heads = [m for m in range(k, j + 1) if pos[m] in ("NOUN", "PROPN")]
                if heads:
                    out.add(heads[-1] + 1); break
                adjs = [m for m in range(k, j + 1) if pos[m] in ("ADJ", "NUM")]
                out.add((adjs[-1] if adjs else k) + 1); break
    return out


def _csubg_bin(o: float) -> str:
    """The occupancy VALUE the cue competes with: a graded belief, binned so the validity of each band is learned
    separately (the organ's cue values are categorical; the bin edges are swept, never adopted)."""
    if o >= CSUBG_BINS[2]:
        return "hi"
    if o >= CSUBG_BINS[1]:
        return "md"
    if o >= CSUBG_BINS[0]:
        return "lo"
    return "no"


def _memo(key, val):
    if len(_CSUB_MEMO) >= _CSUB_MEMO_MAX:
        _CSUB_MEMO.clear()
    _CSUB_MEMO[key] = val
    return val


def _csub_subject_before(toks, pos, c):
    """The subject side of a copular clause: the nearest nominal standing before the tense carrier at 1-based `c`,
    skipping a CASE-MARKED one (a prepositional nominal is oblique, never the subject -- Pinker 1984).  This is
    `csub_sites`' own scan plus the two corrections the pri-117 board A/B paid for, both of which are rules this
    organ already applies on the complement side:
      (hyph) THE RIGHT-HAND HEAD RULE ACROSS A HYPHEN (Williams 1981; `_np_run_end`'s `_HYPHEN` clause).  The
        phrase-start walk stopped at the PUNCT in "with al - Qaeda", so the preposition was never seen and the
        object of a PP was taken as the subject -- one of the two patient items the board lost.
      (clsub) A CLAUSE IS NOT A NOMINAL SUBJECT.  In "Call a vet would be a good idea" the nearest nominal before
        the copula is the OBJECT of the clausal subject's own verb; UD makes that clause (its verb) the subject
        (`csubj`).  A predicate standing to the left of the candidate, inside the same clause, means the subject
        is CLAUSAL, so no nominal pair is proposed -- the other patient item."""
    k = c - 1
    while k >= 1:
        if pos[k - 1] in NOMINAL or pos[k - 1] == "NUM":
            a = k
            while True:
                if a - 1 >= 1 and pos[a - 2] in NP_RUN:
                    a -= 1; continue
                if (CSUB_COVERAGE and CSUB_SUBJ_HYPHEN and a - 2 >= 1 and pos[a - 2] == "PUNCT" and toks[a - 2] in _HYPHEN
                        and pos[a - 3] in NP_RUN):
                    a -= 2; continue                          # (hyph) cross the hyphen of a compound name
                break
            if a - 1 >= 1 and pos[a - 2] == "ADP":
                k = a - 2; continue
            if CSUB_SUBJ_NO_CLAUSAL:
                for m in range(a - 1, 0, -1):                 # (clsub) a predicate to the left, same clause
                    if pos[m - 1] in ("SCONJ", "CCONJ") or (pos[m - 1] == "PUNCT" and toks[m - 1] in _HARD_STOP):
                        break
                    if pos[m - 1] == "VERB":
                        return None
            return k
        if pos[k - 1] in ("VERB", "SCONJ", "CCONJ"):
            return None
        k -= 1
    return None


def _csub_subject_inverted(toks, pos, c, q):
    """SUBJECT-AUXILIARY INVERSION (the interrogative construction, a stored form-meaning pairing the organ
    already carries in `_cop_inverted` / `host_belief`): with no subject to the copula's left, the subject is the
    first nominal to its RIGHT and the predicate stands after it -- "IS that a money maker ?".  pri 113 section
    29 counted 13 clauses where the predicate was found and the (pre-copular) subject scan failed."""
    lows = [t.lower() for t in toks]
    if not _cop_inverted(list(pos), lows, c - 1):
        return None
    for k in range(c + 1, min(q, len(pos) + 1)):
        if pos[k - 1] in ("NOUN", "PROPN", "PRON", "NUM"):
            return k
        if pos[k - 1] in ("VERB", "PUNCT", "SCONJ", "CCONJ"):
            return None
    return None


_CSUB_MEMO = {}          # (tokens, categories) -> pairs; the graded hand-off re-scores the same sentence up to
_CSUB_MEMO_MAX = 8       # four times and each cue pass asks twice, so the scan is memoised (read-time cost)


def cop_subject_pairs(toks, pos):
    """(predicate, subject) pairs, 1-based, for every copular predication in the sentence -- the token holding the
    clause's predicate slot and the nominal the copula predicates it OF.
    CSUB_COVERAGE (pri 117): the predicate comes from `cop_complement` -- the construction set the merged pri-113
    tree carries (inverted / fronted / locative / wh / clause-final / parenthetical) -- instead of the narrow
    `cop_predicates` scan this cue keyed on until now, and the inverted construction's post-copular subject is
    recovered.  pri 113 section 29 located DETECTION COVERAGE as what holds its prototype at 0.65: the pair was
    found for 101 of the 167 non-verbal clauses.  With the switch off the shipped detection is reproduced exactly
    (asserted over 120 sentences)."""
    key = (tuple(toks), tuple(pos), CSUB_COVERAGE, CSUB_VERBAL_HOST)
    hit = _CSUB_MEMO.get(key)
    if hit is not None:
        return hit
    n = len(pos); lows = [t.lower() for t in toks]; out = []
    if not CSUB_COVERAGE:
        for q in sorted(cop_predicates(list(toks), list(pos))):
            c = None
            for k in range(q - 1, 0, -1):
                if pos[k - 1] == "AUX" and lows[k - 1] in COP_FORMS:
                    c = k; break
                if pos[k - 1] == "VERB":
                    break
            if c is None:
                continue
            s = _csub_subject_before(toks, pos, c)
            if s is not None:
                out.append((q, s))
        _memo(key, out)
        return out
    for i in range(n):
        if pos[i] != "AUX" or lows[i] not in COP_FORMS:
            continue
        qi = cop_complement(list(toks), list(pos), i)
        if qi is not None and (qi == i or pos[qi] in ("VERB", "AUX")):
            qi = None
        if qi is None and CSUB_VERBAL_HOST:
            for k in range(i + 1, n):                      # the VERBAL HOST of the same verb group (branch 1)
                if pos[k] == "VERB":
                    qi = k; break
                if pos[k] in ("PUNCT", "SCONJ", "CCONJ") or (pos[k] == "PART" and lows[k] == "to"):
                    break
                if pos[k] in ("ADV", "AUX", "PART"):
                    continue
                break
        if qi is None:
            continue
        q = qi + 1; c = i + 1
        s = _csub_subject_before(toks, pos, c)
        if s is None:
            s = _csub_subject_inverted(toks, pos, c, q)
        if s is None or s == q:
            continue
        out.append((q, s))
    _memo(key, out)
    return out


def csub_sites(toks, pos):
    """COPULAR-SUBJECT cue: value `pred` on the (predicate <- subject) arc and `later` on every
    (verb-to-the-predicate's-right <- the same subject) arc; the validity is LEARNED like every other cue.
    pri 117: the pair detection is `cop_subject_pairs` (the construction set), which is the DETECTION-COVERAGE
    fix pri 113 section 29 located -- the scan this cue keyed on found the predicate in 101 of the 167
    non-verbal clauses, the construction set finds it in more."""
    n = len(pos); out = {}
    for (q, subj) in cop_subject_pairs(toks, pos):
        out[(q, subj)] = "pred"
        for v in range(q + 1, n + 1):
            if pos[v - 1] == "VERB":
                out.setdefault((v, subj), "later")
        if CSUB_SUPPRESS_COP:
            for c in range(min(q, subj), max(q, subj) + 1):
                if pos[c - 1] == "AUX" and toks[c - 1].lower() in COP_FORMS:
                    out.setdefault((c, subj), "carrier")
    return out


def csub_graded_sites(toks, pos, occ):
    """THE GRADED ARC FEATURE (pri 117).  The same two arcs, valued by HOW STRONGLY the candidate head holds its
    clause's predicate slot (pri 110's occupancy, graded off the category organ's own posterior): a confident
    predicate claims its subject, an uncertain one competes weakly.  `occ` is a per-token (0-based) probability;
    without it the cue is silent (the categorical `csub` cue above still fires)."""
    if occ is None:
        return {}
    n = len(pos); out = {}
    for (q, subj) in cop_subject_pairs(toks, pos):
        b = _csubg_bin(float(occ[q - 1]) if q - 1 < len(occ) else 0.0)
        out[(q, subj)] = "pred:" + b
        for v in range(q + 1, n + 1):
            if pos[v - 1] == "VERB":
                out.setdefault((v, subj), "later:" + b)
        if CSUB_SUPPRESS_COP:
            for c in range(min(q, subj), max(q, subj) + 1):
                if pos[c - 1] == "AUX" and toks[c - 1].lower() in COP_FORMS:
                    out.setdefault((c, subj), "carrier:" + b)
    return out


def occupancy_from_posterior(toks, pos, tag_post, tag_names=None):
    """P(this token fills its clause's predicate slot) per 0-based token, from the category organ's GRADED
    hand-off -- the signal pri 110 already computes and hands down only as a tag (pri 113 section 27).
    `tag_post` is the per-token {category: P} the frontend already passes to `arc_scores_graded`."""
    if not tag_post:
        return None
    names = list(tag_names) if tag_names else sorted({k for d in tag_post if d for k in d})
    if not names or any(t not in names for t in _PS_NEEDED):
        return None                                         # a category inventory this computation cannot read
    post = np.zeros((len(toks), len(names)))
    for i, d in enumerate(tag_post):
        if i >= len(toks) or not d:
            continue
        for k, v in d.items():
            j = names.index(k) if k in names else None
            if j is not None:
                post[i, j] = float(v)
    sites = predicate_sites(list(toks), list(pos), post, names)
    occ = np.zeros(len(toks))
    for i, s in sites.items():
        if 0 <= i < len(occ):
            occ[i] = float(s)
    return occ


def occupancy_from_tags(toks, pos):
    """The same read from a ONE-HOT category column -- what the offline teacher (tools/build_attachment_validities)
    has, so the cue is taught at build time with the same values it is read with."""
    names = list(_UPOS)
    if any(t not in names for t in _PS_NEEDED):
        return None
    post = np.zeros((len(toks), len(names)))
    for i, p in enumerate(pos):
        post[i, names.index(p) if p in names else names.index("X")] = 1.0
    sites = predicate_sites(list(toks), list(pos), post, names)
    occ = np.zeros(len(toks))
    for i, s in sites.items():
        if 0 <= i < len(occ):
            occ[i] = float(s)
    return occ


def observe_copular_subject(toks, pos, occ, table=None, weight: float = 1.0) -> int:
    """PLASTICITY -- the observe path for the graded cue's validity (Rescorla-Wagner / Competition-Model validity
    accrual: validity = availability x reliability, accrued from what the reader PERCEIVES).  Every copular
    predication READ is one confirmed outcome: the predicate slot's filler heads the pre-copular nominal, with
    the occupancy as the strength of the belief, and the later verbs inside the predicate phrase accrue the
    competing (zero) outcome.  No treebank and no tree is read -- the construction is stored lexical knowledge
    (Goldberg 1995) the organ already carries in COP_FORMS.  Returns the number of arcs accrued."""
    tab = table if table is not None else load_attachment_validities()
    counts = tab["counts"]; cues = counts.setdefault("cues", {}).setdefault("csubg", {})
    cfgc = counts["config"]; n = len(pos); k = 0
    sc_cfg = lambda j, h: ("ROOT:" + pos[j - 1]) if h == 0 else f"{pos[h - 1]}>{pos[j - 1]}:{'L' if h < j else 'R'}"
    for (q, subj) in cop_subject_pairs(toks, pos):
        o = float(occ[q - 1]) if (occ is not None and q - 1 < len(occ)) else 0.0
        b = _csubg_bin(o)
        comp = [(v, subj, "later:" + b, 0.0) for v in range(q + 1, n + 1) if pos[v - 1] == "VERB"]
        if CSUB_SUPPRESS_COP:
            comp += [(c, subj, "carrier:" + b, 0.0) for c in range(min(q, subj), max(q, subj) + 1)
                     if pos[c - 1] == "AUX" and toks[c - 1].lower() in COP_FORMS]
        for (h, j, val, outcome) in [(q, subj, "pred:" + b, o)] + comp:
            cfg = sc_cfg(j, h)
            if cfg not in cfgc:
                continue                                     # an unseen configuration has no base rate to contrast with
            cell = cues.setdefault(cfg + "|" + val, [0.0, 0.0])
            cell[0] += weight * outcome; cell[1] += weight; k += 1
    if k:
        tab["strength"] = strengths_from_arc_counts(counts)
    return k


REANALYSIS_STATS = {"fired": 0, "eligible": 0, "sentences": 0}


def revise_copular_subject(toks, pos, A, hd, occ=None):
    """PREDICATE-ARRIVAL REANALYSIS of the subject arc (pri 117), the in-order form of pri 113's held decode.
    The incremental decode commits the subject while the predicate's competitor is unresolved, and a verb INSIDE
    the predicate phrase then steals it; the brain revises when the disambiguating word arrives (Frazier &
    Rayner 1982), which is what this organ already does for the ROOT arc (INCR_ROOT_REANALYSIS).  The revision
    (a) fires only when the stealer stands to the RIGHT of the predicate -- so at the predicate's arrival the
    subject was still open and this IS that arrival decision, read in order; (b) carries no parameter: it takes
    the arc the organ's OWN learned activations prefer; (c) never creates a cycle."""
    if not CSUB_REANALYSIS or not hd:
        return hd
    out = dict(hd); n = len(pos)
    for (q, subj) in cop_subject_pairs(toks, pos):
        v = out.get(subj, 0)
        if v == q or not (1 <= q <= n and 1 <= subj <= n):
            continue
        if not (1 <= v <= n or v == 0):
            continue
        if not CSUB_REANALYSIS_ANY and not (1 <= v <= n and pos[v - 1] == "VERB" and (v > q or CSUB_REANALYSIS_LEFT)):
            continue                                        # narrow form: only the late-verb steal
        REANALYSIS_STATS["eligible"] += 1
        cur = float(A[v][subj]) if (0 <= v <= n and np.isfinite(A[v][subj])) else -1e18
        if not (np.isfinite(A[q][subj]) and float(A[q][subj]) > cur):
            continue                                         # the organ's own activations must prefer the predicate
        k = q; ok = True; seen = 0                           # q must not sit below subj
        while k and seen <= n:
            if k == subj:
                ok = False; break
            k = out.get(k, 0); seen += 1
        if ok:
            out[subj] = q; REANALYSIS_STATS["fired"] += 1
    return out



# ---------------------------------------------------------------------------------- THE CLAUSE'S PREDICATE SLOT
# ONE CONVENTION, TWO LOSSES (2026-09-14, pri 110).  UD tags a clause's MAIN-VERB / copular `be` and `have` as AUX.
# The count-based category organ learned that convention, so a real main verb comes out AUX -- and the same 23 tokens
# of UD-EWT test 700 carry 87 NET head flips, 58% of the whole tag-to-head loss (2026-09-13 attribution), while an
# ADDITIVE predicate rescue cannot see them at all (4.7-38.8% of dropped verbs; pri 107 section 4g).  Two consumers,
# one cause, and measuring them apart gave two half-answers.
#
# THE BRAIN.  One predicate per clause (Spivey-Knowlton 1993).  An auxiliary is a TENSE CARRIER for a predicate that
# is not itself finite (Bybee 1994 on auxiliation; Pustet 2003 on the copula as the tense carrier of a NON-VERBAL
# predication).  There are exactly three ways a clause's tense carrier can be discharged:
#     (1) a VERBAL HOST in its own verb group            -> the host is the predicate      (an ordinary auxiliary)
#     (2) a NON-VERBAL PREDICATE it carries tense for    -> the complement is the predicate (copular predication)
#     (3) neither                                        -> THE CARRIER ITSELF predicates   (existential / possessive)
# so the clause's predicate-slot occupancy of a carrier at i is
#     occ_i = (1 - P(verbal host in i's verb group)) * (1 - P(copular predication available at i))
# Term 1 is GRADED, read off the category organ's own posterior, and the walk over intervening words is weighted by
# THEIR belief that they are skippable, so an argmax mis-tag cannot silently carry the walk into the next phrase.
# Term 2 is a CONSTRUCTION test over closed-class forms this organ already carries (COP_FORMS / AUX_BE / AUX_HAVE /
# WH_FORMS): `have` and `do` are never copulas, and a `be` whose pivot is the expletive `there` predicates EXISTENCE
# rather than a property of a subject (Goldberg 1995 -- the existential-there construction).
#
# WHERE IT IS READ.  `revise_for_predicate_slot` applies it to the posterior the CATEGORY organ hands down
# (hdlab/lexical_categories.posterior), so ONE computation reaches every consumer -- the governor through the graded
# category hand-off, the reader's event detector through the tag, and the predicate rescue through the cue block --
# instead of one arm per consumer.  It is a top-down constraint on a settling belief (MacDonald 1994 constraint
# satisfaction), not a second organ.
#
# MEASURED (UD-EWT test 700, live chain, paired bootstrap over sentences; experiments/exp_one_convention_two_losses_v1.py):
#   * THE GOVERNOR.  UAS 0.6245 -> 0.6331 (+0.0086 CI[+0.0047,+0.0126] SEP); on the SOLE-AUX CLAUSES 0.6074 ->
#     0.6588 (+0.0515 CI[+0.0239,+0.0816] SEP).  root +0.0171 SEP (sole-AUX +0.1154 SEP), nsubj +0.0221 SEP
#     (+0.1129 SEP), expl 0.292 -> 0.833 (+0.5417 SEP; on the sole-AUX clauses 0.077 -> 1.000), ccomp +0.0431 SEP,
#     obj / obl SEP up, nmod +0.0000, and after the phase-7 repairs cop is EXACTLY +0.0000: no relation is down.
#     INFORMATION-FREE TWIN (the same number of AUX tokens promoted at random, 3 seeds): UAS 0.6155 / 0.6175 /
#     0.6178, every one CI-separated BELOW the floor.
#   * THE READER (2077 sentences, the convention-free instrument -- does the clause produce an event at all?):
#     gold-verb sentences yielding ZERO events 33 -> 9 of 1240 (0.0266 -> 0.0073; OFF is 55), event recall 0.9501 ->
#     0.9812 (+0.0311 CI[+0.0244,+0.0379] SEP) at event precision 0.8715 -> 0.8621.  It DOMINATES pri 107's boolean
#     sole-AUX arm on all three at once (that arm: recall 0.9597, precision 0.8364, blind 18), which is why
#     HDLAB_PREDICATE_RESCUE_AUX stays default OFF.
#   * THE DECISION ITSELF, against the only question UD's own column CAN adjudicate (is this be/have a main verb?):
#     precision 0.8462 / recall 0.9565 on the AUX population, against 0.1164 for the blanket "a sole AUX is the
#     predicate" rule pri 107 refuted.
#   * GENERALISATION on GUM/GENTLE (1200 sentences by stride over 12+ genres, entirely outside this organ's count
#     supply): UAS 0.6008 -> 0.6096 (+0.0088 CI[+0.0062,+0.0117] SEP), sole-AUX clauses 0.5830 -> 0.6423 (+0.0593
#     CI[+0.0413,+0.0792] SEP), expl 0.221 -> 0.794 -- a LARGER effect out of supply than in it.
# Read-time cost 0.059 ms/sentence (+0.6% of the posterior it revises).
# HDLAB_LC_PREDICATE_SLOT=0 turns it off; HDLAB_PREDICATE_SLOT_TH is the operating point (swept 0.3/0.5/0.7/0.9, flat).
EXPLETIVE = frozenset({"there"})
_PS_SKIP = frozenset({"ADV", "INTJ"})
_PS_NEG = frozenset({"not", "n't", "never", "also", "just", "really", "only", "still", "already"})
PREDICATE_SLOT_TH = float(os.environ.get("HDLAB_PREDICATE_SLOT_TH", "0.5"))
_PS_CARRIERS = None


def main_verb_carriers() -> frozenset:
    """The forms that can HEAD a clause on their own.  A modal cannot (Bybee 1994: the fully auxiliated class);
    `be` predicates existence or location, `have` possession, `do` an activity."""
    global _PS_CARRIERS
    if _PS_CARRIERS is None:
        _PS_CARRIERS = frozenset(set(AUX_BE) | set(AUX_HAVE) | {"do", "does", "did", "doing", "done"})
    return _PS_CARRIERS


def host_belief(toks: Sequence[str], tags: Sequence[str], post, tag_names: Sequence[str], i: int) -> float:
    """P(a VERBAL HOST stands in the verb group of the tense carrier at 0-based i).  The verb group is CONTIGUOUS
    modulo adverbs / negation / an inverted subject pronoun, and an auxiliary CHAIN counts (`has been roiled`: the
    host of `has` is `been`, itself a carrier), so the belief is P(VERB) + P(AUX) at the position reached.
    Infinitival `to` CLOSES the group -- a to-infinitive is a COMPLEMENT, not an auxiliary's host, which is what
    leaves `have` predicative in `have to see`.
    THE WALK IS GRADED, NOT ARGMAX: stepping over a word costs that word's own belief that it is skippable, so an
    upstream mis-tag cannot carry the walk into the next phrase.  MEASURED: in `i have stronger will than you
    think`, `stronger` is argmax-ADV, so an argmax walk stepped over it and read the NOUN `will` (argmax-AUX) as the
    host, scoring the possessive `have` 0.04."""
    vi = tag_names.index("VERB"); ai = tag_names.index("AUX")
    advi = tag_names.index("ADV"); pai = tag_names.index("PART"); pri = tag_names.index("PRON")
    n = len(toks); lows = [t.lower() for t in toks]
    reach = 1.0; best = 0.0; seen_pron = False
    for k in range(i + 1, n):
        if tags[k] == "PART" and lows[k] == "to":
            break
        # AUXILIARY ORDER (modal > have > be > V; Chomsky 1957's Aux rule, a PINNED descriptive fact of English):
        # a MODAL can never be the host of a `have` / `be` / `do` carrier (*have will), so its AUX belief cannot count
        # as host evidence.  Without this, `i have stronger will than you think` reads the NOUN `will` -- which the
        # category organ tags AUX -- as the host of the possessive `have`, and the carrier scores 0.24, not 0.99.
        v = float(post[k, vi]) + (0.0 if lows[k] in AUX_MOD else float(post[k, ai]))
        best = max(best, min(1.0, reach * v))
        skip = float(post[k, advi] + post[k, pai])
        if lows[k] in _PS_NEG:
            skip = max(skip, 1.0)
        if not seen_pron and k <= i + 2 and lows[k] not in EXPLETIVE:
            skip = max(skip, float(post[k, pri]))          # subject-auxiliary inversion: "Should HE have known"
            seen_pron = True
        reach *= min(1.0, skip)
        if reach < 0.02:
            break
    return min(1.0, best)


def is_existential(toks: Sequence[str], tags: Sequence[str], i: int) -> bool:
    """The existential-there construction (Goldberg 1995): the pivot adjacent to the carrier at 0-based i is the
    expletive `there`, so nothing is predicated OF anything and the carrier asserts EXISTENCE.  The backward scan
    steps over an auxiliary chain, because the pivot sits before the WHOLE chain (`there had BEEN none`)."""
    lows = [t.lower() for t in toks]; n = len(toks)
    for k in range(i - 1, max(-1, i - 4), -1):
        if tags[k] in _PS_SKIP or lows[k] in _PS_NEG or tags[k] == "AUX":
            continue
        if lows[k] in EXPLETIVE:
            return True
        break
    for k in range(i + 1, min(n, i + 3)):
        if tags[k] in _PS_SKIP or lows[k] in _PS_NEG:
            continue
        if lows[k] in EXPLETIVE:
            return True
        break
    return False


def copular_available(toks: Sequence[str], tags: Sequence[str], i: int) -> float:
    """1.0 when the carrier at 0-based i is a COPULA with a PREDICABLE COMPLEMENT -- the predicate slot is then held
    by that non-verbal predicate, which `cop_predicates` already promotes and which the UD convention makes the
    clause head.  0.0 when the carrier cannot be a copula at all (`have` / `do`), when the construction is
    existential, or when no complement follows (a bare locative or elliptical `be`, which predicates by itself).
    THE COMPLEMENT, NOT THE SUBJECT, IS THE TEST: keying on the subject instead left 31 false promotions on UD-EWT
    test 700, 26 of them copular clauses whose subject scan failed (inversion, a participial NP, a fronted PP).  The
    slot's occupant is the complement, so that is what has to be looked for."""
    lows = [t.lower() for t in toks]
    if lows[i] not in COP_FORMS or is_existential(toks, tags, i):
        return 0.0
    det = False; crossed = False
    for k in range(i + 1, len(toks)):
        if tags[k] == "DET":
            # A DETERMINER OPENS A NOMINAL, AND THAT NOMINAL IS THE COMPLEMENT: whatever stands next belongs to the
            # phrase the determiner opened, so its own argmax category is not the question.  Without this, `Here is a
            # revised draft` reads the participial modifier `revised` (argmax-VERB) as if a verb stood in complement
            # position and promotes the copula.  A CLAUSE-FINAL determiner is a demonstrative pronoun (`Wtf is this ?`).
            det = True
            if k == len(toks) - 1 or all(tags[m] == "PUNCT" for m in range(k + 1, len(toks))):
                return 1.0
            continue
        if tags[k] in _PS_SKIP or tags[k] in ("NUM", "PUNCT") or lows[k] in _PS_NEG:
            if tags[k] == "PUNCT":
                crossed = True                             # "The answer is , \" Yes ! \"" -- the complement is behind the comma
            continue
        if crossed:
            # A VERBAL FORM BEHIND A PUNCTUATION BOUNDARY IS NOT IN THIS COPULA'S VERB GROUP: it opens a quoted or
            # clausal complement, and THAT occupies the predicate slot -- the same locality `cop_predicates` already
            # respects with _COP_STOP.  `The question is , " Should he have known it was coming ? "`.
            return 1.0
        if det:
            return 1.0
        if tags[k] == "SCONJ" or tags[k] == "PART" or lows[k] in WH_FORMS:
            return 1.0                                     # a CLAUSAL / infinitival complement occupies the slot too
        if tags[k] in ("ADJ", "NOUN", "PROPN", "PRON", "ADP", "SYM", "X", "INTJ"):
            return 1.0
        return 0.0
    # NOTHING TO THE RIGHT AT ALL.  English does not leave a copula complement-less: it FRONTS the predicate
    # ("whatever age you ARE", "the other possibilities you had better") or ELIDES it ("i am sure they ARE"), so a
    # CLAUSE-FINAL copula's complement is ELSEWHERE and the predicate slot is NOT free.  Measured (2026-09-14 phase 7):
    # this is the whole of the state dimension's cost -- naming the three flipped items showed two of them were a
    # clause-final copula promoted against its own fronted/elided predicate; with this the state dimension is FLAT
    # (0.7487 -> 0.7487, 0 items of 378) and the governor's `cop` relation goes from -0.0108 to EXACTLY +0.0000.
    return 1.0


_PS_NEEDED = ("VERB", "AUX", "ADV", "PART", "PRON")


def _next_content_word(toks: Sequence[str], tags: Sequence[str], i: int) -> str:
    """The next word after 0-based i that is not an adverb, a negation or punctuation."""
    for k in range(i + 1, len(toks)):
        if tags[k] in _PS_SKIP or tags[k] == "PUNCT" or toks[k].lower() in _PS_NEG:
            continue
        return toks[k].lower()
    return ""


def predicate_slot_occupancy(toks: Sequence[str], tags: Sequence[str], post, tag_names: Sequence[str]):
    """P(this token occupies its clause's predicate slot), per token.  Non-carrier tokens score 0: a VERB already
    holds the slot and the rescue's noun arm owns the rest.  See the block comment for the computation.
    Returns all-zero (a no-op) under a category inventory that does not carry the UPOS classes the computation
    reads -- the organ's own docstring anticipates swapping to induced classes, and a missing class must degrade to
    silence, not to an exception."""
    n = len(toks); occ = [0.0] * n
    if any(t not in tag_names for t in _PS_NEEDED):
        return occ
    lows = [t.lower() for t in toks]
    carriers = main_verb_carriers()
    for i in range(n):
        if tags[i] != "AUX" or lows[i] not in carriers:
            continue
        if lows[i] in AUX_HAVE and _next_content_word(toks, tags, i) in ("better", "best"):
            continue          # `had better` is a FIXED SEMI-MODAL -- fully auxiliated, like a modal, never a predicate
        occ[i] = ((1.0 - host_belief(toks, tags, post, tag_names, i))
                  * (1.0 - copular_available(toks, tags, i)))
    return occ


def revise_for_predicate_slot(toks: Sequence[str], post, tag_names: Sequence[str], th: float = None):
    """THE HAND-OFF, REVISED ONCE.  The category organ hands DOWN a posterior; the clause's predicate-slot
    expectation is a top-down constraint on that belief, so it is applied HERE, before the hand-off, and every
    consumer reads the revised belief without a second organ:
        P'(VERB) = occ,   P'(t != VERB) = P(t) * (1 - occ) / (1 - P(VERB))
    Only a tense carrier its clause leaves holding the predicate slot is touched (33 of 9,534 UD-EWT test tokens at
    the default operating point); every other row is byte-identical.  Returns (revised posterior, promoted indices)."""
    th = PREDICATE_SLOT_TH if th is None else float(th)
    if post is None or len(toks) == 0:
        return post, []
    tags = [tag_names[int(np.argmax(post[i]))] for i in range(len(toks))]
    occ = predicate_slot_occupancy(toks, tags, post, tag_names)
    vi = tag_names.index("VERB")
    out = None; sites = []
    for i in range(len(toks)):
        if occ[i] < th:
            continue
        pv = float(post[i, vi])
        if occ[i] <= pv:
            continue
        if out is None:
            out = post.copy()
        scale = (1.0 - occ[i]) / max(1e-9, 1.0 - pv)
        out[i] = out[i] * scale
        out[i, vi] = occ[i]
        out[i] = out[i] / max(1e-12, out[i].sum())
        sites.append(i)
    return (post if out is None else out), sites

# ------------------------------------------------------------ BRANCH (2): THE COMPLEMENT THE COPULA PREDICATES OF
# THE PREDICATION IS THE EVENT (2026-09-14, pri 113).  pri 110 (above) computes the tense carrier's three-way
# discharge and ships branch (3) -- the carrier that predicates on its own.  Branch (2), the copula that carries
# tense FOR a NON-VERBAL predicate, was left with no consumer: 167 of the 762 subject-bearing clauses of UD-EWT
# test 700 (21.9%) have their predicate on an ADJ / NOUN / ADV / PROPN / NUM by UD's design, and every downstream
# organ gates on the VERB tag, so the event detector fired on NONE of them.  The two branches are the same product:
#     carrier_occ_i      = (1 - P(verbal host at i)) * (1 - P(copular predication available at i))     [pri 110]
#     complement_occ_q   = (1 - P(verbal host at i)) *      P(copular predication available at i)      [here]
# so they PARTITION (1 - host) and one clause never gets two predicates from this computation (asserted in the
# solver cell's self-test over 90 copulas).
#
# WHICH token is the complement is a question about CONSTRUCTIONS, and the four that `cop_predicates` carries
# implicitly (property / class, right of the copula, one clause, no inversion) are not all of English.  Each of the
# seven below was found by ATTRIBUTING the residual of the participant instrument, never guessed, and each is a
# stored form-meaning pairing (Goldberg 1995) of exactly the kind this organ already holds in COP_FORMS / WH_FORMS
# / EXPLETIVE.  Measured on that instrument (UD-EWT test 700, 762 subject-bearing clauses, paired bootstrap):
#     shipped cop_predicates          recall .9357  precision .8262  on the 167 non-verbal clauses .7246
#     + LOCATION                             .9344            .8260                                .7186
#     + CLAUSE-LOCAL                         .9344            .8287                                .7186
#     + INVERSION                            .9383            .8346                                .7365
#     + DP (NP-internal participle)          .9436            .8325                                .7605
#     + LOCATIVE INVERSION (fronted)         .9501            .8366                                .7904
#     + RIGHT-HAND HEAD RULE (hyphen)        .9514            .8367                                .7964
#     + ELLIPSIS / WH / COMPLEMENT-CLAUSE /
#       SYM / PARENTHETICAL (all fourteen)     .9606            .8356                                .8383
# against the live reader as shipped: recall .8176, precision .8358, non-verbal clauses .1856.
# HDLAB_PREDICATION_CONSTRUCTIONS=0 restores the shipped scan exactly (asserted: 0 mismatches / 200 sentences).
PREDICATION_CONSTRUCTIONS = os.environ.get("HDLAB_PREDICATION_CONSTRUCTIONS", "1") == "1"
# THE LOCATIVE PREDICATE is a DEICTIC or spatial/temporal adverb -- the "location" member of Pustet 2003's inventory
# of non-verbal predication (property / class / location / possession).  It is NOT "any ADV": scoping it to the
# deictic set is what separates "the economy is DOWN" from "is just a little nostalgic" (a degree adverb inside an
# ADJ predicate).
# A WH-FORM IS THE PREDICATE of an identificational copular clause: "Which is WHY he said it",
# "that is HOW i want you to refer to me", "this is WHAT I meant".
WH_PRED = frozenset({"why", "how", "what", "where", "when", "which"})
LOCATIVE_ADV = frozenset({"here", "there", "above", "below", "out", "in", "up", "down", "back", "away", "off",
                          "over", "near", "nearby", "home", "abroad", "inside", "outside", "ahead", "behind",
                          "everywhere", "somewhere", "anywhere", "nowhere", "upstairs", "downstairs",
                          "today", "tomorrow", "yesterday", "tonight", "now", "then", "soon", "early", "late",
                          "attached", "enclosed", "gone", "on", "around", "through", "apart", "together"})
# The frontable predicate of the LOCATIVE-INVERSION / presentational construction (Birner & Ward 1998): "HERE is a
# copy", "BELOW is a list", "WHICH is why he said it".  `that` / `this` are deliberately absent -- they are
# canonical SUBJECTS in the same position, and including them cost .7904 -> .7305 on the 167 (measured).
FRONTABLE_PRED = frozenset({"here", "there", "below", "above", "attached", "enclosed",
                            "why", "how", "what", "where", "when", "which"})
_HYPHEN = frozenset({"-", "--", "\u2013", "\u2014"})
_CLAUSE_EDGE = frozenset({"SCONJ", "CCONJ"})
_NOMINALISH = frozenset({"NOUN", "PROPN", "PRON", "NUM", "ADJ", "DET"})
_HARD_STOP = frozenset({".", "!", "?", ";", ":"})


def _np_run_end(toks: Sequence[str], pos: Sequence[str], k: int) -> int:
    """The end of the NP run starting at 0-based k.  THE RIGHT-HAND HEAD RULE (Williams 1981), which this substrate
    already cites in `graded_role_assigner.is_arg_head`, makes the RIGHTMOST member the head of a compound; a hyphen
    is tagged PUNCT, so a run walk that stops at it returns the LEFT member (`money - redistributors` -> `money`,
    `ill - advised term` -> `ill`, `al - Qaeda operation` -> `al`)."""
    n = len(pos); j = k; seen_head = False
    while True:
        if j + 1 < n and pos[j + 1] in NP_RUN:
            # (dp2) A DETERMINER AFTER THE HEAD OPENS A NEW NOMINAL (Abney 1987's DP, the rule the verb-group scan
            # already uses): in "that 's the WAY the greatest bear market worked" the run must stop before the
            # second `the`, or the head comes out `market`.  Worth EXACTLY ZERO on UD-EWT test 700 and kept anyway,
            # because it is a fact about phrase structure rather than a rule fitted to this gold.
            if PREDICATION_CONSTRUCTIONS and pos[j + 1] == "DET" and seen_head:
                return j
            if pos[j + 1] in ("NOUN", "PROPN"):
                seen_head = True
            j += 1; continue
        if (PREDICATION_CONSTRUCTIONS and j + 2 < n and pos[j + 1] == "PUNCT"
                and toks[j + 1] in _HYPHEN and pos[j + 2] in NP_RUN):
            j += 2; continue
        return j


def _cop_inverted(pos: Sequence[str], lows: Sequence[str], i: int) -> bool:
    """SUBJECT-AUXILIARY INVERSION (the interrogative construction): no subject stands to the copula's left inside
    its own clause, so the first nominal to its RIGHT is the subject, not the complement -- "IS that a money
    maker ?", "ARE you free ?".  `host_belief` already carries this construction for the verb-group walk.
    A COMMA IS NOT A CLAUSE BOUNDARY: treating any PUNCT as one made a parenthetical look like a clause start and
    discarded the complement in "Most Shiites , however , ARE still reluctant" (found by residual attribution)."""
    for k in range(i - 1, -1, -1):
        p = pos[k]
        if p in _CLAUSE_EDGE:
            return True
        if p == "PUNCT":
            if lows[k] in _HARD_STOP:
                return True
            continue
        if p in _NOMINALISH:
            return False
        continue
    return True


def _fronted_predicate(toks: Sequence[str], pos: Sequence[str], i: int):
    """LOCATIVE INVERSION / the presentational construction: the token immediately left of the copula is a deictic
    locative or a wh-form with no nominal between it and the copula, and a NOMINAL follows -- "HERE is a copy".
    A DETERMINER opens that postposed nominal (Abney 1987), so a verbal form after it is an NP-internal participle
    ("here is a REVISED draft"), not the clause's verb."""
    n = len(pos); lows = [t.lower() for t in toks]
    k = i - 1
    while k >= 0 and (pos[k] == "PUNCT" or (pos[k] in ("ADV", "PART") and lows[k] in _PS_NEG)):
        k -= 1
    if k < 0 or lows[k] not in FRONTABLE_PRED or pos[k] not in ("ADV", "PRON", "DET", "ADP", "ADJ"):
        return None
    for m in range(i + 1, n):
        if pos[m] in _CLAUSE_EDGE or pos[m] == "PUNCT":
            break
        if pos[m] == "DET":
            return k
        if pos[m] == "VERB":
            break
        if pos[m] in ("NOUN", "PROPN", "PRON", "NUM"):
            return k
    return None


def cop_complement(toks: Sequence[str], pos: Sequence[str], i: int, constructions: bool = None):
    """The 0-based index of the token the copula at 0-based `i` carries tense FOR, or None.
    `constructions=False` is byte-identical to `cop_predicates`'s own inner scan (0 mismatches over 200 UD-EWT
    sentences, asserted in the solver cell's self-test); True adds the seven constructions in the block above."""
    cons = PREDICATION_CONSTRUCTIONS if constructions is None else bool(constructions)
    n = len(pos); lows = [t.lower() for t in toks]
    if pos[i] != "AUX" or lows[i] not in COP_FORMS:
        return None
    seen_comp = False
    for k in range(i + 1, n):                               # the verb-group locality (cop_predicates', extended)
        if cons and pos[k] in ("ADJ", "NOUN", "PROPN", "PRON", "NUM"):
            # (cl) ONCE THE COMPLEMENT HAS BEEN SEEN, A LATER VERB IS NOT IN THIS COPULA'S VERB GROUP -- it opens
            # the complement's OWN clause ("I am SURE you 've already GONE", "it is IMPORTANT we do this").  The
            # same locality argument as _COP_STOP, one step further: a predicable complement closes the group.
            seen_comp = True
        if seen_comp and pos[k] == "VERB":
            break
        if cons and pos[k] == "DET":
            break                                           # (det) a determiner opens a nominal; see _fronted_predicate
        if pos[k] == "VERB":
            return None
        if pos[k] == "PUNCT":
            break
        if COP_LOCALITY and (pos[k] in _COP_STOP or (pos[k] == "PART" and lows[k] == "to")):
            break
    if cons:
        f = _fronted_predicate(toks, pos, i)
        if f is not None:
            return f
        if all(pos[k] == "PUNCT" for k in range(i + 1, n)):
            # (frontl) A STRANDED COPULA'S PREDICATE IS TO ITS LEFT, PAST ITS SUBJECT: "how RELIABLE that is",
            # "whatever AGE you are".  `copular_available` already encodes that the slot is NOT free there (pri 110
            # phase 7); pri 110 only needed that fact, the event needs to know WHICH token holds it.
            seen_subj = False
            for k in range(i - 1, -1, -1):
                p = pos[k]
                if p in _CLAUSE_EDGE or (p == "PUNCT" and lows[k] in _HARD_STOP):
                    break
                if p in ("PUNCT", "PART") or lows[k] in _PS_NEG:
                    continue
                if not seen_subj and p in ("NOUN", "PROPN", "PRON", "DET", "NUM"):
                    seen_subj = True; continue
                if seen_subj and p in ("ADJ", "NOUN", "PROPN", "ADV", "NUM"):
                    return k
                if p in ("VERB", "AUX"):
                    break
            return None
    skip_subject = cons and _cop_inverted(pos, lows, i)
    seen_nominal = False; opened = False
    k = i
    while True:
        k += 1
        if k >= n:
            break
        if cons and pos[k] == "DET":
            opened = True
        if pos[k] == "PUNCT":
            # (paren) A PARENTHETICAL IS NOT THE COMPLEMENT AND NOT THE END OF THE CLAUSE: "This statement is ,
            # despite its facade of fair - mindedness , so many weasel words ."  `copular_available` already knows
            # the complement is behind such a boundary (pri 110 10b, its `crossed` flag); the complement scan
            # stopped at it.  Skip the WHOLE aside -- comma to matching comma -- so the scan neither stops at it
            # nor wanders into it.
            if cons and lows[k] == "," and not seen_nominal:
                j = k + 1
                while j < n and not (pos[j] == "PUNCT" and lows[j] in (",", ".", "!", "?", ";")):
                    j += 1
                if j < n and lows[j] == ",":
                    k = j
                    continue
            if cons and lows[k] in ('"', "'", "``", "''", "(") and not seen_nominal:
                continue
            break
        if pos[k] == "VERB" and not (cons and opened):
            break
        if cons and pos[k] in _CLAUSE_EDGE:
            break                                           # (clause) the complement is CLAUSE-LOCAL
        if cons and pos[k] == "ADV" and not seen_nominal and lows[k] in LOCATIVE_ADV:
            if k + 1 < n and pos[k + 1] == "ADP":           # (pploc) a COMPLEX locative: "i am OUT OF TOWN"
                for m in range(k + 2, n):
                    if pos[m] in ("NOUN", "PROPN", "PRON", "NUM"):
                        e = _np_run_end(toks, pos, m)
                        hs = [q for q in range(m, e + 1) if pos[q] in ("NOUN", "PROPN")]
                        return hs[-1] if hs else m
                    if pos[m] in ("VERB", "PUNCT") or pos[m] in _CLAUSE_EDGE:
                        break
            return k                                        # (loc) "the economy is DOWN", "he is HERE"
        if cons and pos[k] in ("ADV", "PRON", "DET") and lows[k] in WH_PRED and not seen_nominal:
            return k                                        # (wh) a WH-form predicate: "Which is WHY he said it"
        if cons and pos[k] in ("SYM", "INTJ") and not seen_nominal:
            return k                                        # (sym) a PRICE or a CODE predicates: "is $ 30 an entree"
        if pos[k] in ("ADJ", "NOUN", "PROPN", "PRON", "NUM"):
            if skip_subject and not seen_nominal:
                seen_nominal = True                         # (inv) that was the INVERTED SUBJECT; keep looking
                _np_run_end(toks, pos, k)
                continue
            if pos[k] == "PRON":
                return k
            j = _np_run_end(toks, pos, k)
            heads = [m for m in range(k, j + 1) if pos[m] in ("NOUN", "PROPN")]
            if heads:
                return heads[-1]
            adjs = [m for m in range(k, j + 1) if pos[m] in ("ADJ", "NUM")]
            return adjs[-1] if adjs else k
    if not cons:
        return None
    for k in range(i + 1, n):                               # the LOCATION fallback (bare ADV / ADP phrase)
        if pos[k] == "VERB" or pos[k] == "PUNCT" or pos[k] in _CLAUSE_EDGE:
            break
        if pos[k] == "ADV" and lows[k] in LOCATIVE_ADV:
            return k
        if pos[k] == "ADP":
            for m in range(k + 1, n):
                if pos[m] in ("NOUN", "PROPN", "PRON", "NUM"):
                    j = _np_run_end(toks, pos, m)
                    hs = [q for q in range(m, j + 1) if pos[q] in ("NOUN", "PROPN")]
                    return hs[-1] if hs else m
                if pos[m] in ("VERB", "PUNCT"):
                    break
            break
    return None


def predicate_complements(toks: Sequence[str], pos: Sequence[str]) -> set:
    """The 1-based indices that hold their clause's predicate slot WITHOUT being tagged VERB/AUX -- the non-verbal
    predicate a copula carries tense for.  Arc-free (toks + pos only), so the ROLE competition can read it."""
    out = set()
    if "AUX" not in set(pos) and not any(t.lower() in COP_FORMS for t in toks):
        return out
    for i in range(len(pos)):
        q = cop_complement(toks, pos, i)
        if q is not None and pos[q] not in ("VERB", "AUX"):
            out.add(q + 1)
    return out


def predicate_sites(toks: Sequence[str], tags: Sequence[str], post, tag_names: Sequence[str]) -> dict:
    """P(this token occupies its clause's predicate slot), per 0-based token, for EVERY predicate -- verbal and
    non-verbal.  GRADED both ways (pri 110's lesson): the verbal site carries the category organ's own P(VERB) and
    the complement site carries (1 - host_belief) * copular_available, so a consumer can weight an uncertain
    predication instead of committing it.  Returns {} under a category inventory lacking the UPOS classes this
    computation reads (the pri-15 induced-class swap and the Penn-tagset temporal instance must degrade to silence,
    not to an exception -- the guard pri 110 learned the hard way)."""
    sites = {}
    if post is None or len(toks) == 0 or any(t not in tag_names for t in _PS_NEEDED):
        return sites
    vi = tag_names.index("VERB")
    for i in range(len(toks)):
        if tags[i] == "VERB":
            sites[i] = float(post[i][vi])
    for i in range(len(toks)):
        if tags[i] != "AUX" or toks[i].lower() not in COP_FORMS:
            continue
        ca = copular_available(toks, tags, i)
        if ca <= 0.0:
            continue
        q = cop_complement(toks, tags, i)
        if q is None and PREDICATION_CONSTRUCTIONS and all(tags[k] == "PUNCT" for k in range(i + 1, len(toks))):
            # (ellip) THE COMPLEMENT IS ELIDED and no token carries it -- "i am sure they ARE .",
            # "more miserable than it 's ever BEEN".  The predication still happened, and the stranded auxiliary is
            # its surface residue (Hankamer & Sag 1976), so the copula is the only token that can carry the
            # eventuality.  NARROWED to the TRULY stranded configuration: fired whenever the complement scan merely
            # failed it was 31 extra fires for 2 clauses and took participant precision 0.8367 -> 0.8177,
            # CI-separated DOWN (measured, --ablate).
            q = i
        if q is None or q in sites:
            continue
        s = (1.0 - host_belief(toks, tags, post, tag_names, i)) * ca
        if s > sites.get(q, 0.0):
            sites[q] = s
    return sites



# ---------------------------------------------------------------- THE COPULA IS THE TENSE CARRIER (pri 113)
# `temporal_model.extract_events` skips every AUX lemma and the tense-preserving detector assigns a Reichenbach
# triple only to UPOS==VERB, so a copular clause carried NO tense at all: "she WAS a doctor" and "she IS a doctor"
# were the same record downstream.  Carrying the tense of a predication that is not itself finite is the copula's
# ONE job (Pustet 2003; Bybee 1994 on auxiliation) -- it is the reason English inserts it -- so the tense of a
# non-verbal predication is read off the CARRIER.  Labels match `situation_reader._stock_tense` so the two event
# streams are comparable.  Coverage on UD-EWT test 700: 0 -> 0.8084 of the non-verbal clauses (measured).
_PAST_COP = frozenset({"was", "were", "been"})
_PRES_COP = frozenset({"is", "are", "am", "'s", "'re", "'m", "s", "re", "m", "be", "being",
                       "become", "becomes", "seem", "seems"})
_PAST_LEX = frozenset({"became", "seemed"})
_FUT_AUX = frozenset({"will", "'ll", "ll", "wo", "shall"})
_MODAL_AUX = frozenset({"would", "can", "could", "may", "might", "must", "should"})


def copula_tense(toks: Sequence[str], pos: Sequence[str], i: int) -> str:
    """The stock tense label a copular predication inherits from its CARRIER at 0-based i."""
    lows = [t.lower() for t in toks]
    w = lows[i]; prev = None
    for k in range(i - 1, max(-1, i - 4), -1):
        if pos[k] in ("ADV", "PART", "PUNCT") or lows[k] in _PS_NEG:
            continue
        prev = lows[k]
        break
    if w == "been" and prev in ("had", "'d"):
        return "PAST_PERFECT"
    if prev in _FUT_AUX:
        return "FUTURE"
    if prev in _MODAL_AUX:
        return "MODAL_SUBORDINATE"
    if w in _PAST_COP or w in _PAST_LEX:
        return "SIMPLE_PAST"
    if w in _PRES_COP:
        return "SIMPLE_PRESENT"
    return "OTHER"


def predicate_site_carriers(toks: Sequence[str], tags: Sequence[str], post, tag_names: Sequence[str]) -> dict:
    """{predicate site -> the 0-based copula carrying its tense}.  The same loop as predicate_sites."""
    out = {}
    if post is None or len(toks) == 0 or any(t not in tag_names for t in _PS_NEEDED):
        return out
    verbal = set(i for i in range(len(toks)) if tags[i] == "VERB")
    for i in range(len(toks)):
        if tags[i] != "AUX" or toks[i].lower() not in COP_FORMS:
            continue
        if copular_available(toks, tags, i) <= 0.0:
            continue
        q = cop_complement(toks, tags, i)
        if q is None and PREDICATION_CONSTRUCTIONS and all(tags[k] == "PUNCT" for k in range(i + 1, len(toks))):
            q = i
        if q is None or q in verbal or q in out:
            continue
        out[q] = i
    return out


# ------------------------------------------------------------------- THE SECOND CUE TO THE SAME PREDICATE (pri 113)
# `cop_complement` above is a SURFACE cue -- a construction read off word order and closed-class forms.  The heads
# rung supplies an INDEPENDENT structural one: a copula attaches TO its predicate, and the landed copular state
# reader (`hdlab.copular_binding.robust_cop`) already reads exactly that off the tree.  Measured, the two cues see
# overlapping but not identical sets (98 shared, 20 surface-only, 10 arc-only of the 167).
# THE BRAIN.  Multiple-cue integration (Christiansen & Chater 2001) with RELIABILITY WEIGHTING (Ernst & Banks 2002;
# Ma-Beck-Latham-Pouget 2006: a downstream area weights each input by its reliability, trial by trial) -- and the
# reliability of "this arc names the predicate" is the governor's OWN posterior on that arc, the same quantity
# tools/build_coarse_role_validities.py already uses as its teaching weight.  A RAW UNION costs participant
# precision 0.8370 -> 0.8076, CI-separated DOWN; gating on the reliability recovers almost all of the recall at no
# CI-separated precision cost, and the operating point is FLAT (measured, --arcgrade):
#     tau   recall  precision  F1      on the 167   d(precision) vs the live floor
#     0.00  0.9659  0.8076     0.8797  0.8623       -0.0282 CI[-0.0386,-0.0171]  SEPARATED DOWN
#     0.10  0.9646  0.8320     0.8934  0.8563       -0.0038 CI[-0.0118,+0.0041]  not separated
#     0.50  0.9633  0.8332     0.8935  0.8503       -0.0026 CI[-0.0108,+0.0051]  not separated
#     0.90  0.9593  0.8341     0.8924  0.8323       -0.0016 CI[-0.0099,+0.0058]  not separated
#     off   0.9541  0.8370     0.8917  0.8084       +0.0012 CI[-0.0059,+0.0079]
# The PUREST form of the arc cue (the copula's own MAP head, no fallback chain) is WORSE at every threshold
# (tau 0.5: precision 0.8274 against 0.8332), so `robust_cop`'s gated fallback is carrying real signal.
# DEFAULT OFF, AND THE REASON IS A REVERSAL I HAVE TO RECORD.  It was flipped ON on the strength of a CAPPED board
# A/B in which six of seven dimensions were +0.0000 EXACTLY.  The FULL-SIZE A/B then landed and disagreed: on the
# uncapped board the event arm is DOWN on coref (0.4172 -> 0.4153, n=3145), on who_did_what_patient
# (0.8151 -> 0.8104, n=1255) and on state (0.7487 -> 0.7460, n=378), aggregate 0.6191 -> 0.6185.  Those movements
# are 6, 6 and 1 items and are INVISIBLE at the capped sizes (n=504 / 241 / 73) -- i.e. the capped board was
# UNDERPOWERED and I treated it as decisive.  The coordinator's condition for the default was "if it is not down
# anywhere"; at full size it is down somewhere, so the condition fails and the default goes back to 0.
# WHAT IS STILL TRUE: tau 0.5 takes the 167 from 0.8383 to 0.8743 in supply and GUM's 366 from 0.6120 to 0.6257 out
# of supply, at a participant-precision delta whose CI contains zero in supply and is unchanged out of it.
# WHAT IS NEEDED TO TURN IT ON: a FULL-SIZE `--board-ab --full` of the SHIPPED configuration (constructions + arc
# cue + the state consolidation, which the full run above did NOT include and which is itself +0.0370
# CI[+0.0186,+0.0571] on state).  Set HDLAB_PREDICATION_ARC_TAU=0.5 to measure it.
PREDICATION_ARC_TAU = float(os.environ.get("HDLAB_PREDICATION_ARC_TAU", "0"))


def arc_predicate_sites(toks: Sequence[str], tags: Sequence[str], heads, head_posterior, tau: float = None) -> dict:
    """{0-based predicate index -> P(the copula attaches to it)} from the ARC cue, gated at `tau`.
    Reads the landed copular state reader's own detection (ONE organ owns the arc read) and weights each site by
    the heads rung's own posterior on the copula's arc.  Returns {} if tau <= 0 or anything is unavailable."""
    tau = PREDICATION_ARC_TAU if tau is None else float(tau)
    out = {}
    if tau <= 0.0 or not heads or not head_posterior:
        return out
    try:
        from hdlab.copular_binding import robust_cop
        pairs = robust_cop(list(toks), list(tags), heads, gate=True)
    except Exception:
        return out
    lows = [t.lower() for t in toks]
    for (_h, pr) in pairs:
        if not (0 <= pr < len(tags)) or tags[pr] in ("VERB", "AUX"):
            continue
        best = 0.0
        for c in range(len(toks)):
            if tags[c] != "AUX" or lows[c] not in COP_FORMS or abs(c - pr) > 6:
                continue
            best = max(best, float((head_posterior.get(c + 1) or {}).get(pr + 1, 0.0)))
        if best >= tau and best > out.get(pr, 0.0):
            out[pr] = best
    return out


# ------------------------------------------------------- ONE STRUCTURE PER CLAUSE: the state reader's own pairs
# `situation_reader._read_entity_states` detects its (HOLDER, PROPERTY) pairs with `copular_binding.robust_cop`, a
# SECOND, independent predicate finder for the same clause.  Measured on UD-EWT test 700: where both organs name
# the gold predicate they AGREE 97 times; where they differ the PREDICATE-SLOT read is right 20 times and the state
# reader 9 -- so the right consolidation is a UNION (the 9 are real), not a replacement.  ONE eventuality per clause
# whose SORT is read off the predicate's own category (Maienborn 2005) is the brain-foundational form.
# MEASURED, board A/B with both arms back-to-back in one process, the state dimension at FULL size:
#     state 0.7487 -> 0.7857  (+0.0370, 14 items of 378; its own floor is 0.5714)
#     every other dimension +0.0000; aggregate 0.6290 -> 0.6359
# and the event/state disagreements 29 -> 20, of which 9 are cases the state reader gets RIGHT, so the true
# residual is 11 -- and its cause is `robust_cop`'s HOLDER scan, not the predicate read.
# HDLAB_STATE_FROM_PREDICATE_SLOT=0 restores the shipped detection exactly.
STATE_FROM_PREDICATE_SLOT = os.environ.get("HDLAB_STATE_FROM_PREDICATE_SLOT", "1") == "1"


def state_pairs_from_slot(toks: Sequence[str], tags: Sequence[str], post, tag_names: Sequence[str]) -> set:
    """(HOLDER, PROPERTY) pairs, 0-based, for every predicate-slot site the copular state reader would miss.
    The HOLDER is recovered by `robust_cop`'s own rule -- the nearest nominal preceding the licensing copula -- so
    only the PROPERTY set is consolidated and the holder logic is untouched."""
    out = set()
    if not STATE_FROM_PREDICATE_SLOT:
        return out
    lows = [t.lower() for t in toks]
    for q in predicate_sites(toks, tags, post, tag_names):
        if tags[q] == "VERB":
            continue
        c = None
        for k in range(q - 1, max(-1, q - 8), -1):
            if tags[k] == "AUX" and lows[k] in COP_FORMS:
                c = k
                break
        start = c if c is not None else q
        hold = None
        for k in range(start - 1, -1, -1):
            if tags[k] in ("NOUN", "PROPN", "PRON"):
                hold = k
                break
            if tags[k] in ("VERB", "PUNCT"):
                break
        if hold is not None:
            out.add((hold, q))
    return out



def subordination(toks: Sequence[str], pos: Sequence[str], i: int) -> str:
    """SUBORDINATION CUE: the clause-dependency marking in force at 1-based i -- the nearest preceding clause opener
    (subordinator / relativizer / coordinator) with no finite predicate in between (a VERB or a sentence-final mark
    closes the search).  A complementizer marks its clause DEPENDENT (Diessel 2004)."""
    lows = [t.lower() for t in toks]
    for k in range(i - 1, 0, -1):
        p = pos[k - 1]; w = lows[k - 1]
        if p == "VERB":
            return "none"
        if p == "PUNCT" and w in SENT_END:
            return "none"
        if p == "SCONJ":
            return "sconj"
        if p in ("PRON", "DET", "ADV") and w in WH_FORMS:
            return "wh"
        if p == "CCONJ":
            return "cc"
    return "none"


def assertion_candidates(toks: Sequence[str], pos: Sequence[str], cop=None) -> List[int]:
    """The set the main-assertion competition runs over: every VERB, every copular predicate, and -- in a VERBLESS,
    copula-less utterance, which still asserts (a headline, a list item, a signature, a price) -- the content heads
    of its phrases.  Measured: without the fragment clause, 47 of 169 remaining root misses were fragment heads that
    the rank cue was PENALISING for not being candidates at all."""
    n = len(pos); cop = cop_predicates(toks, pos) if cop is None else cop
    has_verb = any(p == "VERB" for p in pos)
    cand = [j for j in range(1, n + 1)
            if pos[j - 1] == "VERB" or j in cop or (pos[j - 1] == "AUX" and not has_verb)]
    if cand:
        return cand
    heads = [j for j in range(1, n + 1)
             if pos[j - 1] in ("NOUN", "PROPN") and (j == n or pos[j] not in ("NOUN", "PROPN"))]
    return heads or [j for j in range(1, n + 1) if pos[j - 1] in CONTENT or pos[j - 1] == "INTJ"]


def root_cue_values(toks: Sequence[str], pos: Sequence[str]) -> List[Optional[Dict[str, str]]]:
    """The ROOT-configuration cue values per 1-based token (index 0 unused).  Tokens + categories only.
      rpred  a verbal candidate's finiteness class, or a non-verbal candidate's predication status: "cop" (a copula
             makes it the predicate), "nov" (no verb in the sentence at all -- a legitimate fragment root), "hasv"
             (a verb exists elsewhere, so a bare nominal is a poor main assertion);
      rsub   the clause-dependency marking in force ("sconj" / "wh" / "cc" / "none");
      rpos   rank among the assertion candidates ("1" / "2" / "3" / "x") x a nominal to the left with no predicate
             in between ("S") -- the Competition Model's word-order cue."""
    n = len(pos); cop = cop_predicates(toks, pos)
    has_verb = any(p == "VERB" for p in pos)
    cand = assertion_candidates(toks, pos, cop)
    rank = {j: min(k + 1, 3) for k, j in enumerate(cand)}
    last_cand = cand[-1] if cand else None
    out: List[Optional[Dict[str, str]]] = [None] * (n + 1)
    for j in range(1, n + 1):
        p = pos[j - 1]
        if p in ("VERB", "AUX"):
            rpred = finiteness(toks, pos, j)
        elif j in cop:
            rpred = "cop"
        else:
            rpred = "hasv" if has_verb else "nov"
        subj = False
        for k in range(j - 1, 0, -1):
            if pos[k - 1] == "VERB":
                break
            if pos[k - 1] in NOMINAL or pos[k - 1] == "NUM":
                subj = True; break
        if CONJ_RPRED and rpred in ("ed", "base"):
            # CONJUNCTIVE FINITENESS: a bare "ed" conflates a finite past with a bare participle (148 vs 65 of 967
            # test VERB tokens) and a bare "base" a finite present with an infinitive (146 vs 46) -- the same cue
            # value for OPPOSITE predication status. Neither subject support nor rank alone separates them ("the man
            # SEEN yesterday LEFT" and "the man WALKED home" have both); what does is rank PLUS whether a later
            # assertion candidate exists at all: seen -> ed1x, walked -> ed1L.
            rpred = rpred + ("%d" % (rank.get(j) or 0)) + ("L" if j == last_cand else "x")
        r = rank.get(j)
        out[j] = {"rpred": rpred, "rsub": subordination(toks, pos, j),
                  "rpos": ("%d" % r if r else "x") + ("S" if subj else "")}
    return out


PREDICATION_GAMMA = float(os.environ.get("HDLAB_ARM_PREDICATION_GAMMA", "8.0"))   # swept 0/2/4/8/16; never adopted


def predication_boost(A: "np.ndarray", toks: Sequence[str], pos: Sequence[str], g_cop: float = None,
                      g_sub: float = None, g_fin: float = None) -> "np.ndarray":
    """ACQUISITION signal (used by tools/build_attachment_validities.py on the teacher's score matrix, NOT at read
    time) -- the analogue of `parallelism_boost`.  MEASURED GAP: the teacher's root row is beta*(best subject fit +
    best object fit) for a VERB and a flat -1.5 for everything else, so its posterior mass on a gold ADJECTIVAL root
    arc was 0.001 (100% below 0.05 over 400 test sentences; ADV 0.000, PRON 0.000) -- the copular cue had nothing
    to learn a validity from.  Predication + dependency marking, treebank-free: a copular predicate CARRIES the
    assertion (boost its root arc); a subordinator/relativizer-marked predicate is DEPENDENT (penalise); a
    to-infinitival or bare participial verb is NOT finite (penalise).  gammas are a SWEPT operating point.
    Measured effect on the learned validities: ROOT:ADJ|cop +3.47 -> +4.35, ROOT:VERB|sconj -0.74 -> -1.42."""
    g_cop = PREDICATION_GAMMA if g_cop is None else g_cop
    g_sub = PREDICATION_GAMMA if g_sub is None else g_sub
    g_fin = PREDICATION_GAMMA if g_fin is None else g_fin
    n = len(pos); B = A.copy(); cop = cop_predicates(toks, pos)
    for j in range(1, n + 1):
        if not np.isfinite(B[0][j]):
            continue
        rpred = finiteness(toks, pos, j) if pos[j - 1] in ("VERB", "AUX") else ("cop" if j in cop else "")
        d = 0.0
        if rpred == "cop":
            d += g_cop
        if subordination(toks, pos, j) in ("sconj", "wh"):
            d -= g_sub
        if rpred in ("to", "ing"):
            d -= g_fin
        B[0][j] += d
    return B


BOUNDARY_GAMMA = float(os.environ.get("HDLAB_ARM_BOUNDARY_GAMMA", "4.0"))   # swept 0/2/4/8; never adopted


def boundary_penalty(A: "np.ndarray", toks: Sequence[str], pos: Sequence[str], g_clause: float = None,
                     g_np: float = None) -> "np.ndarray":
    """ACQUISITION signal (used by tools/build_attachment_validities.py on the teacher's score matrix, NOT at read
    time) -- the analogue of `parallelism_boost` and `predication_boost` for pri-105's two computations.  The
    knowledge-free teacher is locality + semantic plausibility: it has no notion of a clause or a phrase, so a
    noun's posterior mass is spread over every nearby verb whatever stands between them, and the two new cues have
    little contrast to learn a validity from.  Here the teacher is given the same two facts the child's first-stage
    parser has -- integrate inside the clause (Frazier & Fodor 1978; Gibson DLT) and a determiner opens a new phrase
    (Shi & Melancon 2010) -- as a PENALTY on crossing arcs.  Treebank-free (categories + position only); gammas are
    SWEPT operating points.
    REFUTED AS BUILT (2026-09-13, gamma 4, train 1500, UD-EWT test 700, same floor and seed as the read-time arm):
    it makes the end number slightly WORSE -- in-order UAS 0.6397 -> 0.6256 and core-argument arcs 0.7834 -> 0.7817;
    search UAS 0.6309 -> 0.6176, core 0.7801 -> 0.7751.  It does what it is for (root 0.774 -> 0.781, obl 0.428 ->
    0.463, ccomp 0.698 -> 0.716) and pays for it where the teacher needs long arcs it now penalises (nmod 0.506 ->
    0.405, obj 0.787 -> 0.775, compound 0.509 -> 0.484).  Same shape as pri-97's predication boost: the arm
    self-teaches for 2-3 rounds at alpha 0.8, so its own posterior dominates and a blanket teacher correction is
    re-absorbed -- while the collateral damage to legitimate crossing arcs is not.  KEPT AS AN UNCALLED, DOCUMENTED
    FUNCTION (the convention this module already uses for ROOT_CUE_CENTER and OCCUPANCY); a future attempt should
    penalise only the configurations whose learned validity is already negative, not every crossing arc."""
    g_clause = BOUNDARY_GAMMA if g_clause is None else g_clause
    g_np = BOUNDARY_GAMMA if g_np is None else g_np
    n = len(pos); B = A.copy()
    nv, sb = clause_matrices(toks, pos); V = npb_matrix(toks, pos)
    for j in range(1, n + 1):
        for h in range(1, n + 1):
            if h == j or not np.isfinite(B[h][j]):
                continue
            d = 0.0
            if g_clause:
                d -= g_clause * (float(nv[h][j - 1]) + float(sb[h][j - 1]))
            if g_np and V[h][j - 1] == 2:
                d -= g_np
            B[h][j] += d
    return B


class SentenceCues:
    """ONE cue pass per sentence (shared by every arc): punctuation cumsum for boundaries, construction map, verb lemmas."""

    def __init__(self, toks: Sequence[str], pos: Sequence[str], frames: Dict[str, List[int]],
                 pp_assoc: Optional[Dict[str, Dict[str, float]]] = None,
                 pp_assoc_v2: Optional[Dict[str, object]] = None, occ=None):
        self.toks = list(toks); self.pos = list(pos); self.n = len(toks); self.frames = frames
        self.cum = np.concatenate([[0], np.cumsum([1 if p == "PUNCT" else 0 for p in self.pos])])
        self.constr = construction_map(self.toks, self.pos)
        self.lem = [lemma_verb(t).lower() if p == "VERB" else None for t, p in zip(self.toks, self.pos)]
        self.teacher = _plaus_teacher() if PLAUS_CUE else None
        self.rootcues = root_cue_values(self.toks, self.pos)     # MAIN-ASSERTION cues (one pass; read at h == 0)
        self.csub = csub_sites(self.toks, self.pos) if CSUB_CUE else {}
        # THE PREDICATE SLOT AS A GRADED ARC FEATURE (pri 117): the occupancy the categories rung already computes,
        # delivered to the competition as a cue VALUE whose validity is learned (pri 113 section 27 -- the signal
        # existed upstream and was handed down only as a TAG).  `occ` absent => the graded cue is silent.
        self.occ = occ
        self.csubg = csub_graded_sites(self.toks, self.pos, occ) if (CSUBG_CUE and occ is not None) else {}
        self.clause = clause_matrices(self.toks, self.pos) if CLAUSE_CUE else None   # (predicates, opener) crossed
        self.npb = npb_matrix(self.toks, self.pos) if NPB_CUE else None              # phrase membership
        # PP ATTACHMENT (v2): the case-marked nominals and their retrieved candidate hosts, when the table carries the
        # mined association. The legacy two-candidate `self.pp` path stays for a table that only has `pp_assoc`.
        self.pp_arc: Dict[Tuple[int, int], str] = {}
        self.ppobj_arc: Dict[Tuple[int, int], str] = {}
        self.pp_cased: set = set()
        if pp_assoc_v2:
            self.pp_arc, self.ppobj_arc = pp_arc_values(self.toks, self.pos, pp_assoc_v2)
        if PP_CASE_RULE:
            self.pp_cased = pp_case_marked(self.toks, self.pos)
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
            d0 = self.rootcues[j]        # the ROOT configuration is a cue competition too, not a per-category prior
            if self.clause is not None:
                d0 = dict(d0); d0["clause"] = clause_value(int(self.clause[0][0][j - 1]), int(self.clause[1][0][j - 1]))
            return d0
        pj = self.pos[j - 1]; ph = self.pos[h - 1]; dr = "L" if h < j else "R"
        lo, hi = (h, j) if h < j else (j, h)
        nb = int(self.cum[hi - 1] - self.cum[lo])
        c = {"locality": f"{dr}{dist_bin(abs(h - j))}", "form": "formhead" if ph in FORM else "wordhead",
             "boundary": "0" if nb == 0 else "1" if nb == 1 else "2+",
             "constr": self.constr.get((h, j), "none")}
        site = self.pp.get(j)
        if site is not None and h in (site[0], site[1]):
            c["pp"] = ("V:" if h == site[0] else "N:") + site[2]     # which candidate this head is x the preposition's lean
        v2 = self.pp_arc.get((h, j))
        if v2 is not None:
            c["pp"] = v2                     # v2 REPLACES the two-candidate value when the mined association is present
            c["ppobj"] = self.ppobj_arc.get((h, j), "0")
        if self.teacher is not None and ph == "VERB" and pj in NOMINAL and not (j >= 2 and self.pos[j - 2] == "ADP"):
            # v2 (07:20): CORE slots only -- a case-marked (prepositional) nominal is oblique, and its host is the PP cue's business;
            # v1 fired on PP objects too and traded obl 0.468 -> 0.379 for nmod 0.311 -> 0.375.
            c["plaus"] = ("S:" if h > j else "O:") + _plaus_bin(self.teacher.slot_plausibility(self.toks, self.pos, h, j))
        if self.csub:
            v = self.csub.get((h, j))
            if v is not None:
                c["csub"] = v                 # the copular predicate vs a later verb, for the SUBJECT
        if self.csubg:
            v = self.csubg.get((h, j))
            if v is not None:
                c["csubg"] = v                # the same arcs x HOW STRONGLY this head holds the predicate slot
        if self.clause is not None:
            c["clause"] = clause_value(int(self.clause[0][h][j - 1]), int(self.clause[1][h][j - 1]))
        if self.npb is not None:
            v = int(self.npb[h][j - 1])
            if v:
                c["npb"] = NPB_VALUES[v]      # the two nominals are in one phrase, or a determiner separates them
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
           "pp_assoc_v2": doc.get("pp_assoc_v2"), "strength": strengths_from_arc_counts(doc["counts"])}
    if path is None:
        _TABLE = tab
    return tab


def save_attachment_validities(path: Optional[str] = None, table: Optional[Dict[str, object]] = None) -> str:
    tab = table or load_attachment_validities(); p = path or ASSET
    doc = {"source": "attachment arm of the Competition-Model organ: soft arc counts accrued from reading (knowledge-free teacher + "
                     "anchored self-teaching; no treebank, no hand prior); strengths = attachment_arm.strengths_from_arc_counts",
           "counts": tab["counts"], "frames": tab.get("frames", {}), "pp_assoc": tab.get("pp_assoc"),
           "pp_assoc_v2": tab.get("pp_assoc_v2")}
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
    tab = table or load_attachment_validities(); sc = SentenceCues(toks, pos, tab.get("frames", {}), tab.get("pp_assoc"), tab.get("pp_assoc_v2"))
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


def arc_scores(toks: Sequence[str], pos: Sequence[str], table: Optional[Dict[str, object]] = None,
               occ=None) -> Tuple[np.ndarray, int]:
    """Additive cue activation per arc (row = head incl. 0 = ROOT, col = dependent); form classes never head or root.
    `occ` (pri 117) = P(this token holds its clause's predicate slot) per 0-based token -- the categories rung's own
    graded read; with it the copular-subject cue competes with a graded value instead of a categorical one.
    Vectorised; numerically identical to `arc_scores_reference` (witness: verification/test_attachment_arm_fastpath.py)."""
    if not _ARC_FAST:
        return arc_scores_reference(toks, pos, table, occ)
    tab = table or load_attachment_validities(); ix = _arc_index(tab)
    sc = SentenceCues(toks, pos, tab.get("frames", {}), tab.get("pp_assoc"), tab.get("pp_assoc_v2"), occ=occ); n = sc.n
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
    # PP cue v2 (sparse: <= PP_KCAP cells per case-marked nominal, both channels)
    for _cue, _arcs in (("pp", sc.pp_arc), ("ppobj", sc.ppobj_arc)):
        _T = ix.cue_tab.get(_cue)
        if _T is None or not _arcs:
            continue
        _vid = ix.val_id[_cue]
        for (h, j), val in _arcs.items():
            if 1 <= h <= n and 1 <= j <= n:
                S[h, j - 1] += _T[C[h, j - 1], _vid.get(val, 0)]
    # PP cue (sparse sites)
    if sc.pp and not sc.pp_arc and "pp" in ix.cue_tab:
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
    # MAIN-ASSERTION cues on the root row (n cells; `arc_scores_reference` picks them up from sc.cues(j, 0))
    rc = sc.rootcues; row0 = C[0]; d = np.zeros(n)
    for cue in ROOT_CUES:
        T = ix.cue_tab.get(cue)
        if T is None:
            continue
        vid = ix.val_id[cue]
        for j in range(1, n + 1):
            v = rc[j].get(cue)
            if v is not None:
                d[j - 1] += T[row0[j - 1]][vid.get(v, 0)]
    live = np.isfinite(S[0]) & ~np.array([p in FORM for p in pos])
    if ROOT_CUE_CENTER and live.any():
        d -= float(d[live].mean())
    S[0] += d
    if sc.csub and "csub" in ix.cue_tab:
        vid = ix.val_id["csub"]; T = ix.cue_tab["csub"]
        for (h, j), v in sc.csub.items():
            if 1 <= h <= n and 1 <= j <= n:
                S[h, j - 1] += T[C[h, j - 1]][vid.get(v, 0)]
    if sc.csubg and "csubg" in ix.cue_tab:
        vid = ix.val_id["csubg"]; T = ix.cue_tab["csubg"]
        for (h, j), v in sc.csubg.items():
            if 1 <= h <= n and 1 <= j <= n:
                S[h, j - 1] += T[C[h, j - 1]][vid.get(v, 0)]
    # CLAUSE MEMBERSHIP + CONSTITUENCY (pri-105): dense adds over the same grid
    if sc.clause is not None and "clause" in ix.cue_tab:
        nv, sb = sc.clause; vid = ix.val_id["clause"]
        lut = np.array([[vid.get(clause_value(v, b), 0) for b in (0, 1)] for v in range(CLAUSE_MAXV + 1)], dtype=np.int64)
        S += ix.cue_tab["clause"][C, lut[nv, sb]]
    if sc.npb is not None and "npb" in ix.cue_tab:
        vid = ix.val_id["npb"]
        lut = np.array([0] + [vid.get(v, 0) for v in NPB_VALUES[1:]], dtype=np.int64)
        S += ix.cue_tab["npb"][C, lut[sc.npb]]
    # masks: no self-arcs, form classes never head, form classes never root when a word exists
    A = np.full((n + 1, n + 1), -np.inf); A[:, 1:] = S
    A[np.arange(1, n + 1), np.arange(1, n + 1)] = -np.inf
    A[1:, :][is_form, :] = -np.inf
    if not is_form.all():
        A[0, 1:][is_form] = -np.inf
    return A, n


def arc_scores_reference(toks: Sequence[str], pos: Sequence[str], table: Optional[Dict[str, object]] = None,
                         occ=None) -> Tuple[np.ndarray, int]:
    """THE REFERENCE readout (the original per-pair loop): additive cue activation per arc (row = head incl. 0 = ROOT, col =
    dependent); form classes never head or root. Kept as the oracle for the vectorised `arc_scores`."""
    tab = table or load_attachment_validities(); st = tab["strength"]; sc = SentenceCues(toks, pos, tab.get("frames", {}), tab.get("pp_assoc"), tab.get("pp_assoc_v2"), occ=occ)
    n = sc.n; A = np.full((n + 1, n + 1), -np.inf)
    words = [j for j in range(1, n + 1) if pos[j - 1] not in FORM]
    for j in range(1, n + 1):
        for h in range(0, n + 1):
            if h == j or (h and pos[h - 1] in FORM):
                continue
            if h == 0 and pos[j - 1] in FORM and words:
                continue
            cfg = sc.config(j, h); s = st["cfg"].get(cfg, 0.0)
            cues = sc.cues(j, h)
            if sc.pp_arc and "pp" in cues and (h, j) not in sc.pp_arc:
                # PP CUE, SENTENCE-WIDE GATE (ported from `arc_scores`, which never runs the legacy two-candidate PP
                # cue once the mined v2 association (`pp_arc`) fires ANYWHERE in the sentence -- `SentenceCues.cues`
                # only sees this one pair and falls back to the legacy site-based value for pairs `pp_arc` skipped).
                del cues["pp"]
            for c, v in cues.items():
                s += st.get(c, {}).get(cfg + "|" + v, 0.0)
            if CONVENTION_BONUS and h and sc.constr.get((h, j)) == "fw":
                s += CONVENTION_BONUS
            A[h][j] = s
    if ROOT_CUE_CENTER:                 # the root slot has capacity one: read the main-assertion cues as a competition
        live = [j for j in range(1, n + 1) if np.isfinite(A[0][j])]
        if live:
            m = sum(A[0][j] - st["cfg"].get(sc.config(j, 0), 0.0) for j in live) / len(live)
            for j in live:
                A[0][j] -= m
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
    ''' The top of k's head chain inside [lo, hi].
    pri 117: hd.get(k) can be None -- `map_tree_single_root` leaves a word headless on some out-of-supply
    sentences, and `punct_convention` then raised
    `TypeError: '<=' not supported between instances of 'int' and 'NoneType'`, aborting a whole GUM run of the
    `map1` decode.  A MISSING head means the chain ENDS, which is exactly what 0 already means here, so this is a
    default rather than a new behaviour: the in-order decode is byte-identical and the search decodes stop
    raising (asserted in the solver cell's --self-test). '''
    top = k
    seen = 0
    while k is not None and lo <= k <= hi and seen <= len(hd) + 1:
        top = k; k = hd.get(k) or 0; seen += 1
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
                   temp: float = 1.0, occ=None) -> Dict[int, Dict[int, float]]:
    """The graded signal handed DOWN: exact single-root Matrix-Tree marginals P(head | dependent)."""
    A, n = arc_scores(toks, pos, table, occ); return _punct_posterior(toks, pos, single_root_marginals(A, n, temp))


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
# ROOT PICK, changed 2026-09-13 (solver pri-97) FROM "score" TO "left", and ONLY because the root row now carries
# evidence.  With the old 17-number root row every VERB tied, so "highest root score" meant "prefer a verb, else the
# leftmost" and scored 0.934 given the gold root was offered.  With the main-assertion cues the search decode's OFFER
# stage IMPROVES (gold root inside the unconstrained MAP root set 0.800 -> 0.807; mean root-set size 1.67 -> 1.29) but
# "highest root score" PICKS WORSE among the tree-filtered candidates (0.934 -> 0.867), because the validities are
# calibrated over all tokens, not over the subpopulation the tree already offered -- so the search decode lost
# (root 0.747 -> 0.700) while the in-order decode gained.  MEASURED, UD-EWT test 700, gold categories, cues on:
#   pick "score": root 0.7000 | pick "left" (the leftmost offered candidate; English asserts matrix-first): 0.7729,
#   i.e. +0.0257 CI [+0.0071, +0.0443] over the STRONGEST baseline (base + "score" 0.7471), UAS 0.6198 vs 0.6178.
# Without the cues "left" is WORSE than "score" (0.7200 vs 0.7471), so this flips only together with the cues.
# `incremental_tree` (HDLAB_ARM_DECODE=incr, the live default) never reads ROOT_PICK.
ROOT_PICK = os.environ.get("HDLAB_ARM_ROOT_PICK", "score")  # among several MAP roots: "score" (highest root score; the landed default -- pri 97's final report: at the landed cap 6000 the flip is NOT needed, search root 0.7486 with the decoder untouched) | "left" (leftmost offered; +0.04 search root on the powered arm only; selectable)


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


def hold_expectation(pos: Sequence[str], table: Optional[Dict[str, object]] = None, A: Optional[np.ndarray] = None,
                     toks: Optional[Sequence[str]] = None) -> np.ndarray:
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
    # FINITENESS-CONDITIONED HOLD (round 2): the value of waiting for a head still to come was conditioned on
    # category x verb-seen x subordinator-pending but NOT on finiteness -- so a to-infinitive and a tensed verb
    # predicted a governor to the right with identical strength, although a to-infinitive almost always HAS one to
    # its left and a tensed matrix verb has none (Levy 2008: the expectation is over what the grammar makes likely
    # next, and finiteness is the strongest thing the reader knows about a verb). Learned from the organ's OWN
    # trees, exactly like the rest of the table. MEASURED: NULL on its own (+0.0009 UAS, n.s.) and +0.0018 UAS /
    # +0.0028 root ON TOP of the main-assertion cues -- best UAS of the session (0.6263). HDLAB_ARM_HOLD_FINITENESS=0.
    tab4 = _HOLD_TAB.get("_fin", {}) if HOLD_FINITENESS else {}
    rc = root_cue_values(toks, pos) if (tab4 and toks is not None) else None
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
            if rc is not None:
                e4 = tab4.get(p, {}).get(k + ("s" if sub_pending else "") + "|" + rc[j]["rpred"])
                if e4 is not None:
                    e = e4
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
    acc4: Dict = defaultdict(lambda: defaultdict(list)); cnt4: Dict = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for toks, pos, _, _ in sentences(TRAIN, cap=cap, maxlen=60):
        A, n = arc_scores(toks, pos, tab); hd = map_tree_single_root(A, n); vs = False; sp = False
        rc4 = root_cue_values(toks, pos)
        for j in range(1, n + 1):
            p = pos[j - 1]; k = "1" if vs else "0"; h = hd.get(j)
            if h is None:
                continue
            k3 = k + ("s" if sp else "")
            k4 = k3 + "|" + rc4[j]["rpred"]
            if h > j and np.isfinite(A[h][j]):
                acc4[p][k4].append(float(A[h][j])); cnt4[p][k4][0] += 1
            cnt4[p][k4][1] += 1
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
    fin = {}
    for p in acc4:
        fin[p] = {}
        for k4 in cnt4[p]:
            r, t = cnt4[p][k4]
            if t >= 8:
                fin[p][k4] = (r / t) * (float(np.mean(acc4[p][k4])) if acc4[p][k4] else 0.0)
    expect["_fin"] = fin
    d = {"expect": expect, "cap": cap, "note": "P(right head | cat, verb_seen) x mean realised right-arc activation; organ's own map1 trees; _by_left: also conditioned on the category of the best left candidate"}
    with open(out, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1)
    return d
INCR_STATS = {"sentences": 0, "incomplete_words": 0, "words": 0, "last_incomplete": []}   # last_incomplete: indices repaired at wrap-up (last sentence)


def incremental_tree(A: np.ndarray, n: int, beam: int = INCR_BEAM, hold=INCR_HOLD,
                     temp: float = 1.0, pos_seq=None, wrap_at=None) -> Tuple[Dict[int, int], Dict[int, Dict[int, float]]]:
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
        # CLAUSE-CLOSE WRAP-UP TRIGGER (solver pri-105): the boundary a subordinator/complementiser/`to` OPENS is a
        # clause boundary too, and the reader integrates there (clause-final wrap-up, Just & Carpenter) -- before this
        # the trigger was punctuation or a coordinator only, so a word left waiting from the matrix clause was still
        # competing when the embedded clause's verb arrived.  `wrap_at` (from `decode`) is the same opener computation
        # the `clause` cue uses.  MEASURED alone on the live asset, no rebuild, UD-EWT test 700 in-order: core-argument
        # arcs 0.7784 -> 0.7842 (+0.0058 CI [+0.0017,+0.0104]), UAS 0.6239 -> 0.6258 (+0.0019 CI [+0.0004,+0.0036]),
        # root 0.777 -> 0.780, nsubj +0.005, obj +0.008; advcl -0.007 is the only give-back.
        _wrap = (bool(wrap_at[b - 1]) if wrap_at is not None
                 else (pos_seq is not None and pos_seq[b - 1] in ("PUNCT", "CCONJ")))
        if INCR_CLAUSE_WRAPUP and b < n and _wrap:
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
        hv = hold_expectation(pos, table, A if INCR_HOLD_MODE == "expect_left" else None, toks) + INCR_HOLD if INCR_HOLD_MODE != "const" else INCR_HOLD
        wrap_at = None
        if INCR_CLAUSE_WRAPUP and CLAUSE_WRAP_OPENER:
            _, _opn = predicate_flags(toks, pos)
            wrap_at = [bool(_opn[i]) or pos[i - 1] in ("PUNCT", "CCONJ") for i in range(1, len(pos) + 1)]
        hd, post = incremental_tree(A, n, INCR_BEAM, hv, temp, pos_seq=list(pos), wrap_at=wrap_at)   # module globals read at call time (sweepable)
    elif DECODE == "mbr":
        hd, post = mbr_tree(A, n, temp)
    elif DECODE == "map1":
        hd = map_tree_single_root(A, n); post = single_root_marginals(A.copy(), n, temp)
    else:
        hd = chu_liu_edmonds(A, n); post = single_root_marginals(A.copy(), n, temp)
    hd = occupancy_repair(toks, pos, hd, post)
    # PREDICATE-ARRIVAL REANALYSIS (pri 117): the in-order beam commits the subject of a clause whose predicate has
    # not arrived yet; when it does arrive the subject's attachment is revised, if the organ's OWN activations prefer
    # it (Frazier & Rayner 1982; the same accounting INCR_ROOT_REANALYSIS already applies to the root arc).
    hd = revise_copular_subject(toks, pos, A, hd)
    hd = punct_convention(toks, pos, hd)
    for j in range(1, len(toks) + 1):
        if PUNCT_CONVENTION and pos[j - 1] == "PUNCT" and j in post:
            post[j] = {hd[j]: 1.0}
    return hd, post


def heads(toks: Sequence[str], pos: Sequence[str], table: Optional[Dict[str, object]] = None, occ=None) -> Dict[int, int]:
    """Point heads (MBR tree by default; MAP with HDLAB_ARM_DECODE=map) -- for consumers that insist on a point; prefer head_posterior."""
    A, n = arc_scores(toks, pos, table, occ); return decode(toks, pos, A, n)[0]


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
    # pri 117: the GRADED hand-off is where the predicate-slot occupancy is available, so it is computed ONCE here
    # and handed to every cue pass (the live path is frontend.Parser.parse -> arc_scores_graded).
    occ = occupancy_from_posterior(toks, pos, tag_post) if CSUBG_CUE else None
    A, n = arc_scores(toks, pos, table, occ)
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
        B, _ = arc_scores(toks, pos2, table, occ)
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
    def __init__(self, beta: float = 10.0, lam: float = 0.3, tsp_asset: Optional[str] = None,
                 pp_assoc: Optional[Dict[str, object]] = None):
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
        self.pp_assoc = pp_assoc            # the NOUN side of Hindle & Rooth, for the nominal host slot
        self.obl_slots = obl_slot_store() if OBL_TEACH else None
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
        # THE OBLIQUE SLOT (pri 94 phase 7): a case-marked nominal hosted by a verb is a plausible OBLIQUE of THIS
        # predicate with THIS preposition, not a bad direct object.  Falls through to the object / subject slots when
        # the grown store has never seen this predicate in this slot, so nothing the teacher taught is removed.
        if OBL_TEACH and self.obl_slots is not None and pos[h - 1] == "VERB":
            _pr = pp_case_preps(toks, pos).get(j)
            if _pr is not None:
                _v = obl_slot_plausibility(self.obl_slots, lemma_verb(toks[h - 1]).lower(), _pr,
                                           pp_obj_class(toks, pos, j))
                if _v is not None:
                    return float(_v)
        if PP_CASE_RULE and j in pp_case_marked(toks, pos):
            return 0.0            # PHRASE-level case marking: a case-marked nominal is oblique, not a core participant
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
        # THE NOMINAL HOST SLOT (pri 94 phase 7): give nominal hosts the meaning vote this teacher reserves for
        # verbs.  Applied after the root row, exactly as measured.
        if BETA_NOM > 0.0 and self.pp_assoc is not None:
            for _prep, _obj, _cands in pp_sites(toks, pos):
                _pw = toks[_prep - 1].lower()
                for _q in _cands:
                    if _q == _obj or pos[_q - 1] not in PP_NOM_HOST or not np.isfinite(A[_q][_obj]):
                        continue
                    _hc = pp_host_class(toks, pos, _q)
                    _pl = pp_p_given(self.pp_assoc, pp_host_key(toks, pos, _q), _hc, _pw)
                    _cc = self.pp_assoc["cc"]; _dc = self.pp_assoc["dc"]; _cp = self.pp_assoc["cp"]
                    _m2 = self.pp_assoc.get("m2", 20.0)
                    _pp = (_cp.get(_pw, 0.0) + 0.5) / (self.pp_assoc["tot"] + 1.0)
                    _g = (_cc.get(_hc + "|" + _pw, 0.0) + _m2 * _pp) / (_dc.get(_hc, 0.0) + _m2)
                    A[_q][_obj] += BETA_NOM * (_pl / (_pl + _g) if (_pl + _g) > 0 else 0.5)
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
           "pp_site", "pp_assoc_from_reading", "pp_lr", "pp_sites", "pp_assoc_v2_from_reading", "pp_arc_values",
           "pp_case_marked", "pp_observe", "pp_p_given", "pp_p_obj", "pp_new_assoc", "genitive_arcs",
           "np_starts", "split_runs", "phrase_head", "npb_matrix", "predicate_flags", "clause_matrices", "clause_value",
           "boundary_penalty",
           "root_cue_values", "predication_boost", "finiteness",
           "predicate_slot_occupancy", "revise_for_predicate_slot", "host_belief", "copular_available",
           "is_existential", "main_verb_carriers",
           "cop_predicates", "cop_complement", "predicate_complements", "predicate_sites",
           "cop_subject_pairs", "csub_sites", "csub_graded_sites", "occupancy_from_posterior",
           "occupancy_from_tags", "observe_copular_subject", "revise_copular_subject",
           "predicate_site_carriers", "copula_tense", "arc_predicate_sites",
           "state_pairs_from_slot", "subordination", "assertion_candidates", "arc_scores", "head_posterior", "heads", "arc_scores_graded", "head_posterior_graded", "heads_graded", "SemanticBootstrapTeacher", "ASSET", "FORM"]


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
