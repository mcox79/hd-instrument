#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_pragmatic_curriculum_dialogue_request_response_dailydialog_v1

THE DEFINITIVE MECHANISM TEST on CLEAN MODERN data: re-runs the dialogue request/response
construction-typing test (MDL vs VSA superposition) on modern DailyDialog items instead of the
McGuffey-era children's-lit corpus, with two fixes applied to the two prior failure modes:

(1) DATA CLEANING: drops 3 items the Director identified as mislabeled/ambiguous (index 2 =
    "I hate to leave"/"Can you stay a little longer?" -- murky which turn is the request and which
    is the answer; index 3 = "When do you want to go?"/"Is today OK?" -- two agreeing questions,
    mislabeled UNMET; index 20 = "What can I help you with?"/"...I need some advice..." -- an offer,
    not a request). 27 items remain (15 MET / 12 UNMET).

(2) SPLIT FIX: the prior 24-item test's TRAIN was direct/literal-only and TEST was 100% idiomatic
    (a hard domain-shift that the naive flat VSA superposition (commit 5baf86fea) HARD-FAILed on by
    collapsing to constant-majority -- diagnosed there as COMMON-MODE SWAMPING: near-universal
    filler cues (hand_list_verdict=NA, response_starts_with_quote, ...) dominate the equal-weighted
    bundle, swamping the sparse item-specific idiom cue that actually carries the label). This test
    stratifies TRAIN/TEST by subtype (direct/idiomatic/concession) so BOTH splits contain a mix --
    fixing the domain-shift confound so any residual collapse in the naive arm is attributable to the
    superposition mechanism itself, not to train/test cue-vocabulary disjointness.

THE MECHANISM UNDER TEST (arm 3, the money arm): does adding a SELECTION/ATTENTION front-end --
weighting each cue by its TRAIN discriminativeness (weight_c = |P(MET|c present) - P(MET|c absent)|
estimated on TRAIN only) before bundling -- fix the naive arm's collapse and let the superposition
match-or-beat MDL? This is the brain-faithful attention step the word-level superposition
(exp_word_context_affect_superposition_map_v1.py, HARD_PASS 04af969c4) got for free from its single
SUPPLIED discriminative context dimension (animacy); sentence/construction-level cue-bundles have no
such single clean dimension supplied, so the test is whether LEARNING the weighting from TRAIN alone
recovers it.

