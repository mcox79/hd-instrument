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


def concept_similarity(word_a: str, word_b: str) -> Optional[float]:
    """Shared-feature cosine similarity, or None if either word is OOV of CONCEPT_FEATURES --
    callers MUST treat None as "cannot judge" (fall through to their own existing behavior), never
    crash, never treat OOV as either a link or a non-link by default."""
    va = concept_vector(word_a)
    vb = concept_vector(word_b)
    if va is None or vb is None:
        return None
    return _cos_complex(va, vb)


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

    return {
        "sim_vessel_ferry": round(sim_vessel_ferry, 4),
        "sim_vessel_dock": round(sim_vessel_dock, 4),
        "sim_sister_rival": round(sim_sister_rival, 4),
        "sim_vessel_ferry_scrambled": round(sim_scrambled, 4),
        "threshold": SIMILARITY_LINK_THRESHOLD,
        "n_concepts": len(CONCEPT_FEATURES),
        "n_feature_tags": len(_feature_vocab()),
    }


if __name__ == "__main__":
    import json
    res = self_test()
    print(json.dumps(res, indent=2))
    print("ALL SELF-TESTS PASSED")
