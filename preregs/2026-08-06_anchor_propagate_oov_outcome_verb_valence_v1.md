# Pre-reg: anchor + propagate OOV outcome-verb result-valence (WordNet-neighborhood + opposition)

Date: 2026-08-06. Status: **PRE-REGISTERED, NOT YET EXECUTED** (spec-only cycle, per FORMALIZE-drill
discipline; a cell-author builds and runs this later). Companion spec (read first -- has the full
brain->organ map, the anchor's honest earned-vs-supplied breakdown, the direction-question adjudication,
and the light-verb ceiling analysis): `notes/research_anchor_propagate_oov_outcome_verb_valence_
2026-08-06.md`. This is a NEW PROPOSE-mechanism swap into the EXISTING `hdlab/word_acquisition_loop.py`
scaffolding (propose-trigger / `MIN_CONFIRM=2` consolidation / write-back are REUSED VERBATIM from
increment 1/1b, same convention increment 1b itself used swapping out increment 1's Channel A/B). It
supersedes `preregs/2026-08-06_grounded_word_acquisition_increment1b_v1.md`'s PROPOSE mechanism only
(clause-transitivity structural typer, measured HARD_FAIL, `data/exp_grounded_word_acquisition_
increment1b_v1/metrics.json`) -- everything downstream of `register_acquired_outcome` is untouched.

## What is being built (delta from increment 1b, PROPOSE mechanism only)

1. **NEW: `wordnet_neighbor_propagate(lemma) -> Optional[str]` (POS/NEG/None).** Two-stage, opposition
   before neighborhood (see companion spec Section 3c for full rationale):
   - Stage A (opposition, higher precedence): lift `PolarityLexicon._antonyms` from
     `experiments/exp_arc_aggregation_polarity_ci_v1.py` (clean-copy convention, same pattern
     `hdlab/lexical_similarity.py`/`hdlab/verb_lexical_similarity.py` already used promoting from
     `exp_n11c*` -- copy the method's logic into a new small hdlab-only helper, do NOT import
     `experiments/` from `hdlab/`, matching both existing modules' own documented import discipline).
     `antonyms = _antonyms(lemma) & ANCHOR_WORDS`. If non-empty, predict the OPPOSITE of the
     (majority, tie -> abstain) polarity of the matched anchor word(s).
   - Stage B (neighborhood vote, only if Stage A found nothing): `wn.synsets(lemma, pos=wn.VERB)` (nltk
     WordNet, already a promoted dependency via `hdlab/animacy_lexicon.py`). For each `a` in
     `ANCHOR_WORDS` with at least one verb synset, compute `sim(lemma, a) = max` over
     `wn.path_similarity(s_lemma, s_a)` across all synset pairs (`path_similarity` chosen over
     `wu_palmer_similarity` for this pre-reg -- both are native, deterministic, glass-box; `path_similarity`
     is the simpler/more conservative choice and is the one used for the pre-registered bands below; report
     `wu_palmer_similarity` as a secondary diagnostic, not a second gate, to avoid post-hoc metric
     shopping). Keep neighbors with `sim >= NEIGHBOR_FLOOR`. Predict the `sim`-weighted-majority polarity
     of the kept neighbor set; **abstain** if the kept set is empty, or if the vote margin (winning-pole
     weighted-sum minus losing-pole weighted-sum, normalized) is `< VOTE_MARGIN`.
   - Pre-registered constants (fixed BEFORE any run, not tuned post-hoc): `NEIGHBOR_FLOOR = 0.20`
     (WordNet `path_similarity` for near-synonyms across the ANCHOR's own internal pairs, e.g.
     `sink`/`fall` or `mend`/`repair`, is typically well above this; 0.20 is a conservative floor chosen
     to admit true near-synonyms while excluding merely-same-part-of-speech unrelated verbs -- report the
     ANCHOR's own internal pairwise `path_similarity` distribution in the completion report to confirm
     this floor was not arbitrary after the fact), `VOTE_MARGIN = 0.15` (same numeric convention as
     `verb_lexical_similarity.classify_2way`'s existing `margin` parameter, for direct comparability).
2. **NEW: `ANCHOR_WORDS = frozenset(OUTCOME_SEED_POS) | frozenset(OUTCOME_SEED_NEG)` (52 words) with
   an explicit `ANCHOR_POLARITY: Dict[str,str]` derived from which seed-dict each lemma is in.** Does
   NOT include `OUTCOME_HELDOUT_POS`/`_NEG` (companion spec Section 2's honesty rationale) -- run as a
   SEPARATE, explicitly-labeled ablation arm with the ~78-word anchor (`ANCHOR_WORDS_EXTENDED`) to
   measure whether anchor size matters, but the 52-word arm is PRIMARY for the pre-registered bands.
3. **CONSOLIDATION/WRITE-BACK: REUSED VERBATIM, zero code change** -- `MIN_CONFIRM`-style consolidation
   is not needed here in the SAME form as increment 1/1b (this mechanism is deterministic per-lemma, not
   sampled from noisy corpus mining), so CONSOLIDATE simplifies to: compute
   `wordnet_neighbor_propagate(lemma)` once per lemma; if non-`None`, call
   `register_acquired_outcome(lemma, polarity)` (existing, unchanged API,
   `hdlab/verb_lexical_similarity.py`) directly. Document this simplification explicitly in the
   completion report as a deliberate delta from increment 1/1b's noisy-exposure-driven consolidation gate
   (this mechanism's "noise" is WordNet sense-ambiguity, not corpus-sampling variance, and needs a
   DIFFERENT anti-drift control -- see the noise-canary control below, not `MIN_CONFIRM`).
4. **Consumer paths: UNCHANGED.** `hdlab/goal_typing.py`'s `_verb_classes` Tier-3 sentinel and
   `_tier2_outcome_polarity_scan`'s `classify_2way` fallback both already consult
   `ACQUIRED_OUTCOME_VERB_FEATURES` (confirmed by direct code read of `_features_for`'s choke-point) --
   zero new plumbing.

## Held-out set / test bed

`experiments/data/goal_bearing_modern_eval_v1.jsonl`, the same 36-item OOV-outcome subset increment 1b
scored (`outcome_in_lexicon: false`, re-derived directly this session: 23 met / 13 unmet, majority floor
`23/36 = 0.6389`). **Non-circularity gate (structural, checked at build time, not just claimed):** none
of the 36 items' `outcome_verb_lemma` values overlap `ANCHOR_WORDS` or `ANCHOR_WORDS_EXTENDED` by
construction (both are drawn from `CLASS_REGISTRY`'s pre-existing seed/held-out vocabulary, independently
authored before this eval file existed) -- verify this assertion programmatically at build time and
FAIL the cell immediately (before scoring) if any overlap is found.

**Eligible-subset split (reused exactly from `preregs/2026-08-06_grounded_word_acquisition_increment1b_v1.md`'s
own "Coverage sub-partition," re-verified this session, NOT redefined):** `18/36` items have
`goal_verb_lemma` in the literal base `DESIDERATIVE_PASS` set (`want, hope, wish, mean, plan, intend,
aim, long, yearn, desire`) and are reachable via the FULL `congruence_decision` organ path (gold: 12
met / 6 unmet, majority floor `0.6667`); the other `18/36` fall through to the flat V2-lexicon-fallback
path regardless (gold: 11 met / 7 unmet, majority floor `0.6111`). Report BOTH subsets' accuracy
separately alongside the pooled 36-item primary number, exactly as increment 1b did.

**Light-verb honest-ceiling annotation (pre-registered, NOT a gate, a REPORTING requirement):** of the 33
unique outcome-verb lemmas, pre-register the following 17 as `LIGHT_VERB_NO_INHERENT_VALENCE` (companion
spec Section 4's list, decided from each verb's LEXICAL TYPE before running anything, not from gold
labels): `be, have, come, go, give, take, put, find, make, carry, buy, drink, turn, curve, whisper, drag,
practice`. Report `content_verb_subset_accuracy` (the 36-item primary metric restricted to items whose
`outcome_verb_lemma` is NOT in this list) as a SEPARATE, informative number alongside the pooled 36-item
number -- this is the fairer test of the mechanism itself, and the pooled number is expected to be
capped below it by construction; do not treat a moderate pooled number alone as a verdict without this
breakdown.

## Falsifiable predictions (HARD-PASS / HARD-FAIL / MIDDLE-BAND)

**Primary metric:** `primary_accuracy` = fraction of the 36 OOV-outcome-verb items where the LIVE
`congruence_with_lexicon_fallback` call (Tier-3 overlay populated by this design, everything else
unchanged) correctly types MET/UNMET vs gold. Untyped/abstain = MISS (coverage-inclusive scoring, same
convention increment 1b used).

**HARD-PASS** (ALL of the following):
1. `primary_accuracy >= 27/36` (0.75) AND `unmet_recall >= 5/13` (rules out a degenerate
   always-guess-MET strategy, which scores exactly 0.6389 and must not pass gate 1 -- identical
   class-imbalance guard to increment 1b's own gate 1).
2. `content_verb_subset_accuracy >= 0.70` on the light-verb-excluded subset (the FAIR test of the
   mechanism; report the exact N for this subset at build time -- expected ~16-19 of the 33 unique
   lemmas' corresponding eval items, per the companion spec's pre-registered light-verb list).
3. **Non-circularity gate (structural, must ALSO pass or HARD-PASS is void regardless of accuracy):**
   - (a) SCRAMBLE: fixed-seed (5 seeds, same convention as `verb_lexical_similarity.py::self_test`'s
     circularity check) random permutation of `ANCHOR_POLARITY`'s word->pole assignment, WordNet graph
     UNCHANGED. `scrambled_primary_accuracy` must fall within `[0.35, 0.65]` (collapse toward the
     ~50%-of-mislabeled-anchor base rate) while real `primary_accuracy` clears gate 1. Gap
     `(primary_accuracy - scrambled_primary_accuracy) >= 0.20`.
   - (b) RANDOM-GRAPH ablation: replace the real WordNet-neighbor edges with a degree-matched random
     graph over `ANCHOR_WORDS` (fixed seed, same `torch.randperm`-with-manual-seed convention this
     module family already uses). `random_graph_accuracy` must also fall within `[0.35, 0.65]`.
   - (c) DIRECTION-REMOVED ablation: a neighborhood-only arm that finds the SAME WordNet neighbors
     (Stage B unchanged) but reads only `EVENT_DOMAIN` membership (never `POS_AFFECT`/`NEG_AFFECT`),
     forced to output the domain's majority-gold-in-training-anchor guess or abstain --
     `direction_removed_accuracy` must NOT exceed `0.6389` (the majority floor) by more than
     `MUSTFAIL_EPS = 0.05`. This isolates that DIRECTION (not mere relatedness) is load-bearing.
4. `noise_canary_consolidated_count == 0` on a pre-registered 8-word noise-canary set (semantically
   neutral/manner verbs NOT drawn from the 36-item eval's own vocabulary and NOT in `ANCHOR_WORDS`:
   `walk, sit, speak, stand, sigh, glance, nod, pause`) -- none should get confidently consolidated with
   a polarity via either Stage A or Stage B (mirrors increment 1b's own noise-canary discipline, which
   caught a real leak there: `2/8` wrongly consolidated).

**HARD-FAIL** (ANY of the following):
- `primary_accuracy <= 23/36` (0.6389) -- does not beat blind majority-class guessing.
- `scrambled_primary_accuracy` stays within `0.10` of real `primary_accuracy` -- no genuine
  anchor-content dependence (would mean whatever signal exists is not coming from the anchor's actual
  polarity labels).
- `random_graph_accuracy` stays within `0.10` of real `primary_accuracy` -- no genuine WordNet-structure
  dependence (would mean the win, if any, comes from something other than real relatedness).
- `direction_removed_accuracy > 0.6389 + 0.10` -- would mean mere relatedness (without ever reading
  polarity) is doing the work, contradicting this design's own claim that direction must come from the
  anchor/opposition, not from neighborhood alone; genuinely informative either way, report as such.
- `noise_canary_consolidated_count >= 1` -- anti-drift leak.
- `content_verb_subset_accuracy < 0.55` -- even on the FAIR (light-verb-excluded) subset the mechanism
  underperforms; would falsify the companion spec's central claim that WordNet-relatedness + opposition
  is a workable channel for genuinely lexically-valenced verbs specifically.

**MIDDLE-BAND:** `primary_accuracy` in `(0.6389, 0.75)`, OR gate 1/2 clear but a non-circularity gate is
borderline (e.g. `scrambled_primary_accuracy` in `[0.55, 0.65]` -- partial but not full collapse), OR
`content_verb_subset_accuracy` in `[0.55, 0.70)`. Report honestly, do not force a label either direction
-- same discipline `hdlab/goal_typing.py`'s own module docstring MIDDLE_BAND precedent and increment
1b's pre-reg both already establish.

## Ablation / diagnostic predictions (informational, pre-registered)

1. **`ANCHOR_WORDS` (52) vs `ANCHOR_WORDS_EXTENDED` (~78, includes `OUTCOME_HELDOUT_POS`/`_NEG`)** --
   falsifiable sub-prediction: a larger anchor should give `content_verb_subset_accuracy` a small
   positive or near-zero lift (more neighbor candidates), NOT a large one -- a large lift would suggest
   the 52-word anchor was under-sized relative to what the companion spec's "keep it small, traceable
   provenance" argument assumed, and should prompt revisiting that argument, not just banking the gain.
2. **Antonym-Stage-A-fires vs Neighborhood-Stage-B-fires, per-item breakdown** -- report which of the 36
   items' propagated polarity (if any) came from Stage A vs Stage B; the companion spec's design
   rationale predicts Stage A (explicit antonym) should fire RARELY (WordNet's `lemma.antonyms()`
   coverage for verbs is sparse) and Stage B should carry most of the load -- confirm or refute.
3. **`path_similarity` vs `wu_palmer_similarity` secondary comparison** -- report both metrics' resulting
   `primary_accuracy` even though only `path_similarity` is gated; if `wu_palmer_similarity` differs
   substantially, flag for a follow-up (not a post-hoc metric swap within this pre-reg).
4. **`croak` and other WordNet-primary-sense-mismatch cases** -- report per-item which propagated
   predictions (if any) came from a plausibly WRONG WordNet sense (manual annotation against the item's
   actual usage), as a scoped, honest accounting of the WSD gap the companion spec names but does not
   solve.

## Compute architecture

Sequential-CPU, `nltk.corpus.wordnet` (already a dependency, no new install). No training, no GPU, no
gradient step anywhere in this mechanism -- purely deterministic graph lookups + a weighted vote.
`crlb: n/a` (fixed 36-item classification against gold, not a capacity/argmax-noise-floor cell).
`storage_strategy`: `ACQUIRED_OUTCOME_VERB_FEATURES` remains process-local/in-memory, unchanged from
increment 1/1b. Expected wall time: low tens of seconds (33 unique lemma lookups x ~52-78 anchor
comparisons each, all O(1) WordNet API calls, no corpus scan).

## Cardinality / discriminator / atomicity gates (SCHEMA-VET checklist)

- `cardinality_ok`: `EXPECTED_N_UNITS` = 33 (per-unique-lemma propagation, resumable per-lemma) + 1
  (noise-canary batch) + 5 (scramble seeds) + 1 (random-graph ablation) + 1 (direction-removed ablation)
  + 1 (extended-anchor ablation) = 42 units minimum; resumable per-unit via `tools/exp_checkpoint.py`.
- `discriminator_reachability`: TRUE -- 36-item binary classification, majority floor 0.6389, ceiling
  1.0, not saturated-by-construction; content-verb subset similarly non-saturated.
- `baseline_in_band`: N/A for the primary arm (direct measurement against fixed gold); reference
  baselines (0.6389 majority, 0.4444 increment-1b) are REAL, measured off the live eval file and
  `data/exp_grounded_word_acquisition_increment1b_v1/metrics.json` respectively, not assumed.
- `arms_differ_verified`: real vs scrambled `ACQUIRED_OUTCOME_VERB_FEATURES` entries must hash-differ
  (same META_RULE_AF-style check as this file family's existing self-tests); random-graph arm's edge set
  must differ from the real WordNet edge set by construction (assert non-identical).
- `final_metrics_atomicity`: `tmp_replace`.
- `deterministic_seeding`: fixed integer seeds throughout (no `hash()`-derived seeding, PROT-023/F.5
  compliant); WordNet lookups are themselves deterministic (no seed needed) but the scramble/random-graph
  ablations need fixed seeds, same as this module family's convention.
- `progress_logging`: `print_flush` per-lemma (33 lemmas, low tens of seconds -- heartbeat optional given
  the small N, but include for consistency with the mandatory cell template).
- `non_overlap_assert`: programmatic check that `ANCHOR_WORDS`/`ANCHOR_WORDS_EXTENDED` contain ZERO of
  the 36 eval items' `outcome_verb_lemma` values, asserted BEFORE scoring (fail loud, not a silent
  data-leak risk).

## Cert gate (MANDATORY -- touches production `hdlab/verb_lexical_similarity.py` write-back consumer path)

`python verification/run_certification.py` via `.venv/Scripts/python.exe` BEFORE and AFTER; baseline to
reproduce: 220 passed, 3 skipped (same baseline increment 1b's own pre-reg cites, unchanged by that
cell's own HARD_FAIL since it was standalone). This design ONLY populates the ALREADY-EMPTY-AT-IMPORT
`ACQUIRED_OUTCOME_VERB_FEATURES` overlay via the EXISTING `register_acquired_outcome` API -- strict ADD,
no existing test item's verb vocabulary can collide unless independently OOV of both Tier-1 AND Tier-2
today; trace any such collision by hand against `verification/test_outcome_valence_goal_congruence.py`'s
decisive items before dispatch, same discipline increment 1b's own pre-reg specifies.

## Files to be touched

- `hdlab/verb_lexical_similarity.py` (EDIT, strict-ADD) -- new `ANCHOR_WORDS`/`ANCHOR_WORDS_EXTENDED`/
  `ANCHOR_POLARITY` module-level constants (derived from existing `OUTCOME_SEED_POS`/`_NEG`/
  `OUTCOME_HELDOUT_POS`/`_NEG`, zero new authoring); `register_acquired_outcome` UNCHANGED.
- `hdlab/wordnet_polarity_propagation.py` (NEW, hdlab-only, no `experiments/` import at runtime) --
  `wordnet_neighbor_propagate(lemma)`, the lifted `_antonyms` helper (clean-copy from
  `experiments/exp_arc_aggregation_polarity_ci_v1.PolarityLexicon._antonyms`, credited in the docstring
  per this repo's existing promotion-docstring convention), the WordNet neighbor-search + weighted vote.
- `experiments/exp_wordnet_polarity_propagation_v1.py` (NEW) -- the pre-reg'd cell: builds the anchor,
  runs propagation over the 33 unique OOV lemmas, populates the overlay, scores against the 36-item eval
  via the EXISTING `congruence_with_lexicon_fallback`, runs all ablations/controls above, self-test per
  the mandatory cell template. `experiments/exp_grounded_word_acquisition_increment1_v1.py` /
  `_increment1b_v1.py` and `experiments/data/goal_bearing_modern_eval_v1.jsonl` LEFT UNTOUCHED
  (source-of-truth convention, same as increment 1b's own pre-reg).
- `experiments/exp_arc_aggregation_polarity_ci_v1.py` -- NO CHANGE (source of the lifted `_antonyms`
  logic; read-only reference, not imported at runtime per the hdlab-only-dependency convention).

## Prior-work check (per exp_dev standing discipline)

Direct prior-art, checked against `data/capability_registry.jsonl` this session, not paraphrased from
memory: `grounded_word_acquisition_loop_increment1` (`gate_decision: SHELVE`, revival criteria satisfied
by increment 1b, itself HARD_FAILed -- this pre-reg is a THIRD attempt at the same revival criterion,
now swapping the signal source from clause-transitivity to WordNet-relatedness+opposition, not repeating
either prior attempt's approach); `hdlab/reasoner.py composed entry` (`built_2026-07-25_then_
abandoned_2026-07-27` -- the SOURCE of the lifted `PolarityLexicon`/antonym mechanism, confirmed SHELVED
with zero current consumers, so this pre-reg gives it a genuinely new one rather than duplicating active
functionality); `hdlab/animacy_lexicon.py` (`registered_2026-08-03`, WIRED -- confirms WordNet is an
already-adopted, glass-box hdlab dependency, not a new external-tool risk). No existing
`hdlab/wordnet_polarity_propagation.py`-equivalent module found (checked: no hit for `wordnet` combined
with `polarity`/`propagat` anywhere under `hdlab/` this session) -- confirmed genuinely new, not a
duplicate build.
