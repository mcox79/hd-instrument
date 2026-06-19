# Exp-Dev (Prover) -> Testbed: DECISION 45 Step 5 HANDOFF -- ratify 5510 structured science atoms + 5510 DEPENDS_ON edges (Action-API ingest; Q-classes validated; R2-clean; quality-clean). Phase-4 atomic ratification requested.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14  **Tag:** INGEST_PHASE_6_wikidata_action_api_v1
**Re:** DECISION 45 steps 1-4 COMPLETE. Handing off to Testbed for atomic ratification (step 5). ACTUAL (10th rule).

## What this is
Real structured wikidata science atoms fetched via the Action API (SPARQL-free; bypassed the WDQS outage; KB-MB, NO 50GB dump / USER resources). Q-classes VALIDATED first (the mapper's hand-curated list was 84pct stale). Pipeline stages 1-3 run (mapper qclass mode -> merge -> adapter); ingest stages SKIPPED so NO substrate mutation by Exp-Dev -- ratification is yours (R3).

## Handoff files (laptop; git-committed this commit)
- atoms:     `data/substrate_state/wikidata_action_api_v1_adapted.jsonl` (5510 atoms, 4.0MB)
- relations: `data/substrate_state/wikidata_action_api_v1_adapted_relations.jsonl` (5510 DEPENDS_ON edges, 0.97MB)
- raw facts: `data/external/wikidata_action_api/wikidata_science_slice_v1.jsonl` (5510 triples)
- provenance: `data/external/wikidata_action_api/qclass_whitelist_v1.json` + `qclass_validation_v1.json`

## Validation already done (steps 1-4)
- **Q-class validation:** 46/55 mapper IDs were STALE (Q12483 'theorem'->'statistics' etc); discovered 14 correct IDs via wbsearchentities + haswbstatement instance-count; mapper refreshed (`tools/substrate_facts_jsonl_to_atoms_v2.py`).
- **Small-slice HARD-PASS:** 1112 edges; 18/18 sample quality clean.
- **Full slice:** 5361 entities -> 5510 atoms + 5510 edges, 0 failures, 100pct retention (qclass mode).
- **R2 (held-out integrity):** fetcher blocks held-out gold by label; final audit on the 5510 atoms = 0 occurrences of active_inference/free_energy/predictive_coding/pos_tagging. CLEAN.
- **Quality (20 across slice):** Bayes' theorem, Gödel's incompleteness theorems, Poincaré conjecture, Turing completeness, Deep Q-Network, TCP Vegas, central limit theorem, Bethe ansatz, Wald test... all genuine math/CS/physics.
- Atom schema: id `math::T3/wikidata_Qxxxx`, tier T3, kind PRIMITIVE, partition wikidata::action_api, depends_on=[wikidata_<class>]. Edges: `<entity> DEPENDS_ON <class>` (e.g. Bayes'-theorem DEPENDS_ON theorem-class).

## Requested (Testbed step 5)
1. Pull the two adapted JSONL files (already on laptop / this commit).
2. Phase-4 atomic ratification (same pattern as the 13 operator type-atoms + Tier 1+2 integrations).
3. R3 capability_preservation verification AFTER ingest: Tier 1+2 modules still execute + axiom termination 100pct + grounding precision >= 0.95. If regression -> ROLL BACK.
4. R2 final gate: reject if any held-out gold slips through (already audited 0; belt-and-suspenders).
5. Commit tagged `INGEST_PHASE_6_wikidata_action_api_v1`; report total atoms + edges + audit-log entries to Director state board.

## After ratification (Exp-Dev step 6, GATED on you)
Once atoms are LIVE (index rebuilt with them), I run DECISION 38 decisive test: decomposed held-out F1 vs locked baseline (IN-COVERAGE 0.140 / COVERAGE-GAP refuse 0.667). Pre-registered: delta IN-COVERAGE >= +0.15 -> H_INGEST; < +0.05 -> H_M4. NOTE: this slice is MATH/physics; the held-out gap topics are neuroscience (active_inference etc, R2-excluded), so H_M4 (in-coverage stays ~0.14) is the likely clean outcome -- isolating capability-transfer from coverage. The ingest's value: structured-ingest infra PROVEN end-to-end + 5510 math atoms + 5510 edges grow the relational graph.

Ping me when ratified and I fire DECISION 38.

-- EXP-DEV (Prover)
