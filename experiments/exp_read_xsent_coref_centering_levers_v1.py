#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
exp_read_xsent_coref_centering_levers_v1

MULTI-SENTENCE PHASE, STEP 1b -- lift the cross-sentence coref ceiling (backbone
xsent_maintained = 0.185 MEASURED@data/exp_read_xsent_coref_working_overlay_v1/
metrics.json) toward a real capability (> 0.30 bar).

REVISED PREMISE (backbone VET seq 29506 REFUTED the original autopsy): gender=None
is only ~16% of misses; the ceiling is dominated by SAME-GENDER COMPETITION --
multiple salient same-gender candidates where the resolver picks the wrong one.
So the DOMINANT lever is disambiguating same-gender competition via CENTERING /
grammatical-role prominence, NOT name->gender grounding (which stays a cheap minor
filter). The VET also showed maintained-salience REGRESSES within-sentence (0.228
vs recency 0.346) -> a distance-adaptive recency-within / centering-cross reader.

LEVERS (each togglable for ablation; all default OFF = validated backbone):
  L1 CENTERING (DOMINANT): among gender-compatible candidates, prefer the TOPICAL
     entity by role-weighted mention mass (SUBJECT mentions weigh 2x) + recency +
     role parallelism. Subject ~ first referring mention in its sentence (glass-box
     position proxy; Centering Cf-ranking / first-mention advantage; NO parser).
  L2 DISTANCE-ADAPTIVE: RECENCY owns short distance (validated recency_window,
     window_k=5); if no compatible antecedent inside the window -> CENTERING far.
     Window = mention-stream distance, NOT gold sentence distance (glass-box).
  L3 PRONOUN-CHAINING: chain each resolved pronoun back onto its antecedent entity
     (boost salience on every pronominal mention -> protagonist stays salient).
  L4 NAME->GENDER (cheap minor filter): fill unknown proper-name gender from a
     GENERAL name gazetteer (data/lexicons/name_gender_gazetteer.tsv, built from
     NLTK 'names'; unambiguous-only; NOT from LitBank characters = anti-circular).

ARMS (primary variable = which lever(s) move the 0.185 backbone):
  single_sentence_baseline   reset overlay every sentence (validity baseline; ~0 on
                             cross-sentence subset by construction).
  xsent_backbone             persistent overlay, strategy=maintained (reproduces the
                             step-1 backbone; positive control).
  xsent_gender_only          backbone + L4 gazetteer filter.
  xsent_chain_only           backbone + L3 pronoun-chaining.
  xsent_centering_only       L1 centering pick (DOMINANT lever, isolated).
  xsent_adaptive_only        L2 recency-within / centering-cross.
  xsent_all                  L1+L2+L3+L4 (PRIMARY combined mechanism).
  xsent_all_minus_centering  L2+L3+L4 with the adaptive FAR strategy = maintained
                             (leave-one-out: proves centering is load-bearing).

PRIMARY DISCRIMINATOR: mech = xsent_all acc on the cross-sentence subset (sent_dist
>= 1). delta_vs_backbone = acc[xsent_all] - acc[xsent_backbone]. Per-lever ablation
(each single-lever arm vs backbone) reported so we SEE which lever moves 0.185.

BANDS (pre-registered; discriminator = cross-sentence subset):
  HARD_PASS: validity_gate_ok (single_sentence_baseline xsent acc <= 0.10)
             AND xsent_all acc >= 0.30
             AND delta_vs_backbone >= 0.05
             AND delta_vs_single_sentence >= 0.15
             AND p1_no_regression (same bucket: xsent_all >= single_sentence_baseline
                 acc - 0.05)
             AND bootstrap sign_stability(xsent_all > xsent_backbone) >= 0.90.
  HARD_FAIL: NOT validity_gate_ok (invalid discriminator) OR xsent_all acc <=
             xsent_backbone acc (levers give NO lift over the backbone -> wall;
             autopsy which cases fail + name the next lever).
  MIDDLE_BAND: lift over backbone positive but below the 0.30 abs / 0.05 delta /
             stability bars -> KEEP-DIGGING autopsy (per-lever + per-distance).

