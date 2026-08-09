# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (deterministic construction-cue-vote learner + WordNet-MWE dictionary lookup +
#   FHRR bind/bundle/cleanup, fixed small codebooks, no decoded/noisy continuous signal)
# - HP_SCOPE per-arm declaration (arm iii gates HARD_PASS/HARD_FAIL for GATE-2; others comparators)
# - cardinality_ok: EXPECTED_N_UNITS=4 (one unit per PRIMARY-cohort arm)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (see prereg)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL FHRR bind/unbind/bundle primitives + goal_outcome_relation module
#   (real_code_path); no synthetic-only branch
# - progress_logging: print_flush_true
# See preregs/2026-08-09_direction_b_A_goal_outcome_relation_v1.md for the full pre-reg, INCLUDING
# the mandatory "Scope changes" section (two Director+USER design refinements applied mid-build).
"""exp_direction_b_A_goal_outcome_relation_v1 -- Direction-B fork-A: does a GOAL<->OUTCOME
SEMANTIC-RELATION mechanism recover the DesireDB abstain-cohort residual after M1 (idiom lexicon,
0/37 breadth) and M2/M3-inc1 (learned result-type classifier, "no returns" HARD_FAIL, 3/8 primary /
9/37 breadth)? TWO structurally different sub-mechanisms (hdlab.goal_outcome_relation, see that
module's docstring for the full design + the 2026-08-09 mid-build scope changes):

  GATE-1a: MEANS-END + self-reliance construction -- genuinely COMPOSITIONAL verb-class relations,
    measured via held-out-surface-form GENERALIZATION accuracy of a learned classifier
    (hdlab.learner.registry.learn over construction-cue atoms).
  GATE-1b: CONVENTIONALIZED-CONTRADICTION (disengagement) -- NON-COMPOSITIONAL, measured via
    WordNet-MWE dictionary-lookup COVERAGE against a representative phrase bank, NOT generalization
    accuracy of a learned classifier (idioms share nothing lexically with each other).
  3-way split: (a) dictionary-tractable conventionalized (GATE-1b coverage), (b) concept-relation-
    tractable means-end+self-reliance (GATE-1a subtype accuracy), (c) genuinely-open-world (GATE-1b
    disclosed misses + unrecovered GATE-2 residual).
  GATE-2 (recovery, only runs if GATE-1a clears its HARD-FAIL floor): applies the combined mechanism
    (hdlab.goal_achievement.utility_channel_relation_grounded) to the IDENTICAL M1/Stage-2/M2/M3-inc1
    abstain-to-majority PRIMARY cohort (n=160 draw / cohort n=22, SEED=20260808) + ENLARGED BREADTH
    context cohort (900-row, ENLARGED_SEED=20260809, cohort n=152/37 gold-Unfulfilled).

Arms (PRIMARY cohort):
  (i)   majority-only baseline                                          [Stage-2/M1/M2/M3-inc1 arm i]
  (ii)  utility_channel (Stage-2, WordNet-only)                          [arm ii, unchanged]
  (iii) utility_channel_relation_grounded                                [THE FORK-A MECHANISM ARM]
  (iv)  utility_channel_relation_grounded, SCRAMBLED goal cue            [mandatory pairscramble]

Modes:
  --self-test  GATE-1a fit + held-out eval (hdlab.goal_outcome_relation.self_test, which also
               exercises GATE-1b's dictionary-coverage regression guard) +
               hdlab.goal_achievement.self_test_relation_grounded_channel real-cohort-case
               mechanism-fires checks. No DesireDB needed.
  --smoke      GATE-1a+1b (full, fast) + a DesireDB PRIMARY cohort probe (arms i/ii/iii/iv,
               mechanism-fires + arms-differ checks only, no HARD_PASS/HARD_FAIL claim).
  --full       GATE-1a -> (if >=0.40 held_out_acc) GATE-2 PRIMARY cohort (gate-defining) + ENLARGED
               BREADTH cohort (context) -> combined verdict + 3-way split report.
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

ANCHOR_NAME = "direction_b_A_goal_outcome_relation_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

import exp_utility_satisfaction_channel_v1 as _s2  # noqa: E402 -- reuse loader/cohort/metrics verbatim

from hdlab.goal_achievement import (  # noqa: E402
    goal_achievement_verdict, utility_channel, utility_channel_relation_grounded, activate_attributes,
    self_test_utility_channel, self_test_relation_grounded_channel, self_test as ga_self_test,
    MAJORITY_CLASS,
)
from hdlab import goal_outcome_relation as _gor  # noqa: E402

SEED = _s2.SEED  # 20260808, identical draw to Stage-2/M1/M2/M3-inc1
FULL_N_PER_CLASS = _s2.FULL_N_PER_CLASS  # 80 -> n=160, the exact cohort n=22/8 draw
VALIDITY_N_PER_CLASS = _s2.VALIDITY_N_PER_CLASS  # 40 -> n=80, documented-baseline harness

# GATE-1a (means-end + self-reliance generalization) bands. MEASURED@this session's design-probe
# (hdlab.goal_outcome_relation.self_test(), reproduced identically by this cell's own run_gate1a()):
# held_out_acc=1.0 (11/11), memorization_baseline_acc=0.6364, scramble_control_acc=0.6364.
GATE1A_HP_HELDOUT_ACC = 0.60
GATE1A_HP_DELTA_VS_MEM = 0.15
GATE1A_HARD_FAIL_HELDOUT_ACC = 0.40   # kill criterion: STOP, do not run GATE-2 (DesireDB)
GATE1A_SCRAMBLE_COLLAPSE_MAX = 0.35   # near-chance/near-majority-class-rate; MEASURED this session
                                       # the 3-class TRAIN majority share makes a naive 0.35 ceiling
                                       # too strict for this small a bank -- reported honestly (see
                                       # run_gate1a's own scramble_collapses_strict vs the delta-based
                                       # HARD-PASS/HARD-FAIL disjuncts, which do not require it).

# GATE-2 (recovery) bands -- reused verbatim from M1/M2/M3-inc1 (same cohort, same definitions).
GATE2_HP_RECOVERY = 0.40
GATE2_HARD_FAIL_RECOVERY = 0.15
GATE2_PAIRSCRAMBLE_MAX_DELTA_VS_BASELINE = 0.05   # |scr-i| <= this -> collapses
GATE2_PAIRSCRAMBLE_MAX_DELTA_VS_REAL = 0.03       # |scr-mech| <= this -> leaks (non-goal-conditioned)
VALIDITY_TOLERANCE = 0.03
MIN_COHORT_N = 15

ARM_NAMES = ("i", "ii", "iii", "iv")
ENLARGED_N_ROWS = 900          # identical to M1/M2/M3-inc1 (compute-proportionality; head-to-head
                                # comparability with their measured 0/37 and 9/37 breadth numbers).
ENLARGED_SEED = 20260809


# ============================================================================ GATE-1a: means-end +
# self-reliance generalization
def run_gate1a() -> dict:
    """Fit hdlab.goal_outcome_relation's learner on TRAIN_EXAMPLES; evaluate held-out-surface-form
    generalization + memorization baseline + scramble control + per-subtype breakdown. Returns the
    full report dict (including the fitted (chosen_name, hypothesis) for GATE-2 reuse)."""
    train_eps = [_gor.build_episode(d, o, c, tag) for d, o, c, tag in _gor.TRAIN_EXAMPLES]
    held_eps = [_gor.build_episode(d, o, c, tag) for d, o, c, tag in _gor.HELDOUT_EXAMPLES]
    chosen_name, chosen, all_results = _gor.induce(train_eps)
    if chosen is None:
        return {"verdict_component": "HARD_FAIL", "reason": "GATE1A_INDUCTION_ABSTAINED_ON_TRAIN",
                "held_out_acc": 0.0, "memorization_baseline_acc": None, "scramble_control_acc": None,
                "chosen_name": None, "hypothesis": None}
    majority_train = max(_gor.RELATION_TYPES,
                          key=lambda c: sum(1 for e in train_eps if e["gold_class"] == c))

    def _eval(name, hyp, eps, examples):
        preds, gold, per_item = [], [], []
        for e, (d, o, c, tag) in zip(eps, examples):
            key = "|".join(sorted(e["feats"]))
            pred = _gor.predict(name, hyp, e["feats"], key, default=majority_train)
            preds.append(pred)
            gold.append(e["gold_class"])
            per_item.append({"tag": tag, "gold": c, "pred": pred, "ok": pred == c})
        acc = sum(p == g for p, g in zip(preds, gold)) / len(eps)
        return acc, per_item

    held_acc, held_per_item = _eval(chosen_name, chosen.hypothesis, held_eps, _gor.HELDOUT_EXAMPLES)
    mem_correct = 0
    for (d, o, c, tag) in _gor.HELDOUT_EXAMPLES:
        mem_pred = _gor.memorization_baseline_predict(_gor.TRAIN_EXAMPLES, tag, majority_train)
        mem_correct += (mem_pred == c)
    mem_acc = mem_correct / len(_gor.HELDOUT_EXAMPLES)

    rng = random.Random(20260809)
    scrambled_labels = [e["gold_class"] for e in train_eps]
    rng.shuffle(scrambled_labels)
    scr_train_eps = [{"feats": e["feats"], "gold_class": scrambled_labels[i], "tag": e["tag"]}
                      for i, e in enumerate(train_eps)]
    scr_name, scr_chosen, _ = _gor.induce(scr_train_eps)
    scr_acc, _sp = _eval(scr_name, scr_chosen.hypothesis if scr_chosen else None, held_eps,
                          _gor.HELDOUT_EXAMPLES)

    per_item_by_tag = {it["tag"]: it for it in held_per_item}
    subtype_acc = {}
    for sub, tags in _gor.HELDOUT_SUBTYPES.items():
        n_ok = sum(1 for t in tags if per_item_by_tag[t]["ok"])
        subtype_acc[sub] = round(n_ok / len(tags), 4)

    delta_vs_mem = held_acc - mem_acc
    scramble_collapses_strict = scr_acc <= GATE1A_SCRAMBLE_COLLAPSE_MAX
    hard_fail = held_acc < GATE1A_HARD_FAIL_HELDOUT_ACC
    hard_pass = (not hard_fail) and (held_acc >= GATE1A_HP_HELDOUT_ACC) and \
                (delta_vs_mem >= GATE1A_HP_DELTA_VS_MEM) and scramble_collapses_strict
    verdict_component = "HARD_FAIL" if hard_fail else ("HARD_PASS" if hard_pass else "MIDDLE_BAND")

    return {
        "verdict_component": verdict_component,
        "chosen_name": chosen_name, "hypothesis": chosen.hypothesis,
        "chosen_plugin_description_bits": {k: round(v.description_bits, 3) for k, v in all_results.items()},
        "n_train": len(train_eps), "n_heldout": len(held_eps),
        "held_out_acc": round(held_acc, 4), "memorization_baseline_acc": round(mem_acc, 4),
        "scramble_control_acc": round(scr_acc, 4), "delta_vs_memorization": round(delta_vs_mem, 4),
        "scramble_collapses_strict": scramble_collapses_strict, "majority_train_class": majority_train,
        "subtype_acc": subtype_acc, "held_per_item": held_per_item,
    }


def run_gate1b() -> dict:
    """WordNet-MWE dictionary COVERAGE (not a learned classifier) -- see hdlab.goal_outcome_relation.
    contradiction_dictionary_coverage's docstring."""
    return _gor.contradiction_dictionary_coverage()


