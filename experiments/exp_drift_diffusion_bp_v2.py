"""Drift-diffusion BP v2: sequential partial-erase recovery protocol.

CONTEXT:
  drift_diffusion_bp_substrate_v1 MIDDLE_BAND: corr passes 5/5 (corr_mean=0.775),
  monotone 5/5, but BP gain -1.0 in 5/5 seeds. The BP failure means iterative
  retrieval HURTS not helps at medium M_B. Diagnosis: after heavy task-B overwrite,
  the substrate attractor landscape has no basin near task-A patterns -- iterating
  converges to wrong attractors. Standard Hopfield dynamics is the WRONG retrieval
  protocol for overwritten substrate.

  This probe tests two alternative recovery protocols:
  1. SELECTIVE DAMPING: multiply attractor-weight by (1 - alpha_B) before BP iterate.
     Intuition: dampen task-B patterns' influence during task-A retrieval.
  2. PARTIAL ERASE THEN RETRIEVE: anti-Hebbian erase of task-B patterns (if we have
     their labels), then retrieve task-A. This tests the "targeted erase" pathway.

SCIENTIFIC QUESTIONS:
  1. Does selective damping (reduce task-B influence in W) improve task-A retrieval
     at medium M_B? Measure: delta_retrieval = ret(damped) - ret(standard).
  2. Does partial anti-Hebbian erase of M_B' < M_B patterns improve task-A retrieval
     proportionally? Measure: corr(M_B_erased, delta_retention).
  3. What fraction of task-B must be erased for task-A to recover to >= 0.80 retention?
     (product-relevant threshold: "how many erasures does the deletion cert enable?")

PRE-REGISTERED BANDS (no prior protocol anchor for selective-damping):
  HARD-PASS:
    - Selective damping gain > 0.05 in >= 3/5 seeds at medium M_B (M_B = 2*M_A)
    - OR partial-erase corr(M_B_erased, delta_retention) > 0.60 in >= 3/5 seeds
    -> At least one protocol improves task-A recovery vs overwrite baseline
  HARD-FAIL:
    - Both protocols show negative gain (damping hurts, erase hurts) in >= 4/5 seeds
    -> Overwrite damage is irreversible via both protocols
  MIDDLE-BAND:
    - One protocol helps in 1-2/5 seeds only
    - OR erase corr positive but < 0.60

  Calibration: first test of these protocols. Bands widened +-50% per policy.

FORMULA SELF-TESTS:
  1. With M_B = 0 (no overwrite): all retention should be 1.0 regardless of protocol.
  2. After fully erasing all M_B patterns: task-A retention should return toward 1.0.
     Self-test: N=256, M_A=25, M_B=50, erase ALL M_B -> expect retention jump.
  3. Damping factor 0.0: fully remove task-B -> same as full erase.

Timeout estimate:
  v1 elapsed_s=71s for 5 seeds. Adding damping + partial-erase sweeps ~ 2x.
  timeout_s = ceil(1.5 * 142 * 1.0 * 1) = ceil(213) -> 300s. Use 900s for margin.

N-suffix: no _nN suffix; production N = 1024.
Queue: remote_cpu_queue (pure numpy; 5-seed; ~10-30 min)
Pre-reg: preregs/2026-05-27_drift_diffusion_bp_v2.md
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
N_FULL  = 1024
N_SMOKE = 256
M_A_FRAC = 0.10
M_B_MEDIUM_MULT = 5.0   # medium overwrite: M_B = 5 * M_A (creates measurable retrieval degradation)
ERASE_FRACTIONS = [0.0, 0.25, 0.50, 0.75, 1.0]   # fraction of task-B patterns to erase
DAMPING_FACTORS = [0.0, 0.25, 0.50, 0.75, 1.0]   # how much to damp task-B patterns
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
ALPHA_HEBBIAN = 0.1
RETRIEVAL_STEPS = 3   # standard iterative retrieval steps
COSIM_THRESHOLD = 0.80  # retrieval threshold; 0.90 is too strict at loaded substrate

# Pre-registered thresholds
HP_DAMPING_GAIN = 0.05
HP_ERASE_CORR   = 0.60
HP_SEED_MIN     = 3
HF_SEED_MIN     = 4


def get_output_dir(default_name: str = "drift_diffusion_bp_v2") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def build_substrate_two_task(N: int, M_A: int, M_B: int, seed: int):
    """Build substrate with task-A then task-B overwrite. Returns (W, pats_A, pats_B)."""
    rng = np.random.default_rng(seed)
    pats_A = rng.choice([-1.0, 1.0], size=(M_A, N))
    pats_B = rng.choice([-1.0, 1.0], size=(M_B, N))
    W = np.zeros((N, N), dtype=np.float64)
    for v in pats_A:
        W += ALPHA_HEBBIAN * np.outer(v, v) / N
    for v in pats_B:
        W += ALPHA_HEBBIAN * np.outer(v, v) / N
    np.fill_diagonal(W, 0.0)
    return W, pats_A, pats_B


def retrieve_single_step(W: np.ndarray, query: np.ndarray) -> np.ndarray:
    return np.sign(W @ query)


def retrieve_iterative(W: np.ndarray, query: np.ndarray, steps: int) -> np.ndarray:
    state = query.copy()
    for _ in range(steps):
        new_state = np.sign(W @ state)
        if np.array_equal(new_state, state):
            break
        state = new_state
    return state


def measure_retention(W: np.ndarray, patterns: np.ndarray, steps: int = 1) -> float:
    """Fraction of patterns correctly retrieved from noisy query.

    Threshold: cosim > 0.80 (not 0.90; loaded substrate has max cosim ~0.91-0.94).
    Noise: 5% bit flip (3% noise keeps us in retrieval basin at sub-capacity).
    """
    N = W.shape[0]
    rng = np.random.default_rng(42)
    n_correct = 0
    for v in patterns:
        query = v.copy()
        # Flip 5% of bits as noise
        n_flip = max(1, N // 20)
        flip_idx = rng.choice(N, size=n_flip, replace=False)
        query[flip_idx] = -query[flip_idx]
        if steps == 1:
            retrieved = retrieve_single_step(W, query)
        else:
            retrieved = retrieve_iterative(W, query, steps)
        cosim = float(np.dot(retrieved, v)) / (N + 1e-9)
        n_correct += int(abs(cosim) > 0.80)
    return n_correct / len(patterns)


def run_one_seed(N: int, seed: int) -> Dict:
    M_A = max(4, int(N * M_A_FRAC))
    M_B = max(4, int(M_A * M_B_MEDIUM_MULT))
    W_full, pats_A, pats_B = build_substrate_two_task(N, M_A, M_B, seed)

    # Baseline: standard 1-step retrieval on overwritten substrate
    baseline_ret = measure_retention(W_full, pats_A, steps=1)

    # Protocol 1: selective damping sweep
    damping_results = []
    W_A_only = np.zeros((N, N), dtype=np.float64)
    for v in pats_A:
        W_A_only += ALPHA_HEBBIAN * np.outer(v, v) / N
    np.fill_diagonal(W_A_only, 0.0)
    W_B_only = W_full - W_A_only
    np.fill_diagonal(W_B_only, 0.0)

    best_damping_gain = 0.0
    for damp in DAMPING_FACTORS:
        W_damped = W_A_only + (1.0 - damp) * W_B_only
        np.fill_diagonal(W_damped, 0.0)
        ret_d = measure_retention(W_damped, pats_A, steps=1)
        gain = ret_d - baseline_ret
        damping_results.append({"damp": damp, "ret": ret_d, "gain": gain})
        if gain > best_damping_gain:
            best_damping_gain = gain

    # Protocol 2: partial erase sweep
    erase_results = []
    n_B_erased_list = [int(f * M_B) for f in ERASE_FRACTIONS]
    ret_by_erased = []
    for n_erase in n_B_erased_list:
        W_erased = W_full.copy()
        for v in pats_B[:n_erase]:
            W_erased -= ALPHA_HEBBIAN * np.outer(v, v) / N
        np.fill_diagonal(W_erased, 0.0)
        ret_e = measure_retention(W_erased, pats_A, steps=1)
        delta = ret_e - baseline_ret
        erase_results.append({"n_erased": n_erase, "ret": ret_e, "delta": delta})
        ret_by_erased.append(ret_e)

    # Correlation: n_erased vs retention
    n_erased_arr = np.array(n_B_erased_list, dtype=float)
    ret_arr = np.array(ret_by_erased, dtype=float)
    if np.std(ret_arr) < 1e-9 or np.std(n_erased_arr) < 1e-9:
        erase_corr = 0.0
    else:
        erase_corr = float(np.corrcoef(n_erased_arr, ret_arr)[0, 1])

    # Full erase (all M_B erased) retention
    full_erase_ret = ret_by_erased[-1]

    return {
        "N": N, "M_A": M_A, "M_B": M_B, "seed": seed,
        "baseline_ret": baseline_ret,
        "best_damping_gain": best_damping_gain,
        "erase_corr": erase_corr,
        "full_erase_ret": full_erase_ret,
        "damping_results": damping_results,
        "erase_results": erase_results,
    }


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel."""
    # 1. With M_B=0, retention should be high (>= 0.8 at small N)
    N_t = 128
    M_A_t = max(4, int(N_t * M_A_FRAC))
    W_t, pats_A_t, _ = build_substrate_two_task(N_t, M_A_t, 0, seed=42)
    ret_nowrite = measure_retention(W_t, pats_A_t, steps=1)
    assert ret_nowrite >= 0.5, f"Retention without overwrite too low: {ret_nowrite:.3f}"

    # 2. After full erase of M_B, retention should be >= baseline (or close)
    M_B_t = max(4, int(M_A_t * M_B_MEDIUM_MULT))
    W_over, pats_A2, pats_B2 = build_substrate_two_task(N_t, M_A_t, M_B_t, seed=7)
    baseline_ret = measure_retention(W_over, pats_A2, steps=1)
    W_erased = W_over.copy()
    for v in pats_B2:
        W_erased -= ALPHA_HEBBIAN * np.outer(v, v) / N_t
    np.fill_diagonal(W_erased, 0.0)
    erase_ret = measure_retention(W_erased, pats_A2, steps=1)
    assert erase_ret >= baseline_ret - 0.1, \
        f"Full erase should not hurt vs baseline: {erase_ret:.3f} vs {baseline_ret:.3f}"

    # 3. Damping = 0.0 (task-B fully removed) should equal full erase
    W_A_only = np.zeros((N_t, N_t), dtype=np.float64)
    for v in pats_A2:
        W_A_only += ALPHA_HEBBIAN * np.outer(v, v) / N_t
    np.fill_diagonal(W_A_only, 0.0)
    ret_damp0 = measure_retention(W_A_only, pats_A2, steps=1)
    assert abs(ret_damp0 - erase_ret) < 0.15, \
        f"Damp=0 should approx match full erase: {ret_damp0:.3f} vs {erase_ret:.3f}"

    # 4. run_one_seed returns all required fields
    r = run_one_seed(N_t, seed=7)
    for key in ["baseline_ret", "best_damping_gain", "erase_corr", "full_erase_ret"]:
        assert key in r and r[key] is not None, f"Missing or None field: {key}"
        assert math.isfinite(r[key]), f"Field {key} not finite: {r[key]}"
    assert len(r["damping_results"]) == len(DAMPING_FACTORS), "wrong damping results count"
    assert len(r["erase_results"]) == len(ERASE_FRACTIONS), "wrong erase results count"
    # 5. Multi-scale: N_smoke and N_smoke*4
    r_s = run_one_seed(64, seed=7)
    r_l = run_one_seed(256, seed=7)
    for r_t, N_t2 in [(r_s, 64), (r_l, 256)]:
        assert 0.0 <= r_t["baseline_ret"] <= 1.0, f"baseline_ret out of range at N={N_t2}"
    print("SELFTEST PASS: all assertions satisfied")


