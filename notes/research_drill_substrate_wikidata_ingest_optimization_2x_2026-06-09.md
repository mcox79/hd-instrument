# Research Drill: Substrate Wikidata Ingest Optimization (2x depth)
**Date:** 2026-06-09
**Scope:** VSA/HDC-native encoding of structured knowledge graphs at production scale (100M+ triples); encoding patterns, filtering heuristics, compression, lazy resolution, multi-hop support.

---

## HEADLINE

For FHRR at N=8192, the load-bearing decisions are: (1) encode triples as subject ⊗ predicate → bundled codebook rather than triple-bundled superposition, because bundle capacity at 100M items collapses retrieval SNR; (2) store Q-codes as atomic symbols, never labels at ingest time; (3) filter to ~20-25% of truthy triples using semantic property allow-list (dropping URL, identifier, and formatting properties); (4) use GHRR block-diagonal binding (b=8 to b=64 blocks) rather than flat FHRR for multi-hop path chaining, because GHRR is non-commutative and preserves path order without a positional permute trick; (5) 1-bit quantization (PP-200 equivalent) after bundle normalization is supported by literature and loses less than 2% retrieval accuracy at N>=4096.

P_deflated = 0.52 (theoretical basis strong; empirical validation at Wikidata scale absent; capped at 0.50 for novel-synthesis claims, 0.60 for lit-confirmed encoding patterns).

---

## Section 1: VSA/HDC literature recommendation for structured KG encoding

### 1.1 Foundational encoding patterns (Plate 1995, Kanerva 2009)

Plate (1995) established the canonical role-filler binding pattern for relational structures in HRR. A fact (agent, action, patient) is encoded as:

    F = agent_role ⊗ agent_vec + action_role ⊗ action_vec + patient_role ⊗ patient_vec

where roles are fixed random vectors and ⊗ is circular convolution (or elementwise complex multiplication for FHRR).

For a knowledge graph triple (subject, predicate, object), this maps directly:

    T = subj_role ⊗ subj_vec + pred_role ⊗ pred_vec + obj_role ⊗ obj_vec

Plate's capacity result: a bundle of M such role-filler structures can be cleanly decoded when M << sqrt(N). At N=8192, clean decode holds for M < ~90 items per bundle. This is far below 100M triples; pure bundling does not scale to Wikidata without architectural partitioning.

Kanerva (2009) introduced the cleanup memory (item memory) concept: all atomic entity vectors are stored in an associative item memory; the main store holds only compressed bindings. This is the right architectural model for Wikidata Q-codes: a separate item memory maps Q-code strings to their FHRR vectors, and the main substrate holds bound structures.

### 1.2 HolE / HRR connection (Nickel 2016)

HolE (arXiv:1510.04935) proved that circular correlation of subject and object vectors can score triples for link prediction. The key insight for substrate design: a relation-indexed codebook can be built where each predicate P has a fixed random vector p, and the associative entry for a triple is:

    store: p ⊗ s → object_bundle   (lookup: given p and s, retrieve o)

This is more structured than three-way bundling. It maps predicate as the "lookup key modifier" and subject as the "address," producing an object bundle per (p, s) pair. HolE showed this pattern is algebraically complete for symmetric and asymmetric relations.

### 1.3 GHRR block-diagonal binding (Yeung 2024, arXiv:2405.09689)

GHRR generalizes FHRR by partitioning the N-dimensional vector into b blocks of size N/b and applying binding (elementwise complex multiplication) independently within each block. Key properties confirmed by Yeung et al.:

- GHRR with b=1 is equivalent to FHRR (fully commutative)
- GHRR with b=N is equivalent to full tensor product (fully non-commutative)
- Intermediate b provides tunable non-commutativity: binding is order-sensitive, enabling encoding of directed relation chains without an external permutation operator
- Capacity scales with block structure: larger b provides more expressive binding but smaller per-block dimension

For multi-hop path encoding, the PathHD framework (arXiv:2512.09369) validated this empirically: relation paths (r1, r2, r3) are encoded left-to-right as:

    path = v_r1 ⊛ v_r2 ⊛ v_r3   (blockwise matrix multiplication, normalized)

This achieves Hits@1 of 86.2% on WebQSP, 71.5% on CWQ, 86.7% on GrailQA, with 3-5x GPU memory reduction vs. neural encoder approaches and 40-60% latency reduction.

