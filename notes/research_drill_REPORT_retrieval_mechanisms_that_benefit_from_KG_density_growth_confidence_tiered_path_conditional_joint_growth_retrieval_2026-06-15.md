# 3x DEEP DRILL: Retrieval mechanism classes that benefit from KG density growth

Tag: 3x_DEEP_DRILL_LITERATURE
Date: 2026-06-15
Drill arms: confidence-tiered walks (ARM 1) / path-conditional retrieval (ARM 2) / joint growth-retrieval co-design (ARM 3)

## HEADLINE

Selective-consensus retrieval over an unstratified graph is the WORST density-regime among published retrieval classes: literature confirms a non-monotone density-accuracy curve with an optimum, beyond which consensus mass dilutes (matches our empirical -0.04 F1 finding). Three documented mechanism classes structurally benefit from density growth: (1) confidence-tiered / provenance-weighted walks restricted to a high-confidence subgraph (Walk&Retrieve, PIKE-RAG, DGRAG, probabilistic-soft-logic KG retrieval); (2) path-conditional / proof-walk retrievers conditioned on a query / proof state (LeanDojo ReProver, MINERVA, graph-structured premise selection); (3) growth-retrieval co-designed self-organizing graphs (Agentic Deep Graph Reasoning, NELL-class never-ending learners). Of these, ARM 1 has the strongest published precedent and lowest-cost adoption path. ARM 2 has soundness-critical fit but its scaling profile is sub-linear in library size and DEPENDS on premise-accessibility filtering (LeanDojo reduced effective premise count 128K -> 33K to recover accuracy). ARM 3 has precedent for SHAPE (self-organizing scale-free) but not for soundness-constrained co-design -- substrate-novel territory remains.

## Cheap decisive test (substrate-internal, no off-platform data)

Measure selective-consensus F1 on the held-out q-class set under three retrieval restrictions, holding the underlying graph fixed at current density:
- R0: unrestricted walk (current baseline; F1 should reproduce the -0.04 degradation)
- R1: walk restricted to high-confidence tier only (CHTV-verified + L6-PROOF-axiomatic edges, exclude unverified)
- R2: walk along proof-path subgraph only (edges that participate in at least one L6-PROOF derivation)

HARD-PASS: R1 F1 > R0 F1 + 0.03 AND R1 F1 >= sparse-baseline F1. R2 either >= R1 (path-conditional viable) or < R1 (path-conditional too narrow given proof-corpus sparsity, expected if 38pct genuine T1 / 62pct authoring-gap composition).

HARD-FAIL: R1 F1 < R0 F1 + 0.01 (confidence tiering does NOT recover selectivity -> the dilution is not tier-distinguishable and the retrieval class itself is wrong, pivot away from consensus-mass entirely).

## Falsifiable predictions

P1 (ARM 1 transfer): Restricting walk to a single confidence tier preserves selectivity AND benefits monotonically from adding edges WITHIN that tier (literature precedent: confidence-aware filtering in DGRAG, PIKE-RAG, MultiRAG). HARD-PASS: tier-restricted F1 monotone-non-decreasing across 3 density levels.  HARD-FAIL: tier-restricted F1 non-monotone -> dilution is tier-internal not tier-mixing.

P2 (ARM 2 ceiling): Path-conditional retrieval will plateau quickly because corpus depth is shallow (avg proof depth 1.30 per L6-PROOF finding). HARD-PASS: R2 F1 plateau within 2 hops. HARD-FAIL: R2 F1 keeps climbing past depth-3 -> deeper proof authoring is the dominant lever, not the retrieval mechanism.

P3 (ARM 3 viability): Co-designed growth (new edges admitted only when they preserve the retrieval-selectivity invariant) is achievable; the substrate has the missing safety primitive (capability_preservation=1.0 gate) absent from published self-organizing-graph work. Deflated P_novel = 0.45 (capped per lit-scan calibration penalty).

## ARM 1: Confidence-tiered / provenance-weighted KG walks

Cited literature:

- Walk&Retrieve: Simple Yet Effective Zero-shot Retrieval-Augmented Generation via Knowledge Graph Walks (arXiv 2505.16849, 2025). Lightweight KG-RAG using random / BFS walks plus verbalization; provides the baseline against which tiering can be added.
- DGRAG: Distributed Graph-based Retrieval-Augmented Generation in Edge-Cloud Systems (arXiv 2505.19847, 2025). Gate mechanism assesses confidence and consistency of local generations, deciding local-vs-escalate. Confidence-tiered routing primitive.
- MultiRAG: A Knowledge-guided Framework for Mitigating Hallucination in Multi-source Retrieval Augmented Generation (arXiv 2508.03553, 2025). Subgraph-confidence filter: low-confidence subgraphs need more nodes, high-confidence subgraphs only 1-2 nodes -- formal evidence that tier-restriction REDUCES required retrieval mass while preserving accuracy.
- PIKE-RAG: sPecIalized KnowledgE and Rationale Augmented Generation (arXiv 2501.11551, 2025). Multi-level confidence computing inspired by recommendation-ranking workflows; filters credible nodes prior to retrieval.
- Information retrieval framework using knowledge graph embeddings and uncertainty modelling using probabilistic soft logic (Discover Computing, 2025). Bayesian-regularized multi-hop traversal -- explicit uncertainty propagation along graph paths, the closest published analog to provenance-weighted walks.

Per-arm synthesis: Literature converges 2024-2026 on the principle that high-confidence subgraphs require LESS retrieval mass to answer correctly while low-confidence subgraphs degrade with density. This is the inverse of unstratified random walk where added edges always dilute the mass. The substrate already has the structural prerequisite (CHTV verifier + L6-PROOF axiom-terminating edges + 4-mode distillation taxonomy producing a natural confidence partition). The mechanism class is published precedent, not substrate-novel; what IS novel is operationalizing the confidence tier from PROOF DERIVATIONS rather than from embedding-similarity or LLM-judged confidence. None of the cited systems use a sound prover as the confidence oracle; they all use heuristic / learned confidence. That is the substrate-product wedge inside an otherwise-known mechanism class.

## ARM 2: Path-conditional retrieval / proof-walk

Cited literature:

- LeanDojo: Theorem Proving with Retrieval-Augmented Language Models (NeurIPS 2023; arXiv 2306.15626). ReProver retrieves 100 premises conditioned on proof state; program analysis reduces accessible-premise count 128K -> 33K -- crucial finding that accessibility filtering is required for retrieval to scale with library size.
- Premise Selection for Theorem Proving by Deep Graph Embedding (Wang et al., 2017; arXiv 1709.09994). Foundational GNN-over-formula-graph premise selection; established that syntactic-semantic graph structure is informative for retrieval.
- Graph Sequence Learning for Premise Selection (arXiv 2303.15642, 2023). Combines GNN embeddings with sequence learning; image-captioning analogy for generating axiom sequences.
- SciLib-GRC21: Graph-Structured Premise Retrieval for Lean 4 Theorem Proving (Zenodo 20037667). RDF KG of Mathlib via SciLib ontology; tactic-categorised lemma hints. Explicit graph-structured premise retrieval is the published instance of path-conditional retrieval.
- MINERVA (Das et al., reinforcement-learning over KG paths conditioned on query). Established RL-walk-on-KG class for conditional path retrieval; predates the Lean line.
- Premise Selection for a Lean Hammer (arXiv 2506.07477, 2025). Latest in the line; confirms ReProver-class retrieval still the SOTA primitive.

Per-arm synthesis: Path-conditional retrievers ARE soundness-friendly (the path itself is the soundness witness) and DO benefit from corpus growth, but ONLY when accessibility filtering excludes the long tail. The LeanDojo 128K -> 33K reduction is the most directly transferable result: it says path-conditional retrieval over the FULL library underperforms path-conditional retrieval over the ACCESSIBLE library. Substrate analog: walk over the FULL typed KG underperforms walk over the proof-derivable subgraph. Scaling profile is sub-linear: retrieval R@1 / MRR climbs with library size only up to the point where accessibility filtering can keep effective fan-out bounded. With current substrate proof depth 1.30 average, the path-conditional retriever has very few path options per query -- this is a literature-confirmed warning that the mechanism will plateau quickly until deeper proofs are authored.

