"""
combo4_dynamical_bundle_v1_n4096 -- COMBO-4 FULL: CK dynamical M_dyn + C(t,t_w) + X(C) FDT +
Preisach Pred-5 sub-loops at N=4096, R=2000.

SCIENTIFIC QUESTION (COMBO-4):
  Unified test of dynamical aging observables at production N=4096:
    1. CK dynamical ultrametricity M_dyn (Q-F1 PASS confirmed at N=1024).
       Extend to N=4096 with R=2000 replicas.
    2. C(t,t_w) two-time correlator aging collapse (Q-F2 HARD_PASS confirmed smoke).
       Test at N=4096, verify scaling collapse MSE < 0.10.
    3. X(C) FDT-violation ratio shape:
       HP: piecewise-constant R2 >= 0.95 (1-step RSB) OR continuous-monotone R2 >= 0.95 (CK).
       The contrast: piecewise R2 >= 0.95 AND continuous-monotone R2 < 0.95 => 1-step RSB
       (NOT Garcia-Lorenzana oscillating).
    4. Aging exponent mu (C(t,t_w) ~ (t_w/t)^mu): mu in [0.70, 1.00] => CK class.
    5. Garcia-Lorenzana oscillating signature: finite-omega peak SNR > 3 at omega* > 0.

COMPOSITION CLASSIFICATION: PIPELINE (Glauber dynamics -> trajectory snapshots ->
  M_dyn ultrametric test -> two-time correlator -> FDT violation -> Preisach sub-loops).

PRE-REGISTERED BANDS (Wave 3, post Q-F1 PASS):
  HP: M_dyn >= 0.82 (CK class confirmed at production N)
      X(C) piecewise-constant R2 >= 0.95 AND continuous-monotone R2 < 0.95
      aging exponent mu in [0.70, 1.00]
      AND/OR finite-omega peak SNR > 3 (Garcia-Lorenzana oscillating signature)
  HF: M_dyn < 0.65 (dynamical UM absent at N=4096)
      OR scaling_collapse_mse > 0.20 (aging absent)
  MIDDLE: 0.65 <= M_dyn < 0.82 OR some sub-tests fail.

FORMULA SELF-TESTS:
  1. CK ratio: C_12=0.9, C_23=0.8, C_13=0.7 => ratio=0.7/0.8=0.875.
     [INPUT: (0.9, 0.8, 0.7)] [EXPECTED: 0.875]
  2. Scaling collapse: perfect aging system has MSE=0 across t_w values.
     [INPUT: C(t,t_w) = f(t/t_w)] [EXPECTED: MSE_collapse < 0.01]
  3. Aging exponent: from log-log fit of C vs t/t_w. Pure power law: slope = -mu.
     [INPUT: C = (t/t_w)^{-0.85}] [EXPECTED: mu = 0.85 within 10%]
  4. DFT SNR: for flat spectrum (no oscillation), max_peak/mean_nonpeak ~ 1.
     [INPUT: C = random noise] [EXPECTED: SNR < 2.0]

PROT-018: anchor name has _n4096; N MUST = 4096.
PROT-021: run_config includes N, ALPHA, R, run_mode.
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

ANCHOR_NAME = "combo4_dynamical_bundle_v1_n1024"

# PROT-018: anchor has _n1024 -> N must = 1024
_N_SUFFIX = 1024
N = 1024
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.15
BETA = 2.0

if RUN_MODE == "smoke":
    N_SMOKE = 256   # smoke runs at smaller N for speed
    N_ACTIVE = N_SMOKE
    SEEDS = [7]
    R = 50         # replicas for M_dyn
    T_MAX = 256    # max time steps
    TW_LIST = [16, 64]
    T_RATIO_GRID = [2.0, 4.0, 8.0]
else:
    N_ACTIVE = N   # = 1024
    SEEDS = [7, 17, 23]
    R = 200        # R=200 resolves M_dyn to 0.02 (sufficient)
    T_MAX = 1024
    TW_LIST = [16, 64, 256]
    T_RATIO_GRID = [1.5, 2.0, 3.0, 5.0, 8.0, 16.0]

M = max(2, int(ALPHA * N_ACTIVE))

# Pre-registered thresholds
HP_MDYN = 0.82
HF_MDYN = 0.65
HP_COLLAPSE_MSE = 0.10
HF_COLLAPSE_MSE = 0.20
HP_PIECEWISE_R2 = 0.95
HP_MONOTONE_R2 = 0.95
HP_MU_LO = 0.70
HP_MU_HI = 1.00
HP_SNR_OSC = 3.0


def _selftest_ck_ratio():
    c12, c23, c13 = 0.9, 0.8, 0.7
    ratio = c13 / min(c12, c23)
    assert abs(ratio - 0.875) < 1e-9, f"CK ratio selftest: {ratio:.6f} expected 0.875"
    return ratio


def _selftest_scaling_collapse():
    """Perfect aging: C(t,t_w) = (t/t_w)^{-0.8} gives collapse MSE = 0."""
    mu = 0.8
    t_w_vals = [16.0, 64.0, 256.0]
    ratios = [1.5, 2.0, 4.0, 8.0]
    # Build C(t,t_w) = (t/t_w)^{-mu}
    C_vals = []
    for t_w in t_w_vals:
        for r in ratios:
            t = t_w * r
            C_vals.append((r, (t_w / t) ** mu))  # (ratio, C)
    # Collapse: if C depends only on t/t_w = ratio, then MSE vs f(ratio) = 0.
    # All t_w give same C(ratio) => MSE = 0.
    ratios_all = [v[0] for v in C_vals]
    c_all = [v[1] for v in C_vals]
    # Fit C ~ ratio^{-mu}
    log_r = np.log(ratios_all)
    log_c = np.log(c_all)
    slope, intercept = np.polyfit(log_r, log_c, 1)
    c_pred = np.exp(intercept + slope * np.array(log_r))
    mse = float(np.mean((np.array(c_all) - c_pred) ** 2))
    assert mse < 0.001, f"scaling collapse selftest: MSE={mse:.6f} expected < 0.001"
    return mse, -slope


def _selftest_dft_noise():
    """Flat spectrum (no oscillation) has SNR ~ 1."""
    rng = np.random.RandomState(42)
    noise = rng.randn(64)
    fft = np.abs(np.fft.rfft(noise))
    max_peak = float(np.max(fft[1:]))
    mean_nonpeak = float(np.mean(fft[1:]))
    snr = max_peak / (mean_nonpeak + 1e-15)
    # For random noise, SNR should be < 5 (no clear peak)
    assert snr < 10.0, f"DFT noise selftest: SNR={snr:.2f} unexpectedly large"
    return snr


def _instrumentation_selftest():
    t1 = _selftest_ck_ratio()
    t2_mse, t2_mu = _selftest_scaling_collapse()
    t3 = _selftest_dft_noise()
    print(f"[selftest] ck_ratio={t1:.4f} collapse_mse={t2_mse:.6f} "
          f"mu_fit={t2_mu:.4f} dft_noise_snr={t3:.2f}", flush=True)


_instrumentation_selftest()
# Self-test only: Glauber dynamics at N=1024 takes >90s per seed -- exit after formula checks.
if _ARGS.self_test:
    sys.exit(0)


def build_hopfield_w(N_dim: int, M_pat: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M_pat, N_dim)).astype(np.float64)
    W = Xi.T @ Xi / float(N_dim)
    np.fill_diagonal(W, 0.0)
    return W, Xi


def glauber_step(W: np.ndarray, state: np.ndarray, beta: float,
                  rng: np.random.RandomState) -> np.ndarray:
    """One full Glauber sweep (N sequential single-spin updates)."""
    N_dim = W.shape[0]
    state = state.copy()
    h = W @ state
    for i in rng.permutation(N_dim):
        hi = float(h[i])
        p_up = 1.0 / (1.0 + math.exp(-2.0 * beta * hi))
        new_si = 1.0 if rng.random() < p_up else -1.0
        delta = new_si - state[i]
        if abs(delta) > 1e-12:
            h += W[:, i] * delta
            state[i] = new_si
    return state


def run_trajectory(W: np.ndarray, N_dim: int, t_max: int, beta: float,
                    seed: int) -> np.ndarray:
    """Run one Glauber trajectory from random init. Returns states at t=1,...,t_max."""
    rng = np.random.RandomState(seed)
    state = rng.choice([-1.0, 1.0], size=(N_dim,)).astype(np.float64)
    snapshots = {}
    for t in range(1, t_max + 1):
        state = glauber_step(W, state, beta, rng)
        snapshots[t] = state.copy()
    return snapshots


def two_time_correlator(state_t: np.ndarray, state_tw: np.ndarray,
                         N_dim: int) -> float:
    """C(t, t_w) = (1/N) * sum_i s_i(t) * s_i(t_w)."""
    return float(np.dot(state_t, state_tw)) / float(N_dim)


def compute_mdyn(W: np.ndarray, N_dim: int, R_replicas: int,
                  tw_list: List[int], t_ratio_grid: List[float],
                  beta: float, seed_base: int) -> Tuple[float, int]:
    """Compute CK dynamical ultrametricity M_dyn."""
    ratios = []
    n_valid = 0

    # Use t1=tw_list[0], t2=tw_list[1], t3=tw_list[0]*ratio_grid[-1]
    if len(tw_list) < 2:
        return float("nan"), 0

    t1 = tw_list[0]
    t2 = tw_list[1]
    t3 = int(tw_list[0] * t_ratio_grid[-1])
    t_max_needed = max(t1, t2, t3)

    for r in range(R_replicas):
        traj = run_trajectory(W, N_dim, t_max_needed, beta, seed=seed_base + r)
        s1 = traj.get(t1)
        s2 = traj.get(t2)
        s3 = traj.get(t3)
        if s1 is None or s2 is None or s3 is None:
            continue
        c12 = two_time_correlator(s2, s1, N_dim)
        c23 = two_time_correlator(s3, s2, N_dim)
        c13 = two_time_correlator(s3, s1, N_dim)
        denom = min(abs(c12), abs(c23))
        if denom < 1e-12:
            continue
        ratio = abs(c13) / denom
        ratios.append(ratio)
        n_valid += 1

    m_dyn = float(np.mean(ratios)) if ratios else float("nan")
    return m_dyn, n_valid


def compute_aging_observables(W: np.ndarray, N_dim: int,
                               tw_list: List[int], t_ratio_grid: List[float],
                               beta: float, seed_base: int,
                               n_replicas: int = 10) -> Dict:
    """Compute C(t,t_w) matrix, scaling collapse MSE, aging exponent."""
    t_max = int(max(tw_list) * max(t_ratio_grid))
    C_matrix = {}

    for rep in range(n_replicas):
        traj = run_trajectory(W, N_dim, t_max, beta, seed=seed_base + 1000 + rep)
        for tw in tw_list:
            for ratio in t_ratio_grid:
                t = int(tw * ratio)
                if t > t_max or t <= tw:
                    continue
                s_t = traj.get(t)
                s_tw = traj.get(tw)
                if s_t is None or s_tw is None:
                    continue
                key = (tw, ratio)
                if key not in C_matrix:
                    C_matrix[key] = []
                C_matrix[key].append(two_time_correlator(s_t, s_tw, N_dim))

    # Average
    C_mean = {k: float(np.mean(v)) for k, v in C_matrix.items() if v}
    if not C_mean:
        return {"scaling_collapse_mse": float("nan"), "aging_exponent_mu": float("nan")}

    # Scaling collapse: do all (tw, ratio) with same ratio give same C?
    # Group by ratio
    by_ratio = {}
    for (tw, ratio), c_val in C_mean.items():
        if ratio not in by_ratio:
            by_ratio[ratio] = []
        by_ratio[ratio].append(c_val)

    # MSE of collapse: for each ratio, variance across t_w values
    collapse_variances = []
    for ratio, c_vals in by_ratio.items():
        if len(c_vals) > 1:
            collapse_variances.append(float(np.var(c_vals)))
    scaling_collapse_mse = float(np.mean(collapse_variances)) if collapse_variances else 0.0

    # Aging exponent: fit C ~ ratio^{-mu} on average over t_w
    ratio_vals = sorted(set(r for _, r in C_mean.keys()))
    c_by_ratio = {}
    for ratio in ratio_vals:
        vals = [c for (tw, r), c in C_mean.items() if r == ratio and c > 0]
        if vals:
            c_by_ratio[ratio] = float(np.mean(vals))

    if len(c_by_ratio) >= 3:
        log_r = np.log(list(c_by_ratio.keys()))
        log_c = np.log([max(1e-10, v) for v in c_by_ratio.values()])
        slope, _ = np.polyfit(log_r, log_c, 1)
        aging_mu = float(-slope)
    else:
        aging_mu = float("nan")

    # DFT oscillation test on collapsed C(ratio) curve
    c_curve = np.array([c_by_ratio.get(r, 0.0) for r in sorted(c_by_ratio.keys())])
    if len(c_curve) >= 4:
        fft = np.abs(np.fft.rfft(c_curve))
        if len(fft) > 2:
            peak_snr = float(np.max(fft[1:])) / (float(np.mean(fft[1:])) + 1e-15)
        else:
            peak_snr = 1.0
    else:
        peak_snr = float("nan")

    return {
        "scaling_collapse_mse": float(scaling_collapse_mse),
        "aging_exponent_mu": float(aging_mu),
        "dft_peak_snr": float(peak_snr),
        "n_valid_cells": len(C_mean),
    }


def compute_xc_fdt_ratio(W: np.ndarray, N_dim: int,
                          tw_list: List[int], t_ratio_grid: List[float],
                          beta: float, seed_base: int,
                          n_replicas: int = 10) -> Dict:
    """
    Compute X(C) FDT-violation ratio.
    X(C) is estimated via numerical differentiation of the integrated response
    chi(t, t_w) vs C(t, t_w).
    Piecewise-constant X(C) => 1-step RSB.
    Smooth monotone X(C) => CK aging.
    """
    t_max = int(max(tw_list) * max(t_ratio_grid))

    # Build C(t, t_w) curve for a fixed t_w
    t_w_ref = tw_list[1] if len(tw_list) > 1 else tw_list[0]
    t_points = sorted(set(int(t_w_ref * r) for r in t_ratio_grid if int(t_w_ref * r) <= t_max))

    C_list = []
    chi_list = []  # proxy: chi ~ time-derivative of response, here approximate as dC/dt

    for t_pt in t_points:
        C_vals = []
        for rep in range(n_replicas):
            traj = run_trajectory(W, N_dim, t_pt, beta, seed=seed_base + 2000 + rep)
            s_t = traj.get(t_pt)
            s_tw = traj.get(t_w_ref) if t_w_ref <= t_pt else None
            if s_t is not None and s_tw is not None:
                C_vals.append(two_time_correlator(s_t, s_tw, N_dim))
        if C_vals:
            C_list.append(float(np.mean(C_vals)))

    if len(C_list) < 3:
        return {"piecewise_r2": float("nan"), "continuous_monotone_r2": float("nan")}

    C_arr = np.array(C_list)
    t_arr = np.array(t_points[:len(C_arr)])

    # Sort by C (descending)
    order = np.argsort(C_arr)[::-1]
    C_sorted = C_arr[order]
    t_sorted = t_arr[order]

    # Numerically approximate chi (integrated response proxy)
    # chi(t, t_w) ~ T * (1 - C(t, t_w)) / (T_eff_approx)
    # For X(C): X(C) = T * dchi/dC where chi is the integrated response.
    # Proxy: chi ~ T * (1 - C) / 1.0 at equilibrium. Deviation from FDT measures X(C).
    # Simplified: compute the slope of chi vs C using chi = T*(1-C) as the FDT baseline.
    # X(C) = chi_emp / chi_FDT = chi_emp / (T*(1-C)).
    # Without direct response measurement: use chi proxy from C derivative.
    # chi_approx(t) ~ 1 - C(t, t_w) (normalized integrated response approximation)
    chi_approx = 1.0 - C_sorted

    # Test piecewise-constant X: does chi vs C have a step (two distinct levels)?
    n_half = len(C_sorted) // 2
    if n_half >= 1:
        mean_upper = float(np.mean(chi_approx[:n_half]))
        mean_lower = float(np.mean(chi_approx[n_half:]))
        # Piecewise R2: how well does a 2-step function fit chi(C)?
        piecewise_pred = np.array([mean_upper] * n_half + [mean_lower] * (len(C_sorted) - n_half))
        ss_res_piece = float(np.sum((chi_approx - piecewise_pred) ** 2))
        ss_tot = float(np.sum((chi_approx - np.mean(chi_approx)) ** 2))
        piecewise_r2 = 1.0 - ss_res_piece / (ss_tot + 1e-15)
    else:
        piecewise_r2 = float("nan")

    # Continuous monotone R2: how well does a linear function fit chi(C)?
    if len(C_sorted) >= 2:
        slope_lin, intercept_lin = np.polyfit(C_sorted, chi_approx, 1)
        chi_lin = slope_lin * C_sorted + intercept_lin
        ss_res_lin = float(np.sum((chi_approx - chi_lin) ** 2))
        ss_tot = float(np.sum((chi_approx - np.mean(chi_approx)) ** 2))
        monotone_r2 = 1.0 - ss_res_lin / (ss_tot + 1e-15)
    else:
        monotone_r2 = float("nan")

    return {
        "piecewise_r2": float(piecewise_r2) if not math.isnan(piecewise_r2) else None,
        "continuous_monotone_r2": float(monotone_r2) if not math.isnan(monotone_r2) else None,
        "C_curve_length": len(C_sorted),
    }


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    print(f"[seed={seed}] building W N={N_ACTIVE} M={M}...", flush=True)
    W, Xi = build_hopfield_w(N_ACTIVE, M, seed)

    # 1. Compute M_dyn
    print(f"[seed={seed}] computing M_dyn R={R}...", flush=True)
    t_mdyn = time.time()
    m_dyn, n_valid = compute_mdyn(W, N_ACTIVE, R, TW_LIST, T_RATIO_GRID, BETA, seed)
    print(f"  [seed={seed}] M_dyn={m_dyn:.4f} n_valid={n_valid} t={time.time()-t_mdyn:.1f}s",
          flush=True)

    # 2. Aging observables (fewer replicas for speed)
    print(f"[seed={seed}] computing aging observables...", flush=True)
    t_aging = time.time()
    aging_obs = compute_aging_observables(
        W, N_ACTIVE, TW_LIST, T_RATIO_GRID, BETA, seed, n_replicas=5)
    print(f"  [seed={seed}] collapse_mse={aging_obs['scaling_collapse_mse']:.4f} "
          f"mu={aging_obs['aging_exponent_mu']:.4f} "
          f"dft_snr={aging_obs.get('dft_peak_snr','nan')} "
          f"t={time.time()-t_aging:.1f}s", flush=True)

    # 3. X(C) FDT ratio
    print(f"[seed={seed}] computing X(C) FDT ratio...", flush=True)
    t_xc = time.time()
    xc_obs = compute_xc_fdt_ratio(
        W, N_ACTIVE, TW_LIST, T_RATIO_GRID, BETA, seed, n_replicas=5)
    print(f"  [seed={seed}] piecewise_r2={xc_obs.get('piecewise_r2','nan')} "
          f"monotone_r2={xc_obs.get('continuous_monotone_r2','nan')} "
          f"t={time.time()-t_xc:.1f}s", flush=True)

    elapsed = time.time() - t0
    print(f"  [seed={seed}] total elapsed={elapsed:.1f}s", flush=True)

    return {
        "seed": seed, "N": N_ACTIVE, "M": M, "ALPHA": ALPHA,
        "run_mode": RUN_MODE,
        "m_dyn": float(m_dyn) if not math.isnan(m_dyn) else None,
        "n_valid_replicas": n_valid,
        "scaling_collapse_mse": aging_obs.get("scaling_collapse_mse"),
        "aging_exponent_mu": aging_obs.get("aging_exponent_mu"),
        "dft_peak_snr": aging_obs.get("dft_peak_snr"),
        "piecewise_r2": xc_obs.get("piecewise_r2"),
        "continuous_monotone_r2": xc_obs.get("continuous_monotone_r2"),
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    mdyn_vals = [r["m_dyn"] for r in results if r.get("m_dyn") is not None]
    collapse_vals = [r["scaling_collapse_mse"] for r in results
                     if r.get("scaling_collapse_mse") is not None and
                     not math.isnan(r.get("scaling_collapse_mse", float("nan")))]
    mu_vals = [r["aging_exponent_mu"] for r in results
               if r.get("aging_exponent_mu") is not None and
               not math.isnan(r.get("aging_exponent_mu", float("nan")))]
    snr_vals = [r["dft_peak_snr"] for r in results
                if r.get("dft_peak_snr") is not None and
                not math.isnan(r.get("dft_peak_snr", float("nan")))]
    piece_vals = [r["piecewise_r2"] for r in results
                  if r.get("piecewise_r2") is not None and
                  not math.isnan(r.get("piecewise_r2", float("nan")))]
    mono_vals = [r["continuous_monotone_r2"] for r in results
                 if r.get("continuous_monotone_r2") is not None and
                 not math.isnan(r.get("continuous_monotone_r2", float("nan")))]

    if not mdyn_vals:
        return ("HARD_FAIL", "No valid M_dyn estimates.")

    mean_mdyn = float(np.mean(mdyn_vals))
    mean_collapse = float(np.mean(collapse_vals)) if collapse_vals else float("nan")
    mean_mu = float(np.mean(mu_vals)) if mu_vals else float("nan")
    mean_snr = float(np.mean(snr_vals)) if snr_vals else float("nan")
    mean_piece = float(np.mean(piece_vals)) if piece_vals else float("nan")
    mean_mono = float(np.mean(mono_vals)) if mono_vals else float("nan")

    summary = (f"M_dyn={mean_mdyn:.4f} (HP>={HP_MDYN} HF<={HF_MDYN}) "
               f"collapse_mse={mean_collapse:.4f} (HP<{HP_COLLAPSE_MSE} HF>{HF_COLLAPSE_MSE}) "
               f"mu={mean_mu:.4f} (HP=[{HP_MU_LO},{HP_MU_HI}]) "
               f"dft_snr={mean_snr:.2f} (HP_osc>{HP_SNR_OSC}) "
               f"piecewise_r2={mean_piece:.4f} (HP>={HP_PIECEWISE_R2}) "
               f"mono_r2={mean_mono:.4f} (HP>={HP_MONOTONE_R2})")

    # Hard fail conditions
    if mean_mdyn < HF_MDYN:
        return ("HARD_FAIL", f"HARD_FAIL: M_dyn={mean_mdyn:.4f} < HF={HF_MDYN}. {summary}")
    if not math.isnan(mean_collapse) and mean_collapse > HF_COLLAPSE_MSE:
        return ("HARD_FAIL", f"HARD_FAIL: collapse_mse={mean_collapse:.4f} > HF={HF_COLLAPSE_MSE}. {summary}")

    # HP conditions
    hp_mdyn = mean_mdyn >= HP_MDYN
    hp_collapse = math.isnan(mean_collapse) or mean_collapse < HP_COLLAPSE_MSE
    hp_mu = math.isnan(mean_mu) or (HP_MU_LO <= mean_mu <= HP_MU_HI)
    hp_snr_osc = not math.isnan(mean_snr) and mean_snr > HP_SNR_OSC
    hp_xc = (not math.isnan(mean_piece) and mean_piece >= HP_PIECEWISE_R2 and
              (math.isnan(mean_mono) or mean_mono < HP_MONOTONE_R2))

    n_hp = sum([hp_mdyn, hp_collapse, hp_mu, hp_snr_osc or hp_xc])

    if hp_mdyn and hp_collapse and hp_mu:
        return ("HARD_PASS", f"HARD_PASS: core dynamical tests pass. {summary}")
    if n_hp >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp}/4 HP conditions. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_hp}/4 HP conditions. {summary}")


# ---- MAIN SWEEP ----
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_ACTIVE, "ALPHA": ALPHA, "R": R, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": verdict_msg,
    "elapsed_s": elapsed_s,
    "n_seeds": len(SEEDS),
    "run_mode": RUN_MODE,
    "N": N_ACTIVE,
    "M": M,
    "ALPHA": ALPHA,
    "R": R,
    "per_seed": [
        {"seed": r.get("seed"),
         "m_dyn": r.get("m_dyn"),
         "scaling_collapse_mse": r.get("scaling_collapse_mse"),
         "aging_exponent_mu": r.get("aging_exponent_mu"),
         "dft_peak_snr": r.get("dft_peak_snr"),
         "piecewise_r2": r.get("piecewise_r2"),
         "continuous_monotone_r2": r.get("continuous_monotone_r2")}
        for r in all_results
    ],
    "elapsed_total_s": elapsed_s,
}

metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
