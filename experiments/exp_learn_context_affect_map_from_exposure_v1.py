# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: real-learned-vs-scramble-learned final-predicted-sense digest over the 28
#   ambiguous held-out TEST items MUST differ pairwise (asserted per-seed in aggregate_and_verdict,
#   META_RULE_AF).
# - final_metrics_atomicity: tmp_replace (write metrics.json.tmp then os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no swept capacity dimension; this cell proves a LEARNING mechanism (attribute story
#   consequence -> confirm-gate -> write superposition entry), not a capacity envelope -- the VSA
#   layer runs bundle-of-<=2 word_maps at N_DIM_WORD=1024, same regime as Stage 2 (see that cell's
#   own CAPACITY NOTE; unchanged here, just fed a learned instead of hand-taught sense per class).
# - baseline_in_band: n/a (no chance-level negative-control arm; SCRAMBLE-CONSEQUENCE is the
#   can-fail negative control here, gated on its own lift band, not a 0.5-chance floor).
# - discriminator survives scale: full-N == smoke-N item/story set (fixed); only theta-training
#   steps would differ between smoke/full per the Stage-2 template, but this cell does not carry a
#   bonus theta witness (out of scope for the task brief's gates) so smoke and full are IDENTICAL
#   runs of the SAME fixed corpus -- the discriminator (learned vs scramble collapse) is exercised
#   in full at smoke time, not a reduced regime.
# - cardinality_ok: EXPECTED_N_SEEDS=5; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if fewer land.
# - per-unit failure-class instrumentation (no bare except; per-seed crash recorded).
# - calibration_check: default_ok_for_this_regime (bands fixed BEFORE this cell was run per the task
#   brief's own gate spec: learned held-out>=0.75, lift-over-scramble>=0.15, both noise sub-arms
#   abstain, spoil-reversed holds -- not tuned after seeing results; consequence-template wording was
#   iterated ONLY against hdlab.goal_typing's OWN reading contract via a pre-authoring probe script,
#   never against this cell's gate outcome).
# - deterministic_seeding: torch.Generator per seed for VSA atoms (context-class role vectors + per-
#   (word,sense) fillers); scramble permutation via random.Random(fixed int seed), reusing Stage 2's
#   own _scrambled_teaching_table helper verbatim (PROT-023, not builtin hash()); animacy lookups are
#   themselves deterministic (WordNet first-noun-sense), no RNG; consequence-template selection per
#   occurrence is INDEX-CYCLED (deterministic), no RNG at all -- fully reproducible without seeding.
# - cell_chunked: true (per-seed unit via tools/exp_checkpoint.py).
# - LOCAL ONLY, ISOLATED PROBE: no queue dispatch, no remote ship, no canonical-store write, no
#   hdlab/ edits -- prove-architecture experiment cell (Stage 4 of notes/PLAN_B_grounding_word_
#   context_affect_superposition_map_2026-08-07.md), not production wiring.
# - all reported numbers MEASURED@ tagged in the completion report, not this file.
"""experiments/exp_learn_context_affect_map_from_exposure_v1.py -- ISOLATED prove-architecture probe
for notes/PLAN_B_grounding_word_context_affect_superposition_map_2026-08-07.md STAGE 4: LEARN the
word -> context -> affect superposition map FROM EXPOSURE (stories-with-consequences) instead of
hand-teaching it. This is the CRUX cell for the A-steer/self-improving-reader North Star: the map
must be EARNED by reading a story's own shown consequence, not supplied by a labeled-example table.

THE MECHANISM (glass-box, brain-foundational: reward-prediction-error-style learning from experienced
consequence, gated by a confirm-across-occurrences anti-drift rule):
  For a word W used in a context C (an "He <verb-past> the <patient-noun>." sentence, patient animacy
  = the SAME owned context-key feature Stage 2 used, hdlab.animacy_lexicon.lookup_animacy), followed
  by a SEPARATE consequence sentence, this cell:
    1. READS the consequence's valence via hdlab.goal_typing.congruence_with_lexicon_fallback
       (imported, not reimplemented -- the SAME production outcome-reading organ named in the task
       brief; MET/UNMET/NA -- for these 2-sentence stories the goal-congruence tiers all abstain (no
       antecedent desiderative-goal clause in sentence 1), so the call falls through to that same
       function's own lexicon tier -- STILL the production function's own contract, not a bypass;
       verified empirically for every template used here, see PRE-AUTHORING VERIFICATION below).
    2. VOTES: MET -> +1, UNMET -> -1, anything else (NA/AMBIGUOUS/NONE) -> 0, one vote per exposure.
    3. GATES: aggregates the votes per (word, context_class) pair into a signed margin per candidate
       sense (mean_vote for the RECIPROCITY-pole candidate, -mean_vote for the BLOCK_HIGH-pole
       candidate) and calls hdlab.self_improving_loop.decide_keep_or_revert (imported, not
       reimplemented) with ABSTAIN_BAND_DEFAULT -- the SAME confirm-across-occurrences anti-drift
       controller already promoted for the coref self-improving loop. A pair whose aggregate margin
       does not STRICTLY clear the band writes NOTHING (abstains); only a confirmed pair contributes
       a bind(context_key, sense_vector) entry to that word's superposition bundle.
  The result is a word_map built EXACTLY the way Stage 2's teach_word_map builds one (a bundle of
  bind(context_key, sense) entries, reused hdlab.binding/hdlab.bundling/hdlab.atoms primitives,
  N_DIM_WORD=1024) -- the ONLY thing that changed is WHERE the (context_class -> sense) association
  came from: Stage 2 read it off a hand-labeled table; this cell READS IT OFF THE STORY via the
  outcome-reading organ + the anti-drift gate. Held-out collapse is then evaluated with Stage 2's own
  collapse_predict, on Stage 2's own held-out TEST items where they overlap (spoil/beat/strike/whip/
  crush/cherish) plus 2 new words authored the same way (grill/scald).

PRE-AUTHORING VERIFICATION (MEASURED, not assumed): every POS_CONSEQUENCE_TEMPLATE / NEG_CONSEQUENCE_
TEMPLATE / NEUTRAL_CONSEQUENCE_TEMPLATE string below was run through hdlab.goal_typing.lexicon_predict
and hdlab.goal_typing.congruence_with_lexicon_fallback (paired with every "He <verb> the <noun>."
context sentence this cell uses) in an interactive probe BEFORE this file was authored, confirming:
(a) every POS template alone -> lexicon_predict == "MET" (Tier-1 exact V2_OUTCOME_MET membership:
enjoyed/won/reached/arrived); every NEG template -> "UNMET" (Tier-1 exact V2_OUTCOME_UNMET membership:
sorry/failed/lost/calamity); every NEUTRAL template -> "NONE"; (b) every 2-sentence passage this cell
constructs (context-sentence + consequence-template) resolves via congruence_with_lexicon_fallback's
OWN fallback path (reason="abstain_fallback_to_lexicon", i.e. no goal-congruence tier fires on a bare
"He VERBed the NOUN." with no desiderative-goal clause, exactly as expected) to the SAME verdict as
the template alone -- so every "vote" this cell counts is a real, verified read of the SAME production
function the task brief names, not a guess about how it would classify these sentences.

SUPPLIED vs LEARNED (this cell's version of the line Stage 2 drew): the MENU of candidate senses per
word (WORD_SENSE_MENU, e.g. spoil -> {RUIN, PAMPER}) and which VALIDATED affect pole
(hdlab.goal_typing... no -- Stage 1's RECIPROCITY/BLOCK_HIGH) each candidate sense NAME belongs to
(SENSE_AFFECT_TYPE) are SUPPLIED (reused verbatim from Stage 2, same "dictionary" status as a WordNet
sense list). The EARNED part -- the ONLY thing this cell adds relative to Stage 2 -- is WHICH candidate
each (word, context_class) pair binds to: Stage 2 read that off a hand-labeled TRAIN_ITEMS table;
this cell reads it off the STORY's own shown consequence via the mechanism above. The consequence
TEMPLATE WORDING was authored by a human (the cell author) exactly the way a human author writes any
training corpus with a known ground truth; the LEARNING MECHANISM ITSELF never reads WORD_SENSE_MENU
or any gold_sense label when producing a vote -- it only ever calls congruence_with_lexicon_fallback
on the raw sentence text (verified above) and gates on the RESULT.

WORDS: reuses Stage 2's spoil/beat/strike/whip/crush (5 ambiguous, imported menu/sense-affect-type
verbatim) + cherish (single-sense baseline, verbatim) + 2 NEW ambiguous words (grill/scald,
inanimate=BENIGN-cooking/animate=HARM-injury, same polarity direction as beat/strike/whip/crush) --
noun pools for the 2 new words were verified against hdlab.animacy_lexicon.lookup_animacy the same
defensive way Stage 2 verifies its own (hard assert at import time; see build_words_data). `spoil`
keeps Stage 2's DELIBERATE reversed polarity (inanimate=NEG/animate=POS, opposite of the other 6
ambiguous words) -- the decisive anti-confound this cell also must pass (see CAN-FAIL GATES gate 5).

ANTI-DRIFT / NOISE ARMS (2, dedicated, decoupled from the 7-word accuracy gates so they cannot
contaminate the held-out/scramble comparison): NOISE_INCONSISTENT ("he nudged the <noun>." followed by
ALTERNATING POS/NEG consequence templates, 3-3 split, mean_vote=0.0 exactly) and NOISE_ABSENT (same
context sentences followed by NEUTRAL templates carrying no lexicon signal at all, mean_vote=0.0).
Both feed the SAME decide_keep_or_revert gate (a single-candidate agg_deltas dict); a working gate
must abstain (return None) on both -- proves the gate is a real confirm-across-occurrences filter, not
a rubber stamp that always writes.

CAN-FAIL GATES (bands fixed before running, per task brief):
  1. LEARNED-MAP HELD-OUT: mean acc over the 28 ambiguous held-out TEST items (7 words x 2 context
     classes x 2 held-out nouns each, disjoint from every noun used in the story corpus) >= 0.75,
     using word_maps LEARNED from exposure (no hand-taught sense ever written). Baseline (cherish,
     4 held-out items) separately >= 0.75 for graceful degradation.
  2. SCRAMBLE-CONSEQUENCE (decisive control): rebuild the story corpus with each of the 14 ambiguous
     (word, context_class) pairs' shown consequence-pole GLOBALLY PERMUTED (Stage 2's own
     _scrambled_teaching_table, reused verbatim, applied to POLES not sense-names) -- re-run the FULL
     learning pipeline (real reading + real gate) on this corrupted-but-still-consistent-per-pair
     corpus; held-out accuracy must COLLAPSE: lift = acc_real_learned - acc_scramble_learned >= 0.15.
  3. vs HAND-TAUGHT BASELINE (informational, not gated -- "need not equal" per task brief): Stage 2's
     own teach_word_map, called on the IDENTICAL story items (same nouns, same context_class/gold_
     sense fields, only the SUPERVISION SOURCE differs -- hand-taught reads gold_sense directly,
     learned reads the consequence text), evaluated on the SAME held-out items. Gap reported honestly.
  4. ANTI-DRIFT / NOISE: both NOISE_INCONSISTENT and NOISE_ABSENT arms must ABSTAIN (decide_keep_or_
     revert returns None) -- a word used with inconsistent/absent consequences gets NO confident
     binding written.
  5. SPOIL-REVERSED (anti-confound, reused from Stage 2's own decisive control): the LEARNED map's
     confirmed sense for spoil/inanimate must be RUIN (NEG) and for spoil/animate must be PAMPER
     (POS) -- opposite of the other 6 ambiguous words' inanimate=POS/animate=NEG pattern -- proving
     the learning attributed a WORD-SPECIFIC association from spoil's OWN stories, not a generic
     "animate -> X" rule that would get spoil backwards.

Reuses (wire-don't-island): hdlab.binding (bind/unbind), hdlab.bundling (bundle), hdlab.atoms
(make_atom_fhrr, similarity), hdlab.animacy_lexicon (lookup_animacy), hdlab.goal_typing
(congruence_with_lexicon_fallback, lexicon_predict -- the owned outcome-reading / consequence-as-
teacher organ), hdlab.self_improving_loop (decide_keep_or_revert, ABSTAIN_BAND_DEFAULT -- the owned
confirm-across-occurrences anti-drift gate), experiments.exp_word_context_affect_superposition_map_v1
(Stage 2: WORD_SENSE_MENU, SENSE_AFFECT_TYPE, VERB_PAST, NOUN_POOLS, TEST_ITEMS-equivalent
build_items pattern, teach_word_map [hand-taught comparison arm], collapse_predict [held-out eval],
_scrambled_teaching_table [scramble-control helper], N_DIM_WORD).

Cites: notes/PLAN_B_grounding_word_context_affect_superposition_map_2026-08-07.md (Stage 4, the plan
this cell tests); experiments/exp_word_context_affect_superposition_map_v1.py (Stage 2, HARD_PASS
04af969c4, superposition-map + taught-collapse mechanism this cell now LEARNS instead of hand-teaches);
hdlab/goal_typing.py (congruence_with_lexicon_fallback, the consequence-as-teacher outcome reader);
hdlab/self_improving_loop.py (decide_keep_or_revert / ABSTAIN_BAND_DEFAULT, the anti-drift gate).
"""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

