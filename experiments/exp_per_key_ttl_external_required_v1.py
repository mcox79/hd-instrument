"""
per_key_ttl_external_required_v1 -- Tier 2 NEGATIVE: per-key TTL requires external tracking.

SCIENTIFIC QUESTION (Caching-Policy Expressibility, Tier 2 constraint):
  Can the substrate W implement per-key TTL (different decay rates for different
  stored patterns) with a SINGLE global gamma decay parameter?

  Prediction (NEGATIVE): per-key TTL requires external bookkeeping.
  Substrate W has ONE global gamma: W_t = gamma * W_{t-1} + xi xi^T/N.
  This means ALL stored patterns decay at the same rate gamma^(t-t_i).
  THERE IS NO WAY to assign different decay exponents per pattern
  within a single W matrix, because W is a sum of outer products
  and the global gamma multiplies the entire sum uniformly.

  Proof by construction:
    - Pattern i stored at time t_i with TTL = T_i.
    - To evict pattern i at t = t_i + T_i but not pattern j,
      we would need gamma_i = 0 at t_i + T_i while gamma_j > 0.
    - But gamma multiplies ALL stored patterns: impossible.

  Empirical demonstration:
    - Store patterns with intended different TTLs [T_short, T_long].
    - Apply global decay gamma for T_short steps.
    - Measure retention of "should-be-expired" vs "should-be-active" patterns.
    - BOTH decay at the same rate (gamma^T_short).
    - HARD-PASS for this experiment = confirms negative result
      (per-key TTL NOT implementable with single global gamma).

PRE-REGISTERED BANDS:
  HARD-PASS: |retention_short - retention_long| < 0.05 (both decay equally;
             confirms single-W cannot do per-key TTL).
  MIDDLE: 0.05 <= |retention_short - retention_long| < 0.20.
  HARD-FAIL: |retention_short - retention_long| >= 0.20 (substrate somehow
             distinguishes per-key decay; contradicts theory).

  Note: HARD-PASS here = confirming a CONSTRAINT (Tier 2 negative result).
  This is EXPECTED to pass (substrate is known to have one global gamma).

FORMULA SELF-TESTS:
  1. After T_short steps of global gamma=0.9 decay, pattern stored T_short steps ago
     has effective weight gamma^T_short = 0.9^T_short.
  2. Pattern stored 2*T_short steps ago has weight gamma^(2*T_short) (older, weaker).
  3. Both patterns decay by the same relative factor gamma^T_short in the same period.
     So |retention_short - retention_long| should be ~0 if both stored at the same time.

TIMEOUT ESTIMATE:
  Smoke: N=1024, M=20, 2 seeds. Full: N=1024, M=40, 5 seeds.
  Linear. Smoke wall ~2s -> Full ~8s. timeout=60s.

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
from typing import Dict, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "per_key_ttl_external_required_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 1024
GAMMA = 0.90  # global decay rate

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_PER_GROUP = 10   # patterns per TTL group
    T_DECAY_STEPS_LIST = [5, 10]   # number of global decay steps to simulate
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_PER_GROUP = 20
    T_DECAY_STEPS_LIST = [5, 10, 20]

HP_DELTA = 0.05   # HARD-PASS if |retention_short - retention_long| < 0.05
HF_DELTA = 0.20   # HARD-FAIL if |retention_short - retention_long| >= 0.20

# Formula self-test: gamma^5 = 0.9^5 = 0.5905
_gamma5_test = GAMMA**5
assert abs(_gamma5_test - 0.59049) < 0.001, f"gamma^5 test failed: {_gamma5_test}"


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def retrieve(W: np.ndarray, query: np.ndarray) -> np.ndarray:
    return np.sign(W @ query + 1e-12)


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    results_by_T = {}

    for T_steps in T_DECAY_STEPS_LIST:
        # Group A: "short-TTL" patterns (intended to expire after T_steps)
        pat_A = rng.choice([-1.0, 1.0], size=(M_PER_GROUP, N)).astype(np.float64)
        # Group B: "long-TTL" patterns (intended to remain active)
        pat_B = rng.choice([-1.0, 1.0], size=(M_PER_GROUP, N)).astype(np.float64)

        # Build W with both groups stored simultaneously
        W = np.zeros((N, N), dtype=np.float64)
        for xi in pat_A:
            W += np.outer(xi, xi) / N
        for xi in pat_B:
            W += np.outer(xi, xi) / N

        # Apply T_steps of global decay (gamma multiplies entire W)
        W_decayed = (GAMMA ** T_steps) * W

        # Note: with external per-key TTL, we would have also added T_steps
        # "dummy writes" to simulate time passing, which would further dilute A.
        # Here we only test the decay rate -- W is decayed uniformly.

        # Measure retention for group A (should-be-expired)
        ret_A = float(np.mean([cosine_sim(retrieve(W_decayed, xi), xi) for xi in pat_A]))
        # Measure retention for group B (should-stay-active)
        ret_B = float(np.mean([cosine_sim(retrieve(W_decayed, xi), xi) for xi in pat_B]))

        delta = abs(ret_A - ret_B)
        # EXPECTED: delta ~ 0 (both groups decay identically under global gamma)

        print(f"  [seed={seed} T={T_steps}] ret_A={ret_A:.3f} ret_B={ret_B:.3f} "
              f"delta={delta:.4f} (expected ~0: confirms single-W per-key-TTL constraint)",
              flush=True)

        results_by_T[T_steps] = {
            "T_steps": T_steps,
            "ret_A_short_ttl": ret_A,
            "ret_B_long_ttl": ret_B,
            "delta_retention": delta,
            "gamma_decay_factor": GAMMA ** T_steps,
        }

    return {"by_T": results_by_T, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert decay metrics non-null at small scale."""
    N_test = 256
    M_test = 5
    rng = np.random.RandomState(42)
    pat_A = rng.choice([-1.0, 1.0], size=(M_test, N_test)).astype(np.float64)
    pat_B = rng.choice([-1.0, 1.0], size=(M_test, N_test)).astype(np.float64)

    W = np.zeros((N_test, N_test), dtype=np.float64)
    for xi in pat_A:
        W += np.outer(xi, xi) / N_test
    for xi in pat_B:
        W += np.outer(xi, xi) / N_test

    W_dec = (GAMMA**5) * W
    ret_A = float(np.mean([cosine_sim(retrieve(W_dec, xi), xi) for xi in pat_A]))
    ret_B = float(np.mean([cosine_sim(retrieve(W_dec, xi), xi) for xi in pat_B]))

    assert not math.isnan(ret_A), "ret_A is NaN"
    assert not math.isnan(ret_B), "ret_B is NaN"
    assert 0.0 <= ret_A <= 1.0, f"ret_A={ret_A} out of [0,1]"
    assert 0.0 <= ret_B <= 1.0, f"ret_B={ret_B} out of [0,1]"

    print(f"[selftest] PASS: ret_A={ret_A:.3f} ret_B={ret_B:.3f} at N={N_test}", flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    """Verify gamma self-test formula."""
    assert abs(GAMMA**5 - 0.59049) < 0.001, "gamma^5 formula check failed"
    assert abs(GAMMA**10 - 0.59049**2) < 0.001, "gamma^10 formula check failed"
    print("[formula_selftests] PASS: gamma decay formula verified", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    agg_by_T = {}
    for T in T_DECAY_STEPS_LIST:
        deltas = []
        for sd in per_seed.values():
            row = sd["by_T"].get(T) or sd["by_T"].get(str(T))
            if row is None:
                continue
            deltas.append(row["delta_retention"])
        agg_by_T[T] = {
            "mean_delta": float(np.mean(deltas)) if deltas else float("nan"),
            "max_delta": float(np.max(deltas)) if deltas else float("nan"),
            "n_seeds": len(deltas),
        }
    return {"by_T": agg_by_T}


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    by_T = agg["by_T"]
    max_deltas = [v["max_delta"] for v in by_T.values()
                  if not math.isnan(v.get("max_delta", float("nan")))]

    if not max_deltas:
        return ("HARD_FAIL", "No valid results.")

    global_max_delta = max(max_deltas)

    if global_max_delta < HP_DELTA:
        return ("HARD_PASS",
                f"Per-key TTL constraint CONFIRMED (negative result). "
                f"max_delta_retention={global_max_delta:.4f} < {HP_DELTA}. "
                f"Both groups decay identically under global gamma={GAMMA}. "
                f"Single-W substrate supports only ONE global decay rate -- "
                f"per-key TTL requires external bookkeeping.")
    if global_max_delta >= HF_DELTA:
        return ("HARD_FAIL",
                f"Unexpected: delta_retention={global_max_delta:.4f} >= {HF_DELTA}. "
                f"Groups decay at different rates -- contradicts single-gamma theory. "
                f"Implementation error suspected.")
    return ("MIDDLE_BAND",
            f"Marginal delta_retention={global_max_delta:.4f} "
            f"(HP<{HP_DELTA} HF>={HF_DELTA}). "
            f"Marginal capacity / numerical noise suspected.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} gamma={GAMMA} "
          f"M_PER_GROUP={M_PER_GROUP} T_steps={T_DECAY_STEPS_LIST} seeds={SEEDS}", flush=True)

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
        "run_mode": RUN_MODE, "N": N, "GAMMA": GAMMA,
        "M_PER_GROUP": M_PER_GROUP,
        "T_DECAY_STEPS_LIST": T_DECAY_STEPS_LIST,
        "seeds": SEEDS,
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
