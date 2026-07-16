"""PHASE BOUNDARY of the continual-retention arena: WHERE does the brain-faithful
ROUTE/selectivity cross from LOSING to WINNING vs blind keep-everything?

WHY THIS CELL EXISTS
--------------------
The VET-cleared continual-retention arena
(experiments/exp_multisource_arena_continual_retention_v1.py, VET aed29445) witnessed
HARD_FAIL_ROUTE_LOSES at moderate load (route 0.719 vs keep-everything 0.826) yet a
route WIN in a jointly high-interference corner (D=128 / N=90 / p_noise=0.6 /
mu_schema=2.2). The skunkworks VET raised TWO load-bearing corrections that this cell
resolves:
  (a) the "crossover beyond tested scale" was EXTRAPOLATED, not shown -- no tested point
      demonstrated the route winning by scaling N ALONE; the positive-control win moved
      FOUR axes at once (a joint corner, not pure N).
  (b) the native-vs-superposition comparison MIXED READOUTS (superposition = soft
      clipped-cosine partial-credit; native-exact = hard 0/1 slot-membership) -- so the
      Frontier-2 native_dominates read was a possible units artifact.

DESIGN (resolves both)
----------------------
Correction (a): SWEEP EACH REGIME AXIS SEPARATELY from a fixed MODERATE-interference
  baseline, moving ONE variable at a time, and locate the value at which the route
  reaches TIE-or-WIN:
   - AXIS N        : N in {30..1000}  (pure scale; the exact hypothesis the VET flagged)
   - AXIS p_noise  : fraction of junk items being consolidated (interference pressure)
   - AXIS D        : store dimension (crosstalk SNR ~ sqrt(D/M); lower D = more pressure)
   - AXIS rho      : key overlap (distributed crosstalk pressure)
   - AXIS gate_snr : schema-fit + recurrence separability (mu multiplier; gate quality)
   - AXIS capC_over_N : native capacity ratio C/N (native leg only -- see below)
  For each axis: the crossover value where route >= keep_everything within TIE_EPS
  (and, stricter, where route >= eng_best = max(keep_everything, decide_at_arrival)).

Correction (b): the native leg is scored under the IDENTICAL clipped-cosine retention
  metric as the distributed arms (recall_native_sameread: exact store returns the clean
  value vector v_j for a kept item -> cosine 1.0, else the zero readout -> 0.0, scored by
  the SAME num/den path as recall_superpose). No hard-0/1-vs-soft mixing. Native is
  reported SEPARATELY and never changes the route verdict.

ANTI-RIG: params are NOT tuned to make the route win. The honest phase map is reported
including "N alone never crosses" if that is the result. The arena's three controls
(confirmed_forgetting, route_can_win positive control, null_gate_guard) are re-run at
these regimes and must still fire/hold, or the map is flagged.

DELIVERABLE: the phase map per axis + the pure-N-scaling verdict + the MINIMUM
HONEST-EVALUATION REGIME (smallest N/pressure/structure at which the brain-faithful
mechanisms can be fairly evaluated -- i.e. where the test is not too-easy-to-show-value
and route/keep are actually separable).

PRE-REG BANDS (primary = route_gate_hold - keep_everything early-reliable retention)
  TIE_EPS = 0.010     (imported from the arena; tie band)
  WIN_EPS = 0.010     (route strictly above -> selectivity pays)
  A crossover on an axis = margin(route-keep) goes from < -TIE_EPS at the low-pressure
  end to >= -TIE_EPS at the high-pressure end; crossover value = first pressure value
  reaching tie-or-win. Reported vs keep_everything (task's literal question) AND vs
  eng_best (the stricter "does the HOLD beat an arrival gate too" bar = today's negative).
  HARD_PASS : a CLEAN single-axis crossover found -- route reaches WIN vs keep_everything
              (margin > WIN_EPS) at some swept value of at least one axis, monotone into
              the win => today's negatives were regime-artifacts; honest-eval regime known.
  HARD_FAIL : route NEVER reaches tie vs keep_everything on ANY single axis even at the
              swept extremes of load/scale/gate-SNR => genuine bound: selectivity does not
              pay in this substrate (report the closest approach).
  MIDDLE    : no clean single-axis crossover, BUT the jointly-rigged positive-control
              corner wins (posctrl fired) => only-joint-corner, no single-axis boundary.
  Pure-N verdict is reported SEPARATELY and explicitly: does N alone cross, or plateau?

Pure-Python (numpy only). Imports the VET-cleared arena machinery + its 3 controls; adds
only the per-axis sweep driver + the same-readout native scorer. No substrate atoms, no
torch, no queue/GPU, no origin push. Deterministic FIXED-int seeds. Local commit only.

Run:
  python experiments/exp_multisource_arena_phase_boundary_v1.py --self-test
  python experiments/exp_multisource_arena_phase_boundary_v1.py --profile smoke
  python experiments/exp_multisource_arena_phase_boundary_v1.py --profile full

CELL-TEMPLATE MANDATORY (numpy design/validity cell; queue/substrate mandates n/a):
 - except SystemExit: raise BEFORE except Exception (no BaseException)
 - no bare except; deterministic FIXED-int seeds (no hash()-derived seeds); no list(set())
 - final metrics via tmp + os.replace (atomic; META_RULE_AH tmp_replace)
 - start-marker + crash-diagnostic written
 - arms_differ: route / keep / decide / native retention vectors hashed distinct (inherited)
 - baseline_in_band: keep_everything retention in (0.05,0.95) at the baseline regime
 - discriminator survives scale: the discriminator IS the per-axis crossover; full sweep runs it
 - CRLB: crlb_n/a = "retention is a bounded recall-fidelity in [0,1]; feasibility anchored on
   heteroassoc crosstalk SNR = sqrt(D/M) (THEORETICAL); no Cramer-Rao noise floor applies"
 - real code path: the self-test EXERCISES the real sweep + same-readout native + controls
"""

