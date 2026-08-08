"""experiments/exp_definition_composition_grounding_featurebundle_crosspos_v1.py -- ISOLATED,
LOCAL, non-dispatched cell (2026-08-08, Director task brief: "bounded FIRST INCREMENT of
generalizable grounding via CROSS-POS definition-composition").

WHY: INC-2 (commit 9c4439e92, VET'd) found the narrative met/unmet frontier reduces to
generalizable word-grounding -- its relation channels (class_relation / verb_sim_bucket /
referent_sim_bucket) fire ~0/30 on modern ROCStories narrative because the closed hand-lexicons
(hdlab.goal_typing.CLASS_REGISTRY's 12 hand classes, hdlab.lexical_similarity.CONCEPT_FEATURES'
89 concepts, hdlab.verb_lexical_similarity.OUTCOME_VERB_FEATURES' ~150 verbs) are OOV for modern
vocabulary ("medal"/"restaurant"/"frumpy"/"vomited" never fire). Definition-composition ARM-A
(experiments/exp_definition_composition_grounding_retest_freshset_v1.py, commit ee22c7861)
separately validated that SCALAR result-verb polarity generalizes via gloss-composition (28-word
fresh set: coverage 75%, acc_when_fires 0.9048, acc_overall 0.6786, scramble-collapse delta
0.3215). THIS CELL asks: does EXTENDING that composition mechanism to (a) FEATURE-BUNDLE
composition (an FHRR feature vector, not just a scalar) and (b) a CROSS-POS noun/adjective seed,
un-starve INC-2's relation channels on the SAME modern-narrative split?

HONEST FRAMING (do not over-read): ARM-A's 0.679 was measured on a CLEAN, hand-vetted result-verb
set. This cell is a genuine TEST of whether the SAME kind of composition covers messy modern
narrative vocabulary (nouns/adjectives, not hand-picked result-verbs) -- diagnose, don't declare.

BUILD (reuse-owned, invariant-respecting):
  1. VERB grounding = v1's ARM-A rule, UNCHANGED, imported verbatim (v1.gloss_content_words,
     v1.compose_prediction(..., exclude_light_verbs_source_c=False)) -- NOT re-authored. Used only
     to ground OOV outcome-VERBS from the narrative data (see PART B).
  2. NOUN/ADJECTIVE FEATURE-BUNDLE composition (the new mechanism this cell adds): for an OOV
     word, extract cross-POS WordNet gloss content-words (try NOUN, then ADJ/ADJ_SAT, then VERB
     senses, sense-index 0 of whichever POS resolves first -- a human reads a dictionary entry for
     whichever part of speech applies). For every gloss content-word that is grounded (member of
     hdlab.lexical_similarity.CONCEPT_FEATURES, or of the new cross-POS ADJ_SEED, or one-hop via
     WordNet antonym/similar_to propagation against those two pools), union its OWN feature TAGS
     (not just a scalar) -- the composed word's "feature vector" is
     hdlab.lexical_similarity._concept_vector_from(union_of_tags, hdlab.lexical_similarity.
     _feature_vectors()) -- the SAME bundle/cosine machinery CONCEPT_FEATURES' own 89 concepts use,
     REUSED, not reimplemented. This puts a modern OOV noun/adjective in the SAME FHRR geometry as
     the 89 hand concepts, directly comparable via concept_similarity()-style cosine.
  3. CROSS-POS ADJ_SEED: the same 18-word adjective seed drafted in the retest cell's ARM-C
     (ADJ_SEED_POS/NEG, imported UNMODIFIED from experiments.exp_definition_composition_grounding_
     retest_freshset_v1), reframed here as a feature-tagged lexicon using ONLY tags that ALREADY
     exist in CONCEPT_FEATURES' vocabulary (POS_VALENCE / EVALUATIVE_POSITIVE / NEG_VALENCE -- no
     new tag is invented, so hdlab.lexical_similarity's cached _feature_vectors() stays byte-valid
     for the 89 pre-existing concepts; this is verified by an assertion, not assumed). Antonym /
     similar_to one-hop propagation against this seed's POS/NEG pools is REIMPLEMENTED here (not
     imported) ONLY because it must be parametrizable over a real-vs-scrambled lexicon for the
     MUST-FAIL SCRAMBLED-feature floor below -- retest.ground_adjective() is hardcoded to the real
     seed and cannot serve that ablation; the RELATION PATTERN (antonym-opposition + similar_to
     satellite-cluster neighbor, the idiomatic WordNet relations for adjectives) is identical to
     retest's ARM-C, credited there.
  4. SUBSTITUTION into INC-2's relation channels: OOV referents/verbs are identified from the SAME
     50-item split INC-2 used (experiments/data/narrative_goal_outcome_rocstories_relabeled_v1.jsonl,
     n_train=30, imported split via experiments.exp_narrative_goal_outcome_role_sharded_generality_
     v1.stratified_split). For each OOV referent (noun/adjective) that composes to >=1 grounded
     gloss word, its composed feature-tag-set is REGISTERED into the live
     hdlab.lexical_similarity.CONCEPT_FEATURES dict (in-place mutation of the imported module's
     dict at runtime -- NOT an edit to any hdlab/ file on disk; reverted at the end of the run).
     For each OOV verb ARM-A grounds, its polarity is REGISTERED via hdlab.verb_lexical_similarity.
     register_acquired_outcome() -- an ALREADY-EXISTING, ALREADY-WIRED Tier-3 acquired-overlay
     mechanism built for exactly this purpose (2026-08-06 grounded-word-acquisition increment 1),
     reused unmodified, reverted via clear_acquired_outcome() at the end of the run. Because
     hdlab.goal_typing's Tier-2/3 class/referent resolution and INC-2's own extract_relation_
     features() read these same live module dicts via in_lexicon()/concept_similarity()/
     word_similarity() at CALL time (not import time), re-calling INC-2's own UNMODIFIED
     extract_relation_features()/build_episode()/grounded_rule_predict() after registration is a
     genuine "substitute the extended lexicon for the closed one, nothing else changed" test --
     zero reimplementation of INC-2's relation-feature logic.

INVARIANTS: earn-not-supply (composition from the small seed + gloss text + the already-earned
CONCEPT_FEATURES/OUTCOME_VERB_FEATURES lexicons; no supplied valence DB for the target words
themselves -- only their DEFINITIONS are read, exactly as ARM-A does for verbs); no-borrow
(glass-box FHRR bundle/cosine throughout, no word2vec/GloVe/LLM anywhere in this file).

GATE (pre-registered BEFORE this file was run):
  HARD-PASS: extended lexicon fires (>=1 grounded gloss word) on >=50% of a FRESH held-out
    noun/adjective set (disjoint from every existing lexicon), acc-when-fired>=0.70, scramble
    collapses (delta>=0.30 on gloss-word->polarity permutation); AND on the narrative data, the
    relation channels' fire-rate rises from ~0/30 to >=10/30 with acc-when-fired>=0.65 (beats the
    0.60 surface plateau, not merely ties it).
  HARD-FAIL-COVERAGE: fire stays ~0/30 downstream -> report how many OOV words had >=1 grounded
    gloss content-word (candidate/seed-coverage gap, not a mechanism ceiling).
  HARD-FAIL-CORRECTNESS: fire rises but acc collapses to ~0.50 -> coverage without truth.
  MUST-FAIL FLOORS (both reported): RANDOM-gloss arm (compose from a random word-set of the same
    size, not the real gloss) and SCRAMBLED-feature arm (permute the word->feature-tag assignment,
    fixed seed, same convention as hdlab.lexical_similarity.self_test's own circularity check) --
    both must underperform the real arm, else the coverage gain is bundle-geometry artifact, not
    genuine gloss-content signal.

Isolated, local, non-dispatched diagnostic cell (no queue, no remote ship, no canonical-store
write), test-first / detach-forbidden per the task brief.
"""
from __future__ import annotations

