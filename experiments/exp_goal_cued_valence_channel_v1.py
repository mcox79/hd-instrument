# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (deterministic lexicon-vote + shallow-parse weighting, no decoded/noisy signal)
# - HP_SCOPE per-arm declaration (arm ii gates HARD_PASS/HARD_FAIL; i/iii are comparators only)
# - cardinality_ok: EXPECTED_N_UNITS=3 (one unit per arm, no seed/sweep axis)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (see prereg)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL CandidateGenerator (real_code_path); no synthetic-only branch
# See preregs/2026-08-09_goal_cued_valence_channel_v1.md for the full pre-registration.
"""exp_goal_cued_valence_channel_v1 -- 3-arm falsification test for the goal-CUED relevance-weighted
valence channel (hdlab.goal_achievement.goal_cued_valence_channel) vs the goal-BLIND uniform
valence_channel, on real DesireDB (Rahimtoroghi, Wu, Wang, Anand & Walker, SIGDIAL 2017).

Arms: (i) valence_channel [baseline], (ii) goal_cued_valence_channel [mechanism],
(iii) goal_cued_valence_channel with a SCRAMBLED goal cue [mandatory falsification control].
Subsets: (a) full, (b) mixed-polarity/relation-abstain, (c) single-clause/unambiguous.

DesireDB provenance: publicly hosted, unauthenticated, at
https://github.com/ra-elahe/DesireDB/blob/main/DesireDB.csv (raw content fetched + cached at
data/desiredb_cache/DesireDB.csv, gitignored, never committed -- see prereg "Data" section for the
byte-size verification against the GitHub tree API). outcome field = "Evidence" column,
desire field = "Desire-Expression-Sentence" column -- calibrated (see prereg) to reproduce
hdlab.goal_achievement.goal_achievement_verdict's own documented macro-F1 0.686/F1 0.706/acc 0.688
(within ~0.01-0.015, well under the ~0.05 SE band established for this benchmark at n=80).

Modes:
  --self-test  hand-authored cases, real CandidateGenerator at small scale, no DesireDB needed
  --smoke      DesireDB n=20 balanced (seed 20260808), all 3 arms, subset (a) only
  --full       DesireDB n=160 balanced (seed 20260808) for the 3-arm comparison + subsets (a)/(b)/(c);
               ALSO recomputes the n=80 harness_validity_check against goal_achievement_verdict.
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
import re
import sys
import time
import traceback
import urllib.request
from datetime import datetime, timezone

ANCHOR_NAME = "goal_cued_valence_channel_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

from hdlab.goal_achievement import (  # noqa: E402
    valence_channel, goal_cued_valence_channel, relation_channel, goal_achievement_verdict,
    MAJORITY_CLASS,
)

DESIREDB_RAW_URL = "https://raw.githubusercontent.com/ra-elahe/DesireDB/main/DesireDB.csv"
DESIREDB_CACHE = os.path.join(REPO_ROOT, "data", "desiredb_cache", "DesireDB.csv")
SEED = 20260808
FULL_N_PER_CLASS = 80   # n=160 total (see prereg "Sample size" -- widened from the n=80 starting
                         # point to power subsets (b)/(c); harness_validity_check separately uses
                         # n_per_class=40 for exact comparability with the documented n=80 number)
SMOKE_N_PER_CLASS = 40  # n=80 total -- DISCRIMINATOR-MUST-SURVIVE-SCALE: n=20 (10/class) landed only
                         # 2 subset(b) items (too few to exercise the mechanism's differentiator,
                         # which only diverges from uniform valence_channel when an outcome has
                         # >=2 valence tokens at differing clause-proximity to the goal cue -- exactly
                         # subset (b)'s definition); n=80 gives subset(b)/(c) real headroom to fire.
VALIDITY_N_PER_CLASS = 40  # n=80, matches the documented benchmark exactly

HP_DELTA_VS_I = 0.10
HP_DELTA_VS_III = 0.07
HP_SUBSET_C_MAX_REGRESSION = 0.02
HF_DELTA_VS_I = 0.03
HF_SUBSET_C_MAX_REGRESSION = 0.05
VALIDITY_TOLERANCE = 0.03
MIN_SUBSET_N = 15

csv.field_size_limit(10_000_000)


# ============================================================================ DesireDB loader
def _fetch_desiredb() -> str:
    """Return path to a local DesireDB.csv, downloading + caching from the public GitHub raw URL if
    not already cached. Raises (no silent fallback) if both the cache and the fetch fail."""
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
    sample = rng.sample(pos, n_per_class) + rng.sample(neg, n_per_class)
    return sample


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


def binary_f1(gold, pred, pos="Fulfilled") -> float:
    tp = sum(1 for g, p in zip(gold, pred) if g == pos and p == pos)
    fp = sum(1 for g, p in zip(gold, pred) if g != pos and p == pos)
    fn = sum(1 for g, p in zip(gold, pred) if g == pos and p != pos)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    return 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0


def accuracy(gold, pred) -> float:
    return sum(1 for g, p in zip(gold, pred) if g == p) / len(gold)


def score_subset(gold, pred) -> dict:
    return {"n": len(gold), "acc": round(accuracy(gold, pred), 4),
            "macro_f1": round(macro_f1(gold, pred), 4), "f1": round(binary_f1(gold, pred), 4)}


# ============================================================================ valence-count probe
# (subset (b)/(c) population classification only -- NOT part of the mechanism under test; mirrors
# valence_channel's own opinion_lexicon/wordnet_polarity_propagation detection but returns counts.)
def _valence_counts(outcome: str):
    from hdlab import goal_typing as _gt
    from hdlab import wordnet_polarity_propagation as _wpp
    from hdlab.goal_achievement import _opinion, _AUX_STOP
    pos, neg = _opinion()
    toks = _gt._tokens(outcome)
    npos = nneg = 0
    for idx, tok in enumerate(toks):
        w = tok.lower()
        if not w.isalpha() or len(w) < 2 or w in _AUX_STOP:
            continue
        lem = _gt.lemma_verb(w)
        val = "POS" if (w in pos or lem in pos) else ("NEG" if (w in neg or lem in neg) else None)
        if val is None:
            val = _wpp.dictionary_lookup(lem).polarity
        if val and _gt._verb_negated_before(toks, idx):
            val = "NEG" if val == "POS" else "POS"
        if val == "POS":
            npos += 1
        elif val == "NEG":
            nneg += 1
    return npos, nneg


def classify_subsets(sample: list) -> dict:
    """Returns {idx: {"b": bool, "c": bool}} per-item subset membership."""
    out = {}
    for i, r in enumerate(sample):
        desire, outcome = r["Desire-Expression-Sentence"], r["Evidence"]
        rel, reason = relation_channel(desire, outcome)
        npos, nneg = _valence_counts(outcome)
        in_b = (reason in ("abstain", "no_goal")) and npos >= 1 and nneg >= 1
        in_c = (npos + nneg) <= 1
        out[i] = {"b": in_b, "c": in_c}
    return out


# ============================================================================ arms
def _scrambled_desires(sample: list) -> list:
    """Deterministic derangement: item i's scrambled cue source = item (i + n//2) % n (full offset,
    no self-match for n>1). Not hash()-derived (PROT-023 compliant)."""
    n = len(sample)
    off = max(1, n // 2)
    return [sample[(i + off) % n]["Desire-Expression-Sentence"] for i in range(n)]


def run_arms(sample: list) -> dict:
    gold = [r["Fulfillment-Label"] for r in sample]
    scrambled_cues = _scrambled_desires(sample)
    pred_i, pred_ii, pred_iii = [], [], []
    for i, r in enumerate(sample):
        desire, outcome = r["Desire-Expression-Sentence"], r["Evidence"]
        vi = valence_channel(outcome)
        vii = goal_cued_valence_channel(desire, outcome)
        viii = goal_cued_valence_channel(desire, outcome, goal_cue_desire=scrambled_cues[i])
        pred_i.append(vi if vi is not None else MAJORITY_CLASS)
        pred_ii.append(vii if vii is not None else MAJORITY_CLASS)
        pred_iii.append(viii if viii is not None else MAJORITY_CLASS)
    return {"gold": gold, "i": pred_i, "ii": pred_ii, "iii": pred_iii}


def _arms_must_differ(preds: dict) -> dict:
    """META_RULE_AF: hash-check the 3 arms' prediction vectors are not all bit-identical."""
    digests = {name: hashlib.sha256(json.dumps(preds[name]).encode()).hexdigest()
               for name in ("i", "ii", "iii")}
    all_same = len(set(digests.values())) == 1
    return {"digests": digests, "arms_differ": not all_same}


