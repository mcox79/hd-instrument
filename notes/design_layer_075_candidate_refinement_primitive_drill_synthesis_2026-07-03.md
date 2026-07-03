# Layer 0.75 candidate-refinement primitive — design synthesis (drill A + C, 2026-07-03)

**Status:** synthesis note; Drill B (VSA noise scaling) still in flight and will add parametric detail. Primitive dispatch HELD until Drill B lands.

**Purpose:** operationalize the candidate-refinement primitive between Layer 0.5 (PPR-walk output ~30 chunks) and Layer 1 (FHRR composition input needs ~2-5 clean chunks) discovered as a load-bearing gap by Exp 3 MB_INTERFACE_BOUND landing.

## Failure mode literature-named

Our Exp 3 result maps directly onto two independently-named failure modes in current KG-RAG literature:
- **Static Graph Fallacy** (CatRAG, arXiv 2602.01965) — fixed transition probabilities in PPR cause walk to divert to high-degree hubs before reaching critical evidence
- **Retrieval Coverage Gap** (iterative-RAG diagnostic, arXiv 2601.19827) — high partial recall but no complete evidence chain reaches downstream reasoning

Our numbers: Layer 0.5 achieves 0.993 bridge-recovery (per Exp 2C MEASURED_MECHANISM); Layer 1 achieves 0.822 composition F1 when fed correct 2 chunks (per Exp 3 ORACLE arm); composed pipeline 0.411 (per Exp 3 MAIN). Interface loss = 0.411 gap.

## Architecture (drill A + C convergence)

Both drills independently recommend the same 3-stage LLM-free architecture:

### Stage 1: Node-specificity seed re-weighting (graph-native IDF)

- **Mechanism:** each seed node's PPR personalization probability multiplied by `1 / (number_of_passages_containing_the_node)`
- **Precedent:** HippoRAG (arXiv 2405.14831); ablation: removing this drops MuSiQue R@2 from 40.9 → 37.6 (published)
- **Substrate-native compliance:** cheap, uses signals already in KGStore
- **Composes with:** existing `KGStore` graph structure, existing PPR primitive from Exp 2C

### Stage 2: Hub-dampening (edge weight normalization by degree)

- **Mechanism:** scale down outgoing edge weights of any node with degree > threshold (~50) so total mass through hubs is capped; relative ordering of neighbors preserved
- **Precedent:** standard PageRank literature + CatRAG dynamic edge weighting
- **Addresses:** our specific bipartite-forest topology where 15 hubs at deg>5 dominate mass regardless of query (identified by Exp 2C VET as "hub-and-spoke KG concentrates PPR mass on hubs regardless of specific query")
- **Substrate-native compliance:** parametric only, no learned components
- **Composes with:** PPR primitive; hub-dampening happens INSIDE the walk step, not as post-filter

### Stage 3: Query-conditioned rescore + MMR diversity finalizer

- **Mechanism:** for each candidate surviving stages 1+2, compute cosine(query, candidate); rank; apply MMR (Maximal Marginal Relevance) with λ ≈ 0.3-0.5 to remove near-duplicates
- **Precedent:** MMR (Carbonell & Goldstein 1998); BridgeRAG s(q, b, c) if bridge entity identifiable
- **Substrate-native compliance:** cosine + closed-form MMR; no external LLM, no training
- **Composes with:** existing dense encoder (bge or char-trigram); Layer 0 primitive
- **Design decision pending Drill B:** whether MMR alone is sufficient or whether we need learned reranker (ColBERT-v2 style) trained on graph-mined hard negatives

## Prereg criteria (draft; will finalize post-Drill-B)

- **HP:** Layer 0.5 + 0.75 composed pipeline MAIN ≥ 0.90 × ORACLE = 0.74 on same Exp 3 regime
- **HF:** MAIN < 0.60 × ORACLE = 0.493 (same as Exp 3 gate)
- **MIDDLE:** 0.493 - 0.74

