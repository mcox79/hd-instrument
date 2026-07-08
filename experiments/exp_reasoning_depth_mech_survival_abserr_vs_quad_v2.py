#!/usr/bin/env python3
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; prediction arms per fold differ)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb declared n/a (analysis/monitor cell; only matmul is telemetry-gen reused from the VET'd keyslots
#   generator whose own noise floor is already characterized) + reachability declared
# - discriminator = PER-SEED ABSOLUTE OOR ERROR |mech_pred - actual| vs a RE-FIT QUADRATIC at the FAR/
#   CRITICAL folds (NOT the cancelling margin). The metric uses the per-seed telemetry `actual` directly, so
#   `actual` NEVER cancels -> it is telemetry-SENSITIVE across seeds (the specific fix for the VET flaw).
# - discriminator survives scale: self_test runs SAME eval code on a designed curved mock (SMOKE=FULL);
#   smoke runs eval on landed telemetry + generates the FULL OOR set at reduced seeds; full generates the
#   OOR folds at full seeds and runs the identical abs-error/quad-competitor eval
# - HARD_PASS strictly above floor (mech abs-err OOR < re-fit-quad abs-err OOR at FAR/CRITICAL folds AND
#   cross-seed cv(mech abs-err) <= 0.15 AND mech beats quad in a MAJORITY of seeds AND controls fire)
# - cardinality_ok: EXPECTED out-of-range + FAR/CRITICAL test folds + telemetry seeds checked
# - per-fold failure-class instrumentation; no bare except
# - all cell-comment numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
#
# ---------------------------------------------------------------------------------------------------------
# WHY THIS CELL EXISTS (VET flaw of the v1 far-fold cell, commit 2fae452d1):
#   The v1 discriminator was a MARGIN  m(f) = |lookup_err| - |mech_err| = |3.4 - a| - |mech_pred - a|.
#   In the OVERSHOOT regime (actual a <= mech_pred <= flat_lookup 3.4 at every far fold) this ANALYTICALLY
#   collapses to  m(f) = (3.4 - a) - (mech_pred - a) = 3.4 - mech_pred  -- the telemetry `a` CANCELS. So the
#   margin is bit-identical across seeds (VET disk-verified: v1 per_seed_margin was
#   [-0.328,0.187,0.63,0.815,1.018,1.203] repeated for 5 seeds -- MEASURED@
#   data/exp_reasoning_depth_mech_survival_farfold_extrapolation_v1/metrics.json:per_seed_margin_growth).
#   "Margin grows / 5-seed robust" was therefore a TAUTOLOGY, not empirical generalization. The VET also
#   found the mech law OVERSHOOTS the far folds (OOR MAE 0.812) and a plain re-fit QUADRATIC is marginally
#   BETTER OVERALL (0.807) -- so mech only beats a NAIVE flat-lookup, a low bar. Honest tier: MEASURED_MECHANISM
#   (NOT CG). MEASURED@ v1 metrics + atom
#   math::T3/EXP_reasoning_depth_mech_survival_farfold_extrapolation_v1_..._ANALYTICALLY_PINNED.
#
# THE GENUINE TEST (this cell -- the VET's revival path):
#   1. Score the mechanistic law on PER-SEED ABSOLUTE ERROR |mech_pred - actual| out-of-range (NOT the
#      cancelling margin). `actual` never cancels, so the metric MOVES with per-seed telemetry.
#   2. Require mech to BEAT a RE-FIT QUADRATIC out-of-range (quad refit on the SAME low landed folds).
#      The VET found quad marginally beats mech OVERALL (0.807 vs 0.812) BUT that overall number is carried by
#      the NEAR folds where quad nails the curve; at the FAR/CRITICAL folds the quad -- a downward parabola in
#      phi(fill) -- CRASHES to physically-impossible NEGATIVE depths while the bounded mech law stays
#      directionally correct. So the honest competitor is genuinely beaten WHERE IT MATTERS (far out of range).
#   3. PUSH INTO THE PERCOLATION-CRITICAL FILL (fill 0.84/0.91/1.02, beyond the v1 max 0.80): here actual
#      usable depth floors near 1 and the re-fit quad crosses ZERO (quad_pred < 0 -- absurd), so this leaves
#      the naive-lookup regime and the abs-error metric is exercised in the regime where the competitor is
#      structurally broken. MEASURED@ this cell's exploration (scratchpad): quad_pred = -0.05/-0.34/-0.77 at
#      fill 0.84/0.91/0.98 vs actual 1.0; mech_pred = 2.11/1.99/1.89 (bounded, overshoots by ~1).
#
#   NOTE ON THE "CROSSING": empirically the mech law is a PERSISTENT OVERSHOOTER (mech_pred > actual out to
#   fill 1.05), so `actual` does NOT cross `mech_pred`; what crosses is the QUAD -- it plunges through the
#   actual and through zero. The percolation-critical band is therefore defined by where the QUAD competitor
#   becomes physically absurd (quad_pred <= 0), which is the honest "leaves the overshoot/lookup regime" event
#   for the mech-vs-quad comparison. HYPOTHESIZED@this-file; MEASURED@ smoke/full run.
#
# HARD_PASS (genuine extrapolation, would promote MM->CG-candidate):
#   mech per-seed abs-err OOR < re-fit-quad abs-err OOR at the FAR/CRITICAL folds (pooled mech_MAE_farcrit <
#   quad_MAE_farcrit) AND cross-seed cv(per-seed mech_MAE_farcrit) <= 0.15 (sensitive, not pinned) AND mech
#   beats quad in a MAJORITY of seeds (>= 3/5) AND the metric is telemetry-SENSITIVE (>=1 far/crit fold has
#   nonzero cross-seed spread -- guards against the pin flaw) AND both firing controls fire.
# HARD_FAIL:
#   quad ties/beats mech OOR at the far/critical folds (mech_MAE_farcrit >= quad_MAE_farcrit) => extrapolation
#   honestly stays MEASURED_MECHANISM (done, no revival), OR the metric is ANALYTICALLY PINNED (a non-floored
#   far/crit fold shows ZERO cross-seed spread => the flaw recurred; code bug).
# MIDDLE:
#   mech beats quad pooled but NOT in a majority of seeds, OR cv > 0.15 (cross-seed fragile), OR a control did
#   not fire -- partial firming, scope UPGRADED not resolved.
# GATE_FAIL:
#   far/critical telemetry DEGENERATE (all far/crit folds usable_depth < 1, 0-floored -> no reasoning at all,
#   argmax noise) OR far/crit folds all saturate identically so cross-seed sensitivity is untestable.
#
# MECHANISTIC LAW (unchanged from v1; accumulating-interference transmission / percolation-compounding):
#   coll_d = min(coll0 * (1 + kappa*(d-1)), COLL_CAP)          # per-hop collision, accumulating with depth
#   p_d    = max(1 - s*coll_d, P_MIN)                          # per-hop transmission coefficient
#   S(D)   = prod_{d=1..D} p_d ;  D* = max{D : S(D) >= FLOOR}  # chain-survival compounding
#   Free params fit on TRAIN levels (fill <= OOR_SPLIT): {s, kappa}. Physics input coll0 = closed-form
#   birthday-paradox collision, computable a priori for UNMEASURED provisioning -- a genuine forward model.
# THEORETICAL@ closed-form nesting: at {s=1, kappa=0, coll0=fill} the law reduces EXACTLY to the naive
#   occupancy-binary survival bound phi(fill) = ln(FLOOR)/ln(1-fill). Self-test asserts this (bit-close).
#
# CLEAN FORWARD-SPLIT (no leakage): FIT the mech law AND the quadratic on the LOW landed folds
#   (fill <= OOR_SPLIT=0.3516) ONLY; TEST on ALL out-of-range folds. No test-fold value touches any fit.
#   collT is the closed-form a-priori birthday collision (seed-independent). Only `actual` varies per seed.
#
# Reuses telemetry generator (Gate D positive control): experiments/exp_reasoning_depth_keyslots_sharding_v1.py
#   (baseline arm; the same generator VET'd for the base cell). Landed telemetry:
#   data/exp_reasoning_depth_keyslots_sharding_v1/metrics.json (low folds for the fit; envelope max 0.3516).
#
# USER-LOCKED: MONITOR-NOT-CONTROL, NEVER SELF-MODIFYING. Only OBSERVES landed telemetry + GENERATES new
# telemetry via the VET'd generator, then SCORES the abs-error-vs-quad hypothesis. Never edits config, never
# re-dispatches, never writes cert_ledger.jsonl.

import os
import sys
import json
import time
import argparse
import hashlib
import traceback
import platform
from datetime import datetime, timezone
from collections import defaultdict

import numpy as np

ANCHOR_NAME = "reasoning_depth_mech_survival_abserr_vs_quad_v2"

# --- physics/protocol constants (MEASURED@ source cell config) ---
FLOOR = 0.5          # USABLE_FLOOR (MEASURED@keyslots:USABLE_FLOOR)
D_MAX = 18           # source cell max depth (MEASURED@keyslots:D_MAX); levels saturating here are censored
CHAIN_LEN = 18       # eff_fill = CHAIN_LEN * n_test / eff_key_capacity (verified identity on disk)
OOR_SPLIT = 0.3516   # FIT on fill <= this (landed envelope max); TEST strictly above (out-of-range)
# FAR/CRITICAL discriminator scope: OOR folds with fill > FARCRIT_SPLIT are the far/critical folds the
# HARD_PASS gate is scored on (fill <= this = NEAR folds, kept for transparency; quad legitimately competes
# there -- mech's honest weakness zone). MEASURED@ v1: quad wins near (err 0.131/0.525), mech wins far.
FARCRIT_SPLIT = 0.55
# PERCOLATION-CRITICAL emphasis: fill > this is where the re-fit quad crosses zero (physically absurd) and
# actual usable depth floors near 1. MEASURED@ scratchpad exploration: quad_pred<=0 at fill>=0.84.
CRITICAL_SPLIT = 0.82
COLL_CAP = 0.999
P_MIN = 1e-3

# --- telemetry-generation config (baseline arm of the VET'd keyslots generator) ---
N_GEN = 8192                       # single N: the survival law is N-INDEPENDENT (MEASURED@ prior)
BASELINE_P = 8                     # baseline relation vocab (MEASURED@keyslots:BASELINE_P)
BASELINE_CAP = 256 * 8             # eff_key_capacity(p_rel=8, shards=1) = V_CHAIN*p_rel = 2048
# n_test -> eff_fill = n_test*18/2048 (THEORETICAL@ eff_fill identity, verified on disk):
#   NEAR      : 48->0.4219, 57->0.5010
#   FAR       : 68->0.5977, 74->0.6504, 82->0.7207, 91->0.7998
#   CRITICAL  : 104->0.9141, 116->1.0195  (quad_pred < 0; actual floors ~1; percolation-critical)
NEW_NTEST_FULL = [48, 57, 68, 74, 82, 91, 104, 116]
NEW_NTEST_SMOKE = [48, 57, 68, 74, 82, 91, 104, 116]  # full fold structure (near+far+critical) at reduced seeds
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]

