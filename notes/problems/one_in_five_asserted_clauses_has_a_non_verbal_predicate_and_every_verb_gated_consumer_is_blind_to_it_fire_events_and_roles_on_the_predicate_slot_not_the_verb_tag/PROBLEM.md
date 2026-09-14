---
priority: 113
slug: one_in_five_asserted_clauses_has_a_non_verbal_predicate_and_every_verb_gated_consumer_is_blind_to_it_fire_events_and_roles_on_the_predicate_slot_not_the_verb_tag
status: OPEN
review:
review_text:
---

# PROBLEM: 167 of 762 subject-bearing clauses on UD-EWT test (21.9%) have a predicate UD puts on an ADJ / NOUN / ADV / PROPN / NUM by design ('the sky is blue', 'she is a doctor', 'he was here') -- the event detector, the role competition's frame / slot / rank / existential cues and the tense reader all gate on `tag == "VERB"`, so they never fire on a fifth of what a text asserts; the copular state reader sees 102 of them and 65 are seen by nobody.

**slug:** `one_in_five_asserted_clauses_has_a_non_verbal_predicate_and_every_verb_gated_consumer_is_blind_to_it_fire_events_and_roles_on_the_predicate_slot_not_the_verb_tag` -- **opened:** 2026-09-14 by strategy from pri 110's phase-7 sections 10e and 10f (the counts below are reproduced from there).

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** A clause predicates something of its subject whether the predicate is a verb, an adjective, a noun or a place; the comprehender builds one event/state for the clause and fills its participants from the clause, not from a tag. Replicate the OPERATION, sweep the PARAMETERS.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- the UD treebank is a MEASURING instrument; its VERB column is not the definition of an event. Never score a predication event on an ADJ as a false positive because UD's VERB column lacks it (pri 110 §10f).
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** pri 110 landed the PREDICATE-SLOT OCCUPANCY read (`hdlab/lexical_categories.py`, HDLAB_LC_PREDICATE_SLOT; graded, off the category posterior) and the attachment arm's `cop_predicates`; the event detector (`situation_reader._tense_agnostic_extract`), the role competition (`hdlab/graded_role_assigner.py` head-category gates at ~653 / 676-679 / 730 / 749 / 761) and the copular state reader are CONSUMERS of that one signal. Do not build a second predicate finder.
> **PLASTIC, NEVER FROZEN:** counts + observe paths.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** One predicate per clause (Spivey-Knowlton 1993), satisfied by whatever element carries the predication: a verb, or a copula + complement (property / class / location / possession -- Pustet 2003, Goldberg 1995 for existential *there*). The brain fires the clause's event/state with the COMPLEMENT as its content and the copula as its tense/aspect carrier. Built form: the event detector fires on P(predicate slot occupied) -- pri 110's graded occupancy -- with the predicate = the verb when the slot holds a verb, else the copula's COMPLEMENT (the arm's `cop_predicates` head) carrying the copula's tense; the role competition's head-category gates read the same occupancy instead of `hc in ("VERB","AUX")`; the copular state reader is reconciled with the event so one clause yields ONE structure (an event whose predicate is a property = a state), not two.
> 2. **REUSE.** pri 110's SOLVED.md §10e / §10f and `experiments/exp_one_convention_two_losses_v1.py` (the 762-clause convention-free population and the per-consumer counts); pri 110's occupancy read and `cop_predicates`; pri 107's rescue (the sole-AUX arm stays OFF, answered with numbers); the copular state reader (`_STATE_GRADED`, `copular_is_a_binding`); the role competition's non-verbal-head branch (~707); the tense reader (`hdlab/temporal_model.py`, counts_penn arm).
> 3. **GENERALIZE.** Every consumer that gates on `tag == "VERB"` or `hc in ("VERB","AUX")` -- list them with line numbers (pri 110 §5b enumerated the first set) and measure each on the 167.
> 4. **WALL -> DEEPER.** If firing on non-verbal predicates costs precision at a consumer, the hand-off is graded (P(occupied) x P(complement is the predicate)) and the consumer weights it; measure the graded form before declaring a trade-off. If the event and the state double-count, that is the ONE-STRUCTURE defect to fix, not a reason to keep the gate.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep the occupancy threshold and the complement-vs-copula predicate choice only.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** THE INSTRUMENT FIRST (pri 110 §10f, 7D): a PARTICIPANT instrument on the 762 subject-bearing clauses -- a fired event/state is correct when it governs the clause's gold core arguments (nsubj / obj / xcomp-or-complement), never asking the tag column what category the predicate is; report precision / recall / F1 there for the event detector (before: 595 of 762 reachable at most), the role competition's cue coverage (which cues fire per clause), and the copular state reader's coverage (102 of 167 -> ?; the 65 seen by nobody -> ?); then the board's 7 dimensions (state, agent, patient especially) with `experiments/exp_situation_model_qa_modern_v1.py --run`, HDLAB_EXP_NAME set; the reader's event recall instrument (pri 110 §3b) must not go down.
> 7. **ADJACENT.** pri 108 (labels rung; the copular subjects), pri 110 (landed; the occupancy read), pri 106 (the role decision read by the affected-entity resolver), pri 112 (the passage register; repeatability).
> 8. **COMPLETION BAR.** The participant instrument built and published (gold-free at decision time; a twin with predicates picked at random at the same rate at floor); the 167 clauses reachable: event/state fired on >= 0.90 of them with participant precision not below the verbal clauses' CI-separated; the role competition's full cue set firing on them with role accuracy on the 167 up CI-separated vs the reduced-cue branch; the 65 seen-by-nobody down to a counted residual with reasons; board not down on any dimension; one structure per clause -- OR a numbered located negative naming the consumer that cannot receive the non-verbal predicate and why.

