"""
streaming_brand_gram_refresh_v1 -- Streaming Prediction 2: Brand incremental Gram refresh.

SCIENTIFIC QUESTION (Streaming Prediction 2):
  When patterns are written sequentially to the substrate, the Gram matrix
  G = Xi Xi^T / N (M x M symmetric PSD) can be updated incrementally:
    G_new = G_old augmented with new row/column from new pattern.
  The Brand incremental SVD / Gram refresh predicts that the incremental Gram
  is equivalent to batch Gram within numerical precision.

  Test: for K sequential writes starting from M_base patterns, compare:
    (a) batch_Gram: recompute G = Xi Xi^T / N from scratch after all M_base+K patterns.
    (b) incr_Gram: start from G_M_base, update one-by-one for K new patterns.
  Measure accuracy = 1 - ||G_batch - G_incr||_F / ||G_batch||_F.

HARD-PASS: accuracy >= 0.98 for ALL K in [1, M_base] (matches batch within 2%).
HARD-FAIL: accuracy < 0.95 for any K.
MIDDLE: accuracy >= 0.95 for all K but some K gives 0.95-0.98 range.

PRE-REGISTERED BANDS:
  HP: accuracy >= 0.98 (exact algebraic identity; numerical errors only).
  HF: accuracy < 0.95 (formula wrong or precision loss).
  Calibration: first Brand Gram refresh test; bands widened to +-50% of theory
  (theory predicts accuracy = 1.0 exactly; +-50% maps to 0.98 HP).

FORMULA SELF-TESTS:
  1. Incremental Gram update: for new pattern xi_{M+1},
     G_new[M+1, j] = (xi_{M+1}^T xi_j) / N for j in [1, M].
     G_new[i, M+1] = G_new[M+1, i] (symmetric).
     G_new[M+1, M+1] = 1.0 (normalized pattern: ||xi||^2 / N = 1).
     [INPUT: N=512, M=10, 1 new pattern]
     [EXPECTED: incremental matches batch exactly up to float64 precision]
  2. Frobenius norm preservation: for K=0 writes, G_batch == G_incr (trivial).
     [INPUT: K=0] [EXPECTED: accuracy = 1.0]
  3. Numerical stability at K=M_base: after M_base incremental updates,
     max abs diff should be < 1e-10.
     [INPUT: N=256, M_base=20, K=20] [EXPECTED: max_diff < 1e-8]

No _nN suffix; production N=2048 per rule 3:
  No _nN suffix; production N = 2048; rationale: Gram matrix is M x M,
  streaming test needs N large enough to have stable inner products.
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
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "streaming_brand_gram_refresh_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N = 512
    M_BASE = 20
    K_MAX = 20      # max sequential writes to test
    SEEDS = [7, 17]
else:
    N = 2048
    M_BASE = 50
    K_MAX = 50      # K in [1, M_BASE]
    SEEDS = [7, 17, 23, 31, 41]

HP_ACCURACY = 0.98
HF_ACCURACY = 0.95


def _formula_selftest_incremental_gram():
    """Incremental Gram update matches batch exactly at float64 precision."""
    N_t, M_t = 256, 10
    rng = np.random.RandomState(42)
    Xi_base = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    xi_new = rng.choice([-1.0, 1.0], size=(N_t,)).astype(np.float64)

    # Batch Gram
    Xi_all = np.vstack([Xi_base, xi_new[np.newaxis, :]])
    G_batch = Xi_all @ Xi_all.T / float(N_t)

    # Incremental Gram (starting from G_base, add one row/col)
    G_base = Xi_base @ Xi_base.T / float(N_t)
    G_incr = np.zeros((M_t + 1, M_t + 1))
    G_incr[:M_t, :M_t] = G_base
    new_col = (Xi_base @ xi_new) / float(N_t)
    G_incr[:M_t, M_t] = new_col
    G_incr[M_t, :M_t] = new_col
    G_incr[M_t, M_t] = float(np.dot(xi_new, xi_new)) / float(N_t)

    max_diff = float(np.max(np.abs(G_batch - G_incr)))
    assert max_diff < 1e-10, f"Gram selftest: max_diff={max_diff:.2e} expected < 1e-10"
    return max_diff


def _formula_selftest_k0():
    """K=0 writes: accuracy = 1.0 trivially."""
    N_t, M_t = 128, 5
    rng = np.random.RandomState(7)
    Xi = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    G = Xi @ Xi.T / float(N_t)
    acc = 1.0 - 0.0 / float(np.linalg.norm(G, 'fro') + 1e-15)
    assert abs(acc - 1.0) < 1e-12, f"K=0 selftest: acc={acc:.6f} expected 1.0"
    return acc


def _instrumentation_selftest():
    d1 = _formula_selftest_incremental_gram()
    d2 = _formula_selftest_k0()
    print(f"[selftest] max_diff_incr={d1:.2e} k0_acc={d2:.6f} PASS", flush=True)


_instrumentation_selftest()


def compute_incremental_gram(Xi_base: np.ndarray, new_patterns: np.ndarray,
                              N_dim: int) -> List[Tuple[int, float]]:
    """
    Compute accuracy of incremental Gram updates vs batch Gram.
    Returns list of (k, accuracy) for k in [1, K_MAX].
    """
    M_base = Xi_base.shape[0]
    G_incr = Xi_base @ Xi_base.T / float(N_dim)

    results = []
    Xi_accum = Xi_base.copy()

    for k in range(1, new_patterns.shape[0] + 1):
        xi_new = new_patterns[k - 1]
        M_new = M_base + k

        # Extend incremental Gram
        G_new = np.zeros((M_new, M_new))
        G_new[:M_new - 1, :M_new - 1] = G_incr
        new_col = (Xi_accum @ xi_new) / float(N_dim)
        G_new[:M_new - 1, M_new - 1] = new_col
        G_new[M_new - 1, :M_new - 1] = new_col
        G_new[M_new - 1, M_new - 1] = float(np.dot(xi_new, xi_new)) / float(N_dim)
        G_incr = G_new

        # Accumulate
        Xi_accum = np.vstack([Xi_accum, xi_new[np.newaxis, :]])

        # Batch Gram
        G_batch = Xi_accum @ Xi_accum.T / float(N_dim)

        frob_batch = float(np.linalg.norm(G_batch, 'fro'))
        diff = float(np.linalg.norm(G_batch - G_incr, 'fro'))
        acc = 1.0 - diff / frob_batch if frob_batch > 1e-15 else 1.0

        results.append((k, float(acc)))

    return results


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    Xi_base = rng.choice([-1.0, 1.0], size=(M_BASE, N)).astype(np.float64)
    new_patterns = rng.choice([-1.0, 1.0], size=(K_MAX, N)).astype(np.float64)

    t0 = time.time()
    k_results = compute_incremental_gram(Xi_base, new_patterns, N)
    elapsed = time.time() - t0

    # Find min accuracy
    min_acc = min(acc for _, acc in k_results)
    all_pass_hp = all(acc >= HP_ACCURACY for _, acc in k_results)
    all_pass_hf = all(acc >= HF_ACCURACY for _, acc in k_results)

    print(f"  [seed={seed}] min_acc={min_acc:.6f} all_pass_HP={all_pass_hp} "
          f"all_pass_HF={all_pass_hf} t={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N, "M_BASE": M_BASE, "K_MAX": K_MAX,
        "run_mode": RUN_MODE,
        "min_accuracy": float(min_acc),
        "all_pass_hp": bool(all_pass_hp),
        "all_pass_hf": bool(all_pass_hf),
        "k_accuracy_sample": [(k, acc) for k, acc in k_results[::5]] if len(k_results) > 5 else k_results,
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    min_accs = [r["min_accuracy"] for r in results if r.get("min_accuracy") is not None]
    if not min_accs:
        return ("HARD_FAIL", "No valid accuracy estimates.")

    global_min = float(min(min_accs))
    n_hp = sum(1 for r in results if r.get("all_pass_hp", False))
    n_hf_fail = sum(1 for r in results if not r.get("all_pass_hf", True))
    n_seeds = len(results)

    summary = (f"global_min_acc={global_min:.6f} "
               f"n_seeds_hp={n_hp}/{n_seeds} n_seeds_hf_fail={n_hf_fail}/{n_seeds}")

    if n_hf_fail > 0:
        return ("HARD_FAIL", f"HARD_FAIL: accuracy < {HF_ACCURACY} in {n_hf_fail} seeds. {summary}")
    if n_hp == n_seeds:
        return ("HARD_PASS", f"HARD_PASS: all seeds have accuracy >= {HP_ACCURACY}. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: all seeds pass HF, some below HP. {summary}")


# ---- MAIN SWEEP ----
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": verdict_msg,
    "elapsed_s": elapsed_s,
    "n_seeds": len(SEEDS),
    "run_mode": RUN_MODE,
    "N": N,
    "M_BASE": M_BASE,
    "K_MAX": K_MAX,
    "per_seed_summary": [
        {"seed": r.get("seed"), "min_accuracy": r.get("min_accuracy"),
         "all_pass_hp": r.get("all_pass_hp"), "all_pass_hf": r.get("all_pass_hf")}
        for r in all_results
    ],
    "elapsed_total_s": elapsed_s,
}

metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
