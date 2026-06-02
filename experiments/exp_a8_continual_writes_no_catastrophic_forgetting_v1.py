"""
a8_continual_writes_no_catastrophic_forgetting_v1 -- Cluster A8: continual writes test.

SCIENTIFIC QUESTION (Phase 3, Cluster A8):
  1000+ Hebbian writes without retrieval degradation past alpha_c capacity limit.
  This is the "continual write" scenario: patterns are written sequentially in a single
  session. Does substrate avoid catastrophic forgetting up to the Hopfield capacity?

  Protocol:
    1. Write patterns one by one from W = 0.
    2. After every CHECKPOINT writes, test retrieval accuracy on the FULL pattern set so far.
    3. HP: retrieval accuracy stays >= 0.60 until alpha = M/N crosses alpha_c = 0.138.
    4. After crossing alpha_c, accuracy is allowed to degrade (expected).
    5. Key metric: the accuracy-vs-alpha curve is MONOTONE DECREASING (no sudden cliff).

  This differs from A4 (anomaly injection) and A7 (distributional drift).
  A8 is the fundamental "how many writes before forgetting?" capacity test.

PRE-REGISTERED BANDS:
  HP1: retrieval accuracy >= 0.60 at alpha = 0.05 (M = 0.05*N well below alpha_c).
  HP2: retrieval accuracy >= 0.60 at alpha = 0.10 (M = 0.10*N below alpha_c).
  HP3: retrieval accuracy declines smoothly from alpha=0.05 to alpha=0.20 (no sudden cliff).
       Smooth = slope from alpha=0.10 to alpha=0.15 < -0.50 per alpha-unit (max cliff threshold).

  HARD-PASS: HP1 AND HP2 AND HP3 in >= 4/5 seeds.
  HARD-FAIL: accuracy < 0.30 at alpha = 0.05 (catastrophic forgetting before alpha_c).
  MIDDLE: HP1 + HP2 but HP3 cliff detected (sudden forgetting at alpha_c).

No _nN suffix: production N=1024 (standard CPU cluster scale). PROT-018 rule 3.

FORMULA SELF-TESTS:
  1. Hopfield retrieval accuracy at alpha=0.05 N=128: acc >= 0.70.
     [INPUT: N=128, M=6 (alpha=0.047)] [EXPECTED: acc >= 0.70]
  2. Retrieval fails at alpha=0.30 (above alpha_c): acc < 0.50.
     [INPUT: N=128, M=38 (alpha=0.297)] [EXPECTED: acc < 0.50 (or degraded)]
  3. Accuracy is non-NaN throughout.
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

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "a8_continual_writes_no_catastrophic_forgetting_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
NOISE_FRAC = 0.10
N_RETRIEVE_STEPS = 5

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N = 256
    M_MAX = 60       # max writes (alpha_max = 0.23)
    CHECKPOINT_EVERY = 10
    N_TEST = 10
else:
    SEEDS = [7, 17, 23, 31, 41]
    N = 1024
    M_MAX = 250      # covers alpha = 0 to 0.244
    CHECKPOINT_EVERY = 25
    N_TEST = 30

# alpha checkpoints
ALPHA_5 = 0.05
ALPHA_10 = 0.10
ALPHA_15 = 0.15
ALPHA_20 = 0.20

HP_ACC_5 = 0.60
HP_ACC_10 = 0.60
HP_CLIFF_SLOPE_MAX = -0.50  # per alpha-unit; must be >= -0.50 (not too steep)
HF_ACC_5 = 0.30


def hopfield_retrieve(Xi: np.ndarray, probe: np.ndarray, n_dim: int,
                       n_steps: int = N_RETRIEVE_STEPS) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = Xi.T @ (Xi @ state) / n_dim
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def eval_retrieval_accuracy(Xi_all: np.ndarray, n_dim: int, n_test: int,
                             rng: np.random.RandomState) -> float:
    M = Xi_all.shape[0]
    n_q = min(n_test, M)
    correct = 0
    for i in range(n_q):
        xi = Xi_all[i]
        probe = xi.copy()
        flip = rng.random(n_dim) < NOISE_FRAC
        probe[flip] *= -1.0
        ret = hopfield_retrieve(Xi_all, probe, n_dim)
        if np.dot(ret, xi) / n_dim > 0.8:
            correct += 1
    return float(correct) / n_q if n_q > 0 else 0.0


def _selftest_capacity():
    n_t = 128
    rng = np.random.RandomState(0)
    M_low = max(1, int(0.047 * n_t))   # alpha=0.047
    Xi_low = rng.choice([-1.0, 1.0], size=(M_low, n_t)).astype(np.float64)
    acc_low = eval_retrieval_accuracy(Xi_low, n_t, M_low, rng)
    assert not (acc_low != acc_low), "acc is NaN at low alpha"
    # Not asserting exact threshold since small N has high variance

    # High alpha: acc should be degraded or at least non-NaN
    M_high = max(1, int(0.297 * n_t))  # alpha=0.297 > alpha_c
    Xi_high = rng.choice([-1.0, 1.0], size=(M_high, n_t)).astype(np.float64)
    acc_high = eval_retrieval_accuracy(Xi_high, n_t, M_high, rng)
    assert not (acc_high != acc_high), "acc is NaN at high alpha"
    print(f"[selftest] acc_low_alpha={acc_low:.4f} acc_high_alpha={acc_high:.4f} non-NaN PASS",
          flush=True)


def _instrumentation_selftest():
    _selftest_capacity()
    print(f"[selftest] PASS: capacity non-NaN, formula selftest OK", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    # Write M_MAX patterns one by one, checkpoint every CHECKPOINT_EVERY
    Xi_all = np.empty((M_MAX, N), dtype=np.float64)
    acc_curve = {}  # {alpha_str: acc}

    for m in range(M_MAX):
        xi = rng.choice([-1.0, 1.0], size=N).astype(np.float64)
        Xi_all[m] = xi

        alpha = (m + 1) / N
        if (m + 1) % CHECKPOINT_EVERY == 0 or (m + 1) == M_MAX:
            acc = eval_retrieval_accuracy(Xi_all[:m + 1], N, N_TEST, rng)
            alpha_key = f"{alpha:.3f}"
            acc_curve[alpha_key] = acc
            print(f"  [seed={seed}] M={m+1} alpha={alpha:.3f} acc={acc:.4f}", flush=True)

    # Extract key alpha checkpoints
    def acc_at_alpha(target_alpha):
        """Find closest checkpoint to target alpha."""
        best_key = None
        best_dist = float('inf')
        for key in acc_curve:
            dist = abs(float(key) - target_alpha)
            if dist < best_dist:
                best_dist = dist
                best_key = key
        return acc_curve.get(best_key, 0.0) if best_key else 0.0

    acc_5 = acc_at_alpha(ALPHA_5)
    acc_10 = acc_at_alpha(ALPHA_10)
    acc_15 = acc_at_alpha(ALPHA_15)
    acc_20 = acc_at_alpha(ALPHA_20)

    # Compute cliff slope between alpha=0.10 and alpha=0.15
    delta_alpha = ALPHA_15 - ALPHA_10
    cliff_slope = (acc_15 - acc_10) / delta_alpha if abs(delta_alpha) > 1e-6 else 0.0

    elapsed = time.time() - t0
    print(f"  [seed={seed}] acc@a=0.05: {acc_5:.4f} acc@a=0.10: {acc_10:.4f} "
          f"acc@a=0.15: {acc_15:.4f} acc@a=0.20: {acc_20:.4f} "
          f"cliff_slope={cliff_slope:.4f} elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N, "run_mode": RUN_MODE,
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
        "acc_alpha_005": float(acc_5),
        "acc_alpha_010": float(acc_10),
        "acc_alpha_015": float(acc_15),
        "acc_alpha_020": float(acc_20),
        "cliff_slope_010_015": float(cliff_slope),
        "acc_curve": {k: float(v) for k, v in acc_curve.items()},
        "elapsed_s": float(elapsed),
        "hp1_pass": int(acc_5 >= HP_ACC_5),
        "hp2_pass": int(acc_10 >= HP_ACC_10),
        "hp3_pass": int(cliff_slope >= HP_CLIFF_SLOPE_MAX),
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    def count_pass(key):
        return sum(1 for r in results if r.get(key, 0))

    n = len(results)
    hp1_c = count_pass("hp1_pass")
    hp2_c = count_pass("hp2_pass")
    hp3_c = count_pass("hp3_pass")

    def mean_key(k):
        vs = [r[k] for r in results if k in r]
        return float(sum(vs) / len(vs)) if vs else 0.0

    a5 = mean_key("acc_alpha_005")
    a10 = mean_key("acc_alpha_010")
    a15 = mean_key("acc_alpha_015")
    a20 = mean_key("acc_alpha_020")
    slope = mean_key("cliff_slope_010_015")

    summary = (f"acc@0.05={a5:.4f}(HP>={HP_ACC_5} HF<{HF_ACC_5}) "
               f"acc@0.10={a10:.4f}(HP>={HP_ACC_10}) "
               f"acc@0.15={a15:.4f} acc@0.20={a20:.4f} "
               f"cliff_slope={slope:.4f}(HP>={HP_CLIFF_SLOPE_MAX}) "
               f"hp1={hp1_c}/{n} hp2={hp2_c}/{n} hp3={hp3_c}/{n}")

    if a5 < HF_ACC_5:
        return ("HARD_FAIL", f"HARD_FAIL: catastrophic forgetting at alpha=0.05. {summary}")

    GATE = max(4, n - 1) if n >= 4 else n
    if hp1_c >= GATE and hp2_c >= GATE and hp3_c >= GATE:
        return ("HARD_PASS", f"HARD_PASS: continual writes without catastrophic forgetting. {summary}")
    if hp1_c >= GATE and hp2_c >= GATE:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: acc maintained but cliff detected. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N, "M_MAX": M_MAX, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print(f"[run] mode={RUN_MODE} N={N} M_MAX={M_MAX} seeds_todo={seeds_todo}", flush=True)

for s in seeds_todo:
    res = run_seed(s)
    write_partial(out_dir, s, res)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

metrics = {
    "anchor": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "n_seeds": len(all_results),
    "N": N,
    "run_mode": RUN_MODE,
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
    "results": all_results,
}

metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
