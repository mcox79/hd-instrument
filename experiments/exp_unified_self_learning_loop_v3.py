"""UNIFIED SELF-LEARNING LOOP v3 -- does reading teach NEW (low-pretraining-exposure) concepts?

v2 (unified_self_learning_loop_v2, MIDDLE_BAND) validated the loop MECHANISM (sleep fires every cycle,
comprehension real, controls clean, retention holds) BUT reading added NO SUSTAINED gain: the brain-
faithful arms did not beat plain-averaging's wash-out on the AGGREGATE held-out set. The likely reason:
v2's held-out concepts were pretraining-SATURATED (median ~655 mentions in the 237M-token ARC corpus) --
the encoder already KNEW them, so there was nothing to learn. The BRAIN learns from NOVELTY.

v3 tests the CORRECT question: on concepts the encoder does NOT already know well (LOW pretraining
exposure), does reading produce a SUSTAINED capability gain? It REUSES the v2 loop machinery verbatim
(encoder comprehension engine, clarify FLAG, precision-weighted Kalman consolidation + coverage-aware
OVERRIDE gate, the leak-proof relational probe, the 3 loop-integrity controls) and adds ONE thing:
EXPOSURE-STRATIFIED per-slice AUC. Reading is held CONSTANT across concepts (every held concept reads
the SAME number of mentions per cycle); the only variable is PRETRAINING EXPOSURE (ARC mention count).

STRATIFICATION (the v3 core, per task CONTRACT item 1): held concepts are split into terciles by their
ARC mention count `counts[ci]` (the pretraining-exposure proxy): LOW (bottom, under-known), MID, HIGH
(top, v2-saturated), plus ALL (= reproduces v2's aggregate curve). Per-slice AUC is computed by calling
the v2 relational probe with a SUB-SPLIT whose held_idx is restricted to the slice, SHARING the same
train_eval negative pool (task REUSE INSIGHT). KEY = SUSTAINED gain on the LOW slice.

CONSOLIDATION (task CONTRACT item 3): precision-weighted KALMAN (the best-motivated v2 brain-faithful
arm) + coverage-aware OVERRIDE gate, vs a PLAIN-averaging baseline. Common-mode / CA3 are DROPPED (task:
"NOT common-mode/CA3") to focus the test on precision-vs-plain on novel concepts.

THE BAR (FULL; pre-registered): MAIN_precision on the LOW slice produces SUSTAINED knowledge_gain
(LOW gain > +0.02 AND final within WASHOUT_EPS of the LOW peak = no wash-out) AND LOW gain exceeds HIGH
gain (reading teaches the NEW concept more than the already-known one) -- while keeping sleep-fires-every-
cycle + controls-below-main + retention-held(LOW) + comprehension-real + leak-proof (all validated in v2).
HARD_PASS = the substrate LEARNS NEW concepts from reading. HARD_FAIL (LOW slice flat/negative) => reading
does NOT teach even novel concepts by encoder-averaging => points to loop-v4 (a FAST EPISODIC store; see
notes/research_fast_concept_learning_informs_selflearning_loop_2026-07-27.md). DEFLATE on a null: report
per-slice power (n_query), reading amount (mentions/concept), and gain magnitude -- the why-autopsy.

BRAIN-FAITHFUL / INVARIANTS: TEACHER-FREE; NO borrowed vectors (OUR trained encoder only); GLASS-BOX
(symbolic gates + precision Kalman + coverage override; no external LLM / no autograd at inference);
LEAK-PROOF (predicted edge disjoint from read text; probe negatives degree-matched, adjacency excluded).
ASCII-only. Deterministic seeds. Store writes LOCAL-ONLY + UNCOMMITTED. Agent-reported VET-PENDING.

FULL loads the scale-v2 checkpoint (data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_<seed>.pt) as
the comprehension engine via --ckpt; SMOKE trains a tiny fresh encoder and validates the MECHANISM (the
across-cycle capability GAIN on real concepts is FULL-deferred -- a tiny encoder is below the signal
threshold where mention reps concentrate; v2 MEASURED negative gain on tiny). The SMOKE discriminator is
that the EXPOSURE-STRATIFIED probe FIRES: >=2 slices with sufficient queries and monotone exposure ranges,
plus sleep/comprehension/controls/clarify all firing (all smoke-able on tiny).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scale/floor):
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - final_metrics_atomicity: tmp_replace (os.replace)
# - crash-diagnostic metrics + start-marker + heartbeat
# - arms_differ_verified at smoke gate (NO_READ==READ_NO_SLEEP store exempted: both freeze cycle-0)
# - discriminator (SMOKE) = stratified probe fires (>=2 slices, monotone exposure) + sleep/comprehension/
#     controls/clarify fire (all on tiny); (FULL) = LOW-slice sustained gain (real ckpt; path B analytical)
# - deterministic seeding (fixed ints + default_rng; no hash()/list(set()) ordering)
# - progress_logging: print_flush_true
# - self-test constructs REAL objects (encoder, clarify, learner MDL, Kalman, override, per-slice probe)
# - all reported numbers MEASURED@ this cell's metrics.json
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import sys
import json
import time
import argparse
import hashlib
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_scale_meaning_learn_arc_heldout_v2 as V2
import experiments.exp_unified_self_learning_loop_v2 as LOOP2
from hdlab.clarify_gate import ClarifyGate, GateOutcome

ANCHOR_NAME = "unified_self_learning_loop_v3"

# ---- arms: PLAIN baseline + precision (best v2 brain-faithful) + 3 loop-integrity controls -----------
# spec = (name, do_read, do_sleep, scramble, consolidation_mode). NO common-mode / NO ca3 (task item 3).
ARM_SPECS = [
    ("MAIN_plainavg", True, True, False, "plain"),
    ("MAIN_precision", True, True, False, "precision"),
    ("NO_READ", False, True, False, "precision"),
    ("SCRAMBLED", True, True, True, "precision"),
    ("READ_NO_SLEEP", True, False, False, "precision"),
]
ARMS = [s[0] for s in ARM_SPECS]
ARM_SPEC = {s[0]: dict(read=s[1], sleep=s[2], scramble=s[3], mode=s[4]) for s in ARM_SPECS}
MAIN_MODE_ARMS = ["MAIN_plainavg", "MAIN_precision"]
PLAIN_ARM = "MAIN_plainavg"
PRECISION_ARM = "MAIN_precision"
NOREAD_ARM = "NO_READ"
SCRAM_ARM = "SCRAMBLED"
NOSLEEP_ARM = "READ_NO_SLEEP"
CONTROL_ARMS = [NOREAD_ARM, SCRAM_ARM, NOSLEEP_ARM]

TEXT_KEY = V2.TEXT_ARM          # "ARM_RAW_TEXT"  -- text-alone relational AUC (the loop's readout)
RAW_KEY = V2.RAW_ARM
SH_KEY = V2.SHUFFLE_ARM

# exposure slice names (terciles of ARC mention count among the well-covered held concepts) + ALL
SLICES = ["LOW", "MID", "HIGH", "ALL"]
KEY_SLICE = "LOW"               # the pre-registered slice the BAR is on
SAT_SLICE = "HIGH"              # the v2-saturated contrast slice

# ---------------------------------------------------------------------------
# Config profiles. Base on the v2 loop configs; override the loop schedule so LOW-exposure concepts
# QUALIFY (small mentions/cycle * n_cycles => low `need` floor => concepts with few ARC mentions read),
# and reading is MATCHED across slices (every held concept reads the same count). Drop CM/CA3 knobs.
# ---------------------------------------------------------------------------
def _base_cfg(src):
    cfg = dict(src)
    # v3 uses only plain + precision + override; keep the consol defaults that those paths read.
    return cfg

SELFTEST_CFG = _base_cfg(LOOP2.SELFTEST_CFG)
SELFTEST_CFG.update(run_mode="selftest", n_cycles=3, mentions_per_cycle=2,
                    min_evidence_mentions=2, clarify_min_evidence=6)

SMOKE_CFG = _base_cfg(LOOP2.SMOKE_CFG)
SMOKE_CFG.update(
    run_mode="smoke",
    min_mentions_eval=12, heldout_count=250,
    n_cycles=3, mentions_per_cycle=4, min_evidence_mentions=4, clarify_min_evidence=12,
)

FULL_CFG = _base_cfg(LOOP2.FULL_CFG)
FULL_CFG.update(
    run_mode="full",
    min_mentions_eval=20, heldout_count=800,
    # reading MATCHED + SMALL so LOW-exposure concepts (ARC count ~20-80) qualify: need = 5*4 = 20.
    n_cycles=5, mentions_per_cycle=4, min_evidence_mentions=4, clarify_min_evidence=20,
    gain_margin_hp=0.02,
)

# HARD-PASS bands (FULL). Pre-registered.
HP_GAIN_MARGIN = 0.02          # LOW-slice MAIN_precision AUC[final]-AUC[0] must EXCEED this
WASHOUT_EPS = 0.01             # "sustained" = LOW final within this of the LOW peak (no wash-out)
CONTRAST_EPS = 0.0             # LOW gain must exceed HIGH gain by > this (reading teaches NEW > known)
HP_CONTROL_SEP = 0.0           # best MAIN[final] must exceed each control[final] by > this (LOW slice)
RETENTION_EPS = 0.02           # LOW MAIN_precision AUC may never drop below AUC[0]-eps (no forgetting)
MIN_QUERY_TASKS = 40           # LOW-slice relational power floor (SMOKE relaxed to 8)
SMOKE_POWER_FLOOR = 8


def _out_dir(run_mode):
    suffix = {"selftest": "_selftest", "smoke": "_smoke", "full": ""}.get(run_mode, "")
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME + suffix)
    os.makedirs(d, exist_ok=True)
    return d


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now():
    return datetime.now(timezone.utc).isoformat()


def _fmt(x):
    return ("%.4f" % x) if isinstance(x, (int, float)) else str(x)


def _write_start_marker(out_dir, run_mode, expected_units):
    marker = dict(pid=os.getpid(), ts_iso=_now(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_units)
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(out_dir, "_start_marker.json"))


def _heartbeat(out_dir, unit_idx, total_units, elapsed_s, extra=None):
    row = dict(ts_iso=_now(), unit_idx=int(unit_idx), total_units=int(total_units),
               elapsed_s=round(float(elapsed_s), 2))
    if extra:
        row["extra"] = extra
    with open(os.path.join(out_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


# ===========================================================================
# EXPOSURE STRATIFICATION: split well-covered held concepts into terciles by
# ARC mention count (the pretraining-exposure proxy). Deterministic (stable sort
# with concept-id tiebreak; no list(set()) ordering).
# ===========================================================================
def _build_slices(held, counts):
    order = sorted(held, key=lambda ci: (int(counts[ci]), int(ci)))
    n = len(order)
    a = n // 3
    b = (2 * n) // 3
    slc = {"LOW": sorted(order[:a]), "MID": sorted(order[a:b]),
           "HIGH": sorted(order[b:]), "ALL": sorted(held)}
    meta = {}
    for name in SLICES:
        idxs = slc[name]
        c = np.array([int(counts[ci]) for ci in idxs], dtype=np.int64) if idxs else np.array([0])
        meta[name] = dict(n_concepts=len(idxs),
                          exposure_min=int(c.min()), exposure_median=float(np.median(c)),
                          exposure_max=int(c.max()))
    return slc, meta


# ===========================================================================
# PER-SLICE relational probe: reuse V2.relational_eval with a SUB-SPLIT whose
# held_idx is the slice, SHARING the train_eval negative pool (task REUSE INSIGHT).
# ===========================================================================
def _probe_stratified(store, base_text, ground, counts, universe, split, slices,
                      adj, deg, n_shards, seed):
    text = LOOP2._store_to_text_matrix(store, base_text)
    out = {}
    for name in SLICES:
        idxs = slices[name]
        if not idxs:
            out[name] = dict(auc=None, n_query=0, raw=None, shuffle=None)
            continue
        sub = dict(split)
        sub["held_idx"] = np.array(sorted(idxs), dtype=np.int64)
        rel = V2.relational_eval(ground, text, counts, universe, sub, adj, deg, n_shards, seed, 0.5)
        out[name] = dict(auc=rel.get(TEXT_KEY), n_query=rel.get("_n_query"),
                         raw=rel.get(RAW_KEY), shuffle=rel.get(SH_KEY))
    return out


# ===========================================================================
# ONE ARM: run the full cycle loop, producing PER-SLICE AUC curves. Reuses every
# v2 loop helper (encode, scramble, clarify FLAG, precision/plain SLEEP+override).
# ===========================================================================
def _run_arm(arm, held, slices, postings, model, tok, spec, cfg, device, out_dir,
             ground, counts, universe, split, adj, deg, n_shards, seed, base_text, base_clean):
    a = ARM_SPEC[arm]
    do_read, do_sleep, scramble, mode = a["read"], a["sleep"], a["scramble"], a["mode"]
    gate = ClarifyGate()
    store = {}
    kal_rep, kal_prec, committed_conf = {}, {}, {}
    acc_reps = {ci: [] for ci in held}
    n_cycles = cfg["n_cycles"]
    m = cfg["mentions_per_cycle"]
    # per-slice AUC curves + per-slice n_query curves
    curves = {s: [] for s in SLICES}
    nq_curves = {s: [] for s in SLICES}
    shuffle_curves = {s: [] for s in SLICES}
    sleep_log, flag_log, ncommit_curve = [], [], []
    for k in range(n_cycles):
        read_this_cycle = (k == 0) or do_read
        new_reps = {ci: [] for ci in held}
        if read_this_cycle:
            for ci in held:
                chunk = postings[ci][k * m:(k + 1) * m]
                if not chunk:
                    continue
                if scramble:
                    rng = np.random.default_rng(seed + 1009 * int(ci) + 31 * k)
                    chunk = [LOOP2._scramble_words(s, rng) for s in chunk]
                reps = LOOP2._encode_sentences(model, tok, chunk, cfg, device, spec)
                for r in reps:
                    acc_reps[ci].append(r)
                    new_reps[ci].append(r)
        # FLAG (clarify gate over the whole held population; diagnostic)
        n_flagged = LOOP2._clarify_flag_population(acc_reps, held, gate, cfg)
        flag_log.append(n_flagged)
        # SLEEP (MDL-gated consolidation with plain/precision update + coverage override)
        is_init = (k == 0)
        if is_init or do_sleep:
            slog, _committed = LOOP2._sleep_consolidate(acc_reps, new_reps, store, kal_rep, kal_prec,
                                                        committed_conf, is_init, mode, cfg, base_clean)
            assert slog["n_evaluated"] >= 1, (
                "SLEEP_DID_NOT_FIRE arm=%s cycle=%d (n_evaluated=0)" % (arm, k))
        else:
            slog = dict(n_consolidated=0, n_kept_episodic=len(held), n_evaluated=0,
                        sample_commits=[], sleep_disabled=True)
        sleep_log.append(slog)
        ncommit_curve.append(slog["n_consolidated"])
        # PROBE (per-slice, leak-proof)
        probe = _probe_stratified(store, base_text, ground, counts, universe, split, slices,
                                  adj, deg, n_shards, seed)
        for s in SLICES:
            curves[s].append(probe[s]["auc"])
            nq_curves[s].append(probe[s]["n_query"])
            shuffle_curves[s].append(probe[s]["shuffle"])
        _log("  arm=%s mode=%s cycle=%d LOW=%s(nq=%s) MID=%s HIGH=%s ALL=%s n_flag=%d n_consol=%d"
             % (arm, mode, k, _fmt(probe["LOW"]["auc"]), probe["LOW"]["n_query"],
                _fmt(probe["MID"]["auc"]), _fmt(probe["HIGH"]["auc"]), _fmt(probe["ALL"]["auc"]),
                n_flagged, slog["n_consolidated"]))
        _heartbeat(out_dir, unit_idx=k, total_units=n_cycles, elapsed_s=0.0,
                   extra={"arm": arm, "LOW_auc": probe["LOW"]["auc"], "HIGH_auc": probe["HIGH"]["auc"],
                          "LOW_nq": probe["LOW"]["n_query"]})
    text_final = LOOP2._store_to_text_matrix(store, np.zeros_like(base_text))
    digest = hashlib.sha256(np.ascontiguousarray(text_final).tobytes()).hexdigest()
    return dict(arm=arm, mode=mode, slice_curves=curves, slice_nq_curves=nq_curves,
                slice_shuffle_curves=shuffle_curves, sleep_log=sleep_log, flag_log=flag_log,
                ncommit_curve=ncommit_curve, store_digest=digest, n_committed_final=len(store))


# ===========================================================================
# DATA PREP: reuse the v2 loop prep verbatim (universe/counts/split/postings/adj/
# grounding + encoder acquisition), then add exposure slices. CM/CA3 outputs are
# produced by LOOP2._prepare but UNUSED here (arms are plain/precision).
# ===========================================================================
def _prepare(cfg, out_dir, ckpt_path, device):
    prep = LOOP2._prepare(cfg, out_dir, ckpt_path, device)
    slices, slice_meta = _build_slices(prep["held"], prep["counts"])
    prep["slices"] = slices
    prep["slice_meta"] = slice_meta
    _log("  exposure slices (ARC mention count terciles):")
    for name in SLICES:
        sm = slice_meta[name]
        _log("    %-5s n=%d exposure[min/median/max]=%d/%.0f/%d"
             % (name, sm["n_concepts"], sm["exposure_min"], sm["exposure_median"], sm["exposure_max"]))
    return prep


# ===========================================================================
# VERDICT
# ===========================================================================
def _gain(curve):
    if not curve or curve[0] is None or curve[-1] is None:
        return None
    return curve[-1] - curve[0]


def _sustained(curve):
    g = _gain(curve)
    if g is None:
        return False, g, None
    vals = [c for c in curve if c is not None]
    if not vals:
        return False, g, None
    peak = max(vals)
    washout = (curve[-1] < peak - WASHOUT_EPS)
    return bool(g > HP_GAIN_MARGIN and not washout), g, washout


def _retention_ok(curve):
    if not curve or curve[0] is None:
        return False
    vals = [c for c in curve if c is not None]
    if not vals:
        return False
    return min(vals) >= curve[0] - RETENTION_EPS


def _per_arm_slice_summary(r):
    out = {}
    for s in SLICES:
        curve = r["slice_curves"][s]
        sus, g, wash = _sustained(curve)
        out[s] = dict(
            auc_curve=[(round(c, 4) if c is not None else None) for c in curve],
            nq_curve=r["slice_nq_curves"][s],
            gain=(round(g, 4) if g is not None else None),
            washed_out=wash, sustained=sus, retention_ok=_retention_ok(curve),
        )
    return out


def build_verdict(arm_results, cfg, slice_meta):
    by = {r["arm"]: r for r in arm_results}
    per_arm = {arm: _per_arm_slice_summary(by[arm]) for arm in ARMS}

    prec = per_arm[PRECISION_ARM]
    plain = per_arm[PLAIN_ARM]
    low_prec = prec[KEY_SLICE]
    high_prec = prec[SAT_SLICE]

    low_gain = low_prec["gain"]
    high_gain = high_prec["gain"]
    low_sustained = low_prec["sustained"]
    low_retention = low_prec["retention_ok"]
    # contrast: reading teaches the NEW (low-exposure) concept MORE than the saturated one
    contrast_ok = bool(low_gain is not None and high_gain is not None
                       and low_gain > high_gain + CONTRAST_EPS)

    # sleep fires every cycle across arms that HAVE sleep enabled (READ_NO_SLEEP intentionally off > c0)
    sleep_every = all(all(s.get("n_evaluated", 0) >= 1 for s in by[arm]["sleep_log"])
                      for arm in ARMS if ARM_SPEC[arm]["sleep"])

    # controls-below-main on the LOW slice (best MAIN final > each control final)
    def low_final(arm):
        c = by[arm]["slice_curves"][KEY_SLICE]
        return c[-1] if c and c[-1] is not None else None
    best_main_low = max(MAIN_MODE_ARMS, key=lambda a: (low_final(a) if low_final(a) is not None else -1.0))
    best_main_low_final = low_final(best_main_low)
    ctrl_low_finals = {a: low_final(a) for a in CONTROL_ARMS}
    controls_below_main = all(
        (best_main_low_final is not None and cf is not None and best_main_low_final > cf + HP_CONTROL_SEP)
        for cf in ctrl_low_finals.values())

    # comprehension: MAIN_precision LOW-slice AUC beats SCRAMBLED LOW-slice AUC at c0 and final
    prec_low_curve = by[PRECISION_ARM]["slice_curves"][KEY_SLICE]
    scram_low_curve = by[SCRAM_ARM]["slice_curves"][KEY_SLICE]
    comp_c0 = ((prec_low_curve[0] - scram_low_curve[0])
               if (prec_low_curve[0] is not None and scram_low_curve[0] is not None) else None)
    comp_f = ((prec_low_curve[-1] - scram_low_curve[-1])
              if (prec_low_curve[-1] is not None and scram_low_curve[-1] is not None) else None)
    comprehension_fires = bool(comp_c0 is not None and comp_c0 > 0.0 and comp_f is not None and comp_f > 0.0)

    # NO_READ flat (LOW slice; reading-off => nothing changes) + clarify fired
    noread_low = by[NOREAD_ARM]["slice_curves"][KEY_SLICE]
    noread_vals = [c for c in noread_low if c is not None]
    noread_flat = bool(len(noread_vals) >= 1 and (max(noread_vals) - min(noread_vals) < 1e-6))
    clarify_fired = bool(max(by[PRECISION_ARM]["flag_log"]) > 0)

    # LOW-slice statistical power
    low_nq_final = by[PRECISION_ARM]["slice_nq_curves"][KEY_SLICE][-1] if \
        by[PRECISION_ARM]["slice_nq_curves"][KEY_SLICE] else 0
    power_floor = SMOKE_POWER_FLOOR if cfg["run_mode"] == "smoke" else MIN_QUERY_TASKS
    power_ok = (low_nq_final is not None and low_nq_final >= power_floor)

    # exposure ordering sane (LOW < HIGH median) and >=2 slices populated with queries
    exposure_ordered = bool(slice_meta["LOW"]["exposure_median"] < slice_meta["HIGH"]["exposure_median"])
    slices_with_power = sum(1 for s in ("LOW", "MID", "HIGH")
                            if (by[PRECISION_ARM]["slice_nq_curves"][s][-1] or 0) >= power_floor)
    stratified_probe_fires = bool(exposure_ordered and slices_with_power >= 2)

    # arms differ (plain vs precision store digests distinct)
    modes_differ = (by[PLAIN_ARM]["store_digest"] != by[PRECISION_ARM]["store_digest"])

    if cfg["run_mode"] == "smoke":
        mechanism_ok = bool(sleep_every and stratified_probe_fires and comprehension_fires
                            and noread_flat and clarify_fired and modes_differ and power_ok)
        verdict = "SMOKE_MECHANISM_PASS" if mechanism_ok else "SMOKE_MECHANISM_INCONCLUSIVE"
        teaches_new = None
    else:
        teaches_new = bool(low_sustained and contrast_ok)
        hard = bool(low_sustained and contrast_ok and low_retention and sleep_every
                    and controls_below_main and comprehension_fires and power_ok
                    and stratified_probe_fires)
        any_low_gain = bool(low_gain is not None and low_gain > 0.0)
        verdict = "HARD_PASS" if hard else ("MIDDLE_BAND" if any_low_gain else "HARD_FAIL")

    # DEFLATE autopsy fields (populated always; load-bearing on a null)
    autopsy = dict(
        low_gain=low_gain, high_gain=high_gain, low_sustained=low_sustained,
        low_washed_out=low_prec["washed_out"], contrast_ok=contrast_ok,
        low_nq_final=low_nq_final, mentions_per_concept_total=cfg["n_cycles"] * cfg["mentions_per_cycle"],
        mentions_per_cycle=cfg["mentions_per_cycle"], n_cycles=cfg["n_cycles"],
        low_exposure_median=slice_meta["LOW"]["exposure_median"],
        high_exposure_median=slice_meta["HIGH"]["exposure_median"],
        plain_low_gain=plain[KEY_SLICE]["gain"], plain_high_gain=plain[SAT_SLICE]["gain"],
    )

    return dict(
        verdict=verdict,
        teaches_new_concepts=teaches_new,
        per_arm_slice=per_arm,
        slice_meta=slice_meta,
        low_gain=low_gain, high_gain=high_gain, low_sustained=low_sustained,
        contrast_low_beats_high=contrast_ok,
        low_retention_ok=low_retention,
        best_main_low_arm=best_main_low, best_main_low_final=(round(best_main_low_final, 4)
                                                              if best_main_low_final is not None else None),
        control_low_finals={a: (round(v, 4) if v is not None else None) for a, v in ctrl_low_finals.items()},
        controls_below_main=controls_below_main,
        comprehension_gap_low_cycle0=(round(comp_c0, 4) if comp_c0 is not None else None),
        comprehension_gap_low_final=(round(comp_f, 4) if comp_f is not None else None),
        comprehension_fires=comprehension_fires,
        noread_low_flat=noread_flat, clarify_fired=clarify_fired,
        sleep_fired_every_cycle=sleep_every, modes_differ=modes_differ,
        low_nq_final=low_nq_final, power_ok=power_ok,
        stratified_probe_fires=stratified_probe_fires,
        exposure_ordered=exposure_ordered, slices_with_power=slices_with_power,
        autopsy=autopsy,
        flag_population_curve=by[PRECISION_ARM]["flag_log"],
    )


# ===========================================================================
# ARMS-MUST-DIFFER (META_RULE_AF)
# ===========================================================================
def _arms_differ(arm_results):
    dig = {r["arm"]: r["store_digest"] for r in arm_results}
    # EXEMPT (NO_READ, READ_NO_SLEEP): both freeze the consolidated store at cycle-0 (same mode) by
    # construction -- reading changes nothing under read-off/sleep-off; THAT identity is the finding.
    exempt = {frozenset((NOREAD_ARM, NOSLEEP_ARM))}
    names = sorted(dig)
    collisions = []
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            na, nb = names[a], names[b]
            if dig[na] == dig[nb] and frozenset((na, nb)) not in exempt:
                collisions.append((na, nb))
    assert not collisions, "META_RULE_AF VIOLATION: arms bit-identical (not exempted): %s" % collisions
    return dig


# ===========================================================================
# MAIN RUN
# ===========================================================================
def run_full(cfg, out_dir, ckpt_path):
    device = V2._select_device() if cfg["run_mode"] == "full" else torch.device("cpu")
    _log("device=%s run_mode=%s ckpt=%s" % (device.type, cfg["run_mode"], ckpt_path))
    prep = _prepare(cfg, out_dir, ckpt_path, device)
    held = prep["held"]
    if len(held) < 12:
        raise RuntimeError("too few well-covered held concepts (%d) for tercile stratification" % len(held))
    seed = cfg["seed"]
    arm_results = []
    for arm in ARMS:
        _log("=== ARM %s (mode=%s) ===" % (arm, ARM_SPEC[arm]["mode"]))
        r = _run_arm(arm, held, prep["slices"], prep["postings"], prep["model"], prep["tok"],
                     prep["spec"], cfg, device, out_dir, prep["ground"], prep["counts"],
                     prep["universe"], prep["split"], prep["adj"], prep["deg"], prep["n_shards"],
                     seed, prep["base_text"], prep["base_clean"])
        arm_results.append(r)
    digests = _arms_differ(arm_results)
    verdict = build_verdict(arm_results, cfg, prep["slice_meta"])
    payload = dict(
        anchor_name=ANCHOR_NAME, run_mode=cfg["run_mode"], ts_iso=_now(),
        encoder_source=prep["encoder_source"], device=device.type,
        n_held_concepts=len(held), n_cycles=cfg["n_cycles"], mentions_per_cycle=cfg["mentions_per_cycle"],
        corpus_stats=prep["corpus_stats"], collect_meta=prep["collect_meta"],
        arms={r["arm"]: {k: v for k, v in r.items() if k != "store_digest"} for r in arm_results},
        arm_store_digests=digests,
        consol_cfg={k: cfg[k] for k in LOOP2._CONSOL_DEFAULTS},
        loop_cfg=dict(n_cycles=cfg["n_cycles"], mentions_per_cycle=cfg["mentions_per_cycle"],
                      min_evidence_mentions=cfg["min_evidence_mentions"],
                      concentration_thresh=cfg["concentration_thresh"],
                      min_compression_ratio=cfg["min_compression_ratio"]),
        **verdict,
    )
    au = verdict["autopsy"]
    payload["verdict_msg"] = (
        "teaches_new=%s | LOW_gain=%s(sustained=%s,wash=%s) HIGH_gain=%s contrast=%s | "
        "plain_LOW=%s plain_HIGH=%s | sleep_every=%s controls_below=%s comprehension=%s "
        "LOW_nq=%s LOW_exp_med=%.0f HIGH_exp_med=%.0f" % (
            verdict["teaches_new_concepts"], au["low_gain"], verdict["low_sustained"],
            au["low_washed_out"], au["high_gain"], verdict["contrast_low_beats_high"],
            au["plain_low_gain"], au["plain_high_gain"],
            verdict["sleep_fired_every_cycle"], verdict["controls_below_main"],
            verdict["comprehension_fires"], verdict["low_nq_final"],
            au["low_exposure_median"], au["high_exposure_median"]))
    payload["summary"] = payload["verdict"]
    return payload


# ===========================================================================
# metrics IO (atomic) + crash diag
# ===========================================================================
def _write_metrics(out_dir, payload, elapsed_s):
    payload = dict(payload)
    payload["elapsed_s"] = round(elapsed_s, 3)
    payload.setdefault("verdict", "CYCLE_INCOMPLETE")
    payload.setdefault("verdict_msg", payload.get("verdict"))
    payload.setdefault("summary", payload.get("verdict"))
    payload["VET_PENDING"] = True
    payload["LOCAL_ONLY_UNCOMMITTED"] = True
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, default=str)
    os.replace(tmp, final)
    return final


def _write_crash_metrics(out_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg="%s: %s" % (type(exc).__name__, str(exc)[:500]),
                summary="CELL_CRASHED", elapsed_s=0.0, traceback=traceback.format_exc()[:5000],
                ts_iso=_now(), anchor_name=ANCHOR_NAME)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


# ===========================================================================
# SELF-TEST: constructs REAL objects (encoder, clarify, learner MDL, Kalman,
# override gate, per-slice probe, exposure stratifier) at tiny scale -- NO corpus.
# ===========================================================================
def self_test():
    out = {}
    device = torch.device("cpu")
    torch.manual_seed(7)
    np.random.seed(7)

    # (1) exposure stratifier: terciles by ARC count, monotone exposure ranges, ALL == union
    held = [10, 11, 12, 13, 14, 15, 16, 17, 18]
    counts = np.zeros(64, dtype=np.int64)
    for j, ci in enumerate(held):
        counts[ci] = 20 + j * 40           # strictly increasing exposure
    slices, meta = _build_slices(held, counts)
    assert meta["LOW"]["exposure_median"] < meta["HIGH"]["exposure_median"], meta
    assert sorted(slices["LOW"] + slices["MID"] + slices["HIGH"]) == sorted(held)
    assert slices["ALL"] == sorted(held)
    out["stratify"] = {k: meta[k]["n_concepts"] for k in SLICES}

    # (2) tiny encoder (real V2.TinyTransformer + pooled path) + L2-normalized reps
    from tokenizers import Tokenizer, models, trainers, pre_tokenizers
    toy = ["the cat sat on the mat", "a dog ran in the park", "birds fly over the sea",
           "rocks are hard and heavy", "water is wet and cold", "the sun is very hot"]
    tk = Tokenizer(models.BPE(unk_token="[UNK]"))
    tk.pre_tokenizer = pre_tokenizers.Whitespace()
    tk.train_from_iterator(iter(toy * 20), trainers.BpeTrainer(
        vocab_size=64, special_tokens=["[PAD]", "[UNK]", "[MASK]"], show_progress=False))
    spec = dict(pad=tk.token_to_id("[PAD]"), unk=tk.token_to_id("[UNK]"),
                mask=tk.token_to_id("[MASK]"), size=tk.get_vocab_size())
    model = V2.TinyTransformer(spec["size"], 16, 16, 1, 2, 2, spec["pad"]).to(device)
    model.eval()
    cfg = dict(SELFTEST_CFG)
    cfg["max_len"] = 16
    reps = LOOP2._encode_sentences(model, tk, toy, cfg, device, spec)
    assert reps.shape == (6, 16), reps.shape
    assert np.allclose(np.linalg.norm(reps, axis=1), 1.0, atol=1e-3), "pooled reps must be L2-normalized"
    out["encode"] = {"shape": list(reps.shape)}

    # (3) learner MDL gate + precision Kalman + override gate + clarify (reuse REAL v2 loop objects)
    coherent = [reps[0] + 0.01 * np.random.randn(16).astype(np.float32) for _ in range(4)]
    for c in coherent:
        c /= (np.linalg.norm(c) + 1e-8)
    lr_c, coh_c = LOOP2._concept_learn_result(coherent)
    lr_i, coh_i = LOOP2._concept_learn_result(list(reps[:4]))
    assert coh_c > coh_i, (coh_c, coh_i)
    from hdlab.learner.core import per_cluster_gate
    assert per_cluster_gate(lr_c, 1.0), "coherent evidence must pass MDL gate"
    gate = ClarifyGate()
    n_flag = LOOP2._clarify_flag_population({0: [reps[0]], 1: coherent}, [0, 1], gate,
                                            dict(clarify_min_evidence=6))
    assert n_flag >= 1, "clarify gate must flag the under-known concept"
    # confident concept takes a smaller Kalman step than a cold one for the same mention
    ccfg = dict(LOOP2._CONSOL_DEFAULTS)
    v = reps[1].astype(np.float64)
    mu_cold, _ = LOOP2._kalman_fold(reps[0].astype(np.float64), ccfg["prec_prior"], [v], ccfg)
    mu_conf, _ = LOOP2._kalman_fold(reps[0].astype(np.float64), 20.0, [v], ccfg)
    assert float(np.linalg.norm(mu_conf - reps[0])) < float(np.linalg.norm(mu_cold - reps[0])), \
        "confident concept must take a smaller step"
    # override gate: a 1-mention low-coverage cycle does NOT override a high-confidence rep (retention)
    store, kal_rep, kal_prec, committed_conf = {}, {}, {}, {}
    ocfg = dict(LOOP2._CONSOL_DEFAULTS); ocfg.update(min_compression_ratio=1.0, min_evidence_mentions=1,
                                                     concentration_thresh=0.0)
    LOOP2._sleep_consolidate({0: coherent}, {0: coherent}, store, kal_rep, kal_prec, committed_conf,
                             is_init=True, mode="precision", cfg=ocfg,
                             base_clean=np.zeros((0, 16), np.float32))
    rep_after_init = store[0].copy()
    rng = np.random.default_rng(11)
    lowcov = [rng.standard_normal(16).astype(np.float32)]; lowcov[0] /= np.linalg.norm(lowcov[0])
    slog1, _ = LOOP2._sleep_consolidate({0: coherent[:1]}, {0: lowcov}, store, kal_rep, kal_prec,
                                        committed_conf, is_init=False, mode="precision", cfg=ocfg,
                                        base_clean=np.zeros((0, 16), np.float32))
    assert slog1["n_consolidated"] == 0, ("override gate must defer a low-coverage cycle", slog1)
    assert np.allclose(store[0], rep_after_init), "deferred cycle must not change committed rep (retention)"
    out["consolidation"] = {"coherent_coh": round(coh_c, 4), "clarify_flag": int(n_flag),
                            "lowcov_deferred": True}

    # (4) PER-SLICE probe code path on a tiny synthetic universe/graph -> distinct per-slice AUC + n_query
    K, d = 12, 16
    rng2 = np.random.default_rng(3)
    ground = rng2.standard_normal((K, d)).astype(np.float32)
    ground /= (np.linalg.norm(ground, axis=1, keepdims=True) + 1e-8)
    text = ground.copy()
    universe = dict(ids=["c%d" % i for i in range(K)], K=K, surfaces=["c%d" % i for i in range(K)])
    heldK = list(range(0, 6))
    split = dict(held_idx=np.array(heldK, dtype=np.int64),
                 train_eval_idx=np.arange(6, 12, dtype=np.int64))
    adj = [set() for _ in range(K)]
    for h in range(6):
        nb = 6 + h
        text[nb] = ground[h] * 0.9 + 0.1 * ground[nb]
        text[nb] /= (np.linalg.norm(text[nb]) + 1e-8)
        adj[h].add(nb); adj[nb].add(h)
    deg = np.array([len(a) for a in adj], dtype=np.int64)
    countsK = np.array([100, 100, 100, 5, 5, 5, 1, 1, 1, 1, 1, 1], dtype=np.int64)
    sl, _m = _build_slices(heldK, countsK)
    probe = _probe_stratified({}, text, ground, countsK, universe, split, sl, adj, deg, 1, 7)
    assert probe["ALL"]["n_query"] is not None and probe["ALL"]["n_query"] >= 1, probe["ALL"]
    # slice n_query should sum to <= ALL n_query (each held queried once, partitioned)
    part_sum = sum((probe[s]["n_query"] or 0) for s in ("LOW", "MID", "HIGH"))
    assert part_sum == probe["ALL"]["n_query"], (part_sum, probe["ALL"]["n_query"])
    out["per_slice_probe"] = {s: probe[s]["n_query"] for s in SLICES}

    # (5) FULL code path: v2-checkpoint round-trip via the shared loader
    import tempfile
    ckpt = dict(state_dict={k: v.detach().cpu() for k, v in model.state_dict().items()}, spec=spec,
                model_cfg=dict(vocab=spec["size"], max_len=16, d_model=16, n_layers=1, n_heads=2,
                               ffn_mult=2, pad_id=spec["pad"]),
                tokenizer_json=tk.to_str(), seed=7, run_mode="selftest", anchor="ckpt_roundtrip",
                w_star=0.5, selected_arm="ARM_RAW_TEXT")
    fd, cpath = tempfile.mkstemp(suffix=".pt")
    os.close(fd)
    try:
        torch.save(ckpt, cpath)
        m2, tk2, spec2, mc2 = LOOP2._build_encoder_from_ckpt(cpath, device)
        reps2 = LOOP2._encode_sentences(m2, tk2, toy, cfg, device, spec2)
        assert np.allclose(reps2, reps, atol=1e-4), "reloaded encoder must reproduce saved reps"
        out["ckpt_roundtrip"] = {"reload_ok": True, "d_model": mc2["d_model"]}
    finally:
        try:
            os.remove(cpath)
        except OSError:
            pass
    print("[%s] SELF-TEST PASS %s" % (ANCHOR_NAME, json.dumps(out)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--ckpt", type=str, default=None, help="path to v2 encoder checkpoint (FULL engine)")
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    env_mode = os.environ.get("HDLAB_RUN_MODE", "").lower()
    is_full = bool(args.full or (env_mode == "full" and not args.smoke))
    cfg = dict(FULL_CFG if is_full else SMOKE_CFG)
    if args.seed is not None:
        cfg["seed"] = args.seed
    ckpt_path = args.ckpt
    if is_full and not ckpt_path:
        ckpt_path = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v2",
                                 "ckpt_seed_%d.pt" % cfg["seed"])
    if is_full and not (ckpt_path and os.path.exists(ckpt_path)):
        raise RuntimeError("FULL run requires the v2 comprehension-engine checkpoint; not found at %r "
                           "(pass --ckpt or stage data/exp_scale_meaning_learn_arc_heldout_v2/"
                           "ckpt_seed_%d.pt)" % (ckpt_path, cfg["seed"]))
    out_dir = _out_dir(cfg["run_mode"])
    _write_start_marker(out_dir, cfg["run_mode"], expected_units=len(ARMS) * cfg["n_cycles"])
    t0 = time.perf_counter()
    _log("RUN START run_mode=%s ckpt=%s" % (cfg["run_mode"], ckpt_path))
    payload = run_full(cfg, out_dir, ckpt_path)
    elapsed = time.perf_counter() - t0
    payload["elapsed_s"] = round(elapsed, 3)
    final = _write_metrics(out_dir, payload, elapsed)
    _log("RUN DONE (%.1fs) -> %s" % (payload["elapsed_s"], final))
    _log("VERDICT=%s | %s" % (payload["verdict"], payload["verdict_msg"]))


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _mode = "selftest"
    elif "--full" in sys.argv or (os.environ.get("HDLAB_RUN_MODE", "").lower() == "full"
                                  and "--smoke" not in sys.argv):
        _mode = "full"
    elif "--smoke" in sys.argv:
        _mode = "smoke"
    else:
        _mode = "selftest"
    _od = _out_dir(_mode)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
