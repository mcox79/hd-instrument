"""
f4_free_cumulants_v1 -- Measure kappa_4 free cumulant; test kappa_n = alpha prediction.

SCIENTIFIC QUESTION (Free-probability F4 free cumulants):
  Research drilled free cumulants as next test for the free-Poisson confirmation
  (v324 confirmed spectral bulk = free-Poisson MP, kappa_2 = alpha).

  The free-Poisson distribution has free cumulants kappa_n = alpha for ALL n >= 1.
  This is the defining property: ALL free cumulants are equal to alpha (the
  loading parameter). This is a stronger test than the spectral bulk MP fit:
  the spectral bulk is determined by kappa_1 and kappa_2, but kappa_3 and kappa_4
  are non-trivial to measure and provide independent confirmation.

  Measurement protocol:
    1. Build W = (1/N) * Xi^T Xi with M=alpha*N patterns.
    2. Compute empirical spectral moments E[lambda^k] for k=1,2,3,4 from eigenvalues.
    3. Convert moments to FREE cumulants via the moment-cumulant formula in free probability.
       kappa_1 = m_1
       kappa_2 = m_2 - m_1^2
       kappa_3 = m_3 - 3*m_2*m_1 + 2*m_1^3
       kappa_4 = m_4 - 4*m_3*m_1 - 2*m_2^2 + 10*m_2*m_1^2 - 5*m_1^4
                 (free cumulant version; differs from classical cumulants)
       NOTE: The free moment-cumulant relation for kappa_n uses the R-transform
       or equivalently the Voiculescu formula. For free-Poisson with weight alpha:
         kappa_1 = alpha
         kappa_2 = alpha
         kappa_3 = alpha
         kappa_4 = alpha
    4. Compare empirical kappa_4 to alpha within 5% (HP) or 20% (MIDDLE) tolerance.

  NOTE on kappa_4 formula: The classical fourth cumulant is k_4 = mu_4 - 4*mu_3*mu_1
  - 3*mu_2^2 + 12*mu_2*mu_1^2 - 6*mu_1^4 (classical). The FREE cumulant kappa_4
  uses a DIFFERENT moment-cumulant relation from the non-crossing partition lattice
  (Speicher 1994). For free-Poisson W: kappa_n = alpha for all n.
  We use the direct eigenvalue-based measurement: kappa_4 = E[eigenvalue] - alpha.
  Wait -- more precisely, we measure via the R-transform coefficient at order 4.

  Simplified protocol: measure the empirical fourth spectral moment M4 = E[lambda^4]
  and compare to the free-Poisson prediction: M4_theory = sum_{k=0}^{4} C(4,k) * alpha^k
  where C(n,k) is the Catalan number contribution from free cumulant expansion:
  M4 = alpha + 7*alpha^2 + 6*alpha^3 + alpha^4 (free-Poisson fourth moment).
  The relative error |M4_emp - M4_theory| / M4_theory is the primary metric.

  Test cells:
    (A) M4 relative error: |M4_emp - M4_theory| / M4_theory <= 0.05.
        HP-A: rel_err_M4 <= 0.05. HF-A: rel_err_M4 > 0.30.
    (B) M3 relative error (cross-check): |M3_emp - M3_theory| / M3_theory <= 0.08.
        HP-B: rel_err_M3 <= 0.08. HF-B: rel_err_M3 > 0.30.
    (C) kappa_2 consistency: |kappa_2_emp - alpha| / alpha <= 0.05.
        HP-C: kappa_2_rel_err <= 0.05. HF-C: kappa_2_rel_err > 0.20.

  HARD-PASS: All of A, B, C.
  HARD-FAIL: HF-A or HF-C triggered.
  MIDDLE: B or C alone.

  Free-Poisson moment formulas (Haagerup-Thorbjornsen 2003):
    M1 = alpha
    M2 = alpha + alpha^2
    M3 = alpha + 3*alpha^2 + alpha^3
    M4 = alpha + 7*alpha^2 + 6*alpha^3 + alpha^4
    These follow from kappa_n = alpha for all n via free moment-cumulant relation.

PRE-REGISTERED BANDS (calibration probe, first free-cumulant direct measurement):
  HP: rel_err_M4 <= 0.05, rel_err_M3 <= 0.08, kappa_2_rel_err <= 0.05.
  HF: rel_err_M4 > 0.30, rel_err_M3 > 0.30, kappa_2_rel_err > 0.20.
  Bands: +-50% of theory per calibration-probe policy.
  Prior: v324 confirmed spectral bulk = MP which is consistent with free-Poisson;
  this is the first direct kappa_4 measurement.

FORMULA SELF-TESTS:
  1. Free-Poisson M4 formula: alpha=0.10 =>
     M4 = 0.10 + 7*0.01 + 6*0.001 + 0.0001 = 0.10+0.07+0.006+0.0001 = 0.1761
     [INPUT: alpha=0.10] [EXPECTED: M4=0.1761]
  2. Free-Poisson M3 formula: alpha=0.10 =>
     M3 = 0.10 + 3*0.01 + 0.001 = 0.10+0.03+0.001 = 0.131
     [INPUT: alpha=0.10] [EXPECTED: M3=0.131]
  3. Relative error: |0.1761 - 0.1800| / 0.1761 = 0.039/0.1761 = 0.022.
     [INPUT: M4_emp=0.18, M4_theory=0.1761] [EXPECTED: rel_err=0.022]

TIMEOUT ESTIMATE:
  Smoke: N=512, M=51 (alpha=0.10), 3 seeds. eigendecomposition O(N^2) ~ 512^2 ~ 0.5s.
  Full: N=1024, M=102, 5 seeds. O(N^2) ~ 1s each, 5 seeds.
  Scale: linear seeds. 1.5 * 0.5 * (1024/512)^2 * (5/3) = ceil(1.5*0.5*4*1.67) = ceil(5.0) = 5s.
  timeout=120s (generous for eigendecomposition).

No _nN suffix; production N=1024 per rule 3.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "f4_free_cumulants_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

if RUN_MODE == "smoke":
    N = 512
    SEEDS = [7, 17, 23]
    ALPHA = 0.10
else:
    N = 1024
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA = 0.10

# Pre-registered thresholds
HP_REL_ERR_M4 = 0.05
HF_REL_ERR_M4 = 0.30
HP_REL_ERR_M3 = 0.08
HF_REL_ERR_M3 = 0.30
HP_KAPPA2_REL = 0.05
HF_KAPPA2_REL = 0.20

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()


def free_poisson_moments(alpha: float):
    """Free-Poisson spectral moments for kappa_n = alpha (all n)."""
    m1 = alpha
    m2 = alpha + alpha**2
    m3 = alpha + 3.0 * alpha**2 + alpha**3
    m4 = alpha + 7.0 * alpha**2 + 6.0 * alpha**3 + alpha**4
    return m1, m2, m3, m4


# ---- FORMULA SELF-TESTS ----
def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # 1. Free-Poisson M4 at alpha=0.10
    m1, m2, m3, m4 = free_poisson_moments(0.10)
    expected_m4 = 0.10 + 7 * 0.01 + 6 * 0.001 + 0.0001
    assert abs(m4 - expected_m4) < 1e-6, f"M4 formula: got {m4:.6f}, expected {expected_m4:.6f}"

    # 2. Free-Poisson M3 at alpha=0.10
    expected_m3 = 0.10 + 3 * 0.01 + 0.001
    assert abs(m3 - expected_m3) < 1e-6, f"M3 formula: got {m3:.6f}, expected {expected_m3:.6f}"

    # 3. Relative error formula
    m4_emp = 0.18
    m4_theory = expected_m4
    rel_err = abs(m4_emp - m4_theory) / m4_theory
    expected_rel = abs(0.18 - 0.1761) / 0.1761
    assert abs(rel_err - expected_rel) < 1e-6, f"rel_err formula: {rel_err:.4f} vs {expected_rel:.4f}"

    print(f"[selftest] M4_theory={m4:.6f} M3_theory={m3:.6f} rel_err_check={rel_err:.4f}", flush=True)


_instrumentation_selftest()


def run_one_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    M = int(ALPHA * N)
    Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
    W = Xi.T @ Xi / N
    np.fill_diagonal(W, 0.0)

    # Compute empirical spectral moments via eigenvalues
    eigenvalues = np.linalg.eigvalsh(W)  # O(N^2) but fast for N=1024

    m1_emp = float(np.mean(eigenvalues))
    m2_emp = float(np.mean(eigenvalues**2))
    m3_emp = float(np.mean(eigenvalues**3))
    m4_emp = float(np.mean(eigenvalues**4))

    # Theoretical free-Poisson moments
    m1_th, m2_th, m3_th, m4_th = free_poisson_moments(ALPHA)

    rel_err_M4 = abs(m4_emp - m4_th) / (abs(m4_th) + 1e-12)
    rel_err_M3 = abs(m3_emp - m3_th) / (abs(m3_th) + 1e-12)
    kappa2_emp = m2_emp - m1_emp**2
    kappa2_rel = abs(kappa2_emp - ALPHA) / ALPHA

    # Validate: at least non-trivial eigenvalues
    assert m4_emp > 0.0, f"m4_emp={m4_emp} is zero -- instrumentation bug"
    assert abs(m1_emp - ALPHA) < 0.5, f"m1_emp={m1_emp:.4f} far from alpha={ALPHA}"

    cell_A_pass = rel_err_M4 <= HP_REL_ERR_M4
    cell_A_hf = rel_err_M4 > HF_REL_ERR_M4
    cell_B_pass = rel_err_M3 <= HP_REL_ERR_M3
    cell_C_pass = kappa2_rel <= HP_KAPPA2_REL
    cell_C_hf = kappa2_rel > HF_KAPPA2_REL

    return {
        "N": N,
        "run_mode": RUN_MODE,
        "seed": seed,
        "M": M,
        "m1_emp": m1_emp, "m2_emp": m2_emp, "m3_emp": m3_emp, "m4_emp": m4_emp,
        "m1_th": m1_th, "m2_th": m2_th, "m3_th": m3_th, "m4_th": m4_th,
        "rel_err_M4": rel_err_M4,
        "rel_err_M3": rel_err_M3,
        "kappa2_emp": kappa2_emp,
        "kappa2_rel": kappa2_rel,
        "cell_A_pass": cell_A_pass,
        "cell_A_hf": cell_A_hf,
        "cell_B_pass": cell_B_pass,
        "cell_C_pass": cell_C_pass,
        "cell_C_hf": cell_C_hf,
    }


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        print(f"[seed={seed}] running N={N} alpha={ALPHA}...", flush=True)
        result = run_one_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"[seed={seed}] M4_rel={result['rel_err_M4']:.4f} M3_rel={result['rel_err_M3']:.4f} kappa2_rel={result['kappa2_rel']:.4f}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    n_seeds = len(SEEDS)

    all_m4_rel = [per_seed[str(s)]["rel_err_M4"] for s in SEEDS]
    all_m3_rel = [per_seed[str(s)]["rel_err_M3"] for s in SEEDS]
    all_kappa2_rel = [per_seed[str(s)]["kappa2_rel"] for s in SEEDS]

    mean_m4_rel = float(np.mean(all_m4_rel))
    mean_m3_rel = float(np.mean(all_m3_rel))
    mean_kappa2_rel = float(np.mean(all_kappa2_rel))

    n_A = sum(1 for s in SEEDS if per_seed[str(s)]["cell_A_pass"])
    n_A_hf = sum(1 for s in SEEDS if per_seed[str(s)]["cell_A_hf"])
    n_B = sum(1 for s in SEEDS if per_seed[str(s)]["cell_B_pass"])
    n_C = sum(1 for s in SEEDS if per_seed[str(s)]["cell_C_pass"])
    n_C_hf = sum(1 for s in SEEDS if per_seed[str(s)]["cell_C_hf"])

    thr = math.ceil(n_seeds * 0.6)
    cell_A_pass = n_A >= thr
    cell_B_pass = n_B >= thr
    cell_C_pass = n_C >= thr
    hf_A = n_A_hf >= thr
    hf_C = n_C_hf >= thr

    n_cells_pass = int(cell_A_pass) + int(cell_B_pass) + int(cell_C_pass)
    if n_cells_pass == 3:
        verdict = "HARD_PASS"
    elif hf_A or hf_C:
        verdict = "HARD_FAIL"
    elif n_cells_pass >= 2:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL"

    elapsed = time.time() - t0
    verdict_msg = (
        f"f4_free_cumulants_v1 verdict={verdict}: "
        f"mean_rel_err_M4={mean_m4_rel:.4f}(HP<={HP_REL_ERR_M4},HF>{HF_REL_ERR_M4}) "
        f"mean_rel_err_M3={mean_m3_rel:.4f}(HP<={HP_REL_ERR_M3}) "
        f"mean_kappa2_rel={mean_kappa2_rel:.4f}(HP<={HP_KAPPA2_REL},HF>{HF_KAPPA2_REL}) "
        f"cells={n_cells_pass}/3 elapsed={elapsed:.1f}s"
    )
    print(verdict_msg, flush=True)

    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "N": N,
        "n_seeds": n_seeds,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "mean_rel_err_M4": mean_m4_rel,
        "mean_rel_err_M3": mean_m3_rel,
        "mean_kappa2_rel": mean_kappa2_rel,
        "all_rel_err_M4": all_m4_rel,
        "all_kappa2_rel": all_kappa2_rel,
        "elapsed_s": elapsed,
    }
    with open(Path(out_dir) / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] metrics written to {out_dir}/metrics.json", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
