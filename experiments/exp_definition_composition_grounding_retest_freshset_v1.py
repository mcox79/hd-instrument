"""experiments/exp_definition_composition_grounding_retest_freshset_v1.py -- ISOLATED, LOCAL,
non-dispatched re-test (2026-08-07, Director task brief: "TEST-FIRST validation re-test").

WHY THIS RE-TEST EXISTS: experiments/exp_definition_composition_grounding_probe_v1.py (commit
9907cc8e2, VET'd 2026-08-07 per e64dac0fb) found definition-gloss composition is a real ADDITIVE
grounding channel over the relational baseline (coverage 62.5% vs 18.75%, scramble collapses), but
its accuracy fix -- filtering generic light-verb gloss boilerplate ("make"/"give"/etc, which
spuriously grounds via WordNet Source-C path_similarity and cancels real valence signal) -- was
POST-HOC: written AFTER seeing the primary run's failure mode, then measured on the SAME 16 items
it was tuned against (lifted acc-when-fires 1/2 -> 8/8 on that identical set). Post-hoc-on-the-
same-data is indistinguishable from curve-fitting until re-measured on FRESH, disjoint data with the
fix FROZEN BEFORE the run. That is what this file does. NOTHING about the composition rule, the
grounding sources, or the light-verb stoplist is touched here -- every one of those is IMPORTED
UNMODIFIED from the v1 probe module (wire-don't-island; zero re-implementation risk of silently
drifting from what was actually validated before).

PRE-REGISTRATION (frozen BEFORE this file was run; see the task brief this docstring paraphrases):
  1. Sense selection: wn.synsets(word,'v')[0].definition()+examples(), tokenized. UNCHANGED from v1
     (v1.gloss_content_words, imported verbatim).
  2. Composition rule: signed weighted sum over grounded gloss content-words; sign->prediction;
     0->abstain. UNCHANGED from v1 (v1.compose_prediction, imported verbatim).
  3. LIGHT-VERB FILTER (the thing under test): v1.LIGHT_VERB_STOPLIST, the SAME frozen closed class
     {make, do, give, get, have, take, put, keep, let, cause, become, come, go, set, turn, bring,
     hold, be/is/are, ...}, imported verbatim, NOT edited, NOT re-tuned after seeing this file's
     results.
  4. Grounding sources = v1's: OUTCOME_SEED_POS/NEG (A), CONCEPT_FEATURES ATL-hub direct+one-hop-
     cosine at SIMILARITY_LINK_THRESHOLD=0.50 (B), wordnet_polarity_propagation.dictionary_lookup
     one-hop on the gloss word (C). Imported verbatim via v1.ground_gloss_word / v1.compose_prediction
     -- this file authors ZERO new grounding logic for the ARM A/B primary claim.

THE FRESH HELD-OUT SET (the load-bearing fairness point -- see FRESH_NEG/FRESH_POS below for the
full selection-method writeup, disjointness proof, and gold-labeling method). 28 words (14 NEG +
14 POS), drawn SYSTEMATICALLY from WordNet hyponym trees under four result-verb hypernym roots
(destroy.v.01, damage.v.01, improve.v.01, construct.v.01) -- NOT hand-picked to flatter the filter.
Programmatically verified disjoint from (a) OUTCOME_SEED_POS/NEG (the ~52-word seed anchor),
(b) OUTCOME_HELDOUT_POS/NEG (the ~32-word extended-anchor set, a bonus stricter guard beyond what
the task brief required), and (c) the v1 probe's own 16 held-out words (imported from v1.HELD_OUT_
WORDS, not re-typed, so this can never silently drift out of sync with what "the probe's 16 verbs"
actually were).

ARMS (all measured on the fresh set):
  ARM A = composition WITHOUT the light-verb filter (v1's PRIMARY-pre-fix rule; exclude_light_
          verbs_source_c=False). Reproduces exactly what the original probe's primary run measured,
          just on fresh data.
  ARM B = composition WITH the pre-registered light-verb filter (exclude_light_verbs_source_c=True).
          THE CLAIM UNDER TEST: does ARM B's acc-when-fires generalize (~>=0.8) on fresh data, or
          was the 8/8-on-16-items result curve-fit?
  Relational baseline = wordnet_polarity_propagation.dictionary_lookup(verb) applied directly to the
          target verb (imported verbatim, default ANCHOR_WORDS/ANCHOR_POLARITY -- the wired
          production teacher).
  Scramble control on ARM B = permute (gloss_word -> polarity) grounding facts collected under the
          ARM-B (filtered) grounding function, fixed seed=999, byte-identical convention to v1
          (sorted(words), torch.Generator().manual_seed(999), randperm). Recompose every held-out
          verb's ARM-B prediction using the IDENTICAL grounded-word set but scrambled labels.
  ARM A scramble = same control applied to ARM A, reported for completeness (not required by the
          brief but free to compute and informative).
  ARM C (SECONDARY / EXPLORATORY, clearly separated, measures COVERAGE GAIN ONLY, does NOT
         contaminate the ARM-B primary claim; only run because ARM A/B land cleanly, see report) =
         ARM B's grounding PLUS a small supplied adjective-valence seed (18 words, 9 POS/9 NEG,
         stated below as ADJ_SEED_POS/NEG) propagated ONE HOP via WordNet adjective antonyms and
         similar_to() satellite-cluster links (the idiomatic WordNet relations for adjectives --
         path_similarity, which the verb baseline uses, is not meaningful for the adjective
         satellite-cluster graph shape, so a different but equally standard WordNet relation is
         used, stated honestly here rather than silently reusing a verb-shaped tool on the wrong
         data structure). This targets the task brief's named gap: glosses lean on evaluative
         adjectives ("undesirable", "unpleasant", ...) that NONE of Source A/B/C's existing
         resources cover (verified below: zero of a spot-check of 21 common evaluative adjectives,
         including "undesirable"/"fond"/"attached" from the brief, are members of CONCEPT_FEATURES).

hdlab-only reuse for the grounding mechanism (wire-don't-island); the only NEW code in this file is
(1) the fresh-set constants + their disjointness proof, (2) generic scoring/scrambling glue
identical in spirit to v1's (re-typed here only because v1's scoring helpers are closures private to
v1.run_probe(), not because the SCORING RULE differs), and (3) the ARM-C adjective-seed extension,
which is explicitly exploratory and walled off from the primary claim. No hdlab/ file is edited.
Isolated, local, non-dispatched diagnostic cell per the task brief's "isolated cell, detach-
forbidden" framing.
"""
from __future__ import annotations

