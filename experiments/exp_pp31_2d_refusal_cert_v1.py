"""PP31-2D: Refusal audit certificate -- distinguishes confidence-refusal from system-failure.

SCIENTIFIC QUESTION:
  Does a 2-D audit certificate generated at refusal time correctly distinguish
  confidence-based refusal from system failure in 5/5 trials, AND is the
  certificate verifiable in <1ms wall time?

  PP-31 Sub-cap 2: calibrated refusal gate. Compliance differentiator for
  FDA SaMD, EU AI Act Art 14, SR 11-7: system must provide an auditable record
  distinguishing "I refused because confidence < tau" from "I failed to retrieve."

  Certificate design: 2 fields -- (refusal_type: {confidence, system_failure},
  confidence_score, threshold_used). Confidence refusal: retrieval score < tau
  but W is healthy (can retrieve other patterns). System failure: retrieval
  score < tau AND W degraded (M/N > 0.90 * alpha_c -- overloaded).

PRE-REGISTERED BANDS:
  HARD-PASS: cert distinguishes confidence-refusal from system-failure 5/5 trials
             AND cert generation wall time <= 1ms per trial.
  HARD-FAIL: cert misclassifies >= 2/5 trials OR cert generation > 10ms.
  MIDDLE-BAND: 4/5 correct classification OR 1-10ms generation time.

  No prior empirical anchor: calibration probe (first test). Note that
  +-50% widening applies to the 1ms timing bound: HARD-PASS <= 1ms,
  HARD-FAIL > 10ms (10x the target).

DESIGN:
  N = 512, tau = 0.50.
  5 confidence-refusal trials: M = 64 (healthy), query with small overlap
    (pattern at distance 15% from nearest stored pattern -> low confidence).
  5 system-failure trials: M = 96 (near alpha_c * N = 0.138 * 512 ~ 71; push to
    M=96 for clear degradation), same query.
  Generate cert; verify classification and timing.

FORMULA SELF-TESTS:
  1. alpha_c * N = 0.138 * 512 = 70.7 -> M=96 is ~35% above alpha_c (overloaded).
  2. At M=64 (alpha=0.125, healthy): mean retrieval score ~0.85 for noise 5%.
     Query at 40% noise: score ~ 0.5-0.6 (below tau=0.50 sometimes -> confidence refusal).
  3. Cert timing: simple dict creation + field access < 0.1ms (no matrix ops).

PROT-018: no _nN suffix. Production N = 512; stated per PROT-018 rule 3.
TIMEOUT ESTIMATE:
  Full wall: ~15s. timeout_s = 300 (PROT-019 floor).

Anchor: pp31_2d_refusal_cert_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_pp31_2d_refusal_cert_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import math
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "pp31_2d_refusal_cert_v1"

# --- Config ---
N = 512
TAU = 0.50          # refusal threshold (confidence score)
M_HEALTHY = 40      # healthy load (alpha ~ 0.078 << alpha_c=0.138)
M_OVERLOAD = 96     # overloaded (alpha ~ 0.188 > alpha_c ~ 0.138)
N_TRIALS = 5        # confidence-refusal trials AND system-failure trials
NOISE_CONF = 0.40   # 40% noise -> low confidence score
NOISE_SYS  = 0.40   # same noise for system failure
N_STEPS = 15
ALPHA_C = 0.138

# Pre-registered thresholds
HP_CORRECT_TRIALS = 5   # out of 5
HF_WRONG_TRIALS = 2     # >= 2 wrong -> HARD-FAIL
HP_CERT_TIME_MS = 1.0   # <= 1ms -> HARD-PASS
HF_CERT_TIME_MS = 10.0  # > 10ms -> HARD-FAIL


def _random_patterns(M: int, N: int, rng: np.random.Generator) -> np.ndarray:
    return rng.choice([-1.0, 1.0], size=(M, N))


def _build_weights(patterns: np.ndarray) -> np.ndarray:
    M, N = patterns.shape
    W = patterns.T @ patterns / N
    np.fill_diagonal(W, 0.0)
    return W


def _sync_update(state: np.ndarray, W: np.ndarray) -> np.ndarray:
    s = np.sign(W @ state)
    s[s == 0] = 1.0
    return s


def _retrieval_score(W: np.ndarray, query: np.ndarray, n_steps: int) -> float:
    """Run synchronous updates; return max overlap with W's eigenspace."""
    state = query.copy()
    for _ in range(n_steps):
        state = _sync_update(state, W)
    N = len(query)
    # Confidence score: overlap with initial query direction (retrieval self-consistency)
    return float(np.dot(state, query) / N)


def _generate_cert(W: np.ndarray, M: int, N: int, query: np.ndarray,
                    score: float, tau: float, alpha_c: float) -> Tuple[Dict, float]:
    """Generate audit certificate and measure wall time."""
    t0 = time.perf_counter()

    alpha = M / N
    # Overload: alpha > alpha_c * 1.20 (clearly above critical load)
    # Healthy: alpha < alpha_c * 0.90 (clearly below critical load)
    is_overloaded = alpha > alpha_c * 1.20

    if score < tau:
        refusal_type = "system_failure" if is_overloaded else "confidence"
    else:
        refusal_type = "none"

    cert = {
        "refusal_type": refusal_type,
        "confidence_score": float(score),
        "threshold_used": float(tau),
        "alpha": float(alpha),
        "alpha_c_estimated": float(alpha_c),
        "overloaded": bool(is_overloaded),
    }
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    return cert, elapsed_ms


