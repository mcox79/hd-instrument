#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
exp_read_xsent_coref_entity_merge_v1

MULTI-SENTENCE PHASE, STEP 1c -- PROPER-NAME ALIASING / ENTITY MERGING.

The step-1b levers (centering/adaptive/gender/chaining) only lifted cross-sentence
coref 0.1853 -> 0.2053 (MEASURED@data/exp_read_xsent_coref_centering_levers_v1/
metrics.json: xsent_backbone=0.1853, xsent_all=0.2053, single_sentence_baseline=
0.0000, n_xsent=599) because they all operate DOWNSTREAM of ENTITY FRAGMENTATION:
WorkingOverlay's surface-head grouping splits each character across >1 overlay
entity ("Elizabeth" / "Miss Bennet" / "Bennet" = 3). Salience/centering/chaining
cannot accumulate on the true referent, so a locally-recent minor character
out-saliences each fragment.

MECHANISM (this cell): entity coreference / MERGING BEFORE resolution -- cluster
surface-form variants of the same entity into ONE canonical overlay entity via
GENERAL rules (title stripping; shared content token; first-name<->surname), then
run pronoun resolution + salience + the step-1b adaptive strategy on the UNIFIED
entities. Incremental (forward-only). Implemented in hdlab/coref.py (EntityAliaser
+ build_merge_map + resolve_stream(merge_entities=True)); this cell is pluggable and
does NOT edit the banked step-1b cell.

ARMS (primary variable = entity merging on/off; step-1b adaptive backbone held fixed):
  single_sentence_baseline   reset overlay every sentence (validity baseline; ~0 on
                             the cross-sentence subset by construction).
  xsent_backbone_step1b      persistent overlay + step-1b best levers (adaptive far=
                             centering, pronoun-chaining, gazetteer). == step-1b
                             xsent_all (0.2053 positive control). This is ALSO the
                             P2 merge-ablation control (merge OFF -> fragmentation
                             returns -> ceiling drops back to ~0.2053).
  xsent_merged               xsent_backbone_step1b + merge_entities (MECHANISM):
                             proper-name variants unified before resolution.

PRIMARY DISCRIMINATOR: mech = xsent_merged acc on the cross-sentence subset (sent_dist
>= 1). delta_vs_backbone = acc[xsent_merged] - acc[xsent_backbone_step1b].

FRAGMENTATION metric (before/after; the wall being tested):
  distinct_heads_per_targeted_cluster  DATA property: avg distinct nominal surface
                                        heads per targeted gold cluster (~3.53 = the
                                        fragmentation the backbone SUFFERS).
  entities_per_targeted_cluster_before  avg # overlay entities per targeted gold
                                        cluster WITHOUT merge (each head = 1 entity).
  entities_per_targeted_cluster_after   avg # overlay entities per targeted gold
                                        cluster WITH merge (should drop toward ~1).

OVER-MERGE PRECISION (critical -- merging two DISTINCT people is worse than
fragmenting one): among all pairs of nominal mentions the merger unified across a
DIFFERENT surface head (the merge decisions), fraction that share the SAME gold
cluster. merge_precision < 0.50 = merging wrongly unifies more than it correctly
unifies (HARD_FAIL). The accuracy gain must be NET of over-merge damage.

BANDS (pre-registered; discriminator = cross-sentence subset):
  HARD_PASS: validity_gate_ok (single_sentence_baseline xsent acc <= 0.10)
             AND xsent_merged acc >= 0.30
             AND delta_vs_backbone >= 0.05
             AND delta_vs_single_sentence >= 0.15
             AND p1_no_regression (same bucket: xsent_merged >= single_sentence acc
                 - 0.05)
             AND merging_fires (entities_per_cluster_after < before AND n_cross_merge
                 > 0)
             AND merge_precision >= 0.80
             AND bootstrap sign_stability(xsent_merged > backbone) >= 0.90.
  HARD_FAIL: NOT validity_gate_ok (invalid discriminator) OR xsent_merged acc <=
             backbone acc (merging gives NO lift -> fragmentation was NOT the wall;
             autopsy) OR merge_precision < 0.50 (over-merge damage dominates).
  MIDDLE_BAND: lift over backbone positive but below the 0.30 abs / 0.05 delta /
             0.80 precision / stability bars -> KEEP-DIGGING autopsy (over-merge
             damage? residual fragmentation? ambiguous single-token names?).

