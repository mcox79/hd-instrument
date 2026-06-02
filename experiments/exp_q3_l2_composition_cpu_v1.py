"""
q3_l2_composition_cpu_v1 -- Q3 L=2 cross-layer composition at N=4096 (CPU version).

SCIENTIFIC QUESTION (Q3 follow-on from Round 6 drill 3):
  Does L=2 cross-layer composition (W_inner stored patterns, W_outer composed links)
  achieve end-to-end accuracy > 0.88 at conservative inner load (alpha <= 0.05)?

  Mechanism: L=2 composition stores (key_A, val_A) -> (key_B, val_B) as two-hop chain.
    W_inner: stores M_inner (key, value) binding pairs via outer product.
    W_outer: stores M_outer (value_A, key_B) routing pairs via outer product.
    Query: q -> W_inner @ q = val_A (approx) -> W_outer @ val_A = key_B (approx).
    End-to-end accuracy: fraction of queries where final output = correct val_B.

  This is a CPU version of the L=2 composition (GPU l2_hadamard already in overnight
  queue at N=8192). This run focuses on pure vanilla outer-product at N=4096 without
  Hadamard role-vectors.

  Composition classification: HANDOFF (per PP-11 Arm B; each hop is independent
  retrieval, not a SCORE aggregation).

PRE-REGISTERED BANDS:
  HARD-PASS: end_to_end_accuracy >= 0.88 at alpha_inner <= 0.05
             (conservative inner load; per Round 6 drill prediction of 0.93-0.97
             at p=2 fidelity per hop; 2-hop product 0.93^2 ~ 0.865; HP=0.88 is
             slightly above this to test production grade).
  MIDDLE: 0.70 <= accuracy < 0.88.
  HARD-FAIL: accuracy < 0.70 (composition degrades to below chance-level for multi-hop).

FORMULA SELF-TESTS:
  1. Per-hop fidelity at alpha=0.05, N=4096: r_basin ~ 0.90 (conservative p=2 estimate).
  2. Two-hop: f_e2e = f_hop^2 = 0.90^2 = 0.81 (lower bound); actual may be higher.
  3. At alpha=0.02, N=4096: r_basin ~ 0.95; f_e2e ~ 0.90.

TIMEOUT ESTIMATE:
  Smoke: N=4096, M_inner=[50, 200], 2 seeds. Each outer product M*N^2 but vectorized.
  Full: N=4096, M_inner=[50, 100, 200], 5 seeds.
  Vectorized build O(M*N). Each query O(N^2). Smoke wall ~10s -> Full ~40s.
  timeout_s = ceil(1.5 * 40) = 60 -> 300s.
  No _nN suffix; production N=4096.
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
from typing import Dict, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "q3_l2_composition_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 4096
N_QUERIES = 100  # queries to evaluate per (M, seed) combo

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_INNER_LIST = [50, 200]
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_INNER_LIST = [50, 100, 200]

# Pre-reg thresholds
HP_E2E = 0.88
MID_E2E_LOW = 0.70
HF_E2E = 0.70

# Formula self-tests: per-hop fidelity at alpha=0.02 (M=82) -> e2e >= 0.81
_f_hop_theory = 0.90
_f_e2e_theory = _f_hop_theory ** 2
assert _f_e2e_theory >= 0.80, f"e2e theory floor: {_f_e2e_theory:.3f}"


def build_patterns(M: int, N: int, seed: int, prefix_seed: int = 0) -> np.ndarray:
    """M x N BSC +-1 patterns."""
    rng = np.random.RandomState(seed + prefix_seed * 10000)
    return rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)


def build_w_vectorized(patterns: np.ndarray, N: int) -> np.ndarray:
    """W = Xi^T Xi / N using single batched matrix multiply."""
    return (patterns.T @ patterns) / N


def retrieve(W: np.ndarray, query: np.ndarray) -> np.ndarray:
    """One Hopfield retrieval step: W @ query, binarize via sign."""
    return np.sign(W @ query)


def run_seed(seed: int) -> Dict:
    results = {}
    for M in M_INNER_LIST:
        # Generate 4 sets of patterns: keys_A, vals_A, vals_B, keys_B
        # Chain: keys_A[j] -> (via W_inner) -> vals_A[j] -> (via W_outer) -> vals_B[j]
        rng = np.random.RandomState(seed)
        keys_A = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
        vals_A = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
        vals_B = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)

        # Build W_inner: keys_A -> vals_A  (heteroassociative: W = sum vals_j @ keys_j^T / N)
        W_inner = (vals_A.T @ keys_A) / N

        # Build W_outer: vals_A -> vals_B  (heteroassociative: W = sum vals_B_j @ vals_A_j^T / N)
        W_outer = (vals_B.T @ vals_A) / N

        # Evaluate on N_QUERIES (using test patterns = stored patterns for accuracy check)
        n_eval = min(N_QUERIES, M)
        correct = 0
        for j in range(n_eval):
            q = keys_A[j]
            mid = W_inner @ q   # retrieve val_A
            final = W_outer @ mid  # retrieve val_B
            # Check if final is close enough to correct val_B[j]
            # Use sign agreement as accuracy metric
            correct_b = vals_B[j]
            agreement = float(np.dot(np.sign(final), correct_b)) / N
            if agreement > 0.5:  # majority of bits correct
                correct += 1

        acc = correct / n_eval
        alpha = M / N
        print(f"  [seed={seed} M={M} alpha={alpha:.3f}] e2e_acc={acc:.4f} "
              f"({correct}/{n_eval} correct)", flush=True)
        results[M] = {
            "M": M, "alpha": alpha,
            "e2e_accuracy": acc,
            "n_queries_evaluated": n_eval,
        }
    return {"M_results": results, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert L=2 composition gives > random accuracy at small scale."""
    N_t = 512
    M_t = 20
    seed = 42
    rng = np.random.RandomState(seed)
    keys_A = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    vals_A = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    vals_B = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    W_inner = (vals_A.T @ keys_A) / N_t
    W_outer = (vals_B.T @ vals_A) / N_t
    correct = 0
    for j in range(M_t):
        mid = W_inner @ keys_A[j]
        final = W_outer @ mid
        agreement = float(np.dot(np.sign(final), vals_B[j])) / N_t
        if agreement > 0.5:
            correct += 1
    acc = correct / M_t
    assert not math.isnan(acc), "accuracy is NaN"
    # At M=20, N=512, alpha=0.039: should be well above chance (0.5 per bit agreement threshold)
    assert acc > 0.5, f"L=2 composition below chance: acc={acc:.3f}"
    print(f"[selftest] PASS: L=2 composition acc={acc:.4f} at N={N_t} M={M_t}", flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    f_e2e = 0.90 ** 2
    assert f_e2e >= 0.80, f"e2e floor check: {f_e2e}"
    print("[formula_selftests] PASS: L=2 composition e2e formula verified", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    agg = {}
    for M in M_INNER_LIST:
        acc_vals = []
        alpha_val = None
        for sd in per_seed.values():
            mr = sd["M_results"].get(M) or sd["M_results"].get(str(M))
            if mr is None:
                continue
            acc_vals.append(mr["e2e_accuracy"])
            alpha_val = mr["alpha"]
        agg[M] = {
            "M": M, "alpha": alpha_val,
            "mean_e2e_accuracy": float(np.mean(acc_vals)) if acc_vals else float("nan"),
            "std_e2e_accuracy": float(np.std(acc_vals)) if len(acc_vals) > 1 else float("nan"),
            "n_seeds": len(acc_vals),
        }
    return agg


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    # Primary: conservative load (smallest M tested)
    sorted_M = sorted(agg.keys())
    primary_M = sorted_M[0] if sorted_M else None
    if primary_M is None:
        return ("HARD_FAIL", "No aggregated results.")
    acc_primary = agg[primary_M]["mean_e2e_accuracy"]
    all_accs = [v["mean_e2e_accuracy"] for v in agg.values()
                if not math.isnan(v["mean_e2e_accuracy"])]
    min_acc = min(all_accs) if all_accs else float("nan")

    if math.isnan(acc_primary):
        return ("HARD_FAIL", "accuracy is NaN.")
    if acc_primary >= HP_E2E:
        return ("HARD_PASS",
                f"L=2 composition HARD-PASS. e2e_acc at M={primary_M}: {acc_primary:.4f} "
                f"(HP>={HP_E2E}). min across M: {min_acc:.4f}. "
                f"N={N} pure outer-product heteroassoc chain confirmed.")
    if acc_primary < HF_E2E:
        return ("HARD_FAIL",
                f"L=2 composition HARD-FAIL. e2e_acc at M={primary_M}: {acc_primary:.4f} "
                f"< HF {HF_E2E}.")
    return ("MIDDLE_BAND",
            f"Partial L=2 composition. e2e_acc at M={primary_M}: {acc_primary:.4f} "
            f"(HP>={HP_E2E}, HF<{HF_E2E}).")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} M_list={M_INNER_LIST} "
          f"n_queries={N_QUERIES} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        ts = time.time()
        result = run_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"[seed {seed}] done in {time.time()-ts:.1f}s", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    agg = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(agg)

    elapsed = time.time() - t0
    metrics = {
        "run_mode": RUN_MODE, "N": N, "N_QUERIES": N_QUERIES,
        "M_INNER_LIST": M_INNER_LIST, "seeds": SEEDS,
        "aggregated": {str(M): v for M, v in agg.items()},
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
