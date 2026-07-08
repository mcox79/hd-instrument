"""Lock-in amplifier readout: phase-sensitive detection for coherent signal recovery.

Promotes the Stage-2 chain-grade primitive substrate_lock_in_amp_phase_diagram v2 (3-seed
CG 2026-06-28, cell commit 50362430; math CG atom
EXP_substrate_lock_in_amp_phase_diagram_v2_FULL_3seed_chain_grade_phase_characterization_...)
into hdlab.

Mechanism (certified, unchanged from the cell): a fixed real-valued vector `signal` is
amplitude-modulated by a reference carrier cos(2*pi*freq*p) and transmitted over t samples
through an additive-Gaussian channel; the receiver demodulates by multiplying the received
samples by the SAME carrier (phase-coherent) and integrating with a (2/t) normalization:

    decoded = (2/t) * sum_p received[p] * carrier[p]

The signal adds coherently (each sample contributes signal*cos^2, summing to ~signal) while
zero-mean channel noise adds incoherently, so the output SNR is lifted by sqrt(t/2):
SNR_out = SNR_in * sqrt(t/2). This recovers a coherent component from noise in the regime
SNR_out in [1e-2, 1e0) where single-sample (direct) readout fails -- the textbook lock-in
coherent-integration advantage the cell characterized as a phase diagram.

Convention: numpy at boundaries (matches the certified numpy cell and the sibling readout
primitive hdlab.cleanup_family peel/SIC). Real-valued float64 internally; accepts a passed-in
np.random.Generator for reproducible channel noise. ASCII-only; no substrate tracing state
(scaffold-free -- the certified mechanism is a pure signal-processing readout).

Storage strategy: NO_STORAGE (stateless readout; holds no compositional data). The
compositional-storage physics law does not apply; any L-composition inherits downstream
storage strategy verbatim.
"""
from __future__ import annotations

import math
from typing import Optional

import numpy as np


def reference_carrier(t_int: int, freq: float) -> np.ndarray:
    """Reference carrier cos(2*pi*freq*p) for p in 0..t_int-1; shape (t_int,), float64."""
    if t_int < 1:
        raise ValueError(f"reference_carrier: t_int must be >= 1; got {t_int}")
    return np.cos(2.0 * np.pi * float(freq) * np.arange(t_int, dtype=np.float64))


def snr_gain(t_int: int) -> float:
    """Coherent-integration SNR gain sqrt(t_int/2) (SNR_out / SNR_in)."""
    if t_int < 1:
        raise ValueError(f"snr_gain: t_int must be >= 1; got {t_int}")
    return math.sqrt(t_int / 2.0)


def snr_output(snr_input: float, t_int: int) -> float:
    """Predicted post-integration SNR: snr_input * sqrt(t_int/2)."""
    return float(snr_input) * snr_gain(t_int)


def modulate_and_receive(
    signal: np.ndarray,
    carrier: np.ndarray,
    sigma: float,
    generator: Optional[np.random.Generator] = None,
) -> np.ndarray:
    """Amplitude-modulate signal by carrier and add channel noise; returns (t, N) received.

    received[p] = signal * carrier[p] + N(0, sigma^2). signal is (N,); carrier is (t,).
    """
    if signal.ndim != 1:
        raise ValueError(f"modulate_and_receive: signal must be 1-D (N,); got {signal.shape}")
    if carrier.ndim != 1:
        raise ValueError(f"modulate_and_receive: carrier must be 1-D (t,); got {carrier.shape}")
    if sigma < 0.0:
        raise ValueError(f"modulate_and_receive: sigma must be >= 0; got {sigma}")
    gen = generator if generator is not None else np.random.default_rng()
    sig = signal.astype(np.float64)
    car = carrier.astype(np.float64)
    clean = np.outer(car, sig)  # (t, N)
    if sigma == 0.0:
        return clean
    noise = gen.standard_normal(size=clean.shape) * float(sigma)
    return clean + noise


def lock_in_demodulate(received: np.ndarray, carrier: np.ndarray) -> np.ndarray:
    """Phase-sensitive detection: (2/t) * sum_p received[p] * carrier[p]; returns (N,) float64.

    received is (t, N) time-samples; carrier is (t,) reference. Coherent (same-frequency,
    same-phase) demodulation -- the certified lock-in readout.
    """
    if carrier.ndim != 1:
        raise ValueError(f"lock_in_demodulate: carrier must be 1-D (t,); got {carrier.shape}")
    if received.ndim != 2:
        raise ValueError(
            f"lock_in_demodulate: received must be 2-D (t, N); got {received.shape}")
    t_int = carrier.shape[0]
    if received.shape[0] != t_int:
        raise ValueError(
            f"lock_in_demodulate: received.shape[0]={received.shape[0]} must equal "
            f"carrier length {t_int}")
    car = carrier.astype(np.float64)
    rec = received.astype(np.float64)
    return (2.0 / t_int) * (car @ rec)


