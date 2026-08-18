#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
exp_read_xsent_coref_distractor_suppress_v1

MULTI-SENTENCE PHASE, STEP 1d -- attack the DIAGNOSTIC-CONFIRMED cross-sentence
coref wall (NOT the refuted appositive-bridging, which the diagnostic found is the
best-handled type). The confirmed wall (diagnostic, VET-pending):
  (1) the wrong picks are GENERIC / NON-REFERENTIAL common nouns (servants / people /
      one / country / nobody / neighbourhood) out-competing the correct SPECIFIC
      character;
  (2) the reader NEVER ABSTAINS -- 100% of cross-sentence misses are CONFIDENT wrong
      picks (attempt rate 1.0 on every xsent arm); the single-sentence reader's
      never-confidently-wrong property is absent cross-sentence.

TWO BRAIN-FAITHFUL LEVERS (design + ablate each), pluggable in the NEW module
hdlab.coref_distractor_suppress (banked cells / modules NOT edited):
  LEVER 1  GENERIC-DISTRACTOR SUPPRESSION (general, structural, anti-circular):
             1a NONREF  = closed GRAMMATICAL class of indefinite / quantifier pro-forms
                          (one / none / nobody / someone / other / some / ...). General
                          English function words, NOT LitBank character names.
             1b STRUCT  = a COMMON noun (not a proper name, no gender cue) NEVER realized
                          as a grammatical SUBJECT / agent (parse role rank 0) anywhere in
                          the doc -> a non-topical bare generic. Purely structural, no
                          lexicon, book-agnostic. GUARD: proper-name or gender-cued
                          entities (specific characters) are NEVER suppressed.
  LEVER 2  ABSTENTION (never-confidently-wrong): abstain when no confident SPECIFIC
           antecedent survives (pool empty after suppression, or maintained-salience
           margin below threshold) instead of forcing a pick. Converts confident-wrong
           -> abstain; coverage cost measured honestly (attempt rate + precision).
  LEVER 3  (optional) PRONOUN-CHAIN CONTINUITY: chain a resolved (specific) antecedent so
           the topical entity stays salient across a pronoun run. Default ON to match the
           0.2053 backbone; because resolution targets only the SPECIFIC pool, chaining
           re-adds no generic noise.

DISCRIMINATOR: on the SAME LitBank cross-sentence gold (n=599, sent_dist>=1) vs the
flat-overlay / adaptive plateau 0.2053 (MEASURED@data/exp_read_xsent_coref_centering_
levers_v1/metrics.json:cross_sentence_subset_table.xsent_all.acc) and bundle-focus 0.1870
(MEASURED@data/exp_read_xsent_coref_bundle_focus_v1/metrics.json).
  (a) ACCURACY: does distractor suppression LIFT above 0.2053 by a real margin?
  (b) TRUSTWORTHINESS: does abstention DROP the confident-wrong rate (currently ~0.7947
      of xsent targets = 1 - 0.2053) with retained precision on answered?
Both reported honestly.

PASS CRITERION (pre-registered, DECLARED): the HARD_PASS is on the ACCURACY axis
(sup_both acc >= plateau + 0.03 with paired-bootstrap sign_stability >= 0.90). The
trustworthiness axis is reported as a MEASURED result (expected NEGATIVE per the honest
expectation below); a TRUST_PASS is recognized if it fires but is not required.

HONEST EXPECTATION (stated before the run; the design pre-flight measured these on
disk during authoring and they hold): distractor suppression LIFTS accuracy (the STRUCT
lever is load-bearing); ABSTENTION does NOT buy trustworthiness here because a gender-
compatible SPECIFIC candidate almost always exists (pool-empty abstention fires ~0%) and
the maintained-salience margin is an UNINFORMATIVE confidence signal (margin-abstain
trades away more correct than wrong). So the value is ACCURACY, plus the honest finding
that the residual wall is SAME-GENDER SPECIFIC-CHARACTER competition, not generics.

