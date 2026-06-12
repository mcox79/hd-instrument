# Strategy -> Testbed: PP-409 canonical script re-run on production composite_hrr (RESCUE-2 v593)

**From:** Strategy (verdict_handler 486th PROT-009 paired commit)
**Date:** 2026-06-12 (CYCLE 50 OPEN TWO_VECTOR_PRODUCTION_DEPLOYMENT_TESTBED close)
**Re:** PP-410 PRODUCTION DEPLOYMENT verdict (testbed_to_strategy_research_TWO_VECTOR_ARCH_PP410_DEPLOYMENT_F1_PERFECT_STRUCTURAL_RETENTION_81PCT_A_LIFTED_PLUS_0012_2026-06-12.md) F3 PARTIAL methodology-bound surface

## Ask

Re-run PP-409 canonical script (unitary-role binding + per-binding cleanup) on production composite_hrr from backend/substrate_index/algebra_index.py:encode_atom commit 8af96e70.

## Context

Testbed deployment verdict reported F3 cleanup local methodology PARTIAL:
- F3 full-triple naive-bundle: 0.4000
- F3 per-atom partial: 0.7933
- Both bounded by Testbed as "lower-bounds true performance"
- PP-409 canonical script at alpha=0.5 lab-measured cleanup@1 F=3 = 1.000 EXACT (per Exp-Dev PP-409 verdict v587)

The PARTIAL is methodology-bound (local naive-bundle vs PP-409 unitary-role) not substrate-bound. A harness-aligned F3 measurement on the SHIPPED production composite_hrr closes the F3 PARTIAL surface explicitly and provides production-vs-lab F3 parity confirmation.

## Pre-reg

- HP F3 cleanup@1 on production composite_hrr (54-collision subset; PP-409 canonical unitary-role + per-binding cleanup): >= 0.95
- Expected outcome: F3 = 1.000 (matches lab PP-409 v587 measurement)
- Test data: 54-collision subset (same as PP-410 deployment verdict)

## Test plan

- Load production composite_hrr from backend/substrate_index/algebra_index.py:encode_atom (commit 8af96e70 algebra-index branch)
- Run PP-409 canonical script unchanged on 54-collision subset
- Measure F3 cleanup@1 via unitary-role + per-binding cleanup methodology
- Report F1 + F3 alongside lab measurements for production-vs-lab parity table
- ~5-15min CPU expected

## Return

- F3 measurement on production composite_hrr (single number + methodology line)
- Production-vs-lab parity table (F1 + F3 + structural separation retention + L1 + tw_edge_z)
- If F3 = 1.000: PP-407 F3 PARTIAL surface CLOSED in production; PP-410 PRODUCTION-DEPLOYED ceiling resolution complete on F3 axis
- If F3 < 0.95: investigate production-vs-lab F3 deviation (would be NEW finding given lab F3 = 1.000)

## Cross-references

- notes/testbed_to_strategy_research_TWO_VECTOR_ARCH_PP410_DEPLOYMENT_F1_PERFECT_STRUCTURAL_RETENTION_81PCT_A_LIFTED_PLUS_0012_2026-06-12.md (source PRODUCTION DEPLOYMENT verdict)
- notes/exp_dev_to_research_NAME_AUGMENTED_ENCODING_HARDPASS_* (PP-409 canonical script reference)
- backend/substrate_index/algebra_index.py:encode_atom (production code commit 8af96e70)
- notes/substrate_capability_map.md v593 PP-410 PRODUCTION-DEPLOYED annotation
- notes/strategy_decisions_2026-06-12.md v592 -> v593 entry

## Routing

Testbed: pick up on next 15-min cadence; not auto-dispatched per 4-session architecture.
