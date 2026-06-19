"""Closed-form predictions from Plate, Kanerva, and related VSA literature."""

from __future__ import annotations

import math


def atom_similarity_std(n: int, dtype: str = "complex64") -> float:
    """Expected std of off-diagonal pairwise similarities for random atoms of dimension n.

    FHRR (complex64, unit-magnitude phases): Var(Re(<a,b*>/n)) = 1/(2n), so std = 1/sqrt(2n).
    HRR (float32, gaussian std=1/sqrt(n)): Var(<a,b>/n) = 1/n, so std = 1/sqrt(n).

    Caught when A1 empirical at N=1024 came in at 0.0221 vs the original 1/sqrt(N)=0.0312
    formula. Real FHRR variance derivation: each component contributes Re(z1 * conj(z2)) with
    z1,z2 = exp(i*phi) for independent uniform phases; that's cos(phi1-phi2) which has variance
    1/2. Summed over n components and divided by n, the result has variance 1/(2n).
    """
    if dtype in ("complex64", "complex128"):
        return 1.0 / math.sqrt(2 * n)
    if dtype in ("float32", "float64"):
        return 1.0 / math.sqrt(n)
    raise ValueError(f"Unsupported dtype for atom_similarity_std: {dtype}")


def bundle_capacity_threshold(n: int, target_accuracy: float = 0.99) -> int:
    """Largest bundle size k at which expected recovery accuracy >= target. Plate 1995."""
    raise NotImplementedError("Week 7")


def hebbian_steady_state(eta: float, decay: float, activation_rate: float = 1.0) -> float:
    """Steady-state weight under sustained co-activation: W_inf = eta * activation_rate / decay.

    Derived from W[t+1] = (1-decay) * W[t] + eta * activation_rate at convergence.
    """
    if decay <= 0:
        raise ValueError("decay must be positive for a finite steady state")
    return eta * activation_rate / decay


def hopfield_alpha_c_ags(n: int) -> float:
    """AGS 1985 critical capacity for Hopfield with random patterns + Hebbian W."""
    return 0.138 * n


def bundle_topk_alpha_c_floor(n: int, m: int, target_recovery: float = 0.5) -> float:
    """Plate/Kanerva floor for top-K-against-M recovery via signed-bundle cleanup.

    K* (the K at which top-K recovery against an M-codebook crosses target) satisfies
    K* ~ n / (2 * log(2 * m / (1 - target_recovery))) for small (1 - target_recovery).
    Returns alpha_c = K*/n.
    """
    delta = max(1e-6, 1.0 - target_recovery)
    return 1.0 / (2.0 * math.log(2.0 * m / delta))


def hopfield_recovery_safe_K(n: int, decoder: str = "softmax") -> int:
    """Below this K, modern Hopfield (Ramsauer 2020 / Hu 2023) MUST recover >= 0.95
    on lightly-corrupted queries (~10% bit flips).

    Conservative: 0.05 * n for softmax; 0.10 * n for sparsemax (Hu 2023).
    """
    if decoder == "softmax":
        return max(2, int(0.05 * n))
    if decoder in ("sparsemax", "entmax"):
        return max(2, int(0.10 * n))
    raise ValueError(f"unknown decoder for safe_K: {decoder}")


def antihebbian_orthogonal_residual(alpha: float) -> float:
    """For orthogonal random +/-1 keys, anti-Hebbian rank-1 erase reduces the
    erased value's coefficient from 1 to (1 - alpha).

    At alpha=1 the value is fully zeroed (residual = 0).
    """
    return max(0.0, 1.0 - alpha)


def erase_baseline_leak_rate_random(n_facts: int) -> tuple[float, float]:
    """Baseline (no erase, Method A) leak rate for random keys/values:
    every fact is retrievable, so leak rate ~ 1.0.

    Returns (low, high) sanity range. Use to assert Method A baseline matches.
    """
    return (0.85, 1.0)


def erase_floor_random_alpha_one(n_facts: int, n: int) -> tuple[float, float]:
    """At alpha=1 with orthogonal random keys, Method B leak rate should be at the
    floor: argmax-over-bank of a near-zero retrieved vector is random.

    Floor = ~1/n_facts (random argmax over the codebook).
    Returns (low, high) sanity range.
    """
    expected = 1.0 / max(1, n_facts)
    return (0.0, max(0.1, 3.0 * expected))