FAIRNESS:
  - P1: p1_backbone (CorefReader adaptive+chain+gazetteer) reproduces the 0.2053 plateau.
  - sup_off (SuppressReader, suppression OFF) reproduces p1_backbone BIT-FOR-BIT (the
    suppression module adds no hidden lift; suppression is the ONE isolated variable).
  - VALIDITY GATE: single_sentence_baseline ~0 on the cross-sentence subset.
  - The generic stop-list / structural test are GENERAL (grammatical quantifier class +
    never-a-subject structural signal), NOT tuned to LitBank characters (anti-circular).
  - P2: ablate each lever (nonref-only, struct-only, both, both-no-chain, abstain, margin).
  - NEVER construction-aid: gold clusters ONLY stratify by distance + score correctness.

Header numbers tagged MEASURED@ (cited from disk) / HYPOTHESIZED@ (this file's design
targets); reported numbers are MEASURED@ the metrics.json this run writes.

CELL-TEMPLATE MANDATORY:
# - arms_differ_verified at smoke gate (META_RULE_AF; hash per-target resolved cluster;
#   p1_backbone != sup_both).
# - final_metrics_atomicity: tmp_replace (single-shot; metrics.json.tmp + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: symbolic accuracy metric; no matmul noise floor. Reachability shown
#   empirically: single_sentence_baseline ~0 on the xsent subset leaves full headroom;
#   accuracy is telemetry-sensitive (each lever moves it, measured during pre-flight).
# - baseline_in_band: the DISCRIMINATOR baseline (single-sentence) is ~0 BY VALIDITY
#   DESIGN; the MECHANISM arm (sup_both) is in-band; p1_backbone is the plateau control;
#   sup_off is the faithfulness control (== p1_backbone).
# - discriminator survives scale: full = all 25 cached books; smoke = first 5, asserts the
#   xsent subset non-empty AND suppression FIRES AND validity gate holds AND arms differ.
# - HARD_PASS strictly above the plateau (META_RULE_L): >= plateau + 0.03 AND sign
#   stability >= 0.90, not an at-floor clear.
# - cardinality: EXPECTED_N_UNITS = n_books usable; verdict counts per-book coverage.
# - per-unit failure-class instrumentation; no bare except.
# - calibration_check: default_ok_for_this_regime (overlay constants + centering weights
#   ported VERBATIM; the quantifier stop-list is a general grammatical class; the STRUCT
#   test is parse-structural; no tuned-for-PASS knob; margin_thresh reported not gated).
# - all header numbers tagged MEASURED@ / HYPOTHESIZED@.
# - real_code_path: self-test builds a real temp conll, runs hdlab.coref parse +
#   build_pronoun_targets + CorefReader + SuppressReader end-to-end and asserts the
#   suppress-OFF == CorefReader-adaptive faithfulness identity.
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

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.coref import (  # noqa: E402
    BUCKETS,
    CorefReader,
    build_pronoun_targets,
    load_name_gender,
    parse_litbank_conll,
)
from hdlab.coref_distractor_suppress import SuppressReader  # noqa: E402

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------
ANCHOR_NAME = "read_xsent_coref_distractor_suppress_v1"
CORPUS_DIR = os.path.join(REPO_ROOT, "data", "corpora", "litbank_coref_conll")
SMOKE_N = 5

# Cited plateaus (MEASURED@ disk).
PLATEAU_ACC = 0.2053     # MEASURED@centering_levers xsent_all.acc (adaptive+chain+gaz)
BUNDLE_FOCUS_ACC = 0.1870  # MEASURED@bundle_focus bundle_focus_chain.acc

