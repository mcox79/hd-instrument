"""Verification: bigram_gap_measurement — bigram tighter than unigram; consistent baseline."""

from __future__ import annotations

import math

import numpy as np
import pytest

from hdlab.bigram_gap_measurement import (
    BASELINE_PROVENANCE,
    compute_bigram_gap,
    compute_unigram_top1,
    compute_word_bigram_top1,
)


def test_baseline_provenance_constant() -> None:
    """BASELINE_PROVENANCE marker is set; cross-cell comparisons can grep it."""
    assert isinstance(BASELINE_PROVENANCE, str)
    assert "empirical_conditional" in BASELINE_PROVENANCE


def test_unigram_argmax_on_skewed_corpus() -> None:
    """Unigram baseline picks most-frequent token; top1 matches its eval frequency."""
    v = 5
    train_ids = np.array([0] * 100 + [1] * 30 + [2] * 10 + [3] * 5 + [4] * 1)
    eval_targets = np.array([0, 0, 1, 0, 2, 0])  # 4/6 = 0.6667 are token 0
    out = compute_unigram_top1(train_ids, eval_targets, v)
    assert out["unigram_argmax_id"] == 0
    assert out["unigram_top1"] == pytest.approx(4.0 / 6.0)


def test_bigram_baseline_perfect_on_deterministic_chain() -> None:
    """When next-token is fully determined by prev, bigram baseline hits top1=1.0."""
    v = 5
    # Deterministic cycle 0 -> 1 -> 2 -> 3 -> 4 -> 0 -> ...
    train_ids = np.array([(i % v) for i in range(500)], dtype=np.int64)
    # Eval: same pattern (any t_prev unambiguously predicts (t_prev+1) % v).
    eval_cues = np.array([0, 1, 2, 3, 4], dtype=np.int64)
    eval_tgts = np.array([1, 2, 3, 4, 0], dtype=np.int64)
    out = compute_word_bigram_top1(train_ids, (eval_cues, eval_tgts), v)
    assert out["word_bigram_top1"] == pytest.approx(1.0)
    assert out["coverage"] == pytest.approx(1.0)
    assert out["n_eval"] == 5
    assert out["baseline_provenance"] == BASELINE_PROVENANCE


def test_bigram_tighter_than_unigram_on_structured_corpus() -> None:
    """On a corpus with bigram structure, bigram top1 > unigram top1."""
    v = 4
    rng = np.random.default_rng(0)
    n_train = 5000
    # Strong markov: P(curr | prev) puts 0.85 on (prev+1)%v, rest uniform.
    train = np.empty(n_train, dtype=np.int64)
    train[0] = 0
    for i in range(1, n_train):
        if rng.random() < 0.85:
            train[i] = (train[i - 1] + 1) % v
        else:
            train[i] = rng.integers(0, v)
    n_eval = 1000
    eval_arr = np.empty(n_eval, dtype=np.int64)
    eval_arr[0] = 0
    for i in range(1, n_eval):
        if rng.random() < 0.85:
            eval_arr[i] = (eval_arr[i - 1] + 1) % v
        else:
            eval_arr[i] = rng.integers(0, v)
    eval_cues = eval_arr[:-1]
    eval_tgts = eval_arr[1:]
    bigram_out = compute_word_bigram_top1(
        train, (eval_cues, eval_tgts), v
    )
    unigram_out = compute_unigram_top1(train, eval_tgts, v)
    # Bigram should be ~0.85; unigram should be ~0.25 (each token roughly equally likely).
    assert bigram_out["word_bigram_top1"] > unigram_out["unigram_top1"] + 0.30
    assert bigram_out["word_bigram_top1"] > 0.70


def test_unigram_floor_matches_uniform_for_uniform_corpus() -> None:
    """For ~uniform corpus, unigram top1 ~ 1/V (the entropy-floor analog for top1)."""
    v = 10
    rng = np.random.default_rng(0)
    train = rng.integers(0, v, size=10_000)
    eval_tgts = rng.integers(0, v, size=1000)
    out = compute_unigram_top1(train, eval_tgts, v)
    assert out["unigram_top1"] == pytest.approx(1.0 / v, abs=0.04)


