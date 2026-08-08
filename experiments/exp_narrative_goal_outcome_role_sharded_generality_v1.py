#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_narrative_goal_outcome_role_sharded_generality_v1

THE #1 GENERALITY TEST for the overnight-drill winner, discriminativeness-weighted
ROLE-SHARDED, SHARD-SELECTED VSA superposition typing, WIRED to production
(hdlab.selection_weighted_sharded_typer.SelectionWeightedShardedTyper) after validating at
0.8333 on dialogue request/response (Tier 2/3, commit d47643d87). That validation is honestly
ONE construction. This cell asks: does the SAME wired typer (imported, not reimplemented)
generalize to a genuinely DIFFERENT construction -- NARRATIVE GOAL-OUTCOME (met/unmet) -- on
modern ROCStories-sourced prose, using its own narrative-specific glass-box features and role
map (different cues than dialogue's REQUEST/RESPONSE_POLARITY/DISCOURSE/FILLER_META)?

DATA: experiments/data/narrative_goal_outcome_rocstories_relabeled_v1.jsonl (50 items, 25
MET/25 UNMET). Built (see the sibling build script, and the Director-facing report of this
cycle) by (a) re-labeling the 30 original Story-Cloze-derived items by ACTUAL goal-achievement
(not Story-Cloze "correct ending"=plausible, which is a different axis -- 4 items flip MET->
UNMET, 6 ambiguous/incoherent items dropped, 24 kept) and (b) supplementing with 26 fresh, real
single-ending ROCStories continuations (wza/roc_stories HF mirror) hand-labeled by the same
rule, to reach a clean, balanced 50-item set. goal_text = story context (all sentences but the
last); outcome_text = final sentence; text = full concatenation.

ROLE MAP (narrative-specific, glass-box, presence-only-boolean + always-emit-categorical
encoding -- same 'name=value'/'name=True' convention as the dialogue cells' feat_fn):
  GOAL              goal_marker_type (want/wish/hope/dream/decide/need/plan/determined/none),
                     goal_marker_present, obstacle_cue_present (a contrastive/negated-capability
                     cue already IN the setup, before the outcome is read).
  OUTCOME_POLARITY   achieve_verb_present / fail_verb_present (closed lexical sets of
                     achievement vs failure/loss verbs in outcome_text), negation_present,
                     modal_failure_present ("couldn't"/"unable to"/...), result_state_polarity
                     (situation-adjective polarity: ruined/broken/successful/perfect/... vs
                     none).
  AFFECT_REACTION    positive_affect_present / negative_affect_present -- EXPERIENCER emotion
                     words (happy/glad/thrilled/proud/grateful vs upset/sad/disappointed/
                     devastated/cried/embarrassed), kept distinct from OUTCOME_POLARITY's
                     situation-adjectives (an emotion word describes the character's reaction,
                     not the state of the world).
  FILLER             narrator_person (first/third), has_dialogue_quote, exclamation_present,
                     text_len_bucket, sentence_count_bucket -- near-universal stylistic cues not
                     expected to carry the goal-outcome label, the role a naive equal-weight
                     bundle would let swamp a sparse discriminative cue (the exact failure mode
                     role-sharding exists to fix).
Every feature FAMILY is assigned to exactly one role; assert_full_role_coverage checks this
exhaustively over the fitted vocabulary (instrumentation self-test).

MECHANISM UNDER TEST (imported, not reimplemented -- hdlab/selection_weighted_sharded_typer.py):
  predict()            shard-LOO-weighted combine of unweighted per-role sub-bundles (the
                       VALIDATED/default route on dialogue).
  predict_select()      hard one-hot: route via only the single highest-LOO-accuracy shard.
  predict_composed()    both cue-level AND shard-level weighting together (exploratory on
                       dialogue too).
BASELINES, same held-out set, same feat_fn (zero encoding drift by construction): majority
(TRAIN mode), naive-flat (unweighted single-shard bundle -- realized by fitting a SECOND
SelectionWeightedShardedTyper instance whose role_of_term maps EVERY term to one role "ALL", so
its predict() reduces exactly to an unweighted flat superposition -- reuses the identical class,
zero duplicated VSA code), attention-flat (cue-weighted single-shard bundle -- the SAME
single-role instance's predict_composed(), which reduces exactly to a cue-discriminativeness-
weighted flat superposition since a single shard's shard-level weight is a positive scalar that
cannot change any argmax). SCRAMBLE CONTROL (fixed-seed TRAIN label permutation, everything
re-fit from scratch -- weights, sup_maps, shard LOO scores) on the wired typer's predict() and
predict_select().

SPLIT: total 50 items, exactly 25 MET/25 UNMET. A single fixed stratified split (SPLIT_SEED,
group-by-gold shuffle, deterministic) sends 10 MET + 10 UNMET to TEST (held out, fixed across
every seed) and the remaining 15 MET + 15 UNMET to TRAIN (also fixed across every seed --
unlike the dialogue scaling cell there is no headroom above n_train for a per-seed subsample
draw at this data size, so N_SEEDS=5 varies ONLY the VSA atom-generation seed passed to
SelectionWeightedShardedTyper(seed=...), testing robustness to the random hyperdimensional
substrate draw with a FIXED train/test membership -- disclosed explicitly, not concealed as a
like-for-like reproduction of the dialogue cell's subsampling design).

PRE-REGISTERED GATE (fixed BEFORE running; anti-premature-HARD_FAIL -- brain is the existence
proof narrative goal-tracking is achievable, so any non-pass here is a diagnosis, not a ceiling):
  HARD-PASS: best wired-typer arm (max mean_acc over 5 seeds among {predict, predict_select})
    (a) beats majority (TRAIN-mode floor) by a real margin, (b) STRICTLY beats naive-flat's
    mean_acc, (c) is non-constant per seed (n_distinct_preds > 1 on every seed), AND (d) its
    scramble control collapses (mean_acc_scramble <= SCRAMBLE_BAND=0.60) -> the role-sharded
    selection mechanism GENERALIZES to a second, structurally different construction.
  PARTIAL: wired typer ties naive-flat/attention-flat (within TIE_BAND=0.02) or beats majority
    but not naive-flat -> sharding is not decisively additive on THIS construction/scale; report
    which role carried the signal regardless.
  FAIL/BELOW: at or below baselines, OR scramble does not collapse -> diagnose honestly per the
    task brief's own checklist (re-labeling quality? wrong features/role-map for narrative? is
    goal-outcome genuinely harder here -- needs discourse/consequence tracking a surface-cue
    bundle cannot supply?) -- NOT declared a capability ceiling.
SCRAMBLE_BAND=0.60, TIE_BAND=0.02 (both reused verbatim from the dialogue cells' own
pre-declared, not-tuned-to-outcome bands).

COMPUTE: n=50 items, N_DIM=1024 FHRR complex64 (SelectionWeightedShardedTyper's own default),
5 seeds x 2 typer instances (real-role-map + single-role-map) x {real, scramble} = 20 fit+predict
units, closed-form dense-tensor ops, no training loop -- sub-few-seconds wall time on this
codebase's own comparable cells. Per tools/exp_checkpoint.py multi-unit convention (units.jsonl
shard, resume-safe). LOCAL-ONLY, foreground-to-completion; NO queue, NO push, NO remote-persist,
NO hdlab mutation (SelectionWeightedShardedTyper is READ, not written -- this cell tests the
already-wired organ, doesn't touch it). Deterministic: OMP/MKL/OPENBLAS_NUM_THREADS=1, fixed-int
SPLIT_SEED / SCRAMBLE_SEED, torch.Generator(seed) passed explicitly to every typer.fit() call
(the class's own documented convention -- no implicit global RNG state).
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

import torch

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ANCHOR_NAME = "narrative_goal_outcome_role_sharded_generality_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.selection_weighted_sharded_typer import SelectionWeightedShardedTyper  # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
DATA_PATH = os.path.join(REPO_ROOT, "experiments", "data",
                          "narrative_goal_outcome_rocstories_relabeled_v1.jsonl")

# ---- Pre-registered config / gate (see module docstring) ----
N_DIM = 1024
N_SEEDS = 5
SEED_BASE = 900000            # typer seed = SEED_BASE + seed_idx (VSA atom draw only)
SPLIT_SEED = 240817            # fixed int, NOT hash()-derived
SCRAMBLE_SEED = 461311          # fixed int, NOT hash()-derived (distinct from the dialogue cells')
N_TEST_PER_CLASS = 10
SCRAMBLE_BAND = 0.60
TIE_BAND = 0.02
EPS = 1e-9

LABELS = ["MET", "UNMET"]

# ========================================================================================
# Data loading
# ========================================================================================
def load_items():
    items = []
    with open(DATA_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def stratified_split(items, seed=SPLIT_SEED, n_test_per_class=N_TEST_PER_CLASS):
    """Groups items by gold, seeded-shuffles each group, sends the first n_test_per_class of
    each group to TEST and the rest to TRAIN. Deterministic, fixed once (no per-seed re-split --
    see module docstring)."""
    by_class = {}
    for it in items:
        by_class.setdefault(it["gold"], []).append(it)
    rng = random.Random(seed)
    test, train = [], []
    for cls in sorted(by_class):
        group = list(by_class[cls])
        rng.shuffle(group)
        test.extend(group[:n_test_per_class])
        train.extend(group[n_test_per_class:])
    return train, test


# ========================================================================================
# GLASS-BOX FEATURE EXTRACTION (narrative goal-outcome; see module docstring for the role map)
# ========================================================================================
def _toks(text):
    return re.findall(r"[a-z']+", text.lower())


GOAL_MARKER_PATTERNS = [
    ("want", re.compile(r"\bwant(?:s|ed|ing)?\b")),
    ("wish", re.compile(r"\bwish(?:es|ed|ing)?\b")),
    ("hope", re.compile(r"\bhop(?:e|es|ed|ing)\b")),
    ("dream", re.compile(r"\bdream(?:s|ed|ing)?\b")),
    ("decide", re.compile(r"\bdecid(?:e|es|ed|ing)\b")),
    ("need", re.compile(r"\bneed(?:s|ed|ing)?\b")),
    ("plan", re.compile(r"\bplan(?:s|ned|ning)?\b")),
    ("determined", re.compile(r"\bdetermined\b")),
]

OBSTACLE_CUE_RE = re.compile(
    r"\b(but|however|yet|couldn't|could not|wasn't|was not|didn't have|did not have|"
    r"no money|not good at|hated|no way)\b")

ACHIEVE_VERBS = {
    "won", "win", "wins", "achieve", "achieved", "achieves", "succeed", "succeeded", "succeeds",
    "got", "get", "gets", "found", "find", "finds", "made", "make", "makes", "agreed", "agree",
    "accept", "accepted", "accepts", "grant", "granted", "earn", "earned", "earns", "landed",
    "land", "pass", "passed", "bought", "buy", "buys", "kept", "keep", "loved", "love", "loves",
    "welcome", "welcomed", "stuck", "recruited", "recruit",
}
FAIL_VERBS = {
    "lost", "lose", "loses", "broke", "break", "breaks", "broken", "ruin", "ruined", "ruins",
    "fail", "failed", "fails", "cancel", "cancelled", "canceled", "stole", "stolen", "steal",
    "declin", "declined", "refus", "refused", "dropped", "drop", "miss", "missed", "block",
    "blocked", "quit", "forgot", "forget", "vomited", "cried",
}
MODAL_FAILURE_RE = re.compile(
    r"\b(couldn't|could not|wasn't able|was not able|unable to|didn't|did not|never again)\b")
NEGATION_RE = re.compile(r"\b(not|never|no|n't)\b")

POS_RESULT_ADJ = {"great", "wonderful", "best", "successful", "perfect", "excellent", "lovely",
                   "thrilled", "double blessed", "good"}
NEG_RESULT_ADJ = {"ruined", "broken", "terrible", "raw", "frumpy", "awful", "disappointing",
                   "sad", "dumb", "unfortunately"}

POS_AFFECT = {"happy", "glad", "thrilled", "excited", "proud", "joy", "grateful", "delighted",
              "ecstatic", "loved"}
NEG_AFFECT = {"upset", "sad", "disappointed", "devastated", "cried", "crying", "embarrassed",
              "dumb", "angry", "furious", "ashamed", "annoyed", "shocked"}


def extract_features(item):
    goal_text = item["goal_text"]
    outcome_text = item["outcome_text"]
    full_text = item["text"]

    goal_lower = goal_text.lower()
    outcome_lower = outcome_text.lower()
    outcome_toks = set(_toks(outcome_text))
    full_toks = _toks(full_text)

    goal_marker_type = "none"
    for name, pat in GOAL_MARKER_PATTERNS:
        if pat.search(goal_lower):
            goal_marker_type = name
            break

    n_words = len(full_toks)
    len_bucket = "short" if n_words <= 25 else ("medium" if n_words <= 40 else "long")
    n_sents = full_text.count(".") + full_text.count("!") + full_text.count("?")
    sent_bucket = "short" if n_sents <= 4 else ("medium" if n_sents == 5 else "long")

    feats = {
        # ---- GOAL ----
        "goal_marker_type": goal_marker_type,
        "goal_marker_present": goal_marker_type != "none",
        "obstacle_cue_present": bool(OBSTACLE_CUE_RE.search(goal_lower)),
        # ---- OUTCOME_POLARITY ----
        "achieve_verb_present": bool(outcome_toks & ACHIEVE_VERBS),
        "fail_verb_present": bool(outcome_toks & FAIL_VERBS),
        "negation_present": bool(NEGATION_RE.search(outcome_lower)),
        "modal_failure_present": bool(MODAL_FAILURE_RE.search(outcome_lower)),
        "result_state_polarity": (
            "positive" if any(a in outcome_lower for a in POS_RESULT_ADJ) and
                          not any(a in outcome_lower for a in NEG_RESULT_ADJ)
            else "negative" if any(a in outcome_lower for a in NEG_RESULT_ADJ)
            else "none"),
        # ---- AFFECT_REACTION ----
        "positive_affect_present": bool(outcome_toks & POS_AFFECT),
        "negative_affect_present": bool(outcome_toks & NEG_AFFECT),
        # ---- FILLER ----
        "narrator_person": "first" if ("i" in full_toks or "my" in full_toks) else "third",
        "has_dialogue_quote": ('"' in full_text) or ("“" in full_text),
        "exclamation_present": "!" in full_text,
        "text_len_bucket": len_bucket,
        "sentence_count_bucket": sent_bucket,
    }
    return feats


def feat_fn(item):
    """PRESENCE-ONLY boolean encoding ('name=True' only when the cue fires) + CATEGORICAL
    always-emit encoding for small-vocabulary dimensional features -- the SAME convention as
    experiments.exp_pragmatic_curriculum_dialogue_request_response_first_test_v1.feat_fn."""
    f = item["_features"]
    out = []
    for name, val in f.items():
        if isinstance(val, bool):
            if val:
                out.append("%s=True" % name)
        else:
            out.append("%s=%s" % (name, val))
    return out


def build_episodes(items):
    out = []
    for it in items:
        it = dict(it)
        it["_features"] = extract_features(it)
        out.append(it)
    return out


# ========================================================================================
# ROLE MAP (narrative-specific -- see module docstring). Every feat_fn cue FAMILY must appear
# exactly once; coverage verified by assert_full_role_coverage (instrumentation self-test).
# ========================================================================================
ROLE_GOAL = "GOAL"
ROLE_OUTCOME_POLARITY = "OUTCOME_POLARITY"
ROLE_AFFECT_REACTION = "AFFECT_REACTION"
ROLE_FILLER = "FILLER"
ROLES = [ROLE_GOAL, ROLE_OUTCOME_POLARITY, ROLE_AFFECT_REACTION, ROLE_FILLER]

FAMILY_ROLE = {
    "goal_marker_type": ROLE_GOAL,
    "goal_marker_present": ROLE_GOAL,
    "obstacle_cue_present": ROLE_GOAL,
    "achieve_verb_present": ROLE_OUTCOME_POLARITY,
    "fail_verb_present": ROLE_OUTCOME_POLARITY,
    "negation_present": ROLE_OUTCOME_POLARITY,
    "modal_failure_present": ROLE_OUTCOME_POLARITY,
    "result_state_polarity": ROLE_OUTCOME_POLARITY,
    "positive_affect_present": ROLE_AFFECT_REACTION,
    "negative_affect_present": ROLE_AFFECT_REACTION,
    "narrator_person": ROLE_FILLER,
    "has_dialogue_quote": ROLE_FILLER,
    "exclamation_present": ROLE_FILLER,
    "text_len_bucket": ROLE_FILLER,
    "sentence_count_bucket": ROLE_FILLER,
}
ROLE_MAP_REPORT = {r: sorted(fam for fam, rr in FAMILY_ROLE.items() if rr == r) for r in ROLES}


def cue_family(term):
    return term.split("=", 1)[0]


def role_of_term(term):
    fam = cue_family(term)
    role = FAMILY_ROLE.get(fam)
    if role is None:
        raise KeyError("UNASSIGNED cue family %r (term=%r) -- role map coverage gap" % (fam, term))
    return role


def role_of_term_single(term):
    """Degenerate single-shard role map: every term -> 'ALL'. Fitting a
    SelectionWeightedShardedTyper with this role map and roles=['ALL'] reduces predict() to an
    UNWEIGHTED flat superposition (naive-flat baseline) and predict_composed() to a cue-
    discriminativeness-weighted flat superposition (attention-flat baseline) exactly -- a single
    shard's own weight is a positive scalar multiplying every label's score identically, so it
    cannot change any argmax. Reuses the SAME class/code path as the real role-sharded arms, so
    feature encoding is byte-identical by construction -- zero risk of an encoding-drift
    confound between the wired-typer arms and these baselines."""
    return "ALL"


def assert_full_role_coverage(vocab_terms):
    missing = [t for t in vocab_terms if cue_family(t) not in FAMILY_ROLE]
    if missing:
        raise AssertionError("INSTRUMENTATION_SUSPECT: %d vocab term(s) have no role assignment: %r"
                              % (len(missing), missing))


# ========================================================================================
# Baselines / helpers
# ========================================================================================
def majority_class(items):
    c = Counter(it["gold"] for it in items)
    return c.most_common(1)[0][0] if c else None


def accuracy(preds, gold):
    if not gold:
        return None
    return sum(1 for p, g in zip(preds, gold) if p == g) / len(gold)


def _digest(preds_seq):
    return hashlib.sha256(json.dumps(list(preds_seq)).encode()).hexdigest()[:16]


def scramble_train_labels(train, seed=SCRAMBLE_SEED):
    rng = random.Random(seed)
    labels = [it["gold"] for it in train]
    shuffled = list(labels)
    rng.shuffle(shuffled)
    if shuffled == labels:
        shuffled = shuffled[::-1]
    out = []
    for it, lbl in zip(train, shuffled):
        new_it = dict(it)
        new_it["gold"] = lbl
        out.append(new_it)
    return out


def fit_typer(train_eps, test_eps, seed, single_shard=False):
    """Fits ONE SelectionWeightedShardedTyper on train_eps; vocab_terms includes TEST-side terms
    too (this codebase's own VSA_BASE convention: build vocab atoms once over the whole corpus,
    so predict-time never silently drops an unseen-at-train term with an atom that simply
    doesn't exist -- OOV terms are still skipped honestly at predict-time by the class itself,
    this only pre-registers their atoms)."""
    train_terms = [feat_fn(it) for it in train_eps]
    test_terms = [feat_fn(it) for it in test_eps]
    vocab_terms = sorted({t for terms in (train_terms + test_terms) for t in terms})
    assert_full_role_coverage(vocab_terms)
    gold = [it["gold"] for it in train_eps]
    rmap = role_of_term_single if single_shard else role_of_term
    roles = ["ALL"] if single_shard else ROLES
    typer = SelectionWeightedShardedTyper(n_dim=N_DIM, seed=seed)
    typer.fit(train_terms, gold, rmap, roles=roles, vocab_terms=vocab_terms)
    return typer, train_terms, test_terms


# ========================================================================================
# Per-unit (arm, seed, real|scramble) computation -- checkpointed (tools/exp_checkpoint.py)
# ========================================================================================
ARM_KEYS_WIRED = ["role_shard_weighted", "role_shard_select", "role_shard_weighted_composed"]
ARM_KEYS_BASELINE = ["naive_flat", "attention_flat"]
ARM_KEYS = ARM_KEYS_WIRED + ARM_KEYS_BASELINE


def compute_unit(train_eps, test_eps, seed, scrambled):
    """Fits both typer instances (real role map + single-shard) once and reads off every arm's
    prediction for this (seed, real|scramble) unit -- avoids re-fitting per arm."""
    train_use = scramble_train_labels(train_eps) if scrambled else train_eps
    typer_real, _tr_terms, test_terms = fit_typer(train_use, test_eps, seed, single_shard=False)
    typer_flat, _tr_terms2, _test_terms2 = fit_typer(train_use, test_eps, seed, single_shard=True)

    gold = [it["gold"] for it in test_eps]
    preds = {
        "role_shard_weighted": [typer_real.predict(t) for t in test_terms],
        "role_shard_select": [typer_real.predict_select(t) for t in test_terms],
        "role_shard_weighted_composed": [typer_real.predict_composed(t) for t in test_terms],
        "naive_flat": [typer_flat.predict(t) for t in test_terms],
        "attention_flat": [typer_flat.predict_composed(t) for t in test_terms],
    }
    out = {}
    for arm, arm_preds in preds.items():
        out[arm] = {
            "acc": accuracy(arm_preds, gold),
            "preds": arm_preds,
            "n_distinct_preds": len(set(arm_preds)),
            "digest": _digest(arm_preds),
        }
    out["_selected_role"] = typer_real.selected_role_
    out["_shard_loo_acc"] = dict(typer_real.shard_loo_acc_)
    out["_shard_weights"] = dict(typer_real.shard_weights_)
    out["_shard_weights_used_fallback"] = bool(typer_real.shard_weights_used_fallback_)
    return out


# ========================================================================================
# Instrumentation self-test (data-independent formula checks + role-coverage + split sanity)
# ========================================================================================
def _instrumentation_selftest():
    items = load_items()
    assert len(items) == 50, "expected 50 items, got %d" % len(items)
    n_met = sum(1 for it in items if it["gold"] == "MET")
    n_unmet = sum(1 for it in items if it["gold"] == "UNMET")
    assert n_met == 25 and n_unmet == 25, (n_met, n_unmet)

    train, test = stratified_split(items)
    assert len(train) == 30 and len(test) == 20, (len(train), len(test))
    assert sum(1 for it in train if it["gold"] == "MET") == 15
    assert sum(1 for it in train if it["gold"] == "UNMET") == 15
    assert sum(1 for it in test if it["gold"] == "MET") == 10
    assert sum(1 for it in test if it["gold"] == "UNMET") == 10
    train_ids = {it["id"] for it in train}
    test_ids = {it["id"] for it in test}
    assert not (train_ids & test_ids), "train/test overlap!"
    assert train_ids | test_ids == {it["id"] for it in items}

    train_eps = build_episodes(train)
    test_eps = build_episodes(test)
    train_terms = [feat_fn(it) for it in train_eps]
    test_terms = [feat_fn(it) for it in test_eps]
    vocab_terms = sorted({t for terms in (train_terms + test_terms) for t in terms})
    assert_full_role_coverage(vocab_terms)  # raises on any coverage gap
    for r in ROLES:
        assert ROLE_MAP_REPORT[r], "role %r has zero assigned cue families" % r

    # scramble determinism / non-identity
    scr = scramble_train_labels(train_eps)
    assert [it["gold"] for it in scr] != [it["gold"] for it in train_eps]
    scr2 = scramble_train_labels(train_eps)
    assert [it["gold"] for it in scr] == [it["gold"] for it in scr2], "scramble not deterministic"

    # determinism: same seed -> identical typer fit + predictions
    t1, _tr1, te1 = fit_typer(train_eps, test_eps, seed=SEED_BASE, single_shard=False)
    t2, _tr2, te2 = fit_typer(train_eps, test_eps, seed=SEED_BASE, single_shard=False)
    p1 = [t1.predict(x) for x in te1]
    p2 = [t2.predict(x) for x in te2]
    assert p1 == p2, "predict() not deterministic given the same seed"
    assert t1.shard_loo_acc_ == t2.shard_loo_acc_

    # single-shard reduction sanity: only one role present
    t_flat, _tr3, te3 = fit_typer(train_eps, test_eps, seed=SEED_BASE, single_shard=True)
    assert t_flat.roles_ == ["ALL"]

    return {"n_items": len(items), "n_train": len(train), "n_test": len(test),
            "role_map": ROLE_MAP_REPORT}


_INSTRUMENTATION = _instrumentation_selftest()


# ========================================================================================
# Main pipeline
# ========================================================================================
def run_pipeline(run_mode="full"):
    t0 = time.time()
    items = load_items()
    train_raw, test_raw = stratified_split(items)
    train_eps = build_episodes(train_raw)
    test_eps = build_episodes(test_raw)
    gold_test = [it["gold"] for it in test_eps]

    majority = majority_class(train_eps)
    majority_preds = [majority] * len(test_eps)
    majority_acc = accuracy(majority_preds, gold_test)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    done = completed_units(OUTPUT_DIR)

    n_seeds = 2 if run_mode == "self_test" else N_SEEDS
    for seed_idx in range(n_seeds):
        seed = SEED_BASE + seed_idx
        for scrambled in (False, True):
            key = unit_key("main", seed_idx, "scr" if scrambled else "real")
            if key in done:
                continue
            result = compute_unit(train_eps, test_eps, seed, scrambled)
            record_unit(OUTPUT_DIR, key, {"seed_idx": seed_idx, "scrambled": scrambled,
                                           "result": result})

    units = load_units(OUTPUT_DIR)
    by_seed = {}
    for rec in units.values():
        if rec["seed_idx"] >= n_seeds:
            continue
        by_seed.setdefault(rec["seed_idx"], {})[rec["scrambled"]] = rec["result"]

    def agg(scrambled):
        out = {}
        for arm in ARM_KEYS:
            accs = [by_seed[s][scrambled][arm]["acc"] for s in sorted(by_seed) if scrambled in by_seed[s]]
            n_distinct = [by_seed[s][scrambled][arm]["n_distinct_preds"] for s in sorted(by_seed) if scrambled in by_seed[s]]
            digests = [by_seed[s][scrambled][arm]["digest"] for s in sorted(by_seed) if scrambled in by_seed[s]]
            mean_acc = sum(accs) / len(accs) if accs else None
            std_acc = (sum((a - mean_acc) ** 2 for a in accs) / len(accs)) ** 0.5 if accs else None
            out[arm] = {"mean_acc": mean_acc, "std_acc": std_acc, "accs": accs,
                        "n_distinct_preds": n_distinct, "digests": digests}
        return out

    results_real = agg(False)
    results_scramble = agg(True)

    shard_loo_by_seed = {s: by_seed[s][False]["_shard_loo_acc"] for s in sorted(by_seed) if False in by_seed[s]}
    shard_loo_mean = {r: sum(shard_loo_by_seed[s][r] for s in shard_loo_by_seed) / len(shard_loo_by_seed)
                       for r in ROLES}
    shard_weights_by_seed = {s: by_seed[s][False]["_shard_weights"] for s in sorted(by_seed) if False in by_seed[s]}
    shard_weights_mean = {r: sum(shard_weights_by_seed[s][r] for s in shard_weights_by_seed) / len(shard_weights_by_seed)
                           for r in ROLES}
    selected_roles = [by_seed[s][False]["_selected_role"] for s in sorted(by_seed) if False in by_seed[s]]

    # ---- pre-registered gate ----
    best_wired_arm = max(("role_shard_weighted", "role_shard_select"),
                          key=lambda a: results_real[a]["mean_acc"])
    best_acc = results_real[best_wired_arm]["mean_acc"]
    naive_acc = results_real["naive_flat"]["mean_acc"]
    attn_acc = results_real["attention_flat"]["mean_acc"]
    non_constant = all(n > 1 for n in results_real[best_wired_arm]["n_distinct_preds"])
    scramble_acc = results_scramble[best_wired_arm]["mean_acc"]
    scramble_collapses = scramble_acc <= SCRAMBLE_BAND

    beats_majority = best_acc > majority_acc + EPS
    beats_naive = best_acc > naive_acc + EPS

    if beats_majority and beats_naive and non_constant and scramble_collapses:
        verdict = "HARD_PASS"
        verdict_msg = ("%s mean_acc=%.4f beats majority=%.4f AND naive_flat=%.4f, non-constant, "
                       "scramble collapses to %.4f (<=%.2f) -- role-sharded selection GENERALIZES "
                       "to narrative goal-outcome." % (best_wired_arm, best_acc, majority_acc,
                                                        naive_acc, scramble_acc, SCRAMBLE_BAND))
    elif best_acc >= max(naive_acc, attn_acc) - TIE_BAND and beats_majority:
        verdict = "PARTIAL_TIE"
        verdict_msg = ("%s mean_acc=%.4f ties naive_flat=%.4f/attention_flat=%.4f (within "
                       "TIE_BAND=%.2f) -- sharding not decisively additive on this construction/"
                       "scale; simplest sufficient baseline wins Occam." % (best_wired_arm,
                       best_acc, naive_acc, attn_acc, TIE_BAND))
    else:
        verdict = "BELOW_BASELINE"
        verdict_msg = ("%s mean_acc=%.4f does NOT clear majority=%.4f and/or naive_flat=%.4f "
                       "(scramble_collapses=%s) -- diagnose (labeling/features/role-map/genuine "
                       "difficulty), not a ceiling." % (best_wired_arm, best_acc, majority_acc,
                                                          naive_acc, scramble_collapses))

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": "%s: best_wired_arm=%s mean_acc=%.4f" % (verdict, best_wired_arm, best_acc),
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "n_items": len(items), "n_train": len(train_eps), "n_test": len(test_eps),
        "majority_class": majority, "majority_acc": majority_acc,
        "results_real": results_real, "results_scramble": results_scramble,
        "role_map": ROLE_MAP_REPORT,
        "shard_loo_acc_mean_over_seeds": shard_loo_mean,
        "shard_weights_mean_over_seeds": shard_weights_mean,
        "selected_role_per_seed": selected_roles,
        "best_wired_arm": best_wired_arm, "best_wired_mean_acc": best_acc,
        "beats_majority": beats_majority, "beats_naive_flat": beats_naive,
        "non_constant": non_constant, "scramble_collapses": scramble_collapses,
        "gate": {"SCRAMBLE_BAND": SCRAMBLE_BAND, "TIE_BAND": TIE_BAND},
        "seeds_used": sorted(by_seed.keys()),
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
    ok = ok and all(n > 1 for n in metrics["results_real"]["role_shard_weighted"]["n_distinct_preds"])
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
    print("---- results (mean/std over %d seeds), real vs scramble ----" % len(metrics["seeds_used"]))
    for arm in ARM_KEYS:
        r = metrics["results_real"][arm]
        s = metrics["results_scramble"][arm]
        print("%32s  real mean=%.4f std=%.4f  |  scramble mean=%.4f std=%.4f"
              % (arm, r["mean_acc"], r["std_acc"], s["mean_acc"], s["std_acc"]))
    print("---- majority baseline: %.4f (class=%s) ----" % (metrics["majority_acc"], metrics["majority_class"]))
    print("---- per-role TRAIN LOO accuracy (mean over seeds) ----")
    print(json.dumps(metrics["shard_loo_acc_mean_over_seeds"], indent=2))
    print("---- per-role shard weights (mean over seeds) ----")
    print(json.dumps(metrics["shard_weights_mean_over_seeds"], indent=2))
    print("---- selected role per seed (predict_select route) ----")
    print(metrics["selected_role_per_seed"])


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, exc)
        traceback.print_exc()
        sys.exit(1)
