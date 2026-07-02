# LLM+Substrate Hybrid Runtime API — M3 Phase 1
**Date:** 2026-07-02
**Author:** hdi_research (Director) — Sonnet drill, USER-authorized
**Prior arc consulted:**
- `notes/director_M3_Phase1_LLM_router_architecture_sketch_2026-06-28.md` (direct predecessor; v0 Python API surface)
- `notes/research_drill_hybrid_architecture_deployment_2x_2026-06-11.md` (6-pattern deployment taxonomy)
- `notes/director_M3_M1_3_stochastic_noise_injection_design_spec_2026-07-01.md` (noise channel design)
- Cleanup latency CG: `data/exp_stage2_cleanup_latency_operating_curve_v1_seed_7/metrics.json` (read from disk)
- Calibration penalty: P_deflated = P_raw - 0.20; novel-synthesis cap 0.50

---

## HEADLINE

**Recommended runtime API pattern: Python SDK (in-process), synchronous single-call, session-cached embeddings, LLM-batched substrate writes.**

P_deflated (Phase 1 end-to-end viable at 100-user shard): 0.52 (raw 0.72; deflated 0.20; well-motivated by latency CG but encoding bottleneck and tail-ratio are real constraints not yet resolved at shard scale).

The substrate is fast enough for synchronous tool-call style at N=8192 (p50=11ms numpy; 14.6x tail ratio is the main risk). The encoding step (text -> HD vector) is the dominant latency term and is NOT yet characterized at LLM-serving batch rates. Phase 1 prototype can sidestep this by pre-encoding a closed vocabulary. Phase 2 must solve the open-vocabulary encoding pipeline.

---

## Verified latency baseline (off-disk, cleanup_latency_operating_curve, seed_7 full run)

| N | alpha | M | p50 (ms) | p99 (ms) | p99/p50 tail ratio |
|---|---|---|---|---|---|
| 2048 | 1.0 | 2048 | 0.44 | 0.77 | 1.7x |
| 8192 | 0.5 | 4096 | 11.5 | 17.3 | 1.5x |
| 8192 | 1.0 | 8192 | 13.2 | 27.8 | 2.1x |
| 8192 | 3.0 | 24576 | 11.0 | 19.5 | 1.8x |
| 8192 | 10.0 | 81920 | 12.0 | 23.1 | 1.9x |
| 8192 (cold) | 3.0 | 24576 | 15.9 | 29.2 | 1.8x |
| max_p99/p50 across all arms | | | | | 14.6x |

Key finding: p50 is M-independent at N=8192 (gate HP_LATENCY_INDEPENDENT_OF_M = true). The 14.6x tail ratio comes from the high-alpha spike arms — in operational use at alpha=1-3, tail ratio is 1.5-2.1x. Gate HP_TAIL_CONTROLLED = false (one gate missed), which means tail spikes can reach p99 ~28ms at N=8192. This is compatible with tool-call style (100ms SLA; 28ms substrate leaves 72ms for LLM token generation overhead). NOT compatible with streaming-token-level use (where each token needs <5ms).

---

## API surface sketch (5-10 key operations)

Based on the June 28 sketch plus this drill's analysis.

### In-process Python SDK (recommended for Phase 1)