**(PHASE DIAGRAM.)** The occupancy threshold, the complement choice, and the event/state reconciliation rule are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Tokens -> categories (the occupancy read lives here) -> heads (`cop_predicates`) -> THIS predicate hand-off -> events / roles / states / tense / the board.

## 1. THE PROBLEM IN PLAIN LANGUAGE
One sentence in five says something without a doing-word: "the sky is blue", "she is a doctor", "he was here". The system's event finder and its who-did-what organ only wake up when they see a doing-word, so on those sentences they do nothing; a separate organ that reads "is"-sentences catches about six in ten of them, and the rest are simply never read. The fix is to let those organs fire on "there is a predicate here" (which the system now computes) and take the property or the noun as what is being said.

## 2. WHY THIS ONE
The biggest counted hole at the top of the chain after pri 110: 167 clauses (21.9%) against the 23 tokens pri 110 repaired; three consumers named with line numbers; the instrument that can score it honestly is specified (7D) and not built.

## 3. MEASURED vs INFERRED
MEASURED (pri 110 §10e, UD-EWT test 700, live chain with the slot): 762 subject-bearing clauses; 167 invisible to every VERB gate (19 gold-verbal tag errors + 148 non-verbal by design); event detector misses all 167; the role competition runs its reduced branch on them; copular state reader sees 102; 65 seen by nobody. INFERRED: the board movement (state / agent / patient) once events fire on them.

## 4. ALREADY TRIED / DO NOT REDO
Promoting every sole-AUX token to VERB as a rule (pri 107: refuted against UD's VERB column, which cannot adjudicate its own convention); pri 107 path A (HMM renormalisation on 'the clause has a VERB': UAS -0.0231, refuted by pri 110 with the mechanism -- the event it conditions on is false for copular clauses).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read in full: pri 110's SOLVED.md (§2, §5b, §10e, §10f) and its cell; `hdlab/lexical_categories.py` (the PREDICATE_SLOT read); `hdlab/attachment_arm.py` (`cop_predicates`); `hdlab/situation_reader.py` `_tense_agnostic_extract` and the copular state reader; `hdlab/graded_role_assigner.py` lines ~640-770; `hdlab/temporal_model.py` (tense on a copula).

## 6. THE BAR (can-fail)
See checklist item 8. Floors: the VERB gate as shipped; twin: predicates picked at random at the same rate; paired bootstrap over clauses; the board run with and without.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_nonverbal_predication_participants_v1.py` (your cell: the participant instrument + the consumers' A/B), `notes/problems/<slug>/{SOLVED.md, predicate_slot_consumers_patch.diff}` (unified diffs against the consumers; never edit hdlab/ or tools/ directly), and any NEW asset under `data/hook_state/`.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md` (the 0.8148 state figure; the gold-split entity rows). 19c numbers are informational only.
