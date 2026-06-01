"""T2 CODEBOOK v3: operating-point invariance at N=4096 across (M_frac, beta) pairs.

CONTEXT:
  t2_codebook_boundary_v1_n4096 (v267 HARD_PASS GPU): slope=0.20/unit-c at M_frac=2.0 beta=32.
  Codebook-order is a load-bearing axis. v3 tests whether the codebook-axis
  behavior (monotone slope >= 0.05) is INVARIANT across different operating points.
  Strategy Decision 3 Verdict 7c: "confirm codebook-axis is operating-point-invariant."

  N=4096, CPU-compatible (Kerdock valid, no CUDA needed).

SCIENTIFIC QUESTION:
  At (M_frac, beta) pairs other than v1's (2.0, 32), does the codebook-order axis
  still show monotone retention with slope >= 0.05 per unit c?
  Operating points to test:
    (a) M_frac=2.0, beta=8  (same M_frac as v1, lower beta)
    (b) M_frac=4.0, beta=32 (same beta as v1, higher M_frac -- near transition)
    (c) M_frac=2.0, beta=64 (same M_frac as v1, higher beta)
    (d) M_frac=1.0, beta=32 (lower M_frac -- deep multi-basin)

PRE-REGISTERED BANDS:
  Prior: v1 HARD_PASS at (M_frac=2.0, beta=32): slope=0.202, mono_frac=0.875.
  Expected: codebook-axis invariant across operating points.

  HARD_PASS: codebook-order monotone slope >= 0.05 at >= 3/4 op-points AND >= 2/3 seeds.
    Interpretation: codebook-axis is operating-point-invariant; product claim robust.
  HARD_FAIL: slope < 0.05 at ALL op-points (codebook-axis only works at v1 op-point).
    Interpretation: codebook-order axis is operating-point-specific.
  MIDDLE_BAND: slope >= 0.05 at 1-2/4 op-points.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. C at N=4096 Kerdock: C = 12 * 4096 = 49152.
  3. M at (M_frac=4.0, N=4096): M=16384.
  4. M at (M_frac=1.0, N=4096): M=4096.
  5. OOM at M_frac=4: keys=16384*4096*4=268MB. W=64MB. CB=268MB. Total=600MB. OK.
  6. slope = (ret_at_c1.0 - ret_at_c0.1) / 0.9. HARD_PASS requires >= 0.05.

OOM CHECK:
  M_frac=4.0, N=4096: keys=16384*4096*4=268MB. W=64MB. CB=268MB. Total=600MB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  4 op-pts x 5 c_fracs x 3 seeds = 60 cells. Per cell: store M=8192-16384 + retrieval.
  At N=4096 CPU: ~2s per cell.
  Total: 60*2=120s. Safety: ceil(1.5*120*5)=900s. PROT-019 floor 14400. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: t2_codebook_v3_n4096_op_sweep
Queue: remote_cpu_queue (CPU; N=4096 Kerdock, 4 op-points x 5 c_fracs x 3 seeds)
Pre-reg: prereqs/2026-05-28_t2_codebook_v3_n4096_op_sweep.md
Parent: t2_codebook_boundary_v1_n4096 (v267 HARD_PASS; op-point invariance next step)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load t2v1 for run_one_seed -- LAZY
def _load_t2v1():
    _t2_path = REPO / "experiments" / "exp_t2_codebook_boundary_v1_n4096.py"
    _t2_spec = importlib.util.spec_from_file_location("t2v1_v3", _t2_path)
    t2v1 = importlib.util.module_from_spec(_t2_spec)
    _t2_spec.loader.exec_module(t2v1)
    return t2v1

_t2v1_mod = None

def get_t2v1():
    global _t2v1_mod
    if _t2v1_mod is None:
        _t2v1_mod = _load_t2v1()
    return _t2v1_mod


# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Operating points: (M_frac, beta)
OP_POINTS_FULL  = [(2.0, 8.0), (4.0, 32.0), (2.0, 64.0), (1.0, 32.0)]
OP_POINTS_SMOKE = [(2.0, 32.0)]

C_FRACS_FULL  = [0.1, 0.3, 0.5, 0.7, 1.0]
C_FRACS_SMOKE = [0.1, 0.5, 1.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds (matching v1 with relaxed slope for op-point invariance)
HP_SLOPE_MIN     = 0.05   # v1 had 0.20; relaxed for cross-op-point
HP_OP_POINTS_MIN = 3      # >= 3/4 op-points pass
HP_SEEDS_MIN     = 2      # >= 2/3 seeds per op-point


def get_output_dir(default_name: str = "t2_codebook_v3_n4096_op_sweep") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_slope(ret_by_c: List[float], c_fracs: List[float]) -> float:
    """Linear regression slope of ret vs c."""
    if len(ret_by_c) < 2 or len(c_fracs) < 2:
        return 0.0
    n = len(ret_by_c)
    mx = sum(c_fracs) / n
    my = sum(ret_by_c) / n
    num = sum((c_fracs[i] - mx) * (ret_by_c[i] - my) for i in range(n))
    den = sum((c_fracs[i] - mx) ** 2 for i in range(n))
    return num / den if abs(den) > 1e-12 else 0.0


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("T2V3_INCONCLUSIVE", "No cells.")

    N_cfg = summary.get("N", N_FULL)
    c_fracs = summary.get("c_fracs", C_FRACS_FULL)

    # Organize by (M_frac, beta) -> seed -> slope
    from collections import defaultdict
    per_op: Dict[Tuple, Dict] = defaultdict(dict)
    for c in cells:
        key = (c["M_frac"], c["beta"])
        per_op[key][c["seed"]] = c.get("slope", 0.0)

    # Per op-point: count seeds with slope >= HP_SLOPE_MIN
    op_results = {}
    for op, per_seed in per_op.items():
        n_pass = sum(1 for s in per_seed.values() if s >= HP_SLOPE_MIN)
        op_results[str(op)] = {"n_pass": n_pass, "n_total": len(per_seed),
                                "mean_slope": sum(per_seed.values()) / len(per_seed)}

    n_pass_ops = sum(1 for v in op_results.values() if v["n_pass"] >= HP_SEEDS_MIN)
    n_total_ops = len(op_results)

    detail = (f"op_results={op_results} n_pass_ops={n_pass_ops}/{n_total_ops} N={N_cfg}")

    # HARD_FAIL: no op-point passes
    if n_pass_ops == 0:
        return ("T2V3_HARD_FAIL",
                f"OP-SPECIFIC: codebook-axis only works at v1 op-point. " + detail)

    # HARD_PASS: >= 3/4 op-points pass
    if n_pass_ops >= HP_OP_POINTS_MIN:
        return ("T2V3_HARD_PASS",
                f"OP-INVARIANT: {n_pass_ops}/{n_total_ops} op-points show slope >= {HP_SLOPE_MIN}. " + detail)

    return ("T2V3_MIDDLE_BAND",
            f"PARTIAL: {n_pass_ops}/{n_total_ops} op-points pass. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Formula: M at various M_fracs
    assert int(4.0 * N_FULL) == 16384, f"M at M_frac=4: {int(4.0*N_FULL)}"
    assert int(1.0 * N_FULL) == 4096, f"M at M_frac=1: {int(1.0*N_FULL)}"

    # C at N=4096 Kerdock: C = 12 * 4096 = 49152
    import math
    C = int(math.log2(N_FULL)) * N_FULL
    assert C == 49152, f"C at N=4096: {C}"

    # OOM check
    max_M = int(4.0 * N_FULL)
    keys_bytes = max_M * N_FULL * 4
    w_bytes = N_FULL * N_FULL * 4
    cb_bytes = C * N_FULL * 4
    total = keys_bytes + w_bytes + cb_bytes
    assert total < 6e9, f"OOM: {total/1e9:.2f}GB"

    # compute_slope test
    c5 = [0.1, 0.3, 0.5, 0.7, 1.0]
    ret_mono = [0.1, 0.3, 0.5, 0.7, 0.9]  # perfectly monotone
    slope_mono = compute_slope(ret_mono, c5)
    assert slope_mono >= 0.90, f"monotone slope: {slope_mono:.3f}"  # ~1.0

    ret_flat = [0.5] * 5
    slope_flat = compute_slope(ret_flat, c5)
    assert abs(slope_flat) < 0.01, f"flat slope: {slope_flat:.4f}"

    # Verdict tests
    cells_hp = []
    for mf, beta in [(2.0, 8.0), (4.0, 32.0), (2.0, 64.0), (1.0, 32.0)]:
        for seed in [7, 17]:
            cells_hp.append({"M_frac": mf, "beta": beta, "seed": seed, "slope": 0.20})
    v, msg = compute_verdict({"cells": cells_hp, "N": N_FULL, "c_fracs": C_FRACS_FULL})
    assert "HARD_PASS" in v, f"HP test: {v}: {msg}"

    cells_hf = []
    for mf, beta in [(2.0, 8.0), (4.0, 32.0), (2.0, 64.0), (1.0, 32.0)]:
        cells_hf.append({"M_frac": mf, "beta": beta, "seed": 17, "slope": 0.01})
    v2, _ = compute_verdict({"cells": cells_hf, "N": N_FULL, "c_fracs": C_FRACS_FULL})
    assert "HARD_FAIL" in v2 or "MIDDLE_BAND" in v2, f"HF test: {v2}"

    # Live smoke cell: verify metrics non-null
    t2v1 = get_t2v1()
    device = torch.device("cpu")
    smoke_result = t2v1.run_one_seed(N_SMOKE, 2.0, 32.0, [0.1, 0.5, 1.0], 17, device)
    rbC = smoke_result.get("ret_by_c", [])
    assert len(rbC) == 3, f"ret_by_c length: {len(rbC)}"
    assert all(0 <= v <= 1 for v in rbC), f"ret_by_c OOR: {rbC}"
    slope_live = compute_slope(rbC, [0.1, 0.5, 1.0])
    assert slope_live is not None, "slope is None"

    # Multi-scale: N=1024*4=4096 (valid Kerdock)
    smoke4_result = t2v1.run_one_seed(N_SMOKE * 4, 2.0, 32.0, [0.1, 0.5, 1.0], 17, device)
    rbC4 = smoke4_result.get("ret_by_c", [])
    assert len(rbC4) == 3, f"4x ret_by_c length: {len(rbC4)}"

    print(f"[selftest] t2_codebook_v3_n4096_op_sweep PASS N_FULL={N_FULL} "
          f"smoke_slope={slope_live:.4f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    t2v1 = get_t2v1()
    smoke = args.smoke
    N_cfg    = N_SMOKE if smoke else N_FULL
    op_pts   = OP_POINTS_SMOKE if smoke else OP_POINTS_FULL
    c_fracs  = C_FRACS_SMOKE if smoke else C_FRACS_FULL
    seeds    = SEEDS_SMOKE if smoke else SEEDS_FULL

    device = torch.device("cpu")
    t0 = time.time()
    print(f"t2_codebook_v3_n4096_op_sweep mode={'SMOKE' if smoke else 'FULL'} N={N_cfg} "
          f"op_pts={op_pts} c_fracs={c_fracs} seeds={seeds}", flush=True)

    all_cells = []
    for mf, beta in op_pts:
        print(f"\n== M_frac={mf} beta={beta} ==", flush=True)
        for seed in seeds:
            result = t2v1.run_one_seed(N_cfg, mf, beta, c_fracs, seed, device)
            rbC = result.get("ret_by_c", [0.0] * len(c_fracs))
            slope = compute_slope(rbC, c_fracs)
            total_var = max(rbC) - min(rbC) if rbC else 0.0
            row = {"M_frac": mf, "beta": beta, "seed": seed,
                   "ret_by_c": [round(v, 4) for v in rbC],
                   "slope": round(slope, 4), "total_var": round(total_var, 4)}
            all_cells.append(row)
            print(f"  M_frac={mf} beta={beta} seed={seed} slope={slope:.4f} "
                  f"total_var={total_var:.4f}", flush=True)

    elapsed = round(time.time() - t0, 2)
    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg,
                                             "c_fracs": c_fracs})
    summary = {
        "anchor": "t2_codebook_v3_n4096_op_sweep",
        "N": N_cfg, "smoke": smoke,
        "op_points": op_pts, "c_fracs": c_fracs, "seeds": seeds,
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
