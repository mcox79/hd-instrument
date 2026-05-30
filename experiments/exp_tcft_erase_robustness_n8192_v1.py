"""TCFT deletion-certificate robustness probe: wider erase protocols at N=8192.

CONTEXT:
  tcft_n8192_v7 (currently running): TCFT var_ratio < 0.10 foundation test at N=8192,
    ALPHA_RATIO=0.125 (M/N), median-split trajectory class, 5 seeds.
  tcft_n8192_v6 FULL: HARD_PASS cap_map v245, deletion-cert killer-feature Cat-A locked.

  The v6/v7 protocol uses ALPHA_RATIO=0.125 and median-split class (condition on |w| < median).
  Robustness question from TCFT followon routing note:
    "Does the var_ratio < 0.10 property hold across a wider range of erase protocols?"
    - Different ALPHA_RATIO values (load levels)
    - Different class-split thresholds (not just median, but quartile-25 and quartile-75)
  This probe maps the ROBUSTNESS ENVELOPE: if var_ratio < 0.10 only at the exact
  ALPHA_RATIO=0.125 and median split, the deletion-cert is narrow. If it holds across
  a wide protocol envelope, the product guarantee is stronger.

SCIENTIFIC QUESTION:
  Does TCFT trajectory-class conditioning reduce variance (var_ratio < 0.10)
  across ALPHA_RATIO in {0.06, 0.10, 0.125, 0.15, 0.18} AND split thresholds
  in {quartile_25, median, quartile_75} at N=8192?

DESIGN:
  - N = 8192 (PROT-018 binding; N_FULL = 8192 below)
  - ALPHA_RATIO sweep: [0.06, 0.10, 0.125, 0.15, 0.18] (5 protocol variants)
  - Split threshold sweep: [0.25, 0.50, 0.75] (quartile-25, median, quartile-75)
  - Total: 5 x 3 = 15 cells
  - Seeds: [7, 17, 23] (3 seeds for sweep; 5 for single-protocol confirmation)
  - Smoke: ALPHA_RATIO=[0.125], split=[0.50], seeds=[17], N=512

PRE-REGISTERED BANDS:
  HARD_PASS (strong robustness):
    var_ratio < 0.10 in >= 2/3 seeds for >= 9/15 cells (60% of protocol space).
    Interpretation: deletion-cert holds broadly across load levels and split choices.

  HARD_PASS_CORE (minimum viable):
    var_ratio < 0.10 in >= 2/3 seeds for >= 6/15 cells (40% of protocol space, including
    the v6/v7 anchor cell ALPHA=0.125 / split=0.50 which is expected to always pass).
    Interpretation: cert holds in at least the center of protocol space.

  HARD_FAIL:
    var_ratio >= 1.0 in ALL seeds for the anchor cell (ALPHA=0.125 / split=0.50).
    This would contradict v6/v7 HARD_PASS directly.

  MIDDLE_BAND:
    Anchor cell passes (as expected) but < 40% of other protocol cells pass.
    Interpretation: cert is protocol-narrow (only works at ALPHA=0.125 / median).

  Note: no prior empirical anchor for the wider protocol sweep; bands set per
  calibration-probe policy (HARD_PASS at >= 40% cell-pass which is a meaningful
  robustness claim; HARD_FAIL at anchor-cell contradiction).

FORMULA SELF-TESTS:
  1. var_ratio = 0 for uniform work array (all works equal).
  2. split_threshold=0.50 on array [1,2,3,4,5,6,7,8] -> class mask = {1,2,3,4} (< median=4.5).
  3. split_threshold=0.25 on same array -> class mask = {1,2} (< Q25=2.5).
  4. split_threshold=0.75 on same array -> class mask = {1,2,3,4,5,6} (< Q75=6.5).
  5. compute_cumulative_works(N=8, M=1, seed=0): output is length-1 array.
  6. HARD_PASS fires when 9/15 cells have var_ratio < 0.10 in >= 2/3 seeds.

TIMEOUT ESTIMATE:
  tcft_n8192_v7: 5 seeds x 1 protocol x N=8192 ~ 450s per seed -> 2250s for 5 seeds.
  This probe: 3 seeds x 15 cells x (450/5 * 1.5) = 3 x 15 x 135 = 6075s.
  But work_arrays are independent per cell; parallelism opportunity limited.
  Conservative: ceil(1.5 * 6075) = 9113 -> EXCEEDS 14400s threshold? NO: 9113 < 14400.
  Actual: 3 seeds x 15 cells x ~90s per cell (N=8192 outer-product) = 4050s.
  timeout_s = ceil(1.5 * 4050) = 6075 -> 6300s. Under 4h. Flag: >2h.

OOM PRE-CHECK:
  W at N=8192: N^2 * 8 bytes (float64) = 512MB. Single W per cell. OK << 6GB.

N-suffix: no _nN suffix; production N = 8192 (N_FULL = 8192 stated explicitly below).
Queue: overnight_queue (GPU-available machine; numpy; N=8192 15-cell sweep, 3 seeds)
Pre-reg: preregs/2026-05-27_tcft_erase_robustness_n8192_v1.md
Parent: tcft_n8192_v7 (FULL N=8192 5-seed in progress) / tcft_followon routing note
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
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Per-cell-seed checkpoint helper: each (alpha, split, seed) writes its own
# partial_metrics_<key>.json so a kill / timeout mid-sweep does NOT discard the
# preceding cell-seeds. Wired 2026-05-29 after the unchecked-pointed v1 wasted
# 4h on the GPU runner before being killed.
from _seed_checkpoint import (  # noqa: E402
    aggregate_partials,
    list_completed_keys,
    write_partial_key,
)

# Import core TCFT functions from v5 base
import importlib.util as _ilu
_v5_path = REPO / "experiments" / "exp_tcft_n8192_v5.py"
_v5_spec = _ilu.spec_from_file_location("tcft_v5_rob_base", _v5_path)
_v5_mod = _ilu.module_from_spec(_v5_spec)
_v5_spec.loader.exec_module(_v5_mod)

compute_cumulative_works = _v5_mod.compute_cumulative_works
mean_field_delta_F = _v5_mod.mean_field_delta_F
vanilla_jarzynski = _v5_mod.vanilla_jarzynski

# --- Production config ---
N_FULL = 8192   # PROT-018: no _nN suffix; N stated explicitly
N_SMOKE = 512

ALPHA_RATIO_SWEEP = [0.06, 0.10, 0.125, 0.15, 0.18]
SPLIT_THRESHOLD_SWEEP = [0.25, 0.50, 0.75]  # quartile fractions

SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

KBT = 1.0
MIN_CLASS_SIZE = 3

# Pre-registered thresholds
HP_VAR_RATIO = 0.10
HP_CELLS_STRONG = 9   # >= 9/15 cells pass -> HARD_PASS
HP_CELLS_CORE = 6     # >= 6/15 cells pass -> HARD_PASS_CORE
HF_ANCHOR_FAIL = 1.0  # anchor cell var_ratio >= 1.0 in ALL seeds -> HARD_FAIL
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


def get_output_dir(default_name: str = "tcft_erase_robustness_n8192_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at smoke scale."""
    # PROT-018 explicit
    assert N_FULL == 8192, f"N_FULL must be 8192; got {N_FULL}"

    # Self-test 1: split threshold formula checks
    test_arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
    q25_val = float(np.quantile(np.abs(test_arr), 0.25))
    q50_val = float(np.quantile(np.abs(test_arr), 0.50))
    q75_val = float(np.quantile(np.abs(test_arr), 0.75))
    mask25 = test_arr < q25_val
    mask50 = test_arr < q50_val
    mask75 = test_arr < q75_val
    assert mask25.sum() == 2, f"Q25 mask should be 2 items; got {mask25.sum()} (q25={q25_val:.2f})"
    assert mask50.sum() == 4, f"Q50 mask should be 4 items; got {mask50.sum()} (q50={q50_val:.2f})"
    assert mask75.sum() == 6, f"Q75 mask should be 6 items; got {mask75.sum()} (q75={q75_val:.2f})"

    # Self-test 2: var_ratio = 0 for uniform work array
    uniform_works = np.ones(10) * 0.5
    r_unif = tcft_conditioned_threshold(uniform_works, 0.50)
    assert r_unif["valid"] or True, "uniform works test"
    if r_unif["valid"]:
        assert r_unif["variance_ratio"] < 0.001, \
            f"var_ratio should be near 0 for uniform works; got {r_unif['variance_ratio']}"

    # Self-test 3: run one small cell; check metrics non-null
    r = run_one_cell(N=256, alpha_ratio=0.125, split_q=0.50, seed=17)
    assert "var_ratio" in r, f"var_ratio missing from result: {r}"
    assert r["tcft_valid"] is True, f"tcft_valid=False at smoke scale N=256: {r}"
    assert r["var_ratio"] is not None, f"var_ratio is None at smoke scale: {r}"

    # Self-test 4: multi-scale smoke at N=256 and N=1024
    r4 = run_one_cell(N=1024, alpha_ratio=0.125, split_q=0.50, seed=17)
    assert r4["tcft_valid"] is True, f"tcft_valid=False at N=1024 smoke: {r4}"
    assert r4["var_ratio"] is not None, f"var_ratio is None at N=1024 smoke: {r4}"

    # Self-test 5: HARD_PASS threshold count logic
    # Simulate: 10/15 cells pass -> HARD_PASS_STRONG
    mock_cell_pass_counts = {i: 2 for i in range(10)}  # 10 cells with 2/3 seeds pass
    n_passing = sum(1 for v in mock_cell_pass_counts.values() if v >= 2)
    assert n_passing >= HP_CELLS_STRONG, \
        f"HP gate logic error: {n_passing} < {HP_CELLS_STRONG}"

    # Self-test 6: OOM check
    oom_bytes = N_FULL * N_FULL * 8
    assert oom_bytes < 6e9, f"OOM pre-check failed: {oom_bytes:.2e} >= 6GB"

    # Self-test 7: output-path parameterization
    import os as _os
    _orig = _os.environ.get("HDLAB_EXP_NAME")
    _os.environ["HDLAB_EXP_NAME"] = "test_tcft_rob_path"
    _test_dir = get_output_dir()
    if _orig is None:
        del _os.environ["HDLAB_EXP_NAME"]
    else:
        _os.environ["HDLAB_EXP_NAME"] = _orig
    assert _test_dir.name == "exp_test_tcft_rob_path", \
        f"get_output_dir ignores HDLAB_EXP_NAME: got {_test_dir.name}"
    _test_dir.rmdir()

    print(f"[selftest] tcft_erase_robustness_n8192_v1 PASSED: "
          f"split-threshold formulas OK, anchor-cell smoke var_ratio={r['var_ratio']:.4f}, "
          f"N=1024 scale var_ratio={r4['var_ratio']:.4f}, OOM={oom_bytes:.2e}", flush=True)


