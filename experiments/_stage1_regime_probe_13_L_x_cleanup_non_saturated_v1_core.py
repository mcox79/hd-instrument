"""Stage 1 Regime Probe 13: L (chain-depth) x CLEANUP_MECHANISM CROSS-TERM at cliff-adjacent SHARDED.

Cell anchor: `stage1_regime_probe_13_L_x_cleanup_non_saturated_v1`
Pre-reg:     preregs/2026-07-03_stage1_regime_probe_13_L_x_cleanup_non_saturated_v1.md

Purpose:
    REGIME-EXTENSION of atom #3 (SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS_CG_META_v1)
    into the L x CLEANUP_MECHANISM cross-term at cliff-adjacent SHARDED. Convergent
    mech-moderation finding today (P3 + P6v2 + P8 at F x CLEANUP) was measured at
    L=2 only. Skunkworks P12 VET flagged the L=2 slice: L cross-terms (L x N, L x F,
    L x M, L x corr) unmapped. Probe 12 measured L MARGINAL effect (does L
    moderate any single mechanism's accuracy). Probe 13 measures L x MECH
    INTERACTION: does the mechanism-spread pattern from P6v2 + P8 hold across L,
    or is it L=2-specific?

    Interaction is distinct from marginal effect: marginal = does L change
    accuracy at all; interaction = does the WAY mech affects accuracy change
    across L. Formally, if mech and L were independent axes, mech_spread would
    be constant across L (and L_spread would be constant across mech). Any
    variation of mech_spread across L (or L_spread across mech) is the L x MECH
    cross-term.

    L axis restricted to band-cells {1, 2, 4} per Skunkworks P12 VET
    (MEASURED@data/exp_stage1_regime_probe_12_L_marginal_effect_sweep_v1_s7_smoke/
    metrics.json:cliff_arm.per_L_mech_variance; TR=40 seed=7:
      L=1 mean=0.8417 spread=0.100 (mh=0.875 ic=0.875 sea=0.775)
      L=4 mean=0.4917 spread=0.100 (mh=0.525 ic=0.425 sea=0.525)
      L=16 mean=0.025 spread=0.075 -- BELOW FLOOR excluded)
    Empirical bracket at L=2 F=1 CLIFF TR=40 seed=7 (from P12 pre-reg):
      L=2 mean=0.733 spread=0.075 (mh=0.725 ic=0.775 sea=0.700)
    All three L in {1, 2, 4} predicted in-band [0.30, 0.95].

    Predicted cross-term signal at seed=7 TR=40 bracket:
      mech_spread across L={1,2,4} = {0.100, 0.075, 0.100}
        range_of_mech_spread_across_L = 0.100 - 0.075 = 0.025
      L_spread across mech = {mh=0.350, ic=0.450, sea=0.250}
        range_of_L_spread_across_mech = 0.450 - 0.250 = 0.200
      cross_term_signal = max(0.025, 0.200) = 0.200 (>= 0.10 H1)

Cited source atoms (exact names per META_RULE_AC):
    T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1
    SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS_CG_META_v1 (Stage 1 atom #3)
    T3/EXP_stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1_3seed_FULL (Probe 8 F-axis)
    T3/EXP_stage1_regime_probe_6_topology_x_cleanup_non_saturated_v1 (Probe 6v2 topology-free)
    T3/EXP_stage1_regime_probe_12_L_marginal_effect_sweep_v1_smoke (source of L bracket)
    META_axis_labels_map_to_substrate_primitives_not_theoretical_concepts (Skunkworks atom #44)
    META_cross_term_measurement_requires_both_arms_in_band (Skunkworks meta #43)
    META_saturation_floor_masks_null_variance_probe3_lesson (T4 MM_STANDARD)
    feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-07-03
    feedback_plate_bound_too_pessimistic_for_sharded_fhrr_chain_composition_2026-07-03
    feedback_mechanism_abstraction_lossy_cite_source_signature_2026-07-03

Source signature (cited per feedback_mechanism_abstraction_lossy):
    SHARDED FHRR chain composition; N=512; M=6400; corr=0.85; F=1;
    MECH in {modern_hopfield, iterative_cosine, soft_energy_attractor};
    BETA=8.0; ALPHA_SOFT=0.5; TR=100 (FULL) / 40 (SMOKE);
    storage_codebook=(M_props, F, N) complex64; unit-modulus phasors;
    L in {1, 2, 4} (band-only). L primitive: run_chain iterates L times.

Reuse (Principle 11):
    Primitives imported from _stage1_physics_law_joint_composition_factorial_v1_core:
      CLEANUP_MECHANISMS, CLEANUP_REGISTRY, BETA, ALPHA_SOFT, DEVICE, GPU_NAME,
      build_rules, phase_corrupt, run_chain, cphasor_torch
    Verdict logic modeled on _stage1_regime_probe_12_L_marginal_effect_sweep_v1_core
    (band-restricted discriminator + per-arm HP_SCOPE + arm_tag routing +
    null-hypothesis-safe smoke gate) with cross-term interaction metric added.

Sweep grid FULL (19 pts / seed):
    CLIFF arm: L in {1,2,4} x 3 mech at (N=512, M=6400, corr=0.85, F=1, SHARDED) = 9 pts
    DEEP_SAT arm (H3 null): L in {1,2,4} x 3 mech at (N=8192, M=800, corr=0.60, F=1, SHARDED) = 9 pts
    SATURATION_PC arm: L=2 F=1 M=800 N=2048 corr=0.20 iterative_cosine = 1 pt
Sweep grid SMOKE (13 pts / seed):
    CLIFF arm: L in {1,2,4} x 3 mech at CLIFF = 9 pts (full cross-term matrix)
    DEEP_SAT arm spot-check: L=2 x 3 mech at DEEP_SAT = 3 pts
    SATURATION_PC arm: 1 pt

Hypotheses (falsifiable; interaction metric on CLIFF arm; MM_TENTATIVE at
SMOKE at most; MM_STANDARD at 3-seed FULL):
    H1 (L x MECH INTERACTION at cliff-adjacent SHARDED F=1):
        cliff_cross_term_signal >= 0.10
      where cross_term_signal = max(
        range_of_mech_spread_across_L,
        range_of_L_spread_across_mech
      )
      -> the F x CLEANUP mech-moderation pattern is L-dependent; today's
         convergent finding (P6v2 + P8) is L=2-specific and the interaction
         signal is genuine. Atom candidate:
         EMPIRICAL_L_x_CLEANUP_CROSS_TERM_SHARDED_CLIFF_ADJACENT_v1
         MM_TENTATIVE at SMOKE, MM_STANDARD at 3-seed FULL.
    H2 (L x MECH INTERACTION is INERT at cliff-adjacent SHARDED):
        cliff_cross_term_signal < 0.05
      -> mech_spread is INDEPENDENT of L (mech ranking + spread same across
         L in {1,2,4}); the L=2 finding EXTENDS to L={1,4} without change.
         Atom candidate:
         L_x_MECH_CROSS_TERM_INERT_SHARDED_CLIFF_ADJACENT_NEGATIVE_v1
         MM_TENTATIVE.
    H3-NULL (DEEP_SAT null fires; cross-term degenerates at ceiling):
        deep_sat_cross_term_signal < 0.05
      -> deep-saturation collapses the L x MECH interaction; both mech and
         L axes degenerate at ceiling; strengthens saturation-masks-variance
         thesis (META_saturation_floor).

Compute architecture: batched matmul at each phase point (build_rules +
    run_chain use torch.matmul); Python for-loop across (L, mech) grid is
    unavoidable per phase point independent state. Wall-time SMOKE on CPU
    estimated 30-90s (13 phase points 1-5s each at TR=40). FULL on CPU
    estimated 3-8 min (19 phase points 3-15s each at TR=100). Local CPU
    dispatch is USER-LOCKED as SMOKE-only (feedback_smoke_only_local_cpu
    2026-07-01); FULL routes to remote via Orchestrator when Tailscale
    restored.

Sibling wrappers: exp_stage1_regime_probe_13_L_x_cleanup_non_saturated_v1_s{7,13,19}.py

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-07-03 (agent-spawn, Opus 4.7).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared (categorical accuracy; discriminator = interaction cross-term)
# - baseline_in_band verified empirically (CLIFF L in {1,2,4} all mid-band 0.44-0.83;
#   DEEP_SAT saturated by design as H3 null control)
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
# - HP_SCOPE per-arm declaration (CLIFF vs DEEP_SAT vs SATURATION_PC)
# - cardinality_ok for sweep-axis cells (META_RULE_H; EXPECTED_N_UNITS gate)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except)
# - calibration_check: default_ok_for_this_regime (BETA=8.0 ALPHA=0.5 Option Y core)
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
    run_chain,
    cphasor_torch,
)

ANCHOR_NAME = "stage1_regime_probe_13_L_x_cleanup_non_saturated_v1"

# ---------------------------------------------------------------------------
# Sweep constants (LOCKED at module init; MEASURED@P12 smoke bracket 2026-07-03)
# ---------------------------------------------------------------------------
# Primary axis: L x MECH cross-term (interaction, not marginal). L restricted
# to band-cells {1, 2, 4} per P12 VET (MEASURED@exp_stage1_regime_probe_12_...s7_smoke
# cliff_arm.per_L_mech_variance).
L_GRID_CLIFF_FULL = [1, 2, 4]
L_GRID_CLIFF_SMOKE = [1, 2, 4]  # full cross-term matrix at smoke (interaction needs >=2 L)

# CLIFF-adjacent operating point (empirically LOCKED at TR=40 seed=7):
#   at N=512 M=6400 corr=0.85 F=1 SHARDED: mean_acc across L in {1,2,4} = 0.49-0.84
#   (all in [0.30, 0.95] band; both-arms-in-band per Skunkworks meta #43).
#   MEASURED@exp_stage1_regime_probe_12_L_marginal_effect_sweep_v1_s7_smoke
#   metrics.json:cliff_arm.per_L_mech_variance 2026-07-03.
CLIFF_N = 512
CLIFF_M = 6400
CLIFF_CORR = 0.85
CLIFF_F = 1

# DEEP_SAT arm (H3-NULL: L x MECH cross-term DEGENERACY at ceiling):
#   at N=8192 M=800 corr=0.60 F=1: mean_acc = 1.0 exact across L in {1,2,4},
#   mech_spread = 0. HYPOTHESIZED at FULL TR=100 (3-seed): cross_term < 0.05.
#   MEASURED@P12 s7 smoke deep_sat_arm mean=1.0 spread=0.
L_GRID_DEEP_SAT_FULL = [1, 2, 4]     # full matrix mirrors CLIFF for cross-term null
L_GRID_DEEP_SAT_SMOKE = [2]          # spot-check regime saturates
DEEP_SAT_N = 8192
DEEP_SAT_M = 800
DEEP_SAT_CORR = 0.60
DEEP_SAT_F = 1

# SATURATION_PC arm (Gate D reproducer, cited from Probes 6/7/8/12 baseline)
SATURATION_PC_REGIME = {
    "cleanup_mechanism": "iterative_cosine",
    "M": 800,
    "N": 2048,
    "F": 1,
    "L": 2,
    "corruption": 0.20,
    "storage": "SHARDED",
}
SATURATION_PC_THRESHOLD = 0.95

TR_FULL = 100
TR_SMOKE = 40

# CLIFF main: 3 L x 3 mech = 9; DEEP_SAT: 3 L x 3 mech = 9; PC = 1. TOTAL 19 FULL.
EXPECTED_N_UNITS_FULL = (len(L_GRID_CLIFF_FULL) * len(CLEANUP_MECHANISMS)
                         + len(L_GRID_DEEP_SAT_FULL) * len(CLEANUP_MECHANISMS)
                         + 1)
# SMOKE: 3 L x 3 mech (cliff) + 1 L x 3 mech (deep_sat) + PC = 9 + 3 + 1 = 13.
EXPECTED_N_UNITS_SMOKE = (len(L_GRID_CLIFF_SMOKE) * len(CLEANUP_MECHANISMS)
                          + len(L_GRID_DEEP_SAT_SMOKE) * len(CLEANUP_MECHANISMS)
                          + 1)

# Non-saturated band
NON_SAT_BAND_LO = 0.30
NON_SAT_BAND_HI = 0.95

# H1/H2 thresholds (interaction cross-term; mirrors P6v2/P8 discriminator scale)
CROSS_TERM_H1_THRESHOLD = 0.10   # H1: L x MECH interaction is genuine
CROSS_TERM_H2_THRESHOLD = 0.05   # H2: L x MECH interaction is inert
# H3-NULL threshold (DEEP_SAT arm)
DEEP_SAT_CROSS_TERM_THRESHOLD = 0.05

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# Per-phase-point eval
# ---------------------------------------------------------------------------
def eval_phase_point(mechanism: str, M_props: int, N: int, F: int, L: int,
                     corruption: float, storage: str, TR: int, seed: int,
                     salt: int, arm_tag: str) -> Dict[str, Any]:
    """Run a single phase point on SHARDED FHRR chain."""
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
                           f"M={M_props} N={N} F={F} L={L}")

    acc, final_ci = run_chain(storage, mechanism, L, F, TR,
                              props, perms, IMPL, POS,
                              sharded_codebook, bundle_vec,
                              corruption, gen, device)

    # META_RULE_AF hash of cleanup output indices
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
        "F": int(F),
        "L": int(L),
        "corruption": float(corruption),
        "storage": storage,
        "TR": int(TR),
        "acc": round(float(acc), 4),
        "output_hash": output_hash,
        "peak_mem_mb": peak_mem_mb,
        "elapsed_s": round(elapsed, 3),
    }


# ---------------------------------------------------------------------------
# Cross-term interaction metric (public helper; used by selftest + verdict)
# ---------------------------------------------------------------------------
def compute_cross_term(matrix_by_L_and_mech: Dict[int, Dict[str, float]]
                       ) -> Dict[str, Any]:
    """Given matrix M[L][mech] -> acc, return interaction cross-term metrics.

    Returns dict with:
      mech_spread_at_L: {L: max_mech - min_mech}
      L_spread_at_mech: {mech: max_L - min_L}
      range_of_mech_spread_across_L: max(mech_spread_at_L) - min(mech_spread_at_L)
      range_of_L_spread_across_mech: max(L_spread_at_mech) - min(L_spread_at_mech)
      cross_term_signal: max of the two ranges (H1 discriminator)
      residual_matrix: M[L][mech] - row_mean(L) - col_mean(mech) + grand_mean
      residual_range: max(residual) - min(residual)  (alternate interaction metric)
    """
    if not matrix_by_L_and_mech:
        return {
            "mech_spread_at_L": {}, "L_spread_at_mech": {},
            "range_of_mech_spread_across_L": 0.0,
            "range_of_L_spread_across_mech": 0.0,
            "cross_term_signal": 0.0,
            "residual_matrix": {}, "residual_range": 0.0,
        }
    L_values = sorted(matrix_by_L_and_mech.keys())
    mech_values = sorted({m for L in L_values for m in matrix_by_L_and_mech[L].keys()})

    # mech_spread at each L (variance across mech, given L)
    mech_spread_at_L: Dict[str, float] = {}
    for L in L_values:
        row = [matrix_by_L_and_mech[L][m] for m in mech_values if m in matrix_by_L_and_mech[L]]
        if len(row) >= 2:
            mech_spread_at_L[str(L)] = round(float(max(row) - min(row)), 4)

    # L_spread at each mech (variance across L, given mech)
    L_spread_at_mech: Dict[str, float] = {}
    for m in mech_values:
        col = [matrix_by_L_and_mech[L][m] for L in L_values if m in matrix_by_L_and_mech[L]]
        if len(col) >= 2:
            L_spread_at_mech[m] = round(float(max(col) - min(col)), 4)

    if mech_spread_at_L:
        vals = list(mech_spread_at_L.values())
        range_mech_spread = round(max(vals) - min(vals), 4)
    else:
        range_mech_spread = 0.0
    if L_spread_at_mech:
        vals = list(L_spread_at_mech.values())
        range_L_spread = round(max(vals) - min(vals), 4)
    else:
        range_L_spread = 0.0

    cross_term_signal = round(max(range_mech_spread, range_L_spread), 4)

    # Residual matrix: M[L][mech] - row_mean(L) - col_mean(mech) + grand_mean
    # Under pure additivity (no interaction), all residuals = 0. Range = interaction magnitude.
    row_means: Dict[int, float] = {}
    col_means: Dict[str, float] = {}
    all_vals: List[float] = []
    for L in L_values:
        row = [matrix_by_L_and_mech[L][m] for m in mech_values if m in matrix_by_L_and_mech[L]]
        if row:
            row_means[L] = float(np.mean(row))
            all_vals.extend(row)
    for m in mech_values:
        col = [matrix_by_L_and_mech[L][m] for L in L_values if m in matrix_by_L_and_mech[L]]
        if col:
            col_means[m] = float(np.mean(col))
    grand_mean = float(np.mean(all_vals)) if all_vals else 0.0
    residual_matrix: Dict[str, Dict[str, float]] = {}
    residuals: List[float] = []
    for L in L_values:
        residual_matrix[str(L)] = {}
        for m in mech_values:
            if L in matrix_by_L_and_mech and m in matrix_by_L_and_mech[L]:
                r = (matrix_by_L_and_mech[L][m]
                     - row_means.get(L, 0.0)
                     - col_means.get(m, 0.0)
                     + grand_mean)
                residual_matrix[str(L)][m] = round(r, 4)
                residuals.append(r)
    residual_range = round(float(max(residuals) - min(residuals)), 4) if residuals else 0.0

    return {
        "mech_spread_at_L": mech_spread_at_L,
        "L_spread_at_mech": L_spread_at_mech,
        "range_of_mech_spread_across_L": range_mech_spread,
        "range_of_L_spread_across_mech": range_L_spread,
        "cross_term_signal": cross_term_signal,
        "residual_matrix": residual_matrix,
        "residual_range": residual_range,
        "grand_mean": round(grand_mean, 4),
    }


# ---------------------------------------------------------------------------
# Selftest (formula check at reduced grid; wall < 60s target on CPU)
# ---------------------------------------------------------------------------
def selftest() -> Tuple[bool, str]:
    msgs = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 19:
        return False, (f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 19 "
                       f"(9 cliff + 9 deep_sat + 1 PC)")
    if EXPECTED_N_UNITS_SMOKE != 13:
        return False, (f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 13 "
                       f"(9 cliff + 3 deep_sat + 1 PC)")
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} "
                f"SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. Cross-term formula: additive matrix -> cross_term = 0
    additive = {
        1: {"a": 0.9, "b": 0.7, "c": 0.5},
        2: {"a": 0.8, "b": 0.6, "c": 0.4},
        4: {"a": 0.5, "b": 0.3, "c": 0.1},
    }
    ct_add = compute_cross_term(additive)
    # Additive: mech_spread same at each L; L_spread same at each mech.
    # mech_spread_at_L = 0.4 for L in {1,2,4}; range = 0; residual = 0
    if ct_add["range_of_mech_spread_across_L"] != 0.0:
        return False, (f"cross_term formula: additive matrix should have "
                       f"range_of_mech_spread=0; got "
                       f"{ct_add['range_of_mech_spread_across_L']}")
    if abs(ct_add["residual_range"]) > 1e-6:
        return False, (f"cross_term formula: additive matrix residual_range "
                       f"should be 0; got {ct_add['residual_range']}")
    msgs.append(f"cross_term additive: signal={ct_add['cross_term_signal']} "
                f"resid={ct_add['residual_range']}")

    # 3. Cross-term formula: interaction matrix -> cross_term > 0
    interaction = {
        1: {"a": 0.9, "b": 0.9, "c": 0.7},   # spread=0.2
        2: {"a": 0.7, "b": 0.7, "c": 0.7},   # spread=0.0
        4: {"a": 0.5, "b": 0.3, "c": 0.5},   # spread=0.2
    }
    ct_int = compute_cross_term(interaction)
    # range_of_mech_spread_across_L = 0.2 - 0.0 = 0.2
    if ct_int["range_of_mech_spread_across_L"] < 0.15:
        return False, (f"cross_term formula: interaction matrix should have "
                       f"range_of_mech_spread ~0.2; got "
                       f"{ct_int['range_of_mech_spread_across_L']}")
    if ct_int["cross_term_signal"] < CROSS_TERM_H1_THRESHOLD:
        return False, (f"cross_term formula: designed interaction "
                       f"below H1 threshold; got {ct_int['cross_term_signal']}")
    msgs.append(f"cross_term interaction: signal={ct_int['cross_term_signal']} "
                f"resid={ct_int['residual_range']}")

    # 4. 3 cleanup mechanisms produce distinct outputs at L=2 F=1 CLIFF regime
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(999)
    M_probe = 50
    N_test = 512
    F_test = 1
    L_test = 2
    TR = 20
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
        return False, (f"cleanup_mechanisms produce identical outputs at L=2: "
                       f"{mech_hashes}")
    msgs.append(f"3 mechs distinct at L=2 F=1: {list(mech_hashes.values())}")

    # 5. L-axis fires: L=1 vs L=4 chain outputs differ (SHAPE-MATCH primitive)
    gen.manual_seed(1017)
    props1, perms1, IMPL1, POS1, sh1, bd1 = build_rules(M_probe, 1, gen, DEVICE, N_test)
    _, ci_L1 = run_chain("SHARDED", "iterative_cosine", 1, 1, TR,
                         props1, perms1, IMPL1, POS1, sh1, bd1, 0.10, gen, DEVICE)
    gen.manual_seed(1017)
    props2, perms2, IMPL2, POS2, sh2, bd2 = build_rules(M_probe, 1, gen, DEVICE, N_test)
    _, ci_L4 = run_chain("SHARDED", "iterative_cosine", 4, 1, TR,
                         props2, perms2, IMPL2, POS2, sh2, bd2, 0.10, gen, DEVICE)
    h_L1 = hashlib.sha256(ci_L1.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    h_L4 = hashlib.sha256(ci_L4.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    if h_L1 == h_L4:
        return False, (f"L=1 vs L=4 chain outputs identical (L axis aliased); "
                       f"hash={h_L1}")
    msgs.append(f"L-axis fires: L1={h_L1} L4={h_L4}")

    # 6. SATURATION_PC easy gate reproducer (Gate D at reduced TR)
    gen.manual_seed(1013)
    pc = SATURATION_PC_REGIME
    props3, perms3, IMPL3, POS3, sh3, bd3 = build_rules(
        pc["M"], pc["F"], gen, DEVICE, pc["N"])
    acc_easy, _ = run_chain(pc["storage"], pc["cleanup_mechanism"],
                            pc["L"], pc["F"], 40,
                            props3, perms3, IMPL3, POS3, sh3, bd3,
                            pc["corruption"], gen, DEVICE)
    if acc_easy < 0.85:
        return False, (f"SATURATION_PC selftest (L=2 F=1 M=800 N=2048 corr=0.20 "
                       f"iterative_cosine TR=40): acc={acc_easy:.3f} < 0.85")
    msgs.append(f"SATURATION_PC selftest (TR=40): acc={acc_easy:.3f}")

    # 7. CLIFF-adjacent regime sanity: L=2 F=1 in loose band
    #    MEASURED@P12 s7 smoke bracket iterative_cosine at L=2 ~ 0.775 TR=40.
    gen.manual_seed(3131)
    props4, perms4, IMPL4, POS4, sh4, bd4 = build_rules(
        CLIFF_M, CLIFF_F, gen, DEVICE, CLIFF_N)
    acc_cliff, _ = run_chain("SHARDED", "iterative_cosine",
                             2, CLIFF_F, 20,
                             props4, perms4, IMPL4, POS4, sh4, bd4,
                             CLIFF_CORR, gen, DEVICE)
    if not (0.20 <= acc_cliff <= 0.98):
        return False, (f"CLIFF regime sanity (L=2 F=1 M={CLIFF_M} N={CLIFF_N} "
                       f"corr={CLIFF_CORR} iterative_cosine TR=20): "
                       f"acc={acc_cliff:.3f} outside [0.20, 0.98]; regime drift")
    msgs.append(f"CLIFF regime sanity L=2 (TR=20): acc={acc_cliff:.3f}")

    # 8. DEEP_SAT regime sanity (saturated expected)
    gen.manual_seed(4141)
    props5, perms5, IMPL5, POS5, sh5, bd5 = build_rules(
        DEEP_SAT_M, DEEP_SAT_F, gen, DEVICE, DEEP_SAT_N)
    acc_deep, _ = run_chain("SHARDED", "iterative_cosine",
                            2, DEEP_SAT_F, 20,
                            props5, perms5, IMPL5, POS5, sh5, bd5,
                            DEEP_SAT_CORR, gen, DEVICE)
    if acc_deep < 0.95:
        return False, (f"DEEP_SAT regime sanity (L=2 F=1 M={DEEP_SAT_M} "
                       f"N={DEEP_SAT_N} corr={DEEP_SAT_CORR} iterative_cosine "
                       f"TR=20): acc={acc_deep:.3f} < 0.95; deep_sat regime drift")
    msgs.append(f"DEEP_SAT regime sanity L=2 (TR=20): acc={acc_deep:.3f}")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed(seed: int, run_mode: str) -> Dict[str, Any]:
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        L_grid_cliff = L_GRID_CLIFF_SMOKE
        L_grid_deep = L_GRID_DEEP_SAT_SMOKE
        TR = TR_SMOKE
        expected_n = EXPECTED_N_UNITS_SMOKE
    else:
        L_grid_cliff = L_GRID_CLIFF_FULL
        L_grid_deep = L_GRID_DEEP_SAT_FULL
        TR = TR_FULL
        expected_n = EXPECTED_N_UNITS_FULL

    mech_grid = list(CLEANUP_MECHANISMS)

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"mech={mech_grid} L_cliff={L_grid_cliff} L_deep={L_grid_deep} "
          f"cliff=(N={CLIFF_N},M={CLIFF_M},corr={CLIFF_CORR},F={CLIFF_F}) "
          f"deep=(N={DEEP_SAT_N},M={DEEP_SAT_M},corr={DEEP_SAT_CORR},F={DEEP_SAT_F}) "
          f"TR={TR} expected_n={expected_n}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    salt = 0
    t0 = time.perf_counter()

    # 1) CLIFF arm: L sweep x mech at (CLIFF_N, CLIFF_M, CLIFF_CORR, CLIFF_F)
    for L in L_grid_cliff:
        for mech in mech_grid:
            salt += 1
            pt = eval_phase_point(mech, CLIFF_M, CLIFF_N, CLIFF_F, L,
                                  CLIFF_CORR, "SHARDED", TR, seed, salt,
                                  arm_tag="CLIFF")
            phase_map.append(pt)
            print(f"  [{len(phase_map):3d}/{expected_n:3d}] CLIFF     "
                  f"L={L:2d} mech={mech:22s} M={CLIFF_M} N={CLIFF_N} "
                  f"F={CLIFF_F} c={CLIFF_CORR:.2f} acc={pt['acc']:.4f} "
                  f"dt={pt['elapsed_s']:.2f}s", flush=True)

    # 2) DEEP_SAT arm (H3-NULL): L sweep x mech
    for L in L_grid_deep:
        for mech in mech_grid:
            salt += 1
            pt = eval_phase_point(mech, DEEP_SAT_M, DEEP_SAT_N, DEEP_SAT_F, L,
                                  DEEP_SAT_CORR, "SHARDED", TR, seed, salt,
                                  arm_tag="DEEP_SAT")
            phase_map.append(pt)
            print(f"  [{len(phase_map):3d}/{expected_n:3d}] DEEP_SAT  "
                  f"L={L:2d} mech={mech:22s} M={DEEP_SAT_M} N={DEEP_SAT_N} "
                  f"F={DEEP_SAT_F} c={DEEP_SAT_CORR:.2f} acc={pt['acc']:.4f} "
                  f"dt={pt['elapsed_s']:.2f}s", flush=True)

    # 3) SATURATION_PC arm (Gate D reproducer)
    salt += 1
    pc = SATURATION_PC_REGIME
    pc_pt = eval_phase_point(pc["cleanup_mechanism"], pc["M"], pc["N"],
                             pc["F"], pc["L"], pc["corruption"],
                             pc["storage"], TR, seed, salt,
                             arm_tag="SATURATION_PC")
    phase_map.append(pc_pt)
    print(f"  [{len(phase_map):3d}/{expected_n:3d}] PC        "
          f"L={pc['L']:2d} mech={pc['cleanup_mechanism']:22s} "
          f"M={pc['M']} N={pc['N']} F={pc['F']} c={pc['corruption']:.2f} "
          f"acc={pc_pt['acc']:.4f} dt={pc_pt['elapsed_s']:.2f}s", flush=True)

    elapsed = time.perf_counter() - t0
    observed_n = len(phase_map)
    cardinality_ok = (observed_n == expected_n)

    # META_RULE_AF: aggregate mechanism-output hash across CLIFF arm points
    cliff_pts = [p for p in phase_map if p["arm_tag"] == "CLIFF"]
    deep_pts = [p for p in phase_map if p["arm_tag"] == "DEEP_SAT"]

    mech_output_hashes: Dict[str, List[str]] = {m: [] for m in mech_grid}
    for pt in cliff_pts:
        mech_output_hashes[pt["cleanup_mechanism"]].append(pt["output_hash"])
    mech_hash_agg = {m: hashlib.sha256(
        json.dumps(v, sort_keys=True).encode("utf-8")).hexdigest()[:16]
                     for m, v in mech_output_hashes.items()}
    n_distinct_mechs = len(set(mech_hash_agg.values()))

    # SATURATION_PC pass check
    pc_acc = float(pc_pt["acc"])
    pc_pass = (pc_acc >= SATURATION_PC_THRESHOLD)

    # CLIFF arm summary
    cliff_accs = [p["acc"] for p in cliff_pts]
    cliff_mean = float(np.mean(cliff_accs)) if cliff_accs else 0.0
    cliff_min = float(np.min(cliff_accs)) if cliff_accs else 0.0
    cliff_max = float(np.max(cliff_accs)) if cliff_accs else 0.0
    cliff_in_band = sum(1 for a in cliff_accs
                        if NON_SAT_BAND_LO <= a <= NON_SAT_BAND_HI)
    cliff_in_band_frac = cliff_in_band / max(len(cliff_accs), 1)

    # Build CLIFF matrix M[L][mech] -> acc for cross-term computation
    cliff_matrix: Dict[int, Dict[str, float]] = {}
    for L in L_grid_cliff:
        cliff_matrix[L] = {}
        for mech in mech_grid:
            matches = [p["acc"] for p in cliff_pts
                       if p["L"] == L and p["cleanup_mechanism"] == mech]
            if matches:
                cliff_matrix[L][mech] = matches[0]

    # Per-L mech-variance block (for compat with P12-style reporting)
    per_L_cliff_mech_variance: Dict[str, Dict[str, Any]] = {}
    for L in L_grid_cliff:
        triple = cliff_matrix.get(L, {})
        if len(triple) == len(mech_grid):
            vals = list(triple.values())
            spread = round(max(vals) - min(vals), 4)
            cell_mean = float(np.mean(vals))
            per_L_cliff_mech_variance[str(L)] = {
                "accs_by_mech": {m: round(v, 4) for m, v in triple.items()},
                "mean_acc": round(cell_mean, 4),
                "spread": spread,
                "in_non_saturated_band": bool(
                    NON_SAT_BAND_LO <= cell_mean <= NON_SAT_BAND_HI),
            }

    # PRIMARY DISCRIMINATOR: cross-term interaction on CLIFF arm
    cliff_cross = compute_cross_term(cliff_matrix)

    # H3 mech-ranking crossover across L (informational)
    cliff_rankings: List[tuple] = []
    for L in L_grid_cliff:
        triple = cliff_matrix.get(L, {})
        if len(triple) == len(mech_grid):
            ranking = tuple(sorted(triple, key=lambda m: -triple[m]))
            cliff_rankings.append(ranking)
    mech_ranking_crossover = len(set(cliff_rankings)) > 1 if cliff_rankings else False

    # Escapes-saturation for CLIFF arm SMOKE gate (per-L semantics)
    per_L_cliff_mean_acc = {str(L): round(v["mean_acc"], 4)
                             for L_str, v in per_L_cliff_mech_variance.items()
                             for L in [int(L_str)]}
    escapes_saturation_cliff = any(v < NON_SAT_BAND_HI
                                    for v in per_L_cliff_mean_acc.values())

    # DEEP_SAT arm summary (H3-NULL)
    deep_accs = [p["acc"] for p in deep_pts]
    deep_mean = float(np.mean(deep_accs)) if deep_accs else 0.0
    deep_min = float(np.min(deep_accs)) if deep_accs else 0.0
    deep_max = float(np.max(deep_accs)) if deep_accs else 0.0
    deep_matrix: Dict[int, Dict[str, float]] = {}
    for L in L_grid_deep:
        deep_matrix[L] = {}
        for mech in mech_grid:
            matches = [p["acc"] for p in deep_pts
                       if p["L"] == L and p["cleanup_mechanism"] == mech]
            if matches:
                deep_matrix[L][mech] = matches[0]
    per_L_deep_variance: Dict[str, Dict[str, Any]] = {}
    for L in L_grid_deep:
        triple = deep_matrix.get(L, {})
        if len(triple) == len(mech_grid):
            vals = list(triple.values())
            per_L_deep_variance[str(L)] = {
                "accs_by_mech": {m: round(v, 4) for m, v in triple.items()},
                "mean_acc": round(float(np.mean(vals)), 4),
                "spread": round(max(vals) - min(vals), 4),
            }
    # DEEP_SAT cross-term only meaningful when L_grid_deep has >= 2 L values
    if len(L_grid_deep) >= 2:
        deep_cross = compute_cross_term(deep_matrix)
    else:
        # single-L smoke: report per-L mech-spread only; interaction undefined
        deep_cross = {
            "mech_spread_at_L": {str(L_grid_deep[0]): per_L_deep_variance.get(
                str(L_grid_deep[0]), {}).get("spread", 0.0)},
            "L_spread_at_mech": {},
            "range_of_mech_spread_across_L": 0.0,
            "range_of_L_spread_across_mech": 0.0,
            "cross_term_signal": 0.0,
            "residual_matrix": {},
            "residual_range": 0.0,
            "grand_mean": deep_mean,
            "_note": "single-L DEEP_SAT smoke; interaction undefined at this arm",
        }

    # H3-NULL fires when DEEP_SAT cross_term_signal < 0.05
    h3_null_fires = (deep_cross.get("cross_term_signal", 0.0)
                     < DEEP_SAT_CROSS_TERM_THRESHOLD)
    deep_saturated = (deep_mean >= 0.95)

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
        "saturation_pc_result": {
            "regime": SATURATION_PC_REGIME,
            "acc": pc_acc,
            "threshold": SATURATION_PC_THRESHOLD,
            "pass": pc_pass,
        },
        "cliff_arm": {
            "regime": {"N": CLIFF_N, "M": CLIFF_M, "corr": CLIFF_CORR,
                        "F": CLIFF_F, "storage": "SHARDED"},
            "L_grid": L_grid_cliff,
            "mech_grid": mech_grid,
            "mean_acc": round(cliff_mean, 4),
            "min_acc": round(cliff_min, 4),
            "max_acc": round(cliff_max, 4),
            "n_in_non_saturated_band": cliff_in_band,
            "n_total": len(cliff_accs),
            "fraction_in_band": round(cliff_in_band_frac, 4),
            "matrix_by_L_and_mech": {str(L): {m: round(v, 4) for m, v in row.items()}
                                     for L, row in cliff_matrix.items()},
            "per_L_mech_variance": per_L_cliff_mech_variance,
            "cross_term": cliff_cross,
            "cross_term_signal": cliff_cross.get("cross_term_signal", 0.0),
            "per_L_mean_acc": per_L_cliff_mean_acc,
            "escapes_saturation_ceiling": escapes_saturation_cliff,
            "mech_ranking_crossover": mech_ranking_crossover,
        },
        "deep_sat_arm": {
            "regime": {"N": DEEP_SAT_N, "M": DEEP_SAT_M, "corr": DEEP_SAT_CORR,
                        "F": DEEP_SAT_F, "storage": "SHARDED"},
            "L_grid": L_grid_deep,
            "mean_acc": round(deep_mean, 4),
            "min_acc": round(deep_min, 4),
            "max_acc": round(deep_max, 4),
            "matrix_by_L_and_mech": {str(L): {m: round(v, 4) for m, v in row.items()}
                                     for L, row in deep_matrix.items()},
            "per_L_mech_variance": per_L_deep_variance,
            "cross_term": deep_cross,
            "cross_term_signal": deep_cross.get("cross_term_signal", 0.0),
            "saturated": deep_saturated,
            "h3_null_fires": h3_null_fires,
            "h3_null_threshold": DEEP_SAT_CROSS_TERM_THRESHOLD,
        },
        "non_saturated_band": [NON_SAT_BAND_LO, NON_SAT_BAND_HI],
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
    n_distinct_mechs = body.get("n_distinct_mechanisms", 0)
    if n_distinct_mechs != len(CLEANUP_MECHANISMS):
        return False, (f"arms_differ_fail: {n_distinct_mechs}/"
                       f"{len(CLEANUP_MECHANISMS)} distinct mechanism output "
                       f"hashes (META_RULE_AF violation)")
    pc = body.get("saturation_pc_result", {})
    if not pc.get("pass"):
        return False, (f"saturation_pc_fail: SHARDED L=2 F=1 M=800 N=2048 "
                       f"corr=0.20 iterative_cosine acc={pc.get('acc')} < "
                       f"threshold={pc.get('threshold')}")
    cliff = body.get("cliff_arm", {})
    if not cliff.get("escapes_saturation_ceiling"):
        return False, (f"escapes_saturation_ceiling_fail: no L-slice on CLIFF "
                       f"arm has mean-acc < {NON_SAT_BAND_HI}; per_L_mean_acc="
                       f"{cliff.get('per_L_mean_acc')}; CLIFF regime saturated")
    deep = body.get("deep_sat_arm", {})
    if not deep.get("saturated"):
        return False, (f"deep_sat_regime_drift: mean_acc={deep.get('mean_acc')} "
                       f"< 0.95; H3-NULL control arm did not saturate")
    # NaN sanity
    for pt in phase_map:
        if pt.get("acc") != pt.get("acc"):
            return False, f"NAN_in_phase_map at {pt}"

    # Discriminator variance is INFORMATIONAL, not gating (null-hypothesis
    # discipline; feedback_smoke_gates_null_hypothesis_should_not_gate_on_
    # discriminator_firing_2026-07-03).
    cliff_signal = cliff.get("cross_term_signal", 0.0)
    deep_signal = deep.get("cross_term_signal", 0.0)
    return True, (f"smoke_gate_pass: cardinality_ok + 3-mech-hash-distinct + "
                  f"pc_acc={pc.get('acc')} (>={pc.get('threshold')}) + "
                  f"cliff_mean={cliff.get('mean_acc')} escapes_saturation + "
                  f"deep_sat_saturated(mean={deep.get('mean_acc')}); "
                  f"informational: cliff_cross_term_signal={cliff_signal} "
                  f"deep_cross_term_signal={deep_signal} h3_null_fires="
                  f"{deep.get('h3_null_fires')}")


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
        "saturation_pc_result": body.get("saturation_pc_result"),
        "cliff_arm": body.get("cliff_arm"),
        "deep_sat_arm": body.get("deep_sat_arm"),
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
    cliff = body.get("cliff_arm", {})
    deep = body.get("deep_sat_arm", {})
    pc = body.get("saturation_pc_result", {})
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"expected={expected_n} observed={observed_n}")
    elif not body.get("arms_differ_verified"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_ARMS_MUST_DIFFER_META_RULE_AF: "
                f"{body.get('n_distinct_mechanisms')} distinct mech-output-hashes")
    elif not pc.get("pass"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_SATURATION_PC_MISMATCH: SHARDED L=2 F=1 M=800 N=2048 "
                f"corr=0.20 iterative_cosine acc={pc.get('acc')} < "
                f"threshold={pc.get('threshold')} (Gate D violation)")
    elif not deep.get("saturated"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_DEEP_SAT_ARM_DRIFT: DEEP_SAT mean_acc="
                f"{deep.get('mean_acc')} < 0.95; H3-NULL control regime failed")
    else:
        cliff_signal = cliff.get("cross_term_signal", 0.0)
        deep_signal = deep.get("cross_term_signal", 0.0)
        h3_null_fires = deep.get("h3_null_fires", False)
        crossover = cliff.get("mech_ranking_crossover", False)
        cross_ct = cliff.get("cross_term", {})
        cross_note = (" ; mech_ranking_crossover=True (H3 informational)"
                      if crossover else "")
        h3_null_note = (f" ; H3-NULL fires(deep_cross_term_signal={deep_signal} "
                        f"< {DEEP_SAT_CROSS_TERM_THRESHOLD})"
                        if h3_null_fires else
                        f" ; H3-NULL DID NOT FIRE(deep_cross_term_signal="
                        f"{deep_signal} >= {DEEP_SAT_CROSS_TERM_THRESHOLD}) -- "
                        f"L x MECH interaction persists at deep-saturation")
        breakdown = (f" ; range_of_mech_spread_across_L="
                     f"{cross_ct.get('range_of_mech_spread_across_L', 0.0)} "
                     f"range_of_L_spread_across_mech="
                     f"{cross_ct.get('range_of_L_spread_across_mech', 0.0)} "
                     f"residual_range={cross_ct.get('residual_range', 0.0)}")

        if cliff_signal >= CROSS_TERM_H1_THRESHOLD:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H1_L_x_CLEANUP_CROSS_TERM_AT_CLIFF_ADJACENT_SHARDED: "
                    f"cliff cross_term_signal={cliff_signal} >= "
                    f"{CROSS_TERM_H1_THRESHOLD}; the F x CLEANUP mech-moderation "
                    f"pattern is L-dependent; L x MECH interaction is genuine "
                    f"at cliff-adjacent SHARDED F=1 regime; REGIME-EXTENSION of "
                    f"atom #3 (SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS_CG_META_v1) "
                    f"into the L x CLEANUP cross-term. Atom candidate: "
                    f"EMPIRICAL_L_x_CLEANUP_CROSS_TERM_SHARDED_CLIFF_ADJACENT_v1 "
                    f"MM_STANDARD at 3-seed FULL"
                    f"{breakdown}{cross_note}{h3_null_note}")
        elif cliff_signal < CROSS_TERM_H2_THRESHOLD:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H2_L_x_MECH_INERT_AT_CLIFF_ADJACENT_SHARDED: "
                    f"cliff cross_term_signal={cliff_signal} < "
                    f"{CROSS_TERM_H2_THRESHOLD}; mech_spread INDEPENDENT of L; "
                    f"the L=2 finding (P6v2 + P8 F x CLEANUP mech-moderation) "
                    f"EXTENDS to L in {{1,2,4}} unchanged. Atom candidate: "
                    f"L_x_MECH_CROSS_TERM_INERT_SHARDED_CLIFF_ADJACENT_NEGATIVE_v1 "
                    f"MM_TENTATIVE"
                    f"{breakdown}{cross_note}{h3_null_note}")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_WEAK_L_x_MECH_INTERACTION: cliff "
                    f"cross_term_signal={cliff_signal} in "
                    f"[{CROSS_TERM_H2_THRESHOLD}, {CROSS_TERM_H1_THRESHOLD}); "
                    f"weak L x MECH interaction (MM_TENTATIVE); consider "
                    f"refined sweep or higher TR"
                    f"{breakdown}{cross_note}{h3_null_note}")

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
    })
    return out


__all__ = [
    "ANCHOR_NAME", "DEVICE", "GPU_NAME",
    "CLEANUP_MECHANISMS", "CLEANUP_REGISTRY",
    "L_GRID_CLIFF_FULL", "L_GRID_CLIFF_SMOKE",
    "L_GRID_DEEP_SAT_FULL", "L_GRID_DEEP_SAT_SMOKE",
    "CLIFF_N", "CLIFF_M", "CLIFF_CORR", "CLIFF_F",
    "DEEP_SAT_N", "DEEP_SAT_M", "DEEP_SAT_CORR", "DEEP_SAT_F",
    "TR_FULL", "TR_SMOKE",
    "SATURATION_PC_REGIME", "SATURATION_PC_THRESHOLD",
    "NON_SAT_BAND_LO", "NON_SAT_BAND_HI",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "CROSS_TERM_H1_THRESHOLD", "CROSS_TERM_H2_THRESHOLD",
    "DEEP_SAT_CROSS_TERM_THRESHOLD",
    "REQUIRED_FIELDS",
    "compute_cross_term",
    "eval_phase_point", "selftest", "run_one_seed",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