ANCHOR_NAME = "learn_context_affect_map_from_exposure_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402
from hdlab import binding, bundling, atoms  # noqa: E402 (REUSE: bind/unbind/bundle/cleanup primitives)
from hdlab.animacy_lexicon import lookup_animacy  # noqa: E402 (REUSE: context-key feature extractor)
from hdlab.self_improving_loop import decide_keep_or_revert, ABSTAIN_BAND_DEFAULT  # noqa: E402 (REUSE: anti-drift gate)
from hdlab.goal_typing import congruence_with_lexicon_fallback  # noqa: E402 (REUSE: consequence-as-teacher outcome reader)
import experiments.exp_word_context_affect_superposition_map_v1 as stage2  # noqa: E402 (REUSE: Stage-2 menu/collapse machinery)

SEEDS = [0, 1, 2, 3, 4]
EXPECTED_N_SEEDS = len(SEEDS)
N_DIM_WORD = stage2.N_DIM_WORD  # project default (CLAUDE.md), same namespace as Stage 2's word layer

# ------------------------------------------------------------------------- WORDS (supplied menu, reused + 2 new)
AMBIGUOUS_WORDS_SHARED = ["spoil", "beat", "strike", "whip", "crush"]     # Stage 2, verbatim
AMBIGUOUS_WORDS_NEW = ["grill", "scald"]                                  # new, same BENIGN/HARM pattern
AMBIGUOUS_WORDS = AMBIGUOUS_WORDS_SHARED + AMBIGUOUS_WORDS_NEW
BASELINE_WORD = "cherish"                                                 # Stage 2, verbatim (single-sense)
ALL_WORDS = AMBIGUOUS_WORDS + [BASELINE_WORD]

