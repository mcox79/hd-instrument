"""Stage 1 Regime Probe 8: ALGEBRA (F fan-out) x CLEANUP_MECHANISM at cliff-adjacent regime.

Cell anchor: `stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1`
Pre-reg:     preregs/2026-07-03_stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1.md

Purpose:
    Fills the 4th missing data point on revised regime hypothesis "ALL Stage 1
    axes moderate CLEANUP_MECHANISM at cliff-adjacent regime; NONE at deep-
    saturation." Probes 1, 6 v2, 7 v2 have covered STORAGE, TOPOLOGY (F=[1,4,8,16]),
    N crosses with MECHANISM at (or approaching) cliff. This probe:
      - Adds F=2 as interstitial resolution (Probe 6 v2 missed F=2).
      - Uses a FIXED cliff-adjacent operating point (N=512, M=6400, corr=0.85, L=2)
        empirically confirmed non-saturated (mean acc 0.59-0.77 across F sweep).
      - Adds explicit H3 DEEP_SATURATION null control arm (N=8192, M=800, corr=0.60)
        where mech_var --> 0 by mechanism DEGENERACY (empirically saturated 1.0).

Empirical pre-reg bracket (2026-07-03 exp_dev, TR=40, single seed=7, prior to cell filing):
    Bracket 1 (cliff-adjacent, N=512 M=6400 corr=0.85 L=2):
        F=1  mean=0.59 spread=0.100 (mh=0.55 ic=0.58 sea=0.65)
        F=2  mean=0.68 spread=0.025 (mh=0.68 ic=0.70 sea=0.68)
        F=4  mean=0.77 spread=0.075 (mh=0.80 ic=0.78 sea=0.73)
        F=8  mean=0.66 spread=0.100 (mh=0.70 ic=0.60 sea=0.68)
        F=16 mean=0.73 spread=0.075 (mh=0.78 ic=0.73 sea=0.70)
    Bracket 2 (F=1 cliff walk at N=512 M=6400 L=2):
        corr=0.85 mean=0.59  <-- cliff-adjacent (LOCKED as operating point)
        corr=0.88 mean=0.27  (near-floor)
        corr=0.90 mean=0.12  (floor)
        corr=0.92 mean=0.03  (below floor)
    Bracket 3 (deep-saturation H3 arm, N=8192 M=800 corr=0.60 L=2):
        F=1  mean=1.00 spread=0.000
        F=4  mean=1.00 spread=0.000
        F=16 mean=1.00 spread=0.000
    All numbers MEASURED@scratchpad probe8_cliff_bracket.py 2026-07-03 (single-seed
    TR=40 bracket; noise floor spread ~ sqrt(0.5/40) ~ 0.08 approximately).

Cited source atoms (exact names per META_RULE_AC):
    META_saturation_floor_masks_null_variance_probe3_lesson (T4 MM_STANDARD)
    T3/EXP_stage1_regime_probe_2_N_x_cleanup_mechanism_v1_3seed_FULL_MM_STANDARD_cleanup_axis_regime_narrow_extended_to_N_axis
    MATH_STAGE1_REGIME_MAP_PROBE1_STORAGE_x_CLEANUP_CG_META_v1
    T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1
    T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1
    PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian
    feedback_plate_bound_too_pessimistic_for_sharded_fhrr_chain_composition_2026-07-03
    feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03

Reuse (Principle 11):
    Primitives imported from _stage1_physics_law_joint_composition_factorial_v1_core:
      CLEANUP_MECHANISMS, CLEANUP_REGISTRY, BETA, ALPHA_SOFT, DEVICE, GPU_NAME,
      build_rules, phase_corrupt, cleanup_argmax_idx, run_chain, cphasor_torch
    Verdict logic modeled on _stage1_regime_probe_6_topology_x_cleanup_non_saturated_v1_core
    (band-restricted discriminator + arm_tag routing).

Sweep grid FULL:
    CLIFF arm: F in {1,2,4,8,16} x 3 mech at (N=512, M=6400, corr=0.85, L=2, SHARDED) = 15 pts
    DEEP_SAT arm (H3 null): F in {1,4,16} x 3 mech at (N=8192, M=800, corr=0.60, L=2, SHARDED) = 9 pts
    SATURATION_PC arm: F=1 M=800 N=2048 corr=0.20 iterative_cosine (Gate D reproducer) = 1 pt
    TOTAL: 25 pts / seed
Sweep grid SMOKE:
    CLIFF arm: F in {1,16} (endpoints) x 3 mech at (N=512, M=6400, corr=0.85, L=2) = 6 pts
    DEEP_SAT arm spot-check: F=1 x 3 mech at (N=8192, M=800, corr=0.60, L=2) = 3 pts
    SATURATION_PC arm: 1 pt
    TOTAL: 10 pts

Hypotheses (falsifiable, restricted to CLIFF arm slices with grand-mean(acc) in [0.30, 0.95]):
    H1 (F ALGEBRA moderates at cliff-adjacent):
        max_per_F_mech_variance_in_band >= 0.10 at CLIFF arm
      -> F IS a moderator of CLEANUP_MECHANISM at cliff-adjacent regime;
         completes revised hypothesis "ALL Stage 1 axes moderate at cliff-adjacent".
    H2 (F does NOT moderate at cliff-adjacent):
        max_per_F_mech_variance_in_band < 0.05 at CLIFF arm
      -> ALGEBRA is degenerate; contradicts revised hypothesis; supports
         "STORAGE_UNIQUELY_moderates" thesis (Probe 1 CG_META).
    H3 (mechanism ranking crossover):
        mech_ranking changes across F within CLIFF band (MM_TENTATIVE).
    H3-NULL (DEEP_SAT control fires):
        DEEP_SAT arm max_mech_variance < 0.05 at N=8192 M=800 corr=0.60
      -> confirms mechanism DEGENERACY at deep-saturation; strengthens
         revised regime hypothesis (variance vanishes when substrate saturates).

Compute architecture: batched-GPU (USER-LOCKED). Auto-CUDA when available.
Sibling wrappers: exp_stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1_s{7,13,19}.py

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-07-03 (agent-spawn, Opus 4.7).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared (categorical accuracy; discriminator is F x MECH band-restricted spread)
# - baseline_in_band verified empirically (CLIFF arm mean 0.59-0.77 in [0.30, 0.95] band; DEEP_SAT arm saturated by design as null control)
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

ANCHOR_NAME = "stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1"

# ---------------------------------------------------------------------------
# Sweep constants (LOCKED at module init; MEASURED@empirical-bracket 2026-07-03)
# ---------------------------------------------------------------------------
# Primary axis: F fan-out (ALGEBRA in this cell); Probe 6 v2 had F=[1,4,8,16].
# F=2 added as interstitial resolution; F=[1,2,4,8,16] = 5 levels.
F_GRID_CLIFF_FULL = [1, 2, 4, 8, 16]
F_GRID_CLIFF_SMOKE = [1, 16]  # endpoints (2x speed vs full grid for local smoke)

# CLIFF-adjacent operating point (empirically LOCKED at TR=40 single seed=7):
#   at N=512 M=6400 corr=0.85 L=2: mean_acc across F = 0.59-0.77 in [0.30, 0.95] band.
#   cliff for F=1 sits at 0.85-0.88 (mean drops 0.59 -> 0.27); 0.85 is the mid-band
#   operating point. HYPOTHESIZED at TR=100 3-seed noise-floor ~ 0.05.
CLIFF_N = 512
CLIFF_M = 6400
CLIFF_CORR = 0.85

# DEEP_SAT arm (H3-NULL: mechanism DEGENERACY when saturated):
#   at N=8192 M=800 corr=0.60 L=2: mean_acc = 1.0 across F=[1,4,16], spread=0
#   HYPOTHESIZED at FULL TR=100: mech_var < 0.05 (empirically 0.0 at TR=40).
F_GRID_DEEP_SAT_FULL = [1, 4, 16]  # 3 levels sufficient for null-control assessment
F_GRID_DEEP_SAT_SMOKE = [1]        # single spot-check
DEEP_SAT_N = 8192
DEEP_SAT_M = 800
DEEP_SAT_CORR = 0.60

L_FIXED = 2

# SATURATION_PC arm (Gate D reproducer, cited from Probe 3/6/7 baseline)
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

# CLIFF main: 5 F x 3 mech = 15; DEEP_SAT: 3 F x 3 mech = 9; PC = 1. TOTAL 25.
EXPECTED_N_UNITS_FULL = (len(F_GRID_CLIFF_FULL) * len(CLEANUP_MECHANISMS)
                         + len(F_GRID_DEEP_SAT_FULL) * len(CLEANUP_MECHANISMS)
                         + 1)
# SMOKE: 2 F x 3 mech (cliff) + 1 F x 3 mech (deep_sat) + PC = 6 + 3 + 1 = 10.
EXPECTED_N_UNITS_SMOKE = (len(F_GRID_CLIFF_SMOKE) * len(CLEANUP_MECHANISMS)
                          + len(F_GRID_DEEP_SAT_SMOKE) * len(CLEANUP_MECHANISMS)
                          + 1)

# Non-saturated band
NON_SAT_BAND_LO = 0.30
NON_SAT_BAND_HI = 0.95

# H1/H2 thresholds (mirror Probe 6/7 v2)
MECH_VAR_H1_THRESHOLD = 0.10
MECH_VAR_H2_THRESHOLD = 0.05
# H3-NULL threshold (DEEP_SAT arm)
DEEP_SAT_MAX_VAR_THRESHOLD = 0.05

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
                           f"M={M_props} N={N} F={F}")

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
    if EXPECTED_N_UNITS_SMOKE != 10:
        return False, (f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 10 "
                       f"(6 cliff + 3 deep_sat + 1 PC)")
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} "
                f"SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. Sanity: 3 cleanup mechanisms produce distinct outputs at F=2 multi-slot path
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(999)
    M_probe = 50
    N_test = 512
    F_test = 2
    TR = 20
    props, perms, IMPL, POS, sharded_codebook, bundle_vec = build_rules(
        M_probe, F_test, gen, DEVICE, N_test)
    ci = torch.arange(TR, device=DEVICE) % M_probe
    A_cur = props[ci]
    f_step = torch.ones((TR,), dtype=torch.long, device=DEVICE)
    rule_batch = sharded_codebook[ci, f_step]
    cand = rule_batch * A_cur.conj() * POS[1].unsqueeze(0).conj() * IMPL.conj().unsqueeze(0)
    cand_corr = phase_corrupt(cand, 0.30, gen, DEVICE)
    mech_hashes = {}
    for mech in CLEANUP_MECHANISMS:
        fn = CLEANUP_REGISTRY[mech]
        out = fn(cand_corr, props)
        mech_hashes[mech] = hashlib.sha256(
            out.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    if len(set(mech_hashes.values())) != len(CLEANUP_MECHANISMS):
        return False, (f"cleanup_mechanisms produce identical outputs at F=2: "
                       f"{mech_hashes}")
    msgs.append(f"3 mechs distinct at F=2: {list(mech_hashes.values())}")

    # 3. F-axis arms_differ: F=1 vs F=16 codebook hashes MUST differ (topology axis fires)
    gen.manual_seed(1017)
    _, _, _, _, shard1, _ = build_rules(M_probe, 1, gen, DEVICE, N_test)
    gen.manual_seed(1017)
    _, _, _, _, shard16, _ = build_rules(M_probe, 16, gen, DEVICE, N_test)
    h1 = hashlib.sha256(shard1.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    h16 = hashlib.sha256(shard16.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    if h1 == h16:
        return False, (f"F=1 vs F=16 sharded codebooks identical (topology axis "
                       f"has no effect); hash={h1}")
    # F=2 also distinct from F=1 and F=16
    gen.manual_seed(1017)
    _, _, _, _, shard2, _ = build_rules(M_probe, 2, gen, DEVICE, N_test)
    h2 = hashlib.sha256(shard2.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    if h2 == h1 or h2 == h16:
        return False, (f"F=2 collides with F=1 or F=16: h1={h1} h2={h2} h16={h16}")
    msgs.append(f"F-axis fires: F1={h1} F2={h2} F16={h16}")

    # 4. SATURATION_PC easy gate reproducer (Gate D at reduced TR)
    gen.manual_seed(1013)
    pc = SATURATION_PC_REGIME
    props2, perms2, IMPL2, POS2, sh2, bd2 = build_rules(
        pc["M"], pc["F"], gen, DEVICE, pc["N"])
    acc_easy, _ = run_chain(pc["storage"], pc["cleanup_mechanism"],
                            pc["L"], pc["F"], 40,
                            props2, perms2, IMPL2, POS2, sh2, bd2,
                            pc["corruption"], gen, DEVICE)
    if acc_easy < 0.85:
        return False, (f"SATURATION_PC selftest (F=1 M=800 N=2048 corr=0.20 "
                       f"iterative_cosine) expected >= 0.85 at TR=40; "
                       f"got {acc_easy:.3f}")
    msgs.append(f"SATURATION_PC selftest (TR=40): acc={acc_easy:.3f}")

    # 5. Cliff-adjacent regime sanity (F=1 at cliff should land in band)
    #    MEASURED@bracket 2026-07-03: mean=0.59 at TR=40 seed=7.
    #    Selftest at TR=20 seed=999 for speed; loose sanity check [0.30, 0.95].
    gen.manual_seed(3131)
    props3, perms3, IMPL3, POS3, sh3, bd3 = build_rules(
        CLIFF_M, 1, gen, DEVICE, CLIFF_N)
    acc_cliff, _ = run_chain("SHARDED", "iterative_cosine",
                             L_FIXED, 1, 20,
                             props3, perms3, IMPL3, POS3, sh3, bd3,
                             CLIFF_CORR, gen, DEVICE)
    if not (0.20 <= acc_cliff <= 0.98):
        return False, (f"CLIFF regime sanity (F=1 M={CLIFF_M} N={CLIFF_N} "
                       f"corr={CLIFF_CORR} iterative_cosine TR=20): "
                       f"acc={acc_cliff:.3f} outside [0.20, 0.98]; regime "
                       f"drifted from empirical bracket")
    msgs.append(f"CLIFF regime sanity (TR=20): acc={acc_cliff:.3f}")

    # 6. DEEP_SAT regime sanity (saturated expected)
    #    MEASURED@bracket 2026-07-03: all F all mech = 1.0 at TR=40.
    gen.manual_seed(4141)
    props4, perms4, IMPL4, POS4, sh4, bd4 = build_rules(
        DEEP_SAT_M, 1, gen, DEVICE, DEEP_SAT_N)
    acc_deep, _ = run_chain("SHARDED", "iterative_cosine",
                            L_FIXED, 1, 20,
                            props4, perms4, IMPL4, POS4, sh4, bd4,
                            DEEP_SAT_CORR, gen, DEVICE)
    if acc_deep < 0.95:
        return False, (f"DEEP_SAT regime sanity (F=1 M={DEEP_SAT_M} N={DEEP_SAT_N} "
                       f"corr={DEEP_SAT_CORR} iterative_cosine TR=20): "
                       f"acc={acc_deep:.3f} < 0.95; DEEP_SAT arm did not "
                       f"saturate as expected; regime drifted from empirical")
    msgs.append(f"DEEP_SAT regime sanity (TR=20): acc={acc_deep:.3f}")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed(seed: int, run_mode: str) -> Dict[str, Any]:
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        F_grid_cliff = F_GRID_CLIFF_SMOKE
        F_grid_deep = F_GRID_DEEP_SAT_SMOKE
        TR = TR_SMOKE
        expected_n = EXPECTED_N_UNITS_SMOKE
    else:
        F_grid_cliff = F_GRID_CLIFF_FULL
        F_grid_deep = F_GRID_DEEP_SAT_FULL
        TR = TR_FULL
        expected_n = EXPECTED_N_UNITS_FULL

    mech_grid = list(CLEANUP_MECHANISMS)

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"mech={mech_grid} F_cliff={F_grid_cliff} F_deep={F_grid_deep} "
          f"cliff=(N={CLIFF_N},M={CLIFF_M},corr={CLIFF_CORR}) "
          f"deep=(N={DEEP_SAT_N},M={DEEP_SAT_M},corr={DEEP_SAT_CORR}) "
          f"L={L_FIXED} TR={TR} expected_n={expected_n}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    salt = 0
    t0 = time.perf_counter()

    # 1) CLIFF arm: F sweep x mech at (CLIFF_N, CLIFF_M, CLIFF_CORR)
    for F in F_grid_cliff:
        for mech in mech_grid:
            salt += 1
            pt = eval_phase_point(mech, CLIFF_M, CLIFF_N, F, L_FIXED,
                                  CLIFF_CORR, "SHARDED", TR, seed, salt,
                                  arm_tag="CLIFF")
            phase_map.append(pt)
            print(f"  [{len(phase_map):3d}/{expected_n:3d}] CLIFF     "
                  f"F={F:2d} mech={mech:22s} M={CLIFF_M} N={CLIFF_N} "
                  f"c={CLIFF_CORR:.2f} acc={pt['acc']:.4f} "
                  f"dt={pt['elapsed_s']:.2f}s", flush=True)

    # 2) DEEP_SAT arm (H3-NULL): F sweep x mech at (DEEP_SAT_N, DEEP_SAT_M, DEEP_SAT_CORR)
    for F in F_grid_deep:
        for mech in mech_grid:
            salt += 1
            pt = eval_phase_point(mech, DEEP_SAT_M, DEEP_SAT_N, F, L_FIXED,
                                  DEEP_SAT_CORR, "SHARDED", TR, seed, salt,
                                  arm_tag="DEEP_SAT")
            phase_map.append(pt)
            print(f"  [{len(phase_map):3d}/{expected_n:3d}] DEEP_SAT  "
                  f"F={F:2d} mech={mech:22s} M={DEEP_SAT_M} N={DEEP_SAT_N} "
                  f"c={DEEP_SAT_CORR:.2f} acc={pt['acc']:.4f} "
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
          f"F={pc['F']:2d} mech={pc['cleanup_mechanism']:22s} "
          f"M={pc['M']} N={pc['N']} c={pc['corruption']:.2f} "
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
    # Per-F mech spread (max-min across 3 mechs at each F) on CLIFF arm
    per_F_cliff_variance: Dict[str, Dict[str, Any]] = {}
    per_F_cliff_variance_in_band: Dict[str, Dict[str, Any]] = {}
    for F in F_grid_cliff:
        triple = {}
        for mech in mech_grid:
            matches = [p["acc"] for p in cliff_pts
                       if p["F"] == F and p["cleanup_mechanism"] == mech]
            if matches:
                triple[mech] = matches[0]
        if len(triple) == len(mech_grid):
            vals = list(triple.values())
            spread = round(max(vals) - min(vals), 4)
            cell_mean = float(np.mean(vals))
            per_F_cliff_variance[str(F)] = {
                "accs_by_mech": {m: round(v, 4) for m, v in triple.items()},
                "mean_acc": round(cell_mean, 4),
                "spread": spread,
                "in_non_saturated_band": bool(
                    NON_SAT_BAND_LO <= cell_mean <= NON_SAT_BAND_HI),
            }
            if NON_SAT_BAND_LO <= cell_mean <= NON_SAT_BAND_HI:
                per_F_cliff_variance_in_band[str(F)] = per_F_cliff_variance[str(F)]

    max_cliff_var = max(
        (v["spread"] for v in per_F_cliff_variance.values()), default=0.0)
    max_cliff_var_in_band = max(
        (v["spread"] for v in per_F_cliff_variance_in_band.values()), default=0.0)

    # DEEP_SAT arm summary (H3-NULL)
    deep_accs = [p["acc"] for p in deep_pts]
    deep_mean = float(np.mean(deep_accs)) if deep_accs else 0.0
    deep_min = float(np.min(deep_accs)) if deep_accs else 0.0
    deep_max = float(np.max(deep_accs)) if deep_accs else 0.0
    per_F_deep_variance: Dict[str, Dict[str, Any]] = {}
    for F in F_grid_deep:
        triple = {}
        for mech in mech_grid:
            matches = [p["acc"] for p in deep_pts
                       if p["F"] == F and p["cleanup_mechanism"] == mech]
            if matches:
                triple[mech] = matches[0]
        if len(triple) == len(mech_grid):
            vals = list(triple.values())
            spread = round(max(vals) - min(vals), 4)
            per_F_deep_variance[str(F)] = {
                "accs_by_mech": {m: round(v, 4) for m, v in triple.items()},
                "mean_acc": round(float(np.mean(vals)), 4),
                "spread": spread,
            }
    max_deep_var = max(
        (v["spread"] for v in per_F_deep_variance.values()), default=0.0)
    # H3-NULL fires when DEEP_SAT max_spread < 0.05 (mechanism DEGENERACY at saturation)
    h3_null_fires = (max_deep_var < DEEP_SAT_MAX_VAR_THRESHOLD)
    # DEEP_SAT arm should saturate (mean >= 0.95)
    deep_saturated = (deep_mean >= 0.95)

    # H3 crossover on CLIFF arm within band
    cliff_ranking_by_F_in_band: Dict[str, Dict[str, Any]] = {}
    for F_str, block in per_F_cliff_variance_in_band.items():
        ranking = tuple(sorted(block["accs_by_mech"],
                                key=lambda m: -block["accs_by_mech"][m]))
        cliff_ranking_by_F_in_band[F_str] = {
            "ranking": ranking,
            "means": block["accs_by_mech"],
        }
    rankings = [v["ranking"] for v in cliff_ranking_by_F_in_band.values()]
    mech_ranking_crossover = len(set(rankings)) > 1 if rankings else False

    # Escapes-saturation for CLIFF arm SMOKE gate (per-F semantics)
    per_F_cliff_mean_acc = {F_str: round(v["mean_acc"], 4)
                             for F_str, v in per_F_cliff_variance.items()}
    escapes_saturation_cliff = any(v < NON_SAT_BAND_HI
                                    for v in per_F_cliff_mean_acc.values())

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
                        "L": L_FIXED, "storage": "SHARDED"},
            "F_grid": F_grid_cliff,
            "mean_acc": round(cliff_mean, 4),
            "min_acc": round(cliff_min, 4),
            "max_acc": round(cliff_max, 4),
            "n_in_non_saturated_band": cliff_in_band,
            "n_total": len(cliff_accs),
            "fraction_in_band": round(cliff_in_band_frac, 4),
            "per_F_variance": per_F_cliff_variance,
            "per_F_variance_in_band": per_F_cliff_variance_in_band,
            "per_F_mean_acc": per_F_cliff_mean_acc,
            "max_per_F_mech_variance": round(max_cliff_var, 4),
            "max_per_F_mech_variance_in_band": round(max_cliff_var_in_band, 4),
            "escapes_saturation_ceiling": escapes_saturation_cliff,
            "mech_ranking_by_F_in_band": cliff_ranking_by_F_in_band,
            "mech_ranking_crossover": mech_ranking_crossover,
        },
        "deep_sat_arm": {
            "regime": {"N": DEEP_SAT_N, "M": DEEP_SAT_M, "corr": DEEP_SAT_CORR,
                        "L": L_FIXED, "storage": "SHARDED"},
            "F_grid": F_grid_deep,
            "mean_acc": round(deep_mean, 4),
            "min_acc": round(deep_min, 4),
            "max_acc": round(deep_max, 4),
            "per_F_variance": per_F_deep_variance,
            "max_per_F_mech_variance": round(max_deep_var, 4),
            "saturated": deep_saturated,
            "h3_null_fires": h3_null_fires,
            "h3_null_threshold": DEEP_SAT_MAX_VAR_THRESHOLD,
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
        return False, (f"saturation_pc_fail: SHARDED F=1 M=800 N=2048 corr=0.20 "
                       f"iterative_cosine acc={pc.get('acc')} < "
                       f"threshold={pc.get('threshold')}")
    cliff = body.get("cliff_arm", {})
    if not cliff.get("escapes_saturation_ceiling"):
        return False, (f"escapes_saturation_ceiling_fail: no F-slice on CLIFF "
                       f"arm has mean-acc < {NON_SAT_BAND_HI}; per_F_mean_acc="
                       f"{cliff.get('per_F_mean_acc')}; CLIFF regime fully "
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

    # Discriminator variance is INFORMATIONAL, not gating (null-hypothesis discipline)
    max_var_ib = cliff.get("max_per_F_mech_variance_in_band", 0.0)
    deep_var = deep.get("max_per_F_mech_variance", 0.0)
    return True, (f"smoke_gate_pass: cardinality_ok + 3-mech-hash-distinct + "
                  f"pc_acc={pc.get('acc')} (>={pc.get('threshold')}) + "
                  f"cliff_mean={cliff.get('mean_acc')} escapes_saturation + "
                  f"deep_sat_saturated(mean={deep.get('mean_acc')}); "
                  f"informational: cliff_max_per_F_var_in_band={max_var_ib} "
                  f"deep_max_var={deep_var} h3_null_fires="
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
        vmsg = (f"HARD_FAIL_SATURATION_PC_MISMATCH: SHARDED F=1 M=800 N=2048 "
                f"corr=0.20 iterative_cosine acc={pc.get('acc')} < "
                f"threshold={pc.get('threshold')} (Gate D violation)")
    elif not deep.get("saturated"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_DEEP_SAT_ARM_DRIFT: DEEP_SAT mean_acc="
                f"{deep.get('mean_acc')} < 0.95; H3-NULL control regime failed "
                f"to saturate; regime construction broken")
    elif cliff.get("fraction_in_band", 0.0) < 0.30:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_CLIFF_ARM_ESCAPES_SATURATION_FAIL: "
                f"cliff fraction_in_band={cliff.get('fraction_in_band')} < 0.30; "
                f"CLIFF arm failed to land in non-saturated band; cannot claim "
                f"H1 or H2 with confidence")
    else:
        cliff_max_var_ib = cliff.get("max_per_F_mech_variance_in_band", 0.0)
        deep_max_var = deep.get("max_per_F_mech_variance", 0.0)
        h3_null_fires = deep.get("h3_null_fires", False)
        crossover = cliff.get("mech_ranking_crossover", False)
        cross_note = (" ; mech_ranking_crossover=True (H3 MM_TENTATIVE)"
                      if crossover else "")
        h3_null_note = (f" ; H3-NULL fires(deep_max_var={deep_max_var} < "
                        f"{DEEP_SAT_MAX_VAR_THRESHOLD})"
                        if h3_null_fires else
                        f" ; H3-NULL DID NOT FIRE(deep_max_var={deep_max_var} "
                        f">= {DEEP_SAT_MAX_VAR_THRESHOLD}) -- mechanism "
                        f"variance surprisingly non-zero at deep-saturation")

        if cliff_max_var_ib >= MECH_VAR_H1_THRESHOLD:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H1_F_ALGEBRA_MODERATES_AT_CLIFF_ADJACENT: "
                    f"cliff max_per_F_mech_variance_in_band={cliff_max_var_ib} "
                    f">= {MECH_VAR_H1_THRESHOLD}; F IS a moderator of "
                    f"CLEANUP_MECHANISM at cliff-adjacent regime; completes "
                    f"'ALL Stage 1 axes moderate at cliff-adjacent' regime "
                    f"hypothesis alongside Probes 1/6v2/7v2"
                    f"{cross_note}{h3_null_note}")
        elif cliff_max_var_ib < MECH_VAR_H2_THRESHOLD:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H2_F_ALGEBRA_DEGENERACY_AT_CLIFF_ADJACENT: "
                    f"cliff max_per_F_mech_variance_in_band={cliff_max_var_ib} "
                    f"< {MECH_VAR_H2_THRESHOLD}; F does NOT moderate "
                    f"CLEANUP_MECHANISM at cliff-adjacent regime; contradicts "
                    f"revised 'ALL axes moderate' hypothesis; supports "
                    f"STORAGE_UNIQUELY_moderates thesis (Probe 1 CG_META)"
                    f"{cross_note}{h3_null_note}")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_WEAK_F_MODERATION: cliff max_per_F_mech_"
                    f"variance_in_band={cliff_max_var_ib} in "
                    f"[{MECH_VAR_H2_THRESHOLD}, {MECH_VAR_H1_THRESHOLD}); "
                    f"weak F-moderation (MM_TENTATIVE); consider refined "
                    f"sweep or higher TR to localize"
                    f"{cross_note}{h3_null_note}")

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
    "F_GRID_CLIFF_FULL", "F_GRID_CLIFF_SMOKE",
    "F_GRID_DEEP_SAT_FULL", "F_GRID_DEEP_SAT_SMOKE",
    "CLIFF_N", "CLIFF_M", "CLIFF_CORR",
    "DEEP_SAT_N", "DEEP_SAT_M", "DEEP_SAT_CORR",
    "L_FIXED", "TR_FULL", "TR_SMOKE",
    "SATURATION_PC_REGIME", "SATURATION_PC_THRESHOLD",
    "NON_SAT_BAND_LO", "NON_SAT_BAND_HI",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "MECH_VAR_H1_THRESHOLD", "MECH_VAR_H2_THRESHOLD",
    "DEEP_SAT_MAX_VAR_THRESHOLD",
    "REQUIRED_FIELDS",
    "eval_phase_point", "selftest", "run_one_seed",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
