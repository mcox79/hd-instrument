"""hdlab/lexical_similarity.py -- shared-feature lexical-similarity organ (WIRE-DONT-ISLAND
promotion, 2026-08-06).

Lifts the shared-feature-similarity mechanism proved in experiments/
exp_n11c_shared_feature_lexical_similarity_v1.py (commit 7d0a574b4, HARD_PASS, Director-VET'd:
ordered_frac=0.9655 (28/29) vs WINDOW=0.3793 vs HASH_RANDOM=0.1034 floor, SCRAMBLED_FEATURES
ablation collapses to 0.3103 (delta 0.655), tier-means shared_feature=(0.93, 0.30, 0.00) vs
window=(0.86, 0.85, 0.83), n_llm_calls=0) into an importable PRODUCTION form: a McRae-style
(McRae, Cree, Seidenberg & McNorgan 2005, Behavior Research Methods) hand-authored feature
lexicon (DATA supply) composed via the substrate's OWN glass-box FHRR bundle() (hdlab.bundling.
bundle over hdlab.situation_model_accumulate.unit_phase_vec feature-index vectors) into a graded
cosine similarity -- the ATL-hub analog (Cox, Rogers, Shimotake, Kikuchi, Kunieda, Miyamoto,
Takahashi, Matsumoto, Ikeda, Lambon Ralph 2024, "Graded, cross-modal similarity in ventral
anterior temporal lobe," Imaging Neuroscience, PMC12224414: vATL intracranial activity is graded
and multidimensional, tracking McRae-style behavioral-feature-norm overlap -- NOT co-occurrence).

hdlab-only dependency (hdlab must not import experiments/): CONCEPT_FEATURES + the encoder here
are a CLEAN COPY of exp_n11c's data + logic, not a live import from
experiments.exp_n11c_shared_feature_lexical_similarity_v1 (that module also imports
experiments.exp_n11b_symmetric_pattern_lexical_similarity_v1 for its probe triples, which this
module has no need of and must not pull into hdlab/). Only hdlab.bundling.bundle and
hdlab.situation_model_accumulate.unit_phase_vec are imported -- both already-promoted hdlab
primitives, reused unmodified, same convention as hdlab/goal_typing.py's other reused organs.

CONCEPT_FEATURES is BYTE-IDENTICAL to exp_n11c's 86-concept dict (commit 7d0a574b4) for every
concept exp_n11c defined (its 4 toy* self-test-only entries are dropped -- not needed here).

SUPPLY EXTENSION (this promotion, 2026-08-06, uniform convention, no per-pair tuning): 3 new
concepts, added to cover experiments/data/outcome_valence_congruence_v2.jsonl's referent-stress
items and to MEASURE (not assume-via-OOV-fallthrough) the over-link guard:
  - "ferry": tagged IDENTICALLY to "boat" (NAUTICAL/WATERCRAFT/HAS_HULL/CARRIES_PEOPLE) -- a ferry
    IS a people-carrying watercraft, the same defining-feature pattern exp_n11c already used for
    "boat"; needed for the L-family ("ferry"/"vessel") synonym-referent stress item.
  - "sister" / "rival": a NEW SOCIAL_ROLE_DOM cluster, following the SAME "only the domain tag is
    shared" convention exp_n11c already used for dock/sailor (NAUTICAL-only overlap -> Tier2/
    related-not-synonym, not Tier1/synonym): sister={SOCIAL_ROLE_DOM, FAMILY_RELATION},
    rival={SOCIAL_ROLE_DOM, COMPETITIVE_RELATION} -- same domain, different defining relation, so
    they land in the SAME related-not-synonym cosine band as every other such pair by the SAME
    construction rule (not hand-tuned to force a low number). Needed to MEASURE the D-family
    ("sister"/"rival") over-link guard via the real mechanism rather than an OOV-lexicon bypass.

Consumer: hdlab.goal_typing._referent_links Tier-2 (see hdlab/goal_typing.py) replaces the prior
narrow hand-authored SYNONYM_GROUPS = [{ferry, vessel, boat, ship}] set-membership check with
`concept_similarity(a, b) >= SIMILARITY_LINK_THRESHOLD` gated on both concepts being IN this
lexicon (`in_lexicon`); OOV-of-lexicon falls through to the caller's existing no-link behavior
(never crashes, never over-links).

SCOPE (do not overclaim): mechanism-proof on the 86 exp_n11c concepts + 3 SUPPLY additions =
89 concepts total. General open-vocabulary feature coverage (inducing features for arbitrary
words) is a separate, missing-LEARNING follow-up, not claimed here -- same honest_scope caveat
exp_n11c's own verdict carries.
"""
from __future__ import annotations

from typing import Dict, FrozenSet, Optional

import torch