# Arm spec: (name, reader_kind, kwargs). reader_kind in {"coref", "suppress"}.
ARMS = [
    ("single_sentence_baseline", "coref",
     dict(reset_per_sentence=True, strategy="maintained")),
    ("p1_backbone", "coref",
     dict(reset_per_sentence=False, adaptive=True, chain_pronouns=True,
          use_gazetteer=True)),
    ("sup_off", "suppress",
     dict(suppress_generic=False, chain_pronouns=True, use_gazetteer=True)),
    ("sup_nonref", "suppress",
     dict(suppress_generic=True, use_nonref=True, use_struct=False,
          abstain_on_empty=False, chain_pronouns=True, use_gazetteer=True)),
    ("sup_struct", "suppress",
     dict(suppress_generic=True, use_nonref=False, use_struct=True,
          abstain_on_empty=False, chain_pronouns=True, use_gazetteer=True)),
    ("sup_both", "suppress",
     dict(suppress_generic=True, use_nonref=True, use_struct=True,
          abstain_on_empty=False, chain_pronouns=True, use_gazetteer=True)),
    ("sup_both_nochain", "suppress",
     dict(suppress_generic=True, use_nonref=True, use_struct=True,
          abstain_on_empty=False, chain_pronouns=False, use_gazetteer=True)),
    ("sup_both_abstain", "suppress",
     dict(suppress_generic=True, use_nonref=True, use_struct=True,
          abstain_on_empty=True, chain_pronouns=True, use_gazetteer=True)),
    ("sup_both_margin", "suppress",
     dict(suppress_generic=True, use_nonref=True, use_struct=True,
          abstain_on_empty=True, margin_abstain=True, margin_thresh=0.5,
          chain_pronouns=True, use_gazetteer=True)),
]
ARM_NAMES = [a[0] for a in ARMS]
BASELINE_ARM = "single_sentence_baseline"
P1_ARM = "p1_backbone"
FAITHFUL_ARM = "sup_off"
MECHANISM_ARM = "sup_both"            # PRIMARY accuracy mechanism
TRUST_ARM = "sup_both_abstain"        # trustworthiness attempt

# Bands (pre-registered).
VALIDITY_GATE_MAX = 0.10              # single_sentence acc on xsent subset must be <= this
FAITHFUL_EPS = 0.005                 # |sup_off - p1_backbone| must be <= this
PLATEAU_REPRO_EPS = 0.01            # |p1_backbone - 0.2053| must be <= this
HP_ACC_DELTA = 0.03                # ACCURACY pass: sup_both >= p1_backbone + this
HP_SIGN_STABILITY = 0.90
# TRUST pass (secondary; recognized if fires, not required):
TRUST_CWR_DROP = 0.10              # sup_both_abstain cwr <= p1 cwr - this
TRUST_PREC_GAIN = 0.05            # sup_both_abstain prec >= p1 acc + this
TRUST_ATTEMPT_LO = 0.30
TRUST_ATTEMPT_HI = 0.95

N_BOOTSTRAP = 2000
BOOTSTRAP_SEED = 20260724


def _p(msg):
    print(msg, flush=True)


def _f(x):
    return "None" if x is None else ("%.4f" % x)


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
def run_arm(reader_coref, reader_sup, mentions, targets, kind, kwargs):
    if kind == "coref":
        return reader_coref.resolve_stream(mentions, targets, **kwargs)
    return reader_sup.resolve_stream(mentions, targets, **kwargs)


def evaluate_book(path, reader_coref, reader_sup, gaz):
    mentions, n_sentences = parse_litbank_conll(path, name_gender_map=gaz)
    targets = build_pronoun_targets(mentions)
    if not targets:
        return [], {"n_mentions": len(mentions), "n_sentences": n_sentences,
                    "n_targets": 0}
    per_arm = {}
    for name, kind, kwargs in ARMS:
        per_arm[name] = run_arm(reader_coref, reader_sup, mentions, targets, kind, kwargs)
    n = len(targets)
    unified = []
    for i in range(n):
        b = per_arm[ARMS[0][0]][i]
        u = {"sent_dist": b["sent_dist"], "bucket": b["bucket"],
             "gold_cluster": b["gold_cluster"],
             "correct": {}, "attempted": {}, "resolved_cluster": {},
             "n_cands": {}, "n_pool": {}}
        for name, _k, _kw in ARMS:
            r = per_arm[name][i]
            u["correct"][name] = r["correct"]
            u["attempted"][name] = r["attempted"]
            u["resolved_cluster"][name] = (-1 if r["resolved_cluster"] is None
                                           else r["resolved_cluster"])
            u["n_cands"][name] = r.get("n_cands", -1)
            u["n_pool"][name] = r.get("n_pool", -1)
        unified.append(u)
    meta = {"n_mentions": len(mentions), "n_sentences": n_sentences, "n_targets": n}
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


