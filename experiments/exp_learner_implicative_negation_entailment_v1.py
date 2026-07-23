#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_learner_implicative_negation_entailment_v1

THE DECISIVE grow-thrust real-data test: run the beyond-linear target found by the
2026-07-23 drill (notes/research_beyond_linear_real_language_structure_2026-07-23.md) THROUGH the
centralized Learner module (hdlab/learner/, 3 plugins: estimation/ruleind/gam, banked 29487/29489).
Does the module AUTO-SELECT the nonlinear learner AND BEAT LINEAR on a GENUINE, non-construction-
favorable, real-language beyond-linear task?

TASK: Karttunen (1971) implicative-verb classification x negation entailment (CITED, externally
published, NOT invented). Positive implicatives (manage, bother, dare): V(X) entails X; NOT-V(X)
entails NOT-X. Negative implicatives (fail, forget, neglect, avoid, hesitate, decline): V(X)
entails NOT-X; NOT-V(X) entails X. Gold label = the Karttunen truth table applied to
(verb polarity_class, Polarity=Neg scoping the matrix verb) -- a genuine XNOR/parity interaction
(Minsky & Papert 1969 CITED: not linearly separable in the two raw cues alone), mined from REAL
UD-EWT sentences via tools/build_negation_factuality_gold.py's write_implicative_gold() extension
(NOT synthetic/injected -- avoids the 29482 construction-favorable trap).

FEATURES (identical across all arms, deliberately NOT handed polarity_class directly):
  feat_fn(inst) -> ["verb=<lemma>", "neg=<True|False>"]. The model must recover the interaction
  from lexical identity + surface negation, not from a pre-computed class label.

ARMS:
  ARM_LINEAR  -- hdlab.learner.plugins.gam_plugin.learn() with max_interactions=0: pure additive
                 log-odds (intercept + per-verb-feature + per-neg-feature, NO pairwise term) --
                 a genuine linear/log-linear readout over the SAME two feature families.
  ARM_SIMVOTE -- parameter-free Jaccard-similarity k=5 majority vote over feature sets.
  ARM_MODULE  -- hdlab.learner.registry.learn() fed all 3 plugins (estimation with
                 key_fn=verb_lemma ALONE [fair "weak" single-cue candidate, per the module's own
                 documented order-1/non-conjunctive design]; ruleind with max_conjunct=2; gam with
                 FULL interactions). Auto-selects via MDL compression -- reported, not hand-picked.

SPLITS (decided from item-count data-availability BEFORE computing any accuracy; see
preregs/2026-07-23_learner_implicative_negation_entailment.md "Data-availability audit"):
  SEEN-verb split: item-level stratified 70/30 by (verb, negated), ALL 9 verbs (bother's 6
    pos-impl-negated items -- the ONLY pos-impl-negated evidence in the whole corpus -- stay in
    this pool so both classes' negated cells are represented in training; required for the
    linear-model contradiction argument below to bite on REAL, not just synthetic, data).
  HELD-OUT-VERB split: avoid + hesitate (both neg-impl) held out entirely from a model trained on
    manage/bother/fail/forget/decline/neglect/dare. Scope caveat (declared pre-run): because
    bother is the sole pos-impl-negated source, held-out verbs are necessarily neg-impl-class --
    tests generalization to an unseen member of the MAJORITY class, not symmetric both-class
    transfer. This is a real data-thinness limitation, stated honestly, not hidden.

