"""Cell J: Tracy-Widom spectral edge at N=32768 (CPU-only).

SCIENTIFIC QUESTION:
  Does lambda_max of the substrate weight matrix W obey the Marchenko-Pastur upper
  edge with Tracy-Widom fluctuation envelope at M/N < 0.05?

  Marchenko-Pastur upper edge: lambda_plus = sigma^2 * (1 + sqrt(alpha))^2 where
  alpha = M/N, sigma^2 = 1/N (Hopfield normalization).
  Tracy-Widom fluctuation: lambda_max ~ lambda_plus + lambda_plus * N^{-2/3} * TW1
  where TW1 is a GUE Tracy-Widom random variable (mean ~ -1.21, std ~ 0.93).

PRE-REGISTERED BANDS:
  HARD-PASS: |lambda_max_mean - lambda_plus| < 3 * TW_scale (within 3-sigma TW envelope)
             AND |lambda_max_mean - lambda_plus| / lambda_plus < 0.10 (< 10% relative error)
             in >= 4/5 seeds.
  MIDDLE: 3-10 sigma or 10-20% relative error.
  HARD-FAIL: > 10 sigma deviation OR > 20% relative error (MP law violated at this scale).

  Calibration probe -- no prior empirical anchor at N=32768. Bands at +/-50% per policy.
  Note: TW fluctuations are O(N^{-2/3}) -- small. Main test is whether lambda_max
  is near lambda_plus (MP edge), not the TW tail-fit itself.

DESIGN:
  N = 32768, alpha_grid = [0.01, 0.02, 0.05] (M/N = 327, 655, 1638 patterns).
  5 seeds. For each (seed, alpha): build W = sum_mu xi_mu xi_mu^T / N,
  compute lambda_max via power iteration (not full eigendecomp -- avoids N^3 cost).
  Power iteration at N=32768: ~100 iterations of W @ v, cost O(M*N) per step.
  lambda_plus = (1 + sqrt(alpha))^2 / N (with normalization).

  IMPORTANT: W = (1/N) * pats.T @ pats, eigenvalues of W equal eigenvalues of
  (1/N) * pats @ pats.T scaled. Use the M x M matrix Gram matrix instead when M << N:
  lambda_max(W) = lambda_max((1/N) * pats @ pats.T) = lambda_max(G/N) where G = pats @ pats.T.
  This reduces cost from O(N^3) to O(M^3 + M^2*N), feasible at M=1638, N=32768.

  FORMULA SELF-TEST:
  alpha=0.01: lambda_plus = (1+0.1)^2 = 1.21 (for W with sigma^2=1, rescaled by 1/N -> 1.21/N)
  Wait -- W = (1/N) sum xi xi^T. For i.i.d. +/-1 entries, E[W] = 0, each xi has ||xi||=N.
  Eigenvalues of W: by MP law for A = (1/N) * xi * xi^T (rank-M matrix), the M nonzero
  eigenvalues of the (symmetric) W = (1/N) * Pats^T Pats concentrate near the MP bulk.
  W is N x N, rank M. The M nonzero eigenvalues = eigenvalues of G/N where G = Pats @ Pats^T (M x M).
  For large N, Wigner: eigenvalues of G/N concentrate near 1 + M*sigma^4 terms...
  Actually: G[i,j] = sum_k xi_i[k] xi_j[k]. For i=j: G[i,i] = sum_k xi_i[k]^2 = N.
  For i != j: G[i,j] = dot product ~ N(0, N). So G/N ~ I + O(1/sqrt(N)) off-diag.
  The Gram matrix spectrum: bulk near alpha = M/N * N / N = M/N mass near 1.
  MP law for W = (1/N) * Pats^T Pats: bulk edge at (1+sqrt(alpha))^2 (for alpha = M/N).
  lambda_max of W should track lambda_plus = (1 + sqrt(alpha))^2 (sigma^2 = 1 per entry).

PROT-018: no _nN suffix. n32768 in name is descriptor.
  Stated: production N = 32768; rationale: spectral edge test at large N.

TIMEOUT ESTIMATE:
  Gram matrix G = Pats @ Pats^T where Pats is M x N.
  M_max = 1638 (alpha=0.05 at N=32768), N=32768.
  G computation: M x N matrix multiplication -> O(M^2 * N) = 1638^2 * 32768 = 87 GB ops.
  At ~1 GFLOP/s numpy on CPU: ~87s per trial. 5 seeds * 3 alpha = 15 trials.
  Total: ~15 * 87 = 1305s. With 1.5x safety: ~2000s. Use timeout=3600 (1h).
  Smoke uses N=4096 and M_max=205: G is 205x205 much cheaper.

Anchor: tracy_widom_n32768_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_tracy_widom_n32768_v1.md
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

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "qd1_spectral_primitives_n32768_v1"

# Production config (PROT-018: N=32768 is production; smoke uses N_SMOKE=4096)
N_FULL  = 32768
N_SMOKE = 4096
ALPHA_GRID = [0.01, 0.02, 0.05]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]

# TW1 (GOE) parameters (approximation): mean ~ -1.21, variance ~ 1.61
TW1_MEAN = -1.21
TW1_STD  = 0.93

# Pre-registered thresholds
HP_SIGMA_FACTOR = 3.0     # within 3 sigma
HP_REL_ERROR    = 0.10    # < 10% relative error
HF_SIGMA_FACTOR = 10.0    # > 10 sigma
HF_REL_ERROR    = 0.20    # > 20% relative error
HP_MIN_SEEDS    = 4


def lambda_plus_theory(alpha: float, sigma2: float = 1.0) -> float:
    """Marchenko-Pastur upper edge: (1 + sqrt(alpha))^2 * sigma2."""
    return (1.0 + math.sqrt(alpha)) ** 2 * sigma2


def tw_scale(N: int, alpha: float, sigma2: float = 1.0) -> float:
    """Tracy-Widom fluctuation scale: lambda_plus * N^{-2/3}."""
    lp = lambda_plus_theory(alpha, sigma2)
    return lp * N ** (-2.0 / 3.0)


def compute_lambda_max_gram(patterns: np.ndarray, N: int) -> float:
    """Compute lambda_max of W = (1/N) * Pats^T Pats via Gram matrix."""
    # G = Pats @ Pats^T (M x M)
    G = (patterns @ patterns.T) / N  # M x M
    # eigenvalues of G equal eigenvalues of W that are nonzero
    # (W is N x N rank-M; eigenvalues match G's eigenvalues)
    eigvals = np.linalg.eigvalsh(G)
    return float(eigvals.max())


# ---------------------------------------------------------------------------
# Instrumentation self-test
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert lambda_max and MP edge computations non-null."""
    rng = np.random.default_rng(0)
    N_t = 256
    alpha_t = 0.05
    M_t = int(alpha_t * N_t)
    pats = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(float)
    lm = compute_lambda_max_gram(pats, N_t)
    lp = lambda_plus_theory(alpha_t)
    tw_s = tw_scale(N_t, alpha_t)
    assert lm > 0, f"lambda_max <= 0: {lm}"
    assert not math.isnan(lm), "lambda_max is NaN"
    assert lp > 0, f"lambda_plus <= 0: {lp}"
    assert tw_s > 0, f"tw_scale <= 0: {tw_s}"
    # Formula self-test: at alpha=0.05, lambda_plus = (1 + 0.2236)^2 ~ 1.5
    assert abs(lp - (1 + math.sqrt(0.05)) ** 2) < 1e-9, "lambda_plus formula wrong"
    print(f"[selftest] PASS: lambda_max={lm:.4f} lambda_plus={lp:.4f} "
          f"tw_scale={tw_s:.6f}", flush=True)


