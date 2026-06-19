# Research drill: asymmetric retrieval leg degradation methodology (2x DEEP)

Date: 2026-06-12
Drill type: 2x DEEP operational drill (level-2) on prior FINDING from distractor-density-ceiling drill
Prior drill: research_drill_distractor_density_ceiling_vector_retrieval_corpus_growth_2x_2026-06-12.md
Topic: Literature-grounded testing methodology to measure asymmetric leg degradation in a UNION of (a) structural HRR-encoded algebra cosine and (b) bge text-similarity cosine, as corpus density grows. Identify which leg literature predicts degrades faster.

## Drill spec

- Two retrieval legs measured at corpus densities N1 < N2 < N3
- Generic-term external queries only (per query-privacy)
- Output: pre-registered prediction + measurement protocol + cell design
- Calibration penalty: deflate P by 0.20; cap novel-synthesis P at 0.50

## Round 1 findings (compact)

1. Dense retrieval scaling laws (Fang/Zhan SIGIR 2024): dense models follow power-law in model + data size; contrastive log-likelihood used as evaluation metric. Establishes that dense leg has measurable scaling curves but they are model+data driven, not corpus-density driven directly.
2. BEIR (Thakur et al. NeurIPS 2021): dense embeddings often UNDERPERFORM BM25 out-of-distribution; no single approach dominates; in-domain performance does not correlate with generalization. Key takeaway: dense leg is more fragile under distribution / sparsity shift than BM25.
3. Hubness in high-dimensional embeddings (Radovanovic; Nielsen 2024 on Sentence-BERT): hubness produces ASYMMETRIC neighborhood relations - a few hubs appear as nearest neighbors of many items; many antihubs are neighbors of none. Hubness GROWS with corpus density. This is direct mechanism for dense leg degradation: more items mean more concentrated distance distribution and more hub-collisions.
4. BM25 scaling (multiple): BM25 IDF estimation IMPROVES with corpus growth; absolute gains of ~8% on short-form queries from corpus scaling. BM25 robust across BEIR. Index footprint sub-linear. BM25 is the BENEFIT-from-corpus-growth leg, not the degrades-from-it leg.
5. RRF / hybrid fusion (Cormack; multiple recent): RRF operates on ranks not scores; additive complementarity yields significant gains over best standalone. But complementarity attribution at varying corpus densities is NOT systematically measured in the open literature - this is the gap.
6. VSA / HRR capacity (Plate; Frady-Sommer; Thomas et al. arXiv 2301.10352): HRR capacity grows LINEARLY with dimension D under ideal conditions. Distractor pool n competes with stored items; retrieval fails when any distractor cosine exceeds correct cosine. For fixed D, increasing n monotonically degrades the structural leg precision.

## Round 2 findings (compact, refined)

7. Hubness emergence mechanism (Radovanovic-Nanopoulos-Ivanovic; Feldbauer; Nielsen): hubness is an intrinsic property of i.i.d. embeddings clustered in a narrow hyperspace core; growth with corpus size produces increasing skew in k-occurrence distribution. Hubness-reduction (mutual proximity, local scaling, Sinkhorn normalization) recovers significant retrieval accuracy. Empirically: dense leg degrades super-linearly in some regimes once density crosses a threshold.
8. BM25 IDF saturation under corpus growth: IDF estimation stabilizes as N grows; term-frequency saturation by k1; document-length normalization by b. No reported asymptotic precision collapse for lexical match where surface tokens remain distinct. Tail-query behavior is the weak spot but not corpus-density driven per se.
9. Per-component ablation methodology (multiple hybrid-retrieval papers, including HyReC, Local-Hybrid RAG-QA, DynamicER): standard protocol disables one component at a time, measures Recall@K and MRR@K with bootstrap CIs, reports complementary error reduction. Local-Hybrid RAG-QA explicitly attributes recall to (a) entity-based, (b) embedding-based, (c) multi-seed traversal; finds entity-based recall is condition-intensive and dominates anchored queries.
10. Structural vs lexical entity-linking (Pan et al. 2024 Electronics; SANOM): "Structural information is advantageous in DENSELY structured datasets; semantic information is helpful in SPARSE datasets." This is the LITERATURE DIRECTIONAL PRIOR: structural similarity holds UP better under density growth than semantic / lexical similarity does, PROVIDED the structural encoding has dimensional headroom.
11. VSA distractor pool scaling (Thomas 2023 capacity analysis): capacity = O(D / log n) under union bound for orthogonal codes; for HRR with composite binding, capacity headroom is dimension-bounded but VERY large when D is HD (1024+) and items are O(thousands). For substrate D ~ 1024 and N up to ~10K items, structural leg has ample dimensional headroom; bge dense leg in similar dim but trained-on-text has hubness-mediated collisions earlier.

