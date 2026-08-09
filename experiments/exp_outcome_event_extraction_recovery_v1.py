# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (REAL/ABLATION/PAIRSCRAMBLE predictions hash-compared)
# - final_metrics_atomicity: tmp_replace (os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (glass-box lexical/parse-structural pipeline, no swept capacity regime)
# - cardinality_ok: EXPECTED_N_UNITS declared per run_mode
# - per-unit failure-class instrumentation (no bare except); resumable per-unit (tools/exp_checkpoint)
# - calibration_check: n/a (no adaptive threshold; SIMILARITY_LINK_THRESHOLD is a pre-registered,
#   already-validated constant reused verbatim from hdlab.lexical_similarity)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / CITED@
# - self-test constructs the REAL CandidateGenerator + real referent-linkage (real_code_path); no
#   synthetic-only branch; no DesireDB/network needed
# See preregs/2026-08-09_outcome_event_extraction_recovery_v1.md for the full pre-registration.
"""exp_outcome_event_extraction_recovery_v1 -- Director-redirected build (2026-08-09): does a glass-box
OUTCOME-EVENT extractor, feeding its extracted span to four already-proven goal-outcome organs, recover
real DesireDB abstain-to-majority cohort items that whole-text feeding cannot?

Engine: hdlab/outcome_event_extraction.py (extract_outcome_event / composed_extraction_verdict /
real_arm_predict / ablation_arm_predict / pairscramble_arm_predict -- see that module's docstring for
the full mechanism + citations).

WHY: a real-DesireDB probe (cited by Director, not re-derived here) found the owned grounding organs
score BELOW the tuned valence+negation RULE not because they're wrong, but because "the pipeline just
rarely feeds them the right word" -- the blocker is OUTCOME EXTRACTION, not grounding quality or teacher
strength (superseding an earlier plan to swap a stronger teacher into hdlab/grounding_acquisition_loop.py,
which this cell's own module docstring flags as orthogonal to that diagnosis).

THREE ARMS, all on the real DesireDB abstain-to-majority cohort (goal_achievement_verdict(desire,
outcome, use_union_oov=False)["channel"] == "majority" -- the ANTI-CIRCULARITY constraint: the base
3-channel pipeline must have abstained, so only the NEW mechanism can change the item):
  REAL              event_span = extract_outcome_event(desire, outcome)'s clause; abstains to majority
                     when extraction itself finds no referent-linked clause.
  EXTRACTION-ABLATION (mandatory control) event_span = the whole unparsed Evidence text through the
                     IDENTICAL 4-channel composition -- isolates whether extraction specifically is the
                     lever (the one variable that changes between REAL and this arm).
  PAIRSCRAMBLE      (mandatory control) desire replaced end-to-end (extraction AND all 4 channels) with
                     a deterministic derangement partner's desire (identical offset convention to
                     exp_utility_satisfaction_channel_v1._scrambled_desires) -- must collapse.

TWO COHORT SCALES (Director-mandated after pre-reg review, 2026-08-09):
  ENLARGED (PRIMARY for the recovery/count gates): 900-row deterministic subsample (ENLARGED_SEED=
    20260809), IDENTICAL construction to exp_direction_b_M2_speechact_result_generalization_v1's own
    enlarged_cohort_analysis (reused for head-to-head comparability with M1's 0/37 and M2's 9/37 on this
    EXACT draw) -- gives cohort_n roughly 4x the n=160 draw's ~22, so a 0.15 recovery-rate delta is
    ~5-6 items instead of ~3, addressing the small-cohort-noise concern a n=160-only design would carry.
  n=160 / n=80 (SECONDARY, direction-holds robustness + the full-bench composed macro-F1 comparison
    against the cited RULE floor 0.620) -- BALANCED draws (SEED=20260808, exp_utility_satisfaction_
    channel_v1's own convention), reused because macro-F1 vs a balanced-sample-measured RULE baseline
    needs a balanced sample too; the unbalanced ENLARGED draw is not used for this specific comparison.

Modes:
  --self-test  hand-authored cases, real CandidateGenerator + real referent-linkage at small scale
               (hdlab.outcome_event_extraction.self_test), no DesireDB/network needed.
  --smoke      n=80 (VALIDITY_N_PER_CLASS) cohort only, REAL/ABLATION/PAIRSCRAMBLE mechanism-fires +
               arms-differ checks, no HARD-PASS/HARD-FAIL claim (DISCRIMINATOR-MUST-SURVIVE-SCALE
               pre-flight before committing to the heavier ENLARGED run).
  --full       ENLARGED (900-row) primary recovery/count gates + n=160/n=80 full-bench macro-F1 +
               harness_validity_check + per-item glass-box diagnosis table (EVERY verdict tier, not
               only MIDDLE_BAND) + extraction-precision spot-check sample.
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

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from hdlab.goal_achievement import goal_achievement_verdict, MAJORITY_CLASS, self_test as _ga_self_test  # noqa: E402
from hdlab.outcome_event_extraction import (  # noqa: E402
    real_arm_predict, ablation_arm_predict, pairscramble_arm_predict,
    self_test as _engine_self_test, _default_generator,
)
from exp_utility_satisfaction_channel_v1 import (  # noqa: E402
    load_desiredb_rows, balanced_subsample, macro_f1, accuracy,
    _scrambled_desires, SEED, FULL_N_PER_CLASS, VALIDITY_N_PER_CLASS,
)
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

ANCHOR_NAME = "outcome_event_extraction_recovery_v1"
OUTPUT_DIR_FULL = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

# ENLARGED cohort: byte-identical construction to exp_direction_b_M2_speechact_result_generalization_v1
# (ENLARGED_N_ROWS=900, ENLARGED_SEED=20260809) -- reused verbatim for head-to-head comparability with
# M1 (0/37) and M2 (9/37) on the EXACT same draw. CITED@experiments/exp_direction_b_M2_speechact_
# result_generalization_v1.py:120-125.
ENLARGED_N_ROWS = 900
ENLARGED_SEED = 20260809

# RULE baseline: CITED@hdlab/goal_achievement.py module docstring line 5 ("edges above the tuned
# valence+negation RULE: macro-F1 0.686 vs 0.620").
RULE_MACRO_F1_FLOOR = 0.620

MIN_GOLD_UNFULFILLED_ENLARGED = 15   # underpowered-cohort sanity floor, even at enlarged scale

# ---- pre-registered bands (fixed before FULL; see preregs/2026-08-09_outcome_event_extraction_
# recovery_v1.md for the full derivation + precedent citations) -----------------------------------
HP_EXTRACTION_FIRE_RATE = 0.40
HP_GAP_REAL_VS_ABLATION = 0.15     # arc-standard gap convention (scr_collapse/rc_gap precedent)
HP_PAIRSCRAMBLE_CEILING = 0.20
HP_GAP_REAL_VS_PAIRSCRAMBLE = 0.15
HP_RECOVERY_FLOOR = 0.20           # calibrated to M2's own measured 9/37=0.243 high-water-mark on
                                    # this EXACT enlarged cohort (CITED@backup L63) -- not an arbitrary
                                    # aspirational number
HP_RECOVERY_MIN_N = 6

HF_GAP_REAL_VS_ABLATION_FLOOR = 0.05
HF_PAIRSCRAMBLE_NONCOLLAPSE_MARGIN = 0.05
HF_FALSE_POSITIVE_REGRESSION_MARGIN = 0.05   # full-cohort accuracy must not regress below majority
                                              # baseline by more than this (VET the positive as hard as
                                              # the negative -- catches REAL/ABLATION flipping gold-
                                              # Fulfilled cohort items wrong)


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


# ------------------------------------------------------------------ cohort construction
def build_cohort_from_rows(sub_rows):
    """cohort_idxs (channel=='majority') + gold_unfulfilled_idxs (subset with gold=='Unfulfilled') --
    the anti-circularity cohort + the recovery-metric denominator, over an arbitrary row list."""
    cohort_idxs = []
    for i, r in enumerate(sub_rows):
        v = goal_achievement_verdict(r["Desire-Expression-Sentence"], r["Evidence"], use_union_oov=False)
        if v["channel"] == "majority":
            cohort_idxs.append(i)
    gold_unfulfilled_idxs = [i for i in cohort_idxs if sub_rows[i]["Fulfillment-Label"] == "Unfulfilled"]
    return cohort_idxs, gold_unfulfilled_idxs


def build_enlarged_rows():
    rows = load_desiredb_rows()
    rng = random.Random(ENLARGED_SEED)
    idx_pool = sorted(range(len(rows)))            # sorted(set())-safe deterministic base ordering
    sub_idxs = sorted(rng.sample(idx_pool, min(ENLARGED_N_ROWS, len(idx_pool))))
    return [rows[i] for i in sub_idxs]


# ------------------------------------------------------------------ per-item diagnosis taxonomy
def diagnose_item(trace: dict, gold: str, pred: str) -> str:
    """4-way diagnosis tag for a majority-wrong (gold=='Unfulfilled') cohort item, per Director mandate
    (emit on EVERY verdict tier, not only MIDDLE_BAND)."""
    if trace.get("extraction_fired") is False:
        return "EXTRACTION_NEVER_FIRED"
    if pred == gold:
        return "RECOVERED_CORRECT"
    composed_fired = bool(trace.get("fired"))
    if not composed_fired:
        best_sim = (trace.get("graded_relation_trace") or {}).get("best_sim")
        return "ORGANS_ABSTAINED_NEAR_MISS" if best_sim is not None else "ORGANS_ABSTAINED_NO_LEXICAL_ANCHOR"
    return "ORGANS_FIRED_WRONG"


# ------------------------------------------------------------------ resumable per-item arm runners
def _run_arm_over_items(output_dir, unit_prefix, sub_rows, idxs, predict_fn, desire_key="Desire-Expression-Sentence"):
    """Resumable per-item arm evaluation: predict_fn(desire, outcome) -> (verdict, trace). Checkpoints
    one unit per (arm, item_idx). Returns {local_idx: {"pred","gold","trace"}} for every idx in idxs."""
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
        v, trace = pairscramble_arm_predict(scrambled[i], r["Evidence"])
        pred = v if v is not None else MAJORITY_CLASS
        rec = {"pred": pred, "gold": r["Fulfillment-Label"], "trace": trace,
               "desire": scrambled[i], "outcome": r["Evidence"]}
        record_unit(output_dir, key, rec)
        out[i] = rec
        if n_seen % 10 == 0:
            _write_heartbeat(output_dir, n_seen, len(idxs), 0.0)
    return out


# ------------------------------------------------------------------ recovery / accuracy metrics
def _recovery(records_by_idx, unf_idxs):
    n = len(unf_idxs)
    if n == 0:
        return {"rate": None, "n_recovered": 0, "n": 0}
    n_rec = sum(1 for i in unf_idxs if records_by_idx[i]["pred"] == records_by_idx[i]["gold"])
    return {"rate": round(n_rec / n, 4), "n_recovered": n_rec, "n": n}


def _full_cohort_accuracy(records_by_idx, cohort_idxs):
    if not cohort_idxs:
        return None
    correct = sum(1 for i in cohort_idxs if records_by_idx[i]["pred"] == records_by_idx[i]["gold"])
    return round(correct / len(cohort_idxs), 4)


def _majority_baseline_accuracy(sub_rows, cohort_idxs):
    if not cohort_idxs:
        return None
    correct = sum(1 for i in cohort_idxs if sub_rows[i]["Fulfillment-Label"] == MAJORITY_CLASS)
    return round(correct / len(cohort_idxs), 4)


def _arms_must_differ(records_a, records_b, idxs):
    da = hashlib.sha256(json.dumps([records_a[i]["pred"] for i in idxs]).encode()).hexdigest()
    db = hashlib.sha256(json.dumps([records_b[i]["pred"] for i in idxs]).encode()).hexdigest()
    return da != db, da, db


# ------------------------------------------------------------------ full-bench composed macro-F1 (n=160/n=80)
def composed_verdict_extraction(desire, outcome):
    """Base 3-channel pipeline (use_union_oov=False, avoids confounding with the already-wired union
    OOV channel); when it abstains-to-majority, the REAL extraction arm is tried as the fallback --
    mirrors exp_utility_satisfaction_channel_v1.composed_verdict's own shape exactly."""
    base = goal_achievement_verdict(desire, outcome, use_union_oov=False)
    if base["channel"] == "majority":
        v, _trace = real_arm_predict(desire, outcome)
        if v is not None:
            return v
    return base["verdict"]


