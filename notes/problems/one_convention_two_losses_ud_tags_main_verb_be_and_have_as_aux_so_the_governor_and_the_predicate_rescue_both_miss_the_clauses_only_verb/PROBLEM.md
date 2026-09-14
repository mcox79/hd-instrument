---
priority: 110
slug: one_convention_two_losses_ud_tags_main_verb_be_and_have_as_aux_so_the_governor_and_the_predicate_rescue_both_miss_the_clauses_only_verb
status: OPEN
review:
review_text:
---

# PROBLEM: one treebank convention causes two losses on two rungs -- UD tags a clause's main verb *be* / *have* as AUX, so the category organ learns that convention, the governor loses 58% of its tag-to-head loss on exactly those tokens (pri 97's attribution), and the predicate rescue leaves 4.7-38.8% of dropped verbs invisible (pri 107's remit boundary); measured separately they give two half-answers.

**slug:** `one_convention_two_losses_ud_tags_main_verb_be_and_have_as_aux_so_the_governor_and_the_predicate_rescue_both_miss_the_clauses_only_verb` -- **opened:** 2026-09-14 by strategy from pri 107's question 1 and pri 97 / the 09-13 tag-to-head attribution.

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Name the structure and the computation; replicate the OPERATION, sweep the PARAMETERS (never adopt a number).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- the UD treebank is a MEASURING instrument only; its CONVENTIONS are not facts about the brain. A sentence whose only verbal token is a copula or a possessive *have* has a predicate; the brain fires an event for it.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** the category organ (`hdlab/lexical_categories.py`) decides the category; the predicate rescue (`hdlab/predicate_detector.py`, pri 107's arm) and the attachment arm (`hdlab/attachment_arm.py`, the copular predication cue of pri 97) consume it. Fix the hand-off once, measure at both consumers.
> **PLASTIC, NEVER FROZEN:** counts + observe paths.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.
> **A rigorous negative is a PASS** only if what failed was the brain's mechanism, faithfully built, with the number.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Predicate-hood is a clause-level expectation (one predicate per clause; Spivey-Knowlton 1993) satisfied by whatever verbal element the clause has -- a copula predicates a property, *have* predicates possession. UD's AUX tag for those tokens is a labelling convention the category organ has absorbed from its training counts. The brain-foundational move is NOT to relabel the treebank but to make the consumers read the FUNCTION (the clause's predicate slot) rather than the tag: the rescue's sole-AUX arm (pri 107, built, selectable) and the governor's copular predication cue (pri 97) both already approximate it; the question is whether ONE shared computation (a clause's predicate-slot occupancy from the category posterior) serves both, measured together.
> 2. **REUSE.** pri 107's `clause_spans` / AUX_ARM branch and its convention-free instrument (the share of gold-verb sentences that yield NO event; `experiments/exp_predicate_rescue_bf_cue_v1.py --aux`); pri 97's copular predication cue and root competition in `hdlab/attachment_arm.py`; `experiments/_diag_tag_to_head_loss.py` (the 58% attribution); the category organ's posterior (`tag_with_posterior`) and the reader's cached matrix (`_cached_tag_matrix`).
> 3. **GENERALIZE.** Every consumer that gates on `tag == "VERB"`: the event detector, the rescue, the governor's predicate cues, the role competition's frame slots, the copular state reader. List them; measure the shared computation at each.
> 4. **WALL -> DEEPER.** If firing on sole-AUX clauses costs precision at one consumer while helping another, the hand-off is graded (P(predicate slot occupied) not a boolean) and the consumer weights it -- measure the graded form before declaring a trade-off.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep only the predicate-slot expectation's strength.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Populations: UD-EWT test 700 heads (root / nsubj / cop arcs under the live chain), the convention-free blind-clause share through `SituationReader.read()` on UD-EWT + QA-SRL, the board (7 dims) with HDLAB_PREDICATE_RESCUE_AUX on and off, the copular state read (0.7434 on the BF chain).
> 7. **ADJACENT.** pri 108 (labels rung; copular subjects) consumes the same structures; pri 107's path A (a clause-level predicate expectation INSIDE the category organ's decode) is the deeper form of this brief -- if it is buildable, it subsumes the arms at both consumers.
> 8. **COMPLETION BAR.** The two consumers measured TOGETHER under one switch: governor root / cop arcs up CI-separated on the sole-AUX clauses (the 58% tag-to-head class), blind-clause share down CI-separated through the reader, board not down on any dimension, twin at floor; the shared computation landed as ONE organ path with an observe route -- OR a numbered located negative naming which consumer the convention-free predicate helps and which it hurts, with the graded form measured.

**(PHASE DIAGRAM.)** The predicate-slot expectation's strength and the rescue budget are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Tokens -> categories (the convention lives in the counts) -> the predicate slot -> heads / events / roles / states.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The grammar books the system learned from call "is" and "has" helper words even when they are the only verb in the sentence. The system learned that, so two different organs now skip such sentences: the one that attaches words to their heads loses more than half of its tag-related mistakes there, and the one that recovers missed verbs cannot see them at all. Fixing the two separately gives two half-answers; the fix is one: recognise that a sentence whose only verb-like word is "is" or "has" still has a predicate, and let both organs read that.

## 2. WHY THIS ONE
Two measured losses, one cause, top of the chain; pri 107 built half the fix (selectable, default off pending exactly this joint measurement).

## 3. MEASURED vs INFERRED
MEASURED: 58% of the tag-to-head loss = VERB-as-AUX (09-13 attribution); 4.7-38.8% of dropped verbs AUX-tagged (pri 107); the sole-AUX arm: blind clauses 33 -> 18 of 1240, event recall +0.0096 CI-sep, +0.06 false events/sent; refuted as a RULE against UD's own VERB column (precision 0.02-0.12 there, by construction). INFERRED: the joint board effect.

## 4. ALREADY TRIED / DO NOT REDO
Firing on every sole-AUX token as a hard rule scored against UD's VERB column (the column cannot adjudicate its own convention; use the convention-free instrument).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read in full: pri 107's SOLVED.md (sections 4b and 7A) and `hdlab/predicate_detector.py` (AUX_ARM, clause_spans); pri 97's SOLVED.md (copular predication cue, root competition) and the relevant parts of `hdlab/attachment_arm.py`; `experiments/_diag_tag_to_head_loss.py`; `hdlab/lexical_categories.py` (posterior).

## 6. THE BAR (can-fail)
See checklist item 8. Floors: the arm OFF (today's default) at each consumer; twin: a random equal-size set of AUX tokens promoted; paired bootstrap over sentences; the board run with the switch on and off.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_one_convention_two_losses_v1.py` (your cell), `notes/problems/<slug>/{SOLVED.md, predicate_slot_patch.diff}` (unified diffs against the consumers you change; never edit hdlab/ or tools/ directly), and any NEW asset under `data/hook_state/`.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: the memory file `reference_retired_claims_never_requote.md` (includes the 0.8148 state figure). 19c numbers are informational only.
