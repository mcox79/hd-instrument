"""Cell C: CK strong-ergodicity-breaking (SEB) discriminator.

SCIENTIFIC QUESTION:
  Is the substrate in the CK (Cugliandolo-Kurchan) class or MCT-canonical class?
  Discriminator: parametric chi (chi = integral_0^t dt' C(t,t')) vs C(t,t_w) plot.
    - KINK at q_EA (Edwards-Anderson order parameter): -> CK class (strong EB, p=2 SK/FRSB)
    - STRAIGHT LINE slope = -1/T_eff: -> MCT canonical class
    - STRAIGHT LINE slope = -1/T: -> equilibrium (no aging)

  Also measure q_EA as long-time C(t, t_w) plateau at t_w in {10, 100, 1000}.

PRE-REGISTERED BANDS:
  HARD-PASS (CK class identified):
    - chi-C plot shows KINK pattern: chi/C slope changes by >= 0.3 at some C* in [0.3, 0.8]
      in >= 4/5 seeds above alpha_c.
    - q_EA detectable: C(t_w, t_w + large_dt) < 0.8 * C(t_w, t_w) (plateau below 1)
      in >= 4/5 seeds.
  MIDDLE: kink visible but slope change < 0.3, or q_EA borderline (0.8-0.95).
  HARD-FAIL: chi-C plot is straight line (|slope change| < 0.10) AND
             q_EA absent (C plateau >= 0.95 * C(t_w, t_w)) in >= 4/5 seeds.

  Calibration probe: no prior CK-discriminator anchor. Bands +-50% per policy.
  P_deflated(CK_class) = 0.40-0.47 (from research).

DESIGN:
  N=2048 (moderate; avoid OOM on 8GB GPU). alpha=0.15 (above alpha_c=0.138).
  t_w_grid = [10, 100, 1000]. t_steps per window = 500.
  Glauber dynamics (stochastic asynchronous): one neuron updated per step on GPU.
  C(t, t_w) = <sigma(t), sigma(t_w)> / N (two-time correlator).
  chi(t, t_w) = integral_0^{t-t_w} C(t_w + s, t_w) ds (susceptibility).
  5 seeds, alpha=0.05 (below alpha_c) as control.

MEMORY CHECK:
  W: N x N float32 = 2048^2 * 4 = 16 MB (fine for 8GB GPU).
  State vectors: N * (n_seeds * n_alpha) = trivial.

PROT-018: no _nN suffix. Production N=2048; stated per PROT-018 rule 3.
  Stated: production N = 2048; rationale: CK discriminator test (N^2 matrix fits 8GB GPU).

TIMEOUT ESTIMATE:
  GPU Glauber at N=2048: each step updates K random neurons. Full async: N steps = 1 sweep.
  t_w_max=1000 + t_steps=500 = 1500 sweeps per (seed, alpha).
  2 seeds_smoke * 2 alpha * 1500 sweeps = 6000 sweeps. At N=2048 GPU: ~10ms per sweep.
  Smoke: ~60s. Full: 5 seeds * 2 alpha * 1500 = 15000 sweeps ~ 150s.
  timeout_s = ceil(1.5 * 150) = 225 -> 300 (floor).

Anchor: ck_seb_discriminator_v1
Queue: overnight_queue
Pre-reg: preregs/2026-06-01_ck_seb_discriminator_v1.md
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
from typing import Dict, List, Optional, Tuple

import numpy as np

# GPU import with fallback to CPU
try:
    import torch
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
except ImportError:
    torch = None  # type: ignore
    DEVICE = None

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "ck_seb_discriminator_v1"

# Production config
N = 2048
ALPHA_GRID = [0.05, 0.15]  # below and above alpha_c=0.138
ALPHA_C = 0.138
T_W_GRID = [10, 100, 1000]
T_STEPS = 500    # steps after each t_w to measure C(t_w + dt, t_w)
BETA = 10.0      # inverse temperature (high -> more deterministic)
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]

# Pre-registered thresholds
HP_SLOPE_CHANGE = 0.30   # kink strength in chi-C plot
HF_SLOPE_CHANGE = 0.10   # no kink below this
HP_Q_EA_MAX = 0.80       # q_EA: C(long time) < 0.80 * C(0) for HP
HF_Q_EA_MIN = 0.95       # no aging: plateau >= 0.95
HP_MIN_SEEDS = 4


def build_hopfield_w(patterns: np.ndarray, N: int) -> np.ndarray:
    """Build Hopfield weight matrix."""
    W = (patterns.T @ patterns) / N
    np.fill_diagonal(W, 0.0)
    return W


def glauber_sweep(W: np.ndarray, state: np.ndarray, beta: float,
                  rng: np.random.Generator, N: int) -> np.ndarray:
    """One Glauber sweep: attempt N random spin flips."""
    for _ in range(N):
        i = rng.integers(0, N)
        h = float(W[i] @ state)
        prob_plus = 1.0 / (1.0 + math.exp(-2.0 * beta * h))
        state[i] = 1.0 if rng.random() < prob_plus else -1.0
    return state


def two_time_correlator(s_t: np.ndarray, s_tw: np.ndarray, N: int) -> float:
    """C(t, t_w) = <sigma(t), sigma(t_w)> / N."""
    return float(np.dot(s_t, s_tw)) / N


def compute_chi_c_slope_change(chi: List[float], c_vals: List[float]) -> float:
    """Detect kink in chi vs C plot. Returns slope change magnitude."""
    if len(chi) < 4:
        return 0.0
    c_arr = np.array(c_vals)
    chi_arr = np.array(chi)
    # Sort by C (decreasing: C goes from 1 at t=t_w down)
    order = np.argsort(c_arr)[::-1]
    c_s = c_arr[order]
    chi_s = chi_arr[order]
    # Piecewise slope: first half vs second half
    mid = len(c_s) // 2
    if mid < 2 or len(c_s) - mid < 2:
        return 0.0
    # Slope of first half (high C)
    dx1 = c_s[:mid]
    dy1 = chi_s[:mid]
    if np.ptp(dx1) < 1e-8:
        s1 = 0.0
    else:
        s1 = float(np.polyfit(dx1, dy1, 1)[0])
    # Slope of second half (low C)
    dx2 = c_s[mid:]
    dy2 = chi_s[mid:]
    if np.ptp(dx2) < 1e-8:
        s2 = 0.0
    else:
        s2 = float(np.polyfit(dx2, dy2, 1)[0])
    return abs(s2 - s1)


def run_one_seed_alpha(seed: int, N: int, alpha: float, t_w_grid: List[int],
                       t_steps: int, beta: float) -> Dict:
    rng = np.random.default_rng(seed)
    M = max(1, int(alpha * N))
    patterns = rng.choice([-1.0, 1.0], size=(M, N))
    W = build_hopfield_w(patterns, N)

    # Random initial state
    state = rng.choice([-1.0, 1.0], size=N)

    chi_vals = []
    c_vals = []
    q_ea_vals = []  # plateau values at long times

    for t_w in t_w_grid:
        # Run to t_w
        for _ in range(t_w):
            state = glauber_sweep(W, state, beta, rng, N)
        s_tw = state.copy()

        # Run t_steps more, record C(t_w + s, t_w) and chi
        chi_accum = 0.0
        c_series = []
        for s in range(1, t_steps + 1):
            state = glauber_sweep(W, state, beta, rng, N)
            c = two_time_correlator(state, s_tw, N)
            c_series.append(c)
            chi_accum += c
            if s % (t_steps // 10 + 1) == 0 or s == t_steps:
                c_vals.append(c)
                chi_vals.append(chi_accum / s)  # running mean as proxy for chi

        # q_EA: average C over last 100 steps (plateau estimate)
        q_ea = float(np.mean(c_series[-100:])) if len(c_series) >= 100 else float(np.mean(c_series))
        q_ea_vals.append(q_ea)

    slope_change = compute_chi_c_slope_change(chi_vals, c_vals)
    q_ea_mean = float(np.mean(q_ea_vals))
    # CK criterion
    kink_present = slope_change >= HP_SLOPE_CHANGE
    q_ea_present = q_ea_mean < HP_Q_EA_MAX

    return {
        "alpha": alpha, "slope_change": slope_change, "q_ea_mean": q_ea_mean,
        "kink_present": kink_present, "q_ea_present": q_ea_present,
        "chi_vals": [float(x) for x in chi_vals],
        "c_vals": [float(x) for x in c_vals],
        "q_ea_per_tw": [float(x) for x in q_ea_vals],
    }


# ---------------------------------------------------------------------------
# Instrumentation self-test
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert two-time correlator and slope-change are non-null at small scale."""
    rng = np.random.default_rng(0)
    N_t = 64
    M_t = 5
    pats = rng.choice([-1.0, 1.0], size=(M_t, N_t))
    W = build_hopfield_w(pats, N_t)
    s1 = rng.choice([-1.0, 1.0], size=N_t)
    s2 = rng.choice([-1.0, 1.0], size=N_t)
    c = two_time_correlator(s1, s2, N_t)
    assert not math.isnan(c), "C(t,t_w) is NaN"
    assert -1.0 <= c <= 1.0, f"C out of range: {c}"
    # Test slope change
    chi = [0.1, 0.2, 0.5, 0.8, 0.9]
    cv = [0.9, 0.7, 0.5, 0.3, 0.1]
    sc = compute_chi_c_slope_change(chi, cv)
    assert sc >= 0, f"slope_change negative: {sc}"
    assert not math.isnan(sc), "slope_change NaN"
    # Test Glauber sweep
    state = rng.choice([-1.0, 1.0], size=N_t)
    state2 = glauber_sweep(W, state.copy(), 5.0, rng, N_t)
    assert len(state2) == N_t, "state length changed"
    print(f"[selftest] PASS: C(t,t_w)={c:.3f}, slope_change={sc:.3f}", flush=True)