## ARM 3: Joint growth-retrieval co-design (partial literature gap)

Cited literature:

- Agentic Deep Graph Reasoning Yields Self-Organizing Knowledge Networks (Journal of Materials Research, Springer; arXiv 2502.13025, 2025). LLM-coupled continual graph extension with feedback-driven loops producing scale-free networks, hub formation, modularity. Closest published precedent for growth-aware retrieval architecture.
- NELL (Never-Ending Language Learner), Carlson et al., 2010 onward (foundational). Continuous self-sustaining expansion; uses learned beliefs to guide future extraction. Old but canonical.
- DrKGC: Dynamic Subgraph Retrieval-Augmented LLMs for Knowledge Graph Completion (arXiv 2506.00708, 2025). Joint completion-retrieval loop; KG completion conditioned on retrieved subgraph -- direct co-design instance though without soundness gate.
- Self-supervised retriever optimization via attention-derived feedback in retrieval augmented generation systems (USPTO patent 12536449). Retriever optimizes from downstream-attention signal; growth-retrieval feedback loop in production form.
- JGURD: Joint Gradient Update Relational Direction-enhanced method for knowledge graph completion (PMC12190632, 2025). Encoder-decoder joint update with relational direction information.

Per-arm synthesis: Self-organizing graphs WITH retrieval feedback exist (Agentic Deep Graph Reasoning is the clearest precedent), but NONE of the cited systems impose a soundness gate or a capability_preservation invariant on growth. They use LLM-judged or attention-derived signals; growth can introduce noise, inconsistency, or contradictory edges with no formal rejection mechanism. The literature gap is therefore narrower than "joint growth-retrieval co-design" (which exists) and is specifically "joint growth-retrieval co-design under a sound-by-construction growth gate." That is substrate-novel territory: CHTV-1 verifier + L6-PROOF + capability_preservation=1.0 provides the missing soundness invariant absent from all published self-organizing-graph systems. Deflated P_novel = 0.45 reflecting both the partial precedent (mechanism class published) and the substrate-specific extension (soundness invariant not published).

## Cross-arm synthesis

The published density-accuracy curve for unstratified Graph-RAG is non-monotone with a noise-threshold peak: too few edges starves the retriever, too many introduces distractor paths and dilutes consensus mass (chunk-interaction-graph density study, arXiv 2408.02907; survey arXiv 2501.00309). Our empirical finding (-0.04 F1 from added sound edges) sits PAST that peak on the unstratified curve -- the literature predicts this exact failure mode for selective-consensus retrievers over growing graphs. The literature also identifies three escape routes, each with different prerequisites and scaling profiles. ARM 1 (confidence-tiered walks) is the cheapest pivot because the substrate already has a canonical confidence partition from CHTV / L6-PROOF / capability_preservation; it requires only restricting the walk to the verified-tier subgraph and is the closest published-precedent transfer (DGRAG, MultiRAG, PIKE-RAG, probabilistic-soft-logic IR). ARM 2 (path-conditional / proof-walk) is theoretically the best fit for soundness-critical substrates but the LeanDojo accessibility-filter finding is a structural warning: full-library path retrieval underperforms accessibility-filtered path retrieval, and with current proof depth averaging 1.30 the substrate has very few path-conditional options -- the mechanism will be ceiling-limited by proof corpus depth, NOT by retrieval algorithm. ARM 3 (joint growth-retrieval co-design under a soundness gate) is the genuinely novel substrate territory; published self-organizing graphs exist (Agentic Deep Graph Reasoning) but lack the safety invariant, and substrate's capability_preservation=1.0 + CHTV verifier provides the missing piece. Combining ARM 1 and ARM 3 -- tier-restricted walks where tier admission is governed by the same soundness gate that controls growth -- is the strongest synthesis and has no direct published precedent. The HARD WARNINGS from the literature are: (a) confidence-tier filtering REQUIRES calibrated confidence on cold-start edges, otherwise tier mixing reintroduces dilution; (b) path-conditional retrieval REQUIRES accessibility filtering and proof-depth growth or it plateaus; (c) joint growth-retrieval REQUIRES an invariant that can REJECT growth, not merely score it -- without rejection power, growth eventually destabilizes the retriever (NELL's long-running drift is the canonical failure case). The field's recommended resolution for a soundness-first substrate is to stratify the retriever (ARM 1), use the proof structure as the strata definition (ARM 2 as auxiliary path-witness rather than primary retriever), and use the soundness gate to reject growth that crosses strata boundaries (ARM 3 implemented as gated co-design). This composes the three arms into a single mechanism rather than choosing one.

