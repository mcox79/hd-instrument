"""Graded role assigner -- the Competition-Model patient route for NON-CANONICAL argument structure.

Landed 2026-08-27 from the integrated `the_front_end_mishandles_non_canonical_argument_structure` (SOLVED/EXCELLENT,
owner-DONE; witness `test_noncanonical_role_assigner.py` 6/6 PASS, re-verified first-hand). The composed front-end reads
who-did-what well on canonical sentences but COLLAPSES on non-canonical structure (passives it fails to detect, reduced
object-relatives "the oxygen plants release", fronting). This organ is the brain's method for exactly those cases.

WHAT IS PINNED (copy the operation):
  * Role assignment is GRADED, PARALLEL cue integration (MacWhinney & Bates Competition Model): cues -- word order,
    voice morphology, filler-gap, verb subcategorization, unaccusativity, animacy -- compete by LEARNED VALIDITY.
    English is order-DOMINANT, but morphology/voice OVERRIDE order on marked (non-canonical) constructions. The additive
    cue activation -> softmax IS the Bayesian posterior for cue integration (McClelland 2013); the learned coefficients
    ARE the cue validities. Runs over the landed `hdlab.graded_competition` (`net_activation`/`map_pick`).
  * THE FIDELITY LEVER IS ROUTING, NOT REPLACEMENT. A FLAT integrator that relearns candidate selection is NET-NEGATIVE
    (it wrecks canonical + overt-relativizer relatives). The faithful Competition Model keeps word-order validity HIGH
    and overrides it ONLY where a marked cue fires. So `hybrid_role_patient` keeps `resolve_patient` byte-identical on
    every confident discrete route + plain word-order default, and invokes the competition ONLY on the non-canonical
    fall-through (a strong reduced/got/being/by-PP passive, a relativizer-LESS object gap, or an unaccusative sole theme
    with no post-verbal nominal). This is `graded_competition`'s argmax-collapse-where-decisive / full-competition-in-
    the-residual design.
  * The voice cue is SPLIT BY PRECISION: `passive_strong` (BE/get/being aux + participle, or participle + by-PP) is
    reliable; `passive_weak` (bare participle after a nominal, no aux) is the `-ed` past/participle GARDEN-PATH ambiguity
    -- the learner correctly drives its validity NEGATIVE (-2.99), so it is never a trigger.

VALIDATED (held-out test n=4078, role_balanced_comprehension_gold): the hybrid beats the front-end on the non-canonical
slice 0.6000 vs 0.5758 (+0.0242 CI-sep), NET-POSITIVE overall (+0.0113 CI-sep) with canonical PRESERVED, shuffled-validity
twin LOSING (+0.3843), seed-robust; the graded integration (not the discrete rule) does it (+0.051 over the two-line rule);
robust voice raises passive recall 0.734->0.763. HONEST modest magnitude. The reduced-relative RESIDUAL is UPSTREAM
(verb-subcat SUPPLY -- suppliable from WordNet frames; the incremental structure-builder for clause segmentation; an
unwired coref organ), NOT a cue-mechanism defect -- routes to those lines, do NOT grow a cue pile.

OUR-INVENTION-UNDER-TEST (swept, not adopted): the cue set + the LEARNED validities `DEFAULT_VALIDITIES` (fit offline by
logistic regression on the role-balanced gold train split -- a static asset; the logistic == the softmax posterior); the
precision gate. DEFAULT-SAFE / ISLAND: importing this changes NO existing behaviour; `hybrid_role_patient` is byte-identical
to `resolve_patient` on canonical/confident inputs. Wire behind a flag; measure on the live reader before any claim.
Do NOT: flat-replace the cascade; trust the weak participle cue as an override; hand-patch `precise_passive`.
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors data/bf_status_registry.jsonl
__bf_verified__ = "2026-09-09 operation/math audit (VERIFIED_BF_LEDGER)"
__bf_note__ = "2026-09-14 pri108 NMOD CLASS + CUE SET v4 (self-gated on the asset cue_set key): a nominal licensed by a nominal is a PROPERTY of a thing, not an oblique participant of an event -- UD-EWT test 700, gold heads: gold nmod 0/489 -> 0.7157 CI-sep, gold obl 0.8081 -> 0.8397 CI-sep UP, all expressible nominals 0.6746 -> 0.8528 CI-sep, core arguments +0.0084 n.s.; LIVE frontend Parser heads: nmod 0 -> 0.6667, all expressible 0.5774 -> 0.7061 CI-sep, core +0.0025 n.s.; the ENGLISH GENITIVE as case VALUES, the arc-free LICENSOR cue (Late Closure) read only where a case marker exists, no left-case-marking of a relative pronoun, and the phrasal verb as a stored (lemma+particle) value | 2026-09-13 pri103 CUE SET v3 (self-gated on the asset cue_set key): argument RANK over the verb dependents (precision-gated on the head posterior), the there-BE CONSTRUCTION as a configuration, LEXICAL case with a relativizer-stopped scan, the copula read in both orders, and the ARGUMENT-HEAD population (quantifier/numeral/nominalised-adjective heads) -- UD-EWT test 700 gold heads: core role recall 0.8655 -> 0.9198 CI-sep, previously unlabelled arguments 0.000 -> 0.838 | Competition-Model op pinned; DEFAULT_VALIDITIES gold-FITTED+adopted; agent weights hand-set; UNACC hand-lexicon | 2026-09-12 coarse_roles: argument-role labeler, cue validities LEARNED on UD-EWT train (configuration-conditioned contrasts), live via arc_labeler.COMPETITION_ROLES"
__bf_corrections__ = []   # append "YYYY-MM-DD <fix>: OLD -> NEW" when a fix RAISES the status
# 2026-09-16 pri134 NON-ARGUMENT ARM (self-gated on the presence of its counts asset): the name-run chunk (pri 118),
# the reduced predication (pri 110/117 predicate slot), the genitive case marker (v4) and the copula as tense carrier
# give appos / flat / compound / nmod:poss / cop with NO supervised labeler -- UD-EWT test 2077 sentences, live chain:
# the non-argument target population 0.0000 -> 0.7622 (twin 0.1039), the RETIRED perceptron 0.7081 (+0.0541 CI-sep).

import json
import functools
import os
from typing import Dict, List, Optional, Sequence

import numpy as np

from hdlab.animacy_lexicon import lookup_animacy
from hdlab.graded_competition import map_pick, net_activation, softmax
from hdlab.relcl_resolver import (
    BE_AUX, RELATIVIZERS, _cands, is_object_gap, precise_passive, resolve_patient,
)
from hdlab.thematic_role_labeler import _is_participle, is_passive_clause, is_passive_predicate, lemma_verb

CUES = ["order", "adjacency", "passive_strong", "passive_weak", "gap", "unacc", "byagent", "animacy"]
NOMINAL = {"NOUN", "PROPN", "PRON"}
GET_AUX = {"get", "gets", "got", "gotten", "getting"}
UNACC = frozenset({
    "break", "spread", "melt", "freeze", "boil", "open", "close", "shut", "sink", "float", "grow", "form",
    "rise", "fall", "dissolve", "shatter", "crack", "split", "burst", "collapse", "expand", "shrink",
    "increase", "decrease", "change", "turn", "develop", "evaporate", "condense", "erode", "drop",
    "cool", "warm", "harden", "soften", "widen", "narrow", "deepen", "thicken", "settle", "scatter",
})

# Cue validities learned OFFLINE by logistic regression on the role-balanced gold train split (a static asset;
# the additive-cue -> logistic IS the softmax/Bayesian posterior for cue integration). passive_weak NEGATIVE = the
# -ed garden-path correctly distrusted.
DEFAULT_VALIDITIES: Dict[str, float] = {
    "order": 1.671254, "adjacency": 2.815255, "passive_strong": 3.231728, "passive_weak": -2.992674,
    "gap": 1.908620, "unacc": -0.373305, "byagent": -2.287969, "animacy": 0.466585,
}


def voice_cues(toks: Sequence[str], pos: Sequence[str], v: int) -> Dict[str, bool]:
    """Graded passive-voice cues for verb v (1-based). The union RECALLS reduced/got/being/by-PP passives that the
    strict BE-aux+participle `precise_passive` misses."""
    low = [t.lower() for t in toks]
    vtag = pos[v - 1] if v - 1 < len(pos) else None
    is_part = _is_participle(toks[v - 1], vtag)
    lo = max(1, v - 3)
    be_before = any(low[j - 1] in BE_AUX for j in range(lo, v))
    get_before = any(low[j - 1] in GET_AUX for j in range(lo, v))
    being_before = any(low[j - 1] == "being" for j in range(lo, v))
    by_after = any(low[j - 1] == "by" for j in range(v + 1, min(len(low) + 1, v + 4)))
    prev_nom = (v - 2) >= 0 and pos[v - 2] in NOMINAL
    return {
        "vc_strong": bool(is_part and be_before),
        "vc_get": bool(is_part and get_before),
        "vc_being": bool(is_part and being_before),
        "vc_bypp": bool(is_part and by_after and not be_before),
        "vc_partN": bool(is_part and prev_nom and not be_before and not get_before),
        "is_participle": bool(is_part),
    }


def robust_passive(toks: Sequence[str], pos: Sequence[str], v: int) -> bool:
    """Robust voice DETECTION (recall arm): any graded passive cue fires."""
    c = voice_cues(toks, pos, v)
    return c["vc_strong"] or c["vc_get"] or c["vc_being"] or c["vc_bypp"] or c["vc_partN"]


def _has_post_object(pos: Sequence[str], low: Sequence[str], v: int) -> bool:
    for j in range(v + 1, len(pos) + 1):
        t = pos[j - 1]
        if t == "VERB" or t == "PUNCT" or low[j - 1] in RELATIVIZERS:
            break
        if t in NOMINAL:
            return True
    return False


def gap_config(toks: Sequence[str], pos: Sequence[str], v: int):
    """Generalised active-filler OBJECT-gap detector, RELATIVIZER-OPTIONAL (covers reduced relatives). Returns
    (antecedent_idx, subject_idx) 1-based if it fires, else (None, None): object slot empty + >=2 pre-verbal nominals
    -> nearest pre-verbal = embedded SUBJECT, the one before it = the fronted ANTECEDENT (patient/gap filler)."""
    low = [t.lower() for t in toks]
    if _has_post_object(pos, low, v):
        return None, None
    pre_noms = [i for i in range(1, v) if pos[i - 1] in NOMINAL]
    if len(pre_noms) < 2:
        return None, None
    subj = pre_noms[-1]
    ante = pre_noms[-2]
    if v - subj > 4:
        return None, None
    return ante, subj


def cue_supports(toks: Sequence[str], pos: Sequence[str], v: int, cands: List[int]) -> Dict[str, np.ndarray]:
    """Per-candidate SMART support arrays for each cue (each already points at the nominal that cue favours as
    PATIENT). Reads ONLY toks/pos (no gold)."""
    low = [t.lower() for t in toks]
    post = [i for i in cands if i > v]
    pre = [i for i in cands if i < v]
    nearest_post = post[0] if post else None
    nearest_pre = pre[-1] if pre else None
    vc = voice_cues(toks, pos, v)
    strong = vc["vc_strong"] or vc["vc_get"] or vc["vc_being"] or vc["vc_bypp"]
    weak = vc["vc_partN"] and not strong
    ante, _subj = gap_config(toks, pos, v)
    lemma = lemma_verb(toks[v - 1])
    unacc_sole = (lemma in UNACC and len(pre) == 1)
    S = {c: np.zeros(len(cands)) for c in CUES}
    for j, i in enumerate(cands):
        if i == nearest_post:
            S["order"][j] = 1.0
        elif i > v:
            S["order"][j] = 0.4
        S["adjacency"][j] = 1.0 / (1.0 + abs(i - v))
        if strong and i == nearest_pre:
            S["passive_strong"][j] = 1.0
        if weak and i == nearest_pre:
            S["passive_weak"][j] = 1.0
        if ante is not None and i == ante:
            S["gap"][j] = 1.0
        if unacc_sole and i == nearest_pre:
            S["unacc"][j] = 1.0
        if (i - 2) >= 0 and low[i - 2] == "by":
            S["byagent"][j] = 1.0
        anim = lookup_animacy(toks[i - 1], pos[i - 1] if i - 1 < len(pos) else None)
        av = anim["animacy"] if anim is not None else "unk"
        S["animacy"][j] = 1.0 if av == "inanimate" else (-1.0 if av == "animate" else 0.0)
    return S


def competition_pick(toks: Sequence[str], pos: Sequence[str], v: int, cands: List[int],
                     weights: Optional[Dict[str, float]] = None, np_head_reduce: bool = False) -> Optional[int]:
    """The patient = graded_competition argmax over the learned additive cue activation. NP-HEAD REDUCE
    (default OFF -> byte-identical): when on, reduce `cands` to NP heads first (+0.20 on 19c who-did-what)."""
    if np_head_reduce:
        from hdlab.np_head_reduce import is_np_head
        cands = [i for i in cands if is_np_head(toks, pos, i - 1)] or cands
    w = DEFAULT_VALIDITIES if weights is None else weights
    S = cue_supports(toks, pos, v, cands)
    idx = map_pick(S, w)
    return cands[idx] if 0 <= idx < len(cands) else None


def hybrid_role_patient(toks: Sequence[str], pos: Sequence[str], v: int,
                        cands: Optional[List[int]] = None, weights: Optional[Dict[str, float]] = None,
                        np_head_reduce: bool = False) -> Optional[int]:
    """THE DEPLOYABLE net-positive route. Keep `resolve_patient` BYTE-IDENTICAL on every confident discrete route +
    plain word-order default (canonical / precise-passive / overt-relativizer relatives UNTOUCHED); invoke the graded
    competition ONLY on the non-canonical fall-through where a marked OVERRIDE cue fires: a STRONG reduced/got/being/
    by-PP passive, or a relativizer-LESS object gap / unaccusative sole theme with NO post-verbal nominal to compete
    (word order then carries no signal). The weak bare-participle cue is deliberately NOT a trigger."""
    if cands is None:
        cands = _cands(pos)
    if np_head_reduce:                                       # NP-head reduce ONCE at the top; sub-calls inherit
        from hdlab.np_head_reduce import is_np_head
        cands = [i for i in cands if is_np_head(toks, pos, i - 1)] or cands
    w = DEFAULT_VALIDITIES if weights is None else weights
    base = resolve_patient(toks, pos, v, cands)
    if precise_passive(toks, pos, v) or is_object_gap(toks, pos, v):
        return base                                         # confident discrete route -> untouched
    vc = voice_cues(toks, pos, v)
    strong = vc["vc_strong"] or vc["vc_get"] or vc["vc_being"] or vc["vc_bypp"]
    ante, _subj = gap_config(toks, pos, v)
    lemma = lemma_verb(toks[v - 1])
    pre = [i for i in cands if i < v]
    post = [i for i in cands if i > v]
    unacc_sole = lemma in UNACC and len(pre) == 1
    if strong or ((ante is not None or unacc_sole) and not post):
        return competition_pick(toks, pos, v, cands, w)
    return base                                             # canonical / no override cue -> word-order default


# ===========================================================================
# BRAIN-FOUNDATIONAL AGENT competition -- the AGENT counterpart to hybrid_role_patient.
# ===========================================================================
# Landed 2026-09-04 from the owner-DONE swap_the_positional_role_assigner_for_the_brain_foundational_
# competition_model (SOLVED; scaffold-free witness test_cmrole_agent_board_organ.py 10/10; board who-did-what
# AGENT 0.041 -> ~0.69 full stack). The reader's who-did-what AGENT was POSITIONAL (leftmost-NP subject proxy)
# and COLLAPSED (0.2257 -> 0.0410) when referent_per_np densified the candidate set with non-participant
# content-noun heads. This is the brain's method: GRADED, PARALLEL cue competition -- the Competition Model
# (Bates & MacWhinney 1989), constraint satisfaction (MacDonald 1994), cue-based retrieval (Lewis & Vasishth
# 2005); additive cue activation A_i = sum_c w_c*support_c(i) -> argmax IS the Bayesian posterior (McClelland
# 2013) -- over the TRACKED / GIVEN discourse entities (Centering Cb->subject, Grosz 1995; DuBois 1987
# Preferred Argument Structure: the transitive AGENT is the given/pronominal argument). REUSES
# graded_competition.net_activation VERBATIM (the same organ the PATIENT side above uses; this adds the AGENT
# slot the substrate lacked). The candidate-SET decouple is LOAD-BEARING: the SAME rule over the DENSE set only
# reaches 0.082 -- the AGENT source (tracked/given) must be decoupled from the PATIENT source (dense residual,
# the +0.336). Ported VERBATIM from experiments/exp_cmrole_agent_board_v1.py (agent_supports/cm_agent_pick).
# OUR-INVENTION-UNDER-TEST (swept, not adopted): the cue set + the validity-seeded weights AGENT_VALIDITIES.

# STRUCTURE cue weight (self-gating; SWEPT not adopted). Landed 2026-09-04 from the owner-DONE
# `the_agent_tie_wall_is_embedded_clauses_needs_a_register_general_incremental_parse_cue`: the register-general
# incremental left-corner subject bind (hdlab.incremental_parser.incremental_subject_before) enters the AGENT
# competition as ONE precision-weighted support. It sits between animacy(2) and byagent(6): a real structural
# commitment, ONE cue that must NOT override strong lexical evidence on canonical clauses (the diagnostic
# FIX/BREAK ratio was ~12:1, so a moderate weight is net-positive on BOTH slices without regression). SOLVED
# weight-robust across {1.5, 2.5, 4.0} (all CI-sep vs base; SATURATES >=2.5 -- more weight cannot change the
# argmax once it breaks the tie). Only votes when a caller supplies `subj_before` (self-gating: see agent_supports).
STRUCT_W = 2.5

# BY-PHRASE CASE-MORPHOLOGY cue weight (byhead; self-gating). Landed 2026-09-06 from the owner-DONE
# `grounded_meaning_role_cue_for_non_canonical_who_did_what_where_word_order_misleads`. On a NON-CANONICAL /
# passive clause ("the tea was poured by the WOMAN") word order misleads and the reader mis-picks the agent;
# the fix is a by-phrase CASE cue -- reward the candidate GOVERNED by the passive-agent preposition "by"
# through its NP (scan over DET/ADJ/NUM/possessive to the governing "by"; see `by_governs`), gated by the
# participle+by-PP CONSTRUCTION detector (`participle_bypp_gate`, the V-en + by-NP morphological signature of
# the demoted external argument). Bates & MacWhinney: case marking is a TOP cue and "by" is English's
# morphological marker of the demoted passive agent. ONE additive Competition-Model cue (OUTVOTABLE by the
# aligned word-order/animacy/structure cues), NOT a hard override. Complements the landed `byagent` cue, which
# only fires when a candidate's PREVIOUS token is literally "by" (prevtok=='by') and so MISSES multi-word
# by-phrases ("by the clerk" / "by a natural process") -- byhead recovers those. SWEPT on MODERN QA-SRL
# {4,6,8,10,12}, saturates at 10 (adopted). VALIDATED (19c-clean QA-SRL): clean agent-post slice
# 0.2556->0.6889 (n=90) / full non-canonical 0.5224->0.6866 (n=201), CI-separated over the live-competition
# floor AND the info-free shuffled-by-membership twin; canonical no-regress (n=845, ~0.696 unchanged); LitBank
# board-safe (participle+byPP gate fires ~4/1830, <=1 answer changed). SELF-GATING: agent_supports emits no
# `byhead` support key unless the caller passes byhead_agent_cue AND the construction gate fires -> byte-
# identical elsewhere (net_activation skips a weighted cue with no support array).
BYHEAD_W = 10.0

# validity-seeded AGENT cue weights -- a STATIC asset (like DEFAULT_VALIDITIES above), hand-set from cue
# validity, NOT trained; weight-robustness swept (SOLVED control (5): cm stays 0.211-0.229 across +/-50% on
# every discriminating cue). English is word-order-DOMINANT (agent preverbal); byagent dominates under PASSIVE.
# `structure` is inert unless the caller passes an incremental subj_before, and `byhead` is inert unless the
# caller passes byhead_agent_cue AND the participle+by-PP gate fires (agent_supports omits the support key
# otherwise, and net_activation skips a weighted cue with no support array -> byte-identical for those callers).
AGENT_VALIDITIES: Dict[str, float] = {
    "preverbal": 3.0, "core_arg": 2.0, "animacy": 2.0, "salience": 2.0, "adjacency": 1.0, "byagent": 6.0,
    "structure": STRUCT_W, "byhead": BYHEAD_W}

_AGENT_PREPS = frozenset(("in", "on", "at", "by", "of", "for", "with", "to", "from", "into", "onto", "upon",
                          "over", "under", "through", "about", "among", "amongst", "between", "against",
                          "toward", "towards", "within", "without", "during", "after", "before", "beside",
                          "behind", "beyond", "near", "off", "out", "across", "around", "beneath"))
_AGENT_NP_SKIP = frozenset(("DET", "ADJ", "NUM", "PUNCT"))     # NP-internal modifiers to skip when scanning left
# personal pronouns as discourse participants: nominative (he/she/they/we/i/you) are animate agents; 'it' is
# inanimate; accusative (him/her/them/us/me) are animate but rarely subjects. Only consulted for pronoun cands.
_AGENT_ANIM_PRON = frozenset(("he", "she", "they", "we", "i", "you", "him", "her", "them", "us", "me"))
# CASE cue (Competition Model: case morphology is a HIGH-VALIDITY cue where marked; English marks it on
# pronouns). NOMINATIVE pronouns can be SUBJECTS; accusative/possessive/reflexive pronouns CANNOT.
NOMINATIVE_PRON = frozenset(("he", "she", "they", "we", "i", "you", "it", "who"))
# Clause-boundary markers (brain-foundational clause segmentation: role assignment is CLAUSE-BOUNDED, an
# argument competes within its clause -- incremental parsing). Relativizers (who/which/that) are DELIBERATELY
# NOT boundaries (they EMBED; the main-clause subject precedes them, so bounding there would delete it).
_AGENT_SUBORD = frozenset(("because", "when", "while", "if", "although", "though", "since", "unless", "after",
                           "before", "until", "as", "whereas", "whenever", "wherever", "once", "lest"))
_AGENT_COORD = frozenset(("and", "but", "or", "nor", "yet", "so"))
_AGENT_STRONGPUNCT = frozenset((";", ":", "--", "—", "(", ")"))


# ------------------------------------------------------------------- BY-PHRASE CASE cue (byhead) machinery
# NP-internal tokens scanned through leftward to find a governing "by" (the by-PP head can sit several tokens
# in: "by a natural process"). Ported VERBATIM from experiments/exp_noncanonical_agent_bymorph_v1.py.
_BYHEAD_NP_SKIP = frozenset(("DET", "ADJ", "NUM", "PUNCT", "NOUN", "PROPN", "CCONJ"))
_BYHEAD_NP_SKIP_LOW = frozenset(("'s", "the", "a", "an", "of"))
_BYHEAD_NOM = ("NOUN", "PROPN", "PRON")


# ---------------------------------------------------------------------------------------------------------------
# COARSE ROLE LABELS by cue competition (strategy 2026-09-12, upstream math-BF pass, rung 5 of the affected-entity chain).
# The supervised dependency labeler (arc_labeler, NOT_BF) is the lossy rung of that decision (LABELS -0.0369 of -0.0705;
# BY_AGENT 0.106, PASS_SUBJ 0.581; 25% of gold undergoer pronouns labelled out of the undergoer set).
#
# BRAIN COMPUTATION (PINNED at the computational level -- the Competition Model, Bates & MacWhinney 1982/1989; McDonald &
# MacWhinney 1989): a nominal's grammatical role is decided by PARALLEL competition of surface CUES -- word order relative
# to the governing head (English-dominant), the preposition that introduces the nominal, voice morphology (be/get +
# participle), the copula (a nominal before a non-verbal predicate linked by an AUX is its subject), pronoun case, and
# the class of the governing head. Each cue carries a learned STRENGTH per role = its VALIDITY for that role
# (availability x reliability; MacWhinney, Bates & Kliegl 1984), acquired from experience -- never hand-set. The
# competition is additive: activation(role) = log-prior(role) + SUM_cues strength(cue value -> role), then softmax =
# the posterior (graded_competition.net_activation / softmax). With strength = log P(role | cue value) this IS the
# normative (naive-Bayes) limit of additive cue competition; the counting rule for the strengths is a PARAMETER
# choice (error-driven learning would converge to the same conditional structure).
# v1 (probe v13) cued ONE role per cue with a scalar weight; its learned validities showed `non_verb_head` at chance
# (half of all nominals) and `voice_passive` NEGATIVE -> the loss was cue DESIGN. v2 (this block) uses categorical cue
# VALUES with per-role strengths and adds the three missing structural cues: head-class x order COALITION (a nominal
# before an ADJ/NOUN predicate is not "other"), the COPULA cue, and the SURFACE preposition (the ADP that precedes the
# nominal span, robust to predicted heads). Strengths live in data/frontend_assets/coarse_role_validities_ud_ewt.json
# (built offline by tools/build_coarse_role_validities.py from UD-EWT TRAIN; evaluation treebanks never touched).
# IOBJ added 2026-09-12 (signal trace of the who-did-what PATIENT consumer): folding the RECIPIENT ("gave HIM the book") into
# OBJ made the competition label two post-verbal nominals "obj" and the consumer took the first (23/37 of its lost items).
# The Competition Model separates recipient from patient by ORDER among two bare post-verbal nominals and by ANIMACY.
# NMOD added 2026-09-14 (pri 108). A case-marked phrase licensed by a PREDICATE is an oblique PARTICIPANT of an event;
# one licensed by a NOMINAL is a PROPERTY of a thing -- two different things in the situation model, and the organ could
# not say the second at all (gold `nmod` 0/489 on UD-EWT test 700 even given the gold tree, so the heads rung's whole nmod
# gain died at this boundary). The distinction is a pure function of the LICENSING HOST'S CATEGORY, which the organ already
# computes as its `config` cue, so the class costs no new cue for the prepositional kind; the GENITIVE kind needed the one
# case marker English puts to the nominal's RIGHT (see `genitive_value`). NMOD is deliberately NOT in ROLE_TO_SLOT: a noun
# takes many modifiers, so the class is UNCAPPED in the joint frame-slot decode, like OBL and OTHER.
# MEASURED (UD-EWT test 700, subtype-preserving gold, live-chain perceived accrual, paired item bootstrap over items):
#   GOLD heads -- gold nmod 0.0000 -> 0.7403 (+0.7403 CI[+0.7014,+0.7771]); gold obl 0.8081 -> 0.8691 (+0.0609
#     CI[+0.0339,+0.0880], UP); obl+nmod 0.3841 -> 0.8015 (+0.4174 CI-sep); all expressible nominals 0.6746 -> 0.8661
#     (+0.1915 CI[+0.1729,+0.2101]); CORE arguments 0.9073 -> 0.9191 (+0.0118 CI[+0.0008,+0.0236], CI-separated UP).
#   LIVE heads (hdlab.frontend Parser, attachment arm, in-order MBR tree) -- gold nmod 0.0000 -> 0.6769 (+0.6769
#     CI-sep); all expressible nominals 0.5774 -> 0.7061 (+0.1286 CI[+0.1096,+0.1477]); obl+nmod 0.3637 -> 0.6534;
#     CORE 0.7445 -> 0.7462 (+0.0017 n.s.); gold obl -0.1377 CI-sep, of which ~92% of flips have a WRONG live head
#     (the floor scored those right by accident: with no NMOD class it called every case-marked nominal `obl`).
# Info-free twin (strengths permuted across cue values) CI-separated below in every population and both arms.
# Restricted to the two-way OBL-vs-NMOD readout the 0.9813 host-category figure measures, the organ is 0.8970 (n=932).
ROLE_CLASSES = ["SUBJ", "OBJ", "PASS_SUBJ", "BY_AGENT", "OBL", "OTHER", "IOBJ", "NMOD"]
ROLE_TO_DEP = {"SUBJ": "nsubj", "OBJ": "obj", "PASS_SUBJ": "nsubj:pass", "BY_AGENT": "obl:agent", "OBL": "obl", "OTHER": "dep",
               "IOBJ": "iobj", "NMOD": "nmod"}
# VERB-FRAME SLOTS with capacity ONE per verb (owner-DONE pri 93, 2026-09-13; solver diff landed): cue-based retrieval over the
# verb's frame (Lewis & Vasishth 2005) -- a filled slot lowers its availability for a second same-type filler. SUBJ and PASS_SUBJ
# share the one SUBJECT slot (a clause has one subject whichever voice). OBL / OTHER are UNCAPPED (a verb takes many adjuncts).
# Measured by the solver (UD-EWT test 700): OBJ precision +0.067 CI-sep on the supervised parse, +0.022 on gold heads, ~0 on the
# attachment arm's heads (its core-argument arcs are the binding wall, not this organ); twin CI-sep below in every condition.
# MEASUREMENT METADATA, read by NO computation in this module (owner/supervisor ruling 2026-09-14, the treatment
# pri 94 gave the heads rung's convention layer): the UD subtypes that are an ANNOTATION CONVENTION rather than a
# comprehension distinction this organ could ever draw, recorded HERE so that every scorer of this organ excludes the
# same tokens instead of each one deciding for itself. `nmod:desc` is the UD-2.16 split of a DESCRIPTIVE nominal off
# `compound`/`appos` -- "President Bush", "Enron Corp.", "Mr. Lavorato". It is surface-identical to `compound` (348
# tokens on UD-EWT test 700) and `flat` (188) in the very same configuration, the brain reads "President Bush" and a
# compound as the same object, and it is unwinnable by construction: an UPSTREAM ORACLE (this cue set trained on the
# GOLD TREE) gets 2 of 18. UD-EWT test 700, gold heads: gold nmod 0.7423 over all 489, 0.7707 over the 471
# CONVENTION-FREE tokens, 0.8710 over the 411 that carry a case marker at all.
CONVENTION_SUBTYPES = ("nmod:desc",)
ROLE_TO_SLOT = {"SUBJ": "subj", "PASS_SUBJ": "subj", "OBJ": "obj", "IOBJ": "iobj", "BY_AGENT": "byagent"}
CORE_SLOTS = ["subj", "obj", "iobj", "byagent"]
# lambda[slot] = -log P(2nd filler of slot | >=1), accrued from reading (tools/build_coarse_role_validities.py, stored in the asset
# as counts["slot_capacity"]); the occupancy weight kappa is the swept operating point.
# LANDED SELECTABLE, DEFAULT OFF (2026-09-13 14:00, measured on the LIVE brain-foundational chain): with the attachment arm's heads the
# joint decode costs the who-did-what PATIENT read 0.7954 -> 0.7781 ungated, 0.781 gated at any OCC_MIN_P (the beam posterior is ~1
# on MAP heads, so the gate rarely fires; a mis-attached sibling still displaces a true object). The solver's win (+0.067 OBJ
# precision, CI-sep) is real on the supervised parse and on gold heads -- i.e. the mechanism is right and its input is the wall:
# the governor's CORE-ARGUMENT arcs (pri 97 / pri 94 levers). Flip ON (HDLAB_ROLE_SLOT_OCCUPANCY=1) when those land; re-measure.
SLOT_OCCUPANCY = os.environ.get("HDLAB_ROLE_SLOT_OCCUPANCY", "0") == "1"
OCC_MODE = os.environ.get("HDLAB_ROLE_OCC_MODE", "incr")   # "incr" (soft incremental occupancy over the graded activations; the
#                                                             recommended form with a head posterior) | "hard" (capacity-one greedy)
OCC_KAPPA = float(os.environ.get("HDLAB_ROLE_OCC_KAPPA", "1.0"))
# HEAD-CONFIDENCE GATE (2026-09-13, measured on the live BF governor): the joint decode groups a verb's nominals by their HARD heads;
# when the governor mis-attaches a nominal it competes in the wrong frame and displaces a true object (patient board read 0.7954 ->
# 0.7781 ungated). A verb's frame is decoded jointly only when every member's P(head = this verb) >= OCC_MIN_P (the graded hand-off);
# without a posterior the hard heads are trusted. Swept below.
OCC_MIN_P = float(os.environ.get("HDLAB_ROLE_OCC_MIN_P", "0.8"))
_NEG_INF = -1e9
COARSE_CUES = ["config", "voice_order", "prep", "cop", "case", "post_slot", "pre_slot", "animacy", "frame"]
# 2026-09-12 measured: the nominal's raw 70-way induced category as a cue LOWERED held-out role accuracy 0.9235 -> 0.9115
# (SUBJ 0.941 -> 0.898): too fine-grained for the per-configuration counts (sparse, noisy) -- REFUTED-AS-BUILT at this
# granularity, NOT as a principle; the stronger version is a coarser induced class (or per-cue shrinkage) once the induced
# categories themselves are better than 0.745. Kept behind a flag.
USE_INDUCED_CATEGORY_CUE = False
_OBJ_CASE = frozenset({"him", "her", "them", "me", "us", "whom", "himself", "herself", "themselves", "myself", "ourselves", "itself"})
_SUBJ_CASE = frozenset({"he", "she", "they", "i", "we", "who"})
_SPAN_POS = frozenset({"DET", "ADJ", "NUM", "ADV", "PART", "NOUN", "PROPN", "PRON", "SYM", "X"})
_COARSE_VALIDITIES_PATH = os.environ.get("HDLAB_ROLE_VALIDITIES") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "frontend_assets", "coarse_role_validities_ud_ewt.json")
# HDLAB_ROLE_VALIDITIES (2026-09-13): selects another validity table -- e.g. the one learned from the live governor's PERCEIVED heads
# (tools/build_coarse_role_validities.py --perceived) for the A/B against the gold-convention table.
_COARSE_VALIDITIES_CACHE: Optional[Dict[str, object]] = None
# READING-INDUCED lexical categories (the TOP rung handing DOWN: exp_reading_induced_categories_v1, 1M Simple-Wiki lines, k=68 + 2
# form classes, no labels) -- the nominal's OWN induced category is a cue in the role competition (time/measure nouns, mass
# nouns, names form their own distributional clusters; the gold-named map is NOT used here, only the cluster id).
_INDUCED_CAT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 "data", "frontend_assets", "induced_categories_simplewiki_1m_k68.json")
_INDUCED_CAT_CACHE: Optional[Dict[str, int]] = None


def induced_category(word: str) -> str:
    """The reading-induced category id of a word form ('cNN'), or 'unk' when the word was not read."""
    global _INDUCED_CAT_CACHE
    if _INDUCED_CAT_CACHE is None:
        try:
            with open(_INDUCED_CAT_PATH, encoding="utf-8") as f:
                _INDUCED_CAT_CACHE = json.load(f)["word2cat"]
        except Exception:
            _INDUCED_CAT_CACHE = {}
    c = _INDUCED_CAT_CACHE.get(word.lower())
    return f"c{c}" if c is not None else "unk"


# ---------------------------------------------------------------------------------------------------------------
# CUE SET v3 (pri 103, 2026-09-13). SELF-GATING: every addition below is inert unless the LOADED validity table
# declares "cue_set": "v3" (data/frontend_assets/coarse_role_validities_ud_ewt*.json without that key -> the organ is
# byte-identical to the pre-2026-09-13 behaviour). Five points where the cue set read a surface proxy where the brain
# reads a structure; each measured separately on UD-EWT test 700 (see notes/problems/the_role_competition_misses_one_
# subject_in_six.../SOLVED.md):
#   * ARGUMENT RANK over the verb's own dependents, not over TOKENS (an NP-internal compound is not a second argument
#     slot), and the same rank cue on the PRE-verbal side (the active-filler configuration; Frazier & Clifton 1989)
#     -- PRECISION-GATED on the heads rung's own posterior, since it is the one arc-dependent addition.
#   * the EXPLETIVE does not fill the subject slot, and the there-BE CONSTRUCTION is a CONFIGURATION (Goldberg 1995;
#     MacWhinney item-based constructions), not one additive contrast fighting the general post-verbal configuration.
#   * CASE IS LEXICAL: the preposition FORM is the cue value (Bates & MacWhinney: case marking is a top cue); the
#     surface scan STOPS at a relativizer ("in which KENNEDY joined": "in" governs "which").
#   * the COPULA cue reads BOTH orders (inverted "Here is a draft"), and ADV/ADP/SYM/INTJ predicates get their own
#     head classes instead of one OTHERH bucket.
#   * AN ARGUMENT IS WHATEVER FILLS THE SLOT: a quantifier / numeral / nominalised-adjective phrase HEAD is labelled
#     too (Right-hand Head Rule, Williams 1981 + DP-head, Abney 1987 -- the landed np_head_reduce criterion).
# REFUTED-AS-BUILT here, with numbers, and deliberately NOT included: reading VOICE off the predicate's AUX
# DEPENDENTS (-0.025 subject recall CI-sep: the cue then inherits the governor's attachment noise, and the shipped
# surface window is the higher-validity read); the filler's own CATEGORY as a full-inventory cue (-0.10 CI-sep: it
# double-counts animacy and case); the relative-pronoun FORM and the relative clause as its own configuration (both
# trade subjects for objects, net negative).
EXTRA_ARG = frozenset({"NUM", "ADJ", "DET", "SYM", "X"})   # + the phrase heads the NOMINAL set never labelled
HEADCLS_V3 = ("VERB", "AUX", "NOUN", "PROPN", "ADJ", "PRON", "NUM", "ADV", "ADP", "SYM", "INTJ")
RANK_TAU = float(os.environ.get("HDLAB_ROLE_RANK_TAU", "0.5"))   # SWEPT: the head posterior above which rank votes
_MODSCAN = frozenset({"ADJ", "NUM", "ADV", "DET"})
_POSS_MARK = frozenset({"'s", "'", "s'", "’s", "’"})
_WHREL = frozenset({"who", "whom", "whose", "which", "that", "what", "where", "when", "why"})


# ---------------------------------------------------------------------------------------------------------------
# CUE SET v4 (pri 108, 2026-09-14). SELF-GATING exactly like v3: both additions below are inert unless the LOADED
# validity table declares "cue_set": "v4". Two points where English marks a distinction the cue set never read:
#   * THE GENITIVE IS A CASE MARKER. Case marking is a top Competition-Model cue (Bates & MacWhinney 1989; MacWhinney
#     1987) and pri 103 already lexicalised the PREPOSITION -- but English's other case marker, the genitive clitic 's
#     (and the possessive pronoun forms), was invisible, so a possessor competed against a COMPOUND in the very same
#     NOUN_pre configuration on no evidence at all. Two new VALUES of the EXISTING `case` cue, so a v3 table simply has
#     no entry for them and the cue abstains. Worth gold-heads nmod:poss 0.000 -> 0.928 of the class's 489 tokens.
#   * THE LICENSOR IS ALSO VISIBLE ARC-FREE. The obl/nmod decision IS the host's category, and the organ reads that
#     category ONLY through its `config` cue, i.e. through the governor's arc -- so it inherits every attachment error
#     at BOTH learning and reading time. The nearest preceding lexical head is the default licensor (Late Closure /
#     Recency, Frazier 1979 -- PINNED, the same locality the attachment arm's own distance cue implements), and a
#     genitive-marked nominal's licensor is the FOLLOWING head; a GENITIVE to the left is skipped, because a genitive
#     stands in determiner position and modifies the nominal rather than licensing it. Alone this cue is 0.707 on the
#     obl/nmod population (vs 0.9796 for the arc-bound gold-head rule): HIGH availability, MODERATE reliability --
#     which is what a Competition-Model cue is. Added to the competition, never used as a rule, read ONLY where there is
#     a case marker to interpret, and read ARC-INDEPENDENTLY (the GLOBAL key -- see coarse_role_supports). Measured: it is what turns
#     the class's obl regression into a gain (gold obl 0.7878 -> 0.8352, i.e. -0.0203 CI-sep below the floor ->
#     +0.0271 CI-sep ABOVE it) and what takes CORE arguments CI-separated UP (+0.0135 CI[+0.0025,+0.0245]).
#   * THE COMPETING ATTACHMENT PRINCIPLE. Recency / Late Closure (the licensor cue) is only half the account: the
#     literature pairs it with PREDICATE PROXIMITY (Gibson et al. 1996), which prefers attachment close to a predicate
#     head, and the two are language-modulated rather than absolute. Both are in the competition (`predprox`), which is
#     worth gold obl 0.8352 -> 0.8691 and narrows the live obl loss -0.1580 -> -0.1377.
#   * A RELATIVE PRONOUN IS NOT CASE-MARKED FROM THE LEFT, and A PHRASAL VERB IS A STORED LEXICAL ITEM -- see (b) and
#     (d) in coarse_role_cues. Both were found by tracing the CORE-argument losses the licensor cue exposed: 6
#     relative-clause subjects read as nmod and 8 objects read as obl (the particle of "worked OUT a deal").
# REFUTED-AS-BUILT here, with numbers, and deliberately NOT included: the PROSODIC BREAK (comma/dash/paren) as a cue
# value -- it costs gold-heads CORE argument accuracy -0.0169 CI-sep while leaving gold nmod flat (354 -> 353 correct),
# because an intonation boundary separates appositives, conjuncts and list items (all OTHER) just as often as nmod, so
# the contrast is ~flat for NMOD inside the configuration while it shifts the core classes.
_POSS_PRON = frozenset({"my", "your", "his", "her", "its", "our", "their", "whose",
                        "mine", "yours", "hers", "ours", "theirs"})
_NP_START = frozenset({"NOUN", "PROPN", "ADJ", "NUM", "DET", "PRON", "X", "SYM"})
_CONTENT_CAT = ("NOUN", "PROPN", "PRON", "VERB", "AUX", "ADJ", "NUM", "ADV", "SYM", "INTJ", "X")
_LEFT_SKIP = ("DET", "ADJ", "NUM", "ADV", "PART", "PUNCT")
_LEFT_STOP = ("SCONJ", "CCONJ")


def genitive_value(toks: Sequence[str], pos: Sequence[str], i: int):
    """The ENGLISH GENITIVE as a CASE MARKER -- 'gen_clitic' (the nominal is immediately followed by 's / ') or
    'gen_pron' (the token IS a possessive pronoun form in the pre-nominal determiner position), else None.
    Arc-free; AMBIGUOUS by design ('her' is also the object form) -- the learned validity decides, not a rule."""
    low = toks[i - 1].lower()
    if i < len(toks) and toks[i].lower() in _POSS_MARK:
        return "gen_clitic"
    if low in _POSS_PRON and i < len(toks) and (pos[i] if i < len(pos) else "") in _NP_START:
        return "gen_pron"
    return None


def host_surface(toks: Sequence[str], pos: Sequence[str], i: int, maxscan: int = 8) -> str:
    """THE ARC-FREE LICENSOR CUE: the category of the nearest preceding lexical head, skipping the nominal's own left
    modifiers and at most one ADP case marker (Late Closure / Recency); for a genitive-marked nominal the licensor is
    the nearest FOLLOWING head. Values 'l<CAT>' / 'r<CAT>' / 'none'. Reads toks/pos only -- no arc, so its validity is
    learned from clean experience however the governor attached the token."""
    if genitive_value(toks, pos, i) is not None:
        j, steps = i, 0
        while j < len(pos) and steps < maxscan:
            p = pos[j]
            if p in ("PART", "DET", "ADJ", "NUM", "ADV", "PUNCT"):
                j += 1; steps += 1; continue
            return ("r" + p) if p in _CONTENT_CAT else "rOTHER"
        return "none"
    j, steps, seen_adp = i - 1, 0, False
    while j >= 1 and steps < maxscan:
        p = pos[j - 1]
        if p == "ADP" and not seen_adp:
            seen_adp = True; j -= 1; steps += 1; continue
        if p in _LEFT_SKIP:
            j -= 1; steps += 1; continue
        if genitive_value(toks, pos, j) is not None:
            # a GENITIVE stands in DETERMINER position -- it is the nominal's own left modifier, not its licensor
            # (the DP-head rule the organ already applies in `is_arg_head`). Found by a consumer negative: without
            # this, "HER office is on the third floor" read `Her` as office's licensor and the copular state read
            # lost its holder.
            j -= 1; steps += 1; continue
        if p in _LEFT_STOP:
            return "none"
        return ("l" + p) if p in _CONTENT_CAT else "lOTHER"
    return "none"


_PRED_CAT = ("VERB", "AUX", "ADJ", "ADV")


def predicate_proximity(toks: Sequence[str], pos: Sequence[str], i: int, window: int = 8) -> str:
    """PREDICATE PROXIMITY (Gibson, Pearlmutter, Canseco-Gonzalez & Hickok 1996) -- the SECOND attachment principle,
    the one that competes with Recency / Late Closure: an attachment is preferred as structurally close to the head of
    a PREDICATE phrase as possible. `host_surface` implements Recency alone (the nearest preceding lexical head);
    this is the cue that pulls the other way, and the two are known to be language-modulated rather than absolute --
    which is exactly why the licensor's validity had to be LEARNED (0.707 alone) rather than applied as a rule.
    Having BOTH in the competition is the faithful form, and it is measurably better: gold obl 0.8352 -> 0.8691,
    all expressible nominals 0.8604 -> 0.8661, and the live obl loss narrows -0.1580 -> -0.1377.
    Value = how far back the nearest preceding PREDICATE head is, bucketed. Arc-free (toks/pos only)."""
    d = None
    for j in range(i - 1, max(0, i - 1 - window), -1):
        if pos[j - 1] in _PRED_CAT:
            d = i - j
            break
    if d is None:
        return "far"
    return "1" if d == 1 else ("2" if d == 2 else ("3-4" if d <= 4 else "5-8"))


def is_arg_head(toks: Sequence[str], pos: Sequence[str], i: int, extra=EXTRA_ARG) -> bool:
    """Is token i (1-based) the HEAD of an argument phrase? NOUN/PROPN/PRON always (the pre-v3 population, unchanged);
    a NUM / ADJ / DET / SYM / X only when it is NOT an NP-internal modifier -- the Right-hand Head Rule (Williams 1981)
    and the DP-head rule (Abney 1987), i.e. the landed `hdlab.np_head_reduce.is_np_head` criterion extended over the
    intervening modifier run ("a FEW nerves" -> modifier; "the very FEW who read" -> head; "MANY of them" -> head).
    Arc-free: reads only toks/pos."""
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
        if toks[j].lower() in _POSS_MARK:
            return False
        if q in _MODSCAN:
            j += 1; steps += 1; continue
        break
    return True


def existential_frame(toks: Sequence[str], pos: Sequence[str], h: int) -> bool:
    """The there-BE CONSTRUCTION: a clause-initial expletive `there` before the predicate at h with no nominal
    between. A stored form-meaning pairing whose notional subject FOLLOWS the verb (Goldberg 1995); in the Competition
    Model the construction is the CONFIGURATION within which cue validities are read. Surface-only (arc-free)."""
    low = [t.lower() for t in toks]
    lo, hi = clause_bounds(toks, pos, h - 1)
    for j in range(lo, min(h - 1, hi)):
        if low[j] == "there" and (pos[j] if j < len(pos) else None) in ("PRON", "ADV", "DET"):
            if not any((pos[k] if k < len(pos) else None) in ("NOUN", "PROPN") for k in range(j + 1, h - 1)):
                return True
    return False


def _prep_of_v3(toks, pos, heads, i):
    """(preposition form or None, far) -- like `_prep_of`, but the surface scan STOPS at a relativizer: a wh-word is
    the preposition's OWN object and opens a new clause, so "in which KENNEDY joined" must not read `in` as KENNEDY's
    case marker (8 subjects mislabelled obl on UD-EWT test 700)."""
    for j in range(1, i):                     # ASCENDING (deterministic; heads.items() order is not)
        if heads.get(j) == i and j - 1 < len(pos) and pos[j - 1] == "ADP":
            return toks[j - 1].lower(), False
    j, steps, crossed = i - 1, 0, False
    while j >= 1 and steps < 5:
        p = pos[j - 1]
        low = toks[j - 1].lower()
        if p == "ADP":
            return low, crossed
        if low in _WHREL:
            return None, False
        if p not in _SPAN_POS:
            return None, False
        if p in ("DET", "PRON"):
            return (toks[j - 2].lower(), crossed) if j >= 2 and pos[j - 2] == "ADP" else (None, False)
        if p in ("NOUN", "PROPN", "NUM"):
            crossed = True
        j -= 1; steps += 1
    return None, False


# THE CONFIGURATION IS A RELATION TO THE PREDICATE, NOT A PART OF SPEECH (2026-09-14, pri 113).  In the Competition
# Model the configuration a cue is read within is "this nominal's position relative to the PREDICATE of its clause"
# (Bates & MacWhinney 1989).  `_head_class` read the tag column instead, which did two damages at once on the 21.9%
# of asserted clauses whose predicate UD puts on an ADJ / NOUN / ADV:
#   (i)  it CONFLATED a nominal governed by a PREDICATIVE adjective ("the sky is BLUE" -> sky = SUBJ) with one
#        governed by an ATTRIBUTIVE adjective -- both score hc = "ADJ";
#   (ii) it shut every predicate-relative cue off for the predicative case: measured on UD-EWT test 700 over the 269
#        arguments under a non-verbal predicate, the PRE-VERBAL SLOT cue fired 2 times, the argument-RANK cue 5, the
#        verb-FRAME cue 3 -- against 52 / 136 / 27 once the configuration is read correctly.
# PRED is therefore a head class of its own: it un-conflates (i), opens (ii), and -- because it is NOT "VERB"/"AUX"
# -- keeps the `cop` cue, which is the one cue that currently carries the copular subject.
# CAPABILITY-GATED, NOT ASSUMED: the class is used only when the LOADED validity table carries PRED rows, because
# the strengths are COUNTS the teacher has to accrue (tools/build_coarse_role_validities.py calls this same cue
# function, so a rebuild learns them; `observe_role_outcome` is the online form).  On a table without them every
# `PRED_*` lookup abstains and role accuracy on those clauses falls 0.7361 -> 0.3309 -- measured, which is why this
# guard is code and not a note.  HDLAB_ROLE_PREDICATE_HEADS=0 disables.
PRED_HEADS = os.environ.get("HDLAB_ROLE_PREDICATE_HEADS", "1") == "1"
_HAS_PRED_ROWS = False                      # set by load_coarse_validities from the table itself
_PRED_HC = ("VERB", "AUX", "PRED")


@functools.lru_cache(maxsize=16384)
def _predicate_heads(toks_t, pos_t):
    """The 1-based non-verbal predicate heads of this sentence (attachment_arm.predicate_complements -- ONE organ
    owns predication).  Cached per (tokens, tags): the cue function is called once per argument head."""
    from hdlab.attachment_arm import predicate_complements
    try:
        return frozenset(predicate_complements(list(toks_t), list(pos_t)))
    except Exception:
        return frozenset()


def _pred_heads_for(toks, pos):
    if not (PRED_HEADS and _HAS_PRED_ROWS):
        return frozenset()
    return _predicate_heads(tuple(toks), tuple(pos))


def _head_class(pos: Sequence[str], h: int, v3: bool = False, pred=frozenset()) -> str:
    if h is None or h < 1 or h > len(pos):
        return "ROOT"
    p = pos[h - 1]
    if h in pred and p not in ("VERB", "AUX"):
        return "PRED"                       # this head holds its clause's predicate slot (see the block above)
    if v3:
        return p if p in HEADCLS_V3 else "OTHERH"
    return p if p in ("VERB", "AUX", "NOUN", "PROPN", "ADJ", "PRON", "NUM") else "OTHERH"


def _prep_of(toks: Sequence[str], pos: Sequence[str], heads: Dict[int, int], i: int):
    """The preposition introducing nominal i (1-based) and whether it was perceived DIRECTLY (attached ADP, or an ADP with
    only determiners/modifiers between) or FAR (the surface scan crossed a noun-like token: "in the school bus" vs
    "in the morning John" are indistinguishable by order alone -> a weaker, separately-learned cue value).
    Returns (prep or None, far: bool)."""
    for j, h in heads.items():
        if h == i and j < i and j - 1 < len(pos) and pos[j - 1] == "ADP":
            return toks[j - 1].lower(), False
    j = i - 1
    steps = 0
    crossed = False
    while j >= 1 and steps < 5:
        p = pos[j - 1]
        if p == "ADP":
            return toks[j - 1].lower(), crossed
        if p not in _SPAN_POS:
            return None, False
        if p in ("DET", "PRON"):
            # a determiner / possessive is the NP's LEFT EDGE: only an ADP immediately before it introduces this nominal
            return (toks[j - 2].lower(), crossed) if j >= 2 and pos[j - 2] == "ADP" else (None, False)
        if p in ("NOUN", "PROPN", "NUM"):
            crossed = True
        j -= 1; steps += 1
    return None, False


def coarse_role_cues(toks: Sequence[str], pos: Sequence[str], heads: Dict[int, int], i: int,
                     frames: Optional[Dict[str, Sequence[int]]] = None, v3: bool = False,
                     conf: Optional[Dict[int, float]] = None, v4: bool = False) -> Dict[str, str]:
    """Categorical cue VALUES for nominal token i (1-based) given its governing head (1-based, 0 = root).
    Reads toks / pos / heads only (no gold, no labels). Each value is a key into the learned validity table.
    v3=False (default) -> byte-identical to the pre-2026-09-13 cue set. v3=True -> the pri-103 cue set (see the CUE
    SET v3 block above); conf = {token: P(its MAP head)} from the heads rung, which precision-gates the one
    arc-dependent addition (the argument-rank cue)."""
    h = heads.get(i, 0) or 0
    low = toks[i - 1].lower()
    hc = _head_class(pos, h, v3, _pred_heads_for(toks, pos))
    order = "pre" if (h and i < h) else ("post" if h else "root")
    cfgkey = f"{hc}_{order}"
    if v3 and hc in _PRED_HC and h and existential_frame(toks, pos, h):
        cfgkey += "_ex"                     # the CONSTRUCTION is the configuration
    cues = {"config": cfgkey}
    if hc in ("VERB", "AUX") and h:
        vc = voice_cues(toks, pos, h)
        strong = bool(vc["vc_strong"] or vc["vc_get"] or vc["vc_being"])          # be/get/being + participle
        # pri 111: the voice cue is a property of the PREDICATE h, not of the sentence. (The old call also passed
        # the head index `h` into `is_passive_clause`'s WINDOW parameter -- a latent defect: the scan widened with
        # the predicate's position in the sentence.)
        weak = bool(vc["vc_bypp"] or is_passive_predicate(toks, pos, h, heads=heads))   # by-PP / clause-local passive
        passive = strong or weak
        cues["voice_order"] = ("passive_strong_" if strong else ("passive_weak_" if weak else "active_")) + order
    else:
        passive = False
        cues["voice_order"] = "na"
    prep, far = _prep_of_v3(toks, pos, heads, i) if v3 else _prep_of(toks, pos, heads, i)
    if prep is None:
        cues["prep"] = "none"
    elif prep == "by":
        cues["prep"] = "by_passive" if passive else "by"
    elif v3:
        cues["prep"] = prep + ("_far" if far else "")   # LEXICAL case marking; Dirichlet shrinkage IS the backoff
    elif prep == "of":
        cues["prep"] = "of_far" if far else "of"
    else:
        cues["prep"] = "other_far" if far else "other"
    # PRE-VERBAL SLOT cue (Competition Model "first noun = agent" strategy): for a post-verbal nominal under a VERB/AUX head,
    # is the verb's pre-verbal slot EMPTY (no nominal between the clause edge and the verb)? An empty slot makes a post-verbal
    # nominal the likely SUBJECT (inversion, "said John", questions, relative clauses); a filled slot makes it the OBJECT.
    if order == "post" and hc in _PRED_HC and h:
        if v3:
            eff = [j for j in range(1, h) if heads.get(j) == h and is_arg_head(toks, pos, j)]
            if not eff:
                j = h - 1
                while j >= 1:
                    pj = pos[j - 1]
                    if pj in ("PUNCT", "SCONJ", "CCONJ", "VERB"):
                        break
                    if is_arg_head(toks, pos, j):
                        eff.append(j)
                    j -= 1
            # an EXPLETIVE does not fill the subject slot -- it gets its own cue value, not "filled"
            cues["pre_slot"] = ("empty" if not eff else
                                ("expletive" if all(toks[j - 1].lower() == "there" for j in eff) else "filled"))
        else:
            j = h - 1; filled = False
            while j >= 1:
                pj = pos[j - 1]
                if pj in ("PUNCT", "SCONJ", "CCONJ") or pj in ("VERB",):
                    break
                if pj in NOMINAL:
                    filled = True; break
                j -= 1
            cues["pre_slot"] = "filled" if filled else "empty"
    else:
        cues["pre_slot"] = "na"
    # COPULA cue: a nominal BEFORE a non-verbal predicate with an AUX (be/get) in between is the predicate's subject.
    if v3 and h and hc not in ("VERB", "AUX"):
        # BOTH orders: the inverted locative copular ("Here IS a revised draft") puts the subject AFTER the predicate
        lo_, hi_ = (i, h) if i < h else (h, i)
        between_aux = any(pos[j - 1] == "AUX" for j in range(lo_ + 1, hi_))
        aux_dep = any(heads.get(j) == h and pos[j - 1] == "AUX" for j in range(1, len(pos) + 1))
        cues["cop"] = ("aux_between_" if between_aux else ("aux_dep_" if aux_dep else "none_")) + order
    elif order == "pre" and hc not in ("VERB", "AUX"):
        cues["cop"] = "aux_between" if any(pos[j - 1] == "AUX" for j in range(i + 1, h)) else "none"
    else:
        cues["cop"] = "na"
    cues["case"] = "obj" if low in _OBJ_CASE else ("subj" if low in _SUBJ_CASE else "none")
    # ARGUMENT RANK (v3), PRECISION-GATED: the Competition Model first-noun/second-noun cue is over the verb ARGUMENTS,
    # not over tokens -- "criticized President Bush" must not make the object the SECOND post-verbal nominal. It is the
    # one arc-dependent addition, so where the governor does not believe its own attachment above RANK_TAU the cue
    # abstains and the arc-free cues decide (Ernst & Banks 2002 reliability weighting; the same self-gating the
    # structure / byhead agent cues use). Ungated it costs the LIVE copular subject read 0.667 -> 0.623.
    rank_on = v3 and (conf is None or float(conf.get(i, 1.0)) >= RANK_TAU)
    if order == "post":
        # ONE post-verbal SLOT cue (position x double-object configuration) -- rank and pairing are one coalition, not two
        # independent cues: as separate cues their contrasts double-counted "second post-verbal nominal" and pushed the
        # PATIENT of "give me a call" to OTHER (signal trace 2026-09-12). first/later = ARGUMENTS between the head and i
        # (v3) or nominal TOKENS (pre-v3); pair = a SECOND bare (no preposition) nominal dependent of the same head after
        # the verb (first-of-two + animate = the recipient, later-of-two = the patient).
        if rank_on and h and hc in _PRED_HC:
            between = sum(1 for j in range(h + 1, i) if heads.get(j) == h and is_arg_head(toks, pos, j))
        elif v3:                              # the gate suspends the SIBLING (arc) read, not the argument population
            between = sum(1 for j in range(h + 1, i) if is_arg_head(toks, pos, j))
        else:
            between = sum(1 for j in range(h + 1, i) if pos[j - 1] in NOMINAL)
        if v3:
            sibs = [j for j in range(h + 1, len(pos) + 1) if heads.get(j) == h and is_arg_head(toks, pos, j)
                    and j != i and _prep_of_v3(toks, pos, heads, j)[0] is None]
        else:
            sibs = [j for j in range(h + 1, len(pos) + 1) if heads.get(j) == h and pos[j - 1] in NOMINAL and j != i
                    and _prep_of(toks, pos, heads, j)[0] is None]
        pair = "pair" if (sibs and prep is None) else "single"
        cues["post_slot"] = ("first" if between == 0 else "later") + "_" + pair
    else:
        cues["post_slot"] = "na"
    # PRE-verbal argument RANK (v3): the active-filler configuration (Frazier & Clifton 1989) -- in "the aid THAT
    # Darfur needs" the NEAREST pre-verbal argument is the subject and the earlier one is the extracted object. The
    # pre-verbal side had no rank cue at all before.
    if rank_on and order == "pre" and hc in _PRED_HC and h:
        nearer = sum(1 for j in range(i + 1, h) if heads.get(j) == h and is_arg_head(toks, pos, j))
        cues["pre_rank"] = "nearest" if nearer == 0 else ("second" if nearer == 1 else "earlier")
    elif v3:
        cues["pre_rank"] = "na"
    a = lookup_animacy(low, pos[i - 1])
    an = a.get("animacy") if isinstance(a, dict) else None
    cues["animacy"] = "anim" if an == "animate" else ("inan" if an == "inanimate" else "unk")
    if low in _OBJ_CASE or low in _SUBJ_CASE:
        cues["animacy"] = "anim"            # personal pronouns are animate by form
    # VERB-FRAME cue (the Competition Model's verb-specific knowledge): does this head verb TAKE A RECIPIENT? Read from the
    # learned per-lemma argument-frame counts (frames[lemma] = [n_iobj, n_nominal_deps]) accrued from reading; "unk" = never seen.
    if hc in _PRED_HC and h and frames:
        fr = frames.get(lemma_verb(toks[h - 1]).lower())
        if fr and fr[1] >= 5:
            cues["frame"] = "ditrans" if fr[0] / fr[1] >= 0.05 else "mono"
        else:
            cues["frame"] = "unk"
    else:
        cues["frame"] = "na"
    if v4:
        # ---- CUE SET v4 (pri 108). Four changes, all inert on a pre-v4 asset.
        # (a) THE GENITIVE IS A CASE MARKER -- two new VALUES of the existing `case` cue.
        g = genitive_value(toks, pos, i)
        if g is not None:
            cues["case"] = g
        # (b) A RELATIVE PRONOUN IS THE FILLER OF A GAP, NOT A CASE-MARKED PHRASE. pri 103 stopped the surface case
        #     scan AT a relativizer; it never stopped it FOR one, so "an area THAT will need 15,000" read `to` --
        #     which marks the ANTECEDENT, two nouns to the left -- as `that`'s own case marker. Only a PIED-PIPED
        #     preposition immediately to its left can mark a wh-word ("in which", "to whom").
        if low in _WHREL and not (i >= 2 and pos[i - 2] == "ADP"):
            cues["prep"] = "none"
        # (c) THE ARC-FREE LICENSOR, READ ONLY WHERE THERE IS A CASE MARKER TO INTERPRET. A licensor cue answers
        #     "what licenses this marked phrase"; an UNMARKED nominal is filling a slot, not asking that question, so
        #     the cue abstains there. Measured: firing it on every nominal costs core-argument accuracy -0.0185
        #     CI-sep under gold heads; restricted to marked phrases it is +0.0084 n.s. and takes gold obl UP.
        cues["hostsurf"] = (host_surface(toks, pos, i)
                            if (g is not None or (cues["prep"] != "none"
                                                  and _prep_of_v3(toks, pos, heads, i)[0] is not None))
                            else "na")
        # (c2) THE COMPETING PRINCIPLE. Recency and Predicate Proximity are the two attachment preferences the parsing
        #      literature puts in competition, so both are available in the same situations -- i.e. wherever there is
        #      a case marker whose licensor is in question.
        cues["predprox"] = predicate_proximity(toks, pos, i) if cues["hostsurf"] != "na" else "na"
        # (d) THE PHRASAL VERB IS A STORED LEXICAL ITEM (MacWhinney's item-based constructions; pri 103's own queued
        #     alternate path). The lexical `prep` cue cannot tell the PARTICLE of "worked OUT a deal" from the case
        #     marker of "walked OUT of the room", so objects read as obliques. The distinction is a property of the
        #     VERB-PLUS-PARTICLE PAIR, so the cue VALUE is that pair, learned and shrunk like every other value.
        _pr = cues.get("prep", "none")
        cues["vprep"] = (lemma_verb(toks[h - 1]).lower() + "+" + _pr.split("_")[0]
                         if (h and 1 <= h <= len(pos) and pos[h - 1] in ("VERB", "AUX") and _pr not in ("none", "na"))
                         else "na")
    if USE_INDUCED_CATEGORY_CUE:
        cues["indcat"] = induced_category(low)
    return cues


_GLOBAL_CUES = frozenset({"hostsurf"})   # cues read UNCONDITIONALLY (key "GLOBAL|value"), not within the arc's configuration
_CLASS_ABSENT = -60.0      # log-prior of a class the loaded asset never accrued (it can never win the argmax)
_VALIDITY_ALPHA = 0.5      # add-alpha on the configuration distributions
_VALIDITY_M_SHRINK = 2.0   # Dirichlet pseudo-counts centring a cue value's distribution on its configuration's
# HIERARCHICAL CONFIGURATION BACKOFF (pri 103 round 2; 0.0 = the pre-2026-09-13 maths, byte-identical). Every
# secondary cue VALUE is already shrunk toward its configuration, but the CONFIGURATION itself got add-alpha and
# nothing else -- so a rare one (ADV_pre: 17 weighted decisions; the there-BE construction: 48) was estimated from
# almost no experience. A construction inherits its parent's expectations until experience overrides them (Goldberg
# 1995 inheritance; the usage-based result that construction learning is frequency-driven and item-based, so a
# low-frequency construction is UNDER-learned, not differently learned). Same Dirichlet maths one level up:
#     P(role | cfg) = (n_cfg + m * P(role | PARENT(cfg))) / (N_cfg + m)
# PARENT drops the construction suffix (VERB_post_ex -> VERB_post), then collapses the head class to PRED/NONPRED
# (ADV_pre -> NONPRED_pre). SWEPT 0/2/5/20/50/200/500/1000/3000: a saturating plateau over 200-1000 and a COLLAPSE at
# 3000 (gold subject recall -0.0112 CI-sep). The value comes from the ASSET (key "m_config_backoff"), so a pre-v3
# table carries none and the organ is unchanged.
_PRED_HC = ("VERB", "AUX")


def _parent_config(cfg):
    """(coarse parent, construction base or None), or None when the configuration has no parent."""
    base = cfg[:-3] if cfg.endswith("_ex") else cfg
    if "_" not in base or base.startswith("ROOT"):
        return None
    hc, order = base.rsplit("_", 1)
    return ("PRED" if hc in _PRED_HC else "NONPRED") + "_" + order, (base if base != cfg else None)


def strengths_from_counts(counts: Dict[str, object], m_config: float = 0.0) -> Dict[str, object]:
    """THE ONE implementation of the Competition-Model strength math (used by the offline learner AND the online accrual):
    prior = log P(role); config strength = log P(role|config) - log P(role); cue contrast = log P(role|config,value) -
    log P(role|config) with a Dirichlet prior centred on the configuration (m pseudo-counts); a value that ALWAYS fires within
    its configuration carries no information -> exactly 0. counts = {"prior": [K], "config": {cfg: [K]}, "cues": {cue: {"cfg|value": [K]}}}."""
    # K IS THE ASSET'S OWN CLASS SPACE, not the organ's (pri 108): a table accrued before the NMOD class carries 7-wide
    # count vectors, and reading K from it keeps every smoothing denominator -- hence every strength -- BYTE-IDENTICAL to
    # the pre-2026-09-14 organ. The vectors are then padded out to the organ's space with a never-winning prior, so an
    # older asset can no more emit the new class than it could before. Verified: 3224/3224 identical labels.
    K = len(np.asarray(counts["prior"], dtype=float)); a = _VALIDITY_ALPHA; m = _VALIDITY_M_SHRINK
    prior = np.asarray(counts["prior"], dtype=float); dec = prior.sum()
    logprior = np.log((prior + a) / (dec + a * K))
    par = {}
    if m_config > 0:                                   # parent distributions for the configuration backoff
        for cfg, vec in counts["config"].items():
            pc = _parent_config(cfg)
            if pc is None:
                continue
            coarse, base = pc
            par.setdefault(coarse, np.zeros(K))
            par[coarse] += np.asarray(vec, dtype=float)
            if base:
                par.setdefault(base, np.zeros(K))
                par[base] += np.asarray(vec, dtype=float)
        par = {k: (v + a) / (v.sum() + a * K) for k, v in par.items()}
    p_cfg = {}; strength = {"config": {}}
    for cfg, vec in counts["config"].items():
        v = np.asarray(vec, dtype=float); n = v.sum()
        back = None
        if m_config > 0:
            pc = _parent_config(cfg)
            if pc is not None:
                coarse, base = pc
                back = par.get(base) if (base and base in par) else par.get(coarse)
        probs = ((v + m_config * back) / (n + m_config)) if back is not None else ((v + a) / (n + a * K))
        p_cfg[cfg] = probs; strength["config"][cfg] = np.log(probs) - logprior
    for cue, vals in counts["cues"].items():
        strength[cue] = {}
        for key, vec in vals.items():
            cfg = key.split("|", 1)[0]; base = p_cfg.get(cfg)
            if base is None:
                continue
            v = np.asarray(vec, dtype=float); n = v.sum()
            if n >= np.asarray(counts["config"][cfg], dtype=float).sum():
                strength[cue][key] = np.zeros(K)
            else:
                probs = (v + m * base) / (n + m)
                strength[cue][key] = np.log(probs) - np.log(base)
    KK = len(ROLE_CLASSES)
    if KK > K:                                      # pad a legacy asset out to the organ's class space
        logprior = np.concatenate([logprior, np.full(KK - K, _CLASS_ABSENT)])
        for cue, vals in strength.items():
            for key, vec in vals.items():
                vals[key] = np.concatenate([vec, np.zeros(KK - K)])
    return {"prior": logprior, "strength": strength}


def _upgrade_counts(counts: Dict[str, object]) -> Dict[str, object]:
    """Grow an asset's count vectors to the organ's current class space (zeros for a class it never accrued), so the
    ONLINE path can accrue a class the offline table predates. Idempotent."""
    K = len(ROLE_CLASSES)

    def _p(v):
        return (list(v) + [0] * (K - len(v))) if len(v) < K else v
    counts["prior"] = _p(counts["prior"])
    for cfg, vec in counts["config"].items():
        counts["config"][cfg] = _p(vec)
    for cue, vals in counts["cues"].items():
        for key, vec in vals.items():
            vals[key] = _p(vec)
    return counts


def observe_role_outcome(toks: Sequence[str], pos: Sequence[str], heads: Dict[int, int], i: int, role: str,
                         table: Optional[Dict[str, object]] = None) -> None:
    """PLASTICITY (owner 2026-09-12: learning is never frozen): accrue ONE comprehension outcome -- nominal i was understood
    to bear `role` (a ROLE_CLASSES name) -- into the cue-validity COUNTS and recompute the strengths. The caller supplies the
    outcome from confirmed comprehension (a later agreement check, a resolved event, a correction); the organ never reads gold
    at inference. Persist with save_coarse_validities()."""
    tab = table or load_coarse_validities()
    if "counts" not in tab or not tab["counts"]:
        raise ValueError("this validity table carries no counts (rebuild it with tools/build_coarse_role_validities.py)")
    K = len(ROLE_CLASSES); k = ROLE_CLASSES.index(role)
    _upgrade_counts(tab["counts"])              # PLASTICITY covers the NEW class: a legacy table grows into the full space
    cs = tab.get("cue_set")
    cues = coarse_role_cues(toks, pos, heads, i, tab.get("lemma_frames"), cs in ("v3", "v4"), None, cs == "v4")
    c = tab["counts"]; cfg = cues["config"]
    c["prior"][k] += 1
    c["config"].setdefault(cfg, [0] * K)[k] += 1
    for cue, val in cues.items():
        if cue != "config":
            key = ("GLOBAL|" + val) if cue in _GLOBAL_CUES else (cfg + "|" + val)
            c["cues"].setdefault(cue, {}).setdefault(key, [0] * K)[k] += 1
    if _GLOBAL_CUES & set(cues):                 # the unconditioned base the GLOBAL contrasts are read against
        g = c["config"].setdefault("GLOBAL", [0] * K)
        g[k] += 1
    new = strengths_from_counts(c)
    tab["prior"] = new["prior"]; tab["strength"] = new["strength"]


def save_coarse_validities(path: Optional[str] = None, table: Optional[Dict[str, object]] = None) -> str:
    """Persist the (possibly online-updated) counts + strengths as the grown asset."""
    tab = table or load_coarse_validities(); p = path or _COARSE_VALIDITIES_PATH
    doc = {"source": "Competition-Model cue validities: counts accrued from reading / comprehension outcomes; strengths = "
                     "graded_role_assigner.strengths_from_counts(counts)", "roles": ROLE_CLASSES,
           "counts": tab.get("counts"), "prior": [float(x) for x in tab["prior"]],
           "strength": {c: {v: [float(x) for x in vec] for v, vec in vals.items()} for c, vals in tab["strength"].items()},
           "lemma_frames": tab.get("lemma_frames", {})}
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
    return p


def load_coarse_validities(path: Optional[str] = None) -> Dict[str, object]:
    """The learned validity table: {'prior': log P(role), 'strength': {'config': {cfg: log P(role|cfg) - log P(role)},
    cue: {'cfg|value': log P(role|cfg,value) - log P(role|cfg)}}} -- activation = prior + config + sum of contrasts."""
    global _COARSE_VALIDITIES_CACHE
    if path is None and _COARSE_VALIDITIES_CACHE is not None:
        return _COARSE_VALIDITIES_CACHE
    p = path or _COARSE_VALIDITIES_PATH
    with open(p, encoding="utf-8") as f:
        doc = json.load(f)
    if doc.get("counts"):
        built = strengths_from_counts(doc["counts"], float(doc.get("m_config_backoff", 0.0)))   # pure function of counts
        tab = {"prior": built["prior"], "strength": built["strength"], "counts": doc["counts"],
               "lemma_frames": doc.get("lemma_frames", {})}
    else:
        _K = len(doc["prior"]); _pad = max(0, len(ROLE_CLASSES) - _K)
        tab = {"prior": np.concatenate([np.asarray(doc["prior"], dtype=float), np.full(_pad, _CLASS_ABSENT)]),
               "strength": {c: {v: np.concatenate([np.asarray(vec, dtype=float), np.zeros(_pad)])
                                for v, vec in vals.items()} for c, vals in doc["strength"].items()},
               "lemma_frames": doc.get("lemma_frames", {})}
    tab["slot_capacity"] = (doc.get("counts") or {}).get("slot_capacity") or doc.get("slot_capacity")   # verb-frame capacity counts (pri 93)
    global _HAS_PRED_ROWS
    _HAS_PRED_ROWS = any(k.startswith("PRED_") for k in (tab["strength"].get("config") or {}))
    tab["cue_set"] = doc.get("cue_set")          # "v3" (pri 103) cue set + argument-head population; "v4" (pri 108) adds
    #                                              the genitive case values, the arc-free licensor cue and the NMOD class
    if path is None:
        _COARSE_VALIDITIES_CACHE = tab
    return tab


def coarse_role_supports(toks: Sequence[str], pos: Sequence[str], heads: Dict[int, int], i: int,
                         validities: Optional[Dict[str, object]] = None,
                         conf: Optional[Dict[int, float]] = None) -> Dict[str, np.ndarray]:
    """Per-cue support vectors over ROLE_CLASSES for nominal i: the learned strength vector of each fired cue value
    (plus the role prior). A cue value never seen in training contributes nothing (abstains)."""
    tab = validities or load_coarse_validities()
    cs = tab.get("cue_set")
    cues = coarse_role_cues(toks, pos, heads, i, tab.get("lemma_frames"), cs in ("v3", "v4"), conf, cs == "v4")
    S: Dict[str, np.ndarray] = {"prior": tab["prior"]}
    cfg = cues["config"]
    vec = tab["strength"].get("config", {}).get(cfg)
    if vec is not None:
        S["config"] = vec
    for c, v in cues.items():
        if c == "config":
            continue
        # every secondary cue is read WITHIN its configuration (head class x order): its strength is the CONTRAST
        # log P(role | config, value) - log P(role | config), so an uninformative/absent value contributes ~0 and the
        # majority class is not double-counted across redundant cues (the v2-naive table misfiled OBJ as OBL 1031x)
        # -- EXCEPT the arc-free LICENSOR cue (pri 108), which is read ARC-INDEPENDENTLY under the GLOBAL key:
        # log P(role | value) - log P(role). A cue whose whole purpose is to survive a WRONG arc must not be looked up
        # INSIDE the arc's configuration, because that is the wrong row exactly when the governor mis-attached.
        # Measured (UD-EWT test 700, gold heads): conditioned 0.7157 nmod / 0.9157 core, GLOBAL 0.7423 / 0.9207
        # (core +0.0135 CI[+0.0025,+0.0245] over the floor -- CI-separated UP, not merely not-down).
        vec = tab["strength"].get(c, {}).get(("GLOBAL|" + v) if c in _GLOBAL_CUES else f"{cfg}|{v}")
        if vec is not None:
            S[c] = vec
    return S


def coarse_role_posterior(toks: Sequence[str], pos: Sequence[str], heads: Dict[int, int], i: int,
                          validities: Optional[Dict[str, object]] = None,
                          conf: Optional[Dict[int, float]] = None) -> np.ndarray:
    """The graded role posterior (softmax of the additive cue competition) over ROLE_CLASSES."""
    S = coarse_role_supports(toks, pos, heads, i, validities, conf)
    return softmax(net_activation(S, {c: 1.0 for c in S}), gain=1.0)


# ===============================================================================================================
# THE DECISION TRAVELS WITH ITS CONFIDENCE (pri 106, 2026-09-14).
# Kiani & Shadlen 2009: the same accumulator that makes the choice carries the certainty -- here the MARGIN between
# the top two role activations. Ernst & Banks 2002 / Fetsch et al. 2011 / Ma-Beck-Latham-Pouget 2006: a downstream
# area weights each input by its reliability, trial by trial, and in a probabilistic population code the population
# GAIN is that reliability. So the organ must hand DOWN not just the MAP label but P(this label is right), and a
# consumer must be able to enter the role cue at that weight.
#
# RELIABILITY BELONGS TO THE DECISION THE CONSUMER READS, not to this organ's private 8-way alphabet. Measured on
# UD-EWT train through the live chain (74,608 decisions): the 8-way label is right 0.741 of the time, the coarse
# SUBJ/OBJ/OTHER parallelism class 0.802, the PATIENT flag 0.921 -- because OBJ<->OBL and SUBJ<->PASS_SUBJ
# confusions are harmless to a consumer that only asks "same grammatical class?". Calibrating on the 8-way label
# would UNDER-weight the cue a parallelism consumer actually uses, so three maps are kept.
#
# THE MAP IS COUNTS, AND IT IS PLASTIC: margin bin -> [n_correct, n_total]; r = add-alpha smoothed accuracy pulled
# toward the base rate, then pool-adjacent-violators so r is non-decreasing in the evidence balance. One
# `observe_margin_outcome` call per understood argument keeps it learning online; nothing is frozen.
# ===============================================================================================================
MARGIN_BIN_WIDTH = 0.05          # SWEPT 0.02 / 0.05 / 0.10 / 0.20 on the consumer (flat 0.02-0.10); 0.05 reported
MARGIN_REL_ALPHA = 4.0           # add-alpha pseudo-counts toward the base rate (SWEPT 1 / 4 / 16)
RELIABILITY_KINDS = ("role8", "aer_class", "patient")
_MARGIN_REL_PATHS = tuple(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", d,
                                       "role_margin_reliability_v1.json") for d in ("frontend_assets", "hook_state"))
_MARGIN_REL_CACHE: Optional[Dict[str, object]] = None


def role_margin(posterior) -> float:
    """The balance of evidence this decision carries: top-1 minus top-2 of the role posterior (Kiani & Shadlen's
    certainty read off the same accumulator that makes the choice)."""
    q = np.sort(np.asarray(posterior, dtype=float))
    return float(q[-1] - q[-2]) if len(q) >= 2 else 1.0


def _margin_bin(margin: float, width: float) -> int:
    return int(min(0.999999, max(0.0, float(margin))) / width)


def reliability_from_counts(counts: Dict[object, object], alpha: float = MARGIN_REL_ALPHA) -> Dict[int, float]:
    """bin -> r, a PURE FUNCTION OF THE COUNTS (the same discipline as the cue strengths): add-alpha smoothing
    toward the base rate, then pool-adjacent-violators so reliability never falls as the evidence balance grows."""
    c = {int(k): [float(v[0]), float(v[1])] for k, v in counts.items()}
    tot = sum(v[1] for v in c.values())
    base = (sum(v[0] for v in c.values()) / tot) if tot else 0.5
    bs = sorted(c)
    vals, wts, idx = [], [], []
    for b in bs:
        vals.append((c[b][0] + alpha * base) / (c[b][1] + alpha)); wts.append(c[b][1] + alpha); idx.append([b])
        while len(vals) > 1 and vals[-2] > vals[-1]:
            v2 = (vals[-2] * wts[-2] + vals[-1] * wts[-1]) / (wts[-2] + wts[-1])
            w2 = wts[-2] + wts[-1]; i2 = idx[-2] + idx[-1]
            vals[-2:] = [v2]; wts[-2:] = [w2]; idx[-2:] = [i2]
    out: Dict[int, float] = {}
    for v, group in zip(vals, idx):
        for b in group:
            out[b] = float(v)
    return out


def load_margin_reliability(path: Optional[str] = None) -> Optional[Dict[str, object]]:
    """The margin->reliability maps. Returns None when no asset is on disk, in which case every `margin_reliability`
    call returns 1.0 and every consumer is byte-identical to the pre-2026-09-14 behaviour."""
    global _MARGIN_REL_CACHE
    if path is None and _MARGIN_REL_CACHE is not None:
        return _MARGIN_REL_CACHE if _MARGIN_REL_CACHE else None
    cands = (path,) if path else (os.environ.get("HDLAB_ROLE_MARGIN_RELIABILITY"),) + _MARGIN_REL_PATHS
    doc = None
    for p in cands:
        if p and os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                doc = json.load(f)
            break
    if doc is None:
        if path is None:
            _MARGIN_REL_CACHE = {}
        return None
    tab = {"width": float(doc.get("width", MARGIN_BIN_WIDTH)), "alpha": float(doc.get("alpha", MARGIN_REL_ALPHA)),
           "counts": {k: {int(b): [float(x[0]), float(x[1])] for b, x in doc["maps"][k]["counts"].items()}
                      for k in RELIABILITY_KINDS if k in doc.get("maps", {})}}
    tab["table"] = {k: reliability_from_counts(v, tab["alpha"]) for k, v in tab["counts"].items()}
    if path is None:
        _MARGIN_REL_CACHE = tab
    return tab


def margin_reliability(margin: float, kind: str = "aer_class", table: Optional[Dict[str, object]] = None) -> float:
    """P(the decision of this KIND is right | this margin). 1.0 when no map is on disk (the cue then enters at its
    landed full strength, so an un-upgraded deployment is unchanged)."""
    tab = table if table is not None else load_margin_reliability()
    if not tab or kind not in tab.get("table", {}):
        return 1.0
    t = tab["table"][kind]
    if not t:
        return 1.0
    b = _margin_bin(margin, tab["width"])
    if b in t:
        return float(t[b])
    ks = sorted(t)
    return float(t[ks[0]] if b < ks[0] else t[ks[-1]])


def observe_margin_outcome(margin: float, correct: bool, kind: str = "aer_class",
                           table: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    """PLASTICITY: accrue ONE comprehension outcome -- a role decision taken at `margin` turned out right or wrong --
    into the reliability counts, and recompute r (a pure function of the counts). The caller supplies the outcome
    from confirmed comprehension, exactly as `observe_role_outcome` does; no gold is read at inference. Persist with
    save_margin_reliability()."""
    tab = table if table is not None else load_margin_reliability()
    if not tab:
        tab = {"width": MARGIN_BIN_WIDTH, "alpha": MARGIN_REL_ALPHA,
               "counts": {k: {} for k in RELIABILITY_KINDS}, "table": {k: {} for k in RELIABILITY_KINDS}}
        global _MARGIN_REL_CACHE
        _MARGIN_REL_CACHE = tab
    c = tab["counts"].setdefault(kind, {}).setdefault(_margin_bin(margin, tab["width"]), [0.0, 0.0])
    c[0] += float(bool(correct)); c[1] += 1.0
    tab["table"][kind] = reliability_from_counts(tab["counts"][kind], tab["alpha"])
    return tab


def save_margin_reliability(path: Optional[str] = None, table: Optional[Dict[str, object]] = None) -> str:
    tab = table if table is not None else load_margin_reliability()
    p = path or _MARGIN_REL_PATHS[0]
    doc = {"width": tab["width"], "alpha": tab["alpha"], "cue_set": (load_coarse_validities() or {}).get("cue_set"),
           "source": "P(the Competition-Model role decision is right | its margin), counts accrued from comprehension "
                     "outcomes; r = add-alpha smoothed accuracy per margin bin, monotone by pool-adjacent-violators.",
           "maps": {k: {"counts": {str(b): [v[0], v[1]] for b, v in sorted(tab["counts"][k].items())},
                        "table": {str(b): round(r, 6) for b, r in sorted(tab["table"][k].items())}}
                    for k in tab["counts"]}}
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
    return p


_MEAN_LLR_CACHE: Dict[str, float] = {}


def _llr_weight(r: float, k: int) -> float:
    """The evidence a categorical observation of reliability r carries over k alternatives, in log-odds:
    log P(label | true = label) - log P(label | true != label) = log( r (k-1) / (1-r) ). This is Ernst-Banks in
    the discrete case -- an AMOUNT OF EVIDENCE, not a shrinkage factor."""
    r = min(max(float(r), 1e-6), 1.0 - 1e-6)
    return float(np.log(r * (k - 1) / (1.0 - r)))


def reliability_gain(margin: float, kind: str = "aer_class", n_alt: int = 3,
                     table: Optional[Dict[str, object]] = None) -> float:
    """THE POPULATION GAIN (Ma, Beck, Latham & Pouget 2006: in a probabilistic population code the gain of a
    population IS its precision, and summing gain-scaled log-likelihoods performs the Bayesian product). Returns
    the log-odds evidence of this decision DIVIDED by the average over the whole reliability map, so the cue enters
    at gain 1 ON AVERAGE and only its per-decision VARIATION can move a consumer. 1.0 when no map is on disk."""
    tab = table if table is not None else load_margin_reliability()
    if not tab or kind not in tab.get("table", {}):
        return 1.0
    key = "%s|%d" % (kind, n_alt)
    if key not in _MEAN_LLR_CACHE:
        t = tab["table"][kind]; c = tab["counts"][kind]
        num = sum(_llr_weight(v, n_alt) * c[b][1] for b, v in t.items())
        den = sum(c[b][1] for b in t)
        _MEAN_LLR_CACHE[key] = (num / den) if den else 1.0
    m = _MEAN_LLR_CACHE[key] or 1.0
    # The gain IS the reliability (Ma et al.: the population's gain is its precision), expressed relative to the
    # map's MEAN log-odds evidence -- a per-cue constant, itself a pure function of the counts, that puts the two
    # role cues on a comparable scale before the consumer's swept weight multiplies them. Both cues have their own
    # constant, so a single swept gamma could not absorb them.
    return float(margin_reliability(margin, kind, tab) / m)


def calibrated_class_posterior(posterior, class_of: Sequence[str], r: float) -> Dict[str, float]:
    """P(true class) for a COARSE class alphabet a consumer reads (class_of[k] = the class of ROLE_CLASSES[k]):
    the MAP class takes the count-calibrated mass r, and the remaining 1-r is spread over the other classes in the
    SHAPE the organ's own posterior gives them. CALIBRATE, DO NOT MARGINALISE: pri 103 measured that the raw softmax
    mass is mis-centred (marginalising the head posterior cost 0.027), so its LEVEL is replaced and only its
    RELATIVE shape among the alternatives is kept."""
    p = np.asarray(posterior, dtype=float)
    classes = []
    for c in class_of:
        if c not in classes:
            classes.append(c)
    mass = {c: float(sum(x for x, cc in zip(p, class_of) if cc == c)) for c in classes}
    mc = class_of[int(np.argmax(p))]
    rest = sum(v for c, v in mass.items() if c != mc)
    out = {}
    for c in classes:
        if c == mc:
            out[c] = float(r)
        elif rest > 1e-12:
            out[c] = float((1.0 - r) * mass[c] / rest)
        else:
            out[c] = float((1.0 - r) / max(1, len(classes) - 1))
    return out


def role_decision(toks: Sequence[str], pos: Sequence[str], heads: Dict[int, int], i: int,
                  validities: Optional[Dict[str, object]] = None, conf: Optional[Dict[int, float]] = None,
                  reliability: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    """THE GRADED HAND-OFF a consumer should read instead of the bare label string: the MAP role and its UD-shaped
    dep, the full posterior, the decision's own MARGIN, and P(right) for each kind of decision downstream makes."""
    tab = validities or load_coarse_validities()
    p = np.asarray(coarse_role_posterior(toks, pos, heads, i, tab, conf), dtype=float)
    k = int(np.argmax(p)); m = role_margin(p)
    rel = reliability if reliability is not None else load_margin_reliability()
    return {"role": ROLE_CLASSES[k], "dep": ROLE_TO_DEP[ROLE_CLASSES[k]], "posterior": p, "margin": m,
            "reliability": {kind: margin_reliability(m, kind, rel) for kind in RELIABILITY_KINDS}}


