"""PP31-2A: Hard threshold precision-coverage sweep over tau in [0.3, 0.8].

SCIENTIFIC QUESTION:
  Does the substrate's precision-coverage curve for threshold-based refusal
  exhibit a detectable knee, AND does precision >= 0.92 at coverage >= 0.60
  at some tau in [0.3, 0.8]?

  PP-31 Sub-cap 2-A: foundational sweep for calibrated refusal gate.
  Precision: among retrievals that PASS the threshold (score >= tau),
             fraction that achieve final overlap >= 0.80 (correct retrieval).
  Coverage: fraction of ALL queries that pass the threshold.
  Knee: largest tau where d(precision)/d(tau) > d(coverage)/d(tau)
        (precision-coverage tradeoff bends sharply).

PRE-REGISTERED BANDS:
  HARD-PASS: precision >= 0.92 at coverage >= 0.60 at some tau in [0.3, 0.8]
             AND knee is detectable (precision curve slope changes by >= 0.2
             per 0.1 tau unit somewhere in [0.3, 0.8]);
             in >= 4/5 seeds.
  HARD-FAIL: no tau in [0.3, 0.8] achieves precision >= 0.80 (even at minimal
             coverage) in >= 4/5 seeds; OR coverage < 0.10 for all tau <= 0.50.
  MIDDLE-BAND: precision >= 0.80 but not 0.92, or knee not detectable.

  No prior empirical anchor: bands at +-50% of theory.
  Theory: at alpha = 0.10 (N=512, M=51), retrieval success rate ~ 95% for <5% noise.

DESIGN:
  N = 512, M = 51 (alpha = 0.10, healthy regime).
  tau_grid = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80].
  For each tau: 100 queries (5% noise), compute score, classify pass/fail,
  check if passed query achieves final overlap >= 0.80.
  5 seeds (smoke: 3).

FORMULA SELF-TESTS:
  1. Precision = TP/(TP+FP) where TP = passed AND overlap>=0.80.
  2. Coverage = (TP+FP)/total_queries = fraction passing threshold.
  3. At tau=0.30 (permissive): high coverage (nearly 1.0), precision = baseline success rate.
  4. At tau=0.80 (restrictive): low coverage (<0.20), high precision (~1.0).

PROT-018: no _nN suffix. Production N = 512; stated per PROT-018 rule 3.
TIMEOUT ESTIMATE:
  Smoke: 3 seeds x 11 tau x 100 queries = 3300 queries, 15 steps each ~ 25s.
  Full: 5 seeds x same ~ 40s.
  timeout_s = 300 (PROT-019 floor; actual wall <60s).

Anchor: pp31_2a_precision_coverage_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_pp31_2a_precision_coverage_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import math
import time
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "pp31_2a_precision_coverage_v1"

# --- Config ---
N = 512
M = 51          # alpha = 0.10 (healthy regime)
N_QUERIES_SMOKE = 100
N_QUERIES_FULL  = 200   # walk-back gate: doubled since smoke coverage ~0.57 (within 5% of HP=0.60)
# Noise levels creating a range of confidence scores:
# Low noise (0.05) -> high initial overlap -> score ~ 0.90
# High noise (0.50) -> low initial overlap -> score ~ 0.0
# This ensures queries fall across the tau grid [0.3, 0.8]
NOISE_FRAC_GRID = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55]
N_STEPS = 15
TAU_GRID = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]
OVERLAP_SUCCESS_THRESH = 0.80  # retrieval success threshold

SEEDS_SMOKE = [7, 17, 23]
SEEDS_FULL  = [7, 17, 23, 31, 41]

# Pre-registered thresholds
HP_PRECISION = 0.92
HP_COVERAGE  = 0.60
HF_PRECISION = 0.80    # no tau achieves this -> HARD-FAIL
HF_MIN_COVERAGE_AT_50 = 0.10  # coverage < 10% at tau<=0.50 -> HARD-FAIL
HP_KNEE_SLOPE_CHANGE = 0.20   # slope change >= 0.20 per 0.1 tau -> knee detectable
HP_MIN_SEEDS = 4


def _random_patterns(M: int, N: int, rng: np.random.Generator) -> np.ndarray:
    return rng.choice([-1.0, 1.0], size=(M, N))


def _build_weights(patterns: np.ndarray) -> np.ndarray:
    W = patterns.T @ patterns / N
    np.fill_diagonal(W, 0.0)
    return W


def _sync_update(state: np.ndarray, W: np.ndarray) -> np.ndarray:
    s = np.sign(W @ state)
    s[s == 0] = 1.0
    return s


def _retrieval_score_and_overlap(W: np.ndarray, target: np.ndarray,
                                   noise_frac: float, n_steps: int,
                                   rng: np.random.Generator) -> tuple:
    """Return (confidence_score, final_overlap).

    Confidence score: initial overlap of noisy query with target (BEFORE retrieval).
    This naturally spans [0, 1] as noise_frac increases from 0 to 0.5.
    At noise_frac=0.05: score ~ 0.90; at noise_frac=0.50: score ~ 0.0.
    This ensures queries fall across the tau grid [0.3, 0.8].
    """
    N = len(target)
    state = target.copy()
    flip_mask = rng.random(N) < noise_frac
    state[flip_mask] *= -1.0

    # Confidence score: initial overlap (before retrieval)
    conf_score = float(np.dot(state, target) / N)

    # Full retrieval after n_steps
    s = state.copy()
    for _ in range(n_steps):
        s = _sync_update(s, W)
    final_overlap = float(np.dot(s, target) / N)

    return conf_score, final_overlap


def _compute_precision_coverage_curve(W: np.ndarray, patterns: np.ndarray,
                                       tau_grid: List[float],
                                       n_queries: int,
                                       noise_frac_grid: List[float],
                                       n_steps: int,
                                       rng: np.random.Generator) -> List[Dict]:
    """Compute precision-coverage at each tau.

    Generate queries across the full noise grid so confidence scores span [0, 1].
    """
    target = patterns[0]
    results_by_query = []
    n_per_noise = max(1, n_queries // len(noise_frac_grid))
    for noise_frac in noise_frac_grid:
        for _ in range(n_per_noise):
            score, overlap = _retrieval_score_and_overlap(
                W, target, noise_frac, n_steps, rng)
            results_by_query.append({"score": score, "overlap": overlap})

    curve = []
    for tau in tau_grid:
        passed = [r for r in results_by_query if r["score"] >= tau]
        total = len(results_by_query)
        if len(passed) == 0:
            precision = 1.0  # no queries pass -> trivially all "correct"
        else:
            precision = sum(1 for r in passed if r["overlap"] >= OVERLAP_SUCCESS_THRESH) / len(passed)
        coverage = len(passed) / total
        curve.append({"tau": tau, "precision": precision, "coverage": coverage})
    return curve


def _detect_knee(curve: List[Dict]) -> float:
    """Return max slope change in precision per unit tau (larger = clearer knee)."""
    taus = [c["tau"] for c in curve]
    prec = [c["precision"] for c in curve]
    slopes = []
    for i in range(len(taus) - 1):
        dt = taus[i+1] - taus[i]
        dp = prec[i+1] - prec[i]
        slopes.append(dp / max(dt, 1e-6))
    if len(slopes) < 2:
        return 0.0
    max_change = max(
        abs(slopes[i+1] - slopes[i]) for i in range(len(slopes) - 1)
    )
    return max_change


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel."""
    rng = np.random.default_rng(42)
    M_test = 8
    patterns = _random_patterns(M_test, N, rng)
    W = _build_weights(patterns)

    score_lo, overlap_lo = _retrieval_score_and_overlap(
        W, patterns[0], 0.05, N_STEPS, rng)   # low noise -> high score
    score_hi, overlap_hi = _retrieval_score_and_overlap(
        W, patterns[0], 0.50, N_STEPS, rng)   # high noise -> low score
    for score, overlap in [(score_lo, overlap_lo), (score_hi, overlap_hi)]:
        assert score is not None, "score None"
        assert overlap is not None, "overlap None"
        assert not math.isnan(score), "score NaN"
        assert not math.isnan(overlap), "overlap NaN"
        assert -1.0 <= score <= 1.0, f"score range: {score}"
        assert -1.0 <= overlap <= 1.0, f"overlap range: {overlap}"
    # Low noise should give higher score than high noise
    assert score_lo > score_hi, f"low-noise score {score_lo:.3f} should exceed high-noise {score_hi:.3f}"

    curve = _compute_precision_coverage_curve(
        W, patterns, [0.3, 0.5, 0.7], n_queries=12,
        noise_frac_grid=[0.05, 0.25, 0.50], n_steps=5, rng=rng)
    assert len(curve) == 3, "curve length wrong"
    for c in curve:
        assert "precision" in c and "coverage" in c, "curve missing fields"
        assert 0.0 <= c["precision"] <= 1.0, f"precision out of range: {c['precision']}"
        assert 0.0 <= c["coverage"] <= 1.0, f"coverage out of range: {c['coverage']}"

    # Knee detection: constant precision -> knee=0
    flat_curve = [{"tau": t, "precision": 0.9, "coverage": 1.0 - t}
                   for t in [0.3, 0.4, 0.5, 0.6, 0.7]]
    assert _detect_knee(flat_curve) < 0.01, "flat curve should have near-zero knee"

    print("SELFTEST PASSED: pp31_2a_precision_coverage_v1")


