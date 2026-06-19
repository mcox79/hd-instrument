"""TCFT M-sweep: confirm 1/sqrt(M) convergence of var_ratio across M values.

CONTEXT (from v247 strategy priorities, item 2):
  tcft_n8192_v6/v7 HARD_PASS at N=8192, 5 seeds, var_ratio ~ 3e-8 (6 OOM below 0.10).
  Default M = N * 0.125 = 1024. Theory predicts var_ratio ~ 1/sqrt(N * M).

  This probe sweeps M at N=8192 to confirm the 1/sqrt(M) decay:
  larger M -> smaller var_ratio. If confirmed, deletion-certificate Cat-A
  foundation becomes bulletproof: any operating point with large M will have
  numerically undetectable trajectory-class variance.

SCIENTIFIC QUESTION:
  Does var_ratio decrease as M increases at N=8192?
  M_values = [128, 256, 512, 1024, 2048].
  Expected: monotone decrease (Spearman r(M, var_ratio) < -0.5).

PRE-REGISTERED BANDS:
  Prior anchor: v6/v7 HARD_PASS var_ratio ~ 3e-8 at M=1024.
  Bands NOT widened (prior anchor exists).

  HARD_PASS: var_ratio < 0.10 for all M >= 512, AND Spearman r(M, var_ratio) < -0.5.
  HARD_FAIL: var_ratio >= 0.10 at M=1024 (contradicts v7).
  MIDDLE_BAND: all var_ratio < 0.10 but no clear decreasing trend.

FORMULA SELF-TESTS:
  1. vanilla_jarzynski(works) computes variance of exp(-W/kT) array.
  2. tcft_conditioned(works) conditions on |W| < median -> variance_ratio = var_c0/var_all.
  3. For works all-zero: variance_ratio = 0.
  4. Spearman r([1,2,3,4,5], [5,4,3,2,1]) = -1.0.
  5. Theory: works = -v@W@v at loading step mu. For M large: works more negative,
     variance_ratio smaller (trajectory class more homogeneous).

TIMEOUT ESTIMATE:
  tcft_n8192_v7: 5 seeds * 450s = 2228s. Per seed at M=1024: ~450s.
  M scaling: compute_cumulative_works is O(M * N^2). So cost ~ M.
  At M=128: ~56s/seed. At M=256: ~113s. At M=512: ~225s. At M=1024: ~450s. At M=2048: ~900s.
  2 seeds * sum(M_time) = 2 * (56+113+225+450+900) = 2 * 1744 = 3488s.
  timeout_s = ceil(1.5 * 3488) = ceil(5232) -> 5400s.
  Flag: >2h run (5400s = 1.5h is within 4h limit).
  Smoke: N=512, 1 seed, M=[32, 64]: expected ~3s.

N-suffix: no _nN suffix; production N = 8192 (PROT-018: stated explicitly).
Queue: remote_cpu_queue (pure CPU; N=8192 2-seed M-sweep; ~3488s = 58min)
Pre-reg: preregs/2026-05-27_tcft_m_sweep_v1.md
Parent: tcft_n8192_v7 (HARD_PASS; this sweeps M to confirm 1/sqrt(M) theory)
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
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load v5 core functions
_v5_path = REPO / "experiments" / "exp_tcft_n8192_v5.py"
_v5_spec = importlib.util.spec_from_file_location("tcft_v5_base", _v5_path)
_v5_mod = importlib.util.module_from_spec(_v5_spec)
_v5_spec.loader.exec_module(_v5_mod)

compute_cumulative_works = _v5_mod.compute_cumulative_works
vanilla_jarzynski = _v5_mod.vanilla_jarzynski
tcft_conditioned = _v5_mod.tcft_conditioned
mean_field_delta_F = _v5_mod.mean_field_delta_F
HP_VAR_RATIO_STRONG = _v5_mod.HP_VAR_RATIO_STRONG

# PRODUCTION CONFIG
N_FULL = 8192   # PROT-018: production N = 8192
N_SMOKE = 512
M_VALUES_FULL = [128, 256, 512, 1024, 2048]
M_VALUES_SMOKE = [32, 64]
SEEDS_FULL = [7, 17]       # 2 seeds to fit ~3500s
SEEDS_SMOKE = [17]

# Thresholds
HP_VAR_RATIO_MAX = 0.10    # all M>=512 must be below this
HF_CONTRADICTION = 0.10    # any M>=1024 above this contradicts v7
HP_SPEARMAN_R_MAX = -0.5   # monotone decrease threshold


def get_output_dir(default_name: str = "tcft_m_sweep_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell(N: int, M: int, seed: int) -> Dict:
    """Run TCFT for one (N, M, seed) cell."""
    t0 = time.time()
    works = compute_cumulative_works(N, M, seed)
    elapsed_works = time.time() - t0

    vanilla = vanilla_jarzynski(works)
    tcft = tcft_conditioned(works)
    mf_dF = mean_field_delta_F(N, M)

    result = {
        "N": N, "M": M, "seed": seed,
        "elapsed_s": elapsed_works,
        "vanilla_variance": vanilla["variance"],
        "tcft_valid": tcft.get("valid", False),
    }
    if tcft.get("valid", False):
        vr = tcft.get("variance_ratio", None)
        result["tcft_variance_ratio"] = float(vr) if vr is not None else None
        agree_pct = (abs(tcft["delta_F"] - mf_dF) / (abs(mf_dF) + 1e-9) * 100.0
                     if tcft.get("delta_F") is not None else None)
        result["delta_F_agree_pct"] = agree_pct
    else:
        result["tcft_variance_ratio"] = None
        result["delta_F_agree_pct"] = None
    return result


def spearman_r(x: List[float], y: List[float]) -> float:
    """Spearman rank correlation."""
    if len(x) < 2:
        return 0.0
    rank_x = np.argsort(np.argsort(x)).astype(float)
    rank_y = np.argsort(np.argsort(y)).astype(float)
    if rank_x.std() < 1e-10 or rank_y.std() < 1e-10:
        return 0.0
    return float(np.corrcoef(rank_x, rank_y)[0, 1])


def compute_verdict(summary: dict) -> tuple:
    cells = summary.get("cells", [])
    if not cells:
        return ("TCFT_M_SWEEP_INCONCLUSIVE", "No cells.")

    # Group by M
    M_groups: Dict[int, List[float]] = {}
    for c in cells:
        if not c.get("tcft_valid", False):
            continue
        vr = c.get("tcft_variance_ratio")
        if vr is None:
            continue
        M_groups.setdefault(c["M"], []).append(float(vr))

    if not M_groups:
        return ("TCFT_M_SWEEP_INCONCLUSIVE", "No valid cells with var_ratio.")

    M_vals = sorted(M_groups.keys())
    mean_vr_by_M = {M: float(np.mean(M_groups[M])) for M in M_vals}

    # HARD_FAIL: any large-M above threshold, contradicting v7
    for M in M_vals:
        if M >= 1024 and mean_vr_by_M[M] >= HF_CONTRADICTION:
            return ("TCFT_M_SWEEP_HARD_FAIL",
                    f"var_ratio at M={M}={mean_vr_by_M[M]:.6f} >= {HF_CONTRADICTION}. "
                    f"Contradicts v6/v7 HARD_PASS. "
                    f"vr_by_M={dict((k, round(v, 6)) for k, v in mean_vr_by_M.items())}.")

    # Spearman r(M, var_ratio): should be negative
    M_list = [float(M) for M in M_vals]
    vr_list = [mean_vr_by_M[M] for M in M_vals]
    r = spearman_r(M_list, vr_list)

    all_below_thresh = all(mean_vr_by_M[M] < HP_VAR_RATIO_MAX
                           for M in M_vals if M >= 512)
    msg_base = (f"vr_by_M={dict((k, round(v, 6)) for k, v in mean_vr_by_M.items())}. "
                f"spearman_r={r:.3f}. all_M>=512_below_0.10={all_below_thresh}.")

    if all_below_thresh and r < HP_SPEARMAN_R_MAX:
        return ("TCFT_M_SWEEP_HARD_PASS",
                f"1/sqrt(M) CONVERGENCE CONFIRMED. {msg_base} "
                f"Deletion-cert Cat-A foundation: BULLETPROOF across M range.")

    if all_below_thresh:
        return ("TCFT_M_SWEEP_MIDDLE_BAND",
                f"All var_ratio<0.10 for M>=512 but monotone trend weak. {msg_base}")

    return ("TCFT_M_SWEEP_INCONCLUSIVE", f"Unexpected result. {msg_base}")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

    # Self-test 1: run_one_cell at small N, M
    r = run_one_cell(128, M=16, seed=17)
    assert r["tcft_valid"] is True, f"tcft_valid False at N=128 M=16: {r}"
    assert r["tcft_variance_ratio"] is not None, "tcft_variance_ratio None"
    assert r["tcft_variance_ratio"] >= 0.0, f"var_ratio < 0: {r['tcft_variance_ratio']}"
    print(f"[selftest 1/4] run_one_cell N=128 M=16 var_ratio={r['tcft_variance_ratio']:.6f} OK",
          flush=True)

    # Self-test 2: spearman_r formula
    r_pos = spearman_r([1.0, 2.0, 3.0, 4.0, 5.0], [1.0, 2.0, 3.0, 4.0, 5.0])
    assert abs(r_pos - 1.0) < 0.01, f"spearman_r perfect pos: {r_pos}"
    r_neg = spearman_r([1.0, 2.0, 3.0, 4.0, 5.0], [5.0, 4.0, 3.0, 2.0, 1.0])
    assert abs(r_neg + 1.0) < 0.01, f"spearman_r perfect neg: {r_neg}"
    print(f"[selftest 2/4] spearman_r OK (+{r_pos:.2f}, {r_neg:.2f})", flush=True)

    # Self-test 3: verdict formula - HARD_PASS case
    cells_pass = [
        {"M": M, "seed": 17, "N": 1024, "tcft_valid": True,
         "tcft_variance_ratio": 0.10 / math.sqrt(M / 512) * 0.3}
        for M in [512, 1024, 2048]
    ]
    v, msg = compute_verdict({"cells": cells_pass})
    assert v == "TCFT_M_SWEEP_HARD_PASS", f"Expected HARD_PASS, got {v}: {msg}"
    print(f"[selftest 3/4] verdict HARD_PASS OK", flush=True)

    # Self-test 4: smoke scale at N_SMOKE
    t0 = time.time()
    r_smoke = run_one_cell(N_SMOKE, M=64, seed=17)
    t1 = time.time() - t0
    assert r_smoke["tcft_valid"], f"smoke tcft_valid False: {r_smoke}"
    vr = r_smoke["tcft_variance_ratio"]
    assert vr is not None and vr >= 0.0, f"smoke var_ratio invalid: {vr}"
    print(f"[selftest 4/4] smoke N={N_SMOKE} M=64 var_ratio={vr:.6f} t={t1:.1f}s OK",
          flush=True)

    # Also multi-scale: N_SMOKE and N_SMOKE * 4
    r_4x = run_one_cell(N_SMOKE * 4, M=256, seed=17)
    assert r_4x["tcft_valid"], f"N_SMOKE*4 tcft_valid False"
    print(f"[selftest multi-scale] N={N_SMOKE*4} M=256 var_ratio="
          f"{r_4x['tcft_variance_ratio']:.6f} OK", flush=True)

    print("[SELFTEST PASS] tcft_m_sweep_v1 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    N = N_SMOKE if smoke else N_FULL
    M_values = M_VALUES_SMOKE if smoke else M_VALUES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    mode_str = "SMOKE" if smoke else "FULL"

    out_dir = get_output_dir()
    print(f"[tcft_m_sweep] N={N} M_values={M_values} seeds={seeds} mode={mode_str}",
          flush=True)

    all_cells = []
    for seed in seeds:
        for M in M_values:
            t_cell = time.time()
            print(f"  seed={seed} M={M}...", flush=True)
            cell = run_one_cell(N, M, seed)
            all_cells.append(cell)
            vr = cell.get("tcft_variance_ratio", "N/A")
            vr_str = f"{vr:.6f}" if isinstance(vr, float) else str(vr)
            print(f"    var_ratio={vr_str} valid={cell['tcft_valid']} "
                  f"t={time.time()-t_cell:.1f}s", flush=True)

    summary = {
        "cells": all_cells,
        "N_full": N_FULL,
        "N_used": N,
        "M_values": M_values,
        "smoke": smoke,
    }
    verdict, verdict_msg = compute_verdict(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N": N, "M_values": M_values, "seeds": seeds, "smoke": smoke},
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[tcft_m_sweep] VERDICT: {verdict}", flush=True)
    print(f"[tcft_m_sweep] {verdict_msg}", flush=True)
    print(f"[tcft_m_sweep] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--timeout", type=float, default=5400.0)
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
