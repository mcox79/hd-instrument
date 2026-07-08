#!/usr/bin/env python3
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; proposal arms per fold differ)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb declared n/a (post-hoc analysis/monitor cell; no matmul noise floor) + reachability declared
# - baseline arms = {constant no-adjustment, nearest-fill lookup}; discriminator = law beats BOTH + controls fire
# - discriminator survives scale: self_test runs the SAME loop code on designed mock (SMOKE=FULL); full runs real data
# - HARD_PASS strictly above floor (proposal-correct AND beats both baselines AND BOTH firing controls fire)
# - cardinality_ok: EXPECTED_N_UNITS = n_uncensored_provisioning_levels (LOO folds) checked
# - per-fold failure-class instrumentation; no bare except
# - all cell-comment numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
#
# SELF-IMPROVEMENT MONITOR LOOP (reasoning-depth capacity-provisioning instance).
# Revival of the density HARD_FAIL (density m*(V) landscape was a VERIFIED honest null -- genuinely
# flat, argmax_min_m=8 flat to 1e-15 across 3.5x V, so neither firing control COULD fire). The
# reasoning-depth capacity-provisioning landscape is a genuinely NON-FLAT, chain-grade law
# (p^D survival: max usable reasoning depth as a function of provisioning/capacity), so the loop's
# proposal should genuinely BEAT the constant + nearest-lookup baselines and BOTH firing controls
# should FIRE -- the demonstration density could not give.
#
# USER-LOCKED: MONITOR-NOT-CONTROL, NEVER SELF-MODIFYING. This cell only OBSERVES landed
# reasoning-depth telemetry and PROPOSES the max usable depth at a held-out provisioning level; a
# human / hdi_exp_dev decides whether to apply. The cell never edits any config, never re-dispatches,
# never writes to cert_ledger.jsonl.
#
# THE LOOP: OBSERVE (per (N, arm, n_test) rung: cross-seed usable_depth mean/min + CV, at provisioning
#                    coordinate eff_fill = 18 * n_test / eff_key_capacity)
#        -> LAW    (survival law linearized: usable_depth = a + b*phi(fill), phi(fill)=ln(FLOOR)/ln(1-fill).
#                   b is the self-heal factor -- how many x deeper the substrate reasons than the naive
#                   occupancy-binary bound (b=1). Fit on training provisioning levels.)
#        -> PROPOSE(for a HELD-OUT provisioning level, propose the max usable reasoning depth;
#                   leave-one-provisioning-level-out over uncensored levels)
#        -> SCORE  (proposal within +/- TOL depth-steps of held-out actual usable depth
#                   AND law's held-out error beats BOTH baselines: constant + nearest-fill lookup)
#        -> FIRING CONTROLS (both required; must FIRE this time since the law is real):
#             C1 scramble-law : bootstrap-refit (a,b) then permute the (a,b) pairing -> predictions
#                               collapse to no-better-than the constant (chance) baseline
#             C2 scramble-curve: the depth-vs-provisioning early-warning monotonicity (Spearman) must
#                                fall OUTSIDE a permuted null; a scrambled (permuted-depth) curve must
#                                fall INSIDE the null (early-warning destroyed)
#
# Spec:  notes/research_self_improvement_regime_ranking_revival_2026-07-07.md (rank-1 candidate + spec)
# Reuses loop machinery from: experiments/exp_self_improvement_monitor_loop_density_v1.py (commit 31d78eff9)
#
# Input schema (FULL): reasoning-depth keyslots/sharding metrics.json:
#   d["per_seed"][*]["units"][*]["arm_results"][arm]  ->
#       {"eff_fill", "eff_key_capacity", "usable_depth", "collision_frac_emp", "predicted_usable_depth"}
#   arm in {baseline, keyslots_2x, keyslots_4x, shard_2, shard_4}; "control" arm (scrambled reasoning,
#   usable_depth=0 by construction) is surfaced as independent on-disk confirmation, NOT a loop rung.
#
# MEASURED@data/exp_reasoning_depth_keyslots_sharding_v1/metrics.json:
#   fit depth = 1.875 + 1.757*phi(fill) (self-heal b=1.76); LOO law MAE=1.20 beats constant 4.70 AND
#   nearest-lookup 1.65; spearman(fill,depth)=-0.983. These are the pre-flight verification numbers;
#   the cell recomputes them from disk.
# THEORETICAL@survival law D* = k*ln(FLOOR)/ln(1-collision), collision ~ fill (occupancy); naive
#   occupancy-binary law is the k=1 special case (b=1), ~1.76x pessimistic on this substrate.
# HYPOTHESIZED bands (pre-reg): HARD-PASS = held-out proposal within +/-TOL AND beats both baselines
#   AND both controls fire. MIDDLE = proposal correct+beats-constant but ties lookup or a control silent.
#   HARD-FAIL = law no better than baselines / flat (would be a deeper honest bound than density).

