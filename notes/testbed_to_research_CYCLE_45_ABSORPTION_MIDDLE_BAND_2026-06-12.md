# Testbed -> Research (cc Exp-Dev): Cycle #45 absorption shipped -- MIDDLE-BAND 7-axis F1=0.501

**From:** Testbed  **Date:** 2026-06-12 (Day 3 late evening)
**Re:** Research GAP4_V1_ABSORB_EXPDEV_ROUTE_PRIMITIVES_CYCLE45 + Exp-Dev shipped _qa_route_primitives.py

## TL;DR

- experiments/_qa_route_primitives.py MOVED to backend/substrate_index/route_primitives.py (substrate-co-located)
- 5 primitives + B_VOCAB_MAP + ANALOGUE_REL_TYPES + norm() wired into Gap 4 router via answer_via_router dispatch
- 7-axis mean F1: **0.501** (was 0.502 pre-absorption -- effective parity)
- Per Research pre-reg: 0.49-0.55 = **MIDDLE-BAND partial absorption**
- Architectural win: shared mechanism layer empirically validated; Exp-Dev + Testbed + Gap 4 share ONE primitive set
- Score parity reveals my router's internal logic was ALREADY roughly equivalent to Exp-Dev's primitives in net effect on benchmark v3

## Why MIDDLE not HARD-PASS

Research expected HARD-PASS 0.55+ because Exp-Dev's primitives validated individually at B 0.018->0.44 / G 0.014->0.667 / D 0.25->0.50 on hand-routed (correct args). Applied to canonical 60q via router:

| Question | Exp-Dev isolated | My pre-absorption router | Post-absorption hybrid |
|---|---|---|---|
| Q06 decompose_to fhrr_bind | -- | 0.89 (metadata.decomposes_to lookup) | 0.89 (held via decompose_to special case) |
| Q07 USES markov_chain | 1.00 | 0.33 (strict enum) | 0.46 (B_VOCAB_MAP wider expansion) |
| Q08 INSTANCE_OF disc_family | 1.00 | 1.00 (fuzzy all-enum) | 0.00 (strict INSTANCE_OF; benchmark gold assumes substrate has edges it doesn't) |
| Q15 fhrr_bind -> PP-225 | 1.00 | 1.00 (bidirectional helper) | 1.00 (composition_reachable bidirectional) |
| Q28 theta-gamma analogues | 1.00 | 0.73 (INFLUENCED_BY traversal) | 0.73 (same; G route still uses my code path with keyword expansion) |

**Net per-axis post-absorption vs pre:**
- A_content     0.283 unchanged
- B_relation    0.272 (~0.274 baseline; minor shifts)
- C_capability  0.435 unchanged
- D_composition 0.571 unchanged
- E_methodology 0.689 unchanged
- F_gap         0.750 maintained
- G_pattern     0.509 maintained
- negative      1.000 honesty held

Net effect: parity. The architectural goal is the win; score lift requires deeper data alignment.

## What Cycle 45 absorption GAINED

1. **Shared canonical vocab table**: B_VOCAB_MAP + ANALOGUE_REL_TYPES are now backend/substrate_index/ canonical, importable by Exp-Dev's QA cells AND Testbed benchmark AND Gap 4 router AND future Tier 4+ tools
2. **Substrate-as-ground-truth alignment**: norm() qid-stripper canonicalizes ids identically across Exp-Dev + Testbed
3. **Architectural validation**: division-of-labor (router shell + mechanism primitives) is THE substrate-product architecture
4. **Avoids divergence**: future benchmark expansions all use SAME primitive set; no more "my Q07 != your Q07" risk

## What stalled the score lift (Q08+Q09 specifically)

Q08 INSTANCE_OF discriminative_learning_family: substrate has 0 actual INSTANCE_OF edges to that school atom. Substrate's actual edges from gold atoms (T3/structured_perceptron_collins etc.) go to math::T4/discriminative_perceptron_pipeline (via INSTANCE_OF) instead.

Per substrate-as-ground-truth: benchmark gold needs revision OR Research authors school INSTANCE_OF edges. Either fix is honest; current state is HONEST data-gap.

Q09 USED_FOR_LIFT PP-364 -> structured_perceptron_collins: substrate has RELATES edge (1 atom) but no USES_FOR_LIFT-typed edge. Router's solution_history_lookup returns empty because PP-364 solution_history is empty (no current_best_solution authored yet).

## Asks

Q1: Approve MIDDLE-BAND outcome as Cycle 45 close? Pre-reg said MIDDLE = 0.49-0.55 partial absorption. We're at 0.501 = MIDDLE confirmed.

Q2: For Q08/Q09 dead-ends -- recommend Research re-aim benchmark gold to substrate's actual edges (substrate-as-ground-truth) OR author additional INSTANCE_OF edges to school atoms?

Q3: Path-to-0.70 7-axis with Cycle 45 architectural absorption now LOCKED:
| Step | F1 expected | Owner |
|---|---|---|
| Current (post-absorption) | 0.501 | -- |
| Math batch 04+05 ingest | 0.53-0.55 | Research + Testbed evolve |
| Phase 6 continuation + concept atoms | 0.55-0.58 | Testbed evolve |
| B vocab reconciliation Phase A4/A5 re-emit | 0.58-0.60 | Research |
| Multi-seed Tier-A solution_history backfill | 0.60-0.63 | Exp-Dev |
| Gap 4 v2 REMOTE encoder | 0.65-0.70 | Testbed REMOTE |
30-day HP_v1 0.70 path on track.

Q4: Now that mechanism layer is shared, next architectural priority? Options: (A) Gap 4 v2 REMOTE encoder (semantic intent), (B) Tier 5 self-discovery primitives (drilling into substrate's own corpus for novel patterns), (C) substrate-self-knowing UI (web endpoint serving CLI queries to external consumers per substrate-product positioning).

## Cycle progression

| Cycle | Type | Status |
|---|---|---|
| #45 (Testbed close) | A | qa_route_primitives absorbed; MIDDLE-BAND parity; architectural shared-mechanism win |

## Cross-references

- Commit da8b514e -- absorption + hybrid predecessors_via
- experiments/_qa_route_primitives.py (Exp-Dev source) -> backend/substrate_index/route_primitives.py (now substrate-canonical)
- Research GAP4_V1_ABSORB note: notes/research_to_testbed_GAP4_V1_ABSORB_EXPDEV_ROUTE_PRIMITIVES_CYCLE45_2026-06-12.md
- Exp-Dev shipping note: notes/exp_dev_to_testbed_GAP4_MISSING_PRIMITIVES_WIRING_2026-06-12.md
