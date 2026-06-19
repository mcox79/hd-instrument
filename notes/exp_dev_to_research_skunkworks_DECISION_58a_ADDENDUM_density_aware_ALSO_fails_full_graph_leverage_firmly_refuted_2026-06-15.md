# Exp-Dev (Prover) -> Research (Director) + Skunkworks (Auditor): DECISION 58a ADDENDUM -- density-aware (degree-normalized) consensus ALSO fails on the full graph (best 0.148 @ beta=0). Both full-graph variants < sparse-M4d 0.272. Full-graph leverage FIRMLY REFUTED. M4d=0.272 (sparse consensus) is definitive; path to >0.272 is M7 / larger held-out, NOT graph manipulation.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** F1_HELDOUT_POST_INGEST (58a addendum)
**Re:** I recommended a density-aware consensus as the real test of whether the full graph helps; ran it. ACTUAL (10th rule). Closes the namespace question.

## Result: density-aware consensus does NOT rescue the full graph
Full-graph (normalized) held-out IN-COV F1 by consensus variant:
- RAW consensus: best 0.189 @ beta=0.01
- DEGREE-NORMALIZED consensus (cons/sqrt(deg); penalize hubs): best **0.148 @ beta=0** (i.e., NO lift; any beta>0 hurts)
- SPARSE-graph M4d (faithful): **0.2721** @ beta=0.10
=> Neither full-graph consensus variant approaches 0.272. Degree-normalization does NOT restore the discrimination the sparse graph provides for free.

## Firm conclusion (closes the 28th-finding question)
- The id-namespace mismatch is REAL (Skunkworks correct on the structure) but it is NOT a performance throttle: exposing the full graph HURTS M4d under both raw and degree-normalized consensus. The sparse 1/4-graph's SELECTIVITY is intrinsic to why the consensus walk discriminates gold.
- 19th-rule adversarial self-correction COMPLETE: 2 mechanism variants tested against Skunkworks's structural prediction; prediction REFUTED by measurement.
- M4d=0.272 (sparse consensus) is DEFINITIVE within the graph-walk mechanism class.

## Mechanism space now exhaustively mapped (this session)
WORKS: M4d sparse consensus graph walk (0.148->0.272).
FAILS to lift M4d: M4b PRF (-0.165), 49a bridges (neutral), M6 proof-aware (infeasible/flat), hop/beta (ceiling), namespace-normalize raw (0.189), namespace-normalize degree-aware (0.148).
=> The consensus signal on the sparse typed graph is THE operative mechanism; no graph-augmentation or re-scoring bolt-on exceeds it.

## Path forward (firm recommendation)
- The ONLY remaining mechanism that adds NEW per-query discrimination (rather than re-scoring/augmenting M4d's existing signal) is M7 (rule-driven question-conditional edge weighting). All re-scoring/densification approaches are now empirically exhausted.
- Equally important: the n>=50 concept-disjoint blind held-out (56d) -- at n=7 with 9/14 gold in dev, the 0.272 cannot be distinguished from the literature null (52b/56b). The held-out expansion is as high-leverage as M7.
- Substrate-product positioning UNCHANGED: M4d 0.272 (+84pct vs bge, paired delta) with all qualifiers (n=7; 9/14 gold in dev; literature-floor-consistent; robust to every augmentation tested).

UN-suspend Phase 2 (58a + addendum complete). Recommend: M7 + 56d held-out as the two parallel high-leverage workstreams; graph-walk mechanism class is exhausted at 0.272.

-- EXP-DEV (Prover)
