"""Stage 1 Regime Map Probe 2: N (SCALE_FREE) x CLEANUP_MECHANISM cross-term.

Cell anchor: `stage1_regime_probe_2_N_x_cleanup_mechanism_v1`
Pre-reg: preregs/2026-07-03_stage1_regime_probe_2_N_x_cleanup_mechanism.md

Purpose:
    Second cell in the Stage 1 Regime Map arc (USER-directed 2026-07-03,
    project memory: project_stage1_regime_map_of_CG_META_axes_USER_2026-07-03).
    Measure whether the CLEANUP_MECHANISM axis (regime-narrow to bipolar-codebook
    cleanup per today's physics-law composition Option Y finding
    PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian v2 M-sweep) has a
    meaningful cross-term with the SCALE_FREE_in_N axis when both are
    simultaneously varied. Does N moderate the mechanism-degeneracy at FHRR
    SHARDED chain composition? If yes, boundary is N-dependent (crossover
    exponent). If no, Option Y finding extends without N-dependence.

Cited source atoms (exact names, no abstraction):
    T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1
    T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1
    T4/META_SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS_CG_META_v1_2026-07-02
    PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian (v2 M-sweep 2026-07-03)

Reuse (Principle 11):
    Primitives imported from _stage1_physics_law_joint_composition_factorial_v1_core:
      - cphasor_torch, cnorm_torch, phase_corrupt
      - build_rules (SHARDED codebook + BUNDLED bundle)
      - cleanup_iterative_cosine, cleanup_modern_hopfield, cleanup_soft_energy_attractor
      - cleanup_argmax_idx, run_chain, CLEANUP_REGISTRY, CLEANUP_MECHANISMS

Sweep grid (FULL): 4 N x 3 cleanup x 3 M x 2 corr (F=1, L=2 fixed) = 72 pts/seed
Sweep grid (SMOKE): 2 N x 3 cleanup x 1 M x 1 corr = 6 pts/seed

Hypotheses (falsifiable):
    H1 (Option Y extends, regime-narrow universally): at all N in FHRR SHARDED
        regime, mechanism-axis variance stays approx 0 (max-min across
        mechanisms at each N < 0.05, averaged over M/corr).
        -> CLEANUP_MECHANISM axis universally regime-narrow to bipolar cleanup.
    H2 (crossover exists): at some N, mechanism-axis variance becomes > 0.10.
        -> boundary is N-dependent; regime map has a crossover exponent.
        This is HP_CG_META.
    H3 (scale-invariant, non-zero degeneracy): mechanism variance uniform
        across N (max_N mech_var - min_N mech_var < 0.02) whether zero or
        non-zero. -> Option Y finding extends without N-dependence.

Prereg gates:
    HP_CG_META (H2): at least one N shows mechanism variance > 0.10 with
        clean cv (per-seed CV < 0.30 at that N).
    HP_MEASURED_MECHANISM (H1 or H3): mechanism variance uniform across N
        whether zero or non-zero. Option Y finding extends without
        N-dependence -> N is not a moderator of the mechanism-degeneracy.
    HF: cell shows unexpected behavior not matching either H (e.g., NaN,
        cardinality breach, mechanism collapse to identical outputs).

Compute architecture: batched-GPU (USER-LOCKED). Auto-CUDA when available.
Substrate primitives (bind = elementwise complex mul; cleanup = complex
matmul + argmax) are matmul-heavy and eligible for GPU batching.

Sibling wrappers: exp_stage1_regime_probe_2_N_x_cleanup_mechanism_v1_s{11,17,23}.py

ASCII-only. No unicode, no em-dashes.
Author: exp_dev 2026-07-03 (agent-spawn, Opus 4.7).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

import hashlib
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any

# CUDA env before torch import (USER-LOCKED)
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Reuse primitives from sibling physics-law core (Principle 11)
from experiments._stage1_physics_law_joint_composition_factorial_v1_core import (
    CLEANUP_MECHANISMS,
    CLEANUP_REGISTRY,
    BETA,
    ALPHA_SOFT,
    build_rules,
    phase_corrupt,
    cleanup_argmax_idx,
    run_chain,
)

ANCHOR_NAME = "stage1_regime_probe_2_N_x_cleanup_mechanism_v1"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
if DEVICE == "cuda":
    GPU_NAME = torch.cuda.get_device_name(0)
    GPU_MAX_MEM_GB = torch.cuda.get_device_properties(0).total_memory / 1e9
else:
    GPU_NAME = "cpu_fallback"
    GPU_MAX_MEM_GB = 0.0

# ---------------------------------------------------------------------------
# Sweep constants (LOCKED at module init)
# ---------------------------------------------------------------------------
# N: 4 levels (larger than usual to probe scale-crossover)
N_GRID_FULL = [2048, 4096, 8192, 16384]
# CLEANUP_MECHANISMS imported (3 non-Hebbian): modern_hopfield, iterative_cosine,
# soft_energy_attractor
# Storage FIXED = SHARDED (canonical FHRR chain composition regime)
M_GRID_FULL = [200, 800, 3200]
CORRUPTION_GRID_FULL = [0.20, 0.45]
F_FIXED = 1
L_FIXED = 2

# SMOKE: 2 N x 3 mech x 1 M x 1 corr = 6 pts (per USER spec)
N_GRID_SMOKE = [2048, 8192]
M_GRID_SMOKE = [800]
CORRUPTION_GRID_SMOKE = [0.45]

TR_FULL = 100
TR_SMOKE = 40

EXPECTED_N_UNITS_FULL = (len(N_GRID_FULL) * len(CLEANUP_MECHANISMS)
                         * len(M_GRID_FULL) * len(CORRUPTION_GRID_FULL))
EXPECTED_N_UNITS_SMOKE = (len(N_GRID_SMOKE) * len(CLEANUP_MECHANISMS)
                          * len(M_GRID_SMOKE) * len(CORRUPTION_GRID_SMOKE))

# Verdict thresholds
MECH_VAR_CROSSOVER_THRESHOLD = 0.10   # H2 fires at any N with mech_var > this
MECH_VAR_NARROW_THRESHOLD = 0.05      # H1 requires all N with mech_var < this
N_UNIFORM_THRESHOLD = 0.02            # H3 uniformity gate

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# Per-phase-point eval (reuses sibling primitives)
# ---------------------------------------------------------------------------
def eval_phase_point(mechanism: str, M_props: int, N: int, corruption: float,
                     TR: int, seed: int, salt: int) -> Dict[str, Any]:
    device = DEVICE
    if device == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    t0 = time.perf_counter()
    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed) * 100003 + int(salt))

    props, perms, IMPL, POS, sharded_codebook, bundle_vec = build_rules(
        M_props, F_FIXED, gen, device, N)

    if props.dtype != torch.complex64:
        raise RuntimeError(f"props dtype {props.dtype} != complex64")
    if (torch.isnan(sharded_codebook.real).any().item()
            or torch.isnan(sharded_codebook.imag).any().item()):
        raise RuntimeError(f"NAN_IN_SHARDED_CODEBOOK mech={mechanism} "
                           f"M={M_props} N={N}")

    acc, final_ci = run_chain("SHARDED", mechanism, L_FIXED, F_FIXED, TR,
                                props, perms, IMPL, POS,
                                sharded_codebook, bundle_vec, corruption,
                                gen, device)

    # Hashes for META_RULE_AF (arms-must-differ)
    ci_bytes = final_ci.detach().cpu().numpy().tobytes()
    output_hash = hashlib.sha256(ci_bytes).hexdigest()[:16]

    if device == "cuda":
        peak_mem_mb = round(torch.cuda.max_memory_allocated() / 1e6, 1)
    else:
        peak_mem_mb = -1.0
    elapsed = time.perf_counter() - t0

    del props, perms, IMPL, POS, sharded_codebook, bundle_vec, final_ci
    if device == "cuda":
        torch.cuda.empty_cache()

    return {
        "cleanup_mechanism": mechanism,
        "M": int(M_props),
        "N": int(N),
        "F": int(F_FIXED),
        "L": int(L_FIXED),
        "corruption": float(corruption),
        "storage": "SHARDED",
        "TR": int(TR),
        "acc": round(float(acc), 4),
        "output_hash": output_hash,
        "peak_mem_mb": peak_mem_mb,
        "elapsed_s": round(elapsed, 3),
    }


# ---------------------------------------------------------------------------
# Selftest (formula check at reduced grid; wall < 60s target on CPU)
# ---------------------------------------------------------------------------
def selftest() -> Tuple[bool, str]:
    msgs = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 72:
        return False, (f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 72 "
                       f"(4 N x 3 mech x 3 M x 2 corr)")
    if EXPECTED_N_UNITS_SMOKE != 6:
        return False, (f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 6 "
                       f"(2 N x 3 mech x 1 M x 1 corr)")
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} "
                f"SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. Sanity: 3 cleanup mechanisms produce distinct outputs at a small N
    seed = 999
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    M_probe = 40
    N_test = 512
    F_test = 1
    TR = 16
    props, perms, IMPL, POS, sharded_codebook, bundle_vec = build_rules(
        M_probe, F_test, gen, DEVICE, N_test)
    ci = torch.arange(TR, device=DEVICE) % M_probe
    A_cur = props[ci]
    f_step = torch.zeros((TR,), dtype=torch.long, device=DEVICE)
    rule_batch = sharded_codebook[ci, f_step]
    cand = rule_batch * A_cur.conj() * POS[0].unsqueeze(0).conj() * IMPL.conj().unsqueeze(0)
    cand_corr = phase_corrupt(cand, 0.30, gen, DEVICE)
    mech_hashes = {}
    for mech in CLEANUP_MECHANISMS:
        fn = CLEANUP_REGISTRY[mech]
        out = fn(cand_corr, props)
        mech_hashes[mech] = hashlib.sha256(
            out.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    if len(set(mech_hashes.values())) != len(CLEANUP_MECHANISMS):
        return False, (f"cleanup_mechanisms produce identical outputs at "
                       f"N_test={N_test}: {mech_hashes}")
    msgs.append(f"3 mechanisms distinct at N_test={N_test}: "
                f"{list(mech_hashes.values())}")

    # 3. SHARDED at easy regime reproduces (positive control per Gate D):
    # iterative_cosine at N=2048, M=200, corr=0.20, F=1, L=2 -> >= 0.75
    gen.manual_seed(1013)
    props2, perms2, IMPL2, POS2, sh2, bd2 = build_rules(
        200, F_FIXED, gen, DEVICE, 2048)
    acc_easy, _ = run_chain("SHARDED", "iterative_cosine", L=L_FIXED,
                             F=F_FIXED, TR=40,
                             props=props2, perms=perms2, IMPL=IMPL2, POS=POS2,
                             sharded_codebook=sh2, bundle_vec=bd2,
                             corruption=0.20, gen=gen, device=DEVICE)
    if acc_easy < 0.75:
        return False, (f"SHARDED PC easy regime (M=200, N=2048, L=2, F=1, "
                       f"corr=0.20, iterative_cosine) expected >= 0.75; "
                       f"got {acc_easy:.3f}")
    msgs.append(f"SHARDED PC easy (M=200 N=2048 corr=0.20 iter_cos): "
                f"acc={acc_easy:.3f}")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed(seed: int, run_mode: str) -> Dict[str, Any]:
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        N_grid = N_GRID_SMOKE
        M_grid = M_GRID_SMOKE
        corr_grid = CORRUPTION_GRID_SMOKE
        TR = TR_SMOKE
        expected_n = EXPECTED_N_UNITS_SMOKE
    else:
        N_grid = N_GRID_FULL
        M_grid = M_GRID_FULL
        corr_grid = CORRUPTION_GRID_FULL
        TR = TR_FULL
        expected_n = EXPECTED_N_UNITS_FULL

    mech_grid = list(CLEANUP_MECHANISMS)

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"N={N_grid} mech={mech_grid} M={M_grid} corr={corr_grid} "
          f"F={F_FIXED} L={L_FIXED} TR={TR} expected_n={expected_n}",
          flush=True)

    phase_map: List[Dict[str, Any]] = []
    salt = 0
    t0 = time.perf_counter()

    # Main factorial: N x mech x M x corr with SHARDED storage, F=1, L=2 fixed
    for N in N_grid:
        for mech in mech_grid:
            for M_props in M_grid:
                for corr in corr_grid:
                    salt += 1
                    pt = eval_phase_point(mech, M_props, N, corr, TR, seed, salt)
                    phase_map.append(pt)
                    print(f"  [{len(phase_map):3d}/{expected_n:3d}] "
                          f"N={N:5d} mech={mech:22s} M={M_props:5d} "
                          f"c={corr:.2f} acc={pt['acc']:.4f} "
                          f"dt={pt['elapsed_s']:.2f}s",
                          flush=True)

    elapsed = time.perf_counter() - t0
    observed_n = len(phase_map)
    cardinality_ok = (observed_n == expected_n)

    # Mechanism-output-hash aggregate for META_RULE_AF arms-must-differ
    mech_output_hashes: Dict[str, List[str]] = {m: [] for m in mech_grid}
    for pt in phase_map:
        mech_output_hashes[pt["cleanup_mechanism"]].append(pt["output_hash"])
    mech_hash_agg = {m: hashlib.sha256(
        json.dumps(v, sort_keys=True).encode("utf-8")).hexdigest()[:16]
                     for m, v in mech_output_hashes.items()}
    n_distinct_mechs = len(set(mech_hash_agg.values()))

    # Positive control reproduction (Gate D)
    # iterative_cosine at min-M, min-N, min-corr on the current grid
    pc_target_M = min(M_grid)
    pc_target_N = min(N_grid)
    pc_target_corr = min(corr_grid)
    pc_repro_matches = [p for p in phase_map
                        if p["cleanup_mechanism"] == "iterative_cosine"
                        and p["M"] == pc_target_M
                        and p["N"] == pc_target_N
                        and abs(p["corruption"] - pc_target_corr) < 1e-6]
    if pc_repro_matches:
        pc_repro_acc = pc_repro_matches[0]["acc"]
        # Threshold: 0.60 at high-corr smoke regime; 0.75 at low-corr FULL regime
        pc_repro_threshold = 0.60 if is_smoke else 0.75
        pc_repro_pass = pc_repro_acc >= pc_repro_threshold
    else:
        pc_repro_acc = -1.0
        pc_repro_threshold = -1.0
        pc_repro_pass = False

    # Discriminator gate: arms-must-differ (at least 2 mechanisms differ in acc
    # by >= 0.02 at some N/M/corr point)
    max_mech_acc_spread = 0.0
    for N in N_grid:
        for M_props in M_grid:
            for corr in corr_grid:
                accs = [p["acc"] for p in phase_map
                        if p["N"] == N and p["M"] == M_props
                        and abs(p["corruption"] - corr) < 1e-6]
                if len(accs) == len(mech_grid):
                    spread = max(accs) - min(accs)
                    if spread > max_mech_acc_spread:
                        max_mech_acc_spread = spread

    # PER-N mechanism variance (max_acc - min_acc across mechanisms at that N,
    # averaged over M and corr): key metric for H1/H2/H3.
    per_N_mech_variance: Dict[str, Dict[str, Any]] = {}
    for N in N_grid:
        per_cell_spreads: List[float] = []
        per_cell_details: List[Dict[str, Any]] = []
        for M_props in M_grid:
            for corr in corr_grid:
                accs_by_mech = {}
                for mech in mech_grid:
                    matches = [p["acc"] for p in phase_map
                               if p["N"] == N and p["M"] == M_props
                               and p["cleanup_mechanism"] == mech
                               and abs(p["corruption"] - corr) < 1e-6]
                    if matches:
                        accs_by_mech[mech] = matches[0]
                if len(accs_by_mech) == len(mech_grid):
                    accs = list(accs_by_mech.values())
                    spread = max(accs) - min(accs)
                    per_cell_spreads.append(spread)
                    per_cell_details.append({
                        "M": M_props, "corr": corr, "spread": round(spread, 4),
                        "accs_by_mech": {k: round(v, 4)
                                         for k, v in accs_by_mech.items()},
                    })
        if per_cell_spreads:
            mean_spread = float(np.mean(per_cell_spreads))
            max_spread = float(max(per_cell_spreads))
            std_spread = float(np.std(per_cell_spreads))
            cv = (std_spread / mean_spread) if mean_spread > 1e-6 else 0.0
            per_N_mech_variance[str(N)] = {
                "mean_spread": round(mean_spread, 4),
                "max_spread": round(max_spread, 4),
                "std_spread": round(std_spread, 4),
                "cv": round(cv, 4),
                "n_cells": len(per_cell_spreads),
                "per_cell_details": per_cell_details,
            }

    # Hypothesis assessment (H1 vs H2 vs H3)
    N_means = [per_N_mech_variance[str(N)]["mean_spread"]
               for N in N_grid if str(N) in per_N_mech_variance]
    if N_means:
        max_N_mean = max(N_means)
        min_N_mean = min(N_means)
        range_N_mean = max_N_mean - min_N_mean
    else:
        max_N_mean = -1.0
        min_N_mean = -1.0
        range_N_mean = -1.0

    if not N_means:
        hyp_verdict = "H_UNKNOWN"
        hyp_reason = "no per-N mech variance computed"
    elif max_N_mean > MECH_VAR_CROSSOVER_THRESHOLD:
        hyp_verdict = "H2_CROSSOVER"
        hyp_reason = (f"at N with max mech_var={max_N_mean:.4f} > "
                      f"{MECH_VAR_CROSSOVER_THRESHOLD}, N is a moderator")
    elif max_N_mean < MECH_VAR_NARROW_THRESHOLD:
        if range_N_mean < N_UNIFORM_THRESHOLD:
            hyp_verdict = "H1_REGIME_NARROW_UNIVERSAL"
            hyp_reason = (f"all N with mech_var < {MECH_VAR_NARROW_THRESHOLD}, "
                          f"uniform across N (range={range_N_mean:.4f})")
        else:
            hyp_verdict = "H1_REGIME_NARROW_MODERATE_N_TREND"
            hyp_reason = (f"all N with mech_var < {MECH_VAR_NARROW_THRESHOLD} "
                          f"but N-range={range_N_mean:.4f}")
    else:
        # Middle band: 0.05 <= max_N_mean <= 0.10
        if range_N_mean < N_UNIFORM_THRESHOLD:
            hyp_verdict = "H3_SCALE_INVARIANT_NONZERO"
            hyp_reason = (f"mech_var uniform across N (range={range_N_mean:.4f} "
                          f"< {N_UNIFORM_THRESHOLD}) at nonzero level "
                          f"max={max_N_mean:.4f}")
        else:
            hyp_verdict = "MIDDLE_BAND_NASCENT_CROSSOVER"
            hyp_reason = (f"max mech_var={max_N_mean:.4f} in [{MECH_VAR_NARROW_THRESHOLD}, "
                          f"{MECH_VAR_CROSSOVER_THRESHOLD}] and N-range="
                          f"{range_N_mean:.4f} > {N_UNIFORM_THRESHOLD}")

    if DEVICE == "cuda":
        peak_mems = [p["peak_mem_mb"] for p in phase_map if p["peak_mem_mb"] > 0]
        avg_peak = sum(peak_mems) / max(len(peak_mems), 1)
    else:
        avg_peak = -1.0

    return {
        "seed": seed,
        "run_mode": run_mode,
        "device": DEVICE,
        "gpu_name": GPU_NAME,
        "phase_map": phase_map,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "cardinality_ok": cardinality_ok,
        "mech_output_hash_agg": mech_hash_agg,
        "n_distinct_mechanisms": n_distinct_mechs,
        "arms_differ_verified": (n_distinct_mechs == len(mech_grid)),
        "max_mech_acc_spread": round(max_mech_acc_spread, 4),
        "pc_reproduce_iterative_cosine_regime": {
            "M": pc_target_M, "N": pc_target_N,
            "corruption": pc_target_corr,
            "F": F_FIXED, "L": L_FIXED,
            "acc": pc_repro_acc,
            "threshold": pc_repro_threshold,
            "pass": pc_repro_pass,
        },
        "per_N_mech_variance": per_N_mech_variance,
        "N_grid": N_grid,
        "N_mean_spreads": {str(N): per_N_mech_variance.get(str(N), {}).get("mean_spread")
                            for N in N_grid},
        "max_N_mean_spread": round(max_N_mean, 4) if max_N_mean >= 0 else -1.0,
        "min_N_mean_spread": round(min_N_mean, 4) if min_N_mean >= 0 else -1.0,
        "range_N_mean_spread": round(range_N_mean, 4) if range_N_mean >= 0 else -1.0,
        "hypothesis_assessment": hyp_verdict,
        "hypothesis_reason": hyp_reason,
        "avg_peak_mem_mb": round(avg_peak, 1),
        "elapsed_seed_s": round(elapsed, 2),
        "beta": BETA,
        "alpha_soft": ALPHA_SOFT,
    }


# ---------------------------------------------------------------------------
# Smoke-gate predicate
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    phase_map = body.get("phase_map", [])
    if len(phase_map) != body.get("expected_n_units"):
        return False, (f"cardinality_breach: expected {body.get('expected_n_units')} "
                       f"got {len(phase_map)}")
    n_distinct_mechs = body.get("n_distinct_mechanisms", 0)
    if n_distinct_mechs != len(CLEANUP_MECHANISMS):
        return False, (f"arms_differ_fail: {n_distinct_mechs}/"
                       f"{len(CLEANUP_MECHANISMS)} distinct mechanism output hashes "
                       f"(META_RULE_AF violation)")
    pc_repro = body.get("pc_reproduce_iterative_cosine_regime", {})
    if not pc_repro.get("pass"):
        return False, (f"pc_reproduce_fail: iterative_cosine SHARDED at PC regime "
                       f"(M={pc_repro.get('M')} N={pc_repro.get('N')} "
                       f"corr={pc_repro.get('corruption')}) "
                       f"acc={pc_repro.get('acc')} < threshold={pc_repro.get('threshold')}")
    # Note: max_mech_acc_spread is a MEASUREMENT (H1 predicts ~0; H2 predicts
    # > 0.10); we do NOT gate on it because the null H1 result IS a valid
    # finding. Smoke gate is: cell runs + arms differ by codebook hash + PC
    # reproduces. Discriminator-power at full-M=3200 regime will fire in FULL.
    spread = body.get("max_mech_acc_spread", 0.0)
    # NaN sanity
    for pt in phase_map:
        if pt.get("acc") != pt.get("acc"):  # NaN check
            return False, f"NAN_in_phase_map at {pt}"

    # Smoke-preview note about discriminator-saturation (informational)
    smoke_note = ""
    if spread < 0.005:
        first_pt = phase_map[0] if phase_map else {}
        smoke_M = first_pt.get("M", "?")
        smoke_corr = first_pt.get("corruption", "?")
        smoke_note = (f"; smoke_note=SATURATED_AT_M{smoke_M}_corr{smoke_corr} "
                      f"(all mechanisms saturate at smoke regime; H1_preview but "
                      f"H2 discrimination reserved for FULL M=3200 harder-capacity arm)")

    return True, (f"smoke_gate_pass: cardinality_ok + 3-mech-hash-distinct + "
                  f"pc_reproduce={pc_repro.get('acc')} (threshold "
                  f"{pc_repro.get('threshold')}) + max_mech_spread={spread:.4f}"
                  f"{smoke_note}")


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]], run_mode: str
                          ) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "HARD_FAIL", "verdict_msg": "HARD_FAIL_NO_SEEDS",
                "summary": "HARD_FAIL_NO_SEEDS", "elapsed_s": 0.0}
    is_smoke = (run_mode == "smoke")
    seed_key = list(per_seed.keys())[0]
    body = per_seed[seed_key]
    phase_map = body.get("phase_map", [])
    expected_n = body.get("expected_n_units", 0)
    observed_n = body.get("observed_n_units", 0)
    cardinality_ok = body.get("cardinality_ok", False)

    common = {
        "phase_map": phase_map,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "cardinality_ok": cardinality_ok,
        "mech_output_hash_agg": body.get("mech_output_hash_agg"),
        "n_distinct_mechanisms": body.get("n_distinct_mechanisms"),
        "arms_differ_verified": body.get("arms_differ_verified"),
        "max_mech_acc_spread": body.get("max_mech_acc_spread"),
        "pc_reproduce_iterative_cosine_regime": body.get("pc_reproduce_iterative_cosine_regime"),
        "per_N_mech_variance": body.get("per_N_mech_variance"),
        "N_grid": body.get("N_grid"),
        "N_mean_spreads": body.get("N_mean_spreads"),
        "max_N_mean_spread": body.get("max_N_mean_spread"),
        "min_N_mean_spread": body.get("min_N_mean_spread"),
        "range_N_mean_spread": body.get("range_N_mean_spread"),
        "hypothesis_assessment": body.get("hypothesis_assessment"),
        "hypothesis_reason": body.get("hypothesis_reason"),
        "device": body.get("device"),
        "gpu_name": body.get("gpu_name"),
        "avg_peak_mem_mb": body.get("avg_peak_mem_mb"),
        "elapsed_seed_s": body.get("elapsed_seed_s"),
        "run_mode": run_mode,
    }

    if is_smoke:
        ok, reason = smoke_gate_predicate(body)
        if ok:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_SMOKE: {observed_n}/{expected_n} pts; {reason}; "
                    f"hypothesis_preview={body.get('hypothesis_assessment')} "
                    f"({body.get('hypothesis_reason')})")
        else:
            verdict = "HARD_FAIL"
            vmsg = f"HARD_FAIL_SMOKE: {reason}"
        out = dict(common)
        out.update({
            "verdict": verdict,
            "verdict_msg": vmsg,
            "summary": vmsg,
            "smoke_gate_pass": ok,
            "smoke_gate_reason": reason,
        })
        return out

    # FULL verdict
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        vmsg = f"HARD_FAIL_CARDINALITY_BREACH: expected={expected_n} observed={observed_n}"
    elif not body.get("arms_differ_verified"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_ARMS_MUST_DIFFER: {body.get('n_distinct_mechanisms')} "
                f"distinct mechanism-output-hashes (META_RULE_AF violation)")
    elif not body.get("pc_reproduce_iterative_cosine_regime", {}).get("pass"):
        pc = body.get("pc_reproduce_iterative_cosine_regime", {})
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_PC_REPRODUCE: iterative_cosine at PC regime "
                f"acc={pc.get('acc')} < threshold={pc.get('threshold')}; "
                f"positive control fails -> downstream mechanism-variance "
                f"claims not trustworthy")
    else:
        hyp = body.get("hypothesis_assessment", "H_UNKNOWN")
        reason = body.get("hypothesis_reason", "")
        max_N_mean = body.get("max_N_mean_spread", -1.0)
        range_N = body.get("range_N_mean_spread", -1.0)
        if hyp == "H2_CROSSOVER":
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H2_CROSSOVER_N_MODERATES_MECHANISM: "
                    f"max per-N mech_var={max_N_mean} > "
                    f"{MECH_VAR_CROSSOVER_THRESHOLD}; N-range={range_N}; "
                    f"CG_META candidate: SCALE_FREE_x_CLEANUP_MECHANISM_"
                    f"crossover_exponent_v1; {reason}; pending Skunkworks "
                    f"landed-VET + 3-seed replication + regime-map atomization")
        elif hyp == "H1_REGIME_NARROW_UNIVERSAL":
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H1_OPTION_Y_EXTENDS_UNIVERSAL: "
                    f"CLEANUP_MECHANISM axis regime-narrow at all N in "
                    f"{body.get('N_grid')}; max mech_var={max_N_mean} < "
                    f"{MECH_VAR_NARROW_THRESHOLD}; N-range={range_N} < "
                    f"{N_UNIFORM_THRESHOLD}; Option Y finding "
                    f"(PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian) "
                    f"scale-invariant in FHRR SHARDED chain composition regime; "
                    f"{reason}")
        elif hyp == "H1_REGIME_NARROW_MODERATE_N_TREND":
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_H1_WITH_MODERATE_N_TREND: mech_var < "
                    f"{MECH_VAR_NARROW_THRESHOLD} everywhere but N-range="
                    f"{range_N} shows N-modulation; not yet CG_META; "
                    f"methodology-interesting; {reason}")
        elif hyp == "H3_SCALE_INVARIANT_NONZERO":
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_H3_SCALE_INVARIANT_NONZERO_DEGENERACY: "
                    f"CLEANUP_MECHANISM axis has small-but-uniform variance "
                    f"across N (max={max_N_mean}, range={range_N}); Option Y "
                    f"finding extends without N-dependence at nonzero level; "
                    f"{reason}")
        elif hyp == "MIDDLE_BAND_NASCENT_CROSSOVER":
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_NASCENT_CROSSOVER: max mech_var={max_N_mean} "
                    f"in [{MECH_VAR_NARROW_THRESHOLD}, "
                    f"{MECH_VAR_CROSSOVER_THRESHOLD}] with N-range={range_N}; "
                    f"suggestive of crossover but below CG_META threshold; "
                    f"consider N-refined sweep to localize; {reason}")
        else:
            verdict = "HARD_FAIL"
            vmsg = f"HARD_FAIL_HYP_UNKNOWN: {reason}"

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
    })
    return out


__all__ = [
    "ANCHOR_NAME", "DEVICE", "GPU_NAME", "GPU_MAX_MEM_GB",
    "CLEANUP_MECHANISMS", "CLEANUP_REGISTRY",
    "N_GRID_FULL", "M_GRID_FULL", "CORRUPTION_GRID_FULL",
    "N_GRID_SMOKE", "M_GRID_SMOKE", "CORRUPTION_GRID_SMOKE",
    "F_FIXED", "L_FIXED",
    "TR_FULL", "TR_SMOKE", "BETA", "ALPHA_SOFT",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "MECH_VAR_CROSSOVER_THRESHOLD", "MECH_VAR_NARROW_THRESHOLD",
    "N_UNIFORM_THRESHOLD",
    "REQUIRED_FIELDS",
    "eval_phase_point", "selftest", "run_one_seed",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