# ============================================================================ GATE-2: PRIMARY cohort arms
def run_cohort_arms(sample: list, cohort_idxs: list, chosen_name, hypothesis) -> dict:
    scrambled_cues = _s2._scrambled_desires(sample)
    gold = []
    preds = {name: [] for name in ARM_NAMES}
    activation_fires, verdict_fires_iii = [], []
    relation_traces = []
    for i in cohort_idxs:
        r = sample[i]
        desire, outcome = r["Desire-Expression-Sentence"], r["Evidence"]
        gold.append(r["Fulfillment-Label"])
        activation_fires.append(len(activate_attributes(desire)) > 0)

        preds["i"].append(MAJORITY_CLASS)
        u_wn = utility_channel(desire, outcome)
        preds["ii"].append(u_wn if u_wn is not None else MAJORITY_CLASS)

        u_rel = utility_channel_relation_grounded(desire, outcome, chosen_name, hypothesis)
        preds["iii"].append(u_rel if u_rel is not None else MAJORITY_CLASS)
        verdict_fires_iii.append(u_rel is not None)

        u_scr = utility_channel_relation_grounded(scrambled_cues[i], outcome, chosen_name, hypothesis)
        preds["iv"].append(u_scr if u_scr is not None else MAJORITY_CLASS)

        rv = _gor.relation_votes(desire, outcome, chosen_name, hypothesis)
        relation_traces.append({"idx": i, "gold": r["Fulfillment-Label"],
                                 "matched": rv["matched"], "source": rv.get("source")})
    return {"gold": gold, "preds": preds, "activation_fires": activation_fires,
            "verdict_fires_iii": verdict_fires_iii, "relation_traces": relation_traces}


