#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_pragmatic_curriculum_dialogue_role_sharded_scaling_v1

THE DECISIVE TEST (overnight synthesis point, task brief): does role-sharding's held-out-accuracy
ADVANTAGE over the flat mechanisms GROW as n_train rises? At n_train=12 on the 27-item clean-modern-
DailyDialog set (exp_pragmatic_curriculum_dialogue_role_sharded_binding_v1.py, commit-landed), the
ranking is role-sharded (role_multi_combine_unweighted) 0.7333 > attention-weighted-flat (arm3)
0.6667 > naive-flat (arm2) 0.5333 -- but all three sit within +2/15 items of the 0.600 majority/MDL
floor, i.e. small-n noise cannot be ruled out from a single n_train point. The capacity physics this
lineage is built on (hdlab/role_slot_summarizer.py M1.7: per-slot alpha=K/(S*N) vs FLAT alpha=K/N --
a factor-S capacity multiplier; FLAT top1 collapses to 0.000 at K=1600 while ROLE holds 0.500,
alpha_wall=0.138 Amit-Gutfreund-Sompolinsky Hopfield critical load) predicts that role-sharding's
margin over the flat mechanisms should WIDEN as load/n rises and the flat bundle's common-mode-
swamping bites harder. This cell measures the ACCURACY-vs-n_train curve for the 3 mechanisms (+MDL/
majority reference arms) on a LARGER (72-item) clean-modern-DailyDialog set to see whether that
margin actually widens with n -- the decisive read this lineage has been building toward.

DATA: experiments/data/dialogue_request_response_dailydialog_scaling_v1.jsonl (72 items, freshly
built this session via an independent auto-label pipeline -- see that file's prep_stats.json sibling
and this cell's own module-level NOISE_ESTIMATE_NOTE constant for the Director-facing honesty report
on residual label noise). SAME schema as the original 30-item dialogue_request_response_dailydialog_
v1.jsonl (id/split/source/corpus/subtype/gold/text/request_text/response_text/notes) so every reused
function below (extract_features/feat_fn, build_vocab/build_map/collapse_predict, compute_cue_weights,
build_role_subbundles/run_role_multi_combine_arm) works UNMODIFIED -- zero re-authoring of mechanism
code, only a new data source and a new n_train-sweep harness around it.

