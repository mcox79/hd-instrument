---
priority: 111
slug: the_passive_cue_fires_on_the_whole_sentence_not_the_clause_33_of_43_licensed_agent_overrides_are_gold_active_so_the_marked_cue_override_breaks_more_than_it_fixes
status: OPEN
review:
review_text:
---

# PROBLEM: the passive-voice cue is read off the WHOLE SENTENCE, not the clause of the predicate being decided -- so 33 of the 43 agent decisions where it licenses the marked-cue override are gold-ACTIVE clauses (conflict validity 0.032, right 1 in 31), and the override that should let a marked cue overturn word order breaks 30 decisions to fix 1.

**slug:** `the_passive_cue_fires_on_the_whole_sentence_not_the_clause_33_of_43_licensed_agent_overrides_are_gold_active_so_the_marked_cue_override_breaks_more_than_it_fixes` -- **opened:** 2026-09-14 by strategy from pri 106's phase-7 section 7.4 (`p7_override_anatomy.json`: passive n=43, fixes 1, breaks 30, neutral 12; `passive_cue_fired_gold_active` 33) and pri 106's next-step 3.

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Name the structure and the computation; replicate the OPERATION, sweep the PARAMETERS (never adopt a number).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- spaCy / any off-the-shelf parser at inference is a DEFECT; the UD treebank is a MEASURING instrument only. Voice is a property of ONE predicate and its auxiliary, perceived in order, at the clause where the decision is made.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** the passive cue is a cue VALUE of the Competition-Model organ (`hdlab/graded_role_assigner.py`; the labels arm) whose detector lives in `hdlab/thematic_role_labeler.py::is_passive_clause`. Fix the detector ONCE and every consumer (the override licence, the BY_AGENT class, the frame-slot decode) reads it; do not add a second voice detector.
> **PLASTIC, NEVER FROZEN:** if the cue becomes graded (P(passive | aux, participle morphology, by-PP)), it is counts with an observe path.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.
> **A rigorous negative is a PASS** only if what failed was the brain's mechanism, faithfully built, with the number.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** The Competition Model's voice cue (Bates & MacWhinney) is evaluated for the clause whose arguments are being assigned: the auxiliary + participle morphology of THAT predicate, in the order heard, optionally confirmed by a following by-PP. The shipped detector scans the whole token sequence for ANY be-aux followed within 3 tokens by a participle and returns one boolean for the sentence: a passive relative clause, a passive coordinate clause, or an adjectival participle ('was tired', 'is interested') licenses the override for EVERY predicate in the sentence. The brain-foundational form is clause-local: the cue for predicate h reads only the auxiliary chain attached to h (the reader's own heads are available: `_cached_parse_heads`) and h's own participle morphology (`hdlab/morphology`), and it is GRADED by the strength of that evidence.
> 2. **REUSE.** `hdlab/thematic_role_labeler.py::is_passive_clause` (+ `_is_participle`, `_BE_AUX`); its four call sites in `hdlab/graded_role_assigner.py` (lines ~659 override licence, ~1584 whole-sentence, ~1765 windowed local, ~1874 BY_AGENT want); pri 106's `agent_override_licensed` and `p7_override_anatomy.json`; the reader's `_cached_parse_heads` / `_cached_tag`; the morphology organ's participle read; UD-EWT's `nsubj:pass` / `aux:pass` as the MEASURING gold.
> 3. **GENERALIZE.** List every consumer of the voice cue (the override licence, the BY_AGENT class in the coarse roles, the frame-slot decode, the thematic labeler's own features) and measure each on the clause-local detector.
> 4. **WALL -> DEEPER.** If clause-local detection still false-fires, the residual is adjectival participles (stative 'was tired') -- a lexical cue (the participle's own verb/adjective category mass from the category organ) enters the graded form; measure it before declaring the cue unreliable.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep only the window and the evidence weights.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Detector P/R against UD-EWT test `nsubj:pass`/`aux:pass` clauses (whole-sentence vs clause-local, per predicate); pri 106's override anatomy re-run (fixes / breaks / neutral on the 1423 agent rows, 62 decisive); the board's who-did-what agent dimension (`experiments/exp_situation_model_qa_modern_v1.py --run`, HDLAB_EXP_NAME set) with the C2 gate; the coarse-role BY_AGENT / PASS_SUBJ accuracy on UD-EWT test 700 under live heads.
> 7. **ADJACENT.** pri 106 (the C2 confidence gate; lands independently); pri 108 (labels rung, PASS_SUBJ class); pri 110 (sole-AUX predicates: the same auxiliary chain read from the other side).
> 8. **COMPLETION BAR.** Clause-local detector: false fires on gold-active clauses down from 33/43 CI-separated with recall on true passives not down; the override anatomy flips to net-positive (fixes > breaks) or the licence is withdrawn with the number; every consumer moved to the one detector; the board's agent dimension not down; twin (random equal-size set of clauses declared passive) at floor -- OR a numbered located negative naming which consumer the clause-local cue helps and which it hurts.

**(PHASE DIAGRAM.)** The detection window, the evidence weights and the override threshold are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Tokens -> categories (AUX / VERB / ADJ mass on the participle) -> heads (which auxiliary belongs to which predicate) -> THIS voice cue -> roles / the agent decision / the board.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When the system decides who did what, it may let a strong signal (a "by" phrase, a passive verb) overrule the usual "the first thing named is the doer". It checks for a passive verb by looking anywhere in the whole sentence, so a passive in one clause makes it overrule word order in another clause where the sentence is perfectly active. Of the 43 times that happened, it was wrong 33 times. The fix is to look only at the clause being decided.

## 2. WHY THIS ONE
A cue-detection defect with a clean population (43 licences, 33 false), located by pri 106 to one function, sitting under the board's agent dimension; three of its four call sites already show the whole-sentence form.

## 3. MEASURED vs INFERRED
MEASURED (pri 106, GUM agent rows, live v4 table): passive licence n=43, fixes 1, breaks 30, neutral 12, conflict validity 0.032; gold-active among them 33; pp_gov 0.579. INFERRED: how much of the 33 is whole-sentence scanning vs adjectival participles -- split it with counts.

## 4. ALREADY TRIED / DO NOT REDO
A per-cue validity in place of the gate (pri 106: 0.8496 / 0.8510 vs the global gate 0.8517 -- a population statistic cannot fix a detector); a perfect label-gate (loses).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read in full: `hdlab/thematic_role_labeler.py` (is_passive_clause, _is_participle); the four call sites in `hdlab/graded_role_assigner.py`; pri 106's SOLVED.md sections 7.4 and 7.5 and `data/exp_role_margin_weighted_consumers_v1/p7_override_anatomy.json`; `verification/test_coarse_role_competition.py`.

## 6. THE BAR (can-fail)
See checklist item 8. Floors: the shipped whole-sentence detector; twin: random clauses declared passive at the same rate. Paired bootstrap over clauses / decisions; the board run with and without.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_passive_cue_clause_local_v1.py` (your cell), `notes/problems/<slug>/{SOLVED.md, passive_cue_patch.diff}` (unified diffs against `hdlab/thematic_role_labeler.py` and the call sites in `hdlab/graded_role_assigner.py`; never edit hdlab/ or tools/ directly), and any NEW asset under `data/hook_state/`.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md` (includes the 0.8148 state figure and the gold-split entity rows). 19c numbers are informational only.