def recovery_rate(gold, pred) -> dict:
    """Identical definition to Stage-2/M1/M2/M3-inc1's own recovery_rate: of the cohort items where
    the majority-only baseline is WRONG (gold=='Unfulfilled'), the fraction `pred` gets CORRECT."""
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


# ============================================================================ ENLARGED cohort (context)
def enlarged_cohort_analysis(chosen_name, hypothesis) -> dict:
    """Deterministic-seeded ENLARGED_N_ROWS-row subsample cohort + arm-iii recovery + a bigger-n
    pairscramble-collapse corroboration. Computed ONCE -- context, not gate-defining. Reuses M1's
    exact ENLARGED_SEED/ENLARGED_N_ROWS for head-to-head comparability with M1's 0/37, M2/M3-inc1's
    9/37."""
    import random as _random
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

    n_recovered = 0
    source_counter: dict = {}
    match_counter: dict = {}
    for i in gold_unfulfilled_local:
        r = sub_rows[i]
        desire, outcome = r["Desire-Expression-Sentence"], r["Evidence"]
        pred = utility_channel_relation_grounded(desire, outcome, chosen_name, hypothesis)
        if pred == "Unfulfilled":
            n_recovered += 1
        rv = _gor.relation_votes(desire, outcome, chosen_name, hypothesis)
        src = rv.get("source", "none")
        source_counter[src] = source_counter.get(src, 0) + 1
        for m in rv["matched"]:
            match_counter[m] = match_counter.get(m, 0) + 1

    gold_cohort = [sub_rows[i]["Fulfillment-Label"] for i in cohort_local_idxs]
    pred_i_cohort = [MAJORITY_CLASS for _ in cohort_local_idxs]
    pred_scr_cohort = []
    for i in cohort_local_idxs:
        u = utility_channel_relation_grounded(scrambled[i], sub_rows[i]["Evidence"], chosen_name, hypothesis)
        pred_scr_cohort.append(u if u is not None else MAJORITY_CLASS)
    acc_i_cohort = _s2.accuracy(gold_cohort, pred_i_cohort)
    acc_scr_cohort = _s2.accuracy(gold_cohort, pred_scr_cohort)

    n_denom = len(gold_unfulfilled_local)
    return {
        "n_subsample_rows": len(sub_rows), "n_total_rows_available": len(rows),
        "cohort_n": len(cohort_local_idxs), "gold_unfulfilled_n": n_denom,
        "recovery_arm_iii": {
            "n_recovered": n_recovered, "n_majority_wrong": n_denom,
            "rate": round(n_recovered / n_denom, 4) if n_denom else None},
        "pairscramble_at_scale": {
            "cohort_n": len(cohort_local_idxs), "acc_i": round(acc_i_cohort, 4),
            "acc_scrambled_arm_iii": round(acc_scr_cohort, 4),
            "delta": round(abs(acc_scr_cohort - acc_i_cohort), 4),
            "collapses_at_scale": abs(acc_scr_cohort - acc_i_cohort) <= GATE2_PAIRSCRAMBLE_MAX_DELTA_VS_BASELINE},
        "relation_match_frequency": dict(sorted(match_counter.items(), key=lambda kv: -kv[1])),
        "relation_source_frequency": source_counter,
        "m1_enlarged_cohort_reference": {"recovery_rate": 0.0, "n_recovered": 0, "n_majority_wrong": 37,
                                          "source": "data/exp_direction_b_M1_idiom_grounding_recovery_v1/"
                                                    "metrics.json:enlarged_cohort_context."
                                                    "recovery_primary_mech_arm"},
        "m2_m3inc1_enlarged_cohort_reference": {"recovery_rate": 0.2432, "n_recovered": 9, "n_majority_wrong": 37,
                                                 "source": "data/exp_direction_b_M3inc1_coverage_expansion_v1/"
                                                           "metrics.json:returns_per_expansion."
                                                           "breadth_recovery_rate.v2_combined_plus_idiom_fallback"},
    }