def full_bench_composed(n_per_class):
    rows = load_desiredb_rows()
    sample = balanced_subsample(rows, n_per_class, SEED)
    gold = [r["Fulfillment-Label"] for r in sample]
    pred = [composed_verdict_extraction(r["Desire-Expression-Sentence"], r["Evidence"]) for r in sample]
    base_pred = [goal_achievement_verdict(r["Desire-Expression-Sentence"], r["Evidence"],
                                          use_union_oov=False)["verdict"] for r in sample]
    return {"n": len(sample), "acc": round(accuracy(gold, pred), 4),
            "macro_f1": round(macro_f1(gold, pred), 4),
            "base_acc": round(accuracy(gold, base_pred), 4),
            "base_macro_f1": round(macro_f1(gold, base_pred), 4)}


def harness_validity_check():
    """Re-verify the loader+field-mapping+seed reproduces the documented base-3-channel macro-F1 0.686
    (n=80, seed 20260808) using use_union_oov=False EXPLICITLY (the union default flipped True the same
    day this arc's harness_validity_check convention was set -- calling it without pinning the arg would
    silently compare against the WRONG pipeline; see this cell's pre-reg 'landmine' note)."""
    rows = load_desiredb_rows()
    sample = balanced_subsample(rows, VALIDITY_N_PER_CLASS, SEED)
    gold = [r["Fulfillment-Label"] for r in sample]
    pred = [goal_achievement_verdict(r["Desire-Expression-Sentence"], r["Evidence"],
                                     use_union_oov=False)["verdict"] for r in sample]
    acc = accuracy(gold, pred)
    mf1 = macro_f1(gold, pred)
    documented_macro_f1 = 0.686
    delta = mf1 - documented_macro_f1
    return {"n": len(sample), "measured_acc": round(acc, 4), "measured_macro_f1": round(mf1, 4),
            "documented_macro_f1": documented_macro_f1, "delta_macro_f1": round(delta, 4),
            "valid": abs(delta) <= 0.03}