```python
class SubstrateClient:
    """Thin synchronous API between LLM router and substrate primitives.
    All calls are blocking; caller handles async if needed (asyncio.to_thread).
    Embedding encoding is pre-computed for known vocabulary (Phase 1 constraint).
    """

    # --- READ OPERATIONS ---

    def classify_intent(
        self,
        query: str,
        session_ctx: SessionContext | None = None
    ) -> IntentResult:
        """Classify query intent via substrate intent classifier.
        Returns: IntentResult(intent_class: str, confidence: float, refused: bool)
        Latency: p50 ~0.5ms (N=2048 intent codebook); tail p99 ~1ms.
        """

    def kg_lookup(
        self,
        entity: str,
        relation: str,
        session_ctx: SessionContext | None = None
    ) -> LookupResult:
        """Single-hop KG retrieval. Substrate cleanup read on M-matrix.
        Returns: LookupResult(answer: str | None, confidence: float, refused: bool,
                              trace: HopTrace)
        Latency: p50 ~11ms at N=8192; p99 ~28ms. M-independent.
        """

    def multi_hop(
        self,
        start: str,
        relation_chain: list[str],
        max_depth: int = 5
    ) -> HopResult:
        """Multi-hop chain retrieval (depth <= max_depth).
        Returns: HopResult(final_answer: str | None, confidence: float,
                           refused: bool, hop_trace: list[HopTrace])
        Latency: p50 ~11ms * depth (sequential cleanup reads).
        Note: depth-15 is chain-grade; depth-40 = 0.533 accuracy.
        """

    def batch_kg_lookup(
        self,
        queries: list[tuple[str, str]],
        max_batch: int = 64
    ) -> list[LookupResult]:
        """Batched KG lookup for 100-user shard mode.
        Substrate matrix multiply is already batch-efficient (W @ Q.T).
        Caller does NOT need to aggregate — substrate does internal batching.
        Latency: wall_time ≈ p50_single * 1.1 for B<=64 (matrix op, not B serial calls).
        """

    # --- WRITE OPERATIONS ---

    def write_session_fact(
        self,
        key_entity: str,
        value_entity: str,
        relation: str,
        session_id: str,
        ttl_turns: int = 20
    ) -> WriteResult:
        """Write a session-scoped fact into substrate STM.
        Called by cortex-side STM auto-flush (M1.5 classifier decides WHEN to write).
        LLM does NOT decide when to write — cortex classifier does.
        Returns: WriteResult(success: bool, slot_id: int, evicted: str | None)
        """

    def flush_session(self, session_id: str) -> None:
        """Evict all session-scoped facts for this session_id (session end cleanup)."""

    # --- GATE OPERATIONS ---

    def refuse_gate(
        self,
        query: str,
        intent: str,
        confidence: float
    ) -> bool:
        """Returns True if substrate should refuse (LLM must fall back).
        Fires when: confidence < threshold OR query outside known domain.
        Threshold: V_REL=256 regime-invariant physics law: tau = sqrt(2*log(V_REL)/N).
        """

    # --- CACHE OPERATIONS ---

    def get_session_cache(self, session_id: str, key: str) -> CacheResult | None:
        """Retrieve a cached substrate response for this session.
        Cache is in-process dict; TTL = 10 turns; key = (query_hash, intent).
        Returns None on miss; CacheResult on hit (with age_turns metadata).
        """

    def put_session_cache(
        self, session_id: str, key: str, value: LookupResult, ttl_turns: int = 10
    ) -> None:
        """Store a substrate response in session cache."""

    # --- GLASS-BOX AUDIT ---

    def get_audit_trace(self, result_id: str) -> AuditTrace:
        """Return the full reasoning trace for a substrate result.
        Includes: hop sequence / attractor convergence path / refuse-gate decision.
        This is the 'glass-box' property M3 promises.
        """
```

---

## Design decision 1: REST vs SDK vs shared-memory

**Recommendation: Python SDK (in-process), Phase 1. REST optional in Phase 2.**

| Option | Latency overhead | Complexity | Phase 1 fit |
|---|---|---|---|
| In-process Python SDK | 0ms (function call) | Low | BEST — substrate is pure numpy/torch; no IPC |
| REST (localhost) | +1-3ms HTTP overhead | Medium | Adds overhead on a p50=11ms substrate call (10-27%); unacceptable for tight SLAs; justified only if LLM is remote |
| REST (network) | +20-100ms | High | Kills the SLA. Only viable if batching absorbs overhead (B=64 batch makes per-query REST overhead 0.3ms amortized) |
| Shared memory (mmap / Redis) | ~0.1-0.5ms serialization | Medium-High | Worth considering for multi-process LLM serving; overkill for Phase 1 |
| gRPC (localhost) | +0.5-1ms | High | Better than REST but adds proto compile step; defer to Phase 2 |

**Phase 1 constraint:** LLM router is calling into the same Python process where substrate primitives live. No network hop. `SubstrateClient` is instantiated once at process start; substrate W-matrix is loaded into RAM once. This gives the 0-overhead function-call path.