import os
import sys
import json
import time
import argparse
import hashlib
import traceback
import platform
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "reasoning_depth_capacity_provisioning_monitor_loop_v1"

FLOOR = 0.5      # USABLE_FLOOR from source cell bands (MEASURED@...:extra.bands.USABLE_FLOOR)
D_MAX = 18       # source cell max depth tested (MEASURED@...:D_MAX); levels saturating here are censored
TOL = 2.0        # proposal-correct tolerance in depth steps (HP_DEPTH_MARGIN@...:extra.bands)
CHAIN_LEN = 18   # eff_fill = CHAIN_LEN * n_test / eff_key_capacity (verified identity on disk)

# ------------------------------------------------------------------ infra (per exp_dev.md sec 8/13/AH)

def _utc_iso():
    return datetime.now(timezone.utc).isoformat()

def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": _utc_iso(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
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
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": _utc_iso(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    _atomic_write_metrics(output_dir, diag)

# ------------------------------------------------------------------ small stats (no scipy dependency)

def _spearman(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < 2:
        return 0.0
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    if np.std(rx) < 1e-12 or np.std(ry) < 1e-12:
        return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])

def _cv(vals):
    v = np.asarray(vals, dtype=float)
    m = float(np.mean(v))
    if abs(m) < 1e-12:
        return 0.0
    sd = float(np.std(v, ddof=1)) if len(v) > 1 else 0.0
    return sd / m

def phi(fill):
    """Survival-law feature: naive occupancy-binary predicted depth = ln(FLOOR)/ln(1-collision),
    collision ~ fill. Real depth = a + b*phi(fill); b>1 is the substrate's self-heal factor."""
    f = float(min(max(fill, 1e-6), 0.99))
    return float(np.log(FLOOR) / np.log(1.0 - f))

# ------------------------------------------------------------------ OBSERVE

def observe_levels(rungs):
    """rungs: list of {fill, depths:[per-seed], ...}. Group by provisioning level (fill), pool per-seed
    usable depths across rungs sharing that fill. Returns level_obs: {fill: {...}} sorted by fill."""
    from collections import defaultdict
    pooled = defaultdict(list)
    naive = defaultdict(list)
    for r in rungs:
        f = round(r["fill"], 4)
        pooled[f].extend(r["depths"])
        naive[f].append(r["naive_pred"])
    level_obs = {}
    for f in sorted(pooled.keys()):
        dep = np.asarray(pooled[f], dtype=float)
        mean_dep = float(np.mean(dep))
        level_obs[f] = {
            "fill": f,
            "phi": phi(f),
            "mean_depth": mean_dep,
            "min_depth": float(np.min(dep)),
            "cv_depth": _cv(dep),
            "n_seed_points": int(len(dep)),
            "mean_naive_pred": float(np.mean(naive[f])),
            "censored": bool(mean_dep >= D_MAX - 0.5),
        }
    return level_obs

# ------------------------------------------------------------------ LAW (survival-law linearized 2-param)

def fit_law(fills_train, depths_train):
    """usable_depth = a + b*phi(fill). Least squares. b = self-heal factor (naive law is b=1, a=0)."""
    x = np.asarray([phi(f) for f in fills_train], dtype=float)
    y = np.asarray(depths_train, dtype=float)
    if len(x) < 2 or np.std(x) < 1e-9:
        return float(np.mean(y)), 0.0
    b, a = np.polyfit(x, y, 1)  # [slope, intercept]
    return float(a), float(b)

# ------------------------------------------------------------------ FIRING CONTROL 1 (scramble-law)