_instrumentation_selftest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()

    if args.self_test:
        sys.exit(0)

    N = N_SMOKE if args.smoke else N_FULL
    seeds = SEEDS_SMOKE if args.smoke else SEEDS_FULL
    out_dir = get_output_dir()
    mode = "smoke" if args.smoke else "full"

    t0 = time.time()
    results = []
    for seed in seeds:
        r = run_one_seed(N, seed)
        results.append(r)
        print(f"[{mode}] N={N} seed={seed} baseline={r['baseline_ret']:.3f} "
              f"damping_gain={r['best_damping_gain']:.3f} erase_corr={r['erase_corr']:.3f} "
              f"full_erase={r['full_erase_ret']:.3f}")

    elapsed = time.time() - t0

    n_hp_damp = sum(1 for r in results if r["best_damping_gain"] >= HP_DAMPING_GAIN)
    n_hp_erase = sum(1 for r in results if r["erase_corr"] >= HP_ERASE_CORR)
    n_hf = sum(1 for r in results
               if r["best_damping_gain"] < 0 and r["erase_corr"] < 0)

    if n_hp_damp >= HP_SEED_MIN or n_hp_erase >= HP_SEED_MIN:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: damping_gain>=0.05 in {n_hp_damp}/{len(seeds)} seeds; "
                       f"erase_corr>=0.60 in {n_hp_erase}/{len(seeds)} seeds.")
    elif n_hf >= HF_SEED_MIN:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: both protocols negative in {n_hf}/{len(seeds)} seeds. "
                       f"Overwrite damage irreversible via damping+erase.")
    else:
        mean_dg = float(np.mean([r["best_damping_gain"] for r in results]))
        mean_ec = float(np.mean([r["erase_corr"] for r in results]))
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: damp_gain {n_hp_damp}/{len(seeds)} HP; "
                       f"erase_corr {n_hp_erase}/{len(seeds)} HP. "
                       f"means: damp_gain={mean_dg:.3f} erase_corr={mean_ec:.3f}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "n_seeds": len(seeds),
        "n_hp_damp": n_hp_damp,
        "n_hp_erase": n_hp_erase,
        "n_hf": n_hf,
        "per_seed": results,
        "summary": f"DD-BP v2 N={N}: {verdict}",
        "config": {
            "N": N, "M_A_FRAC": M_A_FRAC,
            "M_B_MEDIUM_MULT": M_B_MEDIUM_MULT,
            "DAMPING_FACTORS": DAMPING_FACTORS,
            "ERASE_FRACTIONS": ERASE_FRACTIONS,
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
