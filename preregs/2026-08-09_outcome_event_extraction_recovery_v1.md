# Pre-reg: outcome-event extraction recovery on real DesireDB (`exp_outcome_event_extraction_recovery_v1`)

Date: 2026-08-09. Status: **BUILT, SELF-TESTED, SMOKE-RUN, FULL-RUN.** Bands below were fixed and sent
to / approved by Director (SendMessage exchange, 2026-08-09, "PRE-REG APPROVED -- strong design")
BEFORE the FULL run; this file formalizes that record for the durable audit trail, per the arc's own
convention (e.g. `preregs/2026-08-09_grounding_acquisition_loop_v1.md`).

Director task: mid-cycle redirect (superseding an earlier "swap a stronger teacher into
`hdlab/grounding_acquisition_loop.py`" plan) -- a real-DesireDB probe found the owned grounding organs
score below the tuned valence+negation RULE not because they are wrong, but because "the pipeline just
rarely feeds them the right word." Attack OUTCOME EXTRACTION directly: build a glass-box POS-aware
outcome-event extractor, feed its span to four already-proven organs, and measure recovery on the real
DesireDB abstain-to-majority cohort against mandatory extraction-ablation and pairscramble controls.

## Prior-work check (per exp_dev standing discipline)

`bash tools/substrate_query.sh "self-growing grounding acquisition loop DesireDB payoff accuracy
exposure curve goal achievement teacher swap content word filter"` (run before the original,
since-superseded plan): top hit cosine=0.2822 (`grounded_word_acquisition_loop_increment1`, SHELVED,
a different mechanism), no close match. **Verdict: no prior cell at cosine>0.30 builds outcome-event
extraction feeding the goal_outcome_relation_grounded/relation_channel/valence_channel organs --
genuinely novel synthesis**, consistent with what the Director's own citations (backup L65-67,
"the wall is OUTCOME EXTRACTION... a different, harder front-end program") already identified as the
open, unattempted lever.

## What is being built

`hdlab/outcome_event_extraction.py` (NEW) + `experiments/exp_outcome_event_extraction_recovery_v1.py`
(NEW). Zero edits to any existing production file (`hdlab/goal_achievement.py`,
`hdlab/goal_outcome_relation_grounded.py`, `hdlab/goal_typing.py`, `hdlab/candidate_generator.py`,
`hdlab/lexical_similarity.py` all imported read-only, called verbatim). No cert gate required.

### Extractor (new)

`extract_outcome_event(desire, outcome)`: parses `outcome` with the persisted UPOS-tagger + arc-parser
(`hdlab.candidate_generator.CandidateGenerator`, the SAME checkpoint `hdlab/parse_goal_extraction.py`
and `goal_cued_valence_channel` already load). Segments the WHOLE outcome into clause spans via
`hdlab.goal_typing._CB_CLAUSE_BOUNDARY` (byte-identical boundary vocabulary to
`hdlab.consequence_learning_loop._credit_targets`'s own clause-bounding, generalized from "one verb's
clause" to "every clause in the text" -- see build note below). Each clause is scored by the highest
`hdlab.goal_typing._referent_links` tier over its NOMINAL tokens against the goal's referent
(`find_desired_state`); ties broken by whether the clause's head verb (VERB, falling back to AUX for
copula clauses) is a WordNet-synonym of the goal verb. No clause anywhere links -> `None` (honest
abstain, never fabricates a span).

