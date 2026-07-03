"""Saddle-cascade plateau signature test -- local re-analysis of existing Bet B data.

Context: notes/research_alternative_theoretical_homes_2026-05-24.md candidate (v):
Saad-Solla / Biehl-Schwarze saddle-cascade framework predicts that retention plateaus
correspond to fixed-points of order-parameter ODEs; their values are set by corpus-
overlap structure, NOT by continuous N/geometry/time parameters (explaining the
parameter-immunity observed in Bet B).

FULL test: 5-teacher overlap-fraction sweep (in-flight GPU probe).
THIS (local re-analysis): test the DISCRETE-JUMP PREDICTION against the *existing*
retention data across different corpus-type categories. The cascade framework predicts
retention(corpus_type) shows DISCRETE LEVELS that do NOT interpolate smoothly.

Specific falsifier: fit both (a) a discrete 3-state step function and (b) a smooth
sigmoid onto the ordering SAME_CORPUS > STAGE4 > DIFF_CORPUS. Cascade framework PASSES
if discrete 3-state fit has lower BIC than sigmoid. Continuous framework PASSES if
sigmoid has lower BIC.

Also: test the PLATEAU-HEIGHT SPACING prediction. Cascade framework predicts:
  - 0.94 plateau (SAME) corresponds to near-Bayes-optimal student
  - 0.74 plateau (STAGE4) corresponds to symmetric saddle with partial overlap
  - 0.60 plateau (DIFF) corresponds to orthogonal-teacher residual
  The 0.20 and 0.14 gaps are NOT random; they follow the formula:
    plateau_k = 1 - k * (1/K) * (1 - plateau_min)
  for K teacher classes and k in {0,1,...,K}. Test this formula.

Pre-registered outcomes:
  CASCADE_PASS: discrete 3-state BIC < sigmoid BIC (DELTA_BIC > 2) AND spacing formula
    predicted values within 0.05 of observed. Cascade framework is the better fit.
  CASCADE_FAIL: sigmoid BIC < discrete BIC by > 2. Continuous framework preferred.
  CASCADE_INCONCLUSIVE: |DELTA_BIC| <= 2. Both frameworks consistent; neither strongly
    preferred.

Queue: local_cpu_queue (pure re-analysis of existing JSON, < 5s)
Pre-reg: preregs/2026-05-25_wave14_betB_saddle_cascade_reanalysis_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
DATA = REPO / "data"


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
# ---------------------------------------------------------------------------
# Instrumentation self-test
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert BIC computation and model fitting are non-null."""
    vals = [0.1, 0.11, 0.5, 0.49, 0.9, 0.91]
    groups = [[0.1, 0.11], [0.5, 0.49], [0.9, 0.91]]
    bic_d = discrete_bic(vals, groups)
    assert bic_d is not None and not math.isnan(bic_d), f"discrete BIC null: {bic_d}"
    # Sigmoid fit on a smooth ramp
    x = [0.0, 0.5, 1.0, 1.5, 2.0]
    y = [0.1, 0.3, 0.5, 0.7, 0.9]
    bic_s = sigmoid_bic(x, y)
    assert bic_s is not None and not math.isnan(bic_s), f"sigmoid BIC null: {bic_s}"
    print("[self-test] BIC computations OK")

_SELFTEST_DEFERRED = True  # called after helpers below


# ---------------------------------------------------------------------------
# Statistical helpers
# ---------------------------------------------------------------------------

def discrete_bic(all_vals: List[float], groups: List[List[float]]) -> float:
    """BIC for a K-group step function model.

    Model: y_i ~ Normal(mu_k, sigma^2) where mu_k is the group mean.
    Parameters: K group means + 1 shared sigma = K+1 parameters.
    """
    n = len(all_vals)
    k = len(groups)
    if n <= k + 1:
        return float("inf")
    # Compute per-group means and shared RSS
    rss = 0.0
    for g in groups:
        if len(g) == 0:
            continue
        mu_g = sum(g) / len(g)
        rss += sum((v - mu_g) ** 2 for v in g)
    if rss <= 0 or n <= 0:
        return float("inf")
    sigma2_hat = rss / n
    log_lik = -n / 2.0 * (math.log(2 * math.pi * sigma2_hat) + 1.0)
    n_params = k + 1  # K means + 1 sigma
    bic = -2.0 * log_lik + n_params * math.log(n)
    return bic


