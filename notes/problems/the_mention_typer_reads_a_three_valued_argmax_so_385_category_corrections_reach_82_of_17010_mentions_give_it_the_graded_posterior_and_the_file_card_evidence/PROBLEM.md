---
priority: 118
slug: the_mention_typer_reads_a_three_valued_argmax_so_385_category_corrections_reach_82_of_17010_mentions_give_it_the_graded_posterior_and_the_file_card_evidence
status: OPEN
review:
review_text:
---

# PROBLEM: the entity layer's mention typer (`experiments/gum_coref._mention_type` for the board rows; the reader's own `referent_per_np` / `coref` typing) is a pure function of the category organ's ARGMAX and is THREE-valued (PRON -> pronoun, PROPN -> name, everything else -> common) -- so when the passage register (pri 112) corrects 385 category argmaxes on the board's 128 test documents, 189 of them (49%) are corrections the type cannot represent (ADJ->NOUN 57, VERB->NOUN 34, NOUN->VERB 16, ADJ->VERB 12) and only 82 of 17,010 mentions (0.48%) change type; the hand-off from categories to entities discards the organ's graded belief and the file-card evidence it was folded into.

**slug:** `the_mention_typer_reads_a_three_valued_argmax_so_385_category_corrections_reach_82_of_17010_mentions_give_it_the_graded_posterior_and_the_file_card_evidence` -- **opened:** 2026-09-14 by strategy from pri 112's phase-7 section P7.6 (the counts above are the agent's, measured end to end with both loader arms in one process) and pri 109's finding that the category organ is the whole common-noun gap.

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** The entity layer receives a graded belief about what kind of referring expression it is looking at (Gundel / Hedberg / Zacharski 1993 givenness statuses; Ariel 1990 accessibility) and the file-card evidence (has this individual been met?), not a three-way label. Replicate the OPERATION, sweep the PARAMETERS.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- no gold column at decision time (pri 109's rule), no thresholds beyond the organ's own posterior mass.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** the category organ (`hdlab/lexical_categories.py`) already computes the posterior AND the file-card individuation evidence `log P(E|c)` (pri 104's entity-feedback arm, now fed in order by pri 112); the mention typer is a CONSUMER that should read both -- the same repair already made at categories -> heads (`arc_scores_graded`). Do not build a second typer; make the one typer graded and route both the reader's stream and the board loader through it.
> **PLASTIC, NEVER FROZEN:** counts + observe paths.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** A mention's type is a graded distribution over {pronoun, name, common, non-nominal} computed from (a) the organ's posterior over categories for the span's head (PROPN / NOUN / PRON / ADJ / VERB mass), and (b) the file-card evidence for the surface form (met before in this passage: a repeat mention carries its own type continuity). Consumers (the coref decision, the aliaser, the common-noun resolver, the salience readout) weight candidates by that distribution instead of branching on a label. Built form: `mention_type_graded(head_posterior, card_evidence) -> {type: P}` in the entity layer, with the argmax available for any consumer that must branch (byte-identical to today when the posterior is peaked).
> 2. **REUSE.** pri 112's P7.6 harness (both loader arms in one process; the 385 / 189 / 82 counts); `experiments/gum_coref.py` (`_mention_type_organ`, `_head_of_span_organ`, `apply_organ_layer`, the twin-identity witness); `hdlab/referent_per_np.py`, `hdlab/coref.py` (`name_content_tokens`, `_span_head_is_name` after pri 109's head-domain fix), `hdlab/online_entity_cluster.py`, `hdlab/unified_referent.py`; the reader's `_cached_tag_matrix` (the posterior matrix is already computed once per sentence); pri 109's paired-subpopulation instrument (identical items, identical floor -- the only instrument that compares typing arms fairly).
> 3. **GENERALIZE.** Enumerate every consumer that branches on `mtype == "name"` / `"pronoun"` / `"common"` (grep `mtype`, `is_pronoun`, `is_name` across hdlab/ and the board arms) and classify: reads the graded type, or branches on the argmax.
> 4. **WALL -> DEEPER.** If the graded type moves the coref / common-noun rows by less than their CI, that is the honest count of how much category correction reaches typing (pri 112: 82 of 17,010); the next rung is the category organ's own accuracy on ADJ/NOUN/VERB boundaries (pri 111's participle/adjective items), which this brief reports with counts, not repairs.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep only the posterior temperature.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** On the board's GUM test split (128 docs, 17,010 mentions): typing accuracy against the gold mention type (name / pronoun / common) for argmax vs graded (report P/R/F1 per type); the coref / common-noun / salience rows gold-free with CIs on the PAIRED subpopulation (pri 109's instrument) and on the full rows; the reader's entity-QA instrument (200 questions); the board's 7 dimensions full size, both arms in one process.
> 7. **ADJACENT.** pri 112 (landed: the register in order), pri 109 (gold-free rows), pri 116 (case: the typer's PROPN mass depends on it -- run after or alongside), pri 104 (the entity-feedback arm).
> 8. **COMPLETION BAR.** The typer reads the graded posterior + the card evidence (one organ path, both the reader's stream and the board loader); typing F1 per type up CI-separated vs the argmax on GUM test; coref / common-noun rows not down (up on the paired subpopulation CI-separated or a counted reason); every consumer classified; twin (posterior rows shuffled across mentions) at floor -- OR a numbered located negative naming the consumer that cannot read a graded type and why.

**(PHASE DIAGRAM.)** The posterior temperature and the card-evidence weight are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Tokens -> categories (posterior + file cards) -> THIS typing hand-off -> entity files -> coref / common-noun / salience / the reader's entity QA.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The word-category organ now has a better, more honest opinion about each word (it reads the passage in order and knows which people and things it has met). But the part of the system that decides whether a phrase is a name, a pronoun or an ordinary noun only looks at the organ's single best guess, and only cares about three answers. So almost all of the organ's improvements never reach the who-is-who decisions: of 385 corrected words, 82 changed a decision. The fix is to hand the who-is-who layer the organ's full belief and its memory of what has been met, and let it weigh candidates with them.

## 2. WHY THIS ONE
pri 109 showed the category organ is the whole common-noun gap and pri 112 located the hand-off where its corrections are discarded, with counts; the same graded-hand-off repair already paid at the heads rung.

## 3. MEASURED vs INFERRED
MEASURED (pri 112 P7.6, GUM test 128 docs / 127,919 tokens / 17,010 mentions, both loader arms in one process): opening the passage moves 385 argmaxes (0.301%), 196 cross the PROPN/PRON boundary, 189 (49.1%) are invisible to the three-valued type, 82 mentions (0.482%) change type (common->name 50, name->common 20, name->pronoun 9); the board rows do not move (coref 0.4172 -> 0.4169; common-noun 0.5470 -> 0.5458 with its margin over floor UP 0.0073 -> 0.0117). INFERRED: the size of the row movement under a graded type.

## 4. ALREADY TRIED / DO NOT REDO
Reading the type from capitalisation (pri 109: F1 0.672, 1,331 false names); a second decider beside the category organ (pri 104's wire equals `upos[head]=="PROPN"` -- one decider).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read in full: pri 112's SOLVED.md (P7.6 and the register sections) and its cell; pri 109's SOLVED.md (the four-decider table, the paired-subpopulation instrument, the head-domain fix); `experiments/gum_coref.py`; `hdlab/referent_per_np.py`, `hdlab/coref.py`, `hdlab/online_entity_cluster.py`; `hdlab/lexical_categories.py` (posterior, the entity-feedback arm, `log_entc`).

## 6. THE BAR (can-fail)
See checklist item 8. Floors: the argmax typer; twin: posterior rows shuffled across mentions; paired bootstrap over mentions / documents; the full board in one process with and without.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_graded_mention_typing_v1.py` (your cell), `notes/problems/<slug>/{SOLVED.md, graded_mention_typing_patch.diff}` (unified diffs against the entity-layer files and `experiments/gum_coref.py`; never edit hdlab/ or tools/ directly), and any NEW asset under `data/hook_state/`.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md` (the gold-split entity rows). 19c numbers are informational only.
