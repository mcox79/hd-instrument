"""Verification: lm_eval_harness — top-K, T-calibrated BPC, regime gates, bigram-gap."""

from __future__ import annotations

import math

import numpy as np
import pytest

from hdlab.lm_eval_harness import (
    DEFAULT_TEMPERATURE_GRID,
    ENCODER_PROVENANCE,
    compute_uniform_baseline_bpc,
    evaluate_lm,
)


def _make_unigram_logits(unigram_probs: np.ndarray, n_eval: int) -> np.ndarray:
    """Tile log-prob row N_eval times so cue-independent unigram baseline scores OK."""
    logp = np.log(np.clip(unigram_probs, 1e-30, 1.0))
    return np.broadcast_to(logp[None, :], (n_eval, unigram_probs.size)).copy()


def test_provenance_constant() -> None:
    """Module exports SUBSTRATE_NATIVE provenance marker."""
    assert ENCODER_PROVENANCE == "SUBSTRATE_NATIVE"


def test_uniform_baseline_bpc() -> None:
    """Uniform distribution over V tokens has BPC = log2(V) exactly."""
    for v in [2, 8, 100, 8192]:
        assert compute_uniform_baseline_bpc(v) == pytest.approx(math.log2(v))


def test_uniform_logits_reproduce_log2_V_BPC() -> None:
    """Cell that returns uniform logits should measure BPC == log2(V) at any T."""
    v = 64
    n = 200
    rng = np.random.default_rng(0)
    targets = rng.integers(0, v, size=n)
    logits = np.zeros((n, v), dtype=np.float32)  # uniform after softmax at any T
    out = evaluate_lm(
        logits, (np.zeros(n, dtype=np.int64), targets), vocab_size=v
    )
    # BPC at every T should equal log2(V) within float tolerance.
    expected = math.log2(v)
    for t_str, bpc in out["BPC_grid"].items():
        assert bpc == pytest.approx(expected, abs=1e-5), (
            f"uniform logits at T={t_str}: BPC={bpc}, expected {expected}"
        )


def test_unigram_baseline_reproduces() -> None:
    """Unigram-argmax baseline top1 matches max(unigram_probs); BPC near entropy."""
    v = 16
    n = 5000
    rng = np.random.default_rng(7)
    # Skewed unigram: token 0 has prob 0.5, rest split remainder.
    probs = np.full(v, 0.5 / (v - 1))
    probs[0] = 0.5
    targets = rng.choice(v, size=n, p=probs)
    cues = np.zeros(n, dtype=np.int64)
    logits = _make_unigram_logits(probs, n)
    out = evaluate_lm(logits, (cues, targets), vocab_size=v)
    # Top1 = predicting argmax (token 0) every step, so accuracy ~ P(target == 0).
    assert out["top1"] == pytest.approx(0.5, abs=0.04)
    # BPC at T=1 with log-prob logits: equals the unigram cross-entropy bits
    # = -sum p log2 p (since target distribution matches the logits).
    expected_bpc = -float(np.sum(probs * np.log2(np.clip(probs, 1e-30, 1.0))))
    assert out["BPC_at_T_1p0"] == pytest.approx(expected_bpc, abs=0.05)


def test_bigram_baseline_tighter_than_unigram() -> None:
    """Synthetic conditional with strong bigram structure: bigram BPC < unigram BPC."""
    v = 8
    n = 4000
    rng = np.random.default_rng(11)
    # Strong bigram: next-token deterministic from prev (next = (prev + 1) % V).
    targets = np.empty(n, dtype=np.int64)
    cues = rng.integers(0, v, size=n)
    for i in range(n):
        targets[i] = (cues[i] + 1) % v
    # Bigram-aware logits: place all mass on (cue + 1).
    logits = np.full((n, v), -10.0, dtype=np.float32)
    for i in range(n):
        logits[i, (int(cues[i]) + 1) % v] = 10.0
    out = evaluate_lm(logits, (cues, targets), vocab_size=v)
    assert out["top1"] == pytest.approx(1.0, abs=1e-6)
    # Sharp logits at low T -> near-zero BPC; at T=1 still small.
    assert out["BPC_at_T_optimal"] < 0.05
    assert out["regime_check_passed"]
    # And saturation flag fires (top1 == 1.0 on non-trivial vocab).
    assert out["saturation_flag"] is True


def test_T_calibration_sweep_monotone_for_sharp_logits() -> None:
    """For correct-but-sharp logits, BPC is monotone-increasing in T up to T*."""
    v = 16
    n = 500
    rng = np.random.default_rng(3)
    targets = rng.integers(0, v, size=n)
    cues = np.zeros(n, dtype=np.int64)
    # Logits where target gets large positive, others ~0.
    logits = np.zeros((n, v), dtype=np.float32)
    for i in range(n):
        logits[i, int(targets[i])] = 5.0
    t_grid = [0.1, 0.25, 0.5, 1.0, 2.0, 4.0]
    out = evaluate_lm(
        logits, (cues, targets), vocab_size=v, temperature_grid=t_grid
    )
    bpcs = [out["BPC_grid"][f"{T:.4g}"] for T in t_grid]
    # T smaller -> probs sharper on correct -> lower BPC; expect monotone-increasing.
    # (With targets always correct, BPC at smaller T is smaller.)
    for i in range(1, len(bpcs)):
        assert bpcs[i] >= bpcs[i - 1] - 1e-6, (
            f"BPC not monotone in T: {list(zip(t_grid, bpcs))}"
        )
    # T_optimal should be smallest T.
    assert out["T_optimal"] == pytest.approx(min(t_grid))


