"""5-corpus equal-spacing extension for Saad-Solla saddle-cascade framework.

CONTEXT: The 4-corpus HARD_PASS (v206; BIC_delta=-121.3, spacing_error=0.0035) confirmed
Saad-Solla equal-spacing arithmetic. The natural next falsifier: add a FIFTH plateau
(NO_REPLAY_SAME_CORPUS, mean~0.682) between G3_STAGE4 (~0.734) and G4_DIFF (~0.633).

Saad-Solla predicts: adding a 5th corpus class yields a 5th plateau with equal-spacing
preserved. If YES, the framework scales to N-plateau. If NO (5th plateau breaks spacing),
the 4-plateau structure has a hard limit.

DESIGN (exp_dev autonomy):
The existing shift_class_predictor data already has 5 distinguishable levels:
  G1_SAME: SAME_CORPUS_PRISTINE (mean~0.941) -- full overlap
  G2_REPLAY: REPLAY_SAME_CORPUS (mean~0.845) -- 3-stage partial WITH replay
  G3_STAGE4: STAGE_4_COMPOUND (mean~0.734) -- 4-stage partial, no replay
  G4_NOREPLAY: NO_REPLAY_SAME_CORPUS (mean~0.682) -- same-corpus, no replay (new 5th level)
  G5_DIFF: DIFF_CORPUS_2TASK (mean~0.633) -- disjoint corpora

The NO_REPLAY_SAME_CORPUS class (n=5) was excluded from the 4-corpus analysis as a
sensitivity check. It falls between G3 and G5 in mean retention. This is the natural 5th
level: it shares the same-corpus condition with G1/G2/G3 but has no replay mechanism.

NOTE: n=5 for G4_NOREPLAY is the boundary of statistical power. The spacing_error metric
is robust to small n (it only uses group means), but CI overlap tests will be wide.
Pre-registered HARD_PASS requires spacing_error < 0.05; CI distinctness is advisory.

Pre-registered bands (Saad-Solla 5-plateau extension):
  HARD_PASS: BIC_5state - BIC_4state < -10 AND spacing_error_5state < 0.05
             AND all 5 plateau heights ordered (mu1>mu2>mu3>mu4>mu5) AND
             G4_NOREPLAY statistically distinct from G3 and G5 (CI overlap < 50%)
  HARD_FAIL: BIC_5state > BIC_4state (4-state still preferred -- no 5th plateau) OR
             spacing_error_5state > 0.10 OR G4_NOREPLAY collapses into G3 or G5
  MIDDLE_BAND: BIC_5state - BIC_4state in (-10, 0) AND spacing_error_5state in [0.05, 0.10]
  INSTRUMENTATION_FAIL: n(G4_NOREPLAY) < 3 (insufficient stats for adjacent-pair CI test)

Note: BIC threshold is relaxed to -10 (vs -30 for 4-corpus) because the 5th class adds
only 5 samples -- the BIC improvement from splitting G4/G5 will be smaller. The
spacing_error is the primary criterion.

Queue: local_cpu_queue (pure re-analysis of existing JSON, < 30s)
Pre-reg: preregs/2026-05-26_wave14_betB_5corpus_equalspacing_v1.md
Parent: exp_wave14_betB_4corpus_equalspacing_v1.py (4-corpus HARD_PASS at v206)
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
# Statistical helpers (carried from 4-corpus script)
# ---------------------------------------------------------------------------

def group_mean_std(vals: List[float]) -> Tuple[float, float]:
    n = len(vals)
    if n == 0:
        return float("nan"), float("nan")
    mu = sum(vals) / n
    if n == 1:
        return mu, 0.0
    var = sum((v - mu) ** 2 for v in vals) / (n - 1)
    return mu, math.sqrt(var)


def ci_95(vals: List[float]) -> Tuple[float, float]:
    """Bootstrap-free 95% CI using t-distribution approximation."""
    n = len(vals)
    if n < 2:
        mu = vals[0] if vals else float("nan")
        return mu, mu
    mu, std = group_mean_std(vals)
    se = std / math.sqrt(n)
    t_table = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
               6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
               12: 2.179, 15: 2.131, 20: 2.086, 25: 2.060, 30: 2.042}
    if n - 1 in t_table:
        t = t_table[n - 1]
    elif n >= 30:
        t = 1.960
    else:
        t = 2.042
    margin = t * se
    return mu - margin, mu + margin


def ci_overlap_fraction(ci_a: Tuple[float, float], ci_b: Tuple[float, float]) -> float:
    lo_a, hi_a = ci_a
    lo_b, hi_b = ci_b
    overlap_lo = max(lo_a, lo_b)
    overlap_hi = min(hi_a, hi_b)
    if overlap_hi <= overlap_lo:
        return 0.0
    overlap = overlap_hi - overlap_lo
    width_a = hi_a - lo_a
    width_b = hi_b - lo_b
    min_width = min(width_a, width_b)
    if min_width <= 0:
        return 0.0
    return overlap / min_width


def t_test_p(vals_a: List[float], vals_b: List[float]) -> float:
    """Welch's t-test p-value (two-sided) approximation."""
    n_a, n_b = len(vals_a), len(vals_b)
    if n_a < 2 or n_b < 2:
        return 1.0
    mu_a = sum(vals_a) / n_a
    mu_b = sum(vals_b) / n_b
    var_a = sum((v - mu_a) ** 2 for v in vals_a) / (n_a - 1)
    var_b = sum((v - mu_b) ** 2 for v in vals_b) / (n_b - 1)
    se_diff = math.sqrt(var_a / n_a + var_b / n_b)
    if se_diff < 1e-12:
        return 0.0
    t_stat = abs(mu_a - mu_b) / se_diff
    df_num = (var_a / n_a + var_b / n_b) ** 2
    df_den = (var_a / n_a) ** 2 / (n_a - 1) + (var_b / n_b) ** 2 / (n_b - 1)
    df = df_num / df_den if df_den > 0 else n_a + n_b - 2
    return _t_pvalue_approx(t_stat, df)