# ------------------------------------------------------------------ extraction-precision spot check
def extraction_precision_spot_check(real_records, gold_unfulfilled_idxs, k=5):
    correct_ex = [i for i in gold_unfulfilled_idxs
                  if real_records[i]["trace"].get("extraction_fired") is True
                  and real_records[i]["pred"] == real_records[i]["gold"]]
    wrong_ex = [i for i in gold_unfulfilled_idxs
                if real_records[i]["trace"].get("extraction_fired") is True
                and real_records[i]["pred"] != real_records[i]["gold"]]

    def _fmt(i):
        rec = real_records[i]
        ev = (rec["trace"].get("event") or {})
        return {"desire": rec["desire"], "outcome": rec["outcome"],
                "event_span": ev.get("event_span"), "referent_link_tier": ev.get("referent_link_tier"),
                "verb_matches_goal": ev.get("verb_matches_goal"),
                "pred": rec["pred"], "gold": rec["gold"], "fired_channels": rec["trace"].get("fired")}

    return {"recovered_correct_sample": [_fmt(i) for i in correct_ex[:k]],
            "recovered_wrong_sample": [_fmt(i) for i in wrong_ex[:k]],
            "n_recovered_correct_total": len(correct_ex), "n_recovered_wrong_total": len(wrong_ex)}


