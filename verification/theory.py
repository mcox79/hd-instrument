"""Closed-form predictions from Plate, Kanerva, and related VSA literature."""

from __future__ import annotations

import math


def atom_similarity_std(n: int) -> float:
    """Expected std of off-diagonal pairwise similarities for random atoms of dimension n."""
    return 1.0 / math.sqrt(n)


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
