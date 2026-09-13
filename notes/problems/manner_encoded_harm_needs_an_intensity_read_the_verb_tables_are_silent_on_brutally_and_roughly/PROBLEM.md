---
priority: 98
slug: manner_encoded_harm_needs_an_intensity_read_the_verb_tables_are_silent_on_brutally_and_roughly
status: OPEN
review:
review_text:
---

# PROBLEM: for verbs like brutalize, manhandle, gore, maltreat, subjugate the harm lives in a MANNER word ("treat brutally", "handle roughly") that no verb table quantifies — every parse-free read of the definition leaks neutral verbs (4-8 leaks, 3-6 wrong signs per 4 recovered) — the reader needs an INTENSITY read: how forceful the manner is, grounded, not looked up

**slug:** `manner_encoded_harm_needs_an_intensity_read_the_verb_tables_are_silent_on_brutally_and_roughly` — **opened:** 2026-09-13 by strategy from the harm/help solver's drilled located negative (owner-DONE pri 14, integrated 11:45: 693 affecting verbs still abstain; the genuine miss is this manner-encoded slice; three parse-free proxies were built and refuted with counts).

> ## SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Name the structure and the computation; replicate the OPERATION, sweep the PARAMETERS (never adopt a number).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** — spaCy / any off-the-shelf parser / treebank-trained model at inference is a DEFECT; the UD treebank is a MEASURING instrument only (its trees are never read while learning).
> **🧩 ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** this is an extension of the ATTACHMENT arm of the Competition-Model organ (`hdlab/attachment_arm.py`; sibling arm `hdlab/graded_role_assigner.coarse_roles`). Do NOT mint a new organ; propose the change as a patch + probe, strategy lands it.
> **PLASTIC, NEVER FROZEN:** knowledge = counts in the asset; strengths = one pure function of counts; an online `observe_*` path must exist for anything you add.
> **🧱 WALL-PUSH PROTOCOL:** before writing wall / ceiling / negative, read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md`. A wall = an upstream trace + a stronger brain build, else a SPECIFIC board question.
> **A rigorous negative is a PASS** only if what failed was the brain's mechanism, faithfully built, with the number.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** How does a reader know "brutalize" harms when its superordinate ("treat") is neutral? By SIMULATING the manner: "brutally/roughly/savagely" carry force and arousal; the brain's outcome valuation (OFC/vmPFC) reads the simulated intensity of the action on the patient (Barsalou grounded simulation; Zwaan; force dynamics: Talmy). Manner adverbs and manner verbs are graded on AROUSAL/DOMINANCE norms and on grounded force features, not only valence. Name the structure and the computation: value = force-intensity(manner) x affectedness(patient) with the sign from the manner's valence.
> 2. **REUSE.** `hdlab/force_dynamics_valence.py` (the arithmetic; `endstate_valence_sign` cascade: result state -> word norm -> superordinate; the manner slice abstains there), `hdlab/affect_lexicon.py` (Warriner valence -- check whether AROUSAL and DOMINANCE columns are present or exportable as a foundation asset), `hdlab/grounded_similarity.py` / the grounded meaning channel (sensorimotor / force features), `hdlab/causation_typing.py` (Wolff/Talmy force typer, dormant), the WordNet gloss of the verb (the manner word is IN the gloss: gore = "wound by piercing"; brutalize = "treat brutally") -- the drilled negative shows the gloss's VALENCE is not the signal; its INTENSITY may be.
> 3. **GENERALIZE.** Manner verbs (brutalize, manhandle, maltreat, mistreat, terrorize), instrument verbs (gore, club, knife), and adverb-modified neutral verbs in text ("treated him brutally", "handled her roughly") -- the same read must fire on the ADVERB in running prose, not only on lexicalised manner verbs.
> 4. **WALL -> DEEPER.** If intensity norms cover the manner words but the read still leaks, split by whether the leak is a neutral verb with high arousal (excite, thrill: positive high-arousal) -- the sign must come from valence and the magnitude from arousal; report the 2x2.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep the intensity threshold as an operating point, never adopt a number.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Populations: the harm/help solver's residual verb list (693 abstaining affecting verbs; the 15 named manner verbs), the Connotation-Frames human gold (Effect(o), `experiments/fetch_connotation_frames_v1.py`) as the independent check, `P_NEUTRAL_BROAD` (n=36) for leaks, the 36-item live modern gold (`experiments/exp_fd_harm_help_live_modern_v1.py`) for no-regress, and a NEW small adverb-in-prose gold you declare (>= 30 sentences: "treated him brutally" vs "treated him kindly").
> 7. **ADJACENT.** The decision feeds `affect_harm_help` and `affected_entity`; report which residual verbs newly decide and their CF agreement; do not edit consumers.
> 8. **COMPLETION BAR.** Recovers the manner slice (>= 8 of the 15 named verbs) at Connotation-Frames precision >= 0.95 with 0 leaks on P_NEUTRAL_BROAD and the live gold held (>= 35/36), the adverb-in-prose gold CI-separated over the current abstaining read, twin (scrambled intensity norms) losing, knowledge as an offline foundation asset + an online observe path -- OR a numbered located negative naming the missing input.

**(PHASE DIAGRAM.)** Intensity threshold, the arousal/valence mixing, the adverb window are FREE TO SWEEP; a wall "at this config" = move the operating point.
**(FULL-STACK UPSTREAM.)** The verb reaches the organ through the reader's events (the category organ must tag it VERB: 'wounded' was mis-tagged ADP until today's reanalysis fix); the patient through the roles rung. If the manner ADVERB is not attached to its verb by the governor, say so with counts (the governor's advmod handling is measurable with `experiments/_diag_decode_incremental.py`).

## 1. THE PROBLEM IN PLAIN LANGUAGE
Some verbs hurt because of HOW the action is done: to brutalize is to treat someone brutally. The reader values an action by the state it leaves a person in, and for these verbs no reference book names that state, so it stays silent -- correctly, because guessing from the definition's words leaks wrong verdicts. People feel the force in "brutally" and "roughly". We want the reader to read that force: a grounded sense of how intense a manner is, with the direction from its goodness or badness.

## 2. WHY THIS ONE
It is the named residual of an integrated solution (helped-or-harmed at 0.93 agreement with human judgements), it recurs in running prose as adverbs ("handled her roughly"), and the drilled negatives prove it cannot be done from verb tables -- it needs the grounded channel, which is the owner-endorsed main event.

## 3. MEASURED vs INFERRED
- **MEASURED (harm/help solver, 2026-09-13):** manner slice abstains (brutalize, manhandle, gore, subjugate, tyrannize, maltreat); gloss strongest-word valence recovers 4 but flips 93 verbs with 8 CF-neutral leaks + 6 wrong signs; adverb-only valence recovers 0; arousal-gated negative recovers 3 with 4 leaks + 3 wrong signs.
- **INFERRED (prove with a number):** intensity (arousal/dominance or grounded force) x valence sign, read on the manner word, recovers the slice at high precision.

## 4. ALREADY TRIED / DO NOT REDO
The three parse-free gloss proxies above, as built. Naive gloss valence. Superordinate inheritance (landed; correctly silent here).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read IN FULL: `hdlab/force_dynamics_valence.py`, `hdlab/affect_lexicon.py`, `notes/problems/the_harm_help_read_needs_the_affective_value_of_the_resulting_state_not_the_verbs_word_valence/SOLVED.md` (the located negative and its drill), `experiments/exp_fd_result_state_hypernym_v1.py`, `notes/BRAIN_MATH_REFERENCE.md` (force-dynamics rows), `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md`.

## 6. THE BAR (can-fail)
See checklist item 8.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_manner_intensity_harm_v1.py` (must use `experiments._seed_checkpoint.get_output_dir`), any offline asset builder under `tools/` (a NEW file), `notes/problems/<slug>/SOLVED.md`, `notes/problems/<slug>/force_dynamics_valence_patch.diff` (do NOT edit hdlab/ directly -- strategy lands it). Commit PATH-LIMITED, never push, never `git add -A`.

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT use spaCy / nltk taggers / any supervised parser / any external LLM at inference. Offline foundation assets (norms, WordNet) are admissible; read them at build time, ship a dict.