Additional ablations for CG-tier eligibility:
- Ablate stage 1 alone → measure lift
- Ablate stage 2 alone → measure lift
- Ablate stage 3 alone → measure lift
- Compare 3-stage stacked vs any individual stage

## Bias controls / discipline compliance

- Positive control: forced-correct-answer path through primitive → must return the correct 2 chunks (verifies primitive doesn't break ORACLE regime)
- Negative control: random-query through primitive → NEG_CTL bounds
- CARDINALITY_OK prereg field
- Local_cpu SMOKE only per USER-locked
- ORACLE reference arm reproduced (verify composition primitive unchanged)
- Fix#28 per-arm off-disk verification

## Chain-grade primitive discipline

- Deliverable = SINGLE primitive (or minimal set of composable primitives), NOT full retrieval pipeline rewrite
- Must be Principle-11 composable: `KGStore` + `CharTrigramEncoder` + `PPR` + new `node_specificity_reweight` + new `hub_dampen` + new `query_rescore_mmr` primitives
- No new abstractions beyond what these 3 mechanisms require

## Composes with today's other findings

- **Substrate-ingest-integrity principle (USER 2026-07-03):** Layer 0.75 must NOT introduce silent truncation; every stage output must expose total-count-processed for downstream truncation detection
- **Director-KB is already a KGStore (drill KEY REFRAME):** Layer 0.75 operates on existing KGStore, no new graph construction needed
- **Encoder-swap DEFERRED (2026-07-03 pivot):** Layer 0.75 primitive uses existing bge/char-trigram frontend; encoder choice orthogonal to primitive design

## What's still open pending Drill B

Drill B is specifically about VSA/HRR argmax noise vs N_DIM × K scaling. Answers:
- IS argmax noise at (K=30, N=4096) actually the primary problem or is candidate contamination the primary problem?
- Would larger N (8192 / 16384) alone solve it without new primitive? (Skunkworks-blocked path (c))
- Are there better cleanup mechanisms than cosine argmax at K=30 that would be worth adding to Stage 3?
- What K target does Stage 3 need to hit for FHRR composition to reliably work at N_DIM=4096?

Pending Drill B, Stage 3's target K is estimated as ≤5 (matching HippoRAG/BridgeRAG/PropRAG published primary-metric K). Drill B may tighten or loosen this bound.

## Next steps post-Drill-B

1. Finalize prereg with K target from Drill B
2. Dispatch hdi_exp_dev to author the primitive (3-stage stacked)
3. SMOKE at same regime as Exp 3 (150 queries × 3 seeds, hub-concept-bridge scope)
4. Skunkworks landed-VET with focus on stage-ablation legitimacy
5. If HP: retrieval-architecture arc CLOSES; Layer 0.5 + 0.75 + 1 pipeline validated
6. If HP + closure: dispatch 170K-atom Director-KB scale re-test (Exp 1 + Exp 2C revival criteria)

## References (verified via drills A + C)

- HippoRAG — Gutierrez et al. NeurIPS 2024, arXiv 2405.14831 (node specificity IDF ablation +3pp)
- HippoRAG 2 — ICML 2025, arXiv 2502.14802 (query-aware dynamic edge weighting)
- BridgeRAG — arXiv 2604.03384 (tripartite scorer s(q, b, c))
- CatRAG "Breaking the Static Graph" — arXiv 2602.01965 (named the pathology)
- Iterative-RAG diagnostic — arXiv 2601.19827 (Retrieval Coverage Gap)
- PropRAG — Wang ACL 2025, arXiv 2504.18070 (2-stage LLM-free exploratory + exploitative)
- PullNet — Sun et al. EMNLP 2019 (learned pull classifier)
- GraftNet — Sun et al. EMNLP 2018 (PPR + GCN reader)
- MMR — Carbonell & Goldstein 1998 (closed-form diversity)
- Anthropic Contextual Retrieval — rerank stage empirically −67% failed retrievals when added
