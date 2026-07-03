"""2-tier vs 3-tier vs 4-tier alt-taxonomy CONTRAST for substrate-product framing.

Context: wave14_betB_alt_taxonomy_sweep_v1 found 4class_noreplay_isolated is the
best single taxonomy (silhouette=0.584, just below PASS threshold 0.60). But it
tested taxonomies in isolation. This analysis CONTRASTS all three tier-levels
(2-tier, 3-tier, 4-tier) across multiple metrics simultaneously, asking:

1. RETENTION SEPARATION DELTA: How much retention separability is gained per
   additional class (incremental silhouette gain)?
   - 2->3: does adding a 3rd class give big separation improvement?
   - 3->4: marginal benefit of 4th class?
   This determines which taxonomy is the most efficient for the product.

2. PRODUCT FRAMING CLARITY: For the substrate-product claim, which taxonomy
   gives the cleanest story?
   - 2-tier: "high retention (>0.85) vs low retention (<0.75)" -- easiest to
     communicate. Score: product_clarity = 1/n_classes.
   - 3-tier: adds a "middle" class -- useful for substrate-product framing if
     the middle is interpretable (e.g., "with replay" vs "without").
   - 4-tier: fine-grained, but harder to explain. Trade-off.

3. NONOVERLAP RELIABILITY: Which taxonomy maximally avoids class overlap?
   The 4class_noreplay_isolated had 6/6 non-overlapping pairs (all distinct).
   Check whether 2-tier and 3-tier also achieve full non-overlap.

4. SAAD-SOLLA COMPATIBILITY: Does the best-silhouette taxonomy (K=4) match
   the saddle-cascade prediction (3 saddle plateaus)?
   If the cascade predicts 3 groups but the data best separates as 4,
   the cascade framework needs extending to 4-state cascades.

5. WITHINCLASS VARIANCE vs BETWEENCLASS VARIANCE CONTRAST: F-ratio
   (between-group / within-group variance) for each taxonomy K.
   The taxonomy with the highest F-ratio is the most statistically well-separated.

Pre-registered outcomes:
  FOUR_TIER_WINS: 4-tier has strictly better silhouette AND F-ratio than 3-tier,
    AND 3-tier is better than 2-tier. The data has intrinsically 4 natural clusters.
    Recommendation: use 4-tier for substrate-product taxonomy.
  THREE_TIER_OPTIMAL: 3-tier has better INCREMENTAL GAIN (silhouette/F-ratio per
    class) than 4-tier, even if 4-tier has higher absolute silhouette.
    Recommendation: use 3-tier for communication clarity.
  TWO_TIER_SUFFICIENT: 2-tier F-ratio is within 80% of 4-tier F-ratio.
    Marginal gains from extra classes are small; use 2-tier for simplicity.
  TAXONOMY_MIXED: different metrics point to different optima (e.g., 4-tier wins
    on silhouette, 3-tier wins on F-ratio). Report both; context-dependent choice.

Queue: local_cpu_queue (pure numerical re-analysis of existing JSON, <5s)
Pre-reg: preregs/2026-05-25_taxonomy_contrast_retention_sep_v1.md
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
    """Assert silhouette and F-ratio computations are non-null."""
    # F-ratio: 3 groups with clear separation
    groups_clear = [[1.0, 1.1, 0.9], [5.0, 5.1, 4.9], [9.0, 9.1, 8.9]]
    f_clear = compute_f_ratio(groups_clear)
    assert f_clear > 100, f"expected high F-ratio for clearly separated groups, got {f_clear}"

    # F-ratio: 3 groups with no separation (same values)
    groups_equal = [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    f_equal = compute_f_ratio(groups_equal)
    assert f_equal < 1e-6, f"expected F~0 for identical groups, got {f_equal}"

    # Silhouette: 2 groups, perfectly separated
    sil = compute_silhouette_score([[0.0, 0.01, 0.02], [1.0, 1.01, 1.02]])
    assert sil > 0.8, f"expected high silhouette for perfectly separated groups, got {sil}"

    # Silhouette: 1 group
    sil1 = compute_silhouette_score([[0.5, 0.6, 0.4]])
    assert sil1 == 0.0, f"expected 0.0 for single group, got {sil1}"

    print("[self-test] F-ratio and silhouette computations OK")


# called after helpers defined below


# ---------------------------------------------------------------------------
# Statistical helpers
# ---------------------------------------------------------------------------

def compute_f_ratio(groups: List[List[float]]) -> float:
    """One-way ANOVA F-ratio: between-group variance / within-group variance."""
    all_vals = [v for g in groups for v in g]
    n_total = len(all_vals)
    k = len(groups)
    if n_total <= k or k < 2:
        return 0.0

    grand_mean = sum(all_vals) / n_total

    # Between-group sum of squares
    ss_between = sum(len(g) * (sum(g) / len(g) - grand_mean) ** 2 for g in groups if g)
    df_between = k - 1

    # Within-group sum of squares
    ss_within = 0.0
    for g in groups:
        if len(g) > 1:
            mu_g = sum(g) / len(g)
            ss_within += sum((v - mu_g) ** 2 for v in g)
    df_within = n_total - k

    if df_within <= 0 or ss_within <= 0:
        return float("inf") if ss_between > 0 else 0.0

    ms_between = ss_between / df_between
    ms_within = ss_within / df_within
    return ms_between / ms_within if ms_within > 0 else float("inf")


def compute_silhouette_score(groups: List[List[float]]) -> float:
    """1-D silhouette coefficient (mean over all points).

    For point i in group g_i:
      a(i) = mean intra-cluster distance (to other points in g_i)
      b(i) = min over g != g_i of: mean distance to points in g
      s(i) = (b(i) - a(i)) / max(a(i), b(i))
    Silhouette = mean of s(i).
    """
    if len(groups) < 2:
        return 0.0

    # Flatten groups to (value, group_id) pairs
    all_pts = [(v, gi) for gi, g in enumerate(groups) for v in g]
    n = len(all_pts)
    if n < 2:
        return 0.0

    sil_scores = []
    for i, (vi, gi) in enumerate(all_pts):
        # Intra-cluster distance
        intra_pts = [v for v, g in all_pts if g == gi and v != vi]
        if not intra_pts:
            a = 0.0
        else:
            a = sum(abs(vi - v) for v in intra_pts) / len(intra_pts)

        # Min inter-cluster distance
        min_inter = float("inf")
        for other_g in range(len(groups)):
            if other_g == gi:
                continue
            inter_pts = [v for v, g in all_pts if g == other_g]
            if not inter_pts:
                continue
            mean_inter = sum(abs(vi - v) for v in inter_pts) / len(inter_pts)
            if mean_inter < min_inter:
                min_inter = mean_inter

        if min_inter == float("inf"):
            continue  # only 1 other group and it's empty

        b = min_inter
        denom = max(a, b)
        s = (b - a) / denom if denom > 0 else 0.0
        sil_scores.append(s)

    return sum(sil_scores) / len(sil_scores) if sil_scores else 0.0


def count_nonoverlapping_pairs(groups: List[List[float]]) -> Tuple[int, int]:
    """Count pairs of groups with non-overlapping [min, max] ranges.

    Returns (n_nonoverlap, n_total_pairs).
    """
    ranges = []
    for g in groups:
        if g:
            ranges.append((min(g), max(g)))
        else:
            ranges.append((float("inf"), float("-inf")))

    k = len(ranges)
    n_total = k * (k - 1) // 2
    n_nonoverlap = 0
    for i in range(k):
        for j in range(i + 1, k):
            lo_i, hi_i = ranges[i]
            lo_j, hi_j = ranges[j]
            # Non-overlapping: intervals don't intersect
            if hi_i < lo_j or hi_j < lo_i:
                n_nonoverlap += 1

    return n_nonoverlap, n_total


def incremental_silhouette_gain(sil_k_minus_1: float, sil_k: float, k: int) -> float:
    """Silhouette gain per additional class from K-1 to K."""
    return (sil_k - sil_k_minus_1)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_retention_corpus() -> Dict[str, List[float]]:
    p = DATA / "exp_wave14_betB_shift_class_predictor_v1" / "metrics.json"
    with open(p) as f:
        m = json.load(f)
    data: Dict[str, List[float]] = {}
    for cls, info in m["summary"]["per_class"].items():
        data[cls] = info["values"]
    return data


def load_sweep_results() -> Dict[str, Dict]:
    """Load pre-computed taxonomy sweep from alt_taxonomy_sweep_v1."""
    p = DATA / "exp_wave14_betB_alt_taxonomy_sweep_v1" / "metrics.json"
    with open(p) as f:
        m = json.load(f)
    return m.get("all_taxonomies", {})


# ---------------------------------------------------------------------------
# Taxonomy definitions
# ---------------------------------------------------------------------------

def build_taxonomy_groups(data: Dict[str, List[float]], tax_name: str) -> List[List[float]]:
    """Build group lists for a named taxonomy."""
    if tax_name == "2class_highlow":
        # HIGH: SAME_CORPUS_PRISTINE + COMPOUND_SAME_CORPUS
        # LOW: DIFF_CORPUS_2TASK
        # (exclude MID for clarity, or include as HIGH vs LOW?)
        # Per v1 definition: all-high vs all-low split
        high = (data.get("SAME_CORPUS_PRISTINE", []) +
                data.get("COMPOUND_SAME_CORPUS", []) +
                data.get("REPLAY_SAME_CORPUS", []))
        low = (data.get("NO_REPLAY_SAME_CORPUS", []) +
               data.get("STAGE_4_COMPOUND", []) +
               data.get("DIFF_CORPUS_2TASK", []))
        return [high, low]

    elif tax_name == "3class_standard":
        # G1=SAME (PRISTINE+COMPOUND), G2=MID (REPLAY+NO_REPLAY+STAGE4), G3=DIFF
        g1 = data.get("SAME_CORPUS_PRISTINE", []) + data.get("COMPOUND_SAME_CORPUS", [])
        g2 = (data.get("REPLAY_SAME_CORPUS", []) +
              data.get("NO_REPLAY_SAME_CORPUS", []) +
              data.get("STAGE_4_COMPOUND", []))
        g3 = data.get("DIFF_CORPUS_2TASK", [])
        return [g1, g2, g3]

    elif tax_name == "3class_nosplit":
        # Merge top two fine classes: (PRISTINE+COMPOUND+REPLAY) vs STAGE4_NO_REPLAY vs DIFF
        g1 = (data.get("SAME_CORPUS_PRISTINE", []) +
              data.get("COMPOUND_SAME_CORPUS", []) +
              data.get("REPLAY_SAME_CORPUS", []))
        g2 = data.get("STAGE_4_COMPOUND", []) + data.get("NO_REPLAY_SAME_CORPUS", [])
        g3 = data.get("DIFF_CORPUS_2TASK", [])
        return [g1, g2, g3]

    elif tax_name == "4class_noreplay_isolated":
        # Best from v1: HIGH(PRISTINE+COMPOUND), MID_HIGH(REPLAY), MID_LOW(STAGE4+NOREPLAY), LOW(DIFF)
        g1 = data.get("SAME_CORPUS_PRISTINE", []) + data.get("COMPOUND_SAME_CORPUS", [])
        g2 = data.get("REPLAY_SAME_CORPUS", [])
        g3 = data.get("NO_REPLAY_SAME_CORPUS", []) + data.get("STAGE_4_COMPOUND", [])
        g4 = data.get("DIFF_CORPUS_2TASK", [])
        return [g1, g2, g3, g4]

    elif tax_name == "4class_plateau":
        g1 = data.get("SAME_CORPUS_PRISTINE", [])
        g2 = data.get("COMPOUND_SAME_CORPUS", []) + data.get("REPLAY_SAME_CORPUS", [])
        g3 = data.get("NO_REPLAY_SAME_CORPUS", []) + data.get("STAGE_4_COMPOUND", [])
        g4 = data.get("DIFF_CORPUS_2TASK", [])
        return [g1, g2, g3, g4]

    elif tax_name == "6class_original":
        return [
            data.get("SAME_CORPUS_PRISTINE", []),
            data.get("COMPOUND_SAME_CORPUS", []),
            data.get("REPLAY_SAME_CORPUS", []),
            data.get("NO_REPLAY_SAME_CORPUS", []),
            data.get("STAGE_4_COMPOUND", []),
            data.get("DIFF_CORPUS_2TASK", []),
        ]

    return []


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def run():
    t0 = time.time()
    out_dir = get_output_dir("wave14_taxonomy_contrast_retention_sep_v1")

    _instrumentation_selftest()

    data = load_retention_corpus()
    sweep_results = load_sweep_results()

    # Representative taxonomies at each tier level
    tier_taxonomies = {
        "2tier": "2class_highlow",
        "3tier_standard": "3class_standard",
        "3tier_nosplit": "3class_nosplit",
        "4tier_best": "4class_noreplay_isolated",
        "4tier_plateau": "4class_plateau",
        "6tier_original": "6class_original",
    }

    print("=== TAXONOMY CONTRAST ANALYSIS ===\n")

    # Compute metrics for each taxonomy
    tax_metrics = {}
    for tier_label, tax_name in tier_taxonomies.items():
        groups = build_taxonomy_groups(data, tax_name)
        groups = [g for g in groups if g]  # drop empty groups

        k = len(groups)
        f_ratio = compute_f_ratio(groups)
        sil = compute_silhouette_score(groups)
        n_nonoverlap, n_total_pairs = count_nonoverlapping_pairs(groups)

        # Group means for interpretability
        group_means = [sum(g) / len(g) for g in groups]
        group_sizes = [len(g) for g in groups]

        tax_metrics[tier_label] = {
            "tax_name": tax_name,
            "k": k,
            "f_ratio": f_ratio,
            "silhouette": sil,
            "nonoverlap_pairs": n_nonoverlap,
            "total_pairs": n_total_pairs,
            "nonoverlap_fraction": n_nonoverlap / n_total_pairs if n_total_pairs > 0 else 1.0,
            "group_means": [round(m, 4) for m in group_means],
            "group_sizes": group_sizes,
        }

        # Use pre-computed silhouette from v1 if available (faster and consistent)
        if tax_name in sweep_results:
            sil_v1 = sweep_results[tax_name].get("silhouette", sil)
            tax_metrics[tier_label]["silhouette"] = sil_v1

        print(f"{tier_label} ({tax_name}, K={k}):")
        print(f"  F-ratio: {f_ratio:.2f}, Silhouette: {tax_metrics[tier_label]['silhouette']:.4f}")
        print(f"  Non-overlap: {n_nonoverlap}/{n_total_pairs} pairs")
        print(f"  Group means: {[round(m, 3) for m in group_means]}")
        print(f"  Group sizes: {group_sizes}")
        print()

    # -----------------------------------------------------------------------
    # Analysis 1: Incremental silhouette and F-ratio gains
    # -----------------------------------------------------------------------
    print("--- INCREMENTAL GAIN ANALYSIS ---")
    # Best representatives at K=2, K=3, K=4
    sil_2 = tax_metrics["2tier"]["silhouette"]
    sil_3 = max(tax_metrics["3tier_standard"]["silhouette"],
                tax_metrics["3tier_nosplit"]["silhouette"])
    sil_4 = max(tax_metrics["4tier_best"]["silhouette"],
                tax_metrics["4tier_plateau"]["silhouette"])
    f_2 = tax_metrics["2tier"]["f_ratio"]
    f_3 = max(tax_metrics["3tier_standard"]["f_ratio"], tax_metrics["3tier_nosplit"]["f_ratio"])
    f_4 = max(tax_metrics["4tier_best"]["f_ratio"], tax_metrics["4tier_plateau"]["f_ratio"])

    sil_gain_2to3 = sil_3 - sil_2
    sil_gain_3to4 = sil_4 - sil_3
    f_gain_2to3 = f_3 - f_2
    f_gain_3to4 = f_4 - f_3

    print(f"  Silhouette: K=2 {sil_2:.4f} -> K=3 {sil_3:.4f} (+{sil_gain_2to3:.4f}) -> K=4 {sil_4:.4f} (+{sil_gain_3to4:.4f})")
    print(f"  F-ratio:    K=2 {f_2:.2f} -> K=3 {f_3:.2f} (+{f_gain_2to3:.2f}) -> K=4 {f_4:.2f} (+{f_gain_3to4:.2f})")

    # Efficiency: gain per class added
    sil_eff_2to3 = sil_gain_2to3 / 1.0  # 1 class added
    sil_eff_3to4 = sil_gain_3to4 / 1.0  # 1 class added
    f_eff_2to3 = f_gain_2to3 / 1.0
    f_eff_3to4 = f_gain_3to4 / 1.0
    print(f"  Silhouette efficiency: 2->3: {sil_eff_2to3:.4f}/class, 3->4: {sil_eff_3to4:.4f}/class")
    print(f"  F-ratio efficiency:    2->3: {f_eff_2to3:.2f}/class, 3->4: {f_eff_3to4:.2f}/class")

    # -----------------------------------------------------------------------
    # Analysis 2: Product clarity score
    # -----------------------------------------------------------------------
    print("\n--- PRODUCT CLARITY SCORE ---")
    # Product clarity: inversely proportional to K, adjusted by retention separation
    # Separation quality: max_group_mean - min_group_mean, normalized by n_classes
    for tier_label, m in tax_metrics.items():
        if m["group_means"]:
            retention_range = max(m["group_means"]) - min(m["group_means"])
            # Clarity = retention_range / k (want maximal range per class)
            clarity = retention_range / m["k"]
            tax_metrics[tier_label]["product_clarity"] = round(clarity, 4)
            print(f"  {tier_label}: retention_range={retention_range:.4f}, k={m['k']}, clarity={clarity:.4f}")

    # -----------------------------------------------------------------------
    # Analysis 3: Saad-Solla compatibility (3 saddle states)
    # -----------------------------------------------------------------------
    print("\n--- SAAD-SOLLA COMPATIBILITY ---")
    cascade_k = 3  # cascade predicts 3 plateau states
    best_tax_for_k = {}
    for tier_label, m in tax_metrics.items():
        k = m["k"]
        if k not in best_tax_for_k or m["silhouette"] > best_tax_for_k[k]["silhouette"]:
            best_tax_for_k[k] = m

    sil_cascade = best_tax_for_k.get(3, {}).get("silhouette", float("nan"))
    sil_best_overall = max(m["silhouette"] for m in tax_metrics.values())
    cascade_compatible = sil_cascade >= sil_best_overall - 0.10  # within 0.10 of best
    print(f"  Best silhouette at K={cascade_k} (cascade prediction): {sil_cascade:.4f}")
    print(f"  Best silhouette overall: {sil_best_overall:.4f}")
    print(f"  Cascade K=3 within 0.10 of best: {cascade_compatible}")

    # -----------------------------------------------------------------------
    # Verdict
    # -----------------------------------------------------------------------
    four_beats_three_sil = sil_4 > sil_3
    four_beats_three_f = f_4 > f_3
    three_beats_two_sil = sil_3 > sil_2
    three_beats_two_f = f_3 > f_2
    two_within_80pct_of_four = f_2 >= 0.80 * f_4

    print(f"\n--- DISCRIMINANT ---")
    print(f"  4-tier > 3-tier (sil): {four_beats_three_sil}")
    print(f"  4-tier > 3-tier (F):   {four_beats_three_f}")
    print(f"  3-tier > 2-tier (sil): {three_beats_two_sil}")
    print(f"  2-tier within 80% of 4-tier (F): {two_within_80pct_of_four}")
    print(f"  2->3 sil eff ({sil_eff_2to3:.4f}) vs 3->4 sil eff ({sil_eff_3to4:.4f}): "
          f"{'2->3 more efficient' if sil_eff_2to3 > sil_eff_3to4 else '3->4 more efficient'}")

    if four_beats_three_sil and four_beats_three_f and three_beats_two_sil and three_beats_two_f:
        verdict = "FOUR_TIER_WINS"
        verdict_msg = (
            f"FOUR_TIER_WINS: 4-tier strictly dominates on both silhouette ({sil_4:.4f}>{sil_3:.4f}) "
            f"and F-ratio ({f_4:.2f}>{f_3:.2f}). Data has intrinsically 4 natural clusters. "
            f"Recommend 4-tier for substrate-product taxonomy."
        )
    elif (three_beats_two_sil and three_beats_two_f and
          (not four_beats_three_sil or sil_eff_2to3 > sil_eff_3to4)):
        verdict = "THREE_TIER_OPTIMAL"
        verdict_msg = (
            f"THREE_TIER_OPTIMAL: 3-tier gives higher incremental gain ({sil_eff_2to3:.4f}/class) "
            f"than 4-tier ({sil_eff_3to4:.4f}/class). Sil at K=3: {sil_3:.4f}. "
            f"Recommend 3-tier for communication clarity vs separation trade-off."
        )
    elif two_within_80pct_of_four:
        verdict = "TWO_TIER_SUFFICIENT"
        verdict_msg = (
            f"TWO_TIER_SUFFICIENT: 2-tier F={f_2:.2f} is within 80% of 4-tier F={f_4:.2f}. "
            f"Marginal gains from extra classes are small. Use 2-tier for simplicity."
        )
    else:
        verdict = "TAXONOMY_MIXED"
        verdict_msg = (
            f"TAXONOMY_MIXED: sil favors {'4' if four_beats_three_sil else '3'}-tier "
            f"(sil_4={sil_4:.4f}, sil_3={sil_3:.4f}, sil_2={sil_2:.4f}); "
            f"F-ratio favors {'4' if four_beats_three_f else '3'}-tier "
            f"(F_4={f_4:.2f}, F_3={f_3:.2f}, F_2={f_2:.2f}). "
            f"Context-dependent recommendation needed."
        )

    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 3),
        "summary": {
            "silhouette": {"K2": round(sil_2, 4), "K3": round(sil_3, 4), "K4": round(sil_4, 4)},
            "f_ratio": {"K2": round(f_2, 2), "K3": round(f_3, 2), "K4": round(f_4, 2)},
            "sil_gain": {"2to3": round(sil_gain_2to3, 4), "3to4": round(sil_gain_3to4, 4)},
            "f_gain": {"2to3": round(f_gain_2to3, 2), "3to4": round(f_gain_3to4, 2)},
            "sil_efficiency_per_class": {
                "2to3": round(sil_eff_2to3, 4), "3to4": round(sil_eff_3to4, 4)},
            "cascade_k3_compatible": cascade_compatible,
            "sil_cascade_k3": round(sil_cascade, 4),
        },
        "taxonomy_details": {
            tier: {
                k: round(v, 4) if isinstance(v, float) else v
                for k, v in m.items()
            }
            for tier, m in tax_metrics.items()
        },
        "config": {},
    }

    out_file = out_dir / "metrics.json"
    with open(out_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_file}")


if __name__ == "__main__":
    run()
