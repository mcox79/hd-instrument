#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_pragmatic_curriculum_dialogue_exemplar_knn_v1

OVERNIGHT DRILL: a different brain-faithful WAY to overcome the flat-bundle-superposition wall
(common-mode swamping, diagnosed in exp_pragmatic_curriculum_vsa_superposition_map_v1.py commit
93c0c39f6) on the SAME dialogue request/response construction-typing test. Prior ways bolted a
SELECTION/ATTENTION front-end onto the flat superposition (arm3, attention-weighted-flat, live
acc~0.667) or SHARDED the bundle by grammatical role before superposing (role-sharded binding,
commit 7f21a4d75, HARD_PASS live acc~0.7333). Both still build ONE averaged sup_map per class and
collapse a query into it.

THIS drill sidesteps the cross-item superposition map ENTIRELY: store each TRAIN item's cue-bundle
as a DISTINCT, un-superposed exemplar vector (no averaging across items at all -- no map to swamp);
type a held-out item by NEAREST-EXEMPLAR retrieval and inherit that exemplar's label. Brain basis:
Nosofsky's Generalized Context Model (GCM, 1986) -- categorization by similarity to stored exemplars,
optionally attention-weighted per dimension; Hintzman's MINERVA2 (1984) -- multiple-trace episodic
memory, no abstracted prototype; hippocampal pattern-separated episodic storage (dentate gyrus keeps
individual traces distinct rather than blending them, unlike a superposed cortical schema).

MECHANISM (near-zero new code, wire-don't-island): the RETRIEVAL primitive is hdlab.cleanup_family.
k_NN_lookup(query, codebook, *, k=1), REUSED UNMODIFIED -- this already IS nearest-exemplar lookup
(raw dot-product argmax over a codebook of un-superposed rows; k>1 returns the mean-of-top-k VECTOR
but not the top-k indices, so k=3 majority-vote is built by calling k_NN_lookup 3x, iteratively
peeling the previous winner out of the codebook -- no new distance/scoring code, only orchestration).

REAL-VECTOR ENCODING NOTE: k_NN_lookup is real-float32-only (`.astype(np.float32)`); the FHRR
cue-bundles here are torch complex64. Re(<a, conj(b)>) = dot(Re(a),Re(b)) + dot(Im(a),Im(b)), so
concatenating [Re(v), Im(v)] into one real (2*N_DIM,) vector and taking k_NN_lookup's plain real dot
product exactly reproduces hdlab.atoms.similarity's FHRR numerator (its argmax ranking is therefore
IDENTICAL, not an approximation). Ranking-equivalence to cosine similarity holds because
hdlab.bundling.bundle() FHRR-normalizes every vector to unit PER-COMPONENT magnitude, so every
cue-bundle (query or codebook row, real or GCM-weighted) has the SAME fixed L2 norm sqrt(N_DIM) --
raw dot product and cosine similarity rank identically.

DATA + FEATURES + SPLIT (reused verbatim, not re-authored -- apples-to-apples with arm2/arm3/
role-sharded): experiments.exp_pragmatic_curriculum_dialogue_request_response_dailydialog_v1 (DD)
clean_items() (27-item DailyDialog, indices 2/3/20 dropped) + find_split() (stratified split,
SPLIT_SEED_BASE=20260808100, TRAIN n=12 / TEST n=15); DD.MDL_BASE.feat_fn (glass-box cue extractor,
imported not copied); DD.VSA_BASE.build_vocab/build_outcome_vecs/build_cue_bundles (the SAME
equal-weight FHRR cue-bundle builder arm2 uses, N_DIM=1024) for the primary (unweighted) exemplar
arms; DD.compute_cue_weights/build_weighted_cue_bundles (arm3's own TRAIN-only discriminativeness
weighting, |P(MET|c)-P(MET|not c)|) for the optional GCM-attention-weighted exemplar arm.

