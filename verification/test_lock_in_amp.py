"""Scaffold-free witness for the lock-in amplifier readout in hdlab.lock_in_amp.

Reproduces the CG-certified phenomenon in miniature: single-sample (direct) readout collapses
at low input SNR while phase-sensitive (lock-in) coherent integration over t samples recovers
the transmitted vector -- the certified sqrt(t/2) SNR gain that lifts the effective SNR into the
substrate-readable band exactly where direct readout fails. Also checks the closed-form clean-
recovery + cos2-normalization oracles (verification.theory), an independent brute-force reference
(equivalence), the sqrt(t/2) gain law, and input validation.

Passes with tracing=False (numpy-only; no substrate tracing state involved).

Certified source: substrate_lock_in_amp_phase_diagram v2 (3-seed chain-grade 2026-06-28,
cell commit 50362430).
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from hdlab.lock_in_amp import (
    reference_carrier,
    lock_in_demodulate,
    modulate_and_receive,
    lock_in_recall_at_1,
    snr_gain,
    snr_output,
)
from verification import theory


def test_clean_recovery_matches_cos2_norm_oracle() -> None:
    """sigma=0 demodulation reconstructs signal exactly at the closed-form cos2 normalization."""
    gen = np.random.default_rng(0)
    v = gen.choice([-1.0, 1.0], size=512).astype(np.float64)
    for t_int in (10, 100, 1000):
        car = reference_carrier(t_int, 0.1)
        received = modulate_and_receive(v, car, sigma=0.0)
        decoded = lock_in_demodulate(received, car)
        factor = theory.lock_in_cos2_norm(t_int, 0.1)
        assert factor == pytest.approx(1.0, abs=0.01)
        assert np.allclose(decoded, factor * v, atol=1e-10)


def test_snr_gain_matches_theory_sqrt_t_over_2() -> None:
    """snr_gain(t) == theory.lock_in_snr_gain(t) == sqrt(t/2); snr_output composes linearly."""
    for t_int in (10, 100, 1000, 10000):
        assert snr_gain(t_int) == pytest.approx(theory.lock_in_snr_gain(t_int))
        assert snr_gain(t_int) == pytest.approx(math.sqrt(t_int / 2.0))
    assert snr_output(0.01, 1000) == pytest.approx(0.01 * math.sqrt(500.0))


def test_demodulate_matches_bruteforce_reference() -> None:
    """Vectorized demodulate == independent explicit per-sample loop (oracle for equivalence)."""
    gen = np.random.default_rng(1)
    v = gen.choice([-1.0, 1.0], size=96).astype(np.float64)
    car = reference_carrier(60, 0.1)
    received = modulate_and_receive(v, car, sigma=0.4, generator=np.random.default_rng(2))
    fast = lock_in_demodulate(received, car)
    acc = np.zeros(96, dtype=np.float64)
    for p in range(60):
        acc += received[p] * car[p]
    slow = (2.0 / 60.0) * acc
    assert np.allclose(fast, slow, atol=1e-10)


def test_lock_in_beats_direct_in_advantage_band() -> None:
    """Low-SNR band (SNR_in=0.01 t=1000): lock-in recovers, direct collapses (discriminator fires)."""
    n_dim, m_cb, t_int, snr_in, n_eval, freq = 2048, 100, 1000, 0.01, 30, 0.1
    sigma = 1.0 / snr_in
    gen = np.random.default_rng(7)
    codebook = gen.choice([-1.0, 1.0], size=(m_cb, n_dim)).astype(np.float64)
    car = reference_carrier(t_int, freq)
    lock_correct = direct_correct = 0
    for _ in range(n_eval):
        tgt = int(gen.integers(m_cb))
        v = codebook[tgt]
        received = modulate_and_receive(v, car, sigma=sigma, generator=gen)
        decoded = lock_in_demodulate(received, car)
        lock_correct += int(lock_in_recall_at_1(codebook, decoded) == tgt)
        direct = v + gen.standard_normal(size=n_dim) * sigma
        direct_correct += int(lock_in_recall_at_1(codebook, direct) == tgt)
    lock_recall = lock_correct / n_eval
    direct_recall = direct_correct / n_eval
    # certified physics: coherent integration recovers where single-sample readout fails
    assert direct_recall < 0.10, f"direct should collapse at SNR_in=0.01, got {direct_recall:.3f}"
    assert lock_recall > 0.90, f"lock-in should recover at SNR_out~0.22, got {lock_recall:.3f}"
    assert lock_recall - direct_recall > 0.30, (
        f"lock-in advantage too small: {lock_recall - direct_recall:+.3f} (need > 0.30)")
    # predicted SNR_out lands in the certified advantage band [1e-2, 1e0)
    assert 1e-2 <= snr_output(snr_in, t_int) < 1e0


def test_floor_regime_both_arms_fail() -> None:
    """Deep-floor (SNR_out < 1e-3): even lock-in cannot recover (true floor, not an artifact)."""
    n_dim, m_cb, t_int, snr_in, n_eval, freq = 2048, 100, 10, 1e-4, 20, 0.1
    sigma = 1.0 / snr_in
    gen = np.random.default_rng(19)
    codebook = gen.choice([-1.0, 1.0], size=(m_cb, n_dim)).astype(np.float64)
    car = reference_carrier(t_int, freq)
    lock_correct = 0
    for _ in range(n_eval):
        tgt = int(gen.integers(m_cb))
        received = modulate_and_receive(codebook[tgt], car, sigma=sigma, generator=gen)
        decoded = lock_in_demodulate(received, car)
        lock_correct += int(lock_in_recall_at_1(codebook, decoded) == tgt)
    assert snr_output(snr_in, t_int) < 1e-3
    assert lock_correct / n_eval <= 0.10, "deep-floor regime should sit at chance"


def test_input_validation() -> None:
    """Bad shapes / negative sigma / mismatched lengths raise ValueError (no silent misuse)."""
    car = reference_carrier(20, 0.1)
    v = np.ones(32, dtype=np.float64)
    with pytest.raises(ValueError):
        reference_carrier(0, 0.1)
    with pytest.raises(ValueError):
        snr_gain(0)
    with pytest.raises(ValueError):
        modulate_and_receive(v, car, sigma=-0.1)
    with pytest.raises(ValueError):
        modulate_and_receive(np.ones((2, 32)), car, sigma=0.1)  # signal not 1-D
    with pytest.raises(ValueError):
        lock_in_demodulate(np.ones(20), car)  # received not 2-D
    with pytest.raises(ValueError):
        lock_in_demodulate(np.ones((19, 32)), car)  # t mismatch
