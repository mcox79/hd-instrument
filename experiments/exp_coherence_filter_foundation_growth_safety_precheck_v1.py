"""COHERENCE-FILTER FOUNDATION-GROWTH SAFETY PRE-CHECK: is the coherence-gate confidence SAFE to filter
consolidation-eligible extractions, and does FILTERED foundation-growth beat UNFILTERED on a real corpus?

QUESTION (per the cross-document compounding drill notes/research_cross_document_compounding_consolidation_
viability_2026-07-19.md -- the "Cheap decisive test (do this FIRST)" + Predictions A/B and the FAIR can-fail
growth test):
  Before growing the foundation by reading more early-reading text, TWO things must hold or growth is unsafe
  (consolidating wrong knowledge measurably HURTS future reading -- Kendeou & van den Broek):
    STEP 0 (the hard gate, fires at smoke): is the coherence-gate confidence signal POSITIVELY correlated
      with gold correctness on the ALREADY-EXISTING patient-precision eval set? If it is null or anti-
      correlated (the CCL failure pattern -- a systematically-wrong signal that entrenches the extractor's
      own mistakes), that is a DECISIVE EARLY KILL: do NOT proceed to a naive growth run; the headline is
      "current filter unsafe for consolidation".
    STEP 1-2 (only meaningful if the signal is usable): does applying the coherence-gate filter to the
      reader's raw foundation-growth extractions raise the CONSOLIDATED-set precision meaningfully above the
      UNFILTERED growth precision (the ~0.44 noisy raw-reader wall / the 0.557 stacked reader), at acceptable
      recall retention -- i.e. is FILTERED growth net-cleaner than UNFILTERED growth?

CO-TRAINING DECORRELATION (Prediction B, the drill's Angle-4 load-bearing constraint): a second filtering
  view helps only if its errors are DECORRELATED from the coherence gate's own errors (Blum-Mitchell). We
  add a genuinely different feature family -- REDUNDANCY (same (verb,patient) extracted from >=2 separate
  sentences) crossed with WordNet-grounded LEXICAL plausibility (is the patient a concrete affected/created/
  perceived thing, an EXTERNAL resource NOT derived from the parser's own structural cues) -- and MEASURE
  whether it is less correlated with the gate's errors than the gate is with itself.

THE THREE CONFIDENCE SIGNALS (per raw reader extraction, over the real early-reading corpus):
  sigA = the EXTRACTOR'S OWN objecthood score (LCCP learned logistic sigmoid(w.x)); the MAXIMALLY-entangled
    signal (built from the exact structural cues that produce the errors) -- the CCL-risk baseline.
  sigB = the COHERENCE-GATE schema-fit: situation-model-conditioned selectional coherence of the patient vs
    the running verb-slot centroid, blended with the verb<->patient association (the existing gate's Score-1).
  sigC = the SECOND VIEW (co-training): WordNet concrete-thing lexical plausibility + cross-sentence
    redundancy. Chosen SPECIFICALLY to NOT be built from the parser's own construction cues.

CORPUS (real early-reading text OUTSIDE the 34-item castle slice; difficulty genuinely ON):
  McGuffey Third Reader lessons L04,L05,L07,L08,L09,L10,L12 (114 sentences; 100 pos + 180 nopat gold items;
  16 frame-ambiguous verbs) via data/gold_mcguffey_lccp_argstruct_v1.json -- the same independent single-
  annotator gold the reader-precision work uses. Gold correctness = patient-lens match_pos (a kept (v_lemma,
  patient) matches a gold POS relation) -- the exact eval the "0.557" reader-precision number is measured on.

ARMS (foundation-growth; ONE VARIABLE = coherence-gate filter ON vs OFF; SAME extractions + SAME gold):
  UNFILTERED_RAW    : consolidate ALL raw-reader (arm-A) extractions (the ~0.44 unfiltered-growth noise wall).
  FILTERED_RAW      : arm-A extractions the coherence gate ACCEPTS (drop content-incoherent; DEFER mid-band).
  FILTERED_RAW_2VIEW: arm-A + gate-accept AND second-view lexical-plausible (the co-training double filter).
  UNFILTERED_LCCP   : the LCCP structural stack (arm-C) kept set, unfiltered (the structural baseline -- the
                       session's "structural-beats-semantic" reference; does the SEMANTIC gate add anything?).
  FILTERED_LCCP     : arm-C + coherence gate (does the semantic gate lift the already-structural stack?).

MEASURED (decisive): STEP-0 point-biserial + Spearman correlation of each signal vs gold correctness (multi-
  seed for the seed-dependent extractor signal); the B-vs-C error decorrelation (Prediction B); per growth
  arm precision / recall / recall-retention; the residual-FP class split of what the gate keeps wrong.

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (G1) REAL baseline = UNFILTERED_RAW (all reader extractions consolidated) AND UNFILTERED_LCCP (the
       structural stack), measured live -- NOT a strawman.
  (G2) baseline_in_band: 0.05 < UNFILTERED_RAW precision < 0.95 (a real, un-saturated growth wall).
  (G3) CAN-FAIL-BOTH-WAYS: STEP-0 corr can be positive (usable) OR null/negative (EARLY KILL); the growth
       filter can RAISE precision (lift) OR fail-to-lift / over-prune recall (noise-bound). Both reachable.
  (G4) discriminator fires: the coherence gate DROPS >0 raw extractions AND the kept set differs from
       unfiltered (arms must differ).
  (G5) ONE VARIABLE: gate ON vs OFF at a fixed operating point (raw / lccp); identical extractions + gold.

VERDICT BANDS (pre-registered):
  STEP-0 confidence-usable  := coherence-gate sigB point-biserial corr with correctness >= +0.15.
  STEP-0 confidence-unsafe  := sigB corr <= +0.05 (null) OR < 0 (anti-correlated, the CCL pattern).
  growth-lift               := FILTERED_RAW precision - UNFILTERED_RAW precision >= 0.05 (real margin) AND
                               FILTERED_RAW precision > 0.557 (beats the current stacked reader) AND
                               FILTERED_RAW recall retention (vs UNFILTERED_RAW) >= 0.60.
  HARD_PASS_FILTERED_GROWTH_SAFE_AND_CLEANER: STEP-0 confidence-usable AND growth-lift.
    => the coherence gate is a SAFE, net-cleaner consolidation filter; read-more-text growth can proceed.
  HARD_FAIL_CONFIDENCE_UNSAFE: STEP-0 confidence-unsafe.
    => current filter recurs CCL one level up; do NOT grow with it. Redirect = find a decorrelated view.
  HARD_FAIL_GROWTH_NOISE_BOUND: STEP-0 usable BUT growth filter fails to lift (FILTERED_RAW - UNFILTERED_RAW
    < 0.03) OR over-prunes (recall retention < 0.50).
    => growth is precision-bound at the wall; redirect = precision-first before compounding.
  MIDDLE_BAND: partial (usable signal, 0.03 <= lift < 0.05, or between the recall bars).

BRAIN-CHECK (pre-registered; outcome NOT pre-assumed): the brain does NOT compound freely from noisy
  knowledge -- erroneous prior knowledge HURTS subsequent comprehension (Kendeou & van den Broek), and the
  fix is an explicit conflict-detection/filter-before-consolidate step (van den Broek co-activation). So a
  filter is brain-mandated. WHERE a same-limit may hit: if the gate's confidence is entangled with the
  extractor's own error mode (glass-box signals built from shared feature families correlate their errors --
  the drill's open substrate-specific risk), filtering entrenches rather than removes the systematic error
  -- same failure the human misconception literature documents. usable+decorrelated => safe; entangled =>
  the honest redirect is a genuinely independent view or a cleaner base reader.

COMPUTE ARCHITECTURE (mandatory): class (b) sequential-CPU with justification -- LCCP logistic train (~few
  hundred candidates x 60 epochs) x 3 seeds + a few hundred GloVe cosines + WordNet lookups over 114
  sentences; wall < ~4 min. Foreground local-to-completion (NO queue; NO push; NO remote-persist). Storage:
  no_storage (extraction-precision + correlation measurement). Determinism: OMP/MKL/OPENBLAS=1, fixed int
  seeds, deterministic hashlib + deterministic WordNet synset order; no salted builtin hash / list(set).

CELL-TEMPLATE MANDATORY (LOCAL foreground measurement; NOT queue-dispatched):
- arms_differ_verified at smoke (UNFILTERED vs FILTERED kept-set hashes differ)
- final_metrics_atomicity: tmp_replace (os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- baseline_in_band at smoke (0.05 < UNFILTERED_RAW precision < 0.95)
- discriminator fires at smoke (gate drops >0; kept sets differ)
- multi-seed (7,13,19) for the seed-dependent extractor signal + arm-C composition
- formula self-tests: point-biserial vs a hand-computed example; correctness-label sanity; determinism guard
- scaffold-free witness: a real coherent-but-WRONG extraction the gate keeps (localizes the residual) + a
  concrete true patient the lexical view accepts + an abstract mis-attachment it rejects
- deterministic seeding; numbers tagged MEASURED@ (printed at run) / CITED@ (0.557 stacked reader; 0.44
  unfiltered growth 07-18)
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_learned_argstruct_parser_lccp_independent_gold_v1 as LCCP  # noqa: E402

ANCHOR_NAME = "coherence_filter_foundation_growth_safety_precheck_v1"
CITED_STACKED_READER_PRECISION = 0.557  # CITED@ stacked reader patient-lens (LCCP+arg/adjunct+quotative, atoms 29342/29345)
CITED_UNFILTERED_GROWTH_PRECISION = 0.44  # CITED@ 07-18 read-to-grow strict foundation-growth precision
GATE_THR_KEEP = 0.15   # CITED@ existing coherence-gate cfg (calibration_check: default_ok_for_this_regime -- same corpus family)
GATE_THR_DEFER = 0.03  # CITED@ existing coherence-gate cfg
SEEDS = [7, 13, 19]

# WordNet concrete-thing lexnames: a direct affected/created/perceived PATIENT is typically a concrete thing.
# Abstract senses (cognition/communication/feeling/time/event/state) are far more often oblique/adjunct
# mis-attachments. This is an EXTERNAL lexical resource, NOT derived from the parser's structural cues.
CONCRETE_LEXNAMES = {"noun.artifact", "noun.object", "noun.person", "noun.animal", "noun.food",
                     "noun.plant", "noun.body", "noun.location", "noun.substance", "noun.possession",
                     "noun.shape", "noun.group"}

_WN = None
_WN_OK = False
_WN_ERR = None
try:
    from nltk.corpus import wordnet as _wnmod
    _ = _wnmod.synsets("table")
    _WN = _wnmod
    _WN_OK = True
except Exception as _e:  # NOT BaseException; explicit, non-silent (flagged in metrics)
    _WN_ERR = f"{type(_e).__name__}: {str(_e)[:200]}"

# Pronoun patients are valid objects but carry no GloVe/WordNet content -- lexical view abstains (None).
_PRONOUN = {"i", "you", "he", "she", "we", "they", "me", "him", "her", "us", "them", "it",
            "myself", "himself", "herself", "themselves"}


# ----------------------------------------------------------------------------------------------
# Signal C.1 -- WordNet concrete-thing lexical plausibility of a patient (external resource).
# ----------------------------------------------------------------------------------------------
def lexical_plausible(p):
    """Return (flag, abstain): flag=1 if p has a concrete-thing WordNet noun sense; abstain=True if the
    lexical view has no opinion (pronoun / OOV -- excluded from lexical correlation)."""
    t = (p or "").lower().strip(".,'\"!?;:")
    if t in _PRONOUN:
        return None, True   # valid object, no lexical content -> abstain
    if not _WN_OK:
        return None, True
    ns = _WN.synsets(t, pos="n")
    if not ns:
        return None, True   # OOV noun -> abstain
    # dominant (first, most frequent) sense decides; deterministic synset order.
    return (1 if ns[0].lexname() in CONCRETE_LEXNAMES else 0), False


# ----------------------------------------------------------------------------------------------
# Build the raw-extraction eval set + the three confidence signals, per seed.
# ----------------------------------------------------------------------------------------------
def build_eval(cfg, seed):
    """Return records over ALL raw-reader (arm-A) extractions with correctness + sigA/sigB/sigC, plus the
    arm-A / arm-C kept sets and gold. Deterministic given seed."""
    lcfg = dict(slice_lessons=cfg["slice_lessons"], sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=60,
                keep_thr=0.45, subcat_thr=0.42, heldout_frac=0.25, k_constructions=4, seed=seed)
    order, sent_text, reader_svo = LCCP.load_slice_and_reader(cfg["slice_lessons"])
    gold, gold_meta = LCCP.load_gold(cfg["slice_lessons"])

    toks = set()
    for sid in order:
        for v, a, p in reader_svo[sid]:
            toks.update([p, LCCP.lemma_verb(v)])
    for sid, rec in gold.items():
        for g in rec["pos"]:
            toks.update([g["patient"], g["v"]])
    glove = LCCP.load_glove_for(toks)

    decisions, artifacts, subcat_dec, ho, seen, inst_groups, w = LCCP.run_arms(
        order, reader_svo, sent_text, glove, lcfg, seed)
    w = np.array(w, dtype=np.float64)

    # flat raw extractions in READING ORDER (arm A), with structural features.
    flat = []
    for sid in order:
        toks_s = LCCP.tokenize(sent_text[sid])
        for tup in reader_svo[sid]:
            feat, _pos = LCCP.candidate_features(toks_s, tup[0], tup[2])
            flat.append({"sid": sid, "v": LCCP.lemma_verb(tup[0]), "p": tup[2], "tup": tup,
                         "feat": np.array(feat, dtype=np.float64)})

    # cross-sentence redundancy of (v_lemma, patient) across the corpus (Signal C.2).
    pair_sids = defaultdict(set)
    for r in flat:
        pair_sids[(r["v"], r["p"])].add(r["sid"])

    # situation-model schema-fit accumulator (Signal B): running verb-slot + global centroids from
    # STRUCTURALLY-clean patients (post-verbal, not prep-governed, not funcword), scored BEFORE self-append.
    slot_vecs = defaultdict(list)
    global_vecs = []

    def schema_fit(v, p, slot, glob):
        pv = glove.get(p)
        if pv is None:
            return None
        if slot:
            ref = np.mean(np.stack(slot, 0), 0)
        elif glob:
            ref = np.mean(np.stack(glob, 0), 0)
        else:
            return None
        n = np.linalg.norm(ref)
        ref = ref / (n if n > 1e-8 else 1.0)
        base = float(np.dot(pv, ref))
        vv = glove.get(v)
        if vv is not None:
            base = 0.7 * base + 0.3 * float(np.dot(pv, vv))  # verb<->patient selectional blend
        return base

    records = []
    for r in flat:
        sid, v, p, feat = r["sid"], r["v"], r["p"], r["feat"]
        rec = gold.get(sid, {"pos": [], "nopat": set(), "pos_verbs": set()})
        correct = 1 if LCCP.match_pos(v, p, rec["pos"]) is not None else 0
        sigA = LCCP.score_cand(w, feat)                       # extractor's own objecthood (entangled)
        sigB = schema_fit(v, p, slot_vecs[v], global_vecs)   # coherence-gate schema-fit (None if OOV/no-ctx)
        lex_flag, lex_abstain = lexical_plausible(p)
        redun = len(pair_sids[(v, p)])
        records.append({"sid": sid, "v": v, "p": p, "tup": r["tup"], "correct": correct,
                        "sigA": float(sigA), "sigB": (float(sigB) if sigB is not None else None),
                        "lex_flag": lex_flag, "lex_abstain": bool(lex_abstain), "redun": int(redun),
                        "postv_clean": bool(feat[2] >= 0.5 and feat[3] < 0.5 and feat[4] < 0.5)})
        # accumulate centroid from structurally-clean patients only (bootstrap schema)
        if feat[2] >= 0.5 and feat[3] < 0.5 and feat[4] < 0.5:
            pv = glove.get(p)
            if pv is not None:
                slot_vecs[v].append(pv)
                global_vecs.append(pv)

    return {"order": order, "sent_text": sent_text, "reader_svo": reader_svo, "gold": gold,
            "gold_meta": gold_meta, "decisions": decisions, "records": records, "w": w.tolist(),
            "glove": glove, "n_reader": len(flat)}


# ----------------------------------------------------------------------------------------------
# Correlation statistics (point-biserial = Pearson with a binary; Spearman = Pearson of ranks).
# ----------------------------------------------------------------------------------------------
def pearson(x, y):
    x = np.asarray(x, dtype=np.float64); y = np.asarray(y, dtype=np.float64)
    if len(x) < 3:
        return None
    xd = x - x.mean(); yd = y - y.mean()
    dn = float(np.sqrt((xd * xd).sum() * (yd * yd).sum()))
    if dn < 1e-12:
        return None
    return float((xd * yd).sum() / dn)


def _rank(a):
    a = np.asarray(a, dtype=np.float64)
    order = np.argsort(a, kind="mergesort")  # stable, deterministic
    ranks = np.empty(len(a), dtype=np.float64)
    ranks[order] = np.arange(len(a), dtype=np.float64)
    # average ranks for ties (deterministic)
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a[order[j + 1]] == a[order[i]]:
            j += 1
        if j > i:
            avg = (i + j) / 2.0
            for k in range(i, j + 1):
                ranks[order[k]] = avg
        i = j + 1
    return ranks


def spearman(x, y):
    if len(x) < 3:
        return None
    return pearson(_rank(x), _rank(y))


def corr_signal_vs_correct(records, signal_key, only_nonnull=True, only_nonabstain=False):
    xs, ys = [], []
    for r in records:
        v = r[signal_key]
        if signal_key == "lex_flag":
            if r["lex_abstain"] or v is None:
                continue
        elif v is None:
            if only_nonnull:
                continue
        xs.append(float(v)); ys.append(float(r["correct"]))
    return {"point_biserial": pearson(xs, ys), "spearman": spearman(xs, ys), "n": len(xs),
            "base_rate_correct": round(float(np.mean(ys)), 4) if ys else None}


# ----------------------------------------------------------------------------------------------
# Growth arms: gate accept/defer/drop on the raw extractions; precision/recall of the consolidated set.
# ----------------------------------------------------------------------------------------------
def gate_decision(r):
    """Coherence-gate accept/defer/drop for a raw extraction. Unscorable (no schema-fit) -> ACCEPT (not
    enough context to punish, exactly the existing gate's w_min behaviour). Returns 'accept'|'defer'|'drop'."""
    s = r["sigB"]
    if s is None:
        return "accept"
    if s >= GATE_THR_KEEP:
        return "accept"
    if s >= GATE_THR_DEFER:
        return "defer"
    return "drop"


def precision_recall(kept_tups, gold):
    """kept_tups: list of (sid, v_lemma, p). Precision over kept; recall over gold pos coverage."""
    n_gold = sum(len(rec["pos"]) for rec in gold.values())
    tp, covered, n_pred = 0, set(), 0
    for sid, v, p in kept_tups:
        n_pred += 1
        rec = gold.get(sid, {"pos": []})
        g = LCCP.match_pos(v, p, rec["pos"])
        if g is not None:
            tp += 1
            covered.add((sid, rec["pos"].index(g)))
    precision = tp / n_pred if n_pred else 0.0
    recall = len(covered) / n_gold if n_gold else 0.0
    return {"precision": round(precision, 4), "recall": round(recall, 4), "n_pred": n_pred, "tp": tp,
            "n_gold": n_gold, "n_gold_covered": len(covered)}


def growth_arms(ev):
    records = ev["records"]; gold = ev["gold"]
    decisions = ev["decisions"]

    raw_tups = [(r["sid"], r["v"], r["p"]) for r in records]
    gate = {id(r): gate_decision(r) for r in records}
    filt_raw = [(r["sid"], r["v"], r["p"]) for r in records if gate[id(r)] == "accept"]
    n_dropped = sum(1 for r in records if gate[id(r)] == "drop")
    n_deferred = sum(1 for r in records if gate[id(r)] == "defer")
    # double filter: gate-accept AND second-view lexical-plausible (abstain -> keep, no opinion).
    filt_raw_2 = [(r["sid"], r["v"], r["p"]) for r in records
                  if gate[id(r)] == "accept" and (r["lex_abstain"] or r["lex_flag"] == 1)]

    # LCCP structural stack (arm C) kept set, unfiltered + gated.
    c_tups = [(sid, LCCP.lemma_verb(t[0]), t[2]) for sid, t in decisions["C_lccp"]]
    # map arm-C tuples to their sigB via a records lookup (by sid,v,p); recompute gate on the same signal.
    sigB_by = {}
    for r in records:
        sigB_by.setdefault((r["sid"], r["v"], r["p"]), r)
    def gate_c(sid, v, p):
        r = sigB_by.get((sid, v, p))
        return gate_decision(r) if r is not None else "accept"
    filt_c = [(sid, v, p) for (sid, v, p) in c_tups if gate_c(sid, v, p) == "accept"]

    arms = {
        "UNFILTERED_RAW": precision_recall(raw_tups, gold),
        "FILTERED_RAW": precision_recall(filt_raw, gold),
        "FILTERED_RAW_2VIEW": precision_recall(filt_raw_2, gold),
        "UNFILTERED_LCCP": precision_recall(c_tups, gold),
        "FILTERED_LCCP": precision_recall(filt_c, gold),
    }
    # residual FP class split of what FILTERED_RAW keeps wrong (localizes the coherent-but-wrong residual).
    resid = defaultdict(int)
    for sid, v, p in filt_raw:
        rec = gold.get(sid, {"pos": [], "nopat": set(), "pos_verbs": set()})
        if LCCP.match_pos(v, p, rec["pos"]) is not None:
            continue
        if v in rec["nopat"]:
            resid["subcat_fp"] += 1
        elif v in rec["pos_verbs"]:
            resid["within_frame_fp"] += 1
        else:
            resid["spurious_verb_fp"] += 1
    arms["_gate_stats"] = {"n_dropped": n_dropped, "n_deferred": n_deferred,
                           "filtered_raw_residual_fp": dict(resid)}
    arms["_kept_sets"] = {"UNFILTERED_RAW": raw_tups, "FILTERED_RAW": filt_raw,
                          "FILTERED_RAW_2VIEW": filt_raw_2, "UNFILTERED_LCCP": c_tups, "FILTERED_LCCP": filt_c}
    return arms


# ----------------------------------------------------------------------------------------------
# B-vs-C error decorrelation (Prediction B / co-training condition).
# ----------------------------------------------------------------------------------------------
def error_decorrelation(records):
    """Over extractions where BOTH sigB and the lexical view have an opinion: correlation of the two signal
    values overall AND restricted to INCORRECT extractions (where filters must disagree to help). Lower
    correlation on the incorrect subset => the views are error-decorrelated (co-training helps)."""
    both, both_wrong = [], []
    for r in records:
        if r["sigB"] is None or r["lex_abstain"] or r["lex_flag"] is None:
            continue
        both.append((r["sigB"], float(r["lex_flag"]), r["correct"]))
        if r["correct"] == 0:
            both_wrong.append((r["sigB"], float(r["lex_flag"])))
    all_corr = pearson([b[0] for b in both], [b[1] for b in both]) if len(both) >= 3 else None
    wrong_corr = pearson([b[0] for b in both_wrong], [b[1] for b in both_wrong]) if len(both_wrong) >= 3 else None
    # fraction of INCORRECT extractions each view catches, and the fraction BOTH miss (shared blind spot).
    n_wrong = len(both_wrong)
    gate_catches = sum(1 for s, _ in both_wrong if s < GATE_THR_KEEP)
    lex_catches = sum(1 for _, l in both_wrong if l == 0)
    both_miss = sum(1 for s, l in both_wrong if s >= GATE_THR_KEEP and l == 1)
    return {"n_both_opinion": len(both), "n_both_opinion_wrong": n_wrong,
            "signal_corr_all": all_corr, "signal_corr_on_incorrect": wrong_corr,
            "gate_catches_wrong_frac": round(gate_catches / n_wrong, 4) if n_wrong else None,
            "lex_catches_wrong_frac": round(lex_catches / n_wrong, 4) if n_wrong else None,
            "both_miss_wrong_frac": round(both_miss / n_wrong, 4) if n_wrong else None}


# ----------------------------------------------------------------------------------------------
# Verdict.
# ----------------------------------------------------------------------------------------------
def build_verdict(step0_sigB_pb, arms_mean):
    """step0_sigB_pb: mean point-biserial of coherence-gate sigB vs correctness (across seeds).
    arms_mean: dict arm -> {precision, recall} means across seeds."""
    unf = arms_mean["UNFILTERED_RAW"]; fil = arms_mean["FILTERED_RAW"]
    lift = fil["precision"] - unf["precision"]
    recall_ret = (fil["recall"] / unf["recall"]) if unf["recall"] > 0 else 0.0
    beats_stacked = fil["precision"] > CITED_STACKED_READER_PRECISION

    confidence_usable = (step0_sigB_pb is not None and step0_sigB_pb >= 0.15)
    confidence_unsafe = (step0_sigB_pb is not None and (step0_sigB_pb <= 0.05 or step0_sigB_pb < 0.0))
    growth_lift = (lift >= 0.05 and beats_stacked and recall_ret >= 0.60)
    growth_fail = (lift < 0.03 or recall_ret < 0.50)

    if confidence_unsafe:
        verdict = "HARD_FAIL_CONFIDENCE_UNSAFE"
    elif confidence_usable and growth_lift:
        verdict = "HARD_PASS_FILTERED_GROWTH_SAFE_AND_CLEANER"
    elif confidence_usable and growth_fail:
        verdict = "HARD_FAIL_GROWTH_NOISE_BOUND"
    else:
        verdict = "MIDDLE_BAND"
    return {"verdict": verdict, "step0_sigB_point_biserial": step0_sigB_pb,
            "confidence_usable": bool(confidence_usable), "confidence_unsafe": bool(confidence_unsafe),
            "growth_lift_precision": round(lift, 4), "filtered_raw_recall_retention": round(recall_ret, 4),
            "filtered_raw_beats_stacked_0557": bool(beats_stacked),
            "unfiltered_raw_precision": unf["precision"], "filtered_raw_precision": fil["precision"]}


def kept_hash(tups):
    items = sorted(f"{sid}|{v}|{p}" for sid, v, p in tups)
    return hashlib.sha256("\n".join(items).encode()).hexdigest()[:16]


def scaffold_free_witness(ev):
    records = ev["records"]; gold = ev["gold"]
    # a coherent-but-wrong extraction the gate KEEPS (high schema-fit but gold-incorrect -> localizes the
    # residual to the parse, not the gate).
    coherent_wrong = None
    for r in records:
        if r["correct"] == 0 and r["sigB"] is not None and r["sigB"] >= GATE_THR_KEEP:
            coherent_wrong = [r["sid"], r["v"], r["p"], round(r["sigB"], 3)]
            break
    # a concrete TRUE patient the lexical view accepts.
    lex_true = None
    for r in records:
        if r["correct"] == 1 and (not r["lex_abstain"]) and r["lex_flag"] == 1:
            lex_true = [r["sid"], r["v"], r["p"]]
            break
    # an abstract mis-attachment the lexical view rejects.
    lex_reject_wrong = None
    for r in records:
        if r["correct"] == 0 and (not r["lex_abstain"]) and r["lex_flag"] == 0:
            lex_reject_wrong = [r["sid"], r["v"], r["p"]]
            break
    return {"coherent_but_wrong_gate_keeps": coherent_wrong, "concrete_true_patient_lex_accepts": lex_true,
            "abstract_wrong_lex_rejects": lex_reject_wrong,
            "witness": "PASS" if (coherent_wrong is not None and lex_reject_wrong is not None) else "PARTIAL"}


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def cfg_smoke():
    return dict(slice_lessons=["L04", "L05"])


def cfg_full():
    return dict(slice_lessons=["L04", "L05", "L07", "L08", "L09", "L10", "L12"])


def _mean_std(vals):
    v = [x for x in vals if x is not None]
    if not v:
        return None, None
    return round(float(np.mean(v)), 4), round(float(np.std(v)), 4)


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))

    per_seed = []
    for seed in SEEDS:
        ev = build_eval(cfg, seed)
        corrs = {
            "sigA_objecthood": corr_signal_vs_correct(ev["records"], "sigA"),
            "sigB_coherence_gate": corr_signal_vs_correct(ev["records"], "sigB"),
            "sigC_lexical": corr_signal_vs_correct(ev["records"], "lex_flag"),
            "sigC_redundancy": corr_signal_vs_correct(ev["records"], "redun"),
        }
        arms = growth_arms(ev)
        decorr = error_decorrelation(ev["records"])
        per_seed.append({"seed": seed, "corrs": corrs, "arms": arms, "decorr": decorr, "ev": ev})

    # aggregate across seeds
    def arm_mean(arm, key):
        m, s = _mean_std([ps["arms"][arm][key] for ps in per_seed])
        return m

    arms_mean = {}
    for arm in ["UNFILTERED_RAW", "FILTERED_RAW", "FILTERED_RAW_2VIEW", "UNFILTERED_LCCP", "FILTERED_LCCP"]:
        arms_mean[arm] = {
            "precision": arm_mean(arm, "precision"), "recall": arm_mean(arm, "recall"),
            "precision_std": _mean_std([ps["arms"][arm]["precision"] for ps in per_seed])[1],
            "n_pred_mean": arm_mean(arm, "n_pred"),
        }

    step0 = {}
    for sk in ["sigA_objecthood", "sigB_coherence_gate", "sigC_lexical", "sigC_redundancy"]:
        pb_m, pb_s = _mean_std([ps["corrs"][sk]["point_biserial"] for ps in per_seed])
        sp_m, sp_s = _mean_std([ps["corrs"][sk]["spearman"] for ps in per_seed])
        step0[sk] = {"point_biserial_mean": pb_m, "point_biserial_std": pb_s,
                     "spearman_mean": sp_m, "spearman_std": sp_s,
                     "n_mean": _mean_std([ps["corrs"][sk]["n"] for ps in per_seed])[0]}

    decorr0 = per_seed[0]["decorr"]  # B/C signals are seed-independent (deterministic); report seed-0.
    decorr_seed_invariant = all(
        (ps["decorr"]["signal_corr_on_incorrect"] == decorr0["signal_corr_on_incorrect"]) for ps in per_seed)

    sigB_pb = step0["sigB_coherence_gate"]["point_biserial_mean"]
    vd = build_verdict(sigB_pb, arms_mean)

    # discriminator + arms-differ + baseline-in-band (on seed-0 kept sets)
    ks0 = per_seed[0]["arms"]["_kept_sets"]
    h_unf = kept_hash(ks0["UNFILTERED_RAW"]); h_fil = kept_hash(ks0["FILTERED_RAW"])
    assert h_unf != h_fil, "META_RULE_AF: UNFILTERED_RAW == FILTERED_RAW (gate no-op)"
    gate_stats0 = per_seed[0]["arms"]["_gate_stats"]
    discriminator_fires = bool(gate_stats0["n_dropped"] > 0 and h_unf != h_fil)
    baseline_in_band = bool(0.05 < arms_mean["UNFILTERED_RAW"]["precision"] < 0.95)

    witness = scaffold_free_witness(per_seed[0]["ev"])
    elapsed = time.perf_counter() - t0
    v = vd["verdict"]

    unf = arms_mean["UNFILTERED_RAW"]; fil = arms_mean["FILTERED_RAW"]; f2 = arms_mean["FILTERED_RAW_2VIEW"]
    ulc = arms_mean["UNFILTERED_LCCP"]; flc = arms_mean["FILTERED_LCCP"]
    b = step0["sigB_coherence_gate"]; a = step0["sigA_objecthood"]; c = step0["sigC_lexical"]
    msg = (f"{v} | slice={'+'.join(cfg['slice_lessons'])} seeds={SEEDS} n_reader~{per_seed[0]['ev']['n_reader']} "
           f"| STEP0 corr(vs correct) pb: sigB_gate={b['point_biserial_mean']}+-{b['point_biserial_std']} "
           f"sigA_extractor={a['point_biserial_mean']} sigC_lex={c['point_biserial_mean']} "
           f"| usable={vd['confidence_usable']} unsafe={vd['confidence_unsafe']} "
           f"| GROWTH UNFILT_RAW P={unf['precision']} R={unf['recall']} -> FILT_RAW P={fil['precision']} "
           f"R={fil['recall']} (2view P={f2['precision']}) | LCCP UNFILT P={ulc['precision']} FILT P={flc['precision']} "
           f"| lift={vd['growth_lift_precision']:+.4f} Rret={vd['filtered_raw_recall_retention']} "
           f"beats0557={vd['filtered_raw_beats_stacked_0557']} "
           f"| decorr(B,C)_on_wrong={decorr0['signal_corr_on_incorrect']} both_miss={decorr0['both_miss_wrong_frac']} "
           f"| gate drop/def={gate_stats0['n_dropped']}/{gate_stats0['n_deferred']} "
           f"base_in_band={baseline_in_band} discrim={discriminator_fires} wn={_WN_OK}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": v, "verdict_msg": msg, "summary": msg,
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(), "config": cfg, "seeds": SEEDS,
        "step0_correlations": step0, "growth_arms_mean": arms_mean, "verdict_detail": vd,
        "error_decorrelation_seed0": decorr0, "decorr_seed_invariant": bool(decorr_seed_invariant),
        "gate_stats_seed0": gate_stats0,
        "per_seed": [{"seed": ps["seed"], "corrs": ps["corrs"],
                      "arms": {k: ps["arms"][k] for k in ["UNFILTERED_RAW", "FILTERED_RAW",
                               "FILTERED_RAW_2VIEW", "UNFILTERED_LCCP", "FILTERED_LCCP"]},
                      "decorr": ps["decorr"]} for ps in per_seed],
        "arms_differ_verified": True, "baseline_in_band": baseline_in_band,
        "discriminator_fires": discriminator_fires, "scaffold_free_witness": witness,
        "kept_hashes_seed0": {"UNFILTERED_RAW": h_unf, "FILTERED_RAW": h_fil},
        "final_metrics_atomicity": "tmp_replace", "wordnet_available": _WN_OK, "wordnet_err": _WN_ERR,
        "calibration_check": "default_ok_for_this_regime (gate thr_keep/thr_defer inherited from the existing "
                             "coherence-gate cell; same McGuffey corpus family)",
        "cited_stacked_reader_precision": CITED_STACKED_READER_PRECISION,
        "cited_unfiltered_growth_precision": CITED_UNFILTERED_GROWTH_PRECISION,
        "independent_gold_source": "data/gold_mcguffey_lccp_argstruct_v1.json (single-annotator; pos + nopat).",
        "gold_meta": per_seed[0]["ev"]["gold_meta"],
        "REQUIRED_FIELDS": ["verdict", "step0_correlations", "growth_arms_mean", "verdict_detail",
                            "error_decorrelation_seed0", "scaffold_free_witness"],
        "notes": ("STEP-0 safety gate + FILTERED-vs-UNFILTERED foundation-growth. STEP-0: coherence-gate "
                  "confidence (sigB) point-biserial corr with gold correctness -- usable if >=+0.15, UNSAFE "
                  "(CCL pattern) if null/negative (decisive early kill). GROWTH: does the gate raise the "
                  "consolidated-set precision >=+0.05 over UNFILTERED_RAW, beat 0.557, retain >=0.60 recall. "
                  "sigA=extractor's own objecthood (maximally entangled); sigC=WordNet-lexical + redundancy "
                  "second view (co-training decorrelation probe). HARD_FAIL_CONFIDENCE_UNSAFE and "
                  "HARD_FAIL_GROWTH_NOISE_BOUND are both valuable documented negatives. CLAIM-VET-pending; "
                  "single-annotator gold (caveated); corpus = McGuffey L04-L12 (real early-reading text "
                  "outside the castle slice). NOT the full cross-document Arm1/2/3 compounding harness "
                  "(Prediction C) -- this is the cheap decisive pre-check that gates whether that build is safe.")
    }
    write_metrics(output_dir, payload)

    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    print(f"  STEP-0 correlations (signal vs gold correctness, point-biserial mean +- std):", flush=True)
    for sk in ["sigB_coherence_gate", "sigA_objecthood", "sigC_lexical", "sigC_redundancy"]:
        s = step0[sk]
        print(f"    {sk:>20}: pb={s['point_biserial_mean']}+-{s['point_biserial_std']} "
              f"spearman={s['spearman_mean']} n={s['n_mean']}", flush=True)
    print(f"  GROWTH arms (precision / recall, mean across seeds):", flush=True)
    for arm in ["UNFILTERED_RAW", "FILTERED_RAW", "FILTERED_RAW_2VIEW", "UNFILTERED_LCCP", "FILTERED_LCCP"]:
        m = arms_mean[arm]
        print(f"    {arm:>20}: P={m['precision']} (+-{m['precision_std']}) R={m['recall']} n_pred~{m['n_pred_mean']}", flush=True)
    print(f"  decorrelation(B,C): corr_on_incorrect={decorr0['signal_corr_on_incorrect']} "
          f"gate_catches_wrong={decorr0['gate_catches_wrong_frac']} lex_catches_wrong={decorr0['lex_catches_wrong_frac']} "
          f"both_miss={decorr0['both_miss_wrong_frac']}", flush=True)
    print(f"  filtered_raw residual FP: {gate_stats0['filtered_raw_residual_fp']}", flush=True)
    print(f"  witness: {witness}", flush=True)
    return payload


