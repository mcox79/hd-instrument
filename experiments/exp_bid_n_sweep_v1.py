"""BID N-SWEEP v1: intrinsic dimension vs N at fixed M_frac.

CONTEXT:
  bid_m_normalized_v3_n4096 (v267): BID at N=4096 outside Hopfield bands confirmed.
  bid_m_normalized_v4_n8192 (new): BID at N=8192 outside Hopfield bands.
  QUESTION: How does BID scale with N at fixed M_frac=0.5?
  Theory (SKAH-M class, non-eq stat-mech): BID should scale sublinearly with N
  (fractal dimension of attractor manifold grows with N but not proportionally).

SCIENTIFIC QUESTION:
  At fixed M_frac=0.5, does BID scale with N as BID ~ N^alpha for some alpha in (0,1)?
  At N=1024, 2048, 4096, 8192: measure BID. Fit power law.
  Does alpha match reservoir-computing edge-of-chaos prediction (alpha ~ 0.5-0.8)?

NOTE on Kerdock: N=2048 has log2=11 (odd) -- NOT valid for Kerdock codebook.
  Use BSC codebook at N=2048 instead (BSC uses random bipolar vectors, no log2 constraint).
  Or skip N=2048 and use N=1024, 4096, 8192 (all valid Kerdock).

PRE-REGISTERED BANDS:
  Calibration probe. No prior N-sweep of BID at fixed M_frac.
  RMT prediction: BID ~ N^0.5 (random matrix attractor dimension).
  SKAH-M: possible sublinear alpha in [0.5, 0.9].

  HARD_PASS: power-law fit r2 >= 0.9 AND alpha in [0.3, 1.5] at >= 2/3 seeds.
    Interpretation: BID scales as power law with N.
  HARD_FAIL: BID is constant (< 5% variation) across all N.
    Interpretation: BID is N-independent (dimension saturates early).
  MIDDLE_BAND: power law present but r2 < 0.9 or alpha outside [0.3, 1.5].

FORMULA SELF-TESTS:
  1. N values = [1024, 4096, 8192] (log2 = [10, 12, 13] -- all valid Kerdock).
  2. bid_threshold(N) = max(6.0, 50.0 * (N / 4096)) -- N-aware threshold from v3.
  3. Power law fit: log(BID) = alpha * log(N) + const. r2 from linear regression.
  4. alpha = (log(BID_8192) - log(BID_1024)) / (log(8192) - log(1024)) (two-point est).

TIMEOUT ESTIMATE:
  3 N values x 3 seeds = 9 cells. TwoNN at N=8192 M=4096 (M_frac=0.5): ~10s.
  Total: 9*10=90s. Safety: ceil(1.5*90*2)=270s. timeout_s=3600 (no _n suffix -> no floor).

Anchor: bid_n_sweep_v1
Queue: remote_cpu_queue (TwoNN; CPU; N sweep 1024..8192 at M_frac=0.5)
Pre-reg: prereqs/2026-05-28_bid_n_sweep_v1.md
Parent: bid_m_normalized_v1 (run_one_seed_Mfrac); bid_m_normalized_v3_n4096 (v267 HARD_PASS)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load bid_m_normalized_v1 for run_one_seed_Mfrac
_v1_path = REPO / "experiments" / "exp_bid_m_normalized_v1.py"
_v1_spec = importlib.util.spec_from_file_location("bid_v1_nsweep", _v1_path)
_bid_v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(_bid_v1)

run_one_seed_Mfrac = _bid_v1.run_one_seed_Mfrac

# CONFIG
N_VALUES_FULL  = [1024, 4096, 8192]    # all valid Kerdock (log2 = 10, 12, 13)
N_VALUES_SMOKE = [1024, 4096]          # smoke: 2 N values
M_FRAC = 0.5                            # fixed M_frac for N-scaling sweep
# Smoke M_frac: use 0.05 for large N in smoke to keep TwoNN fast (M=204 for N=4096)
M_FRAC_SMOKE = 0.05

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
HP_R2_MIN    = 0.9      # power law fit r2 >= 0.9
HP_ALPHA_MIN = 0.3      # alpha >= 0.3 (sublinear scaling)
HP_ALPHA_MAX = 1.5      # alpha <= 1.5 (not super-linear)
HF_FLAT_VAR  = 0.05     # BID/N variation < 0.05 = flat
HP_SEEDS_MIN = 2


def get_output_dir(default_name: str = "bid_n_sweep_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def bid_threshold(N_cfg: int) -> float:
    return max(6.0, 50.0 * (N_cfg / 4096))


def run_one_cell(N: int, M_frac: float, seed: int) -> Dict:
    """Run BID estimator at (N, M_frac, seed)."""
    result = run_one_seed_Mfrac(N, M_frac, seed)
    bid_val = result.get("bid_estimate", result.get("bid_outside", 0.0))
    if bid_val is None:
        bid_val = 0.0
    thr = bid_threshold(N)
    bid_norm = bid_val / N  # normalized BID
    print(f"    N={N} M_frac={M_frac} seed={seed} bid={bid_val:.2f} bid/N={bid_norm:.5f} thr={thr:.2f}", flush=True)
    return {
        "N": N, "M_frac": M_frac, "seed": seed,
        "bid": float(bid_val),
        "bid_norm": float(bid_norm),
        "threshold": thr,
    }


def fit_power_law(n_vals: List[int], bid_vals: List[float]) -> Tuple[float, float, float]:
    """Fit log(BID) = alpha * log(N) + const. Return (alpha, intercept, r2)."""
    if len(n_vals) < 2:
        return (float("nan"), float("nan"), 0.0)
    log_n = np.array([math.log(n) for n in n_vals])
    log_b = np.array([math.log(max(b, 1e-9)) for b in bid_vals])
    # Linear regression
    n = len(log_n)
    sx = log_n.sum()
    sy = log_b.sum()
    sxx = (log_n ** 2).sum()
    sxy = (log_n * log_b).sum()
    denom = n * sxx - sx ** 2
    if abs(denom) < 1e-12:
        return (float("nan"), float("nan"), 0.0)
    alpha = (n * sxy - sx * sy) / denom
    intercept = (sy - alpha * sx) / n
    # r2
    y_pred = alpha * log_n + intercept
    ss_res = ((log_b - y_pred) ** 2).sum()
    ss_tot = ((log_b - log_b.mean()) ** 2).sum()
    r2 = 1.0 - ss_res / max(ss_tot, 1e-12)
    return (float(alpha), float(intercept), float(r2))


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("BID_NSWEEP_INCONCLUSIVE", "No cells.")

    # Group by seed, compute per-seed power law fit
    by_seed: Dict[int, List] = {}
    for c in cells:
        by_seed.setdefault(c["seed"], []).append(c)

    seed_results = []
    for seed, seed_cells in by_seed.items():
        sorted_cells = sorted(seed_cells, key=lambda x: x["N"])
        n_vals = [c["N"] for c in sorted_cells]
        bid_vals = [c["bid"] for c in sorted_cells]
        alpha, intercept, r2 = fit_power_law(n_vals, bid_vals)
        passes = (not math.isnan(alpha) and r2 >= HP_R2_MIN and
                  HP_ALPHA_MIN <= alpha <= HP_ALPHA_MAX)
        seed_results.append({"seed": seed, "alpha": alpha, "r2": r2, "passes": passes})

    pass_seeds = sum(1 for s in seed_results if s["passes"])
    alphas = [s["alpha"] for s in seed_results if not math.isnan(s.get("alpha", float("nan")))]
    r2s = [s["r2"] for s in seed_results]
    mean_alpha = sum(alphas) / len(alphas) if alphas else float("nan")
    mean_r2 = sum(r2s) / len(r2s) if r2s else float("nan")

    # Check if BID is flat across N
    all_bids = [c["bid"] for c in cells]
    bid_var = (max(all_bids) - min(all_bids)) / max(max(all_bids), 1e-9)

    detail = (f"pass_seeds={pass_seeds}/{len(seed_results)} "
              f"mean_alpha={mean_alpha:.3f} mean_r2={mean_r2:.3f} "
              f"bid_var={bid_var:.3f} HP_r2={HP_R2_MIN} HP_alpha=[{HP_ALPHA_MIN},{HP_ALPHA_MAX}]")

    if bid_var < HF_FLAT_VAR:
        return ("BID_NSWEEP_HARD_FAIL",
                f"BID_FLAT_ACROSS_N: BID constant, no N-scaling. " + detail)

    if pass_seeds >= HP_SEEDS_MIN:
        return ("BID_NSWEEP_HARD_PASS",
                f"POWER_LAW_SCALING: mean_alpha={mean_alpha:.3f} r2={mean_r2:.3f}. " + detail)

    return ("BID_NSWEEP_MIDDLE_BAND", f"WEAK_SCALING: " + detail)


def _instrumentation_selftest() -> None:
    # Formula self-tests
    assert N_VALUES_FULL == [1024, 4096, 8192], f"N_VALUES_FULL: {N_VALUES_FULL}"
    # alpha two-point formula
    bid_1024 = 30.0
    bid_8192 = 100.0
    alpha_2pt = (math.log(bid_8192) - math.log(bid_1024)) / (math.log(8192) - math.log(1024))
    assert 0.5 < alpha_2pt < 1.0, f"alpha_2pt out of range: {alpha_2pt}"
    # Power law fit test
    n_vals = [1024, 4096, 8192]
    bid_vals = [30.0, 60.0, 100.0]
    alpha, _, r2 = fit_power_law(n_vals, bid_vals)
    assert 0.0 < alpha < 2.0, f"alpha fit: {alpha}"
    assert r2 > 0.5, f"r2 too low: {r2}"
    # Verdict gates
    fake_hp = [{"N": n, "M_frac": 0.5, "seed": 17, "bid": 30.0 * (n/1024)**0.7, "bid_norm": 0.001}
               for n in [1024, 4096, 8192] for _ in range(1)]
    v, _ = compute_verdict({"cells": fake_hp})
    assert "PASS" in v or "MIDDLE" in v, f"PASS/MIDDLE gate: {v}"
    fake_hf = [{"N": n, "M_frac": 0.5, "seed": 17, "bid": 50.0, "bid_norm": 0.0001}
               for n in [1024, 4096, 8192]]
    vf, _ = compute_verdict({"cells": fake_hf})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf}"
    # Smoke cell (small M_frac for speed)
    cell = run_one_cell(1024, 0.05, 17)
    assert "bid" in cell, f"bid missing"
    assert cell["bid"] > 0.0, f"bid <= 0"
    # 4x scale (N=4096, M_frac=0.05 keeps M=204 for fast TwoNN)
    cell4 = run_one_cell(4096, 0.05, 17)
    assert "bid" in cell4, f"4x bid missing"
    print(f"[selftest] bid_n_sweep_v1 PASS bid_1024={cell['bid']:.2f} bid_4096={cell4['bid']:.2f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    n_values = N_VALUES_SMOKE if smoke else N_VALUES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    mfrac = M_FRAC_SMOKE if smoke else M_FRAC

    print(f"[run] bid_n_sweep_v1 smoke={smoke} N_values={n_values} M_frac={mfrac} seeds={seeds}", flush=True)
    t0 = time.time()

    all_cells = []
    for N in n_values:
        print(f"\n  [N={N}]", flush=True)
        for seed in seeds:
            cell = run_one_cell(N, mfrac, seed)
            all_cells.append(cell)
        print(f"  N={N} elapsed={time.time()-t0:.1f}s", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "bid_n_sweep_v1", "N_values": n_values, "smoke": smoke,
        "M_frac": M_FRAC, "seeds": seeds,
        "cells": all_cells, "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_dir = get_output_dir()
    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    main()