def test_backoff_to_unigram_on_unseen_prev() -> None:
    """Unseen t_prev backs off to unigram-argmax; coverage reflects backoff fraction."""
    v = 5
    train = np.array([0, 1, 0, 1, 0, 1, 0, 1], dtype=np.int64)  # only prev=0 and 1 seen
    eval_cues = np.array([0, 1, 4], dtype=np.int64)  # 4 never seen as prev
    eval_tgts = np.array([1, 0, 0], dtype=np.int64)
    out = compute_word_bigram_top1(train, (eval_cues, eval_tgts), v)
    # prev=4 falls back to unigram-argmax. Unigram counts: 0:4 1:4. argmax=0.
    # So pred for cue 4 = 0 (matches target 0).
    assert out["coverage"] == pytest.approx(2.0 / 3.0)
    assert out["unigram_argmax_id"] == 0


def test_bigram_gap_positive_when_substrate_above_bigram() -> None:
    """gap > 0 when substrate top1 > bigram top1; convention sign-preserving."""
    v = 4
    rng = np.random.default_rng(1)
    train = np.empty(2000, dtype=np.int64)
    train[0] = 0
    for i in range(1, 2000):
        train[i] = (train[i - 1] + 1) % v if rng.random() < 0.6 else rng.integers(0, v)
    eval_cues = train[:-1]
    eval_tgts = train[1:]
    # Substrate hypothetically scored 0.80 top1.
    out = compute_bigram_gap(0.80, train, (eval_cues, eval_tgts), v)
    assert "bigram_gap" in out
    assert out["bigram_gap"] == pytest.approx(
        0.80 - out["word_bigram_top1"]
    )
    assert out["substrate_top1"] == pytest.approx(0.80)


def test_bigram_gap_negative_when_substrate_below_bigram() -> None:
    """gap < 0 when substrate is worse than bigram baseline (chain-grade red-flag)."""
    v = 4
    train = np.array([0, 1, 2, 3] * 200, dtype=np.int64)  # perfectly cyclic
    eval_cues = np.array([0, 1, 2, 3], dtype=np.int64)
    eval_tgts = np.array([1, 2, 3, 0], dtype=np.int64)
    out = compute_bigram_gap(0.30, train, (eval_cues, eval_tgts), v)
    # Bigram on a perfectly cyclic stream -> 1.0; substrate at 0.30 -> negative gap.
    assert out["bigram_gap"] < 0.0
    assert out["bigram_gap"] == pytest.approx(0.30 - 1.0)


def test_substrate_top1_range_validation() -> None:
    """substrate_top1 outside [0, 1] raises ValueError."""
    train = np.array([0, 1, 2, 0, 1, 2], dtype=np.int64)
    pairs = (np.array([0, 1], dtype=np.int64), np.array([1, 2], dtype=np.int64))
    with pytest.raises(ValueError):
        compute_bigram_gap(1.5, train, pairs, 3)
    with pytest.raises(ValueError):
        compute_bigram_gap(-0.1, train, pairs, 3)


def test_empty_eval_raises() -> None:
    """Empty eval pairs raise."""
    train = np.array([0, 1, 2], dtype=np.int64)
    with pytest.raises(ValueError):
        compute_word_bigram_top1(
            train,
            (np.array([], dtype=np.int64), np.array([], dtype=np.int64)),
            3,
        )


def test_n1v3_anchor_regime_smoke() -> None:
    """Smoke: at n1_v3-like anchor regime, bigram baseline lifts above unigram floor.

    Mirrors the n1_v3 anchor numerics: word-bigram top1 should land notably
    above 1/V uniform. This is a smoke-only check that the harness is in the
    right regime; it does NOT reproduce n1_v3 results (which used a Pythia
    encoder + actual Wikipedia stream).
    """
    v = 32
    rng = np.random.default_rng(42)
    # Zipfian-ish frequency with mild bigram structure.
    n = 20_000
    train = np.empty(n, dtype=np.int64)
    train[0] = 0
    for i in range(1, n):
        if rng.random() < 0.5:
            train[i] = (train[i - 1] + rng.integers(1, 4)) % v
        else:
            # Zipf-skewed unigram draw.
            r = rng.random()
            train[i] = int(min(v - 1, math.floor(r ** 2 * v)))
    eval_cues = train[-2000:-1]
    eval_tgts = train[-1999:]
    bigram = compute_word_bigram_top1(train, (eval_cues, eval_tgts), v)
    unigram = compute_unigram_top1(train, eval_tgts, v)
    # Bigram should be measurably above unigram and above uniform (1/V).
    assert bigram["word_bigram_top1"] > unigram["unigram_top1"]
    assert bigram["word_bigram_top1"] > 1.0 / v
