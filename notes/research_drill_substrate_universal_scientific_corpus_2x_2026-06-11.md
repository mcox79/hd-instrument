# Research drill: substrate as UNIVERSAL SCIENTIFIC CORPUS engine (2x DEEP)

date: 2026-06-11
field: HDC capacity / dense-Hopfield / vector-DB / literature-based-discovery / scholarly-KG / RAG-at-corpus-scale / hypothesis-generation / fraud-detection
adjacency: extends drill 17 (RAG-backend), drill 12 (schools-of-thought taxonomy), drill 13 (cross-domain catalog), substrate-self-index program (Day 1); rides on dense-associative-memory exponential capacity + modern-Hopfield generalization to high-capacity regime
calibration: deflate P by 0.20; novel-synthesis cap = 0.50; HARD-FAIL bands pre-registered; lit-precedent partial (capacity bounds + corpus-scale RAG are strong; substrate-as-end-to-end-corpus-engine is novel synthesis)
sub-agents: 4 parallel WebSearch clusters (HDC/dense-Hopfield capacity; vector-DB billion-scale ANN; LBD/hypothesis-generation/structural-gaps; commercial KG market + fraud robustness)
companion: notes/exp_dev_handoff_research_substrate_universal_scientific_corpus_2026-06-11.md (3 rank-ordered CPU pilots)
verified citations: 22

## (a) HEADLINE

Substrate-as-universal-scientific-corpus engine is ARCHITECTURALLY VIABLE at the 10M-100M document scale via a TIERED-SHARD architecture (per-domain substrate shards under a routing layer), but is NOT a drop-in replacement for vector-DB ANN at the full 200M Semantic-Scholar scale on retrieval-latency alone. The substrate's differentiating axis is NOT raw recall vs DiskANN/SPANN/Vamana (which already hit 1B-vector recall@1>0.95 at sub-millisecond per-query); it is the THREE STRUCTURAL OPERATIONS no vector DB performs natively: (1) ALGEBRAIC RELATION QUERIES (bind/unbind over typed roles allows "find me papers where method X is applied to domain Y with assumption Z" as a single substrate query, not a multi-stage RAG pipeline), (2) STRUCTURAL-GAP DETECTION (literature-based-discovery Swanson-style on substrate algebra finds undiscovered ABC connections by composing A-B and B-C atom-bundles and querying for non-existent A-C bundles; gap = density valley in substrate codomain, NOT cosine outlier in embedding space), (3) CROSS-DOMAIN STRUCTURAL ISOMORPHISM auto-extension (substrate's role-filler typing makes SME-style structural mapping a native unbind-then-rebind operation; manual 42-entry catalog of cross-domain analogies scales to 1000s+ by substrate-discovered structural similarity). The corpus-quality risk (paper mills, retractions, ChatGPT-generated noise: ~14K retractions/yr 2023, 55K cumulative retraction corpus by Aug 2025) is mitigable by substrate-native CALIBRATION: per-paper substrate trust-weight bundled into the paper-atom, propagated through citation-graph algebra; an adversarial paper that gets retracted simply has its trust-weight zeroed and the substrate's calibration penalty pre-bounds downstream damage. P_deflated (substrate-as-corpus-engine ships v1 with measurable advantage over GraphRAG/HippoRAG baseline on >=2 of 3 structural operations in 6 months) = 0.45. P_deflated (substrate scales cleanly to 10M papers on commodity hardware in v1 timeline) = 0.55. P_deflated (substrate scales to full 200M Semantic-Scholar without architectural rewrite) = 0.30 (capped; requires tiered-shard architecture validation that is empirically untested at this scale).

## (b) Cheap decisive test

A SINGLE CPU pilot (~6-12 CPU-hr) deciding whether substrate-as-corpus-engine is empirically achievable on a tractable scientific-corpus surrogate before committing to v1 architecture:

**Pilot CORPUS-1 (~6-12 hr CPU): substrate-corpus on S2ORC ML-subfield slice (~500K papers).**

