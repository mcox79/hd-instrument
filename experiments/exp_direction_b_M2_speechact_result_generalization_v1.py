# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (deterministic construction-cue-vote learner + FHRR bind/bundle/cleanup,
#   fixed small codebook, no decoded/noisy continuous signal from a swept capacity regime)
# - HP_SCOPE per-arm declaration (arm iii gates HARD_PASS/HARD_FAIL for GATE-2; others comparators)
# - cardinality_ok: EXPECTED_N_UNITS=5 (one unit per PRIMARY-cohort arm, GATE-2 side)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (see prereg)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL FHRR bind/unbind/bundle primitives + result_type_induction module
#   (real_code_path); no synthetic-only branch
# - progress_logging: print_flush_true (this cell prints [smoke]/[full] progress with flush=True)
# See preregs/2026-08-09_direction_b_M2_speechact_result_generalization_v1.md for the full pre-reg.
"""exp_direction_b_M2_speechact_result_generalization_v1 -- Direction-B milestone M2: does a LEARNED
speech-act/result-type classifier (REFUSAL/GRANT/BLOCK/ACHIEVE/FAIL), induced over construction-cue
features (hdlab.result_type_induction, hdlab.learner.registry.learn) GENERALIZE across surface
forms (vs M1's 29-entry idiom lexicon, which recovered 2/8 on the primary cohort but 0/37 on
breadth -- a non-compositional long-tail)? This is the decisive test of whether the COMMON
COMPOSITIONAL CORE of the DesireDB outcome residual is tractable, and therefore whether the
multi-month M3 (full concept/script/idiom-inventory scaling) is worth committing to.

TWO GATES, run in STRICT SEQUENCE (per the task's anti-circular design mandate):

  GATE-1 (generalization, run FIRST, no DesireDB): fit the learner on hdlab.result_type_induction.
    TRAIN_EXAMPLES (34 hand-authored episodes, 5 classes, seed verbs/phrases per class); evaluate
    held-out-SURFACE-FORM generalization on HELDOUT_EXAMPLES (26 episodes, DIFFERENT verbs/phrases
    never in TRAIN -- e.g. train {said no, declined, replied no}, held-out {told her no, refused,
    objected, answered no, responded no, "Never."} for REFUSAL). Compared against (a) a
    MEMORIZATION baseline (exact TRAIN-surface-form-tag lookup -- by construction can only recall
    TRAIN forms, so it can only score its held-out items' fixed-default share) and (b) a SCRAMBLE
    control (TRAIN gold labels permuted with a fixed seed before fitting). HARD-FAIL <0.40 STOPS the
    cell here -- GATE-2 does not run (per the task's explicit instruction: a construction-cue
    channel that cannot even generalize on its own hand-authored held-out set has no business being
    scored against DesireDB).

  GATE-2 (recovery, only if GATE-1 clears the 0.40 floor): apply the SAME hypothesis GATE-1 fit
    (trained ONLY on TRAIN_EXAMPLES, NEVER on DesireDB -- non-circularity) to
    hdlab.goal_achievement.utility_channel_resulttype_grounded, scored on the IDENTICAL M1/Stage-2
    abstain-to-majority PRIMARY cohort (n=160 draw / cohort n=22, SEED=20260808, reused verbatim via
    experiments/exp_utility_satisfaction_channel_v1's loader) plus the ENLARGED 900-row context
    cohort (M1's exact ENLARGED_SEED=20260809, for head-to-head comparability with M1's 0/37).

Arms (PRIMARY cohort, n=160 draw / cohort n=22):
  (i)   majority-only baseline                                          [Stage-2/M1 arm i, unchanged]
  (ii)  utility_channel (Stage-2, WordNet-only)                          [Stage-2/M1 arm ii, unchanged]
  (iii) utility_channel_resulttype_grounded                              [THE M2 MECHANISM ARM -- gates]
  (iv)  utility_channel_resulttype_grounded, SCRAMBLED goal cue          [mandatory pairscramble control]

Modes:
  --self-test  GATE-1 fit + held-out eval (hdlab.result_type_induction.self_test) +
               hdlab.goal_achievement.self_test_resulttype_grounded_channel real-cohort-case
               mechanism-fires checks. No DesireDB needed.
  --smoke      GATE-1 (full, fast) + a SMALL DesireDB PRIMARY cohort probe (arms i/ii/iii/iv,
               mechanism-fires + arms-differ checks only, no HARD_PASS/HARD_FAIL claim).
  --full       GATE-1 -> (if >=0.40) GATE-2 PRIMARY cohort (gate-defining) + ENLARGED cohort
               (context) -> combined verdict.
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

ANCHOR_NAME = "direction_b_M2_speechact_result_generalization_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

import exp_utility_satisfaction_channel_v1 as _s2  # noqa: E402 -- reuse loader/cohort/metrics verbatim

from hdlab.goal_achievement import (  # noqa: E402
    goal_achievement_verdict, utility_channel, utility_channel_resulttype_grounded, activate_attributes,
    self_test_utility_channel, self_test_resulttype_grounded_channel, self_test as ga_self_test,
    MAJORITY_CLASS,
)
from hdlab import result_type_induction as _rti  # noqa: E402

SEED = _s2.SEED  # 20260808, identical draw to Stage-2/M1
FULL_N_PER_CLASS = _s2.FULL_N_PER_CLASS  # 80 -> n=160, the exact Stage-2/M1 cohort n=22/8 draw
VALIDITY_N_PER_CLASS = _s2.VALIDITY_N_PER_CLASS  # 40 -> n=80, documented-baseline harness

# GATE-1 (generalization) bands. MEASURED@this session's design-probe (hdlab/result_type_induction.
# self_test(), reproduced identically by this cell's own run_gate1() below): held_out_acc=0.8846
# (23/26), memorization_baseline_acc=0.2308, scramble_control_acc=0.0769.
GATE1_HP_HELDOUT_ACC = 0.60
GATE1_HP_DELTA_VS_MEM = 0.15
GATE1_HARD_FAIL_HELDOUT_ACC = 0.40    # kill criterion: STOP, do not run GATE-2 (DesireDB)
GATE1_SCRAMBLE_COLLAPSE_MAX = 0.35    # near-chance/near-majority-class-rate for a 5-way task
                                       # (26-item held-out set; majority class share = 6/26=0.231);
                                       # 0.35 gives headroom above that share while still requiring
                                       # the scrambled fit to be clearly non-informative.

# GATE-2 (recovery) bands -- reused verbatim from M1 (same cohort, same definitions).
GATE2_HP_RECOVERY = 0.40
GATE2_HARD_FAIL_RECOVERY = 0.15
GATE2_PAIRSCRAMBLE_MAX_DELTA_VS_BASELINE = 0.05   # |scr-i| <= this -> collapses
GATE2_PAIRSCRAMBLE_MAX_DELTA_VS_REAL = 0.03       # |scr-mech| <= this -> leaks (non-goal-conditioned)
VALIDITY_TOLERANCE = 0.03
MIN_COHORT_N = 15

ARM_NAMES = ("i", "ii", "iii", "iv")
ENLARGED_N_ROWS = 900          # MEASURED@M1's session: full 3076-row scan ~1218s (~20min), exceeds
                                # the 10-min single-foreground-call budget; 900 rows (~6min est.) is
                                # the SAME scope reduction M1 used (compute-proportionality) -- does
                                # NOT touch the PRIMARY n=160/22/8 gate. Reused verbatim from M1 for
                                # head-to-head comparability (M1 measured 0/37 breadth there).
ENLARGED_SEED = 20260809       # identical to M1's ENLARGED_SEED


# ============================================================================ GATE-1: generalization
def run_gate1() -> dict:
    """Fit hdlab.result_type_induction's learner on TRAIN_EXAMPLES; evaluate held-out-surface-form
    generalization + memorization baseline + scramble control. Returns the full report dict
    (including the fitted (chosen_name, hypothesis) for GATE-2 reuse) and the verdict components."""
    train_eps = [_rti.build_episode(t, c, tag) for t, c, tag in _rti.TRAIN_EXAMPLES]
    held_eps = [_rti.build_episode(t, c, tag) for t, c, tag in _rti.HELDOUT_EXAMPLES]
    chosen_name, chosen, all_results = _rti.induce(train_eps)
    if chosen is None:
        return {"verdict_component": "HARD_FAIL", "reason": "GATE1_INDUCTION_ABSTAINED_ON_TRAIN",
                "held_out_acc": 0.0, "memorization_baseline_acc": None, "scramble_control_acc": None,
                "chosen_name": None, "hypothesis": None}
    majority_train = max(_rti.RESULT_TYPES,
                          key=lambda c: sum(1 for e in train_eps if e["gold_class"] == c))

    def _eval(name, hyp, eps):
        preds, gold = [], []
        for e in eps:
            key = "|".join(sorted(e["feats"]))
            pred = _rti.predict(name, hyp, e["feats"], key, default=majority_train)
            preds.append(pred)
            gold.append(e["gold_class"])
        acc = sum(p == g for p, g in zip(preds, gold)) / len(eps)
        return acc, preds, gold

    held_acc, held_preds, held_gold = _eval(chosen_name, chosen.hypothesis, held_eps)
    mem_correct = 0
    for (t, c, tag), pred_gold in zip(_rti.HELDOUT_EXAMPLES, held_gold):
        mem_pred = _rti.memorization_baseline_predict(_rti.TRAIN_EXAMPLES, tag, majority_train)
        mem_correct += (mem_pred == c)
    mem_acc = mem_correct / len(_rti.HELDOUT_EXAMPLES)

    rng = random.Random(20260809)
    scrambled_labels = [e["gold_class"] for e in train_eps]
    rng.shuffle(scrambled_labels)
    scr_train_eps = [{"feats": e["feats"], "gold_class": scrambled_labels[i], "tag": e["tag"]}
                      for i, e in enumerate(train_eps)]
    scr_name, scr_chosen, _ = _rti.induce(scr_train_eps)
    scr_acc, _sp, _sg = _eval(scr_name, scr_chosen.hypothesis if scr_chosen else None, held_eps)

    per_item = [{"tag": tag, "gold": c, "pred": p, "ok": (p == c)}
                for (t, c, tag), p in zip(_rti.HELDOUT_EXAMPLES, held_preds)]

    delta_vs_mem = held_acc - mem_acc
    collapses = scr_acc <= GATE1_SCRAMBLE_COLLAPSE_MAX
    hard_fail = held_acc < GATE1_HARD_FAIL_HELDOUT_ACC
    hard_pass = (not hard_fail) and (held_acc >= GATE1_HP_HELDOUT_ACC) and \
                (delta_vs_mem >= GATE1_HP_DELTA_VS_MEM) and collapses
    verdict_component = "HARD_FAIL" if hard_fail else ("HARD_PASS" if hard_pass else "MIDDLE_BAND")

    return {
        "verdict_component": verdict_component,
        "chosen_name": chosen_name, "hypothesis": chosen.hypothesis,
        "chosen_plugin_description_bits": {k: round(v.description_bits, 3) for k, v in all_results.items()},
        "n_train": len(train_eps), "n_heldout": len(held_eps),
        "held_out_acc": round(held_acc, 4), "memorization_baseline_acc": round(mem_acc, 4),
        "scramble_control_acc": round(scr_acc, 4), "delta_vs_memorization": round(delta_vs_mem, 4),
        "scramble_collapses": collapses, "majority_train_class": majority_train,
        "per_item_predictions": per_item,
    }


# ============================================================================ GATE-2: PRIMARY cohort arms
def run_cohort_arms(sample: list, cohort_idxs: list, chosen_name, hypothesis) -> dict:
    scrambled_cues = _s2._scrambled_desires(sample)
    gold = []
    preds = {name: [] for name in ARM_NAMES}
    activation_fires, verdict_fires_iii = [], []
    resulttype_traces = []
    for i in cohort_idxs:
        r = sample[i]
        desire, outcome = r["Desire-Expression-Sentence"], r["Evidence"]
        gold.append(r["Fulfillment-Label"])
        activation_fires.append(len(activate_attributes(desire)) > 0)

        preds["i"].append(MAJORITY_CLASS)
        u_wn = utility_channel(desire, outcome)
        preds["ii"].append(u_wn if u_wn is not None else MAJORITY_CLASS)

        u_rt = utility_channel_resulttype_grounded(desire, outcome, chosen_name, hypothesis)
        preds["iii"].append(u_rt if u_rt is not None else MAJORITY_CLASS)
        verdict_fires_iii.append(u_rt is not None)

        u_scr = utility_channel_resulttype_grounded(scrambled_cues[i], outcome, chosen_name, hypothesis)
        preds["iv"].append(u_scr if u_scr is not None else MAJORITY_CLASS)

        resulttype_traces.append({"idx": i, "gold": r["Fulfillment-Label"],
                                   "resulttype_matched": _rti.result_type_votes(
                                       outcome, chosen_name, hypothesis)["matched"]})
    return {"gold": gold, "preds": preds, "activation_fires": activation_fires,
            "verdict_fires_iii": verdict_fires_iii, "resulttype_traces": resulttype_traces}


def recovery_rate(gold, pred) -> dict:
    """Identical definition to Stage-2/M1's own recovery_rate: of the cohort items where the
    majority-only baseline is WRONG (gold=='Unfulfilled'), the fraction `pred` gets CORRECT."""
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
    pairscramble-collapse corroboration. Computed ONCE (no resampling search) -- context, not
    gate-defining. Reuses M1's exact ENLARGED_SEED/ENLARGED_N_ROWS for head-to-head comparability
    with M1's measured 0/37 breadth."""
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
    match_counter: dict = {}
    for i in gold_unfulfilled_local:
        r = sub_rows[i]
        desire, outcome = r["Desire-Expression-Sentence"], r["Evidence"]
        pred = utility_channel_resulttype_grounded(desire, outcome, chosen_name, hypothesis)
        if pred == "Unfulfilled":
            n_recovered += 1
        for m in _rti.result_type_votes(outcome, chosen_name, hypothesis)["matched"]:
            match_counter[m] = match_counter.get(m, 0) + 1

    gold_cohort = [sub_rows[i]["Fulfillment-Label"] for i in cohort_local_idxs]
    pred_i_cohort = [MAJORITY_CLASS for _ in cohort_local_idxs]
    pred_scr_cohort = []
    for i in cohort_local_idxs:
        u = utility_channel_resulttype_grounded(scrambled[i], sub_rows[i]["Evidence"], chosen_name, hypothesis)
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
        "resulttype_match_frequency": dict(sorted(match_counter.items(), key=lambda kv: -kv[1])),
        "m1_enlarged_cohort_reference": {"recovery_rate": 0.0, "n_recovered": 0, "n_majority_wrong": 37,
                                          "source": "data/exp_direction_b_M1_idiom_grounding_recovery_v1/"
                                                    "metrics.json:enlarged_cohort_context."
                                                    "recovery_primary_mech_arm"},
    }


