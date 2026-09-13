---
priority: 99
slug: a_word_never_seen_before_is_read_by_its_form_and_position_the_category_organ_mistakes_names_for_common_nouns
status: OPEN
review:
review_text:
---

# PROBLEM: one word in thirteen has never been seen by the category organ; it gets those right 75 times in 100, and a third of its misses are NAMES read as common nouns (or the reverse) -- the cues a reader uses for an unseen word (its form, its capitalisation RELATIVE TO POSITION, its determiner, its ending, what it is coordinated with) are only partly built

**slug:** `a_word_never_seen_before_is_read_by_its_form_and_position_the_category_organ_mistakes_names_for_common_nouns` -- **opened:** 2026-09-13 by strategy from the unknown-word profile of the live category organ (UD-EWT test, 25,094 tokens: 1,882 unseen tokens, accuracy 0.7519; by shape: lower 0.760 (n=734), Capitalised 0.783 (585), digit 0.776 (281), other 0.657 (143), ALL-CAPS 0.597 (119); gold classes of the unseen words: PROPN 760, NOUN 538, NUM 204, VERB 153, ADJ 126; top confusions PROPN->NOUN 117, NOUN->PROPN 46, ADJ->NOUN 32, PROPN->NUM 30, NOUN->NUM 25, PROPN->ADJ 24, VERB->NOUN 23).

> ## SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Name the structure and the computation; replicate the OPERATION, sweep the PARAMETERS (never adopt a number).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** — spaCy / any off-the-shelf parser / treebank-trained model at inference is a DEFECT; the UD treebank is a MEASURING instrument only (its trees are never read while learning).
> **🧩 ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** this is an extension of the ATTACHMENT arm of the Competition-Model organ (`hdlab/attachment_arm.py`; sibling arm `hdlab/graded_role_assigner.coarse_roles`). Do NOT mint a new organ; propose the change as a patch + probe, strategy lands it.
> **PLASTIC, NEVER FROZEN:** knowledge = counts in the asset; strengths = one pure function of counts; an online `observe_*` path must exist for anything you add.
> **🧱 WALL-PUSH PROTOCOL:** before writing wall / ceiling / negative, read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md`. A wall = an upstream trace + a stronger brain build, else a SPECIFIC board question.
> **A rigorous negative is a PASS** only if what failed was the brain's mechanism, faithfully built, with the number.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** How does a reader categorise a word never met before? From its FORM (endings and orthographic shape: Rastle-Davis morpho-orthographic segmentation; capitalisation as a name cue -- but ONLY where capitalisation is not forced by the convention, i.e. not sentence-initially; readers know the convention), from its SLOT (the determiner and the neighbouring categories -- the distributional frame, Mintz 2003; a bare capitalised word after a preposition is a name, 'the X' is a common noun), and from PARALLELISM (a word coordinated with a name is a name). Name the structure: the visual word-form system feeding a category competition; the cue validities are counts.
> 2. **REUSE.** `hdlab/lexical_categories.py`: `_log_emit_unknown` (suffix channels 1-4 letters + shape), `word_shape` (lower / Cap / ALLCAP / digit / hyphen / other -- POSITION-BLIND: a sentence-initial 'Cap' and a mid-sentence 'Cap' are the same symbol), the reading-acquired cluster cue (`induced_categories`, covers only words the 1M lines showed), the second-order transitions, the fixed-lag revision (lag 2); `hdlab/induced_categories.py` (the acquisition arm). Do NOT mint a new organ.
> 3. **GENERALIZE.** Names (people, places, products: 'Gmail', 'Chand', 'Falluja'), acronyms ('AMS', 'EWS', 'MSM' -- ALL-CAPS is the worst shape), codes and dates ('E17', '01-Feb-02', 'EB3326' -> NUM vs NOUN vs PROPN), file names and web noise ('Guaranty.doc', 'b/c', 'tonite'), and ordinary unseen common nouns/verbs/adjectives (the lower-case 734: 0.760 -- endings and slot).
> 4. **WALL -> DEEPER.** If position-aware capitalisation does not move PROPN/NOUN, split the residual by determiner presence and by sentence position; a residual dominated by web noise (codes, file names) is a population fact -- report it with counts, do not chase it.
> 5. **OPTIMIZE BY EXACT REPLICATION;** the shape-by-position factor is a count table like the others (P(shape, position | c)); smoothing swept; no number adopted.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Full UD-EWT test (25,094 tokens; `experiments/_diag_category_lag.py` prints overall + unknown accuracy at lag 2 = the live default): overall 0.9278 and unknown 0.7519 are the floors; report by shape class and the PROPN/NOUN confusion counts; twin = shuffled shape/suffix tables; also the Penn arm (`lexical_categories_counts_penn_v1.json`, 0.9176) since the temporal organ reads it. DOWNSTREAM: the heads rung under the organ's own tags (`experiments/probe_heads_under_category_posterior_v1.py`, 0.598) and the board's common_noun_coref (0.5671) / coref (0.4681) dimensions, which depend on the name vs common-noun split (`experiments/exp_situation_model_qa_modern_v1.py --run`, a 25-minute board).
> 7. **ADJACENT.** The name/common-noun decision feeds the entity layer (name bridge, common-noun binder, coref). Do not edit consumers; report which board dimension moves.
> 8. **COMPLETION BAR.** Unknown-word accuracy up CI-separated (paired bootstrap over sentences) with overall accuracy not down, PROPN<->NOUN confusions down by a third or more, twin at the floor, knowledge as counts with the existing online observe path -- OR a numbered located negative naming the missing input (e.g. the web-noise share).

**(PHASE DIAGRAM.)** Suffix length, the rare-word mixing kappa, the position split of the shape factor, the cluster cue's threshold are FREE TO SWEEP; a wall "at this config" = move the operating point.
**(FULL-STACK UPSTREAM.)** Tokenisation is upstream (codes and dates arrive as one token); the reading-acquired inventory is the organ's own acquisition arm -- growing its coverage (more reading) is a legitimate lever but must be measured on held-out words, not claimed.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When the reader meets a word it has never seen, it guesses the word's kind from its spelling and its neighbours. It guesses right three times in four. Its commonest slip is taking a name for an ordinary noun, or the other way round, especially for capitalised words and abbreviations. People use one more thing: they know a capital letter at the start of a sentence means nothing, while a capital in the middle of a sentence usually marks a name. We want that knowledge, and the determiner cue ('the' before a word says common noun), in the same learned competition.

## 2. WHY THIS ONE
Unseen words are 7.5% of all tokens and carry about a quarter of the organ's remaining errors; the name/common-noun split is exactly what the weakest board abilities (who is who across a passage; which common noun refers to whom) depend on.

## 3. MEASURED vs INFERRED
- **MEASURED (2026-09-13):** the numbers in the header (unknown 0.7519; PROPN->NOUN 117, NOUN->PROPN 46; ALL-CAPS 0.597; 'other' shape 0.657).
- **INFERRED (prove with a number):** a position-aware capitalisation cue plus the determiner/slot cue recovers a third or more of the PROPN<->NOUN confusions; the acronym class needs the ALL-CAPS shape split by length (2-4 letters = acronym).

## 4. ALREADY TRIED / DO NOT REDO
Shape as a position-blind factor (landed, 0.9165 -> live); rare-word mixing with the unknown estimate (landed); the reading-acquired cluster cue for rare/unknown words (landed, +0.0007); a blanket neighbour-word naive-Bayes channel (REFUTED 2026-09-13 14:35: 0.9152 at full weight; trades AUX/VERB errors) -- do not re-add neighbour words as independent emission channels.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read IN FULL: `hdlab/lexical_categories.py`, `hdlab/induced_categories.py`, `experiments/_diag_category_lag.py`, `notes/OVERNIGHT_PLAN_2026-09-12.md` (entries 07:15-07:50 and 14:24-14:45 local), `notes/BRAIN_MATH_REFERENCE.md` (lexical-category rows), `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md`.

## 6. THE BAR (can-fail)
See checklist item 8.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_category_unknown_word_cues_v1.py` (must use `experiments._seed_checkpoint.get_output_dir`), `notes/problems/<slug>/SOLVED.md`, `notes/problems/<slug>/lexical_categories_patch.diff` (do NOT edit hdlab/ directly -- strategy lands it), a candidate counts asset under `data/hook_state/` (never overwrite `data/frontend_assets/lexical_categories_counts_v1.json`). Commit PATH-LIMITED, never push, never `git add -A`.

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT use spaCy / nltk taggers / any supervised tagger at inference. Do NOT read the treebank's test split while learning.
