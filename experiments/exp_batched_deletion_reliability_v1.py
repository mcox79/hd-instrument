"""Q22 -- Batched deletion verification reliability R(k).

SCIENTIFIC QUESTION:
  Does batched deletion reliability follow R(k) ~ r_1^k for independent S_delete?
  And is the correlated case (c~0.3-0.5 semantic relatedness) worse than r_1^k?
  Sweep k in {1, 5, 10, 20, 50} for both independent and moderately-correlated sets.

THEORY (Q22 DEEPENED, research drill 2026-06-01):
  W_new = W - sum_{i in S_delete} xi_i xi_i^T / N is algebraically exact
  (linearity of outer-product). Joint reliability R(k) ~ r_1^k for independent S_delete.
  At r_1=0.92: k=10 -> R~0.43; k=50 -> R~0.016.
  CORRELATED case: ghost-attractor at cluster centroid not removed by per-pattern
  subtraction; reliability degrades faster than r_1^k for moderately correlated
  (c~0.3-0.5 cosine) delete sets.

PRE-REGISTERED BANDS:
  HARD-PASS:
    - independent case: empirical R(k) matches r_1^k within 2pp for all k in {1,5,10,20}.
      (k=50 may deviate due to very low R -- tolerance 5pp at k=50.)
    - correlated case: R(k) characterized (whether worse than r_1^k for c~0.3-0.5).
      HP criterion for correlated: R(k=10)_corr / R(k=10)_indep measured and reported.
  MIDDLE: independent case matches within 5pp but not 2pp for some k.
  HARD-FAIL: independent case deviates > 10pp from r_1^k prediction at k <= 10
             (algebraic independence assumption violated).

DESIGN:
  N=4096, M=200 stored random patterns.
  Estimate r_1 = single-pattern deletion reliability from k=1 measurement.
  Then verify k in {5, 10, 20, 50} vs r_1^k prediction.
  Two delete-set types:
  (a) Independent: k random patterns from S.
  (b) Correlated: k patterns drawn from a "cluster" -- all near the same centroid
      (cosine similarity ~0.3-0.5). Create by starting from a random vector and
      adding noise: xi_i = sign(centroid + eps_i * noise) for small eps_i.
  Reliability measurement: after deleting k patterns, compute overlap with each
  deleted pattern. Reliable deletion = overlap < threshold (pattern not retrieved).
  Threshold: 0.5 * (overlap_before_delete). If post-delete overlap < threshold, success.
  5 seeds.

FORMULA SELF-TESTS:
  1. k=1: r_1 = P(overlap_after < threshold). Expected ~0.88-0.96 from theory.
  2. k=10 independent: R_pred = r_1^10. If r_1=0.92: R_pred=0.43.
     R_empirical should be within 2pp of 0.43.
  3. Correlated cluster: centroid = sign(sum xi_i) / sqrt(k). After deleting all k,
     ghost attractor at centroid may persist. Test: does overlap with centroid remain high?

PROT-018: no _nN suffix. Production N=4096 per rule 3.
  Stated: production N = 4096; rationale: batched deletion characterization.

TIMEOUT ESTIMATE:
  5 seeds * 5 k_values * 2 types * (M=200 writes + k deletes + eval).
  Per (seed, k, type): ~0.1s at N=4096. Total: 5*5*2*0.1 = 5s. timeout=300.

Anchor: batched_deletion_reliability_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_batched_deletion_reliability_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial  # noqa: E402

ANCHOR_NAME = "batched_deletion_reliability_v1"

# Production config
N = 4096
M = 200
K_GRID = [1, 5, 10, 20, 50]
CORR_LEVEL = 0.40  # target cosine similarity for correlated patterns
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]

# Pre-registered thresholds
HP_INDEP_TOLERANCE   = 0.02  # within 2pp of r_1^k
HP_K50_TOLERANCE     = 0.05  # wider tolerance at k=50
HF_INDEP_DEVIATION   = 0.10  # > 10pp at k <= 10 is HARD_FAIL


def build_w(patterns: np.ndarray, N: int) -> np.ndarray:
    W = (patterns.T @ patterns) / N
    np.fill_diagonal(W, 0.0)
    return W


def make_correlated_cluster(k: int, N: int, corr_level: float,
                            rng: np.random.Generator) -> np.ndarray:
    """Make k binary patterns with mutual cosine similarity ~ corr_level."""
    # Centroid vector
    centroid = rng.choice([-1.0, 1.0], size=N).astype(np.float64)
    # Noise fraction that gives target cosine similarity
    # cos(a, b) ~ 1 - 2*noise_frac (for +/-1 vectors)
    noise_frac = (1.0 - corr_level) / 2.0
    patterns = []
    for _ in range(k):
        p = centroid.copy()
        n_flip = max(1, int(noise_frac * N))
        flip_idx = rng.choice(N, size=n_flip, replace=False)
        p[flip_idx] *= -1
        patterns.append(p)
    return np.array(patterns)


def delete_patterns(W: np.ndarray, patterns: np.ndarray, N: int) -> np.ndarray:
    """Delete k patterns from W: W_new = W - sum xi_i xi_i^T / N."""
    W_new = W.copy()
    for xi in patterns:
        W_new -= np.outer(xi, xi) / N
    np.fill_diagonal(W_new, 0.0)
    return W_new


def measure_deletion_reliability(W_original: np.ndarray, W_deleted: np.ndarray,
                                  del_patterns: np.ndarray, N: int) -> float:
    """Fraction of deleted patterns with post-delete overlap < threshold.

    Threshold = 0.5 * (pre-delete overlap). Uses direct pattern overlap.
    """
    n_success = 0
    all_patterns = del_patterns  # just deleted ones
    for xi in all_patterns:
        # Pre-delete overlap with original W
        pre_ov = float(abs(np.dot(xi, W_original @ xi)) / N)
        # Post-delete overlap
        post_ov = float(abs(np.dot(xi, W_deleted @ xi)) / N)
        threshold = 0.5 * pre_ov if pre_ov > 0.01 else 0.10
        if post_ov < threshold:
            n_success += 1
    return n_success / max(len(all_patterns), 1)


def run_seed(seed: int, N: int, M: int, k_grid: List[int], corr_level: float) -> Dict:
    """Run batched deletion test for one seed."""
    rng = np.random.default_rng(seed)
    patterns = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
    W = build_w(patterns, N)

    results = {}
    for k in k_grid:
        # Independent delete set: k random patterns
        del_idx_indep = rng.choice(M, size=k, replace=False).tolist()
        del_pats_indep = patterns[del_idx_indep]
        W_del_indep = delete_patterns(W, del_pats_indep, N)
        r_indep = measure_deletion_reliability(W, W_del_indep, del_pats_indep, N)

        # Correlated delete set: k patterns from a cluster
        del_pats_corr = make_correlated_cluster(k, N, corr_level, rng)
        # Add correlated patterns to W first (they're not in S -- add then delete)
        W_with_corr = W.copy()
        for xi in del_pats_corr:
            W_with_corr += np.outer(xi, xi) / N
        np.fill_diagonal(W_with_corr, 0.0)
        W_del_corr = delete_patterns(W_with_corr, del_pats_corr, N)
        r_corr = measure_deletion_reliability(W_with_corr, W_del_corr, del_pats_corr, N)

        results[str(k)] = {
            "k": k,
            "r_indep": r_indep,
            "r_corr": r_corr,
        }

    return {"seed": seed, "k_results": results}


# ---------------------------------------------------------------------------
# Instrumentation self-test
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert deletion reliability metrics non-null at tiny scale."""
    res = run_seed(42, 256, 20, [1, 5], 0.40)
    assert "k_results" in res, "k_results missing"
    k1 = res["k_results"]["1"]
    assert "r_indep" in k1 and "r_corr" in k1, "r fields missing"
    assert 0.0 <= k1["r_indep"] <= 1.0, f"r_indep OOB: {k1['r_indep']}"
    assert 0.0 <= k1["r_corr"] <= 1.0, f"r_corr OOB: {k1['r_corr']}"
    print("[selftest] PASS: batched_deletion_reliability_v1 metrics non-null", flush=True)