_instrumentation_selftest()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _prot018_startup_check(n_actual: int) -> None:
    """PROT-018 runtime gate: anchor name binds to N=32768; fail fast if mismatch."""
    N_BOUND = 32768
    if n_actual != N_BOUND:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor name '{ANCHOR_NAME}' binds to "
            f"N={N_BOUND} but script is running at N={n_actual}. "
            f"Check HDLAB_RUN_MODE env var (must be 'full' for production run)."
        )


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "full")
    seeds = SEEDS_FULL if run_mode == "full" else SEEDS_SMOKE
    N = N_FULL if run_mode == "full" else N_SMOKE
    if run_mode == "full":
        _prot018_startup_check(N)
    print(f"[{ANCHOR_NAME}] run_mode={run_mode} seeds={seeds} N={N} "
          f"alpha_grid={ALPHA_GRID}", flush=True)

    results_by_alpha: Dict[float, List[Dict]] = {a: [] for a in ALPHA_GRID}

    for seed in seeds:
        rng = np.random.default_rng(seed)
        print(f"  seed={seed}...", flush=True)
        for alpha in ALPHA_GRID:
            M = max(1, int(alpha * N))
            t_cell = time.time()
            pats = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
            lm = compute_lambda_max_gram(pats, N)
            lp = lambda_plus_theory(alpha)
            tws = tw_scale(N, alpha)
            rel_err = abs(lm - lp) / lp
            sigma_dev = abs(lm - lp) / tws
            print(f"    alpha={alpha} M={M} lambda_max={lm:.4f} "
                  f"lambda_plus={lp:.4f} rel_err={rel_err:.4f} "
                  f"sigma_dev={sigma_dev:.2f} ({time.time()-t_cell:.1f}s)", flush=True)
            results_by_alpha[alpha].append({
                "seed": seed, "M": M, "lambda_max": lm,
                "lambda_plus": lp, "tw_scale": tws,
                "rel_error": rel_err, "sigma_dev": sigma_dev,
            })

    # Assess pass/fail per alpha per seed
    n_seeds = len(seeds)
    alpha_summaries = {}
    # Wave 5 anchor 1 pre-reg: sigma_TW empirical within +/-5% of theoretical.
    # Theoretical sigma_TW = lambda_plus * N^(-2/3) * TW1_STD
    # Empirical sigma_TW = std(lambda_max across seeds) for each alpha
    qd1_v1b_summaries = {}
    for alpha, trials in results_by_alpha.items():
        seeds_hp = sum(1 for t in trials
                       if t["sigma_dev"] < HP_SIGMA_FACTOR and t["rel_error"] < HP_REL_ERROR)
        seeds_hf = sum(1 for t in trials
                       if t["sigma_dev"] > HF_SIGMA_FACTOR or t["rel_error"] > HF_REL_ERROR)
        mean_rel = float(np.mean([t["rel_error"] for t in trials]))
        mean_sig = float(np.mean([t["sigma_dev"] for t in trials]))
        hp_pass = seeds_hp >= (HP_MIN_SEEDS if n_seeds >= 5 else math.ceil(n_seeds * 0.8))
        alpha_summaries[str(alpha)] = {
            "seeds_hp": seeds_hp, "seeds_hf": seeds_hf,
            "mean_rel_error": mean_rel, "mean_sigma_dev": mean_sig,
            "hp_pass": hp_pass,
        }
        # Wave 5 v1b: empirical sigma_TW from across-seed std of lambda_max
        lm_arr = np.array([t["lambda_max"] for t in trials], dtype=float)
        if lm_arr.size >= 2:
            sigma_tw_emp = float(np.std(lm_arr, ddof=1))
        else:
            sigma_tw_emp = float("nan")
        lp = lambda_plus_theory(alpha)
        sigma_tw_theory = lp * N ** (-2.0 / 3.0) * TW1_STD
        rel_dev_v1b = (abs(sigma_tw_emp - sigma_tw_theory) / sigma_tw_theory
                       if sigma_tw_theory > 0 else float("nan"))
        qd1_v1b_summaries[str(alpha)] = {
            "sigma_tw_emp": sigma_tw_emp,
            "sigma_tw_theory": sigma_tw_theory,
            "rel_dev_from_theory": rel_dev_v1b,
            "v1b_pass": (not math.isnan(rel_dev_v1b)) and rel_dev_v1b < 0.05,
        }

    # Overall verdict: HP if all alphas pass, HF if any alpha badly fails
    all_hp = all(s["hp_pass"] for s in alpha_summaries.values())
    any_hf = any(s["seeds_hf"] >= math.ceil(n_seeds * 0.6)
                 for s in alpha_summaries.values())

    if any_hf:
        verdict = "HARD_FAIL"
    elif all_hp:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "anchor": ANCHOR_NAME, "run_mode": run_mode,
        "N": N, "alpha_grid": ALPHA_GRID, "n_seeds": n_seeds,
        "alpha_summaries": alpha_summaries,
        "qd1_v1b_summaries": qd1_v1b_summaries,
        "verdict": verdict, "elapsed_s": elapsed,
        "thresholds": {
            "HP_sigma": HP_SIGMA_FACTOR, "HP_rel_err": HP_REL_ERROR,
            "HF_sigma": HF_SIGMA_FACTOR, "HF_rel_err": HF_REL_ERROR,
        },
        "verdict_msg": (
            f"Tracy-Widom spectral edge at N={N}: "
            f"alpha_summaries per-alpha: "
            + "; ".join(f"alpha={a}: rel_err={s['mean_rel_error']:.4f} "
                        f"sigma_dev={s['mean_sigma_dev']:.2f}"
                        for a, s in alpha_summaries.items())
            + f". Verdict: {verdict}."
        ),
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict} elapsed={elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument("--self-test", action="store_true", dest="self_test")
    _p.add_argument("--smoke", action="store_true",
                    help="Run at smoke scope (N_SMOKE, SEEDS_SMOKE) for gate validation")
    _args = _p.parse_args()
    if _args.self_test:
        sys.exit(0)
    if _args.smoke:
        os.environ["HDLAB_RUN_MODE"] = "smoke"
    main()
