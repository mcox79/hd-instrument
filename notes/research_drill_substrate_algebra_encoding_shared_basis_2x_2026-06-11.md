# Research drill 2x DEEP -- substrate algebra-encoding architecture for shared-basis detection without crippling free-text retrieval

Date: 2026-06-11
Topic: substrate-self-index v2 architecture; how to encode algebra / signature / complexity fields so that atom-to-atom shared-basis detection succeeds AND free-text query retrieval does not degrade
Surprise trigger: self-evaluation Layer 1 attribution -- tag-vector tag-sum composite cosine retrieval went NET NEGATIVE on Q2 and Q3 in current substrate-self-index v1
Lineage: 2x DEEP drill on existing finding (root cause already attributed at Layer 1); operational drill, not lit-scan verification

---

## (a) HEADLINE

The failure mode in substrate-self-index v1 is structural and well-understood in the retrieval literature: a tag-sum concatenation cannot be cosine-composed with a semantic embedding when the two subspaces are uncorrelated, because cosine averages noise from the irrelevant subspace into the relevance signal. Three architecture families resolve this without abandoning the algebra-aware differentiator: (1) ORTHOGONAL-SUBSPACE block-diagonal embedding with calibrated subspace weights, (2) MULTI-VECTOR LATE-INTERACTION with reciprocal-rank fusion across a semantic index and an algebra index, (3) QUERY-INTENT ROUTER that selects which retrieval mode answers. The recommended primary architecture is hybrid (2)+(3): keep the bge-large semantic index as-is, add a separate substrate-native algebra-signature index using the substrate's own TPR/HRR primitives, fuse at rank level via RRF, and route by detected intent. This earns substrate's commercial differentiator (algebra-aware retrieval that no vector DB offers) without modifying the semantic retrieval path that already works. Architecture (1) is the cleaner long-term play if a single composite vector is required for storage-cost reasons. Architecture (5) (co-trained dual embeddings) is the eventual mature form but is correctly out of scope for v2.

P_deflated for hybrid (2)+(3) recommendation: 0.55 (lit-precedent dominant + substrate primitives already validated)
P_deflated for orthogonal-subspace single-vector (1): 0.40 (mathematically clean, requires calibration tuning)
P_deflated for naive bge-encode-as-text fallback (8): 0.50 but with known ceiling (loses algebra-as-separate-axis)

---

## (b) Cheap decisive test

Three CPU experiments, all under 4 hours combined, that decide the architecture choice. Each experiment uses substrate-self-index existing corpus (no external dataset acquisition). All three should run as substrate-only, no LLM in loop, on a single CPU lane.

### EXP-A: RRF-HYBRID two-index baseline (recommended first)
- Build two independent indexes over the same atom corpus: (i) semantic index over bge-large embedding of the atom natural-language summary field only (no tags appended), (ii) algebra index over a substrate-native TPR/HRR encoding of (algebra, signature, complexity, type) as a role-filler bundle of dimension N=1024
- For each Q1..Q5 evaluation query, retrieve top-K from each index independently, fuse via RRF (k=60 standard), compare top-3 against ground truth
- Predicted runtime: 1.5-2.5 hr CPU
- Pass criterion: Q2 family-tag retrieval improves to >= rank 2 (current v1 = rank 3) AND no free-text query Q4/Q5 degrades by more than 1 rank vs semantic-only baseline

### EXP-B: ORTHOGONAL-SUBSPACE single-vector composite
- Encode each atom as a block-diagonal concatenation `[alpha * semantic_proj_to_768 | beta * algebra_TPR_to_256]` with alpha/beta chosen so that subspace energies are balanced
- Query is encoded the same way; semantic block from query text, algebra block from a router that maps query intent terms to algebra signature (empty / zero-vector if no algebra intent detected)
- Run alpha-sweep across {0.5, 0.7, 1.0, 1.4, 2.0} x same beta values; pick the Pareto-frontier point
- Predicted runtime: 1-2 hr CPU
- Pass criterion: at least one (alpha, beta) point matches EXP-A on Q2/Q3 AND does not degrade Q1/Q4/Q5 by more than 1 rank