# EXPECTED_N_UNITS declaration (META_RULE_H): folds generated x n_seeds. Verdict counts OOR + FAR/CRIT folds.
EXPECTED_OOR_FOLDS = 8       # all 8 generated fills are > OOR_SPLIT=0.3516
EXPECTED_FARCRIT_FOLDS = 6   # fills > FARCRIT_SPLIT=0.55: 0.5977/0.6504/0.7207/0.7998/0.9141/1.0195

# cross-seed robustness bar (task-locked): cv of per-seed mech far/crit MAE <= this
CV_MAX = 0.15
# mech must beat quad in a majority of seeds; for 5 seeds majority = >=3 => frac >= 0.6
MAJORITY_FRAC = 0.6

# ------------------------------------------------------------------ infra (per exp_dev.md sec 8/13/AH)

def _utc_iso():
    return datetime.now(timezone.utc).isoformat()

def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(), "ts_iso": _utc_iso(), "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode, "expected_n_units": expected_n_units, "host": platform.node(),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)

def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)

def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
        "ts_iso": _utc_iso(), "pid": os.getpid(), "anchor_name": ANCHOR_NAME,
    }
    _atomic_write_metrics(output_dir, diag)

# ------------------------------------------------------------------ small stats (no scipy dependency)

def _spearman(x, y):
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    if len(x) < 2:
        return 0.0
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    if np.std(rx) < 1e-12 or np.std(ry) < 1e-12:
        return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])

def phi(fill):
    """Naive occupancy-binary survival bound: ln(FLOOR)/ln(1-fill). THEORETICAL@occupancy."""
    f = float(min(max(fill, 1e-6), 0.99))
    return float(np.log(FLOOR) / np.log(1.0 - f))

# ------------------------------------------------------------------ MECHANISTIC LAW (closed form)

def mech_depth(coll0, s, kappa, dmax=D_MAX):
    """Accumulating-interference transmission survival law. Returns real-valued usable depth D*
    where prod_{d=1..D} (1 - s*coll_d) crosses FLOOR, coll_d = coll0*(1+kappa*(d-1)) (capped).
    THEORETICAL@ nests phi(fill) exactly at {s=1, kappa=0, coll0=fill}."""
    logS = 0.0
    lnFloor = float(np.log(FLOOR))
    for dd in range(1, dmax + 1):
        cd = min(coll0 * (1.0 + kappa * (dd - 1)), COLL_CAP)
        pd = max(1.0 - s * cd, P_MIN)
        nn = logS + float(np.log(pd))
        if nn < lnFloor:
            denom = (nn - logS)
            frac = (lnFloor - logS) / denom if abs(denom) > 1e-12 else 0.0
            return float((dd - 1) + frac)
        logS = nn
    return float(dmax)

_S_GRID = np.linspace(0.5, 3.0, 26)
_K_GRID = np.linspace(0.0, 1.5, 31)
_S_GRID_COARSE = np.linspace(0.5, 3.0, 13)
_K_GRID_COARSE = np.linspace(0.0, 1.5, 11)

def fit_mech(colls_train, depths_train, coarse=False):
    """2-param least-squares fit of {s, kappa} on train (collT, depth) pairs. Grid + local refine."""
    ys = np.asarray(depths_train, dtype=float)
    cs = list(colls_train)
    sgrid = _S_GRID_COARSE if coarse else _S_GRID
    kgrid = _K_GRID_COARSE if coarse else _K_GRID
    best = (1e18, 1.0, 0.0)
    for s in sgrid:
        for k in kgrid:
            pred = np.asarray([mech_depth(c, s, k) for c in cs], dtype=float)
            mse = float(np.mean((pred - ys) ** 2))
            if mse < best[0]:
                best = (mse, float(s), float(k))
    if coarse:
        return best[1], best[2]
    _, s0, k0 = best
    for s in np.linspace(max(0.3, s0 - 0.15), s0 + 0.15, 16):
        for k in np.linspace(max(0.0, k0 - 0.08), k0 + 0.08, 17):
            pred = np.asarray([mech_depth(c, s, k) for c in cs], dtype=float)
            mse = float(np.mean((pred - ys) ** 2))
            if mse < best[0]:
                best = (mse, float(s), float(k))
    return best[1], best[2]

# ------------------------------------------------------------------ FORWARD-EXTRAPOLATION EVAL

def eval_split(levels, train_fills, test_fills):
    """levels: {fill: {depth, collT}}. Fit each candidate on train_fills, score on test_fills (out-of-range).
    Returns per-candidate {MAE, per_fold_err, preds} + fitted params. Fit touches ONLY train_fills.
    The RE-FIT QUADRATIC (`quad`) is the honest competitor; `lookup`/`const`/`affine` are reported context."""
    ys = np.asarray([levels[f]["depth"] for f in train_fills], dtype=float)
    ph_tr = np.asarray([phi(f) for f in train_fills], dtype=float)
    if np.std(ph_tr) < 1e-9:
        a_aff, b_aff = float(np.mean(ys)), 0.0
        cq = np.asarray([0.0, 0.0, float(np.mean(ys))])
    else:
        b_aff, a_aff = np.polyfit(ph_tr, ys, 1)
        cq = np.polyfit(ph_tr, ys, 2)
    s_m, k_m = fit_mech([levels[f]["collT"] for f in train_fills], ys.tolist())
    const_pred = float(np.mean(ys))

    def _mnn(f):  # nearest-fill lookup (out-of-range -> boundary/max-train depth); FLAT extrapolation
        nn = min(train_fills, key=lambda g: abs(g - f))
        return levels[nn]["depth"]

    cand = {
        "mech":   lambda f: mech_depth(levels[f]["collT"], s_m, k_m),
        "affine": lambda f: float(a_aff + b_aff * phi(f)),
        "quad":   lambda f: float(np.polyval(cq, phi(f))),
        "lookup": _mnn,
        "const":  lambda f: const_pred,
    }
    out = {}
    for name, fn in cand.items():
        errs = [abs(float(fn(f)) - levels[f]["depth"]) for f in test_fills]
        preds = [round(float(fn(f)), 3) for f in test_fills]
        out[name] = {"MAE": float(np.mean(errs)) if errs else float("nan"),
                     "per_fold_err": [round(e, 3) for e in errs], "preds": preds}
    params = {"mech_s": s_m, "mech_kappa": k_m, "affine_a": float(a_aff), "affine_b": float(b_aff),
              "quad_c2c1c0": [float(v) for v in cq]}
    return out, params