import json
import os
import re
import sys
import traceback
from datetime import datetime, timezone

import torch
from nltk.corpus import wordnet as wn

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(REPO_ROOT)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
EXPERIMENTS_DIR = os.path.join(REPO_ROOT, "experiments")
if EXPERIMENTS_DIR not in sys.path:
    sys.path.insert(0, EXPERIMENTS_DIR)

# ---- REUSE, not reimplement -------------------------------------------------------------------
import exp_definition_composition_grounding_probe_v1 as v1  # noqa: E402
import exp_definition_composition_grounding_retest_freshset_v1 as retest  # noqa: E402
from exp_narrative_goal_outcome_role_sharded_generality_v1 import (  # noqa: E402
    load_items, stratified_split, majority_class, accuracy,
)
import exp_narrative_goal_outcome_achievement_comparison_learnable_grounded_v1 as inc2  # noqa: E402

import hdlab.lexical_similarity as lexsim  # noqa: E402
import hdlab.verb_lexical_similarity as verblex  # noqa: E402
from hdlab.thematic_role_labeler import lemma_verb  # noqa: E402

ANCHOR_NAME = "definition_composition_grounding_featurebundle_crosspos_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

SCRAMBLE_SEED = 999                  # gloss-word->polarity permutation, byte-identical v1/retest convention
FEATURE_SCRAMBLE_SEED = 8171         # word->feature-tag permutation (this cell's own, stated not hidden)
RANDOM_GLOSS_SEED = 4242             # random-gloss-content-word sampling (this cell's own)

# =================================================================================================
# PART 0: cross-POS ADJ_SEED as a FEATURE-TAGGED lexicon (existing CONCEPT_FEATURES tags only, so
# hdlab.lexical_similarity's cached _feature_vectors() stays byte-valid for the 89 pre-existing
# concepts -- verified below, not assumed).
# =================================================================================================
ADJ_SEED_POS = retest.ADJ_SEED_POS   # imported verbatim, not re-typed
ADJ_SEED_NEG = retest.ADJ_SEED_NEG   # imported verbatim, not re-typed
_POS_TAGS = frozenset({"POS_VALENCE", "EVALUATIVE_POSITIVE"})
_NEG_TAGS = frozenset({"NEG_VALENCE"})
ADJ_SEED_FEATURES = {w: _POS_TAGS for w in ADJ_SEED_POS}
ADJ_SEED_FEATURES.update({w: _NEG_TAGS for w in ADJ_SEED_NEG})

_EXISTING_TAG_VOCAB = frozenset(lexsim._feature_vocab())
assert _POS_TAGS <= _EXISTING_TAG_VOCAB and _NEG_TAGS <= _EXISTING_TAG_VOCAB, (
    "ADJ_SEED_FEATURES uses a tag outside CONCEPT_FEATURES' existing vocabulary -- would require "
    "cache invalidation; by design this cell reuses ONLY existing tags")
assert set(ADJ_SEED_FEATURES) & set(lexsim.CONCEPT_FEATURES) == set(), (
    "ADJ_SEED word collides with an existing CONCEPT_FEATURES key")

REAL_LEXICON = dict(lexsim.CONCEPT_FEATURES)
REAL_LEXICON.update(ADJ_SEED_FEATURES)