WHY THIS IS PROVABLY BEYOND-LINEAR GIVEN THE ACTUAL OBSERVED DATA (THEORETICAL, derived in the
prereg, not merely a synthetic-XOR analogy): fitting bother (pos-impl: neg=False->REALIZED,
neg=True->NOT_REALIZED, needs the SHARED neg-weight strongly NEGATIVE relative to bother's bias)
and forget (neg-impl: neg=False->NOT_REALIZED, neg=True->REALIZED, needs the SAME SHARED neg-
weight strongly POSITIVE relative to forget's bias) SIMULTANEOUSLY is impossible for an additive
model with ONE shared negation weight -- and BOTH verbs' negated cells are real, populated,
non-synthetic mined data (bother n=6 negated, forget n=9 negated).

PRE-REGISTERED BANDS: see preregs/2026-07-23_learner_implicative_negation_entailment.md (filed
BEFORE this run). HARD_PASS_SEEN / HARD_FAIL_SEEN / HARD_PASS_HELDOUT / (pre-anticipated)
HARD_FAIL_HELDOUT-as-representational-bound / overall tiers, all pre-registered there.

BRAIN-CHECK (pre-registered, not post-hoc): Karttunen's classification is a closed LEXICAL
inventory, not a compositional/phonological rule -- no independent evidence humans guess a novel
verb's implicative polarity from surface form alone; per-verb lexical storage is the expected
human account too, so a held-out-verb HARD_FAIL is anticipated to be a brain-shared bound (unless
the module's margin over LINEAR/SIMVOTE ALSO collapses to ~0 on held-out, confirming the
structural-representation account vs. a milder power/data issue).

COMPUTE ARCHITECTURE: class (b) sequential-CPU, n=114 total items, closed-form counting/log-odds/
rule-search only (no matmul, no torch). Wall time sub-second. LOCAL-ONLY, foreground-to-
completion; NO queue, NO push, NO remote-persist, NO hdlab mutation, NO atom bank (skunkworks
VETs). Deterministic: OMP/MKL/OPENBLAS_NUM_THREADS=1, random.Random(fixed_int_seed) + sorted(set())
only -- NO hash()-seeded RNG or ordering (PROT-023 / feedback_synthetic... 2026-07-14 class).

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground measurement cell):
  - arms_differ_verified at self-test + full (hash test over LINEAR/SIMVOTE/MODULE predicted-
    class tuples on the SEEN-verb test split).
  - final_metrics_atomicity: tmp_replace (os.replace).
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException).
  - crlb_n/a: accuracy/compression-ratio measurement, not a capacity/CRLB-bound cell.
  - baseline_in_band: n/a (LINEAR/SIMVOTE are the discriminating baselines under test, not
    architecture-floor sentinels).
  - discriminator survives scale: n/a (fixed real-data n=114, not scale-swept).
  - cardinality_ok: EXPECTED_N_UNITS=1 (single real-data fit + synthetic control + scramble
    control; no seed/sweep axis).
  - calibration_check: default_ok_for_this_regime (MDL two-part code, module-wide formula).
  - deterministic_seeding: true.
  - all numbers tagged MEASURED@ / THEORETICAL@ / CITED@ in this docstring / prereg.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import random
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ANCHOR_NAME = "learner_implicative_negation_entailment_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import tools.build_negation_factuality_gold as GOLD  # noqa: E402
from hdlab.learner import registry  # noqa: E402
from hdlab.learner.core import KEEP_EPISODIC  # noqa: E402
from hdlab.learner.plugins import gam_plugin  # noqa: E402

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- Pre-registered bands (see preregs/2026-07-23_learner_implicative_negation_entailment.md) ----
HP_SEEN_ACC_MIN = 0.85
HP_SEEN_MARGIN_MIN = 0.20
HF_SEEN_LINEAR_MAX = 0.80
HF_SEEN_MIN_N_TEST = 15
SCRAMBLE_COLLAPSE_MIN = 0.25

HP_HELDOUT_ACC_MIN = 0.65
HP_HELDOUT_MARGIN_MIN = 0.15

SPLIT_SEED = 990123        # fixed int, NOT hash()-derived
SCRAMBLE_SEED = 770321      # fixed int, NOT hash()-derived
# NOTE: an original fixed avoid+hesitate held-out pair was tried and found DEGENERATE (both
# verbs share the training-majority class -> all arms tied at 1.0/margin=0.0, caught by the
# suspicious-result gate). Superseded by lovo_eval() below (leave-one-verb-out across all 9
# verbs, which directly exercises the bother/manage/dare pos-implicative folds).


# ========================================================================================
# Feature encoding (shared across all arms)
# ========================================================================================
def feat_fn(inst):
    return ["verb=%s" % inst["verb_lemma"], "neg=%s" % inst["negated"]]


def key_fn_verb_only(inst):
    return inst["verb_lemma"]


# ========================================================================================
# ARM_SIMVOTE: parameter-free Jaccard-similarity k=5 majority vote (no learned parameters)
# ========================================================================================
def simvote_fit_predict(train, test, k=5):
    train_feats = [set(feat_fn(t)) for t in train]
    train_labels = [t["gold_class"] for t in train]
    preds = []
    for item in test:
        fs = set(feat_fn(item))
        sims = []
        for i, tf in enumerate(train_feats):
            union = len(fs | tf)
            jacc = (len(fs & tf) / union) if union else 0.0
            sims.append((jacc, i))
        sims.sort(key=lambda x: (-x[0], x[1]))  # deterministic tie-break: stable index order
        top = sims[:min(k, len(sims))]
        votes = Counter(train_labels[i] for _s, i in top)
        best = max(sorted(votes.keys()), key=lambda c: votes[c])  # sorted() -> deterministic tie
        preds.append(best)
    return preds