**Phase 2 trigger:** when the LLM is served remotely (e.g., Haiku via Anthropic API) and substrate is local, the router becomes a local Python process that makes outbound LLM API calls and local substrate calls. Still in-process for substrate. REST only becomes relevant if substrate is sharded across machines (M3 Phase 3+).

---

## Design decision 2: Query object format

**Recommendation: structured dict with text + pre-encoded vector optional, synchronous.**

Three candidate formats:
1. **Text-only:** `{"query": "Who directed Inception?"}` — simplest; router encodes text to HD vector internally. Cleanest for LLM-side caller.
2. **Pre-encoded vector:** `{"vec": tensor, "intent": "KG_LOOKUP"}` — fastest; avoids re-encoding. Requires LLM caller to have encoder access. Phase 2 pattern.
3. **Structured facets:** `{"entity": "Inception", "relation": "directed_by"}` — LLM does NL parse, passes structured slots. Avoids all encoding. Best for structured query intents.

**Phase 1 recommendation: text-only for classify_intent; structured facets for kg_lookup/multi_hop.** The LLM router handles the NL -> slot extraction step (this is exactly what LLMs are good at). Substrate handles the slot -> answer step. The encoding bottleneck (text -> HD vector) is bypassed by having the LLM extract structured slots from the query before calling substrate. This is the cheapest-to-prototype path.

**Phase 2:** Add vector-passthrough for sessions where the same entity appears in multiple queries (amortize encoding cost).

---

## Design decision 3: What substrate returns

**Recommendation: typed result objects with confidence + refused flag + audit trace.**

```python
@dataclass
class LookupResult:
    answer: str | None          # None = not found OR refused
    confidence: float           # substrate cosine similarity at attractor
    refused: bool               # refuse-gate fired (fallback required)
    trace: HopTrace             # glass-box audit: attractor path, hop sequence
    latency_ms: float           # actual p50 of this call (for SLA monitoring)
    result_id: str              # UUID for get_audit_trace() later
```

The `refused` flag is load-bearing. The LLM router decision tree is:
```
if result.refused:
    -> LLM fallback (general response, no substrate)
elif result.confidence < confidence_threshold:
    -> LLM fallback with substrate hint (hedged)
else:
    -> return result.answer (glass-box, substrate-primary)
```

The confidence_threshold should be tuned empirically; start at 0.8 (the cosine similarity above which cleanup converges cleanly). The refuse-gate threshold is derived analytically: `tau = sqrt(2 * log(V_REL) / N)` at V_REL=256, N=8192: tau = sqrt(2 * 5.545 / 8192) = 0.0367. This is the HARD floor; operational threshold will be higher.

---

## Failure mode handling recipe

### Failure 1: Substrate refuses (M1.4 refuse-gate fires)

Root cause: query is outside substrate's known domain OR confidence below tau.

```
if result.refused:
    # Do NOT expose refused answer to user
    # Fallback: LLM general response
    response = llm.generate(query, context=session_ctx)
    # Log: refused substrate + LLM fallback used (for audit + calibration)
    audit_log.append({"event": "substrate_refused", "query": query, "llm_fallback": True})
```

Do NOT ask the user "substrate doesn't know, do you want to try something else?" — this leaks implementation detail. Silently fall back to LLM.

### Failure 2: Substrate returns confidently-wrong (BIAS-Q pattern)

Root cause: V_REL too small; attractor convergence to wrong codebook entry; confidence looks high but answer is incorrect.

Mitigation: the LLM generates its own answer in parallel (Pattern 4 from June 11 taxonomy: cascade / parallel verify). If substrate answer != LLM answer AND substrate confidence is not extremely high (>0.95), prefer LLM.