import json
import os
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

# ---- REUSE v1's exact mechanism (grounding sources, composition rule, light-verb filter) --------
import exp_definition_composition_grounding_probe_v1 as v1  # noqa: E402

from hdlab.verb_lexical_similarity import (  # noqa: E402
    OUTCOME_SEED_POS, OUTCOME_SEED_NEG, OUTCOME_HELDOUT_POS, OUTCOME_HELDOUT_NEG,
)
from hdlab.wordnet_polarity_propagation import dictionary_lookup  # noqa: E402
from hdlab.lexical_similarity import CONCEPT_FEATURES  # noqa: E402

ANCHOR_NAME = "definition_composition_grounding_retest_freshset_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

# ================================================================================================
# FRESH HELD-OUT SET -- selection method (stated, not hidden):
# Drew from wn.synsets(<root>).hyponyms() closure to depth 3, for four standard result-verb
# hypernym roots (2 destructive, 2 constructive/ameliorative): destroy.v.01, damage.v.01 (NEG
# roots); improve.v.01, construct.v.01 (POS roots). Extracted single-word (no underscore) verb
# lemmas from every hyponym synset's lemma set, filtered to those NOT already in OUTCOME_SEED_POS/
# NEG, OUTCOME_HELDOUT_POS/NEG, or v1.HELD_OUT_WORDS (programmatic disjointness -- see
# _assert_disjoint_fresh below). From that filtered pool, hand-selected words meeting TWO
# transparent bars (both applied uniformly, not per-outcome-tuned): (i) wn.synsets(word,'v')[0]
# ITSELF (the sense this whole mechanism reads) must denote the intended, unambiguous-valence
# meaning -- WordNet's frequency-based sense-0 ordering occasionally surfaces an unrelated/neutral
# sense for a word whose common usage is unambiguous (e.g. "rejuvenate" sense-0 is a geology sense
# about river erosion, not "make young again"; "reconstruct" sense-0 is "reassemble mentally", not
# physical rebuilding; "scorch"/"blacken"/"smash"/"mangle"/"maul"/"rectify"/"redevelop" sense-0
# definitions were similarly a wrong-sense or valence-neutral literal reading on inspection --
# EXCLUDED, not cherry-picked to a later sense, since the protocol locks sense_index=0); (ii) the
# resulting valence is unambiguous common-English usage (same "unambiguous outcome-valence words"
# bar v1's own 16-word set used). This is a real, disclosed exclusion step -- honesty requires
# stating it plainly: of ~35+45+124+15 = ~219 raw hyponym-tree candidates (pre-seed-filter), most
# were excluded either as too obscure/archaic (bilge, swinge, corduroy, wattle, groin), as
# duplicate-root morphology, or as failing bar (i)/(ii) above -- the final 28 is NOT "first 28
# alphabetically" or similar unmotivated slice, it is a hand-vetted subset of a systematically-drawn
# pool, and every sense-0 definition is printed in this docstring's development record (see the
# task's completion report) so the vetting is auditable, not asserted.
# ================================================================================================
FRESH_NEG = [
    "demolish", "eradicate", "exterminate", "obliterate", "disfigure", "mutilate", "corrode",
    "corrupt", "sully", "taint", "blight", "blemish", "bruise", "impair",
]
FRESH_POS = [
    "beautify", "alleviate", "cure", "enhance", "enrich", "polish", "perfect", "purify",
    "revitalize", "upgrade", "erect", "rebuild", "fortify", "renovate",
]


