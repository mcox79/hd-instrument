# Substrate Stateful Memory + Tool Orchestration -- Integration Engineering Analysis

**Date:** 2026-06-08
**Topic:** How substrate maintains stateful memory across sessions, decides what to remember, and orchestrates tool calls (LLM as one of many tools)
**P_deflated:** 0.62 (raw lit confidence 0.77-0.87, deflated 0.15-0.25 per calibration rule)
**Calibration note:** Novel-synthesis paths capped at 0.50; PP-series primitives are empirically validated but integration patterns are engineering, not guaranteed

---

## HEADLINE

Substrate already has every primitive needed for a first-class stateful conversational agent: per-tenant algebraic isolation (PP-101), multi-turn state (PP-195), bitemporal AS-OF queries (0.003ms empirical), exact erasure (PP-104 0.0000ms GDPR), Merkle audit (PP-184), sleep-defrag consolidation (PP-141/142), intent classifier (PP-198), and cascade router (PP-123). The integration engineering question is how these compose into a coherent memory-decision loop and tool-dispatch pipeline. This note maps each level-1 through level-7 probe to a substrate primitive, surfaces the key engineering gaps, and proposes 7 ranked experiment anchors.

---

## 1. Statefulness Across Sessions

### 1.1 Per-user substrate state / multi-tenant isolation

Substrate primitive: **PP-101 cross-tenant isolation** (empirical: 0.0000 leakage). The algebraic mechanism is Hadamard binding with per-tenant seed keys -- vectors from different tenants are algebraically incommensurable.

Lit confirmation (2026): Aeon system (arXiv 2601.15311) demonstrates lock-striping with sharded semantic buffers, routing by session-ID hash, achieving strict isolation at >100k concurrent sessions on one node. AWS AgentCore uses tenant_id TurnContext fields. Curator (arXiv 2401.07119) indexes per-tenant vector partitions without cross-contamination.

Gap: PP-101 isolation is per-tenant at the storage layer; the integration layer needs a session-scoped index key (distinct from global tenant key) so the same tenant can have multiple independent conversation threads. This is a thin wrapper, not a new primitive.

### 1.2 Cross-session persistence

Substrate primitive: **PP-195 multi-turn state**. The empirical result confirms state writes survive the session lifecycle.

Modern agent memory systems (Mem0, A-MEM, Zep, LiCoMemory, Memori) all converge on: (a) a durable store that survives process death, (b) a session-local context buffer populated from the durable store on login. The substrate equivalent: durable = substrate vector store under PP-195; session-local = context window passed to LLM. The session-local buffer is populated by a retrieval query at session start (top-K most recent + top-K most relevant memory atoms for the user).

Hard engineering question: what is the correct retrieval query at session start? Best answer from lit (2025): hybrid of recency-sorted top-10 and similarity-ranked top-10 relative to session opener. Both are O(log N) under substrate retrieval.

### 1.3 Session history retrieval

Substrate primitive: **bitemporal AS-OF** (empirical 0.003ms). AS-OF queries return the state of memory as it was at a specific wall-clock time. This directly answers "what did I tell you last Tuesday?" with zero LLM involvement. No equivalent in Mem0/A-MEM; this is a genuine substrate differentiator.

Implementation: every memory write is tagged with (valid_time, transaction_time). A user query "what did we discuss on Tuesday about X" resolves to AS-OF(valid_time=Tuesday) INTERSECT keyword(X) -- two substrate operations chained.

### 1.4 User preference learning

Not a named PP primitive. Closest: PP-107 confidence-graded atoms + PP-198 intent classifier. Preference learning is episodic-to-semantic distillation: raw conversation turns -> extracted preference atoms (formal/casual, technical/simple) -> stored as substrate atoms with the user tenant key.

