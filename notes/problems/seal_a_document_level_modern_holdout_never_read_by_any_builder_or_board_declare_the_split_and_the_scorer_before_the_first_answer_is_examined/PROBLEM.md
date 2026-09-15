---
priority: 126
slug: seal_a_document_level_modern_holdout_never_read_by_any_builder_or_board_declare_the_split_and_the_scorer_before_the_first_answer_is_examined
status: OPEN
review:
review_text:
---

# PROBLEM: every modern number we publish comes from test splits the project has used repeatedly to choose integrations, thresholds and defaults (UD-EWT test on the agent/patient rows and the evaluation's probe; GUM test 128 docs on the coref/salience/state rows; the WiC experiment pools dev and test), so no result is a measurement on a newly sealed population -- seal a document-level modern holdout that no acquisition builder, witness or board has ever read, declare the split rule, the overlap audit, the fixed scorer and the fixed configuration BEFORE the first held-out answer is examined, and report per-dimension results with the DOCUMENT as the unit of uncertainty.

**slug:** `seal_a_document_level_modern_holdout_never_read_by_any_builder_or_board_declare_the_split_and_the_scorer_before_the_first_answer_is_examined` -- **opened:** 2026-09-15 by strategy from the external substrate evaluation (`notes/SUBSTRATE_EVALUATION.md`, finding E13 and its limits section); sequenced AFTER pri 122 (board rows on the live reader) and pri 125 (pronoun discovery from text) land, because a holdout scored through a scorer that reads the annotation column measures the leak, not the reader.

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **THIS IS AN INSTRUMENT BRIEF.** The measurement bar applies in full: per-item scoring on the row's own population, gold-free at decision time, floors recomputed in place, an information-free twin, CI half-widths, modern gold only; 19c informational.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- spaCy, GLUCOSE, MAVEN and ANY off-the-shelf parser/dataset/model are NOT brain-foundational; a vetted static offline FOUNDATION asset is admissible supply; an external tool AT INFERENCE is a DEFECT THAT BLOCKS. This brief changes NO organ: it seals data and fixes a scorer.
> **THE HOLDOUT IS SEALED BY ENUMERATION, NOT BY ASSERTION:** 'never read' means every builder under `tools/`, every experiment under `experiments/`, every witness under `verification/` and every asset under `data/hook_state/` / `data/frontend_assets/` is grepped for the corpus paths and split names it reads, and the held-out document ids are absent from all of them, with the enumeration published.
> **PLAIN LANGUAGE:** the scorecard line for the holdout says in words what was held out, how it was chosen, and that nobody looked at it before the rule was written.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** (a) Enumerate, with file:line, every reader of `data/corpora/ud_english_ewt/*`, `data/corpora/gum/conllu/*` (GUM 275 documents + GENTLE 26), and any other modern gold, and which split / document ids each consumes (builders that TEACH from a split are the critical ones: an asset built on a document contaminates it). (b) From the documents no builder, witness or board row has read, draw the holdout by a PRE-DECLARED seeded rule (document as the unit; stratified by genre; the seed and the rule committed before the draw is executed) -- if UD-EWT and GUM test are both consumed everywhere, the holdout is GUM dev / the unread GUM documents / GENTLE genres with the fewest prior reads, and the report says so. (c) Commit the sealed id list + a SHA-256 of each document + the fixed scorer + the fixed configuration manifest (resolved tag source, heads source, every default flag, asset hashes) BEFORE running the reader on it. (d) Score ONCE per dimension through the live reader on text only (the pri 122 instrument), with abstentions counted wrong, all eligible gold questions in the denominator; report per-dimension model / strongest floor / twin with document-level bootstrap CIs; then the same on the annotated-input path, labelled. (e) Publish the overlap audit (the enumeration) beside the numbers.
> 2. **REUSE.** pri 122's reader-driven rows (`experiments/exp_board_rows_on_the_reader_v1.py` when landed) and its provenance fields; `experiments/gum_coref.py` (the loader; document ids and genres); pri 109's paired-subpopulation instrument; the evaluation's five-document scorer (appendix A2) as the agent/patient/state proxy if pri 122's rows are not yet reader-driven; `tools/substrate_health.py` (the run manifest).
> 3. **GENERALIZE.** The holdout id list becomes a repository asset every future board run can name; a witness asserts no builder reads a held-out id (grep-level, pytest-collectable).
> 4. **WALL -> DEEPER.** If no unread modern documents remain, say so with the enumeration and propose the next sealed source (a new modern corpus placed under `data/corpora/` with provenance) rather than re-using a read split.
> 5. **OPTIMIZE BY EXACT REPLICATION;** no parameters.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Not a read-path change; the report is the seven dimensions on the sealed documents, text-only and annotated, with the previous test-split numbers beside them so the generalisation gap is visible per dimension.
> 7. **ADJACENT.** pri 122 (instrument), pri 125 (text-only reading), the WiC pooling (E03/E13: report dev and test separately from now on).
> 8. **COMPLETION BAR.** A committed sealed list with hashes, a committed rule and seed dated before the draw, an enumeration proving no builder/witness/board read those ids, a fixed scorer and configuration manifest, and the per-dimension held-out table with document-level CIs -- OR a numbered reason no unread modern document exists and the proposed next corpus.

**(PHASE DIAGRAM.)** Nothing to sweep.
**(FULL-STACK UPSTREAM.)** Not a read-path change.

## 1. THE PROBLEM IN PLAIN LANGUAGE
Every score we quote comes from test passages the project has looked at many times while deciding what to build. That is fine for steering the work, but it is not proof the reader works on passages it has never met. Set aside a batch of modern passages nobody has touched, write down the rule for choosing them and how they will be graded before looking, then grade once.

## 2. WHY THIS ONE
The outside review named it as the limit on every capability claim; it is cheap; and it must be sealed BEFORE the next round of landings uses the same test splits again.

## 3. MEASURED vs INFERRED
MEASURED (the evaluation): UD-EWT test used for the agent/patient rows and its own probe; GUM test 128 documents for the coref/salience/state rows; WiC dev+test pooled. INFERRED: which GUM / GENTLE documents remain unread by every builder (the enumeration decides).

## 4. ALREADY TRIED / DO NOT REDO
Treating repeated runs on the same test split as replication.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read: `notes/SUBSTRATE_EVALUATION.md` (E03, E13, limits); `experiments/gum_coref.py`; `experiments/exp_situation_model_qa_modern_v1.py` (which splits each row loads); `tools/build_*.py` (every builder's corpus reads); pri 122's SOLVED.md when landed.

## 6. THE BAR (can-fail)
See checklist item 8.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_sealed_modern_holdout_v1.py` (the enumeration, the draw, the manifest, the scoring; `get_output_dir` per Q115), `data/corpora/holdout/SEALED_modern_v1.json` (ids + hashes + rule + seed + date), `verification/test_sealed_holdout_is_unread.py`, `notes/problems/<slug>/SOLVED.md`. Never edit hdlab/ or tools/.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. 19c numbers are informational only.
