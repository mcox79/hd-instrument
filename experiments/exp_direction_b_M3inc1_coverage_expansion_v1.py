# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace, rebuilt from load_units() every
#   write -- see tools/exp_checkpoint.py; each unit's own record_unit append is itself atomic)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (deterministic construction-cue-vote learner + idiom-regex lexicon + FHRR
#   bind/bundle/cleanup, fixed small codebook, no decoded/noisy continuous signal)
# - HP_SCOPE per-arm declaration (arm iii of the v2_combined unit gates HARD_PASS/HARD_FAIL/WIRE;
#   other arms/units are comparators/context)
# - cardinality_ok: EXPECTED_N_UNITS=3 (v1_resulttype, v2_resulttype, v2_combined)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (see prereg)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL FHRR bind/unbind/bundle primitives + result_type_induction +
#   idiom_grounding modules (real_code_path); no synthetic-only branch
# - cell_chunked: true -- ONE unit per invocation (--unit flag), tools/exp_checkpoint.py per-unit
#   resumable shard (units.jsonl); the ~200s+ per-process WordNet-corpus import cost on this
#   (currently contended) host made a single all-3-units process risk exceeding the 10-min
#   single-foreground-call budget (MEASURED@this session's diagnostic: import alone took 225s) --
#   chunking to one unit per process call is the same discipline M1/M2 already used per-cell,
#   applied at unit granularity here (see cell docstring "Compute budget" note).
# - progress_logging: print_flush_true (this cell's timeout_s can exceed 1800s on this host; prints
#   [unit]/[full] progress lines with flush=True throughout)
# See preregs/2026-08-09_direction_b_M3inc1_coverage_expansion_v1.md for the full pre-registration.
"""exp_direction_b_M3inc1_coverage_expansion_v1 -- Direction-B M3-increment-1: the M3-cost crux test.

Two questions, per the Director's task:
(1) COVERAGE EXPANSION: does growing hdlab.result_type_induction's construction-cue verb-class
    exemplar pools (comm_verb/give_verb/achieve_verb/fail_verb), authored from each candidate word's
    OWN WordNet primary-sense gloss (never tuned against DesireDB labels), push DesireDB recovery
    toward the DesireDB majority -- i.e. do successive pool-expansion increments show roughly LINEAR
    returns (M3, the multi-month full-inventory scaling leg, is tractable) or DIMINISHING/plateauing
    returns (M3's cost is not justified by this lever alone)?
(2) CHANNEL COMBINATION: does combining M2's result-type channel (the compositional core, generalizes
    to unseen surface forms) WITH M1's idiom-lexicon channel (the non-compositional tail, zero
    breadth generalization measured -- M1 landed 0/37) as ONE two-pronged channel (result-type first,
    idiom-lexicon fallback ONLY when result-type genuinely found nothing -- see hdlab.goal_achievement
    .utility_channel_combined_grounded) earn a WIRE (GATE-2 PRIMARY HARD_PASS >= 0.40, the bar M2's
    own cell just missed at 0.375)?

THREE UNITS (`--unit`, one per invocation; tools/exp_checkpoint.py per-unit resumable shard):
  v1_resulttype -- pool_stage=v1_targeted_gap_close (closes the 4 disclosed M2 gaps: object/award/
    provide/quit), channel=resulttype-only. PRIMARY cohort only (fast; no breadth pass -- compute-
    proportionality, this unit exists for the GATE-1 + PRIMARY-cohort trend point only).
  v2_resulttype -- pool_stage=v2_broader_class_expansion (+3 general-vocabulary words: deny/reject/
    abandon), channel=resulttype-only. PRIMARY + full BREADTH (900-row, same seed as M1/M2) --
    isolates POOL-EXPANSION's OWN contribution to breadth recovery, holding the channel fixed at
    resulttype-only (same channel M2 measured 9/37 with).
  v2_combined -- pool_stage=v2_broader_class_expansion, channel=combined (result-type + idiom
    fallback). PRIMARY + full BREADTH. THE GATE-DEFINING UNIT: isolates the CHANNEL-COMBINATION's
    marginal contribution on top of v2_resulttype's pool-expansion-only number, and its PRIMARY
    recovery is what the WIRE decision (GATE-2 PRIMARY HARD_PASS >= 0.40) applies to.

Compute budget: this host's per-process WordNet-corpus import MEASURED at 225s during this session's
design probe (contended host; MEASURED@this session's diagnostic script, not representative of an
idle host) -- each unit is therefore its OWN foreground process (chunked, per cell-template mandate
above), and the 900-row BREADTH pass is included only for v2_resulttype/v2_combined (v1_resulttype
skips it, PRIMARY-cohort-only) to keep each individual invocation inside the 10-min single-
foreground-call budget (compute-proportionality: v1's role is a GATE-1 regression-check + a fast
PRIMARY-cohort trend point, not a second full breadth measurement).

Modes:
  --self-test  Real objects at small scale (goal_achievement/result_type_induction/idiom_grounding
               self-tests + a v0/v1/v2 GATE-1 sanity table), no DesireDB needed.
  --smoke      GATE-1 @ v2 (fast) + a PRIMARY-cohort-only probe of the v2_combined unit's mechanism
               (mechanism-fires + arms-differ checks only, no HARD_PASS/HARD_FAIL claim).
  --full --unit {v1_resulttype,v2_resulttype,v2_combined}
               Computes (or, if already recorded, loads) exactly that one unit, appends it to
               units.jsonl, then rebuilds metrics.json from ALL units recorded so far (verdict is
               only fully meaningful once cardinality_ok=True, i.e. all 3 units present).
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

ANCHOR_NAME = "direction_b_M3inc1_coverage_expansion_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

import exp_utility_satisfaction_channel_v1 as _s2  # noqa: E402 -- reuse loader/cohort/metrics verbatim

from hdlab.goal_achievement import (  # noqa: E402
    goal_achievement_verdict, utility_channel, utility_channel_resulttype_grounded,
    utility_channel_combined_grounded, utility_channel_trace_resulttype_grounded,
    utility_channel_trace_combined_grounded, activate_attributes,
    self_test_utility_channel, self_test_idiom_grounded_channel, self_test_resulttype_grounded_channel,
    self_test_combined_grounded_channel, self_test as ga_self_test, MAJORITY_CLASS,
)
from hdlab import result_type_induction as _rti  # noqa: E402
from hdlab import idiom_grounding as _ig  # noqa: E402

SEED = _s2.SEED  # 20260808, identical draw to Stage-2/M1/M2
FULL_N_PER_CLASS = _s2.FULL_N_PER_CLASS  # 80 -> n=160, the exact Stage-2/M1/M2 cohort n=22/8 draw
VALIDITY_N_PER_CLASS = _s2.VALIDITY_N_PER_CLASS  # 40 -> n=80, documented-baseline harness

# ---- GATE-1 (regression guard) bands. Task's explicit floor: held-out acc >= 0.60 to count as
# "still generalizing"; HARD-FAIL (STOP) if it drops below 0.40 (expansion broke generalization).
GATE1_PASS_FLOOR = 0.60
GATE1_HARD_FAIL_FLOOR = 0.40
GATE1_SCRAMBLE_COLLAPSE_MAX = 0.35  # reused verbatim from M2 (same 26-item HELDOUT set, same
                                     # majority-class share 6/26=0.231 regardless of pool_stage)

# ---- GATE-2 PRIMARY bands. Reused verbatim from M1/M2 (same cohort, same thresholds) -- task's
# explicit framing: "HARD_PASS if >=0.40 (the bar M2 just missed)".
GATE2_HP_RECOVERY = 0.40
GATE2_HARD_FAIL_RECOVERY = 0.15
PAIRSCRAMBLE_MAX_DELTA_VS_BASELINE = 0.05   # |scr-i| <= this -> collapses
PAIRSCRAMBLE_MAX_DELTA_VS_REAL = 0.03       # |scr-mech| <= this -> leaks (non-goal-conditioned)
VALIDITY_TOLERANCE = 0.03
MIN_COHORT_N = 15

ENLARGED_N_ROWS = 900          # MEASURED@M1's session: full 3076-row scan ~1218s (~20min); 900 rows
                                # reused verbatim from M1/M2 for head-to-head comparability with
                                # their measured 9/37 (M2) and 0/37 (M1) breadth numbers.
ENLARGED_SEED = 20260809       # identical to M1/M2's ENLARGED_SEED

# ---- CITED reference numbers (M1/M2 landed metrics -- NOT recomputed here; see MEASURED@ paths).
M1_PRIMARY_RATE = 0.25    # 2/8   MEASURED@data/exp_direction_b_M1_idiom_grounding_recovery_v1/metrics.json:cohort_metrics.recovery_iii_ablation.rate
M1_BREADTH_RATE = 0.0     # 0/37  MEASURED@...:enlarged_cohort_context.recovery_primary_mech_arm.rate
M2_PRIMARY_RATE = 0.375   # 3/8   MEASURED@data/exp_direction_b_M2_speechact_result_generalization_v1/metrics.json:cohort_metrics.recovery_iii.rate
M2_BREADTH_RATE = 0.2432  # 9/37  MEASURED@...:enlarged_cohort_context.recovery_arm_iii.rate
M2_GATE1_V0_HELDOUT_ACC = 0.8846  # 23/26 MEASURED@...:gate1.held_out_acc (v0_baseline pools)

ARM_NAMES = ("i", "ii", "iii", "iv")

UNIT_CONFIG = {
    "v1_resulttype": {"pool_stage": "v1_targeted_gap_close", "channel": "resulttype",
                       "include_breadth": False},
    "v2_resulttype": {"pool_stage": "v2_broader_class_expansion", "channel": "resulttype",
                       "include_breadth": True},
    "v2_combined": {"pool_stage": "v2_broader_class_expansion", "channel": "combined",
                     "include_breadth": True},
}
UNIT_ORDER = ("v1_resulttype", "v2_resulttype", "v2_combined")
GATE_DEFINING_UNIT = "v2_combined"


def _mechanism_trace(desire: str, outcome: str, unit_cfg: dict, chosen_name, hypothesis) -> dict:
    pool_stage = unit_cfg["pool_stage"]
    if unit_cfg["channel"] == "resulttype":
        return utility_channel_trace_resulttype_grounded(desire, outcome, chosen_name, hypothesis,
                                                           pool_stage=pool_stage)
    return utility_channel_trace_combined_grounded(desire, outcome, chosen_name, hypothesis,
                                                     pool_stage=pool_stage)


def _mechanism_pred(desire: str, outcome: str, unit_cfg: dict, chosen_name, hypothesis) -> str:
    v = _mechanism_trace(desire, outcome, unit_cfg, chosen_name, hypothesis)["verdict"]
    return v if v is not None else MAJORITY_CLASS


# ============================================================================ GATE-1
def run_gate1(pool_stage: str) -> dict:
    """Identical structure to M2's own run_gate1, parametrized by pool_stage. No DesireDB."""
    train_eps = [_rti.build_episode(t, c, tag, pool_stage=pool_stage) for t, c, tag in _rti.TRAIN_EXAMPLES]
    held_eps = [_rti.build_episode(t, c, tag, pool_stage=pool_stage) for t, c, tag in _rti.HELDOUT_EXAMPLES]
    chosen_name, chosen, all_results = _rti.induce(train_eps)
    if chosen is None:
        return {"pool_stage": pool_stage, "verdict_component": "HARD_FAIL",
                "reason": "GATE1_INDUCTION_ABSTAINED_ON_TRAIN", "held_out_acc": 0.0,
                "memorization_baseline_acc": None, "scramble_control_acc": None,
                "chosen_name": None, "hypothesis": None}
    majority_train = max(_rti.RESULT_TYPES, key=lambda c: sum(1 for e in train_eps if e["gold_class"] == c))

    def _eval(name, hyp, eps):
        n_ok = 0
        for e in eps:
            key = "|".join(sorted(e["feats"]))
            pred = _rti.predict(name, hyp, e["feats"], key, default=majority_train)
            n_ok += (pred == e["gold_class"])
        return n_ok / len(eps)

    held_acc = _eval(chosen_name, chosen.hypothesis, held_eps)
    mem_correct = sum(1 for t, c, tag in _rti.HELDOUT_EXAMPLES
                       if _rti.memorization_baseline_predict(_rti.TRAIN_EXAMPLES, tag, majority_train) == c)
    mem_acc = mem_correct / len(_rti.HELDOUT_EXAMPLES)

    rng = random.Random(20260809)
    scrambled_labels = [e["gold_class"] for e in train_eps]
    rng.shuffle(scrambled_labels)
    scr_train_eps = [{"feats": e["feats"], "gold_class": scrambled_labels[i], "tag": e["tag"]}
                      for i, e in enumerate(train_eps)]
    scr_name, scr_chosen, _ = _rti.induce(scr_train_eps)
    scr_acc = _eval(scr_name, scr_chosen.hypothesis if scr_chosen else None, held_eps)

    collapses = scr_acc <= GATE1_SCRAMBLE_COLLAPSE_MAX
    hard_fail = held_acc < GATE1_HARD_FAIL_FLOOR
    passes = (not hard_fail) and (held_acc >= GATE1_PASS_FLOOR) and collapses
    verdict_component = "HARD_FAIL" if hard_fail else ("PASS" if passes else "MIDDLE_BAND")

    return {"pool_stage": pool_stage, "verdict_component": verdict_component,
            "chosen_name": chosen_name, "hypothesis": chosen.hypothesis,
            "n_train": len(train_eps), "n_heldout": len(held_eps),
            "held_out_acc": round(held_acc, 4), "memorization_baseline_acc": round(mem_acc, 4),
            "scramble_control_acc": round(scr_acc, 4), "scramble_collapses": collapses,
            "majority_train_class": majority_train}


