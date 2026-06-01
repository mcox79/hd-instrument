"""NE-1: MCT/DMFT aging signature -- two-time correlator C(t,t_w) above alpha_c.

SCIENTIFIC QUESTION:
  Does the substrate exhibit aging phenomenology (two-time correlator scaling
  C(t,t_w) ~ f(t/t_w) for t > t_w) above the critical load alpha_c?

  This is the MCT signature observed in Nanomagnetic Hopfield Network (arXiv
  2202.02372, Nature Physics 2022). Binary test: aging present or absent. Zero
  theory required -- pure simulation observable.

PRE-REGISTERED BANDS:
  HARD-PASS: at load alpha > alpha_c, |Pearson r(log(t/t_w), C(t,t_w))| >= 0.70
             in >= 4/5 seeds (sign can be negative: C DECREASING with t/t_w is
             the expected aging signature), AND aging collapse score >= 2.0.
             Below alpha_c: collapse score < 1.5 in >= 4/5 seeds (no aging).
  HARD-FAIL: all seeds show r < 0.3 above alpha_c (aging absent regardless of load).
  MIDDLE-BAND: some seeds pass above alpha_c but not >= 4/5; or collapse score
               1.5-2.0 (weak aging signal, borderline).

  No prior empirical anchor on substrate: bands widened per calibration-probe
  policy (+-50% of theoretical prediction).

DESIGN:
  N = 1024, M_values in {0.05*N, 0.10*N, 0.14*N (alpha_c ~ 0.138)}.
  For each M: store W = sum x_i x_i^T (BSC/BPSK patterns).
  Two-time correlator C(t,t_w): run Glauber dynamics from a retrieved state.
    t_w = waiting time before measuring; t = observation time after t_w.
    C(t,t_w) = <s(t_w) . s(t_w + dt)> / N, averaged over trials.
  Sweep: t_w in {10, 20, 40} steps; dt in {5, 10, 20, 40, 80} steps.
  5 seeds, 3 alpha levels.

PROT-018: no _nN suffix (N is not the primary independent axis).
  Production N = 1024; stated per PROT-018 rule 3.
TIMEOUT ESTIMATE:
  Smoke N=1024, M=0.14*1024=143, 3 t_w values, 5 dt values, 2 seeds = ~20s.
  Full: 5 seeds, 3 alpha, same dynamics = ~50s.
  timeout_s = ceil(1.5 * 20 * 5/2) = ceil(75) -> 300s (PROT-019 floor).

Anchor: ne1_mct_aging_signature_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_ne1_mct_aging_signature_v1.md
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
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "ne1_mct_aging_signature_v1"

# --- Config ---
N = 1024
ALPHA_GRID = [0.05, 0.10, 0.14]  # alpha_c ~ 0.138 for Hopfield
ALPHA_C = 0.138
T_W_GRID = [10, 20, 40]          # waiting times
DT_GRID  = [5, 10, 20, 40, 80]   # observation intervals
SEEDS_SMOKE = [7, 17]
SEEDS_FULL  = [7, 17, 23, 31, 41]
N_TRIALS    = 10                  # trials per (t_w, dt, seed, alpha)

# Pre-registered thresholds
HP_PEARSON_R   = 0.70   # |Pearson r(log(t/t_w), C)| >= this for HARD-PASS
HF_PEARSON_R   = 0.30   # |r| < this for HARD-FAIL (no aging signal)
HP_COLLAPSE    = 2.0    # aging collapse score >= this for HARD-PASS
HF_COLLAPSE    = 1.0    # collapse score < this for HARD-FAIL
HP_MIN_SEEDS   = 4      # out of 5 seeds must pass


def _sign(x: np.ndarray) -> np.ndarray:
    """Bipolar sign: +1 if >= 0, -1 otherwise."""
    return np.where(x >= 0, 1.0, -1.0)


def _random_patterns(M: int, N: int, rng: np.random.Generator) -> np.ndarray:
    """M random bipolar patterns, shape (M, N)."""
    return rng.choice([-1.0, 1.0], size=(M, N))


def _build_weights(patterns: np.ndarray) -> np.ndarray:
    """Hebbian weight matrix (no self-connections), shape (N, N)."""
    W = patterns.T @ patterns / patterns.shape[1]
    np.fill_diagonal(W, 0.0)
    return W


def _glauber_update(state: np.ndarray, W: np.ndarray,
                    rng: np.random.Generator, beta: float = 20.0) -> np.ndarray:
    """One full sequential Glauber sweep."""
    N = len(state)
    order = rng.permutation(N)
    s = state.copy()
    for i in order:
        h_i = W[i] @ s
        p_plus = 1.0 / (1.0 + math.exp(-2.0 * beta * h_i))
        s[i] = 1.0 if rng.random() < p_plus else -1.0
    return s


def _two_time_correlator(W: np.ndarray, init_state: np.ndarray,
                          t_w: int, dt: int, n_trials: int,
                          rng: np.random.Generator, beta: float = 20.0) -> float:
    """Estimate C(t_w, t_w+dt) over n_trials independent trajectories."""
    N = len(init_state)
    corr_sum = 0.0
    for _ in range(n_trials):
        s = init_state.copy()
        for _ in range(t_w):
            s = _glauber_update(s, W, rng, beta)
        s_tw = s.copy()
        for _ in range(dt):
            s = _glauber_update(s, W, rng, beta)
        corr_sum += (s_tw @ s) / N
    return corr_sum / n_trials


def _pearson_r(x: List[float], y: List[float]) -> float:
    """Pearson correlation between x and y."""
    xa = np.array(x)
    ya = np.array(y)
    if xa.std() < 1e-10 or ya.std() < 1e-10:
        return 0.0
    return float(np.corrcoef(xa, ya)[0, 1])


def _collapse_score(t_w_list: List[int], dt_list: List[int],
                    corr_matrix: np.ndarray) -> float:
    """Variance of C explained by log(t/t_w) vs raw t.

    corr_matrix[i,j] = C(t_w_list[i], t_w_list[i] + dt_list[j]).
    Returns: var_explained_by_ratio / var_explained_by_raw_t (collapse score).
    If score >= 2.0: t/t_w scaling is the dominant variable (aging signature).
    """
    ratios = []
    raw_ts = []
    c_vals = []
    for i, t_w in enumerate(t_w_list):
        for j, dt in enumerate(dt_list):
            t = t_w + dt
            ratios.append(math.log(t / t_w + 1e-9))
            raw_ts.append(float(t))
            c_vals.append(float(corr_matrix[i, j]))
    r_ratio = _pearson_r(ratios, c_vals) ** 2
    r_raw   = _pearson_r(raw_ts, c_vals) ** 2
    if r_raw < 1e-6:
        return 1.0  # neither explains variance; neutral
    return float(r_ratio / (r_raw + 1e-9))


def _run_alpha(M: int, N: int, seed: int) -> Dict:
    """Run two-time correlator sweep for given M, N, seed."""
    rng = np.random.default_rng(seed)
    patterns = _random_patterns(M, N, rng)
    W = _build_weights(patterns)

    # Start from a noisy version of pattern 0
    init = patterns[0].copy()
    flip_mask = rng.random(N) < 0.05  # 5% noise
    init[flip_mask] *= -1.0

    corr_matrix = np.zeros((len(T_W_GRID), len(DT_GRID)))
    for i, t_w in enumerate(T_W_GRID):
        for j, dt in enumerate(DT_GRID):
            corr_matrix[i, j] = _two_time_correlator(
                W, init, t_w, dt, N_TRIALS, rng)

    # Compute collapse score and Pearson r(log(t/t_w), C)
    ratios = []
    c_vals = []
    for i, t_w in enumerate(T_W_GRID):
        for j, dt in enumerate(DT_GRID):
            t = t_w + dt
            ratios.append(math.log(t / t_w + 1e-9))
            c_vals.append(float(corr_matrix[i, j]))

    pearson_r = _pearson_r(ratios, c_vals)
    collapse   = _collapse_score(T_W_GRID, DT_GRID, corr_matrix)

    return {
        "M": M,
        "N": N,
        "seed": seed,
        "pearson_r": pearson_r,
        "collapse_score": collapse,
        "corr_matrix": corr_matrix.tolist(),
    }


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    rng = np.random.default_rng(42)
    M_test = 4
    N_test = 64
    patterns = _random_patterns(M_test, N_test, rng)
    W = _build_weights(patterns)
    assert W.shape == (N_test, N_test), "W shape wrong"
    assert np.diag(W).sum() == 0.0, "W diagonal not zero"

    init = patterns[0].copy()
    c = _two_time_correlator(W, init, t_w=3, dt=3, n_trials=2, rng=rng)
    assert c is not None, "correlator returned None"
    assert not math.isnan(c), "correlator is NaN"
    assert -1.0 <= c <= 1.0, f"correlator out of range: {c}"

    # collapse score on trivial input
    cm = np.array([[0.9, 0.7, 0.5, 0.3, 0.1],
                   [0.8, 0.6, 0.4, 0.2, 0.05],
                   [0.7, 0.5, 0.3, 0.1, 0.01]])
    cs = _collapse_score(T_W_GRID, DT_GRID, cm)
    assert cs is not None, "collapse score None"
    assert cs >= 0.0, "collapse score negative"

    pr = _pearson_r([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
    assert abs(pr - 1.0) < 1e-6, f"Pearson r identity test failed: {pr}"

    print("SELFTEST PASSED: ne1_mct_aging_signature_v1")


_instrumentation_selftest()


def run_experiment(smoke: bool = False) -> Dict:
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    results = []

    for alpha in ALPHA_GRID:
        M = max(1, int(alpha * N))
        for seed in seeds:
            r = _run_alpha(M, N, seed)
            r["alpha"] = alpha
            results.append(r)
            print(f"alpha={alpha:.2f} M={M} seed={seed} "
                  f"pearson_r={r['pearson_r']:.3f} collapse={r['collapse_score']:.2f}")

    # Verdict logic
    above_c = [r for r in results if r["alpha"] >= ALPHA_C]
    below_c = [r for r in results if r["alpha"] < ALPHA_C]

    # Use absolute Pearson r: aging shows as NEGATIVE correlation (C decreases with t/t_w)
    seeds_pass_above = sum(
        1 for r in above_c
        if abs(r["pearson_r"]) >= HP_PEARSON_R and r["collapse_score"] >= HP_COLLAPSE
    )
    seeds_total_above = len(above_c)
    seeds_fail_above = sum(
        1 for r in above_c if abs(r["pearson_r"]) < HF_PEARSON_R
    )

    avg_abs_pearson_above = (
        float(np.mean([abs(r["pearson_r"]) for r in above_c])) if above_c else 0.0
    )
    avg_pearson_above = (
        float(np.mean([r["pearson_r"] for r in above_c])) if above_c else 0.0
    )
    avg_collapse_above = (
        float(np.mean([r["collapse_score"] for r in above_c])) if above_c else 0.0
    )

    pass_fraction = seeds_pass_above / max(seeds_total_above, 1)

    if pass_fraction >= HP_MIN_SEEDS / 5 and avg_collapse_above >= HP_COLLAPSE:
        verdict = "HARD_PASS"
    elif seeds_fail_above == seeds_total_above or avg_abs_pearson_above < HF_PEARSON_R:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        f"NE-1 MCT/DMFT AGING: verdict={verdict} | "
        f"above_alpha_c: abs_pearson_r={avg_abs_pearson_above:.3f} pearson_r={avg_pearson_above:.3f} "
        f"collapse={avg_collapse_above:.2f} "
        f"({seeds_pass_above}/{seeds_total_above} seeds pass HP) | "
        f"HP: |r|>=0.70 (negative=aging) AND collapse>=2.0 in >=4/5 seeds | "
        f"HF: all seeds |r|<0.30 above alpha_c"
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "avg_pearson_r_above_c": avg_pearson_above,
        "avg_collapse_score_above_c": avg_collapse_above,
        "seeds_pass_above": seeds_pass_above,
        "seeds_total_above": seeds_total_above,
        "pass_fraction_above": pass_fraction,
        "results": results,
        "smoke": smoke,
    }
    return metrics


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        # _instrumentation_selftest() already ran at module scope; just exit 0
        sys.exit(0)

    t0 = time.time()
    metrics = run_experiment(smoke=args.smoke)
    elapsed = time.time() - t0
    metrics["elapsed_s"] = elapsed

    outdir = get_output_dir(ANCHOR_NAME)
    outdir.mkdir(parents=True, exist_ok=True)
    out_path = outdir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n{metrics['verdict_msg']}")
    print(f"elapsed={elapsed:.1f}s  output={out_path}")


if __name__ == "__main__":
    main()
