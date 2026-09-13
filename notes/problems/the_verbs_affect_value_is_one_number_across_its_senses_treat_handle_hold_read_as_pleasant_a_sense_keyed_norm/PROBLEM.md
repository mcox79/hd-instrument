---
priority: 100
slug: the_verbs_affect_value_is_one_number_across_its_senses_treat_handle_hold_read_as_pleasant_a_sense_keyed_norm
status: OPEN
review:
review_text:
---

# PROBLEM: the reader's word-level affect value is ONE number per word form -- "treat" is +0.46 because the NOUN sense (a treat) is pleasant, and handle / carry / grab / hold / pull all rate positive -- so neutral events ("the guard treated the prisoner", "he handled the box") are read as HELP; the reader needs an affect value PER SENSE, selected in context

**slug:** `the_verbs_affect_value_is_one_number_across_its_senses_treat_handle_hold_read_as_pleasant_a_sense_keyed_norm` -- **opened:** 2026-09-13 by strategy from the manner-intensity solver's located residual (pri 98, SOLVED 15:12 by an agent session): of its 13 remaining prose errors, 8 are NEUTRAL items where the floor already answers HELP from the sense-conflating word norm; its abstention repair (L2: a verb with an open manner slot does not decide without a manner) was REFUTED by the human gold (Connotation-Frames whole-arm 0.9333 -> 0.9014; live gold 24 -> 23) -- the fix is a SENSE-level norm, not an abstention rule.

> ## SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Name the structure and the computation; replicate the OPERATION, sweep the PARAMETERS (never adopt a number).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** — spaCy / any off-the-shelf parser / treebank-trained model at inference is a DEFECT; the UD treebank is a MEASURING instrument only (its trees are never read while learning).
> **🧩 ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** this is an extension of the ATTACHMENT arm of the Competition-Model organ (`hdlab/attachment_arm.py`; sibling arm `hdlab/graded_role_assigner.coarse_roles`). Do NOT mint a new organ; propose the change as a patch + probe, strategy lands it.
> **PLASTIC, NEVER FROZEN:** knowledge = counts in the asset; strengths = one pure function of counts; an online `observe_*` path must exist for anything you add.
> **🧱 WALL-PUSH PROTOCOL:** before writing wall / ceiling / negative, read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md`. A wall = an upstream trace + a stronger brain build, else a SPECIFIC board question.
> **A rigorous negative is a PASS** only if what failed was the brain's mechanism, faithfully built, with the number.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** How does a reader feel "treat" differently in "a birthday treat", "treated the wound", "treated the prisoner"? The affective value is attached to the MEANING in context, not to the letter string: valence is retrieved from the activated sense (the semantic hub / ATL selects the sense from context; OFC/vmPFC values the selected meaning -- Barsalou situated conceptualisation; Kuperberg's graded meaning activation). A word-form norm (Warriner) is an average over a word's senses weighted by how raters happened to read it -- the brain's value is sense-keyed and context-selected. Name the structure and the computation: value(verb in context) = sum over senses P(sense | context) x value(sense); P(sense | context) from the existing sense-in-context read; value(sense) learned from the sense's own definition, examples and the result states it names.
> 2. **REUSE.** `hdlab/affect_lexicon.py` (Warriner valence/arousal by word form -- the located defect: `treat` +0.46 is the noun), `hdlab/force_dynamics_valence.py` (the cascade: result state -> word norm -> superordinate -> manner -> genus; `context_sense_sign` = the residual-only sense-in-context read, `synset_endstate_sign`, `_gsg`), `tools/build_manner_intensity_asset.py` (the pri 98 builder: parses WordNet definitions with the reader's own glass-box stack at BUILD time -- the same machinery can value each SENSE from its definition/examples), the semantic-graph organ's sense-assignment read (pri-5, live in the grounding loop), VerbNet result states (sense-keyed already). Do NOT mint a new organ: this is a sense-keyed ARM of the affect lexicon consumed by the force-dynamics valuation.
> 3. **GENERALIZE.** Cross-POS conflation (treat / handle / hold / carry / pull / grab / press / beat), cross-sense within the verb (treat = deal with vs give medical care vs regale; beat = strike vs defeat vs mix), and the sense-coverage gap (a sense with no norm word in its definition inherits from its superordinate, as the result-state arm already does).
> 4. **WALL -> DEEPER.** If the sense-keyed value does not move the prose errors, split by whether the sense-in-context read picked the right sense (a selection failure) or the right sense has the wrong value (a valuation failure); report the 2x2 with counts.
> 5. **OPTIMIZE BY EXACT REPLICATION;** the mixing is the expectation over the sense posterior; sweep only the smoothing and the residual-only gate.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Populations: the pri 98 adverb-in-prose gold (n=36; its 8 neutral-cell HELP errors are THE target), `P_NEUTRAL_BROAD` (n=36, 0 leaks must hold), the Connotation-Frames human gold (whole-arm 0.9333 must not fall; CI paired), the 36-item live modern gold (`experiments/exp_fd_harm_help_live_modern_v1.py`, 24/24 decided items held), the real-prose affected-entity probe (standing 0.393) for downstream; a twin = sense values shuffled across senses of the same word. UPSTREAM: the sense-in-context read needs >= 2 content words of context (`_CTX_STOP`); say with counts how often the prose items fall below it.
> 7. **ADJACENT.** The value feeds `affect_harm_help` and `affected_entity`; the same sense-keyed norm could feed the emotion reader (OCC appraisal) -- report, do not edit consumers.
> 8. **COMPLETION BAR.** The 8 neutral-cell HELP errors reduced by at least half with 0 new leaks on P_NEUTRAL_BROAD, CF whole-arm not down (CI), live gold held, twin losing CI-separated, knowledge as counts per sense with an online observe path -- OR a numbered located negative naming the missing input.

**(PHASE DIAGRAM.)** Sense-posterior temperature, residual-only gate, smoothing toward the word-form norm are FREE TO SWEEP; a wall "at this config" = move the operating point.
**(FULL-STACK UPSTREAM.)** The sense selection depends on the category organ (the verb must be tagged VERB: the noun sense of "treat" is exactly the cross-POS leak -- a correct VERB tag already rules it out, so the FIRST lever is a POS-keyed norm, the second the sense-keyed one) and on the governor attaching the context words.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The reader carries one "good or bad" number for each word. For "treat" that number is pleasant, because people who rated the word thought of a treat, the noun. So when the reader meets "the guard treated the prisoner" it leans toward help, and the new manner read cannot undo that because the sentence has no manner word. People do not feel words this way: they feel the meaning that is active. We want the reader to value the sense in play -- at least the right part of speech, and then the right sense.

## 2. WHY THIS ONE
It is the largest remaining error class of a just-solved problem (8 of 13 prose errors), it blocks three separate reads (manner, result-state, sense-in-context), and the "obvious" fix (abstain) was measured and rejected by the human gold -- the right fix is known and bounded.

## 3. MEASURED vs INFERRED
- **MEASURED (pri 98 solver, 2026-09-13):** 8 of 13 prose errors are neutral items answered HELP by the word norm (treat/handle/carry/grab/hold/pull positive in Warriner); L2 abstention: CF 0.9333 -> 0.9014, live gold 24 -> 23 (REFUTED); manner-first ordering: CF 0.9333 -> 0.9111 (REFUTED).
- **INFERRED (prove with a number):** a POS-keyed then sense-keyed value removes at least half of the 8 with no new leaks.

## 4. ALREADY TRIED / DO NOT REDO
L1 manner-first ordering; L2 manner-host abstention (both refuted above). Naive gloss valence (harm/help solver, refuted). Do not add an abstention rule.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read IN FULL: `hdlab/affect_lexicon.py`, `hdlab/force_dynamics_valence.py` (after the pri 98 diff is landed -- check `notes/INTEGRATION_LEDGER.md`), `notes/problems/manner_encoded_harm_needs_an_intensity_read_the_verb_tables_are_silent_on_brutally_and_roughly/SOLVED.md` (sections 5-7, 10), `tools/build_manner_intensity_asset.py`, `notes/BRAIN_MATH_REFERENCE.md` (valuation rows), `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md`.

## 6. THE BAR (can-fail)
See checklist item 8.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_sense_keyed_affect_norm_v1.py` (must use `experiments._seed_checkpoint.get_output_dir`), a NEW offline asset builder under `tools/` and its asset under `data/frontend_assets/` (never overwrite an existing asset), `notes/problems/<slug>/SOLVED.md`, `notes/problems/<slug>/affect_lexicon_patch.diff` (do NOT edit hdlab/ directly -- strategy lands it). Commit PATH-LIMITED, never push, never `git add -A`.

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT use spaCy / nltk taggers / any supervised parser / any external LLM at inference; offline foundation assets (norms, WordNet, VerbNet) are admissible at BUILD time only -- ship a dict.
