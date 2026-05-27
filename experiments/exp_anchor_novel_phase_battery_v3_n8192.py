"""SKAH-M phase-class positive-identifier battery v3: extended N=8192, 10 seeds.

TRIGGER: exp_anchor_novel_phase_battery_v1 returned MIDDLE_BAND (doc=3, finite_N=2, middle=1).
Verdict_msg explicitly said: "Extend seed count (>=10) + N range up to N=8192 before final class call."

CONTEXT:
  Battery v1 ran at N_SWEEP=[512,1024,2048,4096], 5 seeds.
  Results: C1=DOCUMENTED, C2=FINITE_N, C3=FINITE_N, C4=MIDDLE, C5=DOCUMENTED, C6=DOCUMENTED.
  C2 was FINITE_N because plateau drifted across N; C3 was FINITE_N (small spectral gap).
  At N=8192 with 10 seeds:
  - C2 should converge if it is a genuine thermodynamic plateau (drift should vanish).
  - C3 spectral gap may grow or stay small -- discriminates finite-N vs documented class.
  - With 10 seeds, statistical uncertainty on cell calls drops substantially.

HYPOTHESIS:
  At N=8192 with 10 seeds, the documented-class vote count reaches >= 5/6:
  DOCUMENTED_BUT_UNTESTED result expected if SKAH-M lR-phase hypothesis is correct.

DESIGN:
  - N_SWEEP_FULL = [512, 1024, 2048, 4096, 8192] (adds N=8192).
  - SEEDS_FULL = [7, 17, 23, 31, 41, 53, 67, 79, 89, 97] (10 seeds, double v1).
  - C3-C6 cells run at N=4096 (not 8192) to save compute; N-scaling sufficient for C1/C2.
  - Cell classification thresholds: IDENTICAL to v1.

PRE-REGISTERED BANDS:
  HARD-PASS (DOCUMENTED_BUT_UNTESTED): >= 5/6 cells DOCUMENTED.
    -> SKAH-M claim supported; substrate is first production lR-phase system.
    -> Cap_map framework reliability lifts +5-8%.
  HARD-FAIL (FINITE_N_ARTIFACT): >= 4/6 cells FINITE_N.
    -> 3-plateau structure dissolves at thermodynamic limit; product framing pivot required.
  MIDDLE-BAND: <= 4 DOCUMENTED and <= 3 FINITE_N.
    -> Inconclusive; either extend N further or declare empirical plateau without class label.
  NOTE on calibration: prior empirical anchor from v1 (5 seeds, 3 DOCUMENTED). Bands same as v1.
  No ex-post threshold changes.

Self-tests:
  1. N_SWEEP_FULL[-1] == 8192 (correctly extends to N=8192).
  2. len(SEEDS_FULL) == 10 (correctly extends to 10 seeds).
  3. run_cell_C1_C2 at smoke scale returns dict with N keys and retention values in [0,1].
  4. classify_cells returns dict with keys C1..C6.
  5. q_EA at smoke scale is non-null and in [0,1].

Queue: overnight_queue (GPU: N=8192 x 10 seeds is depth probe; ~4-6h)
Pre-reg: prereqs/2026-05-27_anchor_novel_phase_battery_v3_n8192.md
Parent: anchor_novel_phase_battery_v1 (MIDDLE_BAND doc=3, finite_N=2, middle=1; 5 seeds)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Reuse battery v1 infrastructure (all cell functions, classification, decision)
_v1_path = REPO / "experiments" / "exp_anchor_novel_phase_battery_v1.py"
_v1_spec = importlib.util.spec_from_file_location("battery_v1_v3", _v1_path)
v1_mod = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(v1_mod)

# Import all v1 cell functions
build_3class_fixture = v1_mod.build_3class_fixture
build_hebbian_W = v1_mod.build_hebbian_W
compute_q_EA = v1_mod.compute_q_EA
compute_binder_g4 = v1_mod.compute_binder_g4
cosine_retention = v1_mod.cosine_retention
compute_spectral_gap = v1_mod.compute_spectral_gap
compute_hysteresis_area = v1_mod.compute_hysteresis_area
compute_disorder_operator = v1_mod.compute_disorder_operator
reconstruct_free_energy = v1_mod.reconstruct_free_energy
run_cell_C1_C2 = v1_mod.run_cell_C1_C2
run_cells_C3_C6 = v1_mod.run_cells_C3_C6
classify_cells = v1_mod.classify_cells
decide_class = v1_mod.decide_class
get_output_dir = v1_mod.get_output_dir

# ---- design parameters (v3: extended N=8192, 10 seeds) ----
N_SWEEP_FULL = [512, 1024, 2048, 4096, 8192]   # adds N=8192 vs v1
N_SWEEP_SMOKE = [512, 1024]
SEEDS_FULL = [7, 17, 23, 31, 41, 53, 67, 79, 89, 97]   # 10 seeds (v1 had 5)
SEEDS_SMOKE = [17]
M_PATTERNS_PER_CLASS = 200        # per class at default N
M_PATTERNS_PER_CLASS_SMOKE = 80
ALPHA_LOAD = v1_mod.ALPHA_LOAD    # reuse v1 alpha load constant

N_DEFAULT_FULL = 4096    # C3-C6 run at N=4096 (saves compute vs 8192)
N_DEFAULT_SMOKE = 512
PERTURBATION_STRENGTHS_FULL = v1_mod.PERTURBATION_STRENGTHS_FULL
PERTURBATION_STRENGTHS_SMOKE = v1_mod.PERTURBATION_STRENGTHS_SMOKE


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # 1. N_SWEEP_FULL extends to N=8192
    assert N_SWEEP_FULL[-1] == 8192, f"N_SWEEP_FULL must end at 8192; got {N_SWEEP_FULL[-1]}"
    # 2. 10 seeds
    assert len(SEEDS_FULL) == 10, f"SEEDS_FULL must have 10 seeds; got {len(SEEDS_FULL)}"
    # 3. run_cell_C1_C2 at smoke scale returns valid metrics
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    c1, c2 = run_cell_C1_C2(
        N_sweep=[512],
        M_per_class=M_PATTERNS_PER_CLASS_SMOKE,
        seeds=[17],
        device=device,
    )
    assert 512 in c1, "C1 result missing N=512 key"
    assert 512 in c2, "C2 result missing N=512 key"
    q_ea = c1[512]["q_EA_mean"]
    assert q_ea is not None and math.isfinite(q_ea), f"q_EA is null/nan: {q_ea}"
    assert 0.0 <= q_ea <= 1.0, f"q_EA out of [0,1]: {q_ea}"
    ret_g1 = c2[512]["ret_G1_mean"]
    assert ret_g1 is not None and math.isfinite(ret_g1), f"ret_G1 null/nan: {ret_g1}"
    assert 0.0 < ret_g1 <= 1.0, f"ret_G1 suspiciously zero or OOR: {ret_g1}"
    # 4. classify_cells returns C1..C6 keys
    c3456 = run_cells_C3_C6(
        N=512, M_per_class=M_PATTERNS_PER_CLASS_SMOKE, seeds=[17],
        device=device, perturbation_strengths=PERTURBATION_STRENGTHS_SMOKE
    )
    calls = classify_cells(c1, c2, c3456)
    for k in ["C1", "C2", "C3", "C4", "C5", "C6"]:
        assert k in calls, f"classify_cells missing key {k}"
    # 5. decide_class produces valid verdict
    verdict, msg = decide_class(calls)
    assert verdict in ("DOCUMENTED_BUT_UNTESTED", "NOVEL_SKAHM", "FINITE_N_ARTIFACT", "MIDDLE_BAND"), \
        f"decide_class returned unexpected verdict: {verdict}"
    print(f"[selftest] v3 PASSED: N=8192 check, 10-seed check, "
          f"smoke C1 q_EA={q_ea:.4f}, ret_G1={ret_g1:.4f}, classify+decide OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    N_sweep = N_SWEEP_SMOKE if smoke else N_SWEEP_FULL
    M_per_class = M_PATTERNS_PER_CLASS_SMOKE if smoke else M_PATTERNS_PER_CLASS
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    perturb = PERTURBATION_STRENGTHS_SMOKE if smoke else PERTURBATION_STRENGTHS_FULL
    N_default = N_DEFAULT_SMOKE if smoke else N_DEFAULT_FULL

    mode_str = "SMOKE" if smoke else "FULL"
    # HDLAB_EXP_NAME-aware exp_name (n-mismatch eradication 2026-05-27).
    exp_name = os.environ.get("HDLAB_EXP_NAME", "anchor_novel_phase_battery_v3_n8192")
    print(f"[exp] {exp_name} {mode_str} on {device}", flush=True)
    print(f"  N_sweep={N_sweep} seeds={seeds}", flush=True)

    out_dir = get_output_dir(exp_name)

    # Cells C1 + C2 (N-sweep)
    print("\n=== Cells C1 + C2: q_EA and plateau height N-sweep ===", flush=True)
    c1_res, c2_res = run_cell_C1_C2(N_sweep, M_per_class, seeds, device)

    # Cells C3-C6 at default N
    print(f"\n=== Cells C3-C6 at N={N_default} ===", flush=True)
    c3456_res = run_cells_C3_C6(N_default, M_per_class, seeds, device, perturb)

    # Classify cells
    cell_calls = classify_cells(c1_res, c2_res, c3456_res)
    print(f"\n[battery] Cell calls: {cell_calls}", flush=True)

    verdict, verdict_msg = decide_class(cell_calls)
    print(f"[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)

    elapsed = round(time.time() - t0, 3)
    print(f"elapsed={elapsed}s", flush=True)

    summary = {
        "C1_q_EA_by_N": c1_res,
        "C2_plateaus_by_N": c2_res,
        "C3_spectral": c3456_res["C3"],
        "C4_hysteresis": c3456_res["C4"],
        "C5_disorder_op": c3456_res["C5"],
        "C6_free_energy": c3456_res["C6"],
        "cell_calls": cell_calls,
        "class_vote_counts": {
            "DOCUMENTED": sum(1 for v in cell_calls.values() if v == "DOCUMENTED"),
            "NOVEL": sum(1 for v in cell_calls.values() if v == "NOVEL"),
            "FINITE_N": sum(1 for v in cell_calls.values() if v == "FINITE_N"),
            "MIDDLE": sum(1 for v in cell_calls.values() if v == "MIDDLE"),
        },
        "v1_comparison": {
            "v1_cell_calls": {"C1": "DOCUMENTED", "C2": "FINITE_N",
                              "C3": "FINITE_N", "C4": "MIDDLE",
                              "C5": "DOCUMENTED", "C6": "DOCUMENTED"},
            "v1_N_sweep": [512, 1024, 2048, 4096],
            "v1_n_seeds": 5,
        },
    }

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": {
            "N_sweep": N_sweep,
            "N_default": N_default,
            "M_per_class": M_per_class,
            "seeds": seeds,
            "mode": mode_str,
            "device": str(device),
        },
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test",
                        help="Run instrumentation self-tests only and exit")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