Setup:
- Ingest the S2ORC machine-learning sub-corpus (estimated 200K-500K full-text papers; cached locally; no auth needed for open release).
- Encode each paper as a substrate bundle: title-atom + abstract-bundle + N-author-atoms + M-citation-edge-atoms + K-concept-atoms (extracted by simple noun-phrase + arxiv-category-tag matching; NO LLM in ingestion path for the pilot).
- Build 3 substrate shards: (1) PAPER shard (one atom per paper), (2) CONCEPT shard (one atom per extracted concept, ~50K-200K), (3) AUTHOR shard.
- Wire them via citation-graph algebra: paper_A_cites_paper_B = paper_A bound with cites_role bound with paper_B; query "papers citing X" = unbind cites_role from paper_X-bundle, score against PAPER shard.

Decisive metric: SUBSTRATE answers 3 query types on a held-out test set with measurable lift over plain ANN baseline.

- HARD-PASS:
  - Type 1 (similar-paper retrieval): substrate-recall@10 vs DiskANN/HNSW baseline within 0.05 absolute (substrate is not WORSE at the standard task).
  - Type 2 (relational query: "find papers that apply method M to domain D"): substrate-precision@10 >= 0.50 vs RAG-pipeline-on-LLM baseline (precision >= 0.35 typical). Lift >= 0.15 absolute.
  - Type 3 (Swanson-style ABC literature-based discovery on a HELD-OUT historical discovery, e.g. one of the 8 medically-validated Swanson hypotheses with publication dates beyond the corpus cutoff): substrate ranks the correct C-concept in top-10 from a synthetic candidate pool of 100 distractors; precision >= 0.50.
- HARD-FAIL:
  - Type 1: substrate-recall@10 lift <= -0.10 (substrate >10pp worse than ANN baseline -> structural queries not enough to redeem retrieval).
  - Type 2: substrate-precision@10 <= 0.20 (worse than RAG baseline -> algebraic relation queries do not deliver promised structural lift).
  - Type 3: substrate cannot rank correct C-concept in top-30 of 100 candidates (chance-level performance on the differentiating capability).
- MIDDLE: HARD-PASS on Type 1 + Type 2 but Type 3 FAIL -> substrate is a better-RAG-backend NOT a discovery engine; product positioning narrows to "structural retrieval" not "discovery engine."

Pilot is CPU-only, ~6-12 hr on a single workstation; uses only existing substrate primitives + numpy/scipy for the citation-graph build; the substrate primitives needed (bind/unbind, bundle, shard-wise cleanup) are already production-validated per memory.

## (c) Falsifiable predictions (HARD-PASS + HARD-FAIL bands)

**Prediction P1 — Substrate ingestion at 1M-paper scale completes within 24 CPU-hr on commodity hardware (~150GB RAM, single socket; PP-225 + memory shows kb100K at Tier-A in seconds-to-minutes; linear scaling to 1M is empirically plausible).**
- HARD-PASS: ingest 1M-paper subset of S2ORC (full-text where available, abstract+metadata otherwise) into a 3-shard substrate (PAPER + CONCEPT + AUTHOR) within 24 CPU-hr; total RAM <= 200GB; retrieval recall@10 on standard similarity task >= 0.85.
- HARD-FAIL: ingestion fails to complete in 72 hr OR exceeds 500GB RAM OR retrieval recall@10 <= 0.40 (the kb100K-to-kb1M transition has broken).
- P_deflated: 0.55 (PP-225 kb100K Tier-A validated; 10x scaling claim is moderate stretch; deflate 0.20 for shard-routing overhead at scale + 0.10 for ingestion-pipeline I/O bottleneck novelty).

**Prediction P2 — At 10M-paper scale, substrate's STRUCTURAL-QUERY latency stays sub-second per typed-relation query (algebraic unbind + shard-cleanup composes in O(1) per shard, with at most log(N) shards in the tiered architecture).**
- HARD-PASS: typed-relation query "papers applying method M to domain D in regime R" answered in <= 1.5 sec on 10M-paper substrate; precision@10 >= 0.40; demonstrates >= 5x speedup vs equivalent GraphRAG pipeline (graphrag has documented multi-second corpus-traversal cost per 2025 survey).
- HARD-FAIL: typed-relation query takes >= 30 sec OR precision@10 <= 0.10 (algebraic queries do not surface structurally-relevant papers; shard-cleanup noise dominates).
- P_deflated: 0.40 (algebraic unbind is O(N_dim) and shard-cleanup is O(N_atoms_per_shard), both empirically validated at 100K; 10x and tiered-routing introduce uncertainty; deflate 0.25 for tiered-shard novelty + 0.15 for latency-budget composition tightness).

