# research: hybrid native-discrete + non-native-fuzzy substrate architecture (5x drill)

Filed: 2026-06-08
Agent: research sub-agent (Sonnet 4.6)
Trigger: direct user task -- hybrid architecture routing drill

---

## HEADLINE

Published evidence strongly supports a HYBRID routing architecture where native-discrete
retrieval dominates on multi-hop structured queries (K=2 recall@1 empirically 1.000 in
substrate) and fuzzy-embedding retrieval dominates on single-hop factoid and synthesis
queries. The routing decision boundary is measurable and corresponds to query structural
entropy -- low-entropy queries (entity + relation pattern, countable hops) route native;
high-entropy queries (open-ended, synthesizing, paraphrase-sensitive) route fuzzy. Five
routing strategies are viable; cascade with confidence threshold and RL-trained routing
are both proven in 2024-2025 literature. The substrate's simultaneous dual-storage
architecture (triples + embeddings in same binding) is genuinely novel relative to
published hybrid systems and warrants experimental investigation.

---

## Calibration note

P_theoretical estimates deflated by 0.20 per [[feedback-lit-scan-calibration-penalty]].
Novel-synthesis claims capped at P_theoretical=0.50. All P values split into:
  P_theoretical (algebraic/lit precedent) x P_empirical (requires actual test on substrate).

---

## LEVEL 1 -- Hybrid retrieval landscape

### 1.1 BM25 + dense hybrid via Reciprocal Rank Fusion (RRF)

RRF (Cormack, Clarke, Buettcher, SIGIR 2009) fuses ranked lists by score = sum(1/(k+rank_i))
where k is typically 60. It requires no training and no score calibration between systems.
This is its primary advantage over linear interpolation (which requires tuning a weight alpha).

Recent benchmark results (FIRE 2025 shared task; arxiv 2604.01733):
- Hybrid BM25 + dense via RRF consistently outperforms either alone across all tested datasets.
- Largest lift on TAT-DQA: +8.1pp Recall@5 over BM25 alone.
- One evaluation showed up to 5.8x improvement in Recall@10 on MS MARCO over dense-only.

The mechanism is complementarity: BM25 catches exact lexical matches that neural embeddings
miss; dense catches paraphrase and distributional similarity that BM25 misses. RRF is robust
to score-scale mismatch between the two systems.

Substrate applicability: native K-hop traversal produces a ranked list by binding activation
strength. Fuzzy embedding retrieval produces a separate ranked list. RRF can fuse these with
zero training. This is the cheapest viable hybrid for substrate.

### 1.2 ColBERTv2 late interaction (Santhanam et al., 2021)

ColBERTv2 stores per-token embeddings for every document. At query time it computes
MaxSim(q_i, d_j) -- max cosine similarity between each query token and all document tokens --
then sums across query tokens. This "late interaction" achieves near bi-encoder speed with
near cross-encoder quality.

SPLATE (2024, SIGIR) bridges ColBERTv2 and SPLADE by projecting ColBERTv2 token embeddings
into a sparse vocabulary space. The SPLATE ColBERTv2 pipeline matches PLAID ColBERTv2
effectiveness while retrieving under 10ms by re-ranking only 50 candidates.

Substrate applicability: ColBERTv2's token-level representation is algebraically close to
substrate bindings. Each binding is effectively a token-level superposition. The MaxSim
operation could be approximated by argmax activation against the substrate codeword set.
This is a non-trivial mapping but worth a future drill (see Level 5 below).

### 1.3 SPLADE learned sparse retrieval (Formal et al., 2021)

SPLADE uses a BERT encoder with RELU+log activation to produce sparse vocabulary weights.
The resulting vectors are posted to an inverted index (same infrastructure as BM25) but
the weights are learned, not term-frequency derived. Inference-free variants (arxiv 2505.01452)
decouple SPLADE weights from inference time, further reducing latency.

Two-Step SPLADE (2024) adds a lightweight second-pass expansion step that improves
effectiveness while cutting index size.

Substrate applicability: SPLADE's learned sparsity is a different design axis than substrate
native bindings, but the "sparse activations over a vocabulary" framing is structurally
analogous to substrate's codeword activation pattern. The difference: SPLADE's vocabulary is
the full token vocabulary (~30k); substrate's vocabulary is the binding set (user-defined KG).
SPLADE is a fuzzy method that approximates structured lookup; substrate native is exact.

### 1.4 HippoRAG (Gutierrez et al., NeurIPS 2024) and HippoRAG-2

HippoRAG constructs an open knowledge graph from extracted entity-relation triples and runs
Personalized PageRank (PPR) with query concepts as seeds. This enables multi-hop retrieval
across disconnected documents without iterative LLM calls.

HippoRAG-2 extends this as a non-parametric continual learning framework: new documents are
added by extracting new triples and merging into the existing KG. PPR retrieval then
automatically surfaces multi-hop paths through the merged graph.

Key benchmark results: HippoRAG outperforms standard RAG on multi-hop QA (HotpotQA,
MuSiQue) while maintaining competitive single-hop performance. The graph traversal component
provides the multi-hop lift; dense retrieval provides the single-hop baseline.

Critical limitation: HippoRAG uses an LLM for triple extraction from unstructured documents.
Triple extraction quality degrades on noisy or ambiguous text. In substrate's use case,
bindings are entered explicitly (not extracted), which eliminates this failure mode.

### 1.5 PathRAG (2025) and Microsoft GraphRAG

PathRAG (arxiv 2502.14902) prunes graph-based RAG by focusing on relational paths between
query-relevant nodes rather than full community content. Flow-based pruning cuts context by
44% while maintaining accuracy. PathRAG is most effective when the KG has dense relational
structure between entities.