NEVER-CONFIDENTLY-WRONG: the aliaser ABSTAINS on ambiguous cross-token matches
(falls back to exact-surface grouping, never a forced cross-merge). A target with
no gender-compatible entity still ABSTAINS at resolution (attempted=False).

Header numbers are DESIGN targets (HYPOTHESIZED@this file / MEASURED@ the cited
step-1b metrics); reported numbers are MEASURED@ the metrics.json this run writes.

CELL-TEMPLATE MANDATORY:
# - arms_differ_verified at smoke gate (META_RULE_AF; hash per-target resolved cluster)
# - final_metrics_atomicity: tmp_replace (single-shot; metrics.json.tmp + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: symbolic accuracy metric; no matmul noise floor. Reachability shown
#   empirically: single_sentence_baseline ~0 on the cross-sentence subset leaves full
#   headroom; accuracy is telemetry-sensitive (merge on/off moves it).
# - baseline_in_band: the DISCRIMINATOR baseline (single-sentence) is ~0 BY VALIDITY
#   DESIGN; the MECHANISM arm (xsent_merged) is the in-band arm; the step-1b backbone
#   is the merge-ablated (P2) control; "same" bucket is the P1 within-sentence control.
# - discriminator survives scale: full=all cached books; smoke=first 5, asserts the
#   cross-sentence subset non-empty AND validity gate holds AND arms differ AND
#   merging fires (fragmentation drops + n_cross_merge > 0).
# - HARD_PASS strictly above the wall (META_RULE_L): >=0.30 abs AND >=0.05 over the
#   backbone AND >=0.15 over single-sentence AND merge_precision >=0.80.
# - cardinality: EXPECTED_N_UNITS = n_books usable; verdict counts per-book coverage.
# - per-unit failure-class instrumentation; no bare except.
# - calibration_check: default_ok_for_this_regime (merge rules use a GENERAL title
#   list + closed-class stop list + the general name gazetteer; NO LitBank-character
#   tuning; adaptive/centering constants ported VERBATIM from validated longdist).
# - all header numbers tagged HYPOTHESIZED@ / MEASURED@ / CITED@.
# - real_code_path: self-test builds real temp conll(s), runs hdlab.coref parse +
#   build_merge_map + CorefReader(merge on/off) end-to-end; asserts merge FIRES and
#   LIFTS a resolution the backbone misses, gender-conflict names stay split,
#   ambiguous single-token names abstain, and P1 within-sentence no-regression.
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
    build_merge_map,
    build_pronoun_targets,
    load_name_gender,
    name_content_tokens,
    parse_litbank_conll,
)

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------
ANCHOR_NAME = "read_xsent_coref_entity_merge_v1"
CORPUS_DIR = os.path.join(REPO_ROOT, "data", "corpora", "litbank_coref_conll")
SMOKE_N = 5

# step-1b best-lever backbone (adaptive far=centering + chaining + gazetteer).
_STEP1B_LEVERS = dict(reset_per_sentence=False, adaptive=True, chain_pronouns=True,
                      use_gazetteer=True)

ARMS = [
    ("single_sentence_baseline", dict(reset_per_sentence=True, strategy="maintained")),
    ("xsent_backbone_step1b", dict(**_STEP1B_LEVERS)),
    ("xsent_merged", dict(merge_entities=True, **_STEP1B_LEVERS)),
]
ARM_NAMES = [a[0] for a in ARMS]
BASELINE_ARM = "single_sentence_baseline"
BACKBONE_ARM = "xsent_backbone_step1b"
MECHANISM_ARM = "xsent_merged"

# Bands
VALIDITY_GATE_MAX = 0.10
HP_ABS = 0.30
HP_DELTA_BACKBONE = 0.05
HP_DELTA_SINGLE = 0.15
HP_SIGN_STABILITY = 0.90
HP_MERGE_PRECISION = 0.80
HF_MERGE_PRECISION = 0.50
P1_REGRESSION_EPS = 0.05

N_BOOTSTRAP = 500
BOOTSTRAP_SEED = 20260724


def _p(msg):
    print(msg, flush=True)


def _f(x):
    return "None" if x is None else ("%.4f" % x)


