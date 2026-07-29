"""ORDER-CRITICAL COMPREHENSION INSTRUMENT + CALIBRATION GATE (2026-07-28).

NOT a dispatched cell. No queue, no GPU, no bank/push. Standalone script; run to completion in
the foreground (CPU-only) and read results.json off disk.

WHY THIS EXISTS: tonight's ruler-fix re-measure (diag_ruler_fix_remeasure_v1.py,
data/diag_ruler_fix_remeasure_v1/results.json) found that even a KNOWN capable reader
(sentence-transformers/all-MiniLM-L6-v2, scored with its own native mean-pooled sentence
embedding + a properly class-weighted linear decoder -- the SAME fixed methodology that flipped
our frozen encoder to comprehension_specific=True) does NOT clear the comprehension_specific
margin on eval_battery_relational_cloze_v7's task (margin=-0.026, i.e. scrambled scores
about as well as coherent). Diagnosis: CSKG relation-cloze is CONTENT-CUED -- the relation is
recoverable from the bag of content words regardless of word order, so the task does not
REQUIRE reading order even for a real reader. A comprehension test a known-capable reader
cannot pass is BROKEN; it cannot be used to judge our own encoder.

PRINCIPLE: CALIBRATE FIRST on known readers; iterate construction/readout until a known reader
clearly passes; ONLY THEN score our own encoder. Calibration is the acceptance gate, not an
afterthought.

CONSTRUCTION -- two independent ORDER-CRITICAL item families where swapping word order changes
the ground-truth label while the WORD MULTISET stays IDENTICAL (unlike relation-cloze, where
content words alone give away the answer):

  (1) AGENT_PATIENT_REVERSIBLE -- "the {A} {verb} the {B} ." vs "the {B} {verb} the {A} ."
      Same three content words + verb; label = which entity is the AGENT (subject position).
      A bag-of-words / order-blind reader sees the identical multiset for both sentences of a
      pair and cannot solve it above chance; an order-sensitive reader can.

  (2) ENTITY_STATE_TIME_UPDATE -- "{adv1} the {obj} was {sA} . {adv2} it became {sB} ." vs the
      swapped-order sentence with sA/sB exchanged. Label = which state is the FINAL (current)
      state. Same content words (obj, sA, sB, adv1, adv2); only the temporal ORDER of the two
      state-mentions determines which is current -- a direct order/structure requirement.

Both constructions are held out LEAK-PROOF by construction identity: AGENT_PATIENT splits by
UNORDERED ENTITY PAIR (train pairs never appear, in either order, in eval); ENTITY_STATE splits
by (object, state-pair) COMBO. This forces a probe to generalize the "order/direction" feature
across never-seen lexical fillers, not memorize per-item order shortcuts.

CALIBRATION GATE (the deliverable's core): for each of two cached, offline, DIAGNOSTIC-ONLY
known readers (sentence-transformers/all-MiniLM-L6-v2, BAAI/bge-small-en-v1.5 -- never wired
into the substrate, per standing USER directive against borrowed embeddings as the encoder),
try THREE readouts from ONE frozen forward pass over raw per-token hidden states: MEAN_POOL
(attention-mask-weighted mean, the standard SBERT convention -- NOT naive bag-of-words, since
each token's hidden state is already contextualized by self-attention + position embeddings),
CLS_TOKEN (position-0 hidden state; the BGE-family's own recommended pooling), LAST_TOKEN (final
non-pad hidden state, has attended to the full sequence). A class-balanced linear probe is fit
on TRAIN-only coherent embeddings (never touching eval items or their entity/combo identities)
and scored on EVAL coherent vs EVAL word-scrambled (LOOP2._scramble_words) sentences.
comprehension_specific = (coherent_acc - scrambled_acc) >= MARGIN_THRESH AND coherent_acc clears
a floor AND the TRAIN fit itself beats chance (decoder-collapse sanity gate, the exact bug fixed
in tonight's eval_battery_relational_cloze_v7 commit, applied proactively here).

ONLY IF at least one known reader passes on a construction: score OUR frozen encoders
(data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt "BASELINE",
data/exp_scale_meaning_learn_arc_heldout_v3_relobj/ckpt_seed_7.pt "RELOBJ") on the SAME
construction using the MATCHED readout category (our encoder has no CLS token, so MEAN_POOL /
LAST_NON_PAD_TOKEN are the fair matched analogs; readout_mean_pool / readout_last_non_pad reused
verbatim from diag_comprehension_readout_sweep_v1.py) plus HRR_POSITION_BIND as a labeled BONUS
(the v5 fix for our own encoder's order-blindness, informative but not the calibration-matched
comparison point).

REUSE (wiring + one new instrument construction, not new mechanism): experiments.
exp_unified_self_learning_loop_v2._scramble_words (scramble control, unchanged);
experiments.diag_readout_limit_probe_v1.load_frozen_encoder (frozen ckpt loader);
experiments.diag_comprehension_readout_sweep_v1.compute_hidden_cache / readout_mean_pool /
readout_last_non_pad / readout_hrr_position_bind (own-encoder readout machinery, unchanged);
experiments.eval_battery_relational_cloze_v7's class-weighted-CE + train-fit-sanity discipline
(reimplemented here in binary form -- see fit_binary_probe / _probe_sanity -- same fix that
un-collapsed the relation-cloze decoder tonight, applied proactively to a NEW binary task rather
than imported, since the label cardinality differs, K=2 not K=n_relations). New code: the two
item-family generators (gen_agent_patient / gen_entity_state), the raw-HF three-readout encoder
(_raw_hf_encode, transformers AutoTokenizer/AutoModel, offline, CPU), the binary probe fit/eval,
and the calibrate-then-score orchestration in main().

LEAK-PROOFING: TRAIN/EVAL split by entity-pair (construction 1) / (object,state-pair) combo
(construction 2) identity, asserted disjoint by self-test before any probe is fit. The linear
probe for every arm (calibration models AND our own encoders) is fit ONLY on TRAIN coherent
items; EVAL coherent + EVAL scrambled are scored forward-only, never touching the fit.
"""
from __future__ import annotations

import itertools
import os
import sys
import time
import traceback
from datetime import datetime, timezone

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import json  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
import torch.nn as nn  # noqa: E402
import torch.nn.functional as F  # noqa: E402

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from tokenizers import Tokenizer  # noqa: E402

import experiments.exp_unified_self_learning_loop_v2 as LOOP2  # noqa: E402
from experiments.diag_readout_limit_probe_v1 import load_frozen_encoder  # noqa: E402
from experiments.diag_comprehension_readout_sweep_v1 import (  # noqa: E402
    compute_hidden_cache, readout_mean_pool, readout_last_non_pad, readout_hrr_position_bind,
)
from experiments.exp_scale_meaning_learn_arc_heldout_v2 import TinyTransformer  # noqa: E402

OUT_DIR = os.path.join(_REPO, "data", "diag_order_critical_comprehension_calib_v1")
SEED = 20260728
MARGIN_THRESH = 0.15          # coherent_acc - scrambled_acc must clear this to call it "passes"
COHERENT_FLOOR = 0.65         # coherent_acc itself must clear chance(0.5)+0.15
SANITY_MARGIN = 0.10          # train balanced_acc must clear chance + this (decoder-collapse gate)

BASELINE_CKPT = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v2", "ckpt_seed_7.pt")
RELOBJ_CKPT = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v3_relobj", "ckpt_seed_7.pt")

CALIBRATION_MODELS = [
    ("sentence-transformers/all-MiniLM-L6-v2", "MiniLM"),
    ("BAAI/bge-small-en-v1.5", "BGE_SMALL"),
]

