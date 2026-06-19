"""KF-4 DRIFT DETECTION v3: cross-phase drift detection sensitivity at N=4096.

CONTEXT:
  kf4_drift_detect_v2 (prior, completed): drift detection confirmed.
  cap_map KF-phase-class new row (v267). This probe: does drift detection
  sensitivity (threshold for distinguishing drift) change near the phase boundary?

SCIENTIFIC QUESTION:
  At M_frac near M_c (phase boundary), is drift detection EASIER or HARDER?
  Prediction: near boundary, small changes to W have larger effect -> easier detection.

PRE-REGISTERED BANDS:
  No prior anchor for drift-sensitivity vs M_frac.

  HARD_PASS: drift_detection_gap (difference between drifted and undrifted state scores)
    >= 0.20 at M_frac=8.0 (near boundary) AND gap at M_frac=8.0 >= 1.5x gap at M_frac=2.0.
    Interpretation: drift detection enriched near phase boundary.
  HARD_FAIL: drift_detection_gap < 0.05 at ALL M_fracs (no detection).
  MIDDLE_BAND: gap >= 0.20 but ratio < 1.5x.

FORMULA SELF-TESTS:
  1. drift_gap = mean_ret_undrifted - mean_ret_drifted (after n_drift_steps weight edits).
  2. N == 4096 (PROT-018 binding).
  3. M at M_frac=8.0, N=4096: M=32768.
  4. n_drift_steps = 100 random weight updates.

OOM CHECK:
  M=32768, N=4096: W=64MB. Keys=32768*4096*4=537MB. CB=268MB. Total~870MB. OK.

TIMEOUT ESTIMATE:
  2 M_fracs x 3 seeds = 6 cells x 2s = 12s.
  Smoke: 1 M_frac x 1 seed x 2s = 2s.
  Safety: ceil(1.5*12*10)=180s. Floor 14400. timeout_s=14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: kf4_drift_detect_v3_n4096
Queue: remote_cpu_queue (CPU)
Pre-reg: preregs/2026-05-28_kf4_drift_detect_v3_n4096.md
Parent: kf4_drift_detect_v2 (prior drift detection); KF-phase-class cap_map row
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
_c1_spec = importlib.util.spec_from_file_location("axis1c1_kf4", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

store_facts_batched = c1.store_facts_batched
compute_retention = c1.compute_retention
v3 = c1.v3

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FRACS_FULL  = [2.0, 8.0]
M_FRACS_SMOKE = [2.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

BETA = 32.0
N_PROBE = 200
N_DRIFT_STEPS = 100   # number of weight perturbation steps to simulate drift

# Pre-registered thresholds
HP_DRIFT_GAP_MIN   = 0.20    # mean gap >= 0.20 at M_frac=8
HP_RATIO_MIN       = 1.5     # gap(M=8) / gap(M=2) >= 1.5
HF_NO_DETECT       = 0.05    # gap < 0.05 = no detection
HP_SEEDS_MIN       = 2


def get_output_dir(default_name: str = "kf4_drift_detect_v3_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell(N: int, M_frac: float, seed: int, device: torch.device) -> Dict:
    """Measure drift detection gap at (N, M_frac, seed)."""
    M = int(M_frac * N)
    codebook, _ = v3.make_kerdock_4coset_codebook(N, device)
    W, keys, _vals, _key_idx, val_idx = store_facts_batched(codebook, M, seed, N, device)

    # Baseline retention
    ret_base = compute_retention(W, keys, val_idx, codebook, BETA, N, N_PROBE)

    # Simulate drift: add random noise to W
    gen = torch.Generator(device=device).manual_seed(seed + 7777)
    C = codebook.shape[0]
    W_drifted = W.clone()
    for _ in range(N_DRIFT_STEPS):
        # Random outer product noise (like storing a random spurious pattern)
        k_rnd = torch.randint(0, C, (1,), generator=gen, device=device)
        v_rnd = torch.randint(0, C, (1,), generator=gen, device=device)
        noise_k = codebook[k_rnd[0]]
        noise_v = codebook[v_rnd[0]]
        W_drifted = W_drifted + torch.outer(noise_v, noise_k) / N * 0.01

    # Retention after drift
    ret_drifted = compute_retention(W_drifted, keys, val_idx, codebook, BETA, N, N_PROBE)

    drift_gap = ret_base - ret_drifted

    print(f"    N={N} M_frac={M_frac} M={M} seed={seed} ret_base={ret_base:.4f} "
          f"ret_drifted={ret_drifted:.4f} gap={drift_gap:.4f}", flush=True)
    return {
        "N": N, "M_frac": M_frac, "M": M, "seed": seed,
        "ret_base": round(ret_base, 5),
        "ret_drifted": round(ret_drifted, 5),
        "drift_gap": round(drift_gap, 5),
        "passes_hp": drift_gap >= HP_DRIFT_GAP_MIN,
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("KF4_V3_INCONCLUSIVE", "No cells.")

    by_mfrac: Dict[float, List] = {}
    for c in cells:
        by_mfrac.setdefault(c["M_frac"], []).append(c)

    m2_cells = by_mfrac.get(2.0, [])
    m8_cells = by_mfrac.get(8.0, [])

    mean_gap_m2 = sum(c["drift_gap"] for c in m2_cells) / max(1, len(m2_cells)) if m2_cells else None
    mean_gap_m8 = sum(c["drift_gap"] for c in m8_cells) / max(1, len(m8_cells)) if m8_cells else None

    all_gaps = [c["drift_gap"] for c in cells]
    max_gap = max(all_gaps) if all_gaps else 0.0

    # Smoke case (only 1 M_frac)
    if mean_gap_m8 is None:
        m2_str = f"{mean_gap_m2:.4f}" if mean_gap_m2 is not None else "N/A"
        detail = f"mean_gap_m2={m2_str} smoke_only=True"
        if mean_gap_m2 is not None and mean_gap_m2 >= HP_DRIFT_GAP_MIN:
            return ("KF4_V3_SMOKE_PASS", f"DRIFT_DETECTABLE_AT_M2: gap={m2_str}. " + detail)
        return ("KF4_V3_SMOKE_ONLY", f"PARTIAL: gap_m2={m2_str}. " + detail)

    ratio = mean_gap_m8 / max(mean_gap_m2, 1e-6) if mean_gap_m2 else 0.0
    pass_m8 = sum(1 for c in m8_cells if c["passes_hp"])

    detail = (f"mean_gap_m2={mean_gap_m2:.4f} mean_gap_m8={mean_gap_m8:.4f} "
              f"ratio={ratio:.2f} pass_m8={pass_m8}/{len(m8_cells)} "
              f"HP_gap={HP_DRIFT_GAP_MIN} HP_ratio={HP_RATIO_MIN} N={summary.get('N', N_FULL)}")

    if max_gap < HF_NO_DETECT:
        return ("KF4_V3_HARD_FAIL", f"NO_DETECTION: max_gap={max_gap:.4f} < {HF_NO_DETECT}. " + detail)

    if mean_gap_m8 >= HP_DRIFT_GAP_MIN and ratio >= HP_RATIO_MIN and pass_m8 >= HP_SEEDS_MIN:
        return ("KF4_V3_HARD_PASS",
                f"DRIFT_ENRICHED_NEAR_BOUNDARY: gap_m8={mean_gap_m8:.4f} ratio={ratio:.2f}. " + detail)

    return ("KF4_V3_MIDDLE_BAND", f"PARTIAL_DETECTION: ratio={ratio:.2f}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    # Verdict gates
    fake_hp = [{"M_frac": 2.0, "drift_gap": 0.15, "passes_hp": False},
               {"M_frac": 8.0, "drift_gap": 0.30, "passes_hp": True},
               {"M_frac": 8.0, "drift_gap": 0.28, "passes_hp": True}]
    v, _ = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "HARD_PASS" in v or "MIDDLE" in v, f"HP/MIDDLE gate: {v}"
    fake_hf = [{"M_frac": 2.0, "drift_gap": 0.01, "passes_hp": False},
               {"M_frac": 8.0, "drift_gap": 0.02, "passes_hp": False}]
    vf, _ = compute_verdict({"cells": fake_hf, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf}"
    # Smoke cell
    device = torch.device("cpu")
    cell = run_one_cell(N_SMOKE, 2.0, 17, device)
    assert "drift_gap" in cell, f"drift_gap missing"
    assert not math.isnan(cell["drift_gap"]), "drift_gap NaN"
    # 4x scale
    cell4 = run_one_cell(N_SMOKE * 4, 2.0, 17, device)
    assert "drift_gap" in cell4, f"4x drift_gap missing"
    print(f"[selftest] kf4_drift_detect_v3_n4096 PASS gap_smoke={cell['drift_gap']:.4f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    device = torch.device("cpu")
    smoke = args.smoke

    N_cfg = N_SMOKE if smoke else N_FULL
    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] kf4_drift_detect_v3_n4096 smoke={smoke} N={N_cfg} M_fracs={m_fracs} seeds={seeds}", flush=True)
    t0 = time.time()

    all_cells = []
    for M_frac in m_fracs:
        print(f"\n  [M_frac={M_frac}]", flush=True)
        for seed in seeds:
            cell = run_one_cell(N_cfg, M_frac, seed, device)
            all_cells.append(cell)
        print(f"  M_frac={M_frac} elapsed={time.time()-t0:.1f}s", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "kf4_drift_detect_v3_n4096", "N": N_cfg, "smoke": smoke,
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