# ============================================================================ PRIMARY cohort
def run_primary_cohort(unit_cfg: dict, chosen_name, hypothesis) -> dict:
    rows = _s2.load_desiredb_rows()
    sample = _s2.balanced_subsample(rows, FULL_N_PER_CLASS, SEED)
    cohort_idxs = _s2.build_cohort(sample)
    cohort_n = len(cohort_idxs)
    scrambled_cues = _s2._scrambled_desires(sample)

    gold, preds = [], {name: [] for name in ARM_NAMES}
    activation_fires, verdict_fires_iii = [], []
    match_traces = []
    for i in cohort_idxs:
        r = sample[i]
        desire, outcome = r["Desire-Expression-Sentence"], r["Evidence"]
        gold.append(r["Fulfillment-Label"])
        activation_fires.append(len(activate_attributes(desire)) > 0)

        preds["i"].append(MAJORITY_CLASS)
        u_wn = utility_channel(desire, outcome)
        preds["ii"].append(u_wn if u_wn is not None else MAJORITY_CLASS)

        tr = _mechanism_trace(desire, outcome, unit_cfg, chosen_name, hypothesis)
        preds["iii"].append(tr["verdict"] if tr["verdict"] is not None else MAJORITY_CLASS)
        verdict_fires_iii.append(tr["verdict"] is not None)

        u_scr = _mechanism_pred(scrambled_cues[i], outcome, unit_cfg, chosen_name, hypothesis)
        preds["iv"].append(u_scr)

        if r["Fulfillment-Label"] == "Unfulfilled":
            match_traces.append({"idx": i, "gold": r["Fulfillment-Label"], "trace": tr.get("active", {})})

    accs = {name: _s2.accuracy(gold, preds[name]) for name in ARM_NAMES}
    macro_f1s = {name: _s2.macro_f1(gold, preds[name]) for name in ARM_NAMES}
    digests = {name: hashlib.sha256(json.dumps(preds[name]).encode()).hexdigest() for name in ARM_NAMES}
    arms_differ = len(set(digests.values())) > 1

    def _recovery(pred):
        wrong_idxs = [k for k, g in enumerate(gold) if g == "Unfulfilled"]
        if not wrong_idxs:
            return {"n_majority_wrong": 0, "n_recovered": 0, "rate": None}
        n_rec = sum(1 for k in wrong_idxs if pred[k] == gold[k])
        return {"n_majority_wrong": len(wrong_idxs), "n_recovered": n_rec,
                "rate": round(n_rec / len(wrong_idxs), 4)}

    activation_fires_rate = sum(activation_fires) / cohort_n if cohort_n else 0.0
    verdict_fires_rate_iii = sum(verdict_fires_iii) / cohort_n if cohort_n else 0.0

    return {"cohort_n": cohort_n, "n_sample": len(sample),
            "activation_fires_rate": round(activation_fires_rate, 4),
            "verdict_fires_rate_iii": round(verdict_fires_rate_iii, 4),
            "gold_dist": {"Fulfilled": gold.count("Fulfilled"), "Unfulfilled": gold.count("Unfulfilled")},
            **{f"acc_{n}": round(accs[n], 4) for n in ARM_NAMES},
            **{f"macro_f1_{n}": round(macro_f1s[n], 4) for n in ARM_NAMES},
            "recovery_i": _recovery(preds["i"]), "recovery_ii": _recovery(preds["ii"]),
            "recovery_iii": _recovery(preds["iii"]), "recovery_iv": _recovery(preds["iv"]),
            "arms_differ": arms_differ, "arms_digests": digests,
            "match_traces_gold_unfulfilled": match_traces}


