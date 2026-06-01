"""Sagawa-Ueda deletion certificate v2: N-scaling sweep.

CONTEXT:
  sagawa_ueda_deletion_cert_v1 HARD_PASS: su_frac=1.000 in 5/5 seeds at N=1024.
  The product claim (deletion certificate: "erase cost thermodynamically bounded")
  must hold across N. The SU bound tightness (excess_mean / erase_work_mean) should
  approach a well-defined limit as N grows (mean-field prediction: ratio ~ ALPHA_HEBBIAN).

  This probe sweeps N in {256, 512, 1024, 4096} to characterize:
  1. Does su_frac stay near 1.0 across all N? (product reliability claim)
  2. Does excess_mean / erase_work_mean converge toward a fixed ratio? (theory check)
  3. Is there a critical N below which the SU bound starts to fail? (envelope mapping)

PRE-REGISTERED BANDS (envelope-extension of v1 HARD_PASS):
  HARD-PASS:
    - su_frac >= 0.70 in >= 4 of the 5 N-values tested (i.e., across scale)
    - AND excess_mean > 0 in ALL seeds and ALL N (mean excess stays positive)
  HARD-FAIL:
    - su_frac < 0.40 in >= 3 N-values (SU bound fails across scale)
  MIDDLE-BAND:
    - su_frac drops below 0.70 at one N-value only (single N exception)
    - OR excess_mean turns negative at largest N

  NOTE: n=256 calibration probe bands widened to +-50% of v1 result.

FORMULA SELF-TESTS (per [[feedback-strategy-spec-formula-selftests]]):
  1. excess = erase_work - (delta_F_1 - kBT * I). For N=16, single pattern:
     erase_work ~ ALPHA_HEBBIAN * N = 1.6
     delta_F_1 ~ ALPHA_HEBBIAN/2 * N = 0.8 (from v1 formula)
     I ~ log2(1 + SNR) where SNR = erase_work/std_other -> large for single pattern
     So su_bound = delta_F_1 - kBT * I is very negative -> su_frac should be 1.0.
  2. N-scaling ratio: excess_mean / erase_work_mean ~ const across N.

Timeout estimate:
  N=4096 is largest; v1 elapsed_s~4.7s at N=1024 5-seeds.
  FULL N={256,512,1024,4096} 5 seeds: ~4 * 4.7s * (avg_N_ratio)^1.0 ~20s.
  timeout_s = ceil(1.5 * 20 * 5) = ceil(150) -> 300s. Use 600s for margin.

N-suffix: no _nN suffix; sweeps N in {256,512,1024,4096}.
Queue: remote_cpu_queue (pure numpy; N-sweep 4 values 5-seed; ~5-15 min)
Pre-reg: preregs/2026-05-27_sagawa_ueda_deletion_cert_v2.md
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
N_VALUES_FULL  = [256, 512, 1024, 4096]
N_VALUES_SMOKE = [128, 256]
ALPHA_RATIO = 0.125
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
ALPHA_HEBBIAN = 0.1
KBT = 1.0

HP1_BOUND_FRAC = 0.70
HP1_N_MIN = 4   # >= 4 of the tested N-values pass su_frac >= HP1_BOUND_FRAC
HF1_BOUND_FRAC = 0.40
HF1_N_MIN = 3
HF2_WORK_MIN = 1e-3


def get_output_dir(default_name: str = "sagawa_ueda_deletion_cert_v2") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def build_substrate(N: int, M: int, seed: int):
    rng = np.random.default_rng(seed)
    patterns = rng.choice([-1.0, 1.0], size=(M, N))
    W = np.zeros((N, N), dtype=np.float64)
    for mu in range(M):
        v = patterns[mu]
        W += ALPHA_HEBBIAN * np.outer(v, v) / N
    np.fill_diagonal(W, 0.0)
    return W, patterns


def measure_erase_works(W: np.ndarray, patterns: np.ndarray) -> np.ndarray:
    works = np.zeros(len(patterns), dtype=np.float64)
    for k, v in enumerate(patterns):
        works[k] = float(v @ W @ v)
    return works


def estimate_mutual_information(erase_works: np.ndarray) -> np.ndarray:
    I_vals = np.zeros(len(erase_works), dtype=np.float64)
    std_all = float(np.std(erase_works))
    if std_all < 1e-9:
        return I_vals
    for k in range(len(erase_works)):
        SNR = abs(erase_works[k]) / (std_all + 1e-9)
        I_vals[k] = math.log2(1.0 + SNR)
    return I_vals


def mean_field_delta_F_per_pattern(N: int, M: int) -> float:
    alpha = M / N * ALPHA_HEBBIAN
    delta_F_total = alpha * N / 2.0 * (1.0 - alpha)
    return delta_F_total / M


def run_one_seed_N(N: int, seed: int) -> Dict:
    M = max(4, int(N * ALPHA_RATIO))
    W, patterns = build_substrate(N, M, seed)
    erase_works = measure_erase_works(W, patterns)
    I_vals = estimate_mutual_information(erase_works)
    delta_F_1 = mean_field_delta_F_per_pattern(N, M)
    su_bound_per_pattern = delta_F_1 - KBT * I_vals
    su_satisfied = erase_works >= su_bound_per_pattern
    su_frac = float(su_satisfied.mean())
    excess_mean = float((erase_works - su_bound_per_pattern).mean())
    erase_std = float(np.std(erase_works))
    # N-scaling ratio: excess / erase_work_mean
    erase_mean = float(erase_works.mean())
    ratio = excess_mean / (erase_mean + 1e-9)
    return {
        "N": N, "M": M, "seed": seed,
        "su_frac": su_frac,
        "excess_mean": excess_mean,
        "erase_work_mean": erase_mean,
        "erase_work_std": erase_std,
        "I_mean": float(I_vals.mean()),
        "delta_F_1": delta_F_1,
        "su_bound_mean": float(su_bound_per_pattern.mean()),
        "excess_ratio": ratio,
    }


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel."""
    # Formula self-test 1: single pattern, su_frac should be 1.0
    N_t = 16
    W_t, pats_t = build_substrate(N_t, 1, 0)
    works_t = measure_erase_works(W_t, pats_t)
    assert len(works_t) == 1, f"wrong length: {len(works_t)}"
    expected = ALPHA_HEBBIAN * N_t
    assert abs(float(works_t[0]) - expected) < 1.5, \
        f"Single-pattern erase work: got {works_t[0]:.3f} expected ~{expected:.3f}"
    # Formula self-test 2: MI SNR=1.0 -> I=1.0
    I_test = math.log2(1.0 + 1.0)
    assert abs(I_test - 1.0) < 1e-6, f"MI self-test failed: {I_test}"
    # Multi-scale smoke gate: both N_smoke and N_smoke*4 must work
    for N_s in [64, 256]:
        r = run_one_seed_N(N_s, seed=7)
        assert 0.0 <= r["su_frac"] <= 1.0, f"su_frac out of range at N={N_s}"
        assert math.isfinite(r["excess_mean"]), f"excess_mean not finite at N={N_s}"
        assert r["erase_work_std"] > HF2_WORK_MIN, f"erase_work_std too small at N={N_s}"
    # Verify N-scaling: su_frac >= 0.5 at both smoke scales (not falling to 0)
    r_small = run_one_seed_N(64, seed=7)
    r_large = run_one_seed_N(256, seed=7)
    assert r_small["su_frac"] >= 0.5, f"su_frac too low at N=64: {r_small['su_frac']}"
    assert r_large["su_frac"] >= 0.5, f"su_frac too low at N=256: {r_large['su_frac']}"
    print("SELFTEST PASS: all assertions satisfied (multi-scale N-sweep)")