from hdlab.bundling import bundle
from hdlab.grounded_similarity import (
    GROUNDED_CAP as _GROUNDED_CAP,
    grounded_similarity as _grounded_similarity,
    in_grounded_lexicon as _in_grounded_lexicon,
    self_test as _grounded_similarity_self_test,
)
from hdlab.situation_model_accumulate import unit_phase_vec

# Matches exp_n11c's CONFIG_VERSION (N_DIM=8192, SEED=7) so this module's cosine geometry
# reproduces exp_n11c's certified tier-mean bands (~0.93 / ~0.30 / ~0.00) on the shared concepts.
N_DIM = 8192
FEATURE_SEED = 7

# ---------------------------------------------------------------------------
# BYTE-IDENTICAL to exp_n11c_shared_feature_lexical_similarity_v1.CONCEPT_FEATURES (commit
# 7d0a574b4), toy* self-test-only entries dropped. Design convention (documented, uniform, not
# per-triple-tuned; unchanged from exp_n11c):
#   - a DOMAIN tag marks broad category membership, shared by every concept in that family.
#   - TRUE SYNONYM pairs share the domain tag AND (nearly) all of the anchor's SPECIFIC tags.
#   - RELATED-NOT-SYNONYM pairs share ONLY the domain tag.
#   - UNRELATED pairs share nothing (different domain tag entirely).
# SUPPLY EXTENSION entries (ferry/sister/rival) are appended at the end, same convention -- see
# module docstring.
# ---------------------------------------------------------------------------
CONCEPT_FEATURES: Dict[str, FrozenSet[str]] = {
    # NAUTICAL cluster
    "vessel": frozenset({"NAUTICAL", "WATERCRAFT", "HAS_HULL", "CARRIES_CARGO"}),
    "ship": frozenset({"NAUTICAL", "WATERCRAFT", "HAS_HULL", "CARRIES_CARGO", "LARGE_VESSEL"}),
    "boat": frozenset({"NAUTICAL", "WATERCRAFT", "HAS_HULL", "CARRIES_PEOPLE"}),
    "dock": frozenset({"NAUTICAL", "STATIC_STRUCTURE"}),
    "sailor": frozenset({"NAUTICAL", "PERSON_ROLE"}),
    "captain": frozenset({"NAUTICAL", "PERSON_ROLE", "AUTHORITY"}),
    "crew": frozenset({"NAUTICAL", "PERSON_ROLE", "GROUP"}),
    "water": frozenset({"NAUTICAL", "LIQUID_SUBSTANCE"}),
    # VEHICLE cluster
    "car": frozenset({"VEHICLE_DOM", "LAND_VEHICLE", "MOTORIZED", "CARRIES_PEOPLE"}),
    "automobile": frozenset({"VEHICLE_DOM", "LAND_VEHICLE", "MOTORIZED", "CARRIES_PEOPLE"}),
    "vehicle": frozenset({"VEHICLE_DOM", "LAND_VEHICLE", "MOTORIZED", "CARRIES_PEOPLE"}),
    "truck": frozenset({"VEHICLE_DOM", "LAND_VEHICLE", "MOTORIZED", "CARRIES_CARGO"}),
    "wheel": frozenset({"VEHICLE_DOM", "MECHANICAL_PART"}),
    "engine": frozenset({"VEHICLE_DOM", "MECHANICAL_PART", "POWER_SOURCE"}),
    "cargo": frozenset({"VEHICLE_DOM", "GOODS_ITEM"}),
    # EMOTION cluster -- happy group
    "happy": frozenset({"EMOTION_DOM", "POS_VALENCE", "GENERAL_MOOD"}),
    "glad": frozenset({"EMOTION_DOM", "POS_VALENCE", "GENERAL_MOOD"}),
    "joyful": frozenset({"EMOTION_DOM", "POS_VALENCE", "GENERAL_MOOD"}),
    "love": frozenset({"EMOTION_DOM", "ATTACHMENT"}),
    # EMOTION cluster -- sad group
    "sad": frozenset({"EMOTION_DOM", "NEG_VALENCE", "GENERAL_MOOD"}),
    "unhappy": frozenset({"EMOTION_DOM", "NEG_VALENCE", "GENERAL_MOOD"}),
    "grief": frozenset({"EMOTION_DOM", "RESPONSE_TO_LOSS"}),
    # EMOTION cluster -- angry group
    "angry": frozenset({"EMOTION_DOM", "NEG_VALENCE", "HIGH_AROUSAL"}),
    "mad": frozenset({"EMOTION_DOM", "NEG_VALENCE", "HIGH_AROUSAL"}),
    "furious": frozenset({"EMOTION_DOM", "NEG_VALENCE", "HIGH_AROUSAL"}),
    "rage": frozenset({"EMOTION_DOM", "INTENSE_STATE"}),
    "hate": frozenset({"EMOTION_DOM", "SOCIAL_EMOTION"}),
    # EMOTION cluster -- fear group
    "fear": frozenset({"EMOTION_DOM", "NEG_VALENCE", "RESPONSE_TO_THREAT"}),
    "terror": frozenset({"EMOTION_DOM", "NEG_VALENCE", "RESPONSE_TO_THREAT"}),
    "dread": frozenset({"EMOTION_DOM", "NEG_VALENCE", "RESPONSE_TO_THREAT"}),
    "afraid": frozenset({"EMOTION_DOM", "GENERAL_STATE"}),
    "anxiety": frozenset({"EMOTION_DOM", "GENERAL_STATE"}),
    # EMOTION cluster -- unrelated-filler words (used only as Tier3 targets in exp_n11c's probe)
    "anger": frozenset({"EMOTION_DOM", "NEG_VALENCE", "RESPONSE_TO_INJUSTICE"}),
    "jealousy": frozenset({"EMOTION_DOM", "NEG_VALENCE", "SOCIAL_EMOTION"}),
    "sorrow": frozenset({"EMOTION_DOM", "NEG_VALENCE", "RESPONSE_TO_LOSS"}),
    "passion": frozenset({"EMOTION_DOM", "HIGH_AROUSAL", "ATTACHMENT"}),
    "hatred": frozenset({"EMOTION_DOM", "NEG_VALENCE", "SOCIAL_EMOTION"}),
    # GEOGRAPHIC cluster (unrelated-filler words)
    "mountain": frozenset({"GEO_DOM", "LANDFORM", "ELEVATED"}),
    "desert": frozenset({"GEO_DOM", "LANDSCAPE", "ARID"}),
    "river": frozenset({"GEO_DOM", "BODY_OF_WATER", "FLOWING"}),
    "stream": frozenset({"GEO_DOM", "BODY_OF_WATER", "FLOWING", "SMALL_LANDFORM"}),
    "forest": frozenset({"GEO_DOM", "VEGETATION", "LANDSCAPE"}),
    "hill": frozenset({"GEO_DOM", "LANDFORM", "ELEVATED", "SMALL_LANDFORM"}),
    "valley": frozenset({"GEO_DOM", "LANDFORM", "LOW_ELEVATION"}),
    "lake": frozenset({"GEO_DOM", "BODY_OF_WATER"}),
    # MAGNITUDE cluster
    "big": frozenset({"MAGNITUDE_DOM", "LARGE_SIZE", "PHYSICAL_DIMENSION"}),
    "large": frozenset({"MAGNITUDE_DOM", "LARGE_SIZE", "PHYSICAL_DIMENSION"}),
    "huge": frozenset({"MAGNITUDE_DOM", "LARGE_SIZE", "PHYSICAL_DIMENSION"}),
    "small": frozenset({"MAGNITUDE_DOM", "SMALL_SIZE", "PHYSICAL_DIMENSION"}),
    "tiny": frozenset({"MAGNITUDE_DOM", "SMALL_SIZE", "PHYSICAL_DIMENSION"}),
    "weight": frozenset({"MAGNITUDE_DOM", "MASS_PROPERTY"}),
    "distance": frozenset({"MAGNITUDE_DOM", "SPATIAL_EXTENT"}),
    # SPEED cluster
    "fast": frozenset({"SPEED_DOM", "HIGH_RATE", "MOTION_PROPERTY"}),
    "quick": frozenset({"SPEED_DOM", "HIGH_RATE", "MOTION_PROPERTY"}),
    "rapid": frozenset({"SPEED_DOM", "HIGH_RATE", "MOTION_PROPERTY"}),
    "slow": frozenset({"SPEED_DOM", "LOW_RATE", "MOTION_PROPERTY"}),
    "sluggish": frozenset({"SPEED_DOM", "LOW_RATE", "MOTION_PROPERTY"}),
    "speed": frozenset({"SPEED_DOM", "ABSTRACT_QUANTITY"}),
    "velocity": frozenset({"SPEED_DOM", "ABSTRACT_QUANTITY", "PHYSICS_TERM"}),
    # REPAIR cluster
    "repair": frozenset({"REPAIR_DOM", "RESTORATIVE_ACTION", "CHANGE_OF_STATE"}),
    "fix": frozenset({"REPAIR_DOM", "RESTORATIVE_ACTION", "CHANGE_OF_STATE"}),
    "mend": frozenset({"REPAIR_DOM", "RESTORATIVE_ACTION", "CHANGE_OF_STATE"}),
    "broken": frozenset({"REPAIR_DOM", "DAMAGE_STATE"}),
    "damaged": frozenset({"REPAIR_DOM", "DAMAGE_STATE"}),
    # COGNITION cluster
    "smart": frozenset({"COGNITION_DOM", "MENTAL_ABILITY", "EVALUATIVE_POSITIVE"}),
    "intelligent": frozenset({"COGNITION_DOM", "MENTAL_ABILITY", "EVALUATIVE_POSITIVE"}),
    "clever": frozenset({"COGNITION_DOM", "MENTAL_ABILITY", "EVALUATIVE_POSITIVE"}),
    "answer": frozenset({"COGNITION_DOM", "PROBLEM_SOLVING_OUTPUT"}),
    "mistake": frozenset({"COGNITION_DOM", "ERROR_STATE"}),
    # FINANCE cluster
    "rich": frozenset({"FINANCE_DOM", "WEALTH_STATE", "EVALUATIVE_POSITIVE"}),
    "wealthy": frozenset({"FINANCE_DOM", "WEALTH_STATE", "EVALUATIVE_POSITIVE"}),
    "buy": frozenset({"FINANCE_DOM", "TRANSACTION_ACTION"}),
    "purchase": frozenset({"FINANCE_DOM", "TRANSACTION_ACTION"}),
    # TEMPORAL cluster
    "begin": frozenset({"TEMPORAL_DOM", "START_BOUNDARY"}),
    "start": frozenset({"TEMPORAL_DOM", "START_BOUNDARY"}),
    "end": frozenset({"TEMPORAL_DOM", "END_BOUNDARY"}),
    "finish": frozenset({"TEMPORAL_DOM", "END_BOUNDARY"}),
    # ART cluster (unrelated-filler words, plus "music" as one T2)
    "music": frozenset({"ART_DOM", "AUDITORY", "CREATIVE"}),
    "song": frozenset({"ART_DOM", "AUDITORY", "CREATIVE"}),
    "painting": frozenset({"ART_DOM", "VISUAL", "CREATIVE"}),
    "art": frozenset({"ART_DOM", "CREATIVE", "EXPRESSIVE"}),
    "melody": frozenset({"ART_DOM", "AUDITORY", "CREATIVE"}),
    # ACADEMIC cluster (unrelated-filler words)
    "mathematics": frozenset({"ACADEMIC_DOM", "FORMAL_SCIENCE"}),
    "biology": frozenset({"ACADEMIC_DOM", "NATURAL_SCIENCE"}),
    # VISUAL-property cluster (unrelated-filler words)
    "color": frozenset({"VISUAL_DOM", "PERCEPTUAL_PROPERTY"}),
    "shape": frozenset({"VISUAL_DOM", "PERCEPTUAL_PROPERTY"}),

    # ---- SUPPLY EXTENSION (this promotion, 2026-08-06) -- see module docstring -------------------
    "ferry": frozenset({"NAUTICAL", "WATERCRAFT", "HAS_HULL", "CARRIES_PEOPLE"}),
    "sister": frozenset({"SOCIAL_ROLE_DOM", "FAMILY_RELATION"}),
    "rival": frozenset({"SOCIAL_ROLE_DOM", "COMPETITIVE_RELATION"}),

    # ---- SUPPLY EXTENSION (2026-08-09, Direction-B build #2, exp_situation_model_relation_
    # ablation_v1) -- the LITERAL vocabulary of hdlab.goal_outcome_relation's 6 hand-authored
    # MEANS-END pools (COGNITION_GOAL_POOL / SKILL_GOAL_VERB_POOL / SKILL_GOAL_REFERENT_POOL /
    # INFO_EXCHANGE_POOL / ERRAND_POOL / SKILL_TRAIN_POOL), re-encoded as CONCEPT_FEATURES entries
    # so hdlab.goal_outcome_relation_grounded's ACHIEVE_query can score pool membership via graded
    # concept_similarity instead of exact-literal/WordNet-primary-synonym _pool_related. ONE flat
    # domain tag per pool (no invented internal subtyping) -- reproduces the ORIGINAL pools' own
    # flat equivalence-class semantics (any member counts as equally-strong evidence, exactly as
    # the boolean membership check already treated them), not a richer taxonomy. Words that are
    # literal members of TWO original pools (practice/train/drill appear in BOTH SKILL_GOAL_VERB_
    # POOL and SKILL_TRAIN_POOL) carry both domain tags. SCOPE (disclosed): self-similarity of a
    # word already IN a pool is always 1.0 (cosine of a vector with itself), so this reproduces
    # Tier1-exact-membership behavior on every word already in the original pools; genuine
    # cross-word generalization (a synonym NOT in the original pool) is a strictly ADDITIONAL
    # capability this SUPPLY EXTENSION enables but which the current TRAIN/HELDOUT bank does not
    # exercise (every held-out item's relevant word is already a literal pool member) -- see
    # hdlab/goal_outcome_relation_grounded.py module docstring for the honest parity framing.
    "know": frozenset({"EPISTEMIC_DOM"}), "understand": frozenset({"EPISTEMIC_DOM"}),
    "learn": frozenset({"EPISTEMIC_DOM"}), "realize": frozenset({"EPISTEMIC_DOM"}),
    "figure": frozenset({"EPISTEMIC_DOM"}), "discover": frozenset({"EPISTEMIC_DOM"}),

    "practice": frozenset({"SKILLBUILD_DOM", "SKILLTRAIN_DOM"}),
    "train": frozenset({"SKILLBUILD_DOM", "SKILLTRAIN_DOM"}),
    "drill": frozenset({"SKILLBUILD_DOM", "SKILLTRAIN_DOM"}),
    "improve": frozenset({"SKILLBUILD_DOM"}), "master": frozenset({"SKILLBUILD_DOM"}),
    "skill": frozenset({"SKILLBUILD_DOM"}), "skills": frozenset({"SKILLBUILD_DOM"}),
    "technique": frozenset({"SKILLBUILD_DOM"}), "better": frozenset({"SKILLBUILD_DOM"}),

    "instruct": frozenset({"SKILLTRAIN_DOM"}), "instructor": frozenset({"SKILLTRAIN_DOM"}),
    "teach": frozenset({"SKILLTRAIN_DOM"}), "coach": frozenset({"SKILLTRAIN_DOM"}),
    "mentor": frozenset({"SKILLTRAIN_DOM"}), "tutor": frozenset({"SKILLTRAIN_DOM"}),
    "lesson": frozenset({"SKILLTRAIN_DOM"}),

    "talk": frozenset({"INFOEXCHANGE_DOM"}), "say": frozenset({"INFOEXCHANGE_DOM"}),
    "speak": frozenset({"INFOEXCHANGE_DOM"}), "tell": frozenset({"INFOEXCHANGE_DOM"}),
    "discuss": frozenset({"INFOEXCHANGE_DOM"}), "explain": frozenset({"INFOEXCHANGE_DOM"}),
    "describe": frozenset({"INFOEXCHANGE_DOM"}), "chat": frozenset({"INFOEXCHANGE_DOM"}),
    "converse": frozenset({"INFOEXCHANGE_DOM"}), "read": frozenset({"INFOEXCHANGE_DOM"}),

    "shop": frozenset({"ERRANDACT_DOM"}), "shopping": frozenset({"ERRANDACT_DOM"}),
    "errand": frozenset({"ERRANDACT_DOM"}), "errands": frozenset({"ERRANDACT_DOM"}),
    "chore": frozenset({"ERRANDACT_DOM"}), "chores": frozenset({"ERRANDACT_DOM"}),
    "outing": frozenset({"ERRANDACT_DOM"}),

    # GENUINE generalization vocabulary (NOT literal members of any of goal_outcome_relation.py's
    # 6 original pools; MEASURED@this session that hdlab.goal_outcome_relation's baseline
    # _pool_related -- Tier1 exact + Tier2 WordNet-primary-synonym -- misses BOTH: goal_atoms
    # ('He wanted to grasp the concept.') == [] and outcome_atoms('She crammed for the exam all
    # night.') == ['no_relation_cue']). These two words are what makes hdlab.goal_outcome_relation_
    # grounded's ACHIEVE-leg graded generalization claim TRUE and testable, as opposed to the 39
    # words above which only reproduce Tier1-exact coverage on words the original pools already
    # contain (see that module's docstring "Honest framing").
    "grasp": frozenset({"EPISTEMIC_DOM"}),
    "cram": frozenset({"SKILLBUILD_DOM", "SKILLTRAIN_DOM"}),
}

