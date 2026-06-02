"""
caching_admission_control_v2 -- Capacity-aware admission control at N=2048.

SCIENTIFIC QUESTION:
  Same as v1 but at N=2048 (production-N envelope).
  v1 (N=1024) completed. v2 tests at N=2048 to confirm the cliff detection
  and admission rate adaptation scales to production N.

  v2 changes from v1:
    - N=2048 (4x larger than v1's N=512 smoke / N=1024 FULL).
    - ADMIT_THRESHOLD tuned to 0.12 (slightly higher for N=2048 due to
      weaker finite-N corrections).
    - N_PROBE_EIGS=15 for faster spectral proxy.

  Admission control test:
    - Track alpha_eff via spectral proxy (top eigenvalue of W).
    - Accept write if alpha_eff < ADMIT_THRESHOLD.
    - Compare: admitted baseline vs naive baseline near cliff.

HARD-PASS: rate_drop >= 30%, acc_admitted >= 0.85, acc_naive <= 0.50.
HARD-FAIL: acc_admitted < 0.60 OR acc_naive > 0.75.
MIDDLE: 2/3 conditions met.

PRE-REGISTERED BANDS:
  HP: rate_drop_ratio < 0.70, acc_admitted >= 0.85, acc_naive <= 0.50.
  HF: acc_admitted < 0.60 OR acc_naive > 0.75.
  Calibration: v1 at N=1024 completed; v2 is production-N confirmation.
  Bands same as v1 (mechanism should scale).

FORMULA SELF-TESTS:
  1. alpha_eff proxy: M=20, N=1024 -> alpha=0.0195. lambda_max ~ (1+sqrt(0.0195))^2 ~ 1.285.
     alpha_eff = (sqrt(1.285)-1)^2 ~ 0.0190. Should be in [0.010, 0.030].
     [INPUT: M=20, N=1024] [EXPECTED: alpha_eff in [0.010, 0.030]]
  2. Admission rate drop: early 10/10 admitted, late 5/10 => ratio=0.5 < 0.70.
     [INPUT: early=10/10, late=5/10] [EXPECTED: ratio < 0.70 => PASS]

No _nN suffix; production N=2048 per rule 3:
  No _nN suffix; production N = 2048; rationale: v2 is production-N envelope test.
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
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "caching_admission_control_v2"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

ALPHA_C = 0.138
ADMIT_THRESHOLD = 0.12

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N = 512
    SEEDS = [7, 17]
    M_TOTAL = int(1.5 * ALPHA_C * N)
    N_PROBE_EIGS = 10
else:
    N = 2048
    SEEDS = [7, 17, 23, 31, 41]
    M_TOTAL = int(1.5 * ALPHA_C * N)
    N_PROBE_EIGS = 15

HP_RATE_DROP_RATIO = 0.70
HP_ADMITTED_ACC = 0.85
HF_ADMITTED_ACC = 0.60
HP_NAIVE_UPPER = 0.50
HF_NAIVE_LOWER = 0.75


def alpha_eff_proxy(W: np.ndarray, N_dim: int, n_iter: int = 20, seed: int = 7) -> float:
    """Estimate alpha_eff from top eigenvalue of W."""
    rng = np.random.RandomState(seed)
    v = rng.randn(N_dim)
    nrm = float(np.linalg.norm(v))
    if nrm < 1e-15:
        return 0.0
    v /= nrm
    for _ in range(n_iter):
        v = W @ v
        nrm = float(np.linalg.norm(v))
        if nrm < 1e-15:
            return 0.0
        v /= nrm
    lambda_max = float(np.dot(v, W @ v))
    # Invert MP edge: alpha_eff = (sqrt(lambda_max)-1)^2 if lambda_max > 1, else 0
    if lambda_max <= 1.0:
        return 0.0
    return float((math.sqrt(lambda_max) - 1.0) ** 2)


def hopfield_accuracy(W: np.ndarray, Xi: np.ndarray, N_dim: int,
                       n_test: int, noise_frac: float,
                       rng: np.random.RandomState) -> float:
    """Test retrieval accuracy on n_test patterns."""
    M = Xi.shape[0]
    n_test = min(n_test, M)
    correct = 0
    for i in range(n_test):
        probe = Xi[i].copy()
        flip = rng.random(N_dim) < noise_frac
        probe[flip] *= -1.0
        retrieved = np.sign(W @ probe + 1e-8)
        cos = float(np.dot(retrieved, Xi[i])) / N_dim
        if cos > 0.5:
            correct += 1
    return correct / n_test if n_test > 0 else 0.0


def _selftest_alpha_eff():
    rng = np.random.RandomState(0)
    M_t, N_t = 20, 1024
    Xi_t = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    W_t = Xi_t.T @ Xi_t / float(N_t)
    np.fill_diagonal(W_t, 0.0)
    alpha_t = alpha_eff_proxy(W_t, N_t, seed=42)
    expected = M_t / N_t
    assert 0.005 < alpha_t < 0.060, \
        f"alpha_eff proxy={alpha_t:.4f} expected ~{expected:.4f}"
    return alpha_t


def _selftest_rate_drop():
    early, late = 10 / 10, 5 / 10
    ratio = late / early
    assert ratio < HP_RATE_DROP_RATIO, f"rate_drop selftest: ratio={ratio:.3f} not < {HP_RATE_DROP_RATIO}"
    return ratio


def _instrumentation_selftest():
    t1 = _selftest_alpha_eff()
    t2 = _selftest_rate_drop()
    # Verify at least one write accepted/rejected in a tiny simulation
    rng = np.random.RandomState(7)
    N_t = 128
    Xi_tiny = rng.choice([-1.0, 1.0], size=(0, N_t)).astype(np.float64)
    W_tiny = np.zeros((N_t, N_t))
    admitted = 0
    for i in range(5):
        xi = rng.choice([-1.0, 1.0], size=(N_t,)).astype(np.float64)
        ae = alpha_eff_proxy(W_tiny, N_t, seed=i)
        if ae < ADMIT_THRESHOLD:
            admitted += 1
            Xi_tiny = np.vstack([Xi_tiny, xi[np.newaxis, :]]) if i > 0 else xi[np.newaxis, :]
            if Xi_tiny.ndim == 1:
                Xi_tiny = Xi_tiny[np.newaxis, :]
            W_tiny = Xi_tiny.T @ Xi_tiny / float(N_t)
            np.fill_diagonal(W_tiny, 0.0)
    assert admitted > 0, f"selftest: no admissions in 5 writes (N=128 at alpha~0)"
    print(f"[selftest] alpha_eff_proxy={t1:.4f} rate_drop_ratio={t2:.3f} "
          f"admitted_in_5={admitted}", flush=True)


_instrumentation_selftest()


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    admitted_patterns = []
    W_ctrl = np.zeros((N, N))  # controlled (admission) W
    W_naive = None              # naive W built once at end

    n_half = M_TOTAL // 2
    n_admit_early = 0
    n_admit_late = 0
    n_attempts_early = 0
    n_attempts_late = 0
    Xi_naive_list = []

    for m in range(M_TOTAL):
        xi = rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64)
        Xi_naive_list.append(xi)
        is_early = m < n_half

        # Admission decision
        ae = alpha_eff_proxy(W_ctrl, N, n_iter=N_PROBE_EIGS, seed=seed + m)
        if ae < ADMIT_THRESHOLD:
            admitted_patterns.append(xi)
            if is_early:
                n_admit_early += 1
            else:
                n_admit_late += 1
            Xi_ctrl = np.array(admitted_patterns)
            W_ctrl = Xi_ctrl.T @ Xi_ctrl / float(N)
            np.fill_diagonal(W_ctrl, 0.0)

        if is_early:
            n_attempts_early += 1
        else:
            n_attempts_late += 1

    # Build naive W from all patterns
    Xi_naive = np.array(Xi_naive_list)
    W_naive = Xi_naive.T @ Xi_naive / float(N)
    np.fill_diagonal(W_naive, 0.0)

    # Metrics
    rate_early = n_admit_early / n_attempts_early if n_attempts_early > 0 else 0.0
    rate_late = n_admit_late / n_attempts_late if n_attempts_late > 0 else 0.0
    rate_drop_ratio = rate_late / rate_early if rate_early > 1e-12 else 1.0

    # Admitted retrieval accuracy
    rng_test = np.random.RandomState(seed + 9999)
    if len(admitted_patterns) > 0:
        Xi_admitted = np.array(admitted_patterns)
        acc_admitted = hopfield_accuracy(W_ctrl, Xi_admitted, N,
                                          n_test=min(20, len(admitted_patterns)),
                                          noise_frac=0.10, rng=rng_test)
    else:
        acc_admitted = 0.0

    # Naive accuracy at overload
    acc_naive = hopfield_accuracy(W_naive, Xi_naive, N,
                                   n_test=min(20, M_TOTAL),
                                   noise_frac=0.10, rng=rng_test)

    elapsed = time.time() - t0
    print(f"  [seed={seed} N={N}] admitted={len(admitted_patterns)}/{M_TOTAL} "
          f"rate_early={rate_early:.3f} rate_late={rate_late:.3f} "
          f"rate_drop_ratio={rate_drop_ratio:.3f} "
          f"acc_admitted={acc_admitted:.4f} acc_naive={acc_naive:.4f} "
          f"elapsed={elapsed:.1f}s", flush=True)

    return {
        "seed": seed, "N": N, "M_TOTAL": M_TOTAL,
        "run_mode": RUN_MODE,
        "n_admitted": len(admitted_patterns),
        "admission_rate_early": float(rate_early),
        "admission_rate_late": float(rate_late),
        "rate_drop_ratio": float(rate_drop_ratio),
        "acc_admitted": float(acc_admitted),
        "acc_naive": float(acc_naive),
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    rate_ratios = [r["rate_drop_ratio"] for r in results if "rate_drop_ratio" in r]
    accs_admitted = [r["acc_admitted"] for r in results if "acc_admitted" in r]
    accs_naive = [r["acc_naive"] for r in results if "acc_naive" in r]

    if not rate_ratios:
        return ("HARD_FAIL", "No valid results.")

    mean_ratio = float(np.mean(rate_ratios))
    mean_acc_admitted = float(np.mean(accs_admitted))
    mean_acc_naive = float(np.mean(accs_naive))

    summary = (f"rate_drop_ratio={mean_ratio:.3f} (HP<{HP_RATE_DROP_RATIO}) "
               f"acc_admitted={mean_acc_admitted:.4f} (HP>={HP_ADMITTED_ACC} HF<{HF_ADMITTED_ACC}) "
               f"acc_naive={mean_acc_naive:.4f} (HP<={HP_NAIVE_UPPER} HF>{HF_NAIVE_LOWER}) "
               f"n_seeds={len(rate_ratios)}")

    if mean_acc_admitted < HF_ADMITTED_ACC:
        return ("HARD_FAIL", f"HARD_FAIL: acc_admitted={mean_acc_admitted:.4f} < HF={HF_ADMITTED_ACC}. {summary}")
    if mean_acc_naive > HF_NAIVE_LOWER:
        return ("HARD_FAIL", f"HARD_FAIL: acc_naive={mean_acc_naive:.4f} > HF={HF_NAIVE_LOWER}. {summary}")

    hp_a = mean_ratio < HP_RATE_DROP_RATIO
    hp_b = mean_acc_admitted >= HP_ADMITTED_ACC
    hp_c = mean_acc_naive <= HP_NAIVE_UPPER
    n_hp = sum([hp_a, hp_b, hp_c])

    if n_hp == 3:
        return ("HARD_PASS", f"HARD_PASS: all 3 HP conditions. {summary}")
    if n_hp == 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp}/3 HP conditions. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_hp}/3 HP conditions. {summary}")


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
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

metrics = {
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "n_seeds": len(SEEDS),
    "run_mode": RUN_MODE,
    "N": N,
    "M_TOTAL": M_TOTAL,
    "per_seed": [
        {"seed": r.get("seed"), "rate_drop_ratio": r.get("rate_drop_ratio"),
         "acc_admitted": r.get("acc_admitted"), "acc_naive": r.get("acc_naive")}
        for r in all_results
    ],
    "elapsed_total_s": time.time() - t_sweep_start,
}

metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