def harness_validity_check() -> dict:
    """Re-verify (at every --full run) the loader+field-mapping+seed reproduces the documented
    3-channel macro-F1 0.686 (n=80, seed 20260808) -- identical to Stage-2/M1/M2/M3-inc1's own gate."""
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


# ============================================================================ combined verdict logic
def compute_gate2_verdict(cohort_metrics: dict, validity: dict, cohort_n: int) -> tuple:
    if cohort_n < MIN_COHORT_N:
        return "INVALID", f"UNDERPOWERED_COHORT: n={cohort_n} (need >={MIN_COHORT_N})"
    if not validity["valid"]:
        return "INVALID", f"harness_validity_check FAILED: delta_macro_f1={validity['delta_macro_f1']} exceeds tolerance {validity['tolerance']}"
    rec = cohort_metrics["recovery_iii"]
    if rec["rate"] is None:
        return "INVALID", "recovery_rate UNDEFINED: 0 gold-Unfulfilled items in cohort"

    rate = rec["rate"]
    acc_iii = cohort_metrics["acc_iii"]
    acc_iv = cohort_metrics["acc_iv"]
    acc_i = cohort_metrics["acc_i"]
    delta_scr_i = abs(acc_iv - acc_i)
    delta_scr_mech = abs(acc_iv - acc_iii)
    collapses = delta_scr_i <= GATE2_PAIRSCRAMBLE_MAX_DELTA_VS_BASELINE
    leaks = delta_scr_mech <= GATE2_PAIRSCRAMBLE_MAX_DELTA_VS_REAL

    hard_fail = (rate < GATE2_HARD_FAIL_RECOVERY) or leaks or (not collapses)
    hard_pass = (not hard_fail) and (rate >= GATE2_HP_RECOVERY) and collapses and not leaks

    verdict = "HARD_FAIL" if hard_fail else ("HARD_PASS" if hard_pass else "MIDDLE_BAND")
    msg = (f"GATE2 cohort n={cohort_n} activation_fires_rate={cohort_metrics['activation_fires_rate']:.3f} "
           f"recovery_iii={rate:.3f} ({rec['n_recovered']}/{rec['n_majority_wrong']}) "
           f"recovery_ii_stage2ref={cohort_metrics['recovery_ii']['rate']} "
           f"pairscramble(iv): |scr-i|={delta_scr_i:.4f} (<=0.05 collapse={collapses}) "
           f"|scr-mech|={delta_scr_mech:.4f} (>0.03 not-leak, leaks={leaks})")
    return verdict, msg


