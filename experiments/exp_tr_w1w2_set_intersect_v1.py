"""Cell E: tr(W1 W2) set-intersection cardinality estimator.

SCIENTIFIC QUESTION:
  Does the identity tr(W1 W2) = K*N^2 + (M1*M2 - K)*N hold empirically?
  Where K = |S1 intersect S2| (shared patterns), W_i = sum_mu xi_mu xi_mu^T / N,
  M1 = |S1|, M2 = |S2|, N = dimension.
  Predicted SNR ~ 1448 at M=50, N=2048. HP criterion: Pearson r > 0.9999, MAE < 0.5.

PRE-REGISTERED BANDS:
  HARD-PASS: Pearson r > 0.9999 AND MAE < 0.5 cardinality units across all K values.
  MIDDLE: 0.999 <= r <= 0.9999 OR 0.5 <= MAE <= 2.0.
  HARD-FAIL: r < 0.999 OR MAE > 2.0.

DESIGN:
  N=2048, M1=M2=50 (alpha=0.024, healthy regime).
  K in {0, 5, 10, 20, 30, 40, 50} (intersection sizes from empty to full overlap).
  5 seeds, 3 trials per (seed, K) for noise averaging.
  Formula: tr(W1 W2) = sum_{i,j} W1[i,j] * W2[i,j]
    = (1/N^2) * sum_{mu in S1, nu in S2} (xi_mu . xi_nu)^2
    Exact: = (1/N^2) * [K*N^2 + (M1*M2 - K)*N] * N^2 / N^2
           Wait -- let's be careful. W1 = sum_mu xi_mu xi_mu^T / N (no /N^2).
           tr(W1 W2) = tr[(sum_mu xi_mu xi_mu^T / N)(sum_nu xi_nu xi_nu^T / N)]
                     = (1/N^2) sum_mu sum_nu (xi_mu . xi_nu)^2
    For mu=nu (shared, K pairs): (xi_mu . xi_nu)^2 = N^2.
    For mu != nu (unshared, M1*M2 - K pairs): E[(xi_mu . xi_nu)^2] = N.
    -> E[tr(W1 W2)] = (1/N^2) [K*N^2 + (M1*M2-K)*N] = K + (M1*M2-K)/N

  SELF-TESTS:
    - K=0: tr(W1 W2) ~ M1*M2/N = 50*50/2048 ~ 1.22
    - K=50 (full overlap): tr(W1 W2) ~ M1*M2 = 2500 (noise: +0 terms)
    - K=10: tr(W1 W2) ~ 10 + (2500-10)/2048 ~ 10 + 1.22 = 11.22

PROT-018: no _nN suffix (N=2048 is sweep config, not anchor binding). See N-suffix note.
  Note: N=2048 is the sole scale; no _n suffix needed per role contract rule 3.
  Stated: production N = 2048; rationale: fixed-N algebraic identity check.

TIMEOUT ESTIMATE:
  N=2048: W construction O(N^2 * M) + tr(W1 W2) = matmul O(N^2) per trial.
  5 seeds * 7 K_values * 3 trials = 105 trials.
  Each trial: ~0.02s (N=2048 matmul on CPU). Total: ~2s.
  timeout_s = 300 (floor; actual wall << 60s).

Anchor: tr_w1w2_set_intersect_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_tr_w1w2_set_intersect_v1.md
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

ANCHOR_NAME = "tr_w1w2_set_intersect_v1"

# Production config
N = 2048
M1 = 50
M2 = 50
K_GRID = [0, 5, 10, 20, 30, 40, 50]
N_TRIALS = 3
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7]

# Pre-registered thresholds
HP_PEARSON = 0.9999
HP_MAE = 0.5
HF_PEARSON = 0.999
HF_MAE = 2.0


# ---------------------------------------------------------------------------
# Closed-form prediction
# ---------------------------------------------------------------------------

def predicted_trace(K: int, M1: int, M2: int, N: int) -> float:
    """E[tr(W1 W2)] = K + (M1*M2 - K) / N."""
    return K + (M1 * M2 - K) / N


# ---------------------------------------------------------------------------
# Instrumentation self-test
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert trace computation and formula are non-null at toy scale."""
    rng = np.random.default_rng(0)
    N_test = 64
    M_test = 5
    # Build W with K=2 shared patterns
    pats = rng.choice([-1.0, 1.0], size=(M_test, N_test))
    W1 = (pats.T @ pats) / N_test
    W2 = (pats.T @ pats) / N_test  # same patterns -> K=M_test
    tr_val = np.trace(W1 @ W2)
    pred = predicted_trace(M_test, M_test, M_test, N_test)
    assert tr_val is not None, "trace is None"
    assert not math.isnan(tr_val), "trace is NaN"
    assert tr_val > 0, f"trace <= 0: {tr_val}"
    # Formula self-tests (from docstring):
    # K=0, M1=M2=5, N=64: pred = 0 + 25/64 = 0.390625
    pred0 = predicted_trace(0, 5, 5, 64)
    assert abs(pred0 - 0.390625) < 1e-6, f"pred0 mismatch: {pred0}"
    # K=5 (full overlap M1=M2=5, N=64): pred = 5 + (25-5)/64 = 5 + 20/64 = 5.3125
    pred_full = predicted_trace(5, 5, 5, 64)
    assert abs(pred_full - 5.3125) < 1e-6, f"pred_full mismatch: {pred_full}"
    # tr_val at K=5 (W1==W2) should be close to pred_full
    # tr(W^2) = sum_ij W[i,j]^2 = ||W||_F^2
    # = (1/N^2) sum_{mu,nu} (xi_mu.xi_nu)^2 ~ M + M*(M-1)/N = 5 + 20/64 = 5.3125
    assert abs(tr_val - pred_full) < 1.0 * math.sqrt(M_test), \
        f"K=full: tr={tr_val:.4f} pred={pred_full:.4f} diff too large"
    print("[selftest] PASS: trace formula checks OK", flush=True)


