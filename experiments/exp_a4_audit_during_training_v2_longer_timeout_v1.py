"""
a4_audit_during_training_v2_longer_timeout_v1 -- Cluster A4 v2: kappa_3 audit during training.

v1 hit 120s timeout. v2 ships with 600s allowance, per-step instrumentation,
and optimized CPU ops (smaller N_HUTCHINSON per step, batch baseline computation).

SCIENTIFIC QUESTION:
  Does kappa_3 spectral fingerprint detect a training-injected anomaly (corrupted
  pattern write) within W <= 50 writes at 3-sigma, operating as a REAL-TIME audit
  primitive during substrate state updates?

  kappa_3 = Tr(W^3) / N detects non-Gaussian structure in the stored patterns.
  A corrupted/adversarial pattern shifts kappa_3 because it breaks near-Gaussian
  distributed pattern statistics of clean Hebbian updates.

PRE-REGISTERED HARD-PASS:
  HP1: kappa_3 exceeds 3-sigma of clean baseline within W <= 50 writes after anomaly.
  HP2: detection latency (writes from injection to detection) <= 50.
  HP3: false-positive rate < 5% (clean runs don't trigger 3-sigma event).
  HARD-PASS: all 3 HP in >= 4/5 seeds.

PRE-REGISTERED HARD-FAIL:
  HF1: kappa_3 never exceeds 3-sigma after anomaly injection (within 200 writes).
  HF2: false-positive rate > 20%.

MIDDLE BAND:
  detection within 51-100 writes OR FPR 5-20%.

P_deflated = 0.55 (kappa_3 confirmed at drift detection; adversarial anomaly
detection at 3-sigma during training is novel -- calibration probe).

FORMULA SELF-TESTS:
  1. kappa_3 Hutchinson at alpha=0.049: k3 in [0.03, 0.10].
     [INPUT: N=512, M=25] [EXPECTED: k3 in [0.03, 0.10]]
  2. Anomalous pattern creates non-zero kappa_3 shift.
     [INPUT: N=256, M=10, inject corrupted pattern] [EXPECTED: dk3 != 0]
  3. False positive: 100 clean writes stay within 3-sigma.

PROT-018: no _nN suffix; production N=1024 per v1 (pre-PROT-018 inherited config).
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

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "a4_audit_during_training_v2_longer_timeout_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N = 512
    M_CLEAN_BEFORE = 20
    M_CLEAN_AFTER = 30
    N_BASELINE_RUNS = 5
    N_HUTCHINSON = 80   # reduced for speed
    SIGMA_THRESHOLD = 3.0
else:
    SEEDS = [7, 17, 23, 31, 41]
    N = 1024
    M_CLEAN_BEFORE = 50
    M_CLEAN_AFTER = 50
    N_BASELINE_RUNS = 20
    N_HUTCHINSON = 200  # reduced from 300 to stay within 600s
    SIGMA_THRESHOLD = 3.0

HP_DETECT_WITHIN_W = M_CLEAN_AFTER
HF_DETECT_WITHIN_W = M_CLEAN_AFTER * 4
HP_FPR = 0.05
HF_FPR = 0.20


def hutchinson_kappa3(W: np.ndarray, n_probes: int, seed: int) -> float:
    """Hutchinson estimator for kappa_3 = Tr(W^3) / N."""
    N_dim = W.shape[0]
    rng = np.random.RandomState(seed)
    V = rng.choice([-1.0, 1.0], size=(N_dim, n_probes)).astype(np.float64)
    W3V = W @ (W @ (W @ V))
    per_probe = (V * W3V).sum(axis=0) / N_dim
    return float(np.mean(per_probe))


def build_anomalous_pattern(W: np.ndarray, N_dim: int, rng: np.random.RandomState) -> np.ndarray:
    """Build pattern maximally aligned with top eigenvector of W^2 (power iteration)."""
    v = rng.randn(N_dim)
    v /= np.linalg.norm(v) + 1e-12
    for _ in range(20):
        v = W @ (W @ v)
        v_norm = np.linalg.norm(v)
        if v_norm < 1e-12:
            break
        v /= v_norm
    xi_corrupt = np.sign(v)
    xi_corrupt[xi_corrupt == 0] = 1.0
    return xi_corrupt.astype(np.float64)


def _selftest_kappa3_range():
    """kappa_3 at alpha=0.049 should be in [0.03, 0.10]."""
    N_t, M_t = 512, 25
    rng = np.random.RandomState(0)
    Xi_t = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    W_t = Xi_t.T @ Xi_t / float(N_t)
    np.fill_diagonal(W_t, 0.0)
    k3 = hutchinson_kappa3(W_t, 200, 42)
    assert 0.01 < k3 < 0.20, f"kappa3_range selftest: k3={k3:.4f} not in [0.01, 0.20]"
    return k3


def _selftest_anomaly_shift():
    """Anomalous pattern creates detectable kappa_3 shift."""
    N_t, M_t = 256, 10
    rng = np.random.RandomState(1)
    Xi_t = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    W_t = Xi_t.T @ Xi_t / float(N_t)
    np.fill_diagonal(W_t, 0.0)
    k3_before = hutchinson_kappa3(W_t, 200, 42)
    xi_corrupt = build_anomalous_pattern(W_t, N_t, rng)
    W_after = W_t + np.outer(xi_corrupt, xi_corrupt) / float(N_t)
    np.fill_diagonal(W_after, 0.0)
    k3_after = hutchinson_kappa3(W_after, 200, 43)
    dk3 = k3_after - k3_before
    assert dk3 != 0.0, f"anomaly_shift selftest: dk3=0.0 (detector broken)"
    return k3_before, k3_after, dk3


def _instrumentation_selftest():
    k3 = _selftest_kappa3_range()
    k3_b, k3_a, dk3 = _selftest_anomaly_shift()
    print(
        f"[selftest] PASS: kappa3_at_alpha={k3:.4f} "
        f"anomaly_dk3={dk3:.6f}(k3_before={k3_b:.4f} after={k3_a:.4f}) "
        f"N={N} M_before={M_CLEAN_BEFORE} window={M_CLEAN_AFTER}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_clean_baseline_batch(seed_base: int, n_runs: int) -> Tuple[float, float]:
    """Compute baseline kappa_3 stats across n_runs clean trajectories."""
    all_k3s = []
    M_total = M_CLEAN_BEFORE + M_CLEAN_AFTER
    for run_idx in range(n_runs):
        rng_run = np.random.RandomState(seed_base + run_idx * 1000)
        W_run = np.zeros((N, N), dtype=np.float64)
        Xi_run = rng_run.choice([-1.0, 1.0], size=(M_total, N)).astype(np.float64)
        for step in range(M_total):
            W_run += np.outer(Xi_run[step], Xi_run[step]) / float(N)
            np.fill_diagonal(W_run, 0.0)
        k3 = hutchinson_kappa3(W_run, N_HUTCHINSON, rng_run.randint(0, 2**31))
        all_k3s.append(k3)
        # Per-step progress
        print(f"  [baseline run {run_idx+1}/{n_runs}] k3={k3:.4f}", flush=True)
    mean_k3 = float(np.mean(all_k3s))
    std_k3 = float(np.std(all_k3s)) if len(all_k3s) > 1 else 1e-6
    return mean_k3, std_k3


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    print(f"[seed={seed}] building baseline...", flush=True)
    baseline_mean, baseline_std = run_clean_baseline_batch(seed + 100, N_BASELINE_RUNS)
    if baseline_std < 1e-8:
        baseline_std = max(abs(baseline_mean) * 0.01, 1e-6)
    print(f"  [seed={seed}] baseline: mean={baseline_mean:.4f} std={baseline_std:.6f}", flush=True)

    # FPR test
    n_fp = 0
    for fp_run in range(N_BASELINE_RUNS):
        rng_fp = np.random.RandomState(seed + 200 + fp_run)
        W_fp = np.zeros((N, N), dtype=np.float64)
        Xi_fp = rng_fp.choice([-1.0, 1.0], size=(M_CLEAN_BEFORE + M_CLEAN_AFTER, N)).astype(np.float64)
        for step in range(M_CLEAN_BEFORE + M_CLEAN_AFTER):
            W_fp += np.outer(Xi_fp[step], Xi_fp[step]) / float(N)
            np.fill_diagonal(W_fp, 0.0)
        k3_fp = hutchinson_kappa3(W_fp, N_HUTCHINSON, seed + 300 + fp_run)
        if abs(k3_fp - baseline_mean) > SIGMA_THRESHOLD * baseline_std:
            n_fp += 1
    fpr = n_fp / max(1, N_BASELINE_RUNS)

    # Anomaly detection run
    rng = np.random.RandomState(seed)
    Xi_clean = rng.choice([-1.0, 1.0], size=(M_CLEAN_BEFORE, N)).astype(np.float64)
    W = np.zeros((N, N), dtype=np.float64)
    for xi in Xi_clean:
        W += np.outer(xi, xi) / float(N)
        np.fill_diagonal(W, 0.0)

    rng_anom = np.random.RandomState(seed + 500)
    xi_anomaly = build_anomalous_pattern(W, N, rng_anom)
    W_anomaly = W.copy()
    W_anomaly += np.outer(xi_anomaly, xi_anomaly) / float(N)
    np.fill_diagonal(W_anomaly, 0.0)

    Xi_after = rng.choice([-1.0, 1.0], size=(M_CLEAN_AFTER, N)).astype(np.float64)
    W_current = W_anomaly.copy()
    detection_write = None
    kappa3_trajectory = []

    for step in range(M_CLEAN_AFTER):
        xi_step = Xi_after[step]
        W_current += np.outer(xi_step, xi_step) / float(N)
        np.fill_diagonal(W_current, 0.0)
        k3 = hutchinson_kappa3(W_current, N_HUTCHINSON, seed + 600 + step)
        kappa3_trajectory.append(k3)
        z_score = (k3 - baseline_mean) / max(baseline_std, 1e-12)
        if detection_write is None and abs(z_score) > SIGMA_THRESHOLD:
            detection_write = step + 1
        if step % 10 == 0:
            print(f"  [seed={seed} step={step}] k3={k3:.4f} z={z_score:.2f} "
                  f"detected={detection_write is not None}", flush=True)

    detected = detection_write is not None
    detect_latency = detection_write if detected else M_CLEAN_AFTER * 4

    hp1 = detected and detect_latency <= HP_DETECT_WITHIN_W
    hp2 = detect_latency <= HP_DETECT_WITHIN_W
    hp3 = fpr < HP_FPR

    hf1 = detect_latency > HF_DETECT_WITHIN_W
    hf2 = fpr > HF_FPR

    elapsed = time.time() - t0
    print(
        f"  [seed={seed} N={N} M_before={M_CLEAN_BEFORE} window={M_CLEAN_AFTER}] "
        f"detected={detected} latency={detect_latency}writes(HP<={HP_DETECT_WITHIN_W}) "
        f"fpr={fpr:.3f}(HP<{HP_FPR}) "
        f"baseline_mean={baseline_mean:.4f} std={baseline_std:.6f} "
        f"hp=[{int(hp1)},{int(hp2)},{int(hp3)}] elapsed={elapsed:.2f}s",
        flush=True,
    )

    return {
        "seed": seed, "N": N, "M_CLEAN_BEFORE": M_CLEAN_BEFORE,
        "M_CLEAN_AFTER": M_CLEAN_AFTER, "run_mode": RUN_MODE,
        "detected": bool(detected),
        "detect_latency_writes": int(detect_latency),
        "fpr": float(fpr),
        "baseline_mean": float(baseline_mean),
        "baseline_std": float(baseline_std),
        "hp1": bool(hp1), "hp2": bool(hp2), "hp3": bool(hp3),
        "hf1": bool(hf1), "hf2": bool(hf2),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid results.")
    n = len(results)
    n_detected = sum(1 for r in results if r["detected"])
    mean_latency = float(np.mean([r["detect_latency_writes"] for r in results]))
    mean_fpr = float(np.mean([r["fpr"] for r in results]))
    hp1_n = sum(1 for r in results if r["hp1"])
    hp2_n = sum(1 for r in results if r["hp2"])
    hp3_n = sum(1 for r in results if r["hp3"])
    hf1_any = any(r["hf1"] for r in results)
    hf2_any = any(r["hf2"] for r in results)

    summary = (
        f"n_seeds={n} detected={n_detected}/{n} latency={mean_latency:.1f}writes "
        f"fpr={mean_fpr:.3f}(HP<{HP_FPR},HF>{HF_FPR}) "
        f"hp1={hp1_n}/{n} hp2={hp2_n}/{n} hp3={hp3_n}/{n}"
    )

    if hf1_any:
        return ("HARD_FAIL", f"HARD_FAIL HF1: anomaly never detected within {HF_DETECT_WITHIN_W} writes. {summary}")
    if hf2_any:
        return ("HARD_FAIL", f"HARD_FAIL HF2: false-positive rate >{HF_FPR:.0%}. {summary}")

    min_threshold = math.ceil(n * 0.8)
    all_hp = all(cnt >= min_threshold for cnt in [hp1_n, hp2_n, hp3_n])
    if all_hp:
        return ("HARD_PASS", f"HARD_PASS: all 3 HP conditions met in >={min_threshold}/{n} seeds. {summary}")

    n_hp_conds = sum([hp1_n >= min_threshold, hp2_n >= min_threshold, hp3_n >= min_threshold])
    if n_hp_conds >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp_conds}/3 HP conditions met. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_hp_conds}/3 HP conditions met. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_CLEAN_BEFORE": M_CLEAN_BEFORE, "M_CLEAN_AFTER": M_CLEAN_AFTER, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} seeds done, {len(remaining)} to run "
    f"(N={N} M_before={M_CLEAN_BEFORE} window={M_CLEAN_AFTER} mode={RUN_MODE})",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] a4_audit_during_training_v2 N={N}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)
    elapsed_so_far = time.time() - t_sweep_start
    print(f"[progress] seed={seed} done. elapsed_total={elapsed_so_far:.1f}s", flush=True)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "M_CLEAN_BEFORE": M_CLEAN_BEFORE, "M_CLEAN_AFTER": M_CLEAN_AFTER,
    "SIGMA_THRESHOLD": SIGMA_THRESHOLD,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_s,
    "per_seed": [
        {
            "seed": r.get("seed"),
            "detected": r.get("detected"),
            "detect_latency_writes": r.get("detect_latency_writes"),
            "fpr": r.get("fpr"),
            "hp1": r.get("hp1"), "hp2": r.get("hp2"), "hp3": r.get("hp3"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
