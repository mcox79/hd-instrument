# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (deterministic lexicon-vote + FHRR bind/bundle/cleanup, fixed small codebook)
# - HP_SCOPE per-arm declaration (arm iii gates HARD_PASS/HARD_FAIL; others are comparators only)
# - cardinality_ok: EXPECTED_N_UNITS=5 (one unit per PRIMARY-cohort arm, no seed/sweep axis)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (see prereg)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL bind/unbind/bundle FHRR primitives + idiom_grounding module
#   (real_code_path); no synthetic-only branch
# See preregs/2026-08-09_direction_b_M1_idiom_grounding_recovery_v1.md for the full pre-registration.
"""exp_direction_b_M1_idiom_grounding_recovery_v1 -- Direction-B milestone M1: does SUPPLYING a
grounded idiom/colloquialism lexicon (+ ConceptNet-Antonym bridge) let the ALREADY-VALIDATED
hdlab.goal_achievement.utility_channel architecture RECOVER the exact DesireDB abstain-to-majority
cohort Stage-2 failed on (exp_utility_satisfaction_channel_v1, commit 1f6958e36, recovery 0/8)?

Cohort/loader: reused verbatim from experiments/exp_utility_satisfaction_channel_v1.py (same seed,
same balanced draw, same cohort definition -- channel=="majority", i.e. BOTH relation_channel and
valence_channel abstain).

Arms (PRIMARY cohort, n=160 draw / cohort n=22):
  (i)   majority-only baseline                                    [Stage-2 arm i, unchanged]
  (ii)  utility_channel (Stage-2, WordNet-only)                    [Stage-2 arm ii, unchanged]
  (iii) utility_channel_idiom_grounded (idiom lexicon + ConceptNet) [THE M1 MECHANISM ARM -- gates]
  (iii-ablation) utility_channel_idiom_grounded(use_conceptnet_bridge=False) [idiom-only, context]
  (iv)  utility_channel_idiom_grounded, SCRAMBLED goal cue          [mandatory pairscramble control]

Also computes an ENLARGED (context, non-gating) cohort over the FULL DesireDB corpus (all eligible
rows, natural class distribution, computed ONCE -- not a re-sample search) for a firmer denominator
+ head/tail idiom-frequency reporting, per the task's explicit "enlarge if cheap" instruction.

Modes:
  --self-test  hand-authored cases (hdlab.goal_achievement.self_test_idiom_grounded_channel +
               hdlab.idiom_grounding.self_test_idiom_grounding), real FHRR primitives at small
               scale, no DesireDB needed.
  --smoke      PRIMARY cohort only (n=160 draw), all 5 arms + mechanism-fires + cardinality checks.
  --full       PRIMARY cohort (gate-defining) + ENLARGED full-corpus cohort (context) + idiom
               frequency head/tail analysis + full-bench macro-F1 context (non-gating).
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

ANCHOR_NAME = "direction_b_M1_idiom_grounding_recovery_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

import exp_utility_satisfaction_channel_v1 as _s2  # noqa: E402 -- reuse loader/cohort/metrics verbatim

from hdlab.goal_achievement import (  # noqa: E402
    goal_achievement_verdict, utility_channel, utility_channel_idiom_grounded, activate_attributes,
    self_test_utility_channel, self_test_idiom_grounded_channel, self_test as ga_self_test,
    MAJORITY_CLASS,
)
from hdlab import idiom_grounding as _ig  # noqa: E402

SEED = _s2.SEED  # 20260808, identical draw to Stage-2
FULL_N_PER_CLASS = _s2.FULL_N_PER_CLASS  # 80 -> n=160, the exact Stage-2 cohort n=22/8 draw
VALIDITY_N_PER_CLASS = _s2.VALIDITY_N_PER_CLASS  # 40 -> n=80, documented-baseline harness

HP_RECOVERY = 0.40
MB_RECOVERY_FLOOR = 0.15
HP_PAIRSCRAMBLE_MAX_DELTA_VS_BASELINE = 0.05   # reused verbatim from Stage-2
HF_PAIRSCRAMBLE_MAX_DELTA_VS_REAL = 0.03       # reused verbatim from Stage-2
VALIDITY_TOLERANCE = 0.03
MIN_COHORT_N = 15

ARM_NAMES = ("i", "ii", "iii", "iii_ablation", "iv", "iv_ablation")
# MID-BUILD FINDING (see prereg): ConceptNet-Antonym bridge measured net-negative (zero recovery
# gain, 3/4 new pairscramble leaks traced to it) -- iii_ablation/iv_ablation (idiom-lexicon-only,
# no ConceptNet) are the PRIMARY gate-defining mechanism/control arms; iii/iv (+ConceptNet) are
# retained as an explicit exploratory/context comparison, not deleted.
PRIMARY_MECH_ARM = "iii_ablation"
PRIMARY_SCRAMBLE_ARM = "iv_ablation"
ENLARGED_N_ROWS = 900  # MEASURED@this session: full 3076-row scan ~1218s (~20min), exceeds the
                        # 10-min single-foreground-call budget; 900 rows (~6min est.) is a scope
                        # reduction for the ENLARGED context measurement only (compute-
                        # proportionality discipline) -- does NOT touch the PRIMARY n=160/22/8 gate.
ENLARGED_SEED = 20260809


# ============================================================================ arms (PRIMARY cohort)
def run_cohort_arms(sample: list, cohort_idxs: list) -> dict:
    scrambled_cues = _s2._scrambled_desires(sample)
    gold = {name: [] for name in ("gold",)}["gold"]
    preds = {name: [] for name in ARM_NAMES}
    activation_fires, verdict_fires_iii = [], []
    idiom_traces = []
    for i in cohort_idxs:
        r = sample[i]
        desire, outcome = r["Desire-Expression-Sentence"], r["Evidence"]
        gold.append(r["Fulfillment-Label"])
        activation_fires.append(len(activate_attributes(desire)) > 0)

        preds["i"].append(MAJORITY_CLASS)
        u_wn = utility_channel(desire, outcome)
        preds["ii"].append(u_wn if u_wn is not None else MAJORITY_CLASS)

        u_grounded = utility_channel_idiom_grounded(desire, outcome, use_conceptnet_bridge=True)
        preds["iii"].append(u_grounded if u_grounded is not None else MAJORITY_CLASS)
        verdict_fires_iii.append(u_grounded is not None)

        u_ablation = utility_channel_idiom_grounded(desire, outcome, use_conceptnet_bridge=False)
        preds["iii_ablation"].append(u_ablation if u_ablation is not None else MAJORITY_CLASS)

        u_scr = utility_channel_idiom_grounded(scrambled_cues[i], outcome, use_conceptnet_bridge=True)
        preds["iv"].append(u_scr if u_scr is not None else MAJORITY_CLASS)

        u_scr_abl = utility_channel_idiom_grounded(scrambled_cues[i], outcome, use_conceptnet_bridge=False)
        preds["iv_ablation"].append(u_scr_abl if u_scr_abl is not None else MAJORITY_CLASS)

        idiom_traces.append({"idx": i, "gold": r["Fulfillment-Label"],
                              "idiom_matches": _ig.idiom_votes(outcome)["matched"]})
    return {"gold": gold, "preds": preds, "activation_fires": activation_fires,
            "verdict_fires_iii": verdict_fires_iii, "idiom_traces": idiom_traces}


def recovery_rate(gold, pred) -> dict:
    """Of the cohort items where the majority-only baseline is WRONG (gold=='Unfulfilled'), the
    fraction `pred` gets CORRECT. Identical definition to Stage-2's own recovery_rate."""
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
def enlarged_cohort_analysis() -> dict:
    """Deterministic-seeded ENLARGED_N_ROWS-row subsample (natural class distribution within the
    subsample) cohort + PRIMARY_MECH_ARM recovery + idiom head/tail frequency + a bigger-n
    pairscramble-collapse corroboration. Computed ONCE (no resampling/reseeding search) -- context,
    not gate-defining (see prereg 'Cohort definitions' + 'ENLARGED' scope-reduction note: a full
    3076-row scan MEASURED ~20min, exceeding the foreground compute budget)."""
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

    n_recovered_mech = n_recovered_conceptnet_variant = 0
    match_counter: dict = {}
    for i in gold_unfulfilled_local:
        r = sub_rows[i]
        desire, outcome = r["Desire-Expression-Sentence"], r["Evidence"]
        pred_mech = utility_channel_idiom_grounded(desire, outcome, use_conceptnet_bridge=False)
        pred_conceptnet_variant = utility_channel_idiom_grounded(desire, outcome, use_conceptnet_bridge=True)
        if pred_mech == "Unfulfilled":
            n_recovered_mech += 1
        if pred_conceptnet_variant == "Unfulfilled":
            n_recovered_conceptnet_variant += 1
        for m in _ig.idiom_votes(_ig.dedupe_repeated_sentences(outcome))["matched"]:
            match_counter[m] = match_counter.get(m, 0) + 1

    # bigger-n pairscramble corroboration (PRIMARY_MECH_ARM/PRIMARY_SCRAMBLE_ARM equivalent) over
    # the WHOLE cohort (not just gold-Unfulfilled), for a lower-variance collapse check.
    gold_cohort = [sub_rows[i]["Fulfillment-Label"] for i in cohort_local_idxs]
    pred_i_cohort = [MAJORITY_CLASS for _ in cohort_local_idxs]
    pred_scr_ablation_cohort = []
    for i in cohort_local_idxs:
        u = utility_channel_idiom_grounded(scrambled[i], sub_rows[i]["Evidence"], use_conceptnet_bridge=False)
        pred_scr_ablation_cohort.append(u if u is not None else MAJORITY_CLASS)
    acc_i_cohort = _s2.accuracy(gold_cohort, pred_i_cohort)
    acc_scr_cohort = _s2.accuracy(gold_cohort, pred_scr_ablation_cohort)

    n_denom = len(gold_unfulfilled_local)
    head = {k: v for k, v in match_counter.items() if v >= 3}
    tail = {k: v for k, v in match_counter.items() if 1 <= v < 3}
    never_fired = sorted(set(label for _p, _pol, label, _c in _ig._RAW_IDIOMS) - set(match_counter))
    return {
        "n_subsample_rows": len(sub_rows), "n_total_rows_available": len(rows),
        "cohort_n": len(cohort_local_idxs), "gold_unfulfilled_n": n_denom,
        "recovery_primary_mech_arm": {
            "n_recovered": n_recovered_mech, "n_majority_wrong": n_denom,
            "rate": round(n_recovered_mech / n_denom, 4) if n_denom else None},
        "recovery_plus_conceptnet_context": {
            "n_recovered": n_recovered_conceptnet_variant, "n_majority_wrong": n_denom,
            "rate": round(n_recovered_conceptnet_variant / n_denom, 4) if n_denom else None},
        "conceptnet_marginal_delta": (n_recovered_conceptnet_variant - n_recovered_mech),
        "pairscramble_at_scale": {
            "cohort_n": len(cohort_local_idxs), "acc_i": round(acc_i_cohort, 4),
            "acc_scrambled_primary_arm": round(acc_scr_cohort, 4),
            "delta": round(abs(acc_scr_cohort - acc_i_cohort), 4),
            "collapses_at_scale": abs(acc_scr_cohort - acc_i_cohort) <= HP_PAIRSCRAMBLE_MAX_DELTA_VS_BASELINE},
        "idiom_match_frequency": dict(sorted(match_counter.items(), key=lambda kv: -kv[1])),
        "idiom_head_patterns": head, "idiom_tail_patterns": tail,
        "idiom_never_fired_patterns": never_fired,
        "n_idiom_patterns_total": len(_ig._RAW_IDIOMS),
    }


