---
priority: 129
slug: three_default_read_consumers_still_call_the_supervised_arc_labeler_and_the_fitted_parse_confidence_readout_patient_defer_goal_purpose_filter_copular_label_path_route_them_to_the_bf_labels_rung_and_the_competitions_own_margin
status: OPEN
review:
review_text:
---

# PROBLEM: an import probe on the DEFAULT annotation-free read of a modern GUM document (2026-09-15, one document, 85 events) shows two organs the registry marks NOT_BF being imported DURING the read -- `hdlab/arc_labeler.py` (a frozen supervised averaged-perceptron relation labeler) and `hdlab/parse_confidence.py` (a fitted logistic readout) -- by three live consumers in `hdlab/situation_reader.py`: (1) `_patient_arc_confidence` (:2377-2401; the who-did-what patient precision defer, `precision_weight_roles` default ON) calls both, plus the arc-eager conf/marg the calibrator was fitted on; (2) `_frontend_labeler` (:2403-2408) hands UD deprels to the goal ADVCL purpose filter (`goal_register.extract_goals_sentence` branch 3); (3) the entity-states path (:4311-4319) loads a private `PosTagger` + `ArcParser` + `ArcLabeler` for `copular_binding`'s `cop`-label read -- while the brain-foundational LABELS RUNG already exists (pri 108's coarse-role competition with validities from counts, pri 111's one voice organ, pri 117's learned predicate-slot arc feature, pri 106's role margin to consumers): route the three consumers to it and retire the two stand-ins from the live path.