_instrumentation_selftest()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    run_mode = os.environ.get("HDLAB_RUN_MODE", "full")
    seeds = SEEDS_FULL if run_mode == "full" else SEEDS_SMOKE
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_config = {"N": N, "run_mode": run_mode}

    print(f"[{ANCHOR_NAME}] run_mode={run_mode} N={N} M={M} K_GRID={K_GRID} seeds={seeds}", flush=True)

    done, remaining = resumable_seeds(seeds, out_dir, run_config=run_config)
    print(f"[{ANCHOR_NAME}] checkpoint: {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        print(f"  seed={seed}...", flush=True)
        res = run_seed(seed, N, M, K_GRID, CORR_LEVEL)
        res["N"] = N
        res["run_mode"] = run_mode
        for k, v in res["k_results"].items():
            print(f"    k={k}: r_indep={v['r_indep']:.4f} r_corr={v['r_corr']:.4f}", flush=True)
        write_partial(out_dir, seed, res)

    from experiments._seed_checkpoint import aggregate_partials
    per_seed = aggregate_partials(out_dir, seeds, run_config=run_config)

    # Aggregate per k
    k_agg: Dict[str, Dict] = {}
    for k in K_GRID:
        ks = str(k)
        r_indeps = [p["k_results"][ks]["r_indep"] for p in per_seed.values() if ks in p.get("k_results", {})]
        r_corrs  = [p["k_results"][ks]["r_corr"]  for p in per_seed.values() if ks in p.get("k_results", {})]
        k_agg[ks] = {
            "k": k,
            "mean_r_indep": float(np.mean(r_indeps)) if r_indeps else float("nan"),
            "mean_r_corr":  float(np.mean(r_corrs))  if r_corrs  else float("nan"),
            "std_r_indep":  float(np.std(r_indeps))  if r_indeps else float("nan"),
        }

    # Estimate r_1 from k=1 result
    r1_val = k_agg.get("1", {}).get("mean_r_indep", float("nan"))

    # Verify r_1^k prediction for independent case
    deviations = {}
    max_dev_small_k = float("nan")
    if not math.isnan(r1_val):
        devs = []
        for k in [5, 10, 20]:
            ks = str(k)
            r_pred = r1_val ** k
            r_emp  = k_agg.get(ks, {}).get("mean_r_indep", float("nan"))
            if not math.isnan(r_emp):
                dev = abs(r_emp - r_pred)
                deviations[ks] = {"r_pred": r_pred, "r_emp": r_emp, "dev": dev}
                devs.append(dev)
        max_dev_small_k = max(devs) if devs else float("nan")

    if (not math.isnan(max_dev_small_k) and max_dev_small_k < HP_INDEP_TOLERANCE):
        verdict = "HARD_PASS"
    elif (not math.isnan(max_dev_small_k) and max_dev_small_k > HF_INDEP_DEVIATION):
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "anchor": ANCHOR_NAME, "run_mode": run_mode, "N": N, "M": M,
        "n_seeds": len(seeds), "r1_estimate": r1_val,
        "k_aggregates": k_agg, "deviations_from_r1k": deviations,
        "max_deviation_small_k": max_dev_small_k,
        "verdict": verdict, "elapsed_s": elapsed,
        "thresholds": {
            "HP_indep_tolerance": HP_INDEP_TOLERANCE,
            "HF_indep_deviation": HF_INDEP_DEVIATION,
        },
        "verdict_msg": (
            f"Batched deletion reliability N={N} M={M}: r_1={r1_val:.4f}, "
            f"max_dev_small_k(k<=20)={max_dev_small_k:.4f} (HP<{HP_INDEP_TOLERANCE}). "
            f"Correlated case (c={CORR_LEVEL}) characterized: "
            f"r_corr(k=10)={k_agg.get('10',{}).get('mean_r_corr',float('nan')):.4f} "
            f"vs r_indep(k=10)={k_agg.get('10',{}).get('mean_r_indep',float('nan')):.4f}. "
            f"Verdict={verdict}."
        ),
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict} r1={r1_val:.4f} max_dev={max_dev_small_k:.4f} elapsed={elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument("--self-test", action="store_true", dest="self_test")
    _args = _p.parse_args()
    if _args.self_test:
        sys.exit(0)
    main()
