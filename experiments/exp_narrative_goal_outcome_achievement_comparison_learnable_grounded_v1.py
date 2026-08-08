#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_narrative_goal_outcome_achievement_comparison_learnable_grounded_v1

INC-2: the empirically-pinned part-2 build (notes/formalize_narrative_part2_goal_achievement_
inference_2026-08-08.md). The INC-1 diagnostic (fe414d2a1) pinned the narrative met/unmet
bottleneck to the achievement-COMPARISON, not goal-recognition: the owned
hdlab.goal_typing._class_relation (via the hand CLASS_REGISTRY) abstains 43/50 on modern
narrative outcomes ("won a silver medal" / "gave up swimming" / "went to Europe" for an
Africa goal). This cell builds a LEARNABLE/GROUNDED achievement-comparison: given (goal,
outcome), judge does-outcome-achieve-goal -> MET/UNMET, generalizing past the hand
CLASS_REGISTRY, and measures it against the 0.60 surface-cue plateau the generality cell
(exp_narrative_goal_outcome_role_sharded_generality_v1, commit d47643d87 lineage) already
pinned on this SAME held-out split.

DATA / SPLIT: experiments/data/narrative_goal_outcome_rocstories_relabeled_v1.jsonl (50 items,
25 MET/25 UNMET). SAME stratified split as the generality cell -- imported directly
(stratified_split/load_items from that module, not reimplemented) so n_train=30/n_test=20 and
train/test membership are byte-identical, making accuracy numbers directly comparable to the
0.60 surface plateau (naive_flat=0.6100, role_shard_weighted/role_shard_select=0.6000,
majority_acc=0.5000; data/exp_narrative_goal_outcome_role_sharded_generality_v1/metrics.json).