WORD_SENSE_MENU_NEW = {
    "grill": {"inanimate": "BENIGN", "animate": "HARM"},
    "scald": {"inanimate": "BENIGN", "animate": "HARM"},
}
WORD_SENSE_MENU = dict(stage2.WORD_SENSE_MENU)   # copy, do not mutate Stage 2's global
WORD_SENSE_MENU.update(WORD_SENSE_MENU_NEW)
SENSE_AFFECT_TYPE = stage2.SENSE_AFFECT_TYPE      # read-only reuse; no new sense NAMES introduced
                                                   # (grill/scald reuse BENIGN/HARM; sense_vecs are
                                                   # keyed (word, sense_name) so no vector collision)

VERB_PAST_NEW = {"grill": "grilled", "scald": "scalded"}
VERB_PAST = dict(stage2.VERB_PAST)
VERB_PAST.update(VERB_PAST_NEW)

CANDIDATE_SENSES = {w: sorted(set(WORD_SENSE_MENU[w].values())) for w in ALL_WORDS}

# Noun pools for the 2 new words -- every noun below was checked against hdlab.animacy_lexicon.
# lookup_animacy BEFORE authoring (interactive probe; re-verified live in build_words_data() via a
# hard assert, same defensive pattern as Stage 2's build_items). Note some superficially-plausible
# picks (e.g. "pepper", "zucchini") were REJECTED during that probe: WordNet's first-noun-sense
# resolves them to an animal synset, which would have broken the intended inanimate/animate split --
# the probe caught this before authoring, not after a self-test failure.
NOUN_POOLS_NEW = {
    "grill": {"inanimate": (["onion", "carrot", "potato"], ["eggplant", "tomato"]),
              "animate":   (["suspect", "witness", "prisoner"], ["detective", "informant"])},
    "scald": {"inanimate": (["milk", "broth", "stock"], ["cream", "syrup"]),
              "animate":   (["toddler", "worker", "cook"], ["infant", "waiter"])},
}
NOUN_POOLS = dict(stage2.NOUN_POOLS)
NOUN_POOLS.update(NOUN_POOLS_NEW)

