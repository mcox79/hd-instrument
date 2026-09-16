---
priority: 135
slug: the_goal_register_answers_why_with_another_agents_purpose_marks_a_goal_satisfied_by_verb_and_agent_alone_and_reads_future_goals_into_time_limited_prediction_make_agent_object_and_time_constraints_binding
status: OPEN
review:
review_text:
---

# PROBLEM: three goal-register queries silently drop a constraint the question states (follow-up review 2026-09-15, each REPRODUCED IN ISOLATION with controlled inputs): (R02) `GoalRegister.why(pred, agent)` filters candidates by the requested agent and then falls back to "filtered candidates OR all candidates", so `why('work', 'alice')` returns Bob's purpose when Alice has none; (R03) `track_status` / `track_status_thwart` mark a goal satisfied when a later event matches the goal's PREDICATE and AGENT only -- the target argument is ignored ("buy bread" is satisfied by "bought milk") and the event must be in a strictly LATER sentence, so a later action in the same sentence never counts; (R04) `_read_prediction` respects the time bound t for the passage but `_goal_lemmas` reads the full-document wants register and the full event list, so a t-limited prediction is conditioned on goals stated in the future -- make the agent, object and time constraints binding: an identity-constrained answer is unavailable (or an explicitly labelled fallback of the SAME agent) rather than silently broadened; satisfaction compares the goal's object/theme (the same entity or a compatible one from the reader's files) and orders events by (sentence, position) rather than sentence alone; every prediction-time read of goals is bounded by t.

**slug:** `the_goal_register_answers_why_with_another_agents_purpose_marks_a_goal_satisfied_by_verb_and_agent_alone_and_reads_future_goals_into_time_limited_prediction_make_agent_object_and_time_constraints_binding` -- **opened:** 2026-09-15 by strategy from `notes/SUBSTRATE_EVALUATION.md` "Focused follow-up: time, goals and belief consistency" (R02, R03, R04; appendix A11 has the exact programs); R01 (state updates at time zero) was fixed by strategy at filing; R05/R06/O01 (belief timing) are inside pri 132.

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** A goal is a state of an agent about an object at a time (the intention-outcome structure of the situation model: Zwaan & Radvansky's goal dimension; Trabasso's causal network where an outcome closes a goal only when it matches the goal's content); a "why" about Alice retrieves Alice's goal or nothing; a goal is closed by an outcome whose CONTENT matches (the object filled the same role), not by any action of the agent; a prediction at time t conditions on what is known at t.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- spaCy, GLUCOSE, MAVEN and ANY off-the-shelf parser/dataset/model are NOT brain-foundational; an external tool AT INFERENCE is a DEFECT THAT BLOCKS.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** the goal register is the one goal organ; object matching reads the reader's entity files (pri 125/131's ids), not strings; time reads the reader's sentence/position clock (pri 132's occurrence index when it lands).
> **WITNESSES PIN CLAIMS, NOT NUMBERS;** the review's isolated fixtures become the witnesses, plus raw-text integration checks.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** (a) R02: remove the broadening fallback; return None (unavailable) or a fallback labelled with its agent; every caller of `why` handles unavailable. (b) R03: satisfaction = predicate match AND agent match AND object/theme match (entity id when both sides carry one; head lemma compatibility otherwise; a goal without an object matches on predicate+agent and SAYS so in its record) AND the outcome AFTER the goal by (sentence, within-sentence position); the thwart path checks thwart before returning satisfied. (c) R04: thread t through `_goal_lemmas` and every goal read in `_read_prediction`; a t-bounded query reads only goals stated at or before t. (d) D01's polarity (pri 132) is respected here when it lands: a negated outcome does not satisfy.
> 2. **REUSE.** `hdlab/goal_register.py` (`why`, `track_status`, `track_status_thwart`, `make_canonicalizer`), `hdlab/situation_reader.py` (`_read_prediction`, `_goal_lemmas`, `_read_goals`), the goal witnesses (`verification/test_goal_*.py`), the review's A11 programs (copy them as fixtures), pri 132's brief.
> 3. **GENERALIZE.** Every identity-, object- or time-constrained query in the reader's public closures audited for the same silent broadening (grep `or candidates`, `or cands`, `if not ... : ... = all`), listed with file:line and fixed or reported.
> 4. **WALL -> DEEPER.** If object matching by entity id loses recall because the files are split, the loss is the clustering's (pri 131) -- name it; never fall back to predicate+agent silently.
> 5. **OPTIMIZE BY EXACT REPLICATION;** nothing to sweep.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** The goal witnesses before/after; the review's fixtures as new witnesses (why-for-the-other-agent unavailable; buy-bread not satisfied by bought-milk; same-sentence later action counts; t-bounded prediction ignores future goals); the product board's goal-related arms; raw-text integration checks on 16 GUM docs (goal outcomes asked through the live reader).
> 7. **ADJACENT.** pri 132 (polarity, occurrence index, belief timing), pri 131 (entity ids), the goal rows on the board.
> 8. **COMPLETION BAR.** The four fixtures green as witnesses; the audit list closed; goal witnesses not down (or the consumer repair named); the board not down -- OR a numbered located negative.

**(PHASE DIAGRAM.)** Nothing to sweep.
**(FULL-STACK UPSTREAM.)** Events (with objects, times, polarity) -> THIS goal register -> why / status / prediction.

## 1. THE PROBLEM IN PLAIN LANGUAGE
Ask "why did Alice do this?" and, if the reader has no reason for Alice, it answers with Bob's reason instead of saying it does not know. Ask whether Alice achieved "buy bread" and it says yes when she bought milk, and misses it when she bought bread later in the same sentence. Ask what happens next as of an early point in the story and it peeks at goals stated later. Make the who, the what and the when binding.

## 2. WHY THIS ONE
Three reproduced wrong answers in one organ, each a dropped constraint; bounded and cheap; the fixtures exist.

## 3. MEASURED vs INFERRED
MEASURED (the review, in isolation with controlled inputs): the three behaviours. INFERRED: their frequency on real text (the raw-text integration checks decide).

## 4. ALREADY TRIED / DO NOT REDO
Silent fallbacks; string matching of objects.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read the review's R02-R04 and appendix A11 programs; `hdlab/goal_register.py` and the reader's prediction/goal reads; the goal witnesses.

## 6. THE BAR (can-fail)
See checklist item 8.

## 7. FILES AND ENTRY POINTS
Write ONLY: `verification/test_goal_register_constraints_are_binding.py` (NEW; the fixtures), `experiments/exp_goal_constraints_v1.py` (raw-text checks; `get_output_dir` per Q115), `notes/problems/<slug>/{SOLVED.md, goal_constraints_patch.diff}` (unified diffs against `hdlab/goal_register.py`, `hdlab/situation_reader.py`; never edit hdlab/ directly).

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. 19c numbers are informational only.
