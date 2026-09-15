---
priority: 122
slug: the_boards_seven_rows_never_run_the_reader_each_rebuilds_its_own_copy_from_annotated_cased_files_so_a_reader_repair_worth_0_41_propn_f1_is_board_invisible_rebuild_the_rows_on_the_live_reader
status: OPEN
review:
review_text:
---

# PROBLEM: none of the board's seven headline rows runs `SituationReader.read` -- each rebuilds its own copy of the read from the annotated CoNLL-U files (cased text, the loader's organ layer, its own candidate lists), so the reader's own sentence source, memo, register and event stream are never on the scored path; pri 116 measured it exactly: sentence-source calls 0 on every row in both arms, and a repair worth +0.41 PROPN F1 through the live reader (names 0.49 -> 0.85, name-typed mentions 242 -> 599) left all seven rows byte-identical. The board must score the reader the owner runs, or carry a provenance field that says which token stream and which case each row read.

**slug:** `the_boards_seven_rows_never_run_the_reader_each_rebuilds_its_own_copy_from_annotated_cased_files_so_a_reader_repair_worth_0_41_propn_f1_is_board_invisible_rebuild_the_rows_on_the_live_reader` -- **opened:** 2026-09-15 by strategy from pri 116's SOLVED.md (finding 2 and question 1) and the pri 113 head-to-head (both sides: 'the board is verb-gated' / 'the board cannot see it').

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **THIS IS AN INSTRUMENT BRIEF.** The measurement bar applies in full: per-item scoring on the row's own population, gold-free at decision time, floors recomputed in place, an information-free twin, CI half-widths, modern gold only (GUM / UD-EWT); 19c informational.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- the row scores the reader; it must not build a second reader. Where a row today re-implements a read (its own mention stream, its own candidate list, its own role labels from the loader), the re-implementation is the defect: the row reads `sm` (the SituationModel the live reader returns) and scores it against the gold.
> **ONE INSTRUMENT:** the seven rows stay in `experiments/exp_situation_model_qa_modern_v1.py`; the change is WHAT they read (the live reader's output on the document text), not what they ask. The converter from GUM CoNLL-U to the reader's input exists (`gum_to_conll`, `_gum_to_live`); the reader's per-document cost is known (~36 s per doc on the 128-doc test split -- budget the run).
> **PLAIN LANGUAGE:** each row's provenance line on the scorecard must say in words what was read ('the reader's own read of the raw text' vs 'a rebuilt read from the annotated file').

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** For each of the seven rows, state the read it scores today (which function builds the mention stream / events / states / roles; which token stream; cased or lowercased; which organ decisions come from the loader's organ layer vs the reader): pri 116 counted the sentence-source calls (0 on every row); pri 109 found the coref rows read the loader's organ layer; the who-did-what rows iterate gold verbs with the reader's role route on the loader's tokens; the state row reads the copular binding. Then rebuild each row so its model answer comes from `SituationReader(gaz).read(path)` on the document's text (the same reader, the same defaults, one read per document shared by all rows), scored against the same gold, floors recomputed on the same items.
> 2. **REUSE.** `experiments/exp_situation_model_qa_modern_v1.py` (the rows, the aggregate, `new_board_arms`); `experiments/gum_coref.py` (`gum_to_conll` / the loader; keep it for the GOLD, not for the model); pri 116's `experiments/exp_case_through_the_reader_v1.py` (the 16-doc live-reader harness, `board_rows_ab.json`: the seven-row A/B with sentence-source call counts); pri 121's row cell (already reader-driven); the reader's `_write_temp_conll`; pri 109's paired-subpopulation instrument.
> 3. **GENERALIZE.** Every board arm (`new_board_arms` included) gets the provenance field: `token_stream` (reader / loader), `case` (cased / lowercased), `read_by` (SituationReader.read / rebuilt); publish the table.
> 4. **WALL -> DEEPER.** If a reader-driven row drops against the rebuilt row, that drop is the TRUE live number and the repair is in the reader (the rung that loses), never in the row; report both numbers and file the reader item.
> 5. **OPTIMIZE BY EXACT REPLICATION;** no parameters; cap the run by documents, not by items, and report the cap.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Publish the seven rows rebuilt vs reader-driven on the same documents (with CIs), the aggregate on both, and the A/B of the last three landings (pri 113, 116, 117) on the reader-driven rows so their board effect is finally visible; the run cost per row.
> 7. **ADJACENT.** pri 121 (the non-verbal row; already reader-driven), pri 118 (typing), pri 116 (landed), pri 109 (gold-free rows).
> 8. **COMPLETION BAR.** All seven rows scored from the live reader's output on the document text (one read per document), provenance fields published, the old rebuilt numbers retired in `notes/reference_retired_claims_never_requote.md` with the new honest baseline stated, the three landings' effects visible -- OR a numbered reason a row cannot be reader-driven (with the rebuilt form kept and labelled).

**(PHASE DIAGRAM.)** Nothing to sweep.
**(FULL-STACK UPSTREAM.)** Not a read-path change; the rows read the reader.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The scoreboard does not score the reader we actually run. Each line quietly rebuilds its own reading from the annotated test files, so when the real reader gets much better at something (this week: keeping capital letters, which took it from 49 to 85 names in 100), the scoreboard does not move at all. The fix is to make every line grade the real reader's reading of the raw text, and to say on the board what each line read.

## 2. WHY THIS ONE
Two landings in two days (pri 113, pri 116) with large measured gains on the reader's own instruments and byte-identical boards; the owner asked why the needle did not move; the answer is this instrument.

## 3. MEASURED vs INFERRED
MEASURED (pri 116): sentence-source calls 0 on every row in both arms; seven rows byte-identical under a +0.41 PROPN F1 reader repair; (pri 113 both sides): capped and full boards byte-identical on six rows under a +0.55 non-verbal recall gain. INFERRED: the reader-driven rows' levels (expect the coref rows to move most: the mention stream is where case and typing land).

## 4. ALREADY TRIED / DO NOT REDO
Reading the gain off the rebuilt rows (byte-identical by construction); a side board (pri 121's row is registered in the one board on purpose).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read in full: `experiments/exp_situation_model_qa_modern_v1.py` (every row function and `run`); pri 116's SOLVED.md finding 2 and its `board_rows_ab.json`; pri 109's SOLVED.md (the loader's organ layer and the paired instrument); `experiments/gum_coref.py` (`gum_to_conll`, `_gum_to_live`); pri 121's cell.

## 6. THE BAR (can-fail)
See checklist item 8.

## 7. FILES AND ENTRY POINTS
Write ONLY: a cell `experiments/exp_board_rows_on_the_reader_v1.py` (the reader-driven rows standalone + the rebuilt-vs-reader table), `notes/problems/<slug>/{SOLVED.md, board_rows_on_the_reader_patch.diff}` (a unified diff against the board file; strategy applies it), and data under your get_output_dir. Never edit hdlab/ or tools/.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. 19c numbers are informational only.