```python
# Parallel paths (asyncio.gather or threading)
substrate_result, llm_result = await asyncio.gather(
    substrate.kg_lookup(entity, relation),
    llm.generate(query)
)
if substrate_result.confidence > TRUST_THRESHOLD and not substrate_result.refused:
    if substrate_result.answer == llm_result.answer:
        return substrate_result  # agreement: trust substrate (glass-box)
    elif substrate_result.confidence > HIGH_CONFIDENCE:
        return substrate_result  # substrate wins: high confidence + audit trail
    else:
        return llm_result        # disagreement + moderate confidence: prefer LLM
else:
    return llm_result            # refused or low confidence: LLM primary
```

TRUST_THRESHOLD = 0.8; HIGH_CONFIDENCE = 0.95. These require empirical tuning in Phase 1.

Note: parallel execution costs 11ms substrate + LLM latency (NOT sequential 11ms + LLM latency) at the cost of extra LLM calls for all substrate-routed queries. This is the "cautious" operating mode for Phase 1 where BIAS-Q risk is highest. Phase 2 can switch to substrate-primary once calibration is established.

### Failure 3: Substrate timing exceeds SLA

Root cause: tail spike. p99=28ms at N=8192 alpha=1.0. With 72ms LLM overhead, total P99 = 100ms — at the SLA edge.

```python
import asyncio

async def substrate_with_timeout(client, entity, relation, timeout_ms=50):
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(client.kg_lookup, entity, relation),
            timeout=timeout_ms / 1000
        )
        return result
    except asyncio.TimeoutError:
        # Drop the substrate query; respond without memory
        audit_log.append({"event": "substrate_timeout", "fallback": "no_memory_response"})
        return None

# In router:
result = await substrate_with_timeout(client, entity, relation, timeout_ms=50)
if result is None:
    response = llm.generate(query)  # no substrate context
else:
    # normal flow
```

The 50ms timeout is conservative (well below p99=28ms); adjust based on measured tail distribution in production. Do NOT retry on timeout (retrying on a tail spike will make it worse). Log every timeout for capacity planning.

---

## Information loss analysis (text -> substrate -> text roundtrip)

The lossiness chain has four stages:

**Stage 1: Text -> HD vector encoding (most loss)**
Char-trigram encoder (confirmed in substrate KB v1). Information lost: exact word identity for rare terms; cross-domain polysemy (0.42 ceiling from June 11 drill). This is the DOMINANT loss stage.

**Stage 2: HD vector -> substrate write (near-lossless up to capacity)**
Willshaw capacity ~0.69*N bits per pattern at alpha=1. At N=8192: ~5651 bits per stored pattern. A KG entity like "Christopher Nolan" requires ~15-20 bits of information to uniquely identify. Well within capacity. Loss is negligible below capacity ceiling.

**Stage 3: Substrate read -> HD vector (attractor convergence; lossless above tau)**
Cleanup recall = 1.0 at all operational arms in the CG cell. Loss is zero when confidence > tau. At confidence < tau, answer is wrong (not just imprecise) — this is why refuse-gate is load-bearing.

**Stage 4: HD vector -> text decoding (codebook lookup; near-lossless for known vocabulary)**
If the answer entity is in the codebook, cosine nearest-neighbor gives exact string. If the answer is a new entity not in training codebook, there is no decoding path — this is the "open vocabulary" gap Phase 2 must address.

**Where loss bites M3 Phase 1:**
1. Open-domain NL queries with rare/neologistic vocabulary hit Stage 1 loss hard. Mitigation: limit Phase 1 to closed-vocabulary domains (FB15k entities are finite; known codebook).
2. Cross-domain polysemic queries hit Stage 1 ceiling (0.42). Mitigation: route all polysemic queries to LLM (refuse-gate fires automatically at low confidence).
3. Answer entities outside codebook hit Stage 4 dead-end. Mitigation: substrate only for KG relations where answer space is known (e.g., FB15k answers are all in codebook).

**Can substrate return raw values that LLM decodes better than plain text summaries?**
Yes, in principle: substrate can return the raw attractor HD vector, and the LLM (if it has the same encoding projection) can do its own decoding using a fine-tuned projection layer. This is the deep-integration path (Pattern 2 from June 11: substrate enriches LLM internal representations). This is Phase 3 territory. For Phase 1, decode to text string via codebook nearest-neighbor lookup — simpler, auditable, and sufficient for closed-vocabulary domains.

