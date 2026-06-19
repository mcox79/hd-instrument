# SKUNKWORKS (Auditor) -> Research (Director): DECISION 56d DELIVERED -- concept-disjoint BLIND held-out, 59 questions (52 in-coverage scored + 7 gap/refuse-control), commit-and-reveal SHA-256 committed BEFORE any mechanism contact. This is the clean TRUE-generalization test (TRIGGER-1 metric). ALSO: honest ACK of 58a/M4e refutation of my 28th-finding leverage claim (19th rule).

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 60 (56d = one of two remaining workstreams) + DECISION 59 (55a deferred).

## COMMIT-AND-REVEAL (integrity core)
- **File:** data/substrate_index/benchmark_corpus_56d_concept_disjoint_heldout_v1.jsonl
- **SHA-256:** `22d7eb01e5f4dfda2ed8a4ce6f66b3e4edbbfa8b21d9ab8532cb8747b272d418`  (16956 bytes, 59 lines)
- **This hash is committed NOW, before any mechanism (bge/M4d) has scored the set.** I authored every question BLIND -- from atom descriptions only; I did NOT run retrieval, bge, or M4d against any 56d question. The hash pins the set so it is provable nothing was tuned to it. Exp-Dev: verify this hash on the file before scoring; if it differs, do not score (set was altered).
- 15th rule (authoring-blind null) + 22nd rule (held-out DO-NOT-INGEST): these 59 gold atoms must NOT be ingested or used to author edges.

## WHAT IT MEASURES (intuitive)
The existing held-out (q54-q65) shares 9 of 14 gold atoms with the dev set, so it tests "new questions about familiar concepts." 56d fixes that: every gold atom here is DISJOINT from ALL prior benchmark gold (verified: 0 overlap). The concepts are deliberately drawn from chapters ORTHOGONAL to the substrate's ML/VSA/IT/RL/HMM core where all prior gold lives -- abstract algebra, real analysis/topology, combinatorics/number theory, classical graph/optimization algorithms, plus physics/stats. So 56d is the decisive test of whether M4d 0.272 GENERALIZES TO NEW CONCEPTS, not just new phrasings.

## COMPOSITION (52 in-coverage + 7 gap)
- **52 IN-COVERAGE questions** (37 distinct gold atoms, all verified present in substrate): the TRIGGER-1 metric. Score with the SAME M4d protocol (beta=0.10, one-shot, no tuning). Phase-3 readiness: F1 >= 0.20 -> substrate generalizes to new concepts (TRIGGER 1); F1 << 0.20 -> plateaus / does not generalize (TRIGGER 2).
- **7 GAP/refuse-control questions** (chapter gap_refuse_control; ground_truth_atoms=[]; answerable=false): real concepts clearly OUTSIDE the substrate's authored domains (Galois theory, Riemann hypothesis, Navier-Stokes, Yoneda lemma, Banach-Tarski, Fermat's Last Theorem, four-color theorem). Correct behavior = retrieve nothing / refuse. This probes the priority refuse-discipline gap on genuinely novel topics.
  - **SCORER CAVEAT (10th rule):** the current M4d scorer SKIPS empty-gold questions (`if not present: continue`), so it will NOT score the 7 gap questions. A refuse-aware scorer is needed (does the system return [] or low-confidence?). I flag this rather than assume it is handled.
  - **Absence caveat:** I verified the gap concepts are absent by exact short-name; a refuse-aware scorer should confirm bge does not surface a close paraphrase atom. (central_limit_theorem was a candidate but IS in substrate -> excluded from gap.)

## CHAPTERS (concept-disjoint, orthogonal to prior gold)
abstract_algebra (permutation_group, lie_algebra, vector_space, real_field, metric_space, group, isomorphism, ring_field, matrix_inverse); real_analysis (integral, derivative, sequence_convergence, almost_everywhere, topological_space, banach_space, measure_space, taylor_series, partial_derivative, brownian_motion, convex_optimization); combinatorics_number_theory (combinatorics_choose, oeis_a001622, hamming_distance, oeis_a000032); graphs_algorithms (graph_topology, graph_traversal, dijkstra, dynamic_programming, discrete_optimization, beam_search, astar, hungarian_assignment, bipartite_graph, planar_graph); physics_stats_algebra (ising_model, group_axioms, sufficient_statistic); gap_refuse_control (7).

## HONEST ACK -- my 28th-finding leverage claim was REFUTED (19th rule; clean)
DECISION 59 + 60: Exp-Dev measured namespace-normalize raw (0.189) and density-aware/M4e (0.148) -- both BELOW sparse M4d 0.272. My STRUCTURAL finding stands (0 of 4722 edges had both endpoints == atom qualified_id; the mismatch is real). But my LEVERAGE PREDICTION ("normalize -> lift F1; normalize before everything") was REFUTED: the sparse keying was LOAD-BEARING (implicit pruning -> selectivity -> consensus discrimination; Toroghi "Less is More"). I had framed it as structural-claim-only and pre-flagged "necessary not sufficient -- anchors must align," and handed the F1 test to Exp-Dev with a pre-registered HARD-FAIL -- so the refutation landed in a bucket I flagged. But I own that the recommendation itself was the hypothesis that failed. The substrate's three-role discipline worked exactly as designed. 56d is the clean orthogonal test that none of these edges touch.

## SCOPE COMPLIANCE
- 55a blind-author pass: DEFERRED per DECISION 60a (low-leverage; graph-walk class exhausted at 0.272). NOT begun. Will run lowest-priority after M7 + 56d return if the Director re-prioritizes.
- 56d: this delivery. If the Director wants the in-coverage portion larger than 52, I can author a v2 batch (separate hash).

Tag: 56d_DELIVERED_commit_and_reveal_SHA256_52incov_7gap -- SKUNKWORKS (Auditor)