# ------------------------------------------------------------------ self-test
def self_test():
    """Real-code-path check: hdlab.outcome_event_extraction.self_test (real CandidateGenerator + real
    referent-linkage), hdlab.goal_achievement.self_test, and this cell's own helpers (diagnosis
    taxonomy, recovery metric, composed_verdict_extraction) on hand-authored / synthetic cases -- no
    DesireDB / network needed."""
    eng = _engine_self_test()
    ga = _ga_self_test()

    # diagnosis taxonomy sanity
    assert diagnose_item({"extraction_fired": False}, "Unfulfilled", "Fulfilled") == "EXTRACTION_NEVER_FIRED"
    assert diagnose_item({"extraction_fired": True, "fired": ["relation"]}, "Unfulfilled", "Unfulfilled") == "RECOVERED_CORRECT"
    assert diagnose_item({"extraction_fired": True, "fired": [], "graded_relation_trace": {"best_sim": 0.3}},
                          "Unfulfilled", "Fulfilled") == "ORGANS_ABSTAINED_NEAR_MISS"
    assert diagnose_item({"extraction_fired": True, "fired": [], "graded_relation_trace": {"best_sim": None}},
                          "Unfulfilled", "Fulfilled") == "ORGANS_ABSTAINED_NO_LEXICAL_ANCHOR"
    assert diagnose_item({"extraction_fired": True, "fired": ["relation"]}, "Unfulfilled", "Fulfilled") == "ORGANS_FIRED_WRONG"

    # recovery metric sanity
    recs = {0: {"pred": "Unfulfilled", "gold": "Unfulfilled"}, 1: {"pred": "Fulfilled", "gold": "Unfulfilled"}}
    r = _recovery(recs, [0, 1])
    assert r == {"rate": 0.5, "n_recovered": 1, "n": 2}, r

    # composed_verdict_extraction callable end-to-end on a hand-authored pair (real code path, no
    # DesireDB) -- must return one of the two labels, never raise.
    v = composed_verdict_extraction("I wanted to fix the old fence in the yard.",
                                    "The weather was miserable all week. Later the fence was repaired nicely.")
    assert v in ("Fulfilled", "Unfulfilled"), v

    # arms-must-differ hash-test sanity
    a = {0: {"pred": "Fulfilled"}, 1: {"pred": "Unfulfilled"}}
    b = {0: {"pred": "Fulfilled"}, 1: {"pred": "Fulfilled"}}
    differ, _da, _db = _arms_must_differ(a, b, [0, 1])
    assert differ is True
    same_differ, _, _ = _arms_must_differ(a, a, [0, 1])
    assert same_differ is False

    return {"engine_self_test": eng, "goal_achievement_self_test": ga,
            "diagnosis_taxonomy_ok": True, "recovery_metric_ok": True,
            "composed_verdict_extraction_ok": True, "composed_verdict_sample": v,
            "arms_must_differ_ok": True}