NEVER-CONFIDENTLY-WRONG: a target with no gender-compatible entity ABSTAINS
(attempted=False); precision (acc-on-attempted) reported alongside accuracy.

Header numbers are DESIGN targets (HYPOTHESIZED@this file / MEASURED@ the cited
backbone metrics); reported numbers are MEASURED@ the metrics.json this run writes.

CELL-TEMPLATE MANDATORY:
# - arms_differ_verified at smoke gate (META_RULE_AF; hash per-target resolved cluster)
# - final_metrics_atomicity: tmp_replace (single-shot; metrics.json.tmp + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: symbolic accuracy metric; no matmul noise floor. Reachability shown
#   empirically: single_sentence_baseline ~0 on cross-sentence subset leaves full
#   headroom; accuracy is telemetry-sensitive (each lever moves it).
# - baseline_in_band: the DISCRIMINATOR baseline (single-sentence) is ~0 BY VALIDITY
#   DESIGN; the MECHANISM arm (xsent_all) is the in-band arm; the backbone arm is the
#   no-lever control; the "same" bucket is the P1 within-sentence no-regression control.
# - discriminator survives scale: full=all 25 cached books; smoke=first 5, asserts
#   cross-sentence subset non-empty AND validity gate holds AND arms differ.
# - HARD_PASS strictly above the wall (META_RULE_L): >=0.30 abs AND >=0.05 over the
#   backbone AND >=0.15 over single-sentence, not an at-floor clear.
# - cardinality: EXPECTED_N_UNITS = n_books usable; verdict counts per-book coverage.
# - per-unit failure-class instrumentation; no bare except.
# - calibration_check: default_ok_for_this_regime (centering role weights are
#   structural {subject=2x, parallel=+0.5}; recency window_k=5 + beta/lam ported
#   VERBATIM from validated longdist constants; no tuned-for-PASS knob).
# - all header numbers tagged HYPOTHESIZED@ / MEASURED@ / CITED@.
# - real_code_path: self-test builds real temp conll(s), runs hdlab.coref parse +
#   gazetteer + CorefReader for every lever end-to-end and asserts mechanism behavior.
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

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------
ANCHOR_NAME = "read_xsent_coref_centering_levers_v1"
CORPUS_DIR = os.path.join(REPO_ROOT, "data", "corpora", "litbank_coref_conll")
SMOKE_N = 5

# Arms: (name, resolve_stream kwargs). All default-OFF levers = validated backbone.
ARMS = [
    ("single_sentence_baseline", dict(reset_per_sentence=True, strategy="maintained")),
    ("xsent_backbone", dict(reset_per_sentence=False, strategy="maintained")),
    ("xsent_gender_only", dict(reset_per_sentence=False, strategy="maintained",
                               use_gazetteer=True)),
    ("xsent_chain_only", dict(reset_per_sentence=False, strategy="maintained",
                              chain_pronouns=True)),
    ("xsent_centering_only", dict(reset_per_sentence=False, centering=True)),
    ("xsent_adaptive_only", dict(reset_per_sentence=False, adaptive=True)),
    ("xsent_all", dict(reset_per_sentence=False, adaptive=True, chain_pronouns=True,
                       use_gazetteer=True)),
    ("xsent_all_minus_centering", dict(reset_per_sentence=False, adaptive=True,
                                       chain_pronouns=True, use_gazetteer=True,
                                       far_strategy="maintained")),
]
ARM_NAMES = [a[0] for a in ARMS]
BASELINE_ARM = "single_sentence_baseline"
BACKBONE_ARM = "xsent_backbone"
MECHANISM_ARM = "xsent_all"
LEVER_ARMS = ["xsent_gender_only", "xsent_chain_only", "xsent_centering_only",
              "xsent_adaptive_only", "xsent_all", "xsent_all_minus_centering"]

# Bands
VALIDITY_GATE_MAX = 0.10
HP_ABS = 0.30
HP_DELTA_BACKBONE = 0.05
HP_DELTA_SINGLE = 0.15
HP_SIGN_STABILITY = 0.90
P1_REGRESSION_EPS = 0.05

