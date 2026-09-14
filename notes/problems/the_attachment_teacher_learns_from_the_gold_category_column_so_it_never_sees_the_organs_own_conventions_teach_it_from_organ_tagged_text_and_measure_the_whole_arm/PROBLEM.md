---
priority: 114
slug: the_attachment_teacher_learns_from_the_gold_category_column_so_it_never_sees_the_organs_own_conventions_teach_it_from_organ_tagged_text_and_measure_the_whole_arm
status: OPEN
review:
review_text:
---

# PROBLEM: the attachment arm's acquisition teacher (`tools/build_attachment_validities.py`) reads the GOLD UPOS column of the training text, so every cue table is learned over categories the live organ never produces at read time -- the read-time predicate slot (pri 110) is invisible to it, and so is every other convention of the live tagger; pri 110 measured the controlled contrast: teaching the teacher from ORGAN-tagged text is worth +0.0025 CI-separated on top of the read-time slot (+0.0117 CI[+0.0065,+0.0175] together vs +0.0086 slot alone), and it changes every cue table, so landing it is a whole-arm decision with a board A/B.

**slug:** `the_attachment_teacher_learns_from_the_gold_category_column_so_it_never_sees_the_organs_own_conventions_teach_it_from_organ_tagged_text_and_measure_the_whole_arm` -- **opened:** 2026-09-14 by strategy from pri 110's phase-7 section 10d (7A) and its question 1.

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** A learner acquires attachment validities from the categories IT perceives, not from a teacher's answer key: the train/read mismatch is the defect. Replicate the OPERATION, sweep the PARAMETERS.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- an offline FOUNDATION asset built from a treebank is admissible; a teacher that reads a column the live organ never produces builds an asset for a different organ than the one that reads it.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** the attachment arm (`hdlab/attachment_arm.py`) and its builder are one organ; change the builder's INPUT (organ-tagged categories, with the predicate-slot revision) and its measurement, not the cue algebra (pri 94 / 105 / two-sided teacher stay as landed).
> **PLASTIC, NEVER FROZEN:** the observe path must accrue from organ-tagged text too.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** The Competition Model's cue validities are acquired from the learner's own perceived input (Bates & MacWhinney 1987; MacWhinney 2012): the cue is 'the category I assigned', so the table must be indexed by the categories the live organ assigns, including its systematic conventions (VERB-as-AUX repaired by the slot, ADJ/PROPN and NOUN/ADJ confusions, SCONJ/ADP). Built form: the builder tags its training sentences with the live category organ (`hdlab.frontend.tagger()`, with HDLAB_LC_PREDICATE_SLOT on) and learns the cue tables from those categories against the gold ARCS (the arcs are the environment's feedback; the categories are perception). pri 110 built it at cap 6000 as `data/hook_state/attach_pri110_orgtags_slot{off,on}_cap6000_v1.json`: read-time slot only +0.0086 SEP; rebuilt asset only +0.0033 n.s.; both +0.0117 CI[+0.0065,+0.0175] SEP; the controlled O1-O0 contrast +0.0025 CI-separated at both read-time settings.
> 2. **REUSE.** `tools/build_attachment_validities.py` (its call site must pass everything the live organ passes -- 2026-09-14: a teacher shipped oblique-only because the association was never passed at the builder's call site), pri 110's `exp_one_convention_two_losses_v1.py` §10d harness and its two hook_state assets, pri 94's two-sided teacher and pri 105's core-arc work, the live asset `data/frontend_assets/attachment_validities_v1.json` (previous versions under `data/hook_state/`), `verification/test_attachment_arm_*`, the UD-EWT test 700 governor instrument (UAS / LAS per relation, in-order decode).
> 3. **GENERALIZE.** Every other asset builder that reads a gold column the live organ replaces at read time (the coarse-role validities builder `tools/build_coarse_role_validities.py --perceived` already has a perceived mode -- check it is the shipped one; the lexical-categories counts; the copular / state tables): list them and state for each whether it learns from perception or from the key.
> 4. **WALL -> DEEPER.** If organ-tagged acquisition loses on some relation, that relation's cue is being learned on a tagger error class -- report the class with counts (the categories rung's next item), do not revert to gold categories.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep the cap and the teacher's beta only.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Governor UAS on UD-EWT test 700 under the live chain, per relation (root / nsubj / obj / obl / nmod / cop / expl), full cap (not 6000), gold-tagged vs organ-tagged acquisition, with the read-time slot on in both; GUM / GENTLE out-of-supply; the board's 7 dimensions (`experiments/exp_situation_model_qa_modern_v1.py --run`, HDLAB_EXP_NAME set); the copular state read; the attachment witnesses green with re-pins where the asset changes numbers.
> 7. **ADJACENT.** pri 110 (landed: the slot), pri 113 (non-verbal predication), pri 108 (labels rung; the coarse-role builder's perceived mode is the same idea one rung down).
> 8. **COMPLETION BAR.** Full-cap organ-tagged asset built as a NEW file under `data/hook_state/`; governor UAS up CI-separated vs the gold-tagged asset with the slot on in both, no relation down CI-separated; board not down on any dimension; witnesses green (re-pinned with the asset named); the observe path accrues from organ-tagged text -- OR a numbered located negative naming the relation / tag-error class that blocks it.

**(PHASE DIAGRAM.)** Cap, beta, and the slot threshold at acquisition time are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Tokens -> categories (the organ's own, with the slot) -> THIS acquisition -> heads -> every consumer below.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The organ that learns how words attach to each other was taught using the answer key's word categories, but when it reads it uses its own guesses about categories. So it learned rules for a world it never sees. Teaching it from its own categories gains a little on its own, and a bit more together with the copula fix, and it makes the learner honest. Because it changes every rule it learned, the whole organ must be re-measured before it goes live.

## 2. WHY THIS ONE
A train/read mismatch at the heads rung with a controlled CI-separated gain already measured (pri 110 §10d) and an asset already built at cap 6000; the full-cap build and the whole-arm A/B are what remain.

## 3. MEASURED vs INFERRED
MEASURED (pri 110 §10d, cap 6000, UD-EWT test 700): slot only +0.0086 SEP; asset only +0.0033 n.s.; both +0.0117 CI[+0.0065,+0.0175] SEP; O1-O0 +0.0025 CI-sep at both settings. INFERRED: the full-cap number and the board movement.

## 4. ALREADY TRIED / DO NOT REDO
Nothing at this rung; do not re-derive the cue algebra (pri 94 / 105 landed and measured).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read in full: `tools/build_attachment_validities.py`; pri 110's SOLVED.md §10d and its cell; `hdlab/attachment_arm.py` (load / decode / observe); `hdlab/frontend.py`; the attachment witnesses under `verification/`.

## 6. THE BAR (can-fail)
See checklist item 8. Floors: the live gold-tagged asset with the slot on; twin: an asset built from shuffled categories; paired bootstrap over sentences; the board run with and without.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_attachment_acquisition_from_organ_tags_v1.py` (your cell), `notes/problems/<slug>/{SOLVED.md, attachment_teacher_patch.diff}` (unified diffs against `tools/build_attachment_validities.py` and, if needed, `hdlab/attachment_arm.py`; never edit hdlab/ or tools/ directly), and the NEW asset under `data/hook_state/` (strategy swaps it live).

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. 19c numbers are informational only.
