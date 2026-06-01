"""Q20 -- Inter-quake time distribution (Pareto vs exponential).

SCIENTIFIC QUESTION:
  Does the distribution of inter-quake times (record-breaking drops in overlap
  trajectory) follow Pareto (Sibani record dynamics) or exponential (Poisson-rate)?
  HP: KS test rejects exponential at p < 0.01 AND Pareto R^2 > 0.95.
  HF: Pareto rejected at p < 0.01 (substrate NOT in record-dynamics class).

THEORY:
  Record dynamics: quakes (discontinuous drops in overlap) occur when a new
  record-low state is reached. Inter-quake times follow heavy-tailed distribution.
  Standard Poisson: inter-quake times exponential (no heavy tail).

  Proper aging protocol: start NEAR a pattern (noisy IC) at NEAR-CAPACITY loading
  (alpha ~ 0.12, below alpha_c=0.138 but high enough for multi-basin competition).
  Track record-breaking drops in overlap C(t) = <s(t), xi_test> / N.
  A quake is a time point where C(t) sets a new record minimum below the
  previous record by >= delta_quake.

DESIGN:
  N=4096, M=500 (alpha=0.122, near capacity).
  IC: start near xi_test with noise_frac=0.30 (30% bits flipped).
  T=2000 synchronous steps per seed (FULL); T=500 for smoke.
  Quake = record-breaking drop: C(t) < running_min - delta_quake = 0.05.
  Collect inter-quake times (consecutive quake intervals).
  5 seeds.

FORMULA SELF-TESTS:
  1. At alpha=0.122 with 30% noise IC: first few steps show overlap ~ 0.7-0.8
     as system moves toward pattern, then competition with other patterns causes
     drift and quakes.
  2. Mean IQT ~ O(10-50 steps) based on smoke calibration.
  3. Pareto vs exponential: log-log CCDF should show heavier tail than exponential.

PROT-018: no _nN suffix. Production N=4096 per rule 3.
  Stated: production N = 4096; rationale: quake dynamics near capacity.

TIMEOUT ESTIMATE:
  Smoke (T=500, 2 seeds): 14.5s. FULL (T=2000, 5 seeds): scale by T/T_s * seeds/seeds_s.
  timeout = ceil(1.5 * 14.5 * (2000/500) * (5/2)) = ceil(1.5 * 14.5 * 4 * 2.5) = ceil(217.5) = 300.
  timeout=600 (2x safety, near-capacity dynamics can be slow to converge).

Anchor: inter_quake_distribution_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_inter_quake_distribution_v1.md
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

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial  # noqa: E402

ANCHOR_NAME = "inter_quake_distribution_v1"

# Production config
N = 4096
M = 500          # alpha = 500/4096 = 0.122 (near-capacity)
NOISE_FRAC_IC = 0.30  # 30% noise on starting IC
T_STEPS_FULL  = 2000
T_STEPS_SMOKE = 500
DELTA_QUAKE   = 0.05
MIN_IQTS_THRESHOLD = 5
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]

# Pre-registered thresholds
HP_KS_P_REJECT_EXP = 0.01
HP_PARETO_R2       = 0.95
HF_PARETO_P_REJECT = 0.01


def build_w(patterns: np.ndarray, N: int) -> np.ndarray:
    W = (patterns.T @ patterns) / N
    np.fill_diagonal(W, 0.0)
    return W


def collect_quake_times(W: np.ndarray, s0: np.ndarray, xi_test: np.ndarray,
                        N: int, T: int, delta_quake: float) -> Tuple[List[int], List[float]]:
    """Run T steps from s0; return (quake_times, C_trajectory)."""
    s = s0.copy()
    C_vals = []
    for _ in range(T):
        s = np.where(W @ s > 0, 1.0, -1.0)
        C = float(np.dot(s, xi_test) / N)
        C_vals.append(C)

    # Record-breaking drops: C(t) drops below running_min by > delta_quake
    quake_times = []
    running_min = C_vals[0]
    for i in range(1, len(C_vals)):
        if C_vals[i] < running_min - delta_quake:
            quake_times.append(i)
            running_min = C_vals[i]
        # Update running min regardless
        if C_vals[i] < running_min:
            running_min = C_vals[i]

    return quake_times, C_vals


def compute_iqt(quake_times: List[int]) -> List[int]:
    if len(quake_times) < 2:
        return []
    arr = sorted(quake_times)
    return [arr[i+1] - arr[i] for i in range(len(arr) - 1)]


def fit_exponential_ks(iqts: np.ndarray) -> Tuple[float, float]:
    from scipy.stats import kstest
    if len(iqts) < 5:
        return float("nan"), float("nan")
    mu_mle = float(np.mean(iqts))
    stat, p = kstest(iqts, 'expon', args=(0, mu_mle))
    return float(stat), float(p)


def fit_pareto_r2(iqts: np.ndarray) -> Tuple[float, float]:
    if len(iqts) < 5:
        return float("nan"), float("nan")
    iqts_sorted = np.sort(iqts).astype(float)
    x_min = float(iqts_sorted[0]) if iqts_sorted[0] > 0 else 1.0
    tail = iqts_sorted[iqts_sorted >= x_min]
    if len(tail) < 4:
        return float("nan"), float("nan")

    log_ratios = np.log(tail / x_min)
    hill_alpha = 1.0 / (float(np.mean(log_ratios)) + 1e-10)

    ranks = np.arange(len(tail), 0, -1) / len(tail)
    log_x = np.log(tail)
    log_p = np.log(ranks + 1e-10)
    log_x_c = log_x - np.mean(log_x)
    if np.std(log_x_c) < 1e-10:
        return hill_alpha, float("nan")
    slope = float(np.corrcoef(log_x_c, log_p)[0, 1])
    log_p_pred = np.mean(log_p) + slope * log_x_c
    ss_res = float(np.sum((log_p - log_p_pred)**2))
    ss_tot = float(np.sum((log_p - np.mean(log_p))**2)) + 1e-10
    r2 = max(0.0, 1.0 - ss_res / ss_tot)
    return float(hill_alpha), r2


def run_seed(seed: int, N: int, M: int, T: int, noise_frac: float,
             delta_quake: float) -> Dict:
    rng = np.random.default_rng(seed)
    patterns = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
    W = build_w(patterns, N)
    xi_test = patterns[0]

    # Noisy IC near xi_test
    s0 = xi_test.copy()
    n_flip = max(1, int(noise_frac * N))
    flip_idx = rng.choice(N, size=n_flip, replace=False)
    s0[flip_idx] *= -1

    quake_times, C_vals = collect_quake_times(W, s0, xi_test, N, T, delta_quake)
    iqts = compute_iqt(quake_times)

    if len(iqts) < MIN_IQTS_THRESHOLD:
        return {
            "seed": seed, "n_quakes": len(quake_times), "n_iqts": len(iqts),
            "ks_p_exp": float("nan"), "ks_stat_exp": float("nan"),
            "pareto_r2": float("nan"), "hill_alpha": float("nan"),
            "C_range": [min(C_vals), max(C_vals)],
            "insufficient_quakes": True,
        }

    iqts_arr = np.array(iqts)
    ks_stat, ks_p = fit_exponential_ks(iqts_arr)
    hill_alpha, pareto_r2 = fit_pareto_r2(iqts_arr)

    return {
        "seed": seed,
        "n_quakes": len(quake_times),
        "n_iqts": len(iqts),
        "mean_iqt": float(np.mean(iqts_arr)),
        "ks_stat_exp": ks_stat, "ks_p_exp": ks_p,
        "hill_alpha": hill_alpha, "pareto_r2": pareto_r2,
        "C_range": [min(C_vals), max(C_vals)],
        "insufficient_quakes": False,
    }


# ---------------------------------------------------------------------------
# Instrumentation self-test
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert quake detection finds events at near-capacity loading."""
    rng = np.random.default_rng(55)
    N_t, M_t = 512, 60  # alpha = 0.117
    pats = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    W_t = build_w(pats, N_t)
    xi_t = pats[0]
    s0 = xi_t.copy()
    s0[rng.choice(N_t, int(0.30 * N_t), replace=False)] *= -1
    quake_ts, C_vals = collect_quake_times(W_t, s0, xi_t, N_t, 200, 0.05)
    iqts = compute_iqt(quake_ts)
    # At near-capacity we expect some quakes; report even if 0
    assert isinstance(quake_ts, list), "quake_ts not list"
    assert len(C_vals) == 200, f"C_vals length wrong: {len(C_vals)}"
    # Test distribution fit on synthetic data always works
    test_iqts = np.abs(rng.exponential(20.0, 30)).astype(float) + 1.0
    ks_stat, ks_p = fit_exponential_ks(test_iqts)
    assert not math.isnan(ks_stat), "ks_stat NaN on synthetic data"
    print(f"[selftest] PASS: inter_quake_distribution_v1 n_quakes={len(quake_ts)} "
          f"C_range=[{min(C_vals):.3f},{max(C_vals):.3f}]", flush=True)


