---
priority: 101
slug: subordinators_are_not_a_class_the_category_organ_reads_sconj_at_0_73_and_hands_a_null_cue_down_to_the_governor
status: OPEN
review:
review_text:
---

# PROBLEM: the word-category organ reads SUBORDINATORS ("when", "if", "because", "that", "after" before a clause) right only 73 times in 100 -- the weakest tag in the whole chain (AUX 0.98, VERB 0.94) -- so the governor's learned subordination cue (validity -1.42 vs +0.44, correct) receives a NULL input (+0.003) and clause-initial subordinate verbs keep being crowned the main word

**slug:** `subordinators_are_not_a_class_the_category_organ_reads_sconj_at_0_73_and_hands_a_null_cue_down_to_the_governor` -- **opened:** 2026-09-13 by strategy from pri 97's alternate path A (SOLVED by an agent session 17:10: "the knowledge is there; the input cannot deliver it"; the organ's SCONJ/ADP confusion flips a cue value on 370 test tokens, 3.9%%, for the subordination cue alone) and from strategy's own tag-to-head attribution (SCONJ tagged ADP = 31 net lost heads, the second-largest confusion).

> ## SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Name the structure and the computation; replicate the OPERATION, sweep the PARAMETERS (never adopt a number).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** — spaCy / any off-the-shelf parser / treebank-trained model at inference is a DEFECT; the UD treebank is a MEASURING instrument only (its trees are never read while learning).
> **🧩 ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** this is an extension of the ATTACHMENT arm of the Competition-Model organ (`hdlab/attachment_arm.py`; sibling arm `hdlab/graded_role_assigner.coarse_roles`). Do NOT mint a new organ; propose the change as a patch + probe, strategy lands it.
> **PLASTIC, NEVER FROZEN:** knowledge = counts in the asset; strengths = one pure function of counts; an online `observe_*` path must exist for anything you add.
> **🧱 WALL-PUSH PROTOCOL:** before writing wall / ceiling / negative, read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md`. A wall = an upstream trace + a stronger brain build, else a SPECIFIC board question.
> **A rigorous negative is a PASS** only if what failed was the brain's mechanism, faithfully built, with the number.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** How does a reader know "after" opens a clause in "after the game ended" but a phrase in "after the game"? Not from the word: from what FOLLOWS -- a clause (a finite verb arrives) vs a nominal run -- i.e. a FUNCTIONAL split of one closed-class item by its complement type, decided incrementally with revision when the verb arrives (the garden path is real and brief). Subordinators are NOT a coherent distributional substitution class at the organ's granularity (they distribute like prepositions): the reading-induced inventory's V-measure for SCONJ is about 0 at k=68 and 0.55 at k=136 (`notes/BRAIN_MATH_REFERENCE.md`, lexical-category acquisition row). Name the structure and the computation: the category of a closed-class item = its distributional class x the clause/phrase status of its complement, read from the incoming categories (a finite VERB within k words with no intervening nominal head), inside the same fixed-lag revision the organ already does.
> 2. **REUSE.** `hdlab/lexical_categories.py` (count-based generative model; second-order transitions; fixed-lag revision `posterior(words, lag)`, LAG=2; conflict-triggered stem reanalysis as the pattern for a TRIGGERED re-read; the refuted blanket neighbour-word channel -- do not re-add), `hdlab/induced_categories.py` (the reading-acquired inventory; builder `experiments/exp_reading_induced_categories_v2.py` -- raising k brings SCONJ to 0.55 at k=136), `hdlab/attachment_arm.py` (`function_word_arcs`: the subordinator frame; the pri 97 patch's `rsub` cue and `hold_expectation`'s subordinator-pending context -- both read this tag), `experiments/_diag_tag_to_head_loss.py` (attributes tag confusions to lost heads: SCONJ->ADP 31 net).
> 3. **GENERALIZE.** Temporal/causal/conditional subordinators (when/while/after/before/because/if/unless/although), the complementiser "that" (SCONJ before a clause vs DET/PRON), "for" before an infinitival clause, prepositions heading gerund clauses ("after doing" = SCONJ in UD), and "like/as" both ways; sentence-initial vs medial.
> 4. **WALL -> DEEPER.** If the functional split does not move SCONJ, split the residual by whether the complement verb arrives within the revision window (lag 2) or later -- a longer-range dependency may need the governor's clause detection to feed BACK (the heads rung telling the category organ a clause opened), which is a legitimate brain path (top-down prediction) to report with counts.
> 5. **OPTIMIZE BY EXACT REPLICATION;** the split is a count table like the others (P(c | item, complement-type)); sweep the window and the finite-verb criterion only.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Full UD-EWT test (25,094 tokens; `experiments/_diag_category_lag.py` at lag 2 = live): SCONJ recall 0.7326 and the SCONJ<->ADP confusion counts (66 / 15 on test) are the floors; overall 0.9278 (or the live number at the time -- check `notes/INTEGRATION_LEDGER.md`: pri 99's graded morpho-orthographic parse may have landed at 0.9313) must not fall; twin = the split cue with its complement-type labels shuffled; DOWNSTREAM (the point of this brief): the governor's root recall and `rsub` cue effect under the organ's own tags (`experiments/exp_attachment_main_assertion_v1.py` live-chain arm: root 0.769 with the pri 97 patch; `rsub` null +0.0029 is the number to move), and heads under own tags (`experiments/probe_heads_under_category_posterior_v1.py`).
> 7. **ADJACENT.** The subordinator tag feeds the hold expectation and the clause wrap-up of the in-order governor and the temporal organ's clause ordering; report which move; do not edit consumers.
> 8. **COMPLETION BAR.** SCONJ recall up CI-separated (paired bootstrap over sentences) with overall accuracy not down and ADP not down, the governor's `rsub` cue turning from null to a CI-separated root gain under the organ's own tags, twin at the floor, knowledge as counts with the existing observe path -- OR a numbered located negative naming the missing input (e.g. the share of subordinate verbs arriving beyond the revision window).

**(PHASE DIAGRAM.)** The revision window, the finite-verb window k, the inventory's k (68 -> 136) are FREE TO SWEEP; a wall "at this config" = move the operating point.
**(FULL-STACK UPSTREAM.)** Tokens -> this organ; the complement's verb must itself be tagged VERB (the AUX/VERB confusion of be/have is a known 58%%-of-loss item, `notes/OVERNIGHT_PLAN_2026-09-12.md` 14:24) -- say with counts how often the split's evidence is itself mis-tagged.

## 1. THE PROBLEM IN PLAIN LANGUAGE
Words like "when", "if", "after" and "that" announce that a whole clause is coming and that its verb is NOT the sentence's main statement. The reader recognises these words only three times in four, because by their neighbours they look like ordinary prepositions. The governor has already learned the right rule ("a verb under a subordinator is not the main word", strongly) but gets the signal too rarely to use it. People decide by what follows: a verb means a clause, a noun phrase means a phrase. We want that decision in the word-category organ.

## 2. WHY THIS ONE
It is the weakest tag in the chain and the named input ceiling of a just-solved problem whose cue is already learned and correct; it also costs 31 heads directly (the second-largest tag-to-head confusion).

## 3. MEASURED vs INFERRED
- **MEASURED (2026-09-13):** SCONJ recall 0.7326 on test; SCONJ->ADP 66 tokens, ADP->SCONJ 15 (full test); 31 net lost heads from SCONJ->ADP (test 700); `rsub` cue effect +0.0029 (null) with a learned validity of -1.42 vs +0.44; V-measure for SCONJ ~0 at k=68, 0.55 at k=136.
- **INFERRED (prove with a number):** a complement-type split inside the revision window lifts SCONJ recall by 10+ points and turns `rsub` into a CI-separated root gain.

## 4. ALREADY TRIED / DO NOT REDO
A blanket neighbour-WORD emission channel (REFUTED 2026-09-13: 0.9152 at full weight). Raising the inventory's k alone is measured (0.55 at k=136) -- use it as a lever, not as the whole answer.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read IN FULL: `hdlab/lexical_categories.py`, `hdlab/induced_categories.py`, `notes/problems/the_main_assertion_is_a_scorer_deficit_the_governor_rates_non_verbal_predicates_and_subordinate_first_clauses_as_non_roots/SOLVED.md` (sections 6b, 6c, 9), `experiments/_diag_tag_to_head_loss.py`, `notes/BRAIN_MATH_REFERENCE.md` (lexical-category rows), `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md`.

## 6. THE BAR (can-fail)
See checklist item 8.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_category_subordinator_split_v1.py` (must use `experiments._seed_checkpoint.get_output_dir`), `notes/problems/<slug>/SOLVED.md`, `notes/problems/<slug>/lexical_categories_patch.diff` (do NOT edit hdlab/ directly -- strategy lands it), a candidate counts asset under `data/hook_state/` (never overwrite the live asset). Commit PATH-LIMITED, never push, never `git add -A`.

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT use spaCy / nltk taggers / any supervised tagger at inference. Do NOT read the treebank's test split while learning.