# ============================================================================ verdict logic
def compute_verdict(subset_metrics: dict) -> tuple:
    """subset_metrics: {"a": {arm: metrics}, "b": {...}, "c": {...}}. Returns (verdict, msg)."""
    b = subset_metrics.get("b")
    c = subset_metrics.get("c")
    if b is None or c is None:
        return "INVALID", "missing subset b/c metrics"
    # NOTE: underpowered-subset (n < MIN_SUBSET_N) check happens in the caller BEFORE this fn runs.
    delta_ii_i = b["ii"]["macro_f1"] - b["i"]["macro_f1"]
    delta_ii_iii = b["ii"]["macro_f1"] - b["iii"]["macro_f1"]
    c_regression = c["i"]["macro_f1"] - c["ii"]["macro_f1"]
    hard_pass = (delta_ii_i >= HP_DELTA_VS_I and delta_ii_iii >= HP_DELTA_VS_III
                 and c_regression <= HP_SUBSET_C_MAX_REGRESSION)
    hard_fail = (abs(delta_ii_i) < HF_DELTA_VS_I) or (c_regression > HF_SUBSET_C_MAX_REGRESSION)
    ii_beats_iii = delta_ii_iii > 0
    if hard_pass:
        verdict = "HARD_PASS"
    elif hard_fail:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"
    msg = (f"subset(b) n={b['i']['n']}: delta(ii-i)={delta_ii_i:+.4f} "
           f"delta(ii-iii)={delta_ii_iii:+.4f} ii_beats_iii={ii_beats_iii} "
           f"subset(c) n={c['i']['n']}: c_regression(i-ii)={c_regression:+.4f}")
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