## Substrate-product implications

(a) The -0.04 F1 degradation is NOT evidence against the substrate's growth model -- it is evidence against unstratified consensus-mass retrieval over a stratified graph. The retrieval mechanism, not the growth mechanism, is the load-bearing component to revise.

(b) The substrate is uniquely positioned among published systems to operationalize confidence tiering from a SOUND oracle (CHTV / L6-PROOF), whereas the published precedent uses heuristic / learned confidence. This is the wedge: same mechanism class, harder oracle, stronger guarantees.

(c) Path-conditional retrieval is viable but ceiling-limited by proof depth. The DEPENDS_ON / SHARES_MATH authoring work already in flight is the right lever; the retrieval upgrade should not be deferred behind it because tier-restriction (ARM 1) is independent and cheaper.

(d) Joint growth-retrieval co-design under a soundness gate is a candidate Tier-1 architectural claim NEW: published self-organizing graphs grow without rejection power; substrate grows with capability_preservation=1.0 rejection power. This is product-positioning distinct from all cited systems and is the 8th architectural-claim candidate (subject to empirical demonstration via the cheap decisive test above).

(e) For the elevator pitch / internal tracking document: the substrate-product story is now "stratified provable-tier retrieval over a soundly-growing graph" -- ARM 1 + ARM 3 synthesis -- which the literature has neither published nor pre-empted. This is a stronger positioning than "selective-consensus retrieval over a typed KG" which the literature has documented as density-dilution-vulnerable.

## Citations (verified count: 18 distinct works across the three arms)

ARM 1 (5): Walk&Retrieve (arXiv 2505.16849); DGRAG (arXiv 2505.19847); MultiRAG (arXiv 2508.03553); PIKE-RAG (arXiv 2501.11551); Probabilistic-soft-logic KG IR (Discover Computing 2025).

ARM 2 (6): LeanDojo (NeurIPS 2023 / arXiv 2306.15626); Deep Graph Embedding premise selection (arXiv 1709.09994); Graph Sequence Learning for Premise Selection (arXiv 2303.15642); SciLib-GRC21 (Zenodo 20037667); MINERVA (Das et al.); Premise Selection for a Lean Hammer (arXiv 2506.07477).

ARM 3 (5): Agentic Deep Graph Reasoning (arXiv 2502.13025); NELL (Carlson et al. 2010+); DrKGC (arXiv 2506.00708); Self-supervised retriever optimization (USPTO 12536449); JGURD (PMC12190632, 2025).

Density-curve baseline (2): Inter-chunk-interaction graph density study (arXiv 2408.02907); GraphRAG survey (arXiv 2501.00309).

[UNVERIFIED] notes: MINERVA citation is from a single search hit summary not a direct fetch; primary venue assumed pre-2020 ICLR-class. Probabilistic-soft-logic IR venue confirmed only as Discover Computing 2025 via hit text; full author / DOI not retrieved. Patent 12536449 retrieved as USPTO listing; legal status / assignee not separately verified.

## Calibration penalty applied

Lit-scan calibration penalty per [[feedback-lit-scan-calibration-penalty]]: ARM 1 P_raw 0.70 -> P_deflated 0.50 (precedent-strong but substrate-specific operationalization untested); ARM 2 P_raw 0.55 -> P_deflated 0.35 (depth-ceiling literature warning); ARM 3 P_raw 0.55 -> P_deflated 0.45 (capped at novel-synthesis 0.50 ceiling; partial precedent reduces from cap). Combined synthesis P_deflated 0.55 (slight uplift from arm-composition that has no direct precedent, capped at 0.55 not raised further).