def sigmoid_bic(x_vals: List[float], y_vals: List[float], n_steps: int = 200) -> float:
    """BIC for a 2-parameter sigmoid fit: f(x) = 1 / (1 + exp(-a*(x - b))).

    Parameters: a (steepness), b (midpoint), + 1 sigma = 3 parameters.
    Fit via grid search over (a, b).
    """
    n = len(y_vals)
    if n <= 3:
        return float("inf")
    best_rss = float("inf")
    x_min, x_max = min(x_vals), max(x_vals)
    x_range = max(x_max - x_min, 1e-6)
    # Grid search: a in [0.5, 20], b in [x_min-0.5*range, x_max+0.5*range]
    a_vals = [0.5 + 19.5 * i / n_steps for i in range(n_steps + 1)]
    b_vals = [x_min - 0.5 * x_range + 2.0 * x_range * i / n_steps for i in range(n_steps + 1)]
    for a in a_vals:
        for b in b_vals:
            rss = 0.0
            for xi, yi in zip(x_vals, y_vals):
                pred = 1.0 / (1.0 + math.exp(-a * (xi - b)))
                rss += (yi - pred) ** 2
            if rss < best_rss:
                best_rss = rss
    sigma2_hat = best_rss / n
    if sigma2_hat <= 0:
        sigma2_hat = 1e-12
    log_lik = -n / 2.0 * (math.log(2 * math.pi * sigma2_hat) + 1.0)
    n_params = 3  # a, b, sigma
    bic = -2.0 * log_lik + n_params * math.log(n)
    return bic


# ---------------------------------------------------------------------------
# Load retention data
# ---------------------------------------------------------------------------

_instrumentation_selftest()  # called after helpers are defined


