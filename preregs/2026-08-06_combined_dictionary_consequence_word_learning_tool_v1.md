# Pre-reg: combined dictionary-lookup + consequence-learning word-learning tool

Date: 2026-08-06. Status: **PRE-REGISTERED, NOT YET EXECUTED** (spec-only cycle, per FORMALIZE-drill
discipline; a cell-author builds and runs this later). Companion spec (read first -- full integration
check, the combination-rule derivation, light-verb stress-test, coverage-gain claim):
`notes/research_combined_dictionary_consequence_word_learning_tool_2026-08-06.md`. This pre-reg UNIFIES,
rather than supersedes, its two parents: `preregs/2026-08-06_anchor_propagate_oov_outcome_verb_valence_
v1.md` (dictionary half, not yet built) and `preregs/2026-08-06_consequence_learning_loop_oov_outcome_
verb_valence_v1.md` (consequence half, BUILT at `hdlab/consequence_learning_loop.py`, already run twice:
`a892153ea` AND-gate HARD_FAIL, `093ddc1aa` Signal-A-primary HARD_FAIL). Neither parent pre-reg is
deleted; this is the USER-directed combination per `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md`
line 67-68.

## What is being built

1. **`hdlab/wordnet_polarity_propagation.py` (NEW hdlab module, dictionary half).** Implements the
   anchor_propagate pre-reg's Section 3c decision logic (opposition-first Stage A, neighbor-vote Stage B,
   `NEIGHBOR_FLOOR=0.20`, `VOTE_MARGIN=0.15`) UNCHANGED, but returns the extended
   `DictLookup(polarity, confidence, stage, vote_margin, n_neighbors)` record (companion spec Section
   2b/3.2) instead of the bare `Optional[str]` the original spec proposed -- confidence formula:
   `1.0` for a Stage-A antonym hit; `clamp((margin - VOTE_MARGIN) / (VOTE_MARGIN_SATURATE - VOTE_MARGIN),
   0, 1)` for a Stage-B neighbor-vote hit, `VOTE_MARGIN_SATURATE = 0.50` (NEW constant, pre-registered).
   `ANCHOR_WORDS` (52 words, `OUTCOME_SEED_POS | OUTCOME_SEED_NEG`) and `ANCHOR_WORDS_EXTENDED` (~78
   words, includes `OUTCOME_HELDOUT_POS/_NEG`) reused verbatim from the anchor_propagate pre-reg's item 2.
2. **`pseudo_counts_from_dictionary(lookups, k_max=MIN_CONFIRM) -> Dict[str, Dict[str,int]]` (NEW,
   pure function, lives in the new module or a thin new glue module `hdlab/word_learning_tool.py` --
   cell-author's call, either location is acceptable as long as it does not require
   `hdlab/consequence_learning_loop.py` to import WordNet code).** Per lemma with non-abstain
   `DictLookup`: `n = round(k_max * confidence)`; emit `{"POS": n, "NEG": 0}` or `{"POS": 0, "NEG": n}`;
   skip lemmas where `n <= 0` or `polarity is None`. `k_max` defaults to
   `hdlab.consequence_learning_loop.MIN_CONFIRM` (imported, not a duplicated literal).
3. **`hdlab/consequence_learning_loop.py::learn_corpus` -- ONE-LINE EDIT, strictly additive.** Add an
   optional parameter `dictionary_priors: Optional[Dict[str, Dict[str,int]]] = None` (default `None` =
   byte-identical current behavior, so the existing `self_test()` and both prior executed runs
   (`a892153ea`, `093ddc1aa`) remain exactly reproducible). Change line 306 from
   `master: Dict[str, Dict[str, int]] = {}` to
   `master: Dict[str, Dict[str, int]] = {lemma: dict(counts) for lemma, counts in (dictionary_priors or
   {}).items()}`. **No other line in the function changes** -- `setdefault` at line 321 already
   accumulates real exposures on top of a pre-seeded entry (companion spec Section 2c, traced by hand
   against the actual loop body). `consolidate()` (line 225) is untouched, called with zero code changes.