# ============================================================================ BREADTH (enlarged) cohort
def run_breadth_cohort(unit_cfg: dict, chosen_name, hypothesis) -> dict:
    rows = _s2.load_desiredb_rows()
    rng = random.Random(ENLARGED_SEED)
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
    for i in gold_unfulfilled_local:
        r = sub_rows[i]
        desire, outcome = r["Desire-Expression-Sentence"], r["Evidence"]
        tr = _mechanism_trace(desire, outcome, unit_cfg, chosen_name, hypothesis)
        if tr["verdict"] == "Unfulfilled":
            n_recovered += 1
        for attr, info in tr.get("active", {}).items():
            gt = info.get("grounding_trace", {})
            src = gt.get("secondary_source") or ("resulttype" if gt.get("resulttype_matched") else None)
            if src:
                source_counter[src] = source_counter.get(src, 0) + 1

    gold_cohort = [sub_rows[i]["Fulfillment-Label"] for i in cohort_local_idxs]
    pred_i_cohort = [MAJORITY_CLASS for _ in cohort_local_idxs]
    pred_scr_cohort = [_mechanism_pred(scrambled[i], sub_rows[i]["Evidence"], unit_cfg, chosen_name, hypothesis)
                        for i in cohort_local_idxs]
    acc_i_cohort = _s2.accuracy(gold_cohort, pred_i_cohort)
    acc_scr_cohort = _s2.accuracy(gold_cohort, pred_scr_cohort)

    n_denom = len(gold_unfulfilled_local)
    return {
        "n_subsample_rows": len(sub_rows), "n_total_rows_available": len(rows),
        "cohort_n": len(cohort_local_idxs), "gold_unfulfilled_n": n_denom,
        "recovery": {"n_recovered": n_recovered, "n_majority_wrong": n_denom,
                     "rate": round(n_recovered / n_denom, 4) if n_denom else None},
        "pairscramble_at_scale": {
            "cohort_n": len(cohort_local_idxs), "acc_i": round(acc_i_cohort, 4),
            "acc_scrambled": round(acc_scr_cohort, 4),
            "delta": round(abs(acc_scr_cohort - acc_i_cohort), 4),
            "collapses_at_scale": abs(acc_scr_cohort - acc_i_cohort) <= PAIRSCRAMBLE_MAX_DELTA_VS_BASELINE},
        "secondary_source_frequency": dict(sorted(source_counter.items(), key=lambda kv: -kv[1])),
    }


