"""Stage 1 Regime Probe 9: N (SCALE) x TOPOLOGY (F fan-out) at cliff-adjacent regime.

Cell anchor: `stage1_regime_probe_9_N_x_topology_non_saturated_v1`
Pre-reg:     preregs/2026-07-03_stage1_regime_probe_9_N_x_topology_non_saturated_v1.md

Purpose:
    Ninth probe in the Stage 1 Regime Map arc. First NON-MECHANISM axis pair
    on the revised regime map. Prior probes (2,3,6,7) held N or F while
    varying CLEANUP_MECHANISM; probes 4,5 pair STORAGE with N/F. N x F virgin.

    Tests: at cliff-adjacent regime, are there cross-terms between the two
    non-mechanism axes themselves? Does N moderate the effect of TOPOLOGY on
    capacity (or vice versa)? MECHANISM is held constant = modern_hopfield
    (best-performer per Probe 6 v2 at F=1) to isolate the N x F interaction.

Hypotheses (falsifiable, restricted to slices with grand-mean(acc) in [0.30, 0.95]):
    H1 (N x TOPOLOGY cross-term):
        topology_var_at_N (max acc-spread across F values at a given N) >= 0.10
        OR N_var_at_F (max acc-spread across N values at a given F) >= 0.10
        OR N_x_F_max_abs_deviation_in_band >= 0.10
      -> N and TOPOLOGY have joint (non-additive) effect at cliff-adjacent regime.

    H2 (null: N and TOPOLOGY are INDEPENDENT):
        topology_var_at_N < 0.05 AND N_var_at_F < 0.05
        AND N_x_F_max_abs_deviation_in_band < 0.05
      -> Each axis has same marginal effect regardless of the other.
         Strengthens regime map "axes are largely independent above/at cliff".

    H3 (deep-saturation null control):
        at CEILING regime (N=8192, corr=0.60), topology_var_across_F < 0.03
      -> at ceiling, no cross-term visible (expected; positive-null-control).

Cited source atoms (exact names, no abstraction; per META_RULE_AC):
    META_saturation_floor_masks_null_variance_probe3_lesson (T4 MM_STANDARD 2026-07-03)
    MATH_STAGE1_REGIME_MAP_PROBE1_STORAGE_x_CLEANUP_CG_META_v1 (Probe 1 template)
    T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1
    T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1
    regime_probe_6_topology_x_cleanup_non_saturated_v1 (F=modern_hopfield F=1 best)
    PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian
    feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03
    feedback_plate_bound_too_pessimistic_for_sharded_fhrr_chain_composition_2026-07-03

Reuse (Principle 11):
    Primitives imported from _stage1_physics_law_joint_composition_factorial_v1_core:
      CLEANUP_MECHANISMS, CLEANUP_REGISTRY, BETA, ALPHA_SOFT, DEVICE, GPU_NAME
      build_rules, phase_corrupt, cleanup_argmax_idx, run_chain, cphasor_torch

Sweep grid FULL:
    N in {256, 512, 1024, 2048} x F in {1, 4, 8, 16}
    = 16 SHARDED main pts + 1 SATURATION_PC + 4 CEILING_H3 = 21 pts/seed
Sweep grid SMOKE:
    N in {256, 2048} x F in {1, 16}
    = 4 SHARDED main pts + 1 SATURATION_PC = 5 pts

Fixed:
    MECHANISM = modern_hopfield
    STORAGE   = SHARDED
    M         = 6400
    L         = 4      (mid-band chain depth per Director spec)
    corr      = 0.85   (cliff-adjacent per Director spec)

Compute architecture: batched-GPU (USER-LOCKED). Auto-CUDA when available; CPU fallback.
STORAGE STRATEGY: SHARDED (compositional cell; META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW).

Sibling wrappers: exp_stage1_regime_probe_9_N_x_topology_non_saturated_v1_s{7,13,19}.py

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-07-03 (agent-spawn, Opus 4.7). USER-directed arc.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; F-axis endpoints hash-distinct)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared (categorical accuracy; discriminator is band-restricted spread)
# - escapes_saturation_ceiling at smoke (META_RULE_AG-analog for non-saturated design)
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
# - HP_SCOPE per-arm declaration (SHARDED_main vs SATURATION_PC vs CEILING_H3)
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

ANCHOR_NAME = "stage1_regime_probe_9_N_x_topology_non_saturated_v1"

# ---------------------------------------------------------------------------
# Sweep constants (LOCKED at module init)
# ---------------------------------------------------------------------------
# N axis (SCALE): 4 levels spanning below and above the empirical cliff.
# HYPOTHESIZED@this-prereg: at (SHARDED, modern_hopfield, M=6400, L=4, corr=0.85),
# N=256 sits near the cliff (few voting dims), N=2048 is above the cliff.
# Cliff-adjacent means at least one N-slice should have per-cell-mean acc in
# non-saturated band; verified in smoke by escapes_saturation_ceiling gate.
N_GRID_FULL = [256, 512, 1024, 2048]
N_GRID_SMOKE = [256, 2048]

# TOPOLOGY axis (F fan-out in the sharded DAG). Matches Probe 6 F grid.
F_GRID_FULL = [1, 4, 8, 16]
F_GRID_SMOKE = [1, 16]

# Fixed regime (per Director spec)
MECH_FIXED = "modern_hopfield"
STORAGE_FIXED = "SHARDED"
M_FIXED = 6400
L_FIXED = 4
CORRUPTION_FIXED = 0.85

# TR (queries per point)
TR_FULL = 100
TR_SMOKE = 40

# SATURATION_PC arm (Gate D reproducer): modern_hopfield SHARDED at trivial-easy
# regime should reproduce prior chain-grade baseline acc ~ 1.0.
# HYPOTHESIZED@this-prereg: at (SHARDED, modern_hopfield, F=1, M=800, N=2048,
# L=4, corr=0.20), acc >= 0.95 per Probe 6/7 baseline pattern.
PC_MECH = MECH_FIXED
PC_M = 800
PC_N = 2048
PC_F = 1
PC_CORR = 0.20
PC_THRESHOLD = 0.95

# CEILING_H3 arm (deep-saturation null control): at (SHARDED, modern_hopfield,
# M=6400, N=8192, L=4, corr=0.60), across F in {1,4,8,16} we expect
# topology_var_across_F < 0.03 (all F-values saturate at acc >= 0.95).
# HYPOTHESIZED@this-prereg: at ceiling, TOPOLOGY axis has no measurable effect.
CEILING_N = 8192
CEILING_CORR = 0.60
CEILING_F_GRID = [1, 4, 8, 16]
CEILING_TOPOLOGY_VAR_MAX = 0.03  # H3 threshold (topology_var must be BELOW this)

# Cardinality: 4 N x 4 F = 16 main + 1 PC + 4 CEILING = 21 FULL / seed
EXPECTED_N_UNITS_FULL = (len(N_GRID_FULL) * len(F_GRID_FULL)) + 1 + len(CEILING_F_GRID)
# SMOKE: 2 N x 2 F = 4 main + 1 PC = 5 (CEILING skipped in smoke to keep wall time down)
EXPECTED_N_UNITS_SMOKE = (len(N_GRID_SMOKE) * len(F_GRID_SMOKE)) + 1

# Discriminator band + thresholds
NON_SATURATED_BAND_LO = 0.30
NON_SATURATED_BAND_HI = 0.95

# H1 thresholds (cliff-adjacent shows N x F cross-term)
TOPOLOGY_VAR_H1_THRESHOLD = 0.10   # max across-F acc-spread at any N in band
N_VAR_H1_THRESHOLD = 0.10          # max across-N acc-spread at any F in band
N_X_F_DEV_H1_THRESHOLD = 0.10      # max_abs deviation from additive at any (N,F)

# H2 thresholds (null: axes independent)
TOPOLOGY_VAR_H2_THRESHOLD = 0.05
N_VAR_H2_THRESHOLD = 0.05
N_X_F_DEV_H2_THRESHOLD = 0.05

# Grid must escape saturation: >= 30% of pts in [0.30, 0.95]
ESCAPES_SATURATION_MIN_FRACTION = 0.30

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# Per-phase-point eval
# ---------------------------------------------------------------------------
def eval_phase_point(mechanism: str, M_props: int, N: int, F: int, L: int,
                     corruption: float, storage: str, TR: int,
                     seed: int, salt: int,
                     arm_tag: str = "SHARDED_main") -> Dict[str, Any]:
    """Run a single phase point at (mech, M, N, F, L, corr) on SHARDED FHRR chain."""
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
                              sharded_codebook, bundle_vec, corruption,
                              gen, device)

    ci_bytes = final_ci.detach().cpu().numpy().tobytes()
    shard_bytes = sharded_codebook.detach().cpu().numpy().tobytes()
    output_hash = hashlib.sha256(ci_bytes).hexdigest()[:16]
    shard_hash = hashlib.sha256(shard_bytes).hexdigest()[:16]

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
        "peak_mem_mb": peak_mem_mb,
        "elapsed_s": round(elapsed, 3),
    }


# ---------------------------------------------------------------------------
# Selftest (formula check at reduced grid; wall < 60s target on CPU)
# ---------------------------------------------------------------------------
def selftest() -> Tuple[bool, str]:
    msgs = []

    # 1. Cardinality math: FULL 16 main + 1 PC + 4 CEILING = 21; SMOKE 4 + 1 = 5
    if EXPECTED_N_UNITS_FULL != 21:
        return False, (f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 21 "
                       f"(4 N x 4 F + 1 SATURATION_PC + 4 CEILING_H3)")
    if EXPECTED_N_UNITS_SMOKE != 5:
        return False, (f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 5 "
                       f"(2 N x 2 F + 1 SATURATION_PC)")
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} "
                f"SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. F-axis discriminator: F=1 vs F=16 produce DIFFERENT codebook hashes
    #    at same M/N/seed (TOPOLOGY axis endpoints are structurally distinct)
    seed = 999
    gen = torch.Generator(device=DEVICE)
    M_probe = 40
    N_test = 512
    gen.manual_seed(1017)
    props1, perms1, IMPL1, POS1, shard1, bundle1 = build_rules(
        M_probe, 1, gen, DEVICE, N_test)
    gen.manual_seed(1017)
    props16, perms16, IMPL16, POS16, shard16, bundle16 = build_rules(
        M_probe, 16, gen, DEVICE, N_test)
    hash_F1 = hashlib.sha256(shard1.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    hash_F16 = hashlib.sha256(shard16.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    if hash_F1 == hash_F16:
        return False, (f"F=1 and F=16 sharded codebooks bit-identical "
                       f"(TOPOLOGY axis has no effect); hash={hash_F1}")
    msgs.append(f"F-axis fires (F=1 vs F=16): F1_hash={hash_F1} F16_hash={hash_F16}")

    # 3. N-axis wiring sanity: props shape[-1] tracks N argument
    gen.manual_seed(2027)
    p_256, _, _, _, _, _ = build_rules(20, 1, gen, DEVICE, 256)
    gen.manual_seed(2027)
    p_2048, _, _, _, _, _ = build_rules(20, 1, gen, DEVICE, 2048)
    if p_256.shape[-1] != 256 or p_2048.shape[-1] != 2048:
        return False, (f"N-axis wiring broken: props shapes "
                       f"{tuple(p_256.shape)} vs {tuple(p_2048.shape)}")
    msgs.append(f"N-axis fires: props.shape[-1] {p_256.shape[-1]} vs {p_2048.shape[-1]}")

    # 4. SATURATION_PC selftest (Gate D): modern_hopfield SHARDED at trivial-easy
    #    (M=800, N=2048, F=1, L=4, corr=0.20) should reproduce baseline acc ~ 1.0.
    #    Threshold relaxed to 0.85 for TR=40 selftest vs 0.95 for TR=100 FULL.
    gen.manual_seed(1013)
    props2, perms2, IMPL2, POS2, sh2, bd2 = build_rules(
        PC_M, PC_F, gen, DEVICE, PC_N)
    acc_easy, _ = run_chain(STORAGE_FIXED, PC_MECH, L=L_FIXED, F=PC_F, TR=40,
                            props=props2, perms=perms2, IMPL=IMPL2, POS=POS2,
                            sharded_codebook=sh2, bundle_vec=bd2,
                            corruption=PC_CORR, gen=gen, device=DEVICE)
    if acc_easy < 0.85:
        return False, (f"SATURATION_PC selftest ({PC_MECH} M={PC_M} N={PC_N} "
                       f"F={PC_F} L={L_FIXED} corr={PC_CORR}) expected >= 0.85 "
                       f"at TR=40; got {acc_easy:.3f}")
    msgs.append(f"SATURATION_PC selftest ({PC_MECH} M={PC_M} N={PC_N} F={PC_F} "
                f"L={L_FIXED} corr={PC_CORR} TR=40): acc={acc_easy:.3f}")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed(seed: int, run_mode: str) -> Dict[str, Any]:
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        N_grid = N_GRID_SMOKE
        F_grid = F_GRID_SMOKE
        TR = TR_SMOKE
        include_ceiling = False
        expected_n = EXPECTED_N_UNITS_SMOKE
    else:
        N_grid = N_GRID_FULL
        F_grid = F_GRID_FULL
        TR = TR_FULL
        include_ceiling = True
        expected_n = EXPECTED_N_UNITS_FULL

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"N={N_grid} F={F_grid} mech={MECH_FIXED} storage={STORAGE_FIXED} "
          f"M={M_FIXED} L={L_FIXED} corr={CORRUPTION_FIXED} TR={TR} "
          f"expected_n={expected_n} include_ceiling={include_ceiling}",
          flush=True)

    phase_map: List[Dict[str, Any]] = []
    salt = 0
    t0 = time.perf_counter()

    # 1) Main factorial grid: N x F at cliff-adjacent regime
    for N in N_grid:
        for F in F_grid:
            salt += 1
            pt = eval_phase_point(MECH_FIXED, M_FIXED, N, F, L_FIXED,
                                  CORRUPTION_FIXED, STORAGE_FIXED, TR, seed,
                                  salt, arm_tag="SHARDED_main")
            phase_map.append(pt)
            print(f"  [{len(phase_map):3d}/{expected_n:3d}] main "
                  f"N={N:5d} F={F:2d} M={M_FIXED} L={L_FIXED} "
                  f"c={CORRUPTION_FIXED:.2f} acc={pt['acc']:.4f} "
                  f"dt={pt['elapsed_s']:.2f}s", flush=True)

    # 2) SATURATION_PC arm (Gate D reproducer)
    salt += 1
    pc_pt = eval_phase_point(PC_MECH, PC_M, PC_N, PC_F, L_FIXED,
                             PC_CORR, STORAGE_FIXED, TR, seed, salt,
                             arm_tag="SATURATION_PC")
    phase_map.append(pc_pt)
    print(f"  [{len(phase_map):3d}/{expected_n:3d}] PC   "
          f"N={PC_N:5d} F={PC_F:2d} M={PC_M} L={L_FIXED} c={PC_CORR:.2f} "
          f"acc={pc_pt['acc']:.4f} dt={pc_pt['elapsed_s']:.2f}s", flush=True)

    # 3) CEILING_H3 arm (deep-saturation null control) -- FULL only
    ceiling_pts: List[Dict[str, Any]] = []
    if include_ceiling:
        for F in CEILING_F_GRID:
            salt += 1
            cpt = eval_phase_point(MECH_FIXED, M_FIXED, CEILING_N, F, L_FIXED,
                                   CEILING_CORR, STORAGE_FIXED, TR, seed, salt,
                                   arm_tag="CEILING_H3")
            phase_map.append(cpt)
            ceiling_pts.append(cpt)
            print(f"  [{len(phase_map):3d}/{expected_n:3d}] CEIL "
                  f"N={CEILING_N:5d} F={F:2d} M={M_FIXED} L={L_FIXED} "
                  f"c={CEILING_CORR:.2f} acc={cpt['acc']:.4f} "
                  f"dt={cpt['elapsed_s']:.2f}s", flush=True)

    elapsed = time.perf_counter() - t0
    observed_n = len(phase_map)
    cardinality_ok = (observed_n == expected_n)

    # ---- META_RULE_AF arms_must_differ across F-axis endpoints on main grid ----
    # For each N, check hash-distinct across F values.
    main_pts = [p for p in phase_map if p.get("arm_tag") == "SHARDED_main"]
    F_endpoint_distinct = {}
    for N in N_grid:
        pts_at_N = [p for p in main_pts if p["N"] == N]
        hashes = {p["F"]: p["shard_hash"] for p in pts_at_N}
        n_distinct_F = len(set(hashes.values()))
        F_endpoint_distinct[str(N)] = {
            "hashes_by_F": hashes,
            "n_distinct": n_distinct_F,
            "all_distinct": n_distinct_F == len(pts_at_N),
        }
    arms_differ_verified = all(v["all_distinct"] for v in F_endpoint_distinct.values())

    # ---- SATURATION_PC pass/fail ----
    pc_acc = float(pc_pt["acc"])
    pc_pass = (pc_acc >= PC_THRESHOLD)

    # ---- Escapes-saturation gate ----
    main_accs = [p["acc"] for p in main_pts]
    main_mean = float(np.mean(main_accs)) if main_accs else -1.0
    n_in_band = sum(1 for a in main_accs
                    if NON_SATURATED_BAND_LO <= a <= NON_SATURATED_BAND_HI)
    frac_in_band = (n_in_band / len(main_accs)) if main_accs else 0.0
    # Per-N mean acc; per-F mean acc
    per_N_mean_acc: Dict[str, float] = {}
    for N in N_grid:
        slice_accs = [p["acc"] for p in main_pts if p["N"] == N]
        if slice_accs:
            per_N_mean_acc[str(N)] = round(float(np.mean(slice_accs)), 4)
    per_F_mean_acc: Dict[str, float] = {}
    for F in F_grid:
        slice_accs = [p["acc"] for p in main_pts if p["F"] == F]
        if slice_accs:
            per_F_mean_acc[str(F)] = round(float(np.mean(slice_accs)), 4)
    # Smoke gate: at least one slice must escape saturation (per-N OR per-F)
    per_slice_max_mean = 0.0
    per_slice_min_mean = 1.0
    all_slice_means = list(per_N_mean_acc.values()) + list(per_F_mean_acc.values())
    if all_slice_means:
        per_slice_max_mean = float(max(all_slice_means))
        per_slice_min_mean = float(min(all_slice_means))
    escapes_saturation_smoke = (per_slice_min_mean < NON_SATURATED_BAND_HI)
    escapes_saturation_full = (frac_in_band >= ESCAPES_SATURATION_MIN_FRACTION)

    # ---- Discriminator: topology_var_at_N (across F at each N) ----
    topology_var_at_N: Dict[str, Dict[str, Any]] = {}
    topology_var_at_N_in_band: Dict[str, Dict[str, Any]] = {}
    for N in N_grid:
        accs_by_F = {}
        for F in F_grid:
            matches = [p["acc"] for p in main_pts
                       if p["N"] == N and p["F"] == F]
            if matches:
                accs_by_F[F] = matches[0]
        if len(accs_by_F) == len(F_grid):
            vals = list(accs_by_F.values())
            spread = float(max(vals) - min(vals))
            mean = float(np.mean(vals))
            in_band = (NON_SATURATED_BAND_LO <= mean <= NON_SATURATED_BAND_HI)
            entry = {
                "accs_by_F": {str(k): round(v, 4) for k, v in accs_by_F.items()},
                "spread": round(spread, 4),
                "mean": round(mean, 4),
                "in_non_saturated_band": in_band,
            }
            topology_var_at_N[str(N)] = entry
            if in_band:
                topology_var_at_N_in_band[str(N)] = entry
    max_topology_var = max(
        (v["spread"] for v in topology_var_at_N.values()), default=0.0)
    max_topology_var_in_band = max(
        (v["spread"] for v in topology_var_at_N_in_band.values()), default=0.0)

    # ---- Discriminator: N_var_at_F (across N at each F) ----
    N_var_at_F: Dict[str, Dict[str, Any]] = {}
    N_var_at_F_in_band: Dict[str, Dict[str, Any]] = {}
    for F in F_grid:
        accs_by_N = {}
        for N in N_grid:
            matches = [p["acc"] for p in main_pts
                       if p["F"] == F and p["N"] == N]
            if matches:
                accs_by_N[N] = matches[0]
        if len(accs_by_N) == len(N_grid):
            vals = list(accs_by_N.values())
            spread = float(max(vals) - min(vals))
            mean = float(np.mean(vals))
            in_band = (NON_SATURATED_BAND_LO <= mean <= NON_SATURATED_BAND_HI)
            entry = {
                "accs_by_N": {str(k): round(v, 4) for k, v in accs_by_N.items()},
                "spread": round(spread, 4),
                "mean": round(mean, 4),
                "in_non_saturated_band": in_band,
            }
            N_var_at_F[str(F)] = entry
            if in_band:
                N_var_at_F_in_band[str(F)] = entry
    max_N_var = max((v["spread"] for v in N_var_at_F.values()), default=0.0)
    max_N_var_in_band = max(
        (v["spread"] for v in N_var_at_F_in_band.values()), default=0.0)

    # ---- Additive model deviation: cell_mean(N,F) - (marg_N(N) + marg_F(F) - grand) ----
    grand_mean = float(np.mean(main_accs)) if main_accs else 0.0
    marg_N = {N: (per_N_mean_acc.get(str(N), grand_mean)) for N in N_grid}
    marg_F = {F: (per_F_mean_acc.get(str(F), grand_mean)) for F in F_grid}
    N_x_F_deviation_map: Dict[str, float] = {}
    N_x_F_deviation_map_in_band: Dict[str, float] = {}
    max_N_x_F_dev = 0.0
    max_N_x_F_dev_in_band = 0.0
    for N in N_grid:
        for F in F_grid:
            matches = [p["acc"] for p in main_pts
                       if p["N"] == N and p["F"] == F]
            if matches:
                cell = float(matches[0])
                pred = marg_N[N] + marg_F[F] - grand_mean
                dev = cell - pred
                key = f"N{N}_F{F}"
                N_x_F_deviation_map[key] = round(dev, 4)
                if abs(dev) > max_N_x_F_dev:
                    max_N_x_F_dev = abs(dev)
                if (NON_SATURATED_BAND_LO <= cell <= NON_SATURATED_BAND_HI):
                    N_x_F_deviation_map_in_band[key] = round(dev, 4)
                    if abs(dev) > max_N_x_F_dev_in_band:
                        max_N_x_F_dev_in_band = abs(dev)

    # ---- H3 CEILING check: at N=8192, corr=0.60, topology_var across F ~ 0 ----
    ceiling_topology_var = None
    ceiling_topology_pass = None
    ceiling_accs_by_F = None
    if ceiling_pts:
        accs = [p["acc"] for p in ceiling_pts]
        ceiling_accs_by_F = {str(p["F"]): p["acc"] for p in ceiling_pts}
        ceiling_topology_var = float(max(accs) - min(accs))
        ceiling_topology_pass = (ceiling_topology_var <= CEILING_TOPOLOGY_VAR_MAX)

    # ---- Hypothesis assessment (band-restricted) ----
    n_band_slices = (len(topology_var_at_N_in_band)
                     + len(N_var_at_F_in_band))
    if n_band_slices == 0:
        hyp_verdict = "H_UNKNOWN_NO_BAND_SLICES"
        hyp_reason = ("no phase-slices had mean(acc) in "
                      f"[{NON_SATURATED_BAND_LO}, {NON_SATURATED_BAND_HI}]")
    elif (max_topology_var_in_band >= TOPOLOGY_VAR_H1_THRESHOLD
          or max_N_var_in_band >= N_VAR_H1_THRESHOLD
          or max_N_x_F_dev_in_band >= N_X_F_DEV_H1_THRESHOLD):
        hyp_verdict = "H1_N_x_TOPOLOGY_CROSS_TERM_AT_CLIFF"
        hyp_reason = (f"in {n_band_slices} band-slices: "
                      f"max_topology_var_in_band={max_topology_var_in_band:.4f} "
                      f"OR max_N_var_in_band={max_N_var_in_band:.4f} "
                      f"OR max_N_x_F_dev_in_band={max_N_x_F_dev_in_band:.4f}; "
                      f"H1 threshold (any >= 0.10) satisfied; N and TOPOLOGY "
                      f"have joint effect at cliff-adjacent regime")
    elif (max_topology_var_in_band < TOPOLOGY_VAR_H2_THRESHOLD
          and max_N_var_in_band < N_VAR_H2_THRESHOLD
          and max_N_x_F_dev_in_band < N_X_F_DEV_H2_THRESHOLD):
        hyp_verdict = "H2_N_AND_TOPOLOGY_INDEPENDENT"
        hyp_reason = (f"in {n_band_slices} band-slices: "
                      f"topology_var<0.05 AND N_var<0.05 AND dev<0.05; "
                      f"topology_var_in_band={max_topology_var_in_band:.4f} "
                      f"N_var_in_band={max_N_var_in_band:.4f} "
                      f"N_x_F_dev_in_band={max_N_x_F_dev_in_band:.4f}; "
                      f"axes are independent at cliff-adjacent regime; "
                      f"strengthens regime map ORTHOGONAL_AXES thesis")
    else:
        hyp_verdict = "MIDDLE_BAND_WEAK_N_x_TOPOLOGY_MODERATION"
        hyp_reason = (f"in {n_band_slices} band-slices: "
                      f"topology_var_in_band={max_topology_var_in_band:.4f} "
                      f"N_var_in_band={max_N_var_in_band:.4f} "
                      f"N_x_F_dev_in_band={max_N_x_F_dev_in_band:.4f}; "
                      f"between H2 null and H1 threshold; MM_TENTATIVE weak "
                      f"N x TOPOLOGY moderation")

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
        "arms_differ_verified": arms_differ_verified,
        "F_endpoint_distinct": F_endpoint_distinct,
        "saturation_pc": {
            "arm": "SATURATION_PC",
            "mechanism": PC_MECH,
            "M": PC_M, "N": PC_N, "corruption": PC_CORR,
            "F": PC_F, "L": L_FIXED,
            "acc": pc_acc,
            "threshold": PC_THRESHOLD,
            "pass": pc_pass,
        },
        "ceiling_h3": {
            "arm": "CEILING_H3",
            "N": CEILING_N, "corruption": CEILING_CORR, "F_grid": CEILING_F_GRID,
            "mechanism": MECH_FIXED, "M": M_FIXED, "L": L_FIXED,
            "accs_by_F": ceiling_accs_by_F,
            "topology_var": (round(ceiling_topology_var, 4)
                             if ceiling_topology_var is not None else None),
            "topology_var_max_h3": CEILING_TOPOLOGY_VAR_MAX,
            "pass": ceiling_topology_pass,
        } if ceiling_pts else None,
        "main_grid_mean_acc": round(main_mean, 4),
        "main_grid_n_in_non_saturated_band": n_in_band,
        "main_grid_n_total": len(main_accs),
        "main_grid_fraction_in_non_saturated_band": round(frac_in_band, 4),
        "per_N_mean_acc": per_N_mean_acc,
        "per_F_mean_acc": per_F_mean_acc,
        "escapes_saturation_ceiling_smoke": escapes_saturation_smoke,
        "escapes_saturation_ceiling_full": escapes_saturation_full,
        "topology_var_at_N": topology_var_at_N,
        "topology_var_at_N_in_band": topology_var_at_N_in_band,
        "max_topology_var": round(max_topology_var, 4),
        "max_topology_var_in_band": round(max_topology_var_in_band, 4),
        "N_var_at_F": N_var_at_F,
        "N_var_at_F_in_band": N_var_at_F_in_band,
        "max_N_var": round(max_N_var, 4),
        "max_N_var_in_band": round(max_N_var_in_band, 4),
        "N_x_F_deviation_map": N_x_F_deviation_map,
        "N_x_F_deviation_map_in_band": N_x_F_deviation_map_in_band,
        "max_N_x_F_deviation": round(max_N_x_F_dev, 4),
        "max_N_x_F_deviation_in_band": round(max_N_x_F_dev_in_band, 4),
        "grand_mean_main": round(grand_mean, 4),
        "n_band_slices": n_band_slices,
        "hypothesis_assessment": hyp_verdict,
        "hypothesis_reason": hyp_reason,
        "non_saturated_band": [NON_SATURATED_BAND_LO, NON_SATURATED_BAND_HI],
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
    expected_n = body.get("expected_n_units")
    if len(phase_map) != expected_n:
        return False, (f"cardinality_breach: expected {expected_n} "
                       f"got {len(phase_map)}")
    if not body.get("arms_differ_verified"):
        return False, (f"arms_differ_fail (META_RULE_AF): F-axis endpoints "
                       f"not hash-distinct at some N; F_endpoint_distinct="
                       f"{body.get('F_endpoint_distinct')}")
    pc = body.get("saturation_pc", {})
    if not pc.get("pass"):
        return False, (f"saturation_pc_fail: {PC_MECH} SHARDED at PC regime "
                       f"(M={pc.get('M')} N={pc.get('N')} F={pc.get('F')} "
                       f"corr={pc.get('corruption')}) acc={pc.get('acc')} "
                       f"< threshold={pc.get('threshold')}")
    if not body.get("escapes_saturation_ceiling_smoke"):
        return False, (f"escapes_saturation_ceiling_fail: no slice has mean-acc "
                       f"< {NON_SATURATED_BAND_HI}; per_N_mean_acc="
                       f"{body.get('per_N_mean_acc')} per_F_mean_acc="
                       f"{body.get('per_F_mean_acc')}; smoke regime fully "
                       f"saturated -- re-spec grid to higher corr or higher M "
                       f"or smaller N")
    # NaN sanity
    for pt in phase_map:
        if pt.get("acc") != pt.get("acc"):
            return False, f"NAN_in_phase_map at {pt}"
    # Discriminator variance INFORMATIONAL only (null-hypothesis SMOKE discipline).
    max_top = body.get("max_topology_var_in_band", 0.0)
    max_nvar = body.get("max_N_var_in_band", 0.0)
    max_dev = body.get("max_N_x_F_deviation_in_band", 0.0)
    frac = body.get("main_grid_fraction_in_non_saturated_band", 0.0)
    hyp = body.get("hypothesis_assessment")
    return True, (f"smoke_gate_pass: cardinality_ok + F-endpoint-hash-distinct + "
                  f"pc_acc={pc.get('acc')} (>={pc.get('threshold')}) + "
                  f"escapes_saturation (some slice mean<{NON_SATURATED_BAND_HI}) + "
                  f"frac_in_band={frac}; informational: "
                  f"max_topology_var_in_band={max_top} "
                  f"max_N_var_in_band={max_nvar} "
                  f"max_N_x_F_dev_in_band={max_dev} hyp_preview={hyp}")


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
        "arms_differ_verified": body.get("arms_differ_verified"),
        "F_endpoint_distinct": body.get("F_endpoint_distinct"),
        "saturation_pc": body.get("saturation_pc"),
        "ceiling_h3": body.get("ceiling_h3"),
        "main_grid_mean_acc": body.get("main_grid_mean_acc"),
        "main_grid_n_in_non_saturated_band":
            body.get("main_grid_n_in_non_saturated_band"),
        "main_grid_n_total": body.get("main_grid_n_total"),
        "main_grid_fraction_in_non_saturated_band":
            body.get("main_grid_fraction_in_non_saturated_band"),
        "per_N_mean_acc": body.get("per_N_mean_acc"),
        "per_F_mean_acc": body.get("per_F_mean_acc"),
        "escapes_saturation_ceiling_smoke":
            body.get("escapes_saturation_ceiling_smoke"),
        "escapes_saturation_ceiling_full":
            body.get("escapes_saturation_ceiling_full"),
        "topology_var_at_N": body.get("topology_var_at_N"),
        "topology_var_at_N_in_band": body.get("topology_var_at_N_in_band"),
        "max_topology_var": body.get("max_topology_var"),
        "max_topology_var_in_band": body.get("max_topology_var_in_band"),
        "N_var_at_F": body.get("N_var_at_F"),
        "N_var_at_F_in_band": body.get("N_var_at_F_in_band"),
        "max_N_var": body.get("max_N_var"),
        "max_N_var_in_band": body.get("max_N_var_in_band"),
        "N_x_F_deviation_map": body.get("N_x_F_deviation_map"),
        "N_x_F_deviation_map_in_band": body.get("N_x_F_deviation_map_in_band"),
        "max_N_x_F_deviation": body.get("max_N_x_F_deviation"),
        "max_N_x_F_deviation_in_band": body.get("max_N_x_F_deviation_in_band"),
        "grand_mean_main": body.get("grand_mean_main"),
        "n_band_slices": body.get("n_band_slices"),
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
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"expected={expected_n} observed={observed_n}")
    elif not body.get("arms_differ_verified"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_ARMS_MUST_DIFFER_META_RULE_AF: F-axis endpoints "
                f"not hash-distinct at some N; F_endpoint_distinct="
                f"{body.get('F_endpoint_distinct')}")
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
        ceiling = body.get("ceiling_h3") or {}
        ceiling_pass = ceiling.get("pass")
        ceiling_var = ceiling.get("topology_var")
        ceiling_note = ""
        if ceiling_pass is False:
            ceiling_note = (f"; H3_CEILING_CONTROL_FAIL: topology_var at CEILING "
                            f"(N={CEILING_N} corr={CEILING_CORR}) = {ceiling_var} "
                            f"> {CEILING_TOPOLOGY_VAR_MAX}; deep-saturation null "
                            f"control fired unexpectedly; treat H1 claim with "
                            f"caution")
        elif ceiling_pass is True:
            ceiling_note = (f"; H3_CEILING_CONTROL_PASS: topology_var at CEILING "
                            f"= {ceiling_var} <= {CEILING_TOPOLOGY_VAR_MAX}")

        if hyp == "H2_N_AND_TOPOLOGY_INDEPENDENT":
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H2_N_AND_TOPOLOGY_INDEPENDENT_AT_CLIFF: "
                    f"n_band_slices={body.get('n_band_slices')}; "
                    f"max_topology_var_in_band="
                    f"{body.get('max_topology_var_in_band')} < 0.05 AND "
                    f"max_N_var_in_band={body.get('max_N_var_in_band')} < 0.05 "
                    f"AND max_N_x_F_dev_in_band="
                    f"{body.get('max_N_x_F_deviation_in_band')} < 0.05; "
                    f"axes are orthogonal at cliff-adjacent regime; "
                    f"strengthens regime map ORTHOGONAL_AXES thesis; "
                    f"CG_META candidate: N_x_TOPOLOGY_INDEPENDENT_v1; "
                    f"pending Skunkworks landed-VET + 3-seed replication"
                    f"{ceiling_note}; {reason}")
        elif hyp == "H1_N_x_TOPOLOGY_CROSS_TERM_AT_CLIFF":
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H1_N_x_TOPOLOGY_CROSS_TERM_AT_CLIFF: "
                    f"n_band_slices={body.get('n_band_slices')}; "
                    f"max_topology_var_in_band="
                    f"{body.get('max_topology_var_in_band')} "
                    f"max_N_var_in_band={body.get('max_N_var_in_band')} "
                    f"max_N_x_F_dev_in_band="
                    f"{body.get('max_N_x_F_deviation_in_band')}; N and "
                    f"TOPOLOGY have joint effect at cliff-adjacent regime; "
                    f"updates REGIME MAP with FIRST non-mechanism cross-term "
                    f"boundary point{ceiling_note}; {reason}")
        elif hyp == "MIDDLE_BAND_WEAK_N_x_TOPOLOGY_MODERATION":
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_WEAK_N_x_TOPOLOGY_MODERATION: "
                    f"n_band_slices={body.get('n_band_slices')}; "
                    f"weak cross-term (MM_TENTATIVE); consider refined sweep"
                    f"{ceiling_note}; {reason}")
        elif hyp == "H_UNKNOWN_NO_BAND_SLICES":
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_NO_BAND_SLICES: escapes_saturation gate "
                    f"passed but no per-slice mean landed in band; re-spec"
                    f"{ceiling_note}; {reason}")
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
    "ANCHOR_NAME", "DEVICE", "GPU_NAME",
    "N_GRID_FULL", "N_GRID_SMOKE",
    "F_GRID_FULL", "F_GRID_SMOKE",
    "MECH_FIXED", "STORAGE_FIXED", "M_FIXED", "L_FIXED", "CORRUPTION_FIXED",
    "TR_FULL", "TR_SMOKE",
    "PC_MECH", "PC_M", "PC_N", "PC_F", "PC_CORR", "PC_THRESHOLD",
    "CEILING_N", "CEILING_CORR", "CEILING_F_GRID", "CEILING_TOPOLOGY_VAR_MAX",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "NON_SATURATED_BAND_LO", "NON_SATURATED_BAND_HI",
    "ESCAPES_SATURATION_MIN_FRACTION",
    "TOPOLOGY_VAR_H1_THRESHOLD", "N_VAR_H1_THRESHOLD",
    "N_X_F_DEV_H1_THRESHOLD",
    "TOPOLOGY_VAR_H2_THRESHOLD", "N_VAR_H2_THRESHOLD",
    "N_X_F_DEV_H2_THRESHOLD",
    "REQUIRED_FIELDS",
    "eval_phase_point", "selftest", "run_one_seed",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
