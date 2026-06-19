"""Q15 -- Rate-conditioned gain c(lambda) burst tolerance.

SCIENTIFIC QUESTION:
  Does write-protocol modification with c(lambda) = lambda_nominal / lambda_observed
  scaling preserve burst tolerance within 2pp of non-burst baseline AND retention
  curve matches no-burst case within 5% over 1000 steps?

THEORY (Round 6 drill 1):
  Without gain correction: burst B patterns on top of steady-state M causes
  effective load alpha_eff = (M + B * c) / N; c=1 is uncorrected burst.
  With c(lambda) = lambda_nominal/lambda_observed: burst patterns are scaled down
  so their contribution to the Hopfield matrix is reduced to match steady-state
  write rate. c(lambda) < 1 when lambda_observed > lambda_nominal (burst).
  Prediction: scaled burst has same steady-state overlap as no-burst case within 2pp.

PRE-REGISTERED BANDS:
  HARD-PASS: |m_burst_corrected - m_no_burst| < 0.02 (2pp) at t=1000 steps AND
             retention curve at t in {100, 500, 1000} matches no-burst within 5pp.
  MIDDLE: |m_burst_corrected - m_no_burst| in [0.02, 0.10].
  HARD-FAIL: |m_burst_corrected - m_no_burst| > 0.10 (correction ineffective).

  BASELINE BAND (no correction):
  |m_burst_uncorrected - m_no_burst| must be >= 0.02 (otherwise burst is already
  negligible -- correction cannot be validated as doing anything). If baseline burst
  damage < 2pp, shift to MIDDLE with note "burst too mild to validate correction."

DESIGN:
  N=4096, M_steady=200 (alpha_steady=0.049), B_burst=50 patterns.
  lambda_nominal = M_steady / T_window (conceptual rate).
  lambda_observed = (M_steady + B_burst) / T_window.
  c(lambda) = M_steady / (M_steady + B_burst) = 200/250 = 0.80.
  Three conditions per seed:
    (1) no-burst: M=200 patterns only.
    (2) burst uncorrected: M=200 + B=50 additional patterns (c=1).
    (3) burst corrected: M=200 + B=50 patterns, each burst pattern's weight
        contribution scaled by c(lambda) = 0.80 (W += c * xi*xi^T / N).
  Track overlap m(t) = <xi_test, s(t)> / N for t = 0, 100, 500, 1000 steps
  (synchronous Hopfield updates of the test vector).
  Test pattern = patterns[0] (first stored, before burst).
  5 seeds.

FORMULA SELF-TESTS:
  1. c(lambda) = M_steady / (M_steady + B_burst) = 200/250 = 0.80.
  2. alpha_no_burst = 200/4096 = 0.0488.
  3. alpha_burst_uncorrected = 250/4096 = 0.0610.
  4. alpha_burst_corrected_eff = 200/4096 + 0.80*50/4096 = 0.0488 + 0.0098 = 0.0586.
     (slightly higher than no-burst -- correction not perfect but close).
  5. Expected overlap no-burst (below capacity): m ~ 1 - alpha ~ 0.95.

PROT-018: no _nN suffix. Production N=4096 per rule 3.
  Stated: production N = 4096; rationale: burst-tolerance confirmation at moderate N.

TIMEOUT ESTIMATE:
  5 seeds * 3 conditions * 1000 sync steps * O(N^2/N) = O(N).
  N=4096, 5*3*1000 = 15000 steps. Each step: N multiplies = 4096 ops ~ 4us.
  Total: 15000 * 4096 * 1e-9 * 1000 ~ 0.06s overhead.
  Pattern writes: 5 * 250 * N^2 / N = 5 * 250 * N ops = 5 * 250 * 4096 = 5.1M ops.
  timeout=300.

Anchor: rate_cond_gain_burst_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_rate_cond_gain_burst_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial  # noqa: E402

ANCHOR_NAME = "rate_cond_gain_burst_v1"

# Production config
N = 4096
M_STEADY = 200
B_BURST  = 50
C_GAIN   = M_STEADY / (M_STEADY + B_BURST)   # = 0.80
PROBE_STEPS = [0, 100, 500, 1000]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]

# Pre-registered thresholds
HP_M_DIFF    = 0.02   # |corrected - no_burst| < 2pp
HF_M_DIFF    = 0.10   # |corrected - no_burst| > 10pp
HP_CURVE_TOL = 0.05   # retention curve match within 5pp
MIN_BURST_DAMAGE = 0.02  # baseline burst damage must be visible


def build_hopfield_w(patterns: np.ndarray, N: int,
                     scale: float = 1.0) -> np.ndarray:
    """Build Hopfield W from patterns with optional per-batch scaling."""
    W = (patterns.T @ patterns) / N * scale
    np.fill_diagonal(W, 0.0)
    return W


def sync_step(W: np.ndarray, s: np.ndarray) -> np.ndarray:
    """One synchronous Hopfield update."""
    return np.where(W @ s > 0, 1.0, -1.0)


def probe_overlap(W: np.ndarray, xi_test: np.ndarray, N: int,
                  probe_steps: List[int]) -> Dict[int, float]:
    """Run synchronous dynamics from xi_test, record overlap at checkpoints."""
    s = xi_test.copy()
    t = 0
    results = {}
    max_step = max(probe_steps)
    for step in range(max_step + 1):
        if step in probe_steps:
            ov = float(np.dot(s, xi_test) / N)
            results[step] = ov
        if step < max_step:
            s = sync_step(W, s)
    return results


def run_seed(seed: int, N: int, M_steady: int, B_burst: int, c_gain: float,
             probe_steps: List[int]) -> Dict:
    """Run three conditions for one seed."""
    rng = np.random.default_rng(seed)
    # Generate patterns
    patterns_steady = rng.choice([-1.0, 1.0], size=(M_steady, N)).astype(np.float64)
    patterns_burst  = rng.choice([-1.0, 1.0], size=(B_burst, N)).astype(np.float64)
    xi_test = patterns_steady[0]  # test pattern

    # Condition 1: no-burst
    W_no_burst = (patterns_steady.T @ patterns_steady) / N
    np.fill_diagonal(W_no_burst, 0.0)
    ov_no_burst = probe_overlap(W_no_burst, xi_test, N, probe_steps)

    # Condition 2: burst uncorrected (c=1)
    W_burst_raw = W_no_burst.copy()
    W_burst_raw += (patterns_burst.T @ patterns_burst) / N
    np.fill_diagonal(W_burst_raw, 0.0)
    ov_burst_raw = probe_overlap(W_burst_raw, xi_test, N, probe_steps)

    # Condition 3: burst corrected (c = c_gain)
    W_burst_corr = W_no_burst.copy()
    W_burst_corr += (patterns_burst.T @ patterns_burst) / N * c_gain
    np.fill_diagonal(W_burst_corr, 0.0)
    ov_burst_corr = probe_overlap(W_burst_corr, xi_test, N, probe_steps)

    # Key metric: overlap at t=1000 steps
    t_final = max(probe_steps)
    m_no_burst_final  = ov_no_burst[t_final]
    m_burst_raw_final = ov_burst_raw[t_final]
    m_burst_corr_final = ov_burst_corr[t_final]

    burst_damage_baseline  = abs(m_burst_raw_final  - m_no_burst_final)
    burst_damage_corrected = abs(m_burst_corr_final - m_no_burst_final)

    # Retention curve match: max deviation across probe steps
    curve_max_dev = max(
        abs(ov_burst_corr[t] - ov_no_burst[t]) for t in probe_steps
    )

    return {
        "seed": seed,
        "m_no_burst_final": m_no_burst_final,
        "m_burst_raw_final": m_burst_raw_final,
        "m_burst_corr_final": m_burst_corr_final,
        "burst_damage_baseline": burst_damage_baseline,
        "burst_damage_corrected": burst_damage_corrected,
        "curve_max_dev_corrected_vs_no_burst": curve_max_dev,
        "ov_no_burst": {str(t): v for t, v in ov_no_burst.items()},
        "ov_burst_raw": {str(t): v for t, v in ov_burst_raw.items()},
        "ov_burst_corr": {str(t): v for t, v in ov_burst_corr.items()},
    }


# ---------------------------------------------------------------------------
# Instrumentation self-test
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert burst conditions produce non-null distinct overlaps at tiny scale."""
    res = run_seed(42, 256, 20, 5, 20.0/25.0, [0, 10, 50])
    assert "m_no_burst_final" in res, "m_no_burst_final missing"
    assert "m_burst_corr_final" in res, "m_burst_corr_final missing"
    assert not math.isnan(res["m_no_burst_final"]), "m_no_burst_final is NaN"
    assert not math.isnan(res["m_burst_corr_final"]), "m_burst_corr_final is NaN"
    assert 0.0 <= res["burst_damage_corrected"] <= 2.0, f"damage OOB: {res['burst_damage_corrected']}"
    print("[selftest] PASS: rate_cond_gain_burst_v1 metrics non-null", flush=True)