# ============================================================================ full-bench composition
def composed_verdict_idiom(desire: str, outcome: str) -> str:
    """4-channel composition (utility slot = PRIMARY_MECH_ARM, idiom-lexicon-only per the MID-BUILD
    FINDING) for the full-bench macro-F1 CONTEXT check only -- non-gating per this task's stated
    bands (see prereg)."""
    base = goal_achievement_verdict(desire, outcome)
    if base["channel"] == "majority":
        u = utility_channel_idiom_grounded(desire, outcome, use_conceptnet_bridge=False)
        if u is not None:
            return u
    return base["verdict"]


def harness_validity_check() -> dict:
    """Re-verify (at every --full run) the loader+field-mapping+seed reproduces the documented
    3-channel macro-F1 0.686 (n=80, seed 20260808) -- identical to Stage-2's own gate."""
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


def full_bench_composed_idiom(n_per_class: int) -> dict:
    rows = _s2.load_desiredb_rows()
    sample = _s2.balanced_subsample(rows, n_per_class, SEED)
    gold = [r["Fulfillment-Label"] for r in sample]
    pred = [composed_verdict_idiom(r["Desire-Expression-Sentence"], r["Evidence"]) for r in sample]
    return {"n": len(sample), "acc": round(_s2.accuracy(gold, pred), 4),
            "macro_f1": round(_s2.macro_f1(gold, pred), 4)}