## Synthesis

The literature prior is NOT symmetric. It points in one direction for substrate's UNION:

- The **text-embedding (bge) leg should degrade FASTER** than the structural-HRR-algebra leg as corpus density grows.
- Mechanism: hubness emergence in trained dense embeddings produces asymmetric neighborhood collisions that compound with corpus size. Trained embeddings cluster on a narrow manifold; new items add density to that manifold; distance concentration tightens; hubs absorb nearest-neighbor mass disproportionately. The dense leg loses discrimination first.
- The **structural HRR-algebra leg should degrade SLOWER** because (a) HRR composite bindings spread items closer to uniform-on-sphere by design (random rotations, FHRR multiplicative or HRR convolutional binding); (b) dimensional headroom O(D/log n) is far from saturation at substrate scales; (c) literature on structural-vs-lexical entity linking explicitly states structural dominates in dense graphs.
- However: structural leg has an OOV failure mode for content-references / free-text mentions not encoded as bindings. So absolute Recall floor may be lower even when degradation rate is slower.
- Net: asymmetry favors structural-leg ROBUSTNESS to density growth; UNION lift will increasingly be CARRIED BY structural leg as density rises; bge leg becomes the noise-injection floor.

Mechanistically restated: lexical hashes (sparse / BM25-like) have FIXED token entropy; trained dense (bge) lives on a LEARNED manifold with concentration; structural HRR has UNIFORM dimensional spread by construction. Concentration causes earlier collision-rate growth; uniform spread delays it. Substrate-novel point: the UNION's empirical asymmetry should be DIAGNOSTIC of which leg is in distress.

## Pre-registered prediction (HARD-PASS / HARD-FAIL)

Substrate experiment at corpus densities D1 (current ~240 atoms / 1742 corpus), D2 (~600), D3 (~1200), top_k = 5 evaluation against gold set:

- HARD-PASS: bge-leg-only Recall@5 drops by >= 1.5x the drop rate of algebra-leg-only Recall@5 across D1->D3. Specifically: if algebra-leg drops by Delta_a, then bge-leg drops by >= 1.5 * Delta_a. RRF UNION drop is bounded above by min(Delta_a, Delta_b) within 0.05 absolute.
- HARD-FAIL: algebra-leg-only Recall@5 drops FASTER than bge-leg (literature direction REFUTED for substrate; means substrate algebra encoding has hidden concentration / cluster-collision issue worth surfacing).
- MIDDLE-BAND: bge and algebra drop at within +/- 30% relative rate. Indicates the legs are similarly stressed; substrate is in a regime where neither leg dominates degradation.
- Pre-registered numerical bands:
  - Delta_bge / Delta_algebra >= 1.5 = HARD-PASS
  - 0.7 <= Delta_bge / Delta_algebra < 1.5 = MIDDLE
  - Delta_bge / Delta_algebra < 0.7 = HARD-FAIL

P(HARD-PASS) deflated = 0.45 (literature directional prior strong; substrate-specific bge fine-tuning state unknown; novel-synthesis cap 0.50; calibration penalty -0.20 applied to raw 0.65).

## Honest uncertainty bounds

- STRONG: hubness mechanism for trained dense embeddings (multiple replications across image, text, sentence-BERT, cross-modal); HRR linear-in-D capacity (Plate; multiple).
- MODERATE: directional asymmetry that bge degrades FASTER than HRR-algebra at substrate corpus densities. Depends on bge model's specific manifold concentration; unknown without measurement.
- SPECULATIVE: exact 1.5x ratio threshold for HARD-PASS. Chosen as a clearly-discriminating cliff; literature does not give a number for this specific UNION.

## Cross-thread synthesis

