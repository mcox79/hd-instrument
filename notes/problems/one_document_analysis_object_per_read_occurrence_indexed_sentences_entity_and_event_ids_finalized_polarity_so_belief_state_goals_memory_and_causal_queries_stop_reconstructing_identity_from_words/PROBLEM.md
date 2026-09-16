---
priority: 132
slug: one_document_analysis_object_per_read_occurrence_indexed_sentences_entity_and_event_ids_finalized_polarity_so_belief_state_goals_memory_and_causal_queries_stop_reconstructing_identity_from_words
status: OPEN
review:
review_text:
---

# PROBLEM: downstream consumers of one read lose information an upstream organ already produced because they reconstruct identity from WORDS instead of reading one shared analysis -- (D01) polarity is attached LAST in `read()` and state folding, goal realisation and bound event memory reduce events to predicate/agent/patient so "did not give" updates possession like "gave"; (D03) the reader caches category posteriors, tags and parses under `tuple(sentence_tokens)` while the lexical register keys the FIRST occurrence, so a repeated sentence in a new context is served the other occurrence's result; (D04) belief queries receive an EMPTY mention map (`by_sent = {i: []}`) and run their own tag/parse extraction through `space_reader._frontend` (a private PosTagger + ArcParser), so the discovered mentions and the reader's events never reach belief; (D07) causal queries key the graph on the rightmost lowercased word, merging distinct occurrences of one verb and dropping a link between them as a self-edge; (D08) the joint frontend tags an over-160-token sentence once PER TOKEN and its marginal cache is never cleared -- build ONE document-analysis object per read (a read id; occurrence-indexed sentence analyses; predicted entity ids; event ids tied to source spans; finalised truth status and modality BEFORE stateful consumers) and make every consumer read it.