# ===============================================================================================================
# THE PATIENT RELIABILITY THE CONSUMER ACTUALLY ASKS FOR (pri 129, 2026-09-15).
# The who-did-what defer used to score its arc with hdlab.parse_confidence -- a logistic FITTED OFFLINE on the
# arc-eager parser's conf/marg, i.e. on a DIFFERENT parser's features than the live attachment arm now hands
# down.  Two things are wrong with it and one is measurable: (a) it is a fitted readout bolted on after the
# decision, not the deciding accumulator's own certainty (Kiani & Shadlen 2009); (b) the reliability it
# calibrates is of the ORGAN's private 8-way label, while the consumer asks a DIFFERENT question -- "is this
# token the verb's patient".  This module's own §"RELIABILITY BELONGS TO THE DECISION THE CONSUMER READS" says
# so; the margin does not answer it (measured: margin AUC 0.4962, margin-reliability 0.4827 -- at chance,
# because a LARGE margin can mean confidently-OBL).
#
# THE OPERATION.  The consumer's question is a conjunction of two beliefs the competition already holds:
#     P(pk is the patient of v)  =  P(role(pk) in {OBJ, PASS_SUBJ})  x  P(pk wins v's object slot)
# Factor 1 is this organ's posterior for pk, marginalised over the heads rung's P(head | dep) when the
# attachment arm hands one down.  Factor 2 is the SLOT-LEVEL competition -- one object slot, several nominal
# claimants, normalised against each other (Vosse & Kempen 2000 competitive unification; the same
# winner-take-all normalisation `graded_pick` performs over candidates).  ZERO fitted parameters; both factors
# are pure functions of the count-accrued cue validities, so `observe_role_outcome` keeps them plastic.
#
# MEASURED (UD-EWT test, n=1247 patient items the live chain decides, sentence-clustered paired bootstrap,
# experiments/exp_labels_rung_to_live_consumers_v1.py --patient):
#     right-vs-wrong AUC  0.8127  vs the fitted logistic 0.7613  (+0.0517 CI95 [+0.0136, +0.0882])
#     belief alone        0.7861  (+0.0241 CI95 [-0.0141, +0.0629] -- the SLOT factor is what separates)
#     permuted twin       0.4764  (chance)
#     selective accuracy @50% coverage 0.9470 vs 0.9133 (blanket 0.8148); @67% 0.9234 vs 0.9078
# ===============================================================================================================
PATIENT_CLASSES = ("OBJ", "PASS_SUBJ")
SLOT_HEAD_MIN_P = 0.05        # a nominal enters the object-slot competition at this much head mass (swept 0.02/0.05/0.2, flat)


