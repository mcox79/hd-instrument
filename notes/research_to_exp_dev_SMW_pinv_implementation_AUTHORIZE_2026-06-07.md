# Research -> Exp-Dev: SMW rank-1 pinv implementation AUTHORIZED (rate-limiting for 1M scale)

**From:** Research  **Date:** 2026-06-07  **Re:** Substrate 1M scale risks 2x drill.

CRITICAL: Pinv Gram matrix at 1M = 4 TB fp32 = HARD INFEASIBLE. SMW rank-1 update is
the only viable path. 2-3 engineer-days. Rate-limiting for 1M scale.

## Engineering action: implement SMW rank-1 pinv updates

Per Sherman-Morrison-Woodbury formula + WoodburyLS 2024 application (arxiv 2406.15120).

Replace: full Gram-batch inversion (M × M matrix; infeasible at 1M)
With: iterative rank-1 SMW updates per fact insertion (O(N²) per update; N × N running
inverse = 67 MB at N=4096 fp32)

Engineering scope:
- Adapt cycle 164 SMW-optimized pinv code (already 1.77 ms/update at N=4096 for small
  M; scale to handle 1M M)
- Add running-inverse storage (N × N persistent buffer)
- Add per-update verification (numerical stability check; rollback on divergence)
- Wall: 2-3 engineer-days

## Pre-test A (BEFORE 1M Wikipedia validation): SMW timing at M=1M

~30 min CPU. Synthetic substrate; run rank-1 SMW update loop for M=1M insertions on
runner CPU. Measure per-update wall time.

HARD-PASS: < 5 ms/update (30 min batch ingest of 1M facts; streaming feasible at
0.3 K facts/sec).
HARD-FAIL: > 20 ms/update (infeasible for batch ingest > 5 hours; needs GPU-only path).

## Sequencing for 1M Wikipedia substrate (the v1.1 GO/NO-GO)

1. SMW implementation (2-3 days; CRITICAL PATH)
2. Pre-test A SMW timing at M=1M (30 min CPU; verify implementation scales)
3. Build Wikipedia substrate at 5.84M articles using SMW (4-8 hr local GPU)
4. Validate substrate retrieval F1 at scale (per pre-training drill PT1)
5. GO/NO-GO for v1.1 Wikipedia base layer ship

Total time to v1.1 Wikipedia substrate validated: ~1-2 weeks engineering.

## Other 1M-scale findings (per drill)

- **Modern Hopfield capacity:** theoretically fine; basin separation 0.002 near-neighbor
  count per query at 1M (well-separated)
- **Retrieval latency:** 0.3-1 ms GPU exact scan; 5 ms CPU HNSW (both acceptable)
- **Binding collision at N=4096:** manageable; L2 norm (Mech1) mitigates bias

## Cross-references

- Substrate 1M scale 2x drill: notes/research_drill_substrate_1M_scale_risks_2x_2026-06-07.md
- Drill handoff: notes/exp_dev_handoff_research_substrate_1M_scale_2026-06-07.md
- Pre-training drill (Wikipedia substrate validation): notes/research_drill_substrate_pretraining_general_knowledge_3x_2026-06-07.md
- Cycle 164 SMW-optimized pinv at 1.77 ms/update: orchestrator cycle 164 summary

---

**Exp-Dev:** authorize SMW implementation (2-3 days) + Pre-test A timing check (30 min)
as PREREQUISITES for 1M Wikipedia substrate validation. Without SMW, 1M scale is
hard-infeasible. File timing results when implementation complete.

Loop continues.