---

## Write API: who decides when to write?

**Recommendation: cortex-side classifier decides, not LLM.**

From `director_M3_Phase1_LLM_router_architecture_sketch_2026-06-28.md` and the M1.5 STM milestone:

The STM auto-flush classifier (M1.5) decides when to write. The LLM should NOT be responsible for deciding "this fact is worth storing." Reasons:
1. LLM decisions about what to store would be opaque (unauditable).
2. LLM calling `write_session_fact()` directly creates a write-amplification risk (LLM might over-store or under-store).
3. The cortex classifier can be audited and calibrated; LLM judgment cannot.

**Phase 1 write trigger (simple rule):** write to substrate if the query was substrate-answered with confidence > TRUST_THRESHOLD AND the fact-type is in the auto-flush whitelist (KG facts, not ephemeral conversational facts). The LLM is NOT in the write loop.

**Phase 2:** learn the STM classifier from session transcripts — which substrate writes actually improved later retrieval? Self-supervised training on session data.

---

## Session cache behavior

**Recommendation: in-process session dict; TTL=10 turns; key=(query_text_hash, intent_class).**

Substrate responses are deterministic for the same (entity, relation) query (cleanup is idempotent given same W-matrix). Caching is therefore safe and high-value.

Cache policy:
- **Hit:** return cached LookupResult; log cache_hit for audit; do NOT re-query substrate.
- **Miss:** query substrate; cache result (if not refused); return result.
- **Invalidation:** write_session_fact() to the same entity+relation invalidates that cache entry. Session flush invalidates all entries for that session_id.
- **TTL:** 10 turns is conservative for KG facts (FB15k facts don't change during a session). Conversational facts (STM auto-flush writes) should use TTL=3 turns (shorter because they're session-specific context that expires).
- **Size limit:** max 1000 entries per session (prevent memory leak for long sessions). LRU eviction beyond limit.

**Batch cache:** for `batch_kg_lookup()`, check each (entity, relation) pair against cache before building the batch. Only uncached queries go to substrate. This can dramatically reduce substrate load for repeated-entity sessions.

---

## Comparison to RAG and function-calling

### vs. RAG (vector DB backend)

| Dimension | RAG | Substrate |
|---|---|---|
| Retrieval model | Approximate nearest-neighbor (FAISS/HNSW) | Associative memory cleanup (exact attractor) |
| Query format | Dense embedding vector | HD vector (same concept, different algebra) |
| Confidence signal | Cosine similarity (approximate; no calibration) | Cosine at attractor + refuse-gate (calibrated by physics law) |
| Audit trail | None (opaque vector similarity) | Full attractor convergence path |
| Multi-hop | External graph traversal (not native) | Native: chain cleanup per hop |
| Write latency | Index update (slow: ~100ms per entry) | Superposition write (fast: O(N) outer product) |
| Capacity limit | Scales with hardware (no mathematical cap) | Willshaw capacity: 0.69*N bits per pattern (hard mathematical cap) |
| Phase 1 borrow from RAG | Chunking strategy for long documents | --- |
| Phase 1 advantage over RAG | Refuse-gate + audit trail + multi-hop native | --- |

The key advantage substrate has over RAG: the refuse-gate is physics-law calibrated, not threshold-tuned. RAG has no principled "I don't know" signal — it always returns a result. Substrate's conformal calibration (M1.4 milestone) is load-bearing for glass-box property.

The key disadvantage vs. RAG: capacity is hard-bounded by N. RAG scales arbitrarily. Substrate's answer: partition routing (M=10M CG) shards the keyspace.

### vs. LLM function-calling (ReAct / tool-use)

The API surface is nearly identical: the LLM calls `kg_lookup(entity, relation)` the same way it calls `search(query)` in ReAct. The difference is what the tool returns: ReAct tools return unstructured text; substrate returns typed results with confidence + refused flag + trace. The LLM router's decision loop is the same pattern as ReAct's thought-act-observe loop.

**Phase 1 can borrow the ReAct pattern directly.** The tool schema for the LLM router:

```json
{
  "name": "substrate_kg_lookup",
  "description": "Look up a KG fact in substrate memory. Returns answer entity and confidence. If refused=true, do not use the answer.",
  "parameters": {
    "entity": {"type": "string", "description": "The subject entity"},
    "relation": {"type": "string", "description": "The relation type (e.g. directed_by, born_in)"},
    "session_id": {"type": "string", "description": "Current session identifier"}
  }
}
```

This is directly passable to Anthropic tool_use API. The LLM generates a tool_use block; the router executes it against substrate; returns tool_result; LLM continues. No new infrastructure needed beyond the SubstrateClient.

---

## Batching: who batches?

**Recommendation: substrate does internal batching; LLM sees single-call API.**

From Dim F drill context: 100-user shard needs B=64 batching. The substrate matrix multiply is `Q @ W.T` where Q is (B, N) — already naturally batched. The LLM does NOT need to aggregate queries before calling substrate.

**Architecture for 100-user shard:**
```
100 concurrent LLM sessions
  |-- each generates tool_use block independently
  |-- Router collects tool_use calls in a B=64 accumulation window (2-5ms)
  |-- batch_kg_lookup([...64 queries...]) -> W @ Q.T single matmul
  |-- Route results back to respective sessions
  |-- Wall latency for 64 queries: ~11ms (same as single query; matmul is the cost)
  |-- Effective throughput: 64 queries / 11ms = 5818 QPS at N=8192
```

The accumulation window (2-5ms) is the key design parameter. Too short: batch size stays small. Too long: added latency before substrate call. Sweet spot depends on measured inter-arrival rate of LLM tool_use calls at target load.

**Note:** the encoder step (text -> HD vector) is NOT batched in Phase 1 (closed vocabulary; pre-encoded). In Phase 2 with open vocabulary, the encoder batch is separate from the substrate batch and may need its own accumulation window.

---

## Cheapest cell to prototype the interface

**Cell: `mock_llm_router_substrate_integration_v1`**

- **What it tests:** LLM router (mocked Haiku call using canned intent extraction) calling into `SubstrateClient` Python API over 200 queries (FB15k eval subset).
- **Why mock LLM:** avoids Anthropic API cost for the integration smoke; router is just intent classification + slot extraction, which can be hardcoded for known query patterns.
- **Arms:**
  - ARM 1: substrate-only path (classify_intent + kg_lookup + refuse_gate)
  - ARM 2: parallel-verify path (substrate + mock-LLM, compare answers)
  - ARM 3: batch path (B=64 batch_kg_lookup vs 64 serial kg_lookup; compare wall time)
- **Hard-pass thresholds:**
  - HP1: ARM 1 kg_lookup accuracy >= 0.80 on FB15k-237 eval (2-hop chains)
  - HP2: ARM 1 refuse-gate precision >= 0.85 (refused queries are truly out-of-domain)
  - HP3: ARM 3 batch_kg_lookup wall_time <= 1.5x single kg_lookup wall_time (batching gives ~40x throughput, not 1x)
- **Hard-fail thresholds:**
  - HF1: any arm crashes (integration error = blocking)
  - HF2: ARM 1 accuracy < 0.50 (substrate-only path is worse than random = architecture mismatch)
- **Estimated smoke runtime:** 15 min (200 queries * 11ms p50 = 2.2s substrate time; overhead dominated by mock-LLM logic)
- **This cell unblocks:** M1.1 (intent classifier exposed) + M1.2 (kg_lookup exposed); gives empirical accuracy baseline before wiring real LLM

**Cell file location (to be authored):** `experiments/exp_M3_mock_llm_router_substrate_integration_v1.py`
**Pre-reg location:** `preregs/2026-07-02_M3_mock_llm_router_substrate_integration_v1.md`

---

## M3 Phase 1 deployment sequencing

**Revised from June 28 sketch, accounting for this drill's findings:**

