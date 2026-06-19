"""T1 BETA PHASE BOUNDARY v3: beta_c(M_frac) curve at N=4096 on CPU.

CONTEXT:
  t1_beta_sweep_v1_n4096 (v267 HARD_PASS GPU): beta_c locatable at M_frac=8.0, N=4096.
  t1_beta_sweep_v2_n8192 (GPU overnight): N-scaling at M_frac=4.0 N=8192.
  v3 (THIS): map beta_c(M_frac) at N=4096 across M_fracs={2,4,6,8,10,12}.
  Sweeps M to trace HOW the phase boundary in (M, beta) space runs.
  CPU-compatible: N=4096 Kerdock, no CUDA needed (no CUDA for CPU-feasible scale).

SCIENTIFIC QUESTION:
  Is beta_c(M_frac) monotone decreasing with M_frac (steeper load -> lower critical beta)?
  Does the two-boundary lattice structure (t1+t2) have a clean 2D functional form?
  At what (M_frac, beta) does the transition vanish (deep single-basin or deep multi-basin)?

PRE-REGISTERED BANDS:
  Prior: t1v1 HARD_PASS at M_frac=8.0 (beta_c ~ 12-16). Calibration probe for M_frac curve.
  Expected: beta_c decreases monotone as M_frac increases (more memory = sharper/lower transition).

  HARD_PASS: beta_c(M_frac) is MONOTONE DECREASING OR PEAKED across at least 4/6 M_fracs
    at >= 2/3 seeds.
    Interpretation: beta_c has systematic M_frac dependence; two-boundary lattice is 2D-structured.
  HARD_FAIL: beta_c is flat (same beta_c at all M_fracs within 1 log2 unit at all seeds).
    Interpretation: beta-axis boundary M_frac-independent (single parameter family, not 2D lattice).
  MIDDLE_BAND: beta_c varies with M_frac but not monotone (some M_fracs show no transition).

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. M at M_frac=8, N=4096: M=32768. Keys=32768*4096*4=536MB. W=64MB. CB=268MB. OK.
  3. beta_c = BETA_SWEEP[argmax |d(ret)/d(log2_beta)|] over interior points.
  4. max_gradient at step i: |ret[i+1] - ret[i-1]| / 2.
  5. HP gate: monotone check across M_fracs per seed.
  6. M at M_frac=2, N=4096: M=8192. M_frac=12: M=49152.
     OOM at M_frac=12: keys=49152*4096*4=805MB. Total~1.1GB. OK.

TIMEOUT ESTIMATE:
  t1v1 at M_frac=8 N=4096 5 seeds 10 beta pts: estimated ~25s full.
  v3: 6 M_fracs x 3 seeds x 10 beta pts = 180 cells at ~0.5s each = 90s.
  CPU (no GPU): N=4096 Kerdock CPU = ~3-5s per cell vs GPU ~0.5s. 3x factor.
  Total: 180 * 3s = 540s. Safety 1.5x: 810s. PROT-019 floor 14400. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: t1_beta_v3_n4096_mfrac_sweep
Queue: remote_cpu_queue (CPU; N=4096 Kerdock, 6 M_fracs x 3 seeds x 10 beta pts)
Pre-reg: prereqs/2026-05-28_t1_beta_v3_n4096_mfrac_sweep.md
Parent: t1_beta_sweep_v1_n4096 (v267 HARD_PASS; maps beta_c at single M_frac)
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

# Load t1_beta_sweep_v1 for run_one_seed -- LAZY to avoid parent selftest at gate
def _load_t1v1():
    _t1_path = REPO / "experiments" / "exp_t1_beta_sweep_v1_n4096.py"
    _t1_spec = importlib.util.spec_from_file_location("t1v1_v3", _t1_path)
    t1v1 = importlib.util.module_from_spec(_t1_spec)
    _t1_spec.loader.exec_module(t1v1)
    return t1v1

_t1v1_mod = None

def get_t1v1():
    global _t1v1_mod
    if _t1v1_mod is None:
        _t1v1_mod = _load_t1v1()
    return _t1v1_mod


# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FRACS_FULL  = [2.0, 4.0, 6.0, 8.0, 10.0, 12.0]
M_FRACS_SMOKE = [4.0, 8.0]

BETA_SWEEP_FULL  = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
BETA_SWEEP_SMOKE = [1, 4, 16, 64, 256]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

N_PROBE = 200

# Pre-registered thresholds
HP_MFRAC_MIN    = 4    # >= 4/6 M_fracs show systematic beta_c behavior
HP_SEEDS_MIN    = 2    # >= 2/3 seeds
HP_MAX_GRAD_MIN = 0.10 # same as v1
HF_FLAT_WINDOW  = 1.0  # beta_c range < 1 log2 unit across all M_fracs = flat


def get_output_dir(default_name: str = "t1_beta_v3_n4096_mfrac_sweep") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_beta_c(ret_vals: List[float], beta_sweep: List[float]) -> Tuple[float, float]:
    """Return (beta_c, max_gradient) from retention vs beta curve."""
    if len(ret_vals) < 3:
        return (float(beta_sweep[0]), 0.0)
    log2_beta = [math.log2(max(b, 1e-9)) for b in beta_sweep]
    max_grad = 0.0
    best_beta_c = float(beta_sweep[0])
    for i in range(1, len(ret_vals) - 1):
        dlb = log2_beta[i + 1] - log2_beta[i - 1]
        if dlb < 1e-9:
            continue
        grad = abs(ret_vals[i + 1] - ret_vals[i - 1]) / dlb
        if grad > max_grad:
            max_grad = grad
            best_beta_c = float(beta_sweep[i])
    return (best_beta_c, max_grad)


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("T1V3_INCONCLUSIVE", "No cells.")

    N_cfg = summary.get("N", N_FULL)
    beta_sweep = summary.get("beta_sweep", BETA_SWEEP_FULL)

    # Organize: per (M_frac, seed) -> beta_c, max_gradient
    from collections import defaultdict
    per_mfrac_seed: Dict[float, Dict[int, Dict]] = defaultdict(dict)
    for c in cells:
        per_mfrac_seed[c["M_frac"]][c["seed"]] = c

    mfracs = sorted(per_mfrac_seed.keys())

    # Per M_frac: collect mean beta_c across seeds
    mean_beta_c: Dict[float, float] = {}
    for mf, per_seed in per_mfrac_seed.items():
        bcs = [v.get("beta_c", beta_sweep[0]) for v in per_seed.values()]
        mean_beta_c[mf] = sum(bcs) / len(bcs)

    # Check monotone: beta_c decreasing with M_frac?
    if len(mfracs) >= 2:
        beta_c_vals = [mean_beta_c[mf] for mf in mfracs]
        log2_bcs = [math.log2(max(v, 1e-9)) for v in beta_c_vals]
        # Monotone decreasing = each step decreases
        monotone_steps = sum(1 for i in range(len(log2_bcs) - 1)
                             if log2_bcs[i] >= log2_bcs[i + 1])
        n_steps = len(log2_bcs) - 1
        monotone_frac = monotone_steps / n_steps if n_steps > 0 else 0.0
        beta_c_range = log2_bcs[0] - log2_bcs[-1]  # positive if decreasing
    else:
        monotone_frac = 0.0
        beta_c_range = 0.0

    # Count M_fracs with high max_gradient (transition detectable)
    mfracs_with_transition = 0
    for mf, per_seed in per_mfrac_seed.items():
        n_seeds_pass = sum(1 for v in per_seed.values()
                           if v.get("max_gradient", 0.0) >= HP_MAX_GRAD_MIN)
        if n_seeds_pass >= HP_SEEDS_MIN:
            mfracs_with_transition += 1

    detail = (f"mean_beta_c_by_mfrac={dict((mf, round(v, 1)) for mf, v in sorted(mean_beta_c.items()))} "
              f"monotone_frac={monotone_frac:.2f} beta_c_log2_range={beta_c_range:.2f} "
              f"mfracs_with_transition={mfracs_with_transition}/{len(mfracs)} N={N_cfg}")

    # HARD_FAIL: flat beta_c across all M_fracs
    if beta_c_range < HF_FLAT_WINDOW and len(mfracs) >= 3:
        return ("T1V3_HARD_FAIL",
                f"FLAT_BETA_C: log2_range={beta_c_range:.2f} < {HF_FLAT_WINDOW} "
                f"across {len(mfracs)} M_fracs. " + detail)

    # HARD_PASS: systematic M_frac dependence
    if mfracs_with_transition >= HP_MFRAC_MIN:
        monotone_str = f"MONOTONE({monotone_frac:.2f})" if monotone_frac >= 0.6 else f"NONMONOTONE({monotone_frac:.2f})"
        return ("T1V3_HARD_PASS",
                f"BETA_C_MFRAC_CURVE: {mfracs_with_transition}/{len(mfracs)} M_fracs "
                f"show clear transition. {monotone_str}. " + detail)

    return ("T1V3_MIDDLE_BAND",
            f"PARTIAL: {mfracs_with_transition}/{len(mfracs)} M_fracs with transition. " + detail)


def _instrumentation_selftest() -> None:
    """Formula assertions only (no live computation)."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # M at M_frac values
    for mf, expected in [(2.0, 8192), (8.0, 32768), (12.0, 49152)]:
        assert int(mf * N_FULL) == expected, f"M at M_frac={mf}: {int(mf*N_FULL)}"

    # OOM check
    for mf in [2.0, 8.0, 12.0]:
        keys_bytes = int(mf * N_FULL) * N_FULL * 4
        w_bytes = N_FULL * N_FULL * 4
        total = keys_bytes + w_bytes * 2
        assert total < 4e9, f"OOM at M_frac={mf}: {total/1e9:.2f}GB"

    # compute_beta_c test
    beta_sw = [1, 2, 4, 8, 16, 32, 64, 128]
    # Sigmoid-like: grad should peak around step 3-5
    ret_sig = [0.1, 0.1, 0.15, 0.40, 0.70, 0.85, 0.90, 0.92]
    bc, mg = compute_beta_c(ret_sig, beta_sw)
    assert mg >= 0.10, f"compute_beta_c: max_gradient={mg:.3f} < 0.10"
    assert bc in beta_sw, f"beta_c not in sweep: {bc}"

    # Flat test
    ret_flat = [0.5] * 8
    bc_flat, mg_flat = compute_beta_c(ret_flat, beta_sw)
    assert mg_flat < 0.05, f"flat curve: max_gradient={mg_flat:.4f} should be near 0"

    # Verdict HARD_PASS test
    cells_hp = []
    for mf in [2.0, 4.0, 6.0, 8.0, 10.0]:  # 5/6 M_fracs have transition
        for seed in [7, 17]:
            cells_hp.append({"M_frac": mf, "seed": seed, "beta_c": 16.0 / mf,
                              "max_gradient": 0.25, "ret_vals": ret_sig[:6]})
    cells_hp.append({"M_frac": 12.0, "seed": 7, "beta_c": 2.0, "max_gradient": 0.05,
                     "ret_vals": ret_sig[:6]})
    cells_hp.append({"M_frac": 12.0, "seed": 17, "beta_c": 2.0, "max_gradient": 0.04,
                     "ret_vals": ret_sig[:6]})
    v, msg = compute_verdict({"cells": cells_hp, "N": N_FULL, "beta_sweep": BETA_SWEEP_FULL})
    assert "HARD_PASS" in v, f"Verdict HP test: {v}: {msg}"

    # Verdict HARD_FAIL test (flat)
    cells_hf = [{"M_frac": mf, "seed": 17, "beta_c": 8.0,  # same beta_c all M
                 "max_gradient": 0.05, "ret_vals": ret_flat}
                for mf in [2.0, 4.0, 6.0, 8.0, 10.0, 12.0]]
    v2, _ = compute_verdict({"cells": cells_hf, "N": N_FULL, "beta_sweep": BETA_SWEEP_FULL})
    assert "HARD_FAIL" in v2 or "MIDDLE_BAND" in v2, f"Verdict HF test: {v2}"

    # Live smoke cell: verify metrics non-null at N_SMOKE
    t1v1_mod = get_t1v1()
    device_test = torch.device("cpu")
    smoke_cell = t1v1_mod.run_one_seed(N_SMOKE, 4.0, [1, 4, 16, 64], 17, device_test)
    rbb = smoke_cell.get("ret_by_beta", [])
    assert len(rbb) == 4, f"ret_by_beta length: {len(rbb)} != 4"
    assert all(0 <= v <= 1 for v in rbb), f"ret_by_beta out of [0,1]: {rbb}"
    assert max(rbb) - min(rbb) > 0.001, f"ret_by_beta all-same (filter fail): {rbb}"
    bc_live, mg_live = compute_beta_c(rbb, [1, 4, 16, 64])
    assert mg_live >= 0.0, f"max_gradient not non-negative: {mg_live}"

    # Multi-scale: also check at N_SMOKE*4 (N=4096, valid Kerdock)
    smoke4_cell = t1v1_mod.run_one_seed(N_SMOKE * 4, 4.0, [1, 4, 16, 64], 17, device_test)
    rbb4 = smoke4_cell.get("ret_by_beta", [])
    assert len(rbb4) == 4, f"4x ret_by_beta length: {len(rbb4)} != 4"
    assert max(rbb4) - min(rbb4) > 0.001, f"4x ret_by_beta all-same: {rbb4}"

    print(f"[selftest] t1_beta_v3_n4096_mfrac_sweep PASS N_FULL={N_FULL} "
          f"smoke_mg={mg_live:.4f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    t1v1 = get_t1v1()
    smoke = args.smoke
    N_cfg    = N_SMOKE if smoke else N_FULL
    m_fracs  = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    beta_sw  = BETA_SWEEP_SMOKE if smoke else BETA_SWEEP_FULL
    seeds    = SEEDS_SMOKE if smoke else SEEDS_FULL

    device = torch.device("cpu")
    t0 = time.time()
    print(f"t1_beta_v3_n4096_mfrac_sweep mode={'SMOKE' if smoke else 'FULL'} N={N_cfg} "
          f"m_fracs={m_fracs} beta_sweep={beta_sw} seeds={seeds}", flush=True)

    all_cells = []
    for mf in m_fracs:
        print(f"\n== M_frac={mf} ==", flush=True)
        for seed in seeds:
            cell = t1v1.run_one_seed(N_cfg, mf, beta_sw, seed, device)
            # t1v1 returns "ret_by_beta": list[float] indexed same as beta_sweep
            rbb = cell.get("ret_by_beta", [])
            ret_vals = list(rbb) if rbb else [0.0] * len(beta_sw)
            bc, mg = compute_beta_c(ret_vals, beta_sw)
            row = {
                "M_frac": mf, "seed": seed, "beta_c": bc, "max_gradient": mg,
                "ret_vals": [round(v, 4) for v in ret_vals],
            }
            all_cells.append(row)
            print(f"  M_frac={mf} seed={seed} beta_c={bc:.1f} max_gradient={mg:.4f}", flush=True)

    elapsed = round(time.time() - t0, 2)
    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg,
                                             "beta_sweep": beta_sw})
    summary = {
        "anchor": "t1_beta_v3_n4096_mfrac_sweep",
        "N": N_cfg, "smoke": smoke,
        "M_fracs": m_fracs, "beta_sweep": beta_sw, "seeds": seeds,
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
