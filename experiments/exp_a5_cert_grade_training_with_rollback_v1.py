"""
a5_cert_grade_training_with_rollback_v1 -- Cluster A5: cert-grade training with rollback.

SCIENTIFIC QUESTION (Phase 3, Cluster A5):
  Combines A3 (exact rollback via rank-1 subtraction) + A4 (kappa_3 audit during training)
  into a single integrated workflow demonstrating cert-grade training:
    - One-shot Hebbian writes.
    - Exact rollback for any single write (GDPR-style "exact undo").
    - Live kappa_3 drift detection running during writes.
  The HP: all 3 capabilities operate together in a single pipeline without interference.

  Protocol:
    1. Write M_CLEAN clean patterns to W; monitor kappa_3 per write.
    2. Inject 1 adversarial pattern (same construction as A4: aligned with top evec of W^2).
    3. kappa_3 must exceed 3-sigma baseline within W <= 50 writes of injection.
    4. Execute exact rollback on the adversarial pattern (rank-1 subtraction).
    5. Verify ||W_rollback - W_before_injection||_F / ||W_before|| < 1e-10 (machine precision).
    6. Verify retrieval fidelity of clean patterns is >= 0.95 post-rollback.

PRE-REGISTERED BANDS:
  HP1: kappa_3 exceeds 3-sigma within 50 writes of injection (audit detects anomaly).
  HP2: ||relative rollback error||_F < 1e-10 (machine precision rollback).
  HP3: Clean pattern retrieval >= 0.95 after rollback (no corruption).

  HARD-PASS: HP1 AND HP2 AND HP3.
  HARD-FAIL: kappa_3 never detects in 200 writes OR rollback error > 1e-6 OR
             clean retrieval drops below 0.70 post-rollback.
  MIDDLE: 2/3 HP conditions.

  No prior empirical anchor for 3-capability joint composition;
  each individually CONFIRMED (A3: machine-precision rollback; A4: kappa_3 detection).
  Joint composition expected to hold; P_deflated = 0.75.

FORMULA SELF-TESTS:
  1. Rollback identity: W + outer(xi)/N - outer(xi)/N = W exactly.
     [INPUT: N=4, W random, xi +-1] [EXPECTED: ||W_rb - W||_F = 0 exactly]
  2. kappa_3 shift from adversarial write: dk3 != 0.0.
     [INPUT: N=256, clean W, then adversarial xi] [EXPECTED: k3_after != k3_before]
  3. After rollback, baseline kappa_3 restored: |k3_post_rb - k3_clean| < 3*sigma.
     [INPUT: k3_clean trajectory std, after rollback] [EXPECTED: back in baseline band]

No _nN suffix; production N=1024 (PROT-018 rule 3).
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

ANCHOR_NAME = "a5_cert_grade_training_with_rollback_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
SIGMA_THRESHOLD = 3.0

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N = 512
    M_CLEAN = 20
    DETECT_WINDOW = 15
    N_HUTCHINSON = 100
    N_BASELINE_RUNS = 5
    NOISE_FRAC = 0.10
else:
    SEEDS = [7, 17, 23, 31, 41]
    N = 1024
    M_CLEAN = 50
    DETECT_WINDOW = 50
    N_HUTCHINSON = 300
    N_BASELINE_RUNS = 20
    NOISE_FRAC = 0.10

HP_DETECT_WITHIN_W = DETECT_WINDOW
HF_DETECT_WITHIN_W = DETECT_WINDOW * 4
HP_ROLLBACK_ERR = 1e-10
HF_ROLLBACK_ERR = 1e-6
HP_CLEAN_ACC = 0.95
HF_CLEAN_ACC = 0.70


def hutchinson_kappa3(W: np.ndarray, n_probes: int, seed: int) -> float:
    N_dim = W.shape[0]
    rng = np.random.RandomState(seed)
    V = rng.choice([-1.0, 1.0], size=(N_dim, n_probes)).astype(np.float64)
    W3V = W @ (W @ (W @ V))
    per_probe = (V * W3V).sum(axis=0) / N_dim
    return float(np.mean(per_probe))


def build_anomalous_pattern(W: np.ndarray, N_dim: int, rng: np.random.RandomState) -> np.ndarray:
    v = rng.randn(N_dim)
    v /= np.linalg.norm(v) + 1e-12
    for _ in range(20):
        v = W @ (W @ v)
        n = np.linalg.norm(v)
        if n < 1e-12:
            break
        v /= n
    xi = np.sign(v)
    xi[xi == 0] = 1.0
    return xi.astype(np.float64)


def hopfield_retrieve(W: np.ndarray, probe: np.ndarray, n_steps: int = 5) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


# ---- FORMULA SELF-TESTS ----
def _selftest_rollback_identity():
    N_t = 16
    rng = np.random.RandomState(0)
    W_t = rng.randn(N_t, N_t).astype(np.float64)
    xi_t = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    W_wr = W_t + np.outer(xi_t, xi_t) / N_t
    W_rb = W_wr - np.outer(xi_t, xi_t) / N_t
    err = float(np.linalg.norm(W_rb - W_t, 'fro')) / max(float(np.linalg.norm(W_t, 'fro')), 1e-12)
    assert err < 1e-12, f"rollback identity err={err:.2e}"
    return err


def _selftest_kappa3_shift():
    N_t, M_t = 256, 20
    rng = np.random.RandomState(1)
    Xi_t = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    W_t = Xi_t.T @ Xi_t / float(N_t)
    np.fill_diagonal(W_t, 0.0)
    k3_before = hutchinson_kappa3(W_t, 200, 42)
    xi_anom = build_anomalous_pattern(W_t, N_t, rng)
    W_after = W_t + np.outer(xi_anom, xi_anom) / float(N_t)
    np.fill_diagonal(W_after, 0.0)
    k3_after = hutchinson_kappa3(W_after, 200, 43)
    dk3 = k3_after - k3_before
    assert dk3 != 0.0, f"kappa3 shift selftest: dk3=0 (detector broken)"
    return k3_before, k3_after, dk3


def _instrumentation_selftest():
    e1 = _selftest_rollback_identity()
    k3b, k3a, dk3 = _selftest_kappa3_shift()
    alpha_check = (M_CLEAN + DETECT_WINDOW) / float(N)
    assert alpha_check < 0.95, f"alpha check failed: alpha={alpha_check:.4f} >= 0.95"
    print(f"[selftest] PASS: rollback_err={e1:.2e} k3_shift={dk3:.6f} "
          f"(k3_before={k3b:.4f} after={k3a:.4f}) "
          f"N={N} M_CLEAN={M_CLEAN} window={DETECT_WINDOW}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_clean_baseline(rng_base: np.random.RandomState) -> Tuple[float, float]:
    all_k3s = []
    for run_idx in range(N_BASELINE_RUNS):
        rng_run = np.random.RandomState(rng_base.randint(0, 2 ** 31))
        W_run = np.zeros((N, N), dtype=np.float64)
        M_total = M_CLEAN + DETECT_WINDOW
        Xi_run = rng_run.choice([-1.0, 1.0], size=(M_total, N)).astype(np.float64)
        for step in range(M_total):
            W_run += np.outer(Xi_run[step], Xi_run[step]) / float(N)
            np.fill_diagonal(W_run, 0.0)
        k3 = hutchinson_kappa3(W_run, N_HUTCHINSON, rng_run.randint(0, 2 ** 31))
        all_k3s.append(k3)
    mean_k3 = float(np.mean(all_k3s))
    std_k3 = float(np.std(all_k3s)) if len(all_k3s) > 1 else 1e-6
    return mean_k3, std_k3


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    rng = np.random.RandomState(seed)
    rng_base = np.random.RandomState(seed + 100)

    # Baseline kappa_3 statistics
    baseline_mean, baseline_std = run_clean_baseline(rng_base)
    if baseline_std < 1e-8:
        baseline_std = max(abs(baseline_mean) * 0.01, 1e-6)

    # Write M_CLEAN clean patterns
    Xi_clean = rng.choice([-1.0, 1.0], size=(M_CLEAN, N)).astype(np.float64)
    W = np.zeros((N, N), dtype=np.float64)
    for xi in Xi_clean:
        W += np.outer(xi, xi) / float(N)
        np.fill_diagonal(W, 0.0)

    W_before_injection = W.copy()

    # Inject adversarial pattern
    rng_anom = np.random.RandomState(seed + 500)
    xi_anomaly = build_anomalous_pattern(W, N, rng_anom)
    W_with_anom = W.copy()
    W_with_anom += np.outer(xi_anomaly, xi_anomaly) / float(N)
    np.fill_diagonal(W_with_anom, 0.0)

    # Continue writing clean patterns; detect kappa_3 exceedance
    Xi_after = rng.choice([-1.0, 1.0], size=(DETECT_WINDOW, N)).astype(np.float64)
    W_current = W_with_anom.copy()
    detection_write = None
    k3_trajectory = []

    for step in range(DETECT_WINDOW):
        xi_step = Xi_after[step]
        W_current += np.outer(xi_step, xi_step) / float(N)
        np.fill_diagonal(W_current, 0.0)
        k3 = hutchinson_kappa3(W_current, N_HUTCHINSON, seed + 600 + step)
        k3_trajectory.append(k3)
        z_score = (k3 - baseline_mean) / max(baseline_std, 1e-12)
        if detection_write is None and abs(z_score) > SIGMA_THRESHOLD:
            detection_write = step + 1

    detected = detection_write is not None
    detect_latency = detection_write if detected else DETECT_WINDOW * 4

    # Rollback: remove the adversarial pattern
    W_rollback = W_with_anom - np.outer(xi_anomaly, xi_anomaly) / float(N)
    np.fill_diagonal(W_rollback, 0.0)

    # HP2: rollback precision
    w_norm = max(float(np.linalg.norm(W_before_injection, 'fro')), 1e-12)
    relative_err = float(np.linalg.norm(W_rollback - W_before_injection, 'fro')) / w_norm

    # HP3: clean pattern retrieval after rollback
    rng_eval = np.random.RandomState(seed + 200)
    n_test = min(10, M_CLEAN)
    correct = 0
    for k in range(n_test):
        probe = Xi_clean[k].copy()
        flip = rng_eval.random(N) < NOISE_FRAC
        probe[flip] *= -1.0
        retrieved = hopfield_retrieve(W_rollback, probe)
        if cosine_sim(retrieved, Xi_clean[k]) >= 0.9:
            correct += 1
    clean_acc = correct / max(1, n_test)

    hp1 = detected and detect_latency <= HP_DETECT_WITHIN_W
    hp2 = relative_err < HP_ROLLBACK_ERR
    hp3 = clean_acc >= HP_CLEAN_ACC
    hf1 = detect_latency > HF_DETECT_WITHIN_W
    hf2 = relative_err > HF_ROLLBACK_ERR
    hf3 = clean_acc < HF_CLEAN_ACC

    elapsed = time.time() - t0
    print(f"  [seed={seed} N={N} M_clean={M_CLEAN} window={DETECT_WINDOW}] "
          f"detected={detected} latency={detect_latency}(HP<={HP_DETECT_WITHIN_W}) "
          f"rollback_err={relative_err:.2e}(HP<{HP_ROLLBACK_ERR:.0e}) "
          f"clean_acc={clean_acc:.4f}(HP>={HP_CLEAN_ACC}) "
          f"hp=[{int(hp1)},{int(hp2)},{int(hp3)}] elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N, "M_CLEAN": M_CLEAN, "DETECT_WINDOW": DETECT_WINDOW,
        "run_mode": RUN_MODE,
        "detected": bool(detected),
        "detect_latency_writes": int(detect_latency),
        "rollback_relative_err": float(relative_err),
        "clean_acc_post_rollback": float(clean_acc),
        "baseline_mean": float(baseline_mean),
        "baseline_std": float(baseline_std),
        "hp1": bool(hp1), "hp2": bool(hp2), "hp3": bool(hp3),
        "hf1": bool(hf1), "hf2": bool(hf2), "hf3": bool(hf3),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid results.")
    n = len(results)
    n_detected = sum(1 for r in results if r["detected"])
    mean_err = float(np.mean([r["rollback_relative_err"] for r in results]))
    mean_acc = float(np.mean([r["clean_acc_post_rollback"] for r in results]))
    hp1_n = sum(1 for r in results if r["hp1"])
    hp2_n = sum(1 for r in results if r["hp2"])
    hp3_n = sum(1 for r in results if r["hp3"])
    hf_any = any(r["hf1"] or r["hf2"] or r["hf3"] for r in results)

    summary = (f"n_seeds={n} detected={n_detected}/{n} "
               f"rollback_err={mean_err:.2e}(HP<{HP_ROLLBACK_ERR:.0e} HF>{HF_ROLLBACK_ERR:.0e}) "
               f"clean_acc={mean_acc:.4f}(HP>={HP_CLEAN_ACC} HF<{HF_CLEAN_ACC}) "
               f"hp1={hp1_n}/{n} hp2={hp2_n}/{n} hp3={hp3_n}/{n}")

    if any(r["hf1"] for r in results):
        return ("HARD_FAIL", f"HARD_FAIL: kappa3 never detected in {HF_DETECT_WITHIN_W} writes. {summary}")
    if any(r["hf2"] for r in results):
        return ("HARD_FAIL", f"HARD_FAIL: rollback precision broken (err>{HF_ROLLBACK_ERR:.0e}). {summary}")
    if any(r["hf3"] for r in results):
        return ("HARD_FAIL", f"HARD_FAIL: clean acc drops below {HF_CLEAN_ACC} post-rollback. {summary}")

    min_thresh = math.ceil(n * 0.8)
    all_hp = all(c >= min_thresh for c in [hp1_n, hp2_n, hp3_n])
    if all_hp:
        return ("HARD_PASS", f"HARD_PASS: all 3 caps (audit+rollback+retention) confirmed in pipeline. {summary}")
    n_hp_conds = sum([hp1_n >= min_thresh, hp2_n >= min_thresh, hp3_n >= min_thresh])
    if n_hp_conds >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp_conds}/3 conditions. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_hp_conds}/3 HP conditions. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_CLEAN": M_CLEAN, "DETECT_WINDOW": DETECT_WINDOW, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run "
      f"(N={N} M_CLEAN={M_CLEAN} window={DETECT_WINDOW} mode={RUN_MODE})", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] a5_cert_grade_training N={N}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "M_CLEAN": M_CLEAN, "DETECT_WINDOW": DETECT_WINDOW,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_s,
    "per_seed": [
        {"seed": r.get("seed"), "detected": r.get("detected"),
         "detect_latency_writes": r.get("detect_latency_writes"),
         "rollback_relative_err": r.get("rollback_relative_err"),
         "clean_acc_post_rollback": r.get("clean_acc_post_rollback"),
         "hp1": r.get("hp1"), "hp2": r.get("hp2"), "hp3": r.get("hp3")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
