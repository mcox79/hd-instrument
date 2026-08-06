# Pre-reg: grounded-word-acquisition loop, increment 1b (outcome-verb RESULT-CLASS/telicity axis)

Date: 2026-08-06. Status: **PRE-REGISTERED, NOT YET EXECUTED** (spec-only cycle; a cell-author builds
and runs this later). Companion spec: `notes/formalize_word_acquisition_increment1b_result_class_
congruence_2026-08-06.md` (read first -- has the confirmed congruence-organ input contract, the
finding that increment 1's "Channel B" already reduces to a structural mechanism plus a fixed
sign-constant, the AND-gate design flaw, and the two risks this pre-reg's design is built around).
This REVISES increment 1's TARGET + SCORING + channel architecture; it REUSES increment 1's
propose-trigger, consolidation gate, and write-back schema verbatim, and EXTENDS (not replaces) the
existing `hdlab/word_acquisition_loop.py` (372 lines) and `hdlab/goal_typing.py`'s Channel B adapter
section (L834-952) -- both already exist on disk (confirmed via `ls`, commit 7c314c840), registered as
`grounded_word_acquisition_loop_increment1` in `data/capability_registry.jsonl` (`gate_decision:
SHELVE`, revival criteria = the telicity discriminator + goal-passage structure this pre-reg delivers).

Task: close audit gap #1 ("FEATURES: supplied vs LEARNED+GROUNDED",
`notes/audit_SYNTHESIS_semantic_meaning_barrier_2026-08-06.md`) for outcome-verb RESULT-CLASS
membership (`hdlab.goal_typing.CLASS_REGISTRY`, consumed by `_verb_classes`/`congruence_decision`),
the structural axis that actually drives the congruence organ's MET/UNMET decision.

## What is being built (delta from increment 1, all strict-ADD)

1. **Single-channel structural situation-typer (retained + simplified, not net-new).** Reuse
   `_cb_analyze_outcome_clause` (`hdlab/goal_typing.py` L851-898, clause-local animacy/direct-object/
   passive/result-particle read, already built, verb-lemma-blind) + `_cb_antecedent_goal_type`
   (L901-925, explicit antecedent-goal referent-link check, already built) + the implicit
   force-dynamics fallback currently inside `goal_congruence_appraisal_type` (L943-951). **Drop the
   `channel_b_valence_table`/reward-theta indirection** (companion spec Section 1: it is a fixed
   2-value constant, RECIPROCITY->POS/BLOCK_HIGH->NEG, proven redundant) -- map RECIPROCITY ->
   `AGONIST_REALIZED` (POS), BLOCK_HIGH -> `AGONIST_BLOCKED` (NEG) directly, no reward-theta lookup,
   no `experiments.exp_bridge1_governor_grounding_v1`/`hdlab.context_grounded_valence` import in the
   acquisition loop's hot path.
2. **Drop the STRICT two-channel AND-gate** (`combine_votes`, `word_acquisition_loop.py` L255-263) --
   companion spec Section 3 shows this is net-harmful (not merely unhelpful) when paired with a
   channel measured at chance (increment 1's separate MDL-induced Channel A, `channel_A_only=4/7`,
   diagnosed as a majority-class-default artifact). There is one channel now; the full anti-drift
   burden moves to `MIN_CONFIRM=2` consolidation (below), the correct locus per Trueswell 2013 /
   Alishahi-Fazly-Stevenson 2008's propose-but-verify account.
3. **REQUIRED fix (companion spec Section 2) -- pole sentinel for Tier-3-acquired words.** Extend
   `_verb_classes` (`hdlab/goal_typing.py` L513-519): for a lemma resolvable ONLY through
   `ACQUIRED_OUTCOME_VERB_FEATURES` (Tier-1 exact and Tier-2 domain-differentiated similarity both
   fail), return a one-element pole SENTINEL (`{"ACQUIRED_REALIZED"}`/`{"ACQUIRED_BLOCKED"}`) instead
   of `set()`, so `find_actual_state_candidates`'s existing `if classes:` filter (L690-692, UNCHANGED)
   includes it. Add `POS_POLE_CLASSES`/`NEG_POLE_CLASSES` (derived from the existing `OPPOSED_PAIRS`,
   zero new taxonomy) + ONE new branch inside `congruence_decision`'s `same`/`opposed` computation,
   gated strictly on the sentinel shape: compare the desired class's pole against the sentinel's pole
   rather than requiring literal class-name-set intersection. Tier-1/Tier-2 resolution paths are
   completely untouched -- zero regression risk.