# ============================================================================ per-unit compute
def compute_unit(unit_name: str) -> dict:
    cfg = UNIT_CONFIG[unit_name]
    print(f"[unit={unit_name}] pool_stage={cfg['pool_stage']} channel={cfg['channel']} "
          f"include_breadth={cfg['include_breadth']}", flush=True)
    t0 = time.time()
    gate1 = run_gate1(cfg["pool_stage"])
    chosen_name, hypothesis = gate1["chosen_name"], gate1["hypothesis"]
    print(f"[unit={unit_name}] GATE-1: held_out_acc={gate1['held_out_acc']} "
          f"component={gate1['verdict_component']} elapsed={time.time()-t0:.1f}s", flush=True)

    primary = None
    validity = None
    breadth = None
    if chosen_name is not None:
        validity = harness_validity_check()
        primary = run_primary_cohort(cfg, chosen_name, hypothesis)
        print(f"[unit={unit_name}] PRIMARY: cohort_n={primary['cohort_n']} "
              f"recovery_iii={primary['recovery_iii']['rate']} "
              f"({primary['recovery_iii']['n_recovered']}/{primary['recovery_iii']['n_majority_wrong']}) "
              f"elapsed={time.time()-t0:.1f}s", flush=True)
        if cfg["include_breadth"]:
            breadth = run_breadth_cohort(cfg, chosen_name, hypothesis)
            print(f"[unit={unit_name}] BREADTH: cohort_n={breadth['cohort_n']} "
                  f"recovery={breadth['recovery']['rate']} "
                  f"({breadth['recovery']['n_recovered']}/{breadth['recovery']['n_majority_wrong']}) "
                  f"elapsed={time.time()-t0:.1f}s", flush=True)

    elapsed = time.time() - t0
    return {"unit_name": unit_name, "config": cfg, "gate1": {k: v for k, v in gate1.items() if k != "hypothesis"},
            "harness_validity_check": validity, "primary": primary, "breadth": breadth,
            "elapsed_s": round(elapsed, 3)}


