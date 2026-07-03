"""Bet B Alt 1 follow-up: 2-tier coarse taxonomy separation analysis.

Context: Alt 1 alt_taxonomy_sweep_v1 found MIDDLE (silhouette=0.584 at K=4; 6/6 non-overlapping
CIs). The K=4 result is GROUP-LEVEL CONFIRMED (v206) with the 4-corpus equal-spacing HARD_PASS.
But within-cell granularity is still Yellow-PARTIAL (silhouette=0.584 in MIDDLE band).

This analysis tests the COARSEST meaningful taxonomy: 2-tier (HIGH vs LOW) at 5 levels:

  HIGH tier: {SAME_CORPUS_PRISTINE, COMPOUND_SAME_CORPUS, REPLAY_SAME_CORPUS, NO_REPLAY_SAME_CORPUS}
             empirical means: 0.925, 0.885, 0.845, 0.838 (all > 0.80)
  LOW tier:  {STAGE_4_COMPOUND, DIFF_CORPUS_2TASK}
             empirical means: 0.734, 0.633 (all < 0.75)

Also tests 3-tier collapse:
  HIGH:  {SAME_CORPUS_PRISTINE, COMPOUND_SAME_CORPUS} (mean ~0.90-0.93)
  MID:   {REPLAY_SAME_CORPUS, NO_REPLAY_SAME_CORPUS, STAGE_4_COMPOUND} (mean ~0.73-0.85)
  LOW:   {DIFF_CORPUS_2TASK} (mean ~0.63)

Pure re-analysis: reads from data/exp_wave14_betB_shift_class_full_replication_v1/metrics.json.
Zero new compute. Expected runtime: < 5s.

PRE-REGISTERED BANDS:
  HARD-PASS (2-tier clearly separable):
    - 2-tier silhouette >= 0.70 AND 2-tier CI non-overlap: HIGH_ci_lo > LOW_ci_hi AND KW p < 0.001
    -> Coarsest taxonomy is the defensible cap (Bet B retention is binary-classifiable)

  HARD-FAIL (even 2-tier overlaps):
    - 2-tier CI overlap > 0 (HIGH_ci_lo <= LOW_ci_hi)
    -> Bet B retention cannot be classified even at 2 levels; group-level signal only

  MIDDLE:
    - HIGH_ci_lo > LOW_ci_hi AND silhouette in [0.40, 0.70)
    -> Separation exists but moderate; consider production-N replication

SELF-TEST:
  1. CI computation: ci_lo < ci_hi for n >= 2
  2. Silhouette on known 2-cluster data should be > 0.7
  3. Data loading: full replication metrics.json must exist and contain per_class keys

Queue: remote_cpu_queue (pure JSON re-analysis, < 5s)
Pre-reg: preregs/2026-05-26_wave14_betB_2tier_coarse_analysis_v1.md

Per [[feedback-ascii-only-in-scripts]]: ASCII-only in print/verdict_msg.
Per [[feedback-envelope-expansion-fail-bands]]: bands pre-registered.
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

# ---- 2-tier mapping ----
SIX_TO_TWO = {
    "SAME_CORPUS_PRISTINE": "HIGH",
    "COMPOUND_SAME_CORPUS": "HIGH",
    "REPLAY_SAME_CORPUS": "HIGH",
    "NO_REPLAY_SAME_CORPUS": "HIGH",
    "STAGE_4_COMPOUND": "LOW",
    "DIFF_CORPUS_2TASK": "LOW",
}

# ---- 3-tier mapping ----
SIX_TO_THREE = {
    "SAME_CORPUS_PRISTINE": "HIGH",
    "COMPOUND_SAME_CORPUS": "HIGH",
    "REPLAY_SAME_CORPUS": "MID",
    "NO_REPLAY_SAME_CORPUS": "MID",
    "STAGE_4_COMPOUND": "MID",
    "DIFF_CORPUS_2TASK": "LOW",
}

TIER_ORDER_2 = ["HIGH", "LOW"]
TIER_ORDER_3 = ["HIGH", "MID", "LOW"]

# Pre-registered thresholds
SILHOUETTE_HARD_PASS = 0.70
SILHOUETTE_MIDDLE_LO = 0.40
KW_P_HARD_PASS = 0.001


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required keys: {missing}")


def compute_ci(vals: List[float], z: float = 1.96) -> Tuple[float, float]:
    n = len(vals)
    if n == 0:
        return float("nan"), float("nan")
    if n == 1:
        return vals[0], vals[0]
    mean = sum(vals) / n
    var = sum((v - mean) ** 2 for v in vals) / (n - 1)
    se = math.sqrt(var / n)
    return mean - z * se, mean + z * se


def compute_silhouette(clusters: Dict[str, List[float]], tier_order: List[str]) -> float:
    """Compute silhouette width for the given cluster assignment."""
    all_sils = []
    for label, vals in clusters.items():
        if not vals:
            continue
        # Mean within-cluster distance
        if len(vals) > 1:
            mean_self = sum(vals) / len(vals)
            a_i_list = [abs(v - mean_self) for v in vals]
        else:
            a_i_list = [0.0]

        # Mean nearest-cluster distance
        other_means = []
        for other_label, other_vals in clusters.items():
            if other_label == label or not other_vals:
                continue
            other_means.append(sum(other_vals) / len(other_vals))

        if not other_means:
            continue

        cluster_mean = sum(vals) / len(vals)
        b_i_list = [min(abs(cluster_mean - m) for m in other_means)] * len(vals)

        for a_i, b_i in zip(a_i_list, b_i_list):
            s = (b_i - a_i) / max(a_i, b_i, 1e-10)
            all_sils.append(s)

    return sum(all_sils) / len(all_sils) if all_sils else 0.0


def kruskal_wallis_p(groups: List[List[float]]) -> float:
    """Approximate Kruskal-Wallis p-value (chi-sq approximation)."""
    all_vals = []
    for g in groups:
        all_vals.extend(g)
    N = len(all_vals)
    if N < 3:
        return 1.0

    # Rank all values
    sorted_vals = sorted(enumerate(all_vals), key=lambda x: x[1])
    ranks = [0.0] * N
    i = 0
    while i < N:
        j = i
        while j < N and sorted_vals[j][1] == sorted_vals[i][1]:
            j += 1
        avg_rank = (i + j + 1) / 2.0  # 1-indexed average rank
        for k in range(i, j):
            ranks[sorted_vals[k][0]] = avg_rank
        i = j

    # H statistic
    k = len(groups)
    H = 0.0
    idx = 0
    for g in groups:
        n_i = len(g)
        if n_i == 0:
            idx += n_i
            continue
        mean_rank = sum(ranks[idx + j] for j in range(n_i)) / n_i
        H += n_i * (mean_rank - (N + 1) / 2.0) ** 2
        idx += n_i
    H = 12.0 * H / (N * (N + 1))

    # Chi-sq approximation with df = k-1
    df = k - 1
    if df <= 0:
        return 1.0
    # Survival function approximation for chi-sq
    # Use simple gamma regularized incomplete: p ~ 1 - regularized_gamma(df/2, H/2)
    # Rough approximation sufficient for categorical decision
    try:
        import math
        x = H / 2.0
        a = df / 2.0
        # Log-gamma function
        lng = math.lgamma(a)
        # Regularized incomplete gamma (upper tail) via series approximation
        # For decision purposes, use chi-sq critical values:
        # df=1: chi=3.84 (p=0.05), chi=10.83 (p=0.001)
        # df=2: chi=5.99 (p=0.05), chi=13.82 (p=0.001)
        CHI_CRIT = {1: (3.84, 6.63, 10.83), 2: (5.99, 9.21, 13.82)}
        crits = CHI_CRIT.get(df, CHI_CRIT[2])
        if H > crits[2]:
            return 0.0005   # p < 0.001
        elif H > crits[1]:
            return 0.005    # p < 0.01
        elif H > crits[0]:
            return 0.025    # p < 0.05
        else:
            return 0.10     # p > 0.05
    except Exception:
        return 0.10


def analyze_taxonomy(
    per_class_data: dict,
    mapping: Dict[str, str],
    tier_order: List[str]
) -> dict:
    """Analyze a given taxonomy mapping on per_class_data."""
    tiers: Dict[str, List[float]] = {t: [] for t in tier_order}
    for cls_name, cls_data in per_class_data.items():
        tier = mapping.get(cls_name)
        if tier is None:
            continue
        vals = cls_data.get("values", [])
        if not vals:
            # fallback to mean if values not available
            mean = cls_data.get("mean_retention_A", cls_data.get("mean"))
            if mean is not None:
                vals = [float(mean)]
        tiers[tier].extend([float(v) for v in vals])

    # Per-tier stats
    tier_stats = {}
    for tier in tier_order:
        vals = tiers[tier]
        n = len(vals)
        if n == 0:
            tier_stats[tier] = {"n": 0, "mean": None, "ci_lo": None, "ci_hi": None}
            continue
        mean = sum(vals) / n
        ci_lo, ci_hi = compute_ci(vals)
        tier_stats[tier] = {
            "n": n,
            "mean": round(mean, 4),
            "ci_lo": round(ci_lo, 4),
            "ci_hi": round(ci_hi, 4),
        }

    # Silhouette
    silhouette = compute_silhouette(tiers, tier_order)

    # CI non-overlap count
    n_nonoverlap = 0
    for i in range(len(tier_order)):
        for j in range(i + 1, len(tier_order)):
            t_i = tier_order[i]
            t_j = tier_order[j]
            si = tier_stats.get(t_i, {})
            sj = tier_stats.get(t_j, {})
            lo_i = si.get("ci_lo")
            hi_i = si.get("ci_hi")
            lo_j = sj.get("ci_lo")
            hi_j = sj.get("ci_hi")
            if None in (lo_i, hi_i, lo_j, hi_j):
                continue
            # Non-overlapping if one interval is entirely above/below the other
            if hi_i < lo_j or hi_j < lo_i:
                n_nonoverlap += 1

    total_pairs = len(tier_order) * (len(tier_order) - 1) // 2

    # KW p-value
    groups = [tiers[t] for t in tier_order if tiers[t]]
    kw_p = kruskal_wallis_p(groups) if len(groups) >= 2 else 1.0

    return {
        "tier_stats": tier_stats,
        "silhouette": round(silhouette, 4),
        "n_nonoverlap": n_nonoverlap,
        "total_pairs": total_pairs,
        "kw_p": kw_p,
    }


# ---- self-tests ----
def self_test():
    errors = []

    # Self-test 1: CI computation
    ci_lo, ci_hi = compute_ci([0.1, 0.12, 0.11, 0.09])
    if not (ci_lo < ci_hi):
        errors.append(f"Self-test 1 FAIL: CI not ordered: [{ci_lo}, {ci_hi}]")

    # Self-test 2: silhouette on well-separated 2-cluster data
    clusters = {"HIGH": [0.85, 0.86, 0.87, 0.88], "LOW": [0.60, 0.61, 0.62, 0.63]}
    sil = compute_silhouette(clusters, ["HIGH", "LOW"])
    if sil < 0.70:
        errors.append(f"Self-test 2 FAIL: silhouette on well-separated data = {sil:.3f} (expected > 0.70)")

    # Self-test 3: data file check (checked at runtime, logged here as design note)
    # Actual file existence checked in run() before analyze_taxonomy

    if errors:
        for e in errors:
            print(f"[SELF-TEST] {e}", flush=True)
        raise AssertionError(f"Self-tests FAILED ({len(errors)} errors)")
    print(f"[SELF-TEST] All 2 structural self-tests passed (data check in run())", flush=True)


def run():
    t0 = time.monotonic()
    print(f"[2tier_coarse_analysis] loading full replication data", flush=True)

    # Load source data
    source_path = DATA / "exp_wave14_betB_shift_class_full_replication_v1" / "metrics.json"
    if not source_path.exists():
        metrics = {
            "verdict": "INSTRUMENTATION_FAIL",
            "verdict_msg": f"Source data not found at {source_path}. Run wave14_betB_shift_class_full_replication_v1 first.",
            "elapsed_s": round(time.monotonic() - t0, 3),
            "summary": {},
            "config": {"source": str(source_path)},
        }
        out_dir = get_output_dir("wave14_betB_2tier_coarse_analysis_v1")
        with open(out_dir / "metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)
        print(f"[SELF-TEST 3] FAIL: {source_path} not found", flush=True)
        return metrics
    print(f"[SELF-TEST 3] PASS: {source_path} found", flush=True)

    full_rep = json.load(open(source_path))
    per_class = full_rep.get("summary", {}).get("per_class", {})
    if not per_class:
        metrics = {
            "verdict": "INSTRUMENTATION_FAIL",
            "verdict_msg": "No per_class data in source metrics.json.",
            "elapsed_s": round(time.monotonic() - t0, 3),
            "summary": {},
            "config": {"source": str(source_path)},
        }
        out_dir = get_output_dir("wave14_betB_2tier_coarse_analysis_v1")
        with open(out_dir / "metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)
        return metrics

    print(f"[2tier_coarse_analysis] found {len(per_class)} class entries: {list(per_class.keys())}", flush=True)

    # Analyze 2-tier taxonomy
    result_2tier = analyze_taxonomy(per_class, SIX_TO_TWO, TIER_ORDER_2)
    print(f"[2tier] silhouette={result_2tier['silhouette']:.4f} nonoverlap={result_2tier['n_nonoverlap']}/{result_2tier['total_pairs']} kw_p={result_2tier['kw_p']:.6f}", flush=True)
    for tier, stats in result_2tier["tier_stats"].items():
        if stats.get("n"):
            print(f"  {tier}: mean={stats['mean']:.4f} CI=[{stats['ci_lo']:.4f}, {stats['ci_hi']:.4f}] n={stats['n']}", flush=True)

    # Analyze 3-tier taxonomy
    result_3tier = analyze_taxonomy(per_class, SIX_TO_THREE, TIER_ORDER_3)
    print(f"[3tier] silhouette={result_3tier['silhouette']:.4f} nonoverlap={result_3tier['n_nonoverlap']}/{result_3tier['total_pairs']} kw_p={result_3tier['kw_p']:.6f}", flush=True)

    # Verdict based on 2-tier (primary) and 3-tier (secondary)
    s2 = result_2tier["silhouette"]
    n2 = result_2tier["n_nonoverlap"]
    t2 = result_2tier["total_pairs"]
    kw2 = result_2tier["kw_p"]
    high_ci_hi = result_2tier["tier_stats"].get("HIGH", {}).get("ci_hi")
    low_ci_lo = result_2tier["tier_stats"].get("LOW", {}).get("ci_lo")

    # HARD-PASS: 2-tier fully separable
    if (s2 >= SILHOUETTE_HARD_PASS and n2 == t2 and kw2 < KW_P_HARD_PASS
            and high_ci_hi is not None and low_ci_lo is not None
            and high_ci_hi > low_ci_lo + 0.01):
        verdict = "2TIER_HARD_PASS"
        verdict_msg = (
            f"2-tier HIGH/LOW clearly separable: silhouette={s2:.3f} >= {SILHOUETTE_HARD_PASS}, "
            f"{n2}/{t2} non-overlapping CIs, KW p={kw2:.6f} < {KW_P_HARD_PASS}. "
            f"HIGH_ci_hi={high_ci_hi:.3f} > LOW_ci_lo={low_ci_lo:.3f}. "
            f"Bet B retention is BINARY-classifiable at group level. "
            f"Coarsest defensible taxonomy = 2-tier."
        )
    # HARD-FAIL: even 2-tier CIs overlap
    elif high_ci_hi is not None and low_ci_lo is not None and high_ci_hi <= low_ci_lo:
        verdict = "2TIER_HARD_FAIL"
        verdict_msg = (
            f"2-tier CI OVERLAP: HIGH_ci_hi={high_ci_hi:.3f} <= LOW_ci_lo={low_ci_lo:.3f}. "
            f"silhouette={s2:.3f}, {n2}/{t2} non-overlapping. "
            f"Even coarsest taxonomy cannot be separated at cell level. "
            f"Group-level signal only (omnibus KW p={kw2:.6f})."
        )
    else:
        verdict = "2TIER_MIDDLE"
        verdict_msg = (
            f"2-tier MIDDLE: silhouette={s2:.3f} (pass={SILHOUETTE_HARD_PASS}), "
            f"{n2}/{t2} non-overlapping, KW p={kw2:.6f}. "
            f"HIGH_ci_hi={high_ci_hi:.3f} LOW_ci_lo={low_ci_lo:.3f}. "
            f"Separation exists but not at HARD-PASS threshold. "
            f"3-tier: silhouette={result_3tier['silhouette']:.3f} nonoverlap={result_3tier['n_nonoverlap']}/{result_3tier['total_pairs']}."
        )

    elapsed = time.monotonic() - t0
    summary = {
        "2tier": result_2tier,
        "3tier": result_3tier,
    }

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed, 3),
        "summary": summary,
        "config": {"source": str(source_path), "silhouette_hard_pass": SILHOUETTE_HARD_PASS},
    }
    validate_metrics(metrics)

    out_dir = get_output_dir("wave14_betB_2tier_coarse_analysis_v1")
    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f_out:
        json.dump(metrics, f_out, indent=2)

    print(f"[done] verdict={verdict}", flush=True)
    print(f"[done] verdict_msg={verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s metrics={out_path}", flush=True)
    return metrics


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    self_test()
    run()


if __name__ == "__main__":
    main()
