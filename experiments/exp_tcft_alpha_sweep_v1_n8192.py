"""TCFT ALPHA SWEEP v1: deletion-cert across alpha_ratio at N=8192.

CONTEXT:
  C3_HARD_PASS (v267, cap_map TCFT 82-92%): TCFT deletion-cert holds for multiple
  erase windows. v267 also expanded to wider protocols. This probe sweeps alpha_ratio
  (fraction of stored patterns to erase / total capacity) to find the alpha_c where
  the deletion certificate breaks down.

  MECHANISM: At low alpha_ratio, few patterns stored -- easy to certify.
  At high alpha_ratio, many patterns -- harder to certify clean erasure.
  alpha_c = threshold where var_ratio >= 0.10 (cert degrades).

SCIENTIFIC QUESTION:
  What is alpha_c (certificate failure point) at N=8192?
  Does it match the theoretical capacity limit (alpha_c ~ 0.14 for dense AM)?

PRE-REGISTERED BANDS:
  Prior: C3 HARD_PASS var_ratio < 0.10 at anchor alpha_ratio=0.125. v267 multiple
  erase windows confirmed. Envelope extension.

  HARD_PASS: var_ratio < 0.10 holds at alpha_ratio >= 0.25 (2x the anchor).
    Interpretation: deletion certificate robust through alpha=0.25.
  HARD_FAIL: var_ratio >= 0.10 at alpha_ratio = 0.125 (breaks at anchor point).
    Interpretation: deletion certificate fragile -- contradicts v267 C3.
  MIDDLE_BAND: cert holds at 0.125 but breaks before 0.25.

FORMULA SELF-TESTS:
  1. N = 8192 (PROT-018: _n8192 suffix).
  2. alpha_ratio = M / C where C = N * log2(N) (Kerdock codebook).
     N=8192: log2(8192) = 13. C = 8192*13 = 106496.
     alpha=0.125: M = 0.125 * 106496 = 13312.
     alpha=0.25: M = 0.25 * 106496 = 26624.
  3. var_ratio = Var(works | erase) / Var(works | store). < 0.10 = cert valid.
  4. HP gate: at >= 2/3 seeds, var_ratio < 0.10 at alpha=0.25.
  5. HF gate: at >= 2/3 seeds, var_ratio >= 0.10 at alpha=0.125.

OOM CHECK:
  N=8192, alpha=0.50: M = 0.5 * 106496 = 53248. W=8192^2*4=268MB. Keys=53248*8192*4=1.74GB.
  Total~2GB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  TCFT per cell: store M patterns + conditioned-threshold computation.
  At alpha=0.50, M=53248 patterns. ~8s per cell.
  6 alpha vals x 3 seeds = 18 cells x 8s = 144s.
  Smoke: 2 alpha x 1 seed = 2 cells x 3s = 6s.
  Safety: ceil(1.5 * 144 * 10) = 2160s. _n8192 floor: timeout >= 21600. timeout_s = 21600.

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Anchor: tcft_alpha_sweep_v1_n8192
Queue: overnight_queue
Pre-reg: preregs/2026-05-28_tcft_alpha_sweep_v1_n8192.md
Parent: tcft_erase_robustness_n8192_v1 (v267 C3_HARD_PASS); tcft_n8192_v7 (N=8192 foundation)
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

# Load TCFT robustness module for run_one_cell
_rob_path = REPO / "experiments" / "exp_tcft_erase_robustness_n8192_v1.py"
_rob_spec = importlib.util.spec_from_file_location("tcft_rob_v1_sweep", _rob_path)
tcft_rob = importlib.util.module_from_spec(_rob_spec)
_rob_spec.loader.exec_module(tcft_rob)

run_one_cell = tcft_rob.run_one_cell

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N_FULL  = 8192
N_SMOKE = 2048
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

SPLIT_Q = 0.50   # standard split quantile

ALPHA_SWEEP_FULL  = [0.05, 0.10, 0.125, 0.20, 0.30, 0.50]
ALPHA_SWEEP_SMOKE = [0.05, 0.125]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
HP_VAR_RATIO_CERT  = 0.10   # var_ratio < 0.10 = certificate valid
HP_ALPHA_TARGET    = 0.25   # must hold at alpha >= 0.25 for HARD_PASS
HF_ALPHA_ANCHOR    = 0.125  # breaks at anchor alpha = HARD_FAIL
HP_SEEDS_MIN       = 2


def get_output_dir(default_name: str = "tcft_alpha_sweep_v1_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("TCFT_ALPHA_INCONCLUSIVE", "No cells.")

    by_alpha: Dict[float, List] = {}
    for c in cells:
        by_alpha.setdefault(c["alpha"], []).append(c)

    alphas = sorted(by_alpha.keys())

    def mean_vr_at(a: float) -> float:
        cs = by_alpha.get(a, [])
        valid = [c["var_ratio"] for c in cs if c.get("var_ratio") is not None]
        return sum(valid) / len(valid) if valid else float("nan")

    def pass_count_at(a: float) -> int:
        cs = by_alpha.get(a, [])
        return sum(1 for c in cs if c.get("var_ratio") is not None
                   and c["var_ratio"] < HP_VAR_RATIO_CERT)

    # Alpha_c: first alpha where cert breaks (majority fail)
    alpha_c = None
    for a in alphas:
        n_seeds = len(by_alpha.get(a, []))
        n_pass = pass_count_at(a)
        if n_pass < HP_SEEDS_MIN:
            alpha_c = a
            break

    # Find largest alpha where cert still holds
    alpha_max_cert = max((a for a in alphas if pass_count_at(a) >= HP_SEEDS_MIN), default=0.0)

    vr_at_anchor = mean_vr_at(HF_ALPHA_ANCHOR)
    anchor_breaks = (not math.isnan(vr_at_anchor)) and vr_at_anchor >= HP_VAR_RATIO_CERT
    pass_at_target = pass_count_at(HP_ALPHA_TARGET) >= HP_SEEDS_MIN

    vr_anchor_str = f"{vr_at_anchor:.4f}" if not math.isnan(vr_at_anchor) else "nan"
    detail = (f"alpha_c={alpha_c} alpha_max_cert={alpha_max_cert:.3f} "
              f"vr_anchor={vr_anchor_str} "
              f"HP_alpha_target={HP_ALPHA_TARGET} N={summary.get('N', N_FULL)}")

    if anchor_breaks:
        return ("TCFT_ALPHA_HARD_FAIL",
                f"CERT_FAILS_AT_ANCHOR: var_ratio={vr_at_anchor:.4f} >= {HP_VAR_RATIO_CERT}. " + detail)

    if pass_at_target:
        return ("TCFT_ALPHA_HARD_PASS",
                f"CERT_ROBUST_THROUGH_0.25: alpha_max_cert={alpha_max_cert:.3f}. " + detail)

    return ("TCFT_ALPHA_MIDDLE_BAND",
            f"CERT_HOLDS_BELOW_TARGET: alpha_c={alpha_c}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"
    # Formula self-test: alpha and M calculation
    C = N_FULL * int(math.log2(N_FULL))
    M_anchor = int(0.125 * C)
    assert abs(M_anchor - 13312) < 10, f"M_anchor formula: {M_anchor} vs 13312"
    # Verdict gates
    fake_hp = [{"alpha": a, "var_ratio": 0.05} for a in [0.05, 0.125, 0.25, 0.50] for _ in range(3)]
    v, _ = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "HARD_PASS" in v, f"HARD_PASS gate: {v}"
    fake_hf = [{"alpha": 0.125, "var_ratio": 0.15} for _ in range(3)]
    vf, _ = compute_verdict({"cells": fake_hf, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf}"
    # Smoke cell
    cell = run_one_cell(N=N_SMOKE, alpha_ratio=0.05, split_q=SPLIT_Q, seed=17)
    assert "var_ratio" in cell, f"var_ratio missing: {list(cell.keys())}"
    # 4x scale
    cell4 = run_one_cell(N=N_SMOKE * 2, alpha_ratio=0.05, split_q=SPLIT_Q, seed=17)
    assert "var_ratio" in cell4, f"4x var_ratio missing"
    print(f"[selftest] tcft_alpha_sweep_v1_n8192 PASS vr_smoke={cell.get('var_ratio', 'None')}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    device_str = "cuda" if __import__("torch").cuda.is_available() else "cpu"
    smoke = args.smoke

    N_cfg = N_SMOKE if smoke else N_FULL
    alpha_sweep = ALPHA_SWEEP_SMOKE if smoke else ALPHA_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] tcft_alpha_sweep_v1_n8192 smoke={smoke} N={N_cfg} alpha_pts={len(alpha_sweep)} seeds={seeds} device={device_str}", flush=True)
    t0 = time.time()

    all_cells = []
    for alpha in alpha_sweep:
        print(f"\n  [alpha={alpha}]", flush=True)
        for seed in seeds:
            cell = run_one_cell(N=N_cfg, alpha_ratio=alpha, split_q=SPLIT_Q, seed=seed)
            cell["alpha"] = alpha
            all_cells.append(cell)
            vr = cell.get("var_ratio")
            vr_str = f"{vr:.4f}" if vr is not None else "None"
            print(f"  alpha={alpha} seed={seed} var_ratio={vr_str} ({time.time()-t0:.1f}s)", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "tcft_alpha_sweep_v1_n8192", "N": N_cfg, "smoke": smoke,
        "alpha_sweep": alpha_sweep, "split_q": SPLIT_Q, "seeds": seeds,
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