4. **`learn_corpus_combined(goal_windows, oov_lemmas, n_passes=3, k_max=None, **kwargs) -> dict` (NEW,
   thin orchestration wrapper, glue module).** Computes `{lemma: dictionary_lookup(lemma) for lemma in
   oov_lemmas}`, converts via `pseudo_counts_from_dictionary`, calls `consequence_learning_loop.
   learn_corpus(goal_windows, dictionary_priors=priors, n_passes=n_passes, **kwargs)`, attaches the raw
   `dictionary_lookups` dict onto the returned result for the per-verb report. `oov_lemmas` = the 33
   unique OOV lemmas of the live eval file for this pre-reg's primary arm (companion spec Section 5's
   proof that this is equivalent to a full corpus-OOV scan for scoring purposes).
5. **Consumer paths: UNCHANGED.** `hdlab/goal_typing.py`'s Tier-3 sentinel and `classify_2way` fallback
   already consult `ACQUIRED_OUTCOME_VERB_FEATURES` -- zero new plumbing.

## Config (pre-registered before any run, not tuned post-hoc)

- `MIN_CONFIRM = 3`, `NEUTRAL_BAND = 0.34`, `W = 3`, `N_PASSES = 3` -- all inherited unchanged from
  `hdlab/consequence_learning_loop.py`'s existing module constants.
- `NEIGHBOR_FLOOR = 0.20`, `VOTE_MARGIN = 0.15` -- inherited unchanged from the anchor_propagate pre-reg.
- `VOTE_MARGIN_SATURATE = 0.50` -- **NEW**, chosen a priori as "a decisively one-sided WordNet
  neighborhood vote," not tuned post-hoc.
- `K_MAX = MIN_CONFIRM = 3` -- **NEW**, deliberately tied to the existing constant (a maximally-confident
  dictionary hit is worth exactly as much trust as a fully-confirmed consequence lock, no more, no
  separate free parameter).
- Consequence-half signal configuration for ALL arms below: `signal_mode="signal_a_only"`,
  `credit_mode="referent_linked"` -- matches the `093ddc1aa` decisive-run configuration exactly (the
  AND-gate config already measured worse in isolation, per `a892153ea`; re-litigating that choice is out
  of scope here).
- `LIGHT_VERB_CANARY` (26 lemmas) and `NOISE_CANARY` (8 lemmas) -- reused VERBATIM from the consequence
  pre-reg's own config (not redefined).
- `LIGHT_VERB_NO_INHERENT_VALENCE` (17 lemmas: `be, have, come, go, give, take, put, find, make, carry,
  buy, drink, turn, curve, whisper, drag, practice`) -- reused verbatim from the anchor_propagate pre-reg
  Section 4. The complementary **16-lemma content-verb subset** (companion spec Section 5, re-derived
  this session): `admit, agree, befriend, croak, encore, flee, improve, jell, like, rap, refuse, relent,
  ruin, spoil, whip, whitewash`.

## Corpora + non-circularity (BOTH gate classes apply simultaneously, companion spec Section 2d)

- **Vocabulary-disjointness (dictionary half, structural, checked at build time):** `ANCHOR_WORDS` /
  `ANCHOR_WORDS_EXTENDED` must contain ZERO of the 36 eval items' `outcome_verb_lemma` values -- assert
  programmatically, fail loud before scoring (identical to the anchor_propagate pre-reg's own
  `non_overlap_assert`).
- **Text-span exclusion (consequence half, structural, checked at build time AND post-hoc):** the
  4-novel learning corpus (`little_women`, `anne_of_green_gables`, `tom_sawyer`, `wizard_of_oz`) with the
  eval's own `line_citation` ranges (+/-50 lines) excluded -- identical to the consequence pre-reg's own
  `exclusion_integrity_assert`. Both gates are load-bearing for every accuracy number below; an
  unexcluded or overlapping run must be discarded, not reported.
- **Held-out scoring set:** `experiments/data/goal_bearing_modern_eval_v1.jsonl`'s 36-item OOV subset
  (re-derived this session: 23 met / 13 unmet, majority floor `0.6389`).

## THE 3-WAY ABLATION (the decisive test of the whole design)