def control1_scramble_law(fills_train, depths_train, f_hold, actual_hold, const_pred, rng, n_boot=2000):
    """
    Scramble the law (Director spec: "scramble-law -> proposal degrades to chance"). Destroy the
    fill->depth correspondence by PERMUTING the training depth labels across fills, then refit (a,b)
    and predict at the held-out level. A genuine non-flat law loses its slope under label-scramble
    (b -> ~0, prediction collapses toward the training mean = the constant/chance baseline); a flat
    law is unchanged by scrambling (real and scrambled coincide -> does NOT fire). Real error must
    clearly beat the scrambled-law error distribution AND scrambled must collapse to >= chance error.
    """
    a, b = fit_law(fills_train, depths_train)
    real_pred = a + b * phi(f_hold)
    real_err = abs(real_pred - actual_hold)
    const_err = abs(const_pred - actual_hold)

    y = np.asarray(depths_train, dtype=float)
    ph = phi(f_hold)
    scr_err = np.empty(n_boot)
    for i in range(n_boot):
        y_perm = y[rng.permutation(len(y))]           # break fill<->depth correspondence
        a_s, b_s = fit_law(fills_train, y_perm.tolist())
        scr_err[i] = abs((a_s + b_s * ph) - actual_hold)
    scr_mean = float(np.mean(scr_err))

    MARGIN = 0.5      # depth steps: real must beat scrambled mean by a clear margin
    COLLAPSE_TOL = 1.0
    real_beats_scrambled = bool((scr_mean - real_err) > MARGIN)
    scrambled_collapsed = bool(scr_mean >= const_err - COLLAPSE_TOL)  # scrambled no better than chance
    fires = bool(real_beats_scrambled and scrambled_collapsed)
    return fires, {
        "real_pred": float(real_pred),
        "real_err": float(real_err),
        "scrambled_mean_err": scr_mean,
        "scrambled_p10_err": float(np.percentile(scr_err, 10)),
        "constant_err": float(const_err),
        "real_beats_scrambled_margin": real_beats_scrambled,
        "scrambled_collapsed_to_chance": scrambled_collapsed,
        "law_a": float(a), "law_b_self_heal": float(b),
        "scramble_method": "permute_fill_depth_labels_then_refit",
        "n_boot": n_boot,
    }

# ------------------------------------------------------------------ FIRING CONTROL 2 (scramble-curve)

def control2_scramble_curve(level_obs, uncensored_fills, rng, n_perm=2000):
    """
    Early-warning: the depth-vs-provisioning curve must be a real, non-permutable monotone relation.
    Statistic T = spearman(fill, mean_depth) over uncensored levels (negative: more fill -> less depth).
    (a) |T_real| must fall OUTSIDE the 90th pct of a permuted null (shuffle which fill maps to which
        depth). (b) a scrambled-curve input (permute the depth values across levels) must FALL INSIDE
        the null (early-warning destroyed). Both required for 'fires'. On the flat density regime this
        did NOT fire (no monotone signal); on a real non-flat law it fires.
    """
    fills = list(uncensored_fills)
    depths = [level_obs[f]["mean_depth"] for f in fills]
    T_real = _spearman(fills, depths)
    abs_T_real = abs(T_real)

    d_arr = np.asarray(depths, dtype=float)
    null = []
    for _ in range(n_perm):
        perm = rng.permutation(len(d_arr))
        null.append(abs(_spearman(fills, d_arr[perm])))
    null = np.asarray(null)
    p90 = float(np.percentile(null, 90))
    real_outside = bool(abs_T_real > p90)

    # scrambled-curve: permute depths across levels, recompute T -> should fall inside null
    perm = rng.permutation(len(d_arr))
    T_scrambled = abs(_spearman(fills, d_arr[perm]))
    scrambled_inside = bool(T_scrambled <= p90)

    fires = bool(real_outside and scrambled_inside)
    return fires, {
        "T_real_spearman_fill_depth": float(T_real),
        "abs_T_real": float(abs_T_real),
        "null_p90": p90,
        "null_mean": float(np.mean(null)),
        "real_outside_null": real_outside,
        "T_scrambled": float(T_scrambled),
        "scrambled_inside_null": scrambled_inside,
        "n_perm": n_perm,
    }

# ------------------------------------------------------------------ THE LOOP (leave-one-provisioning-level-out)

