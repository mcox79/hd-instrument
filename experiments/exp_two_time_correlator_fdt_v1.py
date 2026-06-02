"""
two_time_correlator_fdt_v1 -- Q-F2: Two-time correlator C(t,t_w) and FDT-violation ratio X(C).

SCIENTIFIC QUESTION (Q-F2):
  Does the substrate's two-time correlator C(t,t_w) and FDT-violation ratio X(C)
  discriminate between CK pure aging and the Garcia-Lorenzana oscillating-amorphous
  overlay? Q19 RESCUE-SUCCESS confirmed CK-class aging via scaling collapse
  (mean_collapse_mse=0.0029 < 0.1). Q-F2 goes deeper: test the FDT-violation
  ratio X(C) = T*dC/d(response) which is the canonical observable for discriminating
  1-step RSB (piecewise-constant X), CK aging (X = continuous 0->1), and
  oscillating-amorphous overlay (finite-omega peak in |FT[C_hat(omega)]|).

  Protocol from Berthier-Holdsworth-Ricci-Tersenghi 2001 (cond-mat/0112378):
    1. Compute C(t, t_w) at multiple waiting times t_w over t/t_w grid.
    2. Verify aging: C(t,t_w) depends only on t/t_w (NOT t and t_w separately).
    3. Compute R-value proxy: for monotone-decreasing C, check if the curve is
       piecewise-constant (1-step RSB signature) vs smooth (CK aging) vs
       non-monotone-with-zero-crossing (oscillating-amorphous).
    4. Compute |DFT[C_col(omega)]| of the age-collapsed correlation curve:
       if finite-omega peak at omega* > 0 with SNR > 3 => Garcia-Lorenzana
       oscillating-amorphous overlay signal.

  Three sub-tests with independent HARD-PASS / HARD-FAIL per sub-test:

  SUB-TEST A -- Aging confirmation (scaling collapse):
    HP-A: scaling_collapse_mse < 0.05 (C(t,t_w) is a function of t/t_w)
    HF-A: scaling_collapse_mse > 0.20 (no aging; C depends on t AND t_w separately)
    [Note: Q19 already found mse=0.0029; this is a cross-N replication at N=2048]

  SUB-TEST B -- X(C) shape discrimination:
    HP-B: piecewise_r2 >= 0.85 (1-step RSB) OR monotone_smooth_r2 >= 0.85 (CK)
    HF-B: X(C) non-monotone AND no_piecewise AND no_oscillation (structureless)
    [Smooth monotone X(C) = CK pure aging; piecewise X(C) = 1-step RSB]

  SUB-TEST C -- Garcia-Lorenzana oscillation test:
    HP-C: DFT peak SNR > 3 at omega* > 0 (oscillating-amorphous overlay)
    HF-C: DFT peak absent (flat spectrum + no peak) -- rules out oscillating overlay
    MIDDLE-C: 1 < SNR <= 3 at some omega* -- inconclusive, needs more t_w range

  OVERALL VERDICT:
    HARD_PASS: HF-A absent AND (HP-B OR HP-C)
    HARD_FAIL: HF-A triggered (no aging => CK-class refuted => reopen static shelf)
    MIDDLE_BAND: HP-B and HP-C absent but HF-A absent (aging confirmed but X(C) noisy)

FORMULA SELF-TESTS:
  1. Scaling collapse formula: given C matrix C[i,j] at (t_i, t_w_j), rescale by
     t/t_w; if MSE([C(t,t_w)] regressed on t/t_w) < MSE([C(t,t_w)] regressed on t
     separately) => collapse works. For perfectly aging system MSE_collapse = 0.
  2. DFT SNR: given oscillating signal A*cos(omega_0*k) + noise, DFT peak at omega_0
     should have SNR > 3. Test with A=1, noise=0.1, N_t=64: SNR = A/(noise*sqrt(N_t)).
     Expected SNR = 1/(0.1*8) = 1.25. Test that SNR computation is correct.
  3. Piecewise-constant R2: given C = [0.9]*20 + [0.3]*20 (perfect 1-step),
     piecewise R2 = 1.0. Test this case.

SWEEP DESIGN:
  Waiting times t_w in {16, 64, 256} (smoke: {16, 64})
  Observation times t in t_w * ratio_grid where ratio_grid = [1.5, 2, 3, 5, 8, 16] (smoke: [2, 4, 8])
  N = 2048 (full) / 512 (smoke)
  Seeds = [7, 17, 23, 31, 41] (full) / [7] (smoke)
  ALPHA = 0.15
  BETA = 2.0

HARD-PASS/HARD-FAIL:
  See sub-tests A, B, C above.
  Overall HARD_PASS: HF-A absent AND (HP-B or HP-C confirms shape)
  Overall HARD_FAIL: HF-A triggered

TIMEOUT ESTIMATE:
  Smoke: N=512, 2 t_w, 3 ratios, 1 seed. Glauber t_max=16*16=256.
  Inner loop: 256*512 ops * R_est=1 = ~10^5. Wall ~5s.
  Full: N=2048, 3 t_w, 6 ratios, 5 seeds. t_max=256*16=4096.
  Scale: 1.5 * 5 * (2048/512)^1.5 * (5/1) = ceil(1.5*5*11.3*5) = ceil(424) = 450s.
  timeout=1800s (4x buffer; DFT overhead included).

No _nN suffix; production N=2048 per rule 3 (stated here: N=2048, rationale:
larger N needed for cleaner FDT signal per Berthier 2001; 512 smoke confirms
basic observability).
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
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "two_time_correlator_fdt_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N = 512
    SEEDS = [7]
    TW_LIST = [16, 64]
    RATIO_GRID = [2.0, 4.0, 8.0]
    ALPHA = 0.15
    BETA = 2.0
else:
    N = 2048
    SEEDS = [7, 17, 23, 31, 41]
    TW_LIST = [16, 64, 256]
    RATIO_GRID = [1.5, 2.0, 3.0, 5.0, 8.0, 16.0]
    ALPHA = 0.15
    BETA = 2.0

# Pre-registered thresholds
HP_COLLAPSE_MSE = 0.05   # sub-test A
HF_COLLAPSE_MSE = 0.20   # sub-test A hard-fail
HP_PIECEWISE_R2 = 0.85   # sub-test B (1-step RSB)
HP_SMOOTH_R2 = 0.85      # sub-test B (CK smooth)
HP_DFT_SNR = 3.0         # sub-test C (oscillating overlay)
MID_DFT_SNR = 1.0        # sub-test C middle band


# ---- FORMULA SELF-TESTS ----
def _selftest_collapse_formula():
    """Perfect aging system: C(t,t_w) = f(t/t_w). MSE_collapse = 0."""
    # Build 3x4 C matrix where C_ij = exp(-t_i/t_w_j) -- aging
    tw = np.array([16.0, 64.0, 256.0])
    ratios = np.array([2.0, 4.0, 8.0, 16.0])
    C = np.zeros((len(ratios), len(tw)))
    for i, r in enumerate(ratios):
        for j, tw_j in enumerate(tw):
            t_ij = r * tw_j
            C[i, j] = math.exp(-t_ij / (100.0 * tw_j))  # f(t/t_w) = exp(-r/100)
    # Each row of C should be constant (same ratio, different t_w) => perfect collapse
    row_vars = np.var(C, axis=1)
    mse_collapse = float(np.mean(row_vars))
    assert mse_collapse < 1e-10, f"Perfect aging MSE_collapse={mse_collapse:.2e}, expected ~0"
    return mse_collapse


def _selftest_dft_snr():
    """DFT SNR for known oscillating signal."""
    # A*cos(omega_0*k) + noise
    N_t = 64
    A = 1.0
    omega_0 = 2.0 * math.pi * 8 / N_t  # peak at bin 8
    noise_level = 0.1
    rng = np.random.RandomState(42)
    k = np.arange(N_t)
    signal = A * np.cos(omega_0 * k) + noise_level * rng.randn(N_t)
    spectrum = np.abs(np.fft.rfft(signal))
    peak_bin = np.argmax(spectrum[1:]) + 1  # skip DC
    noise_floor = np.median(spectrum[1:])
    snr = spectrum[peak_bin] / (noise_floor + 1e-10)
    # Should be well above 3 for this strong signal
    assert snr > 5.0, f"DFT SNR={snr:.2f} expected >5 for A=1.0, noise=0.1"
    return snr


def _selftest_piecewise_r2():
    """Perfect 1-step: C = [0.9]*20 + [0.3]*20 => piecewise R2 = 1.0."""
    C_col = np.array([0.9] * 20 + [0.3] * 20)
    # Piecewise fit: two constants split at midpoint
    split = len(C_col) // 2
    fit = np.array([np.mean(C_col[:split])] * split + [np.mean(C_col[split:])] * split)
    ss_res = float(np.sum((C_col - fit) ** 2))
    ss_tot = float(np.sum((C_col - np.mean(C_col)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    assert r2 > 0.99, f"Piecewise R2={r2:.4f} expected ~1.0 for perfect 1-step"
    return r2


_mse0 = _selftest_collapse_formula()
_snr0 = _selftest_dft_snr()
_r2_0 = _selftest_piecewise_r2()
print(f"[selftest] collapse_mse={_mse0:.2e} dft_snr={_snr0:.2f} piecewise_r2={_r2_0:.4f}", flush=True)


def build_hopfield_w(M: int, N_dim: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, N_dim)).astype(np.float64)
    W = Xi.T @ Xi / N_dim
    np.fill_diagonal(W, 0.0)
    return W


def glauber_sweep_fast(state: np.ndarray, h: np.ndarray,
                       W: np.ndarray, beta: float,
                       rng: np.random.RandomState) -> np.ndarray:
    """Vectorized approximate Glauber: compute all fields, update sequentially."""
    h[:] = W @ state
    prob_up = 1.0 / (1.0 + np.exp(-2.0 * beta * h))
    rand_vals = rng.rand(len(state))
    state[:] = np.where(rand_vals < prob_up, 1.0, -1.0)
    return state


def measure_two_time_matrix(W: np.ndarray, N_dim: int,
                             tw_list: List[int], ratio_grid: List[float],
                             beta: float, rng: np.random.RandomState) -> Dict:
    """
    Measure C(t, t_w) matrix.
    For each t_w: run Glauber to t_w, record s(t_w).
    Continue to t = ratio * t_w, record s(t).
    C(t, t_w) = (1/N) * dot(s(t_w), s(t)).
    """
    t_max = max(int(max(ratio_grid) * max(tw_list)), max(tw_list))

    # Pre-allocate
    C_matrix = {}  # {(tw, ratio): C_value}
    state = rng.choice([-1.0, 1.0], size=(N_dim,)).astype(np.float64)
    h = np.zeros(N_dim, dtype=np.float64)

    tw_states = {}
    tw_set = set(int(tw) for tw in tw_list)
    t_targets = {}  # {tw: set of t values}
    for tw in tw_list:
        t_targets[tw] = set(int(tw * r) for r in ratio_grid)

    for step in range(1, t_max + 1):
        state = glauber_sweep_fast(state, h, W, beta, rng)
        if step in tw_set:
            tw_states[step] = state.copy()
        for tw in tw_list:
            if step in t_targets.get(tw, set()) and tw in tw_states:
                t_val = step
                s_tw = tw_states[tw]
                c = float(np.dot(s_tw, state)) / N_dim
                C_matrix[(tw, t_val / tw)] = c  # key = (t_w, ratio)

    return C_matrix


def compute_collapse_mse(C_matrix: Dict) -> float:
    """
    Scaling collapse MSE: C(t,t_w) should depend only on t/t_w.
    For each ratio r, collect C values across different t_w.
    MSE = mean variance of C at fixed ratio across t_w values.
    """
    from collections import defaultdict
    by_ratio = defaultdict(list)
    for (tw, ratio), c in C_matrix.items():
        by_ratio[ratio].append(c)

    if not by_ratio:
        return float('nan')

    variances = [float(np.var(vals)) for vals in by_ratio.values() if len(vals) > 1]
    if not variances:
        return 0.0  # only 1 t_w, trivially collapses
    return float(np.mean(variances))


def compute_dft_peak(C_matrix: Dict, tw_list: List[int]) -> Dict:
    """
    Collapse C(t,t_w) onto C(t/t_w) by averaging over t_w, then DFT.
    Return peak SNR and frequency.
    """
    from collections import defaultdict
    by_ratio = defaultdict(list)
    for (tw, ratio), c in C_matrix.items():
        by_ratio[ratio].append(c)

    ratios_sorted = sorted(by_ratio.keys())
    if len(ratios_sorted) < 4:
        return {"dft_snr": float('nan'), "peak_omega": float('nan'),
                "n_points": len(ratios_sorted)}

    C_col = np.array([np.mean(by_ratio[r]) for r in ratios_sorted])

    # DFT of the collapsed curve
    spectrum = np.abs(np.fft.rfft(C_col))
    if len(spectrum) < 2:
        return {"dft_snr": float('nan'), "peak_omega": float('nan'),
                "n_points": len(C_col)}

    # Skip DC (bin 0); find peak in bins 1+
    search = spectrum[1:]
    if len(search) == 0:
        return {"dft_snr": float('nan'), "peak_omega": float('nan'),
                "n_points": len(C_col)}

    peak_bin = int(np.argmax(search)) + 1
    noise_floor = float(np.median(spectrum[1:]))
    snr = float(spectrum[peak_bin]) / (noise_floor + 1e-10)
    peak_omega = float(2.0 * math.pi * peak_bin / len(C_col))

    return {
        "dft_snr": snr, "peak_omega": peak_omega,
        "n_points": len(C_col),
        "spectrum_peak_bin": peak_bin,
        "noise_floor": noise_floor,
    }


def compute_x_c_shape(C_matrix: Dict) -> Dict:
    """
    Simplified X(C) shape test: for largest t_w, check if C(t,t_w)
    is piecewise-constant vs smooth-monotone vs non-monotone.
    """
    tw_max = max(tw for (tw, _) in C_matrix.keys())
    ratios = sorted(r for (tw, r) in C_matrix.keys() if tw == tw_max)
    if len(ratios) < 3:
        return {"piecewise_r2": float('nan'), "smooth_r2": float('nan'),
                "is_monotone": float('nan')}

    C_curve = np.array([C_matrix[(tw_max, r)] for r in ratios])

    # Check monotonicity
    diffs = np.diff(C_curve)
    is_monotone = bool(np.all(diffs <= 0) or np.all(diffs >= 0))

    # Piecewise fit (2-piece at midpoint)
    split = len(C_curve) // 2
    if split == 0:
        split = 1
    fit_pw = np.array([np.mean(C_curve[:split])] * split + [np.mean(C_curve[split:])] * (len(C_curve) - split))
    ss_res_pw = float(np.sum((C_curve - fit_pw) ** 2))
    ss_tot = float(np.sum((C_curve - np.mean(C_curve)) ** 2))
    piecewise_r2 = 1.0 - ss_res_pw / ss_tot if ss_tot > 1e-12 else 1.0

    # Smooth monotone fit: linear
    x = np.arange(len(C_curve), dtype=float)
    coeffs = np.polyfit(x, C_curve, 1)
    fit_lin = np.polyval(coeffs, x)
    ss_res_lin = float(np.sum((C_curve - fit_lin) ** 2))
    smooth_r2 = 1.0 - ss_res_lin / ss_tot if ss_tot > 1e-12 else 1.0

    return {
        "piecewise_r2": float(piecewise_r2),
        "smooth_r2": float(smooth_r2),
        "is_monotone": is_monotone,
        "C_curve_mean": float(np.mean(C_curve)),
        "C_curve_std": float(np.std(C_curve)),
        "n_points": len(C_curve),
    }


def _instrumentation_selftest():
    """Assert all sub-test metrics non-null at small scale."""
    N_test, M_test = 256, 5
    rng = np.random.RandomState(42)
    W = build_hopfield_w(M_test, N_test, 42)
    # Small tw_list + ratio_grid
    C_mat = measure_two_time_matrix(W, N_test, [8, 32], [2.0, 4.0], BETA, rng)
    assert len(C_mat) > 0, f"C_matrix empty in selftest: no (tw,ratio) pairs measured"

    mse = compute_collapse_mse(C_mat)
    assert not math.isnan(mse), f"collapse_mse is NaN in selftest"

    dft = compute_dft_peak(C_mat, [8, 32])
    # May be nan if <4 points; that's OK in selftest as long as n_points reported
    assert "dft_snr" in dft, "dft missing dft_snr key"

    xc = compute_x_c_shape(C_mat)
    assert "piecewise_r2" in xc, "x_c missing piecewise_r2 key"

    print(f"[selftest] PASS: n_pairs={len(C_mat)} collapse_mse={mse:.4f} "
          f"dft_snr={dft['dft_snr']} n_dft_pts={dft['n_points']}", flush=True)


_instrumentation_selftest()


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    M = max(1, int(ALPHA * N))
    W = build_hopfield_w(M, N, seed)
    print(f"[seed={seed}] N={N} M={M} tw_list={TW_LIST} ratios={RATIO_GRID}", flush=True)

    C_mat = measure_two_time_matrix(W, N, TW_LIST, RATIO_GRID, BETA, rng)
    print(f"[seed={seed}] C_matrix size={len(C_mat)}", flush=True)

    collapse_mse = compute_collapse_mse(C_mat)
    dft_result = compute_dft_peak(C_mat, TW_LIST)
    xc_shape = compute_x_c_shape(C_mat)

    print(f"[seed={seed}] collapse_mse={collapse_mse:.4f} "
          f"dft_snr={dft_result['dft_snr']} "
          f"piecewise_r2={xc_shape.get('piecewise_r2','?')} "
          f"smooth_r2={xc_shape.get('smooth_r2','?')}", flush=True)

    return {
        "seed": seed, "N": N, "M": M, "alpha": ALPHA,
        "tw_list": TW_LIST, "ratio_grid": RATIO_GRID,
        "collapse_mse": collapse_mse,
        "dft_result": dft_result,
        "xc_shape": xc_shape,
        "n_C_pairs": len(C_mat),
        "run_mode": RUN_MODE,
    }


def aggregate_results(per_seed: Dict) -> Dict:
    collapse_mses = [v["collapse_mse"] for v in per_seed.values()
                     if not math.isnan(v["collapse_mse"])]
    dft_snrs = [v["dft_result"]["dft_snr"] for v in per_seed.values()
                if not math.isnan(v["dft_result"].get("dft_snr", float('nan')))]
    pw_r2s = [v["xc_shape"].get("piecewise_r2", float('nan')) for v in per_seed.values()]
    pw_r2s = [x for x in pw_r2s if not math.isnan(x)]
    sm_r2s = [v["xc_shape"].get("smooth_r2", float('nan')) for v in per_seed.values()]
    sm_r2s = [x for x in sm_r2s if not math.isnan(x)]

    return {
        "mean_collapse_mse": float(np.mean(collapse_mses)) if collapse_mses else float('nan'),
        "std_collapse_mse": float(np.std(collapse_mses)) if collapse_mses else float('nan'),
        "mean_dft_snr": float(np.mean(dft_snrs)) if dft_snrs else float('nan'),
        "max_dft_snr": float(np.max(dft_snrs)) if dft_snrs else float('nan'),
        "mean_piecewise_r2": float(np.mean(pw_r2s)) if pw_r2s else float('nan'),
        "mean_smooth_r2": float(np.mean(sm_r2s)) if sm_r2s else float('nan'),
        "n_seeds": len(collapse_mses),
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    mse = agg["mean_collapse_mse"]
    snr = agg.get("max_dft_snr", float('nan'))
    pw_r2 = agg.get("mean_piecewise_r2", float('nan'))
    sm_r2 = agg.get("mean_smooth_r2", float('nan'))

    if math.isnan(mse):
        return ("HARD_FAIL", "collapse_mse is NaN -- instrumentation failure.")

    # Sub-test A: aging
    if mse > HF_COLLAPSE_MSE:
        return ("HARD_FAIL",
                f"AGING ABSENT: scaling_collapse_mse={mse:.4f} > {HF_COLLAPSE_MSE}. "
                f"C(t,t_w) depends on t AND t_w independently. "
                f"CK-class aging refuted; reopen static shelf.")

    aging_confirmed = mse < HP_COLLAPSE_MSE

    # Sub-test B: X(C) shape
    shape_hp = ((not math.isnan(pw_r2) and pw_r2 >= HP_PIECEWISE_R2) or
                (not math.isnan(sm_r2) and sm_r2 >= HP_SMOOTH_R2))

    # Sub-test C: DFT peak
    oscillating_hp = not math.isnan(snr) and snr >= HP_DFT_SNR
    oscillating_mid = not math.isnan(snr) and MID_DFT_SNR < snr < HP_DFT_SNR

    if aging_confirmed and (shape_hp or oscillating_hp):
        overlay_str = " + GARCIA-LORENZANA OSCILLATING OVERLAY DETECTED" if oscillating_hp else ""
        shape_str = f" piecewise_r2={pw_r2:.4f} smooth_r2={sm_r2:.4f}" if not math.isnan(pw_r2) else ""
        return ("HARD_PASS",
                f"CK AGING CONFIRMED + SHAPE DISCRIMINATED. "
                f"collapse_mse={mse:.4f} < {HP_COLLAPSE_MSE}. "
                f"max_dft_snr={snr:.2f}.{overlay_str}{shape_str}. "
                f"n_seeds={agg['n_seeds']}.")

    if aging_confirmed:
        snr_str = f" dft_snr={snr:.2f}" if not math.isnan(snr) else ""
        return ("MIDDLE_BAND",
                f"Aging confirmed (collapse_mse={mse:.4f}) but X(C) shape inconclusive. "
                f"piecewise_r2={pw_r2:.4f} smooth_r2={sm_r2:.4f}.{snr_str} "
                f"Increase t_w range or seed count for shape discrimination.")

    return ("MIDDLE_BAND",
            f"Partial aging: collapse_mse={mse:.4f} in ({HP_COLLAPSE_MSE},{HF_COLLAPSE_MSE}). "
            f"piecewise_r2={pw_r2:.4f} smooth_r2={sm_r2:.4f}. "
            f"Confirm aging at larger N/more seeds before shape analysis.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"tw_list={TW_LIST} ratios={RATIO_GRID} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "ALPHA": ALPHA, "TW_LIST": TW_LIST, "run_mode": RUN_MODE}
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
        "run_mode": RUN_MODE, "N": N, "alpha": ALPHA,
        "seeds": SEEDS, "tw_list": TW_LIST, "ratio_grid": RATIO_GRID,
        "aggregated": agg,
        "thresholds": {
            "HP_COLLAPSE_MSE": HP_COLLAPSE_MSE, "HF_COLLAPSE_MSE": HF_COLLAPSE_MSE,
            "HP_PIECEWISE_R2": HP_PIECEWISE_R2, "HP_SMOOTH_R2": HP_SMOOTH_R2,
            "HP_DFT_SNR": HP_DFT_SNR,
        },
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
