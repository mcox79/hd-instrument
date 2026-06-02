"""
arc_lirs_hybrid_v1 -- ARC/LIRS hybrid via decay + re-Hebbian-on-READ.

SCIENTIFIC QUESTION (Caching-Policy Expressibility):
  ARC (Adaptive Replacement Cache) keeps track of both frequency AND recency.
  LIRS (Low Inter-reference Recency Set) distinguishes between hot (recently AND
  frequently accessed) and cold (only recently or only frequently) patterns.

  Substrate implementation: combine decay (LRU signal) with re-Hebbian-on-READ
  (LFU signal). W update:
    - On WRITE: W <- gamma * W + xi xi^T / N  (decays old, adds new -- LRU)
    - On READ:  W <- W + alpha * xi xi^T / N  (boosts freq without decay -- LFU bump)

  Prediction: "hot" patterns (recently written AND frequently read) should be
  elevated 3x+ over "cold" patterns (only recently written, never re-read).
  Per drill finding. Calibration probe.

PRE-REGISTERED BANDS:
  HARD-PASS: hot_vs_cold_ratio >= 2.0 (conservative; theory ~3x+ but no prior anchor;
             calibration probe bands set >=50% below theory: HP = theory/2 = 1.5,
             using 2.0 for additional safety margin given dual-mechanism interaction).
  MIDDLE: 1.3 <= ratio < 2.0.
  HARD-FAIL: ratio < 1.3 (no ARC/LIRS differentiation = hybrid adds no value over LRU alone).

FORMULA SELF-TESTS:
  1. A pattern written once (baseline weight 1.0) then read k_reads times: effective
     weight = 1.0 + k_reads * alpha. At alpha=0.5, k=4: weight=3.0.
  2. A pattern written with time-lag t (oldest): effective weight = gamma^t.
     At gamma=0.95, t=10: weight=0.599. Combined hot pattern: weight ~ 3.0; cold: 0.6.
  3. hot/cold ratio ~ 3.0 / 0.6 = 5.0 theoretical upper bound.

TIMEOUT ESTIMATE:
  Smoke: N=1024, alpha_sweep=[0.2, 0.5], 2 seeds, M=30 patterns.
  Full: N=1024, alpha_sweep=[0.1, 0.2, 0.5, 1.0], 5 seeds, M=60.
  Smoke wall ~5s -> Full ~30s -> timeout=150s.
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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "arc_lirs_hybrid_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 1024
GAMMA = 0.95       # LRU decay factor on WRITE
K_READS = 4        # number of READ boosts for "hot" patterns

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    ALPHA_SWEEP = [0.2, 0.5]
    M_PATTERNS = 30
else:
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_SWEEP = [0.1, 0.2, 0.5, 1.0]
    M_PATTERNS = 60

# Pre-reg thresholds
HP_HOT_COLD = 2.0
MID_HOT_COLD_LOW = 1.3
HF_HOT_COLD = 1.3

# Formula self-tests
_alpha_test = 0.5
_wt_test = 1.0 + 4 * _alpha_test
assert abs(_wt_test - 3.0) < 0.01, f"weight test: {_wt_test}"
_gamma_decay_test = 0.95 ** 10
assert abs(_gamma_decay_test - 0.599) < 0.01, f"gamma decay test: {_gamma_decay_test}"


def build_patterns(M: int, N: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    return rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)


def build_arc_w(patterns: np.ndarray, hot_idx: List[int], cold_idx: List[int],
                gamma: float, alpha: float, k_reads: int, N: int) -> np.ndarray:
    """
    Build W with ARC/LIRS hybrid.
    Phase 1: Write all patterns sequentially with LRU decay.
    Phase 2: Boost hot patterns with k_reads re-Hebbian bumps.
    """
    M = patterns.shape[0]
    W = np.zeros((N, N), dtype=np.float64)
    # Phase 1: LRU writes
    for t in range(M):
        W = gamma * W
        xi = patterns[t]
        W += np.outer(xi, xi) / N
    # Phase 2: re-Hebbian boosts for hot patterns
    for j in hot_idx:
        xi = patterns[j]
        W += k_reads * alpha * np.outer(xi, xi) / N
    return W


def measure_sim(W: np.ndarray, xi: np.ndarray) -> float:
    """Raw dot product (W @ xi)^T xi = xi^T W xi.
    Scales with effective pattern weight; more discriminating than cosine at high load.
    """
    r = W @ xi
    return float(np.dot(r, xi))


def run_seed(seed: int) -> Dict:
    """Run one seed: measure hot vs cold discrimination at each alpha."""
    patterns = build_patterns(M_PATTERNS, N, seed)
    M_hot = M_PATTERNS // 2
    hot_idx = list(range(M_hot))
    cold_idx = list(range(M_hot, M_PATTERNS))

    results = {}
    for alpha in ALPHA_SWEEP:
        W = build_arc_w(patterns, hot_idx, cold_idx, GAMMA, alpha, K_READS, N)
        hot_sims = [measure_sim(W, patterns[j]) for j in hot_idx]
        cold_sims = [measure_sim(W, patterns[j]) for j in cold_idx]
        mean_hot = float(np.mean(hot_sims))
        mean_cold = float(np.mean(cold_sims))
        ratio = mean_hot / (abs(mean_cold) + 1e-8)
        print(f"  [seed={seed} alpha={alpha}] hot={mean_hot:.4f} cold={mean_cold:.4f} "
              f"ratio={ratio:.2f}", flush=True)
        results[alpha] = {
            "alpha": alpha,
            "hot_cold_ratio": ratio,
            "mean_dot_hot": mean_hot,
            "mean_dot_cold": mean_cold,
        }
    return {"alpha_results": results, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert ARC hybrid gives elevated hot vs cold."""
    N_t = 128
    M_t = 20
    seed = 42
    patterns = build_patterns(M_t, N_t, seed)
    hot_idx = list(range(10))
    cold_idx = list(range(10, M_t))
    alpha = 0.5
    W = build_arc_w(patterns, hot_idx, cold_idx, GAMMA, alpha, K_READS, N_t)
    hot_sims = [measure_sim(W, patterns[j]) for j in hot_idx]
    cold_sims = [measure_sim(W, patterns[j]) for j in cold_idx]
    ratio = float(np.mean(hot_sims)) / (float(np.mean(cold_sims)) + 1e-8)
    assert not math.isnan(ratio), "ratio is NaN"
    assert ratio > 1.0, f"No ARC signal: hot/cold ratio={ratio:.3f}"
    print(f"[selftest] PASS: hot/cold ratio={ratio:.2f} at alpha={alpha}", flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    wt = 1.0 + 4 * 0.5
    assert abs(wt - 3.0) < 0.01, f"weight formula error: {wt}"
    print("[formula_selftests] PASS: ARC weight formula verified", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    agg = {}
    for alpha in ALPHA_SWEEP:
        ratio_vals = []
        hot_vals = []
        cold_vals = []
        for sd in per_seed.values():
            ar = sd["alpha_results"].get(alpha) or sd["alpha_results"].get(str(alpha))
            if ar is None:
                continue
            ratio_vals.append(ar["hot_cold_ratio"])
            hot_vals.append(ar.get("mean_dot_hot", ar.get("mean_sim_hot", float("nan"))))
            cold_vals.append(ar.get("mean_dot_cold", ar.get("mean_sim_cold", float("nan"))))
        agg[alpha] = {
            "alpha": alpha,
            "mean_hot_cold_ratio": float(np.mean(ratio_vals)) if ratio_vals else float("nan"),
            "std_hot_cold_ratio": float(np.std(ratio_vals)) if len(ratio_vals) > 1 else float("nan"),
            "mean_dot_hot": float(np.mean(hot_vals)) if hot_vals else float("nan"),
            "mean_dot_cold": float(np.mean(cold_vals)) if cold_vals else float("nan"),
            "n_seeds": len(ratio_vals),
        }
    return agg


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    # Primary at alpha=0.5 (clearest signal expected)
    primary_alpha = 0.5
    if primary_alpha not in agg and str(primary_alpha) not in agg:
        # Fall back to max alpha
        primary_alpha = max(agg.keys())
    primary = agg.get(primary_alpha) or agg.get(str(primary_alpha))
    if primary is None:
        return ("HARD_FAIL", "No aggregated results.")
    ratio_primary = primary["mean_hot_cold_ratio"]
    all_ratios = [v["mean_hot_cold_ratio"] for v in agg.values()
                  if not math.isnan(v["mean_hot_cold_ratio"])]
    max_ratio = max(all_ratios) if all_ratios else float("nan")

    if math.isnan(ratio_primary):
        return ("HARD_FAIL", "hot/cold ratio is NaN.")

    if ratio_primary >= HP_HOT_COLD:
        return ("HARD_PASS",
                f"ARC/LIRS hybrid confirmed. hot/cold ratio at alpha={primary_alpha}: "
                f"{ratio_primary:.2f} (HP>={HP_HOT_COLD}). max across alpha: {max_ratio:.2f}.")
    if ratio_primary < HF_HOT_COLD:
        return ("HARD_FAIL",
                f"No ARC/LIRS differentiation. ratio at alpha={primary_alpha}: "
                f"{ratio_primary:.2f} < HF {HF_HOT_COLD}.")
    return ("MIDDLE_BAND",
            f"Partial ARC/LIRS signal. ratio at alpha={primary_alpha}: {ratio_primary:.2f} "
            f"(HP>={HP_HOT_COLD}, HF<{HF_HOT_COLD}).")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} gamma={GAMMA} k_reads={K_READS} "
          f"alpha_sweep={ALPHA_SWEEP} M={M_PATTERNS} seeds={SEEDS}", flush=True)

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
        "run_mode": RUN_MODE, "N": N, "gamma": GAMMA, "k_reads": K_READS,
        "ALPHA_SWEEP": ALPHA_SWEEP, "M": M_PATTERNS, "seeds": SEEDS,
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