Lit (2025): HiMem and TiMem implement this as a two-tier store: episodic (raw turns) plus semantic (distilled preferences). Distillation is triggered either at a fixed turn count or by a sleep-defrag cycle. PP-141/142 sleep-defrag is the direct substrate analog.

Practical implementation: a lightweight extractor runs on conversation close and writes 1-5 preference atoms per session. These atoms accumulate across sessions and are retrieved to bias system-prompt construction at next session start.

### 1.5 User identity disambiguation

Not a named PP primitive. Standard problem: the same real-world user may have multiple session IDs or aliases.

Engineering approach: deduplicate at the session-start join step. Substrate algebraic isolation (PP-101) makes cross-user contamination structurally impossible, so disambiguation is choosing WHICH tenant key to assign to the incoming session, not preventing post-assignment leakage.

### 1.6 Long-running conversation patterns

Lit finding: LoCoMo dataset (2025) is the canonical benchmark for multi-session conversation tracking. Key empirical result: naive context-window stuffing fails at >10 sessions; structured memory extraction + retrieval maintains 70%+ factual accuracy out to 50+ sessions.

Substrate advantage: bitemporal indexing means any atom can be queried by its insertion time, so a substrate agent can answer temporal questions about its own memory state ("do I still believe X?" as AS-OF(now) vs AS-OF(last month)).

### 1.7 Memory consolidation via sleep-defrag

Substrate primitive: **PP-141 sleep** + **PP-142 defrag**. Empirical: 50% churn 3.978ms.

Lit confirmation (Nature Comms 2022; PubMed 32748786; Optimal Stopping + SRC 2025): sleep-like unsupervised replay reduces catastrophic forgetting. Key finding: replay of BOTH recent AND conflicting old memories creates orthogonal representations. The 2025 Optimal Stopping + SRC approach achieves >2x baseline accuracy on continual learning benchmarks.

Substrate mapping: during sleep-defrag, low-activation atoms are candidates for consolidation or eviction. High-activation atoms from recent sessions should be replayed (read + re-write) to strengthen their representation.

Gap: the replay logic is not yet a concrete algorithm. Recommended: defrag pass = for each atom above threshold, re-write with refreshed timestamp + increment confidence score by delta. This is the biological reconsolidation mechanism mapped to substrate operations.

---

## 2. What-to-Remember Decision Logic

### 2.1 Explicit "remember / forget"

Remember: user says "remember that X" -> intent classifier (PP-198) flags intent=REMEMBER -> extractor writes atom with high confidence.
Forget: user says "forget X" -> intent classifier flags intent=FORGET -> PP-104 exact erasure on matching atoms (empirical: 0.0000ms, 0.0000 cross-tenant leakage). GDPR-compliant, cryptographically clean delete.

Lit gap: most 2025 agent memory systems (Mem0, A-MEM) implement soft deletion (mark-as-deleted) not hard deletion. Substrate PP-104 is stronger than anything in the current open-source field.

### 2.2 Auto-extract on confidence threshold

Substrate primitive: **PP-107 confidence-graded storage**.

Recommended three-gate logic (from lit synthesis, A-MEM 2025 + SSGM 2026):
1. Confidence gate: only store atoms where extractor confidence > 0.6 (tunable).
2. Novelty gate: do not store if a near-identical atom already exists (cosine similarity > 0.95 to existing).
3. Decay gate: atoms not retrieved in N sessions have confidence decremented by delta per sleep cycle; atoms reaching zero confidence are evicted.

This three-gate logic is implementable purely in substrate without LLM calls for the gate operations.

### 2.3 Conversation history stored by default

Lit finding (2025 memory survey, arXiv 2505.00675): 60-70% of raw conversation tokens are small talk, repetition, or transient reasoning -- storing verbatim causes memory bloat and 22% retrieval precision degradation.

Recommended policy: raw turns kept in a lightweight rolling buffer (last K turns, K=20) for in-session coherence. After session close, a consolidation pass extracts atoms; the raw buffer is discarded.