ARMS (all measured, all on the SAME 27-item data / stratified split / features):
  1. knn_k1: unweighted cue-bundle codebook (12 TRAIN exemplars), k=1 nearest-exemplar lookup.
  2. knn_k3: same codebook, k=3 majority-vote (ties broken by the k=1/nearest label, glass-box
     logged).
  3. knn_k1_gcm / knn_k3_gcm (Nosofsky attention-weighted variant): codebook built from arm3's
     TRAIN-only discriminativeness-weighted cue-bundles instead of equal-weight ones.
  SCRAMBLE control (rigor, matches arm2/arm3/role-sharded's own single-fixed-seed convention,
  DD.SCRAMBLE_SEED, MDL_BASE.scramble_train_labels reused verbatim): for the unweighted arms this is
  a pure RE-TAG (the codebook vectors are label-independent by construction, so permuting TRAIN
  labels changes only which label a fixed nearest-exemplar identity returns); for the GCM arms the
  WHOLE weighted-bundle pipeline is refit from permuted-label TRAIN (weights + bundles + codebook),
  matching arm3's own scramble rigor.
  POSITIVE CONTROL (mechanism sanity, own synthetic cue-separated toy set, same generative pattern as
  VSA_BASE.run_positive_control but retrieved via k_NN_lookup instead of a superposition map): must
  recover >=0.80 with real labels and collapse to <=0.60 under scramble before the real-27-item
  numbers are trusted.

INCUMBENTS (measured LIVE in this same process, same split -- not stale numbers): DD.run_pipeline()
for arm2 (naive flat superposition, expect ~0.5333), arm3 (attention-weighted-flat, expect ~0.6667),
MDL learner (expect ~0.6000), majority floor (expect ~0.6000); the role-sharded module's
run_pipeline() for its own best arm (expect role_multi_combine_unweighted, ~0.7333, HARD_PASS commit
7f21a4d75) -- all re-measured, not hand-typed, so any drift in a sibling module is caught immediately
by the split-seed cross-check assertions below.

GATE (pre-registered; anti-premature-HARD_FAIL protocol governs any non-pass; brain=existence-proof,
a miss is a fidelity-gap diagnosis, not a ceiling claim):
  HARD-PASS: best exemplar-KNN arm's held-out acc > role-sharded's LIVE best acc, non-constant
    predictions, AND its scramble control collapses (acc_scramble <= DD.SCRAMBLE_BAND=0.60) ->
    exemplar memory is the best brain-faithful mechanism at this data density.
  PARTIAL: best arm lands in [arm3_live_acc, role_sharded_live_acc] and is non-constant -> a valid
    complementary way (note: exemplar memory scales differently from a superposed map -- no bundle-
    capacity wall, but its cost grows with stored-exemplar count, not fixed-map size).
  HARD-FAIL band: best arm <= arm2's LIVE acc AND digest_real == digest_scramble (constant collapse)
    -> DIAGNOSE (over-fitting 12 tiny exemplars? cue-bundles too similar to discriminate? n too
    small?) -- NOT a ceiling claim without that diagnosis (mean pairwise codebook cosine similarity
    reported for exactly this check).
  Anything between PARTIAL and HARD-FAIL band is reported as MIDDLE_BAND with the specific failing
  gate condition named.

COMPUTE: n=27 items, N_DIM=1024 dense complex64 (FHRR) -> 2048-dim real concatenation for k_NN_lookup
only; closed-form, no training loop. Wall time sub-second. LOCAL-ONLY, foreground-to-completion; NO
queue, NO push, NO remote-persist, NO hdlab mutation, NO atom bank (skunkworks VETs). Deterministic:
OMP/MKL/OPENBLAS_NUM_THREADS=1, fixed torch.Generator seeds (VSA_BASE.VOCAB_SEED/OUTCOME_SEED,
reused unmodified), fixed-int random.Random seed (DD.SCRAMBLE_SEED, reused unmodified) for every
scramble permutation, fixed-sequence seed search for the split (DD.find_split, reused unmodified).
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
from collections import Counter
from datetime import datetime, timezone

