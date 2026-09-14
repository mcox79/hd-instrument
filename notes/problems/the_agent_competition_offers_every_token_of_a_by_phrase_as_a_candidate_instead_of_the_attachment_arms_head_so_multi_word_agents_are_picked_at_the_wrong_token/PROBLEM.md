---
priority: 115
slug: the_agent_competition_offers_every_token_of_a_by_phrase_as_a_candidate_instead_of_the_attachment_arms_head_so_multi_word_agents_are_picked_at_the_wrong_token
status: OPEN
review:
review_text:
---

# PROBLEM: the who-did-what AGENT competition cannot say which token of a by-phrase NP is its head -- it offers every token as a separate candidate instead of reading the attachment arm's own `flat` / `compound` / `nmod` decisions -- so a passive agent that is a multi-word name ('by a Vikash Chand Abdul Shakur', 'by al-Qaeda') or a head-final NP ('by an extremist form of the Wahhabi school') is picked at the wrong token: 6 of the 16 gold-passive agents on UD-EWT test are lost this way, and a positional head rule is already measured NOT to reach them.

**slug:** `the_agent_competition_offers_every_token_of_a_by_phrase_as_a_candidate_instead_of_the_attachment_arms_head_so_multi_word_agents_are_picked_at_the_wrong_token` -- **opened:** 2026-09-14 by strategy from pri 111's phase-7b section 18.5 (its counts are reproduced below).

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** A noun phrase is one referent with one head; the comprehender binds the AGENT role to the referent, not to a token. Replicate the OPERATION, sweep the PARAMETERS.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- the UD treebank is a MEASURING instrument; its `flat` convention (a name is headed on its first token) is the measuring convention, and the attachment arm already learns it.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** the heads rung (`hdlab/attachment_arm.py`, the Competition-Model organ's attachment arm) already decides `flat` / `compound` / `nmod`; the agent competition (`hdlab/graded_role_assigner.py::hybrid_agent_pick` and the candidate generator that feeds it) is a CONSUMER of those decisions. This is a JOIN, not a new computation: do not build a second NP-head finder and do not add a positional rule (measured, below).
> **PLASTIC, NEVER FROZEN:** counts + observe paths.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** The candidate set of the agent competition should be REFERENTS (NP heads as the attachment arm decides them, with their spans), not tokens; a by-phrase contributes ONE candidate = the head of its NP, carrying the by-PP case cue. Today the by-PP's tokens each enter separately, so the competition's cues (case, order, animacy) are split across tokens and the pick lands on the wrong one. Built form: the candidate generator reads the reader's cached heads (`_cached_parse_heads`, the frontend Parser's in-order tree + posterior) and collapses each by-NP to its head (the token whose head is the preposition's governor path; `flat` / `compound` dependents fold into it), keeping the posterior mass over alternative heads as a GRADED candidate weight rather than a hard choice.
> 2. **REUSE.** pri 111's SOLVED.md section 18.5 and `experiments/exp_passive_cue_clause_local_v1.py` (the 16-item slice, `oracle_by_nphead`, the by-governed oracle at 12/16); `hdlab/graded_role_assigner.py` (`hybrid_agent_pick`, `byhead_agent_cue`, the candidate list built in `situation_reader._cm_agent_for` and in `experiments/exp_board_agent_slot_ud_v1.py`, now a thin call to the organ after pri 111); `hdlab/attachment_arm.py` (`decode`, the `flat` / `compound` conventions in its cue tables); the reader's `_cached_parse_heads`.
> 3. **GENERALIZE.** Every consumer that builds a candidate list from TOKENS rather than referents (the patient competition, the affected-entity resolver's noms, the space register's obl candidates): list them with line numbers and state which suffer the same split.
> 4. **WALL -> DEEPER.** If collapsing to the arm's head loses on common-noun NPs where the arm's head is wrong, the hand-off is the arm's POSTERIOR over heads (a graded candidate weight), not its argmax -- measure the graded form before declaring a trade-off; a head error there is the heads rung's item (report it with counts).
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep only the candidate-weight temperature.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** The 16-item gold-passive slice (`obl:agent`) of the board's who-did-what AGENT gold on UD-EWT test (floor 0/16, organ 10/16 after pri 111, by-governed oracle 12/16, ceiling 16/16); the full 1423-item agent row computed by the board's own function with its floor and CI; the patient row no-regress; the board's 7 dimensions (`experiments/exp_situation_model_qa_modern_v1.py --run`, HDLAB_EXP_NAME set).
> 7. **ADJACENT.** pri 111 (landed: the clause-local voice cue), pri 108 (labels rung), pri 106 (the role decision read by the affected-entity resolver), pri 114 (organ-tagged attachment acquisition).
> 8. **COMPLETION BAR.** Passive-agent slice from 10/16 to >= 14/16 with the full agent row not down (and its CI-separated margin over the floor kept); the candidate generator reads the arm's decisions (one structure) with the graded weight; every token-list consumer classified; twin (a random token of the by-NP) at floor -- OR a numbered located negative naming the heads-rung error class that blocks it, with counts.

**(PHASE DIAGRAM.)** The candidate-weight temperature is FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Tokens -> categories -> heads (the arm's `flat` / `compound` / `nmod` decisions) -> THIS candidate generator -> the agent competition -> the board's agent row.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When a sentence says "was signed by Vikash Chand Abdul Shakur", the system knows it should look inside the "by" phrase for the doer, but it treats each word of the name as a separate contestant and picks the wrong one. The organ that works out how words attach already knows which word heads a name or a phrase; the doer-finder just never asks it. Six of the sixteen such sentences in the test set are lost this way, and a simple "take the first name / last noun" rule has already been shown not to fix them.

## 2. WHY THIS ONE
A located one-structure defect with a counted population (6 of 16), the positional alternative already refuted (no re-run needed), sitting directly under the board's agent row after pri 111 moved it above its floor.

## 3. MEASURED vs INFERRED
MEASURED (pri 111 §18.5, UD-EWT test, board AGENT gold, 16 gold-passive items): positional floor 0/16; organ + voice cue 10/16; by-governed oracle 12/16; the 6 lost = 2 flat names (`Vikash Chand Abdul Shakur`, `al - Qaeda`) + 4 head-final / head-medial common NPs (`form`, `half`, `Kim`, `businessmen`); `oracle_by_nphead` (first PROPN else last noun) = the same 12/16 and -0.0063 on the full 1423 population. Bound: +0.0042 on the full agent row. INFERRED: which other token-list consumers share the split.

## 4. ALREADY TRIED / DO NOT REDO
A positional NP-head rule (first PROPN of the by-NP, else the last noun): 12/16, identical to 'first by-governed token', -0.0063 on the full population (pri 111 §18.5). Do not re-run it.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read in full: pri 111's SOLVED.md §17-18 and its cell; `hdlab/graded_role_assigner.py` (`hybrid_agent_pick` and its candidate handling); `hdlab/situation_reader.py` `_cm_agent_for`; `experiments/exp_board_agent_slot_ud_v1.py`; `hdlab/attachment_arm.py` (`decode`, the `flat` / `compound` cues); `verification/test_byhead_agent_cue_landing.py`, `verification/test_cmrole_agent_*.py`.

## 6. THE BAR (can-fail)
See checklist item 8. Floors: the token-list candidate generator as shipped; twin: a random token of the by-NP as the candidate; paired bootstrap over items; the board run with and without.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_agent_candidates_are_referents_v1.py` (your cell), `notes/problems/<slug>/{SOLVED.md, agent_candidate_referents_patch.diff}` (unified diffs against `hdlab/graded_role_assigner.py` / `hdlab/situation_reader.py` / the board arm; never edit hdlab/ or tools/ directly), and any NEW asset under `data/hook_state/`.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. 19c numbers are informational only.
