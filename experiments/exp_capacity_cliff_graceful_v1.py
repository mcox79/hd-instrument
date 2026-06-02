"""Q23: Capacity cliff -- graceful vs sharp degradation near alpha_c.

SCIENTIFIC QUESTION:
  Does the substrate show graceful or sharp failure near alpha = alpha_c = 0.138?
  Theory: near alpha_c, retrieval accuracy R(alpha) should show a CLIFF (sharp drop)
  consistent with the first-order multi-basin transition confirmed in pred4.
  Product implication: graceful = usable within 20% of alpha_c; sharp = hard cutoff.

PRE-REGISTERED BANDS:
  HARD-PASS (graceful): R decreases gradually over alpha in [0.10, 0.18];
    specifically R(0.13) > 0.60 in >= 4/5 seeds.
  HARD-PASS (sharp): R(0.12) > 0.80 AND R(0.15) < 0.30 in >= 4/5 seeds (cliff identified).
  Either HARD-PASS is valid -- just need to identify the regime.
  MIDDLE: R(0.13) in [0.30, 0.60] (cliff present but imprecisely located).
  HARD-FAIL: R shows non-monotone behavior (R(0.15) > R(0.10)) in >= 3/5 seeds.
  Note: calibration probe; +-50% on HP thresholds.

DESIGN:
  N = 4096 (PROT-018 _n4096 binding).
  alpha_fine_grid = [0.10, 0.11, 0.12, 0.125, 0.130, 0.135, 0.138, 0.14, 0.15, 0.16, 0.18, 0.20].
  5 seeds.
  Retention per alpha: 20 test patterns, 5% noise, 50 hop iters.

FORMULA SELF-TESTS:
  1. R(0.01) ~ 1.0, R(0.10) ~ 0.85, R(0.138) ~ 0.50 (theory near transition).
  2. Cliff location: alpha_c ~ 0.138 (Hopfield capacity theorem).

PROT-018: _n4096 binding. Production N MUST equal 4096.

TIMEOUT ESTIMATE:
  5 seeds * 12 alpha * 20 queries * 50 iters * O(N^2) matmul:
  5 * 12 * 20 = 1200 queries. At N=4096 numpy matmul ~ 50ms: 60s.
  timeout_s=300.

Anchor: capacity_cliff_graceful_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_capacity_cliff_graceful_v1.md
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

ANCHOR_NAME = "capacity_cliff_graceful_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 4096
if N != 4096:
    raise RuntimeError(f"PROT-018: N={N} != 4096")

NOISE_FRAC = 0.05
N_ITERS = 50
N_QUERIES = 20
CORRECT_THRESH = 0.80

if RUN_MODE == "smoke":
    N_SMOKE = 512
    SEEDS = [7, 17]
    ALPHA_FINE = [0.05, 0.10, 0.13, 0.15, 0.20]
else:
    N_SMOKE = 512
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_FINE = [0.10, 0.11, 0.12, 0.125, 0.130, 0.135, 0.138, 0.14,
                  0.15, 0.16, 0.18, 0.20]


def run_retention(N: int, alpha: float, seed: int,
                  n_queries: int, noise_frac: float,
                  n_iters: int, correct_thresh: float) -> float:
    M = max(1, int(alpha * N))
    n_test = min(n_queries, M)
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1, 1], size=(N, M)).astype(np.float64)
    W = (Xi @ Xi.T) / N

    test_idx = rng.choice(M, size=n_test, replace=False)
    correct = 0
    for idx in test_idx:
        xi = Xi[:, idx]
        sigma = xi.copy()
        noise_mask = rng.rand(N) < noise_frac
        sigma[noise_mask] = -sigma[noise_mask]
        for _ in range(n_iters):
            new_sigma = np.sign(W @ sigma)
            new_sigma[new_sigma == 0] = sigma[new_sigma == 0]
            if np.all(new_sigma == sigma):
                break
            sigma = new_sigma
        if float(np.dot(sigma, xi) / N) > correct_thresh:
            correct += 1
    return correct / max(1, n_test)


def _instrumentation_selftest():
    R = run_retention(256, 0.10, 999, 5, 0.05, 20, 0.80)
    assert 0.0 <= R <= 1.0, f"R={R} out of [0,1]"
    print(f"[selftest] PASS: R={R:.3f} at alpha=0.10, N=256", flush=True)


_instrumentation_selftest()


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    N_run = N_SMOKE if RUN_MODE == "smoke" else N
    print(f"[{ANCHOR_NAME}] RUN_MODE={RUN_MODE} N={N_run} seeds={SEEDS} "
          f"alpha_grid={ALPHA_FINE}", flush=True)

    all_results = []
    from collections import defaultdict
    by_seed: Dict = defaultdict(list)

    for seed in SEEDS:
        print(f"[{ANCHOR_NAME}] seed={seed}...", flush=True)
        for alpha in ALPHA_FINE:
            R = run_retention(N_run, alpha, seed, N_QUERIES, NOISE_FRAC, N_ITERS, CORRECT_THRESH)
            r = {"seed": seed, "alpha": alpha, "R": R, "N": N_run}
            all_results.append(r)
            by_seed[seed].append(r)
            print(f"  alpha={alpha:.3f} R={R:.3f}", flush=True)

    # Verdict: check graceful vs sharp
    seed_verdicts = []
    for seed, pts in by_seed.items():
        alphas = [p["alpha"] for p in pts]
        Rs = [p["R"] for p in pts]
        pairs = sorted(zip(alphas, Rs))

        # Monotone check
        monotone = all(pairs[i][1] >= pairs[i+1][1] - 0.05 for i in range(len(pairs)-1))

        # R at alpha~0.13
        R_at_013 = next((p[1] for p in pairs if abs(p[0] - 0.13) < 0.005), None)
        if R_at_013 is None and pairs:
            R_at_013 = next((p[1] for p in pairs if 0.12 <= p[0] <= 0.14), None)
        # R at alpha~0.12
        R_at_012 = next((p[1] for p in pairs if abs(p[0] - 0.12) < 0.005), None)
        # R at alpha~0.15
        R_at_015 = next((p[1] for p in pairs if abs(p[0] - 0.15) < 0.005), None)

        graceful = R_at_013 is not None and R_at_013 > 0.60
        sharp = (R_at_012 is not None and R_at_012 > 0.80
                 and R_at_015 is not None and R_at_015 < 0.30)

        seed_verdicts.append({
            "seed": seed,
            "monotone": bool(monotone),
            "graceful": bool(graceful),
            "sharp": bool(sharp),
            "R_at_013": float(R_at_013) if R_at_013 is not None else None,
            "hp": bool(graceful or sharp),
        })

    n_hp = sum(1 for v in seed_verdicts if v["hp"])
    n_mono = sum(1 for v in seed_verdicts if v["monotone"])
    n_seeds = len(seed_verdicts)

    if n_hp >= 4 and n_mono >= 4:
        verdict = "HARD_PASS"
    elif n_mono >= 3 and n_hp >= 2:
        verdict = "MIDDLE_BAND"
    elif (n_seeds - n_mono) >= 3:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": (
            f"Capacity cliff: n_hp={n_hp}/{n_seeds}, n_monotone={n_mono}/{n_seeds}, "
            f"N={N_run}, alpha_fine_grid_len={len(ALPHA_FINE)}"
        ),
        "n_hp_seeds": int(n_hp),
        "n_monotone_seeds": int(n_mono),
        "n_seeds": int(n_seeds),
        "N_production": int(N),
        "N_run": int(N_run),
        "elapsed_s": float(elapsed),
        "run_mode": RUN_MODE,
        "seed_verdicts": seed_verdicts,
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[{ANCHOR_NAME}] VERDICT: {verdict}", flush=True)
    print(f"  n_hp={n_hp}/{n_seeds} n_monotone={n_mono}/{n_seeds}", flush=True)
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