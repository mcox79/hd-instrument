"""Regime Probe 6 core: NON-SATURATED TOPOLOGY x CLEANUP_MECHANISM revival.

Cell anchor: `stage1_regime_probe_6_topology_x_cleanup_non_saturated_v1`
Pre-reg: preregs/2026-07-03_stage1_regime_probe_6_topology_x_cleanup_non_saturated_v1.md
Arc: Stage 1 REGIME MAP of 5 CG_META axes (USER 2026-07-03).

Purpose:
    Sixth probe in the Stage 1 Regime Map arc. Skunkworks VET of Probe 3 revealed
    that ALL 72 phase points reached acc=1.0 (saturation-vacuous null). This
    revival forces the regime BELOW saturation so mechanism variance has room to
    appear: adds F=16, corruption in {0.60, 0.70}, extends M to 6400, sweeps N
    in {2048, 8192}. STORAGE fixed = SHARDED (Probe 1 owns STORAGE cross-term).

    If mech-variance appears at non-saturated slices -> Probe 3's null was
    saturation artifact; TOPOLOGY IS a moderator (H1).
    If mech-variance ~0 at non-saturated mean-acc in [0.30, 0.95] -> genuine
    null at non-saturated regime; Probe 1's STORAGE-uniquely-moderates thesis
    validated (H2).

Hypotheses (falsifiable; see prereg for full statements):
    H1: F_x_cleanup_max_abs_deviation_in_band >= 0.15 -> TOPOLOGY is moderator.
    H2: within-band mech-variance < 0.05 -> genuine null at non-saturated regime.
    H3: mech-ranking crossover across F within band -> F-dependent crossover.

Cited source atoms (exact names, no abstraction; META_RULE_AC):
    META_saturation_floor_masks_null_variance_probe3_lesson (T4 METHODOLOGY_RULE 2026-07-03)
    regime_probe_3_topology_x_cleanup_v1_MM_BOUNDED_NULL (Probe 3 landing)
    MATH_STAGE1_REGIME_MAP_PROBE1_STORAGE_x_CLEANUP_CG_META_v1 (Probe 1 template)
    T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1 (F axis)
    T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1 (SHARDED-vs-BUNDLED)
    PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian (3 non-Hebbian mechs)
    feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03

Regime: sharded-rule-storage FHRR chain composition (L=2 fixed).
Primitives imported from `_stage1_physics_law_joint_composition_factorial_v1_core`
(Principle 11 reuse; no re-implementation).

Sweep FULL: 3 cleanup x 4 F x 3 M x 2 N x 3 corruption + 1 SATURATION_PC = 217 pts / seed.
Sweep SMOKE: 3 cleanup x 2 F x 1 M x 1 N x 1 corruption + 1 SATURATION_PC = 7 pts / seed.
L fixed = 2. STORAGE fixed = SHARDED (except SATURATION_PC arm is also SHARDED).

Compute architecture: batched-GPU (auto-CUDA; CPU fallback for local smoke).

ASCII-only. No unicode, no em-dashes, no emojis.
Author: exp_dev 2026-07-03 (agent-spawn, Opus 4.7). USER-directed arc.
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

# Reuse primitives from Option Y core (Principle 11).
from experiments._stage1_physics_law_joint_composition_factorial_v1_core import (
    CLEANUP_MECHANISMS,
    CLEANUP_REGISTRY,
    BETA,
    ALPHA_SOFT,
    DEVICE,
    GPU_NAME,
    build_rules,
    run_chain,
    cleanup_argmax_idx,
    phase_corrupt,
    cphasor_torch,
)

ANCHOR_NAME = "stage1_regime_probe_6_topology_x_cleanup_non_saturated_v1"

# ---------------------------------------------------------------------------
# Sweep constants (LOCKED at module init)
# ---------------------------------------------------------------------------
# TOPOLOGY axis: fan-out F in the sharded DAG.
F_GRID_FULL = [1, 4, 8, 16]
F_GRID_SMOKE = [1, 16]

# M sweep extended to 6400 (revival criterion: sharded_pc drops below 0.95 at high corr).
M_GRID_FULL = [800, 3200, 6400]
M_GRID_SMOKE = [6400]

# N SWEEP (v2 revision 2026-07-03: prereg's [2048, 8192] misprediction — larger N
# makes SHARDED MORE robust to corruption via more voting dims. Empirical cliff
# sits at smaller N. See feedback_plate_bound_too_pessimistic_for_sharded_fhrr_
# chain_composition_2026-07-03 memory rule).
N_GRID_FULL = [512, 2048]
N_GRID_SMOKE = [512]

# corruption raised (v2: prereg's [0.45, 0.60, 0.70] was too low — empirical cliff
# at N=2048 sits above corr=0.90; v2 grid samples both sides of the N=512 cliff).
CORRUPTION_GRID_FULL = [0.70, 0.85, 0.90]
CORRUPTION_GRID_SMOKE = [0.85]

L_FIXED = 2

TR_FULL = 60
TR_SMOKE = 40

# Non-saturated band definition (accuracy interval where mech-variance is measurable).
NON_SAT_BAND_LO = 0.30
NON_SAT_BAND_HI = 0.95

# Positive-control SATURATION arm: reproduces Probe 3 baseline acc=1.0.
# SHARDED F=1 M=800 N=2048 corr=0.20 iterative_cosine -> target acc >= 0.95.
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

EXPECTED_N_UNITS_FULL = (len(CLEANUP_MECHANISMS) * len(F_GRID_FULL)
                         * len(M_GRID_FULL) * len(N_GRID_FULL)
                         * len(CORRUPTION_GRID_FULL)) + 1
# 3 * 4 * 3 * 2 * 3 + 1 = 217

EXPECTED_N_UNITS_SMOKE = (len(CLEANUP_MECHANISMS) * len(F_GRID_SMOKE)
                          * len(M_GRID_SMOKE) * len(N_GRID_SMOKE)
                          * len(CORRUPTION_GRID_SMOKE)) + 1
# 3 * 2 * 1 * 1 * 1 + 1 = 7

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# Per-phase-point evaluation (uses imported build_rules + run_chain)
# ---------------------------------------------------------------------------
def eval_phase_point(mechanism: str, M_props: int, N: int, F: int, L: int,
                     corruption: float, storage: str, TR: int, seed: int,
                     salt: int) -> Dict[str, Any]:
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
        raise RuntimeError(
            f"NAN_IN_SHARDED_CODEBOOK mech={mechanism} M={M_props} N={N} F={F}")

    acc, final_ci = run_chain(storage, mechanism, L, F, TR,
                              props, perms, IMPL, POS,
                              sharded_codebook, bundle_vec,
                              corruption, gen, device)

    shard_bytes = sharded_codebook.detach().cpu().numpy().tobytes()
    bundle_bytes = bundle_vec.detach().cpu().numpy().tobytes()
    ci_bytes = final_ci.detach().cpu().numpy().tobytes()
    shard_hash = hashlib.sha256(shard_bytes).hexdigest()[:16]
    bundle_hash = hashlib.sha256(bundle_bytes).hexdigest()[:16]
    ci_hash = hashlib.sha256(ci_bytes).hexdigest()[:16]

    if device == "cuda":
        peak_mem_mb = round(torch.cuda.max_memory_allocated() / 1e6, 1)
    else:
        peak_mem_mb = -1.0
    elapsed = time.perf_counter() - t0

    del props, perms, IMPL, POS, sharded_codebook, bundle_vec, final_ci
    if device == "cuda":
        torch.cuda.empty_cache()

    return {
        "cleanup_mechanism": mechanism,
        "M": int(M_props),
        "N": int(N),
        "F": int(F),
        "L": int(L),
        "corruption": float(corruption),
        "storage": storage,
        "TR": int(TR),
        "acc": round(float(acc), 4),
        "shard_hash": shard_hash,
        "bundle_hash": bundle_hash,
        "output_hash": ci_hash,
        "peak_mem_mb": peak_mem_mb,
        "elapsed_s": round(elapsed, 3),
    }


# ---------------------------------------------------------------------------
# Selftest (formula check at reduced grid; wall target < 60s)
# ---------------------------------------------------------------------------
def selftest() -> Tuple[bool, str]:
    msgs = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 217:
        return False, (f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 217 "
                       f"(216 factorial + 1 SATURATION_PC)")
    if EXPECTED_N_UNITS_SMOKE != 7:
        return False, (f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 7 "
                       f"(6 factorial + 1 SATURATION_PC)")
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. Sanity: 3 cleanup mechanisms produce distinct outputs at F=2 multi-slot path
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(999)
    M_props = 50
    N_test = 512
    F = 2
    TR = 20
    props, perms, IMPL, POS, sharded_codebook, bundle_vec = build_rules(
        M_props, F, gen, DEVICE, N_test)
    ci = torch.arange(TR, device=DEVICE) % M_props
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
    msgs.append(f"3 mechanisms distinct at F=2: {list(mech_hashes.values())}")

    # 3. Positive-control (Gate D): SHARDED iterative_cosine at F=1 easy regime
    gen.manual_seed(1013)
    acc_easy, _ = run_chain("SHARDED", "iterative_cosine", L=2, F=1, TR=40,
                            props=props, perms=perms, IMPL=IMPL, POS=POS,
                            sharded_codebook=sharded_codebook,
                            bundle_vec=bundle_vec,
                            corruption=0.05, gen=gen, device=DEVICE)
    if acc_easy < 0.80:
        return False, (f"SHARDED PC easy (M=50, N=512, F=2, L=2, corr=0.05) "
                       f"expected >= 0.80; got {acc_easy:.3f}")
    msgs.append(f"SHARDED PC easy: acc={acc_easy:.3f}")

    # 4. F-axis discriminator sanity: F=1 vs F=16 produce DIFFERENT codebook hashes
    #    at same M/N same seed (arms_must_differ across TOPOLOGY axis endpoints).
    gen.manual_seed(1017)
    props1, perms1, IMPL1, POS1, shard1, bundle1 = build_rules(
        M_props, 1, gen, DEVICE, N_test)
    gen.manual_seed(1017)
    props16, perms16, IMPL16, POS16, shard16, bundle16 = build_rules(
        M_props, 16, gen, DEVICE, N_test)
    hash_F1 = hashlib.sha256(shard1.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    hash_F16 = hashlib.sha256(shard16.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    if hash_F1 == hash_F16:
        return False, (f"F=1 and F=16 sharded codebooks identical (topology axis "
                       f"has no effect); hash={hash_F1}")
    msgs.append(f"F-axis fires (F1 vs F16): F1_hash={hash_F1} F16_hash={hash_F16}")

    # 5. N-axis discriminator sanity: same seed, N=2048 vs N=8192 produce different
    #    output shapes (basic scale-axis wiring sanity).
    gen.manual_seed(2027)
    p_2048, _, _, _, _, _ = build_rules(20, 1, gen, DEVICE, 2048)
    gen.manual_seed(2027)
    p_8192, _, _, _, _, _ = build_rules(20, 1, gen, DEVICE, 8192)
    if p_2048.shape[-1] != 2048 or p_8192.shape[-1] != 8192:
        return False, (f"N-axis wiring broken: props shapes "
                       f"{tuple(p_2048.shape)} vs {tuple(p_8192.shape)}")
    msgs.append(f"N-axis fires: props.shape[-1] {p_2048.shape[-1]} vs {p_8192.shape[-1]}")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed(seed: int, run_mode: str) -> Dict[str, Any]:
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        mech_grid = list(CLEANUP_MECHANISMS)
        F_grid = F_GRID_SMOKE
        M_grid = M_GRID_SMOKE
        N_grid = N_GRID_SMOKE
        corr_grid = CORRUPTION_GRID_SMOKE
        TR = TR_SMOKE
        expected_n = EXPECTED_N_UNITS_SMOKE
    else:
        mech_grid = list(CLEANUP_MECHANISMS)
        F_grid = F_GRID_FULL
        M_grid = M_GRID_FULL
        N_grid = N_GRID_FULL
        corr_grid = CORRUPTION_GRID_FULL
        TR = TR_FULL
        expected_n = EXPECTED_N_UNITS_FULL

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"mechs={mech_grid} F={F_grid} M={M_grid} N={N_grid} L={L_FIXED} "
          f"corr={corr_grid} TR={TR} expected_n={expected_n}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    salt = 0
    t0 = time.perf_counter()

    # 1) Main factorial grid: SHARDED storage
    for mech in mech_grid:
        for F in F_grid:
            for M_props in M_grid:
                for N in N_grid:
                    for corr in corr_grid:
                        salt += 1
                        pt = eval_phase_point(mech, M_props, N, F, L_FIXED,
                                              corr, "SHARDED", TR, seed, salt)
                        phase_map.append(pt)
                        print(f"  [{len(phase_map):3d}/{expected_n:3d}] "
                              f"mech={mech:22s} F={F:2d} M={M_props:5d} "
                              f"N={N:5d} L={L_FIXED} c={corr:.2f} "
                              f"storage=SHARDED acc={pt['acc']:.4f} "
                              f"dt={pt['elapsed_s']:.2f}s", flush=True)

    # 2) SATURATION positive-control arm (reproduces Probe 3 baseline)
    salt += 1
    pc = SATURATION_PC_REGIME
    pc_pt = eval_phase_point(pc["cleanup_mechanism"], pc["M"], pc["N"],
                             pc["F"], pc["L"], pc["corruption"],
                             pc["storage"], TR, seed, salt)
    pc_pt["is_saturation_pc"] = True
    phase_map.append(pc_pt)
    print(f"  [{len(phase_map):3d}/{expected_n:3d}] SATURATION_PC "
          f"mech={pc['cleanup_mechanism']} M={pc['M']} N={pc['N']} "
          f"F={pc['F']} L={pc['L']} c={pc['corruption']:.2f} "
          f"storage={pc['storage']} acc={pc_pt['acc']:.4f}", flush=True)

    elapsed = time.perf_counter() - t0
    observed_n = len(phase_map)
    cardinality_ok = (observed_n == expected_n)

    # arms_differ across 3 cleanup mechanisms (SHARDED main-grid outputs only)
    main_pts = [p for p in phase_map if not p.get("is_saturation_pc")]
    mech_output_hashes: Dict[str, List[str]] = {m: [] for m in CLEANUP_MECHANISMS}
    for pt in main_pts:
        mech_output_hashes[pt["cleanup_mechanism"]].append(pt["output_hash"])
    mech_hash_agg = {m: hashlib.sha256(
        json.dumps(v, sort_keys=True).encode("utf-8")).hexdigest()[:16]
                     for m, v in mech_output_hashes.items()}
    n_distinct_mechs = len(set(mech_hash_agg.values()))

    # SATURATION_PC pass check: reproduces Probe 3 baseline acc >= 0.95
    sat_pc_acc = pc_pt["acc"]
    sat_pc_pass = sat_pc_acc >= SATURATION_PC_THRESHOLD

    # Escapes-saturation-ceiling gate: mean(acc across SHARDED main-grid) < 0.95
    if main_pts:
        main_grid_mean_acc = float(np.mean([p["acc"] for p in main_pts]))
        main_grid_min_acc = float(np.min([p["acc"] for p in main_pts]))
        main_grid_max_acc = float(np.max([p["acc"] for p in main_pts]))
    else:
        main_grid_mean_acc = 0.0
        main_grid_min_acc = 0.0
        main_grid_max_acc = 0.0
    escapes_saturation_ceiling = main_grid_mean_acc < 0.95

    # In-band fraction (for FULL discriminator scope)
    in_band_pts = [p for p in main_pts
                   if NON_SAT_BAND_LO <= p["acc"] <= NON_SAT_BAND_HI]
    in_band_frac = (len(in_band_pts) / max(len(main_pts), 1))

    # Per-F mechanism variance (KEY discriminator) restricted to non-sat band.
    # For each F, compute across-mech max(acc) - min(acc) at each (M, N, corr).
    per_F_mech_variance: Dict[str, Dict[str, Any]] = {}
    per_F_mech_variance_in_band: Dict[str, Dict[str, Any]] = {}
    for F in F_grid:
        per_cell_var: Dict[str, float] = {}
        per_cell_var_in_band: Dict[str, float] = {}
        max_var = 0.0
        max_var_in_band = 0.0
        for M_props in M_grid:
            for N in N_grid:
                for corr in corr_grid:
                    triple = []
                    for mech in mech_grid:
                        matches = [p for p in main_pts
                                   if p["cleanup_mechanism"] == mech
                                   and p["F"] == F
                                   and p["M"] == M_props
                                   and p["N"] == N
                                   and abs(p["corruption"] - corr) < 1e-6]
                        if matches:
                            triple.append(matches[0]["acc"])
                    if len(triple) == len(mech_grid):
                        var = round(max(triple) - min(triple), 4)
                        cell_key = f"M{M_props}_N{N}_c{corr:.2f}"
                        per_cell_var[cell_key] = var
                        if var > max_var:
                            max_var = var
                        cell_mean = float(np.mean(triple))
                        if NON_SAT_BAND_LO <= cell_mean <= NON_SAT_BAND_HI:
                            per_cell_var_in_band[cell_key] = var
                            if var > max_var_in_band:
                                max_var_in_band = var
        per_F_mech_variance[str(F)] = {
            "per_cell_mech_variance": per_cell_var,
            "max_mech_variance": round(max_var, 4),
        }
        per_F_mech_variance_in_band[str(F)] = {
            "per_cell_mech_variance_in_band": per_cell_var_in_band,
            "max_mech_variance_in_band": round(max_var_in_band, 4),
            "n_cells_in_band": len(per_cell_var_in_band),
        }

    max_per_F_variance = max(
        (v["max_mech_variance"] for v in per_F_mech_variance.values()),
        default=0.0)
    max_per_F_variance_in_band = max(
        (v["max_mech_variance_in_band"] for v in per_F_mech_variance_in_band.values()),
        default=0.0)

    # Per-axis marginals + F x CLEANUP_MECHANISM interaction (primary FULL disc.)
    per_axis_marginals: Dict[str, Dict[str, Any]] = {}
    per_axis_marginals_in_band: Dict[str, Dict[str, Any]] = {}
    axes = [("cleanup_mechanism", mech_grid), ("F", F_grid),
            ("M", M_grid), ("N", N_grid), ("corruption", corr_grid)]
    for axis_name, axis_vals in axes:
        axis_marg = {}
        axis_marg_in_band = {}
        for v in axis_vals:
            if axis_name == "corruption":
                matches = [p["acc"] for p in main_pts
                           if abs(p[axis_name] - v) < 1e-6]
                matches_ib = [p["acc"] for p in in_band_pts
                              if abs(p[axis_name] - v) < 1e-6]
            else:
                matches = [p["acc"] for p in main_pts if p[axis_name] == v]
                matches_ib = [p["acc"] for p in in_band_pts if p[axis_name] == v]
            if matches:
                axis_marg[str(v)] = {
                    "mean_acc": round(float(np.mean(matches)), 4),
                    "std_acc": round(float(np.std(matches)), 4),
                    "n": len(matches),
                }
            if matches_ib:
                axis_marg_in_band[str(v)] = {
                    "mean_acc": round(float(np.mean(matches_ib)), 4),
                    "std_acc": round(float(np.std(matches_ib)), 4),
                    "n": len(matches_ib),
                }
        per_axis_marginals[axis_name] = axis_marg
        per_axis_marginals_in_band[axis_name] = axis_marg_in_band

    grand_mean = float(np.mean([p["acc"] for p in main_pts])) if main_pts else 0.0
    grand_mean_in_band = (float(np.mean([p["acc"] for p in in_band_pts]))
                          if in_band_pts else 0.0)

    axis_pair_interactions: Dict[str, Any] = {}
    axis_pair_interactions_in_band: Dict[str, Any] = {}
    for i, (a1_name, a1_vals) in enumerate(axes):
        for j, (a2_name, a2_vals) in enumerate(axes):
            if i >= j:
                continue
            interaction_map = {}
            interaction_map_ib = {}
            max_abs_dev = 0.0
            max_abs_dev_ib = 0.0
            for v1 in a1_vals:
                for v2 in a2_vals:
                    def _match(p, an, v):
                        if an == "corruption":
                            return abs(p[an] - v) < 1e-6
                        return p[an] == v
                    matches = [p["acc"] for p in main_pts
                               if _match(p, a1_name, v1) and _match(p, a2_name, v2)]
                    matches_ib = [p["acc"] for p in in_band_pts
                                  if _match(p, a1_name, v1) and _match(p, a2_name, v2)]
                    if matches:
                        cell_mean = float(np.mean(matches))
                        m1 = per_axis_marginals[a1_name].get(str(v1), {}).get("mean_acc", grand_mean)
                        m2 = per_axis_marginals[a2_name].get(str(v2), {}).get("mean_acc", grand_mean)
                        additive_pred = m1 + m2 - grand_mean
                        dev = cell_mean - additive_pred
                        interaction_map[f"{v1}_{v2}"] = round(dev, 4)
                        max_abs_dev = max(max_abs_dev, abs(dev))
                    if matches_ib:
                        cell_mean_ib = float(np.mean(matches_ib))
                        m1_ib = per_axis_marginals_in_band[a1_name].get(
                            str(v1), {}).get("mean_acc", grand_mean_in_band)
                        m2_ib = per_axis_marginals_in_band[a2_name].get(
                            str(v2), {}).get("mean_acc", grand_mean_in_band)
                        additive_pred_ib = m1_ib + m2_ib - grand_mean_in_band
                        dev_ib = cell_mean_ib - additive_pred_ib
                        interaction_map_ib[f"{v1}_{v2}"] = round(dev_ib, 4)
                        max_abs_dev_ib = max(max_abs_dev_ib, abs(dev_ib))
            if interaction_map:
                axis_pair_interactions[f"{a1_name}_x_{a2_name}"] = {
                    "max_abs_deviation": round(max_abs_dev, 4),
                    "deviation_map": interaction_map,
                }
            if interaction_map_ib:
                axis_pair_interactions_in_band[f"{a1_name}_x_{a2_name}"] = {
                    "max_abs_deviation_in_band": round(max_abs_dev_ib, 4),
                    "deviation_map_in_band": interaction_map_ib,
                }

    # Primary FULL discriminator: F x cleanup_mechanism interaction (in-band-restricted)
    F_x_cleanup_dev = axis_pair_interactions.get(
        "cleanup_mechanism_x_F", {}).get("max_abs_deviation", 0.0)
    F_x_cleanup_dev_in_band = axis_pair_interactions_in_band.get(
        "cleanup_mechanism_x_F", {}).get("max_abs_deviation_in_band", 0.0)

    # H3 crossover check: does mech-ranking change across F within band?
    mech_ranking_by_F_in_band = {}
    for F in F_grid:
        pts_at_F_in_band = [p for p in in_band_pts if p["F"] == F]
        if pts_at_F_in_band:
            mech_means = {}
            for mech in mech_grid:
                accs = [p["acc"] for p in pts_at_F_in_band
                        if p["cleanup_mechanism"] == mech]
                if accs:
                    mech_means[mech] = float(np.mean(accs))
            # Rank mechs by mean_acc (highest first)
            if mech_means:
                ranking = tuple(sorted(mech_means, key=lambda m: -mech_means[m]))
                mech_ranking_by_F_in_band[str(F)] = {
                    "ranking": ranking,
                    "means": {m: round(v, 4) for m, v in mech_means.items()},
                }
    rankings = [v["ranking"] for v in mech_ranking_by_F_in_band.values()]
    mech_ranking_crossover = len(set(rankings)) > 1 if rankings else False

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
        "saturation_pc_result": {
            "regime": SATURATION_PC_REGIME,
            "acc": sat_pc_acc,
            "threshold": SATURATION_PC_THRESHOLD,
            "pass": sat_pc_pass,
        },
        "main_grid_mean_acc": round(main_grid_mean_acc, 4),
        "main_grid_min_acc": round(main_grid_min_acc, 4),
        "main_grid_max_acc": round(main_grid_max_acc, 4),
        "escapes_saturation_ceiling": escapes_saturation_ceiling,
        "in_band_fraction": round(in_band_frac, 4),
        "in_band_n": len(in_band_pts),
        "non_saturated_band": [NON_SAT_BAND_LO, NON_SAT_BAND_HI],
        "per_F_mech_variance": per_F_mech_variance,
        "per_F_mech_variance_in_band": per_F_mech_variance_in_band,
        "max_per_F_mech_variance": round(max_per_F_variance, 4),
        "max_per_F_mech_variance_in_band": round(max_per_F_variance_in_band, 4),
        "per_axis_marginals": per_axis_marginals,
        "per_axis_marginals_in_band": per_axis_marginals_in_band,
        "grand_mean_sharded": round(grand_mean, 4),
        "grand_mean_sharded_in_band": round(grand_mean_in_band, 4),
        "axis_pair_interactions": axis_pair_interactions,
        "axis_pair_interactions_in_band": axis_pair_interactions_in_band,
        "F_x_cleanup_max_abs_deviation": round(F_x_cleanup_dev, 4),
        "F_x_cleanup_max_abs_deviation_in_band": round(F_x_cleanup_dev_in_band, 4),
        "mech_ranking_by_F_in_band": mech_ranking_by_F_in_band,
        "mech_ranking_crossover": mech_ranking_crossover,
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
        return False, (f"mechanisms_collapse: {n_distinct_mechs}/"
                       f"{len(CLEANUP_MECHANISMS)} distinct output hashes")
    sat_pc = body.get("saturation_pc_result", {})
    if not sat_pc.get("pass"):
        return False, (f"saturation_pc_fail: SHARDED F=1 M=800 N=2048 corr=0.20 "
                       f"iterative_cosine acc={sat_pc.get('acc')} < "
                       f"threshold={sat_pc.get('threshold')}")
    mean_acc = body.get("main_grid_mean_acc", 1.0)
    if not body.get("escapes_saturation_ceiling"):
        return False, (f"escapes_saturation_ceiling_fail: main-grid mean_acc="
                       f"{mean_acc:.4f} >= 0.95; smoke regime is at ceiling, "
                       f"not the non-saturated regime we designed for; "
                       f"re-spec grid to higher corr or higher M")

    # Discriminator-firing is NOT a smoke gate per null-hypothesis-SMOKE discipline
    # (feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03).
    max_per_F_var_ib = body.get("max_per_F_mech_variance_in_band", 0.0)
    return True, (f"smoke_gate_pass: cardinality_ok + 3-mech-distinct + "
                  f"saturation_pc_pass={sat_pc.get('acc'):.4f} + "
                  f"escapes_saturation_ceiling(mean_acc={mean_acc:.4f}<0.95) + "
                  f"informational_max_per_F_mech_var_in_band={max_per_F_var_ib:.4f}")


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]], run_mode: str
                          ) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "HARD_FAIL",
                "verdict_msg": "HARD_FAIL_NO_SEEDS",
                "summary": "HARD_FAIL_NO_SEEDS",
                "elapsed_s": 0.0}
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
        "saturation_pc_result": body.get("saturation_pc_result"),
        "main_grid_mean_acc": body.get("main_grid_mean_acc"),
        "main_grid_min_acc": body.get("main_grid_min_acc"),
        "main_grid_max_acc": body.get("main_grid_max_acc"),
        "escapes_saturation_ceiling": body.get("escapes_saturation_ceiling"),
        "in_band_fraction": body.get("in_band_fraction"),
        "in_band_n": body.get("in_band_n"),
        "non_saturated_band": body.get("non_saturated_band"),
        "per_F_mech_variance": body.get("per_F_mech_variance"),
        "per_F_mech_variance_in_band": body.get("per_F_mech_variance_in_band"),
        "max_per_F_mech_variance": body.get("max_per_F_mech_variance"),
        "max_per_F_mech_variance_in_band": body.get("max_per_F_mech_variance_in_band"),
        "per_axis_marginals": body.get("per_axis_marginals"),
        "per_axis_marginals_in_band": body.get("per_axis_marginals_in_band"),
        "grand_mean_sharded": body.get("grand_mean_sharded"),
        "grand_mean_sharded_in_band": body.get("grand_mean_sharded_in_band"),
        "axis_pair_interactions": body.get("axis_pair_interactions"),
        "axis_pair_interactions_in_band": body.get("axis_pair_interactions_in_band"),
        "F_x_cleanup_max_abs_deviation": body.get("F_x_cleanup_max_abs_deviation"),
        "F_x_cleanup_max_abs_deviation_in_band": body.get(
            "F_x_cleanup_max_abs_deviation_in_band"),
        "mech_ranking_by_F_in_band": body.get("mech_ranking_by_F_in_band"),
        "mech_ranking_crossover": body.get("mech_ranking_crossover"),
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
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH: expected={expected_n} "
                f"observed={observed_n}")
    elif not body.get("saturation_pc_result", {}).get("pass"):
        sat = body.get("saturation_pc_result", {})
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_SATURATION_PC_MISMATCH: SHARDED F=1 M=800 N=2048 "
                f"corr=0.20 iterative_cosine acc={sat.get('acc')} < "
                f"threshold={sat.get('threshold')}; primitive-invocation "
                f"broken vs Probe 3 baseline")
    else:
        in_band_frac = body.get("in_band_fraction", 0.0)
        if in_band_frac < 0.30:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_ESCAPES_SATURATION_FAIL: "
                    f"in_band_frac={in_band_frac:.3f} < 0.30; FULL grid failed "
                    f"to escape saturation ceiling; cannot claim H1 or H2 with "
                    f"confidence; regime re-spec needed (higher corr / higher M)")
        else:
            F_x_clean_ib = body.get("F_x_cleanup_max_abs_deviation_in_band", 0.0)
            max_per_F_ib = body.get("max_per_F_mech_variance_in_band", 0.0)
            crossover = body.get("mech_ranking_crossover", False)
            if F_x_clean_ib < 0.05 and max_per_F_ib < 0.05:
                verdict = "HARD_PASS"
                vmsg = (f"HARD_PASS_H2_MECHANISM_DEGENERACY_HOLDS_AT_NON_SATURATED: "
                        f"F_x_cleanup_max_abs_dev_in_band={F_x_clean_ib:.4f} < 0.05 "
                        f"AND max_per_F_mech_var_in_band={max_per_F_ib:.4f} < 0.05 "
                        f"at in_band_frac={in_band_frac:.3f}; Probe 3 null result "
                        f"reproduces at NON-SATURATED regime; validates Probe 1 "
                        f"STORAGE-uniquely-moderates thesis; CG_META revival of "
                        f"Probe 3")
            elif F_x_clean_ib >= 0.15 or max_per_F_ib >= 0.10:
                verdict = "HARD_PASS"
                vmsg = (f"HARD_PASS_H1_TOPOLOGY_MODERATES_WHEN_NON_SATURATED: "
                        f"F_x_cleanup_max_abs_dev_in_band={F_x_clean_ib:.4f} OR "
                        f"max_per_F_mech_var_in_band={max_per_F_ib:.4f}; "
                        f"Probe 3 null was saturation artifact; TOPOLOGY IS a "
                        f"moderator at non-saturated regime; REGIME MAP updated "
                        f"with new boundary point; crossover={crossover}")
            else:
                verdict = "MIDDLE_BAND"
                vmsg = (f"MIDDLE_BAND_WEAK_F_MODERATION: "
                        f"F_x_cleanup_max_abs_dev_in_band={F_x_clean_ib:.4f} "
                        f"in [0.05, 0.15) or max_per_F_mech_var_in_band="
                        f"{max_per_F_ib:.4f} in [0.05, 0.10); weak F-moderation; "
                        f"file as MM_TENTATIVE crossover exponent; "
                        f"crossover={crossover}")

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
    })
    return out


__all__ = [
    "ANCHOR_NAME", "DEVICE", "GPU_NAME",
    "F_GRID_FULL", "F_GRID_SMOKE",
    "M_GRID_FULL", "M_GRID_SMOKE",
    "N_GRID_FULL", "N_GRID_SMOKE",
    "CORRUPTION_GRID_FULL", "CORRUPTION_GRID_SMOKE",
    "L_FIXED", "TR_FULL", "TR_SMOKE",
    "SATURATION_PC_REGIME", "SATURATION_PC_THRESHOLD",
    "NON_SAT_BAND_LO", "NON_SAT_BAND_HI",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "REQUIRED_FIELDS",
    "eval_phase_point", "selftest", "run_one_seed",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