def patient_belief(toks: Sequence[str], pos: Sequence[str], heads: Dict[int, int], i: int,
                   head_post: Optional[Dict[int, Dict[int, float]]] = None,
                   conf: Optional[Dict[int, float]] = None,
                   validities: Optional[Dict[str, object]] = None) -> float:
    """P(token i bears a PATIENT role) = the competition's OBJ + PASS_SUBJ mass, marginalised over the heads
    rung's posterior for i when one is supplied (the graded hand-off)."""
    ix = {r: k for k, r in enumerate(ROLE_CLASSES)}
    hpd = (head_post or {}).get(i)
    p = (coarse_role_posterior_headmarg(toks, pos, heads, i, hpd, validities, conf=conf) if hpd
         else coarse_role_posterior(toks, pos, heads, i, validities, conf))
    return float(sum(p[ix[c]] for c in PATIENT_CLASSES))


def patient_slot_confidence(toks: Sequence[str], pos: Sequence[str], heads: Dict[int, int],
                            v: int, pk: int,
                            head_post: Optional[Dict[int, Dict[int, float]]] = None,
                            conf: Optional[Dict[int, float]] = None,
                            validities: Optional[Dict[str, object]] = None) -> Optional[float]:
    """THE RELIABILITY OF THE WHO-DID-WHAT PATIENT DECISION (1-based v, pk), in [0,1], or None when pk is out
    of range.  P(patient role) x P(wins the object slot) -- see the section note above.  This REPLACES
    hdlab.parse_confidence.calibrated_patient_confidence for the reader's defer."""
    n = len(toks)
    if not (1 <= pk <= n) or not (1 <= v <= n):
        return None
    tab = validities or load_coarse_validities()
    pp = patient_belief(toks, pos, heads, pk, head_post, conf, tab)
    cands = [c for c in range(1, n + 1)
             if pos[c - 1] in NOMINAL and (heads.get(c) == v
                                           or (head_post or {}).get(c, {}).get(v, 0.0) >= SLOT_HEAD_MIN_P)]
    if pk not in cands:
        cands.append(pk)
    tot = 0.0
    for c in cands:
        tot += pp if c == pk else patient_belief(toks, pos, heads, c, head_post, conf, tab)
    return float(pp * (pp / tot)) if tot > 0 else 0.0