def _assert_disjoint_fresh():
    """Programmatic disjointness proof: fresh set vs (a) OUTCOME_SEED_POS/NEG, (b)
    OUTCOME_HELDOUT_POS/NEG (bonus, stricter than the brief required), (c) v1.HELD_OUT_WORDS (the
    probe's own 16, imported -- never re-typed, so this can't silently drift). Raises (crashes the
    cell honestly) on any violation rather than silently dropping -- this fresh set was hand-built
    to already be clean, so a violation here would mean a bug in this file, not an expected-drop
    case (unlike v1's _assert_disjoint_from_seed, which DOES expect drops from its task-brief-given
    candidate list)."""
    banned = (set(OUTCOME_SEED_POS) | set(OUTCOME_SEED_NEG) | set(OUTCOME_HELDOUT_POS)
              | set(OUTCOME_HELDOUT_NEG) | set(v1.HELD_OUT_WORDS))
    all_fresh = set(FRESH_NEG) | set(FRESH_POS)
    violations = sorted(all_fresh & banned)
    assert not violations, f"FRESH-SET LEAKAGE: {violations} already present in seed/heldout/v1 sets"
    assert len(set(FRESH_NEG) & set(FRESH_POS)) == 0, "NEG/POS overlap in fresh set"
    assert len(FRESH_NEG) + len(FRESH_POS) >= 24, "fresh set below the pre-registered n>=24 floor"
    return banned


BANNED_WORDS = _assert_disjoint_fresh()
FRESH_GOLD = {w: "NEG" for w in FRESH_NEG}
FRESH_GOLD.update({w: "POS" for w in FRESH_POS})
FRESH_WORDS = sorted(FRESH_GOLD)

SCRAMBLE_SEED = v1.SCRAMBLE_SEED  # identical convention (999), imported not re-typed


# ================================================================================================
# ARM C (exploratory only) -- small supplied adjective-valence seed + one-hop WordNet adjective
# antonym / similar_to propagation. INVARIANT-OK DATA (a small hand-labeled lexicon, same class of
# artifact as OUTCOME_SEED_POS/NEG itself), NOT a new grounding MECHANISM class beyond
# antonym-opposition + neighbor-link that Sources B/C already use -- just applied to the adjective
# POS instead of verb/noun, because verb path_similarity (Source C's relation) is not the idiomatic
# WordNet relation for the adjective satellite-cluster graph shape (adjectives mostly do not form
# is-a hierarchies the way nouns/verbs do; similar_to is the standard substitute relation).
# ================================================================================================
ADJ_SEED_POS = frozenset({
    "good", "beautiful", "healthy", "pleasant", "useful", "clean", "strong", "pure", "kind",
})
ADJ_SEED_NEG = frozenset({
    "bad", "ugly", "unhealthy", "unpleasant", "useless", "dirty", "weak", "foul", "harsh",
})

_adj_ground_cache: dict = {}


