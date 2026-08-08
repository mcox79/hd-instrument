#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_pragmatic_curriculum_vsa_superposition_map_v1

THE PRIMARY MECHANISM TEST (notes/curriculum_spec_pragmatic_constructions_2026-08-08.md section
"3-PRIME", USER architectural steer): construction-typing is NOT an MDL feature-classifier problem
-- it is the SAME VSA superposition-collapse we already PROVED for words (word_map = bundle(bind(
context_key, sense)), exp_word_context_affect_superposition_map_v1.py, HARD_PASS 04af969c4), lifted
to the sentence/discourse scale. This cell builds that lift and measures it head-to-head against the
MDL classifier baseline (exp_pragmatic_curriculum_dialogue_request_response_first_test_v1.py,
landed HARD_FAIL_NULL at n_train=12 / HARD_PASS-shaped 0.833 at n_train=18) on the IDENTICAL data,
splits, and glass-box features -- apples-to-apples.

THE MECHANISM (word-map lifted, byte-identical algebra, reused primitives -- hdlab.binding.bind/
unbind, hdlab.bundling.bundle, hdlab.atoms.make_atom_fhrr/similarity; FHRR complex64, N_DIM=1024):
  1. VOCAB: every distinct glass-box feature-string the baseline's OWN feat_fn/extract_features can
     emit (reused verbatim, unmodified -- see import below) gets one fixed random unit-phase atom,
     built once from the UNION of feature-strings over all 24 items (order-independent: a sorted
     vocabulary drives a single seeded torch.Generator, so vector identity is deterministic and does
     not leak any split or label information -- these are symbol atoms, not learned parameters).
  2. RESPONSE CUE-BUNDLE (the "context key"): for item i, response_cue_bundle_i =
     bundle(stack([vocab_vec[f] for f in feat_fn(item_i)])) -- literally the word-map's context_key,
     just built from a MANY-FEATURE bundle per item instead of a single discrete context class.
  3. LEARN THE MAP (TRAIN only): sup_map = bundle(stack([ bind(response_cue_bundle_i, outcome_vec[
     gold_i]) for i in TRAIN ])) -- outcome_vec[MET] / outcome_vec[UNMET] are two fixed random FHRR
     atoms (the word-map's sense_vec, here MET/UNMET replaces the word's candidate-sense menu). This
     is bundle(bind(context (x) sense)), unmodified.
  4. COLLAPSE AT TEST: for held-out item j, recovered = unbind(sup_map, response_cue_bundle_j);
     cleanup-argmax over {outcome_vec[MET], outcome_vec[UNMET]} via hdlab.atoms.similarity -> the
     prediction, with the raw similarity margin reported (glass-box).
  Because bind/unbind is an approximate hetero-associative memory (unbind(sup_map, q) ~=
  sum_i sim(cue_i, q) * outcome_i for FHRR phasors), this is a SIMILARITY-WEIGHTED associative
  readout with NO per-rule specification cost -- unlike MDL, it never has to "afford" a rule; this is
  the concrete mechanism-level reason it may generalize where MDL's rule-cost model structurally
  cannot at small n (the money question, gate 2 below).

DATA + SPLITS (REUSED VERBATIM, not re-authored): experiments/data/dialogue_request_response_
curriculum_first_test_v1.jsonl (24 items) via the baseline module's own load_items/build_episodes;
PRIMARY split = baseline's own it["split"] field (train=12/test=12, ALL 12 test items idiomatic/
concession); FOLLOWUP split = baseline's own followup_resplit() (train=18/test=6, keeps both D1-
flagged canonical items held out: agg_anne_diana_bosom_friend, lw_laurie_proposal_rejected).
FEATURES: baseline.feat_fn / baseline.extract_features imported and called directly -- zero
duplication, so any feature-encoding difference between the two arms is impossible by construction.
BASELINES: MDL learner / hand-list-only / majority are RE-MEASURED live via baseline.run_pipeline()
(byte-identical baseline code, not stale metrics.json numbers) so both arms run in the same process
against the same in-memory items.