def harness_validity_check() -> dict:
    """Re-verify the loader+field-mapping+seed reproduces the documented 3-channel macro-F1 0.686
    (n=80, seed 20260808) -- identical to Stage-2/M1/M2's own gate. Pool-stage/channel-independent
    (uses plain goal_achievement_verdict, unaffected by any Direction-B channel)."""
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


# ============================================================================ aggregate verdict
def compute_returns_per_expansion(units: dict) -> dict:
    """RETURNS-PER-EXPANSION table: GATE-1 + PRIMARY trend across v0(cited)->v1->v2_resulttype, and
    the pool-expansion-only vs +combination BREADTH decomposition (v0 cited -> v2_resulttype measured
    isolates pool-expansion alone; v2_resulttype -> v2_combined measured isolates the combination's
    own marginal contribution)."""
    v1 = units.get("v1_resulttype")
    v2r = units.get("v2_resulttype")
    v2c = units.get("v2_combined")
    table = {
        "gate1_held_out_acc": {"v0_baseline_cited": M2_GATE1_V0_HELDOUT_ACC,
                                "v1_targeted_gap_close": v1["gate1"]["held_out_acc"] if v1 else None,
                                "v2_broader_class_expansion": (v2r or v2c)["gate1"]["held_out_acc"]
                                if (v2r or v2c) else None},
        "primary_recovery_rate": {
            "v0_M2_resulttype_cited": M2_PRIMARY_RATE,
            "v1_resulttype": v1["primary"]["recovery_iii"]["rate"] if v1 and v1["primary"] else None,
            "v2_resulttype": v2r["primary"]["recovery_iii"]["rate"] if v2r and v2r["primary"] else None,
            "v2_combined": v2c["primary"]["recovery_iii"]["rate"] if v2c and v2c["primary"] else None,
        },
        "breadth_recovery_rate": {
            "v0_M2_resulttype_cited": M2_BREADTH_RATE,
            "v0_M1_idiom_cited": M1_BREADTH_RATE,
            "v2_resulttype_pool_expansion_only": v2r["breadth"]["recovery"]["rate"] if v2r and v2r["breadth"] else None,
            "v2_combined_plus_idiom_fallback": v2c["breadth"]["recovery"]["rate"] if v2c and v2c["breadth"] else None,
        },
    }
    if v2r and v2r["breadth"] and v2c and v2c["breadth"]:
        r0 = M2_BREADTH_RATE
        r1 = v2r["breadth"]["recovery"]["rate"] or 0.0
        r2 = v2c["breadth"]["recovery"]["rate"] or 0.0
        delta_pool_expansion = round(r1 - r0, 4)
        delta_combination = round(r2 - r1, 4)
        table["breadth_delta_from_pool_expansion_v0_to_v2resulttype"] = delta_pool_expansion
        table["breadth_delta_from_combination_v2resulttype_to_v2combined"] = delta_combination
        if delta_pool_expansion <= 0 and delta_combination <= 0:
            trend = "flat_or_negative"
        elif delta_pool_expansion > 0 and delta_combination > 0:
            ratio = delta_combination / delta_pool_expansion if delta_pool_expansion else float("inf")
            trend = "roughly_linear" if 0.4 <= ratio <= 2.5 else (
                "diminishing" if ratio < 0.4 else "accelerating")
        else:
            trend = "mixed"
        table["m3_tractability_trend_assessment"] = trend
    return table