def cwr_on(records, arm):
    """Confident-wrong rate: fraction of ALL targets that are attempted AND wrong."""
    if not records:
        return None
    return sum(1 for r in records if r["attempted"][arm] and not r["correct"][arm]) / len(records)


def bucketize(records):
    out = {b: [] for b in BUCKETS}
    for r in records:
        out[r["bucket"]].append(r)
    return out


def arm_table(records):
    return {name: {"acc": acc_on(records, name), "prec": prec_on(records, name),
                   "attempt_rate": attrate_on(records, name),
                   "confident_wrong_rate": cwr_on(records, name), "n": len(records)}
            for name, _k, _kw in ARMS}


def paired_sign_stability(records, arm_mech, arm_base, n_boot=N_BOOTSTRAP,
                          seed=BOOTSTRAP_SEED):
    if len(records) < 2:
        return None
    rng = np.random.default_rng(seed)
    mech = np.array([r["correct"][arm_mech] for r in records], dtype=float)
    base = np.array([r["correct"][arm_base] for r in records], dtype=float)
    n = len(records)
    pos = 0
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        if mech[idx].mean() - base[idx].mean() > 0:
            pos += 1
    return pos / n_boot


def arms_must_differ(all_records):
    digests = {}
    for name, _k, _kw in ARMS:
        vec = bytes()
        for r in all_records:
            vec += int(r["resolved_cluster"][name]).to_bytes(4, "big", signed=True)
        digests[name] = hashlib.sha256(vec).hexdigest()
    assert digests[P1_ARM] != digests[MECHANISM_ARM], (
        "META_RULE_AF VIOLATION: %s and %s produced bit-identical resolved clusters"
        % (P1_ARM, MECHANISM_ARM))
    return digests


def autopsy(xsent_records):
    """Keep-digging autopsy: fixed/broken vs backbone + residual-miss competitor analysis."""
    fixed = broke = 0
    for r in xsent_records:
        b = r["correct"][P1_ARM]
        m = r["correct"][MECHANISM_ARM]
        if m and not b:
            fixed += 1
        elif b and not m:
            broke += 1
    # residual misses of the mechanism arm: attempted AND wrong on xsent
    misses = [r for r in xsent_records
              if r["attempted"][MECHANISM_ARM] and not r["correct"][MECHANISM_ARM]]
    n_miss = len(misses)
    # how many residual misses still have >=2 SPECIFIC same-gender competitors
    # (n_pool = surviving specific candidates) = the same-gender-competition wall
    multi_specific = sum(1 for r in misses if r["n_pool"][MECHANISM_ARM] >= 2)
    # how many residual misses had generics still present (n_cands > n_pool)
    had_generics = sum(1 for r in misses
                       if r["n_cands"][MECHANISM_ARM] > r["n_pool"][MECHANISM_ARM])
    # per-bucket fixed
    by_bucket = bucketize(xsent_records)
    per_bucket_delta = {}
    for b in BUCKETS:
        recs = by_bucket[b]
        if not recs:
            per_bucket_delta[b] = None
            continue
        per_bucket_delta[b] = {
            "n": len(recs),
            "backbone_acc": acc_on(recs, P1_ARM),
            "sup_both_acc": acc_on(recs, MECHANISM_ARM),
            "delta": (acc_on(recs, MECHANISM_ARM) - acc_on(recs, P1_ARM)),
        }
    return {"fixed_wrong_to_right": fixed, "broken_right_to_wrong": broke,
            "net": fixed - broke, "n_residual_miss": n_miss,
            "residual_miss_multi_specific_competitor": multi_specific,
            "residual_miss_generic_still_present": had_generics,
            "per_bucket_delta_vs_backbone": per_bucket_delta}


