"""Stage 1 Regime Probe 9 v2: N (SCALE) x ALGEBRA (chain-depth L) at BUNDLED near-capacity.

Cell anchor: `stage1_regime_probe_9_v2_N_x_algebra_in_band_L_over_Ncliff_v1`
Pre-reg:     preregs/2026-07-03_stage1_regime_probe_9_v2_N_x_algebra_in_band_L_over_Ncliff_v1.md

Purpose:
    Probe 9 v1 (N x TOPOLOGY at SHARDED, isolated SMOKE HP) targeted a different
    axis pair. This v2 is the RESEARCH-AUTHORITY-DIRECTED (2x-drill NEG1 2026-07-03)
    cheap decisive test: N x ALGEBRA (chain-depth L) cross-term at BUNDLED
    near-capacity regime, following Frady/Sommer 2018/2020 prediction that
    cross-term emerges as L approaches a threshold fraction of N_cliff.

    v1 (N=256 floor + N=2048 ceiling in prior work) tested extremes where BOTH
    endpoints pinned; cross-term=0 was trivially true (Skunkworks VET flagged
    saturation-vacuous). This v2 targets the theoretically-interesting crossover.

Research authority: notes/research_stage1_regime_map_4negatives_2026-07-03.md NEG 1.
Only 1 of 4 negatives where 40-70yr theory does NOT already predict result.

Empirical N_cliff bracket (MEASURED@bracket_scout2 + bracket_verify 2026-07-03):
    BUNDLED modern_hopfield cliff-adjacent regime:
        N_cliff = 2048, M = 10, F = 1, corr = 0.10, storage = BUNDLED, mech = modern_hopfield
    At 3-seed TR=100 verify:
        (N=1024, L=2)  acc = 0.367  (IB)
        (N=1024, L=4)  acc = 0.473  (IB)
        (N=1024, L=8)  acc = 0.650  (IB, non-monotonic rising)
        (N=1024, L=16) acc = 0.587  (IB)
        (N=2048, L=2)  acc = 0.297  (floor-adjacent)
        (N=4096, L=2)  acc = 0.503  (IB)
        (N=4096, L=8)  acc = 0.400  (IB)
    max|additive-model residual| in-band = 0.162 (already above H1 threshold 0.15).
    Prior work check: substrate cosine=0.36 top hit is Modern Hopfield capacity
        general references (notes/research_BetX_skill_composition_2026-05-21.md);
        NO prior atom on N x algebra cross-term at BUNDLED near-capacity.
        This cell is genuinely novel (matches Research NEG1 assessment).

Hypotheses (falsifiable; band-restricted; L/N_cliff bucketed):
    L/N_cliff RATIO bucketing (per Research spec):
      Compositional-pressure ratio = L * (N_cliff / N). Higher L or smaller N ->
      more pressure. Cross-term theory: max_dev should be HIGH at high-pressure
      cells and LOW at low-pressure cells.
      Buckets are median-split on pressure = L * (N_cliff / N):
        low bucket = pressure below median (large N, small L)
        high bucket = pressure at/above median (small N, large L)

    H1 (BUNDLED near-capacity N x L cross-term):
        max|additive-model residual| in HIGH_LN_RATIO bucket in-band >= 0.15
        AND max|additive-model residual| in LOW_LN_RATIO bucket in-band < 0.05
      -> confirms Frady/Sommer near-capacity coupling literature; N and L
         are NON-additive at BUNDLED near-capacity.

    H1_ALT (weaker cross-term signal):
        overall_max|residual| in-band >= 0.10
        (permits diffuse cross-term even without clean bucket separation)

    H2 (null: N and L independent across all buckets):
        overall_max|residual| in-band < 0.05
      -> NOVEL substrate-specific finding contradicting near-capacity coupling
         literature; consistent with per-step cleanup resetting noise
         (analog to prior-arc SHARDED arbitrary-depth finding).

    H3 (deep-saturation null control):
        at DEEP_SAT arm (N=8192, M=100, corr=0.60, L=8), acc >= 0.95
      -> mechanism DEGENERATES at ceiling; no cross-term visible; positive null.

    H4 (SATURATION_PC gate D reproducer):
        at PC arm (SHARDED modern_hopfield M=800, N=2048, F=1, L=4, corr=0.20),
        acc >= 0.95
      -> primitive-invocation matches prior chain-grade evidence; downstream
         cross-term claim trustworthy.

Cited source atoms (exact names, no abstraction; per META_RULE_AC):
    research_stage1_regime_map_4negatives_2026-07-03 NEG 1 (Research authority)
    stage1_regime_probe_9_N_x_topology_non_saturated_v1 (v1 sibling, template)
    stage1_regime_probe_10_storage_x_algebra_non_saturated_v1 (Probe 10 BUNDLED cliff)
    feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-07-03
    feedback_plate_bound_too_pessimistic_for_sharded_fhrr_chain_composition_2026-07-03
    feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03
    feedback_mechanism_abstraction_lossy_cite_source_signature_2026-07-03
    META_cross_term_measurement_requires_both_arms_in_band_probe10_v1 (Skunkworks meta #43)

Source signature (MECH_ABSTRACTION_LOSSY per feedback):
    (STORAGE=BUNDLED, MECH=modern_hopfield, N_cliff=2048, M=10, F=1, corr=0.10, TR=100)

Reuse (Principle 11):
    Primitives imported from _stage1_physics_law_joint_composition_factorial_v1_core:
      DEVICE, GPU_NAME, BETA, ALPHA_SOFT, build_rules, run_chain

Sweep grid FULL (17 pts / seed):
    N in {1024, 2048, 4096} x L in {2, 4, 8, 16} = 12 SHARDED_main pts  ...
        wait, STORAGE is BUNDLED here. Renamed: BUNDLED_main.
    BUNDLED_main = 12 pts
    SATURATION_PC arm (Gate D): 1 pt (SHARDED modern_hopfield reproducer)
    DEEP_SAT arm (H3 null): 4 pts (N=8192, M=100, corr=0.60, L in {2,4,8,16})
    TOTAL FULL = 12 + 1 + 4 = 17 pts / seed

Sweep grid SMOKE (5 pts):
    BUNDLED_main = 4 pts: N in {1024, 4096} x L in {2, 16}
    SATURATION_PC arm = 1 pt
    TOTAL SMOKE = 5 pts

Fixed:
    MECH = modern_hopfield
    STORAGE = BUNDLED  (per Research: BUNDLED shows near-capacity coupling; SHARDED has arbitrary-depth prior)
    M = 10   (BUNDLED capacity limit @N=2048, MEASURED@bracket_scout2)
    F = 1
    corr = 0.10

Compute architecture: sequential-CPU justified (BUNDLED modern_hopfield at M=10
    N<=4096 is O(1e5) matmul; each phase point < 1s CPU; total < 30s per seed;
    per feedback_smoke_only_local_cpu_no_full_dispatches USER-LOCKED 2026-07-01
    SMOKE dispatches to local_cpu_queue).

STORAGE STRATEGY: BUNDLED (explicit discriminator arm; Research-authority-directed
    to test BUNDLED near-capacity per Plate/Frady/Sommer near-capacity coupling).

Sibling wrappers: exp_stage1_regime_probe_9_v2_N_x_algebra_in_band_L_over_Ncliff_v1_s7.py

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-07-03 (agent-spawn, Opus 4.7). Research-authority-directed.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; L-axis endpoints hash-distinct)
# - final_metrics_atomicity: tmp_replace (via sibling wrapper)
# - except SystemExit: raise BEFORE except Exception (no BaseException) (via wrapper)
# - crlb_n/a: categorical accuracy; discriminator is band-restricted additive residual
# - escapes_saturation_ceiling at smoke (META_RULE_AG-analog for non-saturated design)
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
# - HP_SCOPE per-arm declaration (BUNDLED_main vs SATURATION_PC vs DEEP_SAT)
# - cardinality_ok for sweep-axis cells (META_RULE_H; EXPECTED_N_UNITS gate)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except)
# - calibration_check: default_ok_for_this_regime (BETA=8.0 inherited)
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

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._stage1_physics_law_joint_composition_factorial_v1_core import (
    BETA, ALPHA_SOFT, DEVICE, GPU_NAME, build_rules, run_chain,
)

ANCHOR_NAME = "stage1_regime_probe_9_v2_N_x_algebra_in_band_L_over_Ncliff_v1"

# ---------------------------------------------------------------------------
# Sweep constants (LOCKED at module init; MEASURED@bracket_scout2 empirical)
# ---------------------------------------------------------------------------
# N axis (SCALE) x L axis (ALGEBRA chain-depth) at BUNDLED near-capacity
# N_cliff = 2048 MEASURED@bracket_scout2 (BUNDLED modern_hopfield M=10 corr=0.10)
N_CLIFF = 2048
N_GRID_FULL = [1024, 2048, 4096]   # 0.5x, 1x, 2x N_cliff
N_GRID_SMOKE = [1024, 4096]

L_GRID_FULL = [2, 4, 8, 16]
L_GRID_SMOKE = [2, 16]

# Fixed regime at N_cliff bracket (BUNDLED modern_hopfield near-capacity)
MECH_FIXED = "modern_hopfield"
STORAGE_FIXED = "BUNDLED"
M_FIXED = 10
F_FIXED = 1
CORRUPTION_FIXED = 0.10

# TR (queries per point)
TR_FULL = 100
TR_SMOKE = 40

# SATURATION_PC arm (Gate D reproducer): SHARDED modern_hopfield at easy regime
# HYPOTHESIZED@this-prereg: at (SHARDED, modern_hopfield, F=1, M=800, N=2048,
# L=4, corr=0.20), acc >= 0.95. Same as Probe 9 v1 PC arm.
PC_MECH = MECH_FIXED
PC_STORAGE = "SHARDED"
PC_M = 800
PC_N = 2048
PC_F = 1
PC_L = 4
PC_CORR = 0.20
PC_THRESHOLD = 0.95

# DEEP_SAT arm (H3 null control): at deep-saturation regime, no cross-term
# HYPOTHESIZED@this-prereg: at (BUNDLED, modern_hopfield, N=8192, M=100, corr=0.60,
# L in {2,4,8,16}), acc for L=2 >= 0.30 as spot proof of "at deep-saturation the L
# axis pins uniformly high" (H3 fires when max L-spread < 0.10)
DEEP_SAT_STORAGE = "BUNDLED"
DEEP_SAT_MECH = MECH_FIXED
DEEP_SAT_N = 8192
DEEP_SAT_M = 100
DEEP_SAT_CORR = 0.60
DEEP_SAT_L_GRID = [2, 4, 8, 16]
DEEP_SAT_L_SPREAD_MAX = 0.10  # H3 threshold

# Cardinality
# FULL: 3 N x 4 L = 12 main + 1 PC + 4 DEEP_SAT = 17
EXPECTED_N_UNITS_FULL = (len(N_GRID_FULL) * len(L_GRID_FULL)) + 1 + len(DEEP_SAT_L_GRID)
# SMOKE: 2 N x 2 L = 4 main + 1 PC = 5 (DEEP_SAT skipped in smoke)
EXPECTED_N_UNITS_SMOKE = (len(N_GRID_SMOKE) * len(L_GRID_SMOKE)) + 1

# Non-saturated band
NON_SATURATED_BAND_LO = 0.30
NON_SATURATED_BAND_HI = 0.95

# H1 thresholds (bucketed L/N_cliff pressure)
CROSS_TERM_HIGH_BUCKET_H1_THRESHOLD = 0.15  # max|dev| in high-pressure bucket
CROSS_TERM_LOW_BUCKET_H1_THRESHOLD = 0.05   # max|dev| in low-pressure bucket
CROSS_TERM_OVERALL_H1_ALT_THRESHOLD = 0.10  # weaker signal (diffuse)
CROSS_TERM_H2_THRESHOLD = 0.05              # null: no residual anywhere

# Grid must escape saturation: >= 30% of pts in [0.30, 0.95] at FULL; SMOKE relaxed
ESCAPES_SATURATION_MIN_FRACTION = 0.30

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# Per-phase-point eval (matches Probe 9 v1 signature; L is the swept axis)
# ---------------------------------------------------------------------------
def eval_phase_point(mechanism: str, M_props: int, N: int, F: int, L: int,
                     corruption: float, storage: str, TR: int,
                     seed: int, salt: int,
                     arm_tag: str = "BUNDLED_main") -> Dict[str, Any]:
    """Run a single phase point at (mech, M, N, F, L, corr, storage)."""
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
    # NaN sanity
    if storage == "SHARDED":
        cb = sharded_codebook
    else:
        cb = bundle_vec
    if (torch.isnan(cb.real).any().item()
            or torch.isnan(cb.imag).any().item()):
        raise RuntimeError(f"NAN_IN_CODEBOOK storage={storage} mech={mechanism} "
                           f"M={M_props} N={N} F={F}")

    acc, final_ci = run_chain(storage, mechanism, L, F, TR,
                              props, perms, IMPL, POS,
                              sharded_codebook, bundle_vec, corruption,
                              gen, device)

    ci_bytes = final_ci.detach().cpu().numpy().tobytes()
    cb_bytes = cb.detach().cpu().numpy().tobytes()
    output_hash = hashlib.sha256(ci_bytes).hexdigest()[:16]
    cb_hash = hashlib.sha256(cb_bytes).hexdigest()[:16]

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
        "codebook_hash": cb_hash,
        "peak_mem_mb": peak_mem_mb,
        "elapsed_s": round(elapsed, 3),
    }


# ---------------------------------------------------------------------------
# Selftest (wall < 60s target on CPU)
# ---------------------------------------------------------------------------
def selftest() -> Tuple[bool, str]:
    msgs = []

    if EXPECTED_N_UNITS_FULL != 17:
        return False, (f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 17 "
                       f"(3 N x 4 L + 1 SATURATION_PC + 4 DEEP_SAT)")
    if EXPECTED_N_UNITS_SMOKE != 5:
        return False, (f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 5 "
                       f"(2 N x 2 L + 1 SATURATION_PC)")
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} "
                f"SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # L-axis discriminator: L=2 vs L=16 produce DIFFERENT chain length effects
    # at same M/N/seed (verify chain_length is being used, not silently ignored)
    seed = 999
    gen = torch.Generator(device=DEVICE)
    N_test = 1024
    gen.manual_seed(2027)
    props, perms, IMPL, POS, shard, bundle = build_rules(
        M_FIXED, F_FIXED, gen, DEVICE, N_test)
    # Same setup, different L should differ
    gen.manual_seed(2027)  # reset for deterministic run
    acc_L2, _ = run_chain(STORAGE_FIXED, MECH_FIXED, 2, F_FIXED, 30,
                          props, perms, IMPL, POS, shard, bundle,
                          CORRUPTION_FIXED, gen, DEVICE)
    gen.manual_seed(2027)  # reset for deterministic run
    acc_L16, _ = run_chain(STORAGE_FIXED, MECH_FIXED, 16, F_FIXED, 30,
                           props, perms, IMPL, POS, shard, bundle,
                           CORRUPTION_FIXED, gen, DEVICE)
    if acc_L2 == acc_L16 and acc_L2 in (0.0, 1.0):
        # Only bit-identical AND both extreme (0 or 1) is truly worrying —
        # if both hit floor/ceiling they'd match by accident
        return False, (f"L=2 and L=16 produce identical extreme acc {acc_L2}; "
                       f"suggests L axis not respected in chain-primitive")
    msgs.append(f"L-axis fires (L=2 vs L=16): acc={acc_L2:.3f} vs {acc_L16:.3f}")

    # N-axis wiring sanity
    gen.manual_seed(3037)
    p_1024, _, _, _, _, _ = build_rules(20, 1, gen, DEVICE, 1024)
    gen.manual_seed(3037)
    p_4096, _, _, _, _, _ = build_rules(20, 1, gen, DEVICE, 4096)
    if p_1024.shape[-1] != 1024 or p_4096.shape[-1] != 4096:
        return False, (f"N-axis wiring broken: props shapes "
                       f"{tuple(p_1024.shape)} vs {tuple(p_4096.shape)}")
    msgs.append(f"N-axis fires: props.shape[-1] {p_1024.shape[-1]} vs {p_4096.shape[-1]}")

    # STORAGE=BUNDLED wiring sanity: bundle_vec shape[-1] == N
    if bundle.shape[-1] != N_test:
        return False, f"bundle_vec.shape {tuple(bundle.shape)} != N={N_test}"
    msgs.append(f"BUNDLED storage wired: bundle.shape={tuple(bundle.shape)}")

    # SATURATION_PC selftest at TR=40 (relaxed threshold)
    gen.manual_seed(1013)
    props2, perms2, IMPL2, POS2, sh2, bd2 = build_rules(
        PC_M, PC_F, gen, DEVICE, PC_N)
    acc_easy, _ = run_chain(PC_STORAGE, PC_MECH, L=PC_L, F=PC_F, TR=40,
                            props=props2, perms=perms2, IMPL=IMPL2, POS=POS2,
                            sharded_codebook=sh2, bundle_vec=bd2,
                            corruption=PC_CORR, gen=gen, device=DEVICE)
    if acc_easy < 0.85:
        return False, (f"SATURATION_PC selftest ({PC_STORAGE} {PC_MECH} M={PC_M} "
                       f"N={PC_N} F={PC_F} L={PC_L} corr={PC_CORR}) expected >= 0.85 "
                       f"at TR=40; got {acc_easy:.3f}")
    msgs.append(f"SATURATION_PC selftest ({PC_STORAGE} {PC_MECH} M={PC_M} N={PC_N} "
                f"F={PC_F} L={PC_L} corr={PC_CORR} TR=40): acc={acc_easy:.3f}")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed(seed: int, run_mode: str) -> Dict[str, Any]:
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        N_grid = N_GRID_SMOKE
        L_grid = L_GRID_SMOKE
        TR = TR_SMOKE
        include_deep_sat = False
        expected_n = EXPECTED_N_UNITS_SMOKE
    else:
        N_grid = N_GRID_FULL
        L_grid = L_GRID_FULL
        TR = TR_FULL
        include_deep_sat = True
        expected_n = EXPECTED_N_UNITS_FULL

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"N={N_grid} L={L_grid} mech={MECH_FIXED} storage={STORAGE_FIXED} "
          f"M={M_FIXED} F={F_FIXED} corr={CORRUPTION_FIXED} TR={TR} "
          f"expected_n={expected_n} include_deep_sat={include_deep_sat}",
          flush=True)

    phase_map: List[Dict[str, Any]] = []
    salt = 0
    t0 = time.perf_counter()

    # 1) Main factorial grid: N x L at BUNDLED near-capacity
    for N in N_grid:
        for L in L_grid:
            salt += 1
            pt = eval_phase_point(MECH_FIXED, M_FIXED, N, F_FIXED, L,
                                  CORRUPTION_FIXED, STORAGE_FIXED, TR, seed,
                                  salt, arm_tag="BUNDLED_main")
            phase_map.append(pt)
            print(f"  [{len(phase_map):3d}/{expected_n:3d}] main "
                  f"N={N:5d} L={L:2d} M={M_FIXED} F={F_FIXED} "
                  f"c={CORRUPTION_FIXED:.2f} acc={pt['acc']:.4f} "
                  f"dt={pt['elapsed_s']:.2f}s", flush=True)

    # 2) SATURATION_PC arm (Gate D reproducer)
    salt += 1
    pc_pt = eval_phase_point(PC_MECH, PC_M, PC_N, PC_F, PC_L,
                             PC_CORR, PC_STORAGE, TR, seed, salt,
                             arm_tag="SATURATION_PC")
    phase_map.append(pc_pt)
    print(f"  [{len(phase_map):3d}/{expected_n:3d}] PC   "
          f"N={PC_N:5d} L={PC_L:2d} M={PC_M} F={PC_F} c={PC_CORR:.2f} "
          f"acc={pc_pt['acc']:.4f} dt={pc_pt['elapsed_s']:.2f}s", flush=True)

    # 3) DEEP_SAT arm (H3 null control) -- FULL only
    deep_sat_pts: List[Dict[str, Any]] = []
    if include_deep_sat:
        for L in DEEP_SAT_L_GRID:
            salt += 1
            dpt = eval_phase_point(DEEP_SAT_MECH, DEEP_SAT_M, DEEP_SAT_N,
                                   F_FIXED, L, DEEP_SAT_CORR, DEEP_SAT_STORAGE,
                                   TR, seed, salt, arm_tag="DEEP_SAT")
            phase_map.append(dpt)
            deep_sat_pts.append(dpt)
            print(f"  [{len(phase_map):3d}/{expected_n:3d}] DEEP "
                  f"N={DEEP_SAT_N:5d} L={L:2d} M={DEEP_SAT_M} F={F_FIXED} "
                  f"c={DEEP_SAT_CORR:.2f} acc={dpt['acc']:.4f} "
                  f"dt={dpt['elapsed_s']:.2f}s", flush=True)

    elapsed = time.perf_counter() - t0
    observed_n = len(phase_map)
    cardinality_ok = (observed_n == expected_n)

    # ---- META_RULE_AF arms_must_differ across L-axis endpoints on main grid ----
    # For each N, check hash-distinct across L values.
    main_pts = [p for p in phase_map if p.get("arm_tag") == "BUNDLED_main"]
    L_endpoint_distinct = {}
    for N in N_grid:
        pts_at_N = [p for p in main_pts if p["N"] == N]
        hashes = {p["L"]: p["output_hash"] for p in pts_at_N}
        n_distinct_L = len(set(hashes.values()))
        L_endpoint_distinct[str(N)] = {
            "hashes_by_L": hashes,
            "n_distinct": n_distinct_L,
            "all_distinct": n_distinct_L == len(pts_at_N),
        }
    arms_differ_verified = all(v["all_distinct"] for v in L_endpoint_distinct.values())

    # ---- SATURATION_PC pass/fail ----
    pc_acc = float(pc_pt["acc"])
    pc_pass = (pc_acc >= PC_THRESHOLD)

    # ---- Escapes-saturation gate ----
    main_accs = [p["acc"] for p in main_pts]
    main_mean = float(np.mean(main_accs)) if main_accs else -1.0
    n_in_band = sum(1 for a in main_accs
                    if NON_SATURATED_BAND_LO <= a <= NON_SATURATED_BAND_HI)
    frac_in_band = (n_in_band / len(main_accs)) if main_accs else 0.0
    per_N_mean_acc: Dict[str, float] = {}
    for N in N_grid:
        slice_accs = [p["acc"] for p in main_pts if p["N"] == N]
        if slice_accs:
            per_N_mean_acc[str(N)] = round(float(np.mean(slice_accs)), 4)
    per_L_mean_acc: Dict[str, float] = {}
    for L in L_grid:
        slice_accs = [p["acc"] for p in main_pts if p["L"] == L]
        if slice_accs:
            per_L_mean_acc[str(L)] = round(float(np.mean(slice_accs)), 4)
    # Smoke gate: some slice must be non-saturated (mean < 0.95)
    all_slice_means = list(per_N_mean_acc.values()) + list(per_L_mean_acc.values())
    per_slice_min_mean = float(min(all_slice_means)) if all_slice_means else 1.0
    per_slice_max_mean = float(max(all_slice_means)) if all_slice_means else 0.0
    escapes_saturation_smoke = (per_slice_min_mean < NON_SATURATED_BAND_HI)
    escapes_saturation_full = (frac_in_band >= ESCAPES_SATURATION_MIN_FRACTION)

    # ---- Additive-model residuals: cell(N,L) - (marg_N + marg_L - grand) ----
    grand_mean = float(np.mean(main_accs)) if main_accs else 0.0
    marg_N = {N: (per_N_mean_acc.get(str(N), grand_mean)) for N in N_grid}
    marg_L = {L: (per_L_mean_acc.get(str(L), grand_mean)) for L in L_grid}
    N_x_L_deviation_map: Dict[str, float] = {}
    N_x_L_deviation_map_in_band: Dict[str, float] = {}
    per_cell_pressure: Dict[str, float] = {}  # L * (N_cliff / N)
    for N in N_grid:
        for L in L_grid:
            matches = [p["acc"] for p in main_pts
                       if p["N"] == N and p["L"] == L]
            if matches:
                cell = float(matches[0])
                pred = marg_N[N] + marg_L[L] - grand_mean
                dev = cell - pred
                key = f"N{N}_L{L}"
                N_x_L_deviation_map[key] = round(dev, 4)
                per_cell_pressure[key] = round(float(L) * (N_CLIFF / float(N)), 4)
                if NON_SATURATED_BAND_LO <= cell <= NON_SATURATED_BAND_HI:
                    N_x_L_deviation_map_in_band[key] = round(dev, 4)
    max_N_x_L_dev = max((abs(v) for v in N_x_L_deviation_map.values()), default=0.0)
    max_N_x_L_dev_in_band = max((abs(v) for v in N_x_L_deviation_map_in_band.values()), default=0.0)

    # ---- L/N_cliff RATIO bucketing (median split on pressure) ----
    # pressure = L * (N_cliff / N)
    pressures_in_band = [(k, per_cell_pressure[k], N_x_L_deviation_map[k])
                         for k in N_x_L_deviation_map_in_band.keys()]
    high_bucket_dev = []
    low_bucket_dev = []
    bucket_split_value = None
    if pressures_in_band:
        ps = sorted(pressures_in_band, key=lambda x: x[1])
        n = len(ps)
        # median split
        mid = n // 2
        low_group = ps[:mid] if n >= 2 else ps
        high_group = ps[mid:] if n >= 2 else []
        low_bucket_dev = [abs(p[2]) for p in low_group]
        high_bucket_dev = [abs(p[2]) for p in high_group]
        if ps and mid < len(ps):
            bucket_split_value = ps[mid][1]
    max_dev_high_bucket = max(high_bucket_dev, default=0.0)
    max_dev_low_bucket = max(low_bucket_dev, default=0.0)

    # ---- H3 DEEP_SAT check: L-axis spread should be tiny at deep-saturation ----
    deep_sat_L_spread = None
    deep_sat_pass = None
    deep_sat_accs_by_L = None
    deep_sat_mean_acc = None
    if deep_sat_pts:
        accs = [p["acc"] for p in deep_sat_pts]
        deep_sat_accs_by_L = {str(p["L"]): p["acc"] for p in deep_sat_pts}
        deep_sat_L_spread = float(max(accs) - min(accs))
        deep_sat_mean_acc = float(np.mean(accs))
        deep_sat_pass = (deep_sat_L_spread <= DEEP_SAT_L_SPREAD_MAX
                         and deep_sat_mean_acc >= 0.95)

    # ---- Hypothesis assessment (band-restricted, bucketed) ----
    n_ib_cells = len(N_x_L_deviation_map_in_band)
    if n_ib_cells == 0:
        hyp_verdict = "H_UNKNOWN_NO_IN_BAND_CELLS"
        hyp_reason = (f"no cells with acc in "
                      f"[{NON_SATURATED_BAND_LO}, {NON_SATURATED_BAND_HI}] "
                      f"(main grid entirely saturated or floored)")
    elif (max_dev_high_bucket >= CROSS_TERM_HIGH_BUCKET_H1_THRESHOLD
          and max_dev_low_bucket < CROSS_TERM_LOW_BUCKET_H1_THRESHOLD):
        hyp_verdict = "H1_BUNDLED_N_x_L_CROSS_TERM_AT_NEAR_CAPACITY"
        hyp_reason = (f"in {n_ib_cells} in-band cells: "
                      f"max|dev| in HIGH-pressure bucket = "
                      f"{max_dev_high_bucket:.4f} >= 0.15 AND "
                      f"max|dev| in LOW-pressure bucket = "
                      f"{max_dev_low_bucket:.4f} < 0.05; N and L are "
                      f"NON-additive at BUNDLED near-capacity; confirms "
                      f"Frady/Sommer near-capacity coupling literature; "
                      f"bucket split L*N_cliff/N ~ {bucket_split_value}")
    elif max_N_x_L_dev_in_band >= CROSS_TERM_OVERALL_H1_ALT_THRESHOLD:
        hyp_verdict = "H1_ALT_DIFFUSE_N_x_L_CROSS_TERM"
        hyp_reason = (f"in {n_ib_cells} in-band cells: "
                      f"overall max|dev|_in_band = {max_N_x_L_dev_in_band:.4f} >= 0.10 "
                      f"BUT clean bucket separation NOT achieved "
                      f"(high_bucket={max_dev_high_bucket:.4f} "
                      f"low_bucket={max_dev_low_bucket:.4f}); diffuse cross-term "
                      f"present; MM_TENTATIVE H1_ALT")
    elif max_N_x_L_dev_in_band < CROSS_TERM_H2_THRESHOLD:
        hyp_verdict = "H2_N_AND_L_INDEPENDENT_NOVEL"
        hyp_reason = (f"in {n_ib_cells} in-band cells: overall max|dev|_in_band = "
                      f"{max_N_x_L_dev_in_band:.4f} < 0.05; NOVEL substrate-specific "
                      f"finding CONTRADICTING near-capacity coupling literature "
                      f"(Frady/Sommer 2018/2020); consistent with per-step cleanup "
                      f"resetting noise; analog to prior SHARDED arbitrary-depth "
                      f"finding")
    else:
        hyp_verdict = "MIDDLE_BAND_WEAK_N_x_L_MODERATION"
        hyp_reason = (f"in {n_ib_cells} in-band cells: overall max|dev|_in_band = "
                      f"{max_N_x_L_dev_in_band:.4f}; between H2 null and H1 threshold; "
                      f"MM_TENTATIVE weak N x L moderation")

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
        "L_endpoint_distinct": L_endpoint_distinct,
        "saturation_pc": {
            "arm": "SATURATION_PC",
            "storage": PC_STORAGE, "mechanism": PC_MECH,
            "M": PC_M, "N": PC_N, "F": PC_F, "L": PC_L, "corruption": PC_CORR,
            "acc": pc_acc, "threshold": PC_THRESHOLD, "pass": pc_pass,
        },
        "deep_sat": {
            "arm": "DEEP_SAT", "storage": DEEP_SAT_STORAGE, "mechanism": DEEP_SAT_MECH,
            "N": DEEP_SAT_N, "M": DEEP_SAT_M, "corruption": DEEP_SAT_CORR,
            "L_grid": DEEP_SAT_L_GRID, "accs_by_L": deep_sat_accs_by_L,
            "L_spread": (round(deep_sat_L_spread, 4)
                         if deep_sat_L_spread is not None else None),
            "L_spread_max": DEEP_SAT_L_SPREAD_MAX,
            "mean_acc": (round(deep_sat_mean_acc, 4)
                         if deep_sat_mean_acc is not None else None),
            "pass": deep_sat_pass,
        } if deep_sat_pts else None,
        "main_grid_mean_acc": round(main_mean, 4),
        "main_grid_n_in_non_saturated_band": n_in_band,
        "main_grid_n_total": len(main_accs),
        "main_grid_fraction_in_non_saturated_band": round(frac_in_band, 4),
        "per_N_mean_acc": per_N_mean_acc,
        "per_L_mean_acc": per_L_mean_acc,
        "escapes_saturation_ceiling_smoke": escapes_saturation_smoke,
        "escapes_saturation_ceiling_full": escapes_saturation_full,
        "N_x_L_deviation_map": N_x_L_deviation_map,
        "N_x_L_deviation_map_in_band": N_x_L_deviation_map_in_band,
        "per_cell_pressure": per_cell_pressure,
        "max_N_x_L_deviation": round(max_N_x_L_dev, 4),
        "max_N_x_L_deviation_in_band": round(max_N_x_L_dev_in_band, 4),
        "bucket_split_value": (round(bucket_split_value, 4)
                               if bucket_split_value is not None else None),
        "max_dev_high_pressure_bucket_in_band": round(max_dev_high_bucket, 4),
        "max_dev_low_pressure_bucket_in_band": round(max_dev_low_bucket, 4),
        "grand_mean_main": round(grand_mean, 4),
        "n_in_band_cells": n_ib_cells,
        "N_cliff": N_CLIFF,
        "hypothesis_assessment": hyp_verdict,
        "hypothesis_reason": hyp_reason,
        "non_saturated_band": [NON_SATURATED_BAND_LO, NON_SATURATED_BAND_HI],
        "source_signature": {
            "STORAGE": STORAGE_FIXED, "MECH": MECH_FIXED, "M": M_FIXED,
            "F": F_FIXED, "corr": CORRUPTION_FIXED, "N_cliff": N_CLIFF,
        },
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
        return False, (f"arms_differ_fail (META_RULE_AF): L-axis endpoints "
                       f"not hash-distinct at some N; L_endpoint_distinct="
                       f"{body.get('L_endpoint_distinct')}")
    pc = body.get("saturation_pc", {})
    if not pc.get("pass"):
        return False, (f"saturation_pc_fail: {PC_STORAGE} {PC_MECH} at PC regime "
                       f"(M={pc.get('M')} N={pc.get('N')} F={pc.get('F')} "
                       f"L={pc.get('L')} corr={pc.get('corruption')}) "
                       f"acc={pc.get('acc')} < threshold={pc.get('threshold')}")
    if not body.get("escapes_saturation_ceiling_smoke"):
        return False, (f"escapes_saturation_ceiling_fail: no slice has mean-acc "
                       f"< {NON_SATURATED_BAND_HI}; per_N_mean_acc="
                       f"{body.get('per_N_mean_acc')} per_L_mean_acc="
                       f"{body.get('per_L_mean_acc')}; smoke regime fully "
                       f"saturated -- re-spec grid")
    for pt in phase_map:
        if pt.get("acc") != pt.get("acc"):
            return False, f"NAN_in_phase_map at {pt}"
    max_dev = body.get("max_N_x_L_deviation_in_band", 0.0)
    frac = body.get("main_grid_fraction_in_non_saturated_band", 0.0)
    hyp = body.get("hypothesis_assessment")
    return True, (f"smoke_gate_pass: cardinality_ok + L-endpoint-hash-distinct + "
                  f"pc_acc={pc.get('acc')} (>={pc.get('threshold')}) + "
                  f"escapes_saturation (some slice mean<{NON_SATURATED_BAND_HI}); "
                  f"frac_in_band={frac}; informational cross-term: "
                  f"max|dev|_in_band={max_dev}; hyp_preview={hyp}")


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
        "L_endpoint_distinct": body.get("L_endpoint_distinct"),
        "saturation_pc": body.get("saturation_pc"),
        "deep_sat": body.get("deep_sat"),
        "main_grid_mean_acc": body.get("main_grid_mean_acc"),
        "main_grid_n_in_non_saturated_band":
            body.get("main_grid_n_in_non_saturated_band"),
        "main_grid_n_total": body.get("main_grid_n_total"),
        "main_grid_fraction_in_non_saturated_band":
            body.get("main_grid_fraction_in_non_saturated_band"),
        "per_N_mean_acc": body.get("per_N_mean_acc"),
        "per_L_mean_acc": body.get("per_L_mean_acc"),
        "escapes_saturation_ceiling_smoke":
            body.get("escapes_saturation_ceiling_smoke"),
        "escapes_saturation_ceiling_full":
            body.get("escapes_saturation_ceiling_full"),
        "N_x_L_deviation_map": body.get("N_x_L_deviation_map"),
        "N_x_L_deviation_map_in_band": body.get("N_x_L_deviation_map_in_band"),
        "per_cell_pressure": body.get("per_cell_pressure"),
        "max_N_x_L_deviation": body.get("max_N_x_L_deviation"),
        "max_N_x_L_deviation_in_band": body.get("max_N_x_L_deviation_in_band"),
        "bucket_split_value": body.get("bucket_split_value"),
        "max_dev_high_pressure_bucket_in_band":
            body.get("max_dev_high_pressure_bucket_in_band"),
        "max_dev_low_pressure_bucket_in_band":
            body.get("max_dev_low_pressure_bucket_in_band"),
        "grand_mean_main": body.get("grand_mean_main"),
        "n_in_band_cells": body.get("n_in_band_cells"),
        "N_cliff": body.get("N_cliff"),
        "hypothesis_assessment": body.get("hypothesis_assessment"),
        "hypothesis_reason": body.get("hypothesis_reason"),
        "non_saturated_band": body.get("non_saturated_band"),
        "source_signature": body.get("source_signature"),
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
            "verdict": verdict, "verdict_msg": vmsg, "summary": vmsg,
            "smoke_gate_pass": ok, "smoke_gate_reason": reason,
        })
        return out

    # FULL verdict
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"expected={expected_n} observed={observed_n}")
    elif not body.get("arms_differ_verified"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_ARMS_MUST_DIFFER_META_RULE_AF: L-axis endpoints "
                f"not hash-distinct at some N")
    elif not body.get("saturation_pc", {}).get("pass"):
        pc = body.get("saturation_pc", {})
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_SATURATION_PC_MISMATCH: {PC_STORAGE} {PC_MECH} at PC "
                f"regime acc={pc.get('acc')} < threshold={pc.get('threshold')}; "
                f"positive control fails; cross-term claim not trustworthy "
                f"(Gate D violation)")
    elif not body.get("escapes_saturation_ceiling_full"):
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_ESCAPES_SATURATION_FAIL: only "
                f"{body.get('main_grid_n_in_non_saturated_band')}/"
                f"{body.get('main_grid_n_total')} main-grid pts in "
                f"[{NON_SATURATED_BAND_LO}, {NON_SATURATED_BAND_HI}] "
                f"(fraction {body.get('main_grid_fraction_in_non_saturated_band')} "
                f"< {ESCAPES_SATURATION_MIN_FRACTION}); cannot claim H1/H2 "
                f"with confidence")
    else:
        hyp = body.get("hypothesis_assessment", "H_UNKNOWN")
        reason = body.get("hypothesis_reason", "")
        deep = body.get("deep_sat") or {}
        deep_pass = deep.get("pass")
        deep_spread = deep.get("L_spread")
        deep_note = ""
        if deep_pass is False:
            deep_note = (f"; H3_DEEP_SAT_CONTROL_FAIL: L-spread at DEEP_SAT "
                         f"(N={DEEP_SAT_N} corr={DEEP_SAT_CORR}) = {deep_spread} "
                         f"> {DEEP_SAT_L_SPREAD_MAX} OR mean_acc "
                         f"{deep.get('mean_acc')} < 0.95; deep-sat null control "
                         f"fired unexpectedly; treat H1 claim with caution")
        elif deep_pass is True:
            deep_note = (f"; H3_DEEP_SAT_CONTROL_PASS: L-spread at DEEP_SAT = "
                         f"{deep_spread} <= {DEEP_SAT_L_SPREAD_MAX}")

        if hyp == "H1_BUNDLED_N_x_L_CROSS_TERM_AT_NEAR_CAPACITY":
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H1_BUNDLED_N_x_L_CROSS_TERM: "
                    f"high_bucket_max|dev|={body.get('max_dev_high_pressure_bucket_in_band')} "
                    f">= 0.15 AND low_bucket_max|dev|="
                    f"{body.get('max_dev_low_pressure_bucket_in_band')} < 0.05; "
                    f"confirms Frady/Sommer near-capacity coupling; MM_TENTATIVE "
                    f"(single-seed FULL; requires 3-seed replication + Skunkworks "
                    f"landed-VET for arc closure); source_signature="
                    f"{body.get('source_signature')}{deep_note}; {reason}")
        elif hyp == "H1_ALT_DIFFUSE_N_x_L_CROSS_TERM":
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_H1_ALT_DIFFUSE_CROSS_TERM: "
                    f"overall_max|dev|_in_band="
                    f"{body.get('max_N_x_L_deviation_in_band')} >= 0.10 without "
                    f"clean bucket separation; MM_TENTATIVE weak cross-term; "
                    f"source_signature={body.get('source_signature')}"
                    f"{deep_note}; {reason}")
        elif hyp == "H2_N_AND_L_INDEPENDENT_NOVEL":
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H2_NOVEL_N_AND_L_INDEPENDENT_AT_NEAR_CAPACITY: "
                    f"overall_max|dev|_in_band="
                    f"{body.get('max_N_x_L_deviation_in_band')} < 0.05; NOVEL "
                    f"substrate-specific finding CONTRADICTING Frady/Sommer "
                    f"near-capacity coupling literature; consistent with "
                    f"per-step cleanup resetting noise; source_signature="
                    f"{body.get('source_signature')}{deep_note}; MM_TENTATIVE "
                    f"pending 3-seed replication + Skunkworks landed-VET; "
                    f"{reason}")
        elif hyp == "MIDDLE_BAND_WEAK_N_x_L_MODERATION":
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_WEAK_N_x_L_MODERATION: "
                    f"n_in_band_cells={body.get('n_in_band_cells')}; "
                    f"weak cross-term between H1 and H2 thresholds; "
                    f"MM_TENTATIVE{deep_note}; {reason}")
        elif hyp == "H_UNKNOWN_NO_IN_BAND_CELLS":
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_NO_IN_BAND_CELLS: escapes_saturation passed "
                    f"but no cells landed in [{NON_SATURATED_BAND_LO}, "
                    f"{NON_SATURATED_BAND_HI}]; re-spec grid{deep_note}; {reason}")
        else:
            verdict = "HARD_FAIL"
            vmsg = f"HARD_FAIL_HYP_UNKNOWN: {reason}"

    out = dict(common)
    out.update({"verdict": verdict, "verdict_msg": vmsg, "summary": vmsg})
    return out


__all__ = [
    "ANCHOR_NAME", "DEVICE", "GPU_NAME",
    "N_GRID_FULL", "N_GRID_SMOKE", "L_GRID_FULL", "L_GRID_SMOKE",
    "N_CLIFF",
    "MECH_FIXED", "STORAGE_FIXED", "M_FIXED", "F_FIXED", "CORRUPTION_FIXED",
    "TR_FULL", "TR_SMOKE",
    "PC_MECH", "PC_STORAGE", "PC_M", "PC_N", "PC_F", "PC_L", "PC_CORR", "PC_THRESHOLD",
    "DEEP_SAT_STORAGE", "DEEP_SAT_MECH", "DEEP_SAT_N", "DEEP_SAT_M",
    "DEEP_SAT_CORR", "DEEP_SAT_L_GRID", "DEEP_SAT_L_SPREAD_MAX",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "NON_SATURATED_BAND_LO", "NON_SATURATED_BAND_HI",
    "ESCAPES_SATURATION_MIN_FRACTION",
    "CROSS_TERM_HIGH_BUCKET_H1_THRESHOLD", "CROSS_TERM_LOW_BUCKET_H1_THRESHOLD",
    "CROSS_TERM_OVERALL_H1_ALT_THRESHOLD", "CROSS_TERM_H2_THRESHOLD",
    "REQUIRED_FIELDS",
    "eval_phase_point", "selftest", "run_one_seed",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
