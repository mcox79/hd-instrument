---
priority: 117
slug: the_heads_rung_attaches_the_subject_of_a_non_verbal_predicate_at_0_54_against_0_85_for_verbal_ones_land_the_predicate_slot_as_a_graded_online_learned_arc_feature
status: OPEN
review:
review_text:
---

# PROBLEM: the attachment arm attaches the SUBJECT of a non-verbal predicate ('the sky is blue', 'she is a doctor', 'is that a money maker?') at 0.5385 against 0.85 for verbal predicates -- the single largest upstream loss under pri 113's participant instrument (a perfect parse gives recall 1.0 there); the owner's pri 113 run PROTOTYPED the repair as a predicate-slot-biased GRADED arc feature with a held/reshape decode (0.5385 -> 0.6509, above the MAP ceiling; propagating to the event stream 0.6048 -> 0.7186 and to entity binding 0.71 -> 0.89) and showed with a gold-POS test that the loss is NOT tagging; it must land as an ONLINE-LEARNED validity, never a frozen bias.

**slug:** `the_heads_rung_attaches_the_subject_of_a_non_verbal_predicate_at_0_54_against_0_85_for_verbal_ones_land_the_predicate_slot_as_a_graded_online_learned_arc_feature` -- **opened:** 2026-09-14 by strategy from the owner's pri 113 SOLVED.md (sections 4, 18, 20-22, 26-29; next step 1) and the head-to-head comparison (`notes/comparisons/pri113_head_to_head_2026-09-14.md`).

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** The comprehender expects one predicate per clause and attaches the subject to whatever fills the predicate slot; a copula opens the expectation and the complement fills it. Replicate the OPERATION, sweep the PARAMETERS.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- the attachment arm's cue validities are counts; the new cue is a graded value learned online (Rescorla-Wagner / the Competition Model's cue-validity accrual), NEVER a hand-set bias; the UD treebank is the MEASURING instrument only.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** the attachment arm (`hdlab/attachment_arm.py`; the Competition-Model organ's heads arm) already computes the predicate-slot occupancy (pri 110, `revise_for_predicate_slot`, `cop_predicates`) and the copular predication cue (pri 97); this brief adds the occupancy as an ARC FEATURE with a learned validity and the decode change, in that organ. Do not build a second parser and do not edit the decode's punctuation/root conventions.
> **PLASTIC, NEVER FROZEN (owner directive, restated in the owner's pri 113 section 21):** the validity accrues from confirmed attachments with an observe path; batch fits only measure the equilibrium.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** The Competition Model attaches an argument to the head whose cues win; for a copular clause the winning head of the subject is the COMPLEMENT (UD's `cop` convention: the copula depends on the complement), and today's cue set lets the copula or a neighbouring verb win. The owner's prototype: (a) a graded arc feature = the predicate-slot occupancy of the candidate head (P(this token fills the clause's predicate slot), from pri 110's read) entering the arc score with its own validity; (b) a HELD / RESHAPE decode: the subject arc is held until the predicate slot settles, then the tree is reshaped so the subject attaches to the slot filler (0.5385 -> 0.6509 on non-verbal subjects, above the MAP ceiling 0.65; verbal subjects flat). Land (a) with an online-learned validity and (b) as the in-order decode's treatment of a clause whose predicate arrives late.
> 2. **REUSE.** The owner's `experiments/exp_nonverbal_predication_participants_v1.py` (`--heads-fix`, `--reshape`, `--held`, the gold-POS control that rules out tagging, the propagation arms: event stream 0.6048 -> 0.7186, entity binding 0.71 -> 0.89); `hdlab/attachment_arm.py` (`arc_scores_graded`, `decode`, `cop_predicates`, `revise_for_predicate_slot`, `observe`); `tools/build_attachment_validities.py` (the validity table; pri 114's organ-tagged acquisition is the same rebuild); pri 108's inverted-copular lead; pri 115 (the by-NP head) and pri 116 (case) as adjacent heads-rung items.
> 3. **GENERALIZE.** Every consumer that reads the subject arc of a copular clause (the event detector's participants, the copular state reader, the role competition's subject cue, the entity layer's referent per NP): list them and measure each on the 167 with the repaired heads.
> 4. **WALL -> DEEPER.** The owner located three residual walls: (A) premature commitment (the subject attaches before the predicate slot is known -- the held decode is the repair; if it still loses, the decode's lookahead is the parameter to sweep, not a ceiling); (B) detection coverage of inverted / clausal predicates (the scan, not the scorer); (C) the copular-subject validity is UNDER-LEARNED in the current table (the owner's section 27) -- rebuild it (pri 114's rebuild with organ tags covers this) before declaring a ceiling.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep the feature's validity learning rate and the held-decode lookahead only.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Non-verbal-subject attachment on UD-EWT test 700 (0.5385 floor; owner's prototype 0.6509; verbal subjects 0.85 must not fall), UAS / LAS per relation under the live chain (cop / nsubj / root not down CI-separated); the participant instrument's recall on the 167 (pri 113: perfect heads give 1.0; the merged event detector's 0.74-0.88 should rise); GUM / GENTLE out of supply; the board's 7 dimensions (`experiments/exp_situation_model_qa_modern_v1.py --run`, HDLAB_EXP_NAME set), full size, both arms in one process (a capped board's zeros are underpowered).
> 7. **ADJACENT.** pri 113 (landing the event detector on the predicate slot; the typed-STATE register), pri 114 (organ-tagged acquisition: the validity rebuild), pri 108 (inverted copular), pri 115, pri 116.
> 8. **COMPLETION BAR.** Non-verbal-subject attachment up CI-separated from 0.5385 toward the prototype's 0.6509 or beyond, verbal not down, with the feature's validity LEARNED (counts + observe path; a twin with the validity permuted at floor); the held/reshape decode landed in the in-order arm; the participant instrument's recall on the 167 up; board not down full-size -- OR a numbered located negative naming the wall (A / B / C above) with its count.

**(PHASE DIAGRAM.)** The learning rate, the held-decode lookahead and the feature's prior are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Tokens -> categories (the predicate-slot read) -> THIS heads rung -> events / states / roles / entities / the board.

## 1. THE PROBLEM IN PLAIN LANGUAGE
In "the sky is blue" the system has to work out that "the sky" belongs with "blue". It gets that right about half the time, against 85 in 100 for ordinary verbs, because it decides where "the sky" attaches before it has seen "blue". The owner showed that letting the decision wait for the predicate, and telling the attacher how likely each word is to be the clause's predicate, lifts it to 65 in 100 and the gain flows through to events and to which thing a property belongs to. It has to be learned from experience, not set by hand.

## 2. WHY THIS ONE
The largest upstream loss under pri 113's instrument (a perfect parse gives recall 1.0), located to one rung, prototyped by the owner with the number and the propagation measured, and the landing form (online-learned) stated.

## 3. MEASURED vs INFERRED
MEASURED (owner, pri 113, UD-EWT test 700): non-verbal subject attachment 0.5385 -> 0.6509 with the graded feature + held/reshape decode; event stream 0.6048 -> 0.7186; entity binding 0.71 -> 0.89; verbal flat; the gold-POS test rules out tagging as the cause; the copular-subject validity under-learned (section 27). INFERRED: the board movement once the merged pri 113 event detector reads the repaired heads.

## 4. ALREADY TRIED / DO NOT REDO
A frozen bias on the subject arc (the owner's prototype form is a heuristic that LOCATES the signal -- it must not land as is; section 17); agreement and discourse-givenness cues for the inverse cases (prototyped and refuted, owner's section 13); a positional NP-head rule (pri 115).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read in full: the owner's pri 113 SOLVED.md sections 4, 13, 17, 18, 20, 21, 22, 26, 27, 28, 29 and its cell's `--heads-fix` / `--reshape` arms; `hdlab/attachment_arm.py` (arc_scores_graded, decode, observe, cop_predicates, revise_for_predicate_slot); `tools/build_attachment_validities.py`; `verification/test_attachment_arm*.py`; `notes/comparisons/pri113_head_to_head_2026-09-14.md`.

## 6. THE BAR (can-fail)
See checklist item 8. Floors: the live arm; twin: the feature's validity permuted; paired bootstrap over sentences; the full board in one process with and without.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_copular_subject_attachment_learned_v1.py` (your cell), `notes/problems/<slug>/{SOLVED.md, copular_subject_attachment_patch.diff}` (unified diffs against `hdlab/attachment_arm.py` and `tools/build_attachment_validities.py`; never edit hdlab/ or tools/ directly), and the NEW asset under `data/hook_state/` (strategy swaps it live).

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. 19c numbers are informational only.