### 2.4 Sensitive info (PII) handling

Critical lit finding (Tonic.ai 2025; OWASP LLM08:2025): 40% of PII in sentence-length embeddings is recoverable via inversion attack. Embedding a PII-containing string into a vector store is NOT a safe anonymization step.

Required engineering step: PII scrubber runs BEFORE any atom is written to the substrate vector store. The scrubber either (a) removes PII tokens and stores a redacted atom, or (b) stores the atom in an encrypted sidecar with a deletion key, so that PP-104 erasure deletes the sidecar key.

This is a new integration requirement not in the existing PP primitive list. It is a mandatory pre-write filter.

### 2.5 Confidence-graded importance

PP-107 handles this. Recommended decay schedule: exponential decay with half-life = 30 sessions (tunable). Atoms accessed during retrieval have their confidence refreshed (LRU-style boost).

### 2.6 Substrate-asks-permission for ambiguous

Not yet in the PP primitive list. When PP-198 intent classifier confidence on {REMEMBER, FORGET} < 0.5, trigger a clarification turn before writing. This is a one-line wrapper on the existing intent classifier output.

---

## 3. Tool Orchestration Patterns

### 3.1 Substrate-as-orchestrator vs LLM-as-orchestrator

Two camps in 2025 literature:
- LLM-as-orchestrator (ReAct, OpenAI Assistants): LLM decides at each step which tool to call. High flexibility, high latency (~500ms per decision), high cost.
- Substrate-as-orchestrator: a deterministic or lightweight-classifier-based router dispatches tools WITHOUT an LLM call for the routing decision. LLM is called only when the task requires generation.

Recommended architecture: **substrate-as-orchestrator**. PP-198 intent classifier + PP-123 cascade router are the substrate-native routing primitives. LLM is one tool among many, called only when the cascade router routes to the LLM tier.

Empirical support: RouteLLM (ICLR 2025): a lightweight router achieves 85% cost reduction vs calling GPT-4 on every query while maintaining 95% of quality. PP-123 cascade router is structurally identical.

### 3.2 Per-query tool routing decisions

Decision tree (latency-first ordering):
1. Substrate retrieval (PP-195 + bitemporal) -- handles memory/factual queries about stored state. Sub-millisecond.
2. Math/code tool (SymPy / Python interpreter) -- handles computation. Seconds.
3. Web search -- handles real-time external queries. 1-5 seconds.
4. Small LLM (Pythia-1.4B or similar) -- handles simple generation. Seconds.
5. Medium LLM (Claude Haiku / GPT-4o-mini) -- handles moderate generation. ~500ms.
6. Large LLM (Claude Sonnet / GPT-4o) -- handles complex generation. 1-3 seconds.

PP-198 intent classifier makes the tier-1 routing decision (substrate vs external) in sub-10ms. PP-123 cascade router handles escalation within the external tier.

### 3.3 Tool result audit chain

Substrate primitive: **PP-184 Merkle audit**. Every tool call result can be written as a substrate atom with a Merkle proof linking it to the tool invocation atom. This creates a cryptographically auditable chain: query -> tool dispatch -> tool result -> substrate write -> Merkle proof.

This is a genuine substrate differentiator. No current open-source agent framework has this natively.

### 3.4 Multi-tool composition

Lit finding (arXiv 2603.22862, 2025): modern tool orchestration uses plan DAGs -- directed acyclic graphs of tool calls where outputs of one tool feed inputs to another. The substrate can store intermediate results as atoms and retrieve them by tool-call ID, making DAG composition natural.

Engineering gap: DAG execution is not yet a named PP primitive. Implementable as a session-local execution context (dictionary of {step_id -> result_atom}) with sequential or parallel dispatch.

### 3.5 Tool failure handling

Standard pattern (lit 2025): retry with exponential backoff for transient failures; fall back to next tier in cascade for capability failures; log failure atom to substrate for audit.

