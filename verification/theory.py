"""Closed-form predictions from Plate, Kanerva, and related VSA literature."""

from __future__ import annotations

import math


def atom_similarity_std(n: int) -> float:
    """Expected std of off-diagonal pairwise similarities for random atoms of dimension n."""
    return 1.0 / math.sqrt(n)


def bundle_capacity_threshold(n: int, target_accuracy: float = 0.99) -> int:
    """Largest bundle size k at which expected recovery accuracy >= target. Plate 1995."""
    raise NotImplementedError("Week 3")


def hebbian_steady_state(eta: float, decay: float, activation_rate: float) -> float:
    """Analytic steady-state weight under sustained co-activation."""
    raise NotImplementedError("Week 3")