# --- MULTI_ENTITY_STATE gate B (random-init-core control, 2026-07-29) ---
# Gate (B) of the acceptance test: a RANDOM-INIT encoder run through the SAME architecture +
# SAME readout must FAIL (margin near chance) where a TRAINED known reader (gate A) passes. This
# is OUR substrate encoder's own architecture (TinyTransformer, per BASELINE_CKPT's model_cfg),
# not a random-init HF model -- the question is whether OUR encoder family's raw untrained
# structure alone (position embeddings + self-attention geometry) can solve the construction, vs
# requiring the LEARNED weights. Matches design doc D3: "MANDATORY random-init-ENCODER-through-
# the-full-stateful-core control -- if the untrained core matches, it is structure not learning."
RANDOM_INIT_SEED = 20260729
RANDOM_INIT_MARGIN_FAIL_THRESH = 0.05   # gate B: random-init margin must stay BELOW this to "fail" (pass the gate)

# ---------------------------------------------------------------------------
# Vocab (common words -- friendly to a from-scratch BPE vocab trained on real text)
# ---------------------------------------------------------------------------
AGENT_ENTITIES = [
    "man", "woman", "boy", "girl", "dog", "cat", "lion", "tiger", "doctor", "teacher",
    "farmer", "soldier", "king", "queen", "horse", "wolf", "bear", "eagle", "snake", "monkey",
    "child", "nurse", "robot", "alien",
]
AGENT_VERBS = [
    "bit", "chased", "pushed", "kicked", "hit", "scared", "followed", "watched", "helped",
    "hugged", "grabbed", "blocked", "warned", "tricked", "carried", "lifted", "struck",
    "bumped", "nudged", "startled",
]

STATE_OBJECTS = [
    "door", "window", "light", "box", "gate", "valve", "switch", "machine", "engine", "lamp",
    "faucet", "oven", "fan", "alarm", "lock", "screen", "radio", "printer", "pump", "heater",
]
STATE_PAIRS = [
    ("open", "closed"), ("on", "off"), ("up", "down"), ("hot", "cold"), ("loud", "quiet"),
    ("full", "empty"), ("locked", "unlocked"), ("broken", "fixed"), ("wet", "dry"),
    ("bright", "dark"), ("clean", "dirty"), ("new", "old"), ("fast", "slow"), ("heavy", "light"),
    ("sharp", "dull"),
]
TIME_TEMPLATES = [
    ("first", "then"), ("initially", "later"), ("at first", "afterward"),
    ("originally", "eventually"), ("before that", "after that"),
]


def _log(msg):
    print("[order_critical_calib] %s" % msg, flush=True)


def _now():
    return datetime.now(timezone.utc).isoformat()


def _shuffled(seq, rng):
    idx = rng.permutation(len(seq))
    return [seq[i] for i in idx]


def _sample(pool, k, rng):
    k = min(k, len(pool))
    idx = rng.choice(len(pool), size=k, replace=False)
    return [pool[i] for i in idx]


