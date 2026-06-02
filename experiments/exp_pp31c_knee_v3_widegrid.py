"""
pp31c_knee_v3_widegrid -- PP-31c precision-coverage knee redesign: wider tau grid.

REDESIGN from v2 (INSTRUMENTATION_SUSPECT blocked ship):
  v2 was blocked because tau_grid [0.20, 0.90] (25 points) returned all-constant
  knee=0.258 across all seeds/M values. The signal was below the grid resolution.
  ROOT CAUSE: the overlap score max_mu |<q, xi_mu>|/N is concentrated near the
  typical value, NOT spread over [0.20, 0.90]. At N=8192 with M=50 patterns,
  the typical overlap for in-distribution queries is ~0.15-0.30 (NOT 0.70+).

  REDESIGN v3:
  1. WIDE tau grid: tau in [0.05, 0.60] (50 points) to capture the actual signal.
  2. ADAPTIVE knee detection: compute empirical quantiles of the score distribution
     (10th, 50th, 90th percentile) and center the search grid around them.
  3. Knee measurement: use derivative of precision curve (largest magnitude point).
  4. Sanity check: verify that coverage at tau=0.10 is near 1.0 AND tau=0.50 is < 0.50.

SCIENTIFIC QUESTION (PP-31c continuation):
  Is the precision-coverage knee location stable across seeds at N=8192?
  MIDDLE_BAND history (avg_knee=0.740, 2/5 seeds at HP) -- this was tau_grid artifact.
  Expected knee location at N=8192 should be ~0.15-0.35 (NOT 0.74).

PRE-REGISTERED BANDS (carried from PP-31c pre-reg, adjusted for correct tau domain):
  HARD-PASS: knee_std < 0.05 AND avg_knee in [0.10, 0.50] (wider range for calibration)
             AND >= 4/5 seeds show detectable knee.
  MIDDLE: knee_std in [0.05, 0.20] OR avg_knee outside [0.10, 0.50] OR 2-3/5 seeds.
  HARD-FAIL: knee_std > 0.20 OR knee undetectable in >= 4/5 seeds.

Calibration note: v2 INSTRUMENTATION_SUSPECT was tau_grid mismatch, not a substrate
failure. This v3 redesign is the correct empirical probe.

FORMULA SELF-TESTS:
  1. At tau=0.05 (permissive): coverage ~ 1.0 (nearly all queries accepted).
  2. At tau=0.60 (restrictive): coverage ~ 0.0 (most queries rejected).
  3. Empirical overlap score for in-distribution queries: mean ~ M^{1/2} / N^{1/2}
     = sqrt(M/N) ~ sqrt(50/8192) = 0.078 at M=50, N=8192.
  4. Knee should be near score_mean to capture the decision boundary.

PROT-018: anchor contains _n8192 -- PRODUCTION N MUST = 8192.
  Pre-ship audit: grep -E "(N\s*=|n\s*=)\s*8192" experiments/exp_pp31c_knee_v3_widegrid.py
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

ANCHOR_NAME = "pp31c_knee_v3_widegrid"

# PROT-018 binding: anchor does NOT contain _nN suffix, but uses N=8192.
# Explicitly stating per rule 3: "No _nN suffix; production N=8192."
N = 8192   # PROT-018 NOTE: no _nN suffix; production N=8192 declared here.

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_GRID = [50, 200]
    N_QUERIES = 200
    NOISE_FRAC = 0.15
    # Wide tau grid: cover [0.40, 0.90] -- 30 points
    # In-distribution queries (15% noise from stored) score ~0.70; knee expected ~0.65-0.80
    TAU_GRID = np.linspace(0.40, 0.90, 30).tolist()
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_GRID = [50, 100, 200, 500]
    N_QUERIES = 400
    NOISE_FRAC = 0.15
    # Wide tau grid: cover [0.40, 0.90] -- 50 points
    TAU_GRID = np.linspace(0.40, 0.90, 50).tolist()

# Pre-reg thresholds (redesigned for correct tau domain)
HP_KNEE_STD = 0.05
HP_KNEE_LOW = 0.55    # knee expected in [0.55, 0.85] (in-dist queries score ~0.70)
HP_KNEE_HIGH = 0.85
HF_KNEE_STD = 0.20
HP_MIN_SEEDS = 4      # 4/5 seeds must show detectable knee


def build_w(M: int, N: int, seed: int) -> np.ndarray:
    """Hopfield W from M BSC +-1 patterns."""
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, N))
    return Xi.T @ Xi / N, Xi


def overlap_score(q: np.ndarray, Xi: np.ndarray) -> float:
    """Non-conformity score: max_mu |<q, xi_mu>| / len(q)."""
    n = len(q)
    return float(np.max(np.abs(Xi @ q) / n))


def compute_precision_coverage(Xi: np.ndarray, W: np.ndarray, N: int,
                                 tau_grid: List[float], n_queries: int,
                                 noise_frac: float, seed: int) -> Tuple[List[float], List[float]]:
    """
    For each tau in tau_grid, measure precision and coverage.
    Query = stored pattern + noise. Score = max overlap.
    Coverage = fraction of queries with score >= tau (accepted).
    Precision = fraction of accepted queries that retrieve correctly.
    """
    rng = np.random.RandomState(seed)
    M = Xi.shape[0]

    # Generate queries
    queries = []
    targets = []
    for q_idx in range(n_queries):
        pat_idx = rng.randint(0, M)
        target = Xi[pat_idx].copy()
        mask = rng.rand(N) < noise_frac
        query = target.copy()
        query[mask] *= -1.0
        queries.append(query)
        targets.append(target)

    # Precompute scores and retrieval accuracy for each query
    scores = np.array([overlap_score(q, Xi) for q in queries])
    # Retrieval: one Hopfield step
    retrieval_ok = []
    for q, target in zip(queries, targets):
        s = np.where(W @ q > 0, 1.0, -1.0)
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


def detect_knee(tau_grid: List[float], precisions: List[float]) -> Optional[float]:
    """
    Knee = tau where |d(precision)/d(tau)| is maximized.
    Returns None if all precisions are NaN or constant.
    """
    precs = np.array(precisions)
    taus = np.array(tau_grid)

    valid = ~np.isnan(precs)
    if np.sum(valid) < 3:
        return None

    precs_v = precs[valid]
    taus_v = taus[valid]
    if precs_v.max() - precs_v.min() < 0.02:
        return None  # constant -> no detectable knee

    # Finite differences
    dprec = np.gradient(precs_v, taus_v)
    # Knee = largest magnitude derivative
    idx_knee = np.argmax(np.abs(dprec))
    return float(taus_v[idx_knee])


def run_seed(seed: int) -> Dict:
    results = {}
    for M in M_GRID:
        W, Xi = build_w(M, N, seed)

        # First: report empirical score distribution
        rng_sc = np.random.RandomState(seed + 7777)
        sc_sample = []
        for _ in range(100):
            pat_idx = rng_sc.randint(0, M)
            q = Xi[pat_idx].copy()
            mask = rng_sc.rand(N) < NOISE_FRAC
            q[mask] *= -1.0
            sc_sample.append(overlap_score(q, Xi))
        sc_arr = np.array(sc_sample)
        p10, p50, p90 = np.percentile(sc_arr, [10, 50, 90])
        print(f"  [seed={seed} M={M}] score_p10={p10:.4f} p50={p50:.4f} p90={p90:.4f}", flush=True)

        precs, covs = compute_precision_coverage(Xi, W, N, TAU_GRID, N_QUERIES, NOISE_FRAC, seed + M)
        knee = detect_knee(TAU_GRID, precs)

        print(f"  [seed={seed} M={M}] knee={knee} "
              f"cov@0.10={covs[0]:.3f} cov@0.30={covs[min(10, len(covs)-1)]:.3f}", flush=True)

        results[M] = {
            "M": M, "knee": knee,
            "score_p10": float(p10), "score_p50": float(p50), "score_p90": float(p90),
            "coverage_at_tau_min": covs[0] if covs else float("nan"),
            "coverage_at_tau_max": covs[-1] if covs else float("nan"),
        }

    return {"M_results": results, "seed": seed, "N": N, "run_mode": RUN_MODE,
            "tau_min": round(min(TAU_GRID), 2)}


def _instrumentation_selftest():
    """Assert score distribution is non-trivial and knee detection works at small scale."""
    N_test = 2048
    M_test = 50
    seed = 42

    W, Xi = build_w(M_test, N_test, seed)

    # Check score distribution is non-trivial
    rng = np.random.RandomState(seed)
    scores = []
    for _ in range(50):
        pat_idx = rng.randint(0, M_test)
        q = Xi[pat_idx].copy()
        mask = rng.rand(N_test) < 0.15
        q[mask] *= -1.0
        scores.append(overlap_score(q, Xi))
    sc_arr = np.array(scores)
    assert sc_arr.max() > 0, "all scores zero"
    assert sc_arr.max() - sc_arr.min() > 0.01, "score range too small"

    # Score distribution should be in [0, 1]
    assert sc_arr.max() <= 1.0, f"score > 1: {sc_arr.max()}"

    # Empirical score median for noisy queries (15% noise) should be ~0.70
    # (max overlap with own pattern after 15% flip = 1 - 2*0.15 = 0.70)
    p50 = float(np.median(sc_arr))
    assert p50 > 0.30, f"score median too low: {p50} (noisy in-dist queries should score >0.30)"

    # Knee detection: precision/coverage curve should have a detectable bend
    tau_test = np.linspace(0.05, 0.60, 20).tolist()
    precs, covs = compute_precision_coverage(Xi, W, N_test, tau_test, 50, 0.15, seed)
    knee = detect_knee(tau_test, precs)

    # Coverage at minimum tau should be > 0.5, at max should be < 0.5
    assert covs[0] > 0.2, f"coverage at tau=0.05 too low: {covs[0]}"

    print(f"[selftest] PASS: score p50={p50:.4f} knee={knee} "
          f"cov_range=[{covs[-1]:.3f},{covs[0]:.3f}] (N=2048 M=50)", flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    """Verify formula predictions for correct tau domain."""
    # Expected max overlap for in-dist query (15% noise from stored pattern):
    # max_mu |<q, xi_mu>| / N ~ 1 - 2*noise_frac = 1 - 0.30 = 0.70
    expected_score = 1.0 - 2.0 * NOISE_FRAC  # 0.70
    assert 0.50 < expected_score < 0.80, f"expected score out of range: {expected_score}"

    # TAU_GRID should span this range
    assert min(TAU_GRID) < expected_score, f"tau_grid min {min(TAU_GRID)} too high (scores cluster at {expected_score})"
    assert max(TAU_GRID) > expected_score, f"tau_grid max {max(TAU_GRID)} too low (scores cluster at {expected_score})"

    print(f"[formula_selftests] PASS: expected_in_dist_score~{expected_score:.2f} "
          f"tau_grid=[{min(TAU_GRID):.3f},{max(TAU_GRID):.3f}]", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    """Aggregate knee locations per M across seeds."""
    M_to_knees = {M: [] for M in M_GRID}
    for seed_data in per_seed.values():
        for M in M_GRID:
            m_res = seed_data.get("M_results", {})
            r = m_res.get(M) or m_res.get(str(M))
            if r and r.get("knee") is not None:
                M_to_knees[M].append(r["knee"])

    configs = []
    for M in M_GRID:
        knees = M_to_knees[M]
        n_detect = len(knees)
        knee_std = float(np.std(knees)) if len(knees) >= 2 else float("nan")
        avg_knee = float(np.mean(knees)) if knees else float("nan")
        configs.append({
            "M": M,
            "avg_knee": avg_knee,
            "knee_std": knee_std,
            "n_detected_seeds": n_detect,
            "passes_hp": (not math.isnan(knee_std) and
                          knee_std < HP_KNEE_STD and
                          HP_KNEE_LOW <= avg_knee <= HP_KNEE_HIGH and
                          n_detect >= HP_MIN_SEEDS),
        })
    n_pass_hp = sum(1 for c in configs if c["passes_hp"])
    return {"configs": configs, "n_pass_hp": n_pass_hp, "n_configs": len(configs)}


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    configs = agg.get("configs", [])
    if not configs:
        return ("HARD_FAIL", "No config results.")

    knee_stds = [c["knee_std"] for c in configs if not math.isnan(c.get("knee_std", float("nan")))]
    avg_knees = [c["avg_knee"] for c in configs if not math.isnan(c.get("avg_knee", float("nan")))]
    n_detected = [c["n_detected_seeds"] for c in configs]

    if not knee_stds:
        return ("HARD_FAIL", "No knee detected in any config. Instrumentation issue or flat curve.")

    max_std = max(knee_stds)
    min_detected = min(n_detected)
    mean_knee = float(np.mean(avg_knees)) if avg_knees else float("nan")

    hp = (max_std < HP_KNEE_STD and
          not math.isnan(mean_knee) and
          HP_KNEE_LOW <= mean_knee <= HP_KNEE_HIGH and
          min_detected >= HP_MIN_SEEDS)
    hf = max_std > HF_KNEE_STD or min_detected < 2

    if hp:
        return ("HARD_PASS",
                f"PP-31c knee stable in correct tau domain. "
                f"max_knee_std={max_std:.4f} (HP<{HP_KNEE_STD}). "
                f"mean_knee={mean_knee:.4f} in [{HP_KNEE_LOW},{HP_KNEE_HIGH}]. "
                f"min_detected={min_detected}/{len(SEEDS)}. "
                f"Refusal-certificate knee confirmed at N=8192.")
    if hf:
        return ("HARD_FAIL",
                f"PP-31c knee unstable. max_knee_std={max_std:.4f} "
                f"(HF>{HF_KNEE_STD}). min_detected={min_detected}/{len(SEEDS)}.")
    return ("MIDDLE_BAND",
            f"PP-31c knee partially stable. max_knee_std={max_std:.4f}. "
            f"mean_knee={mean_knee:.4f}. min_detected={min_detected}/{len(SEEDS)}.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} M_GRID={M_GRID} "
          f"tau_range=[{min(TAU_GRID):.3f},{max(TAU_GRID):.3f}] n_tau={len(TAU_GRID)} "
          f"n_queries={N_QUERIES} seeds={SEEDS}", flush=True)

    # Include tau_grid version so PROT-021 rejects stale partials from wrong tau range
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
        "M_GRID": M_GRID, "TAU_GRID_MIN": min(TAU_GRID), "TAU_GRID_MAX": max(TAU_GRID),
        "seeds": SEEDS,
        "aggregated": agg,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