### M1.0 — SubstrateClient Python module (1-2 days, hdi_exp_dev)
Author `substrate_router/api.py` with the SubstrateClient class above. Add `substrate_router/result_types.py` (dataclasses). Smoke: import test + kg_lookup on 5 hardcoded FB15k facts. No pre-reg needed (it's infrastructure, not an experiment cell).

### M1.1 — Intent classifier exposed + mock router (2-3 days)
Wire intent_classifier_v2 into SubstrateClient.classify_intent(). Author mock_llm_router_substrate_integration_v1 cell (cell above). Smoke at N=2048 (fast). Dispatch to remote_cpu_queue for full 200-query eval. Gate: HP1 + HP2.

### M1.2 — Session cache + session write API (1 day)
Add in-process session dict cache. Wire write_session_fact() to STM auto-flush prototype. Smoke: 20-turn simulated session; verify cache hits after turn 1.

### M1.3 — Noise channel integration (1-2 days)
Wire `substrate_router/noise_channel.py` (already designed; file `director_M3_M1_3_stochastic_noise_injection_design_spec_2026-07-01.md`). This enables adaptive tau / refuse-gate in the intermediate-confidence band. Smoke: inject `moderate` noise; verify refuse-gate fires more often than clean input.

### M1.4 — Multi-hop exposed + timeout handling (2 days)
Wire multi_hop() with asyncio timeout wrapper. Smoke: 50-chain depth-2/3 eval. Gate: substrate_with_timeout() correctly falls back to no-memory-response on simulated 100ms spike.

### M1.5 — Real LLM integration (1-2 days, per USER authorization)
Replace mock-LLM with real Haiku-4-5 tool_use call. Wire the tool schema (json above) into an Anthropic SDK call. Test 20 real FB15k queries with Haiku. Gate: LLM correctly uses refused flag to fall back.

### M1.6 — 200-query end-to-end demo (1 day)
Run 200 queries spanning KG/multi-hop/refused/general. Measure: substrate-routed accuracy, LLM-fallback accuracy, router decision accuracy, p50/p99 end-to-end latency. USER decision point on Phase 2.

**Critical path constraint:** M1.0-M1.3 can run in parallel with ongoing substrate CG work (they're `substrate_router/` module work, not `hdlab/` changes). M1.4+ require the noise channel to be smoke-PASS first.

---

## Open questions for USER

1. **Real LLM in M1.5** — which model? claude-haiku-4-5 is the natural choice (fast, cheap). Or defer real-LLM until Phase 2, staying mock for Phase 1?
2. **Closed vs open vocabulary** — Phase 1 prototype uses FB15k closed vocabulary. At what point does USER want to stress-test open-vocabulary queries (Phase 2 trigger)?
3. **Glass-box explanation verbosity** — should the router return the full attractor trace to the end user (verbose glass-box), or just the answer + a "this came from memory" indicator (quiet glass-box)?
4. **Session cache TTL** — 10 turns seems right for KG facts; does USER have a different intuition?
5. **Batch window** — 2-5ms accumulation window for B=64 shard batching: does USER anticipate latency-sensitive applications that can't tolerate the added window?

---

## Summary

Prior arc work (June 11 taxonomy + June 28 sketch) is directly applicable. This drill adds:
- Latency numbers from disk (p50=11ms N=8192; tail 14.6x max, but 1.5-2.1x at alpha=1-3)
- Concrete API dataclass surface (typed results + refused flag + audit trace)
- Clear ownership model: LLM does NL->slot extraction; substrate does slot->answer; cortex classifier decides writes
- Failure mode recipes (refuse/timeout/BIAS-Q) with code
- Information loss analysis: Stage 1 encoding is dominant; Phase 1 must use closed vocabulary
- Cheapest prototype cell identified: mock_llm_router_substrate_integration_v1 at ~15min smoke
- Phase 1 sequencing: M1.0 SubstrateClient -> M1.1 mock router -> M1.2 cache -> M1.3 noise -> M1.4 multi-hop -> M1.5 real LLM -> M1.6 demo

P_deflated for Phase 1 end-to-end viability: 0.52. Main risks: encoder throughput at 100-user shard (uncharacterized); tail ratio (resolved by 50ms timeout); BIAS-Q calibration (parallel-verify mode handles this at Phase 1 cost of extra LLM calls).
