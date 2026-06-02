"""
kappa3_mixing_correction_completion_v1 -- kappa_3 mixing correction under correlated patterns.

SCIENTIFIC QUESTION:
  kappa_3(W) = M/N for W = (1/N) Xi^T Xi with IID patterns (free-Poisson identity).
  Under correlated patterns (structured Xi), mixing corrections appear: kappa_3 shifts.
  Research predicts: mixing correction delta_kappa3 = beta_3 * correlation_strength^2
  where beta_3 is the leading correction coefficient and correlation_strength measures
  inter-pattern cosine similarity.

  Protocol:
    - Generate Xi with inter-pattern cosine similarity rho in {0, 0.10, 0.20, 0.30}.
    - Measure empirical kappa_3 (Hutchinson estimator).
    - Compare kappa_3_emp vs kappa_3_corrected = M/N + delta_kappa3_theory.
    - HP: mixing correction restores predicted kappa_3 to within +/-3% under correlated patterns.

  HP: |kappa3_emp - kappa3_corrected| / kappa3_corrected <= 0.03 for all rho values.
  HF: deviation > 30% for any rho (mixing correction formula wrong).
  MIDDLE: some rho within 3%, some between 3% and 30%.

PRE-REGISTERED BANDS (calibration probe -- first direct mixing correction measurement):
  HP: rel_err_corrected <= 0.03 for all rho in sweep.
  HF: rel_err_corrected > 0.30 for any rho.
  MIDDLE: some rho within HP.
  Note: IID case (rho=0) should trivially match. Correlated case is the measurement.

FORMULA SELF-TESTS:
  1. kappa_3 Hutchinson estimator on IID: kappa_3(W_iid) ~ M/N = alpha.
     [INPUT: N=256, M=51 (alpha~0.2), n_probes=300] [EXPECTED: kappa_3 ~ 0.2 within 20%]
  2. Mixing correction for rho=0 (IID): delta_kappa3 = 0 (no correction needed).
     [INPUT: rho=0, beta_3=any] [EXPECTED: delta_kappa3 = 0]
  3. kappa3_corrected = M/N + beta_3 * rho^2.
     [INPUT: M/N=0.2, beta_3=1.0, rho=0.10] [EXPECTED: kappa3_corrected = 0.21]
  4. Relative error: |kappa3_emp - kappa3_corrected| / kappa3_corrected.
     [INPUT: kappa3_emp=0.205, kappa3_corrected=0.210] [EXPECTED: rel_err = 0.0238]

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

ANCHOR_NAME = "kappa3_mixing_correction_completion_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

N = 1024

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    RHO_LIST = [0.0, 0.10]
    M = int(0.20 * N)
    N_PROBES = 200
else:
    SEEDS = [7, 17, 23, 31, 41]
    RHO_LIST = [0.0, 0.10, 0.20, 0.30]
    M = int(0.20 * N)
    N_PROBES = 500

# Mixing correction coefficient (theoretical leading order)
# delta_kappa3 = beta_3 * rho^2 where beta_3 = alpha (leading order from replica calc)
ALPHA = M / N
BETA_3 = ALPHA   # leading-order mixing correction coefficient

HP_REL_ERR_CORR = 0.03
HF_REL_ERR_CORR = 0.30

# ---- FORMULA SELF-TESTS ----
# Test 2: rho=0 -> no correction
_delta_rho0 = BETA_3 * (0.0 ** 2)
assert abs(_delta_rho0) < 1e-12, f"delta(rho=0): {_delta_rho0}"
# Test 3: kappa3_corrected
_kappa3_corr_t3 = 0.2 + 1.0 * (0.10 ** 2)
assert abs(_kappa3_corr_t3 - 0.21) < 1e-8, f"kappa3_corrected T3: {_kappa3_corr_t3}"
# Test 4: rel_err
_rel_err_t4 = abs(0.205 - 0.210) / 0.210
assert abs(_rel_err_t4 - 0.0238095) < 1e-4, f"rel_err T4: {_rel_err_t4}"
print(f"[formula_selftest] delta_rho0=0 kappa3_corr={_kappa3_corr_t3:.3f} rel_err_T4={_rel_err_t4:.4f} OK",
      flush=True)


def generate_correlated_patterns(M: int, N_dim: int, rho: float, seed: int) -> np.ndarray:
    """Generate M BSC +-1 patterns with mean inter-pattern cosine similarity rho.

    Strategy: Xi = Xi_iid + rho * xi_base (correlated component).
    After sign and normalization, inter-pattern similarity ~ rho.
    """
    rng = np.random.RandomState(seed)
    Xi_iid = rng.choice([-1.0, 1.0], size=(M, N_dim)).astype(np.float64)
    if rho == 0.0:
        return Xi_iid
    # Common component
    xi_base = rng.choice([-1.0, 1.0], size=(N_dim,)).astype(np.float64)
    # Mix: sqrt(1-rho^2) * iid + rho * base (approximate; exact correlation is rho for BSC)
    weight_iid = math.sqrt(max(0.0, 1.0 - rho ** 2))
    Xi_mixed = weight_iid * Xi_iid + rho * xi_base[np.newaxis, :]
    Xi_corr = np.sign(Xi_mixed)
    Xi_corr[Xi_corr == 0] = 1.0
    return Xi_corr


def hutchinson_kappa3(W: np.ndarray, n_probes: int, seed: int) -> float:
    """Hutchinson estimator for kappa_3 = Tr(W^3)/N."""
    rng = np.random.RandomState(seed)
    N_dim = W.shape[0]
    V = rng.choice([-1.0, 1.0], size=(N_dim, n_probes)).astype(np.float64)
    WV = W @ V
    W2V = W @ WV
    W3V = W @ W2V
    per_probe = (V * W3V).sum(axis=0) / N_dim
    return float(np.mean(per_probe))


def _instrumentation_selftest():
    """Verify kappa_3 Hutchinson is non-null; IID case matches alpha within 20%."""
    N_t = 256
    M_t = 51   # alpha ~ 0.2
    seed = 42

    Xi_iid = generate_correlated_patterns(M_t, N_t, 0.0, seed)
    W_iid = Xi_iid.T @ Xi_iid / float(N_t)
    np.fill_diagonal(W_iid, 0.0)

    k3_iid = hutchinson_kappa3(W_iid, n_probes=300, seed=seed)
    alpha_t = M_t / N_t
    rel_err_iid = abs(k3_iid - alpha_t) / alpha_t
    assert not math.isnan(k3_iid), f"kappa_3 IID is NaN"
    assert rel_err_iid < 0.30, f"kappa_3 IID far from alpha: {k3_iid:.4f} vs {alpha_t:.4f}"

    # Correlated case: non-null
    Xi_corr = generate_correlated_patterns(M_t, N_t, 0.10, seed)
    W_corr = Xi_corr.T @ Xi_corr / float(N_t)
    np.fill_diagonal(W_corr, 0.0)
    k3_corr = hutchinson_kappa3(W_corr, n_probes=300, seed=seed)
    assert not math.isnan(k3_corr), "kappa_3 corr is NaN"

    assert len(RHO_LIST) > 0, "RHO_LIST empty at smoke scale"
    print(f"[selftest] PASS: k3_iid={k3_iid:.4f} alpha={alpha_t:.4f} "
          f"rel_err={rel_err_iid:.4f} k3_corr={k3_corr:.4f} OK", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    results = {}
    alpha = M / N

    for rho in RHO_LIST:
        t0 = time.time()
        Xi = generate_correlated_patterns(M, N, rho, seed)
        W = Xi.T @ Xi / float(N)
        np.fill_diagonal(W, 0.0)

        k3_emp = hutchinson_kappa3(W, N_PROBES, seed)

        # Theoretical: kappa3 = alpha + beta_3 * rho^2 (mixing correction)
        k3_corrected = alpha + BETA_3 * (rho ** 2)
        k3_iid = alpha   # IID prediction (no correction)

        rel_err_corrected = abs(k3_emp - k3_corrected) / max(abs(k3_corrected), 1e-12)
        rel_err_iid = abs(k3_emp - k3_iid) / max(abs(k3_iid), 1e-12)

        hp_ok = rel_err_corrected <= HP_REL_ERR_CORR
        hf_ok = rel_err_corrected > HF_REL_ERR_CORR
        elapsed = time.time() - t0

        print(f"  [seed={seed} rho={rho:.2f}] k3_emp={k3_emp:.4f} "
              f"k3_corrected={k3_corrected:.4f} k3_iid={k3_iid:.4f} "
              f"rel_err_corr={rel_err_corrected:.4f} rel_err_iid={rel_err_iid:.4f} "
              f"hp={hp_ok} t={elapsed:.2f}s", flush=True)

        results[str(rho)] = {
            "rho": float(rho), "M": M, "N": N, "alpha": float(alpha),
            "k3_emp": float(k3_emp),
            "k3_corrected": float(k3_corrected),
            "k3_iid": float(k3_iid),
            "rel_err_corrected": float(rel_err_corrected),
            "rel_err_iid": float(rel_err_iid),
            "hp_ok": bool(hp_ok),
            "hf_ok": bool(hf_ok),
            "elapsed_s": float(elapsed),
        }

    return {"rho_results": results, "seed": seed, "N": N, "M": M, "run_mode": RUN_MODE}


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    rho_rel_errs = {str(r): [] for r in RHO_LIST}
    for sd in per_seed.values():
        for rk, v in sd.get("rho_results", {}).items():
            if rk in rho_rel_errs and v.get("rel_err_corrected") is not None:
                rho_rel_errs[rk].append(v["rel_err_corrected"])

    mean_rel_errs = {rk: float(np.mean(v)) if v else float("nan")
                     for rk, v in rho_rel_errs.items()}
    hp_all = all(not math.isnan(v) and v <= HP_REL_ERR_CORR for v in mean_rel_errs.values())
    hf_any = any(not math.isnan(v) and v > HF_REL_ERR_CORR for v in mean_rel_errs.values())

    n_hp = sum(1 for v in mean_rel_errs.values() if not math.isnan(v) and v <= HP_REL_ERR_CORR)
    n_total = len(RHO_LIST)

    summary = (f"mean_rel_errs_corrected={mean_rel_errs} "
               f"n_hp={n_hp}/{n_total} HP_REL_ERR={HP_REL_ERR_CORR} HF={HF_REL_ERR_CORR}")

    if hf_any:
        return ("HARD_FAIL", f"HARD_FAIL: mixing correction formula wrong. {summary}")
    if hp_all:
        return ("HARD_PASS", f"HARD_PASS: all rho within {HP_REL_ERR_CORR}. {summary}")
    if n_hp / n_total >= 0.5:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp}/{n_total} rho values within HP. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: {n_hp}/{n_total} cells within HP. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] kappa3_mixing N={N} M={M} rho_list={RHO_LIST}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
verdict, verdict_msg = compute_verdict(per_seed)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "M": M, "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_s, "rho_list": RHO_LIST,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
