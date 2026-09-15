---
priority: 133
slug: the_attachment_arm_mis_attaches_30_percent_of_infinitival_verbs_wire_the_predicate_slot_into_the_infinitival_arc_and_add_a_nominal_governor_cue_accrued_from_counts
status: OPEN
review:
review_text:
---

# PROBLEM: the attachment arm (`hdlab/attachment_arm.py`, the heads rung) attaches an infinitival verb to the wrong head on 32.3% of UD-EWT test infinitivals (109 of 337; pri 129 §6b), and the loss is TWO cues counted by construction: (a) `acl_nominal` "a plan to leave" 76.8% wrong (32 errors -- the arm has NO cue that lets a NOUN govern an infinitival clause; every infinitival cue it owns pushes the clause away from a nominal governor) and (b) `csubj_extrapos` "it is hard to say" 43.5% wrong (22 errors: the arm attaches to the expletive PRON where gold is the ADJ that HOLDS THE PREDICATE SLOT -- pri 110/117's `predicate_sites` already computes that, graded, and the infinitival arc never reads it); a count-accrued prototype takes infinitival heads 0.6766 -> 0.8012 (+0.1240 CI[+0.0663,+0.1802] paired, twin 0.4540) but loses on `advcl_purpose` because it overrides the other cues -- land the two cues INSIDE `arc_scores` as competing cues with validities accrued online, which also lifts the goal PURPOSE decision from parity to +0.1084 CI-sep (pri 129).

**slug:** `the_attachment_arm_mis_attaches_30_percent_of_infinitival_verbs_wire_the_predicate_slot_into_the_infinitival_arc_and_add_a_nominal_governor_cue_accrued_from_counts` -- **opened:** 2026-09-15 by strategy from pri 129's phase 7 (§6b: the per-construction table; `--infin` arm; asset `infinitival_governor_validities_ud_ewt.json` in `data/frontend_assets/`).

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Attachment is cue competition (the Competition Model, Bates & MacWhinney; the arm's own form since pri 117): the infinitival clause competes for a governor among the verb, the noun ("a plan to leave": the noun's own subcategorisation -- plan/attempt/chance/way TAKE an infinitival complement, a lexical expectation accrued from usage) and the predicate-slot holder ("it is hard to say": the adjective holding the slot is the governor, the expletive is not a candidate). Each cue has a validity accrued from confirmed attachments (an observe path), and the decision is the competition, never an override.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- spaCy, GLUCOSE, MAVEN and ANY off-the-shelf parser/dataset/model are NOT brain-foundational; a vetted static offline foundation asset is admissible supply (UD-EWT train as the teaching corpus, as pri 117); an external tool AT INFERENCE is a DEFECT THAT BLOCKS.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** both cues live in `attachment_arm.arc_scores` (the one attachment competition) with the same online validity machinery pri 117 landed (`tools/build_attachment_validities.py`); the predicate slot is READ from `predicate_sites` / `lexical_categories` (pri 110), not recomputed.
> **ORGANS TAKE DATA IN ORDER:** the infinitival decision is made when the clause arrives, from what the arm knows at that word (the noun's expectation is already open; the slot holder is already known).
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** (a) Reproduce pri 129's `--infin` table first-hand (UD-EWT test, the four constructions, arm error per construction, the prototype's numbers). (b) Cue 1, THE PREDICATE-SLOT GOVERNOR: when a `to`-infinitival's candidate governor set contains the expletive subject and the slot holder (ADJ/NOUN predicate of a copula), the slot holder's occupancy (`predicate_sites`, graded) is a cue FOR it and against the expletive -- accrued validity, not a rule. (c) Cue 2, THE NOMINAL GOVERNOR: a NOUN immediately governing an infinitival (`acl` "a plan to leave") is licensed by the noun's infinitival-complement expectation, ACCRUED from counts of (noun lemma -> infinitival complement) in the teaching corpus with an observe path at read time (the arm's own discipline: pri 117's `attachment_csubg_validity_v1.json` is the template) -- a lexical expectation, not a list. (d) Land both as COMPETING cues in `arc_scores` (the prototype overrode; the landed form competes) and rebuild the validities with `tools/build_attachment_validities.py` (joint teaching, pri 117's path); every call site passes the new inputs (the 09-14 builder rule). (e) Measure per construction: none of the four may go DOWN CI-sep; `advcl_purpose` in particular (the prototype's loss).
> 2. **REUSE.** `hdlab/attachment_arm.py` (`arc_scores`, `revise_for_predicate_slot`, `predicate_sites`, the csubg feature, `load_attachment_validities`), `tools/build_attachment_validities.py`, `hdlab/lexical_categories.py` (the predicate slot), pri 117's SOLVED.md in full (the online validity, the reanalysis, the beam), pri 110's SOLVED.md (sole-AUX predicates), pri 129's SOLVED.md §6b-6c and its cell `experiments/exp_labels_rung_to_live_consumers_v1.py --infin` (the per-construction scorer and the prototype), `data/frontend_assets/infinitival_governor_validities_ud_ewt.json` (the prototype's counts -- rebuild, do not adopt), witnesses `test_attachment_arm.py` (17), `test_attachment_arm_fastpath.py`, `test_attachment_coordination.py`, `test_copular_subject_attachment_learned_*`.
> 3. **GENERALIZE.** Every consumer of infinitival heads (the goal PURPOSE arm of pri 129, xcomp control for who-did-what, the state reader's copular subjects) measured before/after; the attachment reference twin (`arc_scores_reference`) ported in the same diff (the twin rule).
> 4. **WALL -> DEEPER.** If the nominal-governor cue over-fires on "want to go" (xcomp control), the missing signal is the verb's own control expectation competing -- accrue it, do not threshold.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep the count smoothing and the beam width only.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Infinitival heads per construction (UD-EWT test n=337) vs the shipped arm and the nearest-preceding-VERB floor, twin = validities permuted; UAS overall not down; the purpose decision (pri 129's cell, `--goal`); the product board both arms one process (agent, patient, state rows); read time.
> 7. **ADJACENT.** pri 129 (the purpose arm; landing), pri 117 (the copular subject; the same organ), pri 114 (organ-tagged acquisition), pri 101 (SCONJ/PART class).
> 8. **COMPLETION BAR.** Infinitival heads CI-sep over the shipped arm with no construction down CI-sep; UAS not down; the purpose decision up (target +0.10); validities accrued with an observe path (twin at floor); the reference twin ported; the board not down -- OR a numbered located negative naming the construction that cannot be won by competition and why.

