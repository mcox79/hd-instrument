# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; predicted-TYPE sequence hash across
#   GOVERNOR/BOW/PER_FORM/SCRAMBLED arms + theta digest vs RANDOM theta)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no swept capacity dimension; classification accuracy discriminator only
# - baseline_in_band: n/a (differential-grounding accuracy cell, not a cleanup-capacity sweep)
# - discriminator survives scale: full-N == smoke-N item sets; only theta-training steps differ
# - cardinality_ok: EXPECTED_N_SEEDS=5; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if fewer land
# - per-unit failure-class instrumentation (no bare except; per-seed crash recorded)
# - calibration_check: default_ok_for_this_regime (bands from the 0.50-by-construction per-form-
#   table floor + chance=0.50 sign discriminator, set BEFORE running)
# - deterministic_seeding: torch.Generator + random.Random per seed; hashlib not builtin hash()
# - cell_chunked: true (per-seed unit via tools/exp_checkpoint.py)
# - all reported numbers MEASURED@ tagged in the completion report, not this file
"""BRIDGE-1 = context-conditioned GROUNDING: an EARNED, glass-box map from (target word, sentence
context) -> the FROZEN appraisal-sim's input dims (congruence HURT/HELP/NEUTRAL, coping HIGH/LOW),
signaled by the SYNTACTIC GOVERNOR (nearest verb) / adjacent-adjective-modifier + Component-3 frame
(reused hdlab.thematic_role_labeler.frame_slot_role) -- NOT bag-of-words co-occurrence. Judged by
DOWNSTREAM DIFFERENTIAL GROUNDING on collision pairs (studied-hard->non-harm vs hit-hard->harm) with
DISJOINT TRAIN/TEST governor+adjective vocabulary (no lexical leakage). Reuses the appraisal-sim's
FROZEN earned theta (experiments/exp_grounded_appraisal_sim_earned_v1.py) as the valuation spoke: a
predicted TYPE -> (cong, cope) -> the sim's own phi() encoding -> theta forward pass -> VALENCE =
Q(harm@coherent) - Q(help@coherent). See preregs/2026-08-05_bridge1_governor_grounding_v1.md.
Per notes/PLAN_grounded_semantic_organ_build.md FOUNDATION + notes/brain_fidelity_vet_components.md.
"""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import random
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

ANCHOR_NAME = "bridge1_governor_grounding_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402
from hdlab.thematic_role_labeler import (  # noqa: E402
    train_perceptron, scramble_weights, frame_slot_role, lemma_verb,
)
import experiments.exp_grounded_appraisal_sim_earned_v1 as sim  # noqa: E402 (REUSE: frozen sim)

SEEDS = [0, 1, 2, 3, 4]
EXPECTED_N_SEEDS = len(SEEDS)
FULL_N_TRAIN_THETA = 8000
SMOKE_N_TRAIN_THETA = 4000

# ------------------------------------------------------------------------- SUPPLIED seed knowledge
# Disjoint TRAIN/TEST governor+adjective vocab pools (the no-lexical-leakage discipline applied to
# the GOVERNOR word, not just the target word).
TRAIN_HARM_VERBS = ["hit", "strike", "kick", "punch"]
TRAIN_HELP_VERBS = ["help", "save", "protect"]
TRAIN_NEUTRAL_VERBS = ["study", "read", "carry", "walk", "build", "sing", "paint", "write"]
TEST_HARM_VERBS = ["wound", "attack", "beat", "stab", "shove", "slap"]
TEST_HELP_VERBS = ["heal", "rescue", "comfort", "aid", "soothe"]
TEST_NEUTRAL_VERBS = ["watch", "cook", "climb", "practice", "travel", "know", "collect", "wear"]

TRAIN_HARM_ADJ = ["cruel", "harsh"]
TRAIN_HELP_ADJ = ["kind", "gentle"]
TEST_HARM_ADJ = ["vicious", "brutal", "nasty", "spiteful"]
TEST_HELP_ADJ = ["generous", "caring", "helpful", "tender"]

LOW_COPE_CUES = {"exhausted", "overwhelmed", "helpless", "unable", "outmatched", "defenseless",
                  "drained", "weary"}

GOVERNOR_VERB_CLASS = {}
for _w in TRAIN_HARM_VERBS + TEST_HARM_VERBS:
    GOVERNOR_VERB_CLASS[_w] = "HARM"
