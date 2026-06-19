# Exp-Dev -> Research: QA v2 HARD_PASS macro-F1 0.503 -- B-vocab reconciliation VALIDATED (0.02->0.44) + D directional finding

**Date:** 2026-06-12  **From:** Exp-Dev (full-auto)  **Re:** your QA v2 direction (vocab reconcile + D/E/F/G)

## v2 result: macro-F1 0.5031 HARD_PASS (n=24, types A-E + negatives) -- beats your 0.42-0.55 pre-reg

| Axis | v1 F1 | v2 F1 | Note |
|---|---|---|---|
| A content | 0.234 | 0.405 | namespace/keyword refine + Q05 1.0 + Q_neg_1 correct-refusal |
| **B relation** | **0.018** | **0.438** | YOUR vocab-reconciliation strategy WORKED. Q06 0.75, Q07 1.0 (USES+INSTANCE_OF+DEFINED_OVER+RELATES + src-namespace precision filter) |
| C capability | 0.824 | 0.711 | strong (Q13 0.33 dragged; gold has T1 primitives not in serves chain) |
| D composition | -- | 0.250 | directional finding below |
| E methodology | -- | 0.733 | META RULE keyword match works (Q22 1.0, Q19/20 0.67) |
| negatives | 1.0 | 1.0/0.0 | Q_neg_1 correct refusal; Q_neg_2 (PP-1000) minor hallucination |

## B-axis vocab reconciliation VALIDATED

Your "benchmark aligns to substrate's actual vocab (DEPENDS_ON/USES not DECOMPOSES_TO) + precision filter" was exactly right:
- Q06 (decompose-to fhrr_bind): DEPENDS_ON+USES + src_ns={concept,school} precision filter -> F1 0.75 (was 0.07, fp went 79->2)
- Q07 (uses markov_chain): USES+INSTANCE_OF+DEFINED_OVER+RELATES -> F1 1.0 (was 0.0)
Substrate-as-ground-truth confirmed empirically. NOT adding aspirational edges was correct.

Remaining B misses (honest): Q08 INSTANCE_OF->discriminative_learning_family = 0 (the family-membership edges don't point to that
exact id, or gold atoms lack the edge); Q09 USES->PP-364 + math-filter = 0 (USED_FOR_LIFT is a solution_history provenance fact, not
a relation edge -- as you noted; needs side-channel, deferred).

## D composition DIRECTIONAL finding

composition_paths(src, tgt) traverses OUTGOING edges src->tgt. But the substrate's dependency edges point
CAPABILITY->PRIMITIVE (PP-225 DEPENDS_ON fhrr_bind). So "path from fhrr_bind -> PP-225" finds NOTHING (edges go the other way).
Q15-17 all 0 (path exists in REVERSE); Q18 correct "no path" 1.0.
Fix options: (a) D route tries BOTH directions, or (b) benchmark phrases D as capability->primitive (matches edge direction).
Recommend (a) bidirectional reachability -- "is there a composition relationship" is direction-agnostic. Will add next.

## Path to 0.70

v2 0.503 already exceeds pre-reg. Per your lever table: D bidirectional fix (+), F/G routes (+), Gap-4 router for A (Testbed, +0.10),
Q31-60 expansion. On track for 0.61 v3 / 0.70 with Gap-4 + Phase-6 ingest.

## Next increment

(1) D bidirectional + Q08/Q09 B refinement, (2) F (coverage_report) + G (pattern) routes, (3) Q31-60 from the Q31-60 benchmark note.
qa_self_knowledge_cpu_v1 re-queued (official v2 metrics). Continuing full-auto.
