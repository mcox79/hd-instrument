#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
exp_read_xsent_coref_event_centrality_v1

INTEGRATION PAYOFF -- does the SITUATION-MODEL MEMORY feed back to lift COREF, with the
memory DRIVING the decision? Tests the untested load-bearing claim of the integration path
(the whole path assumes event/situation structure disambiguates reference -> a situation-
model dimension FEEDS BACK to lift the same-gender coref residual). ONE cell, THREE things:

  1. DECISION-LOAD-BEARING MEMORY (fixes the 29512 gap). 29512 honestly found the Cowan-4
     memory was a WRITE-ONLY WITNESS ("records_identical_hd_on_vs_off=True BY CONSTRUCTION").
     Here the coref resolve() actually QUERIES the event-bundle memory (hdlab.event_bundle
     EventBundleCodec bundles held in a Cowan-4 hdlab.situation_focus.ChunkedFocus; HD
     unbind+cleanup recovers the recent event participants + their roles) and lets it drive
     the same-gender tie-break. The cell reports the decision-change rate (query ON vs OFF);
     > 0 = the memory is decision-driving (the 29512 "identical by construction" is now FALSE).

  2. COREF LIFT, CONTROLLED (the fair, can-fail test). On the SAME same-gender residual set
     (backbone n_pool >= 2; the 29513/29514 wall definition, n~597), memory-query
     EVENT-CENTRALITY as the tie-breaker must BEAT BOTH:
       (a) the banked LOCAL-WINDOW reader (SceneProtagonistReader topical_local_fixed5,
           29514 subset acc 0.407 -- reused as the baseline arm) net, AND
       (b) a RECENCY-CENTRALITY control (IDENTICAL architecture + IDENTICAL HD queries; the
           ONE variable is the centrality WEIGHTING: event_role = AGENT>PATIENT role weight,
           no recency; recency = flat-role, recency-weighted). A win over the RECENCY control
           is the CRUX: it proves EVENT STRUCTURE (who drives the recent events) adds over
           mere recency. If event-centrality does NOT beat recency-centrality that is a CLEAN
           HONEST NEGATIVE (the lift collapses to the locality lever / the +0.036 protagonist
           secondary already banked in 29514; the integration thesis is weaker than hoped =
           Frontier-2 honest) -- reported plainly, NOT engineered into a pass.

  3. GLASS-BOX. The queried centrality is inspectable: which in-focus events, each role
     unbind's cleaned symbol + score, the per-candidate centrality, why the tie broke.

DISCRIMINATOR (can-fail): event_role can tie/lose to recency; difficulty ON = the same-gender
residual (>= 2 same-gender competitors); ONE variable = centrality signal (event-role vs
recency). REAL LitBank coref gold (25 books, the existing cross-sentence eval). Net-change
accounting (fixed vs broke), like the scene cell's +96.

PRE-REGISTERED bands (set BEFORE the final run; HYPOTHESIZED@this file):
  HARD_PASS  = validity + faithful hold AND memory is DECISION-DRIVING (decision-change > 0)
               AND event_centrality subset acc >= recency_centrality + CRUX_MARGIN (0.02)
               with sign_stability(event vs recency) >= 0.90 AND event_centrality >=
               local_window (0.407) - NO_REGRESS_EPS (0.01). = EVENT STRUCTURE adds over
               recency, the integration thesis SUPPORTED.
  MIDDLE_BAND = memory is DECISION-DRIVING (change > 0, the durable 29512-gap fix) BUT
               event_centrality does NOT beat recency by the margin (collapses to
               recency/locality) = HONEST NEGATIVE on the integration thesis; the decision-
               driving memory wiring is the durable win regardless.
  HARD_FAIL  = validity fails, OR faithful fails (off != local_window bit-for-bit), OR the
               memory is NOT decision-driving (decision-change == 0 = the 29512 gap NOT
               fixed), OR (full mode) the local_window / backbone plateau does not reproduce.

Numbers tagged MEASURED@disk / HYPOTHESIZED@this file / CITED@prior; reported numbers are
MEASURED@ the metrics.json this run writes.

