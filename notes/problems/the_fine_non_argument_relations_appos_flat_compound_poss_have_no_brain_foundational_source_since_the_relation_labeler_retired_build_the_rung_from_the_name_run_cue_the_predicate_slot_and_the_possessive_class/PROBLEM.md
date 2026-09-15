---
priority: 134
slug: the_fine_non_argument_relations_appos_flat_compound_poss_have_no_brain_foundational_source_since_the_relation_labeler_retired_build_the_rung_from_the_name_run_cue_the_predicate_slot_and_the_possessive_class
status: OPEN
review:
review_text:
---

# PROBLEM: pri 129 retired the supervised relation labeler from the live path, and the ONE role competition (`graded_role_assigner.coarse_roles`) labels ARGUMENT relations only (nsubj / obj / obl, 'dep' elsewhere) -- so every live consumer that keyed on a FINE non-argument relation now reads 'dep': the crosstype bridge's name-linking cues (`hdlab/crosstype_bridge.py:238-253`: `appos` "Elizabeth, the doctor", `flat` / `compound` "Mary Smith", `nmod:poss` "her brother", the copular verb's obj/xcomp) no longer fire on the reader's own parse (`crosstype_live_adapter._parse_sentence`, routed to the competition at the pri 129 landing), and any other consumer of those relations is in the same state; the brain-foundational rung for them exists in parts and is unassembled: pri 118's span-level NAME-RUN cue (learned online) gives flat/compound, pri 113/117's predicate slot and the nonverbal-predication constructions give appos as a reduced predication, the possessive determiner / genitive class from the category organ gives poss -- assemble them as ONE labels-rung arm with count-accrued validities and an observe path, measure the bridge's name-linking and the affect/experiencer gain (+0.0838 CI-sep before) with and without, and retire the 'dep' fallback.