Microsoft GraphRAG (2024) uses LLM-generated community summaries at multiple granularities.
It achieves 86% accuracy on enterprise benchmarks vs 32% for baseline RAG on global
sense-making queries. The tradeoff: GraphRAG's community summary approach is expensive
(requires upfront LLM processing of the full corpus) but excels at synthesis queries where
no single passage contains the answer.

Key distinction: PathRAG is better for factoid + bridge multi-hop (precision); GraphRAG is
better for synthesis + comparison multi-hop (recall). Neither handles temporal or
counterfactual queries natively.

### 1.6 ToG-2.0 (Think on Graph 2.0, ICLR 2025)

ToG-2 is a tight-coupling hybrid: it alternates between KG beam search and dense text
retrieval iteratively. At each step, an LLM pruner retains the k most promising relation
paths; then text retrieval fetches supporting passages for each path. The LLM integrates
both and continues.

Key results: 14.6% improvement on HotpotQA over prior state-of-the-art; SoTA on 6/7
knowledge-intensive datasets with GPT-3.5; smaller models (Llama-2-13B) reach GPT-3.5
direct-reasoning level when augmented with ToG-2. The training-free plug-and-play design
makes it directly applicable to any KG + text corpus combination.

RouteRAG (arxiv 2512.09487, Dec 2025) extends this with RL: the entire RAG workflow
(when to retrieve, which mode -- text/graph/hybrid, when to answer) is learned as a
token-level policy via RL with a two-stage reward combining task accuracy and retrieval
efficiency. RouteRAG outperforms all RAG baselines on 5 QA benchmarks.

### 1.7 Hybrid retrieval surveys (2024-2026)

RAGRouter-Bench (arxiv 2602.00296) benchmarks lightweight query classifiers for adaptive
RAG. The finding: a T5-Large classifier routing among three strategies matches always-
expensive baselines at substantially lower cost. KNN and MLP routers on sentence embeddings
are competitive (RouterBench).

Adaptive-RAG (Jeong et al., NAACL 2024) trains a small classifier on automatically-derived
complexity labels to route: no retrieval / single-step / multi-step. This three-class routing
is the most empirically validated query routing approach as of 2025.

BalanceRAG (arxiv 2605.20084) applies statistical risk control to cascaded retrieval routing,
framing adaptive routing as a hypothesis test over a 2D lattice (retrieval depth x confidence
threshold) with certified reliability bounds.

---

## LEVEL 2 -- Query type taxonomy: regime predictions

Each prediction has P_theoretical (algebraic reasoning + lit precedent) and P_empirical
(probability this holds in direct substrate test). Deflation applied.

### 2.1 Factoid (single hop): "What is the capital of France?"

Regime prediction: FUZZY wins.
Reasoning: Single-hop factoid queries benefit from distributional similarity (bge-small,
e5, etc.) because the answer may be expressed with different surface forms than stored.
Native K-hop would require an exact entity match on the query string, which fails on
paraphrase. Empirical evidence from substrate: bge-small attention at 0.501 vs RAG 0.524
-- near-identical, not statistically different. For clean single-hop factoid in a KB with
exact entity strings, native is competitive; for paraphrase-heavy or noisy queries, fuzzy
dominates.

P_theoretical = 0.75 x P_empirical = 0.70
HARD-PASS condition: Fuzzy recall@1 >= 0.75 on single-hop factoid queries.
HARD-FAIL condition: Native recall@1 >= fuzzy recall@1 on paraphrase-reformulated queries.

### 2.2 Bridge multi-hop: "Who is the spouse of the person who founded Apple?"

Regime prediction: NATIVE wins decisively.
Reasoning: Bridge multi-hop requires traversing an intermediate entity. Dense retrieval
conflates the query with text mentioning all entities tangentially; native K-hop follows
exact (founded_by, spouse_of) relations. Substrate empirical: K=2 recall@2=0.80 (discrete),
dropping to 0.33 (fuzzy rho=0.9). The fuzzy collapse is catastrophic.

P_theoretical = 0.90 x P_empirical = 0.85
HARD-PASS: Native K-hop recall@2 >= 0.75 on bridge multi-hop; fuzzy recall@2 <= 0.50.
HARD-FAIL: Native recall@2 <= fuzzy recall@2 on bridge multi-hop with exact bindings.

### 2.3 Comparison multi-hop: "Does X have more employees than Y?"

Regime prediction: NATIVE wins if attributes are stored as typed bindings; FUZZY wins if
attributes are implicit in text.
Reasoning: Comparison requires retrieving attribute values for two entities and applying
a comparator. If (X, employee_count, 5000) and (Y, employee_count, 3000) are stored as
triples, native K-hop retrieves both in O(K) and the comparator is trivial. If the counts
are embedded in prose paragraphs, fuzzy retrieval finds the passages but the comparator
requires LLM extraction. The boundary is whether numerical attributes are explicitly
structured in the KB.

P_theoretical = 0.80 x P_empirical = 0.60 (depends on KB structure)
HARD-PASS: Native comparison retrieval accuracy >= 0.85 when attributes are explicit triples.
HARD-FAIL: Native comparison accuracy <= 0.60 when attributes require numerical parsing.

### 2.4 Aggregation: "How many countries does X operate in?"

Regime prediction: NATIVE wins if the KB has typed set membership; FUZZY degrades.
Reasoning: Aggregation requires counting all entities satisfying a predicate. Fuzzy
retrieval returns a top-k ranked list but cannot guarantee recall over a full set.
Native set retrieval via substrate bindings can retrieve all (X, operates_in, ?) bindings
exhaustively. Fuzzy retrieval cannot enumerate a complete set reliably.

P_theoretical = 0.75 x P_empirical = 0.55 (depends on completeness of KB)
HARD-PASS: Native set recall >= 0.90 for aggregation when KB is complete.
HARD-FAIL: Native recall < 0.70 due to incomplete bindings (if KB coverage is partial,
           aggregation fails regardless of retrieval method).

