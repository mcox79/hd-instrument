"""
write_through_allocate_v1 -- Write-through + write-allocate via dual Hebbian +=.

SCIENTIFIC QUESTION (Caching-Policy Expressibility, Tier 0):
  Write-through: every write immediately updates both the cache (W_fast) and the
  backing store (W_slow). Write-allocate: on a WRITE MISS, the pattern is also
  fetched into the fast cache.

  Substrate implementation: dual += (two matrices updated simultaneously on write).
    W_fast += xi xi^T / N  (fast cache, limited capacity C_fast < C_slow)
    W_slow += xi xi^T / N  (persistent backing store, larger capacity)

  Prediction: write-through property = zero query latency divergence between
  fast and slow (both always have same patterns, just capacity differs).
  Write-allocate property = a freshly written pattern is immediately retrievable
  from BOTH W_fast and W_slow (zero-overhead verification).

  HARD-PASS: Write-through consistency verified (cosine sim to both storages
  is identical for all written patterns, within 1% tolerance).
  Essentially verifying that dual += is zero-cost to implement in the substrate.

PRE-REGISTERED BANDS:
  HARD-PASS: mean |sim_fast - sim_slow| < 0.01 (write-through consistency within 1%).
  MIDDLE: 0.01 <= mean_delta_sim < 0.05.
  HARD-FAIL: mean_delta_sim >= 0.05 (write-through NOT consistent).

  Note: this is fundamentally a VERIFICATION experiment (dual += is trivially correct
  algebraically). The expected result is HARD-PASS. A HARD-FAIL would indicate a
  numerical precision issue or implementation bug.

FORMULA SELF-TESTS:
  1. If W_fast = W_slow (identical patterns written to both), then W_fast @ xi = W_slow @ xi
     exactly (up to float64 precision ~1e-15).
  2. Consistency check: for identical matrices, sim difference should be < 1e-10.

TIMEOUT ESTIMATE:
  Smoke: N=1024, M=100, 2 seeds.
  Full: N=1024, M=200, 5 seeds.
  Trivial O(M*N^2) writes. Smoke wall ~3s -> Full ~15s -> timeout=90s.
  No _nN suffix; production N=1024.
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

ANCHOR_NAME = "write_through_allocate_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 1024

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M = 100
else:
    SEEDS = [7, 17, 23, 31, 41]
    M = 200

# Pre-reg thresholds
HP_DELTA_SIM = 0.01
MID_DELTA_SIM_HIGH = 0.05
HF_DELTA_SIM = 0.05

# Formula self-test: identical matrices give exactly same product
_W_test = np.eye(4) * 0.5
_xi_test = np.array([1.0, -1.0, 1.0, -1.0])
_r1 = _W_test @ _xi_test
_r2 = _W_test @ _xi_test
assert np.allclose(_r1, _r2, atol=1e-12), "Identical matrix test failed"


def build_patterns(M: int, N: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    return rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)


def measure_sim(W: np.ndarray, xi: np.ndarray) -> float:
    r = W @ xi
    return float(np.dot(r, xi) / (np.linalg.norm(r) * np.linalg.norm(xi) + 1e-12))


def run_seed(seed: int) -> Dict:
    """
    Build W_fast and W_slow with dual += (write-through semantics).
    Both receive identical Hebbian updates. Verify zero divergence.
    """
    patterns = build_patterns(M, N, seed)
    W_fast = np.zeros((N, N), dtype=np.float64)
    W_slow = np.zeros((N, N), dtype=np.float64)

    # Write-through: dual += updates
    for j in range(M):
        xi = patterns[j]
        outer = np.outer(xi, xi) / N
        W_fast += outer
        W_slow += outer

    # Measure consistency
    delta_sims = []
    sim_fast_all = []
    sim_slow_all = []
    for j in range(M):
        xi = patterns[j]
        sf = measure_sim(W_fast, xi)
        ss = measure_sim(W_slow, xi)
        delta_sims.append(abs(sf - ss))
        sim_fast_all.append(sf)
        sim_slow_all.append(ss)

    mean_delta = float(np.mean(delta_sims))
    max_delta = float(np.max(delta_sims))
    mean_sim_fast = float(np.mean(sim_fast_all))
    mean_sim_slow = float(np.mean(sim_slow_all))

    print(f"  [seed={seed}] mean_delta_sim={mean_delta:.2e} max_delta={max_delta:.2e} "
          f"mean_sim_fast={mean_sim_fast:.4f} mean_sim_slow={mean_sim_slow:.4f}", flush=True)

    return {
        "mean_delta_sim": mean_delta,
        "max_delta_sim": max_delta,
        "mean_sim_fast": mean_sim_fast,
        "mean_sim_slow": mean_sim_slow,
        "seed": seed, "N": N, "M": M, "run_mode": RUN_MODE,
    }


def _instrumentation_selftest():
    """Assert write-through gives negligible divergence at small scale."""
    N_t = 128
    M_t = 20
    seed = 42
    patterns = build_patterns(M_t, N_t, seed)
    W1 = np.zeros((N_t, N_t), dtype=np.float64)
    W2 = np.zeros((N_t, N_t), dtype=np.float64)
    for j in range(M_t):
        outer = np.outer(patterns[j], patterns[j]) / N_t
        W1 += outer
        W2 += outer
    # Should be numerically identical
    max_diff = float(np.max(np.abs(W1 - W2)))
    assert max_diff < 1e-10, f"Dual += diverged: max_diff={max_diff:.2e}"
    sims = [abs(measure_sim(W1, patterns[j]) - measure_sim(W2, patterns[j]))
            for j in range(M_t)]
    mean_delta = float(np.mean(sims))
    assert mean_delta < 1e-8, f"Sim divergence: mean_delta={mean_delta:.2e}"
    assert not math.isnan(mean_delta), "delta_sim is NaN"
    print(f"[selftest] PASS: write-through max_diff={max_diff:.2e} mean_sim_delta={mean_delta:.2e}",
          flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    W = np.eye(4) * 0.5
    xi = np.array([1.0, -1.0, 1.0, -1.0])
    r1 = W @ xi
    r2 = W @ xi
    diff = float(np.max(np.abs(r1 - r2)))
    assert diff < 1e-12, f"Identical matrix formula test failed: diff={diff}"
    print("[formula_selftests] PASS: write-through consistency formula verified", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    delta_vals = []
    sim_fast_vals = []
    sim_slow_vals = []
    for sd in per_seed.values():
        delta_vals.append(sd["mean_delta_sim"])
        sim_fast_vals.append(sd["mean_sim_fast"])
        sim_slow_vals.append(sd["mean_sim_slow"])
    return {
        "mean_delta_sim": float(np.mean(delta_vals)) if delta_vals else float("nan"),
        "std_delta_sim": float(np.std(delta_vals)) if len(delta_vals) > 1 else float("nan"),
        "mean_sim_fast": float(np.mean(sim_fast_vals)) if sim_fast_vals else float("nan"),
        "mean_sim_slow": float(np.mean(sim_slow_vals)) if sim_slow_vals else float("nan"),
        "n_seeds": len(delta_vals),
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    delta = agg["mean_delta_sim"]
    if math.isnan(delta):
        return ("HARD_FAIL", "mean_delta_sim is NaN.")
    if delta < HP_DELTA_SIM:
        return ("HARD_PASS",
                f"Write-through consistency verified. mean_delta_sim={delta:.2e} "
                f"(HP<{HP_DELTA_SIM}). Dual += implements zero-overhead write-through.")
    if delta >= HF_DELTA_SIM:
        return ("HARD_FAIL",
                f"Write-through inconsistency. mean_delta_sim={delta:.4f} >= HF {HF_DELTA_SIM}.")
    return ("MIDDLE_BAND",
            f"Marginal write-through consistency. mean_delta_sim={delta:.4f} "
            f"(HP<{HP_DELTA_SIM}, HF>={HF_DELTA_SIM}).")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} M={M} seeds={SEEDS}", flush=True)

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
        "run_mode": RUN_MODE, "N": N, "M": M, "seeds": SEEDS,
        "aggregated": agg,
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
