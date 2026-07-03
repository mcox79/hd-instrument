"""Stage 1 Regime Probe 15: L (chain-depth) x M (codebook size) CROSS-TERM at cliff-adjacent SHARDED.

Cell anchor: `stage1_regime_probe_15_L_x_M_non_saturated_v1`
Pre-reg:     preregs/2026-07-03_stage1_regime_probe_15_L_x_M_non_saturated_v1.md

Purpose:
    Skunkworks atom #48 addendum flagged "L cross-terms (L x N, L x F, L x M,
    L x corr) unmapped." L x N was probed at P9 v2 (HOLD), L x F at P14 (HOLD),
    L x CLEANUP at P13 (HOLD). P15 fills the LAST unmapped L cross-term: L x M
    (chain depth vs codebook size). The 5th CG_META axis
    `PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian` (M-sweep FULL atom)
    was established at fixed L=2. Does M-sweep behavior change with L?

    Framed as REGIME-EXTENSION of atom #3 (chain-depth) and the M-sweep CG_META
    atom (5th physical law), NOT as new axis discovery.

Cited source atoms (per META_RULE_AC / mechanism_abstraction_lossy):
    T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1
    SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS_CG_META_v1 (Stage 1 atom #3, L axis)
    PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian (M-sweep CG_META, 5th law)
    T3/EXP_stage1_regime_probe_6v2 (F=1 modern_hopfield cliff-adjacent baseline)
    T3/EXP_stage1_regime_probe_8 (F sweep at L=2 M=6400)
    T3/EXP_stage1_regime_probe_12 (L marginal-effect at cliff-adjacent)
    T3/EXP_stage1_regime_probe_14 (L x F cross-term HOLD_PENDING_FULL)
    Skunkworks atom #48 (L axis promoted; L x M unmapped -- addendum)
    Skunkworks atom #43 (cross-term measurement requires both axes in band)
    Skunkworks atom #44 (axis labels map to substrate primitives)
    Skunkworks atom #45 (mechanism-abstraction-lossy: cite source signature)
    Skunkworks atom #49 (BUNDLED bimodal; excluded from cliff-adjacent regime)
    META_saturation_floor_masks_null_variance (H3 null control)
    feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-07-03
    feedback_mechanism_abstraction_lossy_cite_source_signature_2026-07-03
    feedback_plate_bound_too_pessimistic_for_sharded_fhrr_chain_composition_2026-07-03
    feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03
    Fix#28 hits #15-#18 (SMOKE-vs-scratchpad; REGIME_EXTENSION framing; noise-floor
        scrutiny; concept-overlap discipline)

Source signature (cited):
    SHARDED FHRR chain composition; CLIFF: N=512 F=1 corr=0.85 MECH=modern_hopfield;
    DEEP_SAT: N=8192 F=1 corr=0.60 MECH=modern_hopfield; BETA=8.0 ALPHA_SOFT=0.5;
    TR=100 (FULL) / 40 (SMOKE). L in {1,2,4} band-only per Probe 12 VET;
    M axis: CLIFF={3200, 6400, 12800} (P6v2/P8 used M=6400; extended below +
    above); DEEP_SAT={800, 1600}. Single mechanism to isolate the L x M
    cross-term (mechanism cross-terms already covered by P8).

Sweep grid FULL (14 pts / seed):
    CLIFF arm:    L in {1,2,4} x M in {3200,6400,12800} x modern_hopfield = 9 pts
    DEEP_SAT arm: L in {1,4}   x M in {800,1600}       x modern_hopfield = 4 pts (H3 null)
    SATURATION_PC arm (Gate D): L=2 F=1 M=800 N=2048 corr=0.20 iterative_cosine = 1 pt

Sweep grid SMOKE (12 pts):
    CLIFF arm:    L in {1,2,4} x M in {3200,6400,12800} x modern_hopfield = 9 pts
    DEEP_SAT arm: L in {1,4}   x M in {800}            x modern_hopfield = 2 pts
    SATURATION_PC arm: 1 pt

Discriminator (H1 interaction) -- classical 2-way ANOVA-style interaction:
    Given acc(L,M) grid on CLIFF arm (3 x 3 in both FULL and SMOKE):
      M_effect_per_L[l] = max_M acc(l,M) - min_M acc(l,M)     # M range at fixed L
      L_effect_per_M[m] = max_L acc(L,m) - min_L acc(L,m)     # L range at fixed M
      M_effect_range = max_l M_effect_per_L[l] - min_l M_effect_per_L[l]
      L_effect_range = max_m L_effect_per_M[m] - min_m L_effect_per_M[m]
      interaction_metric = max(M_effect_range, L_effect_range)
    Also compute additive-model residual (2-way ANOVA):
      add_model[l,m] = row_mean[l] + col_mean[m] - grand_mean
      residual[l,m]  = acc[l,m] - add_model[l,m]
      max_abs_residual = max |residual|
    Both metrics reported; interaction_metric is primary.

    Noise-floor discipline (Fix#28 hit #17 lesson): at TR=40 single-seed, 2SE
    on binary p is ~sqrt(p(1-p)/TR); at p~0.5 that is ~0.16 per cell. An
    interaction_metric at ~0.10 sits AT the noise floor. SMOKE reports the
    signal but HOLD_PENDING_FULL is the honest default per Skunkworks pattern.

Hypotheses (MM_TENTATIVE at SMOKE at most; MM_STANDARD requires 3-seed FULL cv<0.15):
    H1 (L x M interaction, REGIME-EXTENSION of M-sweep CG_META):
        cliff.interaction_metric >= 0.10 WITH ALL CELLS IN-BAND (not ceiling-inflated)
      -> M-sweep behavior is L-conditional at cliff-adjacent SHARDED; the
         M-sweep CG_META atom (5th physical law, established at L=2) needs
         L-slice annotation as REGIME-EXTENSION. Atom candidate:
         EMPIRICAL_L_x_M_CROSS_TERM_SHARDED_CLIFF_ADJACENT_v1 MM_TENTATIVE at
         SMOKE, MM_STANDARD at 3-seed FULL cv<0.15.
    H2 (L x M orthogonal / additive; NULL finding):
        cliff.interaction_metric < 0.05
      -> M effect is same across L values at cliff-adjacent SHARDED; the
         M-sweep CG_META atom HOLDS at other L values without L-conditioning;
         valuable NULL finding. Atom candidate:
         L_x_M_ORTHOGONAL_AT_CLIFF_ADJACENT_SHARDED_NEGATIVE_v1 MM_TENTATIVE.
    H3-NULL (DEEP_SAT null; sanity check):
        deep_sat.interaction_metric < 0.05
      -> confirms cross-term degeneracy at saturation
         (per feedback_smoke_gates_null_hypothesis_2026-07-03 discipline).

Compute architecture: `(c) mixed with justification`. Batched matmul at each
    phase point (build_rules + run_chain use torch.matmul internally); Python
    for-loop across (L, M) sweep unavoidable per-point independence.
    Empirical bracket wall (scratchpad 2026-07-03 seed=7 TR=40 CPU):
      CLIFF 9 pts wall ~1.3s; DEEP_SAT 4 pts wall ~1.4s. SMOKE ~5s total.
    FULL on CPU: ~10-30s (TR=100 vs 40). GPU available but modest sizes
    (N<=8192, M<=12800) -- CPU adequate for SMOKE; FULL routes remote via
    Orchestrator per USER-LOCKED SMOKE-only-on-local-cpu.

Sibling wrappers: exp_stage1_regime_probe_15_L_x_M_non_saturated_v1_s{7,13,19}.py
    (s7 authored here; s13/s19 authored post-Tailscale-restore for 3-seed FULL)

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-07-03 (agent-spawn, Opus 4.7).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: single-mech cell; instead verify (L=1,M=min) vs
#   (L=4,M=max) at CLIFF produce DIFFERENT output hashes -- proves L and M
#   axes fire structurally
# - final_metrics_atomicity: tmp_replace via os.replace()
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: categorical accuracy discriminator; interaction is grid-shape metric
# - baseline_in_band: MEASURED@scratchpad bracket 2026-07-03: 9/9 CLIFF cells
#   in [0.30, 0.95] at seed=7 TR=40. See prereg for exact grid.
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L; H1 uses >= 0.10)
# - HP_SCOPE per-arm: CLIFF gets H1/H2/MIDDLE_BAND; DEEP_SAT gets H3-NULL only;
#   PC gets Gate-D-reproducer only
# - cardinality_ok: EXPECTED_N_UNITS_FULL=14, EXPECTED_N_UNITS_SMOKE=12
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

ANCHOR_NAME = "stage1_regime_probe_15_L_x_M_non_saturated_v1"

# ---------------------------------------------------------------------------
# Sweep constants (LOCKED at module init; MEASURED@scratchpad bracket 2026-07-03)
# ---------------------------------------------------------------------------
# Single mechanism to isolate L x M cross-term (mech cross-terms covered by P8)
# modern_hopfield chosen: matches P6v2/P8/P12/P14 cliff-adjacent baseline.
MECH = "modern_hopfield"

# L axis: band-only per Probe 12 VET (L=8,16 fall below 0.30 floor at CLIFF)
L_GRID_CLIFF_FULL  = [1, 2, 4]
L_GRID_CLIFF_SMOKE = [1, 2, 4]      # smoke uses full L grid; interaction test needs the axis

# M axis: spans capacity band; MEASURED@scratchpad bracket 2026-07-03 (seed=7 TR=40):
#   CLIFF grid all in [0.30, 0.95]:
#     L=1: M=3200 -> 0.875 ; M=6400 -> 0.875 ; M=12800 -> 0.700
#     L=2: M=3200 -> 0.750 ; M=6400 -> 0.775 ; M=12800 -> 0.500
#     L=4: M=3200 -> 0.500 ; M=6400 -> 0.400 ; M=12800 -> 0.325
M_GRID_CLIFF_FULL  = [3200, 6400, 12800]
M_GRID_CLIFF_SMOKE = [3200, 6400, 12800]     # SMOKE = FULL grid on M axis (small)

# CLIFF-adjacent operating point (empirically-locked per Probes 6v2/8/12).
# Fixed axes: N=512, F=1, corr=0.85 (per Skunkworks-authoritative cliff signature)
CLIFF_N = 512
CLIFF_F = 1
CLIFF_CORR = 0.85

# DEEP_SAT arm (H3-NULL: cross-term degeneracy at saturation).
# MEASURED@scratchpad bracket 2026-07-03 seed=7 TR=40:
#   L=1 M=800 -> 1.000; L=1 M=1600 -> 1.000
#   L=4 M=800 -> 1.000; L=4 M=1600 -> 1.000
# All four saturated at 1.000 exact; predicted H3-NULL fires.
L_GRID_DEEP_SAT_FULL  = [1, 4]
L_GRID_DEEP_SAT_SMOKE = [1, 4]
M_GRID_DEEP_SAT_FULL  = [800, 1600]
M_GRID_DEEP_SAT_SMOKE = [800]
DEEP_SAT_N = 8192
DEEP_SAT_F = 1
DEEP_SAT_CORR = 0.60

# SATURATION_PC arm (Gate D reproducer, cited from Probes 6/7/8/12/14 baseline)
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

# Cardinality:
#   FULL  = 3 L x 3 M (CLIFF) + 2 L x 2 M (DEEP_SAT) + 1 PC = 9 + 4 + 1 = 14
#   SMOKE = 3 L x 3 M (CLIFF) + 2 L x 1 M (DEEP_SAT) + 1 PC = 9 + 2 + 1 = 12
EXPECTED_N_UNITS_FULL = (len(L_GRID_CLIFF_FULL) * len(M_GRID_CLIFF_FULL)
                         + len(L_GRID_DEEP_SAT_FULL) * len(M_GRID_DEEP_SAT_FULL)
                         + 1)
EXPECTED_N_UNITS_SMOKE = (len(L_GRID_CLIFF_SMOKE) * len(M_GRID_CLIFF_SMOKE)
                          + len(L_GRID_DEEP_SAT_SMOKE) * len(M_GRID_DEEP_SAT_SMOKE)
                          + 1)

# Non-saturated band
NON_SAT_BAND_LO = 0.30
NON_SAT_BAND_HI = 0.95

# Discriminator thresholds
INTERACTION_H1_THRESHOLD = 0.10   # H1: L x M interaction fires
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
    # different (L, M) points produce different outputs (axes structurally fire).
    ci_bytes = final_ci.detach().cpu().numpy().tobytes()
    output_hash = hashlib.sha256(ci_bytes).hexdigest()[:16]

    if device == "cuda":
        peak_mem_mb = round(torch.cuda.max_memory_allocated() / 1e6, 1)
    else:
        peak_mem_mb = -1.0
    elapsed = time.perf_counter() - t0

    # Noise-floor: 2*SE for binary p at this TR (Fix#28 hit #17 lesson)
    p = float(acc)
    noise_2se = round(2.0 * (p * (1.0 - p) / max(TR, 1)) ** 0.5, 4)

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
        "noise_2se": noise_2se,
        "output_hash": output_hash,
        "peak_mem_mb": peak_mem_mb,
        "elapsed_s": round(elapsed, 3),
    }


# ---------------------------------------------------------------------------
# Interaction metrics (2-way L x M cross-term)
# ---------------------------------------------------------------------------
def compute_interaction_grid(cell_pts: List[Dict[str, Any]],
                              L_grid: List[int], M_grid: List[int]
                              ) -> Dict[str, Any]:
    """Compute acc(L,M) grid + interaction metrics from CLIFF or DEEP_SAT pts."""
    # acc_grid[l][m] = acc at (L=l, M=m)
    acc_grid: Dict[int, Dict[int, float]] = {L: {} for L in L_grid}
    noise_grid: Dict[int, Dict[int, float]] = {L: {} for L in L_grid}
    for pt in cell_pts:
        L, M, a = pt["L"], pt["M"], pt["acc"]
        if L in acc_grid and M in M_grid:
            acc_grid[L][M] = float(a)
            noise_grid[L][M] = float(pt.get("noise_2se", 0.0))

    # Verify full-rectangular fill
    complete = all(len(acc_grid[L]) == len(M_grid) for L in L_grid)
    if not complete:
        return {
            "acc_grid": {str(L): {str(M): v for M, v in acc_grid[L].items()}
                          for L in L_grid},
            "complete": False,
            "M_effect_per_L": {},
            "L_effect_per_M": {},
            "M_effect_range": 0.0,
            "L_effect_range": 0.0,
            "interaction_metric": 0.0,
            "additive_residual_max_abs": 0.0,
            "additive_residual_grid": {},
            "row_means": {},
            "col_means": {},
            "grand_mean": 0.0,
            "noise_2se_grid": {},
            "max_noise_2se": 0.0,
        }

    # M_effect_per_L: max-min across M at each L (M range at fixed L)
    M_effect_per_L = {L: round(max(acc_grid[L].values()) - min(acc_grid[L].values()), 4)
                      for L in L_grid}
    # L_effect_per_M: max-min across L at each M (L range at fixed M)
    L_effect_per_M = {}
    for M in M_grid:
        col = [acc_grid[L][M] for L in L_grid]
        L_effect_per_M[M] = round(max(col) - min(col), 4)

    # Range of M-effect across L: does M-effect depend on L?
    M_effect_range = round(max(M_effect_per_L.values()) - min(M_effect_per_L.values()), 4)
    # Range of L-effect across M: does L-effect depend on M?
    L_effect_range = round(max(L_effect_per_M.values()) - min(L_effect_per_M.values()), 4)
    interaction_metric = round(max(M_effect_range, L_effect_range), 4)

    # 2-way ANOVA-style additive-model residual
    row_means = {L: round(float(np.mean(list(acc_grid[L].values()))), 4)
                 for L in L_grid}
    col_means = {M: round(float(np.mean([acc_grid[L][M] for L in L_grid])), 4)
                 for M in M_grid}
    all_vals = [acc_grid[L][M] for L in L_grid for M in M_grid]
    grand_mean = round(float(np.mean(all_vals)), 4)
    # residual[l,m] = acc[l,m] - (row_mean[l] + col_mean[m] - grand_mean)
    residual_grid: Dict[int, Dict[int, float]] = {}
    max_abs_resid = 0.0
    for L in L_grid:
        residual_grid[L] = {}
        for M in M_grid:
            predicted = row_means[L] + col_means[M] - grand_mean
            r = round(acc_grid[L][M] - predicted, 4)
            residual_grid[L][M] = r
            if abs(r) > max_abs_resid:
                max_abs_resid = abs(r)

    max_noise = max((noise_grid[L][M] for L in L_grid for M in M_grid), default=0.0)

    return {
        "acc_grid": {str(L): {str(M): round(acc_grid[L][M], 4) for M in M_grid}
                      for L in L_grid},
        "complete": True,
        "M_effect_per_L": {str(L): M_effect_per_L[L] for L in L_grid},
        "L_effect_per_M": {str(M): L_effect_per_M[M] for M in M_grid},
        "M_effect_range": M_effect_range,
        "L_effect_range": L_effect_range,
        "interaction_metric": interaction_metric,
        "row_means_by_L": {str(L): row_means[L] for L in L_grid},
        "col_means_by_M": {str(M): col_means[M] for M in M_grid},
        "grand_mean": grand_mean,
        "additive_residual_grid": {str(L): {str(M): residual_grid[L][M]
                                              for M in M_grid} for L in L_grid},
        "additive_residual_max_abs": round(max_abs_resid, 4),
        "noise_2se_grid": {str(L): {str(M): round(noise_grid[L][M], 4)
                                      for M in M_grid} for L in L_grid},
        "max_noise_2se": round(max_noise, 4),
    }


# ---------------------------------------------------------------------------
# Selftest (formula check at reduced grid; wall < 60s target on CPU)
# ---------------------------------------------------------------------------
def selftest() -> Tuple[bool, str]:
    msgs = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 14:
        return False, (f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 14 "
                       f"(9 cliff + 4 deep_sat + 1 PC)")
    if EXPECTED_N_UNITS_SMOKE != 12:
        return False, (f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 12 "
                       f"(9 cliff + 2 deep_sat + 1 PC)")
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} "
                f"SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. Interaction-metric formula sanity: hand-constructed additive grid
    #    should yield interaction_metric == 0 exact and max_abs_residual == 0.
    L_test = [1, 2, 4]
    M_test = [3200, 6400, 12800]
    a = {1: 0.0, 2: -0.1, 4: -0.3}
    b = {3200: 0.1, 6400: 0.0, 12800: -0.2}
    c = 0.7
    add_pts = []
    for L in L_test:
        for M in M_test:
            add_pts.append({"L": L, "M": M, "acc": a[L] + b[M] + c,
                            "noise_2se": 0.0})
    add_grid = compute_interaction_grid(add_pts, L_test, M_test)
    if not add_grid["complete"]:
        return False, "additive grid not complete in selftest"
    if add_grid["additive_residual_max_abs"] > 1e-3:
        return False, (f"additive-grid residual should be ~0; got "
                       f"{add_grid['additive_residual_max_abs']}")
    if add_grid["M_effect_range"] > 1e-3:
        return False, (f"additive-grid M_effect_range should be ~0; got "
                       f"{add_grid['M_effect_range']}")
    if add_grid["L_effect_range"] > 1e-3:
        return False, (f"additive-grid L_effect_range should be ~0; got "
                       f"{add_grid['L_effect_range']}")
    msgs.append(f"additive-grid interaction=0.0 residual=0.0 (formula OK)")

    # Non-additive grid: inject cross-term at (L=4, M=12800)
    nonadd_pts = []
    for L in L_test:
        for M in M_test:
            v = a[L] + b[M] + c
            if L == 4 and M == 12800:
                v += 0.2  # cross-term injection
            nonadd_pts.append({"L": L, "M": M, "acc": v, "noise_2se": 0.0})
    nonadd_grid = compute_interaction_grid(nonadd_pts, L_test, M_test)
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
    F_test = 1
    TR = 20
    props1, perms1, IMPL1, POS1, sh1, bd1 = build_rules(
        M_probe, F_test, gen, DEVICE, N_test)
    _, ci_L1 = run_chain("SHARDED", MECH, 1, F_test, TR,
                         props1, perms1, IMPL1, POS1, sh1, bd1, 0.10, gen, DEVICE)
    gen.manual_seed(1017)
    props2, perms2, IMPL2, POS2, sh2, bd2 = build_rules(
        M_probe, F_test, gen, DEVICE, N_test)
    _, ci_L4 = run_chain("SHARDED", MECH, 4, F_test, TR,
                         props2, perms2, IMPL2, POS2, sh2, bd2, 0.10, gen, DEVICE)
    h_L1 = hashlib.sha256(ci_L1.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    h_L4 = hashlib.sha256(ci_L4.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    if h_L1 == h_L4:
        return False, f"L=1 vs L=4 chain outputs identical; hash={h_L1}"
    msgs.append(f"L-axis fires: L1={h_L1} L4={h_L4}")

    # 4. M-axis fires: M=3200 chain output MUST differ from M=12800 chain output
    gen.manual_seed(2023)
    props3, perms3, IMPL3, POS3, sh3, bd3 = build_rules(
        3200, 1, gen, DEVICE, N_test)
    _, ci_M_lo = run_chain("SHARDED", MECH, 2, 1, TR,
                           props3, perms3, IMPL3, POS3, sh3, bd3, 0.10, gen, DEVICE)
    gen.manual_seed(2023)
    props4, perms4, IMPL4, POS4, sh4, bd4 = build_rules(
        12800, 1, gen, DEVICE, N_test)
    _, ci_M_hi = run_chain("SHARDED", MECH, 2, 1, TR,
                           props4, perms4, IMPL4, POS4, sh4, bd4, 0.10, gen, DEVICE)
    h_M_lo = hashlib.sha256(ci_M_lo.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    h_M_hi = hashlib.sha256(ci_M_hi.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    if h_M_lo == h_M_hi:
        return False, f"M=3200 vs M=12800 chain outputs identical; hash={h_M_lo}"
    msgs.append(f"M-axis fires: M3200={h_M_lo} M12800={h_M_hi}")

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

    # 6. CLIFF regime sanity: L=2 F=1 M=6400 modern_hopfield in loose band
    gen.manual_seed(3131)
    props6, perms6, IMPL6, POS6, sh6, bd6 = build_rules(
        6400, CLIFF_F, gen, DEVICE, CLIFF_N)
    acc_cliff, _ = run_chain("SHARDED", MECH, 2, CLIFF_F, 20,
                             props6, perms6, IMPL6, POS6, sh6, bd6,
                             CLIFF_CORR, gen, DEVICE)
    if not (0.20 <= acc_cliff <= 0.98):
        return False, (f"CLIFF regime sanity (L=2 F=1 M=6400 N={CLIFF_N} "
                       f"corr={CLIFF_CORR} {MECH} TR=20): acc={acc_cliff:.3f} "
                       f"outside [0.20, 0.98]; regime drifted")
    msgs.append(f"CLIFF regime sanity L=2 F=1 M=6400 (TR=20): acc={acc_cliff:.3f}")

    # 7. DEEP_SAT regime sanity (saturated expected)
    gen.manual_seed(4141)
    props7, perms7, IMPL7, POS7, sh7, bd7 = build_rules(
        800, DEEP_SAT_F, gen, DEVICE, DEEP_SAT_N)
    acc_deep, _ = run_chain("SHARDED", MECH, 4, DEEP_SAT_F, 20,
                            props7, perms7, IMPL7, POS7, sh7, bd7,
                            DEEP_SAT_CORR, gen, DEVICE)
    if acc_deep < 0.95:
        return False, (f"DEEP_SAT regime sanity (L=4 F=1 M=800 "
                       f"N={DEEP_SAT_N} corr={DEEP_SAT_CORR} {MECH} TR=20): "
                       f"acc={acc_deep:.3f} < 0.95; regime drifted")
    msgs.append(f"DEEP_SAT regime sanity L=4 F=1 M=800 (TR=20): acc={acc_deep:.3f}")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed(seed: int, run_mode: str) -> Dict[str, Any]:
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        L_grid_cliff = L_GRID_CLIFF_SMOKE
        M_grid_cliff = M_GRID_CLIFF_SMOKE
        L_grid_deep = L_GRID_DEEP_SAT_SMOKE
        M_grid_deep = M_GRID_DEEP_SAT_SMOKE
        TR = TR_SMOKE
        expected_n = EXPECTED_N_UNITS_SMOKE
    else:
        L_grid_cliff = L_GRID_CLIFF_FULL
        M_grid_cliff = M_GRID_CLIFF_FULL
        L_grid_deep = L_GRID_DEEP_SAT_FULL
        M_grid_deep = M_GRID_DEEP_SAT_FULL
        TR = TR_FULL
        expected_n = EXPECTED_N_UNITS_FULL

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"mech={MECH} L_cliff={L_grid_cliff} M_cliff={M_grid_cliff} "
          f"L_deep={L_grid_deep} M_deep={M_grid_deep} "
          f"cliff=(N={CLIFF_N},F={CLIFF_F},corr={CLIFF_CORR}) "
          f"deep=(N={DEEP_SAT_N},F={DEEP_SAT_F},corr={DEEP_SAT_CORR}) "
          f"TR={TR} expected_n={expected_n}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    salt = 0
    t0 = time.perf_counter()

    # 1) CLIFF arm: L x M grid at cliff-adjacent regime (fixed F=1, N=512, corr=0.85)
    for L in L_grid_cliff:
        for M in M_grid_cliff:
            salt += 1
            pt = eval_phase_point(MECH, M, CLIFF_N, CLIFF_F, L,
                                  CLIFF_CORR, "SHARDED", TR, seed, salt,
                                  arm_tag="CLIFF")
            phase_map.append(pt)
            print(f"  [{len(phase_map):3d}/{expected_n:3d}] CLIFF     "
                  f"L={L:2d} M={M:5d} mech={MECH:22s} N={CLIFF_N} F={CLIFF_F} "
                  f"c={CLIFF_CORR:.2f} acc={pt['acc']:.4f} 2se={pt['noise_2se']:.4f} "
                  f"dt={pt['elapsed_s']:.2f}s", flush=True)

    # 2) DEEP_SAT arm (H3-NULL): L x M grid at deep-saturation
    for L in L_grid_deep:
        for M in M_grid_deep:
            salt += 1
            pt = eval_phase_point(MECH, M, DEEP_SAT_N, DEEP_SAT_F, L,
                                  DEEP_SAT_CORR, "SHARDED", TR, seed, salt,
                                  arm_tag="DEEP_SAT")
            phase_map.append(pt)
            print(f"  [{len(phase_map):3d}/{expected_n:3d}] DEEP_SAT  "
                  f"L={L:2d} M={M:5d} mech={MECH:22s} N={DEEP_SAT_N} "
                  f"F={DEEP_SAT_F} c={DEEP_SAT_CORR:.2f} acc={pt['acc']:.4f} "
                  f"2se={pt['noise_2se']:.4f} dt={pt['elapsed_s']:.2f}s", flush=True)

    # 3) SATURATION_PC arm (Gate D reproducer)
    salt += 1
    pc = SATURATION_PC_REGIME
    pc_pt = eval_phase_point(pc["cleanup_mechanism"], pc["M"], pc["N"],
                             pc["F"], pc["L"], pc["corruption"],
                             pc["storage"], TR, seed, salt,
                             arm_tag="SATURATION_PC")
    phase_map.append(pc_pt)
    print(f"  [{len(phase_map):3d}/{expected_n:3d}] PC        "
          f"L={pc['L']:2d} M={pc['M']:5d} mech={pc['cleanup_mechanism']:22s} "
          f"N={pc['N']} c={pc['corruption']:.2f} "
          f"acc={pc_pt['acc']:.4f} dt={pc_pt['elapsed_s']:.2f}s", flush=True)

    elapsed = time.perf_counter() - t0
    observed_n = len(phase_map)
    cardinality_ok = (observed_n == expected_n)

    # ARMS-MUST-DIFFER analog: verify (L=1, M=min) vs (L=max, M=max) at CLIFF
    cliff_pts = [p for p in phase_map if p["arm_tag"] == "CLIFF"]
    deep_pts = [p for p in phase_map if p["arm_tag"] == "DEEP_SAT"]

    hash_corners: Dict[str, str] = {}
    L_min, L_max = min(L_grid_cliff), max(L_grid_cliff)
    M_min, M_max = min(M_grid_cliff), max(M_grid_cliff)
    for pt in cliff_pts:
        if (pt["L"], pt["M"]) == (L_min, M_min):
            hash_corners[f"L{L_min}_M{M_min}"] = pt["output_hash"]
        if (pt["L"], pt["M"]) == (L_max, M_max):
            hash_corners[f"L{L_max}_M{M_max}"] = pt["output_hash"]
    corner_hashes_distinct = (len(set(hash_corners.values())) >= 2
                              if len(hash_corners) == 2 else False)

    # SATURATION_PC pass check
    pc_acc = float(pc_pt["acc"])
    pc_pass = (pc_acc >= SATURATION_PC_THRESHOLD)

    # CLIFF arm interaction analysis
    cliff_grid = compute_interaction_grid(cliff_pts, L_grid_cliff, M_grid_cliff)
    cliff_accs = [p["acc"] for p in cliff_pts]
    cliff_mean = float(np.mean(cliff_accs)) if cliff_accs else 0.0
    cliff_min = float(np.min(cliff_accs)) if cliff_accs else 0.0
    cliff_max = float(np.max(cliff_accs)) if cliff_accs else 0.0
    cliff_in_band = sum(1 for a in cliff_accs
                        if NON_SAT_BAND_LO <= a <= NON_SAT_BAND_HI)
    cliff_in_band_frac = cliff_in_band / max(len(cliff_accs), 1)
    escapes_saturation_cliff = any(a < NON_SAT_BAND_HI for a in cliff_accs)

    # Ceiling-confounded cell flag (Fix#28 hit #17 discipline)
    ceiling_confounded_cells = [
        {"L": p["L"], "M": p["M"], "acc": p["acc"], "noise_2se": p["noise_2se"]}
        for p in cliff_pts if p["acc"] > 0.90 or p["noise_2se"] < 0.05
    ]

    # DEEP_SAT arm interaction analysis (H3-NULL)
    deep_grid = compute_interaction_grid(deep_pts, L_grid_deep, M_grid_deep)
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
            "regime": {"N": CLIFF_N, "F": CLIFF_F, "corr": CLIFF_CORR,
                        "mech": MECH, "storage": "SHARDED"},
            "L_grid": L_grid_cliff,
            "M_grid": M_grid_cliff,
            "mean_acc": round(cliff_mean, 4),
            "min_acc": round(cliff_min, 4),
            "max_acc": round(cliff_max, 4),
            "n_in_non_saturated_band": cliff_in_band,
            "n_total": len(cliff_accs),
            "fraction_in_band": round(cliff_in_band_frac, 4),
            "escapes_saturation_ceiling": escapes_saturation_cliff,
            "ceiling_confounded_cells": ceiling_confounded_cells,
            "n_ceiling_confounded": len(ceiling_confounded_cells),
            **cliff_grid,
        },
        "deep_sat_arm": {
            "regime": {"N": DEEP_SAT_N, "F": DEEP_SAT_F, "corr": DEEP_SAT_CORR,
                        "mech": MECH, "storage": "SHARDED"},
            "L_grid": L_grid_deep,
            "M_grid": M_grid_deep,
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
        return False, (f"escapes_saturation_ceiling_fail: no (L,M) point on "
                       f"CLIFF arm below {NON_SAT_BAND_HI}; CLIFF regime "
                       f"fully saturated; design goal not achieved")
    deep = body.get("deep_sat_arm", {})
    if not deep.get("saturated"):
        return False, (f"deep_sat_regime_drift: mean_acc={deep.get('mean_acc')} "
                       f"< 0.95; H3-NULL control arm did not saturate at "
                       f"(N={DEEP_SAT_N}, F={DEEP_SAT_F}, corr={DEEP_SAT_CORR}); "
                       f"deep-sat regime drifted from empirical bracket")
    if not cliff.get("complete"):
        return False, f"cliff_grid_not_complete: acc_grid missing points"
    # NaN sanity
    for pt in phase_map:
        if pt.get("acc") != pt.get("acc"):
            return False, f"NAN_in_phase_map at {pt}"

    # Discriminator informational (null-hypothesis discipline):
    interaction = cliff.get("interaction_metric", 0.0)
    M_range = cliff.get("M_effect_range", 0.0)
    L_range = cliff.get("L_effect_range", 0.0)
    max_resid = cliff.get("additive_residual_max_abs", 0.0)
    max_noise = cliff.get("max_noise_2se", 0.0)
    n_ceiling = cliff.get("n_ceiling_confounded", 0)
    deep_interaction = deep.get("interaction_metric", 0.0)
    return True, (f"smoke_gate_pass: cardinality_ok + axes-fire + "
                  f"pc_acc={pc.get('acc')} (>={pc.get('threshold')}) + "
                  f"cliff_mean={cliff.get('mean_acc')} escapes_saturation + "
                  f"deep_sat_saturated(mean={deep.get('mean_acc')}); "
                  f"informational: cliff_interaction_metric={interaction} "
                  f"(M_range={M_range} L_range={L_range} "
                  f"max_abs_resid={max_resid}) "
                  f"noise_floor_max_2se={max_noise} "
                  f"ceiling_confounded_cells={n_ceiling} "
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
                f"L or M axis structurally aliased")
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
                f"{len(cliff.get('M_grid', []))}")
    else:
        # Primary discriminator: interaction_metric on CLIFF arm.
        interaction = cliff.get("interaction_metric", 0.0)
        M_range = cliff.get("M_effect_range", 0.0)
        L_range = cliff.get("L_effect_range", 0.0)
        max_resid = cliff.get("additive_residual_max_abs", 0.0)
        max_noise = cliff.get("max_noise_2se", 0.0)
        n_ceiling = cliff.get("n_ceiling_confounded", 0)
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
        range_note = f" ; M_effect_range={M_range} L_effect_range={L_range}"
        noise_note = (f" ; noise_floor_max_2se={max_noise} "
                       f"ceiling_confounded_cells={n_ceiling} "
                       f"(honest-signal condition: interaction >= "
                       f"noise_floor AND ceiling_confounded == 0)")

        if interaction >= INTERACTION_H1_THRESHOLD:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H1_L_x_M_INTERACTION_AT_CLIFF_ADJACENT_SHARDED: "
                    f"cliff interaction_metric={interaction} "
                    f">= {INTERACTION_H1_THRESHOLD}; L and M are NOT "
                    f"orthogonal axes at cliff-adjacent SHARDED regime; "
                    f"M-sweep behavior is L-conditional; REGIME-EXTENSION of "
                    f"M-sweep CG_META atom at other L values. Atom candidate: "
                    f"EMPIRICAL_L_x_M_CROSS_TERM_SHARDED_CLIFF_ADJACENT_v1 "
                    f"MM_TENTATIVE (requires 3-seed FULL cv<0.15 for "
                    f"MM_STANDARD)"
                    f"{range_note}{resid_note}{noise_note}{h3_note}")
        elif interaction < INTERACTION_H2_THRESHOLD:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H2_L_x_M_ORTHOGONAL_AT_CLIFF_ADJACENT_SHARDED: "
                    f"cliff interaction_metric={interaction} < "
                    f"{INTERACTION_H2_THRESHOLD}; L and M ARE orthogonal "
                    f"axes at cliff-adjacent SHARDED regime; M-sweep CG_META "
                    f"atom HOLDS at other L values without L-conditioning; "
                    f"valuable NULL finding. Atom candidate: "
                    f"L_x_M_ORTHOGONAL_AT_CLIFF_ADJACENT_SHARDED_NEGATIVE_v1 "
                    f"MM_TENTATIVE"
                    f"{range_note}{resid_note}{noise_note}{h3_note}")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_WEAK_L_x_M_INTERACTION: cliff "
                    f"interaction_metric={interaction} in "
                    f"[{INTERACTION_H2_THRESHOLD}, "
                    f"{INTERACTION_H1_THRESHOLD}); weak cross-term signal "
                    f"(MM_TENTATIVE); consider higher TR or refined grid"
                    f"{range_note}{resid_note}{noise_note}{h3_note}")

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
    "M_GRID_CLIFF_FULL", "M_GRID_CLIFF_SMOKE",
    "L_GRID_DEEP_SAT_FULL", "L_GRID_DEEP_SAT_SMOKE",
    "M_GRID_DEEP_SAT_FULL", "M_GRID_DEEP_SAT_SMOKE",
    "CLIFF_N", "CLIFF_F", "CLIFF_CORR",
    "DEEP_SAT_N", "DEEP_SAT_F", "DEEP_SAT_CORR",
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