**slug:** `three_default_read_consumers_still_call_the_supervised_arc_labeler_and_the_fitted_parse_confidence_readout_patient_defer_goal_purpose_filter_copular_label_path_route_them_to_the_bf_labels_rung_and_the_competitions_own_margin` -- **opened:** 2026-09-15 by strategy from the E05 audit prompted by the external substrate evaluation (`notes/SUBSTRATE_EVALUATION.md`) and an import probe (`__import__` hook over `SituationReader().read` on `GUM_academic_*` text-only: imported during read = `hdlab.arc_labeler`, `hdlab.parse_confidence`; imported at construction only = `hdlab.pos_tagger`, `hdlab.arc_parser`, `nltk`).

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Relation labels are not a separate classifier run after the parse: the role a dependent bears is decided by the same cue competition that attaches it (Competition Model, Bates & MacWhinney; the labels rung landed as `graded_role_assigner`'s configuration-conditioned contrast, pri 108/111), and the reliability of a decision is the competition's own margin / posterior (predictive-coding precision, Friston), not a logistic readout fitted afterwards on a different parser's features.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL (OWNER 09-08, HARD PASS/FAIL):** a NOT_BF component on the live path is a DEFECT THAT BLOCKS -- fix to brain-foundational or REMOVE; never keep for a metric. `arc_labeler` and `parse_confidence` are registry NOT_BF (`notes/bf_status_registry.jsonl`); `arceager_parser` / `pos_tagger` stay selectable stand-ins for baselines only.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** the labels come from the ONE role competition (`graded_role_assigner`, coarse roles with count-accrued validities; the voice organ `thematic_role_labeler.is_passive_predicate`; the predicate-slot `cop` read from `attachment_arm` / `lexical_categories` pri 110/117). No new labeler.
> **DOWNSTREAM REGRESSION AFTER A BF UPSTREAM IS NOT FAILURE (OWNER 09-12):** if a consumer drops when it reads the competition instead of the perceptron, repair the consumer to read the GRADED signal; never revert to the stand-in.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** (a) Reproduce the probe (a `builtins.__import__` hook around a default read; list every hdlab module first imported DURING `read()` and the call stack that imported it) on 16 modern documents (pri 116's harness) -- publish the table. (b) Consumer 1, the patient defer: replace `parse_confidence.calibrated_patient_confidence` with the role competition's own patient margin / posterior (the AGENT side already uses `cm_margin` raw, :2593-2596 -- do the same for the PATIENT: `graded_role_assigner`'s competition distribution over the patient candidates; report AUC against the gold patient on UD-EWT test vs the fitted readout's AUC; the defer policy stays coverage/rank-based). (c) Consumer 2, the goal purpose filter: the ADVCL-purpose decision ("to VERB" clause attached as purpose) reads the attachment arm's arc + the predicate slot + the SCONJ/PART class (pri 101's line) instead of a perceptron deprel; measure the goal instrument (`test_goal_*` witnesses; the goal rows) before/after. (d) Consumer 3, the copular label path: `copular_binding.extract_entity_states` reads the `cop` relation from pri 110/117's predicate-slot read (`attachment_arm.cop_predicates` / `predicate_sites`) and drops the private PosTagger/ArcParser/ArcLabeler loads; measure the state row and the copular witnesses. (e) After (b)-(d), the probe shows NO NOT_BF module imported during a default read; `arc_labeler` / `parse_confidence` remain importable for baselines only.
> 2. **REUSE.** `hdlab/graded_role_assigner.py` (the competition, `coarse_role_cues`, validities), `hdlab/attachment_arm.py` (`cop_predicates`, `predicate_sites`, `arc_scores`), `hdlab/lexical_categories.py` (the predicate slot), `hdlab/thematic_role_labeler.py` (`is_passive_predicate`), `hdlab/copular_binding.py`, `hdlab/goal_register.py:259-303`, `hdlab/situation_reader.py` (`_patient_arc_confidence`, `_frontend_labeler`, `_read_entity_states`, the `precision_weight_*` flags), the SOLVED.md files of pri 106 (role margin to consumers), 108 (labels rung), 111 (voice organ), 117 (predicate slot as arc feature), and `precision_weight_the_head_driven_readers_on_calibrated_parse_confidence` (Q111 -- the defer landing and its numbers); witnesses `test_labeled_patient_landing.py`, `test_state_qa_consumer_organ.py`, `test_goal_*`, `test_frontend_role_who_did_what.py`.
> 3. **GENERALIZE.** `verification/test_no_not_bf_organ_on_the_default_read.py`: the import probe as a witness (any module tagged NOT_BF in the registry imported during a default read = red), pytest-collectable.
> 4. **WALL -> DEEPER.** If the competition's patient margin has lower AUC than the fitted readout, the loss is a cue the competition lacks (name it, add it as a count-accrued cue) -- never keep the readout; if the goal filter loses without deprels, the missing signal is the purpose construction's own cue (the `to`-infinitival slot), build it in the categories/predicate-slot organ.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep only the defer tau.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Patient row and agent row full size (both arms one process) with the defer on the competition margin; the state row; the goal witnesses; the probe table (zero NOT_BF imports during read); read time per document (three private asset loads gone).
> 7. **ADJACENT.** pri 125 + 122 (RUNNING -- do not touch `referent_per_np.py`, `coref.py`, `read()`/`_cm_agent_candidates`, or the board file; ship your `situation_reader.py` hunks as a diff strategy applies after they land), pri 127 (NLTK), pri 114 (organ-tagged acquisition).
> 8. **COMPLETION BAR.** The probe witness green on 16 documents (no NOT_BF import during a default read); patient / agent / state rows not down full size (or the consumer repair named with items); the goal witnesses not down; the two stand-ins used by no live consumer (grep-level) -- OR a numbered located negative naming the consumer that cannot read the competition and why.

**(PHASE DIAGRAM.)** The defer tau is FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Tokens -> categories -> heads (attachment arm) -> THIS labels rung (the one competition) -> patient defer / goal filter / copular states.

## 1. THE PROBLEM IN PLAIN LANGUAGE
Three parts of the reader still ask an old machine-learned labeller (and a small fitted confidence formula) while reading: the 'how sure am I about who was acted on' step, the 'is this clause a purpose' step, and the 'the sky is blue' step. We already built the brain's way of deciding those labels; these three parts were never switched over. Switch them, and prove by a probe that nothing old is loaded while reading.

## 2. WHY THIS ONE
The owner's hard rule: a non-brain-foundational part on the live path blocks. This is the last place the audit finds one running on a default read (the tagger/parser stand-ins are import-only). It sits at the labels rung, directly below the heads work just landed.

## 3. MEASURED vs INFERRED
MEASURED: the import probe (one document: `arc_labeler`, `parse_confidence` imported during read; `pos_tagger`, `arc_parser`, `nltk` at construction only); the three call sites with line numbers. INFERRED: the competition margin's AUC vs the readout; the goal filter's dependence on deprels.

## 4. ALREADY TRIED / DO NOT REDO
Keeping the readout because its selective accuracy is high (0.8789 -> ~0.966 on the confident two-thirds) -- a fitted stand-in is not an answer; a second labeler.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
(1) `python tools/substrate_map.py`; (2) run the probe yourself; (3) read in full the three call sites, `hdlab/graded_role_assigner.py`, `hdlab/copular_binding.py`, `hdlab/goal_register.py:240-310`, and the SOLVED.md files named in item 2.

## 6. THE BAR (can-fail)
See checklist item 8. Floors: the current consumers as shipped; twin: the competition margin permuted; paired bootstrap over items; the full board in one process with and without.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_labels_rung_to_live_consumers_v1.py` (your cell; `get_output_dir` per Q115), `verification/test_no_not_bf_organ_on_the_default_read.py` (NEW), `notes/problems/<slug>/{SOLVED.md, labels_rung_consumers_patch.diff}` (unified diffs against `hdlab/situation_reader.py`, `hdlab/copular_binding.py`, `hdlab/goal_register.py`; never edit hdlab/ directly).

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. 19c numbers are informational only.
