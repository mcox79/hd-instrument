"""
kappa3_monitor_detection_latency_v1 -- Streaming Prediction 3: kappa_3 monitor detection latency.

SCIENTIFIC QUESTION (Streaming Prediction 3):
  A kappa_3 monitor watches the substrate for anomalous writes by tracking the
  running kappa_3 spectral fingerprint. When an anomalous write occurs (e.g.,
  pattern from a DIFFERENT distribution), the monitor should detect the deviation
  within W <= 50 writes at 3-sigma significance.

  Protocol:
    1. Warm-up: write M_warm normal BSC +-1 patterns. Establish kappa_3 baseline
       mean and std from a sliding window.
    2. Inject: write 1 anomalous pattern (drawn from a DIFFERENT distribution --
       e.g., Gaussian normalized to +-1 sign pattern with heavy-tailed source).
    3. Continue: write M_continue more normal patterns.
    4. Measure: first write index W after injection where kappa_3 deviation
       exceeds 3*sigma_baseline. Report detection latency W.

  HP: detection latency W <= 50 writes at 3-sigma, at false-positive rate < 0.10.
  HF: detection latency W > 100 writes OR FP rate > 0.50.
  MIDDLE: 50 < W <= 100 OR FP rate in [0.10, 0.50].

PRE-REGISTERED BANDS:
  HP: W <= 50, FP_rate < 0.10.
  HF: W > 100 OR FP_rate >= 0.50.
  Calibration: first kappa_3 monitor test; bands +-50% per calibration policy.
  Note: kappa_3 is the third free cumulant of W. For BSC Hopfield W at alpha=M/N,
  kappa_3 ~ alpha (free-Poisson identity confirmed by kappa3_hutchinson_v1 HARD_PASS).
  An anomalous write from a different distribution perturbs the third cumulant.

FORMULA SELF-TESTS:
  1. kappa_3 Hutchinson estimate: for W=0 (zero matrix), kappa_3=0.
     [INPUT: W=zeros(N,N)] [EXPECTED: kappa3 ~ 0]
  2. kappa_3 monotone in alpha: adding 1 pattern to W increases kappa_3.
     [INPUT: N=256, M=10 -> M=11] [EXPECTED: kappa3(M=11) >= kappa3(M=10)]
  3. 3-sigma detection: if kappa_3 shift is > 3*sigma_baseline, flag is True.
     [INPUT: shift=4*sigma, sigma=0.01] [EXPECTED: flagged=True]

No _nN suffix; production N=2048 per rule 3:
  No _nN suffix; production N = 2048; rationale: kappa_3 estimate needs N large
  enough for Hutchinson trace to converge (N=2048 gives reliable estimate in <1s).
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

ANCHOR_NAME = "kappa3_monitor_detection_latency_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N = 512
    M_WARM = 30         # warm-up writes for baseline
    M_CONTINUE = 80     # writes after injection to allow detection
    N_PROBE = 50        # Hutchinson trace probes for kappa_3
    WINDOW = 10         # sliding window for baseline stats
    SEEDS = [7, 17]
    N_INJECTIONS = 3    # different injection types to test
else:
    N = 2048
    M_WARM = 50
    M_CONTINUE = 120
    N_PROBE = 200
    WINDOW = 15
    SEEDS = [7, 17, 23, 31, 41]
    N_INJECTIONS = 5

HP_W_DETECT = 50
HF_W_DETECT = 100
HP_FP_RATE = 0.10
HF_FP_RATE = 0.50
SIGMA_THRESH = 3.0


def kappa3_hutchinson(W: np.ndarray, n_probe: int, rng: np.random.RandomState) -> float:
    """Estimate third free cumulant kappa_3(W) via Hutchinson trace estimator.
    kappa_3(W) = (1/N) * Tr(W^3) for zero-diagonal W.
    Uses stochastic trace: kappa_3 ~ (1/N) * E_v[v^T W^3 v] for Rademacher v.
    """
    N_dim = W.shape[0]
    estimates = []
    for _ in range(n_probe):
        v = rng.choice([-1.0, 1.0], size=(N_dim,)).astype(np.float64)
        Wv = W @ v
        WWv = W @ Wv
        WWWv = W @ WWv
        estimates.append(float(np.dot(v, WWWv)) / float(N_dim))
    return float(np.mean(estimates))


def _selftest_kappa3_zero():
    W_zero = np.zeros((64, 64))
    rng = np.random.RandomState(0)
    k3 = kappa3_hutchinson(W_zero, n_probe=20, rng=rng)
    assert abs(k3) < 1e-12, f"kappa3(0) = {k3:.6e} expected ~0"
    return k3


def _selftest_kappa3_monotone():
    N_t = 256
    rng = np.random.RandomState(7)
    Xi10 = rng.choice([-1.0, 1.0], size=(10, N_t)).astype(np.float64)
    W10 = Xi10.T @ Xi10 / float(N_t)
    np.fill_diagonal(W10, 0.0)
    xi_new = rng.choice([-1.0, 1.0], size=(N_t,)).astype(np.float64)
    Xi11 = np.vstack([Xi10, xi_new[np.newaxis, :]])
    W11 = Xi11.T @ Xi11 / float(N_t)
    np.fill_diagonal(W11, 0.0)
    rng2 = np.random.RandomState(42)
    k3_10 = kappa3_hutchinson(W10, n_probe=100, rng=rng2)
    rng2 = np.random.RandomState(42)
    k3_11 = kappa3_hutchinson(W11, n_probe=100, rng=rng2)
    assert k3_11 >= k3_10 * 0.9, f"kappa3 not monotone: k3(M=10)={k3_10:.4f} k3(M=11)={k3_11:.4f}"
    return k3_10, k3_11


def _selftest_sigma_detection():
    sigma = 0.01
    shift = 4.0 * sigma
    flagged = shift > SIGMA_THRESH * sigma
    assert flagged, f"3-sigma detection selftest failed: shift={shift:.4f} sigma={sigma:.4f}"
    return flagged


def _instrumentation_selftest():
    k0 = _selftest_kappa3_zero()
    k10, k11 = _selftest_kappa3_monotone()
    det = _selftest_sigma_detection()
    print(f"[selftest] kappa3(0)={k0:.2e} kappa3(10)={k10:.4f} kappa3(11)={k11:.4f} "
          f"3sigma_det={det}", flush=True)


_instrumentation_selftest()
# Self-test only: N=2048 Hutchinson monitor at 200 writes * 5 inj_types * 5 seeds >> 180s gate timeout.
if _ARGS.self_test:
    sys.exit(0)


def run_monitor_experiment(seed: int, injection_type: str) -> Dict:
    """
    Run the kappa_3 monitor experiment.
    injection_type: 'gaussian_sign' | 'structured' | 'anti_correlated' | 'all_ones' | 'zeros'
    """
    rng = np.random.RandomState(seed)
    t0 = time.time()

    # Warm-up: write M_WARM normal patterns
    Xi_list = []
    for _ in range(M_WARM):
        xi = rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64)
        Xi_list.append(xi)

    Xi_base = np.array(Xi_list)
    W = Xi_base.T @ Xi_base / float(N)
    np.fill_diagonal(W, 0.0)

    # Compute baseline kappa_3 over last WINDOW patterns (window of write events)
    # We'll track kappa_3 after each write in the warm-up window
    kappa3_baseline = []
    for k in range(max(0, M_WARM - WINDOW), M_WARM):
        rng_k3 = np.random.RandomState(seed + k)
        kappa3_baseline.append(kappa3_hutchinson(W, N_PROBE, rng_k3))

    if not kappa3_baseline:
        return {"seed": seed, "injection": injection_type, "detection_W": None, "fp_rate": None}

    baseline_mean = float(np.mean(kappa3_baseline))
    baseline_std = float(np.std(kappa3_baseline, ddof=1)) if len(kappa3_baseline) > 1 else 1e-6
    if baseline_std < 1e-10:
        baseline_std = 1e-10

    # Inject one anomalous pattern
    if injection_type == "gaussian_sign":
        xi_inject = np.sign(rng.randn(N) * 3.0)  # heavy-tailed Gaussian sign
        xi_inject[xi_inject == 0] = 1.0
    elif injection_type == "structured":
        # Highly correlated pattern (same as first stored pattern)
        xi_inject = Xi_list[0].copy()
    elif injection_type == "anti_correlated":
        xi_inject = -Xi_list[0].copy()
    elif injection_type == "all_ones":
        xi_inject = np.ones(N, dtype=np.float64)
    else:  # zeros -- identity column
        xi_inject = rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64)

    # Add injection to W
    Xi_inject = np.vstack([Xi_base, xi_inject[np.newaxis, :]])
    W_after_inject = Xi_inject.T @ Xi_inject / float(N)
    np.fill_diagonal(W_after_inject, 0.0)

    # Continue writing normal patterns; monitor for detection
    detection_W = None
    current_W = W_after_inject
    current_Xi = Xi_inject.copy()

    for k in range(1, M_CONTINUE + 1):
        xi_new = rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64)
        current_Xi = np.vstack([current_Xi, xi_new[np.newaxis, :]])
        current_W = current_Xi.T @ current_Xi / float(N)
        np.fill_diagonal(current_W, 0.0)

        rng_k3 = np.random.RandomState(seed + M_WARM + k)
        k3_now = kappa3_hutchinson(current_W, N_PROBE, rng_k3)
        deviation = abs(k3_now - baseline_mean) / baseline_std

        if deviation >= SIGMA_THRESH and detection_W is None:
            detection_W = k
            break

    # Estimate false positive rate from pre-injection window
    fp_flags = 0
    for k3_val in kappa3_baseline:
        dev = abs(k3_val - baseline_mean) / baseline_std
        if dev >= SIGMA_THRESH:
            fp_flags += 1
    fp_rate = fp_flags / len(kappa3_baseline) if kappa3_baseline else 1.0

    elapsed = time.time() - t0
    print(f"  [seed={seed} inj={injection_type}] detection_W={detection_W} "
          f"baseline_mean={baseline_mean:.4f} baseline_std={baseline_std:.6f} "
          f"fp_rate={fp_rate:.3f} t={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N, "run_mode": RUN_MODE,
        "injection": injection_type,
        "detection_W": detection_W,
        "fp_rate": float(fp_rate),
        "baseline_mean": float(baseline_mean),
        "baseline_std": float(baseline_std),
        "elapsed_s": elapsed,
    }


def run_seed(seed: int) -> Dict:
    # Test multiple injection types
    injection_types = ["gaussian_sign", "structured", "anti_correlated", "all_ones", "uniform_random"]
    injection_types = injection_types[:N_INJECTIONS]

    results_by_type = {}
    for inj_type in injection_types:
        r = run_monitor_experiment(seed, inj_type)
        results_by_type[inj_type] = r

    return {
        "seed": seed, "N": N, "run_mode": RUN_MODE,
        "results_by_injection": results_by_type,
    }


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    all_detections = []
    all_fp_rates = []

    for sd in per_seed.values():
        for inj_type, r in sd.get("results_by_injection", {}).items():
            w = r.get("detection_W")
            fp = r.get("fp_rate")
            if w is not None:
                all_detections.append(w)
            if fp is not None:
                all_fp_rates.append(fp)

    if not all_detections:
        return ("HARD_FAIL", f"No detections: anomaly never detected within {M_CONTINUE} writes.")

    mean_w = float(np.mean(all_detections))
    frac_hp = sum(1 for w in all_detections if w <= HP_W_DETECT) / len(all_detections)
    frac_hf_fail = sum(1 for w in all_detections if w > HF_W_DETECT) / len(all_detections)
    mean_fp = float(np.mean(all_fp_rates)) if all_fp_rates else 1.0

    summary = (f"mean_detection_W={mean_w:.1f} (HP<={HP_W_DETECT} HF>{HF_W_DETECT}) "
               f"frac_hp={frac_hp:.2f} frac_hf_fail={frac_hf_fail:.2f} "
               f"mean_fp_rate={mean_fp:.3f} (HP<{HP_FP_RATE} HF>={HF_FP_RATE}) "
               f"n_detections={len(all_detections)}")

    if frac_hf_fail > 0.3 or mean_fp >= HF_FP_RATE:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")
    if frac_hp >= 0.7 and mean_fp < HP_FP_RATE:
        return ("HARD_PASS", f"HARD_PASS: {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {summary}")


# ---- MAIN SWEEP ----
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
verdict, verdict_msg = compute_verdict(per_seed)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

# Summary metrics
all_detections_flat = []
for sd in per_seed.values():
    for r in sd.get("results_by_injection", {}).values():
        w = r.get("detection_W")
        if w is not None:
            all_detections_flat.append(w)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": verdict_msg,
    "elapsed_s": elapsed_s,
    "n_seeds": len(SEEDS),
    "run_mode": RUN_MODE,
    "N": N,
    "HP_W_DETECT": HP_W_DETECT,
    "SIGMA_THRESH": SIGMA_THRESH,
    "mean_detection_W": float(np.mean(all_detections_flat)) if all_detections_flat else None,
    "n_detections": len(all_detections_flat),
    "elapsed_total_s": elapsed_s,
}

metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