import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

# ---- reuse the VET-cleared arena machinery + its 3 controls (DO NOT re-implement) ----
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import exp_multisource_arena_continual_retention_v1 as arena  # noqa: E402

make_stream = arena.make_stream
recall_superpose = arena.recall_superpose
policy_consolidate_everything = arena.policy_consolidate_everything
policy_decide_at_arrival = arena.policy_decide_at_arrival
policy_route_gate_hold = arena.policy_route_gate_hold
native_keep_set = arena.native_keep_set
early_reliable_idx = arena.early_reliable_idx
positive_control_route_can_win = arena.positive_control_route_can_win
null_gate_guard = arena.null_gate_guard

TIE_EPS = arena.TIE_EPS          # 0.010
WIN_EPS = 0.010
FORGET_MIN_DROP = arena.FORGET_MIN_DROP
E_EARLY = arena.E_EARLY

ANCHOR_NAME = "multisource_arena_phase_boundary_v1"
REPO = os.path.dirname(_HERE)
OUTPUT_DIR = os.path.join(REPO, "data", "exp_multisource_arena_phase_boundary_v1")

# ---- fixed MODERATE-interference baseline (held constant while one axis is swept) ----
# anchored to the arena FULL profile (D=256, p_noise=0.35, native_alpha=0.5) at a moderate
# rho and N where the arena witnessed the route LOSING -> room to cross.
BASE = dict(D=256, N=120, rho=0.15, p_noise=0.35, native_alpha=0.5,
            mu_schema=arena.MU_SCHEMA, mu_recur=arena.MU_RECUR)


# ============================================================================
# same-readout native (VET correction b): score the exact store THROUGH the identical
# clipped-cosine retention metric used for the distributed arms.
# ============================================================================
def recall_native_sameread(K, V, keep_set, probe_idx):
    """Exact-addressable recall scored by the SAME num/den clipped-cosine path as
    recall_superpose. yhat_j = v_j (clean value) if the item holds a slot, else the zero
    readout. So a kept item scores cosine(v_j, v_j)=1.0 and an evicted item scores 0.0 --
    identical scoring code path, no hard-0/1-vs-soft-cosine units artifact."""
    P = np.asarray(probe_idx)
    Dn = V.shape[1]
    Yhat = np.zeros((Dn, len(P)))
    for col, j in enumerate(P):
        if int(j) in keep_set:
            Yhat[:, col] = V[int(j)]
    Vp = V[P].T
    num = np.sum(Yhat * Vp, axis=0)
    den = np.linalg.norm(Yhat, axis=0) * np.linalg.norm(Vp, axis=0) + 1e-12
    return np.clip(num / den, 0.0, 1.0)


# ============================================================================
# one episode -> retention per arm, with SAME-READOUT native
# ============================================================================
def episode(D, N, rho, p_noise, native_alpha, mu_schema, mu_recur, rng, e=E_EARLY):
    """Ingest the whole stream under each policy; retention of early reliable items.
    Distributed arms use recall_superpose; native arms use recall_native_sameread (VET-b:
    identical scoring path)."""
    stream = make_stream(D, N, rho, p_noise, mu_schema, mu_recur, rng)
    probe = early_reliable_idx(stream, e)
    K, V = stream["K"], stream["V"]

    m_every = policy_consolidate_everything(stream)
    m_arr = policy_decide_at_arrival(stream)
    m_route = policy_route_gate_hold(stream)
    C = max(1, int(np.ceil(native_alpha * N)))
    keep_all = native_keep_set(stream, C, source_mask=None)
    keep_routed = native_keep_set(stream, C, source_mask=m_route)

    vecs = {
        "consolidate_everything": recall_superpose(K, V, m_every, probe),
        "decide_at_arrival_commit": recall_superpose(K, V, m_arr, probe),
        "route_gate_hold": recall_superpose(K, V, m_route, probe),
        "native_exact_all": recall_native_sameread(K, V, keep_all, probe),
        "native_exact_routed": recall_native_sameread(K, V, keep_routed, probe),
    }
    ret = {k: (float(np.mean(v)) if len(v) else 0.0) for k, v in vecs.items()}
    return ret, vecs


