---
priority: 108
slug: the_role_competition_has_no_nmod_class_a_nominal_licensed_by_a_nominal_is_a_property_not_an_oblique_and_every_label_consumer_must_read_one_structure
status: OPEN
review:
review_text:
---

# PROBLEM: the role competition cannot say "this nominal modifies another nominal" -- its inventory has no NMOD class, so every gold `nmod` is wrong whatever heads it is handed (0 of 489 even on the gold tree), the heads rung's whole nmod gain dies at that boundary, and the consumers that need labels (causation typing among them) still read the supervised arc labeler instead of the competition.

**slug:** `the_role_competition_has_no_nmod_class_a_nominal_licensed_by_a_nominal_is_a_property_not_an_oblique_and_every_label_consumer_must_read_one_structure` -- **opened:** 2026-09-14 02:00 by strategy from pri 94's phase-7 section 17 (its counts are reproduced below) and from the causation-typing landing witness repair (ledger 2026-09-14 01:30).

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Name the structure and the computation; replicate the OPERATION, sweep the PARAMETERS (never adopt a number).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- spaCy / nltk taggers / any off-the-shelf parser / treebank-trained model at inference is a DEFECT; the UD treebank is a MEASURING instrument only (its trees are never read while deciding).
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** the role competition is the LABELS arm of the Competition-Model organ (`hdlab/graded_role_assigner.py`; sibling arm `hdlab/attachment_arm.py`). Add the class THERE; do not build a second labeler and do not leave a consumer on the supervised `arc_labeler`.
> **PLASTIC, NEVER FROZEN:** knowledge = counts in `coarse_role_validities`; strengths = one pure function of counts; the `observe_*` path must cover the new class.
> **WALL-PUSH PROTOCOL:** before writing wall / ceiling / negative, read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md`.
> **A rigorous negative is a PASS** only if what failed was the brain's mechanism, faithfully built, with the number.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** A case-marked phrase licensed by a PREDICATE is an oblique participant of an event; one licensed by a NOMINAL is a property of a thing. The distinction is a pure function of the LICENSING HOST'S CATEGORY (the Competition Model's configuration cue, which the organ already computes for its head-category term) -- not a new cue, a missing CLASS. Measured against the gold tree the host-category rule is 98.1% correct (obl 468/477, nmod 524/534); the 19 residuals (8 nmod with an ADJ host, 5 obl with a NOUN host, 2 nmod with an ADV host, 4 singletons) are what the competition should LEARN toward -- implement the class as learned cue values (host category x order x case marker, the organ's own cue form), never as a hard rule.
> 2. **REUSE.** `hdlab/graded_role_assigner.py` (`ROLE_CLASSES` = [SUBJ, OBJ, PASS_SUBJ, BY_AGENT, OBL, OTHER, IOBJ]; `ROLE_TO_DEP` emits nsubj, nsubj:pass, obj, iobj, obl, obl:agent, dep -- no nmod; `coarse_roles`, `coarse_role_posterior`, the joint frame-slot decode `assign_slots_*` which only groups dependents of a VERB/AUX head -- everything else takes the independent read where OTHER wins by default); `tools/build_coarse_role_validities.py` (`--perceived --weight`; the table must be REBUILT with the new class); pri 94's instruments in `experiments/exp_attachment_pp_association_unambiguous_mining_v1.py` (the labels-consequence read, `metrics_diagfix6000.json`); pri 103's SOLVED.md (cue set v3, the subtype-preserving gold loader); the consumers: `hdlab/causation_typing.py` (`_build_adapt_sent` labels with the supervised `ArcLabeler` -- 'The storm flooded the village': correct head, label `dep`, affector lost), `hdlab/predicate_argument_frontend.py`, `hdlab/affected_entity_resolver.py`, the space register (obl), `_frontend_labeler` sites in `hdlab/situation_reader.py`.
> 3. **GENERALIZE.** Every consumer of a role/deprel must read ONE structure (the competition's posterior), or state with a number why it cannot yet.
> 4. **WALL -> DEEPER.** If the class lands but the consumer numbers do not move, check the joint decode's capacity rule (a noun takes many modifiers -- NMOD must NOT be capped per head, like OBL and OTHER) and the OTHER prior that currently absorbs these tokens.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep the class's cue set and the table's smoothing only.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Measure under GOLD heads and under the LIVE heads (frontend Parser, in-order) separately on UD-EWT test 700 (subtype-preserving gold): label accuracy over the 932 nominal-tagged obl+nmod tokens (443 obl, 489 nmod) and over all nominals the organ can express (n = 2099; currently 0.5765 -> 0.5622 under the better heads -- the confusions obl->dep 61 -> 96 and nmod->dep 195 -> 214 must REVERSE); the board's 7 dimensions no-regress (`experiments/exp_situation_model_qa_modern_v1.py --run`, HDLAB_EXP_NAME set); the causation landing doc ('storm' must become the affector of 'flooded').
> 7. **ADJACENT.** pri 94's two-sided acquisition teacher removes the regression upstream WITHOUT touching the consumer (0.5769 vs 0.5760) -- a mitigation, not this fix; both are needed and independent. pri 106 (the role margin as a reliability signal) reads the same posterior -- do not duplicate it.
> 8. **COMPLETION BAR.** gold nmod labelled correctly under gold heads from 0/489 to >= the host-category ceiling minus noise (>= 0.90) CI-separated, obl not down; under LIVE heads the 82-gained / 40-lost head repairs reach the label (all-nominal role accuracy UP CI-separated vs the 0.5622 base, at least +0.0415's worth); at least one consumer moved from the supervised labeler to the competition with its own measurement (causation typing's affector recovered on the landing doc; or the space register's obl); twin at floor; table rebuilt with counts and the observe path -- OR a numbered located negative naming the upstream quantity that blocks it.

**(PHASE DIAGRAM.)** Cue set, smoothing and the OTHER prior are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Tokens -> categories -> heads (the frontend Parser's in-order tree + posterior) -> THIS labels rung -> every role consumer. Report the loss per rung with counts.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The organ that names the part each word plays ("who did it", "what was done to", "where / with what") has no name for "which belongs to which thing" -- the phrase in "the roof of the house" or "the man with the hat". So every such phrase gets the wrong name no matter how well the previous organ attached it, and the improvement the previous organ just made (attaching those phrases to the right noun, +8 points) is thrown away at this step; worse, the better attachments push these words into the "other" bin, and the reads that combine names get slightly worse. Separately, at least one reader (the one that types cause / enable / prevent) still takes its names from the old statistical labeler rather than this organ, and on the sentence "The storm flooded the village" it loses the storm.

## 2. WHY THIS ONE
A missing class at the labels rung with the number attached (0 of 489), a 98%-correct brain-foundational definition already computed by the organ, +0.0415 CI-separated waiting at the consumer, and the consumers' one-structure defect found on the same day.

## 3. MEASURED vs INFERRED
MEASURED (pri 94, UD-EWT test 700, cap 6000, in-order): all numbers in the checklist. MEASURED (strategy, 01:30): causation typing's labeler gives `dep` to 'storm' on the correct head. INFERRED: the size of the board movement (the board's who-did-what arms are frontend islands; the reader's own consumers will move first).

## 4. ALREADY TRIED / DO NOT REDO
Reverting the heads rung (the head gain is real and CI-separated); a hard host-category rule at read time (it is the ceiling, not the mechanism -- learn it as cue values); pri 103's five rejected levers (in its SOLVED.md).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read in full: `hdlab/graded_role_assigner.py`; `tools/build_coarse_role_validities.py`; pri 94's SOLVED.md section 17 and 12.3; pri 103's SOLVED.md; `hdlab/causation_typing.py` `_build_adapt_sent`; `verification/test_coarse_role_competition.py`, `verification/test_graded_role_assigner_organ.py`, `verification/test_causation_typed_landing_organ.py`.

## 6. THE BAR (can-fail)
See checklist item 8. Floors: the live table (no class); twin: the class's cue values permuted. Paired bootstrap over sentences; the board no-regress run.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_role_nmod_class_v1.py` (your cell), `notes/problems/<slug>/{SOLVED.md, graded_role_assigner_nmod_patch.diff}` (unified diff against `hdlab/graded_role_assigner.py`, `tools/build_coarse_role_validities.py`, and the consumer you move), and the rebuilt table as a NEW file under `data/hook_state/` (strategy swaps it live). Never edit hdlab/ or tools/ directly.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. 19c (LitBank) numbers are informational only.
