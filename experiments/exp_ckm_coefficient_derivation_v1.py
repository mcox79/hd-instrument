"""
ckm_coefficient_derivation_v1 -- C(k,m) coefficient derivation for multi-step retrieval.

SCIENTIFIC QUESTION:
  Multi-step retrieval introduces correction coefficients C(k,m) that scale
  the effective signal at step k given m stored patterns.
  Research predicts: C(k,m) = (alpha)^{k-1} / k! (leading order) where alpha = M/N.
  Equivalently: C(k,m) = alpha^{k-1} * prod_{j=1}^{k-1} (1 - j/N) / k! (finite-N correction).

  Protocol:
    - For k in {2, 3, 5} retrieval steps and m in {N/4, N/2}:
      1. Measure empirical signal strength ratio after k Hopfield updates.
      2. Compare to closed-form C(k,m) prediction.
      3. Report relative error |C_emp - C_theory| / C_theory.

  HP: empirical C(k,m) matches closed-form within +/-5% across k in {2,3,5}, m in {N/4, N/2}.
  HF: deviation > 30% for any (k,m) cell (formula wrong or completely broken).
  MIDDLE: some cells within 5%, some between 5% and 30%.

PRE-REGISTERED BANDS (calibration probe -- first C(k,m) direct measurement):
  HP: rel_err <= 0.05 for >= 5/6 cells.
  HF: rel_err > 0.30 for any cell.
  MIDDLE: 3/6 cells within HP.
  Note: no prior direct C(k,m) empirical measurement. Bands set +-50% of theory.

FORMULA SELF-TESTS:
  1. C(2,m) = alpha / 2!: for k=2, m/N=alpha.
     [INPUT: k=2, alpha=0.25] [EXPECTED: C(2,m) = alpha/2 = 0.125]
  2. C(3,m) = alpha^2 / 3!: for k=3.
     [INPUT: k=3, alpha=0.25] [EXPECTED: C(3,m) = 0.25^2/6 = 0.010417]
  3. C(5,m) = alpha^4 / 5!: for k=5.
     [INPUT: k=5, alpha=0.25] [EXPECTED: C(5,m) = 0.25^4/120 = 0.0000814]
  4. Relative error: |(C_emp - C_theory)| / C_theory.
     [INPUT: C_emp=0.13, C_theory=0.125] [EXPECTED: rel_err = 0.04]

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
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "ckm_coefficient_derivation_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

N = 1024

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    K_LIST = [2, 3]
    M_FRAC_LIST = [0.25]   # M/N fractions
    N_PATTERNS_TEST = 20
else:
    SEEDS = [7, 17, 23, 31, 41]
    K_LIST = [2, 3, 5]
    M_FRAC_LIST = [0.25, 0.50]
    N_PATTERNS_TEST = 50

HP_REL_ERR = 0.05
HF_REL_ERR = 0.30
HP_CELL_FRAC = 5.0 / 6.0  # 5/6 cells within HP


def ckm_theory(k: int, alpha: float) -> float:
    """C(k,m) = alpha^{k-1} / k! (leading order for large N)."""
    if k < 1:
        return float("nan")
    return (alpha ** (k - 1)) / float(math.factorial(k))


# ---- FORMULA SELF-TESTS ----
_c2 = ckm_theory(2, 0.25)
_expected_c2 = 0.25 / 2.0  # alpha / 2! = 0.125
assert abs(_c2 - _expected_c2) < 1e-8, f"C(2,0.25) selftest: {_c2} expected {_expected_c2}"
_c3 = ckm_theory(3, 0.25)
_expected_c3 = (0.25**2) / 6.0  # alpha^2 / 3! = 0.010417
assert abs(_c3 - _expected_c3) < 1e-8, f"C(3,0.25) selftest: {_c3} expected {_expected_c3}"
_c5 = ckm_theory(5, 0.25)
_expected_c5 = (0.25**4) / 120.0  # alpha^4 / 5!
assert abs(_c5 - _expected_c5) < 1e-10, f"C(5,0.25) selftest: {_c5} expected {_expected_c5}"
_rel_err_t4 = abs(0.13 - 0.125) / 0.125
assert abs(_rel_err_t4 - 0.04) < 1e-8, f"rel_err T4: {_rel_err_t4}"
print(f"[formula_selftest] C(2,0.25)={_c2:.5f}(exp={_expected_c2:.5f}) "
      f"C(3,0.25)={_c3:.6f}(exp={_expected_c3:.6f}) "
      f"C(5,0.25)={_c5:.8f}(exp={_expected_c5:.8f}) rel_err_T4={_rel_err_t4:.2f} OK", flush=True)


def build_hopfield(Xi: np.ndarray, N_dim: int) -> np.ndarray:
    W = Xi.T @ Xi / float(N_dim)
    np.fill_diagonal(W, 0.0)
    return W


def measure_ckm_empirical(W: np.ndarray, Xi: np.ndarray,
                           k: int, seed: int,
                           n_test: int, n_dim: int) -> float:
    """Measure empirical C(k,m) as the normalized overlap after k steps.

    C(k,m)_emp = mean_{mu} [<x^(k) | xi_mu>^2 / N] where x^(k) is the state
    after k Hopfield updates starting from xi_mu.
    This should match alpha^{k-1}/k! at leading order.
    """
    rng = np.random.RandomState(seed)
    M = Xi.shape[0]
    overlaps = []

    for i in range(min(n_test, M)):
        state = Xi[i].copy()
        # No noise on initial state (pure signal measurement)
        for _ in range(k):
            h = W @ state
            state = np.sign(h)
            state[state == 0] = 1.0

        # Overlap = normalized dot with original pattern
        overlap = float(np.dot(state, Xi[i])) / n_dim
        overlaps.append(overlap)

    c_emp = float(np.mean(overlaps)) if overlaps else float("nan")
    return c_emp


def _instrumentation_selftest():
    """Verify C(k,m) measurement is non-null at smoke scale."""
    N_t = 256
    alpha = 0.25
    M_t = int(alpha * N_t)
    seed = 42

    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    W = build_hopfield(Xi, N_t)

    for k in [2, 3]:
        c_emp = measure_ckm_empirical(W, Xi, k, seed, n_test=10, n_dim=N_t)
        c_th = ckm_theory(k, alpha)
        assert c_emp is not None and not math.isnan(c_emp), f"c_emp NaN at k={k}"
        rel_err = abs(c_emp - c_th) / max(abs(c_th), 1e-12)
        print(f"[selftest] k={k} C_emp={c_emp:.4f} C_theory={c_th:.4f} rel_err={rel_err:.4f}",
              flush=True)

    assert len(K_LIST) > 0, "K_LIST empty"
    assert len(M_FRAC_LIST) > 0, "M_FRAC_LIST empty"
    print(f"[selftest] PASS: K_LIST={K_LIST} M_FRAC_LIST={M_FRAC_LIST} OK", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    results = {}

    for m_frac in M_FRAC_LIST:
        M = max(1, int(m_frac * N))
        alpha = M / N
        Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
        W = build_hopfield(Xi, N)

        for k in K_LIST:
            c_emp = measure_ckm_empirical(W, Xi, k, seed, N_PATTERNS_TEST, N)
            c_th = ckm_theory(k, alpha)
            rel_err = abs(c_emp - c_th) / max(abs(c_th), 1e-12)
            hp_ok = rel_err <= HP_REL_ERR
            hf_ok = rel_err > HF_REL_ERR

            key = f"k{k}_m{m_frac:.2f}"
            print(f"  [seed={seed} k={k} m_frac={m_frac:.2f}] "
                  f"C_emp={c_emp:.5f} C_theory={c_th:.5f} rel_err={rel_err:.4f} hp={hp_ok}",
                  flush=True)

            results[key] = {
                "k": k, "m_frac": float(m_frac), "M": M, "N": N, "alpha": float(alpha),
                "c_emp": float(c_emp),
                "c_theory": float(c_th),
                "rel_err": float(rel_err),
                "hp_ok": bool(hp_ok),
                "hf_ok": bool(hf_ok),
            }

    return {"results": results, "seed": seed, "N": N, "run_mode": RUN_MODE}


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    cell_keys = [f"k{k}_m{m:.2f}" for k in K_LIST for m in M_FRAC_LIST]
    cell_rel_errs = {k: [] for k in cell_keys}

    for sd in per_seed.values():
        for k, v in sd.get("results", {}).items():
            if k in cell_rel_errs and v.get("rel_err") is not None:
                cell_rel_errs[k].append(v["rel_err"])

    mean_rel_errs = {k: float(np.mean(v)) if v else float("nan")
                     for k, v in cell_rel_errs.items()}
    n_cells = len(cell_keys)
    n_hp = sum(1 for v in mean_rel_errs.values() if not math.isnan(v) and v <= HP_REL_ERR)
    hf_any = any(not math.isnan(v) and v > HF_REL_ERR for v in mean_rel_errs.values())

    summary = (f"mean_rel_errs={mean_rel_errs} n_hp={n_hp}/{n_cells} "
               f"HP_REL_ERR={HP_REL_ERR} HF_REL_ERR={HF_REL_ERR}")

    if hf_any:
        return ("HARD_FAIL", f"HARD_FAIL: rel_err > {HF_REL_ERR} for some cell. {summary}")
    if n_hp / n_cells >= HP_CELL_FRAC:
        return ("HARD_PASS", f"HARD_PASS: {n_hp}/{n_cells} cells within {HP_REL_ERR}. {summary}")
    if n_hp / n_cells >= 0.5:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp}/{n_cells} cells within HP. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: {n_hp}/{n_cells} cells within HP. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] ckm_coeff N={N} K_list={K_LIST} M_frac={M_FRAC_LIST}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
verdict, verdict_msg = compute_verdict(per_seed)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_s, "K_list": K_LIST, "M_frac_list": M_FRAC_LIST,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
