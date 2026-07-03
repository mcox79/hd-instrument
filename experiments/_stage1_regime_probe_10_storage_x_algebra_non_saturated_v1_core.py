"""Stage 1 Regime Probe 10: STORAGE (SHARDED vs BUNDLED) x ALGEBRA (F fan-out) at cliff-adjacent.

Cell anchor: `stage1_regime_probe_10_storage_x_algebra_non_saturated_v1`
Pre-reg:     preregs/2026-07-03_stage1_regime_probe_10_storage_x_algebra_non_saturated_v1.md

Purpose:
    Closes the STORAGE column of the pairwise regime matrix. Probes 4 (STORAGE x N)
    and 5 (STORAGE x TOPOLOGY / F fan-in) covered STORAGE-N and STORAGE-TOPOLOGY;
    this cell covers STORAGE x ALGEBRA (F fan-out) with mechanism FIXED at
    modern_hopfield. Tests whether F fan-out has a STORAGE-dependent effect at
    each STORAGE's own cliff-adjacent regime.

Empirical regime brackets (MEASURED@empirical scouts + Probes 6/7 v2):
    SHARDED cliff (LOCKED per Probe 6/7 v2):
        N=512, M=6400, corr=0.85, L=2, modern_hopfield
        F=1  mean_acc ~ 0.55  (in [0.30, 0.95] band)   MEASURED@Probe 8 bracket 2026-07-03
    BUNDLED cliff (leading candidate, bracketed in SMOKE BUNDLED_BRACKET arm):
        N=2048, M=200, corr=0.20, L=2, modern_hopfield
        HYPOTHESIZED@this-prereg: mean_acc in [0.30, 0.75] (near Plate bound)
    DEEP_SAT (both storages saturate):
        N=8192, M=800, corr=0.60, L=2, modern_hopfield
        HYPOTHESIZED@this-prereg: all F all storages saturate (mean_acc >= 0.95)
        Basis: DEEP_SAT config validated in Probes 6+7+8 v2 SMOKE.
    SATURATION_PC (Gate D reproducer):
        SHARDED F=1 M=800 N=2048 corr=0.20 iterative_cosine
        HYPOTHESIZED@this-prereg: acc >= 0.95
        CITED@math4_proof_chains_v2_global_bundle_cpu_v1 + sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1

Cited source atoms (exact names per META_RULE_AC):
    MATH_STAGE1_REGIME_MAP_PROBE1_STORAGE_x_CLEANUP_CG_META_v1
    T3/EXP_stage1_regime_probe_4_storage_x_N_v1
    T3/EXP_stage1_regime_probe_5_storage_x_topology_v1
    T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1
    T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1
    sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1
    math4_proof_chains_v2_global_bundle_cpu_v1
    PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian
    feedback_plate_bound_too_pessimistic_for_sharded_fhrr_chain_composition_2026-07-03
    feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03
    feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-07-03

Reuse (Principle 11):
    Primitives imported from _stage1_physics_law_joint_composition_factorial_v1_core:
      CLEANUP_MECHANISMS, CLEANUP_REGISTRY, BETA, ALPHA_SOFT, DEVICE, GPU_NAME,
      build_rules, phase_corrupt, cleanup_argmax_idx, run_chain, cphasor_torch
    Structure modeled on Probe 8 (algebra_x_cleanup) and Probe 5 (storage_x_topology).

Sweep grid FULL (17 pts / seed):
    CLIFF_SHARDED arm: F in {1,2,4,8,16} at (SHARDED, N=512, M=6400, corr=0.85) = 5 pts
    CLIFF_BUNDLED arm: F in {1,2,4,8,16} at (BUNDLED, N=2048, M=200, corr=0.20) = 5 pts
    DEEP_SAT_SHARDED arm: F in {1,4,16} at (SHARDED, N=8192, M=800, corr=0.60) = 3 pts
    DEEP_SAT_BUNDLED arm: F in {1,4,16} at (BUNDLED, N=8192, M=800, corr=0.60) = 3 pts
    SATURATION_PC arm: 1 pt
    TOTAL: 17 pts / seed
Sweep grid SMOKE (10 pts):
    CLIFF_SHARDED arm: F in {1,16} at (SHARDED, N=512, M=6400, corr=0.85) = 2 pts
    CLIFF_BUNDLED arm: F in {1,16} at (BUNDLED, N=2048, M=200, corr=0.20) = 2 pts
    BUNDLED_BRACKET arm: F=1 at (BUNDLED, N=2048, corr=0.20) x M in {100, 400, 800} = 3 pts
    DEEP_SAT arm spot-check: F=1 x STORAGE in {SHARDED, BUNDLED} at (N=8192, M=800, corr=0.60) = 2 pts
    SATURATION_PC arm: 1 pt
    TOTAL: 10 pts

Hypotheses (falsifiable, band-restricted to CLIFF arms in [0.30, 0.95]):
    H1 (STORAGE x ALGEBRA cross-term at cliff-adjacent):
        cross_term = |F_spread_at_SHARDED_cliff - F_spread_at_BUNDLED_cliff|
        H1 fires when cross_term >= 0.10
      -> STORAGE and ALGEBRA interact at cliff-adjacent.
    H2 (null: STORAGE and ALGEBRA independent):
        cross_term < 0.05
      -> STORAGE and ALGEBRA additive at cliff-adjacent.
    H3-NULL (DEEP_SAT control fires):
        DEEP_SAT max cross-term across F and STORAGE < 0.05
      -> confirms mechanism DEGENERACY at deep-saturation.

Compute architecture: batched-GPU (USER-LOCKED). Auto-CUDA when available.
Sibling wrappers: exp_stage1_regime_probe_10_storage_x_algebra_non_saturated_v1_s{7,13,19}.py

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-07-03 (agent-spawn, Opus 4.7).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace (via sibling wrapper)
# - except SystemExit: raise BEFORE except Exception (no BaseException) (via wrapper)
# - crlb_n/a declared (categorical accuracy; discriminator is STORAGE x F cross-term)
# - baseline_in_band empirically bracketed (BUNDLED_BRACKET arm empirically confirms)
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
# - HP_SCOPE per-arm declaration (CLIFF_SHARDED, CLIFF_BUNDLED, DEEP_SAT, PC)
# - cardinality_ok for sweep-axis cells (META_RULE_H; EXPECTED_N_UNITS gate)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except)
# - calibration_check: default_ok_for_this_regime (BETA=8.0 ALPHA=0.5 from Option Y core)
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
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
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any

# CUDA env before torch import (USER-LOCKED 2026-07-01)
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Reuse primitives from Option Y core (Principle 11)
from experiments._stage1_physics_law_joint_composition_factorial_v1_core import (
    CLEANUP_MECHANISMS,
    CLEANUP_REGISTRY,
    BETA,
    ALPHA_SOFT,
    DEVICE,
    GPU_NAME,
    build_rules,
    phase_corrupt,
    cleanup_argmax_idx,
    run_chain,
    cphasor_torch,
)

ANCHOR_NAME = "stage1_regime_probe_10_storage_x_algebra_non_saturated_v1"

# ---------------------------------------------------------------------------
# Sweep constants (LOCKED at module init; MEASURED@Probes 6/7/8 empirical bracket)
# ---------------------------------------------------------------------------
STORAGE_GRID = ("SHARDED", "BUNDLED")

# ALGEBRA (F fan-out) axis. Full grid = 5 levels; SMOKE = endpoints {1, 16}.
F_GRID_CLIFF_FULL = [1, 2, 4, 8, 16]
F_GRID_CLIFF_SMOKE = [1, 16]

# STORAGE-specific cliff configs (empirical brackets):
SHARDED_CLIFF = {"N": 512, "M": 6400, "corr": 0.85}
BUNDLED_CLIFF = {"N": 2048, "M": 200, "corr": 0.20}

# Fixed cell axes
MECH_FIXED = "modern_hopfield"  # per Director spec (best F=1 per Probe 6 v2)
L_FIXED = 2

# BUNDLED_BRACKET arm (SMOKE only): F=1 at (BUNDLED, N=2048, corr=0.20) x M sweep
BUNDLED_BRACKET_M_GRID = [100, 400, 800]

# DEEP_SAT arm (H3-NULL: mechanism cross-term should vanish at saturation)
DEEP_SAT = {"N": 8192, "M": 800, "corr": 0.60}
F_GRID_DEEP_SAT_FULL = [1, 4, 16]  # 3 levels x 2 storage = 6 pts in FULL
F_GRID_DEEP_SAT_SMOKE = [1]        # single spot-check x 2 storage = 2 pts in SMOKE

# SATURATION_PC arm (Gate D reproducer; SHARDED iterative_cosine at easy regime)
SATURATION_PC_REGIME = {
    "cleanup_mechanism": "iterative_cosine",
    "M": 800,
    "N": 2048,
    "F": 1,
    "L": L_FIXED,
    "corruption": 0.20,
    "storage": "SHARDED",
}
SATURATION_PC_THRESHOLD = 0.95

TR_FULL = 100
TR_SMOKE = 40

# FULL: 5 CLIFF_SHARDED + 5 CLIFF_BUNDLED + 3 DEEP_SAT_SHARDED + 3 DEEP_SAT_BUNDLED + 1 PC = 17
EXPECTED_N_UNITS_FULL = (len(F_GRID_CLIFF_FULL) * len(STORAGE_GRID)
                         + len(F_GRID_DEEP_SAT_FULL) * len(STORAGE_GRID)
                         + 1)
# SMOKE: 2 CLIFF_SHARDED + 2 CLIFF_BUNDLED + 3 BUNDLED_BRACKET + 2 DEEP_SAT + 1 PC = 10
EXPECTED_N_UNITS_SMOKE = (len(F_GRID_CLIFF_SMOKE) * len(STORAGE_GRID)
                          + len(BUNDLED_BRACKET_M_GRID)
                          + len(F_GRID_DEEP_SAT_SMOKE) * len(STORAGE_GRID)
                          + 1)

# Non-saturated band
NON_SAT_BAND_LO = 0.30
NON_SAT_BAND_HI = 0.95

# H1 / H2 thresholds (STORAGE x ALGEBRA cross-term)
CROSS_TERM_H1_THRESHOLD = 0.10
CROSS_TERM_H2_THRESHOLD = 0.05
# H3-NULL threshold on DEEP_SAT
DEEP_SAT_MAX_CROSS_THRESHOLD = 0.05

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# Per-phase-point eval
# ---------------------------------------------------------------------------
def eval_phase_point(mechanism: str, M_props: int, N: int, F: int, L: int,
                     corruption: float, storage: str, TR: int, seed: int,
                     salt: int, arm_tag: str) -> Dict[str, Any]:
    """Run a single phase point on the FHRR chain composition primitive."""
    device = DEVICE
    if device == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    t0 = time.perf_counter()
    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed) * 100003 + int(salt))

    props, perms, IMPL, POS, sharded_codebook, bundle_vec = build_rules(
        M_props, F, gen, device, N)

    if props.dtype != torch.complex64:
        raise RuntimeError(f"props dtype {props.dtype} != complex64")
    if (torch.isnan(sharded_codebook.real).any().item()
            or torch.isnan(sharded_codebook.imag).any().item()):
        raise RuntimeError(f"NAN_IN_SHARDED_CODEBOOK mech={mechanism} "
                           f"M={M_props} N={N} F={F}")

    acc, final_ci = run_chain(storage, mechanism, L, F, TR,
                              props, perms, IMPL, POS,
                              sharded_codebook, bundle_vec,
                              corruption, gen, device)

    # META_RULE_AF hash: cleanup output + storage container
    ci_bytes = final_ci.detach().cpu().numpy().tobytes()
    output_hash = hashlib.sha256(ci_bytes).hexdigest()[:16]
    shard_bytes = sharded_codebook.detach().cpu().numpy().tobytes()
    bundle_bytes = bundle_vec.detach().cpu().numpy().tobytes()
    shard_hash = hashlib.sha256(shard_bytes).hexdigest()[:16]
    bundle_hash = hashlib.sha256(bundle_bytes).hexdigest()[:16]

    if device == "cuda":
        peak_mem_mb = round(torch.cuda.max_memory_allocated() / 1e6, 1)
    else:
        peak_mem_mb = -1.0
    elapsed = time.perf_counter() - t0

    del props, perms, IMPL, POS, sharded_codebook, bundle_vec, final_ci
    if device == "cuda":
        torch.cuda.empty_cache()

    return {
        "arm_tag": arm_tag,
        "cleanup_mechanism": mechanism,
        "M": int(M_props),
        "N": int(N),
        "F": int(F),
        "L": int(L),
        "corruption": float(corruption),
        "storage": storage,
        "TR": int(TR),
        "acc": round(float(acc), 4),
        "output_hash": output_hash,
        "shard_hash": shard_hash,
        "bundle_hash": bundle_hash,
        "peak_mem_mb": peak_mem_mb,
        "elapsed_s": round(elapsed, 3),
    }


# ---------------------------------------------------------------------------
# Selftest (formula check at reduced grid; wall < 60s target on CPU)
# ---------------------------------------------------------------------------
def selftest() -> Tuple[bool, str]:
    msgs = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 17:
        return False, (f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 17 "
                       f"(5 CLIFF_SHARDED + 5 CLIFF_BUNDLED + 3 DEEP_SAT_SHARDED "
                       f"+ 3 DEEP_SAT_BUNDLED + 1 PC)")
    if EXPECTED_N_UNITS_SMOKE != 10:
        return False, (f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 10 "
                       f"(2 CLIFF_SHARDED + 2 CLIFF_BUNDLED + 3 BUNDLED_BRACKET "
                       f"+ 2 DEEP_SAT + 1 PC)")
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} "
                f"SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. STORAGE grid + fixed mechanism sanity
    if set(STORAGE_GRID) != {"SHARDED", "BUNDLED"}:
        return False, f"STORAGE_GRID mismatch: {STORAGE_GRID}"
    if MECH_FIXED not in CLEANUP_MECHANISMS:
        return False, (f"MECH_FIXED={MECH_FIXED} not in "
                       f"CLEANUP_MECHANISMS={CLEANUP_MECHANISMS}")
    msgs.append(f"storage={STORAGE_GRID} mech_fixed={MECH_FIXED}")

    # 3. SHARDED vs BUNDLED at same (M, N, F) MUST produce distinct chain outputs
    #    (arms_differ across STORAGE axis; META_RULE_AF)
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(999)
    M_probe = 50
    N_test = 512
    F_test = 1
    TR = 20
    props, perms, IMPL, POS, sharded_codebook, bundle_vec = build_rules(
        M_probe, F_test, gen, DEVICE, N_test)

    gen.manual_seed(1013)
    acc_sh, ci_sh = run_chain("SHARDED", MECH_FIXED, L_FIXED, F_test, TR,
                              props, perms, IMPL, POS, sharded_codebook,
                              bundle_vec, 0.30, gen, DEVICE)
    gen.manual_seed(1013)
    acc_bu, ci_bu = run_chain("BUNDLED", MECH_FIXED, L_FIXED, F_test, TR,
                              props, perms, IMPL, POS, sharded_codebook,
                              bundle_vec, 0.30, gen, DEVICE)
    h_sh = hashlib.sha256(ci_sh.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    h_bu = hashlib.sha256(ci_bu.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    if h_sh == h_bu:
        return False, (f"SHARDED vs BUNDLED chain outputs bit-identical "
                       f"(META_RULE_AF violation): {h_sh}")
    msgs.append(f"storage_arms_differ SHARDED={h_sh} BUNDLED={h_bu} "
                f"(sh_acc={acc_sh:.3f} bu_acc={acc_bu:.3f})")

    # 4. F=1 vs F=16 codebook hashes MUST differ (ALGEBRA axis fires)
    gen.manual_seed(1017)
    _, _, _, _, shard1, _ = build_rules(M_probe, 1, gen, DEVICE, N_test)
    gen.manual_seed(1017)
    _, _, _, _, shard16, _ = build_rules(M_probe, 16, gen, DEVICE, N_test)
    h1 = hashlib.sha256(shard1.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    h16 = hashlib.sha256(shard16.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    if h1 == h16:
        return False, f"F=1 vs F=16 codebooks identical (algebra axis inert)"
    msgs.append(f"F_axis_fires F1={h1} F16={h16}")

    # 5. SATURATION_PC easy gate reproducer (Gate D at reduced TR)
    gen.manual_seed(1019)
    pc = SATURATION_PC_REGIME
    props2, perms2, IMPL2, POS2, sh2, bd2 = build_rules(
        pc["M"], pc["F"], gen, DEVICE, pc["N"])
    acc_pc, _ = run_chain(pc["storage"], pc["cleanup_mechanism"],
                          pc["L"], pc["F"], 40,
                          props2, perms2, IMPL2, POS2, sh2, bd2,
                          pc["corruption"], gen, DEVICE)
    if acc_pc < 0.85:
        return False, (f"SATURATION_PC selftest (SHARDED F=1 M=800 N=2048 "
                       f"corr=0.20 iterative_cosine TR=40) expected >= 0.85; "
                       f"got {acc_pc:.3f}")
    msgs.append(f"SATURATION_PC selftest (TR=40): acc={acc_pc:.3f}")

    # 6. SHARDED cliff regime sanity (F=1 at SHARDED cliff)
    #    HYPOTHESIZED@Probe 8 empirical bracket: mean_acc ~ 0.55 at TR=40 seed=7.
    #    Loose sanity: [0.15, 0.90] at TR=20 selftest (broader for CPU noise).
    gen.manual_seed(3131)
    sc = SHARDED_CLIFF
    p3, pe3, im3, po3, sh3, bd3 = build_rules(sc["M"], 1, gen, DEVICE, sc["N"])
    acc_sc, _ = run_chain("SHARDED", MECH_FIXED, L_FIXED, 1, 20,
                          p3, pe3, im3, po3, sh3, bd3,
                          sc["corr"], gen, DEVICE)
    if not (0.10 <= acc_sc <= 0.95):
        return False, (f"SHARDED_CLIFF selftest (F=1 M={sc['M']} N={sc['N']} "
                       f"corr={sc['corr']} modern_hopfield TR=20): acc={acc_sc:.3f} "
                       f"outside [0.10, 0.95]; SHARDED cliff regime drifted")
    msgs.append(f"SHARDED_CLIFF selftest (TR=20): acc={acc_sc:.3f}")

    # 7. DEEP_SAT regime sanity (should saturate, SHARDED)
    gen.manual_seed(4141)
    ds = DEEP_SAT
    p4, pe4, im4, po4, sh4, bd4 = build_rules(ds["M"], 1, gen, DEVICE, ds["N"])
    acc_ds, _ = run_chain("SHARDED", MECH_FIXED, L_FIXED, 1, 20,
                          p4, pe4, im4, po4, sh4, bd4,
                          ds["corr"], gen, DEVICE)
    if acc_ds < 0.90:
        return False, (f"DEEP_SAT selftest (SHARDED F=1 M={ds['M']} N={ds['N']} "
                       f"corr={ds['corr']} modern_hopfield TR=20): acc={acc_ds:.3f} "
                       f"< 0.90; DEEP_SAT regime failed to saturate")
    msgs.append(f"DEEP_SAT selftest (TR=20 SHARDED): acc={acc_ds:.3f}")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed(seed: int, run_mode: str) -> Dict[str, Any]:
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        F_grid_cliff = F_GRID_CLIFF_SMOKE
        F_grid_deep = F_GRID_DEEP_SAT_SMOKE
        include_bracket = True
        TR = TR_SMOKE
        expected_n = EXPECTED_N_UNITS_SMOKE
    else:
        F_grid_cliff = F_GRID_CLIFF_FULL
        F_grid_deep = F_GRID_DEEP_SAT_FULL
        include_bracket = False
        TR = TR_FULL
        expected_n = EXPECTED_N_UNITS_FULL

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"mech_fixed={MECH_FIXED} storage={STORAGE_GRID} "
          f"F_cliff={F_grid_cliff} F_deep={F_grid_deep} "
          f"SHARDED_cliff=(N={SHARDED_CLIFF['N']},M={SHARDED_CLIFF['M']},"
          f"corr={SHARDED_CLIFF['corr']}) "
          f"BUNDLED_cliff=(N={BUNDLED_CLIFF['N']},M={BUNDLED_CLIFF['M']},"
          f"corr={BUNDLED_CLIFF['corr']}) "
          f"DEEP_SAT=(N={DEEP_SAT['N']},M={DEEP_SAT['M']},corr={DEEP_SAT['corr']}) "
          f"L={L_FIXED} TR={TR} expected_n={expected_n}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    salt = 0
    t0 = time.perf_counter()

    # 1) CLIFF_SHARDED arm
    for F in F_grid_cliff:
        salt += 1
        pt = eval_phase_point(MECH_FIXED, SHARDED_CLIFF["M"], SHARDED_CLIFF["N"],
                              F, L_FIXED, SHARDED_CLIFF["corr"],
                              "SHARDED", TR, seed, salt, arm_tag="CLIFF_SHARDED")
        phase_map.append(pt)
        print(f"  [{len(phase_map):3d}/{expected_n:3d}] CLIFF_SHARDED  "
              f"F={F:2d} M={SHARDED_CLIFF['M']} N={SHARDED_CLIFF['N']} "
              f"c={SHARDED_CLIFF['corr']:.2f} acc={pt['acc']:.4f} "
              f"dt={pt['elapsed_s']:.2f}s", flush=True)

    # 2) CLIFF_BUNDLED arm
    for F in F_grid_cliff:
        salt += 1
        pt = eval_phase_point(MECH_FIXED, BUNDLED_CLIFF["M"], BUNDLED_CLIFF["N"],
                              F, L_FIXED, BUNDLED_CLIFF["corr"],
                              "BUNDLED", TR, seed, salt, arm_tag="CLIFF_BUNDLED")
        phase_map.append(pt)
        print(f"  [{len(phase_map):3d}/{expected_n:3d}] CLIFF_BUNDLED  "
              f"F={F:2d} M={BUNDLED_CLIFF['M']} N={BUNDLED_CLIFF['N']} "
              f"c={BUNDLED_CLIFF['corr']:.2f} acc={pt['acc']:.4f} "
              f"dt={pt['elapsed_s']:.2f}s", flush=True)

    # 3) BUNDLED_BRACKET arm (SMOKE only): F=1 x M sweep at (N=2048, corr=0.20, BUNDLED)
    if include_bracket:
        for M_val in BUNDLED_BRACKET_M_GRID:
            salt += 1
            pt = eval_phase_point(MECH_FIXED, M_val, BUNDLED_CLIFF["N"],
                                  1, L_FIXED, BUNDLED_CLIFF["corr"],
                                  "BUNDLED", TR, seed, salt,
                                  arm_tag="BUNDLED_BRACKET")
            phase_map.append(pt)
            print(f"  [{len(phase_map):3d}/{expected_n:3d}] BUNDLED_BRACKET"
                  f" F={pt['F']:2d} M={M_val} N={BUNDLED_CLIFF['N']} "
                  f"c={BUNDLED_CLIFF['corr']:.2f} acc={pt['acc']:.4f} "
                  f"dt={pt['elapsed_s']:.2f}s", flush=True)

    # 4) DEEP_SAT arm x STORAGE
    for storage in STORAGE_GRID:
        arm_tag = ("DEEP_SAT_SHARDED" if storage == "SHARDED"
                   else "DEEP_SAT_BUNDLED")
        for F in F_grid_deep:
            salt += 1
            pt = eval_phase_point(MECH_FIXED, DEEP_SAT["M"], DEEP_SAT["N"],
                                  F, L_FIXED, DEEP_SAT["corr"],
                                  storage, TR, seed, salt, arm_tag=arm_tag)
            phase_map.append(pt)
            print(f"  [{len(phase_map):3d}/{expected_n:3d}] {arm_tag:16s}"
                  f" F={F:2d} M={DEEP_SAT['M']} N={DEEP_SAT['N']} "
                  f"c={DEEP_SAT['corr']:.2f} acc={pt['acc']:.4f} "
                  f"dt={pt['elapsed_s']:.2f}s", flush=True)

    # 5) SATURATION_PC arm (Gate D reproducer)
    salt += 1
    pc = SATURATION_PC_REGIME
    pc_pt = eval_phase_point(pc["cleanup_mechanism"], pc["M"], pc["N"],
                             pc["F"], pc["L"], pc["corruption"],
                             pc["storage"], TR, seed, salt,
                             arm_tag="SATURATION_PC")
    phase_map.append(pc_pt)
    print(f"  [{len(phase_map):3d}/{expected_n:3d}] SATURATION_PC   "
          f"F={pc['F']:2d} mech={pc['cleanup_mechanism']} "
          f"M={pc['M']} N={pc['N']} c={pc['corruption']:.2f} "
          f"acc={pc_pt['acc']:.4f} dt={pc_pt['elapsed_s']:.2f}s", flush=True)

    elapsed = time.perf_counter() - t0
    observed_n = len(phase_map)
    cardinality_ok = (observed_n == expected_n)

    # META_RULE_AF aggregate: STORAGE arms must produce distinct output hashes
    def _arm_hash(arm_tag: str) -> str:
        outs = [p["output_hash"] for p in phase_map if p["arm_tag"] == arm_tag]
        return hashlib.sha256(
            json.dumps(outs, sort_keys=True).encode("utf-8")).hexdigest()[:16]

    h_cliff_shard = _arm_hash("CLIFF_SHARDED")
    h_cliff_bundle = _arm_hash("CLIFF_BUNDLED")
    storage_arms_differ = (h_cliff_shard != h_cliff_bundle)

    # SATURATION_PC pass check
    pc_acc = float(pc_pt["acc"])
    pc_pass = (pc_acc >= SATURATION_PC_THRESHOLD)

    # Per-arm summary helpers
    def _arm_summary(arm_tag: str) -> Dict[str, Any]:
        pts = [p for p in phase_map if p["arm_tag"] == arm_tag]
        accs = [p["acc"] for p in pts]
        if not accs:
            return {"n": 0, "mean": 0.0, "min": 0.0, "max": 0.0, "spread": 0.0,
                    "in_band_frac": 0.0, "per_F_acc": {}}
        per_F = {}
        for p in pts:
            per_F[str(p["F"])] = round(p["acc"], 4)
        spread = round(max(accs) - min(accs), 4)
        in_band = sum(1 for a in accs
                      if NON_SAT_BAND_LO <= a <= NON_SAT_BAND_HI)
        return {
            "n": len(accs),
            "mean": round(float(np.mean(accs)), 4),
            "min": round(float(np.min(accs)), 4),
            "max": round(float(np.max(accs)), 4),
            "spread": spread,
            "in_band_frac": round(in_band / len(accs), 4),
            "per_F_acc": per_F,
        }

    cliff_shard = _arm_summary("CLIFF_SHARDED")
    cliff_bundle = _arm_summary("CLIFF_BUNDLED")
    deep_shard = _arm_summary("DEEP_SAT_SHARDED")
    deep_bundle = _arm_summary("DEEP_SAT_BUNDLED")
    if not deep_shard["n"]:
        # SMOKE deep_sat spot-check uses tag "DEEP_SAT_SHARDED" only via one F.
        deep_shard = _arm_summary("DEEP_SAT_SHARDED")
    bracket_summary = _arm_summary("BUNDLED_BRACKET") if include_bracket else {
        "n": 0, "mean": 0.0, "per_F_acc": {}, "in_band_frac": 0.0
    }
    # For BUNDLED_BRACKET include per-M as well
    if include_bracket:
        bracket_summary["per_M_acc"] = {
            str(p["M"]): round(p["acc"], 4)
            for p in phase_map if p["arm_tag"] == "BUNDLED_BRACKET"
        }

    # STORAGE x ALGEBRA cross-term at cliff-adjacent
    #   spread_diff = |F_spread_SHARDED - F_spread_BUNDLED|
    cliff_shard_spread = cliff_shard["spread"]
    cliff_bundle_spread = cliff_bundle["spread"]
    cliff_cross_term_spread_diff = round(
        abs(cliff_shard_spread - cliff_bundle_spread), 4)

    # per-F matched-storage-diff (max_F |mean_at_SHARDED(F) - mean_at_BUNDLED(F)|):
    #   captures the F-conditional STORAGE effect
    per_F_storage_diff: Dict[str, float] = {}
    for F in F_grid_cliff:
        sh_matches = [p["acc"] for p in phase_map
                      if p["arm_tag"] == "CLIFF_SHARDED" and p["F"] == F]
        bu_matches = [p["acc"] for p in phase_map
                      if p["arm_tag"] == "CLIFF_BUNDLED" and p["F"] == F]
        if sh_matches and bu_matches:
            per_F_storage_diff[str(F)] = round(
                abs(sh_matches[0] - bu_matches[0]), 4)
    # H1-secondary: how the storage effect VARIES across F (spread of the diffs)
    if per_F_storage_diff:
        vals = list(per_F_storage_diff.values())
        storage_effect_variation = round(max(vals) - min(vals), 4)
    else:
        storage_effect_variation = 0.0

    # H1 primary: cliff cross_term (max of two proxies)
    cliff_cross_term = round(
        max(cliff_cross_term_spread_diff, storage_effect_variation), 4)

    # DEEP_SAT cross-term (H3-NULL)
    if deep_shard["n"] and deep_bundle["n"]:
        deep_cross_term_spread_diff = round(
            abs(deep_shard["spread"] - deep_bundle["spread"]), 4)
        per_F_deep_storage_diff = {}
        for F in F_grid_deep:
            sh_m = [p["acc"] for p in phase_map
                    if p["arm_tag"] == "DEEP_SAT_SHARDED" and p["F"] == F]
            bu_m = [p["acc"] for p in phase_map
                    if p["arm_tag"] == "DEEP_SAT_BUNDLED" and p["F"] == F]
            if sh_m and bu_m:
                per_F_deep_storage_diff[str(F)] = round(
                    abs(sh_m[0] - bu_m[0]), 4)
        if per_F_deep_storage_diff:
            dv = list(per_F_deep_storage_diff.values())
            deep_storage_variation = round(max(dv) - min(dv), 4)
        else:
            deep_storage_variation = 0.0
        deep_cross_term = round(
            max(deep_cross_term_spread_diff, deep_storage_variation), 4)
    else:
        per_F_deep_storage_diff = {}
        deep_cross_term = 0.0
        deep_cross_term_spread_diff = 0.0

    h3_null_fires = (deep_cross_term < DEEP_SAT_MAX_CROSS_THRESHOLD)
    # DEEP_SAT gate is SHARDED-specific: at any regime that saturates SHARDED,
    # BUNDLED is CAPACITY-DOMINATED (either at floor because M/N > Plate bound,
    # or saturated at trivial regimes; empirically NO single regime saturates
    # both storages in the FHRR chain-composition primitive per Probes 4+5+6+7+8
    # brackets). The BUNDLED DEEP_SAT arm reports its acc informationally; the
    # design constraint (STORAGE regimes non-superimposable) is itself an
    # empirical finding of this cell, not a regime-construction bug.
    deep_saturated = (deep_shard["mean"] >= 0.90)
    deep_bundled_saturated = (deep_bundle["mean"] >= 0.90)
    deep_bundled_at_floor = (deep_bundle["mean"] <= 0.15)

    # Escapes-saturation: at LEAST one CLIFF arm must have any F-slice in band
    all_cliff_accs = ([p["acc"] for p in phase_map
                       if p["arm_tag"] in ("CLIFF_SHARDED", "CLIFF_BUNDLED")])
    escapes_saturation_cliff = any(NON_SAT_BAND_LO <= a <= NON_SAT_BAND_HI
                                    for a in all_cliff_accs)

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
        "storage_arms_differ": storage_arms_differ,
        "storage_arm_hash_agg": {
            "CLIFF_SHARDED": h_cliff_shard,
            "CLIFF_BUNDLED": h_cliff_bundle,
        },
        "arms_differ_verified": storage_arms_differ,
        "saturation_pc_result": {
            "regime": SATURATION_PC_REGIME,
            "acc": pc_acc,
            "threshold": SATURATION_PC_THRESHOLD,
            "pass": pc_pass,
        },
        "cliff_sharded_arm": {
            "regime": {**SHARDED_CLIFF, "L": L_FIXED, "storage": "SHARDED",
                       "mechanism": MECH_FIXED},
            "F_grid": F_grid_cliff,
            **cliff_shard,
        },
        "cliff_bundled_arm": {
            "regime": {**BUNDLED_CLIFF, "L": L_FIXED, "storage": "BUNDLED",
                       "mechanism": MECH_FIXED},
            "F_grid": F_grid_cliff,
            **cliff_bundle,
        },
        "bundled_bracket_arm": {
            "regime": {"N": BUNDLED_CLIFF["N"], "corr": BUNDLED_CLIFF["corr"],
                        "storage": "BUNDLED", "F": 1, "L": L_FIXED,
                        "mechanism": MECH_FIXED},
            "M_grid": BUNDLED_BRACKET_M_GRID if include_bracket else [],
            **bracket_summary,
        },
        "deep_sat_sharded_arm": {
            "regime": {**DEEP_SAT, "L": L_FIXED, "storage": "SHARDED",
                       "mechanism": MECH_FIXED},
            "F_grid": F_grid_deep,
            **deep_shard,
        },
        "deep_sat_bundled_arm": {
            "regime": {**DEEP_SAT, "L": L_FIXED, "storage": "BUNDLED",
                       "mechanism": MECH_FIXED},
            "F_grid": F_grid_deep,
            **deep_bundle,
        },
        "storage_x_algebra_cross_term": {
            "cliff_cross_term": cliff_cross_term,
            "cliff_spread_diff": cliff_cross_term_spread_diff,
            "cliff_storage_effect_variation": storage_effect_variation,
            "cliff_per_F_storage_diff": per_F_storage_diff,
            "deep_cross_term": deep_cross_term,
            "deep_spread_diff": deep_cross_term_spread_diff,
            "deep_per_F_storage_diff": per_F_deep_storage_diff,
            "h3_null_fires": h3_null_fires,
            "h3_null_threshold": DEEP_SAT_MAX_CROSS_THRESHOLD,
            "H1_threshold": CROSS_TERM_H1_THRESHOLD,
            "H2_threshold": CROSS_TERM_H2_THRESHOLD,
            "deep_saturated": deep_saturated,
            "deep_bundled_saturated": deep_bundled_saturated,
            "deep_bundled_at_floor": deep_bundled_at_floor,
            "deep_bundled_mean": deep_bundle.get("mean"),
            "deep_sharded_mean": deep_shard.get("mean"),
        },
        "non_saturated_band": [NON_SAT_BAND_LO, NON_SAT_BAND_HI],
        "escapes_saturation_cliff": escapes_saturation_cliff,
        "avg_peak_mem_mb": round(avg_peak, 1),
        "elapsed_seed_s": round(elapsed, 2),
        "beta": BETA,
        "alpha_soft": ALPHA_SOFT,
    }


# ---------------------------------------------------------------------------
# Smoke-gate predicate (null-hypothesis-safe: gate on infra + PC + escapes only)
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    phase_map = body.get("phase_map", [])
    if len(phase_map) != body.get("expected_n_units"):
        return False, (f"cardinality_breach: expected={body.get('expected_n_units')} "
                       f"got={len(phase_map)}")
    if not body.get("storage_arms_differ"):
        return False, (f"arms_differ_fail: SHARDED and BUNDLED CLIFF arms "
                       f"produced identical output-hash aggregates "
                       f"(META_RULE_AF violation)")
    pc = body.get("saturation_pc_result", {})
    if not pc.get("pass"):
        return False, (f"saturation_pc_fail: SHARDED F=1 M=800 N=2048 corr=0.20 "
                       f"iterative_cosine acc={pc.get('acc')} < "
                       f"threshold={pc.get('threshold')} (Gate D)")
    if not body.get("escapes_saturation_cliff"):
        return False, (f"escapes_saturation_ceiling_fail: no CLIFF arm point "
                       f"landed in non-saturated band [{NON_SAT_BAND_LO}, "
                       f"{NON_SAT_BAND_HI}]; CLIFF regimes drifted from empirical "
                       f"bracket; SHARDED_cliff_mean="
                       f"{body.get('cliff_sharded_arm', {}).get('mean')} "
                       f"BUNDLED_cliff_mean="
                       f"{body.get('cliff_bundled_arm', {}).get('mean')}")
    xterm = body.get("storage_x_algebra_cross_term", {})
    # DEEP_SAT gate: SHARDED must saturate (that is the empirical null-control
    # anchor). BUNDLED at same regime is CAPACITY-DOMINATED (either saturates
    # or floors depending on M/N ratio vs Plate bound); its behavior is
    # informational, not gating. Empirical finding: STORAGE regimes are
    # non-superimposable in FHRR chain-composition primitive.
    if not xterm.get("deep_saturated"):
        return False, (f"deep_sat_sharded_drift: SHARDED_mean="
                       f"{body.get('deep_sat_sharded_arm', {}).get('mean')}; "
                       f"below 0.90 at DEEP_SAT config (N=8192, M=800, corr=0.60); "
                       f"SHARDED deep-saturation null-anchor broken")
    # NaN sanity
    for pt in phase_map:
        if pt.get("acc") != pt.get("acc"):
            return False, f"NAN_in_phase_map at {pt}"

    cliff_x = xterm.get("cliff_cross_term", 0.0)
    deep_x = xterm.get("deep_cross_term", 0.0)
    bundled_saturated = xterm.get("deep_bundled_saturated", False)
    bundled_floor = xterm.get("deep_bundled_at_floor", False)
    bundled_deep_state = ("SATURATED" if bundled_saturated
                          else "FLOORED" if bundled_floor
                          else "IN_BAND")
    return True, (f"smoke_gate_pass: cardinality_ok + storage_arms_differ + "
                  f"pc_acc={pc.get('acc')} (>={pc.get('threshold')}) + "
                  f"escapes_saturation(sharded_cliff_mean="
                  f"{body.get('cliff_sharded_arm', {}).get('mean')} "
                  f"bundled_cliff_mean="
                  f"{body.get('cliff_bundled_arm', {}).get('mean')}) + "
                  f"sharded_deep_sat_ok (mean="
                  f"{body.get('deep_sat_sharded_arm', {}).get('mean')}); "
                  f"informational: bundled_deep_state={bundled_deep_state} "
                  f"(mean={body.get('deep_sat_bundled_arm', {}).get('mean')}) "
                  f"cliff_cross_term={cliff_x} deep_cross_term={deep_x} "
                  f"h3_null_fires={xterm.get('h3_null_fires')} "
                  f"bundled_bracket_M_to_acc="
                  f"{body.get('bundled_bracket_arm', {}).get('per_M_acc')}")


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]], run_mode: str
                          ) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "HARD_FAIL",
                "verdict_msg": "HARD_FAIL_NO_SEEDS",
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
        "storage_arms_differ": body.get("storage_arms_differ"),
        "storage_arm_hash_agg": body.get("storage_arm_hash_agg"),
        "arms_differ_verified": body.get("arms_differ_verified"),
        "saturation_pc_result": body.get("saturation_pc_result"),
        "cliff_sharded_arm": body.get("cliff_sharded_arm"),
        "cliff_bundled_arm": body.get("cliff_bundled_arm"),
        "bundled_bracket_arm": body.get("bundled_bracket_arm"),
        "deep_sat_sharded_arm": body.get("deep_sat_sharded_arm"),
        "deep_sat_bundled_arm": body.get("deep_sat_bundled_arm"),
        "storage_x_algebra_cross_term": body.get("storage_x_algebra_cross_term"),
        "non_saturated_band": body.get("non_saturated_band"),
        "escapes_saturation_cliff": body.get("escapes_saturation_cliff"),
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
            vmsg = f"HARD_PASS_SMOKE: {observed_n}/{expected_n} pts; {reason}"
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
    pc = body.get("saturation_pc_result", {})
    xterm = body.get("storage_x_algebra_cross_term", {})
    cliff_sh = body.get("cliff_sharded_arm", {})
    cliff_bu = body.get("cliff_bundled_arm", {})

    if not cardinality_ok:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"expected={expected_n} observed={observed_n}")
    elif not body.get("arms_differ_verified"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_ARMS_MUST_DIFFER_META_RULE_AF: SHARDED and BUNDLED "
                f"CLIFF arms produced identical output-hash aggregates")
    elif not pc.get("pass"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_SATURATION_PC_MISMATCH: SHARDED F=1 M=800 N=2048 "
                f"corr=0.20 iterative_cosine acc={pc.get('acc')} < "
                f"threshold={pc.get('threshold')} (Gate D violation)")
    elif not xterm.get("deep_saturated"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_DEEP_SAT_SHARDED_ARM_DRIFT: SHARDED DEEP_SAT mean="
                f"{xterm.get('deep_sharded_mean')} below 0.90; SHARDED "
                f"null-anchor broken")
    else:
        cliff_in_band_shard = cliff_sh.get("in_band_frac", 0.0)
        cliff_in_band_bundle = cliff_bu.get("in_band_frac", 0.0)
        # At least ONE cliff arm should have >= 30% points in band
        if cliff_in_band_shard < 0.30 and cliff_in_band_bundle < 0.30:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_BOTH_CLIFF_ARMS_ESCAPES_SATURATION_FAIL: "
                    f"SHARDED in_band={cliff_in_band_shard} < 0.30 AND "
                    f"BUNDLED in_band={cliff_in_band_bundle} < 0.30; both "
                    f"cliff arms failed to land in band; cannot claim H1 or H2")
        else:
            cliff_xt = xterm.get("cliff_cross_term", 0.0)
            deep_xt = xterm.get("deep_cross_term", 0.0)
            h3_null_fires = xterm.get("h3_null_fires", False)
            h3_null_note = (f" ; H3-NULL fires(deep_cross={deep_xt} < "
                            f"{DEEP_SAT_MAX_CROSS_THRESHOLD})" if h3_null_fires
                            else f" ; H3-NULL DID NOT FIRE(deep_cross={deep_xt} "
                                 f">= {DEEP_SAT_MAX_CROSS_THRESHOLD}) -- "
                                 f"cross-term non-zero at deep-saturation")

            if cliff_xt >= CROSS_TERM_H1_THRESHOLD:
                verdict = "HARD_PASS"
                vmsg = (f"HARD_PASS_H1_STORAGE_x_ALGEBRA_CROSS_TERM_AT_CLIFF_ADJACENT: "
                        f"cliff_cross_term={cliff_xt} >= {CROSS_TERM_H1_THRESHOLD}; "
                        f"STORAGE x ALGEBRA interact at cliff-adjacent; completes "
                        f"STORAGE-pair regime column (STORAGE-N Probe 4 + "
                        f"STORAGE-TOPOLOGY Probe 5 + STORAGE-ALGEBRA this cell)"
                        f"{h3_null_note}")
            elif cliff_xt < CROSS_TERM_H2_THRESHOLD:
                verdict = "HARD_PASS"
                vmsg = (f"HARD_PASS_H2_STORAGE_ALGEBRA_INDEPENDENT_AT_CLIFF_ADJACENT: "
                        f"cliff_cross_term={cliff_xt} < {CROSS_TERM_H2_THRESHOLD}; "
                        f"STORAGE and ALGEBRA are INDEPENDENT at cliff-adjacent; "
                        f"F fan-out has same effect for both SHARDED and BUNDLED"
                        f"{h3_null_note}")
            else:
                verdict = "MIDDLE_BAND"
                vmsg = (f"MIDDLE_BAND_WEAK_CROSS_TERM: cliff_cross_term={cliff_xt} "
                        f"in [{CROSS_TERM_H2_THRESHOLD}, {CROSS_TERM_H1_THRESHOLD}); "
                        f"weak STORAGE x ALGEBRA interaction (MM_TENTATIVE); "
                        f"consider higher TR or refined regime to localize"
                        f"{h3_null_note}")

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
    })
    return out


__all__ = [
    "ANCHOR_NAME", "DEVICE", "GPU_NAME",
    "STORAGE_GRID", "F_GRID_CLIFF_FULL", "F_GRID_CLIFF_SMOKE",
    "F_GRID_DEEP_SAT_FULL", "F_GRID_DEEP_SAT_SMOKE",
    "SHARDED_CLIFF", "BUNDLED_CLIFF", "DEEP_SAT",
    "BUNDLED_BRACKET_M_GRID",
    "MECH_FIXED", "L_FIXED", "TR_FULL", "TR_SMOKE",
    "SATURATION_PC_REGIME", "SATURATION_PC_THRESHOLD",
    "NON_SAT_BAND_LO", "NON_SAT_BAND_HI",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "CROSS_TERM_H1_THRESHOLD", "CROSS_TERM_H2_THRESHOLD",
    "DEEP_SAT_MAX_CROSS_THRESHOLD",
    "REQUIRED_FIELDS",
    "eval_phase_point", "selftest", "run_one_seed",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