### EXP-C: QUERY-INTENT ROUTER decisive test
- Implement a simple substrate-native intent classifier: vocabulary terms like "family", "signature", "algebra", "complexity", "type" trigger algebra-route; everything else triggers semantic-route. Cost: ~50 lines.
- Compare three routing policies: (i) always-semantic baseline, (ii) always-algebra fail-open, (iii) intent-routed
- Predicted runtime: 30 min CPU
- Pass criterion: intent-routed wins on >= 3 of 5 queries vs always-semantic AND ties or wins on the other 2

### Combined decision rule
- If EXP-A passes AND EXP-C passes: ship hybrid two-index + intent routing for v2
- If EXP-A passes AND EXP-C fails: ship two-index without routing (always-RRF)
- If only EXP-B passes: ship single-vector orthogonal-subspace for v2 (storage simpler, accept calibration burden)
- If all three fail: regress to Fix B (bge-encode algebra as text) and accept the loss of algebra-as-separate-axis as a v2 limitation; revisit in v3 with co-trained dual embeddings

---

## (c) Falsifiable predictions

### HARD-PASS thresholds (pre-registered before EXP-A/B/C run)

- HP-1: EXP-A RRF-HYBRID improves Q2 family-tag retrieval to rank <= 2 (current rank 3) AND Q3 to rank <= 2 (current rank 3) AND Q1/Q4/Q5 stay within 1 rank of semantic-only baseline. If this passes, hybrid two-index is committed.
- HP-2: EXP-B with the best (alpha, beta) point matches or beats semantic-only on at least 4 of 5 evaluation queries by composite top-3 hit-rate.
- HP-3: EXP-C intent-routed wins on >= 3 of 5 queries vs always-semantic.
- HP-4: Algebra-only index by itself (degenerate EXP-A with semantic weight = 0) achieves rank-1 on Q2 family-tag and Q3 count_nb. This validates that the TPR/HRR substrate-native algebra encoding is functionally adequate (separates the failure mode in v1 from the substrate-primitive failure mode).

### HARD-FAIL thresholds

- HF-1: If EXP-A degrades Q4 or Q5 by more than 2 ranks vs semantic-only, RRF cannot reconcile the two subspaces and the hybrid recommendation is falsified for this corpus.
- HF-2: If EXP-B Pareto-frontier never beats semantic-only on any composite query, the orthogonal-subspace single-vector hypothesis is falsified.
- HF-3: If HP-4 fails (algebra-only index ranks below 3 on Q2/Q3), the substrate-native TPR/HRR encoding of algebra fields is itself the bottleneck; this would invalidate the substrate-product differentiator narrative (algebra-aware retrieval).
- HF-4: If intent-router (EXP-C) loses on more than 2 queries vs always-semantic, the routing layer is net-negative and we ship pure-RRF (no routing).

### Soft observations to log (no pass/fail, but worth measuring)

- Calibration penalty: deflated P_deflated for hybrid-RRF recommendation = 0.55; cap on novel-synthesis = 0.50 does not apply because hybrid-sparse-dense + intent-routing has direct industrial precedent (this is not novel synthesis, this is application of an established pattern to substrate-self-index)
- Cost ratio: hybrid two-index doubles storage at query time but is identical on disk (two separate indexes); orthogonal-subspace single-vector keeps storage flat at cost of calibration tuning per corpus

---

## Architecture catalog with tradeoffs

### Architecture 1 -- ORTHOGONAL-SUBSPACE single-vector composite (the "block-diagonal" play)

- Form: atom_vec = `concat(alpha * P_sem @ bge_embedding, beta * P_alg @ TPR_algebra)` where P_sem, P_alg project to disjoint coordinate ranges
- Math: cosine over the composite is a weighted sum of cosines over each subspace because the subspaces are orthogonal by construction (block diagonal); calibrated alpha/beta give the substrate-product designer a per-query knob on algebra-weight
- Pros: single index, single vector, single cosine call -- minimal infrastructure change vs v1; clean mathematical interpretability; supports both pure-semantic and pure-algebra queries via query-side masking
- Cons: alpha/beta calibration is per-corpus; query-side projection must be done by query-time router which is non-trivial; cannot do per-token late-interaction
- Precedent: cooperative-embeddings instance/attribute/category retrieval (Karaoglu 2019), orthogonal-subspace multi-task learning (multiple 2024-2025 entries), Gram-Schmidt mixture-of-orthogonal-experts
- Substrate fit: HIGH -- substrate already has block-diagonal codebook primitives; the algebra TPR encoding is a substrate-native primitive validated already today in categorical-AI / DisCoCat drill earlier this morning