def defer_below(confidence: Optional[float], threshold: Optional[float]) -> bool:
    """THE OPT-OUT (Kiani & Shadlen 2009 / Kepecs 2008): do not hard-commit a decision whose own reliability is
    below `threshold`; Friston's precision-weighting in its discrete limit.  threshold=None -> never defer, so an
    un-flipped deployment is byte-identical.  Lives HERE, next to the organ that PRODUCES the confidence, so a
    consumer that defers never has to import the retired fitted readout for a two-line comparison (pri 129: the
    reader's defer branch still did `from hdlab.parse_confidence import defer`, which would have re-imported a
    NOT_BF module the instant anyone set a tau -- invisible today only because the default is None)."""
    if threshold is None or confidence is None:
        return False
    return float(confidence) < float(threshold)


# ===============================================================================================================
# THE PURPOSE / COMPLEMENT ARM (pri 129).  The goal register's ADVCL purpose filter used to reject a "to VINF"
# site by reading the frozen perceptron's deprel (xcomp/ccomp/acl => a complement, not a purpose adjunct).  The
# brain does not run a relation classifier for this: infinitive attachment is LEXICALIST CONSTRAINT SATISFACTION
# -- the governing verb's stored subcategorization frame decides complement-vs-adjunct (MacDonald, Pearlmutter &
# Seidenberg 1994; Trueswell 1996; Garnsey et al. 1997), settled by competition (Vosse & Kempen 2000).  So it is
# an ARM OF THIS ORGAN, with the same machinery: cue values read from the categories organ / the attachment arm /
# the stored verb frame, strengths = configuration-conditioned CONTRASTS accrued from counts, additive activation
# -> softmax.  No new classifier family, no fitted weight, and `observe_purpose_outcome` keeps it learning.
#
# MEASURED (the population goal_register branch (3) actually reaches; fit on UD-EWT train, tau + cue set
# selected on a train-internal dev split, reported on UD-EWT TEST -- see SOLVED.md for the numbers).
# ===============================================================================================================
PURPOSE_CLASSES = ("complement", "purpose")
_PURPOSE_PATHS = tuple(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", d,
                                    "purpose_complement_validities_ud_ewt.json")
                       for d in ("frontend_assets", "hook_state"))