CELL-TEMPLATE MANDATORY:
# - arms_differ_verified at gate (META_RULE_AF): off_faithful == local_window bit-for-bit;
#   event_centrality != off_faithful (the memory query changed >= 1 decision). event vs
#   recency divergence is the EMPIRICAL crux (reported, not asserted).
# - final_metrics_atomicity: tmp_replace (single-shot; metrics.json.tmp + os.replace).
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: symbolic accuracy metric over genuine HD unbind+cleanup; no matmul noise floor
#   on accuracy. Reachability shown empirically: single_sentence ~0 leaves headroom; the
#   HD in-focus round-trip fidelity is reported (memory is genuine, not decorative).
# - baseline_in_band: DISCRIMINATOR baseline (single_sentence) ~0 by validity design;
#   local_window/backbone are in-band plateau controls; off_faithful == local_window.
# - discriminator survives scale: full = 25 books; smoke = first 5, asserts subset non-empty
#   AND the memory query fires (decision-change > 0) AND validity holds AND arms differ.
# - HARD_PASS strictly above the recency control by CRUX_MARGIN (META_RULE_L) + sign-stable.
# - cardinality: EXPECTED_N_UNITS = n_books usable; verdict counts per-book coverage.
# - per-unit failure-class instrumentation; no bare except.
# - calibration_check: default_ok_for_this_regime (overlay/centering constants ported
#   VERBATIM; AGENT_W/PATIENT_W a general role prominence; local-window size = the 29514
#   banked baseline; n_dim=4096 round-trips in-focus events cleanly -- verified, not tuned).
# - real_code_path: self-test builds a real temp conll, runs parse + all readers end-to-end,
#   asserts off_faithful == local_window bit-for-bit AND the memory query changes a decision
#   AND event_role differs from recency on a constructed structure-vs-recency case.
# - progress_logging: print_flush_true (wall < 90s; heartbeat EXEMPT).
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
from hdlab.scene_segment import SceneProtagonistReader, parse_conll_sentences  # noqa: E402
from hdlab.event_centrality_coref import (  # noqa: E402
    EVENT_N_DIM,
    AGENT_W,
    PATIENT_W,
    EventCentralityReader,
)

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------
ANCHOR_NAME = "read_xsent_coref_event_centrality_v1"
CORPUS_DIR = os.path.join(REPO_ROOT, "data", "corpora", "litbank_coref_conll")
SMOKE_N = 5
LOCAL_WINDOW = 5           # fixed local-window (sentences) = the banked 29514 baseline
RANDOM_SEED = 20260724
MEM_SEED = 7
GLASS_BOX_LIMIT = 12       # keep up to N decision-change examples for the glass-box report

# Cited plateaus (MEASURED@disk).
LOCAL_WINDOW_PLATEAU = 0.40704  # MEASURED@data/exp_read_xsent_coref_scene_protagonist_v1/metrics.json:same_gender_subset_acc.topical_local_fixed5
BACKBONE_PLATEAU = 0.24623      # MEASURED@data/exp_read_xsent_coref_scene_protagonist_v1/metrics.json:same_gender_subset_acc.backbone

# Bands (pre-registered; HYPOTHESIZED@this file).
VALIDITY_GATE_MAX = 0.10
PLATEAU_REPRO_EPS = 0.03        # |local_window subset - 0.407| and |backbone - 0.246| (full)
CRUX_MARGIN = 0.02              # event_centrality >= recency_centrality + this (the crux)
HP_SIGN_STABILITY = 0.90
NO_REGRESS_EPS = 0.01           # event_centrality >= local_window - this (no regress vs 0.407)
N_BOOTSTRAP = 2000
BOOTSTRAP_SEED = 20260724

# arms
ARM_NAMES = [
    "single_sentence_baseline", "backbone", "local_window", "off_faithful",
    "recency_centrality", "event_centrality",
]
BASELINE_ARM = "single_sentence_baseline"
BACKBONE_ARM = "backbone"
LOCAL_WINDOW_ARM = "local_window"       # the banked 29514 baseline + faithful target
FAITHFUL_ARM = "off_faithful"           # EventCentralityReader query OFF -> must == local_window
RECENCY_ARM = "recency_centrality"      # control (identical arch, recency weighting)
MECHANISM_ARM = "event_centrality"      # the mechanism (event-role weighting)


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


