---
priority: 121
slug: the_boards_who_did_what_rows_iterate_gold_verbs_so_a_fifth_of_asserted_clauses_are_outside_their_population_add_the_non_verbal_predication_row_to_the_board
status: OPEN
review:
review_text:
---

# PROBLEM: the board's who-did-what AGENT and PATIENT rows iterate GOLD VERB predicates (`gold_agent_items`), the entity rows read mentions, and the state row reads the copular-binding path -- so the event detector's largest gain today (non-verbal-clause recall 0.19 -> 0.74 / 0.88 on the participant instrument, pri 113) has NO board row that reads it, and the same is true of every future gain on the 167-of-762 clauses whose predicate is not a verb; the board must carry a NON-VERBAL PREDICATION row (who-is-what / who-is-where / who-has-what), gold-free at decision time, scored from the reader's event stream on modern gold, so that this fifth of what a text asserts is measured on the same instrument as the rest.

**slug:** `the_boards_who_did_what_rows_iterate_gold_verbs_so_a_fifth_of_asserted_clauses_are_outside_their_population_add_the_non_verbal_predication_row_to_the_board` -- **opened:** 2026-09-14 by strategy from the owner's pri 113 SOLVED.md section 6 and next step 4, the agent's section 6, and the owner's question of 19:55 ('how did that not translate to more than 0.4 points?').

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **THIS IS AN INSTRUMENT BRIEF.** The measurement bar applies in full: the row is scored per item on its OWN population, gold-free at decision time (the gold is the answer key only), with the strongest simple floor recomputed in place, an information-free twin, CI half-widths, and the 19c corpora informational only.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- the row measures the reader; it changes nothing on the read path.
> **ONE INSTRUMENT, NOT TWO:** extend `experiments/exp_situation_model_qa_modern_v1.py` with the row (the same loader, the same split convention, the same aggregate) rather than a side board; the participant instrument built by pri 113 (both cells) is the per-clause scorer to reuse.
> **PLAIN LANGUAGE ON THE SCORECARD:** the row needs a plain-words name for `notes/SCORECARD.md` / `notes/HOW_WE_ARE_DOING.md` ('what things are / where things are / who has what').

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** The comprehension question the row asks: for a clause whose predicate is a property / class / location / possession ('the sky is blue', 'she is a doctor', 'he was here', 'the house has a roof'), did the reader build the right structure -- the right HOLDER (the clause's subject entity) with the right CONTENT (the complement) -- gold-free at decision time? Items: every subject-bearing gold clause whose gold predicate is non-verbal on UD-EWT test (167 of 762) and on GUM (366 of 1,200-cap; both populations reported), the gold being the clause's subject head and predicate head; the reader's answer being the fired event/state (pri 113's structure) or the copular state reader's pair; a hit = both heads right; floors = the shipped UPOS==VERB detector (0 by construction on these items -- report it) and the strongest SIMPLE rule (the nearest nominal before the copula as holder, the first content word after it as content); twin = a random clause token pair at the same firing rate.
> 2. **REUSE.** The participant instrument in `experiments/exp_nonverbal_predication_participants_v1.py` (owner) and `_agent_v1.py` (agent): the 762-clause population builder, the argument-structure scoring, the GUM population; the board's `per_dimension` schema (n / model_acc / strongest_floor / twin_acc / ci_sep_over_strongest / population text) and its aggregate; `gold_agent_items` (to keep the verbal rows' population unchanged); `tools/board.py` / `tools/scorecard_gui.py` (the row's plain-words line).
> 3. **GENERALIZE.** Audit every other board row for a population gate that excludes a class of clause by the gold tag (grep `upos == "VERB"` / `gold_*_items` in the board file): list them; each is either justified by its question or is the same gap.
> 4. **WALL -> DEEPER.** If the row's floor is already near the reader (the simple rule is strong on copular clauses), the row still stands as a no-regress gauge; report the margin honestly.
> 5. **OPTIMIZE BY EXACT REPLICATION;** no parameters.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Publish the row on the current tree (with the merged pri 113 landing) and on the pre-113 tree (HDLAB_NONVERBAL_PREDICATION=0) so the landing's board effect is finally visible; the aggregate with and without the row (the aggregate's population changes -- state the new honest baseline and retire the old in `notes/reference_retired_claims_never_requote.md`).
> 7. **ADJACENT.** pri 113 (landed), pri 117 (copular subject attachment: the holder), pri 119 (the typed attribute: the content), pri 120 (construction memberships).
> 8. **COMPLETION BAR.** The row published in the board's own metrics (both populations, floors, twin, CI), plain-words line on the scorecard, the pre/post-113 A/B visible on it, the aggregate re-baselined and the old figure retired -- OR a numbered reason the row cannot be gold-free at decision time.

**(PHASE DIAGRAM.)** Nothing to sweep.
**(FULL-STACK UPSTREAM.)** Not a read-path change; the row reads the event stream and the state reader.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The scoreboard only asks "who did what" about sentences with an action word. One sentence in five says what something IS or WHERE it is, and the board never asks about those, so a big improvement in reading them cannot show up as points. Add a board row that asks "what is this thing, where is it, what does it have" and grade it the same honest way as the rest.

## 2. WHY THIS ONE
Both pri 113 runs ended with the same finding (the board is verb-gated); the owner asked why the strides did not translate; without the row every landing on this fifth of the text stays board-invisible and its no-regress is unguarded.

## 3. MEASURED vs INFERRED
MEASURED: capped and full boards byte-identical / within items under the pri 113 event detector on every row except state (pri 113 both sides); the participant instrument: 0.1856 -> 0.7365 (owner) / 0.8802 (agent) on the 167, 0.57 / 0.61 on GUM. INFERRED: the row's floor level.

## 4. ALREADY TRIED / DO NOT REDO
Reading the gain off the existing rows (byte-identical by construction).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read in full: `experiments/exp_situation_model_qa_modern_v1.py` (the dimension functions, `gold_agent_items`, the aggregate), both pri 113 cells' participant instrument, `notes/STATUS.md`'s MEASUREMENT BAR, `notes/reference_retired_claims_never_requote.md`.

## 6. THE BAR (can-fail)
See checklist item 8.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_situation_model_qa_modern_v1.py` is STRATEGY'S to patch -- propose the row as `notes/problems/<slug>/board_nonverbal_row_patch.diff` plus a cell `experiments/exp_board_nonverbal_predication_row_v1.py` that computes the row standalone; `notes/problems/<slug>/SOLVED.md`.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. 19c numbers are informational only.