def combine_verdicts(gate1a_component: str, gate2_component: str) -> str:
    """HARD-FAIL if EITHER gate hard-fails; HARD-PASS only if BOTH hard-pass; else MIDDLE_BAND.
    GATE-1b (dictionary coverage) is reported, not gated -- it cannot fail/pass, it measures a
    coverage fraction (see prereg)."""
    if gate1a_component == "HARD_FAIL" or gate2_component in ("HARD_FAIL", "INVALID"):
        return "HARD_FAIL" if gate2_component != "INVALID" else "INVALID"
    if gate1a_component == "HARD_PASS" and gate2_component == "HARD_PASS":
        return "HARD_PASS"
    return "MIDDLE_BAND"


def build_three_way_split(gate1a: dict, gate1b: dict) -> dict:
    """The honest 3-way split the task's contract mandates: (a) dictionary-tractable conventionalized
    (GATE-1b coverage), (b) concept-relation-tractable means-end+self-reliance (GATE-1a subtype
    accuracy), (c) genuinely-open-world (GATE-1b disclosed misses)."""
    return {
        "a_dictionary_tractable_conventionalized": {
            "coverage": gate1b["coverage"], "n": gate1b["n"], "n_hit": gate1b["n_hit"],
            "provenance": gate1b["coverage_provenance"],
            "kaikki_wiktextract_flagged": gate1b["kaikki_wiktextract_flagged"],
        },
        "b_concept_relation_tractable_means_end_and_self_reliance": {
            "means_end_heldout_acc": gate1a["subtype_acc"].get("means_end"),
            "self_reliance_heldout_acc": gate1a["subtype_acc"].get("self_reliance_construction"),
            "held_out_acc_combined": gate1a["held_out_acc"],
            "delta_vs_memorization": gate1a["delta_vs_memorization"],
        },
        "c_genuinely_open_world": {
            "dictionary_misses_n": gate1b["n"] - gate1b["n_hit"],
            "dictionary_misses_fraction": round((gate1b["n"] - gate1b["n_hit"]) / gate1b["n"], 4),
            "dictionary_misses": [m["text"] for m in gate1b["misses"]],
        },
    }


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
    registry.learn() fit + REAL WordNet-MWE scan + real FHRR bind/unbind/bundle primitives via
    goal_outcome_relation.self_test() + goal_achievement.self_test_relation_grounded_channel(), no
    DesireDB needed."""
    r_ga = ga_self_test()
    r_util = self_test_utility_channel()
    r_gor_module = _gor.self_test()
    r_gor_channel = self_test_relation_grounded_channel()

    # metrics helpers sanity
    rr = recovery_rate(["Unfulfilled", "Unfulfilled", "Fulfilled"], ["Unfulfilled", "Fulfilled", "Fulfilled"])
    assert rr == {"n_majority_wrong": 2, "n_recovered": 1, "rate": 0.5}, rr
    rr0 = recovery_rate(["Fulfilled", "Fulfilled"], ["Fulfilled", "Fulfilled"])
    assert rr0["rate"] is None

    # arms-must-differ hash-test sanity
    same = _arms_must_differ({n: ["A", "B"] for n in ARM_NAMES})
    assert same["arms_differ"] is False
    diff_preds = {n: ["A", "B"] for n in ARM_NAMES}
    diff_preds["iii"] = ["A", "C"]
    diff = _arms_must_differ(diff_preds)
    assert diff["arms_differ"] is True

    # GATE-1a end-to-end sanity (fast, no DesireDB): mirrors _gor.self_test()'s own numbers.
    g1a = run_gate1a()
    assert g1a["chosen_name"] is not None, "GATE-1a induction abstained on TRAIN"
    assert g1a["held_out_acc"] > g1a["memorization_baseline_acc"], g1a
    assert g1a["held_out_acc"] > g1a["scramble_control_acc"], g1a

    # GATE-1b sanity (fast, no DesireDB, dictionary lookup).
    g1b = run_gate1b()
    assert g1b["coverage"] > 0.5, g1b
    assert g1b["false_positive_count"] == 0, g1b

    return {"goal_achievement_self_test": r_ga, "utility_channel_self_test": r_util,
            "goal_outcome_relation_self_test": {k: v for k, v in r_gor_module.items()
                                                 if k not in ("held_per_item", "dictionary_coverage_misses")},
            "relation_grounded_channel_self_test": r_gor_channel,
            "gate1a_selftest_repro": {"held_out_acc": g1a["held_out_acc"],
                                       "memorization_baseline_acc": g1a["memorization_baseline_acc"],
                                       "scramble_control_acc": g1a["scramble_control_acc"],
                                       "subtype_acc": g1a["subtype_acc"],
                                       "verdict_component": g1a["verdict_component"]},
            "gate1b_selftest_repro": {"coverage": g1b["coverage"], "n_hit": g1b["n_hit"], "n": g1b["n"],
                                       "false_positive_count": g1b["false_positive_count"]},
            "helpers_ok": True}


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
    expected_units = len(ARM_NAMES)  # 4, PRIMARY cohort only
    _write_start_marker(output_dir, run_mode, expected_units)
    t0 = time.time()

    print(f"[{run_mode}] running GATE-1a (means-end + self-reliance generalization, no DesireDB)...", flush=True)
    gate1a = run_gate1a()
    print(f"[{run_mode}] GATE-1a: held_out_acc={gate1a['held_out_acc']} "
          f"mem_acc={gate1a['memorization_baseline_acc']} scr_acc={gate1a['scramble_control_acc']} "
          f"subtype_acc={gate1a['subtype_acc']} component={gate1a['verdict_component']}", flush=True)
    print(f"[{run_mode}] running GATE-1b (disengagement dictionary coverage, no DesireDB)...", flush=True)
    gate1b = run_gate1b()
    print(f"[{run_mode}] GATE-1b: coverage={gate1b['coverage']} ({gate1b['n_hit']}/{gate1b['n']}) "
          f"false_positive_count={gate1b['false_positive_count']}", flush=True)
    _write_heartbeat(output_dir, 0, expected_units + 1, time.time() - t0)

    if gate1a["verdict_component"] == "HARD_FAIL":
        elapsed = time.time() - t0
        msg = (f"GATE1A_HARD_FAIL: held_out_acc={gate1a['held_out_acc']} < {GATE1A_HARD_FAIL_HELDOUT_ACC} "
               f"-- the means-end+self-reliance construction-cue classifier does NOT generalize across "
               f"surface forms. STOPPING per anti-circular design mandate; GATE-2 (DesireDB) NOT run.")
        metrics = {
            "verdict": "HARD_FAIL", "verdict_msg": msg, "summary": f"HARD_FAIL: {msg}",
            "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
            "gate1a": {k: v for k, v in gate1a.items() if k != "hypothesis"}, "gate1b": gate1b,
            "three_way_split": build_three_way_split(gate1a, gate1b),
            "gate2": None, "enlarged_cohort_context": None, "harness_validity_check": None,
            "cardinality_ok": True, "expected_n_units": expected_units,
            "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
            "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
            "crlb_n/a": "deterministic construction-cue-vote learner (estimation/ruleind over a fixed "
                        "8-atom boolean feature space) + WordNet-MWE dictionary lookup (deterministic "
                        "gloss-keyword match) -- identical justification to Stage-2/M1/M2/M3-inc1's "
                        "crlb_n/a, unchanged FHRR mechanism layer",
            "deterministic_seeding": True,
        }
        _write_metrics(output_dir, metrics)
        print(json.dumps({k: v for k, v in metrics.items() if k not in ("gate1a", "gate1b")},
                          indent=2, default=str))
        return

    chosen_name, hypothesis = gate1a["chosen_name"], gate1a["hypothesis"]

    print(f"[{run_mode}] loading DesireDB...", flush=True)
    rows = _s2.load_desiredb_rows()
    print(f"[{run_mode}] {len(rows)} binary-eligible rows loaded", flush=True)
    # DISCRIMINATOR-MUST-SURVIVE-SCALE option (A): smoke uses the SAME FULL_N_PER_CLASS draw as
    # --full (M1/M2/M3-inc1's own precedent -- a reduced-N smoke draw was MEASURED underpowered in
    # M2's own design probe, cohort n=11 < MIN_COHORT_N=15).
    n_per_class = FULL_N_PER_CLASS
    sample = _s2.balanced_subsample(rows, n_per_class, SEED)
    print(f"[{run_mode}] PRIMARY sample n={len(sample)} (n_per_class={n_per_class}, seed={SEED})", flush=True)

    cohort_idxs = _s2.build_cohort(sample)
    cohort_n = len(cohort_idxs)
    print(f"[{run_mode}] PRIMARY cohort(abstain-to-majority) n={cohort_n} of {len(sample)}", flush=True)

    arms = run_cohort_arms(sample, cohort_idxs, chosen_name, hypothesis)
    for idx, name in enumerate(ARM_NAMES):
        record_unit(output_dir, unit_key(name), {"arm": name, "n": cohort_n})
        _write_heartbeat(output_dir, idx + 1, expected_units + 1, time.time() - t0)

    diff_check = _arms_must_differ(arms["preds"])
    activation_fires_rate = sum(arms["activation_fires"]) / cohort_n if cohort_n else 0.0
    verdict_fires_rate_iii = sum(arms["verdict_fires_iii"]) / cohort_n if cohort_n else 0.0
    print(f"[{run_mode}] activation_fires_rate={activation_fires_rate:.3f} "
          f"verdict_fires_rate_iii={verdict_fires_rate_iii:.3f}", flush=True)

    accs = {name: _s2.accuracy(arms["gold"], arms["preds"][name]) for name in ARM_NAMES}
    macro_f1s = {name: _s2.macro_f1(arms["gold"], arms["preds"][name]) for name in ARM_NAMES}
    cohort_metrics = {
        "cohort_n": cohort_n,
        "activation_fires_rate": round(activation_fires_rate, 4),
        "verdict_fires_rate_iii": round(verdict_fires_rate_iii, 4),
        "gold_dist": {"Fulfilled": arms["gold"].count("Fulfilled"),
                      "Unfulfilled": arms["gold"].count("Unfulfilled")},
        **{f"acc_{name}": round(accs[name], 4) for name in ARM_NAMES},
        **{f"macro_f1_{name}": round(macro_f1s[name], 4) for name in ARM_NAMES},
        "recovery_i": recovery_rate(arms["gold"], arms["preds"]["i"]),
        "recovery_ii": recovery_rate(arms["gold"], arms["preds"]["ii"]),
        "recovery_iii": recovery_rate(arms["gold"], arms["preds"]["iii"]),
        "recovery_iv": recovery_rate(arms["gold"], arms["preds"]["iv"]),
        "relation_traces_gold_unfulfilled": [t for t in arms["relation_traces"] if t["gold"] == "Unfulfilled"],
    }

    if run_mode == "smoke":
        rec_iii = cohort_metrics["recovery_iii"]
        if cohort_n < MIN_COHORT_N:
            verdict, msg = "INVALID", f"SMOKE_UNDERPOWERED_COHORT: n={cohort_n} (need >={MIN_COHORT_N})"
        elif activation_fires_rate == 0.0 and verdict_fires_rate_iii == 0.0:
            verdict, msg = "HARD_FAIL", ("SMOKE_NEVER_FIRED: activation_fires_rate=0.0 AND "
                                          "verdict_fires_rate_iii=0.0 on cohort")
        elif not diff_check["arms_differ"]:
            verdict, msg = "HARD_FAIL", f"SMOKE_ARMS_IDENTICAL: {diff_check['digests']}"
        else:
            verdict = "HARD_PASS"
            msg = (f"SMOKE_OK: GATE1A_component={gate1a['verdict_component']} "
                   f"GATE1B_coverage={gate1b['coverage']} cohort n={cohort_n} "
                   f"activation_fires_rate={activation_fires_rate:.3f} "
                   f"verdict_fires_rate_iii={verdict_fires_rate_iii:.3f} "
                   f"recovery_iii={rec_iii['rate']} ({rec_iii['n_recovered']}/{rec_iii['n_majority_wrong']}) "
                   f"arms_differ={diff_check['arms_differ']}")
        elapsed = time.time() - t0
        metrics = {
            "verdict": verdict, "verdict_msg": msg, "summary": f"{verdict}: {msg}",
            "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
            "n_sample": len(sample), "n_per_class": n_per_class, "seed": SEED,
            "gate1a": {k: v for k, v in gate1a.items() if k != "hypothesis"}, "gate1b": gate1b,
            "cohort_metrics": cohort_metrics,
            "arms_differ_verified": diff_check["arms_differ"], "arms_digests": diff_check["digests"],
            "cardinality_ok": len(load_units(output_dir)) == expected_units,
            "expected_n_units": expected_units,
            "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
            "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
            "deterministic_seeding": True,
        }
        _write_metrics(output_dir, metrics)
        print(json.dumps({k: v for k, v in metrics.items() if k not in ("cohort_metrics", "gate1a", "gate1b")},
                          indent=2, default=str))
        print(json.dumps({"cohort_metrics": cohort_metrics}, indent=2, default=str))
        return

    # ---- FULL: harness validity + combined verdict + enlarged cohort context + 3-way split ----
    validity = harness_validity_check()
    verdict2, msg2 = compute_gate2_verdict(cohort_metrics, validity, cohort_n)
    print(f"[{run_mode}] running ENLARGED BREADTH cohort context (n={ENLARGED_N_ROWS} rows)...", flush=True)
    enlarged = enlarged_cohort_analysis(chosen_name, hypothesis)
    _write_heartbeat(output_dir, expected_units, expected_units + 1, time.time() - t0)

    overall_verdict = combine_verdicts(gate1a["verdict_component"], verdict2)
    three_way = build_three_way_split(gate1a, gate1b)
    overall_msg = (f"GATE1A[{gate1a['verdict_component']}]: held_out_acc={gate1a['held_out_acc']} "
                   f"delta_vs_mem={gate1a['delta_vs_memorization']} subtype_acc={gate1a['subtype_acc']} "
                   f"|| GATE1B: dictionary_coverage={gate1b['coverage']} ({gate1b['n_hit']}/{gate1b['n']}) "
                   f"|| GATE2[{verdict2}]: {msg2} "
                   f"|| BREADTH(context): recovery_arm_iii={enlarged['recovery_arm_iii']['rate']} "
                   f"({enlarged['recovery_arm_iii']['n_recovered']}/{enlarged['recovery_arm_iii']['n_majority_wrong']}) "
                   f"vs M1=0.0(0/37) M2_M3inc1=0.2432(9/37) "
                   f"pairscramble_at_scale_collapses={enlarged['pairscramble_at_scale']['collapses_at_scale']}")

    elapsed = time.time() - t0
    metrics = {
        "verdict": overall_verdict, "verdict_msg": overall_msg, "summary": f"{overall_verdict}: {overall_msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "n_sample": len(sample), "n_per_class": n_per_class, "seed": SEED,
        "gate1a": {k: v for k, v in gate1a.items() if k != "hypothesis"}, "gate1b": gate1b,
        "gate1a_component": gate1a["verdict_component"], "gate2_component": verdict2,
        "three_way_split": three_way,
        "cohort_metrics": cohort_metrics,
        "arms_differ_verified": diff_check["arms_differ"], "arms_digests": diff_check["digests"],
        "harness_validity_check": validity,
        "enlarged_cohort_context": enlarged,
        "cardinality_ok": len(load_units(output_dir)) == expected_units,
        "expected_n_units": expected_units,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "deterministic construction-cue-vote learner (estimation/ruleind over a fixed "
                    "8-atom boolean feature space) + WordNet-MWE dictionary lookup (deterministic "
                    "gloss-keyword match, no decoded/noisy continuous signal) + FHRR bind/bundle/"
                    "cleanup over a fixed 6-role x 3-filler codebook PLUS a separately-seeded 1-role "
                    "RELATION_LINK fallback codebook -- identical justification to Stage-2/M1/M2/"
                    "M3-inc1's crlb_n/a, unchanged FHRR mechanism layer",
        "deterministic_seeding": True,
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps({k: v for k, v in metrics.items()
                       if k not in ("cohort_metrics", "enlarged_cohort_context", "gate1a", "gate1b")},
                      indent=2, default=str))
    print(json.dumps({"gate1a": metrics["gate1a"], "gate1b": metrics["gate1b"],
                       "three_way_split": three_way}, indent=2, default=str))
    print(json.dumps({"cohort_metrics": {k: v for k, v in cohort_metrics.items()
                                          if k != "relation_traces_gold_unfulfilled"}},
                      indent=2, default=str))
    print(json.dumps({"relation_traces_gold_unfulfilled": cohort_metrics["relation_traces_gold_unfulfilled"]},
                      indent=2, default=str))
    print(json.dumps({"enlarged_cohort_context": enlarged}, indent=2, default=str))


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