def fixed_window_scenes(n_sents, size):
    """Scene id = sentence // size (fixed-size chunks = the 29514 locality baseline)."""
    return [i // size for i in range(n_sents)]


# ----------------------------------------------------------------------------
# per-book arm evaluation
# ----------------------------------------------------------------------------
SUP_KW = dict(suppress_generic=True, use_nonref=True, use_struct=True,
              chain_pronouns=True, use_gazetteer=True)


def _resolve_arms(mentions, targets, sents, reader_coref, reader_sup, reader_scene,
                  reader_ec, glass_accum):
    n_sents = len(sents)
    sid_fixed = fixed_window_scenes(n_sents, LOCAL_WINDOW)
    out = {}
    # validity baseline (within-sentence only)
    out["single_sentence_baseline"] = reader_coref.resolve_stream(
        mentions, targets, reset_per_sentence=True, strategy="maintained")
    # backbone plateau (SuppressReader sup_both)
    out["backbone"] = reader_sup.resolve_stream(mentions, targets, **SUP_KW)
    # LOCAL-WINDOW baseline (the banked 29514 topical_local_fixed5, subset ~0.407)
    out["local_window"] = reader_scene.resolve_stream(
        mentions, targets, prefer_topical=True, per_scene=True, scene_ids=sid_fixed,
        topical_mode="rolemass", **SUP_KW)
    # off_faithful: EventCentralityReader with the memory query OFF -> must == local_window
    out["off_faithful"] = reader_ec.resolve_stream(
        mentions, targets, scene_ids=sid_fixed, topical_mode="rolemass",
        query_memory=False, **SUP_KW)
    # RECENCY-CENTRALITY control (identical arch + queries; recency weighting)
    out["recency_centrality"] = reader_ec.resolve_stream(
        mentions, targets, scene_ids=sid_fixed, topical_mode="rolemass",
        query_memory=True, centrality_mode="recency", **SUP_KW)
    # EVENT-CENTRALITY mechanism (event-role weighting) + glass-box capture
    out["event_centrality"] = reader_ec.resolve_stream(
        mentions, targets, scene_ids=sid_fixed, topical_mode="rolemass",
        query_memory=True, centrality_mode="event_role",
        glass_box_limit=GLASS_BOX_LIMIT, **SUP_KW)
    if getattr(reader_ec, "last_glass", None):
        for g in reader_ec.last_glass:
            if len(glass_accum) < GLASS_BOX_LIMIT:
                glass_accum.append(g)
    rt = getattr(reader_ec, "last_rt", (0, 0))
    return out, {"n_sents": n_sents, "rt_ok": rt[0], "rt_total": rt[1]}


def evaluate_book(path, reader_coref, reader_sup, reader_scene, reader_ec, gaz, glass_accum):
    mentions, n_sentences = parse_litbank_conll(path, name_gender_map=gaz)
    sents = parse_conll_sentences(path)
    if len(sents) != n_sentences:
        raise RuntimeError("SENTENCE_MISALIGN: parse_litbank=%d parse_conll_sentences=%d"
                           % (n_sentences, len(sents)))
    targets = build_pronoun_targets(mentions)
    if not targets:
        return [], {"n_mentions": len(mentions), "n_sentences": n_sentences, "n_targets": 0,
                    "rt_ok": 0, "rt_total": 0}
    per_arm, meta0 = _resolve_arms(mentions, targets, sents, reader_coref, reader_sup,
                                   reader_scene, reader_ec, glass_accum)
    n = len(targets)
    unified = []
    for i in range(n):
        b = per_arm[ARM_NAMES[0]][i]
        u = {"sent_dist": b["sent_dist"], "bucket": b["bucket"],
             "gold_cluster": b["gold_cluster"],
             "correct": {}, "attempted": {}, "resolved_cluster": {},
             "n_pool": {}, "mem_changed": {}}
        for name in ARM_NAMES:
            r = per_arm[name][i]
            u["correct"][name] = r["correct"]
            u["attempted"][name] = r["attempted"]
            u["resolved_cluster"][name] = (-1 if r["resolved_cluster"] is None
                                           else r["resolved_cluster"])
            u["n_pool"][name] = r.get("n_pool", -1)
            u["mem_changed"][name] = bool(r.get("mem_changed", False))
        unified.append(u)
    meta = {"n_mentions": len(mentions), "n_sentences": n_sentences, "n_targets": n,
            "rt_ok": meta0["rt_ok"], "rt_total": meta0["rt_total"]}
    return unified, meta


# ----------------------------------------------------------------------------
# metrics helpers
# ----------------------------------------------------------------------------
def acc_on(records, arm):
    if not records:
        return None
    return sum(r["correct"][arm] for r in records) / len(records)


def bucketize(records):
    out = {b: [] for b in BUCKETS}
    for r in records:
        out[r["bucket"]].append(r)
    return out


def subset_acc(records, idx, arm):
    if not idx:
        return None
    return sum(records[i]["correct"][arm] for i in idx) / len(idx)


def fixed_broke(records, idx, mech, base):
    fx = sum(1 for i in idx if records[i]["correct"][mech] and not records[i]["correct"][base])
    bk = sum(1 for i in idx if records[i]["correct"][base] and not records[i]["correct"][mech])
    return fx, bk


def decision_change_rate(records, idx, arm, ref):
    """Fraction of subset targets where arm's resolved cluster differs from ref (query OFF)."""
    if not idx:
        return None
    ch = sum(1 for i in idx
             if records[i]["resolved_cluster"][arm] != records[i]["resolved_cluster"][ref])
    return ch / len(idx)


def paired_sign_stability(records, idx, arm_mech, arm_base,
                          n_boot=N_BOOTSTRAP, seed=BOOTSTRAP_SEED):
    if len(idx) < 2:
        return None
    rng = np.random.default_rng(seed)
    mech = np.array([records[i]["correct"][arm_mech] for i in idx], dtype=float)
    base = np.array([records[i]["correct"][arm_base] for i in idx], dtype=float)
    n = len(idx)
    pos = 0
    for _ in range(n_boot):
        b = rng.integers(0, n, size=n)
        if mech[b].mean() - base[b].mean() > 0:
            pos += 1
    return pos / n_boot


def arms_must_differ(all_records):
    digests = {}
    for name in ARM_NAMES:
        vec = bytes()
        for r in all_records:
            vec += int(r["resolved_cluster"][name]).to_bytes(4, "big", signed=True)
        digests[name] = hashlib.sha256(vec).hexdigest()
    # FAITHFULNESS: the memory-OFF arm must reproduce the local-window baseline bit-for-bit.
    assert digests[FAITHFUL_ARM] == digests[LOCAL_WINDOW_ARM], (
        "FAITHFULNESS VIOLATION: %s must reproduce %s bit-for-bit (memory-query is the ONE "
        "isolated variable)" % (FAITHFUL_ARM, LOCAL_WINDOW_ARM))
    # MECHANISM FIRES: the memory query must change >= 1 decision vs OFF (else it is the
    # 29512 write-only-witness = NOT decision-driving).
    assert digests[MECHANISM_ARM] != digests[FAITHFUL_ARM], (
        "META_RULE_AF / DECISION-DRIVING VIOLATION: %s bit-identical to %s -- the memory "
        "query changed NO decision (write-only witness, the 29512 gap not fixed)"
        % (MECHANISM_ARM, FAITHFUL_ARM))
    return digests


def autopsy(records, idx):
    """Keep-digging autopsy: net fix/broke of event vs local_window and event vs recency;
    residual breaks the mechanism introduces."""
    fx_lw, bk_lw = fixed_broke(records, idx, MECHANISM_ARM, LOCAL_WINDOW_ARM)
    fx_rc, bk_rc = fixed_broke(records, idx, MECHANISM_ARM, RECENCY_ARM)
    # items the mechanism BROKE relative to local_window (was right, now wrong) -- for per-item
    breaks = [i for i in idx
              if records[i]["correct"][LOCAL_WINDOW_ARM] and not records[i]["correct"][MECHANISM_ARM]]
    return {"event_vs_localwindow_fixed": fx_lw, "event_vs_localwindow_broke": bk_lw,
            "event_vs_recency_fixed": fx_rc, "event_vs_recency_broke": bk_rc,
            "event_net_vs_localwindow": fx_lw - bk_lw,
            "event_net_vs_recency": fx_rc - bk_rc,
            "n_breaks_vs_localwindow": len(breaks)}


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
    reader_scene = SceneProtagonistReader()
    reader_ec = EventCentralityReader(n_dim=EVENT_N_DIM, mem_seed=MEM_SEED)
    all_records = []
    per_book = {}
    book_failures = []
    glass_accum = []
    rt_ok_total = 0
    rt_total_total = 0
    for path in books:
        b = os.path.basename(path)
        try:
            recs, meta = evaluate_book(path, reader_coref, reader_sup, reader_scene,
                                       reader_ec, gaz, glass_accum)
            per_book[b] = meta
            rt_ok_total += meta.get("rt_ok", 0)
            rt_total_total += meta.get("rt_total", 0)
            for r in recs:
                r["book"] = b
            all_records.extend(recs)
            _p("[book] %-46s targets=%d sents=%d rt=%d/%d"
               % (b[:46], meta["n_targets"], meta["n_sentences"],
                  meta.get("rt_ok", 0), meta.get("rt_total", 0)))
        except Exception as e:  # noqa: BLE001 -- per-book failure-class recorded, not silent
            book_failures.append({"book": b, "failure_class": type(e).__name__,
                                  "msg": str(e)[:160]})
            _p("[book-FAIL] %s : %s: %s" % (b, type(e).__name__, str(e)[:120]))

    if not all_records:
        raise RuntimeError("NO_TARGETS: parsed %d books, 0 pronoun targets" % len(books))

    digests = arms_must_differ(all_records)

    by_bucket = bucketize(all_records)
    xsent_records = by_bucket["plus1"] + by_bucket["plus2"] + by_bucket["long"]
    n_xsent = len(xsent_records)

    # same-gender-competition subset = backbone pool has >=2 surviving specific candidates
    # (the 29513/29514 wall definition: n_pool>=2 under the backbone).
    idx_subset = [i for i, r in enumerate(xsent_records) if r["n_pool"][BACKBONE_ARM] >= 2]

    overall_xsent = {name: acc_on(xsent_records, name) for name in ARM_NAMES}
    subset_tab = {name: subset_acc(xsent_records, idx_subset, name) for name in ARM_NAMES}

    base_val = overall_xsent[BASELINE_ARM]
    lw_sub = subset_tab[LOCAL_WINDOW_ARM]
    off_sub = subset_tab[FAITHFUL_ARM]
    bk_sub = subset_tab[BACKBONE_ARM]
    rec_sub = subset_tab[RECENCY_ARM]
    ev_sub = subset_tab[MECHANISM_ARM]

    # decision-change rate (memory query ON=event/recency vs OFF=off_faithful) on the subset.
    dc_event = decision_change_rate(xsent_records, idx_subset, MECHANISM_ARM, FAITHFUL_ARM)
    dc_recency = decision_change_rate(xsent_records, idx_subset, RECENCY_ARM, FAITHFUL_ARM)
    # cross-check via the per-target mem_changed flag on the event arm
    mem_changed_rate = (sum(xsent_records[i]["mem_changed"][MECHANISM_ARM] for i in idx_subset)
                        / len(idx_subset)) if idx_subset else None

    crux_delta = None if (ev_sub is None or rec_sub is None) else ev_sub - rec_sub
    stability = paired_sign_stability(xsent_records, idx_subset, MECHANISM_ARM, RECENCY_ARM)
    regress_vs_lw = (ev_sub is not None and lw_sub is not None
                     and ev_sub < lw_sub - NO_REGRESS_EPS)

    aut = autopsy(xsent_records, idx_subset)
    rt_fidelity = (rt_ok_total / rt_total_total) if rt_total_total else None

    # gates
    validity_ok = (base_val is not None and base_val <= VALIDITY_GATE_MAX)
    faithful_ok = (off_sub is not None and lw_sub is not None and off_sub == lw_sub
                   and digests[FAITHFUL_ARM] == digests[LOCAL_WINDOW_ARM])
    decision_driving = (dc_event is not None and dc_event > 0.0)
    lw_plateau_ok = (lw_sub is not None and abs(lw_sub - LOCAL_WINDOW_PLATEAU) <= PLATEAU_REPRO_EPS)
    bk_plateau_ok = (bk_sub is not None and abs(bk_sub - BACKBONE_PLATEAU) <= PLATEAU_REPRO_EPS)
    plateau_gate = (lw_plateau_ok and bk_plateau_ok) if run_mode == "full" else True

    crux_pass = (crux_delta is not None and crux_delta >= CRUX_MARGIN
                 and stability is not None and stability >= HP_SIGN_STABILITY
                 and not regress_vs_lw)

    # verdict
    if n_xsent < 5 or len(idx_subset) < 5:
        verdict = "UNKNOWN"
        verdict_msg = ("xsent/subset too small (n_xsent=%d, n_subset=%d)"
                       % (n_xsent, len(idx_subset)))
    elif not validity_ok:
        verdict = "HARD_FAIL"
        verdict_msg = ("VALIDITY GATE FAILED: single_sentence baseline xsent acc=%.4f > %.2f"
                       % (base_val, VALIDITY_GATE_MAX))
    elif not faithful_ok:
        verdict = "HARD_FAIL"
        verdict_msg = ("FAITHFULNESS FAILED: off_faithful subset=%.4f vs local_window=%.4f "
                       "(digest_eq=%s); the memory-query is not the isolated variable."
                       % (off_sub, lw_sub, digests[FAITHFUL_ARM] == digests[LOCAL_WINDOW_ARM]))
    elif not plateau_gate:
        verdict = "HARD_FAIL"
        verdict_msg = ("PLATEAU REPRO FAILED: local_window=%.4f (cited 0.407) backbone=%.4f "
                       "(cited 0.246), eps=%.3f" % (lw_sub, bk_sub, PLATEAU_REPRO_EPS))
    elif not decision_driving:
        verdict = "HARD_FAIL"
        verdict_msg = ("MEMORY NOT DECISION-DRIVING: decision-change rate (event vs query-off) "
                       "= %.4f == 0. The event-bundle memory is a write-only witness (the "
                       "29512 gap is NOT fixed); the query drives no coref decision."
                       % (dc_event if dc_event is not None else float("nan")))
    elif crux_pass:
        verdict = "HARD_PASS"
        verdict_msg = (
            "INTEGRATION PAYOFF: the memory is DECISION-DRIVING (decision-change event=%.4f "
            "recency=%.4f; the 29512 write-only-witness gap is FIXED) AND EVENT STRUCTURE adds "
            "over recency: event_centrality subset=%.4f vs recency_centrality=%.4f "
            "(crux delta=+%.4f, sign_stability=%.3f) AND event >= local_window %.4f - %.2f "
            "(no regress). Net vs local_window: fixed=%d broke=%d (net %+d). Net vs recency: "
            "fixed=%d broke=%d (net %+d). HD in-focus round-trip fidelity=%s (genuine memory)."
            % (dc_event, dc_recency, ev_sub, rec_sub, crux_delta, stability, lw_sub,
               NO_REGRESS_EPS, aut["event_vs_localwindow_fixed"],
               aut["event_vs_localwindow_broke"], aut["event_net_vs_localwindow"],
               aut["event_vs_recency_fixed"], aut["event_vs_recency_broke"],
               aut["event_net_vs_recency"], _f(rt_fidelity)))
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            "HONEST NEGATIVE on the integration thesis, DURABLE WIN on the memory wiring: the "
            "memory IS DECISION-DRIVING (decision-change event=%.4f recency=%.4f; the 29512 "
            "write-only-witness gap is FIXED -- the query genuinely drives resolve()), BUT "
            "EVENT STRUCTURE does NOT beat recency: event_centrality subset=%.4f vs "
            "recency_centrality=%.4f (crux delta=%+.4f, sign_stability=%s, needs >=+%.2f). "
            "=> the lift collapses to the recency/locality lever (banked 29514 local_window "
            "%.4f) / the +0.036 protagonist secondary; event-role adds no separable signal on "
            "this gold. Net vs local_window: fixed=%d broke=%d (net %+d). HD round-trip "
            "fidelity=%s. Integration thesis WEAKER than hoped (Frontier-2 honest)."
            % (dc_event, dc_recency, ev_sub, rec_sub,
               (crux_delta if crux_delta is not None else float("nan")), _f(stability),
               CRUX_MARGIN, lw_sub, aut["event_vs_localwindow_fixed"],
               aut["event_vs_localwindow_broke"], aut["event_net_vs_localwindow"],
               _f(rt_fidelity)))

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
        "config": {"arms": ARM_NAMES, "baseline_arm": BASELINE_ARM,
                   "local_window_arm": LOCAL_WINDOW_ARM, "faithful_arm": FAITHFUL_ARM,
                   "recency_arm": RECENCY_ARM, "mechanism_arm": MECHANISM_ARM,
                   "local_window": LOCAL_WINDOW, "n_dim": EVENT_N_DIM,
                   "agent_w": AGENT_W, "patient_w": PATIENT_W, "mem_seed": MEM_SEED,
                   "local_window_plateau_cited": LOCAL_WINDOW_PLATEAU,
                   "backbone_plateau_cited": BACKBONE_PLATEAU,
                   "bands": {"validity_gate_max": VALIDITY_GATE_MAX,
                             "plateau_repro_eps": PLATEAU_REPRO_EPS,
                             "crux_margin": CRUX_MARGIN,
                             "hp_sign_stability": HP_SIGN_STABILITY,
                             "no_regress_eps": NO_REGRESS_EPS},
                   "n_bootstrap": N_BOOTSTRAP, "bootstrap_seed": BOOTSTRAP_SEED,
                   "pass_criterion": "memory decision-driving (decision-change>0) AND "
                                     "event_centrality >= recency_centrality + 0.02 "
                                     "(sign_stability>=0.90) AND event >= local_window - 0.01"},
        "n_targets_total": len(all_records), "n_xsent": n_xsent,
        "n_same_gender_subset": len(idx_subset),
        "bucket_counts": {b: len(by_bucket[b]) for b in BUCKETS},
        "overall_xsent_acc": overall_xsent,
        "same_gender_subset_acc": subset_tab,
        "crux_delta_event_minus_recency": crux_delta,
        "sign_stability_event_vs_recency": stability,
        "regress_vs_local_window": regress_vs_lw,
        "decision_change_event_vs_off": dc_event,
        "decision_change_recency_vs_off": dc_recency,
        "mem_changed_rate_event": mem_changed_rate,
        "hd_roundtrip_fidelity_infocus": rt_fidelity,
        "hd_roundtrip_ok": rt_ok_total, "hd_roundtrip_total": rt_total_total,
        "autopsy": aut,
        "glass_box_examples": glass_accum,
        "validity_ok": validity_ok, "faithful_ok": faithful_ok,
        "decision_driving": decision_driving,
        "local_window_plateau_ok": lw_plateau_ok, "backbone_plateau_ok": bk_plateau_ok,
        "crux_pass": crux_pass,
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


