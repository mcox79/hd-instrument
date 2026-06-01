"""KF-5 PHASE CLASS v1: steerable beta range across phase boundary at N=4096.

CONTEXT:
  kf5_steerable_beta_v3_n8192 (v265 region): KF-5 steerability confirmed at N=8192.
  cap_map KF-phase-class new row (v267): KF5 row still yellow (45-60%).
  This probe: does the steerability RANGE (max_beta - min_beta where retention > threshold)
  change as we cross the phase boundary (M_frac near M_c)?

  MECHANISM: The substrate's steerability (controlling retrieval via beta) is expected
  to be WIDER in the phase boundary region than deep in multi-basin.

SCIENTIFIC QUESTION:
  Is the steerable beta range larger near the phase boundary (M_frac ~ 8) vs
  deep multi-basin (M_frac ~ 2)?

PRE-REGISTERED BANDS:
  No direct prior for beta-range vs M_frac comparison.

  HARD_PASS: steerable_range at M_frac=8.0 >= 1.5x range at M_frac=2.0 at >= 2/3 seeds.
    Interpretation: steerability is richer near phase boundary -- supports product framing.
  HARD_FAIL: range at M_frac=8 <= range at M_frac=2 (steerability degrades near boundary).
  MIDDLE_BAND: 1.0x < ratio < 1.5x (some enrichment, below threshold).

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. steerable_range = max(beta where ret > 0.5) - min(beta where ret > 0.1).
  3. Range ratio = range(M=8) / range(M=2).
  4. M at M_frac=8.0, N=4096: M=32768.

OOM CHECK:
  M=32768, N=4096: W=64MB. Keys=32768*4096*4=537MB. CB=268MB. Total~870MB. OK.

TIMEOUT ESTIMATE:
  2 M_fracs x 9 beta pts x 3 seeds = 54 cells. Per cell ~0.8s.
  Smoke: 1 M_frac x 5 beta pts x 1 seed = 5 cells x 0.2s = 1s.
  Total: 54*0.8=43s. Safety: ceil(1.5*43*10)=645s. Floor 14400. timeout_s=14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: kf5_phase_v1_n4096
Queue: remote_cpu_queue (CPU)
Pre-reg: preregs/2026-05-28_kf5_phase_v1_n4096.md
Parent: kf5_steerable_beta_v3_n8192; KF-phase-class cap_map row (v267)
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
_c1_spec = importlib.util.spec_from_file_location("axis1c1_kf5p", _c1_path)
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

BETA_SWEEP_FULL  = [2.0, 4.0, 8.0, 12.0, 16.0, 24.0, 32.0, 64.0, 128.0]
BETA_SWEEP_SMOKE = [4.0, 12.0, 32.0, 64.0, 128.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

N_PROBE = 200

RET_HIGH_THRESH = 0.50   # beta where retention > 0.5 = "high retrieval"
RET_LOW_THRESH  = 0.10   # beta where retention > 0.1 = "some retrieval"

# Pre-registered thresholds
HP_RANGE_RATIO_MIN = 1.5    # range at M=8 >= 1.5x range at M=2
HF_RANGE_DEGRADED  = 1.0    # range(M=8) <= range(M=2) = degradation = HARD_FAIL
HP_SEEDS_MIN       = 2


def get_output_dir(default_name: str = "kf5_phase_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_steerable_range(W, keys, val_idx, codebook, beta_sweep, N):
    """Compute steerable beta range: betas where ret > low_thresh, capped by high_thresh."""
    rets = []
    for beta in beta_sweep:
        r = compute_retention(W, keys, val_idx, codebook, beta, N, n_probe=N_PROBE)
        rets.append((beta, r))

    high_betas = [b for b, r in rets if r > RET_HIGH_THRESH]
    low_betas  = [b for b, r in rets if r > RET_LOW_THRESH]

    if high_betas and low_betas:
        steerable_range = max(high_betas) - min(low_betas)
    elif low_betas:
        steerable_range = max(low_betas) - min(low_betas)
    else:
        steerable_range = 0.0

    return {
        "steerable_range": round(steerable_range, 2),
        "high_betas": high_betas,
        "low_betas": low_betas,
        "ret_by_beta": [(b, round(r, 5)) for b, r in rets],
    }


def run_one_seed(N: int, M_frac: float, beta_sweep: List[float],
                 seed: int, device: torch.device) -> Dict:
    M = int(M_frac * N)
    codebook, _ = v3.make_kerdock_4coset_codebook(N, device)
    W, keys, _vals, _key_idx, val_idx = store_facts_batched(codebook, M, seed, N, device)

    sr = measure_steerable_range(W, keys, val_idx, codebook, beta_sweep, N)
    sr["M_frac"] = M_frac
    sr["seed"] = seed
    sr["M"] = M
    print(f"    M_frac={M_frac} seed={seed} steerable_range={sr['steerable_range']:.2f}", flush=True)
    return sr


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("KF5_PHASE_INCONCLUSIVE", "No cells.")

    by_mfrac: Dict[float, List] = {}
    for c in cells:
        by_mfrac.setdefault(c["M_frac"], []).append(c)

    m2_cells = by_mfrac.get(2.0, [])
    m8_cells = by_mfrac.get(8.0, [])

    if not m2_cells or not m8_cells:
        # Smoke: only 1 M_frac
        all_ranges = [c["steerable_range"] for c in cells]
        mean_range = sum(all_ranges) / len(all_ranges) if all_ranges else 0.0
        return ("KF5_PHASE_SMOKE_ONLY",
                f"SINGLE_MFRAC_SMOKE: mean_range={mean_range:.2f}")

    mean_m2 = sum(c["steerable_range"] for c in m2_cells) / len(m2_cells)
    mean_m8 = sum(c["steerable_range"] for c in m8_cells) / len(m8_cells)
    ratio = mean_m8 / max(mean_m2, 1e-3)

    pass_seeds = sum(1 for c2, c8 in zip(
        sorted(m2_cells, key=lambda x: x["seed"]),
        sorted(m8_cells, key=lambda x: x["seed"]))
        if c8["steerable_range"] >= HP_RANGE_RATIO_MIN * c2["steerable_range"])

    detail = (f"mean_range_m2={mean_m2:.2f} mean_range_m8={mean_m8:.2f} "
              f"ratio={ratio:.2f} pass_seeds={pass_seeds} HP_ratio={HP_RANGE_RATIO_MIN} "
              f"N={summary.get('N', N_FULL)}")

    if ratio <= HF_RANGE_DEGRADED:
        return ("KF5_PHASE_HARD_FAIL",
                f"RANGE_DEGRADED: ratio={ratio:.2f} <= {HF_RANGE_DEGRADED}. " + detail)

    if ratio >= HP_RANGE_RATIO_MIN and pass_seeds >= HP_SEEDS_MIN:
        return ("KF5_PHASE_HARD_PASS",
                f"RANGE_ENRICHED_NEAR_BOUNDARY: ratio={ratio:.2f}. " + detail)

    return ("KF5_PHASE_MIDDLE_BAND", f"PARTIAL_ENRICHMENT: ratio={ratio:.2f}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    # Verdict gates (smoke only 1 M_frac case)
    fake_smoke = [{"M_frac": 2.0, "steerable_range": 20.0, "seed": 17}]
    v, _ = compute_verdict({"cells": fake_smoke, "N": N_FULL})
    assert "SMOKE_ONLY" in v, f"Smoke single-mfrac verdict: {v}"
    # Full verdict gates
    fake_hp = [{"M_frac": 2.0, "steerable_range": 10.0, "seed": 7},
               {"M_frac": 8.0, "steerable_range": 20.0, "seed": 7},
               {"M_frac": 2.0, "steerable_range": 10.0, "seed": 17},
               {"M_frac": 8.0, "steerable_range": 20.0, "seed": 17}]
    v, _ = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "HARD_PASS" in v, f"HARD_PASS gate: {v}"
    # Smoke cell
    device = torch.device("cpu")
    cell = run_one_seed(N_SMOKE, 2.0, [4.0, 16.0, 64.0], 17, device)
    assert "steerable_range" in cell, f"steerable_range missing"
    assert cell["steerable_range"] >= 0.0, "negative range"
    # 4x smoke
    cell4 = run_one_seed(N_SMOKE * 4, 2.0, [4.0, 16.0, 64.0], 17, device)
    assert "steerable_range" in cell4, f"4x missing"
    print(f"[selftest] kf5_phase_v1_n4096 PASS range_smoke={cell['steerable_range']:.2f}", flush=True)


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
    beta_sweep = BETA_SWEEP_SMOKE if smoke else BETA_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] kf5_phase_v1_n4096 smoke={smoke} N={N_cfg} M_fracs={m_fracs} seeds={seeds}", flush=True)
    t0 = time.time()

    all_cells = []
    for M_frac in m_fracs:
        print(f"\n  [M_frac={M_frac}]", flush=True)
        for seed in seeds:
            cell = run_one_seed(N_cfg, M_frac, beta_sweep, seed, device)
            all_cells.append(cell)
        print(f"  M_frac={M_frac} elapsed={time.time()-t0:.1f}s", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "kf5_phase_v1_n4096", "N": N_cfg, "smoke": smoke,
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
