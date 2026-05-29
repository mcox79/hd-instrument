"""PHASE REGION C -- KF-1 variant: M_frac=4, beta=64 at N=4096.

Delegates to exp_phase_region_cd_v1_n4096 for Region C only (M < M_c, beta > beta_c).
KF-1 labeling: Kerdock key-value substrate, first-order association retrieval.

Region C: M_frac=4 (undercapacity), beta=64 (well above beta_c~10-16).
Expected: retention near 1.0 (deep ferromagnetic state stabilized by high beta).
Purpose: confirm that substrate in Region C retrieves reliably.

N-suffix: no _nN suffix -- name uses _n4096 textually but PROT-018 only applies to
the pattern _n<NUMBER> where it is a standalone N-binding. Per the naming convention,
this anchor does NOT carry PROT-018 binding (no underscore before n4096 at end).
Wait -- _n4096 IS present in the name. Must bind.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: region_c_kf1_n4096_beta64_mfrac4
Queue: overnight_queue
Pre-reg: preregs/2026-05-29_phase_region_cd_n4096.md
Parent: phase_region_cd_v1_n4096; t1_beta_sweep_v1_n4096 (v267 beta_c localized)
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
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load phase region driver
_drv_path = REPO / "experiments" / "exp_phase_region_cd_v1_n4096.py"
_drv_spec = importlib.util.spec_from_file_location("phcd_drv_rc_kf1", _drv_path)
_drv = importlib.util.module_from_spec(_drv_spec)
_drv_spec.loader.exec_module(_drv)

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL = 4096  # PROT-018 binding contract (must match _n4096 suffix)
N_SMOKE = _drv.N_SMOKE
assert N_FULL == _drv.N_FULL, f"PROT-018: driver N mismatch: {_drv.N_FULL} != {N_FULL}"

REGION  = "region_C"
M_FRAC  = _drv.REGION_C_MFRAC   # 4.0
BETA    = _drv.BETA_HIGH         # 64.0

HP_RET_MIN = _drv.HP_RETENTION_C_MIN    # 0.70
HF_RET_MAX = _drv.HF_RETENTION_C_MAX   # 0.35
HP_SEEDS   = _drv.HP_SEEDS_C_MIN        # 3


def get_output_dir() -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", "region_c_kf1_n4096_beta64_mfrac4")
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    device = torch.device("cpu")
    cell = _drv.run_one_cell(REGION, M_FRAC, BETA, 17, N_SMOKE, device)
    assert "retention" in cell and not math.isnan(cell["retention"]), (
        f"retention missing or NaN: {cell}")
    assert 0.0 <= cell["retention"] <= 1.0, f"retention out of range: {cell['retention']}"
    cell4x = _drv.run_one_cell(REGION, M_FRAC, BETA, 17, N_SMOKE * 4, device)
    assert "retention" in cell4x
    print(f"[selftest] region_c_kf1_n4096_beta64_mfrac4 PASS "
          f"ret_smoke={cell['retention']:.5f} ret_4x={cell4x['retention']:.5f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    seeds = _drv.SEEDS_SMOKE if smoke else _drv.SEEDS_FULL

    print(f"[run] region_c_kf1_n4096_beta64_mfrac4 smoke={smoke} N={N_cfg} "
          f"region={REGION} M_frac={M_FRAC} beta={BETA} seeds={seeds} device={device_str}",
          flush=True)
    t0 = time.time()

    all_cells = []
    for seed in seeds:
        cell = _drv.run_one_cell(REGION, M_FRAC, BETA, seed, N_cfg, device)
        all_cells.append(cell)
        print(f"  seed={seed} retention={cell['retention']:.5f} ({time.time()-t0:.1f}s)",
              flush=True)

    rets = [c["retention"] for c in all_cells]
    mean_ret = sum(rets) / len(rets) if rets else 0.0
    seeds_pass = sum(1 for r in rets if r >= HP_RET_MIN)

    if mean_ret < HF_RET_MAX:
        verdict = "REGION_C_KF1_HARD_FAIL"
        verdict_msg = (f"FERROMAGNET_ABSENT: mean_ret={mean_ret:.4f} < {HF_RET_MAX} "
                       f"at M_frac={M_FRAC} beta={BETA}")
    elif seeds_pass >= HP_SEEDS:
        verdict = "REGION_C_KF1_HARD_PASS"
        verdict_msg = (f"FERROMAGNET_CONFIRMED: {seeds_pass}/{len(seeds)} seeds "
                       f"mean_ret={mean_ret:.4f} >= {HP_RET_MIN} at beta={BETA}")
    else:
        verdict = "REGION_C_KF1_MIDDLE_BAND"
        verdict_msg = f"PARTIAL: {seeds_pass}/{len(seeds)} seeds mean_ret={mean_ret:.4f}"

    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "region_c_kf1_n4096_beta64_mfrac4", "N": N_cfg, "smoke": smoke,
        "region": REGION, "M_frac": M_FRAC, "beta": BETA, "seeds": seeds,
        "cells": all_cells, "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_path = get_output_dir() / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    main()