def episode_perseed(D, N, rho, p_noise, native_alpha, mu_schema, mu_recur, seeds, axis_id, val_key):
    """Per-seed retention per arm at one regime point (deterministic per-seed rng). Returns
    {arm: [per-seed values]} so downstream can compute the paired margin standard error."""
    accum = None
    for sd in seeds:
        rng = np.random.default_rng(sd * 100003 + axis_id * 991 + val_key * 7 + 17)
        ret, _ = episode(D, N, rho, p_noise, native_alpha, mu_schema, mu_recur, rng)
        if accum is None:
            accum = {k: [] for k in ret}
        for k in ret:
            accum[k].append(ret[k])
    return {k: list(v) for k, v in accum.items()}


def episode_mean(D, N, rho, p_noise, native_alpha, mu_schema, mu_recur, seeds, axis_id, val_key):
    """Seed-averaged retention per arm at one regime point."""
    per = episode_perseed(D, N, rho, p_noise, native_alpha, mu_schema, mu_recur,
                          seeds, axis_id, val_key)
    return {k: float(np.mean(v)) for k, v in per.items()}


# ============================================================================
# per-axis sweep + crossover detection
# ============================================================================
def _override(base, key, val):
    d = dict(base)
    d[key] = val
    return d


def sweep_axis(axis_name, param_key, values, base, seeds, axis_id, pressure_increasing):
    """Vary ONE parameter over `values` (all else = base). Returns per-point retention +
    the route margins vs keep_everything and vs eng_best. `pressure_increasing`=True means
    interference grows as the value grows; False means it grows as the value DECREASES
    (e.g. D) -- used only to order the crossover scan from low to high pressure."""
    points = []
    for vi, val in enumerate(values):
        cfg = _override(base, param_key, val)
        # gate_snr axis scales BOTH cues together (mu multiplier)
        if axis_name == "gate_snr":
            cfg = dict(base)
            cfg["mu_schema"] = arena.MU_SCHEMA * val
            cfg["mu_recur"] = arena.MU_RECUR * val
        val_key = int(round(float(val) * 1000))
        per = episode_perseed(cfg["D"], cfg["N"], cfg["rho"], cfg["p_noise"],
                              cfg["native_alpha"], cfg["mu_schema"], cfg["mu_recur"],
                              seeds, axis_id, val_key + vi)
        route_s = np.array(per["route_gate_hold"])
        keep_s = np.array(per["consolidate_everything"])
        arr_s = np.array(per["decide_at_arrival_commit"])
        eng_s = np.maximum(keep_s, arr_s)
        ret = {k: float(np.mean(v)) for k, v in per.items()}
        keep, arr, route = ret["consolidate_everything"], ret["decide_at_arrival_commit"], ret["route_gate_hold"]
        eng_best = float(np.mean(eng_s))
        n = len(seeds)
        # PAIRED margin standard error across seeds (route and keep share the seed's stream)
        margin_keep_s = route_s - keep_s
        margin_eng_s = route_s - eng_s
        se_keep = float(np.std(margin_keep_s, ddof=1) / np.sqrt(n)) if n > 1 else 0.0
        se_eng = float(np.std(margin_eng_s, ddof=1) / np.sqrt(n)) if n > 1 else 0.0
        points.append(dict(
            value=float(val), retention=ret,
            margin_vs_keep=float(route - keep), margin_vs_eng=float(route - eng_best),
            se_margin_vs_keep=se_keep, se_margin_vs_eng=se_eng,
            eng_best=float(eng_best),
            eng_best_name=("consolidate_everything" if keep >= arr else "decide_at_arrival_commit"),
            native_all=float(ret["native_exact_all"]),
        ))

    # order low->high pressure for crossover scan
    order = list(range(len(points)))
    if not pressure_increasing:
        order = order[::-1]
    scan = [points[i] for i in order]

    def crossover(margin_field, thresh, robust=False, se_field=None):
        """First point (increasing-pressure order) whose margin >= thresh AND (if robust)
        exceeds thresh by >= 2 standard errors, given the margin STARTED below -TIE_EPS AND
        STAYS at/above thresh for the rest of the (increasing-pressure) scan (a clean,
        non-reverting boundary -- not a one-point noise excursion). Returns value or None."""
        started_below = False
        for i, p in enumerate(scan):
            if p[margin_field] < -TIE_EPS:
                started_below = True
                continue
            if not started_below:
                continue
            ok = p[margin_field] >= thresh
            if robust and se_field is not None:
                ok = ok and (p[margin_field] - 2.0 * p[se_field] >= thresh)
            if ok:
                # clean boundary: all subsequent points must also be >= thresh (no revert)
                tail = scan[i:]
                if all(q[margin_field] >= thresh for q in tail):
                    return p["value"]
        return None

    xover_keep_tie = crossover("margin_vs_keep", -TIE_EPS)
    xover_keep_win = crossover("margin_vs_keep", WIN_EPS)
    xover_keep_win_robust = crossover("margin_vs_keep", WIN_EPS, robust=True, se_field="se_margin_vs_keep")
    xover_eng_tie = crossover("margin_vs_eng", -TIE_EPS)
    xover_eng_win = crossover("margin_vs_eng", WIN_EPS)
    xover_eng_win_robust = crossover("margin_vs_eng", WIN_EPS, robust=True, se_field="se_margin_vs_eng")

    best_keep = max(p["margin_vs_keep"] for p in points)
    best_eng = max(p["margin_vs_eng"] for p in points)
    # noise-floor proxy: mean paired SE over the axis (how big a seed-noise excursion looks like)
    mean_se_keep = float(np.mean([p["se_margin_vs_keep"] for p in points]))

    return dict(
        axis=axis_name, param_key=param_key, values=[float(v) for v in values],
        pressure_increasing=bool(pressure_increasing),
        points=points,
        crossover_vs_keep_tie=xover_keep_tie, crossover_vs_keep_win=xover_keep_win,
        crossover_vs_keep_win_robust=xover_keep_win_robust,
        crossover_vs_eng_tie=xover_eng_tie, crossover_vs_eng_win=xover_eng_win,
        crossover_vs_eng_win_robust=xover_eng_win_robust,
        best_margin_vs_keep=float(best_keep), best_margin_vs_eng=float(best_eng),
        mean_se_margin_vs_keep=mean_se_keep,
    )


