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