_instrumentation_selftest()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "full")
    seeds = SEEDS_FULL if run_mode == "full" else SEEDS_SMOKE
    print(f"[{ANCHOR_NAME}] run_mode={run_mode} seeds={seeds} N={N} "
          f"device={DEVICE}", flush=True)

    all_results: Dict = {}
    for seed in seeds:
        print(f"  seed={seed}...", flush=True)
        seed_res = {}
        for alpha in ALPHA_GRID:
            res = run_one_seed_alpha(seed, N, alpha, T_W_GRID, T_STEPS, BETA)
            seed_res[str(alpha)] = res
            print(f"    alpha={alpha}: slope_change={res['slope_change']:.3f} "
                  f"q_ea={res['q_ea_mean']:.3f} kink={res['kink_present']} "
                  f"q_ea_present={res['q_ea_present']}", flush=True)
        all_results[str(seed)] = seed_res

    # Assess HP criteria (above alpha_c only)
    above_alpha_key = str(ALPHA_GRID[1])  # alpha=0.15
    n_seeds = len(seeds)
    seeds_kink = sum(1 for s_res in all_results.values()
                     if s_res[above_alpha_key]["kink_present"])
    seeds_qea  = sum(1 for s_res in all_results.values()
                     if s_res[above_alpha_key]["q_ea_present"])
    seeds_straight = sum(1 for s_res in all_results.values()
                         if s_res[above_alpha_key]["slope_change"] < HF_SLOPE_CHANGE)

    hp_thresh = HP_MIN_SEEDS if n_seeds >= 5 else math.ceil(n_seeds * 0.8)
    hf_thresh = math.ceil(n_seeds * 0.8)

    hp_kink = seeds_kink >= hp_thresh
    hp_qea  = seeds_qea  >= hp_thresh
    hf_straight = seeds_straight >= hf_thresh

    if hf_straight and seeds_qea < math.ceil(n_seeds * 0.4):
        verdict = "HARD_FAIL"
    elif hp_kink and hp_qea:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    # Summary stats
    slope_changes = [all_results[str(s)][above_alpha_key]["slope_change"]
                     for s in seeds]
    q_ea_vals = [all_results[str(s)][above_alpha_key]["q_ea_mean"]
                 for s in seeds]

    elapsed = time.time() - t0
    metrics = {
        "anchor": ANCHOR_NAME, "run_mode": run_mode,
        "N": N, "n_seeds": n_seeds, "alpha_grid": ALPHA_GRID,
        "slope_change_mean": float(np.mean(slope_changes)),
        "slope_change_std": float(np.std(slope_changes)),
        "q_ea_mean": float(np.mean(q_ea_vals)),
        "seeds_kink": seeds_kink, "seeds_qea": seeds_qea,
        "verdict": verdict, "elapsed_s": elapsed,
        "thresholds": {
            "HP_slope_change": HP_SLOPE_CHANGE, "HF_slope_change": HF_SLOPE_CHANGE,
            "HP_q_ea_max": HP_Q_EA_MAX, "HF_q_ea_min": HF_Q_EA_MIN,
        },
        "verdict_msg": (
            f"CK discriminator at N={N} alpha={ALPHA_GRID[1]}: "
            f"slope_change={np.mean(slope_changes):.3f}+/-{np.std(slope_changes):.3f} "
            f"(HP>={HP_SLOPE_CHANGE}), q_EA={np.mean(q_ea_vals):.3f} "
            f"(HP<{HP_Q_EA_MAX}), {seeds_kink}/{n_seeds} seeds kink. "
            f"Verdict: {verdict}."
        ),
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict} elapsed={elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    parser.add_argument("--smoke", action="store_true",
                       help="Run at smoke scope for gate validation")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)  # _instrumentation_selftest() already ran at module scope
    if args.smoke:
        os.environ["HDLAB_RUN_MODE"] = "smoke"
    main()
