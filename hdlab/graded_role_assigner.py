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

from typing import Dict, List, Optional, Sequence

import numpy as np

from hdlab.animacy_lexicon import lookup_animacy
from hdlab.graded_competition import map_pick, net_activation, softmax
from hdlab.relcl_resolver import (
    BE_AUX, RELATIVIZERS, _cands, is_object_gap, precise_passive, resolve_patient,
)
from hdlab.thematic_role_labeler import _is_participle, is_passive_clause, lemma_verb

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
    tag = pos[v0] if v0 < len(pos) else None
    if not _is_participle(toks[v0], tag):
        return False
    low = [t.lower() for t in toks]
    return any(by_governs(low, pos, i) for i in range(len(toks))
               if (pos[i] if i < len(pos) else None) in _BYHEAD_NOM)


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
    passive = is_passive_clause(toks, pos)
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


__all__ = ["hybrid_role_patient", "competition_pick", "cue_supports", "voice_cues", "robust_passive",
           "gap_config", "DEFAULT_VALIDITIES", "CUES", "UNACC",
           "agent_competition_pick", "agent_competition_pick_conf", "agent_supports", "clause_bounds",
           "AGENT_VALIDITIES", "STRUCT_W", "NOMINATIVE_PRON", "_nominals_keep_pron",
           "by_governs", "participle_bypp_gate", "BYHEAD_W"]