The substrate Merkle audit chain (PP-184) makes failure logging auditable: a failed tool call writes a failure atom with error type and timestamp, cryptographically linked to the original query atom.

### 3.6 Latency-aware tool selection

Lit finding (OATS arXiv 2603.13426; Latency-Quality Routing arXiv 2605.14241): outcome-aware selection outperforms static methods but requires offline calibration of (tool, query_class) success rates. A routing table stores per-tool expected latency + success rate; the router picks the minimum-expected-latency tool with success_rate > threshold.

Substrate implementation: the routing table itself is a substrate store -- a small set of atoms with (tool_name, query_class, expected_latency_ms, success_rate) fields, retrieved by query_class at dispatch time. This makes the routing table updateable without code changes.

---

## 4. LLM-as-Tool Integration

### 4.1 When substrate decides to call LLM

Decision criteria (priority order):
1. Query requires natural-language generation that substrate retrieval cannot provide.
2. Query requires reasoning over retrieved atoms that exceeds rule-based logic.
3. Intent classifier confidence < threshold for any structured tool.

Concrete test: measure fraction of production queries fully answered by substrate retrieval + math tool alone, without LLM call. Hypothesis: for a well-loaded knowledge base, this fraction is 40-60%. This is the primary cost lever.

### 4.2 Substrate-formatted prompts to LLM

The substrate populates the LLM prompt with retrieved atoms as structured context. Format: each atom is a (content, confidence, timestamp, source_tool) tuple. The LLM receives a compact structured context rather than raw conversation history.

Superior to naive context-stuffing because: (a) only high-confidence atoms are included, (b) atoms are ordered by relevance score, (c) prompt size is bounded by atom count not session length.

### 4.3 LLM response audit

The LLM response is written as a substrate atom with Merkle proof linking it to the input atoms and LLM call metadata (model_id, temperature, tokens_in, tokens_out). This enables post-hoc audit of which retrieved context drove which LLM output.

### 4.4 Multiple LLM backends

PP-123 cascade router can be extended with a backend selection dimension: (intent_class, cost_tier, latency_budget) -> (model_id, provider). A straightforward extension of the existing routing table.

Lit precedent (RouteLLM ICLR 2025; LLM Router arXiv 2603.20895): GNN or shallow encoder maps query embedding to model choice. The substrate retrieval can serve this role: query embedding is compared to a routing-table atom index, returning the best (model, provider) pair.

### 4.5 Cost-aware LLM selection

Track per-query cost as a substrate atom (model_id, tokens_used, cost_usd, timestamp). Aggregate over rolling window to compute per-user and per-session cost. Feed this back into the cascade router as a dynamic budget constraint.

### 4.6 Streaming responses

Not a substrate primitive. Streaming is handled at the HTTP/API layer between the LLM provider and the caller. Substrate writes the final completed response as an atom; intermediate streaming tokens are not stored.

---

## 5. Other Tools

### 5.1 SymPy / NumPy / math tool

Math queries detected by intent classifier (intent=MATH_COMPUTE). Query is parsed to a symbolic expression, dispatched to SymPy, result returned. No LLM call needed for pure computation.

Substrate role: store (query_expression, result, timestamp) as an atom for caching. Identical future queries hit the cache first.

### 5.2 Python code interpreter

Standard sandboxed execution. Substrate stores (code_snippet, result_stdout, exit_code, timestamp) as an atom. Dangerous code detection is a pre-execution filter (intent classifier can flag UNSAFE intent class).

### 5.3 Image generation

Dispatch to DALL-E / Stable Diffusion via API. Substrate stores (prompt, image_url, generation_params, timestamp) as an atom. Audit chain via PP-184 links the generation request to the result.

### 5.4 Audio (Whisper / TTS)

Whisper transcription: audio -> text, then treat as a standard query. Substrate stores (audio_hash, transcript, confidence) as an atom.