# ----------------------------------------------------------------------------
# RUN
# ----------------------------------------------------------------------------
def run(run_mode):
    t0 = time.perf_counter()
    out_dir = os.path.join(REPO_ROOT, "data",
                           "exp_%s%s" % (ANCHOR_NAME, "_smoke" if run_mode == "smoke" else ""))
    os.makedirs(out_dir, exist_ok=True)
    _write_start_marker(out_dir, run_mode, 0)

    gaz = load_name_gender()
    books = list_books(run_mode)
    if len(books) < 2:
        raise RuntimeError("CORPUS_UNAVAILABLE: only %d books in %s" % (len(books), CORPUS_DIR))

    reader_coref = CorefReader()
    reader_sup = SuppressReader()
    all_records = []
    per_book = {}
    book_failures = []
    n_suppressed_fired = 0
    for path in books:
        b = os.path.basename(path)
        try:
            recs, meta = evaluate_book(path, reader_coref, reader_sup, gaz)
            per_book[b] = meta
            for r in recs:
                r["book"] = b
                if r["n_cands"][MECHANISM_ARM] > r["n_pool"][MECHANISM_ARM]:
                    n_suppressed_fired += 1
            all_records.extend(recs)
            _p("[book] %-50s targets=%d sents=%d" % (b[:50], meta["n_targets"], meta["n_sentences"]))
        except Exception as e:  # noqa: BLE001 -- per-book failure-class recorded, not silent
            book_failures.append({"book": b, "failure_class": type(e).__name__,
                                  "msg": str(e)[:160]})
            _p("[book-FAIL] %s : %s: %s" % (b, type(e).__name__, str(e)[:120]))

    if not all_records:
        raise RuntimeError("NO_TARGETS: parsed %d books, 0 pronoun targets" % len(books))

    digests = arms_must_differ(all_records)

    by_bucket = bucketize(all_records)
    xsent_records = by_bucket["plus1"] + by_bucket["plus2"] + by_bucket["long"]
    same_records = by_bucket["same"]

    xsent_table = arm_table(xsent_records)
    same_table = arm_table(same_records)
    overall_table = arm_table(all_records)
    per_bucket_table = {b: arm_table(by_bucket[b]) for b in BUCKETS}

    n_xsent = len(xsent_records)

    base_acc = xsent_table[BASELINE_ARM]["acc"]
    p1_acc = xsent_table[P1_ARM]["acc"]
    p1_cwr = xsent_table[P1_ARM]["confident_wrong_rate"]
    off_acc = xsent_table[FAITHFUL_ARM]["acc"]
    mech_acc = xsent_table[MECHANISM_ARM]["acc"]
    trust = xsent_table[TRUST_ARM]
    delta_acc = None if (mech_acc is None or p1_acc is None) else mech_acc - p1_acc

    sign_stability = paired_sign_stability(xsent_records, MECHANISM_ARM, P1_ARM)

    # gates
    validity_gate_ok = (base_acc is not None and base_acc <= VALIDITY_GATE_MAX)
    faithful_ok = (off_acc is not None and p1_acc is not None
                   and abs(off_acc - p1_acc) <= FAITHFUL_EPS)
    plateau_repro_ok = (p1_acc is not None and abs(p1_acc - PLATEAU_ACC) <= PLATEAU_REPRO_EPS)
    # plateau reproduction is a FULL-corpus check: the 0.2053 plateau is the 25-book number;
    # on a SMOKE subset the p1 backbone naturally differs (the subset is not the full set).
    plateau_gate = plateau_repro_ok if run_mode == "full" else True

    acc_pass = (validity_gate_ok and faithful_ok and plateau_gate
                and delta_acc is not None and delta_acc >= HP_ACC_DELTA
                and sign_stability is not None and sign_stability >= HP_SIGN_STABILITY)

    trust_pass = (validity_gate_ok and faithful_ok and p1_cwr is not None
                  and trust["confident_wrong_rate"] is not None
                  and trust["confident_wrong_rate"] <= p1_cwr - TRUST_CWR_DROP
                  and trust["prec"] is not None and p1_acc is not None
                  and trust["prec"] >= p1_acc + TRUST_PREC_GAIN
                  and trust["attempt_rate"] is not None
                  and TRUST_ATTEMPT_LO <= trust["attempt_rate"] <= TRUST_ATTEMPT_HI)

    aut = autopsy(xsent_records)

    # verdict
    if delta_acc is None or n_xsent < 5:
        verdict = "UNKNOWN"
        verdict_msg = "cross-sentence subset too small (n_xsent=%d) to decide" % n_xsent
    elif not validity_gate_ok:
        verdict = "HARD_FAIL"
        verdict_msg = ("VALIDITY GATE FAILED: single_sentence baseline acc=%.4f > %.2f on the "
                       "xsent subset => invalid discriminator." % (base_acc, VALIDITY_GATE_MAX))
    elif not (faithful_ok and plateau_gate):
        verdict = "HARD_FAIL"
        verdict_msg = ("FAIRNESS FAILED: sup_off acc=%.4f vs p1_backbone acc=%.4f (eps=%.3f, ok=%s); "
                       "p1_backbone vs plateau 0.2053 (full-mode ok=%s, run_mode=%s). Implementation "
                       "drift; suppression not the isolated variable." %
                       (off_acc, p1_acc, FAITHFUL_EPS, faithful_ok, plateau_repro_ok, run_mode))
    elif acc_pass:
        verdict = "HARD_PASS"
        verdict_msg = ("ACCURACY PASS: generic-distractor suppression lifts cross-sentence coref "
                       "sup_both acc=%.4f vs plateau p1_backbone=%.4f (delta=+%.4f, sign_stability="
                       "%.3f), validity_gate=OK (single_sentence=%.4f), faithful sup_off=%.4f==p1. "
                       "fixed=%d broke=%d net=%d. TRUST axis: sup_both_abstain attempt=%s prec=%s "
                       "cwr=%s (trust_pass=%s)." %
                       (mech_acc, p1_acc, delta_acc, sign_stability, base_acc, off_acc,
                        aut["fixed_wrong_to_right"], aut["broken_right_to_wrong"], aut["net"],
                        _f(trust["attempt_rate"]), _f(trust["prec"]),
                        _f(trust["confident_wrong_rate"]), trust_pass))
    elif trust_pass:
        verdict = "HARD_PASS"
        verdict_msg = ("TRUST PASS (secondary axis): sup_both_abstain cwr=%.4f (p1 cwr=%.4f), prec=%.4f "
                       "(p1 acc=%.4f), attempt=%.4f. ACCURACY axis: sup_both=%.4f delta=+%s." %
                       (trust["confident_wrong_rate"], p1_cwr, trust["prec"], p1_acc,
                        trust["attempt_rate"], mech_acc, _f(delta_acc)))
    elif delta_acc <= 0.005 and not trust_pass:
        verdict = "HARD_FAIL"
        verdict_msg = ("NO LIFT: sup_both acc=%.4f <= plateau p1_backbone=%.4f + 0.005 (delta=%.4f) AND "
                       "no trust pass (sup_both_abstain prec=%s attempt=%s cwr=%s). Honest ceiling on "
                       "LitBank xsent pronoun coref for this glass-box resolver. Autopsy: residual misses "
                       "n=%d, %d with >=2 same-gender specific competitors." %
                       (mech_acc, p1_acc, delta_acc, _f(trust["prec"]), _f(trust["attempt_rate"]),
                        _f(trust["confident_wrong_rate"]), aut["n_residual_miss"],
                        aut["residual_miss_multi_specific_competitor"]))
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = ("PARTIAL: sup_both acc=%.4f (plateau=%.4f, delta=+%.4f, sign_stability=%s) below "
                       "the +0.03 bar or stability short; trust_pass=%s. fixed=%d broke=%d." %
                       (mech_acc, p1_acc, delta_acc, _f(sign_stability), trust_pass,
                        aut["fixed_wrong_to_right"], aut["broken_right_to_wrong"]))

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
        "config": {"arms": ARM_NAMES, "baseline_arm": BASELINE_ARM, "p1_arm": P1_ARM,
                   "faithful_arm": FAITHFUL_ARM, "mechanism_arm": MECHANISM_ARM,
                   "trust_arm": TRUST_ARM, "plateau_acc_cited": PLATEAU_ACC,
                   "bundle_focus_acc_cited": BUNDLE_FOCUS_ACC,
                   "validity_gate_max": VALIDITY_GATE_MAX, "faithful_eps": FAITHFUL_EPS,
                   "plateau_repro_eps": PLATEAU_REPRO_EPS, "hp_acc_delta": HP_ACC_DELTA,
                   "hp_sign_stability": HP_SIGN_STABILITY, "trust_cwr_drop": TRUST_CWR_DROP,
                   "trust_prec_gain": TRUST_PREC_GAIN, "n_bootstrap": N_BOOTSTRAP,
                   "bootstrap_seed": BOOTSTRAP_SEED,
                   "pass_criterion": "ACCURACY (sup_both >= plateau + 0.03, sign_stability >= 0.90); "
                                     "TRUST secondary (recognized if fires, not required)"},
        "n_targets_total": len(all_records), "n_xsent": n_xsent, "n_same": len(same_records),
        "bucket_counts": {b: len(by_bucket[b]) for b in BUCKETS},
        "n_targets_with_suppression_fired": n_suppressed_fired,
        "cross_sentence_subset_table": xsent_table,
        "within_sentence_same_table": same_table,
        "overall_table": overall_table,
        "per_bucket_table": per_bucket_table,
        "base_acc_xsent": base_acc, "p1_acc_xsent": p1_acc, "sup_off_acc_xsent": off_acc,
        "mech_acc_xsent": mech_acc, "delta_acc": delta_acc,
        "sign_stability": sign_stability,
        "validity_gate_ok": validity_gate_ok, "faithful_ok": faithful_ok,
        "plateau_repro_ok": plateau_repro_ok, "acc_pass": acc_pass, "trust_pass": trust_pass,
        "autopsy": aut,
        "arms_differ_digests": digests, "arms_differ_verified": True,
        "per_book": per_book, "book_failures": book_failures,
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