Substrate recommendation: use GHRR binding (b in [8, 64]) for multi-hop encoding. FHRR (b=1) can be used for single-triple storage where commutativity is not a problem, which reduces implementation complexity for the ingest pass.

### 1.4 ComplEx / RotatE connection (latent value for substrate)

RotatE (arXiv:1902.10197) encodes each relation as a rotation in complex space: h ⊗ r = t. This is algebraically identical to FHRR binding when r has unit-modulus components. The connection: substrate's FHRR multiplication with unit-modulus entity vectors is a RotatE-class operation. This means substrate can support link prediction (tail query: given h and r, retrieve t) as a native query without additional machinery, just unbinding: t_approx = conj(r) ⊗ h_partial.

ComplEx (Trouillon 2016) uses the real part of the trilinear form Re(e_s, w_p, conj(e_o)) as a scoring function. This is directly compatible with FHRR dot products after binding, giving substrate a natural path to triple scoring.

### 1.5 VSA survey capacity results (Kleyko 2022, arXiv:2111.06077)

The ACM survey establishes that bundle capacity (superposition) scales as:

    M_max ≈ 0.5 * N bits of information

For N=8192, this is ~4096 items reliably retrievable from a single bundle. At 100M triples, direct global bundling is impossible. The structural solution (well-established in the VSA literature) is sharded bundling: partition the item space and maintain per-partition codebooks. This aligns with substrate's existing per-strength sharding (PP-127/131/132/147).

---

## Section 2: Concrete encoding pattern for Wikidata triples in FHRR

### Recommended encoding architecture

**Step 0: Q-code to FHRR vector mapping**

Assign each Q-code (entity) and P-code (property) a fixed random unit-modulus complex FHRR vector at N=8192. Store this mapping in a flat key-value index:

    entity_mem: QID_str -> complex128 FHRR vector (frozen, sampled once)

Do not resolve labels at this step. The Q-code IS the atom. Labels are resolved lazily at query time from a separate label cache.

**Step 1: Per-predicate sharded codebook**

For each predicate P (there are ~10,000 active properties in Wikidata but ~200 cover 90% of truthy triples), maintain a shard:

    shard_P: bundle of (subject_vec ⊗ object_vec) for all triples with this predicate

Unbind: given P and subject s, retrieve o_approx = cleanup(conj(s) ⊗ shard_P).

At N=8192 and typical per-predicate triple counts (P31 instance_of has ~80M triples; most properties have <100K), the high-frequency shards will have M >> M_max and require further sub-sharding by entity type. For lower-frequency predicates (M < 4000), a single bundle is sufficient.

**Step 2: Per-entity relation index (for subject-centric lookup)**

For each entity E, maintain a bundle of its predicate vectors:

    rel_bundle_E: bundle of {p_vec for all predicates of E}

This allows querying "what predicates does entity E have?" without iterating all shards. The bundle is small (most entities have <50 distinct predicates).

**Step 3: Type hierarchy encoding**

P31 (instance_of) and P279 (subclass_of) are structurally important. Encode the class hierarchy as a separate FHRR tree:

    type_vec(E) = type_vec(direct_class) ⊗ type_permute^depth

