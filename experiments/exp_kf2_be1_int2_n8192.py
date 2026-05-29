"""KF-2 BE-1 PRECISION: int2 (2-bit quantization) at N=8192.

Delegates to exp_kf2_be1_precision_sweep_n8192 with PRECISION='int2'.
int2 = 16x memory compression vs fp32. Symmetric per-tensor quantization (1 level: +/-1).
Expected: isolation likely degrades (2-level quant = significant W perturbation).
Purpose: characterize the degradation floor for the phase diagram.

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Anchor: kf2_be1_int2_n8192
Queue: overnight_queue
Pre-reg: preregs/2026-05-29_kf2_be1_n8192.md
Parent: kf2_be1_precision_sweep_n8192 (sweep driver)
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
sys.path.insert(0, str(REPO / "experiments"))

_drv_path = REPO / "experiments" / "exp_kf2_be1_precision_sweep_n8192.py"
_drv_spec = importlib.util.spec_from_file_location("be1_drv_int2", _drv_path)
_drv = importlib.util.module_from_spec(_drv_spec)
_drv_spec.loader.exec_module(_drv)

PRECISION = "int2"

N_FULL = 8192  # PROT-018 binding contract (must match _n8192 suffix)
N_SMOKE = _drv.N_SMOKE
assert N_FULL == _drv.N_FULL, f"PROT-018: driver N mismatch: {_drv.N_FULL} != {N_FULL}"


def get_output_dir() -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", "kf2_be1_int2_n8192")
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    assert N_FULL == _drv.N_FULL, f"PROT-018: driver N mismatch: {_drv.N_FULL} != {N_FULL}"
    device = torch.device("cpu")
    cell = _drv.run_one_cell_precision(PRECISION, _drv.M_FRAC, 17, N_SMOKE, _drv.N_EDITS, device)
    assert "isolation_ratio" in cell and not math.isnan(cell["isolation_ratio"]), (
        f"isolation_ratio missing or NaN: {cell}")
    assert cell.get("precision_compression_ratio", 0) == 16.0, (
        f"int2 compression must be 16.0; got {cell.get('precision_compression_ratio')}")
    print(f"[selftest] kf2_be1_int2_n8192 PASS iso={cell['isolation_ratio']:.5f}", flush=True)


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

    print(f"[run] kf2_be1_int2_n8192 smoke={smoke} N={N_cfg} precision={PRECISION} "
          f"seeds={seeds} device={device_str}", flush=True)
    t0 = time.time()

    all_cells = []
    for seed in seeds:
        cell = _drv.run_one_cell_precision(PRECISION, _drv.M_FRAC, seed, N_cfg, _drv.N_EDITS, device)
        all_cells.append(cell)
        iso = cell["isolation_ratio"]
        print(f"  {PRECISION} seed={seed} iso={iso:.5f} ({time.time()-t0:.1f}s)", flush=True)

    seeds_pass = sum(1 for c in all_cells if c["isolation_ratio"] < _drv.HP_ISOLATION_MAX)
    max_iso = max(c["isolation_ratio"] for c in all_cells) if all_cells else float("nan")
    theory_bound = 1.0 / math.sqrt(N_cfg)
    compression = all_cells[0].get("precision_compression_ratio", 0.0) if all_cells else 0.0
    if max_iso >= _drv.HF_CONTAMINATION:
        verdict = "KF2_BE1_INT2_HARD_FAIL"
        verdict_msg = (f"INT2_BREAKS_ISOLATION: max_iso={max_iso:.5f} >= {_drv.HF_CONTAMINATION} "
                       f"(expected; characterizes precision floor)")
    elif seeds_pass >= _drv.HP_SEEDS_MIN:
        verdict = "KF2_BE1_INT2_HARD_PASS"
        verdict_msg = (f"INT2_HOLDS: {seeds_pass}/{len(seeds)} seeds pass, "
                       f"max_iso={max_iso:.5f} compression={compression:.1f}x")
    else:
        verdict = "KF2_BE1_INT2_MIDDLE_BAND"
        verdict_msg = f"INT2_PARTIAL: {seeds_pass}/{len(seeds)} seeds, max_iso={max_iso:.5f}"

    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "kf2_be1_int2_n8192", "precision": PRECISION, "N": N_cfg, "smoke": smoke,
        "seeds": seeds, "cells": all_cells,
        "verdict": verdict, "verdict_msg": verdict_msg, "elapsed_s": elapsed,
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