import numpy as np
import torch

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ANCHOR_NAME = "pragmatic_curriculum_dialogue_exemplar_knn_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab import atoms, cleanup_family  # noqa: E402  (REUSE: k_NN_lookup IS nearest-exemplar retrieval)
import experiments.exp_pragmatic_curriculum_dialogue_request_response_first_test_v1 as MDL_BASE  # noqa: E402
import experiments.exp_pragmatic_curriculum_vsa_superposition_map_v1 as VSA_BASE  # noqa: E402
import experiments.exp_pragmatic_curriculum_dialogue_request_response_dailydialog_v1 as DD  # noqa: E402
import experiments.exp_pragmatic_curriculum_dialogue_role_sharded_binding_v1 as ROLE_MOD  # noqa: E402

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
EPS = 1e-9
SCRAMBLE_SEED = DD.SCRAMBLE_SEED
SCRAMBLE_BAND = DD.SCRAMBLE_BAND
CTRL_SEED = 20260808300
CTRL_N_PER_CLASS = 6
CTRL_SCRAMBLE_TRIALS = 9
BAND_CTRL_ACC_MIN = 0.80
BAND_CTRL_SCR_MAX = 0.60


# ========================================================================================
# Real-vector encoding of FHRR complex64 cue-bundles (see module docstring "REAL-VECTOR ENCODING
# NOTE" for the exactness proof) + the owned k-NN retrieval primitive (hdlab.cleanup_family.k_NN_lookup)
# ========================================================================================
def to_real(vec):
    """torch complex64 (n,) -> real numpy float32 (2n,) via concat(Re, Im)."""
    v = vec.detach().cpu().numpy()
    return np.concatenate([v.real, v.imag]).astype(np.float32)


def build_codebook(items, cue_bundles):
    """items -> (codebook (M, 2*N_DIM) float32, labels list[str], ids list[str]), all in `items`
    iteration order (un-superposed: one DISTINCT row per TRAIN item, no cross-item averaging)."""
    ids = [it["id"] for it in items]
    labels = [it["gold_class"] for it in items]
    mat = np.stack([to_real(cue_bundles[i]) for i in ids], axis=0).astype(np.float32)
    return mat, labels, ids


def knn1_predict_all(test_items, query_bundles, codebook, labels, ids):
    """k=1 nearest-exemplar lookup via hdlab.cleanup_family.k_NN_lookup, unmodified."""
    preds, retrieved = [], []
    for it in test_items:
        q = to_real(query_bundles[it["id"]])
        _, diag = cleanup_family.k_NN_lookup(q, codebook, k=1)
        idx = diag["final_argmax_idx"]
        preds.append(labels[idx])
        retrieved.append({"retrieved_train_id": ids[idx], "retrieved_label": labels[idx],
                           "tie": False, "k_used": 1})
    return preds, retrieved


def knn3_predict_all(test_items, query_bundles, codebook, labels, ids):
    """k=3 majority-vote: k_NN_lookup(k=1) is called repeatedly, PEELING the previous winner out of
    the codebook each time (no reimplementation of the distance/scoring formula -- 3 calls to the
    SAME owned primitive). Tie-break: the k=1 (nearest) label wins, glass-box logged."""
    preds, retrieved = [], []
    for it in test_items:
        q = to_real(query_bundles[it["id"]])
        avail = list(range(len(labels)))
        picked = []
        for _ in range(min(3, len(avail))):
            sub_cb = codebook[avail]
            _, diag = cleanup_family.k_NN_lookup(q, sub_cb, k=1)
            local_idx = diag["final_argmax_idx"]
            global_idx = avail[local_idx]
            picked.append(global_idx)
            del avail[local_idx]
        picked_labels = [labels[i] for i in picked]
        counts = Counter(picked_labels)
        max_count = max(counts.values())
        winners = sorted(l for l, c in counts.items() if c == max_count)
        tie = len(winners) > 1
        pred = picked_labels[0] if tie else winners[0]  # tie-break: nearest (1st-picked) label
        preds.append(pred)
        retrieved.append({"retrieved_train_id": ids[picked[0]], "retrieved_label": pred,
                           "retrieved_train_ids_k3": [ids[i] for i in picked],
                           "retrieved_labels_k3": picked_labels, "tie": tie, "k_used": 3})
    return preds, retrieved


def _digest(preds):
    return hashlib.sha256(json.dumps(preds).encode()).hexdigest()[:16]


