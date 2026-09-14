---
priority: 109
slug: the_boards_coref_split_reads_the_gold_category_column_and_the_readers_entity_qa_finds_no_nameable_person_cluster_make_the_entity_instruments_gold_free
status: OPEN
review:
review_text:
---

# PROBLEM: the two board rows that measure the entity layer are not measuring the live system -- the board's coref / common-noun split reads the GOLD category column (a gold peek), and the reader's own entity question instrument finds no nameable person cluster (0 questions, every floor 0.0) -- so the entity layer, the next front, has no honest instrument.

**slug:** `the_boards_coref_split_reads_the_gold_category_column_and_the_readers_entity_qa_finds_no_nameable_person_cluster_make_the_entity_instruments_gold_free` -- **opened:** 2026-09-14 03:55 by strategy from pri 104's instrument audit (SOLVED.md sections 11b and 12f) and the coref-QA witness diagnosis (ledger 2026-09-14 03:05).

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** For an INSTRUMENT the question becomes: what does the live system actually know at decision time? -- the instrument may read only that.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- and every INSTRUMENT must be gold-free at decision time: gold is the answer key, never an input. The UD/GUM treebank is a MEASURING instrument only.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** the name-vs-common decision belongs to the category organ (`hdlab/lexical_categories.py`, PROPN posterior); pri 104's forward wire (`coref_forward_wire_patch.diff`) routes `coref.name_content_tokens` to it. Do not add a second decider.
> **WALL-PUSH PROTOCOL:** before writing wall / ceiling / negative, read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md`.
> **A rigorous negative is a PASS** only if what failed was the brain's mechanism, faithfully built, with the number.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** The reader types a mention (name / common noun / pronoun) from its own category belief and its entity files; the board must score that. Today `experiments/gum_coref._mention_type` branches on `head_tok.upos` = `cols[3]` of the GUM CoNLL-U = the GOLD category column, so the `coref` and `common_noun_coref` rows are scored with a gold split the live reader never has. Measured by pri 104 (GUM, same items): gold split coref 0.4681 / common-noun 0.5671; the live reader's capitalisation rule 0.4709 / 0.5636; the category organ (gold-free) 0.4646 / 0.5764; with pri 104's prior 0.4658 / 0.5760. The fix is the gold-free split read from the category organ's posterior (the same structure the rest of the board reads through `hdlab.frontend`).
> 2. **REUSE.** `experiments/gum_coref.py` (`_mention_type`), `experiments/exp_board_coref_gum_v1.py` and the common-noun arm, `hdlab/frontend.py` (Tagger.tag_with_posterior), pri 104's `coref_forward_wire_patch.diff` (the 8 organs' decider) and its harness in `experiments/exp_entity_to_category_prior_v1.py` (reproduces 0.4681 / 0.5671 exactly and runs the four deciders); for the reader-side instrument: `experiments/exp_situation_model_qa_v1.py` (`build_coref_questions`, `_named_clusters`, `_cluster_name`), `hdlab/situation_reader.py` `_build_entities` / `_read_entities` / the entity layer flags (`referent_per_np` default True, `unified_referent` False, `online_entity_cluster` default-on since 09-09, the 09-11 coref consolidation), `verification/test_situation_model_qa.py::test_coref_which_entity_beats_the_strongest_rereading_floor` (last green 2026-09-07).
> 3. **GENERALIZE.** Every board arm that reads a gold column at decision time must be found and listed (grep `cols[3]`, `upos`, `xpos`, `deprel` reads in `experiments/gum_coref.py`, `exp_board_*`, the who-did-what arms); each becomes gold-free or is marked INFORMATIONAL.
> 4. **WALL -> DEEPER.** If the gold-free coref row drops, that drop is the TRUE live number and the repair is the entity layer's name decision (pri 104's wire), never the instrument; report both.
> 5. **OPTIMIZE BY EXACT REPLICATION;** no thresholds beyond the category organ's own argmax/posterior mass (sweep the mass if a graded typing is used).
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Publish the board's coref and common-noun rows gold-free (with pri 104's wire OFF and ON), CI per row, floors recomputed gold-free; for the reader-side instrument: on the 8 LitBank docs the question builder must again find nameable person clusters -- diagnose WHY every is_person cluster under default flags holds only pronoun mentions (13 persons, 0 with surface heads; with referent_per_np=False 32 persons / 20 with heads but still 0 questions) and whether the name mentions' clusters (negative ids) are the entity layer's singletons that should have merged; fix in the entity layer if the reader is wrong, in the instrument if the instrument is stale.
> 7. **ADJACENT.** pri 104's two diffs (entity prior; forward wire) land through strategy with a board A/B -- the A/B is only meaningful once the split is gold-free; pri 108 (labels rung) and pri 106 (role margin) are independent.
> 7b. **THE WIRE ITSELF (added 2026-09-14 04:10).** pri 104's `coref_forward_wire_patch.diff` is LANDED in `hdlab/coref.py` as an additive capability (`name_content_tokens(span_toks, upos=None)`; byte-identical without `upos`) -- but NONE of the ten call sites passes categories yet: `coref.py:435`, `coref_distractor_suppress.py:296`, `crosstype_live_adapter.py:140`, `entity_resolver.py:235`, `event_centrality_coref.py:442`, `gender_organ.py:72`, `lexical_utils.py:105`, `online_entity_cluster.py:129`, `scene_segment.py:410`, `unified_referent.py:162`. Wiring = every mention dict carries `span_upos` (the category organ's tags for the span, from the reader's `_cached_tag` at mention-building time in `parse_litbank_conll` / `_read_entities` / the referent-per-NP source) and each call site passes it; measure the reader's coref / common-noun / salience through the GOLD-FREE rows (item 8c) and the entity QA instrument; HDLAB_NAME_SOURCE=caps is the regression arm.
> 8. **COMPLETION BAR.** (a) The board's coref and common-noun rows read NO gold column at decision time (a grep-level witness + a twin: scrambled gold column leaves the rows byte-identical), with the new floors and the live number published and the old numbers retired in `notes/reference_retired_claims_never_requote.md`; (b) `test_coref_which_entity...` green again with the question builder finding >= the 09-07 count of questions on the 8 docs, OR a numbered located negative naming the entity-layer change that emptied the person clusters; (c) pri 104's forward wire measured through the gold-free rows (up, down, or neutral with CI -- reported either way).

**(PHASE DIAGRAM.)** The posterior mass used for typing a mention is FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Tokens -> categories (PROPN posterior) -> mention typing -> entity files -> coref / common-noun resolution -> the board rows. Report where the live chain loses against the gold split, rung by rung.

## 1. THE PROBLEM IN PLAIN LANGUAGE
Two of the seven scores on the board measure how well the system keeps track of who is who. It turns out the scorer quietly reads the answer key to decide which words are names, so the board has been grading the system with help it never has when it reads. Fixing that changes those two numbers (one goes slightly down, one up), and only then can today's new name-detector show its effect. Separately, the test that asks the reader "who does 'she' refer to" has been silently asking zero questions since about 9 September, because the reader's person files no longer carry the names themselves.

## 2. WHY THIS ONE
The owner named the entity layer the next front; the board's two entity rows and the reader's own entity test are its instruments, and both are broken in ways that hide real movement (pri 104's wire, worth +0.117 span F1, cannot show on the board as built).

## 3. MEASURED vs INFERRED
MEASURED: the four-decider table above (pri 104, GUM, same items); 13 persons / 0 heads / 0 questions on 1023_bleak_house under default flags, identical under the supervised stack (strategy 03:00). INFERRED: which 09-09..09-11 change emptied the person clusters -- bisect it.

## 4. ALREADY TRIED / DO NOT REDO
Reading the split from capitalisation (`coref.name_content_tokens`: F1 0.672, 1,331 false names); the entity prior as a board lever (neutral by construction while the split is gold).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read in full: `experiments/gum_coref.py`; pri 104's SOLVED.md sections 11 and 12f and its `coref_forward_wire_patch.diff`; `experiments/exp_situation_model_qa_v1.py` (questions + naming); `hdlab/situation_reader.py` `_build_entities`, `_read_entities`, `_apply_commonnoun_gate`; `verification/test_situation_model_qa.py`; the ledger rows of 2026-09-14 03:05.

## 6. THE BAR (can-fail)
See checklist item 8. Floors recomputed gold-free; paired bootstrap over items; the scrambled-gold-column twin must leave the gold-free rows byte-identical.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_entity_instruments_gold_free_v1.py` (your cell), `notes/problems/<slug>/{SOLVED.md, gum_coref_gold_free_patch.diff, entity_layer_patch.diff}` (unified diffs against `experiments/gum_coref.py` / the board arms and, if the reader is at fault, `hdlab/situation_reader.py`). Never edit hdlab/ or tools/ directly; the board experiment files are strategy's to patch on integration.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md` (the gold-split 0.4681 / 0.5671 join it once the gold-free rows publish). 19c numbers are informational only.