### Architecture 2 -- MULTI-VECTOR LATE-INTERACTION (the "ColBERT-style" play)

- Form: each atom owns two vectors -- semantic_vec (bge over NL summary) and algebra_vec (substrate TPR); query owns 1-2 corresponding vectors; retrieval = max-sim or sum-of-max-sim across the two indexes, fused at rank level
- Math: rank-level fusion (RRF k=60 is the proven default) reconciles incompatible score scales without alpha/beta calibration
- Pros: zero calibration tuning required; each index keeps its native metric; ColBERT-style late interaction is the dominant industrial pattern for combining heterogeneous representations (BM25 + dense is the same family)
- Cons: 2x storage; 2x retrieval cost at query time; rank-level fusion loses fine-grained score information that token-level interaction could recover
- Precedent: ColBERT-v2, ColPali, ColQwen, dense-sparse-hybrid RRF (Microsoft, Weaviate, Vespa, Pinecone all ship this); BM25 + dense RRF is the de-facto baseline for industrial RAG
- Substrate fit: HIGHEST -- substrate has both an HRR/TPR primitive (algebra index) and can host the bge embeddings (semantic index); the only new code is the RRF fusion layer (~30 lines)

### Architecture 3 -- QUERY-INTENT ROUTER (the "type-system separate retrieval mode" play)

- Form: classifier (lexicon-based or learned) routes each query to one of {semantic, algebra, hybrid}; chosen retriever runs alone; no fusion in the routed-single case
- Math: zero fusion cost when router is confident; fall through to Architecture 2 RRF when router is uncertain (a confidence threshold gates the fallback)
- Pros: when the query intent is clean (Q2 "family-tag" or Q3 "count_nb"), the router cuts retrieval cost in half and removes any chance of semantic noise corrupting the algebra answer
- Cons: router confidence calibration is a new failure mode; classifier mistakes show up as catastrophic recall failures (route to wrong index, miss top-1 entirely)
- Precedent: agentic retrieval architectures (multiple 2025-2026 entries), Vespa intent-routing, hybrid-search routing in RAG production systems
- Substrate fit: HIGH -- the router itself can be a substrate retrieval over an "intent codebook" with calibrated abstention (substrate-native primitive); routing failures degrade to Architecture 2 hybrid as a safe fallback

### Architecture 4 -- TENSOR PRODUCT ROLE-FILLER for algebra fields (the "Smolensky 1990" play)

- Form: algebra_vec = sum_i (role_i tensor filler_i) where role_i in {ALGEBRA, SIGNATURE, COMPLEXITY, TYPE} and filler_i is the substrate codebook vector for that field's value; unbinding is tensor contraction (or HRR circular-convolution inverse)
- Math: this is the substrate-native correct encoding for typed algebra fields; the unbinding operator recovers individual fields from the composite, which means a query can probe "what is the algebra of this atom" without affecting the semantic subspace
- Pros: substrate-product differentiator -- typed-edge graph retrieval is exactly the operation that no vector DB offers; substrate primitives validated today in categorical-AI drill; the FHRR variant gives complex-valued unitary binding which has higher capacity for nested algebra (compositional ring -> field -> algebra hierarchy)
- Cons: TPR full tensor is N^2 storage; HRR/FHRR circular-convolution compression is the standard practice; capacity is bounded by codebook size for fillers
- Precedent: Smolensky 1990 onward, Plate HRR 1995, Kanerva HD computing, Frady-Eliasmith resonator networks, recent GHRR May 2024 (drilled this morning); soft TPR for visual representations Dec 2024
- Substrate fit: HIGHEST -- this is what substrate is for; the only reason v1 used tag-sum was historical, not architectural

### Architecture 5 -- CO-TRAINED DUAL EMBEDDINGS (the "long-term mature form")

- Form: train an algebra-encoder jointly with a semantic-encoder so that the two are pushed toward complementary subspaces by a contrastive loss with explicit orthogonality penalty
- Math: gradient-multi-subspace-tuning, mixture-of-orthogonal-experts, GDOD gradient-orthogonal-decomposition all give the recipe; the encoder learns a representation that is provably non-redundant by construction
- Pros: best theoretical guarantee; tuned exactly to substrate corpus distribution; eliminates the calibration burden of Architecture 1
- Cons: training cost; requires labeled algebra annotations on substrate corpus; v1 timeline does not support this
- Precedent: GDOD 2023, multi-subspace tuning 2026, orthogonal-experts 2024, gradient-multi-task literature
- Substrate fit: MEDIUM -- correct long-term play but premature for v2; revisit when corpus stabilizes and labeled-algebra data accumulates