def pos_neg_pools(lexicon):
    pos_pool, neg_pool = set(), set()
    for w, tags in lexicon.items():
        if "POS_VALENCE" in tags or "EVALUATIVE_POSITIVE" in tags:
            pos_pool.add(w)
        elif "NEG_VALENCE" in tags:
            neg_pool.add(w)
    return frozenset(pos_pool), frozenset(neg_pool)


REAL_POS_POOL, REAL_NEG_POOL = pos_neg_pools(REAL_LEXICON)

# ---- MUST-FAIL FLOOR #2 build: SCRAMBLED word->feature-tag assignment (fixed seed, byte-identical
# convention to hdlab.lexical_similarity.self_test's own circularity check: sorted(keys),
# torch.Generator().manual_seed(seed), randperm). ----------------------------------------------
_lex_words = sorted(REAL_LEXICON.keys())
_gen = torch.Generator().manual_seed(FEATURE_SCRAMBLE_SEED)
_perm = torch.randperm(len(_lex_words), generator=_gen).tolist()
SCRAMBLED_LEXICON = {_lex_words[i]: REAL_LEXICON[_lex_words[_perm[i]]] for i in range(len(_lex_words))}
SCRAMBLED_POS_POOL, SCRAMBLED_NEG_POOL = pos_neg_pools(SCRAMBLED_LEXICON)


# =================================================================================================
# PART 1: cross-POS gloss extraction + generic (lexicon-parametrized) grounding + composition.
# =================================================================================================
def definition_content_words(word: str):
    """(pos_used, gloss_text, [content_words]) for `word`'s sense-index-0 synset, trying NOUN, then
    ADJ, then ADJ_SAT, then VERB (first POS with >=1 synset wins -- a human reads whichever part of
    speech applies; stated, not cherry-picked per word). (None, None, []) if no synset in any POS."""
    for pos in (wn.NOUN, wn.ADJ, wn.ADJ_SAT, wn.VERB):
        syns = wn.synsets(word, pos=pos)
        if syns:
            syn = syns[0]
            gloss = syn.definition() + " " + " ".join(syn.examples())
            toks = re.findall(r"[a-zA-Z]+", gloss.lower())
            content = [t for t in toks if len(t) >= 3 and t not in v1._STOPWORDS and t != word]
            return pos, gloss, content
    return None, None, []


def ground_word_generic(w: str, lexicon: dict, pos_pool: frozenset, neg_pool: frozenset):
    """(tags, polarity, source) or None. Direct lexicon membership first; else one-hop WordNet
    ADJECTIVE antonym/similar_to propagation against pos_pool/neg_pool (same relation-pattern as
    retest.ground_adjective's ARM-C, reparametrized over an injectable lexicon/pool so it can be
    run against BOTH the real and the scrambled lexicon for the MUST-FAIL floor). Never consults
    held-out gold labels."""
    if w in lexicon:
        tags = lexicon[w]
        if w in pos_pool:
            pol = "POS"
        elif w in neg_pool:
            pol = "NEG"
        else:
            pol = None
        return tags, pol, "lexicon_direct"
    adj_syns = wn.synsets(w, pos=wn.ADJ) + wn.synsets(w, pos=wn.ADJ_SAT)
    if not adj_syns:
        return None
    ants = set()
    for syn in adj_syns:
        for lem in syn.lemmas():
            for ant in lem.antonyms():
                ants.add(ant.name().replace("_", " ").lower())
    hp, hn = ants & pos_pool, ants & neg_pool
    if hp and not hn:
        return _NEG_TAGS, "NEG", "antonym_hop"
    if hn and not hp:
        return _POS_TAGS, "POS", "antonym_hop"
    neighbors = set()
    for syn in adj_syns:
        for sim_syn in syn.similar_tos():
            for lem in sim_syn.lemmas():
                neighbors.add(lem.name().replace("_", " ").lower())
    np_, nn = neighbors & pos_pool, neighbors & neg_pool
    if np_ and not nn:
        return _POS_TAGS, "POS", "similar_to_hop"
    if nn and not np_:
        return _NEG_TAGS, "NEG", "similar_to_hop"
    return None


def compose_word(word: str, lexicon: dict, pos_pool: frozenset, neg_pool: frozenset,
                  content_override=None):
    """The single choke-point composition function. content_override (list of words), if given,
    REPLACES the real gloss content-words (used only by the RANDOM-gloss MUST-FAIL floor) -- the
    grounding lexicon/pools are otherwise identical to the real arm's, isolating "does the REAL
    gloss content matter" from "does the lexicon/composition rule matter"."""
    pos_used, gloss, real_content = definition_content_words(word)
    content = content_override if content_override is not None else real_content
    hits = []
    tagset = set()
    score = 0.0
    for w in content:
        g = ground_word_generic(w, lexicon, pos_pool, neg_pool)
        if g is None:
            continue
        tags, pol, source = g
        hits.append({"word": w, "tags": sorted(tags), "polarity": pol, "source": source})
        tagset |= tags
        if pol == "POS":
            score += 1.0
        elif pol == "NEG":
            score -= 1.0
    pred = "POS" if score > 0 else ("NEG" if score < 0 else None)
    return {
        "pos_used": pos_used._name_ if hasattr(pos_used, "_name_") else str(pos_used),
        "gloss": gloss, "content_words": real_content, "hits": hits,
        "composed_tags": sorted(tagset) if tagset else None,
        "score": score, "prediction": pred,
    }


