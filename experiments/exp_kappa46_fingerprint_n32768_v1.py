"""
kappa46_fingerprint_n32768_v1 -- Wave 5 Anchor 2: kappa_4/6 fingerprint + delta-alpha sensitivity sweep at N=32768.

SCIENTIFIC QUESTION:
  (A) Extend the 1D kappa_3 spectral fingerprint to 3D (kappa_3, kappa_4, kappa_6)
      at production N=32768. Higher cumulants converge only at large N (N=8192 has
      insufficient sample for reliable kappa_6); cloud-N required.
  (B) ADD-2 (amendment 2026-06-02): delta-alpha sensitivity sweep. Does kappa_3
      discriminate substrate perturbations at delta-alpha = {0.0001, 0.001, 0.01,
      0.04, 0.1} with sigma_sep above the 3-sigma detection threshold?
      v324 kappa_3@N=8192 result was sigma_sep=150-1112 (37x-278x predicted
      4-sigma margin); validating extrapolation to N=32768 is the strongest
      sensitivity datum from this batch.

  Theory: kappa_n = alpha (free-Poisson identity for W = Xi^T Xi / N).
  Hutchinson estimator (vectorized): kappa_n = mean((V0 * (W^n @ V0)).sum(0)) / N.

PRE-REGISTERED BANDS:
  (Part A: kappa_4/6 fingerprint)
    HARD-PASS: kappa_4 and kappa_6 each within 5% of alpha.
    MIDDLE: one of {kappa_4, kappa_6} within 10%; other within 20%.
    HARD-FAIL: either >50% off OR sign disagreement.

  (Part B: delta-alpha sensitivity sweep)
    HARD-PASS (all three must hold):
      sigma_sep >= 100 at delta-alpha = 0.04
      sigma_sep >= 10  at delta-alpha = 0.01
      sigma_sep >= 3.0 at delta-alpha = 0.001
    HARD-FAIL (any):
      sigma_sep < 50  at delta-alpha = 0.04 (violates N^(-2/3) scaling)
      sigma_sep < 3.0 at delta-alpha = 0.01
    MIDDLE: sigma_sep at 0.001 in [1.5, 3.0] (detectable but marginal).

OVERALL VERDICT: HARD-PASS if BOTH Part A and Part B HARD-PASS;
  HARD-FAIL if either Part HARD-FAILs; MIDDLE otherwise.

PROT-018: anchor has _n32768 -> N must = 32768.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

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

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "kappa46_fingerprint_n32768_v1"

# PROT-018: anchor has _n32768 -> N must = 32768
_N_SUFFIX = 32768
N_FULL = 32768
N_SMOKE = 4096

ALPHA_GRID = [0.05]  # single alpha at production N (cloud cost discipline)
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]
N_PROBES = 1000  # Hutchinson probes for Part A (kappa_4/6)

# ADD-2 sensitivity sweep config
DELTA_ALPHA_GRID = [0.0001, 0.001, 0.01, 0.04, 0.1]
N_PROBES_SENS = 5000  # heavier probe budget for sensitivity (per amendment)

HP_REL_BAND = 0.05      # Part A: within 5% of alpha
MID_REL_BAND = 0.20     # within 20%
HF_REL_BAND = 0.50      # >50% off = HARD_FAIL

# Part B (sensitivity) thresholds
HP_SIG_SEP_004 = 100.0  # >= 100 at delta-alpha = 0.04
HP_SIG_SEP_001 = 10.0   # >= 10  at delta-alpha = 0.01
HP_SIG_SEP_0001 = 3.0   # >= 3.0 at delta-alpha = 0.001
HF_SIG_SEP_004 = 50.0   # < 50  at delta-alpha = 0.04 -> FAIL
HF_SIG_SEP_001 = 3.0    # < 3.0 at delta-alpha = 0.01 -> FAIL


def hutchinson_kappa_n(W: np.ndarray, n: int, n_probes: int, rng: np.random.Generator) -> float:
    """Vectorized Hutchinson estimator for kappa_n = Tr(W^n) / N.

    Builds Rademacher V (N x n_probes), applies W repeatedly: V <- W @ V.
    After n applications, kappa_n = mean(diag(V_orig^T @ V_after)) / N.
    """
    N = W.shape[0]
    V0 = rng.choice([-1.0, 1.0], size=(N, n_probes)).astype(W.dtype)
    Vk = V0.copy()
    for _ in range(n):
        Vk = W @ Vk
    # diag(V0^T @ Vk) = element-wise (V0 * Vk).sum(axis=0)
    diag = (V0 * Vk).sum(axis=0)
    return float(np.mean(diag)) / float(N)


def kappa3_sensitivity_sweep(N: int, alpha_base: float, delta_alphas: List[float],
                              n_probes: int, rng: np.random.Generator) -> Dict:
    """ADD-2: Build baseline + perturbed substrates; measure kappa_3 sigma_sep.

    For each delta_alpha:
      - Build perturbed Pats at (alpha_base + delta_alpha)
      - Estimate kappa_3 with the SHARED probe set V0 (reused across all delta_alpha
        levels per amendment cost-discipline)
      - per-probe kappa_3 = (1/N) * (V0 * (W^3 @ V0)).sum(axis=0) [length n_probes]
      - kappa_3 mean = mean(per_probe)
      - kappa_3 std_estimator = std(per_probe) / sqrt(n_probes) (standard error)
      - sigma_sep = |kappa_3(perturbed) - kappa_3(base)| / kappa_3_std_estimator

    Probe-set reuse keeps cost minimal (one Hutchinson buffer for all 5 levels).
    """
    # Shared probe set
    V0 = rng.choice([-1.0, 1.0], size=(N, n_probes)).astype(np.float32)
    # Build base substrate at alpha_base
    M_base = max(1, int(alpha_base * N))
    Pats_base = rng.choice([-1.0, 1.0], size=(M_base, N)).astype(np.float32)
    def kappa3_per_probe(Pats):
        # W @ V = (1/N) Pats^T (Pats @ V); apply 3x
        V1 = (Pats.T @ (Pats @ V0)) / N
        V2 = (Pats.T @ (Pats @ V1)) / N
        V3 = (Pats.T @ (Pats @ V2)) / N
        return (V0.astype(np.float64) * V3.astype(np.float64)).sum(axis=0) / N
    k3_base_per = kappa3_per_probe(Pats_base)
    k3_base_mean = float(np.mean(k3_base_per))
    k3_base_se = float(np.std(k3_base_per, ddof=1)) / math.sqrt(n_probes)

    results = {}
    for da in delta_alphas:
        alpha_pert = alpha_base + da
        M_pert = max(1, int(alpha_pert * N))
        # Add only the EXTRA patterns to keep the existing M_base patterns shared
        # (the alpha-perturbation = adding M_pert - M_base patterns to the same
        # substrate; closer to the audit-tamper detection use case).
        n_extra = M_pert - M_base
        if n_extra > 0:
            Extras = rng.choice([-1.0, 1.0], size=(n_extra, N)).astype(np.float32)
            Pats_pert = np.vstack([Pats_base, Extras])
        else:
            Pats_pert = Pats_base
        k3_pert_per = kappa3_per_probe(Pats_pert)
        k3_pert_mean = float(np.mean(k3_pert_per))
        k3_pert_se = float(np.std(k3_pert_per, ddof=1)) / math.sqrt(n_probes)
        # Use pooled SE (conservative)
        pooled_se = math.sqrt(k3_base_se ** 2 + k3_pert_se ** 2)
        delta = k3_pert_mean - k3_base_mean
        sigma_sep = abs(delta) / max(pooled_se, 1e-30)
        results[f"delta_alpha_{da}"] = {
            "delta_alpha": da,
            "k3_base": k3_base_mean,
            "k3_pert": k3_pert_mean,
            "delta": delta,
            "pooled_se": pooled_se,
            "sigma_sep": sigma_sep,
        }
    return {
        "alpha_base": alpha_base,
        "n_probes_sens": n_probes,
        "per_delta_alpha": results,
    }


def _instrumentation_selftest():
    """Identity self-test: for W=I, kappa_n = 1.0 for all n."""
    rng = np.random.default_rng(0)
    N_t = 128
    W_id = np.eye(N_t, dtype=float)
    for n in [3, 4, 6]:
        k_est = hutchinson_kappa_n(W_id, n, 200, rng)
        assert abs(k_est - 1.0) < 0.1, f"kappa_{n}(I) selftest: got {k_est} expected ~1.0"
    print(f"[selftest] PASS: identity-W kappa_n estimates near 1.0", flush=True)


_instrumentation_selftest()


def _prot018_startup_check(n_actual: int) -> None:
    N_BOUND = 32768
    if n_actual != N_BOUND:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor name '{ANCHOR_NAME}' binds to "
            f"N={N_BOUND} but script is running at N={n_actual}. "
            f"Check HDLAB_RUN_MODE env var (must be 'full' for production run).")


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "full")
    seeds = SEEDS_FULL if run_mode == "full" else SEEDS_SMOKE
    N = N_FULL if run_mode == "full" else N_SMOKE
    if run_mode == "full":
        _prot018_startup_check(N)
    print(f"[{ANCHOR_NAME}] run_mode={run_mode} seeds={seeds} N={N} "
          f"alpha_grid={ALPHA_GRID} n_probes={N_PROBES}", flush=True)

    per_seed_results: List[Dict] = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        for alpha in ALPHA_GRID:
            M = max(1, int(alpha * N))
            print(f"  seed={seed} alpha={alpha} M={M}: building W...", flush=True)
            t_cell = time.time()
            Pats = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
            # W = (1/N) Pats^T Pats; rank-M; use Gram trick to avoid N x N materialization
            # W @ v = (1/N) Pats^T (Pats @ v)
            class WOp:
                def __init__(self, P, N):
                    self.P = P
                    self.N = N
                def __matmul__(self, V):
                    return (self.P.T @ (self.P @ V)) / self.N
            W_op = WOp(Pats, N)
            row_result = {"seed": seed, "alpha": alpha, "M": M}
            for n in [3, 4, 6]:
                # Adapted hutchinson with operator (not dense W)
                V0 = rng.choice([-1.0, 1.0], size=(N, N_PROBES)).astype(np.float32)
                Vk = V0.copy()
                for _ in range(n):
                    Vk = W_op @ Vk
                diag = (V0.astype(np.float64) * Vk.astype(np.float64)).sum(axis=0)
                kappa_n = float(np.mean(diag)) / float(N)
                row_result[f"kappa_{n}"] = kappa_n
                row_result[f"kappa_{n}_rel_dev"] = abs(kappa_n - alpha) / alpha
            elapsed_cell = time.time() - t_cell
            row_result["elapsed_s"] = elapsed_cell
            print(f"    kappa_3={row_result['kappa_3']:.5f} "
                  f"kappa_4={row_result['kappa_4']:.5f} "
                  f"kappa_6={row_result['kappa_6']:.5f} "
                  f"(target alpha={alpha}; {elapsed_cell:.1f}s)", flush=True)
            per_seed_results.append(row_result)

    # Aggregate: mean rel dev for kappa_4 and kappa_6 across seeds at primary alpha
    primary_alpha = ALPHA_GRID[0]
    k4_devs = [r["kappa_4_rel_dev"] for r in per_seed_results if r["alpha"] == primary_alpha]
    k6_devs = [r["kappa_6_rel_dev"] for r in per_seed_results if r["alpha"] == primary_alpha]
    k4_mean_dev = float(np.mean(k4_devs))
    k6_mean_dev = float(np.mean(k6_devs))

    k4_hp = k4_mean_dev < HP_REL_BAND
    k6_hp = k6_mean_dev < HP_REL_BAND
    k4_hf = k4_mean_dev > HF_REL_BAND
    k6_hf = k6_mean_dev > HF_REL_BAND

    # Part A verdict (kappa_4/6 fingerprint)
    if k4_hp and k6_hp:
        part_a_verdict = "HARD_PASS"
    elif k4_hf or k6_hf:
        part_a_verdict = "HARD_FAIL"
    else:
        part_a_verdict = "MIDDLE_BAND"

    # ADD-2: Part B sensitivity sweep (single seed sufficient per amendment;
    # reuse probe set across delta-alpha)
    sens_rng = np.random.default_rng(seeds[0] + 9999)
    print(f"  Part B: delta-alpha sensitivity sweep (alpha_base={ALPHA_GRID[0]}, "
          f"delta_alphas={DELTA_ALPHA_GRID}, n_probes_sens={N_PROBES_SENS})...",
          flush=True)
    t_sens = time.time()
    sens_results = kappa3_sensitivity_sweep(
        N, ALPHA_GRID[0], DELTA_ALPHA_GRID, N_PROBES_SENS, sens_rng,
    )
    sens_elapsed = time.time() - t_sens
    print(f"    sensitivity sweep wall: {sens_elapsed:.1f}s", flush=True)
    for k, r in sens_results["per_delta_alpha"].items():
        print(f"    delta_alpha={r['delta_alpha']:>7g}: delta_k3={r['delta']:.6e} "
              f"se={r['pooled_se']:.3e} sigma_sep={r['sigma_sep']:.1f}", flush=True)

    # Part B verdict
    sd = sens_results["per_delta_alpha"]
    sig_004 = sd["delta_alpha_0.04"]["sigma_sep"]
    sig_001 = sd["delta_alpha_0.01"]["sigma_sep"]
    sig_0001 = sd["delta_alpha_0.001"]["sigma_sep"]
    part_b_hp = (sig_004 >= HP_SIG_SEP_004 and sig_001 >= HP_SIG_SEP_001
                 and sig_0001 >= HP_SIG_SEP_0001)
    part_b_hf = (sig_004 < HF_SIG_SEP_004 or sig_001 < HF_SIG_SEP_001)
    if part_b_hp:
        part_b_verdict = "HARD_PASS"
    elif part_b_hf:
        part_b_verdict = "HARD_FAIL"
    else:
        part_b_verdict = "MIDDLE_BAND"

    # Overall verdict: both parts must HARD-PASS for HARD-PASS;
    # any HARD-FAIL -> HARD-FAIL; else MIDDLE
    if part_a_verdict == "HARD_PASS" and part_b_verdict == "HARD_PASS":
        verdict = "HARD_PASS"
    elif part_a_verdict == "HARD_FAIL" or part_b_verdict == "HARD_FAIL":
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "anchor": ANCHOR_NAME, "run_mode": run_mode,
        "N": N, "alpha_grid": ALPHA_GRID, "n_seeds": len(seeds),
        "n_probes": N_PROBES,
        "per_seed_results": per_seed_results,
        "kappa_4_mean_rel_dev": k4_mean_dev,
        "kappa_6_mean_rel_dev": k6_mean_dev,
        "kappa_4_hp": k4_hp, "kappa_6_hp": k6_hp,
        "part_a_verdict": part_a_verdict,
        "sens_sweep": sens_results,
        "sens_elapsed_s": sens_elapsed,
        "part_b_verdict": part_b_verdict,
        "verdict": verdict,
        "elapsed_s": elapsed,
        "verdict_msg": (
            f"kappa_4 + kappa_6 fingerprint at N={N}: "
            f"kappa_4 mean rel_dev = {k4_mean_dev:.4f} ({'HP' if k4_hp else ('HF' if k4_hf else 'MID')}); "
            f"kappa_6 mean rel_dev = {k6_mean_dev:.4f} ({'HP' if k6_hp else ('HF' if k6_hf else 'MID')}). "
            f"Verdict: {verdict}."
        ),
    }
    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict} elapsed={elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    main()