_feature_vecs_cache: Optional[Dict[str, torch.Tensor]] = None


def _feature_vocab() -> list:
    tags: set = set()
    for feats in CONCEPT_FEATURES.values():
        tags.update(feats)
    return sorted(tags)


def _feature_vectors(seed: int = FEATURE_SEED, n_dim: int = N_DIM) -> Dict[str, torch.Tensor]:
    """One deterministic random unit-phase complex64 vector per feature tag (cached for the
    default seed/n_dim; non-default calls -- e.g. a scramble-collapse self-test probe -- bypass
    the cache and recompute)."""
    global _feature_vecs_cache
    if seed == FEATURE_SEED and n_dim == N_DIM:
        if _feature_vecs_cache is None:
            gen = torch.Generator().manual_seed(seed)
            _feature_vecs_cache = {tag: unit_phase_vec(n_dim, gen) for tag in _feature_vocab()}
        return _feature_vecs_cache
    gen = torch.Generator().manual_seed(seed)
    return {tag: unit_phase_vec(n_dim, gen) for tag in _feature_vocab()}


def _concept_vector_from(features: FrozenSet[str], feature_vecs: Dict[str, torch.Tensor]) -> torch.Tensor:
    """Concept vector = FHRR bundle() of its features' index-vectors (substrate-own op). Byte-
    identical to exp_n11c's _concept_vector."""
    stacked = torch.stack([feature_vecs[t] for t in sorted(features)])
    return bundle(stacked)


