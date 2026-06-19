"""
implicit_gram_solve_v1 -- Implicit Gram-solve retrieval vs explicit W.

SCIENTIFIC QUESTION (Q-A4 from research priorities):
  Does implicit Gram-solve retrieval:
    v_retrieved = Xi @ (Xi^T @ Xi / N)^{-1} @ (Xi^T @ query) / N
  (equivalently: Xi @ solve(Gram, Xi^T @ query) where Gram = Xi^T @ Xi / N)
  deliver equivalent or better retrieval quality compared to standard
  Hopfield W @ query iteration, while being cheaper to store and query?

  Theory predictions:
  - Storage: Gram = M x M matrix at 4 MB (float32, M=1000) vs W = N x N at 67 MB.
  - Per-query FLOP: O(M*N) Gram-solve vs O(N^2) W-multiply.
  - Quality: Gram-solve is pseudo-inverse retrieval -- exact for M << N.
  - At alpha = M/N = 0.12 (near capacity), both should produce similar retrieval
    but Gram-solve uses less memory.

PRE-REGISTERED BANDS:
  HARD-PASS: retrieval_accuracy_gram >= retrieval_accuracy_hopfield - 0.05
             (Gram-solve within 5pp of Hopfield across M/N sweep),
             AND Gram memory < 0.10 * Hopfield memory at M=500.
  MIDDLE: gram_acc < hopfield_acc by 5-15pp (some degradation at high alpha).
  HARD-FAIL: gram_acc < hopfield_acc - 0.15pp (severe degradation).

  Calibration note: no prior empirical anchor for Gram-solve on BSC patterns.
  Calibration probe policy: HP band is +-5pp (not the point prediction).

FORMULA SELF-TESTS:
  1. Gram = Xi^T @ Xi / N is M x M. At M=100, N=4096: Gram is 100x100.
  2. Memory ratio: M^2 / N^2 = (100/4096)^2 = 0.000597 (tiny).
  3. Pattern: Xi @ solve(Gram, Xi^T @ q) normalizes to N.

TIMEOUT ESTIMATE:
  Smoke: N=4096, M in {50,100,200,500}, 2 seeds, 200 queries per cell.
  Full: same M sweep, 5 seeds, 500 queries.
  Scaling: 2.5x seeds, 2.5x queries.
  Target smoke <60s -> full ~375s -> timeout=600s.

No _nN suffix; production N=4096 per rule 3.
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

ANCHOR_NAME = "implicit_gram_solve_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 4096

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_LIST = [50, 100, 200, 500]
    N_QUERIES = 100
    NOISE_FRAC = 0.10   # flip 10% of bits for noisy query
    N_HOPFIELD_STEPS = 5
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_LIST = [50, 100, 200, 500]
    N_QUERIES = 300
    NOISE_FRAC = 0.10
    N_HOPFIELD_STEPS = 5

# Pre-reg thresholds
HP_ACC_DELTA = -0.05   # gram >= hopfield - 0.05 (within 5pp)
HF_ACC_DELTA = -0.15   # HARD-FAIL if gram < hopfield - 0.15pp

# Formula self-tests
_gram_size_test = (100 ** 2) / (4096 ** 2)
assert _gram_size_test < 0.001, f"Gram memory ratio test: expected <0.001, got {_gram_size_test}"


def build_xi(M: int, N: int, seed: int) -> np.ndarray:
    """Generate M x N BSC +-1 patterns."""
    rng = np.random.RandomState(seed)
    return rng.choice([-1.0, 1.0], size=(M, N))


def hopfield_retrieve(W: np.ndarray, query: np.ndarray, n_steps: int = 5) -> np.ndarray:
    """Synchronous Hopfield retrieval: s_{t+1} = sign(W s_t)."""
    s = query.copy()
    for _ in range(n_steps):
        s_new = np.where(W @ s > 0, 1.0, -1.0)
        if np.all(s_new == s):
            break
        s = s_new
    return s


def gram_solve_retrieve(Xi: np.ndarray, query: np.ndarray) -> np.ndarray:
    """
    Gram-solve (pseudo-inverse) retrieval.
    v = Xi^T @ solve(Xi @ Xi^T / N, Xi @ query / N)
    This gives the minimum-norm solution to Xi^T v = query.
    Returns sign(v) as binary pattern.
    """
    M, N = Xi.shape
    # Gram matrix M x M
    Gram = (Xi @ Xi.T) / N
    # Project query into pattern space
    xi_q = (Xi @ query) / N   # M-vector: overlaps with each pattern
    # Solve Gram @ c = xi_q for coefficients c
    try:
        c = np.linalg.solve(Gram + 1e-8 * np.eye(M), xi_q)
    except np.linalg.LinAlgError:
        c = np.linalg.lstsq(Gram, xi_q, rcond=None)[0]
    # Reconstruct: v = Xi^T @ c
    v = Xi.T @ c   # N-vector
    return np.where(v > 0, 1.0, -1.0)


def pattern_accuracy(retrieved: np.ndarray, target: np.ndarray) -> float:
    """Fraction of bits matching between retrieved and target."""
    return float(np.mean(retrieved == target))


def run_cell(M: int, N: int, seed: int, n_queries: int) -> Dict:
    """Compare Gram-solve vs Hopfield retrieval at a given M."""
    rng_q = np.random.RandomState(seed + 999)
    Xi = build_xi(M, N, seed)
    W = Xi.T @ Xi / N   # N x N Hopfield weight matrix

    hop_accs = []
    gram_accs = []
    for q_idx in range(n_queries):
        # Pick a random stored pattern, add noise
        pat_idx = rng_q.randint(0, M)
        target = Xi[pat_idx]
        noise = rng_q.rand(N) < NOISE_FRAC
        query = target.copy()
        query[noise] *= -1.0

        # Hopfield retrieval
        retrieved_hop = hopfield_retrieve(W, query, N_HOPFIELD_STEPS)
        acc_hop = pattern_accuracy(retrieved_hop, target)
        hop_accs.append(acc_hop)

        # Gram-solve retrieval
        retrieved_gram = gram_solve_retrieve(Xi, query)
        acc_gram = pattern_accuracy(retrieved_gram, target)
        gram_accs.append(acc_gram)

    mean_hop = float(np.mean(hop_accs))
    mean_gram = float(np.mean(gram_accs))
    delta = mean_gram - mean_hop

    # Memory comparison (bytes)
    mem_hopfield = N * N * 4   # float32 W (N x N)
    mem_gram = M * M * 4       # float32 Gram (M x M)
    mem_ratio = mem_gram / mem_hopfield

    print(f"  [M={M}] hop_acc={mean_hop:.3f} gram_acc={mean_gram:.3f} "
          f"delta={delta:+.3f} mem_ratio={mem_ratio:.5f}", flush=True)

    return {
        "M": M, "N": N,
        "hopfield_acc": mean_hop,
        "gram_acc": mean_gram,
        "acc_delta": delta,
        "mem_hopfield_bytes": mem_hopfield,
        "mem_gram_bytes": mem_gram,
        "mem_ratio": mem_ratio,
        "alpha": M / N,
        "n_queries": n_queries,
    }


def run_seed(seed: int) -> Dict:
    print(f"[seed {seed}] starting M_LIST={M_LIST}", flush=True)
    cells = {}
    for M in M_LIST:
        cells[M] = run_cell(M, N, seed, N_QUERIES)
    return {"cells": cells, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert retrieval metrics are non-null and that Gram-solve produces valid output."""
    N_test = 256
    M_test = 20
    seed = 42
    n_q = 20

    result = run_cell(M_test, N_test, seed, n_q)
    assert result["hopfield_acc"] > 0.5, f"hopfield_acc too low: {result['hopfield_acc']}"
    assert result["gram_acc"] > 0.5, f"gram_acc too low: {result['gram_acc']}"
    assert result["mem_ratio"] < 0.1, f"mem_ratio not small: {result['mem_ratio']}"
    assert not math.isnan(result["acc_delta"]), "acc_delta is NaN"

    print(f"[selftest] PASS: hop_acc={result['hopfield_acc']:.3f} "
          f"gram_acc={result['gram_acc']:.3f} mem_ratio={result['mem_ratio']:.6f}", flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    """Verify pre-registered formula predictions."""
    mem_ratio = (100 ** 2) / (4096 ** 2)
    assert mem_ratio < 0.001, f"Gram memory ratio error: {mem_ratio}"
    print("[formula_selftests] PASS: Gram memory ratio formula verified", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    """Aggregate cell results across seeds."""
    agg = {}
    for M in M_LIST:
        hop_accs, gram_accs, deltas, mem_ratios = [], [], [], []
        for seed_data in per_seed.values():
            cell = seed_data["cells"].get(M) or seed_data["cells"].get(str(M))
            if cell is None:
                continue
            hop_accs.append(cell["hopfield_acc"])
            gram_accs.append(cell["gram_acc"])
            deltas.append(cell["acc_delta"])
            mem_ratios.append(cell["mem_ratio"])
        agg[M] = {
            "M": M, "alpha": M / N,
            "mean_hop_acc": float(np.mean(hop_accs)) if hop_accs else float("nan"),
            "mean_gram_acc": float(np.mean(gram_accs)) if gram_accs else float("nan"),
            "mean_delta": float(np.mean(deltas)) if deltas else float("nan"),
            "mean_mem_ratio": float(np.mean(mem_ratios)) if mem_ratios else float("nan"),
            "n_seeds": len(hop_accs),
        }
    return agg


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    """Pre-registered verdict."""
    deltas = [v["mean_delta"] for v in agg.values() if not math.isnan(v["mean_delta"])]
    if not deltas:
        return ("HARD_FAIL", "No valid delta estimates. Instrumentation failure.")

    min_delta = min(deltas)
    mean_delta = float(np.mean(deltas))
    mean_hop = float(np.mean([v["mean_hop_acc"] for v in agg.values()
                               if not math.isnan(v.get("mean_hop_acc", float("nan")))]))
    mean_gram = float(np.mean([v["mean_gram_acc"] for v in agg.values()
                                if not math.isnan(v.get("mean_gram_acc", float("nan")))]))
    min_mem = min(v["mean_mem_ratio"] for v in agg.values()
                  if not math.isnan(v.get("mean_mem_ratio", float("nan"))))

    hp = min_delta >= HP_ACC_DELTA and min_mem < 0.10
    hf = min_delta < HF_ACC_DELTA

    if hp:
        return ("HARD_PASS",
                f"Gram-solve confirmed equivalent to Hopfield. "
                f"min_delta={min_delta:+.3f} (HP>={HP_ACC_DELTA}). "
                f"mean_hop={mean_hop:.3f} mean_gram={mean_gram:.3f}. "
                f"Memory: Gram ratio={min_mem:.5f} (< 0.10 threshold confirmed).")
    if hf:
        return ("HARD_FAIL",
                f"Gram-solve significantly worse than Hopfield. "
                f"min_delta={min_delta:+.3f} < HF {HF_ACC_DELTA}. "
                f"Gram-solve not viable as Hopfield replacement.")
    return ("MIDDLE_BAND",
            f"Gram-solve partially equivalent. "
            f"min_delta={min_delta:+.3f} mean_delta={mean_delta:+.3f}. "
            f"Some alpha values show degradation beyond HP threshold.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} M_LIST={M_LIST} "
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
        "run_mode": RUN_MODE, "N": N,
        "M_LIST": M_LIST, "N_QUERIES": N_QUERIES,
        "seeds": SEEDS,
        "aggregated": agg,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
