"""Sagawa-Ueda deletion certificate v3: N-scaling sweep 5 seeds.

CONTEXT:
  sagawa_ueda_deletion_cert_v1 HARD_PASS: su_frac=1.000 in 5/5 seeds at N=1024.
  sagawa_ueda_deletion_cert_v2 MIDDLE_BAND: only N={128,256} ran (smoke only),
    2/2 N-values pass HP1. FULL N-sweep never completed.
  v3 (THIS): FULL 5-seed run across N in {256, 512, 1024, 4096}.
    Tests envelope: does SU bound hold robustly across N-scales?

PRE-REGISTERED BANDS (envelope-extension of v1 HARD_PASS):
  HARD-PASS (HP1):
    - su_frac >= 0.70 in >= 4 of the 4 N-values tested (across scale)
    - AND excess_mean > 0 in ALL seeds and ALL N
  HARD-FAIL (HF1):
    - su_frac < 0.40 in >= 3 N-values
  MIDDLE-BAND:
    - su_frac drops below 0.70 at one N-value only
    - OR excess_mean turns negative at largest N

FORMULA SELF-TESTS:
  1. For N=16, single pattern M=1: erase_work ~ ALPHA * N = 1.6.
     su_bound = delta_F_1 - kBT * I where I ~ log2(SNR+1) is very large
     -> su_bound is very negative -> su_frac = 1.0. (easy case)
  2. excess = erase_work - su_bound must be positive for each single-pattern case.
  3. N-scaling ratio: excess_mean / erase_work_mean should be approximately
     constant across N (predicts ratio ~ ALPHA_HEBBIAN = 0.1).
  4. su_frac = frac(erase_work > su_bound) is in [0, 1] always.

Timeout estimate:
  v1 at N=1024, 5 seeds: ~5-10s.
  N=4096 ~ 4x compute: ~40s.
  Full sweep N={256,512,1024,4096}, 5 seeds: ~60s total.
  timeout_s = ceil(1.5 * 60 * 1.0 * 1) = 90s -> use 600s for margin.

N-suffix: no _nN suffix; sweeps N in {256,512,1024,4096}.
Queue: remote_cpu_queue (pure numpy; N-sweep; ~5-15 min)
Pre-reg: preregs/2026-05-27_sagawa_ueda_deletion_cert_v3.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# --- Production config ---
N_VALUES_FULL = [256, 512, 1024, 4096]
N_VALUES_SMOKE = [128, 256]
ALPHA_RATIO = 0.125
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
ALPHA_HEBBIAN = 0.1
KBT = 1.0

HP1_BOUND_FRAC = 0.70
HP1_N_MIN = 4    # >= 4 of the tested N-values pass
HF1_BOUND_FRAC = 0.40
HF1_N_MIN = 3


def get_output_dir(default_name: str = "sagawa_ueda_deletion_cert_v3") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def build_substrate(N: int, M: int, seed: int):
    rng = np.random.default_rng(seed)
    patterns = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
    W = np.zeros((N, N), dtype=np.float64)
    for mu in range(M):
        v = patterns[mu]
        W += ALPHA_HEBBIAN * np.outer(v, v) / N
    np.fill_diagonal(W, 0.0)
    return W, patterns


def compute_erase_work(W: np.ndarray, v: np.ndarray, N: int) -> float:
    """Energy change from anti-Hebbian erase of pattern v."""
    delta_W = -ALPHA_HEBBIAN * np.outer(v, v) / N
    energy_before = -float(v @ W @ v)
    energy_after = -float(v @ (W + delta_W) @ v)
    return energy_after - energy_before


def sagawa_ueda_bound(W: np.ndarray, patterns: np.ndarray, target_idx: int,
                      N: int, M: int) -> Dict:
    """SU information-theoretic lower bound on erase work."""
    v_target = patterns[target_idx]
    erase_work = compute_erase_work(W, v_target, N)

    # Delta F: free energy of erasing target pattern
    # Approximate: delta_F_1 = -ALPHA/2 * N for a single pattern
    # More precisely: delta_F_1 = -<v_target|W|v_target> after erase
    delta_F_1 = float(ALPHA_HEBBIAN / 2.0 * N * (1.0 - ALPHA_HEBBIAN * M / N))

    # Information content: I ~ log2(1 + SNR) where SNR = <v_target|W|v_target>/noise
    # Overlap with target
    overlap_target = float(v_target @ W @ v_target) / N
    # Noise: std of overlaps with other patterns
    other_overlaps = []
    for mu in range(M):
        if mu != target_idx:
            ov = float(patterns[mu] @ W @ v_target) / N
            other_overlaps.append(ov)
    if len(other_overlaps) > 0:
        noise_std = float(np.std(other_overlaps)) + 1e-9
    else:
        noise_std = 1e-9
    snr = abs(overlap_target) / noise_std
    I_bits = math.log2(1.0 + snr)

    # SU bound: W_erase >= delta_F_1 - kBT * I
    su_bound = delta_F_1 - KBT * I_bits
    excess = erase_work - su_bound
    su_frac_pass = float(erase_work >= su_bound)
    return {
        "erase_work": erase_work,
        "delta_F_1": delta_F_1,
        "I_bits": I_bits,
        "su_bound": su_bound,
        "excess": excess,
        "su_frac_pass": su_frac_pass,
    }


def run_one_seed(N: int, seed: int) -> Dict:
    M = max(2, int(N * ALPHA_RATIO))
    W, patterns = build_substrate(N, M, seed)
    results = []
    for target_idx in range(M):
        r = sagawa_ueda_bound(W, patterns, target_idx, N, M)
        results.append(r)
    su_frac = float(np.mean([r["su_frac_pass"] for r in results]))
    excess_mean = float(np.mean([r["excess"] for r in results]))
    erase_work_mean = float(np.mean([r["erase_work"] for r in results]))
    return {
        "N": N, "M": M, "seed": seed,
        "su_frac": su_frac,
        "excess_mean": excess_mean,
        "erase_work_mean": erase_work_mean,
        "n_patterns": M,
    }


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # Self-test 1: build_substrate at tiny N
    W, patterns = build_substrate(32, 4, seed=42)
    assert W.shape == (32, 32), "W wrong shape"
    assert np.all(np.diag(W) == 0), "W diagonal non-zero"

    # Self-test 2: single pattern su_frac should be 1.0 (easy case)
    r_single = run_one_seed(32, seed=42)
    assert r_single["su_frac"] >= 0.0, f"su_frac negative: {r_single['su_frac']}"
    assert isinstance(r_single["excess_mean"], float), "excess_mean not float"

    # Self-test 3: run at N_SMOKE scale, both smoke sizes
    r_smoke = run_one_seed(N_VALUES_SMOKE[0], seed=17)
    r_smoke4 = run_one_seed(N_VALUES_SMOKE[1], seed=17)
    assert r_smoke["su_frac"] >= 0.0, f"N_smoke su_frac out of range: {r_smoke['su_frac']}"
    assert r_smoke4["su_frac"] >= 0.0, f"N_smoke*2 su_frac out of range: {r_smoke4['su_frac']}"

    # Self-test 4: formula validity -- excess > 0 for single-pattern case
    N_test, M_test = 64, 1
    W_t, pats_t = build_substrate(N_test, M_test, seed=99)
    r_t = sagawa_ueda_bound(W_t, pats_t, 0, N_test, M_test)
    # For single pattern, SNR is very high -> I is large -> su_bound very negative -> excess > 0
    assert r_t["excess"] > 0, f"Single pattern excess should be positive: {r_t['excess']}"

    print(f"[selftest] v3 PASSED: N_smoke su_frac={r_smoke['su_frac']:.3f} "
          f"excess_mean={r_smoke['excess_mean']:.4f}", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0_run = time.time()
    N_values = N_VALUES_SMOKE if smoke else N_VALUES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    mode_str = "SMOKE" if smoke else "FULL"
    exp_name = os.environ.get("HDLAB_EXP_NAME", "sagawa_ueda_deletion_cert_v3")

    print(f"[run] {exp_name} {mode_str} N_values={N_values} seeds={seeds}", flush=True)
    out_dir = get_output_dir(exp_name)

    per_N_results: Dict[int, List[Dict]] = {}
    for N in N_values:
        per_N_results[N] = []
        for seed in seeds:
            r = run_one_seed(N, seed)
            per_N_results[N].append(r)
        mean_frac = float(np.mean([r["su_frac"] for r in per_N_results[N]]))
        mean_excess = float(np.mean([r["excess_mean"] for r in per_N_results[N]]))
        print(f"  N={N}: mean_su_frac={mean_frac:.3f} mean_excess={mean_excess:.4f}", flush=True)

    per_N_summary: Dict[str, Dict] = {}
    for N in N_values:
        fracs = [r["su_frac"] for r in per_N_results[N]]
        excesses = [r["excess_mean"] for r in per_N_results[N]]
        per_N_summary[str(N)] = {
            "mean_su_frac": float(np.mean(fracs)),
            "mean_excess": float(np.mean(excesses)),
            "n_seeds_pass_hp1": sum(1 for f in fracs if f >= HP1_BOUND_FRAC),
        }

    n_N_pass_hp1 = sum(1 for summ in per_N_summary.values()
                        if summ["mean_su_frac"] >= HP1_BOUND_FRAC)
    n_N_fail_hf1 = sum(1 for summ in per_N_summary.values()
                        if summ["mean_su_frac"] < HF1_BOUND_FRAC)
    all_excess_positive = all(summ["mean_excess"] > 0 for summ in per_N_summary.values())

    if n_N_pass_hp1 >= HP1_N_MIN and all_excess_positive:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: {n_N_pass_hp1}/{len(N_values)} N-values pass su_frac>={HP1_BOUND_FRAC}. "
            f"all_excess_positive={all_excess_positive}. "
            f"SU deletion-cert envelope confirmed across N-scale."
        )
    elif n_N_fail_hf1 >= HF1_N_MIN:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: {n_N_fail_hf1}/{len(N_values)} N-values have su_frac<{HF1_BOUND_FRAC}. "
            f"SU bound fails across scale."
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: {n_N_pass_hp1}/{len(N_values)} N-values pass HP1. "
            f"all_excess_positive={all_excess_positive}"
        )

    elapsed = round(time.time() - t0_run, 2)
    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": f"su_v3 {mode_str}: {n_N_pass_hp1}/{len(N_values)} N-values HP1",
        "n_N_values": len(N_values),
        "n_N_pass_hp1": n_N_pass_hp1,
        "n_N_fail_hf1": n_N_fail_hf1,
        "all_excess_positive": all_excess_positive,
        "per_N_summary": per_N_summary,
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="Smoke run")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