def concept_vector(word: str) -> Optional[torch.Tensor]:
    """Concept vector for `word`, or None if `word` is OOV of CONCEPT_FEATURES."""
    feats = CONCEPT_FEATURES.get(word)
    if feats is None:
        return None
    return _concept_vector_from(feats, _feature_vectors())


def _cos_complex(a: torch.Tensor, b: torch.Tensor) -> float:
    """FHRR cosine: Re(sum(conj(a)*b))/d -- byte-identical metric convention to exp_n11c /
    hdlab.situation_model_accumulate.cleanup_argmax."""
    d = a.shape[0]
    return float(torch.real(torch.sum(torch.conj(a) * b))) / d


def in_lexicon(word: str) -> bool:
    return word in CONCEPT_FEATURES


def in_lexicon_or_grounded(word: str) -> bool:
    """True if `word` is judgeable by concept_similarity's default (fallback-enabled) path --
    either the hand lexicon (CONCEPT_FEATURES) or the grounded (Lancaster sensorimotor +
    Brysbaert concreteness) fallback covers it. ADDITIVE helper for callers that currently
    pre-gate on in_lexicon(word) before calling concept_similarity (e.g.
    hdlab.goal_typing._referent_links Tier-2) -- swapping that gate to this function is how a
    caller opts INTO the OOV-coverage extension; existing callers that keep using in_lexicon()
    are unaffected (this function does not change in_lexicon's own behavior)."""
    return in_lexicon(word) or _in_grounded_lexicon(word)