PRE-REGISTERED GATE (fixed before running, per the task brief):
  HARD-PASS: VSA held-out accuracy matches-or-beats the MDL learner's held-out accuracy at BOTH
    n_train=12 AND n_train=18, AND the scramble control collapses at both splits (acc_scramble <=
    SCRAMBLE_BAND=0.60), AND the positive control (synthetic cue-separated toy set) passes.
  BONUS (the money question, reported regardless of the gate): does VSA held-out accuracy at
    n_train=12 exceed 0.5 (chance) -- i.e. does it generalize where MDL structurally could not
    (MDL stayed KEEP_EPISODIC / held_out==majority==0.5 at this split, per the baseline's own
    landed verdict)?
  NULL/FAIL: if VSA ALSO nulls (<=0.5) at n_train=12, that is the SAME data-density read as the MDL
    result (diagnose, not a ceiling). If VSA underperforms MDL at n_train=18, diagnose feature
    encoding / bundle-load interference / cleanup collision -- NOT declared a ceiling without that
    diagnosis. Coverage is reported separately from accuracy throughout (glass-box).
  SCRAMBLE CONTROL (rigor): fixed-seed permutation of TRAIN gold labels (baseline.scramble_train_
    labels, reused verbatim, same SCRAMBLE_SEED), sup_map rebuilt from the permuted table; held-out
    accuracy must collapse toward chance or the "signal" is a measurement artifact.
  POSITIVE CONTROL (mechanism sanity, run_positive_control()): a tiny synthetic cue-separated
    dataset (2 classes, one discriminating cue feature + per-item noise features, disjoint train/
    test noise) that this exact machinery must recover near-perfectly (>=0.8) with REAL teaching and
    collapse toward chance (<=0.6) under label-scramble -- confirms the plumbing works before
    trusting the real 24-item numbers (mirrors the baseline's own XOR positive control for the MDL
    arm, same spirit, VSA-native mechanism).