_PURPOSE_CACHE: Optional[Dict[str, object]] = None


def load_purpose_validities(path: Optional[str] = None) -> Optional[Dict[str, object]]:
    """The purpose/complement cue table, or None when no asset is on disk -- in which case every
    `purpose_complement_posterior` call returns None and the goal filter falls through exactly as an unlabeled
    deprel did (so an un-upgraded deployment is unchanged)."""
    global _PURPOSE_CACHE
    if path is None and _PURPOSE_CACHE is not None:
        return _PURPOSE_CACHE or None
    for p in ((path,) if path else (os.environ.get("HDLAB_PURPOSE_VALIDITIES"),) + _PURPOSE_PATHS):
        if p and os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                tab = json.load(f)
            if path is None:
                _PURPOSE_CACHE = tab
            return tab
    if path is None:
        _PURPOSE_CACHE = {}
    return None


def purpose_cues(toks: Sequence[str], pos: Sequence[str], to_i: int, mv_i: int,
                 heads: Dict[int, int], subcat=None):
    """(configuration, {cue: value}) for the infinitival marker at 0-based `to_i` governed by the verb at
    0-based `mv_i`.  CONFIGURATION = the unification window between governor and marker; every cue comes from
    the categories organ, the attachment arm's heads, or the stored verb frame.  Arc-light and glass-box."""
    from hdlab.goal_register import _lemma as _gl   # the SAME key the validity counts were accrued under
    n = len(toks)
    low = [t.lower() for t in toks]
    mv = low[mv_i]
    mvl = _gl(mv)
    pc = None
    if subcat is not None:
        pc = subcat.p_complement(mv)
        if pc is None:
            pc = subcat.p_complement(mvl)
    between = list(pos[mv_i + 1:to_i])
    if not between:
        cfg = "adjacent"
    elif all(c in NOMINAL or c in ("DET", "ADJ", "NUM") for c in between):
        cfg = "objonly"                                  # object control: "told HIM to go"
    elif any(c == "ADP" for c in between):
        cfg = "pp"                                       # "went to the market to buy"
    else:
        cfg = "other"
    h = heads.get(to_i + 2, 0)
    return cfg, {
        "frame": "na" if pc is None else ("hi" if pc >= 0.7 else "mid" if pc >= 0.4 else "lo"),
        "prev": pos[to_i - 1] if to_i - 1 >= 0 else "NONE",
        "dist": "0" if (to_i - mv_i) == 1 else "1" if (to_i - mv_i) == 2 else "2" if (to_i - mv_i) <= 4 else "3+",
        "headcat": (pos[h - 1] if h and 1 <= h <= n else "ROOT"),
        "headismv": "1" if h == mv_i + 1 else "0",
        "post": "end" if (to_i + 2 >= n or all(pos[k] == "PUNCT" for k in range(to_i + 2, n)))
                else pos[min(to_i + 2, n - 1)],
        "mvlem": mvl,
        "hasobj": "1" if any(pos[k] in NOMINAL for k in range(mv_i + 1, to_i)) else "0",
        "comma": "1" if (to_i - 1 >= 0 and low[to_i - 1] == ",") else "0",
    }


def purpose_complement_posterior(cfg: str, cues: Dict[str, str],
                                 table: Optional[Dict[str, object]] = None) -> Optional[float]:
    """P(this 'to VINF' is a COMPLEMENT, not a purpose adjunct) from the additive cue competition, or None when
    no validity asset is on disk.  A cue value never seen enough times in the counts contributes nothing."""
    tab = table if table is not None else load_purpose_validities()
    if not tab:
        return None
    drop = set(tab.get("dropped_cues") or ())
    A = np.array(tab["cfg"].get(cfg) or tab["prior"], dtype=float)
    for cn, cv in cues.items():
        if cn in drop:
            continue
        s = tab["strength"].get("%s|%s|%s" % (cn, cfg, cv))
        if s is not None:
            A = A + np.array(s, dtype=float)
    return float(softmax(A, gain=1.0)[0])


def observe_purpose_outcome(cfg: str, cues: Dict[str, str], outcome: str,
                            table: Optional[Dict[str, object]] = None) -> Optional[Dict[str, object]]:
    """PLASTICITY: accrue ONE confirmed comprehension outcome ('complement' / 'purpose') into the purpose arm's
    counts and recompute its strengths (a pure function of the counts, like every other table here).  Persist
    with `save_purpose_validities`.  No gold is read at inference -- the caller supplies the outcome."""
    tab = table if table is not None else load_purpose_validities()
    if not tab:
        return None
    a = float(tab.get("alpha", 1.0))
    k = len(PURPOSE_CLASSES)
    tab["counts"]["cfg"].setdefault(cfg, {})
    tab["counts"]["cfg"][cfg][outcome] = tab["counts"]["cfg"][cfg].get(outcome, 0) + 1
    for cn, cv in cues.items():
        key = "%s|%s|%s" % (cn, cfg, cv)
        tab["counts"]["cue"].setdefault(key, {})
        tab["counts"]["cue"][key][outcome] = tab["counts"]["cue"][key].get(outcome, 0) + 1
    pri = {c: 0 for c in PURPOSE_CLASSES}
    for v in tab["counts"]["cfg"].values():
        for c, x in v.items():
            pri[c] = pri.get(c, 0) + x
    tot = sum(pri.values())
    tab["prior"] = [float(np.log((pri.get(c, 0) + a) / (max(1, tot) + a * k))) for c in PURPOSE_CLASSES]
    for key, v in tab["counts"]["cfg"].items():
        t = sum(v.values())
        tab["cfg"][key] = [float(np.log((v.get(c, 0) + a) / (t + a * k))) for c in PURPOSE_CLASSES]
    mc = int(tab.get("min_count", 3))
    tab["strength"] = {}
    for key, v in tab["counts"]["cue"].items():
        t = sum(v.values())
        if t < mc:
            continue
        base = tab["cfg"].get(key.split("|")[1]) or tab["prior"]
        tab["strength"][key] = [float(np.log((v.get(c, 0) + a) / (t + a * k)) - base[ci])
                                for ci, c in enumerate(PURPOSE_CLASSES)]
    return tab


def save_purpose_validities(path: Optional[str] = None, table: Optional[Dict[str, object]] = None) -> str:
    tab = table if table is not None else load_purpose_validities()
    p = path or _PURPOSE_PATHS[0]
    with open(p, "w", encoding="ascii", newline="\n") as f:
        json.dump(tab, f, indent=1, sort_keys=True)
    return p


def coarse_role_posterior_tagmarg(toks: Sequence[str], pos: Sequence[str], heads: Dict[int, int], i: int,
                                  tag_post: np.ndarray, tag_labels: Sequence[str],
                                  validities: Optional[Dict[str, object]] = None, min_p: float = 0.02) -> np.ndarray:
    """GRADED UPSTREAM HAND-OFF (signal trace 2026-09-12): the head-class configuration cue reads the HEAD token's CATEGORY
    as a DISTRIBUTION (the tagger's per-token posterior, rows = tokens, cols = tag_labels) instead of a hard tag:
    posterior(role) = SUM_c P(head tag = c) * posterior(role | config built with head class c). Only head classes with
    P >= min_p are expanded (the rest is renormalised away). Falls back to the hard read when the head is the root."""
    h = heads.get(i, 0) or 0
    if not h or h < 1 or h > len(pos):
        return coarse_role_posterior(toks, pos, heads, i, validities)
    tab = validities or load_coarse_validities()
    row = tag_post[h - 1]
    out = np.zeros(len(ROLE_CLASSES)); tot = 0.0
    pos_l = list(pos)
    for c, pc in zip(tag_labels, row):
        if pc < min_p:
            continue
        pos_l[h - 1] = c
        S = coarse_role_supports(toks, pos_l, heads, i, tab)
        out += pc * softmax(net_activation(S, {k: 1.0 for k in S}), gain=1.0); tot += pc
    return out / tot if tot > 0 else coarse_role_posterior(toks, pos, heads, i, validities)


HEAD_POSTERIOR_MIN_P = 0.05     # heads below this posterior mass are dropped from the marginalisation (renormalised)


def coarse_role_posterior_headmarg(toks: Sequence[str], pos: Sequence[str], heads: Dict[int, int], i: int,
                                   head_post: Dict[int, float], validities: Optional[Dict[str, object]] = None,
                                   min_p: float = HEAD_POSTERIOR_MIN_P,
                                   conf: Optional[Dict[int, float]] = None) -> np.ndarray:
    """P(role | token i) MARGINALISED over the head posterior head_post = {h: P(h | i)} (the heads rung hands DOWN a
    distribution, not a point -- spec RESEARCH_attachment_organ_spec s3): sum_h P(h|i) * P(role | config built with h);
    the other tokens keep their MAP heads. Measured (probe v19, UD-EWT test 8362 nominals): over the BF attachment arm's
    heads 0.7260 vs hard head 0.7129 (+0.013); over near-certain supervised heads +0.0016 -- the graded read matters
    exactly when the upstream rung is uncertain. Falls back to the hard-head posterior when no head carries mass."""
    tab = validities or load_coarse_validities()
    out = np.zeros(len(ROLE_CLASSES)); tot = 0.0
    for h, p in sorted(head_post.items(), key=lambda kv: -kv[1]):
        if p < min_p or h == i:
            continue
        hh = dict(heads); hh[i] = int(h)
        S = coarse_role_supports(toks, pos, hh, i, tab, conf)
        out += p * softmax(net_activation(S, {c: 1.0 for c in S}), gain=1.0); tot += p
    if tot <= 0:
        return coarse_role_posterior(toks, pos, heads, i, tab, conf)
    return out / tot


def _frame_slots(toks, pos, heads, verb_idx, tab):
    """The core slots the verb's FRAME licenses (its valence, from the organ's own lemma_frame counts). Every verb has
    {subj, obj, byagent}; the RECIPIENT slot (iobj) exists ONLY for verbs whose learned frame takes an indirect object (the same
    ditransitive threshold the `frame` cue uses). A monotransitive verb has NO iobj slot -> a post-verbal animate nominal cannot
    be a recipient; it takes the object, and a second bare nominal is displaced to an oblique/adjunct."""
    slots = {"subj", "obj", "byagent"}
    frames = (tab or {}).get("lemma_frames") or {}
    fr = frames.get(lemma_verb(toks[verb_idx - 1]).lower())
    if fr and fr[1] >= 5 and fr[0] / fr[1] >= 0.05:
        slots.add("iobj")
    return slots


def _slot_capacity(tab):
    """lambda[slot] from the asset's accrued slot-cardinality counts (a pure function of counts, like the cue strengths);
    a uniform fallback if an older asset carries none."""
    sc = (tab or {}).get("slot_capacity")
    if not sc:
        return {s: 5.0 for s in CORE_SLOTS}
    a = 0.5
    return {s: float(-np.log((sc[s][1] + a) / (sc[s][0] + a))) for s in CORE_SLOTS}


def _mask_ineligible(A, elig):
    A = np.asarray(A, dtype=float).copy()
    for r in range(len(ROLE_CLASSES)):
        slot = ROLE_TO_SLOT.get(ROLE_CLASSES[r])
        if slot is not None and slot not in elig:
            A[r] = _NEG_INF
    return A


def assign_slots_hard(A_by_i, elig):
    """HARD capacity-one greedy joint assignment over the verb's LICENSED slots: assign the globally most-confident (nominal,
    licensed-role) first; once a core slot is taken, later nominals take their best AVAILABLE role (uncapped OBL/OTHER always
    available). Displaced core fillers fall to oblique."""
    Am = {i: _mask_ineligible(A, elig) for i, A in A_by_i.items()}
    assigned, taken, remaining = {}, set(), set(Am)
    while remaining:
        best = None
        for i in remaining:
            for r in range(len(ROLE_CLASSES)):
                slot = ROLE_TO_SLOT.get(ROLE_CLASSES[r])
                if slot is not None and slot in taken:
                    continue
                if best is None or float(Am[i][r]) > best[2]:
                    best = (i, r, float(Am[i][r]))
        i, r, _ = best
        assigned[i] = r
        slot = ROLE_TO_SLOT.get(ROLE_CLASSES[r])
        if slot is not None:
            taken.add(slot)
        remaining.discard(i)
    return assigned


def assign_slots_incr(A_by_i, order, elig, lam, kappa=1.0):
    """SOFT incremental occupancy (left-to-right = 'occupied incrementally'): each nominal's core-role activation is lowered by
    kappa*lambda[slot]*occupancy_belief; the chosen core role adds its posterior mass to that slot. kappa=0 recovers the
    independent read; large -> hard. Frame-ineligible roles masked."""
    assigned, occ = {}, {}
    for i in order:
        A = _mask_ineligible(A_by_i[i], elig)
        for r in range(len(ROLE_CLASSES)):
            slot = ROLE_TO_SLOT.get(ROLE_CLASSES[r])
            if slot is not None and occ.get(slot, 0.0) > 0 and A[r] > _NEG_INF / 2:
                A[r] -= kappa * lam.get(slot, 0.0) * occ[slot]
        r = int(np.argmax(A)); assigned[i] = r
        slot = ROLE_TO_SLOT.get(ROLE_CLASSES[r])
        if slot is not None:
            occ[slot] = occ.get(slot, 0.0) + float(softmax(A)[r])
    return assigned