# =================================================================================================
# PART 2: FRESH GOLD noun/adjective set (hand-labeled BEFORE measurement; disjoint from every
# existing lexicon this file or its imports touch -- verified programmatically below). Drawn to
# resemble the brief's own named modern-narrative examples (medal / restaurant / frumpy): concrete
# achievement/appearance nouns and adjectives, NOT result-verbs (that channel is ARM-A's, already
# validated separately) -- gold assigned by the word's own unambiguous common-usage connotation.
# ================================================================================================
FRESH_NOUNADJ_NEG = [
    "frumpy", "shabby", "disheveled", "grimy", "wretched", "squalid",
    "filthy", "tattered", "disgusting", "revolting", "slovenly", "unkempt",
]
FRESH_NOUNADJ_POS = [
    "medal", "trophy", "elegant", "prestigious", "splendid", "magnificent",
    "glorious", "dapper", "stylish", "gourmet", "pristine", "immaculate",
]


def _assert_disjoint_fresh_nounadj():
    banned = (set(lexsim.CONCEPT_FEATURES) | set(ADJ_SEED_FEATURES)
              | set(verblex.OUTCOME_SEED_POS) | set(verblex.OUTCOME_SEED_NEG)
              | set(verblex.OUTCOME_HELDOUT_POS) | set(verblex.OUTCOME_HELDOUT_NEG)
              | set(v1.HELD_OUT_WORDS) | set(retest.FRESH_NEG) | set(retest.FRESH_POS))
    all_fresh = set(FRESH_NOUNADJ_NEG) | set(FRESH_NOUNADJ_POS)
    violations = sorted(all_fresh & banned)
    assert not violations, f"FRESH NOUN/ADJ SET LEAKAGE: {violations}"
    assert len(set(FRESH_NOUNADJ_NEG) & set(FRESH_NOUNADJ_POS)) == 0
    assert len(FRESH_NOUNADJ_NEG) + len(FRESH_NOUNADJ_POS) >= 24
    return banned


BANNED_NOUNADJ = _assert_disjoint_fresh_nounadj()
FRESH_NOUNADJ_GOLD = {w: "NEG" for w in FRESH_NOUNADJ_NEG}
FRESH_NOUNADJ_GOLD.update({w: "POS" for w in FRESH_NOUNADJ_POS})
FRESH_NOUNADJ_WORDS = sorted(FRESH_NOUNADJ_GOLD)

# ---- RANDOM-gloss pool: union of every REAL content-word seen across the fresh set's own glosses.
_REAL_CONTENT_POOL = sorted({w for word in FRESH_NOUNADJ_WORDS
                              for w in definition_content_words(word)[2]})


def _random_content_for(word: str, k: int, idx: int):
    if k == 0 or not _REAL_CONTENT_POOL:
        return []
    gen = torch.Generator().manual_seed(RANDOM_GLOSS_SEED + idx)
    pool = [w for w in _REAL_CONTENT_POOL if w != word]
    if not pool:
        return []
    n = len(pool)
    perm = torch.randperm(n, generator=gen).tolist()
    idxs = [perm[i % n] for i in range(k)]
    return [pool[i] for i in idxs]


def score_arm(pred_by_word: dict, gold: dict, words):
    n = len(words)
    n_covered = sum(1 for w in words if pred_by_word[w]["hits"])
    n_fires = sum(1 for w in words if pred_by_word[w]["prediction"] is not None)
    n_correct_fires = sum(1 for w in words if pred_by_word[w]["prediction"] is not None
                           and pred_by_word[w]["prediction"] == gold[w])
    n_correct_overall = sum(1 for w in words if pred_by_word[w]["prediction"] == gold[w])
    return {
        "n": n, "coverage": n_covered, "coverage_pct": round(n_covered / n, 4),
        "fires": n_fires, "fires_pct": round(n_fires / n, 4),
        "acc_when_fires": round(n_correct_fires / n_fires, 4) if n_fires else None,
        "acc_overall": round(n_correct_overall / n, 4),
    }


def build_polarity_scramble_map(pred_by_word: dict, words, seed=SCRAMBLE_SEED):
    """gloss-word->polarity permutation, byte-identical convention to v1/retest: collect every
    grounded (gloss_word, polarity) fact actually used, permute the polarity labels, fixed seed."""
    grounded = {}
    for w in words:
        for h in pred_by_word[w]["hits"]:
            grounded[h["word"]] = h["polarity"]
    gw = sorted(grounded)
    if not gw:
        return {}
    pols = [grounded[w] for w in gw]
    gen = torch.Generator().manual_seed(seed)
    perm = torch.randperm(len(gw), generator=gen).tolist()
    return {gw[i]: pols[perm[i]] for i in range(len(gw))}


def compose_word_with_override_polarity(word, lexicon, pos_pool, neg_pool, polarity_override):
    """Recompose using the SAME grounded hits already computed, but with each hit's polarity label
    swapped per polarity_override (the scramble control) -- identical hit-set/tags, scrambled label."""
    comp = compose_word(word, lexicon, pos_pool, neg_pool)
    score = 0.0
    for h in comp["hits"]:
        pol = polarity_override.get(h["word"], h["polarity"])
        score += 1.0 if pol == "POS" else (-1.0 if pol == "NEG" else 0.0)
    pred = "POS" if score > 0 else ("NEG" if score < 0 else None)
    out = dict(comp)
    out["score"] = score
    out["prediction"] = pred
    return out