# ============================================================================
# controls (re-run the arena's own 3) + baseline sanity
# ============================================================================
def rerun_controls(seed=11):
    pc = positive_control_route_can_win(seed)
    ng = null_gate_guard(seed)
    # confirmed_forgetting at the BASELINE regime: keep_everything must forget as N grows
    small = episode_mean(BASE["D"], 30, BASE["rho"], BASE["p_noise"], BASE["native_alpha"],
                         BASE["mu_schema"], BASE["mu_recur"], [11, 23, 37], 99, 30)
    large = episode_mean(BASE["D"], 1000, BASE["rho"], BASE["p_noise"], BASE["native_alpha"],
                         BASE["mu_schema"], BASE["mu_recur"], [11, 23, 37], 99, 1000)
    drop = small["consolidate_everything"] - large["consolidate_everything"]
    forget = dict(every_small=small["consolidate_everything"],
                  every_large=large["consolidate_everything"], drop=float(drop),
                  fired=bool(drop >= FORGET_MIN_DROP))
    return dict(positive_control_route_can_win=pc, null_gate_guard=ng,
                confirmed_forgetting=forget,
                controls_ok=bool(pc["fired"] and ng["held"] and forget["fired"]))


def _hash_vec(a):
    return hashlib.sha256(np.asarray(a, dtype=np.float64).round(6).tobytes()).hexdigest()


# ============================================================================
# metrics IO
# ============================================================================
def _atomic_write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2)
    os.replace(tmp, path)


def _write_start_marker(units, run_mode):
    _atomic_write(os.path.join(OUTPUT_DIR, "_start_marker.json"),
                  {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
                   "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": units})


