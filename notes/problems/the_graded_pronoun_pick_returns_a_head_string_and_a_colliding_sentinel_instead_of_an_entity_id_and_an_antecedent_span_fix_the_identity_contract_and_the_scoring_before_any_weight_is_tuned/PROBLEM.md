---
priority: 131
slug: the_graded_pronoun_pick_returns_a_head_string_and_a_colliding_sentinel_instead_of_an_entity_id_and_an_antecedent_span_fix_the_identity_contract_and_the_scoring_before_any_weight_is_tuned
status: OPEN
review:
review_text:
---

# PROBLEM: pri 125's graded pronoun pick (`hdlab/coref.py::graded_pronoun_resolve`, wired in `situation_reader._read_entities`) identifies candidates by `m["head"].lower()` (two doctors, two people with one name, or a repeated common noun share ONE history and ONE feature card; aliases of one entity stay separate) and returns a `resolved_head` string with `resolved_cluster=-1` as its sentinel -- while the reader's ONLINE entity ids are `-(cluster+1)`, so -1 IS the first live entity: `goal_register.make_canonicalizer` (`names.get(r.resolved_cluster)`) can canonicalise a goal owner to the first entity regardless of the chosen head, and `_read_world_state` (`rc >= 0`) drops every graded link -- and its scoring (D06) reports `coref_acc` 0 instead of unavailable on unannotated text, duplicates the main result as the single-sentence comparator, and credits a wrong same-head antecedent through document-wide head membership; fix the identity contract (a predicted ENTITY id from the reader's own clustering + the antecedent span + the candidate set + an abstention reason; a sentinel that is not a valid id) and the scoring (nullable outcomes; span/entity alignment; an executed comparator) BEFORE any retrieval weight is tuned.