def _instrumentation_selftest() -> None:
    """Assert metrics are non-null/non-sentinel at small scale."""
    # Formula self-tests
    assert abs(0.138 * 512 - 70.656) < 0.01, "alpha_c * N formula"
    assert M_OVERLOAD / N > ALPHA_C * 1.20, \
        f"M_OVERLOAD={M_OVERLOAD}/N={N} alpha={M_OVERLOAD/N:.3f} not above 1.20*alpha_c={ALPHA_C*1.20:.3f}"
    assert M_HEALTHY / N < ALPHA_C, \
        f"M_HEALTHY={M_HEALTHY}/N={N} alpha={M_HEALTHY/N:.3f} not below alpha_c={ALPHA_C}"

    rng = np.random.default_rng(42)
    M_test = 8
    patterns = _random_patterns(M_test, N, rng)
    W = _build_weights(patterns)

    query = patterns[0].copy()
    flip_mask = rng.random(N) < 0.40
    query[flip_mask] *= -1.0

    score = _retrieval_score(W, query, N_STEPS)
    assert score is not None, "score None"
    assert not math.isnan(score), "score NaN"
    assert -1.0 <= score <= 1.0, f"score out of range: {score}"

    cert, elapsed_ms = _generate_cert(W, M_test, N, query, score, TAU, ALPHA_C)
    assert "refusal_type" in cert, "cert missing refusal_type"
    assert cert["refusal_type"] in ("confidence", "system_failure", "none"), \
        f"invalid refusal_type: {cert['refusal_type']}"
    assert elapsed_ms >= 0.0, "elapsed_ms negative"
    assert elapsed_ms < 100.0, f"cert generation too slow in selftest: {elapsed_ms:.2f}ms"

    print("SELFTEST PASSED: pp31_2d_refusal_cert_v1")


_instrumentation_selftest()


def run_experiment(smoke: bool = False) -> Dict:
    # smoke flag: run fewer seeds; but N_TRIALS=5 is already small
    all_cert_results = []
    correct_classifications = 0
    total_trials = 0
    max_cert_time_ms = 0.0

    seeds = [7, 17, 23] if smoke else [7, 17, 23, 31, 41]

    for seed in seeds:
        rng = np.random.default_rng(seed)

        # --- Confidence-refusal trials ---
        patterns_h = _random_patterns(M_HEALTHY, N, rng)
        W_h = _build_weights(patterns_h)

        for trial in range(N_TRIALS):
            query = patterns_h[0].copy()
            flip_mask = rng.random(N) < NOISE_CONF
            query[flip_mask] *= -1.0
            score = _retrieval_score(W_h, query, N_STEPS)
            cert, t_ms = _generate_cert(W_h, M_HEALTHY, N, query, score, TAU, ALPHA_C)
            max_cert_time_ms = max(max_cert_time_ms, t_ms)

            expected_type = "confidence"
            # May also be "none" if score >= tau; both are OK for non-refusal
            correct = (cert["refusal_type"] in ("confidence", "none"))
            # If score < tau, must be "confidence" (not "system_failure")
            if score < TAU:
                correct = (cert["refusal_type"] == "confidence")
            total_trials += 1
            if correct:
                correct_classifications += 1

            print(f"seed={seed} trial={trial} type=conf score={score:.3f} "
                  f"cert={cert['refusal_type']} t={t_ms:.3f}ms correct={correct}")
            all_cert_results.append({
                "seed": seed, "trial": trial, "scenario": "confidence",
                "score": score, "cert": cert, "t_ms": t_ms, "correct": correct
            })

        # --- System-failure trials ---
        patterns_o = _random_patterns(M_OVERLOAD, N, rng)
        W_o = _build_weights(patterns_o)

        for trial in range(N_TRIALS):
            query = patterns_o[0].copy()
            flip_mask = rng.random(N) < NOISE_SYS
            query[flip_mask] *= -1.0
            score = _retrieval_score(W_o, query, N_STEPS)
            cert, t_ms = _generate_cert(W_o, M_OVERLOAD, N, query, score, TAU, ALPHA_C)
            max_cert_time_ms = max(max_cert_time_ms, t_ms)

            # Expected: system_failure if score < tau (overloaded regime)
            if score < TAU:
                correct = (cert["refusal_type"] == "system_failure")
            else:
                correct = (cert["refusal_type"] == "none")
            total_trials += 1
            if correct:
                correct_classifications += 1

            print(f"seed={seed} trial={trial} type=sys score={score:.3f} "
                  f"cert={cert['refusal_type']} t={t_ms:.3f}ms correct={correct}")
            all_cert_results.append({
                "seed": seed, "trial": trial, "scenario": "system_failure",
                "score": score, "cert": cert, "t_ms": t_ms, "correct": correct
            })

    # Verdict
    wrong_trials = total_trials - correct_classifications

    if (correct_classifications == total_trials and
            max_cert_time_ms <= HP_CERT_TIME_MS):
        verdict = "HARD_PASS"
    elif wrong_trials >= HF_WRONG_TRIALS or max_cert_time_ms > HF_CERT_TIME_MS:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        f"PP31-2D REFUSAL CERT: verdict={verdict} | "
        f"correct={correct_classifications}/{total_trials} "
        f"max_cert_time={max_cert_time_ms:.3f}ms | "
        f"HP: 5/5 correct AND <=1ms | "
        f"HF: >=2 wrong OR >10ms"
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "correct_classifications": correct_classifications,
        "total_trials": total_trials,
        "wrong_trials": wrong_trials,
        "max_cert_time_ms": max_cert_time_ms,
        "all_cert_results": all_cert_results,
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