**Two bugs caught and fixed during smoke (disclosed, not silently patched):**
1. The first implementation scoped clauses only around POS=="VERB" tokens. UD tags copulas ("I am
   Kame") as AUX, not VERB, so every copula-headed clause was silently invisible to the extractor --
   caught when a literal referent match ("fluffyyaoi") inside a copula-only sentence produced zero
   candidate clauses. Fixed by segmenting ALL clauses upfront (`_segment_clauses`), independent of
   verb-token presence, with the head-verb search (for the tie-break bonus only) trying VERB then AUX.
2. `_referent_links`'s `pronoun_coref` tier fires whenever a bare pronoun's gender/number is merely
   *compatible* with the referent's -- a promiscuous test for generic pronouns ("it"/"they") when
   applied, as this extractor does, to every NOMINAL token in a full clause (its original callers apply
   it only to a single, already structurally-narrowed candidate). Caught when referent="doctor"
   pronoun-coref-linked to a bare "It" in an unrelated sentence. Fixed by restricting the extractor's
   accepted tiers to `{"literal", "shared_feature"}` only (`_TIER_RANK` excludes `pronoun_coref`) -- a
   disclosed, precision-favoring scope narrowing, not a silent accuracy patch.

### Composition (new, feeds 4 already-proven organs)

`composed_extraction_verdict(desire, event_span)`, fired-majority-vote (tie among firing channels ->
abstain, mirrors `valence_channel`'s own `npos==nneg`->`None` convention):
- CH_A `relation`: `hdlab.goal_achievement.relation_channel`, unmodified.
- CH_B `grounded_relation`: `hdlab.goal_outcome_relation_grounded.relation_votes_grounded` (ACHIEVE
  pool-similarity + CONTRADICT engagement-axis), unmodified; classifier induced once from
  `hdlab.goal_outcome_relation.TRAIN_EXAMPLES`, cached.
- CH_C `graded_relation` (new, small): same shape as CH_A, but the recurrence test is
  `hdlab.lexical_similarity.concept_similarity(goal_verb, event_verb) >= SIMILARITY_LINK_THRESHOLD`
  instead of literal WordNet-synset membership -- the direct wire-in of `concept_similarity` the
  Director named. Reports `best_sim` even sub-threshold (near-miss diagnosis).
- CH_V `valence`: `hdlab.goal_achievement.valence_channel`, unmodified.

## Arms

All on the real DesireDB abstain-to-majority cohort
(`goal_achievement_verdict(desire, outcome, use_union_oov=False)["channel"] == "majority"` -- the
ANTI-CIRCULARITY constraint; `use_union_oov=False` pinned explicitly to avoid confounding with the
already-wired union OOV channel, which flipped its module default to `True` the same day this arc's
`harness_validity_check` convention was set -- calling it unpinned would silently compare against the
wrong pipeline, a landmine this pre-reg flags rather than falls into):

- **REAL**: `event_span` = the extracted clause; abstains to majority when extraction itself finds
  nothing (structurally distinct from ABLATION, never silently falls back to whole-text).
- **EXTRACTION-ABLATION** (mandatory control): `event_span` = the whole unparsed Evidence text through
  the IDENTICAL 4-channel composition. Isolates whether extraction specifically is the lever -- the ONE
  variable that changes between REAL and this arm.
- **PAIRSCRAMBLE** (mandatory control): desire replaced end-to-end (extraction AND all 4 channels) with
  a deterministic derangement partner's desire, identical offset convention to
  `exp_utility_satisfaction_channel_v1._scrambled_desires`. Must collapse toward no-recovery.

## Two cohort scales (Director-mandated refinement after pre-reg review)

- **ENLARGED (primary for the recovery/count gates)**: 900-row deterministic subsample
  (`ENLARGED_SEED=20260809`), construction byte-identical to
  `exp_direction_b_M2_speechact_result_generalization_v1.enlarged_cohort_analysis` (same
  `random.Random(seed).sample` over `sorted(range(len(rows)))`, same `sorted()` re-order) --
  CITED@`experiments/exp_direction_b_M2_speechact_result_generalization_v1.py:120-125`. Reused verbatim
  for head-to-head comparability with M1 (0/37) and M2 (9/37=0.243) on the EXACT same draw. Addresses
  the Director's power concern: n=160's cohort is only ~22 (a 0.15 recovery delta there is ~3 items,
  noise-dominated); the enlarged draw gives cohort_n=152, gold-Unfulfilled n=37 (MEASURED, matches M1/M2
  exactly -- confirms the reused construction is byte-identical).
- **n=160 / n=80 (secondary, direction-holds robustness)**: BALANCED draws (`SEED=20260808`,
  `exp_utility_satisfaction_channel_v1`'s own convention) -- used ONLY for the full-bench composed
  macro-F1 comparison against the cited RULE floor (0.620), which itself was measured on a balanced
  sample; the unbalanced ENLARGED draw is not used for that specific comparison.

## Falsifiable predictions (bands fixed before FULL; HARD-PASS = ALL required)

Applied to the **ENLARGED** cohort's gold-Unfulfilled subset (n=37, MEASURED) unless noted:

1. `HP1` extraction_fire_rate(REAL) >= 0.40
2. `HP2` recovery_real - recovery_ablation >= 0.15 (arc-standard gap convention: `scr_collapse`/`rc_gap`
   precedent across this arc's own cells, e.g. `exp_consequence_learning_loop_*`)
3. `HP3` recovery_pairscramble <= 0.20 AND recovery_real - recovery_pairscramble >= 0.15
4. `HP4` recovery_real >= 0.20 AND n_recovered_real >= 6 (calibrated to M2's own measured 9/37=0.243
   high-water-mark on this EXACT enlarged cohort -- CITED@backup L63 -- not an arbitrary aspirational
   number)
5. `HP5` full_bench composed macro-F1 (REAL wired as the abstain-fallback, n=160) >= a FRESHLY-measured
   base-3-channel macro-F1 on the identical sample (genuine lift over today's pipeline)
6. `HP6` full_bench macro-F1 (n=160) >= 0.620 (the cited tuned-valence+negation RULE floor,
   CITED@`hdlab/goal_achievement.py` module docstring line 5)

**HARD-FAIL** (any):
- `HF1` extraction_fire_rate(REAL) == 0
- `HF2` recovery_real - recovery_ablation < 0.05 (extraction is NOT the lever -- reproduces the
  Director's predicted flat/blocked outcome)
- `HF3` recovery_pairscramble >= recovery_real - 0.05 (control fails to collapse)
- `HF4` enlarged gold-Unfulfilled n < 15 (underpowered even at enlarged scale)
- `HF5` full-cohort accuracy (REAL, both classes) regresses below the majority baseline by more than
  0.05 (VET the positive as hard as the negative -- catches REAL/ABLATION flipping gold-Fulfilled
  cohort items to false-positive wrong)
- `HF6` full_bench macro-F1 (n=160) < 0.620 (regression below the RULE floor)

**MIDDLE_BAND**: no HARD-FAIL, HARD-PASS not fully cleared -> mandatory per-item diagnosis on EVERY
majority-wrong cohort item (Director: emit on every verdict tier, not only MIDDLE_BAND), 4-tag
taxonomy: `EXTRACTION_NEVER_FIRED` / `ORGANS_ABSTAINED_NEAR_MISS` (concept_similarity found something
sub-threshold) / `ORGANS_ABSTAINED_NO_LEXICAL_ANCHOR` (event verb OOV of every organ -- the
non-lexical/deep-inference signature) / `ORGANS_FIRED_WRONG`. Plus an extraction-precision spot-check
sample (recovered-correct vs recovered-wrong, up to 5 each) so a flat result is diagnosable per-item,
not just per-aggregate.

## Compute architecture

Sequential-CPU. Glass-box lexical/parse-structural pipeline: CandidateGenerator (persisted UPOS-tagger
+ arc-parser) + referent-linkage tiering + fired-majority-vote composition. `crlb_n/a`: no swept
capacity regime, no decoded/noisy continuous signal. `storage_strategy`: no persistent storage (cohort
predictions checkpointed per-item via `tools/exp_checkpoint.py` for crash-resilience only). MEASURED
wall time: self-test ~15s (CandidateGenerator checkpoint load dominates), smoke (n=80, cohort_n=16)
32.3s, FULL (ENLARGED 900-row cohort_n=152 + n=160/n=80 robustness) 592.2s (~10min) -- run
FOREGROUND-TO-COMPLETION with an explicit 600000ms Bash timeout per the INLINE-LOCAL-for-light-compute
discipline, resumable per-item throughout (`tools/exp_checkpoint.py`, unit = one (arm, row-index) pair).

## Cardinality / discriminator / atomicity gates (SCHEMA-VET checklist)

- `cardinality_ok`: MEASURED True; `expected_n_units` = `enlarged_cohort_n*2 + enlarged_gold_unfulfilled_n`
  = `152*2 + 37 = 341` (REAL + ABLATION over the full cohort, PAIRSCRAMBLE over the gold-Unfulfilled
  subset only) -- MEASURED 341/341.
- `discriminator_reachability`: smoke (n=80, cohort_n=16) verified extraction fires non-vacuously
  (1/16, `arms_differ_real_vs_ablation` structurally distinct even when both abstain) before committing
  to the heavier ENLARGED run, per DISCRIMINATOR-MUST-SURVIVE-SCALE.
- `arms_differ_verified`: hash-compared REAL vs ABLATION predictions over the full enlarged cohort at
  FULL -- MEASURED True (differ).
- `final_metrics_atomicity`: `tmp_replace`.
- `deterministic_seeding`: fixed integer seeds throughout (`ENLARGED_SEED=20260809`,
  `SEED=20260808`, `random.Random`/`sorted(set())` discipline, no `hash()`-derived ordering).
- `progress_logging`: `print_flush_true` (elapsed 592s clears the `timeout_s>=1800` mandate's spirit
  defensively; every phase prints).
- `real_code_path_exercised`: self-test constructs the REAL `CandidateGenerator` + real
  `find_desired_state`/`_referent_links`/`relation_votes_grounded` calls on hand-authored cases, not a
  synthetic-only branch; MEASURED PASS (no DesireDB/network needed for self-test).

## Cert gate

N/A -- no production file edited.

## Files touched

- `hdlab/outcome_event_extraction.py` (NEW).
- `experiments/exp_outcome_event_extraction_recovery_v1.py` (NEW).
- `preregs/2026-08-09_outcome_event_extraction_recovery_v1.md` (this file, NEW).
- No existing file edited.

## MEASURED result (FULL run, filed for the record; Director/Skunkworks VET decides interpretation)

`data/exp_outcome_event_extraction_recovery_v1/metrics.json`. **Verdict: HARD_FAIL** --
`HF2_EXTRACTION_NOT_THE_LEVER` (gap_real_vs_ablation=0.0000 < 0.05) and
`HF3_PAIRSCRAMBLE_FAILS_TO_COLLAPSE` (both trivially true off a real-arm floor of 0.0). Enlarged cohort
n=152, gold-Unfulfilled n=37 (byte-identical to M1/M2's own measured 37, confirming the reused
construction). extraction_fire_rate_real=0.0541 (2/37); recovery_real=0/37, recovery_ablation=0/37,
recovery_pairscramble=1/37. Diagnosis: `EXTRACTION_NEVER_FIRED`=35/37, `ORGANS_ABSTAINED_NO_LEXICAL_
ANCHOR`=2/37 -- ZERO `ORGANS_FIRED_WRONG` and ZERO `ORGANS_ABSTAINED_NEAR_MISS`. The extraction-precision
spot-check on the 2 items where extraction DID fire shows BOTH were false-positive literal-word
collisions on garbled/duplicated DesireDB text (a common-word/idiom match, not a genuine outcome-event
match) -- extraction's precision on its rare fires is as weak as its recall. n=160 full-bench composed
macro-F1 = 0.6623, byte-identical to the freshly-measured base pipeline (0.6623) -- HP5/HP6 pass
trivially (no regression, clears the RULE floor) precisely because REAL changed zero verdicts there
either. `full_cohort_accuracy_real`=0.75 vs `majority_baseline`=0.7566 (a small, sub-HF5-margin
false-positive cost: one gold-Fulfilled cohort item flipped wrong). This CONFIRMS and SHARPENS the
Director's own prior "extraction wall decomposition" finding (backup L67): the residual is not
clause-selection-findable at all via referent-linkage/lexical recurrence -- the outcome text genuinely
does not mention the goal's referent, even loosely, in the overwhelming majority (35/37) of cases; this
is DEEP SITUATION-MODEL INFERENCE, not an extraction-precision or extraction-recall problem this
specific (referent-linkage clause-selector) mechanism can close.