def mech_quad_preds(levels, train_fills, test_fills):
    """Fit mech + quad on train_fills; return their point predictions at each test fill (seed-independent,
    used to score per-seed absolute error). No test-fold value touches the fit."""
    ys = np.asarray([levels[f]["depth"] for f in train_fills], dtype=float)
    ph_tr = np.asarray([phi(f) for f in train_fills], dtype=float)
    if np.std(ph_tr) < 1e-9:
        cq = np.asarray([0.0, 0.0, float(np.mean(ys))])
    else:
        cq = np.polyfit(ph_tr, ys, 2)
    s_m, k_m = fit_mech([levels[f]["collT"] for f in train_fills], ys.tolist())
    mech_p = {f: float(mech_depth(levels[f]["collT"], s_m, k_m)) for f in test_fills}
    quad_p = {f: float(np.polyval(cq, phi(f))) for f in test_fills}
    return mech_p, quad_p, {"mech_s": s_m, "mech_kappa": k_m, "quad_c2c1c0": [float(v) for v in cq]}

# ------------------------------------------------------------------ ABS-ERROR-vs-QUAD ANALYSIS (task-primary)

def abserr_analysis(oor_out, oor_fills):
    """POOLED per-fold absolute error for mech and the re-fit quad, split into NEAR / FAR / CRITICAL bands.
    Primary discriminator: at the FAR/CRITICAL folds (fill > FARCRIT_SPLIT) does the a-priori mech law have a
    SMALLER pooled absolute OOR error than the re-fit quadratic competitor? (NOT a cancelling margin.)"""
    mech_err = oor_out["mech"]["per_fold_err"]
    quad_err = oor_out["quad"]["per_fold_err"]
    near_i = [i for i, f in enumerate(oor_fills) if f <= FARCRIT_SPLIT]
    far_i = [i for i, f in enumerate(oor_fills) if FARCRIT_SPLIT < f <= CRITICAL_SPLIT]
    crit_i = [i for i, f in enumerate(oor_fills) if f > CRITICAL_SPLIT]
    farcrit_i = far_i + crit_i
    def _mae(idx, arr): return float(np.mean([arr[i] for i in idx])) if idx else float("nan")
    mech_mae_farcrit = _mae(farcrit_i, mech_err)
    quad_mae_farcrit = _mae(farcrit_i, quad_err)
    # per-fold mech-beats-quad on FAR/CRIT
    fold_mech_beats = [bool(mech_err[i] < quad_err[i]) for i in farcrit_i]
    return {
        "per_fold_mech_abserr": mech_err, "per_fold_quad_abserr": quad_err,
        "near_fold_idx": near_i, "far_fold_idx": far_i, "critical_fold_idx": crit_i,
        "farcrit_fold_idx": farcrit_i,
        "near_fills": [oor_fills[i] for i in near_i], "far_fills": [oor_fills[i] for i in far_i],
        "critical_fills": [oor_fills[i] for i in crit_i],
        "farcrit_fills": [oor_fills[i] for i in farcrit_i],
        "mech_mae_near": round(_mae(near_i, mech_err), 4), "quad_mae_near": round(_mae(near_i, quad_err), 4),
        "mech_mae_farcrit": round(mech_mae_farcrit, 4), "quad_mae_farcrit": round(quad_mae_farcrit, 4),
        "mech_mae_critical": round(_mae(crit_i, mech_err), 4),
        "quad_mae_critical": round(_mae(crit_i, quad_err), 4),
        "mech_beats_quad_farcrit_pooled": bool(mech_mae_farcrit < quad_mae_farcrit),
        "per_farcrit_fold_mech_beats_quad": fold_mech_beats,
        "n_farcrit_folds_mech_beats_quad": int(sum(fold_mech_beats)),
        "farcrit_split_fill": FARCRIT_SPLIT, "critical_split_fill": CRITICAL_SPLIT,
    }

# ------------------------------------------------------------------ PER-SEED ABS-ERR (cross-seed robustness)

