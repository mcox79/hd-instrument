"""Regime Probe 4 core: STORAGE x N (SCALE_FREE) cross-term.

Cell anchor: `stage1_regime_probe_4_storage_x_N_v1`
Pre-reg: preregs/2026-07-03_stage1_regime_probe_4_storage_x_N_v1.md
Arc: Stage 1 REGIME MAP of 5 CG_META axes (USER 2026-07-03).

Purpose:
    Fourth probe in the Stage 1 Regime Map arc. Probes 1-3 established:
      Probe 1: STORAGE moderates CLEANUP_MECHANISM (mech_var@BUNDLED = 0.103).
      Probe 2: N does NOT moderate CLEANUP_MECHANISM at SHARDED.
      Probe 3: TOPOLOGY does NOT moderate CLEANUP_MECHANISM at SHARDED.
    This probe FIXES CLEANUP_MECHANISM = iterative_cosine and varies STORAGE
    x N. Question: does STORAGE moderate the SCALE_FREE axis? If yes ->
    STORAGE is master moderator (H1). If no -> STORAGE special only for
    MECHANISM (H2). H3 = SCALE_FREE reversal at BUNDLED (surprising).

Hypotheses (falsifiable):
    H1: storage_x_N_max_abs_deviation >= 0.10 AND
        per_storage_N_monotonicity_break_count[BUNDLED] >= 1 AND
        per_storage_N_monotonicity_break_count[SHARDED] == 0
        -> STORAGE is master; SCALE_FREE is SHARDED-only property.
    H2: storage_x_N_max_abs_deviation < 0.05 AND
        both storages monotonic in N
        -> STORAGE special only for MECHANISM.
    H3: bundled_top1(N=16384) < bundled_top1(N=2048) - 0.10 (reversal at
        cliff corr).

Cited source atoms (exact names, no abstraction; META_RULE_AC):
    stage1_regime_map_storage_x_cleanup_v1 (Probe 1)
    stage1_regime_probe_2_N_x_cleanup_mechanism_v1 (Probe 2)
    regime_probe_3_topology_x_cleanup_v1 (Probe 3)
    T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1
    T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1
    sharded_fhrr_capacity_scale_free_extension_N16384_v1_seed_7
    stage1_physics_law_joint_composition_factorial_v1_s11 (source of primitives)

Regime: FHRR chain composition (L=2, F=1 fixed). Mechanism fixed = iterative_cosine.
Primitives imported from `_stage1_physics_law_joint_composition_factorial_v1_core`
(Principle 11 reuse; no re-implementation).

Sweep FULL: 2 storage x 4 N x 3 M x 2 corruption = 48 pts / seed.
Sweep SMOKE: 2 storage x 2 N x 1 M x 1 corruption + 1 SHARDED_PC_easy = 5 pts.

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

ANCHOR_NAME = "stage1_regime_probe_4_storage_x_N_v1"

# ---------------------------------------------------------------------------
# Sweep constants (LOCKED at module init)
# ---------------------------------------------------------------------------
STORAGE_GRID = ("SHARDED", "BUNDLED")

# N axis: 4 levels spanning 3 octaves for SCALE_FREE curve
N_GRID_FULL = [2048, 4096, 8192, 16384]
# SMOKE: 2 levels (2-octave contrast; keeps smoke short)
N_GRID_SMOKE = [2048, 8192]

M_GRID_FULL = [200, 800, 3200]
M_GRID_SMOKE = [800]

CORRUPTION_GRID_FULL = [0.20, 0.45]
CORRUPTION_GRID_SMOKE = [0.45]

# Fixed axes
F_FIXED = 1
L_FIXED = 2
FIXED_MECHANISM = "iterative_cosine"

TR_FULL = 60
TR_SMOKE = 40

# SHARDED_PC_easy positive control point (added to SMOKE only; in FULL it is
# naturally a sweep point).
SHARDED_PC_EASY_REGIME = {
    "cleanup_mechanism": FIXED_MECHANISM,
    "M": 200,
    "N": 4096,
    "F": F_FIXED,
    "L": L_FIXED,
    "corruption": 0.20,
    "storage": "SHARDED",
}

EXPECTED_N_UNITS_FULL = (len(STORAGE_GRID) * len(N_GRID_FULL)
                         * len(M_GRID_FULL) * len(CORRUPTION_GRID_FULL))
# 2 * 4 * 3 * 2 = 48

EXPECTED_N_UNITS_SMOKE = (len(STORAGE_GRID) * len(N_GRID_SMOKE)
                          * len(M_GRID_SMOKE) * len(CORRUPTION_GRID_SMOKE)) + 1
# 2 * 2 * 1 * 1 + 1 (SHARDED_PC_easy) = 5

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
    if EXPECTED_N_UNITS_FULL != 48:
        return False, (f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 48 "
                       f"(2 storage x 4 N x 3 M x 2 corr)")
    if EXPECTED_N_UNITS_SMOKE != 5:
        return False, (f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 5 "
                       f"(4 sweep + 1 SHARDED_PC_easy)")
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. Sanity: SHARDED and BUNDLED at same (M, N, corr, F, L) produce
    # DIFFERENT output hashes (arms_differ across storage axis).
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(999)
    M_props = 50
    N_test = 512
    F = 1
    TR = 20
    props, perms, IMPL, POS, sharded_codebook, bundle_vec = build_rules(
        M_props, F, gen, DEVICE, N_test)

    gen.manual_seed(1013)
    acc_sharded, ci_sharded = run_chain("SHARDED", FIXED_MECHANISM, L=2, F=1, TR=TR,
                                        props=props, perms=perms, IMPL=IMPL,
                                        POS=POS, sharded_codebook=sharded_codebook,
                                        bundle_vec=bundle_vec,
                                        corruption=0.20, gen=gen, device=DEVICE)
    gen.manual_seed(1013)
    acc_bundled, ci_bundled = run_chain("BUNDLED", FIXED_MECHANISM, L=2, F=1, TR=TR,
                                        props=props, perms=perms, IMPL=IMPL,
                                        POS=POS, sharded_codebook=sharded_codebook,
                                        bundle_vec=bundle_vec,
                                        corruption=0.20, gen=gen, device=DEVICE)
    hash_sharded = hashlib.sha256(
        ci_sharded.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    hash_bundled = hashlib.sha256(
        ci_bundled.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    if hash_sharded == hash_bundled:
        return False, (f"SHARDED and BUNDLED produce identical output at "
                       f"M={M_props} N={N_test}: hash={hash_sharded} "
                       f"(storage axis has no effect)")
    msgs.append(f"storage-axis fires: sharded_hash={hash_sharded} "
                f"bundled_hash={hash_bundled} acc_S={acc_sharded:.3f} "
                f"acc_B={acc_bundled:.3f}")

    # 3. Positive-control (Gate D): SHARDED iterative_cosine at F=1 easy regime
    # reproduces prior CG.
    gen.manual_seed(1017)
    props2, perms2, IMPL2, POS2, shard2, bundle2 = build_rules(
        M_props, F, gen, DEVICE, N_test)
    gen.manual_seed(2019)
    acc_easy, _ = run_chain("SHARDED", FIXED_MECHANISM, L=2, F=1, TR=40,
                            props=props2, perms=perms2, IMPL=IMPL2, POS=POS2,
                            sharded_codebook=shard2, bundle_vec=bundle2,
                            corruption=0.05, gen=gen, device=DEVICE)
    if acc_easy < 0.80:
        return False, (f"SHARDED PC easy (M=50, N=512, F=1, L=2, corr=0.05) "
                       f"expected >= 0.80; got {acc_easy:.3f}")
    msgs.append(f"SHARDED PC easy: acc={acc_easy:.3f}")

    # 4. N-axis discriminator sanity: same seed different N -> different
    # sharded_codebook hash (N axis is real).
    gen.manual_seed(3037)
    _, _, _, _, shard_N256, _ = build_rules(M_props, F, gen, DEVICE, 256)
    gen.manual_seed(3037)
    _, _, _, _, shard_N1024, _ = build_rules(M_props, F, gen, DEVICE, 1024)
    hash_N256 = hashlib.sha256(
        shard_N256.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    hash_N1024 = hashlib.sha256(
        shard_N1024.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    if hash_N256 == hash_N1024:
        return False, (f"N=256 and N=1024 sharded codebooks identical "
                       f"(N axis has no effect); hash={hash_N256}")
    msgs.append(f"N-axis fires: N256_hash={hash_N256} N1024_hash={hash_N1024}")

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

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"storage={STORAGE_GRID} N={N_grid} M={M_grid} corr={corr_grid} "
          f"mech={FIXED_MECHANISM} F={F_FIXED} L={L_FIXED} TR={TR} "
          f"expected_n={expected_n}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    salt = 0
    t0 = time.perf_counter()

    # 1) Main factorial grid: 2 STORAGE x len(N) x len(M) x len(corr)
    for storage in STORAGE_GRID:
        for N in N_grid:
            for M_props in M_grid:
                for corr in corr_grid:
                    salt += 1
                    pt = eval_phase_point(FIXED_MECHANISM, M_props, N, F_FIXED,
                                          L_FIXED, corr, storage, TR, seed, salt)
                    phase_map.append(pt)
                    print(f"  [{len(phase_map):3d}/{expected_n:3d}] "
                          f"storage={storage:8s} N={N:5d} M={M_props:5d} "
                          f"c={corr:.2f} acc={pt['acc']:.4f} "
                          f"dt={pt['elapsed_s']:.2f}s", flush=True)

    # 2) SHARDED_PC_easy positive control (SMOKE only; in FULL it's a sweep point)
    if is_smoke:
        salt += 1
        pc_pt = eval_phase_point(SHARDED_PC_EASY_REGIME["cleanup_mechanism"],
                                 SHARDED_PC_EASY_REGIME["M"],
                                 SHARDED_PC_EASY_REGIME["N"],
                                 SHARDED_PC_EASY_REGIME["F"],
                                 SHARDED_PC_EASY_REGIME["L"],
                                 SHARDED_PC_EASY_REGIME["corruption"],
                                 SHARDED_PC_EASY_REGIME["storage"],
                                 TR, seed, salt)
        pc_pt["is_pc_easy"] = True
        phase_map.append(pc_pt)
        print(f"  [{len(phase_map):3d}/{expected_n:3d}] PC_EASY "
              f"storage=SHARDED N={SHARDED_PC_EASY_REGIME['N']} "
              f"M={SHARDED_PC_EASY_REGIME['M']} "
              f"c={SHARDED_PC_EASY_REGIME['corruption']:.2f} "
              f"acc={pc_pt['acc']:.4f}", flush=True)

    elapsed = time.perf_counter() - t0
    observed_n = len(phase_map)
    cardinality_ok = (observed_n == expected_n)

    # ---- arms_differ across STORAGE axis ----
    storage_output_hashes: Dict[str, List[str]] = {s: [] for s in STORAGE_GRID}
    for pt in phase_map:
        if pt.get("is_pc_easy"):
            continue
        storage_output_hashes[pt["storage"]].append(pt["output_hash"])
    storage_hash_agg = {s: hashlib.sha256(
        json.dumps(v, sort_keys=True).encode("utf-8")).hexdigest()[:16]
                        for s, v in storage_output_hashes.items()}
    n_distinct_storages = len(set(storage_hash_agg.values()))

    # ---- PC easy pass (SHARDED at M=200 N=4096 corr=0.20) ----
    # In SMOKE, use the extra PC_easy point. In FULL, query from sweep.
    pc_easy_threshold = 0.90
    if is_smoke:
        pc_easy_matches = [p for p in phase_map if p.get("is_pc_easy")]
    else:
        pc_easy_matches = [p for p in phase_map
                           if not p.get("is_pc_easy")
                           and p["storage"] == "SHARDED"
                           and p["M"] == SHARDED_PC_EASY_REGIME["M"]
                           and p["N"] == SHARDED_PC_EASY_REGIME["N"]
                           and abs(p["corruption"]
                                   - SHARDED_PC_EASY_REGIME["corruption"]) < 1e-6]
    if pc_easy_matches:
        pc_easy_acc = pc_easy_matches[0]["acc"]
        pc_easy_pass = pc_easy_acc >= pc_easy_threshold
    else:
        pc_easy_acc = -1.0
        pc_easy_pass = False

    # ---- Storage gap at BUNDLED-collapse regime (M > 0.14 N) ----
    # In SMOKE at (M=800, N=2048, corr=0.45): M/N = 0.39 (above Plate bound).
    # In FULL, pick same (M=800, N=2048, corr=0.45) point for consistency.
    sg_M = 800
    sg_N = 2048
    sg_corr = max(corr_grid)  # cliff corr (SMOKE=0.45, FULL=0.45)
    sg_sharded = [p for p in phase_map
                  if not p.get("is_pc_easy")
                  and p["storage"] == "SHARDED"
                  and p["M"] == sg_M
                  and p["N"] == sg_N
                  and abs(p["corruption"] - sg_corr) < 1e-6]
    sg_bundled = [p for p in phase_map
                  if not p.get("is_pc_easy")
                  and p["storage"] == "BUNDLED"
                  and p["M"] == sg_M
                  and p["N"] == sg_N
                  and abs(p["corruption"] - sg_corr) < 1e-6]
    if sg_sharded and sg_bundled:
        sg_sharded_acc = sg_sharded[0]["acc"]
        sg_bundled_acc = sg_bundled[0]["acc"]
        storage_gap_at_collapse = round(sg_sharded_acc - sg_bundled_acc, 4)
    else:
        sg_sharded_acc = -1.0
        sg_bundled_acc = -1.0
        storage_gap_at_collapse = -999.0

    # ---- Per-storage per-N SCALE_FREE curve (accuracy pooled over M and corr) ----
    per_storage_N_curve: Dict[str, Dict[str, Any]] = {}
    for storage in STORAGE_GRID:
        per_N_stats: Dict[int, Dict[str, float]] = {}
        for N in N_grid:
            accs = [p["acc"] for p in phase_map
                    if not p.get("is_pc_easy")
                    and p["storage"] == storage
                    and p["N"] == N]
            if accs:
                per_N_stats[N] = {
                    "mean_acc": round(float(np.mean(accs)), 4),
                    "std_acc": round(float(np.std(accs)), 4),
                    "n": len(accs),
                }
        # monotonicity: count breaks (top1 drops > 0.05 as N grows)
        # in cliff-corr sub-slice (harder discriminator regime)
        cliff_corr = max(corr_grid)
        per_N_cliff: Dict[int, float] = {}
        for N in N_grid:
            cliff_accs = [p["acc"] for p in phase_map
                          if not p.get("is_pc_easy")
                          and p["storage"] == storage
                          and p["N"] == N
                          and abs(p["corruption"] - cliff_corr) < 1e-6]
            if cliff_accs:
                per_N_cliff[N] = round(float(np.mean(cliff_accs)), 4)
        break_count = 0
        prev_acc = None
        sorted_Ns = sorted(per_N_cliff.keys())
        for N in sorted_Ns:
            cur_acc = per_N_cliff[N]
            if prev_acc is not None:
                if cur_acc - prev_acc < -0.05:
                    break_count += 1
            prev_acc = cur_acc
        # Reversal check for H3: bundled at max_N vs min_N at cliff corr
        reversal_gap = 0.0
        if len(sorted_Ns) >= 2:
            reversal_gap = round(per_N_cliff[sorted_Ns[-1]]
                                  - per_N_cliff[sorted_Ns[0]], 4)
        per_storage_N_curve[storage] = {
            "per_N_pooled_stats": per_N_stats,
            "per_N_cliff_corr_mean": per_N_cliff,
            "cliff_corr": cliff_corr,
            "monotonicity_break_count": break_count,
            "reversal_gap_max_N_minus_min_N": reversal_gap,
        }

    # ---- STORAGE x N interaction ANOVA deviation ----
    # (cell mean - additive prediction from marginals)
    sweep_pts = [p for p in phase_map if not p.get("is_pc_easy")]
    per_axis_marginals: Dict[str, Dict[str, Any]] = {}
    for axis_name, axis_vals in [
        ("storage", list(STORAGE_GRID)),
        ("N", N_grid),
        ("M", M_grid),
        ("corruption", corr_grid),
    ]:
        axis_marg = {}
        for v in axis_vals:
            if axis_name == "corruption":
                matches = [p["acc"] for p in sweep_pts if abs(p[axis_name] - v) < 1e-6]
            else:
                matches = [p["acc"] for p in sweep_pts if p[axis_name] == v]
            if matches:
                axis_marg[str(v)] = {
                    "mean_acc": round(float(np.mean(matches)), 4),
                    "std_acc": round(float(np.std(matches)), 4),
                    "n": len(matches),
                }
        per_axis_marginals[axis_name] = axis_marg

    grand_mean = float(np.mean([p["acc"] for p in sweep_pts])) if sweep_pts else 0.0

    # STORAGE x N interaction deviation map
    storage_N_interaction: Dict[str, Any] = {}
    max_abs_dev = 0.0
    for storage in STORAGE_GRID:
        for N in N_grid:
            matches = [p["acc"] for p in sweep_pts
                       if p["storage"] == storage and p["N"] == N]
            if not matches:
                continue
            cell_mean = float(np.mean(matches))
            m_storage = per_axis_marginals["storage"].get(str(storage), {}).get(
                "mean_acc", grand_mean)
            m_N = per_axis_marginals["N"].get(str(N), {}).get("mean_acc", grand_mean)
            additive_pred = m_storage + m_N - grand_mean
            dev = cell_mean - additive_pred
            storage_N_interaction[f"{storage}_{N}"] = {
                "cell_mean": round(cell_mean, 4),
                "additive_pred": round(additive_pred, 4),
                "deviation": round(dev, 4),
                "n": len(matches),
            }
            if abs(dev) > max_abs_dev:
                max_abs_dev = abs(dev)

    # ---- Peak memory ----
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
        "storage_output_hash_agg": storage_hash_agg,
        "n_distinct_storages": n_distinct_storages,
        "pc_easy_result": {
            "regime": SHARDED_PC_EASY_REGIME,
            "acc": pc_easy_acc,
            "threshold": pc_easy_threshold,
            "pass": pc_easy_pass,
        },
        "storage_gap_at_collapse_regime": {
            "regime": {"M": sg_M, "N": sg_N, "corruption": sg_corr,
                       "F": F_FIXED, "L": L_FIXED, "mechanism": FIXED_MECHANISM},
            "sharded_acc": sg_sharded_acc,
            "bundled_acc": sg_bundled_acc,
            "storage_gap": storage_gap_at_collapse,
        },
        "per_storage_N_curve": per_storage_N_curve,
        "per_axis_marginals": per_axis_marginals,
        "grand_mean_sweep": round(grand_mean, 4),
        "storage_N_interaction": storage_N_interaction,
        "storage_x_N_max_abs_deviation": round(max_abs_dev, 4),
        "avg_peak_mem_mb": round(avg_peak, 1),
        "elapsed_seed_s": round(elapsed, 2),
        "beta": BETA,
        "alpha_soft": ALPHA_SOFT,
        "fixed_mechanism": FIXED_MECHANISM,
    }


# ---------------------------------------------------------------------------
# Smoke-gate predicate (per null-hypothesis discipline: does NOT gate on
# discriminator firing; only on plumbing + positive controls)
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    phase_map = body.get("phase_map", [])
    if len(phase_map) != body.get("expected_n_units"):
        return False, (f"cardinality_breach: expected {body.get('expected_n_units')} "
                       f"got {len(phase_map)}")
    n_distinct_storages = body.get("n_distinct_storages", 0)
    if n_distinct_storages != len(STORAGE_GRID):
        return False, (f"storages_collapse: {n_distinct_storages}/"
                       f"{len(STORAGE_GRID)} distinct output-hash aggregates "
                       f"(SHARDED and BUNDLED produce identical sweep outputs)")
    pc_easy = body.get("pc_easy_result", {})
    if not pc_easy.get("pass"):
        return False, (f"pc_easy_fail: SHARDED PC easy acc={pc_easy.get('acc')} "
                       f"< threshold={pc_easy.get('threshold')}")
    sg = body.get("storage_gap_at_collapse_regime", {})
    storage_gap = sg.get("storage_gap", 0.0)
    if storage_gap < 0.30:
        return False, (f"storage_gap_fail: gap={storage_gap:.3f} at "
                       f"BUNDLED-collapse regime (M/N=0.39 above Plate bound); "
                       f"expected >= 0.30 (arms don't differentiate)")

    # Informational (does NOT gate; per null-hypothesis discipline).
    # Preview of STORAGE x N interaction from smoke sweep.
    per_curve = body.get("per_storage_N_curve", {})
    sharded_cliff = per_curve.get("SHARDED", {}).get("per_N_cliff_corr_mean", {})
    bundled_cliff = per_curve.get("BUNDLED", {}).get("per_N_cliff_corr_mean", {})
    Ns_S = sorted(sharded_cliff.keys()) if sharded_cliff else []
    Ns_B = sorted(bundled_cliff.keys()) if bundled_cliff else []
    if len(Ns_S) >= 2 and len(Ns_B) >= 2:
        sharded_delta_N = sharded_cliff[Ns_S[-1]] - sharded_cliff[Ns_S[0]]
        bundled_delta_N = bundled_cliff[Ns_B[-1]] - bundled_cliff[Ns_B[0]]
        preview_note = (f"SHARDED_delta_N={sharded_delta_N:+.4f} "
                        f"BUNDLED_delta_N={bundled_delta_N:+.4f}")
    else:
        preview_note = "N-curve preview unavailable"
    max_abs_dev = body.get("storage_x_N_max_abs_deviation", 0.0)

    return True, (f"smoke_gate_pass: cardinality_ok + 2-storage-distinct + "
                  f"pc_easy_acc={pc_easy.get('acc'):.4f} + "
                  f"storage_gap_at_collapse={storage_gap:.3f} | "
                  f"INFO: storage_x_N_max_abs_dev_smoke={max_abs_dev:.4f} | "
                  f"{preview_note}")


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
        "storage_output_hash_agg": body.get("storage_output_hash_agg"),
        "n_distinct_storages": body.get("n_distinct_storages"),
        "pc_easy_result": body.get("pc_easy_result"),
        "storage_gap_at_collapse_regime": body.get("storage_gap_at_collapse_regime"),
        "per_storage_N_curve": body.get("per_storage_N_curve"),
        "per_axis_marginals": body.get("per_axis_marginals"),
        "grand_mean_sweep": body.get("grand_mean_sweep"),
        "storage_N_interaction": body.get("storage_N_interaction"),
        "storage_x_N_max_abs_deviation": body.get("storage_x_N_max_abs_deviation"),
        "device": body.get("device"),
        "gpu_name": body.get("gpu_name"),
        "avg_peak_mem_mb": body.get("avg_peak_mem_mb"),
        "elapsed_seed_s": body.get("elapsed_seed_s"),
        "run_mode": run_mode,
        "fixed_mechanism": body.get("fixed_mechanism"),
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
    elif not body.get("pc_easy_result", {}).get("pass"):
        pc = body.get("pc_easy_result", {})
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_PC_EASY: SHARDED PC easy acc="
                f"{pc.get('acc')} < threshold={pc.get('threshold')}")
    elif body.get("storage_gap_at_collapse_regime", {}).get("storage_gap", 0.0) < 0.20:
        sg = body.get("storage_gap_at_collapse_regime", {})
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_STORAGE_ARM_BROKEN: storage_gap="
                f"{sg.get('storage_gap')} at collapse regime < 0.20")
    else:
        max_abs_dev = body.get("storage_x_N_max_abs_deviation", 0.0)
        curve = body.get("per_storage_N_curve", {})
        sharded_breaks = curve.get("SHARDED", {}).get("monotonicity_break_count", 0)
        bundled_breaks = curve.get("BUNDLED", {}).get("monotonicity_break_count", 0)
        bundled_reversal = curve.get("BUNDLED", {}).get(
            "reversal_gap_max_N_minus_min_N", 0.0)

        # H3 check first (surprising)
        if bundled_reversal < -0.10:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H3_BUNDLED_SCALE_FREE_REVERSAL: "
                    f"bundled(N=max) - bundled(N=min) at cliff corr = "
                    f"{bundled_reversal:.4f} < -0.10; larger N gives WORSE "
                    f"BUNDLED top1; noise-vs-signal interacts adversely with N; "
                    f"storage_x_N_max_abs_dev={max_abs_dev:.4f}")
        elif (max_abs_dev >= 0.10 and bundled_breaks >= 1 and sharded_breaks == 0):
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H1_STORAGE_MASTER_MODERATOR_SCALE_FREE_BREAKS_AT_BUNDLED: "
                    f"storage_x_N_max_abs_dev={max_abs_dev:.4f} >= 0.10 AND "
                    f"BUNDLED breaks={bundled_breaks} >= 1 AND "
                    f"SHARDED breaks={sharded_breaks} == 0; STORAGE is master; "
                    f"SCALE_FREE is a SHARDED-only property")
        elif (max_abs_dev < 0.05
              and sharded_breaks == 0 and bundled_breaks == 0):
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H2_STORAGE_SPECIAL_ONLY_FOR_MECHANISM: "
                    f"storage_x_N_max_abs_dev={max_abs_dev:.4f} < 0.05 AND "
                    f"both storages monotonic in N (S_breaks={sharded_breaks} "
                    f"B_breaks={bundled_breaks}); STORAGE moderator specific to "
                    f"CLEANUP_MECHANISM axis; SCALE_FREE extends across storage")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_INTERMEDIATE_STORAGE_x_N: "
                    f"storage_x_N_max_abs_dev={max_abs_dev:.4f} "
                    f"(H1 needs >=0.10, H2 needs <0.05); "
                    f"SHARDED_breaks={sharded_breaks} BUNDLED_breaks={bundled_breaks} "
                    f"bundled_reversal={bundled_reversal:.4f}; weak "
                    f"STORAGE x N moderation; file as MM_TENTATIVE crossover")

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
    })
    return out


__all__ = [
    "ANCHOR_NAME", "DEVICE", "GPU_NAME",
    "STORAGE_GRID", "N_GRID_FULL", "N_GRID_SMOKE",
    "M_GRID_FULL", "M_GRID_SMOKE",
    "CORRUPTION_GRID_FULL", "CORRUPTION_GRID_SMOKE",
    "F_FIXED", "L_FIXED", "TR_FULL", "TR_SMOKE",
    "FIXED_MECHANISM", "SHARDED_PC_EASY_REGIME",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "REQUIRED_FIELDS",
    "eval_phase_point", "selftest", "run_one_seed",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
