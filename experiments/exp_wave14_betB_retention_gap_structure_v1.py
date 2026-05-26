"""Retention gap structure analysis: map ALL observed retention values, find natural breaks.

This is a zero-assumption exploration of the full retention distribution across all
available Bet B experiments. Rather than testing a specific taxonomy, it:

  1. Collects ALL retention_A values from all Bet B artifact metrics.json files.
  2. Computes the full density (histogram + gap analysis).
  3. Identifies natural break points (Jenks-like: maximize between-group variance).
  4. Computes the optimal K (2..6) via gap-statistic on the 1D data.
  5. Cross-validates: do the optimal-K cluster centers match the dispatch-note
     observations of 0.94 / 0.74 / 0.60 plateaus?

Pure re-analysis, < 15s on laptop CPU. Uses no external libraries (pure Python).

Pre-registered outcomes:
  STRUCTURE_FOUND: optimal K in {2,3,4} AND at least one cluster center within 0.05
    of the three dispatch-note plateaus (0.94, 0.74, 0.60).
  STRUCTURE_DIFFUSE: optimal K >= 5 OR no cluster center within 0.05 of the
    three dispatch-note plateaus. Data is more spread than the 3-plateau model suggests.
  STRUCTURE_BIMODAL: optimal K = 2, suggesting only HIGH vs LOW matters.

Queue: local_cpu_queue (pure JSON re-analysis, < 15s)
Pre-reg: preregs/2026-05-25_wave14_betB_retention_gap_structure_v1.md
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
from typing import Dict, List, Tuple, Optional

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = DATA / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


# ---------------------------------------------------------------------------
# Instrumentation self-test
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert 1D clustering and gap statistic are non-null."""
    # 3 clean clusters
    data = [0.1, 0.11, 0.12, 0.5, 0.51, 0.52, 0.9, 0.91, 0.92]
    centers, labels = kmeans_1d(data, k=3)
    assert len(centers) == 3, f"expected 3 centers, got {len(centers)}"
    assert all(c is not None and not math.isnan(c) for c in centers), f"centers contain None/NaN: {centers}"
    # between-variance should be high
    bv = between_variance(data, centers, labels)
    assert bv > 0.1, f"expected high between-variance, got {bv}"
    print("[self-test] 1D clustering OK")

_SELFTEST_DEFERRED = True  # called after helpers below


# ---------------------------------------------------------------------------
# 1D K-means
# ---------------------------------------------------------------------------

def kmeans_1d(data: List[float], k: int, n_init: int = 10, max_iter: int = 100) -> Tuple[List[float], List[int]]:
    """Simple 1D K-means. Returns (centers, labels)."""
    if len(data) <= k:
        return sorted(data), list(range(len(data)))
    import random
    rng = random.Random(42)
    best_centers = None
    best_inertia = float("inf")
    for _ in range(n_init):
        # random init
        init_centers = sorted(rng.sample(data, k))
        centers = list(init_centers)
        for _iter in range(max_iter):
            # assign
            labels = [min(range(k), key=lambda c: abs(x - centers[c])) for x in data]
            # update
            new_centers = []
            for c in range(k):
                members = [data[i] for i, l in enumerate(labels) if l == c]
                if members:
                    new_centers.append(sum(members) / len(members))
                else:
                    new_centers.append(centers[c])
            if new_centers == centers:
                break
            centers = new_centers
        inertia = sum((data[i] - centers[labels[i]]) ** 2 for i in range(len(data)))
        if inertia < best_inertia:
            best_inertia = inertia
            best_centers = centers[:]
    # final labels
    labels = [min(range(k), key=lambda c: abs(x - best_centers[c])) for x in data]
    return sorted(best_centers), labels


def between_variance(data: List[float], centers: List[float], labels: List[int]) -> float:
    """Between-cluster variance (sum of weighted squared deviations of centers from grand mean)."""
    if not data:
        return 0.0
    grand_mean = sum(data) / len(data)
    k = len(centers)
    bv = 0.0
    for c in range(k):
        members = [data[i] for i, l in enumerate(labels) if l == c]
        if members:
            n_c = len(members)
            bv += n_c * (centers[c] - grand_mean) ** 2
    return bv / len(data)


def total_variance(data: List[float]) -> float:
    if not data:
        return 0.0
    mean = sum(data) / len(data)
    return sum((x - mean) ** 2 for x in data) / len(data)