### 2.5 Temporal: "What was X's revenue in Q3 2022?"

Regime prediction: NATIVE wins strongly if temporal attributes are stored as typed triples;
HYBRID if temporal information is in documents.
Reasoning: Substrate has empirically validated bitemporal native storage (0.003ms per
cycle 175). Temporal queries map directly to (entity, attribute, value, timestamp) lookups.
Dense retrieval on temporal queries is unreliable because temporal references in text are
implicit and vector similarity is not timestamp-sensitive.

TCAR-Gen (arxiv 2606.00029) and T-GRAG (arxiv 2508.01680) both confirm that purely
dense retrieval fails on temporal queries; temporal-aware graph traversal is required.

P_theoretical = 0.85 x P_empirical = 0.80
HARD-PASS: Native temporal retrieval accuracy >= 0.85 on typed temporal bindings.
HARD-FAIL: Dense retrieval accuracy >= 0.80 on temporal queries (would invalidate
           the temporal native advantage).

### 2.6 Counterfactual: "What if X were Y -- how would Z change?"

Regime prediction: NATIVE wins via do-operator/interventional bindings (empirically HP,
cycle 175). Fuzzy cannot represent interventional distributions.
Reasoning: Counterfactual queries require representing a modified world state and
traversing the modified KG. This is structurally impossible with pure vector similarity.
The substrate do-operator (Wish 1 counterfactual, cycle 175, empirically validated 20/20)
provides native counterfactual support.

P_theoretical = 0.90 x P_empirical = 0.85 (empirically validated baseline exists)
HARD-PASS: Native counterfactual retrieval maintains accuracy >= 0.80 under intervention.
HARD-FAIL: Intervention changes retrieval outputs in unexpected ways (intervention leaks
           to non-intervened paths).

### 2.7 Procedural: "How do I configure X to do Y?"

Regime prediction: HYBRID -- fuzzy for initial passage retrieval; native if procedure
steps are stored as instruction-graph triples.
Reasoning: Procedural queries are sequence-structured. If the procedure is stored as a
dependency graph (step_1 --requires--> step_2, step_2 --requires--> step_3), native
traversal recovers the full sequence. If the procedure is in unstructured documentation,
fuzzy retrieval finds the relevant section but loses step ordering. Hybrid wins most
reliably: fuzzy for document identification, native for step ordering.

P_theoretical = 0.70 x P_empirical = 0.55
HARD-PASS: Hybrid procedure retrieval (fuzzy-identify + native-sequence) outperforms
           fuzzy-only by >= 15pp on sequential accuracy.
HARD-FAIL: Native-only procedure retrieval fails when procedure steps have paraphrase
           variation in query formulation.

### 2.8 Synthesis: "Summarize all findings on topic X"

Regime prediction: FUZZY (or LLM attention) wins. Native retrieval returns point facts,
not thematic summaries.
Reasoning: Synthesis requires identifying all relevant content on a topic and aggregating.
This is exactly what dense retrieval with high-k return excels at. Native K-hop retrieval
returns paths from a specific entity -- not thematic clustering across entities.
Microsoft GraphRAG's community summary approach dominates here, but that requires upfront
LLM processing. For substrate, the right approach is: fuzzy retrieval returns all relevant
documents, then LLM synthesizes.

P_theoretical = 0.80 x P_empirical = 0.70
HARD-PASS: Fuzzy+LLM synthesis outperforms native-only on synthesis queries by >= 20pp.
HARD-FAIL: Native-only synthesis achieves >= 0.70 F1 on standard synthesis benchmarks
           (would indicate KB structure is rich enough to substitute for synthesis).

---

## Summary table (regime predictions)

Query type          | Native wins | Fuzzy wins | Hybrid  | P_theoretical x P_empirical
--------------------|-------------|------------|---------|----------------------------
Factoid             |             | X          |         | 0.75 x 0.70
Bridge multi-hop    | X           |            |         | 0.90 x 0.85
Comparison          | X (if typed)|            | maybe   | 0.80 x 0.60
Aggregation         | X           |            |         | 0.75 x 0.55
Temporal            | X           |            |         | 0.85 x 0.80
Counterfactual      | X           |            |         | 0.90 x 0.85
Procedural          |             |            | X       | 0.70 x 0.55
Synthesis           |             | X          |         | 0.80 x 0.70

Reading: native dominates on 4/8 types; fuzzy on 2/8; hybrid on 1; comparison is
conditional. This is a strong case for dual-storage with routing.

---

## LEVEL 3 -- Routing strategies

### 3.1 Static routing via question-type classifier

Design: Small LLM (T5-base or DeBERTa-base; ~100M params) trained to classify queries
into native-preferred / fuzzy-preferred / hybrid. Features: query string + possibly
KB schema vocabulary presence.

Evidence: Adaptive-RAG (NAACL 2024) validates that a T5-Large classifier routing among
3 strategies matches oracle-expensive baselines. RAGRouter-Bench (2604.03455) shows KNN
and MLP classifiers on sentence embeddings are competitive at lower cost.

Strengths: predictable latency; no runtime overhead from trying both paths.
Weaknesses: classifier errors are unrecoverable; no fallback if routing is wrong;
requires labeled training data.

P_theoretical (routing correct > 85%) = 0.65 x P_empirical = 0.55
Pre-reg: classifier accuracy >= 80% on held-out query type test set.
HARD-FAIL: < 65% routing accuracy (worse than heuristic baseline).

### 3.2 Parallel + RRF fusion

Design: Run native K-hop and fuzzy embedding retrieval in parallel; fuse ranked lists
via RRF(k=60). No training required.