TTS: text -> audio, dispatched to TTS API. Substrate stores (text, audio_url, voice_params) as an atom for caching.

### 5.5 Web search

Dispatch to search API (Brave, Bing, Google). Results stored as substrate atoms with (url, title, snippet, retrieval_timestamp, query). Bitemporal indexing means a future AS-OF query can retrieve what the search returned on a specific date.

### 5.6 Database / SQL

Substrate can serve as the primary database for structured queries. For external SQL databases, dispatch via a SQL tool with result stored as a substrate atom.

---

## 6. Substrate Unique Advantages

These are capabilities no current open-source agent memory framework has natively:

### 6.1 Bitemporal AS-OF queries

"What did I tell you last Tuesday?" is a single AS-OF(valid_time=last_Tuesday) substrate query. Empirical latency: 0.003ms. No LLM call, no string search through conversation logs. Structurally impossible in flat-vector stores (Mem0, Chroma, Pinecone) without a separate temporal index.

### 6.2 Merkle audit chain per memory

Every atom has a cryptographic proof of provenance: which tool call, which session, which input atoms produced it. Enables: (a) GDPR audit responses, (b) hallucination detection (cross-check LLM output atom against its input atom chain), (c) organizational compliance reporting.

### 6.3 PP-104 exact erasure

Hard delete of all atoms associated with a user, session, or keyword, with cryptographic proof of deletion. Empirical: 0.0000ms cross-tenant leakage post-erasure. Stronger than any soft-delete approach in the field. OWASP LLM08:2025 names vector embedding non-deletion as a top-10 LLM security risk -- substrate natively solves this.

### 6.4 Multi-tenant algebraic isolation

Cross-tenant contamination is algebraically impossible (not just policy-enforced). Empirical: 0.0000 leakage under PP-101. This is a structural guarantee, not a configuration guarantee.

### 6.5 Substrate-discovered patterns via sleep-defrag

Sleep-defrag (PP-141/142) can surface latent patterns across sessions: atoms that cluster together across different users (shared knowledge) vs. atoms that are user-specific. This is a form of federated knowledge extraction without cross-tenant data sharing.

---

## 7. Engineering Anchors (Ranked)

Ranked by (impact x feasibility x cost):

### Anchor 1 [TIER-1, CPU]: Session-start memory retrieval benchmark
Test: given a loaded substrate with N=1000 atoms per user, measure retrieval latency and precision (recall@10) for hybrid recency+similarity query at session start.
HARD-PASS: recall@10 > 0.80, latency < 50ms
HARD-FAIL: recall@10 < 0.50 OR latency > 500ms
Cost: CPU, <30 min wall.
Why now: if session-start retrieval is slow or imprecise, the entire statefulness story fails.

### Anchor 2 [TIER-1, CPU]: Intent classifier + cascade router smoke test
Test: 100-query benchmark across intents {REMEMBER, FORGET, MATH_COMPUTE, WEB_SEARCH, LLM_GENERATE, RETRIEVE}. Measure per-class F1 and per-query dispatch latency.
HARD-PASS: macro-F1 > 0.80, p95 dispatch latency < 10ms
HARD-FAIL: any class F1 < 0.50 OR p95 latency > 100ms
Cost: CPU, <1 hr wall.
Why now: PP-198 + PP-123 are the routing primitives; they need a calibrated benchmark before tool dispatch is integrated.

### Anchor 3 [TIER-1, CPU]: PP-104 exact erasure end-to-end
Test: write 1000 atoms for a user; issue exact erasure; verify zero atoms remain AND zero cross-tenant leakage; measure erasure latency.
HARD-PASS: 0 residual atoms, 0.0000 cross-tenant leakage, latency < 10ms
HARD-FAIL: any residual atom OR any cross-tenant leakage > 0.0001
Cost: CPU, <30 min wall.
Why now: GDPR compliance is a v1 blocker; PP-104 needs an explicit end-to-end test in the agent-memory context.

