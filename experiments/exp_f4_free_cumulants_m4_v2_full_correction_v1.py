"""
f4_free_cumulants_m4_v2_full_correction_v1 -- F4 free cumulants M4 v2 with full correction.

BACKGROUND:
  f4_free_cumulants_m4_fixed_v1 MIDDLE_BAND (v334, I-9): M3 + kappa_2 HARD_PASS (rel_err<=5%).
  M4 MIDDLE_BAND: rel_err_M4 = 0.066 (+33% over HP=0.05; HF=0.30 not triggered).

  Root cause hypothesis (I-9): at alpha=0.10 N=1024, the M4 formula
  M4 = alpha + 7*alpha^2 + 6*alpha^3 + alpha^4 has a FINITE-N correction of O(1/N).
  The next order correction for the spectral 4th moment of the Marchenko-Pastur law
  (Bai & Silverstein 1999 + Mingo & Speicher 2017 free-probability results):
    M4_corrected = M4_bulk + (2/N) * alpha^2 * (3*alpha + 2)  (leading 1/N finite-N term)
  This adds ~2*0.01*(0.3+0.2)/1024 = ~0.001/1024 -> negligible at N=1024.

  Alternative: the issue is that alpha = M/N is random (not exactly 0.10) since M=int(0.10*N).
  At N=1024, M=102, actual alpha=102/1024=0.0996. The formula uses exact alpha;
  the empirical 4th moment has additional fluctuation variance ~ O(1/N).

  Fix: (a) sweep alpha over {0.05, 0.10, 0.15, 0.20} to see if M4 error is systematic
  or alpha-specific; (b) also try N=4096 which reduces fluctuations by 4x.

  At N=4096: finite-N corrections drop 4x; if M4 HP at N=4096 the issue was finite-N.
  At multiple alpha: if M4 error tracks alpha-dependent deviation, formula fix needed.

HARD-PASS: rel_err_M4 <= 0.05 for at least 3/4 alpha values AND mean_rel_M4 <= 0.08.
HARD-FAIL: rel_err_M4 > 0.30 for any alpha value (formula is wrong).
MIDDLE: mean rel_err_M4 in (0.05, 0.30) with no HF triggers.

PRE-REGISTERED BANDS:
  HP: rel_err_M4 <= 0.05 for 3/4 alpha values AND mean <= 0.08.
  HF: rel_err_M4 > 0.30 for any alpha (formula inconsistent).
  MIDDLE: mean in (0.05, 0.30).
  Secondary metrics retained: M3 rel_err <= 0.08, kappa2 rel_err <= 0.05.

FORMULA SELF-TESTS:
  1. M4_bulk at alpha=0.20: 0.20 + 7*0.04 + 6*0.008 + 0.0016 = 0.20+0.28+0.048+0.0016 = 0.5296.
     [INPUT: alpha=0.20] [EXPECTED: M4=0.5296]
  2. M4_bulk at alpha=0.05: 0.05 + 7*0.0025 + 6*0.000125 + 0.0000125 = 0.05+0.0175+0.00075+~0 = 0.0683.
     [INPUT: alpha=0.05] [EXPECTED: M4 ~ 0.068]
  3. M4_bulk at alpha=0.10: same as v1 T1: expected=0.1761.
     [INPUT: alpha=0.10] [EXPECTED: M4=0.1761]
  4. W_full diagonal = alpha (BSC +-1).

No _nN suffix; production N in {1024, 4096} per sweep (N=4096 primary for this anchor).
NOTE: smoke at N=1024, FULL at N=4096 to test finite-N hypothesis.
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
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "f4_free_cumulants_m4_v2_full_correction_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N = 1024
    SEEDS = [7, 17, 23]
    ALPHA_GRID = [0.05, 0.10]
else:
    N = 4096    # Larger N to reduce finite-N fluctuations
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_GRID = [0.05, 0.10, 0.15, 0.20]

HP_REL_ERR_M4_PER_CELL = 0.05
HP_REL_ERR_M4_MEAN = 0.08
HF_REL_ERR_M4 = 0.30
HP_REL_ERR_M3 = 0.08
HP_KAPPA2_REL = 0.05
HF_KAPPA2_REL = 0.20


def free_poisson_moments(alpha: float):
    """Free-Poisson spectral moments for W_FULL (no diagonal removal)."""
    m1 = alpha
    m2 = alpha + alpha**2
    m3 = alpha + 3.0 * alpha**2 + alpha**3
    m4 = alpha + 7.0 * alpha**2 + 6.0 * alpha**3 + alpha**4
    return m1, m2, m3, m4


# ---- FORMULA SELF-TESTS ----
def _instrumentation_selftest():
    # Test 1: M4 at alpha=0.20
    _, _, _, m4_20 = free_poisson_moments(0.20)
    expected_20 = 0.20 + 7 * 0.04 + 6 * 0.008 + 0.0016
    assert abs(m4_20 - expected_20) < 1e-6, f"M4(0.20) T1: {m4_20:.6f} vs {expected_20:.6f}"

    # Test 2: M4 at alpha=0.05
    _, _, _, m4_05 = free_poisson_moments(0.05)
    expected_05 = 0.05 + 7 * 0.0025 + 6 * 0.000125 + (0.05)**4
    assert abs(m4_05 - expected_05) < 1e-8, f"M4(0.05) T2: {m4_05:.8f} vs {expected_05:.8f}"

    # Test 3: M4 at alpha=0.10 (same as v1)
    _, _, _, m4_10 = free_poisson_moments(0.10)
    expected_10 = 0.10 + 7 * 0.01 + 6 * 0.001 + 0.0001
    assert abs(m4_10 - expected_10) < 1e-6, f"M4(0.10) T3: {m4_10:.6f} vs {expected_10:.6f}"

    # Test 4: W_full diagonal = alpha
    N_t = 256
    M_t = int(0.10 * N_t)
    rng = np.random.RandomState(42)
    Xi_t = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    W_full_t = Xi_t.T @ Xi_t / float(N_t)
    alpha_t = M_t / N_t
    assert abs(float(np.mean(np.diag(W_full_t))) - alpha_t) < 1e-8, \
        f"W_full diag T4: {np.mean(np.diag(W_full_t)):.6f} vs alpha={alpha_t:.4f}"

    assert len(ALPHA_GRID) >= 2, "ALPHA_GRID too short"
    assert len(SEEDS) >= 2, "SEEDS too short"
    assert N >= 512, "N too small for reliable spectral estimates"

    print(f"[selftest] PASS: M4(0.20)={m4_20:.6f} M4(0.05)={m4_05:.8f} "
          f"M4(0.10)={m4_10:.6f} W_diag=alpha N={N} alpha_grid={ALPHA_GRID}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_one_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()
    results_by_alpha = {}

    for alpha_nom in ALPHA_GRID:
        M = max(1, int(alpha_nom * N))
        alpha = M / N   # exact alpha

        Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
        # FIX: use W_FULL (no diagonal removal) as in f4_free_cumulants_m4_fixed_v1
        W_full = Xi.T @ Xi / float(N)
        # Do NOT fill_diagonal -- this is the key fix

        eigenvalues = np.linalg.eigvalsh(W_full)

        m1_emp = float(np.mean(eigenvalues))
        m2_emp = float(np.mean(eigenvalues**2))
        m3_emp = float(np.mean(eigenvalues**3))
        m4_emp = float(np.mean(eigenvalues**4))

        m1_th, m2_th, m3_th, m4_th = free_poisson_moments(alpha)

        rel_err_M4 = abs(m4_emp - m4_th) / (abs(m4_th) + 1e-12)
        rel_err_M3 = abs(m3_emp - m3_th) / (abs(m3_th) + 1e-12)
        kappa2_emp = m2_emp - m1_emp**2
        kappa2_rel = abs(kappa2_emp - alpha) / alpha

        hp_m4 = rel_err_M4 <= HP_REL_ERR_M4_PER_CELL
        hp_m3 = rel_err_M3 <= HP_REL_ERR_M3
        hp_k2 = kappa2_rel <= HP_KAPPA2_REL
        hf_m4 = rel_err_M4 > HF_REL_ERR_M4

        print(f"  [seed={seed} alpha={alpha:.4f} N={N}] "
              f"M4_emp={m4_emp:.5f} M4_th={m4_th:.5f} rel_M4={rel_err_M4:.4f} "
              f"M3_rel={rel_err_M3:.4f} k2_rel={kappa2_rel:.4f} "
              f"hp_m4={hp_m4}", flush=True)

        assert m4_emp > 0.0, f"m4_emp={m4_emp} is zero at alpha={alpha}"
        assert abs(m1_emp - alpha) < 0.5, f"m1_emp far from alpha at alpha={alpha}"

        results_by_alpha[str(alpha_nom)] = {
            "alpha_nom": float(alpha_nom), "alpha_actual": float(alpha), "M": M, "N": N,
            "m1_emp": float(m1_emp), "m2_emp": float(m2_emp),
            "m3_emp": float(m3_emp), "m4_emp": float(m4_emp),
            "m1_th": float(m1_th), "m2_th": float(m2_th),
            "m3_th": float(m3_th), "m4_th": float(m4_th),
            "rel_err_M4": float(rel_err_M4),
            "rel_err_M3": float(rel_err_M3),
            "kappa2_rel": float(kappa2_rel),
            "hp_m4": bool(hp_m4), "hp_m3": bool(hp_m3),
            "hp_k2": bool(hp_k2), "hf_m4": bool(hf_m4),
        }

    elapsed = time.time() - t0
    return {"seed": seed, "N": N, "run_mode": RUN_MODE,
            "results_by_alpha": results_by_alpha, "elapsed_s": float(elapsed)}


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    results_list = list(per_seed.values())
    if not results_list:
        return ("HARD_FAIL", "No valid results.")

    n = len(results_list)
    # Aggregate rel_err_M4 per alpha_nom across seeds
    alpha_stats = {}
    for r in results_list:
        for alpha_str, cell in r.get("results_by_alpha", {}).items():
            key = float(alpha_str)
            if key not in alpha_stats:
                alpha_stats[key] = {"err_m4": [], "hp_m4": [], "hf_m4": [], "err_m3": [], "err_k2": []}
            alpha_stats[key]["err_m4"].append(cell["rel_err_M4"])
            alpha_stats[key]["hp_m4"].append(cell["hp_m4"])
            alpha_stats[key]["hf_m4"].append(cell["hf_m4"])
            alpha_stats[key]["err_m3"].append(cell["rel_err_M3"])
            alpha_stats[key]["err_k2"].append(cell["kappa2_rel"])

    any_hf_m4 = False
    n_alpha_hp_m4 = 0
    all_m4_errs = []
    summary_parts = []
    for ak in sorted(alpha_stats.keys()):
        mean_m4 = float(np.mean(alpha_stats[ak]["err_m4"]))
        n_hp = sum(alpha_stats[ak]["hp_m4"])
        n_hf = sum(alpha_stats[ak]["hf_m4"])
        all_m4_errs.append(mean_m4)
        if n_hf > 0:
            any_hf_m4 = True
        if n_hp >= math.ceil(n * 0.8):
            n_alpha_hp_m4 += 1
        summary_parts.append(f"alpha={ak:.2f}:M4_err={mean_m4:.3f}")

    n_alpha_total = len(alpha_stats)
    mean_all_m4 = float(np.mean(all_m4_errs)) if all_m4_errs else 1.0
    summary = " ".join(summary_parts) + f" mean_M4_err={mean_all_m4:.4f} N={N} n_seeds={n}"

    if any_hf_m4:
        return ("HARD_FAIL", f"HARD_FAIL: M4 rel_err > {HF_REL_ERR_M4} for some alpha. {summary}")

    hp_count = n_alpha_hp_m4 >= (n_alpha_total - 1)  # 3/4 or better
    hp_mean = mean_all_m4 <= HP_REL_ERR_M4_MEAN

    if hp_count and hp_mean:
        return ("HARD_PASS", f"HARD_PASS: M4 formula confirmed at N={N}. {summary}")
    if mean_all_m4 <= 0.15:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: M4 partial improvement (mean_err={mean_all_m4:.4f}). {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: M4 still off after N-scaling. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "alpha_grid": ALPHA_GRID, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} done, {len(remaining)} to run "
      f"(N={N} alpha_grid={ALPHA_GRID} mode={RUN_MODE})", flush=True)

t_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] F4 M4 v2 full correction N={N}...", flush=True)
    result = run_one_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
verdict, verdict_msg = compute_verdict(per_seed)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
    "alpha_grid": ALPHA_GRID, "elapsed_s": elapsed_s,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