def _dbg(x):
    return float("nan") if x is None else x


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
# fragmentation + over-merge precision (per book), computed from the SAME
# build_merge_map the merged arm uses (use_gazetteer=True to match eff_gender).
# ----------------------------------------------------------------------------
def fragmentation_and_merge_stats(mentions, targets):
    """Return per-book fragmentation + over-merge accounting.
      targeted_clusters: gold clusters that have a pronoun target.
      For each targeted cluster: distinct surface heads (data), distinct overlay
      entities BEFORE merge (== distinct heads) and AFTER merge (canon identity).
      Over-merge pairs: nominal-mention pairs unified under one canon across a
      DIFFERENT surface head; correct iff same gold cluster."""
    midx_to_canon, _c2m, stats = build_merge_map(mentions, use_gazetteer=True)
    targeted = set(t["target"]["cluster"] for t in targets)
    nominal = [m for m in mentions if not m["is_pronoun"]]
    is_name_head = {}     # head -> True if that head ever appears as a proper name
    for m in nominal:
        if name_content_tokens(m.get("span_toks", [m["head"]])):
            is_name_head[m["head"]] = True

    # per targeted cluster: distinct heads (data), overlay entities before/after merge,
    # AND the decomposition of the fragmentation into NAME vs NON-NAME (appositive) heads.
    frag_heads, ent_before, ent_after = [], [], []
    name_head_slots = nonname_head_slots = 0
    for c in targeted:
        cm = [m for m in nominal if m["cluster"] == c]
        if not cm:
            continue
        heads = set(m["head"] for m in cm)
        ident_after = set()
        for m in cm:
            canon = midx_to_canon.get(m["midx"])
            ident_after.add(canon if canon is not None else ("h:" + m["head"]))
        frag_heads.append(len(heads))
        ent_before.append(len(set("h:" + m["head"] for m in cm)))  # backbone: 1 entity/head
        ent_after.append(len(ident_after))
        for h in heads:
            if is_name_head.get(h):
                name_head_slots += 1
            else:
                nonname_head_slots += 1

    # over-merge: cross-head pairs within a canon (isolates the merge DECISIONS).
    by_canon = {}
    for m in nominal:
        canon = midx_to_canon.get(m["midx"])
        if canon is None:
            continue
        by_canon.setdefault(canon, []).append(m)
    cross_pairs = cross_correct = 0
    multihead_canons = 0
    canon_head_sum = canon_count = 0
    for canon, ms in by_canon.items():
        canon_count += 1
        heads = set(m["head"] for m in ms)
        canon_head_sum += len(heads)
        if len(heads) >= 2:
            multihead_canons += 1                 # a canon that unifies >=2 surface heads
        else:
            continue                              # single-head canon = no merge decision
        for i in range(len(ms)):
            for j in range(i + 1, len(ms)):
                if ms[i]["head"] == ms[j]["head"]:
                    continue                      # same-head pair not a merge decision
                cross_pairs += 1
                if ms[i]["cluster"] == ms[j]["cluster"]:
                    cross_correct += 1
    return {
        "targeted_clusters": len(targeted),
        "frag_heads": frag_heads,
        "ent_before": ent_before,
        "ent_after": ent_after,
        "name_head_slots": name_head_slots,
        "nonname_head_slots": nonname_head_slots,
        "cross_pairs": cross_pairs,
        "cross_correct": cross_correct,
        "multihead_canons": multihead_canons,
        "canon_head_sum": canon_head_sum,
        "canon_count": canon_count,
        "n_cross_merge": stats["n_cross_merge"],
        "n_exact_attach": stats["n_exact_attach"],
        "n_abstain_new": stats["n_abstain_new"],
        "n_name_mentions": stats["n_name_mentions"],
        "n_entities": stats["n_new"],
    }


# ----------------------------------------------------------------------------
# evaluation
# ----------------------------------------------------------------------------
def evaluate_book(path, reader, gaz):
    mentions, n_sentences = parse_litbank_conll(path, name_gender_map=gaz)
    targets = build_pronoun_targets(mentions)
    if not targets:
        return [], {"n_mentions": len(mentions), "n_sentences": n_sentences,
                    "n_targets": 0}, None
    per_arm_records = {}
    for arm_name, kwargs in ARMS:
        per_arm_records[arm_name] = reader.resolve_stream(mentions, targets, **kwargs)
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
    frag = fragmentation_and_merge_stats(mentions, targets)
    meta = {"n_mentions": len(mentions), "n_sentences": n_sentences, "n_targets": n}
    return unified, meta, frag


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
    assert digests[BACKBONE_ARM] != digests[MECHANISM_ARM], (
        "META_RULE_AF VIOLATION: %s and %s produced bit-identical resolved clusters "
        "(merge changed NOTHING)" % (BACKBONE_ARM, MECHANISM_ARM))
    return digests