def _arm_result(name, k, test, preds, retrieved, preds_scr):
    gold = [it["gold_class"] for it in test]
    acc = MDL_BASE.accuracy(preds, gold)
    acc_scr = MDL_BASE.accuracy(preds_scr, gold)
    dig_real, dig_scr = _digest(preds), _digest(preds_scr)
    n_distinct = len(set(preds))
    per_item = []
    for it, pred, ret in zip(test, preds, retrieved):
        correct = pred == it["gold_class"]
        row = {"id": it["id"], "subtype": it.get("subtype"), "gold": it["gold_class"],
               "pred": pred, "correct": bool(correct)}
        row.update(ret)
        per_item.append(row)
    return {
        "name": name, "k": k, "n_train": None, "n_test": len(test),
        "acc": acc, "acc_scramble": acc_scr,
        "scramble_delta": (acc - acc_scr) if (acc is not None and acc_scr is not None) else None,
        "digest_real": dig_real, "digest_scramble": dig_scr,
        "arms_differ_real_vs_scramble": dig_real != dig_scr,
        "collapsed_to_constant": n_distinct <= 1,
        "n_distinct_preds": n_distinct,
        "per_item": per_item,
    }


def mean_pairwise_cosine(codebook):
    """Diagnostic (for the HARD-FAIL branch): mean off-diagonal cosine similarity among codebook
    rows -- high values mean the TRAIN exemplars are too similar to discriminate."""
    cb = codebook.astype(np.float32)
    norms = np.linalg.norm(cb, axis=1, keepdims=True)
    norms = np.where(norms > 0, norms, 1.0)
    normed = cb / norms
    sim = normed @ normed.T
    n = sim.shape[0]
    if n < 2:
        return None
    iu = np.triu_indices(n, k=1)
    return float(sim[iu].mean())


# ========================================================================================
# Arm runners
# ========================================================================================
def run_unweighted_knn(train, test, cue_bundles):
    codebook, labels, ids = build_codebook(train, cue_bundles)

    train_scr = MDL_BASE.scramble_train_labels(train, seed=SCRAMBLE_SEED)
    labels_scr = [it["gold_class"] for it in train_scr]
    ids_scr = [it["id"] for it in train_scr]
    assert ids_scr == ids, "INSTRUMENTATION_SUSPECT: scramble_train_labels reordered items"
    # NOTE: the unweighted codebook is label-independent (built purely from each item's own
    # features), so "SCRAMBLE control, re-tag codebook" IS exactly reusing `codebook` unchanged with
    # `labels_scr` swapped in -- no reconstruction needed (verified: ids_scr == ids above).

    preds1, ret1 = knn1_predict_all(test, cue_bundles, codebook, labels, ids)
    preds1_scr, _ = knn1_predict_all(test, cue_bundles, codebook, labels_scr, ids)
    k1 = _arm_result("knn_k1", 1, test, preds1, ret1, preds1_scr)
    k1["n_train"] = len(train)

    preds3, ret3 = knn3_predict_all(test, cue_bundles, codebook, labels, ids)
    preds3_scr, _ = knn3_predict_all(test, cue_bundles, codebook, labels_scr, ids)
    k3 = _arm_result("knn_k3", 3, test, preds3, ret3, preds3_scr)
    k3["n_train"] = len(train)

    k1["mean_pairwise_train_cosine"] = mean_pairwise_cosine(codebook)
    return k1, k3