for _w in TRAIN_HELP_VERBS + TEST_HELP_VERBS:
    GOVERNOR_VERB_CLASS[_w] = "HELP"
for _w in TRAIN_NEUTRAL_VERBS + TEST_NEUTRAL_VERBS:
    GOVERNOR_VERB_CLASS[_w] = "NEUTRAL"

ADJ_MODIFIER_CLASS = {}
for _w in TRAIN_HARM_ADJ + TEST_HARM_ADJ:
    ADJ_MODIFIER_CLASS[_w] = "HARM"
for _w in TRAIN_HELP_ADJ + TEST_HELP_ADJ:
    ADJ_MODIFIER_CLASS[_w] = "HELP"

GENERIC_TRAIN_NOUNS = ["matter", "request", "letter", "situation", "case", "issue", "task",
                        "problem", "proposal", "plan", "report", "message", "project", "idea",
                        "document"]


def _scrambled_class_dict(d: dict, seed: int) -> dict:
    """META_RULE-style scramble control: permute VALUES across keys (hashlib-seeded, not hash())."""
    keys_sorted = sorted(d.keys())
    vals_sorted = [d[k] for k in keys_sorted]
    rng = random.Random(seed)
    permuted = vals_sorted[:]
    rng.shuffle(permuted)
    return dict(zip(keys_sorted, permuted))


# ------------------------------------------------------------------------- governor/adjmod extraction
def nearest_verb_idx(tokens, pos, target_idx):
    for i in range(target_idx - 1, -1, -1):
        if pos[i] == "VERB":
            return i
    return -1


def adjmod_idx(tokens, pos, target_idx):
    """Adjective immediately before the target, skipping a single intervening DET (a/the)."""
    for i in range(target_idx - 1, max(-1, target_idx - 3), -1):
        if pos[i] == "ADJ":
            return i
        if pos[i] != "DET":
            break
    return -1


def cope_cue(tokens):
    return "LOW" if any(t.lower() in LOW_COPE_CUES for t in tokens) else "HIGH"


def extract_governor_feats(tokens, pos, target_idx, verb_class_dict, adj_class_dict):
    """Governor/adjective-modifier + Component-3 frame + cope + order feature list.
    NEVER includes the target word string or raw governor token identity -- only its CLASS."""
    gi = nearest_verb_idx(tokens, pos, target_idx)
    ai = adjmod_idx(tokens, pos, target_idx)
    gov_word = lemma_verb(tokens[gi]) if gi >= 0 else None
    adj_word = tokens[ai] if ai >= 0 else None
    gclass = verb_class_dict.get(gov_word, "UNK") if gov_word else "UNK"
    aclass = adj_class_dict.get(adj_word, "UNK") if adj_word else "UNK"
    frame = frame_slot_role(gov_word, "subj") if gov_word else "none"
    cope = cope_cue(tokens)
    order = "pre" if 0 <= gi < target_idx else ("post" if gi >= 0 else "none")
    feats = [f"gov_class:{gclass}", f"adj_class:{aclass}", f"frame:{frame}",
              f"cope_cue:{cope}", f"order:{order}", "BIAS"]
    return feats, gov_word, adj_word, gclass, aclass, cope


def gold_type_from_classes(gclass, aclass, cope):
    cls = gclass if gclass != "UNK" else aclass
    if cls == "HARM":
        return "BLOCK_HIGH" if cope == "HIGH" else "BLOCK_LOW"
    if cls == "HELP":
        return "RECIPROCITY"
    return "NEUTRAL"


def bow_feats(tokens, target_word):
    return [f"bow:{t.lower()}" for t in tokens if t.lower() != target_word.lower()] + ["BIAS"]


# ------------------------------------------------------------------------- dataset construction
def mk_item(tokens, pos, target_idx, target_word, note=""):
    feats, gov, adj, gclass, aclass, cope = extract_governor_feats(
        tokens, pos, target_idx, GOVERNOR_VERB_CLASS, ADJ_MODIFIER_CLASS)
    gold = gold_type_from_classes(gclass, aclass, cope)
    return {"tokens": tokens, "pos": pos, "target_idx": target_idx, "target_word": target_word,
            "gold_type": gold, "note": note}