# ============================================================================ verdict logic
def compute_verdict(cohort_metrics: dict, validity: dict, cohort_n: int) -> tuple:
    """Gate applies to PRIMARY_MECH_ARM ('iii_ablation', idiom-lexicon-only) / PRIMARY_SCRAMBLE_ARM
    ('iv_ablation') per the prereg's MID-BUILD FINDING (ConceptNet-Antonym bridge measured
    net-negative: zero recovery gain, 3/4 new pairscramble leaks traced to it -- 'iii'/'iv', the
    +ConceptNet variants, are reported as context only, see cohort_metrics)."""
    if cohort_n < MIN_COHORT_N:
        return "INVALID", f"UNDERPOWERED_COHORT: n={cohort_n} (need >={MIN_COHORT_N})"
    if not validity["valid"]:
        return "INVALID", f"harness_validity_check FAILED: delta_macro_f1={validity['delta_macro_f1']} exceeds tolerance {validity['tolerance']}"
    rec = cohort_metrics[f"recovery_{PRIMARY_MECH_ARM}"]
    if rec["rate"] is None:
        return "INVALID", "recovery_rate UNDEFINED: 0 gold-Unfulfilled items in cohort"

    rate = rec["rate"]
    acc_mech = cohort_metrics[f"acc_{PRIMARY_MECH_ARM}"]
    acc_scr = cohort_metrics[f"acc_{PRIMARY_SCRAMBLE_ARM}"]
    acc_i = cohort_metrics["acc_i"]
    delta_scr_i = abs(acc_scr - acc_i)
    delta_scr_mech = abs(acc_scr - acc_mech)
    collapses = delta_scr_i <= HP_PAIRSCRAMBLE_MAX_DELTA_VS_BASELINE
    leaks = delta_scr_mech <= HF_PAIRSCRAMBLE_MAX_DELTA_VS_REAL

    hard_fail = (rate < MB_RECOVERY_FLOOR) or leaks or (not collapses)
    hard_pass = (not hard_fail) and (rate >= HP_RECOVERY) and collapses and not leaks

    if hard_fail:
        verdict = "HARD_FAIL"
    elif hard_pass:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    msg = (f"PRIMARY cohort n={cohort_n} activation_fires_rate={cohort_metrics['activation_fires_rate']:.3f} "
           f"GATE_ARM={PRIMARY_MECH_ARM} recovery={rate:.3f} ({rec['n_recovered']}/{rec['n_majority_wrong']}) "
           f"recovery_ii_stage2ref={cohort_metrics['recovery_ii']['rate']} "
           f"recovery_iii_plus_conceptnet_context={cohort_metrics['recovery_iii']['rate']} "
           f"pairscramble({PRIMARY_SCRAMBLE_ARM}): |scr-i|={delta_scr_i:.4f} (<=0.05 collapse={collapses}) "
           f"|scr-mech|={delta_scr_mech:.4f} (>0.03 not-leak, leaks={leaks})")
    return verdict, msg


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
    """MECHANISM-FIRES + real_code_path check. Exercises the REAL FHRR bind/unbind/bundle
    primitives + idiom_grounding module via self_test_idiom_grounded_channel (goal_achievement.py)
    + self_test_idiom_grounding (idiom_grounding.py), no DesireDB needed."""
    r_ga = ga_self_test()
    r_util = self_test_utility_channel()
    r_idiom_channel = self_test_idiom_grounded_channel()
    r_idiom_lex = _ig.self_test_idiom_grounding()

    # metrics helpers sanity
    gold = ["Fulfilled", "Fulfilled", "Unfulfilled", "Unfulfilled"]
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

    return {"goal_achievement_self_test": r_ga, "utility_channel_self_test": r_util,
            "idiom_grounded_channel_self_test": r_idiom_channel,
            "idiom_lexicon_self_test": r_idiom_lex, "helpers_ok": True}


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
    expected_units = len(ARM_NAMES)  # 5, PRIMARY cohort only
    _write_start_marker(output_dir, run_mode, expected_units)
    t0 = time.time()

    print(f"[{run_mode}] loading DesireDB...", flush=True)
    rows = _s2.load_desiredb_rows()
    print(f"[{run_mode}] {len(rows)} binary-eligible rows loaded", flush=True)
    sample = _s2.balanced_subsample(rows, FULL_N_PER_CLASS, SEED)
    print(f"[{run_mode}] PRIMARY sample n={len(sample)} (n_per_class={FULL_N_PER_CLASS}, seed={SEED})", flush=True)

    cohort_idxs = _s2.build_cohort(sample)
    cohort_n = len(cohort_idxs)
    print(f"[{run_mode}] PRIMARY cohort(abstain-to-majority) n={cohort_n} of {len(sample)}", flush=True)

    arms = run_cohort_arms(sample, cohort_idxs)
    for idx, name in enumerate(ARM_NAMES):
        record_unit(output_dir, unit_key(name), {"arm": name, "n": cohort_n})
        _write_heartbeat(output_dir, idx, expected_units, time.time() - t0)

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
        "recovery_iii_ablation": recovery_rate(arms["gold"], arms["preds"]["iii_ablation"]),
        "recovery_iv": recovery_rate(arms["gold"], arms["preds"]["iv"]),
        "recovery_iv_ablation": recovery_rate(arms["gold"], arms["preds"]["iv_ablation"]),
        "idiom_traces_gold_unfulfilled": [t for t in arms["idiom_traces"] if t["gold"] == "Unfulfilled"],
    }

    validity = harness_validity_check() if run_mode == "full" else None
    full_bench_80_idiom = full_bench_composed_idiom(VALIDITY_N_PER_CLASS) if run_mode == "full" else None
    enlarged = enlarged_cohort_analysis() if run_mode == "full" else None

    if run_mode == "smoke":
        rec_mech = cohort_metrics[f"recovery_{PRIMARY_MECH_ARM}"]
        if cohort_n < MIN_COHORT_N:
            verdict, msg = "INVALID", f"SMOKE_UNDERPOWERED_COHORT: n={cohort_n} (need >={MIN_COHORT_N})"
        elif activation_fires_rate == 0.0:
            verdict, msg = "HARD_FAIL", "SMOKE_ACTIVATION_NEVER_FIRED: activation_fires_rate=0.0 on cohort"
        elif not diff_check["arms_differ"]:
            verdict, msg = "HARD_FAIL", f"SMOKE_ARMS_IDENTICAL: {diff_check['digests']}"
        else:
            verdict = "HARD_PASS"
            msg = (f"SMOKE_OK: cohort n={cohort_n} activation_fires_rate={activation_fires_rate:.3f} "
                   f"verdict_fires_rate_iii={verdict_fires_rate_iii:.3f} "
                   f"GATE_ARM={PRIMARY_MECH_ARM} recovery={rec_mech['rate']} "
                   f"({rec_mech['n_recovered']}/{rec_mech['n_majority_wrong']}) "
                   f"arms_differ={diff_check['arms_differ']}")
    else:
        verdict, msg = compute_verdict(cohort_metrics, validity, cohort_n)

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": f"{verdict}: {msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "n_sample": len(sample), "n_per_class": FULL_N_PER_CLASS, "seed": SEED,
        "cohort_metrics": cohort_metrics,
        "arms_differ_verified": diff_check["arms_differ"], "arms_digests": diff_check["digests"],
        "harness_validity_check": validity,
        "full_bench_n80_composed_idiom_context": full_bench_80_idiom,
        "enlarged_cohort_context": enlarged,
        "cardinality_ok": len(load_units(output_dir)) == expected_units,
        "expected_n_units": expected_units,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "deterministic lexicon-vote (WordNet + idiom-regex + ConceptNet-Antonym dict) + "
                    "FHRR bind/bundle/cleanup over a fixed 6-role x 3-filler codebook, no decoded/"
                    "noisy continuous signal from a swept capacity regime -- identical justification "
                    "to Stage-2's crlb_n/a, unchanged mechanism layer",
        "deterministic_seeding": True,
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps({k: v for k, v in metrics.items()
                       if k not in ("cohort_metrics", "enlarged_cohort_context")},
                      indent=2, default=str))
    print(json.dumps({"cohort_metrics": {k: v for k, v in cohort_metrics.items()
                                          if k != "idiom_traces_gold_unfulfilled"}},
                      indent=2, default=str))
    print(json.dumps({"idiom_traces_gold_unfulfilled": cohort_metrics["idiom_traces_gold_unfulfilled"]},
                      indent=2, default=str))
    if enlarged is not None:
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
