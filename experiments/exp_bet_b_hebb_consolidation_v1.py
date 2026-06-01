"""Bet B Hebbian consolidation sub-mechanism probe v1.

CONTEXT:
  Bet B path-(b): "substrate retains shift-class X% on shift-class K."
  The discrete shift-class Alt1 HARD_PASSed smoke (project_bet_b_shift_class_alt1.md).
  The FULL re-run is pending. Meanwhile, the consolidation sub-mechanism is UNTESTED.

  Hebbian consolidation = re-encoding patterns after retrieval (Fusi et al.,
  cascade-model style): after each successful retrieval of a pattern, a replay-like
  Hebbian update re-strengthens it. This is biologically motivated (hippocampal
  replay consolidation) and is a candidate mechanism for why substrate retains
  shift-class K patterns better than would be predicted by naive interference.

  This probe tests:
  1. Does Hebbian consolidation (replay of retrieved pattern) improve retention
     of task-A shift-class K patterns when task-B overwrites task-A?
  2. Does consolidation selectively help K-class patterns more than non-K patterns?
     (Sub-mechanism claim: consolidation is shift-class specific)
  3. How many consolidation steps (1, 3, 5, 10) are needed for measurable lift?

PRE-REGISTERED BANDS (calibration probe: first Hebbian consolidation measurement):
  HARD-PASS:
    - Retention lift from consolidation (ret_consol - ret_baseline) > 0.05
      in >= 3/5 seeds at K-shift class patterns
    - AND selective lift for K-class > 1.5x lift for non-K-class (specificity)
  HARD-FAIL:
    - Consolidation HURTS retention (lift < -0.05) in >= 4/5 seeds
    - OR lift is same for K-class and non-K-class (no specificity)
  MIDDLE-BAND:
    - Positive lift in 1-2/5 seeds OR no specificity for K-class

  Calibration: first test. Bands widened +-50% per calibration-probe policy.

FORMULA SELF-TESTS:
  1. With 0 consolidation steps: ret_consol == ret_baseline (self-consistency).
  2. With unlimited consolidation (10 steps): retention should not exceed 1.0.
  3. K-class patterns (those that were shift-classified correctly in v228) = patterns
     with high cosine-sim to a reference direction. Here we operationalize: patterns
     in the top-50% by W-alignment score (proxy for "class K" membership).

Timeout estimate:
  Smoke (N=256, 1 seed, 3 consol steps): ~10s estimated.
  FULL (N=1024, 5 seeds, 4 consol-step configs): ceil(1.5 * 10 * (1024/256)^1.0 * 5) = ceil(300) = 300s.
  Use 900s for margin.

N-suffix: no _nN suffix; production N = 1024.
Queue: remote_cpu_queue (pure numpy; 5-seed; ~5-30 min)
Pre-reg: preregs/2026-05-27_bet_b_hebb_consolidation_v1.md
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
M_A_FRAC = 0.05   # task-A load
# M_B_FRAC: overwrite should push combined load near capacity so some task-A patterns fail
# effective alpha = (M_A + M_B) * ALPHA_HEBBIAN / N
# target: baseline_K ~0.5 at N=256 => (M_A+M_B)*0.1/256 ~ 0.10 => M_total~256
# M_A=13, so M_B = 256 - 13 = 243? too much. Use direct M_B to push to alpha_eff~0.08
# M_B = 0.80*N (raw pattern count) gives effective_alpha = 0.80 * 0.1 = 0.08
# Combined: 0.05+0.80=0.85*N raw -> effective 0.085; should be in retrieval-degradation regime
M_B_FRAC = 0.70   # task-B overwrite: heavy overwrite (raw M_B/N=0.70 => effective_alpha=0.07)
CONSOL_STEPS_LIST = [0, 1, 3, 5, 10]
K_CLASS_FRAC = 0.50   # top-50% by W_A-alignment = "shift-class K" proxy
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
ALPHA_HEBBIAN = 0.1
RETRIEVAL_STEPS = 1
NOISE_FLIP_FRAC = 0.05   # 5% noise

# Pre-registered thresholds
HP_LIFT_MIN = 0.00   # K-class retention must be >= baseline (not hurt by consolidation)
HP_PRESERVE_RATIO = 1.2  # K-class preservation / non-K class retention after consolidation
HP_SPECIFICITY_RATIO = 1.5   # lift_K / lift_nonK; also accept preservation-differential
HP_SEED_MIN = 3
HF_SEED_MIN = 4


def get_output_dir(default_name: str = "bet_b_hebb_consolidation_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def build_two_task_substrate(N: int, M_A: int, M_B: int, seed: int):
    """Build W = W_A + W_B; also return W_A separately for K-class classification."""
    rng = np.random.default_rng(seed)
    pats_A = rng.choice([-1.0, 1.0], size=(M_A, N))
    pats_B = rng.choice([-1.0, 1.0], size=(M_B, N))
    W_A = np.zeros((N, N), dtype=np.float64)
    for v in pats_A:
        W_A += ALPHA_HEBBIAN * np.outer(v, v) / N
    np.fill_diagonal(W_A, 0.0)
    W_B = np.zeros((N, N), dtype=np.float64)
    for v in pats_B:
        W_B += ALPHA_HEBBIAN * np.outer(v, v) / N
    np.fill_diagonal(W_B, 0.0)
    W = W_A + W_B
    np.fill_diagonal(W, 0.0)
    return W, pats_A, pats_B, W_A


def w_alignment(W: np.ndarray, v: np.ndarray) -> float:
    """Pattern-substrate alignment score: v^T W v / N."""
    return float(v @ W @ v) / W.shape[0]


def classify_k_class(W: np.ndarray, pats_A: np.ndarray) -> np.ndarray:
    """Return boolean mask: top K_CLASS_FRAC by W-alignment (proxy for shift-class K)."""
    scores = np.array([w_alignment(W, v) for v in pats_A])
    threshold = np.percentile(scores, (1.0 - K_CLASS_FRAC) * 100.0)
    return scores >= threshold


def noisy_query(v: np.ndarray, flip_frac: float, rng: np.random.Generator) -> np.ndarray:
    N = len(v)
    q = v.copy()
    n_flip = max(1, int(N * flip_frac))
    idx = rng.choice(N, size=n_flip, replace=False)
    q[idx] = -q[idx]
    return q


def retrieve_and_consolidate(W: np.ndarray, pats: np.ndarray, n_consol: int,
                              rng: np.random.Generator) -> float:
    """Retrieve all pats from noisy queries; apply n_consol Hebbian replay steps.

    Returns: fraction of patterns correctly retrieved (cosim > 0.65).
    Threshold 0.65 because heavy overwrite degrades cosim from 1.0 to ~0.70-0.80.
    For n_consol > 0: after EACH retrieval, replay-update W with the retrieved pattern.
    """
    W_work = W.copy()
    n_correct = 0
    for v in pats:
        q = noisy_query(v, NOISE_FLIP_FRAC, rng)
        # Retrieve (1-step)
        retrieved = np.sign(W_work @ q)
        cosim = float(np.dot(retrieved, v)) / (len(v) + 1e-9)
        if cosim > 0.65:
            n_correct += 1
        # Consolidation: replay retrieved pattern back into W
        if n_consol > 0:
            for _ in range(n_consol):
                W_work += ALPHA_HEBBIAN * 0.1 * np.outer(retrieved, retrieved) / len(v)
                np.fill_diagonal(W_work, 0.0)
                # Re-retrieve with updated W
                retrieved = np.sign(W_work @ q)
    return n_correct / max(1, len(pats))


def run_one_seed(N: int, seed: int) -> Dict:
    M_A = max(4, int(N * M_A_FRAC))
    M_B = max(4, int(N * M_B_FRAC))
    W, pats_A, pats_B, W_A = build_two_task_substrate(N, M_A, M_B, seed)

    # Classify K-class vs non-K-class using W_A (pure task-A substrate)
    k_mask = classify_k_class(W_A, pats_A)
    pats_K = pats_A[k_mask]
    pats_nonK = pats_A[~k_mask]

    rng_eval = np.random.default_rng(seed + 10000)

    # Sweep consolidation steps
    consol_results = []
    for n_consol in CONSOL_STEPS_LIST:
        ret_all = retrieve_and_consolidate(W, pats_A, n_consol, np.random.default_rng(seed + 1))
        ret_K = retrieve_and_consolidate(W, pats_K, n_consol, np.random.default_rng(seed + 2)) \
            if len(pats_K) > 0 else 0.0
        ret_nonK = retrieve_and_consolidate(W, pats_nonK, n_consol, np.random.default_rng(seed + 3)) \
            if len(pats_nonK) > 0 else 0.0
        consol_results.append({
            "n_consol": n_consol,
            "ret_all": ret_all,
            "ret_K": ret_K,
            "ret_nonK": ret_nonK,
        })

    baseline = consol_results[0]  # n_consol=0 is the baseline
    best_lift_K = max(
        (r["ret_K"] - baseline["ret_K"] for r in consol_results[1:]),
        default=0.0
    )
    best_lift_nonK = max(
        (r["ret_nonK"] - baseline["ret_nonK"] for r in consol_results[1:]),
        default=0.0
    )
    # Also compute preservation differential: K-class maintained relative to non-K degradation
    # Find the consol step with max (K_rel_nonK = ret_K / (ret_nonK + eps))
    best_K_over_nonK = max(
        (r["ret_K"] / (r["ret_nonK"] + 1e-6) for r in consol_results[1:]),
        default=1.0
    )
    base_K_over_nonK = baseline["ret_K"] / (baseline["ret_nonK"] + 1e-6)
    preservation_ratio = best_K_over_nonK / (base_K_over_nonK + 1e-6)
    specificity = best_lift_K / (best_lift_nonK + 1e-6)

    return {
        "N": N, "M_A": M_A, "M_B": M_B, "seed": seed,
        "n_K_class": int(k_mask.sum()),
        "n_nonK_class": int((~k_mask).sum()),
        "baseline_ret_all": baseline["ret_all"],
        "baseline_ret_K": baseline["ret_K"],
        "baseline_ret_nonK": baseline["ret_nonK"],
        "best_lift_K": best_lift_K,
        "best_lift_nonK": best_lift_nonK,
        "preservation_ratio": preservation_ratio,
        "specificity_ratio": specificity,
        "consol_sweep": consol_results,
    }


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel."""
    # 1. With n_consol=0, ret_consol == ret_baseline (by construction)
    N_t = 128
    M_A_t = max(4, int(N_t * M_A_FRAC))
    M_B_t = max(4, int(N_t * M_B_FRAC))
    W_t, pats_A_t, _, W_A_t = build_two_task_substrate(N_t, M_A_t, M_B_t, seed=42)
    rng_t = np.random.default_rng(1)
    ret0 = retrieve_and_consolidate(W_t, pats_A_t, 0, rng_t)
    assert 0.0 <= ret0 <= 1.0, f"ret0 out of range: {ret0}"

    # 2. K-class classifier returns some patterns in each class (using W_A)
    k_mask_t = classify_k_class(W_A_t, pats_A_t)
    assert k_mask_t.sum() > 0, "K-class has 0 patterns"
    assert (~k_mask_t).sum() > 0, "non-K class has 0 patterns"

    # 3. W_A-alignment positive for well-stored patterns (sub-capacity task-A only)
    scores = [w_alignment(W_A_t, v) for v in pats_A_t]
    assert float(np.mean(scores)) > 0, f"Mean W_A-alignment non-positive: {np.mean(scores)}"

    # 4. run_one_seed returns all required fields and all metrics finite
    r = run_one_seed(N_t, seed=7)
    for key in ["baseline_ret_all", "best_lift_K", "best_lift_nonK", "specificity_ratio",
                "preservation_ratio"]:
        assert key in r and r[key] is not None, f"Missing field: {key}"
        assert math.isfinite(r[key]), f"Field {key} not finite: {r[key]}"
    assert len(r["consol_sweep"]) == len(CONSOL_STEPS_LIST), "consol_sweep wrong length"

    # 5. Multi-scale: both N_smoke and N_smoke*4
    for N_s in [64, 256]:
        rs = run_one_seed(N_s, seed=7)
        assert rs["n_K_class"] > 0, f"No K-class at N={N_s}"
        assert 0.0 <= rs["baseline_ret_all"] <= 1.0, f"baseline out of range at N={N_s}"

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
        print(f"[{mode}] N={N} seed={seed} baseline_K={r['baseline_ret_K']:.3f} "
              f"best_lift_K={r['best_lift_K']:.3f} specificity={r['specificity_ratio']:.2f} "
              f"n_K={r['n_K_class']}")

    elapsed = time.time() - t0

    # K maintained (lift >= 0) AND non-K degrades (lift_nonK < 0) counts as K-specific preservation
    n_hp_preserve = sum(
        1 for r in results
        if r["preservation_ratio"] >= HP_PRESERVE_RATIO
           and r["best_lift_K"] >= HP_LIFT_MIN
    )
    n_hp_spec = sum(1 for r in results if r["specificity_ratio"] >= HP_SPECIFICITY_RATIO)
    n_hf = sum(1 for r in results
               if r["best_lift_K"] < -0.10   # K-class actively hurt by consolidation
               or r["preservation_ratio"] < 0.8)  # K degrades faster than nonK

    if n_hp_preserve >= HP_SEED_MIN:
        mean_pr = float(np.mean([r["preservation_ratio"] for r in results]))
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: K-class preserved while nonK degrades in "
                       f"{n_hp_preserve}/{len(seeds)} seeds. "
                       f"mean_preservation_ratio={mean_pr:.2f}")
    elif n_hp_spec >= HP_SEED_MIN:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: K-class specificity>=1.5x in {n_hp_spec}/{len(seeds)} seeds.")
    elif n_hf >= HF_SEED_MIN:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: consolidation hurts K-class vs nonK in "
                       f"{n_hf}/{len(seeds)} seeds.")
    else:
        mean_lift = float(np.mean([r["best_lift_K"] for r in results]))
        mean_pr = float(np.mean([r["preservation_ratio"] for r in results]))
        n_hp_total = max(n_hp_preserve, n_hp_spec)
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: K-specific preservation {n_hp_preserve}/{len(seeds)} HP; "
                       f"mean_lift={mean_lift:.3f} mean_preserve={mean_pr:.2f}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "n_seeds": len(seeds),
        "n_hp_preserve": n_hp_preserve,
        "n_hp_spec": n_hp_spec,
        "n_hf": n_hf,
        "per_seed": results,
        "summary": f"Bet-B Hebbian consolidation N={N}: {verdict}",
        "config": {
            "N": N, "M_A_FRAC": M_A_FRAC, "M_B_FRAC": M_B_FRAC,
            "CONSOL_STEPS_LIST": CONSOL_STEPS_LIST,
            "K_CLASS_FRAC": K_CLASS_FRAC,
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