_instrumentation_selftest()


def run_experiment(smoke: bool = False) -> Dict:
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    all_seed_results = []

    for seed in seeds:
        rng = np.random.default_rng(seed)
        patterns = _random_patterns(M, N, rng)
        W = _build_weights(patterns)
        n_queries = N_QUERIES_SMOKE if smoke else N_QUERIES_FULL

        curve = _compute_precision_coverage_curve(
            W, patterns, TAU_GRID, n_queries, NOISE_FRAC_GRID, N_STEPS, rng)
        knee = _detect_knee(curve)

        # Find tau where precision >= HP_PRECISION AND coverage >= HP_COVERAGE
        hp_tau = None
        for c in curve:
            if c["precision"] >= HP_PRECISION and c["coverage"] >= HP_COVERAGE:
                hp_tau = c["tau"]
                break

        # HF check: any tau achieves precision >= HF_PRECISION?
        any_hf_prec = any(c["precision"] >= HF_PRECISION for c in curve)
        # Coverage at tau=0.50
        cov_at_50 = next((c["coverage"] for c in curve if abs(c["tau"] - 0.50) < 0.01), 0.0)

        passes_hp = (hp_tau is not None and knee >= HP_KNEE_SLOPE_CHANGE)
        passes_hf_prec = not any_hf_prec
        passes_hf_cov  = cov_at_50 < HF_MIN_COVERAGE_AT_50

        print(f"seed={seed} hp_tau={hp_tau} knee={knee:.3f} cov_at_50={cov_at_50:.3f}")
        for c in curve:
            print(f"  tau={c['tau']:.2f} prec={c['precision']:.3f} cov={c['coverage']:.3f}")

        all_seed_results.append({
            "seed": seed,
            "curve": curve,
            "knee": knee,
            "hp_tau": hp_tau,
            "passes_hp": passes_hp,
            "cov_at_50": cov_at_50,
        })

    seeds_pass = sum(1 for r in all_seed_results if r["passes_hp"])
    seeds_hf   = sum(
        1 for r in all_seed_results
        if not any(c["precision"] >= HF_PRECISION for c in r["curve"]) or
           r["cov_at_50"] < HF_MIN_COVERAGE_AT_50
    )

    if seeds_pass >= HP_MIN_SEEDS:
        verdict = "HARD_PASS"
    elif seeds_hf >= HP_MIN_SEEDS:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    avg_knee = float(np.mean([r["knee"] for r in all_seed_results]))

    verdict_msg = (
        f"PP31-2A PRECISION COVERAGE: verdict={verdict} | "
        f"{seeds_pass}/{len(all_seed_results)} seeds pass HP | "
        f"avg_knee={avg_knee:.3f} | "
        f"HP: prec>=0.92 at cov>=0.60 at some tau AND knee>=0.20 in >=4/5 seeds | "
        f"HF: no tau achieves prec>=0.80 OR cov<0.10 at tau<=0.50 in >=4/5 seeds"
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "seeds_pass": seeds_pass,
        "seeds_hf": seeds_hf,
        "seeds_total": len(all_seed_results),
        "avg_knee": avg_knee,
        "all_seed_results": all_seed_results,
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
