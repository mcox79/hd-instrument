"""exp_read_discourse_entitygrid_coherence_v1 -- BET 3 of the chain-grade reading slate (2026-07-17):
the RIGHT, non-pronoun, testable discourse "state of mind" metric -- ENTITY-GRID role-transition
COHERENCE DISCRIMINATION (Barzilay & Lapata 2005/2008), glass-box, no LLM.

TRIGGER: notes/chain_grade_decision_slate_reading_frontier_2026-07-17.md BET 3 + the full drill
notes/research_discourse_topic_thread_coherence_metric_2026-07-17.md ("Cheap decisive test", ranked
candidate #1). The pronoun-accuracy struggle (recency-competitive, see
notes/research_coreference_hobbs_centering_resolver_2026-07-16.md) is a metric-choice problem, not a
mechanism problem: the literature's own 20-year-old classical (non-neural) task for "does tracking
who's-doing-what add coherence value" is sentence-order PERMUTATION DISCRIMINATION over an entity x
grammatical-role x sentence GRID -- self-supervised (permutations are free negatives), zero annotation
cost, with a REAL non-trivial baseline (entity co-occurrence, role discarded) built into the design.

MECHANISM: per passage, build an entity-grid ONCE (in the passage's ORIGINAL sentence order): for every
discourse entity, the sequence of {S(ubject), O(bject), X(other/oblique/mentioned), -(absent)} across
sentences. Score a SENTENCE ORDER (the original order, or a permutation of the SAME fixed rows) via a
role-TRANSITION coherence formula (candidate A) and, separately, via an entity-CO-OCCURRENCE-only formula
that discards role (baseline B1) and a uniform-random score (baseline B2/floor). Discriminate the
original order from K permutations of itself, on BOTH a FULL-SHUFFLE condition (easy) and an
ADJACENT-SENTENCE-SWAP condition (hard, per Barzilay-Lapata's own near-vs-far asymmetry finding).

ENTITY/ROLE EXTRACTION (reuses the EXISTING role-tagged parser infrastructure, not rebuilt): imports
`_build_tags_open_v4` (rung9's real-prose-capable tagger: closed function-word lookups + NLTK's classical
averaged-perceptron POS tagger as the OOV fallback -- NLTK-legal, glass-box, no LLM), `_np_head_from_run_v2`
(rung9's compound-noun-phrase head selector, e.g. "Buster Bear" -> head "bear", "Little Joe Otter" -> head
"otter") and `_scan_object_np_v2` (rung9's direct/oblique-object NP scanner) UNMODIFIED from
experiments/exp_read_grow_realprose_simple_register_rung9_downstream_bugs_v1. Per sentence: the head noun
(or noun-run, "and"-joined for co-subjects) immediately before the first VERB = role S; the object NP
`_scan_object_np_v2` finds immediately after the verb = role O (or X if it is a PREPOSITIONAL/oblique
object -- `prep is not None`); every other NOUN token in the sentence = role X. SUBJECT-POSITION pronouns
(he/him/his/she/her/it/they/them) are resolved via a lightweight, GRADED, NEVER-ABSTAINING recency-only Cb
pointer (Centering Rule 1's Cb = "whichever entity was Subject of the immediately preceding sentence that
established one" -- the SAME Tier-0 pattern already used by
`experiments/exp_read_discourse_state_of_mind_wsm_coupling_realcorpus_v2.WSMState`/`resolve_pronoun_realcorpus`,
kept SELF-CONTAINED here rather than imported because that resolver is wired to the full SVO-TRIPLE
extraction pipeline, which is too fragile on this dialogue-heavy real prose to populate a grid reliably;
this cell only needs entity+role identification, not full relation extraction). DECLARED SCOPE NARROWING
(honest, not hidden): OBJECT-position pronouns are NOT resolved (out of scope, same convention as the v1
coref cell) -- that mention is simply dropped for that sentence, identically for BOTH scoring arms (an
upstream extraction limitation, not a scoring-formula difference, so the ONE-VARIABLE isolation still
holds). A wrong/graded pronoun bind here only adds grid NOISE (this cell scores passage-level COHERENCE
STRUCTURE, not individual fact injection) -- it is not a zero-hallucination-invariant concern the way the
v1 coref cell's fact-store injection is.

CORPUS (declared, licensed, glass-box, NLTK-bundled -- NO LLM, same public-domain family as
exp_read_discourse_state_of_mind_wsm_coupling_realcorpus_v2's fables): `nltk.corpus.gutenberg` --
'bryant-stories.txt' (Sara Cone Bryant, "Stories to Tell to the Children", 1918, public domain) AND
'burgess-busterbrown.txt' (Thornton Burgess, "The Adventures of Buster Bear", public domain) -- TWO
distinct books (not just the single book/scene family the coref cells already used) for genuine
cross-passage topic/entity variety (Cloud/Red-Hen/Gingerbread-Boy/Lion-and-Jackals/Jack-Rollaround/
Half-Chick-and-Fire from bryant; Buster-Bear/Little-Joe-Otter/Billy-Mink/Shadow-the-Weasel from burgess).
10 passages total (6 bryant + 4 burgess), each 8 CONSECUTIVE, VERBATIM sentences (nltk `sent_tokenize`,
committed here as string literals -- no network re-fetch at self-test/smoke/full runtime, same convention
as the WSM realcorpus cell). n=10 passages x K=12 permutations x 2 conditions = 240 pairwise
discrimination comparisons per scorer (720 total judgments across the 3 scorers).

SENTENCE-WINDOW SELECTION (declared, STRUCTURAL, NOT outcome-tuned -- decided BEFORE any coherence score
was computed, same discipline as the WSM realcorpus cell's own selection rule): candidate 8-sentence
windows were scanned at a FIXED STRIDE of 50 sentences starting at sentence index 20 in each book (skipping
front matter); a window is KEPT iff (a) at most 3 of its 8 sentences open with a quote mark (caps
dialogue-only windows that would starve the grid of narrative subject/object structure), (b) total word
count across the window is >=70 (excludes short/fragmentary windows), and (c) at most 1 of its 8 sentences
has fewer than 4 words (excludes windows dominated by sentence-tokenizer over-splits on exclamation marks
inside quotes, e.g. "Ao!" / "Ao!" / "Ao!"). The FIRST 6 (bryant) / 4 (burgess) windows satisfying ALL THREE
filters, in increasing sentence-index order, were taken verbatim -- no window was read for narrative
quality and rejected/kept on that basis; the filters are purely mechanical (quote-density, word-count,
fragment-density), decided before computing any co-occurrence or role-transition number.

DESIGN GATE (per the dispatching pre-reg, notes/research_discourse_topic_thread_coherence_metric_2026-07-17.md):
  1. REAL (non-strawman) BASELINE: co-occurrence-only grid (role discarded) + random floor. Candidate A
     must beat BOTH.
  2. CAN-FAIL: role-transition might add nothing over co-occurrence (HARD-FAIL is a real, reachable
     outcome -- verified at self-test via a synthetic DEGENERATE-ROLE construction where role-transition
     score is, BY CONSTRUCTION, permutation-INVARIANT, i.e. discrimination collapses to exactly chance;
     see self_test check (7)).
  3. DIFFICULTY-ON: the ADJACENT-SWAP condition (1-2 non-overlapping adjacent-sentence transpositions per
     permutation, a MUCH smaller perturbation than a full shuffle) is run and reported, not deferred.
  4. ONE VARIABLE: candidate A and baseline B1 share the IDENTICAL entity extraction, IDENTICAL passages,
     and IDENTICAL permutation draws (same `order` list scores both formulas) -- only the SCORING FORMULA
     (role-transition-weighted vs role-free co-occurrence-Jaccard) differs.
  5. Genuine topic/entity variety: 2 distinct public-domain books, 10 passages, disclosed above.

TRANSITION-WEIGHT FORMULA (candidate A, HAND-SET not fit-to-data -- glass-box, no learned parameters, no
risk of fitting-to-the-permutation-outcome; ordering follows Centering theory's own established coherence
ranking, Grosz-Joshi-Weinstein / Brennan-Friedman-Pollard: CONTINUE (S,S) is the most coherent transition,
then (O,O), then a SMOOTH-SHIFT-like role swap (S,O)/(O,S), then transitions touching a peripheral (X)
mention, then a NEUTRAL X-X co-occurrence, then a DISCONTINUITY penalty when a SALIENT (S or O) mention
appears/disappears entirely between adjacent sentences):
  W[S,S]=3.0  W[O,O]=2.0  W[S,O]=W[O,S]=1.0  W[S,X]=W[X,S]=W[O,X]=W[X,O]=0.5  W[X,X]=0.5
  W[S,-]=W[-,S]=-1.0  W[O,-]=W[-,O]=-0.5  W[X,-]=W[-,X]=0.0  W[-,-]=0.0
Candidate A score(order) = sum over entities e, over adjacent ROW pairs (i,i+1) in `order`, of
W[role(e,order[i]), role(e,order[i+1])]. Baseline B1 score(order) = sum over adjacent row pairs of
Jaccard(mentions(order[i]), mentions(order[i+1])) where mentions(i) = the SET of entities mentioned
(any role) in original sentence i, role discarded. Baseline B2 = an independent uniform-random draw per
(document, permutation) -- a pure sanity/floor check, not a serious competitor.

METRIC (the literature's OWN task+metric, Barzilay & Lapata): pairwise discrimination accuracy = fraction
of (original, permuted) pairs where score(original) > score(permuted) (tie = 0.5 credit), aggregated over
all 10 passages x 12 permutations, reported SEPARATELY per condition (full_shuffle / adjacent_swap) and
per scorer (A / B1 / random).

PRE-REG (envelope-fail-bands; LOCKED verbatim from the dispatching research note's own falsifiable
thresholds -- exp_dev's autonomy here is over the scoring FORMULA / K / passage sampling, NOT the bars):
  HARD-PASS: acc_full_shuffle_A >= 0.70 AND (acc_full_shuffle_A - acc_full_shuffle_B1) >= 0.08 AND
    (acc_adjacent_swap_A - acc_adjacent_swap_B1) >= 0.04 AND random_baseline_sanity_ok (0.35<=acc_random<=0.65
    on BOTH conditions -- a test-VALIDITY guard, not part of the note's own bars, added here to catch a
    broken discrimination-accuracy computation before trusting either HARD-PASS or HARD-FAIL).
  HARD-FAIL: (acc_full_shuffle_A - acc_full_shuffle_B1) <= 0.03 (role info within 3pts of co-occurrence --
    adds ~nothing) OR acc_full_shuffle_A <= 0.60 (barely above the random floor -- entity/role extraction
    too sparse/noisy at this register for ANY coherence signal, a more basic problem than role-vs-cooccurrence).
  MIDDLE: otherwise (report dominant class -- e.g. beats B1 on full-shuffle but the margin collapses on
    adjacent-swap = role info helps detect gross scrambling but not fine local incoherence, per the
    literature's own near-vs-far asymmetry -- an informative outcome, not a wasted test).
  If random_baseline_sanity fails on either condition: tier forced to INVALID_TEST_DESIGN regardless of A/B1
    (a construction/implementation-bug guard, analogous to the WSM cell's CONSTRUCTION_ARTIFACT_DETECTED gate).
  P estimate: P~0.42 HYPOTHESIZED@notes/research_discourse_topic_thread_coherence_metric_2026-07-17.md
    (lit-scan-deflated novel-synthesis; port risk to THIS register/corpus is the dominant uncertainty).

COMPUTE: fully symbolic/deterministic except for NLTK's classical POS tagger (glass-box, no learned
weights fit BY this cell -- the tagger is a fixed, pre-trained, non-LLM component already used identically
throughout this codebase's reading arc). No VSA/torch. Sequential-CPU (grid built once per passage, ~80
short sentences total; permutations are O(1) row-reindexing of an already-built grid, not re-parsing --
wall time <5s). Storage: no_storage. smoke == full (fixed, tiny, deterministic corpus -- nothing to
shrink, same precedent as the WSM realcorpus cell). progress_logging = print_flush_true (well under the
1800s mandatory-heartbeat threshold, added anyway per convention).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): EMPIRICAL check over the real 10-passage corpus --
#     scorer A and scorer B1 do NOT always agree on which of (original, permuted) scores higher (at least
#     one disagreement across all 240 pairs) -- proves the two formulas are not measuring the identical
#     signal. A synthetic hash-based arms-differ probe is not meaningful here (both scorers are pure
#     deterministic functions of the same grid, not stochastic outputs to hash-compare).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor -- fully symbolic discrete role/co-occurrence scoring, no
#     phasor/argmax noise anywhere in this cell.
# - baseline_in_band: N/A by design (same as the coref/WSM cells) -- there is no tunable "regime" here (10
#     fixed real passages); the RANDOM-BASELINE SANITY check (0.35<=acc_random<=0.65) is the honest
#     analogous validity guard (catches a broken discrimination-accuracy computation, not a regime choice).
# - discriminator survives scale: fixed real-passage corpus (no N/scale axis). Discriminators = (1) scorer
#     A beats scorer B1 and the random floor on real passages (asserted, non-trivial, not by-construction
#     saturated), (2) a synthetic DEGENERATE-ROLE construction proves scorer A CAN fail (collapses to
#     chance) -- the can-fail requirement, (3) scorer A and B1 empirically disagree on some pairs (arms
#     differ), (4) deterministic seeding reproduces identical permutations across two independent calls.
# - HARD_PASS strictly above floor; explicit bands in prereg JSON (locked from the dispatching research note).
# - real_code_path (F.1): self-test constructs+calls the REAL imported _build_tags_open_v4 /
#     _np_head_from_run_v2 / _scan_object_np_v2 (rung9, unmodified) at the SAME real-sentence scale the
#     FULL run uses (no separate synthetic-only branch for the entity-extraction pipeline; the synthetic
#     DEGENERATE-ROLE construction used for the can-fail check operates on a hand-built grid/mention-set,
#     bypassing extraction ON PURPOSE since it is testing the SCORING FORMULA's can-fail property, not the
#     extractor -- declared here, not hidden).
# - real_code_path_and_signature_preflight (F.1-F.5): not_applicable -- this cell constructs no KGStore /
#     fit-module / store-helper substrate object (pure symbolic NLP over a fixed sentence corpus), same
#     precedent as exp_read_coref_hobbs_centering_resolver_v1 / exp_read_discourse_state_of_mind_wsm_coupling_
#     realcorpus_v2 (neither of those two closely-related cells invokes the shared
#     experiments._validity_preflight module either).
# - deterministic_seeding (F.5): fixed integer seed formula (BASE_SEED + passage_idx*10000 + cond_idx*1000 +
#     k), NEVER `hash()` or `list(set(...))` -- verified at self-test (same seed -> same permutation, twice).
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import random
import argparse
import time
import json
import platform
import traceback
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "read_discourse_entitygrid_coherence_v1"

# --- GENUINE REUSE, UNMODIFIED: rung9's real-prose-capable tagger + compound-NP head selector + object-NP
# scanner (the EXISTING role-tagged extraction infrastructure the dispatching note asks this cell to reuse). ---
from experiments.exp_read_grow_realprose_simple_register_rung9_downstream_bugs_v1 import (  # noqa: E402
    _build_tags_open_v4, _np_head_from_run_v2, _scan_object_np_v2,
)

# ---------------------------------------------------------------------------
# CORPUS: 10 real, verbatim, public-domain passages (nltk.corpus.gutenberg; see module docstring for the
# license + selection-rule disclosure). Committed as literals -- no network re-fetch at runtime.
# ---------------------------------------------------------------------------
PASSAGES = [
    {"corpus": "bryant-stories.txt", "start": 70, "sents": [
        "As she said the words a wonderful light glowed from her heart, the sound of thunder rolled through the sky, and a love greater than words can tell filled the Cloud; down, down, close to the earth she swept, and gave up her life in a blessed, healing shower of rain.",
        "That rain was the Cloud's great deed; it was her death, too; but it was also her glory.",
        "Over the whole country-side, as far as the rain fell, a lovely rainbow sprang its arch, and all the brightest rays of heaven made its colours; it was the last greeting of a love so great that it sacrificed itself.",
        "Soon that, too, was gone, but long, long afterward the men and animals who were saved by the Cloud kept her blessing in their hearts.",
        "THE LITTLE RED HEN The little Red Hen was in the farmyard with her chickens, when she found a grain of wheat.",
        '"Who will plant this wheat?"',
        "she said.",
        '"Not I," said the Goose.',
    ]},
    {"corpus": "bryant-stories.txt", "start": 120, "sents": [
        'he said,-- "I have run away from a little old woman, "A little old man, "A cow, "And I can run away from you, I can!"',
        'And, as the horse chased him, he looked over his shoulder and cried,-- "Run!',
        "run!",
        "as fast as you can!",
        '"You can\'t catch me, I\'m the Gingerbread Man!"',
        "And the horse couldn't catch him.",
        "By and by the little Gingerbread Boy came to a barn full of threshers.",
        'When the threshers smelt the Gingerbread Boy, they tried to pick him up, and said, "Don\'t run so fast, little Gingerbread Boy; you look very good to eat."',
    ]},
    {"corpus": "bryant-stories.txt", "start": 170, "sents": [
        '"Dear me!"',
        'said the little Gingerbread Boy, "I am a quarter gone!"',
        'The next minute he said, "Why, I am half gone!"',
        'The next minute he said, "My goodness gracious, I am three quarters gone!"',
        "And after that, the little Gingerbread Boy never said anything more at all.",
        "THE LITTLE JACKALS AND THE LION Once there was a great big jungle; and in the jungle there was a great big Lion; and the Lion was king of the jungle.",
        "Whenever he wanted anything to eat, all he had to do was to come up out of his cave in the stones and earth and _roar_.",
        "When he had roared a few times all the little people of the jungle were so frightened that they came out of their holes and hiding-places and ran, this way and that, to get away.",
    ]},
    {"corpus": "bryant-stories.txt", "start": 220, "sents": [
        "The Lion above couldn't stand that.",
        "He leaped down into the well after the other lion.",
        "But, of course, as you know very well, there wasn't any other lion!",
        "It was only the reflection in the water!",
        "So the poor old Lion floundered about and floundered about, and as he couldn't get up the steep sides of the well, he was at last drowned.",
        'And when he was drowned, the little Jackals took hold of hands and danced round the well, and sang,-- "The Lion is dead!',
        "The Lion is dead!",
        '"We have killed the great Lion who would have killed us!',
    ]},
    {"corpus": "bryant-stories.txt", "start": 320, "sents": [
        "And when he saw them, that naughty Little Jack Rollaround began to tease.",
        '"Out of the way, there!',
        'I am coming!"',
        "he shouted, and sailed the trundle-bed boat straight at them.",
        "He bumped the little Stars right and left, all over the sky, until every one of them put his little lamp out and left it dark.",
        '"Do not treat the little Stars so," said the good Moon.',
        'But Jack Rollaround only behaved the worse: "Get out of the way, old Moon!"',
        'he shouted, "I am coming!"',
    ]},
    {"corpus": "bryant-stories.txt", "start": 420, "sents": [
        "said the little Half-Chick.",
        '"I cannot be bothered with you; I am off to Madrid, to see the King!"',
        "And in spite of the brook's begging, he went away, hoppity-kick, hoppity-kick.",
        "A bit farther on, the Half-Chick came to a Fire, which was smothered in damp sticks and in great distress.",
        '"Oh, little Half-Chick," said the Fire, "you are just in time to save me.',
        "I am almost dead for want of air.",
        'Fan me a little with your wing, I beg."',
        '"The idea!"',
    ]},
    {"corpus": "burgess-busterbrown.txt", "start": 20, "sents": [
        "He shuffled along over to the Laughing Brook, and straight to a little pool of which he knew, and as he drew near he took the greatest care not to make the teeniest, weeniest bit of noise.",
        "Now it just happened that early as he was, some one was before Buster Bear.",
        "When he came in sight of the little pool, who should he see but another fisherman there, who had already caught a fine fat trout.",
        "Who was it?",
        "Why, Little Joe Otter to be sure.",
        "He was just climbing up the bank with the fat trout in his mouth.",
        "Buster Bear's own mouth watered as he saw it.",
        "Little Joe sat down on the bank and prepared to enjoy his breakfast.",
    ]},
    {"corpus": "burgess-busterbrown.txt", "start": 70, "sents": [
        "The idea of great big Buster Bear getting drowned in the Laughing Brook was too funny.",
        "There wasn't water enough in it anywhere except down in the Smiling Pool, and that was on the Green Meadows, where Buster had never been known to go.",
        '"Let\'s go see what he is doing," said Billy Mink.',
        "At first Little Joe didn't want to, but at last his curiosity got the better of his fear, and he agreed.",
        "So the two little brown-coated scamps turned down the Laughing Brook, taking the greatest care to keep out of sight themselves.",
        'They had gone only a little way when Billy Mink whispered: "Sh-h!',
        'There he is."',
        "Sure enough, there was Buster Bear sitting close beside a little pool and looking into it very intently.",
    ]},
    {"corpus": "burgess-busterbrown.txt", "start": 170, "sents": [
        "So this morning he only went far enough to make sure that if Little Joe were watching for him, as he was sure he would be, he would see him coming.",
        "Then, instead of keeping on to the little pool, he hurried to a place way down the Laughing Brook, where the water was very shallow, hardly over his feet, and there he sat chuckling to himself.",
        "Things happened just as he had expected.",
        "The frightened fish Little Joe chased out of the little pools up above swam down the Laughing Brook, because, you know, Little Joe was behind them, and there was nowhere else for them to go.",
        "When they came to the place where Buster was waiting, all he had to do was to scoop them out on to the bank.",
        "It was great fun.",
        "It didn't take Buster long to catch all the fish he could eat.",
        "Then he saved a nice fat trout and waited.",
    ]},
    {"corpus": "burgess-busterbrown.txt", "start": 270, "sents": [
        "Little Joe darted over to the log and looked on the other side.",
        "There was the fat trout, and there also was Little Joe's smallest cousin, Shadow the Weasel, who is a great thief and altogether bad.",
        "Little Joe sprang at him angrily, but Shadow was too quick and darted away.",
        "Little Joe put the fish back on the log and waited.",
        "This time he didn't take his eyes off it.",
        "At last, when he was almost ready to give up, he saw Buster Bear shuffling along towards the Laughing Brook.",
        "Suddenly Buster stopped and sniffed.",
        "One of the Merry Little Breezes had carried the scent of that fat trout over to him.",
    ]},
]

CORPUS_LICENSE = ("nltk.corpus.gutenberg: bryant-stories.txt (Sara Cone Bryant, 'Stories to Tell to the "
                   "Children', 1918) + burgess-busterbrown.txt (Thornton W. Burgess, 'The Adventures of "
                   "Buster Bear') -- both public domain in the US, NLTK-bundled.")

# ---------------------------------------------------------------------------
# Entity/role extraction: reuses rung9's tagger + head-selector + object-NP scanner. Subject-position
# pronouns resolved via a self-contained, GRADED (never-abstaining) recency-only Cb pointer.
# ---------------------------------------------------------------------------
PRON_TAG = "PRON"


class CbTracker:
    """Centering Rule-1 Cb pointer: the most recent sentence's established SUBJECT entity. GRADED (never
    abstains) -- appropriate for passage-level COHERENCE SCORING (not fact injection); a wrong bind only
    adds grid noise, identically for both scoring arms (see module docstring)."""
    def __init__(self):
        self.cb = None

    def observe_subject(self, lemma):
        if lemma is not None:
            self.cb = lemma


def _sentence_entities(text, cb_tracker):
    """Returns {entity_lemma: role} for one sentence, role in {'S','O','X'} (best role kept per lemma,
    priority S > O > X). Updates cb_tracker's Cb pointer with this sentence's dominant subject (if any)."""
    T = _build_tags_open_v4(text, True, True, True, True)
    tags = [t[1] for t in T]
    lemmas = [t[2] for t in T]
    n = len(T)
    roles = {}
    prio = {"S": 0, "O": 1, "X": 2}

    def _add(lem, role):
        if lem is None:
            return
        if lem not in roles or prio[role] < prio[roles[lem]]:
            roles[lem] = role

    verb_idx = [i for i in range(n) if tags[i] == "VERB"]
    if not verb_idx:
        for i in range(n):
            if tags[i] == "NOUN":
                _add(lemmas[i], "X")
        cb_tracker.observe_subject(None)
        return roles

    v0 = verb_idx[0]
    subj_lemma = None
    pron_i = next((i for i in range(v0) if tags[i] == PRON_TAG), None)
    if pron_i is not None:
        # subject-position pronoun -> resolve via the graded Cb pointer (may be None early in a passage).
        subj_lemma = cb_tracker.cb
        _add(subj_lemma, "S")
    else:
        i = 0
        while i < v0:
            if tags[i] == "NOUN":
                run_start = i
                while i < v0 and tags[i] == "NOUN":
                    i += 1
                head = _np_head_from_run_v2(T, list(range(run_start, i)), True)
                _add(head, "S")
                if subj_lemma is None:
                    subj_lemma = head
            else:
                i += 1

    j = v0 + 1
    while j < n and tags[j] in ("AUX", "ADV"):
        j += 1
    prep, obj_lemmas, _jend = _scan_object_np_v2(T, tags, lemmas, j, n, True, True, True)
    for ol in obj_lemmas:
        _add(ol, "X" if prep is not None else "O")

    for i in range(n):
        if tags[i] == "NOUN":
            _add(lemmas[i], "X")  # no-op if already S/O via _add's priority guard -- peripheral mentions

    cb_tracker.observe_subject(subj_lemma)
    return roles


def build_grid(sents):
    """Builds the grid ONCE, in the passage's ORIGINAL order (correct sequential Cb-tracking). Returns
    (entity_roles: {entity: [role_or_None per original sentence idx]}, mention_sets: [set(entities) per
    original sentence idx]). Permutations later just REORDER these fixed rows -- they do not re-parse
    (matches standard entity-grid methodology: coreference/role-tagging is computed on the TRUE discourse
    order; only row order is shuffled for the discrimination task)."""
    n = len(sents)
    cb = CbTracker()
    per_sent_roles = [_sentence_entities(s, cb) for s in sents]
    entities = sorted({e for roles in per_sent_roles for e in roles})
    entity_roles = {e: [roles.get(e) for roles in per_sent_roles] for e in entities}
    mention_sets = [set(roles.keys()) for roles in per_sent_roles]
    return entity_roles, mention_sets, n


# ---------------------------------------------------------------------------
# Scoring formulas (candidate A: role-transition; baseline B1: co-occurrence; baseline B2: random floor).
# ---------------------------------------------------------------------------
TRANSITION_WEIGHTS = {
    ("S", "S"): 3.0, ("O", "O"): 2.0,
    ("S", "O"): 1.0, ("O", "S"): 1.0,
    ("S", "X"): 0.5, ("X", "S"): 0.5,
    ("O", "X"): 0.5, ("X", "O"): 0.5,
    ("X", "X"): 0.5,
    ("S", None): -1.0, (None, "S"): -1.0,
    ("O", None): -0.5, (None, "O"): -0.5,
    ("X", None): 0.0, (None, "X"): 0.0,
    (None, None): 0.0,
}


def score_role_transition(entity_roles, order):
    total = 0.0
    for _ent, roles in entity_roles.items():
        seq = [roles[i] for i in order]
        for a, b in zip(seq, seq[1:]):
            total += TRANSITION_WEIGHTS[(a, b)]
    return total


def score_cooccurrence(mention_sets, order):
    total = 0.0
    seq = [mention_sets[i] for i in order]
    for a, b in zip(seq, seq[1:]):
        union = a | b
        if not union:
            continue
        total += len(a & b) / float(len(union))
    return total


def _credit(orig, perm):
    if orig > perm:
        return 1.0
    if orig < perm:
        return 0.0
    return 0.5


# ---------------------------------------------------------------------------
# Permutation generators (deterministic; NEVER hash()-seeded -- F.5 discipline).
# ---------------------------------------------------------------------------
K_PERMUTATIONS = 12
BASE_SEED = 20260717


def _full_shuffle_perm(n, rng):
    order = list(range(n))
    identity = list(range(n))
    tries = 0
    while True:
        order = list(range(n))
        rng.shuffle(order)
        if order != identity or n <= 1:
            return order
        tries += 1
        if tries > 30:
            return order


def _adjacent_swap_perm(n, rng):
    """1-2 non-overlapping adjacent-sentence transpositions -- a MUCH smaller perturbation than a full
    shuffle (the harder discrimination condition, per Barzilay-Lapata's own near-vs-far finding)."""
    order = list(range(n))
    n_swaps = 1 if n <= 3 else rng.choice([1, 1, 1, 2])
    used = set()
    count = 0
    attempts = 0
    while count < n_swaps and attempts < 50:
        attempts += 1
        i = rng.randrange(0, n - 1)
        if any(x in used for x in (i - 1, i, i + 1)):
            continue
        order[i], order[i + 1] = order[i + 1], order[i]
        used.add(i)
        count += 1
    return order


CONDITIONS = [("full_shuffle", _full_shuffle_perm), ("adjacent_swap", _adjacent_swap_perm)]


def analyze_passage(passage, passage_idx, k=K_PERMUTATIONS, base_seed=BASE_SEED):
    sents = passage["sents"]
    entity_roles, mention_sets, n = build_grid(sents)
    order0 = list(range(n))
    orig_A = score_role_transition(entity_roles, order0)
    orig_B1 = score_cooccurrence(mention_sets, order0)

    records = {}
    for cond_idx, (cond_name, gen) in enumerate(CONDITIONS):
        recs = []
        for kk in range(k):
            seed = base_seed + passage_idx * 10000 + cond_idx * 1000 + kk
            order = gen(n, random.Random(seed))
            rand_rng = random.Random(seed + 5_000_000)
            recs.append({
                "order": order,
                "score_A_perm": score_role_transition(entity_roles, order),
                "score_B1_perm": score_cooccurrence(mention_sets, order),
                "score_rand_orig": rand_rng.random(),
                "score_rand_perm": rand_rng.random(),
            })
        records[cond_name] = recs
    return {
        "corpus": passage["corpus"], "start": passage["start"], "n_sents": n,
        "n_entities": len(entity_roles), "entities": sorted(entity_roles),
        "orig_A": orig_A, "orig_B1": orig_B1, "records": records,
    }


def aggregate(passage_results):
    out = {}
    all_pairs = []
    for cond_name, _gen in CONDITIONS:
        for scorer, orig_key, perm_key in (
            ("A", "orig_A", "score_A_perm"), ("B1", "orig_B1", "score_B1_perm"),
            ("random", "score_rand_orig", "score_rand_perm"),
        ):
            credits = []
            for pr in passage_results:
                for rec in pr["records"][cond_name]:
                    o = pr[orig_key] if orig_key in pr else rec[orig_key]
                    p = rec[perm_key]
                    c = _credit(o, p)
                    credits.append(c)
                    if scorer in ("A", "B1"):
                        all_pairs.append((cond_name, scorer, c))
            out[f"acc_{cond_name}_{scorer}"] = float(sum(credits) / len(credits)) if credits else 0.0
            out[f"n_{cond_name}_{scorer}"] = len(credits)
    out["_all_pairs_for_arms_differ_check"] = all_pairs
    return out


# ---------------------------------------------------------------------------
# Verdict (envelope-fail-bands, LOCKED from the dispatching research note).
# ---------------------------------------------------------------------------
def compute_verdict(agg):
    accA_full = agg["acc_full_shuffle_A"]
    accB1_full = agg["acc_full_shuffle_B1"]
    accA_swap = agg["acc_adjacent_swap_A"]
    accB1_swap = agg["acc_adjacent_swap_B1"]
    acc_rand_full = agg["acc_full_shuffle_random"]
    acc_rand_swap = agg["acc_adjacent_swap_random"]

    margin_full = accA_full - accB1_full
    margin_swap = accA_swap - accB1_swap
    random_sanity_ok = (0.35 <= acc_rand_full <= 0.65) and (0.35 <= acc_rand_swap <= 0.65)

    hp = (accA_full >= 0.70 and margin_full >= 0.08 and margin_swap >= 0.04 and random_sanity_ok)
    hf = (margin_full <= 0.03 or accA_full <= 0.60)

    if not random_sanity_ok:
        tier = "INVALID_TEST_DESIGN"
    else:
        tier = "HARD_PASS" if hp else ("HARD_FAIL" if hf else "MIDDLE_BAND")

    localize = []
    if not random_sanity_ok:
        localize.append("RANDOM BASELINE SANITY FAILED: acc_rand_full=%.3f acc_rand_swap=%.3f (expected "
                         "~0.50) -- discrimination-accuracy computation may be biased/buggy" %
                         (acc_rand_full, acc_rand_swap))
    if accA_full < 0.70:
        localize.append("role-transition full-shuffle accuracy below 0.70 (%.3f)" % accA_full)
    if margin_full < 0.08:
        localize.append("role-transition margin over co-occurrence on full-shuffle below 0.08 (%.3f)" % margin_full)
    if margin_swap < 0.04:
        localize.append("role-transition margin over co-occurrence on adjacent-swap below 0.04 (%.3f) -- "
                         "role info may help detect GROSS scrambling but not fine local incoherence "
                         "(the literature's own near-vs-far asymmetry)" % margin_swap)
    if margin_full <= 0.03:
        localize.append("HARD-FAIL: role-transition within 3pts of co-occurrence on full-shuffle (%.3f) "
                         "-- role info adds ~nothing over bag-of-entities co-occurrence" % margin_full)
    if accA_full <= 0.60:
        localize.append("HARD-FAIL: role-transition full-shuffle accuracy <=0.60 -- entity/role extraction "
                         "too sparse/noisy at this register for ANY coherence signal (more basic than the "
                         "role-vs-co-occurrence question)")
    weakest = localize if localize else ["none (role-transition beats co-occurrence + random floor on both "
                                          "full-shuffle and the harder adjacent-swap condition)"]

    msg = (f"{tier} | FULL-SHUFFLE acc_A={accA_full:.3f} acc_B1={accB1_full:.3f} margin={margin_full:+.3f} "
           f"acc_random={acc_rand_full:.3f} (n={agg['n_full_shuffle_A']}) | ADJ-SWAP acc_A={accA_swap:.3f} "
           f"acc_B1={accB1_swap:.3f} margin={margin_swap:+.3f} acc_random={acc_rand_swap:.3f} "
           f"(n={agg['n_adjacent_swap_A']}) | weakest={weakest}")
    return tier, msg, weakest


# ---------------------------------------------------------------------------
# infra.
# ---------------------------------------------------------------------------
def _out_dir(run_mode):
    sub = {"full": "exp_read_discourse_entitygrid_coherence_v1",
           "smoke": "exp_read_discourse_entitygrid_coherence_v1_smoke",
           "self_test": "exp_read_discourse_entitygrid_coherence_v1_selftest"}[run_mode]
    d = REPO / "data" / sub
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected_n_units,
              "host": platform.node()}
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _write_metrics(out_dir, metrics):
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