**slug:** `one_document_analysis_object_per_read_occurrence_indexed_sentences_entity_and_event_ids_finalized_polarity_so_belief_state_goals_memory_and_causal_queries_stop_reconstructing_identity_from_words` -- **opened:** 2026-09-15 by strategy from the external deep review (`notes/SUBSTRATE_EVALUATION.md` D01, D03, D04, D07, D08 and 'Opportunities beyond individual fixes' 1-5).

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** The brain builds ONE situation model per discourse (Zwaan & Radvansky; the event-indexing model: entities, events, time, space, causation indexed on the SAME tokens/episodes), and every later judgement (belief, cause, goal outcome, memory) reads that model; a negated event is encoded as a negated event (Kaup et al.: the negated state is simulated then rejected), never as the affirmative; a repeated sentence is a new EPISODE at a new time (hippocampal indexing is occurrence-bound). Our organs already compute each piece; the defect is that consumers re-derive identity from surface words instead of reading the shared model.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- the belief path's private PosTagger/ArcParser (supervised stand-ins) is a pri 129-class defect: route belief through the reader's own categories/heads. **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** the document analysis IS the SituationModel; consumers are arms over it, not second readers.
> **DOWNSTREAM REGRESSION AFTER A BF UPSTREAM IS NOT FAILURE:** when a consumer moves from word keys to ids, its old number may drop; repair the consumer, keep the ids.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` before writing wall / ceiling / negative.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** (a) Define the object on `SituationModel`: `read_id`; `sentences[i]` = occurrence-indexed analysis (tokens, cased; category posterior; heads; the register time); `mentions` (pri 125's discovered stream with entity ids); `entities` (the reader's online files); `events[k]` with `event_id`, source span, polarity/modality FINALISED before any stateful consumer; `links` (causal/temporal) over event ids. (b) D01: move `_read_polarity` (and modality: desired/hypothetical/reported) BEFORE `_read_world_state`, goal realisation and `BoundEventBackbone.build`, and make those consumers CONSUME it (asserted / negated / unknown handled explicitly; run D01's acceptance pairs). (c) D03: key the per-read caches by (read_id, sentence occurrence), keep a text-only cache ONLY for computations proven context-independent (say which). (d) D04: `_read_belief` receives the object (mentions + entity ids + events + the reader's parse) and `belief_reader` drops its private frontend; bounded, documented cost per query. (e) D07: the causal graph over event ids with verb labels as attributes; a query resolves to ids and exposes ambiguity. (f) D08: one tagging call in the long-sentence fallback; parse + marginal caches cleared together; long-sentence omission visible as coverage. (g) THE BELIEF PATH'S TIME CONTRACT (follow-up review 2026-09-15, R05/R06/O01, reproduced in isolation): `belief_reader.drive` keys observations by (agent, float(sentence_index)) so two events in one sentence overwrite each other and ties resolve to the first -- key by EVENT OCCURRENCE (event id / within-sentence position) and give each its own timestamp; `PerceptualAccessLedger._informed_after` converts LATER testimony into an observed flag attached to the event's ORIGINAL time (an absent agent appears informed earlier) -- knowledge acquired at time t2 is recorded AT t2, never back-dated; `led.observed` re-parses the whole passage per event per query (12 parses for 4 sentences x 3 events, repeated on the next query) -- parse once into the object and answer from it, caching belief timelines under explicit read/config keys after R05/R06 are fixed. Acceptance: the review's isolated fixtures (kitchen-then-garden in one sentence; testimony after absence) become witnesses, plus raw-text integration checks once the object lands.
> 2. **REUSE.** `hdlab/situation_reader.py` (`read()` order ~:4500-4990, `_read_polarity`, `_read_world_state`, `_read_belief`, `_read_causal_reasoning` ~:3723, `_read_predictive_causal` -- the absolute-event-index precedent), `hdlab/world_state_register.py:175`, `hdlab/goal_register.py:413,548`, `hdlab/bound_event_backbone.py:124,230`, `hdlab/belief_reader.py:107,158,422`, `hdlab/space_reader.py:222,287` (pri 125's `mentions=` hand-off is the template), `hdlab/joint_relation_frontend.py:55,115,801`, `hdlab/lexical_categories.py:339,358,748` (the register's occurrence key), pri 112's SOLVED.md (the in-order feed), pri 129's SOLVED.md (routing consumers off private frontends).
> 3. **GENERALIZE.** Boundary witnesses (pytest-collectable): positive/negative action pair through state + goals + memory; two entities sharing a name; a repeated sentence after new context (both occurrences keep their own posterior and time); a correct pronoun followed by a state update; two causal events with the same verb; parser-call counts per read and per belief query.
> 4. **WALL -> DEEPER.** If a consumer's number drops when it reads ids, the loss is a consumer that relied on a word coincidence -- name the items, repair the consumer.
> 5. **OPTIMIZE BY EXACT REPLICATION;** nothing to sweep.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** The product board (pri 122 rows, both arms one process); the belief / goal / world-state / causal witnesses; read time and parser-call counts before/after; `memory_roundtrip` measured on the FINAL representation as well as the early snapshot (opportunity 5).
> 7. **ADJACENT.** pri 131 (the pick's identity contract -- land first; this brief consumes its entity ids), pri 129 (private frontends), pri 125, pri 122.
> 8. **COMPLETION BAR.** The object exists and every named consumer reads it; D01/D03/D04/D07/D08's acceptance cases pass as witnesses; the belief path makes zero private tagger/parser calls; the board not down (or the consumer repair named with items) -- OR a numbered located negative per consumer.

**(PHASE DIAGRAM.)** Nothing to sweep.
**(FULL-STACK UPSTREAM.)** Tokens -> categories -> mentions -> entities / events (THE OBJECT) -> state, goals, memory, belief, causal, space.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The reader works out who is who, what happened and whether it happened, but several later steps throw that away and match on words again: "did not give" can update who owns the book as if it were given; a repeated sentence can be served the wrong context; the belief tracker never sees the pronouns the reader found; two different "left" events become one. Give every step the same finished picture of the passage and make them read it.

## 2. WHY THIS ONE
The outside review's main concern; each item is a locally correct answer becoming a wrong world update; the fix is one shared object, which is also what the brain keeps.

## 3. MEASURED vs INFERRED
MEASURED (static, D01-D08 with file:line): the contracts and orders named above. INFERRED: the accuracy effect (the acceptance cases and the board decide).

## 4. ALREADY TRIED / DO NOT REDO
Per-consumer alias lists and word-level special cases; a second reader inside a consumer.

## 4b. MEASURED REQUIREMENT ADDED 2026-09-16 06:23 (pri 139, confirmed with counts): ONE ID SPACE FOR EVERY CONSUMER

`hdlab/situation_reader.py:4920-4924` re-files NON-pronoun mentions under NEGATIVE online file ids (`-(file+1)`) while pronoun mentions keep their POSITIVE coref-column ids: on 3 GUM documents 744 nominal mentions are all negative, 345 pronoun mentions all non-negative, 0 of 345 shared (25/201/0, 188/129/0, 132/151/0 per document). Any consumer that binds an entity across a name -> pronoun boundary through `m["cluster"]` therefore gets NOTHING by construction: the belief organ's entity binding is dead on the live path (pri 139: `by_cluster = 0` in every cell of its hand-off experiment, with 48 of 50 copular subjects mention-covered), and the same convention already dropped every graded reference link once (deep review D02, `densify_world_state`'s `rc >= 0` test). The gold-free join field that already exists is `resolved_entity` (pri 131's identity contract; pri 136's object files); `resolved_cluster` is gold-derived (pri 109) and cannot be a landed join on annotation-free text. THE ANALYSIS OBJECT MUST CARRY ONE ENTITY ID PER MENTION, pronoun and nominal alike, from the object-file organ, and every consumer (belief, space via pri 137's union, goals, affect, salience, the bridge) reads THAT id -- the negative/positive split is retired. Measure: the belief binding rate (0 today), the space where-is (pri 137's union is the same join done locally: 0.0426 -> 0.4043), and the entity-set row, before/after.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read `notes/SUBSTRATE_EVALUATION.md` D01-D08 and 'Opportunities' in full; `read()` end to end; the files in item 2; pri 131's SOLVED.md when landed.

## 6. THE BAR (can-fail)
See checklist item 8.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_document_analysis_object_v1.py` (your cell; `get_output_dir` per Q115), `verification/test_document_analysis_boundaries.py` (NEW), `notes/problems/<slug>/{SOLVED.md, document_analysis_patch.diff}` (unified diffs against the hdlab files named in item 2; never edit hdlab/ directly).

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. 19c numbers are informational only.