def ground_adjective(w: str):
    """(polarity, depth, weight, source) or None. Direct seed (depth0) -> antonym-of-seed
    (depth1, opposite polarity) -> similar_to-neighbor-of-seed (depth1, same polarity). Deterministic,
    cached. Never consults held-out gold labels."""
    if w in _adj_ground_cache:
        return _adj_ground_cache[w]
    result = None
    if w in ADJ_SEED_POS:
        result = ("POS", 0, 1.0, "adj_seed_direct")
    elif w in ADJ_SEED_NEG:
        result = ("NEG", 0, 1.0, "adj_seed_direct")
    else:
        adj_syns = wn.synsets(w, pos=wn.ADJ) + wn.synsets(w, pos=wn.ADJ_SAT)
        if adj_syns:
            ants = set()
            for syn in adj_syns:
                for lem in syn.lemmas():
                    for ant in lem.antonyms():
                        ants.add(ant.name().replace("_", " ").lower())
            hit_pos, hit_neg = ants & ADJ_SEED_POS, ants & ADJ_SEED_NEG
            if hit_pos and not hit_neg:
                result = ("NEG", 1, 1.0, "adj_antonym")
            elif hit_neg and not hit_pos:
                result = ("POS", 1, 1.0, "adj_antonym")
            else:
                neighbors = set()
                for syn in adj_syns:
                    for sim_syn in syn.similar_tos():
                        for lem in sim_syn.lemmas():
                            neighbors.add(lem.name().replace("_", " ").lower())
                nb_pos, nb_neg = neighbors & ADJ_SEED_POS, neighbors & ADJ_SEED_NEG
                if nb_pos and not nb_neg:
                    result = ("POS", 1, 1.0, "adj_similar_to")
                elif nb_neg and not nb_pos:
                    result = ("NEG", 1, 1.0, "adj_similar_to")
    _adj_ground_cache[w] = result
    return result


def ground_gloss_word_arm_c(w: str):
    """ARM C's grounding choke-point: ARM B's exact grounding (light-verb-filtered) first, THEN
    (only if ARM B found nothing) the adjective-seed extension. Never overrides an ARM-B hit."""
    g = v1.ground_gloss_word(w, exclude_light_verbs_source_c=True)
    if g is not None:
        return g
    return ground_adjective(w)


def compose_prediction_arm_c(content_words):
    hits = []
    score = 0.0
    for w in content_words:
        g = ground_gloss_word_arm_c(w)
        if g is None:
            continue
        polarity, depth, weight, source = g
        hits.append({"word": w, "polarity": polarity, "depth": depth, "weight": round(weight, 4),
                     "source": source})
        score += weight if polarity == "POS" else -weight
    pred = "POS" if score > 0 else ("NEG" if score < 0 else None)
    return {"prediction": pred, "score": round(score, 4), "hits": hits}


# ================================================================================================
# generic scoring (re-typed from v1's private closures -- same scoring RULE, just not importable
# since v1 defines these inside run_probe()).
# ================================================================================================
def score_composition(pred_dict, gold, words):
    n = len(gold)
    n_covered = sum(1 for w in words if len(pred_dict[w]["hits"]) > 0)
    n_fires = sum(1 for w in words if pred_dict[w]["prediction"] is not None)
    n_correct_when_fires = sum(1 for w in words if pred_dict[w]["prediction"] is not None
                                and pred_dict[w]["prediction"] == gold[w])
    n_correct_overall = sum(1 for w in words if pred_dict[w]["prediction"] == gold[w])
    return {
        "n": n, "coverage": n_covered, "coverage_pct": round(n_covered / n, 4),
        "fires": n_fires, "fires_pct": round(n_fires / n, 4),
        "acc_when_fires": round(n_correct_when_fires / n_fires, 4) if n_fires else None,
        "acc_overall": round(n_correct_overall / n, 4),
        "n_correct_overall": n_correct_overall, "n_correct_when_fires": n_correct_when_fires,
    }


def score_baseline(lu_dict, gold, words):
    n = len(gold)
    n_covered = sum(1 for w in words if lu_dict[w].stage != "abstain")
    n_fires = sum(1 for w in words if lu_dict[w].polarity is not None)
    n_correct_when_fires = sum(1 for w in words if lu_dict[w].polarity is not None
                                and lu_dict[w].polarity == gold[w])
    n_correct_overall = sum(1 for w in words if lu_dict[w].polarity == gold[w])
    return {
        "n": n, "coverage": n_covered, "coverage_pct": round(n_covered / n, 4),
        "fires": n_fires, "fires_pct": round(n_fires / n, 4),
        "acc_when_fires": round(n_correct_when_fires / n_fires, 4) if n_fires else None,
        "acc_overall": round(n_correct_overall / n, 4),
        "n_correct_overall": n_correct_overall, "n_correct_when_fires": n_correct_when_fires,
    }