def _t_pvalue_approx(t: float, df: float) -> float:
    z = abs(t)
    t_coef = 1.0 / (1.0 + 0.2316419 * z)
    poly = t_coef * (0.319381530 + t_coef * (-0.356563782 + t_coef * (
        1.781477937 + t_coef * (-1.821255978 + t_coef * 1.330274429))))
    phi = math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)
    p_one_tail = phi * poly
    if df < 30:
        correction = 1.0 + 1.0 / (2.0 * df)
        p_one_tail = min(p_one_tail * correction, 0.5)
    return 2.0 * p_one_tail


def discrete_bic(all_vals: List[float], groups: List[List[float]]) -> float:
    """BIC for a K-group step function model."""
    n = len(all_vals)
    k = len(groups)
    if n <= k + 1:
        return float("inf")
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
    n_params = k + 1
    return -2.0 * log_lik + n_params * math.log(n)


def equal_spacing_error(means: List[float]) -> float:
    """L2 error from perfect equal spacing given endpoints."""
    K = len(means)
    if K < 2:
        return 0.0
    pred = [means[0] - (k / (K - 1)) * (means[0] - means[-1]) for k in range(K)]
    err = math.sqrt(sum((obs - p) ** 2 for obs, p in zip(means, pred)) / K)
    return err


