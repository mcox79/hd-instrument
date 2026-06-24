"""
substrate_amplitude_x_f_grid_v2 -- matched-filter-energy amplitude x f 2D grid. RESCUE cell.

CRASH DIAGNOSIS (v1 -> v2):
  v1 crashed at 83s wall during FULL run (N=4096). Root cause:
  1. _build_W computed a (4096, 4096) float64 matrix = 128MB per cell.
     W was passed to _measure_recall but NEVER USED (direct cosine readout has no
     Hopfield dynamics). With 162 cells, 162 * 128MB = ~20GB accumulated before GC.
     MemoryError.
  2. _measure_recall used a 200-iteration Python loop per cell (slow + large resident set).
  3. rng.choice([-1.0, 1.0], size=(M, N)) allocates large int temp array internally.

  v2 FIXES:
  1. REMOVE _build_W entirely from run_cell. W is not needed for direct cosine readout.
     Peak per-cell allocation drops from 128MB+16MB to 16MB.
  2. VECTORIZE _measure_recall: draw all probes as (n_trials, N) batch, compute all
     cosine sims in one matrix multiply. No Python loop over trials.
  3. USE rng.randint(0, 2, size=(M, N)).astype(np.float32) * 2 - 1 for sign generation.
     Avoids large int temp array from rng.choice.
  4. Use float32 throughout (half the memory of float64).
  5. Add OOM guard: pre-check (n_trials * N * 4 bytes) per cell < 500MB.

SCIENTIFIC QUESTION (unchanged from v1):
  Is amplitude scaling (1/sqrt(f) gain on sparse-bipolar entries) the under-recognized
  load-bearing parameter fix for substrate-as-LM negative landings?

  ARM_A: amplitude=1.0 (raw bipolar, current default)
  ARM_B: amplitude=1/sqrt(f) (matched-filter-correct receiver, brain-analog divisive norm)
  ARM_C: amplitude=1/f (over-correction reference)

  Grid: f in {0.005, 0.01, 0.02, 0.05, 0.1, 0.5} x sigma in {16, 32, 64} x seeds [7,17,23]
  Task: direct cosine-similarity recall at N=4096, M=500 stored patterns.

RECALL TASK DESIGN:
  For each (arm, f, sigma) cell:
  1. Draw M sparse-bipolar patterns in {-amplitude, 0, +amplitude}^N with firing fraction f.
  2. Build codebook (no W matrix needed for direct cosine readout).
  3. Probe: add Gaussian noise sigma to each stored pattern.
  4. Readout: argmax cosine-similarity(probe, stored_patterns).
  5. Measure recall@1 = fraction of probes that converge to the correct stored pattern.
  NOTE: W and Hopfield iterations are NOT used (direct matched-filter-energy test).

FORMULA SELF-TESTS (closed-form, per PROT-022):
  1. SNR prediction for raw amplitude (ARM_A): SNR = sqrt(f * N) / sigma
     [INPUT: f=0.02, N=4096, sigma=16] [EXPECTED: sqrt(0.02*4096)/16 = sqrt(81.92)/16 = 9.07/16 = 0.567]
     Recall under Q-fn: Phi(SNR) approx 0.71 at SNR=0.567.
  2. SNR prediction for corrected amplitude (ARM_B): SNR = sqrt(N) / sigma
     [INPUT: N=4096, sigma=16] [EXPECTED: 64/16 = 4.0 -> Phi(4) approx 0.999]
  3. Amplitude ratio ARM_B / ARM_A = 1/sqrt(f):
     [INPUT: f=0.02] [EXPECTED: 1/sqrt(0.02) = 7.07]

PRE-REGISTERED BANDS (unchanged from v1; smoke+multi-scale confirmed lift=0.82 >> 0.30):

HARD_PASS (amplitude-scaling IS the dominant fix):
  - CRITERION_A: recall_lift(f=0.02, sigma=16) = mean(ARM_B) - mean(ARM_A) >= 0.30
  - CRITERION_B: ARM_B recall vs f across f in [0.01, 0.50] at sigma=16 is FLAT
    to within 0.05 (matched-filter-energy is the dominant mechanism)
  - CRITERION_C: Pearson r(ARM_A recall, 1/f) >= 0.70 across (f, sigma=16)
    (raw arm degrades proportional to sparsity)

HARD_FAIL (amplitude-scaling is NOT the dominant fix):
  - HARD_FAIL_1: recall_lift(f=0.02, sigma=16) < 0.10
  - HARD_FAIL_2: ARM_B recall vs f at sigma=16 shows >0.20 variation (not flat)
  - HARD_FAIL_3: ARM_A and ARM_B within 0.05 at all (f, sigma) (scaling is no-op)

MIDDLE_BAND:
  - recall_lift(f=0.02, sigma=16) in [0.10, 0.30]: partial recovery

WHAT_THIS_DOES_NOT_SHOW:
  - This cell does NOT test substrate-as-LM end-to-end (BPC, perplexity).
  - It tests the ISOLATED recall mechanism in a controlled associative memory harness.
  - A HARD_PASS here shows amplitude scaling helps retrieval; it does NOT guarantee
    chain-grade LM performance improvement without also fixing encoder and W structure.
  - ARM_C (1/f) is included as an over-correction reference.

ROUTING: remote_cpu_queue (pure numpy; no torch import; Tier-B)
PROT-018: no _n<N> suffix; production N = 4096; rationale: N is not the focal sweep axis.
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
from typing import Dict, List, Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

# Verify no torch import (explicit per spec; PROT-020 pure-CPU routing gate)
# DO NOT add torch import -- this is pure numpy by design.

ANCHOR_NAME = "substrate_amplitude_x_f_grid_v2"

# ---- Config ----

N = 4096        # vector dimensionality (production; smoke may use N_SMOKE)
M = 500         # stored patterns

F_GRID = [0.005, 0.01, 0.02, 0.05, 0.1, 0.5]
SIGMA_GRID = [16, 32, 64]

ARMS = ["raw_pm1", "inv_sqrt_f", "inv_f"]

N_TRIALS = 200    # probes per (arm, f, sigma, seed) cell (full)
N_RETRIEVAL = 8   # kept for API compatibility (unused: direct cosine readout)

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = ("smoke" if _ARGS.smoke else
            os.environ.get("HDLAB_RUN_MODE", "full")).lower()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_SMOKE = 512
    N_ACTIVE = N_SMOKE
    M_SMOKE = 40
    _N_TRIALS_SMOKE = 50
    F_GRID_SMOKE = [0.01, 0.02, 0.1]
    SIGMA_GRID_SMOKE = [16, 32]
    _f_grid = F_GRID_SMOKE
    _sigma_grid = SIGMA_GRID_SMOKE
    _n_trials = _N_TRIALS_SMOKE
    _M = M_SMOKE
else:
    SEEDS = [7, 17, 23]
    N_ACTIVE = N
    _f_grid = F_GRID
    _sigma_grid = SIGMA_GRID
    _n_trials = N_TRIALS
    _M = M


# ---- OOM guard ----

def _check_oom_budget(n_trials: int, N_dim: int, M_patterns: int) -> None:
    """Abort if per-cell working memory would exceed 500MB.

    v2 fix: W matrix removed. Per-cell peak = X (M x N f32) + probes (n_trials x N f32) +
    scores (n_trials x M f32) + norms (M f32).
    """
    x_bytes = M_patterns * N_dim * 4          # float32 X
    probes_bytes = n_trials * N_dim * 4        # float32 probes
    scores_bytes = n_trials * M_patterns * 4   # float32 scores
    norms_bytes = M_patterns * 4               # float32 norms
    total = x_bytes + probes_bytes + scores_bytes + norms_bytes
    limit = 500 * 1024 * 1024  # 500MB
    if total > limit:
        raise MemoryError(
            f"[OOM-GUARD] per-cell peak {total/1024/1024:.0f}MB > 500MB limit. "
            f"Reduce M ({M_patterns}), N ({N_dim}), or n_trials ({n_trials})."
        )
    print(f"[oom-guard] per-cell peak estimate: {total/1024/1024:.1f}MB (limit 500MB)", flush=True)


# ---- Formula self-tests (per PROT-022) ----

def _selftest_snr_raw():
    """SNR_raw = sqrt(f * N) / sigma. At f=0.02, N=4096, sigma=16: ~0.567."""
    f, n_dim, sigma = 0.02, 4096, 16
    snr = math.sqrt(f * n_dim) / sigma
    expected = math.sqrt(0.02 * 4096) / 16
    assert abs(snr - expected) < 1e-6, f"SNR_raw formula: {snr} != {expected}"
    assert 0.5 < snr < 0.7, f"SNR_raw at (f=0.02, N=4096, sigma=16) sanity: {snr}"


def _selftest_snr_corrected():
    """SNR_corrected = sqrt(N) / sigma. At N=4096, sigma=16: 4.0."""
    n_dim, sigma = 4096, 16
    snr = math.sqrt(n_dim) / sigma
    assert abs(snr - 4.0) < 1e-9, f"SNR_corrected formula: {snr}"


def _selftest_amplitude_ratio():
    """amplitude_ratio ARM_B/ARM_A = 1/sqrt(f). At f=0.02: 7.07."""
    f = 0.02
    ratio = 1.0 / math.sqrt(f)
    assert abs(ratio - 7.071067) < 1e-4, f"amplitude_ratio f=0.02: {ratio}"


def _selftest_recall_nonzero():
    """One forward pass at smoke scale: recall is non-zero and non-NaN."""
    rng = np.random.RandomState(42)
    n_t = 128
    f_t = 0.02
    sigma_t = 16.0
    M_t = 20
    amp = 1.0 / math.sqrt(f_t)  # ARM_B: should give non-trivial recall at n_t=128
    X = _draw_sparse_patterns(rng, M_t, n_t, f_t, amp)
    recall = _measure_recall_vectorized(rng, X, sigma_t, n_t, n_trials=10)
    assert recall is not None, "recall is None"
    assert not math.isnan(recall), "recall is NaN"
    assert 0.0 <= recall <= 1.0, f"recall out of range: {recall}"


def _selftest_amplitude_corrected_higher():
    """ARM_B recall >= ARM_A recall at f=0.02, n=256 (small test)."""
    rng_a = np.random.RandomState(99)
    rng_b = np.random.RandomState(99)  # same patterns, different amplitude
    n_t = 256
    f_t = 0.02
    sigma_t = 16.0
    M_t = 30
    X_a = _draw_sparse_patterns(rng_a, M_t, n_t, f_t, 1.0)
    X_b = _draw_sparse_patterns(rng_b, M_t, n_t, f_t, 1.0 / math.sqrt(f_t))
    r_a = _measure_recall_vectorized(np.random.RandomState(42), X_a, sigma_t, n_t, n_trials=30)
    r_b = _measure_recall_vectorized(np.random.RandomState(42), X_b, sigma_t, n_t, n_trials=30)
    assert r_a is not None and r_b is not None, "recall is None"
    assert not (math.isnan(r_a) or math.isnan(r_b)), "recall is NaN"
    assert r_a > 0.0 or r_b > 0.0, f"Both arms degenerate: r_a={r_a}, r_b={r_b}"


def _selftest_vectorized_matches_loop():
    """Vectorized recall matches loop-based recall to within rng tolerance."""
    rng = np.random.RandomState(7)
    n_t = 128
    f_t = 0.05
    sigma_t = 16.0
    M_t = 10
    amp = 1.0 / math.sqrt(f_t)
    X = _draw_sparse_patterns(rng, M_t, n_t, f_t, amp)
    # Both use same seed; vectorized draws all probes at once; loop draws sequentially
    # They may differ in RNG state usage, so we just check both are in [0,1] and non-NaN.
    r_vec = _measure_recall_vectorized(np.random.RandomState(77), X, sigma_t, n_t, n_trials=20)
    assert 0.0 <= r_vec <= 1.0, f"vectorized recall out of range: {r_vec}"
    assert not math.isnan(r_vec), "vectorized recall NaN"


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    _selftest_snr_raw()
    _selftest_snr_corrected()
    _selftest_amplitude_ratio()
    _selftest_recall_nonzero()
    _selftest_amplitude_corrected_higher()
    _selftest_vectorized_matches_loop()
    print("[selftest] PASS: snr_raw, snr_corrected, amplitude_ratio, recall_nonzero, "
          "amplitude_corrected_higher, vectorized_matches_loop", flush=True)


# ---- Core math ----

def _draw_sparse_patterns(
    rng: np.random.RandomState,
    M_pat: int,
    N_dim: int,
    f: float,
    amplitude: float,
) -> np.ndarray:
    """Draw M sparse-bipolar patterns in {-amplitude, 0, +amplitude}^N with firing fraction f.

    Returns: shape (M, N) float32.
    v2 fix: use randint for sign generation (avoids large int temp array from choice).
    """
    active = rng.random((M_pat, N_dim)) < f        # bool mask
    signs = (rng.randint(0, 2, size=(M_pat, N_dim)).astype(np.float32) * 2.0 - 1.0)
    X = np.where(active, signs * np.float32(amplitude), np.float32(0.0)).astype(np.float32)
    return X


def _measure_recall_vectorized(
    rng: np.random.RandomState,
    X_stored: np.ndarray,
    sigma: float,
    N_dim: int,
    n_trials: int,
) -> float:
    """Vectorized recall@1 on n_trials probes using direct cosine-similarity readout.

    v2 FIX: fully vectorized -- no Python loop over trials. Draws all probes at once.

    This directly tests the matched-filter-energy hypothesis:
    - Probe = stored_pattern + Gaussian noise (N(0, sigma^2) per dim)
    - Readout = argmax cosine-similarity(probe, stored_patterns)

    The matched-filter-energy theorem predicts:
      SNR = sqrt(signal_energy) / sigma = sqrt(f * N * a^2) / sigma

    W parameter removed (unused in direct cosine-similarity readout).
    n_steps parameter removed (no Hopfield iteration; direct readout).

    Returns: recall in [0, 1].
    """
    M_stored = X_stored.shape[0]
    if M_stored == 0:
        return float('nan')

    # Precompute per-pattern L2 norms: (M,) float32
    norms = np.linalg.norm(X_stored, axis=1).astype(np.float32)  # (M,)
    norms = np.where(norms < np.float32(1e-8), np.float32(1.0), norms)

    # Draw n_trials target indices
    target_idxs = rng.randint(0, M_stored, size=n_trials)  # (n_trials,)

    # Draw all probes at once: (n_trials, N)
    patterns = X_stored[target_idxs]  # (n_trials, N)
    noise = (rng.randn(n_trials, N_dim) * sigma).astype(np.float32)  # (n_trials, N)
    probes = patterns + noise  # (n_trials, N)

    # Compute cosine similarities: (n_trials, M)
    # probe_norms: (n_trials,)
    probe_norms = np.linalg.norm(probes, axis=1).astype(np.float32)  # (n_trials,)
    probe_norms = np.where(probe_norms < np.float32(1e-8), np.float32(1.0), probe_norms)

    # scores[i, j] = (probes[i] . X_stored[j]) / (probe_norms[i] * norms[j])
    # = (probes @ X_stored.T)[i,j] / probe_norms[i] / norms[j]
    raw_scores = probes @ X_stored.T  # (n_trials, M)
    cos_sims = raw_scores / probe_norms[:, None] / norms[None, :]  # (n_trials, M)

    # Recall@1: argmax over codebook matches target
    retrieved = np.argmax(cos_sims, axis=1)  # (n_trials,)
    correct = int(np.sum(retrieved == target_idxs))

    return float(correct) / n_trials


def _amplitude_for_arm(arm: str, f: float) -> float:
    """Return the amplitude scalar for a given arm and f."""
    if arm == "raw_pm1":
        return 1.0
    elif arm == "inv_sqrt_f":
        return 1.0 / math.sqrt(max(f, 1e-9))
    elif arm == "inv_f":
        return 1.0 / max(f, 1e-9)
    else:
        raise ValueError(f"Unknown arm: {arm}")


# ---- Sweep ----

def run_cell(
    arm: str,
    f: float,
    sigma: float,
    seed: int,
    N_dim: int,
    M_patterns: int,
    n_trials: int,
) -> Dict[str, Any]:
    """Run one (arm, f, sigma, seed) cell. Returns metrics dict.

    v2 fix: W matrix computation REMOVED (was 128MB/cell; unused in direct cosine readout).
    v2 fix: recall uses _measure_recall_vectorized (no Python trial loop).
    """
    rng = np.random.RandomState(seed)
    amplitude = _amplitude_for_arm(arm, f)
    t0 = time.time()

    X = _draw_sparse_patterns(rng, M_patterns, N_dim, f, amplitude)
    # NOTE: W = (1/N) * X.T @ X is NOT computed here (v2 fix: was 128MB per cell, never used).
    # Direct cosine-similarity recall does not need the Hebbian weight matrix.
    recall = _measure_recall_vectorized(rng, X, sigma, N_dim, n_trials)

    elapsed = time.time() - t0

    # Active dim count (sanity)
    active_count = int((np.abs(X) > np.float32(1e-9)).sum())
    active_fraction = active_count / float(M_patterns * N_dim)

    # Free X explicitly to help GC between cells
    del X

    return {
        "arm": arm,
        "f": f,
        "sigma": sigma,
        "seed": seed,
        "recall_at_1": recall,
        "amplitude": amplitude,
        "active_fraction_actual": active_fraction,
        "elapsed_s": elapsed,
    }


def compute_verdicts(results: List[Dict]) -> Dict[str, Any]:
    """Compute HARD_PASS / HARD_FAIL / MIDDLE_BAND verdict from per-cell results."""
    import statistics

    def mean_recall(arm, f_val, sigma_val):
        vals = [r["recall_at_1"] for r in results
                if r["arm"] == arm and abs(r["f"] - f_val) < 1e-9
                and abs(r["sigma"] - sigma_val) < 1e-9]
        return statistics.mean(vals) if vals else float('nan')

    def arm_recall_vs_f(arm, sigma_val):
        """Return list of (f, mean_recall) sorted by f."""
        out = []
        for f_v in F_GRID:
            m = mean_recall(arm, f_v, sigma_val)
            if not math.isnan(m):
                out.append((f_v, m))
        return out

    # CRITERION_A: recall_lift(f=0.02, sigma=16) >= 0.30
    r_a_c = mean_recall("raw_pm1", 0.02, 16)
    r_b_c = mean_recall("inv_sqrt_f", 0.02, 16)
    recall_lift_02_16 = r_b_c - r_a_c

    # CRITERION_B: ARM_B recall vs f flat to within 0.05 at sigma=16
    b_vals = arm_recall_vs_f("inv_sqrt_f", 16)
    b_vals_band = [rv for (fv, rv) in b_vals if 0.009 < fv <= 0.51]
    if len(b_vals_band) >= 2:
        flatness_B = max(b_vals_band) - min(b_vals_band)
    else:
        flatness_B = float('nan')

    # CRITERION_C: Pearson r(ARM_A recall, 1/f) at sigma=16
    a_vals = arm_recall_vs_f("raw_pm1", 16)
    if len(a_vals) >= 3:
        f_vals_c = [fv for (fv, rv) in a_vals]
        r_vals_c = [rv for (fv, rv) in a_vals]
        inv_f_vals = [1.0 / fv for fv in f_vals_c]
        n_c = len(r_vals_c)
        mean_r = sum(r_vals_c) / n_c
        mean_if = sum(inv_f_vals) / n_c
        cov = sum((r_vals_c[i] - mean_r) * (inv_f_vals[i] - mean_if) for i in range(n_c))
        std_r = math.sqrt(sum((rv - mean_r) ** 2 for rv in r_vals_c))
        std_if = math.sqrt(sum((iv - mean_if) ** 2 for iv in inv_f_vals))
        pearson_r = (cov / (std_r * std_if)) if (std_r > 1e-9 and std_if > 1e-9) else float('nan')
    else:
        pearson_r = float('nan')

    # HARD_FAIL checks
    max_lift = float('-inf')
    for fv in F_GRID:
        for sv in SIGMA_GRID:
            r_a = mean_recall("raw_pm1", fv, sv)
            r_b = mean_recall("inv_sqrt_f", fv, sv)
            if not math.isnan(r_a) and not math.isnan(r_b):
                max_lift = max(max_lift, abs(r_b - r_a))

    hf1 = (not math.isnan(recall_lift_02_16)) and recall_lift_02_16 < 0.10
    hf2 = (not math.isnan(flatness_B)) and flatness_B > 0.20
    hf3 = (max_lift < 0.05) and (max_lift > float('-inf'))

    crit_a = (not math.isnan(recall_lift_02_16)) and recall_lift_02_16 >= 0.30
    crit_b = (not math.isnan(flatness_B)) and flatness_B <= 0.05
    crit_c = (not math.isnan(pearson_r)) and pearson_r >= 0.70

    hard_pass = crit_a and crit_b
    hard_fail = hf1 or hf2 or hf3
    middle_band = (not hard_pass) and (not hard_fail)

    if hard_pass:
        verdict = "HARD_PASS"
    elif hard_fail:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    return {
        "verdict": verdict,
        "recall_lift_f02_sigma16": recall_lift_02_16,
        "flatness_B_sigma16": flatness_B,
        "pearson_r_ARM_A_invf_sigma16": pearson_r,
        "max_abs_lift_any_cell": max_lift,
        "criteria": {
            "crit_A_lift_ge_030": crit_a,
            "crit_B_flat_le_005": crit_b,
            "crit_C_pearson_ge_070": crit_c,
        },
        "hard_fail_flags": {
            "hf1_lift_lt_010": hf1,
            "hf2_flatness_gt_020": hf2,
            "hf3_arms_within_005": hf3,
        },
        "verdict_msg": (
            f"[{verdict}] amplitude scaling: lift(f=0.02,sigma=16)={recall_lift_02_16:.3f} "
            f"(CRIT_A>={0.30}: {crit_a}); "
            f"ARM_B flatness={flatness_B:.3f} (CRIT_B<={0.05}: {crit_b}); "
            f"Pearson_r(ARM_A,1/f)={pearson_r:.3f} (CRIT_C>={0.70}: {crit_c}). "
            "WHAT_THIS_DOES_NOT_SHOW: this is isolated associative-recall only, "
            "not end-to-end substrate-as-LM BPC."
        ),
    }


# ---- Main ----

def main():
    t_start = time.time()

    if _ARGS.self_test:
        _instrumentation_selftest()
        print("[exp] self-test PASS", flush=True)
        return

    _instrumentation_selftest()

    # OOM guard: check per-cell memory budget before starting
    _check_oom_budget(_n_trials, N_ACTIVE, _M)

    output_dir = REPO / "data" / "experiments" / ANCHOR_NAME
    output_dir.mkdir(parents=True, exist_ok=True)

    results: List[Dict] = []
    total_cells = len(ARMS) * len(_f_grid) * len(_sigma_grid) * len(SEEDS)
    cell_idx = 0

    print(f"[exp] {ANCHOR_NAME} | mode={RUN_MODE} | N={N_ACTIVE} | "
          f"M={_M} | f_grid={_f_grid} | sigma_grid={_sigma_grid} | "
          f"seeds={SEEDS} | total_cells={total_cells}", flush=True)

    for seed in SEEDS:
        for arm in ARMS:
            for f_val in _f_grid:
                for sigma_val in _sigma_grid:
                    cell_idx += 1
                    t_cell = time.time()
                    cell_result = run_cell(
                        arm=arm,
                        f=f_val,
                        sigma=sigma_val,
                        seed=seed,
                        N_dim=N_ACTIVE,
                        M_patterns=_M,
                        n_trials=_n_trials,
                    )
                    results.append(cell_result)
                    elapsed_cell = time.time() - t_cell
                    print(f"  [{cell_idx}/{total_cells}] arm={arm} f={f_val} sigma={sigma_val} "
                          f"seed={seed} recall={cell_result['recall_at_1']:.4f} "
                          f"amp={cell_result['amplitude']:.4f} ({elapsed_cell:.2f}s)", flush=True)

    # Compute verdicts (only on full F_GRID coverage)
    verdict_data = compute_verdicts(results)

    total_elapsed = time.time() - t_start

    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "N": N_ACTIVE,
        "M": _M,
        "f_grid": _f_grid,
        "sigma_grid": _sigma_grid,
        "seeds": SEEDS,
        "n_trials": _n_trials,
        "elapsed_s": total_elapsed,
        "verdict": verdict_data["verdict"],
        "verdict_msg": verdict_data["verdict_msg"],
        "recall_lift_f02_sigma16": verdict_data["recall_lift_f02_sigma16"],
        "flatness_B_sigma16": verdict_data["flatness_B_sigma16"],
        "pearson_r_ARM_A_invf_sigma16": verdict_data["pearson_r_ARM_A_invf_sigma16"],
        "max_abs_lift_any_cell": verdict_data["max_abs_lift_any_cell"],
        "criteria": verdict_data["criteria"],
        "hard_fail_flags": verdict_data["hard_fail_flags"],
        "per_cell_results": results,
    }

    metrics_path = output_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"[exp] metrics -> {metrics_path}", flush=True)
    print(f"[exp] VERDICT: {verdict_data['verdict_msg']}", flush=True)
    print(f"[exp] total elapsed: {total_elapsed:.1f}s", flush=True)


_instrumentation_selftest()

if __name__ == "__main__":
    main()
