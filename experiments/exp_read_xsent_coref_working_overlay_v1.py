#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
exp_read_xsent_coref_working_overlay_v1

MULTI-SENTENCE PHASE, STEP 1 -- the situation model's ENTITY / REFERENCE BACKBONE.

QUESTION: does wiring the VALIDATED symbolic WorkingOverlay (hdlab.state_of_mind)
into a PER-SENTENCE reader pass -- so tracked entities PERSIST across sentence
boundaries -- let it resolve CROSS-SENTENCE pronouns (antecedent in a PRIOR
sentence) that a SINGLE-SENTENCE baseline (entity memory reset every sentence)
PROVABLY CANNOT? Glass-box, NO runtime LLM.

THE DISCRIMINATOR (session's lesson applied): evaluate on the CROSS-SENTENCE
subset -- pronouns whose gold nearest antecedent is in a PRIOR sentence -- the
multi-sentence analog of the passive hard-syntax discriminator (naive=0 there).
A single-sentence baseline is STRUCTURALLY blind to prior-sentence antecedents,
so on this subset it can only abstain or pick a wrong within-sentence distractor.

VALIDITY GATE (crucial): the single-sentence baseline MUST score LOW on the
cross-sentence subset. If it scores high, those cases do not actually require
cross-sentence state -> not a valid discriminator. (By construction of the subset
-- nearest antecedent in a prior sentence => no same-cluster mention earlier in
the current sentence -- the baseline is ~0; the gate asserts subset well-formedness.)

CORPUS: LitBank coref gold (data/corpora/litbank_coref_conll/*.conll; dbamman/
litbank, CC-BY 4.0). Gold mention BOUNDARIES used (standard gold-mention setting);
the resolver NEVER sees gold coref LINKING -- gold clusters ONLY (a) stratify
targets by SENTENCE distance and (b) score correctness. Held-out: WorkingOverlay
was NOT tuned on these chains (validated constants ported verbatim from longdist
49bb99c24). NOT UD-EWT (zero cross-sentence gold there).

ARMS (primary variable = cross-sentence entity memory vs single-sentence reset):
  single_sentence_baseline  reset overlay at every sentence boundary; resolve
                            within-sentence entities only (strategy=maintained).
                            = the P2 ablation of cross-sentence memory.
  xsent_recency             persistent overlay, strategy=recency (nearest
                            compatible; brain: recency owns SHORT distance).
  xsent_maintained          PRIMARY MECHANISM: persistent overlay, strategy=
                            maintained (salience = freq + recency tie-break).
  xsent_freq                persistent overlay, strategy=freq (pure frequency;
                            the honest LONG-distance lever per longdist VET note).

PRIMARY DISCRIMINATOR: delta_xsent = acc[xsent_maintained] - acc[single_sentence
_baseline] on the cross-sentence subset (sent_dist >= 1). Per-distance breakdown
(same / +1 / +2 / long) reported for ALL arms -> which strategy wins at which
distance (honest; longdist VET: freq beats maintained at long distance).

BANDS (pre-registered; discriminator = cross-sentence subset):
  HARD_PASS: validity_gate_ok (baseline_xsent_acc <= 0.10)
             AND xsent_maintained_acc_xsent >= 0.30
             AND delta_xsent >= 0.15
             AND p1_no_regression (same-bucket: xsent_maintained_acc >=
                 single_sentence_baseline_acc - 0.05)
             AND bootstrap sign_stability(delta_xsent > 0) >= 0.90.
  HARD_FAIL: NOT validity_gate_ok (baseline high on cross-sentence subset =>
             invalid discriminator; redirect) OR xsent_maintained_acc_xsent <=
             baseline_xsent_acc (cross-sentence memory gives NO lift -> overlay
             cannot reach prior-sentence antecedents; genuine wall -> autopsy).
  MIDDLE_BAND: lift positive but below 0.30/0.15 bars, or default strategy
             (maintained) beaten by another xsent strategy, or stability short.

NEVER-CONFIDENTLY-WRONG: a target with no compatible entity ABSTAINS (attempted
=False); precision (acc-on-attempted) reported alongside accuracy.

Header numbers are DESIGN targets (HYPOTHESIZED@this file); reported numbers are
MEASURED@ the metrics.json this run writes.

CELL-TEMPLATE MANDATORY:
# - arms_differ_verified at smoke gate (META_RULE_AF; hash per-target resolved cluster)
# - final_metrics_atomicity: tmp_replace (single-shot; metrics.json.tmp + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: symbolic accuracy metric; no matmul noise floor. Reachability shown
#   empirically: baseline ~0 on cross-sentence subset (validity gate) leaves full
#   headroom; xsent accuracy is telemetry-sensitive (strategy + distance move it).
# - baseline_in_band: the DISCRIMINATOR baseline (single-sentence on cross-sentence
#   subset) is ~0 BY VALIDITY-GATE DESIGN (analog of naive=0 on hard syntax); the
#   MECHANISM arm (xsent_maintained) is the in-band arm; the within-sentence baseline
#   ("same" bucket) is the P1 no-regression control.
# - discriminator survives scale: full=all 25 cached books; smoke=first 5, asserts
#   cross-sentence subset non-empty AND delta measurable AND validity gate holds.
# - HARD_PASS strictly above the wall by real margin (META_RULE_L): >=0.30 abs +
#   >=0.15 delta, not an at-floor clear.
# - cardinality: EXPECTED_N_UNITS = n_books usable; verdict counts per-book coverage.
# - per-unit failure-class instrumentation; no bare except.
# - calibration_check: default_ok_for_this_regime (validated overlay constants
#   ported verbatim; no tuned-for-PASS knob).
# - all header numbers tagged HYPOTHESIZED@; reported numbers MEASURED@.
# - real_code_path: self-test builds a real temp conll, runs hdlab.coref parse +
#   build_pronoun_targets + CorefReader (both reset modes) end-to-end.
# - progress_logging: print_flush_true.
"""

import argparse
import glob
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

# repo-root on path so hdlab imports resolve under the runner
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.coref import (  # noqa: E402
    BUCKETS,
    CorefReader,
    build_pronoun_targets,
    parse_litbank_conll,
)

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------
ANCHOR_NAME = "read_xsent_coref_working_overlay_v1"
CORPUS_DIR = os.path.join(REPO_ROOT, "data", "corpora", "litbank_coref_conll")
SMOKE_N = 5

# Arms: (name, reset_per_sentence, strategy)
ARMS = [
    ("single_sentence_baseline", True, "maintained"),
    ("xsent_recency", False, "recency"),
    ("xsent_maintained", False, "maintained"),
    ("xsent_freq", False, "freq"),
]
BASELINE_ARM = "single_sentence_baseline"
MECHANISM_ARM = "xsent_maintained"
XSENT_ARMS = ["xsent_recency", "xsent_maintained", "xsent_freq"]

# Bands
VALIDITY_GATE_MAX = 0.10     # baseline acc on cross-sentence subset must be <= this
HP_ABS = 0.30                # xsent_maintained acc on cross-sentence subset
HP_DELTA = 0.15              # delta over baseline
HP_SIGN_STABILITY = 0.90
P1_REGRESSION_EPS = 0.05     # same-bucket: xsent >= baseline - eps

N_BOOTSTRAP = 500
BOOTSTRAP_SEED = 20260724


def _p(msg):
    print(msg, flush=True)


# ----------------------------------------------------------------------------
# corpus
# ----------------------------------------------------------------------------
def list_books(run_mode):
    paths = sorted(glob.glob(os.path.join(CORPUS_DIR, "*.conll")))
    usable = [p for p in paths if os.path.getsize(p) > 1000]
    if run_mode == "smoke":
        usable = usable[:SMOKE_N]
    return usable


# ----------------------------------------------------------------------------
# evaluation
# ----------------------------------------------------------------------------
def evaluate_book(path, reader):
    """Run all arms on one book. Returns per-target records keyed by arm."""
    mentions, n_sentences = parse_litbank_conll(path)
    targets = build_pronoun_targets(mentions)
    if not targets:
        return [], {"n_mentions": len(mentions), "n_sentences": n_sentences,
                    "n_targets": 0}
    per_arm_records = {}
    for arm_name, reset, strat in ARMS:
        recs = reader.resolve_stream(mentions, targets,
                                     reset_per_sentence=reset, strategy=strat)
        per_arm_records[arm_name] = recs
    # zip into per-target unified records (same target order across arms)
    n = len(targets)
    unified = []
    for i in range(n):
        base_rec = per_arm_records[ARMS[0][0]][i]
        u = {"sent_dist": base_rec["sent_dist"], "bucket": base_rec["bucket"],
             "gold_cluster": base_rec["gold_cluster"], "correct": {}, "attempted": {},
             "resolved_cluster": {}}
        for arm_name, _r, _s in ARMS:
            r = per_arm_records[arm_name][i]
            u["correct"][arm_name] = r["correct"]
            u["attempted"][arm_name] = r["attempted"]
            u["resolved_cluster"][arm_name] = (-1 if r["resolved_cluster"] is None
                                               else r["resolved_cluster"])
        unified.append(u)
    meta = {"n_mentions": len(mentions), "n_sentences": n_sentences,
            "n_targets": n}
    return unified, meta


def acc_on(records, arm):
    if not records:
        return None
    return sum(r["correct"][arm] for r in records) / len(records)


def prec_on(records, arm):
    att = [r for r in records if r["attempted"][arm]]
    if not att:
        return None
    return sum(r["correct"][arm] for r in att) / len(att)


def attrate_on(records, arm):
    if not records:
        return None
    return sum(r["attempted"][arm] for r in records) / len(records)


def bucketize(records):
    out = {b: [] for b in BUCKETS}
    for r in records:
        out[r["bucket"]].append(r)
    return out


def bootstrap_sign_stability(xsent_records, arm_mech, arm_base,
                             n_boot=N_BOOTSTRAP, seed=BOOTSTRAP_SEED):
    """Fraction of resamples with acc[mech] - acc[base] > 0 on the cross-sentence
    subset. Deterministic (fixed integer seed)."""
    if len(xsent_records) < 2:
        return None
    rng = np.random.default_rng(seed)
    mech = np.array([r["correct"][arm_mech] for r in xsent_records], dtype=float)
    base = np.array([r["correct"][arm_base] for r in xsent_records], dtype=float)
    n = len(xsent_records)
    pos = 0
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        if mech[idx].mean() - base[idx].mean() > 0:
            pos += 1
    return pos / n_boot


def arms_must_differ(all_records):
    """Hash each arm's per-target resolved-cluster vector; baseline != mechanism."""
    digests = {}
    for arm_name, _r, _s in ARMS:
        vec = bytes()
        for r in all_records:
            vec += int(r["resolved_cluster"][arm_name]).to_bytes(4, "big", signed=True)
        digests[arm_name] = hashlib.sha256(vec).hexdigest()
    assert digests[BASELINE_ARM] != digests[MECHANISM_ARM], (
        "META_RULE_AF VIOLATION: %s and %s produced bit-identical resolved clusters"
        % (BASELINE_ARM, MECHANISM_ARM))
    return digests


# ----------------------------------------------------------------------------
# RUN
# ----------------------------------------------------------------------------
def run(run_mode):
    t0 = time.perf_counter()
    out_dir = os.path.join(REPO_ROOT, "data",
                           "exp_%s%s" % (ANCHOR_NAME, "_smoke" if run_mode == "smoke" else ""))
    os.makedirs(out_dir, exist_ok=True)
    _write_start_marker(out_dir, run_mode, 0)

    books = list_books(run_mode)
    if len(books) < 2:
        raise RuntimeError("CORPUS_UNAVAILABLE: only %d books in %s" % (len(books), CORPUS_DIR))

    reader = CorefReader()
    all_records = []
    per_book = {}
    book_failures = []
    for path in books:
        b = os.path.basename(path)
        try:
            recs, meta = evaluate_book(path, reader)
            per_book[b] = meta
            for r in recs:
                r["book"] = b
            all_records.extend(recs)
            _p("[book] %-52s targets=%d sents=%d" % (b[:52], meta["n_targets"], meta["n_sentences"]))
        except Exception as e:  # noqa: BLE001 -- per-book failure-class recorded, not silent
            book_failures.append({"book": b, "failure_class": type(e).__name__,
                                  "msg": str(e)[:160]})
            _p("[book-FAIL] %s : %s: %s" % (b, type(e).__name__, str(e)[:120]))

    if not all_records:
        raise RuntimeError("NO_TARGETS: parsed %d books, 0 pronoun targets" % len(books))

    digests = arms_must_differ(all_records)

    # bucket + subset aggregates
    by_bucket = bucketize(all_records)
    xsent_records = by_bucket["plus1"] + by_bucket["plus2"] + by_bucket["long"]
    same_records = by_bucket["same"]

    def arm_table(records):
        return {arm_name: {"acc": acc_on(records, arm_name),
                           "prec": prec_on(records, arm_name),
                           "attempt_rate": attrate_on(records, arm_name),
                           "n": len(records)}
                for arm_name, _r, _s in ARMS}

    per_bucket_table = {b: arm_table(by_bucket[b]) for b in BUCKETS}
    xsent_table = arm_table(xsent_records)
    same_table = arm_table(same_records)
    overall_table = arm_table(all_records)

    baseline_xsent_acc = xsent_table[BASELINE_ARM]["acc"]
    mech_xsent_acc = xsent_table[MECHANISM_ARM]["acc"]
    delta_xsent = (None if (mech_xsent_acc is None or baseline_xsent_acc is None)
                   else mech_xsent_acc - baseline_xsent_acc)

    # honest per-distance winner among xsent strategies
    per_distance_winner = {}
    for b in BUCKETS:
        tab = per_bucket_table[b]
        best_arm, best_acc = None, -1.0
        for arm in XSENT_ARMS:
            a = tab[arm]["acc"]
            if a is not None and a > best_acc:
                best_acc = a
                best_arm = arm
        per_distance_winner[b] = {"arm": best_arm, "acc": (None if best_arm is None else best_acc)}

    # best xsent strategy on the whole cross-sentence subset (reported, not gated)
    best_xsent_arm, best_xsent_acc = None, -1.0
    for arm in XSENT_ARMS:
        a = xsent_table[arm]["acc"]
        if a is not None and a > best_xsent_acc:
            best_xsent_acc = a
            best_xsent_arm = arm

    sign_stability = bootstrap_sign_stability(xsent_records, MECHANISM_ARM, BASELINE_ARM)

    # P1 no-regression on the within-sentence ("same") bucket
    base_same = same_table[BASELINE_ARM]["acc"]
    mech_same = same_table[MECHANISM_ARM]["acc"]
    p1_ok = (base_same is not None and mech_same is not None
             and mech_same >= base_same - P1_REGRESSION_EPS)

    validity_gate_ok = (baseline_xsent_acc is not None
                        and baseline_xsent_acc <= VALIDITY_GATE_MAX)

    # verdict
    n_xsent = len(xsent_records)
    if delta_xsent is None or n_xsent < 5:
        verdict = "UNKNOWN"
        verdict_msg = "cross-sentence subset too small (n_xsent=%d) to decide" % n_xsent
    elif not validity_gate_ok:
        verdict = "HARD_FAIL"
        verdict_msg = ("VALIDITY GATE FAILED: single-sentence baseline acc=%.4f > %.2f on the "
                       "cross-sentence subset => cases do not require cross-sentence state; "
                       "invalid discriminator (redirect)." % (baseline_xsent_acc, VALIDITY_GATE_MAX))
    elif mech_xsent_acc <= baseline_xsent_acc:
        verdict = "HARD_FAIL"
        verdict_msg = ("cross-sentence memory gives NO lift: xsent_maintained acc=%.4f <= baseline "
                       "acc=%.4f on cross-sentence subset (overlay cannot reach prior-sentence "
                       "antecedents). best xsent strategy=%s acc=%s." %
                       (mech_xsent_acc, baseline_xsent_acc, best_xsent_arm,
                        _f(best_xsent_acc if best_xsent_arm else None)))
    elif (mech_xsent_acc >= HP_ABS and delta_xsent >= HP_DELTA and p1_ok
          and sign_stability is not None and sign_stability >= HP_SIGN_STABILITY):
        verdict = "HARD_PASS"
        verdict_msg = ("cross-sentence WorkingOverlay resolves prior-sentence pronouns: "
                       "xsent_maintained acc=%.4f (baseline=%.4f, delta=%.4f), validity_gate=OK "
                       "(baseline_xsent=%.4f<=%.2f), P1_no_regression=OK (same: mech=%.4f vs "
                       "base=%.4f), sign_stability=%.3f, n_xsent=%d." %
                       (mech_xsent_acc, baseline_xsent_acc, delta_xsent, baseline_xsent_acc,
                        VALIDITY_GATE_MAX, mech_same, base_same, sign_stability, n_xsent))
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = ("cross-sentence memory helps but sub-threshold: xsent_maintained acc=%.4f "
                       "(baseline=%.4f, delta=%.4f), best xsent=%s acc=%s, p1_ok=%s, "
                       "sign_stability=%s, n_xsent=%d." %
                       (mech_xsent_acc, baseline_xsent_acc, delta_xsent, best_xsent_arm,
                        _f(best_xsent_acc if best_xsent_arm else None), p1_ok,
                        _f(sign_stability), n_xsent))

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": "%s: %s" % (ANCHOR_NAME, verdict),
        "elapsed_s": round(elapsed, 3),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "host": platform.node(),
        "corpus": {"source": "LitBank coref (dbamman/litbank), CC-BY 4.0",
                   "corpus_dir": CORPUS_DIR, "n_books_usable": len(books),
                   "books": [os.path.basename(p) for p in books]},
        "config": {"arms": [a[0] for a in ARMS], "baseline_arm": BASELINE_ARM,
                   "mechanism_arm": MECHANISM_ARM, "xsent_arms": XSENT_ARMS,
                   "validity_gate_max": VALIDITY_GATE_MAX, "hp_abs": HP_ABS,
                   "hp_delta": HP_DELTA, "hp_sign_stability": HP_SIGN_STABILITY,
                   "p1_regression_eps": P1_REGRESSION_EPS,
                   "n_bootstrap": N_BOOTSTRAP, "bootstrap_seed": BOOTSTRAP_SEED},
        "n_targets_total": len(all_records),
        "n_xsent": n_xsent, "n_same": len(same_records),
        "bucket_counts": {b: len(by_bucket[b]) for b in BUCKETS},
        "cross_sentence_subset_table": xsent_table,
        "within_sentence_same_table": same_table,
        "overall_table": overall_table,
        "per_bucket_table": per_bucket_table,
        "per_distance_winner": per_distance_winner,
        "baseline_xsent_acc": baseline_xsent_acc,
        "mech_xsent_acc": mech_xsent_acc,
        "delta_xsent": delta_xsent,
        "best_xsent_arm": best_xsent_arm,
        "best_xsent_acc": (None if best_xsent_arm is None else best_xsent_acc),
        "validity_gate_ok": validity_gate_ok,
        "p1_no_regression_ok": p1_ok,
        "bootstrap_sign_stability": sign_stability,
        "arms_differ_digests": digests,
        "arms_differ_verified": True,
        "per_book": per_book,
        "book_failures": book_failures,
        "expected_n_units": len(books),
        "cardinality_ok": (len(per_book) == len(books) - len(book_failures)),
    }
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    return metrics, out_dir


def _write_start_marker(out_dir, run_mode, expected_n):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n, "host": platform.node()}
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    final = os.path.join(out_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(out_dir, exc):
    os.makedirs(out_dir, exist_ok=True)
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__,
            "elapsed_s": 0.0, "anchor_name": ANCHOR_NAME,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat()}
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _f(x):
    return "None" if x is None else ("%.4f" % x)


# ----------------------------------------------------------------------------
# SELF-TEST (real code path: temp conll -> hdlab.coref parse + targets + reader)
# ----------------------------------------------------------------------------
def self_test():
    import tempfile

    # Build a tiny 3-sentence conll:
    #  S0: The woman(1,fem) met a man(2,masc) .
    #  S1: She(1) left .                     -> CROSS-SENTENCE (sent_dist=1); baseline
    #                                           resets at S1 -> no entity -> abstain/wrong;
    #                                           xsent: she(fem) compat only with woman(1)
    #                                           -> resolves woman(1) -> CORRECT.
    #  S2: A girl(3,fem) saw her(3) .        -> WITHIN-SENTENCE (sent_dist=0); baseline
    #                                           sees girl in S2 -> correct (P1 control).
    def tok(tidx, word, coref="_"):
        return "selftest\t0\t%d\t%s\t_\t_\t_\t_\t_\t_\t_\t_\t%s" % (tidx, word, coref)

    lines = ["#begin document (selftest); part 0"]
    # S0
    lines += [tok(0, "The"), tok(1, "woman", "(1)"), tok(2, "met"),
              tok(3, "a"), tok(4, "man", "(2)"), tok(5, "."), ""]
    # S1
    lines += [tok(0, "She", "(1)"), tok(1, "left"), tok(2, "."), ""]
    # S2
    lines += [tok(0, "A"), tok(1, "girl", "(3)"), tok(2, "saw"),
              tok(3, "her", "(3)"), tok(4, "."), ""]

    with tempfile.NamedTemporaryFile("w", suffix=".conll", delete=False,
                                     encoding="utf-8") as tf:
        tf.write("\n".join(lines) + "\n")
        tmp_path = tf.name
    try:
        mentions, n_sent = parse_litbank_conll(tmp_path)
        assert n_sent == 3, "expected 3 sentences, got %d" % n_sent
        heads = [m["head"] for m in mentions]
        assert heads.count("woman") == 1 and "man" in heads and "she" in heads \
            and "girl" in heads and "her" in heads, "parse: missing expected heads %s" % heads
        # sentence indexing
        she = [m for m in mentions if m["head"] == "she"][0]
        her = [m for m in mentions if m["head"] == "her"][0]
        assert she["sent_idx"] == 1, "she must be in sentence 1, got %d" % she["sent_idx"]
        assert her["sent_idx"] == 2, "her must be in sentence 2, got %d" % her["sent_idx"]

        targets = build_pronoun_targets(mentions)
        by_head = {t["target"]["head"]: t for t in targets}
        assert set(by_head) == {"she", "her"}, "expected targets she,her got %s" % set(by_head)
        assert by_head["she"]["sent_dist"] == 1, \
            "she must be cross-sentence sent_dist=1, got %d" % by_head["she"]["sent_dist"]
        assert by_head["her"]["sent_dist"] == 0, \
            "her must be within-sentence sent_dist=0, got %d" % by_head["her"]["sent_dist"]

        reader = CorefReader()
        # baseline (reset per sentence)
        base_recs = reader.resolve_stream(mentions, targets, reset_per_sentence=True,
                                          strategy="maintained")
        base_by_midx = {r["target_midx"]: r for r in base_recs}
        # xsent maintained
        xs_recs = reader.resolve_stream(mentions, targets, reset_per_sentence=False,
                                        strategy="maintained")
        xs_by_midx = {r["target_midx"]: r for r in xs_recs}

        she_midx = she["midx"]
        her_midx = her["midx"]

        # CROSS-SENTENCE 'she': baseline blind (abstain or wrong), xsent correct
        assert base_by_midx[she_midx]["correct"] is False, \
            "baseline must FAIL cross-sentence 'she' (resolved=%s)" % base_by_midx[she_midx]["resolved_cluster"]
        assert xs_by_midx[she_midx]["correct"] is True, \
            "xsent must RESOLVE cross-sentence 'she' to woman(1), got %s" % xs_by_midx[she_midx]["resolved_cluster"]

        # WITHIN-SENTENCE 'her': baseline correct (P1 no-regression control)
        assert base_by_midx[her_midx]["correct"] is True, \
            "baseline must resolve within-sentence 'her' to girl(3), got %s" % base_by_midx[her_midx]["resolved_cluster"]
        assert xs_by_midx[her_midx]["correct"] is True, \
            "xsent must also resolve within-sentence 'her', got %s" % xs_by_midx[her_midx]["resolved_cluster"]

        # VALIDITY GATE on this micro-corpus: baseline cross-sentence acc == 0 <= 0.10
        xsent_targets = [she_midx]
        base_xsent_acc = sum(base_by_midx[m]["correct"] for m in xsent_targets) / len(xsent_targets)
        assert base_xsent_acc <= VALIDITY_GATE_MAX, \
            "validity gate: baseline cross-sentence acc %.3f must be <= %.2f" % (base_xsent_acc, VALIDITY_GATE_MAX)

        # arms-differ on the unified records
        recs, _meta = evaluate_book(tmp_path, reader)
        digs = arms_must_differ(recs)
        assert digs[BASELINE_ARM] != digs[MECHANISM_ARM], "arms-differ self-test failed"

        _p("SELF-TEST PASS: parse+sentence-index + cross-sentence target stratification + "
           "CorefReader (baseline-blind vs xsent-resolves) + validity gate + P1 no-regression "
           "+ arms-differ all verified (glass-box, no network).")
        return 0
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())

    run_mode = "smoke" if args.smoke else "full"
    metrics, out_dir = run(run_mode)
    _p("[%s] verdict=%s" % (run_mode, metrics["verdict"]))
    _p(metrics["verdict_msg"])
    _p("bucket_counts=%s" % metrics["bucket_counts"])
    xt = metrics["cross_sentence_subset_table"]
    _p("CROSS-SENTENCE subset (n=%d):" % metrics["n_xsent"])
    for arm_name, _r, _s in ARMS:
        _p("  %-26s acc=%s prec=%s attempt=%s" %
           (arm_name, _f(xt[arm_name]["acc"]), _f(xt[arm_name]["prec"]),
            _f(xt[arm_name]["attempt_rate"])))
    _p("  delta_xsent(maintained-baseline)=%s  validity_gate_ok=%s  sign_stability=%s" %
       (_f(metrics["delta_xsent"]), metrics["validity_gate_ok"],
        _f(metrics["bootstrap_sign_stability"])))
    _p("per-distance winner (xsent strategies): %s" %
       {b: (metrics["per_distance_winner"][b]["arm"],
            _f(metrics["per_distance_winner"][b]["acc"])) for b in BUCKETS})
    _p("metrics -> %s" % os.path.join(out_dir, "metrics.json"))


if __name__ == "__main__":
    _out = os.path.join(REPO_ROOT, "data", "exp_%s" % ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- crash-diag then re-raise (no BaseException)
        _write_crash_metrics(_out, e)
        raise