# ------------------------------------------------------------------------- consequence template bank
# PRE-AUTHORING VERIFICATION (see module docstring): every template below was run through
# hdlab.goal_typing.lexicon_predict AND through congruence_with_lexicon_fallback paired with every
# context sentence this cell constructs, confirming the exact-Tier-1 read claimed here.
POS_CONSEQUENCE_TEMPLATES = [   # lexicon_predict == "MET" (Tier-1 exact V2_OUTCOME_MET membership)
    "Everyone enjoyed the result.",
    "He won great praise for it.",
    "She reached a happy ending.",
    "They arrived at a joyful conclusion.",
]
NEG_CONSEQUENCE_TEMPLATES = [   # lexicon_predict == "UNMET" (Tier-1 exact V2_OUTCOME_UNMET membership)
    "Everyone was sorry about it.",
    "The whole thing failed badly.",
    "He lost everyone's trust.",
    "It was a complete calamity.",
]
NEUTRAL_CONSEQUENCE_TEMPLATES = [   # lexicon_predict == "NONE" (no lexicon signal at all)
    "The sun set slowly.",
    "The clock ticked on the wall.",
    "A bird flew past the window.",
    "The room stayed quiet.",
]
N_TEMPLATES_PER_NOUN = 2   # 3 train nouns x 2 templates = 6 exposures per (word, context_class) pair

# ------------------------------------------------------------------------- noise / anti-drift arms
NOISE_VERB_PAST = "nudged"
NOISE_PATIENT_NOUNS = ["man", "boy", "dog", "man", "boy", "dog"]   # all animate, cycled to 6 items
NOISE_SENTENCE1 = [f"He {NOISE_VERB_PAST} the {n}." for n in NOISE_PATIENT_NOUNS]
NOISE_SENTENCE2_INCONSISTENT = [POS_CONSEQUENCE_TEMPLATES[0], NEG_CONSEQUENCE_TEMPLATES[0]] * 3   # 3-3 split
NOISE_SENTENCE2_ABSENT = [NEUTRAL_CONSEQUENCE_TEMPLATES[i % len(NEUTRAL_CONSEQUENCE_TEMPLATES)]
                          for i in range(6)]


def _pole_of_sense(sense_name: str) -> str:
    return "POS" if SENSE_AFFECT_TYPE[sense_name] == "RECIPROCITY" else "NEG"


def _pole_sign(sense_name: str) -> float:
    return 1.0 if SENSE_AFFECT_TYPE[sense_name] == "RECIPROCITY" else -1.0


REAL_POLE_TABLE = {(w, cls): _pole_of_sense(WORD_SENSE_MENU[w][cls])
                   for w in AMBIGUOUS_WORDS for cls in ("inanimate", "animate")}


def build_words_data(pole_override=None):
    """TRAIN STORIES (word -> list of {sentence1 (context), sentence2 (consequence), context_class,
    gold_sense, true_pole, shown_pole}) + HELD-OUT TEST items (word -> list of {sentence, context_
    class, gold_sense}, disjoint nouns, no consequence -- Stage-2-shaped). `pole_override`
    ({(word,cls): "POS"/"NEG"}, default None) substitutes which consequence-template list a pair's
    stories draw from (the SCRAMBLE-CONSEQUENCE lever); it never touches gold_sense or test_items --
    the evaluation set and the ground truth are unaffected, only what a story SHOWS is corrupted, the
    exact parallel to Stage 2's own _scrambled_teaching_table lever on the taught sense-name."""
    pole_override = pole_override or {}
    train_stories = {w: [] for w in ALL_WORDS}
    test_items = {w: [] for w in ALL_WORDS}
    for word in ALL_WORDS:
        for cls in ("inanimate", "animate"):
            train_nouns, test_nouns = NOUN_POOLS[word][cls]
            assert not (set(train_nouns) & set(test_nouns)), f"{word}/{cls}: TRAIN/TEST noun overlap"
            gold_sense = WORD_SENSE_MENU[word][cls]
            for n in train_nouns + test_nouns:
                real = lookup_animacy(n, "NOUN")
                assert real is not None and real["animacy"] == cls, (
                    f"{word}/{cls}: noun {n!r} classified {real} (expected animacy={cls!r})")
            true_pole = _pole_of_sense(gold_sense)
            shown_pole = pole_override.get((word, cls), true_pole)
            templates = POS_CONSEQUENCE_TEMPLATES if shown_pole == "POS" else NEG_CONSEQUENCE_TEMPLATES
            occ = 0
            for n in train_nouns:
                for _ in range(N_TEMPLATES_PER_NOUN):
                    tmpl = templates[occ % len(templates)]
                    s1 = f"He {VERB_PAST[word]} the {n}."
                    train_stories[word].append({
                        "word": word, "context_class": cls, "patient_noun": n,
                        "gold_sense": gold_sense, "true_pole": true_pole, "shown_pole": shown_pole,
                        "sentence1": s1, "sentence2": tmpl,
                    })
                    occ += 1
            for n in test_nouns:
                s = f"He {VERB_PAST[word]} the {n}."
                test_items[word].append({"word": word, "context_class": cls, "patient_noun": n,
                                          "gold_sense": gold_sense, "sentence": s})
    return train_stories, test_items