4. **OPTIONAL, separately-ablated enrichment atoms** to `_cb_analyze_outcome_clause`'s clause read
   (companion spec Section 4.3, Section 5's own falsifiable framing -- NOT assumed load-bearing):
   `direct_object_is_quantized` (definite/quantized NP test, Beavers 2011 scalar affectedness) and
   `discourse_pole_cue` (CONTRAST connective `{but, however, yet, although}` immediately preceding the
   outcome clause votes reversal; RESULT/continuation connective `{and, so, then, for}` or none votes
   continuation -- Kehler 2002, Hobbs 1979).
5. **Propose trigger + consolidation + write-back: REUSED VERBATIM, zero code change.**
   `word_is_novel` (`predictive_coding.threshold_gate` OOV gate, L65-75); `consolidate`
   (`MIN_CONFIRM=2` signature-match + `decide_keep_or_revert` abstain-band, L266-289);
   `apply_acquired`/`register_acquired_outcome` write-back into `ACQUIRED_OUTCOME_VERB_FEATURES`
   (L331-336, `hdlab/verb_lexical_similarity.py`, unchanged schema).

## Held-out set / test bed

`experiments/data/goal_bearing_modern_eval_v1.jsonl` (44 items, `notes/research_goal_bearing_modern_
eval_2026-08-06.md`, McGuffey-free, 7 modern/classic-narrative corpora).

**Primary scored subset: 36/44 items have `outcome_in_lexicon: false`** (re-derived directly from the
file this session: items 2, 9, 13, 14, 21, 27, 36, 40 are the 8 in-lexicon controls).

**Polarity distribution on the 36-item PRIMARY scored subset (counted directly, corrected from the
task brief's rounder full-44 figure):** 23 MET / 13 UNMET. **Majority-class floor =
23/36 = 0.6389** (not 27/44=0.614 -- that is the full-44 figure, not correctly scoped to the 36-item
primary metric; using it here would understate the real bar). Report both if a future comparison needs
the full-44 figure, but GATE on 0.6389.

**Fall-through / lexicon-fallback baseline: 0/36 = 0.0** (measured: `ACQUIRED_OUTCOME_VERB_FEATURES` is
empty at import; every one of the 36 lemmas is `False` on `in_lexicon(lemma, "outcome")` against the
live module as of this pre-reg's date).

**Coverage sub-partition (companion spec Section 6, pre-registered as a DIAGNOSTIC, not a gate): 18/36
have a `goal_verb_lemma` recognized by `find_desired_state`'s `DESIDERATIVE_PASS` gate** (`{want,
hope, wish, mean, plan, intend, aim, long, yearn, desire}`) and are reachable via the FULL,
Risk-#1-fixed congruence-organ path; the other **18/36 have a goal verb `find_desired_state` cannot
parse** and will structurally fall through to the flat 2-way `lexicon_predict` path regardless of 1b's
mechanism quality. Report BOTH subsets' accuracy separately alongside the pooled 36-item primary
number.

## Acquisition-exposure mining procedure

For each deduplicated OOV outcome lemma among the 36 primary-subset items (a few repeat, e.g. "give"
is the outcome verb in 2 items -- dedupe by lemma, do not double-mine): mine >=2 sentences containing
that lemma (or an inflected form, via `hdlab.thematic_role_labeler.lemma_verb`) from the same 7 source
corpora, **excluding the exact cited passage of the eval item itself** (non-circularity, same
discipline as increment 1's McGuffey mining, which this reuses via `mine_seed_episodes`'s existing
corpus-scanning pattern, `word_acquisition_loop.py` L113-146, generalized from seed-verb mining to
target-lemma mining). A lemma with FEWER than 2 independent occurrences elsewhere is marked
`insufficient_corpus_support`, correctly abstains, and **counts as a MISS in the primary
(coverage-inclusive) accuracy denominator** -- report its count separately (an honest, expected,
corpus-frequency-driven outcome, not a mechanism failure).

## Noise-probe set (anti-drift control, reused verbatim from increment 1)

`walked, sat, spoke, turned, answered, asked, stood, carried` -- 8 classic Vendler (1957) ACTIVITY
verbs, 2 sentences each (16 total), same transitive-with-direct-object shape as the acquisition
sentences. Under the retained structural typer, these ALSO test whether `_cb_analyze_outcome_clause`'s
`agonist_realized`/`agonist_blocked` boolean read incorrectly fires on atelic verbs (it should not,
since none of these denote a scalar result-state) -- a genuine positive control for the existing
mechanism, not just the new atoms.

## Scramble control

Fixed-seed permutation (5 seeds) of the (target-lemma -> mined-acquisition-context) pairing across the
deduplicated OOV lemma set, same convention as increment 1's own scramble and `verb_lexical_
similarity.py::self_test`'s circularity check.

## Falsifiable predictions (HARD-PASS / HARD-FAIL / MIDDLE-BAND)

**Primary metric:** `primary_accuracy` = fraction of the 36 OOV-outcome-verb items where the LIVE
production call (`congruence_with_lexicon_fallback`, with the Tier-3 overlay + Risk-#1 pole-sentinel
fix live) correctly types MET/UNMET matching gold. Untyped/abstain counts as a MISS (coverage-inclusive
scoring, matching how both the 0/36 fall-through and 23/36 majority-class baselines are defined).

**HARD-PASS** (ALL of the following):
1. `primary_accuracy >= 27/36` (0.75, a +0.111 absolute margin over the corrected 0.6389 majority
   floor), AND `unmet_recall >= 5/13` (~0.385) AND `met_recall >= 18/23` (~0.783) -- rules out a
   degenerate always-guess-MET strategy, which scores exactly 0.639 and must not clear gate 1 (same
   class-imbalance-guard logic as increment 1's own gate 1).
2. `noise_consolidated_count == 0/8` AND `noise_gated_count == 8/8` (all 8 activity verbs fail to
   produce a REALIZED/BLOCKED read at all via `_cb_analyze_outcome_clause`'s boolean logic -- report
   this distinctly from the consolidation-level anti-drift check, since it tests a different part of
   the pipeline).
3. `scrambled_primary_accuracy` within `[0.35, 0.65]` while real `primary_accuracy` clears gate 1 --
   non-vacuous collapse.
4. `insufficient_corpus_support_count <= 12/36` -- coverage sanity check (if more than a third of
   target lemmas lack independent corpus support, the eval is under-mined, not the mechanism
   under-performing; re-mine before treating a low `primary_accuracy` as a verdict).
5. `desiderative_eligible_subset_accuracy` (the 18-item reachable-via-full-organ subset) exceeds
   `flat_fallback_subset_accuracy` (the other 18) by a visible margin -- the SHAPE-fix's own
   falsifiable claim (see HARD-FAIL bullet below for the failure-side framing).

**HARD-FAIL** (ANY of the following):
- `primary_accuracy <= 23/36` (0.639) -- does not beat blind majority-class guessing.
- `noise_consolidated_count >= 1/8` -- anti-drift consolidation gate leaks.
- `scrambled_primary_accuracy` stays within `0.10` of real `primary_accuracy` -- no genuine
  construction/pole dependence.
- `desiderative_eligible_subset_accuracy <= flat_fallback_subset_accuracy` -- the SHAPE fix (feeding
  the congruence organ in goal context, Risk #1's sentinel fix) does not outperform the exact
  mechanism-and-consumer-shape increment 1 already measured weak (the flat 2-way path); this is a
  genuine, informative falsification of THIS re-spec's central claim, reported as such, not relabeled.

**MIDDLE-BAND**: `primary_accuracy` in `(23/36, 27/36)`, OR gate 1 clears but the noise/scramble gates
are borderline (e.g. `noise_gated_count == 7/8` with an identifiable, non-systematic cause; scramble
delta in `[0.10, 0.15)`), OR gate 5 shows a marginal (non-zero but small) subset gap. Report honestly
per `outcome_valence_goal_congruence_v2`'s own MIDDLE_BAND precedent (`hdlab/goal_typing.py`'s module
docstring) -- do not force a label either direction.

## Ablation / diagnostic predictions (informational, pre-registered)

1. **Section 4-item-4 enrichment ablation** (`with_enrichment_atoms` vs `structural_core_only`,
   holding everything else fixed) -- falsifiable sub-prediction: since the EXISTING implicit
   force-dynamics read already shows some real signal per increment 1's own provenance ("recovers
   earn, gain"), the enrichment atoms should show a SMALL positive or near-zero delta, not a large
   one -- a large delta would suggest the core read was more impoverished than increment 1's own
   measurement implied and should prompt re-examining that measurement, not just banking the gain
   uncritically.
2. **`desiderative_eligible_subset_accuracy` vs `flat_fallback_subset_accuracy`** (Section, gate 5/
   HARD-FAIL bullet above) -- the single most important diagnostic this pre-reg carries; report the
   per-item breakdown (which of the 18 eligible items succeed/fail and via which `_referent_links`
   tier) alongside the pooled numbers.
3. **`insufficient_corpus_support` lemma list** -- report which specific lemmas among the 36 lacked
   >=2 independent corpus occurrences (expected candidates by inspection: rare/domain-specific outcome
   verbs like "jell," "encore," "croak," "befriend" -- confirm or refute against the actual mining run,
   do not assume).

## Compute architecture

Sequential-CPU. FHRR bundle/cosine (unchanged mechanism class) + referent-linking (already-wired,
zero new cost) + the pole-sentinel branch (O(1) per candidate, no new induction). Removing the MDL-
induced Channel A + reward-theta lookup makes this cell CHEAPER than increment 1's, not more
expensive, despite the larger N (36 lemmas vs 7): no `hdlab.learner.registry.learn` call, no
`context_grounded_valence.score_item` calls. N <=36 target lemmas x 2 exposures + 36 held-out (the
eval items) + 16 noise sentences + 5 scramble seeds -- low hundreds of forward passes, wall time
expected in low tens of seconds. `crlb_n/a`: bounded classification accuracy against fixed 36-item
gold, not a capacity/argmax-noise-floor cell. `storage_strategy`: `ACQUIRED_OUTCOME_VERB_FEATURES`
remains process-local/in-memory (cross-session persistence out of scope, unchanged from increment 1).

## Cardinality / discriminator / atomicity gates (SCHEMA-VET checklist)

- `cardinality_ok`: `EXPECTED_N_UNITS` = <=36 (per-lemma acquire+test, resumable per-lemma) + 1 (noise
  batch) + 1 (scramble, 5 seeds averaged) + 1 (enrichment-atom ablation) + 1 (eligible-vs-fallback
  subset breakdown) = 40 units minimum; resumable per-unit via `tools/exp_checkpoint.py`.
- `discriminator_reachability`: TRUE -- 36-item binary classification, majority floor 0.639, ceiling
  1.0, not saturated-by-construction.
- `baseline_in_band`: N/A for the primary arm (direct measurement against fixed gold); both reference
  baselines (0.639, 0.0) are REAL, measured off the live eval file + live module state, not assumed.
- `arms_differ_verified`: real vs scrambled `ACQUIRED_OUTCOME_VERB_FEATURES` entries must hash-differ
  (same META_RULE_AF-style check as this file family's existing self-tests).
- `final_metrics_atomicity`: `tmp_replace`.
- `deterministic_seeding`: fixed integer seeds throughout (no `hash()`-derived seeding, PROT-023/F.5
  compliant).
- `progress_logging`: `print_flush` heartbeats per-lemma if wall time exceeds 60s (the 36-lemma
  corpus-mining step is more I/O than increment 1's 7-word hand-curated bank).

## Cert gate (MANDATORY -- touches production `hdlab/goal_typing.py`)

`python verification/run_certification.py` via `.venv/Scripts/python.exe` BEFORE and AFTER; baseline
to reproduce: 220 passed, 3 skipped (increment 1's own measured baseline the same day, unchanged by its
own HARD_FAIL since that cell was standalone) -- must stay 220/3 unchanged. The new `_verb_classes`
Tier-3 sentinel branch + `congruence_decision`'s new pole-comparison branch only fire for lemmas
resolvable through `ACQUIRED_OUTCOME_VERB_FEATURES` (empty at import, populated only by the acquisition
loop's own consolidation) -- strict ADD, no existing test item's verb vocabulary can collide unless
independently OOV of both Tier-1 AND Tier-2 today; trace any such collision by hand against
`verification/test_outcome_valence_goal_congruence.py`'s decisive items before dispatch.

## Files to be touched (EXTEND existing files, per the corrected understanding above -- NOT create new
modules where increment 1 already built them)

- `hdlab/goal_typing.py` (EDIT) -- (a) `_verb_classes` Tier-3 sentinel branch + `POS_POLE_CLASSES`/
  `NEG_POLE_CLASSES` + `congruence_decision`'s new pole-comparison branch (Section 3 of "what is being
  built"); (b) `goal_congruence_appraisal_type` simplified to drop the reward-theta call and map
  RECIPROCITY/BLOCK_HIGH directly to REALIZED/BLOCKED (or a NEW sibling function added alongside it if
  preserving the original for comparison is preferred -- implementer's call, document which); (c)
  OPTIONAL: the two new atoms in `_cb_analyze_outcome_clause`, behind an explicit flag so the ablation
  (item 1 above) can run both configurations from one code path.
- `hdlab/word_acquisition_loop.py` (EDIT) -- remove/bypass the `combine_votes` STRICT-AND gate and the
  `channel_b_valence_table`/`channel_a_vote`/`train_channel_a` MDL-induction call path (or leave them
  importable-but-unused for historical comparison -- implementer's call, document which); extend
  `mine_seed_episodes`'s corpus-scanning pattern to target-lemma mining (the acquisition-exposure
  mining procedure above) rather than seed-verb mining.
- `hdlab/verb_lexical_similarity.py` -- NO CHANGE (Tier-3 overlay + `register_acquired_outcome` reused
  byte-identically; only the caller's interpretation of the "polarity" argument's provenance changes).
- `experiments/exp_grounded_word_acquisition_increment1b_v1.py` (NEW) -- the pre-reg'd cell,
  resumable + atomic-write + self-test per the mandates. `experiments/exp_grounded_word_acquisition_
  increment1_v1.py` (increment 1's own cell) and `experiments/data/goal_bearing_modern_eval_v1.jsonl`
  are LEFT UNTOUCHED (source-of-truth convention).

## Prior-work check (per exp_dev standing discipline)

Direct prior-art: `data/capability_registry.jsonl`'s `grounded_word_acquisition_loop_increment1`
row (gate: SHELVE) -- its own `revival_criteria` field states, word-for-word: "A follow-up increment
should add the telicity/result-state discriminator and test on goal+outcome PASSAGE structure (where
find_desired_state supplies a real antecedent goal) rather than bare corpus clauses." This pre-reg is
confirmed to be exactly that follow-up, checked against the registry text directly, not paraphrased
from memory. `hdlab/goal_typing.py`'s `_verb_classes_similarity` (Tier-2) is the only existing
open-vocab RESULT-CLASS mechanism; the Tier-3 pole-sentinel extension is new but minimal (one branch,
no new taxonomy). No existing discourse-connective-cue mechanism exists anywhere in `hdlab/` (checked:
no hit for `discourse`/`connective`/`coherence`/`Kehler`/`Hobbs`-adjacent naming) -- flagged honestly
as the least-precedented, optional piece of this spec (item 4 in "what is being built," explicitly
ablated).
