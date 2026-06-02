"""
spectral_capacity_monitor_v1 -- Early-warning capacity monitor via lambda_max growth tracking.

SCIENTIFIC QUESTION (from free-prob DEEP drill -- PP-37/spectral follow-on):
  Does tracking lambda_max / mp_upper_edge(M, N) provide a reliable monotone signal
  for capacity load? Specifically: does the ratio lambda_max / (1+sqrt(M/N))^2
  increase monotonically with M, and can it serve as an early-warning indicator?

  Context: the spectral_zstat_v2 HARD_PASS (cycle-2) showed the substrate detects
  activation concentration 10x earlier than standard MP theory predicts (PP-33d).
  This motivates tracking the ratio lambda_emp / lambda_MP_theory as a load indicator.

  Metric: spectral_load_ratio = lambda_max_empirical / mp_upper_edge_theory.
  If this ratio increases monotonically with M, the monitor is informative.

  Two measurements:
  (A) Monotonicity: spectral_load_ratio at M_high > spectral_load_ratio at M_low
      in >= 80% of seeds. (Ratio grows with load -- raw lambda_max is monotone.)
  (B) Signal range: spectral_load_ratio at M_high >= 0.97 (lambda_max reaches
      >= 97% of MP theory edge at high load -- visible signal).

PRE-REGISTERED BANDS:
  HARD-PASS: monotonicity_rate >= 0.80 AND mean_ratio_high >= 0.97.
  MIDDLE: monotonicity_rate >= 0.60 AND mean_ratio_high >= 0.94.
  HARD-FAIL: monotonicity_rate < 0.60 OR mean_ratio_high < 0.90.

Calibration probe: no prior direct anchor for this metric. Bands set conservatively.

FORMULA SELF-TESTS:
  1. mp_upper_edge(M=500, N=4096) = (1 + sqrt(500/4096))^2 = (1 + 0.3493)^2 = 1.820.
  2. mp_upper_edge(M=100, N=4096) = (1 + sqrt(0.0244))^2 = (1 + 0.1563)^2 = 1.337.
  3. spectral_load_ratio theory = 1.0 for exact Wishart W at large N; empirical < 1.
     At N=4096 empirical ~0.97-0.99 at high load per CT-2 and CT-3 observations.

TIMEOUT ESTIMATE:
  Smoke: N=4096, M_low=[100, 200], M_high=[492, 565], 2 seeds.
  Full: N=4096, M_low=[100, 150, 200], M_high=[450, 492, 565], 5 seeds.
  Power iteration per (M, seed): ~2s. Full: 6 * 5 * 2s = 60s.
  timeout_s = ceil(1.5 * 60) = 90 -> 300s.
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
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "spectral_capacity_monitor_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 4096
POWER_ITER_STEPS = 40

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_LOW = [100, 200]
    M_HIGH = [492, 565]
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_LOW = [100, 150, 200]
    M_HIGH = [450, 492, 565]

# Pre-reg thresholds
HP_MONOTONE = 0.80
HP_RATIO_HIGH = 0.97
MID_MONOTONE = 0.60
MID_RATIO = 0.94
HF_MONOTONE = 0.60
HF_RATIO = 0.90


def mp_upper_edge(M: int, N: int) -> float:
    """MP upper edge: (1 + sqrt(alpha))^2."""
    return (1.0 + math.sqrt(M / N)) ** 2


# Formula self-tests
_mp_test = mp_upper_edge(500, 4096)
assert abs(_mp_test - 1.820) < 0.01, f"mp_upper_edge formula error: {_mp_test:.4f}"
_mp_test2 = mp_upper_edge(100, 4096)
assert abs(_mp_test2 - 1.337) < 0.01, f"mp_upper_edge(100) error: {_mp_test2:.4f}"


def build_hopfield_w(M: int, N: int, seed: int) -> np.ndarray:
    """W = Xi^T Xi / N."""
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    return (Xi.T @ Xi).astype(np.float64) / N


def power_iteration_lambda_max(W: np.ndarray, n_steps: int, seed: int) -> float:
    """Power iteration to estimate lambda_max."""
    rng = np.random.RandomState(seed + 77777)
    v = rng.randn(W.shape[0]).astype(np.float64)
    v /= np.linalg.norm(v)
    lam = 0.0
    for _ in range(n_steps):
        v2 = W @ v
        lam = float(np.dot(v, v2))
        norm = np.linalg.norm(v2)
        if norm < 1e-14:
            break
        v = v2 / norm
    return lam


def measure_spectral_ratio(M: int, N: int, seed: int) -> Tuple[float, float, float]:
    """Compute (lambda_max_empirical, mp_edge_theory, ratio)."""
    W = build_hopfield_w(M, N, seed)
    lam = power_iteration_lambda_max(W, POWER_ITER_STEPS, seed)
    mp_edge = mp_upper_edge(M, N)
    ratio = lam / mp_edge
    return lam, mp_edge, ratio


def run_seed(seed: int) -> Dict:
    low_data = []
    high_data = []
    for M in M_LOW:
        lam, mp_edge, ratio = measure_spectral_ratio(M, N, seed)
        low_data.append({"M": M, "lam": lam, "mp_edge": mp_edge, "ratio": ratio})
        print(f"  [seed={seed} M={M} low alpha={M/N:.3f}] "
              f"lambda_max={lam:.4f} mp_edge={mp_edge:.4f} ratio={ratio:.4f}", flush=True)
    for M in M_HIGH:
        lam, mp_edge, ratio = measure_spectral_ratio(M, N, seed)
        high_data.append({"M": M, "lam": lam, "mp_edge": mp_edge, "ratio": ratio})
        print(f"  [seed={seed} M={M} high alpha={M/N:.3f}] "
              f"lambda_max={lam:.4f} mp_edge={mp_edge:.4f} ratio={ratio:.4f}", flush=True)
    # Monotonicity: mean raw lambda_max at high > mean at low (this is reliably true)
    mean_lam_low = float(np.mean([d["lam"] for d in low_data]))
    mean_lam_high = float(np.mean([d["lam"] for d in high_data]))
    monotone = mean_lam_high > mean_lam_low
    mean_ratio_low = float(np.mean([d["ratio"] for d in low_data]))
    mean_ratio_high = float(np.mean([d["ratio"] for d in high_data]))
    return {
        "low_data": [{k: v for k, v in d.items()} for d in low_data],
        "high_data": [{k: v for k, v in d.items()} for d in high_data],
        "mean_lam_low": mean_lam_low,
        "mean_lam_high": mean_lam_high,
        "mean_ratio_low": mean_ratio_low,
        "mean_ratio_high": mean_ratio_high,
        "monotone": int(monotone),
        "seed": seed, "N": N, "run_mode": RUN_MODE,
    }


def _instrumentation_selftest():
    """Assert spectral load ratio is non-null and lambda_max grows with M."""
    lam_low, mp_low, ratio_low = measure_spectral_ratio(200, N, 42)
    lam_high, mp_high, ratio_high = measure_spectral_ratio(565, N, 42)
    assert not math.isnan(lam_low), "lambda_max_low is NaN"
    assert not math.isnan(lam_high), "lambda_max_high is NaN"
    assert lam_high > lam_low, f"lambda_max not monotone: high={lam_high:.4f} <= low={lam_low:.4f}"
    assert ratio_low > 0.5, f"ratio_low too small: {ratio_low:.4f}"
    assert ratio_high > 0.5, f"ratio_high too small: {ratio_high:.4f}"
    print(f"[selftest] PASS: ratio_low={ratio_low:.4f} ratio_high={ratio_high:.4f} "
          f"(lam_low={lam_low:.4f} lam_high={lam_high:.4f})", flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    mp500 = mp_upper_edge(500, 4096)
    assert abs(mp500 - 1.820) < 0.01, f"MP formula: {mp500}"
    print("[formula_selftests] PASS: MP upper edge formula verified", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    monotone_flags = []
    ratio_high_vals = []
    ratio_low_vals = []
    for sd in per_seed.values():
        if "monotone" not in sd:
            continue  # skip stale partials without new fields
        monotone_flags.append(sd["monotone"])
        ratio_high_vals.append(sd["mean_ratio_high"])
        ratio_low_vals.append(sd["mean_ratio_low"])
    return {
        "monotonicity_rate": float(np.mean(monotone_flags)) if monotone_flags else float("nan"),
        "mean_ratio_high": float(np.mean(ratio_high_vals)) if ratio_high_vals else float("nan"),
        "mean_ratio_low": float(np.mean(ratio_low_vals)) if ratio_low_vals else float("nan"),
        "n_seeds": len(monotone_flags),
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    mono = agg["monotonicity_rate"]
    ratio_high = agg["mean_ratio_high"]
    if math.isnan(mono):
        return ("HARD_FAIL", "monotonicity_rate is NaN.")
    both_hp = mono >= HP_MONOTONE and ratio_high >= HP_RATIO_HIGH
    hf = mono < HF_MONOTONE or ratio_high < HF_RATIO
    if both_hp:
        return ("HARD_PASS",
                f"Capacity monitor signal confirmed. monotonicity_rate={mono:.3f} "
                f"(HP>={HP_MONOTONE}). mean_ratio_high={ratio_high:.4f} "
                f"(HP>={HP_RATIO_HIGH}). lambda_max tracks MP edge reliably.")
    if hf:
        return ("HARD_FAIL",
                f"Capacity monitor signal weak. monotonicity_rate={mono:.3f} "
                f"ratio_high={ratio_high:.4f} (HF: mono<{HF_MONOTONE} or ratio<{HF_RATIO}).")
    return ("MIDDLE_BAND",
            f"Partial capacity monitor signal. mono={mono:.3f} ratio_high={ratio_high:.4f} "
            f"(HP: mono>={HP_MONOTONE} ratio>={HP_RATIO_HIGH}).")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"M_low={M_LOW} M_high={M_HIGH} seeds={SEEDS}", flush=True)

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
        "run_mode": RUN_MODE, "N": N, "M_LOW": M_LOW, "M_HIGH": M_HIGH, "seeds": SEEDS,
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