def run_fresh_nounadj_measurement():
    real_pred = {w: compose_word(w, REAL_LEXICON, REAL_POS_POOL, REAL_NEG_POOL)
                 for w in FRESH_NOUNADJ_WORDS}
    scramble_map = build_polarity_scramble_map(real_pred, FRESH_NOUNADJ_WORDS)
    scrambled_pol_pred = {w: compose_word_with_override_polarity(
        w, REAL_LEXICON, REAL_POS_POOL, REAL_NEG_POOL, scramble_map) for w in FRESH_NOUNADJ_WORDS}
    random_gloss_pred = {}
    for idx, w in enumerate(FRESH_NOUNADJ_WORDS):
        k = len(definition_content_words(w)[2])
        rand_content = _random_content_for(w, k, idx)
        random_gloss_pred[w] = compose_word(w, REAL_LEXICON, REAL_POS_POOL, REAL_NEG_POOL,
                                             content_override=rand_content)
    scrambled_feature_pred = {w: compose_word(w, SCRAMBLED_LEXICON, SCRAMBLED_POS_POOL,
                                               SCRAMBLED_NEG_POOL) for w in FRESH_NOUNADJ_WORDS}

    scores_real = score_arm(real_pred, FRESH_NOUNADJ_GOLD, FRESH_NOUNADJ_WORDS)
    scores_scr_pol = score_arm(scrambled_pol_pred, FRESH_NOUNADJ_GOLD, FRESH_NOUNADJ_WORDS)
    scores_random_gloss = score_arm(random_gloss_pred, FRESH_NOUNADJ_GOLD, FRESH_NOUNADJ_WORDS)
    scores_scr_feature = score_arm(scrambled_feature_pred, FRESH_NOUNADJ_GOLD, FRESH_NOUNADJ_WORDS)

    glass_box = {w: {
        "gold": FRESH_NOUNADJ_GOLD[w], "pos_used": real_pred[w]["pos_used"],
        "gloss": real_pred[w]["gloss"], "content_words": real_pred[w]["content_words"],
        "hits": real_pred[w]["hits"], "composed_tags": real_pred[w]["composed_tags"],
        "prediction": real_pred[w]["prediction"],
        "correct": real_pred[w]["prediction"] == FRESH_NOUNADJ_GOLD[w],
    } for w in FRESH_NOUNADJ_WORDS}

    return {
        "words": FRESH_NOUNADJ_WORDS, "gold": FRESH_NOUNADJ_GOLD,
        "n_banned_pool": len(BANNED_NOUNADJ),
        "REAL": scores_real,
        "SCRAMBLE_polarity": scores_scr_pol,
        "scramble_collapse_delta_acc_overall": round(
            scores_real["acc_overall"] - scores_scr_pol["acc_overall"], 4),
        "scramble_collapse_delta_acc_when_fires": (
            round(scores_real["acc_when_fires"] - scores_scr_pol["acc_when_fires"], 4)
            if scores_real["acc_when_fires"] is not None and scores_scr_pol["acc_when_fires"] is not None
            else None),
        "MUST_FAIL_random_gloss": scores_random_gloss,
        "MUST_FAIL_random_gloss_underperforms_real": (
            scores_random_gloss["acc_overall"] < scores_real["acc_overall"]
            or scores_random_gloss["fires_pct"] < scores_real["fires_pct"]),
        "MUST_FAIL_scrambled_feature": scores_scr_feature,
        "MUST_FAIL_scrambled_feature_underperforms_real": (
            scores_scr_feature["acc_overall"] < scores_real["acc_overall"]
            or scores_scr_feature["fires_pct"] < scores_real["fires_pct"]),
        "glass_box": glass_box,
    }


# =================================================================================================
# PART 3: downstream narrative substitution -- identify OOV referents/verbs on INC-2's own TRAIN
# split (n=30, byte-identical import), ground them (verbs via v1 ARM-A; nouns/adjectives via
# compose_word), REGISTER into the live lexicons, re-run INC-2's OWN UNMODIFIED extract_relation_
# features()/build_episode()/grounded_rule_predict(), diff BEFORE vs AFTER, then revert.
# =================================================================================================
_STOPWORDS = v1._STOPWORDS


def _outcome_verb_candidates(outcome_text):
    toks = re.findall(r"[a-z']+", outcome_text.lower())
    cands = [t for t in toks if len(t) >= 3 and t not in _STOPWORDS]
    lemmas = sorted({lemma_verb(t) for t in cands})
    return lemmas


def identify_oov(train_raw):
    """Returns (oov_referents: set, oov_verbs: set, per_item_debug: dict) -- every referent/verb
    candidate that is OOV of the CURRENT (pre-registration) lexicons, collected across the 30
    train items. Never mutates any lexicon (read-only scan)."""
    oov_referents, oov_verbs = set(), set()
    per_item = {}
    for it in train_raw:
        feats, debug = inc2.extract_relation_features(it)
        gr, orf = debug.get("goal_referent"), debug.get("outcome_referent")
        gvl = debug.get("goal_verb_lemma")
        for ref in (gr, orf):
            if ref and not lexsim.in_lexicon(ref) and ref not in ADJ_SEED_FEATURES:
                oov_referents.add(ref)
        if gvl and not verblex.in_lexicon(gvl, "outcome"):
            oov_verbs.add(gvl)
        for lemma in _outcome_verb_candidates(it["outcome_text"]):
            if not verblex.in_lexicon(lemma, "outcome"):
                oov_verbs.add(lemma)
        per_item[it["id"]] = debug
    return oov_referents, oov_verbs, per_item