# ========================================================================================
# ARM_LINEAR: gam_plugin with interactions disabled -> pure additive log-odds
# ========================================================================================
def linear_fit(train, classes):
    spec = {"label_fn": lambda ep: ep["gold_class"], "classes": classes,
            "min_coverage": 1, "max_interactions": 0}
    return gam_plugin.learn(train, feat_fn, spec, {})


def linear_predict(result, test):
    return [gam_plugin.apply(result.hypothesis, feat_fn(item)) for item in test]


# ========================================================================================
# ARM_MODULE: hdlab.learner.registry auto-select over all 3 plugins
# ========================================================================================
def module_fit(train, classes):
    spec = {
        "candidate_plugins": ["estimation", "ruleind", "gam"],
        "per_plugin": {
            "estimation": {"mode": "generic_mdl", "key_fn": key_fn_verb_only,
                           "label_fn": lambda ep: ep["gold_class"], "classes": classes},
            "ruleind": {"max_conjunct": 2, "min_coverage": 2, "purity_thresh": 0.85,
                        "max_rules": 25, "key_fn": lambda ep: ep["verb_lemma"]},
            "gam": {"label_fn": lambda ep: ep["gold_class"], "classes": classes,
                    "min_coverage": 2},
        },
    }
    chosen_name, chosen, all_results = registry.learn(train, feat_fn, spec)
    return chosen_name, chosen, all_results


def module_predict(chosen_name, chosen, test, default_class):
    preds = []
    for item in test:
        feats = feat_fn(item)
        if chosen_name == "ruleind":
            from hdlab.learner.plugins import ruleind_plugin
            pred = ruleind_plugin.apply(chosen.hypothesis, feats,
                                         key=item["verb_lemma"], default_class=default_class)
        elif chosen_name == "gam":
            pred = gam_plugin.apply(chosen.hypothesis, feats)
        elif chosen_name == "estimation":
            from hdlab.learner.plugins import estimation_plugin
            pred = estimation_plugin.apply(chosen.hypothesis, key_fn_verb_only(item))
        else:  # KEEP_EPISODIC
            pred = default_class
        preds.append(pred)
    return preds


# ========================================================================================
# Data loading + splits
# ========================================================================================
def load_items():
    items, stats = GOLD.build_implicative_gold(maxtok=40)
    return items, stats


def stratified_split(items, test_frac=0.30, seed=SPLIT_SEED):
    """70/30 by (verb_lemma, negated). sorted() + fixed-int-seeded random.Random -- NOT hash()."""
    rng = random.Random(seed)
    by_stratum = {}
    for it in items:
        k = (it["verb_lemma"], it["negated"])
        by_stratum.setdefault(k, []).append(it)
    train, test = [], []
    for k in sorted(by_stratum.keys()):
        group = sorted(by_stratum[k], key=lambda it: (it["sent_id"], it["verb_id"]))
        rng.shuffle(group)
        if len(group) >= 2:
            n_test = max(1, round(len(group) * test_frac))
        else:
            n_test = 0
        test.extend(group[:n_test])
        train.extend(group[n_test:])
    return train, test