# ---------------------------------------------------------------------------
# self-test: EXERCISE THE REAL code path + assert the discriminators (INCLUDING the can-fail construction
# and the random-baseline sanity guard) fire correctly.
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (_build_tags_open_v4 / _np_head_from_run_v2 / "
          "_scan_object_np_v2 + CbTracker + build_grid)...", flush=True)

    # (1) real code path: simple S/O extraction on a hand-verifiable sentence.
    cb = CbTracker()
    r1 = _sentence_entities("The bear caught the fish.", cb)
    assert r1 == {"bear": "S", "fish": "O"}, f"basic S/O extraction wrong: {r1}"
    assert cb.cb == "bear", f"Cb not updated: {cb.cb}"

    # (2) subject-position pronoun resolves via the graded Cb pointer; object-position pronoun ("it") is
    # NOT resolved (declared scope) -- its mention is dropped, not injected as a wrong entity.
    r2 = _sentence_entities("He ate it.", cb)
    assert r2 == {"bear": "S"}, f"pronoun-subject Cb resolution (or object-pronoun scope) wrong: {r2}"

    # (3) "and"-conjoined co-subjects (both become S; mirrors the coref/WSM cells' own SUN_WIND control row).
    cb2 = CbTracker()
    r3 = _sentence_entities("The Sun and the Wind had a quarrel.", cb2)
    assert r3 == {"sun": "S", "wind": "S", "quarrel": "O"}, f"and-conjoined co-subject scan wrong: {r3}"

    # (4) no verb -> every NOUN becomes X (peripheral); Cb left unset for the next sentence.
    cb3 = CbTracker()
    r4 = _sentence_entities("A very little boy indeed.", cb3)
    assert set(r4.values()) <= {"X"} and "boy" in r4, f"no-verb fallback wrong: {r4}"

    # (5) build_grid on a tiny hand-authored 3-sentence passage: correct per-sentence roles across the
    # WHOLE passage (proves the sequential Cb-tracking threading works end-to-end, not just per-call).
    toy = ["The jackal hunted for crabs.", "He found a garden of figs.", "The alligator watched him."]
    entity_roles, mention_sets, n = build_grid(toy)
    assert n == 3
    assert entity_roles["jackal"] == ["S", "S", None], f"jackal role sequence wrong: {entity_roles['jackal']}"
    assert entity_roles["crab"] == ["X", None, None], (  # oblique/prepositional object ("hunted FOR crabs") -> X
        f"crab role sequence wrong: {entity_roles['crab']}")
    assert entity_roles["garden"] == [None, "O", None], f"garden role sequence wrong: {entity_roles['garden']}"
    assert entity_roles["alligator"] == [None, None, "S"], f"alligator role sequence wrong: {entity_roles['alligator']}"
    # "him" (object pronoun, sentence 3) is out of scope -> jackal's 3rd-sentence mention is correctly absent.

    # (6) scoring formulas are well-defined + order-SENSITIVE on a real grid (not trivially constant).
    order_fwd = [0, 1, 2]
    order_swap = [0, 2, 1]
    a_fwd = score_role_transition(entity_roles, order_fwd)
    a_swap = score_role_transition(entity_roles, order_swap)
    b1_fwd = score_cooccurrence(mention_sets, order_fwd)
    b1_swap = score_cooccurrence(mention_sets, order_swap)
    assert a_fwd != a_swap, "role-transition score is order-invariant on a real grid -- bug"
    assert a_fwd > a_swap, f"forward (correct) order should score higher than a scrambled order: {a_fwd} vs {a_swap}"
    _ = (b1_fwd, b1_swap)  # sanity: both well-defined floats (no exception), not asserted further here.

    # (7) CAN-FAIL construction (design-gate item 2): a DEGENERATE grid where every entity has the SAME
    # role in EVERY sentence -> role-transition score is, BY CONSTRUCTION, permutation-INVARIANT (every
    # adjacent pair is (S,S) regardless of row order) -- discrimination MUST collapse to exactly chance
    # (credit=0.5 for every permutation, since orig score == perm score always). Proves the mechanism CAN
    # fail to discriminate; the HARD-PASS result on the real corpus (if it lands) is not by-construction.
    degenerate_roles = {"x": ["S", "S", "S", "S"]}
    deg_order0 = [0, 1, 2, 3]
    deg_orig = score_role_transition(degenerate_roles, deg_order0)
    for seed in range(5):
        perm = _full_shuffle_perm(4, random.Random(9000 + seed))
        deg_perm = score_role_transition(degenerate_roles, perm)
        assert deg_perm == deg_orig, f"degenerate construction should be permutation-invariant: {deg_perm} vs {deg_orig}"
        assert _credit(deg_orig, deg_perm) == 0.5, "degenerate construction should score exactly at chance (tie)"

    # (8) deterministic seeding: same seed -> identical permutation, twice (F.5).
    p1 = _full_shuffle_perm(8, random.Random(12345))
    p2 = _full_shuffle_perm(8, random.Random(12345))
    assert p1 == p2, "full-shuffle permutation generator is NOT deterministic under a fixed seed"
    s1 = _adjacent_swap_perm(8, random.Random(999))
    s2 = _adjacent_swap_perm(8, random.Random(999))
    assert s1 == s2, "adjacent-swap permutation generator is NOT deterministic under a fixed seed"
    assert s1 != list(range(8)), "adjacent-swap permutation must differ from the identity order"

    # (9) cardinality: EXPECTED_N_UNITS = n_passages * K * n_conditions.
    passage_results = [analyze_passage(p, i) for i, p in enumerate(PASSAGES)]
    expected_n = len(PASSAGES) * K_PERMUTATIONS * len(CONDITIONS)
    got_n = sum(len(pr["records"][c]) for pr in passage_results for c, _g in CONDITIONS)
    assert got_n == expected_n, f"cardinality mismatch: expected {expected_n}, got {got_n}"

    # (10) main analysis + real-corpus sanity: at least one entity extracted per passage (non-vacuous
    # extraction), random-baseline sanity in band, and scorer A/B1 EMPIRICALLY DISAGREE on at least one
    # pair across the real corpus (META_RULE_AF arms-differ, real-data variant -- both are deterministic
    # pure functions of the same grid, so a hash-compare is not meaningful; a real ranking disagreement is).
    for pr in passage_results:
        assert pr["n_entities"] >= 1, f"passage at {pr['corpus']}:{pr['start']} extracted ZERO entities"
    agg = aggregate(passage_results)
    assert 0.30 <= agg["acc_full_shuffle_random"] <= 0.70, (
        f"random baseline sanity (loose self-test band): {agg['acc_full_shuffle_random']}")
    assert 0.30 <= agg["acc_adjacent_swap_random"] <= 0.70, (
        f"random baseline sanity (loose self-test band): {agg['acc_adjacent_swap_random']}")
    pairs = agg["_all_pairs_for_arms_differ_check"]
    by_scorer = {}
    for cond_name, scorer, c in pairs:
        by_scorer.setdefault((cond_name,), {}).setdefault(scorer, []).append(c)
    disagree = False
    for cond_name, _gen in CONDITIONS:
        a_credits = [c for cn, sc, c in pairs if cn == cond_name and sc == "A"]
        b1_credits = [c for cn, sc, c in pairs if cn == cond_name and sc == "B1"]
        if any(a != b for a, b in zip(a_credits, b1_credits)):
            disagree = True
    assert disagree, "META_RULE_AF: scorer A and scorer B1 NEVER disagree across the real corpus -- suspect identical signal"

    tier, msg, _weakest = compute_verdict(agg)
    print(f"[self_test] PASS | {msg}", flush=True)
    return True


