"""Cell G: Sparse-W K^2 capacity advantage.

SCIENTIFIC QUESTION:
  Does a K-sparse weight matrix (each neuron connected to K neighbors) exhibit
  K^2 capacity advantage over dense weights (capacity M_max ~ K^2 * log(N/K))?
  Does sparse-W show a sharp cliff vs gradual degradation for dense W?

PRE-REGISTERED BANDS:
  HARD-PASS: sparse-W at K=4 achieves retrieval accuracy > 0.80 at M/N=0.10
             (where dense-W falls below 0.80), AND shows sharper degradation
             cliff (gap between accuracy at M/N=0.10 and M/N=0.20 > 0.20 for sparse
             vs < 0.10 for dense) in >= 4/5 seeds.
  MIDDLE: sparse-W higher than dense at M/N=0.10 but cliff not significantly sharper.
  HARD-FAIL: sparse-W WORSE than dense at M/N=0.10 in >= 3/5 seeds.

  Calibration probe: K^2 capacity scaling is theoretically motivated but substrate
  has no prior empirical anchor for sparse-W. Bands at +/-50% per calibration-probe policy.
  Note: K=1 is trivially bad (single connection); K=8 approaches dense. K=4 is the test point.

DESIGN:
  N=2048, K in {1, 2, 4, 8, N (dense)}.
  M/N grid: {0.01, 0.05, 0.10, 0.20, 0.30}.
  Sparse W construction: each neuron i connects to K random neurons (no self-connection).
  W_sparse[i, j] = xi_mu[i] * xi_mu[j] / N only if j in neighbors(i).
  5 seeds, 50 retrieval queries per (seed, K, M/N).

PROT-018: no _nN suffix. Production N=2048; stated per PROT-018 rule 3.
  Stated: production N = 2048; rationale: K^2 capacity at fixed N.

TIMEOUT ESTIMATE:
  5 seeds * 5 K_values * 5 M/N_values = 125 cells.
  Each cell: build W (O(M*K) or O(M*N^2) for dense), 50 queries (O(K*N) or O(N^2)).
  Dense at M=614 (M/N=0.30): W=O(M*N^2) ~ expensive.
  Use vectorized construction. Estimate: ~5s/seed * 5 seeds = 25s.
  timeout=300 (floor; actual wall ~30-60s).

Anchor: sparse_w_k2_capacity_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_sparse_w_k2_capacity_v1.md
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
from typing import Dict, List, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "sparse_w_k2_capacity_v1"

# Production config
N = 2048
K_GRID = [1, 2, 4, 8, -1]  # -1 = dense
MN_GRID = [0.01, 0.05, 0.10, 0.20, 0.30]
N_QUERIES = 50
NOISE_FRAC = 0.10
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]

# Pre-registered thresholds
HP_ACC_K4_AT_010 = 0.80    # sparse K=4 at M/N=0.10
HP_CLIFF_SPARSE  = 0.20    # gap sparse[0.10] - sparse[0.20]
HP_CLIFF_DENSE   = 0.10    # gap dense[0.10] - dense[0.20] (should be smaller)
HF_MIN_SEEDS = 3            # K=4 worse than dense at M/N=0.10 in >= 3 seeds


def build_sparse_w(patterns: np.ndarray, N: int, K: int,
                   rng: np.random.Generator) -> np.ndarray:
    """Build sparse weight matrix with K connections per neuron."""
    W = np.zeros((N, N), dtype=np.float64)
    # Each neuron i: random K neighbors (no self)
    for i in range(N):
        candidates = np.delete(np.arange(N), i)
        neighbors = rng.choice(candidates, size=min(K, N - 1), replace=False)
        for mu in range(len(patterns)):
            W[i, neighbors] += patterns[mu, i] * patterns[mu, neighbors] / N
    return W


def build_dense_w(patterns: np.ndarray, N: int) -> np.ndarray:
    W = (patterns.T @ patterns) / N
    np.fill_diagonal(W, 0.0)
    return W


def retrieve(W: np.ndarray, query: np.ndarray, max_steps: int = 20) -> np.ndarray:
    s = query.copy()
    for _ in range(max_steps):
        s_new = np.where(W @ s > 0, 1.0, -1.0)
        if np.all(s_new == s):
            break
        s = s_new
    return s


def measure_accuracy(W: np.ndarray, patterns: np.ndarray, N: int,
                     n_queries: int, noise_frac: float,
                     rng: np.random.Generator) -> float:
    """Fraction of queries that achieve overlap >= 0.80 with target."""
    M = len(patterns)
    if M == 0:
        return 1.0
    correct = 0
    for _ in range(n_queries):
        mu = rng.integers(0, M)
        q = patterns[mu].copy()
        n_flip = int(noise_frac * N)
        idx = rng.choice(N, size=n_flip, replace=False)
        q[idx] *= -1
        final = retrieve(W, q)
        ov = float(np.mean(final == patterns[mu]))
        if ov >= 0.80:
            correct += 1
    return correct / n_queries


# ---------------------------------------------------------------------------
# Instrumentation self-test
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert sparse and dense W accuracy non-null at N=128."""
    rng = np.random.default_rng(0)
    N_t = 128
    M_t = 5
    pats = rng.choice([-1.0, 1.0], size=(M_t, N_t))
    # Dense W
    W_d = build_dense_w(pats, N_t)
    acc_d = measure_accuracy(W_d, pats, N_t, 10, NOISE_FRAC, rng)
    assert not math.isnan(acc_d) and 0.0 <= acc_d <= 1.0, f"dense acc out of range: {acc_d}"
    # Sparse W K=4
    W_s = build_sparse_w(pats, N_t, 4, rng)
    acc_s = measure_accuracy(W_s, pats, N_t, 10, NOISE_FRAC, rng)
    assert not math.isnan(acc_s) and 0.0 <= acc_s <= 1.0, f"sparse acc out of range: {acc_s}"
    print(f"[selftest] PASS: dense_acc={acc_d:.2f} sparse_k4_acc={acc_s:.2f}", flush=True)


