"""Stage 1 Regime Probe 12: L (chain-depth in run_chain) MARGINAL-EFFECT sweep.

Cell anchor: `stage1_regime_probe_12_L_marginal_effect_sweep_v1`
Pre-reg:     preregs/2026-07-03_stage1_regime_probe_12_L_marginal_effect_sweep_v1.md

Purpose:
    Skunkworks structural VET (task afadd5dbd43055cf1, 2026-07-03 21:35Z, atom #48)
    surfaced that L (chain length in `run_chain`) is a GENUINELY DISTINCT 5th
    potential algebra-depth axis but is FIXED at L=2 across all recent probes
    (Probes 1/2/4/5/6v2/7v2/8/9v2/10/11). Structural VET showed TOPOLOGY and
    ALGEBRA in Probes 8/10 both alias to F (sharded-DAG fan-out) — the "algebra"
    label attached to F is not the same abstraction as
    SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS_CG_META_v1 (Stage 1 atom #3) which
    refers to M1.9/M1.10 roundtrip K=5 depth (chain depth). This probe tests
    whether L has a genuine marginal effect on retrieval capacity at
    cliff-adjacent regime, or whether the L=2 convention has been masking a
    real 5th sweep axis.

    5th sweep axis established (probes filed 2026-07-03):
      1. STORAGE (SHARDED vs BUNDLED)   -- Probe 1 CG_META
      2. TOPOLOGY (F fan-out)           -- Probe 6 v2 topology-free
      3. N (SCALE-FREE)                 -- Probe 7 v2 non-saturated
      4. F ALGEBRA                      -- Probe 8 filled today
      5. L CHAIN-DEPTH                  -- THIS PROBE (5th axis)

    L is a substrate primitive:
      - `run_chain(storage, mechanism, L, F, TR, ...)` in
        experiments/_stage1_physics_law_joint_composition_factorial_v1_core.py:249
      - L is directly settable (not derived from F). L = number of consecutive
        bind-shard-unbind-cleanup iterations. Each step: A_cur = props[ci];
        rule = sharded[ci, f_step]; cand = rule * conj(A_cur) * conj(POS[f]) *
        conj(IMPL); Q_clean = cleanup(cand_corr); ci = argmax(<Q_clean, props>).
        After L iterations, gold = perms[f_L-1](..perms[f_0](start)..).

    Empirical bracket at N=512 M=6400 corr=0.85 F=1 SHARDED (single-seed TR=40,
    seed=7, mechanism sweep across 3 cleanup mechs), MEASURED@scratchpad
    probe12_L_bracket 2026-07-03:
        L= 1 mean=0.825 spread=0.200 (mh=0.95 ic=0.75 sea=0.775)
        L= 2 mean=0.733 spread=0.075 (mh=0.725 ic=0.775 sea=0.70)
        L= 4 mean=0.442 spread=0.100 (mh=0.375 ic=0.475 sea=0.475)
        L= 8 mean=0.200 spread=0.175 (mh=0.175 ic=0.30  sea=0.125)
        L=16 mean=0.067 spread=0.125 (mh=0.125 ic=0.00  sea=0.075)
        in_band [0.30, 0.95]: L={1,2,4} True; L={8,16} False (below floor)
        per-mech L-spread (max-min across all L):
          modern_hopfield=0.825; iterative_cosine=0.775; soft_energy_attractor=0.700
    Bracket at N=8192 M=800 corr=0.60 F=1 SHARDED (DEEP_SAT H3-null control):
        L in {1,2,4,8,16}: all mean=1.000 spread=0.000 (fully saturated)
        Consistent with H3-null expectation (deep-saturation collapses L axis).

Cited source atoms (exact names per META_RULE_AC):
    T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1
    SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS_CG_META_v1 (Stage 1 atom #3)
    T3/EXP_stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1_3seed_FULL (Probe 8 F-axis)
    META_saturation_floor_masks_null_variance_probe3_lesson (T4 MM_STANDARD)
    META_axis_labels_map_to_substrate_primitives_not_theoretical_concepts (Skunkworks atom #44)
    META_cross_term_measurement_requires_both_arms_in_band (Skunkworks meta #43)
    feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-07-03
    feedback_plate_bound_too_pessimistic_for_sharded_fhrr_chain_composition_2026-07-03
    feedback_mechanism_abstraction_lossy_cite_source_signature_2026-07-03

Source signature (cited per feedback_mechanism_abstraction_lossy):
    SHARDED FHRR chain composition; N=512; M=6400; corr=0.85; F=1;
    MECH=modern_hopfield | iterative_cosine | soft_energy_attractor;
    BETA=8.0; ALPHA_SOFT=0.5; TR=100 (FULL) / 40 (SMOKE);
    storage_codebook=(M_props, F, N) complex64; unit-modulus phasors; L=1..16.
    L primitive: run_chain iterates L times; per step per trial random f_step in [0,F).

Reuse (Principle 11):
    Primitives imported from _stage1_physics_law_joint_composition_factorial_v1_core:
      CLEANUP_MECHANISMS, CLEANUP_REGISTRY, BETA, ALPHA_SOFT, DEVICE, GPU_NAME,
      build_rules, phase_corrupt, cleanup_argmax_idx, run_chain, cphasor_torch
    Verdict logic modeled on _stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1_core
    (band-restricted discriminator + per-arm HP_SCOPE + arm_tag routing +
    null-hypothesis-safe smoke gate).

Sweep grid FULL:
    CLIFF arm: L in {1,2,4,8,16} x 3 mech at (N=512, M=6400, corr=0.85, F=1, SHARDED) = 15 pts
    DEEP_SAT arm (H3 null): L in {1,4,16} x 3 mech at (N=8192, M=800, corr=0.60, F=1, SHARDED) = 9 pts
    SATURATION_PC arm: L=2 F=1 M=800 N=2048 corr=0.20 iterative_cosine (Gate D) = 1 pt
    TOTAL: 25 pts / seed
Sweep grid SMOKE:
    CLIFF arm: L in {1,4,16} (endpoints + mid) x 3 mech at CLIFF = 9 pts
    DEEP_SAT arm spot-check: L=2 x 3 mech at DEEP_SAT = 3 pts
    SATURATION_PC arm: 1 pt
    TOTAL: 13 pts

Hypotheses (falsifiable, per-mechanism L-spread on CLIFF arm; band-restricted
where possible; MM_TENTATIVE at SMOKE at most; MM_STANDARD at 3-seed FULL):
    H1 (L has genuine marginal effect on retrieval capacity):
        max_per_mech_L_spread >= 0.10 on CLIFF arm
      -> L IS a real 5th sweep axis; today's "regime matrix complete at 6 pairs"
         needs revision to include L cross-terms; CG_META axis set expands to
         include L. Atom: EMPIRICAL_L_MARGINAL_EFFECT_SHARDED_CLIFF_ADJACENT_v1
         MM_TENTATIVE at SMOKE, MM_STANDARD at 3-seed FULL.
    H2 (L is INERT at cliff-adjacent SHARDED):
        max_per_mech_L_spread < 0.05 on CLIFF arm
      -> L does NOT moderate retrieval at this regime; L=2 convention was not
         masking a real axis at this signature; L can be atomized as inert
         negative finding. Atom: L_INERT_AT_SHARDED_CLIFF_ADJACENT_NEGATIVE_v1
         MM_TENTATIVE.
    H3 (mechanism ranking crossover across L, MM_TENTATIVE informational):
        mech ranking changes across L within CLIFF band.
    H3-NULL (DEEP_SAT null fires; sanity check the substrate saturation regime):
        DEEP_SAT arm max_per_mech_L_spread < 0.05 at N=8192 M=800 corr=0.60
      -> confirms L-axis degeneracy at deep-saturation; strengthens the
         saturation-masks-variance thesis (META_saturation_floor).

Compute architecture: batched-GPU when CUDA available; falls back to CPU
    (empirical: CPU wall on smoke = seconds; full = tens of seconds; no batching
    speedup needed at these primitive sizes since M/F/N are modest). Local CPU
    dispatch is USER-LOCKED as SMOKE-only (per feedback_smoke_only_local_cpu 2026-07-01);
    FULL routes to remote via Orchestrator when Tailscale restored.

Sibling wrappers: exp_stage1_regime_probe_12_L_marginal_effect_sweep_v1_s{7,13,19}.py

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-07-03 (agent-spawn, Opus 4.7).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared (categorical accuracy; discriminator is per-mech L-spread)
# - baseline_in_band verified empirically (CLIFF arm L={1,2,4} mean 0.44-0.83 in
#   [0.30, 0.95] band; L={8,16} below floor by construction to span cliff; DEEP_SAT
#   arm saturated by design as H3 null control)
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
# - HP_SCOPE per-arm declaration (CLIFF vs DEEP_SAT vs SATURATION_PC)
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

ANCHOR_NAME = "stage1_regime_probe_12_L_marginal_effect_sweep_v1"

# ---------------------------------------------------------------------------
# Sweep constants (LOCKED at module init; MEASURED@empirical-bracket 2026-07-03)
# ---------------------------------------------------------------------------
# Primary axis: L chain depth (5th potential CG_META axis per Skunkworks structural
# VET atom #48). L is directly settable in run_chain; genuinely distinct from
# F fan-out (F sets choices per step; L sets number of steps).
L_GRID_CLIFF_FULL = [1, 2, 4, 8, 16]
L_GRID_CLIFF_SMOKE = [1, 4, 16]  # endpoints + mid; captures cliff transition

# CLIFF-adjacent operating point (empirically LOCKED at TR=40 seed=7):
#   at N=512 M=6400 corr=0.85 F=1: mean_acc across L in {1,2,4} = 0.44-0.83
#   (in [0.30, 0.95] band); L in {8,16} = 0.07-0.20 (below floor by design to
#   span the L-cliff transition and prove the marginal-effect signal is not
#   band-limited artifact). MEASURED@scratchpad probe12_L_bracket 2026-07-03.
CLIFF_N = 512
CLIFF_M = 6400
CLIFF_CORR = 0.85
CLIFF_F = 1

# DEEP_SAT arm (H3-NULL: L-axis DEGENERACY when saturated):
#   at N=8192 M=800 corr=0.60 F=1: mean_acc = 1.0 across L in {1,2,4,8,16},
#   spread = 0. HYPOTHESIZED at FULL TR=100 (3-seed): max_L_spread < 0.05.
#   MEASURED@bracket 2026-07-03 single-seed TR=40 = 0.00 exact.
L_GRID_DEEP_SAT_FULL = [1, 4, 16]  # 3 levels sufficient for null-control assessment
L_GRID_DEEP_SAT_SMOKE = [2]        # single spot-check
DEEP_SAT_N = 8192
DEEP_SAT_M = 800
DEEP_SAT_CORR = 0.60
DEEP_SAT_F = 1

# SATURATION_PC arm (Gate D reproducer, cited from Probes 6/7/8 baseline)
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

# CLIFF main: 5 L x 3 mech = 15; DEEP_SAT: 3 L x 3 mech = 9; PC = 1. TOTAL 25.
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

# H1/H2 thresholds (mirror Probe 6/7/8 v2 discipline; per-mech L-spread primary)
MECH_L_SPREAD_H1_THRESHOLD = 0.10   # H1: L IS a marginal-effect axis
MECH_L_SPREAD_H2_THRESHOLD = 0.05   # H2: L is inert (degenerate)
# H3-NULL threshold (DEEP_SAT arm)
DEEP_SAT_MAX_SPREAD_THRESHOLD = 0.05

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
# Selftest (formula check at reduced grid; wall < 60s target on CPU)
# ---------------------------------------------------------------------------
def selftest() -> Tuple[bool, str]:
    msgs = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 25:
        return False, (f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 25 "
                       f"(15 cliff + 9 deep_sat + 1 PC)")
    if EXPECTED_N_UNITS_SMOKE != 13:
        return False, (f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 13 "
                       f"(9 cliff + 3 deep_sat + 1 PC)")
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} "
                f"SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. Sanity: 3 cleanup mechanisms produce distinct outputs at L=2 F=1 CLIFF regime
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

    # 3. L-axis fires: L=1 chain output MUST differ from L=4 chain output
    #    (chain depth affects gold trajectory; same seed same start yields
    #    different final indices at different depths -- SHAPE-MATCH check for
    #    L axis being a REAL primitive, not aliased).
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
        return False, (f"L=1 vs L=4 chain outputs identical (L axis has no "
                       f"structural effect; primitive is aliased); hash={h_L1}")
    msgs.append(f"L-axis fires: L1={h_L1} L4={h_L4}")

    # 4. SATURATION_PC easy gate reproducer (Gate D at reduced TR)
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
                       f"iterative_cosine) expected >= 0.85 at TR=40; "
                       f"got {acc_easy:.3f}")
    msgs.append(f"SATURATION_PC selftest (TR=40): acc={acc_easy:.3f}")

    # 5. Cliff-adjacent regime sanity: L=2 F=1 CLIFF should land in loose band
    #    MEASURED@bracket 2026-07-03: iterative_cosine mean=0.775 at TR=40 seed=7.
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
                       f"acc={acc_cliff:.3f} outside [0.20, 0.98]; regime "
                       f"drifted from empirical bracket")
    msgs.append(f"CLIFF regime sanity L=2 (TR=20): acc={acc_cliff:.3f}")

    # 6. DEEP_SAT regime sanity (saturated expected across L)
    gen.manual_seed(4141)
    props5, perms5, IMPL5, POS5, sh5, bd5 = build_rules(
        DEEP_SAT_M, DEEP_SAT_F, gen, DEVICE, DEEP_SAT_N)
    acc_deep, _ = run_chain("SHARDED", "iterative_cosine",
                            4, DEEP_SAT_F, 20,
                            props5, perms5, IMPL5, POS5, sh5, bd5,
                            DEEP_SAT_CORR, gen, DEVICE)
    if acc_deep < 0.95:
        return False, (f"DEEP_SAT regime sanity (L=4 F=1 M={DEEP_SAT_M} "
                       f"N={DEEP_SAT_N} corr={DEEP_SAT_CORR} iterative_cosine "
                       f"TR=20): acc={acc_deep:.3f} < 0.95; DEEP_SAT arm did "
                       f"not saturate as expected; regime drifted from empirical")
    msgs.append(f"DEEP_SAT regime sanity L=4 (TR=20): acc={acc_deep:.3f}")

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

    # 2) DEEP_SAT arm (H3-NULL): L sweep x mech at (DEEP_SAT_N, DEEP_SAT_M, DEEP_SAT_CORR)
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

    # Per-L mech spread (max-min across 3 mechs at each L) on CLIFF arm --
    # this measures MECHANISM variance at fixed L (Probe 8 pattern).
    per_L_cliff_mech_variance: Dict[str, Dict[str, Any]] = {}
    per_L_cliff_mech_variance_in_band: Dict[str, Dict[str, Any]] = {}
    for L in L_grid_cliff:
        triple = {}
        for mech in mech_grid:
            matches = [p["acc"] for p in cliff_pts
                       if p["L"] == L and p["cleanup_mechanism"] == mech]
            if matches:
                triple[mech] = matches[0]
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
            if NON_SAT_BAND_LO <= cell_mean <= NON_SAT_BAND_HI:
                per_L_cliff_mech_variance_in_band[str(L)] = per_L_cliff_mech_variance[str(L)]

    # PER-MECH L-spread (max-min across L within each mech) -- this is the PRIMARY
    # H1 discriminator: does L moderate accuracy for any given mechanism?
    per_mech_L_spread_cliff: Dict[str, Dict[str, Any]] = {}
    per_mech_L_spread_cliff_band_only: Dict[str, Dict[str, Any]] = {}
    band_L_set = set(int(k) for k in per_L_cliff_mech_variance_in_band.keys())
    for mech in mech_grid:
        per_L_accs = {}
        for L in L_grid_cliff:
            matches = [p["acc"] for p in cliff_pts
                       if p["L"] == L and p["cleanup_mechanism"] == mech]
            if matches:
                per_L_accs[L] = matches[0]
        if per_L_accs:
            vals = list(per_L_accs.values())
            spread = round(max(vals) - min(vals), 4)
            per_mech_L_spread_cliff[mech] = {
                "accs_by_L": {str(L): round(v, 4) for L, v in per_L_accs.items()},
                "mean_acc": round(float(np.mean(vals)), 4),
                "spread": spread,
                "L_at_max_acc": max(per_L_accs, key=per_L_accs.get),
                "L_at_min_acc": min(per_L_accs, key=per_L_accs.get),
            }
            # Band-only version (restricted to L values whose mech-mean is in band)
            band_only_accs = {L: v for L, v in per_L_accs.items() if L in band_L_set}
            if len(band_only_accs) >= 2:
                b_vals = list(band_only_accs.values())
                per_mech_L_spread_cliff_band_only[mech] = {
                    "accs_by_L": {str(L): round(v, 4) for L, v in band_only_accs.items()},
                    "spread": round(max(b_vals) - min(b_vals), 4),
                }

    max_per_mech_L_spread = max(
        (v["spread"] for v in per_mech_L_spread_cliff.values()), default=0.0)
    max_per_mech_L_spread_band_only = max(
        (v["spread"] for v in per_mech_L_spread_cliff_band_only.values()),
        default=0.0)

    # Aggregate accuracy_var(L) semantic: variance of per-L mean-accuracy across L
    per_L_mean_acc = {str(L): round(v["mean_acc"], 4)
                       for str_L, L in [(str(L), L) for L in L_grid_cliff]
                       for k, v in per_L_cliff_mech_variance.items()
                       if k == str(L)}
    per_L_mean_acc = {str(L): per_L_cliff_mech_variance[str(L)]["mean_acc"]
                       for L in L_grid_cliff
                       if str(L) in per_L_cliff_mech_variance}
    if per_L_mean_acc:
        means_across_L = list(per_L_mean_acc.values())
        L_mean_range = round(max(means_across_L) - min(means_across_L), 4)
        L_mean_variance = round(float(np.var(means_across_L)), 4)
    else:
        L_mean_range = 0.0
        L_mean_variance = 0.0

    # DEEP_SAT arm summary (H3-NULL)
    deep_accs = [p["acc"] for p in deep_pts]
    deep_mean = float(np.mean(deep_accs)) if deep_accs else 0.0
    deep_min = float(np.min(deep_accs)) if deep_accs else 0.0
    deep_max = float(np.max(deep_accs)) if deep_accs else 0.0
    per_L_deep_variance: Dict[str, Dict[str, Any]] = {}
    per_mech_L_spread_deep: Dict[str, Dict[str, Any]] = {}
    for L in L_grid_deep:
        triple = {}
        for mech in mech_grid:
            matches = [p["acc"] for p in deep_pts
                       if p["L"] == L and p["cleanup_mechanism"] == mech]
            if matches:
                triple[mech] = matches[0]
        if len(triple) == len(mech_grid):
            vals = list(triple.values())
            spread = round(max(vals) - min(vals), 4)
            per_L_deep_variance[str(L)] = {
                "accs_by_mech": {m: round(v, 4) for m, v in triple.items()},
                "mean_acc": round(float(np.mean(vals)), 4),
                "spread": spread,
            }
    for mech in mech_grid:
        per_L_accs = {L: p["acc"] for L in L_grid_deep
                       for p in deep_pts
                       if p["L"] == L and p["cleanup_mechanism"] == mech}
        if per_L_accs and len(per_L_accs) >= 2:
            vals = list(per_L_accs.values())
            per_mech_L_spread_deep[mech] = {
                "accs_by_L": {str(L): round(v, 4) for L, v in per_L_accs.items()},
                "spread": round(max(vals) - min(vals), 4),
            }
    max_deep_per_mech_L_spread = max(
        (v["spread"] for v in per_mech_L_spread_deep.values()), default=0.0)
    max_deep_mech_spread_at_fixed_L = max(
        (v["spread"] for v in per_L_deep_variance.values()), default=0.0)

    # H3-NULL fires when DEEP_SAT max_per_mech_L_spread < 0.05
    # (L-axis degenerates at deep-saturation).
    h3_null_fires = (max_deep_per_mech_L_spread < DEEP_SAT_MAX_SPREAD_THRESHOLD)
    deep_saturated = (deep_mean >= 0.95)

    # H3 crossover on CLIFF arm within band (informational)
    cliff_ranking_by_L_in_band: Dict[str, Dict[str, Any]] = {}
    for L_str, block in per_L_cliff_mech_variance_in_band.items():
        ranking = tuple(sorted(block["accs_by_mech"],
                                key=lambda m: -block["accs_by_mech"][m]))
        cliff_ranking_by_L_in_band[L_str] = {
            "ranking": ranking,
            "means": block["accs_by_mech"],
        }
    rankings = [v["ranking"] for v in cliff_ranking_by_L_in_band.values()]
    mech_ranking_crossover = len(set(rankings)) > 1 if rankings else False

    # Escapes-saturation for CLIFF arm SMOKE gate (per-L semantics)
    per_L_cliff_mean_acc_full = {L_str: round(v["mean_acc"], 4)
                                  for L_str, v in per_L_cliff_mech_variance.items()}
    escapes_saturation_cliff = any(v < NON_SAT_BAND_HI
                                    for v in per_L_cliff_mean_acc_full.values())

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
            "mean_acc": round(cliff_mean, 4),
            "min_acc": round(cliff_min, 4),
            "max_acc": round(cliff_max, 4),
            "n_in_non_saturated_band": cliff_in_band,
            "n_total": len(cliff_accs),
            "fraction_in_band": round(cliff_in_band_frac, 4),
            "per_L_mech_variance": per_L_cliff_mech_variance,
            "per_L_mech_variance_in_band": per_L_cliff_mech_variance_in_band,
            "per_L_mean_acc": per_L_cliff_mean_acc_full,
            "per_mech_L_spread": per_mech_L_spread_cliff,
            "per_mech_L_spread_band_only": per_mech_L_spread_cliff_band_only,
            "max_per_mech_L_spread": round(max_per_mech_L_spread, 4),
            "max_per_mech_L_spread_band_only": round(
                max_per_mech_L_spread_band_only, 4),
            "L_mean_range": L_mean_range,
            "L_mean_variance": L_mean_variance,
            "escapes_saturation_ceiling": escapes_saturation_cliff,
            "mech_ranking_by_L_in_band": cliff_ranking_by_L_in_band,
            "mech_ranking_crossover": mech_ranking_crossover,
        },
        "deep_sat_arm": {
            "regime": {"N": DEEP_SAT_N, "M": DEEP_SAT_M, "corr": DEEP_SAT_CORR,
                        "F": DEEP_SAT_F, "storage": "SHARDED"},
            "L_grid": L_grid_deep,
            "mean_acc": round(deep_mean, 4),
            "min_acc": round(deep_min, 4),
            "max_acc": round(deep_max, 4),
            "per_L_mech_variance": per_L_deep_variance,
            "per_mech_L_spread": per_mech_L_spread_deep,
            "max_per_mech_L_spread": round(max_deep_per_mech_L_spread, 4),
            "max_mech_spread_at_fixed_L": round(max_deep_mech_spread_at_fixed_L, 4),
            "saturated": deep_saturated,
            "h3_null_fires": h3_null_fires,
            "h3_null_threshold": DEEP_SAT_MAX_SPREAD_THRESHOLD,
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
                       f"{cliff.get('per_L_mean_acc')}; CLIFF regime fully "
                       f"saturated; design goal not achieved")
    deep = body.get("deep_sat_arm", {})
    # DEEP_SAT arm should saturate at smoke; if not, the H3 null control regime drifted
    if not deep.get("saturated"):
        return False, (f"deep_sat_regime_drift: mean_acc={deep.get('mean_acc')} "
                       f"< 0.95; H3-NULL control arm did not saturate at "
                       f"(N={DEEP_SAT_N}, M={DEEP_SAT_M}, corr={DEEP_SAT_CORR}); "
                       f"deep-sat regime drifted from empirical bracket")
    # NaN sanity
    for pt in phase_map:
        if pt.get("acc") != pt.get("acc"):
            return False, f"NAN_in_phase_map at {pt}"

    # Discriminator variance is INFORMATIONAL, not gating (null-hypothesis
    # discipline; feedback_smoke_gates_null_hypothesis_should_not_gate_on_
    # discriminator_firing_2026-07-03).
    max_L_spread = cliff.get("max_per_mech_L_spread", 0.0)
    max_L_spread_band = cliff.get("max_per_mech_L_spread_band_only", 0.0)
    L_mean_range = cliff.get("L_mean_range", 0.0)
    deep_L_spread = deep.get("max_per_mech_L_spread", 0.0)
    return True, (f"smoke_gate_pass: cardinality_ok + 3-mech-hash-distinct + "
                  f"pc_acc={pc.get('acc')} (>={pc.get('threshold')}) + "
                  f"cliff_mean={cliff.get('mean_acc')} escapes_saturation + "
                  f"deep_sat_saturated(mean={deep.get('mean_acc')}); "
                  f"informational: cliff_max_per_mech_L_spread={max_L_spread} "
                  f"(band_only={max_L_spread_band}) L_mean_range={L_mean_range} "
                  f"deep_L_spread={deep_L_spread} h3_null_fires="
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
                f"{deep.get('mean_acc')} < 0.95; H3-NULL control regime failed "
                f"to saturate; regime construction broken")
    else:
        # Primary discriminator: max per-mech L-spread on CLIFF arm.
        # H1 fires: L is a real 5th axis (marginal effect).
        # H2 fires: L is inert (below noise floor).
        cliff_max_L_spread = cliff.get("max_per_mech_L_spread", 0.0)
        cliff_max_L_spread_band = cliff.get("max_per_mech_L_spread_band_only", 0.0)
        deep_max_L_spread = deep.get("max_per_mech_L_spread", 0.0)
        h3_null_fires = deep.get("h3_null_fires", False)
        crossover = cliff.get("mech_ranking_crossover", False)
        L_mean_range = cliff.get("L_mean_range", 0.0)
        cross_note = (" ; mech_ranking_crossover=True (H3 MM_TENTATIVE)"
                      if crossover else "")
        h3_null_note = (f" ; H3-NULL fires(deep_max_L_spread={deep_max_L_spread} "
                        f"< {DEEP_SAT_MAX_SPREAD_THRESHOLD})"
                        if h3_null_fires else
                        f" ; H3-NULL DID NOT FIRE(deep_max_L_spread="
                        f"{deep_max_L_spread} >= "
                        f"{DEEP_SAT_MAX_SPREAD_THRESHOLD}) -- L axis "
                        f"surprisingly non-degenerate at deep-saturation")
        L_mean_note = f" ; L_mean_range(across-L per-L-mean acc)={L_mean_range}"

        if cliff_max_L_spread >= MECH_L_SPREAD_H1_THRESHOLD:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H1_L_MARGINAL_EFFECT_AT_CLIFF_ADJACENT_SHARDED: "
                    f"cliff max_per_mech_L_spread={cliff_max_L_spread} "
                    f">= {MECH_L_SPREAD_H1_THRESHOLD}; L IS a genuinely "
                    f"distinct 5th CG_META axis at cliff-adjacent SHARDED "
                    f"regime; today's regime matrix (6 pairs) needs revision "
                    f"to include L cross-terms; L=2 convention has been "
                    f"masking a real axis. Atom candidate: "
                    f"EMPIRICAL_L_MARGINAL_EFFECT_SHARDED_CLIFF_ADJACENT_v1 "
                    f"MM_STANDARD at 3-seed FULL"
                    f"{L_mean_note}{cross_note}{h3_null_note}")
        elif cliff_max_L_spread < MECH_L_SPREAD_H2_THRESHOLD:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H2_L_INERT_AT_CLIFF_ADJACENT_SHARDED: "
                    f"cliff max_per_mech_L_spread={cliff_max_L_spread} "
                    f"< {MECH_L_SPREAD_H2_THRESHOLD}; L does NOT have "
                    f"marginal effect at cliff-adjacent SHARDED regime; "
                    f"L=2 convention was NOT masking a real axis at this "
                    f"signature. Atom candidate: "
                    f"L_INERT_AT_SHARDED_CLIFF_ADJACENT_NEGATIVE_v1 "
                    f"MM_TENTATIVE"
                    f"{L_mean_note}{cross_note}{h3_null_note}")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_WEAK_L_MARGINAL_EFFECT: cliff "
                    f"max_per_mech_L_spread={cliff_max_L_spread} in "
                    f"[{MECH_L_SPREAD_H2_THRESHOLD}, "
                    f"{MECH_L_SPREAD_H1_THRESHOLD}); weak L-moderation "
                    f"(MM_TENTATIVE); consider refined sweep or higher TR"
                    f"{L_mean_note}{cross_note}{h3_null_note}")

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
    "MECH_L_SPREAD_H1_THRESHOLD", "MECH_L_SPREAD_H2_THRESHOLD",
    "DEEP_SAT_MAX_SPREAD_THRESHOLD",
    "REQUIRED_FIELDS",
    "eval_phase_point", "selftest", "run_one_seed",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