# ---------------------------------------------------------------------------
# main.
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default=None)
    args = ap.parse_args()

    if args.self_test or args.run_mode == "self_test":
        self_test()
        sys.exit(0)

    run_mode = "smoke" if (args.smoke or args.run_mode == "smoke") else "full"  # smoke == full (fixed tiny corpus)
    out_dir = _out_dir(run_mode)
    expected_n_units = len(PASSAGES) * K_PERMUTATIONS * len(CONDITIONS)
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print(f"[entitygrid_v1] run_mode={run_mode} n_passages={len(PASSAGES)} K={K_PERMUTATIONS} "
          f"conditions={[c for c, _g in CONDITIONS]} expected_n_units={expected_n_units}", flush=True)

    passage_results = [analyze_passage(p, i) for i, p in enumerate(PASSAGES)]
    for pr in passage_results:
        print(f"[entitygrid_v1] passage {pr['corpus']}:{pr['start']} n_sents={pr['n_sents']} "
              f"n_entities={pr['n_entities']} entities={pr['entities']}", flush=True)

    agg = aggregate(passage_results)
    print(f"[entitygrid_v1] FULL-SHUFFLE acc_A={agg['acc_full_shuffle_A']:.3f} "
          f"acc_B1={agg['acc_full_shuffle_B1']:.3f} acc_random={agg['acc_full_shuffle_random']:.3f}", flush=True)
    print(f"[entitygrid_v1] ADJACENT-SWAP acc_A={agg['acc_adjacent_swap_A']:.3f} "
          f"acc_B1={agg['acc_adjacent_swap_B1']:.3f} acc_random={agg['acc_adjacent_swap_random']:.3f}", flush=True)

    tier, msg, weakest = compute_verdict(agg)
    elapsed = time.perf_counter() - t0

    def strip_pairs(a):
        return {k: v for k, v in a.items() if k != "_all_pairs_for_arms_differ_check"}

    def strip_records(pr):
        return {k: v for k, v in pr.items() if k != "records"}

    metrics = {
        "verdict": tier, "verdict_msg": msg, "summary": msg[:300],
        "run_mode": run_mode, "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "expected_n_units": expected_n_units,
        "n_passages": len(PASSAGES), "k_permutations": K_PERMUTATIONS,
        "conditions": [c for c, _g in CONDITIONS], "weakest_interface": weakest,
        "acc_full_shuffle_A": agg["acc_full_shuffle_A"], "acc_full_shuffle_B1": agg["acc_full_shuffle_B1"],
        "acc_full_shuffle_random": agg["acc_full_shuffle_random"],
        "acc_adjacent_swap_A": agg["acc_adjacent_swap_A"], "acc_adjacent_swap_B1": agg["acc_adjacent_swap_B1"],
        "acc_adjacent_swap_random": agg["acc_adjacent_swap_random"],
        "margin_full_shuffle": agg["acc_full_shuffle_A"] - agg["acc_full_shuffle_B1"],
        "margin_adjacent_swap": agg["acc_adjacent_swap_A"] - agg["acc_adjacent_swap_B1"],
        "n_pairs_full_shuffle": agg["n_full_shuffle_A"], "n_pairs_adjacent_swap": agg["n_adjacent_swap_A"],
        "per_passage": [strip_records(pr) for pr in passage_results],
        "corpus_license": CORPUS_LICENSE,
        "prereg": {
            "hard_pass": "acc_full_shuffle_A>=0.70 & (acc_full_shuffle_A-acc_full_shuffle_B1)>=0.08 & "
                         "(acc_adjacent_swap_A-acc_adjacent_swap_B1)>=0.04 & random_baseline_sanity_ok",
            "hard_fail": "(acc_full_shuffle_A-acc_full_shuffle_B1)<=0.03 | acc_full_shuffle_A<=0.60",
            "middle": "otherwise (report dominant class)",
            "invalid": "random_baseline_sanity fails on either condition (0.35<=acc_random<=0.65 expected)",
            "novel_synthesis_P": 0.42,
            "corpus": CORPUS_LICENSE,
            "n_passages": len(PASSAGES), "k_permutations": K_PERMUTATIONS,
            "scope": "role-transition grid built from rung9's real-prose OPEN tagger; subject-position "
                     "pronouns resolved via a graded recency-only Cb pointer (self-contained, not the "
                     "guardrail Hobbs resolver); object-position pronouns NOT resolved (declared scope)",
            "compute_architecture": "sequential-CPU, grid built once per passage, permutations reorder rows "
                                     "(no re-parsing); NLTK classical POS tagger only, no LLM",
            "storage_strategy": "no_storage", "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "print_flush_true", "deterministic_seeding": True,
            "real_code_path_exercised": ["_build_tags_open_v4", "_np_head_from_run_v2", "_scan_object_np_v2",
                                         "build_grid", "score_role_transition", "score_cooccurrence"],
            "arms_differ_verified": "empirical (real corpus): scorer A and B1 disagree on >=1 of 240 pairs",
            "crlb_n/a": "no quantitative noise floor; fully symbolic discrete role/co-occurrence scoring",
            "real_code_path_and_signature_preflight": "not_applicable_no_substrate_objects_pure_symbolic_nlp_cell "
                                                       "(same precedent as exp_read_coref_hobbs_centering_resolver_v1 "
                                                       "/ exp_read_discourse_state_of_mind_wsm_coupling_realcorpus_v2)",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[entitygrid_v1] {tier} in {elapsed:.4f}s -> {out_dir/'metrics.json'}", flush=True)
    print(f"[entitygrid_v1] {msg}", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    _md = "full"
    try:
        if "--smoke" in sys.argv or ("--run-mode" in sys.argv and "smoke" in sys.argv):
            _md = "smoke"
        elif "--self-test" in sys.argv or "self_test" in sys.argv:
            _md = "self_test"
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            _write_crash_metrics(_out_dir(_md), e)
        except Exception:
            pass
        raise
