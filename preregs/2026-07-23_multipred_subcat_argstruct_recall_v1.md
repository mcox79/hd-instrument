# Pre-registration: multipred_subcat_argstruct_recall_v1

Filed: 2026-07-23 (BEFORE the FULL run below; design-probe iteration used SMOKE_SLICE + FULL_SLICE for
mechanism design only, bands adopted from the pre-existing diagnosis note, not re-set post-hoc).

## Question

Does extending the hand-rule reader's `find_main_verb` (ONE main-verb argument-role pass per sentence) to
process EVERY predicate in a sentence -- each with its own local argument-role pass, gated by a per-verb
SUBCAT/VALENCY frame -- recover the 68%-dominant multi-predicate extraction miss class the leg-2 diagnostic
localized (notes/research_recall_miss_extraction_vs_filter_diagnosis_2026-07-23.md), without flooding
precision?

## Script

`experiments/exp_multipred_subcat_argstruct_recall_v1.py` (full docstring = the complete pre-registration;
this file is a pointer + the exact band values for quick reference).

## Data / split (FAIRNESS)

Same as `exp_pivot_rich_knowledge_full_reader_integration_v1` (29473): FULL_SLICE = L04/L05/L07/L08/L09/L10/
L12; SMOKE_SLICE = L04/L05. Gold = `data/gold_mcguffey_lccp_argstruct_v1.json` (independent, single-
annotator; NOT read while authoring the NOPAT subcat override table).

## Arms

- BASELINE: the real production single-verb reader (`exp_learned_argstruct_parser_lccp_independent_gold_v1
  .load_slice_and_reader`), reused verbatim.
- MULTIPRED_KEEPALL: multi-predicate extraction, subcat gate DISABLED -- MUST-FAIL control (a).
- MULTIPRED_FRAMES: multi-predicate extraction WITH the subcat gate -- headline arm.
- MULTIPRED_SCRAMBLED: multi-predicate extraction, subcat-gate TRUTH TABLE permuted -- MUST-FAIL control (b).

## Pre-registered bands (set BEFORE this run)

The recall_ceiling primary bar (`>= 0.65`, rise `>= 0.05` floor for non-HARD_FAIL) is the diagnosis note's
OWN pre-existing "cheap decisive test" bar (predates this cell's build); this cell adds the required
F1/precision/must-fail-control conditions per the routing task.

- **HARD_PASS_MULTIPRED_RECOVERS_AND_HOLDS_PRECISION**: `recall_ceiling(FRAMES) >= 0.65` AND
  `recall_ceiling(FRAMES) - recall_ceiling(BASELINE) >= 0.15` AND `F1(FRAMES) > F1(BASELINE)` AND
  `precision(FRAMES) >= precision(BASELINE) - 0.02` AND `precision(FRAMES) > precision(KEEPALL)` AND
  `recall_ceiling(FRAMES) > recall_ceiling(SCRAMBLED)` AND zero regression on baseline-covered items.
- **HARD_FAIL_MULTIPRED_NEEDS_REAL_PARSE**: `recall_ceiling(FRAMES) - recall_ceiling(BASELINE) < 0.05` OR
  `F1(FRAMES) <= F1(BASELINE)` OR `precision(KEEPALL) >= precision(FRAMES)`.
- **MIDDLE_BAND**: otherwise.

## Compute architecture

Class (b) sequential-CPU with justification (reader candidate gen reused + per-predicate local role
classification via the existing AveragedPerceptron + O(predicates) VerbNet dict lookups; no matmul/GPU
primitive). Storage: no_storage. Local, foreground-to-completion, NO push / NO remote-persist / NO queue.

## Result (filed after the run; see metrics.json for full detail)

`verdict = HARD_FAIL_MULTIPRED_NEEDS_REAL_PARSE`. recall_ceiling BASELINE=0.44 -> FRAMES=0.47 (rise 0.03,
below the 0.05 floor). F1 rose slightly (0.2708 -> 0.2782) and precision did not collapse (0.1956 ->
0.1975), and both must-fail controls fired correctly (KEEPALL precision 0.1486 < FRAMES 0.1975; SCRAMBLED
recall_ceiling 0.45 < FRAMES 0.47) -- confirming the subcat-gate DESIGN is sound -- but the trigger set's
raw recall coverage (coordinate-VP + infinitival-complement + bare-subordinator) is insufficient to clear
the pre-registered recall_ceiling bar. 17/56 baseline misses recovered, 14 previously-correct items
regressed. Honest conclusion: the residual multi-predicate misses are dominated by constructions this
lightweight trigger set does not detect (reduced relatives, gerund/participial adjuncts, prepositional-
gerund objects) -- a real shallow dependency parse is the likely next lever, not a broader frame-lookup
trigger set. CLAIM-VET-pending (skunkworks).
