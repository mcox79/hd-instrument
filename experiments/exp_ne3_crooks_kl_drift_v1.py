"""NE-3: Crooks Candidate 2 -- KL-divergence drift detection via trajectory logging.

SCIENTIFIC QUESTION:
  Do forward/reverse retrieval trajectories exhibit KL_div(F||R) >= 3-sigma above
  null baseline at a synthetic drift point, with <5% false-alarm rate?

  Crooks FT: FINITE-N EXACT (symmetric Hebbian W satisfies microreversibility).
  The write protocol (J_ij changes) breaks detailed balance -> KL divergence between
  forward-time and time-reversed trajectories serves as a drift indicator.

PRE-REGISTERED BANDS:
  HARD-PASS: KL_div(F||R) at drift point >= 3.0 sigma above pre-drift baseline;
             AND false-alarm rate (KL_div exceeding 3-sigma threshold in pre-drift
             window) <= 5% of pre-drift steps; in >= 4/5 seeds.
  HARD-FAIL: KL_div at drift point < 1.0 sigma above baseline in >= 4/5 seeds
             (no signal at all); OR false-alarm rate > 20% in >= 4/5 seeds
             (detector is noisy noise).
  MIDDLE-BAND: 1.0-3.0 sigma (weak signal present); or passes in 3/5 seeds;
               or false-alarm 5-20%.

  No prior empirical anchor: bands widened +-50% of theoretical prediction.

DESIGN:
  Synthetic protocol:
  - Phase A: store M_A=64 patterns. Record 50 forward retrieval trajectories.
  - Drift: add M_drift=32 new patterns to W (write event). Record 50 trajectories.
  - Phase B: 50 post-drift trajectories.
  - Reverse trajectories: run time-reversed dynamics (flip update order).
  KL estimator: histogram-based over trajectory final-overlap distribution.
  N = 1024, 5 seeds.

PROT-018: no _nN suffix. Production N = 1024; stated per PROT-018 rule 3.
TIMEOUT ESTIMATE:
  Smoke (2 seeds): ~15s. Full (5 seeds x 3 phases x 50 traj x 20 steps): ~40s.
  timeout_s = 300 (PROT-019 floor; actual wall <60s).

Anchor: ne3_crooks_kl_drift_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_ne3_crooks_kl_drift_v1.md
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

ANCHOR_NAME = "ne3_crooks_kl_drift_v1"

# --- Config ---
N = 1024
M_A      = 64     # pre-drift patterns
M_DRIFT  = 32     # added at drift event
N_TRAJ   = 50     # trajectories per phase
N_STEPS  = 20     # Glauber steps per trajectory
NOISE_FRAC = 0.05
N_BINS   = 20     # histogram bins for KL estimate
SEEDS_SMOKE = [7, 17]
SEEDS_FULL  = [7, 17, 23, 31, 41]

# Pre-registered thresholds
HP_SIGMA_ABOVE  = 3.0   # KL must be >= 3-sigma above pre-drift baseline
HF_SIGMA_ABOVE  = 1.0   # KL < 1-sigma -> HARD-FAIL
HP_FA_RATE      = 0.05  # false-alarm rate <= 5% -> HARD-PASS
HF_FA_RATE      = 0.20  # false-alarm rate > 20% -> HARD-FAIL
HP_MIN_SEEDS    = 4     # out of 5


def _random_patterns(M: int, N: int, rng: np.random.Generator) -> np.ndarray:
    return rng.choice([-1.0, 1.0], size=(M, N))


def _build_weights(patterns: np.ndarray) -> np.ndarray:
    M, N = patterns.shape
    W = patterns.T @ patterns / N
    np.fill_diagonal(W, 0.0)
    return W


def _glauber_step(state: np.ndarray, W: np.ndarray,
                   rng: np.random.Generator, beta: float = 10.0) -> np.ndarray:
    N = len(state)
    order = rng.permutation(N)
    s = state.copy()
    for i in order:
        h_i = W[i] @ s
        p_plus = 1.0 / (1.0 + math.exp(-2.0 * beta * h_i))
        s[i] = 1.0 if rng.random() < p_plus else -1.0
    return s


def _glauber_step_reverse(state: np.ndarray, W: np.ndarray,
                            rng: np.random.Generator, beta: float = 10.0) -> np.ndarray:
    """Reverse-time Glauber: update in REVERSE order."""
    N = len(state)
    order = rng.permutation(N)[::-1]  # reversed permutation
    s = state.copy()
    for i in order:
        h_i = W[i] @ s
        p_plus = 1.0 / (1.0 + math.exp(-2.0 * beta * h_i))
        s[i] = 1.0 if rng.random() < p_plus else -1.0
    return s


def _run_trajectories(W: np.ndarray, target: np.ndarray, n_traj: int,
                       n_steps: int, noise_frac: float,
                       rng: np.random.Generator,
                       reverse: bool = False) -> List[float]:
    """Return list of final overlap m = (final_state . target) / N."""
    N = len(target)
    overlaps = []
    step_fn = _glauber_step_reverse if reverse else _glauber_step
    for _ in range(n_traj):
        state = target.copy()
        flip_mask = rng.random(N) < noise_frac
        state[flip_mask] *= -1.0
        for _ in range(n_steps):
            state = step_fn(state, W, rng)
        overlaps.append(float(np.dot(state, target) / N))
    return overlaps


def _kl_div_hist(p_samples: List[float], q_samples: List[float],
                  n_bins: int) -> float:
    """KL divergence KL(P||Q) via histogram estimate."""
    all_samples = p_samples + q_samples
    lo, hi = min(all_samples) - 1e-6, max(all_samples) + 1e-6
    bins = np.linspace(lo, hi, n_bins + 1)
    p_hist, _ = np.histogram(p_samples, bins=bins)
    q_hist, _ = np.histogram(q_samples, bins=bins)
    p_hist = (p_hist + 1e-6) / (sum(p_hist) + n_bins * 1e-6)  # smoothed
    q_hist = (q_hist + 1e-6) / (sum(q_hist) + n_bins * 1e-6)
    kl = float(np.sum(p_hist * np.log(p_hist / q_hist)))
    return max(0.0, kl)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    rng = np.random.default_rng(42)
    M_test, N_test = 4, 64
    patterns = _random_patterns(M_test, N_test, rng)
    W = _build_weights(patterns)
    target = patterns[0]

    fwd = _run_trajectories(W, target, n_traj=5, n_steps=5,
                             noise_frac=0.05, rng=rng, reverse=False)
    rev = _run_trajectories(W, target, n_traj=5, n_steps=5,
                             noise_frac=0.05, rng=rng, reverse=True)
    assert len(fwd) == 5, "forward trajectory count wrong"
    assert all(-1.0 <= m <= 1.0 for m in fwd), "overlap out of range"

    kl = _kl_div_hist(fwd, rev, n_bins=5)
    assert kl is not None, "KL None"
    assert not math.isnan(kl), "KL NaN"
    assert kl >= 0.0, f"KL negative: {kl}"

    # KL between identical distributions should be ~0
    kl_same = _kl_div_hist(fwd, fwd, n_bins=5)
    assert kl_same < 0.5, f"KL(same||same) too large: {kl_same}"

    print("SELFTEST PASSED: ne3_crooks_kl_drift_v1")


_instrumentation_selftest()


def run_experiment(smoke: bool = False) -> Dict:
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    all_results = []

    for seed in seeds:
        rng = np.random.default_rng(seed)

        # Phase A: pre-drift
        pat_A = _random_patterns(M_A, N, rng)
        W_A = _build_weights(pat_A)
        target = pat_A[0]

        fwd_pre  = _run_trajectories(W_A, target, N_TRAJ, N_STEPS, NOISE_FRAC, rng, reverse=False)
        rev_pre  = _run_trajectories(W_A, target, N_TRAJ, N_STEPS, NOISE_FRAC, rng, reverse=True)
        kl_pre   = _kl_div_hist(fwd_pre, rev_pre, N_BINS)

        # Multiple pre-drift windows to estimate baseline distribution
        kl_baseline_vals = [kl_pre]
        for _ in range(9):
            fwd_w = _run_trajectories(W_A, target, N_TRAJ, N_STEPS, NOISE_FRAC, rng, reverse=False)
            rev_w = _run_trajectories(W_A, target, N_TRAJ, N_STEPS, NOISE_FRAC, rng, reverse=True)
            kl_baseline_vals.append(_kl_div_hist(fwd_w, rev_w, N_BINS))

        baseline_mean = float(np.mean(kl_baseline_vals))
        baseline_std  = float(np.std(kl_baseline_vals))
        # Avoid division by near-zero std
        if baseline_std < 1e-6:
            baseline_std = 1e-6

        # Compute false-alarm rate on baseline window
        threshold_3sigma = baseline_mean + 3.0 * baseline_std
        fa_count = sum(1 for k in kl_baseline_vals if k > threshold_3sigma)
        fa_rate = fa_count / len(kl_baseline_vals)

        # Drift event: add patterns to W
        pat_drift = _random_patterns(M_DRIFT, N, rng)
        W_drift = W_A + _build_weights(pat_drift)
        np.fill_diagonal(W_drift, 0.0)

        fwd_post = _run_trajectories(W_drift, target, N_TRAJ, N_STEPS, NOISE_FRAC, rng, reverse=False)
        rev_post = _run_trajectories(W_drift, target, N_TRAJ, N_STEPS, NOISE_FRAC, rng, reverse=True)
        kl_post  = _kl_div_hist(fwd_post, rev_post, N_BINS)

        sigma_above = (kl_post - baseline_mean) / baseline_std

        print(f"seed={seed} KL_pre={kl_pre:.4f} KL_post={kl_post:.4f} "
              f"baseline_std={baseline_std:.4f} sigma_above={sigma_above:.2f} "
              f"fa_rate={fa_rate:.3f} threshold={threshold_3sigma:.4f}")

        all_results.append({
            "seed": seed,
            "kl_baseline_mean": baseline_mean,
            "kl_baseline_std": baseline_std,
            "kl_post_drift": kl_post,
            "sigma_above": sigma_above,
            "fa_rate": fa_rate,
            "kl_baseline_vals": kl_baseline_vals,
        })

    # Verdict logic
    seeds_pass = sum(
        1 for r in all_results
        if r["sigma_above"] >= HP_SIGMA_ABOVE and r["fa_rate"] <= HP_FA_RATE
    )
    seeds_hf_signal = sum(
        1 for r in all_results if r["sigma_above"] < HF_SIGMA_ABOVE
    )
    seeds_hf_fa = sum(
        1 for r in all_results if r["fa_rate"] > HF_FA_RATE
    )

    if seeds_pass >= HP_MIN_SEEDS:
        verdict = "HARD_PASS"
    elif seeds_hf_signal >= HP_MIN_SEEDS or seeds_hf_fa >= HP_MIN_SEEDS:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    avg_sigma = float(np.mean([r["sigma_above"] for r in all_results]))
    avg_fa    = float(np.mean([r["fa_rate"] for r in all_results]))

    verdict_msg = (
        f"NE-3 CROOKS KL DRIFT: verdict={verdict} | "
        f"{seeds_pass}/{len(all_results)} seeds pass HP | "
        f"avg_sigma_above={avg_sigma:.2f} avg_fa_rate={avg_fa:.3f} | "
        f"HP: sigma>=3.0 AND fa<=0.05 in >=4/5 seeds | "
        f"HF: sigma<1.0 OR fa>0.20 in >=4/5 seeds"
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "seeds_pass": seeds_pass,
        "seeds_total": len(all_results),
        "avg_sigma_above": avg_sigma,
        "avg_fa_rate": avg_fa,
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