# ============================================================================ harness validity check
def harness_validity_check() -> dict:
    """Re-verify (at every --full run) that the loader+field-mapping+seed construction reproduces
    goal_achievement_verdict's documented macro-F1 0.686/F1 0.706/acc 0.688 (n=80, seed 20260808),
    using the UNCHANGED 3-channel pipeline (not this cell's new arms). INVALID gate if delta > 0.03."""
    rows = load_desiredb_rows()
    sample = balanced_subsample(rows, VALIDITY_N_PER_CLASS, SEED)
    gold = [r["Fulfillment-Label"] for r in sample]
    pred = [goal_achievement_verdict(r["Desire-Expression-Sentence"], r["Evidence"])["verdict"]
            for r in sample]
    m = score_subset(gold, pred)
    documented = {"macro_f1": 0.686, "f1": 0.706, "acc": 0.688}
    delta_macro_f1 = m["macro_f1"] - documented["macro_f1"]
    return {"n": m["n"], "measured": m, "documented": documented,
            "delta_macro_f1": round(delta_macro_f1, 4),
            "valid": abs(delta_macro_f1) <= VALIDITY_TOLERANCE,
            "tolerance": VALIDITY_TOLERANCE}


# ============================================================================ self-test
def self_test() -> dict:
    """MECHANISM-FIRES + real_code_path check. Constructs the REAL CandidateGenerator (via
    goal_cued_valence_channel, which lazy-loads it) at small hand-authored scale -- no synthetic-only
    branch, no DesireDB needed."""
    from hdlab.goal_achievement import self_test as ga_self_test, self_test_goal_cued
    r1 = ga_self_test()
    r2 = self_test_goal_cued()
    assert r2["cued_corrected"] == "Fulfilled" and r2["uniform_dragged"] == "Unfulfilled"

    # metrics helpers sanity
    gold = ["Fulfilled", "Fulfilled", "Unfulfilled", "Unfulfilled"]
    pred_perfect = list(gold)
    pred_worst = ["Unfulfilled", "Unfulfilled", "Fulfilled", "Fulfilled"]
    assert accuracy(gold, pred_perfect) == 1.0
    assert accuracy(gold, pred_worst) == 0.0
    assert macro_f1(gold, pred_perfect) == 1.0
    assert macro_f1(gold, pred_worst) == 0.0

    # derangement sanity: no self-match
    fake_sample = [{"Desire-Expression-Sentence": f"d{i}"} for i in range(10)]
    scr = _scrambled_desires(fake_sample)
    for i in range(10):
        assert scr[i] != fake_sample[i]["Desire-Expression-Sentence"], "derangement self-matched"

    # arms-must-differ hash-test sanity (identical vs different)
    same = _arms_must_differ({"i": ["A", "B"], "ii": ["A", "B"], "iii": ["A", "B"]})
    assert same["arms_differ"] is False
    diff = _arms_must_differ({"i": ["A", "B"], "ii": ["A", "C"], "iii": ["A", "B"]})
    assert diff["arms_differ"] is True

    return {"goal_achievement_self_test": r1, "goal_cued_self_test": r2, "helpers_ok": True}


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

    subset_membership = classify_subsets(sample)
    n_b = sum(1 for v in subset_membership.values() if v["b"])
    n_c = sum(1 for v in subset_membership.values() if v["c"])
    print(f"[{run_mode}] subset(b)={n_b} subset(c)={n_c} of n={len(sample)}", flush=True)

    preds = run_arms(sample)
    for idx in range(3):
        record_unit(output_dir, unit_key(("i", "ii", "iii")[idx]),
                    {"arm": ("i", "ii", "iii")[idx], "n": len(sample)})
        _write_heartbeat(output_dir, idx, expected_units, time.time() - t0)

    diff_check = _arms_must_differ(preds)

    def _sub_gold_pred(mask_fn):
        idxs = [i for i in range(len(sample)) if mask_fn(subset_membership[i])]
        return idxs, [preds["gold"][i] for i in idxs]

    subset_metrics = {}
    idxs_a = list(range(len(sample)))
    subset_metrics["a"] = {arm: score_subset(preds["gold"], preds[arm]) for arm in ("i", "ii", "iii")}
    idxs_b, gold_b = _sub_gold_pred(lambda v: v["b"])
    subset_metrics["b"] = {arm: score_subset(gold_b, [preds[arm][i] for i in idxs_b])
                            for arm in ("i", "ii", "iii")}
    idxs_c, gold_c = _sub_gold_pred(lambda v: v["c"])
    subset_metrics["c"] = {arm: score_subset(gold_c, [preds[arm][i] for i in idxs_c])
                            for arm in ("i", "ii", "iii")}

    underpowered = (len(idxs_b) < MIN_SUBSET_N) or (len(idxs_c) < MIN_SUBSET_N)

    validity = harness_validity_check() if run_mode == "full" else None

    if underpowered:
        verdict, msg = "INVALID", f"UNDERPOWERED_SUBSET: subset(b) n={len(idxs_b)} subset(c) n={len(idxs_c)} (need >={MIN_SUBSET_N} each)"
    elif validity is not None and not validity["valid"]:
        verdict, msg = "INVALID", f"harness_validity_check FAILED: delta_macro_f1={validity['delta_macro_f1']} exceeds tolerance {VALIDITY_TOLERANCE}"
    else:
        verdict, msg = compute_verdict(subset_metrics)

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": msg,
        "summary": f"{verdict}: {msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "n_sample": len(sample), "n_per_class": n_per_class, "seed": SEED,
        "subset_sizes": {"a": len(sample), "b": len(idxs_b), "c": len(idxs_c)},
        "subset_metrics": subset_metrics,
        "arms_differ_verified": diff_check["arms_differ"],
        "arms_digests": diff_check["digests"],
        "harness_validity_check": validity,
        "cardinality_ok": len(load_units(output_dir)) == expected_units,
        "expected_n_units": expected_units,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "deterministic lexicon-vote + shallow-parse weighting, no decoded/noisy signal",
        "deterministic_seeding": True,
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps({k: v for k, v in metrics.items() if k not in ("subset_metrics",)}, indent=2, default=str))
    print(json.dumps({"subset_metrics": subset_metrics}, indent=2, default=str))


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
