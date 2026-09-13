---
priority: 102
slug: cue_validities_are_a_lifetime_statistic_learn_the_governors_root_validities_online_from_decoded_outcomes_with_a_drift_guard
status: OPEN
review:
review_text:
---

# PROBLEM: the governor's cue validities are counted once from an offline acquisition teacher and frozen into an asset; the brain's validity is a LIFETIME statistic updated by every comprehension outcome -- the online path exists (`observe_arc_outcome` accrues and recomputes) but nothing drives it, because pure self-teaching was measured to DRIFT; the missing piece is the drift guard

**slug:** `cue_validities_are_a_lifetime_statistic_learn_the_governors_root_validities_online_from_decoded_outcomes_with_a_drift_guard` -- **opened:** 2026-09-13 by strategy from pri 97's alternate path B (SOLVED by an agent session 17:10) and the standing rule that batch fits only MEASURE the equilibrium (`notes/BRAIN_MATH_REFERENCE.md`; memory: organs are plastic, never frozen).

> ## SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Name the structure and the computation; replicate the OPERATION, sweep the PARAMETERS (never adopt a number).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** — spaCy / any off-the-shelf parser / treebank-trained model at inference is a DEFECT; the UD treebank is a MEASURING instrument only (its trees are never read while learning).
> **🧩 ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** this is an extension of the ATTACHMENT arm of the Competition-Model organ (`hdlab/attachment_arm.py`; sibling arm `hdlab/graded_role_assigner.coarse_roles`). Do NOT mint a new organ; propose the change as a patch + probe, strategy lands it.
> **PLASTIC, NEVER FROZEN:** knowledge = counts in the asset; strengths = one pure function of counts; an online `observe_*` path must exist for anything you add.
> **🧱 WALL-PUSH PROTOCOL:** before writing wall / ceiling / negative, read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md`. A wall = an upstream trace + a stronger brain build, else a SPECIFIC board question.
> **A rigorous negative is a PASS** only if what failed was the brain's mechanism, faithfully built, with the number.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Cue validity in the Competition Model (Bates & MacWhinney) is availability x reliability over the reader's whole experience, updated as each sentence is understood -- not a batch fit. The update is a stochastic approximation (Robbins-Monro) on the same count-based log-odds contrast the organ already computes; the brain additionally GATES what teaches: confident, confirmed outcomes teach more than guesses (reliability-weighted learning; dopaminergic prediction-error gating of plasticity). Name the structure and the computation: validity_t+1 = validity_t + eta * w_t * (outcome_t - prediction_t), with w_t the outcome's confidence (the governor's own posterior mass, agreement of the in-order decode with the search, clause completeness) and an anchoring term toward the acquisition equilibrium.
> 2. **REUSE.** `hdlab/attachment_arm.py` (`observe_arc_outcome` -- verified to accrue the ROOT cue cells and recompute strengths; `strengths_from_arc_counts`; `head_posterior` / the in-order beam posterior as confidence; the recorded REFUTATION: "pure self-posterior drifts", which is why the teacher anchors each round at alpha 0.8), `tools/build_attachment_validities.py` (the offline equilibrium; the confidence-weighting pattern `--weight` in `tools/build_coarse_role_validities.py` is the same idea at the roles rung), `hdlab/graded_role_assigner.observe_role_outcome` (the roles rung's online path, same shape).
> 3. **GENERALIZE.** The root cues (pri 97), the attachment cues, the role validities -- one mechanism with one guard; held-out text the asset never saw (a different register) is where online learning should show: measure adaptation, not only no-drift.
> 4. **WALL -> DEEPER.** If every guard either drifts or freezes, split by WHICH cue cells drift (closed-class frames vs open-class lexical cues) -- the brain's answer is a different learning rate per cue type (closed-class cues consolidate early and change slowly).
> 5. **OPTIMIZE BY EXACT REPLICATION;** eta, the anchoring weight and the confidence gate are SWEPT operating points; the drift experiment is the deliverable.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** The drift experiment: read UD-EWT train (or 60k simplewiki lines via the frontend) with the online update ON, measure UAS / root on UD-EWT test 700 at checkpoints (0, 1k, 5k, 12k sentences) under both decodes; floor = frozen asset (in-order UAS 0.6239 / root 0.7771 with the pri 97 patch, or the live numbers at the time), twin = online updates with shuffled outcomes; ADAPTATION test: a held-out register (GUM or a different genre) before vs after reading 2k of its sentences. Knowledge stays counts; the guard is a count-level rule, not a frozen number.
> 7. **ADJACENT.** Every consumer of the heads rung; the role validities (same mechanism). Report, do not edit consumers.
> 8. **COMPLETION BAR.** An online path that does NOT drift over 12k sentences (UAS/root within CI of the frozen asset or above), that ADAPTS on a held-out register CI-separated over the frozen asset, with twin at or below the floor and every number a count -- OR a numbered located negative naming why self-teaching cannot be guarded at this rung (with the drift curve).

**(PHASE DIAGRAM.)** eta, anchoring, gate threshold, per-cue-type rates are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** The outcomes that teach are only as good as the category organ's tags and the decode's commitment; gate on both.

## 1. THE PROBLEM IN PLAIN LANGUAGE
Today the governor learns how much to trust each cue once, from a teacher, and then never changes its mind. People keep adjusting: every sentence understood nudges the trust a little, and confident understandings nudge more than guesses. We tried letting the reader teach itself and it drifted; the fix people have is to weight lessons by confidence and to keep an anchor. We want that guard, measured.

## 2. WHY THIS ONE
It is the standing "plastic, never frozen" rule applied to the rung that matters most, the machinery already exists and is verified, and the only missing piece is a research-grade guard -- the pri 97 session named it as more brain-foundational than anything it landed.

## 3. MEASURED vs INFERRED
- **MEASURED:** `observe_arc_outcome` accrues root cells and recomputes strengths (pri 97 self-test); pure self-posterior teaching drifts (recorded refutation; anchoring alpha 0.8 in the offline build); confidence-weighted perception repaired the roles table's subject recall at zero board cost (2026-09-13 17:05).
- **INFERRED (prove with a number):** confidence-gated + anchored online updates neither drift nor freeze, and adapt to a new register.

## 4. ALREADY TRIED / DO NOT REDO
Unguarded self-posterior teaching (REFUTED: drift). Do not re-run it without a guard.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read IN FULL: `hdlab/attachment_arm.py` (cues, teacher, observe path), `tools/build_attachment_validities.py`, `tools/build_coarse_role_validities.py` (`--weight`), `notes/problems/the_main_assertion_is_a_scorer_deficit_the_governor_rates_non_verbal_predicates_and_subordinate_first_clauses_as_non_roots/SOLVED.md` (section 9 path B), `notes/BRAIN_MATH_REFERENCE.md` (attachment rows), `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md`.

## 6. THE BAR (can-fail)
See checklist item 8.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_attachment_online_validities_drift_v1.py` (must use `experiments._seed_checkpoint.get_output_dir`), `notes/problems/<slug>/SOLVED.md`, `notes/problems/<slug>/attachment_arm_patch.diff` (do NOT edit hdlab/ or tools/ directly -- strategy lands it), candidate assets under `data/hook_state/` only. Commit PATH-LIMITED, never push, never `git add -A`.

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT use spaCy / nltk / any supervised parser at inference or as a teacher. Do NOT read the treebank's test trees while learning.