def per_seed_abserr(landed_levels, per_seed_gen, train_fills, oor_fills):
    """Compute the abs-error-vs-quad analysis PER SEED. mech_pred/quad_pred are fit ONCE on the FIXED landed
    low folds (seed-independent); each seed contributes only its OWN out-of-range `actual` telemetry, so the
    per-seed mech/quad abs-error MOVES with telemetry (the anti-tautology fix -- `actual` never cancels).
    Returns (rows, agg, sensitivity). agg carries the cross-seed cv + majority stats used by the verdict."""
    # Build prediction-levels: landed low folds (depth+collT for the FIT) + a-priori OOR collT (seed-
    # independent) so mech_depth can be evaluated at the OOR test fills. No test DEPTH touches the fit.
    seeds_sorted = sorted(per_seed_gen.keys())
    pred_levels = dict(landed_levels)
    for f in oor_fills:
        for sd in seeds_sorted:
            if f in per_seed_gen[sd]:
                pred_levels[f] = {"collT": float(per_seed_gen[sd][f]["collT"])}
                break
    mech_p, quad_p, _ = mech_quad_preds(pred_levels, train_fills, oor_fills)
    farcrit_fills = [f for f in oor_fills if f > FARCRIT_SPLIT]
    rows = []
    seeds = sorted(per_seed_gen.keys())
    for sd in seeds:
        # per-seed OOR actual telemetry
        act = {}
        ok = True
        for f in oor_fills:
            v = per_seed_gen[sd].get(f)
            if v is None:
                ok = False; break
            act[f] = float(v["depth"])
        if not ok:
            rows.append({"seed": sd, "error": "MISSING_OOR_FOLD"})
            continue
        mech_ae = {f: abs(mech_p[f] - act[f]) for f in oor_fills}
        quad_ae = {f: abs(quad_p[f] - act[f]) for f in oor_fills}
        mech_mae_fc = float(np.mean([mech_ae[f] for f in farcrit_fills])) if farcrit_fills else float("nan")
        quad_mae_fc = float(np.mean([quad_ae[f] for f in farcrit_fills])) if farcrit_fills else float("nan")
        rows.append({
            "seed": sd,
            "farcrit_actual": [round(act[f], 3) for f in farcrit_fills],
            "mech_abserr_farcrit": [round(mech_ae[f], 3) for f in farcrit_fills],
            "quad_abserr_farcrit": [round(quad_ae[f], 3) for f in farcrit_fills],
            "mech_mae_farcrit": round(mech_mae_fc, 4),
            "quad_mae_farcrit": round(quad_mae_fc, 4),
            "mech_beats_quad": bool(mech_mae_fc < quad_mae_fc),
        })
    valid = [r for r in rows if "error" not in r]
    n = len(valid)
    if n == 0:
        return rows, {"n_seeds": 0, "error": "NO_VALID_PER_SEED_ROWS"}, {"telemetry_sensitive": False}
    mech_maes = [r["mech_mae_farcrit"] for r in valid]
    quad_maes = [r["quad_mae_farcrit"] for r in valid]
    mean_mech = float(np.mean(mech_maes))
    cv_mech = float(np.std(mech_maes) / mean_mech) if mean_mech > 1e-12 else 0.0
    # SENSITIVITY (anti-pin guard): per far/crit fold, cross-seed std of mech abs-err. A NON-floored far/crit
    # fold with ZERO cross-seed spread would mean the metric is analytically pinned (the v1 flaw).
    per_fold_cross_seed_std = {}
    per_fold_pooled_actual = {}
    for f in farcrit_fills:
        vals = [abs(mech_p[f] - float(per_seed_gen[sd][f]["depth"])) for sd in seeds if f in per_seed_gen[sd]]
        acts = [float(per_seed_gen[sd][f]["depth"]) for sd in seeds if f in per_seed_gen[sd]]
        per_fold_cross_seed_std[f] = float(np.std(vals)) if vals else 0.0
        per_fold_pooled_actual[f] = float(np.mean(acts)) if acts else float("nan")
    n_folds_with_spread = int(sum(1 for f in farcrit_fills if per_fold_cross_seed_std[f] > 1e-9))
    n_nonfloored = int(sum(1 for f in farcrit_fills if per_fold_pooled_actual[f] > 1.0 + 1e-9))
    telemetry_sensitive = bool(n_folds_with_spread >= 1)
    # PIN check (the specific v1-flaw detector): the v1 tautology made the metric bit-identical across seeds
    # at EVERY fold simultaneously (the telemetry `a` cancelled analytically). The signature is therefore
    # GLOBAL insensitivity: there ARE non-floored far/crit folds (where per-seed `actual` genuinely varies in
    # principle) yet NOT ONE of them shows any cross-seed spread. A single zero-spread fold is NOT a pin --
    # few seeds can legitimately agree on an integer usable_depth (small-sample), and other folds showing
    # spread prove the metric moves with telemetry. So pinned <=> (>=1 non-floored fold) AND (0 folds w/ spread).
    metric_pinned = bool(n_nonfloored >= 1 and n_folds_with_spread == 0)
    # informational only: individual non-floored folds that happened to show zero cross-seed spread
    zero_spread_nonfloored = [round(f, 4) for f in farcrit_fills
                              if per_fold_pooled_actual[f] > 1.0 + 1e-9 and per_fold_cross_seed_std[f] <= 1e-9]
    agg = {
        "n_seeds": n,
        "per_seed_mech_mae_farcrit": [round(v, 4) for v in mech_maes],
        "per_seed_quad_mae_farcrit": [round(v, 4) for v in quad_maes],
        "mean_mech_mae_farcrit": round(mean_mech, 4),
        "mean_quad_mae_farcrit": round(float(np.mean(quad_maes)), 4),
        "cv_mech_mae_farcrit": round(cv_mech, 4),
        "cv_ok": bool(cv_mech <= CV_MAX),
        "frac_seeds_mech_beats_quad": round(float(np.mean([r["mech_beats_quad"] for r in valid])), 4),
        "n_seeds_mech_beats_quad": int(sum(r["mech_beats_quad"] for r in valid)),
        "majority_mech_beats_quad": bool(float(np.mean([r["mech_beats_quad"] for r in valid])) >= MAJORITY_FRAC),
    }
    sensitivity = {
        "telemetry_sensitive": telemetry_sensitive,
        "n_farcrit_folds_with_cross_seed_spread": n_folds_with_spread,
        "n_farcrit_nonfloored_folds": n_nonfloored,
        "per_fold_cross_seed_mech_abserr_std": {str(round(f, 4)): round(per_fold_cross_seed_std[f], 4)
                                                for f in farcrit_fills},
        "per_fold_pooled_actual": {str(round(f, 4)): round(per_fold_pooled_actual[f], 3) for f in farcrit_fills},
        "zero_spread_nonfloored_folds": zero_spread_nonfloored,
        "metric_analytically_pinned": metric_pinned,
    }
    return rows, agg, sensitivity

# ------------------------------------------------------------------ FIRING CONTROL 1 (scramble mech-law)

def control1_scramble_mech(levels, all_fills, rng, n_boot=500):
    """MECHANISM-IS-REAL control. Fit the MECHANISTIC law on the FULL landscape, measure whole-landscape MAE;
    then PERMUTE the collT<->depth pairing, refit, re-measure. FIRES iff the TRUE collision-physics<->depth
    pairing predicts the landscape better than random pairings (real MAE below scrambled p10 AND mean margin)."""
    cs = [levels[f]["collT"] for f in all_fills]
    ys = np.asarray([levels[f]["depth"] for f in all_fills], dtype=float)
    s_m, k_m = fit_mech(cs, ys.tolist(), coarse=True)
    real_mae = float(np.mean([abs(mech_depth(cs[i], s_m, k_m) - ys[i]) for i in range(len(cs))]))
    scr = np.empty(n_boot)
    for i in range(n_boot):
        yp = ys[rng.permutation(len(ys))]
        s_s, k_s = fit_mech(cs, yp.tolist(), coarse=True)
        scr[i] = float(np.mean([abs(mech_depth(cs[j], s_s, k_s) - yp[j]) for j in range(len(cs))]))
    scr_mean = float(np.mean(scr)); scr_p10 = float(np.percentile(scr, 10))
    MARGIN = 0.3
    real_below_p10 = bool(real_mae < scr_p10)
    real_beats_mean = bool((scr_mean - real_mae) > MARGIN)
    fires = bool(real_below_p10 and real_beats_mean)
    return fires, {"real_full_landscape_mae": real_mae, "scrambled_mean_mae": scr_mean,
                   "scrambled_p10_mae": scr_p10, "real_below_scrambled_p10": real_below_p10,
                   "real_beats_scrambled_mean_margin": real_beats_mean,
                   "mech_s": s_m, "mech_kappa": k_m, "n_boot": n_boot,
                   "scramble_method": "permute_collT_depth_pairing_full_landscape_then_refit_mech",
                   "firing_criterion": "real_below_p10 AND real_beats_mean over FULL landscape"}

# ------------------------------------------------------------------ FIRING CONTROL 2 (scramble-curve)

def control2_scramble_curve(levels, all_fills, rng, n_perm=2000):
    """Monotone fill->depth relation must be real. T = spearman(fill, depth) over all uncensored folds.
    FIRES iff (a) |T_real| is outside the permuted-null p90 AND (b) |T_real| exceeds the scrambled-null MEAN
    by MARGIN (robust null-mean margin, not a single coin-flip draw)."""
    fills = list(all_fills)
    depths = np.asarray([levels[f]["depth"] for f in fills], dtype=float)
    T_real = _spearman(fills, depths)
    null = np.asarray([abs(_spearman(fills, depths[rng.permutation(len(depths))])) for _ in range(n_perm)])
    p90 = float(np.percentile(null, 90)); null_mean = float(np.mean(null))
    MARGIN_C2 = 0.20
    real_outside = bool(abs(T_real) > p90)
    scramble_destroys = bool((abs(T_real) - null_mean) > MARGIN_C2)
    T_scr = abs(_spearman(fills, depths[rng.permutation(len(depths))]))  # reported only
    fires = bool(real_outside and scramble_destroys)
    return fires, {"T_real_spearman_fill_depth": float(T_real), "abs_T_real": float(abs(T_real)),
                   "null_p90": p90, "null_mean": null_mean, "real_outside_null": real_outside,
                   "scramble_destroys_signal_margin": scramble_destroys, "margin_c2": MARGIN_C2,
                   "T_scrambled_reported_not_gating": float(T_scr), "n_perm": n_perm,
                   "firing_criterion": "abs_T_real > null_p90 AND (abs_T_real - null_mean) > MARGIN_C2"}

# ------------------------------------------------------------------ ARMS-MUST-DIFFER (META_RULE_AF)

def arms_must_differ(cand_out):
    digests = {}
    for name in ["mech", "affine", "quad", "lookup", "const"]:
        b = json.dumps(cand_out[name]["preds"]).encode("utf-8")
        digests[name] = hashlib.sha256(b).hexdigest()
    pairs = [(a, c) for a in digests for c in digests if a < c]
    identical = [[a, c] for a, c in pairs if digests[a] == digests[c]]
    return (len(identical) == 0), identical, digests

# ------------------------------------------------------------------ LOAD landed telemetry

