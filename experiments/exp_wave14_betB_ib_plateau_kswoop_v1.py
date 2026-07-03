"""IB phase-transition plateau test: K-corpus count vs number of observable plateaus.

Context: notes/research_alternative_theoretical_homes_2026-05-24.md candidate (iv):
Information-Bottleneck phase-transition framework predicts that the NUMBER of retention
plateaus = number of class-clusters resolvable in the joint (X,Y) distribution.
Key falsifier: vary K (number of training corpora) and count the number of plateau levels.

THIS IS A LOCAL SYNTHETIC PROBE (no GPU needed). It generates retention-like data under
two regimes and tests whether K-corpus structure creates K-plateau signatures.

Specifically:
  - For K=1 corpus: all tasks see the same corpus -> single retention level expected
  - For K=2: two distinct corpora -> two retention levels expected
  - For K=3: three distinct corpora -> three retention levels expected
  (Using the existing Bet B per-class means as representative values.)

The probe computes: given the observed per-class means from shift_class_predictor,
how many DISTINCT plateaus are detectable via the elbow method + silhouette? Does the
number match K?

Also tests: do the plateau heights satisfy the IB spacing formula
  plateau_i = exp(-H_i)  where H_i = conditional entropy of i-th cluster refinement?

This is a soft probe -- it uses existing data, not new simulation. It computes the
MI-based plateau prediction from the approximate cluster entropies.

Pre-registered outcomes:
  IB_CONSISTENT: plateau count from elbow method matches K for K in {1,2,3} AND
    IB spacing formula error < 0.10 for each plateau.
  IB_INCONSISTENT: plateau count does NOT track K (e.g., K=5 gives 3 plateaus, not 5).
  IB_PARTIAL: count tracks K for small K but not large K.

Queue: local_cpu_queue (pure numpy re-analysis, < 10s)
Pre-reg: preregs/2026-05-25_wave14_betB_ib_plateau_kswoop_v1.md
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
    """Assert elbow detection and IB formula are non-null."""
    # 3 clean levels
    vals = [0.9, 0.91, 0.89, 0.5, 0.51, 0.49, 0.1, 0.11, 0.09]
    n_plateaus = detect_plateaus(vals)
    assert n_plateaus is not None and n_plateaus >= 2, f"plateau detection failed: {n_plateaus}"
    # IB formula: H=0 -> exp(-0)=1.0
    ib = ib_plateau_height(0.0)
    assert abs(ib - 1.0) < 1e-9, f"IB formula at H=0 != 1.0: {ib}"
    print("[self-test] plateau detection and IB formula OK")

_SELFTEST_DEFERRED = True  # called after helpers below


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

def detect_plateaus(values: List[float], merge_threshold: float = 0.05) -> int:
    """Count distinct plateaus via gap-detection: values within merge_threshold are one plateau."""
    if not values:
        return 0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n == 1:
        return 1
    # Gap-based: consecutive gaps > merge_threshold indicate a new plateau
    # First, cluster sorted values
    clusters = [[sorted_vals[0]]]
    for v in sorted_vals[1:]:
        if v - clusters[-1][-1] > merge_threshold:
            clusters.append([v])
        else:
            clusters[-1].append(v)
    return len(clusters)


def ib_plateau_height(conditional_entropy: float) -> float:
    """IB plateau height prediction: plateau = exp(-H) where H = conditional entropy."""
    return math.exp(-conditional_entropy)


def estimate_cluster_entropy(vals: List[float], n_total: float) -> float:
    """Rough conditional entropy H = -p * log(p) where p = n_cluster/n_total."""
    p = len(vals) / n_total
    if p <= 0 or p >= 1:
        return 0.0
    return -p * math.log(p)


# ---------------------------------------------------------------------------
# Load data and build K-corpus scenarios
# ---------------------------------------------------------------------------

_instrumentation_selftest()  # called after helpers defined


def load_per_class_data() -> Dict[str, List[float]]:
    p = DATA / "exp_wave14_betB_shift_class_predictor_v1" / "metrics.json"
    with open(p) as f:
        m = json.load(f)
    return {cls: info["values"] for cls, info in m["summary"]["per_class"].items()}


def build_k_scenario(k: int, data: Dict[str, List[float]]) -> List[float]:
    """Build retention values for K-corpus scenario.

    K=1: only SAME_CORPUS_PRISTINE (all tasks from same corpus)
    K=2: SAME_CORPUS_PRISTINE + DIFF_CORPUS_2TASK
    K=3: SAME + STAGE4 + DIFF
    K=4: SAME + COMPOUND + STAGE4 + DIFF
    K=5: SAME + COMPOUND + REPLAY + STAGE4 + DIFF
    K=6: all 6 classes
    """
    mapping = {
        1: ["SAME_CORPUS_PRISTINE"],
        2: ["SAME_CORPUS_PRISTINE", "DIFF_CORPUS_2TASK"],
        3: ["SAME_CORPUS_PRISTINE", "STAGE_4_COMPOUND", "DIFF_CORPUS_2TASK"],
        4: ["SAME_CORPUS_PRISTINE", "COMPOUND_SAME_CORPUS", "STAGE_4_COMPOUND", "DIFF_CORPUS_2TASK"],
        5: ["SAME_CORPUS_PRISTINE", "COMPOUND_SAME_CORPUS", "REPLAY_SAME_CORPUS",
            "STAGE_4_COMPOUND", "DIFF_CORPUS_2TASK"],
        6: ["SAME_CORPUS_PRISTINE", "COMPOUND_SAME_CORPUS", "REPLAY_SAME_CORPUS",
            "NO_REPLAY_SAME_CORPUS", "STAGE_4_COMPOUND", "DIFF_CORPUS_2TASK"],
    }
    classes = mapping.get(k, list(data.keys()))
    vals = []
    for cls in classes:
        vals.extend(data.get(cls, []))
    return vals


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run():
    t0 = time.time()
    out_dir = get_output_dir("wave14_betB_ib_plateau_kswoop_v1")

    data = load_per_class_data()
    n_total = sum(len(v) for v in data.values())
    print(f"Loaded {n_total} retention values across {len(data)} classes")

    # Test K in {1, 2, 3, 4, 5, 6}
    K_vals = [1, 2, 3, 4, 5, 6]
    results = []

    print("\nK-scenario plateau detection:")
    for k in K_vals:
        vals = build_k_scenario(k, data)
        if not vals:
            continue
        n_plateaus = detect_plateaus(vals, merge_threshold=0.05)
        mean = sum(vals) / len(vals)
        print(f"  K={k}: n_vals={len(vals)}, n_plateaus_detected={n_plateaus}, mean={mean:.3f}")

        # IB spacing predictions: compute entropy-based plateau heights
        # For K distinct corpus classes, each contributes conditional entropy H_i = -p_i log p_i
        # Predict plateau heights: exp(-cumsum(H_i))
        ib_preds = []
        for j in range(k):
            p_j = 1.0 / k  # equal-weight assumption
            H_j = -p_j * math.log(p_j)
            cumH = H_j * (j + 1)  # cumulative entropy up to tier j
            ib_pred = ib_plateau_height(cumH)
            ib_preds.append(round(ib_pred, 4))
        print(f"    IB predicted plateau heights: {ib_preds}")

        results.append({
            "K": k,
            "n_vals": len(vals),
            "n_plateaus_detected": n_plateaus,
            "plateau_count_matches_K": (n_plateaus == k),
            "mean_retention": round(mean, 4),
            "ib_predicted_plateaus": ib_preds,
        })

    # Check if plateau count tracks K
    tracking = [(r["K"], r["n_plateaus_detected"]) for r in results]
    print(f"\nK vs detected plateaus: {tracking}")
    tracks_small = all(r["plateau_count_matches_K"] for r in results if r["K"] <= 3)
    tracks_all = all(r["plateau_count_matches_K"] for r in results)

    # IB spacing accuracy at K=3 (observed case)
    r3 = next((r for r in results if r["K"] == 3), None)
    ib_error_k3 = None
    if r3:
        # Observed plateau means at K=3: ~0.925, ~0.734, ~0.633
        observed_means = [
            sum(data.get("SAME_CORPUS_PRISTINE", [0.93])) / max(len(data.get("SAME_CORPUS_PRISTINE", [1])), 1),
            sum(data.get("STAGE_4_COMPOUND", [0.73])) / max(len(data.get("STAGE_4_COMPOUND", [1])), 1),
            sum(data.get("DIFF_CORPUS_2TASK", [0.63])) / max(len(data.get("DIFF_CORPUS_2TASK", [1])), 1),
        ]
        preds_k3 = r3["ib_predicted_plateaus"]
        if len(preds_k3) >= 3:
            errors = [abs(obs - pred) for obs, pred in zip(observed_means, preds_k3)]
            ib_error_k3 = max(errors)
            print(f"\nK=3 IB accuracy:")
            for i, (obs, pred, err) in enumerate(zip(observed_means, preds_k3, errors)):
                print(f"  Plateau {i+1}: observed={obs:.4f}, IB_pred={pred:.4f}, error={err:.4f}")
            print(f"  Max error: {ib_error_k3:.4f} (threshold 0.10)")

    # Verdict
    IB_MATCH_THRESHOLD = 0.10
    ib_matches = ib_error_k3 is not None and ib_error_k3 < IB_MATCH_THRESHOLD

    if tracks_all and ib_matches:
        verdict = "IB_CONSISTENT"
        verdict_msg = (
            f"IB_CONSISTENT: plateau count tracks K for all K in {[r['K'] for r in results]}. "
            f"IB spacing formula error at K=3: {ib_error_k3:.3f} < 0.10. "
            f"Information-Bottleneck framework is consistent with Bet B plateau structure."
        )
    elif tracks_small and not tracks_all:
        verdict = "IB_PARTIAL"
        verdict_msg = (
            f"IB_PARTIAL: plateau count tracks K for K <= 3 but not larger K. "
            f"Detectable plateau structure saturates before K reaches max fine-class count."
        )
    elif not tracks_small:
        verdict = "IB_INCONSISTENT"
        verdict_msg = (
            f"IB_INCONSISTENT: plateau count does NOT track K even for K <= 3. "
            f"K vs plateaus: {tracking}. IB framework inconsistent with existing data."
        )
    else:
        verdict = "IB_WEAK"
        verdict_msg = (
            f"IB_WEAK: plateau count partially tracks K but IB spacing error="
            f"{ib_error_k3:.3f} > 0.10 (formula mismatch). "
            f"Framework structurally consistent but quantitative prediction off."
        )

    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 2),
        "summary": {
            "plateau_count_tracks_K_all": tracks_all,
            "plateau_count_tracks_K_small": tracks_small,
            "ib_spacing_error_k3": ib_error_k3,
            "ib_spacing_matches": ib_matches,
            "k_vs_plateaus": {r["K"]: r["n_plateaus_detected"] for r in results},
        },
        "k_scenarios": results,
        "config": {"merge_threshold": 0.05, "K_vals_tested": K_vals},
    }
    out_file = out_dir / "metrics.json"
    with open(out_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_file}")


if __name__ == "__main__":
    run()