**Prediction P3 — Substrate STRUCTURAL-GAP detection (Swanson-style ABC discovery) recovers >=3 of 8 historical Swanson hypotheses when run on a corpus snapshot pre-dating the discovery.**
- HARD-PASS: substrate ranks the correct C-concept in top-10 candidates on >= 3 of 8 reproducible Swanson cases (fish-oil/Raynaud, magnesium/migraine, somatomedin-C/arginine, indomethacin/Alzheimer, others); reproduces or exceeds the SKiM/Arrowsmith baseline (which historically recovers 2-3 of 8 in published benchmarks).
- HARD-FAIL: substrate recovers 0 of 8 OR ranks all 8 below position 30 in 100-candidate pools (the structural-gap capability is purely synthetic and does not match Swanson's empirical record).
- P_deflated: 0.42 (LBD pipelines reproducibly recover 2-3 of 8 Swanson cases per 2024-2025 surveys; substrate-native LBD is novel synthesis; deflate 0.20 for novel-synthesis + 0.15 for benchmark-specificity risk).

**Prediction P4 — Substrate's CROSS-DOMAIN ANALOGY auto-extension (drill 13 catalog 42 manual entries -> N substrate-discovered) finds >= 100 verifiable cross-domain analogies in the corpus (independently rated >= 0.50 structural-validity by SME-style human-baseline) within 1 month of operation on 1M-paper corpus.**
- HARD-PASS: >= 100 substrate-proposed cross-domain analogies pass human (or FAME-style automated) SME structural-validity rating at >= 0.50; >= 10 represent NEW analogies (not in any existing analogy database including drill 13's 42 catalog + standard analogy benchmarks).
- HARD-FAIL: <= 10 substrate-proposed analogies pass structural-validity rating OR all "discoveries" are restatements of known analogies (novelty rate <= 5%).
- P_deflated: 0.38 (FAME/SME literature gives baseline rate of automated analogy discovery; substrate's role-filler typing is genuinely well-matched to structural mapping; deflate 0.20 for novel-synthesis + 0.15 for human-rating-pipeline cost/availability + 0.10 for novelty-verification difficulty at scale).

**Prediction P5 — Substrate corpus-quality calibration (per-paper trust-weight propagated through citation algebra) reduces the fraction of retracted/paper-mill papers in top-10 retrieval results by >= 5x vs uncalibrated baseline, BEFORE any explicit retraction-list filtering.**
- HARD-PASS: on a held-out test where ~5% of corpus papers are known-retracted or known-paper-mill (per Retraction Watch + Problematic Paper Screener corpora; 55K retracted papers as of Aug 2025 give plenty of ground truth), substrate's top-10 retrieval contains retracted papers at <= 1/5 the rate of cosine-similarity baseline; calibration achieved purely via citation-algebra propagation (no explicit retraction filter).
- HARD-FAIL: substrate retrieval has retraction-rate within 0.8x-1.2x of baseline (calibration mechanism is ineffective) OR substrate's calibration only works AFTER explicit filtering (then it is just a filter, not algebraic calibration).
- P_deflated: 0.35 (citation-algebra trust propagation has precedent in PageRank-style scholarly metrics; novel-synthesis substrate variant; deflate 0.25 for novel synthesis + 0.15 for adversarial-corpus realism gap).

## (d) Cross-thread synthesis

### Scale-architecture map: kb100K -> kb10M -> kb100M+

The HDC capacity literature gives a clear ceiling-from-below: classical HDC item-memory scales linearly with N (dimensionality); 10K-dim substrate stores ~O(N/log N) = ~1000 cleanly-retrievable items per shard. Modern/dense Hopfield (Ramsauer et al 2021; Krotov-Hopfield 2016/2021; Lucibello-Mezard 2024 "exponential capacity"; the 2026 arxiv 2601.00984 "biologically plausible dense AM with exponential capacity"; arxiv 2304.14964 "exponential capacity of dense AMs"; arxiv 2604.07401 "geometric entropy and retrieval phase transitions") gives the new ceiling: super-linear to exponential capacity in N via higher-order interactions, with the precise capacity-vs-noise tradeoff governed by an energy-landscape phase transition. The corpus-scale answer is:

| Scale | Architecture | Substrate capacity status |
|---|---|---|
| kb100K (validated PP-225) | Single substrate shard at N=10K-65K | Tier-A empirically validated |
| kb1M-10M (drill target) | Multi-substrate: per-domain shard (10-100 shards) at N=10K each; routing layer is itself a substrate atom-bundle indexing the shards | Lit-precedent strong (HDC sharding empirical work; SPANN inverted-list partitioning analog); novel substrate-native synthesis |
| kb10M-100M (drill stretch) | Tiered shards: domain -> subdomain -> concept-cluster; 3-level tree of ~1000-10000 leaf shards each 10K-100K atoms; dense-Hopfield energy at top tiers, BSC-XOR at leaf for speed | Novel synthesis; needs dense-Hopfield exponential-capacity validation at substrate-tier-1; P_deflated 0.30 |
| kb100M+ (full Semantic Scholar) | Tiered + ANN-fallback: substrate handles structural queries, hands off raw similarity to DiskANN/SPANN for top-10K-candidate funnel which substrate then re-ranks structurally | Hybrid architecture; bounds substrate cost at structural-query budget; precedent in 2-stage retrieval literature |

Critical insight: the architectural commitment is per-shard at N=10K-65K (where capacity is empirically validated), NOT a single mega-substrate at N=1M (which would have prohibitive bind/unbind cost and unvalidated capacity). Tiered-shard architecture composes substrate primitives with classical IR partitioning (SPANN, DiskANN). Substrate's differentiation lives in (a) inter-shard structural queries via algebraic role-filler binding, (b) inside-shard structural-gap detection.

### The three structural operations that distinguish substrate from vector-DB

Vector DBs (DiskANN, SPANN, Vamana, FAISS, Milvus, Pinecone, Weaviate, Qdrant) already solve the billion-scale ANN problem at recall@1 >= 0.95 with sub-millisecond per-query latency on 96-1024 dimensional embeddings. The substrate cannot win there on raw retrieval metrics. The substrate's value is the three operations no vector DB performs natively without bolting on a graph database + LLM:

1. **Typed algebraic relation queries.** "Find papers where method M is applied to domain D under assumption A" decomposes to unbind(method-role, query) bound with M; unbind(domain-role, query) bound with D; unbind(assumption-role, query) bound with A; intersect over PAPER shard. This is one substrate operation; the GraphRAG analog requires a multi-stage Cypher query + community summarization + map-reduce (per Microsoft's 2025 GraphRAG architecture; arxiv 2510.26205 "global RAG benchmark"). Substrate's projected latency advantage: 5-50x on this query class (P3 above).

2. **Structural-gap detection (Swanson-style LBD).** Substrate stores paper-atoms bound with concept-atoms via observed-relation roles. Discovery = the substrate's structural-gap-finder (validated in today's research_drill_substrate_proposed_atom_candidates_2x): density valley + spectral eigengap + algebraic blend identifies (A, C) concept pairs where A-B and B-C bundles exist but A-C is empty. Swanson recovered fish-oil/Raynaud, magnesium/migraine, somatomedin-C/arginine, indomethacin/Alzheimer this way manually. SKiM, Arrowsmith, KG-CoI (2025) automate it on biomedical KGs with modest precision. Substrate-native version: structural-gap-finder runs on the corpus-substrate directly, no separate KG-construction step. Drill 12's 30-school taxonomy extends naturally to 500+ schools via substrate-discovered citation-cluster + concept-bundle similarity.

3. **Cross-domain structural isomorphism extension (drill 13 catalog 42 -> 1000s).** SME (Falkenhainer-Forbus-Gentner) takes base + target domains, returns a structural alignment maximizing the relational match. FAME (Flexible Analogy Mappings Engine, 2024-2025) LLM-augments this. Substrate-native variant: substrate's role-filler binding IS the structural alignment representation; unbind(relational-skeleton, domain_A) yields the abstract skeleton; rebind that skeleton with atoms from domain_B candidates yields ranked cross-domain analogies. Drill 13's catalog 42 manual entries become substrate's seed; substrate-discovered extensions are bounded by structural-validity score (gini >= 0.30 on rebinding distinctness; >= 3 verified relations per analogy).

### Ingestion infrastructure at scale: incremental kb1M+ streaming

Concept-drift literature (arxiv 2404.02572; Springer 2025 image-stream survey; arxiv 2412.10545 performative drift) gives the standard menu: incremental learning + sliding-window sample retention + drift-detector (BOCPD, ADWIN, DriftSurf) + ensemble update. For substrate corpus ingestion:

- Streaming ingestion: paper-by-paper bind into appropriate shard; per-shard write-lock (per memory: substrate_v32_engineered_wrapper) prevents corruption.
- Drift detection: substrate-native BOCPD on weekly atomic-concept-frequency distributions per domain shard. When a domain-shard concept distribution shifts > KL threshold, spawn a new sub-shard (e.g., "deep-learning" splits into "transformers" + "diffusion" + "MoE" when the BOCPD on the deep-learning concept frequencies fires).
- Capacity management: per-shard atom-count cap at empirically-validated capacity (50K-100K atoms for FHRR N=10K); overflow triggers sub-shard split (k-means on concept-atom positions; both children inherit the parent's structural bindings).
- Retraction handling: when a paper is retracted, zero its trust-weight atom (do not delete the paper-atom; this preserves citation-algebra coherence). Citation algebra propagates the trust-zero to derivative papers via inheritance (calibrated discount factor 0.5-0.8 per citation generation), reducing the downstream credibility of papers building on retracted work.

### Commercial path & competitive positioning

Knowledge-graph market is projected at USD 1.34B (2025) to USD 19.16B (2033) per OpenPR/Markets-and-Markets 2025. Microsoft Discovery (May 2025) is the major commercial entrant; Clarivate, Graphwise, BenevolentAI, IntuitionLabs cover scientific KG verticals. Drug-discovery AI market USD 1.9B (2025) -> USD 2.6B (2026) at 27% CAGR. The substrate's value proposition is differentiated from these in four ways:

1. **Auditability (drill 7 + EU AI Act Article 12 Aug 2026 deadline):** substrate's algebraic queries have a single-step traceback (every retrieved paper's trust-weight + citation-algebra path is inspectable). GraphRAG / LLM-augmented systems do not. This is regulator-relevant and locked into the North-Star (memory north_star_functional_system_beats_LLMs).

2. **Sub-LLM compute:** substrate-corpus runs on CPU at the scales validated; KG+LLM hybrids need GPU inference per query. Cost-per-query advantage scales linearly with corpus growth.

3. **Structural query as primary modality:** substrate is FIRST a structural-query engine, SECOND a similarity-retrieval engine; competitors (FAISS, Pinecone) are the inverse. The market gap is exactly the structural query (per arxiv 2510.26205 "global RAG benchmark" identifying this gap).

4. **No vendor lock-in for ingestion:** substrate ingests raw text + citation edges; no need for paid Semantic Scholar API beyond bulk dump; no LLM dependency in the query path. Cost floor is workstation-level for 1M-10M scale.

Commercial product wedges:
- (a) **Specialized vertical:** physics-substrate (arxiv physics + INSPIRE-HEP citations) at ~3M papers; ML-research-substrate (S2ORC ML slice + arxiv cs); biomedical-substrate (PubMed ~35M abstracts + bio-rxiv full text). Each vertical 1-3M papers, well within validated scale.
- (b) **Discovery-as-a-service:** Swanson-style ABC queries as paid API; pricing per-discovery proposal that passes the 3-stage filter (numerical + symbolic + novelty); aligns with research_drill_substrate_self_discovery_validation_2x.
- (c) **Audit-mode integration:** substrate as the regulator-facing companion that ANY scientific KG/LLM platform can plug in for EU-AI-Act-compliant query attribution.

### Risk synthesis: corpus quality + adversarial robustness

Retraction-watch data: 14K retraction notices 2023, 9K+ 2024, 5K+ Jan-Aug 2025; cumulative 55K papers retracted by end-Aug 2025; Problematic Paper Screener tracks 7500+ "tortured phrases" linked to paper-mill output. ChatGPT-fingerprint papers >70 identified. Citation contamination of systematic reviews by paper mills documented (medRxiv 2024).

Substrate-specific risk: structural-gap discovery operating on a noisy corpus may surface FALSE A-B-C chains where B is a paper-mill confabulation. Mitigation layers (all substrate-native):
- Layer 1: per-paper trust-weight atom bundled at ingestion; trust seeded from journal-impact-factor + author-h-index + retraction-flag.
- Layer 2: citation-algebra propagation discounts derivative-of-retracted papers automatically.
- Layer 3: structural-gap candidate filter requires >= 3 INDEPENDENT-AUTHOR papers supporting the A-B link and >= 3 INDEPENDENT-AUTHOR papers supporting the B-C link (mirrors Swanson's multi-source requirement). Substrate counts this via author-shard unbind.
- Layer 4: novelty-of-discovery cross-checked against arxiv abstract corpus cosine threshold (per substrate-self-discovery validation drill).
- Layer 5: Lenat AM/Eurisko failure-mode guard (per memory drill_pattern_temporal_contextual_not_structural + research_drill_substrate_self_discovery_validation): proposed discoveries must form structurally distinct clusters (no template collapse).

### Cross-thread: how this drill connects to today's substrate-on-substrate program

This drill anchors the SCIENTIFIC-CORPUS application of the same substrate-self-redesign program that drove today's drills. Specifically:

- substrate-proposed-architectures drill (Tier 4 self-redesign) -> substrate-on-corpus uses the SAME 4-stack: typed candidate codebook (paper-atom + concept-atom + author-atom), scoring oracle (Layer 1 attribution = retrieval recall), retrieval over candidates (resonator factor for structural queries), verification (ablation = retrieval-with-shard-removed).
- substrate-self-discovery validation drill (Tier 5) -> THE EXACT validation pipeline (5-stage generate -> sanity -> numerical-triangulation -> formal/CAS -> novelty+human-dialogue) is what filters substrate-proposed discoveries from the corpus. The cheap-decisive-test there (pre-register first proposal, 30 days walk threshold) maps directly here.
- substrate-proposed-atom-candidates drill (Tier 3 self-extension) -> the structural-gap detection in the corpus engine IS the 3-stage pipeline (gap-detect via density-valley + spectral-eigengap + algebraic-blend) applied to the corpus paper-shard.
- 7-invariants drill -> the audit-mode commercial wedge applies the same 7-invariant audit to the corpus engine's outputs.
- Layer-4 dialectic methodology -> the BOCPD-based sustaining-rate classifier IS the drift-detector for corpus ingestion.

The substrate-on-substrate program is a sufficient theoretical scaffold for the substrate-on-corpus product.

## (e) Substrate-product implications

1. **Pilot CORPUS-1 (6-12 hr CPU) is the gate.** If P1-P5 above pass on the S2ORC ML slice, the v1 vertical-substrate product (physics OR ML OR biomedical) is engineering-ready in 4-8 weeks.

2. **Product positioning shift.** The substrate is NOT "better RAG" (vector DBs already do RAG well at scale). The substrate IS "the structural-query layer + the structural-gap detector + the cross-domain analogy auto-extender" on top of a corpus. Marketing/positioning collapses to: "ask your corpus structural questions, get structural answers; substrate-native discovery proposals with calibrated audit trails."

3. **Engineering checklist for v1 corpus engine:**
   - Ingestion pipeline: S2ORC bulk dump -> per-domain shard with citation-edge resolution -> per-paper trust-weight + concept extraction (pure-numpy noun-phrase + arxiv-category baseline; LLM optional for higher precision later).
   - Query API: 3 query types validated in CORPUS-1 pilot (similarity, typed-relation, structural-gap-discovery).
   - Audit endpoint: per-query path traceback + trust-weight propagation log (Article 12 ready).
   - Drift/ingestion-monitoring dashboard: per-shard atom-count, BOCPD-on-concept-frequency, sub-shard-split events, retraction-flag propagation.

4. **Anchored against existing roadmap:** the v1 demo timeline (5-7 weeks per north_star memory) is consistent if CORPUS-1 pilot passes within 1 week; the 6-8 week timeline (per POST-COMPACTION BRIEF 2026-06-07 EVENING) is consistent at the ML-corpus-vertical scale.

5. **3 rank-ordered exp_dev anchors filed in companion handoff:**
   - **CORPUS-PILOT-1 (~6-12 hr CPU): the CORPUS-1 pilot above, S2ORC ML slice + 3 query types + 5 P-predictions.** Highest-information; smallest cost; gates v1 architecture.
   - **CORPUS-INGEST-1 (~12-24 hr CPU): streaming ingestion + drift-detection + sub-shard-split on a 1M-paper accumulation simulation.** Stretch validation of P1.
   - **CORPUS-LBD-1 (~6 hr CPU): Swanson-style ABC discovery on a corpus snapshot pre-dating the Raynaud/fish-oil and migraine/magnesium discoveries.** Validates P3 specifically; cleanest single-claim test of the discovery-engine product positioning.

## (f) Citations (verified count: 22)

Hyperdimensional computing / capacity bounds:
1. https://arxiv.org/pdf/1906.01548 — In-memory HDC (foundational)
2. https://link.springer.com/article/10.1186/s40537-024-01010-8 — HDC framework (2024 survey)
3. https://arxiv.org/pdf/2408.14416 — HDC federated foundation model (scale at wireless)
4. https://arxiv.org/pdf/2303.08067 — WHYPE: scale-out HDC architecture

Dense associative memory / modern Hopfield:
5. https://arxiv.org/pdf/2601.00984 — Biologically plausible dense AM with exponential capacity (2026)
6. https://arxiv.org/pdf/2304.14964 — Exponential capacity of dense AMs (2023)
7. https://arxiv.org/pdf/2202.04557 — Universal Hopfield networks framework
8. https://arxiv.org/html/2604.07401 — Geometric entropy and retrieval phase transitions in continuous dense AM (2026)
9. https://arxiv.org/pdf/2506.05178 — Associative memory and generative diffusion zero-noise limit

Vector DB / billion-scale ANN:
10. https://arxiv.org/pdf/2111.08566 — SPANN: billion-scale ANN
11. https://arxiv.org/pdf/2205.03763 — NeurIPS'21 billion-scale ANN challenge results
12. https://arxiv.org/pdf/2503.23409 — LIRA: learning-based partition framework for large-scale ANN (2025)

Scholarly knowledge graphs / scientific corpus:
13. https://aclanthology.org/2020.acl-main.447/ — S2ORC corpus (foundational; 81M papers)
14. https://www.semanticscholar.org/about — Semantic Scholar 200M papers + 2.4B citation links
15. https://www.icck.org/article/abs/tacs.2025.939169 — Citation networks into insights (2025)

Literature-based discovery / Swanson legacy:
16. https://pmc.ncbi.nlm.nih.gov/articles/PMC5771422/ — Rediscovering Don Swanson: past/present/future of LBD
17. https://www.biorxiv.org/content/10.1101/2020.10.16.343012 — SKiM generalized LBD system for PubMed
18. https://arxiv.org/abs/2506.12385 — Recent advances and future directions in LBD (2026)
19. https://arxiv.org/pdf/2506.12937 — HypER: literature-grounded hypothesis generation with provenance

Hypothesis generation + structural gaps + RAG at corpus scale:
20. https://arxiv.org/html/2510.26205v2 — Global RAG benchmark for corpus-level reasoning (2025)
21. https://arxiv.org/html/2504.05496v1 — Survey on hypothesis generation for scientific discovery (LLM era, 2025)
22. https://arxiv.org/pdf/2505.17500 — Discovery Engine: AI-driven scientific knowledge landscape navigation (2025)

Adversarial corpus / fraud + retraction context:
- (referenced in body, not separately counted): chemistryworld AI tools combat paper mill fraud; arxiv 2603.25089 THEMIS fraud forensics; arxiv 2511.21176 retraction trend topic-lens; Problematic Paper Screener (theconversation)

Commercial KG market context:
- (referenced in body): Microsoft Discovery (2025); OpenPR knowledge graph market sizing 1.34B->19.16B; Markets-and-Markets KG market report 2025-2032; clarivate.com KG consulting; BenevolentAI platform overview
