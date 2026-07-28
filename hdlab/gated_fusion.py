"""Learned convex-gate fusion (promoted 2026-07-28, testbed).

Extracted from `experiments/exp_grounding_gated_fusion_relation_inference_mammal_v1.py`
-- HARD_PASS, full 8-seed run, all seeds positive, scramble-controlled,
recover_gain +0.297 MRR over the naive equal-weight fusion (2026-07-14). See
`data/capability_registry.jsonl` id=gated_fusion_relation_inference.

MECHANISM: two competing per-row code estimates (a "primary" estimate, e.g.
relation-inference-only, and a "fallback" estimate, e.g. grounding-only) are
combined with a SINGLE scalar gate lambda in [0,1]:

    fused[row] = (1 - lambda) * primary[row] + lambda * fallback[row]

lambda is grid-searched on a held-out VAL split to maximize a caller-supplied
scoring function, NEVER on TEST. Because the search grid includes lambda=1.0
(pure fallback), the learned fusion cannot underperform the fallback
endpoint on VAL by construction -- this is what makes it a RECOVERY gate
(never worse than falling back to the stronger single-arm estimate) rather
than the naive equal-weight SUM fusion, which dilutes a strong arm with a
weak one. Glass-box: one interpretable scalar per corpus/seed, no learned
weight matrix, no black-box combiner.

Deliberately decoupled from any one experiment's scoring/eval pipeline --
callers pass a `score_fn(fused_table) -> float` closure over their own
VAL query set and metric (e.g. filtered MRR), so this module has no
dependency on `experiments/*` eval helpers and can be reused for ANY
two-estimate fusion problem (e.g. text-embedding + structured-grounding
fusion), not just the relation-inference-vs-grounding case it was proven on.

Extraction is mechanical: `gated_table`/`equal_sum_table`/`learn_lambda` here
are the same logic as `_gated_table`/`_equal_sum_table`/`learn_lambda` in the
source cell, generalized (renamed primary/fallback instead of rel/grd) and
with the scoring pipeline replaced by an injected callable.
"""
from __future__ import annotations

from typing import Callable, Dict, Mapping, Sequence, Tuple

import torch

Scorer = Callable[[torch.Tensor], float]


def gated_table(
    X: torch.Tensor,
    primary_codes: torch.Tensor,
    fallback_codes: torch.Tensor,
    held_ids: Sequence[int],
    support_deg: Mapping[int, int],
    lam: float,
) -> torch.Tensor:
    """Convex-combine (1-lam)*primary + lam*fallback on supported held rows; cold rows -> pure fallback.

    A "cold" row (support_deg[row] == 0) has no primary-side evidence at all
    (e.g. a relation-inference arm with zero training support for that
    entity), so it always takes the fallback estimate regardless of lambda.
    """
    Xp = X.clone()
    for s in held_ids:
        if support_deg[s] > 0:
            Xp[s] = (1.0 - lam) * primary_codes[s] + lam * fallback_codes[s]
        else:
            Xp[s] = fallback_codes[s]
    return Xp


def equal_sum_table(
    X: torch.Tensor,
    primary_codes: torch.Tensor,
    fallback_codes: torch.Tensor,
    held_ids: Sequence[int],
    support_deg: Mapping[int, int],
) -> torch.Tensor:
    """Reference/diagnostic: the naive diluting alpha=beta=1 SUM fusion that gated_table replaces."""
    Xp = X.clone()
    for s in held_ids:
        if support_deg[s] > 0:
            Xp[s] = primary_codes[s] + fallback_codes[s]
        else:
            Xp[s] = fallback_codes[s]
    return Xp


def learn_lambda(
    X: torch.Tensor,
    primary_codes: torch.Tensor,
    fallback_codes: torch.Tensor,
    val_ids: Sequence[int],
    support_deg: Mapping[int, int],
    score_fn: Scorer,
    grid: Sequence[float],
    val_n: int,
    min_val_n: int,
) -> Tuple[float, float, Dict[float, float], bool]:
    """Grid-search lambda maximizing score_fn(gated_table(...)) on a VAL split.

    `grid` MUST include 1.0 (pure fallback) so the learned gate cannot
    underperform the fallback endpoint on VAL by construction -- this is what
    makes the mechanism a RECOVERY gate, not a dilution risk.

    val_n / min_val_n: caller-computed VAL-set size and its minimum-viable
    floor; below the floor this falls back to lambda=1.0 (pure fallback,
    still a valid no-op recovery) rather than fitting an unreliable gate on
    too few points.

    Returns (best_lambda, best_score, curve_dict, used_fallback).
    """
    if val_n < min_val_n:
        return 1.0, float("nan"), {}, True
    best_lam, best_score, curve = 1.0, -1.0, {}
    for lam in grid:
        Xp = gated_table(X, primary_codes, fallback_codes, val_ids, support_deg, lam)
        score = float(score_fn(Xp))
        curve[lam] = round(score, 5)
        if score > best_score:
            best_score, best_lam = score, lam
    return best_lam, best_score, curve, False


def _selftest() -> None:
    """Planted-latent smoke: on rows where fallback strictly dominates primary, the gate should
    learn lambda close to 1.0 and beat the naive equal-weight fusion."""
    torch.manual_seed(0)
    n, d = 20, 16
    X = torch.zeros(n, d)
    primary = torch.randn(n, d) * 0.05          # weak, near-noise primary estimate
    fallback = torch.randn(n, d)                # strong signal estimate
    target = fallback.clone()                    # ground truth == fallback (fallback should win)
    held_ids = list(range(n))
    support_deg = {i: 1 for i in range(n)}

    def score_fn(Xp: torch.Tensor) -> float:
        # negative MSE to target = higher is better, closed-form, no external eval dep
        return float(-((Xp[held_ids] - target[held_ids]) ** 2).mean())

    grid = [round(x, 2) for x in torch.linspace(0, 1, 11).tolist()]
    lam, score, curve, used_fallback = learn_lambda(
        X, primary, fallback, held_ids, support_deg, score_fn, grid, val_n=n, min_val_n=5
    )
    assert not used_fallback
    assert lam >= 0.8, f"expected gate to favor the strong fallback arm, got lambda={lam}"

    gated = gated_table(X, primary, fallback, held_ids, support_deg, lam)
    summed = equal_sum_table(X, primary, fallback, held_ids, support_deg)
    gated_err = float(((gated[held_ids] - target[held_ids]) ** 2).mean())
    summed_err = float(((summed[held_ids] - target[held_ids]) ** 2).mean())
    assert gated_err < summed_err, "gate should beat the naive equal-weight dilution fusion"

    # min_val_n floor triggers pure-fallback fallback path
    lam2, score2, curve2, used_fallback2 = learn_lambda(
        X, primary, fallback, held_ids, support_deg, score_fn, grid, val_n=2, min_val_n=5
    )
    assert used_fallback2 and lam2 == 1.0 and curve2 == {}

    print(
        "[selftest] hdlab.gated_fusion OK lambda=%.2f gated_mse=%.5f < equal_sum_mse=%.5f"
        % (lam, gated_err, summed_err)
    )


if __name__ == "__main__":
    _selftest()