def build_train_items():
    items = []
    for v in TRAIN_HARM_VERBS:
        for n in GENERIC_TRAIN_NOUNS[:6]:
            items.append(mk_item(["she", v, "the", n], ["PRON", "VERB", "DET", "NOUN"], 3, n))
            items.append(mk_item(["she", "was", "exhausted", "and", v, "the", n],
                                  ["PRON", "AUX", "ADJ", "CCONJ", "VERB", "DET", "NOUN"], 6, n))
    for v in TRAIN_HELP_VERBS:
        for n in GENERIC_TRAIN_NOUNS[:6]:
            items.append(mk_item(["she", v, "the", n], ["PRON", "VERB", "DET", "NOUN"], 3, n))
    for v in TRAIN_NEUTRAL_VERBS:
        for n in GENERIC_TRAIN_NOUNS[:6]:
            items.append(mk_item(["she", v, "the", n], ["PRON", "VERB", "DET", "NOUN"], 3, n))
    for a in TRAIN_HARM_ADJ:
        for n in GENERIC_TRAIN_NOUNS[:5]:
            items.append(mk_item(["it", "was", "a", a, n], ["PRON", "AUX", "DET", "ADJ", "NOUN"], 4, n))
    for a in TRAIN_HELP_ADJ:
        for n in GENERIC_TRAIN_NOUNS[:5]:
            items.append(mk_item(["it", "was", "a", a, n], ["PRON", "AUX", "DET", "ADJ", "NOUN"], 4, n))
    return items


def build_collision_pairs():
    """6 forms x 2 contexts. Gold sign differs within every pair by construction. TEST-pool
    governor/adjective vocab only (disjoint from TRAIN)."""
    pairs = []
    # 1. hard (verb-path both sides)
    pairs.append(("hard",
        mk_item(["she", "practice", "hard", "for", "the", "exam"],
                ["PRON", "VERB", "ADV", "ADP", "DET", "NOUN"], 2, "hard", "hard_A_nonharm"),
        mk_item(["he", "attack", "her", "hard"], ["PRON", "VERB", "PRON", "ADV"], 3, "hard", "hard_B_harm")))
    # 2. trick (verb-path A, adj-path B)
    pairs.append(("trick",
        mk_item(["he", "know", "a", "card", "trick"],
                ["PRON", "VERB", "DET", "NOUN", "NOUN"], 4, "trick", "trick_A_nonharm"),
        mk_item(["that", "was", "a", "vicious", "trick"],
                ["PRON", "AUX", "DET", "ADJ", "NOUN"], 4, "trick", "trick_B_harm")))
    # 3. blow (adj-path both sides)
    pairs.append(("blow",
        mk_item(["it", "was", "a", "generous", "blow"],
                ["PRON", "AUX", "DET", "ADJ", "NOUN"], 4, "blow", "blow_A_nonharm"),
        mk_item(["it", "was", "a", "brutal", "blow"],
                ["PRON", "AUX", "DET", "ADJ", "NOUN"], 4, "blow", "blow_B_harm")))
    # 4. cross (verb-path both sides)
    pairs.append(("cross",
        mk_item(["he", "wear", "a", "cross"], ["PRON", "VERB", "DET", "NOUN"], 3, "cross", "cross_A_nonharm"),
        mk_item(["he", "attack", "her", "near", "the", "cross"],
                ["PRON", "VERB", "PRON", "ADP", "DET", "NOUN"], 5, "cross", "cross_B_harm")))
    # 5. sound (verb-path both sides)
    pairs.append(("sound",
        mk_item(["he", "watch", "a", "sound"], ["PRON", "VERB", "DET", "NOUN"], 3, "sound", "sound_A_nonharm"),
        mk_item(["he", "beat", "out", "a", "sound"],
                ["PRON", "VERB", "ADP", "DET", "NOUN"], 4, "sound", "sound_B_harm")))
    # 6. bear (verb-path both sides)
    pairs.append(("bear",
        mk_item(["he", "comfort", "the", "bear"], ["PRON", "VERB", "DET", "NOUN"], 3, "bear", "bear_A_nonharm"),
        mk_item(["he", "stab", "the", "bear"], ["PRON", "VERB", "DET", "NOUN"], 3, "bear", "bear_B_harm")))
    return pairs


