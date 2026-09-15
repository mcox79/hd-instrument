---
priority: 124
slug: the_last_separate_voice_detector_voice_cues_robust_passive_feeds_the_coarse_roles_and_the_patient_arms_floor_with_fitted_validities_fold_it_onto_the_one_voice_organ_and_refit_the_validities_from_counts
status: OPEN
review:
review_text:
---

# PROBLEM: after pri 111 folded five voice detectors onto one organ (`is_passive_predicate`, the auxiliary chain read at the predicate, counts with an observe path), ONE separate detector remains on the live path -- `voice_cues` / `robust_passive` in `hdlab/graded_role_assigner.py` (lines ~78 / ~99), feeding the coarse-role cues (the `strong` half, ~658), `cue_supports` (`passive_strong` / `passive_weak`, ~154), `verb_subcat.py:95` and the reader -- and it could not be folded because its two cue values are FITTED constants in `DEFAULT_VALIDITIES` (`passive_strong` 3.2317 / `passive_weak` -2.9927) and it is the voice inside the patient arm's own FLOOR; the brain-foundational form is one voice organ whose validities are accrued from counts, with the patient floor recomputed in place.

**slug:** `the_last_separate_voice_detector_voice_cues_robust_passive_feeds_the_coarse_roles_and_the_patient_arms_floor_with_fitted_validities_fold_it_onto_the_one_voice_organ_and_refit_the_validities_from_counts` -- **opened:** 2026-09-15 by strategy from pri 111's SOLVED.md (section 17.5, the D3 rows of its detector table, next step 'D3 own brief').

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** One voice computation (the auxiliary opens the passive expectation for the predicate it attaches to; the next non-adverbial word confirms or cancels; the by-phrase confirms) serves every consumer; its cue validities are acquired from usage, not fitted once. Replicate the OPERATION, sweep the PARAMETERS.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- fitted constants are the stand-in; counts with an observe path are the landed form (pri 111's `passive_voice_counts_v1.json` and its observe are the template).
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** `hdlab/thematic_role_labeler.is_passive_predicate` (pri 111) is the voice organ; `voice_cues` / `robust_passive` become thin delegates (keep the names so the consumers do not churn), and the two validities are refit from counts on the organ's read.
> **FOLD A DETECTOR ONTO ONE ORGAN -> CHECK THE CONSTRUCTION'S OWN POPULATION, fold to a STRICT SUPERSET** (memory rule from pri 111: two folds looked like precision gains and were losing recall on other corpora).
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** (a) Make `voice_cues` / `robust_passive` read the one organ (a strict superset of what they detect today: the organ's read OR the evidence they used, measured on THEIR construction's population -- the `strong` / `weak` split they emit); (b) refit `passive_strong` / `passive_weak` as count-accrued validities (the Competition Model's cue validity = the cue's conflict validity from confirmed role assignments) with an observe path, replacing the fitted 3.2317 / -2.9927; (c) recompute the patient arm's FLOOR in place (its fallback `hybrid_role_patient` reads `precise_passive`, already the organ; its `robust_passive` half is this brief) so the margin is honest on both sides.
> 2. **REUSE.** pri 111's SOLVED.md 17.5 / 18-20 and its cell (the per-consumer witness runs; the detector table with file:line), `hdlab/thematic_role_labeler.py` (`is_passive_predicate`, the counts asset, the observe path), `hdlab/graded_role_assigner.py` (`voice_cues`, `robust_passive`, `DEFAULT_VALIDITIES`, `cue_supports`, `coarse_role_cues`), `hdlab/verb_subcat.py:95`, the patient board arm (`exp_board_patient_slot_v1`, `_deployed_structural_patient_pick`), `tools/build_coarse_role_validities.py` (pri 108's rebuild path; pri 114's organ-tagged acquisition is the same principle), the witnesses `test_labeled_patient_landing.py`, `test_valency_labeled_patient_landing_organ.py`, `test_coarse_role_competition.py`.
> 3. **GENERALIZE.** Every consumer of `passive_strong` / `passive_weak` / `voice_cues` / `robust_passive` (grep) reads the one organ or is reported with its number.
> 4. **WALL -> DEEPER.** If the refit validities lose against the fitted constants on the patient row, the loss is where the fitted constants encoded a convention the counts do not carry -- name it with the items; the bar is the organ form with counts, and a fitted constant is not an answer.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep the count smoothing only.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** The detector's own construction population (the `strong` and `weak` firings on UD-EWT test; P/R vs `nsubj:pass` / `aux:pass` as the measuring gold; the fold as a strict superset); the coarse-role labels rung on UD-EWT test 700 (PASS_SUBJ / BY_AGENT / all-nominal role accuracy, live table vs refit); the board's who-did-what patient AND agent rows full size, both arms in one process, floor recomputed in place; GUM / GENTLE out of supply.
> 7. **ADJACENT.** pri 111 (landed), pri 108 (the labels rung), pri 114 (organ-tagged acquisition; validity rebuild), pri 123 (the participle/adjective boundary the voice organ reads).
> 8. **COMPLETION BAR.** No separate voice detector left on the live path (grep-level witness); the two validities are counts with an observe path (twin: validities permuted, at floor); the strict-superset fold loses no firing on its construction population; labels rung not down; patient and agent rows not down full size with the floor recomputed -- OR a numbered located negative naming the consumer that cannot read the one organ and why.

**(PHASE DIAGRAM.)** The count smoothing and the strong/weak split threshold are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Tokens -> categories -> heads -> THIS voice read -> roles / the patient and agent competitions / the board.

## 1. THE PROBLEM IN PLAIN LANGUAGE
Yesterday five of the system's six ways of deciding "is this passive?" became one, learned from counts. The sixth is still separate because two of its numbers were fitted by hand long ago and the board's own baseline for "who was acted on" is built on it. Fold it onto the one organ too, learn its two numbers from experience, and recompute that baseline honestly.

## 2. WHY THIS ONE
The last islanded copy of a structure that was consolidated yesterday; it carries fitted constants on the live path (not brain-foundational) and sits inside a board floor, so leaving it distorts both the read and the measurement.

## 3. MEASURED vs INFERRED
MEASURED (pri 111 §17.5, 20): `voice_cues` / `robust_passive` at `graded_role_assigner.py:78/:99` with consumers at :154, :658, `verb_subcat.py:95`, the reader; fitted `passive_strong` 3.2317 / `passive_weak` -2.9927; the two patient witnesses green both ways under the other folds. INFERRED: the refit's effect on the labels rung and the patient row.

## 4. ALREADY TRIED / DO NOT REDO
Folding without refitting (pri 111 declined for exactly this reason); a narrowing fold measured only on the consumer's gold (the memory rule).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read in full: pri 111's SOLVED.md sections 17-20 and its cell; `hdlab/thematic_role_labeler.py`; `hdlab/graded_role_assigner.py` (voice_cues, robust_passive, DEFAULT_VALIDITIES, cue_supports, coarse_role_cues); `hdlab/verb_subcat.py`; `experiments/exp_board_patient_slot_v1.py`; `tools/build_coarse_role_validities.py`; the three witnesses named above.

## 6. THE BAR (can-fail)
See checklist item 8. Floors: the fitted constants as shipped; twin: validities permuted; paired bootstrap over items; the full board in one process with and without.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_voice_organ_last_fold_v1.py` (your cell), `notes/problems/<slug>/{SOLVED.md, voice_last_fold_patch.diff}` (unified diffs against `hdlab/graded_role_assigner.py`, `hdlab/verb_subcat.py` and, if the builder changes, `tools/build_coarse_role_validities.py`; never edit hdlab/ or tools/ directly), and the NEW count asset under `data/hook_state/`.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. 19c numbers are informational only.