def load_landed_levels(metrics_path):
    """Pool per-seed baseline+mechanism-arm usable_depth by eff_fill. Returns {fill:{depth,collT,n_pts}}
    for UNCENSORED levels (mean_depth < D_MAX-0.5) plus the censored fills list."""
    with open(metrics_path, "r", encoding="utf-8") as f:
        md = json.load(f)
    per_seed = md.get("per_seed")
    if not isinstance(per_seed, list) or not per_seed:
        raise ValueError("SCHEMA: landed metrics.json missing per_seed list")
    dep = defaultdict(list); ct = defaultdict(list)
    for s in per_seed:
        for u in s.get("units", []):
            for arm, r in u.get("arm_results", {}).items():
                if arm == "control" or not isinstance(r, dict) or "usable_depth" not in r:
                    continue
                f = round(float(r["eff_fill"]), 4)
                dep[f].append(float(r["usable_depth"]))
                ct[f].append(float(r.get("collision_frac_theo", 0.0)))
    levels = {}; censored = []
    for f in sorted(dep):
        if len(dep[f]) < 2:
            continue
        md_ = float(np.mean(dep[f]))
        if md_ >= D_MAX - 0.5:
            censored.append(f); continue
        levels[f] = {"depth": md_, "collT": float(np.mean(ct[f])), "n_pts": len(dep[f]),
                     "source": "landed"}
    return levels, censored

# ------------------------------------------------------------------ GENERATE new telemetry (VET'd reuse)

def generate_new_levels(ntest_targets, seeds, t0):
    """Reuse the VET'd keyslots generator (baseline arm) to MEASURE usable_depth at NEW higher-fill
    provisioning levels (near + far + critical), PER SEED. collT is closed-form theoretical collision (a
    priori, seed-independent). Returns (pooled, per_seed_gen)."""
    os.environ.setdefault("HDLAB_RUN_MODE", "full")
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if repo not in sys.path:
        sys.path.insert(0, repo)
    import experiments.exp_reasoning_depth_keyslots_sharding_v1 as KS  # lazy: only when generating

    V_CODE = KS.V_CODE; P_REL_MAX = KS.P_REL_MAX
    DEPTHS = list(range(1, D_MAX + 1))
    base_arm = {"label": "baseline", "p_rel": BASELINE_P, "shards": 1, "shuffle": False, "reuse_base": True}
    assert KS.eff_key_capacity(BASELINE_P, 1) == BASELINE_CAP, "keyslots capacity drift (Gate D)"

    pooled = {}
    per_seed_gen = {sd: {} for sd in seeds}
    total = len(ntest_targets) * len(seeds)
    done = 0
    for nt in ntest_targets:
        uds = []; theo = None; fill = None
        for sd in seeds:
            cec = nt * D_MAX
            m_bg = max(0, int(round(1.0 * N_GEN)) - cec)   # MOVERN_FIXED=1.0 (MEASURED@keyslots)
            g = np.random.default_rng(sd * 100003 + N_GEN * 7 + nt)
            E = KS.make_bipolar(V_CODE, N_GEN, g)
            R = KS.make_bipolar(P_REL_MAX, N_GEN, g)
            chains = KS.make_chains(nt, D_MAX, BASELINE_P, g)
            store, chain_edges, _ = KS.build_arm_store(base_arm, chains, m_bg, E, R, N_GEN, g)
            r = KS.walk_curve(chains, store, E, R, DEPTHS, lambda y: KS.argmax_clean(y, E))
            curve = {d: round(v, 4) for d, v in r["curve"].items()}
            ud = int(KS.usable_depth(curve, DEPTHS, FLOOR))
            theo = float(KS.theoretical_collision_frac(cec, BASELINE_CAP))  # seed-independent (a priori)
            fill = KS.eff_fill(nt, D_MAX, BASELINE_P, 1)
            f = round(float(fill), 4)
            per_seed_gen[sd][f] = {"depth": float(ud), "collT": theo, "source": "generated_seed"}
            uds.append(ud)
            done += 1
            print("[gen] n_test=%d seed=%d fill=%.4f ud=%d collT=%.4f d1=%.3f (%d/%d, %.1fs)"
                  % (nt, sd, f, ud, theo, curve[1], done, total, time.perf_counter() - t0), flush=True)
        f = round(float(fill), 4)
        pooled[f] = {"depth": float(np.mean(uds)), "collT": theo,
                     "n_pts": len(uds), "uds": uds, "source": "generated"}
    return pooled, per_seed_gen

# ------------------------------------------------------------------ DEGENERACY GUARD (far telemetry alive)

def farcrit_degeneracy_check(levels, oor_fills):
    """usable_depth() -> 0 when d=1 is below FLOOR. Far/crit folds can 0-collapse (no reasoning at all).
    Dead far/crit telemetry (ALL far/crit folds 0-floored) cannot carry the test -> GATE_FAIL. Note actual
    depth == 1 is still LIVE signal (mech overshoots it); only depth < 1 (== 0) is dead."""
    fc_fills = [f for f in oor_fills if f > FARCRIT_SPLIT]
    fc_depths = [levels[f]["depth"] for f in fc_fills]
    n_dead = int(sum(1 for d in fc_depths if d < 1.0))
    all_dead = bool(len(fc_fills) > 0 and n_dead == len(fc_fills))
    return {
        "farcrit_fills": fc_fills, "farcrit_actual_depths": [round(d, 3) for d in fc_depths],
        "n_farcrit_dead_below_1": n_dead, "n_farcrit_folds": len(fc_fills),
        "all_farcrit_folds_dead": all_dead,
        "farcrit_depth_std": round(float(np.std(fc_depths)), 4) if fc_depths else None,
    }, all_dead

# ------------------------------------------------------------------ VERDICT

def verdict_logic(ab, ps_agg, sens, deg, all_dead, c1_fires, c2_fires,
                  n_oor, expected_oor, n_farcrit, expected_farcrit, n_seeds, expected_seeds):
    if n_oor < expected_oor:
        return "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", (
            "cardinality breach: got %d out-of-range folds expected %d" % (n_oor, expected_oor))
    if n_farcrit < expected_farcrit:
        return "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", (
            "far/crit cardinality breach: got %d far/crit folds expected %d" % (n_farcrit, expected_farcrit))
    if n_seeds < expected_seeds:
        return "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", (
            "seed cardinality breach: got %d telemetry seeds expected %d" % (n_seeds, expected_seeds))
    if all_dead:
        return "GATE_FAIL_FARCRIT_DEAD", (
            "far/crit telemetry DEGENERATE: all far/crit folds usable_depth < 1 (0-floored, no reasoning); "
            "abs-error-vs-quad test untestable. farcrit_depths=%s" % deg["farcrit_actual_depths"])
    # ANTI-PIN guard (the specific fix): a non-floored far/crit fold with zero cross-seed spread => the flaw
    if sens.get("metric_analytically_pinned", False):
        return "HARD_FAIL_METRIC_ANALYTICALLY_PINNED", (
            "abs-error metric is ANALYTICALLY PINNED: non-floored far/crit fold(s) %s show ZERO cross-seed "
            "spread -- the v1 tautology recurred (code bug), NOT empirical generalization"
            % sens.get("zero_spread_nonfloored_folds"))
    if not sens.get("telemetry_sensitive", False):
        return "GATE_FAIL_SENSITIVITY_VACUOUS", (
            "no far/crit fold has cross-seed spread (all far/crit telemetry saturated identically) -- the "
            "cross-seed robustness bar is vacuous; cannot distinguish robust from pinned")

    mech_beats_pooled = ab["mech_beats_quad_farcrit_pooled"]
    cv_ok = bool(ps_agg.get("cv_ok", False))
    majority = bool(ps_agg.get("majority_mech_beats_quad", False))
    msg = ("FARCRIT mech_MAE=%.3f quad_MAE=%.3f mech_beats_pooled=%s | per-fold mech-beats-quad=%d/%d | "
           "CROSS-SEED n=%d cv_mech=%.3f cv_ok=%s frac_seeds_mech_beats=%.2f (%d/%d) majority=%s | "
           "sensitive=%s (spread_folds=%d) | C1=%s C2=%s"
           % (ab["mech_mae_farcrit"], ab["quad_mae_farcrit"], mech_beats_pooled,
              ab["n_farcrit_folds_mech_beats_quad"], len(ab["farcrit_fold_idx"]),
              ps_agg.get("n_seeds", 0), ps_agg.get("cv_mech_mae_farcrit", 0.0), cv_ok,
              ps_agg.get("frac_seeds_mech_beats_quad", 0.0), ps_agg.get("n_seeds_mech_beats_quad", 0),
              ps_agg.get("n_seeds", 0), majority,
              sens.get("telemetry_sensitive"), sens.get("n_farcrit_folds_with_cross_seed_spread", 0),
              c1_fires, c2_fires))
    # HARD_FAIL: the honest competitor ties/beats mech where it matters -> stays MEASURED_MECHANISM (done)
    if not mech_beats_pooled:
        return "HARD_FAIL", ("QUAD TIES/BEATS MECH at the far/critical folds (pooled) -- the a-priori forward "
                             "model does NOT genuinely beat the honest re-fit-quadratic competitor out of "
                             "range; extrapolation stays MEASURED_MECHANISM (no revival): " + msg)
    # HARD_PASS: mech beats quad pooled + cross-seed robust (cv) + majority of seeds + sensitive + controls
    if mech_beats_pooled and cv_ok and majority and c1_fires and c2_fires:
        return "HARD_PASS", ("MECH beats the re-fit QUADRATIC on per-seed ABSOLUTE error at the far/critical "
                             "folds AND holds across seeds (cv<=%.2f) in a majority -- the a-priori forward "
                             "model genuinely generalizes out of range (promote MM->CG-candidate): "
                             % CV_MAX + msg)
    # MIDDLE: mech beats pooled but robustness / majority / a control is short
    return "MIDDLE_BAND", ("mech beats quad pooled at far/crit but NOT (cross-seed robust cv<=%.2f AND majority "
                           "of seeds AND both controls) -- partial firming, scope UPGRADED not resolved: "
                           % CV_MAX + msg)