def build_unseen_items():
    """9 items, target NOUNS never used in TRAIN or collision set, single-context, TEST-pool
    governor/adjective vocab -- generalization to unseen target CONCEPTS."""
    items = []
    items.append(mk_item(["he", "shove", "an", "insult"], ["PRON", "VERB", "DET", "NOUN"], 3, "insult"))
    items.append(mk_item(["he", "rescue", "a", "gift"], ["PRON", "VERB", "DET", "NOUN"], 3, "gift"))
    items.append(mk_item(["it", "was", "a", "spiteful", "curse"],
                          ["PRON", "AUX", "DET", "ADJ", "NOUN"], 4, "curse"))
    items.append(mk_item(["he", "climb", "past", "a", "warning"],
                          ["PRON", "VERB", "ADP", "DET", "NOUN"], 4, "warning"))
    items.append(mk_item(["it", "was", "a", "tender", "reward"],
                          ["PRON", "AUX", "DET", "ADJ", "NOUN"], 4, "reward"))
    items.append(mk_item(["he", "slap", "her", "with", "a", "penalty"],
                          ["PRON", "VERB", "PRON", "ADP", "DET", "NOUN"], 5, "penalty"))
    items.append(mk_item(["he", "aid", "her", "with", "a", "favor"],
                          ["PRON", "VERB", "PRON", "ADP", "DET", "NOUN"], 5, "favor"))
    items.append(mk_item(["it", "was", "a", "nasty", "threat"],
                          ["PRON", "AUX", "DET", "ADJ", "NOUN"], 4, "threat"))
    items.append(mk_item(["he", "was", "exhausted", "and", "wound", "the", "warrior"],
                          ["PRON", "AUX", "ADJ", "CCONJ", "VERB", "DET", "NOUN"], 6, "warrior"))
    return items


TRAIN_ITEMS = build_train_items()
COLLISION_PAIRS = build_collision_pairs()
COLLISION_ITEMS = [it for _f, a, b in COLLISION_PAIRS for it in (a, b)]
UNSEEN_ITEMS = build_unseen_items()


# ------------------------------------------------------------------------- valence via frozen theta
def valence_for_type(cb, theta, type_key: str) -> float:
    """Predicted TYPE -> (cong,cope) -> the SIM's own phi() encoding -> theta forward pass.
    VALENCE = Q(harm@coherent-target) - Q(help@coherent-target). Canonical target: coh=1, rec=0."""
    ep = {"type": type_key, "cong": sim.CONG[type_key], "cope": sim.COPE[type_key], "pool": "eval",
          "coh_slot": 0, "rec_slot": 1,
          "cands": [{"id_idx": 0, "coh": 1, "rec": 0},
                    {"id_idx": 1, "coh": 0, "rec": 1},
                    {"id_idx": 2, "coh": 0, "rec": 0}]}
    q_harm = float(sim.phi(cb, ep, sim.A_HARM0 + 0, "FULL") @ theta)
    q_help = float(sim.phi(cb, ep, sim.A_HELP0 + 0, "FULL") @ theta)
    return q_harm - q_help


def gold_sign(type_key: str) -> int:
    """+1 = harm-congruent behavior (theta must prefer harm@coherent over help@coherent).
    MEASURED (not assumed): only BLOCK_HIGH is harm-congruent under the sim's own reward function
    -- BLOCK_LOW's correct action is WITHDRAW (harm is punished -0.5 there too, per reward()), so a
    faithful theta correctly gives BLOCK_LOW a NEGATIVE Q(harm)-Q(help) same as RECIPROCITY/NEUTRAL.
    Confirmed empirically across 8 seeds at n_train_theta>=4000 (sign(BLOCK_HIGH)=+1 and
    sign(BLOCK_LOW/RECIPROCITY/NEUTRAL)=-1, 100% consistent) before this rule was fixed here."""
    return 1 if type_key == "BLOCK_HIGH" else -1