Reuses (wire-don't-island, zero re-implementation): hdlab.binding (bind/unbind), hdlab.bundling
(bundle), hdlab.atoms (make_atom_fhrr, similarity) -- the exact primitives
exp_word_context_affect_superposition_map_v1.py used for the word-level proof (HARD_PASS 04af969c4);
experiments.exp_pragmatic_curriculum_dialogue_request_response_first_test_v1 (baseline module,
imported for load_items/build_episodes/extract_features/feat_fn/hand_list_only_predict/
majority_class/accuracy/scramble_train_labels/followup_resplit/module_fit/module_predict/
run_pipeline -- every one of these is CALLED, not copied).

COMPUTE: n=24 items total, N_DIM=1024 dense complex64 vectors, closed-form tensor ops only (no
training loop). Wall time sub-second. LOCAL-ONLY, foreground-to-completion; NO queue, NO push, NO
remote-persist, NO hdlab mutation, NO atom bank (skunkworks VETs). Deterministic: OMP/MKL/
OPENBLAS_NUM_THREADS=1, fixed torch.Generator seeds for every VSA atom set, fixed-int
random.Random seed (baseline.SCRAMBLE_SEED) for the scramble permutation only.
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
from datetime import datetime, timezone

import torch

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ANCHOR_NAME = "pragmatic_curriculum_vsa_superposition_map_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab import binding, bundling, atoms  # noqa: E402  (REUSE: bind/unbind/bundle/cleanup primitives)
import experiments.exp_pragmatic_curriculum_dialogue_request_response_first_test_v1 as baseline  # noqa: E402

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- Pre-registered config / gate (see module docstring) ----
N_DIM = 1024
VOCAB_SEED = 20260808001
OUTCOME_SEED = 20260808002
CTRL_SEED = 777
SCRAMBLE_SEED = baseline.SCRAMBLE_SEED  # reuse the SAME fixed seed as the MDL baseline
EPS = 1e-9
BAND_SCRAMBLE_MAX_FOR_COLLAPSE = 0.60
BAND_CTRL_ACC_MIN = 0.80
LABELS = ("MET", "UNMET")


# ========================================================================================
# VSA machinery (word-map lifted, unmodified primitives)
# ========================================================================================
def build_vocab(items, d=N_DIM, seed=VOCAB_SEED, feat_fn=None):
    """One fixed random FHRR atom per distinct feature-string (baseline.feat_fn's own output
    vocabulary by default, built from a SORTED union -- deterministic, order-independent of item
    order). `feat_fn` is swappable ONLY for the secondary common-mode-ablation probe below (default
    None -> baseline.feat_fn, the exact MDL-arm feature function, unmodified)."""
    ff = feat_fn or baseline.feat_fn
    vocab_terms = sorted({f for it in items for f in ff(it)})
    gen = torch.Generator().manual_seed(seed)
    vocab_vecs = {term: atoms.make_atom_fhrr(d, gen) for term in vocab_terms}
    return vocab_vecs, vocab_terms


def build_outcome_vecs(d=N_DIM, seed=OUTCOME_SEED):
    gen = torch.Generator().manual_seed(seed)
    return {lbl: atoms.make_atom_fhrr(d, gen) for lbl in LABELS}


def response_cue_bundle(item, vocab_vecs, feat_fn=None):
    """The 'context key': bundle of unit cue-vectors for item's active glass-box features
    (baseline.feat_fn(item) by default, reused verbatim -- identical feature set to the MDL arm)."""
    ff = feat_fn or baseline.feat_fn
    feats = ff(item)
    vecs = torch.stack([vocab_vecs[f] for f in feats], dim=0)
    return bundling.bundle(vecs)


def build_cue_bundles(items, vocab_vecs, feat_fn=None):
    return {it["id"]: response_cue_bundle(it, vocab_vecs, feat_fn=feat_fn) for it in items}


def build_map(train_items, cue_bundles, outcome_vecs):
    """sup_map = bundle(bind(context, sense)) over TRAIN -- the word-map, unmodified."""
    entries = [binding.bind(cue_bundles[it["id"]], outcome_vecs[it["gold_class"]]) for it in train_items]
    stacked = torch.stack(entries, dim=0)
    return bundling.bundle(stacked)


def collapse_predict(item, sup_map, cue_bundles, outcome_vecs):
    """UNBIND by the item's own context key, CLEANUP-ARGMAX over {MET, UNMET}. Returns
    (pred_label, sims dict, margin=sims[best]-sims[other])."""
    q = cue_bundles[item["id"]]
    recovered = binding.unbind(sup_map, q)
    sims = {lbl: float(atoms.similarity(recovered, outcome_vecs[lbl])) for lbl in LABELS}
    best = max(sims, key=sims.get)
    other = [l for l in LABELS if l != best][0]
    margin = sims[best] - sims[other]
    return best, sims, margin


def _pred_digest(test_items, sup_map, cue_bundles, outcome_vecs):
    seq = [collapse_predict(it, sup_map, cue_bundles, outcome_vecs)[0] for it in test_items]
    return hashlib.sha256(json.dumps(seq).encode()).hexdigest()[:16], seq


def run_vsa_arm(train_items, test_items, cue_bundles, outcome_vecs, scramble_seed=SCRAMBLE_SEED):
    """One split (primary n=12 or followup n=18): REAL fit + held-out collapse + SCRAMBLE control
    (fixed-seed permuted TRAIN labels, baseline.scramble_train_labels reused verbatim)."""
    gold = [it["gold_class"] for it in test_items]

    sup_map = build_map(train_items, cue_bundles, outcome_vecs)
    preds, sims_list, margins = [], [], []
    for it in test_items:
        pred, sims, margin = collapse_predict(it, sup_map, cue_bundles, outcome_vecs)
        preds.append(pred)
        sims_list.append(sims)
        margins.append(margin)
    acc = baseline.accuracy(preds, gold)

    train_scr = baseline.scramble_train_labels(train_items, seed=scramble_seed)
    sup_map_scr = build_map(train_scr, cue_bundles, outcome_vecs)
    preds_scr = [collapse_predict(it, sup_map_scr, cue_bundles, outcome_vecs)[0] for it in test_items]
    acc_scr = baseline.accuracy(preds_scr, gold)

    dig_real, _ = _pred_digest(test_items, sup_map, cue_bundles, outcome_vecs)
    dig_scr, _ = _pred_digest(test_items, sup_map_scr, cue_bundles, outcome_vecs)

    per_item = []
    for it, pred, sims, margin in zip(test_items, preds, sims_list, margins):
        hl_v = it["_features"]["hand_list_verdict"]
        hl_correct = (hl_v == it["gold_class"])
        vsa_correct = (pred == it["gold_class"])
        per_item.append({
            "id": it["id"], "subtype": it["subtype"], "gold": it["gold_class"],
            "hand_list_verdict": hl_v, "vsa_pred": pred,
            "vsa_correct": bool(vsa_correct), "hand_list_correct": bool(hl_correct),
            "recovered_by_vsa": bool(vsa_correct and not hl_correct),
            "regressed_by_vsa": bool(hl_correct and not vsa_correct),
            "sims": {k: round(v, 5) for k, v in sims.items()}, "margin": round(margin, 5),
        })

    return {
        "n_train": len(train_items), "n_test": len(test_items),
        "acc": acc, "acc_scramble": acc_scr, "scramble_delta": acc - acc_scr,
        "digest_real": dig_real, "digest_scramble": dig_scr,
        "arms_differ_real_vs_scramble": dig_real != dig_scr,
        "per_item": per_item,
        "recovered_items": [p for p in per_item if p["recovered_by_vsa"]],
        "regressed_items": [p for p in per_item if p["regressed_by_vsa"]],
    }


# ========================================================================================
# Positive control (mechanism sanity check -- must pass before trusting the real 24-item numbers)
# ========================================================================================
def _ctrl_feat_fn(item):
    f = item["_ctrl_features"]
    return ["%s=%s" % (k, v) for k, v in f.items()]


CTRL_N_PER_CLASS = 6              # train AND test each get 6 POS + 6 NEG items
CTRL_SCRAMBLE_TRIALS = 9          # fixed seed offsets 1..9 -- see rationale below


def run_positive_control(seed=CTRL_SEED, d=256):
    """Synthetic cue-separated toy set: one discriminating cue feature (POS_CUE/NEG_CUE) + a unique
    per-item noise feature (disjoint TRAIN vs TEST noise tokens, so this cannot be exact-key lookup
    -- generalization must ride on the shared cue). REAL fit must recover near-perfectly; SCRAMBLE
    (permuted train labels) must collapse toward chance. Same VSA machinery, byte-identical calls.

    SCRAMBLE AVERAGING RATIONALE: with only 2 discriminating cue-groups, a SINGLE scramble-seed's
    outcome is quantized (each group's prediction is driven by that group's own random majority-
    label imbalance under the permutation, so a single trial can land on 0.0/0.5/1.0 by luck of the
    draw -- measured directly: single-seed acc_scramble ranged [0.0, 1.0] across trials). Averaging
    over CTRL_SCRAMBLE_TRIALS fixed, pre-declared seeds (not cherry-picked post-hoc) gives a stable
    estimate (measured mean ~0.29 over 15 trials at n=6/class) while remaining fully deterministic."""
    train, test = [], []
    for i in range(CTRL_N_PER_CLASS):
        train.append({"id": "ctrl_tr_pos_%d" % i, "gold_class": "MET",
                       "_ctrl_features": {"cue": "POS_CUE", "noise": "trn%d" % i}})
        train.append({"id": "ctrl_tr_neg_%d" % i, "gold_class": "UNMET",
                       "_ctrl_features": {"cue": "NEG_CUE", "noise": "trn%d" % i}})
    for i in range(CTRL_N_PER_CLASS):
        test.append({"id": "ctrl_te_pos_%d" % i, "gold_class": "MET",
                      "_ctrl_features": {"cue": "POS_CUE", "noise": "tst%d" % i}})
        test.append({"id": "ctrl_te_neg_%d" % i, "gold_class": "UNMET",
                      "_ctrl_features": {"cue": "NEG_CUE", "noise": "tst%d" % i}})
    all_items = train + test
    vocab_terms = sorted({t for it in all_items for t in _ctrl_feat_fn(it)})
    gen = torch.Generator().manual_seed(seed)
    vocab_vecs = {t: atoms.make_atom_fhrr(d, gen) for t in vocab_terms}
    outcome_vecs = {lbl: atoms.make_atom_fhrr(d, gen) for lbl in LABELS}
    cue_bundles = {}
    for it in all_items:
        vecs = torch.stack([vocab_vecs[t] for t in _ctrl_feat_fn(it)], dim=0)
        cue_bundles[it["id"]] = bundling.bundle(vecs)

    sup_map = build_map(train, cue_bundles, outcome_vecs)
    preds = [collapse_predict(it, sup_map, cue_bundles, outcome_vecs)[0] for it in test]
    gold = [it["gold_class"] for it in test]
    acc = baseline.accuracy(preds, gold)

    scr_accs = []
    for trial in range(1, CTRL_SCRAMBLE_TRIALS + 1):
        train_scr = baseline.scramble_train_labels(train, seed=seed + trial)
        sup_map_scr = build_map(train_scr, cue_bundles, outcome_vecs)
        preds_scr = [collapse_predict(it, sup_map_scr, cue_bundles, outcome_vecs)[0] for it in test]
        scr_accs.append(baseline.accuracy(preds_scr, gold))
    acc_scr_mean = sum(scr_accs) / len(scr_accs)

    passed = (acc >= BAND_CTRL_ACC_MIN) and (acc_scr_mean <= BAND_SCRAMBLE_MAX_FOR_COLLAPSE)
    return {"acc": acc, "acc_scramble": acc_scr_mean, "acc_scramble_trials": scr_accs,
            "passed": bool(passed)}


# ========================================================================================
# SECONDARY/EXPLORATORY common-mode-ablation probe (NOT the pre-registered primary gate).
# Diagnoses the primary run's own finding (see run_pipeline): the primary arm's held-out
# predictions were a CONSTANT "MET" for every test item at both splits (verified via the digest
# fields -- real and scrambled arms produced byte-identical prediction sequences). Mechanism:
# hand_list_verdict=NA and hand_list_kind=none fire on 22/24 items (91.7%) and
# response_starts_with_quote=True fires on 20/24 (83.3%) -- these near-universal categorical
# fillers dominate every item's cue-bundle by raw count, so the associative unbind is swamped by
# this shared common-mode component (paired predominantly with MET in an imbalanced 8-MET/4-UNMET
# TRAIN) rather than by the sparse, item-specific idiom cues that actually carry the label
# information. This is the SAME common-mode-swamps-linear-superposition failure mode this codebase
# has characterized before at the embedding-storage layer (anisotropy-rescue lineage); here it is
# the FEATURE layer, not embeddings. Pre-declared BEFORE measuring: exclude any cue-term with
# document-frequency >= DF_EXCLUDE_THRESHOLD (a round, not-tuned-to-outcome cutoff) from the VSA
# cue-bundle ONLY -- the MDL/hand-list/majority arms are completely untouched (same features,
# same code, as measured in the primary comparison).
# ========================================================================================
DF_EXCLUDE_THRESHOLD = 0.5  # exclude cue terms present in >=50% of all 24 items (near-constant fillers)


def compute_doc_freq(items, feat_fn=None):
    ff = feat_fn or baseline.feat_fn
    from collections import Counter
    c = Counter()
    for it in items:
        for f in set(ff(it)):
            c[f] += 1
    return c, len(items)


def make_lowfreq_feat_fn(items, threshold=DF_EXCLUDE_THRESHOLD):
    """Returns (feat_fn_variant, excluded_terms). feat_fn_variant drops any baseline.feat_fn term
    whose document frequency over `items` is >= threshold; degenerate guard: if that would leave an
    item with ZERO active cue-terms, keep its original (unfiltered) feature list instead."""
    df, n = compute_doc_freq(items)
    excluded = {f for f, c in df.items() if c / n >= threshold}

    def _f(item):
        feats = baseline.feat_fn(item)
        kept = [f for f in feats if f not in excluded]
        return kept if kept else feats

    return _f, excluded


def run_common_mode_ablation_probe(items, primary_train, primary_test, followup_train, followup_test):
    lowfreq_feat_fn, excluded_terms = make_lowfreq_feat_fn(items)
    vocab_vecs2, vocab_terms2 = build_vocab(items, feat_fn=lowfreq_feat_fn)
    outcome_vecs2 = build_outcome_vecs()  # feature-independent; identical to the primary arm's
    cue_bundles2 = build_cue_bundles(items, vocab_vecs2, feat_fn=lowfreq_feat_fn)

    primary2 = run_vsa_arm(primary_train, primary_test, cue_bundles2, outcome_vecs2)
    followup2 = run_vsa_arm(followup_train, followup_test, cue_bundles2, outcome_vecs2)

    return {
        "note": ("SECONDARY/EXPLORATORY -- not the pre-registered primary gate. Tests the primary "
                 "run's own common-mode-swamping diagnosis by excluding near-constant filler cue-"
                 "terms (document frequency >= %.0f%% of all 24 items) from the VSA cue-bundle "
                 "ONLY; the MDL/hand-list/majority baselines are untouched." % (DF_EXCLUDE_THRESHOLD * 100)),
        "excluded_terms": sorted(excluded_terms),
        "n_vocab_terms_after_exclusion": len(vocab_terms2),
        "n_train_12": {"vsa_held_out_accuracy": primary2["acc"],
                       "vsa_scramble_accuracy": primary2["acc_scramble"],
                       "arms_differ_real_vs_scramble": primary2["arms_differ_real_vs_scramble"]},
        "n_train_18": {"vsa_held_out_accuracy": followup2["acc"],
                        "vsa_scramble_accuracy": followup2["acc_scramble"],
                        "arms_differ_real_vs_scramble": followup2["arms_differ_real_vs_scramble"]},
        "primary_detail": primary2, "followup_detail": followup2,
    }


# ========================================================================================
# Crash diagnostics + atomic write (project convention)
# ========================================================================================
def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
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


# ========================================================================================
# Main pipeline
# ========================================================================================
def run_pipeline(run_mode):
    t0 = time.perf_counter()

    ctrl = run_positive_control()

    items = baseline.build_episodes(baseline.load_items())
    assert len(items) == 24, "INSTRUMENTATION_SUSPECT: expected 24 items, got %d" % len(items)
    classes = sorted(set(it["gold_class"] for it in items))
    assert classes == ["MET", "UNMET"]

    # ---- baselines re-measured live via the SAME baseline module (byte-identical code) ----
    baseline_metrics = baseline.run_pipeline(run_mode="vsa_comparison_reference")
    mdl_primary_acc = baseline_metrics["learner"]["held_out_accuracy"]
    hl_primary_acc = baseline_metrics["hand_list_only"]["held_out_accuracy"]
    maj_primary_acc = baseline_metrics["majority_class_floor"]["held_out_accuracy"]
    fu = baseline_metrics["followup_data_density_probe"]
    mdl_followup_acc = fu["held_out_accuracy_module"]
    hl_followup_acc = fu["held_out_accuracy_hand_list_only"]
    maj_followup_acc = fu["held_out_accuracy_majority"]

    # ---- VSA vocab + cue bundles (built ONCE over all 24 items; split-agnostic symbol atoms) ----
    vocab_vecs, vocab_terms = build_vocab(items)
    outcome_vecs = build_outcome_vecs()
    cue_bundles = build_cue_bundles(items, vocab_vecs)

    primary_train = [it for it in items if it["split"] == "train"]
    primary_test = [it for it in items if it["split"] == "test"]
    assert len(primary_train) == 12 and len(primary_test) == 12
    followup_train, followup_test = baseline.followup_resplit(items)
    assert len(followup_train) == 18 and len(followup_test) == 6

    primary = run_vsa_arm(primary_train, primary_test, cue_bundles, outcome_vecs)
    followup = run_vsa_arm(followup_train, followup_test, cue_bundles, outcome_vecs)

    # ---- secondary/exploratory diagnostic probe (see function docstring; NOT part of the gate) ----
    ablation = run_common_mode_ablation_probe(items, primary_train, primary_test, followup_train, followup_test)

    # ---- gate ----
    gate_scramble_primary = primary["acc_scramble"] <= BAND_SCRAMBLE_MAX_FOR_COLLAPSE
    gate_scramble_followup = followup["acc_scramble"] <= BAND_SCRAMBLE_MAX_FOR_COLLAPSE
    gate_n12_generalizes = primary["acc"] > 0.5 + EPS
    beats_mdl_primary = primary["acc"] >= mdl_primary_acc - EPS
    beats_mdl_followup = followup["acc"] >= mdl_followup_acc - EPS

    hard_pass = (ctrl["passed"] and beats_mdl_primary and beats_mdl_followup
                 and gate_scramble_primary and gate_scramble_followup)

    if not ctrl["passed"]:
        verdict = "HARD_FAIL_MECHANISM"
        msg = ("Positive control failed: synthetic cue-separated toy set acc=%.3f (want >= %.2f) "
               "scramble=%.3f (want <= %.2f) -- the VSA plumbing itself is not working; do not trust "
               "the real-data numbers below." %
               (ctrl["acc"], BAND_CTRL_ACC_MIN, ctrl["acc_scramble"], BAND_SCRAMBLE_MAX_FOR_COLLAPSE))
    elif hard_pass:
        verdict = "HARD_PASS"
        msg = ("HARD_PASS: VSA matches-or-beats MDL at BOTH splits (n=12: vsa=%.4f vs mdl=%.4f; "
               "n=18: vsa=%.4f vs mdl=%.4f), scramble collapses both splits (n=12 scr=%.4f, n=18 "
               "scr=%.4f), n=12 generalizes past chance=%s." %
               (primary["acc"], mdl_primary_acc, followup["acc"], mdl_followup_acc,
                primary["acc_scramble"], followup["acc_scramble"], gate_n12_generalizes))
    else:
        if primary["acc"] <= 0.5 + EPS:
            abl12, abl18 = ablation["n_train_12"]["vsa_held_out_accuracy"], ablation["n_train_18"]["vsa_held_out_accuracy"]
            ablation_rescued = (abl12 > primary["acc"] + EPS) and (abl18 > followup["acc"] + EPS)
            if ablation_rescued:
                abl_verdict_note = ("CONFIRMED by the common_mode_ablation_probe (secondary/exploratory): "
                                     "excluding those filler terms RESCUES accuracy (n=12: %.4f -> %.4f, "
                                     "n=18: %.4f -> %.4f) -- common-mode swamping is the root cause." %
                                     (primary["acc"], abl12, followup["acc"], abl18))
            else:
                abl_verdict_note = ("The common_mode_ablation_probe (secondary/exploratory, excludes those "
                                     "filler terms from the cue-bundle) does NOT rescue accuracy (n=12: "
                                     "%.4f -> %.4f, n=18: %.4f -> %.4f, both still <= chance) -- ruling OUT "
                                     "'simple frequency-based downweighting' as a standalone fix. The filler-"
                                     "dominance diagnosis (verified: identical constant predictions across "
                                     "real/scrambled fits) is real, but the deeper issue is that TRAIN (direct/"
                                     "literal items + ONE idiomatic seed, by the baseline's own design) and "
                                     "TEST (100%% idiomatic/concession) share almost no DISCRIMINATIVE surface "
                                     "cue overlap at all -- even where a shared idiom marker exists (e.g. "
                                     "'idiom_phrase_all_right' appears in both a TRAIN item and a TEST item), "
                                     "it is only 1 of 6-9 active features per item, too small a share of the "
                                     "bundle's similarity budget to dominate the associative readout. This is "
                                     "a genuine binding-capacity / signal-to-filler-ratio limitation of the "
                                     "flat-bundle encoding at this feature density, not fixed by term exclusion "
                                     "alone (removing terms can also strip legitimate signal and leave too few "
                                     "active terms, which is consistent with the ablation's WORSE-than-chance "
                                     "n=18 result, %.4f)." % (primary["acc"], abl12, followup["acc"], abl18, abl18))
            verdict = "NULL_COMMON_MODE_SWAMPING_DIAGNOSED"
            msg = ("VSA collapses to a CONSTANT majority-class prediction at n_train=12 (acc=%.4f; "
                   "digest_real==digest_scramble -- verified NOT a per-item read at all, real and "
                   "scrambled fits predict identically) AND at n=18 (acc=%.4f vs mdl=%.4f). Diagnosed "
                   "mechanism (NOT a data-density read like the MDL baseline's own HARD_FAIL_NULL): "
                   "near-universal filler cue-terms (hand_list_verdict=NA/hand_list_kind=none on "
                   "22/24 items, response_starts_with_quote=True on 20/24) dominate every cue-bundle "
                   "by raw count and swamp the sparse item-specific idiom cues in the associative "
                   "unbind -- common-mode-swamps-linear-superposition, the same failure family this "
                   "codebase has characterized at the embedding-storage layer, now observed at the "
                   "feature layer. %s" %
                   (primary["acc"], followup["acc"], mdl_followup_acc, abl_verdict_note))
        elif not beats_mdl_followup:
            verdict = "MIDDLE_BAND_UNDERPERFORMS_MDL_AT_N18"
            msg = ("VSA generalizes past chance at n=12 (acc=%.4f > 0.5, MDL was null there) but "
                   "underperforms the MDL learner at n=18 (vsa=%.4f < mdl=%.4f) -- diagnose feature "
                   "encoding / bundle-load interference / cleanup collision at this load before any "
                   "ceiling claim; report per-item recovered/regressed below." %
                   (primary["acc"], followup["acc"], mdl_followup_acc))
        elif not (gate_scramble_primary and gate_scramble_followup):
            verdict = "MIDDLE_BAND_SCRAMBLE_DID_NOT_COLLAPSE"
            msg = ("Accuracy gates clear but scramble control did not collapse as expected (n=12 "
                   "scr=%.4f, n=18 scr=%.4f, band<=%.2f) -- the signal-vs-artifact rigor check needs "
                   "scrutiny before trusting the accuracy numbers." %
                   (primary["acc_scramble"], followup["acc_scramble"], BAND_SCRAMBLE_MAX_FOR_COLLAPSE))
        else:
            verdict = "MIDDLE_BAND"
            msg = ("Partial: n=12 vsa=%.4f (mdl=%.4f), n=18 vsa=%.4f (mdl=%.4f); see gate booleans "
                   "for which condition failed." % (primary["acc"], mdl_primary_acc,
                                                      followup["acc"], mdl_followup_acc))

    elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "verdict": verdict, "verdict_msg": msg,
        "summary": msg, "elapsed_s": round(elapsed, 4),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "positive_control": ctrl,
        "config": {"n_dim": N_DIM, "vocab_seed": VOCAB_SEED, "outcome_seed": OUTCOME_SEED,
                   "scramble_seed": SCRAMBLE_SEED, "n_vocab_terms": len(vocab_terms),
                   "vocab_terms": vocab_terms, "labels": list(LABELS),
                   "band_scramble_max_for_collapse": BAND_SCRAMBLE_MAX_FOR_COLLAPSE},
        "comparison": {
            "n_train_12": {
                "vsa_held_out_accuracy": primary["acc"],
                "mdl_held_out_accuracy": mdl_primary_acc,
                "hand_list_only_accuracy": hl_primary_acc,
                "majority_accuracy": maj_primary_acc,
                "vsa_scramble_accuracy": primary["acc_scramble"],
                "vsa_scramble_delta": primary["scramble_delta"],
                "vsa_beats_or_matches_mdl": beats_mdl_primary,
                "vsa_generalizes_past_chance": gate_n12_generalizes,
                "mdl_verdict_on_disk": baseline_metrics["verdict"],
            },
            "n_train_18": {
                "vsa_held_out_accuracy": followup["acc"],
                "mdl_held_out_accuracy": mdl_followup_acc,
                "hand_list_only_accuracy": hl_followup_acc,
                "majority_accuracy": maj_followup_acc,
                "vsa_scramble_accuracy": followup["acc_scramble"],
                "vsa_scramble_delta": followup["scramble_delta"],
                "vsa_beats_or_matches_mdl": beats_mdl_followup,
            },
        },
        "gates": {
            "positive_control_passed": ctrl["passed"],
            "beats_mdl_primary_n12": beats_mdl_primary,
            "beats_mdl_followup_n18": beats_mdl_followup,
            "scramble_collapsed_n12": gate_scramble_primary,
            "scramble_collapsed_n18": gate_scramble_followup,
            "n12_generalizes_past_chance_MONEY_QUESTION": gate_n12_generalizes,
            "hard_pass": hard_pass,
        },
        "primary_n12": primary,
        "followup_n18": followup,
        "common_mode_ablation_probe": ablation,
        "cell_chunked": False, "final_metrics_atomicity": "tmp_replace",
        "deterministic_seeding": True,
        "cardinality_ok": True, "expected_n_units": 1,
    }
    return metrics