def load_per_class_data() -> Dict[str, List[float]]:
    p = DATA / "exp_wave14_betB_shift_class_predictor_v1" / "metrics.json"
    with open(p) as f:
        m = json.load(f)
    data: Dict[str, List[float]] = {}
    for cls, info in m["summary"]["per_class"].items():
        data[cls] = info["values"]
    return data


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def run():
    t0 = time.time()
    out_dir = get_output_dir("wave14_betB_saddle_cascade_reanalysis_v1")

    data = load_per_class_data()
    print("Loaded per-class retention data:")
    for cls, vals in sorted(data.items(), key=lambda x: -sum(x[1])/len(x[1])):
        mean = sum(vals) / len(vals)
        print(f"  {cls}: n={len(vals)}, mean={mean:.4f}")

    # -----------------------------------------------------------------------
    # Test 1: 3-plateau discrete vs. sigmoid on corpus-type ordering
    # Use the 3 natural plateau groups:
    #   Group 1 (SAME): SAME_CORPUS_PRISTINE + COMPOUND_SAME_CORPUS
    #   Group 2 (STAGE4): REPLAY_SAME_CORPUS + NO_REPLAY_SAME_CORPUS + STAGE_4_COMPOUND
    #   Group 3 (DIFF): DIFF_CORPUS_2TASK
    # Ordering axis: 0.0 (SAME) -> 1.0 (STAGE4) -> 2.0 (DIFF)
    # -----------------------------------------------------------------------

    g1 = data.get("SAME_CORPUS_PRISTINE", []) + data.get("COMPOUND_SAME_CORPUS", [])
    g2 = (data.get("REPLAY_SAME_CORPUS", []) + data.get("NO_REPLAY_SAME_CORPUS", [])
          + data.get("STAGE_4_COMPOUND", []))
    g3 = data.get("DIFF_CORPUS_2TASK", [])

    print(f"\nGroup sizes: G1(SAME)={len(g1)}, G2(STAGE4/MID)={len(g2)}, G3(DIFF)={len(g3)}")

    all_vals = g1 + g2 + g3
    groups_for_bic = [g1, g2, g3]

    bic_discrete = discrete_bic(all_vals, groups_for_bic)

    # For sigmoid: assign x = group index (0, 1, 2) to each value
    x_vals = [0.0] * len(g1) + [1.0] * len(g2) + [2.0] * len(g3)
    bic_sigmoid = sigmoid_bic(x_vals, all_vals)

    delta_bic = bic_sigmoid - bic_discrete  # positive = discrete is better
    print(f"\nBIC analysis:")
    print(f"  Discrete 3-state BIC: {bic_discrete:.2f}")
    print(f"  Sigmoid BIC:          {bic_sigmoid:.2f}")
    print(f"  Delta BIC (sigmoid - discrete): {delta_bic:.2f}")
    print(f"  (positive delta = discrete model preferred)")

    # -----------------------------------------------------------------------
    # Test 2: plateau-height spacing formula
    # Cascade framework predicts: plateau_k = plateau_top - k/K * (plateau_top - plateau_bottom)
    # For K=3 classes, observed means ~ 0.94, 0.84, 0.63 (midpoints of groups)
    # Formula: equal spacing prediction
    # -----------------------------------------------------------------------

    mu1 = sum(g1) / len(g1) if g1 else float("nan")
    mu2 = sum(g2) / len(g2) if g2 else float("nan")
    mu3 = sum(g3) / len(g3) if g3 else float("nan")
    print(f"\nGroup means: G1={mu1:.4f}, G2={mu2:.4f}, G3={mu3:.4f}")

    # Equal-spacing prediction
    K = 3
    pred_spacing_top = mu1
    pred_spacing_bottom = mu3
    pred_mid = pred_spacing_top - (1.0 / (K - 1)) * (pred_spacing_top - pred_spacing_bottom)
    spacing_error = abs(mu2 - pred_mid)
    print(f"\nEqual-spacing formula prediction for G2: {pred_mid:.4f}")
    print(f"Observed G2 mean: {mu2:.4f}")
    print(f"Spacing formula error: {spacing_error:.4f} (threshold 0.05)")
    spacing_matches = spacing_error < 0.05

    # Also test: are gaps equal?
    gap_12 = mu1 - mu2
    gap_23 = mu2 - mu3
    gap_ratio = gap_12 / gap_23 if gap_23 > 0 else float("inf")
    print(f"Gap G1->G2: {gap_12:.4f}, Gap G2->G3: {gap_23:.4f}")
    print(f"Gap ratio (should be ~1.0 for equal spacing): {gap_ratio:.3f}")

    # -----------------------------------------------------------------------
    # Test 3: within-group variance vs between-group variance
    # Cascade framework predicts that parameter-variation (N, geometry, etc.) moves
    # points WITHIN a plateau group (high within-group variance relative to between-group
    # variance would indicate the groups are NOT truly discretized -- they'd be spread).
    # Empirically: if within-group std << between-group spacing, plateaus are real.
    # -----------------------------------------------------------------------

    within_stds = []
    for g, name in [(g1, "G1"), (g2, "G2"), (g3, "G3")]:
        if len(g) > 1:
            mu = sum(g) / len(g)
            std = math.sqrt(sum((v - mu) ** 2 for v in g) / (len(g) - 1))
        else:
            std = 0.0
        within_stds.append(std)
        print(f"Within-group std {name}: {std:.4f}")

    between_spacing = (mu1 - mu3) / 2.0  # average inter-group gap
    max_within_std = max(within_stds)
    discretization_ratio = between_spacing / max_within_std if max_within_std > 0 else float("inf")
    print(f"\nBetween-group spacing (avg): {between_spacing:.4f}")
    print(f"Max within-group std: {max_within_std:.4f}")
    print(f"Discretization ratio (higher = more discrete): {discretization_ratio:.2f}")
    discrete_signal_strong = discretization_ratio > 3.0  # 3-sigma-class separation

    # -----------------------------------------------------------------------
    # Verdict
    # -----------------------------------------------------------------------

    CASCADE_BIC_THRESHOLD = 2.0

    if delta_bic > CASCADE_BIC_THRESHOLD and spacing_matches:
        verdict = "CASCADE_PASS"
        verdict_msg = (
            f"CASCADE_PASS: discrete 3-state model preferred over sigmoid (delta_BIC={delta_bic:.1f} > 2). "
            f"Equal-spacing formula matches within {spacing_error:.3f} < 0.05. "
            f"Discretization ratio={discretization_ratio:.2f}. "
            f"Saddle-cascade framework is consistent with existing Bet B data."
        )
    elif delta_bic < -CASCADE_BIC_THRESHOLD:
        verdict = "CASCADE_FAIL"
        verdict_msg = (
            f"CASCADE_FAIL: sigmoid model preferred over discrete (delta_BIC={delta_bic:.1f} < -2). "
            f"Continuous framework better fits the retention data. Saddle-cascade rejected."
        )
    else:
        verdict = "CASCADE_INCONCLUSIVE"
        verdict_msg = (
            f"CASCADE_INCONCLUSIVE: |delta_BIC|={abs(delta_bic):.1f} <= 2. Both frameworks "
            f"statistically consistent. spacing_error={spacing_error:.3f}, "
            f"discretization_ratio={discretization_ratio:.2f}. "
            f"Full GPU overlap-fraction sweep needed for decisive test."
        )

    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 2),
        "summary": {
            "bic_discrete_3state": round(bic_discrete, 2),
            "bic_sigmoid": round(bic_sigmoid, 2),
            "delta_bic_sigmoid_minus_discrete": round(delta_bic, 2),
            "cascade_preferred": delta_bic > CASCADE_BIC_THRESHOLD,
            "group_means": {"G1_SAME": round(mu1, 4), "G2_MID": round(mu2, 4), "G3_DIFF": round(mu3, 4)},
            "group_sizes": {"G1": len(g1), "G2": len(g2), "G3": len(g3)},
            "equal_spacing_pred_G2": round(pred_mid, 4),
            "spacing_error": round(spacing_error, 4),
            "spacing_matches": spacing_matches,
            "gap_G1_G2": round(gap_12, 4),
            "gap_G2_G3": round(gap_23, 4),
            "gap_ratio": round(gap_ratio, 3),
            "discretization_ratio": round(discretization_ratio, 2),
            "discrete_signal_strong": discrete_signal_strong,
        },
        "config": {},
    }
    out_file = out_dir / "metrics.json"
    with open(out_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_file}")


if __name__ == "__main__":
    run()
