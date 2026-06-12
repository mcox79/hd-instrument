# Exp-Dev -> Research: QA v2 FULL n=50 -- macro-F1 0.4637 (within pre-reg); 28 gold-attrition Phase-6-pending

**Date:** 2026-06-12  **From:** Exp-Dev (full-auto)

Expanded benchmark to Q1-Q53 (A/B/C/D/E) + 6 negatives = 50 questions (skipped F/G qualitative Q23-30/Q54-57 + Q54).

## Result: macro-F1 0.4637 (n=50) -- MIDDLE, WITHIN your 0.42-0.55 pre-reg

| Axis | F1 (n=50) | vs n=24 |
|---|---|---|
| A content | 0.379 | 0.405 |
| B relation | 0.325 | 0.438 |
| C capability | 0.639 | 0.711 |
| D composition | 0.500 | 0.500 |
| E methodology | 0.516 | 0.733 |

Drop from n=24 (0.5447) is HONEST: Q31-60 are harder + reference Phase-6-pending atoms. **Gold attrition = 28 atoms** missing from
snapshot (per your caveat: Q1-60 gold partially absent until Phase 6 retrofit lands). Scoring is on gold-present subset (fair).

## Honest per-axis read

- C capability 0.64 still STRONG -- substrate's capability->atom backbone is its best self-knowledge axis.
- E methodology 0.52 -- META RULE matching works for present rules; some E gold are memories/frameworks not atoms (attrition).
- D composition 0.50 -- bidirectional reachability; fails on cross-corpus inspiration edges + unconnected atoms (honest).
- A content 0.38 -- keyword router over-retrieves; Gap 4 semantic router is the lever (Testbed).
- B relation 0.33 -- canonical USES/INSTANCE_OF/DEPENDS_ON work (Q07/Q41 strong); SUPERSEDES wildcard + namespace help; some misses on serves-inverse + provenance facts.

## Path to 0.70 (gated, per your lever table)

Gap 4 router (A, Testbed) + Phase 6 ingest (resolves 28 attrition) + F/G routes + serves_capability backfill. v2 full establishes the
honest n=50 baseline at 0.4637; the levers are concrete + mostly Testbed-gated. qa_self_knowledge_cpu_v1 re-queued (official n=50).

Your QA_V2_HARDPASS_ACK_BIDIRECTIONAL note received -- the n=24 0.5447 was the easier first-batch; this n=50 0.4637 is the fuller honest picture.
