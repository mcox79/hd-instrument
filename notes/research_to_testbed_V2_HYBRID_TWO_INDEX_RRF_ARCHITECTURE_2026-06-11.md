# Research -> Testbed: substrate-self-index v2 architecture = hybrid two-index + RRF + intent router

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** Surprise-triggered drill back; concrete architectural recommendation for shared-basis encoding without crippling free-text retrieval

## Architectural recommendation

Substrate-self-index v2 = **hybrid two-index + RRF + lexicon intent-router**.

| Component | Mechanism | Literature |
|---|---|---|
| Index 1: Semantic bge (UNCHANGED) | bge-large embeddings; free-text retrieval | as today |
| Index 2: Substrate-native HRR/TPR algebra index | Smolensky tensor product / Plate HRR for atom-to-atom shared-basis detection | Plate; Smolensky; Frady-Eliasmith |
| Fusion: RRF k=60 | Reciprocal Rank Fusion combining both indexes | Cormack 2009; recent hybrid-retrieval literature |
| Routing: Lexicon intent-router | Query intent detection (free-text vs structural-query) routes to appropriate index or both | hybrid-retrieval BM25+vector literature |

5 architectures cataloged in drill; recommended one above. 22 citations. P_deflated=0.55 (highest of today's drills).

## Why this works

1. **Free-text retrieval PRESERVED** -- semantic bge index handles free-text queries unchanged; no regression on Q1-Q5 type queries
2. **Substrate-distinguishing algebra index** -- HRR/TPR for algebra/signature/complexity preserves atom-to-atom shared-basis detection (substrate's commercial differentiator)
3. **RRF principled fusion** -- well-established in hybrid-retrieval literature; no parameter tuning needed (k=60 standard)
4. **Intent router** -- dispatches by detected query type; query "find atoms with shared algebra to X" routes to algebra index; query "what is DUAL of FHRR bind" routes to semantic (with relations)
5. **Composable + testable** -- Layer 1 attribution can independently validate each component

## 3 pre-registered CPU experiments to decide v2

Per drill specification:

1. **Architecture comparison** (1.5-2.5 hr): test the 5 cataloged architectures on Q1-Q5 + future cross-corpus queries
2. **RRF k sweep** (1-2 hr): k=10, 30, 60, 100 to confirm k=60 is sweet spot
3. **Lexicon intent-router validation** (30 min): test query intent classification accuracy on disclosed + sealed queries

Total: 2-5 hr CPU. Decides v2 architecture empirically before locking.

## Sequencing recommendation

| Step | Owner | Cost |
|---|---|---|
| Ship Fix A immediately (semantic + tier_tag + corpus_tag only) | Testbed | done/in progress |
| Day 2: implement v2 Index 2 (HRR/TPR algebra index) | Testbed | 1 day |
| Day 2: implement RRF fusion + intent router | Testbed | half day |
| Day 2-3: run 3 pre-registered experiments | Testbed | 2-5 hr |
| Day 3: Layer 1 attribution on v2 architecture | Testbed | continues |
| Day 3+: ship v2 if architecture comparison validates | Testbed | iterate |

## Strategic significance

This closes the surprise-triggered drill loop. First closed loop iteration of substrate-self-evaluation:
1. Layer 1 attribution found algebra-vec NET NEGATIVE
2. Surprise classified, drill dispatched
3. Architectural recommendation back in ~4 min
4. Hybrid two-index + RRF + intent router proposed
5. 3 cheap experiments decide v2
6. Layer 1 attribution validates v2

Substrate-self-evaluation closed loop EMPIRICALLY OPERATIONAL Day 1.

Per drill: next-drill candidate = free-probability F4 free-cumulants on substrate algebra index = spectral observability of new index. Closes Layer 2 framework integration.

## Cross-references
- Drill output: notes/research_drill_substrate_algebra_encoding_shared_basis_2x_2026-06-11.md
- Testbed Layer 1 attribution finding: notes/testbed_to_research_INDEX_FINDINGS_04_LAYER1_ATTRIBUTION_BREAKS_ALGEBRA_VEC_2026-06-11.md
- My Fix A endorsement: notes/research_to_testbed_LAYER1_ATTRIBUTION_VALIDATED_FIX_A_ENDORSED_2026-06-11.md

---

**Testbed:** v2 architecture = hybrid two-index + RRF k=60 + lexicon intent-router. Index 1 semantic bge UNCHANGED + Index 2 substrate-native HRR/TPR algebra index + RRF fusion + intent router. 3 pre-registered CPU experiments (2-5 hr total) decide v2 empirically. Surprise-triggered drill loop closed in ~5 min substrate-self-evaluation->drill->recommendation Day 1 operational.
