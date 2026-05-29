"""PHASE REGION C/D PROBE v1: beta > beta_c unexplored regime at N=4096.

CONTEXT:
  t1_beta_sweep_v1_n4096 (v267 HARD_PASS): beta_c located at M_frac=8.0, N=4096.
  beta_c ~ 10-16 (from v267 transition zone). All prior experiments: beta <= 32 or
  in structured sweeps. Region beta=64 (above beta_c) is UNPROBED.

  Phase diagram regions (for Hopfield-like substrate at N=4096 Kerdock):
    Region A: M < M_c, beta < beta_c -- paramagnetic (low retention, no transition)
    Region B: M < M_c, beta > beta_c -- ferromagnetic (high retention, pattern stabilized)
    Region C: M > M_c, beta < beta_c -- spin-glass (interference dominant, low beta)
    Region D: M > M_c, beta > beta_c -- retrieval possible despite overcapacity?

  M_c from axis1 chunks: transition around M_frac~8-12 at beta=32.
  Region C probe: M_frac=4 (BELOW M_c), beta=64 (ABOVE beta_c~10-16)
    -> Expected: HIGH retention (deep ferromagnetic; beta competes successfully with load)
  Region D probe: M_frac=12 (ABOVE M_c), beta=64
    -> Unknown: can high beta rescue retrieval above M_c?
       Theory: at M > M_c, even high beta cannot recover (too much interference).
       Observation pending.

SCIENTIFIC QUESTION:
  At beta=64 (safely above beta_c~10-16):
  1. [Region C, M_frac=4]: does retention approach 1.0? (confirms ferromagnetic stabilization)
  2. [Region D, M_frac=12]: is retention still low (<0.3) despite high beta? (confirms M_c boundary)
  The contrast between C and D maps the M_c boundary at fixed high beta.

PRE-REGISTERED BANDS (calibration probe; first beta=64 unprobed measurement):
  Per calibration-probe policy: bands set +/-50% around theoretical prediction.

  Region C (M_frac=4, beta=64):
    Theory: retention near 1.0 (deep ferromagnet at high beta). Predict retention_C > 0.70.
    HARD_PASS_C: mean_retention_C >= 0.70 at >= 3/5 seeds (ferromagnetic confirmed).
    HARD_FAIL_C: mean_retention_C < 0.35 (below 50% of prediction; ferromagnetic absent).

  Region D (M_frac=12, beta=64):
    Theory: retention near random (M_c exceeded; interference prevents retrieval). Predict < 0.20.
    HARD_PASS_D: mean_retention_D < 0.30 at >= 3/5 seeds (overcapacity boundary holds).
    HARD_FAIL_D: mean_retention_D >= 0.60 (retrieval survives high M -- unexpected).

  Joint HARD_PASS: both C and D meet their individual criteria (phase boundary confirmed).
  Joint HARD_FAIL: either baseline broken in unexpected direction.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. M at M_frac=4, N=4096: M=16384.
  3. M at M_frac=12, N=4096: M=49152. C=49152 (Kerdock 4-coset at N=4096). M=C at limit.
  4. beta_c ~ 10-16 from v267. beta=64 > beta_c by factor 4-6x.
  5. OOM at M_frac=12, N=4096: keys=49152*4096*4=806MB. W=64MB. CB=268MB. Total~1.1GB. OK.
  6. softmax_confidence at beta=64 for retention_C probe.

OOM CHECK:
  M_frac=12 N=4096: M=49152, keys=49152*4096*4=805MB. W=4096^2*4=64MB. CB=268MB. Total~1.1GB.
  Under 6GB. OK.

TIMEOUT ESTIMATE:
  t1v1 per cell ~0.5s at N=4096 GPU.
  2 regions x 1 beta x 5 seeds = 10 cells x 0.5s = 5s.
  Safety: ceil(1.5 * 5 * 10) = 75s. PROT-019 _n4096 floor = 14400. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: phase_region_cd_v1_n4096
Queue: overnight_queue (GPU; N=4096 Kerdock; 2 phase regions x 5 seeds)
Pre-reg: preregs/2026-05-29_phase_region_cd_v1_n4096.md
Parent: t1_beta_sweep_v1_n4096 (v267 HARD_PASS; beta_c located; region C/D next)
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

# Load t1_beta_sweep_v1 -- use lazy loader to avoid its selftest running at import
def _load_t1v1():
    _t1_path = REPO / "experiments" / "exp_t1_beta_sweep_v1_n4096.py"
    _t1_spec = importlib.util.spec_from_file_location("t1v1_cdprobe", _t1_path)
    t1v1 = importlib.util.module_from_spec(_t1_spec)
    _t1_spec.loader.exec_module(t1v1)
    return t1v1


_t1v1 = _load_t1v1()

store_facts_batched  = _t1v1.store_facts_batched
v3                   = _t1v1.v3
softmax_confidence   = _t1v1.softmax_confidence

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Phase region definitions
REGION_C_MFRAC = 4.0    # M < M_c (below capacity boundary)
REGION_D_MFRAC = 12.0   # M > M_c (above capacity boundary)
BETA_HIGH      = 64.0   # well above beta_c ~ 10-16

REGIONS = [
    ("region_C", REGION_C_MFRAC, BETA_HIGH),
    ("region_D", REGION_D_MFRAC, BETA_HIGH),
]

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

N_PROBE = 200

# Pre-registered thresholds
# Region C: high beta + undercapacity -> retention expected near 1.0
HP_RETENTION_C_MIN  = 0.70   # mean retention >= 0.70 at >= 3/5 seeds
HF_RETENTION_C_MAX  = 0.35   # mean retention < 0.35 = ferromagnet absent
HP_SEEDS_C_MIN      = 3

# Region D: high beta + overcapacity -> retention expected near 0 or low
HP_RETENTION_D_MAX  = 0.30   # mean retention < 0.30 at >= 3/5 seeds
HF_RETENTION_D_MIN  = 0.60   # mean retention >= 0.60 = unexpected retrieval at overcapacity
HP_SEEDS_D_MIN      = 3


def get_output_dir(default_name: str = "phase_region_cd_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell(region: str, M_frac: float, beta: float,
                 seed: int, N_use: int, device: torch.device) -> Dict:
    """Measure softmax confidence at (M_frac, beta) for one seed.

    NOTE: store_facts_batched handles M > C by repeating codebook permutations,
    so M > C is genuine overcapacity (W accumulates repeated interference).
    Do NOT cap M at C; the overcapacity regime is the key scientific probe.
    """
    M = int(M_frac * N_use)
    codebook, _ = v3.make_kerdock_4coset_codebook(N_use, device)
    # Do NOT cap M at C -- overcapacity is the probe for Region D
    W, keys, _vals, _key_idx, val_idx = store_facts_batched(codebook, M, seed, N_use, device)
    retention = softmax_confidence(W, keys, val_idx, codebook, beta, N_use, n_probe=N_PROBE)
    theory_bound_ret = min(1.0, math.exp(-M / N_use))   # rough ferromagnet estimate

    return {
        "region": region, "M_frac": M_frac, "M": M, "N": N_use,
        "beta": beta, "seed": seed,
        "retention": round(float(retention), 5),
        "theory_bound_ret": round(theory_bound_ret, 5),
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("PHASE_CD_INCONCLUSIVE", "No cells.")

    N = summary.get("N", N_FULL)

    c_cells = [c for c in cells if c.get("region") == "region_C"
               and c.get("retention") is not None]
    d_cells = [c for c in cells if c.get("region") == "region_D"
               and c.get("retention") is not None]

    if not c_cells or not d_cells:
        return ("PHASE_CD_INCONCLUSIVE",
                f"Missing region data: C={len(c_cells)} D={len(d_cells)}")

    mean_C = sum(c["retention"] for c in c_cells) / len(c_cells)
    mean_D = sum(c["retention"] for c in d_cells) / len(d_cells)

    # Per-seed pass counts
    c_pass = sum(1 for c in c_cells if c["retention"] >= HP_RETENTION_C_MIN)
    d_pass = sum(1 for c in d_cells if c["retention"] < HP_RETENTION_D_MAX)

    detail = (f"region_C_mean={mean_C:.4f} region_D_mean={mean_D:.4f} "
              f"c_pass={c_pass}/{len(c_cells)} d_pass={d_pass}/{len(d_cells)} "
              f"beta={BETA_HIGH} M_frac_C={REGION_C_MFRAC} M_frac_D={REGION_D_MFRAC} "
              f"N={N}")

    # HARD_FAIL checks
    if mean_C < HF_RETENTION_C_MAX:
        return ("PHASE_CD_HARD_FAIL",
                f"REGION_C_ABSENT: mean_C={mean_C:.4f} < {HF_RETENTION_C_MAX} "
                f"(ferromagnet not found at high beta undercapacity). " + detail)
    if mean_D >= HF_RETENTION_D_MIN:
        return ("PHASE_CD_HARD_FAIL",
                f"REGION_D_UNEXPECTED: mean_D={mean_D:.4f} >= {HF_RETENTION_D_MIN} "
                f"(high retention persists above M_c -- phase boundary absent). " + detail)

    # HARD_PASS: both regions meet criteria
    if c_pass >= HP_SEEDS_C_MIN and d_pass >= HP_SEEDS_D_MIN:
        return ("PHASE_CD_HARD_PASS",
                f"PHASE_BOUNDARY_CONFIRMED: Region C high-retention, Region D low-retention "
                f"at beta={BETA_HIGH}. " + detail)

    return ("PHASE_CD_MIDDLE_BAND",
            f"PARTIAL: not enough seeds meet criteria. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Formula self-tests
    assert int(REGION_C_MFRAC * N_FULL) == 16384, "Region C M check"
    m_d = int(REGION_D_MFRAC * N_FULL)
    assert m_d == 49152, f"Region D M check: {m_d}"

    # OOM check: store_facts_batched stores M items each of size N; W is N^2
    # Memory: W=N^2*4 bytes + keys=M*N*4 bytes
    w_bytes = N_FULL * N_FULL * 4
    k_bytes = m_d * N_FULL * 4
    total_bytes = w_bytes + k_bytes
    assert total_bytes < 6e9, f"OOM: {total_bytes/1e6:.0f}MB >= 6GB"

    # Smoke cell (at N_SMOKE to keep it fast)
    device = torch.device("cpu")
    # NOTE: at N_SMOKE=1024, M_frac=4 -> M=4096; M_frac=12 -> M=12288.
    # store_facts_batched handles M > C with repeated permutations.
    # At smoke scale both regions may show retention=1.0 (small N/high beta).
    # This is the expected N-scale artifact: at small N, interference is low.
    # Full N=4096 will show the genuine phase separation.
    cell_c = run_one_cell("region_C", REGION_C_MFRAC, BETA_HIGH, 17, N_SMOKE, device)
    assert "retention" in cell_c and not math.isnan(cell_c["retention"]), (
        f"retention missing or NaN: {cell_c}")
    assert 0.0 <= cell_c["retention"] <= 1.0, f"retention out of range: {cell_c['retention']}"

    cell_d = run_one_cell("region_D", REGION_D_MFRAC, BETA_HIGH, 17, N_SMOKE, device)
    assert "retention" in cell_d and not math.isnan(cell_d["retention"]), (
        f"region_D retention missing or NaN: {cell_d}")
    assert 0.0 <= cell_d["retention"] <= 1.0, f"region_D retention out of range"

    # 4x scale smoke (both regions)
    cell_c4x = run_one_cell("region_C", REGION_C_MFRAC, BETA_HIGH, 17, N_SMOKE * 4, device)
    cell_d4x = run_one_cell("region_D", REGION_D_MFRAC, BETA_HIGH, 17, N_SMOKE * 4, device)
    assert "retention" in cell_c4x and "retention" in cell_d4x

    # Verdict self-tests
    fake_hp = (
        [{"region": "region_C", "retention": 0.90}] * 5 +
        [{"region": "region_D", "retention": 0.10}] * 5
    )
    v, msg = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "HARD_PASS" in v, f"HARD_PASS gate: {v} {msg}"

    fake_hf_c = [{"region": "region_C", "retention": 0.20}] * 5
    vf, mf = compute_verdict({"cells": fake_hf_c + [{"region": "region_D", "retention": 0.10}] * 5,
                               "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate (C absent): {vf}"

    print(f"[selftest] phase_region_cd_v1_n4096 PASS "
          f"ret_C_smoke={cell_c['retention']:.5f} ret_D_smoke={cell_d['retention']:.5f} "
          f"ret_C_4x={cell_c4x['retention']:.5f} ret_D_4x={cell_d4x['retention']:.5f}",
          flush=True)


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
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] phase_region_cd_v1_n4096 smoke={smoke} N={N_cfg} "
          f"regions={[r[0] for r in REGIONS]} beta={BETA_HIGH} seeds={seeds} "
          f"device={device_str}", flush=True)
    t0 = time.time()

    all_cells = []
    for region, M_frac, beta in REGIONS:
        print(f"\n  [{region} M_frac={M_frac} beta={beta}]", flush=True)
        for seed in seeds:
            cell = run_one_cell(region, M_frac, beta, seed, N_cfg, device)
            all_cells.append(cell)
            print(f"  {region} seed={seed} retention={cell['retention']:.5f} "
                  f"({time.time()-t0:.1f}s)", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "phase_region_cd_v1_n4096", "N": N_cfg, "smoke": smoke,
        "regions": REGIONS, "beta_high": BETA_HIGH, "seeds": seeds,
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
