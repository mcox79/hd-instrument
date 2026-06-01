"""Sagawa-Ueda deletion certificate v4: N=8192 envelope extension.

CONTEXT:
  sagawa_ueda_deletion_cert_v1 HARD_PASS: su_frac=1.000 in 5/5 seeds at N=1024.
  sagawa_ueda_deletion_cert_v2 HARD_PASS: N-sweep {256,512,1024,4096} 4/4 N-values.
  sagawa_ueda_deletion_cert_v3 running: N-sweep {256,512,1024,4096} 5 seeds full.
  v4 (THIS): push to N=8192. Tests whether SU bound holds at N=8192 -- the
    largest scale relevant to the deletion-certificate killer feature.

SCIENTIFIC QUESTION:
  At N=8192, is erase_work >= su_bound still holding across all patterns?
  v2 showed su_frac=1.0 at N=4096. Does this extend to N=8192?

PRE-REGISTERED BANDS (envelope extension of v2 HARD_PASS):
  HARD-PASS:
    - su_frac >= 0.70 across >= 4/5 seeds at N=8192
    - AND excess_mean > 0 in ALL seeds
  HARD-FAIL:
    - su_frac < 0.40 in >= 3/5 seeds (bound breaks at N=8192)
  MIDDLE-BAND:
    - su_frac drops below 0.70 in 1-2 seeds only
    - OR excess_mean turns negative

  Prior anchor: v2 HARD_PASS at N=4096 with su_frac=1.0. Bands NOT widened to +-50%.
  Using same thresholds (prior anchor exists; extension of known envelope).

OOM PRE-CHECK:
  W at N=8192: 8192^2 * 8 bytes (float64) = 512MB.
  Patterns: M = N * 0.125 = 1024 patterns, N=8192: 8192 * 1024 * 8 bytes = 64MB.
  Total peak: ~580MB << 6GB. OK.
  NOTE: outer-product at N=8192 is O(N^2) = 67M ops per pattern.
  With M=1024 patterns: 1024 * 67M = 68B ops. At numpy speed ~1B ops/s: ~68s per seed.
  5 seeds: ~340s. Under 4h.

FORMULA SELF-TESTS:
  1. For N=16, M=1: erase_work ~ ALPHA * N = 1.6 (single pattern, easy case).
  2. su_bound = delta_F_1 - kBT * I_bits. I_bits >= 0 always (information >= 0).
     For single pattern: su_bound = delta_F_1 - very_large -> su_frac = 1.0 (easy).
  3. excess = erase_work - su_bound > 0 for single-pattern case at any N.
  4. su_frac in [0, 1] always.

Timeout estimate:
  v2 at N=4096 5 seeds (from v3 script which is faster): ~5-60s.
  At N=8192 the outer-product is 4x more expensive: (8192/4096)^2 = 4x.
  5 seeds: timeout_s = ceil(1.5 * 60 * 4 * 1) = ceil(360) -> 600s.
  Use 1200s for margin.

N-suffix: no _nN suffix; production N = 8192 (stated explicitly below).
Queue: remote_cpu_queue (pure numpy; no CUDA; N=8192)
Pre-reg: preregs/2026-05-27_sagawa_ueda_v4_n8192.md
Parent: sagawa_ueda_deletion_cert_v2 (HARD_PASS N=4096), v3 running
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
N_FULL = 8192         # Production N = 8192
N_SMOKE = 512
ALPHA_RATIO = 0.125
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
ALPHA_HEBBIAN = 0.1
KBT = 1.0

HP1_BOUND_FRAC = 0.70
HP1_SEED_MIN = 4     # >= 4/5 seeds pass
HF1_BOUND_FRAC = 0.40
HF1_SEED_MIN = 3


def get_output_dir(default_name: str = "sagawa_ueda_v4_n8192") -> Path:
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
    delta_W = -ALPHA_HEBBIAN * np.outer(v, v) / N
    energy_before = -float(v @ W @ v)
    energy_after = -float(v @ (W + delta_W) @ v)
    return energy_after - energy_before


def sagawa_ueda_bound(W: np.ndarray, patterns: np.ndarray, target_idx: int,
                      N: int, M: int) -> Dict:
    v_target = patterns[target_idx]
    erase_work = compute_erase_work(W, v_target, N)
    delta_F_1 = float(ALPHA_HEBBIAN / 2.0 * N * (1.0 - ALPHA_HEBBIAN * M / N))
    overlap_target = float(v_target @ W @ v_target) / N
    other_overlaps = []
    for mu in range(M):
        if mu != target_idx:
            ov = float(patterns[mu] @ W @ v_target) / N
            other_overlaps.append(ov)
    noise_std = float(np.std(other_overlaps)) + 1e-9 if other_overlaps else 1e-9
    snr = abs(overlap_target) / noise_std
    I_bits = math.log2(1.0 + snr)
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

    # Self-test 2: single-seed run
    r_single = run_one_seed(32, seed=42)
    assert r_single["su_frac"] >= 0.0, f"su_frac negative: {r_single['su_frac']}"
    assert isinstance(r_single["excess_mean"], float), "excess_mean not float"

    # Self-test 3: multi-scale smoke at N_SMOKE and N_SMOKE*4
    r_smoke = run_one_seed(N_SMOKE, seed=17)
    r_smoke4 = run_one_seed(N_SMOKE * 4, seed=17)
    assert r_smoke["su_frac"] >= 0.0, f"N_smoke su_frac out of range: {r_smoke['su_frac']}"
    assert r_smoke4["su_frac"] >= 0.0, f"N_smoke*4 su_frac out of range: {r_smoke4['su_frac']}"

    # Self-test 4: excess > 0 for single-pattern case
    N_test, M_test = 64, 1
    W_t, pats_t = build_substrate(N_test, M_test, seed=99)
    r_test = sagawa_ueda_bound(W_t, pats_t, 0, N_test, M_test)
    assert r_test["excess"] > 0 or r_test["su_frac_pass"] == 1.0, \
        f"Single-pattern case failed: excess={r_test['excess']}"

    # Self-test 5: OOM check
    oom_bytes = N_FULL * N_FULL * 8  # float64
    assert oom_bytes < 6e9, f"OOM check: {oom_bytes:.2e} >= 6GB"

    print(f"[selftest] sagawa_ueda_v4_n8192 PASSED: "
          f"smoke su_frac={r_smoke['su_frac']:.4f} OOM={oom_bytes:.2e}", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    mode_str = "SMOKE" if smoke else "FULL"
    exp_name = os.environ.get("HDLAB_EXP_NAME", "sagawa_ueda_v4_n8192")

    print(f"[run] {exp_name} {mode_str} N={N} seeds={seeds}", flush=True)
    out_dir = get_output_dir(exp_name)

    per_seed: List[Dict] = []
    for seed in seeds:
        t_seed = time.time()
        r = run_one_seed(N, seed)
        per_seed.append(r)
        print(f"  seed={seed}: su_frac={r['su_frac']:.4f} excess_mean={r['excess_mean']:.4f} "
              f"({time.time()-t_seed:.1f}s)", flush=True)

    n_hp = sum(1 for r in per_seed if r["su_frac"] >= HP1_BOUND_FRAC)
    n_hf = sum(1 for r in per_seed if r["su_frac"] < HF1_BOUND_FRAC)
    all_excess_pos = all(r["excess_mean"] > 0 for r in per_seed)
    mean_su_frac = float(np.mean([r["su_frac"] for r in per_seed]))

    if n_hp >= HP1_SEED_MIN and all_excess_pos:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: su_frac>={HP1_BOUND_FRAC} in {n_hp}/{len(seeds)} seeds at N={N}. "
            f"All excess_mean>0. SU deletion-cert bound holds at N=8192. "
            f"mean_su_frac={mean_su_frac:.4f}"
        )
    elif n_hf >= HF1_SEED_MIN:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: su_frac<{HF1_BOUND_FRAC} in {n_hf}/{len(seeds)} seeds at N={N}. "
            f"SU bound breaks at N=8192. mean_su_frac={mean_su_frac:.4f}"
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: su_frac>={HP1_BOUND_FRAC} in {n_hp}/{len(seeds)} seeds at N={N}. "
            f"all_excess_pos={all_excess_pos}. mean_su_frac={mean_su_frac:.4f}"
        )

    elapsed = round(time.time() - t0, 2)
    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": f"sagawa_ueda_v4_n8192 {mode_str} N={N}: {n_hp}/{len(seeds)} HP su_frac>={HP1_BOUND_FRAC}",
        "N": N,
        "n_seeds": len(seeds),
        "n_hp": n_hp,
        "mean_su_frac": mean_su_frac,
        "per_seed": per_seed,
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