def run_gcm_knn(train, test, vocab_vecs, feat_fn):
    """Nosofsky GCM-style attention-weighted exemplar distance: codebook built from arm3's own
    TRAIN-only discriminativeness weights (DD.compute_cue_weights) instead of equal-weight bundling."""
    weights = DD.compute_cue_weights(train, feat_fn=feat_fn)
    bundles_train, fb_train = DD.build_weighted_cue_bundles(train, vocab_vecs, weights, feat_fn=feat_fn)
    bundles_test, fb_test = DD.build_weighted_cue_bundles(test, vocab_vecs, weights, feat_fn=feat_fn)
    codebook, labels, ids = build_codebook(train, bundles_train)

    # SCRAMBLE: refit the WHOLE weighted pipeline (weights + bundles + codebook) from permuted-label
    # TRAIN, matching arm3's own scramble rigor (weights are label-dependent here, unlike the
    # unweighted arm above).
    train_scr = MDL_BASE.scramble_train_labels(train, seed=SCRAMBLE_SEED)
    weights_scr = DD.compute_cue_weights(train_scr, feat_fn=feat_fn)
    bundles_train_scr, fb_train_scr = DD.build_weighted_cue_bundles(train_scr, vocab_vecs, weights_scr, feat_fn=feat_fn)
    bundles_test_scr, fb_test_scr = DD.build_weighted_cue_bundles(test, vocab_vecs, weights_scr, feat_fn=feat_fn)
    codebook_scr, labels_scr, ids_scr = build_codebook(train_scr, bundles_train_scr)

    preds1, ret1 = knn1_predict_all(test, bundles_test, codebook, labels, ids)
    preds1_scr, _ = knn1_predict_all(test, bundles_test_scr, codebook_scr, labels_scr, ids_scr)
    k1g = _arm_result("knn_k1_gcm", 1, test, preds1, ret1, preds1_scr)
    k1g["n_train"] = len(train)
    k1g["n_fallback_items_train_real"] = len(fb_train)
    k1g["n_fallback_items_train_scrambled"] = len(fb_train_scr)
    k1g["weights_top8"] = dict(sorted(weights.items(), key=lambda kv: -kv[1])[:8])

    preds3, ret3 = knn3_predict_all(test, bundles_test, codebook, labels, ids)
    preds3_scr, _ = knn3_predict_all(test, bundles_test_scr, codebook_scr, labels_scr, ids_scr)
    k3g = _arm_result("knn_k3_gcm", 3, test, preds3, ret3, preds3_scr)
    k3g["n_train"] = len(train)

    return k1g, k3g


# ========================================================================================
# Positive control (mechanism sanity for the RETRIEVAL primitive itself -- same generative pattern
# as VSA_BASE.run_positive_control's synthetic cue-separated toy set, disjoint train/test noise
# tokens so exact-key lookup is impossible, but typed via k_NN_lookup instead of a superposition map)
# ========================================================================================
def _ctrl_feat_fn(item):
    f = item["_ctrl_features"]
    return ["%s=%s" % (k, v) for k, v in f.items()]


