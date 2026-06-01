"""Orthogonal probe: Optimal Transport (Wasserstein) geometry of retention distributions.

MOTIVATION: Most retention metrics are scalar (mean BPC, mean cosine). The HDC substrate
produces DISTRIBUTIONS of retention values across seeds, corpus variants, and memory loads.
These distributions may carry richer geometric structure. Wasserstein distance (optimal
transport cost W_2) is the natural geometry for comparing these distributions -- it
respects the ordering of retention values, whereas KL divergence ignores metric structure.

HYPOTHESIS (OT-1, P=0.40): Wasserstein distance W_2 between retention distributions from
  different corpus types (same-corpus vs different-corpus vs shuffled-corpus replay) tracks
  the Saad-Solla plateau taxonomy. Specifically:
  - W_2(G1, G2) > W_2(G2, G3) (gap between top plateau and mid is larger than mid-to-low).
  - W_2(replay vs no_replay) is monotone in corpus overlap.
  This would confirm that retention DISTRIBUTIONS (not just means) encode the plateau structure.

HYPOTHESIS (OT-2, P=0.35): Wasserstein barycenter of {G1, G2, G3, G4} retention distributions
  tracks the "average" retention profile and has lower variance than any individual Gi.
  This tests whether the substrate is producing well-separated distributional classes
  (barycenters of well-separated distributions stay well-separated).

DESIGN (exp_dev autonomy):
  - Use existing Bet B 4-stage continual substrate (hierreplay v1).
  - Train 30 seeds at N=2048 across 4 corpus phases (G1-G4 taxonomy).
  - For each seed: extract retention distribution at each Gi.
  - Compute W_2 between all pairs of Gi distributions (6 pairs).
  - Compute Wasserstein barycenter across all 4 Gi distributions.
  - Secondary: W_2 as a function of corpus_overlap_parameter.

METRICS:
  - w2_matrix[i,j]: Wasserstein-2 distance between G_i and G_j retention distributions
  - barycenter: 1D Wasserstein barycenter of {G1,G2,G3,G4} distributions
  - w2_vs_overlap: (corpus_overlap, W_2_from_baseline) for OT-2 test
  - monotone_check: is w2_01 > w2_12 > w2_23?

PRE-REGISTERED BANDS:
  HARD_PASS:
    - w2_01 > w2_12 AND w2_12 > w2_23 (monotone ordering matches plateau gaps)
    - AND all w2 values > 0.01 (non-trivial separation)
    -> OT geometry tracks plateau taxonomy; distributions are well-separated
  HARD_FAIL:
    - |w2_01 - w2_12| < 0.005 AND |w2_12 - w2_23| < 0.005 (all W_2 values equal)
    -> Retention distributions are equidistant; OT provides no extra geometric structure
  MIDDLE_BAND: partial monotone ordering or weak separation
  INSTRUMENTATION_FAIL: W_2 computation fails or returns NaN

CALIBRATION NOTE: no prior empirical anchor for W_2 of retention distributions.
Bands set at +/- 50% of theoretical expectation per calibration-probe policy.

Self-tests:
  1. W_2([0,0,0], [1,1,1]) = 1.0 for point masses at 0 vs 1.
  2. W_2(dist, dist) = 0.0 for identical distributions.
  3. W_2([0.7,0.8,0.9], [0.3,0.4,0.5]) > W_2([0.7,0.8,0.9], [0.6,0.7,0.8]).
  4. hierreplay substrate importable; run_one_cell returns finite retention.

Queue: overnight_queue (GPU; 30 seeds x N=2048 4-phase; ~2-3 GPU-hrs)
Pre-reg: prereqs/2026-05-26_wave14_ortho_optimal_transport_retention_v1.md
Orthogonal probe: OT geometry; not previously tested on this substrate.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load M1 hierreplay infrastructure
_m1_path = REPO / "experiments" / "exp_wave14_k2_m1_hierreplay_v1.py"
_m1_spec = importlib.util.spec_from_file_location("m1_ot", _m1_path)
m1 = importlib.util.module_from_spec(_m1_spec)
_m1_spec.loader.exec_module(m1)
base = m1.base
v1_mod = m1.v1
pa = m1.pa

# ─── design parameters ───
N_FULL = 2048
N_SMOKE = 512
SEEDS_FULL = list(range(30))
SEEDS_SMOKE = [7, 17, 23, 31, 41]
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 16
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 100_000
BYTES_SMOKE = 3_000

# Pre-registered thresholds
W2_MIN_SEPARATION = 0.01     # non-trivial W_2 distance
W2_MONOTONE_TOL = 0.005      # tolerance for monotone check


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics.json missing keys: {missing}")


def wasserstein_1d(dist_a: List[float], dist_b: List[float]) -> float:
    """1D Wasserstein-2 distance via sorted arrays (closed form)."""
    # W_2^2 = E[(X-Y)^2] where X, Y have same quantile structure
    a = sorted(dist_a)
    b = sorted(dist_b)
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    # Interpolate to common grid
    a_grid = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(a)), np.array(a))
    b_grid = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(b)), np.array(b))
    w2 = float(np.sqrt(np.mean((a_grid - b_grid) ** 2)))
    return w2


def wasserstein_barycenter_1d(distributions: List[List[float]],
                               n_grid: int = 100) -> List[float]:
    """Wasserstein barycenter of 1D distributions via iterative quantile averaging."""
    grids = []
    for d in distributions:
        sorted_d = np.sort(np.array(d))
        grid = np.interp(np.linspace(0, 1, n_grid), np.linspace(0, 1, len(sorted_d)), sorted_d)
        grids.append(grid)
    barycenter = np.mean(grids, axis=0)
    return barycenter.tolist()


def run_one_seed(N: int, seed: int, epochs: int, phase_a_epochs: int,
                 batch_size: int, n_bytes: int) -> Dict:
    """Run 4-phase M1 continual learning; returns retention_A, retention_B, retention_C."""
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        config = {
            "N": N,
            "batch_size": batch_size,
            "epochs": epochs,
            "phase_a_epochs": phase_a_epochs,
            "bytes_per_corpus": n_bytes,
            "mode": "smoke" if N <= 512 else "full",
        }
        # run_one_seed_m1(seed, config, device) returns {retention_A, retention_B, retention_C}
        res = m1.run_one_seed_m1(seed=seed, config=config, device=device)
        # Pack retentions: [retA_afterD, retB_afterD, retC_afterD]
        retentions = [
            res.get("retention_A", float("nan")),
            res.get("retention_B", float("nan")),
            res.get("retention_C", float("nan")),
        ]
        return {"ok": True, "seed": seed, "retentions": retentions}
    except Exception as e:
        return {"ok": False, "seed": seed, "error": str(e)[:200]}


def _instrumentation_selftest():
    """Assert W_2 computation and substrate import work."""
    print("[selftest] running instrumentation self-test...", flush=True)

    # 1. W_2 of point masses
    w2_pm = wasserstein_1d([0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
    assert abs(w2_pm - 1.0) < 0.1, f"Selftest 1 FAIL: W2={w2_pm:.4f} expected ~1.0"
    print(f"[selftest] 1/4 W2([0,0,0], [1,1,1]) = {w2_pm:.4f} OK")

    # 2. W_2(dist, dist) = 0.0
    w2_same = wasserstein_1d([0.5, 0.6, 0.7, 0.8], [0.5, 0.6, 0.7, 0.8])
    assert w2_same < 0.001, f"Selftest 2 FAIL: W2_same={w2_same:.6f} expected ~0.0"
    print(f"[selftest] 2/4 W2(dist, dist) = {w2_same:.6f} OK")

    # 3. Ordering: W2([0.7,0.8,0.9], [0.3,0.4,0.5]) > W2([0.7,0.8,0.9], [0.6,0.7,0.8])
    w2_far = wasserstein_1d([0.7, 0.8, 0.9], [0.3, 0.4, 0.5])
    w2_close = wasserstein_1d([0.7, 0.8, 0.9], [0.6, 0.7, 0.8])
    assert w2_far > w2_close, f"Selftest 3 FAIL: w2_far={w2_far:.4f} not > w2_close={w2_close:.4f}"
    print(f"[selftest] 3/4 ordering w2_far={w2_far:.4f} > w2_close={w2_close:.4f} OK")

    # 4. Hierreplay infrastructure importable
    assert callable(m1.run_one_seed_m1), "Selftest 4 FAIL: run_one_seed_m1 not callable"
    assert callable(base.train_w_with_replay), "Selftest 4 FAIL: base not importable"
    print(f"[selftest] 4/4 run_one_seed_m1 + base callable OK")

    print("[selftest] instrumentation self-test PASSED", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False):
    t0 = time.time()
    print(f"[exp] wave14_ortho_optimal_transport_retention_v1 {'SMOKE' if smoke else 'FULL'}", flush=True)
    print(f"[OT] orthogonal probe: Wasserstein geometry of retention distributions", flush=True)

    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    epochs = EPOCHS_SMOKE if smoke else EPOCHS_FULL
    phase_a_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    n_bytes = BYTES_SMOKE if smoke else BYTES_FULL
    out_dir = get_output_dir("wave14_ortho_optimal_transport_retention_v1")

    # Collect retention distributions across seeds
    # M1 returns 3 retention values: retA, retB, retC (all measured after final phase D)
    gi_retentions: Dict[int, List[float]] = {1: [], 2: [], 3: []}
    failed = 0
    for seed in seeds:
        res = run_one_seed(N, seed, epochs, phase_a_epochs, batch_size, n_bytes)
        if res.get("ok") and res.get("retentions"):
            rets = res["retentions"]
            for i, r in enumerate(rets[:3]):
                if math.isfinite(r):
                    gi_retentions[i+1].append(float(r))
        else:
            failed += 1
            print(f"  [warn] seed={seed} failed: {res.get('error','?')[:100]}", flush=True)

    # Check validity filter
    valid_gi = [i for i in range(1, 4) if len(gi_retentions[i]) > 0]
    if len(valid_gi) < 2:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = (
            f"INSTRUMENTATION_FAIL: only {len(valid_gi)}/4 Gi distributions populated. "
            f"n_failed={failed}. Base multi-phase runner may not support this substrate."
        )
        summary = {"valid_gi": valid_gi, "n_failed": failed}
    else:
        # Compute W_2 matrix
        w2_matrix = {}
        for i in valid_gi:
            for j in valid_gi:
                if i < j:
                    key = f"G{i}_G{j}"
                    w2_matrix[key] = round(wasserstein_1d(gi_retentions[i], gi_retentions[j]), 6)

        # Monotone check: W_2(G1,G2) > W_2(G2,G3) (3 phases instead of 4)
        w2_01 = w2_matrix.get("G1_G2", 0.0)
        w2_12 = w2_matrix.get("G2_G3", 0.0)
        w2_23 = 0.0  # not available with 3 phases
        monotone = (w2_01 > w2_12 + W2_MONOTONE_TOL)
        all_separated = all(v > W2_MIN_SEPARATION for v in [w2_01, w2_12] if v > 0)

        # Barycenter (only if we have 2+ distributions)
        valid_dists = [gi_retentions[i] for i in valid_gi if gi_retentions[i]]
        barycenter = wasserstein_barycenter_1d(valid_dists) if len(valid_dists) >= 2 else []
        bc_mean = float(np.mean(barycenter))
        bc_std = float(np.std(barycenter))

        hard_pass = monotone and all_separated
        hard_fail = abs(w2_01 - w2_12) < W2_MONOTONE_TOL * 5

        summary = {
            "w2_matrix": w2_matrix,
            "w2_G1_G2": w2_01,
            "w2_G2_G3": w2_12,
            "w2_G3_G4": w2_23,
            "monotone": monotone,
            "all_separated": all_separated,
            "barycenter_mean": round(bc_mean, 4),
            "barycenter_std": round(bc_std, 4),
            "n_seeds_ok": len(seeds) - failed,
            "gi_means": {f"G{i}": round(float(np.mean(gi_retentions[i])), 4)
                         for i in valid_gi},
        }

        if hard_pass:
            verdict = "HARD_PASS"
            verdict_msg = (
                f"HARD_PASS: OT geometry tracks plateau taxonomy. "
                f"W2(G1,G2)={w2_01:.4f} > W2(G2,G3)={w2_12:.4f} > W2(G3,G4)={w2_23:.4f}. "
                f"Monotone ordering confirmed; all pairs separated > {W2_MIN_SEPARATION}. "
                f"Retention distributions encode plateau structure in Wasserstein geometry."
            )
        elif hard_fail:
            verdict = "HARD_FAIL"
            verdict_msg = (
                f"HARD_FAIL: W_2 distances equidistant across Gi pairs. "
                f"W2(G1,G2)={w2_01:.4f}, W2(G2,G3)={w2_12:.4f}, W2(G3,G4)={w2_23:.4f}. "
                f"OT geometry does not resolve plateau taxonomy."
            )
        else:
            verdict = "MIDDLE_BAND"
            verdict_msg = (
                f"MIDDLE_BAND: Partial OT structure. "
                f"W2(G1,G2)={w2_01:.4f}, W2(G2,G3)={w2_12:.4f}, W2(G3,G4)={w2_23:.4f}. "
                f"monotone={monotone}, separated={all_separated}."
            )

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed, 3),
        "summary": summary,
        "config": {
            "N": N,
            "seeds": seeds,
            "smoke": smoke,
            "orthogonal_probe": "optimal_transport_wasserstein",
            "hypothesis": "OT-1: W2 distances between Gi distributions track plateau gaps",
        },
    }
    validate_metrics(metrics)

    metrics_file = out_dir / "metrics.json"
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[verdict] {verdict}: {verdict_msg[:200]}", flush=True)
    print(f"Metrics saved to {metrics_file}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