def observe_frame_outcome(slot_counts_per_verb, table=None):
    """PLASTICITY: accrue one comprehension outcome -- {slot: n_fillers} for an understood verb frame -- into the slot-capacity
    counts. n1 += 1 per slot with >=1 filler; n2 += 1 per slot with >=2. lambda is then a pure function of the counts
    (see _slot_capacity). Persist with save_coarse_validities()."""
    tab = table or load_coarse_validities()
    sc = tab.setdefault("slot_capacity", {s: [0, 0] for s in CORE_SLOTS})
    for slot, n in slot_counts_per_verb.items():
        if slot in sc:
            sc[slot][0] += 1
            if n >= 2:
                sc[slot][1] += 1
    return tab


def coarse_roles(toks: Sequence[str], pos: Sequence[str], heads: Dict[int, int],
                 validities: Optional[Dict[str, object]] = None,
                 head_posterior: Optional[Dict[int, Dict[int, float]]] = None,
                 conf: Optional[Dict[int, float]] = None) -> Dict[int, str]:
    """Coarse grammatical-role labels (UD-shaped strings) for every NOMINAL token (1-based index -> dep) by cue
    competition: the MAP of the additive cue activation. OTHER -> 'dep' (the organ labels ARGUMENT roles; a consumer
    needing fine non-argument relations keeps its own source for 'dep'). Non-nominal tokens are not labelled.
    head_posterior = {dep: {head: P}} (optional, from the attachment arm): the role read is then MARGINALISED over the
    head posterior (coarse_role_posterior_headmarg) -- the graded hand-off; None = the hard head (byte-identical to before)."""
    tab = validities or load_coarse_validities()
    v3 = tab.get("cue_set") in ("v3", "v4")
    out: Dict[int, str] = {}
    # THE ARGUMENT-HEAD POPULATION (v3): the brain labels whatever FILLS the slot, so a quantifier / numeral /
    # nominalised-adjective phrase head is labelled too. Pre-v3 tables keep the NOUN/PROPN/PRON population exactly.
    # THE HEADS RUNG'S GRADED HAND-OFF IS A RELIABILITY SIGNAL HERE, NOT A MIXTURE (measured, pri 103): marginalising
    # the role read over the attachment posterior costs the LIVE core role recall 0.7224 -> 0.6952 (and costs the
    # pre-v3 cue set 0.7250 -> 0.6970) -- the attachment arm's posterior is BROAD and MIS-CENTRED, not narrow and
    # uncertain (at P >= 0.95 the head is still only 74% correct, AUC 0.678), so the alternative mass is not the right
    # head and averaging dilutes the correct MAP reads without rescuing the wrong ones. Under a v3 table the posterior
    # therefore precision-gates the arc-dependent rank cue and the read stays on the MAP head. Pre-v3 tables keep the
    # marginalising path exactly as landed.
    if conf is None and head_posterior:
        conf = {i: float((head_posterior.get(i) or {}).get(heads.get(i, 0), 1.0)) for i in head_posterior}
    # per-nominal activation vectors (honouring the graded head hand-off where a posterior is given)
    A_by_i: Dict[int, np.ndarray] = {}
    for i in range(1, len(toks) + 1):
        if i - 1 >= len(pos):
            continue
        if not (is_arg_head(toks, pos, i) if v3 else pos[i - 1] in NOMINAL):
            continue
        hp = None if v3 else (head_posterior.get(i) if head_posterior else None)
        if hp:
            A_by_i[i] = np.log(np.asarray(
                coarse_role_posterior_headmarg(toks, pos, heads, i, hp, tab, conf=conf), dtype=float) + 1e-12)
        else:
            S = coarse_role_supports(toks, pos, heads, i, tab, conf)
            A_by_i[i] = np.asarray(net_activation(S, {c: 1.0 for c in S}), dtype=float)
    if not SLOT_OCCUPANCY:                                   # the independent per-nominal read (the pre-2026-09-13 behaviour)
        for i, A in A_by_i.items():
            out[i] = ROLE_TO_DEP[ROLE_CLASSES[int(np.argmax(A))]]
        return out
    # JOINT frame-slot decode (owner-DONE pri 93): group each verb's nominal dependents, assign under capacity-one per slot
    lam = _slot_capacity(tab); groups: Dict[int, list] = {}; grouped = set()
    for i in A_by_i:
        h = heads.get(i, 0) or 0
        if h and 1 <= h <= len(pos) and pos[h - 1] in ("VERB", "AUX"):
            groups.setdefault(h, []).append(i)
    for h, members in groups.items():
        members = sorted(members)
        if head_posterior and any(float((head_posterior.get(i) or {}).get(h, 1.0)) < OCC_MIN_P for i in members):
            continue                                             # the governor is not sure these are siblings: independent read
        grouped.update(members)
        elig = _frame_slots(toks, pos, heads, h, tab)
        sub = {i: A_by_i[i] for i in members}
        asg = assign_slots_hard(sub, elig) if OCC_MODE == "hard" else assign_slots_incr(sub, members, elig, lam, OCC_KAPPA)
        for i, r in asg.items():
            out[i] = ROLE_TO_DEP[ROLE_CLASSES[r]]
    for i, A in A_by_i.items():                              # nominals not governed by a verb: independent read
        if i not in grouped:
            out[i] = ROLE_TO_DEP[ROLE_CLASSES[int(np.argmax(A))]]
    return out


DEP_TO_ROLE = {d: r for r, d in ROLE_TO_DEP.items()}


def roles_with_decisions(toks: Sequence[str], pos: Sequence[str], heads: Dict[int, int],
                         validities: Optional[Dict[str, object]] = None,
                         head_posterior: Optional[Dict[int, Dict[int, float]]] = None,
                         conf: Optional[Dict[int, float]] = None,
                         reliability: Optional[Dict[str, object]] = None) -> Dict[int, Dict[str, object]]:
    """THE GRADED HAND-OFF FOR EVERY CONSUMER AT ONCE (pri 106, strategy ruling Q3, 2026-09-14).

    `coarse_roles` ends in an argmax and returns Dict[int, str]; measured on UD-EWT test, a role POSTERIOR is
    produced 3698/3698 times and 3698/3698 consumers read a string. That one line is where the whole graded signal
    dies, and repairing it per consumer means repairing it many times. This is the SAME decode with each nominal's
    entry being the full DECISION instead of the label:

        {i: {"dep", "role", "posterior", "margin", "reliability": {kind: P(right)}}}

    ADDITIVE AND EXACT: the label is whatever `coarse_roles` decided (the joint frame-slot decode included), so
        coarse_roles(...) == {i: d["dep"] for i, d in roles_with_decisions(...).items()}
    holds by construction and NO existing consumer changes. The posterior is the per-nominal competition's own
    (`coarse_role_posterior`), i.e. the graded read BEFORE any capacity-one slot masking -- a consumer that wants
    the joint belief should read the slot decode itself.

    COST: the posterior is computed twice (once inside `coarse_roles` for the argmax, once here). A consumer that
    needs only labels should keep calling `coarse_roles`; a consumer that needs the decision pays ~2x the role-rung
    cost, which is a small fraction of the parse.
    """
    tab = validities or load_coarse_validities()
    labels = coarse_roles(toks, pos, heads, tab, head_posterior, conf)
    if conf is None and head_posterior:
        conf = {i: float((head_posterior.get(i) or {}).get(heads.get(i, 0), 1.0)) for i in head_posterior}
    rel = reliability if reliability is not None else load_margin_reliability()
    out: Dict[int, Dict[str, object]] = {}
    for i, dep in labels.items():
        d = role_decision(toks, pos, heads, i, tab, conf, rel)
        d["dep"] = dep                                   # the DECODED label wins (it may come from the slot decode)
        d["role"] = DEP_TO_ROLE.get(dep, d["role"])
        out[i] = d
    return out


# ===============================================================================================================
# THE NON-ARGUMENT ARM OF THE LABELS RUNG (pri 134, 2026-09-16).
#
# THE DEFECT IT REPAIRS.  pri 129 retired the frozen supervised relation labeler from the live read and routed
# `crosstype_live_adapter` here.  `coarse_roles` labels ARGUMENT relations only, over the argument-head
# population, so on the reader's own parse every non-argument token read `dep`: no `appos`, no `flat`, no
# `compound`, no `nmod:poss` -- and no `cop`.  The crosstype definite->name bridge's four name-linking cues and
# its Centering POSSESSIVE role key on exactly those strings, so they could not fire.
#
# HOW THE BRAIN DOES THIS, PER RELATION -- none of them needs a classifier:
#   * A NAME RUN ("Mary Smith") is ONE referring expression stored and retrieved as a unit (Kripke 1980 rigid
#     designation; Semenza 2006/2009 proper-name anomia, left temporal pole, ABOVE and fed by the category
#     level).  The relation is the residue of that chunking -- pri 118's span-level NAME-RUN cue.
#   * An APPOSITION ("Elizabeth, the doctor") is a REDUCED PREDICATION: the same construction as "Elizabeth is
#     the doctor" without the copula (Pustet 2003 on copula optionality; Maienborn 2005 Kimian states; Bemis &
#     Pylkkanen 2011 LATL property attribution).  The organ that detects a predication is the PREDICATE SLOT
#     (pri 110/117, `attachment_arm.predicate_sites`, graded).  The comma is surface: only 24 of 105 UD-EWT
#     appositions carry one (counted at pri 129).
#   * A POSSESSIVE ("her brother", "Mary's dog") is CASE MARKING -- the Competition Model's strongest
#     morphological cue (Bates & MacWhinney 1989) -- and `genitive_value` above already reads it (cue set v4).
#   * A COPULA is the TENSE CARRIER of a non-verbal predication, the reason English inserts it (Pustet 2003;
#     Bybee 1994 auxiliation); `attachment_arm.cop_complement` says which token it carries tense FOR.
#   * The CONVENTION LAYER (det / case / cc / mark / amod / nummod / punct / aux) is not a computation the brain
#     performs at all; it is the distributional residue of the category rung, so it is learned as counts.
# Each is a CONSTRUCTION -- a form/GOVERNOR pairing recognised by cues whose VALIDITY is accrued from usage
# (Goldberg 1995; MacWhinney's Competition Model for the decision rule).  So this is an ARM of this organ, not a
# new organ: the SAME strength math (`strengths_from_counts`), the same additive activation, a counts asset, an
# online `observe` path.
#
# THE DIVISION OF LABOUR THAT KEEPS THE ARMS DISJOINT.  `coarse_roles` decides ARGUMENT-vs-NOT; where it says
# OTHER (`dep`) or NMOD (`nmod`) -- "a nominal licensed by a nominal is a PROPERTY of a thing", its own pri-108
# words -- this arm refines.  The ONE exception is deliberate and measured (RUN_MEMBERS below): a NON-HEAD member
# of a nominal run was never a separate slot-filler, so the CHUNKING level overrules the per-token argument read
# there.  Set HDLAB_FINE_RUN_MEMBERS=0 to take even that away and leave every argument decision untouched.
#
# ARC-INDEPENDENT CUES (pri 108's lesson, applied here): "a cue whose whole purpose is to survive a WRONG arc
# must not be looked up INSIDE the arc's configuration".  The name-run chunk, the genitive marker and the
# predicate slot are read off the surface with no arc, so their strength is the GLOBAL contrast.
#
# INERT WITHOUT ITS ASSET: `load_fine_validities()` returns None when the counts file is absent and
# `fine_relations` returns {} -- the caller then sees exactly the pre-pri-134 behaviour.
# ===============================================================================================================
FINE_CLASSES = ["flat", "compound", "appos", "nmod:poss", "nmod", "cop", "det", "case", "amod",
                "nummod", "advmod", "cc", "mark", "punct", "aux", "acl", "advcl", "xcomp", "ccomp",
                "conj", "dep"]
FINE_IDX = {c: k for k, c in enumerate(FINE_CLASSES)}
FINE_CUES = ("dcat", "gen", "run", "gap", "pslot", "hps", "crs", "runsym", "dist", "typepred", "zcop")
GLOBAL_FINE_CUES = frozenset({"run", "runsym", "gen", "pslot", "typepred", "zcop"})   # read arc-INDEPENDENTLY ("GLOBAL|value")
# THE RUN IS ONE UNIT, SO A RUN MEMBER IS NOT A SEPARATE ARGUMENT.  A name phrase / noun compound is ONE referring
# expression filling ONE slot (Kripke 1980; Semenza 2006 -- the basis of the name-run account).  The ARGUMENT arm
# decides per TOKEN, so it hands a core role to each NOUN of a run independently; measured on UD-EWT test that claims
# 211 of 1,108 gold `compound` tokens as nsubj / obj / obl, and they never reach this arm.  With RUN_MEMBERS on, the
# non-head members of a nominal run are in this population whatever the argument arm said -- the CHUNKING level, not
# this arm, is what overrules it.  Measured cost to the CORE-ARGUMENT population: see the pri-134 SOLVED.
RUN_MEMBERS = os.environ.get("HDLAB_FINE_RUN_MEMBERS", "0") == "1"   # 2026-09-16 landing (strategy): OFF. The lever wins the
#   rung (+0.0126 CI-sep on UD non-argument tokens) but the FULL-corpus consumer run (257 GUM docs, pri 134 phase 7) shows it
#   costs the bridge (recall/prec 0.2443/0.6515 OFF vs 0.2159/0.6230 ON) and the C3 consumer (0.1880 vs 0.1797); the
#   consumer is the product. Risk stated: compound recall 0.5352 -> 0.4486 and the UD gain forfeited.
_SUPERSENSE: Dict[str, str] = {}
_SUPERSENSE_ASSET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 "data", "frontend_assets", "noun_supersense_mfs_v1.json")
ARG_DEPS = frozenset({"nsubj", "obj", "nsubj:pass", "obl:agent", "obl", "iobj"})
_NOMH = ("NOUN", "PROPN")
_COP_SURFACE = frozenset({"be", "is", "are", "was", "were", "been", "being", "am"})
_FINE_VALIDITIES_PATHS = tuple([q for q in (os.environ.get("HDLAB_FINE_VALIDITIES"),) if q] +
                               [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                             "data", d, "fine_relation_validities_ud_ewt.json")
                                for d in ("frontend_assets", "hook_state")])
_FINE_VALIDITIES_CACHE = None
_FINE_CACHE_SET = False


def fine_of(dep: str) -> str:
    """A UD deprel folded into the arm's class space.  Used by the OFFLINE learner (the teaching signal) and by
    any scorer; never read at inference."""
    full = dep or ""
    d = full.split(":")[0]
    if full == "nmod:poss":
        return "nmod:poss"
    if full in CONVENTION_SUBTYPES:      # nmod:desc -- the UD-2.16 convention split of a descriptive nominal
        return "compound"
    if d == "nmod":
        return "nmod"
    if d in FINE_IDX:
        return d
    return "dep"


def nominal_runs(pos: Sequence[str], toks: Sequence[str]):
    """Maximal runs of adjacent nominal heads -- a NAME PHRASE or a NOUN COMPOUND read as ONE stored unit; a
    name-internal function word ("Game OF Thrones") does not break the unit.  (start1, end1, kind)."""
    from hdlab.coref import NAME_INTERNAL_FUNCTION
    n = len(pos); runs = []; i = 0
    while i < n:
        if pos[i] not in _NOMH:
            i += 1
            continue
        j = i
        while j + 1 < n:
            if pos[j + 1] in _NOMH:
                j += 1
                continue
            if (pos[i] == "PROPN" and j + 2 < n and pos[j + 2] == "PROPN"
                    and str(toks[j + 1]).lower() in NAME_INTERNAL_FUNCTION):
                j += 2
                continue
            break
        kinds = {pos[k] for k in range(i, j + 1) if pos[k] in _NOMH}
        runs.append((i + 1, j + 1, "propn" if kinds == {"PROPN"} else ("noun" if kinds == {"NOUN"} else "mixed")))
        i = j + 1
    return runs


def _run_index(pos: Sequence[str], toks: Sequence[str]) -> Dict[int, tuple]:
    out = {}
    for (a, b, k) in nominal_runs(pos, toks):
        if b > a:
            for t in range(a, b + 1):
                out[t] = (a, b, k)
    return out


def _fine_gap(toks: Sequence[str], pos: Sequence[str], i: int, h: int) -> str:
    """The intervening material between dependent and governor: the surface signature a construction is read
    off (a comma for the LOOSE appositive, a copular BE for the predication, a determiner for a fresh nominal,
    an adposition for a case-marked oblique)."""
    a, b = (i, h) if i < h else (h, i)
    if b - a <= 1:
        return "adj"
    mid = list(range(a + 1, b))
    if len(mid) > 6:
        return "far"
    lows = [str(toks[k - 1]).lower() for k in mid]
    cats = [pos[k - 1] for k in mid]
    if any(w in _COP_SURFACE for w in lows) and all(c in ("AUX", "VERB", "ADV", "DET", "ADJ", "NUM", "PART") for c in cats):
        return "be"
    if lows[0] == ",":
        return "comma"
    if any(w == "," for w in lows):
        return "comma2"
    if all(c in ("DET", "ADJ", "NUM", "ADV") for c in cats):
        return "det"
    if cats[0] == "ADP" or cats[-1] == "ADP":
        return "adp"
    if all(c == "PUNCT" for c in cats):
        return "punct"
    return "mix"


def _supersense(lemma: str) -> str:
    """The ANTERIOR-TEMPORAL TYPE READ: the most-frequent-sense noun supersense of a lemma, from the frozen offline
    asset (no nltk at inference).  This is the hub-level knowledge an apposition USES -- "Elizabeth, the doctor"
    attributes a noun.person TYPE to a referent (Rogers & McClelland 2004; Patterson, Nestor & Rogers 2007)."""
    if not _SUPERSENSE:
        try:
            with open(_SUPERSENSE_ASSET, encoding="utf-8") as f:
                _SUPERSENSE.update(json.load(f)["table"])
        except Exception:
            _SUPERSENSE["__none__"] = ""
    return _SUPERSENSE.get(str(lemma).lower().strip(".,'\"!?;:-()[]"), "")


def _left_domains(pos, toks, runlist=None) -> Dict[int, object]:
    """{1-based i: the nearest nominal domain (start1, end1, kind) strictly to the LEFT of i, or None} in ONE
    pass -- the appositive's antecedent domain, computed once per sentence."""
    runs = runlist if runlist is not None else nominal_runs(pos, toks)
    out = {}
    cur = None
    k = 0
    for i in range(1, len(pos) + 1):
        while k < len(runs) and runs[k][1] < i:
            cur = runs[k]
            k += 1
        out[i] = cur
    return out


def _typepred_value(toks, pos, i, ldom) -> str:
    """AN APPOSITION IS A TYPE ATTRIBUTION, NOT A COMMA.  An appositive PREDICATES a type of the referent to its
    left, so the cue is the pair of hub TYPES, not the punctuation between them."""
    if pos[i - 1] not in _NOMH:
        return "na"
    left = (ldom or {}).get(i)
    if left is None:
        return "noleft"
    ss = _supersense(toks[i - 1]) or ("PROPN" if pos[i - 1] == "PROPN" else "unk")
    lss = _supersense(toks[left[1] - 1]) or ("PROPN" if pos[left[1] - 1] == "PROPN" else "unk")
    return "%s|%s|%s" % (lss.replace("noun.", ""), ss.replace("noun.", ""),
                         "same" if (ss and ss == lss) else "diff")


def _zcop_strength(toks, pos, i, ldom, mat, tag_names):
    """QUALITY PUSH 3 -- THE ZERO-COPULA PREDICATE SLOT.  `predicate_sites` opens a slot only at an overt copula,
    so it is blind to the reduced predication that an apposition IS (measured: on "Elizabeth , the doctor ,
    arrived" it returns the VERB and nothing for the appositive).  Here the predication organ's OWN functions are
    asked the counterfactual the construction poses: insert a VIRTUAL copula in the gap to the left of this
    nominal and read the slot it would open -- (1 - host_belief) * copular_available at that carrier (Pustet 2003:
    zero-copula predication is the cross-linguistic norm; the appositive is the copula-less form)."""
    if mat is None or pos[i - 1] not in _NOMH:
        return None
    left = (ldom or {}).get(i)
    if left is None:
        return None
    try:
        from hdlab.attachment_arm import host_belief, copular_available
    except Exception:
        return None
    g = left[1]                                       # insert the virtual carrier right after the left domain
    t2 = list(toks[:g]) + ["is"] + list(toks[g:])
    p2 = list(pos[:g]) + ["AUX"] + list(pos[g:])
    try:
        ai = list(tag_names).index("AUX")
    except ValueError:
        return None
    row = np.zeros((1, mat.shape[1]), dtype=float)
    row[0, ai] = 1.0
    m2 = np.concatenate([mat[:g], row, mat[g:]], axis=0)
    try:
        ca = float(copular_available(t2, p2, g))
        if ca <= 0.0:
            return 0.0
        return float((1.0 - host_belief(t2, p2, m2, list(tag_names), g)) * ca)
    except Exception:
        return None


def _ps_bin(v) -> str:
    if v is None:
        return "na"
    v = float(v)
    return "ps0" if v <= 0.0 else ("pslo" if v < 0.34 else ("psmid" if v < 0.67 else "pshi"))