def _write_crash_metrics(exc):
    _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"),
                  {"verdict": "CELL_CRASHED", "summary": "CELL_CRASHED: %s" % type(exc).__name__,
                   "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:400]),
                   "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
                   "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME})


# ============================================================================
# sweep config
# ============================================================================
def sweep_config(profile):
    if profile == "full":
        seeds = [11, 23, 37, 53, 71, 89, 101, 113, 131, 149, 167, 181,
                 199, 211, 233, 251, 271, 293, 311, 331, 353, 373, 397, 419]
        axes = [
            ("N", "N", [30, 60, 120, 250, 500, 1000], True),
            ("p_noise", "p_noise", [0.10, 0.20, 0.35, 0.50, 0.65, 0.80], True),
            ("D", "D", [1024, 512, 256, 128, 64], False),
            ("rho", "rho", [0.0, 0.15, 0.30, 0.50, 0.70], True),
            ("gate_snr", "mu_schema", [0.0, 0.5, 1.0, 1.5, 2.2, 3.0], True),
            ("capC_over_N", "native_alpha", [0.10, 0.25, 0.50, 0.75, 1.0], True),
        ]
    else:  # smoke
        seeds = [11, 23]
        axes = [
            ("N", "N", [30, 120, 500], True),
            ("p_noise", "p_noise", [0.10, 0.50, 0.80], True),
            ("D", "D", [512, 128], False),
            ("gate_snr", "mu_schema", [0.0, 1.0, 3.0], True),
        ]
    return seeds, axes


# ============================================================================
# self-test
# ============================================================================
def _run_selftests():
    fails, notes = [], []

    # ST-1 real-code-path: run a tiny 2-point sweep on the N axis; all 5 arms present.
    seeds = [11, 23]
    ax = sweep_axis("N", "N", [30, 120], BASE, seeds, axis_id=0, pressure_increasing=True)
    arms = set(ax["points"][0]["retention"].keys())
    notes.append("ST-1 real-code-path: N-axis 2pt sweep arms=%s; margins_vs_keep=%s"
                 % (sorted(arms), [round(p["margin_vs_keep"], 3) for p in ax["points"]]))
    if set(arena.ARMS) - arms:
        fails.append("ST-1: not all arms exercised (%s missing)" % (set(arena.ARMS) - arms))

    # ST-2 same-readout native is lossless AND uses the identical scoring path: a kept item
    # scores exactly 1.0; an item NOT kept scores exactly 0.0.
    rng = np.random.default_rng(5)
    s = make_stream(64, 12, 0.0, 0.0, 1.0, 0.8, rng)
    keep = {0, 1, 2}
    v = recall_native_sameread(s["K"], s["V"], keep, [0, 1, 2, 5, 7])
    notes.append("ST-2 same-readout native: kept=%s unkept=%s"
                 % ([round(x, 3) for x in v[:3]], [round(x, 3) for x in v[3:]]))
    if not (np.allclose(v[:3], 1.0) and np.allclose(v[3:], 0.0)):
        fails.append("ST-2: same-readout native not {kept=1.0, unkept=0.0} (got %s)" % v.tolist())

    # ST-3 arms differ: route / keep / decide / native retention vectors distinct at a
    # discriminating regime (high p_noise so the gate actually filters).
    rng = np.random.default_rng(9)
    _, vecs = episode(128, 90, 0.0, 0.6, 0.5, 2.2, 1.8, rng)
    key_arms = ["route_gate_hold", "consolidate_everything", "decide_at_arrival_commit",
                "native_exact_all"]
    distinct = len({_hash_vec(vecs[a]) for a in key_arms})
    notes.append("ST-3 arms_differ: distinct arm outputs = %d/4" % distinct)
    if distinct < 3:
        fails.append("ST-3: arms not distinct (%d/4)" % distinct)

    # ST-4 controls re-run (arena's own 3) fire/hold
    ctl = rerun_controls(11)
    notes.append("ST-4 controls: posctrl gap=%+.3f fired=%s | nullguard delta=%+.3f held=%s | "
                 "forget drop=%+.3f fired=%s"
                 % (ctl["positive_control_route_can_win"]["gap"],
                    ctl["positive_control_route_can_win"]["fired"],
                    ctl["null_gate_guard"]["delta"], ctl["null_gate_guard"]["held"],
                    ctl["confirmed_forgetting"]["drop"], ctl["confirmed_forgetting"]["fired"]))
    if not ctl["controls_ok"]:
        fails.append("ST-4: arena controls did not all fire/hold at these regimes")

    # ST-5 baseline in band: keep_everything retention in (0.05,0.95) at the baseline regime
    base_ret = episode_mean(BASE["D"], BASE["N"], BASE["rho"], BASE["p_noise"],
                            BASE["native_alpha"], BASE["mu_schema"], BASE["mu_recur"],
                            [11, 23, 37], 88, 120)
    kb = base_ret["consolidate_everything"]
    notes.append("ST-5 baseline_in_band: keep_everything@base=%.3f (want 0.05<.<0.95)" % kb)
    if not (0.05 < kb < 0.95):
        fails.append("ST-5: keep_everything baseline out of band (%.3f)" % kb)

    return fails, notes


# ============================================================================
# verdict
# ============================================================================
def build_verdict(profile, seeds, axis_results, controls, elapsed):
    controls_ok = controls["controls_ok"]

    # noise floor: the native-capacity axis does NOT touch route or keep_everything, so its
    # route-vs-keep margin spread is pure seed noise -> a control estimate of the noise floor.
    cap_axis = next((a for a in axis_results if a["axis"] == "capC_over_N"), None)
    if cap_axis is not None:
        cap_margins = [p["margin_vs_keep"] for p in cap_axis["points"]]
        noise_floor_span = float(max(cap_margins) - min(cap_margins))
        noise_floor_se = float(cap_axis["mean_se_margin_vs_keep"])
    else:
        noise_floor_span, noise_floor_se = None, None

    # pure-N verdict (VET correction a): does N ALONE cross ROBUSTLY (2-sigma, non-reverting)?
    n_axis = next(a for a in axis_results if a["axis"] == "N")
    pure_N_crosses_keep = n_axis["crossover_vs_keep_win_robust"] is not None
    pure_N_crosses_eng = n_axis["crossover_vs_eng_win_robust"] is not None
    n_margins = [(p["value"], p["margin_vs_keep"], p["se_margin_vs_keep"]) for p in n_axis["points"]]
    n_keep_vals = [p["margin_vs_keep"] for p in n_axis["points"]]
    n_span = max(n_keep_vals) - min(n_keep_vals)
    # jitter = the vs-keep margin oscillates (non-monotone) around zero without a clean boundary
    signs = [1 if m > TIE_EPS else -1 if m < -TIE_EPS else 0 for m in n_keep_vals]
    sign_flips = sum(1 for i in range(1, len(signs)) if signs[i] * signs[i - 1] < 0)
    pure_N_jitters = (not pure_N_crosses_keep) and sign_flips >= 2

    # single-axis ROBUST crossover (excludes the native-only capacity axis)
    route_axes = [a for a in axis_results if a["axis"] != "capC_over_N"]
    axes_cross_keep_win = [a["axis"] for a in route_axes if a["crossover_vs_keep_win_robust"] is not None]
    axes_cross_keep_tie = [a["axis"] for a in route_axes if a["crossover_vs_keep_tie"] is not None]
    axes_cross_eng_win = [a["axis"] for a in route_axes if a["crossover_vs_eng_win_robust"] is not None]
    any_keep_win = len(axes_cross_keep_win) > 0
    any_keep_tie = len(axes_cross_keep_tie) > 0

    posctrl_fired = bool(controls["positive_control_route_can_win"]["fired"])

    if not controls_ok:
        verdict = "INVALID_CONTROL"
    elif any_keep_win:
        verdict = "HARD_PASS"
    elif posctrl_fired and not any_keep_tie:
        verdict = "MIDDLE_ONLY_JOINT_CORNER"
    elif any_keep_tie:
        # reaches tie on a single axis but never a robust non-reverting win -> boundary edge
        verdict = "MIDDLE_SINGLE_AXIS_TIE_NO_ROBUST_WIN"
    else:
        verdict = "HARD_FAIL_ROUTE_NEVER_WINS"

    # minimum honest-eval regime: the smallest single-axis pressure at which route reaches
    # tie-or-win vs keep_everything (route and keep become separable in the route's favour).
    honest = None
    for a in route_axes:
        xc = a["crossover_vs_keep_win_robust"]
        if xc is not None:
            honest = honest or []
            honest.append(dict(axis=a["axis"], robust_win_value=xc,
                               tie_value=a["crossover_vs_keep_tie"]))
    if honest is None:
        honest_regime = ("NONE_ON_SINGLE_AXIS: route never ROBUSTLY (2-sigma, non-reverting) wins "
                         "vs keep_everything on any single axis at swept extremes; margin crossings "
                         "sit inside the seed-noise floor. Only the jointly-rigged corner (high "
                         "p_noise + high gate-SNR + small D together) separates them. Honest "
                         "evaluation therefore REQUIRES a multi-axis high-interference regime, not "
                         "a single-axis push.")
    else:
        honest_regime = honest

    # native (Frontier-2), same-readout, at the baseline N-axis Nmax point
    n_nmax_pt = n_axis["points"][-1]
    native_all = n_nmax_pt["native_all"]
    route_at = n_nmax_pt["retention"]["route_gate_hold"]
    eng_at = n_nmax_pt["eng_best"]
    native_dominates = (native_all - route_at > TIE_EPS) and (native_all - eng_at > TIE_EPS)

    localization = {
        "HARD_PASS": "clean_robust_single_axis_crossover_route_wins_vs_keep_todays_negatives_were_regime_artifacts",
        "MIDDLE_ONLY_JOINT_CORNER": "no_single_axis_boundary_only_joint_high_interference_corner_separates_route",
        "MIDDLE_SINGLE_AXIS_TIE_NO_ROBUST_WIN": "route_reaches_tie_on_a_single_axis_but_no_2sigma_nonreverting_win_within_noise_floor",
        "HARD_FAIL_ROUTE_NEVER_WINS": "selectivity_does_not_pay_route_never_reaches_tie_on_any_single_axis_genuine_bound",
        "INVALID_CONTROL": "arena_control_failed_map_uninterpretable",
    }[verdict]

    msg = ("profile=%s | %s | PURE-N: robust_crosses_keep=%s robust_crosses_eng=%s jitters=%s (margin_span=%.3f) "
           "| ROBUST single-axis WIN vs keep=%s ; TIE vs keep=%s ; ROBUST WIN vs eng=%s | noise_floor: span=%s se=%s "
           "| posctrl gap=%+.3f fired=%s | native_sameread@Nmax=%.3f (route=%.3f eng=%.3f dominates=%s) "
           "| forget drop=%+.3f | %s" %
           (profile, verdict, pure_N_crosses_keep, pure_N_crosses_eng, pure_N_jitters, n_span,
            axes_cross_keep_win, axes_cross_keep_tie, axes_cross_eng_win,
            ("%.3f" % noise_floor_span if noise_floor_span is not None else "na"),
            ("%.3f" % noise_floor_se if noise_floor_se is not None else "na"),
            controls["positive_control_route_can_win"]["gap"], posctrl_fired,
            native_all, route_at, eng_at, native_dominates,
            controls["confirmed_forgetting"]["drop"], localization))

    return {
        "verdict": verdict, "summary": verdict, "verdict_msg": msg,
        "elapsed_s": float(elapsed), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "profile": profile, "run_mode": profile,
        "primary_metric": "route_gate_hold_minus_keep_everything_early_reliable_retention",
        "bands": {"TIE_EPS": TIE_EPS, "WIN_EPS": WIN_EPS, "FORGET_MIN_DROP": FORGET_MIN_DROP},
        "baseline_regime": BASE,
        "seed_noise_floor": {
            "estimator": "route-vs-keep margin spread over the capC_over_N axis (native_alpha "
                         "touches neither route nor keep_everything -> pure seed noise)",
            "margin_span_vs_keep": noise_floor_span, "mean_paired_se": noise_floor_se,
        },
        "pure_N_scaling": {
            "robust_crosses_vs_keep": bool(pure_N_crosses_keep),
            "robust_crosses_vs_eng": bool(pure_N_crosses_eng),
            "jitters_around_zero": bool(pure_N_jitters),
            "sign_flips": int(sign_flips),
            "margin_span_vs_keep": float(n_span),
            "margins_by_N": [{"N": v, "margin_vs_keep": round(m, 4), "se": round(se, 4)}
                             for v, m, se in n_margins],
            "verdict": ("N_ALONE_ROBUSTLY_CROSSES" if pure_N_crosses_keep
                        else "N_ALONE_JITTERS_WITHIN_NOISE_NEVER_ROBUSTLY_CROSSES" if pure_N_jitters
                        else "N_ALONE_MOVES_BUT_NEVER_ROBUSTLY_CROSSES"),
        },
        "phase_map": [
            {
                "axis": a["axis"], "param": a["param_key"], "values": a["values"],
                "pressure_increasing": a["pressure_increasing"],
                "crossover_vs_keep_tie": a["crossover_vs_keep_tie"],
                "crossover_vs_keep_win": a["crossover_vs_keep_win"],
                "crossover_vs_keep_win_robust": a["crossover_vs_keep_win_robust"],
                "crossover_vs_eng_tie": a["crossover_vs_eng_tie"],
                "crossover_vs_eng_win": a["crossover_vs_eng_win"],
                "crossover_vs_eng_win_robust": a["crossover_vs_eng_win_robust"],
                "best_margin_vs_keep": a["best_margin_vs_keep"],
                "best_margin_vs_eng": a["best_margin_vs_eng"],
                "mean_se_margin_vs_keep": a["mean_se_margin_vs_keep"],
                "points": [{"value": p["value"],
                            "route": round(p["retention"]["route_gate_hold"], 4),
                            "keep_everything": round(p["retention"]["consolidate_everything"], 4),
                            "decide_at_arrival": round(p["retention"]["decide_at_arrival_commit"], 4),
                            "native_sameread": round(p["native_all"], 4),
                            "margin_vs_keep": round(p["margin_vs_keep"], 4),
                            "se_margin_vs_keep": round(p["se_margin_vs_keep"], 4),
                            "margin_vs_eng": round(p["margin_vs_eng"], 4),
                            "se_margin_vs_eng": round(p["se_margin_vs_eng"], 4)}
                           for p in a["points"]],
            }
            for a in axis_results
        ],
        "minimum_honest_eval_regime": honest_regime,
        "frontier2_native_sameread": {
            "note": "native scored under the IDENTICAL clipped-cosine metric as distributed arms (VET-b resolved)",
            "native_sameread_at_Nmax": float(native_all),
            "route_at_Nmax": float(route_at), "eng_best_at_Nmax": float(eng_at),
            "native_dominates_both": bool(native_dominates),
        },
        "controls": controls,
        "localization": localization,
        "crlb_n/a": ("retention is a bounded recall-fidelity in [0,1]; feasibility anchored on "
                     "heteroassoc crosstalk SNR = sqrt(D/M) (THEORETICAL); no Cramer-Rao floor applies"),
    }


# ============================================================================
# main
# ============================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--profile", choices=["smoke", "full"], default="full")
    args = ap.parse_args()
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    t0 = time.perf_counter()

    if args.self_test:
        _write_start_marker(1, "self_test")
        fails, notes = _run_selftests()
        print("=== PHASE-BOUNDARY CELL SELF-TESTS ===")
        for n in notes:
            print("  " + n, flush=True)
        if fails:
            print("SELF-TEST FAILED:")
            for f in fails:
                print("  FAIL: " + f)
            _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"),
                          {"verdict": "SELFTEST_FAIL", "summary": "SELFTEST_FAIL",
                           "verdict_msg": "; ".join(fails),
                           "elapsed_s": time.perf_counter() - t0, "anchor_name": ANCHOR_NAME})
            return 2
        print("SELFTEST_PASS: real sweep code path + same-readout native lossless + arms differ + "
              "arena controls fire/hold + baseline in band")
        return 0

    profile = args.profile
    seeds, axes = sweep_config(profile)
    n_units = sum(len(vals) for _, _, vals, _ in axes) * len(seeds)
    _write_start_marker(n_units, profile)
    print("=== PHASE BOUNDARY profile=%s seeds=%s base=%s ===" % (profile, seeds, BASE), flush=True)

    controls = rerun_controls(11)
    print("  CONTROLS: posctrl gap=%+.3f fired=%s | nullguard delta=%+.3f held=%s | forget drop=%+.3f fired=%s"
          % (controls["positive_control_route_can_win"]["gap"],
             controls["positive_control_route_can_win"]["fired"],
             controls["null_gate_guard"]["delta"], controls["null_gate_guard"]["held"],
             controls["confirmed_forgetting"]["drop"], controls["confirmed_forgetting"]["fired"]), flush=True)

    axis_results = []
    for axis_id, (axis_name, param_key, values, pincr) in enumerate(axes):
        r = sweep_axis(axis_name, param_key, values, BASE, seeds, axis_id, pincr)
        axis_results.append(r)
        print("  AXIS %-12s | robust-win(route>keep)@%s tie@%s | robust-win(route>eng)@%s | best_m_vs_keep=%+.3f mean_se=%.3f"
              % (axis_name, r["crossover_vs_keep_win_robust"], r["crossover_vs_keep_tie"],
                 r["crossover_vs_eng_win_robust"], r["best_margin_vs_keep"],
                 r["mean_se_margin_vs_keep"]), flush=True)

    out = build_verdict(profile, seeds, axis_results, controls, time.perf_counter() - t0)
    _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"), out)

    print("\n" + "=" * 80)
    print("PHASE MAP -- primary = route_gate_hold - keep_everything early-reliable retention")
    nf = out["seed_noise_floor"]
    print("  SEED-NOISE FLOOR (capC axis control): margin_span=%s mean_paired_se=%s"
          % (nf["margin_span_vs_keep"], nf["mean_paired_se"]))
    for a in out["phase_map"]:
        print("\n  AXIS %s (%s), pressure_increasing=%s" % (a["axis"], a["param"], a["pressure_increasing"]))
        print("    %-10s %-8s %-8s %-8s %-12s %-10s" %
              ("value", "route", "keep", "decide", "m_vs_keep(se)", "m_vs_eng"))
        for p in a["points"]:
            print("    %-10s %-8.3f %-8.3f %-8.3f %+.3f(%.3f)  %+-10.3f" %
                  (p["value"], p["route"], p["keep_everything"], p["decide_at_arrival"],
                   p["margin_vs_keep"], p["se_margin_vs_keep"], p["margin_vs_eng"]))
        print("    ROBUST-win vs keep@%s (tie@%s) | ROBUST-win vs eng@%s | best m_vs_keep=%+.3f mean_se=%.3f"
              % (a["crossover_vs_keep_win_robust"], a["crossover_vs_keep_tie"],
                 a["crossover_vs_eng_win_robust"], a["best_margin_vs_keep"], a["mean_se_margin_vs_keep"]))

    pn = out["pure_N_scaling"]
    print("\n  PURE-N VERDICT: %s (robust_crosses_keep=%s robust_crosses_eng=%s jitters=%s sign_flips=%d span=%.3f)"
          % (pn["verdict"], pn["robust_crosses_vs_keep"], pn["robust_crosses_vs_eng"],
             pn["jitters_around_zero"], pn["sign_flips"], pn["margin_span_vs_keep"]))
    print("  MIN HONEST-EVAL REGIME: %s" % (out["minimum_honest_eval_regime"]))
    f2 = out["frontier2_native_sameread"]
    print("  FRONTIER-2 native (same-readout): native@Nmax=%.3f route=%.3f eng=%.3f dominates=%s"
          % (f2["native_sameread_at_Nmax"], f2["route_at_Nmax"], f2["eng_best_at_Nmax"],
             f2["native_dominates_both"]))
    print("\nTOP-LEVEL VERDICT: %s" % out["verdict"])
    print("  " + out["verdict_msg"])
    print("=" * 80)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit
        _write_crash_metrics(e)
        raise
    sys.exit(rc)
