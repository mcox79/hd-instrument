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
from hdlab.graded_competition import map_pick, net_activation
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

# validity-seeded AGENT cue weights -- a STATIC asset (like DEFAULT_VALIDITIES above), hand-set from cue
# validity, NOT trained; weight-robustness swept (SOLVED control (5): cm stays 0.211-0.229 across +/-50% on
# every discriminating cue). English is word-order-DOMINANT (agent preverbal); byagent dominates under PASSIVE.
AGENT_VALIDITIES: Dict[str, float] = {
    "preverbal": 3.0, "core_arg": 2.0, "animacy": 2.0, "salience": 2.0, "adjacency": 1.0, "byagent": 6.0}

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


def agent_supports(toks, pos, v0, cands, gaz=None, cluster_freq=None) -> Dict[str, list]:
    """Per-candidate AGENT support arrays for the Competition-Model cues. `cands` = [(wtok_start, head,
    cluster), ...]; v0 = predicate index (0-based). cluster_freq = passage-level {cluster: mention_count} for
    the Centering givenness cue. Reads ONLY toks/pos + the animacy lexicon + gazetteer + discourse counts --
    glass-box, no gold. Cues: preverbal (word-order), core_arg (PP-government scan), animacy, salience
    (Centering givenness), adjacency (clause-locality), byagent (passive voice)."""
    low = [t.lower() for t in toks]
    passive = is_passive_clause(toks, pos)
    cf = cluster_freq or {}
    S = {"preverbal": [], "core_arg": [], "animacy": [], "salience": [], "adjacency": [], "byagent": []}
    for (p, head, cl) in cands:
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
    return S


def agent_competition_pick(toks, pos, v, cands, cluster_freq=None,
                           weights: Optional[Dict[str, float]] = None, gaz=None, twin_seed=None) -> str:
    """The AGENT = argmax additive cue activation over the tracked/given candidate mentions (REUSES
    graded_competition.net_activation). `cands` = list of mention dicts (each with 'wtok_start', 'head',
    optional 'cluster'); v = predicate index (0-based) in toks-space; weights default to AGENT_VALIDITIES.
    Returns a head string, or '?' when there is no candidate. twin_seed set => INFO-FREE TWIN: shuffle each
    cue's per-candidate support across candidates (the structure->candidate mapping destroyed)."""
    w = AGENT_VALIDITIES if weights is None else weights
    c = [(m["wtok_start"], m["head"], m.get("cluster")) for m in cands]
    if not c:
        return "?"
    S = agent_supports(toks, pos, v, c, gaz, cluster_freq)
    if twin_seed is not None:
        rng = np.random.default_rng(twin_seed + v + len(c))
        S = {k: list(np.asarray(vv)[rng.permutation(len(vv))]) for k, vv in S.items()}
    A = net_activation(S, w)
    return c[int(np.argmax(A))][1]


__all__ = ["hybrid_role_patient", "competition_pick", "cue_supports", "voice_cues", "robust_passive",
           "gap_config", "DEFAULT_VALIDITIES", "CUES", "UNACC",
           "agent_competition_pick", "agent_supports", "clause_bounds", "AGENT_VALIDITIES",
           "NOMINATIVE_PRON", "_nominals_keep_pron"]