# ===========================================================================
# CONSTRUCTION 1: AGENT_PATIENT_REVERSIBLE
# ===========================================================================
def gen_agent_patient(rng, eval_pair_frac=0.30, train_target=900, eval_target_per_label=200):
    entities = AGENT_ENTITIES
    pairs = _shuffled(list(itertools.combinations(range(len(entities)), 2)), rng)
    n_eval_pairs = max(30, int(round(eval_pair_frac * len(pairs))))
    eval_pair_set = set(pairs[:n_eval_pairs])
    train_pair_set = set(pairs[n_eval_pairs:])
    assert train_pair_set.isdisjoint(eval_pair_set), "AGENT_PATIENT leak: pair overlap"

    def build_pools(pair_set):
        pool0, pool1 = [], []
        for (ai, bi) in pair_set:
            a, b = entities[ai], entities[bi]
            for v in AGENT_VERBS:
                pool0.append(dict(sent="the %s %s the %s ." % (a, v, b), label=0, group=(ai, bi), verb=v))
                pool1.append(dict(sent="the %s %s the %s ." % (b, v, a), label=1, group=(ai, bi), verb=v))
        return pool0, pool1

    tr0, tr1 = build_pools(train_pair_set)
    ev0, ev1 = build_pools(eval_pair_set)
    train_items = _shuffled(_sample(tr0, train_target // 2, rng) + _sample(tr1, train_target // 2, rng), rng)
    eval_items = _shuffled(_sample(ev0, eval_target_per_label, rng) + _sample(ev1, eval_target_per_label, rng), rng)
    return dict(name="AGENT_PATIENT", train=train_items, eval=eval_items,
                train_group_set=train_pair_set, eval_group_set=eval_pair_set,
                n_entities=len(entities), n_verbs=len(AGENT_VERBS))


# ===========================================================================
# CONSTRUCTION 3: CROSS_BOUNDARY (added 2026-07-28, comprehension-frontier design-A cell
# `experiments/exp_entity_slot_gate_cross_boundary_v1.py`; extends this instrument IN PLACE
# per notes/comprehension_situation_model_frontier_scoping.md "Measurement").
#
# Genuine cross-CLAUSE-BOUNDARY entity-tracking construction (2-sentence consistent-vs-violated).
# Two entities (e1, e2), ONE shared state-axis (sA, sB) from STATE_PAIRS. Clause 1 is TWO short
# sentences, each stating one entity's current state; clause 2 (the boundary) makes ONE claim --
# "it became sA" -- using the pronoun "it" (standard recency-antecedent convention: "it" binds to
# the LAST-mentioned entity in clause 1, a construction-template ground-truth label, not a resolver
# the mechanism is given).
#   ORDER_1 (e1 first=sA, e2 last=sB): "it"->e2 (was sB); "it became sA" = sB->sA, a VALID
#       antonym flip -> label=1 CONSISTENT.
#   ORDER_2 (e2 first=sB, e1 last=sA; clause 1's two sentences SWAPPED, clause 2 IDENTICAL text):
#       "it"->e1 (was ALREADY sA); "it became sA" while already sA = a null/invalid transition
#       -> label=0 VIOLATED.
# ORDER_1 and ORDER_2 share an IDENTICAL WORD MULTISET (only the order of clause 1's two sentences
# differs) -- exactly the AGENT_PATIENT/ENTITY_STATE discipline (same words, order determines
# label; NOT solvable by bag-of-words / axis-membership shortcuts). Requires carrying an
# entity-state assignment ACROSS the clause boundary to judge clause 2 -- the gap the frontier
# note flags as UNMEASURED (cross-boundary persistence/update), motivating the entity-slot+gate
# mechanism cell.
#
# CALIBRATION ITERATION (2026-07-28, honest record per the calibration-first rule -- "a
# construction no known reader passes is broken; fix the construction, don't score ours"):
#   v1 "adv1 the e1 was sA and the e2 was sB . adv2 it became sA ." (single "and"-joined clause 1,
#     train=900/eval=400) -- FAILED: best margin 0.1175 (BGE_SMALL MEAN_POOL), below
#     MARGIN_THRESH=0.15. MEASURED@this session's exp_dev calibration probe.
#   v2 "... it was still sB ." (direct state-equality framing instead of "became") -- WORSE
#     (margin ~0.02-0.07 across both models): the fixed "sB" target removed a usable structural
#     cue rather than adding one. Reverted.
#   v3 ordinal references ("the second one" / "the one mentioned last" instead of pronoun "it")
#     -- WORSE still (margin ~0.02-0.07): pronoun "it" was not the bottleneck.
#   v4 (LANDED) -- split clause 1 into TWO SEPARATE SENTENCES ("the e1 was sA . the e2 was sB .")
#     instead of one "and"-joined clause, KEEP "it became sA", and INCREASE N (train=1800,
#     eval_per_label=300 vs the sibling constructions' 900/200) -- PASSES: BGE_SMALL MEAN_POOL
#     coherent=0.7483 scrambled=0.4883 margin=+0.2600 (z-sig, train_sanity=True); LAST_TOKEN
#     margin=+0.2450; CLS_TOKEN margin=+0.2450. MiniLM still short (best margin 0.1383) but the
#     calibration gate only requires ONE known reader to pass on ONE readout -- satisfied.
#     MEASURED@this session's exp_dev calibration probe (reduced-scale iteration harness, then
#     reproduced at this exact regime by this script's own main() run -- see results.json).
#
# clause1_text / clause2_text are stored SEPARATELY (not re-parsed from `sent`) so the entity-slot
# mechanism can encode each clause with its own frozen-encoder forward pass without any string
# parsing/resolver logic -- the boundary is known because WE generated the template (construction-
# template info, per the frontier note's ALLOWED list), never inferred by the mechanism.
# ===========================================================================
def gen_cross_boundary(rng, eval_pair_frac=0.30, train_target=1800, eval_target_per_label=300):
    entities = STATE_OBJECTS
    pairs = _shuffled(list(itertools.combinations(range(len(entities)), 2)), rng)
    n_eval_pairs = max(30, int(round(eval_pair_frac * len(pairs))))
    eval_pair_set = set(pairs[:n_eval_pairs])
    train_pair_set = set(pairs[n_eval_pairs:])
    assert train_pair_set.isdisjoint(eval_pair_set), "CROSS_BOUNDARY leak: pair overlap"

    def build_pools(pair_set):
        pool0, pool1 = [], []
        for (ei, ej) in pair_set:
            e1, e2 = entities[ei], entities[ej]
            for pidx, (sA, sB) in enumerate(STATE_PAIRS):
                for (adv1, adv2) in TIME_TEMPLATES:
                    group = (ei, ej, pidx)
                    c1_order1 = "%s the %s was %s . the %s was %s ." % (adv1, e1, sA, e2, sB)
                    c1_order2 = "%s the %s was %s . the %s was %s ." % (adv1, e2, sB, e1, sA)
                    c2 = "%s it became %s ." % (adv2, sA)
                    pool1.append(dict(sent=c1_order1 + " " + c2, clause1=c1_order1, clause2=c2,
                                       label=1, group=group, adv=(adv1, adv2)))
                    pool0.append(dict(sent=c1_order2 + " " + c2, clause1=c1_order2, clause2=c2,
                                       label=0, group=group, adv=(adv1, adv2)))
        return pool0, pool1

    tr0, tr1 = build_pools(train_pair_set)
    ev0, ev1 = build_pools(eval_pair_set)
    # By-construction multiset check: pool0[k]/pool1[k] are built in LOCKSTEP inside the same
    # nested-loop iteration (same group/pidx/adv), so index-aligned pairs are guaranteed to be the
    # ORDER_1/ORDER_2 variant of the identical (group,adv) triple -- check BEFORE sampling (a random
    # post-hoc sample of train/eval need not co-select both labels for the same triple).
    n_checked = 0
    for k in range(0, min(len(tr0), len(tr1)), max(1, len(tr0) // 40)):
        w0 = sorted(tr0[k]["sent"].split())
        w1 = sorted(tr1[k]["sent"].split())
        assert tr0[k]["group"] == tr1[k]["group"] and tr0[k]["adv"] == tr1[k]["adv"], \
            "CROSS_BOUNDARY: pool0/pool1 index-alignment broken at k=%d" % k
        assert w0 == w1, "CROSS_BOUNDARY: multiset mismatch at k=%d: %r vs %r" % (k, w0, w1)
        n_checked += 1
    assert n_checked >= 5, "CROSS_BOUNDARY multiset self-test found too few pairs (%d)" % n_checked
    _log("CROSS_BOUNDARY multiset self-test OK: %d index-aligned ORDER_1/ORDER_2 pairs "
         "share identical word multiset (by-construction, pre-sampling)" % n_checked)

    train_items = _shuffled(_sample(tr0, train_target // 2, rng) + _sample(tr1, train_target // 2, rng), rng)
    eval_items = _shuffled(_sample(ev0, eval_target_per_label, rng) + _sample(ev1, eval_target_per_label, rng), rng)
    return dict(name="CROSS_BOUNDARY", train=train_items, eval=eval_items,
                train_group_set=train_pair_set, eval_group_set=eval_pair_set,
                n_entities=len(entities), n_pairs=len(STATE_PAIRS), has_clause_split=True)


# ===========================================================================
# CONSTRUCTION 2: ENTITY_STATE_TIME_UPDATE
# ===========================================================================
def gen_entity_state(rng, eval_combo_frac=0.30, train_target=900, eval_target_per_label=200):
    objects = STATE_OBJECTS
    pairs = STATE_PAIRS
    combos = _shuffled(list(itertools.product(range(len(objects)), range(len(pairs)))), rng)
    n_eval_combos = max(30, int(round(eval_combo_frac * len(combos))))
    eval_combo_set = set(combos[:n_eval_combos])
    train_combo_set = set(combos[n_eval_combos:])
    assert train_combo_set.isdisjoint(eval_combo_set), "ENTITY_STATE leak: combo overlap"

    def build_pools(combo_set):
        pool0, pool1 = [], []
        for (oi, pi) in combo_set:
            obj = objects[oi]
            sA, sB = pairs[pi]
            for (adv1, adv2) in TIME_TEMPLATES:
                # forward: first sA, then sB -> final state = sB -> label 1
                pool1.append(dict(sent="%s the %s was %s . %s it became %s ." % (adv1, obj, sA, adv2, sB),
                                   label=1, group=(oi, pi), adv=(adv1, adv2)))
                # reverse: first sB, then sA -> final state = sA -> label 0
                pool0.append(dict(sent="%s the %s was %s . %s it became %s ." % (adv1, obj, sB, adv2, sA),
                                   label=0, group=(oi, pi), adv=(adv1, adv2)))
        return pool0, pool1

    tr0, tr1 = build_pools(train_combo_set)
    ev0, ev1 = build_pools(eval_combo_set)
    train_items = _shuffled(_sample(tr0, train_target // 2, rng) + _sample(tr1, train_target // 2, rng), rng)
    eval_items = _shuffled(_sample(ev0, eval_target_per_label, rng) + _sample(ev1, eval_target_per_label, rng), rng)
    return dict(name="ENTITY_STATE", train=train_items, eval=eval_items,
                train_group_set=train_combo_set, eval_group_set=eval_combo_set,
                n_objects=len(objects), n_state_pairs=len(pairs))


# ===========================================================================
# CONSTRUCTION 4: MULTI_ENTITY_STATE (added 2026-07-29, stateful-core measurement-first build,
# notes/stateful_core_situation_model_build_design.md "MEASUREMENT" + D3).
#
# >=3 entities, MULTI-update entity-state tracking: a stream of update events on a SHARED
# state-axis ("the {target} became {sA}", interleaved with distractor entities' updates, "the
# {target} became {sB}"); the query asks for the FINAL state of the SPECIFIC target entity --
# requires tracking WHICH updates applied to WHICH entity across the whole interleaved sequence
# and applying the LAST update to that entity, not the naive "last state-word seen anywhere".
#
# ORDER_1 (consistent, label=1): distractor noise, THEN target's FIRST update (sA), THEN more
#   distractor noise, THEN target's FINAL update (sB); query clause states "the target is sB now"
#   -- TRUE (matches target's actual last update).
# ORDER_0 (violated, label=0): the exact same distractor sentences in the exact same positions,
#   but the target's two update sentences are SWAPPED (final update is now sA, not sB); the SAME
#   query clause text ("the target is sB now") is now FALSE (target's actual last update is sA).
# ORDER_1 and ORDER_0 share an IDENTICAL WORD MULTISET (only the position of the target's two own
# update sentences differs; all distractor sentences + the query are byte-identical and in the
# same slots) -- same discipline as AGENT_PATIENT / ENTITY_STATE / CROSS_BOUNDARY: NOT solvable
# by bag-of-words; a SINGLE positional cue (e.g. "last mention of sB anywhere") is also
# insufficient once >=1 distractor entity's OWN random state words can coincide with sA/sB by
# chance -- the construction requires per-entity state-slot maintenance across intervening
# updates about OTHER entities, harder than CROSS_BOUNDARY's single 2-sentence clause.
#
# DIFFICULTY KNOBS (swept in main(), per the acceptance-gate iteration requirement): n_distractor
# entities (>=2, so total entities >=3) and n_distractor_events (sentences interleaved between the
# target's two own update sentences and around them) -- more distractors = more entities to track
# simultaneously = harder positional-attention-only solution, easier genuine per-entity maintenance
# gate to separate a trained known reader (gate A) from an untrained random-init core (gate B).
# ===========================================================================
def gen_multi_entity_state(rng, n_distractor_entities=3, n_distractor_events=4,
                            eval_combo_frac=0.30, train_target=900, eval_target_per_label=160):
    objects = STATE_OBJECTS
    pairs = STATE_PAIRS
    combos = _shuffled(list(itertools.product(range(len(objects)), range(len(pairs)))), rng)
    n_eval_combos = max(30, int(round(eval_combo_frac * len(combos))))
    eval_combo_set = set(combos[:n_eval_combos])
    train_combo_set = set(combos[n_eval_combos:])
    assert train_combo_set.isdisjoint(eval_combo_set), "MULTI_ENTITY_STATE leak: combo overlap"

    def _distractor_sents(target_idx, n, local_rng, shared_pair, p_shared=0.5):
        """Distractor update sentences for entities OTHER than the target. With probability
        p_shared, reuse the TARGET's own shared state-axis (sA/sB) for the distractor instead of
        an unrelated pair -- this creates lexical overlap (the word sB can appear attached to a
        DIFFERENT entity after the target's own last update) so a naive "last occurrence of the
        word sB anywhere" positional shortcut fails; the correct answer requires binding state
        words to the SPECIFIC entity that owns each update, not just finding the last sB token."""
        distract_pool = [j for j in range(len(objects)) if j != target_idx]
        n_use = min(n_distractor_entities, len(distract_pool))
        pick = local_rng.choice(len(distract_pool), size=n_use, replace=False)
        distract_entities = [objects[distract_pool[j]] for j in pick]
        out = []
        for _ in range(n):
            de = distract_entities[int(local_rng.integers(0, len(distract_entities)))]
            if local_rng.random() < p_shared:
                dpidx_pair = shared_pair
            else:
                dpidx_pair = pairs[int(local_rng.integers(0, len(pairs)))]
            dwhich = int(local_rng.integers(0, 2))
            dval = dpidx_pair[dwhich]
            out.append("the %s became %s ." % (de, dval))
        return out

    def build_pools(combo_set, local_rng):
        pool0, pool1 = [], []
        for (oi, pi) in combo_set:
            obj = objects[oi]
            sA, sB = pairs[pi]
            for (adv1, adv2) in TIME_TEMPLATES:
                n_pre = n_distractor_events // 2
                n_mid = n_distractor_events - n_pre
                d_pre = _distractor_sents(oi, n_pre, local_rng, (sA, sB))
                d_mid = _distractor_sents(oi, n_mid, local_rng, (sA, sB))
                target_first = "%s the %s became %s ." % (adv1, obj, sA)
                target_final = "the %s became %s ." % (obj, sB)
                query = "%s the %s is %s now ." % (adv2, obj, sB)
                # ORDER_1 (label=1, consistent): target's own two updates in TRUE chronological
                # order (first sA, then sB) -> query "target is sB now" is TRUE.
                stream1 = d_pre + [target_first] + d_mid + [target_final]
                # ORDER_0 (label=0, violated): the SAME d_pre/d_mid distractor sentences in the
                # SAME slots, but the target's own two sentences SWAPPED -> target's actual last
                # update is now sA, so the SAME query text "target is sB now" is FALSE. stream0 is
                # a pure permutation of stream1 (same two target sentences + same distractor
                # sentences, only target-sentence SLOT order differs) -> identical word multiset
                # by construction (verified below).
                stream0 = d_pre + [target_final] + d_mid + [target_first]
                group = (oi, pi)
                pool1.append(dict(sent=" ".join(stream1 + [query]), label=1, group=group,
                                   adv=(adv1, adv2), n_distractor_entities=n_distractor_entities,
                                   n_distractor_events=n_distractor_events))
                pool0.append(dict(sent=" ".join(stream0 + [query]), label=0, group=group,
                                   adv=(adv1, adv2), n_distractor_entities=n_distractor_entities,
                                   n_distractor_events=n_distractor_events))
        return pool0, pool1

    tr0, tr1 = build_pools(train_combo_set, rng)
    ev0, ev1 = build_pools(eval_combo_set, rng)

    # By-construction multiset check (same discipline as CROSS_BOUNDARY): index-aligned pool0/
    # pool1 items share the same (group, adv) triple and MUST have identical word multisets --
    # verified BEFORE sampling.
    n_checked = 0
    for k in range(0, min(len(tr0), len(tr1)), max(1, len(tr0) // 40)):
        w0 = sorted(tr0[k]["sent"].split())
        w1 = sorted(tr1[k]["sent"].split())
        assert tr0[k]["group"] == tr1[k]["group"] and tr0[k]["adv"] == tr1[k]["adv"], \
            "MULTI_ENTITY_STATE: pool0/pool1 index-alignment broken at k=%d" % k
        assert w0 == w1, "MULTI_ENTITY_STATE: multiset mismatch at k=%d: %r vs %r" % (k, w0, w1)
        n_checked += 1
    assert n_checked >= 5, "MULTI_ENTITY_STATE multiset self-test found too few pairs (%d)" % n_checked
    _log("MULTI_ENTITY_STATE(distE=%d,distEv=%d) multiset self-test OK: %d index-aligned pairs "
         "share identical word multiset (by-construction, pre-sampling)"
         % (n_distractor_entities, n_distractor_events, n_checked))

    train_items = _shuffled(_sample(tr0, train_target // 2, rng) + _sample(tr1, train_target // 2, rng), rng)
    eval_items = _shuffled(_sample(ev0, eval_target_per_label, rng) + _sample(ev1, eval_target_per_label, rng), rng)
    return dict(name="MULTI_ENTITY_STATE_distE%d_distEv%d" % (n_distractor_entities, n_distractor_events),
                train=train_items, eval=eval_items,
                train_group_set=train_combo_set, eval_group_set=eval_combo_set,
                n_objects=len(objects), n_state_pairs=len(pairs),
                n_distractor_entities=n_distractor_entities, n_distractor_events=n_distractor_events,
                n_total_entities=n_distractor_entities + 1)


def load_random_init_encoder(ckpt_path, seed):
    """Gate-B control: SAME architecture as the frozen checkpoint at ckpt_path (model_cfg only --
    the LEARNED weights are discarded), freshly initialized with `seed`. Same tokenizer/spec as
    the checkpoint (BPE vocab is not the learned representation under test; only the transformer
    weights are). Returns the same (model, tok, spec, meta) tuple shape as load_frozen_encoder so
    it drops into the same readout machinery."""
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    mc = ckpt["model_cfg"]
    torch.manual_seed(seed)
    model = TinyTransformer(mc["vocab"], mc["max_len"], mc["d_model"], mc["n_layers"],
                            mc["n_heads"], mc["ffn_mult"], mc["pad_id"])
    model.eval()
    for p in model.parameters():
        p.requires_grad_(False)
    tok = Tokenizer.from_str(ckpt["tokenizer_json"])
    spec = ckpt["spec"]
    meta = dict(seed=seed, run_mode="RANDOM_INIT_CONTROL", source_arch_ckpt=ckpt_path, model_cfg=mc)
    return model, tok, spec, meta


def _self_test_constructions(constructions, rng):
    """Leak-proofness + scramble self-tests. Raises on violation (no silent continue)."""
    for c in constructions:
        assert c["train_group_set"].isdisjoint(c["eval_group_set"]), \
            "%s: LEAK -- train/eval group overlap" % c["name"]
        y_tr = [it["label"] for it in c["train"]]
        y_ev = [it["label"] for it in c["eval"]]
        assert set(y_tr) == {0, 1}, "%s: TRAIN labels not both present: %s" % (c["name"], set(y_tr))
        assert set(y_ev) == {0, 1}, "%s: EVAL labels not both present: %s" % (c["name"], set(y_ev))
        n0 = sum(1 for y in y_ev if y == 0)
        n1 = sum(1 for y in y_ev if y == 1)
        assert abs(n0 - n1) <= 2, "%s: EVAL not balanced (%d vs %d)" % (c["name"], n0, n1)
        assert len(c["eval"]) >= 300, "%s: EVAL too small for adequate power (%d < 300)" % (c["name"], len(c["eval"]))
        # scramble preserves word multiset, changes order (sample check)
        srng = np.random.default_rng(SEED + 77)
        n_order_changed = 0
        for it in c["eval"][:30]:
            s = it["sent"]
            scr = LOOP2._scramble_words(s, srng)
            assert sorted(s.split()) == sorted(scr.split()), "%s: scramble changed word multiset" % c["name"]
            if scr != s:
                n_order_changed += 1
        assert n_order_changed >= 25, ("%s: scramble suspiciously often a no-op (%d/30 changed) -- "
                                        "RNG or sentence-length bug" % (c["name"], n_order_changed))
        _log("%s self-test OK: train=%d eval=%d (n0=%d n1=%d) train/eval groups disjoint (%d/%d)"
             % (c["name"], len(c["train"]), len(c["eval"]), n0, n1,
                len(c["train_group_set"]), len(c["eval_group_set"])))


# ===========================================================================
# CALIBRATION MODEL ENCODING: one raw HF forward pass -> 3 readouts
# ===========================================================================
_HF_MODEL_CACHE = {}


def _load_hf_model_cached(model_name):
    """Cache tokenizer+model across the many _raw_hf_encode calls per model_name (train/eval/
    eval_scrambled x 2 constructions) -- avoids ~1-2s reload overhead per call, purely an
    efficiency wrapper (no behavior change vs a fresh from_pretrained each time)."""
    if model_name not in _HF_MODEL_CACHE:
        from transformers import AutoTokenizer, AutoModel
        tok = AutoTokenizer.from_pretrained(model_name)
        mdl = AutoModel.from_pretrained(model_name)
        mdl.eval()
        _HF_MODEL_CACHE[model_name] = (tok, mdl)
    return _HF_MODEL_CACHE[model_name]


def _raw_hf_encode(model_name, sentences, batch_size=64, max_length=32):
    tok, mdl = _load_hf_model_cached(model_name)
    means, clss, lasts = [], [], []
    with torch.no_grad():
        for i in range(0, len(sentences), batch_size):
            batch = sentences[i:i + batch_size]
            enc = tok(batch, padding=True, truncation=True, max_length=max_length, return_tensors="pt")
            out = mdl(**enc)
            h = out.last_hidden_state
            mask = enc["attention_mask"]
            keep = mask.unsqueeze(-1).float()
            summed = (h * keep).sum(dim=1)
            cnt = keep.sum(dim=1).clamp(min=1.0)
            mean_g = F.normalize(summed / cnt, dim=1)
            cls_g = F.normalize(h[:, 0, :], dim=1)
            lengths = mask.sum(dim=1).long() - 1
            lengths = lengths.clamp(min=0)
            last_g = h[torch.arange(h.shape[0]), lengths, :]
            last_g = F.normalize(last_g, dim=1)
            means.append(mean_g.numpy())
            clss.append(cls_g.numpy())
            lasts.append(last_g.numpy())
    return dict(MEAN_POOL=np.concatenate(means, axis=0).astype(np.float32),
                CLS_TOKEN=np.concatenate(clss, axis=0).astype(np.float32),
                LAST_TOKEN=np.concatenate(lasts, axis=0).astype(np.float32))


# ===========================================================================
# BINARY LINEAR PROBE: class-balanced CE + decoder-collapse sanity gate
# (binary re-implementation of the SAME fix landed in eval_battery_relational_cloze_v7 tonight)
# ===========================================================================
def fit_binary_probe(X_train, y_train, steps=300, lr=0.05, wd=0.001, seed=0):
    torch.manual_seed(seed)
    d = X_train.shape[1]
    lin = nn.Linear(d, 2)
    opt = torch.optim.Adam(lin.parameters(), lr=lr, weight_decay=wd)
    X = torch.from_numpy(X_train).float()
    y = torch.from_numpy(y_train).long()
    counts = torch.clamp(torch.bincount(y, minlength=2).float(), min=1.0)
    class_weight = counts.sum() / (2 * counts)
    last_loss = float("nan")
    for _ in range(steps):
        opt.zero_grad()
        logits = lin(X)
        loss = F.cross_entropy(logits, y, weight=class_weight)
        loss.backward()
        opt.step()
        last_loss = float(loss.detach())
    if not np.isfinite(last_loss):
        raise FloatingPointError("binary probe training diverged (non-finite loss)")
    return lin, last_loss


def _probe_sanity(lin, X_train, y_train):
    with torch.no_grad():
        pred = lin(torch.from_numpy(X_train).float()).numpy().argmax(axis=1)
    recalls = []
    for c in (0, 1):
        mask = (y_train == c)
        if mask.sum() > 0:
            recalls.append(float((pred[mask] == c).mean()))
    balanced_acc = float(np.mean(recalls)) if recalls else 0.0
    return dict(train_balanced_acc=balanced_acc, chance=0.5,
                train_beats_chance=bool(balanced_acc >= 0.5 + SANITY_MARGIN))


def _probe_eval_acc(lin, X, y):
    with torch.no_grad():
        pred = lin(torch.from_numpy(X).float()).numpy().argmax(axis=1)
    acc = float((pred == y).mean())
    recalls = []
    for c in (0, 1):
        mask = (y == c)
        if mask.sum() > 0:
            recalls.append(float((pred[mask] == c).mean()))
    balanced_acc = float(np.mean(recalls)) if recalls else 0.0
    return acc, balanced_acc


def _two_prop_z(acc1, n1, acc2, n2):
    """Two-proportion z-test for coherent_acc vs scrambled_acc (independent samples)."""
    p_pool = (acc1 * n1 + acc2 * n2) / (n1 + n2)
    se = np.sqrt(p_pool * (1 - p_pool) * (1.0 / n1 + 1.0 / n2))
    if se <= 1e-12:
        return 0.0
    return float((acc1 - acc2) / se)


def score_readout_arm(name, X_train, y_train, X_eval_coh, X_eval_scr, y_eval, seed):
    lin, final_loss = fit_binary_probe(X_train, y_train, seed=seed)
    sanity = _probe_sanity(lin, X_train, y_train)
    coh_acc, coh_bal = _probe_eval_acc(lin, X_eval_coh, y_eval)
    scr_acc, scr_bal = _probe_eval_acc(lin, X_eval_scr, y_eval)
    margin = coh_acc - scr_acc
    z = _two_prop_z(coh_acc, len(y_eval), scr_acc, len(y_eval))
    comprehension_specific = bool(sanity["train_beats_chance"] and coh_acc >= COHERENT_FLOOR
                                   and margin >= MARGIN_THRESH)
    return dict(name=name, decoder_final_loss=final_loss, train_sanity=sanity,
                coherent_acc=coh_acc, coherent_balanced_acc=coh_bal,
                scrambled_acc=scr_acc, scrambled_balanced_acc=scr_bal,
                margin=margin, z_stat=z, n_eval=len(y_eval),
                comprehension_specific=comprehension_specific)


# ===========================================================================
# OUR OWN ENCODER SCORING (matched readout categories + HRR bonus)
# ===========================================================================
def _own_encoder_readouts(ckpt_path, train_sents, eval_coh_sents, eval_scr_sents, seed):
    model, tok, spec, ckpt_meta = load_frozen_encoder(ckpt_path)
    device = torch.device("cpu")
    cfg = dict(max_len=min(32, model.max_len if hasattr(model, "max_len") else 32), encode_batch=256)
    H_tr, M_tr, _ = compute_hidden_cache(model, tok, spec, train_sents, cfg, device)
    H_ec, M_ec, _ = compute_hidden_cache(model, tok, spec, eval_coh_sents, cfg, device)
    H_es, M_es, _ = compute_hidden_cache(model, tok, spec, eval_scr_sents, cfg, device)
    out = {}
    out["MEAN_POOL"] = (readout_mean_pool(H_tr, M_tr), readout_mean_pool(H_ec, M_ec), readout_mean_pool(H_es, M_es))
    out["LAST_TOKEN"] = (readout_last_non_pad(H_tr, M_tr), readout_last_non_pad(H_ec, M_ec), readout_last_non_pad(H_es, M_es))
    out["HRR_POSITION_BIND_bonus"] = (readout_hrr_position_bind(H_tr, M_tr),
                                       readout_hrr_position_bind(H_ec, M_ec),
                                       readout_hrr_position_bind(H_es, M_es))
    return out, ckpt_meta


def _random_init_readouts(arch_ckpt_path, train_sents, eval_coh_sents, eval_scr_sents, seed, max_len=32):
    """Gate-B control: SAME forward-pass + readout machinery as _own_encoder_readouts, but the
    encoder is load_random_init_encoder's untrained SAME-architecture model (see that function's
    docstring). Only MEAN_POOL/LAST_TOKEN -- the two matched-analog readout categories used for
    known-reader comparison -- are computed (no HRR bonus; not needed for the gate).
    `max_len` MUST be sized to the construction's actual sentence length (BPE-token count, not
    word count) -- see MES_MAX_LEN / MES_HF_MAX_LENGTH below; silently truncating at the default
    32 (fine for AGENT_PATIENT/ENTITY_STATE/CROSS_BOUNDARY's <=20-word sentences) would corrupt
    any longer construction (MULTI_ENTITY_STATE's multi-distractor streams run 30-65+ BPE tokens)
    by cutting off the query and/or one of the two target-update sentences -- a truncation-driven
    positional artifact, not a genuine comprehension signal (caught 2026-07-29 by checking actual
    tokenizer output length against the hardcoded cap before trusting the first full run)."""
    model, tok, spec, meta = load_random_init_encoder(arch_ckpt_path, seed)
    device = torch.device("cpu")
    cfg = dict(max_len=min(max_len, model.max_len if hasattr(model, "max_len") else max_len), encode_batch=256)
    H_tr, M_tr, _ = compute_hidden_cache(model, tok, spec, train_sents, cfg, device)
    H_ec, M_ec, _ = compute_hidden_cache(model, tok, spec, eval_coh_sents, cfg, device)
    H_es, M_es, _ = compute_hidden_cache(model, tok, spec, eval_scr_sents, cfg, device)
    out = {}
    out["MEAN_POOL"] = (readout_mean_pool(H_tr, M_tr), readout_mean_pool(H_ec, M_ec), readout_mean_pool(H_es, M_es))
    out["LAST_TOKEN"] = (readout_last_non_pad(H_tr, M_tr), readout_last_non_pad(H_ec, M_ec), readout_last_non_pad(H_es, M_es))
    return out, meta


# ===========================================================================
# Main orchestration
# ===========================================================================
def main():
    t_wall0 = time.perf_counter()
    os.makedirs(OUT_DIR, exist_ok=True)
    rng = np.random.default_rng(SEED)

    ap = gen_agent_patient(rng)
    es = gen_entity_state(rng)
    cb = gen_cross_boundary(rng)   # runs its own by-construction multiset self-test internally
    constructions = [ap, es, cb]
    _self_test_constructions(constructions, rng)

    srng = np.random.default_rng(SEED + 1234)
    for c in constructions:
        c["eval_scrambled_sents"] = [LOOP2._scramble_words(it["sent"], srng) for it in c["eval"]]

    calibration_results = {}
    validated_readout_per_construction = {}

    for model_name, short_name in CALIBRATION_MODELS:
        calibration_results[short_name] = {}
        for c in constructions:
            train_sents = [it["sent"] for it in c["train"]]
            eval_sents = [it["sent"] for it in c["eval"]]
            eval_scr_sents = c["eval_scrambled_sents"]
            y_train = np.array([it["label"] for it in c["train"]], dtype=np.int64)
            y_eval = np.array([it["label"] for it in c["eval"]], dtype=np.int64)

            t0 = time.perf_counter()
            G_tr = _raw_hf_encode(model_name, train_sents)
            G_ec = _raw_hf_encode(model_name, eval_sents)
            G_es = _raw_hf_encode(model_name, eval_scr_sents)
            t_enc = time.perf_counter() - t0
            _log("%s / %s encoded (%.1fs): train=%d eval=%d" % (short_name, c["name"], t_enc, len(train_sents), len(eval_sents)))

            per_readout = {}
            for readout_name in ("MEAN_POOL", "CLS_TOKEN", "LAST_TOKEN"):
                res = score_readout_arm(readout_name, G_tr[readout_name], y_train,
                                         G_ec[readout_name], G_es[readout_name], y_eval, SEED)
                per_readout[readout_name] = res
                _log("  %s/%s/%s: train_sanity=%s coherent=%.4f scrambled=%.4f margin=%+.4f z=%.2f pass=%s"
                     % (short_name, c["name"], readout_name, res["train_sanity"]["train_beats_chance"],
                        res["coherent_acc"], res["scrambled_acc"], res["margin"], res["z_stat"],
                        res["comprehension_specific"]))

            calibration_results[short_name][c["name"]] = dict(per_readout=per_readout, t_encode_s=t_enc)

            passing = [r for r in per_readout if per_readout[r]["comprehension_specific"]]
            if passing:
                best = max(passing, key=lambda r: per_readout[r]["margin"])
                cur = validated_readout_per_construction.get(c["name"])
                if cur is None or per_readout[best]["margin"] > cur["margin"]:
                    validated_readout_per_construction[c["name"]] = dict(
                        model=short_name, readout=best, margin=per_readout[best]["margin"],
                        coherent_acc=per_readout[best]["coherent_acc"])

    instrument_valid_per_construction = {c["name"]: (c["name"] in validated_readout_per_construction)
                                          for c in constructions}
    instrument_valid_overall = all(instrument_valid_per_construction.values())
    instrument_valid_any = any(instrument_valid_per_construction.values())

    _log("CALIBRATION GATE: per-construction valid=%s overall(both)=%s any=%s winners=%s"
         % (instrument_valid_per_construction, instrument_valid_overall, instrument_valid_any,
            validated_readout_per_construction))

    own_encoder_results = {}
    if instrument_valid_any:
        for ckpt_name, ckpt_path in (("BASELINE_v2", BASELINE_CKPT), ("RELOBJ_v3", RELOBJ_CKPT)):
            if not os.path.exists(ckpt_path):
                own_encoder_results[ckpt_name] = dict(skipped="ckpt not found at %s" % ckpt_path)
                continue
            own_encoder_results[ckpt_name] = {}
            for c in constructions:
                if not instrument_valid_per_construction[c["name"]]:
                    own_encoder_results[ckpt_name][c["name"]] = dict(skipped="construction not validated by any known reader")
                    continue
                train_sents = [it["sent"] for it in c["train"]]
                eval_sents = [it["sent"] for it in c["eval"]]
                eval_scr_sents = c["eval_scrambled_sents"]
                y_train = np.array([it["label"] for it in c["train"]], dtype=np.int64)
                y_eval = np.array([it["label"] for it in c["eval"]], dtype=np.int64)

                t0 = time.perf_counter()
                readouts, ckpt_meta = _own_encoder_readouts(ckpt_path, train_sents, eval_sents, eval_scr_sents, SEED)
                t_enc = time.perf_counter() - t0
                _log("%s / %s own-encoder readouts computed (%.1fs)" % (ckpt_name, c["name"], t_enc))

                winner = validated_readout_per_construction[c["name"]]
                matched_readout = "MEAN_POOL" if winner["readout"] in ("MEAN_POOL", "CLS_TOKEN") else "LAST_TOKEN"
                # CLS_TOKEN has no direct analog on a no-CLS encoder; MEAN_POOL is the closest
                # matched "native pooled sentence embedding" category -- documented, not silent.

                per_readout = {}
                for rname in ("MEAN_POOL", "LAST_TOKEN", "HRR_POSITION_BIND_bonus"):
                    G_tr, G_ec, G_es = readouts[rname]
                    res = score_readout_arm(rname, G_tr, y_train, G_ec, G_es, y_eval, SEED)
                    per_readout[rname] = res
                    _log("  %s/%s/%s: train_sanity=%s coherent=%.4f scrambled=%.4f margin=%+.4f pass=%s"
                         % (ckpt_name, c["name"], rname, res["train_sanity"]["train_beats_chance"],
                            res["coherent_acc"], res["scrambled_acc"], res["margin"], res["comprehension_specific"]))

                own_encoder_results[ckpt_name][c["name"]] = dict(
                    per_readout=per_readout, t_encode_s=t_enc, ckpt_meta=ckpt_meta,
                    calibration_winner=winner, matched_readout_used=matched_readout,
                    matched_readout_result=per_readout[matched_readout],
                    matched_vs_known_reader_gap=(winner["margin"] - per_readout[matched_readout]["margin"]),
                    matched_vs_chance=(per_readout[matched_readout]["coherent_acc"] - 0.5),
                )
    else:
        _log("NO construction validated by ANY known reader on ANY readout -- skipping own-encoder scoring "
             "(would be uninterpretable against a broken instrument).")

    # =========================================================================
    # MULTI_ENTITY_STATE two-gate acceptance test (2026-07-29, stateful-core measurement-first
    # gating item). Difficulty escalates (more distractor entities/events); at each difficulty:
    #   Gate A: does >=1 known reader (MiniLM/BGE) x readout clear comprehension_specific
    #     (margin >= MARGIN_THRESH and coherent_acc >= COHERENT_FLOOR)?
    #   Gate B: does a RANDOM-INIT SAME-ARCHITECTURE encoder (untrained TinyTransformer, same
    #     model_cfg as BASELINE_CKPT) through the MATCHED readout stay near chance (margin <
    #     RANDOM_INIT_MARGIN_FAIL_THRESH)?
    # BOTH must hold at the SAME difficulty for the construction to be valid (a known reader can
    # solve it via learned comprehension; raw untrained structure cannot). Stop escalating once
    # BOTH gates pass (success) OR gate A itself fails (already too hard for a trained reader --
    # escalating further will not recover gate A, since more distractors only makes it harder).
    # =========================================================================
    # MES sentences run far longer than AGENT_PATIENT/ENTITY_STATE/CROSS_BOUNDARY's <=20-word
    # items (measured 2026-07-29: 29-65 BPE tokens across these 4 variants, vs the file's default
    # 32-token cap used elsewhere) -- MUST raise max_length here or every variant silently
    # truncates the query and/or one of the two target-update sentences, producing a truncation-
    # POSITION artifact (which target sentence survives near the front of the truncated window)
    # that masquerades as a real order-sensitivity signal at BOTH gate A and gate B. 96 covers the
    # hardest variant (measured max ~65 tokens) with margin; the own-encoder architecture's
    # positional-embedding table (model_cfg max_len=128) comfortably supports it.
    MES_MAX_LEN = 96
    MES_DIFFICULTY_VARIANTS = [
        dict(n_distractor_entities=2, n_distractor_events=2),
        dict(n_distractor_entities=3, n_distractor_events=4),
        dict(n_distractor_entities=4, n_distractor_events=6),
        dict(n_distractor_entities=5, n_distractor_events=8),
    ]
    mes_rng = np.random.default_rng(SEED + 555)
    mes_srng = np.random.default_rng(SEED + 556)
    mes_results = {}
    mes_order = []
    mes_acceptance_gate_satisfied = False
    mes_stop_reason = None

    for variant in MES_DIFFICULTY_VARIANTS:
        mc_ = gen_multi_entity_state(mes_rng, **variant)
        mes_order.append(mc_["name"])
        _self_test_constructions([mc_], mes_rng)   # generic leak/balance/scramble self-test (reused)

        eval_scr_sents = [LOOP2._scramble_words(it["sent"], mes_srng) for it in mc_["eval"]]
        train_sents = [it["sent"] for it in mc_["train"]]
        eval_sents = [it["sent"] for it in mc_["eval"]]
        y_train = np.array([it["label"] for it in mc_["train"]], dtype=np.int64)
        y_eval = np.array([it["label"] for it in mc_["eval"]], dtype=np.int64)

        per_model = {}
        best_known = None
        for model_name, short_name in CALIBRATION_MODELS:
            t0 = time.perf_counter()
            G_tr = _raw_hf_encode(model_name, train_sents, max_length=MES_MAX_LEN)
            G_ec = _raw_hf_encode(model_name, eval_sents, max_length=MES_MAX_LEN)
            G_es = _raw_hf_encode(model_name, eval_scr_sents, max_length=MES_MAX_LEN)
            t_enc = time.perf_counter() - t0
            _log("MES(%s)/%s encoded (%.1fs): train=%d eval=%d"
                 % (mc_["name"], short_name, t_enc, len(train_sents), len(eval_sents)))
            per_readout = {}
            for readout_name in ("MEAN_POOL", "CLS_TOKEN", "LAST_TOKEN"):
                res = score_readout_arm(readout_name, G_tr[readout_name], y_train,
                                         G_ec[readout_name], G_es[readout_name], y_eval, SEED)
                per_readout[readout_name] = res
                _log("  MES(%s)/%s/%s: coherent=%.4f scrambled=%.4f margin=%+.4f pass=%s"
                     % (mc_["name"], short_name, readout_name, res["coherent_acc"],
                        res["scrambled_acc"], res["margin"], res["comprehension_specific"]))
                if res["comprehension_specific"] and (best_known is None or res["margin"] > best_known["margin"]):
                    best_known = dict(model=short_name, readout=readout_name, margin=res["margin"],
                                       coherent_acc=res["coherent_acc"])
            per_model[short_name] = per_readout

        gate_a_pass = best_known is not None

        gate_b = None
        gate_b_pass = None
        if gate_a_pass:
            matched_readout = "MEAN_POOL" if best_known["readout"] in ("MEAN_POOL", "CLS_TOKEN") else "LAST_TOKEN"
            ri_readouts, ri_meta = _random_init_readouts(BASELINE_CKPT, train_sents, eval_sents,
                                                          eval_scr_sents, RANDOM_INIT_SEED,
                                                          max_len=MES_MAX_LEN)
            G_tr, G_ec, G_es = ri_readouts[matched_readout]
            ri_res = score_readout_arm(matched_readout + "_RANDOM_INIT", G_tr, y_train,
                                        G_ec, G_es, y_eval, SEED)
            gate_b = ri_res
            # Gate B PASSES (construction is valid on this axis) when the random-init margin
            # stays BELOW threshold -- i.e. the untrained core FAILS, as required.
            gate_b_pass = bool(ri_res["margin"] < RANDOM_INIT_MARGIN_FAIL_THRESH)
            _log("MES(%s) gate B random-init-core (%s): coherent=%.4f scrambled=%.4f margin=%+.4f "
                 "random_init_fails(gate_b_pass)=%s"
                 % (mc_["name"], matched_readout, ri_res["coherent_acc"], ri_res["scrambled_acc"],
                    ri_res["margin"], gate_b_pass))

        both_gates_pass = bool(gate_a_pass and gate_b_pass)
        mes_results[mc_["name"]] = dict(
            variant=variant, n_train=len(mc_["train"]), n_eval=len(mc_["eval"]),
            n_total_entities=mc_["n_total_entities"], per_model=per_model,
            gate_a_pass=gate_a_pass, best_known_reader=best_known,
            gate_b_random_init=gate_b, gate_b_pass=gate_b_pass, both_gates_pass=both_gates_pass,
        )
        _log("MES(%s) VERDICT: gate_A(known_reader_passes)=%s gate_B(random_init_fails)=%s BOTH=%s"
             % (mc_["name"], gate_a_pass, gate_b_pass, both_gates_pass))

        if both_gates_pass:
            mes_acceptance_gate_satisfied = True
            mes_stop_reason = "both_gates_pass_at_%s" % mc_["name"]
            _log("MES ACCEPTANCE GATE SATISFIED at %s -- stopping difficulty escalation." % mc_["name"])
            break
        if not gate_a_pass:
            mes_stop_reason = "gate_a_failed_at_%s_stopping_escalation" % mc_["name"]
            _log("MES(%s): gate A already fails (no known reader clears comprehension_specific) -- "
                 "already too hard for a TRAINED reader; harder variants will not recover gate A. "
                 "Stopping escalation." % mc_["name"])
            break
        # gate_a_pass True but gate_b_pass False (random-init ALSO matches -> structure-alone,
        # same failure class as the original cross-boundary v1 result) -> escalate to next
        # (harder) variant and re-test.

    if mes_stop_reason is None:
        mes_stop_reason = "exhausted_all_variants_without_resolution"

    mes_verdict_msg = (
        "MULTI_ENTITY_STATE two-gate sweep: acceptance_gate_satisfied=%s (stop_reason=%s); "
        "variants tried=%s; per-variant BOTH-gates=%s"
        % (mes_acceptance_gate_satisfied, mes_stop_reason, mes_order,
           {name: mes_results[name]["both_gates_pass"] for name in mes_order}))
    _log("MES FINAL: %s" % mes_verdict_msg)

    verdict_msg_parts = []
    for c in constructions:
        v = instrument_valid_per_construction[c["name"]]
        w = validated_readout_per_construction.get(c["name"])
        verdict_msg_parts.append("%s: instrument_valid=%s%s" % (
            c["name"], v, ("" if not v else (" (winner=%s/%s margin=%+.4f coherent=%.4f)"
                                              % (w["model"], w["readout"], w["margin"], w["coherent_acc"])))))
    verdict_msg = "ORDER-CRITICAL CALIBRATION: " + " | ".join(verdict_msg_parts) + " || " + mes_verdict_msg
    _log("VERDICT: %s" % verdict_msg)

    payload = dict(
        script=os.path.basename(_THIS), ts_iso=_now(), pid=os.getpid(), seed=SEED,
        margin_thresh=MARGIN_THRESH, coherent_floor=COHERENT_FLOOR, sanity_margin=SANITY_MARGIN,
        constructions_meta={c["name"]: dict(n_train=len(c["train"]), n_eval=len(c["eval"]),
                                             n_train_groups=len(c["train_group_set"]),
                                             n_eval_groups=len(c["eval_group_set"]))
                            for c in constructions},
        calibration_models=[s for _, s in CALIBRATION_MODELS],
        calibration_results=calibration_results,
        instrument_valid_per_construction=instrument_valid_per_construction,
        instrument_valid_overall_both=instrument_valid_overall,
        instrument_valid_any=instrument_valid_any,
        validated_readout_per_construction=validated_readout_per_construction,
        own_encoder_results=own_encoder_results,
        random_init_seed=RANDOM_INIT_SEED,
        random_init_margin_fail_thresh=RANDOM_INIT_MARGIN_FAIL_THRESH,
        mes_difficulty_variants=MES_DIFFICULTY_VARIANTS,
        mes_order=mes_order,
        mes_results=mes_results,
        mes_acceptance_gate_satisfied=mes_acceptance_gate_satisfied,
        mes_stop_reason=mes_stop_reason,
        mes_verdict_msg=mes_verdict_msg,
        verdict_msg=verdict_msg,
        note_caveat=("MiniLM + bge-small-en-v1.5 used DIAGNOSTIC-ONLY for instrument calibration -- "
                     "neither is wired into the substrate and neither is proposed as the encoder "
                     "(per standing USER directive against borrowed embeddings as the substrate's "
                     "encoder). All arms within a construction share the IDENTICAL TRAIN/EVAL split "
                     "and IDENTICAL scrambled-eval sentences, so every comparison is fair and paired."),
        elapsed_s_total=time.perf_counter() - t_wall0,
    )
    tmp = os.path.join(OUT_DIR, "results.json.tmp")
    final = os.path.join(OUT_DIR, "results.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    os.replace(tmp, final)
    _log("wrote %s (elapsed %.1fs)" % (final, payload["elapsed_s_total"]))
    return payload


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        traceback.print_exc()
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(os.path.join(OUT_DIR, "crash.txt"), "w", encoding="utf-8") as f:
            f.write("%s: %s\n\n%s" % (type(e).__name__, e, traceback.format_exc()))
        sys.exit(1)