def compute_overall_verdict(units: dict) -> tuple:
    if len(units) < len(UNIT_ORDER):
        missing = [u for u in UNIT_ORDER if u not in units]
        return "INVALID", f"UNITS_PENDING: {len(units)}/{len(UNIT_ORDER)} complete, missing={missing}", {}

    v2c = units[GATE_DEFINING_UNIT]
    gate1 = v2c["gate1"]
    if gate1["chosen_name"] is None or gate1["held_out_acc"] < GATE1_HARD_FAIL_FLOOR:
        return "HARD_FAIL", (f"GATE1_HARD_FAIL: held_out_acc={gate1['held_out_acc']} < "
                              f"{GATE1_HARD_FAIL_FLOOR} -- expansion broke generalization"), {}
    if v2c["primary"] is None or v2c["breadth"] is None:
        return "INVALID", "GATE_DEFINING_UNIT_MISSING_PRIMARY_OR_BREADTH", {}
    if not v2c["harness_validity_check"]["valid"]:
        return "INVALID", f"harness_validity_check FAILED: {v2c['harness_validity_check']}", {}

    prim = v2c["primary"]
    cohort_n = prim["cohort_n"]
    if cohort_n < MIN_COHORT_N:
        return "INVALID", f"UNDERPOWERED_COHORT: n={cohort_n} (need >={MIN_COHORT_N})", {}
    rec = prim["recovery_iii"]
    if rec["rate"] is None:
        return "INVALID", "recovery_rate UNDEFINED: 0 gold-Unfulfilled items in PRIMARY cohort", {}

    primary_rate = rec["rate"]
    delta_scr_i = abs(prim["acc_iv"] - prim["acc_i"])
    delta_scr_mech = abs(prim["acc_iv"] - prim["acc_iii"])
    primary_collapses = delta_scr_i <= PAIRSCRAMBLE_MAX_DELTA_VS_BASELINE
    primary_leaks = delta_scr_mech <= PAIRSCRAMBLE_MAX_DELTA_VS_REAL

    breadth_rate = v2c["breadth"]["recovery"]["rate"] or 0.0
    breadth_collapses = v2c["breadth"]["pairscramble_at_scale"]["collapses_at_scale"]

    pairscramble_ok = primary_collapses and (not primary_leaks) and breadth_collapses
    no_returns = (primary_rate <= M2_PRIMARY_RATE) and (breadth_rate <= M2_BREADTH_RATE)

    gate2_primary_hard_fail = (primary_rate < GATE2_HARD_FAIL_RECOVERY) or primary_leaks or (not primary_collapses)
    gate2_primary_hard_pass = (not gate2_primary_hard_fail) and (primary_rate >= GATE2_HP_RECOVERY) \
        and primary_collapses and (not primary_leaks)

    hard_fail = gate2_primary_hard_fail or no_returns or (not breadth_collapses)
    hard_pass = (not hard_fail) and gate2_primary_hard_pass \
        and (gate1["held_out_acc"] >= GATE1_PASS_FLOOR) and gate1["scramble_collapses"]

    overall = "HARD_FAIL" if hard_fail else ("HARD_PASS" if hard_pass else "MIDDLE_BAND")
    wire_candidate = gate2_primary_hard_pass

    details = {"primary_rate": primary_rate, "breadth_rate": breadth_rate,
               "primary_collapses": primary_collapses, "primary_leaks": primary_leaks,
               "breadth_collapses": breadth_collapses, "pairscramble_ok": pairscramble_ok,
               "no_returns_from_expansion_or_combination": no_returns,
               "gate2_primary_hard_pass": gate2_primary_hard_pass,
               "gate2_primary_hard_fail": gate2_primary_hard_fail,
               "wire_candidate": wire_candidate}
    msg = (f"GATE1[{gate1['verdict_component']}]: held_out_acc={gate1['held_out_acc']} "
           f"(v0_cited={M2_GATE1_V0_HELDOUT_ACC}) || GATE2_PRIMARY: rate={primary_rate} "
           f"(vs M2={M2_PRIMARY_RATE}, M1={M1_PRIMARY_RATE}) collapses={primary_collapses} "
           f"leaks={primary_leaks} hard_pass={gate2_primary_hard_pass} || GATE2_BREADTH(context): "
           f"rate={breadth_rate} (vs M2={M2_BREADTH_RATE}, M1={M1_BREADTH_RATE}) "
           f"collapses={breadth_collapses} || no_returns={no_returns} || WIRE_CANDIDATE={wire_candidate}")
    return overall, msg, details


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
    idiom lexicon + registry.learn() fit + real FHRR bind/unbind/bundle primitives via all 5
    goal_achievement self-tests + result_type_induction.self_test() + idiom_grounding self-test, plus
    a v0/v1/v2 GATE-1 pool-stage sanity table. No DesireDB needed."""
    r_ga = ga_self_test()
    r_util = self_test_utility_channel()
    r_idiom_channel = self_test_idiom_grounded_channel()
    r_idiom_lex = _ig.self_test_idiom_grounding()
    r_rti_module = _rti.self_test()
    r_rti_channel = self_test_resulttype_grounded_channel()
    r_combined_channel = self_test_combined_grounded_channel()

    gate1_table = {}
    for stage in _rti.POOL_STAGE_ORDER:
        g1 = run_gate1(stage)
        gate1_table[stage] = {"held_out_acc": g1["held_out_acc"],
                               "scramble_control_acc": g1["scramble_control_acc"],
                               "scramble_collapses": g1["scramble_collapses"]}
    assert gate1_table["v0_baseline"]["held_out_acc"] < gate1_table["v2_broader_class_expansion"]["held_out_acc"], (
        f"expansion did not improve held-out acc: {gate1_table}")
    for stage, row in gate1_table.items():
        assert row["held_out_acc"] >= GATE1_PASS_FLOOR, f"{stage} below GATE1_PASS_FLOOR: {row}"
        assert row["scramble_collapses"], f"{stage} scramble did not collapse: {row}"

    return {"goal_achievement_self_test": r_ga, "utility_channel_self_test": r_util,
            "idiom_grounded_channel_self_test": r_idiom_channel,
            "idiom_lexicon_self_test": r_idiom_lex,
            "result_type_induction_self_test": r_rti_module,
            "resulttype_grounded_channel_self_test": r_rti_channel,
            "combined_grounded_channel_self_test": r_combined_channel,
            "gate1_pool_stage_table": gate1_table, "helpers_ok": True}


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--unit", choices=list(UNIT_ORDER), default=None)
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

    if args.smoke:
        run_mode = "smoke"
        output_dir = OUTPUT_DIR + "_smoke"
        _write_start_marker(output_dir, run_mode, 1)
        t0 = time.time()
        print("[smoke] running GATE-1 @ v2_broader_class_expansion...", flush=True)
        gate1 = run_gate1("v2_broader_class_expansion")
        _write_heartbeat(output_dir, 0, 2, time.time() - t0)
        if gate1["chosen_name"] is None:
            verdict, msg = "HARD_FAIL", "SMOKE_GATE1_INDUCTION_ABSTAINED"
        else:
            cfg = UNIT_CONFIG[GATE_DEFINING_UNIT]
            primary = run_primary_cohort(cfg, gate1["chosen_name"], gate1["hypothesis"])
            _write_heartbeat(output_dir, 1, 2, time.time() - t0)
            if primary["cohort_n"] < MIN_COHORT_N:
                verdict, msg = "INVALID", f"SMOKE_UNDERPOWERED_COHORT: n={primary['cohort_n']}"
            elif primary["activation_fires_rate"] == 0.0:
                verdict, msg = "HARD_FAIL", "SMOKE_ACTIVATION_NEVER_FIRED"
            elif not primary["arms_differ"]:
                verdict, msg = "HARD_FAIL", f"SMOKE_ARMS_IDENTICAL: {primary['arms_digests']}"
            else:
                verdict = "HARD_PASS"
                msg = (f"SMOKE_OK: GATE1_held_out_acc={gate1['held_out_acc']} cohort_n={primary['cohort_n']} "
                       f"activation_fires_rate={primary['activation_fires_rate']} "
                       f"verdict_fires_rate_iii={primary['verdict_fires_rate_iii']} "
                       f"recovery_iii={primary['recovery_iii']['rate']} arms_differ={primary['arms_differ']}")
        elapsed = time.time() - t0
        metrics = {"verdict": verdict, "verdict_msg": msg, "summary": f"{verdict}: {msg}",
                   "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
                   "gate1": {k: v for k, v in gate1.items() if k != "hypothesis"},
                   "cell_chunked": True, "start_marker_written": True, "crash_diagnostic_present": True,
                   "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
                   "deterministic_seeding": True}
        _write_metrics(output_dir, metrics)
        print(json.dumps(metrics, indent=2, default=str))
        return

    # ---- FULL: one unit per invocation ----
    if args.unit is None:
        raise SystemExit("--full requires --unit {v1_resulttype,v2_resulttype,v2_combined}")
    run_mode = "full"
    output_dir = OUTPUT_DIR
    _write_start_marker(output_dir, run_mode, len(UNIT_ORDER))
    t0 = time.time()

    done = completed_units(output_dir)
    key = unit_key(args.unit)
    if key in done:
        print(f"[full] unit={args.unit} already recorded, skipping recompute", flush=True)
    else:
        print(f"[full] computing unit={args.unit}...", flush=True)
        result = compute_unit(args.unit)
        record_unit(output_dir, key, result)
        _write_heartbeat(output_dir, UNIT_ORDER.index(args.unit) + 1, len(UNIT_ORDER), time.time() - t0)

    all_units = load_units(output_dir)
    overall_verdict, overall_msg, verdict_details = compute_overall_verdict(all_units)
    returns_table = compute_returns_per_expansion(all_units)

    elapsed = time.time() - t0
    metrics = {
        "verdict": overall_verdict, "verdict_msg": overall_msg, "summary": f"{overall_verdict}: {overall_msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "this_invocation_unit": args.unit, "units_recorded": sorted(all_units.keys()),
        "cardinality_ok": len(all_units) == len(UNIT_ORDER), "expected_n_units": len(UNIT_ORDER),
        "verdict_details": verdict_details, "returns_per_expansion": returns_table,
        "units": all_units,
        "cell_chunked": True, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "deterministic construction-cue-vote learner (ruleind/estimation/proginduction over "
                    "a fixed 7-atom boolean feature space) + idiom-regex lexicon + FHRR bind/bundle/"
                    "cleanup over a fixed 6-role x 3-filler codebook, no decoded/noisy continuous signal "
                    "from a swept capacity regime -- identical justification to Stage-2/M1/M2's crlb_n/a, "
                    "unchanged FHRR mechanism layer",
        "deterministic_seeding": True,
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps({k: v for k, v in metrics.items() if k != "units"}, indent=2, default=str))
    print(json.dumps({"this_unit_result": all_units.get(args.unit)}, indent=2, default=str))


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