_instrumentation_selftest()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    run_mode = os.environ.get("HDLAB_RUN_MODE", "full")
    seeds = SEEDS_FULL if run_mode == "full" else SEEDS_SMOKE
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_config = {"N": N, "run_mode": run_mode}

    print(f"[{ANCHOR_NAME}] run_mode={run_mode} N={N} M_steady={M_STEADY} "
          f"B={B_BURST} c_gain={C_GAIN:.3f} seeds={seeds}", flush=True)

    done, remaining = resumable_seeds(seeds, out_dir, run_config=run_config)
    print(f"[{ANCHOR_NAME}] checkpoint: {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        print(f"  seed={seed}...", flush=True)
        res = run_seed(seed, N, M_STEADY, B_BURST, C_GAIN, PROBE_STEPS)
        res["N"] = N
        res["run_mode"] = run_mode
        write_partial(out_dir, seed, res)

    from experiments._seed_checkpoint import aggregate_partials
    per_seed = aggregate_partials(out_dir, seeds, run_config=run_config)

    damages_baseline  = [p["burst_damage_baseline"]  for p in per_seed.values()]
    damages_corrected = [p["burst_damage_corrected"] for p in per_seed.values()]
    curve_devs        = [p["curve_max_dev_corrected_vs_no_burst"] for p in per_seed.values()]

    avg_damage_baseline  = float(np.mean(damages_baseline))  if damages_baseline  else float("nan")
    avg_damage_corrected = float(np.mean(damages_corrected)) if damages_corrected else float("nan")
    avg_curve_dev        = float(np.mean(curve_devs))        if curve_devs        else float("nan")

    # Verdict
    burst_too_mild = avg_damage_baseline < MIN_BURST_DAMAGE
    if burst_too_mild:
        # Cannot validate correction if baseline burst is already negligible
        verdict = "MIDDLE_BAND"
        verdict_note = "burst_too_mild"
    elif avg_damage_corrected < HP_M_DIFF and avg_curve_dev < HP_CURVE_TOL:
        verdict = "HARD_PASS"
        verdict_note = "correction_effective"
    elif avg_damage_corrected > HF_M_DIFF:
        verdict = "HARD_FAIL"
        verdict_note = "correction_ineffective"
    else:
        verdict = "MIDDLE_BAND"
        verdict_note = "partial_correction"

    elapsed = time.time() - t0
    metrics = {
        "anchor": ANCHOR_NAME, "run_mode": run_mode, "N": N,
        "M_steady": M_STEADY, "B_burst": B_BURST, "c_gain": C_GAIN,
        "n_seeds": len(seeds),
        "avg_burst_damage_baseline": avg_damage_baseline,
        "avg_burst_damage_corrected": avg_damage_corrected,
        "avg_curve_max_dev": avg_curve_dev,
        "verdict": verdict, "verdict_note": verdict_note,
        "elapsed_s": elapsed,
        "thresholds": {
            "HP_m_diff": HP_M_DIFF, "HF_m_diff": HF_M_DIFF,
            "HP_curve_tol": HP_CURVE_TOL,
            "min_burst_damage_visible": MIN_BURST_DAMAGE,
        },
        "verdict_msg": (
            f"Rate-conditioned burst N={N} M_steady={M_STEADY} B={B_BURST} c={C_GAIN:.3f}: "
            f"baseline_damage={avg_damage_baseline:.4f}, "
            f"corrected_damage={avg_damage_corrected:.4f} (HP<{HP_M_DIFF}), "
            f"curve_dev={avg_curve_dev:.4f} (HP<{HP_CURVE_TOL}). "
            f"Note={verdict_note}. Verdict={verdict}."
        ),
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict} corrected_damage={avg_damage_corrected:.4f} elapsed={elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument("--self-test", action="store_true", dest="self_test")
    _args = _p.parse_args()
    if _args.self_test:
        sys.exit(0)
    main()