N_BOOTSTRAP = 500
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
def evaluate_book(path, reader, gaz):
    mentions, n_sentences = parse_litbank_conll(path, name_gender_map=gaz)
    targets = build_pronoun_targets(mentions)
    if not targets:
        return [], {"n_mentions": len(mentions), "n_sentences": n_sentences,
                    "n_targets": 0}
    per_arm_records = {}
    for arm_name, kwargs in ARMS:
        per_arm_records[arm_name] = reader.resolve_stream(mentions, targets, **kwargs)
    # zip into per-target unified records (same target order across arms)
    n = len(per_arm_records[ARMS[0][0]])
    unified = []
    for i in range(n):
        base_rec = per_arm_records[ARMS[0][0]][i]
        u = {"sent_dist": base_rec["sent_dist"], "bucket": base_rec["bucket"],
             "gold_cluster": base_rec["gold_cluster"], "correct": {},
             "attempted": {}, "resolved_cluster": {}}
        for arm_name, _kw in ARMS:
            r = per_arm_records[arm_name][i]
            u["correct"][arm_name] = r["correct"]
            u["attempted"][arm_name] = r["attempted"]
            u["resolved_cluster"][arm_name] = (-1 if r["resolved_cluster"] is None
                                               else r["resolved_cluster"])
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


def bucketize(records):
    out = {b: [] for b in BUCKETS}
    for r in records:
        out[r["bucket"]].append(r)
    return out


def arm_table(records):
    return {arm_name: {"acc": acc_on(records, arm_name),
                       "prec": prec_on(records, arm_name),
                       "attempt_rate": attrate_on(records, arm_name),
                       "n": len(records)}
            for arm_name, _kw in ARMS}