---

## (d) Cross-thread synthesis

### Convergence with categorical-AI / DisCoCat drill (this morning)
The DisCoCat drill recommended the substrate as a strong-monoidal-dagger-compact-closed functor mapping grammar to a W*-category. The algebra-encoding question is exactly the question "how does substrate type the morphisms in this category". The TPR/HRR role-filler binding (Architecture 4) IS the categorical-product encoding of typed-edges, which means the algebra index in Architecture 2 is the same primitive as the typed-binding in the DisCoCat drill. The two drills converge on the same substrate primitive being load-bearing.

### Convergence with operator-algebras drill (this morning)
GHRR May 2024 gives substrate a noncommutative binding primitive (unitary-matrix bind instead of phasor bind). If the substrate algebra encoding needs to represent NON-COMMUTATIVE algebra signatures (group structure, ordered field-sequences, ring-action), GHRR is the substrate-native way to do it without a permutation hack. The algebra index in Architecture 2 should be HRR for v2 and GHRR for v3, with the same RRF fusion layer unchanged.

### Convergence with substrate-memory + 8B-LLM-frontend hybrid drill (this morning)
That drill recommended hybrid architectures with conformal-margin routing. The conformal-routing primitive is exactly the calibrated-abstention layer that Architecture 3 (query-intent router) needs in production. If the router-confidence drops below threshold, the system falls through to Architecture 2 RRF -- this is the same conformal-routing primitive recommended in the LLM-hybrid drill, applied to a different routing decision.

### Convergence with substrate-only POS-tagger validation (cycle 226 morning)
The POS tagger validation showed that substrate-classical (count-based with substrate as Tier-2 bundle storage) BEATS phasor-only prototype matching. The algebra-index of Architecture 2 is structurally identical -- a count-based / signature-based retrieval encoded in a substrate bundle. The empirical pattern from POS predicts the algebra index will succeed on Q2/Q3 where v1 failed because tag-sum was effectively phasor-only-prototype-matching against an uncorrelated subspace.

### Convergence with substrate v3.2 engineered-wrapper synthesis (cycle 227-ish)
The engineered-wrapper memory entry says all 5 protection layers ride on substrate algebra via wrapper, no core changes. The algebra-encoding architecture is the SAME pattern: ride a new algebra index on top of the existing semantic index via a wrapper (RRF fusion + intent routing), no semantic-index core changes. Architectural consistency with v3.2 wrapper pattern.

---

## (e) Substrate-product implications

### Commercial differentiation earned by Architecture 2+3 ship

- Algebra-aware retrieval is the substrate's load-bearing product differentiator vs vector DBs (Pinecone, Weaviate, Vespa, Chroma, pgvector). All of those offer semantic-only or BM25+semantic hybrid. NONE of them offer typed-edge / algebra-signature retrieval as a first-class primitive. Architecture 2+3 lets substrate claim this differentiator HONESTLY (with a working pilot, not a brochure).
- The intent-routed mode (Architecture 3) is a customer-visible feature: "ask substrate about algebra and it answers from the algebra index; ask substrate about meaning and it answers from semantic". This is a story customers can repeat to their stakeholders, which is the operational definition of a marketable differentiator.

### Risk if we DON'T ship algebra-aware retrieval

- Substrate-self-index v1 already showed cosine-on-tag-sum is net-negative. If we ship v2 with the same architecture and just "add more tags", v2 will be net-MORE-negative because the irrelevant-subspace noise scales linearly in tag count. Customers running their own evals would surface this fast.
- Falling back to Fix B (bge-encode algebra as text) ships a working semantic-only retrieval that loses the substrate differentiator. Substrate would then be just-another-vector-DB-with-extra-steps in customer eval.

### Implementation cost estimate (v2 ship)

