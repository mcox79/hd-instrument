"""AXIS-2 CODEBOOK DENSITY v2: collapse curve at high M_frac at N=4096.

CONTEXT:
  axis2_codebook_density_v1_n4096 (MIDDLE_BAND v267): all 3 codebook classes
  (BSC, Hadamard, Kerdock) show ret=0.58 at M/N=8. The HARD_PASS threshold
  was ret < 0.50 at M/N=8, which none reached.
  v2 extends to M_fracs=[4,8,12,16,20] to see the collapse curve per class.

SCIENTIFIC QUESTION:
  At M/N = [4, 8, 12, 16, 20], how does retention decay for each codebook class?
  Do classes collapse together or separately?
  Is any class more robust to loading (e.g., Kerdock vs BSC)?

PRE-REGISTERED BANDS:
  Prior: v1 at M/N=8 -> ret=0.58 for all classes.
  Expected: all classes continue to collapse as M/N increases.

  HARD_PASS: at least 2/3 classes show retention < 0.30 at M/N=16
    AND retention at M/N=4 > 0.80 for all classes.
    Interpretation: generic phase structure, capacity limit universal.
  HARD_FAIL: any class maintains retention > 0.70 at M/N=20 (no capacity limit).
  MIDDLE_BAND: classes differ > 0.30 in retention at M/N=12.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. M at M_frac=16, N=4096: M=65536.
  3. OOM: keys=65536*4096*4=1.07GB. W=64MB. CB=64MB. Total~1.2GB. Under 6GB. OK.
  4. ret(M/N=4) > 0.80: near-capacity but multi-basin regime (from axis1 chunk data).
  5. ret(M/N=16) < 0.30: beyond phase boundary, deep collapse.

TIMEOUT ESTIMATE:
  5 M_fracs x 3 classes x 3 seeds = 45 cells. Per cell: ~1s.
  Total: 45s. Safety: ceil(1.5 * 45 * 10) = 675s. Floor 14400. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: axis2_codebook_density_v2_n4096_collapse
Queue: overnight_queue (GPU; N=4096, 5 M_fracs x 3 classes x 3 seeds)
Pre-reg: prereqs/2026-05-28_axis2_codebook_density_v2_n4096_collapse.md
Parent: axis2_codebook_density_v1_n4096 (MIDDLE_BAND v267)
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

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load axis2_codebook_density_v1 for run_one_cell and codebook builders
_v1_path = REPO / "experiments" / "exp_axis2_codebook_density_v1_n4096.py"
_v1_spec = importlib.util.spec_from_file_location("axis2v1_v2", _v1_path)
v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(v1)

run_one_cell = v1.run_one_cell
build_codebook = v1.build_codebook

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Extended M_fracs into collapse regime
M_FRACS_FULL  = [4.0, 8.0, 12.0, 16.0, 20.0]
M_FRACS_SMOKE = [4.0, 8.0, 12.0]

CODEBOOK_CLASSES_FULL  = ["bsc", "hadamard", "kerdock"]
CODEBOOK_CLASSES_SMOKE = ["bsc", "kerdock"]

BETA = 8.0
SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]
N_PROBE = 150

# Pre-registered thresholds
HP_RET_LOW_M  = 0.80   # retention at M_frac=4 > 0.80 for all classes
HP_RET_HIGH_M = 0.30   # retention at M_frac=16 < 0.30 for >= 2/3 classes
HF_RET_NEVER  = 0.70   # any class > 0.70 at M_frac=20 = HARD_FAIL (no capacity limit)
MB_CLASS_SPREAD = 0.30  # classes differ > 0.30 at M_frac=12 = MIDDLE_BAND
HP_CLASSES_MIN = 2
HP_SEEDS_MIN   = 2


def get_output_dir(default_name: str = "axis2_codebook_density_v2_n4096_collapse") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("AXIS2V2_INCONCLUSIVE", "No cells.")

    N = summary.get("N", N_FULL)

    # Organize by (class, M_frac) -> list of retentions
    by_class_mfrac: Dict[Tuple, List] = {}
    for c in cells:
        key = (c["codebook_class"], c["M_frac"])
        by_class_mfrac.setdefault(key, []).append(c["retention"])

    # Mean retention per (class, M_frac)
    mean_ret: Dict[Tuple, float] = {}
    for k, rets in by_class_mfrac.items():
        mean_ret[k] = sum(rets) / len(rets)

    classes = sorted(set(k[0] for k in mean_ret.keys()))
    m_sorted = sorted(set(k[1] for k in mean_ret.keys()))

    # Check HARD_FAIL: any class > 0.70 at M_frac=20
    hard_fail = False
    for cls in classes:
        ret_at_20 = mean_ret.get((cls, 20.0), None)
        if ret_at_20 is not None and ret_at_20 > HF_RET_NEVER:
            hard_fail = True
            break

    # Check HP: ret < 0.30 at M_frac=16 for >= 2/3 classes
    classes_at_low_high_m = [cls for cls in classes
                              if mean_ret.get((cls, 16.0), 1.0) < HP_RET_HIGH_M]
    hp_collapse_count = len(classes_at_low_high_m)

    # Check HP: ret > 0.80 at M_frac=4 for all classes
    all_above_low = all(mean_ret.get((cls, 4.0), 0.0) > HP_RET_LOW_M for cls in classes)

    # Check MIDDLE_BAND: classes differ > 0.30 at M_frac=12
    rets_at_12 = [mean_ret.get((cls, 12.0), None) for cls in classes
                  if (cls, 12.0) in mean_ret]
    class_spread_12 = max(rets_at_12) - min(rets_at_12) if len(rets_at_12) >= 2 else 0.0

    # Build detail
    ret_at_8 = {cls: round(mean_ret.get((cls, 8.0), float("nan")), 3) for cls in classes}
    ret_at_16 = {cls: round(mean_ret.get((cls, 16.0), float("nan")), 3) for cls in classes}
    detail = (f"hp_collapse_count={hp_collapse_count}/{len(classes)} "
              f"all_above_low={all_above_low} class_spread_12={class_spread_12:.3f} "
              f"ret_at_8={ret_at_8} ret_at_16={ret_at_16} N={N}")

    if hard_fail:
        return ("AXIS2V2_HARD_FAIL",
                f"NO_CAPACITY_LIMIT: class with ret > {HF_RET_NEVER} at M_frac=20. " + detail)

    if hp_collapse_count >= HP_CLASSES_MIN and all_above_low:
        return ("AXIS2V2_HARD_PASS",
                f"GENERIC_COLLAPSE: {hp_collapse_count}/{len(classes)} classes collapse "
                f"(ret < {HP_RET_HIGH_M} at M_frac=16). " + detail)

    if class_spread_12 > MB_CLASS_SPREAD:
        return ("AXIS2V2_MIDDLE_BAND",
                f"CLASS_DIVERGENCE: spread={class_spread_12:.3f} at M_frac=12. " + detail)

    return ("AXIS2V2_MIDDLE_BAND", f"PARTIAL_COLLAPSE: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    # Formula: M at M_frac=16, N=4096
    assert int(16.0 * N_FULL) == 65536, f"M at M_frac=16: {int(16.0*N_FULL)}"
    # Verdict gates
    fake_hp = [{"codebook_class": cls, "M_frac": m, "retention": max(0.0, 0.95 - m*0.05), "seed": 17}
               for cls in ["bsc", "kerdock"] for m in [4.0, 8.0, 12.0, 16.0, 20.0]]
    v, msg = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "PASS" in v or "MIDDLE" in v, f"gate: {v}"
    # Smoke cell at N_SMOKE
    device = torch.device("cpu")
    cell = run_one_cell("bsc", 4.0, 17, device, N_SMOKE)
    assert "retention" in cell, "retention missing"
    assert not math.isnan(cell["retention"]), "retention NaN"
    # 4x smoke: N=4096
    cell4 = run_one_cell("bsc", 4.0, 17, device, N_SMOKE * 4)
    assert "retention" in cell4, "4x retention missing"
    print(f"[selftest] axis2_codebook_density_v2_n4096_collapse PASS "
          f"ret_smoke={cell['retention']:.4f}", flush=True)


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
    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    classes = CODEBOOK_CLASSES_SMOKE if smoke else CODEBOOK_CLASSES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] axis2_codebook_density_v2_n4096_collapse smoke={smoke} N={N_cfg} "
          f"M_fracs={m_fracs} classes={classes} seeds={seeds}", flush=True)
    t0 = time.time()

    all_cells = []
    for cls in classes:
        print(f"\n  [class={cls}]", flush=True)
        for M_frac in m_fracs:
            for seed in seeds:
                cell = run_one_cell(cls, M_frac, seed, device, N_cfg)
                cell["M_frac"] = M_frac  # ensure M_frac is in cell
                all_cells.append(cell)
        print(f"  class={cls} elapsed={time.time()-t0:.1f}s", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "axis2_codebook_density_v2_n4096_collapse",
        "N": N_cfg, "smoke": smoke,
        "M_fracs": m_fracs, "classes": classes, "beta": BETA, "seeds": seeds,
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