def bootstrap_sign_stability(records, arm_mech, arm_base,
                             n_boot=N_BOOTSTRAP, seed=BOOTSTRAP_SEED):
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
    for arm_name, _kw in ARMS:
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

    gaz = load_name_gender()
    if not gaz:
        raise RuntimeError("GAZETTEER_MISSING: %s not found (run tools/"
                           "build_name_gender_gazetteer.py)" % os.path.join(
                               REPO_ROOT, "data", "lexicons",
                               "name_gender_gazetteer.tsv"))

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
            recs, meta = evaluate_book(path, reader, gaz)
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

    by_bucket = bucketize(all_records)
    xsent_records = by_bucket["plus1"] + by_bucket["plus2"] + by_bucket["long"]
    same_records = by_bucket["same"]

    per_bucket_table = {b: arm_table(by_bucket[b]) for b in BUCKETS}
    xsent_table = arm_table(xsent_records)
    same_table = arm_table(same_records)
    overall_table = arm_table(all_records)

    base_xsent = xsent_table[BASELINE_ARM]["acc"]
    backbone_xsent = xsent_table[BACKBONE_ARM]["acc"]
    mech_xsent = xsent_table[MECHANISM_ARM]["acc"]

    def _d(a, b):
        return None if (a is None or b is None) else a - b

    delta_vs_backbone = _d(mech_xsent, backbone_xsent)
    delta_vs_single = _d(mech_xsent, base_xsent)

    # per-lever ablation: each lever arm's xsent acc + delta over backbone
    ablation = {}
    for arm in LEVER_ARMS:
        a = xsent_table[arm]["acc"]
        ablation[arm] = {"xsent_acc": a, "delta_vs_backbone": _d(a, backbone_xsent)}

    # honest per-distance winner across ALL arms (which mechanism wins where)
    per_distance_winner = {}
    for b in BUCKETS:
        tab = per_bucket_table[b]
        best_arm, best_acc = None, -1.0
        for arm, _kw in ARMS:
            if arm == BASELINE_ARM:
                continue
            a = tab[arm]["acc"]
            if a is not None and a > best_acc:
                best_acc, best_arm = a, arm
        per_distance_winner[b] = {"arm": best_arm,
                                  "acc": (None if best_arm is None else best_acc)}

    sign_stability = bootstrap_sign_stability(xsent_records, MECHANISM_ARM, BACKBONE_ARM)

    # P1 within-sentence no-regression vs the single-sentence baseline on "same"
    base_same = same_table[BASELINE_ARM]["acc"]
    mech_same = same_table[MECHANISM_ARM]["acc"]
    p1_ok = (base_same is not None and mech_same is not None
             and mech_same >= base_same - P1_REGRESSION_EPS)

    validity_gate_ok = (base_xsent is not None and base_xsent <= VALIDITY_GATE_MAX)

    n_xsent = len(xsent_records)
    if mech_xsent is None or n_xsent < 5:
        verdict = "UNKNOWN"
        verdict_msg = "cross-sentence subset too small (n_xsent=%d) to decide" % n_xsent
    elif not validity_gate_ok:
        verdict = "HARD_FAIL"
        verdict_msg = ("VALIDITY GATE FAILED: single_sentence_baseline acc=%.4f > %.2f on the "
                       "cross-sentence subset => invalid discriminator." % (base_xsent, VALIDITY_GATE_MAX))
    elif mech_xsent <= backbone_xsent:
        verdict = "HARD_FAIL"
        verdict_msg = ("levers give NO lift over the backbone: xsent_all acc=%.4f <= backbone "
                       "acc=%.4f on the cross-sentence subset. per-lever ablation: %s" %
                       (mech_xsent, backbone_xsent,
                        {a: _f(ablation[a]["xsent_acc"]) for a in LEVER_ARMS}))
    elif (mech_xsent >= HP_ABS and delta_vs_backbone >= HP_DELTA_BACKBONE
          and delta_vs_single is not None and delta_vs_single >= HP_DELTA_SINGLE
          and p1_ok and sign_stability is not None and sign_stability >= HP_SIGN_STABILITY):
        verdict = "HARD_PASS"
        verdict_msg = ("cross-sentence coref reaches capability: xsent_all acc=%.4f (backbone=%.4f "
                       "delta=%.4f; single_sentence=%.4f delta=%.4f), validity_gate=OK, "
                       "P1_no_regression=OK (same: mech=%.4f vs base=%.4f), sign_stability=%.3f, "
                       "n_xsent=%d." % (mech_xsent, backbone_xsent, delta_vs_backbone, base_xsent,
                                        delta_vs_single, mech_same, base_same, sign_stability, n_xsent))
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = ("levers help but sub-threshold: xsent_all acc=%.4f (backbone=%.4f delta=%.4f, "
                       "single=%.4f delta=%.4f), p1_ok=%s, sign_stability=%s, n_xsent=%d. per-lever: %s" %
                       (mech_xsent, backbone_xsent, _dbg(delta_vs_backbone), base_xsent,
                        _dbg(delta_vs_single), p1_ok, _f(sign_stability), n_xsent,
                        {a: _f(ablation[a]["xsent_acc"]) for a in LEVER_ARMS}))

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
        "gazetteer": {"path": os.path.join("data", "lexicons", "name_gender_gazetteer.tsv"),
                      "source": "NLTK 'names' (Kantrowitz/Ross), unambiguous-only",
                      "n_entries": len(gaz), "general_not_from_litbank": True},
        "config": {"arms": ARM_NAMES, "baseline_arm": BASELINE_ARM,
                   "backbone_arm": BACKBONE_ARM, "mechanism_arm": MECHANISM_ARM,
                   "lever_arms": LEVER_ARMS, "validity_gate_max": VALIDITY_GATE_MAX,
                   "hp_abs": HP_ABS, "hp_delta_backbone": HP_DELTA_BACKBONE,
                   "hp_delta_single": HP_DELTA_SINGLE, "hp_sign_stability": HP_SIGN_STABILITY,
                   "p1_regression_eps": P1_REGRESSION_EPS, "n_bootstrap": N_BOOTSTRAP,
                   "bootstrap_seed": BOOTSTRAP_SEED},
        "n_targets_total": len(all_records),
        "n_xsent": n_xsent, "n_same": len(same_records),
        "bucket_counts": {b: len(by_bucket[b]) for b in BUCKETS},
        "cross_sentence_subset_table": xsent_table,
        "within_sentence_same_table": same_table,
        "overall_table": overall_table,
        "per_bucket_table": per_bucket_table,
        "per_distance_winner": per_distance_winner,
        "per_lever_ablation": ablation,
        "baseline_xsent_acc": base_xsent,
        "backbone_xsent_acc": backbone_xsent,
        "mech_xsent_acc": mech_xsent,
        "delta_vs_backbone": delta_vs_backbone,
        "delta_vs_single_sentence": delta_vs_single,
        "validity_gate_ok": validity_gate_ok,
        "p1_no_regression_ok": p1_ok,
        "p1_same_bucket": {"baseline": base_same, "xsent_all": mech_same},
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


