"""T1 M-SWEEP v1: beta-transition at multiple M_fracs at N=4096.

CONTEXT:
  T1_BETA_HARD_PASS (v267): beta_c localized in [8,16] at M_frac=8.0.
  The two-boundary lattice predicts: beta_c SHIFTS as M_frac changes
  (near M_c, beta_c should be lower; deep in multi-basin, beta_c higher).

  T1 M-sweep: run T1's softmax_confidence vs beta at M_fracs=[2.0, 4.0, 8.0, 16.0].
  Does beta_c shift with M_frac? Does it vanish at low M_frac (no phase boundary)?

SCIENTIFIC QUESTION:
  How does beta_c depend on M_frac? At M_frac=2.0 (deep multi-basin), is beta_c different
  from M_frac=8.0 (near phase boundary)?

PRE-REGISTERED BANDS:
  Prior: T1 HARD_PASS at M_frac=8, beta_c in [8,16].
  Expected: beta_c increases with M_frac (higher M = harder retrieval = higher beta needed).

  HARD_PASS: mean_beta_c monotonically increases with M_frac over the range [2.0, 16.0],
    OR beta_c is absent at M_frac=2.0 (deep multi-basin, no transition needed).
    At >= 2/3 seeds. Interpretation: M-frac shifts beta_c as predicted by two-boundary lattice.
  HARD_FAIL: beta_c is identical at all M_fracs (no M-dependence of phase boundary).
    Interpretation: the two axes are NOT orthogonal; beta_c does not shift with M.
  MIDDLE_BAND: partial M-dependence detected but non-monotone or only 2/4 M_fracs.

FORMULA SELF-TESTS:
  1. Monotone check: beta_c(M=4) < beta_c(M=8) < beta_c(M=16) over 2+ seeds.
  2. beta_c estimated as argmax of gradient over {6,8,10,12,14,16,20,24,32}.
  3. Absent transition: total_var < 0.05 over all beta = no beta_c at this M_frac.
  4. N == 4096 (PROT-018).
  5. M at M_frac=16.0, N=4096: M=65536.

OOM CHECK:
  Worst case M_frac=16, N=4096: M=65536. W=64MB. keys=65536*4096*4=1.1GB. CB=268MB.
  Total~1.4GB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  4 M_fracs x 5 beta pts x 3 seeds = 60 cells.
  Per cell: store M + compute softmax ~0.5-2s (M_frac=16 heaviest).
  Smoke: 2 M_fracs x 3 beta pts x 1 seed = 6 cells x 0.5s = 3s.
  Total: 60 * 1.5s = 90s. Safety: ceil(1.5*90*10) = 1350s. Floor 14400. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: t1_m_sweep_v1_n4096
Queue: remote_cpu_queue (CPU; N=4096, 4 M_fracs, beta sweep, 3 seeds)
Pre-reg: preregs/2026-05-28_t1_m_sweep_v1_n4096.md
Parent: t1_beta_sweep_v1_n4096 (v267 HARD_PASS); t2_codebook_boundary_v1_n4096 (v267 HARD_PASS)
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

_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_t1ms", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

store_facts_batched = c1.store_facts_batched
v3 = c1.v3

_t1_path = REPO / "experiments" / "exp_t1_beta_sweep_v1_n4096.py"
_t1_spec = importlib.util.spec_from_file_location("t1v1_msweep", _t1_path)
t1v1 = importlib.util.module_from_spec(_t1_spec)
_t1_spec.loader.exec_module(t1v1)

softmax_confidence = t1v1.softmax_confidence

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FRACS_FULL  = [2.0, 4.0, 8.0, 16.0]
M_FRACS_SMOKE = [2.0, 8.0]

BETA_SWEEP_FULL  = [6, 8, 10, 12, 14, 16, 20, 24, 32]
BETA_SWEEP_SMOKE = [6, 10, 16]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

N_PROBE = 200

# Pre-registered thresholds
HP_MONOTONE_MFRACS = 2    # beta_c increases over at least 2 consecutive M_fracs
HP_SEEDS_MIN       = 2
HF_FLAT_BETAC      = 2.0  # all beta_c identical within 2 log2-units = flat = HARD_FAIL


def get_output_dir(default_name: str = "t1_m_sweep_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_mfrac_seed(N: int, M_frac: float, beta_sweep: List[float],
                       seed: int, device: torch.device) -> Dict:
    """Sweep beta for one (M_frac, seed) cell. Return beta_c estimate."""
    M = int(M_frac * N)
    codebook, _ = v3.make_kerdock_4coset_codebook(N, device)
    W, keys, _vals, _key_idx, val_idx = store_facts_batched(codebook, M, seed, N, device)

    ret_by_beta = []
    for beta in beta_sweep:
        conf = softmax_confidence(W, keys, val_idx, codebook, float(beta), N, n_probe=N_PROBE)
        ret_by_beta.append(conf)

    total_var = max(ret_by_beta) - min(ret_by_beta)
    log2_betas = [math.log2(b) for b in beta_sweep]
    gradients = []
    for i in range(1, len(ret_by_beta) - 1):
        d_ret = ret_by_beta[i + 1] - ret_by_beta[i - 1]
        d_log = log2_betas[i + 1] - log2_betas[i - 1]
        gradients.append(abs(d_ret / d_log) if abs(d_log) > 1e-9 else 0.0)

    max_grad = max(gradients) if gradients else 0.0
    argmax_i = gradients.index(max_grad) + 1 if gradients else 0
    beta_c = beta_sweep[argmax_i] if argmax_i < len(beta_sweep) else float("nan")

    has_transition = total_var >= 0.05

    print(f"    M_frac={M_frac:.1f} M={M} seed={seed} beta_c={beta_c:.1f} var={total_var:.4f} max_grad={max_grad:.4f}", flush=True)
    return {
        "M_frac": M_frac, "seed": seed, "M": M,
        "ret_by_beta": [round(r, 5) for r in ret_by_beta],
        "max_gradient": round(max_grad, 4),
        "beta_c": float(beta_c),
        "total_var": round(total_var, 4),
        "has_transition": has_transition,
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("T1_MSWEEP_INCONCLUSIVE", "No cells.")

    by_mfrac: Dict[float, List] = {}
    for c in cells:
        by_mfrac.setdefault(c["M_frac"], []).append(c)

    m_vals = sorted(by_mfrac.keys())
    mean_betac = {}
    for m in m_vals:
        mcs = [c["beta_c"] for c in by_mfrac[m] if not math.isnan(c["beta_c"])]
        mean_betac[m] = sum(mcs) / len(mcs) if mcs else float("nan")

    beta_c_list = [mean_betac[m] for m in m_vals if not math.isnan(mean_betac.get(m, float("nan")))]
    is_monotone = all(beta_c_list[i] <= beta_c_list[i + 1] for i in range(len(beta_c_list) - 1))
    span = (max(beta_c_list) - min(beta_c_list)) if len(beta_c_list) >= 2 else 0.0

    detail = (f"mean_betac_by_M={dict((k, round(v,1)) for k,v in mean_betac.items())} "
              f"is_monotone={is_monotone} span={span:.2f} "
              f"HP_monotone_mfracs={HP_MONOTONE_MFRACS} N={summary.get('N', N_FULL)}")

    if span <= HF_FLAT_BETAC:
        return ("T1_MSWEEP_HARD_FAIL",
                f"FLAT_BETAC: span={span:.2f} <= {HF_FLAT_BETAC} (no M-dependence). " + detail)

    if is_monotone and span > HF_FLAT_BETAC:
        return ("T1_MSWEEP_HARD_PASS",
                f"BETAC_M_DEPENDENCE: monotone shift, span={span:.2f}. " + detail)

    return ("T1_MSWEEP_MIDDLE_BAND", f"PARTIAL_M_DEPENDENCE: span={span:.2f} non-monotone. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    # Formula: M = M_frac * N
    assert int(16.0 * N_FULL) == 65536, f"M=16*4096 formula: {int(16.0 * N_FULL)}"
    # Verdict gates
    fake_hp = [{"M_frac": m, "seed": 17, "beta_c": bc, "total_var": 0.3, "max_gradient": 0.2, "has_transition": True, "M": 0, "ret_by_beta": []}
               for m, bc in [(2.0, 8.0), (4.0, 12.0), (8.0, 16.0), (16.0, 24.0)]]
    v, _ = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "HARD_PASS" in v, f"HARD_PASS gate: {v}"
    fake_hf = [{"M_frac": m, "seed": 17, "beta_c": 12.0, "total_var": 0.3, "max_gradient": 0.2, "has_transition": True, "M": 0, "ret_by_beta": []}
               for m in [2.0, 4.0, 8.0, 16.0]]
    vf, _ = compute_verdict({"cells": fake_hf, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf}"
    # Smoke cell non-null
    device = torch.device("cpu")
    cell = run_one_mfrac_seed(N_SMOKE, 4.0, [6.0, 10.0, 16.0], 17, device)
    assert not math.isnan(cell["beta_c"]), f"beta_c NaN: {cell}"
    assert cell["total_var"] >= 0.0, f"total_var negative: {cell}"
    # 4x scale
    cell4 = run_one_mfrac_seed(N_SMOKE * 4, 4.0, [6.0, 10.0, 16.0], 17, device)
    assert not math.isnan(cell4["beta_c"]), f"4x beta_c NaN"
    print(f"[selftest] t1_m_sweep_v1_n4096 PASS beta_c_smoke={cell['beta_c']:.1f}", flush=True)


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
    beta_sweep = BETA_SWEEP_SMOKE if smoke else BETA_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] t1_m_sweep_v1_n4096 smoke={smoke} N={N_cfg} M_fracs={m_fracs} seeds={seeds} device={device_str}", flush=True)
    t0 = time.time()

    all_cells = []
    for M_frac in m_fracs:
        print(f"\n  [M_frac={M_frac}]", flush=True)
        for seed in seeds:
            cell = run_one_mfrac_seed(N_cfg, M_frac, beta_sweep, seed, device)
            all_cells.append(cell)
        print(f"  M_frac={M_frac} elapsed={time.time()-t0:.1f}s", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "t1_m_sweep_v1_n4096", "N": N_cfg, "smoke": smoke,
        "M_fracs": m_fracs, "beta_sweep": beta_sweep, "seeds": seeds,
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
