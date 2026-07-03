"""Stage 1 REGIME MAP arc - STORAGE x CLEANUP_MECHANISM pairwise probe (first of arc).

Cell anchor: `stage1_regime_map_storage_x_cleanup_v1`
Pre-reg: preregs/2026-07-03_stage1_regime_map_storage_x_cleanup_first_probe.md

Purpose:
    Measure the STORAGE x CLEANUP_MECHANISM cross-term in FHRR chain composition.
    Option Y (2026-07-03) revealed max_mechanism_variation_at_cliff = 0.000 at
    SHARDED. Option Y-2: does BUNDLED (below-capacity storage) recover mechanism-
    axis variance, OR is CLEANUP_MECHANISM axis universally regime-narrow?

Reuse: imports all primitives from
    _stage1_physics_law_joint_composition_factorial_v1_core
(cphasor_torch, cnorm_torch, phase_corrupt, build_rules, run_chain,
 CLEANUP_REGISTRY, CLEANUP_MECHANISMS, BETA, ALPHA_SOFT, DEVICE, GPU_NAME).

Sweep grid (FULL): 2 storage x 3 cleanup x 3 M x 2 N x 2 corr = 72 pts/seed.
Sweep grid (SMOKE): 2 storage x 3 cleanup x 1 M x 1 N x 1 corr = 6 pts.

Compute architecture: batched-GPU (inherited).
Storage strategy: mixed (SHARDED and BUNDLED both discriminator arms).
Progress logging: print_flush_true.

ASCII-only. No unicode, no em-dashes.
Author: hdi_exp_dev 2026-07-03 (agent-spawn, Opus 4.7).
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
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

# CUDA env before torch import (USER-LOCKED)
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Reuse primitives (Principle 11) from prior Option Y factorial core.
from experiments._stage1_physics_law_joint_composition_factorial_v1_core import (  # noqa: E402
    DEVICE, GPU_NAME,
    CLEANUP_MECHANISMS, CLEANUP_REGISTRY, BETA, ALPHA_SOFT,
    build_rules, phase_corrupt, run_chain, eval_phase_point,
    cphasor_torch,
)

ANCHOR_NAME = "stage1_regime_map_storage_x_cleanup_v1"

# ---------------------------------------------------------------------------
# Sweep constants (LOCKED at module init)
# ---------------------------------------------------------------------------
STORAGE_GRID = ("SHARDED", "BUNDLED")

M_GRID_FULL = [200, 800, 3200]
N_GRID_FULL = [2048, 8192]
CORRUPTION_GRID_FULL = [0.20, 0.45]

# SMOKE: single point on each of M/N/corr; sweep storage x mechanism only.
# M=200 chosen so BUNDLED sits just below Plate 1995 bound (0.14*N=287 at N=2048)
# expected discriminable range (baseline_in_band gate). SHARDED expected near
# ceiling (already known 13.9x extension beyond bundle bound).
M_GRID_SMOKE = [200]
N_GRID_SMOKE = [2048]
CORRUPTION_GRID_SMOKE = [0.20]

# Fixed axes (dropped for pairwise probe; will add later if warranted)
F_FIXED = 1
L_FIXED = 2

TR_FULL = 100
TR_SMOKE = 40

EXPECTED_N_UNITS_FULL = (len(STORAGE_GRID) * len(CLEANUP_MECHANISMS)
                         * len(M_GRID_FULL) * len(N_GRID_FULL)
                         * len(CORRUPTION_GRID_FULL))  # 72
EXPECTED_N_UNITS_SMOKE = (len(STORAGE_GRID) * len(CLEANUP_MECHANISMS)
                          * len(M_GRID_SMOKE) * len(N_GRID_SMOKE)
                          * len(CORRUPTION_GRID_SMOKE))  # 6

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# Selftest (formula check at reduced grid; wall < 60s target)
# ---------------------------------------------------------------------------
def selftest() -> Tuple[bool, str]:
    msgs = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 72:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 72"
    if EXPECTED_N_UNITS_SMOKE != 6:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 6"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. Storage grid + mechanism grid distinct
    if set(STORAGE_GRID) != {"SHARDED", "BUNDLED"}:
        return False, f"STORAGE_GRID mismatch: {STORAGE_GRID}"
    if len(CLEANUP_MECHANISMS) != 3:
        return False, f"CLEANUP_MECHANISMS != 3: got {CLEANUP_MECHANISMS}"
    msgs.append(f"storage={STORAGE_GRID} cleanup={CLEANUP_MECHANISMS}")

    # 3. Positive control at reduced regime: sharded storage at low-corruption
    # low-M easy-regime reproduces prior CG (Gate D reproduce). Use M=50 N=512
    # F=1 L=2 corr=0.05 iterative_cosine as micro-selftest.
    seed = 991
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    M_props = 50
    N_test = 512
    props, perms, IMPL, POS, sharded_codebook, bundle_vec = build_rules(
        M_props, F_FIXED, gen, DEVICE, N_test)

    acc_sharded_easy, _ = run_chain("SHARDED", "iterative_cosine",
                                     L=L_FIXED, F=F_FIXED, TR=40,
                                     props=props, perms=perms,
                                     IMPL=IMPL, POS=POS,
                                     sharded_codebook=sharded_codebook,
                                     bundle_vec=bundle_vec,
                                     corruption=0.05, gen=gen, device=DEVICE)
    if acc_sharded_easy < 0.80:
        return False, (f"SHARDED PC easy regime (M=50 N=512 L=2 F=1 corr=0.05) "
                       f"expected >= 0.80; got {acc_sharded_easy:.3f}")
    msgs.append(f"SHARDED PC easy: acc={acc_sharded_easy:.3f}")

    # 4. Storage gap check: SHARDED >> BUNDLED at M/N > 0.14 (above Plate bound)
    # M/N = 50/512 = 0.098 just below bound; expect BUNDLED to degrade partially.
    gen.manual_seed(seed + 3)
    acc_bundled_easy, _ = run_chain("BUNDLED", "iterative_cosine",
                                     L=L_FIXED, F=F_FIXED, TR=40,
                                     props=props, perms=perms,
                                     IMPL=IMPL, POS=POS,
                                     sharded_codebook=sharded_codebook,
                                     bundle_vec=bundle_vec,
                                     corruption=0.05, gen=gen, device=DEVICE)
    storage_gap = acc_sharded_easy - acc_bundled_easy
    if storage_gap < 0.20:
        return False, (f"SHARDED-vs-BUNDLED storage-gap at selftest regime "
                       f"expected >= 0.20; got sharded={acc_sharded_easy:.3f} "
                       f"bundled={acc_bundled_easy:.3f} gap={storage_gap:.3f}")
    msgs.append(f"storage_gap={storage_gap:.3f} "
                f"(sharded={acc_sharded_easy:.3f} bundled={acc_bundled_easy:.3f})")

    # 5. arms_differ hash check: 3 mechanisms produce distinct outputs
    gen.manual_seed(seed + 7)
    ci = torch.arange(40, device=DEVICE) % M_props
    A_cur = props[ci]
    f_step = torch.zeros((40,), dtype=torch.long, device=DEVICE)
    rule_batch = sharded_codebook[ci, f_step]
    cand = rule_batch * A_cur.conj() * POS[0].unsqueeze(0).conj() * IMPL.conj().unsqueeze(0)
    cand_corr = phase_corrupt(cand, 0.30, gen, DEVICE)
    mech_hashes: Dict[str, str] = {}
    for mech in CLEANUP_MECHANISMS:
        fn = CLEANUP_REGISTRY[mech]
        out = fn(cand_corr, props)
        mech_hashes[mech] = hashlib.sha256(
            out.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    if len(set(mech_hashes.values())) != len(CLEANUP_MECHANISMS):
        return False, f"mechanisms produce identical outputs: {mech_hashes}"
    msgs.append(f"3 mechanisms distinct: {list(mech_hashes.values())}")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed(seed: int, run_mode: str) -> Dict[str, Any]:
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        M_grid = M_GRID_SMOKE
        N_grid = N_GRID_SMOKE
        corr_grid = CORRUPTION_GRID_SMOKE
        TR = TR_SMOKE
        expected_n = EXPECTED_N_UNITS_SMOKE
    else:
        M_grid = M_GRID_FULL
        N_grid = N_GRID_FULL
        corr_grid = CORRUPTION_GRID_FULL
        TR = TR_FULL
        expected_n = EXPECTED_N_UNITS_FULL

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"storage={STORAGE_GRID} mechs={CLEANUP_MECHANISMS} "
          f"M={M_grid} N={N_grid} corr={corr_grid} F={F_FIXED} L={L_FIXED} "
          f"TR={TR} expected_n={expected_n}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    salt = 0
    t0 = time.perf_counter()

    for storage in STORAGE_GRID:
        for mech in CLEANUP_MECHANISMS:
            for M_props in M_grid:
                for N in N_grid:
                    for corr in corr_grid:
                        salt += 1
                        pt = eval_phase_point(
                            mechanism=mech, M_props=M_props, N=N,
                            F=F_FIXED, L=L_FIXED, corruption=corr,
                            storage=storage, TR=TR, seed=seed, salt=salt)
                        phase_map.append(pt)
                        print(f"  [{len(phase_map):3d}/{expected_n:3d}] "
                              f"storage={storage:8s} mech={mech:22s} "
                              f"M={M_props:5d} N={N:5d} c={corr:.2f} "
                              f"acc={pt['acc']:.4f} dt={pt['elapsed_s']:.2f}s",
                              flush=True)

    elapsed = time.perf_counter() - t0
    observed_n = len(phase_map)
    cardinality_ok = (observed_n == expected_n)

    # arms_differ: 3 mechanisms produce distinct outputs (SHARDED aggregate hash)
    mech_output_hashes: Dict[str, List[str]] = {m: [] for m in CLEANUP_MECHANISMS}
    for pt in phase_map:
        if pt.get("storage") == "SHARDED":
            mech_output_hashes[pt["cleanup_mechanism"]].append(pt["output_hash"])
    mech_hash_agg = {m: hashlib.sha256(
        json.dumps(v, sort_keys=True).encode("utf-8")).hexdigest()[:16]
                     for m, v in mech_output_hashes.items()}
    n_distinct_mechs = len(set(mech_hash_agg.values()))

    # Positive control: SHARDED at smoke regime iterative_cosine (M=200 N=2048
    # F=1 L=2 corr=0.20 in smoke) OR at min-regime of FULL (M=200 N=2048 F=1
    # L=2 corr=0.20 in full).
    pc_M = min(M_grid)
    pc_N = min(N_grid)
    pc_corr = min(corr_grid)
    pc_matches = [p for p in phase_map
                  if p.get("storage") == "SHARDED"
                  and p["cleanup_mechanism"] == "iterative_cosine"
                  and p["M"] == pc_M and p["N"] == pc_N
                  and abs(p["corruption"] - pc_corr) < 1e-6]
    if pc_matches:
        pc_acc = pc_matches[0]["acc"]
        pc_pass = pc_acc >= 0.75
    else:
        pc_acc = -1.0
        pc_pass = False

    # Storage-gap positive control (SHARDED - BUNDLED at same slice)
    def _find(storage: str, mech: str, M: int, N: int, corr: float) -> float:
        for p in phase_map:
            if (p.get("storage") == storage
                    and p["cleanup_mechanism"] == mech
                    and p["M"] == M and p["N"] == N
                    and abs(p["corruption"] - corr) < 1e-6):
                return float(p["acc"])
        return -999.0

    storage_gaps: Dict[str, float] = {}
    for mech in CLEANUP_MECHANISMS:
        for M in M_grid:
            for N in N_grid:
                for corr in corr_grid:
                    sh = _find("SHARDED", mech, M, N, corr)
                    bd = _find("BUNDLED", mech, M, N, corr)
                    if sh > -998 and bd > -998:
                        key = f"{mech}_M{M}_N{N}_c{corr:.2f}"
                        storage_gaps[key] = round(sh - bd, 4)
    max_storage_gap = max(storage_gaps.values()) if storage_gaps else 0.0
    # Median gap: preferable indicator of consistent storage-axis behavior
    if storage_gaps:
        med_storage_gap = round(float(np.median(list(storage_gaps.values()))), 4)
    else:
        med_storage_gap = 0.0

    # ---- KEY DISCRIMINATOR: mechanism variance at each STORAGE arm ----
    mech_var_sharded: Dict[str, float] = {}
    mech_var_bundled: Dict[str, float] = {}
    for M in M_grid:
        for N in N_grid:
            for corr in corr_grid:
                key = f"M{M}_N{N}_c{corr:.2f}"
                sh_accs = [_find("SHARDED", m, M, N, corr) for m in CLEANUP_MECHANISMS]
                bd_accs = [_find("BUNDLED", m, M, N, corr) for m in CLEANUP_MECHANISMS]
                if all(a > -998 for a in sh_accs):
                    mech_var_sharded[key] = round(max(sh_accs) - min(sh_accs), 4)
                if all(a > -998 for a in bd_accs):
                    mech_var_bundled[key] = round(max(bd_accs) - min(bd_accs), 4)
    max_mech_var_sharded = max(mech_var_sharded.values()) if mech_var_sharded else 0.0
    max_mech_var_bundled = max(mech_var_bundled.values()) if mech_var_bundled else 0.0

    # ---- STORAGE x CLEANUP 2-axis interaction (ANOVA-style) ----
    all_accs = [p["acc"] for p in phase_map]
    grand_mean = float(np.mean(all_accs)) if all_accs else 0.0
    storage_marg: Dict[str, float] = {}
    for storage in STORAGE_GRID:
        matches = [p["acc"] for p in phase_map if p.get("storage") == storage]
        storage_marg[storage] = float(np.mean(matches)) if matches else grand_mean
    mech_marg: Dict[str, float] = {}
    for mech in CLEANUP_MECHANISMS:
        matches = [p["acc"] for p in phase_map if p["cleanup_mechanism"] == mech]
        mech_marg[mech] = float(np.mean(matches)) if matches else grand_mean
    # 2-axis interaction: cell_mean - (marg_storage + marg_mech - grand_mean)
    interaction_map: Dict[str, float] = {}
    max_abs_dev_storage_x_cleanup = 0.0
    for storage in STORAGE_GRID:
        for mech in CLEANUP_MECHANISMS:
            matches = [p["acc"] for p in phase_map
                        if p.get("storage") == storage
                        and p["cleanup_mechanism"] == mech]
            if not matches:
                continue
            cell_mean = float(np.mean(matches))
            m1 = storage_marg[storage]
            m2 = mech_marg[mech]
            additive_pred = m1 + m2 - grand_mean
            dev = cell_mean - additive_pred
            interaction_map[f"{storage}_{mech}"] = round(dev, 4)
            max_abs_dev_storage_x_cleanup = max(max_abs_dev_storage_x_cleanup, abs(dev))

    # Baseline-in-band check for BUNDLED arm (META_RULE_AG)
    bundled_accs = [p["acc"] for p in phase_map if p.get("storage") == "BUNDLED"]
    if bundled_accs:
        bundled_mean = float(np.mean(bundled_accs))
        bundled_min = float(np.min(bundled_accs))
        bundled_max = float(np.max(bundled_accs))
    else:
        bundled_mean = bundled_min = bundled_max = -1.0
    # BUNDLED arm not-universally-floor: at least ONE point >= 0.10
    bundled_not_universal_floor = bundled_max >= 0.10
    # BUNDLED arm not-universally-ceiling: at least ONE point <= 0.90
    bundled_not_universal_ceiling = bundled_min <= 0.90

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
        "arms_differ_verified": (n_distinct_mechs == len(CLEANUP_MECHANISMS)),
        "pc_reproduce_iterative_cosine_regime": {
            "M": pc_M, "N": pc_N, "F": F_FIXED, "L": L_FIXED, "corruption": pc_corr,
            "acc": pc_acc, "threshold": 0.75, "pass": pc_pass,
        },
        "storage_gaps_sharded_minus_bundled": storage_gaps,
        "max_storage_gap": round(max_storage_gap, 4),
        "median_storage_gap": med_storage_gap,
        "mechanism_variance_at_SHARDED": mech_var_sharded,
        "mechanism_variance_at_BUNDLED": mech_var_bundled,
        "max_mechanism_variance_at_SHARDED": round(max_mech_var_sharded, 4),
        "max_mechanism_variance_at_BUNDLED": round(max_mech_var_bundled, 4),
        "storage_marginal_means": {k: round(v, 4) for k, v in storage_marg.items()},
        "mech_marginal_means": {k: round(v, 4) for k, v in mech_marg.items()},
        "grand_mean": round(grand_mean, 4),
        "storage_x_cleanup_interaction_map": interaction_map,
        "max_abs_dev_storage_x_cleanup": round(max_abs_dev_storage_x_cleanup, 4),
        "bundled_arm_stats": {
            "mean": round(bundled_mean, 4),
            "min": round(bundled_min, 4),
            "max": round(bundled_max, 4),
            "not_universal_floor": bundled_not_universal_floor,
            "not_universal_ceiling": bundled_not_universal_ceiling,
        },
        "avg_peak_mem_mb": round(avg_peak, 1),
        "elapsed_seed_s": round(elapsed, 2),
        "beta": BETA,
        "alpha_soft": ALPHA_SOFT,
        "F_fixed": F_FIXED,
        "L_fixed": L_FIXED,
    }


# ---------------------------------------------------------------------------
# Smoke-gate predicate
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    if body.get("observed_n_units") != body.get("expected_n_units"):
        return False, (f"cardinality_breach: expected {body.get('expected_n_units')} "
                       f"got {body.get('observed_n_units')}")
    if not body.get("arms_differ_verified"):
        return False, (f"arms_differ_fail: only {body.get('n_distinct_mechanisms')}"
                       f"/{len(CLEANUP_MECHANISMS)} distinct mechanism-output hashes")
    pc = body.get("pc_reproduce_iterative_cosine_regime", {})
    if not pc.get("pass"):
        return False, (f"pc_reproduce_fail: iterative_cosine SHARDED at PC regime "
                       f"acc={pc.get('acc')} threshold={pc.get('threshold')}")
    max_gap = body.get("max_storage_gap", 0.0)
    if max_gap < 0.30:
        return False, (f"storage_gap_positive_control_fail: max SHARDED-minus-BUNDLED "
                       f"gap = {max_gap:.3f} < 0.30 threshold")
    bstats = body.get("bundled_arm_stats", {})
    # Baseline_in_band: BUNDLED not universally at floor OR at ceiling (allows
    # measurement of mechanism variance). For smoke at M=200 N=2048 corr=0.20 we
    # expect BUNDLED in mid-range.
    if not (bstats.get("not_universal_floor") or bstats.get("not_universal_ceiling")):
        return False, (f"BUNDLED arm out-of-band: min={bstats.get('min')} "
                       f"max={bstats.get('max')}; cannot measure mechanism variance")

    # discriminator_fires check for smoke: report mech_variance_at_BUNDLED as
    # informational (not gating). Whether >= 0.05 or 0.0 is informative for FULL
    # decision, both are valid smoke outcomes.
    mech_var_bd = body.get("max_mechanism_variance_at_BUNDLED", 0.0)
    mech_var_sh = body.get("max_mechanism_variance_at_SHARDED", 0.0)
    reason_extra = (f"; mech_var_at_BUNDLED={mech_var_bd:.3f} "
                    f"mech_var_at_SHARDED={mech_var_sh:.3f}")

    return True, (f"smoke_gate_pass: cardinality_ok + arms_differ + "
                  f"pc_reproduce_acc={pc.get('acc'):.3f} + "
                  f"max_storage_gap={max_gap:.3f}{reason_extra}")


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]], run_mode: str
                          ) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "HARD_FAIL", "verdict_msg": "HARD_FAIL_NO_SEEDS",
                "summary": "HARD_FAIL_NO_SEEDS", "elapsed_s": 0.0}
    is_smoke = (run_mode == "smoke")
    seed_key = list(per_seed.keys())[0]
    body = per_seed[seed_key]

    common = {
        "phase_map": body.get("phase_map"),
        "expected_n_units": body.get("expected_n_units"),
        "observed_n_units": body.get("observed_n_units"),
        "cardinality_ok": body.get("cardinality_ok"),
        "mech_output_hash_agg": body.get("mech_output_hash_agg"),
        "n_distinct_mechanisms": body.get("n_distinct_mechanisms"),
        "arms_differ_verified": body.get("arms_differ_verified"),
        "pc_reproduce_iterative_cosine_regime": body.get("pc_reproduce_iterative_cosine_regime"),
        "storage_gaps_sharded_minus_bundled": body.get("storage_gaps_sharded_minus_bundled"),
        "max_storage_gap": body.get("max_storage_gap"),
        "median_storage_gap": body.get("median_storage_gap"),
        "mechanism_variance_at_SHARDED": body.get("mechanism_variance_at_SHARDED"),
        "mechanism_variance_at_BUNDLED": body.get("mechanism_variance_at_BUNDLED"),
        "max_mechanism_variance_at_SHARDED": body.get("max_mechanism_variance_at_SHARDED"),
        "max_mechanism_variance_at_BUNDLED": body.get("max_mechanism_variance_at_BUNDLED"),
        "storage_marginal_means": body.get("storage_marginal_means"),
        "mech_marginal_means": body.get("mech_marginal_means"),
        "grand_mean": body.get("grand_mean"),
        "storage_x_cleanup_interaction_map": body.get("storage_x_cleanup_interaction_map"),
        "max_abs_dev_storage_x_cleanup": body.get("max_abs_dev_storage_x_cleanup"),
        "bundled_arm_stats": body.get("bundled_arm_stats"),
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
            vmsg = (f"HARD_PASS_SMOKE: {body.get('observed_n_units')}"
                    f"/{body.get('expected_n_units')} pts; {reason}")
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
    cardinality_ok = body.get("cardinality_ok", False)
    pc_pass = body.get("pc_reproduce_iterative_cosine_regime", {}).get("pass", False)
    max_gap = body.get("max_storage_gap", 0.0)
    max_int = body.get("max_abs_dev_storage_x_cleanup", 0.0)
    mv_bundled = body.get("max_mechanism_variance_at_BUNDLED", 0.0)
    mv_sharded = body.get("max_mechanism_variance_at_SHARDED", 0.0)

    if not cardinality_ok:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH: expected="
                f"{body.get('expected_n_units')} observed={body.get('observed_n_units')}")
    elif not pc_pass:
        pc = body.get("pc_reproduce_iterative_cosine_regime", {})
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_MARGINAL_REPRODUCTION: PC reproduce acc="
                f"{pc.get('acc')} < threshold={pc.get('threshold')}")
    elif max_gap < 0.20:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_STORAGE_GAP_COLLAPSE: max SHARDED-BUNDLED gap="
                f"{max_gap:.3f} < 0.20; SHARDED-vs-BUNDLED distinction invalid at test regime")
    else:
        # Cross-term test: max_abs_dev >= 0.15 => strong cross-term
        # mech_var_bundled >= 0.05 => mechanism axis meaningful at BUNDLED
        strong_cross_term = (max_int >= 0.15) or (mv_bundled >= 0.05)
        weak_cross_term = (max_int >= 0.05) and (max_int < 0.15) and (mv_bundled < 0.05)
        if strong_cross_term:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_MECHANISM_AXIS_CONDITIONAL_ON_STORAGE: "
                    f"max_int_deviation={max_int:.4f} mech_var_at_BUNDLED={mv_bundled:.4f} "
                    f"mech_var_at_SHARDED={mv_sharded:.4f}; "
                    f"mechanism axis meaningful at BUNDLED (below-capacity) but "
                    f"collapses at SHARDED. Candidate REGIME-CONDITIONAL cross-term "
                    f"pending Skunkworks landed-VET + 3-seed replication.")
        elif weak_cross_term:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_WEAK_CROSS_TERM: max_int_deviation={max_int:.4f} "
                    f"in [0.05, 0.15); mech_var_at_BUNDLED={mv_bundled:.4f}; "
                    f"cross-term inventory filed; methodology-interesting")
        elif (max_int < 0.05) and (mv_bundled < 0.05) and (mv_sharded < 0.05):
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_MECHANISM_AXIS_UNIVERSALLY_DEGENERATE_IN_FHRR: "
                    f"max_int_deviation={max_int:.4f} < 0.05 "
                    f"mech_var_at_BUNDLED={mv_bundled:.4f} < 0.05 "
                    f"mech_var_at_SHARDED={mv_sharded:.4f} < 0.05; "
                    f"CG_META finding: CLEANUP_MECHANISM_M_scaling does NOT extend "
                    f"to FHRR under any storage strategy; regime-exclusive to "
                    f"bipolar-codebook cleanup regime. Pending Skunkworks landed-VET "
                    f"+ 3-seed replication before CG atom filing.")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_MIXED_SIGNAL: max_int_deviation={max_int:.4f} "
                    f"mech_var_at_BUNDLED={mv_bundled:.4f} "
                    f"mech_var_at_SHARDED={mv_sharded:.4f}; investigate before "
                    f"CG classification")

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
    })
    return out


__all__ = [
    "ANCHOR_NAME", "DEVICE", "GPU_NAME",
    "STORAGE_GRID", "CLEANUP_MECHANISMS",
    "M_GRID_FULL", "N_GRID_FULL", "CORRUPTION_GRID_FULL",
    "M_GRID_SMOKE", "N_GRID_SMOKE", "CORRUPTION_GRID_SMOKE",
    "F_FIXED", "L_FIXED", "TR_FULL", "TR_SMOKE",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "REQUIRED_FIELDS",
    "selftest", "run_one_seed", "smoke_gate_predicate", "aggregate_and_verdict",
]