def run_positive_control(seed=CTRL_SEED, d=256):
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
    cue_bundles = {it["id"]: VSA_BASE.response_cue_bundle(it, vocab_vecs, feat_fn=_ctrl_feat_fn)
                   for it in all_items}

    codebook, labels, ids = build_codebook(train, cue_bundles)
    preds, _ = knn1_predict_all(test, cue_bundles, codebook, labels, ids)
    gold = [it["gold_class"] for it in test]
    acc = MDL_BASE.accuracy(preds, gold)

    # averaged over fixed pre-declared scramble trials (same rationale as VSA_BASE.run_positive_control:
    # only 2 discriminating cue-groups -> a single scramble seed is quantized/unstable at this n).
    scr_accs = []
    for trial in range(1, CTRL_SCRAMBLE_TRIALS + 1):
        train_scr = MDL_BASE.scramble_train_labels(train, seed=seed + trial)
        labels_scr = [it["gold_class"] for it in train_scr]
        preds_scr, _ = knn1_predict_all(test, cue_bundles, codebook, labels_scr, ids)
        scr_accs.append(MDL_BASE.accuracy(preds_scr, gold))
    acc_scr_mean = sum(scr_accs) / len(scr_accs)

    passed = (acc >= BAND_CTRL_ACC_MIN) and (acc_scr_mean <= BAND_CTRL_SCR_MAX)
    return {"acc": acc, "acc_scramble": acc_scr_mean, "acc_scramble_trials": scr_accs,
            "passed": bool(passed)}


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

    items_cleaned = DD.clean_items()
    split_seed, episodes, hard_missed = DD.find_split(items_cleaned)
    assert len(episodes) == 27
    train = [it for it in episodes if it["split"] == "train"]
    test = [it for it in episodes if it["split"] == "test"]
    assert len(train) == 12 and len(test) == 15, (
        "INSTRUMENTATION_SUSPECT: split sizes drifted (train=%d test=%d)" % (len(train), len(test)))

    vocab_vecs, vocab_terms = VSA_BASE.build_vocab(episodes)
    cue_bundles = VSA_BASE.build_cue_bundles(episodes, vocab_vecs)  # naive equal-weight, reused

    knn_k1, knn_k3 = run_unweighted_knn(train, test, cue_bundles)
    knn_k1_gcm, knn_k3_gcm = run_gcm_knn(train, test, vocab_vecs, MDL_BASE.feat_fn)

    # ---- cited/re-measured LIVE incumbents (not stale numbers), same split cross-checked ----
    dd_metrics = DD.run_pipeline(run_mode="exemplar_knn_comparison_reference")
    assert dd_metrics["split"]["seed_used"] == split_seed, (
        "INSTRUMENTATION_SUSPECT: split seed drift between this cell's own find_split() call and "
        "DD.run_pipeline()'s internal call -- not apples-to-apples any more")
    arm2_acc = dd_metrics["naive_superposition_arm2"]["acc"]
    arm3_acc = dd_metrics["refined_superposition_arm3"]["acc"]
    mdl_acc = dd_metrics["mdl_arm"]["held_out_accuracy"]
    maj_acc = dd_metrics["majority_class_floor"]["held_out_accuracy"]

    role_metrics = ROLE_MOD.run_pipeline(run_mode="exemplar_knn_comparison_reference")
    assert role_metrics["split"]["seed_used"] == split_seed, (
        "INSTRUMENTATION_SUSPECT: split seed drift between this cell's own find_split() call and "
        "ROLE_MOD.run_pipeline()'s internal call -- not apples-to-apples any more")
    role_acc = role_metrics["best_arm_acc"]
    role_name = role_metrics["best_arm_name"]

    # ---- gate ----
    candidate_arms = {"knn_k1": knn_k1, "knn_k3": knn_k3,
                       "knn_k1_gcm": knn_k1_gcm, "knn_k3_gcm": knn_k3_gcm}
    best_name = max(candidate_arms, key=lambda k: (candidate_arms[k]["acc"]
                                                     if candidate_arms[k]["acc"] is not None else -1.0))
    best_arm = candidate_arms[best_name]

    ctrl_ok = ctrl["passed"]
    best_non_constant = best_arm["n_distinct_preds"] > 1
    best_scramble_collapses = (best_arm["acc_scramble"] is not None
                                and best_arm["acc_scramble"] <= SCRAMBLE_BAND + EPS)
    beats_role = best_arm["acc"] is not None and best_arm["acc"] > role_acc + EPS
    matches_band = (best_arm["acc"] is not None
                     and (arm3_acc - EPS) <= best_arm["acc"] <= (role_acc + EPS))
    at_or_below_arm2 = best_arm["acc"] is not None and best_arm["acc"] <= arm2_acc + EPS
    best_constant_collapse = best_arm["digest_real"] == best_arm["digest_scramble"]

    hard_pass = ctrl_ok and beats_role and best_non_constant and best_scramble_collapses
    partial = ctrl_ok and (not hard_pass) and matches_band and best_non_constant
    hard_fail_band = ctrl_ok and at_or_below_arm2 and best_constant_collapse

    mean_cos = knn_k1.get("mean_pairwise_train_cosine")

    if not ctrl_ok:
        verdict = "HARD_FAIL_MECHANISM"
        msg = ("Positive control failed: synthetic cue-separated toy set acc=%.3f (want >= %.2f) "
               "scramble_mean=%.3f (want <= %.2f) -- the k-NN exemplar retrieval plumbing itself is "
               "not working; do not trust the real-27-item numbers below." %
               (ctrl["acc"], BAND_CTRL_ACC_MIN, ctrl["acc_scramble"], BAND_CTRL_SCR_MAX))
    elif hard_pass:
        verdict = "HARD_PASS"
        msg = ("HARD_PASS: best exemplar-KNN arm (%s, acc=%.4f) BEATS role-sharded's LIVE best "
               "(%s, acc=%.4f), non-constant (n_distinct_preds=%d), scramble collapses "
               "(acc_scr=%.4f <= band=%.2f) -> exemplar memory (Nosofsky GCM / Hintzman MINERVA2 / "
               "hippocampal pattern separation) is the best brain-faithful way at this data density." %
               (best_name, best_arm["acc"], role_name, role_acc, best_arm["n_distinct_preds"],
                best_arm["acc_scramble"], SCRAMBLE_BAND))
    elif partial:
        verdict = "PARTIAL_MATCHES_BAND"
        msg = ("PARTIAL: best exemplar-KNN arm (%s, acc=%.4f) lands in the [arm3=%.4f, "
               "role_sharded=%.4f] band, non-constant -- a valid complementary way (exemplar memory "
               "scales by stored-exemplar count, not a fixed superposed map, so its capacity profile "
               "differs from both arm3 and role-sharded even without a strict win here). "
               "scramble=%.4f (%s)." %
               (best_name, best_arm["acc"], arm3_acc, role_acc, best_arm["acc_scramble"],
                "collapses" if best_scramble_collapses else "did NOT collapse"))
    elif hard_fail_band:
        verdict = "HARD_FAIL_DIAGNOSED"
        msg = ("HARD-FAIL band: best exemplar-KNN arm (%s, acc=%.4f) <= arm2's LIVE acc=%.4f AND "
               "digest_real==digest_scramble (constant collapse). DIAGNOSIS (not a ceiling claim): "
               "mean pairwise cosine similarity among the 12 TRAIN codebook rows = %s (near 1.0 "
               "would mean the exemplars are too similar to discriminate -- likely if the near-"
               "universal filler cues identified in the arm2/arm3 common-mode-swamping diagnosis "
               "dominate every item's bundle regardless of superposition; n_train=12 is also simply "
               "tiny for a k=1/3 nearest-exemplar rule to beat luck). See per_item retrieved-exemplar "
               "records below to distinguish 'wrong nearest neighbor picked' from 'right neighbor, "
               "wrong label under scramble-luck'." %
               (best_name, best_arm["acc"], arm2_acc, ("%.4f" % mean_cos) if mean_cos is not None else "n/a"))
    else:
        verdict = "MIDDLE_BAND"
        msg = ("MIDDLE_BAND: best exemplar-KNN arm (%s, acc=%.4f) neither beats role_sharded=%.4f "
               "nor falls in the [arm3=%.4f, role_sharded] band cleanly, nor collapses to the arm2 "
               "hard-fail floor (arm2=%.4f) -- see gate booleans for the specific failing condition." %
               (best_name, best_arm["acc"], role_acc, arm3_acc, arm2_acc))

    elapsed = time.perf_counter() - t0

    money_glass_box = [{"id": p["id"], "subtype": p["subtype"], "gold": p["gold"], "pred": p["pred"],
                         "correct": p["correct"], "retrieved_train_id": p.get("retrieved_train_id"),
                         "retrieved_label": p.get("retrieved_label")}
                        for p in best_arm["per_item"][:5]]

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "verdict": verdict, "verdict_msg": msg,
        "summary": msg, "elapsed_s": round(elapsed, 4),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "positive_control": ctrl,
        "split": {"seed_used": split_seed, "n_train": len(train), "n_test": len(test)},
        "incumbents": {
            "role_sharded_LIVE": {"name": role_name, "acc": role_acc,
                                   "source": "exp_pragmatic_curriculum_dialogue_role_sharded_binding_v1.py, HARD_PASS commit 7f21a4d75"},
            "arm3_attention_weighted_flat_LIVE": arm3_acc,
            "arm2_naive_flat_LIVE": arm2_acc,
            "mdl_LIVE": mdl_acc,
            "majority_floor_LIVE": maj_acc,
        },
        "arms": {"knn_k1": knn_k1, "knn_k3": knn_k3,
                 "knn_k1_gcm": knn_k1_gcm, "knn_k3_gcm": knn_k3_gcm},
        "best_arm_name": best_name, "best_arm_acc": best_arm["acc"],
        "mean_pairwise_train_cosine_unweighted": mean_cos,
        "gates": {
            "positive_control_passed": ctrl_ok,
            "best_non_constant": best_non_constant,
            "best_scramble_collapses": best_scramble_collapses,
            "beats_role_sharded": beats_role,
            "matches_arm3_to_role_band": matches_band,
            "at_or_below_arm2_and_constant": hard_fail_band,
            "hard_pass": hard_pass, "partial": partial, "hard_fail_band": hard_fail_band,
            "scramble_band": SCRAMBLE_BAND,
        },
        "glass_box_money_items": money_glass_box,
        "cell_chunked": False, "final_metrics_atomicity": "tmp_replace",
        "deterministic_seeding": True, "scramble_seed": SCRAMBLE_SEED, "split_seed": split_seed,
        "cardinality_ok": True, "expected_n_units": 1,
    }
    return metrics