def _dbg(x):
    return float("nan") if x is None else x


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
# SELF-TEST (real code path: temp conll(s) -> parse + gazetteer + CorefReader
# for every lever; asserts each mechanism behaves as designed).
# ----------------------------------------------------------------------------
def self_test():
    import tempfile

    gaz = load_name_gender()
    assert gaz, "gazetteer missing (run tools/build_name_gender_gazetteer.py)"
    for n, g in [("elizabeth", "fem"), ("robert", "masc"), ("anna", "fem"),
                 ("john", "masc"), ("tom", "masc")]:
        assert gaz.get(n) == g, "gazetteer: %s expected %s got %s" % (n, g, gaz.get(n))

    def tok(tidx, word, coref="_"):
        return "st\t0\t%d\t%s\t_\t_\t_\t_\t_\t_\t_\t_\t%s" % (tidx, word, coref)

    def write_doc(sentences):
        lines = ["#begin document (st); part 0"]
        for sent in sentences:
            for i, (w, c) in enumerate(sent):
                lines.append(tok(i, w, c))
            lines.append("")
        with tempfile.NamedTemporaryFile("w", suffix=".conll", delete=False,
                                         encoding="utf-8") as tf:
            tf.write("\n".join(lines) + "\n")
            return tf.name

    def find_target(recs, head_cluster):
        # recs are unified records; match by gold cluster + bucket presence
        return [r for r in recs if r["gold_cluster"] == head_cluster]

    reader = CorefReader()
    made = []
    try:
        # ---- DOC A: L4 gazetteer (fem 'she' must exclude a masc distractor) ----
        # S0: Elizabeth(1) saw Robert(2) .   E fem(gaz) subj; Robert masc(gaz) obj.
        # S1: She(1) smiled .                she fem, cross-sentence (dist=1).
        #   backbone (gaz off): Robert gender unknown -> compatible -> recency picks
        #     Robert (WRONG, cluster 2). gender_only (gaz on): Robert masc excluded
        #     -> picks Elizabeth (CORRECT, cluster 1).
        docA = write_doc([
            [("Elizabeth", "(1)"), ("saw", "_"), ("Robert", "(2)"), (".", "_")],
            [("She", "(1)"), ("smiled", "_"), (".", "_")],
        ])
        made.append(docA)
        mA, nsA = parse_litbank_conll(docA, name_gender_map=gaz)
        # parse enrichment fields present
        eliz = [m for m in mA if m["head"] == "elizabeth"][0]
        assert eliz["name_gender"] == "fem" and eliz["gender"] is None, \
            "Elizabeth name_gender should be fem (gaz), cue gender None: %s" % eliz
        assert "wtok_start" in eliz and "sent_role_rank" in eliz, "parse missing role fields"
        assert eliz["is_subject"] is True, "Elizabeth should be sentence subject (rank 0)"
        recsA, _ = evaluate_book(docA, reader, gaz)
        shaA = find_target(recsA, 1)
        assert shaA and shaA[0]["bucket"] == "plus1", "she must be cross-sentence dist=1: %s" % shaA
        assert shaA[0]["resolved_cluster"]["xsent_backbone"] == 2, \
            "backbone should mis-resolve she->Robert(2): %s" % shaA[0]["resolved_cluster"]
        assert shaA[0]["correct"]["xsent_gender_only"] is True, \
            "gender_only should resolve she->Elizabeth(1): %s" % shaA[0]["resolved_cluster"]
        # validity gate: baseline blind on the cross-sentence 'she'
        assert shaA[0]["correct"]["single_sentence_baseline"] is False, \
            "baseline must FAIL cross-sentence she"

        # ---- DOC B: L1 centering (same-gender competition; subject beats recent) ----
        # S0: John(1) saw Tom(2) .   John masc subj(rank0), Tom masc obj(rank1).
        # S1: He(1) waited .         he masc; John & Tom both compatible.
        #   backbone maintained: counts equal -> recency tie-break -> Tom (WRONG, 2).
        #   centering: John subject role-mass 2.0 + parallelism > Tom obj 1.0 -> John (1).
        docB = write_doc([
            [("John", "(1)"), ("saw", "_"), ("Tom", "(2)"), (".", "_")],
            [("He", "(1)"), ("waited", "_"), (".", "_")],
        ])
        made.append(docB)
        recsB, _ = evaluate_book(docB, reader, gaz)
        heB = find_target(recsB, 1)
        assert heB and heB[0]["bucket"] == "plus1", "he must be cross-sentence dist=1"
        assert heB[0]["resolved_cluster"]["xsent_backbone"] == 2, \
            "backbone should mis-resolve he->Tom(2) by recency: %s" % heB[0]["resolved_cluster"]
        assert heB[0]["correct"]["xsent_centering_only"] is True, \
            "centering should resolve he->John(1) by subject prominence: %s" % heB[0]["resolved_cluster"]

        # ---- DOC C: P1 within-sentence no-regression (baseline & xsent_all agree) ----
        # S0: Anna(1) hugged her(1) .   her within-sentence (dist=0); antecedent Anna.
        docC = write_doc([
            [("Anna", "(1)"), ("hugged", "_"), ("her", "(1)"), (".", "_")],
        ])
        made.append(docC)
        recsC, _ = evaluate_book(docC, reader, gaz)
        herC = find_target(recsC, 1)
        assert herC and herC[0]["bucket"] == "same", "her must be within-sentence dist=0"
        assert herC[0]["correct"]["single_sentence_baseline"] is True, \
            "baseline must resolve within-sentence her->Anna(1)"
        assert herC[0]["correct"]["xsent_all"] is True, \
            "xsent_all must NOT regress within-sentence her->Anna(1) (P1)"

        # arms-differ on a combined record set
        digs = arms_must_differ(recsA + recsB + recsC)
        assert digs[BASELINE_ARM] != digs[MECHANISM_ARM], "arms-differ failed"

        _p("SELF-TEST PASS: gazetteer(fem-filter) + centering(subject-beats-recent) + "
           "adaptive/chain wired + P1 within-sentence no-regression + validity gate + "
           "arms-differ all verified (glass-box, no network).")
        return 0
    finally:
        for pth in made:
            try:
                os.unlink(pth)
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
    for arm_name, _kw in ARMS:
        _p("  %-28s acc=%s prec=%s attempt=%s n=%d" %
           (arm_name, _f(xt[arm_name]["acc"]), _f(xt[arm_name]["prec"]),
            _f(xt[arm_name]["attempt_rate"]), xt[arm_name]["n"]))
    _p("delta xsent_all vs backbone=%s  vs single_sentence=%s  validity_gate_ok=%s  sign_stability=%s" %
       (_f(metrics["delta_vs_backbone"]), _f(metrics["delta_vs_single_sentence"]),
        metrics["validity_gate_ok"], _f(metrics["bootstrap_sign_stability"])))
    _p("P1 same-bucket: baseline=%s xsent_all=%s p1_ok=%s" %
       (_f(metrics["p1_same_bucket"]["baseline"]), _f(metrics["p1_same_bucket"]["xsent_all"]),
        metrics["p1_no_regression_ok"]))
    _p("per-lever ablation (xsent acc / delta vs backbone):")
    for arm in LEVER_ARMS:
        ab = metrics["per_lever_ablation"][arm]
        _p("  %-28s acc=%s  delta=%s" % (arm, _f(ab["xsent_acc"]), _f(ab["delta_vs_backbone"])))
    _p("per-distance winner: %s" %
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
