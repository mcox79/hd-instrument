# Research drill: substrate graph-edge typology for content-relevance propagation (1x scoped)

Date: 2026-06-12
Drill type: 1x scoped literature scan informing Stratified Hybrid L4 GNN architecture
Field: network-science-graph-theory (Tier-1b new) x heterogeneous-GNN-IR literature
Queries: 6 generic literature; no substrate-specific terms transmitted externally

## HEADLINE

Literature converges: content-relevance propagation should use subsumption (INSTANCE_OF / hypernymy) and topical co-occurrence (SHARES_FILLER / TOPIC_OF) edges as primary; role-binding (OPERATES_ON) edges as conditional; computational-dependency (DEPENDS_ON) edges as DO-NOT-USE for free-text relevance. Per-edge learned weights via R-GCN-style heterogeneous attention (HAN / RAMHN / RSHN) is the safe meta-architecture: it permits DEPENDS_ON to be present but learn near-zero weight, recovering the unweighted-no-propagation baseline as a degenerate case. Lit P(this principle generalizes to substrate's algebra-HRR graph) = 0.55, deflated to 0.40 per uncharted-regime penalty.

## Drill spec

Question: Why did 2-hop DEPENDS_ON propagation degrade free-text retrieval F1, and which edge types should L4 GNN message-pass over for content-relevance instead?

## Findings

Finding 1: Heterogeneous GNNs treat each edge type as a separate parameter class.
- R-GCN learns one weight matrix W_r per relation r; basis decomposition keeps params tractable when |R| is large
- This is the literature-standard answer to "which edge types help": let the model learn it per relation
- Implication: a single GNN that includes ALL substrate edge types with per-relation weights subsumes any hand-picked subset; the learned weight for a content-irrelevant relation goes to ~0

Finding 2: Semantic-level attention (HAN, RAMHN, ML-HAN) explicitly weights meta-paths by task utility.
- HAN: node-level attention over neighbors + semantic-level attention over meta-paths (relation sequences)
- Empirically, removing or down-weighting task-irrelevant meta-paths is exactly what semantic attention does at train time
- For retrieval: meta-paths that encode topical adjacency (entity -> mention -> entity, or atom -> shares-filler -> atom) consistently dominate

Finding 3: Dependency-class edges hurt when used unweighted for content propagation; literature framing.
- Edge-driven biomedical IR (Sciencedirect 2024) constructs query-doc graphs with distinct edge types: semantic-association, mention, knowledge-link; ablations show removing topical edges degrades while removing structural dependency edges does NOT degrade and sometimes improves
- CorefDiffs (Co-referential / Differential edges): removing differential (dependency-like) edges has mixed effect; removing co-referential (content) edges always hurts
- Personalized-PageRank literature: anchor mass that leaks via low-content-affinity edges biases toward weakly-related nodes (search-spam analogue) and degrades precision; substrate's empirical degradation matches this pattern

Finding 4: Subsumption / hypernymy edges are nuanced — useful for query expansion, harmful for over-generalization.
- Springer 2025 hypernymy-detection HGNN: hyponymy edges help when threshold-calibrated; uncalibrated propagation along IS-A causes drift to overly-general concepts (degrades precision at k)
- Implication for INSTANCE_OF: keep, but calibrate hop count (1-hop safer than 2-hop) and apply learned attenuation per hop

Finding 5: Multi-edge-type IR systems use synonym / context / relation edges in parallel with learned weights.
- Recent GraphRAG / "Breaking the Static Graph" (arxiv 2602.01965): three edge classes — relation edges (OpenIE triples), synonym edges (linguistic variation), context edges (passage-to-entity); per-edge-type weights learned end-to-end
- Mirrors substrate: SHARES_FILLER ~ context, INSTANCE_OF ~ synonym/hypernymy, OPERATES_ON ~ relation, DEPENDS_ON ~ none of these (it's a computational-precedence edge, semantically orthogonal to content)

## Synthesis

- DEPENDS_ON encodes computational precedence (A needs B to compute), which is orthogonal to "B's content is relevant when query mentions A's content." Literature precedent for content-irrelevant edge classes degrading PPR-style propagation is robust (Findings 3, 5).
- The empirical 2-hop DEPENDS_ON F1 regression is consistent with the literature failure-mode: relevance mass leaks to dependency-neighbors whose content does not match the free-text query.
- Per-edge-learned-weight architectures (R-GCN, HAN, RAMHN) are the literature-converged remedy: they preserve the option of including DEPENDS_ON while learning to ignore it. This is strictly safer than hand-pruning, because (a) some edge types may be task-conditional (OPERATES_ON helps for "what method does X use?" queries but not "what is X about?" queries), and (b) the unweighted-no-propagation baseline is recoverable as a degenerate weight setting.
- Per [[feedback-literature-is-not-oracle]]: literature provides PRIOR; substrate-specific empirics REFINE. The substrate-specific empirical that DEPENDS_ON degraded is consistent prior evidence but does not preclude task-conditional usefulness (e.g. "what depends on X?" queries would obviously want DEPENDS_ON).

## Edge-type recommendation table

| Edge type | Class | Use for free-text content-relevance? | Literature support |
|---|---|---|---|
| INSTANCE_OF | subsumption / hypernymy | YES (1-hop, attenuated) | HAN, Springer 2025 HGNN; calibration warning |
| SHARES_FILLER | topical co-occurrence | YES (primary signal) | Edge-driven IR 2024; CorefDiffs co-referential; GraphRAG context edges |
| TOPIC_OF | topical | YES (primary signal) | Same as SHARES_FILLER class |
| OPERATES_ON | role-binding | LEARN_WEIGHT (task-conditional) | RAMHN multiplex; relation edges in GraphRAG |
| SERVES_AS | role-binding | LEARN_WEIGHT | Same |
| PART_OF | hierarchical | LEARN_WEIGHT (1-hop) | Meronymy edges, mixed empirical |
| DEPENDS_ON | computational precedence | NO (or LEARN_WEIGHT with strong prior 0) | Failure-mode-consistent with PPR leakage; empirically degraded; no literature support as content edge |
| SHARES_BACKBONE | structural | LEARN_WEIGHT | Multiplex GNN handles |

## Falsifiable predictions

- HARD-PASS: per-edge-weight R-GCN-style L4 head over all edge types beats no-propagation baseline by >= +0.02 F1 on free-text retrieval, AND learned weight for DEPENDS_ON is < 0.20 (normalized).
- HARD-FAIL: if learned weight for DEPENDS_ON is >= 0.50 OR per-edge R-GCN underperforms no-propagation baseline by > 0.01 F1, the substrate is in a regime where literature priors do not transfer — escalate to substrate-novel edge-typology design.

## Cheap decisive test

Train a single-layer R-GCN over substrate atoms with 6-8 edge types, basis decomposition B=3-4, score retrieval F1 on free-text query benchmark vs no-propagation. Inspect learned per-edge attention weights. ~1 day implementation, ~2 hr remote CPU. No bge load required at scoring time.

## Stratified Hybrid L4 GNN architectural recommendation

- Architecture: R-GCN / HAN hybrid. Per-edge-type weight matrix (R-GCN body), semantic-level attention over meta-paths (HAN head).
- Edge whitelist for v1: SHARES_FILLER, INSTANCE_OF (1-hop), TOPIC_OF as content-primary; OPERATES_ON, SERVES_AS, PART_OF as learn-weight; DEPENDS_ON included but initialized with strong prior weight 0 (or omitted in v1, added in v2 with task-conditional gating).
- Hop budget: 1-hop default; 2-hop only with attenuation factor learned per edge type (per Finding 4).
- Recoverable degenerate: if all learned weights collapse to 0, system reverts to bge-only retrieval (no-propagation baseline), matching algebra-primary + bge fallback hybrid from prior cycles.

## Substrate-product implications

- Substrate's edge typology is the asset, not a liability — the L4 GNN can exploit it via per-edge-learned-weight architectures.
- The earlier DEPENDS_ON propagation failure is a literature-predicted failure mode, NOT an architectural ceiling.
- Substrate-product positioning: substrate exposes typed edges with semantic meaning (DEPENDS_ON vs SHARES_FILLER vs INSTANCE_OF), which is exactly what modern heterogeneous GNN IR consumes; LLM embedding-only retrieval cannot match this expressivity.

## Honest scope

- STRONG: heterogeneous-GNN per-edge-weight architectures (R-GCN, HAN) are mature and widely validated for IR re-ranking and multi-relation entity retrieval.
- MODERATE: the specific principle "computational-dependency edges hurt content-relevance propagation" is consistent across 3 lit sources but no paper explicitly tests DEPENDS_ON-style edges. Inference from edge-class taxonomy.
- SPECULATIVE: the DEPENDS_ON learned weight prediction (< 0.20). Substrate-specific empirics will refine.

## Cross-thread synthesis

- Aligns with memory `substrate_vsa_position_is_meaning_validated_2026-06-12`: hybrid algebra-primary + bge fallback with RRF; L4 GNN extends the algebra path with structured propagation.
- Aligns with `substrate_two_axes_semantic_vs_content_referenced_2026-06-11`: SHARES_FILLER captures content-reference axis (literally co-occurring); INSTANCE_OF and TOPIC_OF capture semantic-vec axis.
- Distinct from materials-physics drills (saturated field per advisor); this drill is in network-science-graph-theory (Tier-1b new field, scope-expansion eligible).

## Citations (verified count: 6)

1. R-GCN: Schlichtkrull et al., "Modeling Relational Data with Graph Convolutional Networks" — verified DGL docs / Kumo.ai RGCNConv guide.
2. HAN: Wang, Ji et al., "Heterogeneous Graph Attention Network" arxiv 1903.07293.
3. RSHN: "Relation Structure-Aware Heterogeneous Graph Neural Network" IEEE ICDM 2019 / par.nsf.gov 10166589.
4. RAMHN: "Relation-aware multiplex heterogeneous graph neural network" Knowledge-Based Systems 2024.
5. Edge-driven biomedical IR: "Knowledge enhanced edge-driven graph neural ranking for biomedical information retrieval" ScienceDirect 2024.
6. GraphRAG / "Breaking the Static Graph: Context-Aware Traversal" arxiv 2602.01965.

P_deflated: 0.40 (literature P 0.55 minus 0.15 uncharted-regime penalty per lit-scan-calibration-penalty rule; novel-synthesis aspect — applying R-GCN over substrate's specific edge typology — capped at 0.50 separately).

Next-drill candidate: network-science-graph-theory deeper — spectral-gap / Cheeger-bound predictions for substrate atom-graph retrieval quality given the recommended edge whitelist.