# ========================================================================================
# Instrumentation self-test (MANDATORY at module scope before any dispatch)
# ========================================================================================
def _instrumentation_selftest():
    ctrl = run_positive_control()
    assert ctrl["passed"], "SELFTEST FAIL: k-NN positive control did not pass: %r" % ctrl

    items_cleaned = DD.clean_items()
    split_seed, episodes, _ = DD.find_split(items_cleaned)
    train = [it for it in episodes if it["split"] == "train"]
    test = [it for it in episodes if it["split"] == "test"]
    assert len(train) == 12 and len(test) == 15, "SELFTEST FAIL: split sizes wrong"

    vocab_vecs, _ = VSA_BASE.build_vocab(episodes)
    cue_bundles = VSA_BASE.build_cue_bundles(episodes, vocab_vecs)

    # real-vector encoding sanity: to_real dot product must equal atoms.similarity's FHRR numerator
    a_id, b_id = train[0]["id"], train[1]["id"]
    a, b = cue_bundles[a_id], cue_bundles[b_id]
    n = a.shape[0]
    expected = float((a * b.conj()).sum().real)  # = atoms.similarity(a,b) * n
    got = float(np.dot(to_real(a), to_real(b)))
    assert abs(expected - got) < 1e-2, (
        "SELFTEST FAIL: to_real dot product (%r) does not match FHRR Re(<a,conj(b)>) (%r)" % (got, expected))

    # codebook build determinism
    cb1, labels1, ids1 = build_codebook(train, cue_bundles)
    cb2, labels2, ids2 = build_codebook(train, cue_bundles)
    assert np.allclose(cb1, cb2) and labels1 == labels2 and ids1 == ids2, \
        "SELFTEST FAIL: build_codebook not deterministic"
    assert cb1.shape == (12, 2 * VSA_BASE.N_DIM), "SELFTEST FAIL: codebook shape wrong: %r" % (cb1.shape,)

    # k=1 / k=3 determinism
    preds1a, _ = knn1_predict_all(test, cue_bundles, cb1, labels1, ids1)
    preds1b, _ = knn1_predict_all(test, cue_bundles, cb1, labels1, ids1)
    assert preds1a == preds1b, "SELFTEST FAIL: knn1 not deterministic"
    preds3a, _ = knn3_predict_all(test, cue_bundles, cb1, labels1, ids1)
    preds3b, _ = knn3_predict_all(test, cue_bundles, cb1, labels1, ids1)
    assert preds3a == preds3b, "SELFTEST FAIL: knn3 not deterministic"
    assert len(preds1a) == 15 and len(preds3a) == 15

    # k=1 sanity: the retrieved label must actually come from the codebook's own label set
    assert set(preds1a) <= set(labels1), "SELFTEST FAIL: knn1 predicted a label not in the codebook"

    # GCM arm runs without crashing and produces 15 predictions
    k1g, k3g = run_gcm_knn(train, test, vocab_vecs, MDL_BASE.feat_fn)
    assert len(k1g["per_item"]) == 15 and len(k3g["per_item"]) == 15

    # full pipeline smoke (also exercises the DD/ROLE_MOD cross-check assertions)
    m = run_pipeline(run_mode="selftest_smoke")
    assert m["verdict"] not in ("CELL_CRASHED",)
    assert m["split"]["n_train"] == 12 and m["split"]["n_test"] == 15


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
    print(json.dumps({k: v for k, v in metrics.items() if k != "arms"}, indent=2, default=str))
    print("---- arms per-item ----")
    for arm_name, arm in metrics["arms"].items():
        print("-- %s (acc=%s, acc_scramble=%s, n_distinct=%s) --" %
              (arm_name, arm["acc"], arm["acc_scramble"], arm["n_distinct_preds"]))
        for p in arm["per_item"]:
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
