# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (deterministic lexicon-vote + FHRR bind/bundle/cleanup, fixed small codebook)
# - HP_SCOPE per-arm declaration (arm ii gates HARD_PASS/HARD_FAIL; i/iii are comparators only)
# - cardinality_ok: EXPECTED_N_UNITS=3 (one unit per arm, no seed/sweep axis)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (see prereg)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL bind/unbind/bundle FHRR primitives (real_code_path); no
#   synthetic-only branch
# See preregs/2026-08-09_utility_satisfaction_channel_v1.md for the full pre-registration.
"""exp_utility_satisfaction_channel_v1 -- 3-arm falsification test for the grounded utility-
satisfaction 4th channel (hdlab.goal_achievement.utility_channel) on real DesireDB
(Rahimtoroghi, Wu, Wang, Anand & Walker, SIGDIAL 2017).

Cohort: items where goal_achievement_verdict(desire, outcome)["channel"] == "majority" (BOTH
relation_channel and valence_channel abstain).

Arms: (i) majority-only baseline, (ii) utility_channel-augmented (fires ? its verdict : majority),
(iii) utility_channel with a SCRAMBLED goal cue [mandatory falsification control].

DesireDB provenance / loader: identical to experiments/exp_goal_cued_valence_channel_v1.py (see that
cell's docstring for the byte-size-verified public-source details). outcome field = "Evidence",
desire field = "Desire-Expression-Sentence".

Modes:
  --self-test  hand-authored cases + real FHRR bind/unbind/bundle at small scale, no DesireDB needed
  --smoke      DesireDB n=80 balanced (40/class, seed 20260808), all 3 arms + cohort/fires checks
  --full       DesireDB n=160 balanced (80/class, seed 20260808) for the 3-arm cohort comparison;
               ALSO recomputes the n=80 harness_validity_check and the n=80 full-bench composed
               macro-F1 (the documented-baseline no-regression gate).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import csv
import hashlib
import json
import platform
import random
import sys
import time
import traceback
import urllib.request
from datetime import datetime, timezone

ANCHOR_NAME = "utility_satisfaction_channel_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

from hdlab.goal_achievement import (  # noqa: E402
    goal_achievement_verdict, utility_channel, activate_attributes,
    self_test_utility_channel, self_test as ga_self_test, MAJORITY_CLASS,
)

DESIREDB_RAW_URL = "https://raw.githubusercontent.com/ra-elahe/DesireDB/main/DesireDB.csv"
DESIREDB_CACHE = os.path.join(REPO_ROOT, "data", "desiredb_cache", "DesireDB.csv")
SEED = 20260808
FULL_N_PER_CLASS = 80    # n=160 total -- the cohort/3-arm draw (MEASURED@this session's calibration
                          # probe: cohort n=22 at this draw, 14 gold-Fulfilled / 8 gold-Unfulfilled)
SMOKE_N_PER_CLASS = 40   # n=80 -- DISCRIMINATOR-MUST-SURVIVE-SCALE: Stage-1 found n=20(10/class) too
                          # sparse for cohort power; n=80(40/class) MEASURED cohort n=16 (this
                          # session's calibration probe), enough to exercise the mechanism in smoke.
VALIDITY_N_PER_CLASS = 40  # n=80, matches the documented 0.686/0.706/0.688 benchmark exactly

HP_RECOVERY = 0.40
MB_RECOVERY_FLOOR = 0.15
HP_FULL_BENCH_MACRO_F1 = 0.686
HF_FULL_BENCH_MACRO_F1_FLOOR = 0.620
HP_PAIRSCRAMBLE_MAX_DELTA_VS_BASELINE = 0.05
HF_PAIRSCRAMBLE_MAX_DELTA_VS_REAL = 0.03
VALIDITY_TOLERANCE = 0.03
MIN_COHORT_N = 15

csv.field_size_limit(10_000_000)


# ============================================================================ DesireDB loader
# (byte-identical convention to exp_goal_cued_valence_channel_v1.py)
def _fetch_desiredb() -> str:
    if os.path.exists(DESIREDB_CACHE) and os.path.getsize(DESIREDB_CACHE) > 1_000_000:
        return DESIREDB_CACHE
    os.makedirs(os.path.dirname(DESIREDB_CACHE), exist_ok=True)
    tmp = DESIREDB_CACHE + ".tmp"
    with urllib.request.urlopen(DESIREDB_RAW_URL, timeout=30) as resp:
        data = resp.read()
    if len(data) < 1_000_000:
        raise RuntimeError(f"DesireDB fetch from {DESIREDB_RAW_URL} returned only {len(data)} bytes "
                            f"(expected ~3.99MB) -- refusing to cache a truncated/error response")
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, DESIREDB_CACHE)
    return DESIREDB_CACHE


def load_desiredb_rows() -> list:
    path = _fetch_desiredb()
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        rows = list(csv.DictReader(f))
    return [r for r in rows if r.get("Fulfillment-Label") in ("Fulfilled", "Unfulfilled")]


def balanced_subsample(rows: list, n_per_class: int, seed: int) -> list:
    pos = [r for r in rows if r["Fulfillment-Label"] == "Fulfilled"]
    neg = [r for r in rows if r["Fulfillment-Label"] == "Unfulfilled"]
    rng = random.Random(seed)
    return rng.sample(pos, n_per_class) + rng.sample(neg, n_per_class)


# ============================================================================ metrics
def macro_f1(gold, pred, classes=("Fulfilled", "Unfulfilled")) -> float:
    f1s = []
    for c in classes:
        tp = sum(1 for g, p in zip(gold, pred) if g == c and p == c)
        fp = sum(1 for g, p in zip(gold, pred) if g != c and p == c)
        fn = sum(1 for g, p in zip(gold, pred) if g == c and p != c)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1s.append(2 * prec * rec / (prec + rec) if (prec + rec) else 0.0)
    return sum(f1s) / len(f1s)


def accuracy(gold, pred) -> float:
    return sum(1 for g, p in zip(gold, pred) if g == p) / len(gold) if gold else 0.0


# ============================================================================ cohort + arms
def build_cohort(sample: list) -> list:
    """Indices of `sample` where goal_achievement_verdict abstains-to-majority (channel=="majority",
    i.e. BOTH relation_channel and valence_channel returned None)."""
    idxs = []
    for i, r in enumerate(sample):
        v = goal_achievement_verdict(r["Desire-Expression-Sentence"], r["Evidence"])
        if v["channel"] == "majority":
            idxs.append(i)
    return idxs


def _scrambled_desires(sample: list) -> list:
    """Deterministic derangement, identical convention to exp_goal_cued_valence_channel_v1.py's
    _scrambled_desires: item i's scrambled cue source = item (i + n//2) % n (PROT-023 compliant, not
    hash()-derived)."""
    n = len(sample)
    off = max(1, n // 2)
    return [sample[(i + off) % n]["Desire-Expression-Sentence"] for i in range(n)]


def run_cohort_arms(sample: list, cohort_idxs: list) -> dict:
    """Predictions for arms (i)/(ii)/(iii) restricted to the cohort indices.

    Tracks TWO distinct fire signals (do not conflate them):
      activation_fires -- activate_attributes(desire) is non-empty (the STAGE-1-KILLER check per the
        prereg: this is purely a GOAL-side lookup, proves the mechanism is not tautologically blocked
        the way Stage-1's was).
      verdict_fires -- utility_channel(desire, outcome) returns non-None (activation AND outcome
        evidence-scoring both succeeded well enough to reach a non-abstain verdict; this is what
        actually drives recovery_rate).
    """
    scrambled_cues = _scrambled_desires(sample)
    gold, pred_i, pred_ii, pred_iii = [], [], [], []
    activation_fires, verdict_fires = [], []
    for i in cohort_idxs:
        r = sample[i]
        desire, outcome = r["Desire-Expression-Sentence"], r["Evidence"]
        gold.append(r["Fulfillment-Label"])
        pred_i.append(MAJORITY_CLASS)
        activation_fires.append(len(activate_attributes(desire)) > 0)
        u_real = utility_channel(desire, outcome)
        pred_ii.append(u_real if u_real is not None else MAJORITY_CLASS)
        u_scr = utility_channel(scrambled_cues[i], outcome)
        pred_iii.append(u_scr if u_scr is not None else MAJORITY_CLASS)
        verdict_fires.append(u_real is not None)
    return {"gold": gold, "i": pred_i, "ii": pred_ii, "iii": pred_iii,
            "activation_fires": activation_fires, "verdict_fires": verdict_fires}


def recovery_rate(gold, pred_ii) -> dict:
    """Of the cohort items where the majority-only baseline is WRONG (gold=="Unfulfilled"), the
    fraction utility_channel (arm ii) gets CORRECT. See prereg 'Metrics' section for the rationale
    (credits genuine discrimination, not raw majority-skewed accuracy)."""
    wrong_idxs = [k for k, g in enumerate(gold) if g == "Unfulfilled"]
    if not wrong_idxs:
        return {"n_majority_wrong": 0, "n_recovered": 0, "rate": None}
    n_rec = sum(1 for k in wrong_idxs if pred_ii[k] == gold[k])
    return {"n_majority_wrong": len(wrong_idxs), "n_recovered": n_rec,
            "rate": round(n_rec / len(wrong_idxs), 4)}


def _arms_must_differ(preds: dict) -> dict:
    digests = {name: hashlib.sha256(json.dumps(preds[name]).encode()).hexdigest()
               for name in ("i", "ii", "iii")}
    all_same = len(set(digests.values())) == 1
    return {"digests": digests, "arms_differ": not all_same}


# ============================================================================ full-bench composition
def composed_verdict(desire: str, outcome: str) -> str:
    """4-channel composition for the full-bench macro-F1 gate ONLY -- NOT the production default
    precedence (utility_channel is not wired into goal_achievement_verdict). See prereg
    'Composition' section for why no re-application of the contrast-override is needed."""
    base = goal_achievement_verdict(desire, outcome)
    if base["channel"] == "majority":
        u = utility_channel(desire, outcome)
        if u is not None:
            return u
    return base["verdict"]


def harness_validity_check() -> dict:
    """Re-verify (at every --full run) that the loader+field-mapping+seed construction reproduces
    goal_achievement_verdict's documented macro-F1 0.686/F1 0.706/acc 0.688 (n=80, seed 20260808),
    using the UNCHANGED 3-channel pipeline (not this cell's utility channel). INVALID gate if
    delta > 0.03."""
    rows = load_desiredb_rows()
    sample = balanced_subsample(rows, VALIDITY_N_PER_CLASS, SEED)
    gold = [r["Fulfillment-Label"] for r in sample]
    pred = [goal_achievement_verdict(r["Desire-Expression-Sentence"], r["Evidence"])["verdict"]
            for r in sample]
    acc = accuracy(gold, pred)
    mf1 = macro_f1(gold, pred)
    documented = {"macro_f1": 0.686, "f1": None, "acc": 0.688}
    delta = mf1 - documented["macro_f1"]
    return {"n": len(sample), "measured_acc": round(acc, 4), "measured_macro_f1": round(mf1, 4),
            "documented_macro_f1": documented["macro_f1"], "delta_macro_f1": round(delta, 4),
            "valid": abs(delta) <= VALIDITY_TOLERANCE, "tolerance": VALIDITY_TOLERANCE}


def full_bench_composed(n_per_class: int) -> dict:
    """Composed 4-channel macro-F1 on a fresh balanced sample of the given size (n=80 for the
    documented-baseline no-regression gate; also called at n=160 for context)."""
    rows = load_desiredb_rows()
    sample = balanced_subsample(rows, n_per_class, SEED)
    gold = [r["Fulfillment-Label"] for r in sample]
    pred = [composed_verdict(r["Desire-Expression-Sentence"], r["Evidence"]) for r in sample]
    return {"n": len(sample), "acc": round(accuracy(gold, pred), 4),
            "macro_f1": round(macro_f1(gold, pred), 4)}


# ============================================================================ verdict logic
def compute_verdict(cohort_metrics: dict, full_bench_80: dict, validity: dict, cohort_n: int) -> tuple:
    if cohort_n < MIN_COHORT_N:
        return "INVALID", f"UNDERPOWERED_COHORT: n={cohort_n} (need >={MIN_COHORT_N})"
    if not validity["valid"]:
        return "INVALID", f"harness_validity_check FAILED: delta_macro_f1={validity['delta_macro_f1']} exceeds tolerance {validity['tolerance']}"
    rec = cohort_metrics["recovery"]
    if rec["rate"] is None:
        return "INVALID", "recovery_rate UNDEFINED: 0 gold-Unfulfilled items in cohort"

    rate = rec["rate"]
    fb_f1 = full_bench_80["macro_f1"]
    delta_iii_i = abs(cohort_metrics["acc_iii"] - cohort_metrics["acc_i"])
    delta_iii_ii = abs(cohort_metrics["acc_iii"] - cohort_metrics["acc_ii"])

    hard_fail = (rate < MB_RECOVERY_FLOOR) or (fb_f1 < HF_FULL_BENCH_MACRO_F1_FLOOR) \
        or (delta_iii_ii <= HF_PAIRSCRAMBLE_MAX_DELTA_VS_REAL)
    hard_pass = (not hard_fail) and (rate >= HP_RECOVERY) and (fb_f1 >= HP_FULL_BENCH_MACRO_F1) \
        and (delta_iii_i <= HP_PAIRSCRAMBLE_MAX_DELTA_VS_BASELINE)

    if hard_fail:
        verdict = "HARD_FAIL"
    elif hard_pass:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    msg = (f"cohort n={cohort_n} activation_fires_rate={cohort_metrics['activation_fires_rate']:.3f} "
           f"verdict_fires_rate={cohort_metrics['verdict_fires_rate']:.3f} "
           f"recovery={rate:.3f} ({rec['n_recovered']}/{rec['n_majority_wrong']}) "
           f"full_bench_n80_macro_f1={fb_f1:.4f} (doc=0.686 floor=0.620) "
           f"pairscramble: |iii-i|={delta_iii_i:.4f} (<=0.05 HP) |iii-ii|={delta_iii_ii:.4f} (<=0.03 HF-leak)")
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
    """MECHANISM-FIRES + STAGE-1-CONFOUND-IMMUNITY + real_code_path check. Constructs the REAL FHRR
    bind/unbind/bundle primitives (via utility_channel_trace, exercised inside
    self_test_utility_channel) at small hand-authored scale -- no synthetic-only branch, no DesireDB
    needed."""
    r_ga = ga_self_test()
    r_util = self_test_utility_channel()
    assert r_util["case3_stage1_immunity"]["verdict"] is not None
    assert r_util["relation_channel_abstained_case3"] is True

    # metrics helpers sanity
    gold = ["Fulfilled", "Fulfilled", "Unfulfilled", "Unfulfilled"]
    assert accuracy(gold, list(gold)) == 1.0
    assert macro_f1(gold, list(gold)) == 1.0
    assert accuracy(gold, ["Unfulfilled"] * 4) == 0.5

    # recovery_rate sanity: 2 majority-wrong items, 1 recovered
    rr = recovery_rate(["Unfulfilled", "Unfulfilled", "Fulfilled"], ["Unfulfilled", "Fulfilled", "Fulfilled"])
    assert rr == {"n_majority_wrong": 2, "n_recovered": 1, "rate": 0.5}, rr
    rr0 = recovery_rate(["Fulfilled", "Fulfilled"], ["Fulfilled", "Fulfilled"])
    assert rr0["rate"] is None

    # derangement sanity: no self-match
    fake_sample = [{"Desire-Expression-Sentence": f"d{i}"} for i in range(10)]
    scr = _scrambled_desires(fake_sample)
    for i in range(10):
        assert scr[i] != fake_sample[i]["Desire-Expression-Sentence"], "derangement self-matched"

    # arms-must-differ hash-test sanity
    same = _arms_must_differ({"i": ["A", "B"], "ii": ["A", "B"], "iii": ["A", "B"]})
    assert same["arms_differ"] is False
    diff = _arms_must_differ({"i": ["A", "B"], "ii": ["A", "C"], "iii": ["A", "B"]})
    assert diff["arms_differ"] is True

    return {"goal_achievement_self_test": r_ga, "utility_channel_self_test": r_util, "helpers_ok": True}


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
    n_per_class = SMOKE_N_PER_CLASS if args.smoke else FULL_N_PER_CLASS
    output_dir = OUTPUT_DIR + "_smoke" if args.smoke else OUTPUT_DIR
    expected_units = 3  # one per arm (i/ii/iii), cardinality_ok
    _write_start_marker(output_dir, run_mode, expected_units)
    t0 = time.time()

    print(f"[{run_mode}] loading DesireDB...", flush=True)
    rows = load_desiredb_rows()
    print(f"[{run_mode}] {len(rows)} binary-eligible rows loaded", flush=True)
    sample = balanced_subsample(rows, n_per_class, SEED)
    print(f"[{run_mode}] sample n={len(sample)} (n_per_class={n_per_class}, seed={SEED})", flush=True)

    cohort_idxs = build_cohort(sample)
    cohort_n = len(cohort_idxs)
    print(f"[{run_mode}] cohort(abstain-to-majority) n={cohort_n} of {len(sample)}", flush=True)

    arms = run_cohort_arms(sample, cohort_idxs)
    for idx, name in enumerate(("i", "ii", "iii")):
        record_unit(output_dir, unit_key(name), {"arm": name, "n": cohort_n})
        _write_heartbeat(output_dir, idx, expected_units, time.time() - t0)

    diff_check = _arms_must_differ(arms)
    activation_fires_rate = sum(arms["activation_fires"]) / cohort_n if cohort_n else 0.0
    verdict_fires_rate = sum(arms["verdict_fires"]) / cohort_n if cohort_n else 0.0
    print(f"[{run_mode}] activation_fires_rate={activation_fires_rate:.3f} (Stage-1-killer check -- "
          f"MUST be > 0, goal-side-only lookup) verdict_fires_rate={verdict_fires_rate:.3f} "
          f"(activation AND outcome-evidence both succeeded)", flush=True)

    acc_i = accuracy(arms["gold"], arms["i"])
    acc_ii = accuracy(arms["gold"], arms["ii"])
    acc_iii = accuracy(arms["gold"], arms["iii"])
    rec = recovery_rate(arms["gold"], arms["ii"])
    cohort_metrics = {"cohort_n": cohort_n,
                       "activation_fires_rate": round(activation_fires_rate, 4),
                       "n_activation_fired": sum(arms["activation_fires"]),
                       "verdict_fires_rate": round(verdict_fires_rate, 4),
                       "n_verdict_fired": sum(arms["verdict_fires"]),
                       "gold_dist": {"Fulfilled": arms["gold"].count("Fulfilled"),
                                     "Unfulfilled": arms["gold"].count("Unfulfilled")},
                       "acc_i": round(acc_i, 4), "acc_ii": round(acc_ii, 4), "acc_iii": round(acc_iii, 4),
                       "macro_f1_i": round(macro_f1(arms["gold"], arms["i"]), 4),
                       "macro_f1_ii": round(macro_f1(arms["gold"], arms["ii"]), 4),
                       "macro_f1_iii": round(macro_f1(arms["gold"], arms["iii"]), 4),
                       "recovery": rec}

    validity = harness_validity_check() if run_mode == "full" else None
    full_bench_80 = full_bench_composed(VALIDITY_N_PER_CLASS) if run_mode == "full" else None
    full_bench_160_context = full_bench_composed(FULL_N_PER_CLASS) if run_mode == "full" else None

    if run_mode == "smoke":
        # smoke does not gate a verdict band; it verifies the mechanism fires + cardinality + arms
        # differ, per the DISCRIMINATOR-MUST-SURVIVE-SCALE pre-flight discipline (same n=80 regime
        # as the harness_validity_check's own baseline scale, so this is a scale-realistic smoke,
        # not a toy-scale one).
        if cohort_n < MIN_COHORT_N:
            verdict, msg = "INVALID", f"SMOKE_UNDERPOWERED_COHORT: n={cohort_n} (need >={MIN_COHORT_N})"
        elif activation_fires_rate == 0.0:
            verdict, msg = "HARD_FAIL", "SMOKE_STAGE1_CONFOUND_REPEAT: activation_fires_rate=0.0 -- attribute-activation never fired on the cohort (would repeat Stage-1's structural confound)"
        else:
            verdict = "HARD_PASS"
            msg = (f"SMOKE_OK: cohort n={cohort_n} activation_fires_rate={activation_fires_rate:.3f} "
                   f"verdict_fires_rate={verdict_fires_rate:.3f} "
                   f"acc(i/ii/iii)=({acc_i:.3f}/{acc_ii:.3f}/{acc_iii:.3f}) "
                   f"recovery={rec['rate']} arms_differ={diff_check['arms_differ']}")
    else:
        verdict, msg = compute_verdict(cohort_metrics, full_bench_80, validity, cohort_n)

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": f"{verdict}: {msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "n_sample": len(sample), "n_per_class": n_per_class, "seed": SEED,
        "cohort_metrics": cohort_metrics,
        "arms_differ_verified": diff_check["arms_differ"], "arms_digests": diff_check["digests"],
        "harness_validity_check": validity,
        "full_bench_n80_composed": full_bench_80,
        "full_bench_n160_composed_context": full_bench_160_context,
        "cardinality_ok": len(load_units(output_dir)) == expected_units,
        "expected_n_units": expected_units,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "deterministic lexicon-vote + FHRR bind/bundle/cleanup over a fixed 6-role x "
                    "3-filler codebook, no decoded/noisy continuous signal from a swept capacity "
                    "regime",
        "deterministic_seeding": True,
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps({k: v for k, v in metrics.items() if k != "cohort_metrics"}, indent=2, default=str))
    print(json.dumps({"cohort_metrics": {k: v for k, v in cohort_metrics.items() if k not in ("fires", "active_counts")}}, indent=2, default=str))


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
