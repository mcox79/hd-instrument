"""Standard metric suite: substrate health, composition fidelity, capacity, calibration."""

from __future__ import annotations

import torch


def pairwise_similarity_stats(vectors: torch.Tensor) -> dict[str, float]:
    """Mean, std, and max abs of off-diagonal pairwise similarities."""
    raise NotImplementedError("Week 1")


def capacity_curve(n: int, k_values: list[int], trials: int) -> dict[int, float]:
    """Recovery accuracy as a function of bundle size k."""
    raise NotImplementedError("Week 3")
