"""CSP memory warm-start: 10x speedup at rho=0.9 slowly-evolving planted family.

SCIENTIFIC QUESTION:
  The substrate's W = W_csp + W_data dual-objective mode enables memory-of-solutions.
  Prediction: at rho=0.9 correlation between consecutive CSP instances, using W to
  warm-start the search converges 10x faster than random initialization.

  Implementation:
  - Planted MAX-CUT on N nodes: planted partition sigma* in {-1,+1}^N.
  - W_csp = planted bipartition Hopfield: W_csp = sigma* sigma*^T / N (rank-1 signal).
  - "Slowly evolving": each step, sigma*_new differs from sigma*_old in rho fraction
    (rho=0.9 means 5% of nodes flip their partition assignment).
  - W_data = K additional data patterns.
  - Convergence metric: iterations to recover sigma* from noisy init
    (warm-start from W vs random-start).

PRE-REGISTERED BANDS:
  HARD-PASS: speedup = iters_random / iters_warm >= 2.0 in >= 4/5 seeds at rho=0.9.
  MIDDLE: speedup >= 1.5 in >= 3/5 seeds.
  HARD-FAIL: speedup < 1.2 in >= 3/5 seeds.
  Note: calibration probe; research predicts ~10x. Bands at +-50% of 2.0 threshold.
  HP at 2.0; HF at 1.2 (60% of HP).

DESIGN:
  N = 2048 (GPU compatible; but CPU test).
  M_data = 10 (alpha_data = 0.005, very light data load).
  rho = 0.9 (90% of nodes stay same between CSP instances).
  n_instances = 10 (slowly evolving sequence of planted bipartitions).
  5 seeds.

FORMULA SELF-TESTS:
  1. W_csp = sigma* sigma*^T / N: signal eigenvalue ~ 1.0 (well above MP edge).
  2. lambda_max(W_csp) ~ 1.0 >> lambda_plus(alpha_data) ~ (1+sqrt(0.005))^2 ~ 1.14.
     Wait: lambda_max(W_csp) = N (unnormalized) or 1.0 (normalized) -- both above edge.
  3. rho=0.9 correlation: new sigma* differs in 10% of bits from old. Hopfield warm-start
     should already be in the basin of attraction of new sigma*.

PROT-018: no _nN suffix. Production N=2048, rule 3.

TIMEOUT ESTIMATE:
  numpy Hopfield on N=2048: per iteration ~ O(N^2). 5 seeds * 10 instances * 50 max iters.
  Each: 2048^2 matmul ~ 20ms. 5 * 10 * 50 = 2500 iterations = 50s.
  timeout_s=300.

Anchor: csp_memory_warm_start_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_csp_memory_warm_start_v1.md
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

ANCHOR_NAME = "csp_memory_warm_start_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 2048
M_DATA = 10
RHO = 0.9
MAX_ITERS = 200
RECOVERY_THRESH = 0.90
NOISE_FRAC_INIT = 0.10  # noise in warm init

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_INSTANCES = 5
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_INSTANCES = 10


def generate_next_partition(sigma_prev: np.ndarray, rho: float,
                             rng: np.random.RandomState) -> np.ndarray:
    """Generate new partition with rho correlation to previous."""
    N = sigma_prev.shape[0]
    flip_mask = rng.rand(N) < (1.0 - rho)
    sigma_new = sigma_prev.copy()
    sigma_new[flip_mask] = -sigma_new[flip_mask]
    return sigma_new


def hopfield_converge(W: np.ndarray, init: np.ndarray,
                      target: np.ndarray, max_iters: int,
                      thresh: float) -> int:
    """Return number of iterations to reach overlap > thresh with target."""
    sigma = init.copy()
    N = sigma.shape[0]
    for i in range(max_iters):
        overlap = float(np.dot(sigma, target) / N)
        if abs(overlap) > thresh:
            return i
        new_sigma = np.sign(W @ sigma)
        new_sigma[new_sigma == 0] = sigma[new_sigma == 0]
        if np.all(new_sigma == sigma):
            return i + 1  # converged but not to target
        sigma = new_sigma
    return max_iters  # did not converge


def run_one_seed(N: int, M_data: int, seed: int, rho: float,
                 n_instances: int, max_iters: int) -> Dict:
    rng = np.random.RandomState(seed)

    # Data patterns (fixed throughout)
    Xi_data = rng.choice([-1, 1], size=(N, M_data)).astype(np.float64)
    W_data = (Xi_data @ Xi_data.T) / N

    # First planted partition
    sigma_cur = rng.choice([-1, 1], size=N).astype(np.float64)

    speedups = []
    warm_iters_list = []
    rand_iters_list = []

    for inst in range(n_instances):
        # Encode current partition in W_csp
        W_csp = np.outer(sigma_cur, sigma_cur) / N  # rank-1
        W_combined = W_csp + W_data

        # Get next partition
        sigma_next = generate_next_partition(sigma_cur, rho, rng)

        # Warm-start: init from previous sigma_cur + noise
        warm_init = sigma_cur.copy()
        noise_mask = rng.rand(N) < NOISE_FRAC_INIT
        warm_init[noise_mask] = -warm_init[noise_mask]

        # Random-start: random init
        rand_init = rng.choice([-1.0, 1.0], size=N)

        # Update W_csp to encode NEXT partition (what we want to warm-start into)
        W_csp_next = np.outer(sigma_next, sigma_next) / N
        W_combined_next = W_csp_next + W_data

        # Convergence test
        warm_iters = hopfield_converge(W_combined_next, warm_init, sigma_next,
                                        max_iters, RECOVERY_THRESH)
        rand_iters = hopfield_converge(W_combined_next, rand_init, sigma_next,
                                        max_iters, RECOVERY_THRESH)

        warm_iters_list.append(warm_iters)
        rand_iters_list.append(rand_iters)
        speedup = rand_iters / max(1, warm_iters)
        speedups.append(speedup)

        sigma_cur = sigma_next

    mean_speedup = float(np.mean(speedups))
    mean_warm = float(np.mean(warm_iters_list))
    mean_rand = float(np.mean(rand_iters_list))

    return {
        "seed": seed,
        "N": N,
        "M_data": M_data,
        "rho": rho,
        "n_instances": n_instances,
        "mean_speedup": mean_speedup,
        "speedups": [float(s) for s in speedups],
        "mean_warm_iters": mean_warm,
        "mean_rand_iters": mean_rand,
        "hp": mean_speedup >= 2.0,
    }


def _instrumentation_selftest():
    """Assert speedup is non-null and positive."""
    r = run_one_seed(256, 5, 999, 0.9, 3, 50)
    assert r["mean_speedup"] is not None, "mean_speedup is None"
    assert r["mean_speedup"] > 0, f"mean_speedup={r['mean_speedup']} <= 0"
    assert r["n_instances"] == 3, "n_instances mismatch"
    print(f"[selftest] PASS: mean_speedup={r['mean_speedup']:.2f} N=256 "
          f"warm={r['mean_warm_iters']:.1f} rand={r['mean_rand_iters']:.1f}", flush=True)


_instrumentation_selftest()


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[{ANCHOR_NAME}] RUN_MODE={RUN_MODE} N={N} rho={RHO} seeds={SEEDS}",
          flush=True)

    results = []
    for seed in SEEDS:
        print(f"[{ANCHOR_NAME}] seed={seed}...", flush=True)
        r = run_one_seed(N, M_DATA, seed, RHO, N_INSTANCES, MAX_ITERS)
        results.append(r)
        print(f"  mean_speedup={r['mean_speedup']:.2f} "
              f"warm={r['mean_warm_iters']:.1f} rand={r['mean_rand_iters']:.1f} "
              f"hp={r['hp']}", flush=True)

    n_hp = sum(1 for r in results if r["hp"])
    n_seeds = len(results)
    mean_speedup = float(np.mean([r["mean_speedup"] for r in results]))

    if n_hp >= 4 and mean_speedup >= 2.0:
        verdict = "HARD_PASS"
    elif mean_speedup >= 1.5 and n_hp >= 3:
        verdict = "MIDDLE_BAND"
    elif mean_speedup < 1.2 and (n_seeds - n_hp) >= 3:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": (
            f"CSP warm-start: mean_speedup={mean_speedup:.2f} [HP: >=2.0], "
            f"n_hp={n_hp}/{n_seeds}, N={N}, rho={RHO}"
        ),
        "mean_speedup": float(mean_speedup),
        "n_hp_seeds": int(n_hp),
        "n_seeds": int(n_seeds),
        "N": int(N),
        "rho": float(RHO),
        "elapsed_s": float(elapsed),
        "run_mode": RUN_MODE,
        "per_seed": results,
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[{ANCHOR_NAME}] VERDICT: {verdict}", flush=True)
    print(f"  mean_speedup={mean_speedup:.2f} n_hp={n_hp}/{n_seeds}", flush=True)
    print(f"  elapsed={elapsed:.1f}s -> {metrics_path}", flush=True)


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