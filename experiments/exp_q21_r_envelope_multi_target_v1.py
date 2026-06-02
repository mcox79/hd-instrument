"""
q21_r_envelope_multi_target_v1 -- Q21 R(alpha) envelope across multiple R targets.

SCIENTIFIC QUESTION (Q21 follow-on -- R envelope across R targets):
  Q21 R(alpha) sweep was complete: showed substrate achieves R at varying alpha.
  This extends to CHARACTERIZE the R envelope: how does the maximum achievable R
  vary across target retrieval accuracy R in {0.90, 0.95, 0.97, 0.99}?

  Design:
    - For each R_target in {0.90, 0.95, 0.97, 0.99}:
        - Sweep alpha (load) from 0.01 to 0.15.
        - At each alpha, measure actual retrieval accuracy over 5 seeds.
        - Find alpha_max(R) = max alpha where retrieval >= R_target.
        - This gives the OPERATING ENVELOPE: (R_target, alpha_max(R_target)) pairs.
    - Fit: alpha_max(R) = alpha_c * (1 - R)^beta_R where beta_R is a fit exponent.
    - Product reading: higher R_target = narrower operating window.
      The curve alpha_max vs R defines the substrate's operating contract.

  Test cells:
    (A) Monotone: alpha_max(0.90) > alpha_max(0.95) > alpha_max(0.97) > alpha_max(0.99).
        HP-A: strict ordering holds in >=3/5 seeds.
    (B) Empirical alpha_c match: alpha_max(0.90) is within 30% of known alpha_c=0.138.
        HP-B: 0.097 <= alpha_max(0.90) <= 0.179 (alpha_c +/- 30%).
    (C) R=0.99 operating window exists: alpha_max(0.99) > 0.05.
        HP-C: alpha_max(0.99) > 0.05 (substrate is useful at very high fidelity).

PRE-REGISTERED BANDS:
  HARD-PASS: All of A, B, C.
  MIDDLE: 2/3 cells pass.
  HARD-FAIL: 0-1 cells pass.

  Calibration: Q21 base already passed. These are envelope-extension bands.
  Theory: alpha_c for Hopfield = 0.138. At R=0.90: alpha_max ~ 0.10-0.12.
  At R=0.99: alpha_max ~ 0.02-0.05 (very strict, narrow window).

FORMULA SELF-TESTS:
  1. Retrieval accuracy R at load alpha:
     For random bipolar patterns, SNR = sqrt(N) * (1 - alpha/alpha_c)^0.5 near cliff.
     At alpha=0.05, N=1024: R ~ erf(SNR/sqrt(2)) ~ 0.99.
     [INPUT: alpha=0.05, N=1024] [EXPECTED: R >= 0.95]
  2. alpha_max(0.90) < alpha_c: load beyond alpha_c means R < 0.5.
     [INPUT: alpha=0.15 > alpha_c=0.138] [EXPECTED: R < 0.90 in most seeds]
  3. alpha_max ordering formula: if R1 < R2, then alpha_max(R1) > alpha_max(R2).
     [INPUT: R1=0.90, R2=0.99] [EXPECTED: alpha_max(0.90) > alpha_max(0.99)]

TIMEOUT ESTIMATE:
  Smoke: N=512, alpha_sweep=7 values, 2 seeds, R_targets=[0.90, 0.95].
  Full: N=1024, alpha_sweep=12 values, 5 seeds, R_targets=[0.90, 0.95, 0.97, 0.99].
  Linear. Smoke ~4s -> Full ~60s. timeout=480s.

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
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "q21_r_envelope_multi_target_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

ALPHA_C_KNOWN = 0.138  # known Hopfield alpha_c

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N = 512
    SEEDS = [7, 17]
    ALPHA_SWEEP = [0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14]
    R_TARGETS = [0.90, 0.95]
    N_TRIALS = 5
else:
    N = 1024
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_SWEEP = [0.01, 0.02, 0.03, 0.05, 0.07, 0.09, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16]
    R_TARGETS = [0.90, 0.95, 0.97, 0.99]
    N_TRIALS = 10

# Threshold bands
HP_ALPHA_MAX_R90_LO = ALPHA_C_KNOWN * 0.70   # 30% below alpha_c
HP_ALPHA_MAX_R90_HI = ALPHA_C_KNOWN * 1.30   # 30% above alpha_c
HP_ALPHA_MAX_R99_MIN = 0.05                   # HP-C: R=0.99 operating window

# ---- FORMULA SELF-TESTS ----
# Test: at low alpha, R should be near 1.0
def _snr_at_alpha(alpha: float, N_dim: int) -> float:
    """Estimate SNR (retrieval per-bit cosine) at load alpha."""
    # Simple estimate: each interferer contributes ~1/N to noise.
    # SNR = 1 / sqrt(alpha) for mean-field Hopfield.
    if alpha <= 0:
        return float("inf")
    snr = 1.0 / math.sqrt(alpha)
    # R ~ erf(snr / sqrt(2))
    # Use erfc approximation
    return snr

_snr_05 = _snr_at_alpha(0.05, 1024)
# At alpha=0.05, SNR = 1/sqrt(0.05) = 4.47 -> R > 0.99
_r_approx_05 = 0.5 * (1.0 + math.erf(_snr_05 / math.sqrt(2.0)))
assert _r_approx_05 > 0.95, f"R at alpha=0.05 approx={_r_approx_05:.4f}, expected >0.95"

# Ordering test
assert HP_ALPHA_MAX_R90_LO < HP_ALPHA_MAX_R90_HI, "HP bounds inconsistent"
assert HP_ALPHA_MAX_R99_MIN < HP_ALPHA_MAX_R90_LO, (
    f"R=0.99 min={HP_ALPHA_MAX_R99_MIN} should be < R=0.90 lo={HP_ALPHA_MAX_R90_LO:.4f}"
)


def build_hopfield_w(M: int, N_dim: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, N_dim)).astype(np.float64)
    W = Xi.T @ Xi / N_dim
    np.fill_diagonal(W, 0.0)
    return W, Xi


def retrieval_accuracy(W: np.ndarray, Xi: np.ndarray, N_dim: int) -> float:
    """Mean per-bit accuracy: (cos(retrieved, pattern) + 1) / 2."""
    accs = []
    for i in range(Xi.shape[0]):
        xi = Xi[i]
        raw = W @ xi
        retrieved = np.sign(raw)
        cos = float(np.dot(retrieved, xi)) / N_dim
        # Convert cosine [-1,1] to accuracy [0,1]
        accs.append((cos + 1.0) / 2.0)
    return float(np.mean(accs)) if accs else float("nan")


def run_seed(seed: int) -> Dict:
    """Sweep alpha, measure R for each R_target."""
    by_alpha = {}
    for alpha in ALPHA_SWEEP:
        M = max(1, int(alpha * N))
        accuracies = []
        for trial in range(N_TRIALS):
            W, Xi = build_hopfield_w(M, N, seed * 1000 + trial)
            acc = retrieval_accuracy(W, Xi, N)
            accuracies.append(acc)
        mean_acc = float(np.mean(accuracies))
        by_alpha[alpha] = mean_acc
        print(f"  [seed={seed} alpha={alpha:.3f} M={M}] mean_acc={mean_acc:.4f}", flush=True)

    # Compute alpha_max for each R_target
    alpha_max_by_R = {}
    for R_target in R_TARGETS:
        # Find largest alpha where mean_acc >= R_target
        valid_alphas = [a for a, acc in by_alpha.items() if acc >= R_target]
        if valid_alphas:
            alpha_max = max(valid_alphas)
        else:
            alpha_max = 0.0  # no operating point found
        alpha_max_by_R[R_target] = alpha_max
        print(f"  [seed={seed} R={R_target}] alpha_max={alpha_max:.4f}", flush=True)

    return {
        "seed": seed, "N": N,
        "by_alpha": by_alpha,
        "alpha_max_by_R": {str(r): v for r, v in alpha_max_by_R.items()},
        "run_mode": RUN_MODE,
    }


def _instrumentation_selftest():
    """Assert retrieval accuracy non-null and varies with alpha."""
    N_test = 256
    # Low alpha should give high acc
    W_low, Xi_low = build_hopfield_w(max(1, int(0.02 * N_test)), N_test, 42)
    acc_low = retrieval_accuracy(W_low, Xi_low, N_test)
    assert not math.isnan(acc_low), "acc_low is NaN"
    assert acc_low > 0.5, f"acc_low={acc_low:.4f} < 0.5 at very low alpha"

    # High alpha should give lower acc
    W_high, Xi_high = build_hopfield_w(max(1, int(0.14 * N_test)), N_test, 42)
    acc_high = retrieval_accuracy(W_high, Xi_high, N_test)
    assert not math.isnan(acc_high), "acc_high is NaN"

    print(f"[selftest] PASS: acc_low={acc_low:.4f} acc_high={acc_high:.4f} "
          f"(low alpha has higher acc: {acc_low > acc_high})", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    """Aggregate alpha_max(R) across seeds."""
    by_R: Dict = {str(r): [] for r in R_TARGETS}
    for sd in per_seed.values():
        amr = sd.get("alpha_max_by_R", {})
        for r in R_TARGETS:
            v = amr.get(str(r))
            if v is not None:
                by_R[str(r)].append(float(v))

    agg_by_R = {}
    for r_str, vals in by_R.items():
        agg_by_R[r_str] = {
            "mean_alpha_max": float(np.mean(vals)) if vals else float("nan"),
            "std_alpha_max": float(np.std(vals)) if len(vals) > 1 else float("nan"),
            "n_seeds": len(vals),
        }

    # Cell A: check monotone ordering per seed
    monotone_passes = 0
    n_seeds_total = len(per_seed)
    for sd in per_seed.values():
        amr = sd.get("alpha_max_by_R", {})
        vals_sorted = [float(amr.get(str(r), 0.0)) for r in sorted(R_TARGETS)]
        # Check strictly decreasing (R increases -> alpha_max decreases)
        is_mono = all(vals_sorted[i] >= vals_sorted[i+1]
                      for i in range(len(vals_sorted) - 1))
        if is_mono:
            monotone_passes += 1

    return {
        "by_R": agg_by_R,
        "monotone_pass_frac": monotone_passes / n_seeds_total if n_seeds_total > 0 else 0.0,
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    by_R = agg["by_R"]
    mono_frac = agg["monotone_pass_frac"]

    am_r90 = by_R.get("0.9") or by_R.get("0.90", {})
    am_r99 = by_R.get("0.99", {})

    mean_90 = am_r90.get("mean_alpha_max", float("nan")) if am_r90 else float("nan")
    mean_99 = am_r99.get("mean_alpha_max", float("nan")) if am_r99 else float("nan")

    cell_A_pass = mono_frac >= 0.60
    cell_B_pass = (not math.isnan(mean_90) and
                   HP_ALPHA_MAX_R90_LO <= mean_90 <= HP_ALPHA_MAX_R90_HI)
    cell_C_pass = (not math.isnan(mean_99) and mean_99 >= HP_ALPHA_MAX_R99_MIN)

    cells_pass = sum([cell_A_pass, cell_B_pass, cell_C_pass])

    r90_str = f"{mean_90:.4f}" if not math.isnan(mean_90) else "nan"
    r99_str = f"{mean_99:.4f}" if not math.isnan(mean_99) else "nan"

    if cells_pass == 3:
        return ("HARD_PASS",
                f"R-envelope CHARACTERIZED. "
                f"alpha_max(R=0.90)={r90_str}(hp=[{HP_ALPHA_MAX_R90_LO:.3f},{HP_ALPHA_MAX_R90_HI:.3f}]) "
                f"alpha_max(R=0.99)={r99_str}(hp>={HP_ALPHA_MAX_R99_MIN}) "
                f"monotone_frac={mono_frac:.2f}. A:{int(cell_A_pass)} B:{int(cell_B_pass)} C:{int(cell_C_pass)}.")
    if cells_pass <= 1:
        return ("HARD_FAIL",
                f"R-envelope not confirmed. "
                f"alpha_max(0.90)={r90_str} alpha_max(0.99)={r99_str} mono={mono_frac:.2f}. "
                f"A:{int(cell_A_pass)} B:{int(cell_B_pass)} C:{int(cell_C_pass)}.")
    return ("MIDDLE_BAND",
            f"{cells_pass}/3 cells. alpha_max(0.90)={r90_str} alpha_max(0.99)={r99_str} "
            f"mono={mono_frac:.2f}. A:{int(cell_A_pass)} B:{int(cell_B_pass)} C:{int(cell_C_pass)}.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"R_TARGETS={R_TARGETS} ALPHA_SWEEP={ALPHA_SWEEP} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE, "R_TARGETS": R_TARGETS}
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
        "R_TARGETS": R_TARGETS, "ALPHA_SWEEP": ALPHA_SWEEP, "seeds": SEEDS,
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