def build_scramble_map_for(grounded_words, exclude_light_verbs_source_c: bool):
    """Byte-identical convention to v1.build_scramble_map (sorted(words), seed 999, randperm), but
    generalized to respect the ARM (filtered vs unfiltered) polarity lookup used to build the map's
    source labels -- v1.build_scramble_map always used the unfiltered lookup, which is correct ONLY
    for ARM A; ARM B's scramble must scramble ARM-B's OWN polarities (v1 handled this identically
    for its own ablation-scramble, inline in run_probe() -- reproduced here as a named helper)."""
    words = sorted(grounded_words)
    if not words:
        return {}
    polarities = [v1.ground_gloss_word(w, exclude_light_verbs_source_c=exclude_light_verbs_source_c)[0]
                  for w in words]
    gen = torch.Generator().manual_seed(SCRAMBLE_SEED)
    perm = torch.randperm(len(words), generator=gen).tolist()
    return {words[i]: polarities[perm[i]] for i in range(len(words))}


# ================================================================================================
# main measurement
# ================================================================================================
def run_retest():
    glossary = {}
    per_word_A, per_word_B = {}, {}
    grounded_A, grounded_B = set(), set()

    for w in FRESH_WORDS:
        gloss, content = v1.gloss_content_words(w)
        glossary[w] = {"gloss": gloss, "content_words": content}
        comp_A = v1.compose_prediction(content, exclude_light_verbs_source_c=False)
        comp_B = v1.compose_prediction(content, exclude_light_verbs_source_c=True)
        per_word_A[w] = comp_A
        per_word_B[w] = comp_B
        for h in comp_A["hits"]:
            grounded_A.add(h["word"])
        for h in comp_B["hits"]:
            grounded_B.add(h["word"])

    # ---- scramble controls (ARM B primary, ARM A informational) -------------------------------
    scramble_map_B = build_scramble_map_for(grounded_B, exclude_light_verbs_source_c=True)
    scramble_map_A = build_scramble_map_for(grounded_A, exclude_light_verbs_source_c=False)
    per_word_B_scrambled, per_word_A_scrambled = {}, {}
    for w in FRESH_WORDS:
        content = glossary[w]["content_words"]
        per_word_B_scrambled[w] = v1.compose_prediction(
            content, polarity_override=scramble_map_B, exclude_light_verbs_source_c=True)
        per_word_A_scrambled[w] = v1.compose_prediction(
            content, polarity_override=scramble_map_A, exclude_light_verbs_source_c=False)

    # ---- relational baseline (target verb itself, default primary anchor) ---------------------
    baseline = {w: dictionary_lookup(w) for w in FRESH_WORDS}

    # ---- ARM C (exploratory, coverage-gain-only measurement) -----------------------------------
    per_word_C = {}
    for w in FRESH_WORDS:
        per_word_C[w] = compose_prediction_arm_c(glossary[w]["content_words"])
    zero_cov_B = {w for w in FRESH_WORDS if len(per_word_B[w]["hits"]) == 0}
    zero_cov_C = {w for w in FRESH_WORDS if len(per_word_C[w]["hits"]) == 0}
    arm_c_rescued = sorted(zero_cov_B - zero_cov_C)

    # ---- scoring --------------------------------------------------------------------------------
    scores_A = score_composition(per_word_A, FRESH_GOLD, FRESH_WORDS)
    scores_B = score_composition(per_word_B, FRESH_GOLD, FRESH_WORDS)
    scores_A_scr = score_composition(per_word_A_scrambled, FRESH_GOLD, FRESH_WORDS)
    scores_B_scr = score_composition(per_word_B_scrambled, FRESH_GOLD, FRESH_WORDS)
    scores_baseline = score_baseline(baseline, FRESH_GOLD, FRESH_WORDS)
    scores_C = score_composition(per_word_C, FRESH_GOLD, FRESH_WORDS)

    # ---- overlap diagnosis (ARM B vs baseline, matches v1's framing) --------------------------
    b_fires = {w for w in FRESH_WORDS if per_word_B[w]["prediction"] is not None}
    base_fires = {w for w in FRESH_WORDS if baseline[w].polarity is not None}
    b_only = sorted(b_fires - base_fires)
    base_only = sorted(base_fires - b_fires)
    both = sorted(b_fires & base_fires)
    neither = sorted(set(FRESH_WORDS) - b_fires - base_fires)

    # ---- glass-box per-word record (every word; report picks a representative subset) ----------
    glass_box = {}
    for w in FRESH_WORDS:
        glass_box[w] = {
            "gold": FRESH_GOLD[w],
            "gloss": glossary[w]["gloss"],
            "content_words": glossary[w]["content_words"],
            "arm_A_hits": per_word_A[w]["hits"], "arm_A_score": per_word_A[w]["score"],
            "arm_A_prediction": per_word_A[w]["prediction"],
            "arm_A_correct": per_word_A[w]["prediction"] == FRESH_GOLD[w],
            "arm_B_hits": per_word_B[w]["hits"], "arm_B_score": per_word_B[w]["score"],
            "arm_B_prediction": per_word_B[w]["prediction"],
            "arm_B_correct": per_word_B[w]["prediction"] == FRESH_GOLD[w],
            "baseline_prediction": baseline[w].polarity, "baseline_stage": baseline[w].stage,
            "baseline_correct": baseline[w].polarity == FRESH_GOLD[w],
            "arm_C_hits": per_word_C[w]["hits"], "arm_C_prediction": per_word_C[w]["prediction"],
        }

    self_test_result = self_test()

    metrics = {
        "verdict": "MEASURED",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "prior_probe_commit": "9907cc8e2",
        "hypothesis": "the pre-registered light-verb filter (ARM B) GENERALIZES beyond the "
                       "16-item set it was post-hoc fit against, i.e. is not a curve-fit",
        "pre_registration": {
            "sense_selection": "wn.synsets(word,'v')[0] definition()+examples(), tokenized "
                                "(v1.gloss_content_words, imported verbatim, unmodified)",
            "composition_rule": "signed weighted sum over grounded gloss content-words; "
                                 "sign->prediction; 0->abstain (v1.compose_prediction, imported "
                                 "verbatim, unmodified)",
            "light_verb_stoplist": sorted(v1.LIGHT_VERB_STOPLIST),
            "grounding_sources": "A=OUTCOME_SEED_POS/NEG direct; B1/B2=CONCEPT_FEATURES ATL-hub "
                                  "direct/one-hop-cosine(thr=0.50); C=wordnet_polarity_propagation."
                                  "dictionary_lookup one-hop on the gloss word (v1.ground_gloss_word, "
                                  "imported verbatim, unmodified)",
            "frozen_before_run": True,
        },
        "fresh_held_out_set": {
            "n_total": len(FRESH_WORDS), "n_neg": len(FRESH_NEG), "n_pos": len(FRESH_POS),
            "words": FRESH_WORDS, "gold": FRESH_GOLD,
            "selection_method": "systematic WordNet hyponym-tree draw under 4 result-verb hypernym "
                                 "roots (destroy.v.01, damage.v.01 -> NEG; improve.v.01, "
                                 "construct.v.01 -> POS), depth<=3, single-word verb lemmas, "
                                 "hand-vetted for (i) sense-0 denoting the intended unambiguous-"
                                 "valence meaning and (ii) unambiguous common-usage valence -- full "
                                 "writeup in this file's module docstring",
            "disjoint_from": ["OUTCOME_SEED_POS", "OUTCOME_SEED_NEG", "OUTCOME_HELDOUT_POS",
                               "OUTCOME_HELDOUT_NEG", "v1.HELD_OUT_WORDS (the probe's 16)"],
            "n_banned_pool": len(BANNED_WORDS),
            "chance_floor_balanced": 0.5,
            "chance_floor_majority_class": round(max(len(FRESH_NEG), len(FRESH_POS))
                                                  / len(FRESH_WORDS), 4),
        },
        "ARM_A_no_light_verb_filter": scores_A,
        "ARM_A_scrambled": scores_A_scr,
        "ARM_A_scramble_collapse_delta_acc_overall": round(
            scores_A["acc_overall"] - scores_A_scr["acc_overall"], 4),
        "ARM_B_light_verb_filter_PRIMARY_CLAIM": scores_B,
        "ARM_B_scrambled": scores_B_scr,
        "ARM_B_scramble_collapse_delta_acc_overall": round(
            scores_B["acc_overall"] - scores_B_scr["acc_overall"], 4),
        "ARM_B_scramble_collapse_delta_acc_when_fires": (
            round(scores_B["acc_when_fires"] - scores_B_scr["acc_when_fires"], 4)
            if scores_B["acc_when_fires"] is not None and scores_B_scr["acc_when_fires"] is not None
            else None),
        "relational_baseline": scores_baseline,
        "coverage_delta_ARM_B_minus_baseline": round(
            scores_B["coverage_pct"] - scores_baseline["coverage_pct"], 4),
        "fires_overlap_ARM_B_vs_baseline": {
            "both_fire": both, "ARM_B_only_fires": b_only, "baseline_only_fires": base_only,
            "neither_fires": neither, "n_ARM_B_only": len(b_only), "n_baseline_only": len(base_only),
        },
        "ARM_C_exploratory_adjective_extension": {
            "disclosure": "SECONDARY/EXPLORATORY. Adds a small supplied 18-word adjective-valence "
                           "seed (ADJ_SEED_POS/NEG) propagated one-hop via WordNet adjective "
                           "antonyms/similar_to, ON TOP OF ARM B. Reported for COVERAGE GAIN ONLY "
                           "per the pre-reg -- its accuracy numbers are informational, NOT used to "
                           "validate the ARM-B primary claim.",
            "adj_seed_pos": sorted(ADJ_SEED_POS), "adj_seed_neg": sorted(ADJ_SEED_NEG),
            "coverage_gain_n_words_rescued_from_zero": len(arm_c_rescued),
            "coverage_gain_words": arm_c_rescued,
            "composition_informational_only": scores_C,
        },
        "evaluative_adjective_gap_spotcheck": {
            "words_checked": sorted(["undesirable", "fond", "attached", "unusable", "imperfect",
                                      "encouragement", "unpleasant", "harmful", "beneficial",
                                      "desirable", "pleasant", "good", "bad", "strong", "weak",
                                      "healthy", "pure", "clean", "dirty", "beautiful", "ugly"]),
            "n_in_CONCEPT_FEATURES": sum(
                1 for w in ["undesirable", "fond", "attached", "unusable", "imperfect",
                            "encouragement", "unpleasant", "harmful", "beneficial", "desirable",
                            "pleasant", "good", "bad", "strong", "weak", "healthy", "pure", "clean",
                            "dirty", "beautiful", "ugly"] if w in CONCEPT_FEATURES),
        },
        "glass_box": glass_box,
        "self_test": self_test_result,
        "reused_organ_self_tests": {
            "wordnet_polarity_propagation_self_test": v1.wnpp_self_test(),
            "lexical_similarity_self_test": v1.lexsim_self_test(),
            "verb_lexical_similarity_self_test": v1.verblex_self_test(),
            "v1_probe_self_test": v1.self_test(),
        },
    }
    return metrics


