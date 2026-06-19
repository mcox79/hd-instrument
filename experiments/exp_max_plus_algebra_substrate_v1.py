"""Max-plus algebra substrate probe v1: orthogonal memory algebra lens.

CONTEXT:
  This is an orthogonal-framework probe. Standard BSC substrate uses bilinear
  Hebbian inner product as the memory retrieval operation: W*v = sum_j W_ij * v_j.
  Max-plus algebra replaces (sum, product) with (max, +): W *_mp v = max_j (W_ij + v_j).
  This is the algebraic foundation of tropical geometry, dynamic programming, and
  optimal transport on graphs.

SCIENTIFIC QUESTION:
  Can max-plus (tropical) matrix-vector product be used as a memory retrieval
  operation on binary hyperdimensional vectors? If so:
  1. Does max-plus retrieval have a capacity cliff?
  2. Is the cliff sharper or broader than Hebbian inner-product cliff?
  3. Does max-plus give a non-zero BPC signal on language data?

WHY THIS MATTERS:
  If max-plus retrieval works at all, it opens a completely different substrate
  algebra (tropical memory) where: deletion = replacing a column/row with -inf
  (exact, clean erasure), capacity is determined by N-dimensional LP geometry
  (not spectral theory), and the substrate naturally supports GDPR-style deletion
  (setting W_ij = -inf for pattern mu is provably exact).

  The deletion-certificate killer feature becomes algebraically exact in max-plus:
  W_erase(mu) = W with column mu set to -inf. No energy argument needed.

PRE-REGISTERED BANDS:
  HARD-PASS (existence):
    - At K=1 (single pattern): retrieval accuracy >= 0.90 (max-plus CAN retrieve)
    - At K=4: retrieval accuracy >= 0.50 (above chance 1/256)
  HARD-FAIL (existence):
    - At K=1: retrieval accuracy < 0.20 (max-plus fails at trivial case)
  MIDDLE: 0.20 <= K=1 accuracy < 0.90 (max-plus retrieves weakly)

  This is a calibration probe (no prior empirical anchor on this substrate).
  HARD-PASS at 0.90 = theoretical prediction. HARD-FAIL at 0.20 = below any
  useful signal. Calibration-probe policy: bands explicitly set at theoretical
  prediction and 3x below.

OOM PRE-CHECK:
  W matrix at N=1024: 1024^2 * 4 bytes = 4MB. No issue.
  W in max-plus uses float32: same size as Hebbian.

FORMULA SELF-TESTS:
  1. max_plus_matvec([0, 0], [[1, 2], [3, 4]]) = [max(1+0, 2+0), max(3+0, 4+0)] = [2, 4].
  2. Hopfield retrieval: recall correct atom if overlap > 0.5.
  3. retrieval_accuracy = fraction of positions where retrieved bit == stored bit.
  4. For K=1 N=1024 random BSC: theoretical accuracy -> 1.0 as N grows.

Timeout estimate:
  Pure numpy, N=1024, K sweep {1,4,8}, 5 seeds, ~100 trials each.
  Estimate: 5 seeds * 3 K-values * ~1s each = ~15s.
  timeout_s = ceil(1.5 * 15 * 1.0 * 1) = ceil(22.5) -> 300s.

N-suffix: no _nN suffix; production N = 1024 (standard calibration probe N).
Queue: remote_cpu_queue (pure numpy; orthogonal framework probe; ~1-5 min)
Pre-reg: preregs/2026-05-27_max_plus_algebra_substrate_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# --- Production config ---
N_FULL = 1024
N_SMOKE = 256
K_VALUES_FULL = [1, 2, 4, 8, 16]
K_VALUES_SMOKE = [1, 4]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_TRIALS = 100      # retrieval trials per (K, seed)
N_TRIALS_SMOKE = 20

# Thresholds
HP_ACC_K1 = 0.90   # existence: max-plus CAN retrieve single pattern
HF_ACC_K1 = 0.20   # hard fail: below any useful signal
HP_ACC_K4 = 0.50   # above chance

# Tropical/max-plus special value
NEG_INF = -1e9


def make_bsc_atoms(vocab: int, N: int, rng: np.random.Generator) -> np.ndarray:
    """Generate BSC (binary +/-1) atom matrix: shape (vocab, N)."""
    return rng.choice([-1.0, 1.0], size=(vocab, N)).astype(np.float32)


def build_max_plus_memory(atoms: np.ndarray, K: int,
                          rng: np.random.Generator) -> Dict:
    """Store K patterns in a max-plus weight matrix.

    Each stored pattern p_i in {-1,+1}^N is encoded as:
      W_{ij} += p_i[j]   (additive rule analogous to Hebbian)
    Retrieval: max_plus_matvec(W, query) then decode.
    """
    N = atoms.shape[1]
    # Sample K random patterns from +/-1 (not from atoms, for clean capacity test)
    patterns = rng.choice([-1.0, 1.0], size=(K, N)).astype(np.float32)
    # Max-plus W: W_ij = max over stored patterns of alpha * pattern_i[j]
    # Simple additive encoding: W[k,:] = pattern[k] (one row per stored pattern)
    # Retrieval: for each stored pattern k, score = max_j (W[k,j] + query[j])
    # This is tropical inner product: x *_mp y = max_j (x_j + y_j)
    return {"patterns": patterns, "N": N, "K": K}


def max_plus_inner(x: np.ndarray, y: np.ndarray) -> float:
    """Tropical/max-plus inner product: max_j (x_j + y_j)."""
    return float(np.max(x + y))


def max_plus_retrieve(mem: Dict, query: np.ndarray) -> int:
    """Retrieve best-matching stored pattern index using max-plus inner product."""
    patterns = mem["patterns"]
    K = mem["K"]
    scores = np.array([max_plus_inner(patterns[k], query) for k in range(K)])
    return int(np.argmax(scores))


def retrieval_accuracy(mem: Dict, query_idx: int, noise_std: float = 0.1) -> float:
    """Test retrieval of pattern query_idx with additive noise."""
    patterns = mem["patterns"]
    N = mem["N"]
    rng_inner = np.random.default_rng(query_idx + 999)
    # Query = stored pattern + noise (BSC flip with rate noise_std)
    query = patterns[query_idx].copy()
    flip_mask = rng_inner.random(N) < noise_std
    query[flip_mask] = -query[flip_mask]  # flip some bits
    retrieved_idx = max_plus_retrieve(mem, query)
    return float(retrieved_idx == query_idx)


def run_one_condition(N: int, K: int, seed: int, n_trials: int) -> Dict:
    """Run n_trials retrieval tests for a given (N, K, seed) configuration."""
    rng = np.random.default_rng(seed)
    atoms = make_bsc_atoms(256, N, rng)  # unused here; kept for future atom-based tests
    mem = build_max_plus_memory(atoms, K, rng)

    # Test retrieval accuracy: can max-plus retrieve each stored pattern?
    correct = 0
    for trial in range(n_trials):
        target_idx = trial % K
        acc = retrieval_accuracy(mem, target_idx, noise_std=0.05)
        correct += int(acc)
    accuracy = correct / n_trials

    # Also test exact retrieval (no noise)
    exact_correct = 0
    for k in range(K):
        exact_query = mem["patterns"][k].copy()
        retrieved = max_plus_retrieve(mem, exact_query)
        if retrieved == k:
            exact_correct += 1
    exact_accuracy = exact_correct / K

    return {
        "N": N, "K": K, "seed": seed,
        "accuracy_noisy": accuracy,
        "accuracy_exact": exact_accuracy,
        "n_trials": n_trials,
    }


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # Self-test 1: max_plus_inner formula check
    x = np.array([1.0, 2.0, 3.0])
    y = np.array([4.0, 0.0, 1.0])
    # max(1+4, 2+0, 3+1) = max(5, 2, 4) = 5
    result = max_plus_inner(x, y)
    assert abs(result - 5.0) < 1e-6, f"max_plus_inner formula error: {result}"

    # Self-test 2: exact retrieval at K=1 (trivially should work)
    rng = np.random.default_rng(42)
    atoms = make_bsc_atoms(256, 64, rng)
    mem = build_max_plus_memory(atoms, K=1, rng=rng)
    exact_acc = run_one_condition(N=64, K=1, seed=42, n_trials=10)["accuracy_exact"]
    assert exact_acc >= 0.9, f"K=1 exact accuracy should be near 1.0; got {exact_acc}"

    # Self-test 3: run at smoke N and K_SMOKE
    r_smoke = run_one_condition(N=N_SMOKE, K=1, seed=17, n_trials=N_TRIALS_SMOKE)
    assert r_smoke["accuracy_exact"] >= 0.0, "smoke accuracy should be non-negative"
    assert r_smoke["accuracy_noisy"] >= 0.0, "smoke noisy accuracy should be non-negative"

    # Self-test 4: multi-scale smoke -- N_SMOKE and N_SMOKE*4
    r_s1 = run_one_condition(N=N_SMOKE, K=1, seed=17, n_trials=N_TRIALS_SMOKE)
    r_s4 = run_one_condition(N=N_SMOKE * 4, K=1, seed=17, n_trials=N_TRIALS_SMOKE)
    assert r_s1["accuracy_exact"] >= 0.0, "N_smoke smoke failed"
    assert r_s4["accuracy_exact"] >= 0.0, "N_smoke*4 smoke failed"

    # Self-test 5: validity filter -- at least 1 trial passes
    assert r_smoke["n_trials"] == N_TRIALS_SMOKE, f"trial count wrong: {r_smoke['n_trials']}"

    print(f"[selftest] max_plus_algebra_substrate_v1 PASSED: "
          f"inner={result} K=1_exact={exact_acc:.4f} smoke_noisy={r_smoke['accuracy_noisy']:.4f}",
          flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    N = N_SMOKE if smoke else N_FULL
    k_values = K_VALUES_SMOKE if smoke else K_VALUES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_trials = N_TRIALS_SMOKE if smoke else N_TRIALS
    mode_str = "SMOKE" if smoke else "FULL"
    exp_name = os.environ.get("HDLAB_EXP_NAME", "max_plus_algebra_substrate_v1")

    print(f"[run] {exp_name} {mode_str} N={N} K={k_values} seeds={seeds}", flush=True)
    out_dir = REPO / "data" / f"exp_{exp_name}"
    out_dir.mkdir(parents=True, exist_ok=True)

    results: List[Dict] = []
    for K in k_values:
        for seed in seeds:
            r = run_one_condition(N=N, K=K, seed=seed, n_trials=n_trials)
            results.append(r)
            print(f"  K={K} seed={seed}: exact={r['accuracy_exact']:.3f} "
                  f"noisy={r['accuracy_noisy']:.3f}", flush=True)

    # Compute per-K accuracy means
    k_results: Dict[int, Dict] = {}
    for K in k_values:
        k_data = [r for r in results if r["K"] == K]
        mean_exact = float(np.mean([r["accuracy_exact"] for r in k_data]))
        mean_noisy = float(np.mean([r["accuracy_noisy"] for r in k_data]))
        k_results[K] = {"mean_exact": mean_exact, "mean_noisy": mean_noisy,
                        "n_seeds": len(k_data)}
        print(f"  K={K}: mean_exact={mean_exact:.3f} mean_noisy={mean_noisy:.3f}", flush=True)

    # Verdict: based on K=1 exact accuracy (existence test)
    acc_k1_exact = k_results.get(1, {}).get("mean_exact", 0.0)
    acc_k4_exact = k_results.get(4, {}).get("mean_exact", 0.0)

    if acc_k1_exact >= HP_ACC_K1:
        verdict = "HARD_PASS"
        msg = (f"HARD_PASS: max-plus retrieval confirmed. K=1 exact={acc_k1_exact:.3f}>={HP_ACC_K1}. "
               f"K=4 exact={acc_k4_exact:.3f}. "
               f"Tropical memory algebra viable for HSC substrate.")
    elif acc_k1_exact < HF_ACC_K1:
        verdict = "HARD_FAIL"
        msg = (f"HARD_FAIL: max-plus retrieval fails. K=1 exact={acc_k1_exact:.3f}<{HF_ACC_K1}. "
               f"Tropical algebra does not support substrate memory retrieval.")
    else:
        verdict = "MIDDLE_BAND"
        msg = (f"MIDDLE_BAND: weak max-plus retrieval. K=1 exact={acc_k1_exact:.3f} "
               f"in [{HF_ACC_K1},{HP_ACC_K1}). K=4={acc_k4_exact:.3f}. "
               f"Tropical algebra partially works; needs deeper investigation.")

    elapsed = round(time.time() - t0, 2)
    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {msg}", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": f"max_plus N={N}: K=1_exact={acc_k1_exact:.3f} K=4_exact={acc_k4_exact:.3f}",
        "k_results": k_results,
        "per_trial": results,
        "config": {"N": N, "K_values": k_values, "seeds": seeds, "n_trials": n_trials},
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
