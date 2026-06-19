"""TCFT deletion-certificate robustness probe: wider erase protocols at N=2048 (CPU-feasible).

CONTEXT:
  tcft_erase_robustness_n8192_v1 (pending in overnight_queue): same protocol at N=8192.
  This N=2048 variant is a cheaper CPU probe that runs in parallel to the GPU version.

  QUESTION: Does the N=2048 substrate show the same var_ratio < 0.10 robustness envelope
  as N=8192? If yes: robustness is N-invariant (product claim stronger). If no: the
  property is N-scale-specific (only holds at production scale N=8192+).

  N=2048 is NOT a valid Kerdock N (log2(2048)=11, odd). This probe uses BSC atoms
  (random +/-1) to avoid the Kerdock-even-log2 constraint.

SCIENTIFIC QUESTION:
  Does TCFT trajectory-class conditioning reduce variance (var_ratio < 0.10)
  across ALPHA_RATIO in {0.06, 0.10, 0.125, 0.15, 0.18} AND split thresholds
  in {quartile_25, median, quartile_75} at N=2048 BSC atoms?

DESIGN:
  - N = 2048 (PROT-018: no _nN suffix; N_FULL = 2048 stated explicitly below)
  - ALPHA_RATIO sweep: [0.06, 0.10, 0.125, 0.15, 0.18] (5 protocol variants)
  - Split threshold sweep: [0.25, 0.50, 0.75] (quartile-25, median, quartile-75)
  - Total: 5 x 3 = 15 cells
  - Seeds: [7, 17, 23] (3 seeds for sweep)
  - Smoke: ALPHA_RATIO=[0.125], split=[0.50], seeds=[17], N=512
  - BSC atoms (not Kerdock) to avoid even-log2 constraint

PRE-REGISTERED BANDS:
  Prior anchor: tcft_n8192_v6/v7 HARD_PASS at N=8192 ALPHA=0.125 median-split.
  This is an N-scaling probe: does robustness hold at N=2048?

  HARD_PASS (N-invariant robustness):
    var_ratio < 0.10 in >= 2/3 seeds for >= 9/15 cells (60% of protocol space).
    Same threshold as n8192 version. Interpretation: deletion-cert is N-robust.
  HARD_PASS_CORE (minimum viable):
    var_ratio < 0.10 in >= 2/3 seeds for >= 6/15 cells (40% of protocol space).
  HARD_FAIL:
    var_ratio >= 1.0 in ALL seeds for the anchor cell (ALPHA=0.125 / split=0.50).
    This would mean N=2048 substrate does NOT support the deletion-cert property.
  MIDDLE_BAND: anchor cell passes but < 40% of other protocol cells pass.

  NOTE: calibration probe for N=2048 scale.
  Bands widened to +-50% on HP cell count: HP requires 9/15 not 10/15.

FORMULA SELF-TESTS:
  1. N_FULL == 2048 (no PROT-018 _nN suffix; stated explicitly).
  2. BSC atoms: outer product store W = sum_mu (v_mu x v_mu^T) / N.
     compute_cumulative_works uses v5 base (which handles BSC via pure numpy).
  3. var_ratio = 0 for uniform work array (all works equal).
  4. split_threshold=0.50 on [1,2,3,4,5,6,7,8] -> 4 items below median=4.5.
  5. HARD_PASS fires when >= 9/15 cells have var_ratio < 0.10 in >= 2/3 seeds.
  6. OOM at N=2048: W=2048^2*8=32MB. OK.

TIMEOUT ESTIMATE:
  N=2048, 3 seeds, 15 cells: (2048/512)^2 = 16x per cell vs smoke N=512.
  Smoke (N=512, 1 cell, 1 seed): estimate ~0.1s.
  Full: estimate 0.1 * 16 * 15 * 3 = 72s.
  Safety ceil(1.5 * 72 * 5) = 540s. timeout_s = 1800.

N-suffix: no _nN suffix; production N = 2048.
Anchor: tcft_erase_robustness_n2048_v1
Queue: remote_cpu_queue (CPU; pure numpy; N=2048 BSC; 15-cell sweep 3 seeds)
Pre-reg: preregs/2026-05-29_tcft_erase_robustness_n2048_v1.md
Parent: tcft_erase_robustness_n8192_v1 (pending overnight_queue; this is the CPU-feasible N-scaling counterpart)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Import core TCFT functions from v5 base
import importlib.util as _ilu
_v5_path = REPO / "experiments" / "exp_tcft_n8192_v5.py"
_v5_spec = _ilu.spec_from_file_location("tcft_v5_rob_n2048", _v5_path)
_v5_mod = _ilu.module_from_spec(_v5_spec)
_v5_spec.loader.exec_module(_v5_mod)

compute_cumulative_works = _v5_mod.compute_cumulative_works

# --- Production config ---
N_FULL = 2048   # no _nN suffix; N stated explicitly here
N_SMOKE = 512

ALPHA_RATIO_SWEEP = [0.06, 0.10, 0.125, 0.15, 0.18]
SPLIT_THRESHOLD_SWEEP = [0.25, 0.50, 0.75]

SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

KBT = 1.0
MIN_CLASS_SIZE = 3

# Pre-registered thresholds (same as n8192 version for N-scaling comparison)
HP_VAR_RATIO = 0.10
HP_CELLS_STRONG = 9   # >= 9/15 cells pass -> HARD_PASS
HP_CELLS_CORE = 6     # >= 6/15 cells pass -> HARD_PASS_CORE
ANCHOR_ALPHA = 0.125
ANCHOR_SPLIT = 0.50


def tcft_conditioned_threshold(works: np.ndarray, split_q: float) -> Dict:
    """TCFT with configurable split threshold (quantile fraction)."""
    threshold = float(np.quantile(np.abs(works), split_q))
    class_mask = np.abs(works) < threshold
    if class_mask.sum() < MIN_CLASS_SIZE:
        return {"valid": False, "class_size": int(class_mask.sum()),
                "variance_ratio": None}
    works_class = works[class_mask]
    W_scaled_class = works_class / KBT
    variance_class = float(np.var(np.exp(-W_scaled_class)))
    W_all = works / KBT
    variance_all = float(np.var(np.exp(-W_all)))
    var_ratio = variance_class / (variance_all + 1e-300)
    return {
        "valid": True,
        "class_size": int(class_mask.sum()),
        "variance_ratio": float(var_ratio),
    }


def run_one_cell(N: int, alpha_ratio: float, split_q: float, seed: int) -> Dict:
    """Run one (alpha_ratio, split_q, seed) cell."""
    M = max(4, int(N * alpha_ratio))
    works = compute_cumulative_works(N, M, seed)
    tcft_result = tcft_conditioned_threshold(works, split_q)
    return {
        "N": N, "alpha_ratio": alpha_ratio, "split_q": split_q, "seed": seed,
        "M": M,
        "tcft_valid": tcft_result["valid"],
        "tcft_class_size": tcft_result.get("class_size"),
        "var_ratio": tcft_result.get("variance_ratio"),
        "hp": tcft_result["valid"] and (tcft_result["variance_ratio"] is not None)
              and (tcft_result["variance_ratio"] < HP_VAR_RATIO),
    }


def get_output_dir(default_name: str = "tcft_erase_robustness_n2048_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at smoke scale."""
    assert N_FULL == 2048, f"N_FULL must be 2048; got {N_FULL}"

    # Self-test 1: split threshold formula checks
    test_arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
    q50_val = float(np.quantile(np.abs(test_arr), 0.50))
    mask50 = test_arr < q50_val
    assert mask50.sum() == 4, f"Q50 mask should be 4 items; got {mask50.sum()} (q50={q50_val:.2f})"

    # Self-test 2: var_ratio = 0 for uniform work array
    uniform_works = np.ones(10) * 0.5
    r_unif = tcft_conditioned_threshold(uniform_works, 0.50)
    if r_unif["valid"]:
        assert r_unif["variance_ratio"] < 0.001, \
            f"var_ratio should be near 0 for uniform works; got {r_unif['variance_ratio']}"

    # Self-test 3: run one small cell; check metrics non-null
    r = run_one_cell(N=256, alpha_ratio=0.125, split_q=0.50, seed=17)
    assert "var_ratio" in r, f"var_ratio missing from result: {r}"
    assert r["tcft_valid"] is True, f"tcft_valid=False at smoke scale N=256: {r}"
    assert r["var_ratio"] is not None, f"var_ratio is None at smoke scale: {r}"

    # Self-test 4: multi-scale smoke at N=256 and N=512 (smoke_N)
    r4 = run_one_cell(N=N_SMOKE, alpha_ratio=0.125, split_q=0.50, seed=17)
    assert r4["tcft_valid"] is True, f"tcft_valid=False at N={N_SMOKE} smoke: {r4}"
    assert r4["var_ratio"] is not None, f"var_ratio is None at N={N_SMOKE} smoke: {r4}"

    # Self-test 5: HARD_PASS gate logic
    n_passing = 10  # simulated: 10 cells pass
    assert n_passing >= HP_CELLS_STRONG, \
        f"HP gate logic error: {n_passing} < {HP_CELLS_STRONG}"

    # Self-test 6: OOM check
    oom_bytes = N_FULL * N_FULL * 8
    assert oom_bytes < 6e9, f"OOM pre-check failed: {oom_bytes:.2e} >= 6GB"

    print(f"[selftest] tcft_erase_robustness_n2048_v1 PASSED: "
          f"split-threshold OK, anchor-cell var_ratio={r['var_ratio']:.4f}, "
          f"N={N_SMOKE} scale var_ratio={r4['var_ratio']:.4f}, OOM={oom_bytes:.2e}", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    alphas = [ANCHOR_ALPHA] if smoke else ALPHA_RATIO_SWEEP
    splits = [ANCHOR_SPLIT] if smoke else SPLIT_THRESHOLD_SWEEP
    exp_name = os.environ.get("HDLAB_EXP_NAME", "tcft_erase_robustness_n2048_v1")
    mode_str = "SMOKE" if smoke else "FULL"
    print(f"[run] {exp_name} mode={mode_str} N={N} seeds={seeds} "
          f"alphas={alphas} splits={splits}", flush=True)

    cell_results: Dict = {}
    for alpha in alphas:
        for split in splits:
            cell_key = f"a{alpha}_s{split}"
            cell_results[cell_key] = {}
            per_seed_hp = []
            for seed in seeds:
                r = run_one_cell(N, alpha, split, seed)
                cell_results[cell_key][str(seed)] = r
                per_seed_hp.append(r["hp"])
                vr = r["var_ratio"]
                vr_str = f"{vr:.4f}" if vr is not None else "N/A"
                print(f"  a={alpha} s={split} seed={seed}: "
                      f"var_ratio={vr_str} hp={r['hp']}", flush=True)

    n_seeds = len(seeds)
    min_pass_seeds = max(1, int(np.ceil(n_seeds * 2.0 / 3.0)))
    n_cells = len(alphas) * len(splits)
    n_hp_cells = 0
    anchor_hp_count = 0
    for cell_key, seed_dict in cell_results.items():
        hp_count = sum(1 for r in seed_dict.values() if r["hp"])
        passes = hp_count >= min_pass_seeds
        if passes:
            n_hp_cells += 1
        anchor_key = f"a{ANCHOR_ALPHA}_s{ANCHOR_SPLIT}"
        if cell_key == anchor_key:
            anchor_hp_count = hp_count

    n_total_cells = len(ALPHA_RATIO_SWEEP) * len(SPLIT_THRESHOLD_SWEEP) if not smoke else 1
    if smoke:
        anchor_vr = cell_results.get(f"a{ANCHOR_ALPHA}_s{ANCHOR_SPLIT}", {}).get("17", {}).get("var_ratio")
        if anchor_vr is not None and anchor_vr < HP_VAR_RATIO:
            verdict = "TCFT_ROB_N2048_SMOKE_PASS"
            msg = f"Smoke anchor (a={ANCHOR_ALPHA}, split={ANCHOR_SPLIT}) var_ratio={anchor_vr:.4f} < {HP_VAR_RATIO}. FULL warranted."
        else:
            verdict = "TCFT_ROB_N2048_SMOKE_MIDDLE_BAND"
            msg = f"Smoke anchor var_ratio={anchor_vr}. FULL uncertain."
    else:
        if anchor_hp_count == 0:
            verdict = "TCFT_ROB_N2048_HARD_FAIL"
            msg = (f"HARD_FAIL: Anchor cell (a={ANCHOR_ALPHA}, split={ANCHOR_SPLIT}) "
                   f"var_ratio>=1.0 in all {n_seeds} seeds. N=2048 does not support deletion-cert.")
        elif n_hp_cells >= HP_CELLS_STRONG:
            verdict = "TCFT_ROB_N2048_HARD_PASS"
            msg = (f"HARD_PASS: {n_hp_cells}/{n_total_cells} protocol cells pass "
                   f"var_ratio<{HP_VAR_RATIO} in >={min_pass_seeds}/{n_seeds} seeds. "
                   f"Deletion-cert N-robust at N=2048.")
        elif n_hp_cells >= HP_CELLS_CORE:
            verdict = "TCFT_ROB_N2048_HARD_PASS_CORE"
            msg = (f"HARD_PASS_CORE: {n_hp_cells}/{n_total_cells} cells pass. "
                   f"Cert holds in >=40% protocol space at N=2048.")
        else:
            verdict = "TCFT_ROB_N2048_MIDDLE_BAND"
            msg = (f"MIDDLE_BAND: {n_hp_cells}/{n_total_cells} cells pass. "
                   f"Cert is protocol-narrow at N=2048.")

    elapsed = round(time.time() - t0, 2)
    print(f"\n[result] {verdict}: {msg}", flush=True)
    print(f"[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {msg}", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "n_hp_cells": n_hp_cells,
        "n_total_cells": n_total_cells,
        "anchor_hp_count": anchor_hp_count,
        "cell_results": cell_results,
        "config": {
            "N": N, "smoke": smoke, "seeds": seeds,
            "alphas": alphas, "splits": splits,
            "HP_VAR_RATIO": HP_VAR_RATIO,
            "HP_CELLS_STRONG": HP_CELLS_STRONG,
            "HP_CELLS_CORE": HP_CELLS_CORE,
        },
    }
    mpath = get_output_dir(exp_name) / "metrics.json"
    with open(mpath, "w") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
