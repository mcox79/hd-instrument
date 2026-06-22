"""Split-conformal prediction. Distribution-free coverage guarantees from a calibration set.

Standard split-conformal: given calibration nonconformity scores and a significance level
alpha, return the (1-alpha) quantile threshold q. Any test instance whose nonconformity
score s satisfies s <= q is included in the prediction set; coverage is >= 1-alpha
(marginal, exchangeable test/cal).

This is the substrate's calibration-set primitive complementing refuse_gate (which solves
threshold-from-paired-distributions); conformal solves threshold-for-coverage-from-single-set.
"""

from __future__ import annotations

import math

import torch


def calibrate_quantile(
    nonconformity_scores: torch.Tensor,
    alpha: float,
) -> float:
    """Split-conformal threshold from calibration nonconformity scores.

    Args:
        nonconformity_scores: 1-D tensor of calibration nonconformity scores
            (e.g. 1 - top-1 softmax prob; or distance-to-nearest; lower = more conformal).
        alpha: significance level in (0, 1). Coverage target is 1 - alpha.

    Returns:
        threshold q (float). At test time, include label y in the prediction set iff
        nonconformity_score(x, y) <= q. Marginal coverage >= 1 - alpha.
    """
    if nonconformity_scores.numel() == 0:
        raise ValueError("calibrate_quantile requires non-empty nonconformity_scores")
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"alpha must be in (0, 1); got {alpha}")

    n = int(nonconformity_scores.numel())
    rank = math.ceil((n + 1) * (1.0 - alpha))
    rank = min(max(rank, 1), n)
    sorted_scores, _ = torch.sort(nonconformity_scores)
    return float(sorted_scores[rank - 1])


def predict_set(
    test_scores: torch.Tensor,
    q: float,
) -> torch.Tensor:
    """Boolean mask: True where test_scores[i] <= q (i.e. included in prediction set)."""
    return test_scores <= q


def empirical_coverage(
    test_nonconformity_scores: torch.Tensor,
    q: float,
) -> float:
    """Fraction of test points with true-label nonconformity <= q.

    Marginal coverage should be approximately >= 1 - alpha when test and calibration
    sets are exchangeable.
    """
    if test_nonconformity_scores.numel() == 0:
        raise ValueError("empirical_coverage requires non-empty test_nonconformity_scores")
    return float((test_nonconformity_scores <= q).float().mean())
