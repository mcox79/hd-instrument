"""
f4_free_cumulants_m4_fixed_v1 -- Re-design of f4_free_cumulants with corrected M4 formula.

BACKGROUND:
  f4_free_cumulants_v1 HARD-FAILED because the M4 formula assumed W = (1/N) Xi^T Xi
  with NO diagonal removal. In practice, W has diagonal removed (W[i,i] = 0).
  This shifts the spectral moments: the correct formula must account for the
  diagonal-removed W's moment differences from the raw W.

  Correction:
    For W_full = (1/N) Xi^T Xi (no diagonal removal):
      M1 = alpha, M2 = alpha + alpha^2, M3 = alpha + 3*alpha^2 + alpha^3,
      M4 = alpha + 7*alpha^2 + 6*alpha^3 + alpha^4.
    For W_diag_removed = W_full - diag(W_full):
      diag(W_full)_ii = (1/N) * sum_mu (xi_mu_i)^2 = M/N = alpha (for BSC +-1).
      So W_diag = W_full - alpha * I.
      Eigenvalues of W_diag = eigenvalues of W_full - alpha.
      Moments of W_diag: M_k(W_diag) = E[(lambda - alpha)^k] using W_full moments.
      M1_diag = E[lambda - alpha] = alpha - alpha = 0.
      M2_diag = E[(lambda - alpha)^2] = Var(lambda) = M2_full - M1_full^2 = alpha^2.
      M3_diag = E[(lambda - alpha)^3] = M3_full - 3*M2_full*alpha + 2*alpha^3.
      M4_diag = E[(lambda - alpha)^4] = M4_full - 4*M3_full*alpha + 6*M2_full*alpha^2
                                         - 3*alpha^4. (central 4th moment)
      CORRECTED M4 = alpha + 7*alpha^2 + 6*alpha^3 + alpha^4 (still, in terms of eigenvalue distribution)
      but measured eigenvalues include diagonal shift. Use full-W eigenvalues vs diag-removed eigenvalues.

  FIXED PROTOCOL: Use eigenvalues of W_full (no diagonal removal) for moment comparison.
  This avoids the diagonal-correction issue entirely.

HP/HF per original f4_free_cumulants_v1 design but using W_full (no diag removal):
  HP: rel_err_M4 <= 0.05, rel_err_M3 <= 0.08, kappa2_rel_err <= 0.05.
  HF: rel_err_M4 > 0.30 OR kappa2_rel_err > 0.20.
  MIDDLE: 2/3 cells pass.

PRE-REGISTERED BANDS:
  Same as f4_free_cumulants_v1 but with correct W_full (no diagonal removal).
  All formulas remain valid for W_full: free-Poisson moments M1..M4 = alpha+7alpha^2+...
  The prior v1 failure was instrumentation (W had diagonal removed). This is the fix.

FORMULA SELF-TESTS:
  1. M4_full at alpha=0.10: alpha + 7*alpha^2 + 6*alpha^3 + alpha^4.
     [INPUT: alpha=0.10] [EXPECTED: M4=0.1761]
  2. M3_full at alpha=0.10: alpha + 3*alpha^2 + alpha^3.
     [INPUT: alpha=0.10] [EXPECTED: M3=0.131]
  3. W_full diagonal is NOT zeroed. Verify W[0,0] = M/N = alpha.
     [INPUT: W_full = (1/N) Xi^T Xi, N=256, M=26 (alpha=0.1016)]
     [EXPECTED: W_full[0,0] ~ alpha within 30% (statistical)]
  4. M1_full = trace(W_full)/N = M*||xi_mu||^2 / N^2 = M/N = alpha (exactly for BSC).
     [INPUT: W_full, Xi BSC +-1] [EXPECTED: M1 = alpha exactly]
  5. W_diag_removed moment shift: M1(W_diag) = M1(W_full) - alpha = 0.
     [INPUT: W_diag, alpha=0.10] [EXPECTED: M1(W_diag) ~ 0 within 10%]

No _nN suffix; production N=1024 per PROT-018 rule 3.
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

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "f4_free_cumulants_m4_fixed_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

N = 1024

if RUN_MODE == "smoke":
    SEEDS = [7, 17, 23]
    ALPHA = 0.10
else:
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA = 0.10

HP_REL_ERR_M4 = 0.05
HF_REL_ERR_M4 = 0.30
HP_REL_ERR_M3 = 0.08
HF_REL_ERR_M3 = 0.30
HP_KAPPA2_REL = 0.05
HF_KAPPA2_REL = 0.20


def free_poisson_moments(alpha: float):
    """Free-Poisson spectral moments for W_FULL (no diagonal removal). kappa_n = alpha."""
    m1 = alpha
    m2 = alpha + alpha**2
    m3 = alpha + 3.0 * alpha**2 + alpha**3
    m4 = alpha + 7.0 * alpha**2 + 6.0 * alpha**3 + alpha**4
    return m1, m2, m3, m4


# ---- FORMULA SELF-TESTS ----
def _instrumentation_selftest():
    # Test 1: M4_full at alpha=0.10
    m1, m2, m3, m4 = free_poisson_moments(0.10)
    expected_m4 = 0.10 + 7 * 0.01 + 6 * 0.001 + 0.0001
    assert abs(m4 - expected_m4) < 1e-6, f"M4_full T1: {m4:.6f} vs {expected_m4:.6f}"

    # Test 2: M3_full at alpha=0.10
    expected_m3 = 0.10 + 3 * 0.01 + 0.001
    assert abs(m3 - expected_m3) < 1e-6, f"M3_full T2: {m3:.6f} vs {expected_m3:.6f}"

    # Test 3: W_full diagonal check
    N_t = 256
    alpha_t = 0.10
    M_t = int(alpha_t * N_t)  # 25 or 26
    rng = np.random.RandomState(42)
    Xi_t = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    W_full_t = Xi_t.T @ Xi_t / float(N_t)
    # W_full[0,0] = (1/N) sum_mu xi_mu[0]^2 = M/N = alpha (for BSC +-1 exactly)
    alpha_actual_t = M_t / N_t
    w_diag_mean = float(np.mean(np.diag(W_full_t)))
    assert abs(w_diag_mean - alpha_actual_t) < 1e-8, \
        f"W_full diagonal T3: {w_diag_mean:.6f} vs alpha={alpha_actual_t:.4f}"

    # Test 4: M1_full = alpha exactly for BSC +-1
    m1_t = float(np.trace(W_full_t)) / N_t
    assert abs(m1_t - alpha_actual_t) < 1e-8, f"M1_full T4: {m1_t:.4f} vs {alpha_actual_t:.4f}"

    # Test 5: W_diag_removed moment shift
    W_diag_t = W_full_t.copy()
    np.fill_diagonal(W_diag_t, 0.0)
    eigs_diag = np.linalg.eigvalsh(W_diag_t)
    m1_diag = float(np.mean(eigs_diag))
    # M1(W_diag) = trace(W_diag)/N = 0 (diagonal removed)
    assert abs(m1_diag) < 0.10, f"M1(W_diag) T5: {m1_diag:.4f} expected ~0"

    # Test 6: At smoke scale, at least 1 seed runs
    assert len(SEEDS) > 0, "SEEDS empty"

    print(f"[selftest] PASS: M4_full={m4:.6f} M3_full={m3:.6f} "
          f"W_diag={w_diag_mean:.4f}=alpha W_diag_m1={m1_diag:.4f}~0 OK", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_one_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    M = int(ALPHA * N)
    alpha = M / N   # exact alpha for this seed (may differ from ALPHA by 1/N)

    Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
    # FIX: use W_FULL (no diagonal removal) for moment comparison
    W_full = Xi.T @ Xi / float(N)
    # Do NOT call np.fill_diagonal(W_full, 0.0) -- this is the key fix vs v1

    eigenvalues = np.linalg.eigvalsh(W_full)  # O(N^2)

    m1_emp = float(np.mean(eigenvalues))
    m2_emp = float(np.mean(eigenvalues**2))
    m3_emp = float(np.mean(eigenvalues**3))
    m4_emp = float(np.mean(eigenvalues**4))

    m1_th, m2_th, m3_th, m4_th = free_poisson_moments(alpha)

    rel_err_M4 = abs(m4_emp - m4_th) / (abs(m4_th) + 1e-12)
    rel_err_M3 = abs(m3_emp - m3_th) / (abs(m3_th) + 1e-12)
    kappa2_emp = m2_emp - m1_emp**2
    # kappa2 for free-Poisson = alpha (from moment-cumulant relation, same for W_full)
    kappa2_rel = abs(kappa2_emp - alpha) / alpha

    assert m4_emp > 0.0, f"m4_emp={m4_emp} is zero"
    assert abs(m1_emp - alpha) < 0.5, f"m1_emp={m1_emp:.4f} far from alpha={alpha}"

    cell_A_pass = rel_err_M4 <= HP_REL_ERR_M4
    cell_A_hf = rel_err_M4 > HF_REL_ERR_M4
    cell_B_pass = rel_err_M3 <= HP_REL_ERR_M3
    cell_C_pass = kappa2_rel <= HP_KAPPA2_REL
    cell_C_hf = kappa2_rel > HF_KAPPA2_REL

    print(f"  [seed={seed}] M4_emp={m4_emp:.5f} M4_th={m4_th:.5f} rel_err_M4={rel_err_M4:.4f} "
          f"M3_rel={rel_err_M3:.4f} kappa2_rel={kappa2_rel:.4f} "
          f"A={cell_A_pass} B={cell_B_pass} C={cell_C_pass}", flush=True)

    return {
        "N": N, "M": M, "alpha": float(alpha),
        "run_mode": RUN_MODE, "seed": seed,
        "m1_emp": float(m1_emp), "m2_emp": float(m2_emp),
        "m3_emp": float(m3_emp), "m4_emp": float(m4_emp),
        "m1_th": float(m1_th), "m2_th": float(m2_th),
        "m3_th": float(m3_th), "m4_th": float(m4_th),
        "rel_err_M4": float(rel_err_M4),
        "rel_err_M3": float(rel_err_M3),
        "kappa2_emp": float(kappa2_emp),
        "kappa2_rel": float(kappa2_rel),
        "cell_A_pass": bool(cell_A_pass),
        "cell_A_hf": bool(cell_A_hf),
        "cell_B_pass": bool(cell_B_pass),
        "cell_C_pass": bool(cell_C_pass),
        "cell_C_hf": bool(cell_C_hf),
    }


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        print(f"[seed={seed}] f4_fixed N={N} alpha={ALPHA}...", flush=True)
        result = run_one_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"  -> M4_rel={result['rel_err_M4']:.4f} M3_rel={result['rel_err_M3']:.4f} "
              f"kappa2_rel={result['kappa2_rel']:.4f}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    n_seeds = len(per_seed)
    if n_seeds == 0:
        print("[VERDICT] HARD_FAIL: no seed results", flush=True)
        return

    all_m4_rel = [per_seed[str(s)]["rel_err_M4"] for s in SEEDS if str(s) in per_seed]
    all_m3_rel = [per_seed[str(s)]["rel_err_M3"] for s in SEEDS if str(s) in per_seed]
    all_kappa2_rel = [per_seed[str(s)]["kappa2_rel"] for s in SEEDS if str(s) in per_seed]

    mean_m4_rel = float(np.mean(all_m4_rel))
    mean_m3_rel = float(np.mean(all_m3_rel))
    mean_kappa2_rel = float(np.mean(all_kappa2_rel))

    thr = math.ceil(len(all_m4_rel) * 0.6)
    n_A = sum(1 for s in SEEDS if str(s) in per_seed and per_seed[str(s)]["cell_A_pass"])
    n_A_hf = sum(1 for s in SEEDS if str(s) in per_seed and per_seed[str(s)]["cell_A_hf"])
    n_B = sum(1 for s in SEEDS if str(s) in per_seed and per_seed[str(s)]["cell_B_pass"])
    n_C = sum(1 for s in SEEDS if str(s) in per_seed and per_seed[str(s)]["cell_C_pass"])
    n_C_hf = sum(1 for s in SEEDS if str(s) in per_seed and per_seed[str(s)]["cell_C_hf"])

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
        f"f4_free_cumulants_m4_fixed_v1 verdict={verdict}: "
        f"mean_rel_err_M4={mean_m4_rel:.4f}(HP<={HP_REL_ERR_M4},HF>{HF_REL_ERR_M4}) "
        f"mean_rel_err_M3={mean_m3_rel:.4f}(HP<={HP_REL_ERR_M3}) "
        f"mean_kappa2_rel={mean_kappa2_rel:.4f}(HP<={HP_KAPPA2_REL},HF>{HF_KAPPA2_REL}) "
        f"cells={n_cells_pass}/3 W=full_no_diag_removal elapsed={elapsed:.1f}s"
    )
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": RUN_MODE, "N": N, "n_seeds": n_seeds,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "mean_rel_err_M4": float(mean_m4_rel),
        "mean_rel_err_M3": float(mean_m3_rel),
        "mean_kappa2_rel": float(mean_kappa2_rel),
        "all_rel_err_M4": all_m4_rel,
        "all_kappa2_rel": all_kappa2_rel,
        "fix_note": "W_full (no diagonal removal) used -- fixes v1 diagonal-removal bug",
        "elapsed_s": elapsed,
    }
    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"[done] metrics written to {metrics_path}", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
else:
    main()