def ground_and_register(oov_referents, oov_verbs):
    """Grounds every OOV referent (compose_word, REAL lexicon) and OOV verb (v1 ARM-A). Registers
    successful grounds into the LIVE lexicons (lexsim.CONCEPT_FEATURES / verblex's Tier-3 overlay).
    Returns (referent_results, verb_results, registered_referents: list) for cleanup + reporting."""
    referent_results, verb_results = {}, {}
    registered_referents = []
    for w in sorted(oov_referents):
        comp = compose_word(w, REAL_LEXICON, REAL_POS_POOL, REAL_NEG_POOL)
        referent_results[w] = comp
        if comp["composed_tags"]:
            lexsim.CONCEPT_FEATURES[w] = frozenset(comp["composed_tags"])
            registered_referents.append(w)
    for w in sorted(oov_verbs):
        gloss, content = v1.gloss_content_words(w)
        comp = v1.compose_prediction(content, exclude_light_verbs_source_c=False)
        verb_results[w] = {"gloss": gloss, "content_words": content, "hits": comp["hits"],
                            "score": comp["score"], "prediction": comp["prediction"]}
        if comp["prediction"] is not None:
            verblex.register_acquired_outcome(w, comp["prediction"])
    return referent_results, verb_results, registered_referents


def cleanup_registrations(registered_referents):
    for w in registered_referents:
        lexsim.CONCEPT_FEATURES.pop(w, None)
    verblex.clear_acquired_outcome()


def channel_fire_counts(episodes):
    n = len(episodes)
    class_rel_fires = sum(1 for ep in episodes if ep["_feats_raw"]["class_relation"] != "none")
    verb_sim_fires = sum(1 for ep in episodes if ep["_feats_raw"]["verb_sim_bucket"] != "oov")
    ref_sim_fires = sum(1 for ep in episodes if ep["_feats_raw"]["referent_sim_bucket"] != "oov")
    ref_recur_fires = sum(1 for ep in episodes
                           if ep["_feats_raw"]["referent_recur_verdict"] in ("MET", "UNMET"))
    return {"n": n, "class_relation_fires": class_rel_fires,
            "verb_sim_bucket_fires": verb_sim_fires, "referent_sim_bucket_fires": ref_sim_fires,
            "referent_recur_verdict_fires": ref_recur_fires}