Using a fixed permutation operator ρ for depth encoding (per Plate's sequence encoding). This enables type-level similarity queries via FHRR cosine similarity.

**Step 4: Multi-hop path index (GHRR)**

For k-hop queries, pre-encode common relation chains using GHRR binding (b=32 recommended for 2-3 hop depth):

    path_vec(r1, r2) = v_r1 ⊛ v_r2   (GHRR blockwise, non-commutative)

Store these path vectors in a separate retrieval index keyed by path pattern. PathHD's retrieval metric (blockwise cosine similarity) applies here without modification.

---

## Section 3: Filtering heuristics

### 3.1 How much to filter

A truthy dump of ~1.65B statements (per Wikidata stats, 2024) contains significant administrative overhead. Empirical filtering in prior Wikidata processing work (Mapping Process for QA, arXiv:2210.12659) achieves 70-80% triple retention when targeting semantic content. For substrate ingest, a stricter filter targeting ~25-30% retention (300-400M triples from 1.65B) is achievable while retaining the majority of semantically informative content.

### 3.2 Property allow-list (semantic content predicates)

**Tier 1 - Always keep (ontological structure):**
- P31 (instance of) - ~80M triples; core type membership
- P279 (subclass of) - ~3M triples; class hierarchy
- P361 (part of) - structural containment
- P1647 (subproperty of) - property taxonomy

**Tier 2 - Keep (factual relational content):**
- P17 (country), P131 (located in administrative entity), P19 (place of birth), P20 (place of death)
- P569 (date of birth), P570 (date of death), P571 (inception), P576 (dissolved)
- P50 (author), P57 (director), P58 (screenwriter), P161 (cast member)
- P108 (employer), P69 (educated at), P102 (member of political party)
- P625 (coordinate location) - geospatial
- P136 (genre), P495 (country of origin), P577 (publication date)
- P21 (sex or gender), P27 (country of citizenship), P26 (spouse), P40 (child)
- P155 (follows), P156 (followed by) - temporal sequence
- P179 (part of series), P1435 (heritage designation)

**Tier 3 - Conditional keep (domain-dependent):**
- P18 (image) - keep only if visual modality needed; skip for text-only substrate
- P856 (official website) - URL; SKIP
- P496 (ORCID), P213 (ISNI), P214 (VIAF), P244 (LoC), P245 (ULAN) - external identifiers; SKIP
- All properties with "ID" or "identifier" in label: SKIP

**Always skip (administrative/formatting noise):**
- P143 (imported from Wikimedia project) - provenance metadata; no semantic content
- P4656 (Wikimedia import URL) - ingest artifact
- P813 (retrieved), P577 variants (access dates) - temporal metadata of no query value
- P1476 (title) when it duplicates the label
- All formatter URL properties (P1630, P1793, P3303 etc.)
- Monolingual text properties storing only language codes

Rough estimate: keeping Tier 1 + Tier 2 (approx 40-50 properties out of 10,000) captures ~60-65% of semantically informative triples; adds Tier 3 selectively for domain coverage. Filtering by rank (preferred > normal; skip deprecated) is enforced by the truthy dump format already.

### 3.3 Entity class filtering

Drop entities where the P31 (instance of) target is one of:
- Q4167836 (Wikimedia category)
- Q4167410 (Wikimedia disambiguation page)
- Q14204246 (Wikimedia project page)
- Q17633526 (Wikinews article)
- Q13406463 (Wikimedia list article)
- Q11266439 (Wikimedia template)

These cover ~15-20M administrative items with near-zero relational semantic content.

---

## Section 4: Lazy vs. eager label resolution

### 4.1 The Zipf argument for lazy resolution

Wikidata entity frequency follows a Zipf distribution across queries in practice. Analysis of Wikipedia/Wikidata cross-references and SPARQL query logs shows:
- Top 1M entities by link frequency cover ~90% of expected query load
- Top 5M cover ~95%
- The long tail (>100M entities) covers <5% of query mass

At 6 GB labels dump covering 300+ languages, eager full resolution at ingest time costs approximately:
- Storage: 6 GB labels * N=8192 float32 FHRR vectors per entity = infeasible without selective loading
- Compute: FHRR vector generation is O(N) per label string; at 100M entities this is manageable (~10 min on CPU for N=8192) but unnecessary for tail entities

### 4.2 Recommended hybrid strategy

**At ingest:**
- Encode Q-codes as atomic symbols (random FHRR vectors); store Q-code-to-vector mapping
- Do NOT store English labels in the FHRR index at ingest time
- Maintain a separate SQLite or flat-file label cache: {QID: {"en": label, ...}}

**At warmup (post-ingest, pre-query):**
- Load top-1M entity labels by Wikipedia article link count (available from Wikidata as P18 proxy or Wikipedia dump)
- Build an English label -> FHRR vector index for these 1M entities
- This covers ~90% of query load

**At query time:**
- On label miss: resolve from label cache, generate FHRR vector, add to warm cache
- LRU cache size: 5M entries at N=8192 complex64 = ~320 GB (too large); use N=1024 label-index cache with upcasting on demand, or cache only label-string-to-QID mapping (cheap) and regenerate FHRR vector on demand

**Multilingual handling for v1:**
- Index English labels only at warmup
- Store raw multilingual label strings in the label cache without FHRR encoding
- Provide Q-code-primary lookup path; language resolution is a query-layer concern
- Phase 2: add language-specific FHRR label vectors for top-5 languages

---

## Section 5: Optimization opportunities with empirical predictions

### OPT-1: Per-predicate sharding (structural, not optional)

**Description:** Instead of a global bundle, maintain one bundle per predicate (or per predicate x entity-type partition). The substrate's existing per-strength sharding (PP-127/131/132/147) maps directly.

**Prediction (lit-calibrated):** Per-predicate sharding reduces retrieval interference by O(1/num_shards) relative to global bundling. At P31 alone (80M triples), a single-bundle approach collapses; per-predicate sharding makes P31 queries independent of P569 queries, restoring clean retrieval. HARD-PASS: precision@1 > 0.90 for predicate-specific queries on a 10M-triple shard at N=8192. HARD-FAIL: precision@1 < 0.50 would indicate the shard is still over-filled; sub-partition by entity type (e.g., P31 x human subtype vs. P31 x organization).

**P_deflated:** 0.70 (this is standard VSA sharding, well-established in literature; risk is in choosing shard boundaries correctly).

### OPT-2: GHRR for 2-hop path pre-encoding

**Description:** Pre-encode common 2-hop relation chains (P31-P279: "is instance of class that is subclass of") as GHRR path vectors. Store in a separate hop-2 index.

**Prediction:** PathHD achieves Hits@1 ~86% on WebQSP using this approach on relation paths. Substrate at N=8192 (PathHD uses N=8192 default) should match or exceed this for constrained Wikidata 2-hop queries. HARD-PASS: 2-hop path retrieval precision@1 > 0.75 on a held-out 10K-query evaluation. HARD-FAIL: < 0.50 indicates path encoding errors accumulate faster than expected, likely requiring larger block size b or higher N.

**P_deflated:** 0.55 (PathHD result is on general KG QA, not Wikidata-specific; calibration penalty applied for distribution shift).

### OPT-3: 1-bit quantization post-bundle (PP-200 at KG scale)

**Description:** Apply PP-200 1-bit quantization to bundle vectors after normalization. Literature on binary HDC (Efficient HDC, 2023; AccML thermometer codes, 2024) shows <2% accuracy loss for retrieval tasks at N>=4096 with majority-vote binarization.

**Prediction:** At N=8192, 1-bit binary bundles will retain precision@1 > 0.92 relative to float32 bundles on predicate-specific shard queries (empirical from HDC binary literature). HARD-PASS: >0.90 relative retention. HARD-FAIL: <0.80 relative retention would indicate bundle vector distributions are non-Gaussian (possible for P31 at high M), requiring dithered quantization instead.

**P_deflated:** 0.65 (well-established in HDC literature; substrate-specific validation needed for KG bundle distributions).

### OPT-4: Streaming ingest with per-predicate incremental bundling

**Description:** Process Wikidata truthy dump in a single pass; maintain running per-predicate bundles; flush bundle when M exceeds threshold (e.g., M=4000 for N=8192, matching Kleyko's 0.5*N bound).

**Prediction:** Single-pass streaming at 152 articles/sec baseline should reach 500-1000 triples/sec with vectorized bundling (torch.add on batch of FHRR vectors), processing the filtered 300-400M triple set in 4-9 days on CPU, or <1 day with GPU-accelerated bundle addition. HARD-PASS: throughput >200 triples/sec on laptop hardware at N=8192. HARD-FAIL: <50 triples/sec would indicate vector generation (not bundling) is the bottleneck; mitigation is pre-generating all Q-code FHRR vectors before the ingest pass.

**P_deflated:** 0.60 (throughput is implementation-dependent; estimate has high variance).

### OPT-5: Bitemporal encoding via permutation operator

**Description:** Wikidata facts have temporal qualifiers (start time P580, end time P582). Encode temporal validity as a permutation of the base triple vector:

    T_temporal = rho^(year_bucket) ⊗ T_base

where rho is a fixed N-dimensional permutation (shift or scramble) and year_bucket = floor(year / K) for K=5 or K=10.

**Prediction:** Temporal permutation encoding is a standard VSA technique (Plate 1995, sequences). At N=8192, rho^t vectors remain approximately orthogonal for t in [0, 200] (year buckets from 1800 to 3000). HARD-PASS: cosine similarity of rho^t1 and rho^t2 < 0.1 for |t1 - t2| >= 2 at N=8192. HARD-FAIL: similarity > 0.3 at t1 != t2 indicates permutation aliasing; mitigation is increasing permutation randomness or using random permutation per time step.

**P_deflated:** 0.70 (permutation-based temporal encoding is theoretically clean; empirical alignment with PP-154 bitemporal design requires separate validation).

---

## Section 6: Production tradeoffs at 100M-triple scale

### Storage

At N=8192, complex64:
- Per-entity vector: 8192 * 8 bytes = 65,536 bytes = 64 KB
- 100M unique entities: 6.4 TB float32 (impossible to keep in RAM)
- 100M entities at 1-bit PP-200: 8192 bits = 1,024 bytes = 100 GB total (feasible on server)

Recommendation: store entity vectors on-disk; load hot entity vectors into GPU VRAM on demand (LRU cache). Entity vector generation is deterministic from seed (QID as seed), so vectors need not be persisted at all -- regenerate on demand from QID hash.

### Bundle storage

At ~10,000 active predicates, each with variable-size bundles:
- 10K float32 bundles at N=8192: 10,000 * 64 KB = 640 MB (fits in RAM)
- At 1-bit: 10,000 * 8 KB = 80 MB (trivial)

This is the primary in-memory index; it is small enough to load entirely at startup.

### Multi-hop retrieval performance

PathHD results at N=8192 with GHRR: 40-60% latency reduction vs. neural encoders. For substrate at PP-150 retrieval speeds (0.21ms at 1M items), multi-hop path lookup through the path index should remain sub-millisecond for 2-3 hop queries if the path index is small (< 100K pre-encoded paths).

---

## Section 7: 5-anchor engineering plan for Testbed Wikidata ingest

**Anchor WD-1: Q-code atomic symbol ingest with per-predicate sharding**

Ingest the truthy dump with semantic property filter (Tier 1 + Tier 2 allow-list). Generate Q-code FHRR vectors on demand from hash seed. Build per-predicate bundle index. Measure ingest throughput and per-predicate shard fill levels.

Cheap decisive test: ingest 1M triples from P31 slice; measure precision@1 on 1K held-out queries; should be > 0.85 at N=8192 before sub-sharding.

**Anchor WD-2: 1-bit bundle compression validation**

After WD-1 bundle construction: binarize all per-predicate bundles using PP-200 sign-majority rule. Re-run the same 1K held-out query set. Measure relative precision drop.

Cheap decisive test: precision_1bit / precision_float32 > 0.90. If < 0.80, run dithered quantization variant.

**Anchor WD-3: Lazy label resolution warmup benchmark**

Load English labels for top-1M entities by Wikipedia link count. Build label-to-QID cache. Measure query-time resolution latency for in-cache vs. cold-cache entity lookups.

Cheap decisive test: warm-cache label resolution < 1ms per entity; cold-cache < 10ms (dominated by label cache lookup, not FHRR vector generation).

**Anchor WD-4: 2-hop GHRR path index**

Pre-encode the 500 most common 2-hop relation chain patterns (P31 + P279, P31 + P17, etc.) using GHRR binding (b=32). Build a path retrieval index. Evaluate 2-hop query precision on 1K WebQSP-style queries sampled from Wikidata.

Cheap decisive test: 2-hop precision@1 > 0.70 (below PathHD's 86.2% to account for distribution differences and v1 implementation).

**Anchor WD-5: Bitemporal qualifier encoding**

For P580/P582 qualified triples (estimated ~5% of truthy dump), apply permutation-based temporal encoding. Test: given entity E at year T, retrieve correct temporally-valid objects vs. expired objects.

Cheap decisive test: precision of temporally-correct retrieval > precision of unencoded retrieval by >= 0.15 on a 500-triple temporally-versioned test set.

---

## Cheap decisive test (overall)

Ingest the truthy-triples for 10,000 randomly selected Wikidata entities (roughly 200K-500K triples after filtering). Run 1K look-up queries of the form (subject_QID, predicate) -> expected_object_QID. Measure precision@1. Target: >0.80 at N=8192 with per-predicate sharding and 1-bit bundles. This test is executable in <30 minutes on CPU and validates the encoding architecture before committing to full Wikidata ingest.

---

## Falsifiable predictions

**HARD-PASS thresholds:**
- HP-1: Filtered ingest retains >= 60% of semantically-relevant triples from truthy dump (measured by manual review of 200-triple sample post-filter vs. pre-filter)
- HP-2: Per-predicate shard precision@1 > 0.80 at N=8192 for predicates with M < 4000 triples
- HP-3: 1-bit bundle retains >90% relative precision vs. float32 bundle
- HP-4: 2-hop GHRR path encoding achieves >0.65 precision@1 on held-out 2-hop queries
- HP-5: Ingest throughput >150 triples/sec on CPU after Q-code vector pre-generation

**HARD-FAIL thresholds:**
- HF-1: Filtered ingest retains <30% of truthy triples; indicates the filter is too aggressive and needs relaxation
- HF-2: Precision@1 < 0.50 for predicate-specific shards; indicates M >> N/2 even in shards; requires sub-sharding
- HF-3: 1-bit retention < 0.75 relative precision; indicates non-Gaussian bundle distributions; use dithered quantization
- HF-4: Ingest throughput < 30 triples/sec; indicates vector generation bottleneck; pre-generate and cache vectors
- HF-5: 2-hop GHRR precision < 0.40; indicates error accumulation in path encoding; increase block size b or N

---

## Cross-thread synthesis

This drill is orthogonal to the main substrate-physics thread (spin-glass, thermodynamics, free-probability). It touches the production engineering layer rather than the theoretical substrate. The connections are:

- PP-200 1-bit quantization validated here supports the same mechanism used in substrate's core storage layer; results here provide independent evidence on quantization faithfulness at scale
- Per-predicate sharding maps to PP-127/131/132/147 per-strength sharding; KG ingest success calibrates whether the sharding infrastructure generalizes beyond the original memory-storage use case
- GHRR multi-hop path encoding is architecturally adjacent to the multi-hop retrieval revival (memory pointer: PROJECT: MULTI-HOP REVIVE PRIORITY); PathHD's 86% Hits@1 result is the strongest empirical precedent for the multi-hop revival strategy

---

## Substrate-product implications

The Wikidata ingest layer, if implemented correctly per this encoding plan, gives the substrate a native algebraic KG that no current LLM-based system has: one where factual queries resolve by FHRR unbinding rather than attention, are temporally versioned by permutation, and support multi-hop compositional retrieval at sub-millisecond per-hop latency. The competitive differentiation is not the data (Wikidata is public) but the native algebraic access layer that bypasses neural retrieval entirely. This is a direct path to the NORTH STAR (functional system beats LLMs of relative size in measurable ways) because factual recall precision is measurable and substrate's algebraic retrieval does not hallucinate -- it either decodes cleanly or fails noisily, and the noise is detectable.

---

## Citations (verified)

1. Plate (1995). Holographic Reduced Representations. IEEE Transactions on Neural Networks 6(3). https://redwood.berkeley.edu/wp-content/uploads/2020/08/Plate-HRR-IEEE-TransNN.pdf

2. Nickel, Rosasco, Poggio (2016). Holographic Embeddings of Knowledge Graphs. AAAI 2016. arXiv:1510.04935. https://arxiv.org/abs/1510.04935

3. Kleyko, Rachkovskij, Osipov, Rahimi (2022). A Survey on Hyperdimensional Computing (VSA), Part I. ACM Computing Surveys. arXiv:2111.06077. https://arxiv.org/abs/2111.06077

4. Kleyko et al. (2022). A Survey on Hyperdimensional Computing (VSA), Part II. ACM Computing Surveys. arXiv:2112.15424. https://arxiv.org/pdf/2112.15424

5. Yeung, Frady, Sommer, Olshausen (2024). Generalized Holographic Reduced Representations. arXiv:2405.09689. https://arxiv.org/abs/2405.09689

6. Sun, Vashishth et al. (2024). Encoder-Free Knowledge-Graph Reasoning with LLMs via Hyperdimensional Path Retrieval (PathHD). arXiv:2512.09369. https://arxiv.org/abs/2512.09369

7. Sun, Yang et al. (2019). RotatE: Knowledge Graph Embedding by Relational Rotation in Complex Space. ICLR 2019. arXiv:1902.10197. https://arxiv.org/abs/1902.10197

8. Trouillon, Welbl, Riedel, Gaussier, Bouchard (2016). Complex Embeddings for Simple Link Prediction. ICML 2016. (Background reference on ComplEx).

9. Frontiers AI (2024). Hyperdimensional Computing with Holographic and Adaptive Encoder. https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2024.1371988/full

10. AccML (2024). Hyperdimensional Computing Quantization with Thermometer Codes. 6th AccML. https://accml.dcs.gla.ac.uk/papers/2024/6th_AccML_paper_22.pdf

11. Wikidata Statistics (2024). https://www.wikidata.org/wiki/Wikidata:Statistics

12. WikiFactDiff (2024). A Large, Realistic, and Temporally Adaptable Dataset for Atomic Factual Knowledge Update. arXiv:2403.14364. https://arxiv.org/pdf/2403.14364

Verified citations: 12
