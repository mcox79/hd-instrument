---
priority: 119
slug: a_non_verbal_predication_is_a_typed_attribute_on_the_entity_not_an_eventive_record_route_it_to_the_entity_state_register_gated_on_subject_binding
status: OPEN
review:
review_text:
---

# PROBLEM: the system records 'the sky is blue' / 'she is a doctor' / 'he was here' as an EVENT token (once pri 113 lands, an event with `is_state`), but a Kimian state is a TYPED ATTRIBUTE on the ENTITY (property / class / location / possession), written into that entity's file when the subject is bound -- which is why the event-token metric plateaued and the eventive board rows stayed byte-identical; the owner's pri 113 prototype captured typed attributes at 0.35 -> 0.56 with the holder right 0.85 of the time, and the attribute route unlocks type-licensed inference and attribute-based bridging / coref ('the doctor' -> 'she'), which fail SILENTLY today.

**slug:** `a_non_verbal_predication_is_a_typed_attribute_on_the_entity_not_an_eventive_record_route_it_to_the_entity_state_register_gated_on_subject_binding` -- **opened:** 2026-09-14 by strategy from the owner's pri 113 SOLVED.md section 14 ('the real path to improvement') and next step 2, and from the agent's one-structure-per-clause consolidation (state +0.0370 CI-sep) as the landed starting point.

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** A property predicated of an individual is stored WITH that individual (the file card / situation-model token), typed by what kind of predication it is, and retrieved by type when a later mention or inference needs it. Replicate the OPERATION, sweep the PARAMETERS.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- the attribute's type comes from the category organ and the copular binding (`copular_binding.predicted_type`: Higgins predicational / specificational / identificational), never from a gold column; the write is gated on the reader's OWN subject binding (the entity layer), never on a gold coref chain.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** the entity-state register (`hdlab/state_register`, the copular binding `copular_binding`, `_read_entity_states`) is the organ; the event detector's `is_state` structure (pri 113 landing) and the copular state reader are its arms; one clause yields ONE structure, and this brief decides WHERE it lives (on the entity) and WHAT reads it (inference, bridging, coref). Do not add a second state store.
> **PLASTIC, NEVER FROZEN:** the attribute types and their licensing are counts with an observe path.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Situation-model tokens carry typed attributes (Zwaan & Radvansky 1998: the entity dimension of the situation model; Kim 1976: states as property exemplifications; Higgins 1973 for the copular types). Built form: on a copular / non-verbal predication, once the subject is bound to an entity file (the reader's own referent, `referent_per_np` / `unified_referent`), write ATTRIBUTE(entity, type in {PROPERTY, CLASS, LOCATION, POSSESSION, IDENTITY}, value = the complement's content, polarity, time) into that entity's card with a symmetric EQUATE fallback for the inverse/specificational cases (the owner's section 4b: do not commit a subject/predicate order the inverse cases do not determine); readers that need it: type-licensed inference (a CLASS attribute licenses the class's expectations), attribute bridging ('the doctor' resolves to the entity carrying CLASS=doctor), and the state QA.
> 2. **REUSE.** The owner's pri 113 cell (`--attr` / section 14 prototype: typed-attribute capture 0.35 -> 0.56, holder 0.85), the agent's `state_pairs_from_slot` (the one-structure consolidation in its diff; state 0.7487 -> 0.7857 at full n), `hdlab/copular_binding.py` (`predicted_type`), the state register and the entity-state QA (`experiments/exp_situation_model_qa_v1.py` state dimension, `test_state_qa_consumer_organ.py`), the entity files (`hdlab/online_entity_cluster.py`, `unified_referent.py`), the common-noun resolver (`hdlab/commonnoun_binder.py`) for the bridging read.
> 3. **GENERALIZE.** Every reader of a copular state today (the state QA, the copular state reader, the temporal reasoner's islanded copular-state-as-event compute -- the owner's AUDIT UPDATE) must read the ONE structure; list them with line numbers and state which read the entity's card and which still read an event token.
> 4. **WALL -> DEEPER.** If the attribute write costs state-QA accuracy, the loss is in the subject binding (the gate), not the write -- measure the write under gold binding to bound it, then the live binding, and report the gap as the entity layer's item.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep the binding-confidence gate only.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Typed-attribute capture on UD-EWT test's 167 non-verbal clauses (owner's instrument: type + holder + value; 0.35 -> 0.56 prototype); the board's state dimension full size (the agent's consolidation 0.7857 is the floor to beat); a NEW instrument for the two consumers the attribute unlocks: attribute bridging on GUM (definite common-noun mentions whose antecedent carries the matching CLASS attribute; today's resolution rate vs with the attribute read) and type-licensed inference (the reasoning board's state arm); the coref / common-noun rows not down; every reader on one structure.
> 7. **ADJACENT.** pri 113 (landing; the `is_state` structure is the input), pri 117 (the heads rung's copular subject: the holder), pri 118 (graded mention typing: the binding), pri 112 (the register the card lives in).
> 8. **COMPLETION BAR.** ONE structure per clause living on the entity (typed attribute), read by the state QA, the copular state reader and the bridging resolver; typed-attribute capture up CI-separated from the prototype's floor with the holder right; the state dimension not below 0.7857; attribute bridging up CI-separated on its own instrument with a twin (attributes shuffled across entities) at floor; the islanded temporal copular-state compute retired or folded -- OR a numbered located negative naming the binding gap with its count.

**(PHASE DIAGRAM.)** The binding-confidence gate and the attribute-type prior are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Tokens -> categories -> heads (the copular subject) -> the predicate slot (pri 110/113) -> THIS attribute write on the entity -> state QA / bridging / inference.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When the text says "she is a doctor", the system now notices that something was asserted, but it files it as a happening rather than as a fact ABOUT HER. So later, when the text says "the doctor", nothing connects it to her, and nothing lets the system expect doctor-like things of her. The fix is to write "doctor" onto her file as a typed attribute, once the system is sure who "she" is, and let the later readers look there.

## 2. WHY THIS ONE
The owner's pri 113 run identified this as the real path after the event-token metric plateaued (section 14), prototyped it (0.35 -> 0.56), and named the two consumers that fail silently today; the agent's consolidation gives a landed one-structure floor to build on.

## 3. MEASURED vs INFERRED
MEASURED (owner, pri 113 §14): typed-attribute capture 0.35 -> 0.56, holder 0.85 (prototype); the eventive board rows byte-identical under the event-token form; (agent, pri 113 §11g) state 0.7487 -> 0.7857 CI-sep with one structure per clause. INFERRED: the bridging / inference gains.

## 4. ALREADY TRIED / DO NOT REDO
Recording the state as a second event token beside the copular state reader (two structures; the agent's disagreement count 30 -> 11 is the consolidation, keep it); committing a subject/predicate order for inverse copulars (owner's section 4b: use the symmetric EQUATE fallback).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read in full: the owner's pri 113 SOLVED.md sections 4b, 14, 15, 33; the agent's `notes/comparisons/pri113_agent/SOLVED_agent.md` sections 4c and 11g and `state_pairs_from_slot` in its diff; `hdlab/copular_binding.py`; the state register and `_read_entity_states` in `hdlab/situation_reader.py`; `hdlab/commonnoun_binder.py`; `verification/test_state_qa_consumer_organ.py`, `test_copular_is_a_binding_landing_organ.py`.

## 6. THE BAR (can-fail)
See checklist item 8. Floors: the landed one-structure event/state; twin: attributes shuffled across entities; paired bootstrap over clauses / mentions; the full board in one process with and without.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_typed_attribute_register_v1.py` (your cell), `notes/problems/<slug>/{SOLVED.md, typed_attribute_register_patch.diff}` (unified diffs against the entity-state files and their readers; never edit hdlab/ or tools/ directly), and any NEW asset under `data/hook_state/`.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md` (the 0.8148 state figure). 19c numbers are informational only.
