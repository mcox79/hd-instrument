"""
caching_eviction_cost_amortized_v1 -- Eviction cost over batch operations; O(1) amortized.

SCIENTIFIC QUESTION (Caching-Policy, Amortized Eviction Cost):
  Research-flagged: what is the AMORTIZED cost of eviction per batch operation?
  The substrate's rank-1 unwrite (W -= outer(xi, xi)/N) is O(N^2) per eviction.
  But for a BATCH of K evictions done simultaneously, cost = K * O(N^2) with
  potential constant factor savings if evictions are batched.

  Hypothesis: amortized cost per eviction = O(1) TIME relative to K when measured
  as wall_time / K vs K. Specifically: wall_time scales linearly in K (not super-linear),
  so wall_time / K stays roughly constant.

  Additional test: substrate "batch unwrite" can be done in one matrix update:
  W_new = W - (1/N) * Xi_evict^T * Xi_evict, where Xi_evict is the K x N matrix of
  evicted patterns. This is O(K*N) not O(K*N^2) if we use the BATCH rank-K update.

  Test cells:
    (A) Amortized cost is O(1): wall_time(K=K1) / K1 ~ wall_time(K=K2) / K2 within 2x.
        HP-A: |wall_per_K_small - wall_per_K_large| / wall_per_K_small <= 1.0
              (within 2x = ratio in [0.5, 2.0]).
        HF-A: wall_per_K_large > wall_per_K_small * 5 (super-linear growth).
    (B) Batch update is faster: batch_unwrite(K) < sequential_unwrite(K) * 0.90
        (batch method takes <= 90% of sequential time).
        HP-B: speedup = wall_seq / wall_batch >= 1.10. HF-B: speedup < 0.95 (batch is slower).
    (C) Retrieval accuracy preserved post-eviction: after evicting K patterns,
        remaining N_remaining patterns still retrieve with accuracy >= 0.85.
        HP-C: acc_post_eviction >= 0.85. HF-C: acc_post_eviction < 0.60.

  HARD-PASS: All of A, B, C.
  HARD-FAIL: HF-A (super-linear = not O(1)) or HF-C (eviction corrupts remaining).
  MIDDLE: 2/3 cells.

PRE-REGISTERED BANDS (calibration probe; no prior batch eviction timing measurement):
  HP: amortized ratio in [0.5, 2.0], speedup >= 1.10, acc >= 0.85.
  HF: ratio > 5.0, speedup < 0.95, acc < 0.60.
  Bands: +-50% per calibration-probe policy.
  Theory: batch rank-K update is O(K*N) vs sequential O(K*N^2); speedup ~ N/K ~ 100x
  for K=10 and N=1024. Real speedup limited by Python overhead.

FORMULA SELF-TESTS:
  1. Sequential unwrite: W_new = W - sum_k outer(xi_k, xi_k)/N.
     Cost: K iterations of O(N^2) each = O(K*N^2).
     For K=10, N=512: 10 * 512^2 = 2.6M ops.
     [INPUT: K=10, N=512] [EXPECTED: result is same as batch unwrite]
  2. Batch unwrite: W_new = W - Xi_evict^T @ Xi_evict / N.
     Same result in one matrix multiply. For K=10, N=512: O(K*N) = 5120 ops.
     [INPUT: K=10, N=512] [EXPECTED: batch result matches sequential within 1e-10]
  3. Amortized ratio: if K1=5 takes 0.01s and K2=20 takes 0.04s,
     per_K_1=0.002 and per_K_2=0.002, ratio=1.0 (perfectly linear).
     [INPUT: wall_5=0.01, wall_20=0.04] [EXPECTED: ratio=1.0]

TIMEOUT ESTIMATE:
  Smoke: N=512, K_sweep=[5,10,20], 2 seeds. Full: N=1024, K_sweep=[5,10,20,40,80], 5 seeds.
  Linear. Smoke ~1s -> Full ~10s. timeout=120s.

No _nN suffix; production N=1024 per rule 3.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "caching_eviction_cost_amortized_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

if RUN_MODE == "smoke":
    N = 512
    SEEDS = [7, 17]
    K_SWEEP = [5, 10, 20]
    M_BASE = 50   # patterns stored before eviction
else:
    N = 1024
    SEEDS = [7, 17, 23, 31, 41]
    K_SWEEP = [5, 10, 20, 40, 80]
    M_BASE = 80

HP_AMORTIZED_RATIO = 2.0   # wall_per_K_large / wall_per_K_small <= this
HF_AMORTIZED_RATIO = 5.0   # fail if super-linear
HP_SPEEDUP = 1.10           # batch speedup >= this
HF_SPEEDUP = 0.95           # fail if batch is slower
HP_ACC_POST = 0.85
HF_ACC_POST = 0.60

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()


# ---- FORMULA SELF-TESTS ----
def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    rng = np.random.RandomState(42)
    K, N_test = 10, 128

    Xi_base = rng.choice([-1.0, 1.0], size=(20, N_test)).astype(np.float64)
    W = Xi_base.T @ Xi_base / N_test
    np.fill_diagonal(W, 0.0)
    Xi_evict = Xi_base[:K].copy()

    # Sequential unwrite
    W_seq = W.copy()
    for k in range(K):
        W_seq -= np.outer(Xi_evict[k], Xi_evict[k]) / N_test
    np.fill_diagonal(W_seq, 0.0)

    # Batch unwrite
    W_batch = W.copy()
    W_batch -= Xi_evict.T @ Xi_evict / N_test
    np.fill_diagonal(W_batch, 0.0)

    # Should be equal within numerical precision
    diff = float(np.max(np.abs(W_seq - W_batch)))
    assert diff < 1e-10, f"Batch vs sequential unwrite mismatch: {diff:.2e}"

    # Amortized ratio formula
    wall_5 = 0.01
    wall_20 = 0.04
    ratio = (wall_20 / 20) / (wall_5 / 5 + 1e-15)
    assert abs(ratio - 1.0) < 0.01, f"Amortized ratio selftest: {ratio:.4f}"

    print(f"[selftest] batch_match_diff={diff:.2e} amortized_ratio={ratio:.4f}", flush=True)


_instrumentation_selftest()


def sequential_unwrite(W: np.ndarray, Xi_evict: np.ndarray, N_dim: int) -> np.ndarray:
    W_new = W.copy()
    for k in range(Xi_evict.shape[0]):
        W_new -= np.outer(Xi_evict[k], Xi_evict[k]) / N_dim
    np.fill_diagonal(W_new, 0.0)
    return W_new


def batch_unwrite(W: np.ndarray, Xi_evict: np.ndarray, N_dim: int) -> np.ndarray:
    W_new = W.copy()
    W_new -= Xi_evict.T @ Xi_evict / N_dim
    np.fill_diagonal(W_new, 0.0)
    return W_new


def retrieval_accuracy(W: np.ndarray, Xi: np.ndarray) -> float:
    if Xi.shape[0] == 0:
        return 0.0
    cosines = [float(np.dot(np.sign(W @ Xi[i]), Xi[i])) / Xi.shape[1] for i in range(Xi.shape[0])]
    return float(np.mean(cosines))


def run_one_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)

    # Build base W with M_BASE patterns
    Xi_base = rng.choice([-1.0, 1.0], size=(M_BASE, N)).astype(np.float64)
    W_base = Xi_base.T @ Xi_base / N
    np.fill_diagonal(W_base, 0.0)

    # Sweep over K values and measure timing
    timing_seq = {}
    timing_batch = {}
    acc_post = {}

    K_small = K_SWEEP[0]
    K_large = K_SWEEP[-1]

    for K in K_SWEEP:
        if K > M_BASE:
            K = M_BASE
        Xi_evict = Xi_base[:K].copy()
        Xi_remain = Xi_base[K:].copy()

        # Sequential
        t_seq_start = time.perf_counter()
        W_seq = sequential_unwrite(W_base.copy(), Xi_evict, N)
        t_seq_end = time.perf_counter()
        timing_seq[K] = t_seq_end - t_seq_start

        # Batch
        t_bat_start = time.perf_counter()
        W_bat = batch_unwrite(W_base.copy(), Xi_evict, N)
        t_bat_end = time.perf_counter()
        timing_batch[K] = t_bat_end - t_bat_start

        # Accuracy post-eviction (using batch result)
        acc_post[K] = retrieval_accuracy(W_bat, Xi_remain) if Xi_remain.shape[0] > 0 else 0.0

    # Amortized cost ratio: (large_K time / large_K) vs (small_K time / small_K)
    wall_per_k_small = timing_batch.get(K_small, 1e-6) / K_small
    wall_per_k_large = timing_batch.get(K_large, 1e-6) / K_large
    amortized_ratio = wall_per_k_large / (wall_per_k_small + 1e-12)

    # Batch speedup vs sequential
    wall_seq_large = timing_seq.get(K_large, 1e-6)
    wall_batch_large = timing_batch.get(K_large, 1e-6)
    speedup = wall_seq_large / (wall_batch_large + 1e-12)

    # Mean accuracy post-eviction across K values
    mean_acc = float(np.mean(list(acc_post.values())))

    assert mean_acc >= 0.0, "acc_post_eviction is negative -- instrumentation bug"

    cell_A_pass = amortized_ratio <= HP_AMORTIZED_RATIO
    cell_A_hf = amortized_ratio > HF_AMORTIZED_RATIO
    cell_B_pass = speedup >= HP_SPEEDUP
    cell_B_hf = speedup < HF_SPEEDUP
    cell_C_pass = mean_acc >= HP_ACC_POST
    cell_C_hf = mean_acc < HF_ACC_POST

    return {
        "N": N,
        "run_mode": RUN_MODE,
        "seed": seed,
        "amortized_ratio": amortized_ratio,
        "speedup": speedup,
        "mean_acc_post_eviction": mean_acc,
        "timing_batch": {str(k): v for k, v in timing_batch.items()},
        "timing_seq": {str(k): v for k, v in timing_seq.items()},
        "acc_post": {str(k): v for k, v in acc_post.items()},
        "cell_A_pass": cell_A_pass,
        "cell_A_hf": cell_A_hf,
        "cell_B_pass": cell_B_pass,
        "cell_B_hf": cell_B_hf,
        "cell_C_pass": cell_C_pass,
        "cell_C_hf": cell_C_hf,
    }


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        result = run_one_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"[seed={seed}] amort_ratio={result['amortized_ratio']:.3f} speedup={result['speedup']:.3f} acc={result['mean_acc_post_eviction']:.3f}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    n_seeds = len(SEEDS)

    all_amort = [per_seed[str(s)]["amortized_ratio"] for s in SEEDS]
    all_speedup = [per_seed[str(s)]["speedup"] for s in SEEDS]
    all_acc = [per_seed[str(s)]["mean_acc_post_eviction"] for s in SEEDS]

    mean_amort = float(np.mean(all_amort))
    mean_speedup = float(np.mean(all_speedup))
    mean_acc = float(np.mean(all_acc))

    n_A = sum(1 for s in SEEDS if per_seed[str(s)]["cell_A_pass"])
    n_A_hf = sum(1 for s in SEEDS if per_seed[str(s)]["cell_A_hf"])
    n_B = sum(1 for s in SEEDS if per_seed[str(s)]["cell_B_pass"])
    n_B_hf = sum(1 for s in SEEDS if per_seed[str(s)]["cell_B_hf"])
    n_C = sum(1 for s in SEEDS if per_seed[str(s)]["cell_C_pass"])
    n_C_hf = sum(1 for s in SEEDS if per_seed[str(s)]["cell_C_hf"])

    thr = math.ceil(n_seeds * 0.6)
    cell_A_pass = n_A >= thr
    cell_B_pass = n_B >= thr
    cell_C_pass = n_C >= thr
    hf_A = n_A_hf >= thr
    hf_C = n_C_hf >= thr

    n_cells_pass = int(cell_A_pass) + int(cell_B_pass) + int(cell_C_pass)
    if n_cells_pass == 3:
        verdict = "HARD_PASS"
    elif hf_A or hf_C:
        verdict = "HARD_FAIL"
    elif n_cells_pass >= 2:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL"

    elapsed = time.time() - t0
    verdict_msg = (
        f"caching_eviction_cost_amortized_v1 verdict={verdict}: "
        f"mean_amortized_ratio={mean_amort:.3f}(HP<={HP_AMORTIZED_RATIO},HF>{HF_AMORTIZED_RATIO}) "
        f"mean_speedup={mean_speedup:.3f}(HP>={HP_SPEEDUP},HF<{HF_SPEEDUP}) "
        f"mean_acc_post_eviction={mean_acc:.3f}(HP>={HP_ACC_POST}) "
        f"cells={n_cells_pass}/3 elapsed={elapsed:.1f}s"
    )
    print(verdict_msg, flush=True)

    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "N": N,
        "n_seeds": n_seeds,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "mean_amortized_ratio": mean_amort,
        "mean_speedup": mean_speedup,
        "mean_acc_post_eviction": mean_acc,
        "n_cell_A_pass": n_A,
        "n_cell_B_pass": n_B,
        "n_cell_C_pass": n_C,
        "elapsed_s": elapsed,
    }
    with open(Path(out_dir) / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] metrics written to {out_dir}/metrics.json", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
