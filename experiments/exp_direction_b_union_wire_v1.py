# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (deterministic construction-cue-vote learners + WordNet-MWE dictionary lookup +
#   FHRR bind/bundle/cleanup, fixed small codebooks, no decoded/noisy continuous signal)
# - HP_SCOPE per-arm declaration (arm vi gates WIRE/NO-WIRE; others comparators/controls)
# - cardinality_ok: EXPECTED_N_UNITS=7 (one unit per PRIMARY-cohort arm)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (all 3 sub-mechanisms + their precedence were
#   calibrated/validated in their OWN prior cells; this cell reuses their fitted hypotheses unchanged)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL FHRR bind/unbind/bundle primitives + all 3 sub-mechanism modules
#   (real_code_path); no synthetic-only branch
# - progress_logging: print_flush_true
# See preregs/2026-08-09_direction_b_union_wire_v1.md for the full pre-registration.
"""exp_direction_b_union_wire_v1 -- Direction-B wire-don't-island close-out: measures the exact UNION
of the three validated OOV-recovery sub-mechanisms (hdlab.goal_achievement.utility_channel_
resulttype_grounded [M2], _idiom_grounded [M1], _relation_grounded [fork-A]) via the new
utility_channel_union_grounded (added this session to hdlab/goal_achievement.py, precedence
resulttype -> relation -> idiom_fallback, plus fork-A's own no-active-attribute RELATION_LINK
fallback reused verbatim). Each sub-mechanism catches a STRUCTURALLY DIFFERENT residual pattern
(M2=refusal/grant/block/achieve/fail constructions; relation=means-end instantiation + dictionary
contradiction; M1=non-compositional colloquialisms neither of the others has any cue for) --
hypothesis: their union is NET-ADDITIVE over M2-alone (the best single sub-mechanism, 3/8 primary,
9/37 breadth). This cell measures that hypothesis and WIRES the union channel into
goal_achievement_verdict (strict-ADD, abstain-only fallback) IFF net-positive.

Arms (PRIMARY cohort, n=160 draw / cohort n=22, 8 gold-Unfulfilled -- identical draw to Stage-2/M1/
M2/M3-inc1/fork-A):
  (i)   majority-only baseline
  (ii)  utility_channel (Stage-2, WordNet-only)                    -- reference, unchanged
  (iii) utility_channel_resulttype_grounded  (M2 ALONE)             -- re-measured fresh this run
  (iv)  utility_channel_idiom_grounded       (M1 ALONE, no ConceptNet bridge -- matches the union's
                                               own idiom_fallback path, see hdlab/goal_achievement.py)
  (v)   utility_channel_relation_grounded    (fork-A ALONE)         -- re-measured fresh this run
  (vi)  utility_channel_union_grounded       (THE UNION MECHANISM ARM -- gates WIRE/NO-WIRE)
  (vii) utility_channel_union_grounded, SCRAMBLED goal cue          -- mandatory pairscramble control

Modes:
  --self-test  hdlab.goal_achievement.self_test_union_grounded_channel() (constructs the REAL
               construction-cue extraction + WordNet-MWE scan + registry.learn() fits + FHRR
               primitives for all 3 sub-mechanisms + the union, real code path, no DesireDB needed).
  --smoke      PRIMARY cohort probe (7 arms, mechanism-fires + arms-differ checks only, no
               HARD_PASS/HARD_FAIL/WIRE claim).
  --full       PRIMARY cohort (gate-defining) + BREADTH cohort context (900 rows) + full-bench
               macro-F1 (n=80 AND n=160, union-wired vs base-alone) + harness_validity_check
               (reproduces the documented 0.686/0.699 macro-F1) -> WIRE/NO-WIRE decision.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import random
import sys
import time
import traceback
from datetime import datetime, timezone

ANCHOR_NAME = "direction_b_union_wire_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

import exp_utility_satisfaction_channel_v1 as _s2  # noqa: E402 -- reuse loader/cohort/metrics verbatim

from hdlab.goal_achievement import (  # noqa: E402
    goal_achievement_verdict, utility_channel, utility_channel_resulttype_grounded,
    utility_channel_idiom_grounded, utility_channel_relation_grounded, utility_channel_union_grounded,
    activate_attributes, self_test_utility_channel, self_test_union_grounded_channel,
    self_test as ga_self_test, MAJORITY_CLASS,
)
from hdlab import result_type_induction as _rti  # noqa: E402
from hdlab import goal_outcome_relation as _gor  # noqa: E402

SEED = _s2.SEED  # 20260808, identical draw to Stage-2/M1/M2/M3-inc1/fork-A
FULL_N_PER_CLASS = _s2.FULL_N_PER_CLASS  # 80 -> n=160, the exact cohort n=22/8 draw
VALIDITY_N_PER_CLASS = _s2.VALIDITY_N_PER_CLASS  # 40 -> n=80, documented-baseline harness

# GATE-2 (recovery) bands -- reused verbatim from M1/M2/M3-inc1/fork-A (same cohort, same definitions).
GATE2_HP_RECOVERY = 0.40
GATE2_HARD_FAIL_RECOVERY = 0.15
GATE2_PAIRSCRAMBLE_MAX_DELTA_VS_BASELINE = 0.05   # |scr-i| <= this -> collapses
GATE2_PAIRSCRAMBLE_MAX_DELTA_VS_REAL = 0.03       # |scr-mech| <= this -> leaks (non-goal-conditioned)
VALIDITY_TOLERANCE = 0.03
MIN_COHORT_N = 15

# WIRE gate: full-bench macro-F1 floor (reused verbatim from Stage-2's own HP/HF bands) + the
# net-positive/genuinely-additive conditions declared in the task contract (not exp_dev's to loosen).
HF_FULL_BENCH_MACRO_F1_FLOOR = 0.620

ARM_NAMES = ("i", "ii", "iii_m2", "iv_m1", "v_relation", "vi_union", "vii_union_scr")
ENLARGED_N_ROWS = 900          # identical to M1/M2/M3-inc1/fork-A (compute-proportionality; head-to-
                                # head comparability with their measured 0/37, 9/37, 3/37 breadth).
ENLARGED_SEED = 20260809

# CITED references from prior landed cells (same 900-row/ENLARGED_SEED draw) -- NOT re-measured
# standalone at breadth for M1/relation (cheap per-item attribution IS re-measured fresh below on the
# breadth gold-Unfulfilled subset; these are the prior cells' own full-cohort-pass numbers for
# cross-check).
M1_BREADTH_REFERENCE = {"recovery_rate": 0.0, "n_recovered": 0, "n_majority_wrong": 37,
                         "source": "data/exp_direction_b_M1_idiom_grounding_recovery_v1/metrics.json"}
M2_BREADTH_REFERENCE = {"recovery_rate": 0.2432, "n_recovered": 9, "n_majority_wrong": 37,
                         "source": "data/exp_direction_b_M2_speechact_result_generalization_v1/metrics.json"}
RELATION_BREADTH_REFERENCE = {"recovery_rate": 0.0811, "n_recovered": 3, "n_majority_wrong": 37,
                               "source": "data/exp_direction_b_A_goal_outcome_relation_v1/metrics.json"}


# ============================================================================ GATE-1: fit
# hypotheses (already validated by M2's and fork-A's own prior cells -- this cell does NOT re-litigate
# GATE-1's held-out generalization bands, only reuses the fitted (chosen_name, hypothesis) pairs those
# cells already gated HARD_PASS [M2] / MIDDLE_BAND-with-held_out_acc=1.0 [fork-A]).
def fit_hypotheses() -> dict:
    rt_name, rt_hyp = _rti.get_induced_hypothesis()
    rel_name, rel_hyp = _gor.get_induced_hypothesis()
    return {"resulttype_chosen_name": rt_name, "resulttype_hypothesis": rt_hyp,
            "relation_chosen_name": rel_name, "relation_hypothesis": rel_hyp,
            "resulttype_fit_ok": rt_hyp is not None, "relation_fit_ok": rel_hyp is not None}


# ============================================================================ PRIMARY cohort arms
def run_cohort_arms(sample: list, cohort_idxs: list, hyps: dict) -> dict:
    rt_name, rt_hyp = hyps["resulttype_chosen_name"], hyps["resulttype_hypothesis"]
    rel_name, rel_hyp = hyps["relation_chosen_name"], hyps["relation_hypothesis"]
    scrambled_cues = _s2._scrambled_desires(sample)
    gold = []
    preds = {name: [] for name in ARM_NAMES}
    activation_fires, verdict_fires_union = [], []
    per_item_attribution = []
    for i in cohort_idxs:
        r = sample[i]
        desire, outcome = r["Desire-Expression-Sentence"], r["Evidence"]
        gold.append(r["Fulfillment-Label"])
        activation_fires.append(len(activate_attributes(desire)) > 0)

        preds["i"].append(MAJORITY_CLASS)
        u_wn = utility_channel(desire, outcome)
        preds["ii"].append(u_wn if u_wn is not None else MAJORITY_CLASS)

        u_m2 = utility_channel_resulttype_grounded(desire, outcome, rt_name, rt_hyp)
        preds["iii_m2"].append(u_m2 if u_m2 is not None else MAJORITY_CLASS)

        u_m1 = utility_channel_idiom_grounded(desire, outcome, use_conceptnet_bridge=False)
        preds["iv_m1"].append(u_m1 if u_m1 is not None else MAJORITY_CLASS)

        u_rel = utility_channel_relation_grounded(desire, outcome, rel_name, rel_hyp)
        preds["v_relation"].append(u_rel if u_rel is not None else MAJORITY_CLASS)

        u_union = utility_channel_union_grounded(desire, outcome, rt_name, rt_hyp, rel_name, rel_hyp)
        preds["vi_union"].append(u_union if u_union is not None else MAJORITY_CLASS)
        verdict_fires_union.append(u_union is not None)

        u_scr = utility_channel_union_grounded(scrambled_cues[i], outcome, rt_name, rt_hyp, rel_name, rel_hyp)
        preds["vii_union_scr"].append(u_scr if u_scr is not None else MAJORITY_CLASS)

        if r["Fulfillment-Label"] == "Unfulfilled":
            per_item_attribution.append({
                "idx": i, "gold": "Unfulfilled",
                "recovered_by_m2": u_m2 == "Unfulfilled",
                "recovered_by_m1": u_m1 == "Unfulfilled",
                "recovered_by_relation": u_rel == "Unfulfilled",
                "recovered_by_union": u_union == "Unfulfilled",
            })
    return {"gold": gold, "preds": preds, "activation_fires": activation_fires,
            "verdict_fires_union": verdict_fires_union, "per_item_attribution": per_item_attribution}


def recovery_rate(gold, pred) -> dict:
    """Identical definition to Stage-2/M1/M2/M3-inc1/fork-A's own recovery_rate: of the cohort items
    where the majority-only baseline is WRONG (gold=='Unfulfilled'), the fraction `pred` gets CORRECT."""
    wrong_idxs = [k for k, g in enumerate(gold) if g == "Unfulfilled"]
    if not wrong_idxs:
        return {"n_majority_wrong": 0, "n_recovered": 0, "rate": None}
    n_rec = sum(1 for k in wrong_idxs if pred[k] == gold[k])
    return {"n_majority_wrong": len(wrong_idxs), "n_recovered": n_rec,
            "rate": round(n_rec / len(wrong_idxs), 4)}


def _arms_must_differ(preds: dict) -> dict:
    digests = {name: hashlib.sha256(json.dumps(preds[name]).encode()).hexdigest() for name in ARM_NAMES}
    all_same = len(set(digests.values())) == 1
    return {"digests": digests, "arms_differ": not all_same}


# ============================================================================ BREADTH cohort (context)
def breadth_cohort_analysis(hyps: dict) -> dict:
    """Deterministic-seeded ENLARGED_N_ROWS-row subsample cohort. Fresh-measures UNION recovery (the
    task's explicit ask) + per-sub-mechanism attribution on the SAME 37-item gold-Unfulfilled breadth
    subset (cheap once the cohort is built -- 3 extra channel calls per item, not a second 900-row
    pass) + a bigger-n pairscramble-collapse corroboration for UNION. Reuses M1/M2/fork-A's exact
    ENLARGED_SEED/ENLARGED_N_ROWS for head-to-head comparability with their CITED 0/37, 9/37, 3/37."""
    import random as _random
    rt_name, rt_hyp = hyps["resulttype_chosen_name"], hyps["resulttype_hypothesis"]
    rel_name, rel_hyp = hyps["relation_chosen_name"], hyps["relation_hypothesis"]
    rows = _s2.load_desiredb_rows()
    rng = _random.Random(ENLARGED_SEED)
    idx_pool = sorted(range(len(rows)))  # sorted(set())-safe deterministic base ordering
    sub_idxs = sorted(rng.sample(idx_pool, min(ENLARGED_N_ROWS, len(idx_pool))))
    sub_rows = [rows[i] for i in sub_idxs]
    scrambled = _s2._scrambled_desires(sub_rows)

    cohort_local_idxs = []
    for i, r in enumerate(sub_rows):
        v = goal_achievement_verdict(r["Desire-Expression-Sentence"], r["Evidence"])
        if v["channel"] == "majority":
            cohort_local_idxs.append(i)
    gold_unfulfilled_local = [i for i in cohort_local_idxs if sub_rows[i]["Fulfillment-Label"] == "Unfulfilled"]

    n_recovered_union = 0
    per_item_attribution = []
    union_source_counter: dict = {}
    for i in gold_unfulfilled_local:
        r = sub_rows[i]
        desire, outcome = r["Desire-Expression-Sentence"], r["Evidence"]
        u_m2 = utility_channel_resulttype_grounded(desire, outcome, rt_name, rt_hyp)
        u_m1 = utility_channel_idiom_grounded(desire, outcome, use_conceptnet_bridge=False)
        u_rel = utility_channel_relation_grounded(desire, outcome, rel_name, rel_hyp)
        u_trace = __import__("hdlab.goal_achievement", fromlist=["utility_channel_trace_union_grounded"]) \
            .utility_channel_trace_union_grounded(desire, outcome, rt_name, rt_hyp, rel_name, rel_hyp)
        u_union = u_trace["verdict"]
        if u_union == "Unfulfilled":
            n_recovered_union += 1
        for attr, info in u_trace.get("active", {}).items():
            src = info.get("grounding_trace", {}).get("secondary_source") or info.get("path")
            union_source_counter[src] = union_source_counter.get(src, 0) + 1
        per_item_attribution.append({
            "idx": i, "gold": "Unfulfilled",
            "recovered_by_m2": u_m2 == "Unfulfilled", "recovered_by_m1": u_m1 == "Unfulfilled",
            "recovered_by_relation": u_rel == "Unfulfilled", "recovered_by_union": u_union == "Unfulfilled",
        })

    gold_cohort = [sub_rows[i]["Fulfillment-Label"] for i in cohort_local_idxs]
    pred_i_cohort = [MAJORITY_CLASS for _ in cohort_local_idxs]
    pred_scr_cohort = []
    for i in cohort_local_idxs:
        u = utility_channel_union_grounded(scrambled[i], sub_rows[i]["Evidence"], rt_name, rt_hyp, rel_name, rel_hyp)
        pred_scr_cohort.append(u if u is not None else MAJORITY_CLASS)
    acc_i_cohort = _s2.accuracy(gold_cohort, pred_i_cohort)
    acc_scr_cohort = _s2.accuracy(gold_cohort, pred_scr_cohort)

    n_denom = len(gold_unfulfilled_local)
    n_max_single = max(sum(1 for it in per_item_attribution if it["recovered_by_m2"]),
                        sum(1 for it in per_item_attribution if it["recovered_by_m1"]),
                        sum(1 for it in per_item_attribution if it["recovered_by_relation"]))
    return {
        "n_subsample_rows": len(sub_rows), "n_total_rows_available": len(rows),
        "cohort_n": len(cohort_local_idxs), "gold_unfulfilled_n": n_denom,
        "recovery_union": {
            "n_recovered": n_recovered_union, "n_majority_wrong": n_denom,
            "rate": round(n_recovered_union / n_denom, 4) if n_denom else None},
        "n_max_single_submechanism_recovered": n_max_single,
        "union_beats_max_single": n_recovered_union > n_max_single,
        "pairscramble_at_scale": {
            "cohort_n": len(cohort_local_idxs), "acc_i": round(acc_i_cohort, 4),
            "acc_scrambled_union": round(acc_scr_cohort, 4),
            "delta": round(abs(acc_scr_cohort - acc_i_cohort), 4),
            "collapses_at_scale": abs(acc_scr_cohort - acc_i_cohort) <= GATE2_PAIRSCRAMBLE_MAX_DELTA_VS_BASELINE},
        "union_source_frequency": union_source_counter,
        "per_item_attribution": per_item_attribution,
        "m1_breadth_reference": M1_BREADTH_REFERENCE, "m2_breadth_reference": M2_BREADTH_REFERENCE,
        "relation_breadth_reference": RELATION_BREADTH_REFERENCE,
    }


# ============================================================================ full-bench composition
def _base3_verdict_from_result(result: dict) -> str:
    """Reconstruct the PRE-union 3-channel-only (relation/valence/contrast-override) verdict from a
    goal_achievement_verdict() result dict, using its trace's 'base'/'override' fields -- those are
    computed BEFORE the union fallback ever runs (see hdlab.goal_achievement.goal_achievement_
    verdict's own docstring: the union is tried ONLY inside the `channel=='majority'` branch, and
    never touches `trace['base']`/`trace['override']`), so this reconstruction is EXACT regardless of
    whether the union itself fired on this item.

    THIS IS LOAD-BEARING, not cosmetic: this cell's own WIRE edit (below, applied because
    WIRE_DECISION=True) modifies hdlab.goal_achievement.goal_achievement_verdict ITSELF to include
    the union fallback. Once that edit lands, calling goal_achievement_verdict directly and trusting
    its `verdict` field to represent 'the base pipeline' would silently return the ALREADY-WIRED
    answer -- collapsing this cell's own base-vs-union comparison into a wired-vs-wired no-op on any
    future re-run (self-test caught this: composed_verdict_base's naive `goal_achievement_verdict(
    ...)["verdict"]` broke immediately after the wire edit landed). Reconstructing from the trace
    keeps 'base' meaning the true pre-union pipeline forever, independent of whether the live
    goal_achievement_verdict has been wired."""
    return "Unfulfilled" if result["trace"]["override"] else result["trace"]["base"]


def composed_verdict_base(desire: str, outcome: str) -> str:
    """The PRE-union PRODUCTION pipeline verdict (relation/valence/contrast-override only, NO
    4th-channel augmentation) -- see `_base3_verdict_from_result` for why this is reconstructed from
    the trace rather than trusted directly off `goal_achievement_verdict`'s own `verdict` field."""
    return _base3_verdict_from_result(goal_achievement_verdict(desire, outcome))


def composed_verdict_union(desire: str, outcome: str, hyps: dict) -> str:
    """The CANDIDATE/CURRENT-WIRED pipeline verdict. Post-wire, `goal_achievement_verdict` itself
    already implements exactly this composition (base verdict, except union's answer when it fired
    on a majority-abstain item), so this is now a thin pass-through; `hyps` is accepted for interface
    stability with pre-wire call sites but unused (the live function fits its own hypotheses)."""
    del hyps
    return goal_achievement_verdict(desire, outcome)["verdict"]


def full_bench_comparison(n_per_class: int, hyps: dict) -> dict:
    """Base-alone vs union-wired composed macro-F1/acc on a FRESH balanced sample of the given size
    (n=80 matches the documented-baseline harness scale; n=160 is the task's explicit WIRE-gate
    comparison scale). Computes `goal_achievement_verdict` ONCE per item and derives BOTH the base
    verdict (via `_base3_verdict_from_result`) and the union/wired verdict (its own `verdict` field,
    post-wire) from that single call/trace -- correct both BEFORE this cell's wire edit lands (when
    `goal_achievement_verdict` has no union fields, `verdict` == base3 always, so pred_union ==
    pred_base pre-wire is the correct 'not yet wired' state) and AFTER (when `verdict` reflects the
    union's own answer on recovered items). `hyps` is accepted for interface stability but unused."""
    del hyps
    rows = _s2.load_desiredb_rows()
    sample = _s2.balanced_subsample(rows, n_per_class, SEED)
    gold = [r["Fulfillment-Label"] for r in sample]
    pred_base, pred_union = [], []
    for r in sample:
        desire, outcome = r["Desire-Expression-Sentence"], r["Evidence"]
        result = goal_achievement_verdict(desire, outcome)
        pred_base.append(_base3_verdict_from_result(result))
        pred_union.append(result["verdict"])
    return {
        "n": len(sample),
        "base": {"acc": round(_s2.accuracy(gold, pred_base), 4), "macro_f1": round(_s2.macro_f1(gold, pred_base), 4)},
        "union": {"acc": round(_s2.accuracy(gold, pred_union), 4), "macro_f1": round(_s2.macro_f1(gold, pred_union), 4)},
        "macro_f1_delta_union_minus_base": round(_s2.macro_f1(gold, pred_union) - _s2.macro_f1(gold, pred_base), 4),
        "no_regression": _s2.macro_f1(gold, pred_union) >= _s2.macro_f1(gold, pred_base),
    }


def harness_validity_check() -> dict:
    """Re-verify (at every --full run) the loader+field-mapping+seed reproduces the documented
    3-channel macro-F1 0.686 (n=80, seed 20260808) -- identical to Stage-2/M1/M2/M3-inc1/fork-A's own
    gate. Stage-2's own landed run MEASURED macro_f1=0.6992 at this exact draw (delta=+0.0132,
    within tolerance) -- the '0.686/0.699' pair the task's contract refers to."""
    rows = _s2.load_desiredb_rows()
    sample = _s2.balanced_subsample(rows, VALIDITY_N_PER_CLASS, SEED)
    gold = [r["Fulfillment-Label"] for r in sample]
    pred = [goal_achievement_verdict(r["Desire-Expression-Sentence"], r["Evidence"])["verdict"]
            for r in sample]
    acc = _s2.accuracy(gold, pred)
    mf1 = _s2.macro_f1(gold, pred)
    documented_macro_f1 = 0.686
    delta = mf1 - documented_macro_f1
    return {"n": len(sample), "measured_acc": round(acc, 4), "measured_macro_f1": round(mf1, 4),
            "documented_macro_f1": documented_macro_f1, "delta_macro_f1": round(delta, 4),
            "valid": abs(delta) <= VALIDITY_TOLERANCE, "tolerance": VALIDITY_TOLERANCE}


# ============================================================================ WIRE gate verdict logic
def compute_wire_verdict(cohort_metrics: dict, breadth: dict, full_bench_160: dict, full_bench_80: dict,
                          validity: dict, cohort_n: int) -> tuple:
    if cohort_n < MIN_COHORT_N:
        return "INVALID", f"UNDERPOWERED_COHORT: n={cohort_n} (need >={MIN_COHORT_N})", False
    if not validity["valid"]:
        return ("INVALID",
                f"harness_validity_check FAILED: delta_macro_f1={validity['delta_macro_f1']} "
                f"exceeds tolerance {validity['tolerance']}", False)
    rec_union = cohort_metrics["recovery_vi_union"]
    if rec_union["rate"] is None:
        return "INVALID", "recovery_rate UNDEFINED: 0 gold-Unfulfilled items in cohort", False

    rate_union = rec_union["rate"]
    rate_m2 = cohort_metrics["recovery_iii_m2"]["rate"]
    acc_vii = cohort_metrics["acc_vii_union_scr"]
    acc_vi = cohort_metrics["acc_vi_union"]
    acc_i = cohort_metrics["acc_i"]
    delta_scr_i = abs(acc_vii - acc_i)
    delta_scr_mech = abs(acc_vii - acc_vi)
    collapses_primary = delta_scr_i <= GATE2_PAIRSCRAMBLE_MAX_DELTA_VS_BASELINE
    leaks_primary = delta_scr_mech <= GATE2_PAIRSCRAMBLE_MAX_DELTA_VS_REAL
    collapses_breadth = breadth["pairscramble_at_scale"]["collapses_at_scale"]

    no_regression_160 = full_bench_160["no_regression"]
    no_regression_80 = full_bench_80["no_regression"]
    floor_ok_160 = full_bench_160["union"]["macro_f1"] >= HF_FULL_BENCH_MACRO_F1_FLOOR
    genuinely_additive = rate_union > rate_m2

    hard_fail = leaks_primary or (not collapses_primary) or (not collapses_breadth) or (not floor_ok_160)
    wire_decision = (not hard_fail) and no_regression_160 and no_regression_80 and genuinely_additive \
        and (rate_union >= GATE2_HARD_FAIL_RECOVERY)

    if hard_fail:
        verdict = "HARD_FAIL"
    elif wire_decision:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    msg = (f"PRIMARY cohort n={cohort_n}: recovery_union={rate_union:.3f} "
           f"({rec_union['n_recovered']}/{rec_union['n_majority_wrong']}) vs recovery_M2_alone={rate_m2:.3f} "
           f"recovery_M1_alone={cohort_metrics['recovery_iv_m1']['rate']} "
           f"recovery_relation_alone={cohort_metrics['recovery_v_relation']['rate']} "
           f"genuinely_additive={genuinely_additive} || "
           f"FULL_BENCH n=160: base_macro_f1={full_bench_160['base']['macro_f1']:.4f} "
           f"union_macro_f1={full_bench_160['union']['macro_f1']:.4f} "
           f"delta={full_bench_160['macro_f1_delta_union_minus_base']:+.4f} no_regression={no_regression_160} || "
           f"FULL_BENCH n=80: base_macro_f1={full_bench_80['base']['macro_f1']:.4f} "
           f"union_macro_f1={full_bench_80['union']['macro_f1']:.4f} no_regression={no_regression_80} || "
           f"pairscramble PRIMARY: |scr-i|={delta_scr_i:.4f} (<=0.05 collapse={collapses_primary}) "
           f"|scr-mech|={delta_scr_mech:.4f} (>0.03 not-leak, leaks={leaks_primary}) || "
           f"pairscramble BREADTH: collapses_at_scale={collapses_breadth} || "
           f"BREADTH(context): recovery_union={breadth['recovery_union']['rate']} "
           f"({breadth['recovery_union']['n_recovered']}/{breadth['recovery_union']['n_majority_wrong']}) "
           f"vs M2=0.2432(9/37) M1=0.0(0/37) relation=0.0811(3/37) "
           f"union_beats_max_single={breadth['union_beats_max_single']} || "
           f"WIRE_DECISION={wire_decision}")
    return verdict, msg, wire_decision


# ============================================================================ output plumbing
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _write_heartbeat(output_dir, unit_idx, total_units, elapsed_s):
    path = os.path.join(output_dir, "_heartbeat.jsonl")
    rec = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total_units, "elapsed_s": round(elapsed_s, 2)}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


# ============================================================================ self-test
def self_test() -> dict:
    """MECHANISM-FIRES + real_code_path check. Exercises the REAL construction-cue extraction +
    WordNet-MWE scan + registry.learn() fits for ALL 3 sub-mechanisms + the REAL FHRR bind/unbind/
    bundle primitives via hdlab.goal_achievement.self_test_union_grounded_channel(), no DesireDB
    needed."""
    r_ga = ga_self_test()
    r_util = self_test_utility_channel()
    r_union_channel = self_test_union_grounded_channel()

    # metrics helpers sanity
    rr = recovery_rate(["Unfulfilled", "Unfulfilled", "Fulfilled"], ["Unfulfilled", "Fulfilled", "Fulfilled"])
    assert rr == {"n_majority_wrong": 2, "n_recovered": 1, "rate": 0.5}, rr
    rr0 = recovery_rate(["Fulfilled", "Fulfilled"], ["Fulfilled", "Fulfilled"])
    assert rr0["rate"] is None

    # arms-must-differ hash-test sanity
    same = _arms_must_differ({n: ["A", "B"] for n in ARM_NAMES})
    assert same["arms_differ"] is False
    diff_preds = {n: ["A", "B"] for n in ARM_NAMES}
    diff_preds["vi_union"] = ["A", "C"]
    diff = _arms_must_differ(diff_preds)
    assert diff["arms_differ"] is True

    # fit_hypotheses end-to-end sanity (fast, no DesireDB).
    hyps = fit_hypotheses()
    assert hyps["resulttype_fit_ok"], "M2 induction abstained on TRAIN"
    assert hyps["relation_fit_ok"], "fork-A induction abstained on TRAIN"

    # composed_verdict_base / composed_verdict_union sanity on a hand-authored abstain-to-majority
    # pair (the union's own case1 flagship -- goal_achievement_verdict's channel=='majority' here, so
    # composed_verdict_base defaults to MAJORITY_CLASS=='Fulfilled'; the union channel recovers
    # 'Unfulfilled' via resulttype precedence -- a genuine flip, proving the wiring actually engages).
    desire = "My girl [wanted to] act it out in real life, even wanting to move to England! Uh. No."
    outcome = "Uh. No. Uh. No."
    assert goal_achievement_verdict(desire, outcome)["channel"] == "majority", "fixture assumption broken"
    assert composed_verdict_base(desire, outcome) == MAJORITY_CLASS
    assert composed_verdict_union(desire, outcome, hyps) == "Unfulfilled", "UNION WIRING FAILURE in self-test"

    return {"goal_achievement_self_test": r_ga, "utility_channel_self_test": r_util,
            "union_grounded_channel_self_test": r_union_channel,
            "hyps_fit_ok": {"resulttype": hyps["resulttype_fit_ok"], "relation": hyps["relation_fit_ok"]},
            "composed_wiring_sanity": True, "helpers_ok": True}


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.full):
        t0 = time.time()
        result = self_test()
        elapsed = time.time() - t0
        metrics = {"verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS", "summary": "self-test green",
                   "elapsed_s": round(elapsed, 3), "run_mode": "self_test", "anchor_name": ANCHOR_NAME,
                   "result": result}
        _write_metrics(OUTPUT_DIR, metrics)
        print(json.dumps(metrics, indent=2, default=str))
        return

    run_mode = "smoke" if args.smoke else "full"
    output_dir = OUTPUT_DIR + "_smoke" if args.smoke else OUTPUT_DIR
    expected_units = len(ARM_NAMES)  # 7, PRIMARY cohort only
    _write_start_marker(output_dir, run_mode, expected_units)
    t0 = time.time()

    print(f"[{run_mode}] fitting M2 + fork-A hypotheses (no DesireDB)...", flush=True)
    hyps = fit_hypotheses()
    print(f"[{run_mode}] resulttype_fit_ok={hyps['resulttype_fit_ok']} relation_fit_ok={hyps['relation_fit_ok']}",
          flush=True)
    if not (hyps["resulttype_fit_ok"] and hyps["relation_fit_ok"]):
        elapsed = time.time() - t0
        msg = "HYPOTHESIS_FIT_FAILURE: M2 or fork-A induction abstained on its own TRAIN set."
        metrics = {"verdict": "HARD_FAIL", "verdict_msg": msg, "summary": f"HARD_FAIL: {msg}",
                   "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
                   "cardinality_ok": True, "expected_n_units": expected_units,
                   "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
                   "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
                   "deterministic_seeding": True}
        _write_metrics(output_dir, metrics)
        print(json.dumps(metrics, indent=2, default=str))
        return

    print(f"[{run_mode}] loading DesireDB...", flush=True)
    rows = _s2.load_desiredb_rows()
    print(f"[{run_mode}] {len(rows)} binary-eligible rows loaded", flush=True)
    # DISCRIMINATOR-MUST-SURVIVE-SCALE option (A): smoke uses the SAME FULL_N_PER_CLASS draw as
    # --full (M1/M2/M3-inc1/fork-A's own precedent -- a reduced-N smoke draw was MEASURED underpowered
    # in M2's own design probe, cohort n=11 < MIN_COHORT_N=15).
    n_per_class = FULL_N_PER_CLASS
    sample = _s2.balanced_subsample(rows, n_per_class, SEED)
    print(f"[{run_mode}] PRIMARY sample n={len(sample)} (n_per_class={n_per_class}, seed={SEED})", flush=True)

    cohort_idxs = _s2.build_cohort(sample)
    cohort_n = len(cohort_idxs)
    print(f"[{run_mode}] PRIMARY cohort(abstain-to-majority) n={cohort_n} of {len(sample)}", flush=True)

    arms = run_cohort_arms(sample, cohort_idxs, hyps)
    for idx, name in enumerate(ARM_NAMES):
        record_unit(output_dir, unit_key(name), {"arm": name, "n": cohort_n})
        _write_heartbeat(output_dir, idx, expected_units + 2, time.time() - t0)

    diff_check = _arms_must_differ(arms["preds"])
    activation_fires_rate = sum(arms["activation_fires"]) / cohort_n if cohort_n else 0.0
    verdict_fires_rate_union = sum(arms["verdict_fires_union"]) / cohort_n if cohort_n else 0.0
    print(f"[{run_mode}] activation_fires_rate={activation_fires_rate:.3f} "
          f"verdict_fires_rate_union={verdict_fires_rate_union:.3f}", flush=True)

    accs = {name: _s2.accuracy(arms["gold"], arms["preds"][name]) for name in ARM_NAMES}
    macro_f1s = {name: _s2.macro_f1(arms["gold"], arms["preds"][name]) for name in ARM_NAMES}
    cohort_metrics = {
        "cohort_n": cohort_n,
        "activation_fires_rate": round(activation_fires_rate, 4),
        "verdict_fires_rate_union": round(verdict_fires_rate_union, 4),
        "gold_dist": {"Fulfilled": arms["gold"].count("Fulfilled"),
                      "Unfulfilled": arms["gold"].count("Unfulfilled")},
        **{f"acc_{name}": round(accs[name], 4) for name in ARM_NAMES},
        **{f"macro_f1_{name}": round(macro_f1s[name], 4) for name in ARM_NAMES},
        "recovery_i": recovery_rate(arms["gold"], arms["preds"]["i"]),
        "recovery_ii": recovery_rate(arms["gold"], arms["preds"]["ii"]),
        "recovery_iii_m2": recovery_rate(arms["gold"], arms["preds"]["iii_m2"]),
        "recovery_iv_m1": recovery_rate(arms["gold"], arms["preds"]["iv_m1"]),
        "recovery_v_relation": recovery_rate(arms["gold"], arms["preds"]["v_relation"]),
        "recovery_vi_union": recovery_rate(arms["gold"], arms["preds"]["vi_union"]),
        "recovery_vii_union_scr": recovery_rate(arms["gold"], arms["preds"]["vii_union_scr"]),
        "per_item_attribution_primary": arms["per_item_attribution"],
    }

    if run_mode == "smoke":
        rec_union = cohort_metrics["recovery_vi_union"]
        if cohort_n < MIN_COHORT_N:
            verdict, msg = "INVALID", f"SMOKE_UNDERPOWERED_COHORT: n={cohort_n} (need >={MIN_COHORT_N})"
        elif activation_fires_rate == 0.0 and verdict_fires_rate_union == 0.0:
            verdict, msg = "HARD_FAIL", ("SMOKE_NEVER_FIRED: activation_fires_rate=0.0 AND "
                                          "verdict_fires_rate_union=0.0 on cohort")
        elif not diff_check["arms_differ"]:
            verdict, msg = "HARD_FAIL", f"SMOKE_ARMS_IDENTICAL: {diff_check['digests']}"
        else:
            verdict = "HARD_PASS"
            msg = (f"SMOKE_OK: cohort n={cohort_n} activation_fires_rate={activation_fires_rate:.3f} "
                   f"verdict_fires_rate_union={verdict_fires_rate_union:.3f} "
                   f"recovery_union={rec_union['rate']} ({rec_union['n_recovered']}/{rec_union['n_majority_wrong']}) "
                   f"recovery_m2={cohort_metrics['recovery_iii_m2']['rate']} "
                   f"recovery_m1={cohort_metrics['recovery_iv_m1']['rate']} "
                   f"recovery_relation={cohort_metrics['recovery_v_relation']['rate']} "
                   f"arms_differ={diff_check['arms_differ']}")
        elapsed = time.time() - t0
        metrics = {
            "verdict": verdict, "verdict_msg": msg, "summary": f"{verdict}: {msg}",
            "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
            "n_sample": len(sample), "n_per_class": n_per_class, "seed": SEED,
            "cohort_metrics": cohort_metrics,
            "arms_differ_verified": diff_check["arms_differ"], "arms_digests": diff_check["digests"],
            "cardinality_ok": len(load_units(output_dir)) == expected_units,
            "expected_n_units": expected_units,
            "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
            "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
            "deterministic_seeding": True,
        }
        _write_metrics(output_dir, metrics)
        print(json.dumps({k: v for k, v in metrics.items() if k != "cohort_metrics"}, indent=2, default=str))
        print(json.dumps({"cohort_metrics": {k: v for k, v in cohort_metrics.items()
                                              if k != "per_item_attribution_primary"}}, indent=2, default=str))
        return

    # ---- FULL: harness validity + full-bench comparison (n=80, n=160) + breadth + WIRE decision ----
    validity = harness_validity_check()
    print(f"[{run_mode}] harness_validity_check: measured_macro_f1={validity['measured_macro_f1']} "
          f"(documented=0.686) valid={validity['valid']}", flush=True)
    _write_heartbeat(output_dir, expected_units, expected_units + 2, time.time() - t0)

    print(f"[{run_mode}] full-bench comparison n=80...", flush=True)
    full_bench_80 = full_bench_comparison(VALIDITY_N_PER_CLASS, hyps)
    print(f"[{run_mode}] full-bench comparison n=160...", flush=True)
    full_bench_160 = full_bench_comparison(FULL_N_PER_CLASS, hyps)
    print(f"[{run_mode}] full_bench_80 base={full_bench_80['base']['macro_f1']} "
          f"union={full_bench_80['union']['macro_f1']} | full_bench_160 base={full_bench_160['base']['macro_f1']} "
          f"union={full_bench_160['union']['macro_f1']}", flush=True)
    _write_heartbeat(output_dir, expected_units + 1, expected_units + 2, time.time() - t0)

    print(f"[{run_mode}] running BREADTH cohort context (n={ENLARGED_N_ROWS} rows)...", flush=True)
    breadth = breadth_cohort_analysis(hyps)
    print(f"[{run_mode}] BREADTH recovery_union={breadth['recovery_union']['rate']} "
          f"({breadth['recovery_union']['n_recovered']}/{breadth['recovery_union']['n_majority_wrong']}) "
          f"union_beats_max_single={breadth['union_beats_max_single']}", flush=True)

    overall_verdict, overall_msg, wire_decision = compute_wire_verdict(
        cohort_metrics, breadth, full_bench_160, full_bench_80, validity, cohort_n)

    elapsed = time.time() - t0
    metrics = {
        "verdict": overall_verdict, "verdict_msg": overall_msg, "summary": f"{overall_verdict}: {overall_msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "n_sample": len(sample), "n_per_class": n_per_class, "seed": SEED,
        "wire_decision": wire_decision,
        "cohort_metrics": cohort_metrics,
        "arms_differ_verified": diff_check["arms_differ"], "arms_digests": diff_check["digests"],
        "harness_validity_check": validity,
        "full_bench_n80": full_bench_80, "full_bench_n160": full_bench_160,
        "breadth_cohort_context": breadth,
        "cardinality_ok": len(load_units(output_dir)) == expected_units,
        "expected_n_units": expected_units,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "deterministic construction-cue-vote learners (M2 resulttype + fork-A relation, "
                    "estimation/ruleind over fixed boolean feature spaces) + WordNet-MWE dictionary "
                    "lookup (fork-A disengagement) + hand-authored idiom-phrase regex (M1) + FHRR "
                    "bind/bundle/cleanup over a fixed 6-role x 3-filler codebook PLUS the separately-"
                    "seeded 1-role RELATION_LINK fallback codebook -- identical justification to "
                    "Stage-2/M1/M2/M3-inc1/fork-A's crlb_n/a, unchanged FHRR mechanism layer",
        "deterministic_seeding": True,
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps({k: v for k, v in metrics.items()
                       if k not in ("cohort_metrics", "breadth_cohort_context")},
                      indent=2, default=str))
    print(json.dumps({"cohort_metrics": {k: v for k, v in cohort_metrics.items()
                                          if k != "per_item_attribution_primary"}}, indent=2, default=str))
    print(json.dumps({"per_item_attribution_primary": cohort_metrics["per_item_attribution_primary"]},
                      indent=2, default=str))
    print(json.dumps({"breadth_cohort_context": {k: v for k, v in breadth.items()
                                                  if k != "per_item_attribution"}}, indent=2, default=str))
    print(json.dumps({"breadth_per_item_attribution": breadth["per_item_attribution"]}, indent=2, default=str))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- deliberately not BaseException, see cell-template mandate
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