# ================================================================================================
# self-test: fresh-set disjointness, determinism, scramble-machinery sanity, ARM-C smoke, no-crash.
# ================================================================================================
def self_test() -> dict:
    # (1) disjointness re-verified at call time (already asserted at import time; re-check here too
    # so a metrics-consumer can trust the reported self_test block on its own).
    banned = _assert_disjoint_fresh()
    assert len(FRESH_WORDS) == 28, f"expected 28 fresh words, got {len(FRESH_WORDS)}: {FRESH_WORDS}"

    # (2) determinism: same word -> byte-identical gloss/content-words/composition across both arms.
    g1 = v1.gloss_content_words("demolish")
    g2 = v1.gloss_content_words("demolish")
    assert g1 == g2, "GLASS-BOX FAILURE: non-deterministic gloss extraction"
    cA1 = v1.compose_prediction(g1[1], exclude_light_verbs_source_c=False)
    cA2 = v1.compose_prediction(g1[1], exclude_light_verbs_source_c=False)
    assert cA1 == cA2, "GLASS-BOX FAILURE: non-deterministic ARM-A composition"
    cB1 = v1.compose_prediction(g1[1], exclude_light_verbs_source_c=True)
    cB2 = v1.compose_prediction(g1[1], exclude_light_verbs_source_c=True)
    assert cB1 == cB2, "GLASS-BOX FAILURE: non-deterministic ARM-B composition"

    # (3) mechanism-fires: at least one fresh word must be covered under ARM A AND under ARM B (if
    # ARM B were 0, the filter would have zeroed out the whole channel -- must not happen silently).
    any_covered_A = any(len(v1.compose_prediction(v1.gloss_content_words(w)[1],
                                                    exclude_light_verbs_source_c=False)["hits"]) > 0
                         for w in FRESH_WORDS)
    any_covered_B = any(len(v1.compose_prediction(v1.gloss_content_words(w)[1],
                                                    exclude_light_verbs_source_c=True)["hits"]) > 0
                         for w in FRESH_WORDS)
    assert any_covered_A, "MECHANISM-FIRES FAILURE: ARM A has zero coverage on the fresh set"
    assert any_covered_B, "MECHANISM-FIRES FAILURE: ARM B has zero coverage on the fresh set"

    # (4) scramble machinery: fixed seed actually changes >=1 grounded word's polarity label for
    # BOTH arms (else the scramble control is a no-op).
    grounded_B = set()
    for w in FRESH_WORDS:
        for h in v1.compose_prediction(v1.gloss_content_words(w)[1],
                                        exclude_light_verbs_source_c=True)["hits"]:
            grounded_B.add(h["word"])
    smap_B = build_scramble_map_for(grounded_B, exclude_light_verbs_source_c=True)
    changed_B = any(smap_B[w] != v1.ground_gloss_word(w, exclude_light_verbs_source_c=True)[0]
                     for w in smap_B)
    assert changed_B or len(smap_B) <= 1, "SCRAMBLE FAILURE (ARM B): permutation is a no-op"

    # (5) ARM-C mechanism smoke: the adjective seed grounds directly, and antonym propagation works
    # one hop (e.g. "unclean" is a WordNet antonym-adjacent/derivationally-related form of "clean" --
    # use a guaranteed-safe direct-seed smoke instead of relying on a specific antonym existing).
    assert ground_adjective("good") == ("POS", 0, 1.0, "adj_seed_direct")
    assert ground_adjective("bad") == ("NEG", 0, 1.0, "adj_seed_direct")
    assert ground_adjective("zzznotarealadjzzz") is None

    # (6) baseline machinery determinism (re-verified at this call-site).
    for w in FRESH_WORDS:
        lu1 = dictionary_lookup(w)
        lu2 = dictionary_lookup(w)
        assert lu1 == lu2, f"GLASS-BOX FAILURE: non-deterministic baseline lookup for {w!r}"

    return {
        "n_fresh": len(FRESH_WORDS), "n_banned_pool": len(banned),
        "any_covered_ARM_A": any_covered_A, "any_covered_ARM_B": any_covered_B,
        "scramble_machinery_changed_a_label_ARM_B": changed_B,
        "arm_c_adjective_smoke_ok": True,
    }