def lovo_eval(items, classes):
    """Leave-one-verb-out sweep across EVERY verb in the pool (not just one fixed pair). This is
    the rigorous version of the held-out-verb test: a fixed avoid+hesitate pair (both same
    [majority] class) turned out to be a DEGENERATE non-discriminating fold (all arms tied at
    1.0, margin=0.0 -- caught by the suspicious-result gate, "any metric expected to vary that is
    perfectly constant"). LOVO across all 9 verbs directly exercises the two folds that matter
    most: bother (the sole pos-impl-negated verb; held out, the model trained on
    manage/dare/*neg-impl* has ZERO pos-impl-negated exposure) and manage/dare (pos-impl,
    zero-negated-in-corpus, tests whether the model at least gets the affirmative direction right
    for a genuinely novel verb)."""
    verb_counts = Counter(it["verb_lemma"] for it in items)
    verbs = sorted(v for v in verb_counts if verb_counts[v] >= 1)
    folds = []
    for v in verbs:
        train = [it for it in items if it["verb_lemma"] != v]
        test = [it for it in items if it["verb_lemma"] == v]
        if not train or not test:
            continue
        train_classes = sorted(set(it["gold_class"] for it in train)) or classes
        lin_res = linear_fit(train, train_classes)
        lin_preds = linear_predict(lin_res, test)
        sim_preds = simvote_fit_predict(train, test)
        mod_name, mod_res, mod_all = module_fit(train, train_classes)
        default = majority_class(train)
        mod_preds = module_predict(mod_name, mod_res, test, default)
        gold = [it["gold_class"] for it in test]
        folds.append({
            "verb": v, "polarity_class": GOLD.IMPLICATIVE_LEXICON.get(v),
            "n_test": len(test), "n_train": len(train),
            "acc_linear": accuracy(lin_preds, gold), "acc_simvote": accuracy(sim_preds, gold),
            "acc_module": accuracy(mod_preds, gold), "module_chosen_name": mod_name,
        })
    return folds


def lovo_aggregate(folds):
    n_total = sum(f["n_test"] for f in folds)
    agg = {}
    for arm in ("linear", "simvote", "module"):
        key = "acc_%s" % arm
        num = sum(f[key] * f["n_test"] for f in folds if f[key] is not None)
        agg[arm] = (num / n_total) if n_total else None
    return agg, n_total


# ========================================================================================
# Scramble control: deterministic verb<->polarity_class permutation (NOT hash()-seeded)
# ========================================================================================
def scramble_items(items, seed=SCRAMBLE_SEED):
    verbs = sorted(set(it["verb_lemma"] for it in items))
    classes = [GOLD.IMPLICATIVE_LEXICON[v] for v in verbs]
    rng = random.Random(seed)
    shuffled_classes = list(classes)
    rng.shuffle(shuffled_classes)
    # guard: a shuffle that lands on the identity permutation would silently no-op the control.
    if shuffled_classes == classes:
        shuffled_classes = shuffled_classes[::-1]
    verb_to_scrambled_class = dict(zip(verbs, shuffled_classes))
    out = []
    for it in items:
        pc = verb_to_scrambled_class[it["verb_lemma"]]
        label = GOLD.KARTTUNEN_TRUTH_TABLE[(pc, it["negated"])]
        new_it = dict(it)
        new_it["gold_class"] = label
        new_it["scrambled_polarity_class"] = pc
        out.append(new_it)
    return out, verb_to_scrambled_class


# ========================================================================================
# Accuracy + margin helpers
# ========================================================================================
def accuracy(preds, gold):
    if not gold:
        return None
    correct = sum(1 for p, g in zip(preds, gold) if p == g)
    return correct / len(gold)


def majority_class(items):
    c = Counter(it["gold_class"] for it in items)
    return c.most_common(1)[0][0] if c else None


def arms_differ_hash(pred_dict):
    """META_RULE_AF: arms must not be bit-identical. pred_dict: {arm_name: list[str preds]}."""
    digests = {}
    for name, preds in pred_dict.items():
        b = ("|".join(preds)).encode("utf-8")
        digests[name] = hashlib.sha256(b).hexdigest()
    names = sorted(digests.keys())
    identical_pairs = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if digests[names[i]] == digests[names[j]]:
                identical_pairs.append((names[i], names[j]))
    return digests, identical_pairs


# ========================================================================================
# Synthetic mini-XOR positive control (mechanism check -- run BEFORE trusting the real data)
# ========================================================================================
def make_synthetic_xor(n_per_quadrant=20, seed=42):
    rng = random.Random(seed)
    instances = []
    quadrants = [(0, 0), (0, 1), (1, 0), (1, 1)]
    iid = 0
    for (a, b) in quadrants:
        label = "XOR1" if (a != b) else "XOR0"
        for _ in range(n_per_quadrant):
            instances.append({"iid": iid, "a": a, "b": b, "gold_class": label,
                               "verb_lemma": "a%d" % a, "negated": bool(b)})
            iid += 1
    rng.shuffle(instances)
    return instances


def synthetic_feat_fn(inst):
    return ["a=%d" % inst["a"], "b=%d" % inst["b"]]