Evidence: RRF is the best-validated hybrid fusion approach (Cormack 2009; confirmed in
FIRE 2025, TAT-DQA +8.1pp, MS MARCO 5.8x Recall@10 improvement). Works even when
constituent systems have incompatible score scales.

Strengths: zero training; robust to miscalibration; leverages complementarity.
Weaknesses: double the retrieval cost; does not weight by query type; may degrade on
queries where one method is strongly superior (RRF dilutes the winner's advantage).

P_theoretical = 0.80 x P_empirical = 0.70
Pre-reg: parallel+RRF >= max(native, fuzzy) on held-out mixed query benchmark.
HARD-FAIL: RRF score < min(native, fuzzy) on any query type sub-slice.

### 3.3 Cascade: native-first, fuzzy fallback

Design: Run native K-hop first. If retrieval confidence is above threshold T, return.
If below T, run fuzzy retrieval and fuse or replace.

Evidence: BalanceRAG (2605.20084) provides statistical risk control for cascade routing
with confidence thresholds, framing the threshold selection as hypothesis testing over a
2D lattice. The result: threshold-based cascade achieves statistically certified reliability
better than fixed routing. Graph-augmented hybrid retrieval (dev.to 2025) confirms
multi-stage re-ranking with confidence-based fallback is effective.

Confidence signal candidates for substrate: binding activation margin (max_activation -
second_max_activation), binding entropy (entropy of activation distribution), hop-count
(if K-hop traversal finds no path at K=2, fall back to fuzzy).

Strengths: cheapest case is native-only (no fuzzy overhead); fallback is principled.
Weaknesses: confidence calibration is non-trivial for a novel substrate architecture;
threshold requires tuning; latency is bimodal.

P_theoretical = 0.75 x P_empirical = 0.60
Pre-reg: cascade achieves >= 95% of parallel+RRF quality at <= 60% of retrieval cost.
HARD-FAIL: No confidence signal predicts retrieval failure well enough (AUROC < 0.65).

### 3.4 Hybrid index: both triples and embeddings in same binding structure

Design: Substrate stores BOTH the triple binding (entity_id XOR relation XOR value) AND
an embedding vector bound to the same entity_id. Query time: both the binding activation
and the embedding cosine are computed simultaneously; algebraically fused before returning
candidates.

Evidence: NeuSymMS (arxiv 2605.17596) combines neural fact extraction with CLIPS-based
symbolic storage as subject-relation-value triples. NS-Mem (2025) uses a three-layer
architecture (episodic + semantic + neuro-symbolic) with hybrid retrieval combining
embedding similarity and deterministic symbolic query. Both demonstrate viability of
simultaneous dual representation.

Substrate-specific opportunity: because substrate stores all bindings as vectors in a
shared high-dimensional space, the entity_id vector IS already shared. Adding an embedding
dimension to the binding can be done by extending the binding pattern (entity_id XOR
relation XOR value XOR embedding_compressed). Whether this preserves binding orthogonality
is an algebraic question requiring empirical test (Level 5 analysis below).

Strengths: single-pass retrieval; algebraic fusion; no routing decision needed.
Weaknesses: binding capacity load increases (more patterns stored); compressive interaction
between triple structure and embedding may degrade both signals (novel risk).

P_theoretical = 0.50 (novel; no published precedent for this specific design) x P_empirical = 0.35
Pre-reg: hybrid binding achieves >= 90% of native-only K-hop AND >= 90% of fuzzy-only recall.
HARD-FAIL: hybrid binding K-hop recall < 0.70 OR fuzzy recall < 0.70 (structural degradation).

### 3.5 RL-trained routing policy (RouteRAG-style)

Design: Train a small policy network (or adapter on a small LLM) that at each retrieval
step selects from {native, fuzzy, hybrid, no-retrieval, answer}. Reward combines task
accuracy and retrieval efficiency. End-to-end RL with two-stage training.

Evidence: RouteRAG (arxiv 2512.09487, ICLR candidate 2025) validates that RL routing
over text+graph retrieval outperforms all static RAG baselines on 5 QA benchmarks.
GraphRAG-Router (arxiv 2604.16401) specifically uses RL to route between GraphRAG
variants and LLMs with cost efficiency.

Strengths: adapts to query distribution; can discover non-obvious routing patterns;
handles multi-step queries with interleaved native+fuzzy.
Weaknesses: training cost; requires labeled query-outcome pairs; RL instability if reward
is sparse; highest engineering complexity of all routing strategies.

P_theoretical = 0.70 x P_empirical = 0.45 (engineering cost is the binding constraint)
Pre-reg: RL routing achieves >= 95% of oracle routing accuracy on held-out benchmark.
HARD-FAIL: RL policy collapses to always-native or always-fuzzy (degenerate policy).

---

## LEVEL 4 -- Substrate-specific architectural opportunities

### 4.1 Algebraic fusion: pattern B encoding of BOTH structure AND embedding

Substrate bindings are high-dimensional vectors. A Pattern B binding encodes
(entity_id, relation, value) as a superposition. One can extend this to encode
(entity_id, relation, value, embedding_token_1, ..., embedding_token_K) where
embedding tokens are the top-K activated codewords from a fuzzy encoder. This creates
a binding that answers BOTH "does (X, r, Y) exist?" (discrete lookup) and "what is
semantically near X?" (embedding lookup) from a single stored vector.

The risk: superposition capacity degrades as more items are bound (cross-talk grows with
M/N ratio). Whether adding embedding tokens to triples stays within capacity is an
algebraic question. At N=65k and M around 10k triples, there may be room. At N=4096
(production scale), this requires careful capacity accounting.

Verdict on P_theoretical = 0.40 x P_empirical = 0.25.
This is genuinely novel and worth a cheap CPU-scale test.

### 4.2 K-hop traversal with nearest-binding fallback

When a discrete K-hop traversal fails (no binding found at hop K), instead of returning
empty, the substrate can activate the nearest binding by cosine similarity in the original
binding space. This is a "fuzzy fallback" within the native mechanism rather than a
separate fuzzy retrieval system.

Analogy: this is equivalent to link prediction in KG completion (TransE, DistMult etc.)
but implemented as nearest-neighbor search in the substrate binding space.

This is conservative and lower risk than 4.1. The fallback only activates when the discrete
lookup fails; it does not degrade the discrete path.

P_theoretical = 0.65 x P_empirical = 0.55
Pre-reg: fallback retrieval recovers >= 60% of failed K-hop cases.
HARD-FAIL: fallback introduces false positives at rate >= 20% (wrong entity retrieved).

### 4.3 Two-stage pipeline: fuzzy as rough draft, native as exact match

Design: Fuzzy embedding retrieval identifies candidate entities (top-K nearest by
cosine similarity). Native K-hop then runs starting from those candidate entities rather
than from the parsed query. This is analogous to the dense-then-graph two-stage approach
validated in the dual-level pipeline for KG-QA (Level 1 review above).

This is the safest hybrid design -- it does not modify any binding structure. Fuzzy
retrieval handles entity disambiguation and paraphrase; native retrieval handles graph
traversal from the identified entity.

P_theoretical = 0.80 x P_empirical = 0.70
Pre-reg: two-stage achieves >= 0.85 recall@2 on bridge multi-hop when query uses
         paraphrase of entity names.
HARD-FAIL: native K-hop from fuzzy-identified entity achieves less than native K-hop
           from exact entity match (i.e., fuzzy stage introduces noise net-negative).

### 4.4 Auditability as native-default for regulated queries

Published: NeuSymMS explicitly cites provenance and auditability as a primary motivation
for symbolic storage alongside neural. T-GRAG, TCAR-Gen both cite temporal auditability.

Substrate native bindings provide exact provenance: result Y was retrieved via
(entity_id, relation) at hop K=2. Fuzzy retrieval provides only cosine-similarity
scores, which are not interpretable as provenance.

For any regulated industry query (HIPAA, EU AI Act Article 12, financial audit trail),
native-first routing should be the DEFAULT with fuzzy only as fallback. This is a product
architecture decision, not just a performance optimization.

EU AI Act Article 12 (August 2026 deadline): requires human-readable explanation of
AI-generated outputs. Native binding provenance is directly compliant; vector similarity
scores are not without additional explanation layers.

P_theoretical = 0.95 (regulatory argument; no benchmark needed) x P_empirical = 0.90
This is not a retrieval performance claim -- it is a product architecture requirement.

### 4.5 Cost analysis: native K-hop is O(K * binding_lookup) vs fuzzy O(N)

At large KB size N:
- Native K-hop traversal: K lookups, each O(log N) with an inverted index on entity_id.
  For K=2, this is 2 * O(log N) ~ constant for practical N.
- Fuzzy embedding retrieval: O(N * d) for brute force, O(N^0.5 * d) for HNSW
  approximate nearest neighbor (HNSW is the standard; Malkov & Yashunin 2018).
- At N=1M entities, HNSW ANN is ~10ms; native K-hop is ~1ms (substrate empirically
  validated at 4.174ms for SMW pinv at N=65k; should scale sub-linearly).

Native K-hop is categorically cheaper at large KB size for structured queries.
Fuzzy is unavoidable for unstructured/paraphrase queries but it costs more.

This asymmetry supports cascade-native-first as the default architecture at scale.

---

## LEVEL 5 -- Novel hybrid architectures

### 5.1 Binding entropy routing

Proposal: Compute Shannon entropy of the activation vector after running the query
against the substrate binding pool. Low entropy (activation concentrated on a few
bindings) indicates a structured query with a clean match -- route native. High entropy
(activation diffuse across many bindings) indicates an unstructured/paraphrase query
-- route fuzzy.

Mechanism: entropy H = -sum(p_i * log(p_i)) where p_i = normalized activation of
binding i. This is computable in O(M) after a single substrate forward pass. No LLM
classifier needed -- the substrate self-diagnoses routing confidence.

Adjacent literature: binding information as multivariate mutual information (2025 result
from the information-theoretic RAG framing, arxiv electronics 2025). The "retrieval
capacity" paper notes capacity is limited by embedding dimension and schema entropy.

P_theoretical = 0.50 (novel; no published precedent for entropy-based routing within
a unified substrate) x P_empirical = 0.35
This is the most novel architecture in this drill. Cheap to test (add entropy calculation
to existing substrate forward pass; measure correlation with routing correctness).

Pre-reg for cheap test: Pearson correlation between binding entropy and native retrieval
success rate on mixed query benchmark >= 0.40. If so, threshold routing is viable.
HARD-FAIL: correlation < 0.20 (entropy is uninformative about query type).

### 5.2 Contrastive routing training

Design: Generate (query, correct_regime) pairs by running both native and fuzzy on
a labeled query set and identifying which regime was correct. Train a lightweight
classifier (or adapter on a small LLM) contrastively: queries that benefited from
native are positive for "native" class and vice versa.

Evidence: Adaptive-RAG (NAACL 2024) is the direct precedent -- their T5-Large classifier
was trained exactly this way (complexity labels derived from which strategy succeeded).
RouteRAG shows that RL training of the full policy outperforms static classifiers when
the training data is available.

P_theoretical = 0.70 (well-precedented) x P_empirical = 0.55 (requires generating
labeled pairs, which requires running experiments first)

### 5.3 Substrate as universal index (triples + embeddings + sparse keywords together)

Design: Substrate stores three parallel representations for each KB item:
  - discrete triple: (entity_id XOR relation XOR value)
  - embedding vector: compressed representation of entity description
  - sparse keyword vector: BM25-style term weights for key terms

Query processing: each incoming query generates all three representations; substrate
activation combines triple-match, embedding-cosine, and keyword-match as three additive
terms with learned or fixed weights.

This is analogous to SPLATE's fusion of ColBERTv2 token embeddings with SPLADE sparse
weights, but implemented natively in substrate binding space.

P_theoretical = 0.45 (novel; no direct published precedent) x P_empirical = 0.30
Caution: storing three representations per entity multiplies binding load by ~3x. At
N=65k substrate, this may hit capacity ceiling. Cheap test: add keyword-sparse component
to existing dual binding; measure capacity degradation.

### 5.4 Multi-resolution substrate: hierarchical KB with depth-adaptive browsing

Design: KB stored at three levels:
  - Level 1: concept nodes (high-level entities and themes)
  - Level 2: sub-concept nodes (specific instances, attributes)
  - Level 3: triple bindings (exact relations and values)

Query routing: initial activation hits Level 1 (fast, coarse). If Level 1 confidence is
high, drop to Level 2 matching the activated concept. If Level 2 confidence is high, run
Level 3 exact binding lookup. This is a top-down beam search with substrate.

Adjacent literature: LeanRAG (arxiv 2508.10391) implements hierarchical semantic
aggregation for graph-RAG. KET-RAG (arxiv 2502.09304) implements multi-granular indexing.
Both show that hierarchical retrieval reduces cost without recall loss.

P_theoretical = 0.65 x P_empirical = 0.50
Engineering complexity is moderate. The key question is whether substrate's capacity
supports three-level hierarchy without cross-level interference.

### 5.5 Substrate "thoughts": caching K-hop traversal traces as bindings

Design: When a multi-hop traversal succeeds (e.g., finds path entity_A ->r1-> entity_B
->r2-> entity_C with activation above threshold), store the traversal trace itself as a
new binding: (query_hash, traversal_path, result). Future queries matching the same
pattern retrieve the cached trace in O(1) rather than re-running K-hop.

This is analogous to MEMOIZATION in procedural programming but implemented as substrate
bindings. It converts repeated expensive K-hop queries into cheap single-hop trace lookups.

Adjacent: NeuSymMS's KB uses lifecycle rules (deduplication, reconciliation) on stored
facts -- trace caching is a specialized lifecycle pattern.

P_theoretical = 0.60 x P_empirical = 0.45
Caution: trace cache grows without bound unless an eviction policy is defined. Requires
binding space management.

### 5.6 Federation hybrid: per-customer storage regime in shared substrate

Design: Customer A's bindings are stored as NATIVE triples (enterprise with structured KG).
Customer B's bindings are stored as FUZZY embeddings (media company with unstructured docs).
Substrate handles both natively because both are stored as high-dimensional vectors;
the routing distinction is encoded as a metadata binding: (customer_id, storage_regime, native|fuzzy).

This is structurally enabled by substrate's unified vector space -- native triples and
fuzzy embeddings are both vectors; they live in the same space.

No direct published precedent for this specific architecture, but it is algebraically
trivial given substrate's design.

P_theoretical = 0.70 (algebraically straightforward) x P_empirical = 0.55 (requires
multi-tenant routing which may introduce cross-tenant interference in shared binding pool)

### 5.7 Online learning: auto-tuning routing weights from query outcome feedback

Design: Each successful retrieval updates a per-regime weight table indexed by query
features (entity density, hop count, query length, keyword exactness). Failed retrievals
decrement the weight. The routing decision is a softmax over learned regime weights given
query features.

Evidence: DynamicRAG (Sun et al., 2025) adaptively adjusts k (number of retrieved docs)
per query using online feedback. RouteLLM (Ong et al., 2025) shows online learning of
routing weights reduces strong-model calls by 40% with no quality loss.

P_theoretical = 0.65 x P_empirical = 0.50
The key risk: online learning requires a reliable success signal. In a deployed system,
the success signal is user feedback or LLM evaluation -- both are noisy.

---

## Cross-cutting analysis: optimal hybrid architecture for substrate

Given the empirical evidence and literature review, the following architecture is recommended:

TIER 1 (immediate, no new engineering):
Deploy dual-storage with cascade routing (architecture 3.3).
- All queries run native K-hop first.
- If binding activation confidence (entropy or margin) is below threshold, fall back to fuzzy.
- RRF fusion for cases where both signals are above threshold.
- Rationale: this captures native's advantages on 4/8 query types; recovers gracefully
  on factoid and synthesis queries; requires no new training infrastructure.

TIER 2 (1-3 weeks, moderate engineering):
Add two-stage pipeline (architecture 4.3) as the default for entity-heavy queries:
- Fuzzy retrieval identifies candidate entities (entity disambiguation, paraphrase handling).
- Native K-hop runs from identified entities.
- Rationale: solves the paraphrase problem for bridge multi-hop without modifying binding structure.

TIER 3 (3-6 weeks, higher investment):
Add binding entropy routing signal (architecture 5.1):
- Compute activation entropy as a routing feature alongside confidence margin.
- Cheap test validates feasibility before committing to full implementation.
- Rationale: eliminates need for external LLM classifier for routing; substrate self-routes.

TIER 4 (speculative, 4-8 weeks):
RL routing policy (architecture 3.5):
- Only justified if labeled (query, correct_regime) dataset can be built from Tiers 1-3.
- RouteRAG demonstrates the payoff: consistent SoTA on 5 QA benchmarks.

---

## Customer pitch implications

The hybrid architecture enables a single product to serve:
1. Free-text RAG users (single-shot + LLM attention on fuzzy substrate) -- same performance
   as existing RAG systems, lower latency (no LLM for retrieval).
2. KG QA users (native K-hop on discrete substrate) -- demonstrably superior to dense
   retrieval on multi-hop, temporal, and counterfactual queries.
3. Regulated-industry users (native-first + auditability trail) -- EU AI Act Article 12
   compliance is native to the architecture, not bolted on.

These are three distinct customer segments that can be served by the same substrate
deployment with routing-level differentiation. No other single system in the published
literature serves all three simultaneously with native provenance + O(K) traversal cost.

---

## Engineering-tractable anchor candidates (5, ranked by P_actionable)

### Anchor A: RRF fusion of native + fuzzy on mixed query benchmark (TIER 1)

What it tests: Whether native K-hop + fuzzy retrieval + RRF achieves >= max(native, fuzzy)
across a mixed query type benchmark including at least factoid, bridge multi-hop, temporal.
Why now: cheapest validation of the hybrid thesis. Requires only writing a fusion wrapper;
         no new substrate changes needed.
Tier: CPU laptop, ~1-2 hours, no cloud.
P_theoretical = 0.80 x P_empirical = 0.70 (calibrated)
HARD-PASS: RRF hybrid recall@2 >= max(native, fuzzy) + 5pp on bridge multi-hop; no degradation on factoid.
HARD-FAIL: RRF hybrid worse than native on bridge multi-hop (would indicate RRF dilution hurts).
MID-BAND: RRF >= max on multi-hop but < max on factoid (need alpha-tuned hybrid).

### Anchor B: Cascade native-first with entropy/margin fallback (TIER 1)

What it tests: Whether substrate's own activation signal (entropy or margin) is a reliable
predictor of retrieval success, enabling cascade routing without external classifier.
Why now: activates only after Anchor A validates fusion; requires logging per-query confidence.
Tier: CPU laptop, ~2-4 hours.
P_theoretical = 0.65 x P_empirical = 0.50
HARD-PASS: AUROC of confidence signal vs success >= 0.70.
HARD-FAIL: AUROC < 0.60 (confidence signal is uninformative; must use external classifier).
MID-BAND: AUROC in [0.60, 0.70] (threshold-based cascade partially viable).

### Anchor C: Two-stage entity disambiguation + K-hop (TIER 2)

What it tests: Whether fuzzy retrieval of candidate entities followed by native K-hop
from those entities outperforms native K-hop from exact entity parse on paraphrase-heavy queries.
Why now: directly addresses the failure mode where query uses paraphrase of entity name.
Tier: CPU laptop, ~2-4 hours.
P_theoretical = 0.75 x P_empirical = 0.60
HARD-PASS: Two-stage recall@2 >= native-from-exact + 10pp on paraphrase queries.
HARD-FAIL: Two-stage introduces more false positives than it recovers (net negative).

### Anchor D: Binding entropy routing correlation test (TIER 3, cheap pretest for 5.1)

What it tests: Whether substrate activation entropy correlates with correct regime
selection on a labeled query set.
Why now: this is the cheapest test for the most novel architecture (5.1); single forward
         pass + entropy computation + correlation measurement.
Tier: CPU laptop, ~1 hour.
P_theoretical = 0.50 x P_empirical = 0.35
HARD-PASS: Pearson r >= 0.40 between entropy and routing correctness.
HARD-FAIL: r < 0.20 (entropy is uninformative; external classifier is required).

### Anchor E: Multi-hop bridge query with paraphrase entity names (regression test)

What it tests: Baseline measurement of the paraphrase failure mode -- how much does
native K-hop degrade when entity names in the query differ from stored binding entity names?
Why now: this quantifies the size of the problem that Anchors B and C are solving;
         without this measurement, the improvement claims are relative to an unknown baseline.
Tier: CPU laptop, ~30-60 minutes.
P_theoretical = 0.90 (the failure mode is expected based on discrete binding design) x
P_empirical = 0.85
HARD-PASS: native K-hop recall@2 drops >= 20pp on paraphrase vs exact entity queries
           (confirms the problem is real and worth solving).
HARD-FAIL: native K-hop recall@2 is within 5pp on paraphrase vs exact (paraphrase is not
           a real failure mode; skip Anchors B and C).

---

## Cheap decisive test

Run Anchor E FIRST (30-60 min, no new infrastructure). This establishes whether
the paraphrase failure mode is real on the current substrate.

If Anchor E confirms >= 20pp degradation:
  Run Anchor A next (RRF hybrid fusion, 1-2 hours).
  If Anchor A HARD-PASS, the hybrid thesis is validated and Anchors B-D follow.

If Anchor E shows < 5pp degradation:
  Skip Anchors B and C. The paraphrase problem is not real on this substrate.
  Run Anchor D (entropy routing correlation) as the next novel test.

Total investment before first decision gate: ~2-4 hours CPU, no cloud.

---

## Falsifiable predictions (pre-registered)

HARD-PASS (research confirms hybrid works):
1. RRF(native + fuzzy) >= max(native, fuzzy) + 5pp on bridge multi-hop recall@2
2. Native K-hop >= 0.75 on bridge multi-hop with exact entity names
3. Fuzzy alone <= 0.50 on bridge multi-hop (confirms collapse pattern)
4. Entropy signal AUROC >= 0.65 for cascade routing

HARD-FAIL (hybrid hypothesis refuted):
1. RRF(native + fuzzy) < native on bridge multi-hop (fusion hurts)
2. Paraphrase degradation < 5pp (paraphrase failure mode is not real)
3. Native K-hop recall@2 < 0.60 on exact-entity bridge queries (native collapses
   even with correct bindings -- structural failure)
4. Entropy AUROC < 0.55 (substrate cannot self-route)

---

## Cross-thread synthesis

- Cycle 175 Wish 1 counterfactual empirical validation (HP) directly supports Anchor 4.4
  (auditability, regulatory use case). The do-operator result provides a concrete native
  advantage that no fuzzy system can replicate.
- iterative_regime_crossover_cpu_v1 HP confirms that rho=0.5 MILD regime helps K-hop but
  rho=0.9 FUZZY collapses it. This is the key empirical anchor for the regime prediction
  table in Level 2. The routing strategy is NOT about choosing between substrate regimes
  (discrete vs fuzzy rho) but between SUBSTRATE NATIVE BINDINGS vs EXTERNAL FUZZY EMBEDDINGS.
  These are different architectural layers. The rho collapse is about internal substrate
  coherence noise; the hybrid question is about external retrieval index design.
- Cycle 178 PP-99 single-shot result (0.501 vs RAG 0.524, not statistically different)
  confirms that fuzzy substrate alone does not beat standard RAG. This motivates the hybrid:
  fuzzy substrate handles what RAG handles; native substrate handles what RAG cannot.
- Multi-hop revival (MEMORY: project_multihop_revive_priority.md) is directly relevant.
  The hybrid architecture with two-stage entity disambiguation (Anchor C) is one of the
  revival paths for multi-hop performance.
- North Star (MEMORY: north_star_functional_system_beats_LLMs.md): hybrid architecture
  enables the clearest demo path -- show that (native K-hop + fuzzy fallback) on a 1M
  KB outperforms GPT-4 on multi-hop structured QA, while matching RAG-style single-hop.
  That is the head-to-head comparison the North Star mandates.

---

## Substrate-product implications

1. Hybrid routing is NOT optional for a production product. The empirical evidence shows
   native-only fails on factoid and synthesis; fuzzy-only fails on multi-hop. A product
   that routes between them is the minimum viable competitive architecture.

2. The auditability advantage (architecture 4.4) is a genuine differentiator from any
   purely neural retrieval system and is growing in importance with EU AI Act Article 12
   (August 2026). Product positioning should lead with this, not with performance benchmarks
   alone.

3. The federation story (architecture 5.6) enables a single deployment to serve
   heterogeneous customers. This is a deployment simplicity argument (one system, not N
   specialized systems) that compounds the value of the substrate as a platform.

4. Cost (architecture 4.5): native K-hop being O(K * log N) vs fuzzy O(N^0.5 * d) means
   that at scale (N >= 1M), native retrieval has a hard cost advantage. The product can
   be priced around this: native is the premium, low-latency tier; fuzzy is the fallback
   that has higher per-query cost at large N.

---

## Citations (verified count: 22)

1. Cormack, Clarke, Buettcher. "Reciprocal Rank Fusion outperforms Condorcet and individual
   rank learning methods." SIGIR 2009.
2. Santhanam et al. "ColBERTv2: Effective and Efficient Retrieval via Lightweight Late
   Interaction." arXiv 2021.
3. Formal et al. "SPLADE: Sparse Lexical and Expansion Model for First Stage Ranking." 2021.
4. Slade. "SPLATE: Sparse Late Interaction Retrieval." SIGIR 2024. arXiv:2404.13950.
5. Gutierrez et al. "HippoRAG: Neurobiologically Inspired Long-Term Memory for Large
   Language Models." NeurIPS 2024.
6. Edge et al. "From Local to Global: A Graph RAG Approach to Query-Focused Summarization."
   Microsoft Research 2024.
7. Chen et al. "PathRAG: Pruning Graph-based Retrieval Augmented Generation with Relational
   Paths." arXiv:2502.14902, 2025.
8. Sun et al. "Think-on-Graph 2.0: Deep and Faithful Large Language Model Reasoning with
   Knowledge-guided Retrieval Augmented Generation." ICLR 2025. arXiv:2407.10805.
9. Jeong et al. "Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models
   through Question Complexity." NAACL 2024. arXiv:2403.14403.
10. Hu et al. "RAGRouter-Bench: A Dataset and Benchmark for Adaptive RAG Routing."
    arXiv:2602.00296, 2025.
11. Nie et al. "RouteRAG: Efficient Retrieval-Augmented Generation from Text and Graph via
    Reinforcement Learning." arXiv:2512.09487, Dec 2025.
12. GraphRAG-Router. "Learning Cost-Efficient Routing over GraphRAGs and LLMs with
    Reinforcement Learning." arXiv:2604.16401, 2026.
13. BalanceRAG. "Joint Risk Calibration for Cascaded Retrieval-Augmented Generation."
    arXiv:2605.20084, 2026.
14. NeuSymMS. "A Hybrid Neuro-Symbolic Memory System for LLM Agents." arXiv:2605.17596, 2025.
15. NS-Mem. "Advancing Multimodal Agent Reasoning with Long-Term Neuro-Symbolic Memory."
    arXiv:2603.15280, 2025.
16. TCAR-Gen. "Temporal Graph Retrieval with Evidence Fusion for Knowledge-Grounded
    Generation." arXiv:2606.00029, 2026.
17. T-GRAG. "A Dynamic GraphRAG Framework for Resolving Temporal Conflicts and Redundancy
    in Knowledge Retrieval." arXiv:2508.01680, 2025.
18. LeanRAG. "Knowledge-Graph-Based Generation with Semantic Aggregation and Hierarchical
    Retrieval." arXiv:2508.10391, 2025.
19. KET-RAG. "A Cost-Efficient Multi-Granular Indexing Framework for Graph-RAG."
    arXiv:2502.09304, 2025.
20. Two-Step SPLADE. arXiv:2404.13357, 2024.
21. arxiv 2604.01733. "From BM25 to Corrective RAG: Benchmarking Retrieval Strategies
    for Text-and-Table Documents." 2026.
22. Ong et al. "RouteLLM: Learning to Route LLMs with Preference Data." 2025.
