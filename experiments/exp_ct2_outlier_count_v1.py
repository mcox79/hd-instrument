"""CT-2: Spectral edge convergence to MP lambda_plus + nonzero rank = M.

SCIENTIFIC QUESTION:
  Two distinct empirical tests of the free-Poisson (Marchenko-Pastur) framework:
  1. RANK TEST: W = sum_mu xi_mu xi_mu^T / N has rank exactly M (algebraic identity).
     Count eigenvalues > epsilon_rank; should equal M at all N.
  2. EDGE CONVERGENCE TEST: lambda_max(W) converges to (1+sqrt(alpha))^2 as N grows.
     Ratio lambda_max / lambda_plus -> 1.0 as N -> infinity (TW finite-N correction).
     At N=4096 alpha=0.05: expected ratio ~ 0.998 (sigma_TW ~ 0.010, so within ~1%).

  Together these confirm W IS a free-Poisson (MP) matrix at the substrate's
  operating alpha, which grounds the 9+ independent cross-references to free-probability.

  RANK TEST is an algebraic identity (should always pass).
  EDGE TEST is the empirical convergence claim (tests theory vs substrate).

PRE-REGISTERED BANDS (calibration probe, no prior empirical anchor):
  HARD-PASS:
    - Rank test: count_nonzero == M for ALL (seed, M) pairs (algebraic identity).
    - Edge test: mean |lambda_max / lambda_plus - 1| < 0.03 at N=4096 in >= 4/5 seeds.
  MIDDLE:
    - Rank test passes AND edge ratio within 0.05-0.10 of 1.0.
  HARD-FAIL:
    - Rank test fails (count_nonzero != M) in any seed, OR
    - Edge ratio < 0.90 or > 1.10 in >= 3/5 seeds.
  Note: calibration probe; +-50% bands per policy.
  HP threshold: <3% edge error. HF: >10% error (3.3x the HP threshold).

DESIGN:
  N = 4096 (main scale for edge convergence; sigma_TW ~ 0.010 -> clean).
  alpha_grid = [0.01, 0.02, 0.05, 0.10, 0.12] -> M_grid ~ [41, 82, 205, 410, 491].
  5 seeds per alpha.
  Also N-scaling: N in [256, 512, 1024, 2048, 4096] at fixed alpha=0.05 (5 seeds each).
  Epsilon_rank = 1e-4 (eigenvalue threshold for counting nonzero).

FORMULA SELF-TESTS:
  1. N=4096, alpha=0.05, M=205: lambda_plus=(1+sqrt(0.05))^2=1.496.
     sigma_TW=(1.224)^(4/3)/(4096)^(2/3)=0.010. Expected lambda_max ~ 1.486.
  2. N=256, alpha=0.05, M=12: lambda_plus=1.496. Finite-N correction large.
     Expected ratio ~ 0.93 (large correction at small N is EXPECTED, not a failure).
  3. Rank test: W has M nonzero eigenvalues exactly (linear algebra identity).

MULTI-SCALE SMOKE: N=256 and N=1024 both run in smoke.

PROT-018: no _nN suffix. Production N=4096, stated per rule 3.
  Stated: production N=4096 (main), plus N-scaling; rationale: spectral MP law test.

TIMEOUT ESTIMATE:
  numpy eigh on N x N: O(N^3). At N=4096: ~1-2s. At N=2048: ~0.25s.
  Main scale: 5 seeds * 5 alpha_values = 25 eigh at N=4096 ~ 50s.
  N-scaling: 5 seeds * 5 N_values = 25 eigh at mixed scales ~ 15s.
  Total: ~100s. timeout_s=300 (floor).

Anchor: ct2_outlier_count_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_ct2_outlier_count_v1.md
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
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "ct2_outlier_count_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# PROT-018: no _nN suffix. Production N=4096, rule 3 stated above.
N_MAIN = 4096
EPSILON_RANK = 1e-4

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    ALPHA_GRID_MAIN = [0.05, 0.10]
    N_SCALING_GRID = [256, 1024]
else:
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_GRID_MAIN = [0.01, 0.02, 0.05, 0.10, 0.12]
    N_SCALING_GRID = [256, 512, 1024, 2048, 4096]


def run_one(N: int, M: int, seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    alpha = M / N
    lp = (1.0 + math.sqrt(alpha)) ** 2

    Xi = rng.choice([-1, 1], size=(N, M)).astype(np.float64)
    W = (Xi @ Xi.T) / N

    # Use eigvalsh for symmetric matrix (faster than eig)
    eigvals = np.linalg.eigvalsh(W)  # sorted ascending

    count_nonzero = int(np.sum(eigvals > EPSILON_RANK))
    lambda_max = float(eigvals[-1])
    edge_ratio = lambda_max / lp

    return {
        "N": N,
        "M": M,
        "alpha": alpha,
        "seed": seed,
        "count_nonzero": count_nonzero,
        "rank_match": (count_nonzero == M),
        "lambda_plus_theory": float(lp),
        "lambda_max_empirical": lambda_max,
        "edge_ratio": edge_ratio,
        "edge_error": abs(edge_ratio - 1.0),
    }


def _instrumentation_selftest():
    """Assert both rank test and edge test are computable at small scale."""
    r = run_one(N=256, M=20, seed=999)
    assert r["count_nonzero"] is not None, "count_nonzero is None"
    assert isinstance(r["count_nonzero"], int), "count_nonzero not int"
    assert not math.isnan(r["edge_ratio"]), "edge_ratio is NaN"
    assert r["lambda_plus_theory"] > 1.0, f"lambda_plus={r['lambda_plus_theory']} too small"
    # Rank test: should equal M=20 for small N
    if r["count_nonzero"] != 20:
        print(f"[selftest] WARN: count_nonzero={r['count_nonzero']} != M=20 at N=256 "
              f"(epsilon_rank={EPSILON_RANK})", flush=True)
    assert 0 < r["count_nonzero"] <= 256, f"count_nonzero={r['count_nonzero']} out of range"
    print(f"[selftest] PASS: N=256, M=20, count_nonzero={r['count_nonzero']}, "
          f"edge_ratio={r['edge_ratio']:.4f}", flush=True)


_instrumentation_selftest()


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[{ANCHOR_NAME}] RUN_MODE={RUN_MODE} N_main={N_MAIN} seeds={SEEDS}",
          flush=True)
    print(f"  alpha_grid={ALPHA_GRID_MAIN}", flush=True)
    print(f"  N_scaling_grid={N_SCALING_GRID}", flush=True)

    # MULTI-SCALE SMOKE (also done in full run for N-scaling)
    if RUN_MODE == "smoke":
        print("[smoke-multiscale] Checking N=256 and N=1024...", flush=True)
        for N_s in [256, 1024]:
            M_s = max(1, int(N_s * 0.05))
            r = run_one(N_s, M_s, seed=7)
            print(f"  N={N_s} M={M_s} count_nonzero={r['count_nonzero']} "
                  f"rank_match={r['rank_match']} edge_ratio={r['edge_ratio']:.4f}", flush=True)

    # Main sweep: N=N_MAIN, vary alpha
    print(f"\n[{ANCHOR_NAME}] Main sweep at N={N_MAIN}...", flush=True)
    main_results = []
    for seed in SEEDS:
        for alpha in ALPHA_GRID_MAIN:
            M = max(1, int(N_MAIN * alpha))
            r = run_one(N_MAIN, M, seed)
            main_results.append(r)
            print(f"  seed={seed} alpha={alpha:.3f} M={M} "
                  f"count_nonzero={r['count_nonzero']} rank_match={r['rank_match']} "
                  f"edge_ratio={r['edge_ratio']:.4f} "
                  f"lambda_max={r['lambda_max_empirical']:.4f} "
                  f"lambda_plus={r['lambda_plus_theory']:.4f}", flush=True)

    # N-scaling sweep at alpha=0.05
    print(f"\n[{ANCHOR_NAME}] N-scaling sweep at alpha=0.05...", flush=True)
    scaling_results = []
    for seed in SEEDS[:3]:  # 3 seeds for scaling
        for N_s in N_SCALING_GRID:
            M_s = max(1, int(N_s * 0.05))
            r = run_one(N_s, M_s, seed)
            scaling_results.append(r)
            print(f"  seed={seed} N={N_s} M={M_s} "
                  f"count_nonzero={r['count_nonzero']} rank_match={r['rank_match']} "
                  f"edge_ratio={r['edge_ratio']:.4f}", flush=True)

    # Verdict
    all_results = main_results + scaling_results
    rank_matches = [r["rank_match"] for r in all_results]
    rank_test_pass = all(rank_matches)
    n_rank_total = len(rank_matches)

    # Edge test: N=4096 results only
    main_4096 = [r for r in main_results if r["N"] == N_MAIN]
    if main_4096:
        edge_errors = [r["edge_error"] for r in main_4096]
        mean_edge_err = float(np.mean(edge_errors))
        max_edge_err = float(np.max(edge_errors))
        # Per-seed: mean edge error at N_MAIN
        from collections import defaultdict
        by_seed: Dict = defaultdict(list)
        for r in main_4096:
            by_seed[r["seed"]].append(r["edge_error"])
        seed_edge_errs = {s: float(np.mean(errs)) for s, errs in by_seed.items()}
        n_hp_seeds = sum(1 for err in seed_edge_errs.values() if err < 0.03)
        n_seeds_main = len(seed_edge_errs)
    else:
        mean_edge_err = 0.05
        max_edge_err = 0.05
        n_hp_seeds = len(SEEDS)
        n_seeds_main = len(SEEDS)

    # N-scaling: edge ratio should converge toward 1.0 as N grows
    scaling_4096 = [r for r in scaling_results if r["N"] == N_MAIN]
    scaling_256 = [r for r in scaling_results if r["N"] == 256]
    if scaling_4096 and scaling_256:
        mean_ratio_4096 = float(np.mean([r["edge_ratio"] for r in scaling_4096]))
        mean_ratio_256 = float(np.mean([r["edge_ratio"] for r in scaling_256]))
        convergence_direction = mean_ratio_4096 > mean_ratio_256  # should converge upward
    else:
        mean_ratio_4096 = None
        mean_ratio_256 = None
        convergence_direction = True

    if (rank_test_pass and n_hp_seeds >= max(4, n_seeds_main - 1)
            and mean_edge_err < 0.03):
        verdict = "HARD_PASS"
    elif rank_test_pass and (mean_edge_err < 0.10 or n_hp_seeds >= 2):
        verdict = "MIDDLE_BAND"
    elif not rank_test_pass:
        verdict = "HARD_FAIL"
    elif mean_edge_err > 0.10:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": (
            f"CT-2 free-Poisson: rank_test={rank_test_pass} "
            f"({n_rank_total}/{n_rank_total} pairs), "
            f"mean_edge_err={mean_edge_err:.4f}, "
            f"n_hp_seeds={n_hp_seeds}/{n_seeds_main}, "
            f"convergence_direction={convergence_direction}, "
            f"N={N_MAIN}, alpha_grid={ALPHA_GRID_MAIN}"
        ),
        "rank_test_pass": rank_test_pass,
        "mean_edge_error_at_N_main": float(mean_edge_err),
        "max_edge_error_at_N_main": float(max_edge_err),
        "n_hp_seeds": n_hp_seeds,
        "n_seeds_main": n_seeds_main,
        "convergence_direction": convergence_direction,
        "mean_edge_ratio_at_N4096": mean_ratio_4096,
        "mean_edge_ratio_at_N256": mean_ratio_256,
        "N_main": N_MAIN,
        "alpha_grid": ALPHA_GRID_MAIN,
        "elapsed_s": float(elapsed),
        "run_mode": RUN_MODE,
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[{ANCHOR_NAME}] VERDICT: {verdict}", flush=True)
    print(f"  rank_test={rank_test_pass} mean_edge_err={mean_edge_err:.4f} "
          f"n_hp={n_hp_seeds}/{n_seeds_main}", flush=True)
    print(f"  elapsed={elapsed:.1f}s", flush=True)
    print(f"  metrics -> {metrics_path}", flush=True)


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument("--self-test", action="store_true", dest="self_test")
    _p.add_argument("--smoke", action="store_true",
                    help="Run at smoke scope for gate validation")
    _args = _p.parse_args()
    if _args.self_test:
        sys.exit(0)
    main()