DATA: experiments/data/dialogue_request_response_dailydialog_v1.jsonl (30 raw items). DROP_INDICES
(0-based line order in the raw file) = [2, 3, 20] -> 27 items retained. FAIR STRATIFIED SPLIT (own
split, NOT the file's own 'split' field, which encodes an unrelated authoring-time grouping):
groups items by (subtype, gold), seeded-shuffles each group, and sends floor(n/2) to TRAIN /
ceil(n/2) to TEST (the extra odd item is biased toward TEST -- more held-out coverage of the hard
idiomatic/concession members, the money question). This makes BOTH splits contain a mix of
direct + idiomatic + concession (fixing the prior domain-shift). SPLIT_SEED search: tries a fixed,
pre-declared sequence of seeds (SPLIT_SEED_BASE + 0, 1, 2, ...) and keeps the FIRST seed under which
TEST still contains >=1 idiomatic/concession member the hand-list detector (hdlab.goal_typing.
congruence_request_response) abstains-on-or-misfires-on -- a coverage constraint on TEST
COMPOSITION, not a search over any arm's accuracy (no arm is evaluated before the seed is fixed).

FEATURES: imported verbatim from
experiments.exp_pragmatic_curriculum_dialogue_request_response_first_test_v1 (extract_features,
feat_fn, key_fn_handlist, hand_list_only_predict, majority_class, accuracy, scramble_train_labels,
module_fit, module_predict, build_episodes, run_positive_control (XOR)) -- zero duplication, so any
feature-encoding difference between arms is impossible by construction. VSA machinery imported
verbatim from experiments.exp_pragmatic_curriculum_vsa_superposition_map_v1 (build_vocab,
build_outcome_vecs, build_cue_bundles, build_map, collapse_predict, run_vsa_arm, _pred_digest,
run_positive_control (synthetic cue-separated toy set)).

ARMS (all measured, all on the SAME 27-item data / stratified split / features):
  1. MDL baseline: hdlab.learner.registry.learn via baseline.module_fit (candidate_plugins =
     estimation/ruleind/gam), applied to held-out via baseline.module_predict.
  2. NAIVE flat superposition (ablation, reuses VSA_BASE.run_vsa_arm unmodified: equal-weight
     bundle(cue_vecs) -> bind(outcome) -> bundle over TRAIN -> unbind+cleanup-argmax at TEST).
     Expected (per the pre-registered gate note) to possibly ALSO work here if the prior failure was
     purely the domain-shift split rather than the flat-bundle mechanism itself.
  3. REFINED superposition WITH a selection/attention front-end (THE TEST): per-cue TRAIN-only
     discriminativeness weight_c = |P(MET|c present) - P(MET|c absent)|, cue-terms with zero TRAIN
     evidence get weight 0; response_cue_bundle_i = bundle(weight_c * vocab_vec[c] for c active in
     item i) (degenerate per-item fallback to equal-weight if EVERY active cue has weight 0, glass-
     box logged, not silently absorbed). sup_map = bundle(bind(weighted_cue_bundle_i, outcome_i))
     over TRAIN; collapse via unbind+cleanup at TEST. SCRAMBLE control recomputes BOTH the weights
     AND the map from permuted-label TRAIN (the whole learned-attention pipeline is re-fit, not just
     the map) -- held-out accuracy must collapse toward chance or the "signal" is an artifact.
  4. Baselines: hand-list-only (congruence_request_response's own verdict; NA = abstain = miss),
     majority-class floor (TRAIN majority, applied uniformly to TEST).
  5. Positive controls (mechanism sanity, both reused verbatim): MDL_BASE.run_positive_control()
     (synthetic XOR, must choose ruleind/gam) and VSA_BASE.run_positive_control() (synthetic
     cue-separated toy set, must recover >=0.80 acc / collapse <=0.60 under scramble).

GATE (pre-registered, per the task brief, anti-premature-HARD_FAIL protocol governs any non-pass):
  HARD-PASS: arm 3 (a) FIXES the naive arm's collapse (per-item predictions are non-constant AND
    digest_real != digest_scramble), (b) held-out accuracy matches-or-beats the MDL arm's held-out
    accuracy, (c) recovers >=1 held-out idiomatic/concession member the hand-list misses that MDL
    also fails to recover OR that the hand list alone misses (glass-box money-question reporting),
    (d) scramble control collapses (acc_scramble <= SCRAMBLE_BAND=0.60), AND both positive controls
    pass. Anything short of this is reported as a DIAGNOSTIC per the branches in the module docstring
    of the two source cells (still-collapses -> report cue-weights + whether discriminative cues got
    up-weighted but still lost the similarity budget; works-but-ties-MDL -> elegance-not-accuracy
    note; naive arm 2 ALSO generalizes here -> the prior failure was the domain-shift split, not the
    flat-bundle mechanism, reported regardless of the primary gate outcome).

COMPUTE: n=27 items, N_DIM=1024 dense complex64 (VSA arms) / closed-form counting (MDL arm). Wall
time sub-second. LOCAL-ONLY, foreground-to-completion; NO queue, NO push, NO remote-persist, NO
hdlab mutation, NO atom bank (skunkworks VETs). Deterministic: OMP/MKL/OPENBLAS_NUM_THREADS=1, fixed
torch.Generator seeds for every VSA atom set (reused from VSA_BASE), fixed-int random.Random seed
(baseline.SCRAMBLE_SEED, reused) for every scramble permutation, fixed-sequence seed search for the
split (see above, pre-declared not accuracy-tuned).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import random
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

import torch

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ANCHOR_NAME = "pragmatic_curriculum_dialogue_request_response_dailydialog_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab import bundling  # noqa: E402  (REUSE: bundle primitive, for the weighted-cue-bundle arm)
import experiments.exp_pragmatic_curriculum_dialogue_request_response_first_test_v1 as MDL_BASE  # noqa: E402
import experiments.exp_pragmatic_curriculum_vsa_superposition_map_v1 as VSA_BASE  # noqa: E402

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
DATA_PATH = os.path.join(REPO_ROOT, "experiments", "data", "dialogue_request_response_dailydialog_v1.jsonl")

# ---- Pre-registered config / gate (see module docstring) ----
DROP_INDICES = [2, 3, 20]  # 0-based raw-file line order
EXPECTED_DROPPED_IDS = {
    "dd_stay_longer_sorry_cant", "dd_is_today_ok_sorry_cant", "dd_mortgage_advice_unfortunately_no",
}
SPLIT_SEED_BASE = 20260808100
SPLIT_SEED_SEARCH_TRIALS = 50  # fixed, pre-declared search width over the coverage constraint only
SCRAMBLE_SEED = MDL_BASE.SCRAMBLE_SEED       # reuse the SAME fixed seed as the MDL/VSA baseline cells
SCRAMBLE_BAND = VSA_BASE.BAND_SCRAMBLE_MAX_FOR_COLLAPSE  # 0.60, reused pre-registered VSA convention
EPS = 1e-9


# ========================================================================================
# Data loading + cleaning (drop the 3 mislabeled items) + fair stratified split
# ========================================================================================
def load_raw_items():
    items = []
    with open(DATA_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def clean_items():
    """Drops the 3 Director-flagged mislabeled/ambiguous items by their 0-based file-line index;
    verifies the dropped ids match the exact ids specified in the task brief (fails loudly if the
    data file has drifted since specification)."""
    raw = load_raw_items()
    assert len(raw) == 30, "INSTRUMENTATION_SUSPECT: expected 30 raw items, got %d" % len(raw)
    dropped_ids = {raw[i]["id"] for i in DROP_INDICES}
    assert dropped_ids == EXPECTED_DROPPED_IDS, (
        "INSTRUMENTATION_SUSPECT: dropped-id mismatch, expected %r got %r" % (EXPECTED_DROPPED_IDS, dropped_ids))
    kept = [it for i, it in enumerate(raw) if i not in DROP_INDICES]
    assert len(kept) == 27, "INSTRUMENTATION_SUSPECT: expected 27 items after drop, got %d" % len(kept)
    return kept


def compute_stratified_split(items, seed):
    """Groups by (subtype, gold); seeded-shuffles each group; sends floor(n/2) to TRAIN and the
    remainder (ceil(n/2)) to TEST. Deterministic given seed (sorted group keys, sorted pre-shuffle
    item order within each group before rng.shuffle). Returns (train_ids, test_ids) as sets."""
    groups = defaultdict(list)
    for it in items:
        groups[(it["subtype"], it["gold"])].append(it)
    rng = random.Random(seed)
    train_ids, test_ids = set(), set()
    for key in sorted(groups.keys()):
        group_items = sorted(groups[key], key=lambda x: x["id"])
        rng.shuffle(group_items)
        n = len(group_items)
        n_train = n // 2
        for it in group_items[:n_train]:
            train_ids.add(it["id"])
        for it in group_items[n_train:]:
            test_ids.add(it["id"])
    return train_ids, test_ids


def apply_split(items, train_ids):
    out = []
    for it in items:
        it2 = dict(it)
        it2["split"] = "train" if it["id"] in train_ids else "test"
        out.append(it2)
    return out


def hard_case_coverage_ok(episodes_test):
    """TEST-composition coverage check (NOT an accuracy check): does TEST still contain >=1
    idiomatic/concession member the hand-list detector abstains-on (NA) or misfires-on (wrong
    verdict)? Uses each item's own _features['hand_list_verdict'], already computed by
    MDL_BASE.build_episodes/extract_features."""
    hard = [it for it in episodes_test if it["subtype"] in ("idiomatic", "concession")]
    missed = [it for it in hard
              if it["_features"]["hand_list_verdict"] == "NA"
              or it["_features"]["hand_list_verdict"] != it["gold_class"]]
    return len(missed) >= 1, missed


def find_split(items_cleaned):
    """Fixed, pre-declared seed search (SPLIT_SEED_BASE + 0..SPLIT_SEED_SEARCH_TRIALS-1); keeps the
    FIRST seed whose resulting TEST split satisfies hard_case_coverage_ok. This is a search over
    TEST-COMPOSITION coverage only -- no arm is fit or evaluated during this search, so it cannot
    leak into any arm's accuracy."""
    for trial in range(SPLIT_SEED_SEARCH_TRIALS):
        seed = SPLIT_SEED_BASE + trial
        train_ids, test_ids = compute_stratified_split(items_cleaned, seed)
        split_items = apply_split(items_cleaned, train_ids)
        episodes = MDL_BASE.build_episodes(split_items)
        test = [it for it in episodes if it["split"] == "test"]
        ok, missed = hard_case_coverage_ok(test)
        if ok:
            return seed, episodes, missed
    raise RuntimeError("INSTRUMENTATION_SUSPECT: no seed in the pre-declared search window satisfied "
                        "the hard-case TEST coverage constraint")


# ========================================================================================
# Arm 3: refined superposition with a selection/attention front-end
# ========================================================================================
def compute_cue_weights(train_items, feat_fn=None):
    """weight_c = |P(MET | c present) - P(MET | c absent)| estimated on TRAIN only. Cue-terms with
    NO train evidence in one of the two groups (e.g. a term that never fires in TRAIN, or that fires
    on every TRAIN item) get weight 0.0 -- conservative: no discriminativeness can be estimated
    without both a present- and an absent- group on TRAIN."""
    ff = feat_fn or MDL_BASE.feat_fn
    per_item_feats = {it["id"]: set(ff(it)) for it in train_items}
    all_terms = sorted({f for feats in per_item_feats.values() for f in feats})
    weights = {}
    for term in all_terms:
        present_met, present_tot, absent_met, absent_tot = 0, 0, 0, 0
        for it in train_items:
            is_met = it["gold_class"] == "MET"
            if term in per_item_feats[it["id"]]:
                present_tot += 1
                present_met += int(is_met)
            else:
                absent_tot += 1
                absent_met += int(is_met)
        if present_tot == 0 or absent_tot == 0:
            weights[term] = 0.0
        else:
            weights[term] = abs(present_met / present_tot - absent_met / absent_tot)
    return weights


def weighted_response_cue_bundle(item, vocab_vecs, weights, feat_fn=None):
    """Weighted cue-bundle: bundle(weight_c * vocab_vec[c]) over item's active features. Degenerate
    guard (glass-box, logged not hidden): if EVERY active cue has weight 0 (no TRAIN evidence for any
    of this item's cues), falls back to an EQUAL-weight bundle of the same cues so the item is not
    silently collapsed to a zero vector; returns (bundle, used_fallback: bool)."""
    ff = feat_fn or MDL_BASE.feat_fn
    feats = ff(item)
    w = [weights.get(f, 0.0) for f in feats]
    if sum(w) <= 0.0:
        vecs = torch.stack([vocab_vecs[f] for f in feats], dim=0)
        return bundling.bundle(vecs), True
    vecs = torch.stack([wi * vocab_vecs[f] for f, wi in zip(feats, w)], dim=0)
    return bundling.bundle(vecs), False


def build_weighted_cue_bundles(items, vocab_vecs, weights, feat_fn=None):
    bundles, fallback_ids = {}, []
    for it in items:
        b, used_fallback = weighted_response_cue_bundle(it, vocab_vecs, weights, feat_fn=feat_fn)
        bundles[it["id"]] = b
        if used_fallback:
            fallback_ids.append(it["id"])
    return bundles, fallback_ids


def run_refined_vsa_arm(train_items, test_items, vocab_vecs, outcome_vecs, feat_fn=None,
                         scramble_seed=SCRAMBLE_SEED):
    ff = feat_fn or MDL_BASE.feat_fn
    gold = [it["gold_class"] for it in test_items]

    weights = compute_cue_weights(train_items, feat_fn=ff)
    cue_bundles, fallback_ids = build_weighted_cue_bundles(train_items + test_items, vocab_vecs, weights, feat_fn=ff)
    sup_map = VSA_BASE.build_map(train_items, cue_bundles, outcome_vecs)

    preds, sims_list, margins = [], [], []
    for it in test_items:
        pred, sims, margin = VSA_BASE.collapse_predict(it, sup_map, cue_bundles, outcome_vecs)
        preds.append(pred)
        sims_list.append(sims)
        margins.append(margin)
    acc = MDL_BASE.accuracy(preds, gold)

    # SCRAMBLE control: recompute BOTH the weights AND the map from permuted-label TRAIN.
    train_scr = MDL_BASE.scramble_train_labels(train_items, seed=scramble_seed)
    weights_scr = compute_cue_weights(train_scr, feat_fn=ff)
    cue_bundles_scr, fallback_ids_scr = build_weighted_cue_bundles(train_scr + test_items, vocab_vecs, weights_scr, feat_fn=ff)
    sup_map_scr = VSA_BASE.build_map(train_scr, cue_bundles_scr, outcome_vecs)
    preds_scr = [VSA_BASE.collapse_predict(it, sup_map_scr, cue_bundles_scr, outcome_vecs)[0] for it in test_items]
    acc_scr = MDL_BASE.accuracy(preds_scr, gold)

    dig_real, _ = VSA_BASE._pred_digest(test_items, sup_map, cue_bundles, outcome_vecs)
    dig_scr, _ = VSA_BASE._pred_digest(test_items, sup_map_scr, cue_bundles_scr, outcome_vecs)

    per_item = []
    for it, pred, sims, margin in zip(test_items, preds, sims_list, margins):
        hl_v = it["_features"]["hand_list_verdict"]
        hl_correct = hl_v == it["gold_class"]
        vsa_correct = pred == it["gold_class"]
        per_item.append({
            "id": it["id"], "subtype": it["subtype"], "gold": it["gold_class"],
            "hand_list_verdict": hl_v, "vsa_pred": pred,
            "vsa_correct": bool(vsa_correct), "hand_list_correct": bool(hl_correct),
            "recovered_by_vsa": bool(vsa_correct and not hl_correct),
            "regressed_by_vsa": bool(hl_correct and not vsa_correct),
            "used_weight_fallback": it["id"] in fallback_ids,
            "sims": {k: round(v, 5) for k, v in sims.items()}, "margin": round(margin, 5),
        })

    n_nonconstant_preds = len(set(preds))
    return {
        "n_train": len(train_items), "n_test": len(test_items),
        "acc": acc, "acc_scramble": acc_scr, "scramble_delta": acc - acc_scr,
        "digest_real": dig_real, "digest_scramble": dig_scr,
        "arms_differ_real_vs_scramble": dig_real != dig_scr,
        "collapsed_to_constant": n_nonconstant_preds <= 1,
        "n_distinct_preds": n_nonconstant_preds,
        "weights": {k: round(v, 5) for k, v in sorted(weights.items(), key=lambda kv: -kv[1])},
        "weights_scrambled": {k: round(v, 5) for k, v in sorted(weights_scr.items(), key=lambda kv: -kv[1])},
        "n_fallback_items_real": len(fallback_ids), "fallback_item_ids_real": fallback_ids,
        "n_fallback_items_scrambled": len(fallback_ids_scr),
        "per_item": per_item,
        "recovered_items": [p for p in per_item if p["recovered_by_vsa"]],
        "regressed_items": [p for p in per_item if p["regressed_by_vsa"]],
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

    mdl_ctrl = MDL_BASE.run_positive_control()
    vsa_ctrl = VSA_BASE.run_positive_control()

    items_cleaned = clean_items()
    split_seed, episodes, hard_missed_at_split_time = find_split(items_cleaned)
    assert len(episodes) == 27
    classes = sorted(set(it["gold_class"] for it in episodes))
    assert classes == ["MET", "UNMET"], "INSTRUMENTATION_SUSPECT: unexpected class set %r" % classes

    train = [it for it in episodes if it["split"] == "train"]
    test = [it for it in episodes if it["split"] == "test"]
    gold_test = [it["gold_class"] for it in test]

    n_features_seen = len(set(f for it in episodes for f in MDL_BASE.feat_fn(it)))
    feature_names_nonconstant = sorted(
        name for name in episodes[0]["_features"]
        if len(set(it["_features"][name] for it in episodes)) > 1
    )
    assert n_features_seen > 5, "INSTRUMENTATION_SUSPECT: degenerate feature space"
    assert len(feature_names_nonconstant) >= 5, "INSTRUMENTATION_SUSPECT: teaching signal may not reach the learner"

    default_train = MDL_BASE.majority_class(train)

    # ---- baselines ----
    hl_preds_test = [MDL_BASE.hand_list_only_predict(it, default_train) for it in test]
    hl_acc_test = MDL_BASE.accuracy(hl_preds_test, gold_test)
    hl_abstain_test = sum(1 for it in test if it["_features"]["hand_list_verdict"] == "NA")
    maj_preds_test = [default_train for _ in test]
    maj_acc_test = MDL_BASE.accuracy(maj_preds_test, gold_test)

    # ---- arm 1: MDL ----
    mdl_name, mdl_chosen, mdl_all = MDL_BASE.module_fit(train, classes)
    mdl_compression = {n: r.compression_ratio for n, r in mdl_all.items()}
    mdl_is_episodic = mdl_chosen is None
    mdl_preds_test = (MDL_BASE.module_predict(mdl_name, mdl_chosen, test, default_train)
                       if mdl_chosen is not None else [default_train] * len(test))
    mdl_acc_test = MDL_BASE.accuracy(mdl_preds_test, gold_test)
    mdl_recovered = []
    for it, hl_pred, mod_pred in zip(test, hl_preds_test, mdl_preds_test):
        hl_correct = hl_pred == it["gold_class"] and it["_features"]["hand_list_verdict"] != "NA"
        if mod_pred == it["gold_class"] and not hl_correct:
            mdl_recovered.append({"id": it["id"], "subtype": it["subtype"], "gold": it["gold_class"]})

    # ---- arm 2: naive flat superposition (reused unmodified) ----
    vocab_vecs, vocab_terms = VSA_BASE.build_vocab(episodes)
    outcome_vecs = VSA_BASE.build_outcome_vecs()
    cue_bundles = VSA_BASE.build_cue_bundles(episodes, vocab_vecs)
    arm2 = VSA_BASE.run_vsa_arm(train, test, cue_bundles, outcome_vecs, scramble_seed=SCRAMBLE_SEED)

    # ---- arm 3: refined (weighted/attention) superposition -- THE TEST ----
    arm3 = run_refined_vsa_arm(train, test, vocab_vecs, outcome_vecs, feat_fn=MDL_BASE.feat_fn,
                                scramble_seed=SCRAMBLE_SEED)

    # ---- money question: which held-out idiomatic/concession members does each arm recover that
    # the hand list misses? ----
    def hard_recovered(arm_per_item):
        return [p for p in arm_per_item if p["recovered_by_vsa"] and p["subtype"] in ("idiomatic", "concession")]

    arm2_hard_recovered = [p for p in arm2["per_item"] if p["recovered_by_vsa"] and p["subtype"] in ("idiomatic", "concession")]
    arm3_hard_recovered = hard_recovered(arm3["per_item"])
    mdl_hard_recovered = [r for r in mdl_recovered if r["subtype"] in ("idiomatic", "concession")]

    # ---- gate ----
    arm3_fixes_collapse = (not arm3["collapsed_to_constant"]) and arm3["arms_differ_real_vs_scramble"]
    arm3_beats_mdl = arm3["acc"] is not None and mdl_acc_test is not None and arm3["acc"] >= mdl_acc_test - EPS
    arm3_recovers_hard = len(arm3_hard_recovered) >= 1
    arm3_scramble_collapses = arm3["acc_scramble"] is not None and arm3["acc_scramble"] <= SCRAMBLE_BAND + EPS
    ctrl_ok = mdl_ctrl["passed"] and vsa_ctrl["passed"]

    arm2_collapsed = arm2["digest_real"] == arm2["digest_scramble"]
    arm2_generalizes_here = (not arm2_collapsed) and arm2["acc"] is not None and arm2["acc"] > maj_acc_test + EPS

    hard_pass = ctrl_ok and arm3_fixes_collapse and arm3_beats_mdl and arm3_recovers_hard and arm3_scramble_collapses

    if not ctrl_ok:
        verdict = "HARD_FAIL_MECHANISM"
        msg = ("Positive control failed: mdl_ctrl passed=%s (chose %r on XOR) vsa_ctrl passed=%s "
               "(acc=%.3f scramble=%.3f) -- do not trust the real-data numbers below." %
               (mdl_ctrl["passed"], mdl_ctrl["chosen_name"], vsa_ctrl["passed"], vsa_ctrl["acc"], vsa_ctrl["acc_scramble"]))
    elif hard_pass:
        verdict = "HARD_PASS"
        msg = ("HARD_PASS: arm3 fixes the naive collapse (distinct_preds=%d, digest_real!=digest_scramble), "
               "held_out_acc arm3=%.4f >= mdl=%.4f, recovers %d held-out idiomatic/concession member(s) the "
               "hand list misses, scramble collapses (acc_scr=%.4f <= band=%.2f)." %
               (arm3["n_distinct_preds"], arm3["acc"], mdl_acc_test, len(arm3_hard_recovered),
                arm3["acc_scramble"], SCRAMBLE_BAND))
    elif not arm3_fixes_collapse:
        verdict = "NULL_ARM3_STILL_COLLAPSES"
        top_w = list(arm3["weights"].items())[:8]
        msg = ("Arm3 STILL collapses (distinct_preds=%d, digest_real==digest_scramble:%s) despite the "
               "discriminativeness weighting. Top-weighted TRAIN cues: %r. Diagnosis needed: did the "
               "discriminative (idiom/negation/grant-verb) cues get up-weighted but still lose the "
               "similarity budget to the SUM of many small-nonzero near-universal categorical cues "
               "(e.g. response_len_bucket/request_pattern each firing on every item with nonzero weight)? "
               "See per-item margins and the full weights table in this record." %
               (arm3["n_distinct_preds"], arm3["digest_real"] == arm3["digest_scramble"], top_w))
    elif not arm3_beats_mdl:
        verdict = "MIDDLE_BAND_ARM3_UNDERPERFORMS_MDL"
        msg = ("Arm3 fixes the collapse (non-constant, scramble differs) and scramble control %s, but "
               "held-out accuracy (%.4f) is BELOW mdl (%.4f) -- the selection front-end unswamps the "
               "signal but the resulting readout is noisier than MDL's rule search at this n. Not a "
               "ceiling claim without further diagnosis (see per-item recovered/regressed)." %
               ("collapses" if arm3_scramble_collapses else "does NOT collapse", arm3["acc"], mdl_acc_test))
    elif not arm3_recovers_hard:
        verdict = "MIDDLE_BAND_ARM3_NO_HARD_RECOVERY"
        msg = ("Arm3 fixes the collapse and matches-or-beats MDL on aggregate accuracy (%.4f vs %.4f), "
               "scramble %s, but recovers ZERO held-out idiomatic/concession members that the hand list "
               "misses -- the accuracy parity may be coming from the (majority-skewed) direct items "
               "rather than genuine idiomatic-construction generalization. See per-item table." %
               (arm3["acc"], mdl_acc_test, "collapses" if arm3_scramble_collapses else "does NOT collapse"))
    elif not arm3_scramble_collapses:
        verdict = "MIDDLE_BAND_SCRAMBLE_DID_NOT_COLLAPSE"
        msg = ("Arm3 fixes the collapse, beats-or-matches MDL (%.4f vs %.4f), and recovers %d hard "
               "member(s), but the scramble control did NOT collapse (acc_scr=%.4f > band=%.2f) -- "
               "the signal-vs-artifact rigor check needs scrutiny before trusting the accuracy numbers." %
               (arm3["acc"], mdl_acc_test, len(arm3_hard_recovered), arm3["acc_scramble"], SCRAMBLE_BAND))
    else:
        verdict = "MIDDLE_BAND"
        msg = "Partial pass; see gate booleans for which condition failed."

    if arm2_generalizes_here:
        msg += (" NOTE: the NAIVE (unweighted) arm2 ALSO generalizes past the majority floor here "
                "(acc=%.4f > majority=%.4f, digest differs) -- unlike the prior 24-item run, suggesting "
                "the earlier collapse was substantially the domain-shift split, not an intrinsic "
                "flat-bundle-mechanism failure; the weighting front-end's marginal contribution over "
                "naive bundling should be read relative to this." % (arm2["acc"], maj_acc_test))
    else:
        msg += (" NOTE: the naive (unweighted) arm2 %s here (digest_real==digest_scramble:%s, acc=%.4f "
                "vs majority=%.4f) even under the fixed stratified split -- consistent with common-mode "
                "swamping being a property of the flat-bundle mechanism itself, not just the prior "
                "domain-shift split." % ("still collapses" if arm2_collapsed else "does not clearly generalize",
                                          arm2_collapsed, arm2["acc"], maj_acc_test))

    elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "verdict": verdict, "verdict_msg": msg,
        "summary": msg, "elapsed_s": round(elapsed, 4),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "positive_controls": {"mdl_xor_control": mdl_ctrl, "vsa_synthetic_control": vsa_ctrl},
        "data": {
            "n_raw": 30, "drop_indices": DROP_INDICES, "dropped_ids": sorted(EXPECTED_DROPPED_IDS),
            "n_cleaned": len(items_cleaned), "n_items": len(episodes),
        },
        "split": {
            "seed_used": split_seed, "seed_search_base": SPLIT_SEED_BASE,
            "n_train": len(train), "n_test": len(test),
            "train_gold_counts": dict(Counter(it["gold_class"] for it in train)),
            "test_gold_counts": dict(Counter(it["gold_class"] for it in test)),
            "train_subtype_counts": dict(Counter(it["subtype"] for it in train)),
            "test_subtype_counts": dict(Counter(it["subtype"] for it in test)),
            "train_ids": [it["id"] for it in train], "test_ids": [it["id"] for it in test],
            "default_train_majority_class": default_train,
            "hard_case_coverage_at_split_time": [{"id": it["id"], "subtype": it["subtype"],
                                                    "hand_list_verdict": it["_features"]["hand_list_verdict"],
                                                    "gold": it["gold_class"]} for it in hard_missed_at_split_time],
        },
        "n_features_seen": n_features_seen, "feature_names_nonconstant": feature_names_nonconstant,
        "majority_class_floor": {"held_out_accuracy": maj_acc_test},
        "hand_list_only": {"held_out_accuracy": hl_acc_test, "n_abstained_NA": hl_abstain_test},
        "mdl_arm": {
            "chosen_plugin": mdl_name, "is_episodic": mdl_is_episodic,
            "compression_ratios_all_plugins": mdl_compression,
            "compression_ratio_chosen": (mdl_chosen.compression_ratio if mdl_chosen is not None else None),
            "held_out_accuracy": mdl_acc_test,
            "held_out_preds": [{"id": it["id"], "gold": it["gold_class"], "pred": p, "subtype": it["subtype"]}
                                for it, p in zip(test, mdl_preds_test)],
            "hypothesis_glass_box": (mdl_chosen.hypothesis if mdl_chosen is not None else None),
            "recovered_over_hand_list": mdl_recovered, "hard_recovered_idiomatic_or_concession": mdl_hard_recovered,
        },
        "naive_superposition_arm2": arm2,
        "naive_arm2_hard_recovered": arm2_hard_recovered,
        "naive_arm2_generalizes_here": arm2_generalizes_here,
        "refined_superposition_arm3": arm3,
        "refined_arm3_hard_recovered": arm3_hard_recovered,
        "gates": {
            "positive_controls_passed": ctrl_ok,
            "arm3_fixes_collapse": arm3_fixes_collapse,
            "arm3_beats_or_matches_mdl": arm3_beats_mdl,
            "arm3_recovers_hard_member": arm3_recovers_hard,
            "arm3_scramble_collapses": arm3_scramble_collapses,
            "hard_pass": hard_pass,
            "scramble_band": SCRAMBLE_BAND,
        },
        "cell_chunked": False, "final_metrics_atomicity": "tmp_replace",
        "deterministic_seeding": True, "scramble_seed": SCRAMBLE_SEED, "split_seed": split_seed,
        "cardinality_ok": True, "expected_n_units": 1,
    }
    return metrics


# ========================================================================================
# Instrumentation self-test (MANDATORY at module scope before any dispatch)
# ========================================================================================
def _instrumentation_selftest():
    mdl_ctrl = MDL_BASE.run_positive_control()
    assert mdl_ctrl["passed"], "SELFTEST FAIL: MDL XOR positive control did not pass: %r" % mdl_ctrl
    vsa_ctrl = VSA_BASE.run_positive_control()
    assert vsa_ctrl["passed"], "SELFTEST FAIL: VSA synthetic positive control did not pass: %r" % vsa_ctrl

    items_cleaned = clean_items()
    assert len(items_cleaned) == 27, "SELFTEST FAIL: expected 27 cleaned items, got %d" % len(items_cleaned)
    ids = [it["id"] for it in items_cleaned]
    assert len(ids) == len(set(ids)), "SELFTEST FAIL: duplicate ids after cleaning"
    assert not (EXPECTED_DROPPED_IDS & set(ids)), "SELFTEST FAIL: a dropped id survived cleaning"
    met = sum(1 for it in items_cleaned if it["gold"] == "MET")
    unmet = sum(1 for it in items_cleaned if it["gold"] == "UNMET")
    assert met == 15 and unmet == 12, "SELFTEST FAIL: expected 15 MET / 12 UNMET, got %d/%d" % (met, unmet)

    split_seed, episodes, hard_missed = find_split(items_cleaned)
    train = [it for it in episodes if it["split"] == "train"]
    test = [it for it in episodes if it["split"] == "test"]
    assert len(train) == 12 and len(test) == 15, "SELFTEST FAIL: split sizes wrong (train=%d test=%d)" % (len(train), len(test))
    assert set(it["id"] for it in train).isdisjoint(set(it["id"] for it in test)), "SELFTEST FAIL: split overlap"
    for split_name, split_list in (("train", train), ("test", test)):
        subtypes = set(it["subtype"] for it in split_list)
        assert {"direct", "idiomatic", "concession"} <= subtypes, \
            "SELFTEST FAIL: %s split is not a mix of all 3 subtypes (got %r) -- domain-shift not fixed" % (split_name, subtypes)
    ok, missed = hard_case_coverage_ok(test)
    assert ok and len(missed) >= 1, "SELFTEST FAIL: TEST does not contain a hand-list-missed idiomatic/concession member"

    # feat_fn determinism (imported, not reimplemented)
    a = MDL_BASE.feat_fn(episodes[0])
    b = MDL_BASE.feat_fn(episodes[0])
    assert a == b, "SELFTEST FAIL: feat_fn not deterministic"

    # cue-weight determinism
    w1 = compute_cue_weights(train)
    w2 = compute_cue_weights(train)
    assert w1 == w2, "SELFTEST FAIL: compute_cue_weights not deterministic"
    assert len(w1) >= 5, "SELFTEST FAIL: degenerate weight table (%d terms)" % len(w1)
    assert any(v > 0 for v in w1.values()), "SELFTEST FAIL: every cue weight is exactly 0 -- no discriminative signal at all"

    # VSA arm3 determinism + glass-box fields present
    vocab_vecs, _ = VSA_BASE.build_vocab(episodes)
    outcome_vecs = VSA_BASE.build_outcome_vecs()
    r1 = run_refined_vsa_arm(train, test, vocab_vecs, outcome_vecs)
    r2 = run_refined_vsa_arm(train, test, vocab_vecs, outcome_vecs)
    assert r1["digest_real"] == r2["digest_real"], "SELFTEST FAIL: arm3 predictions not deterministic"
    assert r1["digest_scramble"] == r2["digest_scramble"], "SELFTEST FAIL: arm3 scramble not deterministic"
    assert all("margin" in p and "sims" in p for p in r1["per_item"]), "SELFTEST FAIL: glass-box margins/sims missing"
    assert len(r1["per_item"]) == 15

    # MDL arm sanity: chosen hypothesis (if any) round-trips through json
    mdl_name, mdl_chosen, _all = MDL_BASE.module_fit(train, ["MET", "UNMET"])
    if mdl_chosen is not None:
        json.dumps(mdl_chosen.hypothesis)


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
        print("[SELFTEST] %s" % ("PASS" if ok else "FAIL"))
        sys.exit(0 if ok else 1)

    metrics = run_pipeline(run_mode=args.run_mode)
    _write_metrics(OUTPUT_DIR, metrics)
    print("[%s] verdict=%s" % (args.run_mode, metrics["verdict"]))
    print("[%s] " % args.run_mode + metrics["verdict_msg"])
    print(json.dumps({k: v for k, v in metrics.items() if k not in (
        "naive_superposition_arm2", "refined_superposition_arm3")}, indent=2, default=str))
    print("---- arm2 (naive) per-item ----")
    for p in metrics["naive_superposition_arm2"]["per_item"]:
        print(json.dumps(p, default=str))
    print("---- arm3 (refined) per-item ----")
    for p in metrics["refined_superposition_arm3"]["per_item"]:
        print(json.dumps(p, default=str))
    print("---- arm3 learned cue-weights (glass-box, sorted desc) ----")
    print(json.dumps(metrics["refined_superposition_arm3"]["weights"], indent=2))


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
