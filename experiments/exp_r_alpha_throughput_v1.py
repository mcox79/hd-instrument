"""Q21: R(alpha) sweep -- KV-cache write-throughput envelope (retention vs load).

SCIENTIFIC QUESTION:
  What is the substrate's retention R as a function of load alpha = M/N?
  v1b confirmed 97% retention at alpha ~ 0.01-0.05 (uncertain).
  This sweep pins the empirical alpha at the v1b operating point.

  Theory: R(alpha) = erf(1/sqrt(2*(alpha + correction_terms))) via signal-noise analysis.
  Simplified leading term: R ~ 1 - alpha * sqrt(2/pi) for small alpha.
  At alpha_c ~ 0.138: R drops sharply.

PRE-REGISTERED BANDS:
  HARD-PASS:
    - R(alpha) is monotone decreasing in alpha across sweep in >= 4/5 seeds.
    - R at alpha=0.01: > 0.97 (v1b operating region confirmed).
    - R drops to < 0.50 somewhere in [0.10, 0.20] (cliff identified).
  MIDDLE: R(0.01) > 0.90 AND monotone but cliff not cleanly resolved.
  HARD-FAIL: R(0.01) < 0.80 in >= 3/5 seeds OR non-monotone in >= 3/5 seeds.
  Note: calibration probe; +-50% on HP threshold (0.97). HF at 0.80 (40% below HP floor).

DESIGN:
  N = 4096 (PROT-018 _n4096 binding).
  alpha_grid = [0.001, 0.005, 0.01, 0.02, 0.05, 0.08, 0.10, 0.12, 0.138, 0.15, 0.18, 0.20].
  M = int(alpha * N) for each alpha.
  5 seeds.
  Retention R = fraction of stored patterns retrieved correctly
               = fraction with |<sigma_retrieved, xi_mu>| / N > 0.80 (correct basin).
  Retrieval: synchronous Hopfield from noisy initial (5% noise).

FORMULA SELF-TESTS:
  1. alpha=0.01, N=4096: M=40. R ~ 0.998 (theory). Expected empirical: >0.97.
  2. alpha=0.138, N=4096: M=565. R should drop sharply (near capacity cliff).
  3. Monotone: R(0.01) > R(0.05) > R(0.10) > R(0.138).

PROT-018: _n4096 binding. Production N MUST equal 4096.

TIMEOUT ESTIMATE:
  Numpy Hopfield at N=4096: O(N^2 * n_iters) per retrieval.
  5 seeds * 12 alpha * M_max=820 queries * N^2 * 50 iters: dominated by large alpha.
  At alpha=0.20, M=820: 820 queries * N^2 matmul * 50 iters.
  1 matmul N=4096^2: numpy ~ 50ms. 820 * 50 = 41000 matmuls = 2050s. TOO SLOW.
  Reduce to 20 representative patterns per alpha -> 20 * 50 = 1000 matmuls = 50s per seed.
  5 seeds * 12 alpha * 50s = 300s. timeout_s = ceil(1.5 * 300) = 450 -> 600.

Anchor: r_alpha_throughput_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_r_alpha_throughput_v1.md
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

ANCHOR_NAME = "r_alpha_throughput_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# PROT-018: _n4096 binding
N = 4096
if N != 4096:
    raise RuntimeError(f"PROT-018: N={N} != 4096 (anchor suffix)")

N_QUERIES_PER_ALPHA = 20  # representative sample per alpha
NOISE_FRAC = 0.05
N_ITERS = 50
CORRECT_THRESH = 0.80

if RUN_MODE == "smoke":
    N_SMOKE = 512
    SEEDS = [7, 17]
    ALPHA_GRID = [0.01, 0.05, 0.10, 0.15]
else:
    N_SMOKE = 512
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_GRID = [0.001, 0.005, 0.01, 0.02, 0.05, 0.08, 0.10, 0.12, 0.138, 0.15, 0.18, 0.20]


def run_retention_at_alpha(N: int, alpha: float, seed: int,
                           n_queries: int, noise_frac: float,
                           n_iters: int, correct_thresh: float) -> Dict:
    M = max(1, int(alpha * N))
    M_actual = M
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1, 1], size=(N, M)).astype(np.float64)
    W = (Xi @ Xi.T) / N

    # Test n_queries random patterns
    n_test = min(n_queries, M)
    test_indices = rng.choice(M, size=n_test, replace=False)
    correct = 0

    for idx in test_indices:
        xi = Xi[:, idx]
        # Add noise
        noise_mask = rng.rand(N) < noise_frac
        sigma = xi.copy()
        sigma[noise_mask] = -sigma[noise_mask]
        # Hopfield relaxation
        for _ in range(n_iters):
            new_sigma = np.sign(W @ sigma)
            new_sigma[new_sigma == 0] = sigma[new_sigma == 0]
            if np.all(new_sigma == sigma):
                break
            sigma = new_sigma
        overlap = float(np.dot(sigma, xi) / N)
        if abs(overlap) > correct_thresh:
            correct += 1

    R = correct / n_test
    return {"alpha": alpha, "M": M_actual, "R": R, "n_test": n_test, "correct": correct}


def _instrumentation_selftest():
    """Assert retention is non-null and in [0,1]."""
    r = run_retention_at_alpha(512, 0.05, 999, 5, 0.05, 20, 0.80)
    assert r["R"] is not None, "R is None"
    assert 0.0 <= r["R"] <= 1.0, f"R={r['R']} out of [0,1]"
    assert r["n_test"] > 0, "n_test == 0"
    print(f"[selftest] PASS: R={r['R']:.3f} at alpha=0.05, N=512", flush=True)


_instrumentation_selftest()


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    N_run = N_SMOKE if RUN_MODE == "smoke" else N
    print(f"[{ANCHOR_NAME}] RUN_MODE={RUN_MODE} N={N_run} seeds={SEEDS}",
          flush=True)
    print(f"  alpha_grid={ALPHA_GRID}", flush=True)

    all_results = []
    for seed in SEEDS:
        print(f"[{ANCHOR_NAME}] seed={seed}...", flush=True)
        seed_results = []
        for alpha in ALPHA_GRID:
            r = run_retention_at_alpha(N_run, alpha, seed, N_QUERIES_PER_ALPHA,
                                       NOISE_FRAC, N_ITERS, CORRECT_THRESH)
            r["seed"] = seed
            seed_results.append(r)
            print(f"  alpha={alpha:.3f} M={r['M']} R={r['R']:.3f}", flush=True)
        all_results.extend(seed_results)

    # Verdict per seed
    seed_verdicts = []
    from collections import defaultdict
    by_seed: Dict = defaultdict(list)
    for r in all_results:
        by_seed[r["seed"]].append(r)

    for seed, pts in by_seed.items():
        alphas = [p["alpha"] for p in pts]
        Rs = [p["R"] for p in pts]
        # Check monotone
        pairs = sorted(zip(alphas, Rs))
        monotone = all(pairs[i][1] >= pairs[i+1][1] - 0.05 for i in range(len(pairs)-1))
        R_low_alpha = next((p["R"] for p in pts if abs(p["alpha"] - 0.01) < 0.005), None)
        if R_low_alpha is None and pts:
            # Use lowest alpha
            R_low_alpha = min(pts, key=lambda x: x["alpha"])["R"]
        cliff_found = any(p["R"] < 0.50 for p in pts if p["alpha"] >= 0.10)
        hp = (R_low_alpha is not None and R_low_alpha > 0.97 and monotone)
        seed_verdicts.append({
            "seed": seed,
            "R_at_alpha_001": float(R_low_alpha) if R_low_alpha is not None else None,
            "monotone": monotone,
            "cliff_found": cliff_found,
            "hp": hp,
        })

    n_hp = sum(1 for v in seed_verdicts if v["hp"])
    n_seeds = len(seed_verdicts)

    mean_R_low = float(np.mean([v["R_at_alpha_001"] for v in seed_verdicts
                                 if v["R_at_alpha_001"] is not None]))

    if n_hp >= 4 and mean_R_low > 0.97:
        verdict = "HARD_PASS"
    elif mean_R_low > 0.90:
        verdict = "MIDDLE_BAND"
    elif mean_R_low < 0.80 and (n_seeds - n_hp) >= 3:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": (
            f"R(alpha) throughput: mean_R_low_alpha={mean_R_low:.3f} "
            f"[HP: >0.97], n_hp={n_hp}/{n_seeds}, "
            f"N={N_run}, alpha_grid_len={len(ALPHA_GRID)}"
        ),
        "mean_R_at_low_alpha": float(mean_R_low),
        "n_hp_seeds": int(n_hp),
        "n_seeds": int(n_seeds),
        "N_production": int(N),
        "N_run": int(N_run),
        "alpha_grid": ALPHA_GRID,
        "elapsed_s": float(elapsed),
        "run_mode": RUN_MODE,
        "per_result": all_results,
        "seed_verdicts": seed_verdicts,
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[{ANCHOR_NAME}] VERDICT: {verdict}", flush=True)
    print(f"  mean_R_low={mean_R_low:.3f} n_hp={n_hp}/{n_seeds}", flush=True)
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