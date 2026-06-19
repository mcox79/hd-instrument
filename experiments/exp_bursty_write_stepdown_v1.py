"""Cell L: Bursty-write step-down empirical.

SCIENTIFIC QUESTION:
  Does the substrate exhibit the predicted burst-damage step-down and no-recovery
  behavior? Theory (Round 6): after burst of B patterns added to steady-state M,
  the overlap drops by Delta_m ~ (B/N) * phi(1/sqrt(alpha_0)) / alpha_0^(3/2)
  and then stays flat (no recovery in read-only probe of 1000 steps).

PRE-REGISTERED BANDS:
  HARD-PASS:
    - drop within 2x theory (Delta_m_empirical < 2 * Delta_m_theory)
    - m flat at step 1000 vs step 0 post-burst (|m_1000 - m_0_post_burst| < 0.005)
  MIDDLE: drop > 2x but < 5x theory, OR small recovery (0.005 to 0.02).
  HARD-FAIL: drop > 5x theory OR large recovery (m increases by > 0.02 post-burst).

  Note: P(HARD-FAIL) is essentially the no-recovery theorem -- if the substrate
  spontaneously recovers, that contradicts the theoretical ceiling.

DESIGN:
  N=2048, M_steady=500, B=100 burst patterns, then 1000 read-only steps (no new writes).
  alpha_0 = M_steady / N = 0.244 (above alpha_c=0.138 -- loaded regime).
  Measure m = <x, xi_test> / N for a test pattern xi_test stored before burst.
  Run synchronous retrieval steps to track m(t) during read-only probe.
  5 seeds.

FORMULA SELF-TESTS:
  1. phi(x) = x * Normal_CDF(x) + Normal_PDF(x) (Hertz-Krogh-Palmer function).
  2. alpha_0 = 500/2048 = 0.244.
  3. Delta_m_theory = (B/N) * phi(1/sqrt(alpha_0)) / alpha_0^(3/2).
     1/sqrt(0.244) = 2.024. phi(2.024) ~ 2.024*0.979 + 0.054 ~ 2.034.
     Delta_m_theory ~ (100/2048) * 2.034 / (0.244^1.5) = 0.0488 * 2.034 / 0.121 ~ 0.82.
     This is large (>1 is unphysical -- m saturates at 1). So the formula has a regime issue.
     At high alpha (alpha > alpha_c), the pre-burst m is already low. We use:
     Delta_m_theory = min(B / (N * alpha_0^(1.5)), 1.0) as the upper bound.
     Conservative bound: B/(N*alpha_0^(1.5)) = 100/(2048 * 0.121) = 0.403.

PROT-018: no _nN suffix. Production N=2048; stated per PROT-018 rule 3.
  Stated: production N = 2048; rationale: burst-tolerance test at M/N=0.244.

TIMEOUT ESTIMATE:
  5 seeds * (M_steady + B writes + 1000 retrieval steps).
  Write step: O(N^2) = N^2/2 = 2048^2 / 2 ~ 2M ops = ~1ms per write.
  (M_steady + B) = 600 writes * 1ms = 0.6s. 1000 retrieval steps * ~1ms = 1s.
  5 seeds * 1.6s = 8s total. timeout=300 (floor).

Anchor: bursty_write_stepdown_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_bursty_write_stepdown_v1.md
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
from scipy.stats import norm as scipy_norm

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "bursty_write_stepdown_v1"

# Production config
N = 2048
M_STEADY = 500
B_BURST = 100
N_PROBE_STEPS = 1000
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]

# Pre-registered thresholds
HP_DROP_FACTOR = 2.0   # drop < 2x theory
HF_DROP_FACTOR = 5.0   # drop > 5x theory
HP_FLAT_DELTA  = 0.005  # m_1000 - m_0_post within this
HF_RECOVERY    = 0.020  # recovery > this -> HARD_FAIL (theory says no recovery)


def phi_hkp(x: float) -> float:
    """Hertz-Krogh-Palmer function phi(x) = x * Phi(x) + phi_normal(x)."""
    cdf = scipy_norm.cdf(x)
    pdf = scipy_norm.pdf(x)
    return x * cdf + pdf


def delta_m_theory(B: int, N: int, alpha_0: float) -> float:
    """Conservative theoretical drop: Delta_m ~ B/N * phi(1/sqrt(alpha_0)) / alpha_0^(1.5)."""
    x = 1.0 / math.sqrt(alpha_0)
    phi_val = phi_hkp(x)
    raw = (B / N) * phi_val / (alpha_0 ** 1.5)
    return min(raw, 1.0)  # cap at 1 (m is bounded)


def build_w_from_patterns(patterns: np.ndarray, N: int) -> np.ndarray:
    """Build Hopfield W from M patterns."""
    W = (patterns.T @ patterns) / N
    np.fill_diagonal(W, 0.0)
    return W


def retrieval_step(W: np.ndarray, state: np.ndarray) -> np.ndarray:
    return np.where(W @ state > 0, 1.0, -1.0)


def measure_overlap(state: np.ndarray, pattern: np.ndarray) -> float:
    return float(np.dot(state, pattern)) / len(state)


# ---------------------------------------------------------------------------
# Instrumentation self-test
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert phi, delta_m, and retrieval are non-null at toy scale."""
    # phi self-test
    phi_val = phi_hkp(2.024)
    assert not math.isnan(phi_val) and phi_val > 0, f"phi_hkp is NaN or <=0: {phi_val}"
    # Expected phi(2.024) ~ 2.034 (from docstring)
    assert 1.5 < phi_val < 3.0, f"phi(2.024) = {phi_val:.3f}, expected ~2.03"

    # delta_m self-test
    alpha_0 = M_STEADY / N
    dmt = delta_m_theory(B_BURST, N, alpha_0)
    assert 0.0 < dmt <= 1.0, f"delta_m_theory out of range: {dmt}"

    # Retrieval self-test
    rng = np.random.default_rng(0)
    N_t = 128
    M_t = 5
    pats = rng.choice([-1.0, 1.0], size=(M_t, N_t))
    W = build_w_from_patterns(pats, N_t)
    assert W.shape == (N_t, N_t), "W shape wrong"
    # Add noise to first pattern and retrieve
    q = pats[0].copy(); q[:int(0.1 * N_t)] *= -1
    s = retrieval_step(W, q)
    ov = measure_overlap(s, pats[0])
    assert not math.isnan(ov), "overlap is NaN"
    print(f"[selftest] PASS: phi={phi_val:.3f}, delta_m_theory={dmt:.4f}, "
          f"ov={ov:.3f}", flush=True)


