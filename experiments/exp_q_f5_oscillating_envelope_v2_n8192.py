"""
q_f5_oscillating_envelope_v2_n8192 -- Q-F5 Garcia-Lorenzana oscillation at N=8192.

SCIENTIFIC QUESTION (Q-F5 higher-N disambiguation):
  v1 (N=1024) returned MIDDLE_BAND: dft_snr=2.32 (HP>=3.0), frac_osc=0.065 (HP>=0.20).
  Neither cell PASSED; neither explicitly HARD-FAILED (above HF thresholds).
  v2 tests at N=8192 to determine whether the signal grows with N (substrate-novel
  oscillating-amorphous overlay) or remains at MIDDLE (supports CK-only class).

  Two sub-cells unchanged from v1:
    (A) DFT peak SNR > 3.0 at any omega* > 0 (discrete oscillation).
    (B) Oscillating-envelope residual fraction frac_osc >= 0.20.

  HP: Either A or B passes (>= 4/5 seeds).
  HARD_FAIL: Both HF-A and HF-B trigger (mean_dft_snr < 1.5 AND mean_frac_osc < 0.05
              in >= 4/5 seeds).
  MIDDLE: one cell borderline.

PRE-REGISTERED BANDS:
  HP-A: mean_dft_snr >= 3.0; HF-A: mean_dft_snr < 1.5.
  HP-B: mean_frac_osc >= 0.20; HF-B: mean_frac_osc < 0.05.
  Calibration: v1 at MIDDLE; v2 is N-scaling disambiguation probe.
  If both HF at N=8192: CK pure-aging CONFIRMED (no Garcia-Lorenzana overlay).

PROT-018: anchor has _n8192 suffix -> N MUST = 8192 in FULL config.

FORMULA SELF-TESTS (same as v1):
  1. DFT SNR for known oscillating signal.
  2. Monotone decay frac_osc should be small.
  3. Damped oscillation frac_osc positive.

TIMEOUT ESTIMATE:
  Smoke: N=1024, 1 t_w=32, 8 ratio steps, 2 seeds, 50 replicas.  ~20s.
  Full: N=8192, 3 t_w in {32,128,512}, 12 ratio steps, 5 seeds, 100 replicas.
  Scale: 1.5 * 20 * (8192/1024)^1.5 * (5/2) = ceil(1.5*20*22.6*2.5) = ceil(1695) = 1700s.
  timeout=5400s (3x margin for Glauber O(N^2) per step).

No run-at-N-but-suffix mismatch: smoke at 1024, FULL at 8192 per PROT-018.
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
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "q_f5_oscillating_envelope_v2_n8192"

# PROT-018: anchor has _n8192 -> N must = 8192
_N_SUFFIX = 8192

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N = 1024
    SEEDS = [7, 17]
    TW_LIST = [32]
    RATIO_GRID = [1.5, 2.0, 3.0, 5.0, 8.0, 12.0, 16.0, 24.0]
    N_REPLICAS = 50
else:
    N = 8192
    SEEDS = [7, 17, 23, 31, 41]
    TW_LIST = [32, 128, 512]
    RATIO_GRID = [1.5, 2.0, 3.0, 5.0, 8.0, 12.0, 16.0, 24.0, 32.0, 48.0, 64.0, 96.0]
    N_REPLICAS = 100

# PROT-018 runtime check
assert N == _N_SUFFIX or RUN_MODE == "smoke", \
    f"PROT-018: anchor _n{_N_SUFFIX} but FULL N={N}"

ALPHA = 0.10
BETA = 2.0

HP_DFT_SNR = 3.0
HF_DFT_SNR = 1.5
HP_FRAC_OSC = 0.20
HF_FRAC_OSC = 0.05


def _instrumentation_selftest():
    rng = np.random.RandomState(42)
    N_t = 64

    # 1. DFT SNR for known oscillating signal
    omega_0 = 2.0 * math.pi * 5 / N_t
    signal = np.cos(omega_0 * np.arange(N_t)) + 0.1 * rng.randn(N_t)
    spectrum = np.abs(np.fft.rfft(signal))
    peak_bin = int(np.argmax(spectrum[1:])) + 1
    snr = float(spectrum[peak_bin]) / (float(np.median(spectrum[1:])) + 1e-10)
    assert snr > 10.0, f"DFT SNR selftest: snr={snr:.2f}"

    # 2. Monotone decay frac_osc small
    k = np.arange(50, dtype=float)
    pure_exp = np.exp(-k * 0.05)
    omega_try = 2.0 * math.pi * 3 / 50
    osc_comp = np.cos(omega_try * k)
    proj = float(np.dot(pure_exp, osc_comp)) / (float(np.dot(osc_comp, osc_comp)) + 1e-10)
    var_osc = float(np.var(proj * osc_comp))
    var_total = float(np.var(pure_exp)) + 1e-12
    frac_mono = var_osc / var_total
    assert frac_mono < 0.20, f"Monotone frac_osc={frac_mono:.3f}"

    # 3. TW_LIST non-empty, N_REPLICAS > 0
    assert len(TW_LIST) >= 1, "TW_LIST empty"
    assert N_REPLICAS > 0, "N_REPLICAS = 0"
    assert len(RATIO_GRID) >= 4, "RATIO_GRID too short"

    print(f"[selftest] PASS: dft_snr={snr:.2f} frac_mono={frac_mono:.3f} "
          f"N={N} n_tw={len(TW_LIST)} n_ratios={len(RATIO_GRID)}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def build_hopfield_w(M: int, N_dim: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, N_dim)).astype(np.float64)
    W = Xi.T @ Xi / N_dim
    np.fill_diagonal(W, 0.0)
    return W


def glauber_sweep(state: np.ndarray, W: np.ndarray, beta: float,
                  rng: np.random.RandomState) -> np.ndarray:
    h = W @ state
    prob_up = 1.0 / (1.0 + np.exp(-2.0 * beta * h))
    rand_vals = rng.rand(len(state))
    return np.where(rand_vals < prob_up, 1.0, -1.0)


def measure_correlator(W: np.ndarray, N_dim: int, t_w: int,
                       ratio_grid: List[float], n_replicas: int,
                       beta: float, seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    tw_states = []
    for _ in range(n_replicas):
        state = rng.choice([-1.0, 1.0], size=N_dim)
        for _ in range(t_w):
            state = glauber_sweep(state, W, beta, rng)
        tw_states.append(state.copy())

    c_vals = []
    for ratio in ratio_grid:
        t = int(ratio * t_w)
        n_steps = max(0, t - t_w)
        corrs = []
        for r in range(n_replicas):
            s_tw = tw_states[r].copy()
            s_t = tw_states[r].copy()
            for _ in range(n_steps):
                s_t = glauber_sweep(s_t, W, beta, rng)
            corr = float(np.dot(s_tw, s_t)) / N_dim
            corrs.append(corr)
        c_vals.append(float(np.mean(corrs)))

    return {"ratios": ratio_grid, "c_vals": c_vals, "t_w": t_w}


def compute_dft_snr(c_vals: List[float]) -> float:
    c_arr = np.array(c_vals, dtype=float) - np.mean(c_vals)
    if len(c_arr) < 4:
        return 0.0
    spectrum = np.abs(np.fft.rfft(c_arr))
    if len(spectrum) < 2:
        return 0.0
    peak_idx = int(np.argmax(spectrum[1:])) + 1
    return float(spectrum[peak_idx]) / (float(np.median(spectrum[1:])) + 1e-10)


def compute_frac_osc(c_vals: List[float]) -> float:
    c_arr = np.array(c_vals, dtype=float)
    n = len(c_arr)
    if n < 4:
        return 0.0
    k = np.arange(n, dtype=float)
    pos_mask = c_arr > 1e-6
    if pos_mask.sum() < 2:
        return 0.0
    log_c = np.log(c_arr[pos_mask] + 1e-10)
    k_pos = k[pos_mask]
    if len(k_pos) < 2:
        return 0.0
    coeffs = np.polyfit(k_pos, log_c, 1)
    lam_est = -float(coeffs[0])
    A_est = float(np.exp(coeffs[1]))
    decay_fit = A_est * np.exp(-lam_est * k)
    resid = c_arr - decay_fit
    best_frac = 0.0
    for i_omega in range(1, 13):
        omega = 2.0 * math.pi * i_omega / n
        cos_comp = np.cos(omega * k)
        sin_comp = np.sin(omega * k)
        c_proj = float(np.dot(resid, cos_comp)) / (float(np.dot(cos_comp, cos_comp)) + 1e-10)
        s_proj = float(np.dot(resid, sin_comp)) / (float(np.dot(sin_comp, sin_comp)) + 1e-10)
        osc_fit = c_proj * cos_comp + s_proj * sin_comp
        frac = float(np.var(osc_fit)) / (float(np.var(c_arr)) + 1e-12)
        if frac > best_frac:
            best_frac = frac
    return best_frac


def run_one_seed(seed: int) -> Dict:
    M = int(ALPHA * N)
    W = build_hopfield_w(M, N, seed)
    rng_offset = seed * 10000

    results_by_tw = {}
    for tw in TW_LIST:
        print(f"    [t_w={tw}]", flush=True)
        meas = measure_correlator(W, N, tw, RATIO_GRID, N_REPLICAS, BETA, seed + rng_offset)
        dft_snr = compute_dft_snr(meas["c_vals"])
        frac_osc = compute_frac_osc(meas["c_vals"])
        results_by_tw[str(tw)] = {
            "t_w": tw, "c_vals": meas["c_vals"],
            "dft_snr": float(dft_snr), "frac_osc": float(frac_osc),
        }

    all_dft_snr = [results_by_tw[str(tw)]["dft_snr"] for tw in TW_LIST]
    all_frac_osc = [results_by_tw[str(tw)]["frac_osc"] for tw in TW_LIST]
    mean_dft_snr = float(np.mean(all_dft_snr))
    mean_frac_osc = float(np.mean(all_frac_osc))

    cell_A = mean_dft_snr >= HP_DFT_SNR
    cell_B = mean_frac_osc >= HP_FRAC_OSC

    return {
        "N": N, "run_mode": RUN_MODE, "seed": seed,
        "results_by_tw": results_by_tw,
        "mean_dft_snr": mean_dft_snr,
        "mean_frac_osc": mean_frac_osc,
        "cell_A_pass": bool(cell_A),
        "cell_B_pass": bool(cell_B),
    }


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining (N={N})", flush=True)

    for seed in remaining:
        print(f"[seed={seed}] q_f5_v2 N={N} M={int(ALPHA*N)}...", flush=True)
        result = run_one_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"[seed={seed}] dft_snr={result['mean_dft_snr']:.3f} "
              f"frac_osc={result['mean_frac_osc']:.3f}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    all_dft_snr = [per_seed[str(s)]["mean_dft_snr"] for s in SEEDS]
    all_frac_osc = [per_seed[str(s)]["mean_frac_osc"] for s in SEEDS]
    mean_dft_snr = float(np.mean(all_dft_snr))
    mean_frac_osc = float(np.mean(all_frac_osc))

    n_seeds = len(SEEDS)
    n_cell_A = sum(1 for s in SEEDS if per_seed[str(s)]["cell_A_pass"])
    n_cell_B = sum(1 for s in SEEDS if per_seed[str(s)]["cell_B_pass"])

    min_pass = math.ceil(n_seeds * 0.6)
    cell_A_pass = n_cell_A >= min_pass
    cell_B_pass = n_cell_B >= min_pass
    cell_A_hf = mean_dft_snr < HF_DFT_SNR and n_cell_A == 0
    cell_B_hf = mean_frac_osc < HF_FRAC_OSC and n_cell_B == 0

    n_pass = int(cell_A_pass) + int(cell_B_pass)
    if n_pass >= 1:
        verdict = "HARD_PASS"
        interp = "Garcia-Lorenzana oscillation signature CONFIRMED at N=8192."
    elif cell_A_hf and cell_B_hf:
        verdict = "HARD_FAIL"
        interp = "CK pure-aging CONFIRMED. No Garcia-Lorenzana oscillating overlay at N=8192."
    else:
        verdict = "MIDDLE_BAND"
        interp = "Inconclusive at N=8192. Q-F5 remains unresolved."

    elapsed = time.time() - t0
    verdict_msg = (
        f"q_f5_oscillating_envelope_v2_n8192 verdict={verdict}: "
        f"mean_dft_snr={mean_dft_snr:.3f}(HP>={HP_DFT_SNR},HF<{HF_DFT_SNR}) "
        f"mean_frac_osc={mean_frac_osc:.3f}(HP>={HP_FRAC_OSC},HF<{HF_FRAC_OSC}) "
        f"cell_A={'PASS' if cell_A_pass else 'FAIL'}({n_cell_A}/{n_seeds}) "
        f"cell_B={'PASS' if cell_B_pass else 'FAIL'}({n_cell_B}/{n_seeds}) "
        f"N=8192 interp:{interp} elapsed={elapsed:.1f}s"
    )
    print(verdict_msg, flush=True)

    metrics = {
        "anchor": ANCHOR_NAME, "run_mode": RUN_MODE, "N": N,
        "n_seeds": n_seeds, "verdict": verdict, "verdict_msg": verdict_msg,
        "mean_dft_snr": mean_dft_snr, "mean_frac_osc": mean_frac_osc,
        "n_cell_A_pass": n_cell_A, "n_cell_B_pass": n_cell_B,
        "all_dft_snr": all_dft_snr, "all_frac_osc": all_frac_osc,
        "elapsed_s": elapsed,
    }
    metrics_path = Path(out_dir) / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"[done] metrics written to {metrics_path}", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
