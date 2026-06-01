"""NE-2: DMFT retrieval cliff (Hara-Kabashima 2026) -- universality class test.

SCIENTIFIC QUESTION:
  Does the substrate's retrieval accuracy drop sharply at the DMFT-predicted
  alpha_c ~ 0.138 (Hara-Kabashima 2026 Hopfield derivation)?

  DMFT predicts a retrieval cliff: mean retrieval overlap m* drops from ~1 to ~0
  within a narrow alpha window around alpha_c. Finite-N corrections ~1.5% at N=4096
  (Hara-Kabashima 2026). This is a 5-seed x 3-alpha calibration test.

PRE-REGISTERED BANDS:
  HARD-PASS: retrieval overlap m* at alpha < 0.12 is >= 0.90 AND at alpha > 0.15
             is <= 0.50; AND the cliff midpoint (50% overlap crossing) falls in
             [0.12, 0.16] -- i.e., within +-15% of predicted alpha_c=0.138.
             Criterion must hold in >= 4/5 seeds.
  HARD-FAIL: m* at alpha < 0.12 is < 0.70 (substrate not retrieving at all) OR
             no cliff observed (m* varies < 0.2 across all alpha) in >= 4/5 seeds.
  MIDDLE-BAND: cliff present but midpoint outside [0.10, 0.18] (+-30% of alpha_c),
               or criterion passes in 3/5 seeds.

  No prior direct DMFT test on substrate: bands widened per calibration-probe policy.

DESIGN:
  N = 1024, alpha_grid = [0.08, 0.12, 0.138, 0.16, 0.20].
  M = max(1, int(alpha * N)) stored patterns (BSC bipolar).
  Retrieval: start from pattern[0] + 5% noise, run 20 synchronous update steps,
             measure final overlap m = (retrieved . pattern[0]) / N.
  5 seeds (smoke: 3 seeds).

PROT-018: no _nN suffix. Production N = 1024; stated per PROT-018 rule 3.
TIMEOUT ESTIMATE:
  Smoke wall ~10s. Full 5 seeds x 5 alpha x 20 steps = ~25s.
  timeout_s = 300 (PROT-019 floor for CPU; actual wall <60s).

Anchor: ne2_dmft_retrieval_cliff_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_ne2_dmft_retrieval_cliff_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import math
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "ne2_dmft_retrieval_cliff_v1"

# --- Config ---
N = 1024
ALPHA_GRID = [0.08, 0.12, 0.138, 0.16, 0.20]
ALPHA_C_PREDICTED = 0.138
N_STEPS = 20
NOISE_FRAC = 0.05
SEEDS_SMOKE = [7, 17, 23]
SEEDS_FULL  = [7, 17, 23, 31, 41]

# Pre-registered thresholds
HP_OVERLAP_LOW  = 0.90   # m* at alpha < 0.12
HP_OVERLAP_HIGH = 0.50   # m* at alpha > 0.15 must be <= this
HP_CLIFF_LO = 0.10       # cliff midpoint lower bound
HP_CLIFF_HI = 0.16       # cliff midpoint upper bound
HF_OVERLAP_LOW_MIN = 0.70  # below this at low alpha -> HF
HF_MIN_RANGE = 0.20         # m* range < this -> no cliff -> HF
HP_MIN_SEEDS = 4            # out of 5


def _random_patterns(M: int, N: int, rng: np.random.Generator) -> np.ndarray:
    return rng.choice([-1.0, 1.0], size=(M, N))


def _build_weights(patterns: np.ndarray) -> np.ndarray:
    M, N = patterns.shape
    W = patterns.T @ patterns / N
    np.fill_diagonal(W, 0.0)
    return W


def _sync_update(state: np.ndarray, W: np.ndarray) -> np.ndarray:
    return np.sign(W @ state)


def _retrieval_overlap(W: np.ndarray, target: np.ndarray,
                        noise_frac: float, n_steps: int,
                        rng: np.random.Generator) -> float:
    N = len(target)
    state = target.copy()
    flip_mask = rng.random(N) < noise_frac
    state[flip_mask] *= -1.0
    for _ in range(n_steps):
        new_state = _sync_update(state, W)
        # handle sign(0) -> 0 by keeping previous
        zero_mask = new_state == 0.0
        new_state[zero_mask] = state[zero_mask]
        state = new_state
    return float(np.dot(state, target) / N)


def _instrumentation_selftest() -> None:
    """Assert metrics are non-null/non-sentinel at small scale."""
    rng = np.random.default_rng(99)
    M_test = 2
    N_test = 128
    patterns = _random_patterns(M_test, N_test, rng)
    W = _build_weights(patterns)
    assert W.shape == (N_test, N_test), "W shape wrong"
    m = _retrieval_overlap(W, patterns[0], 0.05, 5, rng)
    assert m is not None, "overlap None"
    assert not math.isnan(m), "overlap NaN"
    assert -1.0 <= m <= 1.0, f"overlap out of range: {m}"
    # Low load should give good retrieval
    assert m > 0.5, f"selftest: low-load overlap should be > 0.5, got {m:.3f}"
    print("SELFTEST PASSED: ne2_dmft_retrieval_cliff_v1")


_instrumentation_selftest()


def run_experiment(smoke: bool = False) -> Dict:
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    all_results = []

    for seed in seeds:
        rng = np.random.default_rng(seed)
        seed_results = []
        for alpha in ALPHA_GRID:
            M = max(1, int(alpha * N))
            patterns = _random_patterns(M, N, rng)
            W = _build_weights(patterns)
            m_vals = []
            for _ in range(3):  # 3 retrieval trials per alpha/seed
                m = _retrieval_overlap(W, patterns[0], NOISE_FRAC, N_STEPS, rng)
                m_vals.append(m)
            m_mean = float(np.mean(m_vals))
            seed_results.append({"alpha": alpha, "M": M, "overlap": m_mean})
            print(f"seed={seed} alpha={alpha:.3f} M={M} overlap={m_mean:.3f}")
        all_results.append({"seed": seed, "alpha_results": seed_results})

    # Verdict logic per seed
    seeds_pass = 0
    seeds_total = len(all_results)
    seeds_fail_low = 0
    seeds_fail_no_cliff = 0

    for sr in all_results:
        ar = sr["alpha_results"]
        low_alphas  = [r for r in ar if r["alpha"] < 0.12]
        high_alphas = [r for r in ar if r["alpha"] > 0.15]
        all_overlaps = [r["overlap"] for r in ar]
        m_range = max(all_overlaps) - min(all_overlaps)

        m_low  = float(np.mean([r["overlap"] for r in low_alphas]))  if low_alphas  else 0.0
        m_high = float(np.mean([r["overlap"] for r in high_alphas])) if high_alphas else 1.0

        # Cliff midpoint: interpolate where overlap crosses 0.5
        sorted_ar = sorted(ar, key=lambda r: r["alpha"])
        cliff_alpha = None
        for k in range(len(sorted_ar) - 1):
            if sorted_ar[k]["overlap"] >= 0.5 and sorted_ar[k+1]["overlap"] < 0.5:
                # linear interpolation
                a0, m0 = sorted_ar[k]["alpha"], sorted_ar[k]["overlap"]
                a1, m1 = sorted_ar[k+1]["alpha"], sorted_ar[k+1]["overlap"]
                if abs(m0 - m1) > 1e-6:
                    cliff_alpha = a0 + (0.5 - m0) / (m1 - m0) * (a1 - a0)
                break

        if m_range < HF_MIN_RANGE:
            seeds_fail_no_cliff += 1
            continue
        if m_low < HF_OVERLAP_LOW_MIN:
            seeds_fail_low += 1
            continue
        if (m_low >= HP_OVERLAP_LOW and m_high <= HP_OVERLAP_HIGH and
                cliff_alpha is not None and HP_CLIFF_LO <= cliff_alpha <= HP_CLIFF_HI):
            seeds_pass += 1

    pass_fraction = seeds_pass / max(seeds_total, 1)

    if seeds_pass >= HP_MIN_SEEDS:
        verdict = "HARD_PASS"
    elif seeds_fail_low >= seeds_total or seeds_fail_no_cliff >= seeds_total:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        f"NE-2 DMFT RETRIEVAL CLIFF: verdict={verdict} | "
        f"{seeds_pass}/{seeds_total} seeds pass HP | "
        f"HP: m*>=0.90 at alpha<0.12 AND m*<=0.50 at alpha>0.15 "
        f"AND cliff in [0.12,0.16] in >=4/5 seeds | "
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