TRAIN_STORIES_REAL, TEST_ITEMS = build_words_data(pole_override=None)
N_TEST_AMBIGUOUS = sum(len(TEST_ITEMS[w]) for w in AMBIGUOUS_WORDS)   # 28 (7 words x 2 cls x 2 nouns)
N_TEST_BASELINE = len(TEST_ITEMS[BASELINE_WORD])                     # 4

# HARD-PASS / HARD-FAIL bands (fixed BEFORE the full 5-seed run per the task brief's own gate spec).
BAND_LEARNED_HELDOUT_PASS = 0.75
BAND_BASELINE_PASS = 0.75
BAND_MIN_LIFT_OVER_SCRAMBLE = 0.15
BAND_HARD_FAIL_HELDOUT = 0.55


def _read_consequence_vote(sentence1: str, sentence2: str):
    """The ONE call site that reads a story's shown consequence: hdlab.goal_typing.
    congruence_with_lexicon_fallback on the 2-sentence passage (imported, not reimplemented -- see
    module docstring PRE-AUTHORING VERIFICATION for why this always resolves via that function's own
    lexicon-fallback tier for these stories). MET -> +1.0, UNMET -> -1.0, anything else -> 0.0."""
    passage = sentence1 + " " + sentence2
    verdict, detail = congruence_with_lexicon_fallback(passage)
    vote = 1.0 if verdict == "MET" else (-1.0 if verdict == "UNMET" else 0.0)
    return vote, verdict, detail.get("reason")


def learn_word_map(word, stories, ctx_vecs, sense_vecs, abstain_band=ABSTAIN_BAND_DEFAULT):
    """LEARN word's superposition map FROM EXPOSURE: per context_class present in `stories`, vote on
    every story's consequence (_read_consequence_vote), aggregate into a signed margin per candidate
    sense (mean_vote weighted by that sense's affect pole -- RECIPROCITY gets +mean_vote, BLOCK_HIGH
    gets -mean_vote, so a consistent run of MET votes clears the RECIPROCITY-pole candidate's margin
    and a consistent run of UNMET votes clears the BLOCK_HIGH-pole candidate's), then GATE via
    hdlab.self_improving_loop.decide_keep_or_revert (imported, not reimplemented) -- only a class
    whose best candidate STRICTLY clears abstain_band contributes a bind() entry. Returns
    (word_map_or_None, per_class_detail)."""
    by_class = {}
    for s in stories:
        by_class.setdefault(s["context_class"], []).append(s)
    entries = []
    detail = {}
    for cls, story_list in by_class.items():
        candidates = CANDIDATE_SENSES[word]
        votes, verdicts = [], []
        for s in story_list:
            vote, verdict, _reason = _read_consequence_vote(s["sentence1"], s["sentence2"])
            votes.append(vote)
            verdicts.append(verdict)
        mean_vote = sum(votes) / len(votes) if votes else 0.0
        agg_deltas = {c: mean_vote * _pole_sign(c) for c in candidates}
        confirmed = decide_keep_or_revert(agg_deltas, abstain_band=abstain_band)
        detail[cls] = {"votes": votes, "verdicts": verdicts, "mean_vote": mean_vote,
                       "confirmed_sense": confirmed,
                       "agg_deltas": {k: round(v, 4) for k, v in agg_deltas.items()},
                       "n_stories": len(story_list)}
        if confirmed is not None:
            entries.append(binding.bind(ctx_vecs[cls], sense_vecs[(word, confirmed)]))
    word_map = bundling.bundle(torch.stack(entries, dim=0)) if entries else None
    return word_map, detail


def run_noise_arm(sentence1_list, sentence2_list, abstain_band=ABSTAIN_BAND_DEFAULT):
    """The anti-drift/noise gate check: NO VSA vectors needed -- this tests the CONFIRM/ABSTAIN
    decision itself (decide_keep_or_revert), the load-bearing claim of gate 4. A single synthetic
    candidate ("NOISE_SENSE") whose aggregate margin is the mean vote across the given stories;
    inconsistent (alternating MET/UNMET) or absent (no lexicon signal) evidence must average to (or
    near) 0.0 and fail to clear abstain_band -- confirmed=None (abstain)."""
    votes, verdicts = [], []
    for s1, s2 in zip(sentence1_list, sentence2_list):
        vote, verdict, _reason = _read_consequence_vote(s1, s2)
        votes.append(vote)
        verdicts.append(verdict)
    mean_vote = sum(votes) / len(votes) if votes else 0.0
    agg_deltas = {"NOISE_SENSE": mean_vote}
    confirmed = decide_keep_or_revert(agg_deltas, abstain_band=abstain_band)
    return {"votes": votes, "verdicts": verdicts, "mean_vote": mean_vote,
            "confirmed": confirmed, "abstained": confirmed is None}


def eval_word_maps(word_maps, ctx_vecs, sense_vecs, test_items, words):
    """Held-out collapse accuracy via Stage 2's own collapse_predict (imported, not reimplemented). A
    word whose map is None (fully abstained on every class -- never happens for the 7 accuracy-gated
    words given consistent training, but handled defensively) predicts nothing and scores incorrect."""
    n_correct, n_total, items = 0, 0, []
    for w in words:
        wm = word_maps.get(w)
        for it in test_items[w]:
            if wm is None:
                pred, ok = None, False
            else:
                pred, _sims = stage2.collapse_predict(w, it["context_class"], wm, ctx_vecs, sense_vecs,
                                                        CANDIDATE_SENSES[w])
                ok = pred == it["gold_sense"]
            n_correct += int(ok)
            n_total += 1
            items.append({"word": w, "noun": it["patient_noun"], "context_class": it["context_class"],
                          "gold_sense": it["gold_sense"], "pred_sense": pred, "correct": ok})
    acc = n_correct / n_total if n_total else 0.0
    return acc, items


