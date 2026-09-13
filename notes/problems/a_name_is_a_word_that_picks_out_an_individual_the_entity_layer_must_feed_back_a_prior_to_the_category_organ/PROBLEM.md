---
priority: 104
slug: a_name_is_a_word_that_picks_out_an_individual_the_entity_layer_must_feed_back_a_prior_to_the_category_organ
status: OPEN
review:
review_text:
---

# PROBLEM: "the MSM", "the Gateses", "the Europeans" are names WITH a determiner and "the CEO" is not; no form cue separates them -- what does is whether the string picks out an INDIVIDUAL the passage already knows, which the entity layer decides downstream of the category decision it should be informing; the dependency runs both ways and only one direction is wired

**slug:** `a_name_is_a_word_that_picks_out_an_individual_the_entity_layer_must_feed_back_a_prior_to_the_category_organ` -- **opened:** 2026-09-13 by strategy from pri 99's alternate path 1 (PARTIAL by bar, closed 17:12: 25 arms never took the name/common-noun confusions below 144 of 163 because 58 are structurally form-free and the capitalisation oracle's precision/recall are one curve: precision 0.812 / recall 0.658).

> ## SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Name the structure and the computation; replicate the OPERATION, sweep the PARAMETERS (never adopt a number).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** — spaCy / any off-the-shelf parser / treebank-trained model at inference is a DEFECT; the UD treebank is a MEASURING instrument only (its trees are never read while learning).
> **🧩 ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** this is an extension of the ATTACHMENT arm of the Competition-Model organ (`hdlab/attachment_arm.py`; sibling arm `hdlab/graded_role_assigner.coarse_roles`). Do NOT mint a new organ; propose the change as a patch + probe, strategy lands it.
> **PLASTIC, NEVER FROZEN:** knowledge = counts in the asset; strengths = one pure function of counts; an online `observe_*` path must exist for anything you add.
> **🧱 WALL-PUSH PROTOCOL:** before writing wall / ceiling / negative, read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md`. A wall = an upstream trace + a stronger brain build, else a SPECIFIC board question.
> **A rigorous negative is a PASS** only if what failed was the brain's mechanism, faithfully built, with the number.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** A proper name is a word that refers to an individual (Kripke; psycholinguistics: proper-name processing engages the anterior temporal referent system; Semenza). The brain's category decision for a capitalised or unknown word is PREDICTIVE: the discourse model's belief that a referent is an individual (seen before, singular, unique in context) re-enters the lexical competition as a prior (predictive coding, top-down from the referent system to the word-form/category level; Kuperberg & Jaeger 2016). Name the structure and the computation: log P(PROPN | word, context) += log-prior from the entity layer's resolved chains (this string, or a coreferent of it, was bound to an individual entity token before; count-based).
> 2. **REUSE.** `hdlab/lexical_categories.py` (`_log_emit`: one additive log-prior term is the same shape as every cue landed by pri 99 -- see its patch), `hdlab/induced_categories.py`, the entity layer: `hdlab/online_entity_cluster.py`, `hdlab/crosstype_live_adapter.py` (the name bridge), `hdlab/commonnoun_binder.py`, the reader's entity tokens in `hdlab/situation_reader.py` (object files; `sm.entities`), MINERVA-2 episodic traces (`hdlab/learner`), `notes/problems/a_word_never_seen_before_is_read_by_its_form_and_position_the_category_organ_mistakes_names_for_common_nouns/SOLVED.md` (section 12 path 1: the brief-ready text; the `<none>`/form-free counts).
> 3. **GENERALIZE.** Repeated mentions of an unknown capitalised word across a passage (second mention inherits the first's individual status), names with determiners (the Gateses, the Europeans, the MSM), lower-case names and acronyms (58 of the 163; form-free), and the reverse: a capitalised common noun at sentence start that the discourse treats as a kind.
> 4. **WALL -> DEEPER.** If the prior does not move the confusions, split by first vs repeated mention (a first mention has no chain; the prior can only act on repeats) -- report the share of the 163 that are first mentions; that share is a population fact and bounds the lever honestly.
> 5. **OPTIMIZE BY EXACT REPLICATION;** the prior's weight and the chain-confidence gate are SWEPT; the prior is counts from resolved chains.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Populations: UD-EWT test unseen words (1,882; PROPN<->NOUN 163 -> 154 with the pri 99 patch applied inside your cell; `experiments/exp_category_unknown_word_cues_v1.py` has the instrument), and GUM (the board's coref populations: common_noun_coref 0.5671, coref 0.4681 -- the name vs common-noun split is what they depend on; `experiments/exp_situation_model_qa_modern_v1.py --run`, 25 min); twin = the prior from shuffled chains; no-regress: overall category accuracy (0.9312 with pri 99's patch) and heads under own tags.
> 7. **ADJACENT.** Both board coref dimensions; the name bridge; report, do not edit.
> 8. **COMPLETION BAR.** PROPN<->NOUN confusions on repeated mentions down CI-separated with overall accuracy not down, twin at the floor, the board's common_noun_coref not down (report if up), knowledge as counts with an online observe path -- OR a numbered located negative (e.g. the first-mention share) naming the missing input.

**(PHASE DIAGRAM.)** Prior weight, chain-confidence gate, the mention window are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** This is a FEEDBACK path: the category decision feeds the entity layer and the entity layer feeds the category decision; build it as the brain does (a prior at the NEXT mention, never a same-token loop), and say with counts where the first pass errs.

## 1. THE PROBLEM IN PLAIN LANGUAGE
Whether a capitalised word is a name is not written in its letters: "the Europeans" is a name and "the employees" is not. What tells a reader is whether the passage already treats that thing as a particular individual. Today the reader decides the word's kind first and only later works out who it refers to; people let the second inform the first on the next mention. We want that feedback as a learned prior.

## 2. WHY THIS ONE
It is the only path the measurements say reaches the missed third of name/common-noun errors, and those errors feed the two weakest board abilities (who is who; which common noun refers to whom).

## 3. MEASURED vs INFERRED
- **MEASURED (pri 99, 2026-09-13):** PROPN<->NOUN 163 -> 154 with six form cues; floor of 144 across 25 arms; 58/163 form-free; capitalisation oracle precision 0.812 / recall 0.658.
- **INFERRED (prove with a number):** a referent-chain prior on repeated mentions removes a third or more of the remaining confusions with no accuracy cost.

## 4. ALREADY TRIED / DO NOT REDO
Every form cue in pri 99 (graded suffix parse, finer shape alphabet, position-aware capitalisation, Katz determiner presence, frame words, productivity stratum); the determiner-IDENTITY rule (makes it worse: names take determiners).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read IN FULL: `notes/problems/a_word_never_seen_before_is_read_by_its_form_and_position_the_category_organ_mistakes_names_for_common_nouns/SOLVED.md`, its `lexical_categories_patch.diff`, `hdlab/lexical_categories.py`, `hdlab/online_entity_cluster.py`, `hdlab/crosstype_live_adapter.py`, `hdlab/situation_reader.py` (entity tokens), `notes/BRAIN_MATH_REFERENCE.md` (entity tokens + lexical-category rows), `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md`.

## 6. THE BAR (can-fail)
See checklist item 8.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_entity_to_category_prior_v1.py` (must use `experiments._seed_checkpoint.get_output_dir`), `notes/problems/<slug>/SOLVED.md`, `notes/problems/<slug>/entity_to_category_patch.diff` (do NOT edit hdlab/ directly -- strategy lands it), candidate assets under `data/hook_state/` only. Commit PATH-LIMITED, never push, never `git add -A`.

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT use spaCy / nltk / any NER or supervised tagger at inference. Do NOT read gold coreference while learning (the board's GUM gold is the ruler only).
