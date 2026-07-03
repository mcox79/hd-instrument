# Layer 0.75 candidate-refinement primitive — design synthesis (drills A + B + C, 2026-07-03)

**Status:** all 3 drills landed 2026-07-03. Design finalized. Ready for hdi_exp_dev dispatch.

## Drill B critical update: noise-at-K=30 was a RED HERRING for our regime

Drill B computed Frady-Sommer SNR = √(N/M) = √(4096/30) ≈ 11.7 for our regime. Argmax error probability ~10^-15 under i.i.d. codes. Empirical loses factor 1.5-3× with correlated codes; still safe. Empirical breakdown at K ≈ N/(2·log D) — for our regime that's ~200 items, NOT 30.

**Corrected diagnosis:** Exp 3 failure is NOT information-theoretic vector noise. It's **semantic candidate contamination at the graph level** — 28 wrong chunks are semantically-adjacent distractors (hub-adjacent facts), not i.i.d. random. Composition can't distinguish query-relevant from query-irrelevant when 28/30 candidates are all plausible.

**Confirms Skunkworks direction:** don't escalate FULL N_DIM=8192 (path c); build Layer 0.75 primitive to filter semantic contamination (path a). Drill B closes the argmax-noise question.

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

## Substrate-mine findings (2026-07-03; via Explore agent) — REUSE not REINVENT

Substrate-mine sweep found significant in-house prior work informing Layer 0.75:

**Reuse (do NOT rewrite):**
- **MMR canonical impl:** `experiments/exp_h1_mmr_diversified_retrieval_rescue_v1.py:52-61` — `mmr_select(q, items, k, lam)`, HP-verified (propagation 0.433 → 0.067)
- **Inverse-density reweighting** for hub-dampen: `experiments/exp_h3_inverse_density_reweighting_rescue_v1.py` — down-weight by local density; direct precedent for stage 2
- **Query-conditioned rescore:** `hdlab/modern_hopfield_readout.py::top_k_by_retrieved` — ready-made softmax-cosine over candidate set
- **Composable primitives:** `hdlab/multi_hop.py::partition_routed_chain` (adjacent to hub-dampening), `hdlab/cleanup_family.py::k_NN_lookup(k=…)` (top-k averaging)

**Parameter corrections:**
- **λ_MMR = 0.3 (NOT 0.5)** — prior `exp_h2_mmr_lambda_rho_envelope_v1.py` showed λ=0.7 fails at ρ=0.8; λ=0.3 is safe general default

**Design adjustments:**
- **K-sweep as novel axis:** substrate has NEVER run K-sweep as load-bearing axis; Layer 0.75 first cell to do so — K_in ∈ {10, 15, 20, 30} × K_out ∈ {2, 3, 5}
- **DISTINCT_HASHES pre-check** per CSLS+MMR 2026-06-12 HARDFAIL: rerank cannot fix exact encoding collisions; halt if top-30 candidates have collisions
- **Dual HP bar:** (a) MAIN ≥ 0.74 = full arc closure vs ORACLE_0.822; (b) MAIN ≥ Exp 3 baseline 0.411 = non-negative interface. Original prereg used (a) only.

**Precedent for pattern (interface between working components fails):**
- 2026-06-22 `experiments/exp_substrate_native_qa_hotpotqa_v2_composition_drill.py` — HotpotQA cell HARD_FAILed 0.010 EM vs GENERATION_ONLY 0.122 EM (retrieval sabotaged composition). Same shape today.
- 2026-06-10 `research_drill_biological_overcome_compositional_depth_3x_2026-06-10.md` — Rank-1 anchor "ATTRACTOR-AT-EACH-LEVEL" between shard boundaries; Rank-2 anchor "LATERAL-INHIBITION-CLEANUP" winner-take-K'=3; Rank-7 "BOUNDED-K-PER-LEVEL" K ≤ 4-6 per Cowan chunking
- 2026-06-12 `research_drill_network_science_graph_theory_C_axis_PPR_informing_2x_2026-06-12.md` line 146 explicitly noted "hub atoms dominate adjacency-spectrum → PPR mass concentrates on hubs regardless of query → mitigation: PPR with degree-normalization"

**Assessment:** Layer 0.75 is standing-on-shoulders, not novel. Genuinely novel primitive = node-specificity IDF (Stage 1). Everything else exists in-house.

## Drill B answers (FINAL, 2026-07-03)

- IS argmax noise at (K=30, N=4096) the primary problem? **NO.** SNR ≈ 11.7 in Frady-Sommer terms; argmax error probability ~10^-15. Deep in safe zone.
- Would larger N alone solve it? **NO.** Doesn't address root cause (semantic contamination); wastes compute.
- Better cleanup mechanisms? Softmax/modern-Hopfield marginal at K=30; iterative resonator overkill for our case. **Not needed at K=30.**
- What K target for Stage 3? **≤5** (matches HippoRAG/BridgeRAG/PropRAG primary K; well within FHRR-argmax safe zone at N=4096).

**Additional Drill B mitigations noted for future use (but not needed for v1):**
- Softmax/modern-Hopfield cleanup — for future scale-up (K approaching 100+)
- FHRR/GHRR encoding — already using FHRR
- Well-separation regularization at code-generation time — relevant for encoder work, not this primitive

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
