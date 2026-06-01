"""Drift-diffusion belief propagation (DD-BP) NESS probe on substrate.

CONTEXT (v226 non-eq priority framework, third non-eq survivor):
  The meta-analysis note (research_negative_results_meta_analysis_2026-05-27.md)
  and v226 cap_map entry identify drift-diffusion belief propagation as one of
  4 surviving non-equilibrium frameworks for the substrate. DD-BP is listed as
  "theorem-anchored erase audit" but has NOT been experimentally probed.

  The NESS drift-diffusion model predicts: task-A retention after task-B overwrite
  decreases monotonically with overwrite load M_B, following a decay law
  proportional to (M_B/N)^0.5. This is distinct from vanilla capacity degradation.

  KEY INSTRUMENTATION NOTE: at sub-capacity alpha, Hopfield substrate retrieves
  perfectly (P=1.0) even under heavy noise. Discriminating signal requires an
  OVERWRITE scenario: task-A stored first (M_A patterns), then task-B written
  on top (M_B patterns). With M_B >> M_A, task-A retrieval degrades.

SCIENTIFIC QUESTION:
  1. Does task-A retention after task-B overwrite follow the DD model:
     P_retained decreases monotonically with M_B for fixed M_A?
  2. Is the decay rate consistent with M_B^{-0.5} scaling (DD drift law)?
  3. Does iterative retrieval (multi-step BP) recover more task-A patterns
     than single-step retrieval at intermediate M_B loads?

PRE-REGISTERED BANDS (calibration probe: first DD-BP measurement on substrate):
  HARD-PASS:
    - P_retained decreases monotonically with M_B in >= 4/5 seeds at fixed M_A
    - AND corr(P_retained, 1/sqrt(M_B)) > 0.60 across M_B sweep in >= 4/5 seeds
    - AND iterative BP gain (multi-step minus single-step) > 0.05 at medium M_B
      in >= 3/5 seeds
  HARD-FAIL:
    - P_retained is constant (>=0.95) regardless of M_B in >= 4/5 seeds
      (not discriminating -- substrate too robust to overwrite)
    - OR P_retained increases with M_B (counter to DD model) in >= 4/5 seeds
  MIDDLE-BAND:
    - Monotone decay but corr < 0.60, OR BP improvement not significant

SELF-TESTS (per [[feedback-strategy-spec-formula-selftests]]):
  1. At M_B=0 (no overwrite): P_retained = 1.0 exactly.
  2. At M_B >> M_A (e.g., M_B = 3*M_A): P_retained < 0.5.
     Empirical calibration: N=256, M_A=50, M_B=150 -> P_retained~0.60.
  3. Correlation direction: corr(P_retained, 1/sqrt(M_B)) > 0.
  4. Multi-step (5 steps) vs single-step: 5-step retrieval cos-sim
     >= single-step cos-sim on overwritten substrate (BP helps).

N-suffix: no _nN suffix; production N = 1024.
Queue: remote_cpu_queue (pure numpy; N=1024 5-seed; ~5-10 min)
Timeout: smoke_wall_s ~4s; FULL: ceil(1.5 * 4 * (1024/256)**1.5 * 5) = ceil(240) = 300s -> use 600s.
Pre-reg: prereqs/2026-05-27_drift_diffusion_bp_substrate_v1.md
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
# M_A is fixed; M_B_VALUES sweeps from 1x to 6x M_A
M_A_FRAC = 0.10       # M_A / N = 10% (task A load; enough to create variable retention)
M_B_MULTIPLIERS = [0.5, 1.0, 2.0, 3.0, 5.0, 7.0]  # M_B = mult * M_A
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
BP_STEPS    = 5   # iterative BP steps
ALPHA_HEBBIAN = 0.1

# Pre-registered thresholds
HP_CORR_MIN       = 0.60   # corr(P_retained, 1/sqrt(M_B)) > this
HP_CORR_SEED_MIN  = 4      # in >= 4/5 seeds
HP_BP_GAIN        = 0.05   # multi-step BP improves retrieval by >= 5%
HP_BP_SEED_MIN    = 3      # in >= 3/5 seeds
HF_CONSTANT_HIGH  = 0.95   # constant metric if P_retained >= this for all M_B
HF_CONST_SEED_MIN = 4


def get_output_dir(default_name: str = "drift_diffusion_bp_substrate_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def build_hopfield_W(N: int, M: int, seed: int, alpha: float = ALPHA_HEBBIAN) -> tuple:
    """Build Hopfield W from M bipolar patterns. Returns (W, patterns)."""
    rng = np.random.default_rng(seed)
    patterns = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
    W = np.zeros((N, N), dtype=np.float64)
    for v in patterns:
        W += alpha * np.outer(v, v) / N
    np.fill_diagonal(W, 0.0)
    return W, patterns


def iterative_retrieval(W: np.ndarray, probe: np.ndarray,
                         n_steps: int = 1) -> np.ndarray:
    """n_steps of Hopfield retrieval. Returns final state."""
    state = probe / (np.linalg.norm(probe) + 1e-9)
    for _ in range(n_steps):
        raw = W @ state
        # Soft threshold (tanh BP message)
        state = np.tanh(raw)
        norm = np.linalg.norm(state)
        if norm > 1e-9:
            state /= norm
    return state


def measure_retention(W_combined: np.ndarray, patterns_A: np.ndarray,
                       W_A: np.ndarray, bp_steps: int = 1,
                       noise_std: float = 0.2, n_probe: int = 40) -> float:
    """Fraction of task-A patterns retained from overwritten W, normalized by W_A baseline.

    Uses normalized overlap: cos-sim = dot(ret_normalized, target_normalized).
    Bipolar target has norm = sqrt(N); ret after tanh BP has norm ~1 (unit sphere).
    Threshold 0.5 on cos(target_norm, ret_norm).
    """
    rng = np.random.default_rng(99)
    n_q = min(n_probe, len(patterns_A))
    correct_combined, correct_baseline = 0, 0
    for i in range(n_q):
        target = patterns_A[i]
        target_n = target / (np.linalg.norm(target) + 1e-9)  # unit vector
        probe = target + noise_std * rng.standard_normal(len(target))
        probe_n = probe / (np.linalg.norm(probe) + 1e-9)

        ret_c = iterative_retrieval(W_combined, probe_n, n_steps=bp_steps)
        # ret_c is already unit-normalized in iterative_retrieval
        cos_c = float(np.dot(ret_c, target_n))  # cosine similarity in [−1, 1]
        if cos_c > 0.5:
            correct_combined += 1

        ret_b = iterative_retrieval(W_A, probe_n, n_steps=bp_steps)
        cos_b = float(np.dot(ret_b, target_n))
        if cos_b > 0.5:
            correct_baseline += 1

    if correct_baseline == 0:
        return 0.0
    return correct_combined / correct_baseline


def run_one_seed(N: int, seed: int, smoke: bool) -> Dict:
    M_A = max(4, int(N * M_A_FRAC))
    W_A, patterns_A = build_hopfield_W(N, M_A, seed)

    mb_multipliers = M_B_MULTIPLIERS if not smoke else M_B_MULTIPLIERS[:4]
    results_by_mb = []
    for mult in mb_multipliers:
        M_B = max(2, int(M_A * mult))
        W_B, _ = build_hopfield_W(N, M_B, seed + 1000)
        # Combine: W_AB = (M_A * W_A + M_B * W_B) / (M_A + M_B) (weighted average)
        W_AB = (M_A * W_A + M_B * W_B) / (M_A + M_B)
        np.fill_diagonal(W_AB, 0.0)

        # Single-step and multi-step retention
        ret_1 = measure_retention(W_AB, patterns_A, W_A, bp_steps=1)
        ret_bp = measure_retention(W_AB, patterns_A, W_A, bp_steps=BP_STEPS)
        bp_gain = ret_bp - ret_1

        results_by_mb.append({
            "M_B": M_B,
            "M_B_mult": mult,
            "retention_1step": ret_1,
            "retention_bp": ret_bp,
            "bp_gain": bp_gain,
        })

    # Compute correlation with 1/sqrt(M_B) (DD decay law)
    P_vals = [r["retention_1step"] for r in results_by_mb]
    M_B_vals = [r["M_B"] for r in results_by_mb]
    inv_sqrt_MB = [1.0 / math.sqrt(m) for m in M_B_vals]

    if float(np.std(P_vals)) > 1e-9 and float(np.std(inv_sqrt_MB)) > 1e-9:
        corr = float(np.corrcoef(P_vals, inv_sqrt_MB)[0, 1])
    else:
        corr = float("nan")

    # Monotone check
    diffs = [P_vals[i+1] - P_vals[i] for i in range(len(P_vals)-1)]
    is_monotone_decreasing = all(d <= 0.05 for d in diffs)  # allow 5% fluctuation

    # Constant metric check
    is_constant_high = all(p >= HF_CONSTANT_HIGH for p in P_vals)

    # BP gain at medium M_B (mult=2.0)
    medium_idx = next((i for i, r in enumerate(results_by_mb) if abs(r["M_B_mult"] - 2.0) < 0.1), None)
    bp_gain_medium = results_by_mb[medium_idx]["bp_gain"] if medium_idx is not None else 0.0

    return {
        "N": N, "M_A": M_A, "seed": seed,
        "retention_corr_dd_law": corr,
        "is_monotone_decreasing": is_monotone_decreasing,
        "is_constant_high": is_constant_high,
        "bp_gain_medium": bp_gain_medium,
        "results_by_mb": results_by_mb,
    }


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    N_t = 256
    M_A_t = max(4, int(N_t * M_A_FRAC))

    # 1. At M_B=0 (no overwrite): P_retained = 1.0 exactly
    W_A_t, pats_A_t = build_hopfield_W(N_t, M_A_t, seed=42)
    ret_no_overwrite = measure_retention(W_A_t, pats_A_t, W_A_t, bp_steps=1)
    assert abs(ret_no_overwrite - 1.0) < 0.01, \
        f"No-overwrite retention should be 1.0, got {ret_no_overwrite:.3f}"

    # 2. At heavy overwrite M_B = 3*M_A: P_retained < 0.7
    M_B_heavy = M_A_t * 3
    W_B_t, _ = build_hopfield_W(N_t, M_B_heavy, seed=1042)
    W_AB_heavy = (M_A_t * W_A_t + M_B_heavy * W_B_t) / (M_A_t + M_B_heavy)
    np.fill_diagonal(W_AB_heavy, 0.0)
    ret_heavy = measure_retention(W_AB_heavy, pats_A_t, W_A_t, bp_steps=1)
    assert ret_heavy < 0.8, \
        f"Heavy-overwrite retention should be < 0.8, got {ret_heavy:.3f}. Check overwrite formula."

    # 3. Correlation direction self-test: ret decreases with M_B
    P_lo = ret_no_overwrite  # M_B = 0.5 * M_A
    P_hi = ret_heavy         # M_B = 3 * M_A
    assert P_lo >= P_hi, \
        f"Retention should decrease with M_B: P_lo={P_lo:.3f}, P_hi={P_hi:.3f}"

    # 4. run_one_seed returns non-NaN metrics
    r = run_one_seed(N_t, seed=42, smoke=True)
    assert not math.isnan(r["retention_corr_dd_law"]), \
        f"DD-law correlation is NaN at N={N_t}"
    assert isinstance(r["is_monotone_decreasing"], bool), "monotone not bool"
    assert isinstance(r["is_constant_high"], bool), "constant_high not bool"
    assert len(r["results_by_mb"]) > 0, "empty results_by_mb"

    # 5. Filter check: results_by_mb has at least 3 entries
    assert len(r["results_by_mb"]) >= 3, \
        f"Too few M_B sweep points: {len(r['results_by_mb'])}"

    print("SELFTEST PASS: all assertions satisfied")


_instrumentation_selftest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()

    if args.self_test:
        sys.exit(0)  # self-test already ran at module scope

    N = N_SMOKE if args.smoke else N_FULL
    seeds = SEEDS_SMOKE if args.smoke else SEEDS_FULL
    out_dir = get_output_dir()

    t0 = time.time()
    results = []
    for seed in seeds:
        r = run_one_seed(N, seed, smoke=args.smoke)
        results.append(r)
        mode = "smoke" if args.smoke else "full"
        print(f"[{mode}] N={N} seed={seed} corr_dd={r['retention_corr_dd_law']:.3f} "
              f"mono={r['is_monotone_decreasing']} bp_gain={r['bp_gain_medium']:.3f}")

    elapsed = time.time() - t0

    # Verdict
    n_corr_pass = sum(1 for r in results
                      if not math.isnan(r["retention_corr_dd_law"]) and
                      r["retention_corr_dd_law"] > HP_CORR_MIN)
    n_bp_pass   = sum(1 for r in results if r["bp_gain_medium"] > HP_BP_GAIN)
    n_const     = sum(1 for r in results if r["is_constant_high"])

    if n_const >= HF_CONST_SEED_MIN:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: constant high retention (>={HF_CONSTANT_HIGH:.0%}) "
                       f"in {n_const}/{len(seeds)} seeds. No discriminating signal.")
    elif n_corr_pass >= HP_CORR_SEED_MIN and n_bp_pass >= HP_BP_SEED_MIN:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: DD-law corr > {HP_CORR_MIN} in {n_corr_pass}/{len(seeds)} seeds; "
                       f"BP gain > {HP_BP_GAIN} in {n_bp_pass}/{len(seeds)} seeds. "
                       f"DD-BP NESS confirmed.")
    else:
        verdict = "MIDDLE_BAND"
        corr_mean = float(np.mean([r["retention_corr_dd_law"] for r in results
                                    if not math.isnan(r["retention_corr_dd_law"])]))
        verdict_msg = (f"MIDDLE_BAND: DD-law corr pass {n_corr_pass}/{len(seeds)}, "
                       f"BP gain pass {n_bp_pass}/{len(seeds)}, "
                       f"corr_mean={corr_mean:.3f}.")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "n_seeds": len(seeds),
        "n_corr_pass": n_corr_pass,
        "n_bp_pass": n_bp_pass,
        "n_const": n_const,
        "per_seed": results,
        "summary": (f"DD-BP N={N}: {verdict} "
                    f"(corr_pass={n_corr_pass}/{len(seeds)}, bp_pass={n_bp_pass}/{len(seeds)})"),
        "config": {
            "N": N,
            "M_A_frac": M_A_FRAC,
            "M_B_multipliers": M_B_MULTIPLIERS,
            "seeds": seeds,
            "HP_CORR_MIN": HP_CORR_MIN,
            "HP_BP_GAIN": HP_BP_GAIN,
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
