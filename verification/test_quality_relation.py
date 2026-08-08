"""Verification: hdlab.quality_relation two-channel opposition/relation detector -- reproduces
the two proven scratchpad mechanisms (WordNet G1 dominant-synset antonym guard; FPE signed
dimensional axis, HARD-PASS 15/15) as assertions on the wired module. Scaffold-free, passes with
tracing=False (no tracing dependency at all)."""
from __future__ import annotations

from hdlab.lexical_similarity import concept_similarity
from hdlab.quality_relation import OPP_THRESH, SAME_THRESH, quality_relation


# ---------------------------------------------------------------------------------------------
# (1) Channel B -- FPE signed dimensional axis (fpe_quality_axis_proof.py, HARD-PASS 15/15)
# ---------------------------------------------------------------------------------------------
def test_fpe_opposed_pairs_clear_threshold() -> None:
    for a, b in [("dense", "airy"), ("matte", "glossy"), ("energetic", "calm"), ("humorous", "solemn")]:
        r = quality_relation(a, b)
        assert r["verdict"] == "opposed", (a, b, r)
        assert r["channel"] == "fpe_axis", (a, b, r)
        assert r["evidence"]["cosine"] <= OPP_THRESH, (a, b, r)


def test_fpe_same_pairs_clear_threshold() -> None:
    for a, b in [("dense", "thick"), ("humorous", "funny")]:
        r = quality_relation(a, b)
        assert r["verdict"] == "same", (a, b, r)
        assert r["channel"] == "fpe_axis", (a, b, r)
        assert r["evidence"]["cosine"] >= SAME_THRESH, (a, b, r)


def test_fpe_cross_axis_unrelated() -> None:
    r = quality_relation("dense", "humorous")
    assert r["verdict"] == "unrelated", r
    assert r["channel"] == "fpe_axis", r


# ---------------------------------------------------------------------------------------------
# (2) Channel A -- WordNet G1 dominant-synset antonym guard (adj_opposition_precision_sweep.py)
# ---------------------------------------------------------------------------------------------
def test_wordnet_canonical_antonyms_opposed() -> None:
    for a, b in [("hot", "cold"), ("big", "small"), ("tidy", "messy")]:
        r = quality_relation(a, b)
        assert r["verdict"] == "opposed", (a, b, r)
        assert r["channel"] == "wordnet_antonym", (a, b, r)


def test_big_large_not_opposed() -> None:
    r = quality_relation("big", "large")
    assert r["verdict"] != "opposed", r


def test_g1_precision_guard_adversarial_pairs() -> None:
    # G0 (unrestricted-all-synsets) false-positives on both of these; G1 (dominant-synset only,
    # the guard this module carries) must not -- the exact precision regression this consolidation
    # is built to hold.
    for a, b in [("big", "soft"), ("big", "immature")]:
        r = quality_relation(a, b)
        assert r["verdict"] != "opposed", (a, b, r)


# ---------------------------------------------------------------------------------------------
# (3) FLAT-cosine contrast -- documents WHY channel B (FPE signed axis) is needed at all: a plain
# bag-of-features cosine is bounded >=0 by construction and cannot encode signed opposition.
# ---------------------------------------------------------------------------------------------
def test_flat_cosine_cannot_encode_opposition_sign() -> None:
    sim = concept_similarity("big", "small")
    assert sim is not None
    assert sim >= 0.0, (
        "flat bag-of-features cosine is bounded >=0 by construction -- it cannot go negative even "
        "for a canonically opposed pair, which is exactly why channel B (FPE signed axis) exists"
    )


# ---------------------------------------------------------------------------------------------
# (4) determinism
# ---------------------------------------------------------------------------------------------
def test_determinism_same_seed_identical_verdicts() -> None:
    pairs = [("dense", "airy"), ("hot", "cold"), ("big", "large"), ("dense", "humorous")]
    run1 = [quality_relation(a, b, seed=3) for a, b in pairs]
    run2 = [quality_relation(a, b, seed=3) for a, b in pairs]
    assert run1 == run2


def test_oov_never_guesses() -> None:
    r = quality_relation("zzznotarealadjective", "alsofake")
    assert r["verdict"] is None
    assert r["channel"] is None