def _atomic_write(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


def main():
    try:
        st = self_test()
        print("SELF-TEST PASSED:", json.dumps(st))
        metrics = run_retest()
        _atomic_write(OUTPUT_DIR, metrics)
        print(json.dumps({
            "fresh_set_n": metrics["fresh_held_out_set"]["n_total"],
            "ARM_A": {"coverage_pct": metrics["ARM_A_no_light_verb_filter"]["coverage_pct"],
                      "acc_when_fires": metrics["ARM_A_no_light_verb_filter"]["acc_when_fires"],
                      "acc_overall": metrics["ARM_A_no_light_verb_filter"]["acc_overall"],
                      "scramble_collapse": metrics["ARM_A_scramble_collapse_delta_acc_overall"]},
            "ARM_B_PRIMARY": {"coverage_pct": metrics["ARM_B_light_verb_filter_PRIMARY_CLAIM"]["coverage_pct"],
                              "acc_when_fires": metrics["ARM_B_light_verb_filter_PRIMARY_CLAIM"]["acc_when_fires"],
                              "acc_overall": metrics["ARM_B_light_verb_filter_PRIMARY_CLAIM"]["acc_overall"],
                              "scramble_collapse": metrics["ARM_B_scramble_collapse_delta_acc_overall"]},
            "baseline": {"coverage_pct": metrics["relational_baseline"]["coverage_pct"],
                        "acc_overall": metrics["relational_baseline"]["acc_overall"]},
            "ARM_C_coverage_gain": metrics["ARM_C_exploratory_adjective_extension"][
                "coverage_gain_n_words_rescued_from_zero"],
        }, indent=2))
        print("METRICS WRITTEN:", os.path.join(OUTPUT_DIR, "metrics.json"))
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 -- record + re-raise-as-diagnostic, never swallow
        diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
                "traceback": traceback.format_exc()[:5000],
                "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
        final = os.path.join(OUTPUT_DIR, "metrics.json")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(diag, f, indent=2)
        os.replace(tmp, final)
        raise


if __name__ == "__main__":
    main()