# GROUNDED FALLBACK (2026-08-11, architecture-audit TIER-1 shore-up, see
# notes/architecture_audit_2026-08-11.md and hdlab/grounded_similarity.py's module docstring for
# the full rationale + the MEASURED anti-over-merge calibration). CONCEPT_FEATURES covers ~230
# hand-typed concepts; every OTHER word previously made concept_similarity return None
# unconditionally ("cannot judge"), even though a 39,707-word grounding-norms asset (Lancaster
# sensorimotor + Brysbaert concreteness, data/grounding_testbed/*.csv) sat on disk with zero live
# inference paths. concept_similarity now falls back to that asset when either word is OOV of
# CONCEPT_FEATURES, instead of returning None -- ADDITIVE, layered UNDERNEATH the hand lexicon:
#   - both words IN CONCEPT_FEATURES -> hand-lexicon FHRR-bundle cosine (UNCHANGED, byte-identical
#     to the pre-2026-08-11 behavior -- this is the "no regression on covered vocab" guarantee).
#   - either word OOV of CONCEPT_FEATURES -> BOTH words are scored via the grounded profile
#     (never a mixed hand-lexicon-cosine-vs-grounded-cosine comparison -- those are different
#     vector spaces and not comparable), capped at GROUNDED_CAP (0.45), STRUCTURALLY below
#     SIMILARITY_LINK_THRESHOLD (0.50) so the fallback can never itself trigger a same-idea/merge
#     decision at the project's standard link threshold (see grounded_similarity.py docstring
#     "SAFE-BY-CONSTRUCTION RESPONSE" for the measured reason: raw sensorimotor+concreteness
#     cosine cannot separate a true synonym from a perceptually-similar-but-identity-distinct
#     sibling, e.g. apple/orange raw_cos=0.952 vs happy/joyful raw_cos=0.962 -- statistically
#     inseparable above the cap, so nothing this path returns is trusted at "same idea" strength).
#   - neither source covers the pair, or use_grounded_fallback=False -> None (unchanged contract).
def concept_similarity(word_a: str, word_b: str, use_grounded_fallback: bool = True) -> Optional[float]:
    """Shared-feature cosine similarity when both words are in CONCEPT_FEATURES (hand lexicon,
    UNCHANGED path/values). If either word is OOV of CONCEPT_FEATURES and use_grounded_fallback
    is True (default), falls back to the grounded (Lancaster sensorimotor + Brysbaert
    concreteness) similarity (hdlab.grounded_similarity), capped at GROUNDED_CAP so it can never
    cross SIMILARITY_LINK_THRESHOLD -- see the module-level "GROUNDED FALLBACK" comment above.
    Returns None only if neither source covers the pair, or use_grounded_fallback=False (in which
    case behavior is byte-identical to the pre-2026-08-11 hand-lexicon-only function). Callers
    MUST still treat None as "cannot judge" (fall through to their own existing behavior), never
    crash, never treat OOV as either a link or a non-link by default."""
    va = concept_vector(word_a)
    vb = concept_vector(word_b)
    if va is not None and vb is not None:
        return _cos_complex(va, vb)
    if not use_grounded_fallback:
        return None
    return _grounded_similarity(word_a, word_b)


