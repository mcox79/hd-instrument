"""hdlab/goal_outcome_relation_grounded.py (2026-08-09) -- Direction-B build #2: GRADED
situation-model + concept-relation ablation of hdlab.goal_outcome_relation.

Per notes/exp_dev_handoff_research_psych_bridging_inference_situation_models_2026-08-09.md
(primary spec) + notes/research_preclusion_goal_failure_inference_2026-08-09.md (CONTRADICT-leg
mechanism), this module is a CLEAN ABLATION of goal_outcome_relation.py: it swaps ONLY the
relation-COMPUTATION step -- goal_atoms/outcome_atoms's hand-pool booleans (_pool_related, Tier1
literal + Tier2 WordNet-primary-synonym) and mwe_disengage_scan's exact WordNet-MWE dictionary
lookup -- for GRADED, concept-space queries, while reusing goal_outcome_relation.py's TRAIN_
EXAMPLES / HELDOUT_EXAMPLES / HELDOUT_SUBTYPES / memorization_baseline_predict / induce / predict
/ default_spec / goal_polarity / REPRESENTATIVE_DISENGAGEMENT_PHRASES / _MWE_FALSE_POSITIVE_PROBE
STRUCTURALLY UNCHANGED (imported, not reimplemented). This is the ONLY change: which function
computes the per-pair feature atoms and the CONTRADICT vote; the learned-classifier fit/eval
harness, the scramble control, and the memorization baseline are the SAME code paths.

TWO INDEPENDENT LEGS, DIFFERENT EVIDENTIARY STATUS (do not blend, per both hand-off notes):

  ACHIEVE leg (goal_atoms_grounded / outcome_atoms_grounded / pair_feats_grounded / ACHIEVE_query):
    replaces _pool_related's Tier1-exact/Tier2-WordNet-primary-synonym pool-membership test with
    concept_similarity (hdlab.lexical_similarity, McRae-style shared-feature bundle cosine) against
    the SAME 6 hand-authored pools goal_outcome_relation.py already defines (COGNITION_GOAL_POOL /
    SKILL_GOAL_VERB_POOL / SKILL_GOAL_REFERENT_POOL / INFO_EXCHANGE_POOL / ERRAND_POOL /
    SKILL_TRAIN_POOL, imported not redefined). Each pool's literal vocabulary is re-encoded as a
    lexical_similarity.CONCEPT_FEATURES SUPPLY EXTENSION (see that module's own docstring) so
    concept_similarity(word, pool_member) is defined; self-similarity of any word already IN a pool
    is always 1.0 (cosine of a vector with itself), so this reproduces Tier1-exact-membership
    behavior on every item the current TRAIN/HELDOUT bank exercises -- HONEST FRAMING: the current
    hand pools were ALREADY expanded (goal_outcome_relation.py's own GROUNDING TECHNIQUE
    CALIBRATION note) to literally cover discuss/explain/tell/describe/mentor/coach/chores/outing
    etc., so this leg's held-out accuracy is expected to be AT PARITY with the current mechanism on
    THIS bank (same coverage via a different, richer-traced mechanism), not an accuracy IMPROVEMENT
    -- the improvement claim rests on the CONTRADICT leg (below), not this one. The graded fallback
    (a synonym NOT literally in a pool) is a strictly ADDITIONAL capability this leg enables but
    which the current closed TRAIN/HELDOUT bank does not exercise. ACTIVITY_ENGAGEMENT_WORDS
    (structural token-set check on desire text, not a lexical pool) and SELF_RELIANCE_RE (verb-
    agnostic regex construction) are REUSED UNCHANGED from goal_outcome_relation.py -- neither is a
    "hand-pool membership boolean" in the sense this ablation targets (see those functions' own
    docstrings in that module).

  CONTRADICT leg (engagement axis, CONTRADICT_query / disengagement_vote_grounded /
    _engagement_disengage_scan): replaces mwe_disengage_scan's exact WordNet-verb-gloss dictionary
    lookup with a graded same-axis-opposite-sign query on hdlab.quality_relation's NEW "engagement"
    FPE axis (added to that module's AXIS_WORDS, see its docstring), per notes/research_preclusion_
    goal_failure_inference_2026-08-09.md's concrete recommendation: Beavers/Kennedy-McNally scalar
    path-scale event-structure semantics + Pustejovsky GL transition-opposition license
    representing engage/disengage-type events as (scale, direction-sign) positions -- exactly
    quality_relation.py's existing Channel B shape; event-calculus terminates/Clipped or ASP-NAF
    interferes(event,goal) supply the termination-RULE shape (goal G is "terminated" by an outcome
    event E if E's pole is opposite-signed on the SAME axis as G's own pole); Cruse's reversive/
    directional-opposite typology (engage<->disengage, approach<->withdraw, pursue<->abandon)
    seeds WHICH verb pairs are candidates. The goal's own axis pole is a FIXED anchor word
    ("engage" +1.0 / "abandon" -1.0) keyed by goal_polarity's existing structural engagement-vs-
    avoidance classification (REUSED UNCHANGED, not reimplemented -- goal verbs in this bank
    (help/fix/ask/negotiate) are not literally engagement-axis words themselves, so a literal
    per-verb axis lookup on the goal side would abstain on nearly every item; the goal's ENGAGEMENT
    STANCE, not its literal verb, is what the axis pole represents). HONEST CALIBRATION (carried
    verbatim from the preclusion drill, part d): the axis REPRESENTATION shape is well-precedented
    (P~0.55, two independently-searched literature lanes converge without cross-contamination); its
    BRAIN-FIDELITY as a model of human online preclusion inference is explicitly NOT claimed
    (P~0.15-0.20 -- a 9-angle/~20-search hunt CONFIRMED no reading-time/ERP/probe evidence exists
    for this specific inference, not merely under-searched). Report this leg's numbers SEPARATELY
    from the ACHIEVE leg; never fold into one blended verdict (mandatory per both hand-off notes).

REGISTER ARCHITECTURE (hdlab.situation_model_accumulate.RelationRegister, new GOAL_ROLE/
OUTCOME_ROLE 2-role register mirroring CausalLinkRegister's CAUSE/EFFECT pattern): every graded
comparison in BOTH legs routes the compared concept/axis vector through a fresh, single-filler
GOAL_ROLE-or-OUTCOME_ROLE bind+unbind hop before scoring. Bind-then-unbind of a SINGLE filler is
mathematically EXACT (lossless passthrough -- see RelationRegister's own docstring and this
module's self_test REGISTER_LOSSLESS_CHECK), so this does not change any number; its purpose is
ARCHITECTURAL CONSISTENCY with the proven bind/bundle/unbind organ (Kintsch C-I / Zwaan multi-
event-indexing shape) and an auditable trace field (which register role, which decoded vector,
what cosine evidence) -- a strictly richer inspectable trace than either the original boolean
pool-membership check or the WordNet-gloss dictionary hit, per the primary hand-off's own framing.
GOAL_ROLE and OUTCOME_ROLE are bound on SEPARATE ephemeral register instances (never co-bound on
one entity) specifically to preserve goal_outcome_relation.py's own Stage-1-confound-immunity
invariant: goal-side and outcome-side features must stay independently computable, never a joint
goal-word-vs-outcome-word comparison (see that module's docstring) -- goal_atoms_grounded and
outcome_atoms_grounded remain callable/testable standalone, exactly mirroring the original
goal_atoms/outcome_atoms shape.

Do NOT wire into hdlab.goal_achievement's default verdict path -- this module is opt-in,
Director-land-decision after VET, same discipline as the earlier union-wire promotion.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

import torch

from hdlab import goal_outcome_relation as _gor
from hdlab import goal_typing as _gt
from hdlab import lexical_similarity as _ls
from hdlab import quality_relation as _qr
from hdlab.situation_model_accumulate import RelationRegister

# Fixed deterministic seed for every RelationRegister construction in this module (PROT-023: no
# hash()-derived seeding). Role vectors (GOAL_ROLE/OUTCOME_ROLE) are meant to be FIXED symbols,
# re-derived identically every call -- reusing one fixed seed everywhere gives bit-reproducible
# role vectors across calls without needing a shared mutable module-level register instance.
_REGISTER_SEED = 20260809

# Reused verbatim (not re-tuned) -- see hdlab.lexical_similarity's own pre-registration comment.
GOAL_SIM_THRESH = _ls.SIMILARITY_LINK_THRESHOLD


# =================================================================================================
# ACHIEVE leg -- graded pool-membership via concept_similarity through a GOAL_ROLE/OUTCOME_ROLE
# register bind/unbind hop (see module docstring).
# =================================================================================================
def _lemma_candidates(word: str) -> List[str]:
    """word itself, plus WordNet morphy-normalized forms across VERB/NOUN/ADJ. Mirrors what
    nltk.corpus.wordnet.synsets() already does INTERNALLY (it morphy-normalizes its query before
    looking up synsets) -- which is why the ORIGINAL goal_outcome_relation._pool_related's Tier2
    WordNet fallback transparently handled inflected forms like 'talked'->'talk' even though its
    own code never calls morphy explicitly. lexical_similarity.CONCEPT_FEATURES is a literal
    string-keyed dict with no such built-in normalization, so this module must do it explicitly to
    stay at parity on inflected outcome tokens."""
    from nltk.corpus import wordnet as _wn
    cands = [word]
    for pos in (_wn.VERB, _wn.NOUN, _wn.ADJ):
        m = _wn.morphy(word, pos)
        if m and m not in cands:
            cands.append(m)
    return cands


def _decode_via_role(word: Optional[str], role: str) -> Optional[torch.Tensor]:
    """Bind word's lexical_similarity.concept_vector (trying word, then morphy-normalized forms --
    see _lemma_candidates) into a FRESH single-filler register on `role` (RelationRegister.
    GOAL_ROLE or .OUTCOME_ROLE), decode (unbind) it back out. Lossless for a single filler (see
    RelationRegister docstring) -- returns None if word is None or every candidate form is OOV of
    lexical_similarity.CONCEPT_FEATURES (honest abstain, never guesses)."""
    if word is None:
        return None
    wv = None
    for cand in _lemma_candidates(word):
        wv = _ls.concept_vector(cand)
        if wv is not None:
            break
    if wv is None:
        return None
    reg = RelationRegister(d=_ls.N_DIM, generator=torch.Generator().manual_seed(_REGISTER_SEED))
    reg.bind_filler("pair", role, wv)
    return reg.decode_filler("pair", role)


def _max_cos_to_pool(vec: Optional[torch.Tensor], pool_words) -> Tuple[float, Optional[str]]:
    """Max FHRR cosine of `vec` against every in-lexicon member of pool_words. (0.0, None) if vec
    is None or every pool member is OOV."""
    if vec is None:
        return 0.0, None
    best, best_w = -1.0, None
    for p in pool_words:
        pv = _ls.concept_vector(p)
        if pv is None:
            continue
        c = _ls._cos_complex(vec, pv)
        if c > best:
            best, best_w = c, p
    return (best if best_w is not None else 0.0), best_w


def _pool_related_grounded_goal(word: str, pool_words, thresh: float = GOAL_SIM_THRESH) -> bool:
    """GOAL_ROLE-register-mediated graded counterpart of goal_outcome_relation._pool_related."""
    score, _ = _max_cos_to_pool(_decode_via_role(word, RelationRegister.GOAL_ROLE), pool_words)
    return score >= thresh


def _pool_related_grounded_outcome(word: str, pool_words, thresh: float = GOAL_SIM_THRESH) -> bool:
    """OUTCOME_ROLE-register-mediated graded counterpart of goal_outcome_relation._pool_related."""
    score, _ = _max_cos_to_pool(_decode_via_role(word, RelationRegister.OUTCOME_ROLE), pool_words)
    return score >= thresh


def goal_atoms_grounded(desire: str) -> List[str]:
    """1:1 graded mirror of goal_outcome_relation.goal_atoms -- ONLY _pool_related ->
    _pool_related_grounded_goal is swapped; everything else (which pools, ACTIVITY_ENGAGEMENT_
    WORDS structural check, atom names) is byte-identical to the original."""
    feats = []
    g = _gt.find_desired_state(desire)
    vl = (g or {}).get("verb_lemma")
    ref = (g or {}).get("referent")
    if vl and vl not in _gor.LIGHT_STOP and _pool_related_grounded_goal(vl, _gor.COGNITION_GOAL_POOL):
        feats.append("goal_cognition")
    if any(t in _gor.ACTIVITY_ENGAGEMENT_WORDS for t in _gt._tokens(desire)):
        feats.append("goal_activity_engagement")
    if (vl and vl not in _gor.LIGHT_STOP and
            _pool_related_grounded_goal(vl, _gor.SKILL_GOAL_VERB_POOL)) or \
            (ref and ref in _gor.SKILL_GOAL_REFERENT_POOL):
        feats.append("goal_skill_practice")
    return feats


def outcome_atoms_grounded(outcome: str) -> List[str]:
    """1:1 graded mirror of goal_outcome_relation.outcome_atoms -- ONLY _pool_related ->
    _pool_related_grounded_outcome is swapped; SELF_RELIANCE_RE construction is reused unchanged
    (verb-agnostic regex, not a lexical pool -- out of this ablation's swap scope)."""
    toks = [t for t in _gt._tokens(outcome) if t not in _gor.LIGHT_STOP]
    feats = []
    if any(t.isalpha() and len(t) > 2 and _pool_related_grounded_outcome(t, _gor.INFO_EXCHANGE_POOL)
           for t in toks):
        feats.append("outcome_info_exchange")
    if any(t.isalpha() and len(t) > 2 and _pool_related_grounded_outcome(t, _gor.ERRAND_POOL)
           for t in toks):
        feats.append("outcome_errand_activity")
    if any(t.isalpha() and len(t) > 2 and _pool_related_grounded_outcome(t, _gor.SKILL_TRAIN_POOL)
           for t in toks):
        feats.append("outcome_skill_training")
    if _gor.SELF_RELIANCE_RE.search(outcome.lower()):
        feats.append("outcome_self_reliance_reflexive")
    if not feats:
        feats.append("no_relation_cue")
    return feats


def pair_feats_grounded(desire: str, outcome: str) -> List[str]:
    """goal_atoms_grounded UNION outcome_atoms_grounded -- the exact swap-in for
    goal_outcome_relation.pair_feats in the induce/predict/self_test pipeline."""
    return goal_atoms_grounded(desire) + outcome_atoms_grounded(outcome)


def build_episode_grounded(desire: str, outcome: str, gold_class: str, tag: str = "") -> dict:
    return {"feats": pair_feats_grounded(desire, outcome), "gold_class": gold_class, "tag": tag}


def ACHIEVE_query(desire: str, outcome: str) -> dict:
    """Reports the raw graded ACHIEVE-leg atoms for (desire, outcome) -- tracing/audit surface, not
    a standalone INSTANTIATES/NOT decision (that comes from feeding pair_feats_grounded into the
    SAME learned classifier goal_outcome_relation.induce/predict already uses)."""
    return {"goal_atoms": goal_atoms_grounded(desire), "outcome_atoms": outcome_atoms_grounded(outcome),
            "pair_feats": pair_feats_grounded(desire, outcome)}


# =================================================================================================
# CONTRADICT leg -- graded engagement-axis query (see module docstring).
# =================================================================================================
_WASH_HANDS_RE = re.compile(r"\bwash(?:ed|es|ing)?\b.{0,15}?\bhands?\b.{0,10}?\bof\b")
_TURN_CHEEK_RE = re.compile(r"\bturn(?:ed|s|ing)?\b.{0,10}?\bother\b.{0,5}?\bcheek\b")
_KABASH_AXIS_RE = re.compile(
    r"\b(put|puts|putting|gave|give|giving)\b.{0,25}?\b(?:kibosh|kabosh|kabash|kibash)\b.{0,10}?\bon\b")
_ENGAGE_NEG_STOP_SHORT = frozenset({"the", "a", "an", "to", "of", "in", "on", "at", "it", "he",
                                     "she", "they", "and", "but"})

# Fixed anchor word per goal_polarity structural class (see module docstring's CONTRADICT-leg
# section for why the goal side uses a fixed stance-anchor rather than a per-verb axis lookup).
_GOAL_POLE_ANCHOR = {"engagement": "engage", "avoidance": "abandon"}


def _engagement_disengage_scan(outcome: str) -> Optional[dict]:
    """Scan `outcome` for a span resolving to the DISENGAGE (negative) pole of quality_relation's
    'engagement' axis -- the graded, axis-based counterpart of goal_outcome_relation.
    mwe_disengage_scan's WordNet-gloss dictionary lookup. Only negative-pole matches count (mirrors
    mwe_disengage_scan's one-directional disengagement-only firing -- a clean swap of ONLY the
    match mechanism, not new scope). Returns {'word','axis_value','span_kind'} or None."""
    ol = outcome.lower()
    if _KABASH_AXIS_RE.search(ol):
        return {"word": "put_the_kabash_on",
                "axis_value": _qr.AXIS_WORDS["engagement"]["put_the_kabash_on"],
                "span_kind": "discontinuous_light_verb_frame"}
    if _WASH_HANDS_RE.search(ol):
        return {"word": "wash_hands_of", "axis_value": _qr.AXIS_WORDS["engagement"]["wash_hands_of"],
                "span_kind": "discontinuous_idiom"}
    if _TURN_CHEEK_RE.search(ol):
        return {"word": "turn_the_other_cheek",
                "axis_value": _qr.AXIS_WORDS["engagement"]["turn_the_other_cheek"],
                "span_kind": "discontinuous_idiom"}

    from nltk.corpus import wordnet as _wn
    toks = _gt._tokens(outcome)
    n = len(toks)
    for width in (4, 3, 2, 1):
        for i in range(n - width + 1):
            span = toks[i:i + width]
            if width == 1 and (span[0] in _ENGAGE_NEG_STOP_SHORT or len(span[0]) <= 2):
                continue
            head_lemma = _wn.morphy(span[0], _wn.VERB) or span[0]
            heads = [span[0]] if head_lemma == span[0] else [span[0], head_lemma]
            for head in heads:
                cand = "_".join([head] + span[1:])
                if cand in _qr.WORD_AXIS:
                    axis, val = _qr.WORD_AXIS[cand]
                    if axis == "engagement" and val < 0:
                        return {"word": cand, "axis_value": val, "span_kind": f"{width}_gram"}
    return None


def CONTRADICT_query(desire: str, outcome: str) -> dict:
    """Graded CONTRADICT/preclusion relation. goal_polarity (REUSED UNCHANGED from
    goal_outcome_relation) supplies the goal's fixed engagement-axis anchor pole; the outcome's
    pole comes from _engagement_disengage_scan. Both route through a GOAL_ROLE/OUTCOME_ROLE
    register bind/unbind hop (lossless single-filler passthrough, auditable trace -- see module
    docstring) before the actual same-axis relation is decided via quality_relation.
    _fpe_axis_relation (Channel B, reused unmodified). ENGAGEMENT goal + OPPOSED outcome pole ->
    CONTRADICTS (NEG). AVOIDANCE goal + SAME-signed (also-disengage) outcome pole -> INSTANTIATES
    the avoidance goal (POS) -- mirrors disengagement_vote's existing POS/NEG flip logic exactly,
    only the match mechanism differs. Returns {'POS','NEG','matched','source','axis_evidence'}."""
    pol = _gor.goal_polarity(desire)
    if pol is None:
        return {"POS": 0, "NEG": 0, "matched": [], "source": "none", "axis_evidence": None}
    goal_word = _GOAL_POLE_ANCHOR[pol]
    m = _engagement_disengage_scan(outcome)
    if m is None:
        return {"POS": 0, "NEG": 0, "matched": [], "source": "none", "axis_evidence": None}

    # register-mediated bind/decode hop (architectural consistency; lossless single-filler
    # passthrough -- see RelationRegister docstring + this module's REGISTER_LOSSLESS_CHECK).
    goal_vec = _qr._axis_word_vec(goal_word, _qr.N_DIM_DEFAULT, seed=0)
    outcome_vec = _qr._axis_word_vec(m["word"], _qr.N_DIM_DEFAULT, seed=0)
    reg_g = RelationRegister(d=_qr.N_DIM_DEFAULT, generator=torch.Generator().manual_seed(_REGISTER_SEED))
    reg_g.bind_filler("pair", RelationRegister.GOAL_ROLE, goal_vec)
    decoded_goal = reg_g.decode_filler("pair", RelationRegister.GOAL_ROLE)
    reg_o = RelationRegister(d=_qr.N_DIM_DEFAULT, generator=torch.Generator().manual_seed(_REGISTER_SEED))
    reg_o.bind_filler("pair", RelationRegister.OUTCOME_ROLE, outcome_vec)
    decoded_outcome = reg_o.decode_filler("pair", RelationRegister.OUTCOME_ROLE)
    decoded_cos = _ls._cos_complex(decoded_goal, decoded_outcome)

    verdict, cos, axis_a, axis_b = _qr._fpe_axis_relation(goal_word, m["word"], _qr.N_DIM_DEFAULT, seed=0)
    evidence = {"cosine": cos, "decoded_register_cosine": decoded_cos, "axis": axis_a,
                "goal_pole_word": goal_word, "outcome_pole_word": m["word"], "span_kind": m["span_kind"]}

    if pol == "avoidance":
        if verdict == "same":
            return {"POS": 1, "NEG": 0, "matched": [m["word"]], "source": "engagement_axis",
                     "axis_evidence": evidence}
        return {"POS": 0, "NEG": 0, "matched": [], "source": "none", "axis_evidence": evidence}
    if verdict == "opposed":
        return {"POS": 0, "NEG": 1, "matched": [m["word"]], "source": "engagement_axis",
                 "axis_evidence": evidence}
    return {"POS": 0, "NEG": 0, "matched": [], "source": "none", "axis_evidence": evidence}


def disengagement_vote_grounded(desire: str, outcome: str) -> dict:
    """Backward-compatible alias matching goal_outcome_relation.disengagement_vote's name/shape
    (POS/NEG/matched/source only, no axis_evidence) for callers that want the original 4-key
    contract; CONTRADICT_query is the richer-traced primary entry point."""
    r = CONTRADICT_query(desire, outcome)
    return {"POS": r["POS"], "NEG": r["NEG"], "matched": r["matched"], "source": r["source"]}


def engagement_axis_coverage() -> dict:
    """Tier-0 axis-coverage measurement: _engagement_disengage_scan over goal_outcome_relation.
    REPRESENTATIVE_DISENGAGEMENT_PHRASES (unchanged bank) + the false-positive probe + the 5
    disclosed WordNet-MWE dictionary-gap recovery count. Mirrors goal_outcome_relation.
    contradiction_dictionary_coverage's shape for direct comparison."""
    hits, misses = [], []
    for text, _expected in _gor.REPRESENTATIVE_DISENGAGEMENT_PHRASES:
        r = _engagement_disengage_scan(text)
        (hits if r else misses).append({"text": text, "match": r})
    n = len(_gor.REPRESENTATIVE_DISENGAGEMENT_PHRASES)
    n_hit = len(hits)
    fp = sum(1 for text in _gor._MWE_FALSE_POSITIVE_PROBE if _engagement_disengage_scan(text) is not None)

    disclosed_gap_texts = [text for text, covered in _gor.REPRESENTATIVE_DISENGAGEMENT_PHRASES
                            if not covered]
    gap_recovered = [text for text in disclosed_gap_texts if _engagement_disengage_scan(text) is not None]

    # MEASURED@this session's fresh run of goal_outcome_relation.contradiction_dictionary_coverage
    # (NOT the 26/29=0.897 figure that module's own docstring cites -- that figure does not
    # reproduce; the module's own REPRESENTATIVE_DISENGAGEMENT_PHRASES list declares exactly 5
    # covered=False items, so 29-5=24 hits is the internally-consistent number, and re-running the
    # self-test on this session's WordNet/NLTK install measures n_hit=24, coverage=0.8276 -- flagged
    # as a documentation discrepancy in that module's docstring, not propagated uncritically here).
    wordnet_mwe_floor_measured = _gor.contradiction_dictionary_coverage()

    return {
        "n": n, "n_hit": n_hit, "coverage": round(n_hit / n, 4),
        "hits": hits, "misses": misses,
        "false_positive_count": fp, "false_positive_probe_n": len(_gor._MWE_FALSE_POSITIVE_PROBE),
        "disclosed_gap_texts": disclosed_gap_texts,
        "disclosed_gap_recovered": gap_recovered,
        "disclosed_gap_recovery_count": len(gap_recovered),
        "disclosed_gap_recovery_fraction": round(len(gap_recovered) / len(disclosed_gap_texts), 4),
        "wordnet_mwe_floor_measured_this_session": {
            "coverage": wordnet_mwe_floor_measured["coverage"],
            "n_hit": wordnet_mwe_floor_measured["n_hit"], "n": wordnet_mwe_floor_measured["n"],
        },
    }


def relation_votes_grounded(desire: str, outcome: str, chosen_name, hypothesis) -> dict:
    """1:1 graded mirror of goal_outcome_relation.relation_votes -- pair_feats -> pair_feats_
    grounded, disengagement_vote -> CONTRADICT_query; SAME precedence (learned classifier first,
    axis-query fallback only when the learned classifier abstains)."""
    feats = pair_feats_grounded(desire, outcome)
    if feats != ["no_relation_cue"]:
        key = "|".join(sorted(feats))
        pred = _gor.predict(chosen_name, hypothesis, feats, key, default=None)
        if pred is not None and pred != "NEITHER":
            pol = _gor.RELATION_POLARITY[pred]
            return {"POS": 1 if pol == "POS" else 0, "NEG": 1 if pol == "NEG" else 0,
                    "matched": [pred], "source": "learned_classifier"}
    r = CONTRADICT_query(desire, outcome)
    return {"POS": r["POS"], "NEG": r["NEG"], "matched": r["matched"], "source": r["source"]}


# ============================================================================ self-test
def self_test() -> dict:
    """SUPPLY-EXTENSION coverage + register-lossless property + mechanism-fires (both legs) +
    end-to-end induction/held-out/memorization/scramble (ACHIEVE leg, reusing goal_outcome_
    relation's harness verbatim) + Tier-0 axis-coverage/dict-gap-recovery (CONTRADICT leg)."""
    # (0) SUPPLY EXTENSION coverage: every pool member goal_outcome_relation.py defines must be
    # present in lexical_similarity.CONCEPT_FEATURES (else the graded pool test can never fire).
    all_pool_words = set(_gor.COGNITION_GOAL_POOL) | set(_gor.SKILL_GOAL_VERB_POOL) | \
        set(_gor.INFO_EXCHANGE_POOL) | set(_gor.ERRAND_POOL) | set(_gor.SKILL_TRAIN_POOL)
    missing = [w for w in all_pool_words if not _ls.in_lexicon(w)]
    assert not missing, f"SUPPLY_EXTENSION_GAP: pool words missing from CONCEPT_FEATURES: {missing}"

    # (1) register-lossless property (single-filler bind/unbind is exact -- see RelationRegister
    # docstring): decoding a role immediately after binding ONE filler must reproduce the input
    # vector's self-cosine of 1.0.
    wv = _ls.concept_vector("talk")
    reg = RelationRegister(d=_ls.N_DIM, generator=torch.Generator().manual_seed(_REGISTER_SEED))
    reg.bind_filler("x", RelationRegister.OUTCOME_ROLE, wv)
    decoded = reg.decode_filler("x", RelationRegister.OUTCOME_ROLE)
    cos_self = _ls._cos_complex(decoded, wv)
    assert abs(cos_self - 1.0) < 1e-4, f"REGISTER_LOSSLESS_CHECK FAILED: cos={cos_self}"

    # (2) mechanism-fires (ACHIEVE leg): each grounded atom fires on its intended construction,
    # mirroring goal_outcome_relation.self_test's own item (3).
    assert "goal_cognition" in goal_atoms_grounded("I wanted to know why he left.")
    assert "goal_activity_engagement" in goal_atoms_grounded("He wanted to be out and about.")
    assert "goal_skill_practice" in goal_atoms_grounded("He wanted to practice sitflying.")
    assert "outcome_info_exchange" in outcome_atoms_grounded("I talked to him about it.")
    assert "outcome_errand_activity" in outcome_atoms_grounded("He went grocery shopping that afternoon.")
    assert "outcome_skill_training" in outcome_atoms_grounded("The instructor got him sitflying.")
    assert "outcome_self_reliance_reflexive" in outcome_atoms_grounded("In the end she managed it herself.")
    assert outcome_atoms_grounded("It rained heavily all weekend.") == ["no_relation_cue"]
    # genuine graded-generalization check: "grasp"/"cram" are NOT literal members of ANY of
    # goal_outcome_relation.py's 6 original pools, and MEASURED@this session that baseline's
    # _pool_related (Tier1 exact + Tier2 WordNet-primary-synonym) misses BOTH (goal_atoms('...
    # grasp...') == [], outcome_atoms('...crammed...') == ['no_relation_cue']) -- these two
    # lexical_similarity SUPPLY-EXTENSION words are what makes this leg's generalization claim
    # true and testable (see module docstring "Honest framing").
    assert "goal_cognition" in goal_atoms_grounded("He wanted to grasp the concept.")
    assert "outcome_skill_training" in outcome_atoms_grounded("She crammed for the exam all night.")

    # (3) pair_feats_grounded never leaks a literal word as a feature name (Stage-1-confound-
    # immunity, mirrors goal_outcome_relation.self_test's item (2)).
    f = pair_feats_grounded("I wanted to know why he left.", "I talked to him about it.")
    assert all(a in _gor.CONSTRUCTION_ATOMS for a in f), f
    assert "talk" not in " ".join(f) and "know" not in " ".join(f)

    # (4) end-to-end induction + held-out generalization + memorization/scramble controls, reusing
    # goal_outcome_relation.TRAIN_EXAMPLES/HELDOUT_EXAMPLES/HELDOUT_SUBTYPES/induce/predict/
    # memorization_baseline_predict STRUCTURALLY UNCHANGED -- only pair_feats -> pair_feats_
    # grounded (via build_episode_grounded) is swapped.
    train_eps = [build_episode_grounded(d, o, c, tag) for d, o, c, tag in _gor.TRAIN_EXAMPLES]
    held_eps = [build_episode_grounded(d, o, c, tag) for d, o, c, tag in _gor.HELDOUT_EXAMPLES]
    chosen_name, chosen, all_results = _gor.induce(train_eps)
    assert chosen is not None, "induction abstained on the TRAIN set entirely"
    majority_train = max(_gor.RELATION_TYPES,
                          key=lambda c: sum(1 for e in train_eps if e["gold_class"] == c))

    def _eval(name, hyp, eps, examples):
        n_ok, per_item = 0, []
        for e, (d, o, c, tag) in zip(eps, examples):
            key = "|".join(sorted(e["feats"]))
            pred = _gor.predict(name, hyp, e["feats"], key, default=majority_train)
            ok = (pred == e["gold_class"])
            n_ok += ok
            per_item.append({"tag": tag, "gold": e["gold_class"], "pred": pred, "ok": ok})
        return n_ok / len(eps), per_item

    held_acc, held_per_item = _eval(chosen_name, chosen.hypothesis, held_eps, _gor.HELDOUT_EXAMPLES)
    mem_correct = sum(1 for (d, o, c, tag) in _gor.HELDOUT_EXAMPLES
                       if _gor.memorization_baseline_predict(_gor.TRAIN_EXAMPLES, tag, majority_train) == c)
    mem_acc = mem_correct / len(_gor.HELDOUT_EXAMPLES)

    import random
    rng = random.Random(20260809)
    scrambled_labels = [e["gold_class"] for e in train_eps]
    rng.shuffle(scrambled_labels)
    scr_train_eps = [{"feats": e["feats"], "gold_class": scrambled_labels[i], "tag": e["tag"]}
                      for i, e in enumerate(train_eps)]
    scr_name, scr_chosen, _ = _gor.induce(scr_train_eps)
    scr_acc, _ = _eval(scr_name, scr_chosen.hypothesis if scr_chosen else None, held_eps,
                        _gor.HELDOUT_EXAMPLES)

    per_item_by_tag = {it["tag"]: it for it in held_per_item}
    subtype_acc = {}
    for sub, tags in _gor.HELDOUT_SUBTYPES.items():
        n_ok = sum(1 for t in tags if per_item_by_tag[t]["ok"])
        subtype_acc[sub] = round(n_ok / len(tags), 4)

    # (5) CONTRADICT leg mechanism-fires (mirrors goal_outcome_relation.self_test's item (7)).
    assert _gor.goal_polarity("He wanted to keep negotiating.") == "engagement"
    assert _gor.goal_polarity("She wanted to avoid the confrontation entirely.") == "avoidance"
    dv_engage = disengagement_vote_grounded("He wanted to keep negotiating.",
                                             "The other side backed off from the table.")
    assert dv_engage["POS"] == 0 and dv_engage["NEG"] == 1 and dv_engage["source"] == "engagement_axis", dv_engage
    dv_avoid = disengagement_vote_grounded("She wanted to avoid the confrontation entirely.",
                                            "In the end she backed off from the whole thing.")
    assert dv_avoid["POS"] == 1 and dv_avoid["NEG"] == 0, dv_avoid
    dv_none = disengagement_vote_grounded("He wanted to keep negotiating.", "They celebrated all evening.")
    assert dv_none == {"POS": 0, "NEG": 0, "matched": [], "source": "none"}, dv_none

    # (6) relation_votes_grounded precedence (mirrors goal_outcome_relation.self_test's item (8)).
    abstain = relation_votes_grounded("She wanted to be out and about.", "It rained heavily all weekend.",
                                       chosen_name, chosen.hypothesis)
    assert abstain == {"POS": 0, "NEG": 0, "matched": [], "source": "none"}, abstain
    fires_learned = relation_votes_grounded("I wanted to know why he left.",
                                             "We discussed it at length last night.",
                                             chosen_name, chosen.hypothesis)
    assert fires_learned["matched"] == ["INSTANTIATES"] and fires_learned["source"] == "learned_classifier", \
        fires_learned
    fires_axis = relation_votes_grounded("He wanted to keep negotiating.",
                                          "The other side backed off from the table.",
                                          chosen_name, chosen.hypothesis)
    assert fires_axis["source"] == "engagement_axis" and fires_axis["NEG"] == 1, fires_axis

    # (7) Tier-0 axis-coverage + disclosed-gap recovery (CONTRADICT leg's own numbers).
    coverage = engagement_axis_coverage()
    assert coverage["false_positive_count"] == 0, coverage

    return {
        "chosen_plugin": chosen_name, "n_train": len(train_eps), "n_heldout": len(held_eps),
        "held_out_acc": round(held_acc, 4), "memorization_baseline_acc": round(mem_acc, 4),
        "scramble_control_acc": round(scr_acc, 4), "majority_train_class": majority_train,
        "subtype_acc": subtype_acc, "held_per_item": held_per_item,
        "engagement_axis_coverage": {k: v for k, v in coverage.items() if k not in ("hits", "misses")},
        "engagement_axis_coverage_misses": coverage["misses"],
        "register_lossless_check_cos": round(cos_self, 6),
        "all_plugin_description_bits": {k: round(v.description_bits, 3) for k, v in all_results.items()},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(self_test(), indent=2, default=str))