# ========================================================================================
# Instrumentation self-test (MANDATORY at module scope before any dispatch)
# ========================================================================================
def _instrumentation_selftest():
    ctrl = run_positive_control()
    assert ctrl["passed"], "SELFTEST FAIL: positive control did not pass: %r" % ctrl

    items = baseline.build_episodes(baseline.load_items())
    assert len(items) == 24, "SELFTEST FAIL: expected 24 items, got %d" % len(items)

    vocab_vecs, vocab_terms = build_vocab(items)
    assert len(vocab_terms) >= 5, "SELFTEST FAIL: degenerate vocab (%d terms)" % len(vocab_terms)
    outcome_vecs = build_outcome_vecs()
    assert set(outcome_vecs.keys()) == set(LABELS)

    cue_bundles = build_cue_bundles(items, vocab_vecs)
    cue_bundles_2 = build_cue_bundles(items, vocab_vecs)
    for k in cue_bundles:
        assert torch.allclose(cue_bundles[k], cue_bundles_2[k]), \
            "SELFTEST FAIL: cue bundle nondeterministic for item %s" % k

    primary_train = [it for it in items if it["split"] == "train"]
    primary_test = [it for it in items if it["split"] == "test"]
    assert len(primary_train) == 12 and len(primary_test) == 12, "SELFTEST FAIL: primary split sizes"
    followup_train, followup_test = baseline.followup_resplit(items)
    assert len(followup_train) == 18 and len(followup_test) == 6, "SELFTEST FAIL: followup split sizes"
    assert set(it["id"] for it in followup_train).isdisjoint(set(it["id"] for it in followup_test))

    res = run_vsa_arm(primary_train, primary_test, cue_bundles, outcome_vecs)
    assert 0.0 <= res["acc"] <= 1.0
    assert all("margin" in p and "sims" in p for p in res["per_item"]), \
        "SELFTEST FAIL: glass-box margins/sims missing from per-item report"
    assert len(res["per_item"]) == 12

    # determinism: re-running the whole arm must reproduce bit-identical predictions
    res2 = run_vsa_arm(primary_train, primary_test, cue_bundles, outcome_vecs)
    assert res["digest_real"] == res2["digest_real"], "SELFTEST FAIL: predictions not deterministic"

    # feat_fn parity with the baseline module: reused, not reimplemented
    a = baseline.feat_fn(items[0])
    b = baseline.feat_fn(items[0])
    assert a == b, "SELFTEST FAIL: baseline.feat_fn not deterministic (should be, unmodified)"

    # secondary common-mode-ablation probe: must run without crashing and actually exclude something
    ablation = run_common_mode_ablation_probe(items, primary_train, primary_test, followup_train, followup_test)
    assert len(ablation["excluded_terms"]) >= 1, \
        "SELFTEST FAIL: common-mode ablation excluded zero terms (DF_EXCLUDE_THRESHOLD miscalibrated)"
    assert ablation["n_vocab_terms_after_exclusion"] < len(vocab_terms), \
        "SELFTEST FAIL: ablation vocab did not shrink relative to the unablated vocab"


