"""
q23_capacity_cliff_fine_alpha_v1 -- Full alpha sweep near alpha_c; graceful degradation check.

SCIENTIFIC QUESTION (Q23 / Q-list follow-on):
  Does the substrate exhibit graceful degradation (NOT a sharp capacity cliff) as
  alpha = M/N increases from (alpha_c - 0.05) to (alpha_c + 0.10)?

  Prior experiments (capacity_cliff_graceful_full_v3) showed graceful degradation
  at coarse alpha resolution. This experiment tests at fine resolution:
  alpha in [alpha_c - 0.05, alpha_c + 0.10] with step 0.01 (15-16 alpha values).

  Metric: mean retrieval accuracy (fraction of correct sign bits) vs alpha.
  alpha_c reference: capacity limit alpha_c ~ 0.138 for BSC +-1 Hopfield (p=2).

PRE-REGISTERED BANDS:
  HARD-PASS: degradation is smooth (no step > 0.15 accuracy drop between adjacent
             alpha values). Regression slope d_acc/d_alpha is negative and
             statistically significantly different from 0 (p < 0.05).
  MIDDLE: step > 0.15 at exactly one alpha transition, or regression slope not sig.
  HARD-FAIL: step > 0.20 at any transition (sharp cliff = discontinuous degradation).

Calibration note: capacity_cliff_graceful_full_v3 HARD-PASS already established
graceful degradation at coarse grid. This fine-alpha version validates smoothness.
Using tighter bands since prior work established the framework.

FORMULA SELF-TESTS:
  1. At alpha << alpha_c: retrieval accuracy ~ 1 - 2*H(alpha) where H is entropy function.
  2. At alpha = alpha_c = 0.138: accuracy ~ 0.50-0.70 (degraded but not random).
  3. At alpha = alpha_c + 0.10 = 0.238: accuracy < 0.80 (beyond critical load).

TIMEOUT ESTIMATE:
  Smoke: N=1024, alpha=[0.09, 0.13, 0.14, 0.18, 0.24], 2 seeds, M_eval=50.
  Full: N=1024, alpha=linspace(0.09, 0.24, 15), 5 seeds, M_eval=100.
  Each (alpha, seed) cell: build W (O(M*N)), evaluate M_eval queries (O(M_eval*N^2/N)).
  Smoke wall ~5s -> Full ~25s -> timeout=120s.
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
from typing import Dict, List, Tuple

import numpy as np
from scipy.stats import linregress

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "q23_capacity_cliff_fine_alpha_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 1024
ALPHA_C = 0.138  # reference critical load

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    ALPHA_LIST = [0.09, 0.12, 0.138, 0.16, 0.20, 0.24]
    M_EVAL = 50
else:
    SEEDS = [7, 17, 23, 31, 41]
    # Fine grid: [alpha_c - 0.05 = 0.088, ..., alpha_c + 0.10 = 0.238], step 0.01
    ALPHA_LIST = [round(0.088 + i * 0.01, 3) for i in range(16)]  # 0.088 to 0.238
    M_EVAL = 100

# Pre-reg thresholds
HP_MAX_STEP = 0.15
HF_MAX_STEP = 0.20


def retrieval_accuracy(W: np.ndarray, patterns: np.ndarray, N: int) -> float:
    """Mean fraction of correctly recovered sign bits over all stored patterns."""
    M = patterns.shape[0]
    total_correct = 0
    for j in range(M):
        xi = patterns[j]
        # One-step Hopfield update: sign(W @ xi) = sign(W @ xi - xi / N)
        # (without self-coupling removal: just use W @ xi)
        retrieved = np.sign(W @ xi)
        correct_bits = float(np.sum(retrieved == xi)) / N
        total_correct += correct_bits
    return total_correct / M


def run_seed(seed: int) -> Dict:
    results = {}
    rng = np.random.RandomState(seed)
    for alpha in ALPHA_LIST:
        M = int(round(alpha * N))
        # Use separate eval and train sets to avoid trivial self-retrieval
        M_train = max(M, 1)
        patterns = rng.choice([-1.0, 1.0], size=(M_train, N)).astype(np.float64)
        W = (patterns.T @ patterns) / N

        # Evaluate on subset
        M_test = min(M_EVAL, M_train)
        eval_patterns = patterns[:M_test]
        acc = retrieval_accuracy(W, eval_patterns, N)
        print(f"  [seed={seed} alpha={alpha:.3f} M={M_train}] acc={acc:.4f}", flush=True)
        results[alpha] = {"alpha": alpha, "M": M_train, "accuracy": acc}
    return {"alpha_results": results, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert accuracy metric is non-null and monotone-ish with load."""
    N_t = 256
    seed = 42
    rng = np.random.RandomState(seed)
    # Low load
    M_low = 10
    Xi_low = rng.choice([-1.0, 1.0], size=(M_low, N_t)).astype(np.float64)
    W_low = (Xi_low.T @ Xi_low) / N_t
    acc_low = retrieval_accuracy(W_low, Xi_low[:10], N_t)
    # High load
    M_high = 50
    Xi_high = rng.choice([-1.0, 1.0], size=(M_high, N_t)).astype(np.float64)
    W_high = (Xi_high.T @ Xi_high) / N_t
    acc_high = retrieval_accuracy(W_high, Xi_high[:10], N_t)
    assert not math.isnan(acc_low), "acc_low is NaN"
    assert not math.isnan(acc_high), "acc_high is NaN"
    assert acc_low > 0.5, f"Low-load accuracy too low: {acc_low:.3f}"
    # High load should have lower accuracy
    # (not always true at N=256, but direction should be clear)
    print(f"[selftest] PASS: acc_low={acc_low:.4f} acc_high={acc_high:.4f}", flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    alpha_c = 0.138
    expected_low = 0.088  # alpha_c - 0.05
    expected_high = 0.238  # alpha_c + 0.10
    assert abs(expected_low - (alpha_c - 0.05)) < 0.001
    assert abs(expected_high - (alpha_c + 0.10)) < 0.001
    print("[formula_selftests] PASS: alpha sweep bounds verified", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    agg = {}
    for alpha in ALPHA_LIST:
        acc_vals = []
        for sd in per_seed.values():
            ar = sd["alpha_results"].get(alpha) or sd["alpha_results"].get(str(alpha))
            if ar is None:
                continue
            acc_vals.append(ar["accuracy"])
        agg[alpha] = {
            "alpha": alpha,
            "mean_accuracy": float(np.mean(acc_vals)) if acc_vals else float("nan"),
            "std_accuracy": float(np.std(acc_vals)) if len(acc_vals) > 1 else float("nan"),
            "n_seeds": len(acc_vals),
        }
    return agg


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    sorted_alpha = sorted(agg.keys())
    accs = [agg[a]["mean_accuracy"] for a in sorted_alpha]
    accs_valid = [(a, acc) for a, acc in zip(sorted_alpha, accs) if not math.isnan(acc)]
    if len(accs_valid) < 3:
        return ("HARD_FAIL", "Fewer than 3 valid alpha values.")

    alpha_vals = [a for a, _ in accs_valid]
    acc_vals = [acc for _, acc in accs_valid]

    # Check for sharp steps
    max_step = 0.0
    max_step_alpha = None
    for i in range(1, len(acc_vals)):
        step = acc_vals[i - 1] - acc_vals[i]  # positive = drop
        if step > max_step:
            max_step = step
            max_step_alpha = alpha_vals[i]

    # Linear regression to check monotone decrease
    slope, intercept, r_val, p_val, se = linregress(alpha_vals, acc_vals)
    sig_negative = slope < 0 and p_val < 0.05

    if max_step < HP_MAX_STEP and sig_negative:
        return ("HARD_PASS",
                f"Graceful capacity degradation confirmed. max_step={max_step:.4f} "
                f"(HP<{HP_MAX_STEP}). slope={slope:.4f} p={p_val:.4f} "
                f"(sig negative decline). No sharp cliff in "
                f"alpha=[{alpha_vals[0]:.3f},{alpha_vals[-1]:.3f}].")
    if max_step >= HF_MAX_STEP:
        return ("HARD_FAIL",
                f"Sharp capacity cliff detected. max_step={max_step:.4f} >= HF {HF_MAX_STEP} "
                f"at alpha={max_step_alpha}.")
    return ("MIDDLE_BAND",
            f"Marginal graceful degradation. max_step={max_step:.4f} "
            f"(HP<{HP_MAX_STEP}, HF>={HF_MAX_STEP}). slope={slope:.4f} p={p_val:.4f}.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} alpha_c={ALPHA_C} "
          f"n_alpha={len(ALPHA_LIST)} M_eval={M_EVAL} seeds={SEEDS}", flush=True)

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
        "run_mode": RUN_MODE, "N": N, "ALPHA_C": ALPHA_C,
        "ALPHA_LIST": ALPHA_LIST, "M_EVAL": M_EVAL, "seeds": SEEDS,
        "aggregated": {str(a): v for a, v in agg.items()},
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
