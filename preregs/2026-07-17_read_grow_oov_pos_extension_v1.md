# Pre-reg: exp_read_grow_oov_pos_extension_v1 (CHEAP DECISIVE TEST -- OOV-noun coverage via classical POS tagging)

Cell: `experiments/exp_read_grow_oov_pos_extension_v1.py`
Trigger: `notes/research_open_text_glassbox_ie_reading_frontier_curriculum_2026-07-16.md` section (b) "Cheap
decisive test" / section (c) Prediction 1. Director spawn-prompt: build + ship this cell as a NEW standalone
cell (does not edit `exp_read_grow_foundation_realprose_glassbox_ie_v2.py` or
`exp_read_grow_openvocab_fastmap_v1.py` -- the latter concurrently edited by a sibling cell).

Question: does adding a CLASSICAL statistical POS tagger (for OOV nouns the hand-lexicon can't tag) feeding
UNTYPED noun slots into the EXISTING closed-schema glass-box grammar recover substantial open-text coverage
WHILE preserving high precision? NO LLM, NO neural component anywhere.

## Prior-work check (substrate-KB concept-query, per USER-locked discipline)
`bash tools/substrate_query.sh "classical POS tagger OOV noun coverage open text glass-box extraction
syntactic frame"` -- confidence=0.2764, ALL top-5 hits below cosine 0.30 (top hit: entity='syntactical',
cosine=0.2764; next: 'extraction' 0.2676, 'CN_tactical' 0.2646, 'syntactic' 0.2627, an OpenIE citations note
0.2549). Verdict: NONE at cosine>0.30 -- genuinely novel, not a rediscovery.

## Pieces composed (reuse of mechanism, with provenance)
- Closed-schema parser: `exp_read_grow_foundation_realprose_glassbox_ie_v2.py::ie_extract` -- IMPORTED
  verbatim, used UNMODIFIED as the CURRENT arm. Also imports its pure helpers (`_tag_token`, `_tokenize`,
  `_resolve_relation`, `_split_coord`) and closed-lexicon constants (`ADJS`, `ENTITIES`, `RELATIONS`,
  `ANIMALS`, `FOODS`, `PLACES`).
- Classical POS tagger: `nltk.pos_tag` with the `averaged_perceptron_tagger_eng` model -- a real external
  classical (non-neural) structured-perceptron tagger call, context-aware over each full sentence.
- NEW (this cell): `_extract_core` (a faithful re-implementation of v2's structural grammar, PARITY-verified
  bit-for-bit against the import at self-test), `_build_tags_extended` (closed-lexicon-first tagging with a
  tagger+morphology fallback for UNK tokens), `_morph_noun_shape` / `_oov_lemma` (suffix/word-shape
  morphology), the 10-template hand-authored OOV-noun corpus generator.

## Design (arms, per research note section (b))
- **CURRENT**: `ie_extract` unchanged. A noun not in the closed lexicon (`ENTITIES`) is tagged UNK and
  cannot fill a role slot -- expected near-total abstain on the OOV corpus.
- **POS_EXTENDED**: identical grammar rules; a token the closed lexicon tags UNK gets tagged via the
  classical POS tagger (NN/NNS/NNP/NNPS -> NOUN) OR suffix/word-shape morphology (productive plural -s,
  common nominalizing suffixes, capitalization), deferring to the tagger's own verb-family judgment to avoid
  the naive '-s ending' heuristic mis-promoting a 3rd-person-singular verb. No lexicon entry created, no
  fact-content asserted about the OOV word -- pure syntactic-category acceptance (Fisher/Gleitman
  syntactic-bootstrapping, research note Rung 2).

## Corpus (hand-authored; scope decision declared up front)
10 template classes (simple SVO subj/obj/both-OOV, SVO_PREP lives_in subj/obj-OOV, adjective-modified,
subject-coordination both-OOV, passive agent-OOV, chase-SVO subj-OOV, bare-plural-no-determiner both-OOV),
each instantiated `N_PER_TEMPLATE=4` times per seed from OOV word pools (10 animals / 8 foods / 8 places)
confirmed disjoint from the closed `ENTITIES` lexicon (self-test assertion). Function words, ALL verbs, and
adjectives/adverbs are held CLOSED (never OOV) in every template -- this isolates the OOV-NOUN-coverage
question specifically, per the arm design ("holding the existing closed-schema grammar rules fixed"). A
harder fully-open register (real OneStopEnglish/Simple-Wikipedia prose with OOV verbs too) would likely land
in the corrected classical envelope (P:60-85%/R:30-55%, research note section (a)/3) rather than this
controlled corpus's near-ceiling precision -- declared, not hidden.

SCOPE DECISION (not using UD-EWT/GUM independent tagger-accuracy benchmark): NLTK's tagger accuracy is
independently benchmarked in the CITED literature (96-97% PTB); downloading/parsing a CoNLL-U treebank is
heavier than a "cheap decisive test" warrants. Self-test instead asserts hand-verified expected tags on this
cell's own OOV words as a lightweight sanity check (not a full independent benchmark).

HONEST FINDING discovered during design (reported, not hidden): a coordination sentence with ONE known
conjunct + ONE OOV conjunct does NOT fully abstain under CURRENT -- the OOV conjunct is silently invisible
to `noun_idx` (never enters coordination detection), so CURRENT emits a single CORRECT-BUT-INCOMPLETE triple
for the known conjunct (silently drops the OOV fact, no error signal). The primary corpus therefore uses
BOTH-conjuncts-OOV coordination (a clean full-abstain case, verified at self-test); the mixed-conjunct case
is reported separately as `mixed_coord_diagnostic` (non-gating, an additional honest finding, not folded
into the HARD-PASS/FAIL bands).

CORPUS-GENERATION BUG CAUGHT AT SMOKE (reported per discipline, not hidden): the first smoke run
(pre-fix) landed `precision_newly_covered_pooled=0.9545` (2/40 sentences mismatched), traced to a naive
`{word}+"s"` pluralization colliding with the OOV food "moss" (already ending in "-ss"), producing the
non-word "mosss" which the (correctly conservative) singularization heuristic could not reduce back to
"moss". This was a CORPUS-TEMPLATE bug, not a tagger/mechanism precision failure -- fixed via proper
English `-es` pluralization for sibilant-final words (`_pluralize`); re-run confirmed
`precision_newly_covered_pooled=1.000`. Left in the corpus (not excised) as the smoke gate's job is exactly
to catch this class of bug before FULL dispatch -- it did.

## Bands (pre-committed; matches research note section (b) verbatim -- not loosened)
- **HARD-PASS:** `coverage_gain_pp_pooled >= 15.0` (percentage points, POS_EXTENDED - CURRENT over the full
  OOV corpus) AND `precision_newly_covered_pooled >= 0.90` (triple-level, pooled across seeds, on sentences
  CURRENT fully abstains on AND POS_EXTENDED extracts >=1 triple) AND `guard_regression_ok` (EXTENDED does
  not corrupt fully in-lexicon sentences) AND `oos_control_fired` (both arms still abstain on an
  out-of-schema-verb control) AND `current_coverage_floor_ok` (CURRENT coverage <= 0.05 -- vacuous-test
  guard confirming genuine OOV-ness).
- **HARD-FAIL:** `coverage_gain_pp_pooled < 5.0` (POS+morphology signal too weak to matter) OR
  `precision_newly_covered_pooled < 0.75` (accepting untyped noun slots breaks more parses than it fixes --
  would indicate the closed-schema grammar's precision was silently leaning on the lexicon as a
  disambiguation filter, not just a role-filler).
- **MIDDLE_BAND:** otherwise, including the case where POS_EXTENDED produces zero newly-covered sentences
  (mechanism did not fire; cannot grade precision).
- HONEST FRAMING: a HARD-PASS on this controlled corpus does NOT claim the general open-text envelope
  (P:60-85%/R:30-55%) is beaten -- see scope note above. A HARD-FAIL on precision would be a real, reportable
  finding about lexicon-as-disambiguation-filter, not something to be hidden or re-tuned away.

## Schema-vet fields
- compute_architecture: sequential-CPU (pure syntactic parsing over a small hand-authored corpus; wall time
  MEASURED 0.11s smoke / 0.12s FULL -- discrete logic, tiny corpus, no VSA cleanup step).
- storage_strategy: no_storage (pure parser-layer test; no FoundationStore/KGStore touched -- upstream of any
  grounding/VSA subsystem).
- final_metrics_atomicity: tmp_replace. progress_logging: print_flush_true (not required at this wall time,
  included for parity). deterministic_seeding: true (fixed int seeds [7,13,19] via `random.Random(seed)`;
  `sorted()` for all set->list conversions; no `hash()`/`list(set(...))` anywhere).
- start_marker + crash_diagnostic present (tmp+os.replace atomic write pattern).
- real_code_path (F.1): self_test calls the REAL `nltk.pos_tag` (external classical-ML call, not mocked) and
  the REAL imported `ie_extract` (v2, unmodified), asserts PARITY between this cell's `_extract_core` copy
  and the import (proves "identical grammar rules" rather than asserting it), and runs the full `run_seed`
  loop at tiny scale.
- crlb_n/a: no quantitative noise floor -- discriminator is discrete syntactic role-assignment plus the
  classical tagger's own literature-benchmarked accuracy (96-97% PTB, CITED@research note section 3), not
  phasor decode noise. No VSA cleanup step in this cell at all.
- baseline_in_band: N/A BY DESIGN, declared not a META_RULE_AG violation -- AG exists to stop a mechanism
  being unmeasurable because baseline is ALREADY saturated; here the discriminator IS coverage RECOVERY FROM
  a deliberately-constructed near-zero CURRENT baseline (every corpus sentence requires an OOV noun in a
  role slot CURRENT cannot fill), so CURRENT-at-floor is the REQUIRED vacuous-test guard
  (`current_coverage_floor_ok`), not a measurability failure.
- discriminator-fires: verified at self-test AND smoke -- CURRENT coverage = 0.0 on the OOV corpus,
  POS_EXTENDED coverage > 0 (MEASURED 1.00 both smoke and FULL).
- arms_differ (META_RULE_AF): CURRENT vs POS_EXTENDED accepted-triple-set SHA256 hashes verified to differ
  at self-test on the tiny OOV corpus (CURRENT empty, EXTENDED non-empty).
- glass_box_legal: static regex source-scan (`_grep_confirm_no_neural_imports`, anchored to actual import
  statements at line start so the banned-name list literal quoted in the function's own body does not
  self-trigger) confirms no `torch`/`spacy`/`transformers`/`stanza` import anywhere in this file's source.
  `nltk`'s `averaged_perceptron_tagger_eng` is a classical, non-neural, structured-perceptron tagger --
  explicitly named LEGAL in the research note section 4.

## Dispatch
Wall time trivial (0.11-0.12s, discrete syntactic parsing over a 40-120-sentence hand-authored corpus, no
GPU) -- COMPUTE-PROPORTIONALITY (cheapest decisive method): self-test, smoke, and FULL all run
INLINE/FOREGROUND locally, matching the parallel sibling cell's precedent
(`exp_read_grow_relation_identity_v1`). No queue_add.sh / remote SCP / atomize. Pause flag
`data/orchestrator_paused.flag` re-checked absent immediately before this run (absent both times checked).

## Result (MEASURED @ data/exp_read_grow_oov_pos_extension_v1/metrics.json, seeds=[7,13,19], run_mode=full)
HARD_PASS (claim, VET-pending). `coverage_gain_pp_pooled=100.0` (CURRENT coverage=0.000, POS_EXTENDED
coverage=1.000, pooled over 120 sentences across 3 seeds); `precision_newly_covered_pooled=1.000`
(120/120 newly-covered sentences, all extracted triples exactly matched gold); `guard_regression_ok=True`;
`oos_control_fired=True`; `current_coverage_floor_ok=True`. All 10 template classes contributed
newly-covered, correctly-extracted sentences. `mixed_coord_diagnostic` confirms the honest silent-partial-
coverage finding on mixed-conjunct coordination (CURRENT emits the known-conjunct-only triple, correct but
incomplete). Elapsed 0.12s (FULL). Import chain confirmed neural-free via static regex source-scan.

HONEST CAVEAT (not a HARD-PASS overclaim): the near-ceiling 100pp/1.000 result reflects this cell's
DELIBERATELY CONTROLLED corpus (OOV nouns only; all other categories closed-lexicon) -- it demonstrates the
mechanism WORKS CLEANLY on the isolated variable the cheap decisive test targets, not that a fully open
register would clear these bars. The natural next step (per research note section (e) implication 2-3) is
extending toward a less controlled register (OneStopEnglish/Simple-Wikipedia sentences with OOV verbs and
ambiguous function words too), where the corrected classical envelope (P:60-85%/R:30-55%) is the honest
expected ceiling.