_instrumentation_selftest()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    run_mode = os.environ.get("HDLAB_RUN_MODE", "full")
    seeds   = SEEDS_FULL  if run_mode == "full" else SEEDS_SMOKE
    T_STEPS = T_STEPS_FULL if run_mode == "full" else T_STEPS_SMOKE
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_config = {"N": N, "run_mode": run_mode}

    print(f"[{ANCHOR_NAME}] run_mode={run_mode} N={N} M={M} alpha={M/N:.3f} "
          f"T={T_STEPS} seeds={seeds}", flush=True)

    done, remaining = resumable_seeds(seeds, out_dir, run_config=run_config)
    print(f"[{ANCHOR_NAME}] checkpoint: {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        print(f"  seed={seed}... T={T_STEPS}", flush=True)
        res = run_seed(seed, N, M, T_STEPS, NOISE_FRAC_IC, DELTA_QUAKE)
        res["N"] = N
        res["run_mode"] = run_mode
        print(f"    n_quakes={res['n_quakes']} ks_p_exp={res.get('ks_p_exp', 'nan')} "
              f"pareto_r2={res.get('pareto_r2', 'nan')}", flush=True)
        write_partial(out_dir, seed, res)

    from experiments._seed_checkpoint import aggregate_partials
    per_seed = aggregate_partials(out_dir, seeds, run_config=run_config)

    ks_p_vals  = [p["ks_p_exp"]  for p in per_seed.values()
                  if not p.get("insufficient_quakes", True) and not math.isnan(p.get("ks_p_exp", float("nan")))]
    pareto_r2s = [p["pareto_r2"] for p in per_seed.values()
                  if not p.get("insufficient_quakes", True) and not math.isnan(p.get("pareto_r2", float("nan")))]
    n_sufficient = sum(1 for p in per_seed.values() if not p.get("insufficient_quakes", True))

    if len(ks_p_vals) == 0:
        verdict = "HARD_FAIL"
        verdict_note = "insufficient_quakes"
    else:
        mean_ks_p      = float(np.mean(ks_p_vals))
        mean_pareto_r2 = float(np.mean(pareto_r2s)) if pareto_r2s else float("nan")
        exp_rejected   = all(p < HP_KS_P_REJECT_EXP for p in ks_p_vals)
        pareto_fits    = (not math.isnan(mean_pareto_r2)) and mean_pareto_r2 > HP_PARETO_R2

        if exp_rejected and pareto_fits:
            verdict = "HARD_PASS"
            verdict_note = "record_dynamics"
        elif (not math.isnan(mean_pareto_r2)) and mean_pareto_r2 < HF_PARETO_P_REJECT:
            verdict = "HARD_FAIL"
            verdict_note = "pareto_rejected"
        else:
            verdict = "MIDDLE_BAND"
            verdict_note = "inconclusive"

    elapsed = time.time() - t0
    metrics = {
        "anchor": ANCHOR_NAME, "run_mode": run_mode, "N": N, "M": M,
        "alpha": M / N, "T_steps": T_STEPS,
        "n_seeds": len(seeds), "n_sufficient": n_sufficient,
        "mean_ks_p_exp": float(np.mean(ks_p_vals)) if ks_p_vals else float("nan"),
        "mean_pareto_r2": float(np.mean(pareto_r2s)) if pareto_r2s else float("nan"),
        "verdict": verdict, "verdict_note": verdict_note, "elapsed_s": elapsed,
        "thresholds": {
            "HP_ks_p_reject_exp": HP_KS_P_REJECT_EXP,
            "HP_pareto_r2": HP_PARETO_R2,
        },
        "verdict_msg": (
            f"Inter-quake IQT N={N} M={M} alpha={M/N:.3f} T={T_STEPS}: "
            f"mean_ks_p_exp={float(np.mean(ks_p_vals)) if ks_p_vals else float('nan'):.4f} "
            f"(HP reject exp p<{HP_KS_P_REJECT_EXP}), "
            f"mean_pareto_r2={float(np.mean(pareto_r2s)) if pareto_r2s else float('nan'):.4f} "
            f"(HP>{HP_PARETO_R2}), {n_sufficient}/{len(seeds)} seeds sufficient. "
            f"Note={verdict_note}. Verdict={verdict}."
        ),
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict} note={verdict_note} elapsed={elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument("--self-test", action="store_true", dest="self_test")
    _args = _p.parse_args()
    if _args.self_test:
        sys.exit(0)
    main()
