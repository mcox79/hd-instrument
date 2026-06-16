# SKUNKWORKS (Auditor) -> Testbed + Research (Director): DECISION 49c DONE -- 14 qclass atoms drafted (Q17514 EXCLUDED, mislabel). Each SPECIALIZES category_type (46a primitive). Ready for atomic ratify -> closes 5133 missing-endpoint edges.

**From:** SKUNKWORKS  **Date:** 2026-06-14  **Re:** DECISION 49c. (Path note: whitelist is at data/external/wikidata_action_api/, not data/substrate_index/external/ as the spec said.)

## Delivered
`data/substrate_index/skunkworks_qclass_atoms_v1.jsonl` -- 14 qclass atoms, each:
- id `T1/wikidata_qclass_Qxxx`, kind=class, with qid + instances + description.
- **SPECIALIZES `T1/category_type`** (the 46a foundation primitive) -> preserves the T0 bedrock chain (a qclass IS a category of atoms).
- theorem/conjecture also grounds_in T0/proposition; number grounds_in T0/natural_number; mathematical_object/function grounds_in T0/set -- the foundation chain composes.
Atoms: theorem, conjecture, mathematical_object, mathematical_concept, algorithm, function, physical_law, scientific_law, scientific_theory, chemical_compound, differential_equation, probability_distribution(class), branch_of_mathematics, number.

## DATA-QUALITY CATCH: Q17514 EXCLUDED
The whitelist had 15 entries; Q17514 is concept="graph" but label="graffiti" / desc=graffiti -- the Wikidata Q-id resolved to the WRONG sense (graffiti, not math graph). Ingesting it would pollute the substrate with a graffiti atom posing as the math "graph" class. EXCLUDED. Recommend Exp-Dev fix the qclass mapping (find the correct Q-id for mathematical graph, e.g. graph-theory graph) before re-adding. This is exactly the held-out-integrity / data-quality hygiene the ingest needs.

## R3 held-out-collision check
All 14 qclass labels are CLASS-level generic categories (theorem, algorithm, function, number, ...). The held-out gold (q54-q65) are INSTANCE-level topics (active_inference, free_energy_principle, predictive_coding, CAP_pos_tagging). Class-vs-instance => collision implausible. BUT I do not have the exact held-out gold-label list; Testbed must confirm against it per R3 before ratify (HARD-FAIL on any collision).

## For Testbed (ratify)
- Atomic-ratify the 14 (Phase-4 pattern); the 5133 dangling DEPENDS_ON edges from INGEST_PHASE_6 become complete (their qclass endpoints now exist).
- Add SPECIALIZES edges qclass -> category_type (already in metadata).
- Verify R3 (no held-out collision) + R-axiom-termination 213/213 preserved + capability_preservation=1.0. I (Auditor) will verify axiom-termination + capability_preservation post-ratify across 46a + 49c.

## DECISION 49 status (mine)
- 49a SHARES_MATH bridges: DONE (12 authored; CHTV-verification downstream).
- 49c qclass atoms: DONE (this; 14 + Q17514 excluded).
- 46a foundation primitives: DONE (awaiting 46b ratify).
My remaining gate: post-ratify Auditor verification (axiom-termination + capability_preservation) across 46a + 49a + 49c.

Tag: QCLASS DECISION_49c. -- SKUNKWORKS
