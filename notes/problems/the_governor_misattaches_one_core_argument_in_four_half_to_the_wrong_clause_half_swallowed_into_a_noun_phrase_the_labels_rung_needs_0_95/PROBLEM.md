---
priority: 105
slug: the_governor_misattaches_one_core_argument_in_four_half_to_the_wrong_clause_half_swallowed_into_a_noun_phrase_the_labels_rung_needs_0_95
status: OPEN
review:
review_text:
---

# PROBLEM: the governor attaches only three core arguments in four to their predicate (874 of 1,160 on UD-EWT test 700): 143 land in the WRONG CLAUSE (105 under another predicate, 38 flung to the root, 56 of them "the next verb to the right") and 119 are CONSTITUENCY errors (101 swallowed into a neighbouring noun phrase, 18 hung under a function word) -- the labels rung's proven win (all core arguments 0.866 -> 0.920 under perfect heads) shows live only when core-argument arcs reach about 0.95

**slug:** `the_governor_misattaches_one_core_argument_in_four_half_to_the_wrong_clause_half_swallowed_into_a_noun_phrase_the_labels_rung_needs_0_95` -- **opened:** 2026-09-13 by strategy from pri 103's arc-by-arc decomposition (closed 20:10) and its head-repair curve (the labels win becomes CI-separated at ~0.95 core-arc accuracy; at 0.897 it is +0.012 with the CI touching zero); the pri 97 patch (applied 19:40) lifts root and copular arcs but not this population (+0.011 UAS, a quarter of one step on that curve).

> ## SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Name the structure and the computation; replicate the OPERATION, sweep the PARAMETERS (never adopt a number).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** — spaCy / any off-the-shelf parser / treebank-trained model at inference is a DEFECT; the UD treebank is a MEASURING instrument only (its trees are never read while learning).
> **🧩 ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** this is an extension of the ATTACHMENT arm of the Competition-Model organ (`hdlab/attachment_arm.py`; sibling arm `hdlab/graded_role_assigner.coarse_roles`). Do NOT mint a new organ; propose the change as a patch + probe, strategy lands it.
> **PLASTIC, NEVER FROZEN:** knowledge = counts in the asset; strengths = one pure function of counts; an online `observe_*` path must exist for anything you add.
> **🧱 WALL-PUSH PROTOCOL:** before writing wall / ceiling / negative, read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md`. A wall = an upstream trace + a stronger brain build, else a SPECIFIC board question.
> **A rigorous negative is a PASS** only if what failed was the brain's mechanism, faithfully built, with the number.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Two distinct brain computations are failing. (a) CLAUSE MEMBERSHIP: an argument belongs to the predicate whose clause it is in; the reader tracks open clauses incrementally (a subordinator or a complementiser OPENS one, a finite verb PROJECTS one, punctuation/coordination CLOSES one) and attaches an argument to the clause's own predicate, not to a later verb with a stronger lexical pull -- in cue-competition terms the clause boundary is a cue with very high validity that the arm lacks as a constraint (Frazier & Fodor's sausage machine; Gibson's locality with clause-bounded integration). (b) CONSTITUENCY: a noun phrase is a unit whose head is its rightmost noun (the Right-hand Head rule; Williams 1981) with a determiner projecting the phrase (DP hypothesis); an argument noun cannot be "absorbed" into a neighbouring NP when a determiner or a case cue marks it as its own phrase -- `np_head_reduce` (landed) already implements the rule; the governor does not use it as a constraint before attaching. Name both computations and build each as a CUE with learned validity inside the attachment arm (not a rule layer).
> 2. **REUSE.** `hdlab/attachment_arm.py` (cues; `function_word_arcs`; the pri 97 root/predication cues, `hold_expectation` with subordinator-pending context, `incremental_tree` with clause-level wrap-up -- the clause machinery exists for WRAP-UP but not as an attachment constraint; `np_head_reduce`; `arc_scores_graded`), `tools/build_attachment_validities.py` (validities are counts; add cue values and rebuild), pri 103's instrument: `experiments/exp_role_competition_voice_embedding_arguments_v1.py` (`head_repair_curve`, the per-arc decomposition code) and `experiments/_diag_roles_by_clause_type.py`, pri 97's `experiments/exp_attachment_main_assertion_v1.py` (live-chain arm, both decodes).
> 3. **GENERALIZE.** Subjects and objects of embedded clauses (ccomp/xcomp/advcl/relcl), arguments preceding a later verb, NP-internal nouns with determiners/possessives, coordinated arguments, fragments.
> 4. **WALL -> DEEPER.** If the clause cue does not move the 143, split by whether the clause opener was TAGGED (SCONJ recall 0.73 -- pri 101's territory) vs present-and-tagged; if constituency does not move the 119, split by determiner presence vs bare nouns (the latter may be a genuine compound).
> 5. **OPTIMIZE BY EXACT REPLICATION;** cue validities learned from the teacher posterior like every other cue; sweep smoothing, the clause-boundary window and the beam only.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** UD-EWT test 700, both decodes, gold categories AND the live chain (organ tags): core-argument arc accuracy (the 0.753 floor with the pri 97 patch applied; target 0.95 is the requirement, not the bar), the per-class breakdown (wrong clause / constituency / wrong predicate), UAS and root not down, the labels rung measured through (`_diag_roles_by_clause_type.py` live-heads block: matrix nsubj 0.850, embedded 0.721 with the weighted table), twin = shuffled cue values; the board's patient and agent dimensions as no-regress (one board run allowed).
> 7. **ADJACENT.** Every consumer of heads; the labels rung's v3 cue set (landed) gains automatically as heads improve -- report the live-heads labels numbers with your change.
> 8. **COMPLETION BAR.** Core-argument arc accuracy up CI-separated under both decodes with the wrong-clause and constituency classes each down by a third or more, UAS/root not down, the labels rung's live matrix+embedded subject recall up CI-separated as a consequence, twin at floor, knowledge as counts with the observe path -- OR a numbered located negative naming the missing input (e.g. the subordinator tag, pri 101).

**(PHASE DIAGRAM.)** Clause window, beam, cue smoothing are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Clause openers depend on the SCONJ tag (0.73; pri 101); determiners are tagged well (DET 0.87+). Apply the pri 97 patch state as your baseline (it is in the working tree); say with counts what each upstream tag error costs your cues.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The governor puts one core argument in four under the wrong word: half the time under a verb in a different clause (often the next verb along), half the time swallowed into a neighbouring noun phrase. People know which clause they are in and know a noun phrase is a unit with its head at the right. The role organ already reads roles almost perfectly when the attachments are right; it needs the governor to reach about 95 in 100 on these arcs for that to show.

## 2. WHY THIS ONE
It is the quantified requirement handed up by the labels rung (a proven 0.866 -> 0.920 win that the live governor erases), and both failure modes are named with counts and with their brain computations.

## 3. MEASURED vs INFERRED
- **MEASURED (pri 103, 2026-09-13):** 286/1160 core arguments mis-attached: wrong clause 143 (105 under another predicate, 38 root; 56 = next verb right), constituency 119 (101 NP-absorbed, 18 under a function word), wrong predicate token 24; head-repair curve: +0.012 at 0.897, CI-separated at ~0.95.
- **INFERRED (prove with a number):** a clause-membership cue and a constituency cue in the attachment competition lift core-arc accuracy by 5+ points and make the labels win visible live.

## 4. ALREADY TRIED / DO NOT REDO
Root/predication cues, copular detector locality, finiteness hold, whole-grid graded read (pri 97, applied); slot occupancy at decode (refuted for this purpose); the labels rung's own cues cannot fix a wrong head (pri 103, 5 levers rejected).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read IN FULL: `hdlab/attachment_arm.py` (working tree), `tools/build_attachment_validities.py`, `notes/problems/the_role_competition_misses_one_subject_in_six_even_with_perfect_heads_passive_confusions_embedded_clauses_and_arguments_it_never_labels/SOLVED.md` (sections 10-17: the decomposition and the head-repair curve), `notes/problems/the_main_assertion_is_a_scorer_deficit_the_governor_rates_non_verbal_predicates_and_subordinate_first_clauses_as_non_roots/SOLVED.md` (sections 6b, 9), `notes/BRAIN_MATH_REFERENCE.md` (attachment rows), `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md`.

## 6. THE BAR (can-fail)
See checklist item 8.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_attachment_clause_and_constituency_v1.py` (must use `experiments._seed_checkpoint.get_output_dir`), `notes/problems/<slug>/SOLVED.md`, `notes/problems/<slug>/attachment_arm_clause_patch.diff` (do NOT edit hdlab/ or tools/ directly -- strategy lands it), candidate assets under `data/hook_state/` only. Commit PATH-LIMITED, never push, never `git add -A`.

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT use spaCy / nltk / any supervised parser at inference or as a teacher. Do NOT read the treebank's trees while learning.
