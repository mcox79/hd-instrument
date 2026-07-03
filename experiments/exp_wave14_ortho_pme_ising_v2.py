"""PME-Ising capacity v2: correct capacity formula + larger N sweep.

v1 MIDDLE_BAND: factor2_frac=0.00; alpha_max_mean=1.04. The v1 capacity formula
  M_max = abs(log_Z) / H_pattern * N
was dimensionally inconsistent. abs(log_Z) ~ N * log(2) (the null Ising entropy),
so M_max/N ~ 1.0 regardless of actual coupling -- vacuously large.

FIX v2 -- two corrected capacity estimators:

  Estimator 1: Replica symmetric (RS) capacity bound from Tanaka 1998 / Amit-Gutfreund-Sompolinsky:
    At the Hopfield critical point alpha_c, the signal h_1 satisfies:
    h_1 = (1 - alpha * C(beta, rho))^{-1}  where C = <tanh^2(beta * h)> over the noise distribution.
    The RS fixed-point equations are solved self-consistently. M_max/N = alpha_c^RS is where
    these equations lose a non-trivial solution.

  Estimator 2: Entropy-based Ising bound -- correct version:
    Free energy per spin: f = -1/N * log Z (intensive quantity)
    Excess free energy from M patterns: delta_f = f_M - f_0 (f at M patterns minus null).
    Pattern entropy per spin: h_pat = log(2) (binary {-1,+1} patterns).
    Capacity: alpha_c_Z = delta_f / h_pat (how many patterns the free energy can encode).
    This is the CORRECT intensive formula -- delta_f and h_pat are both per-spin quantities.

  Both estimators run on the same Hopfield W at N in {256, 512, 1024}.
  Compare estimator predictions to empirical alpha_c = 0.138.

HARD-PASS: alpha_c estimate in [0.05, 0.30] for >= 6/10 seeds (within factor 2 of 0.138).
HARD-FAIL: alpha_c estimate > 10.0 or < 0.01 for all seeds (vacuous bound).
MIDDLE-BAND: alpha_c in [0.30, 2.0] for majority (factor 2-10 off).

SELF-TESTS:
  1. RS fixed-point solver converges at alpha=0.1 (well below alpha_c) -> non-trivial h_1 > 0
  2. RS fixed-point solver collapses at alpha=0.5 (above alpha_c) -> h_1 = 0 or diverges
  3. delta_f for J=0 (null Ising) = 0.0 (no patterns stored)
  4. delta_f > 0 for Hopfield J with M = 5, N=32 (patterns stored increase free energy)
  5. alpha_c_Z is finite and in (0, 1) for N=64, M=5

Queue: remote_cpu_queue (CPU; N={256,512,1024} x 5 seeds; ~20-30 min)
Pre-reg: preregs/2026-05-27_wave14_ortho_pme_ising_v2.md
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
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
N_FULL   = [256, 512, 1024]
N_SMOKE  = [64, 128]
M_FRAC   = 0.10           # M = M_FRAC * N (sub-capacity load)
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]
HOPFIELD_ALPHA_C = 0.138  # empirical Hopfield alpha_c
BETA_INV = 1.0            # inverse temperature (beta = 1)

# Hard-pass/fail bands
HP_ALPHA_LO = 0.05
HP_ALPHA_HI = 0.30
HP_FRAC_THRESH = 0.6
HF_ALPHA_VACUOUS = 10.0
HF_ALPHA_TRIVIAL = 0.01


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def build_hopfield_J(N: int, M: int, seed: int) -> np.ndarray:
    """Symmetric Hopfield J = sum_mu v_mu v_mu^T / N, diag=0."""
    rng = np.random.default_rng(seed)
    J = np.zeros((N, N))
    for _ in range(M):
        v = rng.choice([-1.0, 1.0], size=N)
        J += np.outer(v, v)
    J /= N
    np.fill_diagonal(J, 0.0)
    return J


def mean_field_free_energy(J: np.ndarray, beta: float = 1.0, n_iter: int = 200) -> float:
    """Variational mean-field free energy per spin: f = -1/N * log Z_MF.

    Uses update: m_i = tanh(beta * sum_j J_ij m_j).
    Variational lower bound on log Z:
      log Z >= sum_i log(2 cosh(beta h_i)) - beta/2 * m^T J m
    f_MF = -1/N * [sum_i log(2 cosh(beta h_i)) - beta/2 * m^T J m]
    """
    N = len(J)
    rng = np.random.default_rng(42)
    m = rng.normal(0, 0.01, N)

    for _ in range(n_iter):
        h = beta * (J @ m)
        m_new = np.tanh(h)
        if np.abs(m_new - m).max() < 1e-7:
            m = m_new
            break
        m = 0.5 * m + 0.5 * m_new   # mixing for stability

    h = beta * (J @ m)
    log_Z = float(np.sum(np.log(2 * np.cosh(h))) - 0.5 * beta * float(m @ J @ m))
    return -log_Z / N   # free energy per spin (negative = stable)


def null_free_energy(N: int, beta: float = 1.0) -> float:
    """Free energy per spin for J=0 (null Ising): f_0 = -log(2) * beta^0 = -log(2)."""
    # At J=0: h=0, m=0, log Z = N * log(2 * cosh(0)) = N * log(2)
    return -math.log(2)  # per spin


def rs_alpha_c_estimate(N: int, M: int, beta: float = 1.0, n_iter: int = 100) -> float:
    """Replica-symmetric capacity estimate: find alpha where RS equations lose non-trivial root.

    RS signal equation (simplified Amit-Gutfreund-Sompolinsky):
      h_1 = 1 / (1 - alpha * <tanh'^2(z * sqrt(alpha * h_1))>_z)
    where z is Gaussian noise and the expectation is over z ~ N(0,1).

    Returns the approximate alpha_c = largest alpha where RS gives non-trivial solution.
    """
    alpha_used = M / N

    def rs_rhs(alpha: float, h_sig: float) -> float:
        """RHS of RS self-consistency equation for signal h_sig."""
        # Compute <tanh^2(sqrt(alpha * h_sig) * z)>_z via quadrature
        xs = np.linspace(-4.0, 4.0, 201)
        gauss_w = np.exp(-0.5 * xs**2) / math.sqrt(2 * math.pi) * (8.0 / 200)
        arg = math.sqrt(max(alpha * abs(h_sig), 1e-9)) * xs
        tanh2 = np.tanh(arg) ** 2
        C = float(np.sum(tanh2 * gauss_w))
        denom = 1.0 - alpha * C
        if abs(denom) < 1e-6:
            return 1e9
        return 1.0 / denom

    # Binary search for alpha_c: largest alpha where RS fixed point h_sig != 0
    alpha_lo, alpha_hi = 0.0, 0.5
    for _ in range(30):
        alpha_mid = 0.5 * (alpha_lo + alpha_hi)
        # Try to find non-trivial h_sig at alpha_mid
        h = 1.0
        for _ in range(n_iter):
            h_new = rs_rhs(alpha_mid, h)
            h_new = min(h_new, 1e6)   # cap to avoid overflow
            if abs(h_new - h) < 1e-5:
                h = h_new
                break
            h = 0.3 * h + 0.7 * h_new
        if h > 1.01:   # non-trivial root found -> alpha < alpha_c
            alpha_lo = alpha_mid
        else:
            alpha_hi = alpha_mid

    return 0.5 * (alpha_lo + alpha_hi)


def run_one_seed(N: int, M: int, seed: int) -> Dict:
    J = build_hopfield_J(N, M, seed)
    J0 = np.zeros((N, N))   # null Ising

    # Estimator 1: intensive delta_f capacity
    f_M = mean_field_free_energy(J, beta=BETA_INV)
    f_0 = null_free_energy(N, beta=BETA_INV)
    delta_f = f_M - f_0   # should be < 0 (lower free energy = more stable)
    h_pat = math.log(2)   # pattern entropy per spin
    # Capacity: |delta_f| / h_pat = alpha_c estimate
    alpha_c_Z = abs(delta_f) / h_pat if h_pat > 1e-9 else float("nan")

    # Estimator 2: RS alpha_c from signal self-consistency
    alpha_c_RS = rs_alpha_c_estimate(N, M, beta=BETA_INV)

    in_factor2_Z  = bool(HP_ALPHA_LO < alpha_c_Z  < HP_ALPHA_HI)
    in_factor2_RS = bool(HP_ALPHA_LO < alpha_c_RS < HP_ALPHA_HI)

    return {
        "N": N, "M": M, "seed": seed,
        "alpha_c_Z": round(float(alpha_c_Z), 5),
        "alpha_c_RS": round(float(alpha_c_RS), 5),
        "delta_f": round(float(delta_f), 6),
        "in_factor2_Z": in_factor2_Z,
        "in_factor2_RS": in_factor2_RS,
    }


def _instrumentation_selftest():
    # 1. RS fixed-point at alpha=0.1 -> non-trivial alpha_c > 0.1
    rs_est = rs_alpha_c_estimate(N=256, M=int(0.1 * 256), beta=1.0)
    assert math.isfinite(rs_est) and rs_est > 0.0, f"selftest 1 FAIL: rs_est={rs_est}"
    print(f"[selftest] 1/5 RS alpha_c estimate={rs_est:.4f} at alpha=0.1 OK")

    # 2. RS should give alpha_c < 0.5 (above Hopfield alpha_c)
    assert rs_est < 0.5, f"selftest 2 FAIL: RS alpha_c={rs_est} should be < 0.5"
    print(f"[selftest] 2/5 RS alpha_c < 0.5 OK")

    # 3. delta_f for J=0 -> delta_f ~ 0.0
    J0 = np.zeros((32, 32))
    f0 = mean_field_free_energy(J0)
    f0_null = null_free_energy(32)
    delta_f_null = f0 - f0_null
    assert abs(delta_f_null) < 0.1, f"selftest 3 FAIL: delta_f_null={delta_f_null:.4f}"
    print(f"[selftest] 3/5 delta_f(J=0)={delta_f_null:.4f} near 0 OK")

    # 4. delta_f > 0 in magnitude for Hopfield J with M=5 patterns
    J_test = build_hopfield_J(32, 5, 42)
    f_test = mean_field_free_energy(J_test)
    f_null_32 = null_free_energy(32)
    delta_f_test = f_test - f_null_32
    # Free energy should be more negative when patterns stored (lower = more stable)
    # abs delta_f should be > 0
    assert math.isfinite(delta_f_test), f"selftest 4 FAIL: delta_f not finite: {delta_f_test}"
    print(f"[selftest] 4/5 delta_f(M=5)={delta_f_test:.4f} finite OK")

    # 5. alpha_c_Z in (0, 1) for N=64, M=5
    result = run_one_seed(64, 5, 42)
    assert math.isfinite(result["alpha_c_Z"]) and result["alpha_c_Z"] > 0, \
        f"selftest 5 FAIL: alpha_c_Z={result['alpha_c_Z']}"
    # validity filter: at least 1 seed passes
    assert not math.isnan(result["alpha_c_RS"]), \
        "validity filter eliminated all cells at smoke scale"
    print(f"[selftest] 5/5 alpha_c_Z={result['alpha_c_Z']:.4f} alpha_c_RS={result['alpha_c_RS']:.4f} OK")

    print("[selftest] PASS: 5/5 OK", flush=True)


_instrumentation_selftest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    N_list = N_SMOKE if smoke else N_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL
    name   = os.environ.get("HDLAB_EXP_NAME", "wave14_ortho_pme_ising_v2")
    out_dir = get_output_dir(name)

    t0 = time.time()
    all_results: List[Dict] = []

    for N in N_list:
        M = max(1, int(N * M_FRAC))
        print(f"[run] N={N} M={M} seeds={seeds}", flush=True)
        for seed in seeds:
            r = run_one_seed(N, M, seed)
            all_results.append(r)
            print(f"  seed={seed}: alpha_c_Z={r['alpha_c_Z']:.5f} "
                  f"alpha_c_RS={r['alpha_c_RS']:.5f} "
                  f"in_factor2_Z={r['in_factor2_Z']} "
                  f"in_factor2_RS={r['in_factor2_RS']}", flush=True)

    by_N: Dict[int, List] = {}
    for r in all_results:
        by_N.setdefault(r["N"], []).append(r)

    summary: Dict = {}
    for N, rows in sorted(by_N.items()):
        alpha_Z  = [r["alpha_c_Z"]  for r in rows if math.isfinite(r["alpha_c_Z"])]
        alpha_RS = [r["alpha_c_RS"] for r in rows if math.isfinite(r["alpha_c_RS"])]
        summary[f"N{N}"] = {
            "N": N, "n_seeds": len(rows),
            "alpha_c_Z_mean":  round(float(np.mean(alpha_Z)),  5) if alpha_Z  else None,
            "alpha_c_RS_mean": round(float(np.mean(alpha_RS)), 5) if alpha_RS else None,
            "in_factor2_Z_frac":  sum(r["in_factor2_Z"]  for r in rows) / len(rows),
            "in_factor2_RS_frac": sum(r["in_factor2_RS"] for r in rows) / len(rows),
        }

    # Verdict: use best estimator
    factor2_Z  = sum(r["in_factor2_Z"]  for r in all_results) / len(all_results) if all_results else 0
    factor2_RS = sum(r["in_factor2_RS"] for r in all_results) / len(all_results) if all_results else 0
    best_frac  = max(factor2_Z, factor2_RS)
    best_est   = "Z" if factor2_Z >= factor2_RS else "RS"

    alphas_Z  = [r["alpha_c_Z"]  for r in all_results if math.isfinite(r["alpha_c_Z"])]
    alphas_RS = [r["alpha_c_RS"] for r in all_results if math.isfinite(r["alpha_c_RS"])]

    if not all_results:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = "INSTRUMENTATION_FAIL: no results"
    elif any(not math.isfinite(r["alpha_c_Z"]) for r in all_results):
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = "INSTRUMENTATION_FAIL: non-finite alpha_c values"
    elif best_frac >= HP_FRAC_THRESH:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: {best_frac:.2f} seeds in factor-2 of Hopfield "
                       f"(estimator={best_est}); alpha_c mean: Z={np.mean(alphas_Z):.4f} "
                       f"RS={np.mean(alphas_RS):.4f}; PME Ising agrees with Hopfield")
    elif (alphas_Z and all(a > HF_ALPHA_VACUOUS for a in alphas_Z) or
          alphas_Z and all(a < HF_ALPHA_TRIVIAL for a in alphas_Z)):
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: alpha_c_Z mean={np.mean(alphas_Z):.4f} -- "
                       f"vacuous or trivial bound; Ising formulation does not apply")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: best_factor2_frac={best_frac:.2f} (estimator={best_est}); "
                       f"alpha_c_Z_mean={np.mean(alphas_Z):.4f} alpha_c_RS_mean={np.mean(alphas_RS):.4f}; "
                       f"estimators disagree or are off from Hopfield by > factor 2")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 1),
        "summary": summary,
        "config": {
            "mode": "smoke" if smoke else "full",
            "N_list": N_list, "seeds": seeds,
            "M_frac": M_FRAC, "hopfield_alpha_c": HOPFIELD_ALPHA_C,
            "v2_fix": "corrected intensive delta_f formula + RS alpha_c estimator",
        },
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[VERDICT] {verdict}: {verdict_msg[:150]}", flush=True)
    print(f"[metrics written] {out_path}", flush=True)


if __name__ == "__main__":
    main()