# ------------------------------------------------------------------------- per-seed unit
def run_seed(seed: int, n_train_theta: int) -> dict:
    failure_class = None
    try:
        # (a) frozen sim theta: reuse train_theta() from the appraisal-sim, FULL variant, unmodified.
        gen = torch.Generator().manual_seed(seed)
        cb = sim.Codebook(gen)
        g_theta = torch.Generator().manual_seed(seed * 100 + sim.hash_variant("FULL"))
        theta = sim.train_theta(cb, g_theta, "FULL", n_train_theta)
        g_rand = torch.Generator().manual_seed(seed * 100 + 7)
        theta_random = torch.randn(2 * sim.N_DIM, generator=g_rand, dtype=torch.float32) * 0.01

        # (b) GOVERNOR arm: earned perceptron on governor/adj-class + frame + cope + order feats.
        train_ex = [(extract_governor_feats(it["tokens"], it["pos"], it["target_idx"],
                                             GOVERNOR_VERB_CLASS, ADJ_MODIFIER_CLASS)[0],
                     it["gold_type"]) for it in TRAIN_ITEMS]
        pred_gov, w_gov, roles = train_perceptron(train_ex, seed=seed + 1000, epochs=20,
                                                    roles=sim.TYPES)

        # (c) BAG-OF-WORDS control: same perceptron engine, raw-token feats (disjoint train/test
        #     vocab means the informative tokens are OOV at eval time).
        train_bow = [(bow_feats(it["tokens"], it["target_word"]), it["gold_type"])
                     for it in TRAIN_ITEMS]
        pred_bow, w_bow, _ = train_perceptron(train_bow, seed=seed + 2000, epochs=20, roles=sim.TYPES)

        # (d) SCRAMBLED-GOVERNOR control: broken verb/adj -> class dicts (values permuted).
        scr_verb = _scrambled_class_dict(GOVERNOR_VERB_CLASS, seed=seed + 3000)
        scr_adj = _scrambled_class_dict(ADJ_MODIFIER_CLASS, seed=seed + 3001)
        train_scr = [(extract_governor_feats(it["tokens"], it["pos"], it["target_idx"],
                                              scr_verb, scr_adj)[0], it["gold_type"])
                     for it in TRAIN_ITEMS]
        pred_scr, w_scr, _ = train_perceptron(train_scr, seed=seed + 3002, epochs=20, roles=sim.TYPES)

        def gov_feats(it):
            return extract_governor_feats(it["tokens"], it["pos"], it["target_idx"],
                                           GOVERNOR_VERB_CLASS, ADJ_MODIFIER_CLASS)[0]

        def scr_feats(it):
            return extract_governor_feats(it["tokens"], it["pos"], it["target_idx"],
                                           scr_verb, scr_adj)[0]

        # (e) PER-FORM TABLE control: governor-arm's own prediction on collision context A, applied
        #     UNCHANGED to context B -- context-blind, single entry per FORM.
        per_form_table = {}
        for form, a, b in COLLISION_PAIRS:
            per_form_table[form] = pred_gov(gov_feats(a))

        def eval_arm(items, pred_fn, feat_fn):
            correct = 0
            preds = []
            for it in items:
                p = pred_fn(feat_fn(it))
                preds.append(p)
                v = valence_for_type(cb, theta, p)
                s = 1 if v > 0 else -1
                if s == gold_sign(it["gold_type"]):
                    correct += 1
            return correct / max(1, len(items)), preds

        pooled = COLLISION_ITEMS + UNSEEN_ITEMS
        diff_acc_gov, preds_gov = eval_arm(COLLISION_ITEMS, pred_gov, gov_feats)
        unseen_acc_gov, _ = eval_arm(UNSEEN_ITEMS, pred_gov, gov_feats)
        pooled_acc_gov, pooled_preds_gov = eval_arm(pooled, pred_gov, gov_feats)

        diff_acc_bow, _ = eval_arm(COLLISION_ITEMS, pred_bow, lambda it: bow_feats(it["tokens"], it["target_word"]))
        unseen_acc_bow, _ = eval_arm(UNSEEN_ITEMS, pred_bow, lambda it: bow_feats(it["tokens"], it["target_word"]))
        _, pooled_preds_bow = eval_arm(pooled, pred_bow, lambda it: bow_feats(it["tokens"], it["target_word"]))

        diff_acc_scr, _ = eval_arm(COLLISION_ITEMS, pred_scr, scr_feats)
        unseen_acc_scr, _ = eval_arm(UNSEEN_ITEMS, pred_scr, scr_feats)
        _, pooled_preds_scr = eval_arm(pooled, pred_scr, scr_feats)

        # per-form table: fixed prediction per form, applied to both members of the pair.
        pf_correct = 0
        pooled_preds_pf = []
        for it in COLLISION_ITEMS:
            p = per_form_table[it["target_word"]]
            pooled_preds_pf.append(p)
            v = valence_for_type(cb, theta, p)
            s = 1 if v > 0 else -1
            if s == gold_sign(it["gold_type"]):
                pf_correct += 1
        diff_acc_pf = pf_correct / max(1, len(COLLISION_ITEMS))
        for it in UNSEEN_ITEMS:
            pooled_preds_pf.append("NEUTRAL")  # never-seen form: production default

        # (f) theta witness: VALENCE(BLOCK_HIGH) != VALENCE(BLOCK_LOW) (same cong=HURT, differ cope)
        v_bh = valence_for_type(cb, theta, "BLOCK_HIGH")
        v_bl = valence_for_type(cb, theta, "BLOCK_LOW")
        v_rec = valence_for_type(cb, theta, "RECIPROCITY")
        v_neu = valence_for_type(cb, theta, "NEUTRAL")
        v_bh_random = float(sim.phi(cb, {"type": "BLOCK_HIGH", "cong": "HURT", "cope": "HIGH",
                                          "pool": "eval", "coh_slot": 0, "rec_slot": 1,
                                          "cands": [{"id_idx": 0, "coh": 1, "rec": 0},
                                                    {"id_idx": 1, "coh": 0, "rec": 1},
                                                    {"id_idx": 2, "coh": 0, "rec": 0}]},
                                         sim.A_HARM0, "FULL") @ theta_random)

        digs = {
            "governor": hashlib.sha256(json.dumps(pooled_preds_gov).encode()).hexdigest()[:16],
            "bow": hashlib.sha256(json.dumps(pooled_preds_bow).encode()).hexdigest()[:16],
            "scrambled": hashlib.sha256(json.dumps(pooled_preds_scr).encode()).hexdigest()[:16],
            "per_form": hashlib.sha256(json.dumps(pooled_preds_pf).encode()).hexdigest()[:16],
            "theta_full": hashlib.sha256(theta.numpy().tobytes()).hexdigest()[:16],
            "theta_random": hashlib.sha256(theta_random.numpy().tobytes()).hexdigest()[:16],
        }
        vals = list(digs.values())
        # arms-must-differ: not ALL FOUR prediction arms bit-identical (would indicate a wiring bug)
        pred_digs = [digs["governor"], digs["bow"], digs["scrambled"], digs["per_form"]]
        arms_all_identical = len(set(pred_digs)) == 1

        return {
            "seed": seed,
            "differential_grounding_acc": diff_acc_gov,
            "unseen_concept_acc": unseen_acc_gov,
            "pooled_acc_governor": pooled_acc_gov,
            "bow_control_diff_acc": diff_acc_bow,
            "bow_control_unseen_acc": unseen_acc_bow,
            "scrambled_diff_acc": diff_acc_scr,
            "scrambled_unseen_acc": unseen_acc_scr,
            "per_form_table_diff_acc": diff_acc_pf,
            "theta_witness": {"BLOCK_HIGH": v_bh, "BLOCK_LOW": v_bl, "RECIPROCITY": v_rec,
                               "NEUTRAL": v_neu, "BLOCK_HIGH_random_theta": v_bh_random,
                               "coh_vs_cope_differ": (v_bh != v_bl)},
            "arms_digests": digs,
            "arms_all_identical": arms_all_identical,
            "failure_class": None,
        }
    except Exception as e:
        failure_class = f"{type(e).__name__}: {str(e)[:300]}"
        return {"seed": seed, "failure_class": failure_class, "traceback": traceback.format_exc()[:3000]}


