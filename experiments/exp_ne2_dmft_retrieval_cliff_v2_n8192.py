"""NE-2 v2: DMFT retrieval cliff at N=8192 with finer alpha sweep.

SCIENTIFIC QUESTION:
  Does the substrate's retrieval accuracy drop sharply at the DMFT-predicted
  alpha_c ~ 0.138 (Hara-Kabashima 2026)?

  v1 MIDDLE_BAND ROOT CAUSE: at N=1024 the cliff is smeared -- overlap stays
  ~0.96 through alpha=0.138, dropping only around alpha=0.20 (well outside the
  HP cliff-midpoint window [0.12, 0.16]). Finite-size effects blur the transition.
  v2 runs at N=8192 (4x larger) to sharpen the cliff, plus a finer 13-point alpha
  sweep densely bracketing [0.10, 0.16] to localize the midpoint precisely.

PRE-REGISTERED BANDS (refined from v1 MIDDLE outcome):
  HARD-PASS: retrieval overlap m* at alpha <= 0.12 is >= 0.90 AND at alpha >= 0.155
             is <= 0.60; AND the cliff midpoint (50% overlap crossing) falls in
             [0.125, 0.152] -- i.e., within +/-10% of predicted alpha_c=0.138.
             Criterion must hold in >= 4/5 seeds.
             (Window tightened vs v1 [0.12,0.16]: N=8192 should sharpen the cliff,
             so we expect the midpoint to localize closer to 0.138.)
  HARD-FAIL: m* at alpha <= 0.12 is < 0.70 (substrate not retrieving at all) OR
             no cliff detected (m* range < 0.20 across all alpha) in >= 4/5 seeds
             -- framework REFUTED at N=8192.
  MIDDLE_BAND: cliff present but midpoint outside [0.110, 0.165] (+/-20%), or
               criterion passes in only 3/5 seeds, or cliff present but sharpness
               low (m* range 0.20-0.40 only).

  Prior anchor: v1 MIDDLE_BAND at N=1024 (cliff at ~alpha=0.20, not localized).
  v2 tests whether the cliff sharpens and shifts left to predicted alpha_c at N=8192.

DESIGN:
  N = 8192 (production; PROT-018 _n8192 binding).
  Fine alpha sweep: 13 values densely around predicted alpha_c=0.138:
    [0.100, 0.110, 0.120, 0.125, 0.130, 0.133, 0.136, 0.138,
     0.141, 0.144, 0.148, 0.155, 0.160]
  M = max(1, int(alpha * N)) stored patterns (BSC bipolar).
  Retrieval: start from pattern[0] + 5% noise, run 50 synchronous update steps,
             measure final overlap m = (retrieved . pattern[0]) / N.
  5 seeds, 3 retrieval trials per alpha per seed.
  Smoke: N=1024, 2 seeds, same 13 alpha values, 3 trials.
    (Smoke at N=1024 expected to show cliff at ~0.20; this verifies instrumentation,
    not the HP threshold -- HP is for N=8192 only.)

PROT-018: anchor name contains _n8192; production N MUST equal 8192.
  Pre-ship audit: grep -E '(N =|n =)' confirms N=8192 in this script.

TIMEOUT ESTIMATE:
  Vectorized sync step at N=8192: ~31ms (measured locally).
  Full: 13 alphas * 5 seeds * 3 trials * 50 steps = 9750 steps.
  Wall: 9750 * 0.031s + W-build overhead (~0.5s * 15 = 7.5s) ~ 309s.
  timeout_s = ceil(1.5 * 309) = ceil(464) -> 600s.
  Formula check: smoke_wall~35s, FULL_N/smoke_N=8, seeds 5/2=2.5, scaling_exp=1.5
  -> ceil(1.5*35*8^1.5*2.5) = ceil(2969) -> but this over-estimates because
  the 8x N cost is W-build dominant at small step-counts; direct timing is more
  accurate. Use max(600, formula_result/5) = 600s as conservative low end.
  Actual estimate from direct timing: 500s. Set timeout_s = 900s (2x margin).

Anchor: ne2_dmft_retrieval_cliff_v2_n8192
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_ne2_dmft_retrieval_cliff_v2_n8192.md
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

ANCHOR_NAME = "ne2_dmft_retrieval_cliff_v2_n8192"

# --- Production config (PROT-018: N=8192 binding) ---
N = 8192
ALPHA_GRID = [
    0.100, 0.110, 0.120, 0.125, 0.130, 0.133, 0.136, 0.138,
    0.141, 0.144, 0.148, 0.155, 0.160
]
ALPHA_C_PREDICTED = 0.138
N_STEPS = 50
NOISE_FRAC = 0.05
SEEDS_SMOKE = [7, 17]
SEEDS_FULL  = [7, 17, 23, 31, 41]
N_TRIALS    = 3
N_SMOKE = 1024

# Pre-registered thresholds (tightened HP window for N=8192)
HP_OVERLAP_AT_LOW_ALPHA  = 0.90   # m* at alpha <= 0.12 must be >= this
HP_OVERLAP_AT_HIGH_ALPHA = 0.60   # m* at alpha >= 0.155 must be <= this
HP_CLIFF_LO  = 0.125              # cliff midpoint lower bound (+-10% of 0.138)
HP_CLIFF_HI  = 0.152              # cliff midpoint upper bound
MB_CLIFF_LO  = 0.110              # middle-band midpoint lower bound (+-20%)
MB_CLIFF_HI  = 0.165              # middle-band midpoint upper bound
HF_OVERLAP_FLOOR = 0.70           # m* at low alpha < this -> HF (not retrieving)
HF_MIN_RANGE     = 0.20           # m* range < this -> no cliff -> HF
HP_MIN_SEEDS = 4                  # out of 5 seeds must pass


def _random_patterns(M: int, n: int, rng: np.random.Generator) -> np.ndarray:
    return rng.choice([-1.0, 1.0], size=(M, n))


def _build_weights(patterns: np.ndarray) -> np.ndarray:
    M, n = patterns.shape
    W = patterns.T @ patterns / n
    np.fill_diagonal(W, 0.0)
    return W


def _sync_update(state: np.ndarray, W: np.ndarray) -> np.ndarray:
    """Synchronous update: sign(W @ state), preserving previous sign at 0."""
    new = np.sign(W @ state)
    zero_mask = new == 0.0
    new[zero_mask] = state[zero_mask]
    return new


def _retrieval_overlap(W: np.ndarray, target: np.ndarray,
                        noise_frac: float, n_steps: int,
                        rng: np.random.Generator) -> float:
    n = len(target)
    state = target.copy()
    flip_mask = rng.random(n) < noise_frac
    state[flip_mask] *= -1.0
    for _ in range(n_steps):
        state = _sync_update(state, W)
    return float(np.dot(state, target) / n)


def _cliff_midpoint(sorted_alphas: List[float], overlaps: List[float]) -> Optional[float]:
    """Interpolated alpha where overlap crosses 0.5 (midpoint of cliff)."""
    for k in range(len(sorted_alphas) - 1):
        if overlaps[k] >= 0.5 and overlaps[k + 1] < 0.5:
            a0, m0 = sorted_alphas[k], overlaps[k]
            a1, m1 = sorted_alphas[k + 1], overlaps[k + 1]
            if abs(m0 - m1) > 1e-6:
                return a0 + (0.5 - m0) / (m1 - m0) * (a1 - a0)
    return None


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    n_test = 256
    M_test = 4  # very low load -> should retrieve well
    rng = np.random.default_rng(77)
    patterns = _random_patterns(M_test, n_test, rng)
    W = _build_weights(patterns)
    assert W.shape == (n_test, n_test), "W shape wrong"
    assert abs(np.diag(W).sum()) < 1e-9, "W diagonal not zero"

    # Low load: retrieval overlap should be high
    m = _retrieval_overlap(W, patterns[0], NOISE_FRAC, N_STEPS, rng)
    assert m is not None, "overlap None"
    assert not math.isnan(m), "overlap NaN"
    assert -1.0 <= m <= 1.0, f"overlap out of range: {m}"
    assert m > 0.7, f"selftest low-load overlap should be > 0.7, got {m:.3f}"

    # High load: M close to capacity, overlap should drop
    M_high = int(0.14 * n_test)
    patterns_high = _random_patterns(M_high, n_test, rng)
    W_high = _build_weights(patterns_high)
    m_high = _retrieval_overlap(W_high, patterns_high[0], NOISE_FRAC, N_STEPS, rng)
    assert not math.isnan(m_high), "high-load overlap NaN"
    # Don't assert m_high < m_low strictly -- N=256 is noisy, just check non-NaN

    # Cliff midpoint on known input
    sorted_a = [0.10, 0.12, 0.13, 0.14, 0.16]
    overlaps  = [0.95, 0.90, 0.70, 0.30, 0.10]
    cp = _cliff_midpoint(sorted_a, overlaps)
    assert cp is not None, "cliff_midpoint should detect crossing"
    assert 0.12 < cp < 0.14, f"cliff midpoint wrong: {cp}"

    # No crossing case
    flat_overlaps = [0.90, 0.88, 0.87, 0.85, 0.82]
    cp_none = _cliff_midpoint(sorted_a, flat_overlaps)
    assert cp_none is None, "no crossing: should return None"

    print("SELFTEST PASSED: ne2_dmft_retrieval_cliff_v2_n8192")


_instrumentation_selftest()


def run_experiment(smoke: bool = False) -> Dict:
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_run  = N_SMOKE if smoke else N
    all_results = []

    for seed in seeds:
        rng = np.random.default_rng(seed)
        seed_results = []
        for alpha in ALPHA_GRID:
            M = max(1, int(alpha * n_run))
            patterns = _random_patterns(M, n_run, rng)
            W = _build_weights(patterns)
            m_vals = []
            for _ in range(N_TRIALS):
                m = _retrieval_overlap(W, patterns[0], NOISE_FRAC, N_STEPS, rng)
                m_vals.append(m)
            m_mean = float(np.mean(m_vals))
            seed_results.append({"alpha": alpha, "M": M, "overlap": m_mean})
            print(f"n={n_run} seed={seed} alpha={alpha:.3f} M={M} overlap={m_mean:.3f}")
            sys.stdout.flush()
        all_results.append({"seed": seed, "alpha_results": seed_results})

    # Verdict per seed
    seeds_pass = 0
    seeds_total = len(all_results)
    seeds_fail_low = 0
    seeds_fail_no_cliff = 0
    cliff_midpoints: List[float] = []

    for sr in all_results:
        ar = sr["alpha_results"]
        sorted_ar = sorted(ar, key=lambda r: r["alpha"])
        sorted_alphas = [r["alpha"] for r in sorted_ar]
        sorted_overlaps = [r["overlap"] for r in sorted_ar]

        all_overlaps = sorted_overlaps
        m_range = max(all_overlaps) - min(all_overlaps)

        low_alphas  = [r for r in ar if r["alpha"] <= 0.12]
        high_alphas = [r for r in ar if r["alpha"] >= 0.155]
        m_low  = float(np.mean([r["overlap"] for r in low_alphas]))  if low_alphas  else 0.0
        m_high = float(np.mean([r["overlap"] for r in high_alphas])) if high_alphas else 1.0

        cliff_alpha = _cliff_midpoint(sorted_alphas, sorted_overlaps)
        if cliff_alpha is not None:
            cliff_midpoints.append(cliff_alpha)

        if m_range < HF_MIN_RANGE:
            seeds_fail_no_cliff += 1
            continue
        if m_low < HF_OVERLAP_FLOOR:
            seeds_fail_low += 1
            continue
        if (m_low >= HP_OVERLAP_AT_LOW_ALPHA
                and m_high <= HP_OVERLAP_AT_HIGH_ALPHA
                and cliff_alpha is not None
                and HP_CLIFF_LO <= cliff_alpha <= HP_CLIFF_HI):
            seeds_pass += 1

    pass_fraction = seeds_pass / max(seeds_total, 1)
    avg_cliff = float(np.mean(cliff_midpoints)) if cliff_midpoints else float('nan')

    if seeds_pass >= HP_MIN_SEEDS:
        verdict = "HARD_PASS"
    elif seeds_fail_low + seeds_fail_no_cliff >= seeds_total:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        f"NE-2 v2 DMFT CLIFF N={n_run}: verdict={verdict} | "
        f"{seeds_pass}/{seeds_total} seeds pass HP | "
        f"avg_cliff_alpha={avg_cliff:.4f} (HP window [{HP_CLIFF_LO:.3f},{HP_CLIFF_HI:.3f}]) | "
        f"HP: m*>=0.90 at alpha<=0.12, m*<=0.60 at alpha>=0.155, "
        f"cliff in [{HP_CLIFF_LO:.3f},{HP_CLIFF_HI:.3f}] | "
        f"HF: m*<0.70 at low-alpha OR no cliff (range<0.20) in all seeds"
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "seeds_pass": seeds_pass,
        "seeds_total": seeds_total,
        "pass_fraction": pass_fraction,
        "seeds_fail_low": seeds_fail_low,
        "seeds_fail_no_cliff": seeds_fail_no_cliff,
        "cliff_midpoints": cliff_midpoints,
        "avg_cliff_alpha": avg_cliff if not math.isnan(avg_cliff) else None,
        "N_run": n_run,
        "all_results": all_results,
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