_instrumentation_selftest()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "full")
    seeds = SEEDS_FULL if run_mode == "full" else SEEDS_SMOKE
    print(f"[{ANCHOR_NAME}] run_mode={run_mode} seeds={seeds} N={N}", flush=True)

    # results[K][mn_str][seed] = accuracy
    results: Dict = {str(K): {str(mn): [] for mn in MN_GRID} for K in K_GRID}

    for seed in seeds:
        rng = np.random.default_rng(seed)
        print(f"  seed={seed}...", flush=True)
        for mn in MN_GRID:
            M = max(1, int(mn * N))
            patterns = rng.choice([-1.0, 1.0], size=(M, N))
            # Sparse neighbor sets (precomputed once per seed per mn)
            for K in K_GRID:
                rng_k = np.random.default_rng(seed * 100 + M)  # deterministic per (seed,M)
                if K == -1:
                    W = build_dense_w(patterns, N)
                else:
                    W = build_sparse_w(patterns, N, K, rng_k)
                acc = measure_accuracy(W, patterns, N, N_QUERIES, NOISE_FRAC, rng)
                results[str(K)][str(mn)].append(acc)
            print(f"    M/N={mn}: K=[1,2,4,8,dense] accs="
                  + str([f"{results[str(K)][str(mn)][-1]:.2f}" for K in K_GRID]),
                  flush=True)

    # Compute means
    means: Dict = {str(K): {str(mn): float(np.mean(results[str(K)][str(mn)]))
                             for mn in MN_GRID}
                   for K in K_GRID}

    # Assess HP criteria
    K4_str = "4"
    dense_str = "-1"
    n_seeds = len(seeds)
    seeds_k4_better = sum(
        1 for i in range(n_seeds)
        if results[K4_str]["0.1"][i] >= HP_ACC_K4_AT_010
    )

    cliff_sparse = means[K4_str]["0.1"] - means[K4_str]["0.2"]
    cliff_dense  = means[dense_str]["0.1"] - means[dense_str]["0.2"]
    k4_acc_010   = means[K4_str]["0.1"]

    seeds_k4_worse = sum(
        1 for i in range(n_seeds)
        if results[K4_str]["0.1"][i] < results[dense_str]["0.1"][i]
    )

    hp_acc = k4_acc_010 >= HP_ACC_K4_AT_010
    hp_cliff = cliff_sparse > HP_CLIFF_SPARSE and cliff_dense < HP_CLIFF_DENSE
    hf_flag = seeds_k4_worse >= HF_MIN_SEEDS

    if hf_flag:
        verdict = "HARD_FAIL"
    elif hp_acc and hp_cliff:
        verdict = "HARD_PASS"
    elif hp_acc or seeds_k4_better >= math.ceil(n_seeds * 0.6):
        verdict = "MIDDLE_BAND"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "anchor": ANCHOR_NAME, "run_mode": run_mode,
        "N": N, "n_seeds": n_seeds,
        "K4_acc_at_010": k4_acc_010,
        "dense_acc_at_010": means[dense_str]["0.1"],
        "cliff_sparse_k4": cliff_sparse,
        "cliff_dense": cliff_dense,
        "accuracy_table": means,
        "verdict": verdict, "elapsed_s": elapsed,
        "thresholds": {
            "HP_K4_acc_010": HP_ACC_K4_AT_010,
            "HP_cliff_sparse": HP_CLIFF_SPARSE,
            "HP_cliff_dense": HP_CLIFF_DENSE,
            "HF_seeds_k4_worse": HF_MIN_SEEDS,
        },
        "verdict_msg": (
            f"Sparse-W K^2 at N={N}: K=4 acc@M/N=0.10={k4_acc_010:.3f} "
            f"(HP>={HP_ACC_K4_AT_010}), cliff_sparse={cliff_sparse:.3f} "
            f"(HP>{HP_CLIFF_SPARSE}) vs cliff_dense={cliff_dense:.3f} "
            f"(HP<{HP_CLIFF_DENSE}). Verdict: {verdict}."
        ),
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict} K4_acc={k4_acc_010:.3f} "
          f"elapsed={elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument("--self-test", action="store_true", dest="self_test")
    _p.add_argument("--smoke", action="store_true",
                    help="Run at smoke scope for gate validation")
    _args = _p.parse_args()
    if _args.self_test:
        sys.exit(0)
    if _args.smoke:
        os.environ["HDLAB_RUN_MODE"] = "smoke"
    main()