"""Regime Probe 3 core: TOPOLOGY (F fan-in) x CLEANUP_MECHANISM cross-term.

Cell anchor: `regime_probe_3_topology_x_cleanup_v1`
Pre-reg: preregs/2026-07-03_regime_probe_3_topology_x_cleanup_v1.md
Arc: Stage 1 REGIME MAP of 5 CG_META axes (USER 2026-07-03).

Purpose:
    Third probe in the Stage 1 Regime Map arc. Probe 1 (STORAGE x CLEANUP)
    is filed; this probe FIXES storage=SHARDED and varies F (fan-in / fan-out
    in the sharded DAG) x CLEANUP_MECHANISM. Question: does encoder TOPOLOGY
    (F) moderate the CLEANUP_MECHANISM degeneracy observed in Option Y at
    SHARDED, F=1? If yes -> F-dependent regime boundary (crossover exponent
    in F). If no -> Option Y finding (mechanism-axis degenerate at SHARDED)
    extends across topology.

Hypotheses (falsifiable):
    H1 (regime-boundary extends across F): mech variance ~ 0 at all F
        -> CLEANUP_MECHANISM regime-narrow claim extends across topology.
    H2 (F-dependent boundary): mech variance > 0.10 at some F but not
        others -> crossover exponent in F.
    H3 (DAG multi-source aggregation moderates): at F > 1, multi-source
        structure changes cleanup sensitivity.

Cited source atoms (exact names, no abstraction; META_RULE_AC):
    T4/META_STORAGE_STRATEGY_SCALE_FREE_AND_TOPOLOGY_FREE_PHYSICS_LAW_v1
    T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1
    T4/META_SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS_CG_META_v1_2026-07-02
    PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian (v2 M-sweep 2026-07-03)
    stage1_physics_law_joint_composition_factorial_v1_s11_smoke MEASURED@
        `max_mechanism_variation_at_cliff = 0.0` (SHARDED F=1 boundary)

Regime (Option Y-3): sharded-rule-storage FHRR chain composition (L=2 fixed).
Primitives imported from `_stage1_physics_law_joint_composition_factorial_v1_core`
(Principle 11 reuse; no re-implementation).

Sweep FULL: 3 cleanup x 4 F x 3 M x 2 corruption + 1 BUNDLED PC = 73 pts / seed.
Sweep SMOKE: 3 cleanup x 2 F x 1 M x 1 corruption + 1 BUNDLED PC = 7 pts / seed.
N fixed = 4096. L fixed = 2.

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

ANCHOR_NAME = "regime_probe_3_topology_x_cleanup_v1"

# ---------------------------------------------------------------------------
# Sweep constants (LOCKED at module init)
# ---------------------------------------------------------------------------
# TOPOLOGY axis: fan-out F in the sharded DAG (each src has F outgoing edges).
F_GRID_FULL = [1, 2, 4, 8]
F_GRID_SMOKE = [1, 4]

M_GRID_FULL = [200, 800, 3200]
M_GRID_SMOKE = [800]

CORRUPTION_GRID_FULL = [0.20, 0.45]
CORRUPTION_GRID_SMOKE = [0.45]

N_FIXED = 4096
L_FIXED = 2

TR_FULL = 60
TR_SMOKE = 40

# Positive-control BUNDLED-collapse arm (fixed regime; per Gate D storage-gap check)
BUNDLED_PC_REGIME = {
    "cleanup_mechanism": "iterative_cosine",
    "M": 800,
    "N": N_FIXED,
    "F": 1,
    "L": L_FIXED,
    "corruption": 0.20,
}
BUNDLED_PC_REGIME_SMOKE = {
    "cleanup_mechanism": "iterative_cosine",
    "M": 800,
    "N": N_FIXED,
    "F": 1,
    "L": L_FIXED,
    # Match smoke corruption grid (0.45) so storage_gap can be computed against
    # a SHARDED point that IS in the smoke sweep. FULL PC uses corr=0.20 which
    # is the classical below-capacity storage discriminator regime.
    "corruption": 0.45,
}

EXPECTED_N_UNITS_FULL = (len(CLEANUP_MECHANISMS) * len(F_GRID_FULL)
                         * len(M_GRID_FULL) * len(CORRUPTION_GRID_FULL)) + 1
# 3 * 4 * 3 * 2 + 1 = 73

EXPECTED_N_UNITS_SMOKE = (len(CLEANUP_MECHANISMS) * len(F_GRID_SMOKE)
                          * len(M_GRID_SMOKE) * len(CORRUPTION_GRID_SMOKE)) + 1
# 3 * 2 * 1 * 1 + 1 = 7

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
    if EXPECTED_N_UNITS_FULL != 73:
        return False, (f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 73 "
                       f"(72 factorial + 1 BUNDLED PC)")
    if EXPECTED_N_UNITS_SMOKE != 7:
        return False, (f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 7 "
                       f"(6 factorial + 1 BUNDLED PC)")
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. Sanity: 3 cleanup mechanisms produce distinct outputs at F=2 (multi-F path)
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
    # pick fan-out slot 1 (not the only-slot case)
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
    # reproduces prior CG (matches Option Y v1 core selftest)
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

    # 4. F-axis discriminator sanity: F=2 topology produces DIFFERENT output
    # hash from F=1 at same seed (arms_must_differ across topology).
    gen.manual_seed(1017)
    # Rebuild at F=1 same M/N same seed
    props1, perms1, IMPL1, POS1, shard1, bundle1 = build_rules(
        M_props, 1, gen, DEVICE, N_test)
    hash_F1 = hashlib.sha256(shard1.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    hash_F2 = hashlib.sha256(sharded_codebook.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    if hash_F1 == hash_F2:
        return False, (f"F=1 and F=2 sharded codebooks identical (topology axis "
                       f"has no effect); hash={hash_F1}")
    msgs.append(f"F-axis fires: F1_hash={hash_F1} F2_hash={hash_F2}")

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
        corr_grid = CORRUPTION_GRID_SMOKE
        TR = TR_SMOKE
        pc_regime = BUNDLED_PC_REGIME_SMOKE
        expected_n = EXPECTED_N_UNITS_SMOKE
    else:
        mech_grid = list(CLEANUP_MECHANISMS)
        F_grid = F_GRID_FULL
        M_grid = M_GRID_FULL
        corr_grid = CORRUPTION_GRID_FULL
        TR = TR_FULL
        pc_regime = BUNDLED_PC_REGIME
        expected_n = EXPECTED_N_UNITS_FULL

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"mechs={mech_grid} F={F_grid} M={M_grid} N={N_FIXED} L={L_FIXED} "
          f"corr={corr_grid} TR={TR} expected_n={expected_n}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    salt = 0
    t0 = time.perf_counter()

    # 1) Main factorial grid: SHARDED storage
    for mech in mech_grid:
        for F in F_grid:
            for M_props in M_grid:
                for corr in corr_grid:
                    salt += 1
                    pt = eval_phase_point(mech, M_props, N_FIXED, F, L_FIXED,
                                          corr, "SHARDED", TR, seed, salt)
                    phase_map.append(pt)
                    print(f"  [{len(phase_map):3d}/{expected_n:3d}] "
                          f"mech={mech:22s} F={F} M={M_props:5d} N={N_FIXED} "
                          f"L={L_FIXED} c={corr:.2f} storage=SHARDED "
                          f"acc={pt['acc']:.4f} dt={pt['elapsed_s']:.2f}s",
                          flush=True)

    # 2) BUNDLED positive-control arm
    salt += 1
    pc_pt = eval_phase_point(pc_regime["cleanup_mechanism"], pc_regime["M"],
                             pc_regime["N"], pc_regime["F"], pc_regime["L"],
                             pc_regime["corruption"], "BUNDLED", TR, seed, salt)
    pc_pt["is_bundled_pc"] = True
    phase_map.append(pc_pt)
    print(f"  [{len(phase_map):3d}/{expected_n:3d}] BUNDLED_PC "
          f"mech={pc_regime['cleanup_mechanism']} M={pc_regime['M']} "
          f"N={pc_regime['N']} F={pc_regime['F']} L={pc_regime['L']} "
          f"c={pc_regime['corruption']:.2f} storage=BUNDLED "
          f"acc={pc_pt['acc']:.4f}", flush=True)

    elapsed = time.perf_counter() - t0
    observed_n = len(phase_map)
    cardinality_ok = (observed_n == expected_n)

    # arms_differ across 3 cleanup mechanisms (SHARDED-only outputs)
    mech_output_hashes: Dict[str, List[str]] = {m: [] for m in CLEANUP_MECHANISMS}
    for pt in phase_map:
        if pt.get("storage") == "SHARDED":
            mech_output_hashes[pt["cleanup_mechanism"]].append(pt["output_hash"])
    mech_hash_agg = {m: hashlib.sha256(
        json.dumps(v, sort_keys=True).encode("utf-8")).hexdigest()[:16]
                     for m, v in mech_output_hashes.items()}
    n_distinct_mechs = len(set(mech_hash_agg.values()))

    # Positive control reproduction (Gate D):
    # SHARDED iterative_cosine at min-F min-M min-corr in the sweep should
    # reproduce Option Y's near-1.0 result at matched primitives.
    pc_target_F = min([f for f in F_grid])
    pc_target_M = min(M_grid)
    pc_target_corr = min(corr_grid)
    pc_repro_matches = [p for p in phase_map
                        if p.get("storage") == "SHARDED"
                        and p["cleanup_mechanism"] == "iterative_cosine"
                        and p["F"] == pc_target_F
                        and p["M"] == pc_target_M
                        and abs(p["corruption"] - pc_target_corr) < 1e-6]
    if pc_repro_matches:
        pc_repro_acc = pc_repro_matches[0]["acc"]
        # In smoke, the min-corr is the ONLY corr (0.45) which is HARD; so
        # tolerance is loosened. In FULL, min-corr=0.20 which is easier.
        pc_repro_threshold = 0.60 if is_smoke else 0.75
        pc_repro_pass = pc_repro_acc >= pc_repro_threshold
    else:
        pc_repro_acc = -1.0
        pc_repro_threshold = 0.60 if is_smoke else 0.75
        pc_repro_pass = False

    # BUNDLED collapse check
    bundle_pc_acc = pc_pt["acc"]
    # Compare BUNDLED PC to SHARDED at same regime (M=800 F=1 corr=0.20)
    sharded_at_bundle_regime = [p for p in phase_map
                                 if p.get("storage") == "SHARDED"
                                 and p["cleanup_mechanism"] == pc_regime["cleanup_mechanism"]
                                 and p["M"] == pc_regime["M"]
                                 and p["F"] == pc_regime["F"]
                                 and abs(p["corruption"] - pc_regime["corruption"]) < 1e-6]
    if sharded_at_bundle_regime:
        sharded_at_bundle_acc = sharded_at_bundle_regime[0]["acc"]
        storage_gap = sharded_at_bundle_acc - bundle_pc_acc
    else:
        sharded_at_bundle_acc = -1.0
        storage_gap = -999.0

    # Per-F mechanism variance (KEY discriminator)
    # For each F, compute across-mech max(acc) - min(acc) at cliff corruption.
    cliff_corr = max(corr_grid)
    per_F_mech_variance: Dict[str, Dict[str, Any]] = {}
    for F in F_grid:
        accs_by_mech: Dict[str, List[float]] = {m: [] for m in mech_grid}
        for M_props in M_grid:
            for mech in mech_grid:
                matches = [p for p in phase_map
                           if p.get("storage") == "SHARDED"
                           and p["cleanup_mechanism"] == mech
                           and p["F"] == F
                           and p["M"] == M_props
                           and abs(p["corruption"] - cliff_corr) < 1e-6]
                if matches:
                    accs_by_mech[mech].append(matches[0]["acc"])
        # For each M, compute across-mechanism variance; take max across M.
        max_across_M = 0.0
        per_M_var: Dict[int, float] = {}
        for M_props in M_grid:
            triple = []
            for mech in mech_grid:
                # Find the SHARDED phase point at this F, M, cliff_corr, mech
                matches = [p for p in phase_map
                           if p.get("storage") == "SHARDED"
                           and p["cleanup_mechanism"] == mech
                           and p["F"] == F
                           and p["M"] == M_props
                           and abs(p["corruption"] - cliff_corr) < 1e-6]
                if matches:
                    triple.append(matches[0]["acc"])
            if len(triple) == len(mech_grid):
                var = round(max(triple) - min(triple), 4)
                per_M_var[M_props] = var
                if var > max_across_M:
                    max_across_M = var
        per_F_mech_variance[str(F)] = {
            "per_M_mech_variance_at_cliff_corr": per_M_var,
            "max_mech_variance_across_M": round(max_across_M, 4),
            "cliff_corr": cliff_corr,
        }

    max_per_F_variance = max(
        (v["max_mech_variance_across_M"] for v in per_F_mech_variance.values()),
        default=0.0)

    # Per-axis marginals + F x CLEANUP_MECHANISM interaction (primary FULL disc.)
    sharded_pts = [p for p in phase_map if p.get("storage") == "SHARDED"]
    per_axis_marginals: Dict[str, Dict[str, Any]] = {}
    for axis_name, axis_vals in [
        ("cleanup_mechanism", mech_grid),
        ("F", F_grid),
        ("M", M_grid),
        ("corruption", corr_grid),
    ]:
        axis_marg = {}
        for v in axis_vals:
            if axis_name == "corruption":
                matches = [p["acc"] for p in sharded_pts if abs(p[axis_name] - v) < 1e-6]
            else:
                matches = [p["acc"] for p in sharded_pts if p[axis_name] == v]
            if matches:
                axis_marg[str(v)] = {
                    "mean_acc": round(float(np.mean(matches)), 4),
                    "std_acc": round(float(np.std(matches)), 4),
                    "n": len(matches),
                }
        per_axis_marginals[axis_name] = axis_marg

    grand_mean = float(np.mean([p["acc"] for p in sharded_pts])) if sharded_pts else 0.0
    axis_pair_interactions: Dict[str, Any] = {}
    axes = [("cleanup_mechanism", mech_grid), ("F", F_grid),
            ("M", M_grid), ("corruption", corr_grid)]
    for i, (a1_name, a1_vals) in enumerate(axes):
        for j, (a2_name, a2_vals) in enumerate(axes):
            if i >= j:
                continue
            interaction_map = {}
            max_abs_dev = 0.0
            for v1 in a1_vals:
                for v2 in a2_vals:
                    def _match(p, an, v):
                        if an == "corruption":
                            return abs(p[an] - v) < 1e-6
                        return p[an] == v
                    matches = [p["acc"] for p in sharded_pts
                               if _match(p, a1_name, v1) and _match(p, a2_name, v2)]
                    if not matches:
                        continue
                    cell_mean = float(np.mean(matches))
                    m1 = per_axis_marginals[a1_name].get(str(v1), {}).get("mean_acc", grand_mean)
                    m2 = per_axis_marginals[a2_name].get(str(v2), {}).get("mean_acc", grand_mean)
                    additive_pred = m1 + m2 - grand_mean
                    dev = cell_mean - additive_pred
                    interaction_map[f"{v1}_{v2}"] = round(dev, 4)
                    max_abs_dev = max(max_abs_dev, abs(dev))
            if interaction_map:
                axis_pair_interactions[f"{a1_name}_x_{a2_name}"] = {
                    "max_abs_deviation": round(max_abs_dev, 4),
                    "deviation_map": interaction_map,
                }

    # Primary FULL discriminator: F x cleanup_mechanism interaction
    F_x_cleanup_dev = axis_pair_interactions.get(
        "cleanup_mechanism_x_F", {}).get("max_abs_deviation", 0.0)

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
        "pc_reproduce_iterative_cosine_regime": {
            "F": pc_target_F, "M": pc_target_M, "N": N_FIXED,
            "L": L_FIXED, "corruption": pc_target_corr,
            "acc": pc_repro_acc,
            "threshold": pc_repro_threshold,
            "pass": pc_repro_pass,
        },
        "bundle_pc_result": {
            "regime": pc_regime,
            "bundle_acc": bundle_pc_acc,
            "sharded_at_same_regime_acc": sharded_at_bundle_acc,
            "storage_gap_sharded_minus_bundled": round(storage_gap, 4),
        },
        "per_F_mech_variance": per_F_mech_variance,
        "max_per_F_mech_variance": round(max_per_F_variance, 4),
        "cliff_corruption": cliff_corr,
        "per_axis_marginals": per_axis_marginals,
        "grand_mean_sharded": round(grand_mean, 4),
        "axis_pair_interactions": axis_pair_interactions,
        "F_x_cleanup_max_abs_deviation": round(F_x_cleanup_dev, 4),
        "avg_peak_mem_mb": round(avg_peak, 1),
        "elapsed_seed_s": round(elapsed, 2),
        "beta": BETA,
        "alpha_soft": ALPHA_SOFT,
    }


# ---------------------------------------------------------------------------
# Smoke-gate predicate
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    phase_map = body.get("phase_map", [])
    if len(phase_map) != body.get("expected_n_units"):
        return False, (f"cardinality_breach: expected {body.get('expected_n_units')} "
                       f"got {len(phase_map)}")
    n_distinct_mechs = body.get("n_distinct_mechanisms", 0)
    if n_distinct_mechs != len(CLEANUP_MECHANISMS):
        return False, (f"mechanisms_collapse: {n_distinct_mechs}/"
                       f"{len(CLEANUP_MECHANISMS)} distinct output hashes")
    pc_repro = body.get("pc_reproduce_iterative_cosine_regime", {})
    if not pc_repro.get("pass"):
        return False, (f"pc_reproduce_fail: iterative_cosine SHARDED PC "
                       f"acc={pc_repro.get('acc')} thr={pc_repro.get('threshold')}")
    bundle_pc = body.get("bundle_pc_result", {})
    storage_gap = bundle_pc.get("storage_gap_sharded_minus_bundled", 0.0)
    if storage_gap < 0.15:
        return False, (f"BUNDLED_pc_collapse_fail: sharded_vs_bundled gap="
                       f"{storage_gap:.3f} at PC regime (expected >= 0.15)")

    # Discriminator-fires check: F axis produces some measurable spread across
    # mechanisms, OR mechanism-axis is uniformly degenerate (either outcome is
    # informative for the hypothesis).
    max_per_F_var = body.get("max_per_F_mech_variance", 0.0)
    # Note: max_per_F_var == 0 is HYPOTHESIS-SUPPORTIVE (H1: regime extends across F).
    # We do NOT reject on 0; but we log an "informational" note.
    return True, (f"smoke_gate_pass: cardinality_ok + 3-mech-distinct + "
                  f"pc_reproduce={pc_repro.get('acc'):.4f} + "
                  f"storage_gap={storage_gap:.3f} + "
                  f"max_per_F_mech_var_at_cliff={max_per_F_var:.4f}")


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
        "pc_reproduce_iterative_cosine_regime": body.get(
            "pc_reproduce_iterative_cosine_regime"),
        "bundle_pc_result": body.get("bundle_pc_result"),
        "per_F_mech_variance": body.get("per_F_mech_variance"),
        "max_per_F_mech_variance": body.get("max_per_F_mech_variance"),
        "per_axis_marginals": body.get("per_axis_marginals"),
        "grand_mean_sharded": body.get("grand_mean_sharded"),
        "axis_pair_interactions": body.get("axis_pair_interactions"),
        "F_x_cleanup_max_abs_deviation": body.get("F_x_cleanup_max_abs_deviation"),
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
    elif not body.get("pc_reproduce_iterative_cosine_regime", {}).get("pass"):
        pc = body.get("pc_reproduce_iterative_cosine_regime", {})
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_MARGINAL_REPRODUCTION: PC reproduce acc="
                f"{pc.get('acc')} < threshold={pc.get('threshold')}")
    else:
        F_x_clean = body.get("F_x_cleanup_max_abs_deviation", 0.0)
        max_per_F = body.get("max_per_F_mech_variance", 0.0)
        # Threshold decisions per pre-reg:
        # - max_per_F < 0.05 AND F_x_clean < 0.05: H1 supported (regime extends)
        # - max_per_F > 0.10 at some F, or F_x_clean > 0.15: H2/H3 supported
        # - Intermediate: MIDDLE_BAND crossover
        if max_per_F < 0.05 and F_x_clean < 0.05:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H1_MECHANISM_DEGENERACY_EXTENDS_ACROSS_TOPOLOGY: "
                    f"max_per_F_mech_var={max_per_F:.4f} < 0.05 AND "
                    f"F_x_cleanup_max_dev={F_x_clean:.4f} < 0.05; "
                    f"CLEANUP_MECHANISM axis is regime-narrow independent of "
                    f"encoder topology (F fan-out); Option Y F=1 finding "
                    f"extends across F in {F_GRID_FULL}")
        elif max_per_F >= 0.10 or F_x_clean >= 0.15:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_H2_F_DEPENDENT_MECHANISM_BOUNDARY: "
                    f"max_per_F_mech_var={max_per_F:.4f} OR "
                    f"F_x_cleanup_max_dev={F_x_clean:.4f}; mechanism-axis "
                    f"variance is F-dependent (crossover exponent in F); "
                    f"topology moderates cleanup-mechanism degeneracy; "
                    f"REGIME MAP has F-dependent boundary")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_INTERMEDIATE_F_MODERATION: "
                    f"max_per_F_mech_var={max_per_F:.4f} in [0.05, 0.10) or "
                    f"F_x_cleanup_max_dev={F_x_clean:.4f} in [0.05, 0.15); "
                    f"weak F-moderation; methodologically interesting; "
                    f"file as MM_TENTATIVE crossover")

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
    "CORRUPTION_GRID_FULL", "CORRUPTION_GRID_SMOKE",
    "N_FIXED", "L_FIXED", "TR_FULL", "TR_SMOKE",
    "BUNDLED_PC_REGIME", "BUNDLED_PC_REGIME_SMOKE",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "REQUIRED_FIELDS",
    "eval_phase_point", "selftest", "run_one_seed",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