def self_test():
    # --- formula self-test: point-biserial vs a hand-computed example ---
    # x=[1,2,3,4], y=[0,0,1,1]; Pearson = 2/sqrt(5) = 0.8944271909999159 (hand-verified). Spearman
    # ranks are identical to the values here -> also 0.8944271909999159.
    _EXP = 0.8944271909999159
    pb = pearson([1, 2, 3, 4], [0, 0, 1, 1])
    assert pb is not None and abs(pb - _EXP) < 1e-9, f"pearson broken: {pb}"
    sp = spearman([10, 20, 30, 40], [0, 0, 1, 1])
    assert sp is not None and abs(sp - _EXP) < 1e-9, f"spearman broken: {sp}"
    # anti-correlation sign
    assert pearson([1, 2, 3, 4], [1, 1, 0, 0]) < 0, "anti-correlation sign wrong"
    # tie-averaged ranks: [5,5,9] -> ranks [0.5,0.5,2]
    r = _rank([5, 5, 9])
    assert abs(r[0] - 0.5) < 1e-9 and abs(r[1] - 0.5) < 1e-9 and abs(r[2] - 2.0) < 1e-9, f"rank ties: {r}"
    # --- lexical view sanity (external resource) ---
    if _WN_OK:
        assert lexical_plausible("castle")[0] == 1, "castle should be concrete (noun.artifact)"
        assert lexical_plausible("door")[0] == 1, "door should be concrete"
        assert lexical_plausible("time")[0] == 0, "time should be non-concrete (noun.event/time)"
        assert lexical_plausible("he")[1] is True, "pronoun should abstain"
    # --- end-to-end smoke (one seed) + determinism guard ---
    cfg = cfg_smoke()
    ev1 = build_eval(cfg, 7)
    ev2 = build_eval(cfg, 7)
    c1 = corr_signal_vs_correct(ev1["records"], "sigB")
    c2 = corr_signal_vs_correct(ev2["records"], "sigB")
    assert c1["point_biserial"] == c2["point_biserial"], "DETERMINISM BREACH: sigB corr differs across identical runs"
    arms = growth_arms(ev1)
    unf = arms["UNFILTERED_RAW"]; fil = arms["FILTERED_RAW"]
    assert 0.05 < unf["precision"] < 0.95, f"baseline out of band: {unf['precision']}"
    assert fil["n_pred"] <= unf["n_pred"], "filter must not add extractions"
    decorr = error_decorrelation(ev1["records"])
    print(f"[{ANCHOR_NAME}] self-test OK: pearson/spearman/ties/lexical/determinism pass", flush=True)
    print(f"[{ANCHOR_NAME}] smoke(L04+L05,seed7): sigB corr pb={c1['point_biserial']} n={c1['n']} "
          f"| UNFILT_RAW P={unf['precision']} R={unf['recall']} -> FILT_RAW P={fil['precision']} R={fil['recall']} "
          f"| gate drop={arms['_gate_stats']['n_dropped']} def={arms['_gate_stats']['n_deferred']} "
          f"| decorr(B,C)_on_wrong={decorr['signal_corr_on_incorrect']} wn={_WN_OK}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run_mode("smoke"); return
    if args.full:
        run_mode("full"); return
    ap.error("specify one of --self-test | --smoke | --full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        diag = {
            "anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
            "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
        }
        try:
            write_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), diag)
        except Exception:
            pass
        raise
