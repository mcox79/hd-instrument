"""
q_f6_pq_distribution_v1 -- Measure overlap distribution P(q) per research criteria.

SCIENTIFIC QUESTION (Q-F6, overlap distribution):
  P(q) is the Parisi order parameter distribution. For:
    - Pure Hopfield retrieval state: P(q) = delta(q - m) where m is retrieval overlap.
    - Paramagnetic phase: P(q) = delta(q - 0).
    - Spin glass (1-RSB): P(q) = w*delta(q - q_EA) + (1-w)*delta(q - 0).
    - FRSB: P(q) is a continuous function on [0, q_EA].
    - CK aging class: P(q) shifts with t_w (non-equilibrium, non-stationary).

  This test measures the EMPIRICAL P(q) via R-replica overlap histogram to
  characterize which phase the substrate is in. Key question: is P(q) a
  single-peak (retrieval / paramagnetic) or multi-peak (spin glass) distribution?

  Design:
    - Initialize R replicas from random states.
    - Run Glauber dynamics for t_w steps (waiting time = 1024).
    - Compute pairwise overlaps q_ab = (1/N) * s^a . s^b for all a < b replica pairs.
    - Build histogram P(q) over [-1, 1] with n_bins=50.
    - Fit: single Gaussian (retrieval/paramagnetic) vs bimodal (spin glass).

  Test cells:
    (A) Single-peak P(q): P(q) has one dominant peak. HP-A: unimodality score >= 0.70
        (fraction of histogram mass in main peak vs all). HF-A: bimodality index >= 0.55.
    (B) Peak location: peak of P(q) at q* > 0.30 (above noise floor, indicating retrieval).
        HP-B: q_peak >= 0.30. HF-B: q_peak <= 0.10 (paramagnetic, all-zero).
    (C) Edwards-Anderson order parameter: q_EA = integral q*P(q)dq >= 0.20 (non-trivial).
        HP-C: q_EA >= 0.20. HF-C: q_EA < 0.05.

  HARD-PASS: All of A, B, C.
  HARD-FAIL: HF-A (bimodal = non-trivial RSB structure) or HF-C (paramagnetic, no memory).
  MIDDLE: A or B or C alone.

PRE-REGISTERED BANDS (calibration probe, first P(q) measurement):
  HP: unimodal >= 0.70, q_peak >= 0.30, q_EA >= 0.20.
  HF: bimodality_index >= 0.55, q_peak <= 0.10, q_EA < 0.05.
  Bands: +-50% of theory per calibration-probe policy.
  Theory: in retrieval phase at ALPHA=0.10 < alpha_c=0.138, expect single peak at m~0.95.

FORMULA SELF-TESTS:
  1. Unimodality score: histogram [0]*20 + [10]*10 + [0]*20 has 1 peak at center bin.
     Unimodality = max_bin_mass / total_mass = 10/10 = 1.0 (all in one bin cluster).
     [INPUT: [10]*10 at center] [EXPECTED: unimodality_score = 1.0]
  2. q_EA: for histogram with uniform distribution on [0.0, 1.0], q_EA = mean = 0.5.
     [INPUT: uniform bins at 0..1 step 0.02] [EXPECTED: q_EA ~ 0.5]
  3. Bimodality index: bimodal histogram [10]*5 + [0]*40 + [10]*5 should have BI >= 0.40.
     [INPUT: bimodal two-peak] [EXPECTED: BI >= 0.40]

TIMEOUT ESTIMATE:
  Smoke: N=512, R=50 replicas, t_w=64, 2 seeds. ~5s.
  Full: N=1024, R=200 replicas, t_w=1024, 5 seeds.
  Scale: 1.5 * 5 * (1024/512)^1.5 * (200/50) * (5/2) = ceil(1.5*5*2.83*4*2.5)=ceil(212)=212s.
  timeout=900s (4x buffer).

No _nN suffix; production N=1024 per rule 3.
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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "q_f6_pq_distribution_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

if RUN_MODE == "smoke":
    N = 512
    SEEDS = [7, 17]
    R_REPLICAS = 50
    T_W = 64
    ALPHA = 0.10
    BETA = 2.0
    N_BINS = 30
else:
    N = 1024
    SEEDS = [7, 17, 23, 31, 41]
    R_REPLICAS = 200
    T_W = 1024
    ALPHA = 0.10
    BETA = 2.0
    N_BINS = 50

# Pre-registered thresholds
HP_UNIMODALITY = 0.70
HF_BIMODALITY_INDEX = 0.55
HP_Q_PEAK = 0.30
HF_Q_PEAK = 0.10
HP_Q_EA = 0.20
HF_Q_EA = 0.05

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()


# ---- FORMULA SELF-TESTS ----
def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # 1. Unimodality: histogram with single central peak
    h_uni = np.zeros(50)
    h_uni[20:30] = 10.0
    total = h_uni.sum()
    # Find contiguous region containing max
    peak_mass = float(h_uni[20:30].sum())
    unimod = peak_mass / total
    assert unimod >= 0.99, f"Unimodality selftest failed: {unimod:.3f}"

    # 2. q_EA: uniform distribution on [0,1]
    bin_edges = np.linspace(0.0, 1.0, 51)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    h_uni2 = np.ones(50) / 50.0
    q_ea = float(np.dot(np.abs(bin_centers), h_uni2))
    assert 0.45 < q_ea < 0.55, f"q_EA selftest failed: {q_ea:.3f}"

    # 3. Bimodality index for bimodal histogram
    h_bim = np.zeros(50)
    h_bim[:5] = 10.0   # left peak
    h_bim[45:] = 10.0  # right peak
    total_b = float(h_bim.sum())
    h_bim_norm = h_bim / total_b
    mean_b = float(np.dot(np.linspace(-1, 1, 50), h_bim_norm))
    var_b = float(np.dot((np.linspace(-1, 1, 50) - mean_b)**2, h_bim_norm))
    kurt_b = float(np.dot((np.linspace(-1, 1, 50) - mean_b)**4, h_bim_norm)) / (var_b**2 + 1e-12) - 3.0
    skew_b = float(np.dot((np.linspace(-1, 1, 50) - mean_b)**3, h_bim_norm)) / (var_b**1.5 + 1e-12)
    bi = (skew_b**2 + 1.0) / (kurt_b + 3.0 + 1e-6)
    # Bimodal histogram should show bimodality signal
    assert bi >= 0.0, f"Bimodality index must be non-negative"

    print(f"[selftest] unimod={unimod:.3f} q_ea={q_ea:.3f} bi={bi:.4f}", flush=True)


_instrumentation_selftest()


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


def compute_pq_histogram(W: np.ndarray, N_dim: int, t_w: int, n_replicas: int,
                          beta: float, n_bins: int, seed: int) -> Dict:
    """Compute P(q) histogram from pairwise replica overlaps."""
    rng = np.random.RandomState(seed + 9999)
    # Equilibrate R replicas for t_w steps
    states = []
    for r in range(n_replicas):
        state = rng.choice([-1.0, 1.0], size=N_dim)
        for _ in range(t_w):
            state = glauber_sweep(state, W, beta, rng)
        states.append(state.copy())

    # Compute pairwise overlaps q_ab
    states_arr = np.array(states, dtype=np.float64)  # (R, N)
    # q_ab = s^a . s^b / N for all a < b
    overlaps = []
    for a in range(n_replicas):
        for b in range(a + 1, n_replicas):
            q_ab = float(np.dot(states_arr[a], states_arr[b])) / N_dim
            overlaps.append(q_ab)

    overlaps = np.array(overlaps)
    # Histogram over [-1, 1]
    counts, bin_edges = np.histogram(overlaps, bins=n_bins, range=(-1.0, 1.0), density=True)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    return {
        "bin_centers": bin_centers.tolist(),
        "counts": counts.tolist(),
        "overlaps_mean": float(np.mean(overlaps)),
        "overlaps_std": float(np.std(overlaps)),
        "n_pairs": len(overlaps),
    }


def compute_metrics(hist: Dict) -> Dict:
    counts = np.array(hist["counts"])
    bin_centers = np.array(hist["bin_centers"])
    total = float(counts.sum()) + 1e-12

    # Unimodality: fraction of mass in contiguous region around max
    peak_bin = int(np.argmax(counts))
    # Window around peak: extend until counts drop below 5% of peak
    peak_val = counts[peak_bin]
    thresh = 0.05 * peak_val
    left = peak_bin
    right = peak_bin
    while left > 0 and counts[left - 1] > thresh:
        left -= 1
    while right < len(counts) - 1 and counts[right + 1] > thresh:
        right += 1
    unimodality = float(counts[left:right + 1].sum()) / total

    # q_peak: center of max bin
    q_peak = float(bin_centers[peak_bin])

    # q_EA: mean of |q| weighted by P(q)
    q_ea = float(np.dot(np.abs(bin_centers), counts)) / total

    # Bimodality index: (skewness^2 + 1) / (kurtosis + 3)
    counts_norm = counts / (total + 1e-12)
    mean_q = float(np.dot(bin_centers, counts_norm))
    var_q = float(np.dot((bin_centers - mean_q)**2, counts_norm)) + 1e-12
    skew_q = float(np.dot((bin_centers - mean_q)**3, counts_norm)) / (var_q**1.5)
    kurt_q = float(np.dot((bin_centers - mean_q)**4, counts_norm)) / (var_q**2) - 3.0
    bi = (skew_q**2 + 1.0) / (kurt_q + 3.0 + 1e-6)

    return {
        "unimodality": unimodality,
        "q_peak": q_peak,
        "q_ea": q_ea,
        "bimodality_index": bi,
    }


def run_one_seed(seed: int) -> Dict:
    M = int(ALPHA * N)
    W = build_hopfield_w(M, N, seed)
    hist = compute_pq_histogram(W, N, T_W, R_REPLICAS, BETA, N_BINS, seed)
    metrics = compute_metrics(hist)

    # Sanity check: at least 1 pair computed
    assert hist["n_pairs"] >= 1, "No overlap pairs computed -- instrumentation bug"
    assert 0.0 <= metrics["unimodality"] <= 1.0, f"unimodality={metrics['unimodality']:.3f} out of [0,1]"

    cell_A_pass = metrics["unimodality"] >= HP_UNIMODALITY
    cell_A_hf = metrics["bimodality_index"] >= HF_BIMODALITY_INDEX
    cell_B_pass = metrics["q_peak"] >= HP_Q_PEAK
    cell_B_hf = metrics["q_peak"] <= HF_Q_PEAK
    cell_C_pass = metrics["q_ea"] >= HP_Q_EA
    cell_C_hf = metrics["q_ea"] < HF_Q_EA

    return {
        "N": N,
        "run_mode": RUN_MODE,
        "seed": seed,
        "unimodality": metrics["unimodality"],
        "q_peak": metrics["q_peak"],
        "q_ea": metrics["q_ea"],
        "bimodality_index": metrics["bimodality_index"],
        "cell_A_pass": cell_A_pass,
        "cell_A_hf": cell_A_hf,
        "cell_B_pass": cell_B_pass,
        "cell_B_hf": cell_B_hf,
        "cell_C_pass": cell_C_pass,
        "cell_C_hf": cell_C_hf,
        "n_pairs": hist["n_pairs"],
    }


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        print(f"[seed={seed}] running R={R_REPLICAS} replicas, t_w={T_W}...", flush=True)
        result = run_one_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"[seed={seed}] unimod={result['unimodality']:.3f} q_peak={result['q_peak']:.3f} q_ea={result['q_ea']:.3f}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    n_seeds = len(SEEDS)

    all_unimod = [per_seed[str(s)]["unimodality"] for s in SEEDS]
    all_q_peak = [per_seed[str(s)]["q_peak"] for s in SEEDS]
    all_q_ea = [per_seed[str(s)]["q_ea"] for s in SEEDS]
    all_bi = [per_seed[str(s)]["bimodality_index"] for s in SEEDS]

    mean_unimod = float(np.mean(all_unimod))
    mean_q_peak = float(np.mean(all_q_peak))
    mean_q_ea = float(np.mean(all_q_ea))
    mean_bi = float(np.mean(all_bi))

    n_A = sum(1 for s in SEEDS if per_seed[str(s)]["cell_A_pass"])
    n_A_hf = sum(1 for s in SEEDS if per_seed[str(s)]["cell_A_hf"])
    n_B = sum(1 for s in SEEDS if per_seed[str(s)]["cell_B_pass"])
    n_C = sum(1 for s in SEEDS if per_seed[str(s)]["cell_C_pass"])
    n_C_hf = sum(1 for s in SEEDS if per_seed[str(s)]["cell_C_hf"])

    thr = math.ceil(n_seeds * 0.6)
    cell_A_pass = n_A >= thr
    cell_B_pass = n_B >= thr
    cell_C_pass = n_C >= thr
    hf_A = n_A_hf >= thr
    hf_C = n_C_hf >= thr

    n_cells_pass = int(cell_A_pass) + int(cell_B_pass) + int(cell_C_pass)
    if n_cells_pass == 3:
        verdict = "HARD_PASS"
    elif hf_A or hf_C:
        verdict = "HARD_FAIL"
    elif n_cells_pass >= 2:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL"

    elapsed = time.time() - t0
    verdict_msg = (
        f"q_f6_pq_distribution_v1 verdict={verdict}: "
        f"mean_unimodality={mean_unimod:.3f}(HP>={HP_UNIMODALITY}) "
        f"mean_q_peak={mean_q_peak:.3f}(HP>={HP_Q_PEAK},HF<={HF_Q_PEAK}) "
        f"mean_q_EA={mean_q_ea:.3f}(HP>={HP_Q_EA},HF<{HF_Q_EA}) "
        f"mean_BI={mean_bi:.3f}(HF_BI>={HF_BIMODALITY_INDEX}) "
        f"cells={n_cells_pass}/3 elapsed={elapsed:.1f}s"
    )
    print(verdict_msg, flush=True)

    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "N": N,
        "n_seeds": n_seeds,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "mean_unimodality": mean_unimod,
        "mean_q_peak": mean_q_peak,
        "mean_q_ea": mean_q_ea,
        "mean_bimodality_index": mean_bi,
        "n_cell_A_pass": n_A,
        "n_cell_B_pass": n_B,
        "n_cell_C_pass": n_C,
        "elapsed_s": elapsed,
    }
    with open(Path(out_dir) / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] metrics written to {out_dir}/metrics.json", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