**Arm 1 -- DICTIONARY-ONLY.** `dictionary_lookup(lemma).polarity` for each of the 33 unique OOV lemmas,
registered directly (bypassing `consolidate`/`MIN_CONFIRM` entirely -- ANY non-abstain hit registers,
regardless of confidence, exactly reproducing the anchor_propagate pre-reg's own primary arm). **This arm
is literally the anchor_propagate pre-reg's primary arm; if that cell has already been executed by the
time this cell runs, reuse its `metrics.json` directly rather than recomputing.**

**Arm 2 -- CONSEQUENCE-ONLY.** `consequence_learning_loop.learn_corpus(goal_windows, dictionary_priors=
None, signal_mode="signal_a_only", credit_mode="referent_linked")`. **This arm is literally the
`093ddc1aa` run already executed and measured** (`primary_accuracy=0.1944`,
`grounded_verb_polarity_match_rate=0.333`, `n_grounded=11`, only 3 lemmas overlap the eval, all 3 light
verbs, 2 wrong). Cite directly; do not recompute unless the corpus or exclusion mask has changed since.

**Arm 3 -- COMBINED.** `learn_corpus_combined(goal_windows, oov_lemmas=<33 unique eval lemmas>,
n_passes=3, k_max=K_MAX, signal_mode="signal_a_only", credit_mode="referent_linked")`, scored via the
existing `congruence_with_lexicon_fallback` exactly as both parent pre-regs score.

**Per-item report schema (mandatory, the task's explicit ask):** for each of the 33 unique OOV lemmas,
report `{lemma, dictionary_stage, dictionary_polarity, dictionary_confidence, dictionary_pseudo_pos,
dictionary_pseudo_neg, consequence_real_pos, consequence_real_neg, combined_total, combined_margin,
final_verdict, gold_polarity_if_in_eval}` -- this table is the concrete evidence for "which words the
dictionary carries and which consequence refines/corrects," not just an aggregate accuracy number.

## Falsifiable predictions (HARD-PASS / HARD-FAIL / MIDDLE-BAND)

**Primary metric:** `primary_accuracy` = fraction of the 36 OOV-outcome items where the live
`congruence_with_lexicon_fallback` call (Tier-3 overlay populated by Arm 3) correctly types MET/UNMET vs
gold. Untyped/abstain = MISS (coverage-inclusive, same convention both parent pre-regs use.)

**Learnable-content subset:** items whose `outcome_verb_lemma` is in the 16-lemma content-verb list
(companion spec Section 5). Report `content_verb_subset_accuracy` separately.

**HARD-PASS** (ALL of the following):
1. `primary_accuracy >= 27/36` (0.75) AND `unmet_recall >= 5/13` (class-imbalance guard, identical
   convention to both parent pre-regs' gate 1).
2. `content_verb_subset_accuracy >= 0.70`.
3. **The decisive 3-way requirement:** `combined_primary_accuracy > dictionary_only_primary_accuracy`
   (Arm 3 > Arm 1) by `>= 0.03` (about 1 item) on the pooled 36-item metric, **AND**
   `combined_content_verb_subset_accuracy >= dictionary_only_content_verb_subset_accuracy` (combining
   must not cost accuracy on the fair subset even where it does not clearly beat it) **AND**
   `combined_primary_accuracy > consequence_only_primary_accuracy` (Arm 3 > Arm 2, `0.1944`) by
   `>= 0.30` (a large, easily-clearable margin given Arm 2's measured near-floor performance -- this
   confirms the combination is not merely "no worse than the strong half," but genuinely value-adding
   over the weak half too).
4. **Non-circularity gates (must ALSO pass or HARD-PASS is void regardless of accuracy) -- both
   inherited gate families, reused, plus one NEW joint gate:**
   - (a) Vocabulary SCRAMBLE (dictionary half, inherited from anchor_propagate pre-reg): permute
     `ANCHOR_POLARITY` labels (5 fixed seeds), WordNet graph unchanged. `scrambled_dictionary_accuracy`
     (Arm 1 recomputed under scramble) must fall in `[0.35, 0.65]`.
   - (b) RANDOM-GRAPH ablation (dictionary half, inherited): degree-matched random graph replacing real
     WordNet edges. Must also collapse to `[0.35, 0.65]`.
   - (c) Teacher-label SCRAMBLE (consequence half, inherited from consequence pre-reg): permute
     `teacher_verdict` labels across recorded exposures (5 fixed seeds) before consolidation.
     `scrambled_consequence_accuracy` (Arm 2 recomputed) must fall in `[0.40, 0.60]`.
   - (d) RANDOM-CREDIT ablation (consequence half, inherited): uniformly-random OOV credit target instead
     of referent-linked. Must be `>= 0.15` below real Arm 2 accuracy on whatever learnable subset it
     produces.
   - (e) **NEW joint gate -- combined-arm, dictionary-only-scrambled:** run Arm 3 with the DICTIONARY
     labels scrambled (same 5 seeds as (a)) but REAL consequence exposures unchanged.
     `combined_dict_scrambled_accuracy` must be materially below real `combined_primary_accuracy`
     (gap `>= 0.15`) -- isolates that the dictionary's ACTUAL polarity content (not just its presence
     as pseudo-mass) drives Arm 3's result, checked INSIDE the combined run itself, not just at the
     arm level.
   - (f) **NEW joint gate -- combined-arm, consequence-only-scrambled:** run Arm 3 with the CONSEQUENCE
     teacher labels scrambled but the real dictionary priors unchanged. `combined_conseq_scrambled_
     accuracy` must be BELOW real `combined_primary_accuracy` by a smaller but non-zero gap (`>= 0.03`)
     -- confirms consequence contributes SOME real marginal value inside the combined run, distinct from
     gate 3's arm-level comparison. A zero or negative gap here (i.e., scrambling consequence doesn't
     hurt the combined result at all) is informative on its own and must be reported honestly even if
     gate 3 otherwise passes -- it would mean the combined result is effectively dictionary-only in
     practice, a MIDDLE-BAND-relevant finding.
5. `noise_canary_consolidated_count == 0` (8-word `NOISE_CANARY`, both dictionary Stage A/B and
   consequence credit-assignment).
6. **The sharpest, most specific gate (companion spec Section 4):** of the `LIGHT_VERB_CANARY` (26
   lemmas), **zero** may reach a `final_verdict` of `POS` or `NEG` with `consequence_real_pos +
   consequence_real_neg == 0` (i.e., locked from dictionary-pseudo-count alone, no real corroborating
   story evidence). This directly tests the light-verb self-lock risk named in the companion spec, not
   just the aggregate neutral-rate.

**HARD-FAIL** (ANY of the following):
- `primary_accuracy <= 0.6389` (majority floor).
- `combined_primary_accuracy <= dictionary_only_primary_accuracy` (combining made things no better than
  the dictionary alone -- falsifies the premise that consequence adds value).
- `scrambled_dictionary_accuracy` or `scrambled_consequence_accuracy` stays within `0.10` of its own
  real-arm accuracy (no genuine content-dependence in that half).
- `random_graph_accuracy` or `random_credit_accuracy` stays within `0.10` of its own real-arm accuracy.
- `combined_dict_scrambled_accuracy` stays within `0.08` of real `combined_primary_accuracy` (the
  dictionary's actual content is not load-bearing inside the combined run).
- `noise_canary_consolidated_count >= 1`.
- **`>= 1` `LIGHT_VERB_CANARY` word self-locks from dictionary-pseudo-alone** (gate 6 above, zero
  tolerance -- this is the single most falsifying result this pre-reg can produce for the design's
  central light-verb-safety claim).
- `content_verb_subset_accuracy < 0.55`.

**MIDDLE-BAND:** `primary_accuracy` in `(0.6389, 0.75)`, OR gate 3's margins clear but gate 4(f)'s gap is
`<= 0` (dictionary is carrying the whole result, consequence's marginal contribution unproven at this
corpus scale -- report honestly per the companion spec's own named uncertainty, do not force a PASS
label), OR `content_verb_subset_accuracy` in `[0.55, 0.70)`.

## Ablation / diagnostic predictions (informational, pre-registered, not pass/fail gates)

1. **Coverage-gain count (companion spec Section 5):** of the 16-lemma content-verb subset, how many get
   `dictionary_lookup(lemma).polarity is not None`, and of those, how many had ZERO real consequence
   exposures in the `093ddc1aa` master tally (the direct, concrete measure of "coverage consequence could
   not reach").
2. **Stage A vs Stage B breakdown**, reused from the anchor_propagate pre-reg's own diagnostic 2: report
   which of the 33 lemmas' dictionary hits (if any) came from Stage A (antonym) vs Stage B (neighbor
   vote); prediction unchanged (Stage A should fire rarely, Stage B should carry most of the load).
3. **`confidence_tier` distribution** across all 33 lemmas (HIGH/MEDIUM/LOW/ABSTAIN, informational
   bucketing of `dictionary_lookup(...).confidence`) -- report separately for the 17 light-verb lemmas vs
   the 16 content lemmas; falsifiable sub-prediction: the light-verb group's confidence distribution
   should skew visibly LOWER than the content-verb group's (a direct, checkable version of the
   "structural" light-verb defense in companion spec Section 4).
4. **`croak` and other WSD-gap cases**, reused from the anchor_propagate pre-reg's own diagnostic 4 --
   report `croak`'s specific `DictLookup` and whether the combined mechanism corrects or compounds the
   known archaic-sense mismatch.

## Compute architecture

Sequential-CPU. Dictionary lookups: deterministic `nltk.corpus.wordnet` calls, O(1) each, seconds total
(33 lemmas x <=78 anchor comparisons). Consequence half: same complexity as its own pre-reg (three
~25K-sentence passes over 4 novels, already measured well under a minute per pass in the executed
`093ddc1aa`/`a892153ea` runs). `crlb: n/a` (fixed classification against gold, not a capacity cell).
`storage_strategy`: `ACQUIRED_OUTCOME_VERB_FEATURES` remains process-local/in-memory. Expected wall time:
low minutes total, dominated by the consequence-half corpus passes (unchanged from its own pre-reg),
Arm 1 and dictionary-prior computation add low tens of seconds.

## Cardinality / discriminator / atomicity gates (SCHEMA-VET checklist)

- `cardinality_ok`: `EXPECTED_N_UNITS` = 3 arms (Arm 1 may be a metrics.json reuse, not a fresh unit, if
  the anchor_propagate cell already ran) + 5 dict-scramble seeds + 1 random-graph + 5 consequence-scramble
  seeds + 1 random-credit + 5 combined-dict-scrambled seeds + 5 combined-consequence-scrambled seeds + 1
  noise-canary batch + 1 light-verb-canary self-lock check = 27 units minimum, resumable per-unit via
  `tools/exp_checkpoint.py` (mandatory per repo convention, all units cheap/CPU-only so this mainly
  protects against a mid-run interruption, not compute cost).
- `discriminator_reachability`: TRUE -- 36-item binary classification, majority floor 0.6389, ceiling
  1.0, not saturated by construction (identical to both parent pre-regs).
- `baseline_in_band`: N/A for the primary arm; reference baselines (0.6389 majority, `093ddc1aa`'s
  0.1944 consequence-only, `a892153ea`'s 0.1667 empty-overlay) are REAL, previously measured off disk,
  not assumed.
- `arms_differ_verified`: Arm 1 vs Arm 3's registered `ACQUIRED_OUTCOME_VERB_FEATURES` entries must
  hash-differ for any lemma where real consequence exposures existed; scrambled vs real entries must
  hash-differ in every scramble arm (same META_RULE_AF-style check both parent pre-regs already use).
- `final_metrics_atomicity`: `tmp_replace`.
- `deterministic_seeding`: fixed integer seeds throughout (no `hash()`-derived seeding, PROT-023/F.5
  compliant); WordNet lookups deterministic (no seed needed); `round()` in `pseudo_counts_from_
  dictionary` uses Python's standard banker's rounding, documented explicitly in the module docstring
  so a future re-implementation does not silently pick a different rounding convention.
- `progress_logging`: `print_flush` per-arm and per-lemma (small N throughout, heartbeat optional but
  included for template consistency).
- `non_overlap_assert` + `exclusion_integrity_assert`: BOTH inherited gates run together (companion spec
  Section 2d), asserted before any scoring, fail loud on violation.

## Cert gate (MANDATORY -- touches production `hdlab/verb_lexical_similarity.py` write-back consumer path)

`python verification/run_certification.py` via `.venv/Scripts/python.exe` BEFORE and AFTER; baseline to
reproduce: 220 passed, 3 skipped (same baseline both parent pre-regs cite). The `learn_corpus` one-line
edit (Section "What is being built" item 3) is defaulted to `None` = current behavior, so the existing
`consequence_learning_loop.self_test()` must remain byte-identical-passing with zero argument changes at
its own call sites; add ONE new self-test case exercising `dictionary_priors != None` explicitly
(mandatory addition, not optional) to prove the seeding-once behavior from companion spec Section 2c
concretely, not just by code inspection.

## Files to be touched

- `hdlab/wordnet_polarity_propagation.py` (NEW) -- `dictionary_lookup`, the lifted `_antonyms` helper
  (clean-copy from `experiments/exp_arc_aggregation_polarity_ci_v1.PolarityLexicon._antonyms`, credited
  in the docstring), `ANCHOR_WORDS`/`ANCHOR_WORDS_EXTENDED`/`ANCHOR_POLARITY`, `pseudo_counts_from_
  dictionary`. No `experiments/` import at runtime (hdlab-only dependency discipline, matching the
  anchor_propagate pre-reg's own convention).
- `hdlab/consequence_learning_loop.py` (EDIT, one new optional parameter + one line inside `learn_corpus`,
  Section "What is being built" item 3) -- all other functions and the existing `self_test()` untouched;
  ADD one new self-test case for `dictionary_priors != None` (cert gate requirement above).
- `hdlab/word_learning_tool.py` (NEW, thin orchestration) -- `learn_corpus_combined`, the per-verb report
  schema builder. This is the file a cell-author actually calls.
- `experiments/exp_combined_dictionary_consequence_word_learning_tool_v1.py` (NEW) -- the pre-reg'd cell:
  runs all 3 arms, all ablations/controls above, self-test per the mandatory cell template, resumable per
  unit via `tools/exp_checkpoint.py`. `hdlab/goal_typing.py`, `experiments/exp_grounded_word_acquisition_
  increment1_v1.py`/`_increment1b_v1.py`, `experiments/exp_consequence_learning_loop_oov_outcome_verb_
  valence_v1.py` (if it exists by the time this cell is authored), and `experiments/data/goal_bearing_
  modern_eval_v1.jsonl` LEFT UNTOUCHED (source-of-truth convention, same as every prior pre-reg in this
  lineage).

## Prior-work check (per exp_dev standing discipline)

Direct prior-art, checked against the live repo and `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md`
this session: `grounded_word_acquisition_loop_increment1` (SHELVE, revival criteria satisfied by
increment 1b, HARD_FAILed; this is a FIFTH attempt at the same revival lineage -- increment1 (channel
A/B) -> increment1b (structural telicity) -> anchor_propagate (WordNet-only, unbuilt) ->
consequence_learning_loop (built, HARD_FAIL x2) -> this combined design, which is the first attempt to
fuse two independently-validated-or-spec'd mechanisms rather than replace one with another); `preregs/
2026-08-06_anchor_propagate_oov_outcome_verb_valence_v1.md` (dictionary half, standing, this pre-reg
consumes its Section 3c decision logic verbatim with a signature extension, does not duplicate it);
`preregs/2026-08-06_consequence_learning_loop_oov_outcome_verb_valence_v1.md` +
`hdlab/consequence_learning_loop.py` (consequence half, BUILT and VALIDATED-at-mechanism-level per its
own `self_test()`, this pre-reg extends it via one additive optional parameter, does not fork or
duplicate the module). No existing `hdlab/wordnet_polarity_propagation.py` or `hdlab/word_learning_
tool.py` found (checked this session: no hit for `wordnet` combined with `polarity`/`propagat`, nor for
`word_learning_tool`, anywhere under `hdlab/`) -- confirmed genuinely new, not a duplicate build.