def harness_validity_check() -> dict:
    """Re-verify (at every --full run) the loader+field-mapping+seed reproduces the documented
    3-channel macro-F1 0.686 (n=80, seed 20260808) -- identical to Stage-2/M1's own gate."""
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


def combine_verdicts(gate1_component: str, gate2_component: str) -> str:
    """HARD-FAIL if EITHER gate hard-fails; HARD-PASS only if BOTH hard-pass; else MIDDLE_BAND.
    (GATE-1 HARD_FAIL should already have short-circuited before GATE-2 ever runs -- this exists
    for the case GATE-1 was MIDDLE_BAND, GATE-2 still ran, and GATE-2 independently HARD_FAILs.)"""
    if gate1_component == "HARD_FAIL" or gate2_component in ("HARD_FAIL", "INVALID"):
        return "HARD_FAIL" if gate2_component != "INVALID" else "INVALID"
    if gate1_component == "HARD_PASS" and gate2_component == "HARD_PASS":
        return "HARD_PASS"
    return "MIDDLE_BAND"


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
    registry.learn() fit + real FHRR bind/unbind/bundle primitives via result_type_induction.
    self_test() + goal_achievement.self_test_resulttype_grounded_channel(), no DesireDB needed."""
    r_ga = ga_self_test()
    r_util = self_test_utility_channel()
    r_rti_module = _rti.self_test()
    r_rti_channel = self_test_resulttype_grounded_channel()

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

    # GATE-1 end-to-end sanity (fast, no DesireDB): mirrors _rti.self_test()'s own numbers.
    g1 = run_gate1()
    assert g1["chosen_name"] is not None, "GATE-1 induction abstained on TRAIN"
    assert g1["held_out_acc"] > g1["memorization_baseline_acc"], g1
    assert g1["held_out_acc"] > g1["scramble_control_acc"], g1

    return {"goal_achievement_self_test": r_ga, "utility_channel_self_test": r_util,
            "result_type_induction_self_test": r_rti_module,
            "resulttype_grounded_channel_self_test": r_rti_channel,
            "gate1_selftest_repro": {"held_out_acc": g1["held_out_acc"],
                                      "memorization_baseline_acc": g1["memorization_baseline_acc"],
                                      "scramble_control_acc": g1["scramble_control_acc"],
                                      "verdict_component": g1["verdict_component"]},
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

    print(f"[{run_mode}] running GATE-1 (generalization, no DesireDB)...", flush=True)
    gate1 = run_gate1()
    print(f"[{run_mode}] GATE-1: held_out_acc={gate1['held_out_acc']} "
          f"mem_acc={gate1['memorization_baseline_acc']} scr_acc={gate1['scramble_control_acc']} "
          f"component={gate1['verdict_component']}", flush=True)
    _write_heartbeat(output_dir, 0, expected_units + 1, time.time() - t0)

    if gate1["verdict_component"] == "HARD_FAIL":
        elapsed = time.time() - t0
        msg = (f"GATE1_HARD_FAIL: held_out_acc={gate1['held_out_acc']} < {GATE1_HARD_FAIL_HELDOUT_ACC} "
               f"-- construction-cue result-type classifier does NOT generalize across surface forms. "
               f"STOPPING per anti-circular design mandate; GATE-2 (DesireDB) NOT run.")
        metrics = {
            "verdict": "HARD_FAIL", "verdict_msg": msg, "summary": f"HARD_FAIL: {msg}",
            "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
            "gate1": gate1, "gate2": None, "enlarged_cohort_context": None,
            "harness_validity_check": None, "cardinality_ok": True, "expected_n_units": expected_units,
            "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
            "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
            "crlb_n/a": "deterministic construction-cue-vote learner (ruleind/estimation/proginduction "
                        "over a fixed 7-atom boolean feature space) + FHRR bind/bundle/cleanup over a "
                        "fixed 6-role x 3-filler codebook -- identical justification to Stage-2/M1's "
                        "crlb_n/a, unchanged FHRR mechanism layer",
            "deterministic_seeding": True,
        }
        _write_metrics(output_dir, metrics)
        print(json.dumps({k: v for k, v in metrics.items() if k != "gate1"}, indent=2, default=str))
        print(json.dumps({"gate1": {k: v for k, v in gate1.items() if k != "hypothesis"}}, indent=2, default=str))
        return

    chosen_name, hypothesis = gate1["chosen_name"], gate1["hypothesis"]

    print(f"[{run_mode}] loading DesireDB...", flush=True)
    rows = _s2.load_desiredb_rows()
    print(f"[{run_mode}] {len(rows)} binary-eligible rows loaded", flush=True)
    # DISCRIMINATOR-MUST-SURVIVE-SCALE option (A): smoke uses the SAME FULL_N_PER_CLASS draw as
    # --full (reused verbatim from M1's own smoke, which measured cohort_n=22 at this N) -- a
    # reduced-N smoke draw was tried first and MEASURED to produce an underpowered cohort (n=11,
    # <MIN_COHORT_N=15) with verdict_fires_rate_iii=0.000 (the mechanism never got a chance to
    # fire), exactly the scale-saturation failure mode this discipline exists to catch.
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
        "resulttype_traces_gold_unfulfilled": [t for t in arms["resulttype_traces"] if t["gold"] == "Unfulfilled"],
    }

    if run_mode == "smoke":
        rec_iii = cohort_metrics["recovery_iii"]
        if cohort_n < MIN_COHORT_N:
            verdict, msg = "INVALID", f"SMOKE_UNDERPOWERED_COHORT: n={cohort_n} (need >={MIN_COHORT_N})"
        elif activation_fires_rate == 0.0:
            verdict, msg = "HARD_FAIL", "SMOKE_ACTIVATION_NEVER_FIRED: activation_fires_rate=0.0 on cohort"
        elif not diff_check["arms_differ"]:
            verdict, msg = "HARD_FAIL", f"SMOKE_ARMS_IDENTICAL: {diff_check['digests']}"
        else:
            verdict = "HARD_PASS"
            msg = (f"SMOKE_OK: GATE1_component={gate1['verdict_component']} cohort n={cohort_n} "
                   f"activation_fires_rate={activation_fires_rate:.3f} "
                   f"verdict_fires_rate_iii={verdict_fires_rate_iii:.3f} "
                   f"recovery_iii={rec_iii['rate']} ({rec_iii['n_recovered']}/{rec_iii['n_majority_wrong']}) "
                   f"arms_differ={diff_check['arms_differ']}")
        elapsed = time.time() - t0
        metrics = {
            "verdict": verdict, "verdict_msg": msg, "summary": f"{verdict}: {msg}",
            "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
            "n_sample": len(sample), "n_per_class": n_per_class, "seed": SEED,
            "gate1": {k: v for k, v in gate1.items() if k != "hypothesis"},
            "cohort_metrics": cohort_metrics,
            "arms_differ_verified": diff_check["arms_differ"], "arms_digests": diff_check["digests"],
            "cardinality_ok": len(load_units(output_dir)) == expected_units,
            "expected_n_units": expected_units,
            "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
            "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
            "deterministic_seeding": True,
        }
        _write_metrics(output_dir, metrics)
        print(json.dumps({k: v for k, v in metrics.items() if k not in ("cohort_metrics", "gate1")},
                          indent=2, default=str))
        print(json.dumps({"cohort_metrics": cohort_metrics}, indent=2, default=str))
        return

    # ---- FULL: harness validity + combined verdict + enlarged cohort context ----
    validity = harness_validity_check()
    verdict2, msg2 = compute_gate2_verdict(cohort_metrics, validity, cohort_n)
    print(f"[{run_mode}] running ENLARGED cohort context (n={ENLARGED_N_ROWS} rows)...", flush=True)
    enlarged = enlarged_cohort_analysis(chosen_name, hypothesis)
    _write_heartbeat(output_dir, expected_units, expected_units + 1, time.time() - t0)

    overall_verdict = combine_verdicts(gate1["verdict_component"], verdict2)
    overall_msg = (f"GATE1[{gate1['verdict_component']}]: held_out_acc={gate1['held_out_acc']} "
                   f"delta_vs_mem={gate1['delta_vs_memorization']} scr_acc={gate1['scramble_control_acc']} "
                   f"|| GATE2[{verdict2}]: {msg2} "
                   f"|| ENLARGED(context): recovery_arm_iii={enlarged['recovery_arm_iii']['rate']} "
                   f"({enlarged['recovery_arm_iii']['n_recovered']}/{enlarged['recovery_arm_iii']['n_majority_wrong']}) "
                   f"vs M1_enlarged=0.0 (0/37)")

    elapsed = time.time() - t0
    metrics = {
        "verdict": overall_verdict, "verdict_msg": overall_msg, "summary": f"{overall_verdict}: {overall_msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "n_sample": len(sample), "n_per_class": n_per_class, "seed": SEED,
        "gate1": {k: v for k, v in gate1.items() if k != "hypothesis"},
        "gate1_component": gate1["verdict_component"], "gate2_component": verdict2,
        "cohort_metrics": cohort_metrics,
        "arms_differ_verified": diff_check["arms_differ"], "arms_digests": diff_check["digests"],
        "harness_validity_check": validity,
        "enlarged_cohort_context": enlarged,
        "cardinality_ok": len(load_units(output_dir)) == expected_units,
        "expected_n_units": expected_units,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "deterministic construction-cue-vote learner (ruleind/estimation/proginduction over "
                    "a fixed 7-atom boolean feature space, MEASURED@this session's design probe: "
                    "n_atoms=7,max_nodes=5 -> 0.26s enumeration) + FHRR bind/bundle/cleanup over a "
                    "fixed 6-role x 3-filler codebook, no decoded/noisy continuous signal from a swept "
                    "capacity regime -- identical justification to Stage-2/M1's crlb_n/a, unchanged "
                    "FHRR mechanism layer",
        "deterministic_seeding": True,
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps({k: v for k, v in metrics.items()
                       if k not in ("cohort_metrics", "enlarged_cohort_context", "gate1")},
                      indent=2, default=str))
    print(json.dumps({"gate1": metrics["gate1"]}, indent=2, default=str))
    print(json.dumps({"cohort_metrics": {k: v for k, v in cohort_metrics.items()
                                          if k != "resulttype_traces_gold_unfulfilled"}},
                      indent=2, default=str))
    print(json.dumps({"resulttype_traces_gold_unfulfilled": cohort_metrics["resulttype_traces_gold_unfulfilled"]},
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