**slug:** `the_graded_pronoun_pick_returns_a_head_string_and_a_colliding_sentinel_instead_of_an_entity_id_and_an_antecedent_span_fix_the_identity_contract_and_the_scoring_before_any_weight_is_tuned` -- **opened:** 2026-09-15 by strategy from the external deep review (`notes/SUBSTRATE_EVALUATION.md` D02, D05, D06, static on the pri 125 working tree) at the pri 125 landing; strategy's landing guard: the sentinel is changed to `None` (every live consumer is None-safe: `rc is not None and rc >= 0`; `names.get(None)` -> no canonicalisation) so the collision cannot bind a wrong owner while this brief is open.

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** A pronoun is resolved to a DISCOURSE ENTITY (a file card / object file: Kahneman-Treisman; Heim's file-change semantics), never to a word: two 'doctor' mentions are two files unless the reader has merged them; retrieval (ACT-R, Lewis & Vasishth) returns the FILE whose features match, and the mention that supplied the evidence is the antecedent span. The reader already keeps those files (`entity_resolver` online clustering, `EntityTokens`); the pick must score THEM.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- spaCy, GLUCOSE, MAVEN and ANY off-the-shelf parser/dataset/model are NOT brain-foundational; an external tool AT INFERENCE is a DEFECT THAT BLOCKS.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** the identity basis is the reader's ONE online entity clustering (`entity_resolver` / the unified referent); the graded pick is a retrieval ARM over it, not a second identity system keyed by strings.
> **SCORE THE PRODUCT FIRST; WITNESSES PIN CLAIMS, NOT NUMBERS** (README 2026-09-15): scoring outcomes are nullable and live OUTSIDE the inference result; abstention, unscoreable and wrong are three different things.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` before writing wall / ceiling / negative.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** (a) The contract: `CorefResolution` carries `resolved_entity` (the reader's online entity id, the `-(cluster+1)` scheme or better a stable per-read entity id), `antecedent_span` (sent_idx, wtok_start, wtok_end), `candidates` (entity id -> score), `abstain_reason` (None | no_candidate | no_compatible | tie), and `resolved_cluster` becomes `None` when unresolved (never a valid id); every consumer (goal canonicaliser, world state densify, affected-entity, belief when D04 lands) reads `resolved_entity`. (b) The pick scores ENTITIES: candidate = a file the reader has opened (via `_coref_mentions` -> entity clustering), features = the file's card (gender/number/name_gender accrued over its mentions, pri 125's fill), history = the file's mention times/roles; keep pri 125's graded ACT-R sum, only the KEY changes. (c) Scoring: `_gold_alignment` None when no annotations -> `coref_acc` None and `_coref_unscoreable` set in BOTH branches; alignment by antecedent SPAN/entity (a wrong same-head antecedent scores wrong); the single-sentence comparator EXECUTED (or omitted and labelled); counts published: discovered pronouns / attempted / abstained / scoreable. (d) Same-clause exclusion for ordinary pronouns (Principle B, the real clause-mate relation from the reader's parse; pri 125's proxy cost -0.104) and the number cue's weight swept from its current 0.
> 2. **REUSE.** `hdlab/coref.py` (`graded_pronoun_resolve`, `discovered_pronoun_targets`, `_gold_alignment`), `hdlab/situation_reader.py` (`_read_entities` ~:1900-1990, `_read_world_state` ~:2946, the entity id scheme ~:4735), `hdlab/entity_resolver.py` (`cluster`, id 0 first), `hdlab/goal_register.py:696-750`, `hdlab/affected_entity_resolver.py` (`EntityTokens`, `coarg_head_gidx`), pri 125's SOLVED.md §6b-6c and its cell's pronoun instrument (28 GUM docs, n=795: the fixed question set with abstention=wrong is the measure), pri 122's reader-driven coref row.
> 3. **GENERALIZE.** Every consumer of `resolved_cluster` / `resolved_head` on the live path (grep) reads the entity id; a witness with two same-head entities and a name+alias entity.
> 4. **WALL -> DEEPER.** If entity-keyed retrieval loses against head-keyed on the pronoun instrument, the loss is in the reader's CLUSTERING (files wrongly merged/split) -- name it with items; never return to the string key.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep the number-cue weight and the accessibility window only.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** The pronoun instrument (28 GUM docs text-only, fixed questions, abstention=wrong; floor nearest-prior-compatible; phi twin) before/after; the goal and world-state witnesses (canonical owner, possession holder) on paired cases from D02's acceptance list; the product board's coref row (pri 122 instrument) both arms one process; annotation invariance kept.
> 7. **ADJACENT.** pri 125 (landed), pri 132 (the document-analysis object: D01/D03/D04/D07/D08), pri 122, the entity-type KB lead (she -> youtube).
> 8. **COMPLETION BAR.** Two same-head entities stay distinct through reference, goals and belief (witness); a wrong same-head antecedent scores wrong; unannotated text reports accuracy unavailable with the four counts; no valid id used as a sentinel; the pronoun instrument not down (or the clustering loss named with items); the coref board row not down -- OR a numbered located negative.

**(PHASE DIAGRAM.)** The number-cue weight and the accessibility window are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Tokens -> categories -> mentions (pri 125) -> ENTITY FILES (clustering) -> THIS retrieval -> goals / world state / belief / the board's coref row.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The new pronoun step answers with a word ("doctor") instead of with the particular person or thing the reader has on file, so two different doctors are one candidate, and its "no answer" code happens to be the same number as the first thing on file, so a later step can hand a goal to the wrong owner. Its self-scoring also says "0 right" on plain text where it should say "cannot be scored". Make it answer with the file and the exact earlier mention, use a no-answer code that cannot be mistaken for a file, and score honestly.

## 2. WHY THIS ONE
It sits directly under the product board's coref row and above goals, world state and belief; tuning any retrieval weight before the identity is right would be tuning noise.

## 3. MEASURED vs INFERRED
MEASURED (D02/D05/D06 static, verified by strategy at the landing): the sentinel/id collision (`-(cluster+1)`, id 0 first), the head-string key, the scoring branches. INFERRED: the accuracy effect of entity-keyed retrieval (the instrument decides).

## 4. ALREADY TRIED / DO NOT REDO
Treating -1 as the first entity by special case (the reviewer's warning); tuning weights on the string-keyed pick.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read `notes/SUBSTRATE_EVALUATION.md` D02, D05, D06 and their acceptance cases; pri 125's SOLVED.md in full; the files in item 2; run pri 125's cell `--self-test` and its pronoun instrument once to have the baseline in hand.

## 6. THE BAR (can-fail)
See checklist item 8. Floors: the string-keyed pick as landed; the nearest-prior-compatible referent; twin: phi permuted (both tables).

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_pronoun_pick_identity_contract_v1.py` (your cell; `get_output_dir` per Q115), `verification/test_pronoun_pick_identity_contract.py` (NEW, pytest-collectable + standalone), `notes/problems/<slug>/{SOLVED.md, pick_identity_contract_patch.diff}` (unified diffs against `hdlab/coref.py`, `hdlab/situation_reader.py`, `hdlab/goal_register.py`; never edit hdlab/ directly).

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. 19c numbers are informational only.