# ----------------------------------------------------------------------------
# markers / crash-diagnostic (atomic)
# ----------------------------------------------------------------------------
def _write_start_marker(out_dir, run_mode, expected_n):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n, "host": platform.node()}
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(out_dir, "_start_marker.json"))


def _write_crash_metrics(out_dir, exc):
    os.makedirs(out_dir, exist_ok=True)
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__,
            "elapsed_s": 0.0, "anchor_name": ANCHOR_NAME,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat()}
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


# ----------------------------------------------------------------------------
# SELF-TEST (real code path: constructed docs + real temp conll)
# ----------------------------------------------------------------------------
def _mk(head, cluster, is_pron, sent, midx, gender, role_rank, number="singular",
        name_gender=None):
    return {"head": head, "cluster": cluster, "is_pronoun": is_pron,
            "sent_idx": sent, "midx": midx, "gender": gender, "number": number,
            "name_gender": name_gender, "sent_role_rank": role_rank,
            "is_subject": (role_rank == 0), "span_toks": [head]}


def self_test():
    # (0) module formula self-tests (memory round-trip, query-off==parent, event!=recency).
    from hdlab.event_centrality_coref import _run_all_selftests
    _run_all_selftests()
    _p("[self-test] event_centrality_coref module self-tests OK")

    # (1) FAITHFULNESS + DECISION-DRIVING on a constructed structure-vs-recency doc.
    # anna is AGENT of the 3 older events (protagonist); bella AGENT of the newest event.
    mentions = []
    mi = 0
    mentions.append(_mk("anna", 1, False, 0, mi, "fem", 0, name_gender="fem")); mi += 1
    mentions.append(_mk("anna", 1, False, 1, mi, "fem", 0, name_gender="fem")); mi += 1
    mentions.append(_mk("anna", 1, False, 2, mi, "fem", 0, name_gender="fem")); mi += 1
    mentions.append(_mk("bella", 2, False, 2, mi, "fem", 1, name_gender="fem")); mi += 1
    mentions.append(_mk("bella", 2, False, 3, mi, "fem", 0, name_gender="fem")); mi += 1
    mentions.append(_mk("she", 1, True, 4, mi, "fem", 0)); mi += 1     # gold=anna
    targets = build_pronoun_targets(mentions)
    n_sents = max(m["sent_idx"] for m in mentions) + 1
    scene_ids = fixed_window_scenes(n_sents, LOCAL_WINDOW)

    scene = SceneProtagonistReader()
    ec = EventCentralityReader(n_dim=EVENT_N_DIM, mem_seed=MEM_SEED)
    lw = scene.resolve_stream(mentions, targets, prefer_topical=True, per_scene=True,
                              scene_ids=scene_ids, topical_mode="rolemass", **SUP_KW)
    off = ec.resolve_stream(mentions, targets, scene_ids=scene_ids, topical_mode="rolemass",
                            query_memory=False, **SUP_KW)
    assert lw[0]["resolved_cluster"] == off[0]["resolved_cluster"], "faithfulness drift"
    ev = ec.resolve_stream(mentions, targets, scene_ids=scene_ids, topical_mode="rolemass",
                           query_memory=True, centrality_mode="event_role",
                           glass_box_limit=4, **SUP_KW)
    rc = ec.resolve_stream(mentions, targets, scene_ids=scene_ids, topical_mode="rolemass",
                           query_memory=True, centrality_mode="recency", **SUP_KW)
    assert ev[0]["resolved_head"] == "anna", "event_role must pick protagonist anna"
    assert rc[0]["resolved_head"] == "bella", "recency must pick newest-event bella"
    assert any(r["mem_changed"] for r in rc), "recency query must change the decision (driving)"
    _p("[self-test] faithfulness (off==local_window) + decision-driving (recency changed the "
       "pick) + event_role->anna / recency->bella")

    # (2) REAL code path: temp conll -> parse + all readers end-to-end via evaluate_book.
    import tempfile

    def tok(tidx, word, coref="_"):
        return "selftest\t0\t%d\t%s\t_\t_\t_\t_\t_\t_\t_\t_\t%s" % (tidx, word, coref)

    lines = ["#begin document (selftest); part 0"]
    lines += [tok(0, "Anna", "(1)"), tok(1, "summoned"), tok(2, "the"),
              tok(3, "servants", "(2)"), tok(4, "."), ""]
    lines += [tok(0, "She", "(1)"), tok(1, "left"), tok(2, "."), ""]
    with tempfile.NamedTemporaryFile("w", suffix=".conll", delete=False,
                                     encoding="utf-8") as tf:
        tf.write("\n".join(lines) + "\n")
        tmp_path = tf.name
    try:
        gaz = load_name_gender()
        mentions2, n_sent = parse_litbank_conll(tmp_path, name_gender_map=gaz)
        sents2 = parse_conll_sentences(tmp_path)
        assert len(sents2) == n_sent == 2, "sentence alignment: %d vs %d" % (len(sents2), n_sent)
        glass = []
        recs, meta = evaluate_book(tmp_path, CorefReader(), SuppressReader(),
                                   SceneProtagonistReader(),
                                   EventCentralityReader(n_dim=EVENT_N_DIM, mem_seed=MEM_SEED),
                                   gaz, glass)
        for r in recs:
            assert r["resolved_cluster"][FAITHFUL_ARM] == r["resolved_cluster"][LOCAL_WINDOW_ARM], \
                "FAITHFULNESS: off_faithful must reproduce local_window bit-for-bit"
        ss = acc_on(recs, BASELINE_ARM)
        assert ss is not None and ss <= VALIDITY_GATE_MAX, "validity gate: %.3f" % ss
        _p("[self-test] real code path: temp conll parse + all 6 arms via evaluate_book + "
           "faithfulness + validity OK")
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    _p("[self-test] PASS (glass-box, no network)")
    return 0


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
    _p("SAME-GENDER subset (n=%d) acc by arm:" % metrics["n_same_gender_subset"])
    st = metrics["same_gender_subset_acc"]
    for name in ARM_NAMES:
        _p("  %-26s subset=%s  overall_xsent=%s"
           % (name, _f(st[name]), _f(metrics["overall_xsent_acc"][name])))
    _p("decision_change event=%s recency=%s | crux(event-recency)=%s stability=%s"
       % (_f(metrics["decision_change_event_vs_off"]),
          _f(metrics["decision_change_recency_vs_off"]),
          _f(metrics["crux_delta_event_minus_recency"]),
          _f(metrics["sign_stability_event_vs_recency"])))
    _p("hd_roundtrip_fidelity_infocus=%s (%d/%d)"
       % (_f(metrics["hd_roundtrip_fidelity_infocus"]),
          metrics["hd_roundtrip_ok"], metrics["hd_roundtrip_total"]))
    _p("autopsy=%s" % json.dumps(metrics["autopsy"]))
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