def fine_relation_cues(toks: Sequence[str], pos: Sequence[str], heads: Dict[int, int], i: int,
                       sites=None, coarse=None, runs=None, ldom=None, mat=None,
                       tag_names=None) -> Dict[str, str]:
    """The cue VALUES fired for token i (1-based).  Every value comes from an organ the reader already runs:
    the category rung (dcat + the configuration), the genitive case marker (`genitive_value`), the name-run
    chunker (pri 118's `coref.span_caps_symbol`), the predicate slot (pri 110/117), and the ARGUMENT arm's own
    read (`crs` -- the graded hand-off between the two arms of this organ)."""
    from hdlab.coref import span_caps_symbol
    h = int(heads.get(i, 0) or 0)
    hcat = pos[h - 1] if 1 <= h <= len(pos) else "ROOT"
    cues = {"config": "%s_%s" % (hcat, "pre" if (h == 0 or i < h) else "post"),
            "dcat": pos[i - 1] if i - 1 < len(pos) else "X",
            "gen": genitive_value(toks, pos, i) or "no"}
    runs = runs if runs is not None else _run_index(pos, toks)
    r = runs.get(i)
    if r is None:
        cues["run"] = "solo" if cues["dcat"] in _NOMH else "na"
        cues["runsym"] = "na"
    else:
        a, b, kind = r
        cues["run"] = "%s_%s" % (kind, "first" if i == a else ("last" if i == b else "mid"))
        cues["runsym"] = span_caps_symbol([str(t) for t in toks[a - 1:b]], i - a,
                                          first_is_sentence_initial=(a == 1))
    cues["gap"] = _fine_gap(toks, pos, i, h) if h else "root"
    sites = sites or {}
    cues["pslot"] = _ps_bin(sites.get(i - 1)) if sites else "na"
    cues["hps"] = _ps_bin(sites.get(h - 1)) if (sites and h) else "na"
    cues["crs"] = (coarse or {}).get(i, "none")
    _ld = ldom if ldom is not None else _left_domains(pos, toks)
    cues["typepred"] = _typepred_value(toks, pos, i, _ld)
    cues["zcop"] = _ps_bin(_zcop_strength(toks, pos, i, _ld, mat, tag_names))
    d = abs(i - h) if h else 0
    cues["dist"] = "d0" if d == 0 else ("d1" if d == 1 else ("d2" if d == 2 else ("d3_5" if d <= 5 else "d6")))
    return cues


def fine_relation_supports(cues, tab, cue_set=None) -> Dict[str, np.ndarray]:
    S = {"prior": tab["prior"]}
    cfg = cues["config"]
    vec = tab["strength"].get("config", {}).get(cfg)
    if vec is not None:
        S["config"] = vec
    for c in (cue_set if cue_set is not None else (tab.get("cue_set") or FINE_CUES)):
        v = cues.get(c)
        if v is None:
            continue
        key = ("GLOBAL|" + str(v)) if c in GLOBAL_FINE_CUES else ("%s|%s" % (cfg, v))
        vec = tab["strength"].get(c, {}).get(key)
        if vec is not None:
            S[c] = vec
    return S


def fine_relation_posterior(cues, tab, cue_set=None) -> np.ndarray:
    """The graded non-argument relation posterior (softmax of the additive cue competition) over FINE_CLASSES."""
    S = fine_relation_supports(cues, tab, cue_set)
    return softmax(net_activation(S, {c: 1.0 for c in S}), gain=1.0)


def _run_nonhead(runs, i) -> bool:
    """Is i a NON-HEAD member of a nominal run?  A propn run is headed by its FIRST token (UD `flat`), a noun
    compound by its LAST (UD `compound`); a mixed run takes the English head-final default."""
    r = runs.get(i)
    if r is None:
        return False
    a, b, kind = r
    return i != (a if kind == "propn" else b)


def fine_population(toks, pos, heads, coarse, runs=None, run_members=None) -> list:
    """The arm's population: every non-root token the ARGUMENT arm did not claim (it emitted nothing, `dep`, or
    `nmod`), PLUS -- with RUN_MEMBERS on -- every non-head member of a nominal run, because a run is ONE referring
    expression filling ONE slot.  Computable at read time -- no gold, no arc label."""
    rm = RUN_MEMBERS if run_members is None else run_members
    if rm and runs is None:
        runs = _run_index(pos, toks)
    out = []
    for i in range(1, len(toks) + 1):
        if not int(heads.get(i, 0) or 0):
            continue
        c = coarse.get(i)
        if c is None or c in ("dep", "nmod") or (rm and _run_nonhead(runs, i)):
            out.append(i)
    return out


def _construction_head(toks, pos, heads, i, rel, runs, copmap):
    """The governor THE CONSTRUCTION ITSELF names -- a construction is a form/governor pairing, so the arm hands
    both down, and the name-link survives an attachment error on the run member.  None = keep the arm's head."""
    n = len(toks)
    r = runs.get(i)
    if rel == "flat" and r:
        return r[0] if r[0] != i else None            # a NAME phrase is headed by its FIRST token
    if rel == "compound" and r:
        return r[1] if r[1] != i else None            # a NOUN compound by its LAST
    if rel == "cop":
        q = copmap.get(i)
        return q if (q and q != i) else None
    if rel == "appos":
        for (_a, b, _k) in reversed(nominal_runs(pos, toks)):
            if b < i:
                return b                              # the nearest nominal domain to the left
        return None
    if rel in ("nmod:poss", "det", "amod", "nummod", "case"):
        for j in range(i + 1, n + 1):
            if pos[j - 1] in _NOMH:
                k = j
                while k + 1 <= n and pos[k] in _NOMH:
                    k += 1
                return k
            if pos[j - 1] not in ("DET", "ADJ", "NUM", "ADV", "PART", "PUNCT"):
                break
        return None
    return None


def fine_relations(toks: Sequence[str], pos: Sequence[str], heads: Dict[int, int],
                   validities: Optional[Dict[str, object]] = None, sites=None, coarse=None,
                   cue_set=None, with_heads: bool = False, tau: float = 0.0, run_members=None,
                   mat=None, tag_names=None):
    """{1-based i: dep} (or {i: (dep, head)} with with_heads) over the non-argument population.
    Returns {} when no validity asset is present -- the caller then sees the pre-pri-134 behaviour exactly."""
    tab = validities if validities is not None else load_fine_validities()
    if tab is None:
        return {}
    coarse = coarse or {}
    _rl = nominal_runs(pos, toks)
    runs = {t: (a, b, k) for (a, b, k) in _rl if b > a for t in range(a, b + 1)}
    ldom = _left_domains(pos, toks, _rl)
    copmap = {}
    if with_heads:
        try:
            from hdlab.attachment_arm import cop_complement
            for k in range(len(toks)):
                if pos[k] == "AUX":
                    q = cop_complement(list(toks), list(pos), k)
                    if q is not None:
                        copmap[k + 1] = q + 1
        except Exception:
            copmap = {}
    out = {}
    for i in fine_population(toks, pos, heads, coarse, runs, run_members):
        cues = fine_relation_cues(toks, pos, heads, i, sites=sites, coarse=coarse, runs=runs,
                                  ldom=ldom, mat=mat, tag_names=tag_names)
        p = fine_relation_posterior(cues, tab, cue_set)
        k = int(np.argmax(p))
        if tau and float(p[k]) < tau:
            continue
        rel = FINE_CLASSES[k]
        if with_heads:
            hh = _construction_head(toks, pos, heads, i, rel, runs, copmap)
            out[i] = (rel, hh if hh else int(heads.get(i, 0) or 0))
        else:
            out[i] = rel
    return out


def all_relations(toks: Sequence[str], pos: Sequence[str], heads: Dict[int, int],
                  validities: Optional[Dict[str, object]] = None, sites=None, coarse=None,
                  cue_set=None, with_heads: bool = False, run_members=None, mat=None, tag_names=None):
    """THE LABELS RUNG'S FULL READ: the ARGUMENT arm's decisions, refined by the NON-ARGUMENT arm wherever the
    argument competition said OTHER / NMOD.  A core argument label never moves, so every argument consumer is
    byte-identical.  With no fine-validity asset this is exactly `coarse_roles`."""
    coarse = dict(coarse if coarse is not None else coarse_roles(toks, pos, heads))
    fine = fine_relations(toks, pos, heads, validities, sites=sites, coarse=coarse,
                          cue_set=cue_set, with_heads=with_heads, run_members=run_members,
                          mat=mat, tag_names=tag_names)
    if with_heads:
        out = {i: (d, int(heads.get(i, 0) or 0)) for i, d in coarse.items() if d in ARG_DEPS}
        out.update(fine)
        return out
    out = {i: d for i, d in coarse.items() if d in ARG_DEPS}
    out.update(fine)
    return out


def empty_fine_counts() -> Dict[str, object]:
    K = len(FINE_CLASSES)
    return {"prior": [0.0] * K, "config": {}, "cues": {c: {} for c in FINE_CUES}}


def accrue_fine(counts, cues, rel, w: float = 1.0) -> None:
    """ONE understood relation into the counts -- the whole learning rule, OFFLINE and ONLINE alike."""
    k = FINE_IDX.get(rel)
    if k is None:
        return
    K = len(FINE_CLASSES)
    counts["prior"][k] += w
    cfg = cues["config"]
    counts["config"].setdefault(cfg, [0.0] * K)[k] += w
    counts["config"].setdefault("GLOBAL", [0.0] * K)[k] += w      # the base the GLOBAL contrasts read against
    for c in FINE_CUES:
        v = cues.get(c)
        if v is None:
            continue
        key = ("GLOBAL|" + str(v)) if c in GLOBAL_FINE_CUES else ("%s|%s" % (cfg, v))
        counts["cues"].setdefault(c, {}).setdefault(key, [0.0] * K)[k] += w


def fine_table_from_counts(counts, cue_set=None) -> Dict[str, object]:
    built = strengths_from_counts(counts, 0.0)                    # THE ONE implementation of the math
    return {"prior": built["prior"], "strength": built["strength"], "counts": counts,
            "cue_set": tuple(cue_set) if cue_set else None}


def observe_fine_relation_outcome(toks, pos, heads, i, rel, table=None, sites=None, coarse=None, w=1.0):
    """PLASTICITY -- the brain is never frozen.  Accrue one understood relation into the SAME counts the
    strengths are a pure function of, and rebuild them.  Persist with `save_fine_validities`."""
    tab = table if table is not None else load_fine_validities()
    if tab is None:
        return None
    cues = fine_relation_cues(toks, pos, heads, i, sites=sites, coarse=coarse)
    accrue_fine(tab["counts"], cues, rel, w)
    built = strengths_from_counts(tab["counts"], 0.0)
    tab["prior"] = built["prior"]
    tab["strength"] = built["strength"]
    return tab


def save_fine_validities(path: Optional[str] = None, table: Optional[Dict[str, object]] = None) -> str:
    tab = table if table is not None else load_fine_validities()
    p = path or _FINE_VALIDITIES_PATHS[0]
    doc = {"source": "Competition-Model cue validities for the NON-ARGUMENT arm of the labels rung: counts "
                     "accrued from the teaching corpus through the LIVE chain; strengths = "
                     "strengths_from_counts(counts). Plastic: observe_fine_relation_outcome accrues one "
                     "understood relation into the same counts.",
           "classes": FINE_CLASSES, "cues": list(FINE_CUES), "counts": tab["counts"],
           "cue_set": list(tab.get("cue_set") or FINE_CUES)}
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="ascii", newline="\n") as f:
        json.dump(doc, f, indent=1)
    return p


def load_fine_validities(path: Optional[str] = None) -> Optional[Dict[str, object]]:
    """The learned non-argument validity table, or None when no asset is on disk (the arm then abstains and
    every caller is byte-identical to the pre-pri-134 organ)."""
    global _FINE_VALIDITIES_CACHE, _FINE_CACHE_SET
    if path is None and _FINE_CACHE_SET:
        return _FINE_VALIDITIES_CACHE
    paths = (path,) if path else _FINE_VALIDITIES_PATHS
    tab = None
    for p in paths:
        try:
            with open(p, encoding="ascii") as f:
                doc = json.load(f)
        except Exception:
            continue
        tab = fine_table_from_counts(doc["counts"], doc.get("cue_set"))
        tab["classes"] = doc.get("classes", FINE_CLASSES)
        break
    if path is None:
        _FINE_VALIDITIES_CACHE = tab
        _FINE_CACHE_SET = True
    return tab

def by_governs(low, pos, p, maxscan=8):
    """Is the nominal at 0-based p the object of the passive-agent preposition 'by'? Scan left through
    NP-internal modifiers + coordination; a 'by' before any clause-blocking token -> by-PP member (the demoted
    passive agent). VERBATIM from exp_noncanonical_agent_bymorph_v1.by_governs. `low` = lowercased tokens."""
    j = p - 1
    for _ in range(maxscan):
        if j < 0:
            return False
        if low[j] == "by":
            return True
        u = pos[j] if j < len(pos) else None
        if u in _BYHEAD_NP_SKIP or low[j] in _BYHEAD_NP_SKIP_LOW:
            j -= 1
            continue
        return False
    return False


def participle_bypp_gate(toks, pos, v0):
    """The by-agent CONSTRUCTION detector: the predicate at 0-based v0 is a PARTICIPLE (V-en) and the clause
    carries a by-governed NP -- the V-en + by-NP morphological signature of the demoted passive agent. The
    UPSTREAM voice gate for the byhead CASE cue; HIGHER-PRECISION than is_passive_clause (14 vs 106 canonical
    false-fires on QA-SRL) while covering >= as many real by-passives -> use IT, not is_passive_clause. VERBATIM
    from exp_cmrole_agent_board_byhead_v1._participle_bypp_gate."""
    if not (0 <= v0 < len(toks)):
        return False
    # pri 111, REPAIRED 2026-09-14 16:10 after the byhead landing witness caught it. THE GATE IS A
    # CONSTRUCTION DETECTOR, NOT A FINITE-CLAUSE VOICE READ, and the two are not the same question. The first
    # fold asked `is_passive_predicate` alone, which REQUIRES an auxiliary -- so it dropped every REDUCED
    # participial passive (`those used BY non-human animals`, `a display performed BY the male`, `mass divided
    # BY volume`), which is exactly where a demoted agent lives. Measured on QA-SRL: gate recall on the clean
    # agent-post slice fell 62/90 -> 53/90 and the byhead pick 0.6667 -> 0.6000.
    # THE BRAIN'S FORM, and it is this organ's own story read in the other direction: the auxiliary OPENS the
    # passive expectation and the by-phrase CONFIRMS it -- so when there is no auxiliary to open it, the
    # confirmation carries the construction by itself. Fire on a by-governed NP plus EITHER the organ's voice
    # read (an auxiliary opened the expectation, which also catches the irregular participles the suffix test
    # missed -- `was blown up by a bomb`) OR participial morphology (the reduced passive). A strict SUPERSET of
    # the pre-fold gate, so it cannot lose a firing it used to have.
    low = [t.lower() for t in toks]
    if not any(by_governs(low, pos, i) for i in range(len(toks))
               if (pos[i] if i < len(pos) else None) in _BYHEAD_NOM):
        return False
    if is_passive_predicate(toks, pos, v0 + 1):
        return True
    return _is_participle(toks[v0], pos[v0] if v0 < len(pos) else None)


def _agent_pp_governed(low, up, p):
    """Is the noun at p the object of a preposition? Scan left over NP-internal modifiers (DET/ADJ/NUM/PUNCT +
    possessive); if a preposition governs before any clause-blocking token, it is a PP object -> NOT a subject."""
    j = p - 1
    for _ in range(5):
        if j < 0:
            return False
        t = low[j]
        u = up[j] if j < len(up) else None
        if t in _AGENT_PREPS:
            return True
        if u in _AGENT_NP_SKIP or t in ("'s", "'", "the", "a", "an"):
            j -= 1
            continue
        return False
    return False


def _agent_is_animate(head: str, tag, gaz) -> float:
    """+1 animate, -1 inanimate, 0 unknown. lookup_animacy covers common nouns; it returns None for most PROPN,
    so recover the animacy of a NAMED discourse referent (a gazetteer given-name, or a PROPN head, is animate in
    narrative prose -- a coverage fix for the SAME cue, not a new cue). Pronouns: nominative/accusative animate,
    'it' inanimate. (Place-name PROPN are typically preposition-governed, so the core_arg cue excludes them.)"""
    if head in _AGENT_ANIM_PRON:
        return 1.0
    if head == "it":
        return -1.0
    a = lookup_animacy(head, tag)
    if a is not None:
        if a["animacy"] == "animate":
            return 1.0
        if a["animacy"] == "inanimate":
            return -1.0
    if gaz and head in gaz:
        return 1.0
    if tag == "PROPN":
        return 1.0
    return 0.0


def clause_bounds(toks, up, v0):
    """The [left, right) CLAUSE span of the verb at v0 (0-based). Left = just after the nearest preceding clause
    boundary (subordinator / strong punct / clause-coordinator that separates two verbs); right = the nearest
    following such boundary. The incremental clause segmentation the subject search is bounded by -- glass-box,
    reads only toks/pos. (SOLVED section 6: crude but net-positive; the full lever is an incremental parser.)"""
    low = [t.lower() for t in toks]
    left = 0
    for i in range(v0):
        t = low[i]
        if t in _AGENT_SUBORD or t in _AGENT_STRONGPUNCT:
            left = i + 1
        elif t in _AGENT_COORD and any(j < len(up) and up[j] == "VERB" for j in range(left, i)):
            left = i + 1                       # a coordinator AFTER a verb in this span = a new coordinate clause
    right = len(toks)
    for i in range(v0 + 1, len(toks)):
        t = low[i]
        if t in _AGENT_SUBORD or t in _AGENT_STRONGPUNCT:
            right = i
            break
        if t in _AGENT_COORD and any(j < len(up) and up[j] == "VERB" for j in range(v0 + 1, i)):
            right = i
            break
    return left, right


def _nominals_keep_pron(mentions, n_sents):
    """Like situation_reader._sentence_nominals but KEEPS pronoun mentions (a subject pronoun is the maximally-
    given Centering mention -> a valid, strong AGENT candidate). Per-sentence, sorted by token position."""
    per = [[] for _ in range(n_sents)]
    for m in mentions:
        si = m["sent_idx"]
        if 0 <= si < n_sents:
            per[si].append(m)
    for lst in per:
        lst.sort(key=lambda mm: (mm["wtok_start"], mm.get("midx", 0)))
    return per


def agent_supports(toks, pos, v0, cands, gaz=None, cluster_freq=None, subj_before=None,
                   byhead_agent_cue=False) -> Dict[str, list]:
    """Per-candidate AGENT support arrays for the Competition-Model cues. `cands` = [(wtok_start, head,
    cluster[, wtok_end]), ...]; v0 = predicate index (0-based). cluster_freq = passage-level {cluster:
    mention_count} for the Centering givenness cue. Reads ONLY toks/pos + the animacy lexicon + gazetteer +
    discourse counts -- glass-box, no gold. Cues: preverbal (word-order), core_arg (PP-government scan),
    animacy, salience (Centering givenness), adjacency (clause-locality), byagent (passive voice).

    STRUCTURE cue (opt-in, SELF-GATING): when `subj_before` is supplied (the register-general incremental
    left-corner subject-before array from hdlab.incremental_parser.incremental_subject_before), add a
    `structure` support of +1 for the candidate the incremental parse binds as this verb's subject -- the
    parser's SUBJECT ATTACHMENT entering the role competition as ONE precision-weighted vote (Matchin-Hickok
    separate pools; eADM minimal precision). It votes only when the bound subject maps onto a candidate; where
    it does not (or `subj_before is None`), no `structure` key is emitted -> byte-identical (net_activation
    skips a weighted cue with no support array). Landed 2026-09-04, VERBATIM from
    experiments/exp_cmrole_agent_struct_v1.py:cm_agent_pick_struct."""
    low = [t.lower() for t in toks]
    passive = is_passive_predicate(toks, pos, v0 + 1)   # pri 111: the voice of THIS predicate, not of the sentence
    cf = cluster_freq or {}
    S = {"preverbal": [], "core_arg": [], "animacy": [], "salience": [], "adjacency": [], "byagent": []}
    # STRUCTURE cue: the incremental left-corner subject token bound for a verb AT v0 (self-gating; abstains
    # -> no `structure` support key -> byte-identical for callers that pass no subj_before).
    use_struct = subj_before is not None
    subj_tok = subj_before[v0] if (use_struct and 0 <= v0 < len(subj_before)) else None
    if use_struct:
        S["structure"] = []
    for cand in cands:
        p, head, cl = cand[0], cand[1], cand[2]
        pre = p < v0
        prevtok = low[p - 1] if p - 1 >= 0 else ""
        by = 1.0 if prevtok == "by" else 0.0
        core = 0.0 if _agent_pp_governed(low, pos, p) else 1.0   # a preposition-governed noun is NOT the subject
        tag = pos[p] if p < len(pos) else None
        if passive:                                             # VOICE flip: surface subject demoted; by-phrase = agent
            S["preverbal"].append(0.0)
            S["byagent"].append(by)
            S["adjacency"].append(1.0 / (1.0 + abs(p - v0)) if by else 0.0)
        else:                                                   # ACTIVE: agent is preverbal (word-order dominant)
            S["preverbal"].append(1.0 if pre else 0.0)
            S["byagent"].append(0.0)
            # clause-locality: the subject is the NEAREST preceding core NP (Lewis-Vasishth most-active retrieval)
            S["adjacency"].append(1.0 / (1.0 + (v0 - p)) if pre else 0.0)
        S["core_arg"].append(core)
        S["animacy"].append(_agent_is_animate(head, tag, gaz))
        # CENTERING givenness (Grosz-Joshi-Weinstein): a TRACKED discourse entity (established coref chain,
        # freq>=2) is the salient center -> realized as SUBJECT. A one-off (fresh singleton) is not.
        S["salience"].append(1.0 if cf.get(cl, 0) >= 2 else 0.0)
        if use_struct:                                          # +1 for the candidate the incremental parse binds
            e = cand[3] if len(cand) > 3 else p                 # candidate span end (head may sit inside the NP span)
            hit = subj_tok is not None and (p == subj_tok or p <= subj_tok <= e)
            S["structure"].append(1.0 if hit else 0.0)
    # BY-PHRASE CASE-MORPHOLOGY cue (byhead, opt-in + SELF-GATING): +1 for a candidate GOVERNED by the passive-
    # agent preposition "by" through its NP (scan over DET/ADJ to the governing "by"; the case-morphology agent
    # signal the landed `byagent` cue -- prevtok=='by' -- misses on multi-word by-phrases). Emitted ONLY when the
    # caller passes byhead_agent_cue AND the participle+by-PP construction gate fires -> no `byhead` support key
    # otherwise -> byte-identical (net_activation skips a weighted cue with no support array). Weight
    # AGENT_VALIDITIES["byhead"]=BYHEAD_W. Landed 2026-09-06 (see BYHEAD_W); VERBATIM from
    # experiments/exp_noncanonical_agent_bymorph_v1.py:pick byhead injection.
    if byhead_agent_cue and participle_bypp_gate(toks, pos, v0):
        S["byhead"] = [1.0 if by_governs(low, pos, cand[0]) else 0.0 for cand in cands]
    return S