# ----------------------------------------------------------------------------
# SELF-TEST (real code path: temp conll -> parse + targets + CorefReader + SuppressReader)
# ----------------------------------------------------------------------------
def self_test():
    import tempfile

    def tok(tidx, word, coref="_"):
        return "selftest\t0\t%d\t%s\t_\t_\t_\t_\t_\t_\t_\t_\t%s" % (tidx, word, coref)

    lines = ["#begin document (selftest); part 0"]
    # S0: Anna(1) summoned the servants(2) .   Anna is the SUBJECT (rank 0); the genderless
    #     'servants' is only ever an OBJECT (never a subject) = the structural generic, and
    #     is the recency-local competitor for the next pronoun.
    lines += [tok(0, "Anna", "(1)"), tok(1, "summoned"), tok(2, "the"),
              tok(3, "servants", "(2)"), tok(4, "."), ""]
    # S1: She(1) left .   -> cross-sentence; gold = Anna(1). Backbone recency picks the more
    #     recent genderless 'servants' (WRONG); suppression removes it so 'anna' wins (RIGHT).
    lines += [tok(0, "She", "(1)"), tok(1, "left"), tok(2, "."), ""]

    with tempfile.NamedTemporaryFile("w", suffix=".conll", delete=False,
                                     encoding="utf-8") as tf:
        tf.write("\n".join(lines) + "\n")
        tmp_path = tf.name
    try:
        gaz = load_name_gender()
        mentions, n_sent = parse_litbank_conll(tmp_path, name_gender_map=gaz)
        assert n_sent == 2, "expected 2 sentences, got %d" % n_sent
        targets = build_pronoun_targets(mentions)
        heads = {t["target"]["head"] for t in targets}
        assert heads == {"she"}, "expected she targets, got %s" % heads
        # both 'she' targets are cross-sentence (antecedent Anna in a prior sentence)
        assert all(t["sent_dist"] >= 1 for t in targets), "targets must be cross-sentence"

        reader_coref = CorefReader()
        reader_sup = SuppressReader()

        # FAITHFULNESS: sup_off == CorefReader adaptive+chain+gaz (the ONE isolated variable).
        base = reader_coref.resolve_stream(mentions, targets, reset_per_sentence=False,
                                           adaptive=True, chain_pronouns=True,
                                           use_gazetteer=True)
        off = reader_sup.resolve_stream(mentions, targets, suppress_generic=False,
                                        chain_pronouns=True, use_gazetteer=True)
        for b, o in zip(base, off):
            assert b["resolved_cluster"] == o["resolved_cluster"], \
                "sup_off must reproduce CorefReader adaptive bit-for-bit"

        # SUPPRESSION: sup_both must suppress the genderless never-subject 'servants' so the
        # specific named 'anna' wins both cross-sentence pronouns -> correct.
        both = reader_sup.resolve_stream(mentions, targets, suppress_generic=True,
                                         use_nonref=True, use_struct=True,
                                         chain_pronouns=True, use_gazetteer=True)
        assert any(r["n_cands"] > r["n_pool"] for r in both), "suppression never fired"
        acc_both = sum(r["correct"] for r in both) / len(both)
        assert acc_both >= 0.99, "suppression should resolve xsent 'she'->anna: acc=%.3f" % acc_both

        # arms-differ on the unified records (p1_backbone != sup_both)
        recs, _meta = evaluate_book(tmp_path, reader_coref, reader_sup, gaz)
        digs = arms_must_differ(recs)
        assert digs[P1_ARM] != digs[MECHANISM_ARM], "arms-differ self-test failed"

        # validity: single_sentence baseline ~0 on this micro xsent subset
        base_ss = reader_coref.resolve_stream(mentions, targets, reset_per_sentence=True,
                                              strategy="maintained")
        ss_acc = sum(r["correct"] for r in base_ss) / len(base_ss)
        assert ss_acc <= VALIDITY_GATE_MAX, "validity gate: baseline %.3f must be <= %.2f" % (
            ss_acc, VALIDITY_GATE_MAX)

        _p("SELF-TEST PASS: parse + xsent targets + FAITHFUL sup_off==CorefReader-adaptive + "
           "suppression fires (servants suppressed, anna wins) + arms-differ + validity gate "
           "all verified (glass-box, no network).")
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
    _p("bucket_counts=%s  n_targets_with_suppression_fired=%d" %
       (metrics["bucket_counts"], metrics["n_targets_with_suppression_fired"]))
    xt = metrics["cross_sentence_subset_table"]
    _p("CROSS-SENTENCE subset (n=%d):" % metrics["n_xsent"])
    for name, _k, _kw in ARMS:
        _p("  %-26s acc=%s prec=%s attempt=%s cwr=%s" %
           (name, _f(xt[name]["acc"]), _f(xt[name]["prec"]),
            _f(xt[name]["attempt_rate"]), _f(xt[name]["confident_wrong_rate"])))
    _p("delta_acc(sup_both-p1)=%s sign_stability=%s validity_ok=%s faithful_ok=%s plateau_repro_ok=%s"
       % (_f(metrics["delta_acc"]), _f(metrics["sign_stability"]), metrics["validity_gate_ok"],
          metrics["faithful_ok"], metrics["plateau_repro_ok"]))
    _p("autopsy=%s" % metrics["autopsy"])
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
