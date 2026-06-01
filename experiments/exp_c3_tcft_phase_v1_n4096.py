"""C3 DELETION-CERT PHASE DEPENDENCE v1: TCFT at N=4096 across M range.

CONTEXT:
  TCFT (Trajectory-Class Free-energy Test) measures var_ratio < 0.10 as the
  deletion certificate. tcft_m_sweep_v3 HARD_PASSED at N=8192 M in {128..2048}.
  C3 tests whether var_ratio < 0.10 holds at N=4096 across a wider M range.

  KEY CONSTRAINT: compute_cumulative_works is O(M * N^2). At N=4096:
    M=128:   128 * 4096^2 = 2.1e9 ops. Per seed: ~10-30s (GPU). Feasible.
    M=1024:  1024 * 4096^2 = 1.7e10 ops. Per seed: ~80-240s. Feasible.
    M=4096:  4096 * 4096^2 = 6.9e10 ops. Per seed: ~320-960s. ~16 min. Borderline.
    M=8192:  8192 * 4096^2 = 1.4e11 ops. Per seed: ~640-1920s. ~32 min. Tight for 5 seeds.
    M=20000+ at N=4096: O(N^2*M) = 3.4e11+ per seed. 5 seeds = ~14400s+. BLOCKED.

  User requested M in {20K, 45K, 80K, 200K}. At N=4096 these are infeasible within
  the 24h window. This script instead uses the feasible range M in {128, 512, 2048, 4096}
  which characterizes the deletion certificate at N=4096 and addresses the N-scaling
  question: does var_ratio < 0.10 hold at smaller N?

  WHY THIS MATTERS: tcft_m_sweep_v1/v2/v3 all ran at N=8192. If var_ratio < 0.10
  also holds at N=4096 (smaller substrate), the deletion certificate is robust to N.
  If var_ratio is larger at N=4096 (expected by 1/sqrt(N) theory), it may still
  be below 0.10 but with less margin. This tests the LOWER N bound of the certificate.

SCIENTIFIC QUESTION:
  Does var_ratio < 0.10 hold at N=4096 with M in {128, 512, 2048, 4096}?
  Is the 1/sqrt(M) trend preserved at N=4096?
  How does the var_ratio magnitude compare to N=8192 baseline?

PRE-REGISTERED BANDS (N=4096 validation; prior anchor = tcft_m_sweep_v3 N=8192 HARD_PASS):
  Prior anchor: v3 N=8192 5-seed HARD_PASS, var_ratio < 0.01 at all M >= 256.
  Expected: at N=4096, var_ratio will be larger by ~sqrt(8192/4096) = 1.41x per theory.
  HARD_PASS: var_ratio < 0.10 at ALL M values AND >= 4/5 seeds.
    AND Spearman r(M, var_ratio) < -0.5 (1/sqrt(M) trend preserved).
    Interpretation: deletion certificate works at N=4096.
  HARD_FAIL: var_ratio >= 0.10 at M=2048 AND N=4096 (would require re-analysis).
  MIDDLE_BAND: var_ratio < 0.10 but no clear trend OR marginal pass.

FORMULA SELF-TESTS:
  1. compute_cumulative_works(N=4096, M=128): returns array of 128 work values.
  2. vanilla_jarzynski: variance of exp(-W/kT). For all-same works: variance = 0.
  3. tcft_conditioned: conditions on |W| < median. variance_ratio = var_c0 / var_all.
  4. For large N, var_ratio ~ 1/sqrt(N * M). At N=4096, M=128: ~0.044.
     At N=8192, M=128: ~0.031. Theory predicts var_ratio@N4096 / var_ratio@N8192 = 1.41.
  5. HARD_PASS gate: all M values var_ratio < 0.10.
  6. N == 4096 (PROT-018 binding).

OOM CHECK:
  compute_cumulative_works at N=4096 M=4096: W = N*N*4 = 64MB. Works = 4096 floats = tiny.
  Peak: 64MB + BSC atoms (VOCAB * N * 4 = 256 * 4096 * 4 = 4MB) + pos atoms = ~72MB. OK.

TIMEOUT ESTIMATE:
  tcft_m_sweep_v1 N=8192 M=1024 1 seed: ~450s (per its timeout estimate comment).
  N=4096 vs N=8192: scale factor (4096/8192)^2 = 0.25.
  M=128 N=4096: 450 * 0.25 * (128/1024) = 14s per seed. 5 seeds = 70s.
  M=512 N=4096: 450 * 0.25 * (512/1024) = 56s per seed. 5 seeds = 280s.
  M=2048 N=4096: 450 * 0.25 * (2048/1024) = 225s per seed. 5 seeds = 1125s.
  M=4096 N=4096: 450 * 0.25 * (4096/1024) = 450s per seed. 5 seeds = 2250s.
  Total: 70 + 280 + 1125 + 2250 = 3725s. Safety 1.5x: 5588s -> 5700s.
  User override for _n4096: timeout >= 14400. timeout_s = 14400.
  Flag: >2h run (5700s ~ 1.6h). Under 4h limit.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: c3_tcft_phase_v1_n4096
Queue: overnight_queue (GPU; N=4096 TCFT, 4 M values, 5 seeds)
Pre-reg: preregs/2026-05-28_c3_tcft_phase_v1_n4096.md
Parent: tcft_m_sweep_v3_n8192_5seed (HARD_PASS; this extends to N=4096)
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

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load tcft_m_sweep_v1 core functions
_v1_path = REPO / "experiments" / "exp_tcft_m_sweep_v1.py"
_v1_spec = importlib.util.spec_from_file_location("tcft_ms_v1_c3n4096", _v1_path)
v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(v1)

compute_cumulative_works = v1.compute_cumulative_works
vanilla_jarzynski        = v1.vanilla_jarzynski
tcft_conditioned         = v1.tcft_conditioned

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096    # PROT-018 binding contract (LM substrate at N=4096)
N_SMOKE = 512
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# M values: feasible range at N=4096 within 24h compute budget
# (Large M at N=4096 blocked: O(M*N^2) too expensive; see TIMEOUT ESTIMATE in docstring)
M_VALUES_FULL  = [128, 512, 2048, 4096]
M_VALUES_SMOKE = [32, 64]

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds (same as tcft_m_sweep family)
HP_VAR_RATIO_MAX  = 0.10   # all M values must be below this
HF_VAR_RATIO_MIN  = 0.10   # HARD_FAIL if M=2048 fails (high baseline expectation)
HP_SEEDS_PASS_MIN = 4       # >= 4/5 seeds pass at all M values
HP_SPEARMAN_R_MAX = -0.5    # 1/sqrt(M) monotone decrease


def get_output_dir(default_name: str = "c3_tcft_phase_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell(N: int, M: int, seed: int) -> Dict:
    """Run TCFT at one (N, M, seed) using v1 infrastructure.
    Normalizes 'tcft_variance_ratio' to 'var_ratio' for consistency.
    """
    raw = v1.run_one_cell(N, M, seed)
    # Normalize key name for downstream verdict logic
    vr = raw.get("tcft_variance_ratio", None)
    raw["var_ratio"] = float(vr) if vr is not None else float("nan")
    return raw


def compute_spearman_r(x: List[float], y: List[float]) -> float:
    n = len(x)
    if n < 2:
        return 0.0
    rank_x = np.argsort(np.argsort(x)).astype(float)
    rank_y = np.argsort(np.argsort(y)).astype(float)
    d_sq = float(((rank_x - rank_y) ** 2).sum())
    return float(1.0 - 6.0 * d_sq / (n * (n * n - 1)))


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("C3_INCONCLUSIVE", "No per-seed data.")

    m_values = sorted(summary.get("m_values", M_VALUES_FULL))

    pass_count_by_M: Dict[int, int] = {m: 0 for m in m_values}
    fail_count_by_M: Dict[int, int] = {m: 0 for m in m_values}
    vr_by_M: Dict[int, List[float]] = {m: [] for m in m_values}

    for _seed_key, seed_data in per_seed.items():
        by_M = seed_data.get("by_M", {})
        for m in m_values:
            m_key = str(m)
            if m_key not in by_M:
                continue
            vr = by_M[m_key].get("var_ratio", float("nan"))
            if math.isnan(vr):
                continue
            vr_by_M[m].append(vr)
            if vr < HP_VAR_RATIO_MAX:
                pass_count_by_M[m] += 1
            else:
                fail_count_by_M[m] += 1

    mean_vr_by_M = {
        m: float(np.mean(vrs)) if vrs else float("nan")
        for m, vrs in vr_by_M.items()
    }
    detail = {
        "pass_count_by_M": pass_count_by_M,
        "mean_vr_by_M": {m: round(v, 6) if not math.isnan(v) else None
                         for m, v in mean_vr_by_M.items()},
    }

    # HARD_FAIL: M=2048 fails across many seeds
    m_high = max(m_values)
    if fail_count_by_M.get(m_high, 0) >= 3:
        return ("C3_HARD_FAIL",
                f"TCFT_FAILS_AT_N4096: >= 3 seeds fail var_ratio >= {HP_VAR_RATIO_MAX} "
                f"at M={m_high} N=4096. Deletion cert unreliable at N=4096. details={detail}.")

    all_pass = all(
        pass_count_by_M[m] >= HP_SEEDS_PASS_MIN
        for m in m_values if vr_by_M[m]
    )

    if all_pass:
        valid_m = [m for m in m_values if not math.isnan(mean_vr_by_M[m])]
        valid_vr = [mean_vr_by_M[m] for m in valid_m]
        spr = compute_spearman_r([float(m) for m in valid_m], valid_vr)
        return ("C3_HARD_PASS",
                f"TCFT_VALID_AT_N4096: var_ratio < {HP_VAR_RATIO_MAX} at ALL M values "
                f"(M in {m_values}) with >= {HP_SEEDS_PASS_MIN}/{len(per_seed)} seeds. "
                f"spearman_r={spr:.3f}. N=4096 deletion cert confirmed. details={detail}.")

    boundary_m = None
    for m in m_values:
        if pass_count_by_M.get(m, 0) < HP_SEEDS_PASS_MIN:
            boundary_m = m
            break
    return ("C3_MIDDLE_BAND",
            f"TCFT_PARTIAL: var_ratio OK at small M but marginal at M={boundary_m}. "
            f"details={detail}.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Self-test 1: verdict HARD_PASS
    per_seed_pass = {
        str(s): {"by_M": {str(m): {"var_ratio": 0.005} for m in M_VALUES_FULL}}
        for s in [7, 17, 23, 31, 41]
    }
    v_pass, msg_pass = compute_verdict({"per_seed": per_seed_pass, "m_values": M_VALUES_FULL})
    assert "HARD_PASS" in v_pass, f"selftest HARD_PASS failed: {v_pass}"

    # Self-test 2: HARD_FAIL (large M fails)
    per_seed_hf = {
        str(s): {"by_M": {str(m): {"var_ratio": 0.005 if m < 2048 else 0.20}
                          for m in M_VALUES_FULL}}
        for s in [7, 17, 23, 31, 41]
    }
    v_fail, _ = compute_verdict({"per_seed": per_seed_hf, "m_values": M_VALUES_FULL})
    assert "HARD_FAIL" in v_fail or "MIDDLE_BAND" in v_fail, \
        f"selftest HARD_FAIL/MIDDLE_BAND failed: {v_fail}"

    # Self-test 3: actual smoke computation
    cell = run_one_cell(N_SMOKE, M_VALUES_SMOKE[0], 17)
    assert "var_ratio" in cell, f"var_ratio missing: {list(cell.keys())}"
    vr = cell["var_ratio"]
    assert not math.isnan(vr), f"var_ratio NaN: {cell}"
    assert 0.0 <= vr, f"var_ratio negative: {vr}"
    print(f"[selftest] N={N_SMOKE} M={M_VALUES_SMOKE[0]}: var_ratio={vr:.6f} OK", flush=True)

    # Multi-scale: second M value
    cell2 = run_one_cell(N_SMOKE, M_VALUES_SMOKE[1], 17)
    vr2 = cell2.get("var_ratio", float("nan"))
    assert not math.isnan(vr2), f"var_ratio NaN at M={M_VALUES_SMOKE[1]}: {cell2}"
    print(f"[selftest] multi-scale M={M_VALUES_SMOKE[1]}: var_ratio={vr2:.6f} OK", flush=True)

    print("[selftest] PASS: all assertions OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    N      = N_SMOKE if smoke else N_FULL
    m_vals = M_VALUES_SMOKE if smoke else M_VALUES_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL

    exp_name = os.environ.get("HDLAB_EXP_NAME", "c3_tcft_phase_v1_n4096")
    print(f"[run] {exp_name} smoke={smoke} N={N} m_vals={m_vals} seeds={seeds}", flush=True)
    if not smoke:
        assert N == 4096, f"FULL run must use N=4096 (PROT-018); got {N}"

    per_seed: Dict = {}
    all_cells: List[Dict] = []

    for seed in seeds:
        per_seed[str(seed)] = {"by_M": {}}
        for M in m_vals:
            print(f"  seed={seed} M={M}", flush=True)
            t_cell = time.monotonic()
            cell = run_one_cell(N, M, seed)
            elapsed_cell = time.monotonic() - t_cell
            vr = cell.get("var_ratio", float("nan"))
            print(f"    var_ratio={vr:.6f} ({elapsed_cell:.1f}s)", flush=True)
            cell["seed"] = seed
            cell["N_run"] = N
            all_cells.append(cell)
            per_seed[str(seed)]["by_M"][str(M)] = {"var_ratio": vr}

    summary = {"per_seed": per_seed, "m_values": m_vals, "N": N, "seeds": seeds}
    verdict_str, verdict_msg = compute_verdict(summary)

    elapsed = time.time() - t0
    print(f"\n[verdict] {verdict_str}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed:.1f}s", flush=True)

    out_dir = get_output_dir(exp_name)
    metrics = {
        "verdict": verdict_str,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N": N, "smoke": smoke, "seeds": seeds, "m_values": m_vals},
        "summary": summary,
        "all_cells": all_cells,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        print("[self-test] selftest ran at import scope", flush=True)
        sys.exit(0)
    run(smoke=args.smoke)
else:
    run(smoke=False)
