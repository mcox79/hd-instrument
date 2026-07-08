#!/usr/bin/env python3
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; prediction arms per fold differ)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb declared n/a (analysis/monitor cell; only matmul is telemetry-gen reused from the VET'd keyslots
#   generator whose own noise floor is already characterized) + reachability declared
# - discriminator = the MECH-vs-LOOKUP per-fold MARGIN (lookup_err - mech_err) GROWS with extrapolation
#   distance; the far-fold aggregate margin exceeds the near-fold aggregate margin
# - discriminator survives scale: self_test runs SAME eval code on a designed curved mock (SMOKE=FULL);
#   smoke runs eval on landed telemetry + generates the FULL far-fold set at reduced seeds; full generates
#   the far folds at full seeds and runs the identical margin-growth eval
# - HARD_PASS strictly above floor (far-margin > near-margin AND mech beats lookup at EVERY far fold AND
#   monotone-growing margin AND both firing controls fire)
# - cardinality_ok: EXPECTED out-of-range + far test folds checked
# - per-fold failure-class instrumentation; no bare except
# - all cell-comment numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
#
# ENVELOPE-PUSH of the VET'd mechanistic reasoning-depth extrapolation
# (base cell: experiments/exp_reasoning_depth_mechanistic_survival_law_extrapolation_v1.py, commit
# ae4dae37a; VET'd MEASURED_MECHANISM). VET finding (2026-07-08): the mechanistic transmission-coefficient
# survival law beats nearest-lookup out-of-range by a MODEST +17.5% margin, and that win is FAR-FOLD-DRIVEN:
# on the NEAREST OOR fold (fill=0.4219) flat lookup actually BEATS mech (the boundary depth is a good
# short-range guess), but mech wins on the 2 FAR folds (0.5010, 0.5977) because a flat lookup DEGRADES with
# extrapolation distance while the a-priori physics law does not. The physics law's edge = ROBUSTNESS across
# horizons.  MEASURED@ base-cell prior VET (per director backup 2026-07-08): nearest-fold lookup-beats-mech;
# far-fold mech-beats-lookup; aggregate margin_vs_lookup ~ +17.5%.
#
# THE HYPOTHESIS (this cell): if the win is FAR-FOLD-DRIVEN, then extending to EVEN FURTHER out-of-range folds
# (fill ~0.65 / 0.72 / 0.80, well beyond the landed 0.60 max) should INCREASE the mech-vs-lookup margin --
# lookup keeps degrading with distance; the a-priori physics law does not. A GROWING margin at longer range
# firms the extrapolation from "modest MM" toward a stronger result AND is the honest test of whether the
# forward-model genuinely generalizes or merely got lucky on 2 folds.
#
# MECHANISTIC LAW (unchanged from base; accumulating-interference transmission / percolation-compounding):
#   coll_d = min(coll0 * (1 + kappa*(d-1)), COLL_CAP)          # per-hop collision, accumulating with depth
#   p_d    = max(1 - s*coll_d, P_MIN)                          # per-hop transmission coefficient
#   S(D)   = prod_{d=1..D} p_d ;  D* = max{D : S(D) >= FLOOR}  # chain-survival compounding
#   Free params fit on TRAIN levels (fill <= OOR_SPLIT): {s, kappa}. Physics input coll0 = closed-form
#   birthday-paradox collision, computable a priori for UNMEASURED provisioning -- a genuine forward model.
# THEORETICAL@ closed-form nesting: at {s=1, kappa=0, coll0=fill} the law reduces EXACTLY to the naive
#   occupancy-binary survival bound phi(fill) = ln(FLOOR)/ln(1-fill). Self-test asserts this (bit-close).
#
# CLEAN FORWARD-SPLIT (no leakage): FIT the mech law + all comparator laws on the LOW landed folds
#   (fill <= OOR_SPLIT=0.3516) ONLY; TEST on ALL out-of-range folds (near 0.42/0.50/0.60 + FAR 0.65/0.72/0.80).
#   nearest-lookup on an out-of-range point == the boundary (max-train) depth (honest flat extrapolation).
#   Per-fold margin m(f) = lookup_err(f) - mech_err(f) (positive => mech better). The far-fold telemetry is
#   MEASURED with the VET'd generator; collT is closed-form a-priori. No test-fold value touches any fit.
#
# PRE-REG BANDS (task-primary; HYPOTHESIZED@this-file until measured):
#   HARD-PASS = margin GROWS with distance: mean far-margin > mean near-margin AND mech beats lookup at EVERY
#               far fold (per-fold margin > 0) AND monotone (spearman(fill, margin) > 0 over all OOR folds)
#               AND both firing controls fire. => the a-priori forward model genuinely generalizes.
#   HARD-FAIL = margin does NOT grow (mean far-margin <= mean near-margin) OR mech ties/loses lookup at any
#               far fold (per-fold margin <= 0). => the +17.5% win was 2-fold luck (honest deflation);
#               escalate to a percolation-critical-fill regime-shift drill.
#   MIDDLE    = margin grows AND all far folds positive but not strictly monotone, or controls don't both
#               fire -- partial firming, scope UPGRADED not resolved.
#   GATE_FAIL = far-fold telemetry DEGENERATE (usable-depth hits the 0-floor at all far folds -> no signal).
#
# PRE-FLIGHT DEGENERACY GUARD: usable_depth() returns 0 when even d=1 is below FLOOR. At high fill the chain
#   can collapse to the floor. Smoke MEASURES the far-fold depths and GATE_FAILs if all far folds are
#   floored (dead telemetry cannot carry a margin-growth test). MEASURED@ smoke run of this cell.
#
# Reuses telemetry generator (Gate D positive control): experiments/exp_reasoning_depth_keyslots_sharding_v1.py
#   (baseline arm; the same generator VET'd for the base cell). Landed telemetry:
#   data/exp_reasoning_depth_keyslots_sharding_v1/metrics.json (low folds for the fit; envelope max 0.3516).
#
# USER-LOCKED: MONITOR-NOT-CONTROL, NEVER SELF-MODIFYING. Only OBSERVES landed telemetry + GENERATES new
# telemetry via the VET'd generator, then SCORES the margin-growth hypothesis. Never edits config, never
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

ANCHOR_NAME = "reasoning_depth_mech_survival_farfold_extrapolation_v1"

# --- physics/protocol constants (MEASURED@ source cell config) ---
FLOOR = 0.5          # USABLE_FLOOR (MEASURED@keyslots:USABLE_FLOOR)
D_MAX = 18           # source cell max depth (MEASURED@keyslots:D_MAX); levels saturating here are censored
CHAIN_LEN = 18       # eff_fill = CHAIN_LEN * n_test / eff_key_capacity (verified identity on disk)
OOR_SPLIT = 0.3516   # FIT on fill <= this (landed envelope max); TEST strictly above (out-of-range)
NEAR_FAR_SPLIT = 0.62  # OOR folds with fill <= this = NEAR (0.42/0.50/0.60); > this = FAR (0.65/0.72/0.80)
COLL_CAP = 0.999
P_MIN = 1e-3

# --- telemetry-generation config (baseline arm of the VET'd keyslots generator) ---
N_GEN = 8192                       # single N: the survival law is N-INDEPENDENT (MEASURED@ prior)
BASELINE_P = 8                     # baseline relation vocab (MEASURED@keyslots:BASELINE_P)
BASELINE_CAP = 256 * 8             # eff_key_capacity(p_rel=8, shards=1) = V_CHAIN*p_rel = 2048
# n_test -> eff_fill = n_test*18/2048 (THEORETICAL@ eff_fill identity, verified on disk):
#   NEAR (already in base cell): 48->0.4219, 57->0.5010, 68->0.5977
#   FAR  (this envelope-push):   74->0.6504, 82->0.7207, 91->0.7998
NEW_NTEST_FULL = [48, 57, 68, 74, 82, 91]   # near + far, generated in ONE self-consistent run
NEW_NTEST_SMOKE = [48, 57, 68, 74, 82, 91]  # full fold structure (near+far) at reduced seeds (option C preview)
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]

