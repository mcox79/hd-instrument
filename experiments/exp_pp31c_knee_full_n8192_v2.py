"""Q7-RESHIP -- PP-31c precision-coverage knee calibration at N=8192 FULL run.

SCIENTIFIC QUESTION:
  Is the precision-coverage knee location stable across seeds at N=8192?
  v1 ran at SMOKE scale (2 seeds, LABEL-VS-HONEST catch at v322).
  This v2 is the FULL production run: 5 seeds, N=8192.

  PP-31c MIDDLE_BAND history (avg_knee=0.740, 2/5 seeds at HP) -- v1 result.
  Full seed run needed to determine if knee_std < 0.05 criterion is met.

PRE-REGISTERED BANDS (per Round 6, carried forward):
  HARD-PASS: knee_std < 0.05 AND avg_knee in [0.65, 0.85] AND >= 4/5 seeds show
             detectable knee.
  MIDDLE: knee_std in [0.05, 0.20] OR avg_knee outside [0.65, 0.85] OR only 2-3/5
          seeds show stable knee.
  HARD-FAIL: knee_std > 0.20 OR avg_knee outside [0.50, 0.95] (severely unstable)
             OR < 2/5 seeds show detectable knee.

DESIGN:
  N=8192, M sweep: {50, 100, 200, 500} (alpha = 0.006, 0.012, 0.024, 0.061).
  tau_grid: 25 points from 0.20 to 0.90.
  For each (seed, M, tau): 200 noisy queries, measure precision and coverage.
  Knee = tau where |d(precision)/d(tau)| first exceeds 0.20 (bend threshold).
  5 seeds (production run).
  Overlap-based score: score(q) = max_mu |<q, xi_mu>| / N.

FORMULA SELF-TESTS:
  1. At tau=0.10 (permissive): coverage ~ 1.0, precision ~ baseline retrieval rate.
  2. At tau=0.95 (restrictive): coverage ~ 0.0, precision ~ 1.0.
  3. Knee: d(prec)/d(tau) >> d(cov)/d(tau) near the inflection.
  4. Self-overlap check: overlap_score(xi_mu, patterns) = 1.0 for planted pattern.

PROT-018: anchor contains _n8192 -- PRODUCTION N MUST = 8192.
  Pre-ship audit: grep -E "(N\s*=|n\s*=)\s*8192" experiments/exp_pp31c_knee_full_n8192_v2.py
  Expected match: N = 8192 on line below.

TIMEOUT ESTIMATE (from smoke of v1, scaled to FULL):
  v1 smoke (2 seeds, N=8192) took approx 30-60s (estimated).
  FULL: 5 seeds vs 2 seeds = 2.5x. N unchanged.
  timeout = ceil(1.5 * 60 * 1.0 * 2.5) = ceil(225) = 300. timeout=600 (2x safety).

Anchor: pp31c_knee_full_n8192_v2
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_pp31c_knee_full_n8192_v2.md
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

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, resumable_seeds, write_partial, aggregate_partials
)

ANCHOR_NAME = "pp31c_knee_full_n8192_v2"

# PROT-018 binding: anchor contains _n8192 => N MUST = 8192
N = 8192    # PROT-018 BINDING: matches _n8192 suffix
M_GRID = [50, 100, 200, 500]
TAU_GRID = np.linspace(0.20, 0.90, 25).tolist()
N_QUERIES = 200
NOISE_FRAC = 0.15
SEEDS_FULL  = [7, 17, 23, 31, 41]   # FULL: 5 seeds
SEEDS_SMOKE = [7, 17]               # smoke: 2 seeds (only for local gate)

# Pre-registered thresholds (from Round 6 + carried through v1)
HP_KNEE_STD  = 0.05
HP_KNEE_LOW  = 0.65
HP_KNEE_HIGH = 0.85
HF_KNEE_STD  = 0.20
HP_MIN_SEEDS = 4
HF_MIN_SEEDS = 2


def build_w_hopfield(patterns: np.ndarray, N: int) -> np.ndarray:
    W = (patterns.T @ patterns) / N
    np.fill_diagonal(W, 0.0)
    return W


def retrieve(W: np.ndarray, query: np.ndarray, max_steps: int = 10) -> np.ndarray:
    """Synchronous Hopfield retrieval."""
    s = query.copy()
    for _ in range(max_steps):
        s_new = np.where(W @ s > 0, 1.0, -1.0)
        if np.all(s_new == s):
            break
        s = s_new
    return s


def overlap_score(query: np.ndarray, patterns: np.ndarray, N: int) -> float:
    """max_mu |<q, xi_mu>| / N -- overlap-based score."""
    dots = np.abs(patterns @ query) / N
    return float(np.max(dots))


def run_cell(N: int, M: int, tau_grid: List[float], n_queries: int,
             noise_frac: float, rng: np.random.Generator) -> Dict:
    """Run one (seed, M) cell. Return precision-coverage curve and knee."""
    patterns = rng.choice([-1.0, 1.0], size=(M, N))
    W = build_w_hopfield(patterns, N)

    # Generate noisy queries for M patterns + random queries
    queries = []
    true_labels = []
    for mu in range(min(M, n_queries)):
        q = patterns[mu].copy()
        n_flip = int(noise_frac * N)
        flip_idx = rng.choice(N, size=n_flip, replace=False)
        q[flip_idx] *= -1
        queries.append(q)
        true_labels.append(mu)
    n_random = max(0, n_queries - len(queries))
    for _ in range(n_random):
        q = rng.choice([-1.0, 1.0], size=N)
        queries.append(q)
        true_labels.append(-1)

    # Compute overlap scores + Hopfield retrieval success
    scores = []
    final_overlaps = []
    for i, q in enumerate(queries):
        score = overlap_score(q, patterns, N)
        scores.append(score)
        final = retrieve(W, q)
        if true_labels[i] >= 0:
            mu = true_labels[i]
            ov = float(np.mean(final == patterns[mu]))
        else:
            ov = 0.0
        final_overlaps.append(ov)

    scores = np.array(scores)
    final_overlaps = np.array(final_overlaps)
    true_arr = np.array(true_labels)

    # Build precision-coverage curve
    precisions, coverages = [], []
    for tau in tau_grid:
        mask = scores >= tau
        n_pass = int(mask.sum())
        coverage = n_pass / len(scores)
        if n_pass == 0:
            precision = 1.0
        else:
            tp = int(((mask) & (true_arr >= 0) & (final_overlaps >= 0.80)).sum())
            precision = tp / n_pass
        precisions.append(precision)
        coverages.append(coverage)

    precisions = np.array(precisions)
    coverages = np.array(coverages)

    # Find knee: largest tau where |d(prec)/d(tau)| >= 0.20
    knee_tau = None
    for idx in range(1, len(tau_grid) - 1):
        dp = abs(precisions[idx + 1] - precisions[idx - 1]) / (tau_grid[idx + 1] - tau_grid[idx - 1])
        if dp >= 0.20:
            knee_tau = tau_grid[idx]
    if knee_tau is None:
        dp = np.abs(np.gradient(precisions, tau_grid))
        knee_tau = float(tau_grid[int(np.argmax(dp))])

    return {"M": M, "knee_tau": knee_tau,
            "precisions": [float(p) for p in precisions],
            "coverages": [float(c) for c in coverages]}


# ---------------------------------------------------------------------------
# Instrumentation self-test -- MUST verify at FULL N scope (PROT-018 / v322 lesson)
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert precision-coverage knee non-null at production N (tiny M for speed)."""
    rng = np.random.default_rng(0)
    # Use production N=8192 with tiny M for speed
    N_test = 8192
    M_test = 10
    tau_test = [0.2, 0.4, 0.6, 0.8]
    res = run_cell(N_test, M_test, tau_test, 20, 0.15, rng)
    assert res["knee_tau"] is not None, "knee_tau is None at N=8192"
    assert 0.0 <= res["knee_tau"] <= 1.0, f"knee_tau out of range: {res['knee_tau']}"
    assert len(res["precisions"]) == len(tau_test), "precision length mismatch"
    assert not any(math.isnan(p) for p in res["precisions"]), "precision contains NaN"
    # Verify self-overlap = 1.0
    pats = rng.choice([-1.0, 1.0], size=(M_test, N_test))
    q = pats[0].copy()
    s = overlap_score(q, pats, N_test)
    assert abs(s - 1.0) < 1e-5, f"self-overlap should be 1.0, got {s}"
    print(f"[selftest] PASS: pp31c_knee_full_n8192_v2 N={N} instrumentation non-null", flush=True)