def gap_statistic_k(data: List[float], max_k: int = 6) -> Tuple[int, List[float]]:
    """Simple gap statistic to find optimal K (1D).

    Gap(k) = log(W_k_uniform) - log(W_k)
    where W_k = within-cluster SS, W_k_uniform = expected W_k under uniform reference distribution.
    Optimal K: first k where gap(k) >= gap(k+1) - sd(k+1).
    """
    if len(data) <= 2:
        return 1, [0.0]

    data_min, data_max = min(data), max(data)
    data_range = max(data_max - data_min, 1e-9)

    n = len(data)
    n_bootstrap = 20
    import random
    rng = random.Random(99)

    def within_ss(data_pts: List[float], k: int) -> float:
        centers, labels = kmeans_1d(data_pts, k)
        return sum((data_pts[i] - centers[labels[i]]) ** 2 for i in range(len(data_pts)))

    gaps = []
    sds = []
    for k in range(1, min(max_k + 1, n)):
        wk = within_ss(data, k)
        if wk <= 0:
            wk = 1e-12
        log_wk = math.log(wk)
        # bootstrap reference
        boot_log_wks = []
        for _ in range(n_bootstrap):
            ref_data = [data_min + rng.random() * data_range for _ in range(n)]
            ref_wk = within_ss(ref_data, k)
            if ref_wk <= 0:
                ref_wk = 1e-12
            boot_log_wks.append(math.log(ref_wk))
        mean_ref = sum(boot_log_wks) / n_bootstrap
        sd_ref = math.sqrt(sum((x - mean_ref) ** 2 for x in boot_log_wks) / n_bootstrap) if n_bootstrap > 1 else 0.0
        gap = mean_ref - log_wk
        gaps.append(gap)
        sds.append(sd_ref * math.sqrt(1 + 1.0 / n_bootstrap))

    # Optimal K: first k where gap(k) >= gap(k+1) - sd(k+1)
    optimal_k = 1
    for i in range(len(gaps) - 1):
        if gaps[i] >= gaps[i + 1] - sds[i + 1]:
            optimal_k = i + 1
            break
    else:
        optimal_k = len(gaps)

    return optimal_k, gaps


# ---------------------------------------------------------------------------
# Load all Bet B retention values
# ---------------------------------------------------------------------------

_instrumentation_selftest()  # called after helpers defined


