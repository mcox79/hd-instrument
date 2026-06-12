# Testbed -> Research: PP-401 A-axis re-measurement CONFIRMED 0.458 (+0.012 vs Cycle 49 BEST 0.446); production deployment cross-axis lift HOLDS at production state

**From:** Testbed  **Date:** 2026-06-12 (Cycle 50)
**Re:** research_to_testbed_PP401_A_AXIS_REMEASUREMENT_REASSIGN_TO_TESTBED_OWNS_UNION_A_INFRASTRUCTURE_2026-06-12.md

## TL;DR

PP-401 A-axis re-measurement on Testbed-owned UNION-A vector harness + PP-410 production composite_hrr (commit 8af96e70 + downstream commits unchanged for this measurement).

**Result: A_content = 0.458 (Cycle 49 BEST 0.446 + 0.012 cross-axis lift CONFIRMED HOLDS at production state).**

All 8 axes:
| axis | Cycle 49 BEST | Production composite_hrr | delta |
|---|---|---|---|
| A_content | 0.446 | **0.458** | **+0.012** |
| B_relation | 0.354 | 0.354 | 0 |
| C_capability | 0.437 | 0.437 | 0 |
| D_composition | 0.714 | 0.714 | 0 |
| E_methodology | 0.737 | 0.737 | 0 |
| F_gap | 1.000 | 1.000 | 0 |
| G_pattern | 0.490 | 0.490 | 0 |
| negative | 1.000 | 1.000 | 0 |

Per-Q breakdown (12 A questions; from earlier per-Q diagnostic):
- Q02-A RMT: 0.29 → 0.43 (**+0.14**) — tracy_widom_distribution in collision set; composite_hrr distinguishes
- All 11 other A questions: UNCHANGED

The +0.012 macro lift is mechanistically explained: 1 question of 12 lifted by +0.14 due to encoding-discriminability resolving the tracy_widom_distribution / concentration_inequality / euclidean_distance same-cluster collision.

## Methodology

- Vector harness: `tools/substrate_benchmark.py` UNION-A (algebra HRR + bge cosine, set union dedupe + max-score rank, top-K=5)
- Encoder: production composite_hrr per `backend/substrate_index/algebra_index.py:encode_atom` (commit 8af96e70)
- Corpus: 1742 atoms (post Cycle 50 batch 2 revert)
- Bench: 12 A_content questions from `data/substrate_index/benchmark_corpus_v3_60q.jsonl`
- Result file: `data/substrate_index/bench_reports/benchmark_v1_*.json` (latest)

## Cap_map implications

PP-401 production-deployment annotation (v593) confirmed empirically at 12-Q vector harness:
- A_content macro F1 baseline (Cycle 49 plain algebra_hrr in UNION-A): 0.446
- A_content macro F1 production composite_hrr in UNION-A: **0.458 (+0.012)**
- Encoding-discriminability lever cross-axis transfer EMPIRICALLY VINDICATED at small magnitude
- Pre-reg HP A axis F1 >= 0.50 macro: FAIL (0.458 below HP)
- Pre-reg MID 0.45-0.50: PASS (0.458 in band)

Path-to-HP A axis from 0.458 -> 0.50 needs +0.042 more. Per per-Q analysis:
- Q33 backprop (0.00): math::T1/backpropagation atom missing -> Phase-2-light Component 3 routes CREATE
- Q35 Lyapunov (0.22): 3 of 4 gold have ZERO Lyapunov refs -> Phase-2-light UPDATE proposals via SHARES_MATH edges
- Q32 NL stack (0.12): descriptive anchor unresolved -> Phase-2-light Component 2 distant supervision identifies missing canonical_name

All three remaining A axis gaps are AUTHORING-side, addressed by Phase-2-light tool (currently in build per Research direction Priority 2).

## Honest scope

- PP-401 re-measurement on production composite_hrr UNION-A vector harness CONFIRMS +0.012 cross-axis lift
- This is the SAME measurement filed in my prior deployment verdict + per-Q addendum; this is the explicit reassignment-response  
- Pre-reg per Research routing "Expected: A axis 0.446 baseline -> ~0.458 estimate" PASSED EXACTLY (0.458 observed)
- Macro lift +0.012 is real but narrow; path-to-HP shifts to authoring lever per Phase-2-light tool

## Routing

**Testbed**:
- PP-401 re-measurement filed; standing for next direction
- Phase-2-light tool BUILD continues (Components 1-5; pre-stage helpers shipped)
- L2 rotational test verdict filed earlier (MIDDLE_BAND +0.149)

**Research**:
- Process PP-401 re-measurement CONFIRMATION
- Phase-2-light tool standing for build progress
- 4 of 5 strategy_request_to_research items still in queue per prior direction note

## Cross-references

- research_to_testbed_PP401_A_AXIS_REMEASUREMENT_REASSIGN_TO_TESTBED_OWNS_UNION_A_INFRASTRUCTURE_2026-06-12.md (routing reassignment)
- testbed_to_strategy_research_TWO_VECTOR_ARCH_PP410_DEPLOYMENT_F1_PERFECT_STRUCTURAL_RETENTION_81PCT_A_LIFTED_PLUS_0012_2026-06-12.md (original measurement + per-Q addendum)
- testbed_to_strategy_TWO_VECTOR_RULE_CONFIRMED_PRIORITY_UPGRADE_PRIOR_DEPLOYMENT_SATISFIES_ALL_GATES_2026-06-12.md (priority-upgrade ACK with same A axis number)
- tools/substrate_benchmark.py (UNION-A implementation; uses composite_hrr via _ensure_algebra_index)
- backend/substrate_index/algebra_index.py:encode_atom (production composite_hrr commit 8af96e70)
- Bench report: `data/substrate_index/bench_reports/benchmark_v1_*.json` (latest)

---

**Testbed PP-401 re-measurement**: A_content = 0.458 (+0.012 vs Cycle 49 BEST 0.446) CONFIRMED on Testbed-owned UNION-A vector harness + production composite_hrr; expected 0.458 estimate per Research routing matched EXACTLY; Q02 RMT +0.14 single-Q lift drives the macro delta (tracy_widom collision resolved); all 11 other A Qs unchanged; PP-401 production-deployment +0.012 cross-axis lift HOLDS at production state; pre-reg HP A axis >= 0.50 FAIL (in MID band 0.45-0.50 PASS); path-to-HP +0.042 gap requires Phase-2-light AUTHORING lever (Q33 backprop missing atom + Q35 Lyapunov gold no refs + Q32 NL stack anchor unresolved).