# ------------------------------------------------------------------------- verdict
def aggregate_and_verdict(per_seed: dict) -> dict:
    seeds = sorted(per_seed.keys())
    failed = [s for s in seeds if per_seed[s].get("failure_class")]
    ok_seeds = [s for s in seeds if not per_seed[s].get("failure_class")]

    def mean(key):
        vals = [float(per_seed[s][key]) for s in ok_seeds]
        return sum(vals) / max(1, len(vals))

    n = len(seeds)
    if n < EXPECTED_N_SEEDS or len(ok_seeds) < EXPECTED_N_SEEDS:
        return {
            "verdict": "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
            "verdict_msg": f"landed {n} seeds ({len(ok_seeds)} ok, {len(failed)} failed), "
                           f"expected {EXPECTED_N_SEEDS}",
            "summary": "cardinality breach", "n_seeds": n, "n_ok": len(ok_seeds),
            "failed_seeds": failed,
        }

    diff = mean("differential_grounding_acc")
    unseen = mean("unseen_concept_acc")
    bow = mean("bow_control_diff_acc")
    scr = mean("scrambled_diff_acc")
    pf = mean("per_form_table_diff_acc")
    arms_all_identical_any = any(per_seed[s]["arms_all_identical"] for s in ok_seeds)
    coh_cope_differ_all = all(per_seed[s]["theta_witness"]["coh_vs_cope_differ"] for s in ok_seeds)

    hard_pass = (diff >= 0.75 and bow <= 0.60 and unseen >= 0.70
                 and (diff - bow) >= 0.15 and pf <= 0.60 and scr <= 0.60
                 and not arms_all_identical_any and coh_cope_differ_all)
    hard_fail = (diff < 0.60 or abs(diff - bow) < 0.05 or pf >= diff - 0.05)

    if arms_all_identical_any:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif hard_pass:
        verdict = "HARD_PASS"
    elif hard_fail:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    summary = (f"differential_grounding_acc={diff:.3f} unseen_concept_acc={unseen:.3f} "
               f"bow_control={bow:.3f} scrambled={scr:.3f} per_form_table={pf:.3f} "
               f"coh_cope_differ_all_seeds={coh_cope_differ_all}")
    return {
        "verdict": verdict, "verdict_msg": f"{verdict}: {summary}", "summary": summary,
        "n_seeds": n, "n_ok": len(ok_seeds), "failed_seeds": failed,
        "means": {"differential_grounding_acc": diff, "unseen_concept_acc": unseen,
                  "bow_control_diff_acc": bow, "scrambled_diff_acc": scr,
                  "per_form_table_diff_acc": pf},
        "bands": {"hard_pass_criteria_met": hard_pass, "hard_fail_criteria_met": hard_fail,
                  "arms_all_identical_any_seed": arms_all_identical_any,
                  "coh_cope_differ_all_seeds": coh_cope_differ_all},
    }