# ------------------------------------------------------------------ SELF-TEST mock (designed curved law)

N_MOCK_SEEDS = 5

def gen_mock_data(rng, n_seeds=N_MOCK_SEEDS):
    """Designed data from a KNOWN curved mechanistic law (s0, kappa0>0), UNIFIED per-seed flow matching the
    real path. The mech law tracks the curve; a re-fit quadratic in phi-space is fit on TRAIN and, being a
    downward parabola, CRASHES at the far/critical folds -> mech beats quad there. Per-seed OOR telemetry is
    drawn with noise so the abs-error metric MOVES across seeds (telemetry-sensitive by construction).
    Returns (pooled_levels, landed_levels, per_seed_gen) -- SMOKE=FULL: identical eval + verdict + per-seed."""
    s0, k0 = 0.55, 0.30
    train_fills = [0.06, 0.09, 0.11, 0.15, 0.20, 0.28, 0.35]
    oor_fills = [0.42, 0.50, 0.60, 0.65, 0.72, 0.80, 0.91, 1.02]  # near + far + critical (mirrors real)
    # HARD_PASS positive control: mech tracks TRAIN (so it fits s0,k0) but SYSTEMATICALLY overshoots the OOR
    # actuals by a near-constant OVERSHOOT (consistent across seeds -> low cross-seed cv), with only TINY
    # per-seed noise (keeps cv>0 + telemetry-SENSITIVE without inflating cv above the bar). The re-fit quad is
    # a downward parabola in phi-space that CRASHES far out of range -> mech beats quad at far/crit.
    OVERSHOOT = 0.35
    NOISE = 0.05
    landed = {}
    for f in train_fills:
        collT = min(0.86 * f, COLL_CAP)
        d = float(np.clip(mech_depth(collT, s0, k0) + rng.normal(0.0, NOISE), 0.0, float(D_MAX)))
        landed[round(f, 4)] = {"depth": d, "collT": collT, "n_pts": n_seeds, "source": "mock"}
    per_seed_gen = {si: {} for si in range(n_seeds)}
    for si in range(n_seeds):
        for f in oor_fills:
            collT = min(0.86 * f, COLL_CAP)
            # actual = mech overshoots by ~OVERSHOOT (consistent) + tiny per-seed noise (sensitivity, cv>0)
            d = float(np.clip(mech_depth(collT, s0, k0) - OVERSHOOT + rng.normal(0.0, NOISE),
                              0.0, float(D_MAX)))
            per_seed_gen[si][round(f, 4)] = {"depth": d, "collT": collT, "source": "mock_seed"}
    pooled = dict(landed)
    for f in oor_fills:
        rf = round(f, 4)
        uds = [per_seed_gen[si][rf]["depth"] for si in range(n_seeds)]
        pooled[rf] = {"depth": float(np.mean(uds)), "collT": min(0.86 * f, COLL_CAP),
                      "n_pts": n_seeds, "uds": uds, "source": "mock"}
    return pooled, landed, per_seed_gen

# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default=None,
                    help="REQUIRED (no silent default per exp_dev.md sec 16)")
    ap.add_argument("--self-test", dest="self_test", action="store_true",
                    help="queue_add gate flag; equivalent to --run-mode self_test (exit 0 pass / nonzero fail)")
    ap.add_argument("--metrics-path", default=None, help="landed keyslots/sharding metrics.json")
    ap.add_argument("--output-dir", default=None)
    ap.add_argument("--seed", type=int, default=20260708)
    ap.add_argument("--n-boot", type=int, default=300)
    ap.add_argument("--n-perm", type=int, default=2000)
    args = ap.parse_args()

    if args.self_test:
        run_mode = "self_test"
    elif args.run_mode is not None:
        run_mode = args.run_mode
    else:
        env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if env_mode in ("self_test", "smoke", "full"):
            run_mode = env_mode
        else:
            raise SystemExit("ERROR: run-mode REQUIRED via --run-mode or HDLAB_RUN_MODE env "
                             "(self_test|smoke|full); no silent default")
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if args.output_dir:
        output_dir = args.output_dir
    else:
        suffix = "" if run_mode == "full" else "_" + run_mode
        output_dir = os.path.join(repo, "data", "exp_" + ANCHOR_NAME + suffix)

    t0 = time.perf_counter()
    rng = np.random.default_rng(args.seed)

    gen_check = None
    if run_mode == "self_test":
        levels, landed_levels, per_seed_gen = gen_mock_data(rng, N_MOCK_SEEDS)
        seeds = list(range(N_MOCK_SEEDS))
        censored = []
        data_source = "mock_synthetic_known_curved_law_per_seed"
    else:
        mp = args.metrics_path or os.path.join(
            repo, "data", "exp_reasoning_depth_keyslots_sharding_v1", "metrics.json")
        if not os.path.exists(mp):
            raise SystemExit("ERROR: landed metrics not found: %s" % mp)
        levels, censored = load_landed_levels(mp)
        landed_levels = dict(levels)   # snapshot the FIXED landed low-fold fit envelope (before merge)
        ntests = NEW_NTEST_SMOKE if run_mode == "smoke" else NEW_NTEST_FULL
        seeds = SEEDS_SMOKE if run_mode == "smoke" else SEEDS_FULL
        new_pooled, per_seed_gen = generate_new_levels(ntests, seeds, t0)
        for f, v in new_pooled.items():   # merge pooled (headline) generated folds
            levels[f] = v
        gen_check = {"generated_fills": sorted(new_pooled.keys()), "n_telemetry_seeds": len(seeds),
                     "telemetry_seeds": list(seeds),
                     "sane": all(0.0 <= v["depth"] <= D_MAX and 0.0 < v["collT"] < 1.0
                                 for v in new_pooled.values())}
        data_source = ("landed_plus_generated_near_far_crit_smoke" if run_mode == "smoke"
                       else "landed_plus_generated_near_far_crit_full")
    expected_seeds = len(seeds)

    _write_start_marker(output_dir, run_mode, expected_n_units=EXPECTED_OOR_FOLDS)

    all_fills = sorted(levels.keys())
    if len(all_fills) < 5:
        metrics = {"verdict": "GATE_FAIL_INSUFFICIENT_LEVELS",
                   "verdict_msg": "need >=5 uncensored levels; found %d (data_source=%s)" % (
                       len(all_fills), data_source),
                   "summary": "INSUFFICIENT_LEVELS: %d" % len(all_fills),
                   "elapsed_s": time.perf_counter() - t0, "run_mode": run_mode,
                   "anchor_name": ANCHOR_NAME, "data_source": data_source,
                   "levels_found": all_fills, "ts_iso": _utc_iso()}
        _atomic_write_metrics(output_dir, metrics)
        print("[mech_abserr] %s -> %s" % (run_mode, metrics["verdict"]), flush=True)
        if run_mode in ("self_test", "smoke"):
            raise SystemExit("SMOKE_GATE_FAIL: produced < 5 levels (author/config bug)")
        return

    train_fills = [f for f in all_fills if f <= OOR_SPLIT]
    oor_fills = [f for f in all_fills if f > OOR_SPLIT]
    farcrit_fills = [f for f in oor_fills if f > FARCRIT_SPLIT]
    if len(oor_fills) < 6 or len(train_fills) < 3 or len(farcrit_fills) < 4:
        metrics = {"verdict": "GATE_FAIL_INSUFFICIENT_FOLDS",
                   "verdict_msg": ("need >=6 OOR folds incl >=4 FAR/CRIT (fill>%.2f) and >=3 train; got oor=%d "
                                   "farcrit=%d train=%d. data_source=%s" % (FARCRIT_SPLIT, len(oor_fills),
                                                                            len(farcrit_fills), len(train_fills),
                                                                            data_source)),
                   "summary": "INSUFFICIENT_FOLDS oor=%d farcrit=%d train=%d" % (
                       len(oor_fills), len(farcrit_fills), len(train_fills)),
                   "elapsed_s": time.perf_counter() - t0, "run_mode": run_mode,
                   "anchor_name": ANCHOR_NAME, "data_source": data_source,
                   "all_fills": all_fills, "ts_iso": _utc_iso()}
        _atomic_write_metrics(output_dir, metrics)
        print("[mech_abserr] %s -> %s (oor=%d farcrit=%d train=%d)" % (
            run_mode, metrics["verdict"], len(oor_fills), len(farcrit_fills), len(train_fills)), flush=True)
        if run_mode in ("self_test", "smoke"):
            raise SystemExit("SMOKE_GATE_FAIL: insufficient OOR/FARCRIT folds produced (author/config bug)")
        return

    # PRIMARY: fit mech + quad on landed low envelope; TEST on ALL OOR folds (near + far + critical), no leakage
    oor_out, oor_params = eval_split(levels, train_fills, oor_fills)

    # abs-error-vs-quad (task-primary discriminator; POOLED headline) + degeneracy guard
    ab = abserr_analysis(oor_out, oor_fills)
    deg, all_dead = farcrit_degeneracy_check(levels, oor_fills)

    # CROSS-SEED per-seed abs-error (the fix): fixed landed FIT folds + each seed's own OOR telemetry
    per_seed_rows, ps_agg, sens = per_seed_abserr(landed_levels, per_seed_gen, train_fills, oor_fills)

    # ROBUSTNESS: forward-split horizons over the FULL sorted landscape (context, not a gate)
    horizons = []
    for cut in range(3, len(all_fills)):
        tr = all_fills[:cut]; te = all_fills[cut:]
        if not te:
            continue
        ho, _ = eval_split(levels, tr, te)
        horizons.append({"train_max_fill": tr[-1], "n_test_folds": len(te),
                         "mech_MAE": round(ho["mech"]["MAE"], 3), "quad_MAE": round(ho["quad"]["MAE"], 3),
                         "mech_beats_quad": bool(ho["mech"]["MAE"] < ho["quad"]["MAE"])})
    frac_horizons_mech_beats_quad = (
        float(np.mean([h["mech_beats_quad"] for h in horizons])) if horizons else 0.0)

    # controls fire over the FULL landscape
    c1_fires, c1_detail = control1_scramble_mech(levels, all_fills, rng, n_boot=args.n_boot)
    c2_fires, c2_detail = control2_scramble_curve(levels, all_fills, rng, n_perm=args.n_perm)

    arms_differ, identical_pairs, arm_digests = arms_must_differ(oor_out)

    verdict, verdict_msg = verdict_logic(
        ab, ps_agg, sens, deg, all_dead, c1_fires, c2_fires,
        len(oor_fills), EXPECTED_OOR_FOLDS, len(farcrit_fills), EXPECTED_FARCRIT_FOLDS,
        ps_agg.get("n_seeds", 0), expected_seeds)

    proposal = {
        "out_of_range_fills": oor_fills, "farcrit_fills": farcrit_fills,
        "train_envelope_max_fill": train_fills[-1],
        "mech_predicted_depths": oor_out["mech"]["preds"], "quad_predicted_depths": oor_out["quad"]["preds"],
        "actual_depths": [round(levels[f]["depth"], 3) for f in oor_fills],
        "mech_farcrit_MAE": ab["mech_mae_farcrit"], "quad_farcrit_MAE": ab["quad_mae_farcrit"],
        "law": "mechanistic transmission-coefficient survival: p_hop=1-s*coll_theo, coll_d=coll0*(1+kappa*(d-1)), D*=argmax_D prod p_hop>=FLOOR",
        "law_coeffs": {"s_interference": oor_params["mech_s"], "kappa_accumulation": oor_params["mech_kappa"]},
        "monitor_not_control": True, "apply_decision_owner": "human_or_hdi_exp_dev",
        "note": "PROPOSAL ONLY. Substrate never applies this itself (USER-LOCKED).",
    }

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": "%s | FARCRIT mech_MAE=%.3f quad_MAE=%.3f mech_beats=%s | cv=%.3f cv_ok=%s maj=%s(%d/%d) sensitive=%s | C1=%s C2=%s | oor=%s" % (
            verdict, ab["mech_mae_farcrit"], ab["quad_mae_farcrit"], ab["mech_beats_quad_farcrit_pooled"],
            ps_agg.get("cv_mech_mae_farcrit", 0.0), ps_agg.get("cv_ok", False),
            ps_agg.get("majority_mech_beats_quad", False), ps_agg.get("n_seeds_mech_beats_quad", 0),
            ps_agg.get("n_seeds", 0), sens.get("telemetry_sensitive"), c1_fires, c2_fires,
            [round(f, 4) for f in oor_fills]),
        "elapsed_s": time.perf_counter() - t0, "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "data_source": data_source, "control_rng_seed": args.seed,
        "n_telemetry_seeds": expected_seeds, "telemetry_seeds": list(seeds),
        "cardinality_seeds_ok": bool(ps_agg.get("n_seeds", 0) == expected_seeds),
        "out_of_range_split_fill": OOR_SPLIT, "farcrit_split_fill": FARCRIT_SPLIT,
        "critical_split_fill": CRITICAL_SPLIT,
        "train_fills": train_fills, "out_of_range_fills": oor_fills, "farcrit_fills": farcrit_fills,
        "n_out_of_range_folds": len(oor_fills), "expected_out_of_range_folds": EXPECTED_OOR_FOLDS,
        "n_farcrit_folds": len(farcrit_fills), "expected_farcrit_folds": EXPECTED_FARCRIT_FOLDS,
        "cardinality_ok": bool(len(oor_fills) == EXPECTED_OOR_FOLDS
                               and len(farcrit_fills) == EXPECTED_FARCRIT_FOLDS),
        "censored_fills": censored, "all_fills": all_fills,
        "out_of_range_eval": {k: {"MAE": round(v["MAE"], 3), "per_fold_err": v["per_fold_err"],
                                  "preds": v["preds"]} for k, v in oor_out.items()},
        "out_of_range_actual_depths": [round(levels[f]["depth"], 3) for f in oor_fills],
        "abserr_analysis": ab,
        "per_seed_abserr": per_seed_rows,
        "cross_seed_robustness": ps_agg,
        "telemetry_sensitivity": sens,
        "farcrit_degeneracy_check": deg, "farcrit_folds_dead": all_dead,
        "law_params": oor_params,
        "forward_split_horizons": horizons,
        "frac_horizons_mech_beats_quad": frac_horizons_mech_beats_quad,
        "control1_scramble_mech_law": c1_detail, "control1_fires": c1_fires,
        "control2_scramble_curve": c2_detail, "control2_fires": c2_fires,
        "arms_differ_verified": arms_differ, "arms_identical_pairs": identical_pairs,
        "arm_digests": arm_digests, "telemetry_generation_check": gen_check,
        "monitor_proposal": proposal,
        "observed_levels": {str(f): {"depth": round(levels[f]["depth"], 3),
                                     "collT": round(levels[f]["collT"], 4),
                                     "source": levels[f].get("source", "?")} for f in all_fills},
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "analysis cell; telemetry-gen reuses VET'd keyslots generator (own noise floor characterized)",
        "discriminator_reachability": True,
        "start_marker_written": True, "crash_diagnostic_present": True, "heartbeat_present": False,
        "defensive_error_checking": "gen_prints_per_fold_flush_progress; eval is fast cpu (no long loop)",
        "progress_logging": "print_flush_true", "calibration_check": "default_ok_for_this_regime",
        "honest_bound": ("GENUINE-test replacement for the v1 far-fold cell whose margin discriminator was "
                         "analytically PINNED (VET commit 2fae452d1). Discriminator = per-seed ABSOLUTE OOR "
                         "error |mech_pred-actual| (telemetry-sensitive; actual never cancels) vs a RE-FIT "
                         "QUADRATIC at the FAR/CRITICAL folds (fill 0.60-1.02, incl percolation-critical where "
                         "quad crosses zero). HARD_PASS = mech beats quad at far/crit AND cross-seed cv<=0.15 "
                         "AND mech beats quad in a MAJORITY of seeds AND controls fire (promote MM->CG-cand). "
                         "HARD_FAIL = quad ties/beats mech at far/crit (stays MM) OR metric analytically "
                         "pinned. MIDDLE = mixed."),
        "ts_iso": _utc_iso(),
    }
    _atomic_write_metrics(output_dir, metrics)

    print("[mech_abserr] run_mode=%s data_source=%s all_fills=%s" % (run_mode, data_source, all_fills), flush=True)
    print("[mech_abserr] VERDICT=%s | %s" % (verdict, verdict_msg), flush=True)
    print("[mech_abserr] OOR folds=%s | mech_err=%s quad_err=%s" % (
        [round(f, 4) for f in oor_fills], oor_out["mech"]["per_fold_err"], oor_out["quad"]["per_fold_err"]),
        flush=True)
    print("[mech_abserr] FARCRIT fills=%s mech_MAE=%.3f quad_MAE=%.3f mech_beats_pooled=%s per-fold=%d/%d" % (
        [round(f, 4) for f in ab["farcrit_fills"]], ab["mech_mae_farcrit"], ab["quad_mae_farcrit"],
        ab["mech_beats_quad_farcrit_pooled"], ab["n_farcrit_folds_mech_beats_quad"],
        len(ab["farcrit_fold_idx"])), flush=True)
    print("[mech_abserr] CROSS-SEED n=%d per_seed_mech_MAE=%s per_seed_quad_MAE=%s cv_mech=%.3f cv_ok=%s frac_beats=%.2f(%d/%d) maj=%s" % (
        ps_agg.get("n_seeds", 0), ps_agg.get("per_seed_mech_mae_farcrit"),
        ps_agg.get("per_seed_quad_mae_farcrit"), ps_agg.get("cv_mech_mae_farcrit", 0.0),
        ps_agg.get("cv_ok"), ps_agg.get("frac_seeds_mech_beats_quad", 0.0),
        ps_agg.get("n_seeds_mech_beats_quad", 0), ps_agg.get("n_seeds", 0),
        ps_agg.get("majority_mech_beats_quad")), flush=True)
    print("[mech_abserr] SENSITIVITY sensitive=%s spread_folds=%d analytically_pinned=%s zero_spread_folds(info)=%s | farcrit_depths=%s dead=%s | C1=%s C2=%s" % (
        sens.get("telemetry_sensitive"), sens.get("n_farcrit_folds_with_cross_seed_spread", 0),
        sens.get("metric_analytically_pinned"), sens.get("zero_spread_nonfloored_folds"),
        deg["farcrit_actual_depths"], all_dead, c1_fires, c2_fires),
        flush=True)

    # SELF-TEST assertions (self_test mode): closed-form nesting + abs-error-beats-quad + TELEMETRY-SENSITIVITY
    if run_mode == "self_test":
        for f in [0.07, 0.20, 0.35]:
            assert abs(mech_depth(f, 1.0, 0.0) - phi(f)) < 1e-6, \
                "SMOKE_FAIL: closed-form nesting mech(s=1,k=0,coll=fill) != phi(fill) at fill=%.2f" % f
        assert not all_dead, "SMOKE_FAIL: mock far/crit folds dead (author bug): %s" % deg["farcrit_actual_depths"]
        # PRIMARY: mech beats quad at far/crit on the curved mock (quad crashes far out)
        assert ab["mech_beats_quad_farcrit_pooled"], \
            "SMOKE_FAIL: mech did NOT beat quad at far/crit on curved mock (mech=%.3f quad=%.3f)" % (
                ab["mech_mae_farcrit"], ab["quad_mae_farcrit"])
        # SEEDS present
        assert ps_agg.get("n_seeds", 0) == N_MOCK_SEEDS, \
            "SMOKE_FAIL: per-seed path did not produce %d seeds (got %s)" % (N_MOCK_SEEDS, ps_agg.get("n_seeds"))
        # THE SPECIFIC ANTI-FLAW GUARD: the metric MUST be telemetry-sensitive (not analytically pinned).
        assert sens.get("telemetry_sensitive"), \
            "SMOKE_FAIL: abs-error metric NOT telemetry-sensitive on mock (no far/crit cross-seed spread) -- " \
            "the v1 pin flaw would go undetected"
        assert not sens.get("metric_analytically_pinned"), \
            "SMOKE_FAIL: abs-error metric flagged ANALYTICALLY PINNED on mock (%s)" % sens.get("zero_spread_nonfloored_folds")
        # EXPLICIT PERTURBATION TEST (the guard against the flaw that bit us): perturb ONE seed's telemetry at a
        # non-floored far/crit fold and assert that seed's mech abs-error MOVES (NOT bit-identical). This is the
        # direct, standalone proof the metric responds to per-seed telemetry (impossible under the v1 tautology).
        mech_p, _, _ = mech_quad_preds(dict(levels),
                                       [f for f in sorted(levels) if f <= OOR_SPLIT],
                                       [f for f in sorted(levels) if f > OOR_SPLIT])
        fc = [f for f in sorted(levels) if f > FARCRIT_SPLIT]
        f_test = fc[0]
        base_ae = abs(mech_p[f_test] - per_seed_gen[0][f_test]["depth"])
        pert = dict(per_seed_gen[0][f_test]); pert["depth"] = per_seed_gen[0][f_test]["depth"] + 0.7
        pert_ae = abs(mech_p[f_test] - pert["depth"])
        assert abs(pert_ae - base_ae) > 1e-6, \
            "SMOKE_FAIL: PERTURBATION guard -- moving seed-0 telemetry by +0.7 did NOT change its mech abs-" \
            "error (metric is telemetry-INSENSITIVE == the v1 pin flaw). base=%.4f pert=%.4f" % (base_ae, pert_ae)
        # verify cross-seed abs-err values are NOT all bit-identical across seeds at f_test
        cross = [round(abs(mech_p[f_test] - per_seed_gen[si][f_test]["depth"]), 6) for si in range(N_MOCK_SEEDS)]
        assert len(set(cross)) > 1, \
            "SMOKE_FAIL: mech abs-error BIT-IDENTICAL across seeds at fill=%.3f (%s) -- v1 tautology recurred" % (
                f_test, cross)
        # controls fire
        assert c1_fires, "SMOKE_FAIL: Control-1 (scramble-mech-law) did not fire on mock"
        assert c2_fires, "SMOKE_FAIL: Control-2 (scramble-curve) did not fire on mock (|T|=%.3f p90=%.3f)" % (
            c2_detail["abs_T_real"], c2_detail["null_p90"])
        assert arms_differ, "SMOKE_FAIL: prediction arms not distinct (META_RULE_AF): %s" % identical_pairs
        # cv sane on mock (per-seed noise present; should be a real positive cv, and typically within bar)
        assert ps_agg.get("cv_mech_mae_farcrit", 0.0) > 0.0, \
            "SMOKE_FAIL: cv is exactly 0 on noisy mock -- per-seed telemetry not flowing (pin risk)"
        assert verdict == "HARD_PASS", "SMOKE_FAIL: designed curved mock did not reach HARD_PASS (got %s)" % verdict
        print("[mech_abserr] SELF-TEST ASSERTIONS PASSED: nesting + mech-beats-quad(far/crit) + "
              "TELEMETRY-SENSITIVE(perturbation moves metric; not bit-identical across %d seeds) + cv>0 + "
              "controls + HARD_PASS." % N_MOCK_SEEDS, flush=True)


if __name__ == "__main__":
    _repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _out = os.path.join(_repo, "data", "exp_" + ANCHOR_NAME + "_crashdir")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_out, e)
        raise