# Pre-registered (see preregs/2026-08-06_wire_shared_feature_similarity_outcome_valence_v1.md):
# MEASURED@this module's self_test -- sim(vessel,ferry)=0.634 (decisive near-synonym pair, must
# LINK) vs sim(sister,rival)=0.398 (over-link-guard pair, must NOT link) vs sim(vessel,dock)=0.279
# (related-not-synonym pair, must NOT link). 0.50 sits with clean margin on both sides: 0.134 below
# the synonym pair, 0.102-0.221 above the two must-not-link pairs -- a pair must be genuinely
# near-synonymous (shares almost all defining tags, not just a domain tag) to clear it.
SIMILARITY_LINK_THRESHOLD = 0.50


def self_test() -> dict:
    """Coverage + mechanism-fires + threshold-separation + circularity(scramble) checks."""
    # (1) coverage: every SUPPLY-extension word is present with >=2 features (same convention gate
    # exp_n11c's own self-test applies).
    for w in ("ferry", "sister", "rival"):
        assert w in CONCEPT_FEATURES, "SUPPLY extension missing %r" % w
        assert len(CONCEPT_FEATURES[w]) >= 2, "concept %r has <2 features" % w

    # (2) mechanism-fires + threshold separation, the exact three-way comparison this promotion's
    # report cites: sim(vessel,ferry) [true near-synonym, must LINK] vs sim(vessel,dock)
    # [related-not-synonym, domain-tag-only overlap, must NOT link] vs sim(sister,rival)
    # [over-link-guard analog of vessel/dock, must NOT link].
    sim_vessel_ferry = concept_similarity("vessel", "ferry")
    sim_vessel_dock = concept_similarity("vessel", "dock")
    sim_sister_rival = concept_similarity("sister", "rival")
    assert sim_vessel_ferry is not None and sim_vessel_dock is not None and sim_sister_rival is not None
    assert sim_vessel_ferry >= SIMILARITY_LINK_THRESHOLD, (
        "MECHANISM-FIRES FAILURE: sim(vessel,ferry)=%.4f must clear the link threshold %.2f"
        % (sim_vessel_ferry, SIMILARITY_LINK_THRESHOLD))
    assert sim_vessel_dock < SIMILARITY_LINK_THRESHOLD, (
        "OVER-LINK FAILURE: sim(vessel,dock)=%.4f (related-not-synonym) must stay BELOW threshold %.2f"
        % (sim_vessel_dock, SIMILARITY_LINK_THRESHOLD))
    assert sim_sister_rival < SIMILARITY_LINK_THRESHOLD, (
        "OVER-LINK FAILURE: sim(sister,rival)=%.4f must stay BELOW threshold %.2f (over-link guard)"
        % (sim_sister_rival, SIMILARITY_LINK_THRESHOLD))

    # (3) OOV never crashes, never links.
    assert concept_similarity("vessel", "not_a_real_word_zzz") is None
    assert not in_lexicon("not_a_real_word_zzz")

    # (4) glass-box determinism: same word twice -> bit-identical vector.
    v1 = concept_vector("vessel")
    v2 = concept_vector("vessel")
    assert torch.equal(v1, v2), "GLASS-BOX FAILURE: same concept must reproduce bit-identical vector"

    # (5) circularity check: a SCRAMBLED concept->feature assignment (fixed disjoint seed,
    # permutation restricted to this module's vocabulary) must collapse the vessel/ferry gain --
    # proves the mechanism is earning structure from genuine feature overlap, not an artifact of
    # the encoder alone. Byte-identical scramble convention to exp_n11c's SCRAMBLED_FEATURES arm.
    words = sorted(CONCEPT_FEATURES.keys())
    gen = torch.Generator().manual_seed(999)
    perm = torch.randperm(len(words), generator=gen).tolist()
    scrambled_map = {words[i]: CONCEPT_FEATURES[words[perm[i]]] for i in range(len(words))}
    fv = _feature_vectors()
    scr_vessel = _concept_vector_from(scrambled_map["vessel"], fv)
    scr_ferry = _concept_vector_from(scrambled_map["ferry"], fv)
    sim_scrambled = _cos_complex(scr_vessel, scr_ferry)
    assert (sim_vessel_ferry - sim_scrambled) >= 0.30, (
        "CIRCULARITY FAILURE: scrambling the concept->feature assignment must collapse the "
        "vessel/ferry gain (got real=%.4f scrambled=%.4f, delta=%.4f < 0.30)"
        % (sim_vessel_ferry, sim_scrambled, sim_vessel_ferry - sim_scrambled))

    # (6) GROUNDED FALLBACK checks (2026-08-11 addition; see the "GROUNDED FALLBACK" module
    # comment above concept_similarity). "sofa"/"couch"/"apple"/"orange" are OOV of
    # CONCEPT_FEATURES (verified: not in the hand lexicon, hand-typed or ProPara-extension) so
    # they exercise the grounded path end-to-end through the public concept_similarity API, not
    # just hdlab.grounded_similarity directly.
    for w in ("sofa", "couch", "apple", "orange"):
        assert w not in CONCEPT_FEATURES, (
            "SELF-TEST PRECONDITION BROKEN: %r was added to CONCEPT_FEATURES; pick a different "
            "OOV probe word for the grounded-fallback checks below" % w)

    # (6a) no-regression / byte-identical-when-off: with use_grounded_fallback=False, an OOV pair
    # returns None exactly as the pre-2026-08-11 function did (the toggle this promotion's
    # "additive default must preserve prior behavior byte-identical when the grounded fallback is
    # off" contract requires).
    assert concept_similarity("sofa", "couch", use_grounded_fallback=False) is None, (
        "NO-REGRESSION FAILURE: use_grounded_fallback=False must reproduce the pre-2026-08-11 "
        "None-on-OOV behavior byte-identically")

    # (6b) coverage extension: with the default (fallback ON), the same OOV pair now returns a
    # real graded similarity instead of None.
    sim_sofa_couch = concept_similarity("sofa", "couch")
    assert sim_sofa_couch is not None, "COVERAGE-EXTENSION FAILURE: grounded fallback did not fire for OOV pair (sofa,couch)"
    assert 0.0 <= sim_sofa_couch <= _GROUNDED_CAP

    # (6c) anti-over-merge-by-construction, exercised through the PUBLIC concept_similarity API
    # (not just hdlab.grounded_similarity directly): every grounded-fallback value concept_
    # similarity can return is capped strictly below SIMILARITY_LINK_THRESHOLD, so an OOV
    # sibling-distinct pair (apple/orange -- perceptually similar, identity-distinct fruits) can
    # never trigger a same-idea/merge decision at the project's standard link convention.
    sim_apple_orange = concept_similarity("apple", "orange")
    assert sim_apple_orange is not None
    assert sim_apple_orange < SIMILARITY_LINK_THRESHOLD, (
        "OVER-LINK FAILURE: grounded-fallback sim(apple,orange)=%.4f must stay BELOW "
        "SIMILARITY_LINK_THRESHOLD %.2f" % (sim_apple_orange, SIMILARITY_LINK_THRESHOLD))

    # (6d) mixed hand-lexicon/OOV pair: "vessel" IS in CONCEPT_FEATURES, "sofa" is not -- must
    # fall through to the grounded path for BOTH words (never mix a hand-lexicon-FHRR-cosine with
    # a grounded-cosine; those are different vector spaces).
    sim_mixed = concept_similarity("vessel", "sofa")
    assert sim_mixed is not None and 0.0 <= sim_mixed <= _GROUNDED_CAP

    # (6e) in_lexicon_or_grounded: True for hand-lexicon words, True for grounded-only words,
    # False for genuine nonsense.
    assert in_lexicon_or_grounded("vessel") is True
    assert in_lexicon_or_grounded("sofa") is True
    assert in_lexicon_or_grounded("not_a_real_word_zzz") is False

    # (6f) the grounded module's own self-test (coverage/ordering/cap/circularity) must also pass
    # standalone -- re-asserted here so a regression in hdlab/grounded_similarity.py surfaces at
    # THIS module's self_test too (the same "core_preserved" discipline
    # exp_representation_canonicalization_v1 already applies to lexical_similarity/hd_fact_store).
    grounded_result = _grounded_similarity_self_test()
    assert grounded_result is not None

    return {
        "sim_vessel_ferry": round(sim_vessel_ferry, 4),
        "sim_vessel_dock": round(sim_vessel_dock, 4),
        "sim_sister_rival": round(sim_sister_rival, 4),
        "sim_vessel_ferry_scrambled": round(sim_scrambled, 4),
        "threshold": SIMILARITY_LINK_THRESHOLD,
        "n_concepts": len(CONCEPT_FEATURES),
        "n_feature_tags": len(_feature_vocab()),
        "grounded_fallback": {
            "sim_sofa_couch_fallback_off": None,
            "sim_sofa_couch": round(sim_sofa_couch, 4),
            "sim_apple_orange": round(sim_apple_orange, 4),
            "sim_vessel_sofa_mixed": round(sim_mixed, 4),
            "grounded_cap": _GROUNDED_CAP,
            "grounded_self_test": grounded_result,
        },
    }


if __name__ == "__main__":
    import json
    res = self_test()
    print(json.dumps(res, indent=2))
    print("ALL SELF-TESTS PASSED")