# ------------------------------------------------------------------------- infra
def out_dir_for(run_mode: str) -> str:
    return OUTPUT_DIR if run_mode == "full" else f"{OUTPUT_DIR}_{run_mode}"


def _write_start_marker(output_dir, run_mode, expected):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected,
              "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, d):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, default=str)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    _write_metrics(output_dir, diag)


def run(n_train_theta, run_mode):
    t0 = time.perf_counter()
    output_dir = out_dir_for(run_mode)
    _write_start_marker(output_dir, run_mode, EXPECTED_N_SEEDS)
    done = completed_units(output_dir)
    for seed in SEEDS:
        k = unit_key("seed", seed)
        if k in done:
            print(f"[resume] seed={seed} already done, skipping", flush=True)
            continue
        ts = time.perf_counter()
        res = run_seed(seed, n_train_theta)
        record_unit(output_dir, k, res)
        if res.get("failure_class"):
            print(f"[FAIL] seed={seed} {res['failure_class']}", flush=True)
        else:
            print(f"[progress] seed={seed} done in {time.perf_counter()-ts:.1f}s "
                  f"diff_grounding={res['differential_grounding_acc']:.3f} "
                  f"bow={res['bow_control_diff_acc']:.3f} unseen={res['unseen_concept_acc']:.3f}",
                  flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(output_dir).values()}
    agg = aggregate_and_verdict(per_seed)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = {"seeds": SEEDS, "n_train_theta": n_train_theta,
                     "n_train_items": len(TRAIN_ITEMS), "n_collision_items": len(COLLISION_ITEMS),
                     "n_collision_pairs": len(COLLISION_PAIRS), "n_unseen_items": len(UNSEEN_ITEMS)}
    agg["per_seed"] = per_seed
    _write_metrics(output_dir, agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.1f}s", flush=True)
    return agg