MECHANISMS UNDER TEST (imported, called not copied -- wire-don't-island):
  naive-flat     : experiments.exp_pragmatic_curriculum_vsa_superposition_map_v1.run_vsa_arm
                   (equal-weight flat cue-bundle superposition; VSA_BASE below).
  attention-flat : experiments.exp_pragmatic_curriculum_dialogue_request_response_dailydialog_v1.
                   run_refined_vsa_arm (TRAIN-only discriminativeness-weighted flat cue-bundle; DD
                   below -- this module also supplies compute_cue_weights, SCRAMBLE_SEED, the
                   MDL/VSA positive controls' shared conventions).
  role-sharded   : experiments.exp_pragmatic_curriculum_dialogue_role_sharded_binding_v1.
                   run_role_multi_combine_arm, UNWEIGHTED sub-bundles (RS.build_role_subbundles(...,
                   weights=None)) -- confirmed via this session's own re-read of the landed run's
                   metrics.json that best_arm_name=="role_multi_combine_unweighted" (acc=0.7333) is
                   exactly the 0.7333 the task brief cites, so this is the SAME arm, not a
                   COMPOSED/weighted variant.
  MDL            : experiments...first_test_v1.module_fit/module_predict (RULEIND/GAM/estimation
                   MDL-select, MDL_BASE below).
  majority       : MDL_BASE.majority_class(train) applied uniformly to the fixed TEST set.
All five reuse the EXACT SAME feat_fn/extract_features (MDL_BASE), the EXACT SAME VSA vocab/outcome
atoms (VSA_BASE.build_vocab/build_outcome_vecs, built ONCE over all 72 items so atom identity is
stable across every n_train/seed), and the EXACT SAME accuracy/scramble helpers.

SPLIT DESIGN: a SINGLE fixed, gold-stratified TEST set (TEST_SIZE=24, 12 MET/12 UNMET, split via a
fixed SPLIT_SEED) is held out ONCE and reused for every n_train/seed combination below -- this is
what makes the accuracy-vs-n curve comparable point-to-point (a moving test set would confound the
n_train effect with test-composition noise). The remaining POOL (48 items, 24 MET/24 UNMET) is the
source for n_train in N_TRAIN_SWEEP=[12, 24, 40] (24 and 40 are the practical ceiling this 72-item
set allows while keeping TEST fixed at 24 -- 40 uses 40 of the 48-item pool, gold-stratified 20/20).
For EACH n_train, N_SEEDS=5 independent gold-stratified subsamples of the pool are drawn (fixed seed
formula SUBSAMPLE_SEED_BASE + n_train*1000 + seed_idx) and every arm is refit+re-evaluated on each,
guarding against a single train-subsample's item-flip noise (the task brief's own concern).

PRE-REGISTERED GATE (margins, fixed BEFORE running):
  margin_role_attn(n)  = mean_acc(role-sharded, n) - mean_acc(attention-flat, n)
  margin_attn_naive(n) = mean_acc(attention-flat, n) - mean_acc(naive-flat, n)
  GROWTH_THRESH = 0.05 (5 percentage points; a round, not-tuned-to-outcome margin-change threshold)
  HARD-PASS ("sharding decisively wins"): margin_role_attn(n_max) - margin_role_attn(n_min) >=
    GROWTH_THRESH AND margin_role_attn(n_max) > 0 (role-sharded still strictly ahead at the largest
    n) -- OR naive-flat degrades/stays floored (mean_acc(naive, n_max) <= mean_acc(naive, n_min) +
    EPS) while role-sharded's own accuracy rises by >= GROWTH_THRESH from n_min to n_max.
  PARTIAL: role-sharded's mean accuracy is >= attention-flat's mean accuracy - EPS at EVERY n_train
    (consistently at-or-ahead) but |margin_role_attn(n_max) - margin_role_attn(n_min)| < GROWTH_THRESH
    (a modest, non-widening win) -- "topology helps a fixed amount."
  NULL/CONVERGE: margin_role_attn(n_max) <= margin_role_attn(n_min) - GROWTH_THRESH, i.e. the margin
    SHRINKS toward/through zero as n grows -- a data-scale read (topology's edge fades once flat
    selection has enough data to work with at THESE scales), reported honestly per the anti-
    premature-HARD_FAIL protocol, NOT a ceiling claim (the organ's own collapse threshold is
    calibrated at K~1600, far above this cell's n -- noted explicitly in the verdict message).
  Anything between PARTIAL and NULL/CONVERGE is reported as MIDDLE_BAND with the specific numbers.
SCRAMBLE CONTROLS: every arm-run function already computes a scramble control internally (fixed
DD.SCRAMBLE_SEED, reused unmodified); reported at every n_train, with a specific pass/fail check
against DD.SCRAMBLE_BAND (<=0.60) called out at the LARGEST n_train per the task brief. COVERAGE
(separate from accuracy): MDL's own is_episodic flag (did MDL_select find a compressing hypothesis
at all, vs fall back to the majority default at every point) is reported per (n_train, seed) --
VSA/role arms never abstain (always produce a prediction), so their "coverage" is trivially 100% by
construction; this is noted rather than silently omitted.
POSITIVE CONTROLS (mechanism sanity, run once, must both pass before trusting real-data numbers):
MDL_BASE.run_positive_control() (synthetic XOR) and VSA_BASE.run_positive_control() (synthetic cue-
separated toy set) -- reused verbatim, unmodified.

COMPUTE: 3 n_train levels x 5 seeds = 15 (train, TEST) combinations, 4 model fits each (MDL, naive-
flat, attention-flat, role-sharded) + majority, all closed-form/dense-tensor (N_DIM=1024 FHRR
complex64, max n=40 train + 24 test = 64 items/combination) -- wall time sub-few-seconds total.
LOCAL-ONLY, foreground-to-completion; NO queue, NO push, NO remote-persist, NO hdlab mutation, NO
atom bank (skunkworks VETs). Deterministic: OMP/MKL/OPENBLAS_NUM_THREADS=1, VSA_BASE's own fixed
torch.Generator seeds (VOCAB_SEED/OUTCOME_SEED, reused unmodified so atoms are bit-identical to the
27-item cell's own), fixed-int random.Random seeds for the gold-stratified TEST split, the per-
(n_train,seed) train subsample draw, and every scramble permutation (DD.SCRAMBLE_SEED, reused).
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
from collections import Counter
from datetime import datetime, timezone

import torch

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ANCHOR_NAME = "pragmatic_curriculum_dialogue_role_sharded_scaling_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_pragmatic_curriculum_dialogue_request_response_first_test_v1 as MDL_BASE  # noqa: E402
import experiments.exp_pragmatic_curriculum_vsa_superposition_map_v1 as VSA_BASE  # noqa: E402
import experiments.exp_pragmatic_curriculum_dialogue_request_response_dailydialog_v1 as DD  # noqa: E402
import experiments.exp_pragmatic_curriculum_dialogue_role_sharded_binding_v1 as RS  # noqa: E402

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
DATA_PATH = os.path.join(REPO_ROOT, "experiments", "data",
                          "dialogue_request_response_dailydialog_scaling_v1.jsonl")

# ---- Pre-registered config / gate (see module docstring) ----
EXPECTED_N_ITEMS = 72
TEST_SIZE = 24                      # fixed, gold-stratified 12 MET / 12 UNMET
N_TRAIN_SWEEP = [12, 24, 40]
N_SEEDS = 5
SPLIT_SEED = 20260822101            # fixed TEST-split seed
SUBSAMPLE_SEED_BASE = 20260822200   # per-(n_train,seed_idx) formula: BASE + n_train*1000 + seed_idx
SCRAMBLE_SEED = DD.SCRAMBLE_SEED             # reused, unmodified
SCRAMBLE_BAND = DD.SCRAMBLE_BAND             # 0.60, reused unmodified
GROWTH_THRESH = 0.05                # margin-change threshold, pre-declared not tuned to outcome
EPS = 1e-9

NOISE_ESTIMATE_NOTE = (
    "Director-facing honesty report (see final task response for the full write-up + 6-8 verbatim "
    "samples): this cell's own eyeball QA of ~40/72 items found roughly 6-8 items (~10-15%) with "
    "either (a) a request/response referent mismatch (the response answers a DIFFERENT proposition "
    "than the one immediately requested, e.g. 'let me take your temperature' answered by a refusal "
    "of 'going to see a doctor'), or (b) a false-positive lexical cue match (e.g. \"won't LOSE "
    "shape\" — a positive durability claim — matched the 'won't' refuse-cue substring; \"will you be "
    "here long\" — an informational question — matched the 'will you' request-pattern and its answer "
    "'I won't have a long time' then matched 'won't' as a refusal of a request that was never really "
    "made). Order-of-magnitude comparable to the original 30-item file's ~10% Director-caught noise; "
    "NOT hand-corrected in this pass (auto-label + filter + honest-report, per the task brief -- "
    "hand-dropping specific indices is a follow-up curation step, not done here)."
)


# ========================================================================================
# Data loading (72-item scaling file; SAME schema as the original 30-item file, reuses
# MDL_BASE.build_episodes/extract_features/feat_fn UNMODIFIED)
# ========================================================================================
def load_scaling_items():
    items = []
    with open(DATA_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def stratified_test_split(items, seed, test_size):
    """Gold-stratified TEST split: shuffles MET and UNMET groups independently (sorted by id first
    for determinism) and takes test_size//2 from each into TEST; the remainder is the POOL n_train
    is subsampled from. Deterministic given seed."""
    met = sorted([it for it in items if it["gold_class"] == "MET"], key=lambda x: x["id"])
    unmet = sorted([it for it in items if it["gold_class"] == "UNMET"], key=lambda x: x["id"])
    rng = random.Random(seed)
    rng.shuffle(met)
    rng.shuffle(unmet)
    half = test_size // 2
    test_items = met[:half] + unmet[:half]
    pool_items = met[half:] + unmet[half:]
    return pool_items, test_items


def subsample_train(pool_items, n_train, seed):
    """Gold-stratified subsample WITHOUT replacement from the pool: n_train//2 MET + the remainder
    UNMET (n_train values in N_TRAIN_SWEEP are all even, so this is an exact 50/50 split every
    time). Deterministic given seed; raises if the pool cannot supply enough of either class
    (an INSTRUMENTATION_SUSPECT condition, not silently truncated)."""
    met = sorted([it for it in pool_items if it["gold_class"] == "MET"], key=lambda x: x["id"])
    unmet = sorted([it for it in pool_items if it["gold_class"] == "UNMET"], key=lambda x: x["id"])
    rng = random.Random(seed)
    rng.shuffle(met)
    rng.shuffle(unmet)
    n_met = n_train // 2
    n_unmet = n_train - n_met
    assert len(met) >= n_met and len(unmet) >= n_unmet, (
        "INSTRUMENTATION_SUSPECT: pool too small for n_train=%d (have %d MET / %d UNMET, need %d/%d)"
        % (n_train, len(met), len(unmet), n_met, n_unmet))
    out = met[:n_met] + unmet[:n_unmet]
    rng.shuffle(out)
    return out


# ========================================================================================
# One (n_train, seed) measurement point: all 5 arms, same TEST, same vocab/outcome atoms,
# same cue_bundles / role sub-bundles (built ONCE outside this function and passed in).
# ========================================================================================
def run_one_point(train_items, test_items, classes, vocab_vecs, outcome_vecs,
                   cue_bundles_flat, subb_role_unweighted):
    gold_test = [it["gold_class"] for it in test_items]
    default_train = MDL_BASE.majority_class(train_items)

    # ---- majority ----
    maj_preds = [default_train] * len(test_items)
    maj_acc = MDL_BASE.accuracy(maj_preds, gold_test)

    # ---- MDL ----
    mdl_name, mdl_chosen, _mdl_all = MDL_BASE.module_fit(train_items, classes)
    mdl_is_episodic = mdl_chosen is None
    mdl_preds = (MDL_BASE.module_predict(mdl_name, mdl_chosen, test_items, default_train)
                 if mdl_chosen is not None else [default_train] * len(test_items))
    mdl_acc = MDL_BASE.accuracy(mdl_preds, gold_test)

    # ---- naive-flat (arm2, reused unmodified) ----
    arm2 = VSA_BASE.run_vsa_arm(train_items, test_items, cue_bundles_flat, outcome_vecs,
                                 scramble_seed=SCRAMBLE_SEED)

    # ---- attention-flat (arm3, reused unmodified -- recomputes its own TRAIN-only weights) ----
    arm3 = DD.run_refined_vsa_arm(train_items, test_items, vocab_vecs, outcome_vecs,
                                   feat_fn=MDL_BASE.feat_fn, scramble_seed=SCRAMBLE_SEED)

    # ---- role-sharded (role_multi_combine, UNWEIGHTED -- the 0.7333 arm) ----
    role = RS.run_role_multi_combine_arm(train_items, test_items, subb_role_unweighted,
                                          subb_role_unweighted, outcome_vecs)

    return {
        "n_train": len(train_items),
        "majority": {"acc": maj_acc},
        "mdl": {"acc": mdl_acc, "chosen_plugin": mdl_name, "is_episodic": mdl_is_episodic},
        "naive_flat": {"acc": arm2["acc"], "acc_scramble": arm2["acc_scramble"],
                        "n_distinct_preds": len(set(p["vsa_pred"] for p in arm2["per_item"]))},
        "attention_flat": {"acc": arm3["acc"], "acc_scramble": arm3["acc_scramble"],
                            "n_distinct_preds": arm3["n_distinct_preds"]},
        "role_sharded": {"acc": role["acc"], "acc_scramble": role["acc_scramble"],
                          "n_distinct_preds": role["n_distinct_preds"]},
    }


# ========================================================================================
# Aggregation helpers (mean +/- spread over N_SEEDS seeds, per n_train, per arm)
# ========================================================================================
ARM_KEYS = ["majority", "mdl", "naive_flat", "attention_flat", "role_sharded"]


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def _stdev(xs):
    xs = [x for x in xs if x is not None]
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return (sum((x - m) ** 2 for x in xs) / len(xs)) ** 0.5


def aggregate_points(points_by_ntrain):
    """points_by_ntrain: {n_train: [per-seed run_one_point() dict, ...]} -> {n_train: {arm: {mean,
    std, values, mean_scramble (where applicable)}}}"""
    agg = {}
    for n_train, points in points_by_ntrain.items():
        agg[n_train] = {}
        for arm in ARM_KEYS:
            accs = [p[arm]["acc"] for p in points]
            entry = {"mean_acc": _mean(accs), "std_acc": _stdev(accs), "acc_values": accs}
            if "acc_scramble" in points[0][arm]:
                scrs = [p[arm]["acc_scramble"] for p in points]
                entry["mean_acc_scramble"] = _mean(scrs)
                entry["acc_scramble_values"] = scrs
            if arm == "mdl":
                entry["frac_episodic"] = sum(1 for p in points if p[arm]["is_episodic"]) / len(points)
            agg[n_train][arm] = entry
    return agg


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

    raw_items = load_scaling_items()
    assert len(raw_items) == EXPECTED_N_ITEMS, (
        "INSTRUMENTATION_SUSPECT: expected %d scaling items, got %d" % (EXPECTED_N_ITEMS, len(raw_items)))
    items = MDL_BASE.build_episodes(raw_items)
    classes = sorted(set(it["gold_class"] for it in items))
    assert classes == ["MET", "UNMET"], "INSTRUMENTATION_SUSPECT: unexpected class set %r" % classes

    pool_items, test_items = stratified_test_split(items, seed=SPLIT_SEED, test_size=TEST_SIZE)
    assert len(test_items) == TEST_SIZE
    assert len(pool_items) == len(items) - TEST_SIZE
    assert set(it["id"] for it in pool_items).isdisjoint(set(it["id"] for it in test_items))
    test_gold_counts = dict(Counter(it["gold_class"] for it in test_items))
    pool_gold_counts = dict(Counter(it["gold_class"] for it in pool_items))
    test_subtype_counts = dict(Counter(it["subtype"] for it in test_items))
    pool_subtype_counts = dict(Counter(it["subtype"] for it in pool_items))

    # ---- vocab/outcome atoms + flat/role cue structures built ONCE over ALL 72 items (split- and
    # n_train-agnostic symbol atoms; stable identity across every measurement point below) ----
    vocab_vecs, vocab_terms = VSA_BASE.build_vocab(items)
    outcome_vecs = VSA_BASE.build_outcome_vecs()
    RS.assert_full_role_coverage(vocab_terms)
    cue_bundles_flat = VSA_BASE.build_cue_bundles(items, vocab_vecs)
    subb_role_unweighted, role_fallback_ids = RS.build_role_subbundles(items, vocab_vecs)  # weights=None

    n_features_seen = len(set(f for it in items for f in MDL_BASE.feat_fn(it)))
    assert n_features_seen > 5, "INSTRUMENTATION_SUSPECT: degenerate feature space"

    # ---- sweep n_train x seeds ----
    points_by_ntrain = {}
    train_ids_by_point = {}
    for n_train in N_TRAIN_SWEEP:
        points = []
        ids_this_n = []
        for seed_idx in range(N_SEEDS):
            seed = SUBSAMPLE_SEED_BASE + n_train * 1000 + seed_idx
            train_items = subsample_train(pool_items, n_train, seed)
            ids_this_n.append({"seed": seed, "seed_idx": seed_idx,
                                "train_ids": sorted(it["id"] for it in train_items)})
            pt = run_one_point(train_items, test_items, classes, vocab_vecs, outcome_vecs,
                                cue_bundles_flat, subb_role_unweighted)
            pt["seed"] = seed
            pt["seed_idx"] = seed_idx
            points.append(pt)
        points_by_ntrain[n_train] = points
        train_ids_by_point[n_train] = ids_this_n

    agg = aggregate_points(points_by_ntrain)

    # ---- scramble controls at the LARGEST n_train (task-brief-flagged; also reported at every
    # n_train above via agg[n]['<arm>']['mean_acc_scramble']) ----
    n_max, n_min = max(N_TRAIN_SWEEP), min(N_TRAIN_SWEEP)
    scramble_at_max = {
        "naive_flat": agg[n_max]["naive_flat"]["mean_acc_scramble"],
        "attention_flat": agg[n_max]["attention_flat"]["mean_acc_scramble"],
        "role_sharded": agg[n_max]["role_sharded"]["mean_acc_scramble"],
    }
    scramble_collapses_at_max = {k: (v is not None and v <= SCRAMBLE_BAND + EPS) for k, v in scramble_at_max.items()}

    # ---- the decisive readout: margins as functions of n_train ----
    margin_role_attn = {n: agg[n]["role_sharded"]["mean_acc"] - agg[n]["attention_flat"]["mean_acc"]
                         for n in N_TRAIN_SWEEP}
    margin_attn_naive = {n: agg[n]["attention_flat"]["mean_acc"] - agg[n]["naive_flat"]["mean_acc"]
                          for n in N_TRAIN_SWEEP}
    role_attn_trend = margin_role_attn[n_max] - margin_role_attn[n_min]
    naive_floored_or_degrades = agg[n_max]["naive_flat"]["mean_acc"] <= agg[n_min]["naive_flat"]["mean_acc"] + EPS
    role_acc_rises = agg[n_max]["role_sharded"]["mean_acc"] - agg[n_min]["role_sharded"]["mean_acc"] >= GROWTH_THRESH
    role_ahead_at_every_n = all(agg[n]["role_sharded"]["mean_acc"] >= agg[n]["attention_flat"]["mean_acc"] - EPS
                                 for n in N_TRAIN_SWEEP)

    grows = (role_attn_trend >= GROWTH_THRESH and margin_role_attn[n_max] > EPS) or \
            (naive_floored_or_degrades and role_acc_rises)
    partial = (not grows) and role_ahead_at_every_n and abs(role_attn_trend) < GROWTH_THRESH
    converges = role_attn_trend <= -GROWTH_THRESH

    # ---- gate verdict ----
    if not ctrl_ok:
        verdict = "HARD_FAIL_MECHANISM"
        msg = ("Positive control failed: mdl_ctrl passed=%s vsa_ctrl passed=%s -- do not trust the "
               "scaling curve below." % (mdl_ctrl["passed"], vsa_ctrl["passed"]))
    elif grows:
        verdict = "HARD_PASS_MARGIN_GROWS"
        msg = ("HARD_PASS: role-sharded's margin over attention-flat GROWS with n_train (margin(n=%d)"
               "=%.4f -> margin(n=%d)=%.4f, trend=%.4f >= thresh=%.2f) %s -- confirms the capacity-"
               "physics prediction that sharding's advantage widens as load/n rises." %
               (n_min, margin_role_attn[n_min], n_max, margin_role_attn[n_max], role_attn_trend,
                GROWTH_THRESH, "AND naive-flat stayed floored/degraded while role-sharded rose"
                if naive_floored_or_degrades and role_acc_rises else ""))
    elif partial:
        verdict = "PARTIAL_CONSISTENT_MODEST_WIN"
        msg = ("PARTIAL: role-sharded stays at-or-ahead of attention-flat at EVERY n_train tested "
               "(margins: %s) but the margin is roughly FLAT (trend=%.4f, |trend| < thresh=%.2f) -- "
               "topology gives a consistent-but-modest win, not a widening one at these scales." %
               ({n: round(margin_role_attn[n], 4) for n in N_TRAIN_SWEEP}, role_attn_trend, GROWTH_THRESH))
    elif converges:
        verdict = "NULL_MARGIN_CONVERGES"
        msg = ("NULL/CONVERGE (data-scale read, NOT a ceiling): role-sharded's margin over attention-"
               "flat SHRINKS as n_train rises (margin(n=%d)=%.4f -> margin(n=%d)=%.4f, trend=%.4f <= "
               "-thresh=%.2f) -- at THESE scales (n up to %d), flat selection catches up once given "
               "enough data; the role-sharded organ's own measured collapse threshold "
               "(hdlab/role_slot_summarizer.py) is calibrated at K~1600, far above this cell's n, so "
               "this is a diagnosis that OUR n range sits below where sharding's structural edge is "
               "expected to bite, not evidence the mechanism itself is wrong." %
               (n_min, margin_role_attn[n_min], n_max, margin_role_attn[n_max], role_attn_trend,
                GROWTH_THRESH, n_max))
    else:
        verdict = "MIDDLE_BAND"
        msg = ("MIDDLE_BAND: margins neither clearly grow (trend=%.4f < thresh=%.2f) nor clearly "
               "converge (trend > -thresh) nor hold a clean PARTIAL (role_ahead_at_every_n=%s) -- see "
               "per-n_train margin table for the exact shape." %
               (role_attn_trend, GROWTH_THRESH, role_ahead_at_every_n))

    if not scramble_collapses_at_max["role_sharded"] or not scramble_collapses_at_max["attention_flat"]:
        msg += (" CAVEAT: scramble control did NOT collapse at n_train=%d for %s (band<=%.2f) -- "
                "treat the accuracy numbers at that n with added scrutiny." %
                (n_max, [k for k, v in scramble_collapses_at_max.items() if not v], SCRAMBLE_BAND))

    elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "verdict": verdict, "verdict_msg": msg,
        "summary": msg, "elapsed_s": round(elapsed, 4),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "positive_controls": {"mdl_xor_control": mdl_ctrl, "vsa_synthetic_control": vsa_ctrl},
        "noise_estimate_note": NOISE_ESTIMATE_NOTE,
        "data": {
            "n_items_total": len(items), "data_path": DATA_PATH,
            "test_size": TEST_SIZE, "test_gold_counts": test_gold_counts,
            "test_subtype_counts": test_subtype_counts,
            "pool_size": len(pool_items), "pool_gold_counts": pool_gold_counts,
            "pool_subtype_counts": pool_subtype_counts,
            "test_ids": sorted(it["id"] for it in test_items),
            "n_features_seen": n_features_seen,
            "role_fallback_ids_unweighted": role_fallback_ids,
        },
        "config": {
            "n_train_sweep": N_TRAIN_SWEEP, "n_seeds": N_SEEDS, "split_seed": SPLIT_SEED,
            "subsample_seed_base": SUBSAMPLE_SEED_BASE, "scramble_seed": SCRAMBLE_SEED,
            "scramble_band": SCRAMBLE_BAND, "growth_thresh": GROWTH_THRESH,
        },
        "curve": {str(n): agg[n] for n in N_TRAIN_SWEEP},
        "raw_points": {str(n): points_by_ntrain[n] for n in N_TRAIN_SWEEP},
        "train_ids_by_point": {str(n): train_ids_by_point[n] for n in N_TRAIN_SWEEP},
        "margins": {
            "margin_role_attn_by_n": {str(n): margin_role_attn[n] for n in N_TRAIN_SWEEP},
            "margin_attn_naive_by_n": {str(n): margin_attn_naive[n] for n in N_TRAIN_SWEEP},
            "role_attn_trend_nmin_to_nmax": role_attn_trend,
            "naive_floored_or_degrades": naive_floored_or_degrades,
            "role_acc_rises_by_at_least_thresh": role_acc_rises,
            "role_ahead_at_every_n": role_ahead_at_every_n,
        },
        "scramble_at_max_ntrain": {
            "n_train": n_max, "accs": scramble_at_max, "collapses": scramble_collapses_at_max,
        },
        "gates": {
            "positive_controls_passed": ctrl_ok, "grows": grows, "partial": partial,
            "converges": converges, "growth_thresh": GROWTH_THRESH,
        },
        "cell_chunked": False, "final_metrics_atomicity": "tmp_replace",
        "deterministic_seeding": True,
        "cardinality_ok": True, "expected_n_units": len(N_TRAIN_SWEEP) * N_SEEDS,
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

    raw_items = load_scaling_items()
    assert len(raw_items) == EXPECTED_N_ITEMS, "SELFTEST FAIL: expected %d items, got %d" % (
        EXPECTED_N_ITEMS, len(raw_items))
    ids = [it["id"] for it in raw_items]
    assert len(ids) == len(set(ids)), "SELFTEST FAIL: duplicate ids in scaling data file"
    for it in raw_items:
        assert it["gold"] in ("MET", "UNMET"), "SELFTEST FAIL: bad gold on %s" % it["id"]
        assert it.get("request_text") and it.get("response_text"), "SELFTEST FAIL: missing text fields on %s" % it["id"]

    items = MDL_BASE.build_episodes(raw_items)
    met_n = sum(1 for it in items if it["gold_class"] == "MET")
    unmet_n = sum(1 for it in items if it["gold_class"] == "UNMET")
    assert met_n == 36 and unmet_n == 36, "SELFTEST FAIL: expected 36/36 MET/UNMET, got %d/%d" % (met_n, unmet_n)

    # split determinism + disjointness + size
    pool1, test1 = stratified_test_split(items, seed=SPLIT_SEED, test_size=TEST_SIZE)
    pool2, test2 = stratified_test_split(items, seed=SPLIT_SEED, test_size=TEST_SIZE)
    assert [it["id"] for it in test1] == [it["id"] for it in test2], "SELFTEST FAIL: test split not deterministic"
    assert len(test1) == TEST_SIZE and len(pool1) == EXPECTED_N_ITEMS - TEST_SIZE
    assert set(it["id"] for it in pool1).isdisjoint(set(it["id"] for it in test1))
    assert Counter(it["gold_class"] for it in test1) == Counter({"MET": TEST_SIZE // 2, "UNMET": TEST_SIZE // 2})

    # subsample determinism + disjointness-from-nothing (just a subset of pool) + size + balance
    for n_train in N_TRAIN_SWEEP:
        tr1 = subsample_train(pool1, n_train, seed=SUBSAMPLE_SEED_BASE + n_train * 1000)
        tr2 = subsample_train(pool1, n_train, seed=SUBSAMPLE_SEED_BASE + n_train * 1000)
        assert sorted(it["id"] for it in tr1) == sorted(it["id"] for it in tr2), \
            "SELFTEST FAIL: subsample_train not deterministic at n_train=%d" % n_train
        assert len(tr1) == n_train
        assert set(it["id"] for it in tr1) <= set(it["id"] for it in pool1)
        assert Counter(it["gold_class"] for it in tr1) == Counter({"MET": n_train // 2, "UNMET": n_train // 2})

    # feat_fn determinism (imported, not reimplemented)
    a = MDL_BASE.feat_fn(items[0])
    b = MDL_BASE.feat_fn(items[0])
    assert a == b, "SELFTEST FAIL: feat_fn not deterministic"

    # vocab/role coverage + determinism
    vocab_vecs, vocab_terms = VSA_BASE.build_vocab(items)
    RS.assert_full_role_coverage(vocab_terms)  # must not raise
    outcome_vecs = VSA_BASE.build_outcome_vecs()
    cue_bundles_flat = VSA_BASE.build_cue_bundles(items, vocab_vecs)
    subb_role, _fb = RS.build_role_subbundles(items, vocab_vecs)

    # one measurement point, run twice -> byte-identical predictions (determinism of the whole
    # per-point pipeline, not just its individual pieces)
    classes = ["MET", "UNMET"]
    tr = subsample_train(pool1, 12, seed=SUBSAMPLE_SEED_BASE + 12 * 1000)
    p1 = run_one_point(tr, test1, classes, vocab_vecs, outcome_vecs, cue_bundles_flat, subb_role)
    p2 = run_one_point(tr, test1, classes, vocab_vecs, outcome_vecs, cue_bundles_flat, subb_role)
    assert p1["naive_flat"]["acc"] == p2["naive_flat"]["acc"], "SELFTEST FAIL: naive_flat not deterministic"
    assert p1["attention_flat"]["acc"] == p2["attention_flat"]["acc"], "SELFTEST FAIL: attention_flat not deterministic"
    assert p1["role_sharded"]["acc"] == p2["role_sharded"]["acc"], "SELFTEST FAIL: role_sharded not deterministic"
    assert p1["mdl"]["acc"] == p2["mdl"]["acc"], "SELFTEST FAIL: mdl not deterministic"
    for arm in ARM_KEYS:
        assert 0.0 <= p1[arm]["acc"] <= 1.0

    # aggregation sanity: mean of a single point equals that point's own value
    agg = aggregate_points({12: [p1]})
    assert agg[12]["role_sharded"]["mean_acc"] == p1["role_sharded"]["acc"], "SELFTEST FAIL: aggregation mean wrong"
    assert agg[12]["role_sharded"]["std_acc"] == 0.0, "SELFTEST FAIL: single-point std should be 0"


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
    print("---- scaling curve (mean/std over %d seeds per n_train) ----" % N_SEEDS)
    for n in N_TRAIN_SWEEP:
        row = {arm: round(metrics["curve"][str(n)][arm]["mean_acc"], 4) for arm in ARM_KEYS}
        print("n_train=%3d  %r" % (n, row))
    print("---- margins ----")
    print(json.dumps(metrics["margins"], indent=2, default=str))


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