def agent_competition_pick(toks, pos, v, cands, cluster_freq=None,
                           weights: Optional[Dict[str, float]] = None, gaz=None, twin_seed=None,
                           subj_before=None, byhead_agent_cue=False) -> str:
    """The AGENT = argmax additive cue activation over the tracked/given candidate mentions (REUSES
    graded_competition.net_activation). `cands` = list of mention dicts (each with 'wtok_start', 'head',
    optional 'cluster'/'wtok_end'); v = predicate index (0-based) in toks-space; weights default to
    AGENT_VALIDITIES. Returns a head string, or '?' when there is no candidate. twin_seed set => INFO-FREE
    TWIN: shuffle each cue's per-candidate support across candidates (the structure->candidate mapping
    destroyed). subj_before (optional): the incremental left-corner subject-before array -> the self-gating
    STRUCTURE cue votes (see agent_supports); None (default) => byte-identical (no structure support).
    byhead_agent_cue (default False): when True, the self-gating BY-PHRASE CASE cue votes on the participle+
    by-PP passive-agent construction (see agent_supports/BYHEAD_W); False => byte-identical (no byhead
    support). The live reader passes True (default-on via SituationReader.cm_agent_byhead)."""
    w = AGENT_VALIDITIES if weights is None else weights
    c = [(m["wtok_start"], m["head"], m.get("cluster"), m.get("wtok_end", m.get("wtok_start"))) for m in cands]
    if not c:
        return "?"
    S = agent_supports(toks, pos, v, c, gaz, cluster_freq, subj_before=subj_before,
                       byhead_agent_cue=byhead_agent_cue)
    if twin_seed is not None:
        rng = np.random.default_rng(twin_seed + v + len(c))
        S = {k: list(np.asarray(vv)[rng.permutation(len(vv))]) for k, vv in S.items()}
    A = net_activation(S, w)
    return c[int(np.argmax(A))][1]


def agent_competition_pick_conf(toks, pos, v, cands, cluster_freq=None,
                                weights: Optional[Dict[str, float]] = None, gaz=None, twin_seed=None,
                                subj_before=None, byhead_agent_cue=False):
    """Like `agent_competition_pick`, but ALSO returns the competition's own RELIABILITY -- so the AGENT pick
    carries a precision the reasoning phase can defer on (Lewis-Vasishth activation gap). Returns
    (pick_head, margin, conf):
      * pick_head : IDENTICAL to agent_competition_pick (same S, same A, same argmax int(np.argmax(A))).
      * margin    : tanh((A_top1 - A_top2)/3.0) in [0,1) -- the competition MARGIN, the AUC~0.76 right-vs-wrong
                    agent reliability (exp_defer_agent_v1); a STRONG raw signal (NO calibration needed -- the
                    Competition Model maintains the full candidate distribution, unlike a greedy parse arc).
      * conf      : 1 - normalized softmax entropy of A (a competing readout; margin is the deployed one).
    This only SURFACES the margin the competition already computed -- the pick is byte-identical, so it is a pure
    ADDITIVE readout. Returns ("?", None, None) when there is no candidate. twin_seed / subj_before /
    byhead_agent_cue behave exactly as in agent_competition_pick."""
    w = AGENT_VALIDITIES if weights is None else weights
    c = [(m["wtok_start"], m["head"], m.get("cluster"), m.get("wtok_end", m.get("wtok_start"))) for m in cands]
    if not c:
        return "?", None, None
    S = agent_supports(toks, pos, v, c, gaz, cluster_freq, subj_before=subj_before,
                       byhead_agent_cue=byhead_agent_cue)
    if twin_seed is not None:
        rng = np.random.default_rng(twin_seed + v + len(c))
        S = {k: list(np.asarray(vv)[rng.permutation(len(vv))]) for k, vv in S.items()}
    A = net_activation(S, w)
    pick = c[int(np.argmax(A))][1]                       # byte-identical to agent_competition_pick
    As = np.sort(np.asarray(A, dtype=float))[::-1]       # descending activation VALUES (tie-break-robust gap)
    if len(As) > 1:
        top2 = float(As[0] - As[1])
        p = softmax(A); ent = float(-(p * np.log(p + 1e-12)).sum() / np.log(len(A)))
    else:
        top2 = float(abs(As[0]) + 1.0); ent = 0.0
    return pick, float(np.tanh(top2 / 3.0)), float(1.0 - ent)


# ===========================================================================
# REGISTER-SAFE AGENT HYBRID -- the AGENT counterpart to hybrid_role_patient (the deployable route).
# ===========================================================================
# Landed 2026-09-06 from the owner-DONE rebuild_the_comprehension_board_on_a_modern_corpus_retire_the_
# 19c_litbank_eval. The always-compete agent_competition_pick is REGISTER-TUNED to 19c and UNDER-performs a
# positional floor on MODERN canonical prose (gold agent = nsubj ~= nearest-preverbal-nominal in fixed-word-
# order English, so word-order is near-ceiling there; UD-EWT full_cm 0.758 vs positional 0.855). The
# brain-foundational fix is the SAME hybrid design proven for the PATIENT (hybrid_role_patient): keep the
# high-validity WORD-ORDER default on canonical clauses BYTE-IDENTICAL, and invoke the Competition-Model
# competition (which already carries the landed byhead by-phrase CASE cue) ONLY on a MARKED override cue --
#   (1) a PASSIVE clause WITH an explicit by-phrase (voice: the surface subject is the patient, the agent is
#       the by-PP; an agentless passive has no agent to flip to, so the by-phrase gate is what buys back the
#       canonical no-regress), (2) the positional pick is PP-GOVERNED (core_arg: a preposition-governed noun
#       is not the subject), (3) the positional pick is a NON-NOMINATIVE pronoun (case: him/her/them cannot
#       be the subject). MEASURED (UD-EWT train+test): full modern set hybrid 0.853 ~= positional 0.8525
#       (no-regress) with NON-CANONICAL +0.077 CI-sep, the info-free twin LOSING (ports the arm reference impl
#       experiments/exp_board_agent_slot_ud_v1.hybrid_agent_pick / exp_board_agent_noncanonical_v1._hybrid_idx).
# DECORRELATED CONSTRUCTION cues (construction=True, opt-in): the mechanism drill proved the competition is
# preverbal-DOMINATED (correlated with position) so the only glass-box way to recover position's failures is a
# cue DECORRELATED from position; Construction Grammar (Goldberg 1995) gives two high-frequency ones tried
# BEFORE the word-order default -- EXISTENTIAL ('there is/was X' -> notional subject = first post-copular NOUN,
# not 'there') and guarded NP-COORDINATION ('NP1 and NP2 V' -> subject head = first conjunct NP1). MEASURED
# together with the hybrid: full who-did-what AGENT set 0.855->0.873 (+0.018 CI-sep), EXACT zero canonical
# regress, twin loses; they compose with byhead (existential/coordination are ACTIVE constructions, byhead
# fires on the passive by-PP -> disjoint). Ports experiments/exp_board_agent_construction_v1.
# DEFAULT-SAFE: importing this changes NO existing behaviour; hybrid_agent_pick is a NEW callable. The live
# reader wires it behind SituationReader.agent_hybrid (default OFF -- the reader's live who-did-what board is
# 19c LitBank, where the always-compete win is register-specific and the hybrid reverts toward position; the
# MODERN board arm computes the hybrid directly). Glass-box, reads only toks/POS + animacy + coref counts.
_CONSTR_NPMOD = frozenset(("DET", "ADJ", "NUM"))
_CONSTR_COORD = frozenset(("and", "or", "nor"))
_CONSTR_PP_SKIP = frozenset(("DET", "ADJ", "NUM"))   # NP-internal modifiers, WITHOUT PUNCT (a comma ends a phrase)


def mention_head_wpos(m) -> int:
    """THE WITHIN-SENTENCE INDEX OF A MENTION'S HEAD (pri 134 phase 7).

    The mention schema (`coref.parse_litbank_conll`, coref.py:167) puts `wtok_start` at the SPAN START and the
    HEAD LAST, so the head sits at `wtok_start + (gtok_end - gtok_start)`.  Two sites in this module read
    `wtok_start` itself as the head index -- a CATEGORY test on the head, and the 1-based index handed to
    `_calibrated_agent_prob` (which calls `is_arg_head` / `coarse_role_posterior` on it).  Both are therefore
    already reading the DETERMINER on any multi-token mention, i.e. on every gold coref-column mention; the
    reader's own stream hid it because `referent_per_np` emitted one-token spans.  A one-token mention is the
    degenerate case where head == start, so this is byte-identical wherever the old reading was right."""
    ws = int(m.get("wtok_start", 0) or 0)
    gs, ge = m.get("gtok_start", -1), m.get("gtok_end", -1)
    if isinstance(gs, int) and isinstance(ge, int) and 0 <= gs <= ge:
        return ws + (ge - gs)
    sp = m.get("span_toks")
    return ws + (len(sp) - 1 if sp else 0)


def _pp_governed_commastop(low, up, p):
    """Core-argument PP-government detector, comma-STOPPED (the deployable one -- mirrors
    experiments/exp_board_agent_noncanonical_v1._pp_governed_fixed): STOP the left-scan at any punctuation (a
    comma closes a fronted constituent), so 'In 2019 , Google launched' does NOT falsely flag the real subject.
    Does NOT skip compound noun modifiers (the aggressive variant over-fires -- a LOCATED NEGATIVE). p 0-based."""
    j = p - 1
    for _ in range(5):
        if j < 0:
            return False
        t = low[j]
        u = up[j] if j < len(up) else None
        if u == "PUNCT" or t in (",", ";", ":", "--"):
            return False
        if t in _AGENT_PREPS:
            return True
        if u in _CONSTR_PP_SKIP or t in ("'s", "'", "the", "a", "an"):
            j -= 1
            continue
        return False
    return False


def _positional_agent_base(cands, v0):
    """The nearest PRE-verbal candidate mention (word-order-only positional floor); else nearest post-verbal;
    else None. cands = mention dicts with 'wtok_start'. v0 = predicate index (0-based). Returns the mention
    dict (or None)."""
    pre = [c for c in cands if c["wtok_start"] < v0]
    if pre:
        return max(pre, key=lambda c: c["wtok_start"])
    post = [c for c in cands if c["wtok_start"] > v0]
    return min(post, key=lambda c: c["wtok_start"]) if post else None


def agent_override_fires(toks, pos, v0, cands):
    """Does a MARKED override cue fire for the verb at v0 (0-based)? True iff the clause is a PASSIVE WITH an
    explicit by-phrase (voice), OR the positional pick (nearest preverbal candidate) is PP-GOVERNED (core_arg),
    OR the positional pick is a NON-NOMINATIVE pronoun (case). This is the gate that decides whether the AGENT
    hybrid invokes the Competition-Model competition instead of the word-order default. Clause-bounded (voice +
    by-phrase are scoped to the verb's clause span; role assignment is clause-local). Reads only toks/POS."""
    low = [t.lower() for t in toks]
    lo, hi = clause_bounds(toks, pos, v0)
    passive_local = is_passive_predicate(toks, pos, v0 + 1)   # pri 111: predicate-anchored, not any passive in the span
    has_by = any(low[i] == "by" for i in range(lo, min(hi, len(low))))
    if passive_local and has_by:
        return True
    base = _positional_agent_base(cands, v0)
    if base is None:
        return False
    bi = base["wtok_start"]
    if _agent_pp_governed(low, pos, bi):
        return True
    bh = str(base["head"]).lower()
    if bh in _AGENT_ANIM_PRON and bh not in NOMINATIVE_PRON:
        return True
    return False


def _existential_agent(toks, pos, v0, cands):
    """EXISTENTIAL construction ('there is/was X'): expletive 'there' (PRON/ADV) pre-verbally in the clause ->
    the notional subject is the first NOUN/PROPN candidate AFTER the verb within the clause. Returns the head
    string or None. Ports experiments/exp_board_agent_construction_v1._existential_subject (v0 0-based)."""
    low = [t.lower() for t in toks]
    lo, hi = clause_bounds(toks, pos, v0)
    if not any(low[i] == "there" and (pos[i] in ("PRON", "ADV")) for i in range(lo, min(hi, v0 + 1))):
        return None
    post = [c for c in cands if v0 < c["wtok_start"] < hi
            and (pos[mention_head_wpos(c)] if mention_head_wpos(c) < len(pos) else None) in ("NOUN", "PROPN")]
    return min(post, key=lambda c: c["wtok_start"])["head"] if post else None


def _first_conjunct_agent(toks, pos, v0, cands):
    """NP-COORDINATION construction ('NP1 and NP2 V'): the subject HEAD is the FIRST conjunct NP1 (position
    picks the nearer NP2). GUARDED (learned from the wall drill): the coordinator immediately joins the two NPs
    (only NP-internal modifiers between); NO ', and' (clause/list coordination); NP1 not PP-governed. Returns
    NP1's head string or None. Ports experiments/exp_board_agent_construction_v1._first_conjunct_subject."""
    base = _positional_agent_base(cands, v0)
    if base is None:
        return None
    base_i = base["wtok_start"]
    if base_i >= v0:
        return None
    low = [t.lower() for t in toks]
    cand_starts = {c["wtok_start"]: c for c in cands}
    j = base_i - 1                                          # skip NP2's own left modifiers to reach the coordinator
    while j >= 0 and ((pos[j] if j < len(pos) else "") in _CONSTR_NPMOD or low[j] in ("the", "a", "an")):
        j -= 1
    if j < 0 or low[j] not in _CONSTR_COORD:
        return None
    if j - 1 >= 0 and low[j - 1] == ",":
        return None                                        # ', and' -> clause/list coordination
    k = j - 1                                              # NP1 head = the nominal immediately before the coordinator
    while k >= 0 and ((pos[k] if k < len(pos) else "") in _CONSTR_NPMOD or low[k] in ("the", "a", "an")):
        k -= 1
    if k < 0 or (pos[k] if k < len(pos) else "") not in ("NOUN", "PROPN", "PRON"):
        return None
    if _pp_governed_commastop(low, pos, k):
        return None                                        # NP1 is a PP object, not a subject conjunct
    return cand_starts[k]["head"] if k in cand_starts else None


# ---------------------------------------------------------------------------------------------------------------
# THE MARKED-CUE OVERRIDE IS A CUE, AND A CUE ENTERS AT ITS RELIABILITY (pri 106, 2026-09-14).
# `hybrid_agent_pick` keeps the high-validity WORD-ORDER default and lets a MARKED cue (passive-with-by /
# PP-governed / non-nominative positional pick) overturn it. That override is UNCONDITIONAL: it fires whether the
# role competition is sure or guessing. Measured on the board's who-did-what AGENT population (UD-EWT test, 1423
# gold agents): of the 103 clauses where it fires, the override FIXES 17 positional picks and BREAKS 45 -- which is
# exactly why the board shows the hybrid 0.0197 CI-separated BELOW its own positional floor.
# The brain does not let an unreliable decision overturn a high-validity default (Ernst & Banks 2002; Fetsch et al.
# 2011 -- reweighting is trial by trial). So license the override by the EVIDENCE DIFFERENCE it can show, in
# log-odds, between the two candidates:
#       licensed  iff  log P_agent(override candidate) - log P_agent(positional candidate) > theta
# with P_agent the role competition's agent probability CALIBRATED by that decision's own margin
# (margin_reliability), and theta a CRITERION LEARNED FROM COUNTS on UD-EWT train (the override is right only
# 193/667 = 0.29 of the times it is decisive there), never hand-set.
# MEASURED (UD-EWT test, n=1423, theta fitted on TRAIN and applied unchanged): positional floor 0.8468, landed
# unconditional hybrid 0.8271, GATED 0.8517 (+0.0246 CI95[+0.0155,+0.0337] over the landed hybrid, CI-separated;
# +0.0049 CI95[0.0000,+0.0098] over the floor). The gate keeps 10 of the 17 good overrides and only 3 of the 45
# bad ones; a PERFECT gate would give 0.8587. TWIN (the confidences permuted across items) falls to 0.8468 = the
# floor exactly, i.e. it stops overriding altogether -- the signal is in the per-decision confidence, not in the
# rate. OFF unless `heads` is supplied, so every existing caller is byte-identical.
# ---------------------------------------------------------------------------------------------------------------
AGENT_OVERRIDE_THETA = float(os.environ.get("HDLAB_AGENT_OVERRIDE_THETA", "6.5"))


def _calibrated_agent_prob(toks, pos, heads, i1, want_role, tab, rel):
    """P(nominal i1 really bears the agent role), the MAP mass replaced by the count-calibrated reliability of a
    decision taken at this margin (calibrate, do not marginalise)."""
    if not (1 <= i1 <= len(pos)) or not is_arg_head(list(toks), list(pos), i1):
        return 1.0 / len(ROLE_CLASSES)
    p = np.asarray(coarse_role_posterior(list(toks), list(pos), heads, i1, tab), dtype=float)
    k = int(np.argmax(p)); m = role_margin(p)
    r = margin_reliability(m, "role8", rel)
    w = ROLE_CLASSES.index(want_role)
    if k == w:
        return float(r)
    rest = 1.0 - float(p[k])
    return float((1.0 - r) * float(p[w]) / rest) if rest > 1e-12 else float((1.0 - r) / (len(ROLE_CLASSES) - 1))


def agent_override_licensed(toks, pos, heads, v0, cands, cm_head, validities=None, reliability=None,
                            theta: Optional[float] = None) -> bool:
    """Is the marked-cue override licensed by the role competition's own confidence? See the block above."""
    if heads is None or cm_head is None:
        return True                                   # no evidence available -> the landed unconditional behaviour
    base = _positional_agent_base(cands, v0)
    if base is None or str(base["head"]).lower() == str(cm_head).lower():
        return True
    tab = validities or load_coarse_validities()
    rel = reliability if reliability is not None else load_margin_reliability()
    from hdlab.thematic_role_labeler import is_passive_predicate
    want = "BY_AGENT" if is_passive_predicate(list(toks), list(pos), v0 + 1, heads=heads) else "SUBJ"
    idx = {str(c["head"]).lower(): mention_head_wpos(c) + 1 for c in cands}
    p_b = _calibrated_agent_prob(toks, pos, heads, idx.get(str(base["head"]).lower(), -1), want, tab, rel)
    p_c = _calibrated_agent_prob(toks, pos, heads, idx.get(str(cm_head).lower(), -1), want, tab, rel)
    th = AGENT_OVERRIDE_THETA if theta is None else float(theta)
    return bool(np.log(max(p_c, 1e-6)) - np.log(max(p_b, 1e-6)) > th)

def hybrid_agent_pick(toks, pos, v, cands, cluster_freq=None, weights=None, gaz=None,
                      subj_before=None, byhead_agent_cue=True, twin_seed=None,
                      construction=False, heads=None, validities=None, override_theta=None):
    """THE DEPLOYABLE brain-foundational AGENT route -- the AGENT counterpart to hybrid_role_patient. Keep the
    POSITIONAL pick (nearest preverbal candidate = the high-validity word-order cue, DOMINANT in canonical
    English) as the default, and invoke the Competition-Model competition (agent_competition_pick, which carries
    the landed byhead by-phrase CASE cue when byhead_agent_cue=True) ONLY when a MARKED override cue fires
    (agent_override_fires: passive-with-by / PP-governed positional pick / non-nominative-case positional pick).
    construction=True (opt-in): try the DECORRELATED construction cues FIRST (existential 'there' -> post-copular
    notional subject; guarded NP-coordination -> first conjunct), then the marked-cue-gated competition, then the
    word-order default. `cands` = list of mention dicts (each 'wtok_start'/'head'[/'cluster'/'wtok_end']); v =
    predicate index (0-based). Returns a head STRING, or None when there is no candidate (the caller keeps its own
    pick). twin_seed set => the info-free twin of the competition branch (agent_competition_pick's shuffle)."""
    if not cands:
        return None
    if construction:
        e = _existential_agent(toks, pos, v, cands)
        if e is not None:
            return e
        c = _first_conjunct_agent(toks, pos, v, cands)
        if c is not None:
            return c
    if agent_override_fires(toks, pos, v, cands):
        cm = agent_competition_pick(toks, pos, v, cands, cluster_freq=cluster_freq, weights=weights,
                                    gaz=gaz, twin_seed=twin_seed, subj_before=subj_before,
                                    byhead_agent_cue=byhead_agent_cue)
        # CONFIDENCE-LICENSED OVERRIDE (pri 106): `heads` supplied -> the override must show enough calibrated
        # evidence to overturn the word-order default; omitted -> byte-identical to the landed behaviour.
        if heads is None or agent_override_licensed(toks, pos, heads, v, cands, cm, validities, None,
                                                    override_theta):
            return cm
    base = _positional_agent_base(cands, v)                 # canonical clause -> word-order default
    return base["head"] if base is not None else None


__all__ = ["hybrid_role_patient", "competition_pick", "cue_supports", "voice_cues", "robust_passive",
           "gap_config", "DEFAULT_VALIDITIES", "CUES", "UNACC",
           "agent_competition_pick", "agent_competition_pick_conf", "agent_supports", "clause_bounds",
           "AGENT_VALIDITIES", "STRUCT_W", "NOMINATIVE_PRON", "_nominals_keep_pron",
           "by_governs", "participle_bypp_gate", "BYHEAD_W",
           "hybrid_agent_pick", "agent_override_fires", "agent_override_licensed",
           "role_margin", "role_decision", "margin_reliability", "observe_margin_outcome",
           "save_margin_reliability", "load_margin_reliability", "calibrated_class_posterior",
           "reliability_from_counts", "RELIABILITY_KINDS", "reliability_gain", "roles_with_decisions",
           "patient_belief", "patient_slot_confidence", "defer_below", "PATIENT_CLASSES",
           "purpose_cues", "purpose_complement_posterior", "observe_purpose_outcome",
           "load_purpose_validities", "save_purpose_validities", "PURPOSE_CLASSES"]