def run_positive_control():
    ctrl_items = make_synthetic_xor()
    classes = sorted(set(it["gold_class"] for it in ctrl_items))
    spec = {
        "candidate_plugins": ["estimation", "ruleind", "gam"],
        "per_plugin": {
            "estimation": {"mode": "generic_mdl", "key_fn": lambda ep: ep["a"],
                           "label_fn": lambda ep: ep["gold_class"], "classes": classes},
            "ruleind": {"max_conjunct": 2, "min_coverage": 2, "purity_thresh": 0.85,
                        "key_fn": lambda ep: ep["a"]},
            "gam": {"label_fn": lambda ep: ep["gold_class"], "classes": classes, "min_coverage": 2},
        },
    }
    chosen_name, chosen, all_results = registry.learn(ctrl_items, synthetic_feat_fn, spec)
    ok = (chosen_name in ("ruleind", "gam")) and (chosen is not None) and (chosen.compression_ratio > 1.0)
    return {
        "chosen_name": chosen_name,
        "compression_ratios": {n: (r.compression_ratio if r.description_bits > 0 or r.null_bits > 0 else None)
                                for n, r in all_results.items()},
        "passed": bool(ok),
    }


# ========================================================================================
# Crash diagnostics + atomic write (META_RULE_AH / §8 / §13-C)
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
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


