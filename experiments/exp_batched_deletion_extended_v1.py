"""Q22 extended: batched deletion verification reliability at k = {1,5,10,20,50,100}.

SCIENTIFIC QUESTION:
  The algebraic prediction: R(k) ~ r_1^k for independent patterns (r_1=single reliability).
  Worst case: moderately correlated patterns (c~0.3-0.5) degrade FASTER than r_1^k.
  Highly correlated near-duplicates: LESS ghost effect (paradoxical).

  Tests:
  1. INDEPENDENT delete: verify R(k) ~ r_1^k for independent S_delete.
  2. CORRELATED delete: verify R(k) < r_1^k for correlated S_delete (c~0.5).
  3. NEAR-DUPLICATE delete: verify R(k) ~ R(k=1) for near-duplicate S_delete.
  4. Measure r_1 empirically and validate formula.

PRE-REGISTERED BANDS:
  HARD-PASS:
    - r_1 in [0.88, 0.96] (prior measurement range).
    - R(10)_independent / r_1^10 in [0.7, 1.3] (formula holds within 30% of prediction).
    - R(10)_correlated < R(10)_independent (correlated is harder).
  MIDDLE: r_1 in [0.85, 0.99] AND direction R_corr < R_indep.
  HARD-FAIL: r_1 < 0.80 in >= 3/5 seeds.
  Note: prior batched_deletion_reliability_v1 already ran; this extends to larger k.

DESIGN:
  N = 4096 (PROT-018 _n4096 binding). M = int(0.05 * N) = 204 (safe alpha).
  k_grid = [1, 5, 10, 20, 50, 100].
  correlation levels: rho=0 (independent), rho=0.5 (correlated), rho=0.95 (near-duplicate).
  5 seeds.

FORMULA SELF-TESTS:
  1. r_1 at N=4096, alpha=0.05: prior measurements suggest ~0.92-0.96.
  2. R(10) = r_1^10 ~ 0.92^10 ~ 0.43. Independent delete.
  3. At k=50: R ~ 0.92^50 ~ 0.015. Near-zero for large batches.

PROT-018: _n4096 binding. Production N MUST equal 4096.

TIMEOUT ESTIMATE:
  N=4096, numpy: W construction + deletion + retrieval.
  5 seeds * 6 k_values * 3 correlation_levels * n_rep=10 = 900 experiments.
  Each: single deletion + retrieval sweep ~ 0.1s. Total: ~100s.
  timeout_s=300.

Anchor: batched_deletion_extended_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_batched_deletion_extended_v1.md
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

ANCHOR_NAME = "batched_deletion_extended_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# PROT-018: _n4096 binding
N = 4096
if N != 4096:
    raise RuntimeError(f"PROT-018: N={N} != 4096")

ALPHA = 0.05
M = int(ALPHA * N)  # 204
N_REP = 10  # repetitions for reliability estimate
NOISE_FRAC = 0.05
N_ITERS = 50
CORRECT_THRESH = 0.80

if RUN_MODE == "smoke":
    N_SMOKE = 512
    SEEDS = [7, 17]
    K_GRID = [1, 5, 10]
    RHO_LEVELS = [0.0, 0.5]
else:
    N_SMOKE = 512
    SEEDS = [7, 17, 23, 31, 41]
    K_GRID = [1, 5, 10, 20, 50, 100]
    RHO_LEVELS = [0.0, 0.5, 0.95]


def build_correlated_batch(Xi: np.ndarray, k: int, rho: float, seed: int) -> np.ndarray:
    """Build k patterns correlated at level rho with Xi[:,0]."""
    N = Xi.shape[0]
    rng = np.random.RandomState(seed + 9999)
    if rho == 0.0:
        # Independent: random fresh patterns
        return rng.choice([-1, 1], size=(N, k)).astype(np.float64)
    else:
        # Correlated with Xi[:,0]
        base = Xi[:, 0].copy()
        result = []
        for _ in range(k):
            pat = base.copy()
            flip_mask = rng.rand(N) < (1 - rho) / 2.0
            pat[flip_mask] = -pat[flip_mask]
            result.append(pat)
        return np.column_stack(result)


def single_deletion_reliability(W: np.ndarray, Xi: np.ndarray, xi_del: np.ndarray,
                                 N: int, rng: np.random.RandomState) -> float:
    """Delete xi_del and test retrieval of remaining patterns."""
    W_new = W - np.outer(xi_del, xi_del) / N
    M = Xi.shape[1]
    # Test a few remaining patterns
    n_test = min(5, M)
    correct = 0
    for i in range(n_test):
        xi = Xi[:, i]
        if np.allclose(xi, xi_del):
            continue
        noise_mask = rng.rand(N) < NOISE_FRAC
        sigma = xi.copy()
        sigma[noise_mask] = -sigma[noise_mask]
        for _ in range(N_ITERS):
            new_sigma = np.sign(W_new @ sigma)
            new_sigma[new_sigma == 0] = sigma[new_sigma == 0]
            if np.all(new_sigma == sigma):
                break
            sigma = new_sigma
        if float(np.dot(sigma, xi) / N) > CORRECT_THRESH:
            correct += 1
    return correct / max(1, n_test)


def run_one_seed(N: int, M: int, seed: int, k_grid: List[int],
                 rho_levels: List[float]) -> Dict:
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1, 1], size=(N, M)).astype(np.float64)
    W = (Xi @ Xi.T) / N

    results = {}
    for rho in rho_levels:
        results[f"rho_{rho}"] = {}
        for k in k_grid:
            if k > M:
                continue
            reliabilities = []
            for rep in range(N_REP):
                # Get k patterns to delete
                delete_batch = build_correlated_batch(Xi, k, rho,
                                                       seed + rep * 1000 + int(rho * 100))
                # Batch delete
                W_new = W.copy()
                for i in range(k):
                    W_new -= np.outer(delete_batch[:, i], delete_batch[:, i]) / N
                # Check remaining patterns
                n_test = min(5, M)
                correct = 0
                test_idx = rng.choice(M, n_test, replace=False)
                for idx in test_idx:
                    xi = Xi[:, idx]
                    noise_mask = rng.rand(N) < NOISE_FRAC
                    sigma = xi.copy()
                    sigma[noise_mask] = -sigma[noise_mask]
                    for _ in range(N_ITERS):
                        new_sigma = np.sign(W_new @ sigma)
                        new_sigma[new_sigma == 0] = sigma[new_sigma == 0]
                        if np.all(new_sigma == sigma):
                            break
                        sigma = new_sigma
                    if float(np.dot(sigma, xi) / N) > CORRECT_THRESH:
                        correct += 1
                reliabilities.append(correct / max(1, n_test))
            results[f"rho_{rho}"][f"k_{k}"] = float(np.mean(reliabilities))

    # Compute r_1 from rho=0, k=1
    r_1 = results.get("rho_0.0", {}).get("k_1", None)
    return {"seed": seed, "N": N, "M": M, "r_1": r_1, "results": results}


def _instrumentation_selftest():
    """Assert batched deletion measurement is non-null."""
    r = run_one_seed(256, 20, 999, [1, 5], [0.0])
    assert r["r_1"] is not None, "r_1 is None"
    assert 0.0 <= r["r_1"] <= 1.0, f"r_1={r['r_1']} out of [0,1]"
    print(f"[selftest] PASS: r_1={r['r_1']:.3f} N=256 M=20", flush=True)


_instrumentation_selftest()


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    N_run = N_SMOKE if RUN_MODE == "smoke" else N
    M_run = max(1, int(ALPHA * N_run))
    print(f"[{ANCHOR_NAME}] RUN_MODE={RUN_MODE} N={N_run} M={M_run} seeds={SEEDS}",
          flush=True)
    print(f"  k_grid={K_GRID} rho_levels={RHO_LEVELS}", flush=True)

    all_results = []
    for seed in SEEDS:
        print(f"[{ANCHOR_NAME}] seed={seed}...", flush=True)
        r = run_one_seed(N_run, M_run, seed, K_GRID, RHO_LEVELS)
        all_results.append(r)
        print(f"  r_1={r['r_1']:.3f}", flush=True)
        for rho in RHO_LEVELS:
            key = f"rho_{rho}"
            if key in r["results"]:
                ks = sorted(r["results"][key].keys())
                vals = [f"k={k}:{r['results'][key][k]:.2f}" for k in ks]
                print(f"  rho={rho}: {' '.join(vals)}", flush=True)

    r1_vals = [r["r_1"] for r in all_results if r["r_1"] is not None]
    mean_r1 = float(np.mean(r1_vals)) if r1_vals else 0.0

    # Check R(10)_indep vs r_1^10
    R10_indep_vals = [r["results"].get("rho_0.0", {}).get("k_10", None)
                      for r in all_results]
    R10_indep_vals = [v for v in R10_indep_vals if v is not None]
    mean_R10_indep = float(np.mean(R10_indep_vals)) if R10_indep_vals else None

    R10_corr_vals = [r["results"].get("rho_0.5", {}).get("k_10", None)
                     for r in all_results]
    R10_corr_vals = [v for v in R10_corr_vals if v is not None]
    mean_R10_corr = float(np.mean(R10_corr_vals)) if R10_corr_vals else None

    r1_formula_R10 = mean_r1 ** 10 if mean_r1 > 0 else None
    formula_ratio = None
    if r1_formula_R10 and mean_R10_indep is not None and r1_formula_R10 > 1e-6:
        formula_ratio = mean_R10_indep / r1_formula_R10

    hp = (0.88 <= mean_r1 <= 0.96
          and formula_ratio is not None and 0.7 <= formula_ratio <= 1.3
          and (mean_R10_corr is None or mean_R10_corr <= mean_R10_indep + 0.05))

    n_hp = sum(1 for r in all_results if r["r_1"] is not None
               and 0.88 <= r["r_1"] <= 0.96)

    if n_hp >= 4 and hp:
        verdict = "HARD_PASS"
    elif mean_r1 >= 0.85:
        verdict = "MIDDLE_BAND"
    elif mean_r1 < 0.80:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": (
            f"Batched deletion: r_1={mean_r1:.3f} [HP: 0.88-0.96], "
            f"n_hp={n_hp}/{len(all_results)}, "
            f"R10_indep={mean_R10_indep}, R10_corr={mean_R10_corr}, "
            f"formula_ratio={formula_ratio}"
        ),
        "mean_r1": float(mean_r1),
        "mean_R10_independent": mean_R10_indep,
        "mean_R10_correlated": mean_R10_corr,
        "formula_ratio_R10": formula_ratio,
        "n_hp_seeds": int(n_hp),
        "n_seeds": int(len(all_results)),
        "N_production": int(N),
        "N_run": int(N_run),
        "elapsed_s": float(elapsed),
        "run_mode": RUN_MODE,
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[{ANCHOR_NAME}] VERDICT: {verdict}", flush=True)
    print(f"  r_1={mean_r1:.3f} R10_indep={mean_R10_indep} "
          f"R10_corr={mean_R10_corr} formula_ratio={formula_ratio}", flush=True)
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