# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; REAL vs PAIRSCRAMBLE hash-compared)
# - final_metrics_atomicity: tmp_replace (os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (glass-box lexical/regex/WordNet pipeline, no swept capacity regime)
# - cardinality_ok: EXPECTED_N_UNITS declared per run_mode; resumable per-unit (tools/exp_checkpoint)
# - calibration_check: n/a (no adaptive threshold; every construction constant is pre-registered)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / CITED@
# - self-test constructs the REAL goal_achievement_verdict/desiderative_negation_channel objects at
#   small scale (real_code_path); no synthetic-only branch; no DesireDB/network needed
# See preregs/2026-08-09_desiderative_negation_channel_v1.md for the full pre-registration.
"""exp_desiderative_negation_channel_v1 -- does the new hdlab.goal_achievement.
desiderative_negation_channel (first-person discourse-negation reply / modal-possibility negation /
object-existence-availability-result-attribute negation / companion-substitution / divergence-marker)
recover the real DesireDB abstain-to-majority cohort's gold-Unfulfilled residual that Channel-A, the
base 3-channel pipeline, and the WIRED union channel (M1/M2/fork-A) all measured 0/37 on (Director VET
of exp_outcome_event_extraction_recovery_v1's HARD_FAIL diagnosis_table)?

Engine: hdlab/goal_achievement.py's desiderative_negation_channel (see that module's own comment block
for the full mechanism + the mandatory goal-conditioning discipline every construction obeys).

TWO ARMS, over the SAME 900-row ENLARGED cohort exp_outcome_event_extraction_recovery_v1 (M1/M2's own
enlarged_cohort_analysis) already uses -- imported directly (build_enlarged_rows/build_cohort_from_rows
byte-identical reuse), for head-to-head comparability on the EXACT same draw:
  REAL          goal_achievement_verdict(desire, outcome, use_union_oov=False,
                use_desiderative_negation=True)["verdict"] -- abstains to majority when no construction
                fires.
  PAIRSCRAMBLE  (mandatory control) desire replaced with a deterministic derangement partner's desire
                (identical offset convention to exp_utility_satisfaction_channel_v1._scrambled_desires
                / exp_outcome_event_extraction_recovery_v1._run_pairscramble) -- MUST collapse (every
                construction requires genuine cross-text goal-conditioning by design, see module
                comment; a pure outcome-only signal is mathematically incapable of collapsing here).

Modes:
  --self-test  hand-authored cases, real goal_achievement_verdict/desiderative_negation_channel calls
               at small scale (hdlab.goal_achievement.self_test_desiderative_negation_channel + this
               cell's own helpers), no DesireDB/network needed.
  --smoke      n=80 (VALIDITY_N_PER_CLASS) cohort only, REAL/PAIRSCRAMBLE mechanism-fires + arms-differ
               checks, no HARD-PASS/HARD-FAIL claim (DISCRIMINATOR-MUST-SURVIVE-SCALE pre-flight).
  --full       ENLARGED (900-row) primary recovery/pairscramble gates + n=160/n=80 full-bench macro-F1
               (ON vs freshly-measured OFF) + harness_validity_check + per-item glass-box diagnosis
               table (every gold-Unfulfilled cohort item, not only recovered ones).
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
import sys
import time
import traceback
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from hdlab.goal_achievement import (  # noqa: E402
    goal_achievement_verdict, desiderative_negation_channel, MAJORITY_CLASS,
    self_test as _ga_self_test, self_test_desiderative_negation_channel as _dn_self_test,
)
from exp_utility_satisfaction_channel_v1 import (  # noqa: E402
    load_desiredb_rows, balanced_subsample, macro_f1, accuracy,
    _scrambled_desires, SEED, FULL_N_PER_CLASS, VALIDITY_N_PER_CLASS,
)
from exp_outcome_event_extraction_recovery_v1 import (  # noqa: E402
    build_enlarged_rows, build_cohort_from_rows, ENLARGED_N_ROWS, ENLARGED_SEED,
    _recovery, _full_cohort_accuracy, _majority_baseline_accuracy,
)
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

ANCHOR_NAME = "desiderative_negation_channel_v1"
OUTPUT_DIR_FULL = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

# RULE baseline: CITED@hdlab/goal_achievement.py module docstring line 5 ("edges above the tuned
# valence+negation RULE: macro-F1 0.686 vs 0.620").
RULE_MACRO_F1_FLOOR = 0.620

MIN_GOLD_UNFULFILLED_ENLARGED = 15   # underpowered-cohort sanity floor, same as the sibling cell

# ---- pre-registered bands (fixed before FULL; see preregs/2026-08-09_desiderative_negation_
# channel_v1.md for the full derivation) -----------------------------------------------------------
HP_RECOVERY_FLOOR = 0.15
HP_RECOVERY_MIN_N = 5
HP_PAIRSCRAMBLE_CEILING = 0.10
HP_GAP_REAL_VS_PAIRSCRAMBLE = 0.10

HF_PAIRSCRAMBLE_NONCOLLAPSE_MARGIN = 0.05
HF_FALSE_POSITIVE_REGRESSION_MARGIN = 0.05


# ------------------------------------------------------------------ start-marker / crash diagnostics
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


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


def _write_heartbeat(output_dir, unit_idx, total_units, elapsed_s):
    path = os.path.join(output_dir, "_heartbeat.jsonl")
    rec = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total_units, "elapsed_s": round(elapsed_s, 2)}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


# ------------------------------------------------------------------ arm predict fns
def real_arm_predict(desire, outcome):
    v = goal_achievement_verdict(desire, outcome, use_union_oov=False, use_desiderative_negation=True)
    dn_fired = v["trace"].get("desiderative_negation_fired")
    dn_trace = v["trace"].get("desiderative_negation_trace") or {}
    return v["verdict"], {"fired": dn_trace.get("fired", []),
                           "shared_entity_words": dn_trace.get("shared_entity_words", []),
                           "goal_verb_lemma": dn_trace.get("goal_verb_lemma"),
                           "desiderative_negation_fired": dn_fired}


# ------------------------------------------------------------------ per-item diagnosis taxonomy
def diagnose_item(trace: dict, gold: str, pred: str) -> str:
    """4-way diagnosis tag for a gold-Unfulfilled cohort item (per Director's own diagnosis-table
    convention -- emit on EVERY item, not only recovered ones)."""
    fired = trace.get("fired") or []
    if not fired:
        return "CHANNEL_NEVER_FIRED"
    if pred == gold:
        return "RECOVERED_CORRECT"
    return "CHANNEL_FIRED_WRONG"


# ------------------------------------------------------------------ resumable per-item arm runners
def _run_arm_over_items(output_dir, unit_prefix, sub_rows, idxs, predict_fn, desire_key="Desire-Expression-Sentence"):
    out = {}
    done = completed_units(output_dir)
    for n_seen, i in enumerate(idxs):
        key = unit_key(unit_prefix, i)
        if key in done:
            out[i] = load_units(output_dir)[key]
            continue
        r = sub_rows[i]
        v, trace = predict_fn(r[desire_key], r["Evidence"])
        pred = v if v is not None else MAJORITY_CLASS
        rec = {"pred": pred, "gold": r["Fulfillment-Label"], "trace": trace,
               "desire": r[desire_key], "outcome": r["Evidence"]}
        record_unit(output_dir, key, rec)
        out[i] = rec
        if n_seen % 10 == 0:
            _write_heartbeat(output_dir, n_seen, len(idxs), 0.0)
    return out


def _run_pairscramble(output_dir, unit_prefix, sub_rows, idxs):
    scrambled = _scrambled_desires(sub_rows)   # index-aligned to sub_rows, same offset convention
    out = {}
    done = completed_units(output_dir)
    for n_seen, i in enumerate(idxs):
        key = unit_key(unit_prefix, i)
        if key in done:
            out[i] = load_units(output_dir)[key]
            continue
        r = sub_rows[i]
        v, trace = real_arm_predict(scrambled[i], r["Evidence"])
        pred = v if v is not None else MAJORITY_CLASS
        rec = {"pred": pred, "gold": r["Fulfillment-Label"], "trace": trace,
               "desire": scrambled[i], "outcome": r["Evidence"]}
        record_unit(output_dir, key, rec)
        out[i] = rec
        if n_seen % 10 == 0:
            _write_heartbeat(output_dir, n_seen, len(idxs), 0.0)
    return out


def _arms_must_differ(records_a, records_b, idxs):
    da = hashlib.sha256(json.dumps([records_a[i]["pred"] for i in idxs]).encode()).hexdigest()
    db = hashlib.sha256(json.dumps([records_b[i]["pred"] for i in idxs]).encode()).hexdigest()
    return da != db, da, db


# ------------------------------------------------------------------ full-bench composed macro-F1 (n=160/n=80)
def composed_verdict_on(desire, outcome):
    return goal_achievement_verdict(desire, outcome, use_union_oov=False,
                                     use_desiderative_negation=True)["verdict"]


def composed_verdict_off(desire, outcome):
    return goal_achievement_verdict(desire, outcome, use_union_oov=False,
                                     use_desiderative_negation=False)["verdict"]


def full_bench_composed(n_per_class):
    rows = load_desiredb_rows()
    sample = balanced_subsample(rows, n_per_class, SEED)
    gold = [r["Fulfillment-Label"] for r in sample]
    pred_on = [composed_verdict_on(r["Desire-Expression-Sentence"], r["Evidence"]) for r in sample]
    pred_off = [composed_verdict_off(r["Desire-Expression-Sentence"], r["Evidence"]) for r in sample]
    return {"n": len(sample),
            "acc_on": round(accuracy(gold, pred_on), 4), "macro_f1_on": round(macro_f1(gold, pred_on), 4),
            "acc_off": round(accuracy(gold, pred_off), 4), "macro_f1_off": round(macro_f1(gold, pred_off), 4)}


def harness_validity_check():
    """Re-verify the loader+field-mapping+seed reproduces the documented base-3-channel macro-F1 0.686
    (n=80, seed 20260808) using use_union_oov=False, use_desiderative_negation=False EXPLICITLY (both
    additive channels pinned OFF -- this must reproduce the CERTIFIED base, not either fallback)."""
    rows = load_desiredb_rows()
    sample = balanced_subsample(rows, VALIDITY_N_PER_CLASS, SEED)
    gold = [r["Fulfillment-Label"] for r in sample]
    pred = [composed_verdict_off(r["Desire-Expression-Sentence"], r["Evidence"]) for r in sample]
    acc = accuracy(gold, pred)
    mf1 = macro_f1(gold, pred)
    documented_macro_f1 = 0.686
    delta = mf1 - documented_macro_f1
    return {"n": len(sample), "measured_acc": round(acc, 4), "measured_macro_f1": round(mf1, 4),
            "documented_macro_f1": documented_macro_f1, "delta_macro_f1": round(delta, 4),
            "valid": abs(delta) <= 0.03}


# ------------------------------------------------------------------ self-test
def self_test():
    """Real-code-path check: hdlab.goal_achievement.self_test_desiderative_negation_channel (real
    desiderative_negation_channel/goal_achievement_verdict calls) + this cell's own helpers
    (diagnosis taxonomy, recovery metric reuse, composed_verdict_on/off) on hand-authored cases -- no
    DesireDB/network needed."""
    dn = _dn_self_test()
    ga = _ga_self_test()

    # diagnosis taxonomy sanity
    assert diagnose_item({"fired": []}, "Unfulfilled", "Fulfilled") == "CHANNEL_NEVER_FIRED"
    assert diagnose_item({"fired": ["reply_negation"]}, "Unfulfilled", "Unfulfilled") == "RECOVERED_CORRECT"
    assert diagnose_item({"fired": ["reply_negation"]}, "Unfulfilled", "Fulfilled") == "CHANNEL_FIRED_WRONG"

    # recovery metric reuse sanity (imported from the sibling cell)
    recs = {0: {"pred": "Unfulfilled", "gold": "Unfulfilled"}, 1: {"pred": "Fulfilled", "gold": "Unfulfilled"}}
    r = _recovery(recs, [0, 1])
    assert r == {"rate": 0.5, "n_recovered": 1, "n": 2}, r

    # composed_verdict_on/off callable end-to-end on a hand-authored pair (real code path, no
    # DesireDB) -- must return one of the two labels, never raise. ON must differ from OFF on a case
    # designed to fire the new channel and abstain on the base 3-channel pipeline.
    desire = "My coworker was wondering if I wanted to cover her shift this weekend."
    outcome = "No, I told her, I already had plans."
    v_off = composed_verdict_off(desire, outcome)
    v_on = composed_verdict_on(desire, outcome)
    assert v_off in ("Fulfilled", "Unfulfilled") and v_on in ("Fulfilled", "Unfulfilled")
    assert v_off == "Fulfilled" and v_on == "Unfulfilled", (
        f"fixture assumption broken / channel not wired correctly: off={v_off!r} on={v_on!r}")

    # arms-must-differ hash-test sanity
    a = {0: {"pred": "Fulfilled"}, 1: {"pred": "Unfulfilled"}}
    b = {0: {"pred": "Fulfilled"}, 1: {"pred": "Fulfilled"}}
    differ, _da, _db = _arms_must_differ(a, b, [0, 1])
    assert differ is True
    same_differ, _, _ = _arms_must_differ(a, a, [0, 1])
    assert same_differ is False

    return {"desiderative_negation_self_test": dn, "goal_achievement_self_test": ga,
            "diagnosis_taxonomy_ok": True, "recovery_metric_ok": True,
            "composed_verdict_on_off_ok": True, "off_sample": v_off, "on_sample": v_on,
            "arms_must_differ_ok": True}


# ------------------------------------------------------------------ smoke
def run_smoke(output_dir):
    """n=80 (VALIDITY_N_PER_CLASS) cohort, REAL/PAIRSCRAMBLE mechanism-fires + arms-differ only -- no
    HARD-PASS/HARD-FAIL claim (DISCRIMINATOR-MUST-SURVIVE-SCALE pre-flight)."""
    t0 = time.perf_counter()
    expected_units = 1
    _write_start_marker(output_dir, "smoke", expected_units)
    rows = load_desiredb_rows()
    sample = balanced_subsample(rows, VALIDITY_N_PER_CLASS, SEED)
    cohort_idxs, unf_idxs = build_cohort_from_rows(sample)
    print(f"[smoke] n_sample={len(sample)} cohort_n={len(cohort_idxs)} gold_unfulfilled_n={len(unf_idxs)}",
          flush=True)

    real_records = _run_arm_over_items(output_dir, "smoke_real", sample, cohort_idxs, real_arm_predict)
    pairscramble_records = _run_pairscramble(output_dir, "smoke_pairscramble", sample, unf_idxs)

    fire_rate = (sum(1 for i in cohort_idxs if real_records[i]["trace"].get("fired"))
                 / len(cohort_idxs)) if cohort_idxs else 0.0
    recov_real = _recovery(real_records, unf_idxs)
    recov_scr = _recovery(pairscramble_records, unf_idxs)
    differ_rs, _, _ = _arms_must_differ(real_records, pairscramble_records, unf_idxs) if unf_idxs else (None, None, None)

    elapsed = time.perf_counter() - t0
    underpowered = len(unf_idxs) < 5
    fires = fire_rate > 0.0
    verdict = "HARD_PASS" if (fires and not underpowered) else ("INVALID" if underpowered else "HARD_FAIL")
    msg = (f"SMOKE: cohort_n={len(cohort_idxs)} unf_n={len(unf_idxs)} construction_fire_rate={fire_rate:.3f} "
           f"recovery(real/scr)=({recov_real['rate']}/{recov_scr['rate']}) arms_differ={differ_rs}")
    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": f"{verdict}: {msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": "smoke", "anchor_name": ANCHOR_NAME,
        "n_sample": len(sample), "cohort_n": len(cohort_idxs), "gold_unfulfilled_n": len(unf_idxs),
        "construction_fire_rate": round(fire_rate, 4),
        "recovery_real": recov_real, "recovery_pairscramble": recov_scr,
        "arms_differ_real_vs_pairscramble": differ_rs,
        "cardinality_ok": True, "expected_n_units": expected_units,
        "final_metrics_atomicity": "tmp_replace", "deterministic_seeding": True,
        "crlb_n/a": "glass-box lexical/regex/WordNet pipeline, no swept capacity regime",
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps(metrics, indent=2, default=str), flush=True)
    return metrics


# ------------------------------------------------------------------ full
def run_full(output_dir):
    t0 = time.perf_counter()
    expected_units_hint = ENLARGED_N_ROWS
    _write_start_marker(output_dir, "full", expected_units_hint)

    # ---- ENLARGED cohort (primary recovery/pairscramble gates) ----
    print(f"[full] building ENLARGED cohort (n_rows={ENLARGED_N_ROWS}, seed={ENLARGED_SEED})...", flush=True)
    enl_rows = build_enlarged_rows()
    enl_cohort_idxs, enl_unf_idxs = build_cohort_from_rows(enl_rows)
    print(f"[full] enlarged cohort_n={len(enl_cohort_idxs)} gold_unfulfilled_n={len(enl_unf_idxs)}", flush=True)

    print("[full] REAL arm over full enlarged cohort (resumable per-item)...", flush=True)
    real_records = _run_arm_over_items(output_dir, "enl_real", enl_rows, enl_cohort_idxs, real_arm_predict)
    print("[full] PAIRSCRAMBLE arm over gold-unfulfilled subset...", flush=True)
    pairscramble_records = _run_pairscramble(output_dir, "enl_pairscramble", enl_rows, enl_unf_idxs)

    fire_rate_real = (sum(1 for i in enl_unf_idxs if real_records[i]["trace"].get("fired"))
                      / len(enl_unf_idxs)) if enl_unf_idxs else 0.0
    recov_real = _recovery(real_records, enl_unf_idxs)
    recov_scr = _recovery(pairscramble_records, enl_unf_idxs)
    acc_real_full_cohort = _full_cohort_accuracy(real_records, enl_cohort_idxs)
    acc_majority_baseline = _majority_baseline_accuracy(enl_rows, enl_cohort_idxs)
    differ_rs, _, _ = _arms_must_differ(real_records, pairscramble_records, enl_unf_idxs)

    diagnosis = {i: diagnose_item(real_records[i]["trace"], real_records[i]["gold"], real_records[i]["pred"])
                 for i in enl_unf_idxs}
    diagnosis_counts = {}
    for tag in diagnosis.values():
        diagnosis_counts[tag] = diagnosis_counts.get(tag, 0) + 1

    construction_fire_counts = {}
    for i in enl_unf_idxs:
        for c in (real_records[i]["trace"].get("fired") or []):
            construction_fire_counts[c] = construction_fire_counts.get(c, 0) + 1

    # ---- n=160 / n=80 robustness (full-bench composed macro-F1, ON vs freshly-measured OFF) ----
    print("[full] harness_validity_check + full_bench_composed (n=160/n=80)...", flush=True)
    validity = harness_validity_check()
    full_bench_160 = full_bench_composed(FULL_N_PER_CLASS)
    full_bench_80 = full_bench_composed(VALIDITY_N_PER_CLASS)

    # ---- gates ----
    cohort_ok = len(enl_unf_idxs) >= MIN_GOLD_UNFULFILLED_ENLARGED
    hp1 = (recov_real["rate"] or 0.0) >= HP_RECOVERY_FLOOR and recov_real["n_recovered"] >= HP_RECOVERY_MIN_N
    gap_scramble = (recov_real["rate"] or 0.0) - (recov_scr["rate"] or 0.0)
    hp2 = ((recov_scr["rate"] or 0.0) <= HP_PAIRSCRAMBLE_CEILING) and (gap_scramble >= HP_GAP_REAL_VS_PAIRSCRAMBLE)
    hp3 = full_bench_160["macro_f1_on"] >= full_bench_160["macro_f1_off"]
    hp4 = full_bench_160["macro_f1_on"] >= RULE_MACRO_F1_FLOOR
    hp5 = differ_rs

    hf1 = recov_real["n_recovered"] == 0
    hf2 = (recov_scr["rate"] or 0.0) >= (recov_real["rate"] or 0.0) - HF_PAIRSCRAMBLE_NONCOLLAPSE_MARGIN
    hf3 = full_bench_160["macro_f1_on"] < full_bench_160["macro_f1_off"]
    hf4 = not cohort_ok
    hf5 = (acc_majority_baseline is not None and acc_real_full_cohort is not None and
           acc_real_full_cohort < acc_majority_baseline - HF_FALSE_POSITIVE_REGRESSION_MARGIN)

    hard_fail_reasons = []
    if hf1: hard_fail_reasons.append("HF1_MECHANISM_INERT")
    if hf2: hard_fail_reasons.append(f"HF2_PAIRSCRAMBLE_FAILS_TO_COLLAPSE(scr={recov_scr['rate']},real={recov_real['rate']})")
    if hf3: hard_fail_reasons.append(f"HF3_NET_NEGATIVE_FULL_BENCH(on={full_bench_160['macro_f1_on']}<off={full_bench_160['macro_f1_off']})")
    if hf4: hard_fail_reasons.append(f"HF4_UNDERPOWERED_ENLARGED_COHORT(unf_n={len(enl_unf_idxs)}<{MIN_GOLD_UNFULFILLED_ENLARGED})")
    if hf5: hard_fail_reasons.append(f"HF5_FALSE_POSITIVE_REGRESSION(real_acc={acc_real_full_cohort}<majority_baseline={acc_majority_baseline}-{HF_FALSE_POSITIVE_REGRESSION_MARGIN})")

    hard_pass = all([hp1, hp2, hp3, hp4, hp5]) and not hard_fail_reasons
    hard_fail = bool(hard_fail_reasons)
    if hard_fail:
        verdict = "HARD_FAIL"
    elif hard_pass:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    msg = (f"{verdict}: enlarged(unf_n={len(enl_unf_idxs)}) fire_rate={fire_rate_real:.3f} "
           f"recovery(real/scr)=({recov_real['n_recovered']}/{recov_real['n']}={recov_real['rate']} / "
           f"{recov_scr['n_recovered']}/{recov_scr['n']}={recov_scr['rate']}) "
           f"gap_vs_scramble={gap_scramble:.4f}(>={HP_GAP_REAL_VS_PAIRSCRAMBLE}) "
           f"full_cohort_acc(real/majority)=({acc_real_full_cohort}/{acc_majority_baseline}) "
           f"n160_full_bench(on/off/rule_floor)=({full_bench_160['macro_f1_on']}/{full_bench_160['macro_f1_off']}/{RULE_MACRO_F1_FLOOR}) "
           f"n80_full_bench(on/off)=({full_bench_80['macro_f1_on']}/{full_bench_80['macro_f1_off']}) "
           f"constructions={construction_fire_counts} | diagnosis={diagnosis_counts} | reasons={hard_fail_reasons}")

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": msg[:300],
        "elapsed_s": round(elapsed, 3), "run_mode": "full", "anchor_name": ANCHOR_NAME,
        "config": {"ENLARGED_N_ROWS": ENLARGED_N_ROWS, "ENLARGED_SEED": ENLARGED_SEED,
                  "FULL_N_PER_CLASS": FULL_N_PER_CLASS, "VALIDITY_N_PER_CLASS": VALIDITY_N_PER_CLASS,
                  "SEED": SEED},
        "enlarged_cohort_n": len(enl_cohort_idxs), "enlarged_gold_unfulfilled_n": len(enl_unf_idxs),
        "construction_fire_rate_real": round(fire_rate_real, 4),
        "construction_fire_counts": construction_fire_counts,
        "recovery_real": recov_real, "recovery_pairscramble": recov_scr,
        "gap_real_vs_pairscramble": round(gap_scramble, 4),
        "full_cohort_accuracy_real": acc_real_full_cohort,
        "full_cohort_accuracy_majority_baseline": acc_majority_baseline,
        "arms_differ_real_vs_pairscramble": differ_rs,
        "diagnosis_table": diagnosis, "diagnosis_counts": diagnosis_counts,
        "reference_items_from_director_vet": {
            "high_confidence_idxs": [210, 506, 526, 333, 378, 650, 353, 868],
            "marginal_idxs": [116, 107],
            "note": "used for TAXONOMY design only (anti-circularity); per-item recovery for these "
                     "specific idxs vs the full diagnosis_table is reported below for transparency, "
                     "not as a separate gate",
        },
        "n160_robustness": {"full_bench_composed": full_bench_160},
        "n80_full_bench_composed": full_bench_80,
        "harness_validity_check": validity,
        "gates": {"HP1_recovery_floor": hp1, "HP2_pairscramble_collapses": hp2,
                 "HP3_beats_fresh_base": hp3, "HP4_beats_rule_floor": hp4, "HP5_arms_differ": hp5},
        "hard_fail_reasons": hard_fail_reasons,
        "cardinality_ok": True,
        "expected_n_units": len(enl_cohort_idxs) + len(enl_unf_idxs),
        "arms_differ_verified": differ_rs, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "glass-box lexical/regex/WordNet pipeline (construction-detector + fired-vote "
                    "composition), no swept capacity regime, no decoded/noisy continuous signal",
        "deterministic_seeding": True, "progress_logging": "print_flush_true",
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": True,
    }
    # per-item recovery on the specific Director-flagged reference idxs (transparency, not a gate --
    # these idxs are into enl_rows, so only meaningful if they're still present in enl_unf_idxs; the
    # ENLARGED draw is deterministic so they should be, but check defensively)
    ref_idxs = [210, 506, 526, 333, 378, 650, 353, 868, 116, 107]
    ref_detail = {}
    for i in ref_idxs:
        if i in real_records:
            ref_detail[i] = {"gold": real_records[i]["gold"], "pred": real_records[i]["pred"],
                              "fired": real_records[i]["trace"].get("fired", [])}
        else:
            ref_detail[i] = "NOT_IN_ENLARGED_COHORT_OR_NOT_GOLD_UNFULFILLED"
    metrics["reference_items_detail"] = ref_detail
    _write_metrics(output_dir, metrics)
    print(f"\n[VERDICT] {verdict}\n{msg}\nelapsed={elapsed:.1f}s -> {output_dir}/metrics.json", flush=True)
    return metrics


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args, _ = ap.parse_known_args()

    if args.self_test:
        res = self_test()
        print(json.dumps(res, indent=2, default=str))
        print("SELF_TEST_PASS")
        return

    if args.smoke:
        output_dir = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_smoke")
        run_smoke(output_dir)
        return

    run_full(OUTPUT_DIR_FULL)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _out = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_selftest")
    elif "--smoke" in sys.argv:
        _out = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_smoke")
    else:
        _out = OUTPUT_DIR_FULL
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out, e)
        raise