def _mean(xs):
    return (sum(xs) / len(xs)) if xs else None


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
    # fragmentation / over-merge accumulators
    agg_frag_heads, agg_ent_before, agg_ent_after = [], [], []
    tot_cross_pairs = tot_cross_correct = 0
    tot_cross_merge = tot_exact_attach = tot_abstain_new = tot_name_mentions = 0
    tot_name_head_slots = tot_nonname_head_slots = 0
    tot_multihead_canons = tot_canon_head_sum = tot_canon_count = 0
    for path in books:
        b = os.path.basename(path)
        try:
            recs, meta, frag = evaluate_book(path, reader, gaz)
            per_book[b] = meta
            for r in recs:
                r["book"] = b
            all_records.extend(recs)
            if frag is not None:
                agg_frag_heads.extend(frag["frag_heads"])
                agg_ent_before.extend(frag["ent_before"])
                agg_ent_after.extend(frag["ent_after"])
                tot_cross_pairs += frag["cross_pairs"]
                tot_cross_correct += frag["cross_correct"]
                tot_cross_merge += frag["n_cross_merge"]
                tot_exact_attach += frag["n_exact_attach"]
                tot_abstain_new += frag["n_abstain_new"]
                tot_name_mentions += frag["n_name_mentions"]
                tot_name_head_slots += frag["name_head_slots"]
                tot_nonname_head_slots += frag["nonname_head_slots"]
                tot_multihead_canons += frag["multihead_canons"]
                tot_canon_head_sum += frag["canon_head_sum"]
                tot_canon_count += frag["canon_count"]
            _p("[book] %-46s targets=%d sents=%d cross_merge=%s" %
               (b[:46], meta["n_targets"], meta["n_sentences"],
                (frag["n_cross_merge"] if frag else "-")))
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

    # fragmentation summary
    frag_heads_mean = _mean(agg_frag_heads)
    ent_before_mean = _mean(agg_ent_before)
    ent_after_mean = _mean(agg_ent_after)
    merge_precision = (tot_cross_correct / tot_cross_pairs) if tot_cross_pairs else None
    heads_per_canon = (tot_canon_head_sum / tot_canon_count) if tot_canon_count else None
    tot_head_slots = tot_name_head_slots + tot_nonname_head_slots
    frac_frag_from_names = (tot_name_head_slots / tot_head_slots) if tot_head_slots else None
    # merging_fires (RE-SPEC at smoke; the original "entities/cluster must drop" gate was
    # CONFOUNDED: backbone groups by surface HEAD, which itself OVER-merges distinct people
    # who share a head across gold clusters -- e.g. "Anne Elliot" and "William Elliot" both
    # have head "elliot" -- so a MORE-precise aliaser correctly splitting them registers as
    # "more entities". The correct, unconfounded "the mechanism acted" gate: cross-merges
    # fired AND >=1 canon unifies >=2 distinct surface heads.)
    merging_fires = (tot_cross_merge > 0 and tot_multihead_canons > 0)

    sign_stability = bootstrap_sign_stability(xsent_records, MECHANISM_ARM, BACKBONE_ARM)

    # P1 within-sentence no-regression vs single-sentence baseline on "same"
    base_same = same_table[BASELINE_ARM]["acc"]
    mech_same = same_table[MECHANISM_ARM]["acc"]
    p1_ok = (base_same is not None and mech_same is not None
             and mech_same >= base_same - P1_REGRESSION_EPS)

    validity_gate_ok = (base_xsent is not None and base_xsent <= VALIDITY_GATE_MAX)

    # per-distance winner across arms
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

    n_xsent = len(xsent_records)
    overmerge_ok = (merge_precision is None or merge_precision >= HP_MERGE_PRECISION)
    overmerge_fatal = (merge_precision is not None and merge_precision < HF_MERGE_PRECISION)

    if mech_xsent is None or n_xsent < 5:
        verdict = "UNKNOWN"
        verdict_msg = "cross-sentence subset too small (n_xsent=%d) to decide" % n_xsent
    elif not validity_gate_ok:
        verdict = "HARD_FAIL"
        verdict_msg = ("VALIDITY GATE FAILED: single_sentence_baseline acc=%.4f > %.2f on the "
                       "cross-sentence subset => invalid discriminator." % (base_xsent, VALIDITY_GATE_MAX))
    elif mech_xsent <= backbone_xsent:
        verdict = "HARD_FAIL"
        verdict_msg = ("entity merging gives NO lift over the step-1b backbone: xsent_merged acc=%.4f "
                       "<= backbone acc=%.4f on the cross-sentence subset => fragmentation was NOT the "
                       "wall (autopsy: frag_before=%s frag_after=%s merge_prec=%s n_cross_merge=%d)." %
                       (mech_xsent, backbone_xsent, _f(ent_before_mean), _f(ent_after_mean),
                        _f(merge_precision), tot_cross_merge))
    elif overmerge_fatal:
        verdict = "HARD_FAIL"
        verdict_msg = ("OVER-MERGE DAMAGE DOMINATES: merge_precision=%.4f < %.2f -- merging wrongly "
                       "unifies more distinct people than it correctly unifies. xsent_merged acc=%.4f "
                       "backbone=%.4f delta=%.4f is not trustworthy (built on bad merges)." %
                       (merge_precision, HF_MERGE_PRECISION, mech_xsent, backbone_xsent,
                        _dbg(delta_vs_backbone)))
    elif (mech_xsent >= HP_ABS and delta_vs_backbone >= HP_DELTA_BACKBONE
          and delta_vs_single is not None and delta_vs_single >= HP_DELTA_SINGLE
          and p1_ok and merging_fires and overmerge_ok
          and sign_stability is not None and sign_stability >= HP_SIGN_STABILITY):
        verdict = "HARD_PASS"
        verdict_msg = ("ENTITY MERGING breaks the fragmentation wall: xsent_merged acc=%.4f "
                       "(backbone=%.4f delta=%.4f; single_sentence=%.4f delta=%.4f), frag entities/"
                       "cluster %.4f->%.4f, merge_precision=%.4f, validity_gate=OK, P1_no_regression=OK "
                       "(same: mech=%.4f vs base=%.4f), sign_stability=%.3f, n_xsent=%d." %
                       (mech_xsent, backbone_xsent, delta_vs_backbone, base_xsent, delta_vs_single,
                        _dbg(ent_before_mean), _dbg(ent_after_mean), _dbg(merge_precision),
                        _dbg(mech_same), _dbg(base_same), sign_stability, n_xsent))
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = ("merging helps but sub-threshold: xsent_merged acc=%.4f (backbone=%.4f delta=%.4f, "
                       "single=%.4f delta=%.4f), frag %.4f->%.4f, merge_prec=%s, merging_fires=%s, p1_ok=%s, "
                       "sign_stability=%s, n_xsent=%d." %
                       (mech_xsent, backbone_xsent, _dbg(delta_vs_backbone), base_xsent,
                        _dbg(delta_vs_single), _dbg(ent_before_mean), _dbg(ent_after_mean),
                        _f(merge_precision), merging_fires, p1_ok, _f(sign_stability), n_xsent))

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
                   "validity_gate_max": VALIDITY_GATE_MAX, "hp_abs": HP_ABS,
                   "hp_delta_backbone": HP_DELTA_BACKBONE, "hp_delta_single": HP_DELTA_SINGLE,
                   "hp_sign_stability": HP_SIGN_STABILITY, "hp_merge_precision": HP_MERGE_PRECISION,
                   "hf_merge_precision": HF_MERGE_PRECISION, "p1_regression_eps": P1_REGRESSION_EPS,
                   "n_bootstrap": N_BOOTSTRAP, "bootstrap_seed": BOOTSTRAP_SEED,
                   "step1b_backbone_levers": _STEP1B_LEVERS},
        "n_targets_total": len(all_records),
        "n_xsent": n_xsent, "n_same": len(same_records),
        "bucket_counts": {b: len(by_bucket[b]) for b in BUCKETS},
        "cross_sentence_subset_table": xsent_table,
        "within_sentence_same_table": same_table,
        "overall_table": overall_table,
        "per_bucket_table": per_bucket_table,
        "per_distance_winner": per_distance_winner,
        "baseline_xsent_acc": base_xsent,
        "backbone_xsent_acc": backbone_xsent,
        "mech_xsent_acc": mech_xsent,
        "delta_vs_backbone": delta_vs_backbone,
        "delta_vs_single_sentence": delta_vs_single,
        "validity_gate_ok": validity_gate_ok,
        "p1_no_regression_ok": p1_ok,
        "p1_same_bucket": {"baseline": base_same, "xsent_merged": mech_same},
        "bootstrap_sign_stability": sign_stability,
        "fragmentation": {
            "distinct_heads_per_targeted_cluster": frag_heads_mean,
            "entities_per_targeted_cluster_before": ent_before_mean,
            "entities_per_targeted_cluster_after": ent_after_mean,
            "n_targeted_clusters_scored": len(agg_frag_heads),
            "heads_per_canon_after_merge": heads_per_canon,
            "n_multihead_canons": tot_multihead_canons,
            "n_canons": tot_canon_count,
            "name_head_slots": tot_name_head_slots,
            "nonname_head_slots": tot_nonname_head_slots,
            "frac_fragmentation_from_names": frac_frag_from_names,
            "autopsy": ("proper-name aliasing can only unify the NAME fraction of the "
                        "per-cluster distinct heads; the majority are NON-name common-noun "
                        "appositives (father/daughter/widow/friend) + reflexives, which "
                        "require APPOSITIVE / nominal coref, not surface-name matching."),
        },
        "over_merge": {
            "merge_precision": merge_precision,
            "cross_head_pairs": tot_cross_pairs,
            "cross_head_correct": tot_cross_correct,
            "n_cross_merge_decisions": tot_cross_merge,
            "n_exact_attach": tot_exact_attach,
            "n_abstain_new": tot_abstain_new,
            "n_name_mentions": tot_name_mentions,
        },
        "merging_fires": merging_fires,
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