def load_all_betb_retentions() -> Dict[str, List[float]]:
    """Collect all retention_A values from all Bet B experiments."""
    all_vals: Dict[str, List[float]] = {}
    for d in sorted(DATA.iterdir()):
        if "betB" not in d.name:
            continue
        mf = d / "metrics.json"
        if not mf.exists():
            continue
        try:
            with open(mf) as f:
                m = json.load(f)
        except Exception:
            continue
        # Try per_class structure
        per_class = m.get("summary", {}).get("per_class", {})
        for cls, info in per_class.items():
            vals = info.get("values", [])
            if vals:
                all_vals.setdefault(cls, []).extend(vals)
        # Also try per_seed_pair structure (can be dict or list)
        psp = m.get("per_seed_pair", [])
        if isinstance(psp, dict):
            flat_entries = []
            for sv in psp.values():
                if isinstance(sv, dict):
                    for cell in sv.values():
                        if isinstance(cell, dict):
                            flat_entries.append(cell)
                elif isinstance(sv, list):
                    flat_entries.extend(sv)
            psp = flat_entries
        for entry in psp:
            if not isinstance(entry, dict):
                continue
            ret = entry.get("retention_A")
            if ret is not None:
                all_vals.setdefault("per_seed_pair", []).append(ret)
    return all_vals


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run():
    t0 = time.time()
    out_dir = get_output_dir("wave14_betB_retention_gap_structure_v1")

    # Load all retention values
    all_vals_by_source = load_all_betb_retentions()
    all_vals = [v for vals in all_vals_by_source.values() for v in vals]
    # Deduplicate (some values may appear in multiple experiments)
    all_vals_unique = sorted(set(round(v, 6) for v in all_vals))

    print(f"Loaded {len(all_vals)} retention values ({len(all_vals_unique)} unique) from Bet B experiments")
    print(f"Range: [{min(all_vals_unique):.4f}, {max(all_vals_unique):.4f}]")
    print(f"Mean: {sum(all_vals_unique)/len(all_vals_unique):.4f}")

    # Use unique values to avoid duplicate bias from repeated experiments
    working_vals = all_vals_unique

    # Histogram (10 bins)
    lo, hi = min(working_vals), max(working_vals)
    n_bins = 10
    bin_width = (hi - lo) / n_bins
    bins = [0] * n_bins
    for v in working_vals:
        bi = min(int((v - lo) / bin_width), n_bins - 1)
        bins[bi] += 1
    print("\nHistogram:")
    for i, cnt in enumerate(bins):
        center = lo + (i + 0.5) * bin_width
        bar = "#" * cnt
        print(f"  [{center:.3f}]: {bar} ({cnt})")

    # Gap analysis: find natural breaks
    print("\nGap analysis (sorted unique values, gaps > 0.04):")
    gaps = []
    for i in range(len(working_vals) - 1):
        gap = working_vals[i + 1] - working_vals[i]
        if gap > 0.04:
            gaps.append({"between": (round(working_vals[i], 4), round(working_vals[i + 1], 4)), "gap": round(gap, 4)})
            print(f"  Gap: {working_vals[i]:.4f} -> {working_vals[i+1]:.4f} (delta={gap:.4f})")

    print(f"  Total natural breaks (gap > 0.04): {len(gaps)}")

    # Gap statistic to find optimal K
    print("\nGap statistic:")
    optimal_k, gap_scores = gap_statistic_k(working_vals, max_k=6)
    for k, g in enumerate(gap_scores, start=1):
        print(f"  K={k}: gap={g:.4f}")
    print(f"  Optimal K (gap statistic): {optimal_k}")

    # K-means at optimal K
    centers, labels = kmeans_1d(working_vals, k=optimal_k)
    centers_sorted = sorted(centers)
    print(f"\nK={optimal_k} cluster centers: {[round(c, 4) for c in centers_sorted]}")

    # Cross-check against dispatch-note plateaus
    dispatch_plateaus = [0.94, 0.74, 0.60]
    matches = []
    for p in dispatch_plateaus:
        nearest = min(centers_sorted, key=lambda c: abs(c - p))
        err = abs(nearest - p)
        matches.append({"dispatch_plateau": p, "nearest_center": round(nearest, 4), "error": round(err, 4),
                         "within_05": err < 0.05})
        print(f"  Dispatch plateau {p:.2f}: nearest center={nearest:.4f}, error={err:.4f}, OK={err < 0.05}")

    n_matching = sum(1 for m in matches if m["within_05"])
    print(f"\n{n_matching}/{len(dispatch_plateaus)} dispatch plateaus matched within 0.05")

    # Verdict
    if optimal_k in [2, 3, 4] and n_matching >= 2:
        verdict = "STRUCTURE_FOUND"
        verdict_msg = (
            f"STRUCTURE_FOUND: optimal K={optimal_k} via gap statistic. "
            f"{n_matching}/{len(dispatch_plateaus)} dispatch-note plateaus matched within 0.05. "
            f"Cluster centers: {[round(c, 4) for c in centers_sorted]}. "
            f"Natural retention structure is consistent with 3-plateau model."
        )
    elif optimal_k == 2:
        verdict = "STRUCTURE_BIMODAL"
        verdict_msg = (
            f"STRUCTURE_BIMODAL: optimal K=2 suggests only HIGH vs LOW distinction. "
            f"Centers: {[round(c, 4) for c in centers_sorted]}. "
            f"3-plateau model may be over-specified."
        )
    else:
        verdict = "STRUCTURE_DIFFUSE"
        verdict_msg = (
            f"STRUCTURE_DIFFUSE: optimal K={optimal_k}, "
            f"{n_matching}/{len(dispatch_plateaus)} dispatch plateaus matched. "
            f"Centers: {[round(c, 4) for c in centers_sorted]}. "
            f"Distribution is more spread than 3-plateau model suggests."
        )

    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 2),
        "summary": {
            "n_unique_values": len(working_vals),
            "n_total_values": len(all_vals),
            "value_range": [round(min(working_vals), 4), round(max(working_vals), 4)],
            "optimal_k": optimal_k,
            "cluster_centers": [round(c, 4) for c in centers_sorted],
            "n_dispatch_plateaus_matched": n_matching,
            "dispatch_plateau_matches": matches,
            "n_natural_breaks_gt04": len(gaps),
        },
        "gap_statistic": {f"K{k}": round(g, 4) for k, g in enumerate(gap_scores, start=1)},
        "natural_breaks": gaps,
        "histogram": [{"bin_center": round(lo + (i + 0.5) * bin_width, 3), "count": c} for i, c in enumerate(bins)],
        "config": {"gap_threshold_for_breaks": 0.04, "max_k": 6, "n_bootstrap": 20},
    }
    out_file = out_dir / "metrics.json"
    with open(out_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_file}")


if __name__ == "__main__":
    run()
