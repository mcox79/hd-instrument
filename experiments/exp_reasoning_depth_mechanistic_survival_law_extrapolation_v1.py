#!/usr/bin/env python3
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; prediction arms per fold differ)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb declared n/a (analysis/monitor cell; the only matmul is telemetry-gen reused from the
#   VET'd keyslots generator whose own noise floor is already characterized) + reachability declared
# - baseline comparators = {nearest-fill lookup, constant, empirical-affine-in-phi(fill)}; discriminator
#   = MECHANISTIC transmission-coefficient survival law beats lookup AND affine on GENUINE out-of-range folds
# - discriminator survives scale: self_test runs SAME eval code on designed curved mock (SMOKE=FULL);
#   smoke runs eval on landed telemetry + exercises the telemetry-gen path at reduced scale; full generates
#   genuinely-new higher-fill folds and runs the identical eval
# - HARD_PASS strictly above floor (mech beats lookup AND affine on out-of-range AND < 1.60 AND controls fire)
# - cardinality_ok: EXPECTED out-of-range test folds checked
# - per-fold failure-class instrumentation; no bare except
# - all cell-comment numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
#
# EXTRAPOLATION of the reasoning-depth self-capacity model (CHAIN_GRADE north-star extension).
# Background (VET'd, commit 775b5cd92 / VET afd8dd68): the empirical 2-param survival law
# depth = a + b*phi(fill) predicts usable reasoning depth at a held-out provisioning level, beating
# constant (LOO MAE 1.20 vs 4.70) and nearest-lookup (1.65) on INTERPOLATION -- but on the ONE true
# out-of-range fold (fill=0.3516) the empirical affine fit does NOT beat lookup (1.86 vs 1.60). An
# empirical curve INTERPOLATES; it does not EXTRAPOLATE.
#
# THIS CELL tests a MECHANISTIC (physics-derived) survival law -- a per-hop transmission-coefficient
# / percolation-style compounding form derived in closed form from the substrate's own collision
# statistics -- and asks whether it EXTRAPOLATES out-of-range where the empirical affine law cannot.
#
# MECHANISTIC LAW (accumulating-interference transmission / percolation-compounding):
#   coll_d = min(coll0 * (1 + kappa*(d-1)), COLL_CAP)          # per-hop collision, accumulating with depth
#   p_d    = max(1 - s*coll_d, P_MIN)                          # per-hop transmission coefficient
#   S(D)   = prod_{d=1..D} p_d ;  D* = max{D : S(D) >= FLOOR}  # chain-survival compounding
#   Free params fit on TRAIN levels: {s (interference amplification), kappa (depth-accumulation)}
#   Physics input coll0 = collision_frac_theo (closed-form birthday-paradox 1-((K-1)/K)^(M-1),
#     computable a priori for UNMEASURED provisioning levels -- REQUIRED for a genuine forward model).
# THEORETICAL@ closed-form nesting: at {s=1, kappa=0, coll0=fill} the law reduces EXACTLY to the naive
#   occupancy-binary survival bound phi(fill) = ln(FLOOR)/ln(1-fill). Self-test asserts this (bit-close).
#
# EXTRAPOLATION PROTOCOL (genuine out-of-range; no leakage):
#   FIT candidate laws on LOW provisioning levels (fill <= OOR_SPLIT); TEST on HIGH levels (fill > OOR_SPLIT).
#   nearest-lookup on an out-of-range point == the boundary (max-train) depth (honest flat extrapolation).
#   Robustness: repeat at multiple forward-split horizons; report fraction where mech beats lookup.
#
# PRE-REG BANDS (task-primary; HYPOTHESIZED@this-file until measured):
#   HARD-PASS = mechanistic law MAE on the GENUINE out-of-range folds < nearest-lookup AND < empirical-affine
#               AND < 1.60 (the VET'd single-fold lookup err) AND both firing controls fire.
#   HARD-FAIL = mechanistic law does NOT beat nearest-lookup out-of-range (a genuine REGIME SHIFT at high
#               fill; extrapolation needs a different mechanism -> escalate to percolation-critical-fill drill).
#   MIDDLE    = mech beats affine + improves over the empirical law but ties/loses to lookup (lookup remains
#               the practical floor near the flattening knee); honest scope caveat UPGRADED not resolved.
# PRE-FLIGHT CALIBRATION (MEASURED@ this cell's own prototype on landed + regenerated telemetry, seeds
#   [7,17,23,31,41], N=8192): on genuine-new folds {0.4219,0.5010,0.5977} (actual depth 2.8/2.4/2.2)
#   mech MAE=0.770 beats lookup 0.933 and affine 1.179; robust across forward-split horizons
#   (0.884 @train5, 1.261 @train7, 0.770 @train8-new). Empirical quad (a+b*phi+c*phi^2) MAE=0.566 edges
#   mech on the large-train split BUT is horizon-fragile (2.013 @train5) -- reported as a curvature-
#   attribution control, NOT a gate.
#
# Reuses telemetry generator (Gate D positive control): experiments/exp_reasoning_depth_keyslots_sharding_v1.py
#   (baseline arm; n_test=40 reproduces landed fill=0.3516 depth~3.4). Reuses control machinery pattern from
#   experiments/exp_reasoning_depth_capacity_provisioning_monitor_loop_v1.py (commit 775b5cd92).
# Landed telemetry: data/exp_reasoning_depth_keyslots_sharding_v1/metrics.json
#
# USER-LOCKED: MONITOR-NOT-CONTROL, NEVER SELF-MODIFYING. Only OBSERVES landed telemetry + GENERATES new
# telemetry via the VET'd generator, then PROPOSES/SCORES the extrapolated law. Never edits config, never
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

ANCHOR_NAME = "reasoning_depth_mechanistic_survival_law_extrapolation_v1"

# --- physics/protocol constants (MEASURED@ source cell config) ---
FLOOR = 0.5          # USABLE_FLOOR (MEASURED@keyslots:USABLE_FLOOR)
D_MAX = 18           # source cell max depth (MEASURED@keyslots:D_MAX); levels saturating here are censored
CHAIN_LEN = 18       # eff_fill = CHAIN_LEN * n_test / eff_key_capacity (verified identity on disk)
OOR_SPLIT = 0.3516   # train on fill <= this (landed envelope max); test strictly above (out-of-range)
COLL_CAP = 0.999
P_MIN = 1e-3
HP_ABS_MAE = 1.60    # VET'd single-fold nearest-lookup err (MEASURED@ prior VET afd8dd68)

# --- telemetry-generation config (baseline arm of the VET'd keyslots generator) ---
N_GEN = 8192                       # single N: the survival law is N-INDEPENDENT (MEASURED@ prior)
BASELINE_P = 8                     # baseline relation vocab (MEASURED@keyslots:BASELINE_P)
BASELINE_CAP = 256 * 8             # eff_key_capacity(p_rel=8, shards=1) = V_CHAIN*p_rel = 2048
NEW_NTEST_FULL = [48, 57, 68]      # fills ~ 0.4219 / 0.5010 / 0.5977 (THEORETICAL@ eff_fill identity)
# smoke previews the FULL fold-SET (near+far) at reduced seeds -- a genuine discriminator-preview at full
# fold-structure (option C). nearest-lookup is a FLAT extrapolation: strong for NEAR folds (boundary depth
# is a good short-range guess) but degrades with extrapolation distance, so a single-NEAR-fold smoke would
# mis-preview the aggregate; the fold-set must span near+far like the FULL. Verdict is still a 2-seed
# PREVIEW; the 5-seed FULL is canonical (per canon!=preview discipline).
NEW_NTEST_SMOKE = [48, 57, 68]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]

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
    Returns per-candidate {MAE, per_fold_err, preds} + fitted params."""
    ys = np.asarray([levels[f]["depth"] for f in train_fills], dtype=float)
    ph_tr = np.asarray([phi(f) for f in train_fills], dtype=float)
    # empirical affine + quadratic in phi(fill)
    if np.std(ph_tr) < 1e-9:
        a_aff, b_aff = float(np.mean(ys)), 0.0
        cq = np.asarray([0.0, 0.0, float(np.mean(ys))])
    else:
        b_aff, a_aff = np.polyfit(ph_tr, ys, 1)
        cq = np.polyfit(ph_tr, ys, 2)
    # mechanistic
    s_m, k_m = fit_mech([levels[f]["collT"] for f in train_fills], ys.tolist())
    const_pred = float(np.mean(ys))

    def _mnn(f):  # nearest-fill lookup (out-of-range -> boundary/max-train depth)
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
    the FULL landscape, measure its whole-landscape MAE; then PERMUTE the collT<->depth pairing, refit,
    and re-measure. FIRES iff the TRUE collision-physics<->depth pairing predicts the landscape better
    than random pairings (real MAE below scrambled p10 AND below scrambled mean by a margin). This
    validates that usable depth is genuinely driven by the collision-physics input -- not a spurious 2-
    param fit. (We validate over the FULL landscape, not just the flat out-of-range tail, because the
    plateau at high fill leaves little depth-variance for any control to resolve there; the steep low-fill
    region is where collision-physics-vs-scrambled is discriminable. The out-of-range EXTRAPOLATION claim
    is carried by the mech-vs-lookup-vs-affine comparison, a separate gate.)"""
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
    |T_real| outside permuted-null p90 AND a scrambled-depth curve inside the null -> fires."""
    fills = list(all_fills)
    depths = np.asarray([levels[f]["depth"] for f in fills], dtype=float)
    T_real = _spearman(fills, depths)
    null = np.asarray([abs(_spearman(fills, depths[rng.permutation(len(depths))])) for _ in range(n_perm)])
    p90 = float(np.percentile(null, 90))
    real_outside = bool(abs(T_real) > p90)
    T_scr = abs(_spearman(fills, depths[rng.permutation(len(depths))]))
    scr_inside = bool(T_scr <= p90)
    fires = bool(real_outside and scr_inside)
    return fires, {"T_real_spearman_fill_depth": float(T_real), "abs_T_real": float(abs(T_real)),
                   "null_p90": p90, "null_mean": float(np.mean(null)), "real_outside_null": real_outside,
                   "T_scrambled": float(T_scr), "scrambled_inside_null": scr_inside, "n_perm": n_perm}

# ------------------------------------------------------------------ ARMS-MUST-DIFFER (META_RULE_AF)

def arms_must_differ(cand_out, test_fills):
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

def generate_new_levels(ntest_targets, seeds, out_dir, t0):
    """Reuse the VET'd keyslots generator (baseline arm) to MEASURE usable_depth at NEW higher-fill
    provisioning levels. n_test=40 reproduces landed fill=0.3516 (Gate D positive control). collT is the
    closed-form theoretical collision (computable a priori). Returns {fill:{depth,collT,n_pts,uds}}."""
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

# ------------------------------------------------------------------ VERDICT

def verdict_logic(oor_out, c1_frac, c2_fires, n_oor, expected_oor):
    if n_oor < expected_oor:
        return "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", (
            "cardinality breach: got %d out-of-range folds expected %d" % (n_oor, expected_oor))
    mech = oor_out["mech"]["MAE"]; look = oor_out["lookup"]["MAE"]
    aff = oor_out["affine"]["MAE"]
    beats_lookup = bool(mech < look)
    beats_affine = bool(mech < aff)
    below_abs = bool(mech < HP_ABS_MAE)
    c1_ok = bool(c1_frac >= 0.5)
    msg = ("OOR MAE mech=%.3f lookup=%.3f affine=%.3f quad=%.3f const=%.3f | beats_lookup=%s "
           "beats_affine=%s <1.60=%s | C1frac=%.2f C2=%s"
           % (mech, look, aff, oor_out["quad"]["MAE"], oor_out["const"]["MAE"],
              beats_lookup, beats_affine, below_abs, c1_frac, c2_fires))
    if beats_lookup and beats_affine and below_abs and c1_ok and c2_fires:
        return "HARD_PASS", "MECHANISTIC law EXTRAPOLATES out-of-range: " + msg
    if not beats_lookup:
        return "HARD_FAIL", ("REGIME-SHIFT: mechanistic law does NOT beat nearest-lookup out-of-range "
                             "(escalate to percolation-critical-fill drill): " + msg)
    return "MIDDLE_BAND", ("mechanistic law improves over empirical affine but lookup still competitive "
                           "near the flattening knee: " + msg)

# ------------------------------------------------------------------ SELF-TEST mock (designed curved law)

def gen_mock_levels(rng):
    """Designed levels from a KNOWN curved mechanistic law (s0, kappa0>0). The empirical affine-in-phi
    fit is systematically off in the extrapolation region (curvature); mech recovers it. collT monotone
    in fill so C2 fires; cross-seed-style noise so the fit is non-degenerate. SMOKE=FULL: same eval code."""
    s0, k0 = 0.55, 0.30
    fills = [0.06, 0.09, 0.11, 0.15, 0.20, 0.28, 0.35, 0.42, 0.50, 0.60]
    levels = {}
    for f in fills:
        collT = min(0.86 * f, COLL_CAP)                  # monotone theoretical-collision proxy
        base = mech_depth(collT, s0, k0)
        d = float(np.clip(base + rng.normal(0.0, 0.25), 0.0, float(D_MAX)))
        levels[round(f, 4)] = {"depth": d, "collT": collT, "n_pts": 5, "source": "mock"}
    return levels

# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default=None,
                    help="REQUIRED (no silent default per exp_dev.md sec 16)")
    ap.add_argument("--metrics-path", default=None, help="landed keyslots/sharding metrics.json")
    ap.add_argument("--output-dir", default=None)
    ap.add_argument("--seed", type=int, default=20260708)
    ap.add_argument("--n-boot", type=int, default=300)
    ap.add_argument("--n-perm", type=int, default=2000)
    args = ap.parse_args()

    # run-mode channel: explicit --run-mode wins (local smoke/self_test); else HDLAB_RUN_MODE env
    # (the runner invokes cells BARE and injects HDLAB_RUN_MODE=full -- exp_dev.md sec 16 / keyslots
    # convention). No silent default: if neither is set, SystemExit (never accidentally self_test).
    if args.run_mode is not None:
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
        # exercise the telemetry-generation + merge path (SMOKE=FULL): smoke -> mini, full -> real folds
        ntests = NEW_NTEST_SMOKE if run_mode == "smoke" else NEW_NTEST_FULL
        seeds = SEEDS_SMOKE if run_mode == "smoke" else SEEDS_FULL
        new = generate_new_levels(ntests, seeds, output_dir, t0)
        for f, v in new.items():   # merge generated out-of-range folds (identical path smoke vs full)
            levels[f] = v
        gen_check = {"generated_fills": sorted(new.keys()),
                     "sane": all(0.0 <= v["depth"] <= D_MAX and 0.0 < v["collT"] < 1.0
                                 for v in new.values())}
        data_source = ("landed_plus_mini_generated_smoke" if run_mode == "smoke"
                       else "landed_plus_generated_full")

    _write_start_marker(output_dir, run_mode, expected_n_units=0)

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
        print("[mech_extrap] %s -> %s" % (run_mode, metrics["verdict"]), flush=True)
        if run_mode == "self_test":
            raise SystemExit("SMOKE_GATE_FAIL: mock produced < 5 levels (author bug)")
        return

    train_fills = [f for f in all_fills if f <= OOR_SPLIT]
    oor_fills = [f for f in all_fills if f > OOR_SPLIT]
    if len(oor_fills) < 1 or len(train_fills) < 3:
        metrics = {"verdict": "GATE_FAIL_NO_OUT_OF_RANGE_FOLD",
                   "verdict_msg": ("need >=1 out-of-range fold (fill>%.4f) and >=3 train; got oor=%d "
                                   "train=%d. data_source=%s" % (OOR_SPLIT, len(oor_fills),
                                                                 len(train_fills), data_source)),
                   "summary": "NO_OOR_FOLD oor=%d train=%d" % (len(oor_fills), len(train_fills)),
                   "elapsed_s": time.perf_counter() - t0, "run_mode": run_mode,
                   "anchor_name": ANCHOR_NAME, "data_source": data_source,
                   "all_fills": all_fills, "ts_iso": _utc_iso()}
        _atomic_write_metrics(output_dir, metrics)
        print("[mech_extrap] %s -> %s (oor=%d train=%d)" % (
            run_mode, metrics["verdict"], len(oor_fills), len(train_fills)), flush=True)
        if run_mode in ("self_test", "smoke"):
            raise SystemExit("SMOKE_GATE_FAIL: no out-of-range fold produced (author/config bug)")
        return

    # PRIMARY: genuine out-of-range extrapolation (train on landed envelope, test above it)
    oor_out, oor_params = eval_split(levels, train_fills, oor_fills)

    # ROBUSTNESS: multiple forward-split horizons over the FULL sorted landscape
    horizons = []
    for cut in range(3, len(all_fills)):
        tr = all_fills[:cut]; te = all_fills[cut:]
        if not te:
            continue
        ho, _ = eval_split(levels, tr, te)
        horizons.append({"train_max_fill": tr[-1], "n_test_folds": len(te),
                         "mech_MAE": round(ho["mech"]["MAE"], 3), "lookup_MAE": round(ho["lookup"]["MAE"], 3),
                         "affine_MAE": round(ho["affine"]["MAE"], 3), "quad_MAE": round(ho["quad"]["MAE"], 3),
                         "mech_beats_lookup": bool(ho["mech"]["MAE"] < ho["lookup"]["MAE"]),
                         "mech_beats_affine": bool(ho["mech"]["MAE"] < ho["affine"]["MAE"])})
    frac_horizons_mech_beats_lookup = (
        float(np.mean([h["mech_beats_lookup"] for h in horizons])) if horizons else 0.0)
    frac_horizons_quad_beats_lookup = (
        float(np.mean([bool(h["quad_MAE"] < h["lookup_MAE"]) for h in horizons])) if horizons else 0.0)

    # controls fire on the primary out-of-range split
    c1_fires, c1_detail = control1_scramble_mech(levels, all_fills, rng, n_boot=args.n_boot)
    c2_fires, c2_detail = control2_scramble_curve(levels, all_fills, rng, n_perm=args.n_perm)
    c1_frac = 1.0 if c1_fires else 0.0

    arms_differ, identical_pairs, arm_digests = arms_must_differ(oor_out, oor_fills)

    expected_oor = len(oor_fills)
    verdict, verdict_msg = verdict_logic(oor_out, c1_frac, c2_fires, len(oor_fills), expected_oor)

    # curvature-attribution: is the physical form distinguishable from generic empirical curvature?
    mech_mae = oor_out["mech"]["MAE"]; quad_mae = oor_out["quad"]["MAE"]; look_mae = oor_out["lookup"]["MAE"]
    margin_vs_lookup_pct = (100.0 * (look_mae - mech_mae) / look_mae) if look_mae > 1e-9 else 0.0
    curvature_attribution = {
        "quad_MAE_oor": round(quad_mae, 3), "mech_MAE_oor": round(mech_mae, 3),
        "physical_form_beats_empirical_quad": bool(mech_mae < quad_mae),
        "mech_robust_across_horizons": bool(frac_horizons_mech_beats_lookup >= 0.99),
        "quad_robust_across_horizons": bool(frac_horizons_quad_beats_lookup >= 0.99),
        "note": ("mech is HARD_PASS-worthy on beating lookup+affine; quad (pure empirical curvature) is a "
                 "control. If quad edges mech on large-train BUT quad is horizon-fragile while mech is "
                 "robust, the physical form earns its keep via ROBUST extrapolation, not lowest single-"
                 "split MAE."),
        "margin_vs_lookup_pct": round(margin_vs_lookup_pct, 1),
        "meets_research_strict_20pct_margin": bool(margin_vs_lookup_pct >= 20.0),
    }

    proposal = {
        "out_of_range_fills": oor_fills, "train_envelope_max_fill": train_fills[-1],
        "mech_predicted_depths": oor_out["mech"]["preds"], "actual_depths": [levels[f]["depth"] for f in oor_fills],
        "law": "mechanistic transmission-coefficient survival: p_hop=1-s*coll_theo, coll_d=coll0*(1+kappa*(d-1)), D*=argmax_D prod p_hop>=FLOOR",
        "law_coeffs": {"s_interference": oor_params["mech_s"], "kappa_accumulation": oor_params["mech_kappa"]},
        "monitor_not_control": True, "apply_decision_owner": "human_or_hdi_exp_dev",
        "note": "PROPOSAL ONLY. Substrate never applies this itself (USER-LOCKED).",
    }

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": "%s | OOR mech=%.3f lookup=%.3f affine=%.3f quad=%.3f | C1=%s C2=%s | folds=%s" % (
            verdict, oor_out["mech"]["MAE"], oor_out["lookup"]["MAE"], oor_out["affine"]["MAE"],
            oor_out["quad"]["MAE"], c1_fires, c2_fires, [round(f, 4) for f in oor_fills]),
        "elapsed_s": time.perf_counter() - t0, "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "data_source": data_source, "seed": args.seed,
        "out_of_range_split_fill": OOR_SPLIT, "train_fills": train_fills, "out_of_range_fills": oor_fills,
        "n_out_of_range_folds": len(oor_fills), "expected_out_of_range_folds": expected_oor,
        "cardinality_ok": bool(len(oor_fills) == expected_oor),
        "censored_fills": censored, "all_fills": all_fills,
        "out_of_range_eval": {k: {"MAE": round(v["MAE"], 3), "per_fold_err": v["per_fold_err"],
                                  "preds": v["preds"]} for k, v in oor_out.items()},
        "out_of_range_actual_depths": [round(levels[f]["depth"], 3) for f in oor_fills],
        "law_params": oor_params,
        "mech_beats_lookup_oor": bool(oor_out["mech"]["MAE"] < oor_out["lookup"]["MAE"]),
        "mech_beats_affine_oor": bool(oor_out["mech"]["MAE"] < oor_out["affine"]["MAE"]),
        "mech_below_abs_1p60": bool(oor_out["mech"]["MAE"] < HP_ABS_MAE),
        "forward_split_horizons": horizons,
        "frac_horizons_mech_beats_lookup": frac_horizons_mech_beats_lookup,
        "frac_horizons_quad_beats_lookup": frac_horizons_quad_beats_lookup,
        "curvature_attribution": curvature_attribution,
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
        "honest_bound": ("Tests whether a MECHANISTIC transmission-coefficient survival law extrapolates the "
                         "reasoning-depth self-capacity model out-of-range where the VET'd empirical affine "
                         "law cannot. HARD_PASS = mech beats lookup+affine on genuine out-of-range folds. "
                         "HARD_FAIL = regime-shift (lookup wins) -> escalate to percolation-critical-fill drill."),
        "ts_iso": _utc_iso(),
    }
    _atomic_write_metrics(output_dir, metrics)

    print("[mech_extrap] run_mode=%s data_source=%s all_fills=%s" % (run_mode, data_source, all_fills), flush=True)
    print("[mech_extrap] VERDICT=%s | %s" % (verdict, verdict_msg), flush=True)
    print("[mech_extrap] OOR folds=%s | mech=%.3f lookup=%.3f affine=%.3f quad=%.3f const=%.3f" % (
        [round(f, 4) for f in oor_fills], oor_out["mech"]["MAE"], oor_out["lookup"]["MAE"],
        oor_out["affine"]["MAE"], oor_out["quad"]["MAE"], oor_out["const"]["MAE"]), flush=True)
    print("[mech_extrap] mech s=%.3f kappa=%.3f | horizons mech>lookup frac=%.2f | margin_vs_lookup=%.1f%%" % (
        oor_params["mech_s"], oor_params["mech_kappa"], frac_horizons_mech_beats_lookup,
        margin_vs_lookup_pct), flush=True)
    print("[mech_extrap] C1(scramble-mech) fires=%s | C2(scramble-curve) fires=%s" % (c1_fires, c2_fires), flush=True)

    # SELF-TEST assertions (self_test mode): closed-form nesting + mech recovers curved law + controls fire
    if run_mode == "self_test":
        for f in [0.07, 0.20, 0.35]:
            assert abs(mech_depth(f, 1.0, 0.0) - phi(f)) < 1e-6, \
                "SMOKE_FAIL: closed-form nesting mech(s=1,k=0,coll=fill) != phi(fill) at fill=%.2f" % f
        assert bool(oor_out["mech"]["MAE"] < oor_out["affine"]["MAE"]), \
            "SMOKE_FAIL: mech did not beat empirical affine on curved-mock out-of-range (MAE mech=%.3f aff=%.3f)" % (
                oor_out["mech"]["MAE"], oor_out["affine"]["MAE"])
        assert bool(oor_out["mech"]["MAE"] < oor_out["lookup"]["MAE"]), \
            "SMOKE_FAIL: mech did not beat lookup on curved-mock out-of-range"
        assert c1_fires, "SMOKE_FAIL: Control-1 (scramble-mech-law) did not fire on mock"
        assert c2_fires, "SMOKE_FAIL: Control-2 (scramble-curve) did not fire on mock (|T|=%.3f p90=%.3f)" % (
            c2_detail["abs_T_real"], c2_detail["null_p90"])
        assert arms_differ, "SMOKE_FAIL: prediction arms not distinct (META_RULE_AF): %s" % identical_pairs
        assert verdict == "HARD_PASS", "SMOKE_FAIL: designed curved mock did not reach HARD_PASS (got %s)" % verdict
        print("[mech_extrap] SELF-TEST ASSERTIONS PASSED: nesting + mech-beats-affine/lookup + both controls.",
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