# ---------------------------------------------------------------------------
# Instrumentation self-test
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert all statistical helpers and data dependencies are valid."""
    # Test 1: BIC 5-state vs 4-state on synthetic equal-spaced data
    g1 = [0.94 + 0.005 * i for i in range(5)]
    g2 = [0.80 + 0.005 * i for i in range(5)]
    g3 = [0.67 + 0.005 * i for i in range(5)]
    g4 = [0.55 + 0.005 * i for i in range(5)]
    g5 = [0.42 + 0.005 * i for i in range(5)]
    all_vals = g1 + g2 + g3 + g4 + g5
    bic5 = discrete_bic(all_vals, [g1, g2, g3, g4, g5])
    bic4 = discrete_bic(all_vals, [g1, g2, g3, g4 + g5])
    assert bic5 < bic4, f"Selftest 1 FAIL: 5-state BIC={bic5:.2f} not < 4-state BIC={bic4:.2f}"
    print("[selftest] 1/5 BIC 5-state preferred for equal-spaced data OK")

    # Test 2: equal-spacing error is 0 for 5-point perfect equal spacing
    means_perf = [0.9, 0.7, 0.5, 0.3, 0.1]
    err_perf = equal_spacing_error(means_perf)
    assert err_perf < 1e-9, f"Selftest 2 FAIL: err={err_perf}"
    print("[selftest] 2/5 equal_spacing_error perfect 5-point OK")

    # Test 3: equal-spacing error is non-zero when 4th point is off
    means_off = [0.9, 0.7, 0.5, 0.25, 0.1]  # G4 should be 0.3 for equal-spacing
    err_off = equal_spacing_error(means_off)
    assert err_off > 0.01, f"Selftest 3 FAIL: err={err_off}"
    print("[selftest] 3/5 equal_spacing_error non-zero for 5-point non-equal OK")

    # Test 4: prerequisite data exists and has the 5 needed classes
    src = DATA / "exp_wave14_betB_shift_class_predictor_v1" / "metrics.json"
    assert src.exists(), f"Selftest 4 FAIL: prerequisite data not found at {src}"
    with open(src) as f:
        m = json.load(f)
    classes = set(m["summary"]["per_class"].keys())
    required = {"SAME_CORPUS_PRISTINE", "REPLAY_SAME_CORPUS", "STAGE_4_COMPOUND",
                "NO_REPLAY_SAME_CORPUS", "DIFF_CORPUS_2TASK"}
    missing = required - classes
    assert not missing, f"Selftest 4 FAIL: missing classes {missing}"
    print(f"[selftest] 4/5 prerequisite data has all 5 required classes OK")

    # Test 5: G4_NOREPLAY has enough data points (n >= 3)
    n4 = len(m["summary"]["per_class"]["NO_REPLAY_SAME_CORPUS"]["values"])
    assert n4 >= 3, f"Selftest 5 FAIL: G4_NOREPLAY has only n={n4} < 3"
    print(f"[selftest] 5/5 G4_NOREPLAY n={n4} >= 3 (INSTRUMENTATION_FAIL threshold) OK")
    print("[selftest] All 5 self-tests passed")


_instrumentation_selftest()


# ---------------------------------------------------------------------------
# Load per-class data
# ---------------------------------------------------------------------------

def load_per_class_data() -> Dict[str, List[float]]:
    p = DATA / "exp_wave14_betB_shift_class_predictor_v1" / "metrics.json"
    with open(p) as f:
        m = json.load(f)
    return {cls: info["values"] for cls, info in m["summary"]["per_class"].items()}


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def run():
    t0 = time.time()
    out_dir = get_output_dir("wave14_betB_5corpus_equalspacing_v1")

    data = load_per_class_data()
    print("Loaded per-class retention data:")
    for cls, vals in sorted(data.items(), key=lambda x: -sum(x[1]) / len(x[1])):
        mu, std = group_mean_std(vals)
        print(f"  {cls}: n={len(vals)}, mean={mu:.4f}, std={std:.4f}")

    # 5-class grouping
    g1 = data.get("SAME_CORPUS_PRISTINE", [])
    g2 = data.get("REPLAY_SAME_CORPUS", [])
    g3 = data.get("STAGE_4_COMPOUND", [])
    g4 = data.get("NO_REPLAY_SAME_CORPUS", [])   # NEW 5th level
    g5 = data.get("DIFF_CORPUS_2TASK", [])

    for label, g in [("G1_SAME", g1), ("G2_REPLAY", g2), ("G3_STAGE4", g3),
                     ("G4_NOREPLAY", g4), ("G5_DIFF", g5)]:
        assert len(g) > 0, f"INSTRUMENTATION-FAIL: group {label} is empty"

    if len(g4) < 3:
        print("INSTRUMENTATION_FAIL: G4_NOREPLAY n < 3 -- insufficient for reliable CI test")
        metrics = {
            "verdict": "INSTRUMENTATION_FAIL",
            "verdict_msg": f"INSTRUMENTATION_FAIL: G4_NOREPLAY n={len(g4)} < 3 threshold",
            "elapsed_s": round(time.time() - t0, 3),
            "summary": {"n_G4": len(g4)},
            "config": {"design": "5-class re-analysis", "issue": "insufficient G4 samples"},
        }
        out_file = out_dir / "metrics.json"
        with open(out_file, "w") as f:
            json.dump(metrics, f, indent=2)
        return

    mu1, std1 = group_mean_std(g1)
    mu2, std2 = group_mean_std(g2)
    mu3, std3 = group_mean_std(g3)
    mu4, std4 = group_mean_std(g4)
    mu5, std5 = group_mean_std(g5)
    means = [mu1, mu2, mu3, mu4, mu5]
    labels = ["G1_SAME", "G2_REPLAY", "G3_STAGE4", "G4_NOREPLAY", "G5_DIFF"]
    groups_list = [g1, g2, g3, g4, g5]

    print(f"\n5-class means: G1={mu1:.4f}, G2={mu2:.4f}, G3={mu3:.4f}, G4={mu4:.4f}, G5={mu5:.4f}")
    print(f"5-class sizes: G1={len(g1)}, G2={len(g2)}, G3={len(g3)}, G4={len(g4)}, G5={len(g5)}")

    # Check monotone ordering (required for equal-spacing)
    ordered = all(means[i] > means[i + 1] for i in range(len(means) - 1))
    print(f"\nMonotone descending order: {ordered}")
    if not ordered:
        for i in range(len(means) - 1):
            if means[i] <= means[i + 1]:
                print(f"  ORDER VIOLATION: {labels[i]}={means[i]:.4f} <= {labels[i+1]}={means[i+1]:.4f}")

    # 95% CIs and adjacent-pair distinctness
    cis = [ci_95(g) for g in groups_list]
    print("\n95% CIs:")
    for lbl, ci in zip(labels, cis):
        print(f"  {lbl}: [{ci[0]:.4f}, {ci[1]:.4f}]")

    adjacent_distinctness = []
    for i in range(len(cis) - 1):
        overlap = ci_overlap_fraction(cis[i], cis[i + 1])
        distinct = overlap < 0.5
        adjacent_distinctness.append({
            "pair": f"{labels[i]}/{labels[i+1]}", "overlap": round(overlap, 3),
            "distinct": distinct
        })
        print(f"  CI overlap {labels[i]}/{labels[i+1]}: {overlap:.3f} ({'distinct' if distinct else 'OVERLAPPING'})")

    # t-test p-values between adjacent groups
    ttest_results = []
    for i in range(len(groups_list) - 1):
        p = t_test_p(groups_list[i], groups_list[i + 1])
        ttest_results.append({"pair": adjacent_distinctness[i]["pair"], "p_value": round(p, 4)})
        print(f"  t-test p-value {labels[i]}/{labels[i+1]}: {p:.4f}")

    # Focus test: G4_NOREPLAY distinctness from neighbors (new 5th level)
    g4_distinct_from_g3 = adjacent_distinctness[2]["distinct"]   # G3/G4
    g4_distinct_from_g5 = adjacent_distinctness[3]["distinct"]   # G4/G5
    g4_distinct = g4_distinct_from_g3 and g4_distinct_from_g5
    print(f"\nG4_NOREPLAY distinct from G3: {g4_distinct_from_g3}")
    print(f"G4_NOREPLAY distinct from G5: {g4_distinct_from_g5}")

    # BIC: 5-state vs 4-state vs 3-state vs sigmoid
    all_vals_5 = g1 + g2 + g3 + g4 + g5
    bic_5state = discrete_bic(all_vals_5, [g1, g2, g3, g4, g5])
    # 4-state: merge G4+G5 (collapses the new level)
    bic_4state = discrete_bic(all_vals_5, [g1, g2, g3, g4 + g5])
    # 3-state: merge G2+G3+G4 (old 3-class baseline)
    bic_3state = discrete_bic(all_vals_5, [g1, g2 + g3 + g4, g5])

    delta_5_vs_4 = bic_5state - bic_4state   # negative = 5-state preferred
    delta_5_vs_3 = bic_5state - bic_3state   # comparison to older baseline

    print(f"\nBIC analysis:")
    print(f"  5-state BIC: {bic_5state:.2f}")
    print(f"  4-state BIC: {bic_4state:.2f}")
    print(f"  3-state BIC: {bic_3state:.2f}")
    print(f"  Delta 5-state vs 4-state: {delta_5_vs_4:.2f} (negative = 5-state preferred)")
    print(f"  Delta 5-state vs 3-state: {delta_5_vs_3:.2f}")

    # Equal-spacing analysis
    spacing_err_5 = equal_spacing_error(means)
    print(f"\nEqual-spacing error (5 groups): {spacing_err_5:.4f}")

    # Predict all interior values from equal spacing (G1 and G5 as endpoints)
    for k, lbl in enumerate(labels):
        pred = mu1 - (k / 4) * (mu1 - mu5)
        print(f"  {lbl}: pred={pred:.4f}, obs={means[k]:.4f}, err={abs(means[k]-pred):.4f}")

    # Gap ratios
    gaps = [means[i] - means[i + 1] for i in range(len(means) - 1)]
    print(f"\nGap sizes:")
    for i, (lbl_a, lbl_b) in enumerate(zip(labels[:-1], labels[1:])):
        print(f"  {lbl_a}->{lbl_b}: {gaps[i]:.4f}")
    # Focus: are all 4 gaps comparable?
    mean_gap = sum(gaps) / len(gaps)
    max_gap_dev = max(abs(g - mean_gap) / mean_gap for g in gaps if mean_gap > 0)
    print(f"  Mean gap: {mean_gap:.4f}, max relative deviation: {max_gap_dev:.3f}")

    # 4-corpus spacing error for comparison
    means_4 = [mu1, mu2, mu3, mu5]   # original 4-class grouping (without G4)
    spacing_err_4_baseline = equal_spacing_error(means_4)
    print(f"\n4-corpus spacing error (without G4_NOREPLAY, for comparison): {spacing_err_4_baseline:.4f}")
    print(f"5-corpus spacing error with G4_NOREPLAY: {spacing_err_5:.4f}")

    # Verdict
    HP_BIC_DELTA = -10.0         # relaxed vs -30 for 4-corpus (n_G4=5 limits BIC improvement)
    HP_SPACING_ERROR = 0.05
    HF_SPACING_ERROR = 0.10

    all_distinct = all(d["distinct"] for d in adjacent_distinctness)

    hard_pass = (
        delta_5_vs_4 < HP_BIC_DELTA and
        spacing_err_5 < HP_SPACING_ERROR and
        ordered and
        g4_distinct
    )

    hard_fail = (
        delta_5_vs_4 > 0 or
        spacing_err_5 > HF_SPACING_ERROR or
        not ordered or
        not g4_distinct
    )

    middle_band = not hard_pass and not hard_fail

    if hard_pass:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: 5-state model preferred over 4-state (BIC_delta={delta_5_vs_4:.1f} < -10). "
            f"Equal-spacing error={spacing_err_5:.4f} < 0.05. "
            f"Monotone ordering: {ordered}. G4_NOREPLAY distinct from G3 and G5: {g4_distinct}. "
            f"Saad-Solla equal-spacing arithmetic preserves to 5-corpus extension. "
            f"Framework generalizes to N-plateau structure."
        )
    elif hard_fail:
        verdict = "HARD_FAIL"
        fail_reasons = []
        if delta_5_vs_4 > 0:
            fail_reasons.append(f"4-state still preferred (BIC_delta={delta_5_vs_4:.1f} > 0)")
        if spacing_err_5 > HF_SPACING_ERROR:
            fail_reasons.append(f"spacing_error={spacing_err_5:.4f} > 0.10")
        if not ordered:
            fail_reasons.append(f"monotone ordering violated")
        if not g4_distinct:
            fail_reasons.append(f"G4_NOREPLAY not distinct from neighbors")
        verdict_msg = (
            f"HARD_FAIL: Saad-Solla 5-plateau equal-spacing does not hold. "
            f"Reasons: {'; '.join(fail_reasons)}. "
            f"4-plateau structure has a limit: the REPLAY/NO_REPLAY boundary is not a "
            f"distinct saddle-cascade plateau level. Framework restricts to exactly 4 plateaus."
        )
    else:
        verdict = "MIDDLE_BAND"
        # Explain which criterion(a) prevented HARD_PASS
        reasons = []
        if delta_5_vs_4 >= HP_BIC_DELTA:
            reasons.append(f"BIC_delta={delta_5_vs_4:.1f} not < {HP_BIC_DELTA} (borderline)")
        if spacing_err_5 >= HP_SPACING_ERROR:
            reasons.append(f"spacing_error={spacing_err_5:.4f} not < {HP_SPACING_ERROR}")
        if not ordered:
            reasons.append("monotone ordering violated")
        if not g4_distinct:
            reasons.append("G4_NOREPLAY not distinct from neighbors")
        verdict_msg = (
            f"MIDDLE_BAND: criteria not all met for HARD_PASS. "
            f"Blocking: {'; '.join(reasons) if reasons else 'unknown'}. "
            f"Note: spacing_error={spacing_err_5:.4f} {'PASSES' if spacing_err_5 < HP_SPACING_ERROR else 'FAILS'} < 0.05. "
            f"G4_NOREPLAY distinct from both neighbors: {g4_distinct}. "
            f"Recommend full-scale 5-corpus GPU experiment for clean BIC test (new data, not re-analysis)."
        )

    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 3),
        "summary": {
            "group_means": {lbl: round(mu, 4) for lbl, mu in zip(labels, means)},
            "group_sizes": {lbl: len(g) for lbl, g in zip(labels, groups_list)},
            "bic_5state": round(bic_5state, 2),
            "bic_4state": round(bic_4state, 2),
            "bic_3state": round(bic_3state, 2),
            "delta_bic_5vs4": round(delta_5_vs_4, 2),
            "delta_bic_5vs3": round(delta_5_vs_3, 2),
            "spacing_error_5state": round(spacing_err_5, 4),
            "spacing_error_4state_baseline": round(spacing_err_4_baseline, 4),
            "gaps": {f"{a}->{b}": round(g, 4) for a, b, g in zip(labels[:-1], labels[1:], gaps)},
            "mean_gap": round(mean_gap, 4),
            "max_gap_relative_deviation": round(max_gap_dev, 3),
            "ordered": ordered,
            "g4_distinct_from_g3": g4_distinct_from_g3,
            "g4_distinct_from_g5": g4_distinct_from_g5,
            "all_adjacent_distinct": all_distinct,
            "adjacent_ci_overlaps": adjacent_distinctness,
            "ttest_p_values": ttest_results,
        },
        "config": {
            "design": "5-class re-analysis of existing shift_class_predictor data",
            "G1": "SAME_CORPUS_PRISTINE",
            "G2": "REPLAY_SAME_CORPUS",
            "G3": "STAGE_4_COMPOUND",
            "G4": "NO_REPLAY_SAME_CORPUS (NEW 5th level)",
            "G5": "DIFF_CORPUS_2TASK",
            "data_source": "data/exp_wave14_betB_shift_class_predictor_v1/metrics.json",
            "parent_experiment": "exp_wave14_betB_4corpus_equalspacing_v1.py",
            "note": "G4_NOREPLAY n=5 is the boundary of statistical power; CI tests advisory",
        },
    }

    out_file = out_dir / "metrics.json"
    with open(out_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_file}")


if __name__ == "__main__":
    run()