- Prior distractor-density-ceiling drill (2026-06-12) established that VSA distractor collision rate scales with corpus growth; this drill localizes WHICH leg of the UNION absorbs that collision rate first.
- Aligns with substrate's content-references vs semantic-vec two-axis finding (memory: substrate_two_axes_semantic_vs_content_referenced_2026-06-11): two orthogonal axes => two distinct degradation modes; this drill predicts dense (semantic-vec / bge) is the fragile axis.
- Refines RULE 12 (substrate partition framing): partitions that route through dense-embedding similarity are more density-sensitive than those routed through structural binding.

## Substrate-product implications

- If HARD-PASS: substrate-product positioning gains an empirical scaling argument: as the knowledge base grows, the structural HRR leg becomes the load-bearing component while LLM-style dense embedding becomes accuracy floor. Justifies algebra-primary + bge-OOV-fallback hybrid as the asymptotically-correct architecture.
- If MIDDLE: both legs share load; UNION remains the canonical pattern but neither leg can be deprecated.
- If HARD-FAIL: structural encoding has a hidden concentration issue; would trigger an investigation into HRR composite-binding entropy (per Plate's worry on naive HRR numerical stability).
- Operational tool: per-leg degradation slope is a CHEAP dashboard signal for substrate's corpus-growth health.

## Cell design

Name: cell_asymmetric_leg_degradation_density_curve
Compute target: CPU local (PartitionedStore stats + index probes, no torch model load)
Hours: ~30-60 min total

Procedure:
1. Build / select three substrate snapshots at corpus densities D1, D2, D3. D1 = current state; D2 = D1 + ~360 atoms (sample from research_history backfill); D3 = D1 + ~960 atoms.
2. For each density, hold the SAME gold evaluation set Q (~60 queries with known target atoms, mix of structural / mention / mixed intent).
3. Measure per-leg Recall@5:
   - algebra-only: query through algebra_index.py only, fetch top_k = 5, compute Recall@5 vs gold.
   - bge-only: query through bge text-similarity only on entity-names+aliases, top_k = 5, Recall@5.
   - UNION RRF (weights 0.6/0.4 per current canonical): top_k = 5, Recall@5.
4. Compute Delta_a = Recall@5_algebra(D1) - Recall@5_algebra(D3); Delta_b = analogous for bge; Delta_u for union.
5. Compute ratio Delta_b / Delta_a; classify against pre-registered bands.
6. Bootstrap CI (1000 resamples on Q) on each ratio.
7. Also log: per-query which leg surfaced gold; track per-leg disagreement rate D1 vs D3; track hubness proxy (top-5 hub concentration: fraction of all retrievals captured by top 1% most-frequent retrieved atoms) on bge leg only.
8. Halt criteria: ratio classification stable across bootstrap (>= 80% of bootstrap samples land in same band).

Deliverable: one verdict file with raw per-leg Recall numbers at D1/D2/D3, ratio, bootstrap CI, hubness proxy, band classification.

## Citations (verified)

1. Fang et al. SIGIR 2024 - Scaling Laws For Dense Retrieval - arXiv:2403.18684
2. Thakur et al. NeurIPS 2021 - BEIR - arXiv:2104.08663
3. Nielsen 2024 - Hubness Reduction Improves Sentence-BERT Semantic Spaces - arXiv:2311.18364
4. Feldbauer-Flexer 2018 - A comprehensive empirical comparison of hubness reduction in high-dimensional spaces - Knowledge and Information Systems
5. Radovanovic-Nanopoulos-Ivanovic 2010 - Hubs in space: popular nearest neighbors in high-dimensional data
6. Plate 2003 - Holographic Reduced Representations
7. Thomas-Dasgupta-Rosing 2023 - Capacity Analysis of Vector Symbolic Architectures - arXiv:2301.10352
8. Schlegel et al. 2021 - A comparison of vector symbolic architectures - Springer
9. Cormack-Clarke-Buettcher 2009 - Reciprocal Rank Fusion outperforms Condorcet
10. Pan et al. 2024 - Integration of Semantic and Topological Structural Similarity for Entity Alignment without Pre-Training - Electronics MDPI
11. Faggioli et al. CEUR 2024 - Reciprocal Rank Fusion Based Hybrid Dense-Sparse Retrieval
12. Frady-Sommer 2019 - Robust computation with rhythmic spike patterns

Verified count: 12

## Routing line

P_deflated = 0.45; next-drill candidate: free-probability (Tracy-Widom edge for HRR composite binding eigenvalue tails to validate "uniform-on-sphere by construction" claim quantitatively)