# ------------------------------------------------------------------------- self-test
def self_test():
    """(1) governor/adjmod extraction sanity on hand-checked examples; (2) gold-label rule
    consistency; (3) TRAIN/TEST governor+adjective vocab pools are disjoint (no leakage); (4) tiny
    run: governor arm beats bow control on collision pairs; (5) per-form table pinned at 0.50 by
    construction; (6) theta witness fires (coping differentiates value at fixed congruence)."""
    # (1) extraction
    toks = ["he", "strike", "her", "hard"]
    pos = ["PRON", "VERB", "PRON", "ADV"]
    gi = nearest_verb_idx(toks, pos, 3)
    assert toks[gi] == "strike", f"governor extraction failed: got {toks[gi]!r}"
    toks2 = ["that", "was", "a", "vicious", "trick"]
    pos2 = ["PRON", "AUX", "DET", "ADJ", "NOUN"]
    ai = adjmod_idx(toks2, pos2, 4)
    assert toks2[ai] == "vicious", f"adjmod extraction failed: got {toks2[ai]!r}"
    gi2 = nearest_verb_idx(toks2, pos2, 4)
    assert gi2 == -1, "AUX 'was' must not be treated as a governing VERB"

    # (2) gold-label rule
    assert gold_type_from_classes("HARM", "UNK", "HIGH") == "BLOCK_HIGH"
    assert gold_type_from_classes("HARM", "UNK", "LOW") == "BLOCK_LOW"
    assert gold_type_from_classes("HELP", "UNK", "HIGH") == "RECIPROCITY"
    assert gold_type_from_classes("UNK", "UNK", "HIGH") == "NEUTRAL"
    assert gold_type_from_classes("UNK", "HARM", "HIGH") == "BLOCK_HIGH", "adj-class fallback failed"

    # (3) disjoint vocab pools (no lexical leakage)
    train_verbs = set(TRAIN_HARM_VERBS + TRAIN_HELP_VERBS + TRAIN_NEUTRAL_VERBS)
    test_verbs = set(TEST_HARM_VERBS + TEST_HELP_VERBS + TEST_NEUTRAL_VERBS)
    assert train_verbs.isdisjoint(test_verbs), "TRAIN/TEST governor verb vocab overlaps"
    train_adj = set(TRAIN_HARM_ADJ + TRAIN_HELP_ADJ)
    test_adj = set(TEST_HARM_ADJ + TEST_HELP_ADJ)
    assert train_adj.isdisjoint(test_adj), "TRAIN/TEST adjective vocab overlaps"
    train_nouns = set(GENERIC_TRAIN_NOUNS)
    coll_nouns = {it["target_word"] for it in COLLISION_ITEMS}
    unseen_nouns = {it["target_word"] for it in UNSEEN_ITEMS}
    assert train_nouns.isdisjoint(coll_nouns), "TRAIN/collision target-word vocab overlaps"
    assert train_nouns.isdisjoint(unseen_nouns), "TRAIN/unseen target-word vocab overlaps"
    assert coll_nouns.isdisjoint(unseen_nouns), "collision/unseen target-word vocab overlaps"
    # every collision item's governor/adj is TEST-pool only
    for it in COLLISION_ITEMS:
        _, gov, adj, gclass, aclass, _cope = extract_governor_feats(
            it["tokens"], it["pos"], it["target_idx"], GOVERNOR_VERB_CLASS, ADJ_MODIFIER_CLASS)
        if gov is not None:
            assert gov not in train_verbs, f"collision item {it['note']} used a TRAIN governor {gov!r}"
        if adj is not None:
            assert adj not in train_adj, f"collision item {it['note']} used a TRAIN adjective {adj!r}"

    # (4)+(5)+(6) tiny end-to-end run
    res = run_seed(0, n_train_theta=SMOKE_N_TRAIN_THETA)
    assert res["failure_class"] is None, f"run_seed crashed: {res.get('failure_class')}"
    assert res["differential_grounding_acc"] > res["bow_control_diff_acc"], (
        f"discriminator did not fire: governor={res['differential_grounding_acc']:.3f} "
        f"bow={res['bow_control_diff_acc']:.3f}")
    assert abs(res["per_form_table_diff_acc"] - 0.50) < 1e-9, (
        f"per-form table not pinned at 0.50 by construction: {res['per_form_table_diff_acc']}")
    assert res["theta_witness"]["coh_vs_cope_differ"], "theta witness: coping did not differentiate value"
    assert not res["arms_all_identical"], "META_RULE_AF: all four arms produced bit-identical predictions"

    print(f"[SELFTEST PASS] diff_grounding={res['differential_grounding_acc']:.3f} "
          f"bow={res['bow_control_diff_acc']:.3f} unseen={res['unseen_concept_acc']:.3f} "
          f"per_form={res['per_form_table_diff_acc']:.3f} "
          f"theta_witness_BH={res['theta_witness']['BLOCK_HIGH']:.4f} "
          f"BL={res['theta_witness']['BLOCK_LOW']:.4f}", flush=True)
    return True


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        ok = self_test()
        raise SystemExit(0 if ok else 1)
    if args.smoke:
        run(SMOKE_N_TRAIN_THETA, "smoke")
        raise SystemExit(0)
    run(FULL_N_TRAIN_THETA, "full")
    raise SystemExit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash(OUTPUT_DIR, e)
        raise
