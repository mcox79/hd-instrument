---
priority: 116
slug: the_reader_lowercases_every_token_at_its_one_sentence_source_so_the_category_organ_misses_70_percent_of_proper_nouns_on_the_live_path_flip_the_case_through_with_a_board_ab
status: OPEN
review:
review_text:
---

# PROBLEM: the live reader's ONE sentence source (`hdlab/scene_segment.parse_conll_sentences`, used by situation_reader, referent_per_np, space_reader and causation_typing) lowercases every token (`cols[3].lower()`), so the category organ reads case-stripped text: on 127,919 GUM test tokens, same organ, same text, case the only difference, PROPN precision/recall/F1 is 0.9050/0.8232/0.8622 CASED vs 0.9417/0.2996/0.4546 LOWERCASED (it misses 5,024 of 7,173 proper nouns, 70%), all-tag accuracy 0.9302 -> 0.9027 on EVERY token for EVERY reader consumer; it also silently kills the mid-sentence-capital cue of `referent_per_np.frame_heads` and `lexical_categories.word_shape`. pri 109 added `parse_conll_sentences(path, lower=True)` with the current default and passes it explicitly at the four hdlab call sites; the flip needs a board A/B and the consumer repairs it exposes.

**slug:** `the_reader_lowercases_every_token_at_its_one_sentence_source_so_the_category_organ_misses_70_percent_of_proper_nouns_on_the_live_path_flip_the_case_through_with_a_board_ab` -- **opened:** 2026-09-14 by strategy from pri 109's phase-7 finding (1) and pri 112's next-step 4 ('forty times anything in this brief').

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Orthographic case is a perceived cue (a word-shape feature the visual word-form system delivers); the comprehender never throws it away before deciding a category. Replicate the OPERATION, sweep the PARAMETERS.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- the category organ (`hdlab/lexical_categories.py`) already learns from cased text; feeding it lowercased text at read time is a train/read mismatch, not a design.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** the sentence source is ONE function; flip it there, then repair every consumer that had adapted to lowercase (lexicon lookups keyed on lowercase, string-identity coref, the name aliaser, the gazetteer), never by lowercasing again downstream of the category decision -- pass the CASED tokens to the organ and let each consumer lowercase for its own lookup where a lookup is case-insensitive by design.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.
> **DOWNSTREAM REGRESSION AFTER A BF UPSTREAM IS NOT FAILURE (owner 09-12):** keep the case ON, name the flips, repair the consumers to receive the richer signal; never revert to satisfy a no-regress gate.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Flip `lower=False` at the four call sites (situation_reader, referent_per_np, space_reader, causation_typing) so the category organ, the attachment arm and every organ below receive cased tokens; consumers that need case-insensitive keys (lemma lookups, lexicons, string identity for coref/aliasing) lowercase at THEIR lookup, not at the source. The category organ's own `word_shape` and the mid-sentence-capital cue then work as designed.
> 2. **REUSE.** pri 109's SOLVED.md phase-7 finding (1) and `entity_layer_patch.diff` (the `lower=` parameter and the four explicit call sites); `hdlab/scene_segment.parse_conll_sentences`; `hdlab/lexical_categories.word_shape` / `_unk_sym` / `position_class`; `referent_per_np.frame_heads`; the reader's `_cached_tag`; the coref stack's string-identity floor and `coref.name_content_tokens`; the gazetteer (`experiments/exp_name_entity_clustering_v1.load_given_gazetteer`).
> 3. **GENERALIZE.** Enumerate every consumer that compares or looks up token strings downstream of the sentence source (grep `.lower()` in hdlab/ along the read path and every dict keyed on tokens): classify each as case-insensitive-by-design (lowercase at its own lookup) or case-sensitive (leave cased); count how many read the organ's category vs the raw string.
> 4. **WALL -> DEEPER.** If a consumer regresses with cased input, it was reading the string where it should read the organ's category or the lemma -- repair it to the organ's output; report each such consumer with the count.
> 5. **OPTIMIZE BY EXACT REPLICATION;** no new parameters.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** The category organ on the live path: PROPN P/R/F1 and all-tag accuracy on GUM test (the 0.4546 -> 0.8622 F1 claim reproduced THROUGH the reader, not just at the organ); the entity layer (name typing count, pri 109's 150 vs 0 names on the reader's own stream), the coref / common-noun / salience board rows, the reader's entity-QA instrument (200 questions), the who-did-what rows, state; the board's 7 dimensions (`experiments/exp_situation_model_qa_modern_v1.py --run`, HDLAB_EXP_NAME set); every landing witness that pins a number (re-pins are strategy's; you report old vs new).
> 7. **ADJACENT.** pri 112 (the passage register; its file cards are keyed by surface type -- case changes the keys), pri 109 (entity instruments), pri 104 (the entity prior), pri 108 (labels).
> 8. **COMPLETION BAR.** The category organ's PROPN F1 through the live reader up CI-separated on GUM test (toward the 0.8622 measured at the organ), all-tag accuracy up; the entity layer's name typing live (>= 150 names typed on the reader's stream); the board's seven rows reported with CIs (up, down or flat -- a down row is repaired at its consumer, not by reverting the case); every string-keyed consumer classified; twin (random case per token) at floor -- OR a numbered located negative naming the consumer that cannot receive cased tokens and why.

**(PHASE DIAGRAM.)** Nothing to sweep; this is a hand-off repair.
**(FULL-STACK UPSTREAM.)** Text -> the sentence source (THIS) -> categories -> everything.

## 1. THE PROBLEM IN PLAIN LANGUAGE
Before the system reads a sentence, it turns every capital letter into a small one. The organ that decides what kind of word each word is was taught on normal text, where a capital is a strong hint that a word is a name; without capitals it misses seven names in ten. Every later step inherits that. The fix is to stop lowercasing at the source and let each later step lowercase only where it looks something up in a list that ignores case.

## 2. WHY THIS ONE
The largest single measured loss at the top of the chain (pri 109: 'more than double pri 104's wire, and it is one argument'), one line at one source, the parameter already landed; only the flip, the consumer repairs and the board A/B remain.

## 3. MEASURED vs INFERRED
MEASURED (pri 109, GUM test 127,919 tokens, at the organ): PROPN F1 0.4546 lowercased vs 0.8622 cased; all-tag 0.9027 vs 0.9302; tag agreement 0.9637. INFERRED: the size of the board movement and which consumers adapted to lowercase (pri 109's reader-faithful arm showed the common-noun row is an artefact-prone instrument for this; use the paired subpopulation).

## 4. ALREADY TRIED / DO NOT REDO
Restoring case only in `referent_per_np._mk_referent` (pri 109: recovers nothing, the case is gone one level up).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read in full: pri 109's SOLVED.md (phase-7 findings 1, 4, 8) and `entity_layer_patch.diff`; `hdlab/scene_segment.py`; `hdlab/lexical_categories.py` (word_shape, _unk_sym, position_class, the entity prior); `hdlab/situation_reader.py` `read()` / `_cached_tag`; `hdlab/referent_per_np.py`; `hdlab/coref.py`; pri 112's SOLVED.md (the register keys).

## 6. THE BAR (can-fail)
See checklist item 8. Floors: lowercase as shipped; twin: random case per token; paired bootstrap over tokens / items; the board run with and without.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_case_through_the_reader_v1.py` (your cell), `notes/problems/<slug>/{SOLVED.md, case_through_patch.diff}` (unified diffs against the four call sites and every consumer you repair; never edit hdlab/ or tools/ directly), and any NEW asset under `data/hook_state/`.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. 19c numbers are informational only.