def _predicted_seq_digest(items):
    seq = [it["pred_sense"] for it in items]
    return hashlib.sha256(json.dumps(seq).encode()).hexdigest()[:16], seq


# ------------------------------------------------------------------------- per-seed unit
def run_seed(seed: int) -> dict:
    try:
        gen_vsa = torch.Generator().manual_seed(seed * 1000 + 42)
        ctx_vecs = {cls: atoms.make_atom_fhrr(N_DIM_WORD, gen_vsa) for cls in ("inanimate", "animate")}
        sense_vecs = {}
        for word in ALL_WORDS:
            for sname in CANDIDATE_SENSES[word]:
                sense_vecs[(word, sname)] = atoms.make_atom_fhrr(N_DIM_WORD, gen_vsa)

        # ---- SCRAMBLE-CONSEQUENCE corpus: global pole-permutation over the 14 ambiguous pairs ----
        scr_pole_table = stage2._scrambled_teaching_table(REAL_POLE_TABLE, seed=seed + 9000)
        train_stories_scramble, _ = build_words_data(pole_override=scr_pole_table)

        # ---- LEARN word_maps: REAL exposure (all 8 words) + SCRAMBLE exposure (7 ambiguous only) ----
        word_maps_real, learn_detail_real = {}, {}
        for word in ALL_WORDS:
            wm, d = learn_word_map(word, TRAIN_STORIES_REAL[word], ctx_vecs, sense_vecs)
            word_maps_real[word] = wm
            learn_detail_real[word] = d
        word_maps_scramble, learn_detail_scramble = {}, {}
        for word in AMBIGUOUS_WORDS:
            wm, d = learn_word_map(word, train_stories_scramble[word], ctx_vecs, sense_vecs)
            word_maps_scramble[word] = wm
            learn_detail_scramble[word] = d

        # ---- HAND-TAUGHT comparison arm: Stage 2's own teach_word_map on the IDENTICAL story items
        #      (same nouns; only the supervision source differs -- gold_sense read directly, not the
        #      consequence text). Informational (gate 3), not pass/fail-gated.
        word_maps_hand_taught = {}
        for word in AMBIGUOUS_WORDS + [BASELINE_WORD]:
            word_maps_hand_taught[word] = stage2.teach_word_map(
                word, TRAIN_STORIES_REAL[word], None, ctx_vecs, sense_vecs)

        # ---- gate 1: held-out collapse, LEARNED (ambiguous 28 items + baseline 4 items) ----
        acc_learned_ambiguous, items_learned = eval_word_maps(word_maps_real, ctx_vecs, sense_vecs,
                                                               TEST_ITEMS, AMBIGUOUS_WORDS)
        acc_baseline_learned, items_baseline = eval_word_maps(word_maps_real, ctx_vecs, sense_vecs,
                                                               TEST_ITEMS, [BASELINE_WORD])

        # ---- gate 2: SCRAMBLE-CONSEQUENCE control, same 28 items ----
        acc_learned_scramble, items_scramble = eval_word_maps(word_maps_scramble, ctx_vecs, sense_vecs,
                                                               TEST_ITEMS, AMBIGUOUS_WORDS)
        lift_over_scramble = acc_learned_ambiguous - acc_learned_scramble

        # ---- gate 3 (informational): vs HAND-TAUGHT baseline, same 28 items ----
        acc_hand_taught, items_hand_taught = eval_word_maps(word_maps_hand_taught, ctx_vecs, sense_vecs,
                                                             TEST_ITEMS, AMBIGUOUS_WORDS)
        gap_vs_hand_taught = acc_hand_taught - acc_learned_ambiguous

        # ---- gate 4: anti-drift / noise (dedicated arms, decoupled from the 8-word maps above) ----
        noise_inconsistent = run_noise_arm(NOISE_SENTENCE1, NOISE_SENTENCE2_INCONSISTENT)
        noise_absent = run_noise_arm(NOISE_SENTENCE1, NOISE_SENTENCE2_ABSENT)

        # ---- gate 5: spoil-reversed anti-confound (LEARNED map, not hand-taught) ----
        spoil_detail = learn_detail_real["spoil"]
        spoil_reversed_holds = (spoil_detail["inanimate"]["confirmed_sense"] == "RUIN"
                                and spoil_detail["animate"]["confirmed_sense"] == "PAMPER")

        # ---- arms-differ digest (META_RULE_AF): real-learned vs scramble-learned predicted-sense seq
        dig_real, seq_real = _predicted_seq_digest(items_learned)
        dig_scr, seq_scr = _predicted_seq_digest(items_scramble)

        return {
            "seed": seed,
            "acc_learned_ambiguous": acc_learned_ambiguous, "acc_baseline_learned": acc_baseline_learned,
            "acc_learned_scramble": acc_learned_scramble, "lift_over_scramble": lift_over_scramble,
            "acc_hand_taught": acc_hand_taught, "gap_vs_hand_taught": gap_vs_hand_taught,
            "noise_inconsistent": {k: v for k, v in noise_inconsistent.items()},
            "noise_absent": {k: v for k, v in noise_absent.items()},
            "noise_inconsistent_abstained": bool(noise_inconsistent["abstained"]),
            "noise_absent_abstained": bool(noise_absent["abstained"]),
            "spoil_reversed_holds": bool(spoil_reversed_holds),
            "spoil_learn_detail": spoil_detail,
            "digests": {"real": dig_real, "scramble": dig_scr},
            "arms_differ_real_vs_scramble": dig_real != dig_scr,
            "learn_detail_real": learn_detail_real, "learn_detail_scramble": learn_detail_scramble,
            "items_learned": items_learned, "items_scramble": items_scramble,
            "items_baseline": items_baseline, "items_hand_taught": items_hand_taught,
            "failure_class": None,
        }
    except Exception as e:
        return {"seed": seed, "failure_class": f"{type(e).__name__}: {str(e)[:300]}",
                "traceback": traceback.format_exc()[:3000]}