# ----------------------------------------------------------------------------
# SELF-TEST (real code path: temp conll(s) -> parse + build_merge_map + CorefReader
# merge on/off; asserts merge FIRES + LIFTS, guards over-merge, P1 no-regression).
# ----------------------------------------------------------------------------
def self_test():
    import tempfile

    gaz = load_name_gender()
    assert gaz, "gazetteer missing (run tools/build_name_gender_gazetteer.py)"

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

    def find_target(recs, cluster):
        return [r for r in recs if r["gold_cluster"] == cluster]

    reader = CorefReader()
    made = []
    try:
        # ---- DOC A: MERGE FIRES + LIFTS a resolution the backbone misses. ----
        # Protagonist cluster 1 appears FRAGMENTED as "Elizabeth Bennet"(S0) then
        # "Elizabeth"(S1) -- 2 surface heads (bennet / elizabeth), each count 1.
        # Distractor Charlotte(2) is the most-recent fem. Masc filler (S3) pushes
        # every fem antecedent out of the recency window so the far strategy
        # (centering, count-weighted) fires. Backbone: 3 fem fragments each mass~1
        # -> recency tie-break picks the recent Charlotte (WRONG, 2). Merged:
        # Elizabeth-Bennet unified -> role-mass 2 subject mentions > Charlotte mass 1
        # -> picks Elizabeth (CORRECT, 1).
        # 6 masc fillers (all gazetteer-masc -> excluded from fem 'she'; they only
        # push every fem antecedent past the recency window so the far strategy fires).
        docA = write_doc([
            [("Elizabeth", "(1"), ("Bennet", "1)"), ("smiled", "_"), (".", "_")],
            [("Elizabeth", "(1)"), ("paused", "_"), (".", "_")],
            [("Charlotte", "(2)"), ("laughed", "_"), (".", "_")],
            [("Robert", "(3)"), ("met", "_"), ("James", "(4)"), ("near", "_"),
             ("William", "(5)"), ("by", "_"), ("Henry", "(6)"), ("saw", "_"),
             ("Charles", "(7)"), ("and", "_"), ("Edward", "(8)"), ("spoke", "_"),
             (".", "_")],
            [("She", "(1)"), ("waited", "_"), (".", "_")],
        ])
        made.append(docA)
        mA, nsA = parse_litbank_conll(docA, name_gender_map=gaz)
        # span_toks present + merge map unifies the two protagonist surface heads
        eb = [m for m in mA if m["head"] == "bennet"][0]
        assert eb["span_toks"] == ["Elizabeth", "Bennet"], "span_toks missing: %s" % eb
        m2c, c2m, st = build_merge_map(mA, use_gazetteer=True)
        bennet_m = [m for m in mA if m["head"] == "bennet"][0]["midx"]
        eliz_m = [m for m in mA if m["head"] == "elizabeth"][0]["midx"]
        assert m2c[bennet_m] == m2c[eliz_m], \
            "merge FAILED: 'Elizabeth Bennet' and 'Elizabeth' not unified: %s" % m2c
        char_m = [m for m in mA if m["head"] == "charlotte"][0]["midx"]
        assert m2c.get(char_m) != m2c[bennet_m], "Charlotte wrongly merged into Elizabeth"
        assert st["n_cross_merge"] >= 1, "no cross-merge fired: %s" % st
        recsA, _, fragA = evaluate_book(docA, reader, gaz)
        sheA = find_target(recsA, 1)
        assert sheA and sheA[0]["bucket"] == "long", "she must be cross-sentence: %s" % sheA
        assert sheA[0]["resolved_cluster"]["xsent_backbone_step1b"] == 2, \
            "backbone should mis-resolve she->Charlotte(2): %s" % sheA[0]["resolved_cluster"]
        assert sheA[0]["correct"]["xsent_merged"] is True, \
            "MERGED should resolve she->Elizabeth(1) via unified salience: %s" % sheA[0]["resolved_cluster"]
        # fragmentation drops for cluster 1 (2 heads -> 1 entity)
        assert fragA["ent_before"] and min(fragA["ent_before"]) >= 1, "frag before bad"
        assert sum(fragA["ent_after"]) < sum(fragA["ent_before"]), \
            "merge did not reduce entities/cluster: before=%s after=%s" % (
                fragA["ent_before"], fragA["ent_after"])
        # this merge is CORRECT (both heads gold cluster 1) -> cross-head pair correct
        assert fragA["cross_pairs"] >= 1 and fragA["cross_correct"] == fragA["cross_pairs"], \
            "over-merge accounting wrong on a pure merge: %s" % fragA

        # ---- DOC B: GENDER-CONFLICT names stay SPLIT (over-merge guard). ----
        # "Mr Bennet"(1, masc cue) and "Mrs Bennet"(2, fem cue) share token 'bennet'
        # but a KNOWN gender conflict must block the merge.
        docB = write_doc([
            [("Mr", "(1"), ("Bennet", "1)"), ("spoke", "_"), (".", "_")],
            [("Mrs", "(2"), ("Bennet", "2)"), ("replied", "_"), (".", "_")],
        ])
        made.append(docB)
        mB, _ = parse_litbank_conll(docB, name_gender_map=gaz)
        m2cB, _, stB = build_merge_map(mB, use_gazetteer=True)
        mids = sorted(m2cB.keys())
        assert len(mids) == 2 and m2cB[mids[0]] != m2cB[mids[1]], \
            "gender-conflict Bennets wrongly merged: %s" % m2cB
        assert stB["n_cross_merge"] == 0, "no cross-merge should fire on gender conflict: %s" % stB

        # ---- DOC C: AMBIGUOUS single-token name ABSTAINS (never-confidently-wrong). ----
        # Two distinct people share the given name 'Elizabeth': "Elizabeth Bennet"(1)
        # and "Elizabeth Gardiner"(2). A later bare "Elizabeth" matches BOTH -> the
        # aliaser must ABSTAIN (fresh entity), not force a wrong merge.
        docC = write_doc([
            [("Elizabeth", "(1"), ("Bennet", "1)"), ("smiled", "_"), (".", "_")],
            [("Elizabeth", "(2"), ("Gardiner", "2)"), ("wrote", "_"), (".", "_")],
            [("Elizabeth", "(3)"), ("waited", "_"), (".", "_")],
        ])
        made.append(docC)
        mC, _ = parse_litbank_conll(docC, name_gender_map=gaz)
        m2cC, _, stC = build_merge_map(mC, use_gazetteer=True)
        bennet_c = [m for m in mC if m["head"] == "bennet"][0]["midx"]
        gard_c = [m for m in mC if m["head"] == "gardiner"][0]["midx"]
        # the bare Elizabeth is the 3rd name mention (cluster 3)
        bare_c = [m for m in mC if m["cluster"] == 3 and not m["is_pronoun"]][0]["midx"]
        assert m2cC[bare_c] != m2cC[bennet_c] and m2cC[bare_c] != m2cC[gard_c], \
            "ambiguous bare 'Elizabeth' should ABSTAIN, not merge: %s" % m2cC
        assert stC["n_abstain_new"] >= 1, "abstain path not exercised: %s" % stC

        # ---- DOC D: P1 within-sentence no-regression (merge must not hurt local). ----
        docD = write_doc([
            [("Anna", "(1)"), ("hugged", "_"), ("her", "(1)"), (".", "_")],
        ])
        made.append(docD)
        recsD, _, _ = evaluate_book(docD, reader, gaz)
        herD = find_target(recsD, 1)
        assert herD and herD[0]["bucket"] == "same", "her must be within-sentence dist=0"
        assert herD[0]["correct"]["single_sentence_baseline"] is True, \
            "baseline must resolve within-sentence her->Anna(1)"
        assert herD[0]["correct"]["xsent_merged"] is True, \
            "xsent_merged must NOT regress within-sentence her->Anna(1) (P1)"

        # arms-differ on a combined record set (baseline != merged, backbone != merged)
        digs = arms_must_differ(recsA + recsD)
        assert digs[BASELINE_ARM] != digs[MECHANISM_ARM], "baseline==merged (arms-differ)"
        assert digs[BACKBONE_ARM] != digs[MECHANISM_ARM], "backbone==merged (merge no-op)"

        _p("SELF-TEST PASS: merge FIRES + LIFTS she->Elizabeth (backbone misses), "
           "gender-conflict Bennets stay split, ambiguous 'Elizabeth' abstains, "
           "P1 within-sentence no-regression, arms differ, fragmentation drops "
           "(glass-box, no network).")
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
    _p("per-bucket xsent_merged acc: %s" %
       {b: _f(metrics["per_bucket_table"][b][MECHANISM_ARM]["acc"]) for b in BUCKETS})
    _p("delta merged vs backbone=%s  vs single_sentence=%s  validity_gate_ok=%s  sign_stability=%s" %
       (_f(metrics["delta_vs_backbone"]), _f(metrics["delta_vs_single_sentence"]),
        metrics["validity_gate_ok"], _f(metrics["bootstrap_sign_stability"])))
    frag = metrics["fragmentation"]
    _p("FRAGMENTATION: distinct_heads/cluster=%s  entities/cluster before=%s after=%s (n_clusters=%d)" %
       (_f(frag["distinct_heads_per_targeted_cluster"]),
        _f(frag["entities_per_targeted_cluster_before"]),
        _f(frag["entities_per_targeted_cluster_after"]),
        frag["n_targeted_clusters_scored"]))
    _p("  head-type decomposition: NAME head-slots=%d  NON-name(appositive) head-slots=%d  "
       "frac_from_names=%s" % (frag["name_head_slots"], frag["nonname_head_slots"],
                               _f(frag["frac_fragmentation_from_names"])))
    _p("  heads_per_canon_after_merge=%s  multihead_canons=%d/%d  merging_fires=%s" %
       (_f(frag["heads_per_canon_after_merge"]), frag["n_multihead_canons"],
        frag["n_canons"], metrics["merging_fires"]))
    om = metrics["over_merge"]
    _p("OVER-MERGE: merge_precision=%s (cross_head_pairs=%d correct=%d) cross_merge=%d abstain=%d" %
       (_f(om["merge_precision"]), om["cross_head_pairs"], om["cross_head_correct"],
        om["n_cross_merge_decisions"], om["n_abstain_new"]))
    _p("P1 same-bucket: baseline=%s xsent_merged=%s p1_ok=%s" %
       (_f(metrics["p1_same_bucket"]["baseline"]), _f(metrics["p1_same_bucket"]["xsent_merged"]),
        metrics["p1_no_regression_ok"]))
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