def test_top1_and_top5_independent_of_temperature() -> None:
    """Top-K accuracy is computed from raw scores; T cannot poison it."""
    v = 100
    n = 50
    rng = np.random.default_rng(5)
    targets = rng.integers(0, v, size=n)
    cues = np.zeros(n, dtype=np.int64)
    logits = rng.normal(size=(n, v)).astype(np.float32)
    # Put target as rank-3 by setting it to 3rd-largest value per row.
    sorted_logits = np.sort(logits, axis=1)
    rank3 = sorted_logits[:, -3]
    for i in range(n):
        logits[i, int(targets[i])] = float(rank3[i]) + 1e-6  # tie -> argmax picks new value sometimes; bump to be exactly rank 3
    # Just verify top5 contains target if there are no ties.
    out_a = evaluate_lm(logits, (cues, targets), vocab_size=v, top_k=[1, 5])
    out_b = evaluate_lm(
        logits, (cues, targets), vocab_size=v, top_k=[1, 5],
        temperature_grid=[0.01, 100.0],
    )
    assert out_a["top1"] == out_b["top1"]
    assert out_a["top5"] == out_b["top5"]


def test_regime_check_gate() -> None:
    """regime_check_passed = top1 > 2 * sanity (sanity = 1/V)."""
    v = 100
    n = 200
    rng = np.random.default_rng(13)
    targets = rng.integers(0, v, size=n)
    cues = np.zeros(n, dtype=np.int64)
    # Random logits -> top1 ~ 1/V; regime check fails.
    logits = rng.normal(size=(n, v)).astype(np.float32)
    out = evaluate_lm(logits, (cues, targets), vocab_size=v)
    assert out["sanity_top1_at_random"] == pytest.approx(0.01)
    # With random logits, top1 << 0.02 with high prob.
    if out["top1"] <= 0.02:
        assert out["regime_check_passed"] is False


def test_callable_scores_fn() -> None:
    """scores_fn callable interface produces identical results to precomputed."""
    v = 32
    n = 50
    rng = np.random.default_rng(17)
    targets = rng.integers(0, v, size=n)
    cues = rng.integers(0, v, size=n)
    # Fixed logits per cue (cue->logits deterministic).
    cue_to_logits = {int(c): rng.normal(size=v).astype(np.float32) for c in cues}

    def scores(cue_id: int) -> np.ndarray:
        return cue_to_logits[cue_id]

    out_callable = evaluate_lm(
        scores, list(zip(cues.tolist(), targets.tolist())),
        vocab_size=v,
    )
    # Build the matrix manually for comparison.
    matrix = np.stack([cue_to_logits[int(c)] for c in cues])
    out_matrix = evaluate_lm(matrix, (cues, targets), vocab_size=v)
    assert out_callable["top1"] == out_matrix["top1"]
    assert out_callable["BPC_at_T_optimal"] == pytest.approx(
        out_matrix["BPC_at_T_optimal"]
    )


def test_bigram_gap_field() -> None:
    """When word_bigram_top1 supplied, bigram_gap = substrate_top1 - word_bigram_top1."""
    v = 10
    n = 100
    targets = np.zeros(n, dtype=np.int64)
    cues = np.zeros(n, dtype=np.int64)
    logits = np.zeros((n, v), dtype=np.float32)
    logits[:, 0] = 10.0  # perfect predict-0
    out = evaluate_lm(
        logits, (cues, targets), vocab_size=v, word_bigram_top1=0.55
    )
    assert out["top1"] == pytest.approx(1.0)
    assert out["bigram_gap"] == pytest.approx(1.0 - 0.55)
    assert out["word_bigram_top1"] == pytest.approx(0.55)


def test_default_temperature_grid_includes_1p0() -> None:
    """DEFAULT_TEMPERATURE_GRID covers the rigged T=1.0 reference."""
    assert 1.0 in DEFAULT_TEMPERATURE_GRID
    # Plus a sub-1 region (sharpening).
    assert any(T < 1.0 for T in DEFAULT_TEMPERATURE_GRID)


def test_empty_eval_raises() -> None:
    """evaluate_lm with empty eval_data raises ValueError."""
    with pytest.raises(ValueError):
        evaluate_lm(
            np.zeros((0, 10), dtype=np.float32),
            (np.zeros(0, dtype=np.int64), np.zeros(0, dtype=np.int64)),
            vocab_size=10,
        )


def test_target_out_of_range_raises() -> None:
    """Out-of-range targets are caught early."""
    v = 10
    logits = np.zeros((3, v), dtype=np.float32)
    cues = np.zeros(3, dtype=np.int64)
    targets = np.array([0, 5, 15], dtype=np.int64)  # 15 >= V
    with pytest.raises(ValueError):
        evaluate_lm(logits, (cues, targets), vocab_size=v)