FEATURES -- the GOAL<->OUTCOME RELATION (not just outcome-surface cues; that is the whole
point). Per (goal, outcome) pair, all REUSED/imported from hdlab (no reimplementation):
  - class_relation: hdlab.goal_typing._class_relation(desired_classes, actual_classes) ->
    same/opposed/none. desired_classes/actual_classes come from
    hdlab.goal_typing.find_desired_state (goal side) and find_actual_state_candidates (outcome
    side, threaded with the goal's own verb lemma so the recurrence channel can fire) -- the
    CLASS_REGISTRY signal, exposed as ONE feature (not the final answer).
  - goal_verb_class / outcome_verb_class: the raw class-name set(s) each side resolved to
    (via Tier-1 literal + Tier-2 shared-feature-similarity + Tier-3 acquired-pole fallback,
    all already inside find_desired_state/find_actual_state_candidates).
  - owned_verdict / owned_reason: hdlab.goal_typing.congruence_outcome_valence_windowed's own
    MET/UNMET/NA call + reason code (referent-linked class comparison + occurrence-gate) --
    the full owned "does outcome achieve goal" mechanism, as features (not consumed as the
    final answer for ARM-LEARN/ARM-GROUNDED, only as a BASELINE and as input signal).
  - referent_recur_verdict: hdlab.goal_typing.congruence_referent_recurrence_windowed's
    referent-recurrence channel (does the goal's target noun recur in the outcome, via
    literal / shared-feature / noun-concept-class matching).
  - referent_literal_match / referent_sim_bucket: literal recurrence of the goal referent in
    the outcome tokens, and a GROUNDED shared-feature cosine bucket
    (hdlab.lexical_similarity.concept_similarity(goal_referent, outcome_referent)).
  - verb_sim_bucket: GROUNDED shared-feature cosine bucket between the goal's own desired verb
    lemma and the highest-similarity verb lemma anywhere in the outcome sentence
    (hdlab.verb_lexical_similarity.word_similarity(goal_verb_lemma, outcome_lemma, "outcome"),
    an OPEN scan over every outcome token -- NOT gated on CLASS_REGISTRY classifiability the
    way find_actual_state_candidates is, so this reaches words class_relation can never see).
  - outcome_verb_negated / outcome_negation_present / modal_failure_present: negation-scope
    signals (hdlab.goal_typing's own _verb_negated_before-derived `negated` flag on the primary
    outcome candidate, plus the generality cell's own surface negation/modal-failure regexes).
  - achieve_verb_present / fail_verb_present / positive_affect_present / negative_affect_present
    / result_state_polarity: the generality cell's OWN achievement-marker / affect-reaction
    lexicons (ACHIEVE_VERBS/FAIL_VERBS/POS_AFFECT/NEG_AFFECT/POS_RESULT_ADJ/NEG_RESULT_ADJ),
    imported not copied -- these are the surface cues the 0.60 plateau arms already used; kept
    here too because the task brief calls for them alongside the relational signals (a fair
    RELATION-vs-surface comparison needs the relation features to have a chance to ADD on top
    of, not replace, the surface ones the learner can already see).
Deliberately EXCLUDED: raw verb lemma / raw referent string as standalone features (that would
be memorizing the hand-vocabulary story-by-story, defeating the "generalize past the hand list"
point of this build) -- only CLASS names, similarity BUCKETS, and boolean/categorical relation
verdicts are exposed to the learner.

ARMS (measured on the SAME held-out 20, same features where applicable):
  ARM-LEARN: hdlab.learner.registry.learn(candidate_plugins=["estimation","ruleind","gam"]) over
    the relation-feature vectors -> MET/UNMET (the part-1 playbook, hdlab/goal_typing.py's own
    induce_hypothesis pattern, applied to the achievement-COMPARISON instead of goal-recognition).
  ARM-GROUNDED: a fixed (non-learned, does not read train labels) lexical_similarity-based rule:
    class_relation same/opposed (grounded via Tier-2/3 shared-feature similarity already inside
    _class_relation) wins first; else a high open-vocab verb-similarity bucket; else a literal or
    high-similarity referent match; else the referent-recurrence channel; else abstain -> majority
    fallback. Pure grounded comparison, no learner, no train-label fitting.
  BASELINE owned_class_relation: hdlab.goal_typing.congruence_outcome_valence_windowed's own
    verdict, majority-fallback on NA (expect high abstention, the 96%-abstain floor the INC-1
    diagnostic measured).
  BASELINE surface plateau: CITED from the generality cell's own metrics.json on this identical
    split (naive_flat mean_acc=0.6100, role_shard_weighted/select=0.6000) -- not recomputed here.
  BASELINE majority: recomputed on this split for self-consistency (must equal 0.5000, the
    generality cell's own majority_acc, since the split is byte-identical).
  SCRAMBLE control: fixed-seed TRAIN label permutation, ARM-LEARN refit from scratch. (ARM-GROUNDED
    never reads train labels, so a label-scramble is definitionally vacuous for it -- reported
    honestly, not silently glossed over; ARM-GROUNDED's non-vacuousness is instead evidenced by
    beats-majority + non-constant-predictions.)

GATE (pre-registered; anti-premature-HARD_FAIL; brain=existence-proof, ACC does goal-monitoring):
  HARD-PASS: max(ARM-LEARN, ARM-GROUNDED) held-out acc > SURFACE_PLATEAU=0.60 AND > majority=0.50,
    non-constant predictions, ARM-LEARN non-episodic (chosen_name != KEEP_EPISODIC) AND its
    scramble collapses (scramble_acc <= SCRAMBLE_BAND=0.60) -> the goal<->outcome RELATION adds
    real signal past surface cues, part-2 tractable.
  NULL/FAIL: <=0.60 -> diagnose (referent-matching/world-knowledge gap? n too small? similarity too
    coarse?), NOT a ceiling.

COMPUTE: n=50 items, closed-form glass-box feature extraction (no VSA fit/no gradient loop for the
relation features themselves; hdlab.learner's ruleind/gam/estimation plugins are also closed-form
counting/search, not iterative training) -- sub-few-seconds wall time. Single blocking run, no
checkpointing needed (this is not a multi-unit long-running cell). Deterministic: fixed-int
SPLIT_SEED (imported from the generality cell, 240817) / SCRAMBLE_SEED (552017, this cell's own,
NOT hash()-derived), no torch RNG in the relation-feature path (hdlab.lexical_similarity /
hdlab.verb_lexical_similarity cache their own deterministic FHRR vectors internally).
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
import re
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ANCHOR_NAME = "narrative_goal_outcome_achievement_comparison_learnable_grounded_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# ---- reuse, not reimplement: the generality cell's own split + surface-cue lexicons ----
from experiments.exp_narrative_goal_outcome_role_sharded_generality_v1 import (  # noqa: E402
    load_items, stratified_split, majority_class, accuracy,
    ACHIEVE_VERBS, FAIL_VERBS, MODAL_FAILURE_RE, NEGATION_RE, POS_RESULT_ADJ, NEG_RESULT_ADJ,
    POS_AFFECT, NEG_AFFECT,
)
# ---- reuse, not reimplement: the owned goal-typing / achievement-comparison organs ----
from hdlab.goal_typing import (  # noqa: E402
    _sentences, find_desired_state, find_actual_state_candidates, _class_relation,
    congruence_outcome_valence_windowed, congruence_referent_recurrence_windowed,
)
from hdlab.thematic_role_labeler import lemma_verb  # noqa: E402
from hdlab.lexical_similarity import (  # noqa: E402
    concept_similarity as lexsim_concept_similarity, in_lexicon as lexsim_in_lexicon,
)
from hdlab import verb_lexical_similarity as verblex  # noqa: E402
from hdlab.learner import apply as learner_apply, learn as learner_learn  # noqa: E402
from hdlab.learner.core import KEEP_EPISODIC  # noqa: E402

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
GENERALITY_METRICS_PATH = os.path.join(
    REPO_ROOT, "data", "exp_narrative_goal_outcome_role_sharded_generality_v1", "metrics.json")

# ---- pre-registered config / gate (see module docstring) ----
SCRAMBLE_SEED = 552017          # fixed int, NOT hash()-derived, distinct from sibling cells'
SCRAMBLE_BAND = 0.60
EPS = 1e-9
SIM_HIGH = 0.60
SIM_LOW = 0.35
SURFACE_PLATEAU = 0.60          # CITED, see module docstring / _load_surface_plateau_citation()
LABELS = ["MET", "UNMET"]


# ========================================================================================
# Feature extraction -- the goal<->outcome RELATION (see module docstring)
# ========================================================================================
def _bucket_sim(sim):
    if sim is None:
        return "oov"
    if sim >= SIM_HIGH:
        return "high"
    if sim >= SIM_LOW:
        return "med"
    return "low"


def _outcome_tokens(text):
    return re.findall(r"[a-z']+", text.lower())


def _outcome_open_verb_sim(goal_verb_lemma, outcome_lemmas):
    """OPEN scan (not gated on CLASS_REGISTRY classifiability): max shared-feature cosine between
    goal_verb_lemma and ANY outcome-sentence token lemma present in the verb_lexical_similarity
    'outcome' domain lexicon. None if goal_verb_lemma itself is OOV or no outcome token is in the
    lexicon at all -- honest abstain, never a forced guess."""
    if goal_verb_lemma is None or not verblex.in_lexicon(goal_verb_lemma, "outcome"):
        return None
    best = None
    for lemma in outcome_lemmas:
        if not verblex.in_lexicon(lemma, "outcome"):
            continue
        s = verblex.word_similarity(goal_verb_lemma, lemma, "outcome")
        if s is not None and (best is None or s > best):
            best = s
    return best


def extract_relation_features(item):
    goal_text = item["goal_text"]
    outcome_text = item["outcome_text"]
    full_text = item["text"]

    goal_sents = _sentences(goal_text)
    desired = None
    for gs in goal_sents:
        d = find_desired_state(gs)
        if d is not None:
            desired = d
            break
    goal_verb_lemma = desired.get("verb_lemma") if desired else None
    goal_referent = desired.get("referent") if desired else None
    desired_classes = set(desired.get("classes", set())) if desired else set()

    outcome_candidates = find_actual_state_candidates(outcome_text, goal_verb_lemma)
    primary = None
    if outcome_candidates:
        primary = next((c for c in outcome_candidates
                         if _class_relation(desired_classes, c["classes"]) is not None),
                        outcome_candidates[0])
    outcome_referent = primary.get("referent") if primary else None
    outcome_verb_negated = bool(primary.get("negated")) if primary else False
    actual_classes = set(primary.get("classes", set())) if primary else set()
    class_relation = _class_relation(desired_classes, actual_classes) or "none"

    owned_verdict, owned_detail = congruence_outcome_valence_windowed(full_text, max_window=4)
    referent_recur_verdict, rr_detail = congruence_referent_recurrence_windowed(full_text, max_window=2)

    outcome_toks = _outcome_tokens(outcome_text)
    outcome_lemmas = [lemma_verb(t) for t in outcome_toks]
    verb_sim = _outcome_open_verb_sim(goal_verb_lemma, outcome_lemmas)

    referent_sim = None
    if (goal_referent is not None and outcome_referent is not None
            and lexsim_in_lexicon(goal_referent) and lexsim_in_lexicon(outcome_referent)):
        referent_sim = lexsim_concept_similarity(goal_referent, outcome_referent)
    referent_literal_match = bool(goal_referent) and (goal_referent in outcome_toks)

    outcome_lower = outcome_text.lower()
    outcome_tokset = set(outcome_toks)

    feats = {
        "owned_verdict": owned_verdict,
        "owned_reason": owned_detail.get("reason", "none"),
        "referent_recur_verdict": referent_recur_verdict,
        "class_relation": class_relation,
        "goal_verb_class": ",".join(sorted(desired_classes)) if desired_classes else "none",
        "outcome_verb_class": ",".join(sorted(actual_classes)) if actual_classes else "none",
        "verb_sim_bucket": _bucket_sim(verb_sim),
        "referent_sim_bucket": _bucket_sim(referent_sim),
        "referent_literal_match": referent_literal_match,
        "outcome_verb_negated": outcome_verb_negated,
        "outcome_negation_present": bool(NEGATION_RE.search(outcome_lower)),
        "modal_failure_present": bool(MODAL_FAILURE_RE.search(outcome_lower)),
        "achieve_verb_present": bool(outcome_tokset & ACHIEVE_VERBS),
        "fail_verb_present": bool(outcome_tokset & FAIL_VERBS),
        "positive_affect_present": bool(outcome_tokset & POS_AFFECT),
        "negative_affect_present": bool(outcome_tokset & NEG_AFFECT),
        "result_state_polarity": (
            "positive" if any(a in outcome_lower for a in POS_RESULT_ADJ) and
                          not any(a in outcome_lower for a in NEG_RESULT_ADJ)
            else "negative" if any(a in outcome_lower for a in NEG_RESULT_ADJ)
            else "none"),
    }
    debug = {
        "goal_verb_lemma": goal_verb_lemma, "goal_referent": goal_referent,
        "outcome_referent": outcome_referent, "verb_sim": verb_sim, "referent_sim": referent_sim,
        "owned_reason": owned_detail.get("reason"), "rr_reason": rr_detail.get("reason"),
    }
    return feats, debug


def feat_fn(feats):
    """PRESENCE-ONLY boolean encoding + always-emit categorical encoding -- same 'name=value'/
    'name=True' convention as the generality cell's own feat_fn."""
    out = []
    for name, val in feats.items():
        if isinstance(val, bool):
            if val:
                out.append("%s=True" % name)
        else:
            out.append("%s=%s" % (name, val))
    return out


def build_episode(item):
    feats, debug = extract_relation_features(item)
    return {"id": item["id"], "gold_class": item["gold"], "feats": feat_fn(feats),
            "_feats_raw": feats, "_debug": debug}


# ========================================================================================
# ARM-GROUNDED: fixed, non-learned lexical_similarity-based rule (no train-label fitting)
# ========================================================================================
def grounded_rule_predict(ep, majority_fallback):
    f = ep["_feats_raw"]
    neg = f["outcome_verb_negated"]
    if f["class_relation"] == "same":
        return "UNMET" if neg else "MET"
    if f["class_relation"] == "opposed":
        return "MET" if neg else "UNMET"
    if f["verb_sim_bucket"] == "high":
        return "UNMET" if neg else "MET"
    if f["referent_literal_match"] or f["referent_sim_bucket"] == "high":
        return "UNMET" if neg else "MET"
    if f["referent_recur_verdict"] in ("MET", "UNMET"):
        return f["referent_recur_verdict"]
    return majority_fallback


# ========================================================================================
# ARM-LEARN: hdlab.learner.registry over the relation-feature vectors
# ========================================================================================
CORE_RELATION_FAMS = {"owned_verdict", "referent_recur_verdict", "class_relation",
                       "achieve_verb_present", "fail_verb_present"}


def estimation_key_fn(ep):
    return tuple(sorted(f for f in ep["feats"] if f.split("=", 1)[0] in CORE_RELATION_FAMS))


def default_key_fn(ep):
    return tuple(sorted(ep["feats"]))


HYP_SPACE_SPEC = {
    "candidate_plugins": ["estimation", "ruleind", "gam"],
    "key_fn": default_key_fn,
    "label_fn": lambda ep: ep["gold_class"],
    "classes": ["MET", "UNMET"],
    "min_coverage": 2, "purity_thresh": 0.85, "max_conjunct": 2, "max_rules": 8,
    # NOTE: hdlab/learner/registry.py's per_plugin override REPLACES the whole spec dict for that
    # plugin (`per_plugin_spec.get(name, hypothesis_space_spec)`), it does not merge -- so the
    # estimation override below must be a COMPLETE spec (label_fn/classes included), not a partial
    # patch, or estimation_plugin's label_fn/classes fall back to their (dict-incompatible)
    # defaults and crash. Only key_fn actually differs from the shared spec above.
    "per_plugin": {"estimation": {
        "key_fn": estimation_key_fn, "label_fn": lambda ep: ep["gold_class"],
        "classes": ["MET", "UNMET"],
    }},
}


def fit_learn_arm(train_episodes, spec=HYP_SPACE_SPEC):
    chosen_name, chosen, all_results = learner_learn(train_episodes, lambda ep: ep["feats"], spec)
    return chosen_name, chosen, all_results


def apply_learn_arm(chosen_name, chosen, ep, majority_fallback):
    if chosen_name == KEEP_EPISODIC or chosen is None:
        return majority_fallback
    if chosen_name == "estimation":
        return learner_apply("estimation", chosen.hypothesis, estimation_key_fn(ep))
    if chosen_name == "ruleind":
        return learner_apply("ruleind", chosen.hypothesis, ep["feats"],
                              key=default_key_fn(ep), default_class=majority_fallback)
    if chosen_name == "gam":
        return learner_apply("gam", chosen.hypothesis, ep["feats"])
    raise ValueError("unexpected chosen_name %r" % chosen_name)


def scramble_labels(episodes, seed=SCRAMBLE_SEED):
    rng = random.Random(seed)
    labels = [ep["gold_class"] for ep in episodes]
    shuffled = list(labels)
    rng.shuffle(shuffled)
    if shuffled == labels:
        shuffled = shuffled[::-1]
    out = []
    for ep, lbl in zip(episodes, shuffled):
        new_ep = dict(ep)
        new_ep["gold_class"] = lbl
        out.append(new_ep)
    return out


# ========================================================================================
# BASELINE: owned achievement-comparison (congruence_outcome_valence_windowed), majority-fallback
# ========================================================================================
def owned_baseline_predict(ep, majority_fallback):
    v = ep["_feats_raw"]["owned_verdict"]
    return v if v in ("MET", "UNMET") else majority_fallback


def _digest(preds):
    return hashlib.sha256(json.dumps(list(preds)).encode()).hexdigest()[:16]


def _load_surface_plateau_citation():
    try:
        with open(GENERALITY_METRICS_PATH, encoding="utf-8") as f:
            m = json.load(f)
        return {
            "source": GENERALITY_METRICS_PATH, "verdict": m.get("verdict"),
            "majority_acc": m.get("majority_acc"),
            "naive_flat_mean_acc": m["results_real"]["naive_flat"]["mean_acc"],
            "role_shard_weighted_mean_acc": m["results_real"]["role_shard_weighted"]["mean_acc"],
            "attention_flat_mean_acc": m["results_real"]["attention_flat"]["mean_acc"],
        }
    except Exception as exc:  # noqa: BLE001
        return {"source": GENERALITY_METRICS_PATH, "error": str(exc)}


# ========================================================================================
# Instrumentation self-test (data-independent formula checks + split/feature sanity)
# ========================================================================================
def _instrumentation_selftest():
    items = load_items()
    assert len(items) == 50, "expected 50 items, got %d" % len(items)
    train_raw, test_raw = stratified_split(items)
    assert len(train_raw) == 30 and len(test_raw) == 20, (len(train_raw), len(test_raw))
    assert sum(1 for it in test_raw if it["gold"] == "MET") == 10
    assert sum(1 for it in test_raw if it["gold"] == "UNMET") == 10
    train_ids = {it["id"] for it in train_raw}
    test_ids = {it["id"] for it in test_raw}
    assert not (train_ids & test_ids), "train/test overlap!"

    # feature extraction determinism: same item twice -> identical feats
    it0 = items[0]
    f1, _ = extract_relation_features(it0)
    f2, _ = extract_relation_features(it0)
    assert f1 == f2, "extract_relation_features is not deterministic"

    # feature extraction must not crash on any of the 50 items
    eps = [build_episode(it) for it in items]
    assert len(eps) == 50

    # scramble determinism / non-identity
    scr = scramble_labels(eps[:30])
    assert [e["gold_class"] for e in scr] != [e["gold_class"] for e in eps[:30]]
    scr2 = scramble_labels(eps[:30])
    assert [e["gold_class"] for e in scr] == [e["gold_class"] for e in scr2], "scramble not deterministic"

    return {"n_items": len(items), "n_train": len(train_raw), "n_test": len(test_raw)}


_INSTRUMENTATION = _instrumentation_selftest()


# ========================================================================================
# Main pipeline
# ========================================================================================
def run_pipeline(run_mode="full"):
    t0 = time.time()
    items = load_items()
    train_raw, test_raw = stratified_split(items)
    train_eps = [build_episode(it) for it in train_raw]
    test_eps = [build_episode(it) for it in test_raw]
    gold_test = [ep["gold_class"] for ep in test_eps]

    majority = majority_class(train_raw)
    majority_preds = [majority] * len(test_eps)
    majority_acc = accuracy(majority_preds, gold_test)

    # ---- BASELINE: owned achievement-comparison ----
    owned_preds = [owned_baseline_predict(ep, majority) for ep in test_eps]
    owned_acc = accuracy(owned_preds, gold_test)
    owned_verdicts_raw = [ep["_feats_raw"]["owned_verdict"] for ep in test_eps]
    owned_fire_rate = sum(1 for v in owned_verdicts_raw if v in ("MET", "UNMET")) / len(test_eps)
    fired_pairs = [(p, g) for p, g, v in zip(owned_preds, gold_test, owned_verdicts_raw) if v in ("MET", "UNMET")]
    owned_acc_when_fired = (sum(1 for p, g in fired_pairs if p == g) / len(fired_pairs)
                             if fired_pairs else None)

    # ---- ARM-GROUNDED (fixed rule, no train-label fitting) ----
    grounded_preds = [grounded_rule_predict(ep, majority) for ep in test_eps]
    grounded_acc = accuracy(grounded_preds, gold_test)
    grounded_fire_mask = [ep["_feats_raw"]["class_relation"] != "none"
                           or ep["_feats_raw"]["verb_sim_bucket"] == "high"
                           or ep["_feats_raw"]["referent_literal_match"]
                           or ep["_feats_raw"]["referent_sim_bucket"] == "high"
                           or ep["_feats_raw"]["referent_recur_verdict"] in ("MET", "UNMET")
                           for ep in test_eps]
    grounded_fire_rate = sum(grounded_fire_mask) / len(test_eps)

    # ---- ARM-LEARN ----
    chosen_name, chosen, all_results = fit_learn_arm(train_eps)
    learn_preds = [apply_learn_arm(chosen_name, chosen, ep, majority) for ep in test_eps]
    learn_acc = accuracy(learn_preds, gold_test)
    learn_non_episodic = chosen_name != KEEP_EPISODIC

    # ---- SCRAMBLE control on ARM-LEARN ----
    scrambled_train = scramble_labels(train_eps)
    scr_chosen_name, scr_chosen, _scr_all = fit_learn_arm(scrambled_train)
    scr_majority = majority_class([{"gold": e["gold_class"]} for e in scrambled_train])
    scr_preds = [apply_learn_arm(scr_chosen_name, scr_chosen, ep, scr_majority) for ep in test_eps]
    scr_acc = accuracy(scr_preds, gold_test)
    scramble_collapses = scr_acc <= SCRAMBLE_BAND

    surface_plateau_citation = _load_surface_plateau_citation()

    # ---- glass-box: per-feature-family train-set label purity (which relation features carry signal) ----
    family_signal = {}
    for fam in sorted(set(k for ep in train_eps for k in ep["_feats_raw"].keys())):
        by_val = {}
        for ep in train_eps:
            v = ep["_feats_raw"][fam]
            by_val.setdefault(str(v), Counter())[ep["gold_class"]] += 1
        rows = {}
        for v, c in by_val.items():
            n = sum(c.values())
            top = c.most_common(1)[0]
            rows[v] = {"n": n, "majority_label": top[0], "purity": round(top[1] / n, 3)}
        family_signal[fam] = rows

    # ---- gate ----
    best_arm_name = "ARM-LEARN" if learn_acc >= grounded_acc else "ARM-GROUNDED"
    best_acc = max(learn_acc, grounded_acc)
    best_preds = learn_preds if best_arm_name == "ARM-LEARN" else grounded_preds
    non_constant = len(set(best_preds)) > 1

    beats_plateau = best_acc > SURFACE_PLATEAU + EPS
    beats_majority = best_acc > majority_acc + EPS

    if (beats_plateau and beats_majority and non_constant and learn_non_episodic
            and scramble_collapses):
        verdict = "HARD_PASS"
        verdict_msg = ("%s held-out acc=%.4f beats SURFACE_PLATEAU=%.2f and majority=%.4f, "
                       "non-constant, ARM-LEARN non-episodic (chosen=%s), scramble collapses to "
                       "%.4f (<=%.2f) -- the goal<->outcome RELATION adds real signal past "
                       "surface cues; part-2 tractable."
                       % (best_arm_name, best_acc, SURFACE_PLATEAU, majority_acc, chosen_name,
                          scr_acc, SCRAMBLE_BAND))
    elif beats_majority and non_constant:
        verdict = "PARTIAL"
        verdict_msg = ("%s held-out acc=%.4f beats majority=%.4f but does NOT clear "
                       "SURFACE_PLATEAU=%.2f (or scramble/episodic gate failed: "
                       "learn_non_episodic=%s scramble_collapses=%s) -- partial relational "
                       "signal, not decisively past the surface-cue ceiling."
                       % (best_arm_name, best_acc, majority_acc, SURFACE_PLATEAU,
                          learn_non_episodic, scramble_collapses))
    else:
        verdict = "NULL_FAIL"
        verdict_msg = ("%s held-out acc=%.4f does not clear majority=%.4f -- diagnose "
                       "(referent-matching/world-knowledge gap? n too small? similarity too "
                       "coarse?), NOT a capability ceiling (ACC does goal-monitoring, brain is "
                       "the existence proof)." % (best_arm_name, best_acc, majority_acc))

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": "%s: best_arm=%s acc=%.4f vs surface_plateau=%.2f vs majority=%.4f vs owned=%.4f"
                   % (verdict, best_arm_name, best_acc, SURFACE_PLATEAU, majority_acc, owned_acc),
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "n_items": len(items), "n_train": len(train_eps), "n_test": len(test_eps),
        "majority_class": majority, "majority_acc": majority_acc,
        "owned_acc": owned_acc, "owned_fire_rate": owned_fire_rate,
        "owned_acc_when_fired": owned_acc_when_fired, "owned_n_fired": len(fired_pairs),
        "owned_preds": owned_preds, "owned_digest": _digest(owned_preds),
        "grounded_acc": grounded_acc, "grounded_fire_rate": grounded_fire_rate,
        "grounded_preds": grounded_preds, "grounded_digest": _digest(grounded_preds),
        "grounded_n_distinct_preds": len(set(grounded_preds)),
        "learn_acc": learn_acc, "learn_chosen_plugin": chosen_name,
        "learn_non_episodic": learn_non_episodic,
        "learn_preds": learn_preds, "learn_digest": _digest(learn_preds),
        "learn_n_distinct_preds": len(set(learn_preds)),
        "learn_hypothesis_metrics": (chosen.metrics if chosen is not None else None),
        "learn_hypothesis_n_free_params": (chosen.n_free_params if chosen is not None else None),
        "learn_hypothesis_compression_ratio": (chosen.compression_ratio if chosen is not None else None),
        "learn_all_plugin_results": {
            name: {"is_episodic": r.is_episodic, "compression_ratio": r.compression_ratio,
                   "cost_rank": r.cost_rank, "metrics": r.metrics}
            for name, r in all_results.items()},
        "scramble_chosen_plugin": scr_chosen_name, "scramble_acc": scr_acc,
        "scramble_collapses": scramble_collapses, "scramble_preds": scr_preds,
        "scramble_digest": _digest(scr_preds),
        "surface_plateau_citation": surface_plateau_citation,
        "family_signal_train": family_signal,
        "best_arm_name": best_arm_name, "best_acc": best_acc,
        "beats_plateau": beats_plateau, "beats_majority": beats_majority,
        "non_constant": non_constant,
        "gate": {"SURFACE_PLATEAU": SURFACE_PLATEAU, "SCRAMBLE_BAND": SCRAMBLE_BAND},
        "test_item_ids": [ep["id"] for ep in test_eps],
        "test_item_debug": {ep["id"]: ep["_debug"] for ep in test_eps},
        "test_item_gold": gold_test,
        "instrumentation": _INSTRUMENTATION,
    }
    return metrics


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


def self_test():
    metrics = run_pipeline(run_mode="self_test")
    _write_metrics(OUTPUT_DIR + "_selftest", metrics)
    print("[self_test] verdict=%s" % metrics["verdict"])
    print("[self_test] " + metrics["verdict_msg"])
    ok = metrics["verdict"] != "CELL_CRASHED"
    ok = ok and metrics["n_items"] == 50 and metrics["n_train"] == 30 and metrics["n_test"] == 20
    return ok


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
    print("---- held-out accuracy (n_test=%d) ----" % metrics["n_test"])
    print("  majority             = %.4f (class=%s)" % (metrics["majority_acc"], metrics["majority_class"]))
    print("  surface plateau CITED= %.4f (see surface_plateau_citation)" % SURFACE_PLATEAU)
    print("  owned (class_relation/congruence, majority-fallback) = %.4f  fire_rate=%.4f  acc_when_fired=%s"
          % (metrics["owned_acc"], metrics["owned_fire_rate"], metrics["owned_acc_when_fired"]))
    print("  ARM-GROUNDED         = %.4f  fire_rate=%.4f  n_distinct=%d"
          % (metrics["grounded_acc"], metrics["grounded_fire_rate"], metrics["grounded_n_distinct_preds"]))
    print("  ARM-LEARN            = %.4f  chosen_plugin=%s  non_episodic=%s  n_distinct=%d"
          % (metrics["learn_acc"], metrics["learn_chosen_plugin"], metrics["learn_non_episodic"],
             metrics["learn_n_distinct_preds"]))
    print("  ARM-LEARN SCRAMBLE   = %.4f  chosen_plugin=%s  collapses(<=%.2f)=%s"
          % (metrics["scramble_acc"], metrics["scramble_chosen_plugin"], SCRAMBLE_BAND,
             metrics["scramble_collapses"]))
    print("---- surface plateau citation ----")
    print(json.dumps(metrics["surface_plateau_citation"], indent=2))
    print("---- ARM-LEARN: all plugin results (compression_ratio / is_episodic / metrics) ----")
    print(json.dumps(metrics["learn_all_plugin_results"], indent=2, default=str))
    print("---- ARM-LEARN chosen hypothesis metrics ----")
    print(json.dumps(metrics["learn_hypothesis_metrics"], indent=2, default=str))
    print("---- glass-box: per-feature-family TRAIN-set label purity ----")
    print(json.dumps(metrics["family_signal_train"], indent=2, default=str))
    print("---- per-test-item: pred vs gold (owned / grounded / learn) ----")
    for i, iid in enumerate(metrics["test_item_ids"]):
        print("%-45s gold=%-6s owned=%-6s grounded=%-6s learn=%-6s"
              % (iid, metrics["test_item_gold"][i], metrics["owned_preds"][i],
                 metrics["grounded_preds"][i], metrics["learn_preds"][i]))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, exc)
        traceback.print_exc()
        sys.exit(1)
