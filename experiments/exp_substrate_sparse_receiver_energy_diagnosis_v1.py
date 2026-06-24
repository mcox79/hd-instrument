"""
exp_substrate_sparse_receiver_energy_diagnosis_v1

SCIENTIFIC QUESTION:
  Does matched-filter-energy loss explain the theta-gamma+brain-compose HARD_FAIL?
  Hypothesis: receiver SNR for sparse bipolar codebook scales as sqrt(f*N)/sigma.
  If true: recall vs sqrt(f*N)/sigma should collapse onto a single monotone curve
  across the (f, sigma) grid -- confirmed by Pearson r >= 0.85.

MECHANISM:
  ARM_DENSE_BASELINE:   dense bipolar codebook, 1-step Hopfield recall
  ARM_SPARSE_RAW:       sparse bipolar (f-fraction active, amplitude +/-1)
  ARM_SPARSE_AMPLIFIED: sparse bipolar (amplitude +/- 1/sqrt(f), energy restored)

  For each f in {0.005, 0.01, 0.02, 0.10, 0.5, 1.0}:
    For each sigma in {16, 32, 64, 128}:
      measure recall@1 (fraction of 200 queries correctly retrieved)

  Summary statistic: Pearson r(recall, sqrt(f*N)/sigma) across the full grid.

PRE-REGISTERED HARD BANDS:
  HARD_PASS:  Pearson r >= 0.85  (matched-filter-energy IS primary mechanism;
              routes to SECONDARY amplitude-scaled rescue cell)
  MIDDLE_BAND: r in [0.50, 0.85]  (partial; another mechanism also contributes)
  HARD_FAIL:  r < 0.50  (matched-filter-energy NOT primary; refer back to Research)

  SECONDARY pre-reg checks (loaded from research note L4 Prediction 1):
  CRITERION_B: ARM_SPARSE_RAW recall @ f=0.02, sigma=16 in [0.45, 0.75]
               (reproduces empirical 0.583 from SINGLE_LOCKIN_SPARSE arm)
  CRITERION_C: ARM_SPARSE_RAW recall @ f=0.50, sigma=16 >= 0.95
               (high-density sparse recovers near-dense; confirms f-driven)
  CRITERION_D: ARM_SPARSE_AMPLIFIED recall @ f=0.02, sigma=16 >= 0.95
               (amplitude fix restores dense-equivalent performance)

  CV < 0.05 across seeds mandatory.

CONFIG (production; N=4096):
  N=4096, M=500, seeds=[7,17,23], N_EVAL=200
  f_grid={0.005, 0.01, 0.02, 0.10, 0.5, 1.0}
  sigma_grid={16, 32, 64, 128}
  Routing: remote_cpu_queue (~30-60min)

CONFIG (smoke; N=512, tiny grid):
  N=512, M=50, f_grid={0.02, 0.50}, sigma_grid={16, 64}, seeds=[7,17]

PROT-018 N-suffix: no _n<NUMBER> suffix. Production N=4096. See config above.
ASCII-only. No emojis.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
import argparse
import time
import math
from pathlib import Path
from typing import Dict, List, Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import numpy as np
from scipy.stats import pearsonr

from experiments._seed_checkpoint import (
    get_output_dir,
    resumable_seeds,
    write_partial_key,
    aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "substrate_sparse_receiver_energy_diagnosis_v1"

RUN_MODE = (
    "smoke"
    if "--smoke" in sys.argv
    else os.environ.get("HDLAB_RUN_MODE", "full")
).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

SMOKE = RUN_MODE == "smoke"

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

if SMOKE:
    N_DIM     = 512
    M         = 50
    SEEDS     = [7, 17]
    N_EVAL    = 50
    F_GRID    = [0.02, 0.50]
    SIGMA_GRID = [16.0, 64.0]
else:
    N_DIM     = 4096
    M         = 500
    SEEDS     = [7, 17, 23]
    N_EVAL    = 200
    F_GRID    = [0.005, 0.01, 0.02, 0.10, 0.5, 1.0]
    SIGMA_GRID = [16.0, 32.0, 64.0, 128.0]


# ---------------------------------------------------------------------------
# Codebook generators
# ---------------------------------------------------------------------------

def make_dense_bipolar_codebook(M: int, N: int, rng: np.random.Generator) -> np.ndarray:
    """Dense bipolar codebook: all entries +/-1. Shape (M, N)."""
    return rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)


def make_sparse_raw_codebook(M: int, N: int, f: float, rng: np.random.Generator) -> np.ndarray:
    """Sparse bipolar codebook: fraction f active, amplitude +/-1. Shape (M, N).

    Signal energy = f * N (much less than dense energy N).
    Receiver SNR penalty = sqrt(f) at fixed sigma.
    """
    codebook = np.zeros((M, N), dtype=np.float32)
    n_active = max(1, int(round(f * N)))
    for i in range(M):
        idx = rng.choice(N, size=n_active, replace=False)
        signs = rng.choice([-1.0, 1.0], size=n_active).astype(np.float32)
        codebook[i, idx] = signs
    return codebook


def make_sparse_amplified_codebook(M: int, N: int, f: float, rng: np.random.Generator) -> np.ndarray:
    """Sparse bipolar codebook with amplitude 1/sqrt(f) so signal energy = N.

    signal_energy = n_active * amplitude^2 = f*N * (1/f) = N  (dense-equivalent).
    Receiver SNR is restored: sqrt(N)/sigma matches dense.
    """
    codebook = np.zeros((M, N), dtype=np.float32)
    n_active = max(1, int(round(f * N)))
    amplitude = float(1.0 / math.sqrt(f))
    for i in range(M):
        idx = rng.choice(N, size=n_active, replace=False)
        signs = rng.choice([-1.0, 1.0], size=n_active).astype(np.float32)
        codebook[i, idx] = signs * amplitude
    return codebook


# ---------------------------------------------------------------------------
# 1-step Hopfield recall (batched for efficiency)
# ---------------------------------------------------------------------------

def compute_recall_grid(
    codebook: np.ndarray,
    sigma_grid: List[float],
    n_eval: int,
    rng: np.random.Generator,
) -> Dict[str, float]:
    """1-step Hopfield recall@1 for a list of sigma values.

    Hoists W = codebook.T @ codebook / N once, then runs batched queries
    for all sigmas.  Returns dict {sigma_key: recall_float}.

    Store all M codebook patterns (Hebbian: W = codebook.T @ codebook / N).
    Query: pick n_eval random targets, add Gaussian noise at each sigma,
    compute W @ noisy_batch (vectorized), argmax over codebook scores.
    """
    M, N = codebook.shape
    W = (codebook.T @ codebook) / float(N)  # (N, N), hoisted once per codebook

    # Draw all targets once; queries per sigma share same targets for fairness
    target_indices = rng.integers(0, M, size=n_eval)          # (n_eval,)
    signals = codebook[target_indices]                         # (n_eval, N)

    results: Dict[str, float] = {}
    for sigma in sigma_grid:
        noise = rng.normal(0.0, sigma, size=(n_eval, N)).astype(np.float32)
        noisy = signals + noise                                # (n_eval, N)
        decoded = noisy @ W                                    # (n_eval, N)
        scores = decoded @ codebook.T                         # (n_eval, M)
        predicted = np.argmax(scores, axis=1)                  # (n_eval,)
        recall = float(np.mean(predicted == target_indices))
        results[f"sigma_{sigma}"] = recall
    return results


# ---------------------------------------------------------------------------
# Instrumentation self-test (MANDATORY per role contract)
# ---------------------------------------------------------------------------

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    rng = np.random.default_rng(0)
    N_s, M_s, f_s = 256, 20, 0.5

    # Test dense codebook + recall at low sigma is non-zero
    cb_dense = make_dense_bipolar_codebook(M_s, N_s, rng)
    results_dense = compute_recall_grid(cb_dense, [4.0, 64.0], n_eval=30, rng=np.random.default_rng(10))
    r_dense_low = results_dense["sigma_4.0"]
    assert 0.0 <= r_dense_low <= 1.0, f"Dense recall out of range: {r_dense_low}"
    assert r_dense_low > 0.0, f"Dense recall is 0.0 at sigma=4 (sentinel -- filter eliminated all)"

    # Test sparse raw codebook at high f
    rng2 = np.random.default_rng(1)
    cb_sparse = make_sparse_raw_codebook(M_s, N_s, f_s, rng2)
    results_sparse = compute_recall_grid(cb_sparse, [4.0], n_eval=30, rng=np.random.default_rng(11))
    r_sparse = results_sparse["sigma_4.0"]
    assert 0.0 <= r_sparse <= 1.0, f"Sparse recall out of range: {r_sparse}"

    # Test sparse amplified: signal energy should match dense within 5%
    rng3 = np.random.default_rng(2)
    cb_ampl = make_sparse_amplified_codebook(M_s, N_s, f_s, rng3)
    energy_ampl = float(np.mean(np.sum(cb_ampl ** 2, axis=1)))
    energy_dense = float(N_s)
    assert abs(energy_ampl - energy_dense) / energy_dense < 0.05, (
        f"Amplified codebook energy mismatch: {energy_ampl:.2f} vs {energy_dense:.2f}"
    )

    # Test Pearson r computation on synthetic monotone data (should be ~1.0)
    x = np.array([0.1, 0.2, 0.3, 0.4, 0.5], dtype=float)
    y = 0.8 * x + 0.1 + np.random.default_rng(99).normal(0, 0.01, 5)
    r_val, _ = pearsonr(x, y)
    assert r_val > 0.95, f"Pearson r on synthetic monotone data is {r_val:.3f} (should be >0.95)"

    # Monotone endpoint check: dense recall at sigma=4 should exceed sigma=64
    assert results_dense["sigma_4.0"] >= results_dense["sigma_64.0"], (
        f"Dense recall not monotone: sigma4={results_dense['sigma_4.0']:.3f} "
        f"< sigma64={results_dense['sigma_64.0']:.3f}"
    )

    print("[selftest] PASS: dense_recall non-null, sparse_recall in-range, "
          "amplified energy restored, Pearson r computable, monotone endpoint check OK.",
          flush=True)


_instrumentation_selftest()


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------

def run_one_seed(seed: int, n_dim: int, m: int, n_eval: int,
                 f_grid: List[float], sigma_grid: List[float]) -> Dict[str, Any]:
    """Run one seed: sweep (f, sigma) grid for all three arms.

    W is hoisted per (arm, f) -- not recomputed per sigma.
    All sigma evaluations for a given codebook are batched.

    Returns dict with per-arm per-f per-sigma recall values,
    plus Pearson r across grid for sparse_raw arm.
    """
    t0 = time.time()

    # Dense codebook: one per seed, reused across all f values
    cb_dense = make_dense_bipolar_codebook(m, n_dim, np.random.default_rng(seed))

    # Dense recall grid: same codebook for all f (f-axis meaningless for dense arm;
    # report under f=1.0 key for consistency; record actual sigma curve once)
    rng_dense_eval = np.random.default_rng(seed * 100000 + 99999)
    dense_sigma_results = compute_recall_grid(cb_dense, sigma_grid, n_eval, rng_dense_eval)

    # Collect (snr_pred, recall) pairs for Pearson r computation
    snr_pred_raw: List[float] = []
    recall_raw: List[float] = []
    snr_pred_ampl: List[float] = []
    recall_ampl: List[float] = []

    arms: Dict[str, Any] = {
        "ARM_DENSE_BASELINE": {},
        "ARM_SPARSE_RAW": {},
        "ARM_SPARSE_AMPLIFIED": {},
    }

    for f in f_grid:
        f_key = f"f_{f}"
        # Dense baseline: same result regardless of f; fill with the pre-computed sigma curve
        arms["ARM_DENSE_BASELINE"][f_key] = dict(dense_sigma_results)

        cb_sparse_raw  = make_sparse_raw_codebook(m, n_dim, f, np.random.default_rng(seed * 1000 + int(f * 10000)))
        cb_sparse_ampl = make_sparse_amplified_codebook(m, n_dim, f, np.random.default_rng(seed * 2000 + int(f * 10000)))

        rng_raw  = np.random.default_rng(seed * 200000 + int(f * 10000))
        rng_ampl = np.random.default_rng(seed * 300000 + int(f * 10000))

        raw_results  = compute_recall_grid(cb_sparse_raw, sigma_grid, n_eval, rng_raw)
        ampl_results = compute_recall_grid(cb_sparse_ampl, sigma_grid, n_eval, rng_ampl)

        arms["ARM_SPARSE_RAW"][f_key]      = raw_results
        arms["ARM_SPARSE_AMPLIFIED"][f_key] = ampl_results

        for sigma in sigma_grid:
            snr_predicted = math.sqrt(f * n_dim) / sigma  # matched-filter prediction
            sig_key = f"sigma_{sigma}"
            recall_r = raw_results[sig_key]
            recall_a = ampl_results[sig_key]

            snr_pred_raw.append(snr_predicted)
            recall_raw.append(recall_r)
            snr_pred_ampl.append(snr_predicted)
            recall_ampl.append(recall_a)

            print(f"  seed={seed} f={f:.3f} sigma={sigma:.0f} "
                  f"snr_pred={snr_predicted:.3f} "
                  f"recall_raw={recall_r:.3f} recall_ampl={recall_a:.3f}",
                  flush=True)

    # Pearson r: recall vs snr_predicted
    if len(set(snr_pred_raw)) > 1 and len(set(recall_raw)) > 1:
        r_raw, p_raw = pearsonr(snr_pred_raw, recall_raw)
    else:
        r_raw, p_raw = float("nan"), float("nan")

    if len(set(snr_pred_ampl)) > 1 and len(set(recall_ampl)) > 1:
        r_ampl, p_ampl = pearsonr(snr_pred_ampl, recall_ampl)
    else:
        r_ampl, p_ampl = float("nan"), float("nan")

    elapsed = time.time() - t0
    print(f"[seed={seed}] Pearson r (sparse_raw vs SNR): {r_raw:.4f}  "
          f"r (sparse_ampl vs SNR): {r_ampl:.4f}  elapsed={elapsed:.1f}s",
          flush=True)

    return {
        "seed": seed,
        "N": n_dim,
        "M": m,
        "run_mode": RUN_MODE,
        "per_arm": arms,
        "pearson_r_sparse_raw": float(r_raw),
        "pearson_r_sparse_ampl": float(r_ampl),
        "pearson_p_sparse_raw": float(p_raw),
        "pearson_p_sparse_ampl": float(p_ampl),
        "snr_pred_vec": snr_pred_raw,
        "recall_raw_vec": recall_raw,
        "elapsed_s": elapsed,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    t_global = time.time()
    print(f"[{ANCHOR_NAME}] run_mode={RUN_MODE} N={N_DIM} M={M} "
          f"n_eval={N_EVAL} seeds={SEEDS} "
          f"f_grid={F_GRID} sigma_grid={SIGMA_GRID}",
          flush=True)

    out_dir = get_output_dir(anchor_name=ANCHOR_NAME)
    run_config = {"N": N_DIM, "M": M, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} of {len(SEEDS)} seeds done; running {remaining}",
          flush=True)

    for seed in remaining:
        result = run_one_seed(seed, N_DIM, M, N_EVAL, F_GRID, SIGMA_GRID)
        write_partial_key(out_dir, seed, result)

    per_seed = aggregate_partials(out_dir, SEEDS)

    # -------------------------------------------------------------------
    # Aggregate across seeds
    # -------------------------------------------------------------------
    # Collect all (snr_pred, recall) pairs across all seeds for Pearson r
    all_snr_pred: List[float] = []
    all_recall_raw: List[float] = []
    all_recall_ampl: List[float] = []

    for sd in SEEDS:
        sd_data = per_seed[str(sd)]
        all_snr_pred.extend(sd_data["snr_pred_vec"])
        all_recall_raw.extend(sd_data["recall_raw_vec"])
        # rebuild amplified from per_arm
        for f in F_GRID:
            f_key = f"f_{f}"
            for sigma in SIGMA_GRID:
                sig_key = f"sigma_{sigma}"
                all_recall_ampl.append(
                    sd_data["per_arm"]["ARM_SPARSE_AMPLIFIED"][f_key][sig_key]
                )

    if len(set(all_snr_pred)) > 1 and len(set(all_recall_raw)) > 1:
        pearson_r_raw, pearson_p_raw = pearsonr(all_snr_pred, all_recall_raw)
    else:
        pearson_r_raw, pearson_p_raw = float("nan"), float("nan")

    if len(set(all_snr_pred)) > 1 and len(set(all_recall_ampl)) > 1:
        pearson_r_ampl, pearson_p_ampl = pearsonr(all_snr_pred, all_recall_ampl)
    else:
        pearson_r_ampl, pearson_p_ampl = float("nan"), float("nan")

    # CV across seeds for Pearson r
    r_vals_per_seed = [per_seed[str(s)]["pearson_r_sparse_raw"] for s in SEEDS]
    r_vals_arr = np.array(r_vals_per_seed)
    cv_r = (float(np.std(r_vals_arr)) / float(np.mean(r_vals_arr))
            if float(np.mean(r_vals_arr)) != 0 else float("nan"))

    # Extract spot-checks from per_arm mean across seeds
    def mean_recall_at(arm: str, f_val: float, sigma_val: float) -> float:
        vals = []
        f_key = f"f_{f_val}"
        sig_key = f"sigma_{sigma_val}"
        for sd in SEEDS:
            try:
                vals.append(per_seed[str(sd)]["per_arm"][arm][f_key][sig_key])
            except KeyError:
                pass
        return float(np.mean(vals)) if vals else float("nan")

    # Criterion B: ARM_SPARSE_RAW @ f=0.02, sigma=16 should be in [0.45, 0.75]
    criterion_b_val = mean_recall_at("ARM_SPARSE_RAW", 0.02, 16.0)
    criterion_b = (not math.isnan(criterion_b_val)) and (0.45 <= criterion_b_val <= 0.75)

    # Criterion C: ARM_SPARSE_RAW @ f=0.50, sigma=16 >= 0.95
    criterion_c_val = mean_recall_at("ARM_SPARSE_RAW", 0.5, 16.0)
    criterion_c = (not math.isnan(criterion_c_val)) and (criterion_c_val >= 0.95)

    # Criterion D: ARM_SPARSE_AMPLIFIED @ f=0.02, sigma=16 >= 0.95
    criterion_d_val = mean_recall_at("ARM_SPARSE_AMPLIFIED", 0.02, 16.0)
    criterion_d = (not math.isnan(criterion_d_val)) and (criterion_d_val >= 0.95)

    # -------------------------------------------------------------------
    # Verdict
    # -------------------------------------------------------------------
    cv_pass = (not math.isnan(cv_r)) and (cv_r < 0.05)
    r = pearson_r_raw if not math.isnan(pearson_r_raw) else -1.0

    if r >= 0.85:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: Pearson r(recall,sqrt(f*N)/sigma)={r:.4f} >= 0.85 -- "
            f"matched-filter-energy IS primary mechanism. "
            f"B(f=0.02@sig16)={criterion_b_val:.3f}(pass={criterion_b}) "
            f"C(f=0.5@sig16)={criterion_c_val:.3f}(pass={criterion_c}) "
            f"D(ampl@f=0.02@sig16)={criterion_d_val:.3f}(pass={criterion_d}) "
            f"cv_r={cv_r:.4f}(pass={cv_pass})"
        )
    elif r >= 0.50:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: Pearson r={r:.4f} in [0.50, 0.85) -- "
            f"matched-filter-energy partial explanation. Another mechanism contributes. "
            f"B={criterion_b_val:.3f} C={criterion_c_val:.3f} D={criterion_d_val:.3f} "
            f"cv_r={cv_r:.4f}"
        )
    else:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: Pearson r={r:.4f} < 0.50 -- "
            f"matched-filter-energy NOT primary mechanism. Refer back to Research. "
            f"B={criterion_b_val:.3f} C={criterion_c_val:.3f} D={criterion_d_val:.3f} "
            f"cv_r={cv_r:.4f}"
        )

    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

    # Build summary arm data (mean across seeds)
    summary_arms: Dict[str, Any] = {
        "ARM_DENSE_BASELINE": {},
        "ARM_SPARSE_RAW": {},
        "ARM_SPARSE_AMPLIFIED": {},
    }
    for arm in summary_arms:
        for f_val in F_GRID:
            f_key = f"f_{f_val}"
            summary_arms[arm][f_key] = {}
            for sigma_val in SIGMA_GRID:
                sig_key = f"sigma_{sigma_val}"
                summary_arms[arm][f_key][sig_key] = mean_recall_at(arm, f_val, sigma_val)

    elapsed_total = time.time() - t_global

    metrics: Dict[str, Any] = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "seeds": SEEDS,
        "config": {
            "N_DIM": N_DIM,
            "M": M,
            "N_EVAL": N_EVAL,
            "F_GRID": F_GRID,
            "SIGMA_GRID": SIGMA_GRID,
        },
        "pearson_r_sparse_raw": float(pearson_r_raw),
        "pearson_p_sparse_raw": float(pearson_p_raw),
        "pearson_r_sparse_ampl": float(pearson_r_ampl),
        "pearson_p_sparse_ampl": float(pearson_p_ampl),
        "cv_pearson_r_across_seeds": float(cv_r),
        "cv_pass": cv_pass,
        "criterion_b_val": float(criterion_b_val),
        "criterion_b_pass": bool(criterion_b),
        "criterion_c_val": float(criterion_c_val),
        "criterion_c_pass": bool(criterion_c),
        "criterion_d_val": float(criterion_d_val),
        "criterion_d_pass": bool(criterion_d),
        "summary": summary_arms,
        "per_seed": per_seed,
        "elapsed_s": elapsed_total,
    }

    write_metrics(out_dir, metrics)
    print(f"[{ANCHOR_NAME}] done. elapsed={elapsed_total:.1f}s "
          f"metrics written to {out_dir}", flush=True)


if __name__ == "__main__":
    main()