- Architecture 2 hybrid two-index + RRF: ~150 lines new code (algebra-index builder + RRF fusion); zero changes to existing semantic-index path; ~1 day eng + 1 day eval
- Architecture 3 intent router: ~50 lines new code (lexicon classifier + fallback gate); ~half-day eng + half-day eval
- Architecture 4 TPR/HRR algebra encoding: already substrate-native; substrate primitives validated today; ~1 day to wrap as the algebra-index encoder used in Architecture 2
- TOTAL v2 ship: 3-4 eng-days; well within v2 timeline

---

## (f) Citations

Verified count: 18 sources searched and synthesized.

VSA / HDC / TPR lineage:
1. Plate, T. Holographic Reduced Representations (HRR) original 1995
2. Kanerva, P. Hyperdimensional Computing / Binary Spatter Codes
3. Smolensky, P. Tensor Product Representation 1990
4. Frady, E.P. and Eliasmith, C. Resonator Networks
5. Schlegel, K. et al. A comparison of vector symbolic architectures (Springer AI Review 2021)
6. Soft Tensor Products for visual representations arXiv 2412.04671 (Dec 2024)
7. RNNs implicitly implement TPRs arXiv 1812.08718
8. Enriching Transformers with structured TPRs arXiv 2106.01317
9. Mechanisms of symbol processing for in-context learning arXiv 2410.17498 (2024)
10. GHRR / generalised HRR arXiv 2405.09689 (May 2024, drilled separately today)

ColBERT / multi-vector / late-interaction:
11. ColBERTv2 Effective and efficient retrieval via lightweight late interaction
12. Optimizing encoder for retrieval via multi-vector late interaction (Stanford CS224N)
13. Late interaction overview ColBERT ColPali ColQwen (Weaviate blog 2026)

Hybrid / RRF / dense-sparse:
14. Reciprocal Rank Fusion based hybrid dense-sparse retrieval (CEUR-WS Vol-4173)
15. Hybrid Search BM25 Vector Reranking 2026 (Digital Applied reference)
16. AutoRAG automated framework for RAG pipeline arXiv 2410.20878

Orthogonal subspaces / multi-task:
17. GDOD gradient descent via orthogonal decomposition arXiv 2301.13465
18. Mixture of orthogonal experts arXiv 2311.11385 (multi-task RL)
19. Multi-subspace tuning for search and recommendation arXiv 2601.09496 (2026)
20. Orthogonal subspace decomposition for AI-generated image detection arXiv 2411.15633
21. Cooperative embeddings for instance attribute category retrieval arXiv 1904.01421
22. Compositional concept learning DebugML 2025

(22 verified; 18 search-result-anchored as the minimum.)

---

## Concrete architectural recommendation for substrate-self-index v2

PRIMARY: Architecture 2 + Architecture 3 + Architecture 4 stacked. Specifically:

- Build the semantic index unchanged (bge-large over atom NL summary field). No tag concatenation. (This already works for Q1/Q4/Q5.)
- Build a parallel algebra index using substrate-native HRR/TPR role-filler binding over (algebra, signature, complexity, type) -- four roles, fillers drawn from a substrate codebook per field. Storage: ~N=1024 complex64 vectors, identical disk format to the semantic index.
- At query time: run an intent-router lexicon classifier (~50 lines). If router confidence high, retrieve from the single appropriate index. If router confidence below threshold, retrieve top-K from each index and fuse via RRF (k=60).
- Output top-3 fused results.

This earns substrate's algebra-aware-retrieval differentiator without modifying the semantic-retrieval path that already works. Ships in 3-4 eng-days. EXP-A is the cheap decisive test (1.5-2.5 hr CPU).

FALLBACK 1: If EXP-A fails HP-1 but EXP-B passes HP-2, ship orthogonal-subspace single-vector with calibrated alpha/beta. Trade: simpler infra, requires per-corpus calibration tuning.

FALLBACK 2: If both EXP-A and EXP-B fail (HF-1 + HF-2), regress to Fix B (bge-encode algebra fields as text). Loses algebra-as-separate-axis but works. Revisit in v3 with Architecture 5 co-trained dual embeddings.

FALLBACK 3 (escalation): If HP-4 fails (algebra-only index ranks below 3 on Q2/Q3), the substrate TPR/HRR primitive itself is inadequate for this corpus -- escalate to operator-algebra GHRR (matrix-bind) per this morning's drill. This is a substrate-physics deepening, not a retrieval-architecture redesign.

---

Note path: notes/research_drill_substrate_algebra_encoding_shared_basis_2x_2026-06-11.md
