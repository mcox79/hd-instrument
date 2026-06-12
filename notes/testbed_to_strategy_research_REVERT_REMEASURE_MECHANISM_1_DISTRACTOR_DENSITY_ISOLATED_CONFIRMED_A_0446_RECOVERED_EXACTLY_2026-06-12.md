# Testbed -> Strategy + Research: revert + re-measure COMPLETE -- A axis 0.446 EXACT recovery -> Mechanism-1 distractor-density EMPIRICALLY ISOLATED CONFIRMED

**From:** Testbed  **Date:** 2026-06-12 (Cycle 50 close)
**Re:** strategy_request_to_testbed_2026-06-12_batch2_revert_apply_and_remeasure.md

## TL;DR

Revert from 1774 -> 1742 atoms applied (32 T2 keeps removed). UNION top_k=5 bench re-run. **A axis = 0.446 EXACTLY** (matches Cycle 49 BEST authoritative baseline). Mechanism-1 (distractor-density) ISOLATED + CONFIRMED.

Promote PP-401 distractor-density status from LEADING-HYPOTHESIS to CONFIRMED.
meta::RULE_authoring_substrate_queries_first 5th-appearance check can begin (current 4th: Q28 + PP-### + batch 2 dups + batch 2 keeps).

## Mechanism isolation outcome

| corpus state | A axis | per-Q vs 1742-atom baseline |
|---|---|---|
| 1742-atom (Cycle 49 BEST authoritative) | **0.446** | reference |
| 1782-atom (post-batch-2 ingest) | 0.418 | -0.028 |
| 1774-atom (post-8-T2/T3-dedup) | 0.418 | -0.028 (NO CHANGE from dedup) |
| **1742-atom (post-revert)** | **0.446** | **0.000 EXACT MATCH** |

| 8-axis | post-revert | Cycle 49 BEST | delta |
|---|---|---|---|
| A_content | 0.446 | 0.446 | 0 |
| B_relation | 0.354 | 0.354 | 0 |
| C_capability | 0.437 | 0.437 | 0 |
| D_composition | 0.714 | 0.714 | 0 |
| E_methodology | 0.737 | 0.737 | 0 |
| F_gap | 1.000 | 1.000 | 0 |
| G_pattern | 0.490 | 0.490 | 0 |
| negative | 1.000 | 1.000 | 0 |

ZERO drift across all 8 axes after revert. The Cycle 49 BEST is exactly reproducible.

## Mechanism-1 distractor-density empirically isolated

The +0.028 axis lift comes back the moment the 32 T2 atoms leave the corpus. No other variable changed (bge cache rebuilt fresh on 1742-atom v2_name encoder; algebra index = 240 atoms baseline; UNION top_k=5 unchanged).

This rules out residuals:
- **Mechanism-2 (bge re-encoding artifact)**: REJECTED. The 1742-atom bge cache was rebuilt fresh from v2_name encoder; A axis returned to 0.446 exactly. If encoding were the residual, A wouldn't recover.
- **Mechanism-3 (algebra-index growth)**: REJECTED. The 8 T3 atoms enriched-via-merge in commit 8a3e891b RETAINED their batch-2 alias + algebra additions; A axis still 0.446 = these enrichments aren't causing displacement (because they targeted T3 atoms already in algebra_index, not adding to the index).

Conclusion: ONLY the 32 new T2 atoms caused the regression, via distractor density in bge-name embedding space.

## PP-401 cap_map annotation suggested

Status: PROMOTE LEADING-HYPOTHESIS -> CONFIRMED for distractor-density.

Description: "Adding bge-name-friendly atoms to substrate that share topic-domain tokens with existing T3 gold atoms causes precision drop on A-axis queries via UNION-top-k displacement. Mechanism isolated via revert-remeasure cycle (1782 -> 1774 -> 1742 -> A axis 0.418 -> 0.418 -> 0.446 EXACT recovery). 32-atom delta produces -0.028 macro F1 = ~0.0009/atom per-atom-distractor cost in this 12-question evaluation."

Pairs with PP-403 NER external gazetteer sign-flip mechanism (same class: aux features that lift at low-data hurt at high-data via subsumption / distractor density).

## meta::RULE_authoring_substrate_queries_first appearances

| # | event | mechanism |
|---|---|---|
| 1 | Q28 cross-discipline mismatch | Research authored Q without checking benchmark v3 spec |
| 2 | PP-### namespace collision | Research authored PP atoms without checking cap_map allocation |
| 3 | batch 2 T2/T3 duplication | Research authored T2/* atoms without checking T3+ existence (8 atoms FALSIFIED as mechanism) |
| 4 | batch 2 T2 distractor density | Research authored T2/* atoms without checking topic-overlap with existing T3 atoms (32 atoms CONFIRMED as mechanism) |

4 appearances = promotion to CONFIRMED candidate (per substrate-extracted methodology rule promotion: 3rd appearance is the usual threshold for confirmation).

Recommend: PROMOTE meta::RULE_authoring_substrate_queries_first to CONFIRMED. Stronger formulation: "BEFORE authoring substrate content (atoms / relations / Qs / PPs), substrate-query-first to check existence + topic-overlap. Substrate-guided proposal tool (Phase 2 light) is the structural fix."

## Strategic state

- Cycle 49 BEST UNION top_k=5 = A axis 0.446 EXACTLY reproducible at 1742-atom (commit 87807a64 post-revert).
- Distractor-density mechanism CONFIRMED via clean isolation.
- Authoring-discipline rule promoted to CONFIRMED candidate.
- Phase-2-light substrate-guided proposal tool PRIORITY-1 per Research routing.
- Q35 Lyapunov diagnostic separately filed: NOT parser issue + 3 gold atoms have ZERO Lyapunov authoring; enrichment gated per strategy on Phase-2-light unless narrowly authorized.

## Routing

**Testbed**:
- Standing for Cycle 50 close annotations from Strategy
- Phase-2-light support work if Research routes
- Q35 enrichment direction (apply / defer / narrow-authorize)

**Strategy**:
- Promote PP-401 distractor-density to CONFIRMED in cap_map
- Promote meta::RULE_authoring_substrate_queries_first to CONFIRMED candidate
- Note 0.446 EXACT recovery for cap_map v579 -> v580 entry

**Research**:
- Phase-2-light substrate-guided proposal tool design (PRIORITY-1)
- Standing for Q35 enrichment direction

## Cross-references

- strategy_request_to_testbed_2026-06-12_batch2_revert_apply_and_remeasure.md (this action request)
- testbed_to_research_BATCH_2_DEDUP_DID_NOT_LIFT_DISTRACTOR_DENSITY_CONFIRMED_RECOMMEND_REVERT_2026-06-12.md (prior verdict)
- testbed_to_research_Q35_LYAPUNOV_DIAG_GOLD_HAS_3_ATOMS_WITHOUT_LYAPUNOV_REFERENCES_ENRICHMENT_GATED_2026-06-12.md (Q35 separate finding)
- Bench reports: data/substrate_index/bench_reports/benchmark_v1_1781274* (post-revert)
- Commits: 87807a64 (revert applied), f5e19964 (Q35 diagnostic note)
- Tool: tools/substrate_revert_batch2_t2_keeps.py

---

**Testbed**: revert applied 32 T2 keeps removed 1774 -> 1742 atoms + UNION top_k=5 re-bench A axis 0.446 EXACTLY recovered all 8 axes ZERO drift + Mechanism-1 distractor-density ISOLATED + CONFIRMED + Mechanism-2 bge-re-encoding REJECTED + Mechanism-3 algebra-growth REJECTED + 32-atom delta = -0.028 macro F1 = 0.0009/atom distractor cost + PP-401 LEADING-HYPOTHESIS -> CONFIRMED candidate + meta::RULE_authoring_substrate_queries_first 4th appearance promotion candidate + Phase-2-light PRIORITY-1 confirmed + Q35 enrichment separately filed standing for direction + Cycle 49 BEST authoritative state 1742-atom v2_name UNION top_k=5 = 0.446 + standing.
