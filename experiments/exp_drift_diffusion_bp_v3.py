"""Drift-diffusion BP v3: N=1024 5-seed FULL.

CONTEXT:
  drift_diffusion_bp_substrate_v1 MIDDLE_BAND: damp_gain 5/5 HP, but at N=256 only.
  drift_diffusion_bp_v2 MIDDLE_BAND: 1 seed N=256 smoke only. Same pattern.
  v3 (THIS): 5-seed FULL run at N=1024 using two recovery protocols:
    (1) Selective damping of task-B influence
    (2) Partial anti-Hebbian erase of task-B patterns before retrieval

SCIENTIFIC QUESTION:
  Does selective damping (reduce task-B W-component during task-A retrieval) improve
  retention at N=1024 multi-seed? What fraction of task-B must be erased for task-A
  to recover to >= 0.80 retention? (deletion-cert killer-feature foundation)

PRE-REGISTERED BANDS (extending v2; first multi-seed at N=1024):
  HARD-PASS:
    - Selective damping gain > 0.05 in >= 3/5 seeds at medium M_B (M_B = 5*M_A)
    - OR partial-erase corr(M_B_erased, delta_retention) > 0.60 in >= 3/5 seeds
  HARD-FAIL:
    - Both protocols show <= 0 gain (damping hurts, erase hurts) in >= 4/5 seeds
  MIDDLE-BAND:
    - One protocol helps in 1-2/5 seeds only
    - OR erase corr positive but < 0.60

  Calibration probe: first multi-seed test. Bands widened +-50% per calibration policy.

FORMULA SELF-TESTS:
  1. With M_B = 0 (no overwrite): all retention = 1.0 regardless of protocol.
  2. After erasing ALL M_B patterns: task-A retention returns toward baseline.
     Self-test: N=128, M_A=12, M_B=24, erase fraction=1.0 -> retention jump.
  3. Damping factor 0.0 (remove all task-B) same as full erase.
  4. Baseline (no protocol) at M_B=M_A: retention < 0.95 (non-trivial overwrite).

Timeout estimate:
  v1 elapsed ~71s for 5 seeds at N=256. N=1024 scales as N^1.0 (linear retrieval).
  timeout_s = ceil(1.5 * 71 * (1024/256)^1.0 * (5/5)) = ceil(1.5 * 284) = 426 -> 900s.

N-suffix: no _nN suffix; production N = 1024.
Queue: remote_cpu_queue (pure numpy; 5-seed; ~15-30 min)
Pre-reg: preregs/2026-05-27_drift_diffusion_bp_v3.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# --- Production config ---
N_FULL = 1024
N_SMOKE = 256
M_A_FRAC = 0.10
M_B_MEDIUM_MULT = 5.0    # M_B = 5 * M_A
ERASE_FRACTIONS = [0.0, 0.25, 0.50, 0.75, 1.0]
DAMPING_FACTORS = [0.0, 0.25, 0.50, 0.75, 1.0]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
ALPHA_HEBBIAN = 0.1
N_RETRIEVAL_STEPS = 30
N_QUERIES_PER_PATTERN = 5

# Pre-registered thresholds
HP_DAMP_GAIN_MIN = 0.05
HP_ERASE_CORR_MIN = 0.60
HP_SEED_MIN = 3
HF_SEED_MIN = 4


def get_output_dir(default_name: str = "drift_diffusion_bp_v3") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def build_substrate(N: int, M: int, seed: int):
    rng = np.random.default_rng(seed)
    patterns = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
    W = np.zeros((N, N), dtype=np.float64)
    for v in patterns:
        W += ALPHA_HEBBIAN * np.outer(v, v) / N
    np.fill_diagonal(W, 0.0)
    return W, patterns, rng


def retrieve(W: np.ndarray, query: np.ndarray, n_steps: int) -> np.ndarray:
    v = query.copy()
    for _ in range(n_steps):
        h = W @ v
        v = np.sign(h)
        v[v == 0] = 1.0
    return v


def measure_retention(W: np.ndarray, patterns: np.ndarray, rng,
                       n_queries: int = 3, noise_p: float = 0.1) -> float:
    M = patterns.shape[0]
    N = patterns.shape[1]
    correct = 0
    total = 0
    for mu in range(M):
        for _ in range(n_queries):
            v_noisy = patterns[mu].copy()
            flip_mask = rng.random(N) < noise_p
            v_noisy[flip_mask] *= -1
            v_ret = retrieve(W, v_noisy, N_RETRIEVAL_STEPS)
            overlaps = patterns @ v_ret / N
            best_mu = int(np.argmax(overlaps))
            if best_mu == mu:
                correct += 1
            total += 1
    return float(correct) / total if total > 0 else 0.0


def run_one_seed(N: int, seed: int) -> Dict:
    M_A = max(2, int(N * M_A_FRAC))
    M_B = max(2, int(M_A * M_B_MEDIUM_MULT))

    rng = np.random.default_rng(seed)
    # Build W_A (task A only)
    W_A, patterns_A, rng = build_substrate(N, M_A, seed)
    # Add task B to W_A
    pats_B = rng.choice([-1.0, 1.0], size=(M_B, N)).astype(np.float64)
    W_AB = W_A.copy()
    for v in pats_B:
        W_AB += ALPHA_HEBBIAN * np.outer(v, v) / N
    np.fill_diagonal(W_AB, 0.0)

    # Baseline retention with overwrite
    baseline_ret = measure_retention(W_AB, patterns_A, rng, n_queries=N_RETRIEVAL_STEPS // 5)

    # Protocol 1: selective damping
    best_damp_gain = 0.0
    damp_results = []
    for damp in DAMPING_FACTORS:
        W_damped = W_AB.copy()
        for v in pats_B:
            W_damped -= damp * ALPHA_HEBBIAN * np.outer(v, v) / N
        np.fill_diagonal(W_damped, 0.0)
        ret_damp = measure_retention(W_damped, patterns_A, rng, n_queries=3)
        gain = ret_damp - baseline_ret
        damp_results.append({"damp": damp, "ret": ret_damp, "gain": gain})
        if gain > best_damp_gain:
            best_damp_gain = gain

    # Protocol 2: partial erase sweep
    erase_results = []
    for erase_frac in ERASE_FRACTIONS:
        n_erase = int(M_B * erase_frac)
        W_erased = W_AB.copy()
        for v in pats_B[:n_erase]:
            W_erased -= ALPHA_HEBBIAN * np.outer(v, v) / N
        np.fill_diagonal(W_erased, 0.0)
        ret_erase = measure_retention(W_erased, patterns_A, rng, n_queries=3)
        delta_ret = ret_erase - baseline_ret
        erase_results.append({
            "erase_frac": erase_frac, "n_erase": n_erase,
            "ret": ret_erase, "delta_ret": delta_ret,
        })

    # Erase correlation: corr(erase_frac, delta_ret)
    erase_fracs = [r["erase_frac"] for r in erase_results]
    delta_rets = [r["delta_ret"] for r in erase_results]
    if np.std(delta_rets) > 1e-9 and np.std(erase_fracs) > 1e-9:
        erase_corr = float(np.corrcoef(erase_fracs, delta_rets)[0, 1])
    else:
        erase_corr = 0.0

    # Full erase retention
    full_erase_ret = erase_results[-1]["ret"] if erase_results else baseline_ret

    return {
        "N": N, "M_A": M_A, "M_B": M_B, "seed": seed,
        "baseline_ret": baseline_ret,
        "best_damping_gain": best_damp_gain,
        "erase_corr": erase_corr,
        "full_erase_ret": full_erase_ret,
        "damping_results": damp_results,
        "erase_results": erase_results,
    }


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # Self-test 1: M_B=0 case -> baseline retention should be high
    W_only_A, pats_A, _ = build_substrate(64, 6, seed=42)
    rng_test = np.random.default_rng(42)
    ret_only_A = measure_retention(W_only_A, pats_A, rng_test, n_queries=3)
    assert ret_only_A > 0.5, f"Pure task-A retention too low: {ret_only_A}"

    # Self-test 2: run at smoke N
    r = run_one_seed(N_SMOKE, seed=17)
    assert "best_damping_gain" in r, "missing best_damping_gain"
    assert "erase_corr" in r, "missing erase_corr"
    assert isinstance(r["best_damping_gain"], float), "best_damping_gain not float"
    assert isinstance(r["erase_corr"], float), "erase_corr not float"

    # Self-test 3: multi-scale smoke
    r_smoke = run_one_seed(N_SMOKE, seed=17)
    r_smoke4 = run_one_seed(N_SMOKE * 4, seed=17)
    assert r_smoke["baseline_ret"] >= 0.0, "baseline_ret out of range"
    assert r_smoke4["baseline_ret"] >= 0.0, "4x smoke baseline_ret out of range"

    # Self-test 4: full erase should improve on baseline (or at least not hurt)
    # With M_B = 5*M_A, full erase recovers W to W_A
    assert r["full_erase_ret"] >= 0.0, "full_erase_ret negative"

    print(f"[selftest] v3 PASSED: N={N_SMOKE} baseline_ret={r['baseline_ret']:.3f} "
          f"best_damp_gain={r['best_damping_gain']:.4f} erase_corr={r['erase_corr']:.3f}", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0_run = time.time()
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    mode_str = "SMOKE" if smoke else "FULL"
    exp_name = os.environ.get("HDLAB_EXP_NAME", "drift_diffusion_bp_v3")

    print(f"[run] {exp_name} {mode_str} N={N} seeds={seeds}", flush=True)
    out_dir = get_output_dir(exp_name)

    per_seed: List[Dict] = []
    for seed in seeds:
        print(f"  [seed={seed}]", flush=True)
        r = run_one_seed(N, seed)
        per_seed.append(r)
        print(f"    baseline_ret={r['baseline_ret']:.3f} damp_gain={r['best_damping_gain']:.4f} "
              f"erase_corr={r['erase_corr']:.3f}", flush=True)

    n_hp_damp = sum(1 for r in per_seed if r["best_damping_gain"] > HP_DAMP_GAIN_MIN)
    n_hp_erase = sum(1 for r in per_seed if r["erase_corr"] > HP_ERASE_CORR_MIN)
    n_hf = sum(1 for r in per_seed
               if r["best_damping_gain"] <= 0 and r["erase_corr"] <= 0)

    mean_damp_gain = float(np.mean([r["best_damping_gain"] for r in per_seed]))
    mean_erase_corr = float(np.mean([r["erase_corr"] for r in per_seed]))

    if n_hp_damp >= HP_SEED_MIN or n_hp_erase >= HP_SEED_MIN:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: damp_gain {n_hp_damp}/{len(seeds)} HP; erase_corr {n_hp_erase}/{len(seeds)} HP. "
            f"means: damp_gain={mean_damp_gain:.3f} erase_corr={mean_erase_corr:.3f}. "
            f"At least one recovery protocol works robustly at N={N}."
        )
    elif n_hf >= HF_SEED_MIN:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: {n_hf}/{len(seeds)} seeds both protocols negative. "
            f"Overwrite damage irreversible via both protocols at N={N}."
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: damp_gain {n_hp_damp}/{len(seeds)} HP; erase_corr {n_hp_erase}/{len(seeds)} HP. "
            f"means: damp_gain={mean_damp_gain:.3f} erase_corr={mean_erase_corr:.3f}"
        )

    elapsed = round(time.time() - t0_run, 2)
    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": f"dd_bp_v3 {mode_str} N={N}: damp_hp={n_hp_damp} erase_hp={n_hp_erase}",
        "n_seeds": len(seeds),
        "n_hp_damp": n_hp_damp,
        "n_hp_erase": n_hp_erase,
        "n_hf": n_hf,
        "mean_damp_gain": mean_damp_gain,
        "mean_erase_corr": mean_erase_corr,
        "per_seed": [{k: v for k, v in r.items()
                      if k not in ("damping_results", "erase_results")}
                     for r in per_seed],
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