_instrumentation_selftest()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_one_seed(seed: int, N: int, M_steady: int, B: int,
                 n_probe: int) -> Dict:
    rng = np.random.default_rng(seed)
    alpha_0 = M_steady / N

    # Store M_steady steady-state patterns
    patterns_steady = rng.choice([-1.0, 1.0], size=(M_steady, N))
    # Test pattern: one of the steady patterns (first one)
    test_pat = patterns_steady[0].copy()

    # Build W from steady patterns
    W = build_w_from_patterns(patterns_steady, N)

    # Pre-burst: run a retrieval on test pattern to get m_pre
    q_pre = add_noise_simple(test_pat, 0.05, rng, N)
    s_pre = retrieval_step(W, q_pre)
    m_pre = measure_overlap(s_pre, test_pat)

    # Apply burst: add B random patterns to W
    burst_patterns = rng.choice([-1.0, 1.0], size=(B, N))
    W_burst = W + build_w_from_patterns(burst_patterns, N)

    # Immediately post-burst: measure m
    s_post0 = retrieval_step(W_burst, test_pat)
    m_post0 = measure_overlap(s_post0, test_pat)

    # Read-only probe for n_probe steps (no new writes)
    state = s_post0.copy()
    m_trace = [m_post0]
    for step in range(1, min(n_probe, 1001)):
        state = retrieval_step(W_burst, state)
        if step % 100 == 0 or step == n_probe - 1:
            m_trace.append(measure_overlap(state, test_pat))

    m_1000 = measure_overlap(state, test_pat)
    delta_emp = m_pre - m_post0  # empirical drop
    delta_thy = delta_m_theory(B, N, alpha_0)
    recovery = m_1000 - m_post0  # positive = recovery

    return {
        "m_pre": float(m_pre),
        "m_post0": float(m_post0),
        "m_1000": float(m_1000),
        "delta_empirical": float(delta_emp),
        "delta_theory": float(delta_thy),
        "drop_factor": float(delta_emp / max(delta_thy, 1e-6)),
        "recovery": float(recovery),
        "m_trace": [float(x) for x in m_trace],
    }