_instrumentation_selftest()


# ---------------------------------------------------------------------------
# Experiment
# ---------------------------------------------------------------------------

def run_one_trial(K: int, M1: int, M2: int, N: int, rng: np.random.Generator) -> float:
    """One trial: build W1, W2 with K shared patterns, return tr(W1 W2)."""
    # Shared patterns (first K)
    shared = rng.choice([-1.0, 1.0], size=(K, N)) if K > 0 else np.zeros((0, N))
    # Unique to S1
    u1 = rng.choice([-1.0, 1.0], size=(M1 - K, N)) if M1 - K > 0 else np.zeros((0, N))
    # Unique to S2
    u2 = rng.choice([-1.0, 1.0], size=(M2 - K, N)) if M2 - K > 0 else np.zeros((0, N))

    pats1 = np.concatenate([shared, u1], axis=0) if K > 0 or M1 - K > 0 else np.zeros((0, N))
    pats2 = np.concatenate([shared, u2], axis=0) if K > 0 or M2 - K > 0 else np.zeros((0, N))

    W1 = (pats1.T @ pats1) / N
    W2 = (pats2.T @ pats2) / N
    return float(np.trace(W1 @ W2))


def run_seed(seed: int, n: int, m1: int, m2: int,
             k_grid: List[int], n_trials: int) -> Dict:
    rng = np.random.default_rng(seed)
    results = {}
    for K in k_grid:
        trials = [run_one_trial(K, m1, m2, n, rng) for _ in range(n_trials)]
        mean_trace = float(np.mean(trials))
        pred = predicted_trace(K, m1, m2, n)
        results[str(K)] = {
            "K": K, "mean_trace": mean_trace,
            "predicted": pred, "error": mean_trace - pred,
            "trials": trials,
        }
    return results


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "full")
    seeds = SEEDS_FULL if run_mode == "full" else SEEDS_SMOKE
    print(f"[{ANCHOR_NAME}] run_mode={run_mode} seeds={seeds} N={N}", flush=True)

    all_seed_results = {}
    for seed in seeds:
        print(f"  seed={seed}...", flush=True)
        res = run_seed(seed, N, M1, M2, K_GRID, N_TRIALS)
        all_seed_results[str(seed)] = res

    # Aggregate: collect (K, predicted, measured) across all seeds
    k_to_preds, k_to_meas = {}, {}
    for seed_res in all_seed_results.values():
        for kstr, cell in seed_res.items():
            K = cell["K"]
            k_to_preds.setdefault(K, []).append(cell["predicted"])
            k_to_meas.setdefault(K, []).append(cell["mean_trace"])

    # Flatten into two arrays for Pearson r
    pred_flat = []
    meas_flat = []
    for K in K_GRID:
        for p, m in zip(k_to_preds[K], k_to_meas[K]):
            pred_flat.append(p)
            meas_flat.append(m)

    pred_arr = np.array(pred_flat)
    meas_arr = np.array(meas_flat)
    pearson_r = float(np.corrcoef(pred_arr, meas_arr)[0, 1])
    mae = float(np.mean(np.abs(pred_arr - meas_arr)))

    # Verdict
    if pearson_r > HP_PEARSON and mae < HP_MAE:
        verdict = "HARD_PASS"
    elif pearson_r < HF_PEARSON or mae > HF_MAE:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "anchor": ANCHOR_NAME, "run_mode": run_mode,
        "N": N, "M1": M1, "M2": M2, "K_grid": K_GRID,
        "n_seeds": len(seeds), "n_trials": N_TRIALS,
        "pearson_r": pearson_r, "mae": mae,
        "per_k_summary": {
            str(K): {
                "predicted": float(np.mean(k_to_preds[K])),
                "measured_mean": float(np.mean(k_to_meas[K])),
                "measured_std": float(np.std(k_to_meas[K])),
            } for K in K_GRID
        },
        "verdict": verdict, "elapsed_s": elapsed,
        "thresholds": {
            "HP_pearson": HP_PEARSON, "HP_mae": HP_MAE,
            "HF_pearson": HF_PEARSON, "HF_mae": HF_MAE,
        },
        "verdict_msg": (
            f"tr(W1 W2) set-intersect identity: Pearson r={pearson_r:.6f} "
            f"(HP>{HP_PEARSON}), MAE={mae:.4f} (HP<{HP_MAE}). "
            f"Verdict: {verdict}."
        ),
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict} r={pearson_r:.6f} mae={mae:.4f} "
          f"elapsed={elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument("--self-test", action="store_true", dest="self_test")
    _p.add_argument("--smoke", action="store_true",
                    help="Run at smoke scope (SEEDS_SMOKE) for gate validation")
    _args = _p.parse_args()
    if _args.self_test:
        sys.exit(0)
    if _args.smoke:
        os.environ["HDLAB_RUN_MODE"] = "smoke"
    main()