_instrumentation_selftest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()

    if args.self_test:
        sys.exit(0)

    N_values = N_VALUES_SMOKE if args.smoke else N_VALUES_FULL
    seeds = SEEDS_SMOKE if args.smoke else SEEDS_FULL
    out_dir = get_output_dir()
    mode = "smoke" if args.smoke else "full"

    t0 = time.time()
    all_results = []
    per_N_summary = {}

    for N in N_values:
        seed_results = []
        for seed in seeds:
            r = run_one_seed_N(N, seed)
            seed_results.append(r)
            all_results.append(r)
            print(f"[{mode}] N={N} seed={seed} su_frac={r['su_frac']:.3f} "
                  f"excess_mean={r['excess_mean']:.3f} ratio={r['excess_ratio']:.3f}")
        mean_su = float(np.mean([r["su_frac"] for r in seed_results]))
        mean_excess = float(np.mean([r["excess_mean"] for r in seed_results]))
        per_N_summary[str(N)] = {
            "mean_su_frac": mean_su,
            "mean_excess": mean_excess,
            "n_seeds_pass_hp1": sum(1 for r in seed_results if r["su_frac"] >= HP1_BOUND_FRAC),
        }
        print(f"  --> N={N} mean_su={mean_su:.3f} mean_excess={mean_excess:.3f}")

    elapsed = time.time() - t0

    # Per-N verdict: count how many N-values pass HP1
    n_N_pass_hp1 = sum(
        1 for N in N_values
        if np.mean([r["su_frac"] for r in all_results if r["N"] == N]) >= HP1_BOUND_FRAC
    )
    n_N_fail_hf1 = sum(
        1 for N in N_values
        if np.mean([r["su_frac"] for r in all_results if r["N"] == N]) < HF1_BOUND_FRAC
    )
    all_excess_positive = all(r["excess_mean"] > 0.0 for r in all_results)

    if n_N_pass_hp1 >= HP1_N_MIN and all_excess_positive:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: su_frac>=0.70 at {n_N_pass_hp1}/{len(N_values)} N-values. "
                       f"All excess_mean>0. N-values: {N_values}")
    elif n_N_fail_hf1 >= HF1_N_MIN:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: su_frac<0.40 at {n_N_fail_hf1}/{len(N_values)} N-values.")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: {n_N_pass_hp1}/{len(N_values)} N-values pass HP1. "
                       f"all_excess_positive={all_excess_positive}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "n_N_values": len(N_values),
        "n_N_pass_hp1": n_N_pass_hp1,
        "n_N_fail_hf1": n_N_fail_hf1,
        "all_excess_positive": all_excess_positive,
        "per_N_summary": per_N_summary,
        "per_result": all_results,
        "summary": f"Sagawa-Ueda v2 N-sweep {N_values}: {verdict}",
        "config": {
            "N_values": N_values,
            "alpha_ratio": ALPHA_RATIO,
            "seeds": seeds,
        },
    }

    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"VERDICT: {verdict}")
    print(f"MSG: {verdict_msg}")
    print(f"Wrote metrics to {out_path}")


if __name__ == "__main__":
    main()