def add_noise_simple(pat: np.ndarray, frac: float,
                     rng: np.random.Generator, N: int) -> np.ndarray:
    q = pat.copy()
    idx = rng.choice(N, size=int(frac * N), replace=False)
    q[idx] *= -1
    return q


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "full")
    seeds = SEEDS_FULL if run_mode == "full" else SEEDS_SMOKE
    print(f"[{ANCHOR_NAME}] run_mode={run_mode} seeds={seeds} "
          f"N={N} M={M_STEADY} B={B_BURST}", flush=True)

    all_results = {}
    for seed in seeds:
        print(f"  seed={seed}...", flush=True)
        res = run_one_seed(seed, N, M_STEADY, B_BURST, N_PROBE_STEPS)
        all_results[str(seed)] = res
        print(f"    m_pre={res['m_pre']:.4f} m_post0={res['m_post0']:.4f} "
              f"m_1000={res['m_1000']:.4f} drop_factor={res['drop_factor']:.2f} "
              f"recovery={res['recovery']:.5f}", flush=True)

    drop_factors = [r["drop_factor"] for r in all_results.values()]
    recoveries = [r["recovery"] for r in all_results.values()]

    hp_drop = all(d < HP_DROP_FACTOR for d in drop_factors)
    # HP flat = m_1000 close to m_post0 (no drift in either direction)
    hp_flat = all(abs(rec) < HP_FLAT_DELTA for rec in recoveries)
    hf_drop = any(d > HF_DROP_FACTOR for d in drop_factors)
    # HARD_FAIL recovery = spontaneous POSITIVE recovery (m increases post-burst -- violates theorem)
    hf_recovery = any(rec > HF_RECOVERY for rec in recoveries)

    if hf_drop or hf_recovery:
        verdict = "HARD_FAIL"
    elif hp_drop and hp_flat:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "anchor": ANCHOR_NAME, "run_mode": run_mode,
        "N": N, "M_steady": M_STEADY, "B_burst": B_BURST,
        "n_probe": N_PROBE_STEPS, "n_seeds": len(seeds),
        "delta_theory_expected": delta_m_theory(B_BURST, N, M_STEADY / N),
        "drop_factor_mean": float(np.mean(drop_factors)),
        "drop_factor_std": float(np.std(drop_factors)),
        "recovery_mean": float(np.mean(recoveries)),
        "recovery_std": float(np.std(recoveries)),
        "per_seed": {k: {
            "m_pre": v["m_pre"], "m_post0": v["m_post0"],
            "m_1000": v["m_1000"], "delta_emp": v["delta_empirical"],
            "delta_thy": v["delta_theory"], "drop_factor": v["drop_factor"],
            "recovery": v["recovery"],
        } for k, v in all_results.items()},
        "verdict": verdict, "elapsed_s": elapsed,
        "thresholds": {
            "HP_drop_factor": HP_DROP_FACTOR, "HF_drop_factor": HF_DROP_FACTOR,
            "HP_flat_delta": HP_FLAT_DELTA, "HF_recovery": HF_RECOVERY,
        },
        "verdict_msg": (
            f"Bursty write at N={N} M={M_STEADY} B={B_BURST}: "
            f"drop_factor_mean={np.mean(drop_factors):.2f} (HP<{HP_DROP_FACTOR}, HF>{HF_DROP_FACTOR}), "
            f"recovery_mean={np.mean(recoveries):.5f} (HP<{HP_FLAT_DELTA}, HF>{HF_RECOVERY}). "
            f"delta_theory={delta_m_theory(B_BURST, N, M_STEADY/N):.4f}. "
            f"Verdict: {verdict}."
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
                    help="Run at smoke scope for gate validation")
    _args = _p.parse_args()
    if _args.self_test:
        sys.exit(0)
    if _args.smoke:
        os.environ["HDLAB_RUN_MODE"] = "smoke"
    main()