def lock_in_recall_at_1(
    codebook: np.ndarray,
    decoded: np.ndarray,
) -> int:
    """argmax cleanup: index of the codebook row best matching the decoded vector.

    codebook is (M, N); decoded is (N,). Returns the argmax index.
    """
    if codebook.ndim != 2:
        raise ValueError(f"lock_in_recall_at_1: codebook must be 2-D (M, N); got {codebook.shape}")
    if decoded.ndim != 1 or decoded.shape[0] != codebook.shape[1]:
        raise ValueError(
            f"lock_in_recall_at_1: decoded must be (N,) matching codebook dim "
            f"{codebook.shape[1]}; got {decoded.shape}")
    return int(np.argmax(codebook.astype(np.float64) @ decoded.astype(np.float64)))


# ----- Formula selftests (reproduce the certified cell's selftests) ----------


def _selftest_clean_recovers_signal_exact() -> None:
    """sigma=0, freq=0.1, t=10, N=512: demodulate reconstructs the transmitted vector exactly."""
    gen = np.random.default_rng(13)
    v = gen.choice([-1.0, 1.0], size=512).astype(np.float64)
    car = reference_carrier(10, 0.1)
    received = modulate_and_receive(v, car, sigma=0.0)
    decoded = lock_in_demodulate(received, car)
    factor = (2.0 / 10.0) * float(np.sum(car ** 2))
    max_diff = float(np.max(np.abs(decoded - factor * v)))
    if max_diff > 1e-10:
        raise AssertionError(f"clean recovery FAIL: max|diff|={max_diff:.2e}")
    if abs(factor - 1.0) > 1e-10:
        raise AssertionError(f"cos2 norm at f=0.1 t=10 should be 1.0; got {factor}")


def _selftest_cos2_normalization() -> None:
    """(2/t) * sum cos^2 ~= 1.0 for t in {10,100,1000,10000} at freq=0.1."""
    for t_int in (10, 100, 1000, 10000):
        car = reference_carrier(t_int, 0.1)
        norm = (2.0 / t_int) * float(np.sum(car ** 2))
        if abs(norm - 1.0) > 0.01:
            raise AssertionError(f"t={t_int}: (2/t)*sum cos^2 = {norm}; expected ~1.0")


def _selftest_snr_gain_sqrt_t_over_2() -> None:
    """snr_gain(t) == sqrt(t/2) and snr_output composes linearly in snr_input."""
    for t_int in (10, 100, 1000, 10000):
        if abs(snr_gain(t_int) - math.sqrt(t_int / 2.0)) > 1e-12:
            raise AssertionError(f"snr_gain({t_int}) mismatch")
    if abs(snr_output(0.01, 1000) - 0.01 * math.sqrt(500.0)) > 1e-12:
        raise AssertionError("snr_output composition FAIL")


def _selftest_demodulate_matches_bruteforce() -> None:
    """Vectorized demodulate == explicit per-sample loop (reference equivalence)."""
    gen = np.random.default_rng(17)
    v = gen.choice([-1.0, 1.0], size=64).astype(np.float64)
    car = reference_carrier(50, 0.1)
    received = modulate_and_receive(v, car, sigma=0.3, generator=np.random.default_rng(5))
    fast = lock_in_demodulate(received, car)
    acc = np.zeros(64, dtype=np.float64)
    for p in range(50):
        acc += received[p] * car[p]
    slow = (2.0 / 50.0) * acc
    if float(np.max(np.abs(fast - slow))) > 1e-10:
        raise AssertionError("demodulate vs brute-force mismatch")


def _selftest_advantage_band_discriminator_fires() -> None:
    """SNR_out band (SNR_in=0.01 t=1000 N=2048): lock-in recovers where direct fails, delta>=0.30."""
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
    if lock_recall - direct_recall < 0.30:
        raise AssertionError(
            f"advantage-band discriminator did NOT fire: lock={lock_recall:.3f} "
            f"direct={direct_recall:.3f} delta={lock_recall - direct_recall:.3f} (need >= 0.30)")


def _run_all_selftests() -> dict:
    _selftest_clean_recovers_signal_exact()
    _selftest_cos2_normalization()
    _selftest_snr_gain_sqrt_t_over_2()
    _selftest_demodulate_matches_bruteforce()
    _selftest_advantage_band_discriminator_fires()
    return {
        "primitive": "lock_in_amp_phase_sensitive_detection",
        "snr_law": "SNR_out = SNR_in * sqrt(t/2)",
        "storage_strategy": "NO_STORAGE",
        "cg_source": (
            "substrate_lock_in_amp_phase_diagram v2 3-seed chain-grade 2026-06-28 "
            "cell commit 50362430"),
    }


if __name__ == "__main__":
    result = _run_all_selftests()
    print(f"[lock_in_amp selftest] PASS {result}")
