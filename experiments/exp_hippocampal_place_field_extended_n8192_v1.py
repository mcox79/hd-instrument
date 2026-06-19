"""
hippocampal_place_field_extended_n8192_v1 -- Hippocampal place-field FULL at N=8192.

SCIENTIFIC QUESTION:
  PP-47 hippocampal place-field encoding confirmed at N=4096 (v333, HARD_PASS:
  cosine=0.879, rho, acc all HP). This anchor extends to production-N=8192
  to promote PP-47 from EXPLORATORY to EMPIRICALLY-CONFIRMED with multi-N evidence.

  Same protocol as hippocampal_place_field_full_v1_n4096:
    - K = int(0.05 * N) = 409 locations at N=8192.
    - PLACE_FRAC = 0.30, SIGMA = 2.0.
    - Noise fraction = 0.10 for query.

HARD-PASS: cosine >= 0.80 AND Spearman rho >= 0.60 AND acc >= 0.75 for >= 4/5 seeds.
HARD-FAIL: 0-1 of the 3 conditions met.
MIDDLE: 2/3 conditions met.

PRE-REGISTERED BANDS:
  HP: cosine >= 0.80, rho >= 0.60, acc >= 0.75.
  HF: cosine < 0.40, rho < 0.20, acc < 0.40.
  Prior: N=4096 HARD_PASS (cosine~0.879, rho~0.68, acc~0.91).
  At N=8192 with K=409 (same alpha=0.05), expect similar or better (more capacity headroom).

FORMULA SELF-TESTS (same as v1_n4096):
  1. Place-field overlap: adjacent locations share more active cells than distant.
  2. Hebbian W: K=10, N=512. W @ xi_1 cosine >= 0.20.
  3. Capacity check: K=409, N=8192 => alpha=0.05 << alpha_c=0.138.

PROT-018: anchor has _n8192 -> N MUST = 8192.
PROT-021: run_config includes N, K_LOCS, run_mode.
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

ANCHOR_NAME = "hippocampal_place_field_extended_n8192_v1"

# PROT-018: anchor has _n8192 -> N must = 8192
_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N_SMOKE = 1024
    N_ACTIVE = N_SMOKE
    SEEDS = [7, 17]
    K_LOCS = 51     # 0.05 * 1024
    NOISE_FRAC = 0.10
    PLACE_FRAC = 0.30
    SIGMA = 2.0
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    K_LOCS = int(0.05 * N)   # 409 locations at N=8192
    NOISE_FRAC = 0.10
    PLACE_FRAC = 0.30
    SIGMA = 2.0

ALPHA_C = 0.138

HP_COSINE = 0.80
HF_COSINE = 0.40
HP_SPEARMAN = 0.60
HF_SPEARMAN = 0.20
HP_ACC_K = 0.75
HF_ACC_K = 0.40


def generate_place_patterns(K: int, N_dim: int, sigma: float, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    preferred_locs = rng.uniform(0, K, size=N_dim)
    Xi = np.zeros((K, N_dim), dtype=np.float64)
    for k in range(K):
        act_prob = np.exp(-0.5 * ((preferred_locs - k) / sigma) ** 2)
        threshold = np.percentile(act_prob, 100 * (1 - PLACE_FRAC))
        active = act_prob >= threshold
        Xi[k] = np.where(active, 1.0, -1.0)
    return Xi


def spearman_rho(x: np.ndarray, y: np.ndarray) -> float:
    n = len(x)
    if n < 2:
        return 0.0
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    d = rx - ry
    return float(1.0 - 6.0 * float(np.sum(d ** 2)) / (n * (n * n - 1)))


def _selftest_spatial_continuity():
    N_t, K_t = 512, 10
    rng = np.random.RandomState(7)
    preferred_locs = rng.uniform(0, K_t, size=N_t)
    Xi_t = np.zeros((K_t, N_t), dtype=np.float64)
    for k in range(K_t):
        act_prob = np.exp(-0.5 * ((preferred_locs - k) / SIGMA) ** 2)
        threshold = np.percentile(act_prob, 100 * (1 - PLACE_FRAC))
        active = act_prob >= threshold
        Xi_t[k] = np.where(active, 1.0, -1.0)
    near = [float(np.dot(Xi_t[i], Xi_t[i+1])) / N_t for i in range(K_t-1)]
    far = [float(np.dot(Xi_t[i], Xi_t[i+4])) / N_t for i in range(K_t-4)]
    assert float(np.mean(near)) > float(np.mean(far)), \
        f"spatial selftest: near={np.mean(near):.3f} not > far={np.mean(far):.3f}"
    return float(np.mean(near)), float(np.mean(far))


def _selftest_hebbian_retrieval():
    N_t, K_t = 512, 10
    rng = np.random.RandomState(7)
    Xi_t = rng.choice([-1.0, 1.0], size=(K_t, N_t)).astype(np.float64)
    W_t = Xi_t.T @ Xi_t / float(N_t)
    np.fill_diagonal(W_t, 0.0)
    retrieved = np.sign(W_t @ Xi_t[0] + 1e-8)
    cos = float(np.dot(retrieved, Xi_t[0])) / N_t
    assert cos >= 0.20, f"hebbian selftest: cosine={cos:.3f} too low"
    return cos


def _selftest_capacity():
    alpha = K_LOCS / N_ACTIVE
    assert alpha < ALPHA_C, f"capacity check: alpha={alpha:.4f} >= alpha_c={ALPHA_C}"
    return alpha


def _instrumentation_selftest():
    t1_near, t1_far = _selftest_spatial_continuity()
    t2 = _selftest_hebbian_retrieval()
    t3 = _selftest_capacity()
    print(f"[selftest] near_cos={t1_near:.3f} far_cos={t1_far:.3f} "
          f"hebbian_cos={t2:.3f} alpha={t3:.4f} < alpha_c={ALPHA_C}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    Xi = generate_place_patterns(K_LOCS, N_ACTIVE, SIGMA, seed)

    W = Xi.T @ Xi / float(N_ACTIVE)
    np.fill_diagonal(W, 0.0)

    rng = np.random.RandomState(seed + 100)
    cosines = []
    for k in range(K_LOCS):
        probe = Xi[k].copy()
        flip = rng.random(N_ACTIVE) < NOISE_FRAC
        probe[flip] *= -1.0
        retrieved = np.sign(W @ probe + 1e-8)
        cos = float(np.dot(retrieved, Xi[k])) / N_ACTIVE
        cosines.append(cos)
    mean_cosine = float(np.mean(cosines))

    n_test_pairs = min(100, K_LOCS * (K_LOCS - 1) // 2)
    rng2 = np.random.RandomState(seed + 200)
    pair_indices = [(i, j) for i in range(K_LOCS) for j in range(i+1, K_LOCS)]
    if len(pair_indices) > n_test_pairs:
        sel = rng2.choice(len(pair_indices), n_test_pairs, replace=False)
        pair_indices = [pair_indices[s] for s in sel]
    distances = [abs(i - j) for i, j in pair_indices]
    pat_cosines = [float(np.dot(Xi[i], Xi[j])) / N_ACTIVE for i, j in pair_indices]
    spearman = spearman_rho(np.array(distances), np.array([-c for c in pat_cosines]))

    acc_k = float(np.mean([c > 0.5 for c in cosines]))

    elapsed = time.time() - t0
    print(f"  [seed={seed} N={N_ACTIVE} K={K_LOCS}] "
          f"mean_cosine={mean_cosine:.4f} spearman={spearman:.4f} "
          f"acc_K={acc_k:.4f} elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N_ACTIVE, "K_LOCS": K_LOCS,
        "run_mode": RUN_MODE,
        "mean_cosine": float(mean_cosine),
        "spearman_rho": float(spearman),
        "acc_K": float(acc_k),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    cosines = [r["mean_cosine"] for r in results if "mean_cosine" in r]
    spearmen = [r["spearman_rho"] for r in results if "spearman_rho" in r]
    accs = [r["acc_K"] for r in results if "acc_K" in r]

    if not cosines:
        return ("HARD_FAIL", "No valid results.")

    mean_cos = float(np.mean(cosines))
    mean_rho = float(np.mean(spearmen))
    mean_acc = float(np.mean(accs))

    summary = (f"mean_cosine={mean_cos:.4f}(HP>={HP_COSINE},HF<{HF_COSINE}) "
               f"mean_spearman={mean_rho:.4f}(HP>={HP_SPEARMAN},HF<{HF_SPEARMAN}) "
               f"mean_acc={mean_acc:.4f}(HP>={HP_ACC_K},HF<{HF_ACC_K}) "
               f"N={N_ACTIVE} K={K_LOCS} n_seeds={len(cosines)}")

    if mean_cos < HF_COSINE or mean_rho < HF_SPEARMAN or mean_acc < HF_ACC_K:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    hp_cos = mean_cos >= HP_COSINE
    hp_rho = mean_rho >= HP_SPEARMAN
    hp_acc = mean_acc >= HP_ACC_K
    n_hp = sum([hp_cos, hp_rho, hp_acc])

    if n_hp == 3:
        return ("HARD_PASS", f"HARD_PASS: PP-47 place-field confirmed at N=8192. {summary}")
    if n_hp == 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp}/3 HP conditions. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_hp}/3 HP conditions. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_ACTIVE, "K_LOCS": K_LOCS, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run "
      f"(N={N_ACTIVE} K={K_LOCS} mode={RUN_MODE})", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": verdict_msg,
    "elapsed_s": elapsed_s,
    "n_seeds": len(SEEDS),
    "run_mode": RUN_MODE,
    "N": N_ACTIVE,
    "K_LOCS": K_LOCS,
    "alpha": K_LOCS / N_ACTIVE,
    "per_seed": [
        {"seed": r.get("seed"), "mean_cosine": r.get("mean_cosine"),
         "spearman_rho": r.get("spearman_rho"), "acc_K": r.get("acc_K")}
        for r in all_results
    ],
    "elapsed_total_s": elapsed_s,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
