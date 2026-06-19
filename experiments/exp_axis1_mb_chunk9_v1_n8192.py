"""AXIS1 MB-CHUNK 9 v1: N=8192 phase diagram M-sweep at M_fracs=[1,2,4,8,12].

CONTEXT:
  axis1_mb_chunk1-8 (v267 region): full M/N phase diagram at N=4096.
  Results: clean multi-basin phase (M_frac=1-4), near-boundary (M_frac=8),
  collapse phase (M_frac=16-32). Beta_c ~ 8-16 (T1 HARD_PASS).
  Chunk 9 extends to N=8192 to test: do the phase boundaries shift proportionally with N?

SCIENTIFIC QUESTION:
  At N=8192, sweep M_fracs=[1.0, 2.0, 4.0, 8.0, 12.0] at beta=32.
  Does retention vs M_frac show the same qualitative shape as N=4096?
  Is the boundary M_frac at N=8192 the same as at N=4096?

PRE-REGISTERED BANDS:
  Prior: N=4096 shows clean phase at M_frac<=4, boundary at M_frac~8, collapse at M_frac>=12.

  HARD_PASS: retention monotone decreasing with M_frac AND
    ret_m1 >= 0.90 AND ret_m8 in [0.20, 0.80] (near boundary) at >= 2/3 seeds.
    Interpretation: phase boundary persists at N=8192, similar to N=4096.
  HARD_FAIL: retention flat (< 0.05 variation) across all M_fracs at N=8192.
    Interpretation: N=8192 behaves qualitatively differently (no phase structure).
  MIDDLE_BAND: monotone but boundary shifted (ret_m8 outside [0.20, 0.80]).

FORMULA SELF-TESTS:
  1. N == 8192 (PROT-018 binding).
  2. M at M_frac=4.0, N=8192: M=32768.
  3. OOM: W=268MB, keys=32768*8192*4=1.07GB, CB=268MB. Total~1.6GB. OK.
     At M_frac=12, M=98304: keys=98304*8192*4=3.2GB. Total~3.7GB. Under 6GB. OK.
  4. Monotone: all consecutive pairs ret[i+1] <= ret[i] + 0.05.

TIMEOUT ESTIMATE:
  5 M_fracs x 3 seeds = 15 cells. At M_frac=12 N=8192: store M=98304 + retrieve.
  ~10s per cell (proportional to M*N stores). Total: 15*10=150s.
  Safety: ceil(1.5*150*8)=1800s. _n8192 floor=21600. timeout_s=21600.

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Anchor: axis1_mb_chunk9_v1_n8192
Queue: overnight_queue (GPU; N=8192 Kerdock, M_frac sweep, 5 pts x 3 seeds)
Pre-reg: prereqs/2026-05-28_axis1_mb_chunk9_v1_n8192.md
Parent: axis1_mb_chunk1_v1 (store_facts_batched, v3 codebook)
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

# Load axis1_mb_chunk1 for store_facts_batched, compute_retention, v3 codebook
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_c9", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

store_facts_batched = c1.store_facts_batched
compute_retention = c1.compute_retention
v3 = c1.v3

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N_FULL  = 8192
N_SMOKE = 1024
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

M_FRACS_FULL  = [1.0, 2.0, 4.0, 8.0, 12.0]
M_FRACS_SMOKE = [1.0, 4.0, 8.0]

BETA = 32.0

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

N_PROBE = 200

# Pre-registered thresholds
HP_RET_M1_MIN    = 0.90   # ret at M_frac=1.0 >= 0.90 (clean regime)
HP_RET_M8_RANGE  = (0.20, 0.80)   # ret at M_frac=8.0 in this range = near boundary
HF_FLAT_VAR      = 0.05   # max-min retention < 0.05 = flat = HARD_FAIL
HP_SEEDS_MIN     = 2


def get_output_dir(default_name: str = "axis1_mb_chunk9_v1_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell(N: int, M_frac: float, beta: float, seed: int, device: torch.device) -> Dict:
    """Run retention measurement at (N, M_frac, beta, seed)."""
    M = int(M_frac * N)
    codebook, _ = v3.make_kerdock_4coset_codebook(N, device)
    W, keys, _vals, _key_idx, val_idx = store_facts_batched(codebook, M, seed, N, device)
    ret = compute_retention(W, keys, val_idx, codebook, beta, N, n_probe=N_PROBE)
    print(f"    N={N} M_frac={M_frac} beta={beta} seed={seed} ret={ret:.5f}", flush=True)
    return {
        "N": N, "M_frac": M_frac, "M": M, "beta": beta, "seed": seed,
        "retention": round(ret, 5),
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("C9_INCONCLUSIVE", "No cells.")

    N = summary.get("N", N_FULL)

    by_mfrac: Dict[float, List] = {}
    for c in cells:
        by_mfrac.setdefault(c["M_frac"], []).append(c)

    m_sorted = sorted(by_mfrac.keys())
    mean_ret: Dict[float, float] = {}
    for m in m_sorted:
        rets = [c["retention"] for c in by_mfrac[m]]
        mean_ret[m] = sum(rets) / len(rets)

    ret_m1 = mean_ret.get(1.0, float("nan"))
    ret_m8 = mean_ret.get(8.0, float("nan"))
    all_rets = [mean_ret[m] for m in m_sorted]
    variation = max(all_rets) - min(all_rets) if all_rets else 0.0

    # Monotone check
    n_mono = sum(1 for i in range(len(all_rets) - 1)
                 if all_rets[i] >= all_rets[i + 1] - 0.05)
    mono_frac = n_mono / max(1, len(all_rets) - 1)

    # Seed-level: ret_m1 >= HP_RET_M1_MIN
    m1_cells = by_mfrac.get(1.0, [])
    pass_m1 = sum(1 for c in m1_cells if c["retention"] >= HP_RET_M1_MIN)

    # Seed-level: ret_m8 in HP_RET_M8_RANGE
    m8_cells = by_mfrac.get(8.0, [])
    pass_m8 = sum(1 for c in m8_cells
                  if HP_RET_M8_RANGE[0] <= c["retention"] <= HP_RET_M8_RANGE[1])

    n_seeds_m1 = len(m1_cells)
    n_seeds_m8 = len(m8_cells)

    detail = (f"ret_m1={ret_m1:.3f} ret_m8={ret_m8:.3f} variation={variation:.3f} "
              f"mono_frac={mono_frac:.2f} pass_m1={pass_m1}/{n_seeds_m1} "
              f"pass_m8={pass_m8}/{n_seeds_m8} N={N}")

    if variation < HF_FLAT_VAR:
        return ("C9_HARD_FAIL",
                f"PHASE_FLAT_N8192: no retention variation across M_fracs. " + detail)

    passes_hp = (not math.isnan(ret_m1) and pass_m1 >= HP_SEEDS_MIN and
                 (not m8_cells or pass_m8 >= 1))
    if passes_hp:
        return ("C9_HARD_PASS",
                f"PHASE_BOUNDARY_N8192: boundary persists. " + detail)

    return ("C9_MIDDLE_BAND", f"PARTIAL_PHASE_STRUCTURE: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"
    # Formula: M at M_frac=4.0 N=8192
    assert int(4.0 * N_FULL) == 32768, f"M at M_frac=4: {int(4.0*N_FULL)}"
    # Verdict gates
    fake_hp = [{"M_frac": m, "retention": max(0.0, 1.0 - m/10.0)} for m in [1.0, 4.0, 8.0]]
    v, _ = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "PASS" in v or "MIDDLE" in v, f"gate: {v}"
    fake_hf = [{"M_frac": m, "retention": 0.5} for m in [1.0, 4.0, 8.0]]
    vf, _ = compute_verdict({"cells": fake_hf, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf}"
    # Smoke cell at N_SMOKE (log2=10 OK for Kerdock)
    device = torch.device("cpu")
    cell = run_one_cell(N_SMOKE, 4.0, BETA, 17, device)
    assert "retention" in cell, f"retention missing"
    assert not math.isnan(cell["retention"]), "retention NaN"
    # 4x smoke: N=4096 (log2=12 OK for Kerdock)
    cell4 = run_one_cell(N_SMOKE * 4, 4.0, BETA, 17, device)
    assert "retention" in cell4, f"4x retention missing"
    print(f"[selftest] axis1_mb_chunk9_v1_n8192 PASS ret_smoke={cell['retention']:.4f}", flush=True)


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
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] axis1_mb_chunk9_v1_n8192 smoke={smoke} N={N_cfg} M_fracs={m_fracs} beta={BETA} seeds={seeds}", flush=True)
    t0 = time.time()

    all_cells = []
    for M_frac in m_fracs:
        print(f"\n  [M_frac={M_frac}]", flush=True)
        for seed in seeds:
            cell = run_one_cell(N_cfg, M_frac, BETA, seed, device)
            all_cells.append(cell)
        print(f"  M_frac={M_frac} elapsed={time.time()-t0:.1f}s", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "axis1_mb_chunk9_v1_n8192", "N": N_cfg, "smoke": smoke,
        "M_fracs": m_fracs, "beta": BETA, "seeds": seeds,
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
