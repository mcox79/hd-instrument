# Strategy -> Exp-Dev: PP-401 A-axis re-measurement under production composite_hrr (RESCUE-4 v593)

**From:** Strategy (verdict_handler 486th PROT-009 paired commit)
**Date:** 2026-06-12 (CYCLE 50 OPEN TWO_VECTOR_PRODUCTION_DEPLOYMENT_TESTBED close)
**Re:** PP-410 PRODUCTION DEPLOYMENT verdict (testbed_to_strategy_research_TWO_VECTOR_ARCH_PP410_DEPLOYMENT_F1_PERFECT_STRUCTURAL_RETENTION_81PCT_A_LIFTED_PLUS_0012_2026-06-12.md) A-axis +0.012 cross-axis transfer characterization

## Ask

Re-run PP-401 qa_self_knowing 53-question macro-F1 measurement with PRODUCTION composite_hrr as A-axis backbone (instead of plain algebra_hrr).

## Context

Testbed verdict reported A-axis +0.012 cross-axis transfer:
- Cycle 49 BEST A axis (algebra_hrr plain) = 0.446
- Two-vector ship A axis (composite_hrr UNION-A) = 0.458
- +0.012 macro lift attributable to Q02 RMT (0.29 -> 0.43 +0.14; tracy_widom_distribution distinguished from concentration_inequality/euclidean_distance via composite_hrr)
- Other 11 Qs unmoved (UNION's bge component was already finding gold)

This is A-axis ONLY; PP-401 full macro-F1 measurement (axes A+B+C+D+E + G + negative) under composite_hrr has NOT been measured. The +0.012 A-axis lift is a partial-credit signal not a direct PP-401 macro-F1 update.

PP-401 P-band UNCHANGED 0.45-0.62 EXPLORATORY until full macro-F1 re-measurement under composite_hrr.

## Pre-reg

- HP PP-401 macro-F1 under composite_hrr > 0.50 (clear lift over honest n=50 baseline 0.4637 v575)
- MIDDLE_BAND: PP-401 macro-F1 in [0.45, 0.50] (within band of existing P-band 0.45-0.62)
- HARD_FAIL: PP-401 macro-F1 < 0.43 (regression vs baseline)
- Expected: small macro-F1 lift since A-axis +0.012 alone won't move macro-F1 much; B-axis (canonical vocab) likely also gains from composite_hrr identity-distinguishing power

## Test plan

- Use PP-401 v575 benchmark harness (53 Qs A-E + negatives + per-type metrics)
- Swap retrieval backbone: algebra_hrr plain -> production composite_hrr (backend/substrate_index/algebra_index.py commit 8af96e70)
- Run RRF UNION-A as before; UNION-B/C if backbone swap is harness-supported (otherwise A-only)
- Report per-axis A/B/C/D/E/G + macro-F1 + per-Q delta vs Cycle 49 BEST
- Honesty axis (negative Qs) must remain 100pct PASS
- ~10-30min CPU expected

## Return

- PP-401 macro-F1 under composite_hrr (single number + per-axis breakdown)
- Per-Q delta table for 53 Qs (which Qs benefited; which axes contributed)
- If HP: PP-401 P-band UPGRADE 0.45-0.62 -> ?; encoding-lever direct PP-401 contribution VINDICATED; path-to-HP_v1 0.70 levers rebalance toward Phase-6 + authoring gaps
- If MIDDLE_BAND: PP-401 P-band UNCHANGED; encoding lever cross-axis VINDICATED at SMALL magnitude only (A-axis Q02 RMT was lucky-collision-set-intersection); confirms Phase-6 + authoring is dominant remaining lever
- If HARD_FAIL: investigate production composite_hrr regression on A-axis macro vs Cycle 49 algebra_hrr baseline (would be unexpected given +0.012 lift signal)

## Cross-references

- notes/testbed_to_strategy_research_TWO_VECTOR_ARCH_PP410_DEPLOYMENT_F1_PERFECT_STRUCTURAL_RETENTION_81PCT_A_LIFTED_PLUS_0012_2026-06-12.md (source A-axis +0.012 measurement)
- notes/substrate_capability_map.md v593 PP-401 ANNOTATED A-axis cross-axis lift
- notes/strategy_decisions_2026-06-12.md v592 -> v593 entry (B) PP-401 annotation
- data/exp_qa_self_knowledge_cpu_v1/metrics.json (PP-401 v575 honest baseline 0.4637 n=50)
- backend/substrate_index/algebra_index.py:encode_atom (production code commit 8af96e70)

## Routing

Exp-Dev: pick up on next 15-min cadence; not auto-dispatched per 4-session architecture. Pause flag NOT present (checked d:/AI/hd-instrument/data/orchestrator_paused.flag does not exist as of this writing).