# ------------------------------------------------------------------------- verdict
def aggregate_and_verdict(per_seed: dict) -> dict:
    seeds = sorted(per_seed.keys())
    failed = [s for s in seeds if per_seed[s].get("failure_class")]
    ok_seeds = [s for s in seeds if not per_seed[s].get("failure_class")]

    def mean_key(key):
        vals = [float(per_seed[s][key]) for s in ok_seeds]
        return sum(vals) / max(1, len(vals))

    n = len(seeds)
    if n < EXPECTED_N_SEEDS or len(ok_seeds) < EXPECTED_N_SEEDS:
        return {
            "verdict": "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
            "verdict_msg": f"landed {n} seeds ({len(ok_seeds)} ok, {len(failed)} failed), "
                           f"expected {EXPECTED_N_SEEDS}",
            "summary": "cardinality breach", "n_seeds": n, "n_ok": len(ok_seeds), "failed_seeds": failed,
        }

    mean_learned = mean_key("acc_learned_ambiguous")
    mean_baseline = mean_key("acc_baseline_learned")
    mean_scramble = mean_key("acc_learned_scramble")
    mean_lift = mean_learned - mean_scramble
    mean_hand_taught = mean_key("acc_hand_taught")
    mean_gap_vs_hand_taught = mean_hand_taught - mean_learned

    noise_all_abstained = all(per_seed[s]["noise_inconsistent_abstained"]
                              and per_seed[s]["noise_absent_abstained"] for s in ok_seeds)
    spoil_all_hold = all(per_seed[s]["spoil_reversed_holds"] for s in ok_seeds)
    any_arms_identical = any(not per_seed[s]["arms_differ_real_vs_scramble"] for s in ok_seeds)

    learned_pass = mean_learned >= BAND_LEARNED_HELDOUT_PASS
    baseline_pass = mean_baseline >= BAND_BASELINE_PASS
    scramble_collapsed = mean_lift >= BAND_MIN_LIFT_OVER_SCRAMBLE
    learned_hard_fail = mean_learned < BAND_HARD_FAIL_HELDOUT

    if any_arms_identical:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif learned_pass and baseline_pass and scramble_collapsed and noise_all_abstained and spoil_all_hold:
        verdict = "HARD_PASS"
    elif learned_hard_fail or not scramble_collapsed or not noise_all_abstained or not spoil_all_hold:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    summary = (f"learned_heldout(ambiguous)={mean_learned:.3f} (band>={BAND_LEARNED_HELDOUT_PASS}) "
               f"learned_heldout(baseline)={mean_baseline:.3f} (band>={BAND_BASELINE_PASS}) "
               f"scramble_acc={mean_scramble:.3f} lift_over_scramble={mean_lift:.3f} "
               f"(band>={BAND_MIN_LIFT_OVER_SCRAMBLE}) "
               f"hand_taught_acc={mean_hand_taught:.3f} gap_vs_hand_taught={mean_gap_vs_hand_taught:.3f} "
               f"(informational, not gated) "
               f"noise_inconsistent_abstained={noise_all_abstained} "
               f"spoil_reversed_holds={spoil_all_hold} "
               f"n_test_ambiguous={N_TEST_AMBIGUOUS} n_test_baseline={N_TEST_BASELINE}")
    return {
        "verdict": verdict, "verdict_msg": f"{verdict}: {summary}", "summary": summary,
        "n_seeds": n, "n_ok": len(ok_seeds), "failed_seeds": failed,
        "means": {"acc_learned_ambiguous": mean_learned, "acc_baseline_learned": mean_baseline,
                  "acc_learned_scramble": mean_scramble, "lift_over_scramble": mean_lift,
                  "acc_hand_taught": mean_hand_taught, "gap_vs_hand_taught": mean_gap_vs_hand_taught},
        "bands": {"learned_pass": learned_pass, "baseline_pass": baseline_pass,
                  "scramble_collapsed": scramble_collapsed, "noise_all_abstained": noise_all_abstained,
                  "spoil_all_hold": spoil_all_hold, "learned_hard_fail": learned_hard_fail,
                  "any_arms_identical": any_arms_identical},
        "words": {"ambiguous": AMBIGUOUS_WORDS, "baseline": BASELINE_WORD, "menu": WORD_SENSE_MENU,
                  "sense_affect_type": {k: v for k, v in SENSE_AFFECT_TYPE.items()}},
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


def run(run_mode):
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
        res = run_seed(seed)
        record_unit(output_dir, k, res)
        if res.get("failure_class"):
            print(f"[FAIL] seed={seed} {res['failure_class']}", flush=True)
        else:
            print(f"[progress] seed={seed} done in {time.perf_counter()-ts:.1f}s "
                  f"learned={res['acc_learned_ambiguous']:.3f} scramble={res['acc_learned_scramble']:.3f} "
                  f"hand_taught={res['acc_hand_taught']:.3f} "
                  f"noise_abstain=({res['noise_inconsistent_abstained']},{res['noise_absent_abstained']}) "
                  f"spoil_ok={res['spoil_reversed_holds']}", flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(output_dir).values()}
    agg = aggregate_and_verdict(per_seed)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = {"seeds": SEEDS, "n_dim_word": N_DIM_WORD,
                      "n_test_ambiguous": N_TEST_AMBIGUOUS, "n_test_baseline": N_TEST_BASELINE,
                      "n_templates_per_noun": N_TEMPLATES_PER_NOUN,
                      "bands": {"learned_heldout_pass": BAND_LEARNED_HELDOUT_PASS,
                                "baseline_pass": BAND_BASELINE_PASS,
                                "min_lift_over_scramble": BAND_MIN_LIFT_OVER_SCRAMBLE,
                                "hard_fail_heldout": BAND_HARD_FAIL_HELDOUT}}
    agg["per_seed"] = per_seed
    _write_metrics(output_dir, agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.1f}s", flush=True)
    return agg


# ------------------------------------------------------------------------- self-test
def self_test():
    """(1) menu composition: 7 ambiguous words with 2 candidates each, 1 baseline with 1 candidate;
    (2) TRAIN/TEST noun pools disjoint per (word,class), already asserted at import time via
    build_words_data, reaffirmed here; (3) consequence-template Tier-1 lexicon reads verified fresh
    (not just at authoring time); (4) tiny end-to-end run: all 5 gates clear their pre-registered
    bands, arms pairwise differ (META_RULE_AF)."""
    from hdlab.goal_typing import lexicon_predict

    # (1) menu composition
    for w in AMBIGUOUS_WORDS:
        assert len(CANDIDATE_SENSES[w]) == 2, f"{w}: expected 2 candidate senses, got {CANDIDATE_SENSES[w]}"
    assert len(CANDIDATE_SENSES[BASELINE_WORD]) == 1
    assert len(AMBIGUOUS_WORDS) == 7 and len(ALL_WORDS) == 8

    # (2) TRAIN/TEST disjointness (reaffirm; build_words_data already asserted this at import time)
    for w in ALL_WORDS:
        for cls in ("inanimate", "animate"):
            train_n, test_n = NOUN_POOLS[w][cls]
            assert not (set(train_n) & set(test_n)), f"{w}/{cls}: TRAIN/TEST overlap"
    assert N_TEST_AMBIGUOUS == 28 and N_TEST_BASELINE == 4

    # (3) consequence-template Tier-1 lexicon reads (re-verify live, not just trust the docstring)
    for t in POS_CONSEQUENCE_TEMPLATES:
        assert lexicon_predict(t) == "MET", f"POS template {t!r} did not read MET: {lexicon_predict(t)}"
    for t in NEG_CONSEQUENCE_TEMPLATES:
        assert lexicon_predict(t) == "UNMET", f"NEG template {t!r} did not read UNMET: {lexicon_predict(t)}"
    for t in NEUTRAL_CONSEQUENCE_TEMPLATES:
        assert lexicon_predict(t) == "NONE", f"NEUTRAL template {t!r} did not read NONE: {lexicon_predict(t)}"

    # (4) tiny end-to-end run (full corpus -- this cell has no reduced-scale smoke regime, see
    # CELL-TEMPLATE header "discriminator survives scale")
    res = run_seed(0)
    assert res["failure_class"] is None, f"run_seed crashed: {res.get('failure_class')}"
    assert res["acc_learned_ambiguous"] >= BAND_LEARNED_HELDOUT_PASS, (
        f"learned held-out did not clear band: {res['acc_learned_ambiguous']:.3f} < {BAND_LEARNED_HELDOUT_PASS}")
    assert res["acc_baseline_learned"] >= BAND_BASELINE_PASS, (
        f"baseline held-out did not clear band: {res['acc_baseline_learned']:.3f} < {BAND_BASELINE_PASS}")
    assert res["lift_over_scramble"] >= BAND_MIN_LIFT_OVER_SCRAMBLE, (
        f"lift over scramble too small: {res['lift_over_scramble']:.3f} < {BAND_MIN_LIFT_OVER_SCRAMBLE}")
    assert res["noise_inconsistent_abstained"], "NOISE_INCONSISTENT arm did not abstain"
    assert res["noise_absent_abstained"], "NOISE_ABSENT arm did not abstain"
    assert res["spoil_reversed_holds"], f"spoil-reversed anti-confound failed: {res['spoil_learn_detail']}"
    assert res["arms_differ_real_vs_scramble"], (
        f"META_RULE_AF: real/scramble predicted-sense digests identical: {res['digests']}")

    print(f"[SELFTEST PASS] learned={res['acc_learned_ambiguous']:.3f} "
          f"baseline={res['acc_baseline_learned']:.3f} scramble={res['acc_learned_scramble']:.3f} "
          f"lift={res['lift_over_scramble']:.3f} hand_taught={res['acc_hand_taught']:.3f} "
          f"gap_vs_hand_taught={res['gap_vs_hand_taught']:.3f} "
          f"noise_abstain=({res['noise_inconsistent_abstained']},{res['noise_absent_abstained']}) "
          f"spoil_ok={res['spoil_reversed_holds']} digests={res['digests']}", flush=True)
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
        run("smoke")   # IDENTICAL corpus to --full (see CELL-TEMPLATE header); no reduced regime
        raise SystemExit(0)
    run("full")
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
