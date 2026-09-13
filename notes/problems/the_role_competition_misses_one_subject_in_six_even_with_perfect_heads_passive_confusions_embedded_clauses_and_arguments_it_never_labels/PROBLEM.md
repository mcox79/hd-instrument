---
priority: 103
slug: the_role_competition_misses_one_subject_in_six_even_with_perfect_heads_passive_confusions_embedded_clauses_and_arguments_it_never_labels
status: OPEN
review:
review_text:
---

# PROBLEM: even when every head is right, the role competition still misses one subject in six -- it calls active subjects PASSIVE (41 cases: "was found", "has been roiled"), calls embedded-clause subjects objects or obliques, labels nothing at all for numeral / quantifier / adjective arguments ("Many", "one", "the poor"), and under the LIVE governor embedded subjects fall to 0.68 -- the labels rung needs voice read from the auxiliary frame, an embedded-clause configuration, and an argument class wider than NOUN/PROPN/PRON

**slug:** `the_role_competition_misses_one_subject_in_six_even_with_perfect_heads_passive_confusions_embedded_clauses_and_arguments_it_never_labels` -- **opened:** 2026-09-13 by strategy from the clause-type diagnostic of the labels rung (`experiments/_diag_roles_by_clause_type.py`, UD-EWT test 700; live table = the confidence-weighted validities or the perceived table, see `notes/INTEGRATION_LEDGER.md`): GOLD heads -- matrix nsubj recall 0.830 (misses: nsubj:pass 25, obj 14, dep 14, <none> 5), embedded nsubj 0.812 (nsubj:pass 16, obj 10, dep 9, obl 8), copular nsubj 0.832 (dep 21, <none> 6), embedded obj 0.877 (<none> 11, nsubj 10), matrix obj 0.825 (dep 12, <none> 11); LIVE heads -- embedded nsubj 0.682 (obl 24, dep 20, <none> 16), matrix nsubj 0.776, matrix obj 0.667. `<none>` = the gold argument's category is not in the labeler's NOMINAL set (NUM/ADJ/DET pronominals), so it is never labelled.

> ## SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Name the structure and the computation; replicate the OPERATION, sweep the PARAMETERS (never adopt a number).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** — spaCy / any off-the-shelf parser / treebank-trained model at inference is a DEFECT; the UD treebank is a MEASURING instrument only (its trees are never read while learning).
> **🧩 ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** this is an extension of the ATTACHMENT arm of the Competition-Model organ (`hdlab/attachment_arm.py`; sibling arm `hdlab/graded_role_assigner.coarse_roles`). Do NOT mint a new organ; propose the change as a patch + probe, strategy lands it.
> **PLASTIC, NEVER FROZEN:** knowledge = counts in the asset; strengths = one pure function of counts; an online `observe_*` path must exist for anything you add.
> **🧱 WALL-PUSH PROTOCOL:** before writing wall / ceiling / negative, read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md`. A wall = an upstream trace + a stronger brain build, else a SPECIFIC board question.
> **A rigorous negative is a PASS** only if what failed was the brain's mechanism, faithfully built, with the number.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Role assignment is cue competition (Bates & MacWhinney; MacWhinney 1987): word order, case, agreement, animacy and VOICE compete, with validities learned from experience and read WITHIN the configuration (head class x order). Three things the brain reads that this rung does not: (a) VOICE from the auxiliary frame ("was found" = passive: be + participle; "has been roiled by" = passive; "was going" = active progressive) -- the morphology/Penn arm already distinguishes participle forms; (b) the EMBEDDED configuration (a subject inside a that-clause / relative / adverbial clause has its own predicate; the matrix verb's frame must not claim it) -- configuration = the clause the nominal belongs to, not the sentence; (c) an ARGUMENT is whatever fills a slot, including quantifier/numeral/adjective heads ("Many want...", "one of them", "the poor") -- the brain labels the filler, not the part of speech. Name the structure and the computation for each.
> 2. **REUSE.** `hdlab/graded_role_assigner.py` (`coarse_role_cues`: the cue set incl. `voice_order`; `coarse_roles`; `NOMINAL`; `ROLE_CLASSES`; the configuration key head-class x order; `observe_role_outcome`), `tools/build_coarse_role_validities.py` (`--perceived --weight`: confidence-weighted accrual; add cues here and rebuild -- the validities are counts), the Penn arm of the category organ (`lexical_categories_counts_penn_v1.json`: VBN/VBG/VBD distinguish participle from finite), `hdlab/attachment_arm.py` (`function_word_arcs`: the AUX frame; the pri 97 patch's finiteness cues -- read, do not edit), `experiments/_diag_roles_by_clause_type.py` (the instrument; extend it with voice and `<none>` splits).
> 3. **GENERALIZE.** Passives with and without by-agents, perfect passives, progressive actives ("was running" is active), reduced relatives ("the flag found in Fallujah"), embedded subjects under ccomp/xcomp/advcl/relcl, quantifier/numeral/adjective arguments, and coordinated subjects.
> 4. **WALL -> DEEPER.** If voice does not move the nsubj:pass confusions, check the gold: UD marks "that was found" as nsubj:pass -- verify the 41 cases against the gold deprel and report how many are annotation noise vs real misses; if embedded subjects do not move, split by whether the governor attached the subject to the right clause at all (the live-heads 0.682 may be a heads problem; the gold-heads 0.812 is the labeler's own share).
> 5. **OPTIMIZE BY EXACT REPLICATION;** cues are count tables; sweep only the shrinkage.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** UD-EWT test 700 under BOTH gold heads (isolates the labeler) and live heads (`_diag_roles_by_clause_type.py`): per clause type nsubj / nsubj:pass / obj recall and the confusion lists are the floors above; the board's who_did_what_patient (0.7944 with the weighted table / 0.7920 live) and who_did_what_agent (0.8271 -- note: this board read does NOT consume the role table; trace what it does consume and say so) via `experiments/exp_situation_model_qa_modern_v1.py --run` (25 min); twin = shuffled cue values.
> 7. **ADJACENT.** Roles feed the affected-entity resolver, the state register and the harm/help reader; report which move; do not edit consumers.
> 8. **COMPLETION BAR.** Under gold heads: nsubj recall up CI-separated in matrix AND embedded clauses with obj not down and the nsubj:pass confusions at least halved (net of verified annotation noise); the `<none>` population labelled with recall >= the NOUN population's; under live heads: embedded nsubj up CI-separated; board patient not down; knowledge as counts with the observe path -- OR a numbered located negative naming the missing input (e.g. the heads rung's clause attachment).

**(PHASE DIAGRAM.)** Shrinkage, the participle window for voice, the clause-boundary criterion are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Voice needs the category organ's AUX/VERB reading of be/have (a known confusion: main-verb be/have tagged AUX, `notes/OVERNIGHT_PLAN_2026-09-12.md` 14:24) and the Penn arm's participle tags; embedded configuration needs the governor's clause attachment (pri 97's patch improves ccomp 0.603 -> 0.690 at the landed cap -- measure with and without it applied inside your cell, never to hdlab/).

## 1. THE PROBLEM IN PLAIN LANGUAGE
Once the reader knows which word each word belongs to, it still has to say who did what. With perfect attachments it still misses about one subject in six: it reads "the flag that was found" as if the flag did the finding, it mixes up subjects inside "that"-clauses with objects, and it never labels "many" or "one" as a doer at all. People read the little verbs ("was", "has been") to tell passive from active, know which clause a word belongs to, and label whatever fills the slot. We want those three readings as learned cues in the same competition.

## 2. WHY THIS ONE
It is the labels rung's own share of the loss (measured with perfect heads), it sits directly under the two board abilities about who did what, and the organ's learning machinery (counts, observe path, confidence-weighted accrual) is already in place -- only cues are missing.

## 3. MEASURED vs INFERRED
- **MEASURED (2026-09-13 17:05, weighted table, gold heads):** matrix nsubj 0.830 (nsubj:pass 25 / obj 14 / dep 14), embedded nsubj 0.812 (nsubj:pass 16 / obj 10 / dep 9 / obl 8), copular nsubj 0.832 (dep 21), `<none>` 5+5+6+11+11 across the five populations; live heads embedded nsubj 0.682.
- **INFERRED (prove with a number):** a voice cue from the AUX frame halves the passive confusions; an embedded-clause configuration lifts embedded nsubj by 5+ points at gold heads; widening the argument class labels the `<none>` population at NOUN-level recall.

## 4. ALREADY TRIED / DO NOT REDO
One-role-per-cue scalar weights and a flat additive table (both REFUTED 2026-09-12; the configuration-conditioned contrast form is required). Slot occupancy at decode (landed selectable, default OFF: it cost the live patient read). The perceived-heads table without confidence weighting (traded subjects for objects; superseded by `--weight`).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read IN FULL: `hdlab/graded_role_assigner.py`, `tools/build_coarse_role_validities.py`, `experiments/_diag_roles_by_clause_type.py`, `notes/problems/attachment_arm_needs_second_order_sibling_factorisation_the_verb_frame_is_occupied_incrementally/SOLVED.md` (pri 93), `notes/BRAIN_MATH_REFERENCE.md` (role-assignment row), `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md`.

## 6. THE BAR (can-fail)
See checklist item 8.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_role_competition_voice_embedding_arguments_v1.py` (must use `experiments._seed_checkpoint.get_output_dir`), `notes/problems/<slug>/SOLVED.md`, `notes/problems/<slug>/graded_role_assigner_patch.diff` (covering hdlab/graded_role_assigner.py and tools/build_coarse_role_validities.py; do NOT edit them directly -- strategy lands it), candidate validity tables under `data/hook_state/` only. Commit PATH-LIMITED, never push, never `git add -A`.

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT use spaCy / nltk / any supervised parser at inference or as a teacher. Do NOT read the treebank's test trees while learning.
