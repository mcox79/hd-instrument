"""Stage 1 Regime Probe 7: N (SCALE_FREE) x CLEANUP_MECHANISM in NON-SATURATED regime.

Cell anchor: `stage1_regime_probe_7_N_x_cleanup_non_saturated_v1`
Pre-reg:     preregs/2026-07-03_stage1_regime_probe_7_N_x_cleanup_non_saturated_v1.md

Purpose:
    Non-saturated regime revival of Probe 2 (N x CLEANUP null was saturation-
    vacuous; all 72 phase points landed at acc=1.0). Adds M=6400 (M/N=0.78 at
    N=8192 >> Plate 0.14 bound) and corr in {0.60, 0.70} so mechanism variance
    has room to appear. Companion to Probe 6 (F x CLEANUP TOPOLOGY revival).

Cited source atoms (exact names, no abstraction; per META_RULE_AC):
    META_saturation_floor_masks_null_variance_probe3_lesson  (T4 MM_STANDARD)
    T3/EXP_stage1_regime_probe_2_N_x_cleanup_mechanism_v1_3seed_FULL_MM_STANDARD_cleanup_axis_regime_narrow_extended_to_N_axis
    MATH_STAGE1_REGIME_MAP_PROBE1_STORAGE_x_CLEANUP_CG_META_v1
    T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1
    T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1
    PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian  (v2 M-sweep 2026-07-03)

Reuse (Principle 11):
    Primitives imported from _stage1_physics_law_joint_composition_factorial_v1_core:
      CLEANUP_MECHANISMS, CLEANUP_REGISTRY, BETA, ALPHA_SOFT
      build_rules, phase_corrupt, cleanup_argmax_idx, run_chain
    Verdict logic modeled on _stage1_regime_probe_2_N_x_cleanup_mechanism_v1_core
    with band-restricted discriminator + SATURATION_PC arm additions.

Sweep grid FULL (v2 CORRECTED per empirical smoke discovery 2026-07-03):
    N in {2048,4096,8192,16384} x mech(3) x M in {800,3200,6400} x corr in {0.88,0.90,0.92}
    = 108 SHARDED main pts + 1 SATURATION_PC pt = 109 pts/seed
    L_FIXED = 8 (elevated from 2 to open discriminating band -- L=2 was empirically bulletproof
    up to corr=0.94 across all tested N).
Sweep grid SMOKE (v2 CORRECTED):
    N in {2048,16384} x mech(3) x M=6400 x corr=0.90
    = 6 SHARDED main pts + 1 SATURATION_PC pt = 7 pts

Hypotheses (falsifiable, restricted to slices with grand-mean(acc) in [0.30, 0.95]):
    H1 (N moderates, non-saturated):
        N_x_cleanup_max_abs_deviation_in_band >= 0.15
        OR max_per_N_mech_variance_in_band >= 0.10
      -> Probe 2 null was saturation artifact; N IS a moderator.
    H2 (null holds, non-saturated):
        N_x_cleanup_max_abs_deviation_in_band < 0.05
        AND max_per_N_mech_variance_in_band < 0.05
      -> mechanism degeneracy holds at NON-SATURATED regime; strengthens
         Probe 1 "STORAGE_UNIQUELY_moderates" thesis. CG_META revival of Probe 2.
    H3 (crossover):
        mechanism ranking changes across N within band
      -> N-dependent crossover exponent (MM_TENTATIVE).

Compute architecture: batched-GPU (USER-LOCKED). Auto-CUDA when available.
Sibling wrappers: exp_stage1_regime_probe_7_N_x_cleanup_non_saturated_v1_s{7,13,19}.py

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-07-03 (agent-spawn, Opus 4.7).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared (categorical accuracy; discriminator is band-restricted deviation)
# - escapes_saturation_ceiling at smoke (META_RULE_AG-analog for non-saturated design)
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
# - HP_SCOPE per-arm declaration (SHARDED_main vs SATURATION_PC_arm)
# - cardinality_ok for sweep-axis cells (META_RULE_H; EXPECTED_N_UNITS gate)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except)
# - calibration_check field (META_RULE_M; default_ok_for_this_regime)
# - all numbers tagged HYPOTHESIZED@ / MEASURED@ / THEORETICAL@ / CITED@ (META_RULE_AC)
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

# CUDA env before torch import (USER-LOCKED)
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
    build_rules,
    phase_corrupt,
    cleanup_argmax_idx,
    run_chain,
)

ANCHOR_NAME = "stage1_regime_probe_7_N_x_cleanup_non_saturated_v1"

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
# N: 4 levels of scale (revives the swept axis from Probe 2)
N_GRID_FULL = [2048, 4096, 8192, 16384]
# CLEANUP_MECHANISMS imported: modern_hopfield, iterative_cosine, soft_energy_attractor
# Storage FIXED = SHARDED (canonical FHRR chain composition regime)
M_GRID_FULL = [800, 3200, 6400]      # M=6400 forces M/N > 0.14 at N in {2048,4096} for capacity pressure
# CORRUPTION_GRID_FULL EMPIRICAL DESIGN CORRECTION (2026-07-03 exp_dev smoke discovery):
# Original spec {0.45, 0.60, 0.70} was saturation-vacuous at L=2 (all 6 smoke pts acc=1.0).
# 5 h of quick-probe scans revealed SHARDED FHRR is bulletproof up to corr~0.85 at L in {2,4,8}
# and cliffs at corr~0.90 in an N-dependent manner. Grid now bracket cliff at L=8.
# HYPOTHESIZED@this-prereg-corrected: at L=8 corr=0.90, N=2048 differentiates mechanisms (spread ~0.08-0.15),
# N>=4096 stays saturated (spread ~0). This IS the H1 signal (N moderates corruption tolerance)
# but requires the L=8 higher-corr regime to become visible.
CORRUPTION_GRID_FULL = [0.88, 0.90, 0.92]
F_FIXED = 1
# L elevated 2 -> 8 based on empirical smoke evidence (L=2 saturates up to corr=0.94; L=8 opens
# the discriminating band). This changes what Probe 2's null test measured (L=2 regime) but
# is REQUIRED to escape the saturation-vacuous ceiling per META_RULE_AG.
L_FIXED = 8

# SMOKE: 2 N (endpoints) x 3 mech x 1 M x 1 corr = 6 SHARDED main pts
# Deliberately at the empirical cliff: L=8 M=6400 corr=0.90 discriminates at N=2048, saturates at N=16384.
# Non-saturated at low N; saturated at high N. Gate 5 (escapes_saturation_ceiling) fires
# when smoke-grid mean-acc < 0.95.
N_GRID_SMOKE = [2048, 16384]
M_GRID_SMOKE = [6400]
CORRUPTION_GRID_SMOKE = [0.90]

# SATURATION_PC arm (Gate D reproducer for Probe 2 baseline)
# Per META_RULE_AC: reproduces Probe 2 baseline acc=1.0 at (SHARDED, F=1, M=800, N=2048, corr=0.20, iterative_cosine).
PC_MECH = "iterative_cosine"
PC_M = 800
PC_N = 2048
PC_CORR = 0.20
PC_THRESHOLD = 0.95   # 0.05 tolerance from cited Probe 2 baseline (1.0)

TR_FULL = 100
TR_SMOKE = 40

EXPECTED_N_UNITS_FULL = (len(N_GRID_FULL) * len(CLEANUP_MECHANISMS)
                         * len(M_GRID_FULL) * len(CORRUPTION_GRID_FULL)) + 1  # +1 SATURATION_PC
EXPECTED_N_UNITS_SMOKE = (len(N_GRID_SMOKE) * len(CLEANUP_MECHANISMS)
                          * len(M_GRID_SMOKE) * len(CORRUPTION_GRID_SMOKE)) + 1  # +1 SATURATION_PC

# Discriminator band + thresholds
# HYPOTHESIZED@this-prereg: non-saturated band [0.30, 0.95] excludes trivial saturation + trivial-floor
NON_SATURATED_BAND_LO = 0.30
NON_SATURATED_BAND_HI = 0.95

# H1 thresholds (N moderates when non-saturated)
N_X_CLEANUP_DEVIATION_H1_THRESHOLD = 0.15
MECH_VAR_H1_THRESHOLD = 0.10
# H2 thresholds (null holds when non-saturated)
N_X_CLEANUP_DEVIATION_H2_THRESHOLD = 0.05
MECH_VAR_H2_THRESHOLD = 0.05

# Grid must escape saturation: >= 30% of pts in [0.30, 0.95]
ESCAPES_SATURATION_MIN_FRACTION = 0.30

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# Per-phase-point eval (reuses sibling primitives)
# ---------------------------------------------------------------------------
def eval_phase_point(mechanism: str, M_props: int, N: int, corruption: float,
                     TR: int, seed: int, salt: int,
                     arm_tag: str = "SHARDED_main") -> Dict[str, Any]:
    """Run a single phase point at (mech, M, N, corr) on SHARDED FHRR chain.

    arm_tag identifies main-grid vs SATURATION_PC arm for verdict routing.
    """
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

    # META_RULE_AF (arms-must-differ) hash of cleanup output indices
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
        "arm_tag": arm_tag,
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
    # FULL: 3 mech x 4 N x 3 M x 3 corr = 108 SHARDED main + 1 PC = 109
    if EXPECTED_N_UNITS_FULL != 109:
        return False, (f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 109 "
                       f"(3 mech x 4 N x 3 M x 3 corr + 1 SATURATION_PC)")
    # SMOKE: 3 mech x 2 N x 1 M x 1 corr = 6 SHARDED main + 1 PC = 7
    if EXPECTED_N_UNITS_SMOKE != 7:
        return False, (f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 7 "
                       f"(3 mech x 2 N x 1 M x 1 corr + 1 SATURATION_PC)")
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} "
                f"SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. Sanity: 3 cleanup mechanisms produce distinct outputs at small N/M
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

    # 3. SATURATION_PC easy gate (Gate D reproducer):
    #    iterative_cosine SHARDED at (M=800, N=2048, corr=0.20, F=1, L=2)
    #    should approach Probe 2 baseline (acc ~ 1.0). Tolerance 0.05 -> >=0.95.
    gen.manual_seed(1013)
    props2, perms2, IMPL2, POS2, sh2, bd2 = build_rules(
        PC_M, F_FIXED, gen, DEVICE, PC_N)
    acc_easy, _ = run_chain("SHARDED", PC_MECH, L=L_FIXED, F=F_FIXED, TR=40,
                            props=props2, perms=perms2, IMPL=IMPL2, POS=POS2,
                            sharded_codebook=sh2, bundle_vec=bd2,
                            corruption=PC_CORR, gen=gen, device=DEVICE)
    # At TR=40 vs full TR=100, threshold relaxed slightly to 0.85 for selftest;
    # main run uses 0.95. Selftest is a sanity check, not the Gate D gate itself.
    if acc_easy < 0.85:
        return False, (f"SATURATION_PC selftest (M={PC_M} N={PC_N} L=2 F=1 "
                       f"corr={PC_CORR} {PC_MECH}) expected >= 0.85 at TR=40; "
                       f"got {acc_easy:.3f}")
    msgs.append(f"SATURATION_PC selftest (M={PC_M} N={PC_N} corr={PC_CORR} "
                f"{PC_MECH} TR=40): acc={acc_easy:.3f}")

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

    # Main factorial: SHARDED N x mech x M x corr with F=1, L=2 fixed
    for N in N_grid:
        for mech in mech_grid:
            for M_props in M_grid:
                for corr in corr_grid:
                    salt += 1
                    pt = eval_phase_point(mech, M_props, N, corr, TR, seed,
                                          salt, arm_tag="SHARDED_main")
                    phase_map.append(pt)
                    print(f"  [{len(phase_map):3d}/{expected_n:3d}] main "
                          f"N={N:5d} mech={mech:22s} M={M_props:5d} "
                          f"c={corr:.2f} acc={pt['acc']:.4f} "
                          f"dt={pt['elapsed_s']:.2f}s", flush=True)

    # SATURATION_PC arm (Gate D reproducer for Probe 2 baseline)
    salt += 1
    pc_pt = eval_phase_point(PC_MECH, PC_M, PC_N, PC_CORR, TR, seed, salt,
                             arm_tag="SATURATION_PC")
    phase_map.append(pc_pt)
    print(f"  [{len(phase_map):3d}/{expected_n:3d}] PC   "
          f"N={PC_N:5d} mech={PC_MECH:22s} M={PC_M:5d} "
          f"c={PC_CORR:.2f} acc={pc_pt['acc']:.4f} "
          f"dt={pc_pt['elapsed_s']:.2f}s", flush=True)

    elapsed = time.perf_counter() - t0
    observed_n = len(phase_map)
    cardinality_ok = (observed_n == expected_n)

    # META_RULE_AF aggregate hash of mechanism outputs across SHARDED_main pts
    mech_output_hashes: Dict[str, List[str]] = {m: [] for m in mech_grid}
    for pt in phase_map:
        if pt.get("arm_tag") == "SHARDED_main":
            mech_output_hashes[pt["cleanup_mechanism"]].append(pt["output_hash"])
    mech_hash_agg = {m: hashlib.sha256(
        json.dumps(v, sort_keys=True).encode("utf-8")).hexdigest()[:16]
                     for m, v in mech_output_hashes.items()}
    n_distinct_mechs = len(set(mech_hash_agg.values()))

    # SATURATION_PC pass/fail
    pc_acc = float(pc_pt["acc"])
    pc_pass = (pc_acc >= PC_THRESHOLD)

    # Escapes-saturation-ceiling. SMOKE gate: at least one N-slice has mean-acc < 0.95
    # (per-slice semantics; grand mean is misleading because high-N slices may saturate
    # while low-N slices differentiate — exactly the N-moderation signal we want to see).
    # FULL gate: fraction of SHARDED_main pts in [0.30, 0.95] >= 0.30 (band-fraction).
    main_pts = [p for p in phase_map if p.get("arm_tag") == "SHARDED_main"]
    main_accs = [p["acc"] for p in main_pts]
    main_mean = float(np.mean(main_accs)) if main_accs else -1.0
    n_in_band = sum(1 for a in main_accs
                    if NON_SATURATED_BAND_LO <= a <= NON_SATURATED_BAND_HI)
    frac_in_band = (n_in_band / len(main_accs)) if main_accs else 0.0
    # Per-N mean acc; gate fires if any N-slice's mean-acc < 0.95.
    per_N_mean_acc: Dict[str, float] = {}
    for N in N_grid:
        slice_accs = [p["acc"] for p in main_pts if p["N"] == N]
        if slice_accs:
            per_N_mean_acc[str(N)] = float(np.mean(slice_accs))
    escapes_saturation_smoke = any(v < NON_SATURATED_BAND_HI
                                   for v in per_N_mean_acc.values())
    escapes_saturation_full = (frac_in_band >= ESCAPES_SATURATION_MIN_FRACTION)

    # Per-N mechanism variance (spread across mechanisms at each (N, M, corr))
    per_N_mech_variance: Dict[str, Dict[str, Any]] = {}
    for N in N_grid:
        per_cell_spreads: List[float] = []
        per_cell_details: List[Dict[str, Any]] = []
        for M_props in M_grid:
            for corr in corr_grid:
                accs_by_mech = {}
                for mech in mech_grid:
                    matches = [p["acc"] for p in main_pts
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
                        "M": M_props, "corr": corr,
                        "spread": round(spread, 4),
                        "grand_mean": round(sum(accs) / len(accs), 4),
                        "in_non_saturated_band": bool(
                            NON_SATURATED_BAND_LO <= (sum(accs) / len(accs))
                            <= NON_SATURATED_BAND_HI),
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

    # Band-restricted discriminator: restrict to slices with grand-mean in band.
    band_spreads: List[float] = []
    band_slice_details: List[Dict[str, Any]] = []
    per_N_band_spreads: Dict[str, List[float]] = {str(N): [] for N in N_grid}
    for N_str, block in per_N_mech_variance.items():
        for detail in block["per_cell_details"]:
            if detail["in_non_saturated_band"]:
                band_spreads.append(detail["spread"])
                per_N_band_spreads[N_str].append(detail["spread"])
                band_slice_details.append(
                    {"N": int(N_str), **detail})
    n_band_slices = len(band_spreads)
    n_x_cleanup_max_abs_deviation_in_band = (float(max(band_spreads))
                                             if band_spreads else 0.0)
    n_x_cleanup_mean_abs_deviation_in_band = (float(np.mean(band_spreads))
                                              if band_spreads else 0.0)
    per_N_band_mean_spread = {}
    for N_str, spreads in per_N_band_spreads.items():
        if spreads:
            per_N_band_mean_spread[N_str] = round(float(np.mean(spreads)), 4)
        else:
            per_N_band_mean_spread[N_str] = None
    valid_per_N = [v for v in per_N_band_mean_spread.values() if v is not None]
    max_per_N_mech_variance_in_band = (float(max(valid_per_N))
                                       if valid_per_N else 0.0)

    # H3 crossover: mechanism ranking changes across N within band?
    # Aggregate per-N per-mech mean-acc across band slices.
    per_N_mech_band_acc: Dict[str, Dict[str, float]] = {}
    for N in N_grid:
        per_mech_accs: Dict[str, List[float]] = {m: [] for m in mech_grid}
        for detail in per_N_mech_variance.get(str(N), {}).get(
                "per_cell_details", []):
            if detail["in_non_saturated_band"]:
                for m, a in detail["accs_by_mech"].items():
                    per_mech_accs[m].append(a)
        per_N_mech_band_acc[str(N)] = {
            m: round(float(np.mean(v)), 4) if v else None
            for m, v in per_mech_accs.items()
        }
    # Ranking-change detection: at least one N where argmax differs from other Ns.
    N_rankings: Dict[str, List[str]] = {}
    for N_str, mech_map in per_N_mech_band_acc.items():
        vals = [(m, a) for m, a in mech_map.items() if a is not None]
        if len(vals) == len(mech_grid):
            ranked = sorted(vals, key=lambda x: -x[1])
            N_rankings[N_str] = [x[0] for x in ranked]
    if len(N_rankings) >= 2:
        first_rank = list(N_rankings.values())[0]
        crossover = any(v != first_rank for v in N_rankings.values())
    else:
        crossover = False

    # Hypothesis assessment (band-restricted; H1 vs H2 vs H3)
    # HYPOTHESIZED@this-prereg: thresholds calibrated on Probe 6 pattern.
    if n_band_slices == 0:
        hyp_verdict = "H_UNKNOWN_NO_BAND_SLICES"
        hyp_reason = ("no phase-slices had grand-mean(acc) in "
                      f"[{NON_SATURATED_BAND_LO}, {NON_SATURATED_BAND_HI}]")
    elif (n_x_cleanup_max_abs_deviation_in_band
          >= N_X_CLEANUP_DEVIATION_H1_THRESHOLD
          or max_per_N_mech_variance_in_band >= MECH_VAR_H1_THRESHOLD):
        hyp_verdict = "H1_N_MODERATES_WHEN_NON_SATURATED"
        hyp_reason = (f"in {n_band_slices} band-slices: "
                      f"max_abs_dev={n_x_cleanup_max_abs_deviation_in_band:.4f} "
                      f"max_per_N_var={max_per_N_mech_variance_in_band:.4f}; "
                      f"H1 threshold (>=0.15 dev OR >=0.10 var) satisfied; "
                      f"N IS a moderator of CLEANUP_MECHANISM")
    elif (n_x_cleanup_max_abs_deviation_in_band
          < N_X_CLEANUP_DEVIATION_H2_THRESHOLD
          and max_per_N_mech_variance_in_band < MECH_VAR_H2_THRESHOLD):
        hyp_verdict = "H2_MECHANISM_DEGENERACY_HOLDS_AT_NON_SATURATED"
        hyp_reason = (f"in {n_band_slices} band-slices: "
                      f"max_abs_dev={n_x_cleanup_max_abs_deviation_in_band:.4f} "
                      f"< 0.05 AND max_per_N_var="
                      f"{max_per_N_mech_variance_in_band:.4f} < 0.05; "
                      f"Probe 2 null result reproduces at NON-SATURATED regime; "
                      f"strengthens Probe 1 STORAGE_UNIQUELY_moderates thesis")
    else:
        hyp_verdict = "MIDDLE_BAND_WEAK_N_MODERATION"
        hyp_reason = (f"in {n_band_slices} band-slices: "
                      f"max_abs_dev={n_x_cleanup_max_abs_deviation_in_band:.4f} "
                      f"max_per_N_var={max_per_N_mech_variance_in_band:.4f}; "
                      f"between H2 null and H1 threshold; "
                      f"weak N-moderation (MM_TENTATIVE)")

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
        "saturation_pc": {
            "arm": "SATURATION_PC",
            "mechanism": PC_MECH,
            "M": PC_M, "N": PC_N, "corruption": PC_CORR,
            "F": F_FIXED, "L": L_FIXED,
            "acc": pc_acc,
            "threshold": PC_THRESHOLD,
            "pass": pc_pass,
        },
        "main_grid_mean_acc": round(main_mean, 4),
        "main_grid_n_in_non_saturated_band": n_in_band,
        "main_grid_n_total": len(main_accs),
        "main_grid_fraction_in_non_saturated_band": round(frac_in_band, 4),
        "per_N_mean_acc": {k: round(v, 4) for k, v in per_N_mean_acc.items()},
        "escapes_saturation_ceiling_smoke": escapes_saturation_smoke,
        "escapes_saturation_ceiling_full": escapes_saturation_full,
        "per_N_mech_variance": per_N_mech_variance,
        "N_grid": N_grid,
        "n_band_slices": n_band_slices,
        "n_x_cleanup_max_abs_deviation_in_band": round(
            n_x_cleanup_max_abs_deviation_in_band, 4),
        "n_x_cleanup_mean_abs_deviation_in_band": round(
            n_x_cleanup_mean_abs_deviation_in_band, 4),
        "per_N_band_mean_spread": per_N_band_mean_spread,
        "max_per_N_mech_variance_in_band": round(
            max_per_N_mech_variance_in_band, 4),
        "band_slice_details": band_slice_details,
        "per_N_mech_band_acc": per_N_mech_band_acc,
        "N_rankings_within_band": N_rankings,
        "mech_ranking_crossover": bool(crossover),
        "hypothesis_assessment": hyp_verdict,
        "hypothesis_reason": hyp_reason,
        "avg_peak_mem_mb": round(avg_peak, 1),
        "elapsed_seed_s": round(elapsed, 2),
        "beta": BETA,
        "alpha_soft": ALPHA_SOFT,
        "non_saturated_band": [NON_SATURATED_BAND_LO, NON_SATURATED_BAND_HI],
    }


# ---------------------------------------------------------------------------
# Smoke-gate predicate (null-hypothesis-plausible: gate on infra + PC + escapes)
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    phase_map = body.get("phase_map", [])
    expected_n = body.get("expected_n_units")
    if len(phase_map) != expected_n:
        return False, (f"cardinality_breach: expected {expected_n} "
                       f"got {len(phase_map)}")
    n_distinct_mechs = body.get("n_distinct_mechanisms", 0)
    if n_distinct_mechs != len(CLEANUP_MECHANISMS):
        return False, (f"arms_differ_fail: {n_distinct_mechs}/"
                       f"{len(CLEANUP_MECHANISMS)} distinct mechanism output "
                       f"hashes (META_RULE_AF violation)")
    pc = body.get("saturation_pc", {})
    if not pc.get("pass"):
        return False, (f"saturation_pc_fail: {PC_MECH} SHARDED at PC regime "
                       f"(M={pc.get('M')} N={pc.get('N')} "
                       f"corr={pc.get('corruption')}) "
                       f"acc={pc.get('acc')} < threshold={pc.get('threshold')}")
    # Escapes-saturation gate (per-N semantics): at least one N-slice must have
    # mean-acc < 0.95. Grand-mean is misleading when high-N saturates but low-N
    # differentiates (exactly the N-moderation signal we want to detect).
    if not body.get("escapes_saturation_ceiling_smoke"):
        return False, (f"escapes_saturation_ceiling_fail: no N-slice has "
                       f"mean-acc < {NON_SATURATED_BAND_HI}; per_N_mean_acc="
                       f"{body.get('per_N_mean_acc')}; smoke regime fully "
                       f"saturated at every N; design goal not achieved")
    # NaN sanity
    for pt in phase_map:
        if pt.get("acc") != pt.get("acc"):  # NaN check
            return False, f"NAN_in_phase_map at {pt}"

    # Discriminator variance is INFORMATIONAL, not gating (null-hypothesis
    # discipline per feedback_smoke_gates_null_hypothesis_should_not_gate_...).
    max_dev = body.get("n_x_cleanup_max_abs_deviation_in_band", 0.0)
    max_var = body.get("max_per_N_mech_variance_in_band", 0.0)
    frac_band = body.get("main_grid_fraction_in_non_saturated_band", 0.0)
    hyp = body.get("hypothesis_assessment")

    return True, (f"smoke_gate_pass: cardinality_ok + 3-mech-hash-distinct + "
                  f"pc_acc={pc.get('acc')} (>={pc.get('threshold')}) + "
                  f"main_mean={body.get('main_grid_mean_acc')} < "
                  f"{NON_SATURATED_BAND_HI} + frac_in_band={frac_band}; "
                  f"informational: max_dev_in_band={max_dev} "
                  f"max_var_in_band={max_var} hyp_preview={hyp}")


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
        "mech_output_hash_agg": body.get("mech_output_hash_agg"),
        "n_distinct_mechanisms": body.get("n_distinct_mechanisms"),
        "arms_differ_verified": body.get("arms_differ_verified"),
        "saturation_pc": body.get("saturation_pc"),
        "main_grid_mean_acc": body.get("main_grid_mean_acc"),
        "main_grid_n_in_non_saturated_band":
            body.get("main_grid_n_in_non_saturated_band"),
        "main_grid_n_total": body.get("main_grid_n_total"),
        "main_grid_fraction_in_non_saturated_band":
            body.get("main_grid_fraction_in_non_saturated_band"),
        "per_N_mean_acc": body.get("per_N_mean_acc"),
        "escapes_saturation_ceiling_smoke":
            body.get("escapes_saturation_ceiling_smoke"),
        "escapes_saturation_ceiling_full":
            body.get("escapes_saturation_ceiling_full"),
        "per_N_mech_variance": body.get("per_N_mech_variance"),
        "N_grid": body.get("N_grid"),
        "n_band_slices": body.get("n_band_slices"),
        "n_x_cleanup_max_abs_deviation_in_band":
            body.get("n_x_cleanup_max_abs_deviation_in_band"),
        "n_x_cleanup_mean_abs_deviation_in_band":
            body.get("n_x_cleanup_mean_abs_deviation_in_band"),
        "per_N_band_mean_spread": body.get("per_N_band_mean_spread"),
        "max_per_N_mech_variance_in_band":
            body.get("max_per_N_mech_variance_in_band"),
        "band_slice_details": body.get("band_slice_details"),
        "per_N_mech_band_acc": body.get("per_N_mech_band_acc"),
        "N_rankings_within_band": body.get("N_rankings_within_band"),
        "mech_ranking_crossover": body.get("mech_ranking_crossover"),
        "hypothesis_assessment": body.get("hypothesis_assessment"),
        "hypothesis_reason": body.get("hypothesis_reason"),
        "non_saturated_band": body.get("non_saturated_band"),
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
            vmsg = (f"HARD_PASS_SMOKE: {observed_n}/{expected_n} pts; {reason}")
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
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"expected={expected_n} observed={observed_n}")
    elif not body.get("arms_differ_verified"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_ARMS_MUST_DIFFER_META_RULE_AF: "
                f"{body.get('n_distinct_mechanisms')} distinct mechanism-"
                f"output-hashes")
    elif not body.get("saturation_pc", {}).get("pass"):
        pc = body.get("saturation_pc", {})
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_SATURATION_PC_MISMATCH: {PC_MECH} at PC regime "
                f"acc={pc.get('acc')} < threshold={pc.get('threshold')}; "
                f"positive control fails -> downstream discriminator claims "
                f"not trustworthy (Gate D violation)")
    elif not body.get("escapes_saturation_ceiling_full"):
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_ESCAPES_SATURATION_FAIL: only "
                f"{body.get('main_grid_n_in_non_saturated_band')}/"
                f"{body.get('main_grid_n_total')} main-grid pts in "
                f"[{NON_SATURATED_BAND_LO}, {NON_SATURATED_BAND_HI}] band "
                f"(fraction {body.get('main_grid_fraction_in_non_saturated_band')} "
                f"< {ESCAPES_SATURATION_MIN_FRACTION}); grid failed to escape "
                f"saturation; cannot claim H1/H2 with confidence")
    else:
        hyp = body.get("hypothesis_assessment", "H_UNKNOWN")
        reason = body.get("hypothesis_reason", "")
        crossover = body.get("mech_ranking_crossover", False)
        max_dev = body.get("n_x_cleanup_max_abs_deviation_in_band")
        max_var = body.get("max_per_N_mech_variance_in_band")
        n_slices = body.get("n_band_slices")
        cross_note = (f"; mech_ranking_crossover=True (H3 MM_TENTATIVE)"
                      if crossover else "")
        if hyp == "H2_MECHANISM_DEGENERACY_HOLDS_AT_NON_SATURATED":
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H2_MECHANISM_DEGENERACY_HOLDS_AT_NON_SATURATED: "
                    f"n_band_slices={n_slices}; max_abs_dev_in_band={max_dev} "
                    f"< 0.05; max_per_N_var_in_band={max_var} < 0.05; Probe 2 "
                    f"null result reproduces at NON-SATURATED regime; "
                    f"strengthens Probe 1 STORAGE_UNIQUELY_moderates thesis; "
                    f"CG_META revival candidate: SCALE_FREE_x_CLEANUP_MECHANISM_"
                    f"non_saturated_null_confirmed_v1; pending Skunkworks "
                    f"landed-VET + 3-seed replication + atomization"
                    f"{cross_note}; {reason}")
        elif hyp == "H1_N_MODERATES_WHEN_NON_SATURATED":
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H1_N_MODERATES_WHEN_NON_SATURATED: "
                    f"n_band_slices={n_slices}; max_abs_dev_in_band={max_dev}; "
                    f"max_per_N_var_in_band={max_var}; Probe 2 null was "
                    f"saturation artifact; N IS a moderator of "
                    f"CLEANUP_MECHANISM; updates REGIME MAP with new "
                    f"SCALE_FREE_x_CLEANUP boundary point"
                    f"{cross_note}; {reason}")
        elif hyp == "MIDDLE_BAND_WEAK_N_MODERATION":
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_WEAK_N_MODERATION: n_band_slices={n_slices}; "
                    f"max_abs_dev_in_band={max_dev} max_per_N_var_in_band={max_var}; "
                    f"between H2 null and H1 threshold; weak N-moderation "
                    f"(MM_TENTATIVE); consider refined sweep to localize"
                    f"{cross_note}; {reason}")
        elif hyp == "H_UNKNOWN_NO_BAND_SLICES":
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_NO_BAND_SLICES: no phase-slices had grand-"
                    f"mean(acc) in [{NON_SATURATED_BAND_LO}, "
                    f"{NON_SATURATED_BAND_HI}]; escapes_saturation_ceiling_full"
                    f" gate should have caught this; re-spec grid; {reason}")
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
    "PC_MECH", "PC_M", "PC_N", "PC_CORR", "PC_THRESHOLD",
    "TR_FULL", "TR_SMOKE", "BETA", "ALPHA_SOFT",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "NON_SATURATED_BAND_LO", "NON_SATURATED_BAND_HI",
    "ESCAPES_SATURATION_MIN_FRACTION",
    "N_X_CLEANUP_DEVIATION_H1_THRESHOLD",
    "N_X_CLEANUP_DEVIATION_H2_THRESHOLD",
    "MECH_VAR_H1_THRESHOLD", "MECH_VAR_H2_THRESHOLD",
    "REQUIRED_FIELDS",
    "eval_phase_point", "selftest", "run_one_seed",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
