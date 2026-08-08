#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_pragmatic_curriculum_dialogue_role_sharded_shard_attention_v1

THE FOLLOW-UP TO THE DECISIVE SCALING TEST (commit d6c90eab6): at n_train=40 on the 72-item clean-
modern-DailyDialog scaling set, ATTENTION-FLAT (discriminativeness-weighted flat superposition) WON
(0.783) over ROLE-SHARDED with an UNWEIGHTED shard combiner (0.533) -- because the equal-weight
shard-sum lets an ANTI-informative REQUEST shard (below-chance train signal) swamp the good
RESPONSE_POLARITY shard's vote. That cell's own ad-hoc diagnosis found the RESPONSE_POLARITY shard
ALONE scores ~0.82 (> attention-flat's 0.783) when routed to in isolation. This cell tests, properly
and at scale (same n_train=40, same >=5 seeds, same fixed TEST set), whether adding SHARD-LEVEL
SELECTION/WEIGHTING to the sharded architecture actually beats plain attention-flat -- i.e. whether
attention needs to be applied ONLY at the cue level (attention-flat's answer) or at BOTH the cue
level AND the shard level (this cell's hypothesis).

MECHANISM (NEW, this cell): a per-shard weight is estimated ON TRAIN ONLY via LEAVE-ONE-OUT
cross-validation of that shard's OWN sup_map (shard_train_loo_accuracy below) -- NOT a naive
self-predict-on-full-TRAIN readout, which would trivially read ~1.0 for every shard (bind-then-unbind
on an item that itself contributed to the map recovers close to that item's own outcome almost by
construction at small n) and make even the anti-informative REQUEST shard falsely look maximally
informative. LOO folds out each TRAIN item once, rebuilds the shard's map on the other n-1, and
predicts the held-out item -- an honest, TRAIN-only, cross-validated readout-accuracy per shard.
  SHARD-WEIGHTED combine: weight_r = max(0, loo_acc_r - 0.5) (a shard at or below chance contributes
    a weight of exactly/toward 0; a shard well above chance dominates the sum), applied to each role's
    similarity-vector BEFORE summing across roles and taking argmax (attention at the SHARD level,
    layered on top of RS.collapse_predict_multi_role's existing per-role unbind+similarity). Degenerate
    guard: if EVERY shard's raw weight is <=0 (no shard beats chance on this TRAIN draw), falls back to
    equal weighting across all shards (glass-box logged, mirrors this codebase's existing per-item/
    per-shard fallback convention in arm3 / role_sharded_binding_v1's COMPOSED arm).
  SHARD-SELECT (hard): route via ONLY the single role with the highest TRAIN LOO accuracy (expected =
    RESPONSE_POLARITY, matching the scaling cell's own ad-hoc ~0.82 lead) -- the one-hot limit of
    shard-weighted, measured properly with seeds + a scramble control this time.
  BOTH-LEVELS (optional, exploratory): shard-level weighting (as above) COMBINED with within-shard
    cue-level discriminativeness weighting (DD.compute_cue_weights applied inside each role's own
    sub-bundle, exactly role_sharded_binding_v1.py's COMPOSED construction) -- attention at both the
    cue level (arm3's mechanism) and the shard level (this cell's new mechanism) simultaneously.
Every one of these reuses RS.build_role_subbundles / RS.role_cue_bundles_dict / RS.build_multi_role_
maps / VSA_BASE.build_map / VSA_BASE.collapse_predict / hdlab.binding.unbind / hdlab.atoms.similarity
UNMODIFIED (called, not copied) -- the only new code is the LOO shard-scoring function and the
shard-weighted combine/select wrappers around RS's existing per-role machinery.

DATA + HARNESS (byte-identical reuse -- apples-to-apples with the scaling result): the SAME 72-item
scaling file (experiments/data/dialogue_request_response_dailydialog_scaling_v1.jsonl) via
SCALE.load_scaling_items(), the SAME fixed gold-stratified TEST split (SCALE.stratified_test_split,
SCALE.SPLIT_SEED, SCALE.TEST_SIZE=24), the SAME gold-stratified train-subsample draw (SCALE.
subsample_train, SCALE.SUBSAMPLE_SEED_BASE + n_train*1000 + seed_idx formula) at the SAME decisive
n_train=40 with the SAME N_SEEDS=5 seed indices (0..4) -- so this cell's train/test sets are BYTE-
IDENTICAL to the n_train=40 points already measured in the scaling cell, not merely comparable. The
five incumbent arms (majority / MDL / naive-flat / attention-flat / role-sharded-unweighted) are
re-measured by literally CALLING SCALE.run_one_point(...) (unmodified), not re-derived, so their
numbers at n_train=40 must reproduce the scaling cell's own 0.783 / 0.533 landed figures exactly
(verified in the instrumentation self-test below).

PRE-REGISTERED GATE (fixed BEFORE running; anti-premature-HARD_FAIL; brain=existence-proof so any
non-pass is a diagnosis, not a ceiling claim):
  best_new_arm = argmax(mean_acc over 5 seeds) among {role_shard_weighted, role_shard_select,
    role_shard_weighted_composed_both_levels}.
  HARD-PASS: best_new_arm's mean acc > attention-flat's mean acc (strict), best_new_arm is
    non-constant at every seed (n_distinct_preds > 1), AND its scramble control collapses
    (mean_acc_scramble <= SCALE.SCRAMBLE_BAND=0.60) -> attention belongs at BOTH the cue level AND the
    shard level; wire the shard-weighted/select combiner into the role-sharded architecture.
  PARTIAL/CONVERGE (TIE_BAND=0.02, a round, not-tuned-to-outcome margin): best_new_arm's mean acc is
    within [attention_flat_acc - 0.02, attention_flat_acc] (ties, does not clear the strict HARD-PASS
    bar) -> attention-flat alone is the simplest sufficient winner; wire it (Occam), shard-level
    weighting is not decisively additive at this n/density.
  BELOW: best_new_arm's mean acc < attention_flat_acc - 0.02 -> diagnose honestly (LOO-fold sparsity
    at n_train=40/4-way-shard ~10 items/shard, shard-map interference, etc.) -- NOT a ceiling claim.
SCRAMBLE CONTROLS: every new arm computes its own scramble control (SCALE.SCRAMBLE_SEED, MDL_BASE.
scramble_train_labels reused unmodified; for role_shard_weighted/role_shard_select the shard LOO
scores AND the resulting weights/selection are RE-DERIVED from the permuted-label TRAIN, matching
arm3/COMPOSED's own rigor -- not just the final sup_map). Reported at n_train=40 for every arm.
GLASS-BOX: per-shard TRAIN LOO accuracies (mean over 5 seeds) and the resulting weights (which shards
get up/down-weighted) are reported per arm; digest_real vs digest_scramble and n_distinct_preds are
reported for the scramble control on every new arm.

COMPUTE: n_train=40 fixed (the decisive scale), N_SEEDS=5, 4 roles x 40 LOO folds per shard-scoring
call (real + scramble, x3 arms that need shard scores) -- all closed-form dense-tensor ops (N_DIM=1024
FHRR complex64), no training loop; the codebase's own comparable cells report sub-few-seconds wall
time at this scale. LOCAL-ONLY, foreground-to-completion; NO queue, NO push, NO remote-persist, NO
hdlab mutation, NO atom bank (skunkworks VETs). Deterministic: OMP/MKL/OPENBLAS_NUM_THREADS=1,
SCALE's own fixed torch.Generator seeds (VOCAB_SEED/OUTCOME_SEED via VSA_BASE, reused unmodified),
fixed-int random.Random seeds for the TEST split / per-seed train subsample / every scramble
permutation (all reused from SCALE/MDL_BASE, unmodified).
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

ANCHOR_NAME = "pragmatic_curriculum_dialogue_role_sharded_shard_attention_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab import binding, atoms  # noqa: E402  (REUSE: unbind/similarity primitives)
import experiments.exp_pragmatic_curriculum_dialogue_request_response_first_test_v1 as MDL_BASE  # noqa: E402
import experiments.exp_pragmatic_curriculum_vsa_superposition_map_v1 as VSA_BASE  # noqa: E402
import experiments.exp_pragmatic_curriculum_dialogue_request_response_dailydialog_v1 as DD  # noqa: E402
import experiments.exp_pragmatic_curriculum_dialogue_role_sharded_binding_v1 as RS  # noqa: E402
import experiments.exp_pragmatic_curriculum_dialogue_role_sharded_scaling_v1 as SCALE  # noqa: E402

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- Pre-registered config / gate (see module docstring). Everything scale/split/seed-related is
# REUSED from SCALE, not redefined, so this cell's train/test sets are byte-identical to the scaling
# cell's own n_train=40 points. ----
N_TRAIN = 40                 # the decisive scale from the scaling cell
N_SEEDS = SCALE.N_SEEDS       # 5
TIE_BAND = 0.02               # round, pre-declared, not tuned to outcome
EPS = 1e-9
ROLES = RS.ROLES


# ========================================================================================
# NEW: per-shard TRAIN-only LEAVE-ONE-OUT readout accuracy (avoids the trivial ~1.0
# self-memorization estimate a naive re-predict-on-full-TRAIN readout would give).
# ========================================================================================
def shard_train_loo_accuracy(role, train_items, subbundles, outcome_vecs):
    """LOO-CV accuracy of role `role`'s OWN sub-bundle map on TRAIN itself: for each train item i,
    build role r's sup_map on train-minus-i (VSA_BASE.build_map, reused unmodified), predict item i
    (VSA_BASE.collapse_predict, reused unmodified) via unbind+cleanup-argmax against that role-
    restricted map, and check correctness. TRAIN-only (zero test leakage). n_train<2 -> 0.0
    (undefined LOO, degenerate guard)."""
    n = len(train_items)
    if n < 2:
        return 0.0
    cue_bundles_role = RS.role_cue_bundles_dict(subbundles, role)
    correct = 0
    for i in range(n):
        held = train_items[i]
        rest = train_items[:i] + train_items[i + 1:]
        sup_map = VSA_BASE.build_map(rest, cue_bundles_role, outcome_vecs)
        pred, _sims, _margin = VSA_BASE.collapse_predict(held, sup_map, cue_bundles_role, outcome_vecs)
        correct += int(pred == held["gold_class"])
    return correct / n


def shard_weights_from_loo_acc(shard_accs, roles=None):
    """weight_r = max(0, loo_acc_r - 0.5) -- a shard at/below chance contributes ~0, a shard above
    chance dominates the sum proportionally to its margin over chance. Degenerate guard: if EVERY
    shard's raw weight is <=0 (no shard beat chance on this TRAIN draw), falls back to equal weight
    1.0 across all shards (glass-box: `used_fallback` reported, not silently substituted)."""
    roles = roles or ROLES
    raw_w = {r: max(0.0, shard_accs[r] - 0.5) for r in roles}
    used_fallback = sum(raw_w.values()) <= 0.0
    if used_fallback:
        raw_w = {r: 1.0 for r in roles}
    return raw_w, used_fallback


def _digest(preds_seq):
    return hashlib.sha256(json.dumps(preds_seq).encode()).hexdigest()[:16]


# ========================================================================================
# Shard-level-weighted combine: layers a per-role weight on top of RS's existing per-role
# unbind+similarity (RS.collapse_predict_multi_role sums roles UNWEIGHTED; this weights them first).
# ========================================================================================
def collapse_predict_weighted_multi_role(item, sup_maps_by_role, subbundles, outcome_vecs,
                                          shard_weights, roles=None):
    roles = roles or ROLES
    combined = {lbl: 0.0 for lbl in VSA_BASE.LABELS}
    per_role_sims = {}
    for r in roles:
        q = subbundles[item["id"]][r]
        recovered = binding.unbind(sup_maps_by_role[r], q)
        sims = {lbl: float(atoms.similarity(recovered, outcome_vecs[lbl])) for lbl in VSA_BASE.LABELS}
        per_role_sims[r] = sims
        w = shard_weights.get(r, 0.0)
        for lbl in VSA_BASE.LABELS:
            combined[lbl] += w * sims[lbl]
    best = max(combined, key=combined.get)
    other = [l for l in VSA_BASE.LABELS if l != best][0]
    margin = combined[best] - combined[other]
    return best, combined, margin, per_role_sims


def run_shard_weighted_combine_arm(train_items, test_items, subbundles, outcome_vecs,
                                    shard_w_real, shard_w_scr, train_scr_items, roles=None):
    roles = roles or ROLES
    gold = [it["gold_class"] for it in test_items]

    sup_maps = RS.build_multi_role_maps(train_items, subbundles, outcome_vecs)
    preds, margins = [], []
    for it in test_items:
        pred, _combined, margin, _prs = collapse_predict_weighted_multi_role(
            it, sup_maps, subbundles, outcome_vecs, shard_w_real, roles=roles)
        preds.append(pred)
        margins.append(margin)
    acc = MDL_BASE.accuracy(preds, gold)

    sup_maps_scr = RS.build_multi_role_maps(train_scr_items, subbundles, outcome_vecs)
    preds_scr = [collapse_predict_weighted_multi_role(
        it, sup_maps_scr, subbundles, outcome_vecs, shard_w_scr, roles=roles)[0] for it in test_items]
    acc_scr = MDL_BASE.accuracy(preds_scr, gold)

    dig_real, dig_scr = _digest(preds), _digest(preds_scr)
    return {
        "acc": acc, "acc_scramble": acc_scr, "scramble_delta": acc - acc_scr,
        "digest_real": dig_real, "digest_scramble": dig_scr,
        "arms_differ_real_vs_scramble": dig_real != dig_scr,
        "n_distinct_preds": len(set(preds)), "collapsed_to_constant": len(set(preds)) <= 1,
        "shard_weights": shard_w_real, "shard_weights_scramble": shard_w_scr,
    }


def run_shard_select_arm(train_items, test_items, subbundles, outcome_vecs,
                          shard_accs_real, shard_accs_scr, train_scr_items, roles=None):
    """Hard one-hot limit of shard-weighted: route via ONLY the single best-LOO-accuracy role."""
    roles = roles or ROLES
    gold = [it["gold_class"] for it in test_items]

    best_role = max(roles, key=lambda r: shard_accs_real[r])
    cue_bundles_real = RS.role_cue_bundles_dict(subbundles, best_role)
    sup_map = VSA_BASE.build_map(train_items, cue_bundles_real, outcome_vecs)
    preds = [VSA_BASE.collapse_predict(it, sup_map, cue_bundles_real, outcome_vecs)[0] for it in test_items]
    acc = MDL_BASE.accuracy(preds, gold)

    best_role_scr = max(roles, key=lambda r: shard_accs_scr[r])
    cue_bundles_scr = RS.role_cue_bundles_dict(subbundles, best_role_scr)
    sup_map_scr = VSA_BASE.build_map(train_scr_items, cue_bundles_scr, outcome_vecs)
    preds_scr = [VSA_BASE.collapse_predict(it, sup_map_scr, cue_bundles_scr, outcome_vecs)[0] for it in test_items]
    acc_scr = MDL_BASE.accuracy(preds_scr, gold)

    dig_real, dig_scr = _digest(preds), _digest(preds_scr)
    return {
        "acc": acc, "acc_scramble": acc_scr, "scramble_delta": acc - acc_scr,
        "digest_real": dig_real, "digest_scramble": dig_scr,
        "arms_differ_real_vs_scramble": dig_real != dig_scr,
        "n_distinct_preds": len(set(preds)), "collapsed_to_constant": len(set(preds)) <= 1,
        "selected_role": best_role, "selected_role_scramble": best_role_scr,
    }


def run_both_levels_arm(train_items, test_items, all_items, vocab_vecs, outcome_vecs, roles=None):
    """Optional/exploratory: shard-level weighting (this cell's new mechanism) COMBINED with
    within-shard cue-level discriminativeness weighting (role_sharded_binding_v1's COMPOSED
    construction, DD.compute_cue_weights applied per-shard) -- attention at both levels at once."""
    roles = roles or ROLES
    gold = [it["gold_class"] for it in test_items]

    cue_w = DD.compute_cue_weights(train_items, feat_fn=MDL_BASE.feat_fn)
    subb_composed, _fb = RS.build_role_subbundles(all_items, vocab_vecs, weights=cue_w)
    accs = {r: shard_train_loo_accuracy(r, train_items, subb_composed, outcome_vecs) for r in roles}
    shard_w, used_fb = shard_weights_from_loo_acc(accs, roles=roles)
    sup_maps = RS.build_multi_role_maps(train_items, subb_composed, outcome_vecs)
    preds = []
    for it in test_items:
        pred, _combined, _margin, _prs = collapse_predict_weighted_multi_role(
            it, sup_maps, subb_composed, outcome_vecs, shard_w, roles=roles)
        preds.append(pred)
    acc = MDL_BASE.accuracy(preds, gold)

    train_scr = MDL_BASE.scramble_train_labels(train_items, seed=SCALE.SCRAMBLE_SEED)
    cue_w_scr = DD.compute_cue_weights(train_scr, feat_fn=MDL_BASE.feat_fn)
    subb_composed_scr, _fb_scr = RS.build_role_subbundles(all_items, vocab_vecs, weights=cue_w_scr)
    accs_scr = {r: shard_train_loo_accuracy(r, train_scr, subb_composed_scr, outcome_vecs) for r in roles}
    shard_w_scr, _used_fb_scr = shard_weights_from_loo_acc(accs_scr, roles=roles)
    sup_maps_scr = RS.build_multi_role_maps(train_scr, subb_composed_scr, outcome_vecs)
    preds_scr = [collapse_predict_weighted_multi_role(
        it, sup_maps_scr, subb_composed_scr, outcome_vecs, shard_w_scr, roles=roles)[0] for it in test_items]
    acc_scr = MDL_BASE.accuracy(preds_scr, gold)

    dig_real, dig_scr = _digest(preds), _digest(preds_scr)
    return {
        "acc": acc, "acc_scramble": acc_scr, "scramble_delta": acc - acc_scr,
        "digest_real": dig_real, "digest_scramble": dig_scr,
        "arms_differ_real_vs_scramble": dig_real != dig_scr,
        "n_distinct_preds": len(set(preds)), "collapsed_to_constant": len(set(preds)) <= 1,
        "shard_weights": shard_w, "shard_train_loo_acc": accs,
        "shard_weights_scramble": shard_w_scr, "shard_train_loo_acc_scramble": accs_scr,
        "used_fallback_real": used_fb,
    }


# ========================================================================================
# One (n_train=40, seed) measurement point: the 5 incumbent arms via SCALE.run_one_point()
# (unmodified -- reproduces the scaling cell's own numbers exactly), PLUS the 3 new shard-
# attention arms.
# ========================================================================================
def run_one_point_v2(train_items, test_items, classes, vocab_vecs, outcome_vecs, cue_bundles_flat,
                      subb_role_unweighted, all_items):
    pt = dict(SCALE.run_one_point(train_items, test_items, classes, vocab_vecs, outcome_vecs,
                                   cue_bundles_flat, subb_role_unweighted))

    shard_accs_real = {r: shard_train_loo_accuracy(r, train_items, subb_role_unweighted, outcome_vecs)
                        for r in ROLES}
    shard_w_real, fb_real = shard_weights_from_loo_acc(shard_accs_real)

    train_scr = MDL_BASE.scramble_train_labels(train_items, seed=SCALE.SCRAMBLE_SEED)
    shard_accs_scr = {r: shard_train_loo_accuracy(r, train_scr, subb_role_unweighted, outcome_vecs)
                       for r in ROLES}
    shard_w_scr, fb_scr = shard_weights_from_loo_acc(shard_accs_scr)

    sw = run_shard_weighted_combine_arm(train_items, test_items, subb_role_unweighted, outcome_vecs,
                                         shard_w_real, shard_w_scr, train_scr)
    ss = run_shard_select_arm(train_items, test_items, subb_role_unweighted, outcome_vecs,
                               shard_accs_real, shard_accs_scr, train_scr)
    bl = run_both_levels_arm(train_items, test_items, all_items, vocab_vecs, outcome_vecs)

    pt["role_shard_weighted"] = {
        "acc": sw["acc"], "acc_scramble": sw["acc_scramble"], "n_distinct_preds": sw["n_distinct_preds"],
        "digest_real": sw["digest_real"], "digest_scramble": sw["digest_scramble"],
        "shard_weights": shard_w_real, "shard_weights_scramble": shard_w_scr,
    }
    pt["role_shard_select"] = {
        "acc": ss["acc"], "acc_scramble": ss["acc_scramble"], "n_distinct_preds": ss["n_distinct_preds"],
        "digest_real": ss["digest_real"], "digest_scramble": ss["digest_scramble"],
        "selected_role": ss["selected_role"], "selected_role_scramble": ss["selected_role_scramble"],
    }
    pt["role_shard_weighted_composed_both_levels"] = {
        "acc": bl["acc"], "acc_scramble": bl["acc_scramble"], "n_distinct_preds": bl["n_distinct_preds"],
        "digest_real": bl["digest_real"], "digest_scramble": bl["digest_scramble"],
        "shard_weights": bl["shard_weights"],
    }
    pt["shard_train_loo_acc"] = shard_accs_real
    pt["shard_train_loo_acc_scramble"] = shard_accs_scr
    pt["shard_weight_fallback_used_real"] = fb_real
    pt["shard_weight_fallback_used_scramble"] = fb_scr
    return pt


# ========================================================================================
# Aggregation (mean +/- spread over N_SEEDS seeds). Reuses SCALE._mean / SCALE._stdev
# (called, not copied) over an EXTENDED arm-key list.
# ========================================================================================
ARM_KEYS = ["majority", "mdl", "naive_flat", "attention_flat", "role_sharded",
            "role_shard_weighted", "role_shard_select", "role_shard_weighted_composed_both_levels"]


def aggregate_points(points):
    agg = {}
    for arm in ARM_KEYS:
        accs = [p[arm]["acc"] for p in points]
        entry = {"mean_acc": SCALE._mean(accs), "std_acc": SCALE._stdev(accs), "acc_values": accs}
        if "acc_scramble" in points[0][arm]:
            scrs = [p[arm]["acc_scramble"] for p in points]
            entry["mean_acc_scramble"] = SCALE._mean(scrs)
            entry["acc_scramble_values"] = scrs
        if "n_distinct_preds" in points[0][arm]:
            entry["min_n_distinct_preds"] = min(p[arm]["n_distinct_preds"] for p in points)
        if arm == "mdl":
            entry["frac_episodic"] = sum(1 for p in points if p[arm]["is_episodic"]) / len(points)
        agg[arm] = entry
    return agg


def aggregate_shard_loo(points):
    """Mean per-shard TRAIN LOO accuracy over seeds (glass-box: which shards get up/down-weighted)."""
    return {r: SCALE._mean([p["shard_train_loo_acc"][r] for p in points]) for r in ROLES}


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
    ctrl_ok = mdl_ctrl["passed"] and vsa_ctrl["passed"]

    raw_items = SCALE.load_scaling_items()
    assert len(raw_items) == SCALE.EXPECTED_N_ITEMS, (
        "INSTRUMENTATION_SUSPECT: expected %d scaling items, got %d" % (SCALE.EXPECTED_N_ITEMS, len(raw_items)))
    items = MDL_BASE.build_episodes(raw_items)
    classes = sorted(set(it["gold_class"] for it in items))
    assert classes == ["MET", "UNMET"], "INSTRUMENTATION_SUSPECT: unexpected class set %r" % classes

    pool_items, test_items = SCALE.stratified_test_split(items, seed=SCALE.SPLIT_SEED, test_size=SCALE.TEST_SIZE)
    assert len(test_items) == SCALE.TEST_SIZE
    assert set(it["id"] for it in pool_items).isdisjoint(set(it["id"] for it in test_items))

    vocab_vecs, vocab_terms = VSA_BASE.build_vocab(items)
    outcome_vecs = VSA_BASE.build_outcome_vecs()
    RS.assert_full_role_coverage(vocab_terms)
    cue_bundles_flat = VSA_BASE.build_cue_bundles(items, vocab_vecs)
    subb_role_unweighted, role_fallback_ids = RS.build_role_subbundles(items, vocab_vecs)

    points = []
    for seed_idx in range(N_SEEDS):
        seed = SCALE.SUBSAMPLE_SEED_BASE + N_TRAIN * 1000 + seed_idx
        train_items = SCALE.subsample_train(pool_items, N_TRAIN, seed)
        pt = run_one_point_v2(train_items, test_items, classes, vocab_vecs, outcome_vecs,
                               cue_bundles_flat, subb_role_unweighted, items)
        pt["seed"] = seed
        pt["seed_idx"] = seed_idx
        pt["train_ids"] = sorted(it["id"] for it in train_items)
        points.append(pt)

    agg = aggregate_points(points)
    shard_loo_mean = aggregate_shard_loo(points)
    shard_loo_mean_scramble = {r: SCALE._mean([p["shard_train_loo_acc_scramble"][r] for p in points]) for r in ROLES}

    # ---- the decisive readout ----
    attn_acc = agg["attention_flat"]["mean_acc"]
    new_arm_names = ["role_shard_weighted", "role_shard_select", "role_shard_weighted_composed_both_levels"]
    best_new_name = max(new_arm_names, key=lambda k: agg[k]["mean_acc"])
    best_new_acc = agg[best_new_name]["mean_acc"]
    best_new_non_constant = agg[best_new_name]["min_n_distinct_preds"] > 1
    best_new_scramble_collapses = agg[best_new_name]["mean_acc_scramble"] <= SCALE.SCRAMBLE_BAND + EPS
    beats_attn = best_new_acc > attn_acc + EPS
    ties_attn = (not beats_attn) and (best_new_acc >= attn_acc - TIE_BAND - EPS)

    hard_pass = ctrl_ok and beats_attn and best_new_non_constant and best_new_scramble_collapses
    partial_ties = ctrl_ok and (not hard_pass) and ties_attn
    below = ctrl_ok and (not hard_pass) and (not ties_attn)

    if not ctrl_ok:
        verdict = "HARD_FAIL_MECHANISM"
        msg = ("Positive control failed: mdl_ctrl passed=%s vsa_ctrl passed=%s -- do not trust the "
               "shard-attention numbers below." % (mdl_ctrl["passed"], vsa_ctrl["passed"]))
    elif hard_pass:
        verdict = "HARD_PASS_SHARD_ATTENTION_WINS"
        msg = ("HARD_PASS: best new shard-attention arm (%s, mean_acc=%.4f over %d seeds) BEATS "
               "attention-flat's mean_acc=%.4f (n_train=%d), non-constant (min n_distinct_preds=%d), "
               "scramble collapses (mean_acc_scramble=%.4f <= band=%.2f) -> attention belongs at BOTH "
               "the cue level (arm3) AND the shard level (this cell); wire the shard-weighted/select "
               "combiner into the role-sharded architecture." %
               (best_new_name, best_new_acc, N_SEEDS, attn_acc, N_TRAIN,
                agg[best_new_name]["min_n_distinct_preds"], agg[best_new_name]["mean_acc_scramble"],
                SCALE.SCRAMBLE_BAND))
    elif partial_ties:
        verdict = "PARTIAL_TIES_ATTENTION_FLAT"
        msg = ("PARTIAL/CONVERGE: best new shard-attention arm (%s, mean_acc=%.4f) TIES attention-"
               "flat's mean_acc=%.4f (within TIE_BAND=%.2f, does not clear the strict HARD-PASS bar) "
               "-> attention-flat alone is the simplest sufficient winner (Occam); shard-level "
               "weighting is not decisively additive at n_train=%d. beats_attn=%s, non_constant=%s, "
               "scramble_collapses=%s." %
               (best_new_name, best_new_acc, attn_acc, TIE_BAND, N_TRAIN, beats_attn,
                best_new_non_constant, best_new_scramble_collapses))
    else:
        verdict = "BELOW_ATTENTION_FLAT"
        msg = ("BELOW (diagnosis, NOT a ceiling): best new shard-attention arm (%s, mean_acc=%.4f) is "
               "MORE than TIE_BAND=%.2f below attention-flat's mean_acc=%.4f at n_train=%d. Per-shard "
               "TRAIN LOO accuracies (mean over %d seeds): %s -- diagnose LOO-fold sparsity "
               "(~%d items/shard at n_train=%d/4 roles) or shard-map interference before any ceiling "
               "claim." % (best_new_name, best_new_acc, TIE_BAND, attn_acc, N_TRAIN, N_SEEDS,
                            {r: round(v, 4) for r, v in shard_loo_mean.items()}, N_TRAIN // len(ROLES), N_TRAIN))

    if not best_new_scramble_collapses:
        msg += (" CAVEAT: scramble control did NOT collapse for the best new arm (%s, mean_acc_scramble"
                "=%.4f, band<=%.2f) -- treat its accuracy with added scrutiny." %
                (best_new_name, agg[best_new_name]["mean_acc_scramble"], SCALE.SCRAMBLE_BAND))

    elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "verdict": verdict, "verdict_msg": msg,
        "summary": msg, "elapsed_s": round(elapsed, 4),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "positive_controls": {"mdl_xor_control": mdl_ctrl, "vsa_synthetic_control": vsa_ctrl},
        "config": {
            "n_train": N_TRAIN, "n_seeds": N_SEEDS, "tie_band": TIE_BAND,
            "split_seed": SCALE.SPLIT_SEED, "test_size": SCALE.TEST_SIZE,
            "subsample_seed_base": SCALE.SUBSAMPLE_SEED_BASE, "scramble_seed": SCALE.SCRAMBLE_SEED,
            "scramble_band": SCALE.SCRAMBLE_BAND, "roles": ROLES,
        },
        "data": {
            "n_items_total": len(items), "data_path": SCALE.DATA_PATH,
            "test_ids": sorted(it["id"] for it in test_items),
            "role_fallback_ids_unweighted": role_fallback_ids,
        },
        "results_n_train_40": {arm: agg[arm] for arm in ARM_KEYS},
        "shard_train_loo_acc_mean_over_seeds": shard_loo_mean,
        "shard_train_loo_acc_mean_over_seeds_scramble": shard_loo_mean_scramble,
        "raw_points": points,
        "decisive_readout": {
            "attention_flat_mean_acc": attn_acc,
            "best_new_arm_name": best_new_name, "best_new_arm_mean_acc": best_new_acc,
            "margin_best_new_minus_attention_flat": best_new_acc - attn_acc,
            "beats_attention_flat_strict": beats_attn, "ties_attention_flat": ties_attn,
            "best_new_non_constant": best_new_non_constant,
            "best_new_scramble_collapses": best_new_scramble_collapses,
            "role_sharded_unweighted_reprint_mean_acc": agg["role_sharded"]["mean_acc"],
            "naive_flat_reprint_mean_acc": agg["naive_flat"]["mean_acc"],
            "mdl_reprint_mean_acc": agg["mdl"]["mean_acc"],
            "majority_reprint_mean_acc": agg["majority"]["mean_acc"],
        },
        "gates": {
            "positive_controls_passed": ctrl_ok, "hard_pass": hard_pass,
            "partial_ties": partial_ties, "below": below, "tie_band": TIE_BAND,
        },
        "cell_chunked": False, "final_metrics_atomicity": "tmp_replace",
        "deterministic_seeding": True,
        "cardinality_ok": True, "expected_n_units": N_SEEDS,
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

    # ---- shard_weights_from_loo_acc formula: plain unit test on contrived values ----
    w, fb = shard_weights_from_loo_acc({"A": 0.9, "B": 0.5, "C": 0.3, "D": 0.6}, roles=["A", "B", "C", "D"])
    assert abs(w["A"] - 0.4) < 1e-9 and abs(w["B"] - 0.0) < 1e-9 and abs(w["C"] - 0.0) < 1e-9 \
        and abs(w["D"] - 0.1) < 1e-9, "SELFTEST FAIL: shard_weights_from_loo_acc formula wrong: %r" % w
    assert fb is False, "SELFTEST FAIL: should not use fallback when a shard beats chance"
    # degenerate: every shard at/below chance -> equal-weight fallback
    w2, fb2 = shard_weights_from_loo_acc({"A": 0.5, "B": 0.4, "C": 0.5, "D": 0.2}, roles=["A", "B", "C", "D"])
    assert fb2 is True and all(abs(v - 1.0) < 1e-9 for v in w2.values()), \
        "SELFTEST FAIL: degenerate all-<=chance case should fall back to equal weight: %r" % w2

    raw_items = SCALE.load_scaling_items()
    items = MDL_BASE.build_episodes(raw_items)
    classes = sorted(set(it["gold_class"] for it in items))
    assert classes == ["MET", "UNMET"]

    pool_items, test_items = SCALE.stratified_test_split(items, seed=SCALE.SPLIT_SEED, test_size=SCALE.TEST_SIZE)
    vocab_vecs, vocab_terms = VSA_BASE.build_vocab(items)
    RS.assert_full_role_coverage(vocab_terms)
    outcome_vecs = VSA_BASE.build_outcome_vecs()
    cue_bundles_flat = VSA_BASE.build_cue_bundles(items, vocab_vecs)
    subb_role_unweighted, _fb = RS.build_role_subbundles(items, vocab_vecs)

    train_items = SCALE.subsample_train(pool_items, N_TRAIN, seed=SCALE.SUBSAMPLE_SEED_BASE + N_TRAIN * 1000)
    assert len(train_items) == N_TRAIN

    # ---- shard_train_loo_accuracy: determinism + range + n<2 degenerate guard ----
    a1 = shard_train_loo_accuracy(RS.ROLE_RESPONSE_POLARITY, train_items, subb_role_unweighted, outcome_vecs)
    a2 = shard_train_loo_accuracy(RS.ROLE_RESPONSE_POLARITY, train_items, subb_role_unweighted, outcome_vecs)
    assert a1 == a2, "SELFTEST FAIL: shard_train_loo_accuracy not deterministic"
    assert 0.0 <= a1 <= 1.0
    assert shard_train_loo_accuracy(RS.ROLE_RESPONSE_POLARITY, train_items[:1], subb_role_unweighted, outcome_vecs) == 0.0, \
        "SELFTEST FAIL: n<2 degenerate guard should return 0.0"

    # ---- run_one_point_v2: determinism (whole per-point pipeline, twice -> byte-identical) ----
    p1 = run_one_point_v2(train_items, test_items, classes, vocab_vecs, outcome_vecs, cue_bundles_flat,
                           subb_role_unweighted, items)
    p2 = run_one_point_v2(train_items, test_items, classes, vocab_vecs, outcome_vecs, cue_bundles_flat,
                           subb_role_unweighted, items)
    for arm in ARM_KEYS:
        assert p1[arm]["acc"] == p2[arm]["acc"], "SELFTEST FAIL: %s not deterministic" % arm
        assert 0.0 <= p1[arm]["acc"] <= 1.0

    # ---- incumbent-arm reproduction: SCALE.run_one_point called via run_one_point_v2 must match a
    # direct call to SCALE.run_one_point byte-for-byte (wire-don't-island: this cell must not have
    # silently drifted from the scaling cell's own numbers) ----
    p_direct = SCALE.run_one_point(train_items, test_items, classes, vocab_vecs, outcome_vecs,
                                    cue_bundles_flat, subb_role_unweighted)
    for arm in ("majority", "mdl", "naive_flat", "attention_flat", "role_sharded"):
        assert p1[arm]["acc"] == p_direct[arm]["acc"], (
            "SELFTEST FAIL: incumbent arm %s drifted from SCALE.run_one_point's own value "
            "(%.4f vs %.4f)" % (arm, p1[arm]["acc"], p_direct[arm]["acc"]))

    # ---- glass-box fields present ----
    for arm in ("role_shard_weighted", "role_shard_select", "role_shard_weighted_composed_both_levels"):
        assert "digest_real" in p1[arm] and "digest_scramble" in p1[arm] and "n_distinct_preds" in p1[arm]
    assert set(p1["role_shard_weighted"]["shard_weights"].keys()) == set(ROLES)
    assert p1["role_shard_select"]["selected_role"] in ROLES

    # ---- aggregation sanity ----
    agg = aggregate_points([p1])
    assert agg["role_shard_weighted"]["mean_acc"] == p1["role_shard_weighted"]["acc"]
    assert agg["role_shard_weighted"]["std_acc"] == 0.0, "SELFTEST FAIL: single-point std should be 0"


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
    print(json.dumps({k: v for k, v in metrics.items() if k not in ("raw_points",)}, indent=2, default=str))
    print("---- n_train=40 results (mean/std over %d seeds) ----" % N_SEEDS)
    for arm in ARM_KEYS:
        e = metrics["results_n_train_40"][arm]
        print("%40s  mean=%.4f std=%.4f" % (arm, e["mean_acc"], e["std_acc"]))
    print("---- per-shard TRAIN LOO accuracy (mean over seeds) ----")
    print(json.dumps(metrics["shard_train_loo_acc_mean_over_seeds"], indent=2))
    print("---- decisive readout ----")
    print(json.dumps(metrics["decisive_readout"], indent=2, default=str))


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