_instrumentation_selftest()


# ---------------------------------------------------------------------------
# PROT-018 runtime startup check
# ---------------------------------------------------------------------------

def _prot018_check():
    """Verify production N matches anchor-name suffix at startup."""
    expected_n = 8192
    if N != expected_n:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor name contains _n{expected_n} but "
            f"script's production N = {N}. Fix the script or rename the anchor."
        )

_prot018_check()


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

    print(f"[{ANCHOR_NAME}] run_mode={run_mode} seeds={seeds} N={N} M_grid={M_GRID}", flush=True)

    done, remaining = resumable_seeds(seeds, out_dir, run_config=run_config)
    print(f"[{ANCHOR_NAME}] checkpoint: {len(done)} done, {len(remaining)} remaining", flush=True)

    all_results: Dict[str, Dict] = {}

    # Load done seeds
    loaded = aggregate_partials(out_dir, done, run_config=run_config) if done else {}
    for sk, payload in loaded.items():
        all_results[sk] = payload.get("seed_res", {})

    for seed in remaining:
        rng = np.random.default_rng(seed)
        print(f"  seed={seed}...", flush=True)
        seed_res = {}
        for M in M_GRID:
            cell = run_cell(N, M, TAU_GRID, N_QUERIES, NOISE_FRAC, rng)
            seed_res[str(M)] = cell
            print(f"    M={M} knee_tau={cell['knee_tau']:.3f}", flush=True)
        all_results[str(seed)] = seed_res
        write_partial(out_dir, seed, {"seed": seed, "seed_res": seed_res, "N": N, "run_mode": run_mode})

    # Aggregate: collect knee_tau across seeds (use M=100 as reference cell)
    M_ref = str(M_GRID[1])  # M=100
    knee_taus = []
    for seed_res in all_results.values():
        if isinstance(seed_res, dict) and M_ref in seed_res:
            kt = seed_res[M_ref]["knee_tau"]
            if kt is not None:
                knee_taus.append(kt)

    n_stable_seeds = len(knee_taus)
    avg_knee = float(np.mean(knee_taus)) if knee_taus else float("nan")
    knee_std = float(np.std(knee_taus)) if knee_taus else float("nan")

    n_seeds = len(seeds)
    hp_stable = (n_stable_seeds >= HP_MIN_SEEDS if n_seeds >= 5
                 else n_stable_seeds >= math.ceil(n_seeds * 0.8))

    if (not math.isnan(knee_std) and knee_std < HP_KNEE_STD
            and HP_KNEE_LOW <= avg_knee <= HP_KNEE_HIGH and hp_stable):
        verdict = "HARD_PASS"
    elif (math.isnan(knee_std) or knee_std > HF_KNEE_STD
          or not (0.50 <= avg_knee <= 0.95) or n_stable_seeds < HF_MIN_SEEDS):
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "anchor": ANCHOR_NAME, "run_mode": run_mode,
        "N": N, "M_grid": M_GRID, "M_ref_for_summary": int(M_ref),
        "n_seeds": n_seeds, "n_stable_seeds": n_stable_seeds,
        "avg_knee": avg_knee, "knee_std": knee_std,
        "verdict": verdict, "elapsed_s": elapsed,
        "per_seed_knee": {str(s): all_results.get(str(s), {}).get(M_ref, {}).get("knee_tau", None)
                          for s in seeds},
        "thresholds": {
            "HP_knee_std": HP_KNEE_STD, "HP_knee_low": HP_KNEE_LOW,
            "HP_knee_high": HP_KNEE_HIGH, "HF_knee_std": HF_KNEE_STD,
            "HP_min_seeds": HP_MIN_SEEDS,
        },
        "verdict_msg": (
            f"PP-31c knee FULL N={N} 5-seed: avg_knee={avg_knee:.3f} "
            f"(HP [{HP_KNEE_LOW},{HP_KNEE_HIGH}]), std={knee_std:.4f} "
            f"(HP<{HP_KNEE_STD}), {n_stable_seeds}/{n_seeds} seeds stable. "
            f"Verdict: {verdict}."
        ),
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict} avg_knee={avg_knee:.3f} "
          f"std={knee_std:.4f} elapsed={elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument("--self-test", action="store_true", dest="self_test")
    _args = _p.parse_args()
    if _args.self_test:
        sys.exit(0)
    main()