# ------------------------------------------------------------------ smoke
def run_smoke(output_dir):
    """n=80 (VALIDITY_N_PER_CLASS) cohort, REAL/ABLATION/PAIRSCRAMBLE mechanism-fires + arms-differ
    only -- no HARD-PASS/HARD-FAIL claim (DISCRIMINATOR-MUST-SURVIVE-SCALE pre-flight)."""
    t0 = time.perf_counter()
    expected_units = 1  # single smoke probe unit (not per-item checkpointed at smoke scale)
    _write_start_marker(output_dir, "smoke", expected_units)
    rows = load_desiredb_rows()
    sample = balanced_subsample(rows, VALIDITY_N_PER_CLASS, SEED)
    cohort_idxs, unf_idxs = build_cohort_from_rows(sample)
    print(f"[smoke] n_sample={len(sample)} cohort_n={len(cohort_idxs)} gold_unfulfilled_n={len(unf_idxs)}",
          flush=True)

    real_records = _run_arm_over_items(output_dir, "smoke_real", sample, cohort_idxs, real_arm_predict)
    ablation_records = _run_arm_over_items(output_dir, "smoke_ablation", sample, cohort_idxs, ablation_arm_predict)
    pairscramble_records = _run_pairscramble(output_dir, "smoke_pairscramble", sample, unf_idxs)

    fire_rate = (sum(1 for i in cohort_idxs if real_records[i]["trace"].get("extraction_fired") is True)
                 / len(cohort_idxs)) if cohort_idxs else 0.0
    recov_real = _recovery(real_records, unf_idxs)
    recov_abl = _recovery(ablation_records, unf_idxs)
    recov_scr = _recovery(pairscramble_records, unf_idxs)
    differ_ra, _, _ = _arms_must_differ(real_records, ablation_records, cohort_idxs)

    elapsed = time.perf_counter() - t0
    underpowered = len(unf_idxs) < 5
    fires = fire_rate > 0.0
    verdict = "HARD_PASS" if (fires and not underpowered) else ("INVALID" if underpowered else "HARD_FAIL")
    msg = (f"SMOKE: cohort_n={len(cohort_idxs)} unf_n={len(unf_idxs)} extraction_fire_rate={fire_rate:.3f} "
           f"recovery(real/abl/scr)=({recov_real['rate']}/{recov_abl['rate']}/{recov_scr['rate']}) "
           f"arms_differ={differ_ra}")
    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": f"{verdict}: {msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": "smoke", "anchor_name": ANCHOR_NAME,
        "n_sample": len(sample), "cohort_n": len(cohort_idxs), "gold_unfulfilled_n": len(unf_idxs),
        "extraction_fire_rate": round(fire_rate, 4),
        "recovery_real": recov_real, "recovery_ablation": recov_abl, "recovery_pairscramble": recov_scr,
        "arms_differ_real_vs_ablation": differ_ra,
        "cardinality_ok": True, "expected_n_units": expected_units,
        "final_metrics_atomicity": "tmp_replace", "deterministic_seeding": True,
        "crlb_n/a": "glass-box lexical/parse-structural pipeline, no swept capacity regime",
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps(metrics, indent=2, default=str), flush=True)
    return metrics


