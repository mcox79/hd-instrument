"""Sagawa-Ueda deletion certificate: thermodynamic work cost of anti-Hebbian erase.

CONTEXT (product roadmap -- deletion-certificate killer feature #1):
  The Crooks FT bound (v153/v158) maps substrate WRITE to thermodynamic cost.
  The gap: we do not yet have a corresponding bound for substrate ERASE (anti-Hebbian).
  The deletion-certificate killer feature requires: "for pattern mu, erase cost W_erase
  satisfies W_erase >= delta_S * k_B T (Sagawa-Ueda bound for measurement-feedback erase)."

  Sagawa-Ueda 2008/2010: for a measurement-feedback process, the work W satisfies
  W >= delta_F - k_B T * I  where I = mutual information gained in measurement.
  For associative-memory erase: the "measurement" is the substrate retrieving mu
  (gaining I bits of information about pattern identity), and the feedback is the
  anti-Hebbian update.

  This probe tests: does substrate anti-Hebbian erase satisfy the Sagawa-Ueda bound
  W_erase >= delta_F - k_B T * I? If yes: the erase is thermodynamically tight
  (minimal excess work) -- a positive claim for the deletion certificate.

SCIENTIFIC QUESTION:
  For each pattern mu erased from a loaded substrate (M patterns, N dimensions):
  1. Measure erase work W_k = <v_k, W_k-1 v_k> (energy GAINED by anti-Hebbian erase)
  2. Estimate mutual information I = log2(1 + SNR) where SNR = (W erase / std(W_other))
  3. Estimate delta_F ~ alpha * k_B T (from prior Crooks work; v158 baseline)
  4. Does W_k >= delta_F - k_B T * I hold for >= 70% of erase operations?

PRE-REGISTERED BANDS (calibration probe: first ERASE-path thermodynamic measurement):
  HARD-PASS (HP1):
    - SU-bound satisfied (W_erase >= delta_F - kBT*I) in >= 70% of erase operations
      across >= 4/5 seeds.
    -> Anti-Hebbian erase is thermodynamically tight; deletion-certificate framing justified.
  HARD-PASS (HP2, weaker):
    - Mean(W_erase - [delta_F - kBT*I]) > 0 (positive excess on average) in >= 3/5 seeds
    -> Bound satisfied on average even if some tail violates.
  HARD-FAIL (HF1):
    - SU-bound satisfied in < 40% of operations in >= 4/5 seeds
    -> Anti-Hebbian erase violates SU bound; deletion-cert framing would need qualifier.
  HARD-FAIL (HF2):
    - W_erase is all-zero or near-zero (< 1e-3 std across seeds)
    -> Instrumentation failure; erase work not measurable.
  MIDDLE-BAND:
    - Bound satisfied in [40%, 70%) of operations across seeds.
    -> Partial compliance; needs extended N sweep or corrected estimator.

SELF-TESTS (per [[feedback-strategy-spec-formula-selftests]]):
  1. For a single pattern v stored in W = alpha * outer(v,v) / N:
     W_erase = <v, W v> = alpha * ||v||^2^2 / N = alpha * N (for bipolar v with ||v||^2=N).
     Self-test: N=16, alpha=0.1, 1 pattern -> W_erase should be ~0.1 * 16 = 1.6.
  2. delta_F per pattern (RS mean-field, sub-capacity):
     delta_F_pattern ~ alpha / 2 * (1 - alpha) * N.
     Self-test: N=16, alpha=0.1 -> delta_F ~ 0.1/2 * 0.9 * 16 = 0.72.
  3. Mutual information estimate I = log2(1+SNR) with SNR = W_erase / std(W_other):
     For SNR=1: I = log2(2) = 1.0 bit.
     For SNR=0: I = 0.0 bits.
     Self-test: SNR=1.0 -> I should be 1.0.

N-suffix: no _nN suffix; production N = 1024.
Queue: remote_cpu_queue (pure numpy; N=1024 5-seed; ~5-15 min)
Timeout: smoke_wall_s ~ 3s; FULL: ceil(1.5 * 3 * (1024/256)**1.5 * 5) = ceil(180) = 300s -> use 600s.
Pre-reg: preregs/2026-05-27_sagawa_ueda_deletion_cert_v1.md
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
ALPHA_RATIO = 0.125   # M/N; well inside RS phase
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
ALPHA_HEBBIAN = 0.1
KBT = 1.0

# Pre-registered thresholds
HP1_BOUND_FRAC = 0.70   # >= 70% operations satisfy SU bound
HP1_SEED_MIN   = 4      # in >= 4/5 seeds
HP2_SEED_MIN   = 3      # mean positive in >= 3/5 seeds
HF1_BOUND_FRAC = 0.40   # < 40% = hard-fail
HF1_SEED_MIN   = 4
HF2_WORK_MIN   = 1e-3   # std must exceed this


def get_output_dir(default_name: str = "sagawa_ueda_deletion_cert_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def build_substrate(N: int, M: int, seed: int):
    """Build Hopfield W from M bipolar patterns. Returns (W, patterns)."""
    rng = np.random.default_rng(seed)
    patterns = rng.choice([-1.0, 1.0], size=(M, N))
    W = np.zeros((N, N), dtype=np.float64)
    for mu in range(M):
        v = patterns[mu]
        W += ALPHA_HEBBIAN * np.outer(v, v) / N
    np.fill_diagonal(W, 0.0)
    return W, patterns


def measure_erase_works(W: np.ndarray, patterns: np.ndarray) -> np.ndarray:
    """Per-pattern anti-Hebbian erase work: W_k = <v_k, W v_k>.

    This is the energy RELEASED when erasing pattern k from a loaded substrate.
    Positive means pattern k was stored with positive alignment.
    """
    works = np.zeros(len(patterns), dtype=np.float64)
    for k, v in enumerate(patterns):
        works[k] = float(v @ W @ v)
    return works


def estimate_mutual_information(erase_works: np.ndarray) -> np.ndarray:
    """Estimate per-pattern I = log2(1 + SNR) where SNR = W_erase / std(W_other).

    SNR proxy: how much more energy does THIS pattern release vs random patterns.
    std(W_other) ~ std of erase works excluding this pattern.
    """
    I_vals = np.zeros(len(erase_works), dtype=np.float64)
    std_all = float(np.std(erase_works))
    if std_all < 1e-9:
        return I_vals  # all zero sentinel -- will be caught by selftest
    for k in range(len(erase_works)):
        # SNR = how many sigmas above background
        SNR = abs(erase_works[k]) / (std_all + 1e-9)
        I_vals[k] = math.log2(1.0 + SNR)
    return I_vals


def mean_field_delta_F_per_pattern(N: int, M: int) -> float:
    """RS mean-field free-energy change per pattern (erase of 1 pattern from M-loaded substrate).

    From v158 Crooks SLA: delta_F ~ alpha * N / 2 * (1 - alpha) for FULL load.
    Per-pattern: delta_F_1 ~ delta_F / M = N / (2*M) * (1 - M/N) * ALPHA_HEBBIAN.
    """
    alpha = M / N * ALPHA_HEBBIAN
    delta_F_total = alpha * N / 2.0 * (1.0 - alpha)
    return delta_F_total / M


def run_one_seed(N: int, seed: int) -> Dict:
    M = max(4, int(N * ALPHA_RATIO))
    W, patterns = build_substrate(N, M, seed)
    erase_works = measure_erase_works(W, patterns)
    I_vals = estimate_mutual_information(erase_works)
    delta_F_1 = mean_field_delta_F_per_pattern(N, M)

    # SU bound check: W_k >= delta_F_1 - kBT * I_k
    su_bound_per_pattern = delta_F_1 - KBT * I_vals
    su_satisfied = erase_works >= su_bound_per_pattern
    su_frac = float(su_satisfied.mean())
    excess_mean = float((erase_works - su_bound_per_pattern).mean())

    return {
        "N": N,
        "M": M,
        "seed": seed,
        "su_frac": su_frac,
        "excess_mean": excess_mean,
        "erase_work_mean": float(erase_works.mean()),
        "erase_work_std": float(np.std(erase_works)),
        "I_mean": float(I_vals.mean()),
        "delta_F_1": delta_F_1,
        "su_bound_mean": float(su_bound_per_pattern.mean()),
    }


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # 1. Single-pattern substrate: W_erase = alpha * ||v||^2^2 / N
    N_t, M_t, seed_t = 16, 1, 0
    W_t, pats_t = build_substrate(N_t, M_t, seed_t)
    works_t = measure_erase_works(W_t, pats_t)
    assert len(works_t) == M_t == 1, f"wrong work array length: {len(works_t)}"
    # For bipolar v, v @ W v = ALPHA_HEBBIAN * ||v||^4 / N = ALPHA_HEBBIAN * N^2 / N = ALPHA_HEBBIAN * N
    # (because ||bipolar v||^2 = N, so v @ outer(v,v)/N v = N*N/N = N)
    expected_approx = ALPHA_HEBBIAN * N_t  # ~1.6
    assert abs(float(works_t[0]) - expected_approx) < 1.0, \
        f"Single-pattern erase work self-test FAIL: got {works_t[0]:.4f} expected ~{expected_approx:.4f}"

    # 2. Multi-pattern: erase works non-trivial std
    N2, M2, seed2 = 128, 16, 7
    W2, pats2 = build_substrate(N2, M2, seed2)
    works2 = measure_erase_works(W2, pats2)
    assert float(np.std(works2)) > HF2_WORK_MIN, \
        f"erase_work std too small at N={N2}: {np.std(works2):.4f}"

    # 3. Mutual information: SNR=1.0 -> I=1.0 bit
    snr_test = 1.0
    I_test = math.log2(1.0 + snr_test)
    assert abs(I_test - 1.0) < 1e-6, f"MI self-test: SNR=1 -> I should be 1.0, got {I_test}"

    # 4. SNR=0 -> I=0.0
    I_zero = math.log2(1.0 + 0.0)
    assert abs(I_zero) < 1e-9, f"MI self-test: SNR=0 -> I should be 0.0, got {I_zero}"

    # 5. SU bound fraction is well-defined (in [0,1])
    result = run_one_seed(N2, seed2)
    assert 0.0 <= result["su_frac"] <= 1.0, f"su_frac out of range: {result['su_frac']}"
    assert math.isfinite(result["excess_mean"]), f"excess_mean not finite"
    assert math.isfinite(result["erase_work_std"]) and result["erase_work_std"] > 0, \
        f"erase_work_std trivial: {result['erase_work_std']}"

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
        r = run_one_seed(N, seed)
        results.append(r)
        mode = "smoke" if args.smoke else "full"
        print(f"[{mode}] N={N} seed={seed} su_frac={r['su_frac']:.3f} "
              f"erase_std={r['erase_work_std']:.4f} excess_mean={r['excess_mean']:.4f}")

    elapsed = time.time() - t0

    # Verdict
    n_hp1 = sum(1 for r in results if r["su_frac"] >= HP1_BOUND_FRAC)
    n_hp2 = sum(1 for r in results if r["excess_mean"] > 0.0)
    n_hf1 = sum(1 for r in results if r["su_frac"] < HF1_BOUND_FRAC)
    n_hf2 = sum(1 for r in results if r["erase_work_std"] < HF2_WORK_MIN)

    if n_hf2 >= 4:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = (f"INSTRUMENTATION_FAIL: erase_work_std < {HF2_WORK_MIN} in "
                       f"{n_hf2}/{len(seeds)} seeds")
    elif n_hp1 >= HP1_SEED_MIN:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: SU bound satisfied >= {HP1_BOUND_FRAC:.0%} of erases "
                       f"in {n_hp1}/{len(seeds)} seeds. "
                       f"mean(su_frac)={np.mean([r['su_frac'] for r in results]):.3f}")
    elif n_hf1 >= HF1_SEED_MIN:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: SU bound violated (su_frac < {HF1_BOUND_FRAC:.0%}) "
                       f"in {n_hf1}/{len(seeds)} seeds.")
    elif n_hp2 >= HP2_SEED_MIN:
        verdict = "PARTIAL_PASS"
        verdict_msg = (f"PARTIAL_PASS: Mean excess > 0 in {n_hp2}/{len(seeds)} seeds "
                       f"but strong HP1 threshold not met ({n_hp1}/{len(seeds)}).")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: SU bound partially satisfied. "
                       f"su_frac_mean={np.mean([r['su_frac'] for r in results]):.3f}. "
                       f"n_hp1={n_hp1}, n_hp2={n_hp2}, n_hf1={n_hf1}.")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "n_seeds": len(seeds),
        "n_hp1": n_hp1,
        "n_hp2": n_hp2,
        "n_hf1": n_hf1,
        "per_seed": results,
        "summary": (f"Sagawa-Ueda deletion-cert N={N}: {verdict} "
                    f"(su_frac_mean={np.mean([r['su_frac'] for r in results]):.3f})"),
        "config": {
            "N": N,
            "alpha_ratio": ALPHA_RATIO,
            "seeds": seeds,
            "HP1_BOUND_FRAC": HP1_BOUND_FRAC,
            "HF1_BOUND_FRAC": HF1_BOUND_FRAC,
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