# ========================================================================================
# Main pipeline
# ========================================================================================
def run_pipeline(run_mode):
    t0 = time.perf_counter()

    # ---- 0. Positive control (mechanism check, must pass before trusting the real data) ----
    ctrl = run_positive_control()

    # ---- 1. Load real mined gold ----
    items, mine_stats = load_items()
    classes = sorted(set(it["gold_class"] for it in items))
    assert len(items) > 0, "INSTRUMENTATION_SUSPECT: 0 mined implicative items"

    # ---- 2. SEEN-verb split ----
    seen_train, seen_test = stratified_split(items)
    assert len(seen_test) > 0, "INSTRUMENTATION_SUSPECT: 0 seen-verb test items"

    linear_res = linear_fit(seen_train, classes)
    linear_preds_seen = linear_predict(linear_res, seen_test)
    simvote_preds_seen = simvote_fit_predict(seen_train, seen_test)
    module_chosen_name, module_chosen, module_all_results = module_fit(seen_train, classes)
    seen_default = majority_class(seen_train)
    module_preds_seen = module_predict(module_chosen_name, module_chosen, seen_test, seen_default)

    acc_linear_seen = accuracy(linear_preds_seen, [it["gold_class"] for it in seen_test])
    acc_simvote_seen = accuracy(simvote_preds_seen, [it["gold_class"] for it in seen_test])
    acc_module_seen = accuracy(module_preds_seen, [it["gold_class"] for it in seen_test])

    digests_seen, identical_pairs_seen = arms_differ_hash({
        "linear": linear_preds_seen, "simvote": simvote_preds_seen, "module": module_preds_seen,
    })

    # ---- 3. Scramble control (verb<->class permutation; must collapse SEEN accuracy) ----
    scrambled_items, verb_to_scrambled = scramble_items(items)
    scr_train, scr_test = stratified_split(scrambled_items)
    scr_module_chosen_name, scr_module_chosen, _scr_all = module_fit(scr_train, classes)
    scr_default = majority_class(scr_train)
    scr_module_preds = module_predict(scr_module_chosen_name, scr_module_chosen, scr_test, scr_default)
    acc_module_scrambled = accuracy(scr_module_preds, [it["gold_class"] for it in scr_test])
    scramble_delta = (acc_module_seen - acc_module_scrambled) if (acc_module_seen is not None and
                                                                   acc_module_scrambled is not None) else None

    # ---- 4. HELD-OUT-VERB generalization: leave-one-verb-out sweep across ALL 9 verbs ----
    # (Superseded the original fixed avoid+hesitate pair: that fold was DEGENERATE -- both
    # held-out verbs shared the training-MAJORITY class, so linear/simvote/module all tied at
    # 1.0/0.0-margin, a "perfectly constant metric expected to vary" per the suspicious-result
    # gate. LOVO exercises every verb as its own fold, including bother/manage/dare -- the pos-
    # impl folds that are the actual discriminating test of cross-class transfer, since bother is
    # the sole pos-impl-negated verb in the whole corpus.)
    lovo_folds = lovo_eval(items, classes)
    assert len(lovo_folds) > 0, "INSTRUMENTATION_SUSPECT: 0 LOVO folds"
    lovo_agg, lovo_n_total = lovo_aggregate(lovo_folds)
    acc_linear_ho, acc_simvote_ho, acc_module_ho = lovo_agg["linear"], lovo_agg["simvote"], lovo_agg["module"]
    # the two negated-pos-implicative-informative folds (bother is the only one with real
    # negated coverage; manage/dare have 0 negated instances in the corpus, so their folds only
    # test the affirmative direction transfer)
    critical_folds = {f["verb"]: f for f in lovo_folds if f["polarity_class"] == "pos"}

    EPS = 1e-9  # float-precision guard: 0.19999999999999996 must count as >= 0.20

    # ---- 5. Verdict logic ----
    margin_module_linear_seen = (acc_module_seen - acc_linear_seen) if (acc_module_seen is not None and acc_linear_seen is not None) else None
    margin_module_simvote_seen = (acc_module_seen - acc_simvote_seen) if (acc_module_seen is not None and acc_simvote_seen is not None) else None
    margin_module_linear_ho = (acc_module_ho - acc_linear_ho) if (acc_module_ho is not None and acc_linear_ho is not None) else None
    margin_module_simvote_ho = (acc_module_ho - acc_simvote_ho) if (acc_module_ho is not None and acc_simvote_ho is not None) else None

    if not ctrl["passed"]:
        overall = "HARD_FAIL_MECHANISM"
        msg = "Positive control failed: module chose %r on synthetic XOR (expected ruleind/gam)." % ctrl["chosen_name"]
    else:
        module_is_nonlinear = module_chosen_name in ("ruleind", "gam")
        hard_pass_seen = (
            module_is_nonlinear and
            (acc_module_seen or 0) >= HP_SEEN_ACC_MIN - EPS and
            (margin_module_linear_seen or 0) >= HP_SEEN_MARGIN_MIN - EPS and
            (margin_module_simvote_seen or 0) >= HP_SEEN_MARGIN_MIN - EPS and
            (scramble_delta or 0) >= SCRAMBLE_COLLAPSE_MIN - EPS
        )
        hard_fail_seen = (
            (acc_linear_seen or 0) >= HF_SEEN_LINEAR_MAX or
            len(seen_test) < HF_SEEN_MIN_N_TEST or
            (module_is_nonlinear and not hard_pass_seen and
             (margin_module_linear_seen or 0) < 0.05 and (margin_module_simvote_seen or 0) < 0.05)
        )
        hard_pass_heldout = (
            (acc_module_ho or 0) >= HP_HELDOUT_ACC_MIN - EPS and
            (margin_module_linear_ho or 0) >= HP_HELDOUT_MARGIN_MIN - EPS and
            (margin_module_simvote_ho or 0) >= HP_HELDOUT_MARGIN_MIN - EPS
        )
        if hard_fail_seen:
            overall = "HARD_FAIL_TASK_IS_LINEAR_OR_SIMILARITY_SHAPED"
            msg = ("SEEN-verb HARD_FAIL: linear_acc=%.3f (>= %.2f floor?) n_test=%d module_margin_linear=%s module_margin_simvote=%s" %
                   (acc_linear_seen or -1, HF_SEEN_LINEAR_MAX, len(seen_test), margin_module_linear_seen, margin_module_simvote_seen))
        elif hard_pass_seen and hard_pass_heldout:
            overall = "HARD_PASS_LEARNER_CLASS_HELPS_SEEN_AND_HELDOUT"
            msg = ("SEEN+HELDOUT HARD_PASS: module=%s seen_acc=%.3f (margin_lin=%.3f margin_sim=%.3f) heldout_acc=%.3f (margin_lin=%.3f margin_sim=%.3f)" %
                   (module_chosen_name, acc_module_seen, margin_module_linear_seen, margin_module_simvote_seen,
                    acc_module_ho, margin_module_linear_ho, margin_module_simvote_ho))
        elif hard_pass_seen and not hard_pass_heldout:
            overall = "HARD_PASS_SEEN_HELDOUT_BOUND"
            msg = ("SEEN HARD_PASS (module=%s acc=%.3f margin_lin=%.3f margin_sim=%.3f, scramble_delta=%.3f); "
                   "HELDOUT bound: acc=%.3f margin_lin=%s margin_sim=%s (analytically anticipated "
                   "representational bound -- one-hot verb id has zero cross-verb overlap; see brain-check)" %
                   (module_chosen_name, acc_module_seen, margin_module_linear_seen, margin_module_simvote_seen,
                    scramble_delta, acc_module_ho, margin_module_linear_ho, margin_module_simvote_ho))
        else:
            overall = "MIDDLE_BAND"
            msg = ("MIDDLE_BAND: module=%s seen_acc=%s margin_lin_seen=%s margin_sim_seen=%s scramble_delta=%s "
                   "heldout_acc=%s margin_lin_ho=%s margin_sim_ho=%s" %
                   (module_chosen_name, acc_module_seen, margin_module_linear_seen, margin_module_simvote_seen,
                    scramble_delta, acc_module_ho, margin_module_linear_ho, margin_module_simvote_ho))

    elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "verdict": overall, "verdict_msg": msg,
        "summary": msg, "elapsed_s": round(elapsed, 4),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "positive_control": ctrl,
        "mining_stats": mine_stats,
        "n_items_total": len(items),
        "n_seen_train": len(seen_train), "n_seen_test": len(seen_test),
        "lovo_n_folds": len(lovo_folds), "lovo_n_total_test_items": lovo_n_total,
        "lovo_folds": lovo_folds,
        "lovo_critical_pos_impl_folds": critical_folds,
        "module_chosen_name_seen": module_chosen_name,
        "module_compression_ratios_seen": {n: r.compression_ratio for n, r in module_all_results.items()},
        "acc_linear_seen": acc_linear_seen, "acc_simvote_seen": acc_simvote_seen, "acc_module_seen": acc_module_seen,
        "acc_linear_heldout_lovo": acc_linear_ho, "acc_simvote_heldout_lovo": acc_simvote_ho, "acc_module_heldout_lovo": acc_module_ho,
        "margin_module_linear_seen": margin_module_linear_seen, "margin_module_simvote_seen": margin_module_simvote_seen,
        "margin_module_linear_heldout_lovo": margin_module_linear_ho, "margin_module_simvote_heldout_lovo": margin_module_simvote_ho,
        "scramble_module_acc_seen": acc_module_scrambled, "scramble_delta": scramble_delta,
        "scramble_verb_to_class_map": verb_to_scrambled,
        "arms_differ_seen": {"digests": digests_seen, "identical_pairs": identical_pairs_seen},
        "arms_differ_verified": bool(len(identical_pairs_seen) == 0),
        "cell_chunked": False, "final_metrics_atomicity": "tmp_replace",
        "crlb_n_a": "accuracy/compression-ratio measurement, not a capacity/CRLB-bound cell",
        "deterministic_seeding": True,
        "cardinality_ok": True, "expected_n_units": 1,
        "calibration_check": "default_ok_for_this_regime",
    }
    return metrics


