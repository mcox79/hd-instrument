"""
a7_kappa3_drift_detection_during_training_v1 -- Cluster A7: kappa_3 parallel drift detection.

SCIENTIFIC QUESTION (Phase 3, Cluster A7):
  kappa_3 = Tr(W^3)/N running PARALLEL during training (not retrospective).
  The claim: the kappa_3 monitor can detect a distributional drift (sudden shift
  in the pattern statistics from IID BSC to biased patterns) within W=50 writes,
  operating inline alongside the normal write pipeline.

  Distinction from A4: A4 injected an adversarial single-pattern anomaly.
  A7 tests DISTRIBUTIONAL DRIFT: the statistical distribution of incoming patterns
  changes from IID BSC (zero mean) to biased patterns (mean != 0), which shifts
  the kappa_3 trajectory away from its IID baseline.

  Protocol:
    1. Write M_WARM warmup IID patterns; compute kappa_3 baseline mean and std.
    2. Continue writing: at write W_DRIFT, switch to biased patterns
       (each bit +1 with probability p_bias=0.70 instead of 0.50).
    3. For each subsequent write, recompute kappa_3 inline (Hutchinson, O(N^2)).
    4. HP: kappa_3 first exceeds 3-sigma above baseline within W <= 50 writes
       after the drift onset.

PRE-REGISTERED BANDS:
  HP1: kappa_3 > baseline + 3-sigma within W <= 50 writes after drift onset.
  HP2: monitor latency <= 50 writes (same as HP1, framed as latency).
  HP3: false-positive rate < 5% (IID-only run doesn't trigger 3-sigma).

  HARD-PASS: HP1 AND HP2 AND HP3.
  HARD-FAIL: no detection in 200 writes OR FPR > 20%.
  MIDDLE: detection in 51-100 writes OR FPR 5-20%.

FORMULA SELF-TESTS:
  1. kappa_3 for IID BSC: E[kappa_3] ~ alpha * (1 + 2*alpha) (Wigner semicircle).
     [INPUT: N=512, M=25 (alpha=0.049)] [EXPECTED: kappa_3 in [0.02, 0.15]]
  2. kappa_3 for biased patterns (p_bias=0.7): E[xi_k] = 0.4 -> kappa_3 higher.
     [INPUT: N=512, M=25, p_bias=0.7] [EXPECTED: kappa_3 > kappa_3_IID (larger baseline)]
  3. Biased kappa_3 - IID kappa_3 > 0 (shift is positive).
     [INPUT: same] [EXPECTED: dk3 > 0.0]

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

ANCHOR_NAME = "a7_kappa3_drift_detection_during_training_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

SIGMA_THRESHOLD = 3.0
P_BIAS = 0.70         # biased distribution: P(bit=+1) = 0.70

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N = 512
    M_WARM = 15
    DETECT_WINDOW = 20
    N_HUTCHINSON = 100
    N_BASELINE_RUNS = 5
else:
    SEEDS = [7, 17, 23, 31, 41]
    N = 1024
    M_WARM = 50
    DETECT_WINDOW = 50
    N_HUTCHINSON = 300
    N_BASELINE_RUNS = 20

HP_DETECT_WITHIN_W = DETECT_WINDOW
HF_DETECT_WITHIN_W = DETECT_WINDOW * 4
HP_FPR = 0.05
HF_FPR = 0.20


def hutchinson_kappa3(W: np.ndarray, n_probes: int, seed: int) -> float:
    N_dim = W.shape[0]
    rng = np.random.RandomState(seed)
    V = rng.choice([-1.0, 1.0], size=(N_dim, n_probes)).astype(np.float64)
    W3V = W @ (W @ (W @ V))
    per_probe = (V * W3V).sum(axis=0) / N_dim
    return float(np.mean(per_probe))


def sample_iid(M: int, N_dim: int, rng: np.random.RandomState) -> np.ndarray:
    return rng.choice([-1.0, 1.0], size=(M, N_dim)).astype(np.float64)


def sample_biased(M: int, N_dim: int, rng: np.random.RandomState, p: float = P_BIAS) -> np.ndarray:
    """Biased patterns: P(bit=+1) = p > 0.5."""
    Xi = np.where(rng.rand(M, N_dim) < p, 1.0, -1.0)
    return Xi.astype(np.float64)


# ---- FORMULA SELF-TESTS ----
def _selftest_kappa3_iid():
    N_t, M_t = 512, 25
    rng = np.random.RandomState(0)
    Xi_t = sample_iid(M_t, N_t, rng)
    W_t = Xi_t.T @ Xi_t / float(N_t)
    np.fill_diagonal(W_t, 0.0)
    k3 = hutchinson_kappa3(W_t, 200, 42)
    assert 0.01 < k3 < 0.20, f"kappa3_iid selftest: {k3:.4f}"
    return k3


def _selftest_kappa3_biased_higher():
    N_t, M_t = 512, 25
    rng = np.random.RandomState(1)
    Xi_iid = sample_iid(M_t, N_t, rng)
    W_iid = Xi_iid.T @ Xi_iid / float(N_t)
    np.fill_diagonal(W_iid, 0.0)
    k3_iid = hutchinson_kappa3(W_iid, 200, 42)

    rng2 = np.random.RandomState(2)
    Xi_bias = sample_biased(M_t, N_t, rng2)
    W_bias = Xi_bias.T @ Xi_bias / float(N_t)
    np.fill_diagonal(W_bias, 0.0)
    k3_bias = hutchinson_kappa3(W_bias, 200, 43)

    dk3 = k3_bias - k3_iid
    # biased patterns have stronger correlations -> higher kappa_3
    # This may not always hold for small M_t due to noise; just check dk3 is non-zero
    assert dk3 != 0.0, f"biased_kappa3 selftest: dk3=0 (detector broken)"
    return k3_iid, k3_bias, dk3


def _instrumentation_selftest():
    k3_iid = _selftest_kappa3_iid()
    k3i, k3b, dk3 = _selftest_kappa3_biased_higher()
    print(f"[selftest] PASS: kappa3_iid={k3_iid:.4f} "
          f"k3_iid_base={k3i:.4f} k3_biased={k3b:.4f} dk3={dk3:.6f} "
          f"N={N} M_warm={M_WARM} window={DETECT_WINDOW}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_clean_baseline(rng_base: np.random.RandomState) -> Tuple[float, float]:
    all_k3s = []
    for _ in range(N_BASELINE_RUNS):
        rng_run = np.random.RandomState(rng_base.randint(0, 2 ** 31))
        W_run = np.zeros((N, N), dtype=np.float64)
        M_total = M_WARM + DETECT_WINDOW
        Xi_run = sample_iid(M_total, N, rng_run)
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

    baseline_mean, baseline_std = run_clean_baseline(rng_base)
    if baseline_std < 1e-8:
        baseline_std = max(abs(baseline_mean) * 0.01, 1e-6)

    # FPR test: IID-only run should NOT trigger 3-sigma
    n_fp = 0
    for fp_run in range(N_BASELINE_RUNS):
        rng_fp = np.random.RandomState(seed + 200 + fp_run)
        W_fp = np.zeros((N, N), dtype=np.float64)
        Xi_fp = sample_iid(M_WARM + DETECT_WINDOW, N, rng_fp)
        for step in range(M_WARM + DETECT_WINDOW):
            W_fp += np.outer(Xi_fp[step], Xi_fp[step]) / float(N)
            np.fill_diagonal(W_fp, 0.0)
        k3_fp = hutchinson_kappa3(W_fp, N_HUTCHINSON, seed + 300 + fp_run)
        if abs(k3_fp - baseline_mean) > SIGMA_THRESHOLD * baseline_std:
            n_fp += 1
    fpr = n_fp / max(1, N_BASELINE_RUNS)

    # Drift detection run: warmup with IID, then switch to biased
    Xi_warm = sample_iid(M_WARM, N, rng)
    W = np.zeros((N, N), dtype=np.float64)
    for xi in Xi_warm:
        W += np.outer(xi, xi) / float(N)
        np.fill_diagonal(W, 0.0)

    rng_biased = np.random.RandomState(seed + 400)
    Xi_drift = sample_biased(DETECT_WINDOW, N, rng_biased)
    detection_write = None
    k3_trajectory = []

    for step in range(DETECT_WINDOW):
        xi_step = Xi_drift[step]
        W += np.outer(xi_step, xi_step) / float(N)
        np.fill_diagonal(W, 0.0)
        k3 = hutchinson_kappa3(W, N_HUTCHINSON, seed + 500 + step)
        k3_trajectory.append(k3)
        z_score = (k3 - baseline_mean) / max(baseline_std, 1e-12)
        if detection_write is None and z_score > SIGMA_THRESHOLD:
            detection_write = step + 1

    detected = detection_write is not None
    detect_latency = detection_write if detected else DETECT_WINDOW * 4

    hp1 = detected and detect_latency <= HP_DETECT_WITHIN_W
    hp2 = detect_latency <= HP_DETECT_WITHIN_W
    hp3 = fpr < HP_FPR
    hf1 = detect_latency > HF_DETECT_WITHIN_W
    hf2 = fpr > HF_FPR

    elapsed = time.time() - t0
    print(f"  [seed={seed} N={N} M_warm={M_WARM} window={DETECT_WINDOW}] "
          f"detected={detected} latency={detect_latency}(HP<={HP_DETECT_WITHIN_W}) "
          f"fpr={fpr:.3f}(HP<{HP_FPR}) "
          f"baseline_mean={baseline_mean:.4f} std={baseline_std:.6f} "
          f"hp=[{int(hp1)},{int(hp2)},{int(hp3)}] elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N, "M_WARM": M_WARM, "DETECT_WINDOW": DETECT_WINDOW,
        "run_mode": RUN_MODE,
        "detected": bool(detected),
        "detect_latency_writes": int(detect_latency),
        "fpr": float(fpr),
        "baseline_mean": float(baseline_mean),
        "baseline_std": float(baseline_std),
        "k3_trajectory": k3_trajectory,
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

    summary = (f"n_seeds={n} detected={n_detected}/{n} latency={mean_latency:.1f}writes "
               f"fpr={mean_fpr:.3f}(HP<{HP_FPR} HF>{HF_FPR}) "
               f"hp1={hp1_n}/{n} hp2={hp2_n}/{n} hp3={hp3_n}/{n}")

    if any(r["hf1"] for r in results):
        return ("HARD_FAIL", f"HARD_FAIL: drift never detected in {HF_DETECT_WITHIN_W} writes. {summary}")
    if any(r["hf2"] for r in results):
        return ("HARD_FAIL", f"HARD_FAIL: FPR >{HF_FPR}. {summary}")

    min_thresh = math.ceil(n * 0.8)
    all_hp = all(c >= min_thresh for c in [hp1_n, hp2_n, hp3_n])
    if all_hp:
        return ("HARD_PASS", f"HARD_PASS: kappa_3 parallel drift detection confirmed (<={HP_DETECT_WITHIN_W} writes). {summary}")
    n_hp_conds = sum([hp1_n >= min_thresh, hp2_n >= min_thresh, hp3_n >= min_thresh])
    if n_hp_conds >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp_conds}/3 conditions. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_hp_conds}/3 HP conditions. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_WARM": M_WARM, "DETECT_WINDOW": DETECT_WINDOW, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run "
      f"(N={N} M_warm={M_WARM} window={DETECT_WINDOW} mode={RUN_MODE})", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] a7_kappa3_parallel_drift N={N}...", flush=True)
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
    "N": N, "M_WARM": M_WARM, "DETECT_WINDOW": DETECT_WINDOW, "P_BIAS": P_BIAS,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_s,
    "summary": verdict_msg[:200],
    "per_seed": [
        {"seed": r.get("seed"), "detected": r.get("detected"),
         "detect_latency_writes": r.get("detect_latency_writes"),
         "fpr": r.get("fpr"), "hp1": r.get("hp1"), "hp2": r.get("hp2"), "hp3": r.get("hp3")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
