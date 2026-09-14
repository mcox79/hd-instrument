---
priority: 120
slug: the_non_verbal_predication_constructions_are_named_word_lists_that_overfit_ud_ewt_0_84_in_supply_0_61_out_learn_the_memberships_from_counts_with_an_observe_path
status: OPEN
review:
review_text:
---

# PROBLEM: the predicate-slot event detector landed by pri 113 reaches the non-verbal clauses through fifteen NAMED constructions whose memberships are closed-class word lists (`LOCATIVE_ADV`, `FRONTABLE_PRED`, `WH_PRED`, the copula scan's fallbacks) -- 0.8383 of the 167 non-verbal clauses in supply (UD-EWT test) against 0.6120 of 366 out of supply (GUM / GENTLE), with a CI-separated out-of-supply precision cost (-0.0083) attributed to the lists and not to the governor read; the gap is the measure of how much of the fifteen is English and how much is this treebank, and the brain-foundational form is memberships LEARNED from counts with an observe path on confirmed predications.

**slug:** `the_non_verbal_predication_constructions_are_named_word_lists_that_overfit_ud_ewt_0_84_in_supply_0_61_out_learn_the_memberships_from_counts_with_an_observe_path` -- **opened:** 2026-09-14 by strategy from the pri 113 agent report (`notes/comparisons/pri113_agent/SOLVED_agent.md` sections 3b, 11i, 11j, 12c; alternate path D) and the head-to-head comparison.

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** A construction is a learned form-meaning pairing whose membership is acquired from usage (Goldberg 1995; Tomasello 2003): the comprehender does not carry a list of which adverbs can be predicates, it has counts of which words have filled the predicate slot after a copula. Replicate the OPERATION, sweep the PARAMETERS.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- a hand-named word list is a stand-in; the landed form is counts (word x construction slot) with an online observe path; the UD treebank is a MEASURING instrument (its gold arcs may teach at BUILD time as the environment's feedback, never be read at decision time).
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** the predicate-slot read (`hdlab/attachment_arm.py`: `predicate_sites`, `predicate_site_carriers`, `cop_predicates`, the fifteen constructions landed by pri 113) is the organ; make its memberships learned there. Do not build a second construction inventory.
> **PLASTIC, NEVER FROZEN:** the memberships accrue from confirmed predications (a fired predication whose participants bind) with `observe()`; batch counts only measure the equilibrium.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Replace each named list by a graded membership P(word fills construction slot c | word, category), estimated from counts of the word appearing as the copula's complement / the fronted predicate / the wh-predicate in the acquisition text (the category organ's own count supply, organ-tagged as pri 114 prescribes), smoothed by the category (an unseen adverb inherits the ADV class's rate), and updated online when a fired predication is confirmed by its participants binding. The constructions' STRUCTURE (the copula chain, the fronting, the wh-form) stays as landed; only the memberships become counts.
> 2. **REUSE.** The pri 113 agent's cell `experiments/exp_nonverbal_predication_participants_agent_v1.py` (the participant instrument; `--ablate` per construction; `--participant --pop gum`; the out-of-supply harness 11j) and the owner's `experiments/exp_nonverbal_predication_participants_v1.py` (the same instrument; `--pop gum` cap 1000); `hdlab/attachment_arm.py` (the landed constructions and their lists); `hdlab/lexical_categories.py` (the count supply, the observe path); pri 114 (organ-tagged acquisition, the same build principle one rung up).
> 3. **GENERALIZE.** Every hand-named list on the live read path in `attachment_arm.py` and `situation_reader.py` that decides a construction (grep for frozenset / tuple literals of words used as gates): list them; those that decide a predication are in scope, the rest are reported.
> 4. **WALL -> DEEPER.** If the learned memberships lose in supply against the lists, the lists carried treebank-specific items -- report the items the counts refuse and their gold status; the bar is the OUT-of-supply number, not the in-supply one.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep the smoothing and the confirmation threshold only.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** The participant instrument on UD-EWT test 700 (the 167; floor = the landed lists 0.8383 / the shipped precision) AND on GUM / GENTLE (366 non-verbal clauses; floor 0.6120, precision -0.0083 vs the live floor): recall / precision / F1 with paired CIs on both; a twin with memberships shuffled across words at floor; the board's 7 dimensions full size, both arms in one process; the event recall instrument (pri 110 3b) not down.
> 7. **ADJACENT.** pri 113 (landed), pri 114 (organ-tagged acquisition), pri 117 (the copular subject's attachment), pri 119 (the typed attribute the predication becomes).
> 8. **COMPLETION BAR.** Out-of-supply recall on the 366 up CI-separated from 0.6120 with the precision cost removed (not CI-separated below the live floor), in-supply not down CI-separated, memberships = counts with an observe path (the twin at floor), no hand-named predicate list left on the decision path -- OR a numbered located negative naming the construction whose membership cannot be learned from the available counts and why.

**(PHASE DIAGRAM.)** The smoothing, the category back-off and the confirmation threshold are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Tokens -> categories (the count supply) -> THIS construction membership -> the predicate slot -> events / states / the board.

## 1. THE PROBLEM IN PLAIN LANGUAGE
To find sentences like "the sky is blue" or "here is the list", the system uses fifteen patterns, and inside several of them a hand-written list of which words count ("here", "there", "away"...). On the text it was tuned on it finds 84 in 100; on other text, 61 in 100, and it starts firing wrongly. People do not carry such lists; they have learned, from hearing, which words go in that slot. The fix is to learn the lists from counts and keep learning.

## 2. WHY THIS ONE
The pri 113 agent measured the generalisation gap and attributed it to the lists, not the mechanism, and named this as the first follow-on; the landed detector is the largest new consumer at the top of the chain and it must not carry a treebank's vocabulary.

## 3. MEASURED vs INFERRED
MEASURED (agent, pri 113 11i/11j): 15 constructions ablated (two worth exactly zero); in supply 0.8383 of the 167 (0.8802 with the arc cue); out of supply 0.6120 of 366 (0.6257 with the arc cue), precision -0.0083 CI[-0.0153,-0.0017] vs the live floor, present with the arc cue off and unchanged with it on. INFERRED: the out-of-supply number under learned memberships.

## 4. ALREADY TRIED / DO NOT REDO
Adding constructions by hand from residual attribution (that is how the lists grew; the two zero-worth ones and the one narrowed are in the agent's 3b/11i); the graded arc cue as a substitute (precision-neutral out of supply, adds 5 clauses -- separate lever, landed off).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read in full: the agent's SOLVED_agent.md sections 3b, 11h, 11i, 11j, 12c and section 8 (alternate path D); the owner's SOLVED.md section 2 (the GUM generalisation) and 3; `hdlab/attachment_arm.py` (the landed constructions); `hdlab/lexical_categories.py` (counts, observe); pri 114's PROBLEM.md.

## 6. THE BAR (can-fail)
See checklist item 8. Floors: the landed lists on both populations; twin: memberships shuffled across words; paired bootstrap over clauses; the full board in one process with and without.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_construction_memberships_from_counts_v1.py` (your cell), `notes/problems/<slug>/{SOLVED.md, construction_memberships_patch.diff}` (unified diffs against `hdlab/attachment_arm.py` and, if the counts live there, `hdlab/lexical_categories.py`; never edit hdlab/ or tools/ directly), and the NEW count asset under `data/hook_state/`.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. 19c numbers are informational only.
