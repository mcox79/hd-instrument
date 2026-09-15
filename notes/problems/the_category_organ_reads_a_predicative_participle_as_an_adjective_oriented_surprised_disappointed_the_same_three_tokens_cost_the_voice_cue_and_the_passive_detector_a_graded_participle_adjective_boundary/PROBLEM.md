---
priority: 123
slug: the_category_organ_reads_a_predicative_participle_as_an_adjective_oriented_surprised_disappointed_the_same_three_tokens_cost_the_voice_cue_and_the_passive_detector_a_graded_participle_adjective_boundary
status: OPEN
review:
review_text:
---

# PROBLEM: the category organ hands down a near-tie or an ADJ argmax on predicative participles ('especially oriented' ADJ 0.950 / VERB 0.050; 'was surprised' 0.517 / 0.481; 'never been disappointed' 0.745 / 0.244), and the SAME three tokens then cost two different consumers -- the clause-local voice cue misses them (3 of the detector's 11 breaks, pri 111 section 17.1) and the widened participle detector loses them (3 of its 31 disagreements, section 20.2) -- because both consumers read the ARGMAX of a boundary the organ itself represents as graded; the participle/adjective boundary is a category-organ item (the VERB mass on a passive-participial reading is real evidence), and the consumers should read that mass, not the label.

**slug:** `the_category_organ_reads_a_predicative_participle_as_an_adjective_oriented_surprised_disappointed_the_same_three_tokens_cost_the_voice_cue_and_the_passive_detector_a_graded_participle_adjective_boundary` -- **opened:** 2026-09-15 by strategy from pri 111's SOLVED.md sections 17.1 and 20.2 and its closing question 1.

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** The adjectival / verbal reading of a participle is a genuine ambiguity the comprehender resolves from the auxiliary chain, the by-phrase and the participle's own frequency of use as each -- a graded belief, not a label. Replicate the OPERATION, sweep the PARAMETERS.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- counts + observe paths; the UD treebank is the MEASURING instrument (its ADJ/VERB convention on participles is itself a convention, not the fact).
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** the category organ (`hdlab/lexical_categories.py`) owns the boundary; the voice cue (`hdlab/thematic_role_labeler.is_passive_predicate`, pri 111) and the participle detector (the folded `participle_bypp_gate`, pri 111) are CONSUMERS -- give them the graded VERB-vs-ADJ mass and let their cue values weight it; do not add a participle list.
> **PLASTIC, NEVER FROZEN:** counts + observe paths.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Two moves, both graded: (a) at the organ, the participle's category posterior should carry its evidence honestly -- the auxiliary chain ('was/been' + -ed/-en), the by-phrase, and the word's own counts as ADJ vs VERB (pri 110's predicate-slot machinery reads the auxiliary chain already); measure how much of the boundary the organ gets right on the gold and whether these three tokens are the organ's error or a convention; (b) at the consumers, read P(VERB) + P(ADJ) with the participial morphology as the passive evidence (a predicative participle after a copula IS a passive-or-adjectival predication either way), so the voice cue and the participle detector do not drop a token whose label happens to fall on the ADJ side of 0.5.
> 2. **REUSE.** pri 111's SOLVED.md 17.1 / 20.2 and its cell `experiments/exp_passive_cue_clause_local_v1.py` (the per-item attribution tables; the 11-break and 31-disagreement lists), `hdlab/thematic_role_labeler.py` (`is_passive_predicate`, the counts asset `data/hook_state/passive_voice_counts_v1.json`), `hdlab/graded_role_assigner.py` (the folded gate), `hdlab/lexical_categories.py` (posterior, `revise_for_predicate_slot`), the reader's `_cached_tag_matrix` (the posterior is already available to every consumer at no cost).
> 3. **GENERALIZE.** Enumerate every consumer that branches on `tag == "ADJ"` vs `"VERB"` for a participle-shaped token (grep `_is_participle`, `VBN`, `-ed`): list them; each reads the mass or is reported.
> 4. **WALL -> DEEPER.** If the organ's posterior on these tokens is genuinely ADJ-dominant because the word IS more often adjectival, the consumer's morphology cue must carry the construction ('was X-ed by' vs 'very X-ed'); measure the by-phrase / degree-modifier split before declaring the organ wrong.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep the mass threshold only.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Category accuracy on participle-shaped tokens on UD-EWT test (ADJ vs VERB, with the gold as the measuring convention), the voice cue's P/R on the 2605 predicates (pri 111's instrument; 11 breaks -> ?), the participle detector's disagreements (31 -> ?), the board's agent and patient rows full size, both arms in one process; GUM / GENTLE out of supply.
> 7. **ADJACENT.** pri 111 (landed), pri 110 (the auxiliary chain read), pri 118 (graded typing: the same graded-hand-off principle one layer over).
> 8. **COMPLETION BAR.** The two consumers read the graded mass (no participle list), the three named tokens recovered without new breaks (voice cue P/R not down, detector disagreements down), category accuracy on participle-shaped tokens not down, board not down full size, twin (mass shuffled across participle tokens) at floor -- OR a numbered located negative naming whether the boundary is the organ's error or the treebank's convention, with counts.

**(PHASE DIAGRAM.)** The mass threshold and the construction cue weights are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Tokens -> categories (this boundary) -> the voice cue / the participle detector -> the agent competition -> the board's agent row.

## 1. THE PROBLEM IN PLAIN LANGUAGE
Words like "surprised" or "disappointed" can describe a state (an adjective) or report something done to someone (a passive verb). The category organ knows it is torn (it gives "surprised" 52 to 48) but hands down only its label; the two organs that read voice then treat "was surprised" as not passive and miss it. Give them the organ's actual degree of belief and let the "was ... by" evidence decide.

## 2. WHY THIS ONE
The same three tokens appeared as the residual in two different consumers of pri 111; the fix is the graded hand-off already made elsewhere in the chain; small but a clean instance of the principle.

## 3. MEASURED vs INFERRED
MEASURED (pri 111): posteriors 0.950/0.050, 0.517/0.481, 0.745/0.244 on the three tokens; 3 of 11 voice-cue breaks; 3 of 31 detector disagreements. INFERRED: how many more participle-shaped tokens sit on the wrong side of the argmax across UD-EWT test.

## 4. ALREADY TRIED / DO NOT REDO
The suffix test as the participle evidence (pri 111's pre-fold gate: it caught these three only by ignoring the category entirely and mis-fired on 30 of 43 licences); a participle word list.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read in full: pri 111's SOLVED.md sections 17, 19, 20 and its cell; `hdlab/thematic_role_labeler.py`; the folded gate in `hdlab/graded_role_assigner.py`; `hdlab/lexical_categories.py` (posterior, the predicate-slot revision); `verification/test_byhead_agent_cue_landing.py`, `test_coarse_role_competition.py`.

## 6. THE BAR (can-fail)
See checklist item 8. Floors: the argmax consumers as landed; twin: the mass shuffled across participle-shaped tokens; paired bootstrap over items; the full board in one process with and without.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_participle_adjective_boundary_graded_v1.py` (your cell), `notes/problems/<slug>/{SOLVED.md, participle_boundary_patch.diff}` (unified diffs against `hdlab/thematic_role_labeler.py` / `hdlab/graded_role_assigner.py` and, if the organ side is the fix, `hdlab/lexical_categories.py`; never edit hdlab/ or tools/ directly), and any NEW asset under `data/hook_state/`.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. 19c numbers are informational only.
