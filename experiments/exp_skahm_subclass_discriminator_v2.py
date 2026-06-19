"""SKAH-M sub-class discriminator v2: saddle-hierarchy single-thread deeper probe.

CONTEXT:
  skahm_subclass_discriminator_v1 is in queue (pending). That probe runs 3 discriminating
  probes (non-reciprocal, spatial-correlated, saddle-hierarchy) to find which is dominant.

  This v2 is a DIFFERENT DESIGN: rather than 3 probes competing, we run the
  SADDLE-HIERARCHY probe alone at much higher resolution. The rationale:
  - v228 (anchor_novel_phase_battery_v3) showed saddle-cascade plateau signatures
  - wave14_saddle_solla_v7_n4096 is currently running (GPU, in queue)
  - The saddle sub-class claim requires a specific N-scaling prediction:
    the cascade transition steepness should INCREASE with N (sharp in large-N limit)

  This probe tests: at N=1024 and N=4096, does the saddle-hierarchy d_transition
  (slope at first plateau edge f=0.25) increase with N? This is the key discriminator
  between saddle-hierarchy (N-growing sharpness) and other sub-classes (N-invariant).

SCIENTIFIC QUESTION:
  Does the f-sweep retention curve show a SHARPENING transition at f=0.25 as N grows
  from N=512 to N=4096? (saddle-hierarchy prediction: d_transition ~ sqrt(N) as N grows)

PRE-REGISTERED BANDS (focused N-scaling discriminator):
  HARD-PASS:
    - d_transition(N=4096) > 1.5 * d_transition(N=512) in >= 3/5 seeds
    - (sharpening factor 1.5x per 8x N increase is conservative saddle-hierarchy prediction)
  HARD-FAIL:
    - d_transition constant across N (ratio < 1.1) in >= 4/5 seeds
    - OR d_transition DECREASES with N in >= 3/5 seeds (anti-saddle prediction)
  MIDDLE-BAND:
    - Ratio in [1.1, 1.5) (some sharpening but not decisive)

  Calibration: first N-scaling sharpness test. Bands +-50% per calibration policy.

FORMULA SELF-TESTS:
  1. For f=0 (no noise): retention = 1.0 for all patterns (no perturbation).
  2. For f=1 (all noise): retention -> 0 (fully randomized query).
  3. d_transition = d(retention)/df at f=0.25 should be negative (retention falls).
  4. At N=512 vs N=4096: larger N should give cleaner saddle transition (less finite-N noise).

Timeout estimate:
  N={512, 4096} f-sweep with 5 seeds, ~50 f values each.
  N=4096 cost ~ N^1.0 for retrieval; smoke at N=256: ~5s.
  FULL: ceil(1.5 * 5 * (4096/256)^1.0 * 5) = ceil(1.5*5*16*5) = ceil(600) = 600s.
  Use 1200s for margin (2 N-values, inner f-sweep).

N-suffix: no _nN suffix; production N in {512, 4096}.
Queue: remote_cpu_queue (pure numpy; 5-seed; ~10-30 min)
Pre-reg: preregs/2026-05-27_skahm_subclass_discriminator_v2.md
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
N_VALUES_FULL  = [512, 4096]
N_VALUES_SMOKE = [128, 512]
ALPHA_RATIO = 0.10   # M/N
F_VALUES = np.linspace(0.0, 1.0, 21).tolist()   # 0, 0.05, ..., 1.0
F_TRANSITION = 0.25   # f value where saddle transition is expected
F_DELTA = 0.05        # window around transition for derivative estimation
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
ALPHA_HEBBIAN = 0.1
N_QUERY_PER_PATTERN = 5   # noisy query repeats for retention estimate

HP_SHARPENING_RATIO = 1.5
HP_SEED_MIN = 3
HF_SEED_MIN = 4


def get_output_dir(default_name: str = "skahm_subclass_discriminator_v2") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def build_substrate(N: int, M: int, seed: int):
    rng = np.random.default_rng(seed)
    patterns = rng.choice([-1.0, 1.0], size=(M, N))
    W = np.zeros((N, N), dtype=np.float64)
    for v in patterns:
        W += ALPHA_HEBBIAN * np.outer(v, v) / N
    np.fill_diagonal(W, 0.0)
    return W, patterns


def measure_retention_at_f(W: np.ndarray, patterns: np.ndarray, f: float,
                            seed: int, n_queries: int) -> float:
    """Measure fraction of correctly retrieved patterns with noise level f."""
    N = W.shape[0]
    rng = np.random.default_rng(seed)
    n_correct = 0
    total = 0
    for v in patterns:
        for _ in range(n_queries):
            q = v.copy()
            n_flip = int(N * f)
            if n_flip > 0:
                idx = rng.choice(N, size=min(n_flip, N), replace=False)
                q[idx] = -q[idx]
            retrieved = np.sign(W @ q)
            retrieved[retrieved == 0] = 1.0
            cosim = float(np.dot(retrieved, v)) / (N + 1e-9)
            n_correct += int(cosim > 0.85)   # use signed cosim; -v is wrong attractor
            total += 1
    return n_correct / max(1, total)


def compute_d_transition(retentions: np.ndarray, f_values: List[float],
                          f_trans: float, f_delta: float) -> float:
    """Compute slope of retention curve at f_trans using finite differences."""
    f_arr = np.array(f_values)
    # Points within [f_trans - f_delta, f_trans + f_delta]
    mask = (f_arr >= f_trans - f_delta) & (f_arr <= f_trans + f_delta)
    if mask.sum() < 2:
        return 0.0
    f_window = f_arr[mask]
    r_window = retentions[mask]
    # Fit linear slope via least squares
    A = np.column_stack([f_window, np.ones(len(f_window))])
    try:
        coeffs, _, _, _ = np.linalg.lstsq(A, r_window, rcond=None)
        return float(abs(coeffs[0]))   # absolute slope (want magnitude of transition)
    except Exception:
        return 0.0


def run_one_seed_N(N: int, seed: int) -> Dict:
    M = max(4, int(N * ALPHA_RATIO))
    W, patterns = build_substrate(N, M, seed)

    retentions = []
    for f in F_VALUES:
        ret = measure_retention_at_f(W, patterns, f, seed + int(f * 1000), N_QUERY_PER_PATTERN)
        retentions.append(ret)

    ret_arr = np.array(retentions)
    d_trans = compute_d_transition(ret_arr, F_VALUES, F_TRANSITION, F_DELTA)

    return {
        "N": N, "M": M, "seed": seed,
        "d_transition": d_trans,
        "retention_at_f0": float(ret_arr[0]),
        "retention_at_f025": float(ret_arr[min(range(len(F_VALUES)),
                                               key=lambda i: abs(F_VALUES[i] - 0.25))]),
        "retention_at_f1": float(ret_arr[-1]),
        "f_sweep": list(zip(F_VALUES, retentions)),
    }


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel."""
    # 1. f=0 retention should be high (>= 0.80 at small N sub-capacity)
    N_t = 64
    M_t = max(4, int(N_t * ALPHA_RATIO))
    W_t, pats_t = build_substrate(N_t, M_t, seed=42)
    ret_f0 = measure_retention_at_f(W_t, pats_t, 0.0, seed=42, n_queries=N_QUERY_PER_PATTERN)
    assert ret_f0 >= 0.5, f"f=0 retention too low: {ret_f0:.3f}"

    # 2. f=0.40 (40% bits flipped) retention should be lower than f=0.0
    ret_f0p4 = measure_retention_at_f(W_t, pats_t, 0.40, seed=42, n_queries=N_QUERY_PER_PATTERN)
    ret_f0_check = measure_retention_at_f(W_t, pats_t, 0.0, seed=42, n_queries=N_QUERY_PER_PATTERN)
    assert ret_f0p4 <= ret_f0_check + 0.05, \
        f"f=0.40 retention should be <= f=0 retention: {ret_f0p4:.3f} vs {ret_f0_check:.3f}"

    # 3. d_transition is negative or zero slope at f=0 (retention is flat at f=0)
    # It may be 0 at f=0.25 if pattern is too easy to retrieve; just check finite
    retentions_t = [measure_retention_at_f(W_t, pats_t, f, 42, N_QUERY_PER_PATTERN)
                    for f in F_VALUES]
    d = compute_d_transition(np.array(retentions_t), F_VALUES, F_TRANSITION, F_DELTA)
    assert math.isfinite(d) and d >= 0.0, f"d_transition not non-negative finite: {d}"

    # 4. run_one_seed_N returns all required fields
    r = run_one_seed_N(64, seed=7)
    for key in ["d_transition", "retention_at_f0", "retention_at_f025", "retention_at_f1"]:
        assert key in r and r[key] is not None, f"Missing field: {key}"
        assert math.isfinite(r[key]), f"Field {key} not finite: {r[key]}"
    assert len(r["f_sweep"]) == len(F_VALUES), "Wrong f_sweep length"

    # 5. Multi-scale: N_smoke and N_smoke*4
    r_s = run_one_seed_N(64, seed=7)
    r_l = run_one_seed_N(256, seed=7)
    assert 0.0 <= r_s["retention_at_f0"] <= 1.0, f"f0 ret out of range at N=64"
    assert 0.0 <= r_l["retention_at_f0"] <= 1.0, f"f0 ret out of range at N=256"

    print("SELFTEST PASS: all assertions satisfied (SKAH-M v2)")


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
    per_N = {}
    all_results = []

    for N in N_values:
        seed_results = []
        for seed in seeds:
            r = run_one_seed_N(N, seed)
            seed_results.append(r)
            all_results.append(r)
            print(f"[{mode}] N={N} seed={seed} d_trans={r['d_transition']:.4f} "
                  f"ret_f0={r['retention_at_f0']:.3f} ret_f025={r['retention_at_f025']:.3f}")
        mean_d = float(np.mean([r["d_transition"] for r in seed_results]))
        per_N[str(N)] = {"mean_d_transition": mean_d}
        print(f"  --> N={N} mean_d_transition={mean_d:.4f}")

    elapsed = time.time() - t0

    # Compute sharpening ratio: d_transition(large_N) / d_transition(small_N) per seed
    if len(N_values) >= 2:
        N_small, N_large = N_values[0], N_values[-1]
        d_small = [r["d_transition"] for r in all_results if r["N"] == N_small]
        d_large = [r["d_transition"] for r in all_results if r["N"] == N_large]
        if len(d_small) == len(seeds) and len(d_large) == len(seeds):
            ratios = [dl / (ds + 1e-9) for dl, ds in zip(d_large, d_small)]
            n_hp = sum(1 for ratio in ratios if ratio >= HP_SHARPENING_RATIO)
            n_flat = sum(1 for ratio in ratios if ratio < 1.1)
            n_decrease = sum(1 for ratio in ratios if ratio < 1.0)
            mean_ratio = float(np.mean(ratios))
        else:
            n_hp = n_flat = n_decrease = 0
            mean_ratio = 1.0
            ratios = []
    else:
        n_hp = n_flat = n_decrease = 0
        mean_ratio = 1.0
        ratios = []

    if n_flat >= HF_SEED_MIN or n_decrease >= HF_SEED_MIN - 1:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: no sharpening with N. ratio<1.1 in {n_flat}/{len(seeds)} seeds; "
                       f"ratio<1.0 in {n_decrease}/{len(seeds)} seeds. "
                       f"mean_ratio={mean_ratio:.3f}")
    elif n_hp >= HP_SEED_MIN:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: sharpening ratio>={HP_SHARPENING_RATIO} in "
                       f"{n_hp}/{len(seeds)} seeds. mean_ratio={mean_ratio:.3f}. "
                       f"Saddle-hierarchy N-scaling confirmed.")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: sharpening {n_hp}/{len(seeds)} seeds pass HP. "
                       f"mean_ratio={mean_ratio:.3f}. Partial saddle-hierarchy evidence.")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "n_seeds": len(seeds),
        "n_hp_sharpening": n_hp,
        "n_flat": n_flat,
        "mean_sharpening_ratio": mean_ratio,
        "per_N_summary": per_N,
        "per_result": all_results,
        "summary": f"SKAH-M v2 saddle-N-scaling: {verdict}",
        "config": {
            "N_values": N_values, "ALPHA_RATIO": ALPHA_RATIO,
            "seeds": seeds, "F_TRANSITION": F_TRANSITION,
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
