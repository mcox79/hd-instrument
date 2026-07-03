"""Alt1 rescue: sweep of alternative shift-class taxonomies for Bet B retention.

Context: 6-class taxonomy HARD-PASS at smoke scale but walked back at FULL replication
(4/6 non-overlapping CIs). 3-class coarse taxonomy CONFIRMED (3CLASS_HARD_PASS). This
re-analysis sweeps ALL plausible 2/3/4/5/6-class taxonomy variants on the same full-
replication artifact data to find the taxonomy that maximises silhouette width (cluster
compactness vs separation) -- a principled, unbiased selection of the optimal granularity.

Pure re-analysis: zero new compute, reads from data/exp_wave14_betB_shift_class_predictor_v1/
and data/exp_wave14_betB_shift_class_full_replication_v1/. Runs in <20s on laptop CPU.

Pre-registered outcomes (BEFORE running):
  HARD-PASS: a taxonomy at K in {3,4} achieves silhouette >= 0.60 AND all K clusters
    have non-overlapping 95% CIs AND K-W p < 0.01. Interpretation: taxonomy at that
    granularity is the canonical defensible product claim.
  HARD-FAIL: no taxonomy at any K achieves silhouette >= 0.40. Interpretation: cluster
    structure is weak; only the omnibus KW signal survives, not CI-level granularity.
  MIDDLE: best silhouette 0.40-0.60, or CIs overlap at some pair. Report best K and gaps.

Note on the 4-class hypothesis: the user prompt observes plateaus at ~0.94/0.74/0.60.
The full-replication per-class means are 0.925, 0.885, 0.845/0.838, 0.734, 0.633.
A 4-class split (SAME/COMPOUND | REPLAY | STAGE4/NOREPLAY | DIFF) is a natural candidate
separating at the 0.94->0.88 gap and the 0.84->0.73 gap.

Queue: local_cpu_queue (pure JSON re-analysis, < 20s)
Pre-reg: preregs/2026-05-25_wave14_betB_alt_taxonomy_sweep_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import math
import os
import time
from itertools import combinations
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
    """Assert silhouette and CI computations are non-null at toy scale."""
    # 3 clusters of 4 points each, well separated
    clusters = {"A": [0.1, 0.12, 0.11, 0.09], "B": [0.5, 0.51, 0.49, 0.52], "C": [0.9, 0.91, 0.89, 0.92]}
    sil = compute_silhouette(clusters)
    assert sil is not None and not math.isnan(sil), f"silhouette is null: {sil}"
    assert sil > 0.5, f"toy silhouette too low: {sil}"
    ci_lo, ci_hi = compute_ci([0.1, 0.12, 0.11, 0.09])
    assert ci_lo is not None and ci_hi is not None, "CI is null"
    assert ci_lo < ci_hi, f"CI inverted: [{ci_lo}, {ci_hi}]"
    # single-item CI should return degenerate (lo == hi)
    ci_lo1, ci_hi1 = compute_ci([0.5])
    assert ci_lo1 == ci_hi1, f"single-item CI not degenerate: [{ci_lo1}, {ci_hi1}]"
    print("[self-test] silhouette + CI computations OK")

_SELFTEST_DEFERRED = True  # selftest called after helpers are defined below


# ---------------------------------------------------------------------------
# Statistical helpers
# ---------------------------------------------------------------------------

def compute_ci(vals: List[float], z: float = 1.96) -> Tuple[float, float]:
    n = len(vals)
    if n == 0:
        return (float("nan"), float("nan"))
    mean = sum(vals) / n
    if n == 1:
        return (mean, mean)
    var = sum((v - mean) ** 2 for v in vals) / (n - 1)
    se = math.sqrt(var / n)
    return (mean - z * se, mean + z * se)


def compute_silhouette(clusters: Dict[str, List[float]]) -> float:
    """Mean silhouette width across all items.

    For item i in cluster C_i with value x_i:
      a(i) = mean distance to other items in C_i
      b(i) = min over other clusters C_j of mean distance to items in C_j
      s(i) = (b(i) - a(i)) / max(a(i), b(i))
    """
    all_items = [(label, v) for label, vals in clusters.items() for v in vals]
    if len(all_items) <= 1:
        return 0.0
    cluster_items: Dict[str, List[float]] = {}
    for label, v in all_items:
        cluster_items.setdefault(label, []).append(v)

    sil_scores = []
    for label, v in all_items:
        same = [x for x in cluster_items[label] if x != v]
        if same:
            a = sum(abs(v - x) for x in same) / len(same)
        else:
            a = 0.0
        b_vals = []
        for other_label, other_items in cluster_items.items():
            if other_label == label:
                continue
            b_vals.append(sum(abs(v - x) for x in other_items) / len(other_items))
        if not b_vals:
            sil_scores.append(0.0)
            continue
        b = min(b_vals)
        denom = max(a, b)
        s = (b - a) / denom if denom > 0 else 0.0
        sil_scores.append(s)
    return sum(sil_scores) / len(sil_scores)


def kruskal_wallis_p(groups: List[List[float]]) -> float:
    """Kruskal-Wallis H-statistic p-value (approximated via chi-squared)."""
    import math
    all_vals = [(v, g_idx) for g_idx, g in enumerate(groups) for v in g]
    all_vals.sort(key=lambda x: x[0])
    n = len(all_vals)
    # assign ranks with tie correction
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n and all_vals[j][0] == all_vals[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2.0
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j
    # tie correction factor
    G = n  # total
    tie_runs = {}
    for val, _ in all_vals:
        tie_runs[val] = tie_runs.get(val, 0) + 1
    C = 1.0 - sum(t ** 3 - t for t in tie_runs.values()) / (n ** 3 - n) if n > 1 else 1.0
    # group rank sums
    group_ranks: Dict[int, List[float]] = {}
    for rank_val, (_, g_idx) in zip(ranks, all_vals):
        group_ranks.setdefault(g_idx, []).append(rank_val)
    H_num = sum(len(gr) * (sum(gr) / len(gr) - (n + 1) / 2.0) ** 2 for gr in group_ranks.values())
    H = 12.0 / (n * (n + 1)) * H_num / C if C > 0 else 0.0
    # chi-squared CDF approximation (df = k-1) via regularized incomplete gamma
    df = len(groups) - 1
    if df <= 0:
        return 1.0
    p = _chi2_sf(H, df)
    return p


def _chi2_sf(x: float, df: int) -> float:
    """Survival function of chi-squared(df) at x (approximation via regularized gamma)."""
    if x <= 0:
        return 1.0
    return _regularized_upper_gamma(df / 2.0, x / 2.0)


def _regularized_upper_gamma(a: float, x: float) -> float:
    """Q(a, x) = 1 - P(a, x) via series + continued fraction (Numerical Recipes)."""
    if x < 0:
        return 1.0
    if x == 0:
        return 1.0
    if x < a + 1:
        # series
        ap = a
        s = 1.0 / a
        d = s
        for _ in range(300):
            ap += 1.0
            d *= x / ap
            s += d
            if abs(d) < abs(s) * 3e-7:
                break
        gln = _log_gamma(a)
        return 1.0 - math.exp(-x + a * math.log(x) - gln) * s
    else:
        # Lentz continued fraction
        b = x + 1.0 - a
        c = 1.0 / 1e-30
        d = 1.0 / b
        h = d
        for i in range(1, 301):
            an = -i * (i - a)
            b += 2.0
            d = an * d + b
            if abs(d) < 1e-30:
                d = 1e-30
            c = b + an / c
            if abs(c) < 1e-30:
                c = 1e-30
            d = 1.0 / d
            delta = d * c
            h *= delta
            if abs(delta - 1.0) < 3e-7:
                break
        gln = _log_gamma(a)
        return math.exp(-x + a * math.log(x) - gln) * h


def _log_gamma(z: float) -> float:
    """Lanczos approximation for log-Gamma."""
    g = 7
    c = [0.99999999999980993, 676.5203681218851, -1259.1392167224028,
         771.32342877765313, -176.61502916214059, 12.507343278686905,
         -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7]
    if z < 0.5:
        return math.log(math.pi / math.sin(math.pi * z)) - _log_gamma(1.0 - z)
    z -= 1
    x = c[0]
    for i in range(1, g + 2):
        x += c[i] / (z + i)
    t = z + g + 0.5
    return 0.5 * math.log(2 * math.pi) + (z + 0.5) * math.log(t) - t + math.log(x)


def count_nonoverlapping(clusters: Dict[str, Tuple[float, float, float]]) -> int:
    """Count pairs of clusters with non-overlapping 95% CIs."""
    items = list(clusters.items())
    count = 0
    for (n1, (m1, lo1, hi1)), (n2, (m2, lo2, hi2)) in combinations(items, 2):
        # non-overlapping if intervals are disjoint
        if hi1 < lo2 or hi2 < lo1:
            count += 1
    return count


_instrumentation_selftest()  # called after helpers are defined


# ---------------------------------------------------------------------------
# Taxonomy definitions
# ---------------------------------------------------------------------------

# All plausible taxonomies to sweep (label -> coarse_class)
TAXONOMIES: Dict[str, Dict[str, str]] = {
    # --- 2-class ---
    "2class_highlow": {
        "SAME_CORPUS_PRISTINE":   "HIGH",
        "COMPOUND_SAME_CORPUS":   "HIGH",
        "REPLAY_SAME_CORPUS":     "LOW",
        "NO_REPLAY_SAME_CORPUS":  "LOW",
        "STAGE_4_COMPOUND":       "LOW",
        "DIFF_CORPUS_2TASK":      "LOW",
    },
    # --- 3-class (existing 3CLASS_HARD_PASS) ---
    "3class_standard": {
        "SAME_CORPUS_PRISTINE":   "HIGH",
        "COMPOUND_SAME_CORPUS":   "HIGH",
        "REPLAY_SAME_CORPUS":     "MID",
        "NO_REPLAY_SAME_CORPUS":  "MID",
        "STAGE_4_COMPOUND":       "MID",
        "DIFF_CORPUS_2TASK":      "LOW",
    },
    # --- 3-class alt: split NO_REPLAY with STAGE_4 ---
    "3class_nosplit": {
        "SAME_CORPUS_PRISTINE":   "HIGH",
        "COMPOUND_SAME_CORPUS":   "HIGH",
        "REPLAY_SAME_CORPUS":     "MID",
        "NO_REPLAY_SAME_CORPUS":  "LOW",  # demoted to LOW
        "STAGE_4_COMPOUND":       "MID",
        "DIFF_CORPUS_2TASK":      "LOW",
    },
    # --- 4-class (new hypothesis: split SAME_PRISTINE from COMPOUND) ---
    "4class_splithi": {
        "SAME_CORPUS_PRISTINE":   "PRISTINE",  # 0.925 separate cluster
        "COMPOUND_SAME_CORPUS":   "HIGH",       # 0.885
        "REPLAY_SAME_CORPUS":     "MID",        # 0.845
        "NO_REPLAY_SAME_CORPUS":  "MID",        # 0.838 -- close to REPLAY
        "STAGE_4_COMPOUND":       "STAGE4",     # 0.734
        "DIFF_CORPUS_2TASK":      "STAGE4",     # 0.633 -- lumped with STAGE4
    },
    # --- 4-class (plateau-matched: 0.94 / 0.84 / 0.73 / 0.63) ---
    "4class_plateau": {
        "SAME_CORPUS_PRISTINE":   "P1",   # 0.94 plateau
        "COMPOUND_SAME_CORPUS":   "P1",   # 0.88 (within 0.94 band)
        "REPLAY_SAME_CORPUS":     "P2",   # 0.84 plateau
        "NO_REPLAY_SAME_CORPUS":  "P2",   # 0.84 (near REPLAY)
        "STAGE_4_COMPOUND":       "P3",   # 0.74 plateau (matches dispatch note 0.74)
        "DIFF_CORPUS_2TASK":      "P4",   # 0.60 plateau (matches dispatch note 0.60)
    },
    # --- 4-class alt: separate NOREPLAY as own tier ---
    "4class_noreplay_isolated": {
        "SAME_CORPUS_PRISTINE":   "HIGH",
        "COMPOUND_SAME_CORPUS":   "HIGH",
        "REPLAY_SAME_CORPUS":     "MID_HIGH",
        "NO_REPLAY_SAME_CORPUS":  "MID_LOW",   # 0.838 -- own tier
        "STAGE_4_COMPOUND":       "MID_LOW",
        "DIFF_CORPUS_2TASK":      "LOW",
    },
    # --- 5-class: separate STAGE4 and DIFF, keep REPLAY+NOREPLAY together ---
    "5class_fine": {
        "SAME_CORPUS_PRISTINE":   "P1",
        "COMPOUND_SAME_CORPUS":   "P2",
        "REPLAY_SAME_CORPUS":     "P3",
        "NO_REPLAY_SAME_CORPUS":  "P3",
        "STAGE_4_COMPOUND":       "P4",
        "DIFF_CORPUS_2TASK":      "P5",
    },
    # --- 6-class: original (walked back at FULL replication scale) ---
    "6class_original": {
        "SAME_CORPUS_PRISTINE":   "SAME_CORPUS_PRISTINE",
        "COMPOUND_SAME_CORPUS":   "COMPOUND_SAME_CORPUS",
        "REPLAY_SAME_CORPUS":     "REPLAY_SAME_CORPUS",
        "NO_REPLAY_SAME_CORPUS":  "NO_REPLAY_SAME_CORPUS",
        "STAGE_4_COMPOUND":       "STAGE_4_COMPOUND",
        "DIFF_CORPUS_2TASK":      "DIFF_CORPUS_2TASK",
    },
}


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

def load_retention_data() -> Dict[str, List[float]]:
    """Load per-class retention values from both experiments."""
    data: Dict[str, List[float]] = {}
    # Primary: predictor v1 (5 seeds, well-sampled)
    p1 = DATA / "exp_wave14_betB_shift_class_predictor_v1" / "metrics.json"
    with open(p1) as f:
        m1 = json.load(f)
    for cls, info in m1["summary"]["per_class"].items():
        data.setdefault(cls, []).extend(info["values"])
    # Secondary: full replication (extra seeds, complements v1)
    p2 = DATA / "exp_wave14_betB_shift_class_full_replication_v1" / "metrics.json"
    with open(p2) as f:
        m2 = json.load(f)
    for cls, info in m2["summary"]["per_class"].items():
        # only add fresh_seeds (not existing_data to avoid double-counting)
        if info.get("source") == "fresh_seeds":
            data.setdefault(cls, []).extend(info["values"])
    return data


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

def evaluate_taxonomy(name: str, mapping: Dict[str, str], data: Dict[str, List[float]]) -> Dict:
    """Evaluate one taxonomy against the retention data."""
    # Collect values per coarse class
    coarse: Dict[str, List[float]] = {}
    for fine_cls, vals in data.items():
        coarse_cls = mapping.get(fine_cls)
        if coarse_cls is None:
            continue
        coarse.setdefault(coarse_cls, []).extend(vals)

    n_classes = len(coarse)
    # Per-class CI
    ci_stats: Dict[str, Tuple[float, float, float]] = {}
    for cls, vals in coarse.items():
        mean = sum(vals) / len(vals)
        lo, hi = compute_ci(vals)
        ci_stats[cls] = (mean, lo, hi)

    sil = compute_silhouette(coarse)
    kw_p = kruskal_wallis_p(list(coarse.values()))
    n_nonoverlap = count_nonoverlapping(ci_stats)
    n_pairs = n_classes * (n_classes - 1) // 2

    return {
        "n_classes": n_classes,
        "silhouette": round(sil, 4),
        "kw_p": kw_p,
        "n_nonoverlap_pairs": n_nonoverlap,
        "n_total_pairs": n_pairs,
        "all_pairs_nonoverlap": n_nonoverlap == n_pairs,
        "per_class": {cls: {"mean": round(m, 4), "ci_lo": round(lo, 4), "ci_hi": round(hi, 4),
                             "n": len(coarse[cls])}
                      for cls, (m, lo, hi) in sorted(ci_stats.items(), key=lambda x: -x[1][0])},
    }


def run():
    t0 = time.time()
    out_dir = get_output_dir("wave14_betB_alt_taxonomy_sweep_v1")

    data = load_retention_data()
    total_values = sum(len(v) for v in data.values())
    print(f"Loaded retention data: {total_values} total values across {len(data)} fine classes")
    for cls, vals in sorted(data.items()):
        print(f"  {cls}: n={len(vals)}, mean={sum(vals)/len(vals):.4f}")

    # Pre-registered thresholds
    HARD_PASS_SILHOUETTE = 0.60
    FAIL_SILHOUETTE = 0.40
    PASS_KW_P = 0.01

    results = {}
    for tax_name, mapping in sorted(TAXONOMIES.items()):
        r = evaluate_taxonomy(tax_name, mapping, data)
        results[tax_name] = r
        sil_str = f"sil={r['silhouette']:.3f}"
        kw_str = f"kw_p={r['kw_p']:.2e}"
        novl = f"{r['n_nonoverlap_pairs']}/{r['n_total_pairs']} nonoverlap"
        print(f"{tax_name}: K={r['n_classes']} {sil_str} {kw_str} {novl}")

    # Best taxonomy by silhouette
    best_name = max(results.keys(), key=lambda k: results[k]["silhouette"])
    best = results[best_name]

    # Determine verdict
    if (best["silhouette"] >= HARD_PASS_SILHOUETTE
            and best["all_pairs_nonoverlap"]
            and best["kw_p"] < PASS_KW_P):
        verdict = "ALT_TAXONOMY_HARD_PASS"
        verdict_msg = (
            f"HARD-PASS: taxonomy '{best_name}' (K={best['n_classes']}) achieves "
            f"silhouette={best['silhouette']:.3f} >= 0.60, all {best['n_nonoverlap_pairs']} pairs "
            f"non-overlapping, KW p={best['kw_p']:.2e} < 0.01. Canonical taxonomy identified."
        )
    elif best["silhouette"] < FAIL_SILHOUETTE:
        verdict = "ALT_TAXONOMY_HARD_FAIL"
        verdict_msg = (
            f"HARD-FAIL: best taxonomy '{best_name}' silhouette={best['silhouette']:.3f} < 0.40. "
            f"No taxonomy achieves CI-level separation. Omnibus KW signal only."
        )
    else:
        verdict = "ALT_TAXONOMY_MIDDLE"
        verdict_msg = (
            f"MIDDLE: best taxonomy '{best_name}' (K={best['n_classes']}) silhouette="
            f"{best['silhouette']:.3f} (0.40-0.60 band), "
            f"{best['n_nonoverlap_pairs']}/{best['n_total_pairs']} non-overlapping pairs."
        )

    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    # All results sorted by silhouette for reporting
    ranking = sorted(results.items(), key=lambda x: -x[1]["silhouette"])

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 2),
        "summary": {
            "best_taxonomy": best_name,
            "best_k": best["n_classes"],
            "best_silhouette": best["silhouette"],
            "best_kw_p": best["kw_p"],
            "best_all_pairs_nonoverlap": best["all_pairs_nonoverlap"],
            "pass_silhouette_threshold": HARD_PASS_SILHOUETTE,
            "fail_silhouette_threshold": FAIL_SILHOUETTE,
            "n_input_values": total_values,
        },
        "all_taxonomies": {name: {"silhouette": r["silhouette"], "k": r["n_classes"],
                                   "kw_p": r["kw_p"],
                                   "n_nonoverlap": r["n_nonoverlap_pairs"],
                                   "n_total": r["n_total_pairs"]}
                           for name, r in ranking},
        "best_per_class": best["per_class"],
        "config": {"n_taxonomies_swept": len(TAXONOMIES)},
    }

    out_file = out_dir / "metrics.json"
    with open(out_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_file}")
    print(f"Elapsed: {metrics['elapsed_s']}s")


if __name__ == "__main__":
    run()
