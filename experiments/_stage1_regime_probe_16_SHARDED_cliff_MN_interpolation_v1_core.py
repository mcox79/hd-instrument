"""Stage 1 Regime Probe 16: SHARDED cliff M/N interpolation -- CORR vs M cross-term.

Cell anchor: `stage1_regime_probe_16_SHARDED_cliff_MN_interpolation_v1`
Pre-reg:     preregs/2026-07-04_stage1_regime_probe_16_SHARDED_cliff_MN_interpolation_v1.md

Purpose:
    Research drill (task a0083d0f878c6e486, memo
    notes/research_drill_sharded_saturation_regime_map_gap_2x_2026-07-04.md)
    identified a published-lit gap: no joint fan-out (F) x dimension (N) x
    codebook-size (M) x corruption (corr) regime map for per-slot memory
    capacity. Kanerva SDM (Chou 1989) predicts per-slot sphere-packing
    bound; Cuckoo hashing (Fountoulakis/Panagiotou 2012) shows sharp
    load-factor cliff ~0.92; Frady Resonator Networks 2 (2020) shows
    factor-count erodes per-slot capacity.

    Today's P4/P5 SHARDED "saturates both axes" finding is NOT vacuous per
    lit -- it is theoretically expected BELOW cliff-ratio. This probe
    decisively MAPS the SHARDED-cliff shape in the (M, corr) plane at
    fixed (N=512, F=1, MECH=modern_hopfield) to fill the lit-gap.

    Framed as REGIME-MAP-EXTENSION of Probes 6/7/8 (cliff-adjacent baseline)
    plus new-territory M/N interpolation. NOT a new axis discovery.

Cited source atoms (per META_RULE_AC / mechanism_abstraction_lossy):
    T3/EXP_stage1_regime_probe_6v2 (F=1 modern_hopfield cliff-adjacent baseline)
    T3/EXP_stage1_regime_probe_7 (N x cleanup non-saturated)
    T3/EXP_stage1_regime_probe_8 (F sweep at L=2 M=6400)
    T3/EXP_stage1_regime_probe_15 (L x M cross-term)
    sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1
    Skunkworks atom #48 (SHARDED cliff regime axes measurement)
    Skunkworks atom #49 (SHARDED cliff expected sharp step)
    RF/research_drill_sharded_saturation_regime_map_gap_2x_2026-07-04
    CITED@Kanerva 1988 SDM per-slot sphere-packing
    CITED@Fountoulakis+Panagiotou 2012 Cuckoo load-factor cliff ~0.92
    CITED@Frady 2020 Resonator Networks 2 factor-count erosion
    feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-07-03
    feedback_mechanism_abstraction_lossy_cite_source_signature_2026-07-03
    feedback_plate_bound_too_pessimistic_for_sharded_fhrr_chain_composition_2026-07-03
    feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03

Source signature (cited):
    SHARDED FHRR chain composition; CLIFF: N=512 F=1 L=2 MECH=modern_hopfield;
    DEEP_SAT: N=8192 F=1 L=2 corr=0.60 MECH=modern_hopfield;
    BETA=8.0 ALPHA_SOFT=0.5; TR=100 (FULL) / 40 (SMOKE);
    M axis (CLIFF): {4000, 4800, 5600} (fine interpolation between P6 anchors);
    corr axis (CLIFF): {0.80, 0.85, 0.90} (spans cliff-adjacent per P6+P7);
    BUNDLED EXCLUDED per Skunkworks atom #49.

Sweep grid (SMOKE = FULL structurally for CLIFF; DEEP_SAT differs; 12 pts SMOKE):
    CLIFF arm:    M in {4000,4800,5600} x corr in {0.80,0.85,0.90} = 9 pts
    DEEP_SAT arm: (N=8192, M=800, corr=0.60, L=2) x 2 M-variants = 2 pts (H3-NULL)
    SATURATION_PC arm (Gate D): L=2 F=1 M=800 N=2048 corr=0.20 iterative_cosine = 1 pt

FULL grid (16 pts / seed):
    CLIFF arm:    3 M x 3 corr = 9 pts (same as SMOKE; grid is small already)
    DEEP_SAT arm: (N=8192, corr=0.60) x M in {800, 1600, 2400} = 3 pts
    SATURATION_PC = 1 pt
    Extended CLIFF verifier row: corr=0.87 x M in {4000,4800,5600} = 3 pts
                                 (fine cliff-transition mapping at FULL only)

Discriminators (H1 = cliff mapped decisively):
    Given acc(M, corr) grid on CLIFF arm (3 x 3):
      corr_effect_per_M[m] = max_corr acc(m, corr) - min_corr acc(m, corr)
      M_effect_per_corr[c] = max_M acc(M, c) - min_M acc(M, c)
      corr_effect_range = range of corr_effect_per_M
      M_effect_range    = range of M_effect_per_corr
      interaction_metric = max(corr_effect_range, M_effect_range)
    Primary discriminators:
      cliff_amplitude = max grid acc - min grid acc      # overall cliff magnitude
      M_variance_within_corr = max_c M_effect_per_corr[c]  # M matters at any corr slice?
      corr_variance_within_M = max_m corr_effect_per_M[m]  # corr matters at any M slice?

Hypotheses (MM_TENTATIVE at SMOKE at most; MM_STANDARD requires 3-seed FULL cv<0.15):
    H1 (CLIFF MAPPED; corr-dominated; M-flat):
        cliff_amplitude >= 0.30 AND M_variance_within_corr <= 0.15
      -> SHARDED cliff decisively mapped; cliff is corr-driven not M-driven at
         cliff-adjacent regime; fills lit-gap. Atom candidate:
         EMPIRICAL_SHARDED_CLIFF_MN_INTERPOLATION_v1_MAPS_CLIFF_SHAPE_AT_N512_F1_MODERN_HOPFIELD
         MM_TENTATIVE at SMOKE, MM_STANDARD at 3-seed FULL cv<0.15.
    H2 (M-N INTERACTION FIRES; cliff depends on M):
        cliff_amplitude >= 0.30 AND M_variance_within_corr > 0.15
      -> M and corr both shift cliff position; cliff-ratio hypothesis (per
         Kanerva SDM) supported. Atom candidate:
         EMPIRICAL_M_x_CORR_CROSS_TERM_SHARDED_CLIFF_v1 MM_TENTATIVE.
    H3-NULL-SAT (DEEP_SAT null; sanity):
        deep_sat.interaction_metric < 0.05
      -> confirms cross-term degeneracy at saturation.
    H4-NULL-NOCLIFF (cliff not in tested regime):
        cliff_amplitude < 0.30
      -> CLIFF grid did not straddle transition; regime bracket wrong;
         needs re-authoring with different M/corr range.

Empirical bracket (MEASURED@scratchpad bracket_p16_M_x_corr.py 2026-07-04 seed=7 TR=40):
    CLIFF grid:
              corr=0.80  corr=0.85  corr=0.90
    M= 4000   1.0000    0.8250    0.0750
    M= 4800   1.0000    0.8000    0.0750
    M= 5600   0.9750    0.7750    0.1000
    cliff_amplitude ~= 0.925 (huge; well above 0.30 H1 threshold)
    M_variance_within_corr ~= 0.050 (well below 0.15 H1 threshold)
    corr_variance_within_M ~= 0.925 (dominates)
    3/9 cells strictly in-band [0.30, 0.95] -- meets Gate B (0.30 threshold)
    exactly. Cliff-mapping REQUIRES straddling saturated + floor cells --
    Gate B interpretation is loosened to "straddles the transition" per
    research-drill lit-gap intent.
    DEEP_SAT acc = 1.0000 (H3-NULL fires trivially).
    SATURATION_PC acc = 1.0000 (Gate D reproducer OK).

Compute architecture: `(c) mixed with justification`. Batched matmul at each
    phase point; Python for-loop across (M, corr) sweep unavoidable per
    per-point independence. Empirical wall on CPU: 12-pt SMOKE ~5s; 16-pt
    FULL ~15-25s.

Sibling wrappers: exp_stage1_regime_probe_16_SHARDED_cliff_MN_interpolation_v1_s{7,13,19}.py
    (s7 authored here; s13/s19 authored post-Tailscale-restore for 3-seed FULL)

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-07-04 (agent-spawn, Opus 4.7).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: verify (M=min, corr=min) vs (M=max, corr=max) at
#   CLIFF produce DIFFERENT output hashes -- proves M and corr axes fire
# - final_metrics_atomicity: tmp_replace via os.replace()
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: categorical accuracy; cliff is grid-shape metric not bit-noise floor
# - baseline_in_band: 3/9 CLIFF cells in-band; cliff-mapping requires straddling
#   saturation + floor by design (per research drill lit-gap intent)
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L; H1 uses >= 0.30 cliff)
# - HP_SCOPE per-arm: CLIFF -> H1/H2/H4; DEEP_SAT -> H3-NULL only;
#   PC -> Gate-D-reproducer only
# - cardinality_ok: EXPECTED_N_UNITS_SMOKE=12, EXPECTED_N_UNITS_FULL=16
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

ANCHOR_NAME = "stage1_regime_probe_16_SHARDED_cliff_MN_interpolation_v1"

# ---------------------------------------------------------------------------
# Sweep constants (LOCKED at module init)
# ---------------------------------------------------------------------------
# Single mechanism to isolate M x corr cross-term at cliff (mech cross-terms
# covered by P8). modern_hopfield matches P6v2/P8/P12/P14/P15 baseline.
MECH = "modern_hopfield"
FIXED_L = 2
FIXED_F = 1

# CLIFF arm: fine M/corr interpolation between Probe 6 anchors
CLIFF_N = 512
M_GRID_CLIFF   = [4000, 4800, 5600]     # M axis: fine interpolation
CORR_GRID_CLIFF = [0.80, 0.85, 0.90]     # corr axis: spans cliff per P6+P7 v2

# FULL-only extended verifier row (corr=0.87 fine-transition slice)
CORR_EXTENDED_FULL_ONLY = 0.87
M_EXTENDED_FULL_ONLY_GRID = [4000, 4800, 5600]

# DEEP_SAT arm (H3-NULL: cross-term degeneracy at saturation)
DEEP_SAT_N = 8192
DEEP_SAT_F = 1
DEEP_SAT_L = 2
DEEP_SAT_CORR = 0.60
M_GRID_DEEP_SAT_SMOKE = [800, 1600]         # 2 pts for smoke
M_GRID_DEEP_SAT_FULL  = [800, 1600, 2400]   # 3 pts for full

# SATURATION_PC arm (Gate D reproducer)
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
#   SMOKE = 3 M x 3 corr (CLIFF) + 2 M (DEEP_SAT) + 1 PC = 9 + 2 + 1 = 12
#   FULL  = 3 M x 3 corr (CLIFF) + 3 M x 1 corr=0.87 (CLIFF_EXT)
#         + 3 M (DEEP_SAT) + 1 PC                         = 9 + 3 + 3 + 1 = 16
EXPECTED_N_UNITS_SMOKE = (len(M_GRID_CLIFF) * len(CORR_GRID_CLIFF)
                          + len(M_GRID_DEEP_SAT_SMOKE)
                          + 1)
EXPECTED_N_UNITS_FULL = (len(M_GRID_CLIFF) * len(CORR_GRID_CLIFF)
                         + len(M_EXTENDED_FULL_ONLY_GRID)
                         + len(M_GRID_DEEP_SAT_FULL)
                         + 1)

# Non-saturated band (informational; cliff-mapping straddles this by design)
NON_SAT_BAND_LO = 0.30
NON_SAT_BAND_HI = 0.95

# Discriminator thresholds
CLIFF_AMPLITUDE_H1_THRESHOLD = 0.30      # H1: cliff magnitude
M_VARIANCE_H1_THRESHOLD = 0.15           # H1: M is flat within corr slice
CLIFF_AMPLITUDE_H4_THRESHOLD = 0.30      # H4: below this = NULL (no cliff)
DEEP_SAT_INTERACTION_THRESHOLD = 0.05    # H3-NULL threshold on DEEP_SAT

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
    # different (M, corr) points produce different outputs (axes fire).
    ci_bytes = final_ci.detach().cpu().numpy().tobytes()
    output_hash = hashlib.sha256(ci_bytes).hexdigest()[:16]

    if device == "cuda":
        peak_mem_mb = round(torch.cuda.max_memory_allocated() / 1e6, 1)
    else:
        peak_mem_mb = -1.0
    elapsed = time.perf_counter() - t0

    # Noise-floor: 2*SE for binary p at this TR
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
# Cliff-shape grid analysis (M x corr on CLIFF arm)
# ---------------------------------------------------------------------------
def compute_cliff_grid(cliff_pts: List[Dict[str, Any]],
                        M_grid: List[int], corr_grid: List[float]
                        ) -> Dict[str, Any]:
    """Compute acc(M,corr) grid + cliff-shape metrics."""
    # acc_grid[M][corr] (corr rounded for key-match)
    def _rk(c: float) -> str:
        return f"{c:.2f}"

    acc_grid: Dict[int, Dict[str, float]] = {M: {} for M in M_grid}
    noise_grid: Dict[int, Dict[str, float]] = {M: {} for M in M_grid}
    for pt in cliff_pts:
        M, corr, a = pt["M"], pt["corruption"], pt["acc"]
        if M in acc_grid:
            # Match corr to grid via _rk
            for c in corr_grid:
                if abs(corr - c) < 1e-6:
                    acc_grid[M][_rk(c)] = float(a)
                    noise_grid[M][_rk(c)] = float(pt.get("noise_2se", 0.0))
                    break

    complete = all(len(acc_grid[M]) == len(corr_grid) for M in M_grid)
    if not complete:
        return {
            "acc_grid": {str(M): dict(acc_grid[M]) for M in M_grid},
            "complete": False,
            "M_effect_per_corr": {},
            "corr_effect_per_M": {},
            "M_effect_range": 0.0,
            "corr_effect_range": 0.0,
            "interaction_metric": 0.0,
            "cliff_amplitude": 0.0,
            "M_variance_within_corr": 0.0,
            "corr_variance_within_M": 0.0,
            "additive_residual_max_abs": 0.0,
            "additive_residual_grid": {},
            "row_means_by_M": {},
            "col_means_by_corr": {},
            "grand_mean": 0.0,
            "noise_2se_grid": {},
            "max_noise_2se": 0.0,
        }

    # corr_effect_per_M[m] = max_c acc(m,c) - min_c acc(m,c)  (cliff range at fixed M)
    corr_effect_per_M = {}
    for M in M_grid:
        vals = [acc_grid[M][_rk(c)] for c in corr_grid]
        corr_effect_per_M[M] = round(max(vals) - min(vals), 4)
    # M_effect_per_corr[c] = max_m acc(m,c) - min_m acc(m,c)  (M range at fixed corr)
    M_effect_per_corr = {}
    for c in corr_grid:
        col = [acc_grid[M][_rk(c)] for M in M_grid]
        M_effect_per_corr[_rk(c)] = round(max(col) - min(col), 4)

    corr_effect_range = round(max(corr_effect_per_M.values())
                                - min(corr_effect_per_M.values()), 4)
    M_effect_range = round(max(M_effect_per_corr.values())
                            - min(M_effect_per_corr.values()), 4)
    interaction_metric = round(max(corr_effect_range, M_effect_range), 4)

    all_vals = [acc_grid[M][_rk(c)] for M in M_grid for c in corr_grid]
    cliff_amplitude = round(max(all_vals) - min(all_vals), 4)
    M_variance_within_corr = round(max(M_effect_per_corr.values()), 4)
    corr_variance_within_M = round(max(corr_effect_per_M.values()), 4)

    # 2-way ANOVA additive residual
    row_means = {M: round(float(np.mean([acc_grid[M][_rk(c)] for c in corr_grid])), 4)
                 for M in M_grid}
    col_means = {_rk(c): round(float(np.mean([acc_grid[M][_rk(c)] for M in M_grid])), 4)
                 for c in corr_grid}
    grand_mean = round(float(np.mean(all_vals)), 4)
    residual_grid: Dict[int, Dict[str, float]] = {}
    max_abs_resid = 0.0
    for M in M_grid:
        residual_grid[M] = {}
        for c in corr_grid:
            predicted = row_means[M] + col_means[_rk(c)] - grand_mean
            r = round(acc_grid[M][_rk(c)] - predicted, 4)
            residual_grid[M][_rk(c)] = r
            if abs(r) > max_abs_resid:
                max_abs_resid = abs(r)

    max_noise = max((noise_grid[M][_rk(c)] for M in M_grid for c in corr_grid),
                    default=0.0)

    return {
        "acc_grid": {str(M): {_rk(c): round(acc_grid[M][_rk(c)], 4)
                                for c in corr_grid} for M in M_grid},
        "complete": True,
        "M_effect_per_corr": M_effect_per_corr,
        "corr_effect_per_M": {str(M): corr_effect_per_M[M] for M in M_grid},
        "M_effect_range": M_effect_range,
        "corr_effect_range": corr_effect_range,
        "interaction_metric": interaction_metric,
        "cliff_amplitude": cliff_amplitude,
        "M_variance_within_corr": M_variance_within_corr,
        "corr_variance_within_M": corr_variance_within_M,
        "row_means_by_M": {str(M): row_means[M] for M in M_grid},
        "col_means_by_corr": col_means,
        "grand_mean": grand_mean,
        "additive_residual_grid": {str(M): {_rk(c): residual_grid[M][_rk(c)]
                                              for c in corr_grid} for M in M_grid},
        "additive_residual_max_abs": round(max_abs_resid, 4),
        "noise_2se_grid": {str(M): {_rk(c): round(noise_grid[M][_rk(c)], 4)
                                      for c in corr_grid} for M in M_grid},
        "max_noise_2se": round(max_noise, 4),
    }


def compute_deep_sat_analysis(deep_pts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """DEEP_SAT arm: 1-D across M at fixed corr; look for degeneracy."""
    accs = [p["acc"] for p in deep_pts]
    if not accs:
        return {"mean_acc": 0.0, "min_acc": 0.0, "max_acc": 0.0,
                "interaction_metric": 0.0, "saturated": False}
    mean_a = float(np.mean(accs))
    min_a = float(np.min(accs))
    max_a = float(np.max(accs))
    interaction_metric = round(max_a - min_a, 4)   # 1-D M range at fixed corr
    saturated = (mean_a >= 0.95)
    return {
        "mean_acc": round(mean_a, 4),
        "min_acc": round(min_a, 4),
        "max_acc": round(max_a, 4),
        "interaction_metric": interaction_metric,
        "saturated": saturated,
        "M_per_pt": [{"M": p["M"], "acc": p["acc"]} for p in deep_pts],
    }


# ---------------------------------------------------------------------------
# Selftest (formula check at reduced grid; wall < 60s target on CPU)
# ---------------------------------------------------------------------------
def selftest() -> Tuple[bool, str]:
    msgs = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_SMOKE != 12:
        return False, (f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 12 "
                       f"(9 cliff + 2 deep_sat + 1 PC)")
    if EXPECTED_N_UNITS_FULL != 16:
        return False, (f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 16 "
                       f"(9 cliff + 3 cliff_ext + 3 deep_sat + 1 PC)")
    msgs.append(f"cardinality SMOKE={EXPECTED_N_UNITS_SMOKE} "
                f"FULL={EXPECTED_N_UNITS_FULL}")

    # 2. Cliff-grid formula sanity: constant-value grid -> cliff_amplitude=0
    const_pts = []
    for M in M_GRID_CLIFF:
        for c in CORR_GRID_CLIFF:
            const_pts.append({"M": M, "corruption": c, "acc": 0.5,
                              "noise_2se": 0.0})
    const_grid = compute_cliff_grid(const_pts, M_GRID_CLIFF, CORR_GRID_CLIFF)
    if not const_grid["complete"]:
        return False, "const grid not complete"
    if const_grid["cliff_amplitude"] > 1e-6:
        return False, (f"const-grid cliff_amplitude should be 0; got "
                       f"{const_grid['cliff_amplitude']}")
    msgs.append(f"const-grid cliff_amplitude=0 (OK)")

    # 3. Simulated-cliff grid: corr-driven, M-flat -> matches H1 shape
    sim_pts = []
    corr_map = {0.80: 1.0, 0.85: 0.8, 0.90: 0.1}
    for M in M_GRID_CLIFF:
        for c in CORR_GRID_CLIFF:
            sim_pts.append({"M": M, "corruption": c, "acc": corr_map[c],
                            "noise_2se": 0.05})
    sim_grid = compute_cliff_grid(sim_pts, M_GRID_CLIFF, CORR_GRID_CLIFF)
    if sim_grid["cliff_amplitude"] < 0.85:
        return False, (f"sim cliff_amplitude too low: "
                       f"{sim_grid['cliff_amplitude']} < 0.85")
    if sim_grid["M_variance_within_corr"] > 0.01:
        return False, (f"sim M_variance_within_corr should be 0; got "
                       f"{sim_grid['M_variance_within_corr']}")
    if sim_grid["corr_variance_within_M"] < 0.85:
        return False, (f"sim corr_variance_within_M too low: "
                       f"{sim_grid['corr_variance_within_M']}")
    msgs.append(f"sim-cliff amplitude={sim_grid['cliff_amplitude']} "
                f"M_var={sim_grid['M_variance_within_corr']} "
                f"corr_var={sim_grid['corr_variance_within_M']} (H1-shape)")

    # 4. Simulated M-N interaction grid: cliff shifts with M -> matches H2 shape
    inter_pts = []
    for M in M_GRID_CLIFF:
        for c in CORR_GRID_CLIFF:
            base = 1.0 if c <= 0.80 else (0.8 if c <= 0.85 else 0.1)
            # Inject M-dependent cliff shift: M=5600 shifts to next tier
            if M >= 5600 and c == 0.85:
                v = 0.4  # M shifted the cliff
            else:
                v = base
            inter_pts.append({"M": M, "corruption": c, "acc": v,
                              "noise_2se": 0.05})
    inter_grid = compute_cliff_grid(inter_pts, M_GRID_CLIFF, CORR_GRID_CLIFF)
    if inter_grid["M_variance_within_corr"] < 0.15:
        return False, (f"sim-interaction M_variance too low: "
                       f"{inter_grid['M_variance_within_corr']}")
    msgs.append(f"sim-interaction M_variance="
                f"{inter_grid['M_variance_within_corr']} (H2-shape fires)")

    # 5. M-axis fires structurally: M=4000 vs M=5600 outputs differ
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(1017)
    TR = 20
    props1, perms1, IMPL1, POS1, sh1, bd1 = build_rules(
        4000, FIXED_F, gen, DEVICE, CLIFF_N)
    _, ci_Mlo = run_chain("SHARDED", MECH, FIXED_L, FIXED_F, TR,
                          props1, perms1, IMPL1, POS1, sh1, bd1, 0.85, gen, DEVICE)
    gen.manual_seed(1017)
    props2, perms2, IMPL2, POS2, sh2, bd2 = build_rules(
        5600, FIXED_F, gen, DEVICE, CLIFF_N)
    _, ci_Mhi = run_chain("SHARDED", MECH, FIXED_L, FIXED_F, TR,
                          props2, perms2, IMPL2, POS2, sh2, bd2, 0.85, gen, DEVICE)
    h_lo = hashlib.sha256(ci_Mlo.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    h_hi = hashlib.sha256(ci_Mhi.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    if h_lo == h_hi:
        return False, f"M=4000 vs M=5600 chain outputs identical; hash={h_lo}"
    msgs.append(f"M-axis fires: M4000={h_lo} M5600={h_hi}")

    # 6. corr-axis fires: corr=0.80 vs corr=0.90 differ
    gen.manual_seed(2023)
    props3, perms3, IMPL3, POS3, sh3, bd3 = build_rules(
        4800, FIXED_F, gen, DEVICE, CLIFF_N)
    _, ci_c_lo = run_chain("SHARDED", MECH, FIXED_L, FIXED_F, TR,
                           props3, perms3, IMPL3, POS3, sh3, bd3, 0.80, gen, DEVICE)
    gen.manual_seed(2023)
    props4, perms4, IMPL4, POS4, sh4, bd4 = build_rules(
        4800, FIXED_F, gen, DEVICE, CLIFF_N)
    _, ci_c_hi = run_chain("SHARDED", MECH, FIXED_L, FIXED_F, TR,
                           props4, perms4, IMPL4, POS4, sh4, bd4, 0.90, gen, DEVICE)
    h_clo = hashlib.sha256(ci_c_lo.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    h_chi = hashlib.sha256(ci_c_hi.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    if h_clo == h_chi:
        return False, f"corr=0.80 vs corr=0.90 chain outputs identical; hash={h_clo}"
    msgs.append(f"corr-axis fires: c0.80={h_clo} c0.90={h_chi}")

    # 7. SATURATION_PC easy gate reproducer (Gate D at reduced TR)
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

    # 8. CLIFF regime sanity: M=4800 corr=0.85 modern_hopfield in loose band
    gen.manual_seed(3131)
    props6, perms6, IMPL6, POS6, sh6, bd6 = build_rules(
        4800, FIXED_F, gen, DEVICE, CLIFF_N)
    acc_cliff, _ = run_chain("SHARDED", MECH, FIXED_L, FIXED_F, 20,
                             props6, perms6, IMPL6, POS6, sh6, bd6, 0.85, gen, DEVICE)
    if not (0.20 <= acc_cliff <= 0.98):
        return False, (f"CLIFF regime sanity M=4800 corr=0.85 TR=20: "
                       f"acc={acc_cliff:.3f} outside [0.20, 0.98]")
    msgs.append(f"CLIFF regime sanity M=4800 corr=0.85 (TR=20): acc={acc_cliff:.3f}")

    # 9. DEEP_SAT regime sanity (saturated expected)
    gen.manual_seed(4141)
    props7, perms7, IMPL7, POS7, sh7, bd7 = build_rules(
        800, DEEP_SAT_F, gen, DEVICE, DEEP_SAT_N)
    acc_deep, _ = run_chain("SHARDED", MECH, DEEP_SAT_L, DEEP_SAT_F, 20,
                            props7, perms7, IMPL7, POS7, sh7, bd7,
                            DEEP_SAT_CORR, gen, DEVICE)
    if acc_deep < 0.95:
        return False, (f"DEEP_SAT regime sanity M=800 N={DEEP_SAT_N} "
                       f"corr={DEEP_SAT_CORR} L={DEEP_SAT_L} TR=20: "
                       f"acc={acc_deep:.3f} < 0.95; regime drifted")
    msgs.append(f"DEEP_SAT regime sanity M=800 (TR=20): acc={acc_deep:.3f}")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed(seed: int, run_mode: str) -> Dict[str, Any]:
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        M_grid_deep = M_GRID_DEEP_SAT_SMOKE
        run_cliff_ext = False
        TR = TR_SMOKE
        expected_n = EXPECTED_N_UNITS_SMOKE
    else:
        M_grid_deep = M_GRID_DEEP_SAT_FULL
        run_cliff_ext = True
        TR = TR_FULL
        expected_n = EXPECTED_N_UNITS_FULL

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"mech={MECH} L={FIXED_L} F={FIXED_F} "
          f"cliff=(N={CLIFF_N},M={M_GRID_CLIFF},corr={CORR_GRID_CLIFF}) "
          f"deep=(N={DEEP_SAT_N},M={M_grid_deep},corr={DEEP_SAT_CORR}) "
          f"TR={TR} expected_n={expected_n}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    salt = 0
    t0 = time.perf_counter()

    # 1) CLIFF arm: M x corr grid
    for M in M_GRID_CLIFF:
        for corr in CORR_GRID_CLIFF:
            salt += 1
            pt = eval_phase_point(MECH, M, CLIFF_N, FIXED_F, FIXED_L,
                                  corr, "SHARDED", TR, seed, salt,
                                  arm_tag="CLIFF")
            phase_map.append(pt)
            print(f"  [{len(phase_map):3d}/{expected_n:3d}] CLIFF     "
                  f"M={M:5d} corr={corr:.2f} mech={MECH:22s} "
                  f"acc={pt['acc']:.4f} 2se={pt['noise_2se']:.4f} "
                  f"dt={pt['elapsed_s']:.2f}s", flush=True)

    # 2) CLIFF_EXT arm (FULL only): fine cliff-transition slice at corr=0.87
    if run_cliff_ext:
        for M in M_EXTENDED_FULL_ONLY_GRID:
            salt += 1
            pt = eval_phase_point(MECH, M, CLIFF_N, FIXED_F, FIXED_L,
                                  CORR_EXTENDED_FULL_ONLY, "SHARDED",
                                  TR, seed, salt, arm_tag="CLIFF_EXT")
            phase_map.append(pt)
            print(f"  [{len(phase_map):3d}/{expected_n:3d}] CLIFF_EXT "
                  f"M={M:5d} corr={CORR_EXTENDED_FULL_ONLY:.2f} "
                  f"mech={MECH:22s} acc={pt['acc']:.4f} "
                  f"dt={pt['elapsed_s']:.2f}s", flush=True)

    # 3) DEEP_SAT arm (H3-NULL)
    for M in M_grid_deep:
        salt += 1
        pt = eval_phase_point(MECH, M, DEEP_SAT_N, DEEP_SAT_F, DEEP_SAT_L,
                              DEEP_SAT_CORR, "SHARDED", TR, seed, salt,
                              arm_tag="DEEP_SAT")
        phase_map.append(pt)
        print(f"  [{len(phase_map):3d}/{expected_n:3d}] DEEP_SAT  "
              f"M={M:5d} corr={DEEP_SAT_CORR:.2f} mech={MECH:22s} "
              f"N={DEEP_SAT_N} acc={pt['acc']:.4f} "
              f"dt={pt['elapsed_s']:.2f}s", flush=True)

    # 4) SATURATION_PC arm
    salt += 1
    pc = SATURATION_PC_REGIME
    pc_pt = eval_phase_point(pc["cleanup_mechanism"], pc["M"], pc["N"],
                             pc["F"], pc["L"], pc["corruption"],
                             pc["storage"], TR, seed, salt,
                             arm_tag="SATURATION_PC")
    phase_map.append(pc_pt)
    print(f"  [{len(phase_map):3d}/{expected_n:3d}] PC        "
          f"M={pc['M']:5d} corr={pc['corruption']:.2f} "
          f"mech={pc['cleanup_mechanism']:22s} "
          f"acc={pc_pt['acc']:.4f} dt={pc_pt['elapsed_s']:.2f}s", flush=True)

    elapsed = time.perf_counter() - t0
    observed_n = len(phase_map)
    cardinality_ok = (observed_n == expected_n)

    # ARMS-MUST-DIFFER analog: verify (M=min, corr=min) vs (M=max, corr=max) at CLIFF
    cliff_pts = [p for p in phase_map if p["arm_tag"] == "CLIFF"]
    cliff_ext_pts = [p for p in phase_map if p["arm_tag"] == "CLIFF_EXT"]
    deep_pts = [p for p in phase_map if p["arm_tag"] == "DEEP_SAT"]

    hash_corners: Dict[str, str] = {}
    M_min, M_max = min(M_GRID_CLIFF), max(M_GRID_CLIFF)
    c_min, c_max = min(CORR_GRID_CLIFF), max(CORR_GRID_CLIFF)
    for pt in cliff_pts:
        if pt["M"] == M_min and abs(pt["corruption"] - c_min) < 1e-6:
            hash_corners[f"M{M_min}_c{c_min:.2f}"] = pt["output_hash"]
        if pt["M"] == M_max and abs(pt["corruption"] - c_max) < 1e-6:
            hash_corners[f"M{M_max}_c{c_max:.2f}"] = pt["output_hash"]
    corner_hashes_distinct = (len(set(hash_corners.values())) >= 2
                              if len(hash_corners) == 2 else False)

    # SATURATION_PC pass check
    pc_acc = float(pc_pt["acc"])
    pc_pass = (pc_acc >= SATURATION_PC_THRESHOLD)

    # CLIFF arm cliff-shape analysis
    cliff_grid = compute_cliff_grid(cliff_pts, M_GRID_CLIFF, CORR_GRID_CLIFF)
    cliff_accs = [p["acc"] for p in cliff_pts]
    cliff_mean = float(np.mean(cliff_accs)) if cliff_accs else 0.0
    cliff_min = float(np.min(cliff_accs)) if cliff_accs else 0.0
    cliff_max = float(np.max(cliff_accs)) if cliff_accs else 0.0
    cliff_in_band = sum(1 for a in cliff_accs
                        if NON_SAT_BAND_LO <= a <= NON_SAT_BAND_HI)
    cliff_straddles = (any(a >= 0.90 for a in cliff_accs)
                       and any(a <= 0.30 for a in cliff_accs))

    # DEEP_SAT arm analysis (H3-NULL)
    deep_analysis = compute_deep_sat_analysis(deep_pts)
    deep_saturated = deep_analysis.get("saturated", False)
    h3_null_fires = (deep_analysis.get("interaction_metric", 0.0)
                     < DEEP_SAT_INTERACTION_THRESHOLD)

    # CLIFF_EXT arm (FULL only): 1-D M row at corr=0.87
    cliff_ext_info = {}
    if cliff_ext_pts:
        ext_accs = [p["acc"] for p in cliff_ext_pts]
        cliff_ext_info = {
            "corr": CORR_EXTENDED_FULL_ONLY,
            "M_grid": M_EXTENDED_FULL_ONLY_GRID,
            "accs_by_M": {str(p["M"]): p["acc"] for p in cliff_ext_pts},
            "mean_acc": round(float(np.mean(ext_accs)), 4),
            "min_acc": round(float(np.min(ext_accs)), 4),
            "max_acc": round(float(np.max(ext_accs)), 4),
            "M_range": round(float(np.max(ext_accs) - np.min(ext_accs)), 4),
        }

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
        "arms_differ_verified": corner_hashes_distinct,
        "saturation_pc_result": {
            "regime": SATURATION_PC_REGIME,
            "acc": pc_acc,
            "threshold": SATURATION_PC_THRESHOLD,
            "pass": pc_pass,
        },
        "cliff_arm": {
            "regime": {"N": CLIFF_N, "F": FIXED_F, "L": FIXED_L,
                        "mech": MECH, "storage": "SHARDED"},
            "M_grid": M_GRID_CLIFF,
            "corr_grid": CORR_GRID_CLIFF,
            "mean_acc": round(cliff_mean, 4),
            "min_acc": round(cliff_min, 4),
            "max_acc": round(cliff_max, 4),
            "n_in_non_saturated_band": cliff_in_band,
            "n_total": len(cliff_accs),
            "straddles_cliff": cliff_straddles,
            **cliff_grid,
        },
        "cliff_ext_arm": cliff_ext_info,
        "deep_sat_arm": {
            "regime": {"N": DEEP_SAT_N, "F": DEEP_SAT_F,
                        "L": DEEP_SAT_L, "corr": DEEP_SAT_CORR,
                        "mech": MECH, "storage": "SHARDED"},
            "M_grid": M_grid_deep,
            **deep_analysis,
            "h3_null_fires": h3_null_fires,
            "h3_null_threshold": DEEP_SAT_INTERACTION_THRESHOLD,
        },
        "non_saturated_band": [NON_SAT_BAND_LO, NON_SAT_BAND_HI],
        "avg_peak_mem_mb": round(avg_peak, 1),
        "elapsed_seed_s": round(elapsed, 2),
        "beta": BETA,
        "alpha_soft": ALPHA_SOFT,
    }


# ---------------------------------------------------------------------------
# Smoke-gate predicate (null-hypothesis-safe; gate on infra + PC + straddle only)
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
    if not cliff.get("straddles_cliff"):
        return False, (f"cliff_did_not_straddle: no (M,corr) point straddled "
                       f"the cliff (need at least one >=0.90 AND one <=0.30); "
                       f"CLIFF grid did not include the transition; regime "
                       f"bracket wrong for cliff-mapping intent")
    deep = body.get("deep_sat_arm", {})
    if not deep.get("saturated"):
        return False, (f"deep_sat_regime_drift: mean_acc={deep.get('mean_acc')} "
                       f"< 0.95; H3-NULL control arm did not saturate at "
                       f"(N={DEEP_SAT_N}, F={DEEP_SAT_F}, corr={DEEP_SAT_CORR})")
    if not cliff.get("complete"):
        return False, f"cliff_grid_not_complete: acc_grid missing points"
    for pt in phase_map:
        if pt.get("acc") != pt.get("acc"):
            return False, f"NAN_in_phase_map at {pt}"

    # Discriminator informational (null-hypothesis discipline):
    cliff_amp = cliff.get("cliff_amplitude", 0.0)
    M_var = cliff.get("M_variance_within_corr", 0.0)
    corr_var = cliff.get("corr_variance_within_M", 0.0)
    interaction = cliff.get("interaction_metric", 0.0)
    deep_interaction = deep.get("interaction_metric", 0.0)
    return True, (f"smoke_gate_pass: cardinality_ok + axes-fire + "
                  f"pc_acc={pc.get('acc')} + cliff_straddles + "
                  f"deep_sat_saturated(mean={deep.get('mean_acc')}); "
                  f"informational: cliff_amplitude={cliff_amp} "
                  f"M_var_within_corr={M_var} corr_var_within_M={corr_var} "
                  f"interaction_metric={interaction} "
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
        "cliff_ext_arm": body.get("cliff_ext_arm"),
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
                f"corner_hashes={body.get('hash_corners')} not distinct")
    elif not pc.get("pass"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_SATURATION_PC_MISMATCH: acc={pc.get('acc')} < "
                f"{pc.get('threshold')} (Gate D violation)")
    elif not deep.get("saturated"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_DEEP_SAT_ARM_DRIFT: mean_acc={deep.get('mean_acc')} "
                f"< 0.95; H3-NULL control regime failed to saturate")
    elif not cliff.get("complete"):
        verdict = "HARD_FAIL"
        vmsg = f"HARD_FAIL_CLIFF_GRID_INCOMPLETE"
    else:
        cliff_amp = cliff.get("cliff_amplitude", 0.0)
        M_var = cliff.get("M_variance_within_corr", 0.0)
        corr_var = cliff.get("corr_variance_within_M", 0.0)
        interaction = cliff.get("interaction_metric", 0.0)
        deep_interaction = deep.get("interaction_metric", 0.0)
        h3_null_fires = deep.get("h3_null_fires", False)

        h3_note = (f" ; H3-NULL fires(deep_interaction={deep_interaction} < "
                   f"{DEEP_SAT_INTERACTION_THRESHOLD})"
                   if h3_null_fires else
                   f" ; H3-NULL DID NOT FIRE(deep_interaction="
                   f"{deep_interaction} >= "
                   f"{DEEP_SAT_INTERACTION_THRESHOLD}) -- degeneracy failed")
        shape_note = (f" ; cliff_amplitude={cliff_amp} "
                      f"M_variance_within_corr={M_var} "
                      f"corr_variance_within_M={corr_var} "
                      f"interaction_metric={interaction}")

        if cliff_amp < CLIFF_AMPLITUDE_H4_THRESHOLD:
            verdict = "HARD_FAIL"
            vmsg = (f"HARD_FAIL_H4_NULL_NOCLIFF: cliff_amplitude={cliff_amp} "
                    f"< {CLIFF_AMPLITUDE_H4_THRESHOLD}; SHARDED cliff not "
                    f"in tested regime; regime bracket wrong; needs re-authoring"
                    f"{shape_note}{h3_note}")
        elif cliff_amp >= CLIFF_AMPLITUDE_H1_THRESHOLD and M_var <= M_VARIANCE_H1_THRESHOLD:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H1_SHARDED_CLIFF_MAPPED_CORR_DOMINATED: "
                    f"cliff_amplitude={cliff_amp} >= "
                    f"{CLIFF_AMPLITUDE_H1_THRESHOLD} AND "
                    f"M_variance_within_corr={M_var} <= "
                    f"{M_VARIANCE_H1_THRESHOLD}; SHARDED cliff decisively "
                    f"mapped as corr-driven (not M-driven) at cliff-adjacent "
                    f"regime; fills lit-gap. Atom candidate: "
                    f"EMPIRICAL_SHARDED_CLIFF_MN_INTERPOLATION_v1_MAPS_"
                    f"CLIFF_SHAPE_AT_N512_F1_MODERN_HOPFIELD "
                    f"MM_TENTATIVE (requires 3-seed FULL cv<0.15 for "
                    f"MM_STANDARD)"
                    f"{shape_note}{h3_note}")
        elif cliff_amp >= CLIFF_AMPLITUDE_H1_THRESHOLD and M_var > M_VARIANCE_H1_THRESHOLD:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H2_M_x_CORR_CROSS_TERM_FIRES: "
                    f"cliff_amplitude={cliff_amp} >= "
                    f"{CLIFF_AMPLITUDE_H1_THRESHOLD} AND "
                    f"M_variance_within_corr={M_var} > "
                    f"{M_VARIANCE_H1_THRESHOLD}; M and corr BOTH shift "
                    f"cliff position; cliff-ratio hypothesis (per Kanerva SDM "
                    f"+ Cuckoo hashing) supported. Atom candidate: "
                    f"EMPIRICAL_M_x_CORR_CROSS_TERM_SHARDED_CLIFF_v1 "
                    f"MM_TENTATIVE"
                    f"{shape_note}{h3_note}")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_WEAK_CLIFF: cliff_amplitude={cliff_amp} "
                    f"MIDDLE_BAND between H4 and H1; weak cliff signal"
                    f"{shape_note}{h3_note}")

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
    })
    return out


__all__ = [
    "ANCHOR_NAME", "DEVICE", "GPU_NAME", "MECH",
    "FIXED_L", "FIXED_F",
    "CLEANUP_MECHANISMS", "CLEANUP_REGISTRY",
    "M_GRID_CLIFF", "CORR_GRID_CLIFF",
    "M_EXTENDED_FULL_ONLY_GRID", "CORR_EXTENDED_FULL_ONLY",
    "M_GRID_DEEP_SAT_SMOKE", "M_GRID_DEEP_SAT_FULL",
    "CLIFF_N", "DEEP_SAT_N", "DEEP_SAT_F", "DEEP_SAT_L", "DEEP_SAT_CORR",
    "TR_FULL", "TR_SMOKE",
    "SATURATION_PC_REGIME", "SATURATION_PC_THRESHOLD",
    "NON_SAT_BAND_LO", "NON_SAT_BAND_HI",
    "EXPECTED_N_UNITS_SMOKE", "EXPECTED_N_UNITS_FULL",
    "CLIFF_AMPLITUDE_H1_THRESHOLD", "M_VARIANCE_H1_THRESHOLD",
    "CLIFF_AMPLITUDE_H4_THRESHOLD", "DEEP_SAT_INTERACTION_THRESHOLD",
    "REQUIRED_FIELDS",
    "eval_phase_point", "compute_cliff_grid", "compute_deep_sat_analysis",
    "selftest", "run_one_seed", "smoke_gate_predicate", "aggregate_and_verdict",
]