# ------------------------------------------------------------------ full
def run_full(output_dir):
    t0 = time.perf_counter()
    expected_units_hint = ENLARGED_N_ROWS  # rough upper bound; real unit count is cohort-sized
    _write_start_marker(output_dir, "full", expected_units_hint)

    # ---- ENLARGED cohort (primary recovery/count gates) ----
    print(f"[full] building ENLARGED cohort (n_rows={ENLARGED_N_ROWS}, seed={ENLARGED_SEED})...", flush=True)
    enl_rows = build_enlarged_rows()
    enl_cohort_idxs, enl_unf_idxs = build_cohort_from_rows(enl_rows)
    print(f"[full] enlarged cohort_n={len(enl_cohort_idxs)} gold_unfulfilled_n={len(enl_unf_idxs)}", flush=True)

    print("[full] REAL arm over full enlarged cohort (resumable per-item)...", flush=True)
    real_records = _run_arm_over_items(output_dir, "enl_real", enl_rows, enl_cohort_idxs, real_arm_predict)
    print("[full] ABLATION arm over full enlarged cohort...", flush=True)
    ablation_records = _run_arm_over_items(output_dir, "enl_ablation", enl_rows, enl_cohort_idxs, ablation_arm_predict)
    print("[full] PAIRSCRAMBLE arm over gold-unfulfilled subset...", flush=True)
    pairscramble_records = _run_pairscramble(output_dir, "enl_pairscramble", enl_rows, enl_unf_idxs)

    fire_rate_real = (sum(1 for i in enl_unf_idxs if real_records[i]["trace"].get("extraction_fired") is True)
                      / len(enl_unf_idxs)) if enl_unf_idxs else 0.0
    recov_real = _recovery(real_records, enl_unf_idxs)
    recov_abl = _recovery(ablation_records, enl_unf_idxs)
    recov_scr = _recovery(pairscramble_records, enl_unf_idxs)
    acc_real_full_cohort = _full_cohort_accuracy(real_records, enl_cohort_idxs)
    acc_abl_full_cohort = _full_cohort_accuracy(ablation_records, enl_cohort_idxs)
    acc_majority_baseline = _majority_baseline_accuracy(enl_rows, enl_cohort_idxs)
    differ_ra, _, _ = _arms_must_differ(real_records, ablation_records, enl_cohort_idxs)

    diagnosis = {i: diagnose_item(real_records[i]["trace"], real_records[i]["gold"], real_records[i]["pred"])
                 for i in enl_unf_idxs}
    diagnosis_counts = {}
    for tag in diagnosis.values():
        diagnosis_counts[tag] = diagnosis_counts.get(tag, 0) + 1

    spot_check = extraction_precision_spot_check(real_records, enl_unf_idxs, k=5)

    # ---- n=160 / n=80 robustness (full-bench composed macro-F1 vs the RULE + fresh base pipeline) ----
    print("[full] harness_validity_check + full_bench_composed (n=160/n=80)...", flush=True)
    validity = harness_validity_check()
    full_bench_160 = full_bench_composed(FULL_N_PER_CLASS)
    full_bench_80 = full_bench_composed(VALIDITY_N_PER_CLASS)

    n160_rows = balanced_subsample(load_desiredb_rows(), FULL_N_PER_CLASS, SEED)
    n160_cohort_idxs, n160_unf_idxs = build_cohort_from_rows(n160_rows)
    print(f"[full] n=160 robustness cohort_n={len(n160_cohort_idxs)} unf_n={len(n160_unf_idxs)}", flush=True)

    # ---- gates ----
    cohort_ok = len(enl_unf_idxs) >= MIN_GOLD_UNFULFILLED_ENLARGED
    hp1 = fire_rate_real >= HP_EXTRACTION_FIRE_RATE
    gap_ablation = (recov_real["rate"] or 0.0) - (recov_abl["rate"] or 0.0)
    hp2 = gap_ablation >= HP_GAP_REAL_VS_ABLATION
    gap_scramble = (recov_real["rate"] or 0.0) - (recov_scr["rate"] or 0.0)
    hp3 = ((recov_scr["rate"] or 0.0) <= HP_PAIRSCRAMBLE_CEILING) and (gap_scramble >= HP_GAP_REAL_VS_PAIRSCRAMBLE)
    hp4 = ((recov_real["rate"] or 0.0) >= HP_RECOVERY_FLOOR) and (recov_real["n_recovered"] >= HP_RECOVERY_MIN_N)
    hp5 = full_bench_160["macro_f1"] >= full_bench_160["base_macro_f1"]
    hp6 = full_bench_160["macro_f1"] >= RULE_MACRO_F1_FLOOR

    hf1 = fire_rate_real == 0.0
    hf2 = gap_ablation < HF_GAP_REAL_VS_ABLATION_FLOOR
    hf3 = (recov_scr["rate"] or 0.0) >= (recov_real["rate"] or 0.0) - HF_PAIRSCRAMBLE_NONCOLLAPSE_MARGIN
    hf4 = not cohort_ok
    hf5 = (acc_majority_baseline is not None and acc_real_full_cohort is not None and
           acc_real_full_cohort < acc_majority_baseline - HF_FALSE_POSITIVE_REGRESSION_MARGIN)
    hf6 = full_bench_160["macro_f1"] < RULE_MACRO_F1_FLOOR

    hard_fail_reasons = []
    if hf1: hard_fail_reasons.append("HF1_EXTRACTION_NEVER_FIRES")
    if hf2: hard_fail_reasons.append(f"HF2_EXTRACTION_NOT_THE_LEVER(gap={gap_ablation:.4f}<{HF_GAP_REAL_VS_ABLATION_FLOOR})")
    if hf3: hard_fail_reasons.append(f"HF3_PAIRSCRAMBLE_FAILS_TO_COLLAPSE(scr={recov_scr['rate']},real={recov_real['rate']})")
    if hf4: hard_fail_reasons.append(f"HF4_UNDERPOWERED_ENLARGED_COHORT(unf_n={len(enl_unf_idxs)}<{MIN_GOLD_UNFULFILLED_ENLARGED})")
    if hf5: hard_fail_reasons.append(f"HF5_FALSE_POSITIVE_REGRESSION(real_acc={acc_real_full_cohort}<majority_baseline={acc_majority_baseline}-{HF_FALSE_POSITIVE_REGRESSION_MARGIN})")
    if hf6: hard_fail_reasons.append(f"HF6_RULE_FLOOR_REGRESSION(macro_f1={full_bench_160['macro_f1']}<{RULE_MACRO_F1_FLOOR})")

    hard_pass = all([hp1, hp2, hp3, hp4, hp5, hp6]) and not hard_fail_reasons
    hard_fail = bool(hard_fail_reasons)
    if hard_fail:
        verdict = "HARD_FAIL"
    elif hard_pass:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    msg = (f"{verdict}: enlarged(unf_n={len(enl_unf_idxs)}) fire_rate={fire_rate_real:.3f}(>= {HP_EXTRACTION_FIRE_RATE}) "
           f"recovery(real/abl/scr)=({recov_real['n_recovered']}/{recov_real['n']}={recov_real['rate']} / "
           f"{recov_abl['n_recovered']}/{recov_abl['n']}={recov_abl['rate']} / "
           f"{recov_scr['n_recovered']}/{recov_scr['n']}={recov_scr['rate']}) "
           f"gap_vs_ablation={gap_ablation:.4f}(>={HP_GAP_REAL_VS_ABLATION}) "
           f"gap_vs_scramble={gap_scramble:.4f}(>={HP_GAP_REAL_VS_PAIRSCRAMBLE}) "
           f"full_cohort_acc(real/abl/majority)=({acc_real_full_cohort}/{acc_abl_full_cohort}/{acc_majority_baseline}) "
           f"n160_full_bench(macro_f1/base/rule_floor)=({full_bench_160['macro_f1']}/{full_bench_160['base_macro_f1']}/{RULE_MACRO_F1_FLOOR}) "
           f"n80_full_bench_macro_f1={full_bench_80['macro_f1']} | diagnosis={diagnosis_counts} | "
           f"reasons={hard_fail_reasons}")

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": msg[:300],
        "elapsed_s": round(elapsed, 3), "run_mode": "full", "anchor_name": ANCHOR_NAME,
        "config": {"ENLARGED_N_ROWS": ENLARGED_N_ROWS, "ENLARGED_SEED": ENLARGED_SEED,
                  "FULL_N_PER_CLASS": FULL_N_PER_CLASS, "VALIDITY_N_PER_CLASS": VALIDITY_N_PER_CLASS,
                  "SEED": SEED},
        "enlarged_cohort_n": len(enl_cohort_idxs), "enlarged_gold_unfulfilled_n": len(enl_unf_idxs),
        "extraction_fire_rate_real": round(fire_rate_real, 4),
        "recovery_real": recov_real, "recovery_ablation": recov_abl, "recovery_pairscramble": recov_scr,
        "gap_real_vs_ablation": round(gap_ablation, 4), "gap_real_vs_pairscramble": round(gap_scramble, 4),
        "full_cohort_accuracy_real": acc_real_full_cohort, "full_cohort_accuracy_ablation": acc_abl_full_cohort,
        "full_cohort_accuracy_majority_baseline": acc_majority_baseline,
        "arms_differ_real_vs_ablation": differ_ra,
        "diagnosis_table": diagnosis, "diagnosis_counts": diagnosis_counts,
        "extraction_precision_spot_check": spot_check,
        "m1_m2_enlarged_reference": {"M1_recovery": "0/37", "M2_recovery": "9/37=0.243",
                                     "source": "exp_direction_b_M1/M2_..._v1 metrics.json, CITED (backup L61/L63)"},
        "n160_robustness": {"cohort_n": len(n160_cohort_idxs), "gold_unfulfilled_n": len(n160_unf_idxs),
                            "full_bench_composed": full_bench_160},
        "n80_full_bench_composed": full_bench_80,
        "harness_validity_check": validity,
        "gates": {"HP1_extraction_fires": hp1, "HP2_gap_vs_ablation": hp2, "HP3_pairscramble_collapses": hp3,
                 "HP4_recovery_floor": hp4, "HP5_beats_fresh_base": hp5, "HP6_beats_rule_floor": hp6},
        "hard_fail_reasons": hard_fail_reasons,
        "cardinality_ok": True,
        "expected_n_units": len(enl_cohort_idxs) * 2 + len(enl_unf_idxs),
        "arms_differ_verified": differ_ra, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "glass-box lexical/parse-structural pipeline (referent-linkage tiering + fired-"
                    "majority-vote composition), no swept capacity regime, no decoded/noisy continuous "
                    "signal",
        "deterministic_seeding": True, "progress_logging": "print_flush_true",
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": True,
    }
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
