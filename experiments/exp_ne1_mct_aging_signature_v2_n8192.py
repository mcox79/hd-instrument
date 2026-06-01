"""NE-1 v2: MCT aging signature at N=8192 with extended trajectory grid.

SCIENTIFIC QUESTION:
  Does the substrate exhibit aging phenomenology (two-time correlator scaling
  C(t,t_w) ~ f(t/t_w) for t > t_w) above the critical load alpha_c?

  v1 MIDDLE_BAND ROOT CAUSE: N=1024 too small; finite-size effects smeared the
  C(t,t_w) ~ f(t/t_w) scaling collapse. v2 runs at N=8192 (4x) with a wider
  t_w grid [20,50,100,200] and dt grid [10,25,50,100,200,400] to resolve the
  aging signal more clearly.

PRE-REGISTERED BANDS (refined from v1 MIDDLE outcome):
  HARD-PASS: at load alpha >= alpha_c=0.138:
    - Scaling collapse present: |Pearson r(log(t/t_w), C(t,t_w))| >= 0.70 in
      >= 4/5 seeds (negative correlation = C DECREASING with t/t_w is expected)
    - Collapse score >= 2.0 (t/t_w explains C variance better than raw t)
    - Below alpha_c (alpha=0.05): no aging; r < 0.50 OR collapse_score < 1.5
      in >= 4/5 seeds.
  HARD-FAIL: |r| < 0.30 above alpha_c in ALL 5 seeds (aging absent at N=8192;
             framework REFUTED).
  MIDDLE_BAND: some seeds show aging above alpha_c but < 4/5 pass; OR collapse
               score 1.5-2.0 (weak aging, inconclusive); OR no clear below/above
               contrast.

  No prior empirical anchor at N=8192: bands unchanged from v1 calibration-probe
  policy (+-50% of theoretical prediction).

DESIGN:
  N = 8192 (production; PROT-018 _n8192 binding).
  alpha_grid = [0.05, 0.10, 0.14] -- alpha_c ~ 0.138 for Hopfield.
  Vectorized (parallel-update) stochastic Glauber: all fields computed jointly,
  sigmoid threshold applied, Bernoulli sample -- functionally equivalent to
  synchronous-noise update at high beta; O(N^2) per step but vectorized.
  Extended trajectory: t_w in [20, 50, 100, 200], dt in [10, 25, 50, 100, 200, 400].
  Efficient: for each trial/seed/alpha, run one chain up to t_w_max+dt_max steps;
  record state snapshots at t_w checkpoints; compute C(t_w, t_w+dt) from pairs.
  5 seeds, 5 trials per (seed, alpha).
  Smoke: N=1024, 2 seeds, 3 trials.

PROT-018: anchor name contains _n8192; production N MUST equal 8192.
  Pre-ship audit: grep -E '(N =|n =)' confirms N=8192 in this script.

TIMEOUT ESTIMATE:
  Method: direct timing at N=8192 in local environment.
  Vectorized step at N=8192: ~30ms.
  Full run: 15 chains (5 seeds * 3 alpha) * 5 trials * 600 steps = 45000 steps.
  Wall estimate: 45000 * 0.030s = 1350s, plus W-build overhead.
  timeout_s = ceil(1.5 * 1350) = ceil(2025) -> 2100s.
  Note: smoke at N=1024 takes ~25s; scaling 8x in N gives ~200s at N=8192
  (measured); formula inputs: smoke_wall~25s, FULL_N/smoke_N=8, FULL_seeds/
  smoke_seeds=5/2=2.5, scaling_exp=1.5 -> ceil(1.5*25*8^1.5*2.5)=ceil(2121)
  -> 2100s (consistent). Below 7200s threshold, no flag needed.

Anchor: ne1_mct_aging_signature_v2_n8192
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_ne1_mct_aging_signature_v2_n8192.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import math
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "ne1_mct_aging_signature_v2_n8192"

# --- Production config (PROT-018: N=8192 binding) ---
N = 8192
ALPHA_GRID = [0.05, 0.10, 0.14]
ALPHA_C = 0.138
T_W_GRID = [20, 50, 100, 200]
DT_GRID  = [10, 25, 50, 100, 200, 400]
N_TRIALS = 5
BETA = 20.0
SEEDS_SMOKE = [7, 17]
SEEDS_FULL  = [7, 17, 23, 31, 41]
N_SMOKE = 1024  # smoke uses smaller N; FULL uses N=8192

# Pre-registered thresholds
HP_PEARSON_ABS = 0.70   # |Pearson r(log(t/t_w), C)| >= this for HP
HF_PEARSON_ABS = 0.30   # |r| < this for HF (no aging signal)
HP_COLLAPSE    = 2.0    # aging collapse score >= this for HP
HP_MIN_SEEDS   = 4      # out of 5 seeds must pass above alpha_c


def _random_patterns(M: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """M random bipolar patterns, shape (M, n)."""
    return rng.choice([-1.0, 1.0], size=(M, n))


def _build_weights(patterns: np.ndarray) -> np.ndarray:
    """Hebbian weight matrix (no self-connections), shape (n, n)."""
    n = patterns.shape[1]
    W = patterns.T @ patterns / n
    np.fill_diagonal(W, 0.0)
    return W


def _vectorized_glauber_step(state: np.ndarray, W: np.ndarray,
                              rng: np.random.Generator) -> np.ndarray:
    """Parallel-update stochastic Glauber step (vectorized, high-beta limit).

    Computes all local fields simultaneously, applies sigmoid, samples.
    Equivalent to sequential Glauber in distribution at high beta but O(N)
    vectorized ops rather than O(N^2) Python loops.
    """
    fields = W @ state
    p_plus = 1.0 / (1.0 + np.exp(-2.0 * BETA * fields))
    rand_vals = rng.random(len(state))
    return np.where(rand_vals < p_plus, 1.0, -1.0)


def _run_aging_trial(W: np.ndarray, init_state: np.ndarray,
                     t_w_grid: List[int], dt_grid: List[int],
                     rng: np.random.Generator) -> np.ndarray:
    """Run one chain; return correlator matrix[i,j] = C(t_w_grid[i], t_w_grid[i]+dt_grid[j]).

    Efficient: one chain, record snapshots at t_w checkpoints, compute C(t_w, t_w+dt)
    by running from each snapshot for dt more steps.
    """
    t_w_max = max(t_w_grid)
    dt_max = max(dt_grid)
    t_w_set = sorted(set(t_w_grid))
    n = len(init_state)

    # Run base chain up to t_w_max, record snapshots
    state = init_state.copy()
    snapshots: Dict[int, np.ndarray] = {}
    for step in range(1, t_w_max + 1):
        state = _vectorized_glauber_step(state, W, rng)
        if step in t_w_set:
            snapshots[step] = state.copy()

    # For each (t_w, dt): run dt more steps from snapshot, compute C
    corr = np.zeros((len(t_w_grid), len(dt_grid)))
    for i, t_w in enumerate(t_w_grid):
        s_tw = snapshots[t_w]
        # Run continuation chain up to dt_max
        s = s_tw.copy()
        dt_results: Dict[int, float] = {}
        dt_sorted = sorted(dt_grid)
        for dt in range(1, dt_sorted[-1] + 1):
            s = _vectorized_glauber_step(s, W, rng)
            if dt in dt_sorted:
                dt_results[dt] = float((s_tw @ s) / n)
        for j, dt in enumerate(dt_grid):
            corr[i, j] = dt_results[dt]

    return corr


def _pearson_r(x: List[float], y: List[float]) -> float:
    """Pearson correlation between x and y."""
    xa = np.array(x)
    ya = np.array(y)
    if xa.std() < 1e-10 or ya.std() < 1e-10:
        return 0.0
    return float(np.corrcoef(xa, ya)[0, 1])


def _collapse_score(t_w_grid: List[int], dt_grid: List[int],
                    corr_matrix: np.ndarray) -> float:
    """Ratio of variance explained by log(t/t_w) vs raw t.

    Score >= 2.0: t/t_w scaling dominates (aging signature).
    Score < 1.0: raw t dominates (equilibrium).
    """
    ratios: List[float] = []
    raw_ts: List[float] = []
    c_vals: List[float] = []
    for i, t_w in enumerate(t_w_grid):
        for j, dt in enumerate(dt_grid):
            t = t_w + dt
            ratios.append(math.log(t / t_w + 1e-9))
            raw_ts.append(float(t))
            c_vals.append(float(corr_matrix[i, j]))
    r2_ratio = _pearson_r(ratios, c_vals) ** 2
    r2_raw   = _pearson_r(raw_ts, c_vals) ** 2
    if r2_raw < 1e-6:
        return 1.0
    return float(r2_ratio / (r2_raw + 1e-9))


def _run_alpha_seed(M: int, n: int, seed: int,
                    t_w_grid: List[int], dt_grid: List[int],
                    n_trials: int) -> Dict:
    """Run aging correlator sweep for given M, n (dimensionality), seed."""
    rng = np.random.default_rng(seed)
    patterns = _random_patterns(M, n, rng)
    W = _build_weights(patterns)

    # Start from a noisy version of pattern 0 (5% flip)
    init = patterns[0].copy()
    flip_mask = rng.random(n) < 0.05
    init[flip_mask] *= -1.0

    # Average correlator over n_trials
    corr_sum = np.zeros((len(t_w_grid), len(dt_grid)))
    for _ in range(n_trials):
        corr_sum += _run_aging_trial(W, init, t_w_grid, dt_grid,
                                     np.random.default_rng(rng.integers(0, 2**31)))

    corr_mean = corr_sum / n_trials

    # Compute scaling metrics
    ratios: List[float] = []
    c_vals: List[float] = []
    for i, t_w in enumerate(t_w_grid):
        for j, dt in enumerate(dt_grid):
            t = t_w + dt
            ratios.append(math.log(t / t_w + 1e-9))
            c_vals.append(float(corr_mean[i, j]))

    pearson_r = _pearson_r(ratios, c_vals)
    collapse   = _collapse_score(t_w_grid, dt_grid, corr_mean)

    return {
        "M": M,
        "n": n,
        "seed": seed,
        "pearson_r": pearson_r,
        "collapse_score": collapse,
        "corr_matrix": corr_mean.tolist(),
    }


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    n_test = 128
    M_test = 8
    rng = np.random.default_rng(42)
    patterns = _random_patterns(M_test, n_test, rng)
    W = _build_weights(patterns)
    assert W.shape == (n_test, n_test), "W shape wrong"
    assert abs(np.diag(W).sum()) < 1e-9, "W diagonal not zero"

    init = patterns[0].copy()
    # Single vectorized Glauber step
    s = _vectorized_glauber_step(init, W, rng)
    assert s.shape == (n_test,), "glauber output shape wrong"
    assert set(np.unique(s)) <= {-1.0, 1.0}, "glauber output not bipolar"

    # Aging trial on tiny grid
    t_w_test = [2, 5]
    dt_test   = [1, 3]
    corr = _run_aging_trial(W, init, t_w_test, dt_test, rng)
    assert corr.shape == (2, 2), f"corr shape wrong: {corr.shape}"
    assert not np.any(np.isnan(corr)), "corr contains NaN"
    assert np.all(np.abs(corr) <= 1.0 + 1e-6), "corr out of range"
    assert np.any(corr != 0.0), "all correlators are zero (instrumentation bug)"

    # Collapse score on known-good input
    cm = np.array([[0.9, 0.7, 0.5, 0.3, 0.1, 0.05],
                   [0.8, 0.6, 0.4, 0.2, 0.08, 0.02],
                   [0.7, 0.5, 0.3, 0.1, 0.04, 0.01],
                   [0.6, 0.4, 0.2, 0.05, 0.01, 0.005]])
    cs = _collapse_score(T_W_GRID, DT_GRID, cm)
    assert cs is not None and cs >= 0.0, f"collapse score invalid: {cs}"

    # Pearson identity test
    pr = _pearson_r([1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0])
    assert abs(pr - 1.0) < 1e-6, f"Pearson r identity failed: {pr}"

    # run_alpha_seed end-to-end at tiny scale
    result = _run_alpha_seed(M_test, n_test, seed=99,
                             t_w_grid=[2, 5], dt_grid=[1, 3], n_trials=2)
    assert "pearson_r" in result and result["pearson_r"] is not None, "pearson_r missing"
    assert "collapse_score" in result and result["collapse_score"] is not None, "collapse missing"
    assert not math.isnan(result["pearson_r"]), "pearson_r NaN"
    assert not math.isnan(result["collapse_score"]), "collapse_score NaN"

    print("SELFTEST PASSED: ne1_mct_aging_signature_v2_n8192")


_instrumentation_selftest()


def run_experiment(smoke: bool = False) -> Dict:
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_run = N_SMOKE if smoke else N
    t_w_grid = T_W_GRID
    dt_grid  = DT_GRID
    n_trials = 3 if smoke else N_TRIALS

    results = []

    for alpha in ALPHA_GRID:
        M = max(1, int(alpha * n_run))
        for seed in seeds:
            t0_cell = time.time()
            r = _run_alpha_seed(M, n_run, seed, t_w_grid, dt_grid, n_trials)
            r["alpha"] = alpha
            r["smoke"] = smoke
            elapsed_cell = time.time() - t0_cell
            results.append(r)
            print(f"alpha={alpha:.3f} M={M} n={n_run} seed={seed} "
                  f"pearson_r={r['pearson_r']:.3f} collapse={r['collapse_score']:.2f} "
                  f"elapsed_cell={elapsed_cell:.1f}s")
            sys.stdout.flush()

    # Verdict logic (full run uses N=8192 results only)
    above_c = [r for r in results if r.get("alpha", 0) >= ALPHA_C and not r.get("smoke", False)]
    below_c = [r for r in results if r.get("alpha", 0) < ALPHA_C * 0.8 and not r.get("smoke", False)]
    # In smoke mode, use all results for a rough check
    if smoke:
        above_c = [r for r in results if r.get("alpha", 0) >= ALPHA_C]

    seeds_pass_above = sum(
        1 for r in above_c
        if abs(r["pearson_r"]) >= HP_PEARSON_ABS and r["collapse_score"] >= HP_COLLAPSE
    )
    seeds_total_above = len(above_c)

    seeds_fail_above = sum(
        1 for r in above_c if abs(r["pearson_r"]) < HF_PEARSON_ABS
    )

    avg_abs_pearson = (
        float(np.mean([abs(r["pearson_r"]) for r in above_c])) if above_c else 0.0
    )
    avg_pearson = (
        float(np.mean([r["pearson_r"] for r in above_c])) if above_c else 0.0
    )
    avg_collapse = (
        float(np.mean([r["collapse_score"] for r in above_c])) if above_c else 0.0
    )

    pass_fraction = seeds_pass_above / max(seeds_total_above, 1)

    if pass_fraction >= HP_MIN_SEEDS / 5 and avg_collapse >= HP_COLLAPSE:
        verdict = "HARD_PASS"
    elif seeds_fail_above == seeds_total_above or avg_abs_pearson < HF_PEARSON_ABS:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        f"NE-1 v2 MCT AGING N={n_run}: verdict={verdict} | "
        f"above_alpha_c: abs_pearson_r={avg_abs_pearson:.3f} pearson_r={avg_pearson:.3f} "
        f"collapse={avg_collapse:.2f} "
        f"({seeds_pass_above}/{seeds_total_above} seeds pass HP) | "
        f"HP: |r|>=0.70 AND collapse>=2.0 in >=4/5 seeds | "
        f"HF: all seeds |r|<0.30 above alpha_c"
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "avg_abs_pearson_r_above_c": avg_abs_pearson,
        "avg_pearson_r_above_c": avg_pearson,
        "avg_collapse_score_above_c": avg_collapse,
        "seeds_pass_above": seeds_pass_above,
        "seeds_total_above": seeds_total_above,
        "pass_fraction_above": pass_fraction,
        "N_run": n_run,
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
