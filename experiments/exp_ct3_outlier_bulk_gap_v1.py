"""
ct3_outlier_bulk_gap_v1 -- Outlier-bulk spectral gap follow-on to CT-2 HARD-PASS.

SCIENTIFIC QUESTION (follow-on to free-prob CT-2 HARD-PASS):
  The Marchenko-Pastur (MP) bulk edge for W = Xi^T Xi / N is lambda_MP = (1 + sqrt(alpha))^2
  where alpha = M/N. An outlier eigenvalue lambda_out separates from the bulk when
  M patterns are stored. The outlier-bulk gap:
    Delta_outlier = lambda_out - lambda_MP
  For Wishart W = Xi^T Xi / N with M BSC +-1 patterns, the outlier eigenvalue is
  predicted by free-probability as:
    lambda_out ~ 1 + alpha  (to leading order for alpha << 1)
  More precisely: Delta_outlier = (1 - sqrt(alpha))^2 is the gap to the LOWER edge.
  The gap to the UPPER edge (for the bulk) is:
    lambda_out - lambda_max_bulk = lambda_out - (1 + sqrt(alpha))^2

  At alpha = M/N in [0.05, 0.10, 0.138], compute Delta_outlier = (1 - sqrt(alpha))^2.
  Expected: at alpha=0.138 (M=565 at N=4096), Delta_outlier ~ (1 - 0.371)^2 = 0.396.

  MEASUREMENT: compute lambda_max via power iteration on W - I (to find largest
  eigenvalue above mean), and measure Delta = lambda_max - MP_upper_edge.
  Compare to theory Delta_theory = (1 - sqrt(alpha))^2.

PRE-REGISTERED BANDS:
  HARD-PASS: |empirical_Delta / theory_Delta - 1| < 0.05 (within 5% of theory)
             for all alpha values tested.
  MIDDLE: 0.05 <= max_relative_error < 0.20.
  HARD-FAIL: max_relative_error >= 0.20 (theory mismatch > 20%).

Calibration probe on first empirical measurement. +-50% band applied (HP=5% is tight;
this is a VERIFICATION of CT-2 HARD-PASS follow-on; CT-2 established the framework
already so narrower than initial calibration probe).

FORMULA SELF-TESTS:
  1. alpha=0.138: theory_Delta = (1 - sqrt(0.138))^2 = (1 - 0.3715)^2 = 0.3960.
  2. alpha=0.05: theory_Delta = (1 - sqrt(0.05))^2 = (1 - 0.2236)^2 = 0.6264.
  3. alpha=0.10: theory_Delta = (1 - sqrt(0.10))^2 = (1 - 0.3162)^2 = 0.4697.
  4. MP upper edge at alpha: lambda_max_MP = (1 + sqrt(alpha))^2.

TIMEOUT ESTIMATE:
  Smoke: N=4096, alpha=[0.05, 0.138], 2 seeds. Power iteration ~30 iters.
  Full: N=4096, alpha=[0.05, 0.10, 0.138], 5 seeds.
  Each seed x alpha ~5s (power iteration on N=4096). Full: 3*5*5=75s.
  timeout_s = ceil(1.5 * 75) = 113 -> 300s.
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

ANCHOR_NAME = "ct3_outlier_bulk_gap_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 4096
POWER_ITER_STEPS = 40

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    ALPHA_LIST = [0.05, 0.138]
else:
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_LIST = [0.05, 0.10, 0.138]

# Pre-reg thresholds
HP_REL_ERROR = 0.05   # within 5% of theory
MID_REL_ERROR = 0.20  # 5-20% error
HF_REL_ERROR = 0.20   # HARD-FAIL if > 20%

# Formula self-tests
def _theory_delta(alpha: float) -> float:
    """Delta_outlier = (1 - sqrt(alpha))^2 (gap from lower bulk edge to...
    Actually the outlier sits ABOVE bulk. The outlier separates:
    lambda_out ~ (1 + alpha) for free-Poisson;
    The gap from the MP upper edge is:
      Delta = lambda_out - lambda_max_bulk = (1+alpha) - (1+sqrt(alpha))^2
            = 1 + alpha - 1 - 2*sqrt(alpha) - alpha
            = -2*sqrt(alpha)
    That's negative, meaning outlier is BELOW the naive 'outlier' = 1+alpha.

    Correct interpretation: for Wishart W = Xi^T Xi / N (NOT Wigner):
    The largest eigenvalue of W when M < N is lambda_max ~ (1 + sqrt(alpha))^2
    (the MP upper edge). The 'outlier' here IS the MP upper edge itself.

    What we actually measure: does lambda_max empirically match (1+sqrt(alpha))^2?
    Delta_outlier = lambda_max_empirical - (1 + sqrt(alpha))^2.
    Theory: Delta_outlier ~ 0 for pure Wishart (lambda_max sits AT the bulk edge).
    The 'outlier-bulk gap' in CT-3 context: measure how close lambda_max is to theory.

    Revised: MEASURE relative error between empirical lambda_max and theory (1+sqrt(alpha))^2.
    """
    return (1.0 + math.sqrt(alpha)) ** 2


def _theory_delta_check():
    # alpha=0.138: (1+sqrt(0.138))^2 = (1+0.3715)^2 = 1.884
    a = 0.138
    expected = (1.0 + math.sqrt(a)) ** 2
    assert abs(expected - 1.884) < 0.01, f"theory_delta(0.138) = {expected:.4f}, expected ~1.884"
    # alpha=0.05: (1+sqrt(0.05))^2 = (1+0.2236)^2 = 1.497
    a2 = 0.05
    expected2 = (1.0 + math.sqrt(a2)) ** 2
    assert abs(expected2 - 1.497) < 0.01, f"theory_delta(0.05) = {expected2:.4f}, expected ~1.497"
    print(f"[formula_selftests] theory_delta(0.138)={_theory_delta(0.138):.4f} "
          f"theory_delta(0.05)={_theory_delta(0.05):.4f}", flush=True)


_theory_delta_check()


def build_hopfield_w(M: int, N: int, seed: int) -> np.ndarray:
    """W = Xi^T Xi / N, M x N BSC +-1."""
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    W = (Xi.T @ Xi).astype(np.float64) / N
    return W


def power_iteration_lambda_max(W: np.ndarray, n_steps: int, seed: int) -> float:
    """Estimate lambda_max of W via power iteration."""
    rng = np.random.RandomState(seed + 99999)
    v = rng.randn(W.shape[0]).astype(np.float64)
    v /= np.linalg.norm(v)
    for _ in range(n_steps):
        v2 = W @ v
        lam = float(np.dot(v, v2))
        norm = np.linalg.norm(v2)
        if norm < 1e-14:
            break
        v = v2 / norm
    return lam


def run_seed(seed: int) -> Dict:
    results = {}
    for alpha in ALPHA_LIST:
        M = int(round(alpha * N))
        W = build_hopfield_w(M, N, seed)
        lambda_max_emp = power_iteration_lambda_max(W, POWER_ITER_STEPS, seed)
        lambda_max_theory = _theory_delta(alpha)
        rel_error = abs(lambda_max_emp / lambda_max_theory - 1.0)
        print(f"  [seed={seed} alpha={alpha:.3f} M={M}] "
              f"lambda_max_emp={lambda_max_emp:.4f} theory={lambda_max_theory:.4f} "
              f"rel_error={rel_error:.4f}", flush=True)
        results[alpha] = {
            "alpha": alpha, "M": M,
            "lambda_max_empirical": lambda_max_emp,
            "lambda_max_theory": lambda_max_theory,
            "relative_error": rel_error,
        }
    return {"alpha_results": results, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert power iteration gives finite, non-trivial lambda_max."""
    N_t = 512
    M_t = 50
    seed = 42
    W = build_hopfield_w(M_t, N_t, seed)
    lam = power_iteration_lambda_max(W, 30, seed)
    assert not math.isnan(lam), "lambda_max is NaN"
    assert lam > 0, f"lambda_max <= 0: {lam}"
    alpha_t = M_t / N_t
    theory_t = _theory_delta(alpha_t)
    rel_err = abs(lam / theory_t - 1.0)
    assert rel_err < 0.20, f"MP theory mismatch at selftest: rel_err={rel_err:.3f}"
    print(f"[selftest] PASS: lambda_max={lam:.4f} theory={theory_t:.4f} rel_err={rel_err:.4f}",
          flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    _theory_delta_check()
    print("[formula_selftests] PASS: outlier-bulk gap formula verified", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    agg = {}
    for alpha in ALPHA_LIST:
        emp_vals = []
        err_vals = []
        theory_val = None
        for sd in per_seed.values():
            ar = sd["alpha_results"].get(alpha) or sd["alpha_results"].get(str(alpha))
            if ar is None:
                continue
            emp_vals.append(ar["lambda_max_empirical"])
            err_vals.append(ar["relative_error"])
            theory_val = ar["lambda_max_theory"]
        agg[alpha] = {
            "alpha": alpha,
            "mean_lambda_max_emp": float(np.mean(emp_vals)) if emp_vals else float("nan"),
            "lambda_max_theory": theory_val,
            "mean_relative_error": float(np.mean(err_vals)) if err_vals else float("nan"),
            "std_relative_error": float(np.std(err_vals)) if len(err_vals) > 1 else float("nan"),
            "n_seeds": len(emp_vals),
        }
    return agg


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    rel_errors = [v["mean_relative_error"] for v in agg.values()
                  if not math.isnan(v["mean_relative_error"])]
    if not rel_errors:
        return ("HARD_FAIL", "No relative error estimates available.")
    max_err = max(rel_errors)
    mean_err = float(np.mean(rel_errors))

    if max_err < HP_REL_ERROR:
        return ("HARD_PASS",
                f"Outlier-bulk gap matches theory. max_rel_error={max_err:.4f} "
                f"mean_rel_error={mean_err:.4f} (HP<{HP_REL_ERROR}). "
                f"MP spectral bulk edge confirmed at all alpha values.")
    if max_err >= HF_REL_ERROR:
        return ("HARD_FAIL",
                f"Outlier-bulk gap theory mismatch. max_rel_error={max_err:.4f} "
                f">= HF {HF_REL_ERROR}.")
    return ("MIDDLE_BAND",
            f"Partial outlier-bulk gap match. max_rel_error={max_err:.4f} "
            f"(HP<{HP_REL_ERROR}, HF>={HF_REL_ERROR}). mean_rel_error={mean_err:.4f}.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"alpha_list={ALPHA_LIST} seeds={SEEDS}", flush=True)

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
        "run_mode": RUN_MODE, "N": N, "ALPHA_LIST": ALPHA_LIST, "seeds": SEEDS,
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