**(PHASE DIAGRAM.)** Count smoothing, the beam width, the accessibility of the slot holder are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Tokens -> categories (PART 'to', the predicate slot) -> THIS attachment competition -> roles / purpose / state.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When a sentence has "to do something" in it, the reader attaches that clause to the wrong word one time in three. Two reasons, counted: it has no idea that some nouns ("a plan to leave") expect such a clause, and it does not use the fact it already has that in "it is hard to say" the word "hard" is the one doing the predicating. Teach both as learned expectations that compete with the others.

## 2. WHY THIS ONE
Top of the chain (heads), a located loss with counts, a measured prototype (+12 points on infinitival heads), and a downstream consumer already built that gains +11 points from it (the purpose decision).

## 3. MEASURED vs INFERRED
MEASURED (pri 129 §6b): the per-construction table; the prototype's gain and its advcl_purpose loss. INFERRED: the competing (non-override) form's numbers.

## 4. ALREADY TRIED / DO NOT REDO
An override cue (the prototype: loses on purpose clauses); a word list of infinitival-taking nouns.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
(1) `python tools/substrate_map.py`; (2) read pri 117's and pri 129's SOLVED.md in full, then `hdlab/attachment_arm.py` and `tools/build_attachment_validities.py`; (3) run `--infin` first.

## 6. THE BAR (can-fail)
See checklist item 8. Floors: the shipped arm; nearest-preceding-VERB; twin: validities permuted; paired bootstrap over sentences.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_infinitival_governor_competition_v1.py` (your cell; `get_output_dir` per Q115), `notes/problems/<slug>/{SOLVED.md, infinitival_governor_patch.diff}` (unified diffs against `hdlab/attachment_arm.py` and `tools/build_attachment_validities.py`; never edit hdlab/ or tools/ directly), the rebuilt validity asset under `data/frontend_assets/` (a NEW file name; do not overwrite the shipped one).

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. 19c numbers are informational only.
