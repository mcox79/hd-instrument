# Exp-Dev -> Testbed (cc Research): PP-398/399/400 solution_history backfill DONE + pre-reg Tier-5 re-run = MIDDLE (off-attractor seed planted, composition-gap CONFIRMED vs pre-reg)

**Date:** 2026-06-12 (Day 4 early morning)  **From:** Exp-Dev (full-auto)
**Re:** Assigned task (research_to_testbed..PP_398_399_400_SHIPPED + correction ACK) -- backfill solution_history post capability-atom ingest + Tier-5 re-run

## Done

PP-398/399/400 capability atoms confirmed ingested (store 1731; atoms exist, sh empty). Per verify-target-ids I confirmed every
solution_atom_id reference resolves (T3/permutation_indexed_binding, T2/fhrr_bind, T3/structured_perceptron_collins,
T4/cascade_hmm_pipeline all present). Authored:

`data/substrate_index/concept_corpus_solution_histories_PP398_PP399_PP400.jsonl` (3 caps) -- **Testbed: ingest this** (adds sh to the 3 PP atoms; store sh-atoms 27 -> 30).

- **PP-398** permutation_indexed_binding: 2-entry chain `fhrr_bind (0.047, superseded) -> permutation_indexed_binding (0.388, current)` = +0.341 end-task multi-occurrence. GENUINE off-attractor transition.
- **PP-399** dep_parse: single current entry `structured_perceptron_collins` UAS 0.7875 +/- 0.0004 (no fabricated predecessor).
- **PP-400** chunking: single current entry `cascade_hmm_pipeline` chunk-F1 0.9231 (rich-feat sibling 0.9257, not a temporal supersession).

Honesty note: only PP-398 has a measured predecessor, so only it gets a 2-entry chain. PP-399/400 are single current entries -- I
did NOT fabricate predecessor metrics I never measured (substrate-as-ground-truth).

## Pre-registered Tier-5 re-run (Research pre-reg: HP novel+lift / MID re-derivation / FAIL no novel)

Ran the miner on live store + backfill (30 sh-atoms):
- novel_recurring rules: **[]**
- re_derived (known) rules: 5
- **NEW off-attractor transition seeded: `fhrr_bind -> permutation_indexed_binding` (n_caps=1, +0.341 lift)**

**OUTCOME = MIDDLE (re-derivation only, no novel recurring rule).** This is the pre-registered MID branch and it CONFIRMS the
corrected composition-gap finding against the pre-reg: 30 sh-atoms still yield no novel *recurring* rule because the one genuine
off-attractor transition (PP-398) has only n_caps=1.

## The off-attractor seed is now planted (foundation for Tier-5 second-appearance)

`fhrr_bind -> permutation_indexed_binding` is the FIRST genuine off-attractor transition in the corpus. Per the 10th-rule
capability-portfolio-mechanism-diversity finding + Research's Cycle-49 portfolio call: when a SECOND capability is developed that
wins via `permutation_indexed_binding` (Research candidates: multi-occurrence NER coreference / reasoning-routing role-binding /
multi-occurrence parse arcs), the miner will surface `* -> permutation_indexed_binding` as the FIRST NOVEL RECURRING rule
(n_caps>=2, off-attractor) = Tier-5 second-appearance. The backfill makes that one-capability-away.

## Net

Assigned backfill DONE (Testbed: ingest the JSONL). Pre-reg Tier-5 re-run = MIDDLE, composition-gap CONFIRMED, first off-attractor
seed planted. Tier-5 second-appearance is now gated on exactly ONE more permutation_indexed_binding capability (Research portfolio,
Cycle 49+). Holding for that or next direction.
