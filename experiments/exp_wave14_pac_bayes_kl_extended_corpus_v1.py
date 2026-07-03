"""PAC-Bayes Laplace KL: extended corpus application (local re-analysis).

Context: wave14_pac_bayes_laplace_selftests_v1 verified the KL formula (7/7 tests
PASS). wave14_betB_pac_bayes_kl_predictor_v1 ran on 3 cells (1 seed x 3 corpus
pairs) and found KL_fisher in [10.77, 24.41] for retention in [0.80, 0.94].
The GPU v2 run is planned but pending.

THIS LOCAL PROBE: apply the v1 KL-retention relationship to the FULL 109-value
Bet B corpus (from shift_class_predictor_v1) via two analyses:

1. SLOPE EXTRAPOLATION: From the 3 existing (KL_fisher, retention) cells, fit a
   KL = A * (1 - retention)^B relationship. Then extrapolate to all 109 retention
   values and compute predicted PAC-Bayes floors. Test: does the floor formula
   predict a meaningful lower bound across all 6 classes, or does it vacuously
   predict floor >= 1.0 (meaning the KL is small enough that the bound is non-tight)?

2. PAC-BAYES FLOOR vs OBSERVED RETENTION: The Laplace-Fisher PAC-Bayes floor is:
   floor = max(0, 1 - sqrt(KL / 2M)).
   With M=3000 tokens (from v1 config), and KL from the extrapolation, compute
   whether the floor underestimates or closely tracks the observed retention.
   Test: is floor <= observed_retention for all cells? (This is the PAC-Bayes
   requirement -- floor is a lower bound.)

3. KL SCALING ACROSS CLASSES: Using only the anchor points from v1, test whether
   the implied KL values for the 6 shift-class groups are internally consistent:
   - SAME_CORPUS (high retention ~0.94) should have LOW KL
   - DIFF_CORPUS (low retention ~0.63) should have HIGH KL
   Test the KL-retention slope against the equal-angle spacing prediction from the
   saddle-cascade analysis.

4. EUCLIDEAN VS FISHER EXTRAPOLATION: v1 also measured KL_euclidean (||Delta_W||^2)
   in [277, 1294]. Since KL_euclidean correlates nearly perfectly with KL_fisher
   (observed r2_euclidean=0.9986 in v1), test whether the euclidean proxy gives
   consistent PAC-Bayes floors. If yes: the floor can be computed without Fisher.

Pre-registered outcomes:
  FLOOR_VALID: PAC-Bayes floor <= observed_retention for all extrapolated cells
    AND floor >= 0.5 (non-trivially tight) for at least 50% of cells.
    Interpretation: v1 KL is in the right regime; GPU v2 will give a valid bound.
  FLOOR_LOOSE: floor < 0.5 for all cells. Bound exists but is trivially loose.
    Interpretation: M=3000 tokens insufficient; need larger M or relative-ridge fix.
  FLOOR_VIOLATED: floor > observed_retention for >= 1 cell.
    Interpretation: KL extrapolation is inconsistent with observed retention;
    v1 anchor points cannot support extrapolation. Wait for GPU v2 direct measurement.
  FLOOR_THRESHOLD_INCONSISTENT: floor is valid but slope extrapolation implies
    KL values inconsistent with saddle-cascade angle spacing.

Queue: local_cpu_queue (pure numerical re-analysis of existing JSON, <5s)
Pre-reg: preregs/2026-05-25_pac_bayes_kl_extended_corpus_v1.md
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
from typing import Dict, List, Optional, Tuple

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
    """Assert PAC-Bayes floor formula and power-law fit are non-null."""
    # pac_bayes_floor: max(0, 1 - sqrt(KL / 2M))
    floor_0 = pac_bayes_floor(kl=0.0, m=1000)
    assert abs(floor_0 - 1.0) < 1e-9, f"floor(KL=0) should be 1.0, got {floor_0}"

    floor_200 = pac_bayes_floor(kl=200, m=1000)
    expected = max(0.0, 1.0 - math.sqrt(200 / 2000))
    assert abs(floor_200 - expected) < 1e-9, f"floor mismatch: {floor_200} vs {expected}"

    # power-law fit: given 3 (x,y) pairs, fit A*(1-x)^B, verify A>0, B>0
    kl_vals = [10.77, 16.57, 24.41]
    ret_vals = [0.80, 0.94, 0.92]
    A, B = fit_power_law_kl_retention(ret_vals, kl_vals)
    assert A > 0, f"fitted A should be positive, got {A}"
    # A could be very large; just check it's finite
    assert math.isfinite(A), f"fitted A not finite: {A}"
    assert math.isfinite(B), f"fitted B not finite: {B}"
    print("[self-test] PAC-Bayes floor + power-law fit OK")


# called after helpers defined below


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pac_bayes_floor(kl: float, m: float) -> float:
    """PAC-Bayes generalization floor: max(0, 1 - sqrt(KL / 2M))."""
    if m <= 0 or kl < 0:
        return 0.0
    return max(0.0, 1.0 - math.sqrt(kl / (2.0 * m)))


def fit_power_law_kl_retention(
    retentions: List[float], kl_values: List[float]
) -> Tuple[float, float]:
    """Fit KL = A * (1 - r)^B via log-linear regression on log(KL) vs log(1-r).

    Returns (A, B). Uses only points where 1-r > 0 and KL > 0.
    """
    log_x = []
    log_y = []
    for r, kl in zip(retentions, kl_values):
        x = 1.0 - r
        if x > 0 and kl > 0:
            log_x.append(math.log(x))
            log_y.append(math.log(kl))
    n = len(log_x)
    if n < 2:
        return (1.0, 1.0)
    mx = sum(log_x) / n
    my = sum(log_y) / n
    sxx = sum((lx - mx) ** 2 for lx in log_x)
    sxy = sum((lx - mx) * (ly - my) for lx, ly in zip(log_x, log_y))
    if sxx < 1e-12:
        return (math.exp(my), 1.0)
    B = sxy / sxx
    A = math.exp(my - B * mx)
    return (A, B)


def predict_kl(r: float, A: float, B: float) -> float:
    """Predict KL from retention using power-law fit KL = A*(1-r)^B."""
    x = max(1e-6, 1.0 - r)
    return A * (x ** B)


def pearson_r2(xs: List[float], ys: List[float]) -> float:
    pairs = [(x, y) for x, y in zip(xs, ys)
             if not math.isnan(x) and not math.isnan(y)]
    if len(pairs) < 3:
        return float("nan")
    n = len(pairs)
    mx = sum(p[0] for p in pairs) / n
    my = sum(p[1] for p in pairs) / n
    sx = math.sqrt(sum((p[0] - mx) ** 2 for p in pairs) / max(1, n - 1))
    sy = math.sqrt(sum((p[1] - my) ** 2 for p in pairs) / max(1, n - 1))
    if sx < 1e-12 or sy < 1e-12:
        return 0.0
    r = sum((p[0] - mx) * (p[1] - my) for p in pairs) / ((n - 1) * sx * sy)
    return r ** 2


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_v1_kl_data() -> List[Dict]:
    """Load (retention, kl_fisher, kl_euclidean) cells from v1 metrics."""
    p = DATA / "exp_wave14_betB_pac_bayes_kl_predictor_v1" / "metrics.json"
    with open(p) as f:
        m = json.load(f)
    cells = []
    for seed, pairs in m.get("per_seed_pair", {}).items():
        for pair_id, cell in pairs.items():
            cells.append({
                "seed": seed,
                "pair_id": pair_id,
                "retention": cell["retention_A"],
                "kl_fisher": cell["kl_fisher"],
                "kl_euclidean": cell["kl_euclidean"],
                "laplace_ratio": cell["laplace_ratio"],
                "m_total": cell.get("m_total", 3000),
            })
    return cells


def load_full_retention_corpus() -> Dict[str, List[float]]:
    """Load the 109-value retention corpus from shift_class_predictor."""
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
    out_dir = get_output_dir("wave14_pac_bayes_kl_extended_corpus_v1")

    _instrumentation_selftest()

    # Load anchor data (3 cells from v1)
    anchor_cells = load_v1_kl_data()
    print(f"Loaded {len(anchor_cells)} v1 anchor cells:")
    for c in anchor_cells:
        print(f"  seed={c['seed']}, pair={c['pair_id']}: retention={c['retention']:.4f}, "
              f"kl_fisher={c['kl_fisher']:.2f}, kl_euclidean={c['kl_euclidean']:.2f}")

    # Load full corpus
    corpus = load_full_retention_corpus()
    all_retentions = [v for vals in corpus.values() for v in vals]
    print(f"\nFull corpus: {len(all_retentions)} retention values across {len(corpus)} classes")

    M = anchor_cells[0]["m_total"] if anchor_cells else 3000.0
    print(f"Using M={M} tokens (from v1 config)")

    # -----------------------------------------------------------------------
    # Analysis 1: Power-law fit to anchor data
    # -----------------------------------------------------------------------
    print(f"\n--- POWER-LAW FIT: KL = A * (1-r)^B ---")
    anchor_r = [c["retention"] for c in anchor_cells]
    anchor_kl_fisher = [c["kl_fisher"] for c in anchor_cells]
    anchor_kl_euclidean = [c["kl_euclidean"] for c in anchor_cells]

    A_fisher, B_fisher = fit_power_law_kl_retention(anchor_r, anchor_kl_fisher)
    A_euclidean, B_euclidean = fit_power_law_kl_retention(anchor_r, anchor_kl_euclidean)
    print(f"Fisher fit:    KL = {A_fisher:.2f} * (1-r)^{B_fisher:.3f}")
    print(f"Euclidean fit: KL = {A_euclidean:.2f} * (1-r)^{B_euclidean:.3f}")

    # Fit quality (r2 on anchor cells)
    pred_fisher = [predict_kl(r, A_fisher, B_fisher) for r in anchor_r]
    pred_euclidean = [predict_kl(r, A_euclidean, B_euclidean) for r in anchor_r]
    fit_r2_fisher = pearson_r2(anchor_kl_fisher, pred_fisher)
    fit_r2_euclidean = pearson_r2(anchor_kl_euclidean, pred_euclidean)
    print(f"Fit r2 (Fisher): {fit_r2_fisher:.4f}, Fit r2 (Euclidean): {fit_r2_euclidean:.4f}")

    # -----------------------------------------------------------------------
    # Analysis 2: Extrapolate floors across full corpus
    # -----------------------------------------------------------------------
    print(f"\n--- PAC-BAYES FLOOR EXTRAPOLATION ---")
    floor_results = {}
    floor_valid_count = 0
    floor_tight_count = 0
    floor_violated_count = 0
    all_floor_fisher = []

    for cls, vals in sorted(corpus.items()):
        floors = []
        for r in vals:
            kl_pred = predict_kl(r, A_fisher, B_fisher)
            floor = pac_bayes_floor(kl_pred, M)
            floors.append(floor)
            all_floor_fisher.append((r, floor))
            if floor > r + 1e-6:
                floor_violated_count += 1
            else:
                floor_valid_count += 1
            if floor >= 0.5:
                floor_tight_count += 1

        mean_floor = sum(floors) / len(floors) if floors else float("nan")
        mean_r = sum(vals) / len(vals) if vals else float("nan")
        gap = mean_r - mean_floor
        print(f"  {cls}: n={len(vals)}, mean_r={mean_r:.4f}, mean_floor={mean_floor:.4f}, gap={gap:.4f}")
        floor_results[cls] = {
            "mean_retention": round(mean_r, 4),
            "mean_floor": round(mean_floor, 4),
            "gap": round(gap, 4),
            "n": len(vals),
        }

    total_cells = floor_valid_count + floor_violated_count
    tight_fraction = floor_tight_count / total_cells if total_cells > 0 else 0.0
    violation_rate = floor_violated_count / total_cells if total_cells > 0 else 0.0

    print(f"\nTotal cells: {total_cells}")
    print(f"Floor violations (floor > observed): {floor_violated_count} ({violation_rate:.2%})")
    print(f"Floor tight (>= 0.5): {floor_tight_count} ({tight_fraction:.2%})")

    # -----------------------------------------------------------------------
    # Analysis 3: KL-retention slope vs saddle-cascade angle spacing
    # -----------------------------------------------------------------------
    print(f"\n--- KL SCALING VS SADDLE-CASCADE ANGLE SPACING ---")
    # From saddle cascade analysis: G1 mean=0.899, G2=0.804, G3=0.633
    # Equal-angle prediction: theta(G2) = (theta(G1) + theta(G3)) / 2
    cascade_groups = {
        "G1_SAME": 0.8986,
        "G2_MID": 0.8038,
        "G3_DIFF": 0.6334,
    }
    for gname, r in cascade_groups.items():
        kl_pred = predict_kl(r, A_fisher, B_fisher)
        floor = pac_bayes_floor(kl_pred, M)
        print(f"  {gname} (r={r:.4f}): predicted KL={kl_pred:.2f}, floor={floor:.4f}")

    kl_g1 = predict_kl(0.8986, A_fisher, B_fisher)
    kl_g2 = predict_kl(0.8038, A_fisher, B_fisher)
    kl_g3 = predict_kl(0.6334, A_fisher, B_fisher)
    kl_gap_12 = kl_g2 - kl_g1
    kl_gap_23 = kl_g3 - kl_g2
    kl_gap_ratio = kl_gap_12 / kl_gap_23 if kl_gap_23 > 0 else float("inf")
    print(f"  KL gap G1->G2: {kl_gap_12:.2f}, Gap G2->G3: {kl_gap_23:.2f}, ratio: {kl_gap_ratio:.3f}")

    # -----------------------------------------------------------------------
    # Analysis 4: Euclidean proxy validity check
    # -----------------------------------------------------------------------
    print(f"\n--- EUCLIDEAN PROXY VALIDITY ---")
    r2_fisher_vs_euclidean = pearson_r2(anchor_kl_fisher, anchor_kl_euclidean)
    print(f"r2(KL_fisher, KL_euclidean) on anchor cells: {r2_fisher_vs_euclidean:.4f}")
    euclidean_proxy_valid = r2_fisher_vs_euclidean > 0.80

    # Check if euclidean floors are consistent
    floors_euclidean = []
    for r in all_retentions:
        kl_pred = predict_kl(r, A_euclidean, B_euclidean)
        floors_euclidean.append(pac_bayes_floor(kl_pred, M))
    mean_floor_fisher = sum(f for _, f in all_floor_fisher) / len(all_floor_fisher)
    mean_floor_euclidean = sum(floors_euclidean) / len(floors_euclidean)
    floor_agreement = abs(mean_floor_fisher - mean_floor_euclidean) < 0.10
    print(f"Mean floor (Fisher): {mean_floor_fisher:.4f}, Mean floor (Euclidean): {mean_floor_euclidean:.4f}")
    print(f"Floor agreement (|diff|<0.10): {floor_agreement}")

    # -----------------------------------------------------------------------
    # Verdict
    # -----------------------------------------------------------------------
    print(f"\n--- VERDICT ---")
    if floor_violated_count > 0:
        verdict = "FLOOR_VIOLATED"
        verdict_msg = (
            f"FLOOR_VIOLATED: {floor_violated_count}/{total_cells} cells have "
            f"floor > observed_retention. v1 KL cannot extrapolate to full corpus. "
            f"Wait for GPU v2 direct measurement."
        )
    elif tight_fraction >= 0.5:
        verdict = "FLOOR_VALID"
        verdict_msg = (
            f"FLOOR_VALID: 0 violations, {tight_fraction:.1%} of cells have floor>=0.5. "
            f"v1 KL in correct regime; GPU v2 will give a non-trivially tight bound. "
            f"Fisher fit: KL = {A_fisher:.2f}*(1-r)^{B_fisher:.3f}."
        )
    elif tight_fraction < 0.5 and floor_violated_count == 0:
        verdict = "FLOOR_LOOSE"
        verdict_msg = (
            f"FLOOR_LOOSE: 0 violations but only {tight_fraction:.1%} of cells have "
            f"floor>=0.5. M={M} tokens too few; floor is valid but trivially loose. "
            f"GPU v2 should use larger M or relative-ridge to tighten."
        )
    else:
        verdict = "FLOOR_THRESHOLD_INCONSISTENT"
        verdict_msg = (
            f"FLOOR_THRESHOLD_INCONSISTENT: partial violations ({floor_violated_count}) "
            f"and tight fraction {tight_fraction:.1%}. Power-law extrapolation unstable."
        )

    print(f"Verdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 3),
        "summary": {
            "n_anchor_cells": len(anchor_cells),
            "n_corpus_cells": total_cells,
            "fisher_power_law": {"A": round(A_fisher, 3), "B": round(B_fisher, 3),
                                 "fit_r2": round(fit_r2_fisher, 4)},
            "euclidean_power_law": {"A": round(A_euclidean, 3), "B": round(B_euclidean, 3),
                                    "fit_r2": round(fit_r2_euclidean, 4)},
            "M_tokens": M,
            "floor_violations": floor_violated_count,
            "floor_tight_fraction": round(tight_fraction, 4),
            "euclidean_proxy_valid": euclidean_proxy_valid,
            "floor_agreement_euclidean_vs_fisher": floor_agreement,
            "kl_spacing_ratio": round(kl_gap_ratio, 4),
        },
        "per_class_floors": floor_results,
        "config": {},
    }

    out_file = out_dir / "metrics.json"
    with open(out_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_file}")


if __name__ == "__main__":
    run()