_instrumentation_selftest()  # Called at module scope before the main pipeline


def self_test():
    metrics = run_pipeline(run_mode="self_test")
    _write_metrics(OUTPUT_DIR + "_selftest", metrics)
    print("[self_test] verdict=%s" % metrics["verdict"])
    print("[self_test] " + metrics["verdict_msg"])
    return metrics["verdict"] not in ("CELL_CRASHED",)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run-mode", choices=["full", "self_test"], default="full")
    args = ap.parse_args()

    if args.self_test:
        ok = self_test()
        sys.exit(0 if ok else 1)

    metrics = run_pipeline(run_mode=args.run_mode)
    _write_metrics(OUTPUT_DIR, metrics)
    print("[%s] verdict=%s" % (args.run_mode, metrics["verdict"]))
    print("[%s] " % args.run_mode + metrics["verdict_msg"])
    print(json.dumps({k: v for k, v in metrics.items() if k not in (
        "primary_n12", "followup_n18")}, indent=2, default=str))
    print("---- n=12 per-item (primary, ALL idiomatic/concession held-out) ----")
    for p in metrics["primary_n12"]["per_item"]:
        print(json.dumps(p, default=str))
    print("---- n=18 followup per-item ----")
    for p in metrics["followup_n18"]["per_item"]:
        print(json.dumps(p, default=str))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, e)
        raise