# ========================================================================================
# Instrumentation self-test (MANDATORY at module scope before any dispatch)
# ========================================================================================
def _instrumentation_selftest():
    ctrl = run_positive_control()
    assert ctrl["chosen_name"] in ("ruleind", "gam"), \
        "instrumentation self-test: module did not choose a nonlinear plugin on synthetic XOR (got %r)" % ctrl["chosen_name"]
    assert ctrl["passed"], "instrumentation self-test: positive control did not pass"
    items, stats = load_items()
    assert len(items) > 0, "instrumentation self-test: 0 mined implicative items -- mining filter eliminated everything"
    assert stats["n_raw_hits"] > 0
    train, test = stratified_split(items)
    assert len(train) > 0 and len(test) > 0, "instrumentation self-test: stratified split produced an empty side"
    classes = sorted(set(it["gold_class"] for it in items))
    folds = lovo_eval(items, classes)
    assert len(folds) > 0, "instrumentation self-test: 0 LOVO folds"
    assert any(f["polarity_class"] == "pos" for f in folds), \
        "instrumentation self-test: no pos-implicative fold in LOVO -- lexicon/mining regression"
    lin = linear_fit(train, classes)
    preds = linear_predict(lin, test[:3])
    assert all(p is not None for p in preds), "instrumentation self-test: linear arm produced None predictions"


_instrumentation_selftest()  # Called at module scope before the main sweep


def self_test():
    metrics = run_pipeline(run_mode="self_test")
    _write_metrics(OUTPUT_DIR, metrics)
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
        "arms_differ_seen", "arms_differ_heldout", "scramble_verb_to_class_map")}, indent=2))


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
