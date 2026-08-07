"""experiments/exp_definition_composition_grounding_probe_v1.py -- ISOLATED DIAGNOSTIC PROBE
(2026-08-07, Director task brief): does "look it up in the dictionary" (WordNet GLOSS text,
composed over already-grounded content-words) ground an out-of-vocabulary (OOV) outcome-verb's
result-VALENCE, and does it ADD coverage/accuracy beyond the existing RELATIONAL teacher
(hdlab.wordnet_polarity_propagation.dictionary_lookup, which never reads gloss text -- it only
votes over WordNet graph structure: antonym-opposition + path_similarity neighbor-vote against the
same 52-word anchor)?

HYPOTHESIS UNDER TEST: a human learns an unknown word from its DEFINITION, which reduces the
unknown word to ALREADY-KNOWN words. Formalized here as: tokenize the gloss (definition +
examples) of an OOV outcome-verb's most-frequent WordNet verb sense; for every gloss content-word
that is ALREADY GROUNDED (directly in the 52-word seed lexicon, directly in the ATL-hub noun/adj
valence lexicon, or one hop away from either via the SAME relational machinery the baseline uses),
compose a POS/NEG prediction by a confidence-weighted vote. This is DISTINCT from the baseline: the
baseline looks up the TARGET verb itself against the anchor; this probe looks up the target verb's
DEFINITION WORDS against the same (and one more) grounded resource(s), then composes.

SENSE SELECTION (principled, stated up front): sense index 0 of `wn.synsets(lemma, pos='v')` --
WordNet orders a lemma's synsets by (empirically-tagged) sense frequency, so index-0 IS "the most
frequent verb sense" by construction, not an arbitrary pick. definition() + examples() are BOTH
tokenized (a human reading a dictionary entry reads the example sentence too, not just the terse
gloss line) -- this is stated, not hidden.

GROUNDING SOURCES for a gloss content-word (three sources, precedence in this order; every one is
an ALREADY-EXISTING, ALREADY-VETTED hdlab organ -- nothing new is authored here except the glue):
  (A) hdlab.verb_lexical_similarity.OUTCOME_SEED_POS / OUTCOME_SEED_NEG (the literal ~52-word
      seed lexicon named in the task brief). depth=0, weight=1.0.
  (B) hdlab.lexical_similarity.CONCEPT_FEATURES (the 89-concept ATL-hub noun/adj shared-feature
      lexicon): (B1) the gloss word is DIRECTLY a member carrying an explicit valence-discriminating
      tag (POS_VALENCE / NEG_VALENCE / EVALUATIVE_POSITIVE -- the only such tags this lexicon
      defines; no EVALUATIVE_NEGATIVE tag exists in CONCEPT_FEATURES today, an honest coverage gap
      noted in the report). depth=0, weight=1.0. (B2) ONE HOP: the gloss word is a CONCEPT_FEATURES
      member WITHOUT an explicit valence tag, but its concept_similarity() (the module's own FHRR
      bundle-cosine, SIMILARITY_LINK_THRESHOLD=0.50, reused unmodified/un-retuned) to the NEAREST
      valence-tagged concept clears that pre-registered threshold -- inherits that concept's
      valence. depth=1, weight=cosine value.
  (C) hdlab.wordnet_polarity_propagation.dictionary_lookup(gloss_word, ANCHOR_WORDS,
      ANCHOR_POLARITY) -- the SAME relational-teacher machinery the baseline uses (antonym
      opposition then path_similarity neighbor-vote), run on the GLOSS WORD instead of the target
      verb, against the SAME primary 52-word anchor (NOT the extended 82-word anchor -- staying
      inside the "~52 words" scope the task brief names). A non-abstain result is a genuine
      one-hop WordNet-graph grounding. depth=1, weight=DictLookup.confidence (1.0 for an antonym
      hit). NOTE (honest, stated in the report): dictionary_lookup's Stage B internally restricts
      to `wn.synsets(lemma, pos=wn.VERB)` -- it can only fire for gloss words that ARE THEMSELVES
      VERBS in WordNet. Most gloss content-words are adjectives/nouns (e.g. "undesirable",
      "unusable", "imperfect", "encouragement"), so this source's reach is narrower than it looks;
      this is a real, measured coverage limiter, quantified in the report, NOT a mechanism failure.

COMPOSITION RULE (stated): score = sum over grounded gloss-words of (+weight if POS, -weight if
NEG). score > 0 -> predict POS; score < 0 -> predict NEG; score == 0 (including the
no-grounded-words case) -> abstain. "Fires" = a directional (non-abstain) prediction was produced;
"coverage" = >=1 gloss content-word was grounded at all (a strictly looser bar than "fires", since
a tied composition still counts as covered-but-abstained).

BASELINE (measured on the SAME held-out set, for comparison): hdlab.wordnet_polarity_propagation.
dictionary_lookup(verb) applied DIRECTLY to the target OOV verb (not its gloss), default 52-word
ANCHOR_WORDS/ANCHOR_POLARITY -- the existing relational teacher, wired in production.

HELD-OUT SET (task-brief-specified candidates, filtered): 10 NEG + 10 POS candidates named in the
task brief, MINUS any already present in OUTCOME_SEED_POS/OUTCOME_SEED_NEG (verified programmatically
below, not by hand -- see _assert_disjoint_from_seed). Dropped: "wreck" (OUTCOME_SEED_NEG),
"mend"/"restore"/"rescue" (OUTCOME_SEED_POS). Final: 9 NEG (spoil, squander, mar, ruin, tarnish,
sabotage, botch, deface, thwart) + 7 POS (cherish, nurture, bolster, salvage, uplift, hearten,
refine) = 16 words. GOLD is hand-labeled (unambiguous outcome-valence words, stated inline in
HELD_OUT_GOLD) -- majority class is NEG (9/16 = 0.5625), so the report gives BOTH the 0.50
balanced-chance floor AND the 0.5625 majority-class floor.

SCRAMBLE CONTROL: collect every (gloss_word -> polarity) grounding fact actually used across the
whole held-out set; build a SCRAMBLED version by permuting the polarity labels across those words
(fixed seed=999, byte-identical scramble convention to hdlab.verb_lexical_similarity.self_test /
hdlab.lexical_similarity.self_test: sorted(words), torch.randperm). Recompose every held-out verb's
prediction using the IDENTICAL set of grounded words/depths/weights but the SCRAMBLED polarity
labels. If the real mechanism is reading genuine gloss content (not just "did some words match"),
accuracy must collapse toward chance under scrambling.

hdlab-only reuse (wire-don't-island); NO hdlab/ file is edited; this is an ISOLATED, LOCAL,
non-dispatched diagnostic cell (no queue, no remote ship, no canonical-store write) per the task
brief's "isolated cell, detach-forbidden" framing.
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

from hdlab.verb_lexical_similarity import OUTCOME_SEED_POS, OUTCOME_SEED_NEG  # noqa: E402
from hdlab.lexical_similarity import (  # noqa: E402
    CONCEPT_FEATURES, concept_similarity, SIMILARITY_LINK_THRESHOLD,
)
from hdlab.wordnet_polarity_propagation import (  # noqa: E402
    dictionary_lookup, ANCHOR_WORDS, ANCHOR_POLARITY, DictLookup,
    self_test as wnpp_self_test,
)
from hdlab.lexical_similarity import self_test as lexsim_self_test  # noqa: E402
from hdlab.verb_lexical_similarity import self_test as verblex_self_test  # noqa: E402

ANCHOR_NAME = "definition_composition_grounding_probe_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

# ================================================================================================
# HELD-OUT SET -- gold hand-labeled, unambiguous outcome-valence verbs.
# ================================================================================================
CANDIDATE_NEG = ["spoil", "squander", "mar", "wreck", "ruin", "tarnish", "sabotage", "botch",
                 "deface", "thwart"]
CANDIDATE_POS = ["cherish", "mend", "restore", "nurture", "bolster", "rescue", "salvage", "uplift",
                  "hearten", "refine"]


def _assert_disjoint_from_seed():
    """Programmatically drop (and report) any candidate already present in the ~52-word seed
    lexicon (OUTCOME_SEED_POS/NEG) -- the task brief's explicit fair-test guard. Returns
    (final_neg, final_pos, dropped)."""
    seed_all = set(OUTCOME_SEED_POS) | set(OUTCOME_SEED_NEG)
    dropped = [w for w in CANDIDATE_NEG if w in seed_all] + [w for w in CANDIDATE_POS if w in seed_all]
    final_neg = [w for w in CANDIDATE_NEG if w not in seed_all]
    final_pos = [w for w in CANDIDATE_POS if w not in seed_all]
    return final_neg, final_pos, dropped


HELD_OUT_NEG, HELD_OUT_POS, DROPPED_SEED_MEMBERS = _assert_disjoint_from_seed()
HELD_OUT_GOLD = {w: "NEG" for w in HELD_OUT_NEG}
HELD_OUT_GOLD.update({w: "POS" for w in HELD_OUT_POS})
HELD_OUT_WORDS = sorted(HELD_OUT_GOLD)

# ================================================================================================
# tokenization / stopwords (hand-authored, offline -- nltk 'stopwords' corpus is not installed in
# this environment; a short closed-class function-word list is the standard Lesk-style substitute
# and is stated here, not hidden).
# ================================================================================================
_STOPWORDS = frozenset("""
a an the of to and or in on at by for with from as is are was were be been being do does did
this that these those it its it's his her their our your my he she they we you i not no nor so
than then thus which who whom whose what when where why how all any some such into onto over
under again further once here there very can will would should could may might must shall
also used use up down out off if but each own same too more most other another one two used
having has have had them him me us
""".split())


def gloss_content_words(word: str, sense_index: int = 0):
    """(gloss_text, [content_words]) for `word`'s sense-index-th verb synset (most-frequent sense
    by WordNet's own sense-frequency ordering, index 0). gloss_text = definition() + ' ' +
    ' '.join(examples()) -- both are read, matching how a human reads a dictionary entry. Returns
    (None, []) if `word` has no WordNet verb sense at all. Content words = alphabetic tokens,
    lowercased, length>=3, not in _STOPWORDS, and not equal to `word` itself (avoid trivial
    self-reference)."""
    syns = wn.synsets(word, pos=wn.VERB)
    if not syns:
        return None, []
    syn = syns[sense_index] if sense_index < len(syns) else syns[0]
    gloss = syn.definition() + " " + " ".join(syn.examples())
    toks = re.findall(r"[a-zA-Z]+", gloss.lower())
    content = [t for t in toks if len(t) >= 3 and t not in _STOPWORDS and t != word]
    return gloss, content


# ================================================================================================
# grounding sources (A/B/C), precedence A > B > C (first hit wins; each is independently correct,
# precedence only matters for the reported "source" tag, not for the composition score).
# ================================================================================================
def _atl_hub_valence(w: str):
    """(B) ATL-hub CONCEPT_FEATURES grounding. Returns (polarity, depth, weight, source) or None.
    B1: w directly tagged POS_VALENCE/NEG_VALENCE/EVALUATIVE_POSITIVE -> depth 0, weight 1.0.
    B2 (one hop): w is a CONCEPT_FEATURES member without an explicit valence tag; its nearest
    valence-tagged-concept cosine (SIMILARITY_LINK_THRESHOLD, reused un-retuned) grounds it,
    depth 1, weight = that cosine."""
    if w not in CONCEPT_FEATURES:
        return None
    tags = CONCEPT_FEATURES[w]
    if "POS_VALENCE" in tags or "EVALUATIVE_POSITIVE" in tags:
        return ("POS", 0, 1.0, "atl_hub_direct")
    if "NEG_VALENCE" in tags or "EVALUATIVE_NEGATIVE" in tags:
        return ("NEG", 0, 1.0, "atl_hub_direct")
    # B2: one-hop cosine to the nearest explicitly valence-tagged concept.
    best_sim, best_pol = -2.0, None
    for other, other_tags in CONCEPT_FEATURES.items():
        if other == w:
            continue
        if "POS_VALENCE" in other_tags or "EVALUATIVE_POSITIVE" in other_tags:
            pol = "POS"
        elif "NEG_VALENCE" in other_tags or "EVALUATIVE_NEGATIVE" in other_tags:
            pol = "NEG"
        else:
            continue
        sim = concept_similarity(w, other)
        if sim is not None and sim > best_sim:
            best_sim, best_pol = sim, pol
    if best_pol is not None and best_sim >= SIMILARITY_LINK_THRESHOLD:
        return (best_pol, 1, float(best_sim), "atl_hub_cosine_hop")
    return None


_ground_cache: dict = {}
_ground_cache_no_light: dict = {}

# POST-HOC DIAGNOSTIC ABLATION ONLY (not part of the primary pre-specified composition rule; added
# AFTER the primary run below surfaced its driver -- see run_probe's "diagnostic_ablation" section
# and the completion report for the honest disclosure that this list was written in response to an
# observed failure mode, not chosen blind). The standard closed class of English "light"/support
# verbs (Jespersen 1954 do/give/have/make/take, commonly extended with get/go/become/put/use) that
# carry near-zero lexical content of their own and appear as dictionary-gloss boilerplate ("make
# imperfect", "make dirty", "give encouragement to") -- WordNet path_similarity's neighbor-vote
# (Source C, Stage B) can weakly and spuriously link these to an anchor by graph-structure
# coincidence, not genuine shared meaning. This list is the SAME standard closed class the
# already-vetted exp_wordnet_verbid_earn_from_exposure_v1.py cell down-weights for the identical
# reason (its verb_selectional_weight LIGHT/LOADED split), reused here as a UNIFORM filter (not
# tuned per test item) restricted to Source C only (Sources A/B are hand-curated closed lexicons
# with no light-verb noise problem).
LIGHT_VERB_STOPLIST = frozenset({
    "make", "made", "makes", "making", "get", "gets", "got", "getting", "give", "gives", "gave",
    "giving", "do", "does", "did", "doing", "go", "goes", "went", "going", "take", "takes", "took",
    "taking", "become", "becomes", "became", "becoming", "have", "has", "had", "having", "put",
    "puts", "putting", "use", "uses", "used", "using",
})


def ground_gloss_word(w: str, exclude_light_verbs_source_c: bool = False):
    """The single choke-point grounding function applied uniformly to every gloss content-word,
    regardless of which target verb's gloss it came from (no leakage: this function only ever
    consults the 52-word seed lexicon / ATL-hub lexicon / WordNet-anchor relational lookup -- NEVER
    the held-out gold labels). Returns (polarity, depth, weight, source) or None (ungroundable).
    `exclude_light_verbs_source_c`: POST-HOC DIAGNOSTIC ABLATION toggle (see LIGHT_VERB_STOPLIST
    docstring) -- False reproduces the PRIMARY pre-specified composition rule exactly."""
    cache = _ground_cache_no_light if exclude_light_verbs_source_c else _ground_cache
    if w in cache:
        return cache[w]
    result = None
    # (A) direct seed-lexicon membership.
    if w in OUTCOME_SEED_POS:
        result = ("POS", 0, 1.0, "outcome_seed")
    elif w in OUTCOME_SEED_NEG:
        result = ("NEG", 0, 1.0, "outcome_seed")
    else:
        # (B) ATL-hub (direct or one-hop cosine).
        result = _atl_hub_valence(w)
        if result is None and not (exclude_light_verbs_source_c and w in LIGHT_VERB_STOPLIST):
            # (C) one-hop relational lookup of the GLOSS WORD ITSELF against the primary anchor.
            lu: DictLookup = dictionary_lookup(w, ANCHOR_WORDS, ANCHOR_POLARITY)
            if lu.polarity is not None:
                result = (lu.polarity, 1, float(lu.confidence) if lu.confidence > 0 else 1.0,
                          "wordnet_anchor_hop")
    cache[w] = result
    return result


# ================================================================================================
# composition
# ================================================================================================
def compose_prediction(content_words, polarity_override: dict = None,
                        exclude_light_verbs_source_c: bool = False):
    """polarity_override: optional {word: "POS"/"NEG"} used only by the SCRAMBLE control (keeps the
    exact same grounded-word set / depths / weights, swaps only the polarity label).
    exclude_light_verbs_source_c: POST-HOC DIAGNOSTIC ABLATION toggle, see LIGHT_VERB_STOPLIST.
    Returns dict with prediction (POS/NEG/None), score, and the list of (word, polarity, depth,
    weight, source) hits actually used (glass-box)."""
    hits = []
    score = 0.0
    for w in content_words:
        g = ground_gloss_word(w, exclude_light_verbs_source_c=exclude_light_verbs_source_c)
        if g is None:
            continue
        polarity, depth, weight, source = g
        if polarity_override is not None:
            polarity = polarity_override.get(w, polarity)
        hits.append({"word": w, "polarity": polarity, "depth": depth,
                     "weight": round(weight, 4), "source": source})
        score += weight if polarity == "POS" else -weight
    if score > 0:
        pred = "POS"
    elif score < 0:
        pred = "NEG"
    else:
        pred = None
    return {"prediction": pred, "score": round(score, 4), "hits": hits}


# ================================================================================================
# scramble control -- byte-identical convention to hdlab.verb_lexical_similarity.self_test /
# hdlab.lexical_similarity.self_test (sorted(words), torch.Generator().manual_seed(999), randperm).
# ================================================================================================
SCRAMBLE_SEED = 999


def build_scramble_map(grounded_words):
    words = sorted(grounded_words)
    if not words:
        return {}
    polarities = [ground_gloss_word(w)[0] for w in words]
    gen = torch.Generator().manual_seed(SCRAMBLE_SEED)
    perm = torch.randperm(len(words), generator=gen).tolist()
    return {words[i]: polarities[perm[i]] for i in range(len(words))}


# ================================================================================================
# main measurement
# ================================================================================================
def run_probe():
    per_word = {}
    glossary = {}
    all_grounded_words = set()

    for w in HELD_OUT_WORDS:
        gloss, content = gloss_content_words(w)
        glossary[w] = {"gloss": gloss, "content_words": content}
        comp = compose_prediction(content)
        per_word[w] = comp
        for h in comp["hits"]:
            all_grounded_words.add(h["word"])

    # ---- scramble control -------------------------------------------------------------------
    scramble_map = build_scramble_map(all_grounded_words)
    per_word_scrambled = {}
    for w in HELD_OUT_WORDS:
        content = glossary[w]["content_words"]
        comp = compose_prediction(content, polarity_override=scramble_map)
        per_word_scrambled[w] = comp

    # ---- POST-HOC DIAGNOSTIC ABLATION: exclude the standard light-verb closed class from Source C
    # only (see LIGHT_VERB_STOPLIST docstring -- added after the primary run above surfaced "make"
    # repeatedly spuriously grounding POS via WordNet path_similarity coincidence and cancelling
    # real NEG signal from "destroy"/"damage" in botch/spoil/tarnish/mar). Kept STRICTLY SEPARATE
    # from the primary composition/scramble numbers above.
    per_word_noLV = {}
    all_grounded_words_noLV = set()
    for w in HELD_OUT_WORDS:
        content = glossary[w]["content_words"]
        comp = compose_prediction(content, exclude_light_verbs_source_c=True)
        per_word_noLV[w] = comp
        for h in comp["hits"]:
            all_grounded_words_noLV.add(h["word"])
    words_noLV = sorted(all_grounded_words_noLV)
    if words_noLV:
        pols_noLV = [ground_gloss_word(w, exclude_light_verbs_source_c=True)[0] for w in words_noLV]
        gen = torch.Generator().manual_seed(SCRAMBLE_SEED)
        perm = torch.randperm(len(words_noLV), generator=gen).tolist()
        scramble_map_noLV = {words_noLV[i]: pols_noLV[perm[i]] for i in range(len(words_noLV))}
    else:
        scramble_map_noLV = {}
    per_word_noLV_scrambled = {}
    for w in HELD_OUT_WORDS:
        content = glossary[w]["content_words"]
        comp = compose_prediction(content, polarity_override=scramble_map_noLV,
                                   exclude_light_verbs_source_c=True)
        per_word_noLV_scrambled[w] = comp

    # ---- baseline: relational teacher applied directly to the TARGET verb -------------------
    baseline = {w: dictionary_lookup(w) for w in HELD_OUT_WORDS}

    # ---- scoring ------------------------------------------------------------------------------
    def score_composition(pred_dict):
        n = len(HELD_OUT_GOLD)
        n_covered = sum(1 for w in HELD_OUT_WORDS if len(pred_dict[w]["hits"]) > 0)
        n_fires = sum(1 for w in HELD_OUT_WORDS if pred_dict[w]["prediction"] is not None)
        n_correct_when_fires = sum(
            1 for w in HELD_OUT_WORDS
            if pred_dict[w]["prediction"] is not None and pred_dict[w]["prediction"] == HELD_OUT_GOLD[w])
        n_correct_overall = sum(
            1 for w in HELD_OUT_WORDS if pred_dict[w]["prediction"] == HELD_OUT_GOLD[w])
        return {
            "n": n, "coverage": n_covered, "coverage_pct": round(n_covered / n, 4),
            "fires": n_fires, "fires_pct": round(n_fires / n, 4),
            "acc_when_fires": round(n_correct_when_fires / n_fires, 4) if n_fires else None,
            "acc_overall": round(n_correct_overall / n, 4),
            "n_correct_overall": n_correct_overall, "n_correct_when_fires": n_correct_when_fires,
        }

    def score_baseline(lu_dict):
        n = len(HELD_OUT_GOLD)
        n_covered = sum(1 for w in HELD_OUT_WORDS if lu_dict[w].stage != "abstain")
        n_fires = sum(1 for w in HELD_OUT_WORDS if lu_dict[w].polarity is not None)
        n_correct_when_fires = sum(
            1 for w in HELD_OUT_WORDS
            if lu_dict[w].polarity is not None and lu_dict[w].polarity == HELD_OUT_GOLD[w])
        n_correct_overall = sum(
            1 for w in HELD_OUT_WORDS if lu_dict[w].polarity == HELD_OUT_GOLD[w])
        return {
            "n": n, "coverage": n_covered, "coverage_pct": round(n_covered / n, 4),
            "fires": n_fires, "fires_pct": round(n_fires / n, 4),
            "acc_when_fires": round(n_correct_when_fires / n_fires, 4) if n_fires else None,
            "acc_overall": round(n_correct_overall / n, 4),
            "n_correct_overall": n_correct_overall, "n_correct_when_fires": n_correct_when_fires,
        }

    composition_scores = score_composition(per_word)
    scrambled_scores = score_composition(per_word_scrambled)
    baseline_scores = score_baseline(baseline)
    ablation_scores = score_composition(per_word_noLV)
    ablation_scrambled_scores = score_composition(per_word_noLV_scrambled)

    # ---- overlap diagnosis: which held-out verbs does composition cover that the baseline MISSES
    # (fires), and vice versa -- the "does this ADD coverage the relational path misses" question.
    comp_fires_set = {w for w in HELD_OUT_WORDS if per_word[w]["prediction"] is not None}
    base_fires_set = {w for w in HELD_OUT_WORDS if baseline[w].polarity is not None}
    comp_only = sorted(comp_fires_set - base_fires_set)
    base_only = sorted(base_fires_set - comp_fires_set)
    both = sorted(comp_fires_set & base_fires_set)
    neither = sorted(set(HELD_OUT_WORDS) - comp_fires_set - base_fires_set)

    # ---- depth-1-vs-depth-2 diagnosis for the "no grounded word at depth 1" misses: for every
    # held-out verb with ZERO grounded gloss content-words (composition did not cover it at all),
    # check whether ANY of ITS gloss words would themselves ground if we recursed one level deeper
    # (i.e. whether the FIRST-DEGREE gloss word's OWN gloss contains a grounded word) -- quantifies
    # "would deeper recursion help" honestly rather than asserting it.
    depth2_rescue = {}
    for w in HELD_OUT_WORDS:
        if len(per_word[w]["hits"]) > 0:
            continue  # already covered at depth<=1, not a miss
        content = glossary[w]["content_words"]
        rescued_via = []
        for cw in content:
            _, cw_content = gloss_content_words(cw)
            for cw2 in cw_content:
                g = ground_gloss_word(cw2)
                if g is not None:
                    rescued_via.append({"gloss_word": cw, "grounds_via": cw2, "polarity": g[0]})
        depth2_rescue[w] = rescued_via

    n_zero_coverage = sum(1 for w in HELD_OUT_WORDS if len(per_word[w]["hits"]) == 0)
    n_zero_coverage_depth2_rescuable = sum(
        1 for w in HELD_OUT_WORDS if len(per_word[w]["hits"]) == 0 and len(depth2_rescue[w]) > 0)

    # ---- glass-box examples (report a representative spread: covered+correct, covered+wrong,
    # not-covered, baseline-miss-composition-hit) ------------------------------------------------
    glass_box_examples = {}
    for w in HELD_OUT_WORDS:
        glass_box_examples[w] = {
            "gold": HELD_OUT_GOLD[w],
            "gloss": glossary[w]["gloss"],
            "content_words": glossary[w]["content_words"],
            "grounded_hits": per_word[w]["hits"],
            "composition_score": per_word[w]["score"],
            "composition_prediction": per_word[w]["prediction"],
            "composition_correct": per_word[w]["prediction"] == HELD_OUT_GOLD[w],
            "baseline_prediction": baseline[w].polarity,
            "baseline_stage": baseline[w].stage,
            "baseline_confidence": round(baseline[w].confidence, 4),
            "baseline_correct": baseline[w].polarity == HELD_OUT_GOLD[w],
        }

    # ---- self-test (mechanism sanity, run every invocation) ------------------------------------
    self_test_result = self_test()

    metrics = {
        "verdict": "MEASURED",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "hypothesis": "definition-gloss composition over already-grounded content-words can ground "
                       "an OOV outcome-verb's result-valence",
        "sense_selection": "wn.synsets(word, pos='v')[0] (most-frequent WordNet verb sense); "
                            "definition()+examples() both tokenized",
        "grounding_depth": "A=seed direct(0); B1=ATL-hub direct(0); B2=ATL-hub one-hop cosine(1); "
                            "C=wordnet_polarity_propagation.dictionary_lookup one-hop on the gloss "
                            "word itself(1). No depth>=2 grounding is used in the primary composition "
                            "(depth-2 is measured SEPARATELY below as a what-if diagnosis only).",
        "composition_rule": "score = sum(+weight if POS else -weight over every grounded gloss "
                             "content-word); sign(score) -> prediction; score==0 -> abstain",
        "chance_floor_balanced": 0.5,
        "chance_floor_majority_class": round(
            max(len(HELD_OUT_NEG), len(HELD_OUT_POS)) / len(HELD_OUT_WORDS), 4),
        "held_out_set": {
            "n_total": len(HELD_OUT_WORDS), "n_neg": len(HELD_OUT_NEG), "n_pos": len(HELD_OUT_POS),
            "words": HELD_OUT_WORDS, "gold": HELD_OUT_GOLD,
            "dropped_already_in_seed_lexicon": DROPPED_SEED_MEMBERS,
        },
        "composition": composition_scores,
        "composition_scrambled": scrambled_scores,
        "scramble_collapse_delta_acc_overall": round(
            composition_scores["acc_overall"] - scrambled_scores["acc_overall"], 4),
        "scramble_collapse_delta_acc_when_fires": (
            round(composition_scores["acc_when_fires"] - scrambled_scores["acc_when_fires"], 4)
            if composition_scores["acc_when_fires"] is not None
               and scrambled_scores["acc_when_fires"] is not None else None),
        "baseline_relational_teacher": baseline_scores,
        "coverage_delta_composition_minus_baseline": round(
            composition_scores["coverage_pct"] - baseline_scores["coverage_pct"], 4),
        "post_hoc_diagnostic_ablation_light_verb_filtered_source_c": {
            "disclosure": "NOT the primary pre-specified composition rule. Added AFTER the primary "
                           "run (above) surfaced that generic light verbs ('make' etc.) in gloss "
                           "boilerplate spuriously ground via Source C's WordNet path_similarity "
                           "neighbor-vote and cancel real signal. Tests whether that specific, named "
                           "composition-rule flaw (not gloss-composition-in-general) is the driver. "
                           "Needs a FRESH held-out set to confirm as a generalizable fix rather than "
                           "post-hoc curve-fitting to these 16 items.",
            "light_verb_stoplist": sorted(LIGHT_VERB_STOPLIST),
            "composition": ablation_scores,
            "composition_scrambled": ablation_scrambled_scores,
            "scramble_collapse_delta_acc_overall": round(
                ablation_scores["acc_overall"] - ablation_scrambled_scores["acc_overall"], 4),
        },
        "fires_overlap": {
            "both_fire": both, "composition_only_fires": comp_only,
            "baseline_only_fires": base_only, "neither_fires": neither,
            "n_composition_only": len(comp_only), "n_baseline_only": len(base_only),
        },
        "depth2_recursion_diagnosis": {
            "n_zero_coverage_at_depth<=1": n_zero_coverage,
            "n_of_those_rescuable_at_depth2": n_zero_coverage_depth2_rescuable,
            "detail": depth2_rescue,
        },
        "glass_box_examples": glass_box_examples,
        "self_test": self_test_result,
        "reused_organ_self_tests": {
            "wordnet_polarity_propagation_self_test": wnpp_self_test(),
            "lexical_similarity_self_test": lexsim_self_test(),
            "verb_lexical_similarity_self_test": verblex_self_test(),
        },
    }
    return metrics


# ================================================================================================
# self-test: coverage sanity, determinism, scramble-machinery sanity, OOV-never-crashes.
# ================================================================================================
def self_test() -> dict:
    # (1) held-out set truly disjoint from the seed lexicon (the fair-test guard the task brief
    # requires -- programmatic, not by-hand).
    seed_all = set(OUTCOME_SEED_POS) | set(OUTCOME_SEED_NEG)
    for w in HELD_OUT_WORDS:
        assert w not in seed_all, f"HELD-OUT LEAKAGE: {w!r} is in the seed lexicon"
    assert len(HELD_OUT_WORDS) == 16, f"expected 16 held-out words after filtering, got " \
                                       f"{len(HELD_OUT_WORDS)}: {HELD_OUT_WORDS}"

    # (2) grounding function never crashes on a nonsense token, never grounds it.
    assert ground_gloss_word("zzznotarealwordzzz") is None

    # (3) determinism: same word -> byte-identical gloss/content-words/grounding twice.
    g1 = gloss_content_words("spoil")
    g2 = gloss_content_words("spoil")
    assert g1 == g2, "GLASS-BOX FAILURE: non-deterministic gloss extraction"
    c1 = compose_prediction(g1[1])
    c2 = compose_prediction(g1[1])
    assert c1 == c2, "GLASS-BOX FAILURE: non-deterministic composition"

    # (4) mechanism-fires: at least one held-out verb must be COVERED (>=1 grounded gloss word) --
    # if this is ever 0, the whole probe is vacuous and must not report a verdict.
    any_covered = any(len(compose_prediction(gloss_content_words(w)[1])["hits"]) > 0
                       for w in HELD_OUT_WORDS)
    assert any_covered, "MECHANISM-FIRES FAILURE: zero held-out verbs have any grounded gloss word"

    # (5) scramble machinery: with a FIXED seed, scrambling actually changes at least one grounded
    # word's polarity label somewhere in the held-out set's gloss content (else the scramble control
    # is a no-op and cannot demonstrate anything).
    all_words = set()
    for w in HELD_OUT_WORDS:
        for h in compose_prediction(gloss_content_words(w)[1])["hits"]:
            all_words.add(h["word"])
    smap = build_scramble_map(all_words)
    changed = any(smap[w] != ground_gloss_word(w)[0] for w in smap)
    assert changed or len(smap) <= 1, "SCRAMBLE FAILURE: permutation did not change any label " \
                                       "(degenerate for len>1)"

    # (6) ATL-hub one-hop cosine grounding is reachable in principle (mechanism smoke, not a
    # held-out-set claim): "smart" (EVALUATIVE_POSITIVE, depth 0) must ground POS directly.
    g_smart = ground_gloss_word("smart")
    assert g_smart is not None and g_smart[0] == "POS", "ATL-hub direct valence grounding broken"

    # (7) baseline machinery: dictionary_lookup is deterministic and never crashes on the held-out
    # set (already self-tested upstream, re-verified here at the call-site).
    for w in HELD_OUT_WORDS:
        lu1 = dictionary_lookup(w)
        lu2 = dictionary_lookup(w)
        assert lu1 == lu2, f"GLASS-BOX FAILURE: non-deterministic baseline lookup for {w!r}"

    return {
        "n_held_out": len(HELD_OUT_WORDS), "n_dropped_seed_members": len(DROPPED_SEED_MEMBERS),
        "any_covered": any_covered, "scramble_machinery_changed_a_label": changed,
        "atl_hub_direct_smoke_ok": True,
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
        metrics = run_probe()
        _atomic_write(OUTPUT_DIR, metrics)
        print(json.dumps({
            "coverage_pct": metrics["composition"]["coverage_pct"],
            "fires_pct": metrics["composition"]["fires_pct"],
            "acc_when_fires": metrics["composition"]["acc_when_fires"],
            "acc_overall": metrics["composition"]["acc_overall"],
            "scrambled_acc_overall": metrics["composition_scrambled"]["acc_overall"],
            "scramble_collapse_delta": metrics["scramble_collapse_delta_acc_overall"],
            "baseline_coverage_pct": metrics["baseline_relational_teacher"]["coverage_pct"],
            "baseline_acc_overall": metrics["baseline_relational_teacher"]["acc_overall"],
            "n_composition_only_fires": metrics["fires_overlap"]["n_composition_only"],
            "n_baseline_only_fires": metrics["fires_overlap"]["n_baseline_only"],
            "ABLATION_light_verb_filtered": {
                "coverage_pct": metrics["post_hoc_diagnostic_ablation_light_verb_filtered_source_c"]
                ["composition"]["coverage_pct"],
                "acc_when_fires": metrics["post_hoc_diagnostic_ablation_light_verb_filtered_source_c"]
                ["composition"]["acc_when_fires"],
                "acc_overall": metrics["post_hoc_diagnostic_ablation_light_verb_filtered_source_c"]
                ["composition"]["acc_overall"],
                "scramble_collapse_delta": metrics[
                    "post_hoc_diagnostic_ablation_light_verb_filtered_source_c"][
                    "scramble_collapse_delta_acc_overall"],
            },
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