def run_downstream_measurement():
    items = load_items()
    train_raw, test_raw = stratified_split(items)
    majority = majority_class(train_raw)

    # ---- BEFORE (unmodified lexicons; reproduces INC-2's own train-split fire counts) ----------
    before_eps = [inc2.build_episode(it) for it in train_raw]
    before_fires = channel_fire_counts(before_eps)
    before_grounded_preds = [inc2.grounded_rule_predict(ep, majority) for ep in before_eps]
    before_gold = [ep["gold_class"] for ep in before_eps]
    before_grounded_acc = accuracy(before_grounded_preds, before_gold)
    before_fire_mask = [len(ep["_feats_raw"]) > 0 and (
        ep["_feats_raw"]["class_relation"] != "none"
        or ep["_feats_raw"]["verb_sim_bucket"] == "high"
        or ep["_feats_raw"]["referent_literal_match"]
        or ep["_feats_raw"]["referent_sim_bucket"] == "high"
        or ep["_feats_raw"]["referent_recur_verdict"] in ("MET", "UNMET")) for ep in before_eps]
    before_acc_when_fired = (
        round(sum(1 for p, g, f in zip(before_grounded_preds, before_gold, before_fire_mask)
                  if f and p == g) / max(sum(before_fire_mask), 1), 4)
        if any(before_fire_mask) else None)

    # ---- identify + ground + register OOV -------------------------------------------------------
    oov_referents, oov_verbs, _ = identify_oov(train_raw)
    referent_results, verb_results, registered_referents = ground_and_register(
        oov_referents, oov_verbs)
    n_referents_covered = sum(1 for r in referent_results.values() if r["hits"])
    n_referents_fired = sum(1 for r in referent_results.values() if r["prediction"] is not None
                             or r["composed_tags"])
    n_verbs_covered = sum(1 for r in verb_results.values() if r["hits"])
    n_verbs_fired = sum(1 for r in verb_results.values() if r["prediction"] is not None)

    try:
        # ---- AFTER (extended lexicons; re-runs INC-2's OWN unmodified logic) --------------------
        after_eps = [inc2.build_episode(it) for it in train_raw]
        after_fires = channel_fire_counts(after_eps)
        after_grounded_preds = [inc2.grounded_rule_predict(ep, majority) for ep in after_eps]
        after_gold = [ep["gold_class"] for ep in after_eps]
        after_grounded_acc = accuracy(after_grounded_preds, after_gold)
        after_fire_mask = [(
            ep["_feats_raw"]["class_relation"] != "none"
            or ep["_feats_raw"]["verb_sim_bucket"] == "high"
            or ep["_feats_raw"]["referent_literal_match"]
            or ep["_feats_raw"]["referent_sim_bucket"] == "high"
            or ep["_feats_raw"]["referent_recur_verdict"] in ("MET", "UNMET")) for ep in after_eps]
        after_acc_when_fired = (
            round(sum(1 for p, g, f in zip(after_grounded_preds, after_gold, after_fire_mask)
                      if f and p == g) / max(sum(after_fire_mask), 1), 4)
            if any(after_fire_mask) else None)
        after_glass_box = {ep["id"]: {
            "gold": ep["gold_class"], "class_relation": ep["_feats_raw"]["class_relation"],
            "verb_sim_bucket": ep["_feats_raw"]["verb_sim_bucket"],
            "referent_sim_bucket": ep["_feats_raw"]["referent_sim_bucket"],
            "referent_recur_verdict": ep["_feats_raw"]["referent_recur_verdict"],
            "grounded_pred": pred,
        } for ep, pred in zip(after_eps, after_grounded_preds)}
    finally:
        cleanup_registrations(registered_referents)

    return {
        "n_train": len(train_raw), "majority_class": majority,
        "oov_referents_n": len(oov_referents), "oov_verbs_n": len(oov_verbs),
        "oov_referents": sorted(oov_referents), "oov_verbs": sorted(oov_verbs),
        "referent_coverage_fire_rate": (
            round(n_referents_covered / len(oov_referents), 4) if oov_referents else None),
        "verb_coverage_fire_rate": (
            round(n_verbs_covered / len(oov_verbs), 4) if oov_verbs else None),
        "referent_composed_examples": {w: referent_results[w] for w in sorted(referent_results)[:8]},
        "verb_composed_examples": {w: verb_results[w] for w in sorted(verb_results)[:8]},
        "n_referents_registered": len(registered_referents),
        "n_verbs_registered": sum(1 for r in verb_results.values() if r["prediction"] is not None),
        "BEFORE": {
            "channel_fires": before_fires, "grounded_acc": before_grounded_acc,
            "grounded_fire_rate": round(sum(before_fire_mask) / len(before_eps), 4),
            "grounded_acc_when_fired": before_acc_when_fired,
        },
        "AFTER": {
            "channel_fires": after_fires, "grounded_acc": after_grounded_acc,
            "grounded_fire_rate": round(sum(after_fire_mask) / len(after_eps), 4),
            "grounded_acc_when_fired": after_acc_when_fired,
        },
        "delta_grounded_fire_rate": round(
            sum(after_fire_mask) / len(after_eps) - sum(before_fire_mask) / len(before_eps), 4),
        "delta_class_relation_fires": (
            after_fires["class_relation_fires"] - before_fires["class_relation_fires"]),
        "delta_verb_sim_fires": after_fires["verb_sim_bucket_fires"] - before_fires["verb_sim_bucket_fires"],
        "delta_referent_sim_fires": (
            after_fires["referent_sim_bucket_fires"] - before_fires["referent_sim_bucket_fires"]),
        "after_glass_box_sample": dict(list(after_glass_box.items())[:6]),
        "surface_plateau_citation": 0.60,
    }


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> dict:
    _assert_disjoint_fresh_nounadj()
    assert len(FRESH_NOUNADJ_WORDS) == 24, len(FRESH_NOUNADJ_WORDS)

    # determinism
    c1 = compose_word("frumpy", REAL_LEXICON, REAL_POS_POOL, REAL_NEG_POOL)
    c2 = compose_word("frumpy", REAL_LEXICON, REAL_POS_POOL, REAL_NEG_POOL)
    assert c1 == c2, "GLASS-BOX FAILURE: non-deterministic composition"

    # mechanism-fires: at least one fresh word must ground
    any_covered = any(compose_word(w, REAL_LEXICON, REAL_POS_POOL, REAL_NEG_POOL)["hits"]
                       for w in FRESH_NOUNADJ_WORDS)
    assert any_covered, "MECHANISM-FIRES FAILURE: zero fresh noun/adj words have any grounded gloss word"

    # OOV never crashes, never grounds
    assert compose_word("zzznotarealwordzzz123", REAL_LEXICON, REAL_POS_POOL, REAL_NEG_POOL
                         )["prediction"] is None

    # scramble machinery: polarity permutation changes >=1 label
    real_pred = {w: compose_word(w, REAL_LEXICON, REAL_POS_POOL, REAL_NEG_POOL)
                 for w in FRESH_NOUNADJ_WORDS}
    smap = build_polarity_scramble_map(real_pred, FRESH_NOUNADJ_WORDS)
    grounded_pols = {h["word"]: h["polarity"] for w in FRESH_NOUNADJ_WORDS
                     for h in real_pred[w]["hits"]}
    changed = any(smap[w] != grounded_pols[w] for w in smap)
    assert changed or len(smap) <= 1, "SCRAMBLE FAILURE: permutation is a no-op"

    # feature-scramble machinery: word->tag permutation actually changes >=1 word's tag-set
    tag_changed = any(SCRAMBLED_LEXICON[w] != REAL_LEXICON[w] for w in REAL_LEXICON)
    assert tag_changed, "FEATURE-SCRAMBLE FAILURE: permutation is a no-op"

    # registration round-trip leaves the live lexicons byte-identical (hygiene: no leakage across
    # runs / no accidental permanent mutation of the production dicts)
    concept_before = dict(lexsim.CONCEPT_FEATURES)
    acquired_before = dict(verblex.ACQUIRED_OUTCOME_VERB_FEATURES)
    _rr, _vr, _reg = ground_and_register({"zzz_test_referent_word_not_real"}, {"zzz_test_verb_not_real"})
    cleanup_registrations(_reg)
    assert lexsim.CONCEPT_FEATURES == concept_before, "REGISTRATION LEAK: CONCEPT_FEATURES not restored"
    assert verblex.ACQUIRED_OUTCOME_VERB_FEATURES == acquired_before, (
        "REGISTRATION LEAK: ACQUIRED_OUTCOME_VERB_FEATURES not restored")

    # reused-organ self-tests (mechanism sanity of what this cell builds on)
    lexsim_st = lexsim.self_test()
    verblex_st = verblex.self_test()
    v1_st = v1.self_test()
    retest_st = retest.self_test()

    return {
        "n_fresh_nounadj": len(FRESH_NOUNADJ_WORDS), "any_covered": any_covered,
        "scramble_machinery_changed_a_label": changed,
        "feature_scramble_machinery_changed_a_tag": tag_changed,
        "registration_round_trip_clean": True,
        "reused_organ_self_tests": {"lexsim": lexsim_st, "verblex": verblex_st, "v1": v1_st,
                                     "retest": retest_st},
    }