**slug:** `the_fine_non_argument_relations_appos_flat_compound_poss_have_no_brain_foundational_source_since_the_relation_labeler_retired_build_the_rung_from_the_name_run_cue_the_predicate_slot_and_the_possessive_class` -- **opened:** 2026-09-15 by strategy at the pri 129 landing (the reader-driven board crashed on `_frontend_labeler`; the adapter was routed to the competition; the fine relations read 'dep').

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** A name run ("Mary Smith") is one referring expression recognised as a unit (the span-level name cue the reader already learns online, pri 118); an apposition ("Elizabeth, the doctor") is a REDUCED PREDICATION (the same construction as "Elizabeth is the doctor" without the copula -- the nonverbal-predication organ of pri 113 and the predicate slot of pri 110/117 already detect predications; the appositive is their juxtaposed form); a possessive is a determiner-class relation the category organ already tags (PRON possessive / genitive 's). None needs a supervised labeler: each is a construction with a cue whose validity is accrued from usage.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- spaCy, GLUCOSE, MAVEN and ANY off-the-shelf parser/dataset/model are NOT brain-foundational; the retired `arc_labeler` stays retired; an external tool AT INFERENCE is a DEFECT THAT BLOCKS.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** this is the NON-ARGUMENT ARM of the one labels rung (`graded_role_assigner`), reading the constructions the other organs already detect; `coarse_roles` returns it alongside the argument roles under the same UD-shaped strings so consumers do not churn.
> **DOWNSTREAM REGRESSION AFTER A BF UPSTREAM IS NOT FAILURE:** the perceptron's retirement stands; the consumers are repaired by giving them this arm.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` before writing wall / ceiling / negative.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** (a) Enumerate (grep, file:line) every live consumer of a non-argument deprel string (`appos`, `flat`, `compound`, `nmod:poss` / `poss`, `xcomp`, `acl`, `advcl`, `conj`, `cc`, `det`, `case`, `mark`) in hdlab/ and what each does with it; count how many fire on the live default read with the perceptron gone (expect: none). (b) Build the arm: flat/compound from the name-run cue (pri 118 `mention_span_cue_counts.json` + the category organ's PROPN runs), appos from juxtaposed nominal predication (the nonverbal-predication constructions; comma-bounded NP after a name/NP), poss from the possessive class (PRON possessive forms; the 's genitive PART), xcomp/acl/advcl from the attachment arm's arc type where it already distinguishes them (pri 117's csubg/predicate-slot features; pri 133's infinitival cues) -- each cue's validity ACCRUED from the teaching corpus with an observe path (`tools/build_coarse_role_validities.py` is the template). (c) Return them from `coarse_roles` (or a sibling `fine_relations`) under the UD strings; the adapter and every consumer in (a) read them. (d) Measure on UD-EWT test: per-relation P/R vs gold deprels (the measuring gold, not a training target); the crosstype bridge's name-linking precision/recall on GUM (its cell); the affect/experiencer gain through the live reader (the +0.0838 CI-sep the bridge recovered on 2026-09-0x; its witness `test_affect_reroute_landing.py`).
> 2. **REUSE.** `hdlab/graded_role_assigner.py` (`coarse_roles`, validities), `hdlab/coref.py` (pri 118's name-run cue), `hdlab/attachment_arm.py` (constructions, predicate slot), `hdlab/lexical_categories.py` (PRON possessive, PART), the nonverbal-predication organ (pri 113), `hdlab/crosstype_live_adapter.py` + `hdlab/crosstype_bridge.py`, `tools/build_coarse_role_validities.py`, pri 108/111/129 SOLVED.md, witnesses `test_crosstype_live_wire.py`, `test_deleak_crosstype_live_adapter.py`, `test_affect_reroute_landing.py`, `test_coarse_role_competition.py`.
> 3. **GENERALIZE.** Every consumer from (a) reads the arm; a witness asserts no live consumer keys on a relation the rung cannot produce.
> 4. **WALL -> DEEPER.** If appos precision is low, the missing cue is the predication organ's own confidence (graded), not a comma rule.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep the count smoothing only.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Per-relation P/R on UD-EWT test vs the retired perceptron's numbers (informational floor); the bridge's numbers; the affect gain through the live reader; the product board both arms one process.
> 7. **ADJACENT.** pri 129 (landed with the 'dep' fallback), pri 118, pri 113, pri 133, pri 131.
> 8. **COMPLETION BAR.** The bridge's name-linking cues fire again on the reader's own parse from the BF arm; the affect/experiencer gain reproduced (or its loss attributed by relation); per-relation P/R published; validities accrued with an observe path; the board not down -- OR a numbered located negative per relation.

**(PHASE DIAGRAM.)** Count smoothing FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Tokens -> categories (PROPN runs, possessive class, PART) -> heads (constructions) -> THIS arm -> the crosstype bridge / affect / goals.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The old machine-learned labeller told the reader things like "Mary Smith is one name", "Elizabeth, the doctor" means Elizabeth is the doctor, and "her brother" is a possession. It is gone (it was not brain-foundational). The reader already has the pieces to work those out itself; put them together so the name-linking step gets them back.

## 2. WHY THIS ONE
A consumer went quiet at the pri 129 landing (the bridge's name links), and the ingredients are all built.

## 3. MEASURED vs INFERRED
MEASURED: the consumer list at `crosstype_bridge.py:107-253` (relations used); the crash and the 'dep' fallback at the landing. INFERRED: the size of the bridge's loss under 'dep' (measured at the landing in `data/hook_state/pri129_crosstype.log` -- read it first) and the arm's P/R.

## 4. ALREADY TRIED / DO NOT REDO
Reviving the perceptron labeler; a comma rule for appositions.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read pri 129's SOLVED.md, `hdlab/crosstype_bridge.py` and `crosstype_live_adapter.py`, `coarse_roles`, pri 118's name-run cue, the landing log named above.

## 6. THE BAR (can-fail)
See checklist item 8.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_fine_relations_arm_v1.py` (your cell; `get_output_dir` per Q115), `notes/problems/<slug>/{SOLVED.md, fine_relations_arm_patch.diff}` (unified diffs against `hdlab/graded_role_assigner.py`, `hdlab/crosstype_live_adapter.py` and the consumers from item 1a; never edit hdlab/ directly), the NEW validity asset under `data/frontend_assets/`.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. 19c numbers are informational only.
