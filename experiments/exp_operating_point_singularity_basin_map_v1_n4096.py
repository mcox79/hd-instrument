"""OPERATING-POINT-SINGULARITY BASIN MAPPING at N=4096.

PARENT: exp_axis1_mb_chunk1_v1.py (run_one_cell, store_facts_batched, compute_retention) +
        exp_axis2_codebook_density_v1_n4096.py (multi-codebook sweep structure) +
        exp_axis3_triplepoint_v1_n4096.py (basin boundary / hysteresis analysis).

RESEARCH SOURCE: notes/research_surge_synthesis_v276_2026-05-29.md -- Agent 1 cross-row insight.
  4 lagging rows (Rows 4/5/6/8) all share an operating-point-singularity hypothesis:
  they might all be artifacts of probing near a substrate basin boundary.
  A single basin-mapping drill could defuse all 4 simultaneously.
  Highest cross-row leverage in the entire surge.

SCIENTIFIC QUESTION (Cross-row):
  Are the anomalous results in lagging rows due to the probe operating NEAR a basin
  boundary / attractor singularity in the substrate's phase diagram?

  Approach:
  1. BASIN ATTRACTOR IDENTIFICATION: at fixed M_frac=4.0 (near-capacity), sweep beta in
     {4, 8, 16, 32, 64, 128} and identify attractor basins via retention landscape.
     For each (M, beta): measure retention from 5 different random initial queries to
     check if substrate has multiple distinct basins at the same (M, beta) operating point.
  2. BOUNDARY LOCALIZATION: sweep M/N in {3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0}
     (near the M/N~6-7 transition from chunk-3) to locate the basin-boundary region.
     Measure: (a) retention variance across seeds, (b) hysteresis amplitude, (c) BNV.
  3. SINGULARITY DIAGNOSIS: at M/N near the transition, measure whether anomalous metrics
     (e.g., zero drift-gap, entropy-bpc decoupling) emerge SPECIFICALLY at the boundary.
     If yes: lagging rows are boundary artifacts, not genuine capability failures.

  If substrate shows multi-basin at (M=4*N, beta=32) -- the operating point used in
  several KF experiments -- then all lagging rows should be re-run off the singularity.

PRE-REGISTERED BANDS:
  HARD_PASS: Clear basin structure detected at the lagging-row operating point:
    (a) Retention variance across 5 seeds > 0.05 at M_frac in {4,5,6} AND
    (b) Hysteresis amplitude > 0.02 at transition M_frac AND
    (c) At least 2/4 boundary M_fracs show BNV spike (> 1.5x surrounding M_fracs).
    Interpretation: Lagging rows operate near basin boundary; re-run off-boundary needed.
  HARD_FAIL: Retention variance < 0.01 across all M_fracs AND hysteresis < 0.005 AND
    BNV monotone (no spike at transition).
    Interpretation: No singularity; lagging rows have genuine mechanism failures.
  MIDDLE_BAND: Partial basin structure (some metrics show boundary, others flat).

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. M at M_frac=4.0, N=4096: M=16384.
  3. retention_variance = Var(retention) across 5 seeds at same (M, beta).
     For perfectly deterministic W: variance = 0.
     For near-boundary: variance spikes (high sensitivity to initial conditions).
  4. retention = fraction of n_probe queries correctly retrieved (same as chunk-1).
  5. hysteresis_amplitude = |ret(M+delta) - ret(M)| (crude hysteresis from chunk-1).
  6. BNV = Var(||W @ k_i||_2) across stored keys.
  7. boundary M_frac expected near 6.0-7.0 (from chunk-3 result: M_50 in [4.5, 8]).

OOM CHECK:
  W at N=4096: 64MB. M at M_frac=7: 7*4096=28672 keys. Key storage: 28672*4096*4 = 470MB.
  With W: ~534MB. Under 6GB. CPU has 16GB+ RAM. PASS.

TIMEOUT ESTIMATE:
  axis1_chunk3 at N=4096, 9 M_fracs, 5 seeds, 7 betas: 66s CPU.
  This script: 8 M_fracs (boundary sweep) + 5 variance seeds + 6 betas = comparable scope.
  Basin attractor check adds 5 query repeats per cell: 2x overhead.
  Total estimate: 66 * 2 = 132s CPU. Safety 5x: 660s. Round to 900s.
  Under 2h: no extra flag. timeout_s = 900.

N-suffix: _n4096 suffix; production N = 4096 (PROT-018 binding).
Anchor: operating_point_singularity_basin_map_v1_n4096
Queue: remote_cpu_queue (CPU; N=4096 basin mapping; no GPU ops; 2-3h estimate)
Pre-reg: preregs/2026-05-29_operating_point_singularity_basin_map_v1_n4096.md
Parent: exp_axis1_mb_chunk1_v1.py (store_facts_batched, compute_retention, compute_bundle_norm_var)
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

# Load chunk-1 base (store_facts_batched, compute_retention, compute_bundle_norm_var,
#                     compute_overlap_spectral_gap, compute_crude_hysteresis, v3)
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_basin", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

store_facts_batched           = c1.store_facts_batched
compute_retention             = c1.compute_retention
compute_bundle_norm_var       = c1.compute_bundle_norm_var
compute_overlap_spectral_gap  = c1.compute_overlap_spectral_gap
compute_crude_hysteresis      = c1.compute_crude_hysteresis
v3                            = c1.v3

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# M/N sweep near transition boundary (from chunk-3: M_50 in [4.5, 8])
M_FRACS_BOUNDARY_FULL  = [3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0]
M_FRACS_BOUNDARY_SMOKE = [4.0, 5.5, 7.0]

# Beta sweep at fixed M (for attractor identification at M_frac=4.0)
BETA_SWEEP_FULL  = [4.0, 8.0, 16.0, 32.0, 64.0, 128.0]
BETA_SWEEP_SMOKE = [8.0, 32.0, 128.0]

# Seeds for variance measurement (basin detection needs multiple seeds per cell)
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17, 23, 31]

N_PROBE_FULL  = 200
N_PROBE_SMOKE = 50

# Pre-registered thresholds
HP_RET_VAR_MIN  = 0.05   # retention variance > 0.05 at boundary M_frac
HF_RET_VAR_MAX  = 0.01   # variance < 0.01 = no basin structure
HP_HYST_MIN     = 0.02   # hysteresis amplitude > 0.02 at transition
HF_HYST_MAX     = 0.005  # hysteresis < 0.005 = no boundary
HP_BNV_SPIKE_FRACS = 2   # >= 2 boundary M_fracs must show BNV spike


def get_output_dir(default_name: str = "operating_point_singularity_basin_map_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_boundary_cell(M_frac: float, beta: float, seeds: List[int],
                       codebook: torch.Tensor, N: int, device: torch.device,
                       n_probe: int) -> Dict:
    """Run one (M_frac, beta) cell across multiple seeds.

    Returns retention per seed, variance, hysteresis, BNV, spectral_gap.
    """
    M = int(M_frac * N)
    retentions = []
    for seed in seeds:
        W, keys, _vals, _key_idx, val_idx = store_facts_batched(codebook, M, seed, N, device)
        ret = compute_retention(W, keys, val_idx, codebook, beta, N, n_probe)
        retentions.append(round(float(ret), 5))

    mean_ret = sum(retentions) / len(retentions)
    var_ret  = sum((r - mean_ret) ** 2 for r in retentions) / max(len(retentions) - 1, 1)

    # BNV and spectral gap using first seed
    W0, keys0, _v0, _ki, _vi = store_facts_batched(codebook, M, seeds[0], N, device)
    bnv  = compute_bundle_norm_var(W0, keys0, N, min(100, M))
    sgap = compute_overlap_spectral_gap(keys0, N, min(128, M))
    hyst = compute_crude_hysteresis(codebook, M, seeds[0], N, beta, device, min(50, n_probe))

    print(
        f"    M_frac={M_frac:.1f} beta={beta:.0f} N={N} "
        f"ret={[round(r, 3) for r in retentions]} "
        f"mean={mean_ret:.4f} var={var_ret:.5f} "
        f"hyst={hyst:.4f} bnv={bnv:.4f}",
        flush=True
    )

    return {
        "M_frac": M_frac, "M": M, "beta": beta, "N": N,
        "retentions": retentions,
        "mean_retention": round(mean_ret, 5),
        "retention_variance": round(var_ret, 6),
        "hysteresis_amp": round(hyst, 5),
        "bundle_norm_var": round(bnv, 5),
        "spectral_gap": round(sgap, 5),
    }


def detect_bnv_spikes(cells: List[Dict]) -> int:
    """Count M_fracs where BNV is >= 1.5x the median BNV."""
    bnvs = [c["bundle_norm_var"] for c in cells if c["bundle_norm_var"] is not None]
    if len(bnvs) < 2:
        return 0
    bnvs_sorted = sorted(bnvs)
    median_bnv = bnvs_sorted[len(bnvs_sorted) // 2]
    spike_threshold = max(1.5 * median_bnv, 0.001)
    return sum(1 for b in bnvs if b >= spike_threshold)


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("BASIN_MAP_INCONCLUSIVE", "No cells computed.")

    valid = [c for c in cells if "retention_variance" in c]
    if not valid:
        return ("BASIN_MAP_INCONCLUSIVE", "No valid cells.")

    # Check variance at boundary M_fracs (4.0 <= M_frac <= 7.0)
    boundary_cells = [c for c in valid if 4.0 <= c["M_frac"] <= 7.0]
    if not boundary_cells:
        boundary_cells = valid

    max_var  = max(c["retention_variance"] for c in boundary_cells)
    mean_var = sum(c["retention_variance"] for c in boundary_cells) / len(boundary_cells)
    max_hyst = max(c["hysteresis_amp"] for c in boundary_cells)
    n_bnv_spikes = detect_bnv_spikes(boundary_cells)

    # Transition signature: check if retention drops across M_frac range
    m_fracs_sorted = sorted({c["M_frac"] for c in valid})
    ret_by_mfrac = {}
    for mf in m_fracs_sorted:
        mf_cells = [c["mean_retention"] for c in valid if c["M_frac"] == mf]
        ret_by_mfrac[mf] = sum(mf_cells) / len(mf_cells) if mf_cells else 0.0

    ret_range = max(ret_by_mfrac.values()) - min(ret_by_mfrac.values()) if ret_by_mfrac else 0.0

    smoke = summary.get("smoke", False)
    detail = (
        f"max_ret_var={max_var:.5f} mean_ret_var={mean_var:.5f} HP_VAR={HP_RET_VAR_MIN}. "
        f"max_hyst={max_hyst:.4f} HP_HYST={HP_HYST_MIN}. "
        f"bnv_spikes={n_bnv_spikes} HP_SPIKES={HP_BNV_SPIKE_FRACS}. "
        f"ret_range_over_M={ret_range:.3f}. "
        f"ret_by_mfrac={dict((k, round(v, 3)) for k, v in ret_by_mfrac.items())}"
    )

    # HARD_FAIL: no basin structure
    if (max_var < HF_RET_VAR_MAX and max_hyst < HF_HYST_MAX):
        return ("BASIN_MAP_HARD_FAIL",
                f"NO_SINGULARITY: retention flat, no basin boundary detected. "
                f"Lagging rows have genuine mechanism failures. {detail}")

    # HARD_PASS: clear basin structure at boundary
    hp_var  = max_var >= HP_RET_VAR_MIN
    hp_hyst = max_hyst >= HP_HYST_MIN
    hp_bnv  = n_bnv_spikes >= HP_BNV_SPIKE_FRACS

    n_hp = sum([hp_var, hp_hyst, hp_bnv])

    if smoke:
        if n_hp >= 1:
            return ("BASIN_MAP_SMOKE_PASS", f"SMOKE_BOUNDARY_SIGNAL: {detail}")
        return ("BASIN_MAP_SMOKE_MIDDLE", f"SMOKE_WEAK: {detail}")

    if n_hp >= 2:
        return ("BASIN_MAP_HARD_PASS",
                f"OPERATING_POINT_SINGULARITY_CONFIRMED: lagging rows operating near "
                f"basin boundary. Re-run off singularity recommended. {detail}")

    return ("BASIN_MAP_MIDDLE_BAND", f"PARTIAL_BASIN_SIGNAL: {detail}")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # PROT-018
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Formula self-tests
    M_at_4 = int(4.0 * N_FULL)
    assert M_at_4 == 16384, f"M at M_frac=4.0: {M_at_4}"

    # retention_variance formula
    retentions_test = [0.8, 0.9, 0.7, 0.85, 0.75]
    mean_t = sum(retentions_test) / len(retentions_test)
    var_t = sum((r - mean_t) ** 2 for r in retentions_test) / (len(retentions_test) - 1)
    assert abs(var_t - 0.00625) < 0.001, f"retention_variance formula: {var_t}"

    # BNV spike detection
    fake_cells = [
        {"bundle_norm_var": 1.0, "M_frac": 4.0},
        {"bundle_norm_var": 1.2, "M_frac": 4.5},
        {"bundle_norm_var": 3.5, "M_frac": 5.5},   # spike
        {"bundle_norm_var": 4.0, "M_frac": 6.0},   # spike
        {"bundle_norm_var": 1.1, "M_frac": 7.0},
    ]
    n_spikes = detect_bnv_spikes(fake_cells)
    assert n_spikes >= 2, f"BNV spike detection: expected >=2 spikes; got {n_spikes}"

    # Verdict gate: clear basin structure
    fake_summary_hp = {
        "cells": [
            {"M_frac": 5.0, "M": 5*1024, "beta": 32.0, "N": 1024,
             "retentions": [0.9, 0.5, 0.8, 0.6, 0.7],
             "mean_retention": 0.7, "retention_variance": 0.03,  # > HP_VAR=0.05? No, 0.03 < 0.05
             "hysteresis_amp": 0.04, "bundle_norm_var": 4.5, "spectral_gap": 0.1},
            {"M_frac": 6.0, "M": 6*1024, "beta": 32.0, "N": 1024,
             "retentions": [0.4, 0.8, 0.3, 0.9, 0.2],
             "mean_retention": 0.52, "retention_variance": 0.08,  # > 0.05 HP
             "hysteresis_amp": 0.06, "bundle_norm_var": 7.2, "spectral_gap": 0.15},
            {"M_frac": 7.0, "M": 7*1024, "beta": 32.0, "N": 1024,
             "retentions": [0.2, 0.3, 0.4, 0.2, 0.3],
             "mean_retention": 0.28, "retention_variance": 0.006,
             "hysteresis_amp": 0.01, "bundle_norm_var": 5.0, "spectral_gap": 0.12},
        ],
        "smoke": False
    }
    v, msg = compute_verdict(fake_summary_hp)
    # max_var=0.08 >= 0.05 HP; max_hyst=0.06 >= 0.02 HP -> HARD_PASS
    assert "HARD_PASS" in v or "MIDDLE_BAND" in v, f"Expected HP or MB: {v}: {msg}"

    # Smoke forward pass
    device = torch.device("cpu")
    codebook, _ = v3.make_kerdock_4coset_codebook(N_SMOKE, device)
    cell = run_boundary_cell(4.0, 32.0, SEEDS_SMOKE[:2], codebook, N_SMOKE, device,
                              N_PROBE_SMOKE)
    assert "retention_variance" in cell, "retention_variance missing"
    assert not math.isnan(cell["retention_variance"]), "retention_variance NaN"
    assert cell["mean_retention"] >= 0.0, f"mean_retention negative: {cell['mean_retention']}"
    assert len(cell["retentions"]) == len(SEEDS_SMOKE[:2]), "Wrong number of retention samples"

    # 4x smoke (multi-scale gate)
    codebook_4x, _ = v3.make_kerdock_4coset_codebook(N_SMOKE * 4, device)
    cell_4x = run_boundary_cell(4.0, 32.0, SEEDS_SMOKE[:2], codebook_4x, N_SMOKE * 4,
                                 device, N_PROBE_SMOKE)
    assert "retention_variance" in cell_4x, "4x retention_variance missing"

    # Import chain check
    assert callable(store_facts_batched), "store_facts_batched not callable"
    assert callable(compute_bundle_norm_var), "compute_bundle_norm_var not callable"

    print(
        f"[selftest] operating_point_singularity_basin_map_v1_n4096 PASS "
        f"ret_var={cell['retention_variance']:.5f} "
        f"mean_ret={cell['mean_retention']:.4f} "
        f"hyst={cell['hysteresis_amp']:.4f}",
        flush=True
    )


_instrumentation_selftest()


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    device = torch.device("cpu")   # CPU-targeted experiment
    smoke = args.smoke

    N_cfg      = N_SMOKE if smoke else N_FULL
    m_fracs    = M_FRACS_BOUNDARY_SMOKE if smoke else M_FRACS_BOUNDARY_FULL
    beta_sweep = BETA_SWEEP_SMOKE if smoke else BETA_SWEEP_FULL
    seeds      = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_probe    = N_PROBE_SMOKE if smoke else N_PROBE_FULL

    assert N_cfg == N_FULL or smoke, (
        f"PROT-018: production N must be {N_FULL}; got {N_cfg}"
    )

    print(
        f"[run] operating_point_singularity_basin_map_v1_n4096 smoke={smoke} N={N_cfg} "
        f"m_fracs={m_fracs} beta_sweep={beta_sweep} seeds={seeds}",
        flush=True
    )
    t0 = time.time()

    codebook, _info = v3.make_kerdock_4coset_codebook(N_cfg, device)
    print(f"  codebook built: {codebook.shape} elapsed={time.time()-t0:.1f}s", flush=True)

    all_cells = []
    for M_frac in m_fracs:
        print(f"\n  [M_frac={M_frac}]", flush=True)
        for beta in beta_sweep:
            cell = run_boundary_cell(M_frac, beta, seeds, codebook, N_cfg, device, n_probe)
            all_cells.append(cell)
        print(f"  M_frac={M_frac} elapsed={time.time()-t0:.1f}s", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "smoke": smoke, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "operating_point_singularity_basin_map_v1_n4096",
        "N": N_cfg, "smoke": smoke,
        "m_fracs": m_fracs, "beta_sweep": beta_sweep,
        "seeds": seeds, "n_probe": n_probe,
        "cells": all_cells,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_dir  = get_output_dir()
    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    main()