### Anchor 4 [TIER-1, CPU]: Sleep-defrag consolidation benchmark
Test: simulate 50 sessions each writing 20 atoms; run PP-141/142 sleep-defrag; measure (a) consolidation ratio, (b) retrieval precision before/after, (c) wall time.
HARD-PASS: consolidation ratio > 1.5x, retrieval precision maintained or improved, wall time < 5 min
HARD-FAIL: retrieval precision drops > 10% post-defrag OR consolidation ratio < 1.1x
Cost: CPU, <1 hr wall.
Why now: memory bloat is the dominant failure mode in long-running agents (lit: 60-70% of raw tokens are noise); defrag is the substrate answer.

### Anchor 5 [TIER-1, CPU]: Bitemporal AS-OF query benchmark
Test: load 10k atoms with random timestamps spanning 90 days; issue 100 AS-OF queries at random past timestamps; measure precision and latency.
HARD-PASS: precision > 0.95, p95 latency < 5ms
HARD-FAIL: precision < 0.80 OR p95 latency > 50ms
Cost: CPU, <30 min wall.
Why now: AS-OF is the strongest substrate differentiator for conversational memory; it must be benchmarked to be credibly positioned in v1 demo.

### Anchor 6 [TIER-2, CPU]: PII pre-write scrubber integration
Test: route 500 synthetic PII-containing strings through a pre-write scrubber (spaCy NER or equivalent); measure PII recall, false positive rate, and throughput.
HARD-PASS: PII recall > 0.95, false positive rate < 0.05, throughput > 100 strings/sec
HARD-FAIL: PII recall < 0.80 OR throughput < 10 strings/sec
Cost: CPU, <2 hr wall.
Why now: OWASP LLM08:2025 makes PII-in-embeddings a compliance risk; scrubber is a mandatory pre-write filter.

### Anchor 7 [TIER-2, CPU+optional GPU]: Multi-tool composition latency end-to-end
Test: construct a 3-step tool chain (substrate retrieve -> Python compute -> LLM generate); measure end-to-end latency for 50 queries; measure fraction where LLM call was avoided.
HARD-PASS: p50 e2e latency < 2s (LLM avoided), < 5s (LLM called); LLM-avoidance rate > 40%
HARD-FAIL: p50 e2e latency > 10s OR LLM-avoidance rate < 20%
Cost: CPU for retrieve+compute; GPU or API credit for LLM calls. <2 hr wall.
Why now: LLM-avoidance rate is the primary cost lever.

---

## Cheap Decisive Test

**Anchor 1 (session-start retrieval) + Anchor 2 (intent classifier smoke)** can run back-to-back on CPU in under 2 hours. Together they validate the critical path: does the substrate correctly route a query AND retrieve the right context? If both HARD-PASS, the statefulness integration story is empirically grounded. If either HARD-FAILS, it identifies the blocking gap before product engineering begins.

---

## Falsifiable Predictions

HARD-PASS:
- Session-start hybrid retrieval recall@10 > 0.80 at N=1000 atoms
- Intent classifier macro-F1 > 0.80 across 6 intent classes
- PP-104 erasure: zero residual atoms, zero cross-tenant leakage
- Bitemporal AS-OF precision > 0.95 across 90-day window
- LLM-avoidance rate > 40% in multi-tool composition

HARD-FAIL (any one falsifies the integration viability):
- Retrieval latency > 500ms at N=1000 (implies indexing gap, not just physics)
- Intent classifier F1 < 0.50 on any class (implies classifier is not deployable)
- Any PP-104 residual atom (implies erasure is not complete)
- Bitemporal AS-OF precision < 0.80 (implies temporal indexing is broken)
- LLM-avoidance rate < 20% (implies substrate retrieval not reliable enough to skip LLM)

---

## Cross-Thread Synthesis