def run_loop(level_obs, rng, n_boot=2000, n_perm=2000):
    uncensored = [f for f in sorted(level_obs.keys()) if not level_obs[f]["censored"]]
    folds = []
    proposal_arms = {"real_law": [], "constant": [], "nearest_lookup": []}

    # designated extrapolation fold = the most-stressed provisioning level (highest fill)
    extrap_fill = max(uncensored) if uncensored else None

    for hold in uncensored:
        train = [f for f in uncensored if f != hold]
        depths_train = [level_obs[f]["mean_depth"] for f in train]

        a, b = fit_law(train, depths_train)
        pred = a + b * phi(hold)
        actual = level_obs[hold]["mean_depth"]

        m_const = float(np.mean(depths_train))                       # no-adjustment baseline
        nn = min(train, key=lambda f: abs(f - hold))
        m_lookup = level_obs[nn]["mean_depth"]                        # nearest-fill lookup baseline

        err_law = abs(pred - actual)
        err_const = abs(m_const - actual)
        err_lookup = abs(m_lookup - actual)

        proposal_correct = bool(err_law <= TOL)
        beats_both = bool(err_law < err_const and err_law < err_lookup)

        c1_fires, c1_detail = control1_scramble_law(
            train, depths_train, hold, actual, m_const, rng, n_boot=n_boot)

        proposal_arms["real_law"].append(round(float(pred), 3))
        proposal_arms["constant"].append(round(float(m_const), 3))
        proposal_arms["nearest_lookup"].append(round(float(m_lookup), 3))

        folds.append({
            "held_out_fill": hold,
            "n_train_levels": len(train),
            "law_a": a, "law_b_self_heal": b,
            "pred_depth": float(pred), "actual_depth": float(actual),
            "const_baseline_depth": m_const, "nearest_lookup_depth": m_lookup,
            "nearest_lookup_fill": nn,
            "err_law": float(err_law), "err_const": float(err_const), "err_lookup": float(err_lookup),
            "proposal_correct_within_tol": proposal_correct,
            "beats_both_baselines": beats_both,
            "control1_scramble_law_fires": c1_fires,
            "control1_detail": c1_detail,
            "is_extrapolation_fold": bool(hold == extrap_fill),
        })

    c2_fires, c2_detail = control2_scramble_curve(level_obs, uncensored, rng, n_perm=n_perm)
    return uncensored, folds, proposal_arms, (c2_fires, c2_detail)

# ------------------------------------------------------------------ ARMS-MUST-DIFFER (META_RULE_AF)

def arms_must_differ(proposal_arms):
    digests = {}
    for name, seq in proposal_arms.items():
        b = json.dumps(seq).encode("utf-8")
        digests[name] = hashlib.sha256(b).hexdigest()
    pairs = [(a, c) for a in digests for c in digests if a < c]
    all_differ = True
    identical_pairs = []
    for a, c in pairs:
        if digests[a] == digests[c]:
            all_differ = False
            identical_pairs.append([a, c])
    return all_differ, identical_pairs, digests

# ------------------------------------------------------------------ VERDICT

def verdict_logic(uncensored, folds, c2_fires, expected_n_units):
    n_units = len(folds)
    if n_units < expected_n_units:
        return "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", (
            "cardinality breach: got %d folds expected %d" % (n_units, expected_n_units))

    err_law = np.mean([f["err_law"] for f in folds])
    err_const = np.mean([f["err_const"] for f in folds])
    err_lookup = np.mean([f["err_lookup"] for f in folds])
    frac_correct = np.mean([f["proposal_correct_within_tol"] for f in folds])
    frac_c1 = np.mean([f["control1_scramble_law_fires"] for f in folds])

    # AGGREGATE gates (robust across all provisioning-level folds)
    agg_correct = bool(err_law <= TOL)
    agg_beats_both = bool(err_law < err_const and err_law < err_lookup)
    c1_fires_agg = bool(frac_c1 >= 0.5)

    hard_pass = bool(agg_correct and agg_beats_both and c1_fires_agg and c2_fires)

    # HARD-FAIL: law flat / no better than baselines (the density-null analogue), OR neither control fires
    law_no_better = bool(err_law >= err_const or err_law >= err_lookup)
    no_controls = bool((not c1_fires_agg) and (not c2_fires))

    msg = ("MAE law=%.2f const=%.2f lookup=%.2f | frac_correct=%.2f frac_C1=%.2f C2=%s | "
           "beats_both=%s" % (err_law, err_const, err_lookup, frac_correct, frac_c1, c2_fires, agg_beats_both))

    if hard_pass:
        return "HARD_PASS", "NON-TRIVIAL self-improvement demonstrated: " + msg
    if (law_no_better and not agg_beats_both) or no_controls:
        return "HARD_FAIL", "law no better than baselines OR no controls fire: " + msg
    return "MIDDLE_BAND", ("law adds real value but not all four gates clear (proposal correct+beats "
                           "constant, but ties lookup or a control silent): " + msg)