# =================================================================================================
# main
# =================================================================================================
def _atomic_write(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


def compute_verdict(nounadj, downstream):
    real = nounadj["REAL"]
    hard_pass_coverage = real["fires_pct"] >= 0.50 and (real["acc_when_fires"] or 0) >= 0.70
    hard_pass_scramble = nounadj["scramble_collapse_delta_acc_overall"] >= 0.30
    after_fire_rate30 = round(downstream["AFTER"]["grounded_fire_rate"] * downstream["n_train"])
    hard_pass_downstream = (after_fire_rate30 >= 10
                             and (downstream["AFTER"]["grounded_acc_when_fired"] or 0) >= 0.65
                             and downstream["AFTER"]["grounded_acc"] > 0.60)
    must_fail_ok = (nounadj["MUST_FAIL_random_gloss_underperforms_real"]
                    and nounadj["MUST_FAIL_scrambled_feature_underperforms_real"])

    if hard_pass_coverage and hard_pass_scramble and hard_pass_downstream and must_fail_ok:
        verdict = "HARD_PASS"
        msg = ("Cross-POS feature-bundle composition fires on %.0f%% of fresh noun/adj words "
               "(acc_when_fires=%.4f, scramble delta=%.4f) AND downstream fire-rate rises to "
               "%d/%d (acc_when_fired=%s) beating the 0.60 plateau -- generalizable grounding "
               "un-starves narrative typing." % (
                   real["fires_pct"] * 100, real["acc_when_fires"] or 0.0,
                   nounadj["scramble_collapse_delta_acc_overall"], after_fire_rate30,
                   downstream["n_train"], downstream["AFTER"]["grounded_acc_when_fired"]))
    elif (real["fires_pct"] < 0.50 and after_fire_rate30 < 10):
        verdict = "HARD_FAIL_COVERAGE"
        msg = ("Fresh noun/adj fire-rate=%.4f (<0.50) and downstream fire-rate stays low "
               "(%d/%d, was %d/%d before) -- the modern-vocab gloss content-words also aren't "
               "groundable from the seed; candidate/seed-coverage gap, not a mechanism ceiling."
               % (real["fires_pct"], after_fire_rate30, downstream["n_train"],
                  round(downstream["BEFORE"]["grounded_fire_rate"] * downstream["n_train"]),
                  downstream["n_train"]))
    elif (real["fires_pct"] >= 0.50 or after_fire_rate30 >= 10) and not hard_pass_downstream:
        acc_val = downstream["AFTER"]["grounded_acc_when_fired"]
        verdict = "HARD_FAIL_CORRECTNESS" if (acc_val is not None and acc_val <= 0.55) else "PARTIAL"
        msg = ("Fire-rate rises (fresh=%.4f, downstream=%d/%d) but the HARD-PASS bar is not "
               "cleared (acc_when_fires=%s fresh / %s downstream, must-fail floors ok=%s) -- "
               "coverage gain without decisive correctness, or a partial/mixed result."
               % (real["fires_pct"], after_fire_rate30, downstream["n_train"],
                  real["acc_when_fires"], acc_val, must_fail_ok))
    else:
        verdict = "PARTIAL"
        msg = "Mixed result -- see per-arm metrics for diagnosis."
    return verdict, msg, {
        "hard_pass_coverage": hard_pass_coverage, "hard_pass_scramble": hard_pass_scramble,
        "hard_pass_downstream": hard_pass_downstream, "must_fail_floors_ok": must_fail_ok,
        "after_fire_rate_30": after_fire_rate30,
    }


def main():
    st = self_test()
    print("SELF-TEST PASSED:", json.dumps({k: v for k, v in st.items()
                                            if k != "reused_organ_self_tests"}, default=str))

    nounadj = run_fresh_nounadj_measurement()
    downstream = run_downstream_measurement()
    verdict, verdict_msg, gate_detail = compute_verdict(nounadj, downstream)

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
        "gate_detail": gate_detail,
        "fresh_nounadj_measurement": nounadj,
        "downstream_narrative_measurement": downstream,
        "self_test": {k: v for k, v in st.items() if k != "reused_organ_self_tests"},
        "reused_organ_self_tests": st["reused_organ_self_tests"],
    }
    _atomic_write(OUTPUT_DIR, metrics)

    print(json.dumps({
        "verdict": verdict, "verdict_msg": verdict_msg,
        "fresh_nounadj_REAL": nounadj["REAL"],
        "fresh_nounadj_scramble_delta": nounadj["scramble_collapse_delta_acc_overall"],
        "fresh_nounadj_MUST_FAIL_random_gloss": nounadj["MUST_FAIL_random_gloss"],
        "fresh_nounadj_MUST_FAIL_scrambled_feature": nounadj["MUST_FAIL_scrambled_feature"],
        "oov_referents_n": downstream["oov_referents_n"], "oov_verbs_n": downstream["oov_verbs_n"],
        "referent_coverage_fire_rate": downstream["referent_coverage_fire_rate"],
        "verb_coverage_fire_rate": downstream["verb_coverage_fire_rate"],
        "BEFORE": downstream["BEFORE"], "AFTER": downstream["AFTER"],
        "delta_grounded_fire_rate": downstream["delta_grounded_fire_rate"],
        "delta_class_relation_fires": downstream["delta_class_relation_fires"],
        "delta_verb_sim_fires": downstream["delta_verb_sim_fires"],
        "delta_referent_sim_fires": downstream["delta_referent_sim_fires"],
    }, indent=2, default=str))
    print("METRICS WRITTEN:", os.path.join(OUTPUT_DIR, "metrics.json"))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
                "traceback": traceback.format_exc()[:5000],
                "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
        final = os.path.join(OUTPUT_DIR, "metrics.json")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(diag, f, indent=2)
        os.replace(tmp, final)
        traceback.print_exc()
        sys.exit(1)
