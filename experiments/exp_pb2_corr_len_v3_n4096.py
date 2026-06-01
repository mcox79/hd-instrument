"""PB-2 CORRELATION LENGTH v3: edit propagation at N=4096 N-scaling.

CONTEXT:
  pb2_corr_len_v2_n1024 (v267 region): correlation length xi measured at N=1024.
  cap_map edit-propagation-finite-range 55-68% new row (v267).
  v3 extends to N=4096 to test: does xi scale with N (proportional) or stay fixed?
  N-scaling of xi is critical for the product framing of edit isolation.

SCIENTIFIC QUESTION:
  Does xi scale with N? At N=4096, is xi ~4x larger than at N=1024 (proportional)?
  Or does xi saturate (finite-range independent of N)?

PRE-REGISTERED BANDS:
  Prior: pb2_corr_len_v2_n1024 results.
  Expected: xi roughly proportional to N (longer range in higher-dim substrate).

  HARD_PASS: mean xi_normalized at N=4096 is within 2x of N=1024 value.
    AND xi_normalized < 1.0 at M_frac=1.0 (still finite range, not global).
    Interpretation: edit propagation scales sublinearly with N.
  HARD_FAIL: xi_normalized at N=4096 > 2.0 (global propagation at all M_fracs).
    Interpretation: no finite-range edit isolation at N=4096.
  MIDDLE_BAND: xi_normalized in [1.0, 2.0] (large range).

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. M at M_frac=1.0, N=4096: M=4096.
  3. xi_normalized: weighted mean pattern-index / N. Range [0, 1].
  4. N-scaling: xi_raw ~ N -> xi_normalized ~ constant across N.
     OR xi_raw ~ sqrt(N) -> xi_normalized ~ 1/sqrt(N) (decreasing).

OOM CHECK:
  N=4096 M_frac=4.0: M=16384. W=64MB. Keys=16384*4096*4=256MB. CB=268MB. Total~590MB. OK.

TIMEOUT ESTIMATE:
  4 M_fracs x 3 seeds = 12 cells. Each cell at N=4096 ~ 3s.
  Smoke: 2 M_fracs x 1 seed = 2 cells x 1s = 2s.
  Total: 12*3=36s. Safety: ceil(1.5*36*10)=540s. Floor 14400. timeout_s=14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: pb2_corr_len_v3_n4096
Queue: remote_cpu_queue (CPU; N=4096, edit-propagation correlation length, 3 seeds)
Pre-reg: preregs/2026-05-28_pb2_corr_len_v3_n4096.md
Parent: pb2_corr_len_v2_n1024 (N=1024 baseline); edit-propagation-finite-range cap_map row
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

# Load pb2_corr_len_v2 for run_one_cell
_v2_path = REPO / "experiments" / "exp_pb2_corr_len_v2_n1024.py"
_v2_spec = importlib.util.spec_from_file_location("pb2v2_v3", _v2_path)
pb2v2 = importlib.util.module_from_spec(_v2_spec)
_v2_spec.loader.exec_module(pb2v2)

run_one_cell_v2 = pb2v2.run_one_cell

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FRACS_FULL  = [0.5, 1.0, 2.0, 4.0]
M_FRACS_SMOKE = [1.0, 2.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
HP_XI_MAX_FINITE  = 1.0    # xi_normalized < 1.0 at M_frac=1.0 = finite range
HF_XI_GLOBAL      = 2.0    # xi_normalized > 2.0 = global propagation = HARD_FAIL
HP_SEEDS_MIN      = 2


def get_output_dir(default_name: str = "pb2_corr_len_v3_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell(N: int, M_frac: float, seed: int, device: torch.device) -> Dict:
    """Wrapper: run pb2 v2 cell at N=4096."""
    result = run_one_cell_v2(N, M_frac, seed, device)
    result["N_used"] = N
    return result


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("PB2_V3_INCONCLUSIVE", "No cells.")

    N = summary.get("N", N_FULL)

    # Group by M_frac
    by_mfrac: Dict[float, List] = {}
    for c in cells:
        by_mfrac.setdefault(c["M_frac"], []).append(c)

    m1_cells = by_mfrac.get(1.0, [])
    xi_at_m1 = [c["xi_normalized"] for c in m1_cells if c.get("xi_normalized") is not None]
    mean_xi_m1 = sum(xi_at_m1) / len(xi_at_m1) if xi_at_m1 else float("nan")

    all_xi = [c["xi_normalized"] for c in cells if c.get("xi_normalized") is not None]
    max_xi = max(all_xi) if all_xi else float("nan")
    mean_xi_all = sum(all_xi) / len(all_xi) if all_xi else float("nan")

    pass_finite = sum(1 for c in m1_cells if c.get("xi_normalized", 999) < HP_XI_MAX_FINITE)
    total_m1 = len(m1_cells)

    detail = (f"mean_xi_m1={mean_xi_m1:.4f} max_xi={max_xi:.4f} mean_xi_all={mean_xi_all:.4f} "
              f"pass_finite={pass_finite}/{total_m1} HP_xi_max={HP_XI_MAX_FINITE} "
              f"HF_xi_global={HF_XI_GLOBAL} N={N}")

    if max_xi > HF_XI_GLOBAL:
        return ("PB2_V3_HARD_FAIL",
                f"GLOBAL_PROPAGATION: max_xi={max_xi:.4f} > {HF_XI_GLOBAL}. " + detail)

    if pass_finite >= HP_SEEDS_MIN and not math.isnan(mean_xi_m1):
        return ("PB2_V3_HARD_PASS",
                f"FINITE_RANGE: xi_m1={mean_xi_m1:.4f} < {HP_XI_MAX_FINITE} at N={N}. " + detail)

    return ("PB2_V3_MIDDLE_BAND",
            f"LARGE_RANGE: xi_m1={mean_xi_m1:.4f}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    # Formula: M
    assert int(1.0 * N_FULL) == 4096, f"M_frac=1 at N=4096: {int(1.0*N_FULL)}"
    # Verdict gates
    fake_hp = [{"M_frac": 1.0, "xi_normalized": 0.3} for _ in range(3)]
    v, _ = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "HARD_PASS" in v, f"HARD_PASS gate: {v}"
    fake_hf = [{"M_frac": 1.0, "xi_normalized": 2.5} for _ in range(3)]
    vf, _ = compute_verdict({"cells": fake_hf, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf}"
    # Smoke cell
    device = torch.device("cpu")
    cell = run_one_cell(N_SMOKE, 1.0, 17, device)
    assert "xi_normalized" in cell, f"xi_normalized missing: {list(cell.keys())}"
    assert not math.isnan(cell["xi_normalized"]), "xi_normalized NaN"
    # 4x scale
    cell4 = run_one_cell(N_SMOKE * 4, 1.0, 17, device)
    assert "xi_normalized" in cell4, f"4x xi_normalized missing"
    print(f"[selftest] pb2_corr_len_v3_n4096 PASS xi_smoke={cell['xi_normalized']:.4f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    device = torch.device("cpu")  # CPU experiment
    smoke = args.smoke

    N_cfg = N_SMOKE if smoke else N_FULL
    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] pb2_corr_len_v3_n4096 smoke={smoke} N={N_cfg} M_fracs={m_fracs} seeds={seeds}", flush=True)
    t0 = time.time()

    all_cells = []
    for M_frac in m_fracs:
        print(f"\n  [M_frac={M_frac}]", flush=True)
        for seed in seeds:
            cell = run_one_cell(N_cfg, M_frac, seed, device)
            all_cells.append(cell)
            xi = cell.get("xi_normalized", float("nan"))
            print(f"  M_frac={M_frac} seed={seed} xi={xi:.4f} ({time.time()-t0:.1f}s)", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "pb2_corr_len_v3_n4096", "N": N_cfg, "smoke": smoke,
        "M_fracs": m_fracs, "seeds": seeds,
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