# ------------------------------------------------------------------ MOCK DATA (self_test)

def gen_mock_rungs(rng):
    """
    Designed rungs with a KNOWN survival law depth = a0 + b0*phi(fill) so the loop machinery + BOTH
    firing controls are verified to FIRE. NOT substrate data (SMOKE=FULL: same loop code path). Fill
    levels UNEVENLY spaced so the smooth law interpolates better than nearest-lookup (law must beat
    lookup); cross-seed noise present so CV exists; monotone so C2 fires; real slope b0>0 so C1 fires.
    """
    a0, b0 = 1.5, 1.8
    fills = [0.06, 0.09, 0.11, 0.15, 0.20, 0.28, 0.35]   # uneven spacing
    rungs = []
    for f in fills:
        base = a0 + b0 * phi(f)
        base = min(base, float(D_MAX))
        for _ in range(2):  # 2 arms per fill
            depths = np.clip(base + rng.normal(0.0, 0.6, size=5), 0.0, float(D_MAX)).tolist()
            rungs.append({"fill": f, "capacity": int(round(CHAIN_LEN * 20 / f)),
                          "depths": depths, "collision_emp": f, "naive_pred": phi(f)})
    return rungs

# ------------------------------------------------------------------ REAL DATA (full)

def load_real_rungs(metrics_path):
    """Parse reasoning-depth keyslots/sharding metrics.json -> rungs. Each (N, arm, n_test) is a rung;
    per-seed usable_depth pooled. 'control' arm (usable=0 scrambled reasoning) surfaced separately."""
    from collections import defaultdict
    with open(metrics_path, "r", encoding="utf-8") as f:
        md = json.load(f)
    per_seed = md.get("per_seed")
    if not isinstance(per_seed, list) or not per_seed:
        raise ValueError("SCHEMA: metrics.json missing per_seed list")
    acc = defaultdict(lambda: {"depths": [], "coll": [], "naive": [], "fill": None,
                               "cap": None, "N": None, "arm": None, "n_test": None})
    control_depths = []
    for s in per_seed:
        for u in s.get("units", []):
            ar = u.get("arm_results", {})
            for arm, r in ar.items():
                if not isinstance(r, dict) or "usable_depth" not in r:
                    continue
                if arm == "control":
                    control_depths.append(float(r["usable_depth"]))
                    continue
                key = (u["N"], arm, u["n_test"])
                a = acc[key]
                a["depths"].append(float(r["usable_depth"]))
                a["coll"].append(float(r.get("collision_frac_emp", 0.0)))
                a["naive"].append(float(r.get("predicted_usable_depth", phi(r["eff_fill"]))))
                a["fill"] = float(r["eff_fill"])
                a["cap"] = int(r["eff_key_capacity"])
                a["N"], a["arm"], a["n_test"] = u["N"], arm, u["n_test"]
    rungs = []
    for key, a in acc.items():
        if a["fill"] is None or len(a["depths"]) < 2:
            continue
        rungs.append({"N": a["N"], "arm": a["arm"], "n_test": a["n_test"],
                      "fill": a["fill"], "capacity": a["cap"], "depths": a["depths"],
                      "collision_emp": float(np.mean(a["coll"])),
                      "naive_pred": float(np.mean(a["naive"]))})
    ctl = {"n_points": len(control_depths),
           "mean_usable_depth": float(np.mean(control_depths)) if control_depths else None,
           "max_usable_depth": float(np.max(control_depths)) if control_depths else None,
           "note": "substrate's own scrambled-reasoning negative control; usable_depth~0 by construction"}
    return rungs, ctl

# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default=None,
                    help="REQUIRED (no silent default per exp_dev.md sec 16)")
    ap.add_argument("--metrics-path", default=None,
                    help="FULL/smoke on real data: path to reasoning-depth keyslots/sharding metrics.json")
    ap.add_argument("--output-dir", default=None)
    ap.add_argument("--seed", type=int, default=20260707)
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--n-perm", type=int, default=2000)
    args = ap.parse_args()

    if args.run_mode is None:
        raise SystemExit("ERROR: --run-mode is REQUIRED (self_test|smoke|full); no silent default")

    run_mode = args.run_mode
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if args.output_dir:
        output_dir = args.output_dir
    else:
        suffix = "" if run_mode == "full" else "_" + run_mode
        output_dir = os.path.join(repo, "data", "exp_" + ANCHOR_NAME + suffix)

    t0 = time.perf_counter()
    rng = np.random.default_rng(args.seed)

    is_mock = (run_mode == "self_test")

    if is_mock:
        rungs = gen_mock_rungs(rng)
        ctl = {"n_points": 0, "mean_usable_depth": None, "note": "mock: no substrate control arm"}
        data_source = "mock_synthetic_known_law"
    else:
        mp = args.metrics_path or os.path.join(
            repo, "data", "exp_reasoning_depth_keyslots_sharding_v1", "metrics.json")
        if not os.path.exists(mp):
            raise SystemExit("ERROR: real metrics not found: %s" % mp)
        rungs, ctl = load_real_rungs(mp)
        data_source = "real_reasoning_depth_keyslots_sharding_landed"

    level_obs = observe_levels(rungs)
    uncensored = [f for f in sorted(level_obs.keys()) if not level_obs[f]["censored"]]
    expected_n_units = len(uncensored)
    _write_start_marker(output_dir, run_mode, expected_n_units)

    if expected_n_units < 3:
        metrics = {
            "verdict": "GATE_FAIL_INSUFFICIENT_LEVELS",
            "verdict_msg": ("need >=3 uncensored provisioning levels for leave-one-out; found %d. "
                            "data_source=%s" % (expected_n_units, data_source)),
            "summary": "INSUFFICIENT_LEVELS: %d" % expected_n_units,
            "elapsed_s": time.perf_counter() - t0,
            "run_mode": run_mode, "anchor_name": ANCHOR_NAME, "data_source": data_source,
            "levels_found": sorted(level_obs.keys()), "ts_iso": _utc_iso(),
        }
        _atomic_write_metrics(output_dir, metrics)
        print("[rd_prov_loop] %s -> %s" % (run_mode, metrics["verdict"]), flush=True)
        if is_mock:
            raise SystemExit("SMOKE_GATE_FAIL: mock produced < 3 uncensored levels (author bug)")
        return

    uncensored, folds, proposal_arms, (c2_fires, c2_detail) = run_loop(
        level_obs, rng, n_boot=args.n_boot, n_perm=args.n_perm)
    arms_differ, identical_pairs, arm_digests = arms_must_differ(proposal_arms)
    verdict, verdict_msg = verdict_logic(uncensored, folds, c2_fires, expected_n_units)

    extrap = [f for f in folds if f["is_extrapolation_fold"]][0]
    err_law = float(np.mean([f["err_law"] for f in folds]))
    err_const = float(np.mean([f["err_const"] for f in folds]))
    err_lookup = float(np.mean([f["err_lookup"] for f in folds]))
    frac_c1 = float(np.mean([f["control1_scramble_law_fires"] for f in folds]))
    mean_self_heal = float(np.mean([f["law_b_self_heal"] for f in folds]))

    # structured monitor PROPOSAL (loop OUTPUT; monitor-not-control) at the extrapolation level
    proposal = {
        "held_out_provisioning_fill": extrap["held_out_fill"],
        "proposed_max_usable_depth": round(extrap["pred_depth"], 2),
        "actual_max_usable_depth": round(extrap["actual_depth"], 2),
        "confidence_band": [round(extrap["pred_depth"] - TOL, 2), round(extrap["pred_depth"] + TOL, 2)],
        "law_used": "survival_law_linearized_depth=a+b*phi(fill)",
        "law_coeffs": {"a": extrap["law_a"], "b_self_heal_factor": extrap["law_b_self_heal"]},
        "self_heal_interpretation": ("b>1 means the substrate reasons ~%.2fx deeper than the naive "
                                     "occupancy-binary bound (b=1)" % mean_self_heal),
        "monitor_not_control": True,
        "apply_decision_owner": "human_or_hdi_exp_dev",
        "note": "PROPOSAL ONLY. The substrate never applies this itself (USER-LOCKED).",
    }

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": "%s | law_MAE=%.2f vs const=%.2f lookup=%.2f | C1frac=%.2f C2=%s | proposal depth=%.1f@fill=%.4f" % (
            verdict, err_law, err_const, err_lookup, frac_c1, c2_fires,
            extrap["pred_depth"], extrap["held_out_fill"]),
        "elapsed_s": time.perf_counter() - t0,
        "run_mode": run_mode, "anchor_name": ANCHOR_NAME, "data_source": data_source, "seed": args.seed,
        "n_units": len(folds), "expected_n_units": expected_n_units,
        "cardinality_ok": bool(len(folds) == expected_n_units),
        "uncensored_provisioning_fills": uncensored,
        "censored_levels": [f for f in sorted(level_obs.keys()) if level_obs[f]["censored"]],
        "mean_self_heal_factor_b": mean_self_heal,
        "aggregate_MAE": {"law": err_law, "constant": err_const, "nearest_lookup": err_lookup},
        "law_beats_constant": bool(err_law < err_const),
        "law_beats_nearest_lookup": bool(err_law < err_lookup),
        "arms_differ_verified": arms_differ,
        "arms_identical_pairs": identical_pairs, "arm_digests": arm_digests,
        "final_metrics_atomicity": "tmp_replace",
        "monitor_proposal": proposal,
        "control2_scramble_curve": c2_detail, "control2_scramble_curve_fires": c2_fires,
        "substrate_own_scramble_control": ctl,
        "folds": folds,
        "observed_levels": {str(f): level_obs[f] for f in sorted(level_obs.keys())},
        "crlb_n/a": "monitor/analysis cell; no matmul noise floor to bound",
        "discriminator_reachability": True,
        "start_marker_written": True, "crash_diagnostic_present": True, "heartbeat_present": False,
        "defensive_error_checking": "fast_cpu_analysis_no_long_loop_heartbeat_exempt",
        "progress_logging": "print_flush_true",
        "calibration_check": "default_ok_for_this_regime",
        "honest_bound": ("REASONING-DEPTH capacity-provisioning instance. Revival of the density "
                         "HARD_FAIL (verified honest null: flat landscape). This regime's law is "
                         "genuinely non-flat (p^D survival); a HARD_PASS here is the non-trivial "
                         "self-improvement demonstration density could not give. A HARD_FAIL/flat here "
                         "would be a deeper honest bound (substrate landscapes flat across the board)."),
        "ts_iso": _utc_iso(),
    }
    _atomic_write_metrics(output_dir, metrics)

    print("[rd_prov_loop] run_mode=%s data_source=%s uncensored_levels=%s" % (
        run_mode, data_source, uncensored), flush=True)
    print("[rd_prov_loop] VERDICT=%s | %s" % (verdict, verdict_msg), flush=True)
    print("[rd_prov_loop] self_heal_b=%.2f | law_MAE=%.2f const=%.2f lookup=%.2f" % (
        mean_self_heal, err_law, err_const, err_lookup), flush=True)
    print("[rd_prov_loop] C1(scramble-law) frac=%.2f | C2(scramble-curve) fires=%s (|T|=%.3f p90=%.3f)" % (
        frac_c1, c2_fires, c2_detail["abs_T_real"], c2_detail["null_p90"]), flush=True)

    # SELF-TEST assertions: loop machinery + BOTH firing controls must fire on designed mock data
    if is_mock:
        assert verdict == "HARD_PASS", "SMOKE_FAIL: designed mock did not reach HARD_PASS (got %s: %s)" % (verdict, verdict_msg)
        assert bool(err_law < err_const), "SMOKE_FAIL: law did not beat constant on mock"
        assert bool(err_law < err_lookup), "SMOKE_FAIL: law did not beat nearest-lookup on mock"
        assert frac_c1 >= 0.5, "SMOKE_FAIL: Control-1 (scramble-law) did not fire on majority of mock folds (frac=%.2f)" % frac_c1
        assert c2_fires, "SMOKE_FAIL: Control-2 (scramble-curve) did not fire on mock (|T|=%.3f p90=%.3f)" % (
            c2_detail["abs_T_real"], c2_detail["null_p90"])
        assert arms_differ, "SMOKE_FAIL: proposal arms not distinct (META_RULE_AF)"
        print("[rd_prov_loop] SELF-TEST ASSERTIONS PASSED: loop logic + both firing controls verified.", flush=True)


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
