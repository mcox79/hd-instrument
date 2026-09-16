---
priority: 136
slug: the_readers_entity_clustering_is_the_numbered_pronoun_lever_262_of_1486_files_mix_two_gold_entities_and_a_gold_entity_oracle_adds_0_1168_ci_sep_build_the_file_merge_split_decision_as_a_cue_competition_with_online_validities
status: OPEN
review:
review_text:
---

# PROBLEM: with the pronoun pick's identity contract landed (pri 131: the pick scores the reader's own entity files, antecedent span returned, phi-weighted ACT-R retrieval), the identity basis is measured FREE (head-string 0.3263 == entity files 0.3263 on one code path) while a GOLD-ENTITY oracle for the same pick scores 0.4431 (+0.1168 CI-sep, 28 GUM docs, 795 fixed questions, abstention=wrong) -- so the remaining pronoun signal is the reader's ENTITY CLUSTERING: 262 of 1,486 files opened on those documents touch more than one gold entity (merged files) and aliases of one entity stay split; the clustering (`hdlab/entity_resolver.py::cluster`, the online same-head recency + the crosstype bridge's name links) decides merge/split by string coincidences and fixed licences -- build the merge/split decision as the ONE cue competition it should be (name identity, head-lemma identity, phi agreement, type compatibility from the entity-type spoke, the appositive/copular predication link, discourse recency and role prominence) with validities ACCRUED ONLINE from the reader's own confident decisions, measured against gold entity partitions (GUM) with the pronoun pick as the end consumer.

