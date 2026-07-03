"""Stage 1 Regime Probe 14: L (chain-depth) x F (fan-out) CROSS-TERM at cliff-adjacent SHARDED.

Cell anchor: `stage1_regime_probe_14_L_x_F_non_saturated_v1`
Pre-reg:     preregs/2026-07-03_stage1_regime_probe_14_L_x_F_non_saturated_v1.md

Purpose:
    Skunkworks atom #48 addendum flagged "L cross-terms unmapped." L was
    established as a CG_META axis at Probe 12 (atom #3 chain), and F was
    filled at Probe 8. Prior probes (6v2, 8) fixed L=2 while varying F.
    Probe 14 asks: does F effect depend on L, or are L and F orthogonal
    axes as prior L=2-fixed-convention implicitly assumed?

Cited source atoms (per META_RULE_AC / mechanism_abstraction_lossy):
    T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1
    SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS_CG_META_v1 (Stage 1 atom #3, L axis)
    T3/EXP_stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1_3seed_FULL (F axis)
    T3/EXP_stage1_regime_probe_12_L_marginal_effect_sweep_v1 (L marginal-effect)
    Skunkworks atom #48 (L axis promoted; L cross-terms unmapped -- addendum)
    Skunkworks atom #43 (cross-term measurement requires both axes in band)
    Skunkworks atom #44 (axis labels map to substrate primitives)
    Skunkworks atom #49 (BUNDLED bimodal; excluded from cliff-adjacent regime)
    META_saturation_floor_masks_null_variance_probe3_lesson (H3 null control)
    feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-07-03
    feedback_mechanism_abstraction_lossy_cite_source_signature_2026-07-03
    feedback_plate_bound_too_pessimistic_for_sharded_fhrr_chain_composition_2026-07-03
    feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03

Source signature (cited):
    SHARDED FHRR chain composition; CLIFF: N=512 M=6400 corr=0.85;
    DEEP_SAT: N=8192 M=800 corr=0.60; MECH=modern_hopfield (best F=1 performer
    per Probe 6 v2 at cliff-adjacent regime); BETA=8.0 ALPHA_SOFT=0.5;
    TR=100 (FULL) / 40 (SMOKE). L in {1,2,4} band-only per Probe 12 VET;
    F in {1,2,4,8,16} per Probe 8 grid. Single mechanism to keep cardinality
    tight and isolate the L x F cross-term signal (mechanism cross-terms
    already covered by Probe 8 F x MECH).

Sweep grid FULL (20 pts / seed):
    CLIFF arm:   L in {1,2,4} x F in {1,2,4,8,16} x modern_hopfield = 15 pts
    DEEP_SAT arm: L in {1,4}   x F in {1,16}      x modern_hopfield = 4 pts (H3 null)
    SATURATION_PC arm (Gate D): L=2 F=1 M=800 N=2048 corr=0.20 iterative_cosine = 1 pt

Sweep grid SMOKE (12 pts):
    CLIFF arm:    L in {1,2,4} x F in {1,4,16}    x modern_hopfield = 9 pts
    DEEP_SAT arm: L in {1,4}   x F in {1}         x modern_hopfield = 2 pts
    SATURATION_PC arm: 1 pt

Discriminator (H1 interaction) -- classical 2-way ANOVA-style interaction:
    Given acc(L,F) grid on CLIFF arm (3 x 5 in FULL, 3 x 3 in SMOKE):
      F_effect_per_L[l] = max_F acc(l,F) - min_F acc(l,F)     # F range at fixed L
      L_effect_per_F[f] = max_L acc(L,f) - min_L acc(L,f)     # L range at fixed F
      F_effect_range = max_l F_effect_per_L[l] - min_l F_effect_per_L[l]
      L_effect_range = max_f L_effect_per_F[f] - min_f L_effect_per_F[f]
      interaction_metric = max(F_effect_range, L_effect_range)
    Also compute additive-model residual (2-way ANOVA):
      add_model[l,f] = row_mean[l] + col_mean[f] - grand_mean
      residual[l,f]  = acc[l,f] - add_model[l,f]
      max_abs_residual = max |residual|
    Both metrics reported; interaction_metric is primary.

Hypotheses (MM_TENTATIVE at SMOKE; MM_STANDARD requires 3-seed FULL):
    H1 (L x F interaction):
        cliff.interaction_metric >= 0.10
      -> F effect is L-conditional; L and F NOT orthogonal at cliff-adjacent
         SHARDED; today's 6-pair regime matrix needs L-slice annotation.
         Atom candidate: L_x_F_CROSS_TERM_AT_CLIFF_ADJACENT_SHARDED_v1
         MM_TENTATIVE at SMOKE, MM_STANDARD at 3-seed FULL.
    H2 (L x F orthogonal, additive):
        cliff.interaction_metric < 0.05
      -> F effect is same across L; L and F ARE orthogonal axes at this
         signature; prior Probes 6v2/8 findings hold at L=2 slice without loss
         of generality. Atom candidate:
         L_x_F_ORTHOGONAL_AT_CLIFF_ADJACENT_SHARDED_NEGATIVE_v1 MM_TENTATIVE.
    H3-NULL (DEEP_SAT null):
        deep_sat.interaction_metric < 0.05
      -> confirms cross-term degeneracy at saturation.

Compute architecture: `(c) mixed with justification`. Batched matmul at each
    phase point (build_rules + run_chain use torch.matmul internally); Python
    for-loop across (L, F) sweep unavoidable per-point independence.
    Wall-time smoke on CPU: ~30-90s (12 phase points at 1-8s each; F=16 x L=4
    is the slowest cell). FULL on CPU: ~2-6 min. GPU available but modest
    sizes (N<=8192, M<=6400) -- CPU adequate for smoke; FULL routes remote
    via Orchestrator per USER-LOCKED SMOKE-only-on-local-cpu.

Sibling wrappers: exp_stage1_regime_probe_14_L_x_F_non_saturated_v1_s{7,13,19}.py
    (s7 authored here; s13/s19 authored post-Tailscale-restore for 3-seed FULL)

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-07-03 (agent-spawn, Opus 4.7).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: single-mech cell; instead verify (L=1,F=1) vs (L=4,F=16)
#   produce DIFFERENT output hashes -- proves L and F axes fire structurally
# - final_metrics_atomicity: tmp_replace via os.replace()
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: categorical accuracy discriminator; interaction is grid-shape metric
# - baseline_in_band: L in {1,2,4} lands in [0.30, 0.95] at F=1 CLIFF per Probe 12
#   bracket; F sweep at L=2 lands in band per Probe 8 (F=1 top, F=16 floor-adjacent)
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L; H1 uses >= 0.10)
# - HP_SCOPE per-arm: CLIFF gets H1/H2/MIDDLE_BAND; DEEP_SAT gets H3-NULL only;
#   PC gets Gate-D-reproducer only
# - cardinality_ok: EXPECTED_N_UNITS_FULL=20, EXPECTED_N_UNITS_SMOKE=12
# - per-unit failure-class: RuntimeError with specific class name propagated
# - calibration_check: default_ok_for_this_regime (BETA=8.0 ALPHA=0.5 inherited)
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

ANCHOR_NAME = "stage1_regime_probe_14_L_x_F_non_saturated_v1"

# ---------------------------------------------------------------------------
# Sweep constants (LOCKED at module init; MEASURED@empirical brackets 2026-07-03)
# ---------------------------------------------------------------------------
# Single mechanism to isolate L x F cross-term (mech cross-terms covered by P8)
# modern_hopfield chosen: best F=1 performer per Probe 6 v2 at cliff-adjacent.
MECH = "modern_hopfield"

# L axis: band-only per Probe 12 VET (L=8,16 fall below floor at CLIFF)
L_GRID_CLIFF_FULL  = [1, 2, 4]
L_GRID_CLIFF_SMOKE = [1, 2, 4]      # smoke uses full L grid; interaction test needs the axis
# F axis: matches Probe 8 grid
F_GRID_CLIFF_FULL  = [1, 2, 4, 8, 16]
F_GRID_CLIFF_SMOKE = [1, 4, 16]     # endpoints + mid; captures F cliff transition

# CLIFF-adjacent operating point (empirically-locked per Probes 6v2/8/12).
# MEASURED@scratchpad probe12_L_bracket 2026-07-03: L in {1,2,4} at F=1
#   modern_hopfield: L1=0.95, L2=0.725, L4=0.375; all in [0.30, 0.95]
# MEASURED@Probe 8 smoke iterative_cosine F sweep 2026-07-03: F=1 top, F=16
#   floor-adjacent, both in-band at TR=100 3-seed.
CLIFF_N = 512
CLIFF_M = 6400
CLIFF_CORR = 0.85

# DEEP_SAT arm (H3-NULL: cross-term degeneracy at saturation).
# MEASURED@scratchpad probe12_L_bracket 2026-07-03: mean_acc=1.000 exact
# across L in {1,2,4,8,16} at F=1. Expect the same across (L, F) grid.
L_GRID_DEEP_SAT_FULL  = [1, 4]
L_GRID_DEEP_SAT_SMOKE = [1, 4]
F_GRID_DEEP_SAT_FULL  = [1, 16]
F_GRID_DEEP_SAT_SMOKE = [1]
DEEP_SAT_N = 8192
DEEP_SAT_M = 800
DEEP_SAT_CORR = 0.60

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

# Cardinality: FULL = 3 L x 5 F (CLIFF) + 2 L x 2 F (DEEP_SAT) + 1 PC = 15+4+1 = 20
EXPECTED_N_UNITS_FULL = (len(L_GRID_CLIFF_FULL) * len(F_GRID_CLIFF_FULL)
                         + len(L_GRID_DEEP_SAT_FULL) * len(F_GRID_DEEP_SAT_FULL)
                         + 1)
# SMOKE = 3 L x 3 F (CLIFF) + 2 L x 1 F (DEEP_SAT) + 1 PC = 9+2+1 = 12
EXPECTED_N_UNITS_SMOKE = (len(L_GRID_CLIFF_SMOKE) * len(F_GRID_CLIFF_SMOKE)
                          + len(L_GRID_DEEP_SAT_SMOKE) * len(F_GRID_DEEP_SAT_SMOKE)
                          + 1)

# Non-saturated band
NON_SAT_BAND_LO = 0.30
NON_SAT_BAND_HI = 0.95

# Discriminator thresholds
INTERACTION_H1_THRESHOLD = 0.10   # H1: L x F interaction fires
INTERACTION_H2_THRESHOLD = 0.05   # H2: orthogonal / additive
# H3-NULL threshold on DEEP_SAT arm
DEEP_SAT_INTERACTION_THRESHOLD = 0.05

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

    # META_RULE_AF-analog hash of cleanup output indices; used later to prove
    # different (L, F) points produce different outputs (axes structurally fire).
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
# Interaction metrics (2-way L x F cross-term)
# ---------------------------------------------------------------------------
def compute_interaction_grid(cell_pts: List[Dict[str, Any]],
                              L_grid: List[int], F_grid: List[int]
                              ) -> Dict[str, Any]:
    """Compute acc(L,F) grid + interaction metrics from CLIFF or DEEP_SAT pts."""
    # acc_grid[l][f] = acc at (L=l, F=f)
    acc_grid: Dict[int, Dict[int, float]] = {L: {} for L in L_grid}
    for pt in cell_pts:
        L, F, a = pt["L"], pt["F"], pt["acc"]
        if L in acc_grid and F in F_grid:
            acc_grid[L][F] = float(a)

    # Verify full-rectangular fill
    complete = all(len(acc_grid[L]) == len(F_grid) for L in L_grid)
    if not complete:
        return {
            "acc_grid": {str(L): {str(F): v for F, v in acc_grid[L].items()}
                          for L in L_grid},
            "complete": False,
            "F_effect_per_L": {},
            "L_effect_per_F": {},
            "F_effect_range": 0.0,
            "L_effect_range": 0.0,
            "interaction_metric": 0.0,
            "additive_residual_max_abs": 0.0,
            "additive_residual_grid": {},
            "row_means": {},
            "col_means": {},
            "grand_mean": 0.0,
        }

    # F_effect_per_L: max-min across F at each L (F range at fixed L)
    F_effect_per_L = {L: round(max(acc_grid[L].values()) - min(acc_grid[L].values()), 4)
                      for L in L_grid}
    # L_effect_per_F: max-min across L at each F (L range at fixed F)
    L_effect_per_F = {}
    for F in F_grid:
        col = [acc_grid[L][F] for L in L_grid]
        L_effect_per_F[F] = round(max(col) - min(col), 4)

    # Range of F-effect across L: does F-effect depend on L?
    F_effect_range = round(max(F_effect_per_L.values()) - min(F_effect_per_L.values()), 4)
    # Range of L-effect across F: does L-effect depend on F?
    L_effect_range = round(max(L_effect_per_F.values()) - min(L_effect_per_F.values()), 4)
    interaction_metric = round(max(F_effect_range, L_effect_range), 4)

    # 2-way ANOVA-style additive-model residual
    row_means = {L: round(float(np.mean(list(acc_grid[L].values()))), 4)
                 for L in L_grid}
    col_means = {F: round(float(np.mean([acc_grid[L][F] for L in L_grid])), 4)
                 for F in F_grid}
    all_vals = [acc_grid[L][F] for L in L_grid for F in F_grid]
    grand_mean = round(float(np.mean(all_vals)), 4)
    # residual[l,f] = acc[l,f] - (row_mean[l] + col_mean[f] - grand_mean)
    residual_grid: Dict[int, Dict[int, float]] = {}
    max_abs_resid = 0.0
    for L in L_grid:
        residual_grid[L] = {}
        for F in F_grid:
            predicted = row_means[L] + col_means[F] - grand_mean
            r = round(acc_grid[L][F] - predicted, 4)
            residual_grid[L][F] = r
            if abs(r) > max_abs_resid:
                max_abs_resid = abs(r)

    return {
        "acc_grid": {str(L): {str(F): round(acc_grid[L][F], 4) for F in F_grid}
                      for L in L_grid},
        "complete": True,
        "F_effect_per_L": {str(L): F_effect_per_L[L] for L in L_grid},
        "L_effect_per_F": {str(F): L_effect_per_F[F] for F in F_grid},
        "F_effect_range": F_effect_range,
        "L_effect_range": L_effect_range,
        "interaction_metric": interaction_metric,
        "row_means_by_L": {str(L): row_means[L] for L in L_grid},
        "col_means_by_F": {str(F): col_means[F] for F in F_grid},
        "grand_mean": grand_mean,
        "additive_residual_grid": {str(L): {str(F): residual_grid[L][F]
                                              for F in F_grid} for L in L_grid},
        "additive_residual_max_abs": round(max_abs_resid, 4),
    }


# ---------------------------------------------------------------------------
# Selftest (formula check at reduced grid; wall < 60s target on CPU)
# ---------------------------------------------------------------------------
def selftest() -> Tuple[bool, str]:
    msgs = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 20:
        return False, (f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 20 "
                       f"(15 cliff + 4 deep_sat + 1 PC)")
    if EXPECTED_N_UNITS_SMOKE != 12:
        return False, (f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 12 "
                       f"(9 cliff + 2 deep_sat + 1 PC)")
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} "
                f"SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. Interaction-metric formula sanity: hand-constructed additive grid
    #    should yield interaction_metric == 0 exact (no interaction) and
    #    max_abs_residual == 0. Non-additive grid should yield >0.
    #    Purely-additive: acc[l,f] = a_l + b_f + c
    L_test = [1, 2, 4]
    F_test = [1, 4, 16]
    a = {1: 0.0, 2: -0.1, 4: -0.3}
    b = {1: 0.1, 4: 0.0, 16: -0.2}
    c = 0.7
    add_pts = []
    for L in L_test:
        for F in F_test:
            add_pts.append({"L": L, "F": F, "acc": a[L] + b[F] + c})
    add_grid = compute_interaction_grid(add_pts, L_test, F_test)
    if not add_grid["complete"]:
        return False, "additive grid not complete in selftest"
    # Tolerance 1e-3 accounts for 4-decimal rounding in row/col/grand means.
    if add_grid["additive_residual_max_abs"] > 1e-3:
        return False, (f"additive-grid residual should be ~0; got "
                       f"{add_grid['additive_residual_max_abs']}")
    # F_effect at each L should be same (max_F b - min_F b = 0.1 - (-0.2) = 0.3)
    # so F_effect_range should also be 0.
    if add_grid["F_effect_range"] > 1e-3:
        return False, (f"additive-grid F_effect_range should be ~0; got "
                       f"{add_grid['F_effect_range']}")
    if add_grid["L_effect_range"] > 1e-3:
        return False, (f"additive-grid L_effect_range should be ~0; got "
                       f"{add_grid['L_effect_range']}")
    msgs.append(f"additive-grid interaction=0.0 residual=0.0 (formula OK)")

    # Non-additive grid: introduce cross-term at (L=4, F=16)
    nonadd_pts = []
    for L in L_test:
        for F in F_test:
            v = a[L] + b[F] + c
            if L == 4 and F == 16:
                v += 0.2  # cross-term injection
            nonadd_pts.append({"L": L, "F": F, "acc": v})
    nonadd_grid = compute_interaction_grid(nonadd_pts, L_test, F_test)
    if nonadd_grid["interaction_metric"] < 0.05:
        return False, (f"non-additive grid interaction_metric too low: "
                       f"{nonadd_grid['interaction_metric']}")
    if nonadd_grid["additive_residual_max_abs"] < 0.05:
        return False, (f"non-additive grid residual too low: "
                       f"{nonadd_grid['additive_residual_max_abs']}")
    msgs.append(f"non-additive-grid interaction="
                f"{nonadd_grid['interaction_metric']} residual="
                f"{nonadd_grid['additive_residual_max_abs']} (both fire)")

    # 3. L-axis fires: L=1 chain output MUST differ from L=4 chain output
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(1017)
    M_probe = 50
    N_test = 512
    F_test_int = 1
    TR = 20
    props1, perms1, IMPL1, POS1, sh1, bd1 = build_rules(
        M_probe, F_test_int, gen, DEVICE, N_test)
    _, ci_L1 = run_chain("SHARDED", MECH, 1, F_test_int, TR,
                         props1, perms1, IMPL1, POS1, sh1, bd1, 0.10, gen, DEVICE)
    gen.manual_seed(1017)
    props2, perms2, IMPL2, POS2, sh2, bd2 = build_rules(
        M_probe, F_test_int, gen, DEVICE, N_test)
    _, ci_L4 = run_chain("SHARDED", MECH, 4, F_test_int, TR,
                         props2, perms2, IMPL2, POS2, sh2, bd2, 0.10, gen, DEVICE)
    h_L1 = hashlib.sha256(ci_L1.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    h_L4 = hashlib.sha256(ci_L4.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    if h_L1 == h_L4:
        return False, f"L=1 vs L=4 chain outputs identical; hash={h_L1}"
    msgs.append(f"L-axis fires: L1={h_L1} L4={h_L4}")

    # 4. F-axis fires: F=1 chain output MUST differ from F=16 chain output
    gen.manual_seed(2023)
    props3, perms3, IMPL3, POS3, sh3, bd3 = build_rules(
        M_probe, 1, gen, DEVICE, N_test)
    _, ci_F1 = run_chain("SHARDED", MECH, 2, 1, TR,
                         props3, perms3, IMPL3, POS3, sh3, bd3, 0.10, gen, DEVICE)
    gen.manual_seed(2023)
    props4, perms4, IMPL4, POS4, sh4, bd4 = build_rules(
        M_probe, 16, gen, DEVICE, N_test)
    _, ci_F16 = run_chain("SHARDED", MECH, 2, 16, TR,
                          props4, perms4, IMPL4, POS4, sh4, bd4, 0.10, gen, DEVICE)
    h_F1 = hashlib.sha256(ci_F1.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    h_F16 = hashlib.sha256(ci_F16.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    if h_F1 == h_F16:
        return False, f"F=1 vs F=16 chain outputs identical; hash={h_F1}"
    msgs.append(f"F-axis fires: F1={h_F1} F16={h_F16}")

    # 5. SATURATION_PC easy gate reproducer (Gate D at reduced TR)
    gen.manual_seed(1013)
    pc = SATURATION_PC_REGIME
    props5, perms5, IMPL5, POS5, sh5, bd5 = build_rules(
        pc["M"], pc["F"], gen, DEVICE, pc["N"])
    acc_easy, _ = run_chain(pc["storage"], pc["cleanup_mechanism"],
                            pc["L"], pc["F"], 40,
                            props5, perms5, IMPL5, POS5, sh5, bd5,
                            pc["corruption"], gen, DEVICE)
    if acc_easy < 0.85:
        return False, (f"SATURATION_PC selftest expected >= 0.85 at TR=40; "
                       f"got {acc_easy:.3f}")
    msgs.append(f"SATURATION_PC selftest (TR=40): acc={acc_easy:.3f}")

    # 6. Cliff-adjacent regime sanity: L=2 F=1 modern_hopfield in loose band
    gen.manual_seed(3131)
    props6, perms6, IMPL6, POS6, sh6, bd6 = build_rules(
        CLIFF_M, 1, gen, DEVICE, CLIFF_N)
    acc_cliff, _ = run_chain("SHARDED", MECH, 2, 1, 20,
                             props6, perms6, IMPL6, POS6, sh6, bd6,
                             CLIFF_CORR, gen, DEVICE)
    if not (0.20 <= acc_cliff <= 0.98):
        return False, (f"CLIFF regime sanity (L=2 F=1 M={CLIFF_M} N={CLIFF_N} "
                       f"corr={CLIFF_CORR} {MECH} TR=20): acc={acc_cliff:.3f} "
                       f"outside [0.20, 0.98]; regime drifted")
    msgs.append(f"CLIFF regime sanity L=2 F=1 (TR=20): acc={acc_cliff:.3f}")

    # 7. DEEP_SAT regime sanity (saturated expected)
    gen.manual_seed(4141)
    props7, perms7, IMPL7, POS7, sh7, bd7 = build_rules(
        DEEP_SAT_M, 1, gen, DEVICE, DEEP_SAT_N)
    acc_deep, _ = run_chain("SHARDED", MECH, 4, 1, 20,
                            props7, perms7, IMPL7, POS7, sh7, bd7,
                            DEEP_SAT_CORR, gen, DEVICE)
    if acc_deep < 0.95:
        return False, (f"DEEP_SAT regime sanity (L=4 F=1 M={DEEP_SAT_M} "
                       f"N={DEEP_SAT_N} corr={DEEP_SAT_CORR} {MECH} TR=20): "
                       f"acc={acc_deep:.3f} < 0.95; regime drifted")
    msgs.append(f"DEEP_SAT regime sanity L=4 F=1 (TR=20): acc={acc_deep:.3f}")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed(seed: int, run_mode: str) -> Dict[str, Any]:
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        L_grid_cliff = L_GRID_CLIFF_SMOKE
        F_grid_cliff = F_GRID_CLIFF_SMOKE
        L_grid_deep = L_GRID_DEEP_SAT_SMOKE
        F_grid_deep = F_GRID_DEEP_SAT_SMOKE
        TR = TR_SMOKE
        expected_n = EXPECTED_N_UNITS_SMOKE
    else:
        L_grid_cliff = L_GRID_CLIFF_FULL
        F_grid_cliff = F_GRID_CLIFF_FULL
        L_grid_deep = L_GRID_DEEP_SAT_FULL
        F_grid_deep = F_GRID_DEEP_SAT_FULL
        TR = TR_FULL
        expected_n = EXPECTED_N_UNITS_FULL

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"mech={MECH} L_cliff={L_grid_cliff} F_cliff={F_grid_cliff} "
          f"L_deep={L_grid_deep} F_deep={F_grid_deep} "
          f"cliff=(N={CLIFF_N},M={CLIFF_M},corr={CLIFF_CORR}) "
          f"deep=(N={DEEP_SAT_N},M={DEEP_SAT_M},corr={DEEP_SAT_CORR}) "
          f"TR={TR} expected_n={expected_n}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    salt = 0
    t0 = time.perf_counter()

    # 1) CLIFF arm: L x F grid at cliff-adjacent regime
    for L in L_grid_cliff:
        for F in F_grid_cliff:
            salt += 1
            pt = eval_phase_point(MECH, CLIFF_M, CLIFF_N, F, L,
                                  CLIFF_CORR, "SHARDED", TR, seed, salt,
                                  arm_tag="CLIFF")
            phase_map.append(pt)
            print(f"  [{len(phase_map):3d}/{expected_n:3d}] CLIFF     "
                  f"L={L:2d} F={F:2d} mech={MECH:22s} M={CLIFF_M} N={CLIFF_N} "
                  f"c={CLIFF_CORR:.2f} acc={pt['acc']:.4f} "
                  f"dt={pt['elapsed_s']:.2f}s", flush=True)

    # 2) DEEP_SAT arm (H3-NULL): L x F grid at deep-saturation
    for L in L_grid_deep:
        for F in F_grid_deep:
            salt += 1
            pt = eval_phase_point(MECH, DEEP_SAT_M, DEEP_SAT_N, F, L,
                                  DEEP_SAT_CORR, "SHARDED", TR, seed, salt,
                                  arm_tag="DEEP_SAT")
            phase_map.append(pt)
            print(f"  [{len(phase_map):3d}/{expected_n:3d}] DEEP_SAT  "
                  f"L={L:2d} F={F:2d} mech={MECH:22s} M={DEEP_SAT_M} "
                  f"N={DEEP_SAT_N} c={DEEP_SAT_CORR:.2f} acc={pt['acc']:.4f} "
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
          f"L={pc['L']:2d} F={pc['F']:2d} mech={pc['cleanup_mechanism']:22s} "
          f"M={pc['M']} N={pc['N']} c={pc['corruption']:.2f} "
          f"acc={pc_pt['acc']:.4f} dt={pc_pt['elapsed_s']:.2f}s", flush=True)

    elapsed = time.perf_counter() - t0
    observed_n = len(phase_map)
    cardinality_ok = (observed_n == expected_n)

    # ARMS-MUST-DIFFER analog: verify (L=1,F=1) vs (L=max,F=max) at CLIFF
    # produce different output hashes (proves L and F axes structurally fire
    # under the single-mechanism regime; META_RULE_AF-analog).
    cliff_pts = [p for p in phase_map if p["arm_tag"] == "CLIFF"]
    deep_pts = [p for p in phase_map if p["arm_tag"] == "DEEP_SAT"]

    hash_corners: Dict[str, str] = {}
    L_min, L_max = min(L_grid_cliff), max(L_grid_cliff)
    F_min, F_max = min(F_grid_cliff), max(F_grid_cliff)
    for pt in cliff_pts:
        if (pt["L"], pt["F"]) == (L_min, F_min):
            hash_corners[f"L{L_min}_F{F_min}"] = pt["output_hash"]
        if (pt["L"], pt["F"]) == (L_max, F_max):
            hash_corners[f"L{L_max}_F{F_max}"] = pt["output_hash"]
    corner_hashes_distinct = (len(set(hash_corners.values())) >= 2
                              if len(hash_corners) == 2 else False)

    # SATURATION_PC pass check
    pc_acc = float(pc_pt["acc"])
    pc_pass = (pc_acc >= SATURATION_PC_THRESHOLD)

    # CLIFF arm interaction analysis
    cliff_grid = compute_interaction_grid(cliff_pts, L_grid_cliff, F_grid_cliff)
    cliff_accs = [p["acc"] for p in cliff_pts]
    cliff_mean = float(np.mean(cliff_accs)) if cliff_accs else 0.0
    cliff_min = float(np.min(cliff_accs)) if cliff_accs else 0.0
    cliff_max = float(np.max(cliff_accs)) if cliff_accs else 0.0
    cliff_in_band = sum(1 for a in cliff_accs
                        if NON_SAT_BAND_LO <= a <= NON_SAT_BAND_HI)
    cliff_in_band_frac = cliff_in_band / max(len(cliff_accs), 1)
    escapes_saturation_cliff = any(a < NON_SAT_BAND_HI for a in cliff_accs)

    # DEEP_SAT arm interaction analysis (H3-NULL)
    deep_grid = compute_interaction_grid(deep_pts, L_grid_deep, F_grid_deep)
    deep_accs = [p["acc"] for p in deep_pts]
    deep_mean = float(np.mean(deep_accs)) if deep_accs else 0.0
    deep_min = float(np.min(deep_accs)) if deep_accs else 0.0
    deep_max = float(np.max(deep_accs)) if deep_accs else 0.0
    deep_saturated = (deep_mean >= 0.95)
    h3_null_fires = (deep_grid.get("interaction_metric", 0.0)
                     < DEEP_SAT_INTERACTION_THRESHOLD)

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
        "mech": MECH,
        "hash_corners": hash_corners,
        "corner_hashes_distinct": corner_hashes_distinct,
        "arms_differ_verified": corner_hashes_distinct,  # single-mech analog
        "saturation_pc_result": {
            "regime": SATURATION_PC_REGIME,
            "acc": pc_acc,
            "threshold": SATURATION_PC_THRESHOLD,
            "pass": pc_pass,
        },
        "cliff_arm": {
            "regime": {"N": CLIFF_N, "M": CLIFF_M, "corr": CLIFF_CORR,
                        "mech": MECH, "storage": "SHARDED"},
            "L_grid": L_grid_cliff,
            "F_grid": F_grid_cliff,
            "mean_acc": round(cliff_mean, 4),
            "min_acc": round(cliff_min, 4),
            "max_acc": round(cliff_max, 4),
            "n_in_non_saturated_band": cliff_in_band,
            "n_total": len(cliff_accs),
            "fraction_in_band": round(cliff_in_band_frac, 4),
            "escapes_saturation_ceiling": escapes_saturation_cliff,
            **cliff_grid,
        },
        "deep_sat_arm": {
            "regime": {"N": DEEP_SAT_N, "M": DEEP_SAT_M, "corr": DEEP_SAT_CORR,
                        "mech": MECH, "storage": "SHARDED"},
            "L_grid": L_grid_deep,
            "F_grid": F_grid_deep,
            "mean_acc": round(deep_mean, 4),
            "min_acc": round(deep_min, 4),
            "max_acc": round(deep_max, 4),
            "saturated": deep_saturated,
            "h3_null_fires": h3_null_fires,
            "h3_null_threshold": DEEP_SAT_INTERACTION_THRESHOLD,
            **deep_grid,
        },
        "non_saturated_band": [NON_SAT_BAND_LO, NON_SAT_BAND_HI],
        "avg_peak_mem_mb": round(avg_peak, 1),
        "elapsed_seed_s": round(elapsed, 2),
        "beta": BETA,
        "alpha_soft": ALPHA_SOFT,
    }


# ---------------------------------------------------------------------------
# Smoke-gate predicate (null-hypothesis-safe; gate on infra + PC + escapes only)
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    phase_map = body.get("phase_map", [])
    if len(phase_map) != body.get("expected_n_units"):
        return False, (f"cardinality_breach: expected={body.get('expected_n_units')} "
                       f"got={len(phase_map)}")
    if not body.get("corner_hashes_distinct"):
        return False, (f"corner_hashes_not_distinct: axes did not fire "
                       f"structurally; hashes={body.get('hash_corners')}")
    pc = body.get("saturation_pc_result", {})
    if not pc.get("pass"):
        return False, (f"saturation_pc_fail: SHARDED L=2 F=1 M=800 N=2048 "
                       f"corr=0.20 iterative_cosine acc={pc.get('acc')} < "
                       f"threshold={pc.get('threshold')}")
    cliff = body.get("cliff_arm", {})
    if not cliff.get("escapes_saturation_ceiling"):
        return False, (f"escapes_saturation_ceiling_fail: no (L,F) point on "
                       f"CLIFF arm below {NON_SAT_BAND_HI}; CLIFF regime "
                       f"fully saturated; design goal not achieved")
    deep = body.get("deep_sat_arm", {})
    if not deep.get("saturated"):
        return False, (f"deep_sat_regime_drift: mean_acc={deep.get('mean_acc')} "
                       f"< 0.95; H3-NULL control arm did not saturate at "
                       f"(N={DEEP_SAT_N}, M={DEEP_SAT_M}, corr={DEEP_SAT_CORR}); "
                       f"deep-sat regime drifted from empirical bracket")
    if not cliff.get("complete"):
        return False, f"cliff_grid_not_complete: acc_grid missing points"
    # NaN sanity
    for pt in phase_map:
        if pt.get("acc") != pt.get("acc"):
            return False, f"NAN_in_phase_map at {pt}"

    # Discriminator informational (null-hypothesis discipline):
    interaction = cliff.get("interaction_metric", 0.0)
    F_range = cliff.get("F_effect_range", 0.0)
    L_range = cliff.get("L_effect_range", 0.0)
    max_resid = cliff.get("additive_residual_max_abs", 0.0)
    deep_interaction = deep.get("interaction_metric", 0.0)
    return True, (f"smoke_gate_pass: cardinality_ok + axes-fire + "
                  f"pc_acc={pc.get('acc')} (>={pc.get('threshold')}) + "
                  f"cliff_mean={cliff.get('mean_acc')} escapes_saturation + "
                  f"deep_sat_saturated(mean={deep.get('mean_acc')}); "
                  f"informational: cliff_interaction_metric={interaction} "
                  f"(F_range={F_range} L_range={L_range} "
                  f"max_abs_resid={max_resid}) "
                  f"deep_interaction={deep_interaction} "
                  f"h3_null_fires={deep.get('h3_null_fires')}")


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
        "mech": body.get("mech"),
        "hash_corners": body.get("hash_corners"),
        "corner_hashes_distinct": body.get("corner_hashes_distinct"),
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
        vmsg = (f"HARD_FAIL_ARMS_MUST_DIFFER_META_RULE_AF_ANALOG: "
                f"corner_hashes={body.get('hash_corners')} not distinct; "
                f"L or F axis structurally aliased")
    elif not pc.get("pass"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_SATURATION_PC_MISMATCH: SHARDED L=2 F=1 M=800 N=2048 "
                f"corr=0.20 iterative_cosine acc={pc.get('acc')} < "
                f"threshold={pc.get('threshold')} (Gate D violation)")
    elif not deep.get("saturated"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_DEEP_SAT_ARM_DRIFT: DEEP_SAT mean_acc="
                f"{deep.get('mean_acc')} < 0.95; H3-NULL control regime failed "
                f"to saturate; regime construction broken")
    elif not cliff.get("complete"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CLIFF_GRID_INCOMPLETE: acc_grid missing points; "
                f"expected {len(cliff.get('L_grid', []))}x"
                f"{len(cliff.get('F_grid', []))}")
    else:
        # Primary discriminator: interaction_metric on CLIFF arm.
        # H1 fires: cross-term interaction (L conditional on F or vice versa).
        # H2 fires: orthogonal / additive (no interaction).
        interaction = cliff.get("interaction_metric", 0.0)
        F_range = cliff.get("F_effect_range", 0.0)
        L_range = cliff.get("L_effect_range", 0.0)
        max_resid = cliff.get("additive_residual_max_abs", 0.0)
        deep_interaction = deep.get("interaction_metric", 0.0)
        h3_null_fires = deep.get("h3_null_fires", False)

        h3_note = (f" ; H3-NULL fires(deep_interaction={deep_interaction} < "
                    f"{DEEP_SAT_INTERACTION_THRESHOLD})"
                    if h3_null_fires else
                    f" ; H3-NULL DID NOT FIRE(deep_interaction="
                    f"{deep_interaction} >= "
                    f"{DEEP_SAT_INTERACTION_THRESHOLD}) -- cross-term "
                    f"surprisingly non-degenerate at deep-saturation")
        resid_note = f" ; additive_residual_max_abs={max_resid}"
        range_note = f" ; F_effect_range={F_range} L_effect_range={L_range}"

        if interaction >= INTERACTION_H1_THRESHOLD:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H1_L_x_F_INTERACTION_AT_CLIFF_ADJACENT_SHARDED: "
                    f"cliff interaction_metric={interaction} "
                    f">= {INTERACTION_H1_THRESHOLD}; L and F are NOT "
                    f"orthogonal axes at cliff-adjacent SHARDED regime; F "
                    f"effect is L-conditional; today's 6-pair regime matrix "
                    f"needs L-slice annotation per Skunkworks atom #48 "
                    f"addendum. Atom candidate: "
                    f"L_x_F_CROSS_TERM_AT_CLIFF_ADJACENT_SHARDED_v1 "
                    f"MM_STANDARD at 3-seed FULL"
                    f"{range_note}{resid_note}{h3_note}")
        elif interaction < INTERACTION_H2_THRESHOLD:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H2_L_x_F_ORTHOGONAL_AT_CLIFF_ADJACENT_SHARDED: "
                    f"cliff interaction_metric={interaction} < "
                    f"{INTERACTION_H2_THRESHOLD}; L and F ARE orthogonal "
                    f"axes at cliff-adjacent SHARDED regime; F effect same "
                    f"across L values; prior Probes 6v2/8 findings hold at "
                    f"L=2 slice without loss of generality; L=2 fixed "
                    f"convention was correctly labeled orthogonal. Atom "
                    f"candidate: L_x_F_ORTHOGONAL_AT_CLIFF_ADJACENT_SHARDED_"
                    f"NEGATIVE_v1 MM_TENTATIVE"
                    f"{range_note}{resid_note}{h3_note}")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_WEAK_L_x_F_INTERACTION: cliff "
                    f"interaction_metric={interaction} in "
                    f"[{INTERACTION_H2_THRESHOLD}, "
                    f"{INTERACTION_H1_THRESHOLD}); weak cross-term signal "
                    f"(MM_TENTATIVE); consider higher TR or refined grid"
                    f"{range_note}{resid_note}{h3_note}")

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
    })
    return out


__all__ = [
    "ANCHOR_NAME", "DEVICE", "GPU_NAME", "MECH",
    "CLEANUP_MECHANISMS", "CLEANUP_REGISTRY",
    "L_GRID_CLIFF_FULL", "L_GRID_CLIFF_SMOKE",
    "F_GRID_CLIFF_FULL", "F_GRID_CLIFF_SMOKE",
    "L_GRID_DEEP_SAT_FULL", "L_GRID_DEEP_SAT_SMOKE",
    "F_GRID_DEEP_SAT_FULL", "F_GRID_DEEP_SAT_SMOKE",
    "CLIFF_N", "CLIFF_M", "CLIFF_CORR",
    "DEEP_SAT_N", "DEEP_SAT_M", "DEEP_SAT_CORR",
    "TR_FULL", "TR_SMOKE",
    "SATURATION_PC_REGIME", "SATURATION_PC_THRESHOLD",
    "NON_SAT_BAND_LO", "NON_SAT_BAND_HI",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "INTERACTION_H1_THRESHOLD", "INTERACTION_H2_THRESHOLD",
    "DEEP_SAT_INTERACTION_THRESHOLD",
    "REQUIRED_FIELDS",
    "eval_phase_point", "compute_interaction_grid", "selftest",
    "run_one_seed", "smoke_gate_predicate", "aggregate_and_verdict",
]