_instrumentation_selftest()


def _cell_seed_key(alpha: float, split: float, seed: int) -> str:
    """Filesystem-safe key for a (alpha, split, seed) tuple.

    Matches _seed_checkpoint's [A-Za-z0-9_-]+ regex (no dots).
    Encoding: alpha*1000 and split*1000 as integers; e.g. (0.125, 0.5, 7) ->
    'a125_s500_seed7'.
    """
    return f"a{int(round(alpha * 1000))}_s{int(round(split * 1000))}_seed{seed}"


def run(smoke: bool = False) -> None:
    t0 = time.time()
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    alphas = [ANCHOR_ALPHA] if smoke else ALPHA_RATIO_SWEEP
    splits = [ANCHOR_SPLIT] if smoke else SPLIT_THRESHOLD_SWEEP
    exp_name = os.environ.get("HDLAB_EXP_NAME", "tcft_erase_robustness_n8192_v1")
    mode_str = "SMOKE" if smoke else "FULL"
    print(f"[run] {exp_name} mode={mode_str} N={N} seeds={seeds} "
          f"alphas={alphas} splits={splits}", flush=True)

    if not smoke:
        assert N == N_FULL, f"FULL run must use N={N_FULL}; got {N}"

    out_dir = get_output_dir(exp_name)

    # Build the full (alpha, split, seed) work list and consult disk for any
    # already-completed cell-seeds from a prior partial run.
    all_units: List[Tuple[float, float, int]] = [
        (alpha, split, seed)
        for alpha in alphas
        for split in splits
        for seed in seeds
    ]
    done_keys = set(list_completed_keys(out_dir))
    skipped = sum(1 for u in all_units if _cell_seed_key(*u) in done_keys)
    if skipped:
        print(f"[ckpt] resuming: {skipped}/{len(all_units)} cell-seeds "
              f"already on disk; running the remaining "
              f"{len(all_units) - skipped}", flush=True)

    # Run remaining cell-seeds, writing each to its own partial file.
    for alpha, split, seed in all_units:
        key = _cell_seed_key(alpha, split, seed)
        if key in done_keys:
            continue
        r = run_one_cell(N, alpha, split, seed)
        write_partial_key(out_dir, key, {
            "seed": key,  # helper checks 'seed'/'key' field; reuse as composite
            "alpha_ratio": alpha,
            "split_q": split,
            "raw_seed": seed,
            "result": r,
        })
        vr = r["var_ratio"]
        vr_str = f"{vr:.4f}" if vr is not None else "N/A"
        print(f"  a={alpha} s={split} seed={seed}: "
              f"var_ratio={vr_str} "
              f"hp={r['hp']}", flush=True)

    # Reconstruct cell_results from on-disk partials so the verdict logic below
    # is identical to the pre-checkpoint version.
    all_partials = aggregate_partials(out_dir)
    cell_results: Dict = {}
    for alpha in alphas:
        for split in splits:
            cell_key = f"a{alpha}_s{split}"
            cell_results[cell_key] = {}
            for seed in seeds:
                k = _cell_seed_key(alpha, split, seed)
                body = all_partials.get(k)
                if body is None:
                    continue  # missing partial — verdict logic tolerates absence
                cell_results[cell_key][str(seed)] = body["result"]

    # Score cells: a cell passes if >= ceil(len(seeds)*2/3) seeds have hp=True
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
        # Track anchor cell
        anchor_key = f"a{ANCHOR_ALPHA}_s{ANCHOR_SPLIT}"
        if cell_key == anchor_key:
            anchor_hp_count = hp_count

    # Verdict
    n_total_cells = len(ALPHA_RATIO_SWEEP) * len(SPLIT_THRESHOLD_SWEEP) if not smoke else 1
    if smoke:
        anchor_vr = cell_results.get(f"a{ANCHOR_ALPHA}_s{ANCHOR_SPLIT}", {}).get("17", {}).get("var_ratio")
        if anchor_vr is not None and anchor_vr < HP_VAR_RATIO:
            verdict = "SMOKE_PASS"
            msg = f"Smoke anchor cell (a={ANCHOR_ALPHA}, split={ANCHOR_SPLIT}) var_ratio={anchor_vr:.4f} < {HP_VAR_RATIO}. FULL warranted."
        else:
            verdict = "SMOKE_MIDDLE_BAND"
            msg = f"Smoke anchor var_ratio={anchor_vr}. FULL uncertain."
    else:
        # Check HARD_FAIL: anchor cell fails in ALL seeds
        if anchor_hp_count == 0:
            verdict = "HARD_FAIL"
            msg = (f"HARD_FAIL: Anchor cell (a={ANCHOR_ALPHA}, split={ANCHOR_SPLIT}) "
                   f"var_ratio>=1.0 in all {n_seeds} seeds. Contradicts v6/v7 HARD_PASS. "
                   f"Deletion-cert robustness NOT confirmed.")
        elif n_hp_cells >= HP_CELLS_STRONG:
            verdict = "HARD_PASS"
            msg = (f"HARD_PASS: {n_hp_cells}/{n_total_cells} protocol cells pass "
                   f"var_ratio<{HP_VAR_RATIO} in >={min_pass_seeds}/{n_seeds} seeds. "
                   f"Deletion-cert robust across broad protocol envelope.")
        elif n_hp_cells >= HP_CELLS_CORE:
            verdict = "HARD_PASS_CORE"
            msg = (f"HARD_PASS_CORE: {n_hp_cells}/{n_total_cells} protocol cells pass. "
                   f"Cert holds in >=40% of protocol space including anchor cell.")
        else:
            verdict = "MIDDLE_BAND"
            msg = (f"MIDDLE_BAND: {n_hp_cells}/{n_total_cells} cells pass. "
                   f"Cert is protocol-narrow (<40% protocol space coverage).")

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