# EXPECTED_N_UNITS declaration (META_RULE_H): 6 folds generated x n_seeds. Verdict counts OOR folds.
EXPECTED_OOR_FOLDS = 6   # all 6 generated fills are > OOR_SPLIT=0.3516

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
    Returns per-candidate {MAE, per_fold_err, preds} + fitted params. Fit touches ONLY train_fills."""
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

# ------------------------------------------------------------------ FIRING CONTROL 1 (scramble mech-law)

def control1_scramble_mech(levels, all_fills, rng, n_boot=500):
    """MECHANISM-IS-REAL control (full-landscape collision-physics scramble). Fit the MECHANISTIC law on
    the FULL landscape, measure its whole-landscape MAE; then PERMUTE the collT<->depth pairing, refit, and
    re-measure. FIRES iff the TRUE collision-physics<->depth pairing predicts the landscape better than
    random pairings (real MAE below scrambled p10 AND below scrambled mean by a margin)."""
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
    FIRES iff (a) |T_real| is outside the permuted-null p90 (the real monotone relation is significant)
    AND (b) scrambling DESTROYS the signal by a robust margin: |T_real| exceeds the scrambled-null MEAN by
    MARGIN. NOTE: the base cell gated on a SINGLE fresh scrambled draw being inside p90 -- but the null is
    itself built from scrambled draws, so ~10% of fresh draws exceed their own p90 by construction, giving a
    ~10% flaky false-non-fire with zero discriminating value. This robust null-mean margin replaces that
    coin-flip; T_scrambled is still reported for transparency but no longer gates."""
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
    provisioning levels (near + far). collT is the closed-form theoretical collision (computable a priori).
    Returns {fill:{depth,collT,n_pts,uds}}."""
    os.environ.setdefault("HDLAB_RUN_MODE", "full")
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if repo not in sys.path:
        sys.path.insert(0, repo)
    import experiments.exp_reasoning_depth_keyslots_sharding_v1 as KS  # lazy: only when generating

    V_CODE = KS.V_CODE; P_REL_MAX = KS.P_REL_MAX
    DEPTHS = list(range(1, D_MAX + 1))
    base_arm = {"label": "baseline", "p_rel": BASELINE_P, "shards": 1, "shuffle": False, "reuse_base": True}
    assert KS.eff_key_capacity(BASELINE_P, 1) == BASELINE_CAP, "keyslots capacity drift (Gate D)"

    levels = {}
    total = len(ntest_targets) * len(seeds)
    done = 0
    for nt in ntest_targets:
        uds = []; ths = []; fill = None
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
            ud = KS.usable_depth(curve, DEPTHS, FLOOR)
            theo = KS.theoretical_collision_frac(cec, BASELINE_CAP)
            fill = KS.eff_fill(nt, D_MAX, BASELINE_P, 1)
            uds.append(int(ud)); ths.append(float(theo))
            done += 1
            print("[gen] n_test=%d seed=%d fill=%.4f ud=%d collT=%.4f d1=%.3f (%d/%d, %.1fs)"
                  % (nt, sd, fill, ud, theo, curve[1], done, total, time.perf_counter() - t0), flush=True)
        f = round(float(fill), 4)
        levels[f] = {"depth": float(np.mean(uds)), "collT": float(np.mean(ths)),
                     "n_pts": len(uds), "uds": uds, "source": "generated"}
    return levels

# ------------------------------------------------------------------ MARGIN-GROWTH ANALYSIS (task-primary)

def margin_growth_analysis(oor_out, oor_fills):
    """Per-fold margin m(f) = lookup_err(f) - mech_err(f) (positive => mech beats lookup). Split OOR folds
    into NEAR (<= NEAR_FAR_SPLIT) and FAR (> NEAR_FAR_SPLIT). The far-fold-driven hypothesis predicts the
    margin GROWS with extrapolation distance: mean far-margin > mean near-margin, all far folds positive,
    and a positive monotone trend spearman(fill, margin)."""
    mech_err = oor_out["mech"]["per_fold_err"]
    look_err = oor_out["lookup"]["per_fold_err"]
    margins = [round(float(look_err[i]) - float(mech_err[i]), 4) for i in range(len(oor_fills))]
    near_i = [i for i, f in enumerate(oor_fills) if f <= NEAR_FAR_SPLIT]
    far_i = [i for i, f in enumerate(oor_fills) if f > NEAR_FAR_SPLIT]
    near_m = [margins[i] for i in near_i]
    far_m = [margins[i] for i in far_i]
    near_mean = float(np.mean(near_m)) if near_m else float("nan")
    far_mean = float(np.mean(far_m)) if far_m else float("nan")
    all_far_positive = bool(len(far_m) > 0 and all(m > 0.0 for m in far_m))
    margin_grows = bool(len(far_m) > 0 and len(near_m) > 0 and far_mean > near_mean)
    spear_margin = _spearman(oor_fills, margins)
    monotone_grows = bool(spear_margin > 0.0)
    return {
        "per_fold_margin_lookupErr_minus_mechErr": margins,
        "near_fold_idx": near_i, "far_fold_idx": far_i,
        "near_fills": [oor_fills[i] for i in near_i], "far_fills": [oor_fills[i] for i in far_i],
        "near_margin_mean": round(near_mean, 4), "far_margin_mean": round(far_mean, 4),
        "far_minus_near_margin": round(far_mean - near_mean, 4) if far_m and near_m else None,
        "all_far_folds_mech_beats_lookup": all_far_positive,
        "margin_grows_far_gt_near": margin_grows,
        "spearman_fill_margin": round(float(spear_margin), 4),
        "monotone_growing_margin": monotone_grows,
        "near_far_split_fill": NEAR_FAR_SPLIT,
    }

# ------------------------------------------------------------------ DEGENERACY GUARD (far telemetry alive)

def far_degeneracy_check(levels, oor_fills):
    """usable_depth() -> 0 when d=1 is below FLOOR. Far folds can collapse to the 0-floor. Dead far
    telemetry (all far folds floored) cannot carry the margin-growth test -> GATE_FAIL. MEASURED@ this run."""
    far_fills = [f for f in oor_fills if f > NEAR_FAR_SPLIT]
    far_depths = [levels[f]["depth"] for f in far_fills]
    n_floored = int(sum(1 for d in far_depths if d < 1.0))
    all_floored = bool(len(far_fills) > 0 and n_floored == len(far_fills))
    return {
        "far_fills": far_fills, "far_actual_depths": [round(d, 3) for d in far_depths],
        "n_far_floored_below_1": n_floored, "n_far_folds": len(far_fills),
        "all_far_folds_floored": all_floored,
        "far_depth_std": round(float(np.std(far_depths)), 4) if far_depths else None,
    }, all_floored

# ------------------------------------------------------------------ VERDICT

def verdict_logic(mg, deg, far_floored, c1_frac, c2_fires, n_oor, expected_oor):
    if n_oor < expected_oor:
        return "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", (
            "cardinality breach: got %d out-of-range folds expected %d" % (n_oor, expected_oor))
    if far_floored:
        return "GATE_FAIL_FAR_FOLDS_FLOORED", (
            "far-fold telemetry DEGENERATE: all far folds usable_depth < 1 (floored); "
            "margin-growth hypothesis untestable on dead telemetry. far_depths=%s"
            % deg["far_actual_depths"])
    grows = mg["margin_grows_far_gt_near"]
    all_far_pos = mg["all_far_folds_mech_beats_lookup"]
    monotone = mg["monotone_growing_margin"]
    c1_ok = bool(c1_frac >= 0.5)
    msg = ("far_margin=%.3f near_margin=%.3f (far-near=%s) | all_far_beat_lookup=%s grows=%s monotone=%s "
           "spearman=%.3f | C1=%s C2=%s"
           % (mg["far_margin_mean"], mg["near_margin_mean"], mg["far_minus_near_margin"],
              all_far_pos, grows, monotone, mg["spearman_fill_margin"], c1_ok, c2_fires))
    # HARD_FAIL: the far-fold win was luck -- margin does not grow OR mech ties/loses at a far fold
    if (not grows) or (not all_far_pos):
        return "HARD_FAIL", ("FAR-FOLD WIN WAS 2-FOLD LUCK: margin does NOT grow with distance / mech "
                             "ties-or-loses lookup further out (escalate to percolation-critical-fill "
                             "regime-shift drill): " + msg)
    # HARD_PASS: growing margin + every far fold positive + monotone + both controls
    if grows and all_far_pos and monotone and c1_ok and c2_fires:
        return "HARD_PASS", ("MECH-vs-LOOKUP MARGIN GROWS with extrapolation distance -- a-priori forward "
                             "model genuinely generalizes further out-of-range: " + msg)
    return "MIDDLE_BAND", ("margin grows AND all far folds beat lookup but not strictly monotone OR a "
                           "control did not fire -- partial firming, scope UPGRADED not resolved: " + msg)

# ------------------------------------------------------------------ SELF-TEST mock (designed curved law)

def gen_mock_levels(rng):
    """Designed levels from a KNOWN curved mechanistic law (s0, kappa0>0). Flat nearest-lookup extrapolates
    the boundary depth as a CONSTANT, so lookup_err GROWS monotonically with fill while the mech law tracks
    the curve -> the mech-vs-lookup margin grows with distance (the far-fold-driven signature). Includes
    NEAR (0.42/0.50/0.60) and FAR (0.65/0.72/0.80) OOR folds. SMOKE=FULL: same eval + verdict code."""
    s0, k0 = 0.55, 0.30
    fills = [0.06, 0.09, 0.11, 0.15, 0.20, 0.28, 0.35, 0.42, 0.50, 0.60, 0.65, 0.72, 0.80]
    levels = {}
    for f in fills:
        collT = min(0.86 * f, COLL_CAP)                  # monotone theoretical-collision proxy
        base = mech_depth(collT, s0, k0)
        d = float(np.clip(base + rng.normal(0.0, 0.15), 0.0, float(D_MAX)))
        levels[round(f, 4)] = {"depth": d, "collT": collT, "n_pts": 5, "source": "mock"}
    return levels

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
        levels = gen_mock_levels(rng)
        censored = []
        data_source = "mock_synthetic_known_curved_law"
    else:
        mp = args.metrics_path or os.path.join(
            repo, "data", "exp_reasoning_depth_keyslots_sharding_v1", "metrics.json")
        if not os.path.exists(mp):
            raise SystemExit("ERROR: landed metrics not found: %s" % mp)
        levels, censored = load_landed_levels(mp)
        ntests = NEW_NTEST_SMOKE if run_mode == "smoke" else NEW_NTEST_FULL
        seeds = SEEDS_SMOKE if run_mode == "smoke" else SEEDS_FULL
        new = generate_new_levels(ntests, seeds, t0)
        for f, v in new.items():
            levels[f] = v
        gen_check = {"generated_fills": sorted(new.keys()),
                     "sane": all(0.0 <= v["depth"] <= D_MAX and 0.0 < v["collT"] < 1.0
                                 for v in new.values())}
        data_source = ("landed_plus_generated_near_far_smoke" if run_mode == "smoke"
                       else "landed_plus_generated_near_far_full")

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
        print("[mech_farfold] %s -> %s" % (run_mode, metrics["verdict"]), flush=True)
        if run_mode in ("self_test", "smoke"):
            raise SystemExit("SMOKE_GATE_FAIL: produced < 5 levels (author/config bug)")
        return

    train_fills = [f for f in all_fills if f <= OOR_SPLIT]
    oor_fills = [f for f in all_fills if f > OOR_SPLIT]
    far_fills = [f for f in oor_fills if f > NEAR_FAR_SPLIT]
    if len(oor_fills) < 4 or len(train_fills) < 3 or len(far_fills) < 2:
        metrics = {"verdict": "GATE_FAIL_INSUFFICIENT_FOLDS",
                   "verdict_msg": ("need >=4 OOR folds incl >=2 FAR (fill>%.2f) and >=3 train; got oor=%d "
                                   "far=%d train=%d. data_source=%s" % (NEAR_FAR_SPLIT, len(oor_fills),
                                                                        len(far_fills), len(train_fills),
                                                                        data_source)),
                   "summary": "INSUFFICIENT_FOLDS oor=%d far=%d train=%d" % (
                       len(oor_fills), len(far_fills), len(train_fills)),
                   "elapsed_s": time.perf_counter() - t0, "run_mode": run_mode,
                   "anchor_name": ANCHOR_NAME, "data_source": data_source,
                   "all_fills": all_fills, "ts_iso": _utc_iso()}
        _atomic_write_metrics(output_dir, metrics)
        print("[mech_farfold] %s -> %s (oor=%d far=%d train=%d)" % (
            run_mode, metrics["verdict"], len(oor_fills), len(far_fills), len(train_fills)), flush=True)
        if run_mode in ("self_test", "smoke"):
            raise SystemExit("SMOKE_GATE_FAIL: insufficient OOR/FAR folds produced (author/config bug)")
        return

    # PRIMARY: fit on landed low envelope; TEST on ALL OOR folds (near + far), no leakage
    oor_out, oor_params = eval_split(levels, train_fills, oor_fills)

    # margin-growth (task-primary discriminator) + degeneracy guard
    mg = margin_growth_analysis(oor_out, oor_fills)
    deg, far_floored = far_degeneracy_check(levels, oor_fills)

    # ROBUSTNESS: forward-split horizons over the FULL sorted landscape (context, not a gate)
    horizons = []
    for cut in range(3, len(all_fills)):
        tr = all_fills[:cut]; te = all_fills[cut:]
        if not te:
            continue
        ho, _ = eval_split(levels, tr, te)
        horizons.append({"train_max_fill": tr[-1], "n_test_folds": len(te),
                         "mech_MAE": round(ho["mech"]["MAE"], 3), "lookup_MAE": round(ho["lookup"]["MAE"], 3),
                         "mech_beats_lookup": bool(ho["mech"]["MAE"] < ho["lookup"]["MAE"])})
    frac_horizons_mech_beats_lookup = (
        float(np.mean([h["mech_beats_lookup"] for h in horizons])) if horizons else 0.0)

    # controls fire over the FULL landscape
    c1_fires, c1_detail = control1_scramble_mech(levels, all_fills, rng, n_boot=args.n_boot)
    c2_fires, c2_detail = control2_scramble_curve(levels, all_fills, rng, n_perm=args.n_perm)
    c1_frac = 1.0 if c1_fires else 0.0

    arms_differ, identical_pairs, arm_digests = arms_must_differ(oor_out)

    verdict, verdict_msg = verdict_logic(mg, deg, far_floored, c1_frac, c2_fires,
                                         len(oor_fills), EXPECTED_OOR_FOLDS)

    proposal = {
        "out_of_range_fills": oor_fills, "near_fills": mg["near_fills"], "far_fills": mg["far_fills"],
        "train_envelope_max_fill": train_fills[-1],
        "mech_predicted_depths": oor_out["mech"]["preds"],
        "actual_depths": [round(levels[f]["depth"], 3) for f in oor_fills],
        "per_fold_margin": mg["per_fold_margin_lookupErr_minus_mechErr"],
        "law": "mechanistic transmission-coefficient survival: p_hop=1-s*coll_theo, coll_d=coll0*(1+kappa*(d-1)), D*=argmax_D prod p_hop>=FLOOR",
        "law_coeffs": {"s_interference": oor_params["mech_s"], "kappa_accumulation": oor_params["mech_kappa"]},
        "monitor_not_control": True, "apply_decision_owner": "human_or_hdi_exp_dev",
        "note": "PROPOSAL ONLY. Substrate never applies this itself (USER-LOCKED).",
    }

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": "%s | far_margin=%.3f near_margin=%.3f grows=%s all_far_beat=%s monotone=%s | C1=%s C2=%s | oor=%s" % (
            verdict, mg["far_margin_mean"], mg["near_margin_mean"], mg["margin_grows_far_gt_near"],
            mg["all_far_folds_mech_beats_lookup"], mg["monotone_growing_margin"], c1_fires, c2_fires,
            [round(f, 4) for f in oor_fills]),
        "elapsed_s": time.perf_counter() - t0, "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "data_source": data_source, "seed": args.seed,
        "out_of_range_split_fill": OOR_SPLIT, "near_far_split_fill": NEAR_FAR_SPLIT,
        "train_fills": train_fills, "out_of_range_fills": oor_fills, "far_fills": far_fills,
        "n_out_of_range_folds": len(oor_fills), "expected_out_of_range_folds": EXPECTED_OOR_FOLDS,
        "cardinality_ok": bool(len(oor_fills) == EXPECTED_OOR_FOLDS),
        "censored_fills": censored, "all_fills": all_fills,
        "out_of_range_eval": {k: {"MAE": round(v["MAE"], 3), "per_fold_err": v["per_fold_err"],
                                  "preds": v["preds"]} for k, v in oor_out.items()},
        "out_of_range_actual_depths": [round(levels[f]["depth"], 3) for f in oor_fills],
        "margin_growth_analysis": mg,
        "far_degeneracy_check": deg, "far_folds_floored": far_floored,
        "law_params": oor_params,
        "forward_split_horizons": horizons,
        "frac_horizons_mech_beats_lookup": frac_horizons_mech_beats_lookup,
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
        "honest_bound": ("Envelope-push of the VET'd mechanistic reasoning-depth extrapolation. Tests whether "
                         "the mech-vs-nearest-lookup MARGIN GROWS at further-out-of-range folds (fill 0.65/"
                         "0.72/0.80). HARD_PASS = far-margin > near-margin AND every far fold beats lookup AND "
                         "monotone-growing margin AND controls fire (a-priori forward model generalizes). "
                         "HARD_FAIL = margin does not grow / mech ties-or-loses far out (the +17.5% win was "
                         "2-fold luck) -> escalate to percolation-critical-fill drill."),
        "ts_iso": _utc_iso(),
    }
    _atomic_write_metrics(output_dir, metrics)

    print("[mech_farfold] run_mode=%s data_source=%s all_fills=%s" % (run_mode, data_source, all_fills), flush=True)
    print("[mech_farfold] VERDICT=%s | %s" % (verdict, verdict_msg), flush=True)
    print("[mech_farfold] OOR folds=%s | mech_err=%s lookup_err=%s margin=%s" % (
        [round(f, 4) for f in oor_fills], oor_out["mech"]["per_fold_err"], oor_out["lookup"]["per_fold_err"],
        mg["per_fold_margin_lookupErr_minus_mechErr"]), flush=True)
    print("[mech_farfold] near_margin=%.3f far_margin=%.3f (far-near=%s) grows=%s all_far_beat=%s monotone=%s spearman=%.3f" % (
        mg["near_margin_mean"], mg["far_margin_mean"], mg["far_minus_near_margin"],
        mg["margin_grows_far_gt_near"], mg["all_far_folds_mech_beats_lookup"],
        mg["monotone_growing_margin"], mg["spearman_fill_margin"]), flush=True)
    print("[mech_farfold] far_depths=%s floored=%s | C1=%s C2=%s" % (
        deg["far_actual_depths"], far_floored, c1_fires, c2_fires), flush=True)

    # SELF-TEST assertions (self_test mode): closed-form nesting + margin-growth signature + controls fire
    if run_mode == "self_test":
        for f in [0.07, 0.20, 0.35]:
            assert abs(mech_depth(f, 1.0, 0.0) - phi(f)) < 1e-6, \
                "SMOKE_FAIL: closed-form nesting mech(s=1,k=0,coll=fill) != phi(fill) at fill=%.2f" % f
        assert not far_floored, "SMOKE_FAIL: mock far folds floored (author bug): %s" % deg["far_actual_depths"]
        assert mg["margin_grows_far_gt_near"], \
            "SMOKE_FAIL: margin did NOT grow on curved mock (far=%.3f near=%.3f)" % (
                mg["far_margin_mean"], mg["near_margin_mean"])
        assert mg["all_far_folds_mech_beats_lookup"], \
            "SMOKE_FAIL: mech did not beat lookup at every far fold on mock (margins=%s)" % (
                mg["per_fold_margin_lookupErr_minus_mechErr"])
        assert mg["monotone_growing_margin"], \
            "SMOKE_FAIL: margin not monotone-growing on mock (spearman=%.3f)" % mg["spearman_fill_margin"]
        assert c1_fires, "SMOKE_FAIL: Control-1 (scramble-mech-law) did not fire on mock"
        assert c2_fires, "SMOKE_FAIL: Control-2 (scramble-curve) did not fire on mock (|T|=%.3f p90=%.3f)" % (
            c2_detail["abs_T_real"], c2_detail["null_p90"])
        assert arms_differ, "SMOKE_FAIL: prediction arms not distinct (META_RULE_AF): %s" % identical_pairs
        assert verdict == "HARD_PASS", "SMOKE_FAIL: designed curved mock did not reach HARD_PASS (got %s)" % verdict
        print("[mech_farfold] SELF-TEST ASSERTIONS PASSED: nesting + margin-grows + all-far-beat + monotone + controls.",
              flush=True)


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