**slug:** `the_readers_entity_clustering_is_the_numbered_pronoun_lever_262_of_1486_files_mix_two_gold_entities_and_a_gold_entity_oracle_adds_0_1168_ci_sep_build_the_file_merge_split_decision_as_a_cue_competition_with_online_validities` -- **opened:** 2026-09-15 by strategy from pri 131's SOLVED.md (the oracle probe; next step 1) at its landing.

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** A new mention either updates an existing object file or opens a new one (Kahneman & Treisman object files; Heim's file-change semantics): the decision is a graded match of the mention's features against the open files -- identity of name, compatibility of type (a doctor can be 'she', not 'it'), agreement, and the discourse's current focus -- and the reader learns which cues are reliable from its own confirmed updates (the Competition Model's validity accrual, the same discipline as the attachment arm pri 117 and the role competition pri 108). A string coincidence is one cue among several, never the decision.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- spaCy, GLUCOSE, MAVEN and ANY off-the-shelf parser/dataset/model are NOT brain-foundational; an external tool AT INFERENCE is a DEFECT THAT BLOCKS; the entity-type spoke (`data/frontend_assets/entity_type_spoke_v1.sqlite`) is admissible offline supply.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** the object-file organ is `entity_resolver` (the reader's online clustering); the crosstype bridge's name links and the common-noun binder are ARMS feeding cues into its one competition, not competing clusterings; the pronoun pick (pri 131) reads its files.
> **DOWNSTREAM REGRESSION AFTER A BF UPSTREAM IS NOT FAILURE:** consumers of `sm.entities` (who-has-what, goals, affect, salience, the entity-KB path) are measured and repaired, never used to veto the competition.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** (a) Reproduce pri 131's oracle probe first-hand (its cell `experiments/exp_pronoun_pick_identity_contract_v1.py --identity-basis`): head-string == files, gold oracle +0.1168; then COUNT the clustering errors by type on the 28 docs against GUM gold entities: merged (two gold entities in one file: which cue merged them -- same head? same name? bridge link?), split (one gold entity across files: which cue was missing -- alias, pronoun-only file, type), with the pronoun questions each error costs. (b) Build the merge/split decision as a cue competition in `entity_resolver.cluster`: for each new mention, activation over open files = sum of cue x validity (name identity; head-lemma identity; phi compatibility (gender/number from pri 125's filled card); type compatibility (entity-type spoke, animate/inanimate, person/org/place); predication link (appositive/copular from the nonverbal-predication organ); recency and role prominence (Centering)); open a new file when no activation clears the accrued threshold; validities ACCRUED ONLINE from the reader's own high-margin decisions (an observe path; the pri 117 template), initialised from the teaching corpus (GUM train partitions as the admissible offline supply). (c) Route the crosstype bridge's name links and the common-noun binder's decisions as CUES into that competition (not as separate overrides).
> 2. **REUSE.** `hdlab/entity_resolver.py` (`cluster`, the licences at :538-545), `hdlab/coref.py` (`graded_pronoun_resolve` -- the consumer; pri 131's entity ids), `hdlab/referent_per_np.py` (the filled card), `hdlab/crosstype_bridge.py` + `crosstype_live_adapter.py`, `hdlab/commonnoun_binder.py`, `hdlab/typed_spokes.py` / the entity-type spoke, `hdlab/affected_entity_resolver.py` (`EntityTokens`, role prominence), pri 131's cell and SOLVED.md (the oracle; the 262/1486 count), pri 125's SOLVED.md §6 (the youtube flood: type compatibility is the missing cue), pri 118's SOLVED.md (the name-vs-common route), the entity-type KB lead (`acquire_wikidata_p31_entity_type_kb_for_name_bridge_coref`), witnesses `test_entity_resolver_unified.py`, `test_unified_referent_landing.py`, `test_entity_maintenance_chaining.py`, `test_coref_stack_landing.py`.
> 3. **GENERALIZE.** Every consumer of `sm.entities` / `_online_lab` reads the competition's files; the bridge and the binder no longer write cluster ids directly.
> 4. **WALL -> DEEPER.** If the competition merges what the gold splits (or the reverse) on a class of items, the missing cue is named with the items (expect: type knowledge for names, the entity-type KB lead) -- never a fixed licence list.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep the open-new-file threshold and the accrual rate only.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Entity partition quality vs GUM gold on the 28 docs (a partition metric, e.g. B-cubed / CEAF over the reader's files, all mentions counted) before/after; the pronoun instrument (795 questions, abstention=wrong) vs its floor and the gold oracle (the target: close the 0.1168 gap; report the fraction closed with CIs); the product board both arms one process (coref, common-noun, salience, who-has-what rows); read time.
> 7. **ADJACENT.** pri 131 (landed; the consumer), pri 134 (fine relations for the bridge), pri 125, the entity-type KB lead, pri 132 (the analysis object).
> 8. **COMPLETION BAR.** Partition quality up CI-sep on the 28 docs; the pronoun instrument up CI-sep with the fraction of the oracle gap closed stated; validities accrued with an observe path (twin at floor); consumers not down (or repaired with items); the board's coref row (after the answer-key fix) not down -- OR a numbered located negative naming the cue that cannot be had without new knowledge.

**(PHASE DIAGRAM.)** The open-new-file threshold and the accrual rate are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Tokens -> categories -> mentions (pri 125, the card) -> THIS object-file competition -> the pronoun pick (pri 131) / who-has-what / goals / affect / salience.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The pronoun step now looks up the right kind of thing (the reader's own file for each person or object), and we measured that the files themselves are the problem: one file in six mixes two different people, and some people are split across files. A perfect filing would add nearly 12 points to pronoun reference. Make the "same file or new file" decision a proper weighing of evidence (name, kind of thing, gender and number, recent focus) that the reader learns from its own confident decisions.

## 2. WHY THIS ONE
The largest numbered lever on the pronoun row, found with the identity variable isolated; it sits right above the pick and below the mention discovery that just landed.

## 3. MEASURED vs INFERRED
MEASURED (pri 131): head-string == files 0.3263; gold oracle 0.4431 (+0.1168 CI-sep); 262/1486 impure files. INFERRED: the error-type breakdown and the fraction of the gap a competition closes.

## 4. ALREADY TRIED / DO NOT REDO
Merging referents INTO the coref pool (refuted 2026-09-03); the fixed licence list; the 'she -> youtube' filtering (pri 125: unfixable by filters -- the cue is TYPE knowledge).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
(1) `python tools/substrate_map.py`; (2) read pri 131's SOLVED.md and cell, `hdlab/entity_resolver.py` in full, pri 125 §6, pri 118; (3) run the oracle probe first.

## 6. THE BAR (can-fail)
See checklist item 8. Floors: the clustering as shipped; twin: validities permuted; paired bootstrap over documents.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_object_file_competition_v1.py` (your cell; `get_output_dir` per Q115), `verification/test_object_file_competition.py` (NEW), `notes/problems/<slug>/{SOLVED.md, object_file_competition_patch.diff}` (unified diffs against `hdlab/entity_resolver.py`, `hdlab/crosstype_live_adapter.py`, `hdlab/commonnoun_binder.py`; never edit hdlab/ directly), the NEW validity asset under `data/frontend_assets/`.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. 19c numbers are informational only.