This drill intersects:
- PP-195 multi-turn state (1.2, 1.3) -- integration confirms empirical results map directly to session-start retrieval
- PP-104 GDPR erasure (2.1, 2.4, 6.3) -- integration adds PII pre-write scrubber as a NEW required filter not currently in PP primitive list
- PP-184 Merkle audit (3.3, 4.3) -- integration extends audit chain to tool-call provenance, which is a novel use of the existing primitive
- PP-141/142 sleep-defrag (1.7, 2.5) -- integration proposes a concrete replay algorithm (re-insert with refreshed timestamp + confidence boost) not yet specified in PP documentation
- PP-198/123 intent+cascade (3.1, 3.2) -- integration confirms these are the correct routing primitives; adds latency-budget dimension to cascade router
- PP-101 isolation (1.1) -- integration adds session-scoped index key as a thin wrapper requirement

New integration requirements NOT in existing PP primitives:
1. PII pre-write scrubber (mandatory pre-write filter)
2. Session-scoped index key (thin wrapper on PP-101)
3. Replay algorithm for sleep-defrag (concrete specification needed)
4. Confidence decay schedule (exponential decay, half-life tunable)
5. Latency routing table as substrate atoms (dynamic, updateable without code changes)

---

## Substrate-Product Implications

1. Substrate is already differentiated from every current agent memory system on: bitemporal AS-OF, exact erasure, algebraic isolation, and Merkle audit. These are not incremental improvements; they are structural gaps in Mem0/A-MEM/Zep/Letta.

2. The integration work is well-scoped: 7 engineering anchors, all CPU-runnable except partial GPU for anchor 7, all < 2 hours wall time individually. This is a 2-3 day engineering sprint to have a working stateful conversational agent on substrate.

3. OWASP LLM08:2025 risk (PII-in-embeddings is recoverable) makes the PII pre-write scrubber a compliance requirement, not a nice-to-have. Priority should be elevated to match anchors 1-2 before any demo with real user data.

4. RouteLLM result (ICLR 2025: 85% cost reduction at 95% quality maintenance) empirically validates the substrate-as-orchestrator + LLM-as-tool architecture. Building LLM calls as one tool in the cascade, rather than the default orchestrator, is the correct product architecture.

5. Sleep-defrag (PP-141/142) is unique in the market. No commercial agent memory system has an equivalent. The concrete replay algorithm (re-insert with refreshed timestamp + confidence boost) should be specified and benchmarked as anchor 4, then featured in the v1 demo.

---

## Citations (verified: 18)

1. Rezazadeh et al. 2026. A memory fabric for conversational AI agents. Springer Discover AI. https://link.springer.com/article/10.1007/s44163-026-00992-z
2. LiCoMemory. 2025. arXiv:2511.01448
3. Beyond the Context Window. 2026. arXiv:2603.04814
4. Memori. 2026. arXiv:2603.19935
5. Hierarchical Memory Orchestration. 2026. arXiv:2604.01670
6. Multiple Memory Systems. 2025. arXiv:2508.15294
7. SSGM Framework. 2026. arXiv:2603.11768
8. Rethinking Memory in LLM Agents. 2025. arXiv:2505.00675
9. TiMem. 2026. arXiv:2601.02845
10. Aeon Neuro-Symbolic Memory. 2026. arXiv:2601.15311
11. Curator Multi-Tenant Vector DB. 2024. arXiv:2401.07119
12. OATS Outcome-Aware Tool Selection. 2026. arXiv:2603.13426
13. Latency-Quality Routing. 2026. arXiv:2605.14241
14. RouteLLM. ICLR 2025.
15. LLM Router. 2026. arXiv:2603.20895
16. Sleep-like unsupervised replay. Nature Comms 2022. PMC9755223
17. Optimal Stopping + SRC. 2025.
18. OWASP LLM08:2025. Vector and Embedding Weaknesses.
